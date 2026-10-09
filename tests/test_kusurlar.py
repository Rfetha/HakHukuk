"""Görev 21 — kusur 3·4·5b·8·12a·13 kapı testleri (+ inceleme bulguları B1·B2·B3·B6).

⚠️ Bu dosya KIRMIZI doğdu (Adım 1: üretim kodu henüz değişmemişti) ve artık KAPANIŞ hâlini
anlatır: kusurlar kapatıldı, testler YEŞİL ve bundan sonra REGRESYON KAPISIdır — biri
kapanan bir kusuru geri getirirse burası kırmızıya döner. Kırmızı hâlin kaydı commit
mesajlarındadır (`d75b5c5` ve inceleme düzeltme turu). İki test grubu hiç kırmızı olmadı ve
bilerek öyle: "ölçüm hattı dokunulmazlık kapısı" (henüz kırılmamış bir şeyi ÇİVİLİYOR) ve
"kısa-ama-dolu sorgu reddedilmiyor" (uydurulmuş bir eşik EKLENMEDİĞİNİ garanti eden muhafız).

Hiçbir test retriever/llama-server/korpus yüklemez — monkeypatch ve sahte nesne kullanılır.
"""
import importlib
import inspect
import json
import pathlib
import re
import shutil
import sys

import pytest

from hakhukuk.arayuz import cli, tui
from hakhukuk.cekirdek import servis, tipler
from hakhukuk.cekirdek.tipler import Cevap, Durum, Kaynak

REPO_KOK = pathlib.Path(__file__).resolve().parent.parent

IS_K_31 = Kaynak(kanun_adi="İŞ KANUNU", kanun_no="4857", madde_no="Madde 31",
                 metin="Muvazzaf askerlik ödevi dışında …", sira=1)


# ── kusur 4 — boş sorgu KAPISI `servis.answer`/`servis.answer_arac`'a konur ──────────

def _patlayan_getir():
    """`_getir` çağrılırsa test'i düşürecek sahte — boş sorgu KAPI'yı geçmemeli."""
    cagrildi = []

    def getir(soru, k):
        cagrildi.append(soru)
        raise AssertionError(f"boş/boşluk sorgu ({soru!r}) _getir'e ULAŞTI")
    return getir, cagrildi


def test_answer_bos_sorgu_getire_ulasmiyor(monkeypatch):
    getir, cagrildi = _patlayan_getir()
    monkeypatch.setattr(servis, "_getir", getir)
    c = servis.answer("")
    assert not cagrildi, "boş sorgu _getir'e ulaştı"
    assert isinstance(c, Cevap) and c.metin.strip(), "boş sorguda okunur bir mesaj yok"


def test_answer_bosluk_sorgu_getire_ulasmiyor(monkeypatch):
    getir, cagrildi = _patlayan_getir()
    monkeypatch.setattr(servis, "_getir", getir)
    c = servis.answer("   ")
    assert not cagrildi, "yalnız boşluktan ibaret sorgu _getir'e ulaştı"
    assert isinstance(c, Cevap) and c.metin.strip(), "boşluk sorgusunda okunur bir mesaj yok"


def test_answer_arac_bos_sorgu_getire_ulasmiyor(monkeypatch):
    """`answer_arac` aynı kapıdan geçmeli — ayrı yol, ayrı savunmasızlık olmasın."""
    getir, cagrildi = _patlayan_getir()
    monkeypatch.setattr(servis, "_getir", getir)
    # araclar= verilmeden çağrılırsa _varsayilan_araclar() ağır korpusu yükler; kapı
    # _getir'den ÖNCE tetiklenmeliyse zaten oraya hiç gerek kalmaz, ama testi ağır
    # bağımlılıktan bağımsız tutmak için sahte bir nesne veriyoruz.
    c = servis.answer_arac("   ", araclar=object())
    assert not cagrildi, "boşluk sorgu answer_arac üzerinden _getir'e ulaştı"
    assert isinstance(c, Cevap) and c.metin.strip(), "answer_arac boşluk sorgusunda okunur mesaj yok"


def test_answer_kisa_dolu_sorgu_reddedilmiyor(monkeypatch):
    """Uydurulmuş uzunluk eşiği YOK: "kira?" gibi kısa ama dolu bir soru _getir'e ulaşmalı.

    Bu, kapı henüz eklenmeden de bugün zaten doğru (muhafız testi) — kapı eklendikten
    sonra da BOZULMAMASI gereken davranış budur.
    """
    cagrildi = []
    monkeypatch.setattr(servis, "_getir", lambda soru, k: cagrildi.append(soru) or ())
    servis.answer("kira?")
    assert cagrildi == ["kira?"], "kısa ama dolu bir soru _getir'e ulaşmadı — uydurulmuş eşik var"


# ── kusur 12a — `bicimle()`'de iskele işareti süzgeci; `Cevap.metin` HAM kalır ───────

def test_bicimle_iskele_isaretlerini_temizler_alinti_metni_kalir():
    ham = "Bu konuda ##begin_quote##ilgili kanun hükmü##end_quote## uygulanır."
    c = Cevap(metin=ham, durum=Durum.CEVAP, atiflar=(), kaynaklar=())
    sunum = cli.bicimle(c)
    assert "##begin_quote##" not in sunum, "sunumda iskele işareti kaldı"
    assert "##end_quote##" not in sunum, "sunumda iskele işareti kaldı"
    assert "ilgili kanun hükmü" in sunum, "işaretlerle birlikte alıntı metni de silindi"


def test_cevap_metin_ham_alan_isaretleri_koruyor():
    """`Cevap.metin` modelin ham çıktısıdır — `bicimle()` onu MUTASYONA UĞRATMAZ."""
    ham = "Bu konuda ##begin_quote##ilgili kanun hükmü##end_quote## uygulanır."
    c = Cevap(metin=ham, durum=Durum.CEVAP, atiflar=(), kaynaklar=())
    cli.bicimle(c)  # yan etkisi olmamalı
    assert c.metin == ham, "Cevap.metin bicimle() çağrısından sonra değişti — ham kayıt bozuldu"


