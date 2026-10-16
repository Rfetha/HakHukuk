"""Servis katmanının kapı testleri (plan Görev 9). Sunucu ve indeks GEREKMEZ."""
from hakhukuk.cekirdek import servis
from hakhukuk.cekirdek.tipler import Durum, Kaynak

IS_K_31 = Kaynak(kanun_adi="İŞ KANUNU", kanun_no="4857", madde_no="Madde 31",
                 metin="Muvazzaf askerlik ödevi dışında …", sira=1)


def test_answer_kaynaklari_ve_atiflari_dondurur(monkeypatch):
    monkeypatch.setattr(servis, "_getir", lambda soru, k: (IS_K_31,))
    monkeypatch.setattr(servis, "_uret",
                        lambda mesajlar: ("İş Kanunu Madde 31 uyarınca askıya alınır.", "stop"))
    c = servis.answer("Askerlik nedeniyle iş sözleşmesi ne olur?")
    assert c.durum is Durum.CEVAP
    assert c.kaynaklar == (IS_K_31,)
    assert any(a.dogrulandi for a in c.atiflar)


def test_answer_bos_getirmede_susar(monkeypatch):
    """Retriever boş dönerse model konuşturulmaz — üründe M5 koşulu OLUŞMAMALI."""
    monkeypatch.setattr(servis, "_getir", lambda soru, k: ())
    patladi = []
    monkeypatch.setattr(servis, "_uret",
                        lambda mesajlar: patladi.append(1) or ("olmamalı", "stop"))
    c = servis.answer("İlgisiz soru")
    assert c.durum is Durum.SUSKUNLUK
    assert c.kaynaklar == ()
    assert not patladi, "🚨 kaynaksız soruda model ÇAĞRILDI — üründe M5 koşulu oluştu"


def test_answer_kesigi_gizlemez(monkeypatch):
    monkeypatch.setattr(servis, "_getir", lambda soru, k: (IS_K_31,))
    monkeypatch.setattr(servis, "_uret", lambda mesajlar: ("Yarım cüm", "length"))
    assert servis.answer("x").durum is Durum.KESIK


# ── Araç katmanı — çok adımlı mod (Görev 18 · ADR-0076) ──────────────────────
# ⛔ Bu testlerin hiçbiri sunucu, indeks ya da ağ istemez.

class _SahteAraclar:
    """`ara` çağrıldığını kaydeder; başka araç kullanılmaz."""

    def __init__(self, sonuc=(IS_K_31,)):
        self.cagrildi = []
        self._sonuc = sonuc

    def ara(self, sorgu, k=10):
        self.cagrildi.append((sorgu, k))
        return self._sonuc


def _uret_dizisi(*adimlar):
    """Her çağrıda sıradaki `(metin, finish, arac_cagrilari)` üçlüsünü döndürür."""
    kalan = list(adimlar)

    def uret(mesajlar, semalar=None):
        return kalan.pop(0) if kalan else ("", "stop", ())
    return uret


def test_arac_dongusu_SINIRA_dayaninca_ARAMA_TUKENDI(monkeypatch):
    """⛔ Sınır GÖRÜNÜR olmalı (ADR-0076). Model sonsuza kadar arayamaz ve sınıra
    dayandığında vatandaşa sessizce yarım dayanaklı bir cevap teslim EDİLMEZ."""
    monkeypatch.setattr(servis, "_getir", lambda soru, k: (IS_K_31,))
    a = _SahteAraclar()
    hep_arar = lambda mesajlar, semalar=None: ("", "stop", ({"ad": "ara", "arg": {"sorgu": "x"}},))
    c = servis.answer_arac("x", araclar=a, uret=hep_arar, azami_adim=3)
    assert c.durum is Durum.ARAMA_TUKENDI
    assert len(a.cagrildi) == 3, "döngü sınırı uygulanmadı"


