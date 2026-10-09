#!/usr/bin/env bash
# Tanı: llama-server sohbet şablonunu nasıl işliyor + EOG kümesinde ne var?
# Gerekçe (2026-07-24): 12B duman testinde model durmadı, '<|turn>user' üretip
# kendi kendine konuşmaya devam etti — bir CANON koşusunu sessizce çöpe çevirecek hata.
#
# Genişletme (2026-07-24, CP0 / Qwen3.5): iki eksen eklendi, çünkü ikisi de sessizce bozar:
#   (a) --jinja VAR/YOK — llama.cpp --jinja'sız modelin GÖMÜLÜ jinja'sını kullanmaz,
#       kendi C++ şablon tespitine düşer. Düşünen modellerde bu, üretim isteminin
#       sonundaki düşünce kanalını tamamen kaybettirebilir. Hata vermez.
#   (b) enable_thinking bayrağı ÇALIŞIYOR mu, yoksa SESSİZCE YOK SAYILIYOR mu —
#       #38'in tam mekanizması. Ayrım için bayrak true/false render'ları KARŞILAŞTIRILIR:
#       ikisi birebir aynıysa bayrak yok sayılıyordur.
#
# Kullanım: bash scripts/olcum_uretim/diag_chat_template.sh <gguf>
set -euo pipefail
MODEL="${1:?gguf yolu gerekli}"
PORT="${PORT:-8091}"
BIN="$HOME/code/llama.cpp/build-cuda/bin/llama-server"
OUT="${OUT_DIR:-/tmp/diag_tpl}"
mkdir -p "$OUT"

MSGS='{"messages":[{"role":"system","content":"SISTEM METNI"},{"role":"user","content":"KULLANICI SORUSU"}]}'

render() {   # render <etiket> <ekstra-json-alanlari>
  local tag="$1" extra="${2:-}"
  local body="$MSGS"
  [ -n "$extra" ] && body=$(python3 -c "
import json,sys; d=json.loads(sys.argv[1]); d.update(json.loads(sys.argv[2])); print(json.dumps(d))" "$MSGS" "$extra")
  curl -s "http://127.0.0.1:$PORT/apply-template" -H 'Content-Type: application/json' -d "$body" \
    | python3 -c "import sys,json;print(json.load(sys.stdin)['prompt'],end='')" > "$OUT/$tag.txt" 2>/dev/null \
    || { echo "  ❌ $tag: /apply-template hata verdi"; return 0; }
  echo "  → $tag:"
  python3 -c "import sys;print('    '+repr(open(sys.argv[1]).read()))" "$OUT/$tag.txt"
}

boot() {     # boot <server-ek-argumanlari...>
  "$BIN" -m "$MODEL" -ngl 99 -fa on -c 4096 --host 127.0.0.1 --port "$PORT" "$@" \
    > "$OUT/server.log" 2>&1 &
  SRV=$!
  for i in $(seq 1 90); do
    curl -sf "http://127.0.0.1:$PORT/health" >/dev/null 2>&1 && return 0
    kill -0 $SRV 2>/dev/null || { echo "❌ server öldü:"; tail -20 "$OUT/server.log"; return 1; }
    sleep 2
  done
  echo "❌ server 180s'te açılmadı"; tail -20 "$OUT/server.log"; return 1
}
stop() { kill ${SRV:-0} 2>/dev/null || true; wait ${SRV:-0} 2>/dev/null || true; sleep 1; }
trap stop EXIT

echo "==================== A) --jinja YOK (llama.cpp'nin kendi tespiti) ===================="
boot || exit 1
render "A_nojinja"
echo
echo "### /props:"
curl -s "http://127.0.0.1:$PORT/props" | python3 -c "
import sys,json; d=json.load(sys.stdin)
print('  bos:',repr(d.get('bos_token')),' eos:',repr(d.get('eos_token')))
print('  chat_template (ilk 160):',repr((d.get('chat_template') or '')[:160]))"
stop

echo
echo "==================== B) --jinja VAR (modelin GÖMÜLÜ şablonu) ===================="
boot --jinja || exit 1
render "B_jinja"
render "B_jinja_think_true"  '{"chat_template_kwargs":{"enable_thinking":true}}'
render "B_jinja_think_false" '{"chat_template_kwargs":{"enable_thinking":false}}'
stop

echo
echo "==================== KARAR TABLOSU ===================="
cmp_files() {  # cmp_files <a> <b> <ayni-mesaj> <farkli-mesaj>
  if [ -f "$OUT/$1.txt" ] && [ -f "$OUT/$2.txt" ]; then
    if cmp -s "$OUT/$1.txt" "$OUT/$2.txt"; then echo "  $3"; else echo "  $4"; fi
  else echo "  ⚠️  $1/$2 render'ı üretilemedi — elle bak"; fi
}
echo "[jinja ekseni]"
cmp_files A_nojinja B_jinja \
  "⚠️  --jinja VAR/YOK aynı render → llama.cpp gömülü şablonu zaten kullanıyor olabilir; yine de GÖZLE doğrula" \
  "🚨 --jinja VAR/YOK FARKLI render → --jinja'sız koşmak BAŞKA bir istem demektir. Eval/eğitim aynı bayrakla koşmalı."
echo "[düşünce bayrağı ekseni]"
cmp_files B_jinja_think_true B_jinja_think_false \
  "🚨 enable_thinking true/false AYNI render → bayrak SESSİZCE YOK SAYILIYOR (#38 mekanizması). Yamalı .jinja gerekir." \
  "✅ enable_thinking true/false FARKLI render → bayrak gerçekten çalışıyor"
echo
echo "### server log — token/EOG/şablon uyarıları:"
grep -iE "control-looking|eog|eos|template|jinja|warn" "$OUT/server.log" | head -15 || true
echo
echo "### render dosyaları: $OUT/*.txt  (gözle okumak ZORUNLU — kapı 2 budur)"
