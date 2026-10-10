# A Survey on LLM-as-a-Judge (arXiv 2411.15594) — proje notu

> **Ne:** Gu ve diğ., *A Survey on LLM-as-a-Judge*, arXiv:2411.15594 **v6 (19 Ekim 2025)**, cs.CL.
> Makale 1'in ölçüm tasarımı (`docs/YAYIN_YOL_HARITASI.md` §2.5) için okundu, 2026-10-10.
>
> **Okuma yöntemi ve sınırı (önemli):** TeX kaynağı (`https://arxiv.org/src/2411.15594`)
> indirilemedi: kabuktaki ağ erişimi kum havuzunda kapalıydı, kum havuzu dışında çalıştırma izni de
> reddedildi. Metin arXiv'in aynı TeX'ten ürettiği **HTML sürümünden** (`arxiv.org/html/2411.15594`,
> v6, ~294 bin karakter) bir getirme aracıyla, bölüm bölüm soru sorularak okundu. Araç metni
> kelimesi kelimesine vermedi, **özetledi**. Sayısal tablolar (Tablo 2, 3, 4) sayı sayı alındı; Tablo
> 4'ün `majority@5` satırı HTML çıkarımında bozuk geldi ve aşağıda kullanılmadı. Kilit iddialar ikinci
> bir sorguyla ayrıca doğrulandı (bölüm numarası ve kısa ifade ile). TeX'ten yeniden doğrulamak için:
> `curl -L -o ~/.cache/arxiv-papers/2411.15594.tar.gz https://arxiv.org/src/2411.15594`.
>
> **Gösterim:** `S§x.y` = survey'in bölümü · `YYH §x.y` = `docs/YAYIN_YOL_HARITASI.md` bölümü.
> "Bizim çıkarımımız" yazan her şey survey'de **yoktur**; survey'e atfedilmez.
>
> *Yazım notu (ana oturum):* metni bir alt ajan üretti; alt ajanların dosya yazması araç tarafından
> engellendiği için ana oturum ajanın metnini olduğu gibi yazdı. Ajan yol haritasının 2026-10-10 tarihli
> **ilk** sürümünü okudu; metindeki YYH atıflarının güncel karşılıkları: eski §4 → §2.5 (eski §4.3 → §2.5.3,
> §4.4 → §2.5.4, §4.5 → §2.5.5) · eski §5 (takvim, F-satırları) → §2.6 · eski §3.4 (dondurma) → §2.3
> "Dondurma" · eski §3.6 kalem 2 → §2.6 F0 · K4 → §2.5.2 · K8 → §2.5.4 · K15 → §3.2.

---

## 1. TL;DR

LLM-as-a-Judge'ı bir değerlendirme **süreci** olarak tanımlayan (`ℰ ← P_LLM(x ⊕ C)`) ve tartışmanın
merkezine **güvenilirliği** koyan (`ℛ ← f_R(P_LLM, x, C)`: tutarlılık, dayanıklılık, insanla uyum)
geniş bir derleme. Kullanım (istem biçimleri, model seçimi, son işleme), iyileştirme (istem tasarımı,
ince ayar, çoklu kaynak birleştirme), hakemin kendisinin değerlendirilmesi (insan uyumu, önyargılar,
saldırılara dayanıklılık) ve küçük bir deney içerir. Deneyin ana mesajı: en iyi hakemler bile insan
etiketiyle yalnız **%50-62** uyuşuyor; "açıklama iste", "kendini doğrula", "ortalama al",
"en iyisini seç" gibi popüler stratejiler çoğunlukla **işe yaramıyor ya da zarar veriyor**; çoklu
model oylaması bileşimine çok duyarlı.

## 2. Ana katkılar

- Biçimsel tanım ve güvenilirlik odaklı çerçeve: dört soru — ne, nasıl kullanılır, nasıl iyileştirilir,
  nasıl değerlendirilir (S§1, S§2 girişi).
- Kullanım taksonomisi: istem biçimleri (puan · Evet/Hayır · ikili karşılaştırma · çoktan seçmeli),
  genel ↔ ince ayarlı hakem, son işleme (belirteç çıkarımı · logit normalizasyonu · cümle seçimi),
  değerlendirme hattı (model · veri · ajan · akıl yürütme) ve dört adımlı "Quick Practice" (S§2).
- İyileştirme stratejileri taksonomisi (S§3): görev anlayışı, çıktı biçimi standardı, uzman ince
  ayar, geri bildirimle yineleme, çoklu kaynak birleştirme, doğrudan çıktı optimizasyonu.
- Önyargı taksonomisi: göreve bağlı olmayan (çeşitlilik, kültür, öz-yüceltme) ve yargıya özgü (konum,
  merhamet solması, üslup, uzunluk, somutluk) (S§4.2); saldırılara dayanıklılık (S§4.3).
- Küçük bir meta-değerlendirme deneyi: LLMEval2 (2.553 örnek, insan etiketli, ikili karşılaştırma) +
  EvalBiasBench (80 örnek, altı önyargı türü), 10 hakem, 6 strateji (S§4.4, Tablo 2-4).
- Meta-değerlendirmenin yeniden düşünülmesi (S§4.5), açık sorunlar (S§6), gelecek işler (S§7), alan
  uygulamaları arasında hukuk (S§5.2.2).

## 3. Akılda tutulacak teknik ayrıntılar

### 3.1 Tanım

- `ℰ ← P_LLM(x ⊕ C)`: `x` girdi, `C` bağlam (çoğunlukla istem şablonu), `⊕` birleştirme işleci, `ℰ`
  puan / seçim / etiket / cümle olabilir (S§2).
