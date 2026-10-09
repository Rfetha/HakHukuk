"""`scripts/hf_kart.py` kapı testleri.

⚠️ Varlık sebebi: HF kartı elle yazıldığında `MODEL_CARD.md`'den **iki kez ayrıştı**.
Bu testler ayrışmayı değil, üretimin doğruluğunu sınar.
"""
import pathlib
import re
import sys

KOK = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "scripts"))

import hf_kart  # noqa: E402

_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def test_on_bilgi_bastadir_ve_lisans_tasir():
    cikti = hf_kart.uret()
    assert cikti.startswith("---\n"), "YAML ön bilgisi en başta olmalı"
    assert "license: apache-2.0" in cikti.split("---")[1]


def test_goreli_baglanti_KALMAZ():
    """HF deposunda docs/ ve outputs/ yoktur; göreli bağlantı orada ölü bağlantıdır."""
    govde = hf_kart.uret().split("---\n", 2)[2].lstrip("\n")
    kalan = [h for h in _LINK.findall(govde)
             if not h.startswith(("http://", "https://", "mailto:", "#"))]
    assert not kalan, f"mutlaklaşmamış bağlantı: {kalan[:5]}"


def test_capa_baglantisi_BOZULMAZ():
    assert hf_kart.mutlaklastir("[x](#bolum)") == "[x](#bolum)"
    assert hf_kart.mutlaklastir("[x](https://a.b)") == "[x](https://a.b)"


def test_govde_MODEL_CARD_ile_aynidir():
    """Üretim yalnız ekler ve bağlantı çevirir; metni değiştirmez."""
    govde = hf_kart.uret().split("---\n", 2)[2].lstrip("\n")
    kaynak = hf_kart.KAYNAK.read_text(encoding="utf-8")
    assert govde.count("\n") == kaynak.count("\n")
    assert "HakHukuk-4B" in govde
