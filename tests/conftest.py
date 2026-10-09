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

sys.path[:0] = [
    _SCRIPTS,
    *(os.path.join(_SCRIPTS, d) for d in sorted(os.listdir(_SCRIPTS))
      if os.path.isdir(os.path.join(_SCRIPTS, d)) and d[0] not in "_."),
    _REPO,
]
