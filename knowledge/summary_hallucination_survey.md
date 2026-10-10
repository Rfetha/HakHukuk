# LLM halüsinasyonu taraması (arXiv 2311.05232) — proje notu

> **Literatür özeti.** Kaynak: TeX kaynağı (`~/.cache/arxiv-papers/2311.05232/`), tüm içerik bölümleri okundu (§1-§8; `.cls` ve `.bib` atlandı). Aşağıdaki "HakHukuk için" önerileri **makalenin değil, bu notun yorumudur**. Her biri dayandığı makale bölümüne bağlanmıştır. Makalede olmayan şey makaleye atfedilmemiştir. Bölüm numaraları TeX bölüm sırasından çıkarılmıştır, derlenmiş PDF ile karşılaştırılmamıştır. Proje kararları `docs/adr/` ve `docs/YAYIN_YOL_HARITASI.md` ile birlikte okunmalıdır.
>
> *Yazım notu (ana oturum):* metni bir alt ajan üretti; alt ajanların dosya yazması araç tarafından engellendiği için ana oturum ajanın metnini olduğu gibi yazdı.

**Gerçek başlık (kaynaktan):** *A Survey on Hallucination in Large Language Models: Principles, Taxonomy, Challenges, and Open Questions* (`main.tex`). Bu bir **derleme (survey)** makalesidir: deney yok, ölçülmüş sayı yok. Bulgular alıntılanan çalışmalara aittir ve burada ikinci elden aktarılır.

---

## TL;DR

- Halüsinasyon iki ana sınıfa ayrılır: **olgusallık** (çıktı gerçek dünyayla çelişiyor ya da doğrulanamıyor) ve **sadakat** (çıktı kullanıcı girdisine, bağlama ya da kendi mantığına uymuyor). Sadakat üçe bölünür: talimat, **bağlam**, mantık tutarsızlığı (§1, §2.3).
- HakHukuk'un çalışma alanı sadakat tarafıdır: kaynak maddeler bağlamda verilir, soru "model bağlama sadık mı"dır. Olgusal doğruluk (parametrik bilgi) M5'te anti-hedef olarak ayrıca izlenir.
- RAG'de halüsinasyonun iki kaynağı vardır: **getirme hatası** ve **üretim darboğazı** (§6). Bizim "isabetsiz atıf" kusurumuz makalenin sınıflarından hiçbirine **birebir** oturmaz. En yakın akrabaları gürültülü bağlam, bağlam kullanımı ve kaynak atfıdır (§6.2).
- Tespit: iddia düzeyinde ayrıştırma (FActScore), NLI sınıflandırıcıları, QA-tabanlı yöntemler, belirsizlik ve LLM-hakem (§4.1). Makale her birinin zayıf noktasını da sayar. Bu, "hakem + gözle okuma" tercihimizi destekler.
- Azaltma: veri, eğitim ve çıkarım nedenlerine göre ayrılır. SFT'nin modele **reddetmeyi öğretmeden tamamlamayı dayatması** halüsinasyon nedeni olarak açıkça sayılır (§3.2.2). Bu, M2/M3 çekinme eğitimimizin literatür gerekçesidir.

## Ana katkılar

1. **Yeni taksonomi** (§2.3, Tablo 1). Eski intrinsic/extrinsic ayrımı (kaynakla çelişki / kaynaktan doğrulanamama) LLM çağına uyarlanıp yeniden kurulur:
   - Olgusallık: *olgusal çelişki* (varlık hatası, ilişki hatası) ve *olgusal uydurma* (doğrulanamaz, aşırı iddia).
   - Sadakat: *talimat*, *bağlam* ve *mantık* tutarsızlığı.
2. **Nedenler**, üç aşamada (§3):
   - Veri: yanlış bilgi, taklitçi yanlışlık, bilgi sınırı (uzun kuyruk, güncellik), yetersiz hizalama verisi.
   - Eğitim: ön eğitim, SFT, RLHF ve dalkavukluk.
   - Çıkarım: örnekleme rastgeleliği, aşırı güven, softmax darboğazı, akıl yürütme hatası.
