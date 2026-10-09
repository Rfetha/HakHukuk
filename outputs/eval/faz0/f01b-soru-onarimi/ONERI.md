# Soru onarımı — ÖNERİ (insan onayı bekliyor, hiçbir sete yazılmadı)

**Tarih:** 2026-09-06 · **yazar:** model · **denetçi:** insan (onaysız sete girmez)

## Ölçüt
Soru tek başına okunduğunda (i) hangi kanun ailesine ait olduğu ve (ii) o kanun içinde hangi
hükmü sorduğu ayırt edilebiliyor mu? Biri yoksa **belirlenemez**.
Kusur sınıfları: **A** askıda gönderim · **B** kanun ailesi belirsiz · **C** kurum belirsiz.

## Yanlılık korumaları (ADR-0050 ruhu)
1. Her soru **yalnız altın maddenin metnine** bakılarak yazıldı. Retriever çıktısına, model
   cevabına, hangi kalemin kaçırıldığına **bakılmadı**.
2. ⛔ **Maddenin ayırt edici ifadeleri kopyalanmadı** — kopyalamak `recall`'u yapay olarak
   şişirir. Eklenen tek şey, hangi kanun/kurum olduğunu belirleyen **asgari** bağlam.
3. Sorular vatandaş dilinde; uzman terimi ancak kaçınılmazsa.
4. ⭐ **Eşleşmeler denetlendi ve DOĞRU çıktı.** Tam metne bakıldı: KMK 21 gerçekten *"kendi
   bağımsız bölümünü ayrıca sigorta ettirme"*yi, KMK 33 gerçekten *"hâkim ... hangi kurallara
   göre karar verir"*i, CMK 142/9 gerçekten avukatlık ücretini düzenliyor.
   ⇒ Kusur **yer-gerçeğinde değil, sorunun bağlamının sökülmüş olmasında.**

## DEV `core_hard.jsonl` — 13 kalem

| id | altın | sınıf | ESKİ | ÖNERİLEN |
| :-- | :--- | :-: | :--- | :--- |
| 1 | TCK 89 | C | Birden fazla kişiye zarar verirsem cezam ne olur? | **Dikkatsizliğim yüzünden birden fazla kişi yaralanırsa ceza nasıl belirlenir?** |
| 24 | 6284/10 | A+B | Başvurum kabul edilirse ne olur? | **Aile içi şiddet nedeniyle yaptığım başvuru kabul edilirse bu karar kimlere bildirilir?** |
| 27 | HMK 294 | C | Mahkeme ne zaman davayı sona erdirir? | **Hukuk davasında mahkeme davayı hangi kararla bitirir ve hüküm ne zaman açıklanır?** |
| 41 | İş K 31 | B | İşten ayrılıp işe dönmek istersem eski işimle aynı şartlarda mı çalışırım? | **Askerlik veya manevra nedeniyle işinden ayrılan işçinin iş sözleşmesi ne olur?** |
| 43 | İş K 21 | A | İşverene başvurmazsam ne olur? | **Mahkeme işe iademe karar verdi; süresinde işverene başvurmazsam ne olur?** |
| 47 | 6284/6 | B | Birisi silah bulunduruyorsa ne olur? | **Aile içi şiddet tedbiri uygulanan kişinin silah bulundurması ayrıca suç oluşturuyorsa, ceza kanunlarındaki hükümler ne olur?** |
| 49 | İİK 31/a | B | Mahkeme benim lehime bir karar verirse ne olur? | **Gemiyle ilgili açtığım davayı kazanırsam mahkeme resmî kayıtlara bir bildirim yapar mı?** |
| 57 | KMK 21 | B | Sigorta bedeli ben kendim için yaptırırsam ne olur? | **Apartmandaki dairemi kendi adıma ayrıca sigorta ettirirsem sigorta bedeli kime ait olur?** |
| 58 | KMK 33 | B | Mahkeme hangi kurallara göre karar verir? | **Kat maliklerinden biri yükümlülüğünü yerine getirmediği için mahkemeye başvurduğumda hâkim neye göre karar verir?** |
| 71 | TBK 217 | B | Ürünüm elimden alınırsa, geri alabilir miyim? | **Satın aldığım mal üçüncü bir kişi tarafından elimden alınırsa satıcıdan neleri isteyebilirim?** |
| 75 | KMK 53 | C | Gayrimenkulün yönetimiyle ilgili hangi kurallara uyulmalı? | **Henüz kat mülkiyetine geçilmemiş, eski tarihli irtifak hakkı bulunan bir binada yönetim hangi kanuna tabidir?** |
| 78 | 6284/7 | A+B | İhbar ettikten sonra ne olacak? | **Şiddet gördüğümü resmî makamlara ihbar edersem, ihbarı alan görevliler ne yapmak zorunda?** |
| 79 | 6284/11 | A | Kolluk güçleri bu eğitimleri ne için alıyor? | **Aile içi şiddet ihbarlarına bakan kolluk personelinde hangi nitelik aranır?** |

## TEST `canon/core_hard.jsonl` — 2 kalem

| id | altın | sınıf | ESKİ | ÖNERİLEN |
| :-- | :--- | :-: | :--- | :--- |
| 7 | CMK 142 | B | Avukatlık ücreti nasıl belirleniyor? | **Koruma tedbirleri nedeniyle açtığım tazminat davasında avukatlık ücreti nasıl hesaplanır?** |
| 36 | TMK 819 | C | Bir eşyanın intifa hakkı sona ererse ne olur? | **Tüketilebilen bir mal üzerindeki intifa hakkı sona erdiğinde geri verme nasıl yapılır?** |

**TEST'te DEĞİŞTİRİLMEYENLER — gerekçeli:**
- **id 31 (KMK 44)** — soru maddenin *"kapanan eski kütük sayfasiyle ... bağlantı sağlanması"*
  ifadesini **birebir kopyalıyor**. Bu **ters yönde** bir kusur: erişimi yapay kolaylaştırıyor.
  ⛔ Düzeltmek kendi sayımızı **yükseltmek** olur → **dokunulmadı**, damgalandı.
- **id 34 (TMK 727)** — mecra irtifakı; soru maddeyle uyumlu, **kusur yok**.
- 🚨 **`canon/trap.jsonl` (35 kalem) DOKUNULMADI** — oradaki *"seçim sonuçları ne zaman ilan
  edildi?"* gibi sorular kusur değil **kasıtlı tuzak**; set reddetme davranışını ölçüyor.
  Aynı ölçütle "düzeltmek" testin kendisini yok ederdi.

## Uygulanırsa ne olur

- DEV `core_hard` → **v2**; eski dosya `core_hard.jsonl.v1-2026-09-06` olarak **saklanır**.
- ⚠️ `#39-#61` arasındaki **her DEV sayısı v1 birimindedir** ve damgalanır: kütle (%68,4 · %73,0 ·
  %62,8) · aşırı-red (9/80 · 8/80) · isabetsizlik (5/80 · 7/80) · **ARA KAPI eşiği 0,8649 ve merge
  M2b 0,766** · ADR-0052'nin 0,506→0,766 sıçraması · B10'un 80 kalemlik gözle okuması.
- Yeniden koşulacaklar: bizim h1 kolumuz (yerel, $0 + hakem ~$0,15) · üç rakip (F0.4'te **zaten
  bütçelenmişti**, ~$1,35) · F0.3 gözle okuma (zaten planlıydı).
- ⇒ **Parasal ek yük ≈ $0,15. Harcanan şey kaydın karşılaştırılabilirliği.**
