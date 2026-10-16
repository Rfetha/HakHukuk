#!/usr/bin/env python
"""
HakHukuk — Modal image teşhis koşusu (ucuz, GPU'da saniyeler).

⚠️ NEDEN VAR (2026-07-25, CP4): `transformers`'ın tembel-modül sarmalayıcısı gerçek
`ImportError`'ı yutup yerine
    ModuleNotFoundError: Could not import module 'Qwen3_5ForConditionalGeneration'
diye TEK SATIRLIK, kök nedeni GİZLEYEN bir hata basıyor. Bu hata A100'de, model
indirildikten SONRA, ~25 dakikalık bir koşunun sonunda görüldü — yani teşhis için her
denemede A100 yakmak gerekiyordu.

Bu dosya aynı image'ı EN UCUZ GPU'da açar ve fast-path zincirini **tek tek** import edip
gerçek istisnayı basar. `modal_train.py`'nin image tanımını AYNEN kullanır (kopya değil,
import) — yoksa teşhis ettiğimiz image ile eğittiğimiz image ayrışır.

Kullanım:
    modal run scripts/egitim/kosu/modal_diag.py::check
"""
import modal

from modal_train import image as _base_image   # AYNI image — kopyalama, ithal et

# ⚠️ Konteyner modal_diag.py'yi yeniden import eder; yukarıdaki satırın orada da çalışması için
# modal_train.py'nin uzak python yoluna girmesi gerekir. `modal_train.py` image'a KONMAZSA
# uzak taraf `ModuleNotFoundError: No module named 'modal_train'` verir (bir kez yaşandı).
image = _base_image.add_local_python_source("modal_train")

app = modal.App("hukuk-diag")


@app.function(image=image, gpu="L4", timeout=600)
def _probe():
    import traceback

    out = []

    def line(s=""):
        print(s, flush=True)
        out.append(s)

    import torch
    line(f"torch={torch.__version__} cuda={torch.version.cuda} available={torch.cuda.is_available()}")
    import transformers
    line(f"transformers={transformers.__version__}")

    for mod in ("triton", "einops", "fla", "causal_conv1d"):
        try:
            m = __import__(mod)
            line(f"✓ {mod}={getattr(m, '__version__', '?')}")
        except Exception as e:
            line(f"✗ {mod}: {type(e).__name__}: {e}")

    # transformers'ın kapı fonksiyonları (modeling_qwen3_5 bunlara bakıyor)
    try:
        from transformers.utils.import_utils import (is_causal_conv1d_available,
                                                     is_flash_linear_attention_available)
        line(f"is_flash_linear_attention_available={is_flash_linear_attention_available()}")
        line(f"is_causal_conv1d_available={is_causal_conv1d_available()}")
    except Exception as e:
        line(f"✗ import_utils: {type(e).__name__}: {e}")

    # 🔍 ASIL SORU: modeling_qwen3_5'in yaptığı iki import GERÇEKTEN çalışıyor mu?
    for what, fn in (
        ("fla.modules.FusedRMSNormGated",
         lambda: __import__("fla.modules", fromlist=["FusedRMSNormGated"]).FusedRMSNormGated),
        ("fla.ops.gated_delta_rule.chunk_gated_delta_rule",
         lambda: __import__("fla.ops.gated_delta_rule",
                            fromlist=["chunk_gated_delta_rule"]).chunk_gated_delta_rule),
    ):
        try:
            fn()
            line(f"✓ {what}")
        except Exception:
            line(f"✗ {what} — GERÇEK İSTİSNA:")
            line(traceback.format_exc())

    # Ve nihayet modelin kendi modülü
    try:
        from transformers.models.qwen3_5 import modeling_qwen3_5 as m
        line(f"✓ modeling_qwen3_5 · is_fast_path_available={m.is_fast_path_available}")
        line(f"  chunk_gated_delta_rule = {m.chunk_gated_delta_rule}")
        line(f"  causal_conv1d_fn       = {m.causal_conv1d_fn}")
    except Exception:
        line("✗ modeling_qwen3_5 — GERÇEK İSTİSNA:")
        line(traceback.format_exc())

    return "\n".join(out)


@app.local_entrypoint()
def check():
    print(_probe.remote())      # teşhis: kısa ve senkron — spawn kuralı (ADR-0008) uzun
                                # EĞİTİM koşuları içindi; burada çıktıyı beklemek istiyoruz.
