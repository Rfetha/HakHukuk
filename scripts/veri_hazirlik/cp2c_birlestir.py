#!/usr/bin/env python3
"""CP2-c hasat dizinlerini kabul zincirine TEK temiz girdi hâline getirir.

Niçin var: CP2-c hasadı iki dizine dağıldı ve biri kirli bitti.

  /cp2c      16:19 denemesi, `-np 32`, verim kapısında durdu → 113 aday
  /cp2c-64   16:47 üretim koşusu, `-np 64`
             ⚠️ 16:52-17:05 arası AYNI dosyaya yazan ikinci bir iş vardı (#48 §5):
                → YİNELENEN id'ler   → tekilleştirilmezse ORPO aynı çifti iki kez görür
                → yazarken kesilmiş son satır → yarım JSON

İkisi de sessiz yanlışlık sınıfı: kabul zinciri yinelenen id'yle çökmez, yalnız yanlış
sayı üretir. Bu yüzden onarım kabul zincirinden ÖNCE, ayrı ve kayıtlı bir adım.

Taşıyıcı kimliği (ADR-0047 m.2) `-np`'yi ve kartı serbest bırakır, dolayısıyla iki koşunun
karışması geçerlidir — ama karışım **açıkça künyeye yazılır**: her kayda `kaynak`, dizine
`BIRLESIM.json`.

Kullanım (öncelik = komut satırı sırası; çakışan id'de İLK dizin kazanır):
  python scripts/veri_hazirlik/cp2c_birlestir.py --out data/_ham_ve_ara/cp2c_birlesik \
      outputs/_indirilen/cp2c-64 outputs/_indirilen/cp2c
"""
import argparse
import json
import os


def oku(path):
    """jsonl → (kayıtlar, atılan_yarim_satir_sayisi).

    Son satır yarım JSON ise atılır (bilinen sebep: süreç yazarken durduruldu).
    ORTADAKİ bozuk satır ATILMAZ — o bilinmeyen bir bozulmadır, çökerek bildirir.
    """
    with open(path, encoding="utf-8") as f:
        satirlar = [l for l in f if l.strip()]
    kayitlar, atilan = [], 0
    for i, l in enumerate(satirlar):
        try:
            kayitlar.append(json.loads(l))
        except json.JSONDecodeError:
            if i == len(satirlar) - 1:
                atilan = 1
                print(f"  ⚠️  {os.path.basename(path)}: yarım son satır atıldı "
                      f"({len(l)} karakter)")
            else:
                raise SystemExit(
                    f"❌ {path} satır {i+1}: bozuk JSON — son satır DEĞİL. "
                    f"Bu bilinen kesilme kalıbı değil, dosya incelenmeli.")
    return kayitlar, atilan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dizinler", nargs="+", help="hasat dizinleri; çakışmada İLK kazanır")
    ap.add_argument("--out", required=True)
    ap.add_argument("--types", nargs="+", default=["m2", "m2b"])
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    kunye = {"dizinler_oncelik_sirasi": a.dizinler, "tipler": {}}

    for tip in a.types:
        gorulen, birlesik = set(), []
        pay = {}          # dizin → kabul edilen kayıt sayısı (karışım oranı)
        atilan_toplam = yinelenen_toplam = 0

        for d in a.dizinler:
            p = os.path.join(d, f"cp2c_{tip}.jsonl")
            if not os.path.exists(p):
                print(f"  – {p} yok, atlanıyor")
                continue
            kayitlar, atilan = oku(p)
            atilan_toplam += atilan
            ad = os.path.basename(os.path.normpath(d))
            n_yeni = 0
            for r in kayitlar:
                if r["id"] in gorulen:
                    yinelenen_toplam += 1
                    continue
                gorulen.add(r["id"])
                r["kaynak"] = ad           # kayıt düzeyinde köken — denetlenebilirlik
                birlesik.append(r)
                n_yeni += 1
            pay[ad] = n_yeni
            print(f"  {ad}/{tip}: {len(kayitlar)} okundu → {n_yeni} yeni")

        if not birlesik:
            print(f"  ⚠️  {tip}: hiç kayıt yok, dosya yazılmadı")
            continue

        hedef = os.path.join(a.out, f"cp2c_{tip}.jsonl")
        with open(hedef, "w", encoding="utf-8") as f:
            for r in birlesik:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        kunye["tipler"][tip] = {"tekil_kayit": len(birlesik), "karisim": pay,
                                "yinelenen_atilan": yinelenen_toplam,
                                "yarim_satir_atilan": atilan_toplam}
        print(f"[birleşim] {tip}: **{len(birlesik)}** tekil · yinelenen atılan "
              f"{yinelenen_toplam} · yarım satır {atilan_toplam} → {hedef}")

    kunye["toplam_tekil"] = sum(v["tekil_kayit"] for v in kunye["tipler"].values())
    kp = os.path.join(a.out, "BIRLESIM.json")
    json.dump(kunye, open(kp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\n[birleşim] TOPLAM TEKİL: {kunye['toplam_tekil']} → {kp}")
    print(f"Sıradaki: bash scripts/veri_hazirlik/cp2c_kabul.sh {a.out}")


if __name__ == "__main__":
    main()
