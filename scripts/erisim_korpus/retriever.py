#!/usr/bin/env python3
"""Harness'ın retriever'ı — hibrit (BM25 + yoğun gömme, RRF), kalıcı indeksli.

S3a ön-probu (research_log #49) yöntemi **ölçerek** seçti:

    yöntem                         recall@10   recall@20
    BM25                             0,625       0,750
    multilingual-e5-base             0,700       0,750
    BAAI/bge-m3                      0,800       0,863
    hibrit (BM25 + bge-m3, RRF)      0,875       0,925   ← bu (RRF_K=60, soru seti v1)

    ⚠️ 2026-09-06: iki şey değişti, ESKİ SATIR SİLİNMEDİ — damgalandı.
    Soru seti v2 (KUNYE_soru_onarimi_2026-09-06.json) + RRF_K 60→10 (ADR-0068):
    hibrit, DEV-v2, RRF_K=10        r@10 0,9500   r@5 0,8250   r@1 0,5500
    Aynı indeks, aynı korpus. Yukarıdaki 0,875 v1 soru setinin sayısıdır ve
    v2 ile KIYASLANMAZ.

⚠️ **Chunk = TAM MADDE** (ADR-0054/K2). Eval-ayna kuralının 900 karakter kırpması
retriever'da **uygulanmaz**; bağlam modele verilirken uygulanır — kuralın öznesi
modelin girdisi, indeks değil. İndeksi kırpmak uzun maddelerin sonundaki hükümleri
aranamaz yapardı.

⚠️ **Harness GPU'ya girmez** (sprint3 değişmezi). `--cihaz cuda` yalnız **bir kerelik
indeks kurulumunu** hızlandırır; sorgu anında gömme CPU'da milisaniyeler, kaba kuvvet
arama 40.496 madde için **8,2 ms** ve indeks fp16'da **83 MB** — bu ölçekte ANN indeksi
de vektör veritabanı da gerekmiyor (research_log #49 §7).

Kullanım:
  python scripts/erisim_korpus/retriever.py kur   --korpus data/corpus/mevzuat_maddeler.jsonl \\
                                    --indeks data/index/mevzuat_bge_m3 --cihaz cuda
  python scripts/erisim_korpus/retriever.py sorgu --indeks data/index/mevzuat_bge_m3 \\
                                    --soru "İşe iade davası ne zaman açılır?" -k 5
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

MODEL = "BAAI/bge-m3"
AZAMI_TOKEN = 512   # kıyas değişmezi (research_log #49 §4.2) — modeller arası eşitlenir
RRF_K = 10   # ADR-0068 (2026-09-06): 60 → 10.
# Why: RRF_K=60 çok-sistemli füzyon için varsayılandır. İKİ kollu ve kolları çok farklı
# davranan bu sistemde "iki kolda vasat" olanı "bir kolda mükemmel" olana tercih ediyordu:
# k=60'ta 0. sıra + 97. sıra = 1/60 + 1/157 = 0,0231 < iki kolda 5. sıra = 2/65 = 0,0308.
# Ölçüldü (DEV-v2, n=80): k=60'ta altını YOĞUN kol 0. sırada bulduğu kalem (id 79) ve
# BM25 kolun 0. sırada bulduğu kalem (id 12) ilk 10'un DIŞINA itiliyordu.
# Seçim gerekçesi PLATO, sivrilik değil: r@5 = 0,8250 k∈[5,20] boyunca sabit (k=30'da
# 0,8125, k=60'ta 0,7875); k=10 o platonun ORTASI. r@10'daki fazladan kalem BONUSTUR.
# Seçim DEV'de yapıldı; doğrulaması donmuş TEST'tedir.

# Önek sözleşmesi. `bge-m3` sorgu/belge öneki ALMAZ — gömülen metin `_gomulecek_metin`'in
# ürettiğinin AYNISIDIR, sorgu da çıplak gider.
# Why künyeye yazılıyor: E5 ailesi "query: "/"passage: " ister ve önek DÜŞERSE hiçbir hata
# çıkmaz, yalnız recall düşer. İndeksi başka bir makinede/kodla kullanan, sorguyu hangi
# sözleşmeyle kodlayacağını künyeden okur; `yukle` kodun bugünkü sözleşmesiyle karşılaştırır.
ONEK = {"sorgu": "", "belge": ""}


# ── scripts/ yol köprüsü (T5, 2026-09-07) ────────────────────────────────────
# Kardeş modüller alt klasörlere bölündükten SONRA da bulunsun diye scripts/ kökü, tüm
# alt klasörleri ve repo kökü sys.path'e girer. Uzantısız `import X` bu köprü olmadan
# taşımada SESSİZCE kırılır: ImportError çalışma zamanında, bazen GPU koşusunun ortasında.
# ⚠️ 26 dosyada BİREBİR aynı; değiştirirsen hepsinde değiştir (grep: "yol köprüsü").
import os, sys
_K = os.path.dirname(os.path.abspath(__file__))
_K = _K if os.path.basename(_K) == "scripts" else os.path.dirname(_K)
sys.path[:0] = [_K, *(os.path.join(_K, _d) for _d in sorted(os.listdir(_K))
                      if os.path.isdir(os.path.join(_K, _d)) and _d[0] not in "_."),
                os.path.dirname(_K)]
# ─────────────────────────────────────────────────────────────────────────────

from hakhukuk.cekirdek.tipler import Yururluk


def rrf_birlestir(skor_listeleri, rrf_k=RRF_K):
    """Tek sorgu için RRF: her skor dizisini sıraya çevir, 1/(k+sıra) topla.

    Why RRF, ham toplam değil: BM25 skoru sınırsız, kosinüs −1..1. Ham toplam
    BM25'e **görünmeyen** bir ağırlık verir. RRF yalnız sırayı kullanır.
    ⚠️ Sıra hesabı sessizce ters dönebilir — testle çivilendi.
    """
    n = len(skor_listeleri[0])
    toplam = np.zeros(n, dtype=np.float32)
    for s in skor_listeleri:
        sira = np.empty(n, dtype=np.int64)
        sira[np.argsort(s)[::-1]] = np.arange(n)   # en yüksek skor → sıra 0
        toplam += 1.0 / (rrf_k + sira + 1)
    return toplam


def _korpus_imzasi(yol: str, indeks_dizini: str) -> dict:
    """Korpusun TAŞINABİLİR kimliği: indekse göreli yol + içerik hash'i.

    ⚠️ Ne mutlak yol ne `mtime` — ikisi de makineye bağlıdır. `git clone`/`checkout`
    mtime'ı içeriğe dokunmadan değiştirir; 2026-08-06'da bu tam olarak oldu ve
    yanlış alarm verdi (o gün elle düzeltildi, kök neden burada kapanıyor).
    """
    ham = open(yol, "rb").read()
    return {"yol": os.path.relpath(os.path.abspath(yol), os.path.abspath(indeks_dizini)),
            "bayt": len(ham), "sha256": hashlib.sha256(ham).hexdigest()}


def _korpus_yolu(indeks_dizini: str, imza: dict) -> str:
    return os.path.normpath(os.path.join(indeks_dizini, imza["yol"]))


# ── Korpus KİMLİKLE bulunur (ADIM 6.1, kusur 32) ─────────────────────────────
# İndeks HF'ten dataset olarak inince indeks dizininin İKİ ÜSTÜNDE `corpus/` OLMAYACAK
# — künyedeki göreli yol tek başına artık yeterli değil. Çözüm merdiveni SIRAYLA:
#   (a) HAKHUKUK_KORPUS ortam değişkeni — açık geçersiz kılma, tanımlıysa YALNIZ o denenir
#   (b) künyedeki göreli yol — bugünkü davranış, DEĞİŞMEDİ
#   (c) bilinen köklerde sha256 ile arama — (b) çözülemediğinde devreye girer
# Her basamakta sha256 doğrulanır; tutmayan aday atlanır (yerleşim değil, KİMLİK bağlar).
_KORPUS_ORTAM_DEGISKENI = "HAKHUKUK_KORPUS"
_KORPUS_DOSYA_ADI = "mevzuat_maddeler.jsonl"
_REPO_KOKU = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _korpus_hash_tutuyor_mu(yol: str, beklenen_sha256: str) -> bool:
    return os.path.exists(yol) and hashlib.sha256(open(yol, "rb").read()).hexdigest() == beklenen_sha256


def _bilinen_kokler(indeks_dizini: str) -> list[str]:
    """(c) basamağının SIRAYLA arayacağı kökler. Kök 1 = (b), burada TEKRAR denenmez."""
    return [
        os.path.normpath(os.path.join(indeks_dizini, "..", "corpus")),
        os.path.normpath(os.path.join(indeks_dizini, "corpus")),
        os.path.join(_REPO_KOKU, "data", "corpus"),
        os.path.join(_REPO_KOKU, "hakhukuk", "veri"),
    ]


def _korpus_bul(indeks_dizini: str, imza: dict) -> str:
    """Korpusu bul: (a) ortam değişkeni → (b) göreli yol → (c) bilinen köklerde kimlikle arama.

    ⚠️ (b) adayı VAR ama sha256 tutmuyorsa arama SÜRMEZ — bu, bayat indeksi yakalayan
    kapıdır (kural 3) ve "korpus DEĞİŞTİ" der. Dosya HİÇ yoksa (c)'ye geçilir.
    """
    ortam = os.environ.get(_KORPUS_ORTAM_DEGISKENI)
    if ortam:
        if _korpus_hash_tutuyor_mu(ortam, imza["sha256"]):
            return ortam
        raise SystemExit(
            f"[retriever] 🚫 {_KORPUS_ORTAM_DEGISKENI}={ortam} — dosya yok ya da sha256 "
            f"tutmuyor; açık geçersiz kılma olduğu için YALNIZ bu yol denendi, arama sürmedi")

    b_yolu = _korpus_yolu(indeks_dizini, imza)
    if os.path.exists(b_yolu):
        if _korpus_hash_tutuyor_mu(b_yolu, imza["sha256"]):
            return b_yolu
        simdi = _korpus_imzasi(b_yolu, indeks_dizini)
        raise SystemExit(
            f"[retriever] 🚫 korpus indeks kurulduğundan beri DEĞİŞTİ "
            f"({imza['bayt']}→{simdi['bayt']} bayt, sha256 {imza['sha256'][:12]}→"
            f"{simdi['sha256'][:12]}) — indeks bayat, yeniden kur:\n"
            f"   python scripts/erisim_korpus/retriever.py kur --korpus {b_yolu} "
            f"--indeks {indeks_dizini}")

    denenen = [b_yolu]
    for kok in _bilinen_kokler(indeks_dizini):
        aday = os.path.join(kok, _KORPUS_DOSYA_ADI)
        if _korpus_hash_tutuyor_mu(aday, imza["sha256"]):
            return aday
        denenen.append(aday)

    raise SystemExit(
        "[retriever] 🚫 korpus hiçbir bilinen yolda bulunamadı (kimlik: sha256 "
        f"{imza['sha256'][:12]}…) — denenen yollar:\n" +
        "\n".join(f"   {y}" for y in denenen))


def _model_revizyonu(model_adi: str) -> str | None:
    """Modelin yerel HF önbelleğindeki commit'i. Bilinmiyorsa `None` — uydurulmaz."""
    from huggingface_hub.constants import HF_HUB_CACHE
    ref = os.path.join(HF_HUB_CACHE, "models--" + model_adi.replace("/", "--"),
                       "refs", "main")
    return open(ref).read().strip() if os.path.exists(ref) else None


