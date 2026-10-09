#!/usr/bin/env python3
"""Birden çok koşuyu (base / τ kolları / rakip) yan yana markdown tabloya bas.

Sayı **hafızadan değil `outputs/eval/*_summary.json`'dan** gelir — belge disiplininin
(CLAUDE.md) makine tarafı. Kafesin her yeni hücresi bir sütun ekler; base ve rakip
sütunları sabit çıpa olarak durur, yeniden koşulmaz.

İki kapı var, ikisi de sessiz-yanlış-sayı sınıfına karşı:
  1. **Hakem yığını eşleşmiyorsa TABLO BASILMAZ.** Aynı model kimliği farklı servis
     yığınında koşmuşsa sayılar kıyaslanamaz ve bu hata vermez (ADR-0029).
  2. **Kalibre edilmemiş ailenin regex-red sayısı ⚠️ ile işaretlenir.** Kalibrasyonsuz
     regex rakibin reddini eksik sayar → sapma bizim lehimize (TASARIM §3.4).

Kullanım:
    python scripts/puanlama/compare_runs.py --labels base tg gem --out docs/record/cp6-tablo.md
"""
from __future__ import annotations

import argparse
import json
import os

EVAL_DIR = "outputs/eval"
GND_MODES = ("m1", "m4", "m5")          # groundedness hakemi
ABST_MODES = ("m2", "m2b", "m3")        # abstention hakemi

# Why: red-regex YALNIZ bu ailelerde elle kalibre edildi (research_log #39: 15/15 ileri +
# 2/2 geri). Listede olmayan her etiketin regex-red sayısı raporlanamaz. Yeni aile eklemek
# = buraya bir satır + kalibrasyon işi; sırasız eklemek sayıyı bizim lehimize kaydırır.
REGEX_CALIBRATED = {"base", "tg", "ta", "tgta"}   # kendi base'imiz ve ondan türeyen kollar


def load(path: str):
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else None


def collect(label: str) -> dict:
    d = {"gnd": {}, "a1": {}, "abst": {}, "reg": {}}
    for m in GND_MODES:
        d["gnd"][m] = load(f"{EVAL_DIR}/gnd_{m}_{label}_summary.json")
        d["a1"][m] = load(f"{EVAL_DIR}/a1_{m}_{label}.txt")
    for m in ABST_MODES:
        d["abst"][m] = load(f"{EVAL_DIR}/abst_{m}_{label}_summary.json")
    for m in GND_MODES + ABST_MODES:
        d["reg"][m] = load(f"{EVAL_DIR}/reg_{m}_{label}_summary.json")
    return d


def judge_stack(data: dict) -> set:
    """Tabloya giren her özetin (hakem modeli, gateway) çifti."""
    out = set()
    for group in ("gnd", "abst"):
        for s in data[group].values():
            if s:
                out.add((s.get("judge_model"), s.get("judge_gateway")))
    return out


def fmt(v, nd=4):
    return "—" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--labels", nargs="+", required=True,
                   help="etiket sırası, ör. base tg gem (sütun sırası budur)")
    p.add_argument("--out", help="markdown çıktısı (verilmezse ekrana)")
    a = p.parse_args()

    runs = {lab: collect(lab) for lab in a.labels}

    # 🚨 Kapı 1 — hakem yığını tek olmalı.
    stacks = set().union(*(judge_stack(d) for d in runs.values()))
    if len(stacks) != 1:
        raise SystemExit(f"[compare] 🚫 hakem yığını TEK DEĞİL: {sorted(stacks)}\n"
                         "  Farklı hakem/gateway ile üretilmiş sayılar kıyaslanamaz (ADR-0029).")
    judge_model, judge_gateway = stacks.pop()

    rows = []
    for m in ("m1", "m4"):
        rows.append((f"**{m.upper()}** faith_macro (ALL)",
                     [(runs[l]["gnd"][m] or {}).get("faithfulness_macro") for l in a.labels]))
        rows.append((f"{m.upper()} **A1** (cevaplanan)",
                     [(runs[l]["a1"][m] or {}).get("A1_faithfulness_macro_answered") for l in a.labels]))
        rows.append((f"{m.upper()} **coverage**",
                     [_cov(runs[l]["a1"][m]) for l in a.labels]))
        rows.append((f"{m.upper()} cit_precision",
                     [(runs[l]["gnd"][m] or {}).get("cit_precision_micro") for l in a.labels]))
    for m in ABST_MODES:
        rows.append((f"**{m.upper()}** Rej (LLM hakemi)",
                     [(runs[l]["abst"][m] or {}).get("rejection_rate") for l in a.labels]))
        rows.append((f"{m.upper()} Rej (regex)",
                     [_regex_rej(runs[l]["abst"][m], l) for l in a.labels]))
        rows.append((f"{m.upper()} geçerli tuzak *(payda)*",
                     [(runs[l]["abst"][m] or {}).get("valid_traps") for l in a.labels]))
    rows.append(("**M5** faith_macro *(ANTİ-HEDEF ↓)*",
                 [(runs[l]["gnd"]["m5"] or {}).get("faithfulness_macro") for l in a.labels]))
    rows.append(("M5 **coverage** *(kör cevaplama ↓)*",
                 [_cov(runs[l]["a1"]["m5"]) for l in a.labels]))
    for m in ("m1", "m4", "m2", "m2b"):
        rows.append((f"register proxy {m.upper()}",
                     [(runs[l]["reg"][m] or {}).get("register_mean") for l in a.labels]))

    lines = [
        f"| eksen | {' | '.join(a.labels)} |",
        f"| :--- | {' | '.join(['---:'] * len(a.labels))} |",
    ]
    lines += [f"| {name} | {' | '.join(fmt(v) for v in vals)} |" for name, vals in rows]

    uncal = [l for l in a.labels if l not in REGEX_CALIBRATED]
    lines += [
        "",
        f"*Hakem: `{judge_model}` / `{judge_gateway}` · seed 3407 · harness KAPALI · DEV havuzu.*",
    ]
    if uncal:
        lines.append(f"*⚠️ **regex-red kalibre edilmedi**: {', '.join(uncal)} — o satırlar "
                     "raporlanamaz, LLM-red satırı okunur (TASARIM §3.4).*")
    lines.append("*Rej paydaları modele göre değişir (`geçerli tuzak` satırı) — oranlar payda ile "
                 "birlikte okunur.*")

    text = "\n".join(lines)
    if a.out:
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        open(a.out, "w", encoding="utf-8").write(text + "\n")
        print(f"[compare] → {a.out}")
    print(text)


def _cov(a1: dict | None):
    if not a1:
        return None
    return f"{a1['n_answered']}/{a1['n_total']} = %{100 * a1['n_answered'] / a1['n_total']:.1f}"


def _regex_rej(s: dict | None, label: str):
    if not s:
        return None
    v = s.get("rejection_exact")
    return f"{v:.4f}" if label in REGEX_CALIBRATED else f"⚠️ {v:.4f}"


if __name__ == "__main__":
    main()
