"""F0.4 — eğitim ortamı kilidi: yaml tek kaynak, betik başı kontrolü kodda (test_konteyner.py'nin eşi).

Kilit üç parçadır (EGITIM_ORTAMI §1): belge · `configs/egitim_ortami.yaml` · betik başı kontrolü.
Bu test (a) yaml'ı belgeye ve kilit dosyasına, (b) kontrolün kurallarını sahte gözlemlerle,
(c) kontrolün iki eğitim betiğinde model yüklenmeden ÖNCE çağrıldığını kod ağacından,
(d) Modal zincirinin kilidi taşıdığını sınar. GPU gerekmez.
"""
import ast
import hashlib
import os
import re
from argparse import Namespace

import pytest

import ortam_kilidi as ok  # noqa: E402

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
YAML = os.path.join(KOK, "configs/egitim_ortami.yaml")
BELGE = os.path.join(KOK, "docs/EGITIM_ORTAMI.md")
MODULLER11 = ["q_proj", "k_proj", "v_proj", "o_proj", "in_proj_qkv", "in_proj_z", "in_proj_a",
              "in_proj_b", "gate_proj", "up_proj", "down_proj"]


@pytest.fixture(scope="module")
def kilit():
    return ok.OrtamKilidi.yukle(YAML)


def _belge_satiri(alan):
    """EGITIM_ORTAMI §2 tablosunda `| alan | değer | kaynak |` satırının değer+kaynak metni."""
    for satir in open(BELGE, encoding="utf-8"):
        hucre = [h.strip() for h in satir.split("|")]
        if len(hucre) > 3 and hucre[1].strip("`").startswith(alan):
            return " ".join(hucre[2:])
    raise AssertionError(f"§2'de '{alan}' satırı yok")


# ── (a) yaml ↔ belge ↔ kilit dosyası ──────────────────────────────────────────

def test_kilit_dosyasinin_ozeti_yamldaki_ile_ayni(kilit):
    yol = os.path.join(KOK, kilit.veri["paketler"]["kilit_dosyasi"])
    assert hashlib.sha256(open(yol, "rb").read()).hexdigest() == kilit.veri["paketler"]["kilit_sha256"]


def test_kilit_dosyasindaki_surumler_yamldaki_ile_ayni(kilit):
    yol = os.path.join(KOK, kilit.veri["paketler"]["kilit_dosyasi"])
    pin = dict(l.strip().split("==", 1) for l in open(yol, encoding="utf-8") if "==" in l)
    for paket, surum in kilit.veri["paketler"]["surumler"].items():
        assert pin.get(paket) == surum, paket
    for paket in [*kilit.veri["paketler"]["ek"], *kilit.veri["paketler"]["yasak"]]:
        assert paket not in pin, f"{paket} kilit dosyasında olmamalı (imaja ayrıca kurulur)"


def test_yaml_belge_ile_alan_alan_ayni(kilit):
    v = kilit.veri
    assert v["gpu"]["modal_dizesi"] in _belge_satiri("Modal kart dizesi")
    assert "8.0" in _belge_satiri("GPU") and v["gpu"]["hesaplama_surumu"] == [8, 0]
    assert v["python"] in _belge_satiri("Python")
    paket = _belge_satiri("paketler")
    assert v["paketler"]["kilit_sha256"] in paket
    for p, s in v["paketler"]["surumler"].items():
        assert f"{p} {s}" in paket, p
    assert "bf16 taban + LoRA" in _belge_satiri("hassasiyet") and v["hassasiyet"] == "bf16-taban"
    lora = _belge_satiri("LoRA")
    l = v["lora"]
    assert f"r={l['r']}" in lora and f"α={l['alpha']}" in lora
    assert f"dropout {l['dropout']}".replace(".", ",") in lora and "use_rslora=False" in lora
    assert " ".join(l["hedef_moduller"]) in lora and l["hedef_moduller"] == MODULLER11
    sft, s = _belge_satiri("SFT tarifi"), v["tarifler"]["sft"]
    for parca in (s["veri"], "17.323", str(s["max_seq_len"]), f"{s['batch']} × biriktirme {s['grad_accum']}",
                  "checkpointing **kapalı**", "lr 1e-4 cosine", s["optim"], "1.083 adım", "packing **yok**"):
        assert parca in sft, parca
    orpo, o = _belge_satiri("ORPO tarifi"), v["tarifler"]["orpo"]
    for parca in (o["veri"], "845 satır", "lr 1e-5", "beta 0,1", "biriktirme 64", "5 epoch = 70 adım",
                  "--fresh-adapter"):
        assert parca in orpo, parca
    assert all(str(t) in _belge_satiri("seed") for t in v["seedler"])


