#!/usr/bin/env python
"""A2 — Correctness skorlayıcı (cevap DOĞRU mu, yer-gerçeği = GERÇEK madde metni).

A1 (groundedness) ile A2 (correctness) FARKLI eksenlerdir, ortalanmaz (ALCE / RAGBench-TRACe /
Wallat "Correctness is not Faithfulness"). A1 = "her iddia VERİLEN kaynakta var mı" (attribution,
kendi bilgini kullanma). A2 = "cevap, GERÇEK kanuna göre soruyu DOĞRU cevaplıyor mu" (accuracy;
burada madde = yer-gerçeği, hakem onu DOĞRU kabul eder). A2 KÖR+Oracle iki modda da geçerli;
A1 yalnız Oracle'da tanımlı.

Hakem (response-level, holistik): CORRECT / PARTIAL / WRONG / ABSTAIN.
  CORRECT  = kilit hukuki sonuç maddeye göre doğru.
  PARTIAL  = doğru yönde ama bir şart/koşul eksik.
  WRONG    = yanlış hukuki sonuç / maddeyle çelişiyor.
  ABSTAIN  = cevap vermeyi reddetti ("bilmiyorum / kaynakta yok / danışın") — yanlış DEĞİL, kaçış.
Atıf formatı (A4) ve fazladan-sadık detay A2'yi ETKİLEMEZ.

Payda = TÜM sorular (Q4): correct_rate = CORRECT / n. CORE'da abstain = over-refusal (cezalı).
Selective-prediction (Point 5): yanında coverage = (n-ABSTAIN)/n ve conditional_acc = CORRECT/(n-ABSTAIN)
ayrıca raporlanır ki over-refusal gizlenmesin. correct_rate'e bootstrap %95 GA (Point 7).

Referans:
  --ref-mode detail (varsayılan): detail'deki "referans" (CORE'da gerçek doğru madde).
  --ref-mode gold (TRAP-A2, Q7): gerçek gold maddeyi join et (verilen tuzak madde DEĞİL).
    Gerekir: --eval-set data/eval/canon/trap.jsonl (gold_madde_no) + --madde-path (gold metin).

Girdi: gen_eval_grounded çıktısı (outputs/eval/{label}_detail.jsonl)
Çıktı: outputs/eval/corr_{label}.jsonl + corr_{label}_summary.json
Kullanım:
  python scripts/puanlama/score_correctness.py --details outputs/eval/bench_core_v1_detail.jsonl --label bench_core_v1
  python scripts/puanlama/score_correctness.py --details outputs/eval/bench_trap_v1_detail.jsonl --label bench_trap_v1 \
      --ref-mode gold --eval-set data/eval/canon/trap.jsonl
"""
import argparse
import json
import os
import random

JUDGE_SYSTEM = (
    "Sen titiz bir Türk hukuku değerlendirme hakemisin. Sana bir SORU, sorunun GERÇEK kanun maddesi "
    "(YER-GERÇEĞİ) ve modelin CEVABI verilecek. GERÇEK MADDE'yi DOĞRU kabul et; modelin cevabını bu "
    "maddeye göre değerlendir. Atıf formatına, üsluba veya fazladan doğru detaya BAKMA — yalnız "
    "sorunun hukuki cevabının DOĞRU olup olmadığına bak. YALNIZ JSON döndür:\n"
    "{\n"
    '  "verdict": "CORRECT" | "PARTIAL" | "WRONG" | "ABSTAIN",\n'
    '  "reason": "tek cümle"\n'
    "}\n"
    "CORRECT = kilit hukuki sonuç maddeye göre doğru (madde no yanlış/eksik olsa bile içerik doğruysa CORRECT).\n"
    "PARTIAL = doğru yönde ama bir şart/koşul/istisna eksik ya da yarım.\n"
    "WRONG   = yanlış hukuki sonuç veya maddeyle çelişiyor.\n"
    "ABSTAIN = model cevap vermeyi reddetti / 'bilmiyorum', 'kaynakta yok', 'bir avukata/maddeye danışın' "
    "dedi (esaslı cevap YOK). Bu yanlış sayılmaz, ayrı bir kategoridir."
)

