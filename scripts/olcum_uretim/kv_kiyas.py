#!/usr/bin/env python3
"""KV önbelleği kuantizasyon kıyası — HAKEMSİZ, deterministik (Görev 22 Adım 1).

İki `*_detail.jsonl` koşusunu kalem kalem karşılaştırır. İki koşu arasında REJİMİN
tek farkı `--cache-type-k/-v` olmalıdır; bu betik farkın BÜYÜKLÜĞÜNÜ ölçer.

⛔ KÜTLE HESAPLAMAZ — kütle hakem ister. Burada yalnız hakemsiz eksenler var:
   bayt kimliği (sha256) · çekinme (`exact_reject`, mode=data) · kesik/boş ·
   uzunluk dağılımı · uydurulmuş madde numarası (`atif_dogrula`, korpusa karşı) ·
   durum sınıfı (`hakhukuk.cekirdek.terazi.siniflandir`) · erişim kontrolü (getirilen birebir mi).

Erişim kontrolü bir KONTROL DEĞİŞKENİDİR: retriever KV'den bağımsızdır, bu yüzden
getirilen kaynaklar birebir aynı olmalıdır. Olmazsa fark KV'ye atfedilemez.

Kullanım:
  python scripts/olcum_uretim/kv_kiyas.py --cipa <detail.jsonl> --yeni <detail.jsonl> \
      [--out KARSILASTIRMA.json]
"""
import argparse
import hashlib
import json
import statistics

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
from score_abstention import exact_reject  # noqa: E402
from atif_dogrula import Dogrulayici, MADDE_YOK, AYRISTIRILAMADI  # noqa: E402
from hakhukuk.cekirdek.terazi import siniflandir  # noqa: E402
from hakhukuk.cekirdek.tipler import Kaynak  # noqa: E402

# Why "data": `harness_tablo.py:122` çekinmeyi BU modda sayar ve çıpanın 5/80'i oradan
# doğdu (GOZLE_OKUMA_80.md §1 gözle doğruladı). Başka bir mod SESSİZCE başka sayı üretir
# (ADR-0061). Mod künyeye basılır.
MOD = "data"

KORPUS = "data/corpus/mevzuat_maddeler.jsonl"


def _kanun_no_haritasi(korpus=KORPUS):
    """(kanun_adi, madde_no) → kanun_no. `harness.getirilen` kanun NUMARASINI taşımıyor.

    Why yürürlükte olan tercih edilir: aynı ad+madde iki kanunda olabiliyor (İŞ KANUNU
    Madde 111 → 4857 ve mülga 1475). Canlı retriever 2026-09-07'den beri mülgayı ELİYOR
    (A8b), dolayısıyla yürürlükteki kayıt getirilenin kimliğine daha yakındır. Bu bir
    YENİDEN KURULUMDUR; ürün yolunda `kanun_no` doğrudan taşınır, burada türetilir.
    """
    harita = {}
    for satir in open(korpus, encoding="utf-8"):
        if not satir.strip():
            continue
        r = json.loads(satir)
        anahtar = (r["kanun_adi"], r["madde_no"])
        if anahtar not in harita or (harita[anahtar][1] and not r.get("mulga")):
            harita[anahtar] = (str(r["kanun_no"]), bool(r.get("mulga")))
    return {k: v[0] for k, v in harita.items()}


def _kaynaklar(kayit, harita):
    out = []
    for sira, ham in enumerate((kayit.get("harness") or {}).get("getirilen") or [], 1):
        kanun_adi, _, madde_no = ham.partition("|")
        out.append(Kaynak(kanun_adi=kanun_adi, kanun_no=harita.get((kanun_adi, madde_no), ""),
                          madde_no=madde_no, metin="", sira=sira))
    return tuple(out)


def oku(yol):
    kayitlar = [json.loads(l) for l in open(yol, encoding="utf-8") if l.strip()]
    return {k["id"]: k for k in kayitlar}


def sha(metin):
    return hashlib.sha256((metin or "").encode("utf-8")).hexdigest()


def ozet(kayitlar):
    uz = [len(k.get("cevap") or "") for k in kayitlar.values()]
    tok = [k["completion_tokens"] for k in kayitlar.values() if k.get("completion_tokens")]
    return {
        "n": len(kayitlar),
        "cekinme_n": sum(1 for k in kayitlar.values()
                         if exact_reject(k.get("cevap", ""), MOD)),
        "cekinme_idler": sorted(i for i, k in kayitlar.items()
                                if exact_reject(k.get("cevap", ""), MOD)),
        "kesik_n": sum(1 for k in kayitlar.values() if k.get("finish_reason") == "length"),
        "kesik_idler": sorted(i for i, k in kayitlar.items()
                              if k.get("finish_reason") == "length"),
        "bos_n": sum(1 for k in kayitlar.values() if not (k.get("cevap") or "").strip()),
        "bos_idler": sorted(i for i, k in kayitlar.items()
                            if not (k.get("cevap") or "").strip()),
        "zorla_kapatma_n": sum(1 for k in kayitlar.values() if k.get("forced_close")),
        "uzunluk_medyan": statistics.median(uz),
        "uzunluk_ortalama": round(statistics.mean(uz), 1),
        "uzunluk_min": min(uz),
        "uzunluk_maks": max(uz),
        "completion_tokens_ort": round(statistics.mean(tok), 1) if tok else None,
        "completion_tokens_medyan": statistics.median(tok) if tok else None,
        "completion_tokens_toplam": sum(tok) if tok else None,
    }


