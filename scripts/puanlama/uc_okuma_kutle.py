#!/usr/bin/env python3
"""Üç-okuma kütle türetici — ALET / GÖZ-orta / GÖZ-katı (ADIM 6.5, `v1-son-iş` planı §2.1).

NEDEN VAR: `0,6925 · 0,7050 · 0,7425` (3.5 Flash, `gpt-4o-mini` hakem) bugüne kadar
depoda YALNIZ düz metin tablolarda vardı — onu üreten hiçbir betik yoktu (BULGU-A,
2026-09-12). Bu betik o türetmeyi koda geçirir ve **kalibrasyon kapısı** taşır: aynı
girdiyle koşulduğunda yayımlanmış üç sayıyı birebir üretmelidir (bkz. `tests/`).

FORMÜL (miras: `docs/superpowers/plans/2026-09-12-v1-son-is.md` §2.1):

    kütle(okuma) = Σ faithfulness( okumanın CEVAP saydığı kalemler ) / n_toplam

ALET okuması "cevap sayılan" kümeyi çekinme dedektöründen (`score_abstention.exact_reject`,
mod "data") alır. GÖZ okumaları bu kümeye elle doğrulanmış kalem id'lerini EKLER — hiçbir
kalemi çıkarmaz (bu round'da göz her zaman aleti genişletiyor, daraltmıyor).

⚠️ MİRAS ALINAN KÜME ÜYELİĞİDİR, PUAN DEĞİL: eklenen kalemlerin `faithfulness`'ı yeniden
puanlanan hakemin gnd dosyasından okunur — 1,0 varsayılmaz.

Hesap `kutle.py`'dedir (F0.5 a·c): payda dondurulmuş kümenin boyutu, eksik ya da tutarsız
girdide puanlama durur. Sıfır iddialı cevaplanmış kalem 0 puan alır — bu betiğin formülü
zaten buydu; `harness_tablo.py` ile ayrışma (tuzak 2.22) artık mümkün değil.

Kullanım:
  python scripts/puanlama/uc_okuma_kutle.py \\
      --details outputs/eval/faz0/f04-rakip-onsozsuz/h1_3_5_flash_nb_detail.jsonl \\
      --gnd outputs/eval/faz0/f04-rakip-onsozsuz/gnd_h1_3_5_flash_nb.jsonl \\
      --kume data/eval/dev/core_hard.jsonl --goz-orta-ekle 28 --goz-kati-ekle 15,24,27
"""
import argparse
import json
import os
import sys

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

from kutle import DondurulmusKume, kutle_hesapla  # noqa: E402
from olcum_aleti import GUNCEL  # noqa: E402
from part_dosya import tamamlanmis_jsonl  # noqa: E402


def _id_set(s):
    """'15,24,27' → {15,24,27}; boş/None → set()."""
    if not s:
        return set()
    return {int(x) for x in str(s).split(",") if x.strip() != ""}


def uc_okuma(detay_satirlari, gnd_satirlari, kume, goz_orta_ekle=(), goz_kati_ekle=()):
    """Üç okumayı da hesaplar. `goz_kati_ekle`, `goz_orta_ekle`'nin ÜSTÜNE eklenir
    (kümülatif — GÖZ-katı her zaman GÖZ-orta'yı içerir)."""
    orta = set(goz_orta_ekle)
    kati = orta | set(goz_kati_ekle)

    def okuma(ekle):
        s = kutle_hesapla(detay_satirlari, gnd_satirlari, kume, GUNCEL, goz_ekle=frozenset(ekle))
        toplam = sum(k.puan for k in s.kalemler if k.cevaplandi and k.puan is not None)
        return {"n_cevaplanan": s.n_cevaplanan, "toplam": round(toplam, 4), "kutle": s.kutle}

    return {
        "n": kume.boyut,
        "kume": kume.kunye(),
        "olcum_aleti": GUNCEL.kunye(),
        "ALET": okuma(set()),
        "GOZ_ORTA": {**okuma(orta), "eklenen": sorted(orta)},
        "GOZ_KATI": {**okuma(kati), "eklenen": sorted(kati)},
    }


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--details", required=True, help="h1_..._detail.jsonl (cevap metni + id)")
    p.add_argument("--gnd", required=True, help="gnd_..._.jsonl (groundedness.py çıktısı)")
    p.add_argument("--kume", required=True,
                   help="dondurulmuş soru kümesi (ör. data/eval/dev/core_hard.jsonl) — payda buradan")
    p.add_argument("--goz-orta-ekle", default="", help="GÖZ-orta'nın ALET'e eklediği id'ler, virgüllü")
    p.add_argument("--goz-kati-ekle", default="", help="GÖZ-katı'nın GÖZ-orta'ya eklediği id'ler, virgüllü")
    p.add_argument("--out", default="")
    return p.parse_args()


def main():
    a = parse_args()
    detay = tamamlanmis_jsonl(a.details)
    gnd = tamamlanmis_jsonl(a.gnd)
    sonuc = uc_okuma(detay, gnd, DondurulmusKume.yukle(a.kume),
                     _id_set(a.goz_orta_ekle), _id_set(a.goz_kati_ekle))
    print(json.dumps(sonuc, ensure_ascii=False, indent=2))
    if a.out:
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(sonuc, f, ensure_ascii=False, indent=2, sort_keys=True)
        print(f"[uc-okuma] → {a.out}")


if __name__ == "__main__":
    main()
