#!/usr/bin/env python3
"""Hasat kapısı (spec 2026-10-15 bölüm 6; kullanıcı kararı 2026-10-16): llama.cpp Q4_K_M'in yanlış yaptığı kalemlerin
ne kadarı vLLM'de, aynı Q4 ağırlığıyla (Q4'ten açılmış) da yanlış?

Hasat (hard-negative üretimi) vLLM'e taşınırsa negatifler vLLM'de üretilmiş cevapların hatalarıdır; ADR-0047 negatiflerin
gönderdiğimiz modelin (llama.cpp Q4_K_M) hataları olmasını gerekçe yapmıştı. "Yanlış" = tekrar ortalaması `faithfulness` < esik (varsayılan 0,5);
puansız kalem (sıfır iddia, çekinme) sayılmaz. Eşik değeri (örtüşme oranı için geçme çizgisi) ölçümden önce plana yazılır.

Kullanım:
  python scripts/olcum_uretim/hasat_ortusme.py \\
      --q4 outputs/eval/f0/f06-hakem-gecisi/gnd_ds-acik_t{1,2,3,4,5}.jsonl \\
      --vllm outputs/eval/f0/f016-vllm-pilot/puanlama/gnd_vllm-q4-acilmis_t{1,2,3}.jsonl
"""
import argparse
import json


def yanlis_kalemler(gnd_tekrarlari: list[list[dict]], esik: float = 0.5) -> set[int]:
    toplam: dict[int, list[float]] = {}
    for tekrar in gnd_tekrarlari:
        for r in tekrar:
            if r.get("faithfulness") is not None:
                toplam.setdefault(r["id"], []).append(r["faithfulness"])
    return {i for i, v in toplam.items() if sum(v) / len(v) < esik}


def ortusme(q4: set[int], vllm: set[int]) -> dict:
    ortak = q4 & vllm
    return {"q4_yanlis": len(q4), "vllm_yanlis": len(vllm), "ortak": len(ortak),
            "oran": len(ortak) / len(q4) if q4 else None}


def _oku(yollar: list[str]) -> list[list[dict]]:
    return [[json.loads(l) for l in open(y, encoding="utf-8") if l.strip()] for y in yollar]


def main(argv=None):
    p = argparse.ArgumentParser(description="hasat kapısı: Q4 hataları vLLM'de (Q4 ağırlığı) da var mı")
    p.add_argument("--q4", nargs="+", required=True)
    p.add_argument("--vllm", nargs="+", required=True)
    p.add_argument("--esik", type=float, default=0.5)
    a = p.parse_args(argv)
    s = ortusme(yanlis_kalemler(_oku(a.q4), a.esik), yanlis_kalemler(_oku(a.vllm), a.esik))
    print(json.dumps(s, ensure_ascii=False))


if __name__ == "__main__":
    main()
