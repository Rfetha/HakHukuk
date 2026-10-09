#!/usr/bin/env bash
# CP7 skorlama — Gemini çıktıları, gpt-4o-mini hakem (OpenAI-direct, aile-dışlama OK).
# ⚠️ ÖNCE §3.4: red-regex'in Gemini'nin red dağarcığını yakaladığını DOĞRULA (kalibre kendi
#    base'imize göreydi; Gemini farklı kalıp kullanabilir). Yakalamıyorsa abstention sayısı YANLIŞ.
set -uo pipefail
cd /home/ersoy/code/Hukuk-SLM
source ~/code/global_venv/bin/activate

echo "════════ §3.4 — Gemini red-dağarcığı regex recall kontrolü ════════"
python - <<'PY'
import json, re, sys
sys.path.insert(0,"scripts")
from score_abstention import REJECT_RE
# Gemini'nin cevaplarının ilk cümlelerinden red adaylarını topla (M2/M2b/M3 = red beklenen modlar)
cand=[]
for m in ("m2","m2b","m3"):
    for l in open(f"outputs/eval/{m}_gem_detail.jsonl",encoding="utf-8"):
        if not l.strip(): continue
        c=(json.loads(l).get("cevap") or "").strip()
        cand.append(c)
# regex'in yakaladığı vs "red gibi görünen ama yakalanmayan"
REDLIKE=re.compile(r"bulunma|yer al|düzenle|kapsa|içer|belirtil|değinil|mevcut değ|yok\b|danış|edilemez|mümkün değ",re.I)
caught=[c for c in cand if REJECT_RE.search(c)]
redlike=[c for c in cand if REDLIKE.search(c[:120])]
missed=[c for c in redlike if not REJECT_RE.search(c)]
print(f"toplam(m2+m2b+m3)={len(cand)} · regex-RED={len(caught)} · red-gibi(ilk120)={len(redlike)} · YAKALANMAYAN={len(missed)}")
print("\n— regex'in KAÇIRDIĞI red-gibi cevaplar (elle bak, kalıp eklenmeli mi?):")
seen=set()
for c in missed:
    key=c[:60]
    if key in seen: continue
    seen.add(key); print(f"   {c[:130]}")
    if len(seen)>=15: break
if not missed: print("   (yok — regex Gemini'nin red dağarcığını da kapsıyor)")
PY

echo; echo "════════ Groundedness (m1/m4/m5) ════════"
set -a && . ./.env && set +a && export LLM_GATEWAY=openai   # HAKEM OpenAI-direct
for M in m1 m4 m5; do
  echo "── gnd $M ──"
  python scripts/puanlama/groundedness.py --details outputs/eval/${M}_gem_detail.jsonl --label ${M}_gem --mode data 2>&1 | tail -3
done
echo; echo "════════ Abstention (m2/m2b/m3) ════════"
for M in m2 m2b m3; do
  echo "── abst $M ──"
  EXTRA=""; [ "$M" = "m2b" ] && EXTRA="--source-field context_shown"
  python scripts/puanlama/score_abstention.py --details outputs/eval/${M}_gem_detail.jsonl --label ${M}_gem $EXTRA 2>&1 | tail -3
done
echo; echo "════════ A1 cevaplanan-only ════════"
python scripts/puanlama/rescore_answered.py --gnd outputs/eval/gnd_m1_gem.jsonl --bench outputs/eval/m1_gem_detail.jsonl --label m1_gem 2>&1 | grep -iE "answer|faith|cover"
python scripts/puanlama/rescore_answered.py --gnd outputs/eval/gnd_m4_gem.jsonl --bench outputs/eval/m4_gem_detail.jsonl --label m4_gem 2>&1 | grep -iE "answer|faith|cover"
echo "════ CP7 SKORLAMA TAM ════"