PRICE = {"gpt-4o-mini": (0.15 / 1e6, 0.60 / 1e6), "gpt-4o": (2.5 / 1e6, 10.0 / 1e6)}
VERDICTS = ("CORRECT", "PARTIAL", "WRONG", "ABSTAIN")


def load_jsonl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def norm(x):
    return str(x or "").strip()


def build_gold_index(eval_set_path, madde_path):
    """TRAP için: soru → gerçek gold madde metni (verilen tuzak madde DEĞİL)."""
    # madde metni indeksi (en dolu metin)
    midx = {}
    for line in open(madde_path, encoding="utf-8"):
        r = json.loads(line)
        k = f"{norm(r.get('kanun_no'))}|{norm(r.get('madde_no'))}"
        t = (r.get("text") or "").strip()
        if t and len(t) > len(midx.get(k, "")):
            midx[k] = t
    # soru → gold madde metni
    q2gold = {}
    for line in open(eval_set_path, encoding="utf-8"):
        r = json.loads(line)
        soru = next((m["content"] for m in r.get("messages", []) if m["role"] == "user"), None)
        gold_no = r.get("gold_madde_no") or r.get("madde_no")
        k = f"{norm(r.get('kanun_no'))}|{norm(gold_no)}"
        if soru:
            q2gold[soru.strip()] = midx.get(k, "")
    return q2gold


def judge(client, model, soru, ref, cevap):
    user = (f"SORU:\n{soru}\n\nGERÇEK MADDE (yer-gerçeği):\n{ref[:3500]}\n\n"
            f"MODELİN CEVABI:\n{cevap}")
    r = client.chat.completions.create(
        model=model, temperature=0, response_format={"type": "json_object"},
        messages=[{"role": "system", "content": JUDGE_SYSTEM},
                  {"role": "user", "content": user}])
    d = json.loads(r.choices[0].message.content)
    u = r.usage
    p = PRICE.get(model, PRICE["gpt-4o-mini"])
    return d, u.prompt_tokens * p[0] + u.completion_tokens * p[1]


