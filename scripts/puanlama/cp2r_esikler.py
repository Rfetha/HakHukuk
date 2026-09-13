#!/usr/bin/env python3
"""CP2-r — ARA KAPI eşiklerini düzeltilmiş cevaba-kör çıpadan TÜRET (ADR-0049 m.1).

Ön-kayıtlı olan **FORMÜL**, sayı değil:

    M2 eşiği       = base M2  + 0.12          (ADR-0045 m.1 · "base + 12 puan")
    M2b onarım     = base M2b × 0.90          (ADR-0045 m.2 · muhafız çarpanıyla aynı)
    M1 A1 muhafızı = base M1 A1 × 0.90        ← valid_trap'ten ETKİLENMEZ (groundedness)

Emsal: eşikler thinking-off → bütçeli geçişinde bir kez zaten taşındı (0.75/0.876 → 0.934/0.888).

⚠️ Yön bizim lehimize ve rapora öyle geçiyor. Savunma (ADR-0049 m.1): (a) `τ_a` **henüz yok**,
sonucu bilmeden düzeltiliyor; (b) düzeltme base'e, rakibe ve her hücreye **aynı** uygulanıyor;
(c) bozuk ölçümden türeyen eşiği korumak ön-kayıtlılığı değil **hatayı** korumaktır.
**Eski eşiğe karşı sonuç da raporlanır.**

Ayrıca ADR-0049 m.3'ün ön-kayıtlı tabanını okur: m2b cevaba-kör geçerli tuzak **< 40/80** ise
merge onarım kontrolü **tanımlayıcıya** iner ve ARA KAPI'nın 2. gözlemi olmaktan çıkar.

⚠️ 2026-08-06 (K-3): girdi artık `score_abstention.py`'nin **gerçek** `abst_*_summary.json`
çıktısı. Önceki girdi `_KOR.json` yan dosyalarıydı; onları üreten betik **SİLİNDİ** (repoda
yok, adı yalnız `docs/record/kronoloji-53-62.md#58` §K-3'te ve
tuzak 2.18'de geçer) — çekinme oranlarını ikinci bir yerde bölüyordu ve `reject_exact`i
satırda SAKLANMIŞ (bayat dedektör sürümüne ait) alandan okuyordu (tuzak 2.9).
"ESKİ" sütunu, varsa `.ONCEKI-*` yedeğinden okunur; yoksa `—` basılır.

Kullanım:
  python scripts/puanlama/cp2r_esikler.py --kosu-dir outputs/eval/cp09-butceli-1024-512 \
      --a1-summary outputs/eval/cp1-hakem-meta-iddia/gnd_m1_base_th_summary.json
"""
import argparse
import glob
import json
import os

BASE_TAG = "base_th"
M2_ARTIS = 0.12          # ADR-0045 m.1, ön-kayıtlı
MUHAFIZ_CARPAN = 0.90    # ADR-0045 m.2 / muhafız, ön-kayıtlı
M2B_TABAN = 40           # ADR-0049 m.3, ön-kayıtlı (80 kalemin yarısı)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--kosu-dir", required=True,
                   help="base kolunun skorlandığı koşu klasörü (abst_{mod}_{tag}_summary.json)")
    p.add_argument("--merge-m2b-summary", default="",
                   help="merge kolunun m2b/h2b özeti — verilirse ARA KAPI 2. gözlemi HÜKME "
                        "BAĞLANIR (geçti/düştü). ⛔ ADR-0050: eşiğe/çarpana dokunulmaz, "
                        "yalnız yeniden türetilir ve çıkan hüküm olduğu gibi yazılır.")
    p.add_argument("--a1-summary", default="",
                   help="base M1 A1 dosyası (muhafız için) — `a1_m1_base_th.txt`, alan "
                        "`A1_faithfulness_macro_answered`. Boşsa muhafız ESKİ değerle raporlanır.")
    p.add_argument("--eski-m2-esik", type=float, default=0.934)
    p.add_argument("--eski-m2b-esik", type=float, default=0.887)
    p.add_argument("--out", default="")
    return p.parse_args()


def oku(kosu_dir, mode, tag=BASE_TAG):
    """Bugünkü özet + (varsa) yayımlanmış ESKİ değeri `.ONCEKI-*` yedeğinden."""
    p = f"{kosu_dir}/abst_{mode}_{tag}_summary.json"
    if not os.path.exists(p):
        raise SystemExit(f"YOK: {p} — önce score_abstention.py koşulmalı")
    s = json.load(open(p, encoding="utf-8"))
    yedekler = sorted(glob.glob(p + ".ONCEKI-*"))
    eski = json.load(open(yedekler[0], encoding="utf-8")) if yedekler else {}
    alanlar = ("rejection_rate", "fabrication_rate", "rejection_exact",
               "parametric_leak", "valid_traps", "invalid_traps", "n")
    return {"YENI": {k: s.get(k) for k in alanlar},
            "ESKI_ozneye_bagli_payda": {k: eski.get(k) for k in alanlar},
            "eski_kaynak": yedekler[0] if yedekler else None,
            "valid_trap_kaynagi": s.get("valid_trap_kaynagi")}


