#!/usr/bin/env python3
"""Harness AÇIK ölçüm tablosu (sprint3 Adım 4) — deterministik eksenler.

Harness AÇIK bir koşunun `*_detail.jsonl`'ini okur ve şunları çıkarır:

  1. **Erişim** — altın madde getirildi mi, kaçıncı sırada (`recall@k`, modelden bağımsız)
  2. **Kütle** — coverage × A1. ⚠️ Tek eksenle okuma yasağı (Sprint 2'nin en pahalı dersi):
     A1 cevaplanan-only, çekinerek kazanmayı ödüllendirir. Hesap `kutle.py`'dedir (F0.5 a·c):
     payda `--kume`'nin boyutu; eksik/tutarsız girdide ya da hakem puanı olmayan cevaplanmış
     kalemde puanlama durur.
  3. **Kapı** — ADR-0038 katı + `cogunluk`/`cerrahi` ablasyonları, aynı küme üzerinde post-hoc
  4. **Atıf** — doğrulandı / madde yok / kanun yok / ayrıştırılamadı
  5. **K2'nin bedeli** — altın getirildi AMA cevap 900 char kırpmasının ötesinde kalmış olabilir

⚠️ **Kıyas şerhi.** `groundedness --mode data` yer-gerçeği olarak **tek** altın maddeyi
alır. Harness KAPALI'da altın bağlamda garanti; harness AÇIK'ta olmayabilir ve model
soruyu **başka** bir maddeden doğru cevaplasa bile bu ölçü onu sadakatsiz sayar. Bu yüzden
A1 hem tüm kümede hem **altın getirilen alt kümede** raporlanır — ikincisi ON/OFF için
kıyaslanabilir olandır.

Kullanım:
  python scripts/puanlama/tablo/harness_tablo.py --details outputs/eval/sprint2-olcum/s3-harness-acik/h1_<etiket>_detail.jsonl \\
      --gnd outputs/eval/sprint2-olcum/s3-harness-acik/gnd_h1_<etiket>.jsonl --kume data/eval/dev/core_hard.jsonl
"""
import argparse
import json
import os
import re
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
from hakhukuk.cekirdek.atif_dogrula import (Dogrulayici, DOGRULANDI, MADDE_YOK, KANUN_YOK,  # noqa: E402
                          AYRISTIRILAMADI, MULGA)
from red_kapisi import kapi, POLITIKALAR  # noqa: E402
from hakhukuk.cekirdek.madde_anahtar import madde_anahtari, korpus_indeksi  # noqa: E402
from kutle import DondurulmusKume, kutle_hesapla  # noqa: E402
import olcum_aleti  # noqa: E402
from part_dosya import tamamlanmis_jsonl  # noqa: E402


def _oran(pay, payda):
    return round(pay / payda, 4) if payda else None


def _icerik_kelimeleri(metin: str) -> set:
    """≥5 harfli kelimeler — kaba ama deterministik bir içerik-kelime filtresi.
    Türkçe durak kelimelerinin çoğu bu eşiğin altında kalır ve liste bakımı gerekmez."""
    return {w for w in re.findall(r"\w+", (metin or "").lower()) if len(w) >= 5}


