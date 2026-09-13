"""Görev 20 — konteyner dağıtımının kapı testleri ([ADR-0078](../docs/adr/kararlar-0064-0085.md#adr-0078)).

⛔ **Docker GEREKMEZ ve ÇAĞRILMAZ.** `compose.yaml` bir metin dosyası olarak değil, YAML
olarak **ayrıştırılır**; `indir.py` kapısı ağa çıkmadan, indirme monkeypatch'lenerek sınanır.

⚠️ Niçin metin araması YASAK: `grep "cache-type-k" compose.yaml` bayrağın **doğru servise**,
**doğru değerle** geçtiğini kanıtlamaz — bir yorum satırında, yanlış kutuda ya da değeri
düşmüş hâlde de eşleşir. Bu hattın hata sınıfı tam olarak budur: bayrak sessizce düşer, koşu
hata vermeden yanlış sayı üretir (`docs/record/yurutme-tuzaklari.md` birinci madde).

⚠️ `yaml` bir KAPI şartıdır, `importorskip` ile atlanmaz: atlanan test kapı değildir.
`PyYAML==6.0.3` `requirements.lock.txt`'te pinli ve kurulu ortamdan okundu (2026-09-11).
"""
import hashlib
import pathlib
import re

import pytest
import yaml

KOK = pathlib.Path(__file__).resolve().parent.parent

# ── Ölçüm rejiminin BAĞLAYICI bayrakları (ADR-0078 madde 1 · MODEL_CARD §7.10).
# Ticket 2 ölçtü: yalnız KV önbelleğinin kuantizasyonu değişince (q8_0 ↔ fp16) aynı soruda
# cevap DEĞİŞTİ. Bunlar tercih değil, cevabı belirleyen ayarlardır.
# ⚠️ `--host` bilerek burada DEĞİL: tek izinli sapma aşağıda ayrıca sınanır.
KANONIK_DEGERLI = {
    "-ngl": "99",
    "-fa": "on",
    "--cache-type-k": "q8_0",
    "--cache-type-v": "q8_0",
    "-c": "8192",
    "--port": "8080",
    # ⚠️ Üretimin bağlayıcı komutunda YOKTU; 2026-09-11'de insan kararıyla AÇIKÇA pinlendi
    # (açık kusur 20). Ürün yolunun iki geçişli zorunlu kapatması (ADR-0080)
    # `message.reasoning_content` alanına bağımlı; varsayılan `auto` başka bir biçime
    # çözülürse mekanizma SESSİZCE tek geçişe düşer ve boş cevap kusuru geri gelir.
    # Rejim DEĞİŞMEDİ: `auto` ≡ `deepseek` olduğu koşan sunucuya doğrudan istekle ÖLÇÜLDÜ.
    "--reasoning-format": "deepseek",
}
KANONIK_DEGERSIZ = ("--no-context-shift",)


