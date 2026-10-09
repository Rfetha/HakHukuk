#!/usr/bin/env bash
# A4 duman testi — llama-server'ı aç, gerçek bir RAG istemi sor, VRAM'i ölç, kapat.
# Hepsi TEK süreç ömründe: arka plan sunucuları oturum sonunda toparlanıyor (SIGTERM),
# bu yüzden ölçüm ve istek aynı çağrının içinde yapılmalı.
#
# Kullanım: bash scripts/olcum_uretim/smoke_llamacpp.sh <gguf> [ctx]
#   CHAT_TEMPLATE=configs/<base>.jinja bash scripts/olcum_uretim/smoke_llamacpp.sh <gguf> 131072
set -euo pipefail
MODEL="${1:?gguf yolu gerekli}"
CTX="${2:-8192}"
PORT=8089
BIN="$HOME/code/llama.cpp/build-cuda/bin/llama-server"

base=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits)
echo "### VRAM taban (server öncesi): ${base} MiB"

# ⚠️ ÖĞRENİLMİŞ DERS (2026-07-24, Gemma 4): llama.cpp'nin minja motoru bazı gömülü chat
# şablonlarını YANLIŞ render eder. Somut vaka: `enable_thinking is defined` dalı yanlış
# değerlendirildi → üretim isteminin sonundaki boş düşünce kanalı yazılmadı → model DURMADI,
# girdiyi tekrarladı, ayrıştırıcı 500 verdi. Bir CANON koşusunu sessizce çöpe çevirecek hata.
#
# → Her YENİ base için: `diag_chat_template.sh` ile /apply-template render'ını GÖZLE doğrula.
#   Gömülü şablon bozuksa yamalı bir .jinja yaz ve CHAT_TEMPLATE ile ver.
TPL="${CHAT_TEMPLATE:-}"
TPL_ARG=()
if [ -n "$TPL" ]; then
  [ -f "$TPL" ] || { echo "❌ CHAT_TEMPLATE bulunamadı: $TPL"; exit 1; }
  TPL_ARG=(--chat-template-file "$TPL")
  echo "### chat şablonu: $TPL"
else
  echo "### chat şablonu: modelin GÖMÜLÜ şablonu (⚠️ render'ı doğrulanmalı)"
fi

"$BIN" -m "$MODEL" -ngl 99 -fa on --no-context-shift \
  --cache-type-k q8_0 --cache-type-v q8_0 -c "$CTX" "${TPL_ARG[@]}" \
  --host 127.0.0.1 --port "$PORT" > /tmp/smoke_server.log 2>&1 &
SRV=$!
trap 'kill $SRV 2>/dev/null || true' EXIT

for i in $(seq 1 120); do
  curl -sf "http://127.0.0.1:$PORT/health" >/dev/null 2>&1 && break
  kill -0 $SRV 2>/dev/null || { echo "❌ server öldü:"; tail -5 /tmp/smoke_server.log; exit 1; }
  sleep 2
done

peak=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits)
echo "### VRAM yüklü: ${peak} MiB  →  SERVER PAYI: $(( peak - base )) MiB ($(echo "scale=2; ($peak-$base)/1024" | bc) GiB)"
echo "### ctx=$CTX"

t0=$(date +%s.%N)
resp=$(curl -s "http://127.0.0.1:$PORT/v1/chat/completions" -H 'Content-Type: application/json' -d @- <<'JSON'
{"model":"local","temperature":0,"max_tokens":220,"messages":[
{"role":"system","content":"Sen Türk hukuku alanında uzman bir asistansın. Yalnızca verilen KAYNAK MADDE'ye dayanarak cevap ver. Kaynakta cevap yoksa 'Verilen kaynakta bu bilgi yer almıyor.' de."},
{"role":"user","content":"KAYNAK MADDE:\nTürk Borçlar Kanunu Madde 146 — Kanunda aksine bir hüküm bulunmadıkça, her alacak on yıllık zamanaşımına tabidir.\n\nSORU: Genel zamanaşımı süresi nedir?"}]}
JSON
)
t1=$(date +%s.%N)

python3 - "$resp" "$t0" "$t1" <<'PY'
import json, sys
d = json.loads(sys.argv[1]); dt = float(sys.argv[3]) - float(sys.argv[2])
u = d.get("usage", {})
print("### CEVAP:"); print(d["choices"][0]["message"]["content"])
ct = u.get("completion_tokens", 0)
print(f"### usage: {u}")
print(f"### süre: {dt:.1f}s · {ct/dt:.1f} tok/s" if ct else f"### süre: {dt:.1f}s")
PY
