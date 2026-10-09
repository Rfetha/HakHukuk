#!/usr/bin/env bash
# CP0.9 — rakip çıpasının BÜTÇELİ DÜŞÜNCE kipinde yeniden koşulması (ADR-0043 m.3-m.4).
#
# Sprint 1'in `run_gemini_benchmark.sh`'ı DOKUNULMADAN duruyor: o, thinking-off protokolünün
# kaydı. Bu betik yeni protokolün karşılığı — aynı 6 mod, aynı DEV havuzu, aynı n/seed/klip,
# tek fark düşünce bütçesi.
#
# Kullanım:
#   bash scripts/olcum_uretim/cp09_gemini_gen.sh gem_th
#   MODEL=google/gemini-3.1-flash-lite RBUDGET=1024 MAXTOK=512 bash scripts/olcum_uretim/cp09_gemini_gen.sh gem_th
#
# 🚨 Neden bu betik var (docs/record/yurutme-tuzaklari.md):
#   1.1 `--data` düşerse EĞİTİM setinin komşusu gelir, hata vermez        → burada AÇIK
#   1.4 `--max-chunk-chars 900` eval-mirror değişmezi (ADR-0011)          → burada AÇIK
#   1.5 n/seed base ile birebir aynı olmalı, yoksa delta anlamsız         → mode_args ortak
#   1.7 rakip farklı kod yolundan geçerse kıyaslanamaz                    → aynı gen_eval_grounded.py
#   2.7 sağlayıcı pinlenmemiş → farklı yığın, sessizce kıyaslanamaz sayı  → provider künyeye yazılır
#   5.4 `set -e` mesajı yutar                                             → -e YOK, açık `die`
#
# ⚠️ ADALET (ADR-0043 m.3): düşünce bütçesi REJİM DEĞİŞMEZİ — "bütün özneler, bütün kollar,
# bütün rakipler aynı bütçeyle". Bizde zorunlu kapatma gerekiyor (Qwen sonlanmıyor), Gemini'de
# bütçeyi sunucu uyguluyor (`reasoning.max_tokens`). Aynı sayı, farklı mekanizma; ikisi de
# künyeye `reasoning_tokens` olarak yazılır. Rakibi düşüncesiz koşmak sapmayı BİZİM LEHİMİZE
# kaydırırdı (tuzak 2.2'nin sınıfı).

set -uo pipefail        # -e BİLEREK yok: tuzak 5.4

die() { echo "❌ $*" >&2; exit 1; }

TAG="${1:?kullanım: cp09_gemini_gen.sh <etiket-son-eki>   (örn. gem_th)}"

cd /home/ersoy/code/Hukuk-SLM || die "repo dizinine geçilemedi"
[ -f .env ] || die ".env yok — OPENROUTER_API_KEY yüklenemez"
set -a; . ./.env; set +a
[ -n "${OPENROUTER_API_KEY:-}" ] || die "OPENROUTER_API_KEY boş"

MODEL="${MODEL:-google/gemini-3.1-flash-lite}"
SRV="${SRV:-https://openrouter.ai/api/v1}"
RBUDGET="${RBUDGET:-1024}"        # ÖN-KAYITLI: bizim --think-budget ile aynı
MAXTOK="${MAXTOK:-512}"           # ÖN-KAYITLI: cevap bütçesi, Sprint 1 ile aynı
DEV="${DEV:-data/eval/dev}"
MODES="${MODES:-m1 m4 m2 m2b m3 m5}"
OUT_DIR="${OUT_DIR:-outputs/eval/cp/cp09-butceli-1024-512}"   # koşu klasörü (2026-07-29)

[ -f "$DEV/core_hard.jsonl" ] || die "DEV havuzu yok: $DEV/core_hard.jsonl"
[ -f "$DEV/trap.jsonl" ]      || die "DEV havuzu yok: $DEV/trap.jsonl"
mkdir -p "$OUT_DIR"

# gen_eval_grounded HTTP yolu api_key'i OPENAI_API_KEY'den okur → OpenRouter'a yönlendir.
export OPENAI_API_KEY="$OPENROUTER_API_KEY"

# n = base/τ_g koşusuyla BİREBİR (tuzak 1.5) — cp0_thinking_gen.sh ile aynı tablo.
mode_args() {
  case "$1" in
    m1)  echo "--data $DEV/core_hard.jsonl --distractors 4 --n 80" ;;
    m4)  echo "--data $DEV/core_hard.jsonl --with-source   --n 80" ;;
    m2)  echo "--data $DEV/trap.jsonl      --with-source   --n 70" ;;
    m2b) echo "--data $DEV/core_hard.jsonl --distractors 4 --no-gold --n 80" ;;
    m3)  echo "--data $DEV/core_hard.jsonl --empty-context --n 80" ;;
    m5)  echo "--data $DEV/core_hard.jsonl                 --n 80" ;;   # kör
    *)   return 1 ;;
  esac
}

