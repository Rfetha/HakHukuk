#!/usr/bin/env python3
"""Grounded SFT korpusu için GERÇEK groundedness kalite kapısı (eğitmeden ÖNCE).

Neden ayrı script: `score_corpus.py` referans=cevap koyar → groundedness'e verilince
hakem cevabı kendi kaynağı sanar (faith sahte-yüksek). gen_sft_v1 çıktısında madde METNİ
yok (sadece kanun_adi/madde_no/kanun_no). Bu köprü o boşluğu kapatır:

  train.jsonl örneği → her kayıt için data/corpus/mevzuat_maddeler.jsonl'den (kanun_no|madde_no)
  ile GERÇEK madde metnini join et → referans alanına koy → groundedness.py --mode data.

Böylece "v0 hatasını tekrarlama" kapısı dürüst çalışır: cevap GERÇEK maddeye karşı ölçülür.

Kullanım:
  python scripts/puanlama/score_grounded_corpus.py --data data/train/grounded_qa/train.jsonl \
      --label sft_v1 --n 40                 # detail yaz + groundedness koş (gpt-4o-mini)
  python scripts/puanlama/score_grounded_corpus.py --data ... --label sft_v1 --n 40 \
      --judge-model gpt-4o --runs 3         # paper-grade çapraz-aile hakem
  python scripts/puanlama/score_grounded_corpus.py --data ... --label sft_v1 --detail-only
"""
import argparse
import json
import os
import random
import subprocess
import sys

MADDE_PATH = "data/corpus/mevzuat_maddeler.jsonl"


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True, help="messages+atıf alanlı jsonl (gen_sft_v1 çıktısı)")
    p.add_argument("--label", required=True)
    p.add_argument("--n", type=int, default=40)
    p.add_argument("--seed", type=int, default=3407)
    p.add_argument("--out-dir", default="outputs/eval")
    p.add_argument("--madde-path", default=MADDE_PATH)
    p.add_argument("--detail-only", action="store_true",
                   help="sadece detail.jsonl üret; groundedness'i çağırma")
    # groundedness'e geçirilen
    p.add_argument("--judge-model", default=os.environ.get("GND_JUDGE", "gpt-4o-mini"))
    p.add_argument("--runs", type=int, default=1)
    return p.parse_args()


def norm(v):
    """kanun_no|madde_no anahtarını string olarak normalize et (int/str karışmasın)."""
    return "" if v is None else str(v).strip()


def load_madde_index(path):
    """(kanun_no|madde_no) → en uzun madde metni (aynı anahtar tekrarsa içerikçe en dolu olan)."""
    idx = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            k = f"{norm(r.get('kanun_no'))}|{norm(r.get('madde_no'))}"
            t = (r.get("text") or "").strip()
            if t and len(t) > len(idx.get(k, "")):
                idx[k] = t
    return idx


def extract(rec):
    msgs = rec.get("messages", [])
    soru = next((m["content"] for m in msgs if m["role"] == "user"), None)
    cevap = next((m["content"] for m in msgs if m["role"] == "assistant"), None)
    return soru, cevap


def main():
    a = parse_args()
    rows = [json.loads(l) for l in open(a.data, encoding="utf-8") if l.strip()]
    idx = load_madde_index(a.madde_path)
    random.seed(a.seed)
    sample = random.sample(rows, min(a.n, len(rows)))

    os.makedirs(a.out_dir, exist_ok=True)
    detail = os.path.join(a.out_dir, f"gnd_{a.label}_detail.jsonl")
    n_ok = n_no_madde = n_no_text = 0
    with open(detail, "w", encoding="utf-8") as f:
        for i, rec in enumerate(sample):
            soru, cevap = extract(rec)
            if not soru or not cevap:
                continue
            k = f"{norm(rec.get('kanun_no'))}|{norm(rec.get('madde_no'))}"
            source = idx.get(k, "")
            if not source:
                n_no_madde += 1
                continue
            out = {
                "id": i, "soru": soru, "cevap": cevap,
                "referans": source,                      # GERÇEK madde metni = yer-gerçeği
                "kanun_adi": rec.get("kanun_adi"),
                "madde_no": rec.get("madde_no"),
                "kanun_no": rec.get("kanun_no"),
                "source": rec.get("source"),
            }
            f.write(json.dumps(out, ensure_ascii=False) + "\n")
            n_ok += 1
    cov = n_ok / len(sample) if sample else 0
    print(f"[gnd-corpus] {a.label}: {n_ok}/{len(sample)} kayıt madde-metni eşleşti "
          f"(kapsam={cov:.0%}; eşleşmeyen={n_no_madde}) → {detail}")
    if cov < 0.8:
        print(f"[gnd-corpus] ⚠️ kapsam <%80 — kanun_no|madde_no eşleşmesi zayıf, "
              f"skor örneklemi temsil etmeyebilir.")

    if a.detail_only:
        print(f"[gnd-corpus] --detail-only → groundedness'i sen koş:\n"
              f"  python scripts/puanlama/groundedness.py --details {detail} --label {a.label} "
              f"--mode data --judge-model {a.judge_model} --runs {a.runs}")
        return

    cmd = [sys.executable, "scripts/puanlama/groundedness.py", "--details", detail,
           "--label", a.label, "--mode", "data",
           "--judge-model", a.judge_model, "--runs", str(a.runs)]
    print(f"[gnd-corpus] → {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
