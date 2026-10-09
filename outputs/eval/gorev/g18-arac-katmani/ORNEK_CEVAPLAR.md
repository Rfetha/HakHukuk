# HakHukuk-4B v0.3 — örnek çıktılar

Bu dosya, modelin ürün yolunda (`hakhukuk.servis.answer`) ürettiği ham çıktılardan bir
seçkidir. Seçki, iyi örnekleri olduğu kadar kusurlu örnekleri de içerecek biçimde
oluşturulmuştur; dört durum sınıfının tamamı temsil edilmektedir.

**Koşu künyesi.** 2026-09-09 · erişim katmanı etkin, k=10 · seed 3407 · önsözsüz istem ·
araç katmanı kapalı · üretim bütçesi 1536 belirteç (düşünce dahil) · yerel `llama-server`,
Q4_K_M · geliştirme kümesi `data/eval/dev/core_hard.jsonl`, n=80.

**Uyarı.** Bu, bildirilen %80,1'lik kütlenin ölçüldüğü hat değildir. Ölçüm hattı düşünce
kanalını zorla kapatır; ürün yolu kapatmaz. Farkın sonucu aşağıda id 66'da görülmektedir:
cevap tamamen boştur. Ayrıntı için model kartının 2. bölümüne bakınız.

**Atıf işaretleri.** `doğrulandı` = atfedilen madde, modele verilen kaynaklar arasında
bulunmaktadır (deterministik denetim, hakem değil). `doğrulanamadı` = bulunmamaktadır.

---

## Örnek 0 — CEVAP
*dayanağı getirilen kaynaklarda, atıfları doğrulandı*

**Soru.** Cumhuriyet savcıları hangi durumlarda doğrudan soruşturma yapar?

**Beklenen dayanak.** CEZA MUHAKEMESİ KANUNU Madde 161

**Model çıktısı.**

```
1) KAYNAK 7, Cumhuriyet savcısının soruşturma ve kovuşturma yetkisini düzenleyen CEZA MUHAKEMESİ KANUNU Madde 160'dır. Bu madde, savcının hangi durumlarda doğrudan soruşturma yapacağını açıkça belirtmektedir. Diğer kaynaklar, savcının genel görevleri veya diğer konularla ilgili olduğundan, sorunun cevabını sağlamamaktadır.

2) ##begin_quote## "Cumhuriyet savcısı, ihbar veya başka bir suretle bir suçun işlendiği izlenimini veren bir hâli öğrenir öğrenmez kamu davasını açmaya yer olup olmadığına karar vermek üzere hemen işin gerçeğini araştırmaya başlar." ##end_quote##

3) Sonuç olarak, Cumhuriyet savcıları, ihbar veya başka bir suretle bir suçun işlendiği izlenimini aldıklarında doğrudan soruşturma yaparlar (CEZA MUHAKEMESİ KANUNU, Madde 160).
```

**Atıf denetimi.** 5271 Madde 160 (doğrulandı) · 5271 Madde 160 (doğrulandı)

**Getirilen kaynaklar (10 maddenin ilk beşi).** 5271/Madde 161, 2802/Madde 5, 5411/Madde 166, 5271/Madde 332, 2802/Madde 115

---

## Örnek 2 — CEVAP
*dayanağı getirilen kaynaklarda, atıfları doğrulandı*

**Soru.** Bir örgüt kapsamında organ alırsam cezam ne olur?

**Beklenen dayanak.** TÜRK CEZA KANUNU Madde 91

**Model çıktısı.**

