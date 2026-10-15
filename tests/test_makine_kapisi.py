"""F0.16 makine geçiş kapısı (ADR-0098 m.3): yeni makine referansın bütün cevaplarını birebir yeniden
üretmeden üretime girmez. Pilotun "birebir aynı cevap oranı" da aynı karşılaştırmadan gelir."""
import json

import pytest

import makine_kapisi as mk  # noqa: E402

SHA = "a" * 64


def _satirlar(n=80, sha=SHA):
    return [{"id": i, "cevap": f"cevap {i}", "harness": {"donmus_baglam": sha}} for i in range(n)]


def test_ayni_80_cevap_kapidan_gecer():
    s = mk.karsilastir(_satirlar(), _satirlar())
    assert (s["n"], s["ayni"], s["gecti"], s["farkli_id"]) == (80, 80, True, [])


def test_tek_cevabi_degistirilmis_referansta_kapi_duser():
    ref = _satirlar()
    ref[41]["cevap"] = "cevap 41."          # tek noktalama farkı da farktır
    s = mk.karsilastir(ref, _satirlar())
    assert (s["ayni"], s["gecti"], s["farkli_id"]) == (79, False, [41])


@pytest.mark.parametrize("bozma", ["eksik", "yinelenen"])
def test_eksik_ya_da_yinelenen_id_karsilastirmayi_durdurur(bozma):
    aday = _satirlar()
    if bozma == "eksik":
        aday.pop()
    else:
        aday[5] = dict(aday[4])
    with pytest.raises(SystemExit, match="id"):
        mk.karsilastir(_satirlar(), aday)


def test_farkli_donmus_baglamla_uretilmis_dosyalar_karsilastirilmaz():
    """Bağlam farklıysa cevap farkı makinenin değil girdinin farkıdır — sessizce sayılmaz."""
    with pytest.raises(SystemExit, match="donmus_baglam"):
        mk.karsilastir(_satirlar(), _satirlar(sha="b" * 64))


def test_komut_satiri_kapi_dustugunde_sifirdan_farkli_cikar(tmp_path):
    ref, aday = tmp_path / "ref.jsonl", tmp_path / "aday.jsonl"
    r = _satirlar()
    r[0]["cevap"] = "başka"
    ref.write_text("".join(json.dumps(x) + "\n" for x in r), encoding="utf-8")
    aday.write_text("".join(json.dumps(x) + "\n" for x in _satirlar()), encoding="utf-8")
    assert mk.main(["--referans", str(ref), "--aday", str(aday)]) == 1
    aday.write_text(ref.read_text(encoding="utf-8"), encoding="utf-8")
    assert mk.main(["--referans", str(ref), "--aday", str(aday)]) == 0