# ── ölçüm hattı DOKUNULMAZLIK KAPISI — kusur 12a'nın çözümü scripts/'e SIZMAMALI ─────

def test_score_register_begin_quote_deseni_yerinde_duruyor():
    """`##begin_quote##` `score_register.py`'de register göstergesi olarak SAYILIYOR
    (CLAUDE.md karar 2). Bu desen silinirse register ölçümü bozulur."""
    dosya = REPO_KOK / "scripts" / "puanlama" / "score_register.py"
    icerik = dosya.read_text(encoding="utf-8")
    assert "##begin_quote##" in icerik, (
        "score_register.py'deki begin_quote deseni kayboldu — register ölçümü bozulur")


def test_scripts_altinda_begin_quote_temizleme_suzgeci_yok():
    """kusur 12a'nın süzgeci YALNIZ `cli.bicimle()`'de olmalı; `scripts/` ölçüm hattına
    hiçbir zaman bir begin_quote/end_quote STRIP işlemi sızmamalı."""
    desen = re.compile(
        r'(replace|sub)\(\s*[rRuU]?["\'][^"\']*(begin_quote|end_quote)[^"\']*["\']\s*,\s*'
        r'[rRuU]?["\']{2}', re.IGNORECASE)
    supheli = []
    for dosya in (REPO_KOK / "scripts").rglob("*.py"):
        icerik = dosya.read_text(encoding="utf-8")
        if desen.search(icerik):
            supheli.append(str(dosya.relative_to(REPO_KOK)))
    assert not supheli, f"scripts/ altında begin_quote SÜZGECİ bulundu: {supheli}"


# ── kusur 3 — TUI: `answer()` olay döngüsünde DOĞRUDAN çağrılmıyor ───────────────────

def test_tui_answer_dogrudan_olay_dongusunde_cagrilmiyor():
    """`on_input_submitted` senkron olay döngüsü metodudur; içinde `answer(` doğrudan
    çağrılırsa ağ + retriever I/O arayüzü DONDURUR."""
    kaynak = inspect.getsource(tui.HakHukukTUI.on_input_submitted)
    assert "answer(" not in kaynak, (
        "answer() doğrudan on_input_submitted içinde çağrılıyor — arayüz donar")


def test_tui_answer_calisan_ipliginde_calistiriliyor():
    """answer() bir yerde `@work(thread=True)` ya da `run_worker(..., thread=True)` ile
    çalışan iş parçacığına alınmış olmalı."""
    tum_kaynak = inspect.getsource(tui)
    assert "answer(" in tum_kaynak, "answer() TUI'den tamamen kayboldu"
    isaretli = ("@work(thread=True)" in tum_kaynak
               or ("run_worker(" in tum_kaynak and "thread=True" in tum_kaynak))
    assert isaretli, "answer() çalışan iş parçacığına (worker) alınmamış"


# ── kusur 8 + 5b — açılış yönergesi + STATİK kapsam satırı (KUNYE.json'dan okunur) ───

def test_tui_kapsam_satiri_kunyeden_sayilari_okuyor():
    """Sayılar `data/corpus/KUNYE.json`'dan okunmalı, koda gömülmemeli."""
    kunye = json.loads((REPO_KOK / "data/corpus/KUNYE.json").read_text(encoding="utf-8"))
    satir = tui.kapsam_satiri()
    assert isinstance(satir, str) and satir.strip()
    n_kanun, n_madde = kunye["n_kanun"], kunye["n_madde"]
    n_madde_bicimli = f"{n_madde:,}".replace(",", ".")
    assert str(n_kanun) in satir, "kapsam satırında kanun sayısı yok"
    assert str(n_madde) in satir or n_madde_bicimli in satir, "kapsam satırında madde sayısı yok"
    for kapsam_disi in ("yönetmelik", "tüzük", "khk", "tebliğ"):
        assert kapsam_disi in satir.lower(), f"kapsam dışı tür anılmıyor: {kapsam_disi}"


def test_tui_kapsam_satiri_sayilari_koda_gommez():
    """Kod, KUNYE.json'daki güncel sayıları OKUMALI — kendi kopyasını GÖMMEMELİ."""
    kaynak = inspect.getsource(tui)
    kunye = json.loads((REPO_KOK / "data/corpus/KUNYE.json").read_text(encoding="utf-8"))
    n_madde_bicimli = f"{kunye['n_madde']:,}".replace(",", ".")
    assert str(kunye["n_kanun"]) not in kaynak, "kanun sayısı koda gömülmüş"
    assert str(kunye["n_madde"]) not in kaynak and n_madde_bicimli not in kaynak, (
        "madde sayısı koda gömülmüş")


def test_tui_acilis_ekrani_yonerge_ve_kapsam_satirini_gosteriyor():
    """Açılış ekranı BOŞ değil: `compose()` hem yönerge hem statik kapsam satırını
    üretmeli. Sınıflandırıcı YOK — kapsam her zaman aynı statik satırdır (karar 3)."""
    kaynak = inspect.getsource(tui.HakHukukTUI.compose)
    assert "kapsam_satiri(" in kaynak, "açılış ekranı statik kapsam satırını göstermiyor"


# ── kusur: TUI sunumu `c.metin`'i HAM basıyor — iskele işareti vatandaşa gidiyor ─────

