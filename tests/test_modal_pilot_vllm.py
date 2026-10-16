"""F0.16 vLLM pilotunun Modal yapıştırıcısı — statik kurallar (ağ yok, Modal'a bağlanılmaz)."""
import ast
import os
import re

_KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_YOL = os.path.join(_KOK, "scripts", "olcum_uretim", "modal_pilot_vllm.py")


def _kaynak():
    return open(_YOL, encoding="utf-8").read()


def _sabit(ad):
    return next(ast.literal_eval(n.value) for n in ast.parse(_kaynak()).body
                if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", None) == ad)


def test_vllm_surumu_tam_sabit_taban_imaj_surumlu():
    """Sürüm kayarsa ölçülen şey değişir: `latest` ve aralık yasak."""
    assert re.fullmatch(r"\d+\.\d+\.\d+", _sabit("VLLM_SURUMU"))
    assert re.fullmatch(r"nvidia/cuda:\d+\.\d+\.\d+-devel-ubuntu\d+\.\d+", _sabit("TABAN_IMAJ"))


def test_vllm_pilot_konteynerine_anahtar_gitmez():
    assert "Secret" not in _kaynak()
    for n in ast.walk(ast.parse(_kaynak())):
        if isinstance(n, ast.Call) and getattr(n.func, "attr", None) == "function":
            assert all(k.arg != "secrets" for k in n.keywords)


def test_vllm_pilot_tokenizer_dosyalari_sablon_ve_yapilandirmayi_icerir():
    d = _sabit("TOKENIZER_DOSYALARI")
    assert {"chat_template.jinja", "config.json", "tokenizer.json"} <= set(d)


def test_vllm_pilot_rejim_tek_yerden_gelir():
    """Bütçe, seed ve kırpma bu dosyada tekrar yazılmaz; `olcum_karti.REJIM` ve `toplu_uret.py` taşır."""
    k = _kaynak()
    assert "1024" not in k.replace("1024 *", "") and "900" not in k and "max-new-tokens" not in k
    assert "olcum_karti" in k and "toplu_uret.py" in k


def test_vllm_pilot_dosyasi_derlenir():
    compile(_kaynak(), _YOL, "exec")


def test_vllm_pilotunun_hf_hub_sabiti_vllmin_alt_sinirini_karsilar():
    """İlk derleme bu yüzden düştü: llama pilotundan kopyalanan huggingface_hub==1.18.0, vLLM 0.30.0'ın
    istediği >=1.31.0 ile çakıştı (ResolutionImpossible)."""
    surum = tuple(int(x) for x in _sabit("HF_HUB_SURUMU").split("."))
    assert surum >= (1, 31, 0)


def test_vllm_pilotu_gguf_eklentisi_kullanmaz_cevrilmis_klasoru_sha_kapisindan_gecirir():
    """Eklenti Qwen3.5'i tanımıyordu (aşama A). Akış: GGUF → gguf_hf_cevir.py → vLLM; konteynerdeki çeviri,
    yerelde orijinalle doğrulanmış çevirinin tensör sha256'larıyla bire bir aynı olmalı."""
    k = _kaynak()
    assert "vllm-gguf-plugin" not in k and "vllm_gguf_plugin" not in k
    assert "gguf_hf_cevir.py" in k and "CEVIRI_KUNYE" in k


def test_vllm_pilotu_iki_agirlik_destekler_ve_batch_invariant_kullanmaz():
    """GDN katmanlarında batch-invariant desteklenmiyor (LMCache belgesi); pilot G4 ile belirlenimciliği ölçer,
    modu zorlamaz."""
    assert _sabit("AGIRLIKLAR") == ("q4-acilmis", "bf16-orijinal")
    assert "VLLM_BATCH_INVARIANT" not in _kaynak()


def test_vllm_pilotu_bf16_klasorunu_manifestle_dogrular():
    k = _kaynak()
    assert "bf16_manifest.json" in k and "bf16_yukle" in k
    assert _sabit("ES_ZAMANLI") == 32


def test_pilot_hata_verse_de_kunye_yazar():
    """Ücretli koşu yarıda kalırsa neden ve biten koşular kaybolmasın: künye `finally` içinde yazılır,
    hata nedeni `hata_sonu` alanına girer (inceleme bulgusu, 2026-10-16)."""
    kaynak = _kaynak()
    agac = ast.parse(kaynak)
    pilot = next(n for n in agac.body if isinstance(n, ast.FunctionDef) and n.name == "pilot")
    denemeler = [n for n in ast.walk(pilot) if isinstance(n, ast.Try)]
    assert any(isinstance(c, ast.Call) and getattr(c.func, "id", None) == "_yaz"
               for t in denemeler for s in t.finalbody for c in ast.walk(s))
    assert "hata_sonu" in ast.get_source_segment(kaynak, pilot)


def test_pilot_ek_uretim_kosulari_pilot_kanitinin_ustune_yazmaz():
    """Ek üretim koşuları (2026-10-16 gürültü ölçümü) ayrı tekrar numaraları ve ayrı klasör ekiyle koşar; varsayılan
    (1, 2) ve ek yok, yani pilotun kendi koşusu değişmeden yeniden üretilebilir."""
    agac = ast.parse(_kaynak())
    pilot = next(n for n in agac.body if isinstance(n, ast.FunctionDef) and n.name == "pilot")
    adlar = [a.arg for a in pilot.args.args]
    assert adlar[-2:] == ["tekrarlar", "dizin_eki"]
    assert [ast.literal_eval(d) for d in pilot.args.defaults[-2:]] == [(1, 2), ""]
    kaynak = ast.get_source_segment(_kaynak(), pilot)
    assert 'f"{CIKTI_KOK}/{tip}/{agirlik}{dizin_eki}"' in kaynak and "for t in tekrarlar:" in kaynak
    baslat = next(n for n in agac.body if isinstance(n, ast.FunctionDef) and n.name == "baslat")
    assert {"tekrarlar", "dizin_eki"} <= {a.arg for a in baslat.args.args}
