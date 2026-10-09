#!/usr/bin/env bash
# CP7 — erken rakip önizlemesi: Gemini 3.1 Flash-Lite, 6-mod CANON, DEV havuzu.
# ⚠️ Sprint 5 parite İDDİASI DEĞİL — "nerede duruyoruz" erken sinyali (harness KAPALI, model-düzeyi).
#
# ÜRETİM  → OpenRouter (google/gemini-3.1-flash-lite), provider "Google AI Studio".
# SKORLAMA→ ayrı adım, gpt-4o-mini OpenAI-direct (aile-dışlama: Google özneyi OpenAI hakem notlar).
#
# ⚠️ Adil kıyas: base --thinking off (düşünce yok) ile koştu; Gemini 3.1 flash-lite varsayılan
# reasoning_tokens=0 → aynı bantta. Bizim tarafta --thinking none (Qwen bayrağı Gemini'ye gitmez).
set -uo pipefail
cd /home/ersoy/code/Hukuk-SLM
source ~/code/global_venv/bin/activate
set -a && . ./.env && set +a

MODEL="google/gemini-3.1-flash-lite"
DEV=data/eval/dev
# gen_eval_grounded HTTP yolu: base_url=--server-url, api_key=OPENAI_API_KEY (env).
# Üretim için OpenRouter'a yönlendir: key'i OpenRouter yap, base_url OpenRouter.
export OPENAI_API_KEY="$OPENROUTER_API_KEY"
SRV="https://openrouter.ai/api/v1"
G="python scripts/olcum_uretim/gen_eval_grounded.py --server-url $SRV --server-model $MODEL --thinking none --max-new-tokens 512"

echo "### CP7 Gemini üretim — $MODEL @ $SRV"
$G --label m1_gem  --data $DEV/core_hard.jsonl --distractors 4 --max-chunk-chars 900 --n 80  2>&1 | grep -vE "^  \[|Unsloth|🦥" | tail -4
$G --label m4_gem  --data $DEV/core_hard.jsonl --with-source --n 80                          2>&1 | grep -vE "^  \[|Unsloth|🦥" | tail -4
$G --label m2_gem  --data $DEV/trap.jsonl      --with-source --n 70                          2>&1 | grep -vE "^  \[|Unsloth|🦥" | tail -4
$G --label m2b_gem --data $DEV/core_hard.jsonl --distractors 4 --no-gold --n 80              2>&1 | grep -vE "^  \[|Unsloth|🦥" | tail -4
$G --label m3_gem  --data $DEV/core_hard.jsonl --empty-context --n 80                        2>&1 | grep -vE "^  \[|Unsloth|🦥" | tail -4
$G --label m5_gem  --data $DEV/core_hard.jsonl --n 80                                        2>&1 | grep -vE "^  \[|Unsloth|🦥" | tail -4
echo "### ÜRETİM BİTTİ"
wc -l outputs/eval/m*_gem_detail.jsonl