def test_tui_suzgeci_cli_ile_AYNI_nesne():
    """`tui.py` sunumu `cli.py`'den İMPORT etmeli, KOPYALAMAMALI (S18'in dersi:
    `SORUMLULUK_IBARESI` bu deponun yerleşik emsalidir — `is` ile sınanır).

    ⚠️ Test 2026-09-11'de GÜNCELLENDİ (silinmedi): kusur 17 kapatılınca TUI artık tek
    tek süzgeç import etmiyor, SUNUMUN TAMAMINI import ediyor. Sınanan şart aynı, yalnız
    daha güçlü — tek bir `is` bütün sunum katmanının ortaklığını çiviliyor.
    """
    assert tui.bicimle is cli.bicimle, (
        "tui'nin sunumu cli'dekiyle AYNI nesne değil — kopyalanmış olabilir")


def test_tui_sunum_dizesinde_iskele_isareti_yok(monkeypatch):
    """TUI sunumu `cli.bicimle()`'den geldiği için ##begin_quote##/##end_quote##
    vatandaşa GİTMEZ — bu test o yolu kapalı tutar (2026-09-11 öncesi TUI kendi dizesini
    kuruyordu ve süzgeci yalnız AYRICA import ettiği için geçiyordu; kusur 17).
    `servis.answer` sahtelenir; llama-server/indeks GEREKMEZ."""
    import asyncio

    from textual.widgets import Static

    ham = "Bu konuda ##begin_quote##ilgili kanun hükmü##end_quote## uygulanır."
    sahte_cevap = Cevap(metin=ham, durum=Durum.CEVAP, atiflar=(), kaynaklar=())
    monkeypatch.setattr(tui, "answer", lambda soru: sahte_cevap)

    async def _calistir() -> str:
        app = tui.HakHukukTUI()
        async with app.run_test() as pilot:
            await pilot.click("#soru")
            await pilot.press(*"soru", "enter")
            await app.workers.wait_for_complete()
            await pilot.pause()
            return str(app.query_one("#cikti", Static).content)

    cikti = asyncio.run(_calistir())
    assert "##begin_quote##" not in cikti, "TUI sunumunda iskele işareti kaldı"
    assert "##end_quote##" not in cikti, "TUI sunumunda iskele işareti kaldı"
    assert "ilgili kanun hükmü" in cikti, "işaretlerle birlikte alıntı metni de silindi"


# ══ inceleme bulguları (kod incelemesi, 2026-09-11) ══════════════════════════════════

# ── B1 — TUI'de eşzamanlı iki çalışan: "son biten kazanır" ekranda YANLIŞ eşleşme üretir ─

def test_tui_kosu_surerken_ikinci_sorgu_calisan_baslatmiyor(monkeypatch):
    """İki ardışık Enter → İKİ çalışan; yavaş biten 1. soruysa ekranda 2. sorunun altında
    1. sorunun cevabı görünür ve hiçbir hata çıkmaz ("hata vermeden yanlış").

    Kapatma: koşu sürerken girdi DEVRE DIŞI + çalışan `exclusive`.
    """
    import threading

    kapi = threading.Event()
    cagrilar = []

    def yavas_answer(soru):
        cagrilar.append(soru)
        kapi.wait(timeout=5)
        return Cevap(metin=f"cevap:{soru}", durum=Durum.CEVAP, atiflar=(), kaynaklar=())

    import asyncio

    from textual.widgets import Input, Static

    monkeypatch.setattr(tui, "answer", yavas_answer)

    async def _calistir():
        app = tui.HakHukukTUI()
        async with app.run_test() as pilot:
            await pilot.click("#soru")
            await pilot.press(*"bir", "enter")
            await pilot.pause()
            await pilot.press(*"iki", "enter")   # koşu SÜRERKEN — yok sayılmalı
            await pilot.pause()
            kapi.set()
            await app.workers.wait_for_complete()
            await pilot.pause()
            return (str(app.query_one("#cikti", Static).content),
                    app.query_one("#soru", Input).disabled)

    try:
        cikti, girdi_kapali = asyncio.run(_calistir())
    finally:
        kapi.set()

    assert cagrilar == ["bir"], (
        f"koşu sürerken ikinci sorgu da başladı — iki çalışan yarışıyor: {cagrilar}")
    assert "cevap:bir" in cikti, "ekranda koşan sorunun cevabı yok"
    assert not girdi_kapali, "koşu bitti ama girdi kapalı kaldı — arayüz kilitli"


def test_tui_hata_yolunda_girdi_tekrar_aciliyor(monkeypatch):
    """`answer()` patlarsa girdi AÇILMALI — yoksa llama-server kapalıyken arayüz
    tek bir hatadan sonra kalıcı olarak kilitlenir."""
    import asyncio

    from textual.widgets import Input

    def patlayan_answer(soru):
        raise RuntimeError("llama-server kapalı")

    monkeypatch.setattr(tui, "answer", patlayan_answer)

    async def _calistir():
        app = tui.HakHukukTUI()
        async with app.run_test() as pilot:
            await pilot.click("#soru")
            await pilot.press(*"soru", "enter")
            await app.workers.wait_for_complete()
            await pilot.pause()
            return app.query_one("#soru", Input).disabled

    assert not asyncio.run(_calistir()), "hata yolunda girdi kapalı kaldı"


# ── B2 — kapsam satırı MÜLGA maddeleri "yürürlükteki" saymamalı ──────────────────────

def test_kapsam_satiri_mulgayi_duserek_yururlukteki_madde_sayisini_veriyor(monkeypatch, tmp_path):
    """`n_madde` TOPLAMdır; retriever varsayılanı mülgayı eler ⇒ vatandaşa gösterilecek
    sayı `n_madde - n_mulga`. Sayı künyeden TÜRETİLİR, koda gömülmez (sahte künye)."""
    sahte = tmp_path / "KUNYE.json"
    sahte.write_text(json.dumps(
        {"n_kanun": 3, "n_madde": 100, "n_mulga": 40, "anlik_goruntu_tarihi": "2026-01-01"}),
        encoding="utf-8")
    monkeypatch.setattr(cli, "_KUNYE_YOLU", sahte)
    satir = cli.kapsam_satiri()
    assert "yürürlükteki 60 madde" in satir, (
        f"yürürlükteki madde sayısı mülga düşülerek verilmiyor: {satir!r}")


