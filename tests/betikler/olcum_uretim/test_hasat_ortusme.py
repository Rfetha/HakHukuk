"""Hasat kapısı (spec bölüm 6; kullanıcı kararı 2026-10-16): Q4_K_M'in yanlış yaptığı kalemlerin ne kadarı vLLM (Q4 ağırlığı) da yanlış?"""
import pytest

import hasat_ortusme as ho  # noqa: E402


def _tekrar(puanlar):
    return [{"id": i, "faithfulness": p} for i, p in enumerate(puanlar)]


def test_yanlis_kalem_tekrar_ortalamasi_esigin_altinda_olandir():
    t = [_tekrar([1.0, 0.0, 0.4]), _tekrar([1.0, 0.2, 0.8])]       # ortalamalar: 1,0 · 0,1 · 0,6
    assert ho.yanlis_kalemler(t, esik=0.5) == {1}


def test_puansiz_kalem_yanlis_sayilmaz():
    t = [_tekrar([None, 0.0]), _tekrar([None, 0.0])]
    assert ho.yanlis_kalemler(t) == {1}


def test_ortusme_orani_ortak_bolu_q4_yanlis():
    s = ho.ortusme({1, 2, 3, 4}, {3, 4, 5})
    assert s == {"q4_yanlis": 4, "vllm_yanlis": 3, "ortak": 2, "oran": pytest.approx(0.5)}


def test_q4_hic_yanlis_yapmadiysa_oran_tanimsiz():
    assert ho.ortusme(set(), {1})["oran"] is None
