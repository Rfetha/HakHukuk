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

Kullanım:
  python scripts/puanlama/uc_okuma_kutle.py \\
      --details outputs/eval/f04-rakip-onsozsuz/h1_3_5_flash_nb_detail.jsonl \\
      --gnd outputs/eval/f04-rakip-onsozsuz/gnd_h1_3_5_flash_nb.jsonl \\
      --goz-orta-ekle 28 --goz-kati-ekle 15,24,27
"""
import argparse
import json
import os
import sys

_K = os.path.dirname(os.path.abspath(__file__))
_K = _K if os.path.basename(_K) == "scripts" else os.path.dirname(_K)
sys.path[:0] = [_K, *(os.path.join(_K, _d) for _d in sorted(os.listdir(_K))
                      if os.path.isdir(os.path.join(_K, _d)) and _d[0] not in "_."),
                os.path.dirname(_K)]

from score_abstention import exact_reject  # noqa: E402


def _load_jsonl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def _id_set(s):
    """'15,24,27' → {15,24,27}; boş/None → set()."""
    if not s:
        return set()
    return {int(x) for x in str(s).split(",") if x.strip() != ""}


def alet_cevaplanan_kumesi(detay_satirlari):
    """ALET okumasının 'cevap sayılan' kümesi — dedektör (`exact_reject`, mod 'data')."""
    return {r.get("id", i) for i, r in enumerate(detay_satirlari)
            if not exact_reject(r.get("cevap", ""), "data")}


def kutle(id_kumesi, gnd_map, n_toplam):
    """kütle(okuma) = Σ faithfulness(id_kumesi'ndeki, puanı olan kalemler) / n_toplam.

    Puanı olmayan (`faithfulness` None — sıfır iddia çıkarılmış) bir kalem kümede olsa
    bile toplama 0 katkı yapar; bu, aletin kendi `coverage × A1` tanımıyla denktir
    (bu round'da hiçbir kalem bu farkı göstermedi — doğrulama testinde sınanır)."""
    s = sum(gnd_map[i]["faithfulness"] for i in id_kumesi
            if i in gnd_map and gnd_map[i].get("faithfulness") is not None)
    return round(s, 4), round(s / n_toplam, 4) if n_toplam else None


def uc_okuma(detay_satirlari, gnd_satirlari, goz_orta_ekle=(), goz_kati_ekle=()):
    """Üç okumayı da hesaplar. `goz_kati_ekle`, `goz_orta_ekle`'nin ÜSTÜNE eklenir
    (kümülatif — GÖZ-katı her zaman GÖZ-orta'yı içerir)."""
    n = len(detay_satirlari)
    gnd_map = {g["id"]: g for g in gnd_satirlari}

    alet = alet_cevaplanan_kumesi(detay_satirlari)
    orta = alet | set(goz_orta_ekle)
    kati = orta | set(goz_kati_ekle)

    sum_a, k_a = kutle(alet, gnd_map, n)
    sum_o, k_o = kutle(orta, gnd_map, n)
    sum_k, k_k = kutle(kati, gnd_map, n)

    return {
        "n": n,
        "ALET": {"n_cevaplanan": len(alet), "toplam": sum_a, "kutle": k_a},
        "GOZ_ORTA": {"n_cevaplanan": len(orta), "toplam": sum_o, "kutle": k_o,
                     "eklenen": sorted(goz_orta_ekle)},
        "GOZ_KATI": {"n_cevaplanan": len(kati), "toplam": sum_k, "kutle": k_k,
                     "eklenen": sorted(set(goz_orta_ekle) | set(goz_kati_ekle))},
    }


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--details", required=True, help="h1_..._detail.jsonl (cevap metni + id)")
    p.add_argument("--gnd", required=True, help="gnd_..._.jsonl (groundedness.py çıktısı)")
    p.add_argument("--goz-orta-ekle", default="", help="GÖZ-orta'nın ALET'e eklediği id'ler, virgüllü")
    p.add_argument("--goz-kati-ekle", default="", help="GÖZ-katı'nın GÖZ-orta'ya eklediği id'ler, virgüllü")
    p.add_argument("--out", default="")
    return p.parse_args()


def main():
    a = parse_args()
    detay = _load_jsonl(a.details)
    gnd = _load_jsonl(a.gnd)
    sonuc = uc_okuma(detay, gnd, _id_set(a.goz_orta_ekle), _id_set(a.goz_kati_ekle))
    print(json.dumps(sonuc, ensure_ascii=False, indent=2))
    if a.out:
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(sonuc, f, ensure_ascii=False, indent=2, sort_keys=True)
        print(f"[uc-okuma] → {a.out}")


if __name__ == "__main__":
    main()
