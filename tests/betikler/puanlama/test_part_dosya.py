"""F0.5 (c) — üretici `.part` adıyla yazar, iş bitince yeniden adlandırır; puanlama `.part` okumaz.

Tuzak 5.10'un üretici tarafındaki karşılığı: yarım kalan bir üretim geçerli JSONL'dir, yalnız
EKSİKTİR — adı tamamlanmış dosyanınkiyle aynıysa ayırt edilemez.
"""
import ast
import json
import os

import pytest

from part_dosya import TamamlanmamisDosya, part_ile_yaz, tamamlanmis_jsonl  # noqa: E402


def test_part_ile_yaz_basarili_bitiste_yeniden_adlandirir(tmp_path):
    hedef = tmp_path / "x_detail.jsonl"
    with part_ile_yaz(str(hedef)) as f:
        f.write('{"id": 0}\n')
        assert (tmp_path / "x_detail.jsonl.part").exists()
        assert not hedef.exists()
    assert hedef.read_text() == '{"id": 0}\n'
    assert not (tmp_path / "x_detail.jsonl.part").exists()


def test_part_ile_yaz_yarida_kesilince_part_kalir(tmp_path):
    hedef = tmp_path / "x_detail.jsonl"
    with pytest.raises(KeyboardInterrupt):
        with part_ile_yaz(str(hedef)) as f:
            f.write('{"id": 0}\n')
            raise KeyboardInterrupt
    assert not hedef.exists()
    assert (tmp_path / "x_detail.jsonl.part").read_text() == '{"id": 0}\n'


def test_part_ile_yaz_eski_tam_dosyayi_yarida_kesilmede_ezmez(tmp_path):
    hedef = tmp_path / "x_detail.jsonl"
    hedef.write_text('{"id": "eski"}\n')
    with pytest.raises(RuntimeError):
        with part_ile_yaz(str(hedef)) as f:
            f.write('{"id": "yeni"}\n')
            raise RuntimeError("koşu öldü")
    assert hedef.read_text() == '{"id": "eski"}\n'


def test_tamamlanmis_jsonl_part_dosyasini_okumaz(tmp_path):
    p = tmp_path / "x_detail.jsonl.part"
    p.write_text(json.dumps({"id": 0}) + "\n")
    with pytest.raises(TamamlanmamisDosya):
        tamamlanmis_jsonl(str(p))


def test_tamamlanmis_jsonl_tam_dosyayi_okur(tmp_path):
    p = tmp_path / "x_detail.jsonl"
    p.write_text('{"id": 0}\n\n{"id": 1}\n')
    assert tamamlanmis_jsonl(str(p)) == [{"id": 0}, {"id": 1}]


# ── üreticiler ve okuyucular bağlı mı (kod ağacından, metin aramasıyla değil) ─────────────
_KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
_URETICILER = {
    "scripts/olcum_uretim/uretim/gen_eval_grounded.py": 1,   # *_detail.jsonl
    "scripts/puanlama/skorlayici/groundedness.py": 2,            # gnd_*.jsonl + özet
    "scripts/puanlama/skorlayici/score_abstention.py": 2,        # abst_*.jsonl + özet
}


def _cagrilar(yol, ad):
    agac = ast.parse(open(os.path.join(_KOK, yol), encoding="utf-8").read())
    return [n for n in ast.walk(agac) if isinstance(n, ast.Call)
            and (getattr(n.func, "id", None) == ad or getattr(n.func, "attr", None) == ad)]


def _yazma_kipli_open(yol):
    """`open(x, "w")` çağrıları (önbellek gibi kendi geçici+replace düzeni olanlar hariç)."""
    return [n for n in _cagrilar(yol, "open")
            if len(n.args) >= 2 and isinstance(n.args[1], ast.Constant) and n.args[1].value == "w"
            and not (isinstance(n.args[0], ast.Name) and n.args[0].id == "gecici")]


@pytest.mark.parametrize("yol,beklenen", sorted(_URETICILER.items()))
def test_uretici_ciktisini_part_ile_yazar(yol, beklenen):
    assert len(_cagrilar(yol, "part_ile_yaz")) >= beklenen
    assert _yazma_kipli_open(yol) == [], [ast.unparse(n) for n in _yazma_kipli_open(yol)]


@pytest.mark.parametrize("yol", ["scripts/puanlama/skorlayici/groundedness.py",
                                 "scripts/puanlama/skorlayici/score_abstention.py",
                                 "scripts/puanlama/tablo/harness_tablo.py",
                                 "scripts/puanlama/tablo/uc_okuma_kutle.py"])
def test_puanlayici_girdisini_tamamlanmis_jsonl_ile_okur(yol):
    assert _cagrilar(yol, "tamamlanmis_jsonl")
