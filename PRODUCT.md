# HakHukuk — ürün tanımı

> **Bir vatandaşın gerçekten sorabileceği hukuk danışmanı.** Açık kaynak, Apache-2.0;
> ağırlıklar + kod + veri + **araştırma kaydının tamamı** yayında.
> Her sayının yanında **kaynak dosya adı** vardır; hiçbir sayı hatırlanarak yazılmamıştır.

## Kim için

Hukukçu **değil**. Kanun metnini açtığında ne dediğini anlamayan, "bu benim durumumda ne
demek" diye soran kişi. Onun sorusu şuna benziyor:

> *"Askerlik nedeniyle işten ayrılırsam sözleşmem ne olur?"*
> *"Kat malikleri kurulu hangi çoğunlukla karar alır?"*
> *"Aldığım ürün ayıplı çıktı, hangi haklarım var?"*

Cevap şuna benziyor — **dayanağı gösterilmiş**, uydurmayan, bilmediğinde susan bir metin:

```
✅ CEVAP — dayanağı getirilen kaynaklarda

Muvazzaf askerlik ödevi dışında manevra veya herhangi bir sebeple silâh altına alınan
işçinin iş sözleşmesi, bu süre boyunca askıda kalır. …

Atıflar:
  ✓ 4857/Madde 31

Kaynaklar:
  [1] İŞ KANUNU Madde 31
  …

⚖️  Bu yanıt hukuki tavsiye değil, bilgilendirme amaçlıdır. …
```

## Ne yapar

