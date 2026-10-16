"""F0.9 — kayıp maskesi kapısı: `train_on_responses_only`ın ürettiği `labels` doğru yeri mi örtüyor.

Sahte tokenizer'la kapının kurallarını sınar. Gerçek tokenizer ve Unsloth'un kendi maskeleme
fonksiyonuyla iki modelde yapılan döküm kronolojide (#78); kapı her eğitimde de çalışır.
"""
import json
import os
from argparse import Namespace

import pytest

import ortam_kilidi as ok  # noqa: E402

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
U, A = "<u>", "<a>"
SOZLUK = {1: U, 2: "soru", 3: A, 4: "cevap", 5: "<son>"}


class _Tokenizer:
    def decode(self, ids):
        return "".join(SOZLUK[i] for i in ids)


def _bloklar(labels, ids=(1, 2, 3, 4, 5)):
    return ok.maske_bloklari(list(ids), labels, _Tokenizer())


def test_maske_bloklari_ardisik_bloklari_birlestirir():
    assert _bloklar([-100, -100, -100, 4, 5]) == [(False, "<u>soru<a>"), (True, "cevap<son>")]


def test_maske_ihlalleri_dogru_maskede_bos():
    assert ok.maske_ihlalleri(_bloklar([-100, -100, -100, 4, 5]), U, A) == []


@pytest.mark.parametrize("labels,parca", [
    ([-100] * 5, "kayıp alan token yok"),
    ([1, 2, 3, 4, 5], "bütün tokenlar"),
    ([-100, -100, 3, 4, 5], "asistan işaretinden hemen sonra"),   # işaretin kendisi kayıp alıyor
    ([-100, 2, 3, 4, 5], "asistan işaretinden hemen sonra"),
])
def test_maske_ihlalleri_bozuk_maskeyi_yakalar(labels, parca):
    ihlal = ok.maske_ihlalleri(_bloklar(labels), U, A)
    assert any(parca in i for i in ihlal), ihlal


def test_maske_ihlalleri_kullanici_turu_sizmasini_yakalar():
    # iki tur: ikinci kullanıcı turu kayıp alan bloğa sızmış
    ids = (1, 2, 3, 4, 1, 2, 3, 4)
    labels = [-100, -100, -100, 4, 1, 2, 3, 4]
    ihlal = ok.maske_ihlalleri(_bloklar(labels, ids), U, A)
    assert any("kullanıcı turu" in i for i in ihlal), ihlal


def _kapi(tmp_path, labels):
    (tmp_path / "KUNYE.json").write_text('{"durum": "basladi"}', encoding="utf-8")
    veri = [{"input_ids": [1, 2, 3, 4, 5], "labels": labels}] * 3
    args = Namespace(user_part=U, assistant_part=A)
    ok.maske_kapisi(veri, _Tokenizer(), args, str(tmp_path))


def test_maske_kapisi_dokumu_ve_kunyeyi_yazar(tmp_path):
    _kapi(tmp_path, [-100, -100, -100, 4, 5])
    assert (tmp_path / "maske_ornegi.txt").read_text(encoding="utf-8") == "<u>soru<a>⟦cevap<son>⟧"
    m = json.loads((tmp_path / "KUNYE.json").read_text(encoding="utf-8"))["maske"]
    assert m == {"ornek_token": 5, "ornek_kayipli_token": 2, "satir_maske_sonrasi": 3}


def test_maske_kapisi_bozuk_maskede_durur_ama_dokumu_birakir(tmp_path):
    with pytest.raises(SystemExit):
        _kapi(tmp_path, [-100] * 5)
    assert (tmp_path / "maske_ornegi.txt").exists()


def test_train_sft_kapiyi_maskelemeden_sonra_egitimden_once_cagirir():
    import ast
    agac = ast.parse(open(os.path.join(KOK, "scripts/egitim/kosu/train_sft.py"), encoding="utf-8").read())
    main = next(n for n in agac.body if isinstance(n, ast.FunctionDef) and n.name == "main")

    def satir(ad):
        return min(n.lineno for n in ast.walk(main) if isinstance(n, ast.Call)
                   and (getattr(n.func, "id", None) == ad or getattr(n.func, "attr", None) == ad))
    assert satir("train_on_responses_only") < satir("maske_kapisi") < satir("train")