- Temel tanım güvenilirliği garanti etmez → `ℛ ← f_R(...)`: `f_R` bir kısıtlar ve doğrulama
  yöntemleri kümesidir; güvenilirlik "ek doğrulama, kalibrasyon ve standardizasyon adımlarıyla"
  sağlanır (S§2). Survey'in "kalibrasyon" kelimesini kullandığı yerler: bu tanım, Wang ve diğ.
  (2024c)'nin konum-takası kalibrasyonu (S§3.1.1), TrustJudge'ın beklenen puanı (S§3.3.2).

### 3.2 Puanlama biçimleri (S§2.1)

| biçim | ayrıntı | survey'in örnekleri |
| :--- | :--- | :--- |
| puan (pointwise) | ayrık (1-3, 1-5, 1-10) ya da sürekli (0-1, 0-100); kriter bazlı Likert | Bai ve diğ. 2023 (dört boyut 1-3 + genel 1-5) · Zhu ve diğ. 2023 · Xiong ve diğ. 2024 |
| Evet/Hayır | iki sabit cevap; geri besleme döngülerinde (Reflexion) ve yeterlilik kontrolünde | Shinn ve diğ. 2023 · Sun ve diğ. 2023c (getirilen bilginin yeterliliği) |
| ikili (pairwise) | iki seçenek · üç seçenek (+ beraberlik) · dört seçenek (+ "ikisi de iyi" / "ikisi de kötü"); kazanma/beraberlik/kaybetme sayımı; listeye genişleme (listwise) | PandaLM (Wang ve diğ. 2023d) · Qin ve diğ. 2024 · Liu ve diğ. 2024b |
| çoktan seçmeli | en uygun seçeneği seçme; "ilk üçünden daha nadir" | kaynak verilmemiş |

- Girdi tasarımı: tür (metin/görüntü), biçim (tek tek · ikili · toplu), istemdeki konum. Toplu ↔ tek
  değerlendirmenin artı/eksisi **yazılmamış**.
- İkili lehine iki iddia: Liu ve diğ. (2024b) ikili ortamda insanla uyumun puanlamadan yüksek olduğunu
  bildirir; Zheng ve diğ. (2023b) ve Liusie ve diğ. (2024) ikili yöntemlerde konum tutarlılığının daha
  iyi olduğunu söyler (S§2.1.3). PARIS (Liu ve diğ. 2024b) puanlamayı ikili sıralamaya çevirir (S§3.1.1).
- S§4.4.2'deki "ikili, noktasaldan daha güvenilir" hükmü doğrudan bir ikili↔noktasal deneyden değil,
  `majority@5` ↔ `mean@5` karşılaştırmasından çıkarılmıştır (zayıf kanıt).
- Biçimlere genel çekinceler: küçük istem değişikliğinde çıktı oynaması, puanlarda değerlendiriciler
  arası tutarsızlık, Evet/Hayır ve çoktan seçmelide belirsizlik, konum ve uzunluk yanlılığı (S§2.1).

### 3.3 Model seçimi (S§2.2)

- Genel hakem (GPT-4 sınıfı) ya da ince ayarlı hakem: PandaLM (Wang ve diğ. 2023d), JudgeLM (Zhu ve
  diğ. 2023), Auto-J (Li ve diğ. 2023b), Prometheus (Kim ve diğ. 2023).
- İnce ayarlı hakemler kendi test kümelerinde iyi, dışında zayıf genelleşir; eğitim verisinin
  önyargılarını devralır (S§2.2.2, S§3.2.1). Ticari hakemler kara kutu ve **sürüme bağımlı**, bu da
  yeniden üretilebilirliği bozar (S§6.1).

### 3.4 Son işleme (S§2.3)

- **Belirteç çıkarımı** (S§2.3.1): kurala dayalı çıkarım "doğası gereği kırılgan"; biçim değişkenliği
  ayrıştırmayı bozar. Kısıtlı çözümleme (DOMINO, XGrammar, SGLang) biçimi zorlar ama dağılımı bozabilir,
  kaliteyi düşürebilir, mühendislik ve çıkarım maliyeti getirir.
- **Logit normalizasyonu** (S§2.3.2): "Evet" belirtecinin olasılığından [0,1] sürekli puan;
  etkinliği istem tasarımına ve belirteçleştirme tutarlılığına çok bağlı.
- Bütün son işleme yöntemleri saldırgan girdilere açık (S§2.3.3). Hakem sayı yerine metin üretirse
  otomatik hat kırılır (S§6.2 "brittleness of scoring mechanisms").

### 3.5 Hızlı uygulama (S§2.5)

Dört aşama, bu sırayla: (1) **düşünme** — amaç, neyin ölçüleceği, insanların bunu nasıl
değerlendirdiği, güvenilir örnek vakalar; (2) **istem tasarımı** — puanlama boyutları, göreli
karşılaştırmayı tercih etme, iyi örnekler; (3) **model seçimi** — güçlü akıl yürütme ve talimat izleme,
önyargıların hesaba katılması; (4) **standart süreç ve son işleme** — yapılandırılmış çıktı (kutulu
cevap, sayı, Evet/Hayır). Baştan sona yineleme, yeniden test ve "açık güvenilirlik metrikleri" önerilir.
İnsanla doğrulama bu dört adım içinde ayrı bir adım olarak **yazılmamıştır**; S§4.1'de ele alınır.

### 3.6 İyileştirme stratejileri (S§3)

