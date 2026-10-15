"""F0.9 — Gemma 4 E4B'nin ayrı eğitim kilidi: Qwen'inkinden yalnız bilinen alanlarda ayrılır.

Kilit dosyası, yaml, LoRA deseni, yerleşim kapısı ve Modal zinciri GPU'suz sınanır; Gemma'nın
gerçekten eğitilmesi deneme koşusunun (F0.9 smoke) işidir.
"""
import ast
import hashlib
import os
import re
from argparse import Namespace

import pytest
import yaml

import ortam_kilidi as ok  # noqa: E402
from test_egitim_ortami import _gozlem, _orpo_args, _sft_args  # noqa: E402

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODAL = os.path.join(KOK, "scripts/egitim/modal_train.py")


@pytest.fixture(scope="module")
def gemma():
    return ok.OrtamKilidi.yukle(os.path.join(KOK, "configs/egitim_ortami_gemma.yaml"))


@pytest.fixture(scope="module")
def qwen():
    return ok.OrtamKilidi.yukle(os.path.join(KOK, "configs/egitim_ortami.yaml"))


def _pinler(yol):
    return dict(l.strip().split("==", 1) for l in open(os.path.join(KOK, yol), encoding="utf-8") if "==" in l)


def test_gemma_kilit_dosyasinin_ozeti_yamldaki_ile_ayni(gemma):
    yol = os.path.join(KOK, gemma.veri["paketler"]["kilit_dosyasi"])
    assert hashlib.sha256(open(yol, "rb").read()).hexdigest() == gemma.veri["paketler"]["kilit_sha256"]


def test_gemma_kilit_dosyasi_qwenden_yalniz_unsloth_ikilisiyle_ayrilir(qwen, gemma):
    q, g = _pinler("requirements.lock.txt"), _pinler("requirements.gemma4.lock.txt")
    assert {p for p in {*q, *g} if q.get(p) != g.get(p)} == {"unsloth", "unsloth_zoo"}
    assert g["unsloth"] == g["unsloth_zoo"] == "2026.10.1"


def test_gemma_yamlindaki_surumler_kilit_dosyasiyla_ayni(gemma):
    pin = _pinler(gemma.veri["paketler"]["kilit_dosyasi"])
    for paket, surum in gemma.veri["paketler"]["surumler"].items():
        assert pin.get(paket) == surum, paket
    for paket in [*gemma.veri["paketler"]["ek"], *gemma.veri["paketler"]["yasak"]]:
        assert paket not in pin


def test_gemma_yamli_qwenden_yalniz_bilinen_alanlarda_ayrilir(qwen, gemma):
    q, g = qwen.veri, gemma.veri
    farkli = {k for k in {*q, *g} if q.get(k) != g.get(k)}
    assert farkli == {"model", "tur_isaretleri", "paketler", "lora", "yukleme"}
    assert q["tarifler"] == g["tarifler"] and q["seedler"] == g["seedler"]   # tek değişken: model
    assert q["lora"]["r"] == g["lora"]["r"] and q["lora"]["alpha"] == g["lora"]["alpha"]
    assert q["gpu"] == g["gpu"] and q["hassasiyet"] == g["hassasiyet"]


def test_gemma_modeli_ve_tur_isaretleri(gemma):
    assert gemma.veri["model"] == "google/gemma-4-E4B-it"
    assert gemma.veri["tur_isaretleri"] == {"user_part": "<|turn>user\n", "assistant_part": "<|turn>model\n"}
    assert gemma.veri["yukleme"] == {"use_exact_model_name": True}


# ── LoRA deseni ───────────────────────────────────────────────────────────────

def _desen(gemma):
    (d,) = gemma.veri["lora"]["hedef_moduller"]
    return d


@pytest.mark.parametrize("ad,eslesir", [
    ("model.language_model.layers.0.self_attn.q_proj", True),
    ("model.language_model.layers.41.mlp.down_proj", True),
    ("model.vision_tower.encoder.layers.3.self_attn.q_proj.linear", False),
    ("model.vision_tower.encoder.layers.3.self_attn.q_proj", False),
    ("model.audio_tower.layers.0.self_attn.q_proj", False),
    ("model.language_model.layers.5.per_layer_input_gate", False),
    ("model.language_model.layers.5.per_layer_projection", False),
    ("model.language_model.embed_tokens", False),
])
def test_gemma_lora_deseni_yalniz_dil_kulesini_secer(gemma, ad, eslesir):
    assert bool(re.fullmatch(_desen(gemma), ad)) is eslesir


