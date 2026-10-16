"""vLLM pilotunun kapıları (spec 2026-10-15 bölüm 5): ölçütler pilot sonucunu görmeden kilitlidir."""
import pytest

import vllm_kapilari as vk  # noqa: E402


def _g(n=80, kesik=0, dusunen=80):
    return {"n": n, "kesik_orani": kesik / n if n else None, "dusunen": dusunen}


def _agirlik(sure=150.0, kutle=0.7540, g=None):
    return {"kosular": [{"sure_s": sure, "gecerlilik": g or _g()}, {"sure_s": sure, "gecerlilik": g or _g()}],
            "kutle_ort": kutle, "iki_toplu_kosu_ayni": 80}


def _girdi(**d):
    base = {"q4_acilmis": _agirlik(), "bf16_orijinal": _agirlik(sure=160.0, kutle=0.7700),
            "referans_kutle_ort": 0.7515, "sekiz_soru": {"ayni": 8, "n": 8}}
    base.update(d)
    return base


def test_esikler_spec_ile_ayni():
    assert vk.LLAMA_SURE_S == 640.6 and vk.ESIK_HIZ_ORAN == pytest.approx(1 / 3)
    assert vk.ESIK_KUTLE_PUAN == 0.6 and vk.KESIK_ESIGI == 0.05 and vk.N_KALEM == 80


def test_hepsi_gecerse_ilerle():
    s = vk.degerlendir(_girdi())
    assert s["ilerle"] is True and s["g3"]["fark_puan"] == pytest.approx(0.25)


@pytest.mark.parametrize("sure,gecer", [(213.0, True), (214.0, False)])
def test_hiz_kapisi_llama_cpp_suresinin_ucte_birinde_kesilir(sure, gecer):
    s = vk.degerlendir(_girdi(q4_acilmis=_agirlik(sure=sure)))
    assert s["g2"]["gecti"] is gecer and s["ilerle"] is gecer


def test_motor_etkisi_0_6_puani_asarsa_ilerlemez():
    s = vk.degerlendir(_girdi(q4_acilmis=_agirlik(kutle=0.7580)))      # fark 0,65 puan
    assert s["g3"]["gecti"] is False and s["ilerle"] is False


def test_motor_etkisi_tam_0_6_puanda_gecer():
    assert vk.degerlendir(_girdi(q4_acilmis=_agirlik(kutle=0.7575)))["g3"]["gecti"] is True


def test_kesik_orani_yuzde_besi_asarsa_g1_duser():
    s = vk.degerlendir(_girdi(bf16_orijinal=_agirlik(g=_g(kesik=5))))   # 5/80 = %6,25
    assert s["g1"]["gecti"] is False and s["ilerle"] is False


def test_dusunce_kanali_hic_kullanilmadiysa_g1_duser():
    assert vk.degerlendir(_girdi(q4_acilmis=_agirlik(g=_g(dusunen=0))))["g1"]["gecti"] is False


@pytest.mark.parametrize("ayni,dal", [(8, "bayt"), (7, "puan"), (0, "puan")])
def test_belirlenimcilik_dali_bayt_ya_da_puan_ama_ilerlemeyi_etkilemez(ayni, dal):
    s = vk.degerlendir(_girdi(sekiz_soru={"ayni": ayni, "n": 8}))
    assert s["g4"]["dal"] == dal and s["ilerle"] is True


def test_q4_etkisi_yalniz_raporlanir_kapi_degildir():
    s = vk.degerlendir(_girdi(bf16_orijinal=_agirlik(kutle=0.5000)))
    assert s["g5"]["fark_puan"] == pytest.approx(25.4) and s["ilerle"] is True
