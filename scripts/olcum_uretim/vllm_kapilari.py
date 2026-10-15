#!/usr/bin/env python3
"""vLLM pilotunun kapıları G1-G5 (spec 2026-10-15 bölüm 5). Saf fonksiyonlar; dosya okumaz.

Ölçütler pilot sonucunu görmeden kilitlidir; değiştirmek ayrı ADR ister.
  G1 açılıyor     iki ağırlığın bütün koşularında n=80, kesik <= %5, düşünce kanalı kullanılmış
  G2 hız          koşu başına süre <= llama.cpp süresi ÷ 3
  G3 motor etkisi |kütle(Q4'ten açılmış, vLLM) − kütle(referans, llama.cpp)| <= 0,6 puan
  G4 belirlenimcilik  8 soru tek tek ↔ toplu aynı mı (bilgi; dal: bayt | puan)
  G5 Q4 etkisi    |kütle(bf16 orijinal) − kütle(Q4'ten açılmış)| (yalnız rapor)
"""
AGIRLIKLAR = ("q4-acilmis", "bf16-orijinal")
N_KALEM = 80
LLAMA_SURE_S = 640.6          # A10 referansı: outputs/eval/f0/f016-pilot/A10/m1/KUNYE.json, 1. tekrar
ESIK_HIZ_ORAN = 1 / 3
ESIK_KUTLE_PUAN = 0.6
KESIK_ESIGI = 0.05            # olcum_karti.KESIK_ESIGI ile aynı


def _gecerli(g: dict) -> bool:
    return (g["n"] == N_KALEM and g["kesik_orani"] is not None and g["kesik_orani"] <= KESIK_ESIGI
            and g["dusunen"] > 0)


def degerlendir(girdi: dict) -> dict:
    ag = {"q4_acilmis": girdi["q4_acilmis"], "bf16_orijinal": girdi["bf16_orijinal"]}
    sonuc = {"g1": {"esik": f"n={N_KALEM}, kesik<={KESIK_ESIGI}, dusunen>0",
                    "gecti": all(_gecerli(k["gecerlilik"]) for a in ag.values() for k in a["kosular"])}}
    sureler = {ad: sum(k["sure_s"] for k in a["kosular"]) / len(a["kosular"]) for ad, a in ag.items()}
    limit = LLAMA_SURE_S * ESIK_HIZ_ORAN
    sonuc["g2"] = {"ortalama_sure_s": sureler, "esik_s": limit, "gecti": all(s <= limit for s in sureler.values())}
    fark3 = round(abs(ag["q4_acilmis"]["kutle_ort"] - girdi["referans_kutle_ort"]) * 100, 6)
    sonuc["g3"] = {"fark_puan": fark3, "esik_puan": ESIK_KUTLE_PUAN, "gecti": fark3 <= ESIK_KUTLE_PUAN}
    s8 = girdi["sekiz_soru"]
    sonuc["g4"] = {"ayni": s8["ayni"], "n": s8["n"], "dal": "bayt" if s8["ayni"] == s8["n"] else "puan",
                   "gecti": True}
    sonuc["g5"] = {"fark_puan": round(abs(ag["bf16_orijinal"]["kutle_ort"] - ag["q4_acilmis"]["kutle_ort"]) * 100, 6),
                   "gecti": True}
    sonuc["ilerle"] = sonuc["g1"]["gecti"] and sonuc["g2"]["gecti"] and sonuc["g3"]["gecti"]
    return sonuc
