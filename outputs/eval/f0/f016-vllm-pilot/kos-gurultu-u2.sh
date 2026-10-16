#!/usr/bin/env bash
# vLLM üretim gürültüsü (son incelemenin önemli uyarısı 2; kullanıcı onayı 2026-10-16): Q4'ten açılmış ağırlığın 2. üretim
# koşusu (t2), 1. koşuyla aynı hakem ayarıyla 3 tekrar x 8 parça = 24 süreç. t1 ↔ t2 kütle farkı = iki üretim çekilişi arası.
# Parça başına bütçe sınırı $0,2 (kos-parcali.sh'ta varsayılan $5'tı; 48 süreçte fiilen ~$240 tavan demekti).
set -uo pipefail
cd "$(dirname "$0")/../../../.."
source ~/code/global_venv/bin/activate
set -a; . ./.env; set +a
export OPENAI_API_KEY="$OPENROUTER_API_KEY" LLM_GATEWAY=openrouter OPENAI_BUDGET_USD=0.2
K=outputs/eval/f0/f016-vllm-pilot
O=$K/puanlama/u2
P=$O/parcalar
mkdir -p "$P"
a=q4-acilmis
D=$K/A10/$a/h1_tgta_v1_vllm_${a}_t2_detail.jsonl
for j in 1 2 3 4 5 6 7 8; do
  sed -n "$(( (j-1)*10 + 1 )),$(( j*10 ))p" "$D" > "$P/girdi_${a}-u2_p$j.jsonl"
done
for r in 1 2 3; do
  for j in 1 2 3 4 5 6 7 8; do
    python scripts/puanlama/groundedness.py --details "$P/girdi_${a}-u2_p$j.jsonl" --mode data \
      --label "vllm-${a}-u2_t${r}_p$j" --out-dir "$P" \
      --judge-model deepseek-v4.1-flash --hakem-saglayici deepinfra/fp8 --hakem-dusunme acik \
      > "$P/log_vllm-${a}-u2_t${r}_p$j.txt" 2>&1 &
  done
done
wait
python $K/birlestir.py --kok "$O" --parca-dizini "$P" --ek=-u2 --agirlik $a || exit 1
for r in 1 2 3; do
  python scripts/puanlama/harness_tablo.py --details "$D" --gnd "$O/gnd_vllm-${a}-u2_t$r.jsonl" \
    --kume data/eval/dev/core_hard.jsonl --out "$O/harness_tablo_${a}-u2_t$r.json" \
    > "$O/log_tablo_${a}-u2_t$r.txt" 2>&1 || echo "harness_tablo HATA: t$r"
done
grep -lE "Traceback|hakem hata|BÜTÇE" "$P"/log_*.txt "$O"/log_tablo_*.txt 2>/dev/null || echo "hata yok"