def test_lora_hedefi_regexi_str_duz_listeyi_liste_dondurur(gemma):
    assert ok.lora_hedefi(gemma.veri["lora"]["hedef_moduller"]) == _desen(gemma)
    assert ok.lora_hedefi(["q_proj", "k_proj"]) == ["q_proj", "k_proj"]
    assert ok.lora_hedefi(["q_proj"]) == ["q_proj"]


def test_gemma_tarifi_dogru_argumanlarda_ihlal_yok(gemma):
    d = dict(model="google/gemma-4-E4B-it", target_modules=gemma.veri["lora"]["hedef_moduller"],
             user_part="<|turn>user\n", assistant_part="<|turn>model\n")
    assert ok.tarif_ihlalleri(gemma, "sft", _sft_args(**d)) == []
    assert ok.tarif_ihlalleri(gemma, "orpo", _orpo_args(**{k: v for k, v in d.items() if "part" not in k})) == []


def test_gemma_kilidine_qwen_modeli_ve_duz_liste_verilirse_durur(gemma):
    ihlal = ok.tarif_ihlalleri(gemma, "sft", _sft_args())
    assert any("model" in i for i in ihlal) and any("target_modules" in i for i in ihlal)


# ── ortam: fla yalnız kilidinde varsa denetlenir ──────────────────────────────

def _gemma_gozlem(**degis):
    s = {"torch": "2.10.0", "triton": "3.6.0", "transformers": "5.10.2", "peft": "0.19.1", "trl": "0.24.0",
         "unsloth": "2026.10.1", "unsloth_zoo": "2026.10.1", "accelerate": "1.13.0",
         "bitsandbytes": "0.49.2", "datasets": "4.3.0", "einops": "0.8.2", "causal-conv1d": None}
    return _gozlem(surumler=s, **degis)


def test_gemma_ortami_dogru_gozlemde_ihlal_yok(gemma):
    assert ok.ortam_ihlalleri(gemma, _gemma_gozlem()) == []


def test_gemma_ortaminda_qwen_unsloth_surumu_ihlaldir(gemma):
    g = _gemma_gozlem()
    g.surumler["unsloth"] = g.surumler["unsloth_zoo"] = "2026.6.1"
    assert sum("unsloth" in i for i in ok.ortam_ihlalleri(gemma, g)) == 2


def test_fla_hatasi_gemmada_denetlenmez_qwende_ihlaldir(qwen, gemma):
    assert ok.ortam_ihlalleri(gemma, _gemma_gozlem(fla_hatasi="ModuleNotFoundError")) == []
    assert any("fla" in i for i in ok.ortam_ihlalleri(qwen, _gozlem(fla_hatasi="ModuleNotFoundError")))


# ── yerleşim kapısı ───────────────────────────────────────────────────────────

YER = {"yol_oneki": "model.language_model.", "modul_sayisi": 3}


def test_yerlesim_dogru_takimda_ihlal_yok():
    assert ok.yerlesim_ihlalleri([f"model.language_model.layers.{i}.mlp.up_proj" for i in range(3)], YER) == []


def test_yerlesim_kule_disina_takilani_yakalar():
    adlar = ["model.language_model.layers.0.mlp.up_proj", "model.language_model.layers.1.mlp.up_proj",
             "model.vision_tower.encoder.layers.0.self_attn.q_proj.linear"]
    ihlal = ok.yerlesim_ihlalleri(adlar, YER)
    assert any("dışında" in i and "vision_tower" in i for i in ihlal), ihlal


def test_yerlesim_sayi_tutmazsa_yakalar():
    assert any("≠ kilit 3" in i for i in ok.yerlesim_ihlalleri(["model.language_model.a"], YER))


class _Modul:
    def __init__(self, lora):
        if lora:
            self.lora_A = object()


class _Model:
    def __init__(self, adlar):
        self.adlar = adlar

    def named_modules(self):
        return [("", _Modul(False))] + [(f"base_model.model.{a}", _Modul(True)) for a in self.adlar]


def _kapi(tmp_path, adlar, kilit_yolu):
    (tmp_path / "KUNYE.json").write_text("{}", encoding="utf-8")
    ok.lora_yerlesim_kapisi(_Model(adlar), Namespace(ortam_kilidi=kilit_yolu), str(tmp_path))
    return (tmp_path / "KUNYE.json").read_text(encoding="utf-8")


def test_yerlesim_kapisi_qwen_kilidinde_hicbir_sey_yapmaz(tmp_path):
    assert _kapi(tmp_path, ["x.y"], os.path.join(KOK, "configs/egitim_ortami.yaml")) == "{}"


def test_yerlesim_kapisi_gemma_kilidinde_kule_disinda_durur_ve_kunyeye_yazar(tmp_path):
    adlar = [f"model.language_model.layers.{i}.mlp.up_proj" for i in range(257)] + ["model.vision_tower.q"]
    with pytest.raises(SystemExit):
        _kapi(tmp_path, adlar, os.path.join(KOK, "configs/egitim_ortami_gemma.yaml"))
    assert '"kule_disi": 1' in (tmp_path / "KUNYE.json").read_text(encoding="utf-8")