def test_kapsam_satiri_tek_kaynak_tui_cli_ile_AYNI_nesne():
    """B4: metin `cli.py`'de tanımlı, `tui.py` IMPORT eder (SORUMLULUK_IBARESI emsali)."""
    assert tui.kapsam_satiri is cli.kapsam_satiri, (
        "tui'nin kapsam satırı cli'dekiyle AYNI nesne değil — kopyalanmış olabilir")


# ── B6 — alıntı iskelesi SİLİNMEZ, tipografik tırnağa ÇEVRİLİR ───────────────────────

def test_alinti_isaretleri_tipografik_tirnaga_ceviriliyor():
    """İşaretin TAŞIDIĞI bilgi "burası kanunun kendi cümlesidir" sınırıdır; silinirse
    birebir kanun metni ile modelin yorumu ayırt edilemez hâle gelir."""
    sunum = cli.alinti_isaretlerini_tirnaga_cevir(
        "Kanun der ki: ##begin_quote##İşçi kıdem tazminatına hak kazanır.##end_quote## Ancak…")
    assert "“İşçi kıdem tazminatına hak kazanır.”" in sunum, f"alıntı sınırı kayboldu: {sunum!r}"
    assert "##" not in sunum, "iskele işareti sunuma sızdı"


def test_eslesmeyen_tek_alinti_isareti_siliniyor():
    """Eşleşmeyen tek işaret (model kapatmayı unutmuş) tırnak AÇMAZ — silinir."""
    sunum = cli.alinti_isaretlerini_tirnaga_cevir("Kanun der ki: ##begin_quote##İşçi …")
    assert "##" not in sunum, "eşleşmeyen iskele işareti sunumda kaldı"
    assert "İşçi" in sunum, "işaretle birlikte metin de silindi"
    assert "“" not in sunum and "”" not in sunum, "eşleşmeyen işaret için tırnak açıldı"


def test_alinti_cevirisi_ham_metni_bozmuyor():
    ham = "Bu konuda ##begin_quote##ilgili kanun hükmü##end_quote## uygulanır."
    c = Cevap(metin=ham, durum=Durum.CEVAP, atiflar=(), kaynaklar=())
    cli.bicimle(c)
    assert c.metin == ham, "Cevap.metin sunum çevirisinden sonra değişti — ham kayıt bozuldu"


# ══ İKİNCİ TUR (2026-09-11) — kusur 17 · 15 · 19 · 16 · 14 · 20 ══════════════════════
#
# ⚠️ Turun kök nedeni kusur **17**: `tui.py` `cli.bicimle()`'yi ÇAĞIRMIYOR, kendi sunum
# dizesini kuruyordu. Birinci turda kapatılan iki sızıntının (`##begin_quote##` ve kapsam
# satırı) ikisi de TUI'de AYRI AYRI unutuldu. S18'in ölçülmüş dersi: aynı metin iki yerde
# durursa sessizce ayrışır — bu turda İKİ KEZ ayrıştı. Bu yüzden 17 önce kapatılır;
# 15 · 19 · 16 onun üstüne oturur ve tek yerden ÜÇ yüzeye birden iner.

def _tui_ekran_metni(monkeypatch, cevap) -> str:
    """TUI'yi BAŞSIZ kipte gerçekten açar, sahte `answer` ile bir soru sorar, ekranı verir.

    ⛔ Kaynak denetimi YETMEZ: `python -m hakhukuk.arayuz.tui` bir kez hiç açılmıyordu ve 163 test
    bunu görmedi (2026-09-09). Sunum birliği ancak ÇALIŞAN programdan okunarak sınanır.
    """
    import asyncio

    from textual.widgets import Static

    monkeypatch.setattr(tui, "answer", lambda soru: cevap)

    async def _calistir() -> str:
        app = tui.HakHukukTUI()
        async with app.run_test() as pilot:
            await pilot.click("#soru")
            await pilot.press(*"soru", "enter")
            await app.workers.wait_for_complete()
            await pilot.pause()
            return str(app.query_one("#cikti", Static).content)

    return asyncio.run(_calistir())


def _ornek_cevap() -> Cevap:
    return Cevap(
        metin="İş Kanunu Madde 31 uyarınca sözleşme askıya alınır.",
        durum=Durum.CEVAP,
        atiflar=(tipler.Atif(kanun_no="4857", madde_no="Madde 31", dogrulandi=True),
                 tipler.Atif(kanun_no="", madde_no="Madde 99", dogrulandi=False)),
        kaynaklar=(IS_K_31,))


def test_tui_sunumu_bicimle_ciktisiyla_BIREBIR_AYNI(monkeypatch):
    """kusur 17: TEK sunum katmanı. Tek meşru fark ROZET sözlüğüdür, o da PARAMETREdir."""
    c = _ornek_cevap()
    assert _tui_ekran_metni(monkeypatch, c) == cli.bicimle(c, rozet=tui.ROZET), (
        "TUI kendi sunum dizesini kuruyor — iki sunum katmanı sessizce ayrışır (S18)")


def test_bicimleye_eklenen_yeni_parca_TUIde_KENDILIGINDEN_gorunuyor(monkeypatch):
    """Kusur 17'nin ASIL şartı: `bicimle()` büyüyünce TUI'nin DEĞİŞMESİ gerekmemeli.

    Birinci turda tam bu şart yoktu: `bicimle()`'ye iskele süzgeci ve kapsam satırı
    eklendi, TUI ikisini de almadı ve ikisi de vatandaşa kusurlu gitti.
    """
    monkeypatch.setattr(tui, "bicimle", lambda cevap, rozet=None: "YENİ_PARÇA_İŞARETİ")
    assert "YENİ_PARÇA_İŞARETİ" in _tui_ekran_metni(monkeypatch, _ornek_cevap()), (
        "TUI `bicimle()`'yi çağırmıyor — sunuma eklenen her parça TUI'de ayrıca unutulur")


