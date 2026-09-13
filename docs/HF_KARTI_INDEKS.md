---
license: apache-2.0
language:
  - tr
task_categories:
  - text-retrieval
pretty_name: HakHukuk Mevzuat Arama İndeksi (bge-m3, şema s2)
tags:
  - legal
  - turkish
  - retrieval
  - embeddings
  - bge-m3
  - rag
---

# HakHukuk — Mevzuat Arama İndeksi (`bge-m3`, şema `s2`)

Bu, `bge-m3` yoğun gömme + BM25 hibrit arama indeksinin gömme matrisidir. HakHukuk hukuk
asistanının retriever katmanı, sorguyu ve mevzuat maddelerini bu indeksle eşleştirir.

## İçerik

Bu depoda **yalnızca şu iki dosya** vardır — başka bir şey yoktur:

| dosya | bayt | sha256 |
| :--- | ---: | :--- |
| `gomme.npy` | 82.935.936 | `16f54cab972eaccb4b30143a70d728faca07253385ce75d5455b4b407a62bedc` |
| `KUNYE.json` | 2.354 | `dfe1562744dd65c405d1fe543b1cf05915251a5b530fdcd65ef2e1e009a6a767` |

toplam 82.938.290 bayt (~79,1 MiB).

**Korpus bu depoya GİRMEZ.** Korpus (`mevzuat_maddeler.jsonl`) zaten git'te izleniyor *ve*
HakHukuk imajına `COPY` ile giriyor; üçüncü bir kopya yayımlamak **ikinci bir doğruluk
kaynağı** yaratırdı — `hakhukuk/indir.py::yerlestir_korpus`'un docstring'inin kelimesi
kelimesine uyardığı sınıf (*"iki farklı korpustan cevap verir ve bu HATA VERMEDEN
yanlıştır"*).

## Hangi korpustan üretildi

`data/corpus/mevzuat_maddeler.jsonl` — 38.751.499 bayt,
sha256 `a35e6efc16123f70c4d0eaf48951f0e4d5bd3134a6faa942964222117c0af468`.

Korpus künyesi — **2026-08-06 anlık görüntüsü**: 892 kanun · 40.496 madde · 2.547 mülga ·
kapsam **yalnız kanunlar**. Kaynak: Mevzuat.gov.tr (kamuya açık).

## ⚠️ Bu indeks bir fotoğraftır, canlı bir kaynak değildir

**Mevzuat değişir; ağırlıklar değişmez.** Bu indeks 2026-08-05'te kurulduğu günün gömme
matrisidir ve otomatik güncellenmez. Tazelik (yeni madde/değişiklik indekse yansıması)
`v2`'nin işidir — bu depo tekil, sürümlü bir anlık görüntüdür.

## Ölçülmüş performans

`recall@10 = 0,9500` (n=80, `data/eval/dev/core_hard.jsonl`, k=10).

## `model_revision`: ölçülmedi, uydurulmadı

`KUNYE.json`'daki `model_revision` alanı `null`'dır ve öyle kalacaktır. Sebep: indeks
2026-08-05 17:30'da kuruldu; yerel HF önbelleği 2026-09-06 18:07'de doldu (iki ayrı
snapshot var) ⇒ önbellekteki commit, indeksin kurulduğu günkü kolun kanıtı DEĞİLDİR —
tahmini bir revizyon yazmak, ölçülmemiş bir şeyi ölçülmüş gibi göstermek olurdu. Bundan
sonra kurulan her indeks bu alanı `retriever.kur` ile **ölçerek** yazacaktır.

## Lisans

Apache-2.0.

## Nasıl kullanılır

`hakhukuk` paketinin varsayılan davranışı bu depoyu çeker:

```python
from hakhukuk import indir
indir.indir_indeks("/artefakt")
```

Başka bir indeks depoya çekmek gerekirse `HAKHUKUK_INDEKS_DEPO` ortam değişkeni
varsayılanı geçersiz kılar. İnen `gomme.npy` bayt sayısı ve `sha256` ile doğrulanır
(`hakhukuk.indir.INDEKS_GOMME_BAYT` / `INDEKS_GOMME_SHA256`); tutmazsa indirme
`KimlikHatasi` ile durur.

## Kod deposu

https://github.com/Rfetha/HakHukuk