**İstem (S§3.1).**
- Az örnekli istem: FActScore (Min ve diğ. 2023), SALAD-Bench, GPTScore.
- Değerlendirme adımlarını ayrıştırma (CoT): G-Eval (Liu ve diğ. 2023b), DHP, SocREval (Sokratik).
- Ölçütleri ayrıştırma: Branch-Solve-Merge (Saha ve diğ. 2024) alt ölçütleri paralel değerlendirip
  birleştirir; HD-Eval hiyerarşik ayrıştırma; Hu ve diğ. (2024) 11 ölçütlü hiyerarşi. Hedef:
  değerlendiriciler arası tutarsızlık ve ölçüt karışması. Bedeli: her alt görev için ayrı istem ve
  birleştirme adımı.
- Konum yanlılığına karşı içerik takası/karıştırma: Wang ve diğ. (2024c) takas edip ortalar; Auto-J ve
  JudgeLM karıştırır; PandaLM takasta çelişen sonucu "beraberlik" sayar.
- Çıktı biçimi (S§3.1.2): form doldurma ("X: Y"), JSON (LLM-EVAL), gerekçeli puan (CLAIR), adım adım
  açıklama (FLEUR).

**Yetenek (S§3.2).** Uzman ince ayar (PandaLM, JudgeLM'in "reference support / reference drop" verisi,
OffsetBias'ın uzunluk-somutluk önyargısını azaltan çiftleri, CritiqueLLM) ve geri bildirimle yineleme:
INSTRUCTSCORE, **JADE** (Zhang ve diğ. 2023c: insanlar hakem kararlarını düzeltir, en çok düzeltilen
örnekler az örnekli istemin örneklerine eklenir), Think-J.

**Çoklu kaynak birleştirme (S§3.3.1).**
- Çoklu koşu: tekrarlı puanların ortalaması (Sottana ve diğ. 2023); 10 koşunun ortalaması ve standart
  sapması (PsychoBench); ölçütlü ve ölçütsüz eleştirilerin birleşimi (Auto-J).
- Çoklu model: üç LLM'le oylama (CPAD), merkezsiz akran incelemesi (Bai ve diğ. 2023), eşiği aşan puan
  çatışmasını çoğunluk oyuyla çözme (EvalMORAAL).
- **Basamaklı seçici değerlendirme** (Jung ve diğ. 2024): güvene göre küçük hakemden büyüğe
  yükseltme; değerlendirmelerin çoğu küçük modelde kalır, maliyet düşer.
- Kalabalık temelli karşılaştırma (Zhang ve diğ. 2025b).
- Bu bölümde hakem tartışması (debate) **yok**; ChatEval yalnız S§5.1.1'de, metin üretimi
  uygulamalarında anılır. Farklı ailelerden jüri (PoLL) ve hakem ağırlıklandırma **yok**.

**Doğrudan çıktı optimizasyonu (S§3.3.2).** FLEUR: rakam belirteçlerinin olasılığıyla puan
yumuşatma; TrustJudge (Wang ve diğ. 2025a): ayrık puan olasılıklarından sürekli beklenen puan; öz
doğrulama: hakeme kararından ne kadar emin olduğu sorulur, geçenler tutulur (TrueTeacher). İlk ikisi
belirteç olasılığına erişim ister. Survey bunların etkinliğinin "daha fazla doğrulama" gerektirdiğini
yazar.

### 3.7 Önyargılar (S§4.2)

| önyargı | tanım (survey) | survey'deki azaltma |
| :--- | :--- | :--- |
| çeşitlilik (S§4.2.1) | demografik gruplara karşı; kalıp yargıya uyan cevaba yüksek puan | yok |
| kültür (S§4.2.1) | başka kültürün ifadesini yanlış okuma, bölgesel dil varyantlarını tanımama | yok |
| öz-yüceltme (S§4.2.1) | hakemin kendi ürettiğini tercih etmesi (erişimde "source bias") | aynı modeli hakem yapmamak — survey'e göre "only a stopgap" |
| konum (S§4.2.2) | istemdeki konuma göre tercih; ChatGPT hakemken Vicuna-13B yalnız ikinci sıraya konunca kazanır (Wang ve diğ. 2024c) | metrikler: Position Consistency, Preference Fairness (Shi ve diğ. 2024), Conflict Rate (Wang ve diğ. 2024c); S§4.4.2 takas ve çok turlu çoğunluk oyu önerir |
| merhamet solması (S§4.2.2) | model adı görününce puanın kayması ("gpt-4" etiketi) | "anonim değerlendirmenin gerekliliği" |
| üslup / duygu (S§4.2.2) | görsel olarak çekici metin (emoji), belli duygu tonu | yok |
| uzunluk (S§4.2.2) | çoğunlukla uzun cevabı tercih | tespit: cevabı uzatarak yeniden yazma; ama uzatma akıcılığı ve üslubu da değiştirir, eş kaliteli örnek zor |
| somutluk / otorite / atıf (S§4.2.2) | otoriter kaynak, sayı, terim içeren cevabı tercih; ayrıntının doğruluğunu ihmal etmek halüsinasyonu teşvik eder (Agrawal ve diğ. 2023) | yok |

Survey bu bölümde "bandwagon", "distraction", "fallacy-oversight", "refinement-aware" adlarını
**kullanmaz** (çoğunluk iddiası S§4.3'te saldırı olarak geçer).

### 3.8 Saldırılara dayanıklılık (S§4.3)

Öğrenilmiş şişirme ifadeleri (Raina ve diğ.) · kesinlik/belirsizlik ifadelerine duyarlılık (EMBER, Lee
ve diğ.) · girdiden bağımsız sabit cevabın yüksek kazanma oranı (Zheng ve diğ. 2024a) · `:` ya da
"Thought process:" gibi açılışların hakemi olumlu karara itmesi (Zhao ve diğ. 2025) · "%90'ı bunu
daha iyi buluyor" türü çoğunluk iddiaları · istemdeki ilgisiz cümleler. Şaşkınlık (perplexity) tabanlı
savunmalar yalnız sınırlı saldırı türünü yakalar; sorun açık.

### 3.9 Meta-değerlendirme

**Metrikler (S§4.1).** Yüzde uyum `Σ 𝕀(S_llm = S_human) / |𝒟|` · Cohen κ · Spearman · hakemi bir
sınıflandırıcı sayıp insan etiketine karşı precision/recall. **Hiçbir metrik için eşik verilmez.**
Bölüm, hakemin insan yargısıyla uyumunun sıkı denetlenmesini savunarak biter.

**Deney (S§4.4).** Sıcaklık 0. Hakemler: GPT-4-turbo, GPT-3.5-turbo, Qwen2.5-7B, LLaMA3-8B,
Mistral-7B, Mixtral-8×7B; akıl yürütme modelleri o1-mini, o3-mini, Gemini 2.0 thinking, DeepSeek-R1.
Strateji deneyleri GPT-3.5-turbo üzerinde.

| Tablo 2 (yüzde) | uyum (n=5106) | konum (n=2633) | uzunluk (n=34) | somutluk (n=28) | boş referans (n=26) |
| :--- | ---: | ---: | ---: | ---: | ---: |
| GPT-4-turbo | 61,54 | 80,31 | 91,18 | 89,29 | 65,38 |
| GPT-3.5-turbo | 54,72 | 68,78 | 20,59 | 64,29 | 23,08 |
| Qwen2.5-7B-Instruct | 56,54 | 63,50 | 64,71 | 71,43 | 69,23 |
| o3-mini | 61,66 | 74,63 | 82,35 | 92,86 | 73,08 |
| DeepSeek-R1 | 56,48 | 69,17 | 94,12 | 100,00 | 50,00 |

- Bütün hakemlerde insanla uyum **%50,72-61,66** bandında. Akıl yürütme modelleri uyumda tutarlı bir
  üstünlük göstermiyor.
- Tablo 3 (LLMEval2, insan etiketine göre): insan "beraberlik" dediğinde doğruluk **%13,20-42,31**
  (GPT-4-turbo %29,73, Gemini 2.0 thinking %13,20, o3-mini %42,31); taraf seçilen kalemlerde %60-78.
  Hakemler beraberliği / belirsizliği çok kötü yakalıyor.

| Tablo 4, GPT-3.5 tabanlı (yüzde) | uyum | konum | uzunluk | iç içe talimat |
| :--- | ---: | ---: | ---: | ---: |
| taban | 54,72 | 68,78 | 20,59 | 58,33 |
| + açıklama | 52,47 | **48,97** | 35,29 | 41,67 |
| + öz doğrulama | 54,86 | 69,31 | 23,53 | 41,67 |
| + çok tur, `mean@5` | 54,72 | 69,58 | 11,76 | 50,00 |
| + çok tur, `best-of-5` | 51,95 | 58,72 | 5,88 | 37,50 |
| çoklu LLM, küme 1 (LLaMA3-8B'li) | 57,66 | **32,28** | 26,47 | 66,67 |
| çoklu LLM, küme 2 (Qwen2.5-7B'li) | 58,19 | 70,98 | 64,71 | 45,83 |

Survey'in metindeki hükümleri (S§4.4.2): açıklama istemek genelde zarar verir ve "değerlendirme ile
açıklamayı aynı anda üretmek değerlendirme kalitesini bozabilir"; öz doğrulamanın etkisi en az
(muhtemelen aşırı özgüven); çok turda çoğunluk oyu fayda, ortalama ve en-iyisi fayda yok; çoklu LLM
sonucu seçilen modellere sıkı bağlı. Özet önerisi: güçlü hakem, konum takası, çok turlu çoğunluk oyu.
Not: metindeki bazı yüzdeler tablodan küçük farklarla ayrılıyor (69,44 ↔ 69,47 gibi).

**Meta-değerlendirmeyi yeniden düşünmek (S§4.5).** (1) Uyum, çok sayıda önyargı türü ve saldırı
dayanıklılığını birlikte ölçen birleşik bir meta-değerlendirme ölçütü yok; çalışmalar kendi
protokollerini kurup elle doğruluyor. (2) Kontrollü çalışma zor: bir önyargıyı ayırmak için cevabı
uzatmak üslubu da değiştirir; GPT-4'ün kendi çıktısını GPT-3.5'inkine tercih etmesi öz-yüceltme de
olabilir, gerçekten daha iyi metni seçmek de. Survey somut kontrol yöntemi önermez.

### 3.10 Zorluklar ve gelecek (S§6, S§7)

- S§6 alt başlıklarında **atıf yok**; iddialar örnekleme düzeyinde.
- S§6.1: istemdeki küçük değişiklik ve örnek sırası sonucu oynatır; ticari hakemler sürüme bağımlı.
- S§6.3: hakem bir hukuki argümanın mantık zincirindeki ince ama temel kusuru kaçırabilir.
- S§6.4: hakem hangi içtihada / mevzuata dayandığını gösteremez; uzmanın izleyebileceği açık ve
  doğrulanabilir gerekçe istenir.
- S§6.5: **değerlendirme kayması** — mart sürümünün kabul ettiği cevabı haziran sürümü güvenlik ince
  ayarından sonra cezalandırır (kaynaksız örnek).
- S§7.2: tutarlılık ve dayanıklılığın biçimsel tanımı; hakemler arası güvenilirlik için Cohen κ ve
  **Krippendorff α**.
- S§7.3: belirsizlik ölçümü, kritik kararlar için insan-döngüde sistemler, karşıt eğitim.
- S§7.5: bilinen saldırgan özellikli test kümeleri (kelime ikamesi, yeniden ifade), hakemin zaman ve
  sürümler boyunca kararlılığının izlenmesi.

### 3.11 Hukuk (S§5.2.2)

Ma ve diğ. (2024): uzman tasarımlı az örnekli istemle hukuken ilgili olgu ve emsal işaretleme ·
Cheong ve diğ. (2024): sorumlu hukuki tavsiye için dört boyutlu çerçeve · **Ryu ve diğ. (2023)
Eval-RAG**: hukuki metni getirmeyle destekli değerlendiren hakem; Korece hukuki soru-cevapta insan
uzmanla daha yakın uyum · ölçütler: LegalBench, LexEval, IndoCareer, AgentHarm. Riskler: olgusal
halüsinasyon, "ince ama hukuken önemli ayrımları" kaçırmak, yargı çevresine özgü çerçeveler. Öneriler:
hukuki veritabanına karşı doğrulama, uzman yönlendirmeli kalibrasyon, açık gerekçe ve mevzuat atfı veren
hakemler.

---

## 4. HakHukuk için somut uygulamalar

Bugünkü tasarım (kayıttan): bağlayıcı `gpt-4o-mini`, ikinci aile `claude-sonnet-5`; κ 0,534 (tam
sadakat) / 0,409 (atıf temizliği), Pearson r 0,705; ikinci hakem sistematik olarak daha katı (24/80
düşük, 8/80 yüksek); aile dışlaması ([ADR-0032](../docs/adr/kararlar-0027-0044.md#adr-0032)); tek
gözlemde öz-tercih ters çıktı; cevabı gören hakem "geçerli tuzak" paydasını 22,3 p (mini) / 8,4 p
(4o) kaydırdı ([#45](../docs/record/kronoloji-39-52.md#45)); konum yanlılığı bir denetimde görüldü,
konum-ters kontrolüyle sınandı ([#55](../docs/record/kronoloji-53-62.md#55)); regex dedektör üç kez
fazla red saydı; iddia düzeyinde FactScore-benzeri sadakat; gürültü tabanı ~0,3 A1; fatura × 1,596.
Kaynaklar: [`MODEL_CARD.md`](../MODEL_CARD.md) §5.3,
[`KAPPA.md`](../outputs/eval/hp/hp-hakem-paneli/KAPPA.md).

Maliyet hesapları **ölçüm değil, hesaptır**: `KAPPA.md` §1'deki birim bedellerden (mini $0,0417/80
cevap, Sonnet $1,8604/80 cevap) ve 1,596 fatura payından türetildi.

### 4.1 Önerilen eklemeler (öncelik sırasıyla)

**Ö1 — İnsan↔hakem pilotu dondurmadan önce (F1), yalnız F4'te değil.**
- *Ne:* Mevcut kolların DEV cevaplarından ~40-60 kalem, kör, kullanıcı okur (F4 hızıyla ~2 sa, hesap).
  Hakem seçimi ve istemler bu pilotun uyumuyla dondurma ADR'sine yazılır. F4'ün ~300 kalemlik okuması
  doğrulayıcı (confirmatory) kalır.
- *Neden:* Plan insan yer-gerçeğini **son ölçümden sonra** (F3 → F4) kuruyor. Uyum düşük çıkarsa hakem
  ancak test açıldıktan sonra değişebilir; bu, YYH'nin "test açıldıktan sonra gelen yeni fikir yeni
  hipotezdir" kuralıyla çatışır. Bugünkü iki hakemin κ'sı zaten 0,6'nın altında.
- *Survey:* S§2.5 (önce insanların nasıl değerlendirdiğini ve güvenilir örnek vakaları anlamak,
  yineleme, "açık güvenilirlik metrikleri"), S§4.1 (insan uyumu birincil meta-değerlendirme), S§7.3
  (kritik kararlar için insan-döngüde).
- *Nereye:* YYH insan doğrulaması ve takvim (F1 satırı) · dondurma ADR'si · DEV, test değil.

**Ö2 — Türkçe önyargı ve dayanıklılık sondası (pertürbasyon), DEV cevapları üzerinde.**
- *Ne:* ~40 DEV cevabına tek değişkenli bozmalar; her hakem ve regex dedektör için karar değişim
  oranı: (a) uzatma (aynı içerik, yeniden ifade) · (b) gerçek ama soruya ait olmayan bir madde atfı
  ekleme · (c) kesinlik/şerh cümlesi ekleme-çıkarma ("bir avukata danışın" dahil) · (d) "Düşünce
  süreci:" açılışı · (e) bağlamdaki kaynak sırasını ters çevirme · (f) kol adını isteme sızdırma.
- *Neden:* (b) isabetsiz atıf eksenimizin tam kendisi ve otomatik vekili yok
  ([ADR-0066](../docs/adr/kararlar-0064-0085.md#adr-0066)); (c) dedektörün üç kez fazla red saymasının
  hakem tarafındaki eşi; (a) öznelerin cevap uzunlukları 171-862 belirteç arasında değişiyor
  (MODEL_CARD §5.1, rakipler dahil); Makale 1 kolları için ölçülmedi. Sonuçlar RQ2'nin ("ölçüm
  düzeltmesi hükmü çeviriyor mu") doğal bir ek satırıdır.
- *Survey:* S§4.2.2 (uzunluk, somutluk/atıf, merhamet solması, konum), S§4.3 (kesinlik ifadeleri,
  "Thought process:" açılışı), S§4.5 (tek değişkenli kontrollü çalışma), S§7.5 (bilinen saldırgan
  özellikli test kümeleri).
- *Nereye:* F0-F1, `outputs/eval/hp/<yeni-koşu>/` + `KUNYE.json`, kronoloji #72+. *Maliyet (hesap):*
  mini, 5 sonda × 40 = 200 çağrı ≈ $0,17; Sonnet aynı kapsamda ≈ $7,4 → Sonnet yalnız (b), (c), (e)
  için ≈ $4,5.

**Ö3 — İddia listesini sabitle, doğrulamayı çok turlu çoğunlukla yap; iddia düzeyi κ'yı mümkün kıl.**
- *Ne:* `groundedness.py` bugün `--runs N` ile iddia havuzunu **birleştiriyor** (ortalamaya yakın) ve
  her turda iddiaları yeniden çıkarıyor. Öneri: Aşama 1'in iddia listesini içerik-adresli önbelleğe al,
  Aşama 2'yi N=3 koş, iddia başına çoğunluk etiketi. İki hakem aynı iddia listesini doğrularsa iddia
  düzeyinde κ kurulabilir (`KAPPA.md` §3: 273 ↔ 341 iddia eşleşmediği için kurulamamıştı).
- *Neden:* Hakemler arası farkın bir kısmı ayrıştırma granülerliğinden, bir kısmı doğrulamadan geliyor;
  bugün ayrılamıyor.
- *Survey:* S§3.3.1 (çoklu tur), S§4.4.2 (çoğunluk oyu ↔ ortalama ↔ en-iyisi; çoğunluğun uyum
  satırındaki kazancı sıfıra yakın, kanıt zayıf), S§3.1.1 (ölçüt ayrıştırma, Branch-Solve-Merge).
  İddia düzeyi κ önerisi **bizim çıkarımımız**.
- *Bedel:* Aşama 1 tek aileye (çıkaran hakem) bağlanır; Sonnet'in tarihsel sayılarıyla birim değişir.
  Bütçe için yalnız birincil karşılaştırmada ve insan örnekleminde uygulanabilir. *Nereye:* F0 kod
  işi, dondurma ADR'si.

**Ö4 — Hakem çağrısı hatası ve sıfır iddialı cevap paydadan sessizce düşebilir: geçerlilik kapısı.**
- *Ne:* `scripts/puanlama/groundedness.py` (satır 257-272) hakem çağrısı ya da JSON ayrıştırması
  bütün turlarda başarısız olursa kalemi yalnız ekrana yazıp **atlıyor**; özette başarısız kalem
  sayısı yok. Sıfır iddia çıkan cevap `faithfulness=None` alıyor. `scripts/puanlama/harness_tablo.py`
  (satır 129-136) A1'i yalnız puanı olan cevaplanan kalemlerden hesaplıyor, `coverage` ise regexten.
  Kontrol edilmesi önerilen kapı: "puanlanan cevaplanan kalem = cevaplanan kalem", aksi hâlde dur;
  özete `n_hakem_hata` ve `n_sifir_iddia`.
- *Durum:* Kod okundu, **koşularda kaç kalemin etkilendiği sayılmadı** — doğrulanmalı. Bu sınıf
  `docs/record/yurutme-tuzaklari.md`'nin "hata vermeden yanlış sayı" sınıfına aday.
- *Survey:* S§2.3.1 (kurala dayalı çıkarımın kırılganlığı), S§6.2 (puanlama mekanizmasının
  kırılganlığı otomatik hattı bozar). Koda bağlantı **bizim çıkarımımız**.
- *Nereye:* F0 temel düzeltmeler.

**Ö5 — Hakem sürümünü sabitle ve bir kayma çıpası ölç.**
- *Ne:* Tarihli model kimlikleri ve sağlayıcı yönlendirmesi `KUNYE.json`'a ve dondurma ADR'sine; F0'da ve
  F3'te aynı 80 DEV cevabı (`tgta_v1`) aynı hakemle yeniden puanlanır; fark gürültü tabanını aşarsa
  F3 puanlaması durur.
- *Neden:* F0 ile F3 arasında aylar var; OpenRouter üzerinden çağrılan hakemin arkadaki sürümü
  değişebilir. `llm_client.py` sağlayıcıları zaten kaydediyor (ADR-0029), ama zaman içi kayma ölçülmüyor.
- *Survey:* S§6.1 (sürüme bağımlılık), S§6.5 (değerlendirme kayması), S§7.5 (zaman ve sürümler
  boyunca kararlılık). *Maliyet (hesap):* okuma başına mini ≈ $0,07, Sonnet ≈ $3,0.

**Ö6 — Uyum raporunun metrik seti ve okuma aracı.**
- *Ne:* İnsan↔hakem/dedektör/ajan için yüzde uyum + Cohen κ + **sınıf başına precision/recall**
  (seyrek sınıflar: gereksiz red 4/80, isabetsiz atıf 8/80); sürekli sadakat için Spearman; çok okuyuculu
  ve eksik hücreli (öğrenciler ~üçte bir) insan↔insan için Krippendorff α. Okuma protokolüne
  "belirsiz" kategorisi; uyum belirsizli ve belirsizsiz ayrı raporlanır.
- *Araç:* `scripts/puanlama/judge_agreement.py` bugün yalnız iki okuyuculu κ ve Pearson hesaplıyor;
  `export` ilk N kaydı alıyor (rastgele/katmanlı değil) ve CSV'de hakem kararını insanın dolduracağı
  sütunun **yanında** gösteriyor — bu, YYH'nin "kör okuma" şartıyla bağdaşmaz.
- *Survey:* S§4.1 (yüzde uyum, κ, Spearman, precision/recall), S§7.2 (κ ve Krippendorff α), Tablo 3
  (hakemler beraberliği %13-42 doğrulukla yakalıyor). Okuyucunun hakem kararına çapalanması survey'deki
  merhamet solmasıyla (S§4.2.2, "anonim değerlendirme") yalnız **benzeşimdir**; doğrudan survey bulgusu
  değil. Seyrek sınıfta κ'nın kararsızlığı da **bizim** notumuz.
- *Nereye:* insan doğrulaması, F4 hazırlığı (F1'deki pilotta ilk kullanım).

**Ö7 — Birincil karşılaştırmada uzunluk ve atıf yoğunluğu kontrolü; insan örneklemini katmanla.**
- *Ne:* Kol başına ortalama cevap uzunluğu ve atıf sayısı; hakem puanı ↔ uzunluk korelasyonu kol içinde;
  insan örneklemine bütün isabetsiz atıf kalemleri (B1 sınıfı) ve hakemlerin ayrıştığı kalemler zorunlu
  tabaka olarak.
- *Survey:* S§4.2.2 (uzunluk; somutluk/otorite/atıf önyargısı "halüsinasyonu teşvik eder"), S§4.5
  (uzunluk karıştırıcıdır). *Nereye:* istatistik planında "ikincil" analiz, insan örneklemi.

**Ö8 — İz↔cevap tutarlılık hakemi: önce deterministik, sonra yapılandırılmış LLM yargısı.**
- *Ne:* İzde seçilen kaynak kimlikleri (`KAYNAK n`) ile cevapta atıflanan maddeler deterministik
  eşleştirilir; LLM yalnız kalan kalemlere, katı JSON etiketle (tutarlı / tutarsız / belirsiz) ve
  kaynak sırası iki yönde verilerek bakar; iki sıra çelişirse "belirsiz" (Conflict Rate raporlanır).
  Hakem izi okurken izin "düşünce" açılışlarından etkilenebileceği sondada (Ö2-d) ölçülmüş olur.
- *Survey:* S§2.4.4 ve S§5.1.1 (adım düzeyi akıl yürütme yargısı; "güvenli görünen ama temelden kusurlu
  değerlendirmeler"), S§4.3 ("Thought process:" açılışı), S§6.3 (hukuki argümandaki mantık kusurunu
  kaçırma), S§3.1.1 (ayrıştırma, takas), S§5.1.1 (Tang ve diğ. 2024c permütasyonla öz tutarlılık).
  Deterministik ön katman, projenin "hakemsiz omurga" ilkesinin uzantısıdır (bizim tasarımımız).
- *Nereye:* düşünce koruma ekseni, F1 tasarımı, dondurmadan önce.

### 4.2 Yapılmaması önerilenler (survey'in olumsuz bulgularından)

- Ek "emin misin?" öz doğrulama turu eklemeyin: etkisi en az (S§3.3.2, S§4.4.2).
- Hakem turlarını ortalamayla ya da en-iyisi seçimiyle birleştirmeyin (S§4.4.2, Tablo 4).
- İki hakemi ortalamayın ya da oylamayın: çoklu LLM sonucu bileşime sıkı bağlı, zayıf bir üye konum
  tutarlılığını 68,78'den 32,28'e düşürdü (S§4.4.2, Tablo 4). Bugünkü kural — manşet, iki ailenin
  aralığı ([ADR-0057](../docs/adr/kararlar-0045-0063.md#adr-0057)) — bununla uyumlu.
- Bağlayıcı istemleri hattın ortasında değiştirmeyin. Survey açıklama alanının zarar verebildiğini
  söylüyor (S§4.4.2); `score_abstention.py`'nin hakemi kararla aynı JSON'da tek cümlelik `reason`
  istiyor. Ama bulgu GPT-3.5 ve İngilizce ikili karşılaştırmadan geliyor ve istemi değiştirmek tarihsel
  sayıları kıyaslanamaz yapar (dosyadaki "KASTEN DEĞİŞTİRİLMEDİ" notu). Gerekirse yalnız DEV'de, Ö2'nin
  bir sondası olarak ölçülür.

### 4.3 Makale 2 için

- **Hakemsiz ödül survey'le destekleniyor:** hakemler yüzeysel belirteçlerle manipüle edilebiliyor
  (S§4.3) ve LLM-as-a-Judge ile model optimizasyonu "henüz emekleme döneminde" (S§7.9). Ödüle LLM hakem
  girmezse değerlendirme hakemi politikadan bağımsız kalır (bu çıkarım bizim).
- RL çıktının üslubunu (atıf yoğunluğu, kesinlik dili) kaydırabilir; Ö2'nin sondaları RL sonrası
  kolda yeniden koşulmalı ki hakem önyargısı RL kazancı gibi okunmasın (S§4.2.2, S§4.3; bağlantı bizim).
- Rakip ölçümünde maliyet için basamaklı değerlendirme (S§3.3.1, Jung ve diğ. 2024) ve belirteç
  olasılığından güven (S§2.3.2, S§3.3.2) düşünülebilir; ama öz bildirilen güven işe yaramıyor (S§4.4.2)
  ve olasılık erişimi aileye göre değişir (aşağıda).
- Öz-tercih hücresi (Claude özne × Claude hakem) yalnız hakem farkıyla yorumlanamaz: daha sert puan
  kalite farkından da gelebilir (S§4.5'in GPT-4 örneğiyle aynı karıştırıcı). İnsan etiketli alt küme
  hakem: aynı cevaplarda iki hakemin insana göre sapması karşılaştırılır (bizim önerimiz).

---

## 5. Survey ile planın çeliştiği ya da planın eksik kaldığı yerler

1. **Zamanlama:** survey önce doğrulayıp sonra ölçeklemeyi öneriyor (S§2.5, S§4.1); plan insan
   doğrulamasını son ölçümden sonraya koyuyordu (F3 → F4). → Ö1.
2. **Bağlayıcı hakem zayıf olan:** survey güçlü hakem öneriyor (S§4.4.2 özeti); kayıtta mini'nin
   çapalanması 4o'nunkinin ~2,7 katı (22,3 ↔ 8,4 p). Plan ikinci hakemi yalnız birincil karşılaştırmaya
   ve 1 seed'e kısmış. Çelişki değil, bilinçli bütçe kararı; ama bağlayıcı hakemin insanla uyumunun F4'ten
   önce bilinmemesi riski büyütüyor.
3. **Çok turlu birleştirme:** survey çoğunluk oyu öneriyor; `groundedness.py` turları havuzluyor
   (ortalamaya yakın) ve varsayılan `--runs 1`. → Ö3.
4. **Yanlılık envanteri eksik:** plan konum ve çapalanma dışındaki önyargıları (uzunluk, somutluk/atıf,
   kesinlik dili) ölçmüyor; bunlardan ikisi doğrudan bizim eksenlerimize denk. → Ö2, Ö7.
5. **Kayma:** plan hakem sürümünün F0-F3 arasında sabit kaldığını varsayıyor. → Ö5.
6. **Survey'in eksik kaldığı, planın önde olduğu yerler:** survey bootstrap, güven aralığı ya da
   istatistiksel çıkarım tartışmıyor (S§4-S§7'yi kapsayan kısımda bulunamadı); κ eşiği vermiyor;
   hakemsiz deterministik omurgayı (atıf doğrulama, regex dedektör) ve dedektörün kendi kalibrasyonunu
   ele almıyor; aile dışlamasını yalnız "geçici çözüm" olarak anıyor. Plandaki soru × seed bootstrap ve
   aile dışlaması survey'e dayanmaz, başka kaynakla gerekçelendirilmeli. `judge_agreement.py`'deki
   0,6 / 0,8 eşikleri de survey'den gelmiyor; makalede ayrı bir kaynağa bağlanmalı.

## 6. Aktarılamayanlar ve çekinceler

- **Deney ortamı farklı:** S§4.4 İngilizce, ikili tercih (LLMEval2) ve önyargı (EvalBiasBench)
  verisiyle, GPT-3.5/GPT-4-turbo dönemi hakemlerle; bizimki Türkçe, mevzuata dayalı, referanslı ve
  iddia düzeyinde. Tablo 4'teki etki büyüklükleri bize taşınmaz, yalnız yönü fikir verir.
- **Örneklemler küçük:** önyargı sütunları n=24-34; ±1 kalem 3-4 puan oynatır. Survey bunları belirsizlik
  aralığı olmadan raporluyor.
- **Referanslı ↔ referanssız** ayrımına ayrı bir bölüm yok (JudgeLM, CritiqueLLM ve EvalBiasBench'in
  "boş referans" türüyle dolaylı geçiyor); bizim hakemimiz altın maddeyle referanslıdır.
- **İnce ayarlı hakemler** (PandaLM, JudgeLM, Auto-J, Prometheus) İngilizce ve kendi dağılımına aşırı
  uyumlu (S§2.2.2); Türkçe hukukta kullanılamaz, üstelik yeni bir aile ekler.
- **Belirteç olasılığı yöntemleri** (S§2.3.2, S§3.3.2) olasılık erişimi ister. OpenAI tarafında
  mümkün; Anthropic API'sinin olasılık döndürmediği bilgisi bu oturumda **doğrulanmadı**. Yöntem iki aileye
  simetrik uygulanamayabilir.
- **S§6 kaynaksız:** zorluklar bölümünün alt başlıklarında atıf yok; değerlendirme kayması örneği dahil.
  Makalede bunlar "survey'in tespiti" olarak anılabilir, kanıt olarak değil.
- **Metin ↔ tablo farkları:** S§4.4.2 metnindeki bazı yüzdeler tablodan ayrılıyor; GPT-4'ün "büyük
  farkla" önde olduğu iddiası Tablo 2 ile tam örtüşmüyor (o3-mini uyumda 61,66 ↔ 61,54). Tablo 4'ün
  `majority@5` satırı HTML'de bozuk; çoğunluk oyunun faydası yalnız metindeki hükümden biliniyor.
- **Okuma sınırı:** bu not TeX'ten değil, özetleyen bir araçla HTML'den okundu (başa bakın). Doğrudan
  alıntı yapılacaksa TeX ya da PDF'den yeniden doğrulanmalı.