def _gomulecek_metin(r: dict) -> str:
    """Kanun adı ayırt edici bir sinyal — madde gövdesiyle birlikte gömülür."""
    return f"{r['kanun_adi']} {r['madde_no']} {r['text']}"


def bge_gomucu(cihaz: str = "cpu", model_adi: str = MODEL):
    """Gerçek gömücü. `Retriever.kur`'a geçirilir; testler sahte gömücü verir."""
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(model_adi, device=cihaz)
    model.max_seq_length = AZAMI_TOKEN

    def kodla(metinler):
        return model.encode(metinler, batch_size=32, normalize_embeddings=True,
                            convert_to_numpy=True, show_progress_bar=len(metinler) > 1000)
    return kodla


class Retriever:
    """Hibrit retriever. Arayüz üç şey: `kur` · `yukle` · `getir`.

    BM25 indeksi yüklemede yeniden kuruluyor (40.496 madde için ~10 sn) — diske
    yazılan yalnız gömme matrisi, çünkü pahalı olan o.
    """

    def __init__(self, kayitlar, gomme, kunye, gomucu=None, cihaz="cpu"):
        self._kayitlar = kayitlar
        self._gomme = gomme.astype(np.float32)
        self._kunye = kunye
        self._gomucu = gomucu
        self._cihaz = cihaz
        # Yürürlük maskesi bir kez kurulur: her sorguda 40.496 kaydı taramak
        # sessizce çalışır, yalnız yavaştır.
        self._mulga = np.array([bool(r.get("mulga")) for r in kayitlar])
        from rank_bm25 import BM25Okapi
        self._bm25 = BM25Okapi([_gomulecek_metin(r).lower().split() for r in kayitlar])

    def _kodla(self, metinler):
        # Why tembel + tek sefer: gömme modeli ~2 GB ve yüklenmesi saniyeler sürüyor.
        # Her sorguda kurmak sessizce çalışır, yalnız 100× yavaştır.
        if self._gomucu is None:
            self._gomucu = bge_gomucu(self._cihaz, self._kunye["model"])
        return self._gomucu(metinler)

    @staticmethod
    def kur(korpus_yolu: str, indeks_dizini: str, gomucu=None,
            model_adi: str = MODEL, cihaz: str = "cpu") -> None:
        """Korpusu göm ve indeksi diske yaz. Bir kerelik; sorgu anında çağrılmaz."""
        kayitlar = [json.loads(l) for l in open(korpus_yolu, encoding="utf-8") if l.strip()]
        gomucu = gomucu or bge_gomucu(cihaz, model_adi)
        gomme = gomucu([_gomulecek_metin(r) for r in kayitlar]).astype(np.float16)

        os.makedirs(indeks_dizini, exist_ok=True)
        np.save(os.path.join(indeks_dizini, "gomme.npy"), gomme)
        kunye = {
            "yontem": "hibrit_bm25+yogun_rrf", "rrf_k": RRF_K,
            "model": model_adi, "max_seq_length": AZAMI_TOKEN,
            "chunk": "tam madde (ADR-0054/K2)",
            "gomulen_metin": "kanun_adi + madde_no + text",
            "n": len(kayitlar), "boyut": int(gomme.shape[1]),
            "korpus": _korpus_imzasi(korpus_yolu, indeks_dizini),
            "onek": ONEK,
            "model_revision": _model_revizyonu(model_adi),
            "secim_gerekcesi": "S3a ön-probu, research_log #49 — recall@10 0,875",
        }
        json.dump(kunye, open(os.path.join(indeks_dizini, "KUNYE.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        print(f"[retriever] indeks → {indeks_dizini} · {len(kayitlar):,} madde · "
              f"{gomme.nbytes / 1e6:.0f} MB", flush=True)

    @staticmethod
    def yukle(indeks_dizini: str, gomucu=None, cihaz: str = "cpu") -> "Retriever":
        """İndeksi yükle. Korpus değiştiyse ERKEN patlar — bayat indeks sessiz yanlışlıktır."""
        kunye = json.load(open(os.path.join(indeks_dizini, "KUNYE.json"), encoding="utf-8"))
        imza = kunye["korpus"]
        if "sha256" not in imza:
            raise SystemExit(
                f"[retriever] 🚫 {indeks_dizini}/KUNYE.json eski biçim (mutlak yol + mtime) "
                f"— taşınabilir değil, yeniden kur (G8 Adım 1b)")
        if kunye.get("onek") != ONEK:
            raise SystemExit(
                f"[retriever] 🚫 önek sözleşmesi uyuşmuyor: indeks {kunye.get('onek')} ↔ "
                f"kod {ONEK} — sorgu bu indeksin kodlandığı gibi kodlanmıyor, recall SESSİZCE "
                f"düşer; indeksi yeniden kur")
        korpus_yolu = _korpus_bul(indeks_dizini, imza)
        kayitlar = [json.loads(l) for l in open(korpus_yolu, encoding="utf-8") if l.strip()]
        gomme = np.load(os.path.join(indeks_dizini, "gomme.npy"))
        if len(kayitlar) != gomme.shape[0]:
            raise SystemExit(f"[retriever] 🚫 korpus {len(kayitlar)} kayıt, gömme "
                             f"{gomme.shape[0]} satır — indeks tutarsız")
        return Retriever(kayitlar, gomme, kunye, gomucu, cihaz)

    def getir(self, soru: str, k: int = 10,
              yururluk: Yururluk = Yururluk.YALNIZ_YURURLUKTE) -> list[dict]:
        """Soruya en uygun k maddeyi sırayla döndür. Metin **kırpılmadan** gelir (K2).

        ⚠️ Varsayılan olarak YÜRÜRLÜKTEN KALKMIŞ maddeler elenir. Ölçüldü 2026-09-07:
        süzgeç yokken 800 getirilen kaynağın 2'si mülgaydı (id 7 · 63) ve vatandaşa
        gidiyordu. Süzülen kayıt kaybolmaz — `MULGA_DAHIL` ile açıkça istenebilir; ve
        dönen her kayıt `mulga` alanını taşır ki ürün rozet gösterebilsin.
        """
        q = self._kodla([soru]).astype(np.float32)[0]
        if q.shape[0] != self._gomme.shape[1]:
            raise SystemExit(f"[retriever] 🚫 gömme boyutu uyuşmuyor: sorgu {q.shape[0]}, "
                             f"indeks {self._gomme.shape[1]} — indeks {self._kunye['model']} "
                             f"ile kuruldu, başka bir modelle sorgulanıyor")
        skor = rrf_birlestir([self._bm25.get_scores(soru.lower().split()), q @ self._gomme.T])
        sirali = np.argsort(skor)[::-1]
        if yururluk is Yururluk.YALNIZ_YURURLUKTE:
            # ⚠️ Skoru -inf yapmak YETMEZ: yürürlükteki kayıt sayısı k'dan azsa mülga
            # yine listeye girer (testle yakalandı). Eleme yapılır, bastırma değil.
            sirali = sirali[~self._mulga[sirali]]
        ilk = sirali[:k]
        return [dict(self._kayitlar[ix], skor=float(skor[ix]), sira=yer)
                for yer, ix in enumerate(ilk)]


def main():
    p = argparse.ArgumentParser()
    alt = p.add_subparsers(dest="komut", required=True)
    a = alt.add_parser("kur")
    a.add_argument("--korpus", required=True)
    a.add_argument("--indeks", required=True)
    a.add_argument("--model", default=MODEL)
    a.add_argument("--cihaz", default="cpu", choices=["cpu", "cuda"],
                   help="yalnız indeks kurulumunu hızlandırır; sorgu anı CPU")
    b = alt.add_parser("sorgu")
    b.add_argument("--indeks", required=True)
    b.add_argument("--soru", required=True)
    b.add_argument("-k", type=int, default=5)
    x = p.parse_args()

    if x.komut == "kur":
        Retriever.kur(x.korpus, x.indeks, model_adi=x.model, cihaz=x.cihaz)
    else:
        for r in Retriever.yukle(x.indeks).getir(x.soru, x.k):
            print(f"[{r['sira']}] {r['skor']:.5f}  {r['kanun_adi']} {r['madde_no']}")
            print(f"      {r['text'][:160].replace(chr(10), ' ')}")


if __name__ == "__main__":
    sys.exit(main())
