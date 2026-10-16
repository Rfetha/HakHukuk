#!/usr/bin/env bash
# F0.16 vLLM pilotu puanlaması, PARÇALI (kullanıcı kararı 2026-10-16: 8 parça; plandaki kos.sh'ın eşi, ölçüm aynı).
# İki ağırlık x 3 hakem tekrarı x 8 parça = 48 süreç eş zamanlı. DeepSeek V4.1 Flash, deepinfra/fp8, hakemin düşünmesi açık.
# Girdi: her ağırlığın 1. üretim koşusu. Sonra birlestir.py (tamlık kapısı) ve harness_tablo.
set -uo pipefail
cd "$(dirname "$0")/../../../.."
source ~/code/global_venv/bin/activate
set -a; . ./.env; set +a
export OPENAI_API_KEY="$OPENROUTER_API_KEY" LLM_GATEWAY=openrouter
K=outputs/eval/f0/f016-vllm-pilot
O=$K/puanlama
P=$O/parcalar
mkdir -p "$P"
for a in q4-acilmis bf16-orijinal; do
  D=$K/A10/$a/h1_tgta_v1_vllm_${a}_t1_detail.jsonl
  # 80 satır → 8 parça x 10 satır (id'ler satırların içinde, değişmez)
  for j in 1 2 3 4 5 6 7 8; do
    sed -n "$(( (j-1)*10 + 1 )),$(( j*10 ))p" "$D" > "$P/girdi_${a}_p$j.jsonl"
  done
  for r in 1 2 3; do
    for j in 1 2 3 4 5 6 7 8; do
      python scripts/puanlama/groundedness.py --details "$P/girdi_${a}_p$j.jsonl" --mode data \
        --label "vllm-${a}_t${r}_p$j" --out-dir "$P" \
        --judge-model deepseek-v4.1-flash --hakem-saglayici deepinfra/fp8 --hakem-dusunme acik \
        > "$P/log_vllm-${a}_t${r}_p$j.txt" 2>&1 &
    done
  done
done
wait
python $K/birlestir.py || exit 1
for a in q4-acilmis bf16-orijinal; do
  D=$K/A10/$a/h1_tgta_v1_vllm_${a}_t1_detail.jsonl
  for r in 1 2 3; do
    python scripts/puanlama/harness_tablo.py --details "$D" --gnd "$O/gnd_vllm-${a}_t$r.jsonl" \
      --kume data/eval/dev/core_hard.jsonl --out "$O/harness_tablo_${a}_t$r.json" \
      > "$O/log_tablo_${a}_t$r.txt" 2>&1 || echo "harness_tablo HATA: $a t$r"
  done
done
grep -l Traceback "$P"/log_*.txt "$O"/log_tablo_*.txt 2>/dev/null || echo "Traceback yok"
