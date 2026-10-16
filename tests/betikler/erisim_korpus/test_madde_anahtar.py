from madde_anahtar import madde_anahtari


def test_madde_anahtari_buyuk_kucuk_harf_ayirt_etmez():
    assert madde_anahtari("5271", "Madde 161") == madde_anahtari("5271", "MADDE 161")


def test_madde_anahtari_gecici_maddeyi_normalden_ayirir():
    # ⚠️ Bu testin sebebi: ilk taslak ikisini AYNI saydı ve korpusta
    # 40.496 madde → 27.706 anahtara düştü (3.598 çakışma maskelendi).
    assert madde_anahtari("634", "Geçici Madde 1") != madde_anahtari("634", "Madde 1")


def test_madde_anahtari_harfli_numarayi_korur():
    assert madde_anahtari("5271", "Madde 12/A")[2] == "12/A"


def test_korpus_indeksi_dev_altinlarinin_tamamini_bagliyor():
    import json
    from madde_anahtar import korpus_indeksi
    idx = korpus_indeksi("data/corpus/mevzuat_maddeler.jsonl")
    dev = [json.loads(l) for l in open("data/eval/dev/core_hard.jsonl", encoding="utf-8") if l.strip()]
    baglanan = sum(1 for d in dev if madde_anahtari(d["kanun_no"], d["madde_no"]) in idx)
    assert baglanan == len(dev), f"{len(dev) - baglanan} altın etiket korpusa bağlanamadı"
