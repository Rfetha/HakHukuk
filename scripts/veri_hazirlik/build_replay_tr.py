#!/usr/bin/env python3
"""Replay seti üret — genel TR instruction (catastrophic forgetting'e karşı, V2_PLAN §5.1-D).

NEDEN: v2b SFT, base'in genel yeteneğini/akıcılığını köreltmesin diye eğitime %1-5 genel
(hukuk-DIŞI) TR instruction karıştırılır. LoRA + düşük-rank + **replay** = kanıtlı anti-forgetting
üçlüsü (§5.1-D). v1 abstention çöküşünün (0.74→0.00) sigortalarından biri.

KAYNAK: `AlicanKiraz0/Turkish-SFT-Dataset-v1.0` (HF, **MIT** lisans → license-clean kuralına uygun).
  · 5.579 satır, system/user/assistant, genel instruction (aritmetik/kod/etik/mantık/güvenli-ret).
  · ⚠️ kart: "tam kapsamlı manuel denetim yapılmadı" → BU SCRIPT EDA-süzer (HARD RULE: doğrula).

SÜZME:
  (a) hukuk-DIŞI  — replay saf genel kapasiteyi korusun, hukuk pattern'i pekiştirmesin.
  (b) token ≤ --max-tok  — max_seq_len=2048 altında TRUNCATION YOK (yarım-kesik çıktı öğretmesin).
  (c) dedup (user metni) — tekrar örnek bias yapmasın.

ÇIKTI: data/train/replay_tr.jsonl  (chat-template `messages`: [system, user, assistant]).
  Replay örneği KENDİ (genel) system promptunu taşır → model "verilen system'e uy" davranışını korur.
  Sonra: build_sft_v2b.py assemble --replay data/train/replay_tr.jsonl --replay-frac 0.03

Kullanım:
  python scripts/veri_hazirlik/build_replay_tr.py --n 600 --max-tok 1500
"""
import argparse
import json
import os
import random
import re
import warnings

warnings.filterwarnings("ignore")

DATASET = "AlicanKiraz0/Turkish-SFT-Dataset-v1.0"
OUT = "data/train/replay_tr.jsonl"
# ⚠️ Token sayımı base'in tokenizer'ına bağlı (--max-tok bütçesi). Eskiden bir LoRA adaptör
# dizininden okunuyordu (outputs/v1) — o adaptör emekli olunca kırıldı. Artık parametre.

# Hukuk sızıntısı — saf-genel tutmak için ele. ("madde/dava" genel metinde de geçer; replay
# için temkinli davranıp hepsini düşürmek ucuz, havuz yine de yeterli.)
LEGAL_RE = re.compile(
    r"\b(madde|kanun|TCK|TMK|HMK|CMK|mahkeme|dava|yarg[ıi]tay|mevzuat|hukuk|tazminat|"
    r"sözleşme|ceza\b|iddianame|temyiz|icra|haciz|velayet|miras|tapu)\b", re.IGNORECASE)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=600, help="hedef replay örnek sayısı")
    p.add_argument("--max-tok", type=int, default=1500,
                   help="örnek başına token tavanı (max_seq_len=2048 altı; truncation önler)")
    p.add_argument("--seed", type=int, default=3407)
    p.add_argument("--out", default=OUT)
    p.add_argument("--tokenizer", required=True,
                   help="token sayımı için tokenizer (base HF repo id veya yerel yol)")
    p.add_argument("--keep-system", action="store_true", default=True,
                   help="genel system promptunu koru (replay 'system'e uy' davranışını korusun)")
    a = p.parse_args()

    from datasets import load_dataset
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(a.tokenizer)
    d = load_dataset(DATASET)["train"]
    print(f"[replay] kaynak={DATASET} n={len(d)} (MIT)")

    def n_tok(msgs):
        # NOT: apply_chat_template(tokenize=True) bu kayıtlı tokenizer'da bozuk (2 token döndürür) →
        # içerikleri düz tokenize et + rol/şablon payı (~12 tok). Filtre için yeterince doğru
        # (TR ~3.7 char/token; max_seq_len=2048 tavanın altında geniş pay bırakıyoruz).
        text = "\n".join(m["content"] for m in msgs)
        return len(tok(text)["input_ids"]) + 12

    kept = []
    seen = set()
    n_legal = n_long = n_dup = n_empty = 0
    for ex in d:
        sysm = (ex.get("system") or "").strip()
        user = (ex.get("user") or "").strip()
        asst = (ex.get("assistant") or "").strip()
        if not user or not asst:
            n_empty += 1
            continue
        if LEGAL_RE.search(user) or LEGAL_RE.search(asst):
            n_legal += 1
            continue
        key = user[:120]
        if key in seen:
            n_dup += 1
            continue
        msgs = []
        if a.keep_system and sysm:
            msgs.append({"role": "system", "content": sysm})
        msgs += [{"role": "user", "content": user},
                 {"role": "assistant", "content": asst}]
        if n_tok(msgs) > a.max_tok:
            n_long += 1
            continue
        seen.add(key)
        kept.append({"messages": msgs})

    print(f"[replay] süzme: hukuk-ele={n_legal} uzun-ele={n_long} dup={n_dup} boş={n_empty} "
          f"→ uygun havuz={len(kept)}")
    if len(kept) < a.n:
        print(f"[replay] ⚠️ havuz ({len(kept)}) < hedef ({a.n}) → --max-tok yükselt veya --n düşür. "
              f"Hepsi yazılıyor.")
    rng = random.Random(a.seed)
    rng.shuffle(kept)
    out_rows = kept[:a.n]

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        for r in out_rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    # kısa EDA özeti
    import statistics
    toks = [n_tok(r["messages"]) for r in out_rows]
    print(f"[replay] → {a.out}: {len(out_rows)} örnek · token median={statistics.median(toks):.0f} "
          f"max={max(toks)} (tavan={a.max_tok})")
    print(f"[replay] sıradaki: build_sft_v2b.py assemble --answers ... "
          f"--replay {a.out} --replay-frac 0.03")


if __name__ == "__main__":
    main()
