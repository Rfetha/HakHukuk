#!/usr/bin/env python
"""HakHukuk Eval Suite — test seti üreticisi (literatüre dayalı; bkz knowledge/summary_eval_benchmark_literature.md).

İki set üretir (deterministik, sabit seed → modeller AYNI soruları görür):

  CORE-HARD  : gold maddesi YÜKSEK KARMAŞIKLI (çok fıkra/bent/istisna) + 10 kanuna DENGELİ.
               Zorluk = KARMAŞIKLIK, uzunluk DEĞİL (Dahl "Large Legal Fictions": halüsinasyon
               görev-karmaşıklığıyla ölçekleniyor). Tavanı kırar → groundedness (A1) ayırt eder.

  TRAP       : soru, onu CEVAPLAMAYAN ama KONU-YAKINI bir madde (topic-near hard-negative) ile
               eşleştirilir (RGB negative-rejection + FaithEval unanswerable: distractor rastgele
               DEĞİL, konu-ilgili hard-negative). Doğru davranış = uydurmadan "bu madde bu konuyu
               düzenlemiyor" (abstain) → Rejection Rate (A3). Kayıtta `kanun_no|madde_no` = TUZAK
               madde (gen_eval --with-source onu enjekte etsin); `gold_*` = asıl madde.

Kullanım:
  python scripts/veri_hazirlik/build_eval_sets.py --core-n 40 --trap-n 35
Çıktı: data/eval/canon/core_hard.jsonl , data/eval/canon/trap.jsonl
"""
import argparse
import collections
import json
import os
import random
import re

MADDE_PATH = "data/corpus/mevzuat_maddeler.jsonl"
TEST_PATH = "data/train/grounded_qa/test.jsonl"

# --- KARMAŞIKLIK proxy'si (uzunluk değil) ---
FIKRA_RE = re.compile(r"\((\d{1,2})\)")            # (1) (2) ... fıkra işaretleri
BENT_RE = re.compile(r"(?:^|\s)([a-zçğıöşü])\)")   # a) b) ... bent işaretleri
EXC_WORDS = ("ancak", "hariç", "istisna", "şu kadar ki", "meğer", "kaydıyla",
             "şartıyla", "dışında", "saklıdır", "halinde", "takdirde")


def complexity(t):
    low = t.lower()
    fikra = len(set(FIKRA_RE.findall(t)))
    bent = len(set(BENT_RE.findall(low)))
    exc = sum(low.count(w) for w in EXC_WORDS)
    return fikra * 2 + bent + exc            # çok-koşullu/istisnalı = zor


def norm(v):
    return "" if v is None else str(v).strip()


def q_of(rec):
    msgs = rec.get("messages", [])
    return next((m["content"] for m in msgs if m["role"] == "user"), None)


def toks(t):
    return set(w for w in re.findall(r"[a-zçğıöşü]{4,}", t.lower()))


