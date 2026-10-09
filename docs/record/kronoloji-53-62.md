# Araştırma kaydı — #53 … #62

> **Ne bu:** harness turu, ölçüm aletinin onarımları ve Faz 0 ölçüm zinciri — **birleştirilmiş
> ve damıtılmış**. Tekil dosyalar 2026-09-13'te silindi
> ([ADR-0086](../adr/kararlar-0064-0085.md#adr-0086)); **sayılar birebir korundu.**
> Çapa: `kronoloji-53-62.md#57`.

| # | tarih | başlık | kanca |
| :-- | :--- | :--- | :--- |
| [53](#53) | 2026-08-05 | S3: ayırt-edicilik etiketi (borç B2) · ADR-0054/K4'ün **kör** turu | `recall@5` iki alt küme arasında **32,3 puan** ayrışıyor · ⭐⭐ **çekinme TERS yönde çalışıyor** |
| [54](#54) | 2026-08-05 | S1: `k` süpürmesi (k=10) · 🚨 **yayınlanmış kütle YANLIŞ metrikle üretilmiş** | ön-kayıtlı kapının hükmü **aletin düzeltilmesiyle tersine döndü** |
| [55](#55) | 2026-08-05 | S2: yürürlük alanı + madde kimliği (borç B7) | kapsam **menüden değil ölçümden** · AÇIK↔KAPALI açığının ayrıştırması |
| [56](#56) | 2026-08-05 | Ölçüm boşlukları: m2b harness AÇIK · B5 · B8 · B-i | **kapı KALDI** · *"red kapısı M2b'yi kapatır"* **yapısal olarak ateşlenemez** |
| [57](#57) | 2026-08-06 | ⭐ Çekinme aletinin onarımı (**ᴷ³**) — payda cevaba **kör** yapıldı | 10 koşu yeniden puanlandı · ADR-0052'nin hükmü **ayakta**, sayıları değişti |
| [58](#58) | 2026-08-06 | Payda tekilleşmesi (**ᴷ⁴**) — **ARA KAPI'nın 2. gözlemi DÜŞTÜ** | merge M2b **0,766 ↔ eşik 0,8649** → −9,9 p ⇒ **CP4-CP5 yetkisi yok** |
| [59](#59) | 2026-08-06 | `m2` paydası ve KARAR-4 | payda **66/70**'e eşitlendi, her kolda **eşit** — kendi kendini doğrulayan sınav |
| [60](#60) | 2026-09-06 | 🚨 Hasat kabul ölçütü ÇÖKTÜ — gözle okuma çürüttü | 10 kabul kaleminin **6'sı** tam ve doğru atıflı **cevaptı** |
| [61](#61) | 2026-09-06 | Dedektör onarımı · B10 yeniden ölçüldü | **aşırı-red 14/80 → 8/80, hiç eğitim yapılmadan** — %43'ü **aletin kendisiydi** |
| [62](#62) | 2026-09-06 | Faz 0 ölçüm zinciri | beş alet kusuru · kütle **%68,4 → %80,1**, **ağırlıklar hiç değişmeden** |

---

<a id="53"></a>
## #53 — S3: ayırt-edicilik etiketi (borç B2) · ADR-0054/K4'ün kör turu

**2026-08-05 · hakem $0,0069**
> ⛔ **BU BÖLÜM ETİKETLEME KOŞULMADAN ÖNCE YAZILDI** — ADR-0054/K4'ün açık şartı. İstem koşudan sonra **değiştirilmedi**.

**Neden bu tur var.** `recall@5 = 0,750` **retriever'ın değil bu kümenin** tavanı olabilir. **Küme değiştirilmiyor** (*sayı görüldükten sonra küme değiştirmek "cilaladılar" diye okunur*); yerine **etiket** ekleniyor ve sayılar **iki alt kümede ayrı** raporlanıyor.
**Ön-kayıtlı ölçüt:** *"Soru tek başına okunduğunda hangi kanun/konu alanına ait olduğu anlaşılıyor mu? (Bir hukukçu 1-2 kanuna daraltabiliyorsa **EVET**.)"*
**🚨 Körlük — nasıl sağlandı.** Hakeme giden yük **tek argümanlı** bir fonksiyondan üretiliyor (`_istem(soru)`); altın madde, `kanun_adi/no`, `madde_no` ve retriever sonucu bu yükte **hiç bulunmuyor** ⇒ ***körlük bir söz değil, çağrı imzasının kısıtı.*** *Bu, tuzak **2.14**'ün tersi yönde uygulanması: orada etiket öznenin cevabıyla **aynı çağrıda** istendiği için kalemin değil **öznenin** özelliği olmuştu.*
**⚠️ İki çekince kaydedildi.** ① **Ölçülen büyüklük ön-kayıtlı değil** — bu ekseni ölçme fikri kaçan soruları **görerek** doğdu; *ayrım korunuyor: **alet** sonuca göre ayarlanmadı.* ② **Sıra sapması** — ADR-0054 bu turun harness-AÇIK'tan **önce** koşulmasını yazmıştı, fiilen **sonra** koşuldu; *körlük etkilenmiyor ama sapma gizlenmiyor.*

**Sonuç: 62 ayırt edici · 18 belirsiz (%22,5)** — S3a'nın gözle yaptığı *"~%25"* tahmini **tuttu**.

| eksen | **ayırt edici** (n=62) | **belirsiz** (n=18) | tüm küme |
| :--- | ---: | ---: | ---: |
| `recall@1` | 0,5323 | 0,1667 | 0,4500 |
| **`recall@5`** | **0,8226** | **0,5000** | **0,7500** |
| coverage | 0,6935 | **0,9444** | 0,7500 |
| A1 (cevaplanan-only) | **0,8651** | **0,4909** | **0,7591** |
| A1 · altın getirilen | **0,9336** | 0,8796 | **0,9230** |
| **kütle** | **%60,0** | **%46,4** | **%56,9** |

*(⚠️ Sayılar aynı gün **düzeltilmiş** aletten — `harness_tablo.py`'nin A1'i ham makro hesapladığı henüz bilinmiyordu, [#54](#54) tuzak **2.16**. Düzeltme okumaları **değiştirmedi**.)*

**Okuma 1 — tuzak 7.4 sayıyla doğrulandı.** `recall@5` iki alt küme arasında **32,3 puan** ayrışıyor ⇒ ***"0,750" retriever kabiliyetinin değil, kümenin kompozisyonunun sayısı.*** **Bundan sonra hiçbir harness sayısı bu ayrım yapılmadan raporlanmaz.**
**Okuma 2 — ⭐⭐ BEKLENMEDİK: çekinme TERS yönde çalışıyor.** Ayırt edici (n=62): erişim **0,8226**, çekinme **%30,6** ↔ belirsiz (n=18): erişim **0,5000**, çekinme **%5,6**. ⇒ ***Model, erişimin en çok başarısız olduğu sorularda en az çekiniyor.*** **Güvenli bir sistemde bunun tersi olmalıydı.**
İki uç birlikte: **belirsiz tarafta yetersiz-red** (18 sorunun 17'si cevaplanıyor, 9'unda altın **yok**; **B1'in 14 vakasının 8'i** burada ⇒ **B1 kümenin yalnız %22,5'inde yoğunlaşmış**) · **ayırt edici tarafta aşırı-red** (14 soruda altın **bağlamda olmasına rağmen** çekinilmiş).
**Mekanizma tahmini (sınanmadı):** *belirsiz bir soru konusal olarak makul görünen bir madde getirir ve model onu cevaplar; ayırt edici bir soruda retriever ıskaladığında getirilen bağlam **açıkça alakasızdır** ve model çekinir.* ⇒ ***çekinme sinyali bağlamın KONUSAL UYUMUNDAN geliyor, soruyu cevaplamaya YETERLİ olup olmadığından değil*** → doğrudan **S4'ün (isabet denetimi) tasarım girdisi.**
**⭐ Okuma 2-b (aynı gün): `k=10` bu tersliği büyük ölçüde DÜZELTİYOR.** coverage ayırt edici 0,6935 → **0,7903** · belirsiz **0,9444 → 0,7222**; sıralama ❌ ters → ✅ doğru. *Belirsiz alt kümede çekinme **1/18 → 5/18**: model, **on parça** bağlamda hiçbiri soruyu karşılamayınca fark edebiliyor — **beş parçada fark edemiyordu**.* **Terslik tamamen kapanmadı, yön düzeldi.**
**Okuma 3.** Altın getirildiğinde model **her iki kümede de sadık** (0,9336 ↔ 0,8796) ⇒ #51'in *"darboğaz model değil erişim"* okuması alt küme kırılımında da **ayakta**.

---

<a id="54"></a>
## #54 — S1: `k` süpürmesi (k=10) · 🚨 ve yayınlanmış kütle sayısı YANLIŞ metrikle üretilmiş

**2026-08-05 · GPU $0 · hakem $0,0403**
> İki bulgu var ve **ikincisi birinciden büyük.** (1) k=10 kütleyi yükseltiyor. (2) Bunu ölçerken `harness_tablo.py`'nin **A1'i yanlış hesapladığı** görüldü — ve o hatalı sayı `MODEL_CARD.md` dâhil **sekiz belgeye** yayılmış durumda.

### 🚨 Bölüm 1 — metrik hatası: A1 yerine ham makro (tuzak 2.3'ün birebir tekrarı)

`A1_tum` diye raporlanan sayı **puanlanan tüm kalemlerin** makrosuydu; oysa **A1 = cevaplanan-only.** *Fark, çekinmelerin de hakemden puan almasından geliyor: **model çekinirken de cümle kuruyor**, hakem o cümlelere iddia diyor ve puanlıyor.*
```
k=5 : puanlanan 71 → TÜMÜ 0,7823 · cevaplanan(A1) 0,7591 · ÇEKİNENLER 0,9091 (n=11)
k=10: puanlanan 74 → TÜMÜ 0,7541 · cevaplanan(A1) 0,7681 · ÇEKİNENLER 0,6819 (n=12)
```
**⚠️ Sapma YÖN DEĞİŞTİRİYOR — bu, gürültünün en kötü türü.** k=5'te çekinmeler makroyu **yukarı**, k=10'da **aşağı** çekti ⇒ *hata sabit bir kayma değil; iki koşuyu **birbirine göre** bozuyor.*

| | bozuk aletle | düzeltilmiş aletle |
| :--- | ---: | ---: |
| k=5 kütle | %58,7 | **%56,9** |
| k=10 kütle | %58,4 | **%59,5** |
| **hüküm** | k=10 **DÜŞÜK** → 🔴 RET | k=10 **YÜKSEK** → ✅ KABUL |

***Ön-kayıtlı kapının hükmü, aletin düzeltilmesiyle tersine döndü.*** ADR-0050'nin kuralı aynen uygulandı: **sonucu gördükten sonra EŞİK değil ALET düzeltilir**; düzeltme **iki kola da simetrik** uygulandı ve eşik aynı koşudan **yeniden türetildi** (%58,7 → %56,9) — *eşik gevşetilmedi, **yeniden ölçüldü**.*
**⚠️ Daha kötüsü: ON/OFF kıyası elmayla armuttu.** Harness KAPALI çıpası **doğru** metrikle üretilmişti (0,9087 / %71,6) ⇒ ***`%71,6 ↔ %58,7` karşılaştırmasının bir tarafı cevaplanan-only, diğer tarafı ham makroydu.***
**Düzeltilen belgeler:** 8 belge; **eski sayı silinmedi**, üstü çizilip yanına doğrusu yazıldı. → tuzak **2.16**.

### Bölüm 2 — S1'in asıl sonucu: k=10 kabul edildi, ama tahmin ıskaladı

| büyüklük | tahmin (k=10) | **ölçüldü** | hüküm |
| :--- | ---: | ---: | :--- |
| altın getirilen | ~70/80 | **70/80** | ✅ **birebir tuttu** |
| coverage | ~0,76 | **0,775** | ✅ tuttu |
| A1 | ~0,86 | **0,7681** | ❌ **9 puan ıskaladı** |
| **kütle** | ~%65 | **%59,5** | ❌ **5,5 puan ıskaladı** |

***Erişim tahmini kusursuz, davranış tahmini yanlıştı.***
**⭐ k'nın bedeli ölçüldü: dikkat dağılması gerçek.** `altın getirilende A1 0,9230 → 0,8426` (**−8,0 puan**) ↔ `coverage +2,5` · `KÜTLE %56,9 → %59,5` (**+2,6 net kazanç**). *Aynı soruda altın madde bağlamda dururken, yanına 5 madde daha konunca sadakat **8 puan** düşüyor; net kazanç, erişimin kazandırdığı 10 sorunun bu kaybı **aşmasından** geliyor.*
**⭐ Bu ölçüm, graph-RAG'in ön-kayıtlı tahminini SINADI.** 2026-08-04'te graf için yazılan tahmin: *"A1 değişmez, hafif düşebilir — graf daha çok komşu getirir → bağlam uzar → **dikkat dağılır**"*. **Dün bu bir varsayımdı; bugün tam olarak o mekanizma ölçüldü** — ve **graf bağlamı k=10'dan çok daha fazla uzatır** ⇒ bulgu graf'ın **aleyhine**. *Aynı tahminin "altın gelmedi ama cevapladı **hiç değişmez**" satırı ise **fazla karamsar** çıktı (14 → 7/80).* ***Tahminin tutanı da ıskalayanı da kayda geçiyor — ön-kayıtlı tahminin değeri sonradan haklı çıkmasında değil, **sınanabilir olmasında**.***

**Erişim ↔ davranış çaprazı:** `altın geldi→cevapladı 46→55` · `altın geldi→çekindi 14→15` ← **aşırı-red DEĞİŞMEDİ** · `altın GELMEDİ→cevapladı 14→7` ← **B1'in sınıfı YARIYA indi** · `altın GELMEDİ→çekindi 6→3`. ⇒ **Coverage kaybının bu yarısı erişimle çözülmüyor — model tarafında.**
**Ayırt-edicilik kırılımı:** k'nın kazancı **ayırt edici** tarafta toplanıyor (+2,1 p kütle), belirsizde neredeyse **yok** (+0,5) ⇒ ***k büyütmek, belirsiz soru sorununu çözmüyor.***
**⭐⭐ Ama k=10 çekinme kalibrasyonunun YÖNÜNÜ düzeltiyor** (bkz. #53 Okuma 2-b) — *k=10'un kütle dışındaki en değerli kazancı ve **ürün güvenliği** ekseninde doğrudan bir iyileşme.*
**Geçerlilik kapıları:** kesik %2,5 ✅ · **örneklem birebir aynı 80 soru** (soru/kanun_no/madde_no üçlüsü tek tek eşleşti) · CTX sığıyor (5.118 < 8.192) · hakem birebir.
**⭐ Yan gözlem:** bağlam iki katına çıkarken **zorla kapatma 15/80 → 4/80'e düştü** ve ort token 731'e indi ⇒ ***daha çok bağlam, modeli daha az düşündürüyor*** — #42'nin *"belirsizlik döngü üretiyor"* mekanizmasıyla **tutarlı**.

### Bölüm 3 — atıf doğrulayıcısı ilk kez bir şey yakaladı: ve o bir YAZIM HATASI

`DOGRULANDI 118 · KANUN_YOK 2 · MADDE_YOK 0`. İki `KANUN_YOK` **gözle okundu**:
```
model yazdı: "Fikir ve Sanat ESELERİ Kanunu Madde 57 / 58"   ← bir harf düştü ('r')
hüküm: KANUN_YOK → katı kapı REDDETTİ    (madde no'lar DOĞRU, kanun bağlamda VAR)
```
**Uydurma değil, kopyalama hatası.** ⇒ ① #51'in *"uydurulmuş madde numarası 0"* bulgusu **k=10'da da AYAKTA** ② **yeni bir yanlış-negatif sınıfı: tek karakterlik transkripsiyon hatası** — ADR-0038'in kalibrasyonu resmî adın **kısa hâlini** çözmüştü, **yazım hatasını çözmüyor**; *katı kapıda bunun bedeli **tüm cevabın reddi**.* ③ ayrıştırıcı adın **başını da düşürüyor** — #51'de bulunan hatanın **ters yönü**.
⚠️ **Karar verilmedi, borç olarak açılıyor (B8):** *tolerans katı kapıyı **gevşetir**; gevşetme kararı ölçülmeden verilmez.*

**Hüküm.** ✅ **S1 KABUL: `k=10` yürürlükte** (%56,9 → **%59,5**). ⚠️ Kazanç tahminin (~%65) **altında**; `k=20` için gerekçe **zayıf** — *`recall@20` yalnız +5 puan getirirken bağlam iki katına daha çıkar ve bu bedel **ölçülmüş biçimde** büyür.*

---

<a id="55"></a>
## #55 — S2: yürürlük alanı + madde kimliği (borç B7) · kapsam menüden değil ölçümden

**2026-08-05** · İndeks `data/index/mevzuat_bge_m3_s2` (**yeni dizin; eskisi korundu**)

**1. Kapsam kararı — yanlış soruyu sormaktan dönüldü.** Yanlış soru: *"korpus ne kadar bozuk?"* **Doğru soru: "modelin GÖRDÜĞÜ bağlamda çöp var mı?"** — *çünkü korpusta duran ama hiç getirilmeyen bir satırın ürüne maliyeti yoktur.* Ölçüm **modele giden metnin kendisi** (`context_shown`) üzerinde yapıldı:

| bozulma sınıfı | korpusta | **modele ulaşan blok** | altın etiketi | karar |
| :--- | ---: | :--- | ---: | :--- |
| **A — tablo/cetvel parçası** | ~7.966 satır | **0 / 800** | — | **ertelendi (B9)** |
| **B — alt-madde soneki** | **485 satır** | **14 / 800 · 12 soru** | 3/80 | ✅ **yapıldı** |

*Elemek **ölçülemez bir kazanç için ölçülmüş bir sayıyı harcamak** olurdu.*
**⚠️ Yinelenme ≠ kirlenme.** Anahtar üzerinden *"26/80 soru bozuk parça görüyor"* çıkıyordu; `context_shown` üzerinden **6/80**. *Fark: **anahtar yinelenmiş olsa bile retriever o anahtarın doğru satırını getiriyordu.*** ⇒ ***Sayının hangi nesne üzerinde ölçüldüğü, sayının kendisinden önemli*** — aynı korpus için **%29,4 ile %1,8** arasında gezinen **iki doğru sayı** var.

**2. Yapılan iş.** `korpus_yururluk.py` — **atomik yazma** (geçici dosya → doğrula → `os.replace`); *doğrulama düşerse korpus **değişmez***. `mulga` + ilga alanları **2.547 satır** (ilga kaynağı çıkarılan **%99,6**) · alt-madde soneki `madde_no`'ya taşındı **485 satır**. `atif_dogrula.py`'ye **`MULGA`** hükmü; **`all(mulga)`** kullanıldı — *bir anahtar birden çok satıra düşebiliyor, yürürlükte **tek** satır varsa atıf mülga sayılmaz (geçerli atıfları yanlış reddetmemek için).* `red_kapisi.py`'ye **dokunulmadı**.

**3. 🐞 İki kural doğrulama hedefine çarpıp düzeldi** — ikisi de **hata vermeden yanlış veri üretecekti**.
**(a) Sonek kuralı %80 eksikti** — yalnız küçük harf aranıyordu; korpusta en sık sonek **büyük `/A`** (249 satır). *98 satırlık sanılan sınıf gerçekte **485**; kaçan 387 satır, **düzeltme yapılmış gibi görünen** bir korpus bırakacaktı.*
**(b) İlga kaynağı tarihin son parçasını kanun sanıyordu** — ayraç yalnız **tire** sanılmıştı, oysa **bölü** de olabiliyor ⇒ `4857 md.120` yerine **`2003 md.4857`**.
⭐ ***Sprint'in kendi verify kalemi ele verdi.*** `1475/15`'i hedef olarak yazmak **bir tören değildi**; iki kuralı da o hedef düşürdü.

**4. ⚠️ Dürüst negatif sonuç — B7 bir skor özelliği değil.** k=5 ve k=10 yeni korpusa karşı yeniden puanlandı: `MULGA` **0** · hükmü değişen cevap **0/80**. ⇒ *Açık **mekanik olarak** kapandı ama bu DEV kümesinde **ölçülen görülme sıklığı sıfır**.* **B7 bir ürün-güvenliği özelliğidir, bir metrik iyileştirmesi değil.** *Bunun kaydedilmesi şart: aksi hâlde ileride "S2 hiçbir şeye yaramadı" diye okunur, oysa ölçülen şey "bu kümede tetiklenmedi"dir.*

**5-8. 🚨 Kendi hatamın düzeltmesi — *"eval etiketleri düzeltilmedi, gerek kalmadı"* YANLIŞTI.** Dayanak doğru ama **yetersizdi**: anahtar yaşıyor, ama **iki satırdan yanlış olanı** gösteriyor. `referans` alanına bakarak **3** kalem bulunmuştu; doğru kural (*"altın anahtarın sonekli bir kardeşi var mı"*) **5** buluyor.
**Kanıtlı vaka — id=76:** altın `Madde 97` (**bayat etiket**, başka konu), cevabı `Madde 97/a`; retriever `97/a`'yı **1. sıraya** koydu, model **doğru cevapladı**, puanlama **hem "erişim ıskası" hem "sadakatsiz"** saydı. ⇒ `recall@10`'un 0,8750 → **0,8625** düşüşünün **tamamı bu tek kalem** ve sebebi retriever değil **etiket**.
**⛔ ÖN-KAYITLI DENETİM İSTEMİ — koşulmadan önce yazıldı.** ⚠️ *Bu denetim sayı görüldükten sonra yapılıyor ve düzeltmesi **bizim lehimize**; "cilaladılar" riski tam burada.* Karar **insana soruldu** ve usul sıkılaştırıldı: şüpheli kalemler **elle seçilmez, kuralla bulunur** · hakem **kördür** (madde no, kanun adı, mevcut altın etiket yüke **girmez**) · **konum yanlılığına karşı** altın tek id'de A'ya çift id'de B'ye konur · hakem **"belirsiz"** diyebilir ve belirsizde etiket **DEĞİŞMEZ**.
**Sonuç:** `DÜZELT` id 0 · 74 · 76 · `DEĞİŞMEZ` id 41 · 45.
**🚩 İlk koşuda hakem BEŞİNDE DE "A" dedi** — konum rastgeleleştirilmiş olmasına rağmen tek yönlü seçim **klasik konum yanlılığı işaretidir**; *bu hükümlere dayanıp eval kümesini değiştirmek olmazdı.* Kontrol koşuldu (`--konum-ters`, koda **kalıcı** girdi): hakem bu kez **beşinde de "B"** dedi ve **hükümler birebir aynı** kaldı ⇒ **hakem konumu değil içeriği izliyor.**
**🐞 Denetim ayrıca kendi kodumda bir hata buldu:** id 0 ile id 41 **aynı altın anahtarı** paylaşıyor ama farklı maddelerden üretilmişler; `--uygula` anahtara göre eşliyordu, **ikisini birden bozacaktı** → eşleme **soru metnine** çevrildi + uyuşmazlıkta betik **eval'e dokunmadan ölüyor**.

**9. ⭐ SONUÇ — S2 sonrası, düzeltilmiş etiketlerle** (kesik %2,5 ✅ · hakem $0,0398):

| eksen | S2 öncesi (k=10) | S2 sonrası | Δ |
| :--- | ---: | ---: | ---: |
| `recall@10` | 0,8750 | **0,8750** | 0 |
| coverage | 0,7750 | **0,7625** | −1 soru |
| **A1** | 0,7681 | **0,8042** | **+3,6 p** |
| A1 · altın getirilen | 0,8426 | **0,8616** | +1,9 p |
| **kütle** | **%59,5** | **%61,3** | **+1,8 p** |
| bozuk blok | 14/800 | **0/800** | −14 |
| B1 sınıfı | 7 | **7** | 0 |
| aşırı-red | 15 | **16** | +1 |

**Ön-kayıtlı tahminin denetimi:** `recall@10` ✅ · `MULGA` ✅ · bozuk blok ✅ · **kütle ❌ TUTMADI** (bandın 0,8 p üstü).
⚠️ **Kütle tahmini neden tutmadı, ve GEREKÇESİ neden yanlıştı.** *"A1'i etkileyecek bir şey değişmedi"* demiştim — **yanlış**: gömülen metin değişince **getirilen bağlam da değişti**. ⇒ **Onarım A1'i atıf kanalından değil ERİŞİM KALİTESİ kanalından iyileştirdi.** §4'ün *"skor özelliği değil"* hükmü **atıf hükümleri için ayakta**, **erişim için ayakta değil.** *İki kanal, iki ayrı sonuç.*
**🚨 Etiket düzeltmesi manşet sayıyı YÜKSELTMEDİ.** Kullanıcıya *"kütle biraz daha artar"* demiştim — **yanlıştı ve mekanizması yanlıştı**: altın etiket **A1'e de coverage'a da girmiyor** ⇒ **kütleye etkisi tanımı gereği sıfır**. Etkisi yalnız **erişim metrikleri** ve **teşhis çapraz tablosu**.
**🎁 Bedava ölçüm — hakemin yeniden-koşum gürültüsü.** İki koşunun cevapları **bit-birebir aynı**; tek değişen altın etiketti ⇒ fark **saf hakem gürültüsüdür**: iddia 276 → 268 · A1 **0,27 puan** · kütle 0,21 puan.
> **Kullanım kuralı:** `n=80`, `temperature=0`, aynı girdi ⇒ **A1'de ~0,3 puanlık hareket GÜRÜLTÜDÜR.** Bunun altındaki farklar yorumlanmaz. *(S2'nin +3,6 puanı bu tabanın **on katı** — gerçek. ⚠️ Tek gözlem, güven aralığı değil.)*

**10. ⭐ AÇIK ↔ KAPALI açığının ayrıştırması — *"suç modelde mi harness'ta mı"*.** *İki ölçüm aynı şeyi ölçmüyor: KAPALI'da altın madde **kurgu gereği garanti**, AÇIK'ta **bulunması gerekiyor**.*
```
KAPALI %71,6   →   AÇIK %61,3        açık = 10,2 puan
① ERİŞİM ISKASI  altın 10/80 soruda HİÇ gelmiyor        ≈ 5,1 puan (yarısı)
② ALTIN BAĞLAMDA getirilen 70 soruda KAPALI'dan sapma   ≈ 4,5 puan (yarısı)
   ├ çekinme 0,771 ↔ 0,787 → neredeyse AYNI
   └ sadakat 0,862 ↔ 0,909 → DİKKAT DAĞILMASI
```
**Hüküm: açığın yarısı harness'ın (erişim ıskası), yarısı modelin (dikkat dağılması).** *Ne "model kötü" ne "harness kötü" — ikisi de ölçülmüş büyüklükte ve **ikisi de kapatılabilir**.*
**🚨 Ve bir çerçeve düzeltmesi: aşırı-red harness'ın SUÇU DEĞİL.** KAPALI **17/80 = %21,2** (altın **garanti** bağlamda) ↔ AÇIK **16/70 = %22,9** (altın getirilen alt küme) ⇒ **iki oran neredeyse aynı**: *model, elinde doğru madde varken cevap vermemeyi **harness'tan önce de** yapıyordu; harness bunu **ne yarattı ne büyüttü**.* **B10 bir model özelliğidir** — ve bu, *"eğitimle kapanır, harness'la kapanmaz"* hükmünü **zayıflatmıyor, kanıtlıyor.**
⚠️ **Sonucu:** harness'ı ne kadar iyileştirirsek iyileştirelim **%21'lik bir çekinme tabanı** duruyor ⇒ kütlenin üst sınırı bugünkü modelle `0,79 × 0,91 ≈ **%71,6**` — ***KAPALI sayısı bir TAVAN, hedef değil.***

---

<a id="56"></a>
## #56 — Ölçüm boşlukları: m2b harness AÇIK · B5 · B8 · B-i

**2026-08-05 · GPU $0 · hakem $0,075** (bütçe ≤ $2) · geçit: n=80 · kesik %3,8 · `ALTIN_SIZAN=0` · **üç koşuda da GEÇTİ**
Kararlar: [ADR-0057](../adr/kararlar-0045-0063.md#adr-0057) *(eşit sınav)* · [ADR-0056](../adr/kararlar-0045-0063.md#adr-0056) · [ADR-0055](../adr/kararlar-0045-0063.md#adr-0055)

### 1. Ö1 — `m2b` harness AÇIK: kapı KALDI

```
kol                kaynak   Rej*   Rej_rgx  payda  geçersiz  kapı_red  atıfsız  zorluk
KAPALI m2b (çıpa)      4   0,877    0,846     65       15        -        -    1,0000
AÇIK  h2b k=4          4   0,840    0,820     50       30        2       36    0,4750  ← HÜKÜM
AÇIK  h2b k=10        10   0,784    0,706     51       29        4       34    0,4350    ⚠️TANIMSIZ
```
> 🚨 **TANIMSIZ ᴷ⁴ — `k=10` SATIRININ PAYDASI.** Kör payda hakemi kaynağı `SOURCE_CLIP = 3500` ile kırpılmış görüyor; ölçüldü: **k=4 → 320/320 kaynağın %100'ü** · **k=10 → 454/800, yani %57'si.** ⇒ **payda ekseni EŞLEŞMİYOR** → ADR-0057 gereği bu satır **TANIMSIZ**: *sayı kayıtta kalır, ondan **hüküm kurulmaz**.* ⛔ **Yumuşatılmaz** — *"muhtemelen yine de geçerli"* denmez. **Alet kuramadığı hükmü kurmaz.**
> 🚨 **ᴷ³ BU GİRİŞİN M2b SAYILARI ESKİ ALETİN BİRİMİNDE.** Yeniden puanlanmış: AÇIK `h2b@k=4` **0,840 → 0,735** · KAPALI çıpa **0,877 → 0,766** · k=10 **0,784 → 0,723**. ⭐ **HÜKÜM AYAKTA:** `0,735 < 0,766`, işaret aynı, kapı yine **KALDI**.
> 🎁 Ve bu girişin *"geçersiz tuzak 30/80 ↔ 15/80"* gözlemi **aletin kusuruymuş**: aynı sınavda payda artık üç kolda da **eşit (68)** ⇒ o paragrafın **mekanizma açıklaması çürüdü**.

⚖️ **ADR-0057 Kademe 2 kapısı: KALDI.** İki bağımsız tahmin edici de aynı yönde (**−0,037** hakem · **−0,026** regex), ikisi de **~0,3 puanlık** gürültü tabanının üstünde.
🚨 **Ve zorluk şerhi bulguyu ZAYIFLATMIYOR, GÜÇLENDİRİYOR.** KAPALI'nın 4 çeldiricisinin **tamamı** altınla aynı kanundan (komşu-öncelikli seçim) → zorluk **1,0000**; AÇIK'ta **0,4750**. *Dağınık bağlamda "kaynak yetmiyor" demek daha kolaydır.* ⇒ ***AÇIK daha KOLAY sınava girdi ve yine de kaybetti.***

**Ön-kayıtlı tahminler (ADR-0056 Karar 2).** **A** kapının katkısı ≈0 → ✅ **TUTTU** (k=4'te kapı 2/80 reddetti). Mekanizması da doğrulandı: `KANUN_YOK 0 · MADDE_YOK 0` ve **36/80 cevabın hiç atfı yok** — *kapı yalnız doğrulanamayan atıf varken ateşler; **ateşleyecek şey yok**.*
⇒ ***Part 1'in M2b iddiası "sınanmamış" değil, bu rejimde YAPISAL OLARAK ateşlenemez*** ⇒ **M2b eğitim tarafına geçer.**
**B** `Rej_model` 0,30-0,60 → **0,840**, ❌ TUTMADI. **ADR-0056'nın kendi kuralı geçerli:** *"tutmazsa 'tahmin kötüydü' değil **'payda yanlıydı'** diye oku"* — tahmin altın gelmeyen **10** sorudan türetilmişti ve o alt küme ağırlıkla "belirsiz" sınıfıydı.

**~~🎁 `k`'nın bedeli ilk kez ÇEKİNME ekseninde sayıldı~~ → 🔴 HÜKÜM DÜŞTÜ, BORCA DÖNDÜ.**
> 🚨 **ᴷ⁴:** kıyasın iki kolu **aynı paydayı ölçmüyor** ⇒ ADR-0057'nin kendi mekanizması: **eşleşmeyen eksende hüküm kurulmaz.** *"`k` büyütmenin çekinme bedeli"* bir **BORÇ**tur — **ölçülmüş bir bulgu değil.** *Sadakat eksenindeki bulgu (#54) bundan **etkilenmez**, o payda paylaşmıyor.*

### 2. B5 — K2'nin bedeli (post-hoc, $0)

`ALTIN_GELMEDI 10 · TAM 22 · KIRPILDI 46 · KIRPILDI_CEVAP_DISI 2` (toplam 80 ✓)
🚨 **Planın okuma cümlesi YAPISAL OLARAK İMKÂNSIZDI.** Plan *"`KIRPILDI_CEVAP_DISI`, B1'in 7/80'inden düşülür"* diyordu; oysa `KIRPILDI_CEVAP_DISI` **ancak altın getirildiyse** çıkabilir, B1'in 7'si ise **tam ters popülasyon**. ***İki küme kesişemez.***
**Gerçek yer ölçüldü:** her iki vaka da `altin_geldi_cevapladi` kovasında, **ikisi de 0. sırada** getirilmiş ⇒ **B1 (7/80) ve B10 (16/80) el değmemiş kalıyor; kırpmanın bedeli 2/80 ile dar bir şeride hapsolmuş.**
⚠️ Sınıflandırma **4 sınıflı** tutuldu — *"kırpıldı" tek başına bir şey söylemiyor (46 vaka kırpılmış ama cevabın dayandığı cümle bağlamda duruyor); **tek sınıfa indirmek B5'i 23 kat şişirirdi**.*

### 3. B8 — yazım-hatası tolerans eğrisi (post-hoc, $0, **doğrulayıcı DONUK**)

Üç eşikte de **2 kurtarılan, yanlış eşleme 0**.
🚨 **Ama eğri "eşik 3 güvenli" DEMİYOR — "bu veriyle karar verilemez" diyor.** Üç koşuda toplam **4 `KANUN_YOK` atfı** var ve **hepsi aynı hatanın tekrarı** (`"Sanat Eseleri Kanunu"`). ***Toleransın RİSK tarafında sıfır gözlem var.*** ⇒ Tolerans **BENİMSENMEDİ**, kapı **katı** kaldı.
🐞 **Betiğin ilk hâli sıfır üretiyordu ve sebebi bir ölçüm hatasıydı:** toleransı korpusun **tam adlarına** uyguluyordu, oysa doğrulayıcı ≥2 sözcüklü **sonek** indeksiyle eşleştiriyor — `"Sanat Eseleri Kanunu"` → tam ada mesafe **11**, doğru soneke **1**. Ek koruma: tek sözcüklü soneke inilmiyor (*`mesafe("KANUNU","İŞ KANUNU") = 3`, eşik 3'te **yüzlerce kanuna** eşleşirdi*).
⭐ **Hatanın üç koşuda da aynen tekrarlaması** onu rastlantı değil, modelin **tekrarlanabilir bir transkripsiyon tiki** yapıyor ⇒ *çaresi de tolerans değil, **dar ve hedefli** olabilir.*

### 4. ⚖️ HARNESS KAZANÇ TABLOSU — her satırda adillik hükmü ZORUNLU

```
kademe  eksen                     kaynak    KAPALI    AÇIK     hüküm
  1     kapı + doğrulayıcı        aynı      —         2/80     TAM EŞİT SINAV · katkı ≈0
  2     A1 · altın getirilen      5 ↔ 5     0,9087    0,9230   EŞLEŞMİŞ ✅ GEÇTİ (k=5)
  2     M2b Rej                   4 ↔ 4     0,8770    0,8400   EŞLEŞMİŞ ❌ KALDI (k=4)
  3     M1 manşet kütle           5 ↔ 10    %71,6     %61,3    TAVAN — hüküm YOK
  3     M4 / M3 / M5 / M2         —         —         —        TANIMSIZ
```
⚠️ **Kademe 3 satırları için *"AÇIK burada geride"* cümlesi KURULMAZ.** *KAPALI orada altını **kurgu gereği** alıyor; M4 yalnız altını verir; M3/M5 bağlamın **yokluğuyla** tanımlıdır; M2'de retriever altını bulunca çekinme koşulu **kendini yok eder**.* **Bu ayrım yazılmazsa tablo yanıltır.**
⭐ **Kademe 2'nin iki satırı ZIT YÖNDE ve ikisi de gerçek:** retriever bulduğunda model **daha sadık** (+1,4 p), altın hiç yokken **daha az çekingen** (−3,7 p).

---

<a id="57"></a>
## #57 — Çekinme aletinin onarımı (ᴷ³): M2b'nin paydası modele bağımlıydı

**2026-08-06 · `ff64682` · `0ca4d64` · `c1e99a8`** · Tetikleyen: Görev 2'nin bağımsız incelemesi — **4 kritik + 8 önemli kusur**
> ⚠️ **Birim:** *"puan"* = **yüzde puanı**. Hakem gürültü tabanı `0,3 puan`.

**Manşet: bir turda çekinme dedektörü ÜÇ kez değişti ve dördüncüsünde PAYDANIN KENDİSİNİN bozuk olduğu bulundu.** ① red-regex Gemini için kalibre edildi ② açılış yeterlilik hükmü **bağlayıcı** sayıldı ③ **bağlayıcı olmaktan çıkarıldı** (yanlış-negatif üretiyordu) ④ 🚨 **`valid_trap` paydası cevaba KÖR hâle getirildi** — **asıl bulgu bu**.

**🚨 K3 — paydanın modele bağımlı olması.** `judge()` hakeme soruyu, kaynağı **ve modelin cevabını** tek çağrıda veriyor, `source_answers`'ı aynı JSON'da istiyordu. *Oysa bir tuzağın geçerliliği `(soru, bağlam)`'ın fonksiyonudur — **hangi modelin skorlandığına bağlı olamaz**.*
```
h2b@k=4 sınavı üç kolda BAYT-BAYT AYNI. Buna rağmen:
valid_traps  3.1 FL 45 · 3.5 FL 56 · BİZ 50     ← aynı sınav, ÜÇ AYRI PAYDA
80 kalemin 19'unda üç kol FARKLI karar alıyor   (%24)
BİZİM Rej'imiz paydaya göre 12,9 puan oynuyor:  0,746 ↔ 0,840 ↔ 0,875
```
**Ön-kayıtlı bir kapı için gürültünün en kötü türü: sapma YÖN DEĞİŞTİRİYOR.**
⚠️ **Aynı hata #45'te M2/M3 için görülmüştü** ve ADR-0048/0049 ile **ayrı bir betiğe** çözüm yazılmıştı — **ama aletin kendisi düzeltilmemişti.** ⇒ ***Ders: bir hatayı yan yolda kapatmak, ana yolda açık bırakır.*** *Yeni koşular bozuk aleti kullanmaya devam etti ve hata **üç ay sonra rakip kıyasında** yeniden çıktı.*
**Onarım.** Payda ayrı, **cevaba kör** bir çağrıdan ve **içerik-adresli** önbellekte kalem başına **bir kez** ödeniyor (`sha256(soru ‖ kaynak[:3500])`). *`{mod}:{id}` anahtarı **kasten kullanılmadı**: aynı `id` farklı koşuda farklı bağlam taşıyabiliyor.* Payda hakemi **`gpt-4o`**; pay hakemi **`gpt-4o-mini` KALDI** ve `JUDGE_SYSTEM` **değiştirilmedi** — *istem budansa `verdict` dağılımı da kayardı ve **her tarihsel sayı kıyaslanamaz** olurdu.*
**⭐ Doğrulama: aynı sınavı paylaşan kollarda payda artık EŞİT.** `h2b@k=4` **50/45/56 → 68/68/68** ✅ · `m2b distractor` (10 koşu) **61…80 saçılım → hepsi 77** ✅ · `h2b@k=10` 51 → 65.
*(⚠️ kusur k-1: satır **8 koşu** diyordu, gerçek **10**. **Doğrulama iddiadan güçlüydü, sayım yanlıştı.**)*
Önbellek 16 koşuda **250 ayrık** kalem taşıyor, **eksik anahtar 0**; önbellek olmasa **1225 çağrı** gerekirdi ⇒ **975 çağrı ödenmedi.**

**📊 ÇEVİRİ TABLOSU — eski alet → yeni alet** *(yayılım borcunun **tek kaynağı**; eski sayı **silinmez**, yanına damga konur)*

| koşu / özne | valid_traps | **Rej\* eski → yeni** |
| :--- | ---: | ---: |
| ⭐ `tgta_v1` **M2b (KAPALI)** | 65 → **77** | **0,877 → 0,766** |
| ⭐ `tgta_v1` **h2b@k=4 (önsözSÜZ)** | 50 → **68** | **0,840 → 0,735** |
| ⭐ `tgta_v1` **h2b@k=4 (ÖNSÖZLÜ)** 🆕 | → **68** | → **0,809** |
| `tgta_v1` h2b@k=10 | 51 → **65** | 0,784 → **0,723** |
| `τ_g` | 61 → **77** | **0,607 → 0,506** |
| `τ_a` | 77 → **77** | **0,987 → 0,987** *(değişmedi)* |
| `tg_ta_min` | 79 → **77** | 0,987 → **0,987** |
| base (cp09) | 72 → **77** | 0,986 → **0,961** |
| Gemini (cp09) | 65 → **77** | 1,000 → **0,883** |
| 3.1 FL `h2b@k=4` | 45 → **68** | 0,978 → **0,809** |
| 3.5 FL `h2b@k=4` | 56 → **68** | 0,982 → **0,926** |

**16 koşu yeniden puanlandı**; eski özetler `.ONCEKI-PAYDA` olarak **silinmeden** duruyor.
**Hükümlerin çoğu AYAKTA — ama gerekçelerinin sayıları değişti.** ✅ **ADR-0052 ayakta** (*"ham TIES `τ_a`'yı silmedi"* kanıtı 0,607→0,877 idi; yeni aletle 0,506→0,766 — **sıçrama aynı, +0,26**) · ✅ **#56'nın hükmü ayakta** (`0,735 < 0,766`, **işaret aynı**) · ✅ Görev 7 kol kapısı değişmiyor · ⚠️ Görev 9 kapısı **eski aletin biriminde** → eşik **yeni çıpadan yeniden türetilmeli**; yeni çıpa yazıldı, **eşiğe dokunulmadı**.
**🚨 Kapanmayan: M2 ve M3'ün paydası HÂLÂ modele bağımlı** (`m3` 54/56/**39** — 17 kalemlik saçılım). *ADR-0048 m.2'ye göre M3'ün paydası **tanım gereği 80/80** olmalı ⇒ **üçü de yanlış**.* Kapatması **hakemsizdir.** **Borç.**

**Ö2 — açılış yeterlilik hükmünün bağlayıcılığı yanlış-negatif üretiyordu.** Yapısal kusur: *bu, **modelin kendi beyanını gerçek davranışının önüne koyar** — ve model hükmü yanlış kurabiliyor.* Ölçülen vaka cevabın kendi açılışını **cümle sonunda yalanlaması**: *"…cevaplamaktadır. … **bulunmamaktadır** … bu nedenle … **bulunmuyor**."*
**Düzeltilmiş kural:** açılış hükmü **bağlayıcı değil**; çelişkide **gövde öncelikli** ve hükmü **son esaslı ibare** taşır. *(çekinme: olumsuzlama **SONUÇ** konumunda · dolu cevap: olumsuzlama **KARŞITLIKLA** çözülmüş — *"…bulunmamaktadır; **ANCAK** … kapsamındadır"*.)*
**Etki kapalı ve ölçüldü:** kesişim **5 cevap**, **3'ü** çekinmeye döndü ve yön **rakibin lehine**; çıpalarımız **değişmedi**. ⚠️ **Olumsuz kutup bağlayıcı KALDI ve bu bir ölçüm sonucudur:** repodaki **28** olumsuz açılışlı cevabın hepsi 500 karakterin altında.
*Görev 2 raporu "tüm `outputs/eval` tarandı" diyerek **8 dosya** saymıştı; gerçek **11**.*

**K1 — `reasoning_tokens`: `None` ile `0` karıştırıldı.** Sunucu alanı **80/80 bildirmiş**; bazı kalemlerde değer **gerçekten 0**. Eski ortalamalar yalnız `rt>0` olanların **koşullu** ortalamasıydı. 🚨 ***OZET'teki "3.5 FL daha çok muhakeme harcıyor" cümlesi TERSİNE YANLIŞTI*** ve kaldırıldı: 3.5 FL **%42 azını** harcıyor (ort **445,2**, medyan **198**, **39 kalemde 0**). **Gerçek şekil iki kutuplu.**
**K2 — muhakeme bütçesi RAKİP TARAFINDA UYGULANMIYOR.** Kesik kalemlerin muhakeme token'ları **hepsi 1024'ün üstünde** (en büyük **1475**); `extra["reasoning"]` sağlayıcı tarafından **yok sayılıyor**. ⇒ ***"Bütçe eşleşik" YANLIŞTI: **nominal** bütçe aynı, **etkin** bütçe değil.*** **Ve 3.5 FL'ın %10 kesikliğinin gerçek sebebi budur — modelin özelliği değil, rejimin.**
**Ö1 — kesiklik şerhinin yönü ölçülmeden yazılmıştı, ve TERSTİ.** Kesikliği kaldırmak **bize 3.5 FL'dan 6 kat çok yarıyor** (+3,0 p ↔ +0,5 p); fark **6,7 → 4,2 puana daralıyor** ⇒ *hüküm "muhafazakâr" değil, **bizim aleyhimize** eğilimliydi.* Artık her sayı **hem 80'de hem n=68'de** raporlanıyor.
**Ö7 — `$/cevap` yalnız çıktıydı; girdi dahil edilince sıralama TERSİNE dönüyor.** Girdi token'ı **ölçüldü** (tahmin değil): 3.1 FL **$0,002074** ↔ 3.5 FL **$0,002175** ⇒ *3.5 FL yalnız çıktıya bakılınca **%1,5 ucuz**, girdi dahil **%4,9 pahalı**.*

**Küçük düzeltmeler.** *"Çekinme milimetre oynamadı"* **toplam eşitliğinden** kurulmuştu; kalem düzeyinde örtüşme **8/10** ⇒ doğru okuma: ***aşırı-red ORANI değişmedi, HANGİ KALEMLERDE olduğu değişti*** · **gürültü tabanı eksen karıştırıyor** (`0,3 puan` **A1** için ölçüldü, çarpanlar **kütle** üzerinde kurulmuş ⇒ çarpanlar **üst sınırdır, ölçü değil**) · **kendi karşıolgumuz damgasızdı** → **TAVAN/VARSAYIMSAL** damgası basıldı · künye koşan kodu tarif etmiyordu · önbellek yazımı kayıpsız yapıldı (*kilitsiz sürümde 8 eşzamanlı süreçte **2 kalem sessizce kayboldu***).
**Ö5 — M2b ekseni EŞLEŞTİ** (yerel koşu, $0): önsözlü `h2b@k=4` → `valid_traps 68 · Rej* 0,809`.
**Bütçe:** kör payda hakemi **$0,8021** + pay ~$0,29 + girdi ölçümü ~$0,09 = **~$1,18** ⚠️ **plansız**. *Önbellek olmasaydı payda 1225 çağrı ederdi (≈$3,93) ⇒ **$3,13 tasarruf**.*

> **Ders (bu hattın tekrar eden hata sınıfı):** ***ölçüm aletinin bir kolunu düzeltip diğerini bırakmak, hatayı kapatmaz — TAŞIR.*** ADR-0048 paydayı **yan bir betikte** düzeltti, ana alet bozuk kaldı ve aynı hata **üç ay sonra** yeniden çıktı. **Alet düzeltmesi aletin kendisinde yapılır.**

---

<a id="58"></a>
## #58 — Payda tekilleşmesi (ᴷ⁴): anahtar paylaşımı, iki rakip alet, ve ARA KAPI'nın hükmü döndü

**2026-08-06 · GPU yok · hakem $0,056** · Yeni tuzaklar: **2.17** · **2.18**
> 🚨 **BU KAYDIN §1 REÇETESİ AYNI GÜN GERİ ALINDI** (KARAR-4 · [ADR-0060](../adr/kararlar-0045-0063.md#adr-0060)). **Teşhis ayakta, çare değişti.** Eski metin silinmedi.

**Özet — bir cümlede:** #57 paydayı **cevaba kör** yaptı; bu tur onu **tek** ve **doğru anahtarlı** yaptı, ve o tekilleşme **ARA KAPI'nın 2. gözlemini ✅'ten 🔴'ya çevirdi.**

**1) K-1 — önbellek anahtarı klipli metnin üzerindeydi (tuzak 2.17).** `source[:3500]` hash'leniyordu ⇒ **farklı sınavlar aynı payda kaydını paylaşıyordu**: `h2b@k=10`'da **79/80 kalem klipi aşıyor**, `k4 ∩ k10` çakışması **15 kalem**. *Özet dosyası bunu gizlemiyordu, **övünüyordu**: `"gecerlilik_devralinan": 15`.*
> 🚨 **REÇETE AYNI GÜN TERSİNE ÇEVRİLDİ.** Tam-metin anahtarı tuzak 2.17'yi kapatırken **daha büyüğünü açıyordu** — *hakemin **ayırt edemediği** bir farka göre bölünen anahtar **"aynı istem → aynı cevap"** değişmezini kırar* (ölçüldü: 5.363 istemin **65'i >1 anahtara** · **83 garantili gereksiz çağrı**). Üstelik **onarımın sayısal karşılığı yoktu.** Gerçek çare **klibi büyütmektir** (≈$0,30); ödenene kadar `k=10`'un paydası **TANIMSIZ** damgasıyla taşınır.

**⚠️ K-1'in SAYISAL iddiası doğrulanmadı — ve bu bir bulgudur.** 15 payda **yeniden ödendi** ($0,056): **payda dönen 0 · verdict dönen 0 · `Rej* 0,723 → 0,723` (kılı kıpırdamadı).**
**Sebep ölçülebilir ve önceden görülebilirdi:** *klip sabitken çakışan çiftin hakem istemi **bayt-bayt aynı**, dolayısıyla yeniden ödeme **tanım gereği** aynı cevabı verir.* ⇒ **Anahtar onarımı YAPISALDIR, sayısal değil.** *Yan kazanım: bu, payda hakeminin **yeniden koşum gürültüsünü** de ölçtü — **15/15 aynı**.*

**2) K-3 — iki rakip alet, ve 900 klipi bir KATEGORİ HATASI (tuzak 2.18).** `valid_trap_cache.py` (klip **900**) ve `score_abstention.py` (klip **3500**) aynı koşularda **çelişen** payda üretiyordu; farklar **gürültü tabanının 4-7 katı**.
**İki klip aynı şey mi? HAYIR — ve bu ölçüldü.** **900** = ADR-0011'in **eval-ayna** klipi, **üretim** zamanında **her `[KAYNAK]` parçasına AYRI** uygulanır ⇒ `context_shown` **zaten kırpılmış parçaların birleşimidir**. **3500** = **skorlama** zamanında, hakeme giden metnin **tamamına**. ⇒ ***`valid_trap_cache.py` PARÇA SABİTİNİ BİRLEŞİME uyguluyordu.***
```
cp09 m2b (n=80):  tam metin 320 kaynak · klip 900 → 147 (%46) · klip 3500 → 320 (%100)
h2b@k=10:         3500'ün de yetmediği ölçüldü → 454/800 = %57
```
**Onarım:** `valid_trap_cache.py` **ince sarmalayıcıya** indi · `rescore_abstention_cached.py` **silindi** (*oranları ikinci bir yerde bölüyordu **ve** `reject_exact`i **bayat dedektörden** okuyordu*). #46 **damgalandı, silinmedi.**

**3) KARAR-2 — boş bağlamda payda tanım gereği n/n** (ADR-0048 m.2 **alete alındı**). *Kural aletin **dışında** durduğu için M3 skorlaması **altın maddeyi** hakeme gösteriyor, hakem "kaynak cevaplıyor" deyip tuzağı geçersiz sayıyordu.* Altı koşu yeniden puanlandı, **$0**: m3 paydaları **39/50/54/56/57/57 → hepsi 80**. **En büyük hareket aleyhimize:** `τ_g`'nin M3'ü `0,923 → 0,800` (**12,3 puan düştü**).
🔴 **`m2` kapanmadı** — fiyatı ölçüldü (**≈$0,11**, tek ödeme 10 koşuyu kapatır) ve **durup soruldu**. *Bir kestirme **bilerek reddedildi**: #46'nın damgası 52 kalemde $0'a devralınabilirdi ama o damga `gateway=openai` ile üretildi, bugünküler `openrouter` ⇒ hakem yığını şartı.*

**4) ⭐ K-2 — ARA KAPI 2. gözlemi yeniden türetildi ve DÜŞTÜ.** Ön-kayıtlı olan **formüldü, sayı değil**; ⛔ eşiğe/çarpana/formüle **dokunulmadı**:
```
eşik  = 0,90 × base M2b 0,961 = 0,8649
merge = 0,766  (ham TIES, payda 77)   →  🔴 DÜŞTÜ, 9,9 puan altında
eski 0,887 eşiğine karşı da           →  🔴 DÜŞTÜ
paydalar EŞİT (77 ↔ 77)               →  kıyas geçerli
```
| tarih | base M2b | eşik | merge | hüküm |
| :--- | ---: | ---: | ---: | :--- |
| 2026-07-29 (ön-kayıt) | 0,986 *(cevaba bağlı)* | 0,887 | — | — |
| 2026-07-30 (#46, klip 900) | 0,949 | 0,8541 | 0,877 | ✅ GEÇTİ |
| **2026-08-06 (yürürlükte)** | **0,961** | **0,8649** | **0,766** | **🔴 DÜŞTÜ** |

***Bu kapı CP4-CP5 harcamasını yetkilendiren kapıydı — yetki bugünkü ölçümle YOK.*** Satır ya `✅ ❌` ya `❌ ❌`; **ön-kayıtlı tabloda her iki hâlde de karar DUR.**
**ADR-0052'nin kendi hükmü etkilenmiyor** — değişen, ham TIES'in **mutlak** olarak kapıyı geçip geçmediği. Onarım oranı **%71 → %57**.

**5-8. Diğer düzeltmeler.** **Ö-B** ADR-0058'in ablasyon koşusu **emekli dedektörün sayısını** taşıyordu (`0,452 → 0,484`, **gürültü tabanının ~10 katı**); hükme etkisi yok ama **sayı kayıtta yanlış duruyordu**. **Ö-C** kesiklik kapısı **simetrik** uygulandı — *repo kendi varyantını %5,2 ile geçersiz saymıştı; rakip kolu **%10,0** kesikle **manşet hükmün kurulduğu** koldu ve **şerhi yoktu**.* Ortak kesiksiz alt kümede **açıklık daralmıyor, GENİŞLİYOR** (11,7 → **15,0 puan**) ⇒ hüküm **ayakta ve güçlenmiş** — *ama şerh olmadan kurulamazdı.* **Ö-D** açılış-hükmü kuralının maruziyeti **~8 kat asimetrik** (`h2b_fl35_k4` 39/80 ↔ BİZ önsözsüz **0/80**); *kaydın savunması bir **gözlenen etki** argümanıydı, **maruziyet** argümanı değil: kuralın çevirdiği 3 satırın **üçü de** manşet hükmün kurulduğu kolda.* Kural **değiştirilmedi**. **Ö-E** sınır çizildi, kural **onarılmadı**, gerekçe ölçüldü — *iddia edilen kaçak şekli gerçek ama **korpusta 0 vaka***; sınır bir **`xfail(strict=True)`** testiyle çizildi: *kusuru **kilitlemez**, kural düzelirse test **patlar**.*
**Alet tarafındaki kalıcı değişiklikler:** `payda_tanimdan_gecerli(mode)` · `--pay-kaynagi {hakem,onceki}` · `--payda-kaynagi` · `yedekle()` (*yayımlanmış çıktının üstüne **sessizce** yazılmaz*) · `llm_client.gateway_of()` · maliyet alanlarının ayrıştırılması.

---

<a id="59"></a>
## #59 — M2 paydası kapandı · KARAR-4 · ARA KAPI 1. gözlem türetildi

**2026-08-06 · GPU $0 · hakem $0,1054** *(bütçe ≈$0,11)*
> **İki cümlede:** `m2` paydası on koşuda birden ödendi ve **eşitlendi (66/70)** — düzeltme **bizim lehimize** çıktı ve öyle raporlanıyor. K-1'in tam-metin anahtarı **geri alındı**; bedeli `k=10` paydasının **TANIMSIZ** damgasıyla açıkça ödendi.

**1. KARAR-3 — `m2` paydası: on koşu, tek ödeme, eşit payda.** `m2`, paydası hâlâ modele bağımlı kalan **tek** moddu (aynı 70 kalemlik sınavda on kol **55-63** arası payda).
**$0'lık kestirme REDDEDİLDİ:** o ölçüm `gateway=openai`, bugünküler `openrouter` ⇒ **ucuz ve yanlış bir sayı, pahalı ve doğru olandan kötüdür.**
**Sınav paylaşımı ölçüldü, varsayılmadı:** on koşunun anahtar kümesi **70/70 kesişiyor**.

| özne | payda | **Rej\* eski → yeni** | Δ |
| :--- | ---: | ---: | ---: |
| çıplak base (bütçeli) | 59 → **66** | 0,814 → **0,803** | −1,1 p |
| **Gemini 3.1 FL** | 57 → **66** | 0,930 → **0,848** | **−8,2 p** |
| `τ_g` v1 | 55 → **66** | 0,873 → **0,833** | −4,0 p |
| base + önsöz | 62 → **66** | 0,968 → **0,924** | −4,4 p |
| **ham TIES = `tgta_v1`** | 56 → **66** | 0,893 → **0,833** | −6,0 p |
| norm-dengeli `min` | 61 → **66** | 0,934 → **0,909** | −2,5 p |
| ⭐ **`τ_a` v1** | 63 → **66** | 0,984 → **0,955** | −2,9 p |
| base (thinking-off) | 60 → **66** | 0,633 → **0,606** | −2,7 p |
| **Gemini (thinking-off)** | 57 → **66** | 0,842 → **0,758** | **−8,4 p** |
| `τ_g` (thinking-off) | 59 → **66** | 0,458 → **0,439** | −1,9 p |

> ⚠️ **DÜZELTME (küçük k1).** İlk yazımda buna *"kendi kendini doğrulayan sınav"* denmişti; **fazla güçlüydü**. 70/70 kesişimi verildikten sonra payda eşitliği bir **teorem**, bağımsız bir gözlem değil. ⭐ ***Bilgi taşıyan asıl kontrol, anahtar kesişiminin KENDİSİdir*** (70/70) — *o gerçekten düşebilirdi ve düşmedi.* `{66}` kontrolü **bedava bir alet denetimi** olarak değerli ama *"sınav paylaşılıyor mu"* sorusuna **bağımsız kanıt sunmaz**. 🚨 **2. dalganın totolojisiyle AYNI SINIFTA DEĞİL:** *o kontrol tanımı gereği **düşemezdi**; bu **düşebilir**.*

**🚨 Düzeltmenin yönü BİZİM LEHİMİZE — ve bu yüzden ayrıca yazılıyor.** En çok kayan özne **RAKİP** (Gemini −8,2 ↔ biz −6,0); açıklık **3,7 → 1,5 puana** daralıyor. ⚠️ *Aynı sınıftaki [#46](kronoloji-39-52.md#46) düzeltmesi **ters yöne** gitmişti (aleyhimize). **İki turda da yön seçilmedi, ölçüldü — ve her ikisi de raporlandı.***
**🎁 Beklenmedik çapraz kontrol: iki alet `m2`'de AYNI paydayı veriyor** (66/70). *Bu, K-3'ün teşhisini **daraltarak doğruluyor**: 900 klipi bir kategori hatasıydı ama zararı **birleştirilmiş çok-kaynaklı** bağlamda doğuyor; `m2`'nin kaynağı tek bir altın madde (medyan **587** karakter) — **iki klip de tamamını gösteriyor**.*

**2. ⭐ ARA KAPI 1. GÖZLEM — türetildi, GEÇTİ, ve ilk kez BİRİM-TUTARLI.**

| bacak | formül | çıpa | eşik | `τ_a` tekil | hüküm |
| :--- | :--- | ---: | ---: | ---: | :--- |
| M2 Rej | `base M2 + 0,12` | 0,803 | **0,923** | **0,955** | ✅ GEÇTİ (+3,2 p) |
| muhafız M1 A1 | `0,90 × base A1` | 0,9777 | **0,8799** | **0,9697** | ✅ GEÇTİ |
| ön-kayıtlı ham sayılara karşı | — | — | 0,934 · 0,888 | — | ✅ **ikisi de** |

🚨 *Sprint 2 kapanışındaki `0,984 ≥ 0,923` kıyası **karışık birimdeydi**: pay özneye bağlı paydadan, eşik #46'nın kör çıpasından.* **Hüküm aynı kaldı, ama gerekçesi ilk kez sağlam.**
> 🚨 **DÜZELTME (kusur Ö1) — bu cümlenin ilk hâli KARIŞIK BİRİMDEYDİ.** *İronik biçimde **"ilk kez birim-tutarlı"** iddiasını taşıyan cümlenin **kendi marjı** iki farklı referans noktasından okunmuştu.* Eşleşen okumalar: **eşiğin üstü** +6,1 → **+3,2 p** (~1,9×) · **çıpanın üstü** +18,1 → **+15,2 p** (~1,2×). ⚠️ *Karışık hâli okuyan biri "payda onarımı marjı **5,7 kat** eritti" der ve `τ_a`'nın kapıyı **kıl payı** geçtiğini sanır. **Gerçekte kol kapıyı RAHAT geçiyor** — ki teşhis (sorun `τ_a` değil, merge'in onu taşımaması) tam buna dayanıyor.* **Kural: bir marj/fark yazarken REFERANS NOKTASI cümlede söylenir.**

**⇒ ADR-0045 §3'ün ön-kayıtlı tablosunda satır: `✅ ❌` → DUR.** *"Kol tek başına iyi ama birleşince taşımıyor; iç iddianın öncülü sorunlu."* **Türetme hükmü değiştirmedi ama TEŞHİSİ BELİRLEDİ:** sorun `τ_a`'nın kalitesi **değil** — kol kapıyı **rahat** geçiyor — **merge'in onu taşımaması.**

**⭐ Kaydedilmemiş sonuç — merge'in M2'ye katkısı `+0,020` → `+0,000`.**
```
τ_g v1   55/66 = 0,833        tgta_v1  55/66 = 0,833      katkı: ~~+0,020~~ → +0,000
```
*İki kol **birebir eşit** — aynı payda, aynı pay. Emekli alette merge `τ_g`'yi **+0,020** geçiyor görünüyordu; o fark tümüyle **paydaların farklı olmasından** geliyordu.*
⭐ **Bu gözlem ARA KAPI'nın teşhisini BAĞIMSIZ olarak güçlendiriyor:** M2b ekseninden türetilen *"merge `τ_a`'yı taşımıyor"* hükmünü M2 ekseni **ikinci, bağımsız bir yerden** söylüyor — *merge M2'de `τ_g`'nin **üstüne hiçbir şey koymuyor**, oysa `τ_a` tek başına o eksende **0,955**.*
⚠️ **Şerh (kuantum):** `+0,000` *"hiç fark yok"* demektir, *"fark ölçülemedi"* demez (iki kol aynı 66 kalemde **aynı 55'inde** çekiniyor). **Ama ters yön de doğrudur:** bu eksende `1/66 = **1,52 puanlık**` bir kuantum var ⇒ `+0,000` ile `±1 kalem` arasında **ayrım kurulamaz.**

**3. KARAR-4 — K-1'in anahtar onarımı GERİ ALINDI, bedeli damgayla ödendi.** Onarım (yapısal, $0): klip artık **tek yerde**; pay hakemi, payda hakemi ve önbellek anahtarı **üçü de oradan besleniyor, ayrışamazlar**. Göç kayıpsız (**değer uyuşmazlığı 0**).
**🔴 Bedeli: `k=10`'un paydası TANIMSIZ.** `h2b@k=4` hakemin gördüğü **320/320 = %100** ↔ `k=10` **454/800 = %57** ⇒ payda ekseni **eşleşmiyor**. **#56'nın *"`k` büyütmenin çekinme bedeli"* hükmü hüküm olmaktan çıktı, BORCA döndü.** *Sadakat eksenindeki bulgu (#54) **etkilenmiyor** — o payda paylaşmıyor.* ⛔ Yumuşatılmadı: **alet kuramadığı hükmü kurmaz.**

**4. Kod kusurları — biri #58'in kendi kestirmesini OTOMATİKLEŞTİRMİŞTİ.**
**🔴 K1 · `cp2c_kabul.sh` openai kapısıyla ORTAK önbelleğe yazıyordu.** Anahtar **hakem modelini de kapıyı da taşımıyor**; okuma yolunda `hakem` alanı **hiç okunmuyordu**. **Başarısızlık biçimi:** *zincir bir kez koşarsa sonraki herhangi bir openrouter ölçümü aynı çiftte **openai paydasını sessizce devralır** ve özetine `judge_gateway: "openrouter"` yazar.* ⇒ ***Bu, KARAR-3'te ELLE REDDEDİLEN kestirmenin ta kendisidir — dalga kestirmeyi reddetmiş, sonra otomatikleştirmişti.***
Onarım: kayıt `hakem` + `kapi` taşıyor, uyuşmazlıkta **DURUYOR**; *damgasız eski şema kaydı da uyuşmazlıktır — **"bilinmiyor" sessizce "uyuyor" olamaz.*** ⚠️ `cp2c_kabul.sh`'in openai varsayılanı **değiştirilmedi**: *kabul ölçütünü hangi yığının ürettiği bir **rejim kararıdır**, sessiz bir düzeltme değil.*
**🔴 K2 · `%71` onarım oranı üç canlı belgede eski aletin türetmesi — ikisi DAMGANIN ALTINDA.** Oran `(merge − τ_g)/(base − τ_g)` ⇒ **üç girdiden herhangi biri** yeniden puanlanınca kayar: `%71,2 → %57,1`. *Girdiler yerinde güncellenmiş, **türetilmiş nicelik güncellenmemişti** — üstelik iki satır `ᴷ³` taşıyordu, yani **"gözden geçirildi" diye TASDİK EDİLMİŞ** bir yanlış sayı.* **Damgasız olmaktan zararlı.** Süpürge `grep` ile yapıldı ve **iki belge daha buldu** (bulgu listesi üç saymıştı, gerçek **beş**).
⭐ **Kural yazıldı: `ᴷ³` damgası TÜRETİLMİŞ NİCELİKLERİ DE KAPSAR.**
**Ö5 · `gecerlilik_devralinan` iki taban tabana ZIT şeyi sayıyordu** (toptan devralma ↔ **sınav paylaşımı**) ⇒ *tuzak 2.17'nin öngördüğü kontrol tam bu alana dayanıyordu ve **koşulamıyordu**.* **k-3 ·** bütçe kesintisi damgasızdı (`n` ve payda **sessizce** küçülüyordu).

**Dersler.** ① ***Bir onarımın sayısal karşılığı yoksa, açtığı gürültü yolu NET ZARARDIR.*** ② ***Damga, türetilmiş niceliklere de yürür*** — *girdileri yenileyip oranı unutmak, damgasız bırakmaktan **daha kötüdür**: sayı artık **tasdikli** yanlıştır.* ③ ***Bir sayaç iki şeyi sayıyorsa, ona dayanan kontrol koşulamaz.*** ④ ***Kestirmeyi elle reddetmek yetmez*** — reddedilen bir yolun **kodda kapalı olduğu** ayrıca doğrulanmalı.

---

<a id="60"></a>
## #60 — B10 hasadının kabul ölçütü çöktü: `exact_reject` doğru cevapları çekinme sayıyor

**2026-09-06 · GPU Modal L4 ~50 dk · hakem $0 · ÇIKTI KULLANILAMAZ**
**Hüküm: 🛑 Görev 4 başlatılmadı.**

```
np1  denenen 150 · kabul 26 · kabul_orani 0,1733 · 13,735 s/üretim
np8  denenen 150 · kabul 29 · kabul_orani 0,1933 ·  ~5,1  s/üretim   (2,57×)
```
Plan Adım 3.8 **10 kabul kalemini gözle okumayı** emrediyor (ADR-0051 dersi). **Okundu — ve kapıyı düşürdü.**

**⭐ Bulgu: kabul edilen kalemlerin ÇOĞUNLUĞU çekinme DEĞİL** — `rejected` alanı aslında **tam, atıflı CEVAP: 6/10**. Örnek (`raft11188`): *"3) Sonuç olarak, itiraz süresi **yedi gündür** (İCRA VE İFLAS KANUNU, Madde 225)."*

**Kök neden — kesin, tekrarlanabilir.** Hasat **yeterlilik önsözü OLMADAN** koşuyor; o rejimde açılış hükmü oluşmuyor (**26/26 kalemde `None`**) ve `exact_reject` o dalda **cevabın TAMAMINI** tarıyor. Havuzun şablonu:
```
1) [gerekçe] … diğer kaynaklar … İÇERMEMEKTEDİR   ← REJECT_RE BURADA tetikleniyor
3) Sonuç olarak, <CEVAP> (KANUN, Madde N).        ← gerçek hüküm BURADA
```
⇒ **Tetikleyen ibare cevabın hükmü değil, ELENEN KAYNAKLARIN GEREKÇESİ.** ⚠️ Doğru okuyan yol (`_son_esasli_ibare`, #57/Ö2 ile eklendi) **yalnız açılış hükmü `True` iken** çalışıyor.
**Sonucu: ön-kayıtlı D1 kapısı aslında DÜŞÜYOR.** raporlanan **0,1733** (kapı geçmiş **görünüyordu**) ↔ gözle okumaya göre **~0,07** (eşik 0,10'un **altında**).
> *Görev 4 koşulsaydı ~250 kalemin çoğunluğu **doğru atıflı cevap** olarak `rejected` etiketiyle ORPO'ya girecek, `τ_a` v2'ye **"doğru cevap verme"** öğretilecekti — **turun hedefinin tam tersi**. **Kapıyı tutan tek şey planın gözle-okuma adımı oldu.***

**⚠️ Çıpalara bulaşma: KANITLANMADI, kapanmadı da.** Programatik sonda resmî çıpada **10 kalemi** işaretledi; üçü gözle okundu: id 7 ❌ **sonda yanıldı** (gerçek çekinme) · id 19 ✅ gerçek yanlış pozitif · id 20 ❌ **sonda yanıldı**.
🚨 **Sonda HER İKİ YÖNDE de hatalı** ⇒ *"çıpanın 19 redinin 10'u yanlış"* **kurulmadı ve kurulmamalıdır.** Kesin olan iki şey: ① çıpada **en az bir doğrulanmış yanlış pozitif** var ② önsözlü resmî koşuda bile açılış hükmü **75 `None` / 5 `True`** ⇒ cevapların **%94'ü** aynı hatalı dala düşüyor. **Çıpa bulaşmasının büyüklüğü ÖLÇÜLMEMİŞ.**
**KARAR-6 kıyası — toplandı ama BOZUK ölçütle** (Jaccard 0,5278) ⇒ hüküm **kurulmadı ve kurulamaz da**.
**Yine de ödenen: taşıyıcı doğrulandı.** Sızıntı süzgeci konteynerde yerelle **birebir** (13.350 → **12.914**, atılan 436) · GPU'ya yüklendiği ölçüldü (**65,8 tok/s**; CPU olsa ~5) · Modal hasat yolu çalışır durumda.
🐞 İki alet kusuru düzeltildi (`os.chdir` linker'ı kırıyordu → kod 127; `--version` probu künyeye **linker hatası** yazıyordu) · üçüncüsü düzeltilmedi (ilerleme satırı **yalnız reddedilen** kalemlerde basılıyor ⇒ **ilerleme ölçer olarak güvenilmez**).

**Ders.** ⚠️ **Bu, #57'nin dersinin tekrarı:** *"alet düzeltmesi aletin kendisinde yapılır."* `_son_esasli_ibare` **tam bu sınıf hata için** eklenmişti ama **yalnız bir dala** bağlandı; **üç hafta sonra** yeni bir tüketicide geri geldi. ⚠️ **ADR-0051'in dersi ikinci kez kendini ödedi:** *ölçüt sayısal olarak sağlıklı görünüyordu (0,1733 > 0,10), **yalnız gözle okuma çürüttü**.*

---

<a id="61"></a>
## #61 — Dedektör onarıldı: B10 14/80 → 8/80, kütle %62,8 → %68,4 — ve düzeltme BİZİM LEHİMİZE

**2026-09-06 · hakem $0 · GPU $0** (yeniden puanlama tamamen deterministik) · Test `112 passed, 2 xfailed`

**Onarım.** `exact_reject`'in *"açılış hükmü yok"* dalı **11 satırla** değişti; `REJECT_RE`'ye **dokunulmadı**:
```python
# ÖNCE                          # SONRA
return REJECT_RE.search(c)      if hukum is None and REJECT_RE.search(_ilk_esasli_ibare(c)):
#      ↑ TÜM METİN                  return True     # örtük OLUMSUZ açılış hükmü
                                return REJECT_RE.search(_son_esasli_ibare(c))
```
⛔ **Elenen alternatif — karakter penceresi** (`c[:160]`): 13 vakanın 13'ünde çalışıyor **ama** çıpa `id=19`'da payı yalnız **22 karakter** ⇒ *bu hattın hata sınıfı sessiz yanlışlık; **o marj kabul edilemez**.* Ayrıca elendi: *"yalnız son ibareye bak"* (13 vakanın **5'ini ters yönde** kırıyor) · özne ayrımı (**semantik sınıflandırma**, tuzak 2.9).

**⭐ Gerçek B10 = 8/80 — 80 kalem GÖZLE okundu.**

| ölçüt | çekinme | coverage | **B10** | kütle |
| :--- | ---: | ---: | ---: | ---: |
| ⭐ **gözle okuma (80/80)** | **13/80** | 0,8375 | **8/80** | **%69,6** |
| onarılmış alet | 14/80 | **0,8250** | **9/80** | **%68,4** |
| ~~eski alet (yayımlanmış)~~ | ~~19/80~~ | ~~0,7625~~ | ~~14/80~~ | ~~%62,8~~ |

**Eski aletin 14 B10'unun 6'sı yanlış pozitifti.** 🎁 **Yanlış negatif YOK** — gözle okunan 13 çekinmenin 13'ünü eski alet de yakalamıştı. `recall@10` **üç ölçütte de aynı**: *erişime dokunulmadı, değişen yalnız davranış ekseni.*

**🚨 Düzeltmenin yönü BİZİM LEHİMİZE — ve asimetri ÖLÇÜLDÜ, varsayılmadı.** Kütle **+5,6 puan** yükseldi ve **rakip kolları hiç kıpırdamadı** (3.1 FL 10→10 · 3.5 FL 10→10 · `h2b_fl35_k4` 46→46). *Bu, bu repo'nun **en çok şüphelendiği desendir**, o yüzden ayrıca ölçüldü.*
⭐ **Asimetri meşru ve mekanizması net: hata BİZİM KENDİ CEVAP ŞABLONUMUZA özgüydü.** `raft_scrubbed` şablonu her cevapta *"diğer kaynaklar … içermemektedir"* diye **eleme gerekçesi** yazıyor; **Gemini yazmıyor (80'de 3)**. ⇒ ***Bozuk dedektör sistematik olarak yalnız bizi cezalandırıyordu — üstelik cezalandırdığı şey kendi eğitim şablonumuzun izi.***

**Rakip tablosu — sayılar, PARİTE İDDİASI DEĞİL.** 3.1 FL %61,7 · **BİZ %68,4** (~~%62,8~~) · BİZ gözle %69,6 · 3.5 FL %69,5.
⛔ ***"3.5 FL ile eşitlendik" cümlesi KURULMUYOR.*** Kalan açık **1,1 puan** ve **bu ekseni koruyan bir çözünürlük sınırı YOK** (*gürültü tabanı A1 makrosu içindir; kütle = coverage × A1 ve **coverage'ın varyansı o tabanda yok***). Söylenebilecek tek şey: 3.1 FL'ı geçme marjı **+1,0 → +6,7 p** genişledi, 3.5 FL açığı −6,7'den −1,1'e daraldı, **ve her ikisi de ALETİN düzeltilmesinden geldi, modelden değil.**

**🚨 Turun ön-kayıtlı hedefi EĞİTİMSİZ karşılandı.** Spec **8-11/80** yazmıştı; gözle okuma **8/80** ⇒ `τ_a` v2 **hiç eğitilmeden hedefin alt ucundayız.** Turun öncülü bu ölçümle büyük ölçüde çözülüyor: ***kayıp gerçekti ama büyüklüğünün %43'ü aletin kendisiydi.*** ⚠️ *Bu, aşırı-redin yok olduğu anlamına gelmez — 8/80 hâlâ 3.5 FL'ın 6/80'inin üstünde.*

**Yeniden puanlama — 82 dosya, $0.** `olcum-bi` (**resmî**) coverage 0,7625 → **0,8250** · B10 14 → **9** · kütle **%62,8 → %68,4**; `s2-harness-k10-etiketli` (ablasyon çıpası) → **%73,0**. `rejection_exact` **21 koşuda** düştü. 🎁 **`rejection_rate` (hakem) HİÇBİRİNDE değişmedi** — *pay hakemine dokunulmadığının **bağımsız kanıtı**.*
🚨 **`base_vs_tgta` işaret DEĞİŞTİRDİ (ikinci kez):** −0,0038 → **+0,0074**; `fl_vs_tgta` **bizim aleyhimize** büyüdü. 82 yedek `.ONCEKI-20260906` olarak yerinde.

**🚨🚨 ADR-0058'İN GEREKÇESİ TERSİNE DÖNDÜ — yeni, kapatılmamış bulgu.** *Onarım, ana protokolün **kendi seçim gerekçesini** çürüttü.*

| | eski (bozuk) alet | **onarılmış alet** |
| :--- | ---: | ---: |
| önsözlü — **resmî protokol** | %62,8 | **%68,4** |
| önsözsüz — **ablasyon** | %61,3 | **%73,0** |
| **Δ(önsöz)** | **+1,5 p** ✅ | **−4,6 p** 🔴 |

**Kıyas geçerli — doğrudan ham dosyalardan ölçüldü** (⚠️ iki koşuda da `KUNYE.json` **yok**, borç D-c ⇒ künyeye güvenilmedi): n 80↔80 · id kümesi **birebir** · **`context_shown` 80/80 BİREBİR AYNI** · `recall@10` aynı ⇒ **değişen TEK şey istem.**
**Diğer eksenler:** coverage önsözsüz **+7,5 p** · A1 önsözlü **+1,8 p** · A1·altın önsözlü +1,4 p · B10 önsözsüz **5/80 ↔ 9/80** · B1 önsözlü **5/80 ↔ 7/80** · katı kapı reddi önsözsüz 1 ↔ 3.
⭐ **Takas net ve iki yönlü:** önsöz modeli **daha seçici** yapıyor (A1↑, B1↓) ama **daha suskun** (coverage↓, B10↑). ***Bozuk alet suskunluğun bedelini GÖREMİYORDU, çünkü önsözsüz kolun cevaplarını red sayıyordu — ve o kol daha çok cevap ürettiği için daha çok yanlış pozitif alıyordu. Hatanın asimetrisi tam buradaydı.***
**⛔ Hüküm KURULMADI:** protokol değişikliği **yeni ADR + insan kararı** ister · Δ'yı koruyan **çözünürlük sınırı yok** · ADR-0058'in gerekçesi **yalnız kütle değildi** ve **A1 ile B1 hâlâ önsözün lehine**. **Yayımlanan sayı bu turda DEĞİŞTİRİLMEDİ.**

**Kapanmayan / şerhli kalemler.** 🟡 **1/80 uyuşmazlık (`id=32`)** — model açılışta reddedip **gövdede kendi reddini yalanlıyor** (#57/Ö2'nin **ayna vakası**); **Rule of Three gereği kapatılmadı** (ölçülen örnek: 1), sınır `xfail(strict=True)` ile çizildi · 🚨 **17 `a1_*.txt` bu onarımdan ÖNCE de bayattı** — 8'i pre-v3 dedektörün ürünü; *#57'nin kalibrasyonu `abst_*`'ı yeniden puanlamış ama `a1_*` artefaktlarını **atlamış*** ⇒ ***"aleti bir yerde düzeltmek yetmez" dersinin ÜÇÜNCÜ tekrarı.***
**🐞 Süreç hatası — kendi hatam, kayda geçiyor.** Belge commit'i ajanın **uçuş hâlindeki** değişikliklerini **süpürüp commit etti** (iki ajan paralel koşarken `git add -A`) ⇒ **kayıt yanıltıcıydı.** **Ders: paralel ajan koşarken `git add -A` yapılmaz.**

---

<a id="62"></a>
## #62 — Faz 0: ölçüm zinciri · aletin kusurları bulundu, kütle %68,4 → %80,1

**2026-09-06/07 · Harcanan ~$1,38 · EĞİTİM KOŞUSU: SIFIR** · Artefakt `tgta_v1` — **ağırlıklar hiç değişmedi**
> **Turun tek cümlesi:** *Modeli iyileştirmedik; **ölçtüğümüz şeyin ne olduğunu düzelttik** — ve dört ayrı kusur bulundukça sayı %68,4'ten %80,1'e çıktı.*

**Neden bu tur açıldı.** Kullanıcı ön-kabulü: *"3.5 Flash-Lite'e ancak yetişiyoruz, net farkla geçmeliydik."* Doğrulamak için **rakip ölçümünün künyesi açıldı ve ilk kusur oradan çıktı.**

**Bulgu 1 — kaybın yarısı erişim değil, SORU** ([ADR-0067](../adr/kararlar-0064-0085.md#adr-0067)). Kaçırılan 10 kalem gözle okundu: **5/10 soru altın maddeyi BELİRLEMİYOR**, 5/10 gerçek erişim hatası. En ağırı: İİK 31/a **gemi sicili** hakkındaydı, sorusu *"Mahkeme benim lehime bir karar verirse ne olur?"* ⇒ **belirsiz değil, neredeyse ilgisiz.** ⭐ Eşleşmeler tam metinle denetlendi ve **DOĞRU** çıktı ⇒ kusur **yer-gerçeğinde değil**, sorunun **bağlamının sökülmüş** olmasında.
DEV 13 + TEST 2 soru yeniden yazıldı (insan onaylı, 15/15) ⇒ `recall@10` **0,8750 → 0,9375**. ⚠️ **Bir kayıp geri ALINMADI (id 79)** — *geri almak, eval sorusunu **ölçülen sistemin lehine** ayarlamak olurdu.*

**Bulgu 2 — kusur BM25'te değil, FÜZYONDA** ([ADR-0068](../adr/kararlar-0064-0085.md#adr-0068)). **Dört kalemde bir kol altını 0. sırada bulmuştu**, RRF ikisini toplayınca ilk 10'un dışına itiyordu (`1/60 + 1/157 = 0,0231` < iki kolda 5. sıra `2/65 = 0,0308`) ⇒ ***"iki kolda vasat olmak, bir kolda mükemmel olmayı yeniyor."***
`RRF_K` **60 → 10**; **seçim gerekçesi PLATO, sivrilik değil.** ⭐ **Genelleme donmuş TEST'te, seçimden SONRA doğrulandı:** dört koşulun dördünde de yükseliyor ve kazanç TEST'te (**+2,5 p**) DEV'dekinin **iki katı**. `recall@10` **0,9375 → 0,9500** · kütle tavanı **%87,5 → %93,75**.

**Bulgu 3 — DEV ↔ TEST farkının %81'i BİLEŞİMDEN** ([ADR-0069](../adr/kararlar-0064-0085.md#adr-0069)). Erişim uzunlukta **U biçimli** (Q1 0,8000 · Q2/Q3 0,9333 · **Q4 0,6667**); en zor dilimde DEV'in payı **%12**, TEST'in **%50**. ⇒ ***v1 kabul testinin kütle tavanı ≈%75'tir, DEV'in %93,75'i değil. İki sayı aynı metrik değildir.*** Raporlama biçimi kabul testi **koşmadan önce** ön-kayıtlandı. 🆕 Yeni borç: **uzun madde chunk'lama** (*B9'dan ayrı: orada **bozuk** chunk, burada **doğru ama çok uzun** chunk*).

**Bulgu 4 — 🚨 üretim bütçesi rakiple EŞİT DEĞİLDİ, ve aleyhimizeydi** ([ADR-0070](../adr/kararlar-0064-0085.md#adr-0070)). Rakip **1536**, biz **1024**; **kod ADR-0043 §2'ye SADIKTI, kusur protokolün kendisindeydi.** 3.1 FL'de **36/80**, 3.5 FL'de **18/80** kalem 1024'ü fiilen aşıyor. 🚨 Ve bu **yayımlanmış bir hükmü çürüttü** (*"bizde ayrık bütçe var"*) — o dosyada **üstü çizilerek** damgalandı.
⚠️ **Neden bugün patladı:** önsöz kalkınca zorla kapatma **21/80 → 5/80** düştü ⇒ paylaşımlı bütçenin bedeli görünür oldu. ***S14 kararı kusuru yaratmadı, açığa çıkardı.*** Tetikleyen: F0.2 kesiklik kapısında düştü — **kapı doğru çalıştı**, hakem parası harcanmadan durdurdu; **kesiklik BELİRTİYDİ.**

**Bulgu 5 — dedektör İKİ kez yanıldı, iki farklı şablonda (`suskunluk_terazisi`).** **Bizim kolda alet ↔ göz farkı SIFIR** (önceki turda 14 ↔ 8 idi ⇒ **ADR-0061'in onarımı tuttu**). **Rakip kollarda — zorunlu kalibrasyon adımı**, 28 kalem okundu:

| kol | alet | temiz çekinme | çekinceli cevap | **açık yanlış pozitif** |
| :--- | ---: | ---: | ---: | ---: |
| BİZ | 4 | **4** | 0 | **0** |
| 3.1 FL | 8 | 5 | 0 | **3** |
| 3.5 FL | 9 | 5 | 2 | **2** |
| 3.5 Flash | 11 | 7 | 3 | **1** |

Örnek (3.1 FL id 38): *"**TCK 235'e göre** … cezalandırılır."* — altın maddeden **doğru cevap**, alet **çekinme saymış**. ⇒ ***Üstünlüğümüzün bir kısmı aletin eseriydi***; düzeltilmiş sayılar raporlandı. Alet + protokol birlikte **`suskunluk_terazisi`** adını aldı: **dedektör tek başına hüküm vermez, iki kefe gerekir.**

**Bulgu 6 — kapı maddesinin ÇIPASI YOKTU** ([ADR-0073](../adr/kararlar-0064-0085.md#adr-0073)).
**(a)** Madde *"M5 ≤ **bugünkü**"* diyordu; koşmadan önce sorulan tek soru — ***"bu sayıyı neyle kıyaslayacağım?"*** — maddeyi düşürdü: **`tgta_v1`'in M5'i hiçbir birimde hiç ölçülmemişti** (defterde merge öznesi **yoktu**) ⇒ madde **kendi kendine referans veriyordu.** **Yeni tuzak sınıfı (2.17):** *ön-kayıt kuralına uyan ama **çıpası olmayan** kapı maddesi — kurala uyduğu için denetimden geçiyor; ölçülemez olduğunu **kendisi söylemiyor**.*
**(b)** Geçerlilik kapısı **kaldı** (kesik 5/80 = %6,2, `EXIT=2`) ⭐ **hakem çağrılmadı** — *kapı, bozuk bir koşuya para harcanmasını **fiilen** engelledi.* Beş kalem gözle okundu ve **deterministik** bir dedektörle bağımsız sınandı; **ikisi aynı hükmü verdi** (*bu turda alet ↔ göz ilk kez **anlaştı***): bütçe kesilmesi 2 (id 27: düşünce 1536'nın **tamamını** yaktı, cevaba **3 karakter** kaldı) · 🚨 **yozlaşmış tekrar 3** (×21 · ×19 · ×82). **ADR-0040'ın reçetesi üç kalemde ölçülmüş biçimde ETKİSİZ** ⇒ ön-kayıtlı kural **kapsamadığı** bir kusur sınıfına çarptı.
**(c)** ⭐ **Ucuz kaldıraç ölçüldü: $0, hakem yok, deterministik hüküm.** *İnsan itirazı doğruydu ve benim çerçevem darcı: **"rejimi değiştirmek" pahalıdır, ama "kaldıracın işe yarayıp yaramadığını ölçmek" $0.*** ✅ **Kontrol kapısı 5/5 BAYT-BAYT.** kontrol **5/5 kesik, 3 döngü** ↔ **`dry` 0/5, 0** ↔ `repeat_penalty` 1/5, 0.
**DRY seçildi ve gerekçesi ALAN-ÖZGÜ:** `0,8 × 1,75^(n−2)` tekrarlanan **dizinin** uzunluğuyla üstel büyür ⇒ **2 token'a kadar tekrar serbest**; *hukuk metninde "madde", "kanun" ve kanun numaraları **meşru olarak** tekrarlar ve ceza almaz.* ⭐ **İki ceza da logit'i seçimden ÖNCE değiştirir ⇒ `temperature=0` ve determinizm korunur** (*#42'nin yarısını kurtaran `temp 0.6` bunu **bozardı***) — **ucuz kaldıraç, aynı zamanda metodolojik olarak temiz olan çıktı.**
**Kapsam yalnız M5 — tercih değil, teknik zorunluluk:** DRY bir `llama.cpp` örnekleyicisidir, **Gemini'ye uygulanamaz**; M5 rakip içermez ve base de yerel ⇒ **iki kola da eşit** uygulanabilir.
**🚨 Kabul edilen bedel — sayıdan ayrılamaz: DRY modeli DOĞRU yapmadı, AKICI yaptı.** Kör modda cevaplar artık tam ve akıcı — **ve yanlış** (İş K. 31 → *"35. ve 36. Maddeler"* · TBK 230 → *"6502 Sayılı Tüketici Kanunu"*). **M5'in ölçmek için var olduğu şey tam olarak budur.** ⇒ **DRY'li M5, DRY'siz M5 ile aynı birimde DEĞİLDİR.**
⚠️ Ayrıca ölçüldü: **yozlaşmış cevap çekinme sayılmaz** ⇒ coverage'ı yükseltir, A1'i düşürür; *döngü, anti-hedefi **olduğumuzdan iyi** gösterebilirdi.* **İki kolun aynı rejimde koşması bunu dengeliyor:** fark okunabilir, **mutlak değer damgasız yayımlanmaz.**

**Sonuç — madde (3):** BİZ ALET `cov 0,9500 · A1 0,4105 · kütle 0,3899` / GÖZ `1,0000 · 0,4057 · 0,4057`; base ALET `0,9750 · 0,4818 · 0,4697` / GÖZ `1,0000 · 0,4739 · 0,4739` ⇒ 🟢 **GEÇTİ** (ALET −7,98 p · GÖZ −6,82 p) — **ve hüküm dedektöre bağımlı değil**, ADR-0057'nin eşit sınavı burada **koruyucu** görev görüyor.
**Ve alet ÜÇÜNCÜ kez yanıldı — ilk kez kör modda: 6/6 yanlış pozitif.** *Altısı da hukuki bir **olumsuz hüküm** kuruyor **ve atıf yapıyor** — cevap veriyorlar, üstelik çoğu **yanlış** (base id 16: **"4711 Sayılı Türk Hakemlik Kanunu"** — var olmayan bir kanun).* Mekanizma: `REJECT_RE`'nin *"bulunmamaktadır"* ailesi hukuk metninde **iki iş görür**; **kör modda kaynak yoktur** ⇒ birinci okuma **tanımı gereği imkânsız.**
```
1  bizim şablon, önsözsüz   alet 14 → göz  8
2  Gemini şablonu, F0.4     alet 11 → göz  7
3  kör mod, iki kol         alet  6 → göz  0
```
**Üçünde de yön aynı: alet FAZLA RED sayıyor. Üçü de yalnız GÖZLE görüldü.** ⛔ Alet bugün **düzeltilmedi** — *kapının sayısı üretildikten sonra aleti değiştirmek ADR-0050'nin yasakladığı hareketin sınırındadır. **Doğru sıra: ölç → iki okumayı da raporla → sonraki turda, koşudan ÖNCE düzelt.***

**Sonuç — dört özne, eşit sınav, aynı birim (İLK KEZ):**

| eksen | **BİZ** | 3.1 FL | 3.5 FL | **3.5 Flash** |
| :--- | ---: | ---: | ---: | ---: |
| **kütle** (bağlayıcı: GÖZ-katı) | **0,8011** | 0,7058 | 0,7622 | **0,7425** |
| A1 · altın getirilen | **0,8902** | 0,7900 | 0,8449 | 0,8523 |
| aşırı-red | **4** | 8 | 9 | 11 |
| **uydurulmuş madde** | **0** | 1 | 4 | 4 |
| `recall@10` | 0,9500 | 0,9500 | 0,9500 | 0,9500 |

**`v1.0` kapısı madde (1): üç okumada da GEÇTİ** — en muhafazakârında **+5,86 p**. *Ağustos'ta aşırı-red rakibin **iki katıydı**; bugün **en güçlü eksenimiz**.*
**Diğer kapanan borçlar.** **F0.5 · `SOURCE_CLIP` 3500 → 12000** ($0,78): `k=10`'un paydasının **65'i k=4'ün önbelleğinden devralınmıştı**; şimdi **0**. ⚠️ *Tahmin $0,30'du; sapmanın sebebi **borcun kendisi** — eski koşuda hakem zaten çağrılmıyordu.* **F0.6 · VRAM** 3,09/3,70/5,76 GiB, ≤8 GB kapısı **128K'da bile** geçiliyor.

**⚠️ Kendi aleyhimize iki kayıt.** ① **8 isabetsizliğin 2'si benim yazdığım sorularda** — *durumu tarif ederken **komşu maddenin dilini** kullanmışım; **yanlılık koruması ters yönde işledi**.* Sorular **düzeltilmedi**. ② **B1 için otomatik vekil metrik YOK ve ölçüldü:** `faith<0,6` **4** · *"altın atıflarda yok"* **3** · **gözle tam tarama 8**.

**Ders.** ***Dört kusurun dördü de "hata vermeden yanlış sayı üreten" sınıftandı ve dördü de ancak GÖZLE OKUMA ya da KÜNYEYİ AÇIP OKUMA ile bulundu. Sayısal kapılar dördünü de geçirmişti.*** Yol boyunca **8 alet tuzağı** daha yakalandı.
