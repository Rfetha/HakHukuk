#!/usr/bin/env python3
"""F0.7 — τ_g / τ_a seyreklik tablosu: ham TIES'te hangi kolun ne kadarı sağ kalıyor (CPU, $0).

NEDEN: B4 — τ_a birleştirmede zayıflıyor (M2b 0,987 → 0,766). Olası mekanizma TIES'in iki adımı:
kırpma (her kolda en büyük `trim_k` oranı kalır) ve işaret seçimi (kütle-ağırlıklı toplamın işareti;
büyük normlu kol küçüğünü ezebilir). Bu betik her tensörde, kol başına, şunları ölçer:
  kirpma_sonrasi   kırpmadan sağ kalan kare kütle / kolun kare kütlesi
  isaret_sonrasi   kırpma + işaret seçiminden sağ kalan kare kütle / kolun kare kütlesi
  izdusum          ⟨birleşik, τ⟩ / ‖τ‖²  (birleşik vektör kolu kendi yönünde ne kadar taşıyor)
Modül türüne göre ve toplamda kütle ağırlıklı toplanır.

ΔW `merge_lora.load_deltas` + `merge_ties.dw` ile açılır (yeni materyalize kodu yok). Kırpma ve
işaret seçimi `merge_ties.ties` ile aynı adımlardır; her tensörde birleşik sonuç `ties()`'in çıktısıyla
bit düzeyinde karşılaştırılır, tutmazsa betik durur.

Kullanım:
  python scripts/egitim/birlestirme/seyreklik_tablosu.py --adapter tg=outputs/tg_v1 --adapter ta=outputs/ta_v1 \\
      --trim-k 0.2 --out outputs/egitim/f07-seyreklik/seyreklik.json
"""
import argparse
import datetime
import hashlib
import json
import os

import torch

from merge_lora import load_deltas
from merge_ties import dw, modul_adi, ties


def tensor_istatistigi(taus: dict, trim_k: float) -> dict:
    """Bir tensör için kol başına kare kütle sayaçları + oranlar; `_birlesik` = ham TIES sonucu (bf16)."""
    adlar = list(taus)
    flat = torch.stack([taus[a] for a in adlar]).reshape(len(adlar), -1).float()
    n = flat.shape[1]
    tut = max(1, int(round(n * trim_k)))
    esik = flat.abs().kthvalue(n - tut + 1, dim=1, keepdim=True).values
    kirp = torch.where(flat.abs() >= esik, flat, torch.zeros_like(flat))
    isaret = torch.sign(kirp.sum(dim=0))
    uyusan = (torch.sign(kirp) == isaret.unsqueeze(0)) & (kirp != 0) & (isaret != 0).unsqueeze(0)
    birlesik = (kirp * uyusan).sum(dim=0) / uyusan.sum(dim=0).clamp(min=1)

    sonuc = {"_birlesik": birlesik.reshape(taus[adlar[0]].shape).to(torch.bfloat16)}
    for i, ad in enumerate(adlar):
        kare = flat[i].pow(2).sum().item()
        sayac = {"kare_norm": kare,
                 "kirpma_kare": kirp[i].pow(2).sum().item(),
                 "isaret_kare": (kirp[i] * uyusan[i]).pow(2).sum().item(),
                 "ic_carpim": (birlesik @ flat[i]).item()}
        sonuc[ad] = {**sayac, **_oranlar(sayac)}
    return sonuc


def _oranlar(s):
    k = s["kare_norm"]
    return {"kirpma_sonrasi": s["kirpma_kare"] / k if k else 0.0,
            "isaret_sonrasi": s["isaret_kare"] / k if k else 0.0,
            "izdusum": s["ic_carpim"] / k if k else 0.0}


def _topla(hedef, sayac):
    for alan in ("kare_norm", "kirpma_kare", "isaret_kare", "ic_carpim"):
        hedef[alan] = hedef.get(alan, 0.0) + sayac[alan]


