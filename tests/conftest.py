"""pytest yol kurulumu — TEK yerde.

⚠️ NEDEN VAR (T5, 2026-09-07): testler `scripts/`'i kendileri `sys.path`'e ekliyordu ve
**sekizi göreli yol** (`sys.path.insert(0, "scripts")`) kullanıyordu — yani `pytest` yalnız
repo kökünden koşulunca çalışıyordu. `scripts/` alt klasörlere bölününce ikisi birden kırılır:
göreli yol yanlış yeri gösterir, mutlak yol da artık kardeş modülleri içermez.

Kurulum `scripts/*.py` içindeki "yol köprüsü" bloğuyla AYNI mantığı kurar — ikisi ayrışırsa
testler üretimin görmediği bir yolu sınar. Değiştirirsen ikisini birlikte değiştir.
"""
import os
import sys

_KOK = os.path.dirname(os.path.abspath(__file__))          # tests/
_REPO = os.path.dirname(_KOK)
_SCRIPTS = os.path.join(_REPO, "scripts")

_YOLLAR = []
for _y, _alt, _ in os.walk(_SCRIPTS):   # her derinlik (ADR-0112: scripts/<grup>/<alt>/)
    _alt[:] = sorted(a for a in _alt if a[0] not in "_.")
    _YOLLAR.append(_y)
sys.path[:0] = [*_YOLLAR, _REPO]