| | nasıl | kaynak |
| :--- | :--- | :--- |
| Soruyu **mevzuata bağlar** | hibrit BM25 + `bge-m3`, RRF füzyon (`RRF_K=10`) | [ADR-0068](docs/adr/) · `recall@10` **0,9500** ([`harness_tablo.json`](outputs/eval/f02-biz-onsozsuz/harness_tablo.json)) |
| **Uydurmaz** | atıflar getirilen kaynağa karşı deterministik doğrulanır | uydurulmuş madde **0/114** ↔ rakipler 1 · 4 · 4 ([`KUNYE.json`](outputs/eval/f02-biz-onsozsuz/KUNYE.json)) |
| **Bilmediğinde susar** | dört durum ayrı: cevap · çekinceli · suskunluk · kesik | `hakhukuk/terazi.py` · aşırı-red **4/80** ([`GOZLE_OKUMA_80.md`](outputs/eval/f02-biz-onsozsuz/GOZLE_OKUMA_80.md)) |
| **Yürürlükten kalkmışı göstermez** | mülga madde süzgeci varsayılan | sızıntı **2 → 0**, `recall@10` değişmedi ([#64](docs/record/)) |
| **Tüketici donanımında çalışır** | GGUF Q4_K_M, 2,59 GiB; harness GPU'ya **girmez** | [ADR-0071](docs/adr/kararlar-0064-0085.md#adr-0071) |

**Bugünkü manşet:** faithful-answer **kütle %69,4-80,1 aralığı** (`claude-sonnet-5` ↔
`gpt-4o-mini`, ADR-0084) — GÖZ-katı, bağlayıcı okuma **%80,1**'dir
(`outputs/eval/f02-biz-onsozsuz/KUNYE.json`).

## Ne VAAT ETMEZ

Bunlar eksiklik listesi değil, **ürünün sınırı**:

1. **Hukuki tavsiye değildir.** Avukat değildir; çıktısı bir iddiadır, karar değil. Gerçek bir
   mesele için nitelikli bir avukata danışın. İbarenin **nihai hukuki metni** hâlâ açık
   (**S10**) — hukukçu görüşü bekliyor.
2. **%100 doğruluk değil.** Ölçülen kütle %80,1'dir; yani **beş cevaptan biri** dayanağıyla tam
   örtüşmüyor. Ayrıca *"gerçek ama soruya uymayan maddeden cevaplama"* (isabetsizlik) **8/80**
   ölçüldü ve bu **rakiplerden iyi değil** (8 ↔ 8 ↔ 7 ↔ 8).
3. **Güncellik ağırlıkta değil, kütüphanededir.** Mevzuat değişir, ağırlıklar değişmez. Korpus
   bir **anlık görüntüdür**: `data/corpus/KUNYE.json` → **2026-08-06**, 892 kanun, 40.496 madde.
   **Yönetmelik · tüzük · KHK · tebliğ · genelge · CB kararı KAPSAM DIŞI.**
4. **Canlı mevzuat bağlantısı yok.** `bedesten.adalet.gov.tr` sözleşmesi doğrulandı (4/4) ama
   **ürün onu çağırmıyor** (borç B6; ayrıca TR IP şartı var). Tazelik boru hattı `v2`.
5. **Sayılar tek hakem ailesinin hükmü.** İkinci bir aile aynı 80 cevabı puanladığında kütle
   %80,1 → **%69,4** düştü (κ = 0,534, eşiğin **altında**). Bu düşüş kapı hükmüne girmiyor
   çünkü rakip kolu aynı hakemle puanlanmadı — ama **sayının hakem seçimine duyarlı olduğu
   ölçülmüştür**. [ADR-0074](docs/adr/kararlar-0064-0085.md#adr-0074)
6. **Tek boyut, tek kuantizasyon.** Bir ~4B modeli, bir `Q4_K_M` artefaktı. *"Daha büyüğü daha
   iyi olur mu"* ve *"kuantizasyonun bedeli nedir"* **ölçülmedi** (ADR-0018'in eğrisi yok).

## `v1` ↔ `v2` sınırı

| | `v1` — **SFT** modeli | `v2` — **RL** modeli + uygulama |
| :--- | :--- | :--- |
| eğitim | ham base → SFT (`τ_g`) + ORPO (`τ_a`) → ham TIES merge | `tgta_v1` **yeni başlangıç** → GRPO + düşünce ayarı |
| ne | ağırlıklar + kod + veri + araştırma kaydı, **uçtan uca çalışır** | daha güçlü model + API/servis |
| arayüz | `hakhukuk "soru"` (CLI) · `hakhukuk-tui` — **yeterli** (insan kararı) | HTTP API, web (**S9 açık**) |
| araçlar | 5 **deterministik** kaldıraç, istem katmanında ([ADR-0076](docs/adr/kararlar-0064-0085.md#adr-0076)) | araç kullanımının **eğitimi** (GRPO ödülü) |
| erişim | yerel indeks, anlık görüntü korpus | canlı `bedesten` (B6) · tam kapsam · tazelik |
| durum | bu turda | sonra |

**Çizgi [ADR-0075](docs/adr/kararlar-0064-0085.md#adr-0075) ile çekildi (2026-09-08):**
`v1` **SFT ile kapanır** — `B1`/`B4` eğitim turları koşulmaz. `v2` **sequential RL**'dir,
task vector değil ⇒ ADR-0027'nin merge hattı `v1`'de **dondurulur**.
`v2`'yi mümkün kılan şey: **doğrulanabilir ödül** zaten yazılmış (`hakhukuk/terazi.py` atıf
doğrulaması deterministik) ⇒ reward model gerekmiyor.

## Sürüm şeması — ürün ve iddia AYRI

[ADR-0065](docs/adr/kararlar-0064-0085.md#adr-0065): *ürün sürümü* kullanıcının eline geçen şeyi,
*iddia sürümü* hangi ölçümün savunulduğunu sayar. İkisi birlikte hareket etmez.

| | bugün | koşulu |
| :--- | :--- | :--- |
| **ürün** | `v0.2` | uçtan uca çalışan CLI/TUI + yeniden üretim yolu |
| **iddia** | `v0.1` | **donmuş TEST kabul koşusu** — henüz koşulmadı |

## `v1.0` kapısı — üç madde

Ön-kayıtlı, [ADR-0064](docs/adr/). DEV'de üçü de **geçti**; `v1.0` yine de **verilmedi**, çünkü
donmuş TEST kabul koşusu koşulmadı.

| # | madde | DEV sonucu |
| :-- | :--- | :--- |
| 1 | kütle ≥ `3.5 Flash` − 2,0 p | **0,8011** ↔ eşik 0,7225 |
| 2 | isabetsizlik kötüleşmesin | çıpa 8/80'de yeniden çakıldı |
| 3 | M5 (ezber) yükselmesin | BASE'e göre **−6,82 p** |

Kabul testinin erişim tavanı DEV'in 0,95'i değil, **≈0,75**'tir
([ADR-0069](docs/adr/kararlar-0064-0085.md#adr-0069)) — ham kütle manşet olur,
tavan kullanımı **yanında** raporlanır, rakip kıyası o orandan **kurulmaz**.
