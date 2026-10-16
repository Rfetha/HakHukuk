# LLM bilgi damıtması (KD) taraması: HakHukuk için proje notu

> **Kaynak:** arXiv 2402.13116, *A Survey on Knowledge Distillation of Large Language Models* (Xu, Li, Tao, Shen, Cheng, Li, Xu, Tao, Zhou). TeX kaynağından okundu (`main.tex` + `latex/1-6`, tam metin). Şekiller ve özet tablo (`tab:my_label`) okunmadı. Başlık `\title{}` alanından doğrulandı.
> **Tür:** tarama (survey). Yeni deney veya sayı üretmez; yöntemleri sınıflar. Uygulamaların çoğu makalenin **taksonomisine** dayanır, ölçülmüş bir kazanca değil.
> **Not:** literatür özetidir; proje kararı değildir. Karar gerekirse ADR'ye ayrıca yazılır.
>
> *Yazım notu (ana oturum):* metni bir alt ajan üretti; alt ajanların dosya yazması araç tarafından engellendiği için ana oturum ajanın metnini olduğu gibi yazdı.

---

## TL;DR

- Makale, LLM çağında damıtmayı "öğretmenin **bilgisini çekme**" (Knowledge) ve "öğrenciye **enjekte etme**" (Distillation) diye ikiye ayırır (Bölüm 3). Kapalı öğretmenlerde pratik yol: öğretmen çıktısı üretilir, öğrenci SFT ile eğitilir. Veri artırma (DA) bu hattın motorudur (Bölüm 2.2).
- Bilgi çekmenin altı biçimi: **Labeling, Expansion, Data Curation, Feature, Feedback, Self-Knowledge** (Bölüm 3.1). HakHukuk'un madde → soru-cevap hattı, makalenin sınıflamasında **Labeling ile Data Curation arası** bir yerdedir: madde meta-bilgi/tohum, soru ve cevap öğretmen çıktısıdır (çıkarım).
- Projeyi en çok ilgilendiren uyarılar:
  - Öğrenci öğretmenin **üslubunu** taklit eder, olgusal doğruluğunu değil (Bölüm 4.1.1, 4.2.1).
  - Expansion'da veri **homojenleşir** ve öğretmen/tohum yanlılığını büyütür (Bölüm 3.1.2).
  - Öğrenci öğretmenin **güvenilirlik sorunlarını miras alır** (Bölüm 6).
  - Lisans için tek cümle var: sağlayıcı şartlarına uy, rakip ürün geliştirme kısıtı (Bölüm 7, dipnot).
- Makale şunları **kapsamaz**: modern akıl yürütme izi damıtması (R1 tarzı uzun iz), doğrulanabilir ödülle RL, dil bazlı (Türkçe) iz hizalaması, damıtmada değerlendirme metodolojisi, ayrıntılı lisans/etik analizi. Bu başlıklarda makaleye atıf yapılamaz.

---

## Ana katkılar

1. **Üç eksenli taksonomi** (Bölüm 2.3): algoritma (bilgi + damıtma), beceri (bağlam izleme, hizalama, ajan, NLP görevleri, çok kipli), dikey alan (hukuk, tıp, finans, bilim).
2. **Genel boru hattı** (Bölüm 2.4): hedef beceri/alanla öğretmeni yönlendir, tohum bilgi ver, öğretmen bilgi örnekleri üretsin, öğrenciyi bir öğrenme hedefiyle eğit. İki denklem: `D_kd = {parse(o,s) | o ~ p_T(o | I ⊕ s)}` ve `L = Σ_I L_I(D_kd_I; θ_S)`.
3. **DA ile KD'nin birleşimi** (Bölüm 2.2): geleneksel DA'dan (paraphrase, geri çeviri) farkı, alan/beceri hedefli, bağlam zengini veri üretmesidir.
4. **Altı bilgi çekme biçimi** formülleriyle (Bölüm 3.1) ve beş damıtma hedefi: SFT, diverjans, benzerlik, RL, sıralama eniyilemesi (Bölüm 3.2).
5. **Açık problemler** (Bölüm 6): veri seçimi ve ne kadar veri gerektiği, maliyet, çoklu öğretmen, daha zengin bilgi, felaket unutma, güvenilir damıtma, zayıftan güçlüye, öz-hizalama.

---

## Akılda tutulacak teknik ayrıntılar