def test_ARAMA_TUKENDI_KESIK_DEGILDIR(monkeypatch):
    """İkisi vatandaşa farklı şey söyler; birleştirilmeleri sınırı görünmez kılardı."""
    monkeypatch.setattr(servis, "_getir", lambda soru, k: (IS_K_31,))
    hep_arar = lambda mesajlar, semalar=None: ("", "stop", ({"ad": "ara", "arg": {"sorgu": "x"}},))
    c = servis.answer_arac("x", araclar=_SahteAraclar(), uret=hep_arar, azami_adim=1)
    assert c.durum is Durum.ARAMA_TUKENDI and c.durum is not Durum.KESIK


def test_KAPILAR_arac_hic_cagrilmasa_da_calisir(monkeypatch):
    """🔒 KAPI ↔ KALDIRAÇ (ADR-0076): atıf doğrulama ve durum sınıflandırma döngünün
    DIŞINDA, koşulsuz çalışır. Uydurma madde 0/114 garantisi buradan geliyor."""
    monkeypatch.setattr(servis, "_getir", lambda soru, k: (IS_K_31,))
    a = _SahteAraclar()
    uret = _uret_dizisi(("İş Kanunu Madde 31 uyarınca askıya alınır.", "stop", ()))
    c = servis.answer_arac("x", araclar=a, uret=uret)
    assert a.cagrildi == [], "araç çağrılmadı, doğru"
    assert c.durum is Durum.CEVAP
    assert any(x.dogrulandi for x in c.atiflar), "🚨 KAPI atlandı — atıf doğrulanmadı"


def test_arac_sonuclari_KAYNAKLARA_eklenir(monkeypatch):
    """Vatandaş, cevabın hangi maddelere dayandığını görmeli — araçla gelen de dahil."""
    ek = Kaynak(kanun_adi="İŞ KANUNU", kanun_no="4857", madde_no="Madde 21",
                metin="İşe iade.", sira=1)
    monkeypatch.setattr(servis, "_getir", lambda soru, k: (IS_K_31,))
    uret = _uret_dizisi(
        ("", "stop", ({"ad": "ara", "arg": {"sorgu": "işe iade"}},)),
        ("İş Kanunu Madde 21 uyarınca başvurulur.", "stop", ()))
    c = servis.answer_arac("x", araclar=_SahteAraclar((ek,)), uret=uret)
    assert c.durum is Durum.CEVAP
    kimlikler = {s.kimlik for s in c.kaynaklar}
    assert IS_K_31.kimlik in kimlikler and ek.kimlik in kimlikler


def test_araclı_yol_KESIGI_de_gizlemez(monkeypatch):
    monkeypatch.setattr(servis, "_getir", lambda soru, k: (IS_K_31,))
    uret = _uret_dizisi(("Yarım cüm", "length", ()))
    assert servis.answer_arac("x", araclar=_SahteAraclar(), uret=uret).durum is Durum.KESIK


# ── Görev 22 kusur 1 — ÜRÜN YOLUNDA İKİ GEÇİŞLİ ZORUNLU DÜŞÜNCE KAPATMASI ────────────
# 🛑 İnsan rejim onayı 2026-09-11: ürün yolu, ölçüm hattının rejimine gelir. Yayımlanan
# 0,8011 ÖLÇÜM HATTININ sayısıdır ve değişmez; değişen ürün yoludur.
# Ölçülmüş kusur: `aracsiz_yol_80.json` → 4/80 kalem TAMAMEN BOŞ (id 7·64·65·66), 7/80 kesik.
# Sebep sonlanmama (research_log #42): model `</think>`'i kapatmıyor, bütçeyi düşüncede
# bitiriyor, llama-server HTTP 200 + boş `content` + dolu `reasoning_content` döndürüyor.
# ⛔ Bu testlerin hiçbiri ağ/GPU/model istemez — `_istek` (tek HTTP dikişi) sahtelenir.

def _sahte_istek(*yanitlar):
    """Sırayla verilen yanıtları döndürür; çağrılan (url, gövde) çiftlerini kaydeder."""
    kalan = list(yanitlar)
    kayit = []

    def istek(url, govde):
        kayit.append((url, govde))
        return kalan.pop(0)
    return istek, kayit


