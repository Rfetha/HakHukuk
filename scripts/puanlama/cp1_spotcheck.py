#!/usr/bin/env python3
"""CP1 — muafiyet sınırının elle doğrulaması (ADR-0041 "Sonuç" maddesi, ~20 örnek).

Kural DAR olmalı: *kaynak seçimi/eleme* cümleleri ayrıştırılmamalı, ama kaynağın **içeriği**
hakkındaki her iddia puanlanmaya devam etmeli. Gevşek bir muafiyet `τ_g`'nin gerçek hatalarını
da siler ve sayıyı bizim lehimize kaydırır — bu, düzeltmenin kendisinden büyük bir taraflılık olur.

Bu betik karar VERMEZ; iki koşunun iddia listelerini yan yana basar, gözle okunur.
İki otomatik sayaç da üretir:
  · kaybolan iddialardan kaçı SEÇİM kalıbına uyuyor  (beklenen: hepsi ≈ muafiyet doğru çalışıyor)
  · kaybolan iddialardan kaçı uymuyor                (⚠️ aşırı-silme sinyali — elle bakılır)

Kullanım:
  python scripts/puanlama/cp1_spotcheck.py --old outputs/eval/cp/cp09-butceli-1024-512 \
      --new outputs/eval/cp/cp1-hakem-meta-iddia --label m1_tg_v1_th --n 20
"""
import argparse
import json
import re

# Seçim/eleme kalıbı: öznesi bir KAYNAK olan ve ilgililik/konu/cevaplayabilirlik söyleyen cümle.
SECIM_RE = re.compile(
    r"(kaynak\s*\d|bu kaynak|diğer kaynaklar|kaynaklar(?:ın|dan)?\b|ilgili kaynak)",
    re.IGNORECASE)
ICERIK_IPUCU_RE = re.compile(
    r"(madde|fıkra|gün|süre|hak|yüküml|şart|ceza|tazminat|dava|başvur|karar ver|zorunlu|"
    r"edilebilir|verilir|uygulanır|sayılır|tabi)", re.IGNORECASE)


def load(p):
    return {r["id"]: r for r in
            (json.loads(l) for l in open(p, encoding="utf-8") if l.strip())}


def claims(rec):
    return [(c.get("claim", ""), c.get("label", "")) for c in rec.get("labels", [])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", required=True)
    ap.add_argument("--new", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--n", type=int, default=20)
    a = ap.parse_args()

    old = load(f"{a.old}/gnd_{a.label}.jsonl")
    new = load(f"{a.new}/gnd_{a.label}.jsonl")
    ids = sorted(set(old) & set(new))

    kayip_secim = kayip_diger = yeni_eklenen = 0
    ornek_diger = []
    shown = 0
    for i in ids:
        o, n = claims(old[i]), claims(new[i])
        otxt = {c for c, _ in o}
        ntxt = {c for c, _ in n}
        kayip = [c for c in o if c[0] not in ntxt]
        eklenen = [c for c in n if c[0] not in otxt]
        yeni_eklenen += len(eklenen)
        for c, lab in kayip:
            if SECIM_RE.search(c):
                kayip_secim += 1
            else:
                kayip_diger += 1
                ornek_diger.append((i, lab, c))
        if kayip and shown < a.n:
            shown += 1
            print(f"\n=== id {i}  (eski {len(o)} iddia → yeni {len(n)})")
            for c, lab in kayip:
                bayrak = "SEÇİM ✓" if SECIM_RE.search(c) else "⚠️ SEÇİM DEĞİL"
                print(f"  − [{lab:<14}] {bayrak}  {c[:130]}")
            for c, lab in n:
                print(f"    [{lab:<14}]           {c[:130]}")

    print("\n" + "=" * 70)
    print(f"{a.label}: kaybolan iddia — SEÇİM kalıbına uyan: {kayip_secim} · "
          f"uymayan: {kayip_diger} · yeni eklenen: {yeni_eklenen}")
    if kayip_diger:
        print("\n⚠️ SEÇİM kalıbına UYMAYAN kayıplar (aşırı-silme adayları, elle okunur):")
        for i, lab, c in ornek_diger[:15]:
            ic = "içerik-ipucu VAR" if ICERIK_IPUCU_RE.search(c) else "içerik-ipucu yok"
            print(f"  id={i} [{lab}] ({ic}) {c[:140]}")
    else:
        print("✅ Kaybolan her iddia seçim/eleme kalıbına uyuyor — muafiyet DAR kalmış.")


if __name__ == "__main__":
    main()
