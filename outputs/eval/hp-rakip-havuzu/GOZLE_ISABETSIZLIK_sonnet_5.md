# HP — `claude-sonnet-5` · 80 kalemde İSABETSİZLİK (gözle tam tarama)

**Tarih:** 2026-09-12 · **dosya:** `h1_sonnet_5_nb_detail.jsonl` · **n = 80/80** (örneklem değil)
⭐ **Neden bu tarama şimdi yapıldı:** `HF_KARTI.md` dipnot ᵈ, dört öznede (BİZ · 3.1 FL · 3.5
FL-lite · 3.5 Flash) 80/80 gözle sayıldığını, Sonnet-5 kolunda ise bu taramanın YAPILMADIĞINI ve
tahmin yazılmadığını kaydediyordu. Bu, yayımlanan kıyas tablosundaki tek gerçek asimetriydi —
beşinci özne, kütlede önde olandı.
**Tanım:** [`f02/GOZLE_OKUMA_80.md`](../f02-biz-onsozsuz/GOZLE_OKUMA_80.md) §2 ve
[`f04/GOZLE_ISABETSIZLIK_3_5_FLASH.md`](../f04-rakip-onsozsuz/GOZLE_ISABETSIZLIK_3_5_FLASH.md) ile
**birebir aynı**: cevabın dayandığı kaynak (genelde ilk/esaslı cümlede adlandırılan) altın maddeyle
karşılaştırılır. İsabetsizlik = bağlamdaki **gerçek ama yanlış** maddeye dayandırma; madde uydurma
ile karıştırılmaz. Modelin sonradan altını esaslı biçimde kullandığı kalemler (önce başka maddeden
söz edip sonra altını gerçek gerekçe olarak işleyen), emsalin id 32 · 41 · 69 için uyguladığı kural
gereği **isabetli** sayılır.

## 1 · İsabetsizlik — **7/80**

| id | altın | modelin dayandığı | gerçek mi | not |
| :-- | :--- | :--- | :--- | :--- |
| 10 | 6284 M.10 | **HMK 393** | ✅ | altın **gelmedi** (`sirasi=None`); ihtiyati tedbirden cevapladı — aynı desen `f04` id 10 |
| 21 | TBK 99 | **EURO K. M.5/7** | ✅ | altın **gelmedi**; para birimi yerine Euro geçiş mevzuatından cevapladı — aynı desen `f04` id 21 |
| 26 | İİK 62 | **AATUHK 58 + İİK 66** | ✅ | ⭐ altın **1. sırada**, referans metni doğrulandı: İİK 62 lafzen *"Borcun bir kısmına itiraz eden borçlunun o kısmın cihet ve miktarını açıkca göstermesi lazımdır"* — sorunun ta kendisi; model hiç anmadı |
| 27 | KMK 33 | **KMK 25** | ✅ | ⭐ altın **3. sırada**, referans metni doğrulandı: KMK 33 f.2 lafzen *"Hakim... bu kanuna ve yönetim plânına ve bunlarda bir hüküm yoksa, genel hükümlere ve hakkaniyet kaidelerine göre... kararını verir"* — soru budur; model KMK 25'in (mülkiyetin devri, ağır/farklı yaptırım) sınırına kaydı |
| 34 | CMK 161 | **HSK 116 + CMK 332 + Bankacılık K. 166** | ✅ | ⭐ altın **0. sırada**, hiç anılmadı; cevap kesik (`finish_reason=length`), genel kurala ("Cumhuriyet savcısı...") tam varmadan token bitti — aynı desen `f04` id 34 |
| 36 | KMK 53 | **KMK 10/12/13/14** | ✅ | altın **8. sırada**, hiç anılmadı; model kat mülkiyeti kuruluş sürecinin genel maddelerini anlattı, 53'ün 1965-öncesi irtifak geçiş hükmüne değinmedi — aynı desen `f02` "biz" id 36 |
| 70 | TMK 241 | **TMK 268/269/210** | ✅ | altın **2. sırada**, hiç anılmadı; model mal rejimi borç-sorumluluğu genel kurallarını anlattı, 241'in (3. kişilerden istem/tasfiye) özel hükmüne değinmedi — aynı desen `f04` id 70 |

**Altın bağlamdayken ıskalanan: 5/7.** Altın hiç gelmemişken komşu mevzuattan konuşan: 2/7 (id 10 · 21).

## 2 · Sınır durum — **5**, sayılmadı