def _yanit_dusunce_kapanmadi(dusunce="Kaynak 1 askerlik iznini düzenliyor, kaynak 2 ilgisiz"):
    """llama-server'ın ölçülmüş davranışı: HTTP 200, boş içerik, dolu düşünce izi."""
    return {"choices": [{"message": {"content": "", "reasoning_content": dusunce},
                         "finish_reason": "length"}]}


def test_uret_dusunce_kapanmazsa_BOS_METIN_DONMEZ(monkeypatch):
    """🚨 Kusur 1'in çivisi: `</think>` kapanmadığında ürün yolu boş metin DÖNDÜREMEZ."""
    istek, kayit = _sahte_istek(
        _yanit_dusunce_kapanmadi(),
        {"prompt": "<|im_start|>system…<|im_start|>assistant\n<think>\n"},
        {"choices": [{"text": "İş Kanunu Madde 31 uyarınca sözleşme askıya alınır.",
                      "finish_reason": "stop"}]},
    )
    monkeypatch.setattr(servis, "_istek", istek)
    metin, finish = servis._uret([{"role": "user", "content": "x"}])
    assert metin.strip(), "düşünce kapanmadı ve ürün yolu BOŞ METİN döndürdü"
    assert finish == "stop"
    assert len(kayit) == 3, f"iki geçişli zorunlu kapatma yapılmadı (istek sayısı {len(kayit)})"


def test_uret_zorunlu_kapatmada_iz_ve_think_kapanisi_isteme_ekleniyor(monkeypatch):
    """2. geçiş: şablonun ham istemi + düşünce izi + `</think>` — model cevabı yazmak
    ZORUNDA kalır. İz atılırsa model kendi muhakemesini görmeden cevaplar (rejim değişir)."""
    iz = "Kaynak 3 bu soruyu karşılıyor"
    istek, kayit = _sahte_istek(
        _yanit_dusunce_kapanmadi(iz),
        {"prompt": "HAM_ISTEM"},
        {"choices": [{"text": "cevap", "finish_reason": "stop"}]},
    )
    monkeypatch.setattr(servis, "_istek", istek)
    servis._uret([{"role": "user", "content": "x"}])
    sablon_url, _ = kayit[1]
    tamamlama_url, tamamlama_govde = kayit[2]
    assert sablon_url.endswith("/apply-template"), f"şablon uç noktası değil: {sablon_url}"
    assert tamamlama_url.endswith("/completions") and "/chat/" not in tamamlama_url, (
        f"2. geçiş sohbet uç noktasına gitti (mid-mesaj devam ettiremez): {tamamlama_url}")
    istem = tamamlama_govde["prompt"]
    assert istem.startswith("HAM_ISTEM"), "şablonun ham istemi kullanılmadı"
    assert iz in istem, "düşünce izi 2. geçişe taşınmadı"
    assert istem.rstrip().endswith("</think>"), "`</think>` zorla kapatılmadı"
    assert tamamlama_govde["max_tokens"] == servis.CEVAP_BUTCESI, (
        "2. geçiş cevap bütçesini almadı — bütçe hâlâ tek havuz")


def test_uret_dusunce_kapanirsa_IKINCI_GECIS_YAPILMAZ(monkeypatch):
    """Muhafız: normal kalemde fazladan istek YOK — 80 kalemin 76'sı bu daldan geçiyor."""
    istek, kayit = _sahte_istek(
        {"choices": [{"message": {"content": "Madde 31 uyarınca askıya alınır.",
                                  "reasoning_content": "kısa muhakeme"},
                      "finish_reason": "stop"}]})
    monkeypatch.setattr(servis, "_istek", istek)
    metin, finish = servis._uret([{"role": "user", "content": "x"}])
    assert metin.startswith("Madde 31") and finish == "stop"
    assert len(kayit) == 1, f"gereksiz 2. geçiş yapıldı ({len(kayit)} istek)"


