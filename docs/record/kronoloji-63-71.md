# Araştırma kaydı — #63 … #74

> **Ne bu:** skor kartının kapatılması, hakem paneli, donmuş TEST, konteyner ve `v1.0` turu —
> **birleştirilmiş ve damıtılmış**. Tekil dosyalar 2026-09-13'te silindi
> ([ADR-0086](../adr/kararlar-0064-0085.md#adr-0086)); **sayılar birebir korundu.**
> Çapa: `kronoloji-63-71.md#70`. **Dosya doldu (12 girdi); #75'ten itibaren [`kronoloji-75-86.md`](kronoloji-75-86.md).**

| # | tarih | başlık | kanca |
| :-- | :--- | :--- | :--- |
| [63](#63) | 2026-09-07 | Skor kartının boşlukları kapatıldı — **üçü de kendi aleyhimize** | `ölçülmedi` dört farklı şeyi saklıyordu · base **ÖLÇÜLEMİYOR** |
| [64](#64) | 2026-09-07 | Hakem paneli: ikinci aile · **κ EŞİĞİN ALTINDA** | κ **0,534/0,409** · manşet **11 puan** oynuyor |
| [65](#65) | 2026-09-09 | Donmuş TEST açıldı · frontier havuza girdi · iki alet kusuru | ham kütle **0,5804** · Sonnet-5 **önde** · `v1.0` **verilmedi** |
| [66](#66) | 2026-09-11 | Ürün yüzeyi temizlendi; temizlik **aygıtta üç kusur buldu** | tuzak **1.11 · 1.12 · 1.13** · KV: cevapların **%81,2'si** bayt olarak değişti |
| [67](#67) | 2026-09-12 | Alet onarıldı, çıpalar yeniden puanlandı, konteyner ayağa kalktı | **702 atfın 1'i** değişti ve **aleyhimize** · kusurların **dördü aynı gün bizim koddan** |
| [68](#68) | 2026-09-12 | S17: kuantizasyon eğrisi ölçüldü, **monoton çıkmadı** | `Q4 ≈ Q8`, **`Q5` ikisinin de üstünde** · artefakt **değişmedi** |
| [69](#69) | 2026-09-12 | Tabakalanmış duman koşusu, para kapısı GEÇTİ | tahmin **$1,97** ↔ düz ön-tahmin $2,81 |
| [70](#70) | 2026-09-13 | **On dört bulgu · κ borcu kapandı · kapı yeni birimde GEÇTİ** | tuzak 1.11 **dört farklı biçimde** ısırdı · öz-tercih **tersi** çıktı |
| [71](#71) | 2026-09-13 | Aşırı-red ekseni tek birime oturtuldu | **yayımlanan bir sayı DEĞİŞTİ, aleyhimize** — Sonnet-5 önde |
| [72](#72) | 2026-10-11 | F0 P1: eski geçmiş okundu | #62 çıpası puanlama için uygun değil · %68,4 formüle bağlı (0,6838 ↔ 0,6734) |
| [73](#73) | 2026-10-11 | F0.5 (a)(c): kütle tek yerden | eski alet beş tabloyu birebir verdi · 49 koşunun 7'sinde 10 sıfır iddialı kalem |
| [74](#74) | 2026-10-11 | F0.4: eğitim kilidi kodda | `fla` 0.5.1 önbellekli katmandan okundu · seed artık Modal'dan geçiyor |

---

<a id="63"></a>
## #63 — Skor kartının boşlukları kapatıldı: üç ölçüm, üçü de kendi aleyhimize

**2026-09-07 · harcanan $0,21 · GPU $0**
**Neden bu tur açıldı:** kart klasik skor kartı düzenine çevrildi ve tabloda **11 "ölçülmedi" hücresi** çıktı. İnsan kararı: *"tamamını kapamalıyız."*

**Bulgu 0 — dört boşluk, DÖRT FARKLI SINIF; kartta hepsi aynı görünüyordu.** *Asıl kusur buydu: `ölçülmedi` etiketi **boşluk · kayıt eksiği · insan-zamanı · karar** ayrımını siliyordu.* isabetsizlik = **insan-zamanı** · `$/cevap` = **kayıt eksiği** · M5 = **karar** (ADR-0039 rakip çıpasını reddetmişti) · base sütunu = **boşluk**.

**Bulgu 1 — isabetsizlik: *"biz iyiyiz"* cümlesi KURULMUYOR.** Üç rakip kolu **80/80 gözle** okundu, **birebir aynı tanımla**: biz **8/80** · 3.1 FL **8/80** · 3.5 FL **7/80** · 3.5 Flash **8/80**.
⛔ *"İsabetsizlikte berabereyiz, o hâlde eşitiz"* — **iki 8 aynı tabanda değil** (Flash 9 kalemde sustuğu için **71**'de sınandı, biz **75**'te).
⭐ **Asıl sarsıcı bulgu:** bizim isabetsiz olduğumuz **id 27 ve 42**, kendi öz-denetimimizde *"benim soru yazımım komşu maddeye kaydırdı"* diye işaretlediğimiz kalemlerdi. ***Rakip o tuzağa düşmedi*** ⇒ kaynağı soru **değil, model** olabilir ⇒ **B1 turunun hedefini doğrudan değiştirir.** ⭐ Üç kolda da isabetsiz olan **id 32·36·61** ise **ortak zorluk** adayı.

**Bulgu 2 — `$/cevap`: kayıt eksiği YENİDEN KOŞMADAN kapatıldı.** Yeniden üretim ~$1,22 tutacaktı. ⭐ **Ucuz yol ölçümle bulundu:** istem 80/80 **bayt-bayt aynı** ve üç Gemini **aynı tokenizer'ı** kullanıyor (3 kalemde sınandı, `prompt_tokens` birebir) ⇒ sayım yalnız **en ucuz** modelde yapıldı: **$0,48 yerine $0,0487'ye AYNI exact sayı.**
3.1 FL **$0,001895** · 3.5 FL **$0,001152** · **3.5 Flash $0,009914** · biz **$0**.
⭐ Girdi token'ı üçünde **birebir aynı (193.042)** — **eşit sınavın maliyet tarafındaki kanıtı.** ⭐ Kapı çıpası 3.5 Flash, 3.5 FL'nin **8,6 katı**. 🆕 *Bundan sonraki her koşu `prompt_tokens`'ı da yazacak.*

**Bulgu 3 — M5: düşük olmamız İKİ ŞEY BİRDEN söylüyor.** biz **0,3900** · base 0,4698 · 3.1 FL 0,6710 · 3.5 FL 0,7013 · **3.5 Flash 0,8241**.
⛔ ***"M5'te rakipleri yendik" KURULMAZ.*** M5 bir **anti-hedef** ve çıpa **base**'dir. *Düşük M5 bizim için "kaynağa dayanıyoruz" demek; **aynı sayı** aynı zamanda **"Gemini Türk hukukunu kaynaksızken bizden iki kat iyi biliyor"** demektir* (0,8241 ↔ 0,4105).
⭐ DRY rakiplere **uygulanamadı** — **ve ölçüldü ki gerekmiyor**: üç kolda da döngü **yok**.

**Bulgu 4 — base aynı bütçede ÖLÇÜLEMİYOR, ve sebebi bir bulgu.** Base geçerlilik kapısından **kaldı** (kesik **16/80 = %20**); **hakem çağrılmadı, kapı parayı korudu.** 🔬 16 kesiğin **15'i GERÇEK kesilme**, yalnız 1'i döngü ⇒ **DRY işe yaramaz** (M5'in tam tersi). Sebep: base **uzun, kaynak alıntılayan** cevaplar yazıyor ve 1536'ya sığmıyor.
⭐ **Karşılaştırma bulgunun kendisi:** base **kör modda** yalnız **2/80** kesik veriyor ⇒ ***base'i şişiren şey KAYNAKLARIN KENDİSİ*** — [#42](kronoloji-39-52.md#42)'nin bulgusunun **harness açıkken** ölçülmüş hâli: aynı bütçede **biz 4/80, base 16/80**.
⚠️🚨 **Modal bunu ÇÖZMEZ** — kesiklik donanımdan değil **bütçeden**. ⛔ Daha büyük bütçeli koşudan ***"ince ayar şu kadar kazandırdı" cümlesi KURULAMAZ*** — *fark ince ayardan mı bütçeden mi **ayırt edilemez**.*

**🆕 Borç — eval setinde altın etiket şüphesi (id 46).** **İki bağımsız gözle okuma, birbirinden habersiz, AYNI kalemi işaretledi.** Üç kolda da **sınır durum** sayıldı ⇒ **üç öznenin de sayısı bugün ALT SINIRDA.** 🚨 *Doğruysa bu bir **model kusuru değil ÖLÇÜM kusurudur**.* ⛔ Bugün düzeltilmedi (insan onayı usulü + donmuş TEST).

**Ders.** ***Bir skor kartında `ölçülmedi` yazmak, ölçmemekten daha tehlikeli olabilir*** — dört farklı şeyi tek etiket altında saklıyor. Dördü ayrıştırılınca **üçü $0,21'e kapandı**, dördüncüsü *"ölçülemedi"*ye dönüştü — **ve o dönüşüm kendi başına bir bulgu oldu.** ⚠️ **Bu turun üç sayısı da kendi aleyhimize çıktı. Üçü de olduğu gibi yazıldı.**

---

<a id="64"></a>
## #64 — Hakem paneli: ikinci aile eklendi, κ EŞİĞİN ALTINDA çıktı

**2026-09-07 · hakem $1,9774 raporlanan / $3,155 GERÇEKTE DÜŞEN · GPU $0** · [ADR-0074](../adr/kararlar-0064-0085.md#adr-0074)

İkinci hakem ailesi (`anthropic/claude-sonnet-5`) **aynı 80 cevabı** yeniden puanladı. ⛔ **Üretim yeniden koşulmadı — tek oynayan değişken hakem.**

**(1) κ eşiğin ALTINDA:** `tam_sadık` **0,534** · `atıf_temiz` **0,409** (aracın eşiği ≥0,6). `faithfulness` r = 0,705 · `cit_precision` r = 0,487.
**(2) Kayma TEK YÖNLÜ — sistematik katılık, gürültü değil.** Anthropic **24/80**'de daha düşük, **8/80**'de daha yüksek; A1 farkı **11,33 puan = gürültü tabanının 38 katı** ⇒ *"hakemler ayrışıyor"* **kurulabilir**.
**(3) Manşet sayı hakem seçimine duyarlı:** kütle **0,8011** ↔ **0,6940**. Coverage **değişmedi** (hakemden bağımsız); **farkın tamamı A1'den.**
**(4) 🚨 Ama bu tablodan *"kapı düştü"* SONUCU ÇIKARILAMAZ — ve çıkarmak ADR-0057 ihlali olurdu.** *Kapının eşiği çıpa rakibin kütlesinden türetildi ve **o sayı da `gpt-4o-mini`'nin hükmüdür**; ikinci hakem rakibi de aynı katılıkla notlarsa **eşik de düşer**.* **İki tarafı farklı hakemlerle kıyaslamak kapıyı SAHTE BİÇİMDE devirir.** ⇒ `0,6940` **açık borç**, **yayımlanmıyor.**
**(5) İddia düzeyinde κ KURULAMAZ — yapısal:** iki hakem farklı sayıda iddia çıkardı (**273 ↔ 341**) ve iddialar **birebir eşleşmiyor** ⇒ **kalem düzeyi tek ortak zemindir.**
**(6) 💸 Gerçek fatura, raporlanan bedelin 1,596 katı.** Sebep **kapının kendi marjı** — *docstring bunu zaten söylüyordu ama bütçe planı **liste fiyatıyla** yapılmıştı.* ⇒ **Bundan sonra her tahmin ×1,6.**
**(7) 💸 Liste fiyat oranı maliyeti TAHMİN ETMİYOR.** `sonnet-5` liste fiyatı ~**14 katı**, **gerçek bedeli 45 katı** ($0,0417 → $1,8604) — *hakem çok daha uzun gerekçe üretiyor.* **Duman koşusu şart.**
**(8) ⛔ `:batch` varyantı bu yoldan kullanılamaz** (senkron çağrıya **404**). Bedeli $0 oldu, olgu **koda damgalandı**.

**Kapanmayan.** Panel **iki aileli kaldı** — sebep sayıyla: bakiye **$3,45**, rakip kolunu ikinci hakemle puanlamanın tahmini **$2,81** (**bakiyenin %81'i**) ve kabul koşusunun puanlaması da aynı bakiyeden ödenecekti ⇒ **insan kararı: harcanmadı.** **Öz-tercih ölçülmedi** (Google özne ↔ Google hakem hücresi **aile dışlaması gereği yasak** — *o hücre hiçbir bütçeyle ölçülemez*). **Borcun kapanma koşulu tek:** `3.5 Flash`'ın aynı ikinci hakemle puanlanması.

**Ders.** ⭐ ***Tek hakem bir "eksiklik" değil, ÖLÇÜLMÜŞ bir kırılganlıktı*** — panel kurulmadan önce bu bir **usul borcuydu**; kurulduktan sonra **sayısı var**: manşet **11 puan** oynuyor. *Ama aynı ölçüm, düzeltmenin **tek taraflı yapılamayacağını** da gösterdi — hakem değiştirmek yalnız kendi kolunda yapılırsa elde kalan şey daha doğru bir sayı değil, **eşiti olmayan bir sınavdır**.*

---

<a id="65"></a>
## #65 — Donmuş TEST açıldı, frontier havuza girdi, iki alet kusuru daha

**2026-09-09 · $1,2127 (OpenRouter) + $0 (yerel GPU)** · [ADR-0077](../adr/kararlar-0064-0085.md#adr-0077)

**1. `KUNYE` taşınabilirliği.** İndeks künyesi korpusu **mutlak yol + `(bayt, mtime)`** ile damgalıyordu ⇒ `git clone` sonrası **her makinede `SystemExit`**. Yol **indeks dizinine göreli**, `mtime` vekili **sha256** oldu. `verify:` repo başka dizine kopyalandı, `mtime` tazelendi, indeks oradan yüklendi → **`recall@10` 0,9500** — *yeniden gömerek ölçülenin birebir aynısı, **bağımsız çapraz kontrol***. 🆕 `recall_indeksten.py` — *"dağıtılan indeks doğru mu"* sorusu bugüne kadar **ölçülemiyordu**.

**2. Frontier havuza girdi: `claude-sonnet-5` — ve ÖNDE.** Eşit sınav kanıtı: `recall@1/3/5/10` **dört basamak da bizim kolla birebir**; kesiklik 4/80 ↔ 4/80.
**Zorunlu ön adım — red dedektörü yeni ailede kalibre edildi** (8/8 gözle): alet 8 çekinme sayıyor, **3'ü açık yanlış pozitif**. **Kusur ADR-0061'in birebir aynı sınıfı, aile değişti:** *dedektör **son esaslı ibareyi** tarıyor, bu ailenin şablonu cevabı **şerh cümlesiyle** kapatıyor* ⇒ **olumlu hükmün İÇİNDEKİ olumsuzlama red sayılmış.** ⛔ `REJECT_RE`'ye dokunulmadı.

| okuma | BİZ `tgta_v1` | Sonnet-5 | fark |
| :--- | ---: | ---: | ---: |
| ALET | **0,8011** | 0,7911 | +1,00 p bize |
| GÖZ-orta | 0,8011 | **0,8223** | −2,12 p |
| **GÖZ-katı** | 0,8011 | **0,8348** | **−3,37 p** |

***Öne geçtiğimiz tek okuma, önde olmadığımızı bildiğimiz okumadır.*** *Aynı düzeltmeyi F0.4'te Gemini ailesinin **lehine** yapmıştık; burada kendi **aleyhimize** uygulandı.*
🚨 **B1 hakkındaki cümlemiz çürüdü.** *"Rakiplerden geride değiliz"* yalnız **Gemini havuzunda** doğruydu: `wrong_ref_rate` **BİZ 0,0769 ↔ Sonnet 0,0083 = 9,3× geride**. Deterministik doğrulayıcı ise *uydurma madde* ekseninde bizi **önde** gösteriyor (**0/114 ↔ 2/163**). *İkisi çelişmiyor, **farklı şey sayıyor**: madde **uydurmuyoruz**, var olan **yanlış** maddeye atıf yapıyoruz.* Karar değişmedi ama **gerekçesi düştü.**
**Bedel dersi:** tam koşu **$1,1932**, tahmin **$0,82** (**+%45**, `$1` kapısı aşıldı). *5 kalemlik duman koşusundan **×16 doğrusal ekstrapolasyon**, cevap uzunluğu soruya göre değişen bir özne için **kapı kurmaya yetmiyor**.* ⇒ Tabakalanmış duman ya da **%50 emniyet payı**.

**3. Donmuş TEST açıldı (insan onaylı, TEK KEZ) — ham kütle 0,5804.**

| | TEST | DEV |
| :--- | ---: | ---: |
| ham kütle | **0,5804** | 0,8011 |
| tavan `recall@10` | 0,7500 | 0,9500 |
| tavan kullanımı | 0,7739 | 0,8433 |
| uydurulmuş madde | **0/52** | 0/114 |
| `wrong_ref_rate` | 0,2424 | 0,0769 |

**Düşüşün ayrıştırılması:** toplam −22,07 p ⇒ **tavanın açıkladığı −16,87 p (%76)**, **açıklamadığı −5,20 p (%24)**. ⇒ *ADR-0069'un öngörüsü **doğrulandı ama tam değil** — model görülmemiş veride **tavanını da daha kötü kullanıyor**.* ***"Hepsi bileşim" denmedi.***
**Gözle okuma kapısı:** 9/40 çekinmenin dokuzu okundu, **yanlış pozitif 0** ⇒ **ALET = GÖZ.** *Alet bizim ailemizde doğru, başka ailelerde değil.*

**4. 🚨 Donmuş TEST'in yakaladığı kusur — `atif_dogrula.py`.** Alet önce **MÜLGA 2** dedi; okundu: altın `İŞ KANUNU (4857) Madde 111` **1. sırada**, model **doğru** cevaplamış ve **kanun numarasız** atıf yapmış. Korpusta bu ada **iki** kanun uyuyor (4857 yürürlükte · **1475 mülga**) ve `dogrula()` adayları `sorted()` ile gezip **ilk taşıyanı** döndürüyordu ⇒ **doğru cevap MÜLGA damgası yiyordu. Vatandaşa giden rozet buna bağlı.**
*Kodun kendi ilkesi — "yürürlükte tek satır bile varsa mülga sayılmaz" — tek bir `kanun_no` **içinde** vardı, **adaylar arasında** yoktu.* Bir seviye yukarı taşındı (TDD). `DOGRULANDI` **50→52**, `MULGA` **2→0**; manşet **değişmedi**.
⭐ **Ders: donmuş seti açmanın bedeli tek seferliktir; karşılığında yayına gidecek bir ROZET HATASI yakalandı.**

**5. Hüküm: `v1.0` verilmedi → `v0.3`.** *Donmuş TEST için **ön-kayıtlı sayısal eşik yoktu** ve sayı görüldükten sonra eşik yazmak ADR-0050'nin yasağıdır.* Hüküm **ADR-0064'ün kendi metnine** dayandırıldı ⇒ ***`v1.0`'ı bloke eden model değil, ÖLÇÜM AYGITI.***

**6. Araç katmanı ve regresyon kapısı.** `answer()`'a **bayrak eklenmedi**; ayrı fonksiyon yazıldı — diff **120 ekleme, 0 silme**. **Regresyon kapısı ölçülerek geçildi:** aynı betik iki kez koşuldu (bu görevin kodu ↔ görev öncesi, ayrı `git worktree`) → **80/80 kalem birebir aynı**.
⚠️ Kapı önce **KIRMIZI yandı; sebebi karşılaştırmanın yanlışlığıydı, kodun değil** (ölçüm hattının kümesiyle kıyaslanıyordu).
🚨 **Yan ürün — yeni borç: ürün yolu ile ölçüm hattı AYNI ŞEYİ ÇALIŞTIRMIYOR.** kesik veya boş **7/80 (%8,75)** ↔ 4/80 · **tamamen boş metin 4/80** ↔ 0. *Yedi kesik kalemin yedisi de ölçüm hattında `stop` ile tamamlanıyor ⇒ sorun **bütçe mimarisi**.* **ADR-0040'ın %5'lik kapısını ürün yolu geçemezdi.**

**7. Yayın.** Ağırlıklar ilk kez yayımlandı. Kartın ilk üç bölümü şu kısıtları bildiriyor: **model tek başına bildirilen başarımı üretemez** (indeks dağıtılmadı) · cevapların ~%5'i boş döner · hukuki tavsiye değildir.

**8. Sunucu bayrakları cevabı değiştiriyor — YAYINDAN SONRA yakalandı.** Belirsizlik sanıldı, **ölçülerek çürütüldü** (aynı sunucuda iki koşu **birebir aynı**). Kontrollü deney: `q8_0` → **SUSKUNLUK** (201 kar) ↔ varsayılan `fp16` → **ÇEKİNCELİ** (622 kar).
⇒ **Ürünün cevabı sunucu yapılandırmasına bağlı.** *Ağırlıklar bu bulgudan **önce** yayımlanmıştı ve kartta sunucu bayrakları **yazmıyordu** — yani **indiren kişi ölçtüğümüzden başka bir ürün koşacaktı**.* ⚠️ Farkın 80 kalemdeki toplam etkisi **ölçülmedi**.
⭐ **Ders:** *"aynı soru aynı cevabı verir"* değişmezi **yapılandırma sabitken** geçerlidir ve **yayımlanan bir artefaktta yapılandırma sabit DEĞİLDİR** — indiren kişi kendi bayraklarını seçer. ***Yayın kartı, ölçüm künyesinin yerine geçmez; künyeyi TAŞIMAK zorundadır.***

---

<a id="66"></a>
## #66 — Ürün yüzeyi temizlendi; temizliğin kendisi aygıtta üç yeni kusur buldu

**2026-09-11 · Bedel $0** (hakem hiç çağrılmadı) · [ADR-0079](../adr/kararlar-0064-0085.md#adr-0079) · [ADR-0080](../adr/kararlar-0064-0085.md#adr-0080)
> **Turun tek cümlesi:** *ürün yüzeyi temizlendi; temizliğin kendisi, **ölçüm aygıtında üç yeni kusur** buldu.* Ağırlıklara dokunulmadı, **yayımlanmış hiçbir sayı değişmedi.**

**1. Ürün yüzeyi kusur temizliği (TDD, 10 kırmızı → yeşil).** Boş sorgu kapısı (`servis.answer()` içinde — *arayüzlerde değil*, **uydurulmuş uzunluk eşiği yok**) · iskele işareti süzgeci (**yalnız sunum katmanında**; `Cevap.metin` **ham** kalır) · `madde_sayisi` · TUI donması · **statik kapsam satırı** — *sınıflandırıcı **kurulmadı**: yanılan bir kapsam sınıflandırıcısı vatandaşa "bu konu kapsamda yok" diyerek **cevabı olan soruyu öldürür**.* Takım **178 → 216 yeşil**.

**2. Asıl ders: testler yeşilken duran DÖRT "hata vermeden yanlış".** *Adım 10 yeşildi, şartname uyumu dört kilitli kararda da tamdı — ve bağımsız kod incelemesi yine **dört ayrı sessiz yanlış** buldu. **Hiçbirini test yakalamamıştı, çünkü hiçbiri hata vermiyordu.***
① `tui.py` `bicimle()`'yi **hiç çağırmıyordu** ⇒ `##begin_quote##` **vatandaşa gidiyordu** ② kapsam satırı *"40.496 madde"* diyordu, **retriever mülgayı eliyor** ⇒ doğru sayı **37.949** ③ `madde_sayisi` *"Geçici Madde 1"* ile *"Madde 1"*i **aynı sayıya** indiriyordu (*karışırsa `recall@k` şişer ve **hiçbir yerde hata çıkmaz***) ④ TUI'de iki ardışık Enter **iki çalışan** başlatıyordu ⇒ **ikinci sorunun altında birinci sorunun cevabı.**
**Alıntı sınırı da düzeltildi:** işaretler **silinmek** yerine tipografik tırnağa çevrildi — *işaretler gürültü değil, **"burası kanunun kendi cümlesidir"** sınırıdır; silmek **kanunun lafzı ile modelin yorumunu** tipografik olarak ayırt edilemez hâle getiriyordu.*
**Kök neden kayda geçti (kusur 17):** `tui.py` ve `cli.py` **iki paralel sunum katmanıdır**; iki sızıntı tek tek kapatıldı, **kök neden duruyor.**

**3. Ön-kayıtlı ÖLÇÜM: rozet EKLENMEDİ** (n=80, CPU, 65,7 s, **$0**, hakemsiz). **Rejim çıpası tuttu** (`recall@10` 0,9500 birebir) ⇒ **ayrışmanın yokluğu ölçümün kusuru değil.** Altı göstergenin hiçbiri ayırmıyor; en iyi adayda dört kaçağı yakalayan eşik **23/76** doğru kalemi *"zayıf"* damgalardı. `marj_1_2` ve `entropi`'de **kaçırılanların medyanı DAHA İYİ** — ***retriever yanılırken de kendinden emin görünüyor.***
**n=4 damgası zorunlu.** **Eşik uydurulmadı, kusur 5a AÇIK KALIR — ve bu bir BULGUDUR, başarısızlık değil.**
*Aynı belgenin iki **yorum** cümlesi tablolarıyla çelişiyordu; sayılar ve hüküm **değişmedi**, iki gerekçe cümlesi düzeltildi ve her sayı ham veriden **yeniden hesaplandı**. Kural: **çelişki damgalanır, sessizce düzeltilmez.***

**4. Konteyner rejim kilidi.** *Paketleme burada kolaylık değil **rejim kilididir**: bağlayıcı bayraklar bugüne kadar yalnız **düz metin** olarak üç belgede yazılıydı.* Testler compose'u **`yaml.safe_load` ile ayrıştırarak** sınıyor, **metin araması yapmıyor**; indirme kapısı **ağsız**. **İkinci bir `--host` sapması doğdu** ve kilitli beş kararda **yoktu** ⇒ **insan damgası bekliyor**.
**Adım 4'ün iki boyut tahmini ölçümle düzeldi** (`du -sb`, **tahmin değil**): `models/**` **74,2 GiB** (plan *"2,6 GB"* diyordu — **o tek GGUF'un boyutuydu**) · indeks **158,2 MiB** (*"79 MB"* **tek dosyaydı**).

**5. KV kuantizasyonu 80 kalemde, hakemsiz, $0.** *Kusur 2 bugüne kadar **tek soruda** gözlenmişti.* Düşen tek bayrak çifti `--cache-type-k/-v q8_0`:

| eksen | çıpa `q8_0` | `f16` |
| :--- | ---: | ---: |
| **bayt olarak değişen cevap** | — | **65/80 (%81,2)** |
| karakter medyanı | 715,0 | 706,5 (−%1,2) |
| çekinme | 5/80 | 5/80 |
| tamamen boş | 0/80 | 0/80 |
| durum sınıfı `CEVAP/CEKINCELI/SUSKUNLUK/KESIK` | 70/1/5/4 | 71/1/5/3 |
| katı atıf kapısı reddi | **0** | **3** |
| uydurulmuş madde | **0/114** | **0/152** |

**Manşet: cevapların %81,2'si bayt olarak değişti, buna karşılık HİÇBİR SAYAÇ birden fazla kalem oynamadı.** *Toplulaştırılmış eksenler kıpırdamadı, **kalem düzeyi büyük oynadı**: 6/80 kalem durum sınıfı değiştirdi ve toplam uzunluk farkını **dört kalem** taşıyor — **döngü sınıfı iki rejimde de var, değişen hangi kalemin döngüye girdiğidir**.*
**Kütle üzerine cümle KURULMADI** (hakem para ister, para kapısı **insan kararıdır**).
**Kusur 2 kaydının tek-soruluk gözlemi ÇÜRÜDÜ** — 80 kalemin **hiçbirinde tekrarlanmadı**. *Bu bir **çürütmedir**, "doğrulanamadı" değil.*
Çekinme sayısı iki koşuda da 5 **ama bileşimi farklı**: aşırı-red **4 → 3**, altın gelmediği için susma **1 → 2**.
**fp16'nın ürettiği, çıpada hiç görülmeyen bozulma sınıfı (kusur 19):** model **istem yer tutucusunu harfiyen bastı** (**0/80 ↔ 2/80**). ⇒ *"KV kuantizasyonu manşet dağılımı bozmuyor"* **denebilir**; *"cevaplar aynı kalıyor"* **denemez**.
**Kontrol değişkeni sızıntısı — şerh:** 2 kalem farklı kaynak gördü; sebep **KV değil**, çıpadan **sonra** gelen yürürlük süzgeci ⇒ *"tek değişken KV"* **tam doğru değildir**, temiz alt küme **n=78**.

**Adım 2 — aynı koşunun KÜTLESİ, hakemle** (insan bedel kapısı geçildi): kütle **0,8011 → 0,7932 (−0,79 p)** · `coverage` **değişmedi** · `A1` −0,84 p · **`wrong_ref_rate_micro` 0,0769 → 0,1553 = 2,0× KÖTÜLEŞME.**
**Kütle farkı tek yönlü hükme YETMİYOR.** *−0,79 p, devralınan tabanın 2,8 katı; **ama o taban aynı cevaplara** hakemi yeniden koşmanın gürültüsüdür ve **burada cevaplar da değişti**.* **Bu koşu çiftine ait aynı-cevap tabanı ÖLÇÜLMEDİ.** Kalem düzeyinde **18/80** kalemin `faithfulness`'ı **iki yönlü** oynadı ve toplam fark bu salınımların **artakalanıdır**. ⇒ Kurulabilen: *"fp16 KV kütleyi **YÜKSELTMEDİ**."* Kurulamayan: *"fp16 modeli 0,8 puan bozar."*
**Tabanın açıkça üstündeki TEK eksen atıf isabetidir ve KÖTÜLEŞTİ** — *iki bağımsız alet aynı şeyi söylüyor.* ⇒ **Öneri — kapı değil: taşıyıcı rejim `q8_0` kalsın.**

**Adım 3-4 — REJİM DEĞİŞİKLİĞİ** (insan kararı, DUR-ve-SOR): **boş metin 4/80 → 0/80** · kesik **%8,75 → %3,75** ⇒ ADR-0040 kapısı **GEÇTİ** · **`sha256` değişen 4/80** (76 kalem **birebir**) ⇒ **CERRAHİ** · getirilen kaynak değişen **0/80**. **Kütle bu koşuda HESAPLANMADI.**
**İki kabul edilen bedel:** ① B10'a **+2 kalemlik yük** (bu tur **ölçmedi, yalnız kaydetti**) ② **kusur 20** — 2. geçiş `reasoning_content`'e bağımlı, sunucu varsayılanı değişirse **sessizce tek geçişe düşer**; **testle çivilenemiyor** (*bağımlılık sunucunun davranışında, kodun değil*).

**6. Turun en pahalı bulgusu: ölçüm aygıtında ÜÇ YENİ KUSUR.**
**1.11 — duman koşusundan doğrusal maliyet tahmini kapı kurmuyor** (tahmin $0,82 ↔ gerçek $1,1932, kapı **%45** aşıldı). **Kural yazıldı (kod değil).**
**1.12 — künyenin KV satırı SABİT DİZE.** *Aynı satırdaki `$CTX`·`$NGL`·`$PORT` değişkenken **KV değil**; betik dış sunucuya bağlandığında o sunucunun KV ayarını **hiç okumuyor**.* Bu koşunun logu **`q8_0` dedi, gerçek `f16` idi** ⇒ ***kıyasın ölçmek için var olduğu TEK DEĞİŞKEN künyede yanlış görünüyordu.*** Yakalayan şey künye değil, `/proc/<pid>/cmdline` okumasıydı; **bağımsız ikinci kanıt sunucu günlüklerinden** geldi. **İroni aynı betiğin iki satır üstünde yazılı:** *"künyede görünmeyen bayrak sessizce düşer, koşu geçerli görünür."* ⇒ **Genel kural: künyedeki her alan ya bir DEĞİŞKENDEN ya bir ÖLÇÜMDEN gelir; elle yazılmış bir alan künyeyi KANIT OLMAKTAN ÇIKARIR.**
**1.13 — atıf doğrulayıcı kanun adını GEVŞEK eşleştirip YANLIŞ kanuna çözüyor.** *"Gelir Vergisi Kanunu Madde 73"* → `1319` **EMLAK VERGİSİ** → `MADDE_YOK` = **uydurma** damgası; oysa madde korpusta **VAR** (`193/Madde 73`, adı **parantezli**). Korpusta **16 kanun** parantezli ad taşıyor.
**Bu alet, yayımlanan `0/114` manşetini üretendir.** Çıpada `MADDE_YOK` **hiç yok** ⇒ manşet **yanlış-pozitif yönünden temizdir.** *Fakat aynı gevşeklik **ters yönde** de çalışabilir — yanlış çözülen bir kanunda aynı numaralı madde varsa atıf **yanlış `DOGRULANDI`** alır — **ve o yön ÖLÇÜLMEMİŞTİR.*** **Çürütülen bir şey yoktur; ÖLÇÜLMEMİŞ BİR YÖN vardır.**

**7. Ders.** ***Bu turda ürün yüzeyinde kapatılan her kusur, aygıtta bir kusur açığa çıkardı — ve hiçbirini sayısal bir kapı yakalamadı.*** Dördünü **kod incelemesi** yakaladı (testler yeşilken), üçünü **künyeyi ya da aletin kendisini doğrudan koşturmak**. *Kapılar geçilmişti: Adım 10 yeşildi, şartname uyumu tamdı, geçerlilik kapısı geçiyordu, künye dolmuştu.*

**§13 — turun ikinci dersi: TOPLULAŞTIRILMIŞ SAYAÇ NEYİ GİZLER?** İki örnek ölçüldü, ikisi de aynı şeyi söylüyor — **sayı sabitken içerik değişebiliyor**: ① çekinme **5/80 ↔ 5/80 ama küme farklı** ② kütlenin **−0,79 puanı, 18 kalemin iki yönlü salınımının ARTAKALANIDIR.**
> **Kural: toplulaştırılmış bir sayaç kıpırdamadıysa *"hiçbir şey değişmedi"* demek değildir. Sayacın BİLEŞİMİ ayrıca raporlanmazsa, değişim kayda geçmeden geçer.**

---

<a id="67"></a>
## #67 — Alet onarıldı, çıpalar yeniden puanlandı, konteyner ayağa kalktı

**2026-09-11/12 · Bedel $0,045067** (turun tek hakem çağrısı #66'nın ekinde) — *bu kaydın işlerinin tamamı **hakemsiz, GPU'suz, ağsız***
[ADR-0081](../adr/kararlar-0064-0085.md#adr-0081) · [ADR-0082](../adr/kararlar-0064-0085.md#adr-0082) · **31 commit**
> **#67'nin dersi bir adım öteye gidiyor:** bu turda bulunan kusurların **dördü bizim aynı gün yazdığımız koddandı** ve **hiçbirini test yakalamadı.** Yayımlanan **tek** sayı değişti ve o da **aleyhimize**.

**1. Yedi insan kararı uygulandı (kusur 14-20).** **14** `madde_sayisi` **ölü alandı — SİL** (YAGNI) · **15** kapsam satırı **üç yüzey birden** aldı · **16** rozet ile gövde birbirini yalanlıyordu → **altıncı `Durum`: `BOS_SORGU`** (*tip düzeyi değişiklik olduğu için **kod yazılmadan önce** karara bağlandı*) · **17** iki paralel sunum katmanı **BİRLEŞTİR** (rozet **parametre**, bool bayrak yok) · **19** fp16'da yer tutucu — **silinmedi, dürüstçe işaretlendi** · **20** ikisi de: **erken ve gürültülü patlama** + `--reasoning-format deepseek` **pinlendi**.

**2. Atıf doğrulayıcı ONARILDI ve ÇIPALAR yeniden puanlandı.** *Model çağrılmadı, donmuş TEST'e yeni soru sorulmadı — diskte **zaten duran** cevaplara **düzeltilmiş alet** yeniden uygulandı.* **TDD:** 8 test, onarımdan önce **4 kırmızı**; kalan 4 bilerek konmuş **regresyon çıpasıdır.**
**Çözüm kuralı — tek cümle:** ad çözümünde **en çok TEK gevşemeye** izin verilir (≥2 sözcüklü **sonek** **ya da** baştaki fazla sözcüklerin atılması) — **ikisi birden ASLA**; ikisi birden gerekiyorsa hüküm **`AYRISTIRILAMADI`** ve **sessizce bir kanun SEÇİLMEZ.** Ayrıca `Hukum` artık **çözülen kanunun ADINI** taşıyor, *ki yanlış çözüm **gözle görülebilsin**.*
**Sentetik prob ($0), 16 parantezli kanun:** doğru kanuna çözdü **0/16 → 7/16** · **YANLIŞ kanuna çözüp yine `DOGRULANDI` aldı 7/16 → 0/16**.
**Çıpalar OYNAMADI — ve bu bir bulgudur, boş bir sonuç değil:** DEV `114 → 114` · donmuş TEST `52 → 52` · fp16 `149 → 150`. *`g22-atif-cozum` "manşet temiz ama **TESADÜFEN** — korunma aletten değil **ÖRNEKLEMDEN**" demişti; **artık korunma ALETTEN geliyor** ve manşet aynı yerde duruyor.*
**Geniş süpürme:** 94 dosya · **11.634 atıf**, **41'inin (%0,35)** hükmü değişti. **Tek gerçek kayıp:** korpus adı `SİLÂHLI` (şapkalı `â`) yazıyor, ayrıştırıcının sözcük sınıfı `â` taşımıyor — *eski gevşek çözüm bu **yazım farkını** tesadüfen kurtarıyordu.* Bedeli **tek vakada** ve o vaka **geçersiz ilan edilmiş** bir koşuda.

**3. RAKİPLER de yeniden puanlandı — sonuç ALEYHİMİZE, öyle yazıldı.** İnsan kararı: *"Sonuç aleyhimize çıksa bile yazılır: bugün tabloda **iki farklı aletin sayısı yan yana** duruyor."*
**Kalibrasyon kapısı önce koşuldu ve GEÇTİ:** yayımlanan boru hattı **bizim** kolumuzda koşuldu ve `harness_tablo.json` ile **alan alan birebir** çıktı ⇒ **kapı geçti ⇒ rakiplere geçilebildi.**
**702 atfın YALNIZ 1'i değişti** ve o da **rakip aleyhine yanlış** basılmış bir damgaydı: `gemini-3.1-flash-lite` **`1/152` → `0/153`** (gözle okundu; korpus tanığı **vardır ve mülga değildir**).
**Kaybettiğimiz şey ve karşılığında aldığımız şey — ikisi de yazılır.** *"Uydurulmuş madde numarası" bugüne kadar rakiplerin **tamamının** üstünde olduğumuz **tek deterministik** eksendi; `3.1 flash-lite` artık bizimle **eşittir**.* Karşılığında **eşit sınav** sağlanmıştır: **beş sütunun beşi de aynı, onarılmış aletin sayısıdır.** Her kol **iki kez** koşuldu, çıktılar **bayt bayt aynı.**
**🚨 Satırın BİRİMİ hiçbir yerde yazılı değildi — ve bu bir ön sondayı zaten yanıltmıştı:**
```
pay   ("uydurulmuş madde") = MADDE_YOK + KANUN_YOK
payda ("doğrulanan atıf")  = DOGRULANDI        <- TOPLAM ATIF DEĞİL
```
*Ön sonda "3.5 Flash-Lite 4 → 3" okumuştu; **yeniden üretilemedi ve çürütüldü** — o kolda **hiçbir atfın hükmü değişmedi**; düşüş bir **birim kaymasıydı**.* Çelişki **iki yerde** damgalandı. **Yan kusur (25) kapatılmadı:** Sonnet-5 hücresi **farklı birim** kullanıyor.

**4. Kusur 21 — ürün yüzeyi ile ölçüm hattı AYRIŞMIŞTI, ve ayrışma büyüktü.** `araclar.py` **kendi ikinci ad indeksini** taşıyordu (tuzak **2.18**: *aynı ölçümün ikinci bir aleti*) ⇒ **vatandaşa giden atıf doğrulaması ile yayımlanan sayıyı üreten doğrulama AYRIYDI.**
**Ayrışma önce ÖLÇÜLDÜ, sonra onarıldı:** 892 kanun adında **19** · parantezli 16'da **7** · çıpanın gerçek atıflarında **24/114**.
**Ve ayrışmanın YÖNÜ beklenenin tersiydi:** *ürün yüzeyi onarımdan **daha da katı** bir eski hâl taşıyordu — yanlış kanuna basmıyordu, ama parantezli adları **hiç çözemiyor**, modele "böyle bir kanun yok" diyordu.* Sonrası **0/892 · 0/16 · 0/114**. **Eşdeğerlik kanıtlandı:** 94 dosya · 11.634 hüküm, `sha256` **birebir**.

**5. Konteyner uçtan uca ÇALIŞTI, ama ÖNCE KIRILDI** — *sıra olduğu gibi anlatılır, çünkü **kırılmanın kendisi turun en öğretici bulgusudur**.*
**5.1 İmaj ÖLÇÜLDÜ (tahmin yazılmadı):** build **234 sn** · `hakhukuk:0.3.0` **2,13 GB** · llama.cpp imajı **6,99 GB** · toplam **9,12 GB**. `.dockerignore` **74 GB'lık `models/**`'ı kesti**; imajda tek bir `.gguf`/`.npy`/`safetensors` **yok** (`find / -xdev` → **0 eşleşme**).
**G20 ajanının torch endişesi ÇÜRÜTÜLDÜ:** imajın içinden ölçüldü — `torch 2.14.0+cpu`, `version.cuda = None` ⇒ **CPU tekerleği**, katman **943 MB**'da kaldı.
**5.2 `docker compose up`: indirme kapısı GEÇTİ, ama her soru HTTP 500.** **`sha256` + bayt kapısı GERÇEKTEN ateşlendi ve TUTTU**; indeks **volume'de** bulundu ve HF yedeğine **hiç gidilmedi**. **Ama gerçek soru 500 verdi (kusur 32).**
**Kök sebep, ve bu turun en öğretici bulgusu:** indeksin künyesi korpus yolunu **indeks dizinine göreli** tutuyordu; konteynerde indeks **volume'de** olduğu için `/corpus/`'a çözülüyor ve korpus orada değil. ⇒ ***Bu, `G8 Adım 1b`'nin TAŞINABİLİRLİK onarımının TERS YÜZÜDÜR: mutlak → göreli değişikliği `git clone`'u ONARDI, ama indeksin repo ağacının DIŞINA taşındığı tek düzeni KIRDI.*** **Sessiz değildi:** `SystemExit` ile gürültülü patlıyordu.
**5.3 Çözümün inceliği ve S18 kapısı.** Korpusu öylece koymak **yetmezdi** (`../../` **iki** seviye çıkar) ⇒ **repo düzeni birebir aynalandı**. **S18 kapısı kuruldu:** korpus imajda **ve** volume'de; `sha256` eşitliği **her koşuda** sınanır, tutmazsa **iki daemon da HİÇ BAŞLAMAZ**.
**Sonuç: uçtan uca HTTP 200**, **ikinci, farklı** bir soruyla da doğrulandı; model **yeniden inmedi** (sha + bayt birebir).
**Üç şerh gizlenmedi:** (a) `git clone` sonrası indeks dizinini **insan doldurmak zorunda** — *kusur **kapanmadı, görünür oldu*** (b) korpus artık **üç yerde**; **repo ↔ imaj ayrışması SINANMIYOR** (c) uçtan uca doğrulama **iki soru** ile yapıldı.

**6. GÖZ KAPISININ BİLANÇOSU — bu kaydın asıl dersi.** Üç insan gözü kapısı **süit YEŞİLKEN duran dört kusuru** yakaladı:
**26** sunumda **çift tırnak** — ***bu kusuru AYNI GÜN BİZ EKLEDİK*** ve testlerimiz **tırnaksız** alıntıyla yazıldığı için bu hâli görmemişti · **27** madde biçimi tutmuyor (korpusun **ham** tutarsızlığının ekrana yansıması), **AÇIK** · **28** `hakhukuk-*` komutları **çalışmıyordu** — iki sebep: paket **hiç kurulmamıştı** ve **latent kusur** (`license` PEP 639 **dize** biçimi ↔ `setuptools>=68`; *yalıtımlı kurulum çalışıyor, **`--no-build-isolation` PATLIYORDU***) · **30** `cli.py` künye yolunu **repo köküne göreli** çözüyordu ⇒ ***bu kusuru da AYNI GÜN BİZ EKLEDİK***; **konteynerin İÇİNDE** yakalandı, *host'ta **görünmüyordu** çünkü paket **editable** kurulu.*
⚠️ **DÜZELTME:** kapanış bloğunda önce *"273 test yeşilken"* yazılmıştı ve **yanlıştı** — dördü aynı ana ait değil (26·27 → süit **267** · 28 → **273** · 30 → **274**). *Tek bir yuvarlak sayıya bağlamak üçünü de yanlış anlatır.*

**Turun sayıları:** test **178 → 281 yeşil** · commit **31** (turun tamamı 50) · **push YAPILMADI** (60 gönderilmemiş commit) · harcanan **$0,045067** · ADR **0079·0080·0081·0082** · tuzak **1.11·1.12·1.13** · açık kusur kaydı **13 → 32 kalem** · **ağırlıklar değişmedi.**

**8. Ders.** *#66'nın dersi "ürün yüzeyini temizlemek aygıtta kusur buldu" idi.* **#67'nin dersi bir adım öteye gidiyor:** bulunan kusurların **dördü bizim aynı gün yazdığımız koddandı** ve **hiçbirini test yakalamadı** — ***çünkü testler, kusurun GÖRÜLMEDİĞİ varsayımla yazılmıştı:*** alıntı testi **tırnaksızdı**, kurulum testi **editable** kurulumun altında koşuyordu, yol testi **repo ağacının içinden** bakıyordu. ⇒ ***Kapıların yakaladığı şey kodun yanlışlığı değil, TESTİN KÖRLÜĞÜYDÜ; test bir varsayımı paylaştığı sürece o varsayımı sınayamaz.*** *Ve bir onarımın başka bir düzeni kırması, **"onarım da bir değişikliktir ve kendi regresyonunu ister"** kuralının bu hattaki **üçüncü** kanıtıdır.*

---

<a id="68"></a>
## #68 — S17 kapandı: kuantizasyon eğrisi ölçüldü, monoton çıkmadı

**2026-09-12 · üç puanlama $0,1210** (tahmin ~$0,12, kapı geçti) · GPU yerel $0 · Kapatılan: **S17**

`models/merged/tgta_v1` → f16 GGUF → `Q5_K_M` ve `Q8_0`. Ayrıca yayımlanan `Q4_K_M`'nin **bugünkü** araç zinciriyle **bit-bazında** yeniden üretilip üretilemediği sınandı. Dört kol da **aynı rejimde**.

| kol | dosya boyutu | kütle | coverage | A1 | kesiklik |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `Q4_K_M` @2026-08-03 (yayımlanan çıpa) | 2.783.446.720 | 0,8011 | 0,9375 | 0,8545 | %5,0 |
| `Q4_K_M` @2026-09-12 | 2.783.446.688 | 0,7921 | 0,9375 | 0,8449 | %5,0 |
| **`Q5_K_M`** @2026-09-12 | 3.161.425.568 | **0,8673** | 0,9750 | 0,8895 | %2,5 |
| `Q8_0` @2026-09-12 | 4.610.580.128 | 0,7909 | 0,9250 | 0,8550 | %1,2 |

n=80 ⇒ çözünürlük adımı **1,25 p**. `Q4`@ağustos ↔ `Q4`@bugün **−0,90 p (BELİRSİZ)** · `Q4`↔`Q8` **−0,12 p (BELİRSİZ)** · `Q4`↔`Q5` **+7,52 p (ölçülebilir)** · `Q5`↔`Q8` **−7,64 p (ölçülebilir)**.
**Eğri MONOTON DEĞİL:** `Q4 ≈ Q8`, **`Q5` ikisinin de belirgin üstünde.** Mekanizma **coverage** ekseninde (75/80 → 78/80 → 74/80), A1 dar bantta sıkışık ⇒ *kuantizasyon burada **doğruluğu değil çekinme eşiğini** oynatıyor gibi görünüyor* — **ama bu bir GÖZLEM, AÇIKLAMA değil**; mekanizma hipotezi ölçülmedi, **hüküm kurulmadı.**

**BULGU-G — araç zinciri sapması var ama davranışsal fark ölçülemez düzeyde.** Yayımlanan GGUF ile bugünkü kopyası **bayt-bayt aynı değil** (−32 bayt, farklı `sha256`). *Bu, deponun **"yayımlanan artefakt yeniden üretilebilir"** iddiasına karşı ölçülmüş bir sınav ve **sonucu kısmi**: dosya farklı ama davranış **çözünürlük altında**, üretim tarafı **neredeyse örtüşüyor** (ort. completion token 782,5 ↔ 782,4). **İki bulgu birlikte yazılıyor, biri diğerini geçersiz kılmıyor.***

**Kusur 33 bu turda CANLI yakalandı.** `yeniden_uret.sh`'ın `recall@10` kapısı **var olmayan alanları** okuyup **her koşuda 0,0000** basıyordu — `Q5_K_M` kolunun ilk denemesi bu yüzden **geçerli bir üretimi GEÇERSİZ sayıp attı.** Eş zamanlı kapatıldı; kalibrasyon **çıpanın kendi verisinde ve bu turun üç kolunda** doğru sonuç verdi.
**BULGU-E — yeni tuzak: sağlık kontrolü BAŞKA BİR SÜRECİN sunucusuna 200 alıyor.** Port 8080'i işi bitmiş bir konteyner çifti tutuyordu; yeni `llama-server` **bağlanamadan öldü**, ama `curl /health` döngüsü **eski sunucudan `200 OK` aldığı için** betik *"hazır"* deyip devam etti ⇒ **8 kalem YANLIŞ MODEL karşısında sessizce üretildi.** Yakalanma: `ps -p <pid>` + `/v1/models` doğrulaması. **Sonraki her sunucu başlatmasında `/v1/models` doğrulaması zorunlu hâle getirildi.** → tuzak **7.8**.

**Karar — ALINMADI.** *`Q5_K_M`'nin daha yüksek kütle vermesi artefakt değişikliğini **tetiklemiyor** — bu turun ön-kaydı böyleydi ve korundu.* ***Eğri bir İFŞADIR: "bu hassasiyeti seçtik, bedeli/kazancı şu kadarmış."***

---

<a id="69"></a>
## #69 — ADIM 6.4 kapandı: tabakalanmış duman koşusu, para kapısı GEÇTİ

**2026-09-12 · toplam $0,2960** (duman ölçümü, **hiçbir hükme girmiyor**) · Kapatılan risk: tuzak **1.11**

`3.5 Flash` kolunun tam koşusu 6.5'te `claude-sonnet-5` hakemle puanlanacak. Önce maliyeti ölçmek için **tabakalanmış** duman koşusu: 80 kalem `completion_tokens`'a göre **tercile'landı** (26/26/28), her dilimden **dilim-içi 1/3 ve 2/3** konumundaki kalemler seçildi (n=6). Sağlayıcı pinlendi — *körü körüne `OpenAI` yazılmadı, `judge_providers` ile doğrulandı.*

| dilim | ort. `completion_tokens` | gerçek maliyet (n=2) | ort./kalem |
| :--- | ---: | ---: | ---: |
| kısa | 237,3 | $0,0477 | $0,02385 |
| orta | 650,4 | $0,0613 | $0,03065 |
| uzun | 1173,9 | $0,0395 | **$0,01975** |

**Ağırlıklı tahmin $1,9700** — ADR-0074'ün düz ön-tahmininin (**$2,81**) **~%30 altında.**
**Şaşırtıcı yön: UZUN dilim en DÜŞÜK ortalama maliyeti verdi** — *cevabın kendi `completion_tokens`'ı ile **hakemin ürettiği** token sayısı (asıl fatura kalemi) **düz orantılı değil**.* ⇒ Tuzak 1.11'in dersi **ikinci kez, farklı yönden** doğrulandı: **tabakalama bile tam düz bir ilişki vermiyor; n=6 bir aralık değil NOKTA tahmini üretiyor.**
**Çapraz doğrulama:** birleşik koşu ($0,1475) ile üç dilimli koşunun toplamı ($0,1485) örtüştü; **bakiye farkı ikisinin toplamıyla BİREBİR eşleşti** — *iki bağımsız ölçüm yöntemi aynı sayıyı verdi.*
*Küçük determinizm notu: id 65 birleşik koşuda 17 iddia, dilimli koşuda 16 — `temperature=0` **"tam deterministik değil"**, betiğin kendi uyarısı; diğer 5 kalem birebir.*
**Kapı:** `tavan = min($1,97×1,5; $8,00) = $2,955` ⇒ **GEÇTİ.** *(Formülün **kendine-referans** doğası not edildi: `tavan` `tahmin`den türediği için kapı fiilen *"tahmin $8,00'i aşıyor mu"* sorusuna indirgeniyor.)*

---

<a id="70"></a>
## #70 — On dört ölçülmüş bulgu, κ borcu kapandı, kapının üç maddesi yeni birimde GEÇTİ

**2026-09-12 (ölçüm) / 2026-09-13 (kayıt) · ADIM 6.1-6.7 toplamı ≈$5,73** (6.5 $1,6831 · 6.6b $2,6212 · 6.6d $0,8993 · 6.4 $0,2960 · 6.3c $0,1210 · 6.3b $0,0438) · **bu kaydın kendisi $0** · [ADR-0084](../adr/kararlar-0064-0085.md#adr-0084) · **53 commit**
> **#70 turun geri kalanıdır:** korpus artık **kimlikle** bulunuyor, indeks HF'te **public**, ürün yolunun **kendi kütlesi ilk kez** ölçüldü, S17 eğrisi çıkarıldı, **κ borcu kapandı** ve kapının üç maddesi **iki bağımsız hakem ailesi altında da GEÇTİ**. **Ağırlıklar bu turda da hiç değişmedi.**

### 1 · Korpus ve indeks (6.1-6.3)

**BULGU-C — 🚨 en tehlikeli bulgu, HENÜZ ZARAR VERMEDEN yakalandı.** İki koşunun `id` alanları **farklı sıralamaları** gösteriyordu: soru **metinleri 80/80 birebir eşleşirken** `id` ile eşleşen kalem **0/80**'di. ***`id` üzerinden birleştirme yapılsaydı 80 kalemin 80'i de YANLIŞ ALTIN MADDEYE karşı puanlanır, hata vermezdi.*** Korunma: birleştirme **normalize edilmiş soru metni** üzerinden, ve 80↔80 eşleşme birleştirmeden **ÖNCE** iddia edildi.
**BULGU-B — ürün yolunda boş cevap ilk kez ölçüldü: 0/80** (konteynerden) ⇒ *"ölçülmedi"* şerhi kapandı; **ADR-0080'in mekanizması konteynerde de tutuyor.**
**BULGU-D — ürün yolunun kendi kütlesi ilk kez ölçüldü: 0,7792** (çıpa 0,8011, **−2,19 p**). 🚨 **Ayrıştırılamayan karıştırıcı:** bu koşuda `judge_providers` `["Azure","OpenAI"]`, çıpada `["OpenAI"]` (**tuzak 2.7'nin tekrarı**); kalem düzeyinde dağılım **ölçülemiyor** (koddan doğrulandı). ⇒ *"−2,19 p'nin ne kadarı ürün yolundan, ne kadarı hakem taşıyıcısından"* **CEVAPSIZ kalıyor ve öyle yayımlanıyor.** **Ürün yolunun kütlesi kapı maddesine GİRMEZ.**
**BULGU-E — 🚨 sağlık kontrolü başkasının sunucusunu kendi sanıyor** (tuzak **7.8**): **8 kalem yanlış modele karşı üretildi, hiçbir yerde hata vermedi.** *Kök sebep: 6.3'ün konteyneri işi bittikten **2 saat sonra da** ayakta kalmıştı.* **Yakalayan şey `/v1/models` + `ps` doğrulamasıydı, sayısal bir kapı değil.** ⚠️ *Bu turda **bir yayımlanmış sayıyı da** vurabilirdi — `f02` çıpası aynı betikle üretilmişti ve o koşuda korunma **aletten değil TESADÜFTEN** geldi (8080 boştu).*
**BULGU-F — kusur 33: yeniden üretim kapısı HİÇBİR KOŞUDA geçmiyordu.** Sayaç her zaman **0** kaldı ve kapı *"harness OYNAMIŞ"* diye **her zaman** düşüyordu — **çıpanın kendi verisinde bile.** **KAPANDI.**
**BULGU-G/H — yayımlanan GGUF bit-eşit yeniden üretilemiyor (−32 bayt), ama S17 eğrisi bunu DAVRANIŞSAL olarak ELEDİ** (fark **0,7 çözünürlük adımı, BELİRSİZ**) ⇒ *32 baytlık fark davranışa yansımıyor, **yayımlanan sayı çözünürlük içinde yeniden üretilebiliyor**.* ⛔ Artefakt **değişmedi** — **eğri bir ifşadır, sürüm önerisi değil.**

### 2 · κ borcu ve kapı (6.4-6.7)

**BULGU-I — κ BORCU KAPANDI.** ADR-0074'ün tek cümlelik koşulu karşılandı; kapı **ikinci hakem altında da GEÇTİ** (marj **+9,57 p** eşiğe / **+7,57 p** çıpaya göre). **κ kendisi DEĞİŞMEDİ (0,534/0,409) — kapanan şey κ değil, EŞİT SINAVIN YOKLUĞUYDU.**
⭐ **Ön-kaydın en ince maddesi doğrulandı: göz düzeltmesinden MİRAS ALINAN KÜMEDİR, PUANLAR DEĞİL** — *dört miras kalemin üçü Anthropic altında 1,0'dan düştü; **puanlar da miras alınsaydı** çıpa `0,7425 → 0,6496`'ya şişer, marj `+5,86 → +6,44 p`'ye inerdi (**bu kez lehimize çıktı, ama kural koşudan ÖNCE yazılmıştı**).* → tuzak **2.20**.
Maliyet: gerçek **$1,6831** ↔ tabakalanmış tahmin $1,97 (**%14,6 fazla, GÜVENLİ yönde**) ↔ düz ön-tahmin $2,81 (%60 fazla).
**BULGU-J — kusur 23 KAPATILMADI, ve bu DOĞRU KARAR.** Deterministik taraf **üç bağımsız sınamada** temiz; **ama orijinal olayın kök nedeni hâlâ bulunamadı** ⇒ *kapatmaya **zorlanmadı**.* `id65` farkı bu turda **açıklandı ve kusur 23'ün sınıfı DEĞİL** (hakem katmanı `temp=0`'da bile bit-eşit değil) — *kesin kanıt değil, **makul çıkarım**.*
**BULGU-K — öz-tercih ilk kez ölçüldü, sonuç BEKLENENİN TERSİ.** `claude-sonnet-5` **kendi ailesini** bizden **~2 kat daha sert** cezalandırdı (Δ_sonnet **−20,03 p** ↔ Δ_biz **−10,71 p**) ⇒ **kayırma lehine kanıt YOK, ters yönde.** ⛔ Kapsam şerhi: **tek özne/tek hakem/tek koşu ⇒ GÖSTERGE, KANIT DEĞİL.**
**BULGU-L — Sonnet-5'in isabetsiz atfı gözle sayıldı: 7/80 (biz 8/80) — ön-kayıt ÇÜRÜDÜ, ve çürümesi bulgunun kendisi.** *Hakem-tabanlı vekil ölçüt Sonnet-5'i bizim **~9 kat** altımızda gösteriyordu; göz sayımı gerçek farkın **1 kalem** olduğunu buldu.* ⇒ ***Vekil ölçüt bu ekseni CİDDİ BİÇİMDE yanlış temsil ediyor.*** ⚠️ *Fark **kıl payı**: 5 sınır durum sayılmadı, ikisi sayılsa **yön değişebilir** — şerh yayında kalmalı.*
**BULGU-M — Sonnet-5'in M5'i ölçüldü; üstünlüğümüz KORUNDU.** BİZ **0,3899** (en iyi) · base 0,4697 · 3.1 FL 0,6710 · 3.5 FL 0,7013 · **Sonnet-5 0,7772** · 3.5 Flash 0,8241. Farkımız **38,73 p = 31 çözünürlük adımı — BELİRSİZ DEĞİL.** *Ön-kayıtlı kaybetme senaryosu **gerçekleşmedi**; sayı yalın yazıldı.*
**BULGU-N — 🎯 kapının üç maddesi yeni birimde okundu: GEÇTİ.** (1) kütle `gpt-4o-mini` **0,8011** ↔ çıpa 0,7425 ✅ **+5,86 p** · (1) kütle `claude-sonnet-5` **0,6940** ↔ 0,6183 ✅ **+7,57 p** · (2) isabetsizlik **8/80** ✅ · (3) M5 **0,3899** ↔ base 0,4697 ✅ **−7,98 p**.
*Marjlar çözünürlük bandının **kat kat** üstünde; ajan üç maddeyi de **kaynak dosyadan** okudu, şartnameden kopyalamadı.* ⛔ **Bu `v1.0` DEĞİLDİR.** ⚠️ Açık gerilim: **ADR-0032'nin üç aile kuralı hâlâ 2/3'te.**

### 3 · İki ön-kayıt ÇÜRÜDÜ — ve çürümeleri bulgunun kendisi

① vekil ölçüt yanıltıcı çıktı (BULGU-L) ② kaybetme senaryosu gerçekleşmedi (BULGU-M).
> ***İki ön-kaydın da çürümesi kayıp değil, BULGU: ikisi de sonuç görülmeden yazılmıştı ve aleyhe sonuca AÇIKTI — sonucun lehimize çıkması, ön-kaydın gereksiz olduğu anlamına gelmez.***

### 4 · Tuzak 1.11 bu turda DÖRT farklı biçimde ısırdı

| yüz | ne oldu | sapma |
| :--- | :--- | ---: |
| **doğrusal ekstrapolasyon** | `n=5`'ten `×16` | **%45 eksik** (önceki tur) |
| **düz ön-tahmin** | $2,81 ↔ gerçek $1,6831 | **%60 fazla** |
| **başka bir öznenin faturasından tahmin** | 6.6b bizim kolumuzun faturasından ($1,86); **Sonnet-5 665 iddia** üretti (bizimki ~273, **2,4×**) ↔ gerçek $2,6212 | **%41 fazla** — *hakem maliyeti tamamlama uzunluğuyla değil **İDDİA SAYISIYLA** ölçekleniyor* |
| **farklı bir moddan tabakalama** | h1 profilinden tabakalandı, M5-kör modda uzunluklar üç dilimde de **810-1050'ye sıkıştı** | proxy ayrışma **göstermedi** ⇒ **tabakalama anlamsızlaştı** |

> **Ortak ders:** *bir maliyet tahmini, **puanlanacak öznenin kendi profilinden** ve **aynı moddan** türetilmediği sürece — ekstrapolasyon, düz tahmin, başka özne, başka mod, **dördü de aynı hatanın yüzleri**.*

### 5 · Koordinatör hataları — bunlar da yazılır

**`git add -A` ile yarım dosya commit'i, İKİ KEZ.** İkincisinde `q8_0` detay dosyasının **43/80 satırlık yarım hâli** yakalandı; kalıcı zarar yok — *ama **aynı ders ikinci kez** verilmek zorunda kaldı.* ⇒ **Sert kural: alt ajan koşarken asla `git add -A`; dosyalar adıyla eklenir, `outputs/eval/**`'e koordinatör hiç dokunmaz.**
**Şartnameye yanlış sağlayıcı pini yazıldı:** *ajan çelişkiyi gördü, **emsali izledi**, varsayımını açıkça bildirdi — **doğru davranış**; ama yanlış pin kullanılsaydı beşinci kol diğer dördüyle **kıyaslanamaz** olurdu.*

### 6 · Tuzak 7.8'in korunması KODA yazıldı (TDD)

*Defterdeki "korunma" satırı koda **karşılıksız** kalmıştı ve tuzak bu turda **fiilen ısırdı**.* Önce **kırmızı test** (ağsız, sahte `curl`): tuzağın bire bir tekrarı **4/5 testte reprodüklendi**, sonra `dogrula_model_kimligi()` **her iki dala** bağlandı — `/v1/models` okunur, beklenen GGUF'un basename'iyle karşılaştırılır, **uyuşmazsa gürültülü `die()`**. Süit **326 → 331 yeşil**.

### 7-8 · Turun sayıları ve ders

test **331 yeşil, 2 xfail** · commit **53 + 3** · harcanan **≈$5,73 / tavan $8,00** · kapanan kusurlar **24·29·33** · açık **6** (5a · 10 · 23 · 25 · 27 · 31) · yeni tuzak **7.7·7.8·2.19·2.20** · **κ 0,534/0,409 — değişmedi** · **ağırlıklar değişmedi.**

> **Ders.** Bu turun 14 bulgusunun **hiçbiri eğitimden gelmedi** — üçü **ölçüm aygıtının kendi kusuruydu**, biri kalıcı bir tuzak sınıfının **dördüncü tekrarıydı**, ikisi ön-kaydın **aleyhe sonuca açık olduğunu kanıtlayan çürümelerdi**. *#67'nin dersi "kusurların çoğu bizim aynı gün yazdığımız koddandı" idi;* **#70'in dersi bir adım öteye gidiyor:** ***bir ölçüm aygıtının güvenilirliği, ikinci bağımsız bir hakemle sınandığında bile, hâlâ kendi İÇ TUTARLILIĞINDAN (id eşleşmesi, alan adları, sağlayıcı pinlemesi) AYRI BİR EKSENDİR*** — κ borcu kapandı ve kapı iki ailede de geçti, **ama bu turda bulunan üç aygıt kusurunun hiçbiri o κ ölçümüyle YAKALANAMAZDI**; hepsini yakalayan şey **göz okuması, birebir eşleşme iddiası ve *"bu sayı hiçbir koşuda geçmiyorsa şüphe eşiğe değil ALETE düşer"*** kuralıydı.

---

<a id="71"></a>
## #71 — Aşırı-red ekseni tek birime oturtuldu: yayımlanan bir sayı DEĞİŞTİ, aleyhimize

**2026-09-13 · Koşu yok, para harcanmadı** — mevcut çıktı dosyalarının yeniden okunması

**Ne arandı.** Kart yeniden yazılırken *aşırı çekinme* satırının **karışık birimde** olduğu görüldü: bizim hücremiz **gözle düzeltilmiş** sayı (4/80), rakip hücreleri **ham araç** sayısı (8·9·11) — **kusur 25'in birebir aynı sınıfı.** Satırı tek birime çekmeye çalışınca ikinci bir katman çıktı: **eksenin gözle düzeltilmiş sayıları depoda DÖRT AYRI YERDE DÖRT AYRI BİÇİMDE kayıtlıydı** (`4·5·5·7` ↔ `4·8·9·11·4` ↔ `5·7·9·9` ↔ `4·7·9·7·4`).

**Ne bulundu: birim çatışması gerçekti ve ADI AYNIYDI — *"temiz çekinme"*.** Kalibrasyonda = **altın gelmişken susulan** kalemler · Sonnet-5 dosyasında aynı ad = **TÜM** çekinmeler. Kapsam farkı ham alanlardan **birebir doğrulandı**:

| kol | altın geldi & sustu | altın yok & sustu | toplam | kalibrasyonun okuduğu |
| :--- | ---: | ---: | ---: | ---: |
| HakHukuk | 4 | 1 | 5 | **5** (tümü) |
| 3.1 Flash-Lite | 8 | 2 | 10 | **8** (yalnız altın-geldi) |
| 3.5 Flash-Lite | 9 | 1 | 10 | **9** (yalnız altın-geldi) |
| 3.5 Flash | 11 | 2 | 13 | **11** (yalnız altın-geldi) |
| Sonnet-5 | 7 | 1 | 8 | **8** (tümü) |

*Üç Gemini kolunda 8+9+11 = **28**, ve kalibrasyon dosyasının kendi cümlesi "28 rakip çekinme kalemi okundu" diyor ⇒ o üç kolun birimi **tanım gereği** altın-geldi.*

**Yayımlanan sayı değişti.** Sonnet-5 kalibrasyon dosyası kendi gerekçesinde şunu **zaten yazmış**: *"id 79'da altın zaten getirilmemişti ⇒ o kalemde çekinme **DOĞRU davranış**."* — **Bu cümle dosyada duruyordu ama SATIRA HİÇ YANSIMAMIŞTI.** ⇒ Sonnet-5'in aşırı-redi **4 değil 3**.

| kol | aşırı çekinme (altın geldi & sustu, gözle) |
| :--- | ---: |
| HakHukuk | 4/80 |
| `gemini-3.1-flash-lite` | 5/80 |
| `gemini-3.5-flash-lite` | 5/80 |
| `gemini-3.5-flash` | 7/80 |
| **`claude-sonnet-5`** | **3/80** |

⇒ **Sonnet-5 bu eksende bizden İYİ, eşit değil.** Kart *"aşırı çekinmede iki model eşittir"* diyordu; artık *"Sonnet-5 öndedir"* diyor. **Değişim aleyhimizedir ve olduğu gibi yazıldı.**

**Ders.** ***Bir kalibrasyon dosyasının gerekçe metninde duran şerh, satıra yansımadıysa YOK HÜKMÜNDEDİR.*** *Doğru sayı türetilebilir hâldeydi — gereken tek şey **dosyanın kendi cümlesini okumaktı**; dört ayrı belgeye dört ayrı sayı yazıldı ve **hiçbiri bunu yapmadı**.*
***Koşullu ölçütlerde KOŞUL METRİK ADINA yazılmalı.*** *"Temiz çekinme"* adı koşulu **taşımıyor**; *"altın geldi & sustu"* taşıyor. **Aynı ad iki farklı kapsamda kullanıldığında sayısal kapı uyarmaz — bu yine *"hata vermeden yanlış"* sınıfıdır.**

---

<a id="72"></a>
## #72 — F0 P1: eski geçmiş okundu; #62 çıpası puanlama için uygun değil, %68,4'ün kendisi formüle bağlı

**2026-10-11 · Koşu yok, para harcanmadı** — bundle klonu (`~/yedek/HakHukuk-2026-10-10.bundle`, 590 commit)
ve depodaki çıktı dosyalarının yeniden okunması. Plan: `docs/superpowers/plans/2026-10-11-F0-zemin.md`, P1.

**F0.3 — τ_g v1'in hassasiyeti, iki alıntı.**

| # | dosya:satır (eski geçmiş) | satır |
| :-- | :-- | :-- |
| 1 | `9f4b43d:docs/record/sprint1/NEXT-SESSION.md:62` | `--bf16-base --no-system --no-grad-checkpoint --batch 2 --grad-accum 8 \` (τ_g'nin hazırlanmış koşu komutu, 59-64) |
| 2 | `b995182:docs/open_questions.md:318` | `\| precision \| bf16 taban (ADR-0031) \| QLoRA NF4 sabit → --bf16-base \| ZORUNLU eşleşme …` |

İkinci satır `b995182`'de duruyor ama orada yazılmadı: `git blame` onu aynı gün iki saat önceki `64073b4`'e
bağlıyor; kod tarafı da orada (`64073b4:scripts/train_orpo.py:119` bayrak, `:132`
`load_in_4bit = not args.bf16_base`). `b995182` yalnız `--target-modules`'u zorunlu yaptı. Birinci satır
hazırlanmış bir komut; gerçek koşunun günlüğü eski geçmişte yok. Hüküm değişmedi: **belge kanıtı, künye
değil** (`kollar.md` dipnot ⁽²⁾). τ_a'nın koşu satırı kayıtlı (`--fresh-adapter --bf16-base`, #48).

**F0.5(b) — eski alet envanteri.**

| alet | eski hâli | değiştiği commit | hakem çağrılır mı |
| :-- | :-- | :-- | :-- |
| çekinme dedektörü | `aa0b85a^:scripts/score_abstention.py` | `aa0b85a`, 2026-09-06 (bir belge commit'ine süpürüldü; kaydı `463e8da`, #61) | hayır |
| hakeme giden kaynak kırpması (çekinme hakemi) | 3500 (2026-06-13'ten beri) | `ef440d6`, 2026-09-07 → 12000 | evet |
| A1 tanımı | ham makro (`A1_tum`) | `67ff585`, 2026-08-05 | hayır |
| kör payda | tuzak geçerliliği cevapla aynı çağrıda | `80b1f64`, 2026-08-06 (+ `5a40084`, `444b38b`, `91d6de0`) | evet |
| hakem | `gpt-4o-mini` | değişmedi (`0ed78f4`, 2026-06-08) | evet |
| `RRF_K` | 60 (`a7b293f`) | `9f86635`, 2026-09-06 → 10 | — |
| yeterlilik önsözü | metin `aa04c78` ile bugünkü `SUFFICIENCY_PREAMBLE` birebir aynı | varsayılan 2026-09-06'da kapandı; bayrak duruyor | — |

Belgelerde geçmeyen bir kırpma daha: doğruluk hakemine giden altın madde `groundedness.py:63`'te
`MAX_SOURCE_CHARS = 3500` ile kesiliyor; değer hiç değişmedi. DEV'de 80 altın maddenin 3'ü 3.500 karakteri
aşıyor (en uzunu 5.419). Etkisi ölçülmedi.

**Dedektör anahtarı bundle'daki eski fonksiyonla yeniden üretildi, birebir tuttu ($0):**

| koşu | eski dedektör | bugünkü | kayıttaki |
| :-- | --: | --: | :-- |
| `sprint2-olcum/olcum-bi` | 0,6275 (kapsama 0,7625) | 0,6838 (0,8250) | `harness_tablo.json.ONCEKI-20260906` ↔ `harness_tablo.json` |
| `sprint2-olcum/s2-harness-k10-etiketli` | 0,6132 (0,7625) | 0,7299 (0,9000) | aynı çift |

**#62 çıpasının kaynağı.** %68,4 = `outputs/eval/sprint2-olcum/olcum-bi/harness_tablo.json` `kutle_tum`
0,6838 (v1 sorular · `RRF_K` 60 · önsözlü · bütçe 1024 · `gpt-4o-mini`; künye yok). %80,1 =
`outputs/eval/faz0/f02-biz-onsozsuz/harness_tablo.json` `kutle_tum` 0,8011 (v2 sorular · `RRF_K` 10 ·
önsözsüz · bütçe 1536 · `gpt-4o-mini`; `KUNYE.json`). İki koşu aynı dedektör ve aynı hakemle puanlandı;
aradaki 11,7 puanın tamamı cevapları değiştiren dört şeyden geliyor (soru seti, `RRF_K`, önsöz, bütçe).
⇒ **Puanlama anahtarlarını sınamak için çıpa değildir.** F0.5(b) kutusuna anahtar başına çıpa yazıldı.

**Yan bulgu — %68,4 kullanılan formüle bağlı.** `olcum-bi`'de id 31 cevap sayılıyor (*"KAYNAK 1, toplu yapı
tanımını açıkça içermektedir. KAT MÜLKİYETİ KANUNU Madde 66"*) ama hakem sıfır iddia çıkarmış, puanı yok
(`n_claims 0`, `faithfulness None`). Depodaki iki kütle formülü bu kalemde ayrışıyor:

| formül | kalemle ne yapıyor | kütle |
| :-- | :-- | --: |
| `harness_tablo.py` (kapsama × A1) | A1 ortalamasından çıkarıyor (cevaplanan 66, puanlı 65) | 0,6838 |
| `uc_okuma_kutle.py` (toplam ÷ 80) | 0 puan veriyor | 0,6734 |

Fark −1,04 puan. `uc_okuma_kutle.py`'nin açıklaması iki formülün denk olduğunu söylüyor; bu yalnız sıfır
iddialı cevaplanmış kalem yokken doğru. `f02-biz-onsozsuz`'da böyle kalem yok (75/75 puanlı), %80,1
etkilenmiyor. Tuzak 2.22.

**Ders.** *Bir çıpanın "neyin sayısı" olduğu iki uçtaki koşunun künyesi yan yana okunmadan bilinmez:*
%68,4 → %80,1 bir "alet düzeltmesi" gibi anılıyordu, oysa aradaki her şey üretim tarafındaydı. Aynı okumada
çıpanın kendisi de iki formülden birine bağlı çıktı.

---

<a id="73"></a>
## #73 — F0.5 (a)(c): kütle tek yerden, payda kümeden; eski alet kayıttaki beş tabloyu birebir verdi

**2026-10-11 · Koşu yok, para harcanmadı** — kod + test (TDD) ve depodaki çıktı dosyalarının yeniden okunması.
Karar: [ADR-0099](../adr/kararlar-0064-0085.md#adr-0099) m.1-2.

**Ne yazıldı.**
- `scripts/puanlama/kutle.py` — kütle tek hesap. Payda dondurulmuş kümenin boyutu (`--kume`); (c) satır
  sayısı ≠ küme boyutu, yinelenen id, id'ler 0…n-1 değil ya da soru listesi kümeyle aynı değilse puanlama
  durur; (a) cevap sayılan bir kalemin hakem satırı yoksa ya da `durum: hakem_hata` ise durur. Sıfır
  iddialı cevaplanmış kalem 0 puan (eski alette A1'den çıkarılır).
- `scripts/puanlama/olcum_aleti.py` — RQ2 anahtarlarının adlı değerleri; her çıktıya `olcum_aleti` künyesi.
- `scripts/puanlama/part_dosya.py` — üretici `X.part`'a yazar, iş bitince yeniden adlandırır; okuyucu
  `.part`'ı reddeder. Bağlananlar: `gen_eval_grounded.py` · `groundedness.py` · `score_abstention.py`
  (üretici); `harness_tablo.py` · `uc_okuma_kutle.py` · `groundedness.py` · `score_abstention.py` (okuyucu).
- `groundedness.py` artık kalem düşürmüyor: her girdi kalemi `durum` ∈ puanli · sifir_iddia · hakem_hata ·
  bos_girdi ile bir satır alır, özete `n_*` sayaçları; bütçe biterse dosya `.part` kalır ve betik durur;
  birden çok hakem koşusundan biri düşerse kalem `hakem_hata` olur (eskiden eksik koşuyla havuzlanıyordu);
  iddia çıkarılıp doğrulama boş etiket dönerse hakem hatasıdır, sıfır iddia değil.
- `harness_tablo.py` ve `uc_okuma_kutle.py` kütleyi `kutle.py`'den alır; ikisi de `--kume` ister
  (`yeniden_uret.sh`'a eklendi; `N_OVERRIDE=10` duman koşusu 4/5'te bilerek durur).

**Eski alet kayıttaki tabloları birebir verdi.** Eski sıfır-iddia kuralıyla, depodaki beş
`harness_tablo.json` (`sprint2-olcum/` altında `olcum-bi` · `s2-harness-k10-etiketli` · `s2-harness-k10` ·
`s3-harness-acik` · `s3-harness-k10`; v1 soru kümesi, `--etiketler s3-ayirt-edicilik/etiketler.jsonl`)
yeniden üretildi; `kaynak` dışındaki **bütün alanlar** aynı. İlk denemede iki tabloda dördüncü hanede ±0,0001
fark çıktı: eski tablo kapsama ve A1'i önce dört haneye yuvarlayıp çarpıyordu (`s3-harness-k10` 0,6914, tek
yuvarlamayla 0,6913). Çift yuvarlama eski alette korundu; yeni kuralda kütle = Σ/n tek yuvarlamayla.
`f02-biz-onsozsuz` (%80,1) iki kuralda da 0,8011; `uc_okuma_kutle`'nin kalibrasyonu (0,6925 · 0,7050 · 0,7425)
değişmedi.

**F0.5 (a) — geçmiş koşularda bu yoldan düşen kalemler.** `outputs/eval/**` altında detay ve hakem dosyası
eşleşen 49 koşu okundu (çekinme dedektörü kipiyle: kör modda `blind`). **Eksik hakem satırı: 0.** Cevap
sayılıp sıfır iddialı kalem: **7 koşuda 10**:

| koşu | n | cevaplanan | sıfır iddialı id | kütle eski kural → 0 puan |
| :-- | --: | --: | :-- | :-- |
| `cp/cp09-butceli-1024-512` `m4_base_th` | 80 | 80 | 18 | 0,9715 → 0,9594 (−1,21 p) |
| `cp/cp3-supurme-min` `m1_tg_ta_min_th` | 80 | 43 | 19 | 0,5343 → 0,5219 (−1,24 p) |
| `cp/cp3c-ta-v1` `m1_ta_v1_th` | 80 | 34 | 35 | 0,4121 → 0,4000 (−1,21 p) |
| `cp/cp3e-merge` `m1_tg_ta_nb_th` | 80 | 2 | 19 | 0,0250 → 0,0125 (−1,25 p) |
| `faz0/f10-rakip-m5` Sonnet-5 M5 | 80 | 80 | 4 | 0,7772 → 0,7675 (−0,97 p) |
| `sprint1/sprint1-thinking-off` `m5_tg` | 80 | 80 | 4 · 5 · 76 · 77 | 0,4421 → 0,4200 (−2,21 p) |
| `sprint2-olcum/olcum-bi` `h1_tgta_v1_bi_k10` | 80 | 66 | 31 | 0,6838 → 0,6734 (−1,04 p) |

Bu tablo kütle tanımını eski koşulara uygular; o koşuların çoğu kayıtta kütle değil A1 olarak raporlandı
(A1 eski kuralla zaten bu kalemleri dışarıda bırakıyordu). Kayıttaki sayılar değiştirilmedi.

**Test.** 38 yeni test (`test_kutle.py` · `test_part_dosya.py` · `test_groundedness.py` ·
`test_harness_tablo_kutle.py`, `test_uc_okuma_kutle.py`'ye bir tane); hızlı takım 373 → 412 yeşil.

**Bağlanmayan yollar** (kütleyi kendi hesaplıyor, bu turda `kutle.py`'ye bağlanmadı, Tablo 1'i üretmiyor):
`rescore_answered.py` (payda gnd ∩ bench) ve onun `a1_*.txt` çıktısını okuyan `cp09_tablo.py` ·
`cp0_thinking_score.sh` · `compare_runs.py` · `cp1_delta.py` · `cp2r_esikler.py`; `bench_scorecard.py`;
`score_correctness.py`. `konteyner_urun_yolu_80.py` kendi devam düzeneğiyle yazar, `.part`'a bağlanmadı.

**Ders.** *Aynı adı taşıyan iki formülün denkliği açıklamada yazılıydı ama sınanmamıştı* (tuzak 2.22). Eski
aleti "birebir" üretmek, onun yuvarlama alışkanlığını da üretmeyi gerektirdi.

---

<a id="74"></a>
## #74 — F0.4: eğitim ortamı kilidi kodda; `fla` sürümü Modal'ın önbellekli katmanından okundu

**2026-10-11 · Modal ~$0,01 (GPU'suz okuma)** · Karar: [ADR-0099](../adr/kararlar-0064-0085.md#adr-0099) m.3-4.

**Sürüm okuması.** `modal_train.py`'nin imaj tanımı (`add_local_dir` hariç) birebir kopyalanıp ilk Modal
hesabında (eğitimin yapıldığı hesap, `hukuk-*` birimleri 2026-06-08'den beri) GPU'suz bir işlevle koşuldu;
imaj **yeniden kurulmadı**, önbellekten geldi. Okunan: `einops` 0.8.2 · `fla-core` 0.5.1 ·
`flash-linear-attention` 0.5.1 (üçünün kurulum zamanı **2026-07-25 06:03 UTC**) · torch 2.10.0 (kurulum
2026-06-08) · triton 3.6.0 · transformers 5.10.2 · peft 0.19.1 · trl 0.24.0 · unsloth / unsloth_zoo 2026.6.1 ·
accelerate 1.13.0 · bitsandbytes 0.49.2 · datasets 4.3.0 — hepsi `requirements.lock.txt` ile aynı. İmaj
tanımı `fla`'nın eklendiği `89277a6`'dan (2026-07-25) bugüne metin olarak aynı; τ_g (2026-07-28) ve τ_a
(2026-08-03) bu katmanla eğitildi. PyPI: `fla-core` 0.5.2 2026-07-27'de çıktı — imaj o gün yeniden kurulsaydı
τ_g başka sürümle eğitilirdi, hata vermezdi.

**Ne yazıldı.**
- `configs/egitim_ortami.yaml` — kilidin makine okunur tek kaynağı (model, tur işaretleri, GPU, Python,
  paketler + ek paketler + yasak paket, hassasiyet, LoRA, SFT ve ORPO tarifleri, seed listesi).
- `scripts/egitim/ortam_kilidi.py` — `kilidi_uygula`: model yüklenmeden önce koşunun argümanları, verinin
  satır sayısı, GPU (ad öneki `NVIDIA A100`, hesaplama sürümü 8.0), paket sürümleri (yerel ek soyularak),
  yasak paket ve `from fla.modules import FusedRMSNormGated` kilitle karşılaştırılır; uymayan her alan
  listelenir, koşu durur. Geçerse çıktı dizinine `KUNYE.json` (EGITIM_ORTAMI §5), bitince gerçekleşen adım.
- `train_sft.py` / `train_orpo.py` — `--hassasiyet {bf16-taban,nf4}` ve `--ortam-kilidi` zorunlu,
  varsayılansız; `--bf16-base` kaldırıldı; kayıp geçmişi (`trainer_state.json`) çıktı dizinine; ORPO'ya
  `--durdur-adim N` (takvim tam koşuya göre kurulur, eğitim N. adımda kesilir).
- `modal_train.py` — GPU varsayılanı kilitten `A100-40GB` (önceden `"A100"`, tuzak 6.7); ek paketler
  kilitteki sürümle; `configs/` ve `hakhukuk/` imaja giriyor (önceden yalnız `scripts/`; `train_sft.py`
  `hakhukuk.cekirdek.istem`'i içe aktarıyor); `seed` · `max_steps` · `durdur_adim` Modal'dan geçirilebilir
  (önceden seed hiç geçirilemiyordu, ORPO'da 10 adım istenemiyordu).
- `tests/test_egitim_ortami.py` — yaml ↔ EGITIM_ORTAMI §2 ↔ `requirements.lock.txt`; kuralların sahte
  gözlemlerle kırmızısı (yanlış GPU, yanlış sürüm, fla yok, yasak paket, `lr` farkı, hassasiyet, seed, veri
  satırı …); kontrolün iki betikte model yüklemesinden önce çağrıldığı (kod ağacından); Modal zinciri.

**Kontrolün yakalayacağı kayıtlı bir sessiz düşme:** `spawn_sft`'te `lr` varsayılanı 0.0 ve `if lr:` ile
iletiliyor; `--lr` unutulursa betiğin varsayılanı 2e-4 koşardı (tarif 1e-4). Artık kilit kontrolü
`lr: koşu 0.0002 ≠ kilit 0.0001` diye model yüklenmeden durdurur.

**Açık:** eşdeğerlik ve gürültü tabanı koşuları (F0.4 kutusu; ORPO toleransı %2,5 göreli, 2026-10-11).