def _sha256(yol):
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for parca in iter(lambda: f.read(1 << 20), b""):
            h.update(parca)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--adapter", action="append", required=True, help="ad=dizin (en az iki)")
    p.add_argument("--trim-k", type=float, required=True, help="tgta_v1: 0,2 (kollar.md)")
    p.add_argument("--out", required=True)
    a = p.parse_args()
    adaptorler = dict(x.split("=", 1) for x in a.adapter)
    if len(adaptorler) < 2:
        raise SystemExit("[seyreklik] 🚫 en az iki kol gerekli")

    yuk = {ad: load_deltas(d) for ad, d in adaptorler.items()}
    anahtarlar = [set(deltas) for deltas, _ in yuk.values()]
    if any(k != anahtarlar[0] for k in anahtarlar):
        raise SystemExit("[seyreklik] 🚫 kolların tensör kümeleri farklı — aynı rejimden değiller")

    modul, toplam = {}, {ad: {} for ad in adaptorler}
    for ad_t in sorted(anahtarlar[0]):
        taus = {ad: dw(*deltas[ad_t], olcek) for ad, (deltas, olcek) in yuk.items()}
        s = tensor_istatistigi(taus, a.trim_k)
        beklenen, _ = ties(torch.stack(list(taus.values())), a.trim_k)
        if not torch.equal(s["_birlesik"], beklenen):
            raise SystemExit(f"[seyreklik] 🚫 {ad_t}: hesap ties() ile aynı sonucu vermiyor")
        m = modul_adi(ad_t)
        for ad in adaptorler:
            _topla(modul.setdefault(m, {}).setdefault(ad, {}), s[ad])
            _topla(toplam[ad], s[ad])

    tablo = {m: {ad: {**v, **_oranlar(v), "norm": v["kare_norm"] ** 0.5} for ad, v in kollar.items()}
             for m, kollar in sorted(modul.items())}
    for ad, v in toplam.items():
        v.update(_oranlar(v), norm=v["kare_norm"] ** 0.5)
    for m in tablo:
        for ad in adaptorler:
            tablo[m][ad]["norm_payi"] = tablo[m][ad]["kare_norm"] / toplam[ad]["kare_norm"]
    cikti = {
        "tarih": datetime.date.today().isoformat(),
        "trim_k": a.trim_k,
        "adaptorler": {ad: {"dizin": d, "sha256": _sha256(os.path.join(d, "adapter_model.safetensors")),
                            "olcek": yuk[ad][1]} for ad, d in adaptorler.items()},
        "n_tensor": len(anahtarlar[0]),
        "ties_ile_tutarlilik": f"{len(anahtarlar[0])}/{len(anahtarlar[0])} tensör bit düzeyinde aynı",
        "torch": torch.__version__,
        "toplam": toplam,
        "modul": tablo,
    }
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(cikti, f, ensure_ascii=False, indent=2)

    adlar = list(adaptorler)
    print(f"| modül | " + " | ".join(f"‖τ_{x}‖ payı · kırpma · işaret · izdüşüm" for x in adlar) + " |")
    for m, kollar in tablo.items():
        print(f"| {m} | " + " | ".join(
            f"{kollar[x]['norm_payi']:.3f} · {kollar[x]['kirpma_sonrasi']:.3f} · "
            f"{kollar[x]['isaret_sonrasi']:.3f} · {kollar[x]['izdusum']:.3f}" for x in adlar) + " |")
    print(f"| TOPLAM | " + " | ".join(
        f"‖τ‖={toplam[x]['norm']:.4f} · {toplam[x]['kirpma_sonrasi']:.3f} · "
        f"{toplam[x]['isaret_sonrasi']:.3f} · {toplam[x]['izdusum']:.3f}" for x in adlar) + " |")
    print(f"[seyreklik] → {a.out}")


if __name__ == "__main__":
    main()