def test_yaml_ek_paket_surumleri_belgede(kilit):
    """EGITIM_ORTAMI §2 einops/fla satırı sürümleri taşımalı (belge düzenlemesi onay bekliyor)."""
    ek = _belge_satiri("einops")
    for p, s in kilit.veri["paketler"]["ek"].items():
        assert f"{p} {s}" in ek, p


# ── (b) kontrolün kuralları ───────────────────────────────────────────────────

def _sft_args(**degis):
    a = dict(model="Qwen/Qwen3.5-4B", data="/data/raft_scrubbed", hassasiyet="bf16-taban",
             max_seq_len=2048, batch=2, grad_accum=8, no_grad_checkpoint=True, lr=1e-4,
             warmup_ratio=0.05, epochs=1.0, max_steps=-1, lora_r=16, lora_alpha=32,
             lora_dropout=0.05, target_modules=list(reversed(MODULLER11)), seed=3407,
             no_system=True, allow_high_lr=False,
             user_part="<|im_start|>user\n", assistant_part="<|im_start|>assistant\n")
    a.update(degis)
    return Namespace(**a)


def _orpo_args(**degis):
    a = dict(model="Qwen/Qwen3.5-4B", data="/data/orpo_abstain_cp2c", hassasiyet="bf16-taban",
             max_length=2048, max_prompt_length=1536, batch=1, grad_accum=64, lr=1e-5, beta=0.1,
             warmup_ratio=0.05, epochs=5.0, max_steps=-1, durdur_adim=None, lora_r=16,
             lora_alpha=32, lora_dropout=0.05, target_modules=MODULLER11, seed=3408,
             fresh_adapter=True, adapter=None)
    a.update(degis)
    return Namespace(**a)


def test_tarif_dogru_sft_argumanlarinda_ihlal_yok(kilit):
    assert ok.tarif_ihlalleri(kilit, "sft", _sft_args()) == []


def test_tarif_dogru_orpo_argumanlarinda_ihlal_yok(kilit):
    assert ok.tarif_ihlalleri(kilit, "orpo", _orpo_args()) == []


@pytest.mark.parametrize("degis,alan", [
    ({"lr": 2e-4}, "lr"),                         # Modal'ın `if lr:` düşmesi → betiğin 2e-4'ü
    ({"hassasiyet": "nf4"}, "hassasiyet"),
    ({"batch": 1, "grad_accum": 16}, "batch"),
    ({"warmup_ratio": 0.03}, "warmup_ratio"),     # betiğin varsayılanı
    ({"target_modules": MODULLER11[:7]}, "target_modules"),
    ({"seed": 42}, "seed"),
    ({"no_grad_checkpoint": False}, "grad_checkpoint"),
    ({"model": "Qwen/Qwen3.5-9B"}, "model"),
    ({"data": "/data/raft"}, "veri"),
    ({"no_system": False}, "sistem_istemi"),
])
def test_tarif_sapmasi_sft_ihlal_uretir(kilit, degis, alan):
    ihlal = ok.tarif_ihlalleri(kilit, "sft", _sft_args(**degis))
    assert any(alan in i for i in ihlal), ihlal


@pytest.mark.parametrize("degis,alan", [
    ({"fresh_adapter": False, "adapter": "/outputs/tg"}, "taze_adaptor"),
    ({"epochs": 3.0}, "epochs"),
    ({"beta": 0.3}, "beta"),
])
def test_tarif_sapmasi_orpo_ihlal_uretir(kilit, degis, alan):
    ihlal = ok.tarif_ihlalleri(kilit, "orpo", _orpo_args(**degis))
    assert any(alan in i for i in ihlal), ihlal


def _gozlem(**degis):
    g = dict(gpu_adi="NVIDIA A100-SXM4-40GB", hesaplama_surumu=(8, 0),
             surumler={"torch": "2.10.0+cu128", "triton": "3.6.0", "transformers": "5.10.2",
                       "peft": "0.19.1", "trl": "0.24.0", "unsloth": "2026.6.1",
                       "unsloth_zoo": "2026.6.1", "accelerate": "1.13.0", "bitsandbytes": "0.49.2",
                       "datasets": "4.3.0", "einops": "0.8.2", "fla-core": "0.5.1",
                       "flash-linear-attention": "0.5.1", "causal-conv1d": None},
             fla_hatasi="")
    g.update(degis)
    return ok.OrtamGozlemi(**g)


def test_ortam_dogru_gozlemde_ihlal_yok(kilit):
    assert ok.ortam_ihlalleri(kilit, _gozlem()) == []


