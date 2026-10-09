#!/usr/bin/env python
"""A4 — Atıf-format tutarlılığı (deterministik, LLM YOK, ücretsiz, anında).

SFT'nin görünür katkısı "tutarlı atıf disiplini" iddiasını ölçer. Hakem değil, regex:
  cite_present_rate : cevapların kaçında bir kanun/madde atfı var (Madde N / X sayılı)
  paren_cite_rate   : kaçında STANDART parantezli biçim "(KANUN..., Madde N)" var (tutarlılık)
  single_cite_rate  : kaçında TEK atıf (derli toplu; base dağınık-çok-atıf yapar)
  med_len           : medyan cevap uzunluğu (karakter)

Girdi: gen_eval_grounded çıktısı (outputs/eval/{label}_detail.jsonl)
Çıktı: outputs/eval/fmt_{label}_summary.json
Kullanım: python scripts/puanlama/score_format.py --details outputs/eval/bench_core_v1_detail.jsonl --label bench_core_v1
"""
import argparse
import json
import os
import re
import statistics

CITE_RE = re.compile(r"madde\s*\d+|m\.\s*\d+|\d+\s*sayılı", re.I)
PAREN_RE = re.compile(r"\([^)]*kanun[^)]*madde\s*\d+[^)]*\)", re.I)


def load_jsonl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--details", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--out-dir", default="outputs/eval")
    a = ap.parse_args()

    rows = load_jsonl(a.details)
    n = len(rows)
    has_cite = paren = single = 0
    lens = []
    for r in rows:
        c = r.get("cevap", "") or ""
        lens.append(len(c))
        cites = CITE_RE.findall(c)
        if cites:
            has_cite += 1
        if PAREN_RE.search(c):
            paren += 1
        if len(cites) == 1:
            single += 1

    summary = {
        "label": a.label, "n": n,
        "cite_present_rate": round(has_cite / n, 3) if n else None,
        "paren_cite_rate": round(paren / n, 3) if n else None,
        "single_cite_rate": round(single / n, 3) if n else None,
        "med_len": int(statistics.median(lens)) if lens else None,
        "note": "deterministik regex; atıf-disiplini sinyali (SFT'nin görünür katkı iddiası).",
    }
    os.makedirs(a.out_dir, exist_ok=True)
    json.dump(summary, open(f"{a.out_dir}/fmt_{a.label}_summary.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"[fmt] {a.label}: cite={summary['cite_present_rate']} paren={summary['paren_cite_rate']} "
          f"single={summary['single_cite_rate']} med_len={summary['med_len']} (n={n})")


if __name__ == "__main__":
    main()
