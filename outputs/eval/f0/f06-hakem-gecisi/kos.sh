#!/usr/bin/env bash
# F0.6 puanlaması (2026-10-15, kullanıcı onayı "Başlat"): pilotun referans cevapları, altı hakem koşusu eş zamanlı.
set -uo pipefail
cd "$(dirname "$0")/../../../.."
source ~/code/global_venv/bin/activate
set -a; . ./.env; set +a
export OPENAI_API_KEY="$OPENROUTER_API_KEY" LLM_GATEWAY=openrouter
D=outputs/eval/f0/f016-pilot/A10/m1/h1_tgta_v1_A10_m1_t1_detail.jsonl
O=outputs/eval/f0/f06-hakem-gecisi
for mod in acik kapali; do for t in 1 2; do
  python scripts/puanlama/groundedness.py --details $D --mode data --label ds-${mod}_t$t --out-dir $O \
    --judge-model deepseek-v4.1-flash --hakem-saglayici deepinfra/fp8 --hakem-dusunme $mod \
    > $O/log_ds-${mod}_t$t.txt 2>&1 &
done; done
for t in 1 2; do
  python scripts/puanlama/groundedness.py --details $D --mode data --label mini_t$t --out-dir $O \
    --judge-model openai/gpt-4o-mini --hakem-saglayici OpenAI > $O/log_mini_t$t.txt 2>&1 &
done
wait
for f in $O/log_*.txt; do echo "== $f"; tail -3 "$f"; done