@pytest.fixture(scope="module")
def compose() -> dict:
    return yaml.safe_load((KOK / "compose.yaml").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def indir():
    """Gecikmeli içe alma: modül yoksa test ADIYLA kırmızı düşsün, toplama çökmesin."""
    from hakhukuk import indir as modul
    return modul


def _bayraklar(komut: list[str]) -> dict[str, str | None]:
    """`["-ngl", "99", "--no-context-shift"]` → `{"-ngl": "99", "--no-context-shift": None}`.

    ⚠️ Değersiz bayrak `None` ile durur: *"bayrak var"* ile *"bayrağın değeri şu"* ayrı
    şeylerdir ve ikisi ayrı ayrı çivilenir.
    """
    esleme: dict[str, str | None] = {}
    for i, jeton in enumerate(komut):
        if not jeton.startswith("-"):
            continue
        sonraki = komut[i + 1] if i + 1 < len(komut) else None
        esleme[jeton] = None if sonraki is None or sonraki.startswith("-") else sonraki
    return esleme


# ── (a) kanonik bayrak kümesi BİREBİR ────────────────────────────────────────────────────

def test_llama_komutu_kanonik_bayraklari_birebir_tasiyor(compose):
    bayrak = _bayraklar(compose["services"]["llama"]["command"])
    for ad, deger in KANONIK_DEGERLI.items():
        assert bayrak.get(ad) == deger, f"{ad} bayrağı {bayrak.get(ad)!r}, beklenen {deger!r}"
    for ad in KANONIK_DEGERSIZ:
        assert ad in bayrak, f"{ad} bayrağı DÜŞMÜŞ"
        assert bayrak[ad] is None, f"{ad} değersiz bayraktır, {bayrak[ad]!r} almış"


def test_llama_model_yolu_volumedeki_gguf_dosyasini_gosteriyor(compose, indir):
    """Model yolu imajın içini değil, `indir` kutusunun yazdığı volume'ü göstermeli."""
    llama = compose["services"]["llama"]
    yol = _bayraklar(llama["command"])["-m"]
    bagli = [b.split(":")[1] for b in llama["volumes"]]
    assert any(yol.startswith(hedef.rstrip("/") + "/") for hedef in bagli), \
        f"-m {yol} bağlı volume'lerin ({bagli}) hiçbirinin altında değil"
    assert yol.endswith(indir.GGUF_DOSYA)


# ── (b) tek izinli sapma + erişim yüzeyi — İKİSİ BİRLİKTE ────────────────────────────────

def test_llama_host_sapmasi_var_ve_yayin_yalniz_yerele(compose):
    """⚠️ Bu iki hüküm AYRILMAZ: biri olmadan diğeri tehlikelidir.

    `--host 0.0.0.0` konteyner içinde zorunludur (`127.0.0.1` komşu kutudan erişilemez),
    ama erişim yüzeyi `ports` ile host'un `127.0.0.1`'ine kısıtlı KALMALIDIR — aksi hâlde
    sunucu ağa açılır ve S9 (barındırma/mahremiyet) sessizce açılmış olur.
    """
    llama = compose["services"]["llama"]
    assert _bayraklar(llama["command"])["--host"] == "0.0.0.0"
    assert llama["ports"] == ["127.0.0.1:8080:8080"]


# ── (c) indirme bir KAPIdır: tutmazsa erken çıkar, hedefe HİÇBİR ŞEY bırakmaz ────────────

@pytest.fixture
def sahte_inis(monkeypatch, indir):
    """`_hf_indir`'i ağsız bir sahteyle değiştirir; inen baytları çağıran seçer."""
    def kur(icerik: bytes):
        def sahte(depo, dosya, revizyon, dizin):
            yol = pathlib.Path(dizin) / dosya
            yol.write_bytes(icerik)
            return yol
        monkeypatch.setattr(indir, "_hf_indir", sahte)
    return kur


def test_indir_yanlis_sha256_karsisinda_erken_cikiyor(tmp_path, monkeypatch, indir, sahte_inis):
    """Bayt sayısı tutan ama içeriği BAŞKA olan dosya — kapı yalnız boyuta bakamaz."""
    icerik = b"bu dogru artefakt DEGIL"
    sahte_inis(icerik)
    monkeypatch.setattr(indir, "GGUF_BAYT", len(icerik))       # bayt kapısı GEÇSİN
    with pytest.raises(indir.KimlikHatasi):
        indir.indir_model(tmp_path)
    assert list(tmp_path.iterdir()) == [], "kapı tutmadı ama hedefte artık var"


def test_indir_yanlis_bayt_sayisi_karsisinda_erken_cikiyor(tmp_path, monkeypatch, indir,
                                                           sahte_inis):
    """Bayt kapısı `sha256`'dan BAĞIMSIZ tutmalı: özet doğru olsa bile boyut yanlışsa durur."""
    icerik = b"kisa"
    sahte_inis(icerik)
    monkeypatch.setattr(indir, "GGUF_SHA256", hashlib.sha256(icerik).hexdigest())
    with pytest.raises(indir.KimlikHatasi):
        indir.indir_model(tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_indir_kapi_tutmazsa_cikis_kodu_sifirdan_farkli(tmp_path, indir, sahte_inis, capsys):
    """Compose bağı çıkış koduna bakar: `indir` patlarsa iki daemon da HİÇ başlamaz."""
    sahte_inis(b"yanlis artefakt")
    assert indir.main([str(tmp_path)]) != 0
    assert list(tmp_path.iterdir()) == []


def test_indir_kapi_tutunca_artefakti_hedefe_tasiyor(tmp_path, monkeypatch, indir, sahte_inis):
    """Mutlu yol: dosya hedefe taşınır ve geçici hiçbir kalıntı kalmaz."""
    icerik = b"dogru artefakt oldugunu varsaydigimiz baytlar"
    sahte_inis(icerik)
    monkeypatch.setattr(indir, "GGUF_BAYT", len(icerik))
    monkeypatch.setattr(indir, "GGUF_SHA256", hashlib.sha256(icerik).hexdigest())
    yol = indir.indir_model(tmp_path)
    assert yol.read_bytes() == icerik
    assert [y.name for y in tmp_path.iterdir()] == [indir.GGUF_DOSYA]


# ── (d) revizyon PİNLİ — `latest` yasak ──────────────────────────────────────────────────

def test_pinlenmis_revizyon_latest_degil_ve_tam_commit_sha(indir):
    """*"En güncel modeli çek"* bu hattın hata sınıfıdır: yayımlanan sayı BELİRLİ bir
    dosyanındır (`kollar.md` 2026-09-09). Dal adı da yetmez — dal ilerler."""
    assert indir.GGUF_REVIZYON != "latest"
    assert re.fullmatch(r"[0-9a-f]{40}", indir.GGUF_REVIZYON), \
        f"revizyon 40 karakterlik commit sha'sı değil: {indir.GGUF_REVIZYON!r}"


def test_compose_imajlari_pinli(compose):
    """Aynı kuralın imaj tarafı: etiketsiz ya da `latest` imaj sessizce başka bir ikili çeker."""
    for ad, servis in compose["services"].items():
        if "image" not in servis:
            continue
        etiket = servis["image"].rsplit(":", 1)
        assert len(etiket) == 2 and etiket[1] != "latest", \
            f"{ad} servisinin imajı pinli değil: {servis['image']}"


# ── (e) app kutusu: llama'ya yönelir, yalnız yerele yayımlar ─────────────────────────────

def test_app_llama_kutusuna_yoneliyor_ve_yalniz_yerele_yayimliyor(compose):
    app = compose["services"]["app"]
    assert app["environment"]["HAKHUKUK_SUNUCU"] == "http://llama:8080/v1"
    assert app["ports"] == ["127.0.0.1:8000:8000"]


# ── (f) indirme başarısızsa İKİ daemon da hiç başlamaz ───────────────────────────────────

@pytest.mark.parametrize("daemon", ["llama", "app"])
def test_daemonlar_indir_kapisina_bagli(compose, daemon):
    bag = compose["services"][daemon]["depends_on"]["indir"]
    assert bag["condition"] == "service_completed_successfully"


# ── (g) kusur 32: indeksin künyesi korpusu GÖRELİ tutar — volume yerleşimi bunu çözmeli ──
#
# ⚠️ Bu kusur `G8 Adım 1b`'nin taşınabilirlik onarımının TERS YÜZÜdür: künyedeki mutlak yol
# indekse göreli (`../../corpus/…`) yapılınca `git clone` düzeldi, ama indeksin repo ağacının
# DIŞINA (volume'e) taşındığı tek düzen kırıldı — `/artefakt/<ad>/../../corpus` = `/corpus`.
# Çözüm repo düzenini AYNALAMAK: indeks iki seviye derinde (`/artefakt/index/<ad>/`),
# korpus `/artefakt/corpus/`. Aşağıdaki kapı bunu künyeden OKUYARAK doğrular — sabit yol
# yazılmaz, çünkü künye değişirse kapının da değişmesi gerekir.

def _indir_hedef_dizini(compose) -> str:
    """`indir` kutusunun yazdığı volume dizini — komutun son argümanı."""
    return compose["services"]["indir"]["command"][-1]


def test_indeks_kunyesindeki_goreli_korpus_yolu_volume_yerlesiminde_cozuluyor(compose, indir):
    """`normpath(HAKHUKUK_INDEKS + künyedeki göreli yol)` = `indir`'in korpusu koyduğu yer."""
    import json
    import os

    hedef_dizin = _indir_hedef_dizini(compose)
    indeks_yolu = compose["services"]["app"]["environment"]["HAKHUKUK_INDEKS"]
    assert indeks_yolu == str(indir.indeks_hedefi(hedef_dizin)), \
        "app'in gösterdiği indeks, `indir`'in kurduğu indeks DEĞİL"

    kunye = json.loads((KOK / "data" / "index" / indir.INDEKS_ADI / "KUNYE.json")
                       .read_text(encoding="utf-8"))
    goreli = kunye["korpus"]["yol"]
    assert not os.path.isabs(goreli), "künye mutlak yol taşıyor — taşınabilir değil"
    cozulen = os.path.normpath(os.path.join(indeks_yolu, goreli))
    assert cozulen == str(indir.korpus_hedefi(hedef_dizin)), (
        f"künyedeki {goreli!r} {indeks_yolu} altında {cozulen} çözülüyor, ama `indir` korpusu "
        f"{indir.korpus_hedefi(hedef_dizin)} yoluna koyuyor — retriever korpusu BULAMAZ")


def test_cozulen_korpus_yolu_app_kutusuna_bagli_volumenin_altinda(compose, indir):
    """Doğru çözülen yol, `app`'in gerçekten bağladığı bir volume'ün altında olmalı."""
    bagli = [b.split(":")[1] for b in compose["services"]["app"]["volumes"]]
    korpus = str(indir.korpus_hedefi(_indir_hedef_dizini(compose)))
    assert any(korpus.startswith(hedef.rstrip("/") + "/") for hedef in bagli), \
        f"{korpus} app'e bağlı volume'lerin ({bagli}) hiçbirinin altında değil"


def test_indir_korpusu_kaynagindan_kopyalayip_sha256_dogruluyor(tmp_path, monkeypatch, indir):
    """Korpus HF'ten İNMEZ, imajdaki kopyadan gelir; kopya `sha256` ile doğrulanır (ağ YOK)."""
    import hashlib

    kaynak = tmp_path / "kaynak" / "mevzuat_maddeler.jsonl"
    kaynak.parent.mkdir(parents=True)
    icerik = b'{"id": 1, "text": "madde"}\n'
    kaynak.write_bytes(icerik)
    monkeypatch.setattr(indir, "korpus_kaynagi", lambda: kaynak)

    hedef_dizin = tmp_path / "artefakt"
    yol = indir.yerlestir_korpus(hedef_dizin)
    assert yol == indir.korpus_hedefi(hedef_dizin)
    assert yol.read_bytes() == icerik
    assert hashlib.sha256(yol.read_bytes()).hexdigest() == hashlib.sha256(icerik).hexdigest()
    assert [y.name for y in yol.parent.iterdir()] == [indir.KORPUS_DOSYA], "geçici kalıntı var"


def test_indir_volumedeki_korpus_imajdakinden_ayrisirsa_erken_patliyor(tmp_path, monkeypatch,
                                                                       indir):
    """S18 · İKİNCİ KOPYA: `servis.py` imajdakini, retriever volume'dekini okur. Ayrışırlarsa
    ürün iki farklı korpustan cevap verir — bu SESSİZ yanlışlıktır, kapı burada durur."""
    kaynak = tmp_path / "kaynak" / "mevzuat_maddeler.jsonl"
    kaynak.parent.mkdir(parents=True)
    kaynak.write_bytes(b'{"id": 1}\n')
    monkeypatch.setattr(indir, "korpus_kaynagi", lambda: kaynak)

    hedef_dizin = tmp_path / "artefakt"
    hedef = indir.korpus_hedefi(hedef_dizin)
    hedef.parent.mkdir(parents=True)
    hedef.write_bytes(b'{"id": 2}\n')          # volume'deki kopya AYRIŞMIŞ

    with pytest.raises(indir.KimlikHatasi):
        indir.yerlestir_korpus(hedef_dizin)


def test_indir_kapisi_korpus_dusunce_cikis_kodu_sifirdan_farkli(tmp_path, monkeypatch, indir,
                                                                 sahte_inis):
    """`main` üç artefaktı da kurar: model · korpus · indeks. YALNIZ korpus düşse bile ≠ 0."""
    icerik = b"dogru artefakt oldugunu varsaydigimiz baytlar"
    sahte_inis(icerik)
    monkeypatch.setattr(indir, "GGUF_BAYT", len(icerik))
    monkeypatch.setattr(indir, "GGUF_SHA256", hashlib.sha256(icerik).hexdigest())

    hedef_dizin = tmp_path / "artefakt"
    indeks = indir.indeks_hedefi(hedef_dizin)          # indeks kapısı GEÇSİN
    indeks.mkdir(parents=True)
    (indeks / "gomme.npy").write_bytes(b"")
    monkeypatch.setattr(indir, "korpus_kaynagi", lambda: tmp_path / "yok.jsonl")

    assert indir.main([str(hedef_dizin)]) != 0


# ── (h) G8 — indeksin HF varsayılan deposu ve kimlik kapısı ──────────────────────────────
#
# ⚠️ İndeksin GGUF'un aksine hiçbir kimlik kapısı YOKTU (satır 157 yalnız `gomme.npy var mı`
# diye bakıyordu) — oysa cevabı belirleyen şey indeks. Aşağıdaki kapı GGUF kapısının kalıbını
# izler: bayt sayısı önce (ucuz), `sha256` sonra, ağsız sınanır.

@pytest.fixture
def sahte_indeks_inis(monkeypatch, indir):
    """`_hf_indeks_indir`'i ağsız bir sahteyle değiştirir; istenen depo adı yakalanır."""
    istenen_depo: list[str] = []

    def kur(icerik: bytes):
        def sahte(depo, dizin):
            istenen_depo.append(depo)
            dizin = pathlib.Path(dizin)
            (dizin / "gomme.npy").write_bytes(icerik)
            return dizin
        monkeypatch.setattr(indir, "_hf_indeks_indir", sahte)
    return kur, istenen_depo


def test_indeks_depo_varsayilani_tanimli(indir):
    """G8 kapandı: sabit bir varsayılan depo var — dosya adı, `INDEKS_ADI` ve depo adı
    aynı dizeyi taşır (insan kararı 2026-09-12: *"hangi indeks?"* dosya adından cevaplanır)."""
    assert indir.INDEKS_DEPO == "Rfetha/HakHukuk-mevzuat-bge-m3-s2"


def test_indeks_ortam_degiskeni_tanimliyken_varsayilan_yerine_o_kullaniliyor(
        tmp_path, monkeypatch, indir, sahte_indeks_inis):
    """Bugünkü davranış korunur: `HAKHUKUK_INDEKS_DEPO` tanımlıysa varsayılanı GEÇERSİZ kılar."""
    kur, istenen = sahte_indeks_inis
    icerik = b"sahte gomme baytlari"
    kur(icerik)
    monkeypatch.setattr(indir, "INDEKS_GOMME_BAYT", len(icerik))
    monkeypatch.setattr(indir, "INDEKS_GOMME_SHA256", hashlib.sha256(icerik).hexdigest())
    monkeypatch.setenv(indir.INDEKS_DEPO_ORTAM, "baska-kullanici/baska-indeks")

    indir.indir_indeks(tmp_path / "artefakt")

    assert istenen == ["baska-kullanici/baska-indeks"]


def test_indeks_ortam_degiskeni_yoksa_varsayilan_depo_kullaniliyor(
        tmp_path, monkeypatch, indir, sahte_indeks_inis):
    """`HAKHUKUK_INDEKS_DEPO` tanımsızken artık PATLAMAZ — `INDEKS_DEPO` varsayılanına düşer."""
    kur, istenen = sahte_indeks_inis
    icerik = b"sahte gomme baytlari"
    kur(icerik)
    monkeypatch.setattr(indir, "INDEKS_GOMME_BAYT", len(icerik))
    monkeypatch.setattr(indir, "INDEKS_GOMME_SHA256", hashlib.sha256(icerik).hexdigest())
    monkeypatch.delenv(indir.INDEKS_DEPO_ORTAM, raising=False)

    indir.indir_indeks(tmp_path / "artefakt")

    assert istenen == [indir.INDEKS_DEPO]


def test_indeks_kimlik_kapisi_yanlis_sha256da_erken_cikiyor(
        tmp_path, monkeypatch, indir, sahte_indeks_inis):
    """Bayt sayısı tutan ama içeriği BAŞKA olan indeks — kapı yalnız boyuta bakamaz."""
    kur, _ = sahte_indeks_inis
    icerik = b"bu dogru indeks DEGIL"
    kur(icerik)
    monkeypatch.setattr(indir, "INDEKS_GOMME_BAYT", len(icerik))     # bayt kapısı GEÇSİN
    monkeypatch.delenv(indir.INDEKS_DEPO_ORTAM, raising=False)

    hedef_dizin = tmp_path / "artefakt"
    with pytest.raises(indir.KimlikHatasi):
        indir.indir_indeks(hedef_dizin)
    assert not indir.indeks_hedefi(hedef_dizin).exists(), "kapı tutmadı ama hedefte artık var"


def test_indeks_kimlik_kapisi_yanlis_bayt_sayisinda_erken_cikiyor(
        tmp_path, monkeypatch, indir, sahte_indeks_inis):
    """Bayt kapısı `sha256`'dan BAĞIMSIZ tutmalı: özet doğru olsa bile boyut yanlışsa durur."""
    kur, _ = sahte_indeks_inis
    icerik = b"kisa"
    kur(icerik)
    monkeypatch.setattr(indir, "INDEKS_GOMME_SHA256", hashlib.sha256(icerik).hexdigest())
    monkeypatch.delenv(indir.INDEKS_DEPO_ORTAM, raising=False)

    hedef_dizin = tmp_path / "artefakt"
    with pytest.raises(indir.KimlikHatasi):
        indir.indir_indeks(hedef_dizin)
    assert not indir.indeks_hedefi(hedef_dizin).exists()


# ── (i) volume'de ZATEN duran indeks de kapıdan geçmeli — 6.2'nin bırakılan açığı ────────
#
# ⚠️ Bugüne kadar `(hedef / "gomme.npy").exists()` yeterliydi: HF'e hiç gidilmiyor ama
# `sha256`/bayt da hiç sınanmıyordu. GGUF tarafında böyle değil (`indir_model` idempotent
# yolda da `_kapidan_gecir`'i ÇAĞIRIR) — bu asimetri G8 raporunun kendi öz-inceleme
# bölümünde şüphe olarak not edilmişti. Aşağıdaki iki test ağsız (`_hf_indeks_indir`
# çağrılırsa patlar) sınanır.

def test_indeks_volumede_dogru_gomme_varsa_hf_e_gitmeden_kapidan_geciyor(
        tmp_path, monkeypatch, indir):
    """Volume'de kimliği TUTAN bir kopya varsa: indirme yok, kapı geçer, yol döner."""
    def hic_cagrilmamali(depo, dizin):
        raise AssertionError("volume'de doğru kopya varken HF'e gidilmemeli")
    monkeypatch.setattr(indir, "_hf_indeks_indir", hic_cagrilmamali)

    icerik = b"dogru indeks oldugunu varsaydigimiz baytlar"
    monkeypatch.setattr(indir, "INDEKS_GOMME_BAYT", len(icerik))
    monkeypatch.setattr(indir, "INDEKS_GOMME_SHA256", hashlib.sha256(icerik).hexdigest())

    hedef_dizin = tmp_path / "artefakt"
    hedef = indir.indeks_hedefi(hedef_dizin)
    hedef.mkdir(parents=True)
    (hedef / "gomme.npy").write_bytes(icerik)

    yol = indir.indir_indeks(hedef_dizin)
    assert yol == hedef


def test_indeks_volumede_yanlis_icerikli_gomme_varsa_erken_patliyor(
        tmp_path, monkeypatch, indir):
    """Volume'deki kopya elle bozulmuş/yarım inmişse SESSİZCE kullanılmamalı.

    Bugün (onarım öncesi) bu kırmızı düşer: `indir_indeks` `gomme.npy var mı` dışında hiçbir
    şey sınamadan hedefi döndürür — cevabı belirleyen indeks böylece hatasız yanlış olur.
    """
    def hic_cagrilmamali(depo, dizin):
        raise AssertionError("kimlik kapısı volume'deki kopyaya bakmalı, HF'e gitmemeli")
    monkeypatch.setattr(indir, "_hf_indeks_indir", hic_cagrilmamali)

    dogru_icerik = b"dogru indeks oldugunu varsaydigimiz baytlar"
    monkeypatch.setattr(indir, "INDEKS_GOMME_BAYT", len(dogru_icerik))
    monkeypatch.setattr(indir, "INDEKS_GOMME_SHA256", hashlib.sha256(dogru_icerik).hexdigest())

    hedef_dizin = tmp_path / "artefakt"
    hedef = indir.indeks_hedefi(hedef_dizin)
    hedef.mkdir(parents=True)
    (hedef / "gomme.npy").write_bytes(b"volumede elle bozulmus BASKA baytlar")

    with pytest.raises(indir.KimlikHatasi):
        indir.indir_indeks(hedef_dizin)
