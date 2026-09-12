"""Artefakt indirme KAPISI — pinlenmiş revizyon, `sha256` ve bayt sayısı.

⛔ Kapı TEK YERDE durur (ADR-0078, elenen seçenek *"indirmeyi iki servise dağıtmak"*):
`llama` kendi GGUF'unu, `app` kendi indeksini çekseydi aynı mantık iki yerde durur ve
sessizce ayrışırdı — S18'in ölçülmüş dersi.

⚠️ **Kapı tutmazsa hedefte HİÇBİR ŞEY kalmaz.** Önce hedefin yanındaki geçici bir dizine
inilir, kapı geçerse `os.replace` ile taşınır. Yarım yazılmış bir artefakt bu hattın
*"hata vermeden yanlış"* sınıfının kendisidir: sonraki koşu onu geçerli sanar.

Kimlik `docs/record/kollar.md` 2026-09-09 bloğundan OKUNDU, tahmin edilmedi. Yayımlanan
`0,8011` **belirli bir dosyanın** sayısıdır; *"en güncel modeli çek"* onu sessizce başka bir
artefakta bağlar.
"""
import hashlib
import os
import pathlib
import shutil
import sys
import tempfile

GGUF_DEPO = "Rfetha/HakHukuk-4B-v0.3-Q4_K_M"
GGUF_DOSYA = "HakHukuk-4B-v0.3-Q4_K_M.gguf"
GGUF_REVIZYON = "902ace67259b3fac18c56907070485f5cace272b"   # ⛔ `latest` YASAK (ADR-0078 m.3)
GGUF_SHA256 = "755e15e92e9f7021934f2d5eada6c1f02fcc92be23f0536b0c2a0a9586e7bffc"
GGUF_BAYT = 2_783_446_720                                     # = 2,592 GiB

INDEKS_ADI = "mevzuat_bge_m3_s2"
KORPUS_DOSYA = "mevzuat_maddeler.jsonl"

# ⛔ VOLUME YERLEŞİMİ REPO AĞACINI AYNALAR — kolaylık değil, ZORUNLULUK (kusur 32).
# İndeksin `KUNYE.json`'u korpusu **indeks dizinine GÖRELİ** tutar (`../../corpus/…`).
# Bu, `G8 Adım 1b`'nin taşınabilirlik onarımıydı: mutlak yol + mtime her `git clone`'dan
# sonra yanlış alarm veriyordu. Onarım repo içini düzeltti, indeksin repo ağacının DIŞINA
# taşındığı tek düzeni KIRDI: indeks `/artefakt/<ad>/` iken `../../corpus/` = `/corpus`'a
# çıkar ve retriever *"korpus bulunamadı"* ile ölür (ölçüldü, canlı konteynerde HTTP 500).
# ⚠️ Korpusu `/artefakt/corpus/`'a koymak TEK BAŞINA YETMEZ: indeks de **iki seviye derine**
# inmelidir. `data/index/<ad>/` ↔ `data/corpus/` ikilisi burada `<volume>/index/<ad>/` ↔
# `<volume>/corpus/` olarak birebir aynalanır.
INDEKS_ALT = "index"
KORPUS_ALT = "corpus"
# ⛔ İndeks deposu bir PARAMETREdir, varsayılanı YOKTUR — ADR-0026'nın *"tanımsız base ERKEN
# patlar"* kuralının aynı sınıfı. Görev 8 (indeks dağıtımı) BEKLETİLİYOR: korpus 8,4×
# büyüyecek ve *"83 MB mı 697 MB mı"* kararı henüz verilmedi ⇒ uydurulmuş bir depo adı
# yazmak, olmayan bir artefakta bağlanmak olurdu.
INDEKS_DEPO_ORTAM = "HAKHUKUK_INDEKS_DEPO"

_OKUMA_PARCASI = 1 << 20


class KimlikHatasi(RuntimeError):
    """İnen dosya beklenen artefakt DEĞİL. Sessiz devam yoktur (ADR-0078 madde 3)."""


def _hf_indir(depo: str, dosya: str, revizyon: str, dizin: pathlib.Path) -> pathlib.Path:
    """HF Hub'dan tek dosya çeker. Testler bunu değiştirir — sınamada ağ YOKTUR."""
    from huggingface_hub import hf_hub_download  # noqa: PLC0415 — ağır, yalnız indirirken
    return pathlib.Path(hf_hub_download(repo_id=depo, filename=dosya, revision=revizyon,
                                        local_dir=str(dizin)))


