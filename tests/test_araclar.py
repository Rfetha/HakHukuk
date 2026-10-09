"""Araç katmanı — KALDIRAÇ'lar (ADR-0076).

⛔ Bu testlerin hiçbiri ağ, model ya da indeks İSTEMEZ. Araçlar deterministiktir; LLM
çağıran bir araç yeni bir hata kaynağı olurdu ve ADR-0076 bunu yasaklıyor.
"""
import pytest

from hakhukuk.cekirdek.araclar import Araclar
from hakhukuk.cekirdek.tipler import Kaynak, Yururluk


KORPUS = [
    {"kanun_no": "4857", "kanun_adi": "İŞ KANUNU", "madde_no": "Madde 21",
     "text": "İşe iade davası açan işçi işverene başvurur.", "mulga": False},
    {"kanun_no": "4857", "kanun_adi": "İŞ KANUNU", "madde_no": "Madde 111",
     "text": "Sanayiden sayılacak işlerin esasları.", "mulga": False},
    {"kanun_no": "1475", "kanun_adi": "İŞ KANUNU", "madde_no": "Madde 111",
     "text": "Mülga hüküm.", "mulga": True},
    {"kanun_no": "634", "kanun_adi": "KAT MÜLKİYETİ KANUNU", "madde_no": "Geçici Madde 1",
     "text": "Ortak giderlere katılmayan kat maliki gecikme tazminatı öder.", "mulga": False},
    # ⚠️ Kusur 18/21 çivileri: SONDA parantezli ad + onun gevşek eşleşmede çalındığı kanun,
    # ve resmî adın yalnız SONEKİ yazılan kanun. İkisi de gerçek atıflarda ölçüldü.
    {"kanun_no": "193", "kanun_adi": "GELİR VERGİSİ KANUNU (G.V.K.)", "madde_no": "Madde 73",
     "text": "Emsal kira bedeli esası.", "mulga": False},
    {"kanun_no": "1319", "kanun_adi": "EMLAK VERGİSİ KANUNU", "madde_no": "Madde 1",
     "text": "Bina vergisinin mevzuu.", "mulga": False},
    {"kanun_no": "2004", "kanun_adi": "İCRA VE İFLAS KANUNU", "madde_no": "Madde 1",
     "text": "İcra daireleri.", "mulga": False},
]


@pytest.fixture
def araclar():
    return Araclar(KORPUS)


# ── madde_getir · madde_var_mi ────────────────────────────────────────────────

def test_madde_getir_kaynak_dondurur(araclar):
    k = araclar.madde_getir("4857", "Madde 21")
    # ⚠️ `.lower()` KULLANILMAZ: Python'ın `"İ".lower()` çıktısı `i̇` (birleşen noktalı i) ve
    # eşleşmiyor — kodun kendi belgelediği tuzağın aynısı (`_ad_normal` docstring'i).
    assert isinstance(k, Kaynak) and k.kanun_no == "4857" and "iade davası" in k.metin


def test_madde_getir_yoksa_None(araclar):
    assert araclar.madde_getir("4857", "Madde 9999") is None


def test_madde_kimligi_madde_anahtari_ile_karsilastirilir(araclar):
    """⛔ Düz metin karşılaştırması korpusun %22'sinde yanlış negatif veriyordu.

    `MADDE 21` ↔ `Madde 21` aynı maddedir; `Geçici Madde 1` ↔ `Madde 1` AYRI maddelerdir.
    """
    assert araclar.madde_var_mi("4857", "MADDE 21") is True
    assert araclar.madde_var_mi("4857", "madde 21") is True
    assert araclar.madde_var_mi("634", "Geçici Madde 1") is True
    assert araclar.madde_var_mi("634", "Madde 1") is False


# ── yururlukte_mi ─────────────────────────────────────────────────────────────

def test_yururlukte_mi_uc_hal(araclar):
    assert araclar.yururlukte_mi("4857", "Madde 111") is Yururluk.YALNIZ_YURURLUKTE
    assert araclar.yururlukte_mi("1475", "Madde 111") is Yururluk.MULGA_DAHIL
    assert araclar.yururlukte_mi("4857", "Madde 9999") is None


# ── kanun_bul ─────────────────────────────────────────────────────────────────

def test_kanun_bul_cok_anlamli_adda_HEPSINI_dondurur(araclar):
    """🚨 Donmuş TEST'in dersi (2026-09-09): `İŞ KANUNU` hem 4857 hem 1475'tir.

    Tek numara döndürmek, atıf doğrulayıcıyı mülga olana bağlayan kusurun aynısını
    araç katmanında yeniden üretirdi.
    """
    assert set(araclar.kanun_bul("İş Kanunu")) == {("4857", "İŞ KANUNU"), ("1475", "İŞ KANUNU")}
    assert araclar.kanun_bul("Bulunmayan Kanun") == ()


