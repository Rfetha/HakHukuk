# HakHukuk

> **Türkçe bir hukuk asistanı: dizüstünde koşacak kadar küçük, "bu kaynaklarda yok" demeyi
> öğrenmiş 4B'lik bir model.**
> Açık kaynak **ürün** — ağırlık + kod + veri + **araştırma kaydının tamamı**.

[**Model kartı**](MODEL_CARD.md) · [English](README.md) · [Yol haritası](ROADMAP.md) · [Ağırlıklar](https://huggingface.co/Rfetha/HakHukuk-4B-GGUF) · [İndeks](https://huggingface.co/datasets/Rfetha/HakHukuk-mevzuat-bge-m3-s2) · [Lisans](LICENSE)

Bir hukuk asistanının işinin büyük kısmı cevap vermek değil, **kaynak desteklemiyorken cevap
vermemektir.** Kendinden emin ve yanlış bir madde numarası sessizlikten kötüdür. `HakHukuk-4B`
bu işin iki yarısı için de eğitildi: cevabı verilen mevzuata **dayandır**, mevzuat soruyu
kapsamıyorsa **çekin**.

## Kurulum

Üç bileşen de yayımlanmıştır: ağırlıklar, arama indeksi ve kod. Konteyner yolu bağlayıcı
sunucu bayraklarını **zorlar** — elle kurulumda bunları kendiniz yazmanız gerekir.

```bash
git clone https://github.com/Rfetha/HakHukuk && cd HakHukuk
docker compose up          # API 127.0.0.1:8000 · llama-server 127.0.0.1:8080
```

`indir` kutusu GGUF'u ve indeksi **pinlenmiş revizyondan**, `sha256` + bayt kapısının
arkasından çeker; kapı tutmazsa **iki daemon da hiç başlamaz**. Gereksinim: NVIDIA GPU +
Docker (compose v2.30+).

Paket olarak:

```bash
pip install -e .
hakhukuk "Askerlik nedeniyle iş sözleşmesi ne olur?"   # komut satırı
hakhukuk-tui                                           # tek ekran arayüz
hakhukuk-api                                           # HTTP API
```

Ağırlığı tek başına indirmek için:

```bash
hf download Rfetha/HakHukuk-4B-GGUF HakHukuk-4B-v0.3-Q4_K_M.gguf --local-dir models/gguf
```

⚠️ **Model tek başına bildirilen sayıyı üretmez.** Manşet, erişim katmanı **açıkken**
ölçülmüştür; kaynaksız koşulda model yüksek güvenle yanlış hukuki içerik üretir.

## Manşet sayılar

DEV kümesi, `n=80` · erişim katmanı açık (`k=10`) · önsözsüz · seed 3407 · bütçe 1536.

| eksen | değer |
| :--- | ---: |
| **sadık-cevap kütlesi** | **%69,4-80,1** |
| `recall@10` (kütlenin tavanı) | 0,9500 |
| uydurulmuş madde numarası | **0 / 114** |
| aşırı çekinme (altın bağlamdayken sustu) | 4 / 80 |
| isabetsiz atıf | 8 / 80 |
| VRAM (ctx 4.096) · cevap bedeli | 3,09 GiB · **$0** |

⚠️ **Manşet tek sayı değil, koşulsuz bir aralıktır:** iki bağımsız hakem ailesi aynı 80 cevabı
puanladı ve sonuç **0,8011 ↔ 0,6940** çıktı. Manşeti sonuca göre biçimlendirmek (kapı geçince
tek sayı, emin olmayınca aralık) bu projenin reddettiği bir kendini-kandırma kalıbıdır.

Rakip karşılaştırması, ölçüm rejimi, eksen tanımları, sınırlar ve **kurulmayan cümleler**:
[**MODEL_CARD.md**](MODEL_CARD.md).

## Ne vaat **etmiyor**

- **Hukuki tavsiye değildir.** Ürettiği her madde numarası
  [mevzuat.gov.tr](https://www.mevzuat.gov.tr) üzerinden doğrulanmalıdır.
- **%100 doğruluk değildir.** 80 soruda 8 isabetsiz atıf ve 4 aşırı çekinme ölçüldü.
- **Güncellik ağırlıkta değil, kütüphanededir.** Mevzuat değişir, ağırlıklar değişmez.
- **Kapsam: yalnız yürürlükteki TC kanunları** (892 kanun, 40.496 madde; 2026-08-06 anlık
  görüntüsü). Yönetmelik, tüzük, KHK ve tebliğ kapsam dışıdır.
- **Parite iddiası yok.** Kıyas DEV'de, maliyet normalize edilmeden yapıldı.

## Sürümleme — üç numara, birbirinin yerine geçmez

| numara | bugün | neyi adlandırır |
| :--- | :--- | :--- |
| artefakt | `HakHukuk-4B-v0.1` | ağırlıkların kendisi; **kalıcı** |
| dosya | `HakHukuk-4B-v0.3-Q4_K_M.gguf` | içerik değişmediği için **adı da değişmez** |
| ürün / iddia | **`v1.0`** | ölçüm aygıtının ulaştığı doğrulama düzeyi |

⚠️ **`v1.0` "model iyileşti" demez** — ağırlıklar hiç değişmedi. Kapanan şey, sürüm kapısının
üç maddesinin **ikinci, bağımsız bir hakem ailesi altında da** geçmesidir
([ADR-0084](docs/adr/kararlar-0064-0085.md#adr-0084)).

## Repo haritası

| yer | ne |
| :--- | :--- |
| [`hakhukuk/`](hakhukuk/) | **ürün paketi** — istem · servis · CLI · TUI · HTTP API · indirici |
| [`scripts/`](scripts/) | **ölçüm aleti**, üründen bilinçli olarak ayrı |
| [`docs/record/`](docs/record/) | araştırma kaydı, kronolojik — **#71**'e kadar |
| [`docs/adr/`](docs/adr/) | karar defteri — **0085**'e kadar |
| [`docs/record/kollar.md`](docs/record/kollar.md) | artefakt sicili. *Satırı olmayan artefakt isimsizdir.* |
| [`docs/record/yurutme-tuzaklari.md`](docs/record/yurutme-tuzaklari.md) | *"hata vermeden yanlış sayı üretir"* kalıpları — her biri fiilen ısırdı |
| [`outputs/eval/`](outputs/eval/) | ham ölçüm çıktıları ve koşu künyeleri |
| [`tests/`](tests/) | `pytest` — **335 passed, 2 xfailed** |

## Araştırma kaydının kendisi bir değer

**Negatif bulgular birinci sınıftır.** Bu depoda kendi ön-kayıtlı kapısına takılan koşular,
ölçüm çeliştiği için **tersine çevrilen** bir karar
([ADR-0052](docs/adr/kararlar-0045-0063.md#adr-0052)) ve **düşmüş** bir ara kapı
([ADR-0045](docs/adr/kararlar-0045-0063.md#adr-0045)) damgalı olarak durur.

Sayılar **hatırlanmaz, kaynaklanır**: her sonucun metriği, `n`'i, hakemi, seed'i ve çıktı
dosyası koşu künyesinde (`KUNYE.json`) sabitlenmiştir.

## Veri ve lisans

Kaynaklar yalnız kamuya açık ve lisansı uygun olanlardır: mevzuat.gov.tr · Resmî Gazete ·
Yargıtay açık portalı · açık lisanslı veri setleri · gerçek mevzuat metninden üretilip
**doğrulanmış** sentetik çiftler. Eğitim verisinde PII maskelenir.
Veri planı: [`docs/VERI_PLANI.md`](docs/VERI_PLANI.md).

**Lisans: Apache-2.0** ([`LICENSE`](LICENSE)) — ağırlık, kod, veri ve araştırma kaydı.
Base model `Qwen/Qwen3.5-4B` Apache-2.0'dır; atıf zinciri [`NOTICE`](NOTICE) dosyasındadır.

## Katkı

Katkı, eleştiri ve **yeniden üretme denemeleri** — özellikle yeniden üretme denemeleri —
memnuniyetle karşılanır. Bir sayıyı yeniden üretemiyorsanız bu bir hata raporudur.
