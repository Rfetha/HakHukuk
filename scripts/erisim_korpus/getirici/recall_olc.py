#!/usr/bin/env python3
"""S3a ön-prob — retriever altın maddeyi bulabiliyor mu? `recall@k`.

Model çağrısı YOK, hakem YOK, GPU YOK. Altın etiket zaten elimizde: DEV soruları
maddelerden üretildi.

⛔ ÖN-KAYITLI EŞİKLER (sayı görülmeden yazıldı, değiştirilemez):
   recall@10 ≥ %90   → S3 planı aynen koşar
   recall@10 %70-90  → hibrit (BM25 + yoğun) eklenir, S3 büyür
   recall@10 < %70   → DUR, insana sor — sorun korpus yapısında

Kullanım:
  python scripts/erisim_korpus/getirici/recall_olc.py --yontem bm25 --out outputs/eval/sprint2-olcum/s3a-on-prob
  python scripts/erisim_korpus/getirici/recall_olc.py --yontem yogun --model intfloat/multilingual-e5-base --out ...
"""
import argparse
import json
import os
import sys
import time
from collections import defaultdict

# ── scripts/ yol köprüsü (T5 2026-09-07 · ADR-0112 2026-10-16) ───────────────
# Kardeş modüller iç içe alt klasörlerde de bulunsun diye scripts/ kökü, altındaki HER
# derinlikteki klasör ve repo kökü sys.path'e girer. Uzantısız `import X` bu köprü olmadan
# taşımada SESSİZCE kırılır: ImportError çalışma zamanında, bazen GPU koşusunun ortasında.
# ⚠️ 39 dosyada BİREBİR aynı; değiştirirsen hepsinde değiştir (grep: "yol köprüsü").
import os, sys
_K = os.path.abspath(__file__)
_K = _K[:_K.rindex(os.sep + "scripts" + os.sep)] + os.sep + "scripts"  # dışarıda: ValueError
_Y = []
for _y, _alt, _f in os.walk(_K):
    _alt[:] = sorted(_a for _a in _alt if _a[0] not in "_.")
    _Y.append(_y)
sys.path[:0] = [*_Y, os.path.dirname(_K)]
# ─────────────────────────────────────────────────────────────────────────────
from hakhukuk.cekirdek.madde_anahtar import madde_anahtari, korpus_indeksi  # noqa: E402,F401

KORPUS = "data/corpus/mevzuat_maddeler.jsonl"
DEV = "data/eval/dev/core_hard.jsonl"
KLER = (1, 5, 10, 20)


def recall_at_k(siralar: list, k: int) -> float:
    """Altının ilk k içinde geldiği oran. `sira=None` → hiç gelmedi."""
    if not siralar:
        return 0.0
    return sum(1 for s in siralar if s is not None and s < k) / len(siralar)


def korpus_yukle():
    kayitlar = [json.loads(l) for l in open(KORPUS, encoding="utf-8") if l.strip()]
    anahtarlar = [madde_anahtari(r["kanun_no"], r["madde_no"]) for r in kayitlar]
    # Gömülecek metin: kanun adı + madde no + gövde. Kanun adı ayırt edici bir sinyal.
    metinler = [f"{r['kanun_adi']} {r['madde_no']} {r['text']}" for r in kayitlar]
    return kayitlar, anahtarlar, metinler


def dev_yukle():
    dev = [json.loads(l) for l in open(DEV, encoding="utf-8") if l.strip()]
    sorular = [d["messages"][0]["content"] for d in dev]
    altinlar = [madde_anahtari(d["kanun_no"], d["madde_no"]) for d in dev]
    return sorular, altinlar


def skorla_bm25(metinler, sorular):
    from rank_bm25 import BM25Okapi
    bm25 = BM25Okapi([m.lower().split() for m in metinler])
    return [bm25.get_scores(s.lower().split()) for s in sorular]


