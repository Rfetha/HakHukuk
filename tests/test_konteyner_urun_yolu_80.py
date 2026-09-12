"""ADIM 6.3 incelemesinin bulguları — `scripts/olcum_uretim/konteyner_urun_yolu_80.py`.

⛔ Ağsız: gerçek `urllib.request.urlopen` hiç çağrılmaz, sahte bir katmanla değiştirilir.
⛔ `outputs/eval/g23-konteyner-urun-yolu-80/` OKUNMAZ/YAZILMAZ — bu testler yalnız `tmp_path`
kullanır, `main()` hiçbir testte çağrılmaz (gerçek çıktı dizinine yazardı).

Bulgular:
  1. `_sor()` yalnız `HTTPError` yakalıyordu; `URLError`/zaman aşımı betiği ortasında
     çökertiyordu (kayıtlar diskte kalır ama künye/özet hiç yazılmaz). Şimdi yakalanıyor,
     sınırlı sayıda yeniden denemeyle, ve hata SESSİZCE yutulmuyor — kalem `durum="hata"`
     ile işaretlenip hata metni saklanıyor.
  2. Resume yoktu — her koşu `dev[0]`'dan başlıyordu. Şimdi çıktı dosyasındaki kalem sayısından
     devam ediyor, ama rejim (künye) ayrışmışsa PATLIYOR (sessizce karışık bir dosya üretmek
     yerine).
"""
import json
import pathlib
import socket
import urllib.error

import pytest

import importlib
modul = importlib.import_module("konteyner_urun_yolu_80")  # yol köprüsü: tests/conftest.py


# ── (1) ağ hatası sessizce yutulmuyor, sınırlı deneme ────────────────────────────────────

class _SahteYanit:
    def __init__(self, gövde: dict):
        self._gövde = json.dumps(gövde).encode("utf-8")
        self.status = 200

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        return self._gövde


def test_sor_url_hatasinda_durum_hata_ile_isaretlenir_ve_sessizce_yutulmaz(monkeypatch):
    monkeypatch.setattr(modul.time, "sleep", lambda *_: None)

    def patlayan(*a, **k):
        raise urllib.error.URLError("bağlantı reddedildi")
    monkeypatch.setattr(modul.urllib.request, "urlopen", patlayan)

    sonuc = modul._sor("test sorusu")

    assert sonuc["durum"] == "hata"
    assert sonuc["http"] is None
    assert "bağlantı reddedildi" in sonuc["hata"]


def test_sor_soket_zaman_asiminda_da_yutulmaz(monkeypatch):
    monkeypatch.setattr(modul.time, "sleep", lambda *_: None)

    def patlayan(*a, **k):
        raise socket.timeout("zaman aşımı")
    monkeypatch.setattr(modul.urllib.request, "urlopen", patlayan)

    sonuc = modul._sor("test sorusu")

    assert sonuc["durum"] == "hata"
    assert sonuc["http"] is None
    assert "hata" in sonuc


def test_sor_geciciyken_ikinci_denemede_toparlaniyor(monkeypatch):
    monkeypatch.setattr(modul.time, "sleep", lambda *_: None)
    denemeler = []

    def once_patla_sonra_gec(*a, **k):
        denemeler.append(1)
        if len(denemeler) == 1:
            raise urllib.error.URLError("geçici")
        return _SahteYanit({"metin": "cevap", "durum": "cevap"})
    monkeypatch.setattr(modul.urllib.request, "urlopen", once_patla_sonra_gec)

    sonuc = modul._sor("test sorusu")

    assert len(denemeler) == 2
    assert sonuc["http"] == 200
    assert "hata" not in sonuc


def test_sor_deneme_sayisi_sinirli_sonsuz_retry_yok(monkeypatch):
    monkeypatch.setattr(modul.time, "sleep", lambda *_: None)
    denemeler = []

    def hep_patla(*a, **k):
        denemeler.append(1)
        raise urllib.error.URLError("kalıcı")
    monkeypatch.setattr(modul.urllib.request, "urlopen", hep_patla)

    sonuc = modul._sor("test sorusu")

    assert len(denemeler) == modul.MAX_DENEME
    assert sonuc["durum"] == "hata"


def test_sor_httperror_davranisi_korunuyor(monkeypatch):
    """Regresyon: mevcut `HTTPError` davranışı (retry yok, gövde okunur) bozulmamalı."""
    import io

    def patlayan(*a, **k):
        gövde = io.BytesIO(b'{"detail": "soru bos olamaz"}')
        raise urllib.error.HTTPError("http://x", 422, "unprocessable", {}, gövde)
    monkeypatch.setattr(modul.urllib.request, "urlopen", patlayan)

    sonuc = modul._sor("")

    assert sonuc["http"] == 422
    assert "detay" in sonuc


# ── (2) resume: rejim aynıysa devam eder, ayrışırsa patlar ───────────────────────────────

def test_onceki_kayitlari_yukle_cikti_dosyasi_yoksa_bos_liste_doner(tmp_path):
    cikti = tmp_path / "urun_yolu_80.json"
    kunye_yolu = tmp_path / "KUNYE.json"

    sonuc = modul._onceki_kayitlari_yukle(cikti, kunye_yolu, {"a": 1})

    assert sonuc == []


def test_onceki_kayitlari_yukle_rejim_ayniyken_kayitlari_dondurur(tmp_path):
    cikti = tmp_path / "urun_yolu_80.json"
    kunye_yolu = tmp_path / "KUNYE.json"
    onceki_kayit = [{"id": 0, "soru": "x", "http": 200}]
    cikti.write_text(json.dumps(onceki_kayit), encoding="utf-8")
    onceki_kunye = {"api_url": "http://x", "tarih": "2026-09-11"}
    kunye_yolu.write_text(json.dumps(onceki_kunye), encoding="utf-8")
    mevcut_kunye = {"api_url": "http://x", "tarih": "2026-09-12"}  # yalnız tarih farklı

    sonuc = modul._onceki_kayitlari_yukle(cikti, kunye_yolu, mevcut_kunye)

    assert sonuc == onceki_kayit


def test_onceki_kayitlari_yukle_rejim_ayrisincha_patlar(tmp_path):
    cikti = tmp_path / "urun_yolu_80.json"
    kunye_yolu = tmp_path / "KUNYE.json"
    cikti.write_text(json.dumps([{"id": 0}]), encoding="utf-8")
    onceki_kunye = {"api_url": "http://x", "artefakt_sha256": {"gguf": "AAA"}}
    kunye_yolu.write_text(json.dumps(onceki_kunye), encoding="utf-8")
    mevcut_kunye = {"api_url": "http://x", "artefakt_sha256": {"gguf": "BBB"}}  # ayrıştı

    with pytest.raises(modul.RejimUyusmazligi):
        modul._onceki_kayitlari_yukle(cikti, kunye_yolu, mevcut_kunye)

    # ⚠️ Patladıktan sonra dahi eski kayıt dosyası ELLENMEMİŞ olmalı (yalnız okunur).
    assert json.loads(cikti.read_text(encoding="utf-8")) == [{"id": 0}]


# ── (3) künye toplandığı anda diske yazılır ───────────────────────────────────────────────

def test_kunye_yaz_dosyayi_hemen_olusturur(tmp_path):
    yol = tmp_path / "KUNYE.json"
    kunye = {"api_url": "http://x"}

    modul._kunye_yaz(yol, kunye)

    assert json.loads(yol.read_text(encoding="utf-8")) == kunye
