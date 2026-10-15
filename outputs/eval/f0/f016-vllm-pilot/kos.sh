#!/usr/bin/env bash
# F0.16 vLLM pilotu puanlaması (kullanıcı onayıyla): iki ağırlık x 3 hakem tekrarı, DeepSeek V4.1 Flash, hakemin düşünmesi açık.
# Altı koşu eş zamanlı (~2 saat, tahmini ~$1,6). Girdi: her ağırlığın 1. üretim koşusu.
set -uo pipefail
cd "$(dirname "$0")/../../../.."
source ~/code/global_venv/bin/activate
set -a; . ./.env; set +a
export OPENAI_API_KEY="$OPENROUTER_API_KEY" LLM_GATEWAY=openrouter
K=outputs/eval/f0/f016-vllm-pilot
O=$K/puanlama
mkdir -p "$O"
for a in q4-acilmis bf16-orijinal; do
  D=$K/A10/$a/h1_tgta_v1_vllm_${a}_t1_detail.jsonl
  for r in 1 2 3; do
    python scripts/puanlama/groundedness.py --details "$D" --mode data --label "vllm-${a}_t$r" --out-dir "$O" \
      --judge-model deepseek-v4.1-flash --hakem-saglayici deepinfra/fp8 --hakem-dusunme acik \
      > "$O/log_vllm-${a}_t$r.txt" 2>&1 &
  done
done
wait
for a in q4-acilmis bf16-orijinal; do
  D=$K/A10/$a/h1_tgta_v1_vllm_${a}_t1_detail.jsonl
  for r in 1 2 3; do
    python scripts/puanlama/harness_tablo.py --details "$D" --gnd "$O/gnd_vllm-${a}_t$r.jsonl" \
      --kume data/eval/dev/core_hard.jsonl --out "$O/harness_tablo_${a}_t$r.json" \
      > "$O/log_tablo_${a}_t$r.txt" 2>&1
  done
done
for f in "$O"/log_vllm-*.txt; do echo "== $f"; tail -2 "$f"; done
