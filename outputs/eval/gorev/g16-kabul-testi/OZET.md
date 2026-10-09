# G16 — `v1.0` KABUL TESTİ · ⛔ DONMUŞ TEST AÇILDI (tek kez, insan onaylı)

**Tarih:** 2026-09-09 · **veri:** `data/eval/canon/core_hard.jsonl` **n=40** ⛔ donmuş ·
özne `tgta_v1` = `HakHukuk-4B-v0.1` · taşıyıcı `llama-server` YEREL ·
seed 3407 · k=10 · 900 klip · bütçe **1536** (think 1024 + cevap 512) · **önsözsüz** ·
⛔ **ARAÇSIZ** (ADR-0076 m.4 — rakipler araç kullanamaz, eşit sınav) ·
hakem `openai/gpt-4o-mini` · `judge_cost_usd` **$0,0195**

Rejim künyesi DEV koşusunun (`f02-biz-onsozsuz/KUNYE.json`) **her ekseninde birebir aynı**.

## ✅ Geçerlilik kapısı (ADR-0040)

| | değer | eşik | sonuç |
| :--- | ---: | ---: | :--- |
| kesik cevap | **1/40 = %2,5** | > %5 → GEÇERSİZ | ✅ **GEÇTİ** *(DEV tam eşikteydi: %5,0)* |
| düşünce kanalı kullanan | 40/40 | — | — |
| zorla kapatılan `</think>` | 3/40 | — | künyeye yazıldı |

## 📊 MANŞET — ham kütle (ADR-0069 m.1: bağlayıcı sayı budur)

# **kütle = 0,5804**

⚠️ **Yanına ZORUNLU olarak (ADR-0069 m.3):**

| | **TEST** (40) | **DEV** (80) |
| :--- | ---: | ---: |
| **ham kütle** | **0,5804** | **0,8011** |
| `recall@10` = **tavan** | **0,7500** | **0,9500** |
| **tavan kullanımı** = kütle ÷ `recall@10` | **0,7739** | **0,8433** |
| coverage | 0,7750 | 0,9375 |
| `A1_cevaplanan` | 0,7489 | 0,8545 |
| `A1_altın_getirilen_alt_küme` | 0,7927 | 0,8902 |

⚠️ **ADR-0069'un formülü ile örneği çelişiyor, damgalanır:** karar metni oranı
`kütle ÷ recall@10` diye tanımlıyor, ama kendi örneğinde `0,730 ÷ **0,9375**` yazıyor —
0,9375 DEV'in **coverage**'ıdır, `recall@10` (0,9500) değil. Burada **tanımdaki formül**
kullanıldı. Coverage paydasıyla: TEST **0,7489** ↔ DEV **0,8545** (fark aynı yönde, −10,56 p).
⛔ ADR'ye dokunulmadı (`docs/adr/**` değiştirilmez); çelişki burada ve planda yazılı.

## 🚨 Düşüşün ayrıştırılması — tavan ne kadarını açıklıyor

```
DEV kütle                                        0,8011
TAVAN-EŞDEĞER BEKLENTİ (0,8433 × 0,7500)         0,6324
TEST kütle (ölçülen)                             0,5804
```

| | puan | pay |
| :--- | ---: | ---: |
| toplam düşüş | **−22,07 p** | %100 |
| **tavanın açıkladığı** (bileşim farkı, ADR-0069) | **−16,87 p** | **%76** |
| **tavanın AÇIKLAMADIĞI** | **−5,20 p** | **%24** |

⇒ ADR-0069'un öngörüsü **doğrulandı ama tam değil**: düşüşün dörtte üçü setin erişim
tavanından geliyor, **dörtte biri gelmiyor.** Model görülmemiş veride tavanını **daha kötü**
kullanıyor (0,7739 ↔ 0,8433). Bu sayı süslenmedi ve *"hepsi bileşim"* denmedi.

## Eksen eksen · DEV ↔ TEST (Wilson %95, S5)

| eksen | TEST | DEV | not |
| :--- | ---: | ---: | :--- |
| coverage | 0,7750 **[0,625–0,877]** | 0,9375 **[0,862–0,973]** | aralıklar **örtüşmüyor** |
| `recall@10` | 0,7500 **[0,598–0,858]** | 0,9500 **[0,878–0,980]** | tavan farkı |
| **aşırı-red** *(altın bağlamdaydı, sustu)* | **5/40 = 0,1250** [0,055–0,261] | **4/80 = 0,0500** [0,020–0,122] | ⚠️ **aralıklar ÖRTÜŞÜYOR** — *"iki katına çıktı"* **nokta tahmindir** |
| **uydurulmuş madde no** | **0/52** | **0/114** | ✅ **korundu** |
| mülga atıf | **0** *(aletin ham çıktısı 2 idi — alet onarıldı, aşağıda)* | 0 | |
| `cit_precision_micro` | 0,7576 | 0,9231 | ⚠️ geriledi |
| `wrong_ref_rate_micro` | **0,2424** | 0,0769 | 🚨 **3,2× kötü** — B1 |
| `cit_recall_macro` | 0,6500 | 0,9000 | ⚠️ geriledi |
| kapı (üç politika) | 40/40 geçti, `atifsiz_gecen` **10** | 80/80, `atifsiz_gecen` 7 | |