def skorla_yogun(metinler, sorular, model_adi, cihaz="cpu"):
    from sentence_transformers import SentenceTransformer
    # Why: recall@k CİHAZDAN BAĞIMSIZ bir sayı; --cihaz yalnız indeksleme süresini
    # değiştirir. "Harness CPU'da" değişmezi SERVİS anını korur (GPU'da model durur),
    # bir kerelik çevrimdışı indeks kurmayı değil. Ölçüldü: CPU ~4,1 madde/sn →
    # 40.496 madde ≈ 2s45d/model; GPU'da dakikalar.
    model = SentenceTransformer(model_adi, device=cihaz)
    # Why: karşılaştırma değişmezi. e5 doğal olarak 512 token, bge-m3 8192 —
    # sabitlemezsek "hangi model daha iyi" ile "hangisi daha çok metin gördü"
    # karışır ve fark hiçbir yerde görünmez. 512 token, eval-ayna 900 karakter
    # kırpmasını (ADR-0011) rahatça kapsıyor.
    model.max_seq_length = 512
    # Why: e5 ailesi `query:`/`passage:` önekiyle EĞİTİLDİ. Öneksiz koşmak hata
    # vermez, yalnızca e5'i sistematik olarak düşük gösterir — K1 kararı bu
    # sayıyla veriliyor. bge-m3 önek istemez.
    q_on, p_on = ("query: ", "passage: ") if "e5" in model_adi.lower() else ("", "")
    K = model.encode([p_on + m for m in metinler], batch_size=32, normalize_embeddings=True,
                     show_progress_bar=True, convert_to_numpy=True)
    S = model.encode([q_on + s for s in sorular], normalize_embeddings=True,
                     convert_to_numpy=True)
    return [S[i] @ K.T for i in range(len(sorular))]


def skorla_hibrit(metinler, sorular, model_adi, cihaz="cpu", rrf_k=60):
    """BM25 + yoğun füzyon, Reciprocal Rank Fusion.

    RRF seçildi çünkü BM25 skorları (sınırsız) ile kosinüs benzerliği (-1..1)
    aynı ölçekte değil; ham toplam BM25'e ağırlık verir ve bu ağırlık hiçbir
    yerde görünmez. RRF yalnız SIRAYI kullanır, ölçek sorununu ortadan kaldırır.
    """
    bm = skorla_bm25(metinler, sorular)
    yg = skorla_yogun(metinler, sorular, model_adi, cihaz)
    return [rrf_birlestir([bm[i], yg[i]], rrf_k) for i in range(len(sorular))]


def rrf_birlestir(skor_listeleri, rrf_k=60):
    """Tek soru için RRF: her skor dizisini sıraya çevir, 1/(k+sıra) topla.

    ⚠️ Sıra hesabı sessizce ters dönebilir — testle çivilendi.
    """
    import numpy as np
    n = len(skor_listeleri[0])
    toplam = np.zeros(n, dtype=np.float32)
    for s in skor_listeleri:
        sira = np.empty(n, dtype=np.int64)
        sira[np.argsort(s)[::-1]] = np.arange(n)  # en yüksek skor → sıra 0
        toplam += 1.0 / (rrf_k + sira + 1)
    return toplam


