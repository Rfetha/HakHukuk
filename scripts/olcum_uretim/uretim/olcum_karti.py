#!/usr/bin/env python3
"""Ölçüm kartı koşucusunun saf parçaları (ADR-0097, ADR-0102) — kiralık kartta üretimin tek tanımı.

Platforma (Modal, Vast) bağlı kod yalnız makineyi açar ve bu fonksiyonları çağırır; rejim burada durur:
  sunucu_komutu   llama-server'ın komutu `docker/compose.yaml`'dan (bayrakların tek kaynağı; yalnız model yolu,
                  adres ve port değişir; `-np` eklenmez — istekler tek tek gider, ADR-0102 m.1)
  sunucu_kimligi  sürüm, derleme ve slot sayısı KOŞAN süreçten (`--version` ve sunucu günlüğü; tuzak 1.12)
  uretim_komutu   `gen_eval_grounded.py`'nin h1 rejimi (ADR-0043 · 0067 · 0068 · 0070) + dondurulmuş bağlam
  gecerlilik      kesik oranı ≤ %5 (ADR-0040) ve düşünce kanalı kullanılmış (#38) — değilse koşu geçersiz
"""
import re

import yaml

SUNUCU_IKILISI = "/app/llama-server"      # imajın ENTRYPOINT'i (compose.yaml'daki not)

# h1 rejimi — `cp0_thinking_gen.sh`'in h1 satırı ve f02'nin künyesiyle aynı değerler.
REJIM = {"--thinking": "on", "--think-budget": "1024", "--max-new-tokens": "512",
         "--max-chunk-chars": "900", "--seed": "3407", "--harness-k": "10", "--rrf-k": "10", "--n": "80"}
KESIK_ESIGI = 0.05


def sunucu_komutu(compose_yolu: str, gguf_yolu: str, port: int) -> list[str]:
    """compose'daki `llama` servisinin bayrakları; `-m` bu makinedeki GGUF'a, `--host` 127.0.0.1'e döner."""
    with open(compose_yolu, encoding="utf-8") as f:
        komut = list(yaml.safe_load(f)["services"]["llama"]["command"])
    for bayrak, deger in (("-m", gguf_yolu), ("--host", "127.0.0.1"), ("--port", str(port))):
        komut[komut.index(bayrak) + 1] = deger
    return [SUNUCU_IKILISI, *komut]


def sunucu_kimligi(surum_ciktisi: str, gunluk: str) -> dict:
    """`llama-server --version` çıktısı + sunucu günlüğü → {build, commit, n_slots, kv_unified, surum_satiri}.
    Bir alan okunamazsa None kalır; künyede None görünmesi bir uyarıdır, uydurulmaz."""
    m = re.search(r"build (\d+), commit ([0-9a-f]+)", surum_ciktisi)
    s = re.search(r"n_slots = (\d+).*?kv_unified = '(\w+)'", gunluk)
    return {"surum_satiri": (surum_ciktisi.strip().splitlines() or [""])[0],
            "build": int(m.group(1)) if m else None, "commit": m.group(2) if m else None,
            "n_slots": int(s.group(1)) if s else None,
            "kv_unified": (s.group(2) == "true") if s else None}


def uretim_komutu(python: str, betik: str, sunucu_url: str, veri: str, donmus_baglam: str,
                  etiket: str, cikti_dizini: str) -> list[str]:
    komut = [python, betik, "--server-url", sunucu_url, "--server-model", "local", "--data", veri,
             "--donmus-baglam", donmus_baglam, "--label", etiket, "--out-dir", cikti_dizini]
    for bayrak, deger in REJIM.items():
        komut += [bayrak, deger]
    return komut


def gecerlilik(satirlar: list[dict]) -> dict:
    n = len(satirlar)
    kesik = sum(1 for r in satirlar if r.get("finish_reason") == "length")
    dusunen = sum(1 for r in satirlar if (r.get("reasoning_len") or 0) > 0)
    return {"n": n, "kesik": kesik, "kesik_orani": kesik / n if n else None, "dusunen": dusunen,
            "zorla_kapatilan": sum(1 for r in satirlar if r.get("forced_close")),
            "gecerli": bool(n) and kesik / n <= KESIK_ESIGI and dusunen > 0}
