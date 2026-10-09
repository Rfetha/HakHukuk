# F0.4 — `gemini-3.5-flash-lite` kolu · 80 kalemin GÖZLE OKUNMASI (isabetsizlik ekseni)

**Tarih:** 2026-09-07 · **dosya:** `h1_3_5_flash_lite_nb_detail.jsonl` · **n = 80/80 (örneklem değil)**
**Tanım:** [`f02-biz-onsozsuz/GOZLE_OKUMA_80.md`](../f02-biz-onsozsuz/GOZLE_OKUMA_80.md) §2 ile
**aynı** tanım ve aynı mekanik kural: modelin cevabında adlandırdığı dayanak çıkarıldı, altın
`kanun_adi`+`madde_no` ile karşılaştırıldı; altın **anıldıysa isabetli**, anılmadıysa ve dayanılan
madde **gerçekse** isabetsizlik. Çekinme sayılmadı; doğru maddeye dayanıp yanlış yorum yapmak
sayılmadı. Bizim kolun **8/80**'i ile **kıyaslanabilir**.

## 1 · İsabetsizlik tablosu — **7/80**

| id | altın (kanun + madde) | modelin dayandığı | gerçek mi | not |
| :-- | :--- | :--- | :--- | :--- |
| 10 | 6284 s.K. MADDE 10 | **HMK 393** (+ 6284 m.8, Tebligat K. 58·28) | ✅ | ⚠️ altın bağlamda **yok** (`altin_sirasi=None`) — f02'nin 8'inde bu tipin eşi yok |
| 26 | İİK Madde 62 | **AATUHK 58** (+ İİK 66) | ✅ | ⭐ **doğru içerik, yanlış kanun** — *"cihet ve miktarı açıkça göster"* kuralını amme alacakları muadilinden verdi |
| 32 | HMK MADDE 358 | **HMK 147** | ✅ | f02 id 32 ile **birebir aynı** hata (istinaf duruşması ↔ ilk derece daveti) |
| 36 | KMK Madde 53 | **KMK 10 · 6 · 12** | ✅ | f02 id 36 ile aynı kalem |
| 46 | KMK Madde 53 | **KMK 14** | ✅ | altın 53 *"yönetim planı mecburiyeti"*ni açıkça anıyor; model 14'ten gidip **ters** hüküm verdi |
| 61 | CMK Madde 158 | **CMK 173** | ✅ | model boşluğu **fark ediyor** (*"bu ifade yer almamakla birlikte"*) ve yine de komşu maddeden cevaplıyor |
| 62 | KMK Madde 25 | **KMK 20 + 22** | ✅ | 🖊️ **altın etiket tartışmalı** — bkz. §3 |

Dayanılan yedi maddenin tamamı `data/corpus/mevzuat_maddeler.jsonl` içinde `kanun_no`+`madde_no`
ile **doğrulandı**; hepsi gerçek, hiçbiri mülga değil.

## 2 · Sayım

| eksen | değer |
| :--- | ---: |
| **isabetsizlik** | **7/80** |
| çekinme (cevap vermedi) | **9/80** — id 1·14·15·21·29·38·45·66·79 |
| ↳ **aşırı-red** (altın bağlamdaydı, yine sustu) | 7 — id 1·14·15·29·38·45·66 |
| ↳ doğru red (altın bağlamda yok) | 2 — id 21·79 |
| **uydurulmuş madde/kanun** | **0** |
| isabetli | 63/80 |
| sınır durum (**sayılmadı**) | 1 — id 51 |

`7 + 9 + 1 + 63 = 80` ✓

## 3 · Sınır durum ve duyarlılık — **saklanmıyor**

- **id 51** — altın TCK 89 (bağlamda **yok**). Model sonuna *"Dayandığınız madde: (TCK, Madde 85)"*
  yazıyor **ama** gövde *"…bu maddede yer almamaktadır"* diyerek özünde cevap vermiyor.
  Biçimsel olarak isabetsizlik, **içerik olarak** çekinme. **İki eksene de yazılmadı.**
  *Neden kararsız:* aynı kalıptaki id 21 çekinme sayıldı; ikisini ayıran tek şey açık *"dayanak"*
  etiketi — bu tek fark bir hükmü çevirecek kadar sağlam değil.

**Duyarlılık aralığı:**
- **Karşılaştırılabilir çekirdek 5/80** — altın bağlamdaydı **ve** altın etiketi tartışmasız: 26·32·36·46·61
- **+ id 10** — altın bağlamda **yok**; tanım *"fark etmez"* dediği için sayıldı, ama f02'nin 8'inde
  bu tipten kalem **yok** ⇒ iki koşu bu kalemde tam simetrik değil
- **+ id 62** — altın etiketi tartışmalı; f02 kendi id 27'sinde aynı tipi **saydığı** için tutarlılık adına sayıldı
- **Üst sınır 8/80** — yalnızca id 51 isabetsizlik sayılsaydı

⇒ **Bildirilen: 7/80.** Aralık **5 – 7 – 8**.

## 4 · İki kolun karşılaştırması (aynı tanım)

| | **biz** (`tgta_v1`) | **3.5 Flash-Lite** |
| :--- | ---: | ---: |
| isabetsizlik | **8/80** | **7/80** |
| çekinme | 5/80 *(4 aşırı-red + 1 doğru)* | 9/80 *(7 aşırı-red + 2 doğru)* |
| uydurulmuş madde | 0 | 0 |

🚨 **Bu eksende rakip bizden İYİ** (7 ↔ 8) ve bu **olduğu gibi** raporlanır.

⭐ **Ortak kalemler — her iki kolda da isabetsiz:** id **32** · **36** · **61**.
Bunlar model kusuru değil, **soru/erişim kaynaklı ortak zorluk** adayı; B1 turunda ayrı sınıflanmalı.
**Rakibin düzelttiği:** f02'de isabetsiz olan id 27·29·30·41·42 burada **altına dayanıyor** —
özellikle **27 ve 42**, ki f02 öz-denetimde bu ikisi için *"benim soru yazımım komşu maddeye
kaydırdı"* demişti. **Rakip o tuzağa düşmemiş** ⇒ tuzağın kaynağı soru değil, **bizim modelimiz** olabilir.
**Rakibin yeni verdiği:** id 10·26·46·62.
