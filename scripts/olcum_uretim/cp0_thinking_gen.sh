#!/usr/bin/env bash
# CP0 — düşünce modu ölçümü: 6-mod CANON üretimi, `--thinking on` (ADR-0040, sprint2.md CP0).
#
# Ne yapar: llama-server'ı açar, DEV havuzunda 6 modu üretir, KESİK-CEVAP KAPISINI uygular,
# sunucuyu kapatır. Puanlama AYRI betik: scripts/puanlama/cp0_thinking_score.sh
#
# Kullanım:
#   bash scripts/olcum_uretim/cp0_thinking_gen.sh models/gguf/q35-4b-q4_k_m.gguf base_th          # CP0-a (6 mod)
#   THINK_BUDGET=1024 MAXTOK=512 bash scripts/olcum_uretim/cp0_thinking_gen.sh models/gguf/tg_v1-q4_k_m.gguf tg_v1_th
#
# Ortam: PORT=8080 · CTX=8192 · MAXTOK=4096 · NGL=99 · DEV=data/eval/dev · MODES="m1 m4 m2 m2b m3 m5"
#
# 🚨 Neden bu betik var (docs/record/yurutme-tuzaklari.md):
#   1.1 `--data` düşerse varsayılan EĞİTİM setinin komşusu gelir, hata vermez → burada AÇIK
#   1.2 `--thinking` düşerse ölçülen şey başka moddur                        → burada AÇIK
#   1.4 `--max-chunk-chars 900` eval-mirror değişmezi (ADR-0011)             → burada AÇIK
#   1.5 n/seed CP2 ile birebir aynı, yoksa delta anlamsız                    → tablo aşağıda
#   5.4 `set -e` mesajı yutar                                                → -e YOK, açık `die`
#   5.5 göreli yol `cd`'den sonra kayar                                      → GGUF başta mutlaklaştırılır
#
# ⚠️ CTX: Sprint 1 çıpaları `-c 4096` ile üretildi. Düşünce açıkken 4096 token'lık üretim bütçesi
# istemin YANINA sığmıyor → varsayılan 8192. İstem birebir aynı; değişen yalnız sunucu kapasitesi.
# Bu sapma künyeye yazılır (research_log #42).

set -uo pipefail        # -e BİLEREK yok: tuzak 5.4

die() { echo "❌ $*" >&2; exit 1; }

GGUF_IN="${1:?kullanım: cp0_thinking_gen.sh <gguf> <etiket-son-eki> }"
TAG="${2:?kullanım: cp0_thinking_gen.sh <gguf> <etiket-son-eki> }"

GGUF="$(readlink -f "$GGUF_IN")" || die "GGUF yolu çözülemedi: $GGUF_IN"
[ -f "$GGUF" ] || die "GGUF yok: $GGUF"

PORT="${PORT:-8080}"
CTX="${CTX:-8192}"
MAXTOK="${MAXTOK:-4096}"          # CEVAP bütçesi (bütçeli düşüncede Sprint 1 ile aynı: 512)
THINK_BUDGET="${THINK_BUDGET:-0}" # >0 → zorunlu kapatma (research_log #42); ÖN-KAYITLI seçilir
SERVER_URL="${SERVER_URL:-}"      # verilirse sunucu AÇILMAZ, var olan kullanılır
# Sunucuya geçirilen EK örnekleme bayrakları (ADR-0073). Boş = bugünkü rejim.
# ⚠️ Künyeye BASILIR: parametre künyede görünmüyorsa koşulmuş sayılmaz (tuzak 6.12).
SERVER_EXTRA="${SERVER_EXTRA:-}"
NGL="${NGL:-99}"
DEV="${DEV:-data/eval/dev}"
MODES="${MODES:-m1 m4 m2 m2b m3 m5}"
# Çıktılar KOŞU KLASÖRÜNE yazılır (2026-07-29): her ölçüm turu kendi dizininde + KUNYE.json.
# Düz `outputs/eval` artık yalnız koşu klasörlerini barındırır; oraya yazmak turları karıştırır.
OUT_DIR="${OUT_DIR:-outputs/eval/cp09-butceli-1024-512}"
BIN="${BIN:-$HOME/code/llama.cpp/build-cuda/bin/llama-server}"
LOG="$OUT_DIR/cp0_server_${TAG}.log"

