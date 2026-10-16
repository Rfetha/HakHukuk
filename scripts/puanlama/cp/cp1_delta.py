#!/usr/bin/env python3
"""CP1 — eski ↔ yeni hakem istemi karşılaştırması (ADR-0041 m.2 ve m.3).

m.2: istem değişikliği BAŞKA eksenleri (iddia sayısı, `cit_precision`) kaydırıyor mu — ölçülür.
m.3: düzeltilmiş sayıların YANINDA ham sayılar da yayımlanır; `τ_g`'nin kalan açığı maskelenmez.

Sayılar dosyalardan üretilir (elle kopyalama yok — `cp09_tablo.py` ile aynı disiplin).
Kullanım:
  python scripts/puanlama/cp/cp1_delta.py --old outputs/eval/cp/cp09-butceli-1024-512 \
      --new outputs/eval/cp/cp1-hakem-meta-iddia --tags "base_th tg_v1_th gem_th" --mode m1
"""
import argparse
import json
import os


def load_jsonl(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def label_counts(rows):
    """Ham etiket sayaçları — özet JSON yalnız oranları taşıyor, kayma buradan okunur."""
    c = {"SUPPORTED": 0, "CONTRADICTED": 0, "NOT_IN_SOURCE": 0}
    for r in rows:
        for x in r.get("labels", []):
            k = x.get("label")
            if k in c:
                c[k] += 1
    return c


def read(run_dir, label):
    s = json.load(open(f"{run_dir}/gnd_{label}_summary.json", encoding="utf-8"))
    rows = load_jsonl(f"{run_dir}/gnd_{label}.jsonl")
    a1p = f"{run_dir}/a1_{label}.txt"
    a1 = json.load(open(a1p, encoding="utf-8")) if os.path.exists(a1p) else {}
    return {"summary": s, "counts": label_counts(rows), "a1": a1}


def fmt(v, nd=4):
    return "—" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--tags", required=True)
    ap.add_argument("--mode", default="m1")
    a = ap.parse_args()

    rows = [
        ("toplam iddia", lambda d: d["summary"]["total_claims"], 0),
        ("SUPPORTED", lambda d: d["counts"]["SUPPORTED"], 0),
        ("CONTRADICTED", lambda d: d["counts"]["CONTRADICTED"], 0),
        ("NOT_IN_SOURCE", lambda d: d["counts"]["NOT_IN_SOURCE"], 0),
        ("faith_micro", lambda d: d["summary"]["faithfulness_micro"], 4),
        ("unsupported_micro", lambda d: d["summary"]["unsupported_micro"], 4),
        ("cit_precision_micro", lambda d: d["summary"]["cit_precision_micro"], 4),
        ("A1 (cevaplanan)", lambda d: d["a1"].get("A1_faithfulness_macro_answered"), 4),
        ("coverage n_answered", lambda d: d["a1"].get("n_answered"), 0),
    ]

    for tag in a.tags.split():
        label = f"{a.mode}_{tag}"
        try:
            old, new = read(a.old, label), read(a.new, label)
        except FileNotFoundError as e:
            print(f"\n### {label}: eksik dosya → {e}")
            continue
        print(f"\n### {label}")
        print(f"{'ölçüt':<22} {'ESKİ (ham)':>12} {'YENİ (ADR-0041)':>16} {'fark':>10}")
        for name, get, nd in rows:
            o, n = get(old), get(new)
            if isinstance(o, (int, float)) and isinstance(n, (int, float)):
                d = n - o
                ds = f"{d:+.{nd}f}" if nd else f"{d:+d}"
            else:
                ds = "—"
            print(f"{name:<22} {fmt(o, nd):>12} {fmt(n, nd):>16} {ds:>10}")
        # hatalı iddia oranı = ADR-0041'in bağlam tablosundaki eksen
        for tag_name, d in (("ESKİ", old), ("YENİ", new)):
            t = d["summary"]["total_claims"]
            bad = d["counts"]["CONTRADICTED"] + d["counts"]["NOT_IN_SOURCE"]
            print(f"  hatalı iddia oranı {tag_name}: {bad}/{t} = "
                  f"{100.0 * bad / t:.1f}%" if t else "  —")
        print(f"  hakem bedeli (yeni koşu): ${new['summary']['judge_cost_usd']:.4f}")


if __name__ == "__main__":
    main()
