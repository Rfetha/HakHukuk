#!/usr/bin/env bash
# Modal koşusunu periyodik yoklar; bitince çıkar.
#
#   bash scripts/olcum_uretim/watch_run.sh <app-id> [dakika] [run-adi]
#   bash scripts/olcum_uretim/watch_run.sh ap-4p3NmNBunsOzxH1Uw20OPi 10 tg
#
# Why: `modal app logs` takip modunda bloke eder — arka planda bırakınca ne bittiğini haber verir
# ne de ilerleme özetler. Bu döngü her turda TEK ilerleme satırı basar ve çıktı volume'de
# göründüğü an durur.
set -uo pipefail

APP="${1:?app-id gerekli — 'modal app list' ile al}"
MIN="${2:-10}"
RUN="${3:-tg}"

echo "[watch] $APP · her $MIN dk · çıktı beklenen: hukuk-outputs:/$RUN"

while :; do
    TS=$(date +%H:%M)

    # Why: dizinin VARLIĞI yetmez — trainer `/$RUN`'ı koşu başında boş olarak yaratıyor.
    # Bitiş işareti adaptör dosyasının kendisi.
    if modal volume ls hukuk-outputs "/$RUN" 2>/dev/null | grep -q "adapter_model"; then
        echo "[$TS] ✅ BİTTİ — /$RUN volume'de. İndir:"
        echo "        modal volume get hukuk-outputs /$RUN ./outputs/$RUN"
        modal volume ls hukuk-outputs "/$RUN" 2>/dev/null | tail -20
        break
    fi

    LAST=$(timeout 60 modal app logs "$APP" 2>/dev/null \
           | grep -vF "Loading weights" \
           | grep -E "s/it|it/s|loss|Traceback|Error|🚫" \
           | tail -1)
    echo "[$TS] ${LAST:-(ilerleme satırı yok — yükleme/tokenize sürüyor olabilir)}"

    sleep "$((MIN * 60))"
done
