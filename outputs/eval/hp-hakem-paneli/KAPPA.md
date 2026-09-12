# Hakem paneli — κ, bias/gürültü ve BAĞLAYICI OKUMA

> **Koşu:** 2026-09-07 · plan Görev 1-3 · girdi `outputs/eval/f02-biz-onsozsuz/h1_tgta_v1_f02_nb_detail.jsonl`
> ⛔ **Üretim yeniden koşulmadı** — aynı 80 cevap, yalnız HAKEM değişti (ADR-0017).

## 1. Panel — kim var, kim yok

| aile | hakem | n | bedel | durum |
| :--- | :--- | ---: | ---: | :--- |
| OpenAI | `openai/gpt-4o-mini` | 80 | $0.0417 | ✅ bugüne kadarki TEK hakem |
| Anthropic | `anthropic/claude-sonnet-5` | 80 | $1.8604 | ✅ bu turda eklendi |
| Google | — | — | — | ⛔ **KURULMADI** — bütçe (aşağıda, §5) |

⚠️ Panel **iki ailelidir**, ADR-0032 üç aile öngörüyordu. Bu bir **rejim sapmasıdır** ve
yayında eksiklik olarak yazılır; bütçe bahanesi olarak değil — sebebi §5'te sayıyla duruyor.

## 2. Aile dışlaması matrisi (ADR-0032)

| özne | ailesi | OpenAI hakem | Anthropic hakem | Google hakem |
| :--- | :--- | :---: | :---: | :---: |
| **`tgta_v1` (biz)** | Qwen/Alibaba | ✅ | ✅ | ✅ *(kurulmadı)* |
| `gemini-3.1-FL` · `3.5-FL` · `3.5-Flash` | **Google** | ✅ | ✅ | ❌ **YASAK** |
| `claude-sonnet-5` *(2026-09-09'da özne olarak girdi)* | **Anthropic** | ✅ | ✅ **öz-tercih hücresi** | — |

⇒ Üçlü κ **yalnız bizim kolumuzda** kurulabilirdi; rakip kolları her hâlükârda **iki aileyle**
notlanır. Bu bir eksiklik değil, **kuralın doğrudan sonucudur**.
✅ **ADIM 6.6b'de (2026-09-12) ÖLÇÜLDÜ, yalnız Anthropic ailesi için:** `claude-sonnet-5` özne
× `claude-sonnet-5` hakem hücresi kuruldu (aynı-aile). Sonuç kayırma LEHİNE değil — Anthropic
hakem kendi ailesinin cevaplarını `gpt-4o-mini`'ye göre bizim (çapraz-aile) kolumuzdan **daha
büyük** bir düşüşle cezalandırdı (20,03 p ↔ 10,71 p, çözünürlüğün — 1,25 p — çok üstünde bir
fark) ⇒ bu tek hücrede **ek katılık** ölçüldü, kayırma değil. Tek özne/tek hakem/tek koşu ⇒
gösterge, kanıt değil; notlamaya girmez (ADR-0032 aile dışlaması yürürlükte). Detay:
`outputs/eval/hp-oz-tercih-anthropic/OZ_TERCIH.md`.
🆕 **Hâlâ ölçülemeyen, AÇIK BORÇ:** Google özne ↔ Google hakem hücresi — aile dışlaması gereği
**hiçbir bütçeyle** kurulamaz. `gpt-4o-mini`'nin kendi ailesi de aynı sebeple ölçülemez (panelde
`gpt-4o-mini`-tabanlı bir özne yok). ⇒ *"öz-tercih ölçüldü"* cümlesi **genel olarak** hâlâ
kurulmaz — yalnız Anthropic hücresi için kurulur.

## 3. Uyum — κ ve r *(araç: `scripts/puanlama/judge_agreement.py`, eşiği: κ ≥ 0,6 makul · ≥ 0,8 güçlü)*

| eksen | ölçü | değer | hüküm |
| :--- | :--- | ---: | :--- |
| `faithfulness` | Pearson r | **0,705** | makul |
| `cit_precision` | Pearson r | **0,487** | ZAYIF |
| `tam_sadık` *(faithfulness = 1,0)* | Cohen's κ | **0,534** | **ZAYIF** — eşiğin altında |
| `atıf_temiz` *(cit_precision = 1,0)* | Cohen's κ | **0,409** | **ZAYIF** |

⚠️ **İddia düzeyinde κ KURULAMADI ve kurulamaz:** iki hakem farklı sayıda iddia çıkardı
(273 ↔ 341) ve iddialar birebir eşleşmiyor. Kalem düzeyi tek ortak zemindir;
ikili etiketler oradan **türetildi** (türetme kuralı tabloda parantez içinde).

## 4. Bias ↔ gürültü — AYRI raporlanır

