#!/usr/bin/env python3
"""GGUF (Q4_K_M) → Hugging Face biçimi (yalnız metin, bf16): vLLM'in ana desteğiyle açabileceği klasör.

Neden: vLLM'in GGUF eklentisi Qwen3.5'i tanımıyor (`Unknown gguf model_type: qwen3_5`, vLLM pilotu aşama A).
Ne yapar: her tensörü GGUF'un kendi açma fonksiyonuyla açar, llama.cpp'nin dönüşümlerini geri alır, bf16 yazar.
  · norm ağırlıkları  GGUF'ta `+1` eklenmiş (sıfır merkezli RMSNorm) → `-1`
  · doğrusal dikkat   llama.cpp 32 değer başını "döşemeli" dizer [j*NK + k]; HF'de k-başına gruplu [k*vpk + j]
    (qkv'nin v kısmı, z, out_proj sütunları, alpha, beta, conv1d'nin v kanalları, A_log, dt_bias) → geri dizilir
  · `A_log` = log(-ssm_a) (llama.cpp `-exp(A_log)` saklar)
  · MTP katmanı (blk.32.*) normal çıkarımda kullanılmaz, açıkça atlanır; başka bilinmeyen tensör DURDURUR
Doğrulama (kapı): her tensör orijinal (sıkıştırılmamış) ağırlıkla karşılaştırılır; göreli hata sıkıştırma
gürültüsünü (Q4_K ~%7,5 · Q6_K ~%1,8 · F32 ~0) aşarsa çeviri durur. Yanlış diziliş hata vermez ama modeli
bozar; yanlış dizilişte hata %40-136 çıkar (ölçüldü, 2026-10-15), eşikler bunu ayırır.

Kullanım:
  python scripts/olcum_uretim/pilot/gguf_hf_cevir.py --gguf models/gguf/tgta_v1-q4_k_m.gguf \\
      --yapilandirma-dizini models/merged/tgta_v1 --cikti /tmp/hf_q4km --orijinal-dizin models/merged/tgta_v1
"""
# ── scripts/ yol köprüsü (T5 2026-09-07 · ADR-0112 2026-10-16) ───────────────
# Kardeş modüller iç içe alt klasörlerde de bulunsun diye scripts/ kökü, altındaki HER
# derinlikteki klasör ve repo kökü sys.path'e girer. Uzantısız `import X` bu köprü olmadan
# taşımada SESSİZCE kırılır: ImportError çalışma zamanında, bazen GPU koşusunun ortasında.
# ⚠️ 39 dosyada BİREBİR aynı; değiştirirsen hepsinde değiştir (grep: "yol köprüsü").
import os, sys
_K = os.path.abspath(__file__)
_K = _K[:_K.rindex(os.sep + "scripts" + os.sep)] + os.sep + "scripts"  # dışarıda: ValueError
_Y = []
for _y, _alt, _f in os.walk(_K):
    _alt[:] = sorted(_a for _a in _alt if _a[0] not in "_.")
    _Y.append(_y)
sys.path[:0] = [*_Y, os.path.dirname(_K)]
# ─────────────────────────────────────────────────────────────────────────────
import argparse  # noqa: E402
import glob  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import shutil  # noqa: E402
from typing import NamedTuple  # noqa: E402

import numpy as np  # noqa: E402

KATMAN_SAYISI = 32          # Qwen3.5-4B; blk.32 = MTP katmanı (atlanır)
# Sıkıştırma tipine göre izin verilen göreli hata (||çevrilen − orijinal|| / ||orijinal||).
ESIK = {"F32": 1e-3, "F16": 1e-3, "BF16": 1e-3, "Q4_K": 0.09, "Q6_K": 0.025}
F32_KALIR = ("linear_attn.A_log", "linear_attn.norm.weight")      # orijinalde F32 (öbürleri bf16)
SHARD_BAYT = 2 * 1024 ** 3
TOKENIZER_DOSYALARI = ("tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt", "chat_template.jinja")

