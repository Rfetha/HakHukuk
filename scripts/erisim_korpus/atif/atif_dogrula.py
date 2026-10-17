#!/usr/bin/env python3
"""Atıf doğrulama komut satırı.

Modül 2026-10-17'de pakete taşındı (`hakhukuk/cekirdek/atif_dogrula.py`, kusur 11): ürün ve ölçüm hattı aynı kodu
oradan içe aktarır. Bu dosya yalnız eski komut satırı yolunu korur; içe aktarılmaz.

Kullanım:
  python scripts/erisim_korpus/atif/atif_dogrula.py --details outputs/eval/<koşu>/m1_<etiket>_detail.jsonl
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

from hakhukuk.cekirdek.atif_dogrula import main  # noqa: E402

if __name__ == "__main__":
    main()
