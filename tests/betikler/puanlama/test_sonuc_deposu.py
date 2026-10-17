"""#74 R4 — hakem sonuç deposu: anahtar hakemin gördüğü her şeydir; depo yalnız açıkça istenince
kullanılır. Ağ yok, para yok.
"""
import pytest

import sonuc_deposu  # noqa: E402

KUNYE = {"model": "z-ai/glm-5.3-flash-20260826", "saglayici": "novita/fp8", "dusunme": "kapali"}
GIRDI = dict(hakem_kunye=KUNYE, istemler=("cikar", "dogrula"), mode="data", soru="s",
             kaynak_kirpilmis="madde", gold="K, madde 1", cevap="c")


def test_anahtar_ayni_girdide_ayni():
    assert sonuc_deposu.anahtar(**GIRDI) == sonuc_deposu.anahtar(**GIRDI)


@pytest.mark.parametrize("alan,deger", [
    ("hakem_kunye", {**KUNYE, "dusunme": "acik"}), ("istemler", ("cikar", "dogrula v2")),
    ("mode", "model"), ("soru", "s2"), ("kaynak_kirpilmis", "madde2"), ("gold", "K, madde 2"),
    ("cevap", "c2")])
def test_anahtar_hakemin_gordugu_tek_alan_degisince_degisir(alan, deger):
    assert sonuc_deposu.anahtar(**GIRDI) != sonuc_deposu.anahtar(**{**GIRDI, alan: deger})


def test_depo_ekler_bulur_ve_yeniden_acilinca_okur(tmp_path):
    d = sonuc_deposu.SonucDeposu(tmp_path, KUNYE)
    assert d.bul("a") is None
    d.ekle("a", {"n_claims": 1}, "kosu1")
    assert sonuc_deposu.SonucDeposu(tmp_path, KUNYE).bul("a") == {"n_claims": 1}


def test_depo_hakem_kimligi_basina_ayri_dosyadir(tmp_path):
    sonuc_deposu.SonucDeposu(tmp_path, KUNYE).ekle("a", {"n_claims": 1}, "kosu1")
    assert sonuc_deposu.SonucDeposu(tmp_path, {**KUNYE, "dusunme": "acik"}).bul("a") is None
