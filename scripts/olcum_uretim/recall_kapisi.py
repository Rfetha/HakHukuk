#!/usr/bin/env python3
"""recall@10 GEÇERLİLİK KAPISI — `*_detail.jsonl`'deki `harness` alanından okur.

Kusur 33 (ADR-0083 §A): `yeniden_uret.sh`'ın eski kapısı `gold_retrieved`/`altin_getirildi`
alanlarını okuyordu — bu alanlar detay kayıtlarında hiç YOK, kapı bu yüzden HER ZAMAN 0
sayıp düşüyordu (çıpanın kendi verisinde bile: f02, gerçek recall 76/80=0,9500 iken kapının
hesabı 0/80'di). Gerçek şekil:

    "harness": {"k": 10, "altin_dusuruldu": false, "altin_sirasi": 3, "getirilen": [...]}

`altin_sirasi` 0-tabanlıdır (doğrulama: f02 kayıt 0'da altın kaynak `getirilen[3]`'te ve
`altin_sirasi == 3`). `altin_dusuruldu=true` ise 900-karakter kırpması altın maddeyi
listeden düşürmüş demektir — bulunamadı sayılır.

`recall_at_k` (`erisim_korpus/recall_olc.py`) zaten bir sıra listesinden recall hesaplıyor;
burada tek iş `harness` alanından o sıra listesini ÇIKARMAK — hesap tekrar edilmez.
"""
from __future__ import annotations

# ── scripts/ yol köprüsü (T5, 2026-09-07) ────────────────────────────────────
# Kardeş modüller alt klasörlere bölündükten SONRA da bulunsun diye scripts/ kökü, tüm
# alt klasörleri ve repo kökü sys.path'e girer. Uzantısız `import X` bu köprü olmadan
# taşımada SESSİZCE kırılır: ImportError çalışma zamanında, bazen GPU koşusunun ortasında.
# ⚠️ 26 dosyada BİREBİR aynı; değiştirirsen hepsinde değiştir (grep: "yol köprüsü").
import os, sys
_K = os.path.dirname(os.path.abspath(__file__))
_K = _K if os.path.basename(_K) == "scripts" else os.path.dirname(_K)
sys.path[:0] = [_K, *(os.path.join(_K, _d) for _d in sorted(os.listdir(_K))
                      if os.path.isdir(os.path.join(_K, _d)) and _d[0] not in "_."),
                os.path.dirname(_K)]
# ─────────────────────────────────────────────────────────────────────────────
from recall_olc import recall_at_k  # noqa: E402


def harness_siralari(satirlar: list[dict]) -> list:
    """Her kayıttan altının kaçıncı sırada geldiğini çıkarır (0-tabanlı, None = yok).

    `harness` alanı eksik bir kayıtta sessizce 0 saymak kusur 33'ün ta kendisidir —
    bu yüzden GÜRÜLTÜLÜ patlar.
    """
    siralar = []
    for i, r in enumerate(satirlar):
        if "harness" not in r:
            raise KeyError(
                f"kayıt {i} (id={r.get('id', i)!r}): 'harness' alanı yok — "
                "recall@10 sessizce 0 sayılamaz (kusur 33, ADR-0083 §A)")
        h = r["harness"]
        siralar.append(None if h.get("altin_dusuruldu") else h.get("altin_sirasi"))
    return siralar


def recall_at_10(satirlar: list[dict]) -> float:
    """Geçerlilik kapısının kullandığı recall@10 — bkz. modül docstring'i."""
    return recall_at_k(harness_siralari(satirlar), 10)
