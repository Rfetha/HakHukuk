#!/usr/bin/env python3
"""Atıf ÇÖZÜM denetimi — doğrulayıcı hangi kanuna çözdü? (yürütme tuzağı 1.13)

`atif_dogrula.Dogrulayici` atıftaki kanun adını **gevşek** (en uzun ≥2 sözcüklü sonek)
eşleştirir. Ölçüldü 2026-09-11: *"Gelir Vergisi Kanunu Madde 73"* → `1319` (EMLAK VERGİSİ
KANUNU). Yanlış-pozitif yönü (`MADDE_YOK` = uydurma damgası) zaten biliniyordu; bu betik
**TERS YÖNÜ** ölçer: atıf yanlış kanuna çözülüyor ama o kanunda aynı numaralı madde
**bulunduğu** için `DOGRULANDI` damgası alıyor mu? Bu yön gerçekleşiyorsa yayımlanan
*"uydurulmuş madde 0/114"* manşeti **iyimser** okunuyor demektir.

⛔ Bu betik bir ÖLÇÜMDÜR: `atif_dogrula.py`'ye DOKUNMAZ, onarım ayrı turdur (insan kararı:
"önce ölç"). Hüküm de insanındır — burada yalnız sayı ve gözle-okuma listesi üretilir.

⚠️ Ad karşılaştırması Türkçe-duyarlı yapılır: `str.upper()`/`lower()` Türkçe'de `i↔I`
eşlemesini bozar ve **aletin kendisi yanlış sayı üretir**. Karşılaştırma, denetlenen
modülünkinden BAĞIMSIZ olarak burada yeniden yazılmıştır — denetim, denetlediği hatayı
miras almamalıdır.

Kullanım:
  python scripts/erisim_korpus/atif/atif_cozum_denetle.py \
      --details outputs/eval/faz0/f02-biz-onsozsuz/h1_tgta_v1_f02_nb_detail.jsonl:cipa \
      --details outputs/eval/gorev/g22-kv-fp16/h1_tgta_v1_g22_fp16_detail.jsonl:fp16 \
      --out-dir outputs/eval/gorev/g22-atif-cozum
"""
import argparse
import json
import os
import sys
from collections import Counter, defaultdict

# ── scripts/ yol köprüsü (T5 2026-09-07 · ADR-0112 2026-10-16) ───────────────
# Kardeş modüller iç içe alt klasörlerde de bulunsun diye scripts/ kökü, altındaki HER
# derinlikteki klasör ve repo kökü sys.path'e girer. Uzantısız `import X` bu köprü olmadan
# taşımada SESSİZCE kırılır: ImportError çalışma zamanında, bazen GPU koşusunun ortasında.
# ⚠️ 39 dosyada BİREBİR aynı; değiştirirsen hepsinde değiştir (grep: "yol köprüsü").
import os, sys
_K = os.path.abspath(__file__)
_K = _K[:_K.rindex(os.sep + "scripts" + os.sep)] + os.sep + "scripts"  # dışarıda: ValueError
_Y = []
for _y, _alt, _f in os.walk(_K):
    _alt[:] = sorted(_a for _a in _alt if _a[0] not in "_.")
    _Y.append(_y)
sys.path[:0] = [*_Y, os.path.dirname(_K)]
# ─────────────────────────────────────────────────────────────────────────────
from hakhukuk.cekirdek.atif_dogrula import (KORPUS, DOGRULANDI, Dogrulayici, atiflari_ayikla,  # noqa: E402
                          _ad_adaylari)

TAM = "TAM"            # ad birebir aynı
SONEK = "SONEK"        # biri diğerinin sözcük-soneki ("İflas Kanunu" ⊂ "İCRA VE İFLAS KANUNU")
UYUSMAZ = "UYUSMAZ"    # gözle okunacak sınıf
COZUMSUZ = "COZUMSUZ"  # hüküm bir kanuna bağlanmadı (AYRISTIRILAMADI / KANUN_YOK)


def tr_kucuk(s: str) -> str:
    """Türkçe-duyarlı küçük harf. `I→ı`, `İ→i` elle eşlenir, sonra casefold.

    Why elle: `"İŞ".lower()` → `i̇ş` (birleşik nokta) ve `"KANUNU".lower()` sorunsuzken
    `"KANUNI".lower()` → `kanuni` yerine yanlış eşleşir; Python'ın varsayılanı Türkçe
    değildir. Bu satır yanlışsa denetimin ÜRETTİĞİ sayı yanlış olur, hata vermez.
    """
    return (s or "").replace("I", "ı").replace("İ", "i").casefold()


def sozcukler(ad: str) -> list[str]:
    return tr_kucuk(ad).replace("(", " ").replace(")", " ").replace(".", " ").split()


def _ikili_uyusma(a: list[str], k: list[str]) -> str:
    if not a or not k:
        return UYUSMAZ
    if a == k:
        return TAM
    if a == k[-len(a):] or k == a[-len(k):]:
        return SONEK
    return UYUSMAZ


