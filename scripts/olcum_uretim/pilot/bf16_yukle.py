#!/usr/bin/env python3
"""Orijinal bf16 ağırlıkların Modal hacmine yüklenmesi (vLLM pilotu, spec 2026-10-15 bölüm 4).

  manifest  yerel dosyaların bayt ve sha256 tablosunu JSON'a yazar (konteyner hacimdeki dosyaları bununla karşılaştırır)
  put       `modal volume put` komutlarını BASAR. Çalıştırmak dışarı giden iştir; kullanıcı onayıyla elle yapılır.

Kullanım:
  python scripts/olcum_uretim/pilot/bf16_yukle.py manifest --dizin models/merged/tgta_v1 \\
      --cikti outputs/eval/f0/f016-vllm-pilot/bf16_manifest.json
  python scripts/olcum_uretim/pilot/bf16_yukle.py put --dizin models/merged/tgta_v1
"""
import argparse
import glob
import hashlib
import json
import os
import shlex

HACIM = "hukuk-outputs"
HACIM_YOLU = "/f016-vllm-pilot/bf16"
DESENLER = ("*.safetensors", "model.safetensors.index.json", "config.json", "generation_config.json",
            "tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt", "chat_template.jinja",
            "preprocessor_config.json", "video_preprocessor_config.json")


def dosyalar(dizin: str) -> list[str]:
    bulunan = sorted({os.path.basename(y) for d in DESENLER for y in glob.glob(os.path.join(dizin, d))})
    if not any(a.endswith(".safetensors") for a in bulunan):
        raise SystemExit(f"[bf16-yukle] 🚫 {dizin} içinde .safetensors dosyası yok")
    return bulunan


def _sha256(yol: str) -> str:
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for parca in iter(lambda: f.read(1 << 20), b""):
            h.update(parca)
    return h.hexdigest()


def manifest(dizin: str, adlar: list[str] | None = None) -> dict:
    sonuc = {}
    for ad in (adlar if adlar is not None else dosyalar(dizin)):
        yol = os.path.join(dizin, ad)
        if os.path.exists(yol):
            sonuc[ad] = {"bayt": os.path.getsize(yol), "sha256": _sha256(yol)}
    return {"dizin": os.path.basename(os.path.normpath(dizin)), "dosyalar": sonuc}


def farklar(beklenen: dict, eldeki: dict) -> list[str]:
    cikti = []
    for ad, b in beklenen["dosyalar"].items():
        e = eldeki["dosyalar"].get(ad)
        if e is None:
            cikti.append(f"{ad}: eksik")
        elif e["bayt"] != b["bayt"]:
            cikti.append(f"{ad}: bayt {e['bayt']} ≠ {b['bayt']}")
        elif e["sha256"] != b["sha256"]:
            cikti.append(f"{ad}: sha256 farklı")
    return cikti


def put_komutlari(dizin: str) -> list[list[str]]:
    return [["modal", "volume", "put", HACIM, os.path.join(dizin, ad), f"{HACIM_YOLU}/{ad}"]
            for ad in dosyalar(dizin)]


def main(argv=None):
    p = argparse.ArgumentParser(description="bf16 ağırlıkların Modal hacmine yüklenmesi")
    p.add_argument("komut", choices=("manifest", "put"))
    p.add_argument("--dizin", required=True)
    p.add_argument("--cikti", help="manifest için JSON yolu")
    a = p.parse_args(argv)
    if a.komut == "manifest":
        if not a.cikti:
            raise SystemExit("[bf16-yukle] 🚫 manifest için --cikti zorunlu")
        m = manifest(a.dizin)
        os.makedirs(os.path.dirname(a.cikti), exist_ok=True)
        with open(a.cikti, "w", encoding="utf-8") as f:
            json.dump(m, f, ensure_ascii=False, indent=2)
        print(f"[bf16-yukle] {len(m['dosyalar'])} dosya → {a.cikti}")
    else:
        for k in put_komutlari(a.dizin):
            print(shlex.join(k))


if __name__ == "__main__":
    main()
