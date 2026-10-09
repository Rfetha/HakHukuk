#!/usr/bin/env bash
# CP3 merge SÜPÜRMESİ — bir merge varyantını uçtan uca ölç (GGUF → eval → puanlama).
#
# Neden var: §21'de norm-dengelemenin geri-ölçek kuralı küçük kolu 4,9× şişirdi ve model
# dejenere oldu. Kural DEV'de süpürülüyor; her deneme aynı zinciri koşuyor, tek fark merge.
#
# Kullanım:
#   bash scripts/olcum_uretim/cp3_merge_dene.sh <merged-hf-dizini> <etiket>
#     ör: bash scripts/olcum_uretim/cp3_merge_dene.sh models/merged/tg_ta_min min
#
# 🛑 Geçerlilik kapısı (ADR-0040, kesik > %5) düşerse zincir `&&` ile KIRILIR ve
#    puanlamaya para HARCANMAZ. Bu kasıtlı: geçersiz koşunun sayısı okunmaz.
#
# ⚠️ Rejim değişmezleri (ADR-0043) burada SABİT: 1024+512 · seed 3407 · chunk 900 · CTX 8192.
#    Bunlar süpürülmez — süpürülen yalnız MERGE parametreleridir.

set -uo pipefail        # -e BİLEREK yok: tuzak 5.4

die() { echo "❌ $*" >&2; exit 1; }

MERGED="${1:?kullanım: cp3_merge_dene.sh <merged-hf-dizini> <etiket>}"
ETIKET="${2:?kullanım: cp3_merge_dene.sh <merged-hf-dizini> <etiket>}"

[ -d "$MERGED" ] || die "merge dizini yok: $MERGED"
[ -f .env ] && { set -a; . ./.env; set +a; }
export LLM_GATEWAY="${LLM_GATEWAY:-openrouter}"
export LLM_PROVIDER_ORDER="${LLM_PROVIDER_ORDER:-OpenAI}"

TAG="tg_ta_${ETIKET}"
RUN="outputs/eval/cp3-supurme-${ETIKET}"
GGUF="models/gguf/${TAG}-q4_k_m.gguf"

echo "### merge süpürme · varyant=$ETIKET · kapı=$LLM_GATEWAY · sağlayıcı=${LLM_PROVIDER_ORDER}"

# 1) GGUF (varsa atlanır — betik kendi kontrol ediyor)
QUANT=Q4_K_M PURE=0 bash scripts/egitim/setup_llamacpp.sh "$MERGED" "$TAG" || die "GGUF"
[ -f "$GGUF" ] || die "GGUF üretilmedi: $GGUF"

# 2) Üretim — kapı burada. Düşerse `&&` zinciri kırılır, puanlama koşmaz.
THINK_BUDGET=1024 MAXTOK=512 CTX=8192 MODES="m2b m1 m2" OUT_DIR="$RUN" \
  bash scripts/olcum_uretim/cp0_thinking_gen.sh "$GGUF" "${TAG}_th" || {
    echo "🛑 Geçerlilik kapısı düştü ya da üretim kırıldı — PUANLAMA KOŞMADI, para yanmadı."
    exit 2
  }

# 3) Puanlama — 2. gözlem (M2b) + kütle ekseni (M1) + ikinci çekinme ekseni (M2)
#    ⚠️ M2 kapıda YOK ama tek eksenle çekinme okumak bu turda iki kez yanılttı (§18 · §21):
#    cevaplanan-only / tek-eksen metrikler çekinerek kazanmayı ödüllendiriyor.
python -u scripts/puanlama/score_abstention.py --details "$RUN/m2b_${TAG}_th_detail.jsonl" \
    --label "m2b_${TAG}_th" --judge-model gpt-4o-mini --out-dir "$RUN" \
    --source-field context_shown || die "m2b puanlama"

python -u scripts/puanlama/groundedness.py --details "$RUN/m1_${TAG}_th_detail.jsonl" \
    --label "m1_${TAG}_th" --out-dir "$RUN" --mode data --judge-model gpt-4o-mini \
    || die "m1 groundedness"

python -u scripts/puanlama/rescore_answered.py --gnd "$RUN/gnd_m1_${TAG}_th.jsonl" \
    --bench "$RUN/m1_${TAG}_th_detail.jsonl" --label "m1_${TAG}_th" \
    | tee "$RUN/a1_m1_${TAG}_th.txt" || die "A1/kütle"

python -u scripts/puanlama/score_abstention.py --details "$RUN/m2_${TAG}_th_detail.jsonl" \
    --label "m2_${TAG}_th" --judge-model gpt-4o-mini --out-dir "$RUN" \
    --source-field referans || die "m2 puanlama"

echo; echo "✅ süpürme varyantı bitti: $ETIKET → $RUN"
