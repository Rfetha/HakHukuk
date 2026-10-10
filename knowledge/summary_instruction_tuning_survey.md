# Instruction Tuning for Large Language Models: A Survey (arXiv 2308.10792)

> **LİTERATÜR ÖZETİ.** Kaynak makalenin bulguları geçerlidir. Bunlardan çıkan **proje kararları** `docs/adr/` ve `docs/YAYIN_YOL_HARITASI.md` içinde yaşar ve değişebilir. Bu belge karar değil, girdidir.
>
> *Yazım notu (ana oturum):* metni bir alt ajan üretti; alt ajanların dosya yazması araç tarafından engellendiği için ana oturum ajanın metnini olduğu gibi yazdı.

**Okundu:** 2026-10-10 · TeX kaynak (`main.tex`, sürüm 6, son güncelleme 11 Ağu 2025) · Yazarlar: Zhang, Dong, Li, Zhang, Sun, Wang, Li, Hu, Zhang, Wu, Wang · ACL biçimi.

**Önemli çekince:** Bu bir **derleme (survey)** makalesidir. Kendi deneyi yoktur, sayılar atıf verdiği çalışmalardan gelir. Karışım oranları, unutma (catastrophic forgetting), replay, çekinme/halüsinasyon eğitimi, model birleştirme, ORPO ve RAFT hakkında neredeyse hiçbir şey söylemez (kaynakta bu terimler arandı, yok). Aşağıdaki uygulamalar bu yüzden kısıtlı ve dürüst tutuldu. Makalede olmayan bir şey makaleye atfedilmedi.

## TL;DR

Talimat ayarı (IT, makalede SFT ile eş anlamlı) modeli (talimat, çıktı) çiftleri üzerinde denetimli eğitmektir. Veri üç yoldan gelir: insan yapımı, öğretmen modelden damıtma, modelin kendini geliştirmesi (Bölüm 3). Projeye en değerli iki mesaj:

1. SFT çoğunlukla **biçim/stil** öğretir. Destek verilmeyen görevlerde kazanç yoktur ya da gerileme olabilir (Bölüm 8.8, 9.2).
2. RLHF ve DPO hattı pratikte hep bir **SFT aşamasıyla başlar** (Bölüm 9.1).

Değerlendirme kısmı (Bölüm 8) genel amaçlı kıyaslara (MMLU, AlpacaEval, MT-Bench) odaklıdır ve HakHukuk'un ölçüm hattıyla doğrudan örtüşmez.

## Ana katkılar

- **Yöntem (Bölüm 2):** Örnek = talimat + isteğe bağlı girdi + çıktı. Kurma yolları: mevcut etiketli veri kümelerini şablonla dönüştürmek (Flan, P3) ya da LLM ile çıktı üretmek (Self-Instruct, InstructWild). Eğitim, çıktı belirteçleri üzerinde standart denetimli kayıptır.
- **Veri sınıflaması (Bölüm 3):**
  - İnsan yapımı: Natural Instructions (193K örnek), Dolly (15K), OpenAssistant, LIMA (1K).
  - Damıtma: Alpaca (52K), WizardLM/Evol-Instruct, Orca, Baize.
  - Kendini geliştirme: Self-Instruct (52K), SPIN, instruction back-translation (502K).
  - Akıl yürütme kümeleri: PRM800K, MathGenie ve benzerleri.
- **Modeller (Bölüm 4), çok-modlu (Bölüm 5) ve alana özgü uygulamalar (Bölüm 6;** tıp, kod, aritmetik dahil).
- **Verimli ince ayar (Bölüm 7):** LoRA, QLoRA (NF4), LOMO, HINT, delta-tuning.
- **Değerlendirme, analiz, eleştiri (Bölüm 8)** ve SFT'nin RLHF/DPO/istem mühendisliği karşısındaki rolü (Bölüm 9).

## Teknik ayrıntılar

### Veri kurma ve kalite

