# F1.1 — BASE (Qwen3.5-4B) harness AÇIK · 8 eksen

**Tarih:** 2026-09-07 · **özne:** `Qwen3.5-4B` base (ince ayar YOK) ·
**taşıyıcı:** YEREL `llama-server` 0cea362, RTX 5070 Ti Laptop, ŞARJDA, 40 dk 21 s, **$0** ·
**hakem:** `openai/gpt-4o-mini` (OpenRouter, `LLM_PROVIDER_ORDER=OpenAI`), **$0,0511** ·
**kaynak:** `outputs/eval/f11-base-harness-butce2048/`

> # ⚠️ EŞİT SINAV DEĞİL — bütçe 2048 ↔ 1536
> Base bu koşuda **2048** token üretim bütçesi aldı (düşünce 1024 + cevap 1024).
> BİZ ve üç rakip **1536** ile koştu (ADR-0070 tek formülü).
> ⛔ Aşağıdaki hiçbir hücreden *"ince ayar şu kadar kazandırdı"* cümlesi **kurulamaz** —
> fark ince ayardan mı bütçeden mi **ayırt edilemez** (ADR-0057).

---

## Sekiz eksen

> ### ⚠️ EŞİT SINAV DEĞİL — bütçe 2048 ↔ 1536

| # | eksen | **BASE** (bütçe 2048) | **BİZ** `tgta_v1` (1536) | **3.5 Flash** (1536) | eşit mi? |
| :-- | :--- | ---: | ---: | ---: | :--- |
| 1 | **kütle** (`kutle_tum`) | **0,6685** | 0,8011 | 0,6925 | ❌ bütçe |
| 2 | **coverage** | **0,7875** | 0,9375 | 0,8375 | ❌ bütçe |
| 3 | **A1 · cevaplanan** | **0,8489** | 0,8545 | 0,8269 | ❌ bütçe |
| 4 | **A1 · altın getirilen** | **0,8593** | 0,8902 | 0,8523 | ❌ bütçe |
| 5 | **recall@10** | **0,9500** | 0,9500 | 0,9500 | ✅ **BİREBİR** |
| 6 | **aşırı-red** (altın bağlamda sustu) | **14/80** | 4/80 | 11/80 | ❌ bütçe + alet |
| 7 | **uydurulmuş madde** | **4** `MADDE_YOK` (+1 `KANUN_YOK`, 4 `AYRIŞTIRILAMADI`) / 170 doğrulanan | 0 / 114 | 4 / 133 | ❌ bütçe |
| 8 | **token / cevap** | **2354,3** | 782,5 | 699,4 | ❌ **eksenin KENDİSİ bütçe** |

**Tek eşit eksen `recall@10`'dur** ve o da 0,9500'de üç kolda birebir aynı — harness oynamadı,
üç koşu da aynı bağlamı gördü. Kalan yedi eksen **CEILING/TANIMSIZ** damgası taşır.

**Eksen 8 özel olarak okunamaz:** token/cevap doğrudan bütçenin fonksiyonudur. 2354,3 ↔ 782,5
farkı bir model özelliği değil, **koşu ayarının kendisidir**.

---

## Geçerlilik kapıları

| kapı | değer | eşik | hüküm |
| :--- | ---: | ---: | :--- |
| kesik cevap (ADR-0040) | **3/80 = %3,8** | %5 | ✅ **GEÇTİ** |
| düşünce kanalı kullanıldı | 80/80 | >0 | ✅ GEÇTİ |
| `recall@10` sapması | 0,9500 | 0,9500 | ✅ BİREBİR |

**Önceki koşu neden düştü:** `outputs/eval/f08-base-harness/` — aynı rejim, bütçe **1536**,
kesik **16/80 = %20,0** ⇒ ADR-0040 gereği **GEÇERSİZ**, puanlanmadı, künyesi yok.
16 kesiğin 15'i gerçek kesilme, 1'i döngü (insan sınıflaması) ⇒ **DRY işe yaramaz, sebep bütçe.**
Çapraz kontrol: base **kör** modda yalnız 2/80 kesik veriyor ⇒ şişiren şey **kaynakların kendisi**.

---

## 🚨 Kapı değil, BULGU: base düşünmeyi bitirmiyor

| kol | `forced_close` (`</think>` ZORLA kapatıldı) | ort. completion token |
| :--- | ---: | ---: |
| **BASE** (2048) | **76/80** | 2354,3 |
| BİZ `tgta_v1` (1536) | 3/80 | 782,5 |
| 3.5 Flash (1536) | 0/80 | 699,4 |

`research_log` #42'nin *"base `</think>`'i kapatmıyor"* mekanizması **harness AÇIK'ta da geçerli**.
Pratik sonucu: `MAXTOK`'u büyütmek 1. geçişin tavanını da 1536→2048 büyütür ve base o tavanı
**her seferinde yakar** ⇒ büyüyen yalnız cevap payı değil, 2. geçişe yapıştırılan **düşünce izi**
de uzadı. *"Yalnız cevap bütçesi büyüdü"* cümlesi bu yüzden **yanlıştır**.

---

## Bu belgeden KURULMAYAN cümleler

1. ⛔ **"İnce ayar şu kadar kazandırdı."** Bütçe farkı ayırt edilemez kılıyor.
2. ⛔ **"Base bütçe kayrılmasına rağmen geride."** Sapmanın **işareti ölçülmedi**. Karşı kanıt
   aynı zincirde var: F0.4'te 3.5 Flash-Lite **171,1** token/cevap harcayıp GÖZ-katı **0,7622**,
   3.5 Flash **699,4** harcayıp **0,7425** aldı — token harcaması bu kümede skoru **yordamıyor**.
3. ⛔ **"Base'in 1536'daki skoru şudur."** O koşu geçersiz; puanlanmadı, sayısı **yok**.
4. ⛔ **"Aşırı-red 14/80'dir."** Bu **alet** sayısı. Red dedektörü Qwen-base şablonunda
   **gözle kalibre edilmedi** — F0.4'te üç Gemini kolunda 28 kalem okunmuş ve alet **sistematik
   fazla red** saymıştı. Aynı sınıf hata burada da olabilir ve **eksen 2 ile 6'yı doğrudan** vurur.
5. ⛔ **"TEST'te de böyledir."** Ölçüm **DEV**'de.

## Açık borç

- **B-f11.1** — base'in 17 çekinmesinin **gözle okunması** (F0.4'ün 28-kalem emsali). Yapılmadan
  eksen 2 ve 6 alet-sayısıdır.
- **B-f11.2** — eşit sınav istenirse **tek yol**: BİZ + üç rakibi de 2048'de yeniden koşmak.
  Base'i 1536'ya indirmek işe yaramaz — orada kapıdan düşüyor (%20).
