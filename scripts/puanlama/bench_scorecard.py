#!/usr/bin/env python
"""HakHukuk Eval Suite — CANON birleşik scorecard (mod-stratifiye).

Eksenler (AYRI raporlanır, ortalanmaz — ALCE/RAGBench-TRACe):
  A1 Groundedness  (yalnız Oracle; KÖR'de TANIMSIZ — kaynak yok)   gnd_*_summary.json
  A2 Correctness   (KÖR + Oracle; yer-gerçeği=gerçek madde)        corr_*_summary.json
  A3 Abstention    (TRAP; RGB negative-rejection)                   abst_*_summary.json
  A4 Format        (KÖR + Oracle; deterministik)                    fmt_*_summary.json
  A1∧A2 Grounded-Accuracy (Oracle; TÜRETİLMİŞ İKİNCİL diagnostik — manşet DEĞİL, per-axis birincil)

Hücreler (her model):
  CORE × KÖR     → A2, A4               (label: bench_core_{m}_blind)
  CORE × Oracle  → A1, A2, A1∧A2, A4    (label: bench_core_{m})
  TRAP × Oracle  → A3 + TRAP-A2(diag)   (label: bench_trap_{m})

A1∧A2: per-item join (gnd_*.jsonl hallucination_rate==0) ∧ (corr_*.jsonl verdict==CORRECT).

Kullanım: python scripts/puanlama/bench_scorecard.py --models base v1
Çıktı: ekran + outputs/BENCHMARK_REPORT.md

⚠️ Akademik çerçeve (deep-research 2026-06-13):
- Per-eksen sayılar BİRİNCİL; A1∧A2 yalnız türetilmiş ikincil (alan ayrı raporlar, Trust-Score ORTALAR=zıt).
- A3 abstention çöküşü = BİZİM ÖZGÜN K3 negatif bulgumuz (replikasyon DEĞİL; yayınlı FT-harm lit OVER-refusal'dır).
- G1 cross-judge CROSS-FAMILY olmalı (Claude/Gemini) — gpt-4o aynı-aile, self-preference'ı gidermez (Wataoka).
- n=40/35 PİLOT → bootstrap GA (corr) + paired McNemar (analiz) raporla; paper-cetveli n=100/75.
"""
import argparse
import json
import os


def load(p):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def load_jsonl(p):
    """gnd_* satır-JSONL (groundedness f.write), corr_* JSON-array (json.dump) — ikisini de oku."""
    if not os.path.exists(p):
        return None
    txt = open(p, encoding="utf-8").read().strip()
    if not txt:
        return None
    try:
        d = json.loads(txt)                       # JSON-array (corr_*)
        return d if isinstance(d, list) else [d]
    except json.JSONDecodeError:
        return [json.loads(l) for l in txt.splitlines() if l.strip()]  # satır-JSONL (gnd_*)


def g(d, k):
    return d.get(k) if d else None


def fmt(v):
    if v is None:
        return "—"
    if isinstance(v, list):  # CI [lo,hi]
        return f"[{v[0]:.2f},{v[1]:.2f}]" if v and v[0] is not None else "—"
    return f"{v:.3f}" if isinstance(v, float) else str(v)


def conjunction(ed, m):
    """A1∧A2: Oracle CORE'da hallucination==0 (grounded) ∧ verdict==CORRECT, id ile join."""
    gnd = load_jsonl(f"{ed}/gnd_bench_core_{m}.jsonl")
    corr = load_jsonl(f"{ed}/corr_bench_core_{m}.jsonl")
    if not gnd or not corr:
        return None, 0
    grounded = {r["id"]: (r.get("hallucination_rate") == 0) for r in gnd if "id" in r}
    correct = {r["id"]: (r.get("verdict") == "CORRECT") for r in corr if "id" in r}
    ids = set(grounded) & set(correct)
    if not ids:
        return None, 0
    both = sum(1 for i in ids if grounded[i] and correct[i])
    return round(both / len(ids), 3), len(ids)