```
1) İlgili kaynak, Türk Ceza Kanunu Madde 91'dir. Bu madde, organ ve doku ile ilgili suçların cezasını düzenlemektedir ve özellikle bir örgütün faaliyeti çerçevesinde işlenmesi halinde uygulanacak ceza hükümlerini içermektedir. Diğer kaynaklar, organ nakli ile ilgili genel düzenlemeler veya örgüt suçları hakkında bilgi verirken, doğrudan organ alımına ilişkin ceza hükümlerini içermemektedir.

2) ##begin_quote## "Bir ve üçüncü fıkralarda tanımlanan suçların bir örgütün faaliyeti çerçevesinde işlenmesi halinde, sekiz yıldan onbeş yıla kadar hapis ve onbin güne kadar adlî para cezasına hükmolunur." ##end_quote##

3) Sonuç olarak, bir örgüt kapsamında organ alımına ilişkin suç işlenmesi durumunda, sekiz yıldan onbeş yıla kadar hapis cezası ve onbin güne kadar adlî para cezası uygulanır (TÜRK CEZA KANUNU, Madde 91).
```

**Atıf denetimi.** 5237 Madde 91 (doğrulandı) · 5237 Madde 91 (doğrulandı)

**Getirilen kaynaklar (10 maddenin ilk beşi).** 5237/Madde 91, 5237/Madde 220, 5237/Madde 221, 5237/Madde 314, 2238/Madde 7

---

## Örnek 5 — CEVAP
*dayanağı getirilen kaynaklarda, atıfları doğrulandı*

**Soru.** Zorla fuhşa sevketme, insanlığa karşı suç mudur?

**Beklenen dayanak.** TÜRK CEZA KANUNU Madde 77

**Model çıktısı.**

```
1) KAYNAK 1, zorla fuhşa sevketme fiilinin insanlığa karşı suç olduğunu açıkça belirtmektedir. Diğer kaynaklar, bu konuyla ilgili doğrudan bilgi sunmamaktadır; bu nedenle yalnızca KAYNAK 1 geçerlidir.

2) ##begin_quote## "Aşağıdaki fiillerin, siyasal, felsefi, ırki veya dini saiklerle toplumun bir kesimine karşı bir plan doğrultusunda sistemli olarak işlenmesi, insanlığa karşı suç oluşturur: ... h) Zorla fuhşa sevketme." ##end_quote##

3) Sonuç olarak, zorla fuhşa sevketme fiili, belirli koşullar altında insanlığa karşı suç olarak kabul edilmektedir (TÜRK CEZA KANUNU, Madde 77).
```

**Atıf denetimi.** 5237 Madde 77 (doğrulandı)

**Getirilen kaynaklar (10 maddenin ilk beşi).** 5237/Madde 77, 5237/Madde 227, 5237/Madde 80, 5271/Madde 100, 5237/Madde 76

---

## Örnek 30 — KESİK
*üretim bütçesi doldu; cevap yarım ya da boş*

**Soru.** Mazeret bildirmezsem ve duruşmaya katılmazsam ne olur?

**Beklenen dayanak.** HUKUK MUHAKEMELERİ KANUNU MADDE 358

**Model çıktısı.**

```
1) KAYNAK 5 - HUKUK MUHAKEMELERİ KANUNU MADDE 147

2) KAYNAK 8 - DİSİPLİN MAHKEMELERİ KURULUŞU, YARGILAMA USULÜ VE DİSİPLİN SUÇ VE CEZALARI HAKKINDA KANUN MADDE 19

3) KAYNAK 9 - HUKUK MUHAKEMELERİ KANUNU MADDE 358

4) KAYNAK 1 - CEZA MUHAKEMESİ KANUNU MADDE 188

5) KAYNAK 4 - CEZA MUHAKEMESİ KANUNU MADDE 195

6) KAYNAK 2 - HUKUK MUHAKEMELERİ KANUNU MADDE 245

7) KAYNAK 3 - TÜRK SİLÂHLI KUVVETLERİ PERSONEL KANUNU MADDE 125

8) KAYNAK 6 - ANAYASA MAHKEMESİNİN KURULUŞU VE YARGILAMA USULLERİ HAKKINDA KANUN MADDE 70

9) KAYNAK 7 - MAL BİLDİRİMİNDE BULUNULMASI, RÜŞVET VE YOLSUZLUKLARLA MÜCADELE KANUNU MADDE 10

10) KAYNAK 10 - ASKERALMA KANUNU MADDE 21

##begin_quote## "Taraflara gönderilecek davetiyede, belirlenen gün ve saatte geçerli bir özrü olmadan mahkemede hazır bulunmadıkları takdirde, duruşmaya yokluklarında devam edileceği ve yapılan işlemlere itiraz edemeyecekleri, tahkikatın sona erdiği duruşmada sözlü yargılamaya
```