# ── kusur 15 — kapsam satırı ÜÇ yüzeyde: CLI · TUI · HTTP ────────────────────────────
#
# İnsan kararı 2026-09-11: *"CLI ve HTTP'ye de EKLE"*. Tek kaynak `cli.kapsam_satiri()`
# zaten vardı ama yalnız TUI AÇILIŞ ekranında görünüyordu; cevabın kendisiyle birlikte
# hiçbir yüzeyde gitmiyordu. Kusur 17 kapandığı için tek yere (`bicimle()`) eklemek
# üçünü birden kapatır — bu, 17'yi önce yapmanın ölçülebilir karşılığıdır.

def _sahte_kunye(monkeypatch, tmp_path, *, n_kanun=3, n_madde=100, n_mulga=40):
    sahte = tmp_path / "KUNYE.json"
    sahte.write_text(json.dumps({"n_kanun": n_kanun, "n_madde": n_madde,
                                 "n_mulga": n_mulga,
                                 "anlik_goruntu_tarihi": "2026-01-01"}), encoding="utf-8")
    monkeypatch.setattr(cli, "_KUNYE_YOLU", sahte)
    return "yürürlükteki 60 madde"


def _http_sunum(monkeypatch, cevap) -> str:
    from fastapi.testclient import TestClient

    from hakhukuk.arayuz import api
    monkeypatch.setattr(api.servis, "answer", lambda soru, **kw: cevap)
    g = TestClient(api.uygulama).post("/sor", json={"soru": "zamanaşımı kaç yıl"})
    assert g.status_code == 200, g.text
    return g.json()["sunum"]


def test_kapsam_satiri_CLI_ciktisinda_gorunuyor(monkeypatch, tmp_path):
    beklenen = _sahte_kunye(monkeypatch, tmp_path)
    assert beklenen in cli.bicimle(_ornek_cevap()), "kapsam satırı CLI çıktısında yok"


def test_kapsam_satiri_TUI_cevabinda_gorunuyor(monkeypatch, tmp_path):
    beklenen = _sahte_kunye(monkeypatch, tmp_path)
    assert beklenen in _tui_ekran_metni(monkeypatch, _ornek_cevap()), (
        "kapsam satırı TUI cevabında yok")


def test_kapsam_satiri_HTTP_sunum_alaninda_gorunuyor(monkeypatch, tmp_path):
    beklenen = _sahte_kunye(monkeypatch, tmp_path)
    assert beklenen in _http_sunum(monkeypatch, _ornek_cevap()), (
        "kapsam satırı HTTP `sunum` alanında yok")


def test_kapsam_satiri_uc_yuzeyde_de_KUNYEDEN_geliyor(monkeypatch, tmp_path):
    """⛔ Sayılar koda GÖMÜLMEZ: künye değişince üç yüzey de değişmeli.

    Aynı sahte künyeyle üç yüzey sınanır; biri sabit metin taşısaydı burada ayrışırdı.
    """
    _sahte_kunye(monkeypatch, tmp_path, n_kanun=7, n_madde=200, n_mulga=50)
    c = _ornek_cevap()
    for ad, metin in (("CLI", cli.bicimle(c)),
                      ("TUI", _tui_ekran_metni(monkeypatch, c)),
                      ("HTTP", _http_sunum(monkeypatch, c))):
        assert "yürürlükteki 150 madde" in metin, f"{ad} kapsam satırı künyeyi okumuyor"
        assert "7 kanun" in metin, f"{ad} kapsam satırı künyedeki kanun sayısını okumuyor"


def test_sorumluluk_ibaresi_SON_satir_kalir(monkeypatch, tmp_path):
    """Kapsam satırı ibarenin ÜSTÜNE girer: kapsam bir olgu şerhi, ibare hukuki uyarıdır
    ve çıktının EN GÜÇLÜ cümlesi son satır olarak kalmalıdır."""
    _sahte_kunye(monkeypatch, tmp_path)
    assert cli.bicimle(_ornek_cevap()).rstrip().endswith(cli.SORUMLULUK_IBARESI)


# ── kusur 19 — istem YER TUTUCUSU sızıntısı sunumda süzülür ──────────────────────────
#
# Ölçüldü 2026-09-11 (G22 Adım 1, fp16 koşusu): model istemin kendi yer tutucusunu
# harfiyen bastı — `(KANUN ADI, Madde 13)` — `0/80 ↔ 2/80` (id 23 · 36),
# `outputs/eval/gorev/g22-kv-fp16/KARSILASTIRMA.md`. Çıpa rejiminde yok; rejime bağlı bozulma.
# İnsan kararı 2026-09-11: KAPATILSIN, sunum katmanında (kusur 12a'nın yanında).

def test_yer_tutucu_sunumda_HARFIYEN_gorunmuyor():
    ham = "Bu durumda (KANUN ADI, Madde 13) uygulanır."
    c = Cevap(metin=ham, durum=Durum.CEVAP, atiflar=(), kaynaklar=())
    sunum = cli.bicimle(c)
    assert "KANUN ADI" not in sunum, "istem yer tutucusu vatandaşa gitti"