def test_uret_ilk_gecis_butcesi_dusunce_arti_cevap(monkeypatch):
    """ADR-0043 · ADR-0070: 1. geçiş 1024+512 = 1536 alır (ölçüm hattıyla birebir)."""
    istek, kayit = _sahte_istek(
        {"choices": [{"message": {"content": "x"}, "finish_reason": "stop"}]})
    monkeypatch.setattr(servis, "_istek", istek)
    servis._uret([{"role": "user", "content": "x"}])
    assert kayit[0][1]["max_tokens"] == servis.DUSUNCE_BUTCESI + servis.CEVAP_BUTCESI


def test_uret_zorunlu_kapatma_sonrasi_KESIK_hala_damgalaniyor(monkeypatch):
    """⛔ `Durum.KESIK` KORUNUR: 2. geçiş de bütçeyi doldurursa kesiklik GİZLENMEZ."""
    istek, _ = _sahte_istek(
        _yanit_dusunce_kapanmadi(),
        {"prompt": "HAM"},
        {"choices": [{"text": "Yarım cüm", "finish_reason": "length"}]},
    )
    monkeypatch.setattr(servis, "_istek", istek)
    monkeypatch.setattr(servis, "_getir", lambda soru, k: (IS_K_31,))
    assert servis.answer("x").durum is Durum.KESIK


def test_answer_dusunce_kapanmazsa_bos_cevap_teslim_etmez(monkeypatch):
    """Uçtan uca: kusurun ölçüldüğü hâl (`answer()` boş metin) artık ÜRETİLEMEZ."""
    istek, _ = _sahte_istek(
        _yanit_dusunce_kapanmadi(),
        {"prompt": "HAM"},
        {"choices": [{"text": "İş Kanunu Madde 31 uyarınca askıya alınır.",
                      "finish_reason": "stop"}]},
    )
    monkeypatch.setattr(servis, "_istek", istek)
    monkeypatch.setattr(servis, "_getir", lambda soru, k: (IS_K_31,))
    c = servis.answer("Askerlikte sözleşme ne olur?")
    assert c.metin.strip(), "🚨 ürün vatandaşa BOŞ cevap teslim etti"
    assert c.durum is Durum.CEVAP


def test_answer_arac_da_ayni_rejime_geliyor(monkeypatch):
    """İkisi de ÜRÜN YOLUDUR; araçlı yol da `_uret` üzerinden zorunlu kapatmayı alır."""
    istek, kayit = _sahte_istek(
        _yanit_dusunce_kapanmadi(),
        {"prompt": "HAM"},
        {"choices": [{"text": "Madde 31 uyarınca askıya alınır.", "finish_reason": "stop"}]},
    )
    monkeypatch.setattr(servis, "_istek", istek)
    monkeypatch.setattr(servis, "_getir", lambda soru, k: (IS_K_31,))
    c = servis.answer_arac("x", araclar=_SahteAraclar())
    assert c.metin.strip(), "🚨 araçlı ürün yolu BOŞ cevap teslim etti"
    assert len(kayit) == 3, "araçlı yol zorunlu kapatmayı almadı"


# ── Görev 21 kusur 20 — ÇALIŞMA ANI KAPISI: reasoning kanalı yoksa ERKEN ve GÜRÜLTÜLÜ ──
#
# ADR-0080'in 2. geçişi `message.reasoning_content` alanına BAĞIMLIDIR. `llama-server`'ın
# `--reasoning-format` varsayılanı değişir ve iz ayrı alanda dönmezse, ayrım noktasındaki
# *"içerik boş VE iz dolu"* koşulu hiç tutmaz: mekanizma SESSİZCE tek geçişe düşer ve boş
# cevap kusuru (4/80) geri gelir. İnsan kararı 2026-09-11: kapı KODA, açık bayrak
# compose'a (compose yarısı `1d0c616`'da yapıldı). ⛔ Sessiz düşüş YASAK — ADR-0026 kalıbı.