| eksen | bias (B−A, sistematik) | gürültü (\|B−A\|, rastgele) | aynı not |
| :--- | ---: | ---: | ---: |
| `faithfulness` | **−0,1133** | 0,1573 | 48/80 |
| `cit_precision` | −0,1838 | 0,2088 | 63/80 |
| `cit_recall` | −0,1875 | 0,1875 | 65/80 |
| `hallucination_rate` | +0,1133 | 0,1573 | 48/80 |

**Kayma TEK YÖNLÜ:** Anthropic 24/80 kalemde daha DÜŞÜK, 8/80'de daha YÜKSEK not verdi.
⇒ Bu rastgele gürültü değil, **sistematik katılık**.

⚠️ **Gürültü tabanı şerhi:** yeniden-koşum gürültü tabanı **0,3 A1 puanıdır ve YALNIZ A1 için
ölçüldü.** Hakemler arası A1 farkı **11,33 puan** = tabanın **38 katı** ⇒ *"hakemler ayrışıyor"*
cümlesi **kurulabilir**. **Kütle için ayrı taban YOKTUR** (kütle = coverage × A1; coverage
varyansı o tabanda yer almıyor), bu yüzden kütle farkı için oran hesabı yapılmadı.

## 5. 🚨 Hakem seçimi manşet sayıyı oynatıyor — ve KAPI HÜKMÜ BURADAN KURULAMAZ

| eksen | `gpt-4o-mini` | `claude-sonnet-5` | fark |
| :--- | ---: | ---: | ---: |
| coverage *(hakemden bağımsız)* | 0.9375 | 0.9375 | +0.00 p |
| A1 (cevaplanan) | 0.8545 | 0.7403 | -11.42 p |
| **kütle** | **0.8011** | **0.6940** | **-10.71 p** |

⛔ **BU TABLODAN *"v1.0 kapısı düştü"* SONUCU ÇIKARILAMAZ.** Kapının eşiği (0,7225) çıpa
rakibin (`3.5 Flash`) kütlesinden türetildi ve **o sayı da `gpt-4o-mini`'nin hükmüdür.**
Anthropic hakem rakibi de aynı katılıkla notlarsa eşik de düşer ve marj korunabilir.
İki tarafı **farklı hakemlerle** kıyaslamak, ADR-0057'nin *eşit sınav* kuralının tam olarak
yasakladığı şeydir — kapıyı **sahte biçimde** devirir.

⇒ **Rakip kolu bu turda Anthropic hakemle puanlanamadı.** Ölçülen bedel: OpenRouter bakiyesi
**$3,45**, rakip koşusunun tahmini gerçek faturası **$2,81** (bakiyenin %81'i, tampon $0,64) —
ve donmuş TEST kabul koşusunun puanlaması da aynı bakiyeden ödenecekti. İnsan kararı: **harcanmadı.**

🆕 **AÇIK BORÇ:** *"kütle, Anthropic hakemle 0.6940"* sayısı **kayda geçti ama
YAYIMLANMAZ** — eşiti olmayan bir sınavın sonucudur. Yayımlanabilmesi için `3.5 Flash` kolunun
**aynı hakemle** puanlanması şarttır.

## 6. BAĞLAYICI OKUMA — bu tur ne söylüyor, ne söylemiyor

1. **Bağlayıcı olan hâlâ `gpt-4o-mini` hükmüdür** — çünkü kapının **iki tarafı da** onunla
   ölçülmüş tek hakem odur. Bu bir tercih değil, **eşit sınavın sonucudur**.
2. **Ama artık "tek hakem" bir borç değil, ÖLÇÜLMÜŞ bir kırılganlıktır:** κ eşiğin altında
   (0,534 · 0,409) ve kayma tek yönlü. Manşet %80,1'in yanında bu şerh **durmak zorundadır**.
3. Panel iki aileli kaldı ⇒ *"üç aile"* iddiası **kurulmaz**.
4. Öz-tercih **genel olarak hâlâ ölçülmedi** (Google/`gpt-4o-mini` hücreleri aile dışlaması
   gereği hiçbir bütçeyle kurulamaz) ⇒ *"hakem kendi ailesini kayırmıyor"* cümlesi **genel
   olarak kurulmaz**. **Yalnız Anthropic ailesi için** (ADIM 6.6b, 2026-09-12) ölçüldü ve
   sonuç **ters yönde** çıktı: Anthropic hakem kendi ailesinin cevaplarını (Sonnet-5) bizim
   kolumuza göre **daha büyük** bir düşüşle cezalandırdı (20,03 p ↔ 10,71 p) — kayırma
   LEHİNE kanıt yok, tek hücrelik bir gösterge var
   (`outputs/eval/hp-oz-tercih-anthropic/OZ_TERCIH.md`). Bu bulgu §2'deki notlama yasağı
   gereği kapı hükmüne girmez.

Kural olarak ADR-0074'te ön-kayıtlandı — **kapı koşusundan ÖNCE**.

