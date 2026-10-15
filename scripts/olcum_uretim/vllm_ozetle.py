#!/usr/bin/env python3
"""vLLM pilotu: dosyalardan kapı girdisini toplar, G1-G5'i değerlendirir, OZET.json yazar.

Beklenen dosya düzeni (`modal volume get` ve `kos.sh` sonrası):
  <kok>/A10/<ağırlık>/KUNYE.json, h1_tgta_v1_vllm_<ağırlık>_t{1,2}_detail.jsonl
  <kok>/kontrol-bf16-orijinal/KUNYE.json
  <kok>/puanlama/harness_tablo_<ağırlık>_t{1,2,3}.json
  referans: outputs/eval/f0/f06-hakem-gecisi/OZET.json (DeepSeek-açık, A10 referansı, 5 tekrar)
"""
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
import argparse  # noqa: E402
import json  # noqa: E402

import makine_kapisi  # noqa: E402
import vllm_kapilari as vk  # noqa: E402
from part_dosya import tamamlanmis_jsonl  # noqa: E402

KOK = "outputs/eval/f0/f016-vllm-pilot"
REFERANS_OZET = "outputs/eval/f0/f06-hakem-gecisi/OZET.json"
HAKEM_TEKRARI = 3


def _json(yol: str):
    with open(yol, encoding="utf-8") as f:
        return json.load(f)


def _kutle_ort(kok: str, ad: str) -> float:
    d = [_json(f"{kok}/puanlama/harness_tablo_{ad}_t{r}.json")["kutle_ekseni"]["kutle_tum"]
         for r in range(1, HAKEM_TEKRARI + 1)]
    return sum(d) / len(d)


def girdi_olustur(kok: str = KOK, referans_ozet: str = REFERANS_OZET) -> dict:
    girdi = {}
    for ad in vk.AGIRLIKLAR:
        kunye = _json(f"{kok}/A10/{ad}/KUNYE.json")
        t1 = tamamlanmis_jsonl(f"{kok}/A10/{ad}/h1_tgta_v1_vllm_{ad}_t1_detail.jsonl")
        t2 = tamamlanmis_jsonl(f"{kok}/A10/{ad}/h1_tgta_v1_vllm_{ad}_t2_detail.jsonl")
        girdi[ad.replace("-", "_")] = {
            "kosular": [{"sure_s": k["sure_s"], "gecerlilik": k["gecerlilik"]} for k in kunye["kosular"]],
            "kutle_ort": _kutle_ort(kok, ad),
            "iki_toplu_kosu_ayni": makine_kapisi.karsilastir(t1, t2)["ayni"]}
    girdi["referans_kutle_ort"] = _json(referans_ozet)["modlar"]["ds-acik"]["kutle_ort"]
    girdi["sekiz_soru"] = {"ayni": _json(f"{kok}/kontrol-bf16-orijinal/KUNYE.json")["sekiz_soru"]["birebir_ayni_cevap"],
                           "n": 8}
    return girdi


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="vLLM pilotu kapı özeti")
    p.add_argument("--kok", default=KOK)
    p.add_argument("--referans-ozet", default=REFERANS_OZET)
    a = p.parse_args(argv)
    girdi = girdi_olustur(a.kok, a.referans_ozet)
    sonuc = vk.degerlendir(girdi)
    with open(f"{a.kok}/OZET.json", "w", encoding="utf-8") as f:
        json.dump({"girdi": girdi, "kapilar": sonuc}, f, ensure_ascii=False, indent=2)
    print(json.dumps(sonuc, ensure_ascii=False, indent=2))
    return 0 if sonuc["ilerle"] else 1


if __name__ == "__main__":
    sys.exit(main())
