"""F0.6 kodu — hakem kimliği tek nesnede: model · sabit sağlayıcı · hakemin düşünme modu.

RQ2'nin "hakem" anahtarı ile DeepSeek geçişi aynı nesnedir (ADR-0099 m.1). Ağ yok, para yok.
"""
import json
import sys

import pytest

import groundedness  # noqa: E402
from llm_client import Dusunme, HakemKimligi  # noqa: E402

DS = "deepseek/deepseek-v4.1-flash-20260910"


def test_dusunme_ailesinde_mod_verilmezse_kurulmaz():
    with pytest.raises(ValueError, match="düşünme"):
        HakemKimligi(DS, saglayici="DeepSeek", dusunme=None)


def test_sabit_saglayici_zorunlu_ailede_saglayici_verilmezse_kurulmaz():
    with pytest.raises(ValueError, match="sağlayıcı"):
        HakemKimligi(DS, saglayici=None, dusunme=Dusunme.KAPALI)


def test_dusunme_modu_olmayan_ailede_mod_verilirse_kurulmaz():
    with pytest.raises(ValueError, match="düşünme"):
        HakemKimligi("openai/gpt-4o-mini", saglayici="OpenAI", dusunme=Dusunme.ACIK)


@pytest.mark.parametrize("mod,beklenen", [(Dusunme.ACIK, True), (Dusunme.KAPALI, False)])
def test_istek_ekleri_saglayiciyi_sabitler_ve_dusunmeyi_tasir(mod, beklenen):
    ek = HakemKimligi(DS, saglayici="DeepSeek", dusunme=mod).istek_ekleri()
    assert ek["extra_body"]["provider"] == {"order": ["DeepSeek"], "allow_fallbacks": False}
    assert ek["extra_body"]["reasoning"] == {"enabled": beklenen}


def test_eski_hakem_ortam_degiskeninden_saglayiciyla_calisir(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER_ORDER", "OpenAI")
    ek = HakemKimligi("openai/gpt-4o-mini", saglayici=None, dusunme=None).istek_ekleri()
    assert ek["extra_body"]["provider"]["order"] == ["OpenAI"]
    assert "reasoning" not in ek["extra_body"]


def test_kunye_tarihli_kimligi_ve_saglayiciyi_tasir():
    k = HakemKimligi(DS, saglayici="DeepSeek", dusunme=Dusunme.KAPALI).kunye()
    assert k == {"model": DS, "saglayici": "DeepSeek", "dusunme": "kapali"}


def _detay(tmp_path):
    p = tmp_path / "h1_x_detail.jsonl"
    p.write_text(json.dumps({"id": 0, "soru": "s", "referans": "m", "cevap": "c"}) + "\n",
                 encoding="utf-8")
    return p


def test_groundedness_fiyati_kayitsiz_hakemi_para_harcamadan_reddeder(monkeypatch, tmp_path):
    cagri = []
    monkeypatch.setattr(groundedness, "make_client", lambda: (object(), "openrouter"))
    monkeypatch.setattr(groundedness, "score_record", lambda *a: cagri.append(a))
    monkeypatch.setattr(sys, "argv", ["groundedness.py", "--details", str(_detay(tmp_path)),
                                      "--label", "x", "--out-dir", str(tmp_path),
                                      "--judge-model", "deepseek/fiyati-kayitsiz-20990101",
                                      "--hakem-saglayici", "DeepSeek", "--hakem-dusunme", "kapali"])
    with pytest.raises(SystemExit):
        groundedness.main()
    assert cagri == []


def test_groundedness_ozeti_hakem_kunyesini_tasir(monkeypatch, tmp_path):
    monkeypatch.setattr(groundedness, "make_client", lambda: (object(), "openrouter"))
    monkeypatch.setattr(groundedness, "score_record", lambda *a: ({
        "n_claims": 1, "sup": 1, "con": 0, "nis": 0, "nis_unsup": 0, "n_cit": 0, "cit_ok": 0,
        "cit_wrong": 0, "source_cited": False, "labels": [], "citations": []}, []))
    monkeypatch.setattr(sys, "argv", ["groundedness.py", "--details", str(_detay(tmp_path)),
                                      "--label", "x", "--out-dir", str(tmp_path),
                                      "--judge-model", "openai/gpt-4o-mini",
                                      "--hakem-saglayici", "OpenAI"])
    ozet = groundedness.main()
    assert ozet["hakem"] == {"model": "openai/gpt-4o-mini", "saglayici": "OpenAI", "dusunme": None}


def test_deepseek_kisa_ad_tarihli_kimlige_cozulur_ve_saglayici_fiyati_kayitli():
    """F0.14 (2026-10-15): tarihli kimlik + sabit sağlayıcının (DeepInfra, fp8) fiyatı #81'de kaynaklı."""
    from llm_client import family, price, resolve
    assert resolve("deepseek-v4.1-flash", "openrouter") == DS
    assert family("deepseek-v4.1-flash") == "deepseek"
    assert price(DS) == (0.14 / 1e6, 0.42 / 1e6)


GLM = "z-ai/glm-5.3-flash-20260826"


def test_glm_kisa_ad_tarihli_kimlige_cozulur_ve_saglayici_fiyati_kayitli():
    """#74 R7b (2026-10-17): ikinci hakem GLM, sabit sağlayıcı Novita (fp8), fiyat indirim düşülmüş."""
    from llm_client import family, price, resolve
    assert resolve("glm-5.3-flash", "openrouter") == GLM
    assert family("glm-5.3-flash") == "z-ai"
    assert price(GLM) == (0.084 / 1e6, 0.28 / 1e6)


@pytest.mark.parametrize("saglayici,dusunme,hata", [("novita/fp8", None, "düşünme"),
                                                     (None, Dusunme.DUSUK, "sağlayıcı")])
def test_glm_dusunme_modu_ve_sabit_saglayici_zorunlu(saglayici, dusunme, hata):
    with pytest.raises(ValueError, match=hata):
        HakemKimligi(GLM, saglayici=saglayici, dusunme=dusunme)


def test_glm_dusunme_kapatilamaz_kimlik_kurulmaz():
    """#74: GLM-5.3-Flash'ta düşünme zorunlu; `kapali` 400 döndürürdü — paradan önce reddedilir."""
    with pytest.raises(ValueError, match="kapatılamaz"):
        HakemKimligi(GLM, saglayici="novita/fp8", dusunme=Dusunme.KAPALI)


def test_glm_dusuk_modda_istek_ekleri_saglayiciyi_sabitler_ve_dusunme_duzeyini_low_verir():
    ek = HakemKimligi(GLM, saglayici="novita/fp8", dusunme=Dusunme.DUSUK).istek_ekleri()
    assert ek["extra_body"] == {"provider": {"order": ["novita/fp8"], "allow_fallbacks": False},
                                "reasoning": {"effort": "low"}}
