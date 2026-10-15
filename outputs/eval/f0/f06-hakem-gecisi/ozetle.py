"""F0.6 — hakem koşularının özeti: koşu başına özet + kütle (harness_tablo); mod başına tekrarların ortalaması,
standart sapması ve aralığı; hakem değişikliğinin etkisi. Kullanım (repo kökünden):
  python outputs/eval/f0/f06-hakem-gecisi/ozetle.py"""
import glob
import json
import os
import re
import statistics as st
import subprocess
import sys

O = "outputs/eval/f0/f06-hakem-gecisi"
D = "outputs/eval/f0/f016-pilot/A10/m1/h1_tgta_v1_A10_m1_t1_detail.jsonl"
MODLAR = ("ds-acik", "ds-kapali", "mini")

kosular = sorted(re.match(r".*/gnd_(.+)_summary\.json", y).group(1) for y in glob.glob(f"{O}/gnd_*_summary.json"))
satirlar = {}
for k in kosular:
    ozet = json.load(open(f"{O}/gnd_{k}_summary.json", encoding="utf-8"))
    tablo = f"{O}/harness_tablo_{k}.json"
    if not os.path.exists(tablo):
        subprocess.run([sys.executable, "scripts/puanlama/harness_tablo.py", "--details", D, "--gnd",
                        f"{O}/gnd_{k}.jsonl", "--kume", "data/eval/dev/core_hard.jsonl", "--out", tablo],
                       check=True, capture_output=True)
    t = json.load(open(tablo, encoding="utf-8"))["kutle_ekseni"]
    satirlar[k] = {"faithfulness_macro": ozet["faithfulness_macro"], "A1": t["A1_cevaplanan"],
                   "coverage": t["coverage"], "kutle": t["kutle_tum"], "total_claims": ozet["total_claims"],
                   "n_sifir_iddia": ozet.get("n_sifir_iddia"), "n_hakem_hata": ozet.get("n_hakem_hata"),
                   "judge_providers": ozet["judge_providers"], "judge_cost_usd": ozet["judge_cost_usd"],
                   "hakem": ozet.get("hakem")}

print(f"{'koşu':<14}{'faith_mac':>10}{'A1':>8}{'kapsama':>9}{'kütle':>8}{'iddia':>7}{'0-iddia':>8}{'hata':>6}{'$':>8}  sağlayıcı")
for k, s in satirlar.items():
    print(f"{k:<14}{s['faithfulness_macro']:>10.4f}{s['A1']:>8.4f}{s['coverage']:>9.4f}{s['kutle']:>8.4f}"
          f"{s['total_claims']:>7}{str(s['n_sifir_iddia']):>8}{str(s['n_hakem_hata']):>6}{s['judge_cost_usd']:>8.4f}  {s['judge_providers']}")

ozet_mod = {}
print()
for mod in MODLAR:
    ks = [s for k, s in satirlar.items() if k.startswith(mod + "_t")]
    if not ks:
        continue
    kut, a1 = [s["kutle"] for s in ks], [s["A1"] for s in ks]
    ozet_mod[mod] = {"n_tekrar": len(ks), "kutle_ort": st.mean(kut), "kutle_ss": st.stdev(kut) if len(ks) > 1 else None,
                     "kutle_aralik": max(kut) - min(kut), "A1_ort": st.mean(a1),
                     "A1_ss": st.stdev(a1) if len(ks) > 1 else None, "maliyet_ort": st.mean(s["judge_cost_usd"] for s in ks)}
    m = ozet_mod[mod]
    print(f"{mod:<10} n={m['n_tekrar']} · kütle ort {m['kutle_ort']:.4f} ss {(m['kutle_ss'] or 0) * 100:.2f} p "
          f"aralık {m['kutle_aralik'] * 100:.2f} p · A1 ort {m['A1_ort']:.4f} ss {(m['A1_ss'] or 0) * 100:.2f} p "
          f"· koşu başına ${m['maliyet_ort']:.4f}")
if "mini" in ozet_mod:
    for mod in ("ds-acik", "ds-kapali"):
        if mod in ozet_mod:
            print(f"hakem değişikliği {mod} − mini: kütle {(ozet_mod[mod]['kutle_ort'] - ozet_mod['mini']['kutle_ort']) * 100:+.2f} p")
json.dump({"kosular": satirlar, "modlar": ozet_mod}, open(f"{O}/OZET.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