def main():
    a = parse_args()
    m2, m2b, m3 = oku(a.kosu_dir, "m2"), oku(a.kosu_dir, "m2b"), oku(a.kosu_dir, "m3")

    b_m2, b_m2b = m2["YENI"]["rejection_rate"], m2b["YENI"]["rejection_rate"]
    e_m2, e_m2b = m2["ESKI_ozneye_bagli_payda"]["rejection_rate"], \
        m2b["ESKI_ozneye_bagli_payda"]["rejection_rate"]

    yeni_m2_esik = round(b_m2 + M2_ARTIS, 4)
    yeni_m2b_esik = round(b_m2b * MUHAFIZ_CARPAN, 4)

    v = m2b["YENI"]["valid_traps"]
    m2b_ayakta = v >= M2B_TABAN

    print("=" * 72)
    print("ARA KAPI EŞİKLERİ — düzeltilmiş cevaba-kör çıpadan türetildi (ADR-0049 m.1)")
    print("=" * 72)
    def g(x):
        return "—" if x is None else str(x)

    print(f"\n{'çıpa':22} {'ESKİ (yayımlanmış)':>20} {'YENİ (bugünkü alet)':>20}")
    print("-" * 66)
    print(f"{'base M2 Rej':22} {g(e_m2):>20} {g(b_m2):>20}")
    print(f"{'base M2b Rej':22} {g(e_m2b):>20} {g(b_m2b):>20}")
    print(f"{'base M3 Rej':22} {g(m3['ESKI_ozneye_bagli_payda']['rejection_rate']):>20} "
          f"{g(m3['YENI']['rejection_rate']):>20}")
    print(f"\n{'payda (geçerli tuzak)':22} {'ESKİ':>20} {'YENİ':>20}")
    print("-" * 66)
    for ad, d in (("m2", m2), ("m2b", m2b), ("m3", m3)):
        print(f"{ad:22} {g(d['ESKI_ozneye_bagli_payda']['valid_traps'])+'/'+g(d['YENI']['n']):>20} "
              f"{g(d['YENI']['valid_traps'])+'/'+g(d['YENI']['n']):>20}   "
              f"{(d['valid_trap_kaynagi'] or '')[:40]}")

    print(f"\n{'EŞİK':30} {'ESKİ':>12} {'YENİ':>12}   formül")
    print("-" * 76)
    print(f"{'1) τ_a tekil M2 Rej ≥':30} {a.eski_m2_esik:>12} {yeni_m2_esik:>12}   base + 0.12")
    print(f"{'2) merge M2b ≥':30} {a.eski_m2b_esik:>12} {yeni_m2b_esik:>12}   base × 0.90")

    a1_yeni = None
    if a.a1_summary and os.path.exists(a.a1_summary):
        s = json.load(open(a.a1_summary, encoding="utf-8"))
        a1 = s.get("A1_faithfulness_macro_answered")
        if a1:
            a1_yeni = round(a1 * MUHAFIZ_CARPAN, 4)
            print(f"{'   muhafız M1 A1 ≥':30} {0.888:>12} {a1_yeni:>12}   base A1 × 0.90 "
                  f"(A1={a1}; valid_trap'ten ETKİLENMEZ)")
    if a1_yeni is None:
        print(f"{'   muhafız M1 A1 ≥':30} {0.888:>12} {'—':>12}   ⏳ base A1 özeti verilmedi")

    print(f"\n{'M2b KURGU TABANI (ADR-0049 m.3)':30}")
    print("-" * 76)
    durum = "✅ AYAKTA — merge onarımı ARA KAPI'nın 2. gözlemi olarak kalır" if m2b_ayakta \
        else "🔴 KIRILDI — merge onarımı TANIMLAYICIYA iner, 2. gözlem olmaktan çıkar"
    print(f"  m2b cevaba-kör geçerli tuzak = {v}/{m2b['YENI']['n']}  ·  taban {M2B_TABAN}/80")
    print(f"  → {durum}")

    print("\n⚠️ Eşik hareketinin yönü ve savunması ADR-0049 m.1'de; sonuç ESKİ eşiğe karşı da "
          "raporlanır.")

    # ── ARA KAPI 2. GÖZLEM — hüküm (ADR-0045 m.2) ────────────────────────────
    # ⛔ ADR-0050: eşiğe, çarpana, formüle DOKUNULMAZ. Yalnız yeniden türetilir ve
    # çıkan hüküm OLDUĞU GİBİ yazılır. Bu kapı CP4-CP5 harcamasını yetkilendiren kapıydı.
    hukum = None
    if a.merge_m2b_summary:
        ms = json.load(open(a.merge_m2b_summary, encoding="utf-8"))
        merge = ms["rejection_rate"]
        gecti = merge >= yeni_m2b_esik
        hukum = {
            "kol": ms.get("label"), "kaynak": a.merge_m2b_summary,
            "merge_m2b": merge, "esik": yeni_m2b_esik,
            "formul": f"base M2b {b_m2b} × {MUHAFIZ_CARPAN}",
            "gecti": gecti, "fark_puan": round((merge - yeni_m2b_esik) * 100, 1),
            "eski_esige_karsi": {"esik": a.eski_m2b_esik,
                                 "gecti": merge >= a.eski_m2b_esik},
            "payda_esit": ms.get("valid_traps") == m2b["YENI"]["valid_traps"],
        }
        print(f"\n{'ARA KAPI 2. GÖZLEM — merge onarımı':30}")
        print("-" * 76)
        print(f"  eşik      = {MUHAFIZ_CARPAN} × base M2b {b_m2b} = {yeni_m2b_esik}")
        print(f"  merge     = {merge}  ({ms.get('label')}, payda {ms.get('valid_traps')})")
        print(f"  → {'✅ GEÇTİ' if gecti else '🔴 DÜŞTÜ'}  ({hukum['fark_puan']:+.1f} puan)")
        print(f"  eski eşiğe ({a.eski_m2b_esik}) karşı: "
              f"{'✅ GEÇTİ' if hukum['eski_esige_karsi']['gecti'] else '🔴 DÜŞTÜ'}")
        if not hukum["payda_esit"]:
            print(f"  ⚠️ PAYDA EŞİT DEĞİL: base {m2b['YENI']['valid_traps']} ↔ "
                  f"merge {ms.get('valid_traps')} — aynı sınav değil, kıyas şerhli okunur")

    out = {
        "olcum": "ARA KAPI eşikleri — düzeltilmiş cevaba-kör çıpadan türetildi",
        "karar_belgesi": "ADR-0049 m.1 (formül ön-kayıtlı, sayı değil) · ADR-0045",
        "cipalar": {
            "base_m2":  {"eski": e_m2,  "yeni": b_m2},
            "base_m2b": {"eski": e_m2b, "yeni": b_m2b},
            "base_m3":  {"eski": m3["ESKI_ozneye_bagli_payda"]["rejection_rate"],
                         "yeni": m3["YENI"]["rejection_rate"]},
        },
        "paydalar": {ad: {"eski": d["ESKI_ozneye_bagli_payda"]["valid_traps"],
                          "yeni": d["YENI"]["valid_traps"], "n": d["YENI"]["n"]}
                     for ad, d in (("m2", m2), ("m2b", m2b), ("m3", m3))},
        "esikler": {
            "m2_tekil":     {"eski": a.eski_m2_esik,  "yeni": yeni_m2_esik,  "formul": "base + 0.12"},
            "m2b_merge":    {"eski": a.eski_m2b_esik, "yeni": yeni_m2b_esik, "formul": "base × 0.90"},
            "m1_a1_muhafiz": {"eski": 0.888, "yeni": a1_yeni,
                              "formul": "base A1 × 0.90", "not": "valid_trap'ten ETKİLENMEZ"},
        },
        "m2b_kurgu_tabani": {"taban": M2B_TABAN, "olculen": v, "n": m2b["YENI"]["n"],
                             "ayakta": m2b_ayakta,
                             "kural": "ADR-0049 m.3 — altında merge onarımı tanımlayıcıya iner"},
        "ara_kapi_2_gozlem": hukum,
        # 🚨 Hangi çıpanın paydası BUGÜNKÜ aletle üretildi, hangisi değil — eşiği okuyanın
        # bunu görmeden hüküm kurmaması için (tuzak 2.6/2.14).
        "payda_onarildi_mi": {ad: d["valid_trap_kaynagi"] or "🔴 HAYIR — eski, modele bağımlı payda"
                              for ad, d in (("m2", m2), ("m2b", m2b), ("m3", m3))},
        "serh": "Eşik hareketi τ_a LEHİNE. Savunma: (a) τ_a henüz yok; (b) düzeltme her özneye aynı; "
                "(c) bozuk ölçümden türeyen eşiği korumak hatayı korumaktır. Eski eşiğe karşı da raporlanır.",
    }
    if a.out:
        json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"\n→ {a.out}")


if __name__ == "__main__":
    main()
