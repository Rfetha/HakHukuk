#!/usr/bin/env bash
# CP0 — düşünce modu ölçümünün PUANLANMASI (ADR-0040, sprint2.md CP0).
# Girdi: cp0_thinking_gen.sh'ın ürettiği {mod}_{etiket}_detail.jsonl dosyaları.
#
# Kullanım:
#   bash scripts/puanlama/cp0_thinking_score.sh base_th
#   MODES="m1 m2" bash scripts/puanlama/cp0_thinking_score.sh base_th
#
# 🚨 Neden bu betik var (docs/record/yurutme-tuzaklari.md):
#   2.11 `.env` yüklenmez → hakem anahtarı görünmez, koşu boşa gider   → burada `set -a; source .env`
#   2.7  sağlayıcı pinlenmemiş → farklı yığın, kıyaslanamaz sayı        → LLM_GATEWAY=openai PİNLİ
#   2.3  A1 yerine ham ortalama → çekinme macro'yu çeker                → rescore_answered ZORUNLU
#   2.1  red-regex kalibrasyonu → tek kaynak score_abstention.REJECT_RE (kendi ailemiz kalibre, #39)
# Hakem CP2/CP6 ile AYNI olmalı: gpt-4o-mini · OpenAI-direct (Sprint 1 künyesi).

set -uo pipefail        # -e BİLEREK yok: tuzak 5.4

die() { echo "❌ $*" >&2; exit 1; }

TAG="${1:?kullanım: cp0_thinking_score.sh <etiket-son-eki>   (örn. base_th)}"
OUT_DIR="${OUT_DIR:-outputs/eval/cp/cp09-butceli-1024-512}"   # koşu klasörü (2026-07-29)
MODES="${MODES:-m1 m4 m2 m2b m3 m5}"

# --- hakem erişimi: .env kabuğa YÜKLENİR (tuzak 2.11) ------------------------
if [ -f .env ]; then set -a; . ./.env; set +a; else die ".env yok — hakem anahtarı yüklenemez"; fi
[ -n "${OPENAI_API_KEY:-}" ] || die "OPENAI_API_KEY boş (.env yüklendi ama anahtar yok)"
# Why openrouter: 2026-08-05'ten itibaren TEK geçit OpenRouter (insan kararı, bakiye orada).
# Sağlayıcı yine pinli — geçit değişse de yığın aynı kalmalı (tuzak 2.7).
export LLM_GATEWAY="${LLM_GATEWAY:-openrouter}"
export GND_JUDGE="${GND_JUDGE:-openai/gpt-4o-mini}"          # CP2/CP6 ile aynı hakem
export LLM_PROVIDER_ORDER="${LLM_PROVIDER_ORDER:-OpenAI}"    # tuzak 2.7: sağlayıcı PİNLİ
echo "### hakem: $GND_JUDGE · gateway=$LLM_GATEWAY · sağlayıcı=$LLM_PROVIDER_ORDER · etiket=*_$TAG · modlar=$MODES"
echo

for M in $MODES; do
  D="$OUT_DIR/${M}_${TAG}_detail.jsonl"
  [ -f "$D" ] || die "detay yok: $D (önce cp0_thinking_gen.sh)"
done

for M in $MODES; do
  D="$OUT_DIR/${M}_${TAG}_detail.jsonl"
  L="${M}_${TAG}"
  echo "==================== $L ===================="
  case "$M" in
    m1|m4|m5|h1)   # groundedness hakemi (M5 = ANTİ-HEDEF, yükselmemeli; h1 = harness AÇIK M1)
      python scripts/puanlama/groundedness.py --details "$D" --label "$L" --mode data --out-dir "$OUT_DIR" \
        || die "$L groundedness başarısız"
      # A1 = cevaplanan-only (tuzak 2.3) — coverage ile birlikte okunur
      python scripts/puanlama/rescore_answered.py --gnd "$OUT_DIR/gnd_${L}.jsonl" --bench "$D" --label "$L" \
        | tee "$OUT_DIR/a1_${L}.txt" || die "$L rescore başarısız"
      ;;
    m2|m3)      # abstention hakemi — kaynak GÖSTERİLDİ (referans alanı)
      python scripts/puanlama/score_abstention.py --details "$D" --label "$L" --out-dir "$OUT_DIR" \
        || die "$L abstention başarısız"
      ;;
    m2b|h2b)    # gold GÖSTERİLMEDİ → payda `context_shown` üzerinden
      python scripts/puanlama/score_abstention.py --details "$D" --label "$L" --out-dir "$OUT_DIR" \
        --source-field context_shown || die "$L abstention başarısız"
      ;;
    # ⚠️ Tanınmayan mod SESSİZCE geçmez. `h1` tam bunu yaşadı: dalı yoktu, betik yalnız
    # score_register koştu, hakemi HİÇ çağırmadı ve yine de 0 ile çıktı (tuzak sınıfı: sessiz yanlışlık).
    *) die "tanınmayan mod: $M — puanlayıcı dalı yok, sessizce geçilmez" ;;
  esac
  python scripts/puanlama/score_register.py --details "$D" --label "$L" --out-dir "$OUT_DIR" \
    || die "$L register başarısız"
  echo
