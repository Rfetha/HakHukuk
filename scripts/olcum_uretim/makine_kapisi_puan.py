#!/usr/bin/env python3
"""Makine geçiş kapısının puan düzeyi dalı (vLLM hattı; spec 2026-10-15 bölüm 5, G4 'puan').

vLLM'de aynı soru toplu gönderilince aynı cevabı vermeyebilir (Qwen3.5 GDN katmanlarında batch-invariant yok).
Bayt eşitliği yerine, yeni makinenin referans koşusuyla aynı hakemle puanlanmış kütle farkı gürültü bandının
içinde mi diye bakılır. Eşik G3 ile aynıdır (0,6 puan).

Kullanım:
  python scripts/olcum_uretim/makine_kapisi_puan.py --referans-kutle 0.7515 --aday-kutle 0.7540
  → çıkış kodu 0: kapı geçti · 1: düştü
"""
import argparse
import sys

ESIK_PUAN = 0.6


def puan_kapisi(referans_kutle_ort: float, aday_kutle_ort: float, esik_puan: float = ESIK_PUAN) -> dict:
    fark = round(abs(aday_kutle_ort - referans_kutle_ort) * 100, 6)
    return {"fark_puan": fark, "esik_puan": esik_puan, "gecti": fark <= esik_puan}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="makine kapısı, puan düzeyi")
    p.add_argument("--referans-kutle", type=float, required=True)
    p.add_argument("--aday-kutle", type=float, required=True)
    p.add_argument("--esik-puan", type=float, default=ESIK_PUAN)
    a = p.parse_args(argv)
    s = puan_kapisi(a.referans_kutle, a.aday_kutle, a.esik_puan)
    print(f"[makine-kapisi-puan] fark {s['fark_puan']:.3f} puan, eşik {s['esik_puan']} → "
          f"{'GEÇTİ' if s['gecti'] else 'DÜŞTÜ'}")
    return 0 if s["gecti"] else 1


if __name__ == "__main__":
    sys.exit(main())