**Bilgi çekme biçimleri (Bölüm 3.1)**

| biçim | tanım (makaleye göre) | proje ilişkisi (çıkarım) |
| :--- | :--- | :--- |
| Labeling (3.1.1) | girdi `x` hazır, öğretmen `y` etiketler; CoT/PoT açıklaması da etiket olabilir | gerçek madde + üretilen soru → cevap etiketi |
| Expansion (3.1.2) | az demodan ICL ile hem `x` hem `y` üretilir (Self-Instruct, Evol-Instruct) | tek madde başına çok soru üretimi; çeşitlilik riski |
| Data Curation (3.1.3) | meta-bilgiden (konu, belge) sıfırdan sentez; phi, UltraChat | kanun/madde kimliği = meta-bilgi |
| Feature (3.1.4) | logit/gizli durum; yalnız beyaz kutu öğretmen | kapalı öğretmende yok |
| Feedback (3.1.5) | öğrenci çıktısına öğretmen tercihi/düzeltmesi (RLAIF, UltraFeedback, PERsD) | tuzak/ret çiftleri ve hakem ayrımı |
| Self-Knowledge (3.1.6) | aynı model üretir, süzülür/puanlanır (Self-Instruct, LMSI, ReST, Self-Rewarding) | kendi örneklemesi / ret örneklemesi |

**Makalenin anlattığı süzme ve kalite örnekleri**

- Self-Instruct: üretilen talimatlardan tekrar/benzerleri eleme (Bölüm 4.1.1, Basic Instructions).
- Impossible Distillation: **entailment, uzunluk, çeşitlilik** süzgeçleri (Bölüm 3.1.6).
- LMSI: her soru için birden çok CoT yolu üret, **en tutarlı cevaba** giden yolları tut (Bölüm 3.1.6).
- ReST: *Grow* (örnekle) / *Improve* (puanlayıcıyla sırala, süz, çevrimdışı RL) döngüsü (Bölüm 3.1.6).
- SAIL: her getirilen pasajı ve doğru cevabı **entailment modeliyle** ilgili/ilgisiz diye etiketler, sonra öğretmenden cevap ister; öğrenci arama sonucundaki gürültüyü ayıklamayı öğrenir (Bölüm 4.1.3).
- Self-RAG: öğretmenden (GPT-4) küçük bir eleştirmene "getirme gerekli mi / sonuç iyi mi" **yansıma jetonları** damıtılır (Bölüm 4.1.3).
- Veri seçimi: AlpaGasus (ChatGPT puanı), Superfiltering (küçük modelle süzme), DEITA (karmaşıklık-kalite-çeşitlilik), MoDS (kalite-kapsama-gereklilik), LIMA'nın "1000 iyi örnek yeter" savı (Bölüm 4.1.1 ve Bölüm 6, "Further Data Selection"). Makale "ne kadar veri gerekir" sorusunu **çözülmemiş** diye işaretler.

**Düşünce biçimi (Bölüm 4.2.1)**

- Orca "explanation tuning": öğretmenden adım adım açıklama izleri; sistem mesajı ile iz zenginleştirilir. Orca 2: farklı görevlere farklı çözüm stratejisi öğretmek.
- SelFee / Reflection-Tuning: cevapla birlikte **revizyon zinciri** de hedef olur.
- Uyarı: öğrenci cevap üslubunu taklit eder, **akıl yürütme sürecini** değil (Orca atfıyla).

**Damıtma hedefi (Bölüm 3.2)**

- SFT (SeqKD) kapalı öğretmen için en basit ve en yaygın hedeftir (3.2.1).
- Diverjans: ileri KL "mod kapsayan" olup halüsinasyona itebilir, ters KL "mod arayan" olup çeşitliliği düşürür (3.2.2). Yalnız logit erişimi varken geçerlidir; kapalı öğretmende kullanılamaz.
- RL: önce öğretmen tercihlerinden ödül modeli, sonra KL kısıtlı PPO (3.2.3). DPO/RRHF/PRO: örnekleme gerektirmeyen, sabit tercih verisiyle sıralama eniyilemesi (3.2.4). Zephyr, dDPO'yu UltraFeedback üzerinde kullanır.

**Güvenilirlik ve unutma (Bölüm 6)**