_TABLO = {
    "attn_norm.weight": ("input_layernorm.weight", "norm"),
    "post_attention_norm.weight": ("post_attention_layernorm.weight", "norm"),
    "ffn_gate.weight": ("mlp.gate_proj.weight", "duz"),
    "ffn_up.weight": ("mlp.up_proj.weight", "duz"),
    "ffn_down.weight": ("mlp.down_proj.weight", "duz"),
    "attn_q.weight": ("self_attn.q_proj.weight", "duz"),
    "attn_k.weight": ("self_attn.k_proj.weight", "duz"),
    "attn_v.weight": ("self_attn.v_proj.weight", "duz"),
    "attn_output.weight": ("self_attn.o_proj.weight", "duz"),
    "attn_q_norm.weight": ("self_attn.q_norm.weight", "norm"),
    "attn_k_norm.weight": ("self_attn.k_norm.weight", "norm"),
    "attn_qkv.weight": ("linear_attn.in_proj_qkv.weight", "qkv"),
    "attn_gate.weight": ("linear_attn.in_proj_z.weight", "z"),
    "ssm_out.weight": ("linear_attn.out_proj.weight", "out"),
    "ssm_alpha.weight": ("linear_attn.in_proj_a.weight", "ab"),
    "ssm_beta.weight": ("linear_attn.in_proj_b.weight", "ab"),
    "ssm_a": ("linear_attn.A_log", "a"),
    "ssm_dt.bias": ("linear_attn.dt_bias", "dt"),
    "ssm_conv1d.weight": ("linear_attn.conv1d.weight", "conv"),
    "ssm_norm.weight": ("linear_attn.norm.weight", "duz"),
}
_UST = {"token_embd.weight": ("model.embed_tokens.weight", "duz"), "output_norm.weight": ("model.norm.weight", "norm")}


class Boyut(NamedTuple):
    k_bas: int
    v_bas: int
    k_boy: int
    v_boy: int


def boyutlar(config: dict) -> Boyut:
    t = config.get("text_config", config)
    return Boyut(t["linear_num_key_heads"], t["linear_num_value_heads"], t["linear_key_head_dim"],
                 t["linear_value_head_dim"])


