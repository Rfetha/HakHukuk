"""#74 R1 — hakem yanıtındaki fatura satırı okunur; alan yoksa eksik sayılır, sıfır sayılmaz.

Yanıt, SDK'nın kendi kullanım tipiyle kurulur (OpenRouter'ın `cost` alanı tipte yok, ek alan olarak
gelir). Ağ yok, para yok.
"""
from types import SimpleNamespace

import pytest
from openai.types.completion_usage import CompletionUsage

from llm_client import Kullanim, fatura_ozeti, kullanim_oku  # noqa: E402

DS = "deepseek/deepseek-v4.1-flash-20260910"


def _yanit(**usage):
    return SimpleNamespace(usage=CompletionUsage(**usage))


def test_kullanim_oku_maliyeti_onbellegi_ve_dusunceyi_okur():
    k = kullanim_oku(_yanit(prompt_tokens=1000, completion_tokens=50, total_tokens=1050,
                            prompt_tokens_details={"cached_tokens": 800},
                            completion_tokens_details={"reasoning_tokens": 0}, cost=0.00004))
    assert k == Kullanim(girdi=1000, cikti=50, onbellekli_girdi=800, dusunce=0, maliyet_usd=0.00004)


def test_kullanim_oku_alan_yoksa_none_yazar_sifir_yazmaz():
    k = kullanim_oku(_yanit(prompt_tokens=1000, completion_tokens=50, total_tokens=1050))
    assert (k.onbellekli_girdi, k.dusunce, k.maliyet_usd) == (None, None, None)


def test_fatura_ozeti_orani_yalniz_maliyeti_okunan_cagrilardan_hesaplar_ve_eksigi_sayar():
    okunan = Kullanim(girdi=1_000_000, cikti=0, onbellekli_girdi=500_000, dusunce=0, maliyet_usd=0.07)
    eksik = Kullanim(girdi=1_000_000, cikti=0, onbellekli_girdi=None, dusunce=None, maliyet_usd=None)
    o = fatura_ozeti(DS, [okunan, eksik])
    assert o["fatura_orani"] == pytest.approx(0.07 / 0.14)
    assert o["gercek_maliyet_usd"] == pytest.approx(0.07)
    assert o["liste_maliyet_usd"] == pytest.approx(0.28)
    assert o["onbellek_isabeti"] == 0.5
    assert o["eksik"] == {"maliyet": 1, "onbellek": 1, "dusunce": 1}


def test_fatura_ozeti_hic_okunmadiysa_gercek_maliyet_ve_oran_bos():
    o = fatura_ozeti(DS, [Kullanim(girdi=10, cikti=10, onbellekli_girdi=None, dusunce=None,
                                   maliyet_usd=None)])
    assert (o["gercek_maliyet_usd"], o["fatura_orani"], o["onbellek_isabeti"]) == (None, None, None)
