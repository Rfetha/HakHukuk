from atif_dogrula import Dogrulayici, atiflari_ayikla, dogrula  # noqa: E402
from red_kapisi import KATI, COGUNLUK, CERRAHI, kapi  # noqa: E402

KORPUS = [
    {"kanun_no": "6098", "kanun_adi": "TÜRK BORÇLAR KANUNU", "madde_no": "Madde 350", "text": "x"},
    {"kanun_no": "6098", "kanun_adi": "TÜRK BORÇLAR KANUNU", "madde_no": "Madde 353", "text": "y"},
    {"kanun_no": "4721", "kanun_adi": "TÜRK MEDENİ KANUNU", "madde_no": "Madde 1024", "text": "z"},
]


def _hukumler(cevap):
    return [dogrula(a, KORPUS) for a in atiflari_ayikla(cevap)]


IYI = "TÜRK BORÇLAR KANUNU Madde 350 uygulanır. Ayrıca TÜRK BORÇLAR KANUNU Madde 353 geçerlidir."
KARISIK = ("TÜRK BORÇLAR KANUNU Madde 350 uygulanır. Ayrıca TÜRK BORÇLAR KANUNU Madde 353 "
           "geçerlidir. Buna ek olarak TÜRK MEDENİ KANUNU Madde 9999 gereklidir.")


def test_kati_tum_atiflar_dogruysa_gecirir():
    k = kapi(IYI, _hukumler(IYI), KATI)
    assert k.gecti and k.n_atif == 2 and k.n_dogrulanan == 2


def test_kati_tek_dogrulanamayan_atif_tum_cevabi_reddettirir():
    # ADR-0038'in tam hükmü: ikili, ara durum yok.
    k = kapi(KARISIK, _hukumler(KARISIK), KATI)
    assert not k.gecti and k.n_atif == 3 and k.n_dogrulanan == 2


def test_kati_ayristirilamayan_atifi_da_reddettirir():
    cevap = "Bu konu Türk Medeni Kanunu'nun ilgili maddelerinde düzenlenmiştir."
    h = _hukumler(cevap)
    assert h and not kapi(cevap, h, KATI).gecti


def test_atifsiz_cevap_kapidan_gecer_ve_ayri_sayilir():
    # Çekinme cevabında atıf yoktur; kapı atıf kapısıdır, reddedecek bir şey yok.
    # ⚠️ n_atif=0 ayrıca raporlanır: 'atıfsız geçti' kendi sınıfıdır (bkz. modül notu).
    cevap = "Verilen kaynaklarda bu konuyu düzenleyen madde bulunmuyor."
    k = kapi(cevap, _hukumler(cevap), KATI)
    assert k.gecti and k.n_atif == 0


def test_cogunluk_yarisindan_fazlasi_dogruysa_gecirir():
    k = kapi(KARISIK, _hukumler(KARISIK), COGUNLUK)
    assert k.gecti and k.n_dogrulanan == 2


def test_cogunluk_yarisi_yetmez():
    cevap = "TÜRK BORÇLAR KANUNU Madde 350 ve TÜRK MEDENİ KANUNU Madde 9999 uygulanır."
    assert not kapi(cevap, _hukumler(cevap), COGUNLUK).gecti


def test_cerrahi_yalnizca_kotu_atifin_cumlesini_atar():
    k = kapi(KARISIK, _hukumler(KARISIK), CERRAHI)
    assert k.gecti
    assert "Madde 9999" not in k.cevap
    assert "Madde 350" in k.cevap and "Madde 353" in k.cevap


def test_cerrahi_gecerli_cumle_kalmazsa_reddeder():
    cevap = "TÜRK MEDENİ KANUNU Madde 9999 uygulanır."
    assert not kapi(cevap, _hukumler(cevap), CERRAHI).gecti


def test_politikalar_ayni_cevapta_post_hoc_kosulabilir():
    # ADR-0038: üç politika aynı cevap kümesinde post-hoc uygulanır, yeniden
    # üretim gerekmez — coverage/precision eğrisi bu yüzden ~0 maliyetli.
    h = _hukumler(KARISIK)
    assert [kapi(KARISIK, h, p).gecti for p in (KATI, COGUNLUK, CERRAHI)] == [False, True, True]