def fark_dagilimi(c, y, alan):
    """Kalem başına farkın dağılımı. `alan(kayit) -> sayı`."""
    farklar = sorted(((alan(y[i]) - alan(c[i]), i) for i in c), reverse=True)
    return {
        "uzayan_n": sum(1 for f, _ in farklar if f > 0),
        "kisalan_n": sum(1 for f, _ in farklar if f < 0),
        "ayni_n": sum(1 for f, _ in farklar if f == 0),
        "en_cok_uzayan": [{"id": i, "fark": f} for f, i in farklar[:2]],
        "en_cok_kisalan": [{"id": i, "fark": f} for f, i in farklar[-2:]],
        "mutlak_fark_medyan": statistics.median(abs(f) for f, _ in farklar),
    }


def atif_ozeti(kayitlar, dogrulayici):
    """Deterministik atıf doğrulama — uydurulmuş madde = MADDE_YOK (korpusta yok)."""
    sayac, atifsiz, uydurma_idler, ayristirilamadi_idler = {}, 0, [], []
    for i, k in sorted(kayitlar.items()):
        hukumler = dogrulayici.cevabi_dogrula(k.get("cevap", ""))
        if not hukumler:
            atifsiz += 1
        for h in hukumler:
            sayac[h.hukum] = sayac.get(h.hukum, 0) + 1
            if h.hukum == MADDE_YOK:
                uydurma_idler.append({"id": i, "kanun": h.atif.kanun, "madde": h.atif.madde})
            elif h.hukum == AYRISTIRILAMADI:
                ayristirilamadi_idler.append(i)
    toplam = sum(sayac.values())
    return {
        "n_atif": toplam,
        "atifsiz_cevap": atifsiz,
        "dagilim": sayac,
        "uydurulmus_madde": f"{sayac.get(MADDE_YOK, 0)}/{toplam}",
        "uydurulmus_kalemler": uydurma_idler,
        "ayristirilamadi_idler": ayristirilamadi_idler,
    }


def durum_ozeti(kayitlar, harita):
    """`hakhukuk.cekirdek.terazi.siniflandir` — ürün yüzeyinin dört durumu."""
    return {i: siniflandir(k.get("cevap", "") or "", _kaynaklar(k, harita),
                           k.get("finish_reason", ""))[0].value
            for i, k in kayitlar.items()}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cipa", required=True)
    p.add_argument("--yeni", required=True)
    p.add_argument("--out", default="")
    a = p.parse_args()

    c, y = oku(a.cipa), oku(a.yeni)
    if set(c) != set(y):
        raise SystemExit(f"🚫 id kümeleri farklı — kıyas GEÇERSİZ "
                         f"(yalnız çıpada {sorted(set(c)-set(y))}, yalnız yenide {sorted(set(y)-set(c))})")

    # ── KONTROL DEĞİŞKENİ: retriever KV'den bağımsız; getirilenler birebir olmalı ──
    erisim_sapan = sorted(i for i in c
                          if (c[i].get("harness") or {}).get("getirilen")
                          != (y[i].get("harness") or {}).get("getirilen"))
    soru_sapan = sorted(i for i in c if c[i].get("soru") != y[i].get("soru"))

    degisen = sorted(i for i in c if sha(c[i].get("cevap")) != sha(y[i].get("cevap")))
    oc, oy = ozet(c), ozet(y)

    harita = _kanun_no_haritasi()
    dogrulayici = Dogrulayici()
    dc, dy = durum_ozeti(c, harita), durum_ozeti(y, harita)
    gecisler = {}
    for i in sorted(c):
        if dc[i] != dy[i]:
            gecisler.setdefault(f"{dc[i]} → {dy[i]}", []).append(i)

    cek_c, cek_y = set(oc["cekinme_idler"]), set(oy["cekinme_idler"])
    sonuc = {
        "cipa_dosya": a.cipa,
        "yeni_dosya": a.yeni,
        "cekinme_dedektoru": f"score_abstention.exact_reject(cevap, mode={MOD!r})",
        "kontrol_degiskenleri": {
            "getirilen_kaynak_sapan_idler": erisim_sapan,
            "soru_metni_sapan_idler": soru_sapan,
        },
        "bayt_kimligi": {
            "degisen_n": len(degisen),
            "degismeyen_n": len(c) - len(degisen),
            "degisen_idler": degisen,
        },
        "cipa": oc,
        "yeni": oy,
        "cekinme_yon_degistiren": {
            "cipada_cekindi_yenide_cevapladi": sorted(cek_c - cek_y),
            "cipada_cevapladi_yenide_cekindi": sorted(cek_y - cek_c),
        },
        "uzunluk_farki_karakter": fark_dagilimi(c, y, lambda k: len(k.get("cevap") or "")),
        "uzunluk_farki_token": fark_dagilimi(c, y, lambda k: k.get("completion_tokens") or 0),
        "atif_cipa": atif_ozeti(c, dogrulayici),
        "atif_yeni": atif_ozeti(y, dogrulayici),
        "durum_sinifi": {
            "cipa_dagilim": {d: sum(1 for v in dc.values() if v == d) for d in sorted(set(dc.values()))},
            "yeni_dagilim": {d: sum(1 for v in dy.values() if v == d) for d in sorted(set(dy.values()))},
            "degisen_n": sum(1 for i in c if dc[i] != dy[i]),
            "gecisler": gecisler,
        },
        "kesik_yon_degistiren": {
            "cipada_kesik_yenide_degil": sorted(set(oc["kesik_idler"]) - set(oy["kesik_idler"])),
            "cipada_degil_yenide_kesik": sorted(set(oy["kesik_idler"]) - set(oc["kesik_idler"])),
        },
    }
    metin = json.dumps(sonuc, ensure_ascii=False, indent=2)
    print(metin)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(metin + "\n")
        print(f"\n→ {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