def test_yer_tutucu_MADDE_NUMARASINI_korur_ve_eksigi_DURUSTCE_soyler():
    """⛔ Vatandaşa yalan söyleme: parantezi silmek, modelin ürettiği GERÇEK bilgiyi
    (madde numarası) yok ederdi; `KANUN ADI`'nı olduğu gibi bırakmak ise onu bir kanun
    ADI gibi gösterirdi. Dürüst orta yol: numara kalır, eksiklik AÇIKÇA yazılır."""
    sunum = cli.bicimle(Cevap(metin="Bu durumda (KANUN ADI, Madde 13) uygulanır.",
                              durum=Durum.CEVAP, atiflar=(), kaynaklar=()))
    assert "(kanun adı belirtilmemiş, Madde 13)" in sunum, sunum


def test_gercek_atiflar_BOZULMUYOR():
    """Muhafız: süzgeç yalnız yer tutucuya dokunur; gerçek atıf aynen kalır."""
    ham = "Kira artışı (Türk Borçlar Kanunu, Madde 344) ile sınırlıdır."
    sunum = cli.bicimle(Cevap(metin=ham, durum=Durum.CEVAP, atiflar=(), kaynaklar=()))
    assert "(Türk Borçlar Kanunu, Madde 344)" in sunum, "gerçek atıf bozuldu"


def test_yer_tutucu_suzgeci_HAM_metni_bozmuyor():
    """⛔ `Cevap.metin` modelin ham çıktısıdır — ölçüm hattı onu sayıyor, DEĞİŞTİRİLEMEZ."""
    ham = "Bu durumda (KANUN ADI, Madde 13) uygulanır."
    c = Cevap(metin=ham, durum=Durum.CEVAP, atiflar=(), kaynaklar=())
    cli.bicimle(c)
    assert c.metin == ham, "ham kayıt sunum süzgecinden sonra değişti"


def test_yer_tutucu_suzgeci_UC_YUZEYDE_de_calisiyor(monkeypatch):
    """Kusur 17'nin karşılığı: süzgeç tek yere kondu, üç yüzey de aldı."""
    c = Cevap(metin="Bu durumda (KANUN ADI, Madde 13) uygulanır.",
              durum=Durum.CEVAP, atiflar=(), kaynaklar=())
    for ad, metin in (("CLI", cli.bicimle(c)),
                      ("TUI", _tui_ekran_metni(monkeypatch, c)),
                      ("HTTP", _http_sunum(monkeypatch, c))):
        assert "KANUN ADI" not in metin, f"{ad} yüzeyinde yer tutucu kaldı"


# ── kusur 16 — ALTINCI `Durum`: boş sorgu ≠ kaynakta karşılık yok ────────────────────
#
# İnsan kararı 2026-09-11: ALTINCI `Durum` EKLENSİN (tip düzeyi değişiklik ⇒ ADR-0081).
# Kusur: boş sorgu `Durum.SUSKUNLUK` dönüyordu; rozet "kaynaklarda karşılık bulunamadı"
# (aradım, bulamadım) derken gövde "soru boş" diyordu — oysa o dalda hiç ARAMA YAPILMADI.
# `tipler.py`'nin kendi başlığının yasakladığı birleştirme: dedektör ÜÇ kez yanıldı çünkü
# dünya ikili değil; iki FARKLI hâli tek değere indirmek tam o hatanın sınıfıdır.

def test_bos_sorgu_SUSKUNLUK_degil_BOS_SORGU_doner(monkeypatch):
    getir, _ = _patlayan_getir()
    monkeypatch.setattr(servis, "_getir", getir)
    for sorgu in ("", "   ", "\t\n"):
        c = servis.answer(sorgu)
        assert c.durum is Durum.BOS_SORGU, f"{sorgu!r} → {c.durum}"
        assert c.durum is not Durum.SUSKUNLUK, "boş sorgu suskunluk sayımını kirletiyor"


def test_answer_arac_da_BOS_SORGU_doner(monkeypatch):
    getir, _ = _patlayan_getir()
    monkeypatch.setattr(servis, "_getir", getir)
    assert servis.answer_arac("   ", araclar=object()).durum is Durum.BOS_SORGU


def test_gercek_suskunluk_hala_SUSKUNLUK(monkeypatch):
    """Muhafız: kaynak bulunamadığında hâlâ SUSKUNLUK — altıncı değer onu YUTMAZ."""
    monkeypatch.setattr(servis, "_getir", lambda soru, k: ())
    assert servis.answer("ilgisiz soru").durum is Durum.SUSKUNLUK


def test_terazi_BOS_SORGU_URETMEZ():
    """⛔ Kapı `answer()`'da, TERAZİDEN ÖNCE. Terazi bir MODEL ÇIKTISINI sınıflandırır;
    boş sorgu diye bir model çıktısı yoktur. Bu değeri terazinin üretebilmesi, ölçüm
    hattına sızabileceği anlamına gelirdi — ölçüm hattı `siniflandir`'ı kullanır."""
    from hakhukuk.cekirdek import terazi
    kaynak = inspect.getsource(terazi)
    assert "BOS_SORGU" not in kaynak, "altıncı durum terazi katmanına sızmış"
    for metin, kaynaklar, finish in (("", (), "stop"), ("   ", (IS_K_31,), "stop"),
                                     ("cevap", (IS_K_31,), "length")):
        durum, _ = terazi.siniflandir(metin, kaynaklar, finish)
        assert durum is not Durum.BOS_SORGU, "terazi BOS_SORGU üretti"


def test_iki_ROZET_sozlugu_de_ALTI_durumu_tasiyor():
    """`bicimle()` rozeti sözlükten okur: eksik değer `KeyError` ile ÜRÜNÜ düşürür."""
    for ad, sozluk in (("cli", cli.ROZET), ("tui", tui.ROZET)):
        eksik = [d.name for d in Durum if d not in sozluk]
        assert not eksik, f"{ad}.ROZET eksik: {eksik}"


