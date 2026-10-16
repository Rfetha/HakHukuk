#!/usr/bin/env bash
# vLLM üretim gürültüsü, ek çekilişler (kullanıcı kararı 2026-10-16 "biraz daha ölç"): Q4'ten açılmış ağırlığın t3-t5 üretim
# koşuları (A10/q4-acilmis_u345/), her biri BİR hakem puanlaması x 8 parça = 24 süreç; ayar t1/t2 ile aynı.
# Parça başına bütçe sınırı $0,2.
set -uo pipefail
cd "$(dirname "$0")/../../../.."
source ~/code/global_venv/bin/activate
set -a; . ./.env; set +a
export OPENAI_API_KEY="$OPENROUTER_API_KEY" LLM_GATEWAY=openrouter OPENAI_BUDGET_USD=0.2
K=outputs/eval/f0/f016-vllm-pilot
O=$K/puanlama/u345
P=$O/parcalar
mkdir -p "$P"
a=q4-acilmis
for u in 3 4 5; do
  D=$K/A10/${a}_u345/h1_tgta_v1_vllm_${a}_t${u}_detail.jsonl
  for j in 1 2 3 4 5 6 7 8; do
    sed -n "$(( (j-1)*10 + 1 )),$(( j*10 ))p" "$D" > "$P/girdi_${a}-u${u}_p$j.jsonl"
    python scripts/puanlama/groundedness.py --details "$P/girdi_${a}-u${u}_p$j.jsonl" --mode data \
      --label "vllm-${a}-u${u}_t1_p$j" --out-dir "$P" \
      --judge-model deepseek-v4.1-flash --hakem-saglayici deepinfra/fp8 --hakem-dusunme acik \
      > "$P/log_vllm-${a}-u${u}_t1_p$j.txt" 2>&1 &
  done
done
wait
for u in 3 4 5; do
  D=$K/A10/${a}_u345/h1_tgta_v1_vllm_${a}_t${u}_detail.jsonl
  python $K/birlestir.py --kok "$O" --parca-dizini "$P" --ek=-u$u --agirlik $a --tekrar 1 || exit 1
  python scripts/puanlama/harness_tablo.py --details "$D" --gnd "$O/gnd_vllm-${a}-u${u}_t1.jsonl" \
    --kume data/eval/dev/core_hard.jsonl --out "$O/harness_tablo_${a}-u${u}_t1.json" \
    > "$O/log_tablo_${a}-u${u}.txt" 2>&1 || echo "harness_tablo HATA: u$u"
done
grep -lE "Traceback|hakem hata|BÜTÇE" "$P"/log_*.txt "$O"/log_tablo_*.txt 2>/dev/null || echo "hata yok"
