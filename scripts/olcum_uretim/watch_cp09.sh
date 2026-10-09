#!/usr/bin/env bash
# CP0.9 üretimini periyodik yoklar; üç özne de bitince çıkar.
#
#   bash scripts/olcum_uretim/watch_cp09.sh [dakika]
#   bash scripts/olcum_uretim/watch_cp09.sh 15
#
# Why: üretim saatler sürüyor ve `tail -f` tek satır akıtıyor — ne hangi öznenin nerede olduğunu
# ne de KESİK ORANINI gösteriyor. Kesik oranı burada kritik: >%5 koşuyu geçersiz kılıyor
# (ADR-0040 geçerlilik ön şartı) ve bunu üretim bittikten SONRA öğrenmek saatleri yakar.
# Bu döngü her turda özne başına tek satır + birikimli kesik oranı basar.
set -uo pipefail
cd /home/ersoy/code/Hukuk-SLM || exit 1

MIN="${1:-15}"
TAGS="${TAGS:-base_th tg_v1_th gem_th}"
LOG="${LOG:-outputs/eval/cp09_watch.log}"

echo "[watch] CP0.9 · her $MIN dk · özneler: $TAGS · log: $LOG" | tee -a "$LOG"

while :; do
    SNAP=$(python - $TAGS <<'PY'
import json, os, sys
NEED = {"m1": 80, "m4": 80, "m2": 70, "m2b": 80, "m3": 80, "m5": 80}
TOTAL = sum(NEED.values())
done_all = True
for tag in sys.argv[1:]:
    n = trunc = tok_s = tok_n = forced = 0
    parts = []
    for m, need in NEED.items():
        p = f"outputs/eval/{m}_{tag}_detail.jsonl"
        if not os.path.exists(p):
            parts.append(f"{m}:—"); continue
        rows = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
        n += len(rows)
        trunc += sum(1 for r in rows if r.get("finish_reason") == "length")
        forced += sum(1 for r in rows if r.get("forced_close"))
        tk = [r["completion_tokens"] for r in rows if r.get("completion_tokens")]
        tok_s += sum(tk); tok_n += len(tk)
        parts.append(f"{m}:{'✅' if len(rows) >= need else str(len(rows))}")
    if n < TOTAL:
        done_all = False
    # %5 kapısı PAYDA=470 üzerinden okunur; bitmeden "oran" yanıltır → ikisi de basılır.
    print(f"  {tag:<10} {n:>3}/{TOTAL}  kesik={trunc} (%{100*trunc/max(1,n):.2f})"
          f"  ort_tok={tok_s/max(1,tok_n):.0f}  zorla={forced}  | " + " ".join(parts))
sys.exit(0 if done_all else 1)
PY
)
    RC=$?
    { echo "[$(date '+%H:%M:%S')]"; echo "$SNAP"; } | tee -a "$LOG"

    if [ "$RC" -eq 0 ]; then
        echo "[watch] ✅ üç özne de 470/470 — üretim bitti. Sıradaki: cp0_thinking_score.sh" | tee -a "$LOG"
        break
    fi
    # Üretim süreci ölmüşse sonsuza kadar dönme (tuzak: sessizce duran koşuyu beklemek).
    if ! pgrep -f "gen_eval_grounded.py" >/dev/null; then
        echo "[watch] ⚠️ gen_eval_grounded.py süreci YOK ama özneler eksik — koşu durmuş olabilir." | tee -a "$LOG"
        echo "[watch]    kontrol: tail -30 outputs/eval/cp09_gen_local.log" | tee -a "$LOG"
        break
    fi
    sleep "$((MIN * 60))"
done
