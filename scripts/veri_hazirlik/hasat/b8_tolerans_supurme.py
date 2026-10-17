#!/usr/bin/env python3
"""B8 — katı kapının yazım-hatası toleransı için EĞRİ ÖLÇÜMÜ (borç B8).

🔒 **Bu betik `atif_dogrula.py`'yi DEĞİŞTİRMEZ** (ADR-0056 Karar 4). Yalnız
*"tolerans şu olsaydı ne olurdu"*yu eldeki koşu çıktısı üzerinde sayar.

Neden ölçülmeden karar verilmez: tolerans kapıyı **gevşetir**. `ESERLERİ→ESELERİ`
(mesafe 1) kurtarılmalı, ama `TÜRK CEZA→TÜRK MEDENİ` asla. Aradaki eşik ampiriktir.

Kullanım:
  python scripts/veri_hazirlik/hasat/b8_tolerans_supurme.py \\
      --details outputs/eval/sprint2-olcum/s2-harness-k10-etiketli/h1_..._detail.jsonl \\
      --korpus  data/corpus/mevzuat_maddeler.jsonl
"""
import argparse
import json
import os
import sys

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
from hakhukuk.cekirdek.atif_dogrula import (Dogrulayici, DOGRULANDI, MULGA, KANUN_YOK,  # noqa: E402
                          ASGARI_SONEK_SOZCUK, _ad_normal)


def mesafe(a: str, b: str) -> int:
    """Levenshtein. Kütüphane yok — 40 satırlık bir bağımlılık eklemeye değmez."""
    a, b = _ad_normal(a), _ad_normal(b)
    if a == b:
        return 0
    onceki = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        simdi = [i]
        for j, cb in enumerate(b, 1):
            simdi.append(min(onceki[j] + 1, simdi[j - 1] + 1,
                             onceki[j - 1] + (ca != cb)))
        onceki = simdi
    return onceki[-1]


def _adaylar_toleransli(kanun: str, adlar: dict, esik: int) -> set:
    """`atif_dogrula._ad_adaylari`'nın toleranslı ikizi — kanun_no kümesi döndürür.

    ⚠️ Why sonek uzayında: doğrulayıcı tam adları değil, korpus adlarının **≥2 sözcüklü
    SONEKLERİNİ** indeksliyor, çünkü model resmî adın kısa hâlini yazıyor. Toleransı tam
    adlara uygulamak ölçtüğümüz şeyi ıskalar: gerçek vaka `"Sanat Eseleri Kanunu"` yazdı;
    tam ada mesafesi **11**, doğru sonek `SANAT ESERLERİ KANUNU`'na mesafesi **1**.

    ⚠️ Why tek sözcüklü sonekte duruyoruz: `mesafe("KANUNU", "İŞ KANUNU") == 3` — eşik 3'te
    "KANUNU" yazan her atıf yüzlerce kanuna eşleşir. Doğrulayıcının `ASGARI_SONEK_SOZCUK`
    kuralının toleranslı karşılığı budur; olmazsa eğri anlamsız biçimde şişer.
    """
    sozcukler = _ad_normal(kanun).split()
    for i in range(len(sozcukler) - ASGARI_SONEK_SOZCUK + 1):
        parca = " ".join(sozcukler[i:])
        eslesen = set()
        for ad, nolar in adlar.items():
            if mesafe(parca, ad) <= esik:
                eslesen |= nolar
        if eslesen:
            return eslesen
    return set()


def supur(detay_yolu: str, korpus_yolu: str, esikler=(0, 1, 2, 3)) -> dict:
    """Her eşik için: kaç `KANUN_YOK` kurtulur, kaç YANLIŞ kanuna eşleşir.

    Hüküm, doğrulayıcının kendi mantığıyla yeniden türetilir (`_hukum`'un aynısı):
    ad çözülür → madde o kanunda var mı bakılır. Ölçüt *"bağlamda mı"* değildir; kapı
    **hükme** bakıyor. Ama çözülen kanunun bağlamda olup olmadığı da ayrıca sayılır —
    gevşemenin riski tam orada: bağlamda hiç gösterilmemiş bir kanuna eşleşmek.

      kurtarilan     KANUN_YOK → DOGRULANDI, üstelik kanun BAĞLAMDA gösterilmiş
      yanlis_esleme  KANUN_YOK → DOGRULANDI, ama kanun bağlamda YOK  🚨 gevşemenin bedeli
      belirsiz       ad çözüldü ama madde o kanunda yok (MADDE_YOK) → kapı yine reddeder
    """
    dog = Dogrulayici(korpus_yolu)
    ad_no = {}   # kanun_no → kanun_adi (bağlam kontrolü için)
    for r in dog._kayitlar:
        if r.get("kanun_adi"):
            ad_no.setdefault(str(r["kanun_no"]).strip(), r["kanun_adi"])

    sonuc = {str(e): {"kurtarilan": 0, "yanlis_esleme": 0, "belirsiz": 0} for e in esikler}
    ornekler = []
    with open(detay_yolu, encoding="utf-8") as f:
        for satir in f:
            if not satir.strip():
                continue
            kayit = json.loads(satir)
            baglam = _ad_normal(kayit.get("context_shown") or "")
            for h in dog.cevabi_dogrula(kayit.get("cevap") or ""):
                if h.hukum != KANUN_YOK:
                    continue
                for e in esikler:
                    if e == 0:
                        continue
                    kova = sonuc[str(e)]
                    tasiyan = hukum = None
                    for kn in sorted(_adaylar_toleransli(h.atif.kanun, dog._dizin.sonek, e)):
                        satirlar = dog._indeks.get((kn, h.atif.tip, h.atif.madde))
                        if satirlar:
                            tasiyan = kn
                            hukum = MULGA if all(r.get("mulga") for r in satirlar) else DOGRULANDI
                            break
                        tasiyan = tasiyan or kn
                    if hukum is None:
                        if tasiyan:
                            kova["belirsiz"] += 1
                        continue
                    baglamda = _ad_normal(ad_no.get(tasiyan, "\0")) in baglam
                    kova["kurtarilan" if baglamda else "yanlis_esleme"] += 1
                    ornekler.append({
                        "id": kayit.get("id"), "esik": e, "yazilan": h.atif.kanun,
                        "madde": h.atif.madde, "cozulen_no": tasiyan,
                        "cozulen_ad": ad_no.get(tasiyan), "hukum": hukum,
                        "baglamda": baglamda,
                    })
    return {"esik_egrisi": sonuc, "ornekler": ornekler}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--details", required=True)
    p.add_argument("--korpus", default="data/corpus/mevzuat_maddeler.jsonl")
    p.add_argument("--out", default="")
    a = p.parse_args()

    cikti = {"kaynak": a.details, **supur(a.details, a.korpus)}
    print(json.dumps(cikti, ensure_ascii=False, indent=2))
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(cikti, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
