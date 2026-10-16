#!/usr/bin/env python3
"""F0.16 vLLM pilotu — dondurulmuş bağlamdan sorular AYNI ANDA gönderilir (toplu üretim).

`gen_eval_grounded.py` soruları döngüde tek tek yollar; vLLM'in hızı birçok isteğin aynı anda çözülmesinden gelir.
Bu sürücü o betiğin `generate_http` fonksiyonunu AYNEN kullanır (istem, bütçe, seed, zorunlu kapatma tek
kaynak) ve yalnız üç şeyi değiştirir:
  1. istekler `--es-zamanli` iş parçacığıyla paralel gider; kayıtlar yine kalem sırasında yazılır
  2. zorunlu kapatmanın ham istemi `/apply-template` (llama-server'a özgü) yerine yerel tokenizer
     klasöründeki şablondan gelir (şablon GGUF'takiyle bayt bayt aynıdır: tests/betikler/olcum_uretim/test_toplu_uret.py)
  3. vLLM düşünceyi `reasoning` adıyla döndürürse `reasoning_content` olarak da okunur
Kayıt biçimi sıralı üretimin `_detail.jsonl`'iyle aynıdır; puanlama ve `makine_kapisi.py` olduğu gibi çalışır.

Kullanım (rejim `olcum_karti.REJIM`'den; para harcamaz, sunucu adresi verilir):
  python scripts/olcum_uretim/uretim/toplu_uret.py --server-url http://127.0.0.1:8000/v1 --server-model local \\
      --data data/eval/dev/core_hard.jsonl --donmus-baglam data/eval/dev/baglam/h1-k10.json \\
      --tokenizer-dizini models/merged/tgta_v1 --es-zamanli 16 --etiket vllm_t1 --cikti-dizini /tmp/o
"""
# ── scripts/ yol köprüsü (T5 2026-09-07 · ADR-0112 2026-10-16) ───────────────
# Kardeş modüller iç içe alt klasörlerde de bulunsun diye scripts/ kökü, altındaki HER
# derinlikteki klasör ve repo kökü sys.path'e girer. Uzantısız `import X` bu köprü olmadan
# taşımada SESSİZCE kırılır: ImportError çalışma zamanında, bazen GPU koşusunun ortasında.
# ⚠️ 39 dosyada BİREBİR aynı; değiştirirsen hepsinde değiştir (grep: "yol köprüsü").
import os, sys
_K = os.path.abspath(__file__)
_K = _K[:_K.rindex(os.sep + "scripts" + os.sep)] + os.sep + "scripts"  # dışarıda: ValueError
_Y = []
for _y, _alt, _f in os.walk(_K):
    _alt[:] = sorted(_a for _a in _alt if _a[0] not in "_.")
    _Y.append(_y)
sys.path[:0] = [*_Y, os.path.dirname(_K)]
# ─────────────────────────────────────────────────────────────────────────────
import argparse  # noqa: E402
import json  # noqa: E402
import time  # noqa: E402
from concurrent.futures import ThreadPoolExecutor  # noqa: E402
from unittest import mock  # noqa: E402

import olcum_karti  # noqa: E402
from part_dosya import part_ile_yaz  # noqa: E402


def yerel_sablon(tokenizer_dizini: str):
    """(mesajlar, düşünme) → şablonun ürettiği ham istem; `/apply-template`'in yerel karşılığı."""
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(tokenizer_dizini)

    def sablon(mesajlar, dusunme):
        kw = {} if dusunme == "none" else {"enable_thinking": dusunme == "on"}
        return tok.apply_chat_template(mesajlar, tokenize=False, add_generation_prompt=True, **kw)
    return sablon


def metin_yapilandirmasi(tam: dict) -> dict:
    """Görüntü kulesiyle gelen model yapılandırması → yalnız metin yapılandırması (GGUF metin ağırlıkları taşır)."""
    m = {k: v for k, v in tam["text_config"].items()}
    m["architectures"] = ["Qwen3_5ForCausalLM"]
    return m


class _AlanAdiEsle:
    """İstemciyi sarar: vLLM düşünceyi `reasoning` adıyla verirse `reasoning_content` olarak da okunur."""

    def __init__(self, istemci):
        self._i = istemci
        self.completions = istemci.completions
        self.chat = _Sohbet(istemci.chat.completions)


class _Sohbet:
    def __init__(self, tamamlamalar):
        self.completions = self
        self._t = tamamlamalar

    def create(self, **kw):
        r = self._t.create(**kw)
        for ch in r.choices:
            m = ch.message
            if not getattr(m, "reasoning_content", None) and getattr(m, "reasoning", None):
                m.reasoning_content = m.reasoning
        return r


