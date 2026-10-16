"""F0.5 (a)(c) — groundedness kalem düşürmez; her kalem bir `durum`la yazılır, özette sayılır.

Önceden beş yerde kalem sessizce düşüyordu (boş girdi · hakem hatası · bütçe · sıfır iddia ·
boş etiket); düşen kalem A1'in paydasından da sessizce çıkıyordu. Hakem çağrısı sahte —
ağ yok, para yok.
"""
import json
import sys

import pytest

import groundedness  # noqa: E402
from llm_client import HakemKimligi  # noqa: E402
from olcum_aleti import GUNCEL  # noqa: E402
from part_dosya import TamamlanmamisDosya  # noqa: E402


def _puan(n_claims=2, sup=2):
    return {"n_claims": n_claims, "sup": sup, "con": 0, "nis": n_claims - sup,
            "nis_unsup": n_claims - sup, "n_cit": 1, "cit_ok": 1, "cit_wrong": 0,
            "source_cited": True, "labels": [], "citations": []}, 0.001


def _detay(tmp_path, n=3):
    p = tmp_path / "h1_x_detail.jsonl"
    p.write_text("".join(json.dumps({"id": i, "soru": f"soru {i}", "referans": f"madde {i}",
                                     "cevap": f"cevap {i}", "kanun_adi": "K"}) + "\n"
                         for i in range(n)), encoding="utf-8")
    return p


def _kos(monkeypatch, tmp_path, davranis, *ek, detay=None):
    monkeypatch.setattr(groundedness, "make_client", lambda: (object(), "openrouter"))
    monkeypatch.setattr(groundedness, "resolve", lambda m, g: m)
    monkeypatch.setattr(groundedness, "score_record",
                        lambda client, model, soru, *a: davranis(soru))
    d = detay or _detay(tmp_path)
    monkeypatch.setattr(sys, "argv", ["groundedness.py", "--details", str(d), "--label", "x",
                                      "--out-dir", str(tmp_path), "--judge-model",
                                      "openai/gpt-4o-mini", *ek])
    return groundedness.main()


def _gnd(tmp_path):
    return {r["id"]: r for r in (json.loads(l) for l in
                                 open(tmp_path / "gnd_x.jsonl", encoding="utf-8") if l.strip())}


def test_groundedness_hakem_hatasi_satir_olarak_yazilir_ve_sayilir(monkeypatch, tmp_path):
    def davranis(soru):
        if soru == "soru 1":
            raise ValueError("JSON ayrıştırılamadı")
        return _puan()
    ozet = _kos(monkeypatch, tmp_path, davranis)
    g = _gnd(tmp_path)
    assert g[1]["durum"] == "hakem_hata" and g[1]["faithfulness"] is None
    assert g[0]["durum"] == "puanli"
    assert ozet["n_hakem_hata"] == 1 and ozet["n_puanli"] == 2


def test_groundedness_sifir_iddia_durumu_ve_sayaci(monkeypatch, tmp_path):
    ozet = _kos(monkeypatch, tmp_path,
                lambda soru: _puan(0, 0) if soru == "soru 2" else _puan())
    assert _gnd(tmp_path)[2]["durum"] == "sifir_iddia"
    assert ozet["n_sifir_iddia"] == 1


def test_groundedness_bos_cevap_satir_olarak_yazilir(monkeypatch, tmp_path):
    d = _detay(tmp_path)
    satirlar = [json.loads(l) for l in d.read_text(encoding="utf-8").splitlines()]
    satirlar[0]["cevap"] = ""
    d.write_text("".join(json.dumps(r) + "\n" for r in satirlar), encoding="utf-8")
    ozet = _kos(monkeypatch, tmp_path, lambda soru: _puan(), detay=d)
    assert _gnd(tmp_path)[0]["durum"] == "bos_girdi"
    assert ozet["n_bos_girdi"] == 1


def test_groundedness_yarida_kesilirse_part_kalir(monkeypatch, tmp_path):
    def davranis(soru):
        if soru == "soru 2":
            raise KeyboardInterrupt
        return _puan()
    with pytest.raises(KeyboardInterrupt):
        _kos(monkeypatch, tmp_path, davranis)
    assert (tmp_path / "gnd_x.jsonl.part").exists()
    assert not (tmp_path / "gnd_x.jsonl").exists()


def test_groundedness_butce_bitince_part_kalir_ve_durur(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENAI_BUDGET_USD", "0.0015")
    with pytest.raises(SystemExit):
        _kos(monkeypatch, tmp_path, lambda soru: _puan())
    assert (tmp_path / "gnd_x.jsonl.part").exists()
    assert not (tmp_path / "gnd_x.jsonl").exists()


def test_groundedness_part_girdiyi_reddeder(monkeypatch, tmp_path):
    d = _detay(tmp_path)
    part = tmp_path / "h1_x_detail.jsonl.part"
    d.rename(part)
    with pytest.raises(TamamlanmamisDosya):
        _kos(monkeypatch, tmp_path, lambda soru: _puan(), detay=part)


def test_score_record_iddia_var_etiket_yoksa_hakem_hatasidir(monkeypatch):
    """İddia çıkarıldı ama doğrulama boş etiket döndü → bu sıfır iddia DEĞİL, hakem arızası."""
    monkeypatch.setattr(groundedness, "extract_claims", lambda *a: (["iddia"], 10, 10))
    monkeypatch.setattr(groundedness, "verify_claims", lambda *a: ({"labels": []}, 10, 10))
    with pytest.raises(ValueError):
        groundedness.score_record(None, HakemKimligi("openai/gpt-4o-mini", None, None),
                                  "s", "k", "g", "c", "data", GUNCEL.altin_kirpma)