3. **Tespit** (§4.1) ve **kıyas kümeleri** (§4.2), olgusallık ve sadakat için ayrı ayrı.
4. **Nedene bağlı azaltma** (§5): veri filtreleme, model düzenleme ve RAG; mimari ve hizalama; olgusal ve sadakatli kod çözme.
5. **RAG'e özgü halüsinasyon analizi** (§6). Projeye en yakın bölümdür.
6. Gelecek yönler: görsel-dil modelleri ve **bilgi sınırının** anlaşılması (§7).

## Teknik ayrıntılar

**Tespit (§4.1)**
- *Olgusal tespit:* iki adım vardır, iddia çıkarma ve iddia doğrulama. Doğrulama dış getirme ile (FActScore: üretimi atomik olgulara böler, desteklenen oranı hesaplar) ya da iç kontrolle (CoVe, p(True)) yapılır. Makale, parametrik bilgiye dayanan iç kontrolün güvenilmez olduğunu not eder.
- *Belirsizlik:* iç durum (token olasılığı, entropi) ve davranış (çoklu örnekleme tutarlılığı, dolaylı sorgu, LMvLM çapraz sorgu) olarak ikiye ayrılır.
- *Sadakat tespiti, beş grup:*
  - olgu-tabanlı (n-gram, varlık, ilişki üçlüsü)
  - sınıflandırıcı (NLI). Girdi ayrıntı düzeyi uyumsuzluğu nedeniyle cümle birimine bölüp skorları toplamak gibi uyarlamalar vardır.
  - QA-tabanlı
  - belirsizlik-tabanlı (entropi, uzunluğa normalize log-olasılık)
  - **LLM-hakem** (ikili ya da Likert; doğrudan, CoT, bağlam-içi örnekli ya da açıklamalı)
- n-gram metriklerinin ince sapmaları ayırt edemediği açıkça yazılmıştır (§4.1.2).

**Kıyas kümeleri (§4.2, tablo).** Ağırlıkla İngilizce ve Çince, genel alandır.
- Değerlendirme tarafı: PopQA, Head-to-Tail, RealTimeQA, FreshQA (yanlış önerme soruları dahil), Med-HALT, TruthfulQA, HalluQA, HaluEval 2.0.
- Tespit tarafı: SelfCheckGPT-Wikibio, HaluEval, FELM, BAMBOO, ScreenEval, PHD, RealHall, SAC3, LSum.
- **Hukuk ya da Türkçe küme yok.**

**Nedenler (§3)**
- SFT: model bilgi sınırının ötesindeki yanıtları uydurmaya zorlanır. Geleneksel SFT belirsizliği ifade ettirmez. Yeni olgusal bilgiye aşırı uyum uydurmayı artırır (§3.2.2, §3.1.3).
- RLHF: dalkavukluk. İnsan ve tercih modeli dalkavuk yanıtı doğrulardan fazla tercih edebilir (§3.2.3).
- Çıkarım: örnekleme sıcaklığı halüsinasyon riskiyle ilişkilidir. Aşırı güven, yerel bağlama odaklanıp kaynak bağlamı ihmal eder (§3.3.1-3.3.2).

**RAG (§6)**
- *Getirme hatası:*
  - Kullanıcı sorusu: kör getirme (getirme gerektirmeyen soruda getirme yanıltır), belirsiz soru, karmaşık soru (sorgu ayrıştırma).
  - Kaynak: LLM üretimi içerik yanlılığı, güvenilirlik farkındalıklı üretim.
  - Getirici: parçalama ayrıntı düzeyi, alan dışı gömme. RAPTOR, önerme-düzeyi ve anlamsal parçalama anılır.
- *Üretim darboğazı, bağlam farkındalığı:*
  - **Gürültülü bağlam:** rastgele getirmede belirgin düşüş görülür. NLI ile süzmek ilgili parçaları da atar. İlgisiz bağlamı görmezden gelmeyi **eğitim verisine ilgisiz bağlam katarak** öğretmek daha etkilidir. Chain-of-Note önce okuma notu üretir, yetersizse "bilmiyorum" der.
  - **Bağlam çatışması:** parametrik ile bağlamsal bilgi çatışır. Karşı-olgusal veriyle ince ayar bağlama güveni artırır.
  - **Bağlam kullanımı:** ortada kaybolma.