@pytest.mark.parametrize("degis,alan", [
    ({"gpu_adi": "NVIDIA H100 80GB HBM3", "hesaplama_surumu": (9, 0)}, "GPU"),
    ({"gpu_adi": "NVIDIA GeForce RTX 5090", "hesaplama_surumu": (12, 0)}, "GPU"),
    ({"fla_hatasi": "ModuleNotFoundError: fla.modules"}, "fla"),
])
def test_ortam_sapmasi_ihlal_uretir(kilit, degis, alan):
    ihlal = ok.ortam_ihlalleri(kilit, _gozlem(**degis))
    assert any(alan in i for i in ihlal), ihlal


def test_ortam_paket_surumu_ve_yasak_paket(kilit):
    s = dict(_gozlem().surumler, **{"fla-core": "0.5.2", "causal-conv1d": "1.5.0"})
    ihlal = ok.ortam_ihlalleri(kilit, _gozlem(surumler=s))
    assert any("fla-core" in i for i in ihlal) and any("causal-conv1d" in i for i in ihlal)


def test_veri_satir_sayisi_kilitten_sapinca_ihlal(kilit, tmp_path):
    d = tmp_path / "raft_scrubbed"
    d.mkdir()
    (d / "train.jsonl").write_text('{"a": 1}\n' * 3)
    (d / "validation.jsonl").write_text('{"a": 1}\n')
    ozet = ok.veri_ozeti(str(d))
    assert ozet["train"]["satir"] == 3
    assert any("satir" in i for i in ok.veri_ihlalleri(kilit, "sft", ozet))


def _kunye_yaz(dizin):
    (dizin / "KUNYE.json").write_text('{"durum": "basladi"}', encoding="utf-8")


def test_kunye_tamamla_tepe_vram_ve_adim_suresini_yazar(tmp_path, monkeypatch):
    import json
    import torch
    monkeypatch.setattr(torch.cuda, "max_memory_allocated", lambda: 30_000_000_000)
    monkeypatch.setattr(torch.cuda, "max_memory_reserved", lambda: 32_000_000_000)
    _kunye_yaz(tmp_path)
    ok.kunye_tamamla(str(tmp_path), 50, 100.0, 0)
    k = json.loads((tmp_path / "KUNYE.json").read_text(encoding="utf-8"))
    assert k["durum"] == "bitti" and k["adim_gerceklesen"] == 50
    o = k["olcum"]
    assert o["tepe_vram_ayrilan_bayt"] == 30_000_000_000 and o["tepe_vram_rezerve_bayt"] == 32_000_000_000
    assert o["oturum_adim"] == 50 and o["s_adim"] == 2.0


def test_kunye_tamamla_devam_eden_koshuda_yalniz_bu_oturumun_adimlarina_boler(tmp_path, monkeypatch):
    import json
    import torch
    monkeypatch.setattr(torch.cuda, "max_memory_allocated", lambda: 1)
    monkeypatch.setattr(torch.cuda, "max_memory_reserved", lambda: 1)
    _kunye_yaz(tmp_path)
    ok.kunye_tamamla(str(tmp_path), 250, 100.0, 200)
    o = json.loads((tmp_path / "KUNYE.json").read_text(encoding="utf-8"))["olcum"]
    assert o["oturum_adim"] == 50 and o["s_adim"] == 2.0


@pytest.mark.parametrize("yol", ["scripts/egitim/kosu/train_sft.py", "scripts/egitim/kosu/train_orpo.py"])
def test_egitim_betikleri_kunyeye_sure_ve_ilk_adimi_gecirir(yol):
    cagri = next(n for n in ast.walk(_main_govdesi(yol)) if isinstance(n, ast.Call)
                 and getattr(n.func, "id", None) == "kunye_tamamla")
    assert len(cagri.args) == 4


# ── (c) iki eğitim betiğinde kontrol model yüklenmeden ÖNCE ───────────────────

def _main_govdesi(yol):
    agac = ast.parse(open(os.path.join(KOK, yol), encoding="utf-8").read())
    return next(n for n in agac.body if isinstance(n, ast.FunctionDef) and n.name == "main")


def _ilk_satir(govde, ad):
    satirlar = [n.lineno for n in ast.walk(govde) if isinstance(n, ast.Call)
                and (getattr(n.func, "attr", None) == ad or getattr(n.func, "id", None) == ad)]
    assert satirlar, f"{ad} çağrısı yok"
    return min(satirlar)


