#!/usr/bin/env python3
"""LoRA adaptörünü ham base'e AKITARAK birleştir → tam HF dizini (GGUF'a hazır).

Neden ayrı script: `setup_llamacpp.sh` HF repo alıyor, adaptör almıyor — zincirin
aradaki halkası yoktu (sprint1 CP6).

Neden akıtmalı (tensör-tensör), `PeftModel.merge_and_unload()` değil:
CLAUDE.md merge doktrini "host RAM, streaming tensor-by-tensor" diyor. Modeli
tümüyle bf16'da açmak 9.3 GB tutar; WSL2 VM'i host'un yarısını görür (15.9 GB).
Akıtmalı yolun tepesi tek tensör (~1.3 GB). Sprint 3'ün k-yollu TIES'i de bu raydan geçer.

ΔW = (lora_alpha / r) · B @ A   —   W' = W + ΔW, float32'de toplanıp özgün dtype'a döner.

Kullanım:
    python scripts/egitim/merge_lora.py --base Qwen/Qwen3.5-4B --adapter outputs/tg_v1 \\
        --out models/merged/tg_v1
"""
from __future__ import annotations

import argparse
import json
import os
import shutil

import torch
from safetensors import safe_open
from safetensors.torch import save_file

# Adaptörden gelmeyen, base dizininden merged dizine kopyalanacak dosyalar.
# (safetensors + index hariç — onları biz yazıyoruz.)
SKIP_SUFFIX = (".safetensors", ".gitattributes")
SKIP_NAMES = ("model.safetensors.index.json",)


def parse_args():
    p = argparse.ArgumentParser()
    # ⚠️ ADR-0026: base GÖMÜLÜ DEĞİL, varsayılanı YOK — tanımsızsa ERKEN patla.
    p.add_argument("--base", required=True,
                   help="HF repo-id (cache'te indirilmiş) ya da yerel dizin")
    p.add_argument("--adapter", required=True, help="LoRA adaptör dizini")
    p.add_argument("--out", required=True, help="birleştirilmiş HF dizini (üzerine yazar)")
    return p.parse_args()


def resolve_base(ref: str) -> str:
    """Yerel dizin ya da HF cache snapshot'ı → mutlak yol."""
    if os.path.isdir(ref):
        return ref
    from huggingface_hub import snapshot_download
    return snapshot_download(ref, local_files_only=True)


def load_deltas(adapter_dir: str) -> tuple[dict[str, tuple[torch.Tensor, torch.Tensor]], float]:
    """adapter_model.safetensors → {base tensör adı: (A, B)} + ölçek."""
    cfg = json.load(open(os.path.join(adapter_dir, "adapter_config.json")))
    # Bu script düz LoRA içindir; DoRA/rsLoRA farklı ölçek/ayrıştırma demek — sessizce
    # yanlış ΔW üretmektense dur.
    if cfg.get("use_dora") or cfg.get("use_rslora"):
        raise SystemExit("[merge] 🚫 DoRA/rsLoRA destelenmiyor — ΔW ölçeği farklı.")
    if cfg.get("modules_to_save"):
        raise SystemExit(f"[merge] 🚫 modules_to_save dolu: {cfg['modules_to_save']} "
                         "— bunlar LoRA değil, tam tensör; ayrı ele alınmalı.")
    scale = cfg["lora_alpha"] / cfg["r"]

    pairs: dict[str, dict[str, torch.Tensor]] = {}
    with safe_open(os.path.join(adapter_dir, "adapter_model.safetensors"), "pt") as f:
        for k in f.keys():
            stem, _, tail = k.partition(".lora_")
            side = tail[0]                       # 'A' | 'B'
            # PEFT sarmalayıcı öneki → base index anahtarı
            name = stem.removeprefix("base_model.model.") + ".weight"
            pairs.setdefault(name, {})[side] = f.get_tensor(k)

    deltas = {}
    for name, ab in pairs.items():
        if set(ab) != {"A", "B"}:
            raise SystemExit(f"[merge] 🚫 {name}: eksik LoRA yarısı ({sorted(ab)})")
        deltas[name] = (ab["A"], ab["B"])
    return deltas, scale


def main():
    a = parse_args()
    base_dir = resolve_base(a.base)
    deltas, scale = load_deltas(a.adapter)
    print(f"[merge] base={base_dir}")
    print(f"[merge] adaptör={a.adapter} | {len(deltas)} LoRA çifti | ölçek α/r={scale}")

    index = json.load(open(os.path.join(base_dir, "model.safetensors.index.json")))
    weight_map: dict[str, str] = index["weight_map"]
    shards: dict[str, list[str]] = {}
    for tensor_name, shard in weight_map.items():
        shards.setdefault(shard, []).append(tensor_name)

    os.makedirs(a.out, exist_ok=True)
    applied = 0
    for shard, names in shards.items():
        out_tensors = {}
        with safe_open(os.path.join(base_dir, shard), "pt") as f:
            for name in names:
                w = f.get_tensor(name)
                if name in deltas:
                    A, B = deltas[name]
                    if B.shape[0] != w.shape[0] or A.shape[1] != w.shape[1]:
                        raise SystemExit(
                            f"[merge] 🚫 şekil uyuşmazlığı {name}: W{tuple(w.shape)} "
                            f"vs B{tuple(B.shape)}@A{tuple(A.shape)}")
                    dw = (B.float() @ A.float()) * scale
                    w = (w.float() + dw).to(w.dtype)
                    applied += 1
                out_tensors[name] = w
        save_file(out_tensors, os.path.join(a.out, shard), metadata={"format": "pt"})
        print(f"[merge]   {shard}: {len(names)} tensör yazıldı")
        del out_tensors

    # 🚨 Sessiz-bozulma kapısı: adaptörün bir kısmı base'de karşılık bulamazsa,
    # dosya yine yazılır ve "merge oldu" görünür. Eksik uygulama = geçersiz τ.
    if applied != len(deltas):
        missing = sorted(set(deltas) - set(weight_map))
        raise SystemExit(f"[merge] 🚫 {applied}/{len(deltas)} uygulandı. "
                         f"Base'de bulunamayan: {missing[:5]}")

    for fn in sorted(os.listdir(base_dir)):
        if fn.endswith(SKIP_SUFFIX) or fn in SKIP_NAMES:
            continue
        src = os.path.realpath(os.path.join(base_dir, fn))
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(a.out, fn))
    shutil.copy2(os.path.realpath(os.path.join(base_dir, "model.safetensors.index.json")),
                 os.path.join(a.out, "model.safetensors.index.json"))

    print(f"[merge] ✅ {applied}/{len(deltas)} LoRA çifti uygulandı → {a.out}")


if __name__ == "__main__":
    main()
