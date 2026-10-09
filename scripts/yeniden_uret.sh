#!/usr/bin/env bash
# Yayımlanan manşet sayıyı (kütle) SIFIRDAN yeniden üretir — tek komut.
#
# ⚠️ Neden var: 2026-09-07'ye kadar %80,1 kütlesini modeli indiren HİÇ KİMSE yeniden
# üretemiyordu. İstem `gen_eval_grounded.py` içindeydi (Görev 5 çözdü), indeks git'te yok
# (Görev 8 çözecek) ve komut zinciri hiçbir yerde TEK PARÇA yazılı değildi.
#
# Kullanım:
#   bash scripts/yeniden_uret.sh                       # tam koşu (80 kalem)
#   N_OVERRIDE=10 bash scripts/yeniden_uret.sh         # hızlı duman koşusu
#   ETIKET=deneme bash scripts/yeniden_uret.sh
#
# ⛔ Bu script REJİMİ SABİTLER. Buradaki hiçbir sayıyı komut satırından değiştirme —
#    uyuşmazlık hata VERMEZ, yalnız kıyası geçersiz kılar (bkz. docs/record/yurutme-tuzaklari.md).
set -euo pipefail

ETIKET="${ETIKET:-yeniden_uretim}"
OUT_DIR="${OUT_DIR:-outputs/eval/yeniden-uretim}"
GGUF="${GGUF:-models/gguf/tgta_v1-q4_k_m.gguf}"
INDEKS="${INDEKS:-data/index/mevzuat_bge_m3_s2}"
HAKEM="${HAKEM:-openai/gpt-4o-mini}"      # ADR-0074: BAĞLAYICI hakem — değiştirme

# ── Rejim değişmezleri (ADR-0043 · 0057 · 0067 · 0068 · 0070) ────────────────
export MODES="h1"
export HARNESS_INDEKS="$INDEKS"
export HARNESS_K=10
export THINK_BUDGET=1024      # düşünce
export MAXTOK=512             # cevap  ⇒ toplam üretim bütçesi 1536
export CTX=8192
export OUT_DIR

echo "=== 0/5 · ön koşullar ==="
[ -f "$GGUF" ]   || { echo "🚫 GGUF yok: $GGUF"; exit 1; }
[ -d "$INDEKS" ] || { echo "🚫 indeks yok: $INDEKS — bkz. hakhukuk/kurulum.py (Görev 8)"; exit 1; }
[ -f .env ]      || { echo "🚫 .env yok — hakem anahtarı gerekli"; exit 1; }
command -v llama-server >/dev/null || { echo "🚫 llama-server PATH'te yok"; exit 1; }
echo "  gguf   : $GGUF"
echo "  indeks : $INDEKS"
echo "  hakem  : $HAKEM  (ADR-0074 · bağlayıcı)"
echo "  güç    : $(cat /sys/class/power_supply/AC*/online 2>/dev/null | head -1 | sed 's/1/ŞARJDA/;s/0/PİLDE ⚠️ (GPU 180 MHz'\''e kısılır — 12× yavaş)/')"

echo "=== 1/5 · üretim (llama-server açılır, h1 koşulur, sunucu kapanır) ==="
bash scripts/olcum_uretim/cp0_thinking_gen.sh "$GGUF" "$ETIKET"

DETAY="$OUT_DIR/h1_${ETIKET}_detail.jsonl"
[ -f "$DETAY" ] || { echo "🚫 üretim çıktısı yok: $DETAY"; exit 1; }

echo "=== 2/5 · geçerlilik kapıları (koşu GEÇERSİZ olabilir — sayı üretmeden ÖNCE bak) ==="
source ~/code/global_venv/bin/activate
python - "$DETAY" <<'PY'
import json, sys
sys.path[:0] = ["scripts", "scripts/olcum_uretim", "scripts/erisim_korpus"]
from recall_kapisi import recall_at_10  # kusur 33 (ADR-0083 §A) düzeltmesi

satirlar = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
n = len(satirlar)
kesik = sum(1 for r in satirlar if (r.get("finish_reason") or "") == "length")
altin_orani = recall_at_10(satirlar)
print(f"  n                = {n}")
print(f"  kesiklik         = {kesik}/{n} = {kesik/n:.1%}   eşik %5 (ADR-0040)")
print(f"  recall@10        = {altin_orani:.4f}                 beklenen 0,9500")
kotu = []
if kesik / n > 0.05:
    kotu.append(f"kesiklik %{kesik/n*100:.1f} > %5 ⇒ koşu GEÇERSİZ")
if abs(altin_orani - 0.95) > 1e-9:
    kotu.append(f"recall@10 {altin_orani:.4f} ≠ 0,9500 ⇒ harness OYNAMIŞ, kıyas geçersiz")
if kotu:
    print("\n🚫 GEÇERLİLİK KAPISI DÜŞTÜ — sayı üretilmez:")
    for k in kotu:
        print("   ·", k)
    sys.exit(1)
print("  ✅ iki kapı da geçti")
PY

echo "=== 3/5 · puanlama (hakem) ==="
set -a && . ./.env && set +a
export OPENAI_API_KEY="$OPENROUTER_API_KEY"
LLM_GATEWAY=openrouter LLM_PROVIDER_ORDER=OpenAI \
python scripts/puanlama/groundedness.py \
  --details "$DETAY" --label "h1_${ETIKET}" --mode data \
  --judge-model "$HAKEM" --out-dir "$OUT_DIR"

echo "=== 4/5 · manşet tablo ==="
python scripts/puanlama/harness_tablo.py \
  --details "$DETAY" --gnd "$OUT_DIR/gnd_h1_${ETIKET}.jsonl" \
  --out "$OUT_DIR/harness_tablo.json"

echo "=== 5/5 · sonuç ==="
python - "$OUT_DIR/harness_tablo.json" <<'PY'
import json, sys
t = json.load(open(sys.argv[1], encoding="utf-8"))["kutle_ekseni"]
print(f"  coverage      {t['coverage']:.4f}")
print(f"  A1            {t['A1_cevaplanan']:.4f}")
print(f"  KÜTLE         {t['kutle_tum']:.4f}    ← manşet")
print()
print("  çıpa (2026-09-06, F0.2): kütle 0,8011")
sapma = abs(t["kutle_tum"] - 0.8011) * 100
print(f"  sapma         {sapma:.2f} puan   (hakem gürültü tabanı 0,30 puan)")
print("  ⛔ Sapma 0,30 puanı aşıyorsa DUR — fark KAYNAKLANMADAN yayımlanmaz."
      if sapma > 0.30 else "  ✅ gürültü tabanının içinde")
PY
