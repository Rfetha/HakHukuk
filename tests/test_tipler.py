"""Ürün tiplerinin kapı testleri (plan Görev 6)."""
import pytest

from hakhukuk.cekirdek.tipler import Atif, Cevap, Durum, Kaynak


def test_durum_alti_hali_var():
    """⚠️ Dört hâl BEŞE çıktı (2026-09-09, Görev 18 · ADR-0076): araç döngüsü sınıra
    dayanabilir ve bu, dört hâlin hiçbiriyle aynı şey değildir. Davranış değişti, test de
    değişti — sessizce değil, gerekçesiyle.

    ⚠️ BEŞ hâl ALTIYA çıktı (2026-09-11, ADR-0081, insan kararı): boş sorgu `SUSKUNLUK`
    dönüyordu ve rozet ile gövde FARKLI şey söylüyordu. Testin ADI da güncellendi —
    "bes" diyen bir ad altı değerli kümeyi yanlış anlatır.

    ⛔ `ARAMA_TUKENDI` `KESIK`'e katlanmaz: `KESIK` *"cümle yarım"*, `ARAMA_TUKENDI`
    *"cümle tam, dayanağı eksik olabilir"* demektir.
    ⛔ `BOS_SORGU` `SUSKUNLUK`'a katlanmaz: `SUSKUNLUK` *"aradım, karşılık yok"*,
    `BOS_SORGU` *"soru yazılmadı, ARAMA YAPILMADI"* demektir.
    """
    assert {d.name for d in Durum} == {"CEVAP", "CEKINCELI", "SUSKUNLUK", "KESIK",
                                       "ARAMA_TUKENDI", "BOS_SORGU"}


def test_cevap_donmus_ve_degistirilemez():
    c = Cevap(metin="x", durum=Durum.CEVAP, atiflar=(), kaynaklar=())
    with pytest.raises(Exception):
        c.metin = "y"


def test_kaynak_kimligi_kanun_madde_ciftidir():
    k = Kaynak(kanun_adi="İŞ KANUNU", kanun_no="4857", madde_no="Madde 31",
               metin="…", sira=1)
    assert k.kimlik == "4857/Madde 31"


def test_atif_dogrulanmamis_olarak_baslar():
    a = Atif(kanun_no="4857", madde_no="Madde 31")
    assert a.dogrulandi is False
