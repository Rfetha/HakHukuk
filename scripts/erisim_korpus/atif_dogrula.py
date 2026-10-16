#!/usr/bin/env python3
"""Atıf doğrulayıcı — **deterministik**, hakem gerektirmez (sprint3 Adım 2).

Cevaptaki kanun/madde atıflarını ayıklar ve korpusta **gerçekten var mı** diye bakar.
Uydurulan madde numarasını yakalar; A1'in (0,909) açığının bir kısmı burada kapanıyor
ve bu **kod**la kapandığı için hakem kütlesinden düşüyor.

⚠️ **En tehlikeli hata bu dosyada şu yöndedir:** ayrıştırıcı bir atıf biçimini tanımazsa
atıf **yok** sayılır ve red kapısı cevabı **geçirir** — yani sessiz yanlışlık, kapının
korumak için var olduğu şeyin tam tersi. Bu yüzden tanınmayan *"madde"* bahisleri
`AYRISTIRILAMADI` olarak **görünür** kalır; kapı onları doğrulanmamış sayar.

⚠️ `Geçici Madde 1` ile `Madde 1` **ayrı** anahtarlardır (`madde_anahtar.py`). Karıştıran
bir doğrulayıcı, var olmayan bir maddeyi onaylar.

Kullanım:
  python scripts/erisim_korpus/atif_dogrula.py --details outputs/eval/<koşu>/m1_<etiket>_detail.jsonl
"""
import argparse
import json
import os
import re
import sys
from dataclasses import dataclass

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
from madde_anahtar import madde_anahtari, korpus_indeksi  # noqa: E402

KORPUS = "data/corpus/mevzuat_maddeler.jsonl"

DOGRULANDI = "DOGRULANDI"
MADDE_YOK = "MADDE_YOK"
KANUN_YOK = "KANUN_YOK"
AYRISTIRILAMADI = "AYRISTIRILAMADI"
# Madde korpusta VAR ama yürürlükte DEĞİL. DOGRULANDI'dan ayrı bir hüküm olması şart:
# ölçüldü, "İŞ KANUNU Madde 15" (1475/15, 2003'te ilga) doğrulamayı ve katı kapıyı
# geçiyordu — vatandaşa mülga hükmün cevabı veriliyordu (sprint3 borç B7).
MULGA = "MULGA"

# "İŞ KANUNU Madde 21" · "HUKUK MUHAKEMELERİ KANUNU MADDE 436'nun" ·
# "(CEZA MUHAKEMESİ KANUNU, Madde 161)" · "KAT MÜLKİYETİ KANUNU Geçici Madde 1" ·
# "Türk Ceza Kanunu Madde 102" · "Türk Medeni Kanunu'nun Madde 313"
# ⚠️ Başlık biçimi ŞART: gerçek model çıktısı iki biçimi de yazıyor ve yalnız büyük
# harfi tanımak gerçek atıfları AYRISTIRILAMADI'ya düşürüyordu (ölçüldü: 5/49).
_SOZCUK = r"[A-ZÇĞİÖŞÜ][A-ZÇĞİÖŞÜa-zçğıöşü0-9'’]*"
_ATIF = re.compile(
    rf"(?P<kanun>(?:{_SOZCUK}\s+)*(?:KANUN[A-ZÇĞİÖŞÜ]*|Kanun[a-zçğıöşü]*))(?:['’]\w+)?"
    r"[\s,]+(?P<gecici>[Gg]eçici\s+)?(?:MADDE|Madde|madde)\s*(?P<no>\d+[/-]?[A-Za-zÇĞİÖŞÜçğıöşü]?)",
)
# Ayrıştırılamayan atıf sezgisi: "madde" geçiyor ama yukarıdaki kalıba oturmuyor.
# `bulunmuyor/bulunuyor` çekinme cümlesinin kendisidir — atıf değildir.
_MADDE_BAHSI = re.compile(r"\bmadde\w*\b", re.IGNORECASE)
_CEKINME_BAHSI = re.compile(r"madde\s+bulun(?:m[uı]yor|uyor)", re.IGNORECASE)


@dataclass(frozen=True)
class Atif:
    ham: str
    kanun: str
    madde: str
    tip: str          # "NORMAL" · "GECICI" · AYRISTIRILAMADI