**Atıf denetimi.** 6100 Madde 147 (doğrulandı) · 477 Madde 19 (doğrulandı) · 6100 Madde 358 (doğrulandı) · 5271 Madde 188 (doğrulandı) · 5271 Madde 195 (doğrulandı) · 6100 Madde 245 (doğrulandı) · 926 Madde 125 (doğrulandı) · 6216 Madde 70 (doğrulandı) · 3628 Madde 10 (doğrulandı) · 7179 Madde 21 (doğrulandı)

**Getirilen kaynaklar (10 maddenin ilk beşi).** 5271/Madde 188, 6100/MADDE 245, 926/Madde 125, 5271/Madde 195, 6100/MADDE 147

---

## Örnek 1 — ÇEKİNCELİ CEVAP
*cevap üretildi, ancak en az bir atıf getirilen kaynaklarda doğrulanamadı*

**Soru.** Dikkatsizliğim yüzünden birden fazla kişi yaralanırsa ceza nasıl belirlenir?

**Beklenen dayanak.** TÜRK CEZA KANUNU Madde 89

**Model çıktısı.**

```
1) KAYNAK 8 - Türk Ceza Kanunu Madde 88, kasten yaralamanın ihmali davranışla işlenmesi durumunda uygulanacak ceza ile ilgili düzenlemeleri içermektedir. Diğer kaynaklar, kasten yaralama veya ölümle ilgili suçları düzenlemektedir, bu nedenle sorunun cevabı için uygun değildir.

2) ##begin_quote## "Kasten yaralamanın ihmali davranışla işlenmesi halinde, verilecek ceza üçte ikisine kadar indirilebilir." ##end_quote##

3) Sonuç olarak, dikkatsizliğiniz yüzünden birden fazla kişi yaralanması durumunda, kasten yaralama suçunun ihmali davranışla işlenmesi halinde ceza üçte ikisine kadar indirilebilir (TÜRK CEZA KANUNU, Madde 88).
```

**Atıf denetimi.**  Madde 88 (DOĞRULANAMADI) ·  Madde 88 (DOĞRULANAMADI)

**Getirilen kaynaklar (10 maddenin ilk beşi).** 5237/Madde 85, 2918/Madde 88, 5237/Madde 43, 5320/Madde 15, 6706/MADDE 10

---

## Örnek 10 — SUSKUNLUK
*model dayanak bulamadığını bildirdi*

**Soru.** Tüketici davalarında mahkeme kararları nasıl yayınlanır?

**Beklenen dayanak.** TÜKETİCİNİN KORUNMASI HAKKINDA KANUN MADDE 73

**Model çıktısı.**

```
Verilen kaynaklarda bu konuyu düzenleyen madde bulunmuyor.
```

**Atıf denetimi.** yok

**Getirilen kaynaklar (10 maddenin ilk beşi).** 6502/MADDE 70, 6502/MADDE 73, 6502/MADDE 68, 6502/MADDE 74, 6100/MADDE 372

---

## Örnek 34 — SUSKUNLUK
*model dayanak bulamadığını bildirdi*

**Soru.** Eğer tüketici hakem heyetinin oluşumu sağlanamazsa ne olur?

**Beklenen dayanak.** TÜKETİCİNİN KORUNMASI HAKKINDA KANUN MADDE 66