def ad_uyusmasi(atif_adi: str, korpus_adlari_: list[str]) -> str:
    """Atıftaki ad, çözülen kanunun adlarından HERHANGİ biriyle örtüşüyor mu?

    Why sözcük-soneki, iki yönde: ayrıştırıcı ad öncesindeki başlık-harfli sözcüğü
    yutabiliyor (*"Ayrıca TÜRK BORÇLAR KANUNU"*), model de resmî adın kısa hâlini yazıyor.

    Why parantezsiz varyant: korpusta 16 kanun parantezli ad taşıyor
    (`GELİR VERGİSİ KANUNU (G.V.K.)`). Parantezi ada dahil sayarsak DOĞRU çözümü
    UYUSMAZ ilan ederiz — denetim kendi yanlış-pozitifini üretir. En İYİ sınıf alınır.
    """
    a = sozcukler(atif_adi)
    en_iyi = UYUSMAZ
    for ad in korpus_adlari_:
        for varyant in (ad, ad.split("(")[0]):
            h = _ikili_uyusma(a, sozcukler(varyant))
            if h == TAM:
                return TAM
            if h == SONEK:
                en_iyi = SONEK
    return en_iyi


def birebir_adaylar(atif_adi: str, tam_adlar: dict[str, set]) -> set:
    """Atıftaki adın, bir kanunun TAM adına (parantezsiz varyantı dahil) birebir eşiti.

    Why: ad-uyuşması testi yalnız ÇÖZÜLEN kanunu sorgular; adı uyuşan ama yine de yanlış
    kanuna gitmiş atıfları göremez (eş adlı kanunlar, `İŞ KANUNU` → 4857 ∧ 1475). Burada
    tersten sorulur: atıftaki ada BİREBİR uyan bir kanun var mı, ve çözüm ona mı gitti?
    """
    a = tuple(sozcukler(atif_adi))
    return {no for no, adlar_ in tam_adlar.items() if a in adlar_}


def tam_ad_indeksi(korpus_yolu: str) -> dict[str, set]:
    """kanun_no → {ad sözcük-demeti} (parantezli ve parantezsiz varyantlarıyla)."""
    idx: dict[str, set] = defaultdict(set)
    with open(korpus_yolu, encoding="utf-8") as f:
        for satir in f:
            if satir.strip():
                r = json.loads(satir)
                ad = r["kanun_adi"]
                no = str(r["kanun_no"]).strip()
                idx[no].add(tuple(sozcukler(ad)))
                idx[no].add(tuple(sozcukler(ad.split("(")[0])))
    return dict(idx)


def korpus_adlari(korpus_yolu: str) -> dict[str, set]:
    """kanun_no → o numaraya ait kanun adları kümesi."""
    adlar = defaultdict(set)
    with open(korpus_yolu, encoding="utf-8") as f:
        for satir in f:
            if satir.strip():
                r = json.loads(satir)
                adlar[str(r["kanun_no"]).strip()].add(r["kanun_adi"])
    return dict(adlar)


def denetle(details_yolu: str, etiket: str, d: Dogrulayici, adlar: dict,
            tam_adlar: dict, alan="cevap") -> list[dict]:
    """Her atıf için: hüküm + çözülen kanun_no + o numaranın korpustaki ADI + uyuşma sınıfı."""
    kayitlar = [json.loads(l) for l in open(details_yolu, encoding="utf-8") if l.strip()]
    cikti = []
    for r in kayitlar:
        cevap = r.get(alan, "")
        for atif, hukum in zip(atiflari_ayikla(cevap), d.cevabi_dogrula(cevap)):
            cozulen = sorted(adlar.get(hukum.kanun_no, [])) if hukum.kanun_no else []
            cozulen_ad = " | ".join(cozulen)
            cikti.append({
                "kosu": etiket, "soru_id": r.get("id"),
                "ham_atif": atif.ham, "atif_kanun_adi": atif.kanun,
                "atif_madde": atif.madde, "atif_tip": atif.tip,
                "hukum": hukum.hukum, "cozulen_kanun_no": hukum.kanun_no,
                "cozulen_kanun_adi": cozulen_ad,
                "uyusma": ad_uyusmasi(atif.kanun, cozulen) if hukum.kanun_no else COZUMSUZ,
                "aday_sayisi": len(_ad_adaylari(atif.kanun, d._dizin)) if atif.kanun else 0,
                "birebir_adaylar": sorted(birebir_adaylar(atif.kanun, tam_adlar)) if atif.kanun else [],
                "altin_kanun_no": str(r.get("kanun_no", "")), "altin_kanun_adi": r.get("kanun_adi", ""),
                "altin_madde_no": r.get("madde_no", ""),
            })
    return cikti


