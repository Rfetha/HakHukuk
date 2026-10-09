#!/usr/bin/env python3
"""CP2 — kabul edilen `rejected` adaylarının DENETİMİ (LLM red hakemi ile).

Neden gerekli: ADR-0042'nin kabul ölçütü **regex** (`exact_reject` RED saymıyor), ama ARA KAPI'nın
ve bütün M2/M2b tablolarının okuduğu sayı **LLM hakemi** (`rejection_rate`). CP0.9'da ikisi
arasındaki fark base M2'de **0.61 → 0.814 = 20 puan** ölçülmüştü (tuzak 2.5). Yani regexin
"fabrikasyon" dediği bir cevap, hakemin ABSTAIN dediği bir cevap olabilir — ve o örnek ORPO'da
`rejected` olarak kullanılırsa modele **çekinmeyi cezalandırmak** öğretilir.

Bu betik kabul edilen adayları hakemin şemasına çevirir; puanlama `score_abstention.py` ile
yapılır (ikinci bir hakem gövdesi YAZILMAZ — tek kaynak kuralı).

`context_shown` alanı yoksa (hasadın ilk sürümü onu saklamıyordu) bağlam **deterministik olarak
yeniden üretilir**: hasat, `random.seed(SEED)` ile karıştırılmış listede `Random(SEED + i)`
kullanıyor, dolayısıyla id → i eşlemesi tek anlamlıdır.

Kullanım:
  python scripts/puanlama/cp2_audit.py --harvest data/_ham_ve_ara/cp2_pilot_m2b.jsonl \
      --out outputs/eval/cp/cp2-rejected-hasat/kontrol_m2b_detail.jsonl
  python scripts/puanlama/score_abstention.py --details <o dosya> --label kontrol_m2b \
      --out-dir outputs/eval/cp/cp2-rejected-hasat --source-field context_shown
"""
import argparse
import json
import os
import random
import sys

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

import raft_pack
from build_sft_v2b import clip_sources_block

PACKED = "data/_ham_ve_ara/orpo_packed.jsonl"
MADDE_PATH = "data/corpus/mevzuat_maddeler.jsonl"
TRAP_CLIP = 900


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--harvest", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--packed", default=PACKED)
    ap.add_argument("--madde-path", default=MADDE_PATH)
    ap.add_argument("--seed", type=int, default=3407)
    ap.add_argument("--distractors", type=int, default=4)
    ap.add_argument("--max-chunk-chars", type=int, default=900)
    a = ap.parse_args()

    harvest = [json.loads(l) for l in open(a.harvest, encoding="utf-8") if l.strip()]
    if not harvest:
        raise SystemExit("hasat dosyası boş")
    tip = harvest[0]["tip"]

    rows = [json.loads(l) for l in open(a.packed, encoding="utf-8") if l.strip()]
    rows = [r for r in rows if r.get("slice") == "abstain_trap_v3"]
    random.seed(a.seed)
    random.shuffle(rows)                      # hasat ile BİREBİR aynı sıra
    pos = {r["id"]: i for i, r in enumerate(rows)}
    by_id = {r["id"]: r for r in rows}

    pool_recs = pool_by_kanun = None
    if tip == "m2b":
        pool_recs, pool_by_kanun = raft_pack.load_madde_pool(a.madde_path)

    out = []
    for h in harvest:
        rec = by_id[h["id"]]
        ctx = h.get("context_shown")
        if not ctx:                            # eski hasat sürümü → yeniden üret
            if tip == "m2":
                ctx = (rec.get("trap_text") or "")[:TRAP_CLIP]
            else:
                i = pos[h["id"]]
                grec = {"kanun_adi": rec.get("gold_kanun_adi", ""),
                        "madde_no": rec.get("gold_madde_no", ""),
                        "kanun_no": rec.get("gold_kanun_no", ""), "messages": []}
                rng = random.Random(a.seed + i)
                chunks, _ = raft_pack.pack_context(
                    grec, rec.get("gold_text") or "", pool_recs, pool_by_kanun,
                    a.distractors, rng, include_gold=False)
                ctx = raft_pack.format_sources_block(chunks)
                if a.max_chunk_chars > 0:
                    ctx = clip_sources_block(
                        ctx, "", f"{grec['kanun_adi']} {grec['madde_no']}", a.max_chunk_chars)
        out.append({"id": h["id"], "soru": h["soru"], "cevap": h["rejected"],
                    "referans": (rec.get("trap_text") or "")[:TRAP_CLIP],
                    "context_shown": ctx, "mode": h["mode"]})

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        for o in out:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    print(f"[cp2-audit] tip={tip} · {len(out)} aday → {a.out}")
    sf = "referans" if tip == "m2" else "context_shown"
    print(f"[cp2-audit] sıradaki: score_abstention.py --details {a.out} --source-field {sf}")


if __name__ == "__main__":
    main()