**Model çıktısı.**

```
Verilen kaynaklarda bu konuyu düzenleyen madde bulunmuyor. KAYNAK 7'de tüketici hakem heyetlerinin kurulması ve çalışma usulleri yönetmelikle belirlendiği belirtilse de, heyetin kurulamaması durumunda ne olacağına dair bir düzenleme bulunmamaktadır.
```

**Atıf denetimi.** yok

**Getirilen kaynaklar (10 maddenin ilk beşi).** 6502/MADDE 70, 6502/MADDE 66, 6502/MADDE 68, 6502/MADDE 67, 5957/MADDE 10

---

## Örnek 66 — KESİK
*üretim bütçesi doldu; cevap yarım ya da boş*

**Soru.** Vasiliğe atanma kararı kesinleşince ne yapılmalı?

**Beklenen dayanak.** TÜRK MEDENİ KANUNU Madde 438

**Model çıktısı.**

```
(boş — model </think> etiketini kapatmadı, bütçe düşünce kanalında tükendi)
```

**Atıf denetimi.** yok

**Getirilen kaynaklar (10 maddenin ilk beşi).** 4721/Madde 425, 4721/Madde 438, 4721/Madde 424, 4721/Madde 423, 4721/Madde 422

---

## Örnek 68 — KESİK
*üretim bütçesi doldu; cevap yarım ya da boş*

**Soru.** Sözleşmemde bir para birimi belirttiğimde ne olur?

**Beklenen dayanak.** TÜRK BORÇLAR KANUNU MADDE 99

**Model çıktısı.**