[ -x "$BIN" ] || die "llama-server yok: $BIN"
[ -f "$DEV/core_hard.jsonl" ] || die "DEV havuzu yok: $DEV/core_hard.jsonl"
[ -f "$DEV/trap.jsonl" ]      || die "DEV havuzu yok: $DEV/trap.jsonl"
mkdir -p "$OUT_DIR"

# n = CP2/CP6 ile BİREBİR (tuzak 1.5). N_OVERRIDE yalnız CP0-b'nin gözle-bakma koşusu için.
mode_args() {
  case "$1" in
    m1)  echo "--data $DEV/core_hard.jsonl --distractors 4 --n ${N_OVERRIDE:-80}" ;;
    m4)  echo "--data $DEV/core_hard.jsonl --with-source   --n ${N_OVERRIDE:-80}" ;;
    m2)  echo "--data $DEV/trap.jsonl      --with-source   --n ${N_OVERRIDE:-70}" ;;
    m2b) echo "--data $DEV/core_hard.jsonl --distractors 4 --no-gold --n ${N_OVERRIDE:-80}" ;;
    m3)  echo "--data $DEV/core_hard.jsonl --empty-context --n ${N_OVERRIDE:-80}" ;;
    m5)  echo "--data $DEV/core_hard.jsonl                 --n ${N_OVERRIDE:-80}" ;;   # kör
    # HARNESS AÇIK (sprint3 Adım 4): bağlamı distractor kurgusu değil RETRIEVER seçer.
    # m1 ile tek farkı bu; kırpma, sistem promptu ve üretim rejimi AYNI kalır.
    h1)  echo "--data $DEV/core_hard.jsonl --harness-indeks $HARNESS_INDEKS --harness-k ${HARNESS_K:-5} --n ${N_OVERRIDE:-80}" ;;
    # HARNESS AÇIK + ALTIN ABLASYONU (ADR-0056 Karar 1) = m2b'nin harness-AÇIK karşılığı.
    # h1 ile tek farkı budur; k, kırpma, istem ve rejim AYNI kalır.
    h2b) echo "--data $DEV/core_hard.jsonl --harness-indeks $HARNESS_INDEKS --harness-k ${HARNESS_K:-10} --harness-no-gold --n ${N_OVERRIDE:-80}" ;;
    *)   return 1 ;;
  esac
}

# 🚨 Veri kapısı: h1 istendi ama indeks verilmediyse, model yüklenmeden dur (tuzak 6.2).
case " $MODES " in
  *" h1 "*|*" h2b "*) [ -n "${HARNESS_INDEKS:-}" ] || die "h1/h2b modu HARNESS_INDEKS ister (ör. data/index/mevzuat_bge_m3_s2)";;
esac

# --- KV kimliği: künye ile komut TEK kaynaktan (tuzak 1.12) -----------------
# 1.12 fiilen ısırdı (2026-09-11): künye `KV q8_0/q8_0` diye SABİT DİZE basıyordu, koşu fp16'ydı.
# Bu iki değişken bundan böyle HEM `--cache-type-k/-v` bayraklarına HEM künyeye gider; künyedeki
# değer, koşan komutun kendisinden türer. İkiye ayırırsan tuzağı yeniden kurarsın.
KV_K="q8_0"
KV_V="q8_0"
# Dış sunucuda KV ayarı OKUNAMAZ ve uydurulmaz: SERVER_URL'in portu $PORT'tan bağımsızdır, adres
# uzak olabilir, sunucu konteynerdeyse /proc/<pid> bu ad alanında yoktur. Yanlış okuma, sabit
# dizeyle aynı sınıftan bir yalandır — bu yüzden açıkça BİLİNMİYOR yazılır.
if [ -n "$SERVER_URL" ]; then KV_KUNYE="BİLİNMİYOR (dış sunucu)"; else KV_KUNYE="$KV_K/$KV_V"; fi
# --- /KV kimliği ------------------------------------------------------------