def _kayit(i, kalem, g):
    out = {"id": i, "soru": kalem["soru"], "referans": kalem["referans"],
           "context_shown": kalem["sources_block"], "mode": "harness", "cevap": g.text,
           "finish_reason": g.finish_reason, "reasoning_len": g.reasoning_len,
           "completion_tokens": g.completion_tokens, "reasoning_tokens": g.reasoning_tokens,
           "forced_close": g.forced_close, "kanun_adi": kalem.get("kanun_adi"),
           "madde_no": kalem.get("madde_no"), "kanun_no": kalem.get("kanun_no"),
           "harness": kalem["harness"]}
    if not g.text:
        raise SystemExit(f"[toplu-uret] 🚫 BOŞ cevap — örnek {i}, finish_reason={g.finish_reason!r}, "
                         f"reasoning_content={g.reasoning_len} kar. Boş cevaplar üzerinde ÜRETİLEN HER "
                         f"SAYI GEÇERSİZDİR — koşu durduruldu.")
    return out


def uret(istemci, model_adi, kalemler, es_zamanli, sablon):
    """Kalemleri `es_zamanli` iş parçacığıyla üretir → (kalem sırasında kayıtlar, süre_s)."""
    import gen_eval_grounded as gen
    rejim = olcum_karti.REJIM
    sarmal = _AlanAdiEsle(istemci)

    def tek(i_kalem):
        i, kalem = i_kalem
        g = gen.generate_http(sarmal, model_adi, kalem["soru"], int(rejim["--max-new-tokens"]),
                              source=None, sources_block=kalem["sources_block"], thinking=rejim["--thinking"],
                              think_budget=int(rejim["--think-budget"]), server_url="", reasoning_budget=0,
                              sufficiency=False)
        return _kayit(i, kalem, g)

    t0 = time.time()
    with mock.patch.object(gen, "render_prompt", lambda server_url, mesajlar, dusunme: sablon(mesajlar, dusunme)):
        with ThreadPoolExecutor(max_workers=es_zamanli) as havuz:
            kayitlar = list(havuz.map(tek, enumerate(kalemler)))
    return kayitlar, time.time() - t0


def yaz(kayitlar, yol):
    with part_ile_yaz(yol) as f:
        for k in kayitlar:
            f.write(json.dumps(k, ensure_ascii=False) + "\n")


def main(argv=None):
    p = argparse.ArgumentParser(description="vLLM pilotu — toplu üretim (F0.16)")
    p.add_argument("--server-url", required=True)
    p.add_argument("--server-model", required=True)
    p.add_argument("--data", required=True)
    p.add_argument("--donmus-baglam", required=True)
    p.add_argument("--tokenizer-dizini", required=True)
    p.add_argument("--es-zamanli", type=int, required=True)
    p.add_argument("--etiket", required=True)
    p.add_argument("--cikti-dizini", required=True)
    p.add_argument("--ilk-n", type=int, default=0, help="0 = hepsi; N>0 = yalnız ilk N kalem (kontrol aşaması)")
    a = p.parse_args(argv)

    from baglam_dondur import Ayar, oku, sha256_dosya
    r = olcum_karti.REJIM
    kalemler = oku(a.donmus_baglam,
                   Ayar(seed=int(r["--seed"]), n=int(r["--n"]), harness_k=int(r["--harness-k"]),
                        rrf_k=int(r["--rrf-k"]), max_chunk_chars=int(r["--max-chunk-chars"]),
                        harness_no_gold=False),
                   veri_sha256=sha256_dosya(a.data))
    if a.ilk_n:
        kalemler = kalemler[:a.ilk_n]
    from openai import OpenAI
    istemci = OpenAI(base_url=a.server_url, api_key="none", max_retries=2, timeout=600.0)
    os.makedirs(a.cikti_dizini, exist_ok=True)
    kayitlar, sure = uret(istemci, a.server_model, kalemler, a.es_zamanli, yerel_sablon(a.tokenizer_dizini))
    yol = os.path.join(a.cikti_dizini, f"{a.etiket}_detail.jsonl")
    yaz(kayitlar, yol)
    tok = sum(k["completion_tokens"] or 0 for k in kayitlar)
    print(f"[toplu-uret] {len(kayitlar)} kalem · {sure:.1f} s · {tok / sure:.0f} token/s · "
          f"{sum(1 for k in kayitlar if k['forced_close'])} zorla kapatma · → {yol}", flush=True)


if __name__ == "__main__":
    main()
