"""Makine geçiş kapısının puan düzeyi dalı (vLLM hattı, G4 'puan' dalı): bayt eşitliği aranmaz, kütle farkı bakılır."""
import pytest

import makine_kapisi_puan as mp  # noqa: E402


def test_fark_esigin_icindeyse_gecer():
    s = mp.puan_kapisi(0.7515, 0.7540)
    assert s["gecti"] is True and s["fark_puan"] == pytest.approx(0.25)


def test_fark_esigi_asarsa_duser():
    assert mp.puan_kapisi(0.7515, 0.7600)["gecti"] is False        # 0,85 puan


def test_tam_esikte_gecer():
    assert mp.puan_kapisi(0.7500, 0.7560)["gecti"] is True          # 0,6 puan


def test_cikis_kodu_kapiyi_yansitir():
    assert mp.main(["--referans-kutle", "0.7515", "--aday-kutle", "0.7540"]) == 0
    assert mp.main(["--referans-kutle", "0.7515", "--aday-kutle", "0.7700"]) == 1
