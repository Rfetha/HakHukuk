#!/usr/bin/env python3
"""Korpusa yürürlük alanı ekler ve alt-madde kimliğini onarır (sprint3 S2 · borç B7).

İki dönüşüm, ikisi de `data/corpus/mevzuat_maddeler.jsonl` üzerinde:

  1. `mulga` + ilga eden kanun/madde/tarih  — madde BAŞINDA "(Mülga: ...)" varsa
  2. alt-madde soneki `madde_no`'ya taşınır — metni "/a – ..." diye başlayan satır
     aslında "Madde 31" değil "Madde 31/a"dır (research_log #52 §7)

⚠️ Tablo/cetvel parçası satırları (sınıf A) KASTEN elenmiyor — ölçüldü, modele hiç
ulaşmıyorlar; elemek yalnız indeksi değiştirip ölçülmüş sayıları harcardı (borç B9).

Yazma atomik: geçici dosyaya yazılır, doğrulama geçerse `os.replace` ile yerine konur.
Doğrulama düşerse korpus DEĞİŞMEZ ve betik hata ile çıkar.

Kullanım:
    python scripts/erisim_korpus/korpus_yururluk.py --korpus data/corpus/mevzuat_maddeler.jsonl
    python scripts/erisim_korpus/korpus_yururluk.py --korpus ... --kuru   # yazmaz, yalnız rapor
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

# Madde işaretleyici öneki (»110- «, »– «) atlanır, ardından "(Mülga" gelmeli.
# Why: 1475/15 metni "110- (Mülga: ...)" diye başlar; salt "^\(" çıpası onu kaçırır.
MULGA_BAS = re.compile(r"^[\s\d\-–—.,:;/()]*\(\s*Mülga", re.I)
# "(Mülga birinci fıkra: ...)" — madde bütünüyle değil, FIKRA düzeyinde ilga.
MULGA_FIKRA = re.compile(r"\(\s*Mülga\s+[^):]*?fıkra", re.I)
ONEK = " 0123456789-–—.,:;/"

MULGA_ICI = re.compile(r"\(\s*Mülga[^:)]*:\s*([^)]*?)\s*\)", re.I)
# "22/5/2003/4857/120 md." · "2/7/2018 – KHK-703/49 md." · "16/5/2012-6306/22 md."
# Why: tarih ile kanun arasındaki ayraç TİRE de olabilir BÖLÜ de. Ayraç yalnız tire
# sanılınca "22/5/2003/4857/120" içinden "2003/4857" okunuyordu — yani TARİHİN SON
# PARÇASI kanun numarası oluyordu (1475/15'in ilga kaynağı 4857 değil "2003" çıktı).
KAYNAK = re.compile(
    r"(?:(\d{1,2}/\d{1,2}/\d{4})\s*[-–—/]?\s*)?(KHK\s*[-–—]?\s*\d+|\d{3,5})\s*/\s*(\d+)"
)

# Metin "/a – ", "/A- ", "/İ - " gibi bir alt-madde sonekiyle başlıyorsa kimlik eksik demektir.
# Why: BÜYÜK harf şart — korpusta en sık sonek "/A" (249 satır). Yalnız küçük harf aranınca
# sınıfın %80'i (387/485) sessizce kaçıyordu (research_log #52 §7).
SONEK = re.compile(r"^\s*/\s*([A-Za-zÇĞİIÖŞÜçğıöşü])\s*[–—\-)]?\s*")


def yururluk(text: str) -> dict:
    """Madde metninden yürürlük alanlarını çıkarır. Mülga değilse yalnız {'mulga': False}."""
    if not MULGA_BAS.match(text) or MULGA_FIKRA.match(text.lstrip(ONEK)):
        return {"mulga": False}
    alan = {"mulga": True, "ilga_eden_kanun": None, "ilga_eden_madde": None, "ilga_tarihi": None}
    ic = MULGA_ICI.search(text)
    if ic and (k := KAYNAK.search(ic.group(1))):
        alan["ilga_tarihi"] = k.group(1)
        alan["ilga_eden_kanun"] = re.sub(r"\s*[-–—]\s*", "-", k.group(2)).upper()
        alan["ilga_eden_madde"] = k.group(3)
    return alan


def kimlik_onar(kayit: dict) -> bool:
    """madde_no'ya düşmüş alt-madde sonekini geri taşır. Değişiklik olduysa True."""
    m = SONEK.match(kayit["text"])
    if not m or "/" in kayit["madde_no"]:
        return False
    kayit["madde_no"] = f"{kayit['madde_no']}/{m.group(1)}"
    kayit["text"] = kayit["text"][m.end():]
    return True


def _dogrula(kayitlar: list[dict]) -> None:
    """Ön-kayıtlı kabul ölçütü. Düşerse korpusa YAZILMAZ."""
    bul = lambda kno, mno: next(
        (r for r in kayitlar if r["kanun_no"] == kno and r["madde_no"] == mno), None
    )
    for kno, mno, bekle in [("1475", "Madde 15", True), ("1475", "Madde 14", False)]:
        r = bul(kno, mno)
        if r is None:
            sys.exit(f"❌ doğrulama: {kno}/{mno} korpusta yok")
        if r["mulga"] is not bekle:
            sys.exit(f"❌ doğrulama: {kno}/{mno} mulga={r['mulga']}, beklenen {bekle}")
    print("✅ doğrulama: 1475/15 mulga=True · 1475/14 mulga=False")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--korpus", required=True)
    ap.add_argument("--kuru", action="store_true", help="yazma, yalnız rapor")
    a = ap.parse_args()

    kayitlar = [json.loads(l) for l in open(a.korpus, encoding="utf-8")]
    onarilan = sum(kimlik_onar(r) for r in kayitlar)
    for r in kayitlar:
        r.update(yururluk(r["text"]))

    mulga = [r for r in kayitlar if r["mulga"]]
    kaynakli = sum(1 for r in mulga if r["ilga_eden_kanun"])
    print(f"satır {len(kayitlar)} · mulga {len(mulga)} "
          f"(ilga kaynağı çıkarılan {kaynakli}, %{100*kaynakli/max(len(mulga),1):.1f})")
    print(f"alt-madde kimliği onarılan: {onarilan}")
    _dogrula(kayitlar)

    if a.kuru:
        print("🔸 --kuru: korpus DEĞİŞMEDİ")
        return

    gecici = a.korpus + ".tmp"
    with open(gecici, "w", encoding="utf-8") as f:
        for r in kayitlar:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(gecici, a.korpus)
    print(f"✍️  yazıldı: {a.korpus}")


if __name__ == "__main__":
    main()