def k2_bedeli(kayit, korpus_idx):
    """ADR-0054/K2'nin kabul edilen bedelini SINIFLANDIR (borç B5).

    Dört hâl var ve karıştırılmaları B1'i yanlış okutur:
      ALTIN_GELMEDI        erişim ıskaladı — kırpmanın suçu değil
      TAM                  altın maddenin tamamı bağlamda
      KIRPILDI             kırpıldı ama referans cevabın dayandığı cümle İÇERİDE
      KIRPILDI_CEVAP_DISI  🚨 B5'in çekirdeği: erişim başardı, kırpma cevabı KESTİ

    ⚠️ Why 4 sınıf: "kırpıldı" tek başına bir şey söylemez — 40.496 maddenin çoğu
    900 karakteri aşıyor. Anlamlı olan, kırpmanın CEVABI dışarıda bırakıp
    bırakmadığı. Tek sınıfa indirmek B5'i sistematik olarak şişirir.
    """
    izi = kayit.get("harness") or {}
    if izi.get("altin_sirasi") is None:
        return "ALTIN_GELMEDI"

    anahtar = madde_anahtari(kayit.get("kanun_no"), kayit.get("madde_no"))
    kayitlar = korpus_idx.get(anahtar) or []
    if not kayitlar:
        return "ALTIN_GELMEDI"
    tam_metin = max((r.get("text") or "" for r in kayitlar), key=len)

    gosterilen = kayit.get("context_shown") or ""
    if tam_metin and tam_metin in gosterilen:
        return "TAM"

    # Kırpıldı. Zararlı mı? Ölçüt: referans cevabın DAYANDIĞI kelimeler hâlâ
    # gösteriliyor mu. ⚠️ Why kuyruk eşleştirmesi DEĞİL: "son 60 karakter duruyor mu"
    # maddenin nerede bittiğini ölçer, cevabın nereye dayandığını değil — cevap
    # maddenin ortasındaki bir fıkraya dayanıyorsa o ölçü yanlış suçlama üretir.
    dayanak = _icerik_kelimeleri(kayit.get("referans") or "") & _icerik_kelimeleri(tam_metin)
    if not dayanak:
        return "KIRPILDI"          # dayanak çıkarılamadı → suçlanmaz (borç uydurulmaz)
    kalan = {w for w in dayanak if w in gosterilen.lower()}
    return "KIRPILDI" if len(kalan) / len(dayanak) >= 0.5 else "KIRPILDI_CEVAP_DISI"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--details", required=True)
    p.add_argument("--gnd", required=True, help="groundedness çıktısı (A1 için)")
    p.add_argument("--kume", required=True,
                   help="dondurulmuş soru kümesi (ör. data/eval/dev/core_hard.jsonl) — payda buradan")
    p.add_argument("--etiketler", default="",
                   help="ayirt_edicilik_etiketle.py çıktısı; verilirse sayılar iki alt kümede "
                        "AYRI raporlanır (ADR-0054/K4, borç B2)")
    p.add_argument("--korpus", default="data/corpus/mevzuat_maddeler.jsonl")
    p.add_argument("--out", default="")
    olcum_aleti.argparse_ekle(p)
    a = p.parse_args()
    alet = olcum_aleti.argumanlardan(a)

    kayitlar = tamamlanmis_jsonl(a.details)
    if not kayitlar or "harness" not in kayitlar[0]:
        raise SystemExit("[tablo] 🚫 bu dosyada harness izi yok — harness AÇIK koşusu mu?")
    n = len(kayitlar)
    k = kayitlar[0]["harness"]["k"]

    # 1) Erişim
    siralar = [r["harness"]["altin_sirasi"] for r in kayitlar]
    getirildi = [s is not None for s in siralar]
    # k'nın kendisi listeye girer: k süpürmesinin (borç B3) kabul ölçütü recall@k.
    erisim = {f"recall@{j}": _oran(sum(1 for s in siralar if s is not None and s < j), n)
              for j in sorted({1, 3, 5, k}) if j <= k}

    # 2) Kütle — tamlık ve payda kapıları dahil tek kaynaktan (kutle.py, F0.5 a·c).
    # 🚨 A1 = CEVAPLANAN-ONLY (ADR-0011 · tuzak 2.3). Çekinmeler de hakemden puan alıyor
    # (iddia üretiyorlar) ve makroyu kaydırıyorlar — üstelik SABİT YÖNDE DEĞİL: k=5'te
    # çekinenler 0,9091 alıp ALL'ı yukarı, k=10'da 0,6819 alıp aşağı çekti. Bu ayrım
    # yapılmazsa k kıyası TERSİNE döner (research_log #54).
    kume = DondurulmusKume.yukle(a.kume)
    gnd_satirlari = tamamlanmis_jsonl(a.gnd)
    ks = kutle_hesapla(kayitlar, gnd_satirlari, kume, alet)
    cevaplandi = {kl.id: kl.cevaplandi for kl in ks.kalemler}
    coverage, a1 = ks.kapsama, ks.A1
    a1_getirilen = ks.alt_kume([r["id"] for r, g in zip(kayitlar, getirildi) if g]).A1
    puanli = [g for g in gnd_satirlari if g.get("faithfulness") is not None]
    # Çekinmeler DAHİL makro — silinmiyor, doğru adıyla yanına yazılıyor (ADR-0050 kuralı:
    # sonucu gördükten sonra ölçüt değil ALET düzeltilir, eski alan kıyaslanabilirlik için kalır).
    faith_macro_tum = _oran(sum(g["faithfulness"] for g in puanli), len(puanli)) if puanli else None
    sira = {r["id"]: s for r, s in zip(kayitlar, siralar)}

    def eksenler(idler):
        """Aynı eksenler, bir id alt kümesi üzerinde — alt küme sayıları tüm kümeyle
        aynı tanımdan üretilsin diye tek yerden."""
        s = set(idler)
        m = len(s)
        alt = ks.alt_kume(s)
        return {
            "n": m,
            "erisim": {f"recall@{j}": _oran(sum(1 for i in s if sira[i] is not None
                                                and sira[i] < j), m)
                       for j in sorted({1, 3, 5, k}) if j <= k},
            "coverage": alt.kapsama,
            "A1_tum": alt.A1,
            "A1_altin_getirilen_alt_kume": alt.alt_kume([i for i in s if sira[i] is not None]).A1,
            "kutle_tum": alt.kutle,
        }

    # 3) Kapı (üç politika, post-hoc aynı küme — ADR-0038)
    d = Dogrulayici(a.korpus)
    _korpus_idx = korpus_indeksi(a.korpus)
    hukumler = [d.cevabi_dogrula(r.get("cevap", "")) for r in kayitlar]
    kapilar = {}
    for pol in POLITIKALAR:
        kararlar = [kapi(r.get("cevap", ""), h, pol) for r, h in zip(kayitlar, hukumler)]
        gecen = sum(1 for x in kararlar if x.gecti)
        kapilar[pol] = {
            "gecen": gecen, "reddedilen": n - gecen,
            "atifsiz_gecen": sum(1 for x in kararlar if x.gecti and x.n_atif == 0),
            "kapi_sonrasi_coverage": _oran(
                sum(1 for x, r in zip(kararlar, kayitlar) if x.gecti and cevaplandi[r["id"]]), n),
        }

    # 4) Atıf dağılımı
    dagilim = {x: 0 for x in (DOGRULANDI, MADDE_YOK, KANUN_YOK, AYRISTIRILAMADI, MULGA)}
    for hs in hukumler:
        for h in hs:
            dagilim[h.hukum] += 1

    # 5) Erişim ↔ davranış çapraz tablosu — harness'ın asıl sınavı
    cev = [cevaplandi[r["id"]] for r in kayitlar]
    capraz = {
        "altin_geldi_cevapladi": sum(1 for g, c in zip(getirildi, cev) if g and c),
        "altin_geldi_cekindi": sum(1 for g, c in zip(getirildi, cev) if g and not c),
        "altin_gelmedi_cevapladi": sum(1 for g, c in zip(getirildi, cev) if not g and c),
        "altin_gelmedi_cekindi": sum(1 for g, c in zip(getirildi, cev) if not g and not c),
    }

    # 6) Ayırt-edicilik alt kümeleri (borç B2). `recall@k` bu kümenin tavanı olabilir —
    # tuzak 7.4; etiket kümeyi değiştirmeden sayıyı iki eksene ayırır.
    alt_kumeler = None
    if a.etiketler:
        et = {}
        for l in open(a.etiketler, encoding="utf-8"):
            if l.strip():
                d = json.loads(l)
                et[d["id"]] = d["ayirt_edici"]
        eksik = [r["id"] for r in kayitlar if r["id"] not in et]
        if eksik:
            raise SystemExit(f"[tablo] 🚫 {len(eksik)} kalemin etiketi yok (ör. id={eksik[:5]}) — "
                             "etiketleme kümesi bu koşuyla aynı değil, sayı üretilmez.")
        alt_kumeler = {
            "ayirt_edici": eksenler([i for i in et if et[i]]),
            "belirsiz": eksenler([i for i in et if not et[i]]),
        }

    sonuc = {
        "kaynak": a.details, "n": n, "harness_k": k,
        "kume": kume.kunye(), "olcum_aleti": alet.kunye(),
        "erisim": erisim,
        "kutle_ekseni": {"coverage": coverage,
                         "A1_cevaplanan": a1,
                         "faith_macro_tum_cekinme_dahil": faith_macro_tum,
                         "A1_tum": a1,      # geriye dönük ad; artık CEVAPLANAN-only (bkz. #54)
                         "A1_altin_getirilen_alt_kume": a1_getirilen,
                         "kutle_tum": ks.kutle,
                         "n_cevaplanan": ks.n_cevaplanan,
                         "n_puanli_cevaplanan": ks.n_puanli_cevaplanan,
                         "n_sifir_iddia": ks.n_sifir_iddia},
        "kapi": kapilar,
        "atif_dagilimi": dagilim,
        "erisim_davranis_caprazi": capraz,
        "k2_bedeli": {
            sinif: sum(1 for r in kayitlar if k2_bedeli(r, _korpus_idx) == sinif)
            for sinif in ("ALTIN_GELMEDI", "TAM", "KIRPILDI", "KIRPILDI_CEVAP_DISI")
        },
        "ayirt_edicilik_alt_kumeleri": alt_kumeler,
        "not": ("A1 tek-altın yer-gerçeğine göre; harness AÇIK'ta model BAŞKA bir maddeden "
                "doğru cevaplasa da sadakatsiz sayılır → ON/OFF kıyası için "
                "A1_altin_getirilen_alt_kume kullanılır."),
    }
    print(json.dumps(sonuc, ensure_ascii=False, indent=2))
    if a.out:
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        json.dump(sonuc, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"[tablo] → {a.out}")


if __name__ == "__main__":
    main()
