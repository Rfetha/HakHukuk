#!/usr/bin/env bash
# CP1 — ADR-0041: groundedness hakem istemine kaynak-seçimi meta-iddia muafiyeti eklendi;
# ÜÇ ÖZNE BİRDEN yeniden puanlanır (tek kola uygulamak sayıyı doğrudan bizim lehimize kaydırır).
#
# Üretim YENİDEN YAPILMAZ — CP0.9'un detay dosyaları girdi, değişen tek şey hakem istemi.
# Bu yüzden --details cp09 klasörünü, --out-dir CP1 klasörünü gösterir: eski skorlar
# yerinde kalır (ADR-0041 m.2, kontrol olarak saklanır).
#
# 🚨 Tuzaklar (docs/record/yurutme-tuzaklari.md):
#   2.11 `.env` yüklenmez → hakem anahtarı yok             → set -a; . ./.env
#   2.7  sağlayıcı pinlenmemiş → kıyaslanamaz sayı          → LLM_GATEWAY=openai PİNLİ
#   2.3  A1 yerine ham ortalama → çekinme macro'yu çeker    → rescore_answered ZORUNLU
#   5.4  `set -e` mesajı yutar                              → -e yok, die() var
#
# Kullanım: bash scripts/puanlama/cp/cp1_rescore_meta.sh

set -uo pipefail        # -e BİLEREK yok: tuzak 5.4

die() { echo "❌ $*" >&2; exit 1; }

SRC_DIR="${SRC_DIR:-outputs/eval/cp/cp09-butceli-1024-512}"
OUT_DIR="${OUT_DIR:-outputs/eval/cp/cp1-hakem-meta-iddia}"
TAGS="${TAGS:-base_th tg_v1_th gem_th}"
MODE="m1"   # meta-cümle YALNIZ çok-kaynaklı modda görülüyor (M4/M5'te 0/80 — ölçüldü)

if [ -f .env ]; then set -a; . ./.env; set +a; else die ".env yok — hakem anahtarı yüklenemez"; fi
[ -n "${OPENAI_API_KEY:-}" ] || die "OPENAI_API_KEY boş"
export LLM_GATEWAY="${LLM_GATEWAY:-openai}"
export GND_JUDGE="${GND_JUDGE:-gpt-4o-mini}"

mkdir -p "$OUT_DIR"
echo "### CP1 · hakem=$GND_JUDGE · gateway=$LLM_GATEWAY · mod=$MODE · özneler=$TAGS"
echo "### girdi=$SRC_DIR  →  çıktı=$OUT_DIR"
echo

for T in $TAGS; do
  D="$SRC_DIR/${MODE}_${T}_detail.jsonl"
  [ -f "$D" ] || die "detay yok: $D"
done

for T in $TAGS; do
  L="${MODE}_${T}"
  echo "==================== $L ===================="
  python scripts/puanlama/skorlayici/groundedness.py --details "$SRC_DIR/${L}_detail.jsonl" --label "$L" \
    --mode data --out-dir "$OUT_DIR" || die "$L groundedness başarısız"
  python scripts/puanlama/skorlayici/rescore_answered.py --gnd "$OUT_DIR/gnd_${L}.jsonl" \
    --bench "$SRC_DIR/${L}_detail.jsonl" --label "$L" \
    | tee "$OUT_DIR/a1_${L}.txt" || die "$L rescore başarısız"
  echo
done

echo "==================== ESKİ ↔ YENİ (ADR-0041 m.2/m.3) ===================="
python scripts/puanlama/cp/cp1_delta.py --old "$SRC_DIR" --new "$OUT_DIR" --tags "$TAGS" --mode "$MODE"
