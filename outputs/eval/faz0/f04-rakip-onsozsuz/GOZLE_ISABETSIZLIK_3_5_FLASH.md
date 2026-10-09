# F0.4 — `gemini-3.5-flash` · 80 kalemde İSABETSİZLİK (gözle tam tarama)

**Tarih:** 2026-09-07 · **dosya:** `h1_3_5_flash_nb_detail.jsonl` · **n = 80/80** (örneklem değil)
⭐ **Neden bu özne özel:** `v1.0` kapısının madde (1) eşiği bunun kütlesinden türetiliyor.
**Tanım:** [`f02/GOZLE_OKUMA_80.md`](../f02-biz-onsozsuz/GOZLE_OKUMA_80.md) §2 ile **birebir aynı**.

## 1 · İsabetsizlik — **8/80**

| id | altın | modelin dayandığı | gerçek mi | not |
| :-- | :--- | :--- | :--- | :--- |
| 10 | 6284/10 | **HMK 393** | ✅ | altın **gelmedi**; ihtiyati tedbirden cevapladı |
| 15 | TMK 398 | **TMK 450·440·444·454·464** | ✅ | 🟡 çekinceli cevap (altın 5. sırada) |
| 21 | TBK 99 | **VUK 215 + EURO K. 4·5·7** | ✅ | altın **gelmedi**; muhasebe/€ mevzuatı |
| 26 | İİK 62 | **AATUHK 58 + İİK 66** | ✅ | ⭐ altın **1. sırada**; kural doğru, **kanun yanlış** |
| 27 | KMK 33 | **KMK 26·25·22** | ✅ | 🟡 çekinceli; *"Madde 33'ün devamı yarım kaldı"* diyor |
| 29 | TKHK 49 | **TKHK 18 (+24)** | ✅ | kesik kalem |
| 34 | CMK 161 | **CMK 332 + Bankacılık K. 166 + HSK 116** | ✅ | ⭐ altın **0. sırada**, hiç anılmadı |
| 70 | TMK 241 | **AATUHK 62 + İİK 85** | ✅ | mal rejimi yerine icra/tahsilat |

**Altın bağlamdayken ıskalanan: 6/8.** Altın hiç gelmemişken komşu mevzuattan konuşan: 2/8.

## 2 · Çekinme — 9/80, ve **alet ↔ göz farkı 4**

| tür | id | n |
| :--- | :--- | ---: |
| aşırı-red (altın vardı, sustu) | 1·14·38·43·45·59·66 | **7** |
| doğru red (altın gelmedi) | 51·79 | 2 |

`exact_reject` **13** kalem işaretliyor. Fark, `KALIBRASYON_ve_OZET.md`'deki tuzağı **birebir** doğruluyor:

| aletin fazladan saydığı | göz hükmü |
| :--- | :--- |
| 15 · 24 · 27 | 🟡 **çekinceli cevap** — *"doğrudan madde yok, bununla birlikte…"* + tam gerekçeli atıflı cevap ⇒ **cevaptır** |
| 28 | ❌ **açık yanlış pozitif** — TBK 230'dan eksiksiz, doğru, atıflı cevap |

⇒ 13 − 2 = **11**, kalibrasyon notundaki *"alet 11"* ile aynı; göz ayrımı da **7 + 3 + 1** olarak tutuyor.

## 3 · Uydurulmuş madde — **0**

⚠️ Harness tablosundaki `"MADDE_YOK": 4` bir **ayrıştırma artefaktıdır**, uydurma değil: dördü de
eğik çizgili madde numarası (İİK **31/a · 79/a · 97/a · 149/b**), hepsi bağlamda **ve** korpusta var.

## 4 · Sınır durum — **1**, sayılmadı

**id 46** · altın KMK 53 ↔ model **KMK 14**. KMK 14 lafzen *"Kat mülkiyetine geçişte ayrıca yönetim
plânı istenmez"* diyor — **soruyu doğrudan karşılıyor**. Altın KMK 53 ise 1965 öncesi irtifak
haklarına dair bir **geçiş hükmü**. 🚨 Burada kusurlu olan modelden çok **altın etiketin kendisi**
olabilir. Sayılsaydı 9/80.

⭐ **Ayrıca:** id 32 · 41 · 62 · 69'da model **önce altın olmayan** maddeden konuşup **sonra altını
esaslı biçimde kullandı** ⇒ tanım gereği isabetli. ⚠️ **32 ve 41 bizim kolumuzda İSABETSİZ**di.

## 5 · Çivilenen sayılar

| eksen | **3.5 Flash** | (kıyas) **BİZ** |
| :--- | ---: | ---: |
| **isabetsizlik** | **8/80** | **8/80** |
| cevaplanan tabanda | 8/71 = **%11,3** | 8/75 = **%10,7** |
| çekinme | 9/80 | 5/80 |
| — aşırı-red | **7/80** | **4/80** |
| çekinceli cevap | **3** | **0** |
| uydurulmuş madde | 0 | 0 |
| alet ↔ göz farkı (çekinme) | **4** | **0** |
| sınır durum | 1 (id 46) | — |

🚨 **Bu tablodan KURULMAYACAK cümle:** *"İsabetsizlikte berabereyiz, o hâlde eşitiz."*
İki 8 **aynı tanımla** sayıldı ama **aynı tabanla değil**: Flash 9 kalemde sustuğu için **71**
kalemde sınandı, biz **75**'te. Ayrı yön: bizim kolda **çekinceli cevap ve alet-göz farkı sıfırken**,
bu kolda ölçüm aracının kendisi **4 kalemde** yanılıyor.
