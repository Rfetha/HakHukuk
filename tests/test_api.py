"""Görev 19 — HTTP API kapı testleri.

⚠️ Sunucu ve model GEREKMEZ: `servis.answer` monkeypatch'lenir. Sebep, ölçüm hattının kendi
dersi — bir kabuğun sözleşmesini sınamak için 2,6 GB'lık modeli ayağa kaldırmak, testi
çalıştırılamaz kılar ve kapı fiilen düşer.
⛔ API bir İNCE KABUKtur: sınıflandırma, atıf doğrulama ve kaynak seçimi `answer()`'ın
içindedir. Buraya sızarsa iki yerde bakım doğar (S18'in ölçülmüş dersi).
"""
import pathlib

import pytest
from fastapi.testclient import TestClient

from hakhukuk.arayuz import cli
from hakhukuk.cekirdek.tipler import Atif, Cevap, Durum, Kaynak

KOK = pathlib.Path(__file__).resolve().parent.parent


def _cevap(metin="Sözleşme 10 yılda zamanaşımına uğrar.", durum=Durum.CEVAP):
    return Cevap(
        metin=metin,
        durum=durum,
        atiflar=(Atif(kanun_no="6098", madde_no="146", dogrulandi=True),),
        kaynaklar=(Kaynak(kanun_adi="TÜRK BORÇLAR KANUNU", kanun_no="6098",
                          madde_no="146", metin="…", sira=1),),
    )


@pytest.fixture
def istemci(monkeypatch):
    from hakhukuk.arayuz import api
    monkeypatch.setattr(api.servis, "answer", lambda soru, **kw: _cevap())
    return TestClient(api.uygulama)


# ── karar 2: yapısal alanlar + HAZIR `sunum` dizesi ────────────────────────────────────────

def test_sunum_dizesi_dort_parcayi_da_tasiyor(istemci):
    """Tembel tüketici tek alanı bassa bile rozet + atıf + kaynak + ibare gitmeli.

    Dürüstlük sözleşmesi CLI'da vardı; HTTP'ye geçerken düşmemeli.
    """
    g = istemci.post("/sor", json={"soru": "zamanaşımı kaç yıl"})
    assert g.status_code == 200
    sunum = g.json()["sunum"]
    assert "CEVAP" in sunum                      # rozet
    assert "6098/146" in sunum                   # atıf
    assert "TÜRK BORÇLAR KANUNU" in sunum        # kaynak
    assert cli.SORUMLULUK_IBARESI in sunum       # ibare


def test_yapisal_alanlar_da_var(istemci):
    g = istemci.post("/sor", json={"soru": "zamanaşımı kaç yıl"}).json()
    assert g["durum"] == "cevap"
    assert g["atiflar"] == [{"kanun_no": "6098", "madde_no": "146", "dogrulandi": True}]
    assert g["kaynaklar"][0]["kanun_adi"] == "TÜRK BORÇLAR KANUNU"
    assert g["metin"].startswith("Sözleşme")


def test_sorumluluk_ibaresi_TEK_kaynaktan_geliyor():
    """`cli.py`'den IMPORT edilir, kopyalanmaz — aynı metin iki yerde sessizce ayrışır."""
    kaynak = (KOK / "hakhukuk" / "arayuz" / "api.py").read_text(encoding="utf-8")
    assert "SORUMLULUK_IBARESI" in kaynak
    assert "hukuki tavsiye değil" not in kaynak


# ── karar 4: boş metin → 503 · dolu KESİK → 200 ────────────────────────────────────────────

def test_bos_metin_503_doner(monkeypatch):
    """*"HTTP 200 ile boş içerik"* bu hattın #42'de ölçtüğü kusurun ADIDIR; sınırı geçmesin."""
    from hakhukuk.arayuz import api
    monkeypatch.setattr(api.servis, "answer",
                        lambda soru, **kw: _cevap(metin="   ", durum=Durum.KESIK))
    g = TestClient(api.uygulama).post("/sor", json={"soru": "x"})
    assert g.status_code == 503