```
1) KAYNAK 9 - EURO'NUN HUKUKİ ARAÇLARA ETKİSİ İLE AKARYAKIT TÜKETİM VERGİSİ KANUNUNDA DEĞİŞİKLİK YAPILMASI HAKKINDA KANUN Madde 4

2) KAYNAK 3 - EURO'NUN HUKUKİ ARAÇLARA ETKİSİ İLE AKARYAKIT TÜKETİM VERGİSİ KANUNUNDA DEĞİŞİKLİK YAPILMASI HAKKINDA KANUN Madde 5

3) KAYNAK 5 - EURO'NUN HUKUKİ ARAÇLARA ETKİSİ İLE AKARYAKIT TÜKETİM VERGİSİ KANUNUNDA DEĞİŞİKLİK YAPILMASI HAKKINDA KANUN Madde 7

4) KAYNAK 1 - TÜRKİYE CUMHURİYETİ DEVLETİNİN PARA BİRİMİ HAKKINDA KANUN Madde 1

5) KAYNAK 2 - VERGİ USUL KANUNU Madde 215

6) KAYNAK 4 - SİGORTACILIK KANUNU GEÇİCİ MADDE 9

7) KAYNAK 6 - ÖLÇÜLER VE AYAR KANUNU Madde 6

8) KAYNAK 7 - ENERJİ VERİMLİLİĞİ KANUNU GEÇİCİ MADDE 7

9) KAYNAK 8 - JEOTERMAL KAYNAKLAR VE DOĞAL MİNERALLİ SULAR KANUNU GEÇİCİ MADDE 4

10) KAYNAK 10 - TÜRK TİCARET KANUNU MADDE 69

##begin_quote## "Kanunlarda ve diğer mevzuatta ulusal para birimlerine yapılan bütün göndermeler, ulusal paraların tedavülden kaldırıldıkları tarihten itibaren, Avrupa Birliği tarafından geri dönülmez şekilde sabitlenerek belirlenen ve Türkiye Cumhuriyet Merkez Bankası tarafından da ilan edilen değişim oranı uygulanarak EURO'ya yapılmış olarak kabul edilir." ##end_quote##

##begin_quote## "EURO'nun kullanıma girmesiyle, hukuki araçlarda ECU'nun 3 üncü maddenin (b) bendinde yapılan tanımına gönderme yapıldığı takdirde, ECU bire bir oranında EURO'ya dönüşür." ##end_quote##

##begin_quote## "Sözleşmelerin ve diğer hukuki işlemlerin devamlılığı" ##end_quote##

##begin_quote## "EURO'nun kullanıma girmesi veya ulusal para birimlerinin tedavülden kaldırılarak tek para sistemine dahil Avrupa Birliğine üye devletlerde EURO'nun tek para birimi olma niteliğini kazanması veya ulusal para birimi ya da ECU için belirlenen faiz oranının veya oran belirleme yönteminin değişmesi, mevcut sözleşmenin veya diğer hukuki işlemlerin taraflarından birine, sözleşmeyi veya hukuki işlemi tek taraflı olarak değiştirme veya fesih hakkını vermez." ##end_quote##

##begin_quote## "Bu Kanunun kapsamında; a) Ulusal para birimlerinin EURO'ya dönüştürülmesine ilişkin işlemler ile bu işlemlerin yapılması sırasında her ne nam altında olursa olsun lehe alınan paralar hakkında 13.7.1956 tarihli ve 6802 sayılı Gider Vergileri Kanunu hükümleri, b) EURO'nun kullanıma girdiği tarihten önce veya sonraki dönemde ulusal para birimi cinsinden akdedilmiş sözleşmeler ile gerçekleştirilmiş diğer hukuki işlemlerde ulusal para birimine, komisyon, faiz ve diğer masraflara gönderme yapan hükümlerin EURO cinsinden değiştirilmesi için düzenlenecek kağıtlar hakkında 1.7.1964 tarihli ve 488 sayılı Damga Vergisi Kanunu ile 2.7.1964 tarihli ve 492 sayılı Harçlar Kanunu hükümleri, uygulanmaz." ##end_quote##

##begin_quote## "Resmi ve özel sözleşmeler, her türlü evrak, belge ve ilanlar ile miktar belirten etiketlerde ve kanunlara göre tutulan defterlerde, uluslararası birimlerin kullanılması zorunludur." ##end_quote##

##begin_quote## "Yılsonu finansal tablolar; a) Türkiye Muhasebe Standartlarına uyularak düzenlenmeli, b) Açık ve anlaşılır olmalı, c) Düzenli bir işletme faaliyeti akışının gerekli kıldığı süre içinde çıkarılmalıdır." ##end_quote##

##begin_quote## "Türkiye Cumhuriyeti Devletinin para birimi Yeni Türk Lirasıdır. Yeni Türk Lirasının alt birimi Yeni Kuruştur. Bir Yeni Türk Lirası (YTL) yüz Yeni Kuru
```

**Atıf denetimi.** 4538 Madde 4 (doğrulandı) · 4538 Madde 5 (doğrulandı) · 4538 Madde 7 (doğrulandı) · 5083 Madde 1 (doğrulandı) · 213 Madde 215 (doğrulandı) ·  Madde 9 (DOĞRULANAMADI) · 3516 Madde 6 (doğrulandı) · 4538 Madde 7 (doğrulandı) · 4538 Madde 4 (doğrulandı) · 6102 Madde 69 (doğrulandı)

**Getirilen kaynaklar (10 maddenin ilk beşi).** 5083/Madde 1, 213/Madde 215, 4538/Madde 5, 5684/GEÇİCİ MADDE 9, 4538/Madde 7

---

## Seçki hakkında

Dokuz örneğin dağılımı, 80 kalemlik koşunun dağılımını temsil etmez; kusurlu sınıflar
bilerek fazla temsil edilmiştir. Koşunun tamamındaki dağılım şöyledir: CEVAP 69,
KESİK 7, SUSKUNLUK 3, ÇEKİNCELİ CEVAP 1. Ham kayıt, GitHub deposunda
`outputs/eval/g18-arac-katmani/aracsiz_yol_80.json` dosyasındadır.