- Öğrenci öğretmenin güvenilirlik sorunlarını miras alabilir; küçük açık modeller güvenilirlikte kapalı olanların gerisindedir (TrustLLM atfıyla).
- Felaket unutmaya karşı: tekrar (rehearsal), düzenlileştirme, aynı alandan zor talimat üretimi (Lion).
- Zayıftan güçlüye genelleme (Burns ve ark.): zayıf etiketle ince ayar zayıf denetçiden iyi olabilir, ama saf ince ayar yetmez. Superfiltering: küçük model (GPT-2) veri zorluğunu büyük modelle tutarlı sıralar.

**Hukuk alanı (Bölüm 5.1):** makale yalnız **Çince** hukuk modellerini anar (LawyerLLaMA, LawGPT, Fuzi): hukuk külliyatı üzerinde sürekli ön eğitim, ardından ChatGPT ile üretilmiş danışma/talimat verisi ve sınav soruları üzerinde ince ayar. Kalite kapısı, atıf doğrulaması veya Türk hukuku hakkında bir şey **yoktur**.

**Değerlendirici damıtması (Bölüm 4.4.5):** PandaLM, Prometheus, InstructScore, TigerScore, Auto-J. Bir öğretmenden (GPT-3.5/4) hakem davranışı damıtılıp küçük değerlendirici eğitilir. Hakem yanlılığı veya uyumu burada ele alınmaz.

---

## HakHukuk için somut uygulamalar

Her madde makale bölümüne bağlıdır. "Çıkarım" işaretli olanlar makalenin çerçevesinden bizim yaptığımız çıkarımdır; makaleye atfedilmemelidir.

### A. Sentetik soru/veri üretiminin kalite kapıları (eğitim verisi; Makale 1 ve ürün)

1. **Üretim biçimini adlandır ve kayda geçir.** Mevcut hat: madde (meta-bilgi) → soru → cevap → doğrulama. Makalenin formülüyle `x ~ p_T(x | I ⊕ m)`, `y ~ p_T(y | I ⊕ x)` (Data Curation, Bölüm 3.1.3). Madde metni cevabın bağlamına da girdiği için bu fiilen "temellendirilmiş Data Curation"dır (çıkarım). *Aşama: F0 kayıt, Makale 1 yöntem bölümü.*
2. **Süzgeç katmanlarını makalenin süzme örnekleriyle karşılaştır.** Elimizde uydurma-alıntı süzgeci ve öğretmen etiketi temizliği var. Makalenin süzgeçleri farklı eksenlerdedir: entailment (Impossible Distillation 3.1.6; SAIL 4.1.3), çeşitlilik/tekrar (Self-Instruct 4.1.1; DEITA, MoDS Bölüm 6), tutarlılık (LMSI 3.1.6). Çıkarım: mevcut süzgeç *sadakat* eksenini tutuyor; **çeşitlilik** ve **cevap soruyu karşılıyor mu** eksenleri ayrı kapı olarak ölçülmemiş olabilir. Kayıttan doğrula, eksikse ekle. *Aşama: F0 / veri denetimi.*
3. **Çeşitlilik denetimi (homojenleşme).** Makale: tek tohumdan çok üretimde veri benzeşir ve tohum yanlılığı büyür (3.1.2; Bölüm 6 "Further Data Selection"). Madde başına kaç soru üretildiğini, kanun dağılımının eğriliğini ve soru kalıplarının tekrarını raporla (kanun/madde uzunluğuyla katmanlı, ADR-0069 ile uyumlu). Makale ölçüt dayatmaz; ölçütü biz seçeriz.
4. **Ret/tuzak örnekleri için negatif bilgi kaynağı.** Makale, tercih çiftlerinin öğrencinin **kendi çıktısından** ya da kontrast istemlerle üretilebildiğini söyler (RLCD 3.1.6, Self-Play 3.1.6, Feedback 3.1.5, PERsD). Çıkarım: projedeki A1.7 dersi (`rejected` modele özgüdür) ile uyumlu; reddedilen taraf her temel modelden yeniden hasat edilmelidir. Makale bunu "model özgü" diye söylemez.
5. **Öğretmen-miras riski için ayrı denetim.** Makale Bölüm 6: öğrenci öğretmenin güvenilirlik sorunlarını miras alır. gpt-4o-mini etiketlerinde "uydurma alıntı" dışında *yanlış hukuki yorum* da olabilir. Kullanıcının okuyacağı küçük bir insan örneklemiyle yalnız alıntı doğruluğunu değil cevap doğruluğunu da ölç. *Aşama: eğitim verisi denetimi; Makale 1 sınırlılıklar.*
6. **Veri miktarı sorusu.** Makale "ne kadar veri" sorusunu çözümsüz bırakır ve LIMA'yı anar (Bölüm 6). Yeni veri üretmeden önce mevcut setin alt örneklem öğrenme eğrisi (%25/%50/%100) ucuz bir pilot olabilir. Bu makalenin önerdiği bir deney değil, açık sorudan çıkarımdır.