def _hf_indeks_indir(depo: str, dizin: pathlib.Path) -> pathlib.Path:
    """İndeks deposunun tamamını çeker (Görev 8'in kod gövdesi)."""
    from huggingface_hub import snapshot_download  # noqa: PLC0415
    return pathlib.Path(snapshot_download(repo_id=depo, repo_type="dataset",
                                          local_dir=str(dizin)))


def _ozet(yol: pathlib.Path) -> str:
    """Dosyanın `sha256`'sı, parça parça — 2,6 GB'lık artefakt belleğe alınmaz."""
    ozet = hashlib.sha256()
    with open(yol, "rb") as dosya:
        for parca in iter(lambda: dosya.read(_OKUMA_PARCASI), b""):
            ozet.update(parca)
    return ozet.hexdigest()


def _kapidan_gecir(yol: pathlib.Path, bekleyen_bayt: int, bekleyen_sha: str, ad: str) -> None:
    """Bayt sayısı ve `sha256` tutmuyorsa `KimlikHatasi`. Önce boyut: büyük dosyayı boşuna özetleme.

    `ad` yalnız hata mesajınadır — birden çok artefakt (GGUF, indeks) aynı kapıyı paylaşır.
    """
    boyut = yol.stat().st_size
    if boyut != bekleyen_bayt:
        raise KimlikHatasi(
            f"bayt sayısı tutmadı: {boyut} ≠ {bekleyen_bayt} (beklenen artefakt {ad})")
    bulunan = _ozet(yol)
    if bulunan != bekleyen_sha:
        raise KimlikHatasi(f"sha256 tutmadı: {bulunan} ≠ {bekleyen_sha} (beklenen artefakt {ad})")


def korpus_kaynagi() -> pathlib.Path:
    """Korpusun İMAJDAKİ kopyası — `Dockerfile` `data/corpus/`'u repo köküne kopyalar.

    ⛔ HF'ten İNMEZ. Korpus zaten imajda; ikinci bir indirme kapısı açmak, kimliği iki
    yerde tutmak olurdu (S18'in ölçülmüş dersi).
    """
    return pathlib.Path(__file__).resolve().parent.parent / "data" / KORPUS_ALT / KORPUS_DOSYA


def indeks_hedefi(hedef_dizin) -> pathlib.Path:
    """İndeksin volume'deki yeri — künyedeki `../../corpus/…` bundan çözülür."""
    return pathlib.Path(hedef_dizin) / INDEKS_ALT / INDEKS_ADI


def korpus_hedefi(hedef_dizin) -> pathlib.Path:
    """Korpusun volume'deki yeri. `indeks_hedefi` ile birlikte repo düzenini aynalar."""
    return pathlib.Path(hedef_dizin) / KORPUS_ALT / KORPUS_DOSYA


def indir_model(hedef_dizin) -> pathlib.Path:
    """GGUF'u pinlenmiş revizyondan indirir, kapıdan geçirir, hedefe taşır.

    Yan etki: `hedef_dizin` oluşturulur ve içine tek dosya yazılır. Idempotent — hedefte
    dosya varsa yeniden indirilmez, ama YİNE DE kapıdan geçirilir (elle bozulmuş bir kopya
    sessizce kullanılmaz).
    """
    hedef_dizin = pathlib.Path(hedef_dizin)
    hedef_dizin.mkdir(parents=True, exist_ok=True)
    hedef = hedef_dizin / GGUF_DOSYA
    if hedef.exists():
        _kapidan_gecir(hedef, GGUF_BAYT, GGUF_SHA256, GGUF_DOSYA)
        return hedef

    gecici = pathlib.Path(tempfile.mkdtemp(dir=hedef_dizin, prefix=".indiriliyor-"))
    try:
        inen = _hf_indir(GGUF_DEPO, GGUF_DOSYA, GGUF_REVIZYON, gecici)
        _kapidan_gecir(inen, GGUF_BAYT, GGUF_SHA256, GGUF_DOSYA)
        os.replace(inen, hedef)      # aynı dosya sisteminde atomik
    finally:
        shutil.rmtree(gecici, ignore_errors=True)
    return hedef


