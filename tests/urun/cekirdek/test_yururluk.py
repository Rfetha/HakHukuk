"""Yürürlük kapısı (plan Görev 8b).

⚠️ Neden bu bir KAPI: `mulga` bayrağı korpusta 2026-08 tarihinden beri VAR (2.547 madde)
ama `retriever.py` onu HİÇ okumuyordu — ölçüldü 2026-09-07: gerçek koşuda 800 getirilen
kaynağın 2'si yürürlükten kalkmış maddeydi ve vatandaşa gidiyordu. Bu eksik özellik değil,
YANLIŞ CEVAPtır.
"""
import json
import os

import numpy as np
import pytest

from hakhukuk.cekirdek.tipler import Yururluk

RETRIEVER = pytest.importorskip("hakhukuk.cekirdek.getirici")

KORPUS_KUNYE = "data/corpus/KUNYE.json"


def _sahte_retriever():
    """Üç kayıtlı oyuncak indeks — biri mülga. Gerçek gömme modeli yüklenmez."""
    kayitlar = [
        {"kanun_no": "4857", "kanun_adi": "İŞ KANUNU", "madde_no": "Madde 31",
         "text": "askerlik sebebiyle sözleşme askıya alınır", "mulga": False},
        {"kanun_no": "1475", "kanun_adi": "İŞ KANUNU (mülga)", "madde_no": "Madde 15",
         "text": "askerlik sebebiyle sözleşme askıya alınır", "mulga": True},
        {"kanun_no": "4721", "kanun_adi": "TÜRK MEDENİ KANUNU", "madde_no": "Madde 503",
         "text": "vesayet makamı", "mulga": False},
    ]
    gomme = np.eye(3, dtype=np.float32)
    kunye = {"model": "sahte", "rrf_k": 10}
    # Gömücü hep 2. kaydın (mülga) vektörünü döndürür ⇒ süzgeç yoksa o 1. sırada gelir.
    return RETRIEVER.Retriever(kayitlar, gomme, kunye,
                               gomucu=lambda m: np.array([[0.0, 1.0, 0.0]], dtype=np.float32))


def test_mulga_madde_varsayilan_olarak_GETIRILMEZ():
    sonuc = _sahte_retriever().getir("askerlik sözleşme askıya", k=3)
    assert sonuc, "hiç sonuç dönmedi"
    assert not any(r.get("mulga") for r in sonuc), \
        f"mülga madde vatandaşa gitti: {[r['kanun_no'] for r in sonuc if r.get('mulga')]}"


def test_mulga_ACIKCA_istenirse_getirilir():
    sonuc = _sahte_retriever().getir("askerlik sözleşme askıya", k=3,
                                     yururluk=Yururluk.MULGA_DAHIL)
    assert any(r.get("mulga") for r in sonuc), "MULGA_DAHIL istendi ama mülga madde gelmedi"


def test_getirilen_kaynak_mulga_alanini_TASIR():
    """Rozet gösterilebilmesi için alan sonuçta durmalı — sessizce düşürülmez."""
    for r in _sahte_retriever().getir("vesayet", k=3):
        assert "mulga" in r


def test_korpus_kunyesi_anlik_goruntu_tarihi_tasir():
    """"Bu korpus ne zamana göre günceldir" sorusu bugün CEVAPLANAMIYOR."""
    assert os.path.exists(KORPUS_KUNYE), f"{KORPUS_KUNYE} yok"
    k = json.load(open(KORPUS_KUNYE, encoding="utf-8"))
    for alan in ("anlik_goruntu_tarihi", "kaynak", "kapsam", "n_kanun", "n_madde",
                 "n_mulga", "sha256", "kapsam_disi"):
        assert alan in k, f"künyede {alan} yok"
    assert k["kapsam"] == "kanun"
    assert k["n_madde"] == 40496
    assert k["n_mulga"] == 2547
    assert "yönetmelik" in k["kapsam_disi"], "ne KAPSAMADIĞI açıkça yazılmalı"