def test_BOS_SORGU_rozeti_ARAMA_YAPILMADIGINI_soyluyor():
    """Kusurun ta kendisi buydu: rozet "kaynaklarda karşılık bulunamadı" diyordu."""
    for ad, sozluk in (("cli", cli.ROZET), ("tui", tui.ROZET)):
        rozet = sozluk[Durum.BOS_SORGU].lower()
        assert "boş" in rozet, f"{ad}.ROZET boş sorguyu adıyla anmıyor"
        assert "bulunamadı" not in rozet, (
            f"{ad}.ROZET hâlâ 'bulunamadı' diyor — o dalda arama YAPILMADI")


def test_HTTP_yuzeyi_BOS_SORGUyu_hic_URETMEZ(monkeypatch):
    """422 kapısı `answer()`'dan ÖNCE durur ⇒ bu değer HTTP'de görünmez. Bir tüketici
    `durum == "bos_sorgu"` diye dal yazarsa o dal ÖLÜ olur; şema büyümedi."""
    from fastapi.testclient import TestClient

    from hakhukuk.arayuz import api
    monkeypatch.setattr(api.servis, "answer",
                        lambda soru, **kw: pytest.fail("boş sorgu answer()'a ULAŞTI"))
    assert TestClient(api.uygulama).post("/sor", json={"soru": "   "}).status_code == 422


# ══ DÖRDÜNCÜ TUR (2026-09-11) — insan gözü kapısı: ÇİFT TIRNAK + KAÇAK BOŞLUK ════════
#
# Kusur GERÇEK ekranda görüldü: model çoğu zaman ##begin_quote##…##end_quote##
# işaretlerinin İÇİNE kendi düz tırnağını (") da yazıyor. `alinti_isaretlerini_tirnaga_
# cevir` bunu SOYMADAN üstüne bir tırnak daha sarıyordu ⇒ çift tırnak + kaçak boşluk.
# Testler tırnaksız alıntıyla yazılmıştı (bkz. B6 testleri yukarıda) ve bu hâli hiç
# görmemişti — kapıyı insan gözü yakaladı, otomatik test değil.

_GERCEK_EKRAN_GIRDISI = (
    '2) ##begin_quote## "Taraflardan her biri, üç gün önceden feshedebilir." '
    '##end_quote##')
_GERCEK_EKRAN_BEKLENEN = '2) “Taraflardan her biri, üç gün önceden feshedebilir.”'


def test_duz_tirnakli_alinti_tek_tirnaga_iner_boslukla_birlikte():
    """Model işaretin İÇİNE kendi düz tırnağını da yazmış — çift tırnak + kaçak boşluk
    OLUŞMAMALI. Gerçek ekranda görülen girdi (2026-09-11) birebir kullanılıyor."""
    sunum = cli.alinti_isaretlerini_tirnaga_cevir(_GERCEK_EKRAN_GIRDISI)
    assert sunum == _GERCEK_EKRAN_BEKLENEN, f"çift tırnak/kaçak boşluk kaldı: {sunum!r}"
    assert '"' not in sunum, "düz tırnak sunuma sızdı"


def test_tirnaksiz_alinti_davranisi_bugunku_gibi_korunuyor():
    """Tırnaksız içerik bugün zaten DOĞRU çalışıyor — düzeltme bunu BOZMAMALI."""
    sunum = cli.alinti_isaretlerini_tirnaga_cevir(
        "2) ##begin_quote##Tırnaksız alıntı metni##end_quote##")
    assert sunum == "2) “Tırnaksız alıntı metni”", f"tırnaksız davranış bozuldu: {sunum!r}"


def test_alinti_ortasindaki_duz_tirnak_silinmiyor_yalniz_saran_cift_bozuluyor():
    """Yalnız SARAN çift tırnak soyulur; içerikte ORTADA geçen düz tırnak (bir iç
    alıntı) SİLİNMEZ."""
    sunum = cli.alinti_isaretlerini_tirnaga_cevir(
        '##begin_quote##Sözleşme "makul süre" içinde feshedilir.##end_quote##')
    assert sunum == '“Sözleşme "makul süre" içinde feshedilir.”', (
        f"ortadaki iç alıntı yanlış değiştirildi: {sunum!r}")


def test_eslesmeyen_tek_alinti_isareti_hala_siliniyor_duz_tirnakli_icerikte_de():
    """Kapanışı olmayan işaret düz tırnaklı içerikte de SİLİNMELİ — tırnak açmaz."""
    sunum = cli.alinti_isaretlerini_tirnaga_cevir('Kanun der ki: ##begin_quote## "İşçi …')
    assert "##" not in sunum, "eşleşmeyen iskele işareti sunumda kaldı"
    assert "“" not in sunum and "”" not in sunum, "eşleşmeyen işaret için tırnak açıldı"


def test_alinti_cevirisi_duz_tirnakli_girdide_de_ham_metni_bozmuyor():
    """`Cevap.metin` bu durumda da HAM kalmalı — fonksiyon saf, yan etkisiz."""
    ham = _GERCEK_EKRAN_GIRDISI
    c = Cevap(metin=ham, durum=Durum.CEVAP, atiflar=(), kaynaklar=())
    cli.bicimle(c)
    assert c.metin == ham, "Cevap.metin düz tırnaklı girdide de değişmemeli"


def test_duz_tirnakli_alinti_uc_yuzeyde_de_tek_tirnaga_iniyor(monkeypatch):
    """Kusur 17 emsali: düzeltme CLI · TUI · HTTP üçünde de KENDİLİĞİNDEN görünmeli —
    üçü de `cli.bicimle()` üzerinden aynı süzgeci kullanır."""
    c = Cevap(metin=_GERCEK_EKRAN_GIRDISI, durum=Durum.CEVAP, atiflar=(), kaynaklar=())
    for ad, metin in (("CLI", cli.bicimle(c)),
                      ("TUI", _tui_ekran_metni(monkeypatch, c)),
                      ("HTTP", _http_sunum(monkeypatch, c))):
        assert _GERCEK_EKRAN_BEKLENEN in metin, f"{ad} yüzeyinde çift tırnak/boşluk kaldı"
        assert '"' not in metin, f"{ad} yüzeyinde düz tırnak sızdı"