### B. Test sorusu üretimi (yeni ~200-225 soru; kullanıcı tek tek okuyacak)

7. **Üretici ile eğitim üreticisi ilişkisi.** Makale test üretimini ele almaz. KD'deki öğretmen yanlılığı (3.1.2, Bölüm 6) soru üretici modelin üslubunun teste sızacağı anlamına gelir (çıkarım). Üretici eğitim verisi üreticisiyle (gpt-4o-mini) aynıysa test soruları eğitim sorularıyla **biçimsel olarak benzeşir**. Yol haritasındaki "eğitim verisiyle örtüşme denetimi" yalnız madde/leksik değil, **soru kalıbı** düzeyinde de yapılmalı. Mümkünse test üreticisi farklı bir model/istem olsun (lisans notu için madde 13).
8. **Zorluk katmanı için Evol-Instruct fikri.** Makale (4.1.1 Complex Instructions) zorluk ve çeşitlilik boyunda talimat evrimini anlatır (WizardLM, 4 tur). Çıkarım: yeni test soruları madde uzunluğu katmanına ek olarak "tek madde / madde çifti / istisna içeren hüküm" gibi zorluk kademeleriyle üretilebilir. Test soruları eğitim setine geri sızdırılmamalıdır; makale bu ayrımı tartışmaz.
9. **Bağlayıcı kapı insandır.** Makalenin Selective Reflection-Tuning ve LMSI örnekleri otomatik kapılardır. Test için bağlayıcı kapı kullanıcının okumasıdır (ADR-0069 "kendi başına anlaşılır" kuralı). Otomatik kapılar yalnız okunacak havuzu daraltan **ön eleme** olabilir (entailment/belirsizlik işaretleri). Ön elemeyle atılan soruların bir kısmı da okunup eleme hatası ölçülmeli (çıkarım).

### C. Düşünce izi, hizalama, lisans (Makale 2, ürün)

10. **İz hedefi: Orca çerçevesi ne söyler, ne söylemez.** Makale 4.2.1: öğrenci yalnız cevabı taklit ederse akıl yürütmeyi öğrenmez; açıklama izleri ayrıca hedef olmalıdır. Makale izin **dilini** (Türkçe iz), iz-cevap tutarlılığını veya iz kalitesinin ölçümünü ele almaz. Makale 2'deki Türkçe iz hedefi için makaleye dayanılacak tek şey genel gerekçedir. Yöntem ve ölçüt başka kaynaktan gelmeli.
11. **İzleri kendi örneklemesinden alma seçeneği.** Self-Knowledge (3.1.6): LMSI (tutarlı cevaba giden izleri tut) ve ReST (Grow/Improve). STaR yalnız atıf listesinde geçer. Hepsi öğrencinin kendi izleri üzerinden süzme ve yeniden eğitme döngüsüdür. Çıkarım: Türkçe iz için kendi izlerimizi **kapalı modele göndermeden** (lisans yükü yok) yeniden örnekle; cevap ve atıf doğrulaması geçenleri ve Türkçe olanları tut; ödülü hakemsiz doğrulayıcıdan al (YAYIN_YOL_HARITASI §3.2 ile uyumlu). Makale bunu Türkçe için denemez; etki **ölçülmemiştir**. *Aşama: Makale 2 ön kayıt ADR'si, ödül terimi seçimi.*
12. **RL tarafı.** Makale yalnız öğretmen ödüllü RL anlatır: ödül modeli öğretmen tercihlerinden eğitilir ya da öğretmen doğrudan ödül verir (3.2.3). Bizim planımız, altın madde bilindiği için hakemsiz doğrulanabilir ödüldür; makalenin kapsamı dışındadır ve makale iki yolu kıyaslamaz. DPO/ORPO türü sıralama eniyilemesinin RL'den kararlı olduğu savı (3.2.4) ORPO tercihimizle uyumlu bir arka plandır, kanıt değil.
13. **Lisans/şart disiplini.** Makale tek cümle söyler (Bölüm 7, dipnot): ChatGPT/Llama gibi modellerden damıtırken sağlayıcı şartlarına uy, **rakip ürün geliştirme kısıtı** dahil (OpenAI iş şartları atfıyla). Başka lisans/etik analizi yoktur. Çıkarımlar:
    - Eğitim verisinin kaynağı gerçek mevzuat metni olduğundan çıktı verisini ayrıştırmak kolaydır. Ancak öğretmen çıktısı (gpt-4o-mini soru-cevap) sağlayıcı şartlarına tabidir; bu veriyi Apache-2.0 altında dağıtmanın şartlarla uyumu şart metni düzeyinde ayrıca doğrulanmalıdır.
    - "Gemini/Claude çıktısıyla öğrenci eğitilmez" kuralı geçerliyse Makale 2 için öğretmen olarak yalnız açık lisanslı modeller ya da öğrencinin kendisi (Self-Knowledge) kalır.
    - Kapalı modeller **hakem** olarak (puanlama) kullanılabilir. Hakem çıktısından eğitim sinyali (ödül/tercih) türetmek damıtma sayılabilir; sınır önceden yazılmalıdır.

    *Aşama: F0 ADR, Makale 1 etik bölümü.*