@dataclass(frozen=True)
class Hukum:
    atif: Atif
    hukum: str
    kanun_no: str = ""
    # Why: çözülen kanunun ADI hükümle birlikte taşınır ki yanlış çözüm GÖZLE görülebilsin
    # (tuzak 1.13). Numara tek başına "193 mü 1319 mu" sorusunu okuyucuya sordurmaz.
    kanun_adi: str = ""


def atiflari_ayikla(cevap: str) -> list[Atif]:
    """Cevaptaki atıfları sırayla döndür. Tanınmayan madde bahsi AYRISTIRILAMADI olur."""
    metin = cevap or ""
    atiflar = [
        Atif(ham=m.group(0), kanun=m.group("kanun").strip(), madde=m.group("no").upper(),
             tip="GECICI" if m.group("gecici") else "NORMAL")
        for m in _ATIF.finditer(metin)
    ]
    if not atiflar and _MADDE_BAHSI.search(metin) and not _CEKINME_BAHSI.search(metin):
        # Why: burada sessiz kalmak kapıyı kör eder — bkz. modül docstring'i.
        atiflar.append(Atif(ham=metin.strip()[:120], kanun="", madde="",
                            tip=AYRISTIRILAMADI))
    return atiflar


ASGARI_SONEK_SOZCUK = 2   # "KANUNU" tek başına her kanuna uyar — doğrulayıcıyı öldürür

_SON_PARANTEZ = re.compile(r"\s*\([^()]*\)\s*$")


@dataclass(frozen=True)
class KanunDizini:
    """Ad çözümünün üç tablosu — `_dizin_kur` doldurur, `_ad_adaylari` okur."""
    sonek: dict      # ≥2 sözcüklü ad soneki → {kanun_no}
    tam: dict        # birebir ad → {kanun_no}
    adi: dict        # kanun_no → korpustaki ad


def _ad_varyantlari(ad: str) -> set:
    """Bir kanun adının eşleşmeye giren yazımları: tam ad + SONDAKİ parantezi atılmış hâli.

    ⚠️ Why: korpusta 16 kanunun adı parantez taşıyor, 7'sinde parantez **sondadır**
    (`GELİR VERGİSİ KANUNU (G.V.K.)`). Model parantezsiz yazar; parantezli ad birebir
    eşleşmediği için çözüm gevşek sonek eşleşmesine düşüyor ve YANLIŞ kanuna gidiyordu:
    *"Gelir Vergisi Kanunu Madde 73"* → `1319` EMLAK VERGİSİ KANUNU → `MADDE_YOK`
    (tuzak 1.13 · `outputs/eval/gorev/g22-atif-cozum/BULGU.md` §4).
    """
    tam = _ad_normal(ad)
    return {tam, _SON_PARANTEZ.sub("", tam)} - {""}


def _dizin_kur(kayitlar) -> KanunDizini:
    """Korpus kayıtlarından ad çözüm tablolarını kur.

    ⚠️ Why küme: bir ad birden çok kanuna ait olabilir. Ölçüldü — `İŞ KANUNU` hem
    **4857** (yürürlükte) hem **1475** (mülga) için geçerli. Ad→tek no eşlemesi
    sözlükte sessizce sonuncuyu tutuyor ve GERÇEK atıfları `MADDE_YOK` sayıyordu.

    ⚠️ Why sonek: model resmî adın yaygın **kısa hâlini** yazıyor ve bu hâl resmî
    adın sonekidir — *"İflas Kanunu"* ⊂ `İCRA VE İFLAS KANUNU`, *"Teknik Düzenlemeler
    Kanunu"* ⊂ `ÜRÜN GÜVENLİĞİ VE TEKNİK DÜZENLEMELER KANUNU`. Ölçüldü (harness AÇIK):
    5 `KANUN_YOK`'un **tamamı** bu yüzden yanlış negatifti ve katı kapıda her yanlış
    negatif **doğrudan coverage kaybıdır** (ADR-0038'in adını koyduğu kalibrasyon borcu).
    """
    sonek: dict = {}
    tam: dict = {}
    adi: dict = {}
    for r in kayitlar:
        no = str(r["kanun_no"]).strip()
        adi.setdefault(no, r.get("kanun_adi", ""))
        for varyant in _ad_varyantlari(r.get("kanun_adi", "")):
            tam.setdefault(varyant, set()).add(no)
            sozcukler = varyant.split()
            for i in range(len(sozcukler) - ASGARI_SONEK_SOZCUK + 1):
                sonek.setdefault(" ".join(sozcukler[i:]), set()).add(no)
    return KanunDizini(sonek, tam, adi)


