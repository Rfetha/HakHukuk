"""`MODEL_CARD.md` → Hugging Face deposunun `README.md`'si.

Why: iki ayrı kart tutuldu ve **iki kez sessizce ayrıştı** — biri bir turun hiçbir
güncellemesini almadı, düzeltilmiş bir kusuru açıkmış gibi ilan etmeye devam etti.
Tek kaynak `MODEL_CARD.md`'dir; HF sürümü elle yazılmaz, buradan üretilir.

İki dönüşüm yapılır:
  1. HF'in zorunlu YAML ön bilgisi başa eklenir (depo sayfasındaki etiketleri o üretir).
  2. Göreli bağlantılar mutlak GitHub adreslerine çevrilir — HF deposunda `docs/` ve
     `outputs/` yoktur, göreli bağlantı orada sessizce ölü bağlantıya döner.
"""
import pathlib
import re

KOK = pathlib.Path(__file__).resolve().parent.parent
KAYNAK = KOK / "MODEL_CARD.md"
GITHUB = "https://github.com/Rfetha/Hukuk-SLM/blob/master/"

ON_BILGI = """---
license: apache-2.0
language:
  - tr
base_model: Qwen/Qwen3.5-4B
pipeline_tag: text-generation
library_name: llama.cpp
tags:
  - legal
  - turkish
  - rag
  - gguf
  - task-arithmetic
---

"""

# Markdown bağlantısı; http(s), mailto ve saf çapa (#…) dokunulmadan bırakılır.
_GORELI = re.compile(r"(\[[^\]]*\]\()(?!https?://|mailto:|#)([^)\s]+)(\))")


def mutlaklastir(metin: str) -> str:
    """Göreli bağlantıları GitHub'a çivile; çapra (`#…`) dokunma."""
    return _GORELI.sub(lambda m: f"{m.group(1)}{GITHUB}{m.group(2)}{m.group(3)}", metin)


def uret(kaynak: pathlib.Path = KAYNAK) -> str:
    return ON_BILGI + mutlaklastir(kaynak.read_text(encoding="utf-8"))


if __name__ == "__main__":
    print(uret(), end="")