def table(title, header, rows):
    out = [f"**{title}**", "", "| model | " + " | ".join(header) + " |",
           "|" + "---|" * (len(header) + 1)]
    out += rows
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--eval-dir", default="outputs/eval")
    ap.add_argument("--out", default="outputs/BENCHMARK_REPORT.md")
    a = ap.parse_args()
    ed = a.eval_dir

    # ---- veri yükle ----
    data = {}
    for m in a.models:
        conj, nconj = conjunction(ed, m)
        data[m] = {
            "a1": load(f"{ed}/gnd_bench_core_{m}_summary.json"),          # Oracle CORE
            "a2_or": load(f"{ed}/corr_bench_core_{m}_summary.json"),      # Oracle CORE
            "a2_bl": load(f"{ed}/corr_bench_core_{m}_blind_summary.json"),# KÖR CORE
            "a4_or": load(f"{ed}/fmt_bench_core_{m}_summary.json"),       # Oracle CORE
            "a4_bl": load(f"{ed}/fmt_bench_core_{m}_blind_summary.json"), # KÖR CORE
            "a3": load(f"{ed}/abst_bench_trap_{m}_summary.json"),         # TRAP
            "a2_trap": load(f"{ed}/corr_bench_trap_{m}_summary.json"),    # TRAP-A2 diag
            "conj": conj, "nconj": nconj,
        }

    # ---- Hücre 1: CORE × KÖR (ezberden) ----
    h1 = ["A2 correct↑", "CI95", "A2 lenient", "abstain", "A4 cite", "A4 paren", "med_len"]
    r1 = []
    for m in a.models:
        d = data[m]
        r1.append(f"| **{m}** | " + " | ".join([
            fmt(g(d["a2_bl"], "correct_rate")), fmt(g(d["a2_bl"], "correct_rate_ci95")),
            fmt(g(d["a2_bl"], "lenient_rate")), fmt(g(d["a2_bl"], "abstain_rate")),
            fmt(g(d["a4_bl"], "cite_present_rate")), fmt(g(d["a4_bl"], "paren_cite_rate")),
            fmt(g(d["a4_bl"], "med_len"))]) + " |")

    # ---- Hücre 2: CORE × Oracle (madde verili) ----
    h2 = ["A1 faith", "A1 hall", "A1 wrong_ref", "A2 correct↑", "CI95", "A1∧A2🟢", "A4 paren"]
    r2 = []
    for m in a.models:
        d = data[m]
        r2.append(f"| **{m}** | " + " | ".join([
            fmt(g(d["a1"], "faithfulness_micro")), fmt(g(d["a1"], "hallucination_micro")),
            fmt(g(d["a1"], "wrong_ref_rate_micro")), fmt(g(d["a2_or"], "correct_rate")),
            fmt(g(d["a2_or"], "correct_rate_ci95")),
            f"{d['conj']:.3f} (n={d['nconj']})" if d["conj"] is not None else "—",
            fmt(g(d["a4_or"], "paren_cite_rate"))]) + " |")

    # ---- Hücre 3: TRAP × Oracle (yanlış madde) ----
    h3 = ["A3 Rej*↑", "A3 Rej_exact↑", "A3 fab↓", "param_leak", "valid", "TRAP-A2 correct(diag)"]
    r3 = []
    for m in a.models:
        d = data[m]
        r3.append(f"| **{m}** | " + " | ".join([
            fmt(g(d["a3"], "rejection_rate")), fmt(g(d["a3"], "rejection_exact")),
            fmt(g(d["a3"], "fabrication_rate")), fmt(g(d["a3"], "parametric_leak")),
            fmt(g(d["a3"], "valid_traps")), fmt(g(d["a2_trap"], "correct_rate"))]) + " |")

    md = [
        "# HakHukuk Eval Suite — CANON Scorecard",
        "",
        "> LLM-judge (gpt-4o-mini), model-vs-model SIRALAMA (mutlak değil). Eksenler AYRI (ortalanmaz). "
        "Setler: CORE-HARD (karmaşıklık-seçili) + TRAP (topic-near hard-negative). Mod: KÖR (ezberden) / "
        "Oracle (gerçek RAG değil, doğru/tuzak madde elle verili — gerçek RAG'ın iyimser tavanı).",
        "",
        "## Hücre 1 — CORE × KÖR · *kanunu ezberden biliyor mu* (A1 burada TANIMSIZ: kaynak yok)",
        table("CORE-KÖR", h1, r1),
        "",
        "## Hücre 2 — CORE × Oracle · *madde verilince doğru+dayanaklı mı*",
        table("CORE-Oracle", h2, r2),
        "> A1∧A2 = TÜRETİLMİŞ İKİNCİL diagnostik (per-axis sayılar birincil). grounded=hallucination==0 ∧ correct=CORRECT.",
        "",
        "## Hücre 3 — TRAP × Oracle · ⭐ *yanlış madde verilince reddedebiliyor mu* (asıl ayırt edici)",
        table("TRAP-Oracle", h3, r3),
        "> Rej*↑=uydurmadan 'kaynak yetersiz' diyebilme. TRAP-A2 = abstain etmeyenlerin gerçek-gold'a göre doğruluğu "
        "(diagnostik: fabrication 'yanlış-uydurma' mı 'doğru-ezber ama dayanaksız' mı).",
        "",
        "## G1 — Hakem geçerliliği (paper öncesi)",
        "> ⚠️ Cross-judge **CROSS-FAMILY** olmalı (Claude/Gemini) — gpt-4o aynı-aile, self-preference'ı gidermez "
        "(Wataoka). Hem raw-agreement hem Cohen's κ raporla (κ≥0.6 bar). + ~30 yazar spot-check.",
        "",
        "## Limitations / Future (akademik dürüstlük — deep-research 2026-06-13 ile teyitli)",
        "- **A3 abstention çöküşü = BİZİM ÖZGÜN K3 negatif bulgumuz**, replikasyon DEĞİL. Yayınlı FT-harm lit "
        "(Know-Your-Limits/CRaFT/R-Tuning) abstention-ODAKLI tuning'den OVER-refusal belgeler; bizimki generic-SFT'den "
        "UNDER-refusal (zıt yön) → özgün sun.",
        "- **A1∧A2 conjunction'ın temiz kanonik öncülü YOK** (Trust-Score ortalar=zıt felsefe) → ikincil tut, "
        "hallucination==0 eşiğini açıkça gerekçelendir.",
        "- **n=40/35 PİLOT** → underpowered; bootstrap GA (corr'da var) + **paired McNemar** (blind-vs-oracle / base-vs-v1) "
        "raporla; **paper-cetveli n=100/75**.",
        "- **Kontaminasyon kontrolü:** sorular sentetik-üretici + eğitim kanunlarıyla in-distribution (held-out). "
        "Memorization vs generalization ayrımı için **OOD unseen-statute dilimi** (+insan-yazımı dilim) paper öncesi şart.",
        "- **A1/A2 operasyonel tanımları açık yazılmalı** (ALCE/RAGBench/Wallat çizgiyi farklı çeker).",
        "- **G3 Completeness / G4 span-level — future.** Oracle = gerçek RAG'ın iyimser tavanı (retriever-hatasız).",
        "- LLM-judge mutlak değil + 'LLM-judge=human' ABARTILMAMALI (deep-research'te o iddia çürütüldü) → "
        "**model-vs-model SIRALAMA.**",
        "",
    ]
    report = "\n".join(md)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write(report)
    print(report)
    print(f"\n[scorecard] → {a.out}")


if __name__ == "__main__":
    main()
