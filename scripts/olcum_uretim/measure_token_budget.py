#!/usr/bin/env python
"""Token bütçesi ölçer — `max_seq_len` yüzünden kaç örnek SESSİZCE bozuluyor?

NEDEN VAR (research_log #15). 12B hattında `max_seq_len=2048` ile **1.421/17.323 (%8,2)** örnek
"tüm label −100" diye düşürüldü, toplam **2.010 (%11,6)** örneğin cevabı kısmen kesikti —
*yarım cevap öğretimi*, tek bir uyarı bile vermeden. Kök neden ölçülünce suçlu cevap değil
(median 196 token) **kaynak bloğu** çıktı (median 1.030, max 12.805) → 900-char clip ile
%11,6 → %0,03. Yeni tokenizer Türkçe'yi farklı verimlilikte kodlar, o yüzden **her base için
yeniden ölçülür** (`sprint1.md` CP2).

İKİ SAYI ÜRETİR — ikisi de eğitimi sessizce bozan biçim:
  · DÜŞEN      — istem tek başına sınırı doldurmuş, cevaptan hiç token kalmamış (label yok)
  · KESİK      — cevap başlamış ama ortasında kesilmiş (yarım cevap öğretimi)

Kullanım:
  python scripts/olcum_uretim/measure_token_budget.py --data data/train/raft/train.jsonl \\
         --model <base-repo-id> --max-seq-len 2048
"""
import argparse
import json
import os
import statistics


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True, help="messages taşıyan jsonl")
    # ⚠️ Gömülü base default'u YOK (ADR-0026): yanlış tokenizer'la ölçmek, ölçmemekten kötüdür.
    p.add_argument("--model", default=os.environ.get("BASE_MODEL"),
                   help="tokenizer kaynağı — HF repo id veya yerel yol")
    p.add_argument("--max-seq-len", type=int, default=2048)
    p.add_argument("--n", type=int, default=-1, help="ilk N satır (hızlı bakış)")
    p.add_argument("--out", default=None, help="özet json yolu (ops.)")
    return p.parse_args()


def pct(x, n):
    return round(100.0 * x / n, 2) if n else 0.0


def dist(xs):
    xs = sorted(xs)
    if not xs:
        return {}
    q = lambda f: xs[min(len(xs) - 1, int(len(xs) * f))]   # noqa: E731
    return {"median": statistics.median(xs), "p90": q(0.90), "p99": q(0.99), "max": xs[-1]}


def main():
    a = parse_args()
    if not a.model:
        raise SystemExit(
            "[tok] 🚫 --model (veya BASE_MODEL env) ZORUNLU — tokenizer olmadan token sayılmaz "
            "ve yanlış tokenizer'la çıkan sayı sessizce yanıltır (ADR-0026).")

    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(a.model)
    if not getattr(tok, "chat_template", None):
        raise SystemExit(f"[tok] 🚫 '{a.model}' tokenizer'ında chat_template yok — CP0'a dön.")

    rows = [json.loads(l) for l in open(a.data, encoding="utf-8") if l.strip()]
    if a.n and a.n >= 0:
        rows = rows[:a.n]

    total, prompt_lens, answer_lens, user_lens = [], [], [], []
    dropped = truncated = 0
    by_slice = {}

    for r in rows:
        msgs = r["messages"]
        prompt_msgs = [m for m in msgs if m["role"] != "assistant"]
        full = tok(tok.apply_chat_template(msgs, tokenize=False), add_special_tokens=False)
        prom = tok(tok.apply_chat_template(prompt_msgs, tokenize=False, add_generation_prompt=True),
                   add_special_tokens=False)
        n_full, n_prom = len(full["input_ids"]), len(prom["input_ids"])
        total.append(n_full)
        prompt_lens.append(n_prom)
        answer_lens.append(max(0, n_full - n_prom))
        u = next((m["content"] for m in msgs if m["role"] == "user"), "")
        user_lens.append(len(tok(u, add_special_tokens=False)["input_ids"]))

        sl = r.get("slice", "?")
        b = by_slice.setdefault(sl, {"n": 0, "dropped": 0, "truncated": 0})
        b["n"] += 1
        if n_prom >= a.max_seq_len:            # cevaba hiç yer kalmadı → tüm label −100
            dropped += 1
            b["dropped"] += 1
        elif n_full > a.max_seq_len:           # cevap başladı ama kesildi → yarım cevap
            truncated += 1
            b["truncated"] += 1

    n = len(rows)
    summary = {
        "data": a.data, "model": a.model, "n": n, "max_seq_len": a.max_seq_len,
        "dropped": dropped, "dropped_pct": pct(dropped, n),
        "truncated": truncated, "truncated_pct": pct(truncated, n),
        "affected_pct": pct(dropped + truncated, n),
        "tokens_total": dist(total), "tokens_prompt": dist(prompt_lens),
        "tokens_user_msg": dist(user_lens), "tokens_answer": dist(answer_lens),
        "by_slice": by_slice,
    }

    print(f"[tok] {a.data} | n={n} | max_seq_len={a.max_seq_len} | tokenizer={a.model}")
    print(f"[tok] toplam  {summary['tokens_total']}")
    print(f"[tok] istem   {summary['tokens_prompt']}   ← kaynak bloğu burada, 12B'de suçlu buydu")
    print(f"[tok] user    {summary['tokens_user_msg']}")
    print(f"[tok] cevap   {summary['tokens_answer']}")
    print(f"[tok] DÜŞEN   {dropped} (%{summary['dropped_pct']}) — cevaba yer kalmadı, label yok")
    print(f"[tok] KESİK   {truncated} (%{summary['truncated_pct']}) — yarım cevap öğretimi")
    for sl, b in sorted(by_slice.items()):
        print(f"[tok]   {sl:<10} n={b['n']:<6} düşen={b['dropped']:<5} kesik={b['truncated']}")

    tot_pct = summary["affected_pct"]
    if tot_pct > 1.0:
        print(f"[tok] ⚠️  etkilenen %{tot_pct} > %1 — KOŞMA. Kaynak bloğunu kıs "
              f"(--max-chunk-chars) ya da max_seq_len'i büyüt; 12B'de çözüm 900-char clip'ti.")
    else:
        print(f"[tok] ✅ etkilenen %{tot_pct} — bütçe uygun.")

    if a.out:
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(f"[tok] → {a.out}")


if __name__ == "__main__":
    main()
