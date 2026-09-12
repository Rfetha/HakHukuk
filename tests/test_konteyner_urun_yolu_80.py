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

ADIM 6.3'ün İNCELEMESİNİN bulguları (kimlik değil AD karşılaştırma + altın kimlik eksikliği):
  3. `_konteyner_imaji()` `{{.Config.Image}}` (TAG) okuyordu, `{{.Image}}` (DİGEST) değil —
     aynı tag farklı içerikle yeniden derlenince künyenin hiçbir alanı farkı yakalamıyordu
     (ölçüldü: `sha256:35053579…` → `sha256:b5d8e07a…`, ikisi de `hakhukuk:0.3.0`). Şimdi
     `_konteyner_imaj_etiketi()` (insan okusun) ve `_konteyner_imaj_digest()` (kimlik) ayrı;
     künyede ikisi de saklanıyor. `dev_seti` de artık yol + `sha256` taşıyor — yalnız yol değil.
  4. Üretim çıktısı yalnız `id`+`soru` taşıyordu; `id` koşuya özgü bir sayaç olduğu için altın
     maddeye GÜVENİLİR bağlanamıyordu (ölçüldü: g23↔f02 arası `id` eşleşmesi 0/80). Şimdi her
     kalem `kanun_no`/`madde_no`/`kanun_adi`'yi DEV setinden taşıyor (`_kalem_olustur`).
"""
import hashlib
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


# ── (4) imaj kimliği DİGEST'le, dev seti SHA256'la kimlikleniyor ─────────────────────────

def test_konteyner_imaj_etiketi_config_image_formatini_okur(monkeypatch):
    komutlar = []

    def sahte(komut):
        komutlar.append(komut)
        return "hakhukuk:0.3.0"
    monkeypatch.setattr(modul, "_calistir", sahte)

    etiket = modul._konteyner_imaj_etiketi("hakhukuk-app-1")

    assert etiket == "hakhukuk:0.3.0"
    assert komutlar == [["docker", "inspect", "hakhukuk-app-1", "--format", "{{.Config.Image}}"]]


def test_konteyner_imaj_digest_image_formatini_okur_config_image_DEGIL(monkeypatch):
    """Bulgu: `{{.Config.Image}}` TAG'dir, yeniden derlemede AYNI kalır — kimlik `{{.Image}}`."""
    komutlar = []

    def sahte(komut):
        komutlar.append(komut)
        return "sha256:b5d8e07a..."
    monkeypatch.setattr(modul, "_calistir", sahte)

    digest = modul._konteyner_imaj_digest("hakhukuk-app-1")

    assert digest == "sha256:b5d8e07a..."
    assert komutlar == [["docker", "inspect", "hakhukuk-app-1", "--format", "{{.Image}}"]]


def test_kunye_topla_imajlari_digestle_dev_setini_sha256la_kimliklendirir(monkeypatch, tmp_path):
    dev = tmp_path / "core_hard.jsonl"
    dev.write_text('{"soru": "x"}\n', encoding="utf-8")
    monkeypatch.setattr(modul, "DEV_YOLU", str(dev))
    monkeypatch.setattr(modul, "_konteyner_sureci", lambda ad: f"cmd-{ad}")
    monkeypatch.setattr(modul, "_konteyner_imaj_etiketi", lambda ad: f"etiket-{ad}")
    monkeypatch.setattr(modul, "_konteyner_imaj_digest", lambda ad: f"sha256:digest-{ad}")
    monkeypatch.setattr(modul, "_dosya_sha256", lambda konteyner, yol: f"sha256-{konteyner}-{yol}")

    kunye = modul.kunye_topla()

    assert kunye["imajlar"]["app/indir"] == {
        "etiket": "etiket-hakhukuk-app-1", "digest": "sha256:digest-hakhukuk-app-1"}
    assert kunye["imajlar"]["llama"] == {
        "etiket": "etiket-hakhukuk-llama-1", "digest": "sha256:digest-hakhukuk-llama-1"}
    assert kunye["dev_seti"] == {
        "yol": str(dev), "sha256": hashlib.sha256(dev.read_bytes()).hexdigest()}


def test_kunye_topla_ayni_etiket_farkli_digestte_rejim_ayrisir_END_TO_END(monkeypatch, tmp_path):
    """Bulgu tam olarak bunu ölçmüştü: aynı TAG, yeniden derlemeyle DEĞİŞEN digest — künyenin
    HİÇBİR ALANI bunu yakalamıyordu. Şimdi imaj değişse bile etiket aynı kalsa dahi resume
    PATLAR (`RejimUyusmazligi`)."""
    dev = tmp_path / "core_hard.jsonl"
    dev.write_text('{"soru": "x"}\n', encoding="utf-8")
    monkeypatch.setattr(modul, "DEV_YOLU", str(dev))
    monkeypatch.setattr(modul, "_konteyner_sureci", lambda ad: "cmd")
    monkeypatch.setattr(modul, "_konteyner_imaj_etiketi", lambda ad: "hakhukuk:0.3.0")  # SABİT
    monkeypatch.setattr(modul, "_dosya_sha256", lambda konteyner, yol: "sha")

    monkeypatch.setattr(modul, "_konteyner_imaj_digest", lambda ad: "sha256:ESKI")
    eski_kunye = modul.kunye_topla()
    cikti = tmp_path / "urun_yolu_80.json"
    kunye_yolu = tmp_path / "KUNYE.json"
    cikti.write_text(json.dumps([{"id": 0}]), encoding="utf-8")
    modul._kunye_yaz(kunye_yolu, eski_kunye)

    monkeypatch.setattr(modul, "_konteyner_imaj_digest", lambda ad: "sha256:YENI")  # yeniden derlendi
    yeni_kunye = modul.kunye_topla()

    with pytest.raises(modul.RejimUyusmazligi):
        modul._onceki_kayitlari_yukle(cikti, kunye_yolu, yeni_kunye)


# ── (5) üretim çıktısı ALTIN KİMLİĞİ (kanun_no/madde_no/kanun_adi) taşır ──────────────────

def test_kalem_olustur_altin_kimligi_dev_setinden_tasir():
    """Bulgu: çıktı yalnız id+soru taşıyordu ve `id` koşuya özgü bir sayaçtı — g23↔f02 arası
    `id` eşleşmesi ÖLÇÜLDÜ: 0/80. Altın madde artık `id` ile değil, bu alanlarla bağlanabilir."""
    dev_ogesi = {
        "messages": [{"role": "user", "content": "soru metni"}],
        "kanun_adi": "TÜRK CEZA KANUNU", "kanun_no": "5237", "madde_no": "Madde 89",
    }

    kalem = modul._kalem_olustur(7, dev_ogesi, {"http": 200, "metin": "cevap"})

    assert kalem["id"] == 7
    assert kalem["soru"] == "soru metni"
    assert kalem["kanun_no"] == "5237"
    assert kalem["madde_no"] == "Madde 89"
    assert kalem["kanun_adi"] == "TÜRK CEZA KANUNU"
    assert kalem["http"] == 200 and kalem["metin"] == "cevap"