# ── ara ───────────────────────────────────────────────────────────────────────

def test_ara_retriever_olmadan_ACIKCA_patlar(araclar):
    """⛔ Sessiz boş liste YASAK: 'arama sonuç vermedi' ile 'arama hiç çalışmadı'
    vatandaşa AYNI ŞEYİ söylemez ve ikincisi bir kusurdur."""
    with pytest.raises(RuntimeError, match="retriever"):
        araclar.ara("işe iade")


def test_ara_verilen_retrieveri_kullanir():
    cagri = {}

    def sahte_getir(soru, k, yururluk):
        cagri["soru"], cagri["k"], cagri["yururluk"] = soru, k, yururluk
        return [dict(KORPUS[0], skor=1.0, sira=0)]

    a = Araclar(KORPUS, getir=sahte_getir)
    sonuc = a.ara("işe iade", k=3)
    assert cagri == {"soru": "işe iade", "k": 3, "yururluk": Yururluk.YALNIZ_YURURLUKTE}
    assert len(sonuc) == 1 and isinstance(sonuc[0], Kaynak) and sonuc[0].sira == 1


# ── ⛔ KALDIRAÇ sınırı: hiçbir araç LLM çağırmaz ───────────────────────────────

def test_hicbir_arac_LLM_cagirmaz():
    """ADR-0076: araç katmanı DETERMİNİSTİK kalır. Model çağıran bir araç, ölçülemeyen
    ikinci bir hata kaynağıdır ve kapıların garantisini buharlaştırır."""
    import inspect

    from hakhukuk.cekirdek import araclar as m
    kaynak = inspect.getsource(m)
    for yasak in ("_uret(", "chat/completions", "urllib", "openai", "requests"):
        assert yasak not in kaynak, f"araç katmanına model çağrısı sızmış: {yasak}"


# ── ad çözümü: ÜRÜN YÜZEYİ ↔ ÖLÇÜM ALETİ tek kaynak (kusur 21) ────────────────

def _olcum_adaylari(ad: str) -> set:
    """Ölçüm hattının (onarılmış `atif_dogrula`) aynı girdideki cevabı."""
    from atif_dogrula import _ad_adaylari, _dizin_kur
    return set(_ad_adaylari(ad, _dizin_kur(KORPUS)))


@pytest.mark.parametrize("ad", [
    "Gelir Vergisi Kanunu", "GELİR VERGİSİ KANUNU", "Emlak Vergisi Kanunu",
    "İş Kanunu", "İflas Kanunu", "İcra ve İflas Kanunu",
    "Kat Mülkiyeti Kanunu", "Bulunmayan Kanun", "Kanunu",
])
def test_kanun_bul_atif_dogrula_ile_AYNI_sonucu_verir(araclar, ad):
    """🚨 Tuzak 2.18: aynı ölçümün İKİ aleti sessizce ayrışır.

    Ürün yüzeyinin ad çözümü ile yayımlanan sayıyı üreten doğrulayıcınınki AYNI
    olmalıdır; ayrıştıkları an vatandaşa giden rozet ile rapor edilen sayı farklı
    dünyalardan gelir.
    """
    assert {no for no, _ in araclar.kanun_bul(ad)} == _olcum_adaylari(ad)


def test_kanun_bul_parantezli_adi_DOGRU_kanuna_cozer(araclar):
    """⛔ Kusur 18'in ürün yüzeyindeki hâli: *"Gelir Vergisi Kanunu"* → **193**, `1319` DEĞİL.

    Korpus adı `GELİR VERGİSİ KANUNU (G.V.K.)`; sondaki parantez atılmadan birebir
    eşleşme tutmaz ve çözüm `VERGİSİ KANUNU` soneğine düşüp EMLAK VERGİSİ'ne giderdi.
    """
    bulunan = {no for no, _ in araclar.kanun_bul("Gelir Vergisi Kanunu")}
    assert bulunan == {"193"}, f"1319'a kayma ya da çözememe: {bulunan}"


def test_kanun_bul_resmi_adin_SONEGINI_de_cozer(araclar):
    """Model resmî adın kısa hâlini yazıyor: *"İflas Kanunu"* ⊂ `İCRA VE İFLAS KANUNU`."""
    assert {no for no, _ in araclar.kanun_bul("İflas Kanunu")} == {"2004"}
