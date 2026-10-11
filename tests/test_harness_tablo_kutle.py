"""harness_tablo.py'nin kütle ekseni `kutle.py`'den gelir (F0.5 a·c, tuzak 2.22).

Uçtan uca: gerçek koşu dosyaları, sıfır API çağrısı. Kütle dışındaki alanlar
(`erisim`, `kapi`, `atif_dagilimi` …) bu değişiklikten etkilenmez.
"""
import json
import os
import sys

import pytest

import harness_tablo  # noqa: E402
from kutle import DondurulmusKume, OlcumKapisiHatasi  # noqa: E402
from olcum_aleti import GUNCEL  # noqa: E402
from uc_okuma_kutle import uc_okuma  # noqa: E402

_KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEV = os.path.join(_KOK, "data/eval/dev/core_hard.jsonl")
_DEV_V1 = os.path.join(_KOK, "data/eval/dev/core_hard.jsonl.v1-2026-09-06")
_BI = os.path.join(_KOK, "outputs/eval/sprint2-olcum/olcum-bi")
_BI_DET = os.path.join(_BI, "h1_tgta_v1_bi_k10_detail.jsonl")
_BI_GND = os.path.join(_BI, "gnd_h1_tgta_v1_bi_k10.jsonl")


def _kos(monkeypatch, tmp_path, *arg):
    out = tmp_path / "tablo.json"
    monkeypatch.setattr(sys, "argv", ["harness_tablo.py", *arg, "--out", str(out)])
    harness_tablo.main()
    return json.loads(out.read_text(encoding="utf-8"))


def test_harness_tablo_kume_verilmezse_calismaz(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "argv", ["harness_tablo.py", "--details", _BI_DET, "--gnd", _BI_GND])
    with pytest.raises(SystemExit):
        harness_tablo.main()


def test_harness_tablo_ve_uc_okuma_ayni_kutleyi_verir(monkeypatch, tmp_path):
    """Tuzak 2.22: iki yol olcum-bi'de 0,6838 ↔ 0,6734 ayrışıyordu; artık aynı kaynaktan."""
    t = _kos(monkeypatch, tmp_path, "--details", _BI_DET, "--gnd", _BI_GND, "--kume", _DEV_V1)
    jl = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    u = uc_okuma(jl(_BI_DET), jl(_BI_GND), DondurulmusKume.yukle(_DEV_V1))
    assert t["kutle_ekseni"]["kutle_tum"] == u["ALET"]["kutle"] == 0.6734
    assert t["kutle_ekseni"]["n_sifir_iddia"] == 1
    assert t["olcum_aleti"] == GUNCEL.kunye()
    assert t["kume"]["boyut"] == 80


def test_harness_tablo_eski_kural_kayittaki_tabloyu_birebir_verir(monkeypatch, tmp_path):
    """Eski sıfır-iddia kuralıyla depodaki harness_tablo.json'un kütle ekseni aynen çıkar."""
    t = _kos(monkeypatch, tmp_path, "--details", _BI_DET, "--gnd", _BI_GND, "--kume", _DEV_V1,
             "--sifir-iddia", "ortalamadan-cikar")
    kayit = json.load(open(os.path.join(_BI, "harness_tablo.json"), encoding="utf-8"))
    for alan in ("coverage", "A1_cevaplanan", "A1_tum", "A1_altin_getirilen_alt_kume",
                 "faith_macro_tum_cekinme_dahil", "kutle_tum"):
        assert t["kutle_ekseni"][alan] == kayit["kutle_ekseni"][alan], alan
    for alan in ("erisim", "kapi", "atif_dagilimi", "erisim_davranis_caprazi", "k2_bedeli"):
        assert t[alan] == kayit[alan], alan


def test_harness_tablo_yanlis_kumede_durur(monkeypatch, tmp_path):
    with pytest.raises(OlcumKapisiHatasi):
        _kos(monkeypatch, tmp_path, "--details", _BI_DET, "--gnd", _BI_GND, "--kume", _DEV)


def test_harness_tablo_part_dosyasini_okumaz(monkeypatch, tmp_path):
    from part_dosya import TamamlanmamisDosya
    part = tmp_path / "x_detail.jsonl.part"
    part.write_text(open(_BI_DET, encoding="utf-8").read(), encoding="utf-8")
    with pytest.raises(TamamlanmamisDosya):
        _kos(monkeypatch, tmp_path, "--details", str(part), "--gnd", _BI_GND, "--kume", _DEV_V1)


def test_harness_tablo_eski_kural_cift_yuvarlamayi_korur(monkeypatch, tmp_path):
    """Eski tablo kapsama ve A1'i önce 4 haneye yuvarlayıp çarpıyordu; s3-harness-k10'da bu
    0,6914 verir (tek yuvarlama 0,6913). Eski alet kayıttaki sayıyı birebir üretmeli."""
    d = os.path.join(_KOK, "outputs/eval/sprint2-olcum/s3-harness-k10")
    t = _kos(monkeypatch, tmp_path, "--details", os.path.join(d, "h1_tgta_v1_h1_k10_detail.jsonl"),
             "--gnd", os.path.join(d, "gnd_h1_tgta_v1_h1_k10.jsonl"), "--kume", _DEV_V1,
             "--sifir-iddia", "ortalamadan-cikar",
             "--etiketler", os.path.join(_KOK, "outputs/eval/sprint2-olcum/s3-ayirt-edicilik/etiketler.jsonl"))
    kayit = json.load(open(os.path.join(d, "harness_tablo.json"), encoding="utf-8"))
    assert t["kutle_ekseni"]["kutle_tum"] == kayit["kutle_ekseni"]["kutle_tum"] == 0.6914
    assert t["ayirt_edicilik_alt_kumeleri"] == kayit["ayirt_edicilik_alt_kumeleri"]