| id | altın | modelin dayandığı | gerekçe |
| :-- | :--- | :--- | :--- |
| 29 | TKHK 49 | (survey: TKHK 18/24/43 + FSEK 58) | Soru fazla genel (*"Cayma hakkı nedir?"*); altın (49, finansal hizmetler mesafeli sözleşmesi) da diğerleri gibi yalnızca bağlam-özel bir hüküm — genel tanım değil. Model dürüstçe *"genel tanım yok"* diyerek dört bağlam-özel hükmü sıraladı, hiçbirini "the" cevap olarak sunmadı; tek bir yanlış maddeye dayandırma yok. |
| 46 | KMK 53 | **KMK 14** | Emsalin **kendi** id 46 hükmü (`f04`, 3.5-flash) burada da geçerli: *"kusurlu olan modelden çok altın etiketin kendisi olabilir."* KMK 14 lafzen soruyu (*"yönetim planı zorunlu mu"*) birebir karşılıyor (*"Kat mülkiyetine geçişte ayrıca yönetim plânı istenmez"*); KMK 53 ayrı bir konuya (1965-öncesi irtifak hakları) ait. Aynı gerekçeyle sayılmadı. |
| 55 | İİK 168 | **İİK 171** | Korpustaki iki madde (168 haciz yolu, 171 iflas yolu kambiyo senedi takibi) sorunun cevabı olan açılış cümlesini **kelimesi kelimesine aynı** taşıyor: *"İcra memuru, senedin kambiyo senedi olduğunu ve vadesinin geldiğini görürse... hemen bir ödeme emri gönderir."* Model doğru içeriği doğru biçimde aktardı, yalnız madde numarası komşu/paralel hükme kaydı. |
| 61 | CMK 158 | **CMK 173 (+172)** | Soru *"soruşturma yapılmasına yer olmadığı"* kararına itirazı sorar; altın CMK 158/f.6 bu hakkı tanıyıp *"173 üncü maddedeki usule göre itiraz edilebilir"* diyor. Model doğrudan 173'ü (+172) anlattı — usul, süre (2 hafta) ve mercii (sulh ceza hâkimliği) **birebir doğru**, yalnız hakkı tanıyan 158 yerine referans verilen 173'ü esas aldı. Sonuç doğru, dayanak maddesi komşu. |
| 62 | KMK 25 | **KMK 20 + 22** | Soru genel (*"ortak giderleri ödemiyorsa ne olur"*); KMK 20 tam bu yükümlülüğü ve ihlalinde dava/icra yolunu düzenliyor, KMK 22 müteselsil sorumluluk + ipoteği ekliyor — ikisi de doğrudan cevap. Altın KMK 25 ise yalnız *"çekilmez hale gelen"* tekrarlı ihlallerde uygulanan istisnai/ağır yaptırım (mülkiyetin devri) — id 27/46 ile aynı desen (dar/istisnai altın, genel soru). |

Sayılsaydı **12/80** olurdu. Sayılmama gerekçesi hepsinde aynı aile: ya altın etiketin kendisi
sorunun genelliğine göre dar/istisnai kalıyor (29 · 46 · 62), ya da model içerik olarak doğru
kaynağa ulaşıp yalnız numarada komşu bir maddeye kayıyor (55 · 61).

## 3 · Kapsam dışı not — çekinme ekseniyle karışmasın

Bu tarama **yalnız isabetsizlik** eksenini sayar. Aynı 80 kalemde 4 gerçek çekinme
(id 15 · 45 · 66 · 79) zaten [`GOZLE_KALIBRASYON_sonnet_5.json`](GOZLE_KALIBRASYON_sonnet_5.json)
ile ayrıca sayılmıştır (HF_KARTI'nin *"Aşırı çekinme 4/80"* satırının kaynağı) ve bu dosyaya
tekrar dahil edilmedi. id 32 · 41 · 69'da model önce altın olmayan maddeden söz edip sonra altını
esaslı biçimde kullandı ⇒ tanım gereği **isabetli** sayıldı (emsalin aynı üç id için verdiği
hükümle birebir).

## 4 · Çivilenen sayılar

| eksen | **Sonnet-5** | (kıyas) **BİZ** |
| :--- | ---: | ---: |
| **isabetsizlik** | **7/80** | **8/80** |
| cevaplanan tabanda | 7/76 = **%9,2** | 8/75 = **%10,7** |
| sınır durum (sayılmadı) | 5 (id 29 · 46 · 55 · 61 · 62) | — |
| çekinme (temiz, ayrı ölçüldü) | 4/80 | 5/80 |

🚨 **Bu tablodan KURULMAYACAK cümle:** *"Vekil ölçüt (`wrong_ref_rate_micro` 0,0083) doğrulandı,
göz sayımı gereksizdi."* Ön-kayıt gereği sayı **çıktığı gibi** raporlanır: göz sayımı **7/80**,
vekil ölçütten (0,0083 ≈ 1/120 atıf tabanında) çok daha yüksek çıkmıştır — iki ölçüt **farklı
eksenler** (biri kalem bazlı gözle hüküm, diğeri hakem tabanlı atıf-bazlı vekil) ve biri diğerini
"yanıltıyor" demek bu turun kapsamı dışındadır. Sonnet-5, bizim **8/80**'imizin **altında**
kalmıştır (7/80); dipnot ᵈ'nin *"bu eksen HakHukuk'un açık borcudur"* hükmü Sonnet-5 için de
**değişmeden** geçerlidir.