def test_yerlesim_kapisi_gemma_kilidinde_258_modulle_gecer(tmp_path):
    adlar = [f"model.language_model.layers.{i}.mlp.up_proj" for i in range(258)]
    assert '"takilan_modul": 258' in _kapi(tmp_path, adlar, os.path.join(KOK, "configs/egitim_ortami_gemma.yaml"))


def test_yukleme_secenekleri_gemmada_tam_ad_qwende_bos():
    kw = lambda ad: ok.yukleme_secenekleri(Namespace(ortam_kilidi=os.path.join(KOK, f"configs/{ad}")))
    assert kw("egitim_ortami_gemma.yaml") == {"use_exact_model_name": True}
    assert kw("egitim_ortami.yaml") == {}


# ── eğitim betikleri ve Modal ─────────────────────────────────────────────────

@pytest.mark.parametrize("betik", ["train_sft.py", "train_orpo.py"])
def test_betikler_yukleme_secenekleri_hedef_deseni_ve_kapiyi_kullanir(betik):
    kaynak = open(os.path.join(KOK, "scripts/egitim", betik), encoding="utf-8").read()
    assert "**yukleme_secenekleri(args)" in kaynak
    assert "target_modules=lora_hedefi(args.target_modules)" in kaynak
    assert kaynak.index("get_peft_model") < kaynak.index("lora_yerlesim_kapisi(model, args, out)")


def _modal_fn(ad):
    agac = ast.parse(open(MODAL, encoding="utf-8").read())
    return next(n for n in ast.walk(agac) if isinstance(n, ast.FunctionDef) and n.name == ad)


@pytest.mark.parametrize("fn", ["spawn_sft", "spawn_orpo"])
def test_modal_giris_noktalari_ortam_kilidini_varsayilansiz_ister(fn):
    f = _modal_fn(fn)
    varsayilan = dict(zip([a.arg for a in f.args.args][-len(f.args.defaults):], f.args.defaults))
    assert ast.literal_eval(varsayilan["ortam_kilidi"]) == ""
    assert "_kilit_secimi" in ast.unparse(f)


def test_modal_kilit_secimi_modelle_uyusmayani_ve_bilinmeyeni_reddeder():
    import modal_train as m
    assert m._kilit_secimi("configs/egitim_ortami.yaml", "Qwen/Qwen3.5-4B") == "qwen"
    assert m._kilit_secimi("configs/egitim_ortami_gemma.yaml", "google/gemma-4-E4B-it") == "gemma"
    for kilit, model in (("configs/egitim_ortami_gemma.yaml", "Qwen/Qwen3.5-4B"),
                         ("configs/egitim_ortami.yaml", "google/gemma-4-E4B-it"),
                         ("configs/baska.yaml", "Qwen/Qwen3.5-4B"), ("", "Qwen/Qwen3.5-4B")):
        with pytest.raises(SystemExit):
            m._kilit_secimi(kilit, model)


def test_modal_gemma_imaji_gemma_kilidinden_kurulur_qwen_imaji_degismez():
    kaynak = open(MODAL, encoding="utf-8").read()
    gemma = kaynak[kaynak.index("\ngemma_image = ("):kaynak.index("\ndata_vol")]
    assert 'pip_install_from_requirements("requirements.gemma4.lock.txt"' in gemma
    assert '_KILIT_GEMMA["paketler"]["ek"]' in gemma and "requirements.lock.txt" not in gemma
    qwen = kaynak[kaynak.index("\nimage = ("):kaynak.index("\ngemma_image = (")]
    assert 'pip_install_from_requirements("requirements.lock.txt"' in qwen


@pytest.mark.parametrize("fn,kilit", [("train", "KILIT_KONTEYNER"), ("train_gemma", "KILIT_GEMMA_KONTEYNER"),
                                      ("train_orpo", "KILIT_KONTEYNER"),
                                      ("train_orpo_gemma", "KILIT_GEMMA_KONTEYNER")])
def test_modal_egitim_fonksiyonu_kendi_kilidini_ve_imajini_tasir(fn, kilit):
    f = _modal_fn(fn)
    govde = ast.unparse(f)
    assert kilit in govde and ({"KILIT_KONTEYNER", "KILIT_GEMMA_KONTEYNER"} - {kilit}).isdisjoint(govde.split())
    imaj = "gemma_image" if "gemma" in fn else "image"
    assert ast.unparse(f.decorator_list[0]).startswith(f"app.function(image={imaj},")