def _ad_normal(ad: str) -> str:
    """Türkçe-duyarlı büyük harf + boşluk sadeleştirme.

    ⚠️ Why elle: Python'ın `upper()`'ı Türkçe değil — `i` → `I` yapıyor, oysa doğrusu
    `İ`. Korpus adları `TÜRK MEDENİ KANUNU`; `"Türk Medeni Kanunu".upper()` ise
    `TÜRK MEDENI KANUNU` verip eşleşmiyor ve GERÇEK atıf `KANUN_YOK` sayılıyordu.
    """
    s = re.sub(r"\s+", " ", (ad or "")).strip()
    return s.replace("i", "İ").replace("ı", "I").upper()


def _ad_adaylari(kanun: str, dizin: KanunDizini) -> set:
    """Atıftaki ad → kanun_no kümesi. **En çok TEK gevşeme**; yoksa boş küme.

    İki gevşemeye ayrı ayrı izin vardır, ikisine BİRDEN asla:
      (1) atıftaki adın **tamamı** bir kanun adının ≥2 sözcüklü soneki olabilir — model
          resmî adın kısa hâlini yazıyor, ayrıştırıcı da adı küçük harfli `ve`'de ya da
          `î`'de kesiyor (*"İflas Kanunu"* ⊂ `İCRA VE İFLAS KANUNU`).
      (2) ayrıştırıcı ad önüne başlık-harfli bir sözcük katmış olabilir (*"Ayrıca TÜRK
          BORÇLAR KANUNU"*); o sözcükler atılır, ama kalan **BİREBİR** bir kanun adı olmalı.

    ⚠️ İkisi birden serbest bırakılırsa (eski davranış) *"Gelir Vergisi Kanunu"* önce
    `GELİR`i atıp `VERGİSİ KANUNU` sonekine düşüyor ve **EMLAK VERGİSİ KANUNU**'na
    çözülüyordu — tuzak 1.13'ün ta kendisi.
    """
    sozcukler = _ad_normal(kanun).split()
    if len(sozcukler) < ASGARI_SONEK_SOZCUK:
        return set()
    adaylar = dizin.sonek.get(" ".join(sozcukler))
    if adaylar:
        return adaylar
    for i in range(1, len(sozcukler) - ASGARI_SONEK_SOZCUK + 1):
        adaylar = dizin.tam.get(" ".join(sozcukler[i:]))
        if adaylar:
            return adaylar
    return set()


def _gevsek_adaylar(kanun: str, dizin: KanunDizini) -> set:
    """ÇİFT gevşemeyle (baştan sözcük at **ve** korpus adının sonekine düş) ulaşılan adaylar.

    Yalnız *"bilmiyorum"* diyebilmek için hesaplanır: boş değilse ad **çözülememiştir** ve
    `AYRISTIRILAMADI` döner — sessizce bir kanun SEÇİLMEZ (tuzak 1.13 reçetesi).
    """
    sozcukler = _ad_normal(kanun).split()
    for i in range(1, len(sozcukler) - ASGARI_SONEK_SOZCUK + 1):
        adaylar = dizin.sonek.get(" ".join(sozcukler[i:]))
        if adaylar:
            return adaylar
    return set()


