"""#74 — hakem koşularının özeti: koşu başına kütle (harness_tablo) ve fatura; DeepSeek'in F0.6 kapalı
mod bandı (ort ± 2 ss) kontrolü; GLM'in 5 tekrarının ortalaması, standart sapması (eşik ≤ 0,9 p) ve
aralığı; R3: ikinci kolun doğrulama çağrısında önbellekten okunan girdi.
Kullanım (repo kökünden): python outputs/eval/f0/k74-fatura-glm/ozetle.py"""
import glob
import json
import os
import re
import statistics as st
import subprocess
import sys

O = "outputs/eval/f0/k74-fatura-glm"
D = "outputs/eval/f0/f016-pilot/A10/m1/h1_tgta_v1_A10_m1_t1_detail.jsonl"
F06 = json.load(open("outputs/eval/f0/f06-hakem-gecisi/OZET.json", encoding="utf-8"))["modlar"]["ds-kapali"]
BANT = (F06["kutle_ort"] - 2 * F06["kutle_ss"], F06["kutle_ort"] + 2 * F06["kutle_ss"])


def kutle(k):
    tablo = f"{O}/harness_tablo_{k}.json"
    if not os.path.exists(tablo):
        subprocess.run([sys.executable, "scripts/puanlama/tablo/harness_tablo.py", "--details", D, "--gnd",
                        f"{O}/gnd_{k}.jsonl", "--kume", "data/eval/dev/core_hard.jsonl", "--out", tablo],
                       check=True, capture_output=True)
    return json.load(open(tablo, encoding="utf-8"))["kutle_ekseni"]


kosular = sorted(re.match(r".*/gnd_(.+)_summary\.json", y).group(1) for y in glob.glob(f"{O}/gnd_*_summary.json"))
satirlar = {}
for k in kosular:
    oz = json.load(open(f"{O}/gnd_{k}_summary.json", encoding="utf-8"))
    s = {"n": oz["n"], "n_hakem_hata": oz["n_hakem_hata"], "n_sifir_iddia": oz["n_sifir_iddia"],
         "total_claims": oz["total_claims"], "judge_providers": oz["judge_providers"],
         "judge_cost_usd": oz["judge_cost_usd"], "fatura": oz["fatura"], "hakem": oz["hakem"]}
    if not (k == "ds-kapali_r3" or k.endswith("_duman")):   # Why: r3 iki kol karışık, duman 3 kalem
        t = kutle(k)
        s |= {"kutle": t["kutle_tum"], "A1": t["A1_cevaplanan"], "coverage": t["coverage"]}
    satirlar[k] = s
    f = s["fatura"]["toplam"]
    print(f"{k:<18} kütle {s.get('kutle', float('nan')):.4f} · hata {s['n_hakem_hata']} · 0-iddia "
          f"{s['n_sifir_iddia']} · liste ${f['liste_maliyet_usd']:.4f} · gerçek ${f['gercek_maliyet_usd'] or 0:.4f} "
          f"· oran {f['fatura_orani']} · önbellek {f['onbellek_isabeti']} · düşünce {f['dusunce_token']} "
          f"· eksik {f['eksik']} · {s['judge_providers']}")

sonuc = {"kosular": satirlar, "f06_ds_kapali_bant": BANT}
if "ds-kapali_r1" in satirlar:
    k = satirlar["ds-kapali_r1"]["kutle"]
    sonuc["ds_bant_icinde"] = BANT[0] <= k <= BANT[1]
    print(f"\nDeepSeek r1 kütle {k:.4f} · F0.6 bandı {BANT[0]:.4f}-{BANT[1]:.4f} → "
          f"{'İÇİNDE' if sonuc['ds_bant_icinde'] else 'DIŞINDA — DUR'}")

glm = [s for k, s in satirlar.items() if re.fullmatch(r"glm-dusuk_t\d", k)]
if len(glm) > 1:
    kut = [s["kutle"] for s in glm]
    sonuc["glm"] = {"n_tekrar": len(glm), "kutle_ort": st.mean(kut), "kutle_ss": st.stdev(kut),
                    "kutle_aralik": max(kut) - min(kut), "esik_ss": 0.009,
                    "esik_gecti": st.stdev(kut) <= 0.009,
                    "ds_kapali_farki_p": (st.mean(kut) - F06["kutle_ort"]) * 100}
    g = sonuc["glm"]
    print(f"GLM n={g['n_tekrar']} · kütle ort {g['kutle_ort']:.4f} · ss {g['kutle_ss'] * 100:.2f} p "
          f"(eşik 0,90) → {'GEÇTİ' if g['esik_gecti'] else 'KALDI'} · aralık {g['kutle_aralik'] * 100:.2f} p "
          f"· DeepSeek kapalıdan fark {g['ds_kapali_farki_p']:+.2f} p")


def dogrulama_onbellegi(gnd, onek):
    """Seçilen kalemlerin doğrulama çağrılarında önbellekten okunan girdi payı."""
    girdi = onb = n = 0
    for r in (json.loads(x) for x in open(gnd, encoding="utf-8") if x.strip()):
        if not str(r["id"]).startswith(onek):
            continue
        for c in r.get("kullanim", []):
            if c["asama"] == "dogrulama" and c["onbellekli_girdi"] is not None:
                girdi, onb, n = girdi + c["girdi"], onb + c["onbellekli_girdi"], n + 1
    return {"n_cagri": n, "girdi": girdi, "onbellekli": onb, "pay": round(onb / girdi, 4) if girdi else None}


if os.path.exists(f"{O}/gnd_ds-kapali_r3.jsonl"):
    sonuc["r3"] = {"birinci_kol": dogrulama_onbellegi(f"{O}/gnd_ds-kapali_r3.jsonl", "a-"),
                   "ikinci_kol": dogrulama_onbellegi(f"{O}/gnd_ds-kapali_r3.jsonl", "v-"),
                   "bugunku_sira_r1": dogrulama_onbellegi(f"{O}/gnd_ds-kapali_r1.jsonl", "")}
    print("R3 doğrulama çağrısı önbellek payı:", json.dumps(sonuc["r3"], ensure_ascii=False))

json.dump(sonuc, open(f"{O}/OZET.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
