# F0.4 — Rakip çıpaları, ÖNSÖZSÜZ · dört özne, eşit sınav

**Tarih:** 2026-09-06 · **veri:** `data/eval/dev/core_hard.jsonl` **v2** (ADR-0067) ·
indeks `mevzuat_bge_m3_s2` · `RRF_K=10` (ADR-0068) · k=10 · seed 3407 · 900 klip ·
bütçe **1536, tek formül** (ADR-0070) · hakem `openai/gpt-4o-mini` (aile dışlaması: Google özne ↔ OpenAI hakem)

## Sınavın eşit olduğunun KANITI (varsayılmadı, ölçüldü)

| eksen | BİZ | 3.1 FL | 3.5 FL | 3.5 Flash |
| :--- | :--- | :--- | :--- | :--- |
| **`recall@10`** | **0,9500** | **0,9500** | **0,9500** | **0,9500** |
| **`context_shown`** | — | **80/80 bayt-bayt aynı** | **80/80** | **80/80** |
| istem | önsözsüz | aynı | aynı | aynı |
| bütçe | 1536 | 1536 | 1536 | 1536 |

## 🚨 ZORUNLU ÖN ADIM: red dedektörünün rakip ailelerde kalibrasyonu

`CLAUDE.md` kuralı: *"calibrate the refusal-detection regex on every competitor family."*
Bu adım yapıldı — **28 rakip çekinme kalemi tek tek gözle okundu** — ve dedektörün
Gemini şablonunda **sistematik olarak fazla red saydığı** bulundu:

| kol | alet | temiz çekinme | çekinceli cevap | **açık yanlış pozitif** |
| :--- | ---: | ---: | ---: | ---: |
| **BİZ** | 4 | **4** | 0 | **0** |
| 3.1 Flash-Lite | 8 | 5 | 0 | **3** — id 3 · 28 · 38 |
| 3.5 Flash-Lite | 9 | 5 | 2 | **2** — id 28 · 43 |
| 3.5 Flash (TAM) | 11 | 7 | 3 | **1** — id 28 |

Örnek (3.1 FL id 38): *"**Türk Ceza Kanunu'nun 235. maddesine göre** … cezalandırılır."* —
altın maddeden verilmiş **doğru cevap**, alet çekinme saymış.
⇒ **Üstünlüğümüzün bir kısmı aletin eseriydi.** Aşağıdaki tablo bunu düzeltiyor.

## Üç okuma altında kütle

| kol | ALET (ham) | GÖZ-orta *(yanlış pozitif düzeltildi)* | GÖZ-katı *(+çekinceli cevaplar da cevap)* |
| :--- | ---: | ---: | ---: |
| **BİZ (tgta_v1)** | **0,8011** | **0,8011** | **0,8011** |
| 3.1 Flash-Lite | 0,6746 | 0,7058 | 0,7058 |
| 3.5 Flash-Lite | 0,7174 | 0,7403 | 0,7622 |
| **3.5 Flash (TAM)** | 0,6925 | 0,7050 | 0,7425 |

*(BİZ üç okumada da aynı, çünkü kendi kolumuzda yanlış pozitif ve çekinceli cevap **yok** —
80 kalem gözle okundu, alet↔göz farkı sıfır.)*

## v1.0 kapısı madde (1) — ADR-0064 formülünden mekanik türetme

```
kütle ≥ 3.5 Flash'ın kütlesi − 2,0 puan
```

| okuma | Flash | eşik | BİZ | hüküm | fark |
| :--- | ---: | ---: | ---: | :--- | ---: |
| ALET | 0,6925 | 0,6725 | 0,8011 | ✅ **GEÇTİ** | +10,86 p |
| GÖZ-orta | 0,7050 | 0,6850 | 0,8011 | ✅ **GEÇTİ** | +9,61 p |
| **GÖZ-katı** (en muhafazakâr) | 0,7425 | 0,7225 | 0,8011 | ✅ **GEÇTİ** | **+5,86 p** |

⭐ **Kapı üç okumanın üçünde de geçiyor** — hüküm okuma seçimine bağlı değil.

## Diğer eksenler (ham alet sayıları)

| eksen | BİZ | 3.1 FL | 3.5 FL | 3.5 Flash |
| :--- | ---: | ---: | ---: | ---: |
| A1 · altın getirilen | **0,8902** | 0,7900 | 0,8449 | 0,8523 |
| **uydurulmuş madde** | **0** | 1 | 4 | 4 |
| doğrulanan atıf | 114 | 152 | 130 | 133 |
| kesik kalem | 4 (%5,0) | **5 (%6,2)** | 0 | 4 (%5,0) |
| ort completion token | 782,5 | 861,5 | **171,1** | 699,4 |
| tavan kullanımı (ADR-0069) | **0,8433** | 0,7101 | 0,7552 | 0,7289 |

## ⚠️ Bu tablodan KURULMAYAN cümleler

1. **"TEST'te de geçeriz."** Ölçüm **DEV**'de. TEST'in erişim tavanı ≈%75 (ADR-0069) ve
   kabul testi koşulmadı.
2. **Hakem panelinden geçmiş bir hüküm.** Hâlâ **tek aile** (`gpt-4o-mini`), κ yok,
   self-preference ölçülmedi. Bu, kapanmamış bir borç.
3. **3.1 FL için kesikliğe duyarlı hüküm.** %6,2 ile bizim kolumuzu düşüren eşiğin üstünde;
   ADR-0040 simetrik uygulanmalı (Ö-C emsali: kol düşürülmez, ortak kesiksiz alt kümede de raporlanır).
4. **"Model bu kadar iyileşti."** Kazancın büyük kısmı **eğitimden değil ölçümden** geldi:
   soru onarımı (+6,25 p recall), füzyon onarımı, bütçe eşitlenmesi. Model ağırlıkları
   **hiç değişmedi** — `tgta_v1` sabahki artefaktın aynısı.
