"""Kusur 33 (ADR-0083 §A) — `yeniden_uret.sh`'ın recall@10 geçerlilik kapısı.

Eski kapı `gold_retrieved`/`altin_getirildi` alanlarını okuyordu; bu alanlar detay
kayıtlarında hiç yok, kapı bu yüzden HER ZAMAN 0/n okuyup düşüyordu — çıpanın kendi
verisinde bile (f02). Gerçek şekil `harness.altin_sirasi` (0-tabanlı) + `harness.
altin_dusuruldu`. Bu dosya ağsız çalışır, sahte detay kayıtları kullanır.
"""
import pytest

from recall_kapisi import harness_siralari, recall_at_10


def _kayit(altin_sirasi=None, altin_dusuruldu=False, id_=0):
    return {"id": id_, "harness": {"k": 10, "altin_dusuruldu": altin_dusuruldu,
                                    "altin_sirasi": altin_sirasi, "getirilen": []}}


def test_recall_at_10_dogru_sekilli_veride_beklenen_orani_verir():
    # 76 kayıt altını ilk 10'da buluyor (sıra 0-8 arası), 4 kayıt hiç bulamıyor (None).
    satirlar = [_kayit(altin_sirasi=i % 9) for i in range(76)]
    satirlar += [_kayit(altin_sirasi=None) for _ in range(4)]
    assert recall_at_10(satirlar) == 0.95


def test_recall_at_10_altin_dusuruldu_olan_kalemi_saymiyor():
    satirlar = [_kayit(altin_sirasi=3, altin_dusuruldu=True)]
    assert recall_at_10(satirlar) == 0.0


def test_recall_at_10_altin_sirasi_none_olani_saymiyor():
    satirlar = [_kayit(altin_sirasi=None)]
    assert recall_at_10(satirlar) == 0.0


def test_recall_at_10_k_disindaki_sirayi_saymiyor():
    satirlar = [_kayit(altin_sirasi=10)]  # k=10 ⇒ sıra 0..9 içeride, 10 dışarıda
    assert recall_at_10(satirlar) == 0.0


def test_recall_at_10_harness_alani_eksikse_gurultulu_patliyor():
    satirlar = [{"id": 0}]
    with pytest.raises(KeyError, match="harness"):
        recall_at_10(satirlar)


def test_harness_siralari_f02_ankor_uzerinde_dogru_sayiyi_uretir():
    """Kalibrasyon: çıpanın kendi verisinde 76/80 = 0,9500 çıkmalı (görev tanımında
    doğrulandı — bu test onu tekrar üretir, ağ/dosya OKUMADAN, aynı dağılımla)."""
    # 76 bulunan (0-8 arası sıra) + 4 bulunamayan (None) — f02'nin gerçek dağılımı.
    satirlar = [_kayit(altin_sirasi=i % 9) for i in range(76)] + \
               [_kayit(altin_sirasi=None) for _ in range(4)]
    siralar = harness_siralari(satirlar)
    assert siralar.count(None) == 4
    assert recall_at_10(satirlar) == 0.95
