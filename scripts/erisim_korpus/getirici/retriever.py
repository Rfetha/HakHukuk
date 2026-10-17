#!/usr/bin/env python3
"""Getirici komut satırı (`kur` · `sorgu`).

Modül 2026-10-17'de pakete taşındı (`hakhukuk/cekirdek/getirici.py`, kusur 11): ürün ve ölçüm hattı aynı kodu
oradan içe aktarır. Bu dosya yalnız eski komut satırı yolunu korur; içe aktarılmaz.

Kullanım:
  python scripts/erisim_korpus/getirici/retriever.py kur   --korpus data/corpus/mevzuat_maddeler.jsonl \\
                                    --indeks data/index/mevzuat_bge_m3 --cihaz cuda
  python scripts/erisim_korpus/getirici/retriever.py sorgu --indeks data/index/mevzuat_bge_m3 \\
                                    --soru "İşe iade davası ne zaman açılır?" -k 5
"""
# ── scripts/ yol köprüsü (T5 2026-09-07 · ADR-0112 2026-10-16) ───────────────
# Kardeş modüller iç içe alt klasörlerde de bulunsun diye scripts/ kökü, altındaki HER
# derinlikteki klasör ve repo kökü sys.path'e girer. Uzantısız `import X` bu köprü olmadan
# taşımada SESSİZCE kırılır: ImportError çalışma zamanında, bazen GPU koşusunun ortasında.
# ⚠️ 39 dosyada BİREBİR aynı; değiştirirsen hepsinde değiştir (grep: "yol köprüsü").
import os, sys
_K = os.path.abspath(__file__)
_K = _K[:_K.rindex(os.sep + "scripts" + os.sep)] + os.sep + "scripts"  # dışarıda: ValueError
_Y = []
for _y, _alt, _f in os.walk(_K):
    _alt[:] = sorted(_a for _a in _alt if _a[0] not in "_.")
    _Y.append(_y)
sys.path[:0] = [*_Y, os.path.dirname(_K)]
# ─────────────────────────────────────────────────────────────────────────────

from hakhukuk.cekirdek.getirici import main  # noqa: E402

if __name__ == "__main__":
    main()