def load_madde(path):
    by_key, by_law = {}, collections.defaultdict(list)
    for line in open(path, encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        kn, mn = norm(r.get("kanun_no")), norm(r.get("madde_no"))
        t = (r.get("text") or "").strip()
        k = f"{kn}|{mn}"
        if len(t) > len(by_key.get(k, "")):
            by_key[k] = t
    for k, t in by_key.items():
        kn, mn = k.split("|", 1)
        if len(t) >= 250:                    # tuzak havuzu: gerçek hükümler
            by_law[kn].append((mn, t))
    return by_key, by_law


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--core-n", type=int, default=40)
    p.add_argument("--trap-n", type=int, default=35)
    p.add_argument("--seed", type=int, default=3407)
    p.add_argument("--out-dir", default="data/eval")
    # ⚠️ DEV/TEST ayrımı (ADR-0027 §3.2) BUNSUZ SAĞLANAMAZ. CORE-HARD seçimi karmaşıklığa göre
    # sıralı ve seed'den BAĞIMSIZ → farklı --seed AYNI maddeleri verir, büyük --core-n ise
    # TEST'in üst kümesini. DEV üretirken TEST'i mutlaka --exclude ile dışarıda bırak.
    p.add_argument("--exclude", nargs="*", default=[], metavar="JSONL",
                   help="bu set(ler)deki sorular havuzdan düşülür (DEV üretirken canon'u ver)")
    a = p.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    rng = random.Random(a.seed)

    by_key, by_law = load_madde(MADDE_PATH)
    test = [json.loads(l) for l in open(TEST_PATH, encoding="utf-8") if l.strip()]

    excluded = set()
    for path in a.exclude:
        for line in open(path, encoding="utf-8"):
            if line.strip():
                q = q_of(json.loads(line))
                if q:
                    excluded.add(q)
    if a.exclude:
        print(f"[eval-sets] dışlanan: {len(excluded)} soru ← {', '.join(a.exclude)}")

    items = []
    for r in test:
        kn, mn = norm(r.get("kanun_no")), norm(r.get("madde_no"))
        src = by_key.get(f"{kn}|{mn}", "")
        q = q_of(r)
        if src and q and q not in excluded:
            items.append({"rec": r, "kn": kn, "mn": mn, "src": src, "q": q,
                          "law": r.get("kanun_adi"), "L": len(src),
                          "cx": complexity(src)})

    # ---------- CORE-HARD: kanun başına en KARMAŞIK maddeler, dengeli ----------
    by_law_items = collections.defaultdict(list)
    for it in items:
        by_law_items[it["law"]].append(it)
    laws = sorted(by_law_items, key=lambda L: -len(by_law_items[L]))
    per_law = max(1, a.core_n // len(laws))
    core, used = [], set()
    for L in laws:
        pool = sorted(by_law_items[L], key=lambda x: -x["cx"])   # en karmaşık (zor) önce
        for it in pool[:per_law]:
            core.append(it); used.add(it["q"])
    if len(core) < a.core_n:                                     # küçük kanunlar az verdiyse tamamla
        rest = sorted((it for it in items if it["q"] not in used), key=lambda x: -x["cx"])
        for it in rest[: a.core_n - len(core)]:
            core.append(it); used.add(it["q"])
    core = sorted(core, key=lambda x: -x["cx"])[: a.core_n]

    with open(os.path.join(a.out_dir, "core_hard.jsonl"), "w", encoding="utf-8") as f:
        for it in core:
            f.write(json.dumps({
                "messages": it["rec"]["messages"],
                "kanun_adi": it["law"], "kanun_no": it["kn"], "madde_no": it["mn"],
                "_complexity": it["cx"], "_src_len": it["L"], "_set": "core_hard",
            }, ensure_ascii=False) + "\n")

    # ---------- TRAP: soru ↔ TOPIC-NEAR hard-negative (en yüksek kelime-örtüşmeli kardeş) ----------
    rng.shuffle(items)
    trap, seen_law = [], collections.Counter()
    cap = max(1, a.trap_n // 5)              # tek kanun baskısını engelle
    for it in items:
        if len(trap) >= a.trap_n:
            break
        if seen_law[it["law"]] >= cap:
            continue
        gold_tok = toks(it["src"])
        sibs = [(mn, t) for (mn, t) in by_law.get(it["kn"], []) if mn != it["mn"]]
        if not sibs or not gold_tok:
            continue
        # topic-near = gold ile en yüksek örtüşen kardeş (konu yakın, ama cevabı içermez)
        wmn, wsrc = max(sibs, key=lambda s: len(toks(s[1]) & gold_tok) / (len(toks(s[1]) | gold_tok) + 1))
        ov = len(toks(wsrc) & gold_tok) / (len(toks(wsrc) | gold_tok) + 1)
        trap.append({
            "messages": it["rec"]["messages"],
            "kanun_adi": it["law"], "kanun_no": it["kn"],
            "madde_no": wmn,                 # gen_eval BUNU enjekte eder = TUZAK kaynak
            "gold_madde_no": it["mn"],       # asıl doğru madde
            "expected": "abstain",
            "_overlap": round(ov, 3), "_set": "trap",
        })
        seen_law[it["law"]] += 1

    with open(os.path.join(a.out_dir, "trap.jsonl"), "w", encoding="utf-8") as f:
        for t in trap:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")

    cl = collections.Counter(it["law"] for it in core)
    cxs = sorted(x["cx"] for x in core)
    print(f"[eval-sets] CORE-HARD: {len(core)} | karmaşıklık med={cxs[len(cxs)//2]} min={cxs[0]} max={cxs[-1]}")
    for L, n in cl.most_common():
        print(f"    {n:3}  {L}")
    ovs = sorted(t["_overlap"] for t in trap)
    print(f"[eval-sets] TRAP: {len(trap)} | topic-near örtüşme med={ovs[len(ovs)//2] if ovs else 0}")
    print(f"[eval-sets] → {a.out_dir}/core_hard.jsonl , {a.out_dir}/trap.jsonl")


if __name__ == "__main__":
    main()
