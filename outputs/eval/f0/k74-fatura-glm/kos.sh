#!/usr/bin/env bash
# #74 (2026-10-17, kullanıcı onayı Durak 1): F0.6'nın 80 DEV cevabı, hakem kapalı modda.
#   ds        DeepSeek tek koşu, yalnız başına (R2b: önbellek isabeti, gerçek fatura oranı)
#   r3        aynı sorunun iki kolu art arda (A10 ↔ vLLM q4 t1), tek dosyada (R3)
#   glm-duman GLM 3 kalem (gözle okunur); GLM düşünmesi kapatılamaz → düzey low (kullanıcı kararı)
#   glm       GLM 5 tekrar, eş zamanlı (gürültü tabanı, eşik ≤ 0,9 p; kayma çıpası F3.1)
set -uo pipefail
cd "$(dirname "$0")/../../../.."
source ~/code/global_venv/bin/activate
set -a; . ./.env; set +a
export OPENAI_API_KEY="$OPENROUTER_API_KEY" LLM_GATEWAY=openrouter OPENAI_BUDGET_USD=0.5
D=outputs/eval/f0/f016-pilot/A10/m1/h1_tgta_v1_A10_m1_t1_detail.jsonl
O=outputs/eval/f0/k74-fatura-glm
G=scripts/puanlama/skorlayici/groundedness.py
DS="--judge-model deepseek-v4.1-flash --hakem-saglayici deepinfra/fp8 --hakem-dusunme kapali"
GLM="--judge-model glm-5.3-flash --hakem-saglayici novita/fp8 --hakem-dusunme dusuk"
date -u +%FT%TZ >> $O/baslangic_$1_utc.txt
case "$1" in
  ds)  python $G --details $D --mode data --label ds-kapali_r1 --out-dir $O $DS > $O/log_ds-kapali_r1.txt 2>&1 ;;
  r3)  python $G --details $O/r3_sirali_detail.jsonl --mode data --label ds-kapali_r3 --out-dir $O $DS \
         > $O/log_ds-kapali_r3.txt 2>&1 ;;
  glm-duman) python $G --details $D --mode data --label glm-dusuk_duman --out-dir $O --n 3 $GLM \
         > $O/log_glm-dusuk_duman.txt 2>&1 ;;
  glm) for t in 1 2 3 4 5; do
         python $G --details $D --mode data --label glm-dusuk_t$t --out-dir $O $GLM > $O/log_glm-dusuk_t$t.txt 2>&1 &
       done; wait ;;
  *) echo "aşama: ds | r3 | glm-duman | glm"; exit 2 ;;
esac
for f in $O/log_*.txt; do echo "== $f"; tail -2 "$f" | cut -c1-300; done
