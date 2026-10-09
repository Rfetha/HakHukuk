#!/usr/bin/env bash
# Şablon düzeldikten sonra model M4-tipi (oracle) bir soruda yanlışlıkla çekimser kalıyor.
# Soru: format artefaktı mı, yoksa istemin çekimserlik talimatının aşırı tetiklenmesi mi?
set -euo pipefail
MODEL="${1:?gguf yolu gerekli}"
PORT=8099
BIN="$HOME/code/llama.cpp/build-cuda/bin/llama-server"
# CHAT_TEMPLATE=<yol> ile yamalı şablon verilebilir; boşsa modelin gömülü şablonu.
TPL_ARG=(); [ -n "${CHAT_TEMPLATE:-}" ] && TPL_ARG=(--chat-template-file "$CHAT_TEMPLATE")
"$BIN" -m "$MODEL" -ngl 99 -fa on -c 8192 "${TPL_ARG[@]}" \
  --host 127.0.0.1 --port "$PORT" > /tmp/abs_server.log 2>&1 &
SRV=$!; trap 'kill $SRV 2>/dev/null || true' EXIT
for i in $(seq 1 90); do curl -sf "http://127.0.0.1:$PORT/health" >/dev/null 2>&1 && break; sleep 2; done

U='KAYNAK MADDE:\nTürk Borçlar Kanunu Madde 146 — Kanunda aksine bir hüküm bulunmadıkça, her alacak on yıllık zamanaşımına tabidir.\n\nSORU: Genel zamanaşımı süresi nedir?'

chat() {
  local sys="${1:-}"
  python3 -c "
import json,sys,urllib.request
sys_msg=sys.argv[1]; user=sys.argv[2].replace('\\\\n','\n')
msgs=([{'role':'system','content':sys_msg}] if sys_msg else [])+[{'role':'user','content':user}]
body=json.dumps({'model':'local','temperature':0,'max_tokens':200,'messages':msgs}).encode()
r=urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:$PORT/v1/chat/completions',body,{'Content-Type':'application/json'}))
d=json.load(r); print('   ', repr(d['choices'][0]['message']['content'][:220]))
" "$sys" "$U"
}

echo "── A) sistemsiz"; chat ""
echo "── B) sistem: sadece rol"; chat "Sen Türk hukuku alanında uzman bir asistansın."
echo "── C) sistem: rol + yalnızca-kaynak"; chat "Sen Türk hukuku alanında uzman bir asistansın. Yalnızca verilen KAYNAK MADDE'ye dayanarak cevap ver."
echo "── D) sistem: rol + yalnızca-kaynak + çekimserlik talimatı (CANON istemi)"; chat "Sen Türk hukuku alanında uzman bir asistansın. Yalnızca verilen KAYNAK MADDE'ye dayanarak cevap ver. Kaynakta cevap yoksa 'Verilen kaynakta bu bilgi yer almıyor.' de."