def _hukum(atif: Atif, dizin: KanunDizini, indeks: dict) -> Hukum:
    """Tek atıf → hüküm. Doğrulama mantığının TEK kaynağı.

    `indeks`: madde anahtarı → o anahtarı taşıyan korpus satırları (`korpus_indeksi`).
    Set değil sözlük olması, maddenin VARLIĞI ile YÜRÜRLÜĞÜNÜ aynı aramada görmek içindir.
    """
    if atif.tip == AYRISTIRILAMADI:
        return Hukum(atif, AYRISTIRILAMADI)
    adaylar = _ad_adaylari(atif.kanun, dizin)
    if not adaylar:
        # Ad çözülemedi ≠ kanun yok. Gevşek eşleşme bir kanun SEÇMEZ, görünür kalır
        # (tuzak 1.13); korpusta gerçekten olmayan kanun ise hüküm KANUN_YOK'tur.
        return Hukum(atif, AYRISTIRILAMADI if _gevsek_adaylar(atif.kanun, dizin)
                     else KANUN_YOK)
    # Ad çok anlamlıysa maddeyi TAŞIYAN kanun doğrular; hangisi olduğu hükme yazılır.
    # Why `all`: anahtar birden çok satıra düşebiliyor (korpusta madde kimliği yinelenebiliyor
    # — research_log #52). Yürürlükte TEK bir satır bile varsa atıf mülga sayılmaz; aksi hâlde
    # geçerli atıfları yanlışlıkla reddederiz.
    # ⚠️ Ve aynı ilke ADAYLAR ARASINDA da uygulanır. Eskiden `sorted(adaylar)` ilk taşıyanı
    # döndürüyordu; `İŞ KANUNU` için bu **1475** (mülga), oysa yürürlükteki **4857** de aynı
    # maddeyi taşıyor ⇒ DOĞRU cevap MÜLGA damgası yiyordu. Donmuş TEST'te yakalandı
    # (2026-09-09, id 32) ve vatandaşa giden rozeti etkiliyordu — sessiz değil, GÖRÜNÜR hata.
    tasiyan = [(kn, indeks[(kn, atif.tip, atif.madde)]) for kn in sorted(adaylar)
               if indeks.get((kn, atif.tip, atif.madde))]
    for kn, satirlar in tasiyan:
        if not all(r.get("mulga") for r in satirlar):
            return Hukum(atif, DOGRULANDI, kn, dizin.adi.get(kn, ""))
    if tasiyan:
        return Hukum(atif, MULGA, tasiyan[0][0], dizin.adi.get(tasiyan[0][0], ""))
    secilen = sorted(adaylar)[0]
    return Hukum(atif, MADDE_YOK, secilen, dizin.adi.get(secilen, ""))


def dogrula(atif: Atif, kayitlar) -> Hukum:
    """Atfı korpus kayıt listesine karşı doğrula (tek atışlık; toplu iş için `Dogrulayici`)."""
    indeks: dict = {}
    for r in kayitlar:
        indeks.setdefault(madde_anahtari(r["kanun_no"], r["madde_no"]), []).append(r)
    return _hukum(atif, _dizin_kur(kayitlar), indeks)


class Dogrulayici:
    """Korpus indeksini bir kez kurup çok cevabı doğrular (CLI ve harness bunu kullanır)."""

    def __init__(self, korpus_yolu: str = KORPUS):
        self._kayitlar = [json.loads(l) for l in open(korpus_yolu, encoding="utf-8") if l.strip()]
        self._dizin = _dizin_kur(self._kayitlar)
        self._indeks = korpus_indeksi(korpus_yolu)

    def cevabi_dogrula(self, cevap: str) -> list[Hukum]:
        return [_hukum(a, self._dizin, self._indeks) for a in atiflari_ayikla(cevap)]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--details", required=True, help="gen_eval_grounded çıktısı (*_detail.jsonl)")
    p.add_argument("--korpus", default=KORPUS)
    p.add_argument("--alan", default="cevap")
    a = p.parse_args()

    d = Dogrulayici(a.korpus)
    kayitlar = [json.loads(l) for l in open(a.details, encoding="utf-8") if l.strip()]
    sayac = {DOGRULANDI: 0, MULGA: 0, MADDE_YOK: 0, KANUN_YOK: 0, AYRISTIRILAMADI: 0}
    atifsiz = 0
    for r in kayitlar:
        h = d.cevabi_dogrula(r.get(a.alan, ""))
        if not h:
            atifsiz += 1
        for x in h:
            sayac[x.hukum] += 1
    toplam = sum(sayac.values())
    print(json.dumps({
        "n_cevap": len(kayitlar), "atifsiz_cevap": atifsiz,
        "n_atif": toplam, "dagilim": sayac,
        "dogrulanan_oran": round(sayac[DOGRULANDI] / toplam, 4) if toplam else None,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