- *Bağlamsal hizalama:*
  - **Kaynak atfı:** planla-sonra-üret; üret-sonra-yansıt (yansıtma jetonları; AGREE: atıflı iddia üret, desteksizleri işaretle); öz-atıf (saliency).
  - **Sadakatli kod çözme:** bağlam-farkındalıklı kod çözme (CAD); sadakat tespit edicisiyle ışın aramasında geri izleme.
- Bağlam-farkındalıklı kod çözme gibi yöntemlerde sadakat artışı çeşitlilik pahasınadır (§5.3.2 tartışması).

## HakHukuk için somut uygulamalar

Eşleme kuralı: önce makalenin ne dediği, sonra bizim için çıkarım. Aşama adları `YAYIN_YOL_HARITASI.md`'ye göredir (Makale 1 = Checkpoint 1, Makale 2 = Checkpoint 2).

### 1. İsabetsiz atıfın literatürdeki karşılığı ve ölçülmesi

- **Makalede doğrudan bir "gerçek ama yanlış kaynağa dayanma" sınıfı yoktur.** En yakın olanlar:
  - (a) Bağlam tutarsızlığı (§2.3.2). Bu sınıf çelişkiyi anlatır; bizdeki gibi *bağlamla çelişmeyen, yalnız sorunun cevabı olmayan* bir dayanmayı anlatmaz.
  - (b) Gürültülü bağlamın üreticiyi yanıltması (§6.2.1).
  - (c) Kaynak atfı (§6.2.2).

  Dolayısıyla isabetsiz atıf için literatürde hazır metrik beklememek gerekir. ADR-0066'nın "otomatik vekil yok" tespiti bu açıdan tutarlıdır.