def indir_indeks(hedef_dizin) -> pathlib.Path:
    """İndeksi hazırlar. İKİ YOLLU (ADR-0078 madde 4): volume öncelikli, HF yedek.

    Volume'de indeks varsa ona dokunulmaz — G8'in *"boyut kararı HF'te yaşar, imaj
    değişmez"* hükmü bu sırayla korunur. Depo tanımsızsa **erken patlar**: indekssiz ayağa
    kalkmak, ürünün kaynaksız cevap vermesi demektir ve `servis.py` bunu ölçülmüş bir kusur
    olarak yasaklar.
    """
    hedef_dizin = pathlib.Path(hedef_dizin)
    hedef = indeks_hedefi(hedef_dizin)
    if (hedef / "gomme.npy").exists():
        return hedef

    depo = os.environ.get(INDEKS_DEPO_ORTAM, "").strip()
    if not depo:
        raise KimlikHatasi(
            f"indeks volume'de yok ve {INDEKS_DEPO_ORTAM} tanımsız. Görev 8 (indeks dağıtımı) "
            f"bekletiliyor ⇒ yayımlanmış bir HF deposu yok; indeksi {hedef} yoluna elle koyun "
            f"(⚠️ dizin derinliği ZORUNLU — künye korpusu `../../corpus/` ile arar) ya da "
            f"{INDEKS_DEPO_ORTAM} ile depo adını verin")

    hedef.parent.mkdir(parents=True, exist_ok=True)
    gecici = pathlib.Path(tempfile.mkdtemp(dir=hedef.parent, prefix=".indeks-"))
    try:
        inen = _hf_indeks_indir(depo, gecici)
        if not (inen / "gomme.npy").exists():
            raise KimlikHatasi(f"{depo} deposunda gomme.npy yok — bu bir indeks deposu değil")
        os.replace(inen, hedef)
    finally:
        shutil.rmtree(gecici, ignore_errors=True)
    return hedef


def yerlestir_korpus(hedef_dizin) -> pathlib.Path:
    """Korpusu İMAJDAKİ kopyadan volume'e koyar ve **iki kopyanın `sha256`'sını eşitler**.

    ⚠️ **S18 · İKİNCİ KOPYA — bu kapının varlık sebebi.** Korpus artık hem imajda hem
    volume'de duruyor ve İKİ KOD YOLU ikisini ayrı ayrı okuyor: `hakhukuk.servis`
    `_varsayilan_araclar` içinde imajdakini (repo köküne göreli), `retriever` ise indeksin
    künyesinden çözdüğü volume'dekini. Bugün ikisi aynı dosyadan türüyor; ayrışırlarsa ürün
    iki farklı korpustan cevap verir ve bu HATA VERMEDEN yanlıştır. Ayrışma hâlinde
    `KimlikHatasi` → çıkış ≠ 0 ⇒ iki daemon da HİÇ başlamaz.

    Idempotent: hedefte dosya varsa yeniden kopyalanmaz, ama YİNE DE eşitlik sınanır.
    """
    kaynak = korpus_kaynagi()
    if not kaynak.exists():
        raise KimlikHatasi(f"korpus imajda bulunamadı: {kaynak} (Dockerfile `data/corpus/`'u "
                           "kopyalar — imaj yeniden kurulmalı)")
    bekleyen = _ozet(kaynak)
    hedef = korpus_hedefi(hedef_dizin)
    if hedef.exists():
        bulunan = _ozet(hedef)
        if bulunan != bekleyen:
            raise KimlikHatasi(
                f"volume'deki korpus imajdakinden AYRIŞMIŞ: {hedef} sha256 {bulunan[:12]} ≠ "
                f"{kaynak} sha256 {bekleyen[:12]} — `servis.py` ile `retriever` farklı "
                "korpuslardan cevap verirdi; volume'deki kopyayı silin ve yeniden koşun")
        return hedef

    hedef.parent.mkdir(parents=True, exist_ok=True)
    gecici = pathlib.Path(tempfile.mkdtemp(dir=hedef.parent, prefix=".korpus-"))
    try:
        ara = gecici / KORPUS_DOSYA
        shutil.copyfile(kaynak, ara)
        bulunan = _ozet(ara)
        if bulunan != bekleyen:
            raise KimlikHatasi(f"korpus kopyası bozuldu: sha256 {bulunan} ≠ {bekleyen}")
        os.replace(ara, hedef)
    finally:
        shutil.rmtree(gecici, ignore_errors=True)
    return hedef


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 1:
        print("kullanım: python -m hakhukuk.indir <hedef-dizin>", file=sys.stderr)
        return 2
    hedef_dizin = argv[0]
    try:
        gguf = indir_model(hedef_dizin)
        korpus = yerlestir_korpus(hedef_dizin)
        indeks = indir_indeks(hedef_dizin)
    except KimlikHatasi as hata:
        # ⛔ Sessiz düşme yok: çıkış ≠ 0 ⇒ compose iki daemon'u da HİÇ başlatmaz.
        print(f"KAPI TUTMADI: {hata}", file=sys.stderr)
        return 1
    print(f"model:  {gguf}")
    print(f"korpus: {korpus}")
    print(f"indeks: {indeks}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
