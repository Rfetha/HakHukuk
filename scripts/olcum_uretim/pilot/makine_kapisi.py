#!/usr/bin/env python3
"""F0.16 — makine geçiş kapısı (ADR-0098 m.3) ve pilotun "birebir aynı cevap oranı".

Kural: üretime giren her yeni makine, seçilen kart tipinin ilk makinesinin referans cevaplarının TAMAMINI
(en uzun bağlamlılar dahil, alt küme yok) birebir yeniden üretir; tek cevap farklıysa o makine kullanılmaz.
Karşılaştırma `cevap` alanında, tam metin eşitliğidir (tek noktalama farkı da farktır).

İki dosya aynı dondurulmuş bağlamdan üretilmiş olmalı (`harness.donmus_baglam` sha256'sı aynı); değilse
cevap farkı makinenin değil girdinin farkıdır ve karşılaştırma durur.

Kullanım:
  python scripts/olcum_uretim/pilot/makine_kapisi.py --referans REF_detail.jsonl --aday YENI_detail.jsonl
  → çıkış kodu 0: kapı geçti · 1: kapı düştü
"""
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
import argparse  # noqa: E402
import json  # noqa: E402

from part_dosya import tamamlanmis_jsonl  # noqa: E402


def _id_haritasi(satirlar: list[dict], ad: str) -> dict:
    harita = {r["id"]: r for r in satirlar}
    if len(harita) != len(satirlar):
        raise SystemExit(f"[makine-kapisi] 🚫 {ad}: {len(satirlar)} satır, {len(harita)} tekil id "
                         f"(yinelenen kalem)")
    return harita


def _baglam_imzasi(satirlar: list[dict], ad: str) -> str:
    imzalar = {(r.get("harness") or {}).get("donmus_baglam") for r in satirlar}
    if len(imzalar) != 1 or None in imzalar:
        raise SystemExit(f"[makine-kapisi] 🚫 {ad}: donmus_baglam imzası tek ve dolu değil ({imzalar}) — "
                         f"dosya dondurulmuş bağlamla üretilmemiş")
    return imzalar.pop()


def karsilastir(referans: list[dict], aday: list[dict]) -> dict:
    """→ {n, ayni, farkli_id, gecti}. Kalem kümeleri ya da bağlam imzaları farklıysa DURUR."""
    ref, ady = _id_haritasi(referans, "referans"), _id_haritasi(aday, "aday")
    if set(ref) != set(ady):
        raise SystemExit(f"[makine-kapisi] 🚫 id kümeleri farklı: yalnız referansta "
                         f"{sorted(set(ref) - set(ady))[:10]} · yalnız adayda {sorted(set(ady) - set(ref))[:10]}")
    imza_r, imza_a = _baglam_imzasi(referans, "referans"), _baglam_imzasi(aday, "aday")
    if imza_r != imza_a:
        raise SystemExit(f"[makine-kapisi] 🚫 donmus_baglam farklı: {imza_r[:12]}… ↔ {imza_a[:12]}… — "
                         f"cevap farkı makinenin değil bağlamın farkı olurdu")
    farkli = sorted(i for i in ref if ref[i]["cevap"] != ady[i]["cevap"])
    return {"n": len(ref), "ayni": len(ref) - len(farkli), "farkli_id": farkli, "gecti": not farkli}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="F0.16 makine geçiş kapısı (ADR-0098 m.3)")
    p.add_argument("--referans", required=True)
    p.add_argument("--aday", required=True)
    a = p.parse_args(argv)
    s = karsilastir(tamamlanmis_jsonl(a.referans), tamamlanmis_jsonl(a.aday))
    print(json.dumps(s, ensure_ascii=False))
    print(f"[makine-kapisi] {s['ayni']}/{s['n']} birebir aynı → "
          + ("✅ GEÇTİ" if s["gecti"] else f"🚫 DÜŞTÜ (farklı id: {s['farkli_id'][:20]})"))
    return 0 if s["gecti"] else 1


if __name__ == "__main__":
    sys.exit(main())