## ✅ Gözle okuma — ADR-0064 madde (*) kapısı

Aletin işaretlediği **9/40 çekinmenin dokuzu da tek tek okundu**: dokuzu da gerçek çekinme,
**açık yanlış pozitif 0**. ⇒ ALET = GÖZ; kütle üç okumada da **0,5804**.
*(Kıyas: Sonnet-5 kolunda 8 çekinmenin 3'ü yanlış pozitifti. Alet bizim ailemizde doğru,
başka ailelerde değil — F0.4'ün bulgusu TEST'te de sürüyor.)*

Beşi altın bağlamdayken sustu (id **9 · 13 · 16 · 22 · 38**), dördünde altın zaten gelmemişti.

## 🚨 DONMUŞ TEST'İN YAKALADIĞI KUSUR — atıf doğrulayıcı, `atif_dogrula.py`

Alet önce **MÜLGA 2** raporladı. Okunduğunda tek kalemden (id 32) geldiği görüldü:
altın `İŞ KANUNU (4857) Madde 111`, 1. sırada getirilmiş, model doğru cevaplamış ve
*"İş Kanunu Madde 111"* diye **kanun numarasız** atıf yapmış. Korpusta bu ada **iki** kanun
uyuyor: **4857** (yürürlükte) ve **1475** (mülga). `dogrula()` adayları `sorted()` ile
**alfabetik** geziyor ve ilk taşıyanı döndürüyordu ⇒ **1475** kazanıyor, DOĞRU cevap
**MÜLGA** damgası yiyordu. Vatandaşa gidecek rozet buna bağlı.

⛔ Kodun kendi ilkesi (*"yürürlükte tek satır bile varsa mülga sayılmaz"*) tek bir `kanun_no`
**içinde** uygulanıyordu; **adaylar arasında** uygulanmıyordu. Düzeltme o ilkeyi bir seviye
yukarı taşır — ölçüt değişmedi, **alet düzeltildi** (ADR-0050).

- Test önce yazıldı, **kırmızı görüldü** (`MULGA ≠ DOGRULANDI`), sonra kod yazıldı.
- **Manşet sayı DEĞİŞMEDİ** (kütle = coverage × A1; ikisi de bu doğrulayıcıdan gelmez) ⇒
  düzeltme *"sayıyı güzelleştirmek"* değildir.
- **Geçmiş hiçbir yayımlanmış sayı oynamadı:** DEV kolu 114 DOGRULANDI (aynı), Sonnet-5 kolu
  161 + 2 `MADDE_YOK` (aynı).
- TEST atıfları: `DOGRULANDI` **50 → 52** · `MULGA` **2 → 0**.

## ⛔ HÜKÜM KURULMADI — ön-kayıtlı sayısal kabul eşiği YOK

Bu bir bulgu, bir mazeret değil:

- **ADR-0064 madde (1)** eşiği `3.5 Flash − 2,0 p`. O çıpa **DEV**'de ölçüldü; rakipler
  donmuş TEST'te **hiç koşmadı** ⇒ eşik TEST'te mekanik olarak **türetilemiyor**.
- **ADR-0069 m.3** açık: *"tavan kullanımı **KAPI DEĞİLDİR**"* ve *"rakip kıyas cümlesi bu
  orandan **KURULMAZ**"*.
- **Plan Adım 3** yalnız *"geçerse `v1.0`"* diyor; **"geçmek"in tanımı hiçbir yerde yazılı değil.**

⇒ Sayıyı gördükten sonra eşik yazmak, ADR-0050'nin engellemek için var olduğu şeydir.
**`v1.0` hükmü İNSAN KARARIDIR** ve bu belge kararın önüne sayıyı ham hâliyle koyar.

## Ne KURULMAZ

- ⛔ **Rakip kıyası bu koşudan kurulmaz.** Rakipler TEST'te koşmadı; kıyas DEV'de, eşit sınavda.
- ⛔ **Tavan kullanımı bir kapı değildir** (ADR-0069 m.3).
- ⛔ **DEV 0,8011 ile TEST 0,5804 aynı metrik değildir** — tavanları farklı, yan yana konurken
  bu damga zorunlu.
- ⚠️ Hâlâ **tek hakem ailesi** (`gpt-4o-mini`); κ 0,534 ile aracın 0,6 eşiğinin **altında**
  (ADR-0074). n=40'ta Wilson aralıkları geniş.