def test_dolu_kesik_200_doner_ve_durumu_GIZLENMEZ(monkeypatch):
    """KESİK yarım bir cevaptır ama cevaptır — 503'e çevirmek bilgiyi yok eder."""
    from hakhukuk.arayuz import api
    monkeypatch.setattr(api.servis, "answer",
                        lambda soru, **kw: _cevap(metin="Yarım kalan bir cümle",
                                                  durum=Durum.KESIK))
    g = TestClient(api.uygulama).post("/sor", json={"soru": "x"})
    assert g.status_code == 200
    assert g.json()["durum"] == "kesik"
    assert "KESİK" in g.json()["sunum"]


# ── karar 5: boş/boşluk sorgu → 422, UYDURULMUŞ uzunluk eşiği YOK ──────────────────────────

@pytest.mark.parametrize("soru", ["", "   ", "\t\n"])
def test_bos_sorgu_422(istemci, soru):
    """Ölçüldü 2026-09-09: `_getir("")` sabit bir gürültü kümesi döndürüyor (ticket 4)."""
    assert istemci.post("/sor", json={"soru": soru}).status_code == 422


def test_KISA_ama_dolu_sorgu_REDDEDILMEZ(istemci):
    """Uydurulmuş uzunluk eşiği YOK: 'kira?' geçerli bir sorudur."""
    assert istemci.post("/sor", json={"soru": "kira?"}).status_code == 200


# ── karar 3 + ince kabuk kapısı ────────────────────────────────────────────────────────────

def test_api_kendi_mantigi_yok_yalnizca_answer_cagirir():
    """`test_tui.py`'nin aynı kapısı. Mantık sızarsa iki yerde bakım doğar."""
    kaynak = (KOK / "hakhukuk" / "arayuz" / "api.py").read_text(encoding="utf-8")
    for yasak in ("REJECT_RE", "re.compile", "siniflandir(", "_getir(", "_uret("):
        assert yasak not in kaynak, f"api.py kendi mantığını taşıyor: {yasak}"


def test_answer_arac_ACILMADI():
    """Taşıyıcı araç çağrısı ayrıştırmıyor ⇒ açılırsa tüketici araç kullanıldığını SANIR."""
    kaynak = (KOK / "hakhukuk" / "arayuz" / "api.py").read_text(encoding="utf-8")
    assert "answer_arac" not in kaynak


# ── karar 1 + 6: yerel · tek kullanıcı · serileştirilmiş istek ─────────────────────────────

def test_sunucu_YALNIZ_yerel_arayuze_baglanir():
    """S9 açılmadı: API yerel ve tek kullanıcıdır. `0.0.0.0` sessizce girerse S9 açılmış olur."""
    from hakhukuk.arayuz import api
    assert api.HOST == "127.0.0.1"
    kaynak = (KOK / "hakhukuk" / "arayuz" / "api.py").read_text(encoding="utf-8")
    assert "0.0.0.0" not in kaynak


def test_istekler_SERILESTIRILIR():
    """Tekilin evre güvenliği ÖLÇÜLMEDİ; ölçüm rejimi sıralı istekti. Kilit GÖRÜNÜR olmalı."""
    from hakhukuk.arayuz import api
    assert api._KILIT is not None


def test_api_ekstrasi_cekirdek_kurulumu_SISIRMEZ():
    """`fastapi`/`uvicorn` çekirdek bağımlılık DEĞİL — opsiyonel ekstra `hakhukuk[api]`.

    ⚠️ Metin araması DEĞİL, `tomllib` ile yapı okunur: ilk sürümü yorum satırındaki bir
    "fastapi" geçişine takıldı ve KODU değil ALETİ yanılttı — bu hattın bilinen sınıfı.
    """
    import tomllib
    veri = tomllib.loads((KOK / "pyproject.toml").read_text(encoding="utf-8"))
    cekirdek = " ".join(veri["project"]["dependencies"])
    assert "fastapi" not in cekirdek and "uvicorn" not in cekirdek
    ekstra = " ".join(veri["project"]["optional-dependencies"]["api"])
    assert "fastapi" in ekstra and "uvicorn" in ekstra
    assert veri["project"]["scripts"]["hakhukuk-api"] == "hakhukuk.arayuz.api:main"