# --- model kimliği doğrulama (tuzak 7.8) ------------------------------------
# 7.8 fiilen ısırdı (2026-09-12): $PORT'ta BAŞKASININ sunucusu vardı (konteynerin
# llama-server'ı); health-check onu "sunucu ayakta" saydı ve 8 kalem YANLIŞ MODELE karşı
# üretildi — hiçbir yerde hata vermeden. Port dinliyor olması KANIT DEĞİLDİR: hangi GGUF'un
# servis edildiği `/v1/models`'tan okunup betiğin açmak istediği GGUF ile karşılaştırılır.
dogrula_model_kimligi() {
  local yanit beklenen gorulen
  yanit="$(curl -sf "$SERVER_URL/models")" || die "$SERVER_URL/models okunamadı — sunucu yok ya da bozuk"
  beklenen="$(basename "$GGUF")"
  gorulen="$(printf '%s' "$yanit" | python3 -c '
import json, sys
try:
    print(json.load(sys.stdin)["data"][0]["id"])
except Exception:
    pass' 2>/dev/null)"
  [ -n "$gorulen" ] || die "$SERVER_URL/models beklenmeyen biçimde yanıt verdi: $yanit"
  case "$gorulen" in
    *"$beklenen"*) : ;;
    *) die "PORT BAŞKA BİR MODELİ servis ediyor (tuzak 7.8) — beklenen '$beklenen', görülen '$gorulen'; port dinliyor olması kanıt değildir" ;;
  esac
}
# --- /model kimliği doğrulama ------------------------------------------------

echo "### künye"
echo "  gguf      : $GGUF"
# Why künyeye: bayrağı elle koşuya gömmek bu hattın en pahalı tuzak sınıfıdır
# (dropped flag) — künyede görünmeyen bayrak sessizce düşer, koşu geçerli görünür.
echo "  ekstra    : ${EXTRA_ARGS:-<yok>}"
echo "  etiket    : *_${TAG}"
echo "  modlar    : $MODES"
echo "  thinking  : on   | cevap bütçesi: $MAXTOK | düşünce bütçesi: ${THINK_BUDGET:-—} | max_chunk_chars: 900 | seed: 3407"
echo "  sunucu    : ctx=$CTX  -ngl $NGL -fa on  KV $KV_KUNYE  port=$PORT
  örnekleme : ${SERVER_EXTRA:-<varsayılan · ceza yok>}
  harness   : ${HARNESS_INDEKS:-KAPALI}${HARNESS_INDEKS:+ · k=${HARNESS_K:-5}}"
echo "  güç       : $(cat /sys/class/power_supply/AC*/online 2>/dev/null | head -1 | sed 's/1/ŞARJDA/;s/0/PİLDE ⚠️/')"  # tuzak 1.6
echo

# ---- sunucu ----------------------------------------------------------------
stop_server() { :; }
if [ -n "$SERVER_URL" ]; then
  echo "ℹ️  var olan sunucu kullanılıyor: $SERVER_URL (yeni süreç açılmadı)"
  dogrula_model_kimligi
  echo "✅ $SERVER_URL doğru modeli servis ediyor: $(basename "$GGUF")"
else
  SERVER_URL="http://127.0.0.1:$PORT/v1"
  "$BIN" -m "$GGUF" -ngl "$NGL" -fa on --no-context-shift \
    --cache-type-k "$KV_K" --cache-type-v "$KV_V" -c "$CTX" \
    --host 127.0.0.1 --port "$PORT" ${SERVER_EXTRA:-} > "$LOG" 2>&1 &
  SRV=$!
  stop_server() { kill "$SRV" 2>/dev/null || true; wait "$SRV" 2>/dev/null || true; }
  trap stop_server EXIT

  for _ in $(seq 1 120); do
    curl -sf "http://127.0.0.1:$PORT/health" >/dev/null 2>&1 && break
    kill -0 "$SRV" 2>/dev/null || { tail -25 "$LOG"; die "llama-server öldü (log: $LOG)"; }
    sleep 2
  done
  curl -sf "http://127.0.0.1:$PORT/health" >/dev/null 2>&1 || { tail -25 "$LOG"; die "sunucu 240s'te açılmadı"; }
  dogrula_model_kimligi
  echo "✅ llama-server hazır (pid $SRV, log $LOG)"
