#!/usr/bin/env python
"""A-register — uzman mı vatandaş-basit mi sinyali (canon eval v2, ADR-0013).

v2 hedefi = UZMAN register (V2_PLAN §3.1). Bu eksen "çıktı uzman dilinde mi, yoksa vatandaş-basit
mi" ölçer. Mevcut canon (A1/A2/A3/A4) bunu ölçmüyordu → ADR-0013 ile eklendi.

⚠️ Bu v1 = DETERMİNİSTİK LEKSİK PROXY (hakemsiz, ücretsiz). Kanonik metrik LLM-judge rubriği
olacak (ADR-0013'te metot AÇIK; Muhakim linguistic-coherence çapası + rubrik). Proxy, ucuz bir
ön-sinyal + hakem ile çapraz-kontrol için; tek başına manşet DEĞİL.

register_score ∈ [0,1]: 1=uzman, 0=vatandaş-basit, 0.5=nötr/sinyal yok.
Girdi: gen_eval_grounded çıktısı (outputs/eval/{label}_detail.jsonl) — `cevap` alanı.
Çıktı: outputs/eval/reg_{label}.jsonl + reg_{label}_summary.json
Kullanım: python scripts/puanlama/score_register.py --details outputs/eval/bench_core_v2b_detail.jsonl --label bench_core_v2b
"""
import argparse
import json
import os
import re

# ── scripts/ yol köprüsü (T5, 2026-09-07) ────────────────────────────────────
# Kardeş modüller alt klasörlere bölündükten SONRA da bulunsun diye scripts/ kökü, tüm
# alt klasörleri ve repo kökü sys.path'e girer. Uzantısız `import X` bu köprü olmadan
# taşımada SESSİZCE kırılır: ImportError çalışma zamanında, bazen GPU koşusunun ortasında.
# ⚠️ 26 dosyada BİREBİR aynı; değiştirirsen hepsinde değiştir (grep: "yol köprüsü").
import os, sys
_K = os.path.dirname(os.path.abspath(__file__))
_K = _K if os.path.basename(_K) == "scripts" else os.path.dirname(_K)
sys.path[:0] = [_K, *(os.path.join(_K, _d) for _d in sorted(os.listdir(_K))
                      if os.path.isdir(os.path.join(_K, _d)) and _d[0] not in "_."),
                os.path.dirname(_K)]
# ─────────────────────────────────────────────────────────────────────────────

import runlock  # aynı label'a paralel yazım = sessiz bozulma (bkz. runlock.py)

# Uzman/teknik-hukuk register işaretleri (resmî bağlaç, mevzuat dili, atıf, alıntı).
EXPERT_PAT = [
    r"uyarınca", r"gereğince", r"hükm(ü|ünce|leri|üne)", r"mezkûr", r"işbu", r"tabidir",
    r"düzenlen(mektedir|miştir)", r"öngör(ülmektedir|ülen)", r"hâl(inde|lerinde)",
    r"dolayısıyla", r"bu itibarla", r"ne var ki", r"ilgili madde", r"madde hükmü",
    r"##begin_quote##", r"\([^)]*,\s*Madde\s*\d", r"\b[A-ZÇĞİÖŞÜ]{2,}\s+(?:KANUN|Madde)",
]
# Vatandaş-basit register işaretleri (doğrudan hitap, sadeleştirme, tavsiye kalıbı).
CITIZEN_PAT = [
    r"yapabilirsin(iz)?", r"edebilirsin(iz)?", r"alabilirsin(iz)?", r"\bsiz(in|e)?\b",
    r"\byani\b", r"basitçe", r"kısaca", r"merak etme", r"endişelen", r"unutmayın",
    r"öneririm", r"danışman(ız|ızı)", r"şöyle ki", r"örneğin siz",
]

EXPERT_RE = [re.compile(p, re.IGNORECASE) for p in EXPERT_PAT]
CITIZEN_RE = [re.compile(p, re.IGNORECASE) for p in CITIZEN_PAT]


def hits(text, regexes):
    return sum(1 for r in regexes if r.search(text or ""))


def register_score(cevap):
    e = hits(cevap, EXPERT_RE)
    c = hits(cevap, CITIZEN_RE)
    if e + c == 0:
        return 0.5, e, c          # sinyal yok → nötr
    return e / (e + c), e, c


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--details", required=True)
    p.add_argument("--label", required=True)
    p.add_argument("--out-dir", default="outputs/eval")
    a = p.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)

    rows = [json.loads(l) for l in open(a.details, encoding="utf-8") if l.strip()]
    out_path = os.path.join(a.out_dir, f"reg_{a.label}.jsonl")
    runlock.acquire(out_path, tag=f"register {a.label}")   # 🚨 YARIŞ KAPISI
    scores = []
    with open(out_path, "w", encoding="utf-8") as f:
        for r in rows:
            s, e, c = register_score(r.get("cevap", ""))
            scores.append(s)
            f.write(json.dumps(
                {"id": r.get("id"), "register_score": s, "expert_hits": e,
                 "citizen_hits": c, "cevap": (r.get("cevap", "")[:200])},
                ensure_ascii=False) + "\n")

    n = len(scores)
    mean = sum(scores) / n if n else 0.0
    expert_frac = sum(1 for s in scores if s >= 0.6) / n if n else 0.0
    citizen_frac = sum(1 for s in scores if s <= 0.4) / n if n else 0.0
    summary = {
        "label": a.label, "n": n,
        "register_mean": round(mean, 3),
        "expert_frac(>=0.6)": round(expert_frac, 3),
        "citizen_frac(<=0.4)": round(citizen_frac, 3),
        "method": "v1-lexical-proxy (hakemsiz); kanonik=LLM-judge rubriği (ADR-0013, TODO)",
    }
    sum_path = os.path.join(a.out_dir, f"reg_{a.label}_summary.json")
    json.dump(summary, open(sum_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"[register] detay → {out_path} | özet → {sum_path}")


if __name__ == "__main__":
    main()