- **Self-Instruct (Bölüm 3.3):**
  - 175 elle yazılmış tohum kullanılır.
  - Havuzdan 8 tohumla az-örnekli istem hazırlanır.
  - Çıktı-önce / girdi-önce ayrımı yapılır.
  - Son adım kural ya da modelle süzmedir.
  - Makale uyarır: güçlü bir temel model yoksa döngü modelin kendi sınırına kilitlenir, önyargı ve hataları büyütebilir.
- **Instruction back-translation (Bölüm 3.3.2):** Gerçek metinden talimat türetilir, ardından değerlendirme modeliyle puanlanıp süzülür. 502K örnek üretilmiştir.
- **MathGenie (Bölüm 3.4.3) ve PRM800K (Bölüm 3.4.1):** Doğrulamaya dayalı süzme uygulanır. Yalnız doğrulanan çözümler tutulur. Doğrulanabilir alanlarda kalite kapısı örneğidir.
- **LIMA (Bölüm 3.1, 8.6):**
  - 1.000 özenle seçilmiş örnek kullanır (%75 topluluk Q&A, %20 yazarlar, %5 SuperNI).
  - Gerekçesi "yüzeysel hizalama hipotezi"dir: bilgi ön eğitimde edinilir, hizalama yalnız biçimi öğretir.
- **Wang vd. (Bölüm 8.7):**
  - Tek bir en iyi SFT kümesi yoktur. Kümeleri elle birleştirmek en iyi genel başarımı verdi.
  - Küçük modeller ve yüksek kaliteli tabanlar SFT'den en çok yararlanır.
  - Karışım oranı ayrıntısı makalede yoktur.
- **Gupta vd. (Bölüm 8.5):**
  - 119 SuperNI görevinde çok-görevli (MTL) ayarda SOTA'ya ulaşmak için hedef eğitim verisinin yalnız %6'sı yetti. Tek-görev ayarda oran %25'tir.
  - Yalnız T5 ölçeğinde denendi. Makale büyük LLM'de denenmediğini kendisi söyler.

### Eleştiri ve sınırlar

- **Gudibande vd. (Bölüm 8.8):**
  - Öğretmen çıktısıyla ince ayar, destek verilen görevlerde büyük kazanç sağlar. Verilmeyenlerde kazanç yoktur ya da düşüş görülür.
  - Model üslubu (akıcı, kendinden emin, yapılandırılmış) taklit eder. Bu, "genel yetenek" yanılsaması yaratır.
  - Öneri: taklit yerine temel model ve talimat kalitesini iyileştirmek.
- **Kung vd. (Bölüm 9.2):**
  - Anlamsal içeriği silinmiş görev tanımlarıyla ve yanlış girdi-çıktı eşlemeli örneklerle eğitilen modeller, orijinaline yakın başarım verdi.
  - Sonraki çalışmalar (LIMA, Lin vd.) benzer sonuca vardı.
  - Kazancın büyük kısmı çıktı biçiminde ustalaşmaktan ve "bilinçli tahminden" gelebilir.
- **Halüsinasyon:** InstructGPT ve Claude bölümleri (Bölüm 4.1, 4.6) "daha az halüsinasyon" gibi insan değerlendirme eksenlerini sayar. Ayrıntılı bir halüsinasyon-azaltma tarifi yoktur.

### Hizalama yöntemleriyle ilişki (Bölüm 9)

- **RLHF:** SFT, ödül modeli, PPO aşamalarından oluşur. Pahalıdır, kararsızdır, ödül istismarı ve "alignment tax" riski taşır. Ham taban modelden RL zor olduğu için SFT ile başlanır (Bölüm 9.1.1).
- **DPO:** Ödül modelsiz çalışır, tercih çiftleriyle eğitilir. PPO'dan basit ve kararlıdır (Bölüm 9.1.2).
  - Sınırları: tercih verisi kalitesine bağımlıdır, dağılım kaymasında zayıftır, örtük ödül dağılım-dışı çıktılara yanlılık yaratabilir.
  - SFT'li bir modelden başlamak sonucu iyileştirir. OpenAI rehberi SFT'yi DPO'dan önce önerir.