---

## Aktarılamayanlar / çekinceler

- **Tarih ve kapsam.** Tarama Şubat 2024'te yazıldı (arXiv kaynağındaki en son sürüm Ekim 2024'e uzanır). Uzun akıl yürütme izi damıtması, doğrulanabilir ödülle RL (GRPO vb.), Qwen3/Gemma 4 sınıfı küçük modeller ve düşünme kanalı hakkında hiçbir şey yoktur. Makale 2'nin Türkçe iz hedefi için makale doğrudan kanıt değildir.
- **Hukuk bölümü zayıf.** Bölüm 5.1 yalnız üç Çince modeli iki paragrafta anlatır; kalite kapısı, atıf doğrulama, ret/çekinme yoktur. HakHukuk'un asıl sorunları (aşırı ret, isabetsiz atıf, temellendirme-ret çatışması) taramada karşılanmaz. Bunlar için `summary_citation_grounding.md`, `summary_saullm.md` ve proje ADR'leri esas alınmalı.
- **Damıtmada değerlendirme yok.** "Öğrenci öğretmene ne kadar yaklaştı", "öğretmen hatası ne kadar geçti", hakem yanlılığı ya da veri sızıntısı ölçütü yoktur; yalnız değerlendirici damıtması (4.4.5) ve veri seçimi (Bölüm 6) vardır. Öğretmen hatalarının geçişi için tek dayanak Bölüm 6'daki genel uyarı ve Bölüm 4.1.1'deki "üslup taklit edilir, olgusal doğruluk değil" gözlemidir; nicel sonuç yok.
- **Anti-hedefle gerilim.** Makale damıtmayı kapsama/yeteneği artıran bir araç olarak sunar. Projede kapsam artışı tek başına hedef değildir: düz SFT çekinmeyi yok etti (gemma4-12b-dersler A2.1). Makale çekinme/ret becerisinin damıtılmasını ele almaz.
- **Kapalı öğretmen varsayımı.** Taramanın merkezindeki GPT-4/Gemini'den damıtma, "yalnız açık kaynak ve lisansı uygun veri" kuralımızla doğrudan uyuşmaz. Bu özetteki öneriler bu yüzden *öğretmen* yerine *süzgeç, kalite kapısı ve kendi örnekleme* kısımlarına yaslanır.
- **Yalnız atıf düzeyindeki içerik.** STaR, ReST, LMSI, Impossible Distillation, SAIL, Self-RAG, DEITA, MoDS, Superfiltering taramada birkaç cümleyle anlatılır; ayrıntılı koşullar ve sonuçlar için asıl makaleler okunmalı (okunmadı).
- **Okunmayan kısımlar.** Bölüm 4.3 (ajan), 4.4.1-4.4.4 ve 4.4.6 (NLU, NLG, IR, öneri, kod), 4.5 (çok kipli) ve 5.2-5.5 (tıp, finans, bilim) projeye uzak olduğu için ayrıntılı özetlenmedi; yalnız başlıkları tarandı.
