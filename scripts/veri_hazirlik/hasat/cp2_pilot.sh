#!/usr/bin/env bash
# CP2 PİLOT — hasat boyutlandırması: iki tipin KABUL ORANI ve s/üretim'i ölçülür.
# sprint2.md CP2: "Hasat boyutu burada ölçülür ve kaydedilir." Üretim koşusuna
# girmeden önce bu iki sayı bilinmeli — tam hasat saatler sürüyor.
#
# Ön koşul: llama-server ÇIPLAK BASE ile açık (q35-4b-q4_k_m.gguf), port 8080.
# Kullanım: bash scripts/veri_hazirlik/hasat/cp2_pilot.sh [N]        (N = tip başına deneme, vars. 120)

set -uo pipefail        # -e BİLEREK yok: tuzak 5.4

N="${1:-120}"
OUT_DIR="${OUT_DIR:-outputs/eval/cp/cp2-rejected-hasat}"
mkdir -p "$OUT_DIR"

curl -sf http://127.0.0.1:8080/health >/dev/null 2>&1 || { echo "❌ llama-server yok (port 8080)"; exit 1; }

for T in m2 m2b; do
  echo "==================== PİLOT $T (n=$N) ===================="
  # -u: çıktı tamponlanmasın, huni canlı görünsün ([[training-log-buffering]])
  python -u scripts/veri_hazirlik/hasat/cp2_harvest.py --type "$T" --limit "$N" \
    --out "data/_ham_ve_ara/cp2_pilot_${T}.jsonl" || echo "⚠️ $T pilotu hata verdi"
  echo
done

echo "==================== HUNİ ÖZETİ ===================="
python -u - "$OUT_DIR" <<'PY'
import json, os, sys
rows = []
for t in ("m2", "m2b"):
    p = f"data/_ham_ve_ara/cp2_pilot_{t}_funnel.json"
    if os.path.exists(p):
        rows.append(json.load(open(p, encoding="utf-8")))
if not rows:
    sys.exit("huni dosyası yok")
print(f"{'tip':<5} {'denenen':>8} {'kabul':>6} {'oran':>7} {'s/üretim':>9} {'ort tok':>8} {'zorla':>9}")
for r in rows:
    print(f"{r['tip']:<5} {r['denenen']:>8} {r['kabul']:>6} {r['kabul_orani']:>7.3f} "
          f"{r['saniye_per_uretim']:>9.1f} {r['ort_completion_tokens']:>8.0f} {r['zorunlu_kapatma']:>9}")
# Boyutlandırma projeksiyonu: mevcut havuz 1495 abstain çifti (orpo_report.json)
print("\n--- 1.495 negatif için projeksiyon (mevcut havuz boyu) ---")
for r in rows:
    if not r["kabul_orani"]:
        print(f"{r['tip']:<5} kabul oranı 0 → projeksiyon YAPILAMAZ")
        continue
    need = 1495 / r["kabul_orani"]
    hrs = need * r["saniye_per_uretim"] / 3600
    print(f"{r['tip']:<5} gereken üretim ≈ {need:,.0f} · süre ≈ {hrs:,.1f} saat")
PY