- **İstem mühendisliği (URIAL vb., Bölüm 9.1.3):** Yüzeysel uyuma yeter, yeni bilgi veya beceri ekleyemez. Yeni bilgi için ağırlık güncellemesi gerekir.
- **SFT'nin sürekliliği (Bölüm 9.1.4):** Son paragrafta "talimat kalıntıları" (eski bir modelin farkını yeni tabana eklemek) gibi melez hilelerden kısaca söz edilir. Bunlar mevcut ayarlanmış bir kaynak modele bağımlıdır. Ayrıntı verilmez, ham TIES ile ilişkilendirilemez.

### PEFT (Bölüm 7)

- **LoRA:** `W = W0 + BA`, düşük rank. GPT-3'te eğitilebilir parametre 10.000x, bellek 3x azalır.
- **QLoRA:** NF4 + çift niceleme + sayfalı optimizatör. Makale iddiasına göre 65B model tek 48 GB GPU'da, 16-bit tam ince ayara göre kayıpsız eğitilir.
- Makale rank, alfa, hedef modül seçimi, LoRA'da unutma ya da birden fazla adaptörün birleştirilmesi hakkında bilgi vermez.

### Değerlendirme (Bölüm 8)

- **Kapalı uçlu (Bölüm 8.1):** MMLU, MATH, GSM8K, BBH, HumanEval, IFEval.
- **Hakem-LLM (Bölüm 8.3):** AlpacaEval, uzunluk denetimli AlpacaEval, MT-Bench, WildBench.
  - Uzunluk denetimi, Chatbot Arena ile Spearman uyumunu 0,94'ten 0,98'e çıkarır.
  - MT-Bench'te GPT-4 ile insan uyumu %80'in üzerindedir.
- Makale hakem-LLM'in **uzunluk yanlılığını** açıkça anar. Kendi-ailesini-kayırma (self-preference) ya da çok-aileli hakem paneli konusu geçmez.

## HakHukuk için somut uygulamalar

Bağlam: iki LoRA kolu.

- **tau_g:** RAFT biçimli SFT, 17.323 satır.
- **tau_a:** ORPO çekinme, 726 çift + 145 temellendirme tekrar satırı.

Makale 1 (`docs/YAYIN_YOL_HARITASI.md`) bunları ham TIES birleştirme, birlikte eğitim ve ardışık eğitim olarak karşılaştırır. Her öneri bir makale bölümüne bağlıdır. **(Dolaylı)** işareti, makalenin yalnız genel bir ilke verdiği ve HakHukuk'a uyarlamanın bizim çıkarımımız olduğu anlamına gelir.

### 1. Birlikte-eğitim kolunun tasarımı (F0 kod ve Modal pilotu, F1 DEV ayarı)

- **SFT sonra tercih sırası.** Makale, RLHF ve DPO hattının SFT ile başladığını ve DPO'dan önce SFT'nin sonucu iyileştirdiğini aktarır (Bölüm 9.1.2 ve 9.1.4). Bu, **ardışık kolun** (SFT sonra ORPO) literatürdeki standart sıra olduğunu gösterir ve Makale 1'de makul bir referans nokta sağlar.
  - Makale **ORPO'dan ve tek koşuda SFT+tercih eğitiminden** söz etmez.
  - Birlikte-eğitim kolunun gerekçesi bu makaleden türetilemez. **(Dolaylı)**
- **İki kaybı ayrı izlemek.** Makalenin çerçevesinde SFT, çıktı belirteçleri üzerinde denetimli kayıptır (Bölüm 2.2). Tercih kaybı ayrı bir mekanizmadır (Bölüm 9.1.2). Birlikte-eğitim kodunda her adımda SFT kaybını ve tercih kaybını ayrı günlüğe yazmak, F1'deki karışım ayarını yorumlanabilir kılar. Bu bir uygulama önerisidir, makale söylemez. **(Dolaylı)**