def bootstrap_ci(bits, iters=2000, seed=3407):
    """correct_rate için %95 bootstrap GA (Point 7). bits = [0/1] per-item CORRECT göstergesi."""
    if not bits:
        return [None, None]
    rng = random.Random(seed)
    n = len(bits)
    means = []
    for _ in range(iters):
        s = sum(bits[rng.randrange(n)] for _ in range(n))
        means.append(s / n)
    means.sort()
    lo = means[int(0.025 * iters)]
    hi = means[int(0.975 * iters)]
    return [round(lo, 3), round(hi, 3)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--details", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--judge-model", default=os.environ.get("GND_JUDGE", "gpt-4o-mini"))
    ap.add_argument("--ref-mode", choices=["detail", "gold"], default="detail",
                    help="detail=detail'deki referans (CORE); gold=gerçek gold madde (TRAP-A2)")
    ap.add_argument("--eval-set", default=None, help="ref-mode=gold için kaynak (data/eval/canon/trap.jsonl)")
    ap.add_argument("--madde-path", default="data/corpus/mevzuat_maddeler.jsonl")
    ap.add_argument("--out-dir", default="outputs/eval")
    a = ap.parse_args()

    key = os.environ.get("OPENAI_API_KEY", "").strip()
    assert key, "OPENAI_API_KEY yok (.env)"
    from openai import OpenAI
    client = OpenAI(api_key=key)
    budget = float(os.environ.get("OPENAI_BUDGET_USD", "5") or "5")

    q2gold = None
    if a.ref_mode == "gold":
        assert a.eval_set, "ref-mode=gold için --eval-set gerekli"
        q2gold = build_gold_index(a.eval_set, a.madde_path)

    rows = load_jsonl(a.details)
    out, spent = [], 0.0
    cnt = {v: 0 for v in VERDICTS}
    n_noref = 0
    bits = []  # per-item CORRECT göstergesi (bootstrap için)
    print(f"[corr] {a.label}: {len(rows)} cevap | hakem={a.judge_model} | ref={a.ref_mode}")
    for r in rows:
        if spent >= budget:
            print(f"[corr] BÜTÇE doldu (${spent:.3f}) — kalan atlandı"); break
        soru = r["soru"]
        ref = q2gold.get(soru.strip(), "") if a.ref_mode == "gold" else r.get("referans", "")
        if not ref:
            n_noref += 1
            continue  # referans yoksa skorlanamaz (TRAP gold join tutmadıysa)
        d, c = judge(client, a.judge_model, soru, ref, r["cevap"])
        spent += c
        v = d.get("verdict")
        if v not in VERDICTS:
            v = "WRONG"
        cnt[v] += 1
        bits.append(1 if v == "CORRECT" else 0)
        out.append({"id": r.get("id"), "soru": soru[:80], "cevap": r["cevap"][:160],
                    "verdict": v, "reason": d.get("reason")})
        mark = {"CORRECT": "✓DOĞRU", "PARTIAL": "~KISMİ", "WRONG": "✗YANLIŞ", "ABSTAIN": "○ABSTAIN"}[v]
        print(f"  id={r.get('id'):>2}  {mark:10} {(d.get('reason') or '')[:62]}")

    n = sum(cnt.values())
    cov = (n - cnt["ABSTAIN"]) / n if n else None
    summary = {
        "label": a.label, "n": n, "judge_model": a.judge_model, "ref_mode": a.ref_mode,
        "no_ref_skipped": n_noref,
        "correct_rate": round(cnt["CORRECT"] / n, 3) if n else None,            # MANŞET (strict, payda=tüm)
        "correct_rate_ci95": bootstrap_ci(bits),                                # Point 7
        "lenient_rate": round((cnt["CORRECT"] + cnt["PARTIAL"]) / n, 3) if n else None,  # CORRECT+PARTIAL
        "partial_rate": round(cnt["PARTIAL"] / n, 3) if n else None,
        "wrong_rate": round(cnt["WRONG"] / n, 3) if n else None,
        "abstain_rate": round(cnt["ABSTAIN"] / n, 3) if n else None,
        "coverage": round(cov, 3) if cov is not None else None,                 # Point 5 (denenen oranı)
        "conditional_acc": round(cnt["CORRECT"] / (n - cnt["ABSTAIN"]), 3)      # Point 5 (denediğinde isabet)
        if (n - cnt["ABSTAIN"]) else None,
        "counts": cnt,
        "judge_cost_usd": round(spent, 4),
        "note": "A2 correctness (yer-gerçeği=gerçek madde). A1'den AYRI eksen, ortalanmaz. "
                "payda=tüm soru; CORE'da abstain=over-refusal. coverage+conditional_acc yan-rapor (selective-pred). "
                "correct_rate_ci95=bootstrap %95.",
    }
    os.makedirs(a.out_dir, exist_ok=True)
    json.dump(out, open(f"{a.out_dir}/corr_{a.label}.jsonl", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    json.dump(summary, open(f"{a.out_dir}/corr_{a.label}_summary.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"\n[corr] ÖZET {a.label}: correct={summary['correct_rate']} "
          f"CI95={summary['correct_rate_ci95']} | lenient={summary['lenient_rate']} "
          f"abstain={summary['abstain_rate']} coverage={summary['coverage']} "
          f"cond_acc={summary['conditional_acc']} (n={n}, ref-yok={n_noref}) ${spent:.3f}")


if __name__ == "__main__":
    main()
