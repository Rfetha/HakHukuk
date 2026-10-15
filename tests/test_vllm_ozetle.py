"""vLLM pilotunun dosyalardan kapı girdisi toplayan yapıştırıcısı (ağ yok, GPU yok)."""
import json
import os

import vllm_kapilari as vk
import vllm_ozetle as vo  # noqa: E402

SHA = "a" * 64


def _yaz(yol, nesne):
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(nesne, f)


def _satirlar(yol, n=80, degisen=()):
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    with open(yol, "w", encoding="utf-8") as f:
        for i in range(n):
            f.write(json.dumps({"id": i, "cevap": f"c{i}" + ("x" if i in degisen else ""),
                                "harness": {"donmus_baglam": SHA}}) + "\n")


def _kur(tmp_path):
    kok = str(tmp_path / "pilot")
    g = {"n": 80, "kesik_orani": 0.0, "dusunen": 80}
    for ad, kutle, degisen in (("q4-acilmis", 0.7540, ()), ("bf16-orijinal", 0.7700, (3,))):
        _yaz(f"{kok}/A10/{ad}/KUNYE.json", {"kosular": [{"sure_s": 150.0, "gecerlilik": g},
                                                         {"sure_s": 152.0, "gecerlilik": g}]})
        _satirlar(f"{kok}/A10/{ad}/h1_tgta_v1_vllm_{ad}_t1_detail.jsonl")
        _satirlar(f"{kok}/A10/{ad}/h1_tgta_v1_vllm_{ad}_t2_detail.jsonl", degisen=degisen)
        for r in (1, 2, 3):
            _yaz(f"{kok}/puanlama/harness_tablo_{ad}_t{r}.json", {"kutle_ekseni": {"kutle_tum": kutle}})
    _yaz(f"{kok}/kontrol-bf16-orijinal/KUNYE.json", {"sekiz_soru": {"birebir_ayni_cevap": 8}})
    ref = str(tmp_path / "f06" / "OZET.json")
    _yaz(ref, {"modlar": {"ds-acik": {"kutle_ort": 0.7515}}})
    return kok, ref


def test_girdi_dosyalardan_toplanir_ve_kapilar_degerlendirilir(tmp_path):
    kok, ref = _kur(tmp_path)
    g = vo.girdi_olustur(kok, ref)
    assert g["referans_kutle_ort"] == 0.7515 and g["sekiz_soru"] == {"ayni": 8, "n": 8}
    assert g["q4_acilmis"]["kutle_ort"] == 0.7540 and g["q4_acilmis"]["iki_toplu_kosu_ayni"] == 80
    assert g["bf16_orijinal"]["iki_toplu_kosu_ayni"] == 79            # id 3'ün cevabı iki koşuda farklı
    assert vk.degerlendir(g)["ilerle"] is True


def test_main_ozet_json_yazar_ve_cikis_kodu_ilerlemeyi_yansitir(tmp_path):
    kok, ref = _kur(tmp_path)
    assert vo.main(["--kok", kok, "--referans-ozet", ref]) == 0
    assert json.load(open(f"{kok}/OZET.json", encoding="utf-8"))["kapilar"]["ilerle"] is True
    _yaz(f"{kok}/puanlama/harness_tablo_q4-acilmis_t1.json", {"kutle_ekseni": {"kutle_tum": 0.60}})
    assert vo.main(["--kok", kok, "--referans-ozet", ref]) == 1
