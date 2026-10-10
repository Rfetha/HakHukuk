# HakHukuk

Dizüstü GPU'sunda çalışan ve yalnız kendisine verilen mevzuattan cevap veren 4B'lik bir Türkçe hukuk asistanı.

[Model kartı](../MODEL_CARD.md) · [English](../README.md) · [Yol haritası](ROADMAP_v1.md) · [Ağırlıklar](https://huggingface.co/Rfetha/HakHukuk-4B-GGUF) · [İndeks](https://huggingface.co/datasets/Rfetha/HakHukuk-mevzuat-bge-m3-s2) · [Lisans](../LICENSE)

## Ne yapar

Bir soru ve ilgili madde metinleri verildiğinde model ya cevaplar ve dayandığı maddeyi belirtir,
ya da verilen kaynakların soruyu kapsamadığını söyler. Hukukta kendinden emin ama yanlış bir
madde numarası susmaktan daha zararlı olduğu için iki davranış ayrı eğitilmiştir: temellendirme
için bir LoRA kolu, çekinme için bir LoRA kolu; ikisi `Qwen/Qwen3.5-4B` üzerinde görev vektörü
olarak TIES ile birleştirilmiştir. Maddeleri bulan arama katmanı (BM25 + `bge-m3`) modelle
birlikte gelir.

## Hızlı başlangıç

Konteyner (önerilen; sayıların ölçüldüğü sunucu bayraklarını zorlar ve her indirmeyi `sha256`
ile doğrular):

```bash
git clone https://github.com/Rfetha/HakHukuk && cd HakHukuk
docker compose -f docker/compose.yaml up      # API 127.0.0.1:8000 · llama-server 127.0.0.1:8080
```

Python paketi (`llama-server`'ı `127.0.0.1:8080`'de bekler; bayraklar
[MODEL_CARD §7](../MODEL_CARD.md#7-çalıştırma)'de):

```bash
pip install -e .
hakhukuk "Askerlik nedeniyle iş sözleşmesi ne olur?"
```

Yalnız ağırlıklar:

```bash
hf download Rfetha/HakHukuk-4B-GGUF HakHukuk-4B-v0.3-Q4_K_M.gguf --local-dir models/gguf
```

Model tek başına bildirilen sayıları üretmez; sayılar arama katmanı açıkken ölçülmüştür.

## Manşet sayılar

| Geliştirme kümesi, n=80, arama katmanı açık | |
| :--- | ---: |
| Sadık cevap kütlesi (iki hakem ailesi) | 0,694 – 0,801 |
| Uydurulmuş madde numarası | 0 / 114 |
| Kaynak elindeyken gereksiz çekinme | 4 / 80 |
| Yanlış maddeye dayanan cevap | 8 / 80 |
| VRAM (4.096 bağlam) | 3,09 GiB |
| Cevap başına maliyet | $0 (yerel) |

Aralığın iki ucu, aynı 80 cevabın `gpt-4o-mini` (0,8011) ve `claude-sonnet-5` (0,6940)
tarafından puanlanmasıdır. Rakip karşılaştırması, donmuş test sonucu ve sınırlar:
[MODEL_CARD §5](../MODEL_CARD.md#5-sonuçlar).

## Neyi vaat etmez

- Hukuki tavsiye değildir. Ürettiği her madde numarası
  [mevzuat.gov.tr](https://www.mevzuat.gov.tr) üzerinden doğrulanmalıdır.
- Arama katmanı olmadan bildirilen sonucu üretmez; kaynaksız kullanımda kendinden emin ama yanlış
  hukuki içerik üretir.
- Kapsam yalnız yürürlükteki Türkiye Cumhuriyeti kanunlarıdır: 892 kanun, 40.496 madde,
  2026-08-06 anlık görüntüsü. Yönetmelik, tüzük, KHK ve tebliğ kapsam dışıdır.
- Rakip modellerle eşdeğerlik iddiası yoktur.

`v1.0` bir ölçüm sürümüdür: ağırlıklar `v0.3`'ten beri değişmemiştir. Üç sürüm numarası
(artefakt, dosya, ürün) [MODEL_CARD §1](../MODEL_CARD.md#1-model-nedir)'de açıklanır.

## Depo haritası

| nerede | ne |
| :--- | :--- |
| [`hakhukuk/`](../hakhukuk/) | ürün paketi: `cekirdek/` (servis, istem, sınıflandırıcı) · `arayuz/` (CLI, TUI, HTTP API) · `dagitim/` (doğrulamalı indirme) |
| [`scripts/`](../scripts/) | ölçüm hattı, üründen ayrı tutulur |
| [`docker/`](../docker/) | Dockerfile ve `compose.yaml` |
| [`docs/`](README.md) | bütün belgeler; indeks `docs/README.md` |
| [`docs/adr/`](adr/README.md) | karar defteri, ADR-0088'e kadar |
| [`docs/record/`](record/README.md) | kronolojik araştırma kaydı, #71'e kadar |
| [`outputs/eval/`](../outputs/eval/README.md) | ham değerlendirme çıktıları ve koşu künyeleri, `<grup>/<koşu>/` düzeninde |
| [`tests/`](../tests/) | `pytest`: 335 geçti, 2 xfail |

## Araştırma kaydı

Olumsuz sonuçlar olumlu sonuçlarla aynı özenle tutulur: kendi ön-kayıtlı kapısınca geçersiz
sayılan koşular, ölçümle tersine dönen kararlar, geçilemeyen bir kapı. Her sayının metriğini,
`n`'ini, hakemini, seed'ini ve çıktı dosyasını sabitleyen bir koşu künyesi (`KUNYE.json`) vardır.
Ayrıntılı ölçüm tabloları [`docs/OLCUM.md`](OLCUM.md)'dedir.

## Katkı

Eleştiri, düzeltme ve özellikle yeniden üretim denemeleri memnuniyetle karşılanır
([`docs/YENIDEN_URETIM.md`](YENIDEN_URETIM.md)). Yeniden üretilemeyen bir sayı hata raporudur.

## Lisans

Ağırlık, kod, veri ve araştırma kaydı için Apache-2.0 ([`LICENSE`](../LICENSE)). Temel model
`Qwen/Qwen3.5-4B` de Apache-2.0'dır.