def parantezli_prob(d: Dogrulayici, korpus_yolu: str) -> list[dict]:
    """Adında parantez taşıyan HER kanun için sentetik prob ($0, ağ yok).

    İki istem: (a) ad BİREBİR (parantezli), (b) parantez atılmış hâli — modelin fiilen
    yazdığı biçim. Her ikisinde de doğru `kanun_no`ya çözüyor mu?
    """
    ilk_madde: dict[str, tuple] = {}
    with open(korpus_yolu, encoding="utf-8") as f:
        for satir in f:
            if not satir.strip():
                continue
            r = json.loads(satir)
            ad = r["kanun_adi"]
            if "(" not in ad:
                continue
            no = str(r["kanun_no"]).strip()
            madde = str(r["madde_no"])
            # Sentetik prob NORMAL madde ister: "Geçici Madde" ayrı anahtardır.
            if no in ilk_madde or "eçici" in madde or not any(c.isdigit() for c in madde):
                continue
            ilk_madde[no] = (ad, "".join(c for c in madde if c.isdigit()))

    sonuc = []
    for no, (ad, madde) in sorted(ilk_madde.items(), key=lambda kv: int(kv[0]) if kv[0].isdigit() else 0):
        satir = {"kanun_no": no, "kanun_adi": ad, "madde": madde}
        for anahtar, istem_adi in (("birebir", ad), ("parantezsiz", ad.split("(")[0].strip())):
            hukumler = d.cevabi_dogrula(f"{istem_adi} Madde {madde} uyarınca.")
            h = hukumler[0] if hukumler else None
            satir[anahtar] = {
                "istem": f"{istem_adi} Madde {madde}",
                "hukum": h.hukum if h else "ATIF_YOK",
                "cozulen_kanun_no": h.kanun_no if h else "",
                "dogru_kanuna_cozdu": bool(h and h.kanun_no == no),
            }
        sonuc.append(satir)
    return sonuc


def main():
    p = argparse.ArgumentParser(description="Atıf çözümünün DOĞRU kanuna gidip gitmediğini ölç")
    p.add_argument("--details", action="append", required=True,
                   help="<yol>[:etiket] — birden çok kez verilebilir")
    p.add_argument("--korpus", default=KORPUS)
    p.add_argument("--alan", default="cevap")
    p.add_argument("--out-dir", required=True)
    a = p.parse_args()

    os.makedirs(a.out_dir, exist_ok=True)
    d = Dogrulayici(a.korpus)
    adlar = korpus_adlari(a.korpus)
    tam_adlar = tam_ad_indeksi(a.korpus)

    satirlar: list[dict] = []
    for spec in a.details:
        yol, _, etiket = spec.partition(":")
        satirlar += denetle(yol, etiket or os.path.basename(yol), d, adlar, tam_adlar, a.alan)

    ham = os.path.join(a.out_dir, "atif_cozum.jsonl")
    with open(ham, "w", encoding="utf-8") as f:
        for s in satirlar:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    prob = parantezli_prob(d, a.korpus)
    with open(os.path.join(a.out_dir, "parantezli_prob.json"), "w", encoding="utf-8") as f:
        json.dump(prob, f, ensure_ascii=False, indent=2)

    for kosu in sorted({s["kosu"] for s in satirlar}):
        alt = [s for s in satirlar if s["kosu"] == kosu]
        sayac = Counter(s["uyusma"] for s in alt)
        uyusmaz = [s for s in alt if s["uyusma"] == UYUSMAZ]
        # Adı uyuşsa BİLE yanlış kanuna gitmiş olabilir: atıfla birebir aynı adlı bir kanun
        # var ama çözüm ona gitmediyse, ters yön ADAY DEMEKTİR — gözle okunur.
        kacak = [s for s in alt if s["birebir_adaylar"] and s["cozulen_kanun_no"]
                 and s["cozulen_kanun_no"] not in s["birebir_adaylar"]]
        cok_aday = [s for s in alt if s["aday_sayisi"] > 1]
        print(f"\n=== {kosu}: n_atif={len(alt)}  {dict(sayac)}  "
              f"UYUSMAZ∧DOGRULANDI={sum(1 for s in uyusmaz if s['hukum'] == DOGRULANDI)}")
        print(f"    birebir-adı-BAŞKA-kanunda: {len(kacak)} · çoklu aday (>1): {len(cok_aday)}")
        for s in kacak:
            print(f"      id={s['soru_id']} «{s['atif_kanun_adi']} m.{s['atif_madde']}» → "
                  f"{s['cozulen_kanun_no']} [{s['hukum']}] ama birebir ad: {s['birebir_adaylar']}")
        for s in uyusmaz:
            print(f"  id={s['soru_id']:>3}  «{s['atif_kanun_adi']} m.{s['atif_madde']}»  →  "
                  f"{s['cozulen_kanun_no']} {s['cozulen_kanun_adi']}  [{s['hukum']}]"
                  f"   altın: {s['altin_kanun_no']} {s['altin_kanun_adi']}")
    kotu = [x for x in prob if not x["parantezsiz"]["dogru_kanuna_cozdu"]]
    print(f"\n=== parantezli kanun: {len(prob)} · birebir adla yanlış çözülen: "
          f"{sum(1 for x in prob if not x['birebir']['dogru_kanuna_cozdu'])} · "
          f"parantezsiz adla yanlış çözülen: {len(kotu)}")
    for x in kotu:
        print(f"  {x['kanun_no']} {x['kanun_adi']} → {x['parantezsiz']['cozulen_kanun_no'] or '—'} "
              f"[{x['parantezsiz']['hukum']}]")
    print(f"\nham: {ham}")


if __name__ == "__main__":
    main()