def ters_baslar(x, k_bas: int, v_bas: int, eksen: int, blok: int):
    """llama.cpp'nin döşemeli v-başı dizilişini (gguf[j*NK + k]) HF dizilişine (hf[k*vpk + j]) geri çevirir.
    `eksen` boyunca uzunluk v_bas*blok olmalı (blok = bir başın kapladığı satır/sütun)."""
    vpk = v_bas // k_bas
    perm = np.array([(h % k_bas) * vpk + h // k_bas for h in range(v_bas)])
    x = np.moveaxis(x, eksen, 0)
    s = x.shape
    if s[0] != v_bas * blok:
        raise SystemExit(f"[gguf-hf] 🚫 baş yeniden dizme: eksen uzunluğu {s[0]}, beklenen {v_bas}×{blok}")
    xr = x.reshape(v_bas, blok, *s[1:])
    out = np.empty_like(xr)
    out[perm] = xr
    return np.moveaxis(out.reshape(s), 0, eksen)


def hedef_ad(ad: str, katman_sayisi: int = KATMAN_SAYISI):
    """GGUF tensör adı → HF adı; atlanacak (MTP) tensörde None; bilinmeyen adda DURUR."""
    if ad in _UST:
        return _UST[ad][0]
    m = re.fullmatch(r"blk\.(\d+)\.(.+)", ad)
    if m is None:
        raise SystemExit(f"[gguf-hf] 🚫 bilinmeyen tensör adı: {ad}")
    n, ek = int(m.group(1)), m.group(2)
    if n >= katman_sayisi:
        return None
    if ek not in _TABLO:
        raise SystemExit(f"[gguf-hf] 🚫 bilinmeyen tensör adı: {ad}")
    return f"model.layers.{n}.{_TABLO[ek][0]}"


def _donusum(ad: str) -> str:
    if ad in _UST:
        return _UST[ad][1]
    return _TABLO[re.fullmatch(r"blk\.\d+\.(.+)", ad).group(1)][1]


def hata_kapisi(ad: str, tip: str, hata: float) -> None:
    if tip not in ESIK:
        raise SystemExit(f"[gguf-hf] 🚫 {ad}: {tip} tipi için eşik tanımlı değil — tanımlamadan çeviri yapılmaz")
    if not hata <= ESIK[tip]:
        raise SystemExit(f"[gguf-hf] 🚫 doğrulama {ad}: göreli hata {hata:.4f} > eşik {ESIK[tip]} ({tip}) — "
                         f"eşleme ya da diziliş yanlış olabilir")


class GGUFDosyasi:
    def __init__(self, yol: str):
        import gguf
        self._gguf = gguf
        self._t = {t.name: t for t in gguf.GGUFReader(yol).tensors}

    def adlar(self) -> list[str]:
        return list(self._t)

    def tip(self, ad: str) -> str:
        return self._gguf.GGMLQuantizationType(self._t[ad].tensor_type).name

    def oku(self, ad: str):
        from gguf.quants import dequantize
        t = self._t[ad]
        return dequantize(t.data, t.tensor_type).astype(np.float32)


class OrijinalAgirliklar:
    """Sıkıştırılmamış (bf16) orijinal ağırlıklar; yalnız doğrulama için."""

    def __init__(self, dizin: str):
        from safetensors import safe_open
        self._safe_open = safe_open
        self.config = json.load(open(os.path.join(dizin, "config.json"), encoding="utf-8"))
        self._dosya = {}
        for f in sorted(glob.glob(os.path.join(dizin, "*.safetensors"))):
            with safe_open(f, "pt") as s:
                for k in s.keys():
                    self._dosya[k] = f

    def al(self, ad: str):
        with self._safe_open(self._dosya[ad], "pt") as s:
            return s.get_tensor(ad).float().numpy()


def _orijinal_ad(hf_ad: str) -> str:
    return hf_ad.replace("model.layers.", "model.language_model.layers.").replace(
        "model.embed_tokens.", "model.language_model.embed_tokens.").replace(
        "model.norm.", "model.language_model.norm.")


def dogrula(hf_ad: str, y, tip: str, orij: OrijinalAgirliklar) -> float:
    o = orij.al(_orijinal_ad(hf_ad))
    if o.shape != y.shape:
        raise SystemExit(f"[gguf-hf] 🚫 doğrulama {hf_ad}: şekil {y.shape} ↔ orijinal {o.shape}")
    hata = float(np.linalg.norm(y - o) / np.linalg.norm(o))
    hata_kapisi(hf_ad, tip, hata)
    return hata


def cevir_tensor(ad: str, dosya: GGUFDosyasi, boyut: Boyut):
    """→ (HF adı, float32 dizi, hedef dtype adı) ya da MTP tensöründe None."""
    hf = hedef_ad(ad)
    if hf is None:
        return None
    x, tur = dosya.oku(ad), _donusum(ad)
    kb, vb, kd, vd = boyut
    qk = 2 * kb * kd                                  # qkv/conv: önce q ve k (dizilmemiş), sonra v
    if tur == "norm":
        x = x - 1.0
    elif tur == "qkv":
        x = np.concatenate([x[:qk], ters_baslar(x[qk:], kb, vb, 0, vd)])
    elif tur == "z":
        x = ters_baslar(x, kb, vb, 0, vd)
    elif tur == "out":
        x = ters_baslar(x, kb, vb, 1, vd)
    elif tur in ("ab", "dt"):
        x = ters_baslar(x, kb, vb, 0, 1)
    elif tur == "a":
        x = np.log(-ters_baslar(x, kb, vb, 0, 1))
    elif tur == "conv":
        x = np.concatenate([x[:qk], ters_baslar(x[qk:], kb, vb, 0, vd)])[:, None, :]
    return hf, x, "float32" if hf.endswith(F32_KALIR) else "bfloat16"


def cevir(gguf_yolu: str, yapilandirma_dizini: str, cikti: str, orijinal_dizin: str | None) -> dict:
    import torch
    from safetensors.torch import save_file
    from toplu_uret import metin_yapilandirmasi
    dosya = GGUFDosyasi(gguf_yolu)
    tam = json.load(open(os.path.join(yapilandirma_dizini, "config.json"), encoding="utf-8"))
    boyut = boyutlar(tam)
    orij = OrijinalAgirliklar(orijinal_dizin) if orijinal_dizin else None
    os.makedirs(cikti, exist_ok=True)
    agirlik_haritasi, tablo, parti, parti_bayt, sira, atlanan = {}, [], {}, 0, 0, []

    def bosalt():
        nonlocal parti, parti_bayt, sira
        if not parti:
            return
        ad = f"model-{sira:05d}.safetensors"
        save_file(parti, os.path.join(cikti, ad))
        agirlik_haritasi.update({k: ad for k in parti})
        parti, parti_bayt, sira = {}, 0, sira + 1

    for ad in dosya.adlar():
        s = cevir_tensor(ad, dosya, boyut)
        if s is None:
            atlanan.append(ad)
            continue
        hf, y, dtype = s
        hata = dogrula(hf, y, dosya.tip(ad), orij) if orij else None
        t = torch.from_numpy(np.ascontiguousarray(y)).to(getattr(torch, dtype))
        tablo.append({"hf": hf, "gguf": ad, "tip": dosya.tip(ad), "dtype": dtype, "sekil": list(t.shape),
                      "goreli_hata": hata, "sha256": hashlib.sha256(t.view(torch.uint8).numpy().tobytes()).hexdigest()})
        parti[hf] = t
        parti_bayt += t.numel() * t.element_size()
        if parti_bayt >= SHARD_BAYT:
            bosalt()
    bosalt()
    json.dump({"metadata": {}, "weight_map": agirlik_haritasi},
              open(os.path.join(cikti, "model.safetensors.index.json"), "w", encoding="utf-8"), indent=1)
    cfg = metin_yapilandirmasi(tam)
    cfg.update({"mtp_num_hidden_layers": 0, "dtype": "bfloat16"})
    json.dump(cfg, open(os.path.join(cikti, "config.json"), "w", encoding="utf-8"), indent=1)
    for d in TOKENIZER_DOSYALARI:
        shutil.copy(os.path.join(yapilandirma_dizini, d), os.path.join(cikti, d))
    kunye = {"gguf": os.path.basename(gguf_yolu), "n_tensor": len(tablo), "atlanan": atlanan,
             "dogrulandi": bool(orij), "tensorler": tablo}
    json.dump(kunye, open(os.path.join(cikti, "CEVIRI_KUNYE.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return kunye


def main(argv=None):
    p = argparse.ArgumentParser(description="GGUF → HF (bf16, yalnız metin)")
    p.add_argument("--gguf", required=True)
    p.add_argument("--yapilandirma-dizini", required=True, help="config.json ve tokenizer dosyalarının klasörü")
    p.add_argument("--cikti", required=True)
    p.add_argument("--orijinal-dizin", help="verilirse her tensör orijinalle doğrulanır")
    a = p.parse_args(argv)
    k = cevir(a.gguf, a.yapilandirma_dizini, a.cikti, a.orijinal_dizin)
    hatalar = [t["goreli_hata"] for t in k["tensorler"] if t["goreli_hata"] is not None]
    print(f"[gguf-hf] {k['n_tensor']} tensör yazıldı, {len(k['atlanan'])} atlandı (MTP) → {a.cikti}"
          + (f" · doğrulandı: en büyük göreli hata {max(hatalar):.4f}" if hatalar else " · doğrulanmadı"), flush=True)


if __name__ == "__main__":
    main()
