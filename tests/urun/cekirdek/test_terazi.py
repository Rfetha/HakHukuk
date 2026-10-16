"""suskunluk_terazisi ürün yüzeyinin kapı testleri (plan Görev 7).

Vakalar UYDURULMADI — hepsi Faz 0'da gözle okunmuş gerçek kalemler.
"""
from hakhukuk.cekirdek.terazi import siniflandir
from hakhukuk.cekirdek.tipler import Durum, Kaynak

IS_K_31 = Kaynak(kanun_adi="İŞ KANUNU", kanun_no="4857", madde_no="Madde 31",
                 metin="Muvazzaf askerlik ödevi dışında manevra veya herhangi bir "
                       "sebeple silâh altına alınan …", sira=1)


def test_olumsuz_hukum_kaynak_VARKEN_cevaptir_cekinme_degildir():
    """2026-09-07 · GERÇEK vaka (BİZ id=37): alet bunu çekinme saydı, göz CEVAP dedi.

    "…zorunlu bir şart bulunmamaktadır" bir HUKUKİ HÜKÜMDÜR, red değil.
    """
    metin = ("Vesayet altındaki bir kişi için aile meclisinin kurulmasının zorunlu bir "
             "şartı bulunmamaktadır. Vesayet, mahkeme kararıyla atanır. "
             "**İlgili Kanun:** Türk Medeni Kanunu, 503. madde.")
    durum, atiflar = siniflandir(metin, kaynaklar=(IS_K_31,), finish_reason="stop")
    assert durum is not Durum.SUSKUNLUK


def test_kaynak_YOKKEN_ayni_metin_suskunluk_sayilabilir():
    """Aynı metin, kaynak yokken: "kaynakta yok" okuması artık MÜMKÜN."""
    metin = "Bu konuda elimdeki kaynaklarda bir hüküm bulunmamaktadır."
    durum, _ = siniflandir(metin, kaynaklar=(), finish_reason="stop")
    assert durum is Durum.SUSKUNLUK


def test_kesik_cevap_gizlenmez():
    """Faz 0 · id 43: yarım cümle sessizce teslim edilmez."""
    durum, _ = siniflandir("İddianame, Cumhuriyet Başsavcılığı tarafından mahkemeye "
                           "sunulur ve mahkeme tarafından kabul edilirse",
                           kaynaklar=(IS_K_31,), finish_reason="length")
    assert durum is Durum.KESIK


def test_uydurulmus_atif_dogrulanmadi_isaretlenir():
    """Faz 0 · base id=16: "4711 Sayılı Türk Hakemlik Kanunu" — var olmayan kanun."""
    metin = "Karşı oy yer almaz. 4711 Sayılı Türk Hakemlik Kanunu'nun 33. maddesi."
    _, atiflar = siniflandir(metin, kaynaklar=(IS_K_31,), finish_reason="stop")
    assert atiflar, "atıf çıkarılamadı"
    assert all(not a.dogrulandi for a in atiflar), "getirilen kaynakta olmayan atıf doğrulanmış"


def test_kaynaktaki_atif_dogrulanir():
    metin = "İş Kanunu Madde 31 uyarınca sözleşme askıya alınır."
    _, atiflar = siniflandir(metin, kaynaklar=(IS_K_31,), finish_reason="stop")
    assert any(a.dogrulandi for a in atiflar)


# ── Atıf doğrulamanın kimlik normalizasyonu (subagent ölçümü, 2026-09-07) ──────
# Korpusta madde_no yazımı TEK TİP DEĞİL: 23.766 "Madde" · 8.922 "MADDE" · 7.808 diğer.
# Düz metin karşılaştırması bu yüzden DOĞRU atıfları "doğrulanamadı" damgalıyordu —
# kullanıcıya haksız uyarı gider ve cevap haksız yere ÇEKİNCELİ'ye düşer.

TKHK_11 = Kaynak(kanun_adi="TÜKETİCİNİN KORUNMASI HAKKINDA KANUN", kanun_no="6502",
                 madde_no="MADDE 11", metin="Ayıplı mal…", sira=1)          # BÜYÜK yazım
KMK_30 = Kaynak(kanun_adi="KAT MÜLKİYETİ KANUNU", kanun_no="634",
                madde_no="Madde 30", metin="Kat malikleri kurulu…", sira=2)  # küçük yazım


def test_BUYUK_yazimli_kaynaga_yapilan_dogru_atif_dogrulanir():
    """Ölçüldü: korpusun %22'si 'MADDE' yazımlı; o kayıtlara atıf hiç doğrulanmıyordu."""
    metin = "6502 sayılı Kanunun 11. maddesi uyarınca seçimlik haklarınız vardır."
    _, atiflar = siniflandir(metin, kaynaklar=(TKHK_11,), finish_reason="stop")
    assert any(a.dogrulandi for a in atiflar), "BÜYÜK yazımlı kaynaktaki doğru atıf kaçtı"


def test_gecici_madde_normal_maddeyle_KARISTIRILMAZ():
    """'Geçici Madde 1' ile 'Madde 1' aynı sayılırsa doğrulama SESSİZCE şişer."""
    gecici = Kaynak(kanun_adi="X KANUNU", kanun_no="1234", madde_no="Geçici Madde 1",
                    metin="…", sira=1)
    _, atiflar = siniflandir("1234 sayılı Kanun Madde 1 uyarınca…",
                             kaynaklar=(gecici,), finish_reason="stop")
    assert not any(a.dogrulandi for a in atiflar)


def test_cok_kanunlu_baglamda_TEK_eslesme_dogrulanir():
    """k=10 hibrit retriever neredeyse hep birden çok kanun getiriyor; kanun numarası
    anılmasa bile madde no kaynaklarda TEK eşleşiyorsa atıf bağlanabilir."""
    _, atiflar = siniflandir("Kat malikleri kurulu Madde 30'a göre karar alır.",
                             kaynaklar=(TKHK_11, KMK_30), finish_reason="stop")
    assert any(a.dogrulandi and a.kanun_no == "634" for a in atiflar)


def test_cok_kanunlu_baglamda_BELIRSIZ_eslesme_dogrulanmaz():
    """Aynı madde numarası iki kaynakta varsa hangisi olduğu bilinmez — TAHMİN EDİLMEZ."""
    a = Kaynak(kanun_adi="A", kanun_no="111", madde_no="Madde 5", metin="…", sira=1)
    b = Kaynak(kanun_adi="B", kanun_no="222", madde_no="MADDE 5", metin="…", sira=2)
    _, atiflar = siniflandir("Madde 5 uyarınca…", kaynaklar=(a, b), finish_reason="stop")
    assert not any(x.dogrulandi for x in atiflar)
