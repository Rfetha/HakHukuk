#!/usr/bin/env python3
"""Madde anahtarı — altın etiketi korpusa bağlayan normalleştirme.

⚠️ Neden ayrı modül: burada yapılan bir hata SESSİZDİR. `Geçici Madde 1` ile
`Madde 1` aynı sayılırsa recall@k şişer ve hiçbir yerde hata çıkmaz.
Ölçüldü (2026-08-03): ayrım yapılmayınca 40.496 madde 27.706 anahtara düşüyor.
"""
import json
import re
from collections import defaultdict

_NUMARA = re.compile(r"(\d+[a-zA-Z/]*)")
_GECICI = re.compile(r"geçici", re.IGNORECASE)


def madde_anahtari(kanun_no: str, madde_no: str) -> tuple[str, str, str]:
    """(kanun_no, tip, numara) — büyük/küçük harf duyarsız, geçici maddeyi ayırır."""
    metin = str(madde_no).strip()
    tip = "GECICI" if _GECICI.search(metin) else "NORMAL"
    m = _NUMARA.search(metin)
    return (str(kanun_no).strip(), tip, m.group(1).upper() if m else metin.upper())


def korpus_indeksi(yol: str) -> dict[tuple, list[dict]]:
    """Korpusu anahtara göre indeksle. Aynı anahtarda birden çok kayıt olabilir
    (mükerrer/tadil) — ölçüldü: 4.188 anahtar. Recall'da HERHANGİ birine isabet sayılır."""
    idx = defaultdict(list)
    with open(yol, encoding="utf-8") as f:
        for satir in f:
            if not satir.strip():
                continue
            r = json.loads(satir)
            idx[madde_anahtari(r["kanun_no"], r["madde_no"])].append(r)
    return dict(idx)