- **Terim önerisi (yorum):** makale diliyle isabetsiz atıf, *getirilen bağlamın üreticide yanlış seçilmesidir*. Bağlamda altın madde ve ilgisiz ama gerçek madde birlikte varken seçim hatası yapılır. Kayıtlarda "gürültülü bağlama dayanma" olarak da etiketlenebilir (§6.2.1 ile köprü).
- **Ölçüm seçenekleri ve neden yetmedikleri:**
  - Atıf doğrulama (deterministik): uydurma maddeyi yakalar, isabetsizliği yakalamaz (ADR-0066'nın ölçtüğü şey).
  - NLI/sınıflandırıcı (§4.1.2): "iddia kaynaktan çıkar mı" sorusunu ölçer. Kaynak gerçekse ve iddiayı destekliyorsa isabetsiz atıfı **geçirir**. Aynı yapısal kör nokta, yüksek `faithfulness` ile kaçırılan kalemlerde ölçüldü. NLI'yı vekil olarak denemek ancak *soru-madde uygunluğu* sorusuna çevrilirse anlamlıdır. Bu makalede önerilmiyor, kendi tasarımımız olurdu.
  - QA-tabanlı sadakat (§4.1.2): kaynaktan ve cevaptan çıkarılan cevapları karşılaştırır. Soruya göre değil iddiaya göre çalışır, aynı kör nokta geçerlidir.
  - **Kullanılabilir fikir:** altın madde biliniyorsa (eğitim ve DEV kümesi) *altın-madde kapsama* ölçülebilir. ADR-0066 bunun da tek başına yetmediğini ölçtü, çünkü cevap altın maddeyi başka yerde anabiliyor. Bu nedenle makale değil kendi ölçümümüz kazanır: **gözle tarama bağlayıcı kalır.**
- **Aşama:** Makale 1 ölçümü (raporlama) ve Makale 2 ödülü (aşağıda).

### 2. Sadakat puanlaması (iddia düzeyi)

- Makale FActScore'u olgusal tarafta (§4.1.1), LLM-hakemi sadakat tarafında (§4.1.2) sayar. Bizim iddia düzeyindeki hakem puanlamamız bu ikisini birleştirir: *iddiaları böl, her birini yalnız verilen bağlama karşı doğrula* (dış bilgiye karşı değil).
- **Yorum:** FActScore'un bilgi kaynağı Wikipedia'dır. Bizde "bilgi kaynağı", o sorunun bağlamındaki maddelerdir. Bu, olgusallık ölçüsünü sadakat ölçüsüne çevirir. Projede zaten böyledir. Makale bu uyarlamayı anlatmaz.
- Makalenin uyarısı (§4.1.1): iç kontrol (modelin kendi bilgisiyle doğrulaması) güvenilmezdir. Hakem ailesi dışlama ve iki aileli panel (ADR-0074) bu riske karşı doğru yöndedir.
- **Aşama:** Makale 1 hakem paneli. Yeni iş yok, yalnız literatür dayanağı var: "n-gram ve varlık örtüşmesi sadakat için yetersiz" (§4.1.2) cümlesi, regex tabanlı ölçümleri neden hakemle tamamladığımızı savunmakta kullanılabilir.

### 3. Çekinme (M2/M2b/M3)

- Makale: SFT modele tamamlamayı öğretir, reddetmeyi ya da belirsizliği ifade etmeyi öğretmez (§3.2.2). Bilgi sınırı hizalaması (yetenek hizasızlığı) için "sınırlı araştırma var" der (§5.2.2). RAG tarafında Chain-of-Note, getirme yetersizse "bilmiyorum" demeyi öğretir (§6.2.1). Bu, M2b (yalnız ilgisiz kaynak varken susma) için en doğrudan literatür dayanağıdır.
- **Önemli çekince:** makale tersi riski (aşırı çekinme, bizim 4/80 gereksiz red) **ölçmez ve tartışmaz**. Yalnız ilgisiz bağlama sağlamlığı ile "bilmiyorum" yeteneğini birlikte anar. Kütle ile çekinme arasındaki dengeyi bizim ölçümlerimiz yönetir.
- **Yorum:** "ilgisiz bağlamı eğitim verisine katarak görmezden gelmeyi öğret" fikri (§6.2.1), M2b eğitim örneklerini nasıl kuracağımızla örtüşür. Örneklerde ilgisiz ama gerçek madde bulunmalı; hedef çekinme ya da doğru maddeyi seçmek olmalı.
- **Aşama:** Makale 1 (SFT verisi bileşimi) ve Makale 2 (M2b ödülü).

### 4. Makale 2 ödülü (GRPO)

- Makale RL/GRPO'dan **söz etmez**. RLHF'yi yalnız dalkavukluk nedeni olarak ele alır (§3.2.3, §5.2.2). Bu yüzden ödül tasarımı için makaleden doğrudan dayanak yoktur. Aşağıdakiler, makaledeki tespit ve azaltma fikirlerinin ödül terimine çevrilmiş **yorumudur**.
- **Dalkavukluk ve ödül kırma uyarısı (§3.2.3, §5.2.2):** tercih sinyali doğruluğu değil insan onayını ödüllendirirse model hoşa gideni öğrenir. Bizim ödülümüz doğrulanabilir (altın madde bilinir) ve hakemsizdir. Bu, makalenin tarif ettiği riskten kaçınır. Ödül tablosundaki "altın bağlamdayken susma: −" satırı, çekinmeyi ödül kırmasına (her şeye "bilmiyorum") karşı korur. Bu dengenin bozulmaması için ablasyon planındaki "çekinme terimsiz" kolu değerlidir.
- **Olası ek terim (makaleden esinli, kanıtsız):** kaynak atfı yöntemleri (§6.2.2) cevabı atfa bağlar: önce destekleyici maddeyi belirle, sonra cevapla. Eğitim sonrası çıktı biçimi "madde seç, sonra cevapla" ise ödül, seçilen maddenin altın olmasını ödüllendirebilir. Bu bir tasarım seçeneğidir. Ürün yoluna (`servis.answer`) ve "ürün yolu = ölçüm yolu" kuralını bozmamalıdır.
- **Kod çözme yöntemleri (CAD, sadakat kod çözmesi; §5.3.2, §6.2.2) bu aşamaya uygun değil.** Ürün yolu ile ölçüm yolu eşit olmalı ve llama.cpp sunucu bayrakları bir rejim kilididir. Kod çözme müdahalesi iki yolu da değiştirir. Yalnız literatür notu olarak kalmalıdır.
- **Aşama:** Makale 2, ödül ön-kaydından önce (ADR'de katsayılarla).

### 5. Düşünce hizalaması (yol haritası §3.3)

- Makale §5.3.2'de "mantıksal tutarlılık" altında şunları anar: CoT ara gerekçelerinin modelin gerçek davranışını yansıtmaması, bağlam, CoT ve cevap arasındaki nedensel ilişki, çıkarımsal köprüleme ve DPO tabanlı karşı-olgusal tercih hedefi.
- **Eşleme:** yol haritasındaki "iz ile karar tutarlı mı" ölçüsü bu yazının doğrudan karşılığıdır. Mantık tutarsızlığı sınıfı (§2.3.3) buna ad verir. Makale Türkçe iz için bir şey söylemez.
- **Aşama:** Makale 2 ölçüm ve ödül ek terimi. Çıkarım tarafında ilgisi sınırlıdır.

### 6. Küçük, düşük maliyetli notlar

- **Kıyas kümesi boşluğu:** §4.2 tablosunda hukuk ve Türkçe yok. HakHukuk'un M-modları (M1-M5) bu boşluğa yerleşir. Makalede "yanlış önerme" (FreshQA) ve "yanıtlanamaz soru" (§7.2) tasarımları var. M2b tuzaklarını bu çerçeveye bağlayarak savunmak mümkündür.
- **Getirici:** §6.1.3'teki parçalama ayrıntı düzeyi uyarısı (kaba parça dikkat dağıtır, ince parça bağlamsız kalır) madde-birimli, 900 karakter kırpmalı rejimimizle ilgilidir. Rejim kilitlidir, değiştirilmeyecek; Sınırlar bölümünde anılacak bir nottur.
- **Güncellik:** §3.1.2'deki, güncel bilgiyi modele değil RAG'e bırakma yaklaşımı CLAUDE.md'deki "güncellik kitaplıkta" ilkesiyle uyumludur.

## Aktarılamayanlar / çekinceler

- **Derleme, deney değil.** Hiçbir sayı bu makaleden alıntılanamaz. Alıntılanan çalışmaların sonuçları ikinci elden aktarılmıştır. Yayında atıf yaparken özgün çalışmalara gidilmelidir. Bu notta çalışma adları yalnız metindeki anılışlarıdır (atıf anahtarları süzüldü, `custom.bib` ile eşlenmedi).
- **Tarih:** arXiv kaynağı Kasım 2023 çıkışlıdır ve sonraki revizyonlarla genişletilmiştir (RAG bölümü 2024 çalışmalarını da anar). En güncel RAG-halüsinasyon ve hakem-tabanlı değerlendirme yazını burada **yoktur**.
- **Eksik konular:** RL/GRPO ve doğrulanabilir ödül, küçük (4B) modeller, hukuk alanı, Türkçe, aşırı çekinme maliyeti, atıf düzeyi (iddia-madde eşleşmesi) doğruluğu. Bu alanlar için makaleden dayanak yoktur.
- **Tespit yöntemlerinin çoğu rejimimize doğrudan taşınamaz.** Belirsizlik tabanlı yöntemler (token olasılığı, çoklu örnekleme) sabit tohum ve bütçeli düşünce rejiminde yeni maliyet ve gürültü getirir. Ölçüm gürültü tabanı (~0,3 A1 puanı) altındaki farklar yorumlanamaz.
- **Taksonomi uyarısı:** "olgusal çelişki/uydurma" ile bizim "uydurulmuş madde" (0/114) kavramı örtüşür, ama bizim ölçümümüz bağlama göre doğrulama yapar. Makalenin olgusallık tespiti dış dünya bilgisine göre yapılır. İki terim aynı şeyi ölçmez. Yayında ayrı tanımlanmalıdır.