### 2. Karışım oranı yapılandırmaları (F1, DEV)

- Makale oran önermez. İlgili tek bulgu, kümeleri birleştirmenin en iyi genel başarımı verdiğidir (Bölüm 8.7, Wang vd.). Bu bulgu, "SFT satırları + ORPO çiftleri" karışımının tek sabit oranla bırakılmayıp DEV'de birden fazla oranla denenmesi için zayıf bir destektir. Hangi oran, hangi aralık sorusuna makale veri vermez.
- **Öneri (makaleden bağımsız, bu bulguyla tutarlı):** F1'deki "ikişer yapılandırma" bütçesinde bir yapılandırmayı SFT ağırlıklı, diğerini çekinme ağırlıklı seçmek. Örneğin ikincisinde 145 tekrar satırı ve 726 çift artırılır.
  - Hangi eksenin ayarlandığı DEV'de raporlanır.
  - Değerler DEV'de kararlaştırılır, burada sabitlenmez. **(Dolaylı)**

### 3. Unutma ve replay

- Makalede **unutma, replay ve çok-görevli karışımda çatışma** yoktur. Bu konudaki literatür taraması, F0'daki "birleştirme ve birlikte eğitim" taramasına ayrıca eklenmelidir. Bu makale o boşluğu doldurmaz.
- Dolaylı bir bağ: Gudibande vd. (Bölüm 8.8), destek verilmeyen görevlerde gerileme bildirir. Emekli 12B hattındaki "düz SFT çekinmeyi sıfırlamıştı (0,741 → 0,000)" bulgusu bununla kalitatif olarak uyumludur, çünkü çekinme SFT kümesinde desteklenmeyen bir davranıştır.
  - Bu bir benzetmedir. Makale çekinmeyi ölçmedi. **(Dolaylı)**
- Aynı çerçeve, birlikte-eğitim akışında çekinme örneklerinin (145 temellendirme tekrarı gibi) sürekli temsil edilmesinin neden önemli olabileceğini açıklar. Makale replay'in işe yaradığını göstermez. **(Dolaylı)**

### 4. tau_g tarifi ve veri kalitesi (F0 yeniden ölçüm, F1)

- **Yüzeysel hizalama uyarısı (Bölüm 9.2) tau_g için doğrudan ilgilidir.**
  - tau_g'nin cevap biçimi (çıkarım, birebir alıntı, sonuç + atıf) güçlü bir biçim kalıbıdır.
  - Kung vd. ve LIMA bulguları, bir modelin bu kalıbı içeriği anlamadan alabileceğini söyler.
  - Önlem makaleden değil projenin kendi ilkesinden gelir ("sayıyı değil maddeleri gözle oku"): alıntının gerçekten altın maddede geçtiği, projede mevcut **deterministik atıf doğrulamasıyla** ölçülmeli.
  - Makale bunu önermez, yalnız riski adlandırır. **(Dolaylı)**
- **Süzme kalıbı.** MathGenie ve PRM800K (Bölüm 3.4) "yalnız doğrulanan örnek kalır" kalıbını gösterir. RAFT satırlarında birebir alıntının altın maddede geçtiğini otomatik doğrulayıp tutmayanları atmak bunun hukuk karşılığıdır. Veri hazırlığı bunu zaten yapıyorsa yeni değildir, kayıttan teyit edilmeli. **(Dolaylı)**
- **Kalite mi nicelik mi.** LIMA (1K örnek, Bölüm 8.6) ve Wang vd. (Bölüm 8.7) "az ama özenli" yönünü destekler. Bunlar genel sohbet ayarıdır.
  - 17.323 satırlık tau_g'nin özenle süzülmüş 1-3K'lık bir alt kümesiyle bir DEV kolu çalıştırmak, boyut/kalite sorusuna kendi verimizle cevap verir.
  - Makale bunun hukukta işe yarayacağını göstermez. **(Dolaylı)**
