#!/usr/bin/env python3
"""Tamlık kapısının dosya tarafı (F0.5 c, ADR-0098 m.1): üretici `.part` adıyla yazar.

NEDEN: yarıda kesilen bir üretim geçerli bir JSONL bırakır, yalnız EKSİKTİR; adı tamamlanmış
dosyanınkiyle aynıysa ayırt edilemez (tuzak 5.10'un üretici tarafı). Burada dosya iş bitene
kadar `<yol>.part` adını taşır ve yalnız blok hatasız biterse `<yol>`'a taşınır; puanlama
`.part` ile biten yolu reddeder. Önceki tam dosya yarıda kesilen bir yeniden koşuda ezilmez.
"""
import json
import os
from contextlib import contextmanager

PART = ".part"


class TamamlanmamisDosya(Exception):
    """Okunmak istenen dosya bitmemiş bir üretimin ara ürünü."""


@contextmanager
def part_ile_yaz(yol: str):
    """`yol + '.part'`'a yazan dosya tutamacı verir; blok hatasız biterse `yol`'a taşır.

    Hata ya da kesinti olursa `.part` yerinde kalır ve hata yükselir (yutulmaz)."""
    ara = yol + PART
    with open(ara, "w", encoding="utf-8") as f:
        yield f
    os.replace(ara, yol)


def tamamlanmis_jsonl(yol: str) -> list:
    """JSONL oku; `.part` ile biten yol (bitmemiş üretim) reddedilir."""
    if yol.endswith(PART):
        raise TamamlanmamisDosya(
            f"{yol} bitmemiş bir üretimin ara ürünü — puanlanmaz. Üretim tamamlanınca "
            f"dosya `.part` eki olmadan yazılır.")
    with open(yol, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]
