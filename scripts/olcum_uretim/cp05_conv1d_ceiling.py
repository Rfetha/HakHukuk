#!/usr/bin/env python3
"""CP0.5 — `causal-conv1d` kaldıracının **tavanını** ölç (ADR-0033'ün açık kapısı).

## Neden bu ölçüm, A/B kurulum yerine

`transformers/models/qwen3_5/modeling_qwen3_5.py` okundu (satır 420-423): çekirdekler
**bağımsız** ikame ediliyor —

    self.causal_conv1d_fn      = causal_conv1d_fn                                  # yoksa None
    self.chunk_gated_delta_rule = chunk_gated_delta_rule or torch_chunk_...        # fla'dan GELİYOR

Yani `fla-core` kurulu olduğu için **pahalı özyineli çekirdek zaten hızlı yolda.**
`is_fast_path_available` (satır 425) yalnız bir `warning_once` tetikliyor, başka hiçbir
şeyi kapatmıyor — *"fast path is not available"* uyarısı bu yüzden yanıltıcı (tuzak 3.5).
`causal-conv1d` yokluğunda fallback'e düşen **tek şey** satır 497:

    mixed_qkv = F.silu(self.conv1d(mixed_qkv)[:, :, :L])        # depthwise conv, kernel=4

Dolayısıyla kazancın **matematiksel tavanı** = bu op'un adım süresindeki payı. Bunu ölçmek
için `causal-conv1d`'yi derlemeye gerek yok: hızlı yol dalına **bedeli sıfır bir saplama**
konur (`x -> x`). Gerçek füzyonlu çekirdek bundan hızlı olamaz.

    A "bugün"      : causal_conv1d_fn = None          → torch fallback (satır 497)
    B "ideal, $0"  : causal_conv1d_fn = lambda x: x   → op tamamen kalkmış gibi

    tavan = t_A / t_B

## Neden katman seviyesi yeterli (ve model seviyesinden GÜÇLÜ)

Conv yalnız 24 linear-attention katmanında var; kalan 8 full-attention katmanı, 32 MLP ve
248.320'lik lm_head **paydaya eklenir, paya eklenmez.** Dolayısıyla katman-seviyesi tavan,
model-seviyesi tavanın **üst sınırıdır**. Katmanda 2× çıkmıyorsa modelde de çıkamaz.

⚠️ Şerh: ölçüm yerel RTX 5070 Ti'de; çıpa (6.8-7.0 s/it) A100-40GB'de. Oran iki op'un
göreli maliyeti olduğu için taşınabilir, ama mutlak s/it taşınmaz — künyeye yazılır.

Kullanım: python scripts/olcum_uretim/cp05_conv1d_ceiling.py --batch 2 --seq 2048
"""
import argparse
import json
import statistics

import torch
from transformers import AutoConfig
from transformers.models.qwen3_5.modeling_qwen3_5 import Qwen3_5GatedDeltaNet


def free_conv_stub(x=None, weight=None, bias=None, activation=None, seq_idx=None):
    """İdeal füzyonlu çekirdek: bedeli sıfır. Gerçek çekirdek bundan hızlı olamaz."""
    return x


def bench(layer, hidden, iters, warmup):
    """fwd+bwd süresi (ms/iter) — CUDA event, ısınma atılır."""
    times = []
    for i in range(warmup + iters):
        h = hidden.clone().requires_grad_(True)
        torch.cuda.synchronize()
        s, e = torch.cuda.Event(True), torch.cuda.Event(True)
        s.record()
        out = layer(h)
        out = out[0] if isinstance(out, tuple) else out
        out.float().pow(2).mean().backward()
        e.record()
        torch.cuda.synchronize()
        if i >= warmup:
            times.append(s.elapsed_time(e))
        layer.zero_grad(set_to_none=True)
    return times


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3.5-4B", help="base PARAMETRE (ADR-0026)")
    ap.add_argument("--batch", type=int, default=2, help="Modal eğitim koşusu: 2 (ADR-0033)")
    ap.add_argument("--seq", type=int, default=2048, help="max_seq_len (ADR-0033)")
    ap.add_argument("--iters", type=int, default=30)
    ap.add_argument("--warmup", type=int, default=10)
    ap.add_argument("--out", default="outputs/eval/_artefakt/cp05_conv1d_ceiling.json")
    a = ap.parse_args()

    assert torch.cuda.is_available(), "CUDA yok — ölçüm anlamsız"
    cfg = AutoConfig.from_pretrained(a.model)
    tcfg = getattr(cfg, "text_config", None) or cfg
    n_linear = sum(1 for t in tcfg.layer_types if t == "linear_attention")

    torch.manual_seed(3407)
    layer = Qwen3_5GatedDeltaNet(tcfg, layer_idx=0).to("cuda", torch.bfloat16)
    hidden = torch.randn(a.batch, a.seq, tcfg.hidden_size, device="cuda", dtype=torch.bfloat16)

    print(f"[cp05] {torch.cuda.get_device_name(0)} · batch={a.batch} seq={a.seq} "
          f"· katman {n_linear}/{tcfg.num_hidden_layers} linear-attention "
          f"· conv_kernel={tcfg.linear_conv_kernel_dim}")

    layer.causal_conv1d_fn = None            # A: bugün (torch fallback, satır 497)
    ta = bench(layer, hidden, a.iters, a.warmup)
    layer.causal_conv1d_fn = free_conv_stub  # B: ideal çekirdek, bedel 0
    tb = bench(layer, hidden, a.iters, a.warmup)

    ma, mb = statistics.median(ta), statistics.median(tb)
    ceiling = ma / mb
    res = {
        "gpu": torch.cuda.get_device_name(0), "model": a.model,
        "batch": a.batch, "seq": a.seq, "iters": a.iters, "warmup": a.warmup,
        "n_linear_attention_layers": n_linear, "n_layers": tcfg.num_hidden_layers,
        "A_torch_fallback_ms_median": round(ma, 4),
        "A_ms_stdev": round(statistics.stdev(ta), 4),
        "B_ideal_free_kernel_ms_median": round(mb, 4),
        "B_ms_stdev": round(statistics.stdev(tb), 4),
        "conv_share_of_layer_step": round((ma - mb) / ma, 4),
        "speedup_ceiling_layer": round(ceiling, 4),
        "gate": "≥2.0× yoksa causal-conv1d EKLENMEZ (sprint2.md CP0.5 · ADR-0033)",
        "verdict": "GEÇTİ — eklenir" if ceiling >= 2.0 else "KALDI — eklenmez, negatif bulgu",
        "note": ("Katman-seviyesi tavan, model-seviyesi tavanın ÜST SINIRIdır: conv yalnız "
                 f"{n_linear}/{tcfg.num_hidden_layers} katmanda var, kalan katmanlar + MLP + "
                 f"lm_head (vocab {tcfg.vocab_size}) paydaya eklenir, paya eklenmez."),
    }
    print(json.dumps(res, ensure_ascii=False, indent=2))
    import os
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    print(f"[cp05] → {a.out}")


if __name__ == "__main__":
    main()