echo "### künye"
echo "  rakip     : $MODEL @ $SRV"
echo "  etiket    : *_${TAG}"
echo "  modlar    : $MODES"
echo "  düşünce   : reasoning.max_tokens=$RBUDGET (sunucu-taraflı) | cevap bütçesi: $MAXTOK"
echo "  değişmez  : max_chunk_chars 900 | seed 3407 | n = 80/80/70/80/80/80"
echo "  sağlayıcı : provider künyesi aşağıda ilk çağrıdan okunur (tuzak 2.7)"
echo

# ---- sağlayıcı pini (tuzak 2.7): hangi yığında koştuğu SAYIDAN ÖNCE yazılır ----
python - "$MODEL" "$SRV" "$RBUDGET" <<'PY' || die "sağlayıcı probu başarısız — koşu başlatılmadı"
import json, os, sys, urllib.request
model, srv, rb = sys.argv[1], sys.argv[2], int(sys.argv[3])
req = urllib.request.Request(srv.rstrip("/") + "/chat/completions",
    data=json.dumps({"model": model, "messages": [{"role": "user", "content": "test"}],
                     "max_tokens": rb + 32, "temperature": 0,
                     "reasoning": {"max_tokens": rb}}).encode(),
    headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
             "Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=120) as r:
    d = json.load(r)
u = d.get("usage", {})
print(f"  provider  : {d.get('provider')}  (model={d.get('model')})")
print(f"  probe     : completion={u.get('completion_tokens')} "
      f"reasoning={(u.get('completion_tokens_details') or {}).get('reasoning_tokens')}")
PY
echo

# ---- üretim ----------------------------------------------------------------
for M in $MODES; do
  ARGS="$(mode_args "$M")" || die "bilinmeyen mod: $M"
  echo "==================== $M → ${M}_${TAG} ===================="
  # shellcheck disable=SC2086
  python scripts/olcum_uretim/gen_eval_grounded.py \
    --server-url "$SRV" --server-model "$MODEL" \
    --thinking none --reasoning-budget "$RBUDGET" --max-new-tokens "$MAXTOK" \
    --max-chunk-chars 900 --seed 3407 \
    --label "${M}_${TAG}" --out-dir "$OUT_DIR" $ARGS \
    || die "$M üretimi başarısız — sonraki modlar KOŞULMADI"
  echo
done

# ---- 🚨 GEÇERLİLİK KAPISI: kesik-cevap > %5 → koşu GEÇERSİZ (base ile aynı kural) ----
echo "==================== GEÇERLİLİK KAPISI ===================="
python - "$OUT_DIR" "$TAG" $MODES <<'PY'
import json, sys
out_dir, tag, modes = sys.argv[1], sys.argv[2], sys.argv[3:]
tot = trunc = 0; tok_sum = tok_n = 0; rt_sum = rt_n = 0
print(f"{'mod':<5} {'n':>4} {'kesik':>6} {'%':>6} {'ort tok':>8} {'ort düşünce':>12}")
for m in modes:
    rows = [json.loads(l) for l in open(f"{out_dir}/{m}_{tag}_detail.jsonl", encoding="utf-8") if l.strip()]
    t = sum(1 for r in rows if r.get("finish_reason") == "length")
    tk = [r["completion_tokens"] for r in rows if r.get("completion_tokens")]
    rt = [r["reasoning_tokens"] for r in rows if r.get("reasoning_tokens") is not None]
    tot += len(rows); trunc += t; tok_sum += sum(tk); tok_n += len(tk); rt_sum += sum(rt); rt_n += len(rt)
    print(f"{m:<5} {len(rows):>4} {t:>6} {100*t/max(1,len(rows)):>5.1f}% "
          f"{(sum(tk)/len(tk) if tk else 0):>8.1f} {(sum(rt)/len(rt) if rt else 0):>12.1f}")
pct = 100 * trunc / max(1, tot)
print(f"\nTOPLAM  n={tot}  kesik={trunc} (%{pct:.1f})  ort completion_tokens={tok_sum/max(1,tok_n):.1f}  "
      f"ort reasoning_tokens={rt_sum/max(1,rt_n):.1f} (bildirilen {rt_n}/{tot})")
if rt_n and rt_sum == 0:
    print("\n🚨 reasoning_tokens HER cevapta 0 → bütçe bayrağı İŞLEMEDİ; rakip düşüncesiz ölçülmüş "
          "olur ve sapma BİZİM LEHİMİZE kayar (tuzak 2.2). SONUÇ OKUNMAZ.")
    sys.exit(2)
if pct > 5.0:
    print(f"\n🚨 KOŞU GEÇERSİZ — kesik-cevap %{pct:.1f} > %5 eşiği. Sonuç OKUNMAZ; "
          "puanlamaya para harcanmaz.")
    sys.exit(2)
print("\n✅ Geçerlilik kapısı geçildi. Sıradaki: bash scripts/puanlama/cp0_thinking_score.sh " + tag)
PY