done

# --- ÖN-KAYITLI KARAR KURALI (ADR-0040) -------------------------------------
# ⚠️ Kuralın referansı BASE'in thinking-off sayılarıdır → hüküm yalnız BASE öznesi için okunur.
# Başka bir özne (τ_g, rakip) için basılan bir "🟢 YEŞİL" satırı o öznenin bulgusu sanılır —
# bu hattın hata sınıfı tam olarak bu (sessiz yanlışlık). Bu yüzden hüküm TAG'e bağlı.
BASE_TAG="${BASE_TAG:-base_th}"
echo "==================== ADR-0040 KARAR KURALI ===================="
python - "$OUT_DIR" "$TAG" "$BASE_TAG" <<'PY'
import json, os, sys
out_dir, tag, base_tag = sys.argv[1], sys.argv[2], sys.argv[3]

def j(p):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None

def a1(mod):
    p = f"{out_dir}/a1_{mod}_{tag}.txt"
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None

# Referans: base --thinking off (DEV, #39/#41 · sprint1-sonuc-tablosu.md)
REF = {"m2_rej": 0.6330, "m1_kutle": 42.6, "m5_kutle": 10.7, "tok": 249}

m1, m5 = a1("m1"), a1("m5")
m2 = j(f"{out_dir}/abst_m2_{tag}_summary.json")

def kutle(d):
    if not d or not d.get("A1_faithfulness_macro_answered"):
        return None
    return 100.0 * d["n_answered"] / d["n_total"] * d["A1_faithfulness_macro_answered"]

k1, k5 = kutle(m1), kutle(m5)
rej = None
if m2:
    for key in ("rejection_rate", "llm_rejection_rate", "rej_llm", "rejection_rate_llm"):
        if key in m2:
            rej = m2[key]; break
    if rej is None:
        print("⚠️ abst_m2 özetinde LLM-red alanı bulunamadı — anahtarlar:", sorted(m2))

print(f"M2 Rej (LLM)        : {rej}            ref {REF['m2_rej']}   eşik ≥ 0.78")
print(f"M1 sadık-cevap kütle: {k1 and round(k1,1)}%   ref %{REF['m1_kutle']}  eşik ≥ %57.6")
print(f"M5 ezber kütlesi    : {k5 and round(k5,1)}%   ref %{REF['m5_kutle']}  MUHAFIZ ≤ %10.7")
if m1: print(f"  (M1 coverage {m1['n_answered']}/{m1['n_total']} · A1 {m1['A1_faithfulness_macro_answered']})")
if m5: print(f"  (M5 coverage {m5['n_answered']}/{m5['n_total']} · A1 {m5['A1_faithfulness_macro_answered']})")

if rej is None or k1 is None or k5 is None:
    sys.exit("\n⚠️ Karar için gereken üç sayının hepsi yok — eksik modu koş, sonra tekrar.")

if tag != base_tag:
    sys.exit(f"\nℹ️ Yukarıdaki üç sayı `{tag}` öznesinin — ADR-0040 HÜKMÜ BASILMADI.\n"
             f"   Kuralın referansı base'in thinking-off sayıları; hüküm yalnız `{base_tag}` için\n"
             f"   okunur. Bu öznenin kıyası: compare_runs.py ile base_th'ye karşı.")

kazanc_m2 = 100 * (rej - REF["m2_rej"])          # puan
kazanc_m1 = k1 - REF["m1_kutle"]                 # puan
esik = rej >= 0.78 or k1 >= 57.6
muhafiz = k5 <= REF["m5_kutle"]
print(f"\nkazanç: M2 {kazanc_m2:+.1f} puan · M1 kütle {kazanc_m1:+.1f} puan · M5 muhafız "
      f"{'✅ geçti' if muhafiz else '❌ İHLAL'}")

if esik and muhafiz:
    verdict = ("🟢 YEŞİL — RS-FT Sprint 2 kapsamına alınır. ADR-0030 m.2 geri alınır, "
               "ADR-0035 yeniden açılır, üç özne thinking-açık protokolde yeniden koşulur.")
elif kazanc_m2 <= 5.0 and kazanc_m1 <= 5.0:
    verdict = ("🔴 KIRMIZI — ADR-0030 m.2 kanıtla teyit. Limitations'taki itiraf BULGUYA döner. "
               "RS-FT future-work.")
else:
    verdict = ("🟡 SARI — plan değişmez; thinking rapor edilen bir eksen olur. "
               "RS-FT Kapı 6 merdiveninin 4. basamağında bekler."
               + ("" if muhafiz else "  (sebep: M5 muhafızı İHLAL)"))
print("\n" + verdict)
print("\n→ research_log #42'ye yaz: künye (thinking=on, MAXTOK, ctx, kesik oranı, ort token) + "
      "bu üç sayı + karar.")
PY
