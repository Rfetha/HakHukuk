"""`scripts/olcum_uretim/izle_kosu.py` — koşu izleyicinin saf çekirdeği.

Why: bu betik koşu SÜRERKEN okunuyor ve gördüğü sayılara göre koşu durdurulabiliyor
(kesiklik > %5 → ADR-0040 geçerlilik kapısı). Yanlış sayan bir izleyici, koşuyu boşuna
sürdürür ya da boşuna durdurur; ikisi de pahalı.
"""
import json

import pytest

from izle_kosu import alan, ozetle, oku


def _kayit(kid, durum="cevap", cevap="metin", sure=10.0, http=200):
    return {"id": kid, "soru": f"soru {kid}", "sunum": cevap,
            "durum": durum, "gecen_sn": sure, "http": http}


def test_alan_aday_listesini_sirayla_dener():
    assert alan({"sunum": "a", "metin": "b"}, "cevap") == "a"      # sunum önce
    assert alan({"metin": "b"}, "cevap") == "b"                    # sunum yoksa metin
    assert alan({"cevap": "c"}, "cevap") == "c"


def test_alan_bulunamayan_alani_UYDURMAZ():
    assert alan({"id": 1}, "durum") is None


def test_ozetle_ilerleme_ve_kalan_sureyi_hesaplar():
    o = ozetle([_kayit(i, sure=12.0) for i in range(20)], n=80)
    assert o["uretilen"] == 20 and o["yuzde"] == 25 and o["bitti"] is False
    assert o["ortalama_sn"] == 12.0
    assert o["kalan_dk"] == pytest.approx(60 * 12.0 / 60)          # 60 kalem × 12 sn


def test_ozetle_BOS_cevabi_yakalar():
    kayitlar = [_kayit(0), _kayit(1, cevap="   "), _kayit(2, cevap="")]
    assert ozetle(kayitlar, n=3)["bos"] == [1, 2]


def test_ozetle_http_hatasini_yakalar_ama_alan_yoksa_HATA_SAYMAZ():
    kayitlar = [_kayit(0), _kayit(1, http=500), {"id": 2, "sunum": "x"}]
    o = ozetle(kayitlar, n=3)
    assert o["http_hatali"] == [1]          # alanı olmayan kalem hatalı SAYILMAZ


def test_ozetle_durumlari_sayar():
    kayitlar = [_kayit(0), _kayit(1, durum="suskunluk"), _kayit(2, durum="kesik")]
    assert ozetle(kayitlar, n=3)["durumlar"] == {"cevap": 1, "suskunluk": 1, "kesik": 1}


def test_ozetle_hata_durumundaki_kalem_BOS_cevap_SAYILMAZ():
    """Bulgu: bir `hata` kalemi (ağ hatası, bkz. konteyner_urun_yolu_80.py::_sor) sunum/metin/
    cevap alanlarının HİÇBİRİNİ taşımaz — dışlanmazsa aynı kalem hem `💥 hata` hem `␀ BOŞ cevap`
    sayılır ve tam ADR-0080/§7.9'un canlı okunduğu yerde bir ağ kesintisi "ürün yolu bozuldu"
    gibi okunur."""
    kayitlar = [{"id": 5, "soru": "x", "durum": "hata", "http": None, "hata": "URLError: x"}]

    o = ozetle(kayitlar, n=1)

    assert o["bos"] == []
    assert o["durumlar"] == {"hata": 1}


def test_ozetle_bos_kosuda_patlamaz():
    o = ozetle([], n=80)
    assert o["uretilen"] == 0 and o["ortalama_sn"] == 0.0 and o["bitti"] is False


def test_oku_json_dizisi_ve_jsonl_ikisini_de_okur(tmp_path):
    kayitlar = [_kayit(0), _kayit(1)]
    dizi = tmp_path / "a.json"
    dizi.write_text(json.dumps(kayitlar), encoding="utf-8")
    satirli = tmp_path / "b.jsonl"
    satirli.write_text("\n".join(json.dumps(k) for k in kayitlar), encoding="utf-8")
    assert oku(str(dizi)) == kayitlar == oku(str(satirli))


def test_oku_YARIM_yazilan_dosyada_patlamaz(tmp_path):
    """Why: canlı izlerken üretici dosyayı yazıyor olabilir; patlamak izlemeyi öldürürdü."""
    yarim = tmp_path / "y.json"
    yarim.write_text('[{"id": 0, "soru": "x"', encoding="utf-8")
    assert oku(str(yarim)) == []

    yarim_satir = tmp_path / "y.jsonl"
    yarim_satir.write_text(json.dumps(_kayit(0)) + "\n{\"id\": 1, \"so", encoding="utf-8")
    assert [k["id"] for k in oku(str(yarim_satir))] == [0]      # tam satır okunur


def test_oku_olmayan_dosyada_bos_doner(tmp_path):
    assert oku(str(tmp_path / "yok.json")) == []
