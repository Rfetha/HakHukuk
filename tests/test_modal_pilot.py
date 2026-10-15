"""F0.16 pilotunun Modal yapıştırıcısı — statik kurallar (ağ yok, Modal'a bağlanılmaz)."""
import ast
import os

import yaml

_KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_YOL = os.path.join(_KOK, "scripts", "olcum_uretim", "modal_pilot.py")


def _agac():
    return ast.parse(open(_YOL, encoding="utf-8").read())


def _sabit(ad):
    return next(ast.literal_eval(n.value) for n in _agac().body
                if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", None) == ad)


def test_pilot_sunucu_imaji_compose_ile_ayni():
    """ADR-0097 m.2 / ADR-0102 m.1: kiralık kartta ürünün konteyner imajı koşar; compose'daki sürüm
    değişirse pilot sessizce eski sürümde kalmasın."""
    compose = yaml.safe_load(open(os.path.join(_KOK, "docker", "compose.yaml"), encoding="utf-8"))
    assert _sabit("SUNUCU_IMAJI") == compose["services"]["llama"]["image"]


def test_pilot_konteynerine_anahtar_gitmez():
    """GGUF deposu herkese açık; hakem ve HF anahtarları kiralık makineye gönderilmez."""
    for n in ast.walk(_agac()):
        if isinstance(n, ast.Call) and getattr(n.func, "attr", None) == "function":
            assert all(k.arg != "secrets" for k in n.keywords)
    assert "Secret" not in open(_YOL, encoding="utf-8").read()
