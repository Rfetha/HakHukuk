#!/usr/bin/env python3
"""recall@10'u KURULU indeksten ölç — dağıtılan artefaktın kapısı.

⚠️ `recall_olc.py` bu işi YAPMAZ: korpusu sıfırdan gömer (CPU'da ~2 sa 45 dk) ve
diskteki indekse hiç bakmaz. Yani bugüne kadar *"dağıtılan indeks doğru mu"* sorusu
ölçülemiyordu — ölçülen hep yeniden üretilmiş bir gömmeydi.

Ölçüldü 2026-09-09 (G8 Adım 1b verify'ı): repo başka bir dizine kopyalandı, korpusun
`mtime`'ı `git checkout` gibi tazelendi, indeks oradan yüklendi → **recall@10 0,9500
(76/80)** — yeniden gömerek ölçülen değerin BİREBİR aynısı, bağımsız çapraz kontrol.

Kullanım:
  python scripts/erisim_korpus/recall_indeksten.py
"""
import json, os, sys

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path[:0] = [os.path.join(KOK, "scripts", "erisim_korpus"), KOK]
from retriever import Retriever            # noqa: E402
from madde_anahtar import madde_anahtari   # noqa: E402

r = Retriever.yukle(os.path.join(KOK, "data/index/mevzuat_bge_m3_s2"))
dev = [json.loads(l) for l in open(os.path.join(KOK, "data/eval/dev/core_hard.jsonl"),
                                   encoding="utf-8") if l.strip()]
isabet = 0
for d in dev:
    altin = madde_anahtari(d["kanun_no"], d["madde_no"])
    getirilen = r.getir(d["messages"][0]["content"], k=10)
    if any(madde_anahtari(g["kanun_no"], g["madde_no"]) == altin for g in getirilen):
        isabet += 1
print(f"n={len(dev)} · isabet={isabet} · recall@10 = {isabet/len(dev):.4f}", flush=True)