def _kapiyi_sifirla(monkeypatch):
    """Kapı bir KEZ yoklanır ⇒ bayrak modül düzeyinde. Testler yalıtılmalı."""
    monkeypatch.setattr(servis, "_REASONING_KANALI_GORULDU", False)


def test_uret_reasoning_kanali_YOKSA_erken_patlar(monkeypatch):
    """🚨 Sunucu boş içerik döndürüyor ve `reasoning_content` HİÇ YOK ⇒ mekanizma ölü."""
    import pytest
    _kapiyi_sifirla(monkeypatch)
    istek, _ = _sahte_istek({"choices": [{"message": {"content": ""},
                                          "finish_reason": "length"}]})
    monkeypatch.setattr(servis, "_istek", istek)
    with pytest.raises(RuntimeError) as hata:
        servis._uret([{"role": "user", "content": "x"}])
    assert "--reasoning-format" in str(hata.value), "hata mesajı ONARIM YOLUNU söylemiyor"


def test_uret_dusunce_CONTENT_icine_gomulurse_erken_patlar(monkeypatch):
    """`--reasoning-format none`: iz `content`'in içinde `<think>` olarak gelir. Sunucu
    "dolu" cevap döndürür, 2. geçiş hiç tetiklenmez ve vatandaşa MUHAKEME METNİ gider."""
    import pytest
    _kapiyi_sifirla(monkeypatch)
    istek, _ = _sahte_istek({"choices": [
        {"message": {"content": "<think>Kaynak 1 ilgili görünüyor"},
         "finish_reason": "length"}]})
    monkeypatch.setattr(servis, "_istek", istek)
    with pytest.raises(RuntimeError):
        servis._uret([{"role": "user", "content": "x"}])


def test_kapi_DUSUNCESIZ_mesru_sunucuyu_OLDURMEZ(monkeypatch):
    """⚠️ Kapının gerçek tehlikesi buydu: `reasoning_content` döndürmeyen MEŞRU bir
    yapılandırmayı da öldürebilirdi. Öldürmez — çünkü kapı bir AÇILIŞ YOKLAMASI değil,
    GÖZLEM kapısıdır: yalnız zaten kusurlu olan hâlde (boş içerik ya da `<think>` sızıntısı)
    ateşler. Düşünmeyen ama düzgün cevap veren bir sunucu bu dala hiç girmez."""
    _kapiyi_sifirla(monkeypatch)
    istek, kayit = _sahte_istek({"choices": [
        {"message": {"content": "Madde 31 uyarınca askıya alınır."}, "finish_reason": "stop"}]})
    monkeypatch.setattr(servis, "_istek", istek)
    metin, finish = servis._uret([{"role": "user", "content": "x"}])
    assert metin.startswith("Madde 31") and finish == "stop"
    assert len(kayit) == 1, "meşru yapılandırmaya fazladan istek atıldı"


def test_kapi_BIR_KEZ_yoklanir_sonra_karismaz(monkeypatch):
    """Kanal bir kez görüldükten sonra kapı kenara çekilir: sunucunun `reasoning_format`'ı
    koşu ortasında değişmez. Aksi hâlde her kalemde yeniden hüküm kurulurdu."""
    _kapiyi_sifirla(monkeypatch)
    istek, _ = _sahte_istek(
        _yanit_dusunce_kapanmadi(),                       # kanal GÖRÜLÜR
        {"prompt": "HAM"},
        {"choices": [{"text": "cevap", "finish_reason": "stop"}]},
        {"choices": [{"message": {"content": ""}, "finish_reason": "length"}]},
    )
    monkeypatch.setattr(servis, "_istek", istek)
    servis._uret([{"role": "user", "content": "x"}])
    assert servis._REASONING_KANALI_GORULDU, "kanal görüldü ama bayrak kalkmadı"
    metin, _ = servis._uret([{"role": "user", "content": "y"}])   # patlamamalı
    assert metin == ""
