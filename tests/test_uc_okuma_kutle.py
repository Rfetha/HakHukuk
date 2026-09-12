"""ADIM 6.5 kalibrasyon kapısı — üç okuma türetici, YAYIMLANMIŞ sayılara birebir çivilenir.

`0,6925 · 0,7050 · 0,7425` (3.5 Flash, `gpt-4o-mini` hakem) 2026-09-12'ye kadar hiçbir
betikte yoktu (BULGU-A). Bu test, `uc_okuma_kutle.py`'nin bu üç sayıyı gerçek depo
verisinden (yeniden puanlamadan, sıfır API çağrısıyla) birebir ürettiğini çiviler.
"""
import json
import os

from uc_okuma_kutle import uc_okuma  # noqa: E402

_KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DETAILS = os.path.join(_KOK, "outputs/eval/f04-rakip-onsozsuz/h1_3_5_flash_nb_detail.jsonl")
_GND = os.path.join(_KOK, "outputs/eval/f04-rakip-onsozsuz/gnd_h1_3_5_flash_nb.jsonl")


def _load_jsonl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def test_uc_okuma_gpt4o_mini_kalibrasyon_birebir():
    """GÖZ listesi kesin: id 28 (GÖZ-orta) + id 15,24,27 (GÖZ-katı, orta'nın üstüne)."""
    detay = _load_jsonl(_DETAILS)
    gnd = _load_jsonl(_GND)
    sonuc = uc_okuma(detay, gnd, goz_orta_ekle={28}, goz_kati_ekle={15, 24, 27})

    assert sonuc["n"] == 80
    assert sonuc["ALET"]["n_cevaplanan"] == 67
    assert sonuc["ALET"]["kutle"] == 0.6925
    assert sonuc["GOZ_ORTA"]["n_cevaplanan"] == 68
    assert sonuc["GOZ_ORTA"]["kutle"] == 0.7050
    assert sonuc["GOZ_KATI"]["n_cevaplanan"] == 71
    assert sonuc["GOZ_KATI"]["kutle"] == 0.7425


def test_besinci_kalem_id79_disarida_kalirsa_cipa_yukselmez():
    """Tuzak: dedektör 13 kalemi çekinme sayar, hakem yalnız 8'ini puanlamaz — aradaki 5'in
    4'ü göz listesi, 1'i (id 79, faith 0,5) GÖZ okumasının GERİ ALMADIĞI kalemdir. Yanlışlıkla
    eklenirse çıpa 0,7425 → 0,7488 olur (eşik yükselir) — bu test onu dışarıda tutar."""
    detay = _load_jsonl(_DETAILS)
    gnd = _load_jsonl(_GND)
    gnd_map = {g["id"]: g for g in gnd}
    assert gnd_map[79]["faithfulness"] == 0.5  # kalem puanlı ama göz onu geri ALMIYOR

    dogru = uc_okuma(detay, gnd, goz_orta_ekle={28}, goz_kati_ekle={15, 24, 27})
    yanlis = uc_okuma(detay, gnd, goz_orta_ekle={28}, goz_kati_ekle={15, 24, 27, 79})

    assert dogru["GOZ_KATI"]["kutle"] == 0.7425
    assert yanlis["GOZ_KATI"]["kutle"] > dogru["GOZ_KATI"]["kutle"]


def test_kutle_formulu_toplam_bolu_seksen():
    """Formül `Σ faithfulness(cevap sayılan) / n_toplam` — n_toplam HER ZAMAN 80,
    cevaplanan alt kümesinin büyüklüğü değil."""
    detay = _load_jsonl(_DETAILS)
    gnd = _load_jsonl(_GND)
    sonuc = uc_okuma(detay, gnd)
    assert sonuc["ALET"]["kutle"] == round(sonuc["ALET"]["toplam"] / 80, 4)
