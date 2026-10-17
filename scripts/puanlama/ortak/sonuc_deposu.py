#!/usr/bin/env python
"""Hakem sonuç deposu (#74 R4) — aynı hakem aynı girdiyi bir kez puanlar.

Anahtar, hakemin gördüğü HER ŞEYDİR: hakem kimliği · iki sistem istemi · mod · soru · hakeme giden
(kırpılmış) altın madde · altın atıf · cevap. Eksik alanlı anahtar farklı sınavları aynı kayda
düşürür (tuzak 2.17a); aynı girdi aynı anahtarı verir.

⚠️ Gürültü tabanında, kayma çıpasında ve tekrar ortalamasında KULLANILMAZ: orada amaç aynı girdiyi
yeniden puanlatmaktır. Bu yüzden `groundedness.py`'de varsayılan KAPALI.
"""
import fcntl
import hashlib
import json
import os
from datetime import datetime, timezone
from enum import Enum


class DepoModu(Enum):
    KULLAN = "kullan"
    KAPALI = "kapali"


def anahtar(hakem_kunye, istemler, mode, soru, kaynak_kirpilmis, gold, cevap):
    return hashlib.sha256(json.dumps([hakem_kunye, *istemler, mode, soru, kaynak_kirpilmis, gold,
                                      cevap], ensure_ascii=False).encode("utf-8")).hexdigest()


class SonucDeposu:
    """Bir hakem kimliğinin deposu: `<kok>/<model>__<sağlayıcı>__<düşünme>.jsonl`, yalnız ekleme.
    Satır = {anahtar, puan, kosu, tarih}; `puan` `score_record`'un tek koşuluk sonucu."""

    def __init__(self, kok, hakem_kunye):
        ad = "__".join(str(hakem_kunye[k]) for k in ("model", "saglayici", "dusunme"))
        self.yol = os.path.join(kok, ad.replace("/", "_") + ".jsonl")
        self._kayit = {}
        if os.path.exists(self.yol):
            with open(self.yol, encoding="utf-8") as f:
                for satir in f:
                    if satir.strip():
                        r = json.loads(satir)   # Why: yarım satır = bozuk depo; sessizce atlanmaz
                        self._kayit[r["anahtar"]] = r["puan"]

    def bul(self, k):
        return self._kayit.get(k)

    def ekle(self, k, puan, kosu):
        os.makedirs(os.path.dirname(self.yol), exist_ok=True)
        satir = json.dumps({"anahtar": k, "puan": puan, "kosu": kosu,
                            "tarih": datetime.now(timezone.utc).isoformat(timespec="seconds")},
                           ensure_ascii=False) + "\n"
        # Why: aynı depoya yazan paralel koşuların satırları birbirine karışmasın
        with open(self.yol, "a", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.write(satir)
            f.flush()
            fcntl.flock(f, fcntl.LOCK_UN)
        self._kayit[k] = puan
