# F0.7 — M5 çekinme sınıflandırmasının GÖZLE OKUNMASI (kapı adımı)

**Tarih:** 2026-09-07 · **koşular:** `m5_tgta_v1_m5_dry` · `m5_base_m5_dry` (DRY rejimi, ADR-0073)
**Neden kapı:** ADR-0064 madde (*) — *"her sayım adımında gözle okuma zorunlu"*. `coverage`
doğrudan çekinme sınıflandırmasından türüyor; `ezber kütlesi = coverage × A1` olduğu için
dedektörün her hatası **kapı maddesine** taşınır.

## Alet ne dedi

| kol | `exact_reject` çekinme dedi |
| :--- | ---: |
| BİZ (`tgta_v1`) | **4**/80 (id 13 · 37 · 57 · 59) |
| base (Qwen3.5-4B) | **2**/80 (id 13 · 16) |

## 🚨 Göz ne dedi: **ALTISI DA ÇEKİNME DEĞİL** — yanlış pozitif 6/6

Altı kalemin tamamı **hukuki bir OLUMSUZ HÜKÜM** kuruyor ve **atıf yapıyor**; yani
*"cevap veremem"* demiyor, *"böyle bir hüküm yok"* diyor. Bu bir **cevaptır** — üstelik
çoğu **yanlış** cevaptır, ki M5'in ölçmek istediği tam olarak budur.

| kol | id | altın | modelin dediği | neden çekinme DEĞİL |
| :-- | :-- | :--- | :--- | :--- |
| BİZ | 13 | TMK 313 | *"…belirli süre bakım gerektiği bir hüküm **bulunmamaktadır**"* + TMK atfı | olumsuz hüküm + atıf |
| BİZ | 37 | TMK 398 | *"…aile meclisi kurulması zorunlu değil… **503. madde**"* | cevap **ve yanlış madde** |
| BİZ | 57 | 6284 m.11 | *"…özel nitelik listesi bulunmamaktadır; ancak…"* + 1141 karakter gerekçe | uzun, gerekçeli cevap |
| BİZ | 59 | TKHK 56 | *"…doğrudan bir liste şeklinde belirtilmemiştir. Ancak…"* | olumsuz hüküm + devamı |
| BASE | 13 | TMK 313 | *"…**belirli bir süre bakım şartı** bulunmamaktadır"* + *"Aile Kanunu (6284)"* | cevap, **kanun adı uydurulmuş** |
| BASE | 16 | HMK 436 | *"Karşı oy yer almaz… **4711 Sayılı Türk Hakemlik Kanunu** 33. madde"* | kendinden emin cevap, **kanun uydurulmuş** |

**Tetikleyen kalıp:** `REJECT_RE`'nin *"bulunmamaktadır / belirtilmemiştir"* ailesi. Bu ibare
**hukuk metninde iki farklı iş görür**: (a) *"kaynakta yok, cevaplayamam"* = çekinme,
(b) *"kanunda böyle bir hüküm yok"* = **esasa ilişkin cevap**. Kör modda **kaynak yoktur**,
dolayısıyla (a) okuması **tanımı gereği imkânsızdır** — geriye yalnız (b) kalır.

## Sayıya etkisi — İKİ OKUMA DA RAPORLANIR

| kol | okuma | `coverage` | `A1` | **ezber kütlesi** |
| :--- | :--- | ---: | ---: | ---: |
| BİZ | ALET | 0,9500 | 0,4105 | **0,3899** |
| BİZ | **GÖZ** | **1,0000** | 0,4057 | **0,4057** |
| base | ALET | 0,9750 | 0,4818 | **0,4697** |
| base | **GÖZ** | **1,0000** | 0,4739 | **0,4739** |

### Madde (3) hükmü — okumadan BAĞIMSIZ

```
ALET  coverage 0,9500 ≤ 0,9750 ✅   ezber kütlesi 0,3899 ≤ 0,4697 ✅  (−7,98 p)
GÖZ   coverage 1,0000 ≤ 1,0000 ✅   ezber kütlesi 0,4057 ≤ 0,4739 ✅  (−6,82 p)
```

⭐ **Hüküm dedektöre bağımlı değil.** Kusur iki kolu da **aynı yönde** etkiliyor; ADR-0057'nin
eşit sınavı burada koruyucu görev görüyor. ⇒ 🟢 **MADDE (3) GEÇTİ.**

## Bulgu: `suskunluk_terazisi` ÜÇÜNCÜ kez yanıldı — ilk kez KÖR modda

| # | ne zaman | nerede | yanlış pozitif |
| :-- | :--- | :--- | :--- |
| 1 | 2026-09-06 | **bizim** şablonumuz, önsözsüz rejim (ADR-0061) | 14 → göz 8 |
| 2 | 2026-09-06 | **Gemini** şablonu, F0.4 kalibrasyonu | 11 → göz 7 |
| 3 | **2026-09-07** | **kör mod**, iki kol birden | **6 → göz 0** |

Üçünde de yön aynı: **alet fazla red sayıyor**. Ve üçü de ancak **gözle okununca** görüldü.
⇒ Aletin adının *"terazi"* olması tesadüf değil: **tek kefe hüküm vermiyor.**

## 🆕 Açık borç — `exact_reject`'in kör moddaki dalı

ADR-0044 kör mod için **feragat cümlesini** çıkarıyor (`DISCLAIMER_RE`), ama
*"…bulunmamaktadır"* ailesini çıkarmıyor. Kör modda **kaynak olmadığı için** *"kaynakta yok"*
okuması imkânsız ⇒ bu ailenin kör modda red sayılması **tanım gereği yanlıştır**.
⛔ **Bugün DÜZELTİLMEDİ:** aleti kapının sayısını ürettikten sonra değiştirmek, ADR-0050'nin
yasakladığı hareketin sınırında durur. Doğru sıra: **ölç → iki okumayı da raporla → aleti
sonraki turda, koşudan ÖNCE düzelt.** Bugün yapılan budur.
