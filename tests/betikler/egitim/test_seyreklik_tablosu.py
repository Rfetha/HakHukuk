"""F0.7 — seyreklik tablosu: kol başına kırpma ve işaret seçiminden sağ kalan kütle (CPU, $0).

Hesap `merge_ties.ties()` ile aynı adımları izler ve her tensörde onun birleşmiş çıktısıyla
bit düzeyinde aynı sonucu vermek zorundadır (aksi hâlde tablo yayımlanan birleştirmeyi tarif etmez).
"""
import pytest
import torch

from merge_ties import ties  # noqa: E402
from seyreklik_tablosu import tensor_istatistigi  # noqa: E402

torch.manual_seed(3407)


def test_ayni_iki_kolda_isaret_secimi_kutle_kaybettirmez():
    t = torch.randn(64, 32)
    s = tensor_istatistigi({"g": t, "a": t.clone()}, trim_k=0.2)
    assert s["a"]["kirpma_sonrasi"] == pytest.approx(s["a"]["isaret_sonrasi"])
    assert 0.2 < s["a"]["kirpma_sonrasi"] < 1.0


def test_zit_iki_kolda_isaret_secimi_her_seyi_siler():
    t = torch.randn(64, 32)
    s = tensor_istatistigi({"g": t, "a": -t}, trim_k=0.2)
    assert s["g"]["isaret_sonrasi"] == 0.0 and s["a"]["isaret_sonrasi"] == 0.0


def test_buyuk_kol_kucuk_kolu_isaret_seciminde_ezer():
    g = torch.randn(64, 32) * 10
    a = torch.randn(64, 32)
    s = tensor_istatistigi({"g": g, "a": a}, trim_k=0.2)
    assert s["a"]["isaret_sonrasi"] < s["g"]["isaret_sonrasi"]
    assert s["g"]["kare_norm"] > s["a"]["kare_norm"]


def test_hesap_ties_ile_bit_duzeyinde_ayni():
    g, a = torch.randn(48, 40) * 3, torch.randn(48, 40)
    s = tensor_istatistigi({"g": g, "a": a}, trim_k=0.2)
    beklenen, _ = ties(torch.stack([g, a]), 0.2)
    assert torch.equal(s["_birlesik"], beklenen)
