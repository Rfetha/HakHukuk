#!/usr/bin/env python3
"""G21 Adım 8 — "zayıf eşleşme" rozeti mümkün mü? Ölçüm, özellik değil.

Soru: recall@10'un KAÇIRDIĞI kalemler ile TUTTURDUĞU kalemlerin RRF skor
dağılımı ayrışıyor mu? Ayrışmıyorsa rozet EKLENMEZ (bkz. BULGU.md).

⛔ Eşik uydurulmaz — veriye bakmadan hiçbir sayı seçilmez. Bu script yalnız
ÖLÇER; hüküm BULGU.md'de, eldeki dağılıma bakılarak yazılır.

Retriever üretimde kullanılanın AYNISI: `scripts.erisim_korpus.retriever.Retriever`
(hibrit BM25+bge-m3, RRF_K=10, yürürlük süzgeci varsayılan AÇIK) — F0.2 künyesindeki
rejimle birebir (`data/index/mevzuat_bge_m3_s2`, k=10).

Kullanım:
  python scripts/erisim_korpus/zayif_eslesme_olc.py --out outputs/eval/g21-zayif-eslesme
"""
import argparse
import json
import os
import subprocess
import sys
import time

import numpy as np

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
from madde_anahtar import madde_anahtari  # noqa: E402
from retriever import Retriever  # noqa: E402

INDEKS = "data/index/mevzuat_bge_m3_s2"
DEV = "data/eval/dev/core_hard.jsonl"
K = 10
CIPA_RECALL_10 = 0.9500  # outputs/eval/f02-biz-onsozsuz/KUNYE.json (recall_at_10)


def dev_yukle(yol: str) -> list[dict]:
    return [json.loads(l) for l in open(yol, encoding="utf-8") if l.strip()]


def ozellikler(skorlar: list[float]) -> dict:
    """Aday ayrışım göstergeleri, ilk k RRF skorundan. Uydurma eşik yok — sadece ölçüm."""
    s = np.asarray(skorlar, dtype=np.float64)
    top1 = float(s[0])
    top2 = float(s[1]) if len(s) > 1 else float("nan")
    marj = top1 - top2 if len(s) > 1 else float("nan")
    ortalama = float(s.mean())
    std = float(s.std())
    yayilim = float(s.max() - s.min())
    p = s / s.sum() if s.sum() > 0 else np.full_like(s, 1.0 / len(s))
    entropi = float(-np.sum(p * np.log(p + 1e-12)))
    return {
        "top1_skor": top1, "top2_skor": top2, "marj_1_2": marj,
        "ortalama_skor": ortalama, "std_skor": std, "yayilim": yayilim,
        "entropi": entropi,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--indeks", default=INDEKS)
    p.add_argument("--dev", default=DEV)
    p.add_argument("-k", type=int, default=K)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    komut_satiri = "python " + " ".join(sys.argv)

    os.makedirs(a.out, exist_ok=True)
    dev = dev_yukle(a.dev)
    print(f"[g21] DEV {len(dev)} kalem · indeks={a.indeks} · k={a.k}", flush=True)

    t0 = time.time()
    retriever = Retriever.yukle(a.indeks, cihaz="cpu")
    print(f"[g21] indeks yüklendi ({time.time()-t0:.1f} sn)", flush=True)

    kayitlar = []
    for i, d in enumerate(dev):
        soru = d["messages"][0]["content"]
        altin = madde_anahtari(d["kanun_no"], d["madde_no"])
        sonuclar = retriever.getir(soru, k=a.k)
        skorlar = [r["skor"] for r in sonuclar]
        altin_sira = None
        for r in sonuclar:
            if madde_anahtari(r["kanun_no"], r["madde_no"]) == altin:
                altin_sira = r["sira"]
                break
        kayit = {
            "index": i, "soru": soru,
            "kanun_no": d["kanun_no"], "madde_no": d["madde_no"],
            "altin_sira": altin_sira,
            "isabet_10": altin_sira is not None,
            "skorlar_top_k": skorlar,
            **ozellikler(skorlar),
        }
        kayitlar.append(kayit)
        if (i + 1) % 20 == 0:
            print(f"[g21]  {i+1}/{len(dev)}", flush=True)

    gecen = time.time() - t0
    isabet = sum(1 for k_ in kayitlar if k_["isabet_10"])
    recall10 = isabet / len(kayitlar)
    print(f"[g21] recall@{a.k} ölçülen = {recall10:.4f} ({isabet}/{len(kayitlar)}) "
          f"· çıpa = {CIPA_RECALL_10:.4f}", flush=True)

    skorlar_yolu = os.path.join(a.out, "skorlar_80.json")
    json.dump(kayitlar, open(skorlar_yolu, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    repo_koku = os.path.dirname(_K)
    # ⚠️ Sessiz `null` YASAK: künyede boş bir alan "commit alınamadı" ile "commit yok"u
    # aynı şeye çevirirdi ve künyeyi okuyan rejimi doğrulayamazdı. Hata YAKALANIR ama
    # GÖRÜNÜR kılınır — alana nedeni yazılır ve ekrana uyarı basılır.
    try:
        retriever_commit = subprocess.check_output(
            ["git", "log", "-1", "--format=%H", "--", "scripts/erisim_korpus/retriever.py"],
            cwd=repo_koku, stderr=subprocess.PIPE,
        ).decode().strip() or "BOŞ: git bu dosya için kayıt döndürmedi"
    except (OSError, subprocess.CalledProcessError) as hata:
        retriever_commit = f"ALINAMADI: {type(hata).__name__}: {hata}"
        print(f"[g21] ⚠️ retriever commit'i alınamadı — künyeye NEDENİ yazılıyor: {hata}",
              flush=True)

    kunye = {
        "tarih": time.strftime("%Y-%m-%d"),
        "indeks": a.indeks,
        "k": a.k,
        "rrf_k": "modül sabiti RRF_K=10 (retriever.py, ADR-0068) — indeksin KUNYE.json'undaki "
                 "rrf_k=60 kur-zamanı METADATA'dır, sorgu ANINDA kullanılmaz",
        "yururluk_suzgeci": "Yururluk.YALNIZ_YURURLUKTE (varsayılan)",
        "dev": a.dev, "n": len(dev),
        "retriever_dosya_commit": retriever_commit,
        "komut_satiri": komut_satiri,
        "recall_at_10_olculen": round(recall10, 4),
        "recall_at_10_cipa": CIPA_RECALL_10,
        "cipa_tutuyor_mu": abs(recall10 - CIPA_RECALL_10) < 1e-9,
        "hic_bulunmayan": len(kayitlar) - isabet,
        "gecen_sure_s": round(gecen, 1),
        "kaynak_cipa": "outputs/eval/f02-biz-onsozsuz/KUNYE.json (recall_at_10) · "
                       "docs/record/kronoloji-63-71.md#65",
    }
    json.dump(kunye, open(os.path.join(a.out, "KUNYE.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"[g21] → {skorlar_yolu}", flush=True)
    print(f"[g21] → {os.path.join(a.out, 'KUNYE.json')}", flush=True)


if __name__ == "__main__":
    sys.exit(main())
