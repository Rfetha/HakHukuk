"""Toplu üretim sürücüsü (vLLM pilotu): sorular aynı anda gider, kayıt biçimi sıralı üretimle aynı kalır,
vLLM'in düşünce alanı adı farklı gelse de zorla kapatma çalışır, şablon GGUF'takiyle aynıdır.
Ağ yok, GPU yok; istemci sahtedir."""
import hashlib
import json
import os
import threading
import time
from types import SimpleNamespace

import pytest

import toplu_uret as tu  # noqa: E402

_KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFERANS = os.path.join(_KOK, "outputs", "eval", "f0", "f016-pilot", "A10", "m1",
                        "h1_tgta_v1_A10_m1_t1_detail.jsonl")
TOKENIZER = os.path.join(_KOK, "models", "merged", "tgta_v1")
GGUF = os.path.join(_KOK, "models", "gguf", "tgta_v1-q4_k_m.gguf")


def _kalem(i):
    return {"sira": i, "soru": f"soru {i}", "referans": f"madde {i}", "kanun_adi": "K", "madde_no": f"{i}",
            "kanun_no": "1", "sources_block": f"KAYNAK {i}",
            "harness": {"altin_sirasi": 0, "donmus_baglam": "a" * 64}}


def _cevap(icerik, dusunce=None, alan="reasoning_content", bitis="stop"):
    mesaj = SimpleNamespace(content=icerik)
    if dusunce is not None:
        setattr(mesaj, alan, dusunce)
    return SimpleNamespace(choices=[SimpleNamespace(finish_reason=bitis, message=mesaj)],
                           usage=SimpleNamespace(completion_tokens=7, completion_tokens_details=None))


class SahteIstemci:
    """chat → ilk geçiş; completions → zorunlu kapatmadan sonraki ikinci geçiş."""

    def __init__(self, chat, completions=None, bekle=0.0):
        self._chat, self._comp, self._bekle = chat, completions, bekle
        self._kilit, self.icerde, self.en_cok = threading.Lock(), 0, 0
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._chat_create))
        self.completions = SimpleNamespace(create=self._comp_create)

    def _chat_create(self, **kw):
        with self._kilit:
            self.icerde += 1
            self.en_cok = max(self.en_cok, self.icerde)
        time.sleep(self._bekle)
        with self._kilit:
            self.icerde -= 1
        return self._chat(kw)

    def _comp_create(self, **kw):
        return self._comp(kw)


def _sablon(mesajlar, dusunme):
    return "ISTEM"


def test_sonuclar_istek_sirasina_degil_kalem_sirasina_gore_yazilir():
    # Geç gelen cevap erken kalemin cevabı olsa bile kayıt id sırasında kalır.
    def chat(kw):
        n = int(kw["messages"][1]["content"].split("SORU: soru ")[1])
        time.sleep(0.05 * (4 - n))
        return _cevap(f"cevap {n}")
    kayitlar, _ = tu.uret(SahteIstemci(chat), "m", [_kalem(i) for i in range(4)], es_zamanli=4, sablon=_sablon)
    assert [k["id"] for k in kayitlar] == [0, 1, 2, 3]
    assert [k["cevap"] for k in kayitlar] == [f"cevap {i}" for i in range(4)]


def test_istekler_gercekten_ayni_anda_gider_ve_sinira_uyar():
    ist = SahteIstemci(lambda kw: _cevap("c"), bekle=0.05)
    tu.uret(ist, "m", [_kalem(i) for i in range(8)], es_zamanli=3, sablon=_sablon)
    assert 1 < ist.en_cok <= 3


@pytest.mark.skipif(not os.path.exists(REFERANS), reason="pilot referans cevap dosyası yok")
def test_kayit_alanlari_siralı_uretimin_referans_dosyasiyla_ayni():
    beklenen = list(json.loads(open(REFERANS, encoding="utf-8").readline()).keys())
    kayitlar, _ = tu.uret(SahteIstemci(lambda kw: _cevap("c")), "m", [_kalem(0)], es_zamanli=1, sablon=_sablon)
    assert list(kayitlar[0].keys()) == beklenen


def test_bos_cevap_sessiz_gecmez_kosuyu_durdurur():
    with pytest.raises(SystemExit, match="BOŞ cevap"):
        tu.uret(SahteIstemci(lambda kw: _cevap("")), "m", [_kalem(0)], es_zamanli=1, sablon=_sablon)


def test_vllm_reasoning_alanini_reasoning_content_gibi_okur_ve_zorla_kapatir():
    # Düşünce `reasoning` adıyla gelir, `content` boş: bütçe dolmuş → ikinci geçiş devreye girmeli.
    chat = lambda kw: _cevap(None, dusunce="uzun düşünce", alan="reasoning", bitis="length")
    comp = lambda kw: SimpleNamespace(choices=[SimpleNamespace(text=" nihai cevap ", finish_reason="stop")],
                                      usage=SimpleNamespace(completion_tokens=5))
    kayitlar, _ = tu.uret(SahteIstemci(chat, comp), "m", [_kalem(0)], es_zamanli=1, sablon=_sablon)
    k = kayitlar[0]
    assert (k["cevap"], k["forced_close"], k["reasoning_len"]) == ("nihai cevap", True, len("uzun düşünce"))


@pytest.mark.skipif(not os.path.isdir(TOKENIZER), reason="yerel tokenizer klasörü yok (models/ git dışı)")
def test_yerel_sablon_dusunme_acikken_think_acik_birakir():
    sablon = tu.yerel_sablon(TOKENIZER)
    istem = sablon([{"role": "system", "content": "S"}, {"role": "user", "content": "U"}], "on")
    assert istem.startswith("<|im_start|>system\nS<|im_end|>\n<|im_start|>user\nU<|im_end|>\n")
    assert istem.endswith("<|im_start|>assistant\n<think>\n")


@pytest.mark.skipif(not (os.path.isdir(TOKENIZER) and os.path.exists(GGUF)), reason="yerel model dosyaları yok")
def test_tokenizer_sablonu_gguf_icindekiyle_bayt_bayt_ayni():
    gguf = pytest.importorskip("gguf")
    f = gguf.GGUFReader(GGUF).fields["tokenizer.chat_template"]
    gguf_sablon = bytes(f.parts[f.data[0]]).decode("utf-8")
    yerel = open(os.path.join(TOKENIZER, "chat_template.jinja"), encoding="utf-8").read()
    assert hashlib.sha256(gguf_sablon.encode()).hexdigest() == hashlib.sha256(yerel.encode()).hexdigest()


@pytest.mark.skipif(not os.path.isdir(TOKENIZER), reason="yerel tokenizer klasörü yok (models/ git dışı)")
def test_metin_yapilandirmasi_gorsel_kismi_atar_metin_alanlarini_yukari_alir():
    # GGUF yalnız metin ağırlıklarını taşır; vLLM'e görüntü kulesiyle birlikte yapılandırma verilirse yük uyuşmaz.
    tam = json.load(open(os.path.join(TOKENIZER, "config.json"), encoding="utf-8"))
    m = tu.metin_yapilandirmasi(tam)
    assert m["architectures"] == ["Qwen3_5ForCausalLM"] and m["model_type"] == "qwen3_5_text"
    assert "vision_config" not in m and "text_config" not in m
    for alan in ("hidden_size", "num_hidden_layers", "layer_types", "vocab_size", "tie_word_embeddings"):
        assert m[alan] == tam["text_config"][alan]