@pytest.mark.parametrize("yol", ["scripts/egitim/kosu/train_sft.py", "scripts/egitim/kosu/train_orpo.py"])
def test_kilit_kontrolu_model_yuklenmeden_once(yol):
    govde = _main_govdesi(yol)
    assert _ilk_satir(govde, "kilidi_uygula") < _ilk_satir(govde, "from_pretrained")


@pytest.mark.parametrize("yol", ["scripts/egitim/kosu/train_sft.py", "scripts/egitim/kosu/train_orpo.py"])
def test_hassasiyet_ve_kilit_zorunlu_bf16_bayragi_yok(yol):
    kaynak = open(os.path.join(KOK, yol), encoding="utf-8").read()
    agac = ast.parse(kaynak)
    argumanlar = {}
    for n in ast.walk(agac):
        if isinstance(n, ast.Call) and getattr(n.func, "attr", None) == "add_argument":
            ad = n.args[0].value
            argumanlar[ad] = {k.arg: k.value for k in n.keywords}
    assert "--bf16-base" not in argumanlar
    for ad in ("--hassasiyet", "--ortam-kilidi"):
        assert ad in argumanlar, ad
        assert isinstance(argumanlar[ad].get("required"), ast.Constant) and argumanlar[ad]["required"].value
        assert "default" not in argumanlar[ad]


# ── (d) Modal zinciri ─────────────────────────────────────────────────────────

MODAL = os.path.join(KOK, "scripts/egitim/kosu/modal_train.py")


def _egitim_imaji_blogu():
    kaynak = open(MODAL, encoding="utf-8").read()
    return kaynak[kaynak.index("\nimage = ("):kaynak.index("\ndata_vol")]


def test_modal_egitim_imaji_ek_paketleri_yamldan_sabit_surumle_kurar():
    blok = _egitim_imaji_blogu()
    assert not re.search(r'pip_install\(\s*"einops"', blok), "sürümsüz kurulum kaldı"
    assert '["paketler"]["ek"]' in blok


def test_modal_egitim_imajina_configs_ve_hakhukuk_girer():
    blok = _egitim_imaji_blogu()
    assert re.search(r'add_local_dir\("configs"', blok)
    assert re.search(r'add_local_dir\("hakhukuk"', blok)


def test_modal_gpu_dizesi_yamldan(kilit):
    import modal_train
    assert modal_train.GPU == kilit.veri["gpu"]["modal_dizesi"] or os.environ.get("HUKUK_GPU")


@pytest.mark.parametrize("fn,param", [("spawn_sft", "seed"), ("spawn_sft", "max_steps"),
                                      ("spawn_sft", "hassasiyet"), ("spawn_orpo", "seed"),
                                      ("spawn_orpo", "hassasiyet"), ("spawn_orpo", "durdur_adim"),
                                      ("train", "seed"), ("train_orpo", "durdur_adim"),
                                      ("train", "hesap"), ("train_orpo", "hesap")])
def test_modal_giris_noktalari_parametreyi_tasir(fn, param):
    agac = ast.parse(open(MODAL, encoding="utf-8").read())
    f = next(n for n in ast.walk(agac) if isinstance(n, ast.FunctionDef) and n.name == fn)
    assert param in [a.arg for a in f.args.args]
    assert "bf16_base" not in [a.arg for a in f.args.args]


def test_modal_hesabi_aktif_profilin_workspace_adini_dondurur():
    import modal_train
    profiller = [{"name": "a", "workspace": "hesap-a", "active": False},
                 {"name": "b", "workspace": "hesap-b", "active": True}]
    assert modal_train._modal_hesabi(profiller) == "hesap-b"


@pytest.mark.parametrize("profiller", [
    [{"name": "a", "workspace": "hesap-a", "active": False}],
    [{"name": "a", "workspace": "Unknown (authentication failure)", "active": True}],
])
def test_modal_hesabi_okunamazsa_durur(profiller):
    import modal_train
    with pytest.raises(SystemExit):
        modal_train._modal_hesabi(profiller)


def test_alt_surec_bitince_beklemeden_doner():
    """Ara commit aralığı (900 sn) boyunca uyumak, kısa koşuda bitişi 15 dk geciktirip boşta GPU
    faturası yazıyordu (F0.4 eşdeğerlik koşuları, 2026-10-11). Alt süreç bitince hemen dönmeli."""
    import sys
    import time
    import modal_train

    class _Hacim:
        def __init__(self):
            self.commit_sayisi = 0

        def commit(self):
            self.commit_sayisi += 1

    h = _Hacim()
    t0 = time.monotonic()
    modal_train._run_with_commits([sys.executable, "-c", "pass"], [h], every_s=600)
    assert time.monotonic() - t0 < 30
    assert h.commit_sayisi >= 1, "son commit atlanmamalı"
