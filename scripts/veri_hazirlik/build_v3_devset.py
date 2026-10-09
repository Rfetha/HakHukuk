#!/usr/bin/env python3
"""v3 ADIM 5 — held-out zor near-miss DEV-SET (ORPO hiperparametre ayarı için).

v3_recipe Q7: ~80 zor near-miss, eğitim seed'lerinden VE eval trap.jsonl'dan AYRIK. Sızıntı-kontrol.
Dev-set ile ORPO tuning (beta/lr) → karar eval'i (kanon 6-mod) KİRLENMEZ.

Seçim: packed_v3.jsonl'dan yüksek-ov_gold (zor, eval M2 dağılımıyla örtüşük) trap'ler; eval
trap.jsonl'daki sorularla ÇAKIŞMAYANLAR. Çıktı dev id'leri ADIM 6 paketlemede eğitimden ÇIKARILIR.

Çıktı: data/train/orpo_abstain/dev.jsonl (id, soru, trap_text, trap/gold alanları, ov_gold, expected=abstain).

Kullanım: python scripts/veri_hazirlik/build_v3_devset.py --n 80
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PACKED = "data/_ham_ve_ara/orpo_packed.jsonl"
EVAL_TRAP = "data/eval/canon/trap.jsonl"
OUT = "data/train/orpo_abstain/dev.jsonl"


def norm_soru(s):
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--packed", default=PACKED)
    p.add_argument("--eval-trap", default=EVAL_TRAP)
    p.add_argument("--out", default=OUT)
    p.add_argument("--n", type=int, default=80)
    p.add_argument("--min-ov-gold", type=float, default=0.12,
                   help="dev zor olmalı: ov_gold≥ (eval M2 med≈0.123)")
    p.add_argument("--max-ov-gold", type=float, default=0.35,
                   help="hi_overlap tail (>0.35, muhtemelen-geçersiz/kazara-cevaplayan) HARİÇ → eval M2 bandı")
    p.add_argument("--seed", type=int, default=3407)
    a = p.parse_args()

    rows = [json.loads(l) for l in open(a.packed, encoding="utf-8") if l.strip()]

    # Eval trap sızıntı-kümesi: soru metni + (gold_kanun_no|gold_madde_no)
    leak_soru, leak_gold = set(), set()
    if os.path.exists(a.eval_trap):
        for l in open(a.eval_trap, encoding="utf-8"):
            if not l.strip():
                continue
            r = json.loads(l)
            msgs = r.get("messages", [])
            s = next((m["content"] for m in msgs if m.get("role") == "user"), r.get("soru", ""))
            leak_soru.add(norm_soru(s))
            leak_gold.add(f"{r.get('kanun_no')}|{r.get('gold_madde_no')}")

    # Zor-AMA-GEÇERLİ bant + sızıntısız aday havuzu (eval M2 dağılımını yansıt, uç tail hariç).
    cands = [r for r in rows
             if a.min_ov_gold <= r["ov_gold"] <= a.max_ov_gold
             and norm_soru(r["soru"]) not in leak_soru
             and f"{r['gold_kanun_no']}|{r['gold_madde_no']}" not in leak_gold]
    n_leak = sum(1 for r in rows if norm_soru(r["soru"]) in leak_soru
                 or f"{r['gold_kanun_no']}|{r['gold_madde_no']}" in leak_gold)
    # Temsili örnekleme: deterministik shuffle (band-içi dağılımı koru, top-tail'e yığılma yok).
    import random
    random.Random(a.seed).shuffle(cands)

    # Kanun-çeşitliliği: tek kanun baskısını engelle (en fazla n//5 / kanun).
    cap = max(1, a.n // 5)
    from collections import Counter
    seen_law = Counter()
    dev = []
    for r in cands:
        if len(dev) >= a.n:
            break
        law = r["gold_kanun_adi"]
        if seen_law[law] >= cap:
            continue
        dev.append(r)
        seen_law[law] += 1
    if len(dev) < a.n:                       # çeşitlilik yetmezse kalanı sırayla tamamla
        have = {r["id"] for r in dev}
        for r in cands:
            if len(dev) >= a.n:
                break
            if r["id"] not in have:
                dev.append(r)

    with open(a.out, "w", encoding="utf-8") as f:
        for r in dev:
            f.write(json.dumps({
                "id": r["id"], "soru": r["soru"],
                "trap_text": r["trap_text"], "trap_kanun_adi": r["trap_kanun_adi"],
                "trap_madde_no": r["trap_madde_no"],
                "gold_kanun_adi": r["gold_kanun_adi"], "gold_madde_no": r["gold_madde_no"],
                "gold_kanun_no": r["gold_kanun_no"],
                "ov_gold": r["ov_gold"], "expected": "abstain", "_set": "v3_dev",
            }, ensure_ascii=False) + "\n")

    ovs = sorted(r["ov_gold"] for r in dev)
    print(f"[v3-dev] → {a.out}: {len(dev)} dev | eval-trap sızıntı elenen={n_leak} "
          f"| ov_gold med={ovs[len(ovs)//2]:.3f} min={ovs[0]:.3f} max={ovs[-1]:.3f}")
    print(f"[v3-dev] {len(seen_law)} kanun | dev id'leri ADIM 6 paketlemede eğitimden ÇIKARILACAK.")


if __name__ == "__main__":
    main()