- **Kendi-kendine üretilen veride risk (Bölüm 3.3, 8.8).** RAFT cevapları güçlü bir LLM ile üretildiyse damıtma uyarıları (taklit yanılsaması) geçerlidir. RAFT çıktılarının kaynağı ve süzme prosedürü künyede kayıtlı olmalı. **(Dolaylı)**

### 5. Değerlendirme (F0 yeniden ölçüm, F3 son ölçüm)

- **Hakem yanlılığı.** Makale uzunluk yanlılığını ve uzunluk denetimini gösterir (Bölüm 8.3). Cevap biçimi uzun bir tau_g kolu ile çekinen kısa bir tau_a kolunu hakemle karşılaştırırken cevap uzunluğu ayrı raporlanmalı ya da denetlenmeli. Projenin çok katmanlı yargıç savunmasında uzunluk eksenini açıkça adlandırmak makaleyle tutarlıdır. **(Dolaylı)**
- **Genel yetenek koruma ölçüsü.** Makale kapalı uçlu genel kıyasları listeler (MMLU, IFEval vb.; Bölüm 8.1). Küçük bir genel kıyas, birlikte-eğitim kolunda "genel yeteneği bozdu mu" sigortası olarak düşünülebilir. Bu kıyaslar ürün iddiası değil sigortadır. M5 anti-hedefi korunur. Makale bunu önermez. **(Dolaylı)**

## Aktarılamayanlar / çekinceler

- **Derleme, deney değil.** Tüm sayılar atıf verilen çalışmalardandır, HakHukuk'un kendi ölçümünün yerini tutmaz. Hiçbir sayı kayda "bu makale ölçtü" diye geçirilmemeli. Asıl kaynağa (Gudibande, Kung, Wang, Gupta) inilmeli.
- **Ölçek farkı.** Atıf verilen çalışmaların çoğu 7B-65B LLaMA sınıfında, İngilizce genel sohbet ayarındadır. Gudibande 1,5B-13B aralığını kapsar, yine de İngilizce genel görevlerdir. HakHukuk ise 4B, hukuk RAG bağlamı, Türkçedir.
- **Konu dışı kalanlar.** Makalede yok: karışım oranı, unutma/replay, çekinme/halüsinasyon eğitimi, ORPO, RAFT, task-vector/TIES birleştirme, birden fazla LoRA adaptörünün birlikte yönetimi, Türkçe ya da hukuk alanı. Bu başlıklar için başka kaynak gerekir (F0 literatür taraması).
- **Hukuk alanı.** Alana özgü bölüm tıp, kod ve aritmetiği örnekler (Bölüm 6). Hukuk örneği yoktur. ChatDoctor tıbbi örneği "ince ayar + dış bilgi erişimi" birleşimini anar (Bölüm 6.4). Bu RAG ve SFT yönüne benzer bir gerekçedir, ama tek paragraflık bir tanıtımdır ve kanıt değildir.
- **Yüzeysel hizalama çerçevesi.** LIMA hipotezi "bilgi ön eğitimde, SFT biçimi öğretir" der. Projenin "güncellik kütüphanede, modelin kafasında değil" ilkesi de buna paraleldir. Bu tutarlılık makalenin hukuk için doğru olduğunu **kanıtlamaz**.
- **Sürüm notu.** Makale sürüm 6 (Ağustos 2025) olarak okundu. Sonraki sürümlerde bölüm numaraları kayabilir. Numaralar bu kaynaktaki sıraya göredir: 1 Giriş, 2 Yöntem, 3 Veri, 4 Modeller, 5 Çok-modlu, 6 Alan, 7 Verimli ayar, 8 Değerlendirme/Analiz, 9 SFT'nin rolü.