fi
echo

# ---- üretim ----------------------------------------------------------------
for M in $MODES; do
  ARGS="$(mode_args "$M")" || die "bilinmeyen mod: $M"
  echo "==================== $M → ${M}_${TAG} ===================="
  # shellcheck disable=SC2086
  python scripts/olcum_uretim/gen_eval_grounded.py \
    --server-url "$SERVER_URL" --server-model local \
    --thinking on --max-new-tokens "$MAXTOK" --think-budget "$THINK_BUDGET" \
    --max-chunk-chars 900 --seed 3407 \
    --label "${M}_${TAG}" --out-dir "$OUT_DIR" $ARGS ${EXTRA_ARGS:-} \
    || die "$M üretimi başarısız — sonraki modlar KOŞULMADI"
  echo
done

stop_server
trap - EXIT

# ---- 🚨 GEÇERLİLİK KAPISI (ADR-0040): kesik-cevap > %5 → koşu GEÇERSİZ --------
echo "==================== GEÇERLİLİK KAPISI ===================="
python - "$OUT_DIR" "$TAG" $MODES <<'PY'
import json, sys
out_dir, tag, modes = sys.argv[1], sys.argv[2], sys.argv[3:]
tot = trunc = 0; tok_sum = tok_n = 0; think_n = forced_n = 0
print(f"{'mod':<5} {'n':>4} {'kesik':>6} {'%':>6} {'ort tok':>8} {'düşünen':>8} {'zorla':>6}")
for m in modes:
    rows = [json.loads(l) for l in open(f"{out_dir}/{m}_{tag}_detail.jsonl", encoding="utf-8") if l.strip()]
    t = sum(1 for r in rows if r.get("finish_reason") == "length")
    tk = [r["completion_tokens"] for r in rows if r.get("completion_tokens")]
    th = sum(1 for r in rows if (r.get("reasoning_len") or 0) > 0)
    fc = sum(1 for r in rows if r.get("forced_close"))
    tot += len(rows); trunc += t; tok_sum += sum(tk); tok_n += len(tk); think_n += th; forced_n += fc
    print(f"{m:<5} {len(rows):>4} {t:>6} {100*t/max(1,len(rows)):>5.1f}% "
          f"{(sum(tk)/len(tk) if tk else 0):>8.1f} {th:>7} {fc:>6}")
pct = 100 * trunc / max(1, tot)
print(f"\nTOPLAM  n={tot}  kesik={trunc} (%{pct:.1f})  "
      f"ort completion_tokens={tok_sum/max(1,tok_n):.1f}  düşünce kanalı kullanan={think_n}/{tot}  "
      f"zorla kapatılan={forced_n}/{tot}")
if think_n == 0:
    print("\n🚨 HİÇBİR cevapta reasoning_content YOK → `enable_thinking` bayrağı işlemedi olabilir "
          "(#38 mekanizması). diag_chat_template.sh ile render'ı GÖZLE doğrula. SONUÇ OKUNMAZ.")
    sys.exit(2)
if pct > 5.0:
    print(f"\n🚨 KOŞU GEÇERSİZ — kesik-cevap %{pct:.1f} > %5 eşiği (ADR-0040 geçerlilik ön şartı).\n"
          "   Sonuç OKUNMAZ. MAXTOK büyütülüp tekrar koşulur; puanlamaya para harcanmaz.")
    sys.exit(2)
print("\n✅ Geçerlilik kapısı geçildi — sonuç okunabilir. Sıradaki: scripts/puanlama/cp0_thinking_score.sh")
PY
