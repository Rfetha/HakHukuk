#!/usr/bin/env python
"""CP0.9 birleşik tablo — 3 özne × 2 protokol × 6 mod, tek kural (ADR-0044).

Why: iki protokolün sayıları iki ayrı kaynaktan geliyor (Sprint 1 = `*_adr0044.txt`,
CP0.9 = `a1_*_th.txt`) ve m5 hariç aynı kuralla hesaplandı. Elle kopyalamak, bu hattın
klasik sessiz-bozulma yolu; tablo tek yerden ve dosyalardan üretilir.

  python scripts/puanlama/cp/cp09_tablo.py            # markdown tablo
"""
import json
import os

# Koşu klasörleri (2026-07-29): iki protokol iki ayrı dizinde, künyeleri yanlarında.
OFF_DIR = "outputs/eval/sprint1/sprint1-thinking-off"
ON_DIR = "outputs/eval/cp/cp09-butceli-1024-512"
# özne → (thinking-off etiketi, bütçeli-on etiketi)
SUBJ = [("base", "base", "base_th"),
        ("τ_g v1", "tg", "tg_v1_th"),
        ("Gemini 3.1 FL", "gem", "gem_th")]


def _load(p):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


def _dir(off):
    return OFF_DIR if off else ON_DIR


def a1(mode, tag, off):
    """A1/coverage. thinking-off tarafında ADR-0044 ile yeniden hesaplanmış dosya kullanılır."""
    suffix = "_adr0044" if off else ""
    return _load(f"{_dir(off)}/a1_{mode}_{tag}{suffix}.txt")


def abst(mode, tag, off):
    return _load(f"{_dir(off)}/abst_{mode}_{tag}_summary.json")


def detail(mode, tag, off):
    p = f"{_dir(off)}/{mode}_{tag}_detail.jsonl"
    if not os.path.exists(p):
        return []
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def kutle(d):
    if not d or d.get("A1_faithfulness_macro_answered") is None:
        return None
    return 100.0 * d["n_answered"] / d["n_total"] * d["A1_faithfulness_macro_answered"]


def fmt(v, suf="", nd=1):
    return "—" if v is None else (f"{v:.{nd}f}{suf}" if isinstance(v, float) else f"{v}{suf}")


def rows():
    """(satır adı, ok-yönü, değer fonksiyonu) — ok: ↑ iyi, ↓ iyi (anti-hedef)."""
    return [
        ("**M1** sadık-cevap kütlesi %", "↑", lambda t, o: kutle(a1("m1", t, o))),
        ("M1 coverage %", "·", lambda t, o: (lambda d: 100 * d["n_answered"] / d["n_total"] if d else None)(a1("m1", t, o))),
        ("M1 A1 (cevaplanan)", "↑", lambda t, o: (lambda d: d and d["A1_faithfulness_macro_answered"])(a1("m1", t, o))),
        ("**M4** oracle kütlesi %", "↑", lambda t, o: kutle(a1("m4", t, o))),
        ("**M2** Rej (LLM)", "↑", lambda t, o: (lambda d: d and d["rejection_rate"])(abst("m2", t, o))),
        ("M2 geçerli tuzak (payda)", "·", lambda t, o: (lambda d: d and d["valid_traps"])(abst("m2", t, o))),
        ("M2 fabrikasyon", "↓", lambda t, o: (lambda d: d and d.get("fabrication_rate"))(abst("m2", t, o))),
        ("**M2b** Rej (LLM)", "↑", lambda t, o: (lambda d: d and d["rejection_rate"])(abst("m2b", t, o))),
        ("**M3** Rej (LLM)", "↑", lambda t, o: (lambda d: d and d["rejection_rate"])(abst("m3", t, o))),
        ("**M5** ezber kütlesi % *(ANTİ-HEDEF)*", "↓", lambda t, o: kutle(a1("m5", t, o))),
        ("M5 coverage %", "↓", lambda t, o: (lambda d: 100 * d["n_answered"] / d["n_total"] if d else None)(a1("m5", t, o))),
    ]


def maliyet(tag, off):
    R = [x for m in ("m1", "m4", "m2", "m2b", "m3", "m5") for x in detail(m, tag, off)]
    if not R:
        return None, None
    tk = [x["completion_tokens"] for x in R if x.get("completion_tokens")]
    fc = sum(1 for x in R if x.get("forced_close"))
    return (sum(tk) / len(tk) if tk else None), 100.0 * fc / len(R)


def main():
    cols = [(lab, tag, off) for lab, o, t in SUBJ for (tag, off, lab) in
            [(o, True, f"{lab} (off)"), (t, False, f"{lab} (bütçeli)")]]
    head = "| ölçüt | yön | " + " | ".join(c[0] for c in cols) + " |"
    sep = "| :--- | :-: | " + " | ".join("---:" for _ in cols) + " |"
    print(head); print(sep)
    for name, arrow, fn in rows():
        vals = []
        for _, tag, off in cols:
            v = fn(tag, off)
            vals.append(fmt(v) if isinstance(v, float) and v > 2 else fmt(v, nd=4) if isinstance(v, float) else fmt(v))
        print(f"| {name} | {arrow} | " + " | ".join(vals) + " |")
    tok = [maliyet(tag, off) for _, tag, off in cols]
    print("| **ort token/cevap** | ↓ | " + " | ".join(fmt(t[0], nd=0) for t in tok) + " |")
    print("| zorunlu kapatma % | · | " + " | ".join(fmt(t[1]) for t in tok) + " |")


if __name__ == "__main__":
    main()