def en_iyiler(skorlar, adaylar, en_fazla):
    """Skorlardan ilk `en_fazla` aday indeksi. `adaylar=None` → tüm korpus.

    Kapsam daraltma burada yapılır, skorlamada değil: oracle-kanun ölçümü
    aynı skorları farklı aday havuzunda okur, yeniden skorlamaz.
    """
    import numpy as np
    if adaylar is None:
        return np.argsort(skorlar)[::-1][:en_fazla]
    adaylar = np.asarray(adaylar)
    return adaylar[np.argsort(skorlar[adaylar])[::-1][:en_fazla]]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--yontem", choices=["bm25", "yogun", "hibrit"], required=True)
    p.add_argument("--model", default="intfloat/multilingual-e5-base",
                   help="yalnız --yontem yogun için")
    p.add_argument("--cihaz", default="cpu", choices=["cpu", "cuda"],
                   help="yalnız indeksleme hızını değiştirir; recall cihazdan bağımsız")
    p.add_argument("--kapsam", default="korpus", choices=["korpus", "kanun"],
                   help="kanun = aday havuzu altının kendi kanunuyla sınırlı (oracle-kanun tanısı)")
    p.add_argument("--out", required=True)
    a = p.parse_args()

    os.makedirs(a.out, exist_ok=True)
    kayitlar, anahtarlar, metinler = korpus_yukle()
    sorular, altinlar = dev_yukle()
    print(f"[s3a] korpus {len(kayitlar):,} madde · DEV {len(sorular)} soru · "
          f"yöntem={a.yontem} · kapsam={a.kapsam}", flush=True)

    en_fazla = max(KLER)
    t0 = time.time()
    if a.yontem == "bm25":
        skorlar = skorla_bm25(metinler, sorular)
        etiket = "bm25"
    elif a.yontem == "hibrit":
        skorlar = skorla_hibrit(metinler, sorular, a.model, a.cihaz)
        etiket = "hibrit_bm25+" + a.model.replace("/", "_")
    else:
        skorlar = skorla_yogun(metinler, sorular, a.model, a.cihaz)
        etiket = a.model.replace("/", "_")
    gecen = time.time() - t0

    if a.kapsam == "kanun":
        etiket += "_kanunkapsam"
        kanun_adaylari = defaultdict(list)
        for ix, r in enumerate(kayitlar):
            kanun_adaylari[str(r["kanun_no"]).strip()].append(ix)
        sirali = [en_iyiler(skorlar[i], kanun_adaylari[altinlar[i][0]], en_fazla)
                  for i in range(len(sorular))]
    else:
        sirali = [en_iyiler(skorlar[i], None, en_fazla) for i in range(len(sorular))]

    # Altının kaçıncı sırada geldiği. Aynı anahtarda birden çok kayıt olabilir
    # (mükerrer/tadil) — HERHANGİ birine isabet sayılır.
    siralar = []
    for i, altin in enumerate(altinlar):
        sira = None
        for yer, ix in enumerate(sirali[i]):
            if anahtarlar[ix] == altin:
                sira = yer
                break
        siralar.append(sira)

    # Kanun-düzeyi recall: ilk k maddenin KANUNLARI arasında altının kanunu var mı.
    # İki aşamalı retriever (kanun seç → madde seç) uygulanabilir mi sorusunu bu
    # yanıtlıyor; madde-düzeyi recall'un neyi kaçırdığını ayırır.
    kanun_siralari = []
    for i, altin in enumerate(altinlar):
        sira = None
        for yer, ix in enumerate(sirali[i]):
            if str(kayitlar[ix]["kanun_no"]).strip() == altin[0]:
                sira = yer
                break
        kanun_siralari.append(sira)

    sonuc = {
        "yontem": etiket, "n": len(sorular), "korpus": len(kayitlar),
        # Why: hibrit de gömme koşturur. Koşul `== "yogun"` iken hibrit künyeye
        # `cpu` yazıyordu — künyeye yanlış yazılan parametre, koşulmamış sayılır (6.12).
        "cihaz": "cpu" if a.yontem == "bm25" else a.cihaz,
        "recall": {f"recall@{k}": round(recall_at_k(siralar, k), 4) for k in KLER},
        "kanun_recall": {f"kanun_recall@{k}": round(recall_at_k(kanun_siralari, k), 4)
                         for k in KLER},
        "hic_bulunmayan": sum(1 for s in siralar if s is None),
        "gecen_sure_s": round(gecen, 1),
        "esik_karari": None,  # aşağıda dolduruluyor
    }
    r10 = sonuc["recall"]["recall@10"]
    sonuc["esik_karari"] = (
        "PLAN AYNEN" if r10 >= 0.90 else
        "HIBRIT GEREKIR" if r10 >= 0.70 else
        "DUR — INSANA SOR"
    )
    yol = os.path.join(a.out, f"recall_{etiket}.json")
    json.dump(sonuc, open(yol, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps(sonuc, ensure_ascii=False, indent=2))
    print(f"[s3a] → {yol}", flush=True)


if __name__ == "__main__":
    main()
