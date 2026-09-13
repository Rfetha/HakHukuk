# ADR-0077 — Kabul testi koştu; `v1.0` **VERİLMEDİ**, sürüm **`v0.3`**

**Tarih:** 2026-09-09
**Statü:** ✅ yürürlükte
**Karar:** model (insan *"tercih yok"* diyerek devretti — ⚠️ bu bir insan onayı **değil**,
delegasyondur ve insan tarafından **tersine çevrilebilir**)
**Bağlı:** [ADR-0064](0064-v1-kapisi-uc-maddeli-on-kayit.md) (kapının üç maddesi) ·
[ADR-0065](0065-bolunmus-surumleme.md) (bölünmüş sürümleme) ·
[ADR-0069](0069-kabul-testi-tavan-kullanimi-raporlamasi.md) (tavan kullanımı raporlaması) ·
[ADR-0074](0074-hakem-paneli-kuruldu-baglayici-hukum.md) (hakem paneli, κ) ·
[ADR-0050](0050-verim-kapisi-tahmin-edici-duzeltmesi.md) (alet düzeltilir, eşik oynatılmaz)
**Kaynak koşu:** `outputs/eval/g16-kabul-testi/` (`OZET.md` · `KUNYE.json`)

## Bağlam

Donmuş TEST (`data/eval/canon/core_hard.jsonl`, n=40) **2026-09-09'da açık insan onayıyla,
tek kez açıldı** ve kabul testi koştu. Rejim DEV koşusunun (`f02-biz-onsozsuz/KUNYE.json`)
her ekseninde birebir; araçsız (ADR-0076 m.4). Geçerlilik kapısı geçildi (kesiklik %2,5).

| | TEST (40) | DEV (80) |
| :--- | ---: | ---: |
| **ham kütle** *(manşet, ADR-0069 m.1)* | **0,5804** | 0,8011 |
| `recall@10` = tavan | 0,7500 | 0,9500 |
| tavan kullanımı | 0,7739 | 0,8433 |
| uydurulmuş madde no | **0/52** | 0/114 |
| `wrong_ref_rate_micro` | 0,2424 | 0,0769 |
| aşırı-red | 5/40 [0,055–0,261] | 4/80 [0,020–0,122] *(aralıklar örtüşüyor)* |

Düşüşün **%76'sı** setin erişim tavanından (ADR-0069'un öngörüsü), **%24'ü değil**.

## Sorun: donmuş TEST için ön-kayıtlı sayısal eşik YOK

- ADR-0064 madde (1)'in eşiği `3.5 Flash − 2,0 p`. Bu çıpa **DEV**'de ölçüldü ve rakipler
  donmuş TEST'te **hiç koşmadı** ⇒ eşik TEST'te **mekanik olarak türetilemez**.
- ADR-0069 m.3: tavan kullanımı **KAPI DEĞİLDİR** ve rakip kıyası ondan **kurulmaz**.
- Planın kendi cümlesi yalnız *"geçerse `v1.0`"* diyor; **"geçmek" tanımsız**.

⇒ Sayı görüldükten **sonra** eşik yazmak, ADR-0050'nin engellemek için var olduğu şeydir.
Bu ADR **eşik yazmıyor**; sürüm hükmünü **başka, zaten yazılı bir ölçüte** dayandırıyor.

## Karar

**`v1.0` VERİLMEZ. Yayımlanan sürüm `v0.3` olur.**

Gerekçe **ADR-0064'ün kendi metnidir**, yeni bir ölçüt değil. Orada `v1.0` için eksik olan
**iki** şey sayılıyor:

> *(a) donmuş TEST'in kabul testi koşmadı · (b) her sayı hâlâ tek hakem ailesinin hükmü*

- **(a) BUGÜN KAPANDI** — kabul testi koştu, sayısı yukarıda, ham hâliyle yayımlanıyor.
- **(b) AÇIK** — bağlayıcı hakem hâlâ **tek aile** (`gpt-4o-mini`); ADR-0074 κ'yı **ilk kez**
  ölçtü ve `tam_sadık` **0,534** · `atıf_temiz` **0,409** çıktı, aracın **0,6** eşiğinin
  **altında**. Üçüncü hakem (G2) insan kararıyla (bütçe) **atlandı**.

⇒ **`v1.0`'ı bloke eden şey model değil, ölçüm aygıtıdır.** Bu cümle küçültme değil: aynı
aygıt bugün de kendi kusurunu yakaladı (aşağıda).

`v0.2 → v0.3` yükselmesinin karşılığı, bugün ölçülmüş **iki ürün onarımı**:
`KUNYE` taşınabilirliği (indeks artık her makinede yüklenir) ve mülga rozeti kusuru.

## Bu koşunun tek başına haklı çıkardığı şey

Donmuş TEST **bir kusur yakaladı**: `atif_dogrula.py` çok anlamlı kanun adında adayları
`sorted()` ile geziyordu; `İŞ KANUNU` için ilk aday **1475 (mülga)** ve altın **4857/111**
1. sırada olmasına rağmen **doğru cevap MÜLGA damgası yiyordu**. Vatandaşa giden rozet buna
bağlı. TDD ile onarıldı (TEST atıf `DOGRULANDI` 50→52, `MULGA` 2→0).
⛔ **Manşet değişmedi** (kütle = coverage × A1; ikisi de bu doğrulayıcıdan gelmez) ve
**geçmiş yayımlanmış hiçbir sayı oynamadı** (DEV 114, Sonnet-5 161+2 aynı) ⇒ ADR-0050'nin
*"alet düzeltilir, eşik oynatılmaz"* kuralına uygun.

## Ne KURULMAZ

1. **"Model TEST'te kaldı."** Kalınacak bir eşik **yoktu**. Sayı düşük, sebebi %76 oranında
   setin bileşimi ve **rakip kıyası bu koşudan kurulmaz** (rakipler TEST'te koşmadı).
2. **"`v0.3` bir gerileme."** Model ağırlıkları **hiç değişmedi**; `tgta_v1` aynı artefakt.
   Değişen: iki kusur onarıldı ve donmuş TEST'in sayısı ilk kez var.
3. **"(b) kapanınca `v1.0` otomatik gelir."** Gelmez — o zaman kapının üç maddesi **yeni
   birimde yeniden okunur** (ADR-0050'nin kendi hükmü).

## `v1.0`'ın önündeki TEK açık madde

**Hakem paneli (b).** Bugünkü hâliyle bağlayıcı hüküm tek ailenin ve κ eşiğin altında.
Kapatma yolu: üçüncü hakem ailesi (G2) ya da κ'yı yükselten bir hakem protokolü.
⛔ Bu ADR o işi **planlamıyor**, yalnız `v1.0`'ın önündeki engelin **adını** koyuyor.

> **2026-09-13 güncellemesi:** madde (b)'nin kapanma koşulu
> [ADR-0084](0084-kappa-borcu-kapandi-kapi-yeni-birimde-gecti.md)'te karşılandı — κ **değişmedi**
> (hâlâ 0,534/0,409), ama kapının üç maddesi artık **iki** bağımsız hakem ailesi altında da
> GEÇTİ. Bu ADR'nin metni **değiştirilmedi**; o gün öyle yazılmıştı ve kayıt öyle durur.
