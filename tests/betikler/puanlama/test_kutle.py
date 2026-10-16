"""F0.5 (a)(c) — kütle tek yerden, dondurulmuş kümeye karşı (ADR-0098 m.1).

Çıpalar depodaki gerçek koşulardan, sıfır API çağrısıyla:
  f02-biz-onsozsuz   0,8011  (%80,1 — sıfır iddialı cevaplanmış kalem YOK, iki kural aynı)
  olcum-bi           0,6838 ↔ 0,6734  (%68,4 — id 31 sıfır iddialı; tuzak 2.22, #72)
"""
import hashlib
import json
import os

import pytest

from kutle import DondurulmusKume, OlcumKapisiHatasi, kutle_hesapla  # noqa: E402
from dataclasses import replace  # noqa: E402

from olcum_aleti import GUNCEL, A1Tanimi, Dedektor, SifirIddia  # noqa: E402

_KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
_DEV = os.path.join(_KOK, "data/eval/dev/core_hard.jsonl")
_DEV_V1 = os.path.join(_KOK, "data/eval/dev/core_hard.jsonl.v1-2026-09-06")
_F02 = os.path.join(_KOK, "outputs/eval/faz0/f02-biz-onsozsuz")
_BI = os.path.join(_KOK, "outputs/eval/sprint2-olcum/olcum-bi")

_ESKI_KURAL = replace(GUNCEL, sifir_iddia=SifirIddia.ORTALAMADAN_CIKAR)
_SPR2 = os.path.join(_KOK, "outputs/eval/sprint2-olcum")


def _jsonl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def _f02():
    return (_jsonl(os.path.join(_F02, "h1_tgta_v1_f02_nb_detail.jsonl")),
            _jsonl(os.path.join(_F02, "gnd_h1_tgta_v1_f02_nb.jsonl")))


def _bi():
    return (_jsonl(os.path.join(_BI, "h1_tgta_v1_bi_k10_detail.jsonl")),
            _jsonl(os.path.join(_BI, "gnd_h1_tgta_v1_bi_k10.jsonl")))


# ── dondurulmuş küme ──────────────────────────────────────────────────────────

def test_kume_yukle_boyutu_ve_ozeti_dosyadan_gelir():
    kume = DondurulmusKume.yukle(_DEV)
    assert kume.boyut == 80
    assert kume.sha256 == hashlib.sha256(open(_DEV, "rb").read()).hexdigest()


# ── (c) tamlık kapısı ─────────────────────────────────────────────────────────

def test_tamlik_tam_dosyada_f02_kutlesi_birebir():
    detay, gnd = _f02()
    s = kutle_hesapla(detay, gnd, DondurulmusKume.yukle(_DEV), GUNCEL)
    assert s.n == 80
    assert s.kutle == 0.8011


def test_tamlik_eksik_satirda_durur():
    detay, gnd = _f02()
    with pytest.raises(OlcumKapisiHatasi, match="satır"):
        kutle_hesapla(detay[:-1], gnd, DondurulmusKume.yukle(_DEV), GUNCEL)


def test_tamlik_yinelenen_idde_durur():
    detay, gnd = _f02()
    detay[5] = dict(detay[5], id=detay[4]["id"])
    with pytest.raises(OlcumKapisiHatasi, match="id"):
        kutle_hesapla(detay, gnd, DondurulmusKume.yukle(_DEV), GUNCEL)


def test_tamlik_baska_kumenin_sorularinda_durur():
    """olcum-bi v1 soru setiyle üretildi; v2 kümesine karşı puanlanamaz (boyut aynı: 80)."""
    detay, gnd = _bi()
    with pytest.raises(OlcumKapisiHatasi, match="soru"):
        kutle_hesapla(detay, gnd, DondurulmusKume.yukle(_DEV), GUNCEL)


# ── (a) payda kapısı + sıfır iddia kuralı ─────────────────────────────────────

def test_sifir_iddia_sifir_puan_olcum_bi():
    """Kullanıcı kararı 2026-10-11: cevap sayılıp hiç iddia çıkarılamayan kalem 0 puan."""
    detay, gnd = _bi()
    s = kutle_hesapla(detay, gnd, DondurulmusKume.yukle(_DEV_V1), GUNCEL)
    assert (s.n_cevaplanan, s.n_puanli_cevaplanan, s.n_sifir_iddia) == (66, 65, 1)
    assert s.kutle == 0.6734
    assert s.kutle == round(s.kapsama * s.A1, 4)


def test_sifir_iddia_eski_kural_kayittaki_0_6838i_verir():
    """2026-10-11 öncesi harness_tablo: kalem A1 ortalamasından çıkarılıyordu (#61'in %68,4'ü)."""
    detay, gnd = _bi()
    s = kutle_hesapla(detay, gnd, DondurulmusKume.yukle(_DEV_V1), _ESKI_KURAL)
    assert s.kutle == 0.6838
    assert s.kapsama == 0.825