# ── kusur B (g20 imaj ölçümü) — künye yolu KONTEYNERDE bulunamıyor, sessiz düşüş ────
#
# `_KUNYE_YOLU` repo köküne GÖRELİ çözülüyordu (`Path(__file__).parent.parent /
# "data/corpus/KUNYE.json"`). Paket EDITABLE kuruluyken (host, `pip install -e .`) bu
# yol repoya işaret ettiği için kusur GÖRÜNMEZDİ; paket NORMAL kurulunca (konteyner,
# `pip install ".[api]"`) `hakhukuk/` site-packages altına taşınır ama `data/corpus/`
# ONUNLA BİRLİKTE TAŞINMAZ — yol `site-packages/data/corpus/KUNYE.json`'a düşer, dosya
# orada YOKTUR. `kapsam_satiri()` PATLAMAZ (`except OSError` yutar) ve vatandaş sessizce
# "künye okunamadı — sayı belirsiz" okur. Duman denetiminde birebir görüldü
# (`outputs/eval/gorev/g20-imaj-olcumu/BULGU.md`, endişe B).
#
# Bu testin `monkeypatch.setattr(cli, "_KUNYE_YOLU", ...)` ile yazılması kusuru SINAMAZ:
# gerçek şart *"künye dosyası paket ağacına göre NEREDE aranıyor"*dur, sabitin değeri
# değil. Bu yüzden paket repo AĞACI OLMADAN bir geçici dizine kopyalanır, künye paketin
# İÇİNDE beklenen konuma konur ve `sys.path` üzerinden TAZE bir `hakhukuk.arayuz.cli` içe
# aktarılır — kurulu (editable olmayan) bir paketin gördüğü tam şartı taklit eder.

def _hakhukuk_modullerini_yedekle_ve_temizle() -> dict:
    yedek = {ad: mod for ad, mod in sys.modules.items()
             if ad == "hakhukuk" or ad.startswith("hakhukuk.")}
    for ad in yedek:
        del sys.modules[ad]
    return yedek


def _hakhukuk_modullerini_geri_yukle(yedek: dict) -> None:
    for ad in [a for a in sys.modules if a == "hakhukuk" or a.startswith("hakhukuk.")]:
        del sys.modules[ad]
    sys.modules.update(yedek)


def test_kapsam_satiri_kurulu_pakette_repo_agaci_olmadan_sayilari_buluyor(tmp_path):
    gercek_kunye = json.loads((REPO_KOK / "data/corpus/KUNYE.json").read_text(encoding="utf-8"))

    paket_hedefi = tmp_path / "hakhukuk"
    shutil.copytree(pathlib.Path(cli.__file__).resolve().parent.parent, paket_hedefi,
                    ignore=shutil.ignore_patterns("__pycache__"))
    # Künye PAKETİN İÇİNDE beklenen konuma konur — `tmp_path` altında repo AĞACI (üstte
    # bir `data/` klasörü) hiç YOK; kurulu paketin site-packages'ta göreceği şart budur.
    kunye_hedefi = paket_hedefi / "veri" / "KUNYE.json"
    kunye_hedefi.parent.mkdir(parents=True, exist_ok=True)
    kunye_hedefi.write_text(json.dumps(gercek_kunye), encoding="utf-8")

    yedek = _hakhukuk_modullerini_yedekle_ve_temizle()
    sys.path.insert(0, str(tmp_path))
    try:
        kurulu_cli = importlib.import_module("hakhukuk.arayuz.cli")
        satir = kurulu_cli.kapsam_satiri()
    finally:
        sys.path.remove(str(tmp_path))
        _hakhukuk_modullerini_geri_yukle(yedek)

    assert "künye okunamadı" not in satir, (
        f"kurulu pakette (repo ağacı yok) künye BULUNAMADI — kusur B geri geldi: {satir!r}")
    assert str(gercek_kunye["n_kanun"]) in satir, f"kanun sayısı satırda yok: {satir!r}"
    n_yururlukte = gercek_kunye["n_madde"] - gercek_kunye["n_mulga"]
    assert f"{n_yururlukte:,}".replace(",", ".") in satir, f"yürürlükteki madde sayısı satırda yok: {satir!r}"


def test_kapsam_satiri_kunye_hic_yoksa_durust_dusus_koruyor(tmp_path):
    """Düşüş dalı KALMALI: künye gerçekten yoksa uygulama açılmamak yerine dürüst bir
    satır göstermeye devam etmeli (brief madde 3) — bu, kurulu-paket düzeltmesiyle
    bozulmaması gereken davranıştır."""
    paket_hedefi = tmp_path / "hakhukuk"
    shutil.copytree(pathlib.Path(cli.__file__).resolve().parent.parent, paket_hedefi,
                    ignore=shutil.ignore_patterns("__pycache__"))
    kunye_yolu_olasi = paket_hedefi / "veri" / "KUNYE.json"
    if kunye_yolu_olasi.exists():
        kunye_yolu_olasi.unlink()

    yedek = _hakhukuk_modullerini_yedekle_ve_temizle()
    sys.path.insert(0, str(tmp_path))
    try:
        kurulu_cli = importlib.import_module("hakhukuk.arayuz.cli")
        satir = kurulu_cli.kapsam_satiri()
    finally:
        sys.path.remove(str(tmp_path))
        _hakhukuk_modullerini_geri_yukle(yedek)

    assert "künye okunamadı" in satir, f"künye gerçekten yokken düşüş dalı kaybolmuş: {satir!r}"
