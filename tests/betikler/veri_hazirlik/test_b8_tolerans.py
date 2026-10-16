from b8_tolerans_supurme import mesafe  # noqa: E402


def test_mesafe_ayni_metin_sifir():
    assert mesafe("İŞ KANUNU", "İŞ KANUNU") == 0


def test_mesafe_tek_harf_dusmesi_bir():
    """B8'in gerçek vakası: ESERLERİ → ESELERİ (bir 'R' düşmüş)."""
    assert mesafe("FİKİR VE SANAT ESERLERİ KANUNU",
                  "FİKİR VE SANAT ESELERİ KANUNU") == 1


def test_mesafe_farkli_kanunlar_buyuk():
    """Tolerans BUNLARI birbirine karıştırmamalı — kapının gevşeme riski burada."""
    assert mesafe("TÜRK CEZA KANUNU", "TÜRK MEDENİ KANUNU") > 3


def test_mesafe_simetrik():
    assert mesafe("abc", "abd") == mesafe("abd", "abc")