def test_payda_cevaplanan_kalemin_hakem_satiri_yoksa_durur():
    detay, gnd = _f02()
    gnd = [g for g in gnd if g["id"] != 0]          # id 0 cevaplanmış bir kalem
    with pytest.raises(OlcumKapisiHatasi, match="hakem"):
        kutle_hesapla(detay, gnd, DondurulmusKume.yukle(_DEV), GUNCEL)


def test_payda_hakem_hata_durumlu_satir_durdurur():
    detay, gnd = _f02()
    gnd = [dict(g, durum="hakem_hata", faithfulness=None, n_claims=0) if g["id"] == 0 else g
           for g in gnd]
    with pytest.raises(OlcumKapisiHatasi, match="hakem"):
        kutle_hesapla(detay, gnd, DondurulmusKume.yukle(_DEV), GUNCEL)


def test_payda_cekinmenin_hakem_satiri_eksikse_kutle_degismez():
    """Çekinilen kalem kütleye girmez; onun hakem satırının yokluğu hesabı durdurmaz."""
    detay, gnd = _f02()
    tam = kutle_hesapla(detay, gnd, DondurulmusKume.yukle(_DEV), GUNCEL)
    cekinilen = [r["id"] for r in detay if not GUNCEL.cevap_mi(r["cevap"])]
    assert cekinilen
    eksik = [g for g in gnd if g["id"] != cekinilen[0]]
    assert kutle_hesapla(detay, eksik, DondurulmusKume.yukle(_DEV), GUNCEL).kutle == tam.kutle


# ── alt küme ve göz okuması ──────────────────────────────────────────────────

def test_alt_kume_payi_alt_kumenin_boyutu():
    detay, gnd = _f02()
    s = kutle_hesapla(detay, gnd, DondurulmusKume.yukle(_DEV), GUNCEL)
    ilk40 = s.alt_kume(range(40))
    assert ilk40.n == 40
    assert ilk40.n_cevaplanan == sum(1 for r in detay if r["id"] < 40 and GUNCEL.cevap_mi(r["cevap"]))


def test_goz_ekle_kalemi_cevap_kumesine_katar():
    detay, gnd = _f02()
    kume = DondurulmusKume.yukle(_DEV)
    cekinilen = next(r["id"] for r in detay if not GUNCEL.cevap_mi(r["cevap"]))
    alet = kutle_hesapla(detay, gnd, kume, GUNCEL)
    goz = kutle_hesapla(detay, gnd, kume, GUNCEL, goz_ekle={cekinilen})
    assert goz.n_cevaplanan == alet.n_cevaplanan + 1


# ── RQ2 anahtarları (F0.5 b): hakemi çağırmayanlar, saklı hakem çıktılarından, BİREBİR ────

def _kos(kosu, etiket):
    d = os.path.join(_SPR2, kosu)
    return (_jsonl(os.path.join(d, f"{etiket}_detail.jsonl")),
            _jsonl(os.path.join(d, f"gnd_{etiket}.jsonl")))


@pytest.mark.parametrize("kosu,etiket,eski,yeni", [
    ("olcum-bi", "h1_tgta_v1_bi_k10", 0.6275, 0.6838),                   # #61: %62,8 → %68,4
    ("s2-harness-k10-etiketli", "h1_tgta_v1_h1_k10_et", 0.6132, 0.7299),  # #61: %61,3 → %73,0
])
def test_rq2_dedektor_anahtari_61_cipasi_birebir(kosu, etiket, eski, yeni):
    detay, gnd = _kos(kosu, etiket)
    kume = DondurulmusKume.yukle(_DEV_V1)
    alet_eski = replace(_ESKI_KURAL, dedektor=Dedektor.ADR0061_ONCESI)
    assert kutle_hesapla(detay, gnd, kume, alet_eski).kutle == eski
    assert kutle_hesapla(detay, gnd, kume, _ESKI_KURAL).kutle == yeni


@pytest.mark.parametrize("kosu,etiket,ham,cevaplanan", [
    ("s3-harness-acik", "h1_tgta_v1_h1", 0.5867, 0.5693),      # #54 k=5:  %58,7 → %56,9
    ("s3-harness-k10", "h1_tgta_v1_h1_k10", 0.5844, 0.5953),   # #54 k=10: %58,4 → %59,5
])
def test_rq2_a1_tanimi_anahtari_54_cipasi_birebir(kosu, etiket, ham, cevaplanan):
    """#54'ün o günkü dedektörü bu koşularda ADR-0061 öncesiyle aynı sonucu verir (2026-10-11)."""
    detay, gnd = _kos(kosu, etiket)
    kume = DondurulmusKume.yukle(_DEV_V1)
    o_gun = replace(_ESKI_KURAL, dedektor=Dedektor.ADR0061_ONCESI)
    assert kutle_hesapla(detay, gnd, kume, replace(o_gun, a1_tanimi=A1Tanimi.HAM_MAKRO)).kutle == ham
    assert kutle_hesapla(detay, gnd, kume, o_gun).kutle == cevaplanan


def test_olcum_aleti_kunyesi_butun_anahtarlari_tasir():
    assert set(GUNCEL.kunye()) >= {"dedektor", "sifir_iddia", "a1_tanimi"}
