# A Survey on Large Language Model Benchmarks (arXiv 2508.15361) — test kümesi tasarımı için not

> **LİTERATÜR ÖZETİ.** Kaynağın bulguları kaynağa aittir; buradan çıkan proje önerileri **karar
> değildir**, karar olursa ADR-0089 ve sonrasına işlenir.
>
> **Kaynak:** arXiv 2508.15361 (Ağustos 2025), TeX kaynağından okundu:
> `~/.cache/arxiv-papers/2508.15361/neurips_2025.tex` (tek dosya, 1.207 satır, `\input` zinciri yok;
> `.bbl`/`.bib` ve şekil PDF'i okunmadı). Bütün bölümler okundu, 2026-10-10.
> Yazarlar: Shiwen Ni, Guhong Chen, … Min Yang (sorumlu yazar); ağırlıkla Shenzhen Institutes of
> Advanced Technology (CAS). NeurIPS 2025 biçim dosyasıyla dizilmiştir; bu bir kabul bilgisi değildir.
>
> **Gerçek konu (kaynaktan doğrulandı):** genel bir LLM benchmark **taraması**. 283 benchmark üç
> sınıfa ayrılıyor: genel yetenek · alan-özgü · hedef-özgü (risk, ajan, diğer). Bir benchmark kurma
> **yöntem rehberi değildir**: örneklem büyüklüğü, güven aralığı, seed, etiketçi uyumu üzerine bölüm
> yoktur. Hukuk bir alt bölümdür (~1 sayfa).
>
> **Okunan proje belgeleri:** `CLAUDE.md` · `docs/YAYIN_YOL_HARITASI.md` · `MODEL_CARD.md` §3-§5 ·
> `data/README.md`. `data/eval/canon/` açılmadı. Yol haritası bu not yazılırken (2026-10-10 04:08)
> yeniden düzenlendi; aşağıdaki § atıfları **yeni sürüme** göredir (§2.5.x ölçüm, §2.6 takvim F0-F5).
>
> **Atıf kuralı:** "Survey:" ile başlayan her cümlenin yanında bölüm adı vardır. "Bizim çıkarımımız"
> yazan şey survey'de yoktur. Bölüm numaraları TeX'teki sıradan türetildi.
>
> *Yazım notu:* metni bir alt ajan üretti; alt ajanların dosya yazması araç tarafından engellendiği
> için ana oturum ajanın metnini olduğu gibi bu dosyaya yazdı.

---

## TL;DR

- Survey'in ana tezi: benchmark'ların üç kronik sorunu var — **kirlenmenin şişirdiği skorlar**,
  **kültürel/dilsel yanlılık**, **süreç güvenilirliği ve dinamik ortam ölçümünün eksikliği** (§1).
- Önerdiği çare çoğunlukla **dinamik / canlı / kamuya açık olmayan** kümeler (LiveBench,
  LiveCodeBench), **pertürbasyonla genelleme sınaması** (MATH-P) ve **çok hakemli, denetlenen**
  LLM-hakem kullanımıdır.
- Hukuk bölümü: Çin, ABD, Kore kümeleri; Bloom tabanlı görev taksonomileri (LawBench, LexEval),
  hukukçu kıyası (LAiW), LegalBench'in beş görev tipi, atıflı cevap için CiteLaw. Gelecek yönü:
  çok dilli / çok yargı alanlı, medeni hukuk ↔ common law farkını gözeten taksonomi.
- **HakHukuk'a en değerli aktarımlar:** mühürlü parçanın kamuya açık depoda durmaması · örtüşme
  denetiminin "şablon ezberi" düzeyine genişletilmesi · soru üreticisinin aile damgası · vatandaş dili
  pertürbasyon dilimi · görev tipi etiketi · hakem kontrol kalemleri · insan protokolünde sadakatin iddia
  düzeyinde tanımı · Türkçe genel yetenek kontrolü.
- **Survey'in bize söylemediği:** istatistik (planın §2.5.5'i survey'in çok önünde), soru belirsizliği,
  madde uzunluğu katmanlaması, RAG çekinmesi (bunlar için
  [`summary_eval_benchmark_literature.md`](summary_eval_benchmark_literature.md) daha iyi kaynak).

---

## Ana katkılar (survey'in kendi beyanı, §1)

1. 283 benchmark'ın üç sınıflı taksonomisi (Şekil 2): **genel yetenek** (dil çekirdeği, bilgi, akıl
   yürütme) · **alan-özgü** (doğa bilimleri, beşeri ve sosyal bilimler, mühendislik) · **hedef-özgü**
   (risk ve güvenilirlik, ajan, diğer).
2. Her benchmark için ortak bir tanım satırı: **Focus · Language · Source · Data Type · Eval.
   (AE / LLM / ME / Human) · Indicators · Amount · Method · Citations**. Survey bunu "sonraki benchmark
   tasarımı için doğrudan başvurulabilir paradigma" olarak sunar.
3. Üç ana sorun: kirlenmeden şişen skorlar · kültürel ve dilsel yanlılıktan haksız değerlendirme ·
   "süreç güvenilirliği" ve "dinamik ortam" değerlendirmesinin yokluğu.

Giriş ayrıca şunları sayar: statik değerlendirme gerçek dünyayı taklit edemez; tek göstergeye
(doğruluk, BLEU) aşırı dayanma; büyük ölçekli değerlendirmenin hesap ve insan maliyeti.

---

## Akılda tutulacak teknik ayrıntılar

### Kirlenme ve doygunluk

- Survey (§3.2.3 Knowledge — Summary): kirlenme "en yaygın" sorundur; çare **dinamik ya da
  "Google-Proof"** kümeler (GPQA) ve **kirlenmeyi tespit eden sağlam istatistik yöntemleri** (yöntem
  adı vermez).
- Survey (§3.3.3 Applied and Contextual Reasoning): web kaynaklı kümelerde test kümesinin eğitim
  korpusuna sızmasını önlemek "neredeyse imkânsız"; **kamuya açık olmayan, dinamik** kümeler (LiveBench,
  "canlı, özel kullanıcı sorguları") "doğrudan ve gerekli bir cevap".
- Survey (§4.3.1 Software Engineering): LiveCodeBench, canlı yarışma sorularıyla modelleri "gerçekten
  görülmemiş veride" ölçer.
- Survey (§4.1.6 Natural Sciences — Summary): eğitimde görülmüş değerlendirme verisi sınavı "açık
  kitap sınavına" çevirir. Asıl genelleme sorusu, modelin bilgiyi mi anladığı yoksa **benzer problemlerin
  çözüm şablonlarını mı ezberlediği**dir; MATH-P, ASyMOB gibi **pertürbasyon** kümeleri SOTA modellerin
  bile "kısayol öğrenmesine" dayandığını gösterir.
- Survey (§3.2.1 Knowledge — Evolution; §3.1.2 Cross-Cutting Design Innovations): doygunluğa cevap
  ya zorluğu artırmak (MMLU → MMLU-Pro: daha çok seçenek, daha çok akıl yürütme) ya da "yaşayan"
  çerçevelerdir (HELM, BIG-Bench sürekli görev ekler).
- Survey (§3.1.1 Evolution, Phase 1-2): GLUE'nun tanı kümesi modellerin **sözcük örtüşmesine** ve
  sahte istatistik ipuçlarına dayandığını gösterdi; HellaSwag ve WinoGrande (AFLITE) etiketleme
  artefaktlarına karşı **adversaryal süzme** kullandı.
- Survey (§5.1.4 Data Leak): bu başlık esas olarak **kişisel veri (PII)** sızıntısı ve üyelik çıkarımıdır
  (WikiMIA, gösterge Min-k% Prob; KoLA; C²LEVA). Test-kümesi kirlenmesiyle aynı kavram değildir; survey
  ikisini aynı başlıkta tutar.

### LLM hakem güvenilirliği

- Survey (§3.1.3 Linguistic Core — Summary): **"LLM-hakemin kendine gönderme tuzağı"** — öncü
  modeller hakem olduğunda kendi üretim kalıplarını döngüsel biçimde onaylayıp "tanıdık olanı" ödüllendirme
  riski. Çare: **adversaryal denetim çerçeveleri** ve **uzmanlaşmış, alana ayarlı hakem toplulukları**
  (insan uyumunu koruyarak).
- Survey (§4.1.6 Natural Sciences — Summary): LLM-hakem paradigmasının sağlamlığı sorgulanıyor;
  LLM'in ürettiği değerlendirme raporlarında **iç çelişki** gözlenmiş.
- Survey (§5.3 Others): JudgeBench, LLM hakemlerin tutarlılığını 350 çoktan seçmeli soruyla ölçer.

### Hukuk (§4.2.1 Law)

- **Görev taksonomisi.** Survey: gerçek dünyadaki hukuki destek "LLM'lerin kısa kanun metinlerini
  ezberlemesini, uygun biçimde uygulamasını ve açık, mantıklı akıl yürütmeyle cevap vermesini"
  gerektirir. LawBench: Bloom'dan türetilmiş üç düzey (hukuki bilgiyi ezberleme · anlama · uygulama),
  20 görev. LexEval: altı boyut (ezber, anlama, mantıksal çıkarım, ayırt etme, üretim, etik), 23 görev;
  **hukukun değişimi** ve etik (yanlılık, ayrımcılık, mahremiyet) dahil. LAiW: hukukçunun kıyas
  düşüncesinden üç düzey — **temel bilgi getirme · hukuki temel çıkarımı · karmaşık hukuki uygulama**.
  LegalBench: 162 görev, survey'in özetiyle beş tip — sorun tespiti · kural hatırlama · kural uygulama
  ve sonuç · kanun yorumu · retorik anlama. LBOX OPEN: Kore, dava analizi. CiteLaw: **uygun atıflı,
  hukuken sağlam cevap**; göstergeler MAUVE, ROUGE, atıf kalitesi; 1.000 kalem. CaseGen: belge üretimi.
- **Veri kaynağı.** Survey: en önemli kaynak gerçek hukuki belge ve davalardır; çoğu küme eski
  yarışma verilerini (CAIL, LAIC) yeniden derler; üçüncü yol **hukukçuların elle ürettiği veri** —
  "alan uzmanlığını artırır ve **veri sızıntısı riskini azaltır**".
- **Gelecek yönü.** Survey: çok dilli / çok yargı alanlı küme eksik; bu yalnız dil eklemek değil,
  **medeni hukuk ↔ common law** gibi gelenek farklarını yakalayan taksonomi gerektirir; çok kipli
  hukuk kümesi yok.
- Survey (§4.2.6 Humanities — Summary): değerlendirmeden önce **ince taneli, senaryoya dayalı görev
  taksonomisi** kurulmalı; yalnız çoktan seçmeli soru yetersiz, **senaryo odaklı** değerlendirme gerekli.
- Survey (§5.2.3 Domain Proficiency): CourtBench (AgentCourt), simüle duruşmada avukat ajanları; 124
  çoktan seçmeli kalem.

### Halüsinasyon, sağlamlık, çekinme

- Survey (§5.1.2 Hallucination): iki tür — **olgusal** (doğrulanabilir olguya aykırı, uydurma) ve
  **sadakat** (talimattan, girdi bağlamından ya da iç tutarlılıktan sapma). Çözümler arasında RAG.
  FActScore çıktıyı **atomik olgulara** bölüp dış kaynağa karşı doğrular. FreshQA ve RealtimeQA
  **bayat bilgiden** doğan halüsinasyonu ölçer. Açık sorunlar: (1) birleşik çerçeve yok, (2) uzun belgede
  tutarlılık halüsinasyonu zor yakalanır, (3) **öznel yargı ile doğrulanabilir olgu arasındaki tanım
  belirsizliği**.
- Survey (§5.1.3 Robustness): boyutlar — adversaryal · talimat izleme · **istem** · araç kullanımı.
  PromptRobust: istemin ifadesindeki küçük değişiklikler başarımı belirgin biçimde değiştirir. BOSS:
  dağılım dışı sağlamlık.
- Survey (§5.3 Others): **OR-Bench**, 80 bin "aşırı ret" kalemiyle red ↔ kabul dengesini ölçer
  (göstergeler: over-refusal rate, acceptance rate). Survey'deki diğer red kümeleri (SORRY-Bench,
  Do-Not-Answer, HarmBench) **güvenlik reddi**dir — kanıt yetersizliğinden çekinme değil.
- Survey (§5.2.5 Agent — Summary): güvenlik değerlendirmesi "ikili ret tespitinin ötesine", niyet ve
  risk bağlamı modellemesine geçmeli.
- Survey (§5.1.5 Risk — Summary): **dinamik gerçek zamanlı değerlendirme** (zamana duyarlı bilgi),
  İngilizce dışı ve düşük kaynaklı diller, uzun bağlam ve çok tur tutarlılığı, sürekli kırmızı takım.

### Süreç ve dil

- Survey (§3.3.1 Logical; §3.3.4 Reasoning — Summary): doğruluk kırılgan bir göstergedir; akıl yürütme
  zincirinin **sadakati, mantıksal tutarlılığı ve verimliliği** ölçülmeli.
- Survey (§3.1.1 Phase 3; §3.1.3 Summary): Xtreme, analitik dillerden **eklemeli (agglutinative)**
  dillere geçişte belirgin başarım düşüşü gösterdi; ünlü uyumu gibi yapısal olgular "yalnız üstveri"
  olarak kalıyor. §3.2.3: kümeler çoğunlukla Batı ve İngilizce merkezli, statik.
- Survey (§3.2.2 Knowledge — Methodological Landscape): sınav tabanlı kümeler (AGIEval, GAOKAO)
  modeli insana göre **yorumlanabilir** biçimde konumlar; §3.2.3: çoktan seçmeli biçim modelin
  **belirsizliği kabul etmesini** ölçemez.

### Survey'in tablolarından (bizim okumamız, survey'in iddiası değil)

- Küçük kümeler yaygındır: MT-Bench 80, HumanEval 164, TPBench 57, RealtimeQA 30, FactCheck-Bench 94,
  CourtBench 124. Survey bunun istatistik yeterliliğini tartışmaz.
- Tablolar iç tutarsız olabilir: GPQA bilgi tablosunda 448, doğa bilimleri tablosunda 1,1k kalem.
  Survey'in tablo sayıları **birincil kaynaktan doğrulanmadan** alıntılanmamalı.

---

## HakHukuk için somut uygulamalar

Bağlam olguları: CANON 6 mod · bağlayıcı metrik kütle = `coverage × A1` · DEV 80 + 70 · eski TEST
40 + 35 bir kez açıldı · yeni test ~200-225 + ~100 mühürlü (§2.5.1) · sorular altın maddenin içinden
LLM ile üretiliyor, ~%22'si tek başına belirsizdi ([#53](../docs/record/kronoloji-53-62.md#53)) ·
LegalBench/BigLaw koşulmadı (ADR-0016) · HMGS kapsam dışı (§1) · n=80'de %10'luk oranın güven aralığı
genişliği 13,4 puan.

### Öncelik tablosu

| # | öneri | survey dayanağı | aşama · dosya |
| :-- | :--- | :--- | :--- |
| U1 | Mühürlü ~100 soru **kamuya açık depoya girmez**; depoya yalnız SHA-256 özeti yazılır | §3.3.3 Applied and Contextual Reasoning · §3.2.3 Knowledge Summary | F2 dondurma · dondurma ADR'si · `data/README.md` · `tests/` kapı testi |
| U2 | Örtüşme denetimi üç düzeyde; sonuçlar "altın madde eğitimde görüldü mü" kırılımında ikincil raporlanır; test soruları eğitim verisini üretenden farklı üretici/istemle üretilir | §4.1.6 Natural Sciences Summary · §3.2.3 | F1 üretim · dondurma ADR'si istatistik planı (§2.5.5) |
| U3 | Soru üreticisinin modeli, sürümü, istemi damgalanır; aile dışlaması **üreticiye** genişletilir | §3.1.3 Linguistic Core Summary (genişletme bizim) | F1 · yeni test kümesinin künyesi |
| U4 | Vatandaş dili pertürbasyon dilimi (~50 soru, birer yeniden ifade) — ikincil eksen | §5.1.3 Robustness · §3.1.1 Phase 1-2 · §4.1.6 | F1 üretim · F2 okuma · F3 rapor |
| U5 | Her yeni soruya görev tipi **etiketi** (katman değil) | §4.2.1 Law — Legal Task Taxonomy · §4.2.6 Summary | F1 üretim · F3 rapor |
| U6 | Hakem kontrol kalemleri: etiketi bilinen, kasten bozulmuş cevaplar (isabetsiz atıf dahil) hakem partisine kör karıştırılır | §3.1.3 · §5.3 Others (JudgeBench) · §4.1.6 | F1 hazırlık · F3 puanlama · §2.5.2 |
| U7 | İnsan protokolünde **sadakat** açık bir madde olur ve iddia düzeyinde tanımlanır (doğrulanabilir ↔ yorum) | §5.1.2 Hallucination (FActScore; açık sorun 3) | F1 protokol taslağı · F4 · §2.5.3 |
| U8 | Genel yetenek kontrolü **Türkçe + İngilizce** iki küçük küme | §3.1.1 Phase 3 · §3.1.3 · §3.2.3 | F0 küme seçimi · §2.5.4 · §6 lisans satırı |
| U9 | Yeni test kümesine survey'in dokuz alanlı tanım satırı (künye) | §1 katkı 2 · bütün özet tabloları | F2 · `data/README.md` yeni bölüm |
| U10 | Tuzakların zorluğu **modelsiz** özelliklerle tasarlanır (örtüşme, komşu madde), model çıktısıyla süzülmez | §3.2.1 · §3.1.2 (süzme yasağı bizim çıkarımımız) | F1 üretim |

### Ayrıntılar

**U1 — mühürlü parça ve kamuya açık test.** Depo `github.com/Rfetha/HakHukuk` ve proje beyanına
göre veri dahil her şey açık; `data/README.md` "`data/` tamamı versiyonlanır" diyor. Makale 1'in
özneleri (Qwen3.5-4B, Gemma 4 E4B) testten önce yayımlandığı için Makale 1 güvende. Risk Makale 2'de
(Mart-Nisan 2028): rakipler "o günün" kapalı modelleridir (§3.5); eğitim kesimi 2027'den sonraysa eski
TEST, DEV ve yayımlanmış yeni test onların eğitim verisinde olabilir. Survey'in cevabı kamuya açık olmayan
küme (§3.3.3). Somut: (a) mühürlü dosya git dışında tutulur, depoya yalnız özeti ve satır sayısı
yazılır, açıldığı gün eklenir; (b) `tests/` altına "mühürlü dosya izlenmiyor" kapı testi (projenin rejimi
teste çevirme alışkanlığı, `MODEL_CARD.md` §4.2); (c) §3.5'teki ~1.100 cevaplık rakip koşusunda kamuya
açık parçalardaki rakip sayıları "kirlenme penceresi açık" damgası taşır, bağlayıcı rakip hükmü yalnız
mühürlü parçadan kurulur. Özet taahhüdü ve damga survey'de **yoktur**, bizim önerimizdir.
`docs/record/yurutme-tuzaklari.md` için aday satır: "mühürlü küme kamuya açık depoya commit edildi —
hata vermez, sınavı sessizce bozar".

**U2 — örtüşme denetiminin tanımı.** §2.5.1 "eğitim verisiyle örtüşme denetimi" diyor ama düzeyini
tanımlamıyor. Önerilen üç düzey: (i) soru düzeyi yakın-kopya (eğitim sorularına göre); (ii) **altın
madde düzeyi** — test sorusunun altın maddesi `raft_scrubbed` / `orpo_abstain_cp2c` /
`grounded_qa` içinde altın madde olarak geçmiş mi; (iii) **şablon düzeyi** — test soruları eğitim
sorularıyla aynı üretici ve istemle üretilirse eğitilen kollar, ham modele göre, içerikten değil üslup
tanıdıklığından kazanabilir (survey'in "çözüm şablonu ezberi", §4.1.6). İki seçenek: (a) görülmüş
maddeleri tutup sonuçları görülmüş/görülmemiş kırılımında ikincil raporlamak — dağılım ürün kullanımına
yakın kalır; (b) görülmüş maddeleri dışlamak — temiz ama dağılımı değiştirir. Tercih (a); seçim dondurma
ADR'sine girer. Kırılımlar yalnız betimseldir (aşağıda istatistik notu).
Denetlendi ve **uygulanamaz** bulundu: "temel modelin kesiminden sonra çıkmış kanun" dilimi (LiveCodeBench
fikri, §4.3.1). Korpustaki en büyük kanun numarası 7524'tür (`data/corpus/mevzuat_maddeler.jsonl`,
2026-10-10'da sayıldı); kanun numaraları sıralıdır ve bu 2024'e düşer (Resmî Gazete'den doğrulanmalı).
Korpus Checkpoint 2'ye kadar değişmediği için (§4.4) böyle bir dilim kurulamaz.

**U3 — üretici ailesi.** Survey'in kendine gönderme tuzağı hakem için yazılmıştır; aynı mantığın soru
üreticisine uygulanması bizim çıkarımımızdır. Sorunlu durum: eski yol haritası "ajan test sorularını
üretir" diyordu; ajan Claude ailesidir ve `claude-sonnet-5` Makale 2'nin rakibidir (§3.5). Mühürlü parçayı
Claude üretirse Makale 2'de Claude kendi ailesinin yazdığı soruları alır. Seçenekler: (a) üretici, ne özne
(Qwen, Gemma; yedek Ministral) ne Makale 2 rakibi (Gemini, Claude) olan bir aile — fiilen OpenAI ya da
üçüncü bir aile; OpenAI bağlayıcı hakemin ailesidir, bu da yazılır; (b) Claude üretir, Makale 2'deki Claude
sütunu damgalanır. Her iki durumda üretici modeli, sürümü, istemi ve tarihi künyeye girer.

**U4 — vatandaş dili dilimi.** Sorular altın maddenin içinden üretildiği için madde sözcüklerini taşır;
BM25 ayağı ve model, sözcük örtüşmesinden kolaylık görebilir (survey'in GLUE tanı kümesi ve
etiketleme artefaktı tartışması, §3.1.1). Ürünün kullanıcısı ise vatandaştır. Öneri: yeni temel
sorulardan ~50'sine, hukuk terimi kullanmayan birer gündelik dil yeniden ifadesi; kullanıcı anlamın
korunduğunu okur. Raporlanan: kütle ve `recall@10` farkı (orijinal ↔ yeniden ifade), kol başına. Birincil
metriğe girmez. Ek olarak her yeni soru için soru↔altın madde içerik-sözcük örtüşmesi hesaplanıp bir alan
olarak saklanır (tuzaklarda `_overlap` zaten var) ve sonuçlar örtüşme dilimine göre betimlenir. Bu,
RQ2'nin "ölçüm aleti hükmü çevirir mi" sorusuna da bir satır verebilir; ön-kayıtta ikincil olarak yazılmalı.
Maliyet: üretim <$1, okuma ~1 saat (tahmin).

**U5 — görev tipi etiketi.** CANON modları **davranış koşulu**dur (bağlam türü); sorunun bilişsel türünü
ayırmaz. LAiW'in üç düzeyine yakın bir etiket önerisi: madde ne diyor (doğrudan okuma) · koşul/istisna
(çok koşullu, istisnalı madde) · vaka uygulaması (senaryodan sonuç) · sayı/süre (süre, oran, tutar).
Üretici etiketi önerir, kullanıcı okurken düzeltir. **Katman yapılmaz**: kanun ve madde uzunluğu katmanına
üçüncü eksen eklemek hücreleri boşaltır. Raporu ikincil ve betimseldir. Eski küme `_complexity` alanı
taşıyor; yeni etiketle eşlenebilirliği F1'de kontrol edilir.

**U6 — hakem kontrol kalemleri.** Kayıtta iki hakem arasında κ 0,534 / 0,409 ve 10,71 puanlık kütle
kayması var (`MODEL_CARD.md` §5.3); isabetsiz atıfın otomatik vekili yok (ADR-0066). Öneri: ~40 kontrol
kalemi — bir kısmı doğru ve atıflı cevap, bir kısmı tek bir yerinden bozulmuş (süre/tutar değişmiş ·
atıf **komşu gerçek maddeye** kaydırılmış · bağlamda olmayan bir iddia eklenmiş). Kullanıcı etiketleri
doğrular, kalemler hakem partisine kör karışır. Raporlanan: her hakem ailesi için bozma türüne göre
yakalama oranı. Survey'in "adversaryal denetim" çağrısının (§3.1.3) ve JudgeBench'in (§5.3) bize uyarlanmış
hâli. Yararı: §5'teki kesme sırasında ikinci hakem ilk kesilen kalemdir; kesilirse hakem geçerliliğinin
tek kanıtı bu kalemler ve insan örneklemi olur. Maliyet: hakem payı küçük (~$1, tahmin), okuma ~1 saat.

**U7 — insan protokolünde sadakat.** §2.5.3'ün protokol listesi: cevap ↔ çekinme · altın bağlamdayken
susma · isabetsiz atıf · iz ↔ cevap tutarlılığı. Kütlenin hakemli bileşeni olan **sadakat (A1)** listede
açıkça yok, ama "insan↔hakem uyumu" raporlanacak. Öneri: sadakat ayrı bir madde olur ve iddia düzeyinde
tanımlanır — doğrulanabilir iddialar (madde no, süre, tutar, koşul, istisna) kaynakla tek tek karşılanır;
yorum cümleleri ayrı işaretlenir. Survey'in halüsinasyon bölümündeki üçüncü açık sorun (öznel yargı ↔
doğrulanabilir olgu belirsizliği) ve FActScore'un atomik olgu ayrıştırması bu ayrımın dayanağıdır. İki
hakem ailesinin düşük κ'sının bir kısmı tanım belirsizliğinden geliyor olabilir — bu bir hipotezdir,
ölçülmemiştir.

**U8 — genel yetenek kontrolü.** §2.5.4 "açık lisanslı küçük bir genel küme" diyor, dilini söylemiyor.
Eğitim Türkçe ve `data/train/replay_tr.jsonl` tam da genel Türkçeyi unutmayı bastırmak için var; yalnız
İngilizce bir küme Türkçeye özgü bozulmayı göremez, yalnız Türkçe bir küme de genel akıl yürütme kaybını
dilden ayıramaz. Survey'in eklemeli diller ve dilsel yanlılık tespiti (§3.1.1, §3.1.3, §3.2.3) dayanaktır;
aday Türkçe kümeler survey'den **değil**, [`summary_eval_benchmark_literature.md`](summary_eval_benchmark_literature.md)'den
gelir (Cetvel, TurkBench, TARA, TrGLUE; TurkishMMLU'nun bir sürümü CC BY-NC uyarılı). Lisans §6'daki satırla
F0'da okunur.

**U9 — küme künyesi.** Survey'in her benchmark için kullandığı alanlar yeni küme için doldurulur: odak ·
dil · kaynak (Mevzuat.gov.tr anlık görüntüsü 2026-08-06, sha256 `data/corpus/KUNYE.json`'da) · veri tipi
(üretim) · değerlendirme (hakemsiz + LLM hakem + insan = karma) · göstergeler · miktar · katmanlar ·
üretici (U3). Yer: `data/README.md`'de yeni bölüm (README kuralı: mevcut dosya düzenlenmez, yeni dosya
eklenir) ve kümenin kendi künye dosyası. Makalenin veri bölümü bu satırdan yazılır.

**U10 — doygunluk, süzmesiz.** Kayıtta τ_a'nın M2'si 0,955 civarında; tuzaklar kolay olursa Tablo 1'in M2
sütunu kolları ayıramaz. Survey'in doygunluk cevabı zorluğu yükseltmektir (§3.2.1). Ancak survey'in
övdüğü adversaryal süzme (§3.1.2) bizde **kullanılmamalı**: soruları bir kolun ya da ham modelin
çıktısına göre ayıklamak hem testi açmak sayılır (§2.3 "bir kez açılır") hem de süzmede kullanılan modelin
aleyhine bir yanlılık kurar (bizim çıkarımımız). Zorluk modelsiz özelliklerle kurulur: tuzak↔altın sözcük
örtüşmesi, aynı kanundan komşu madde, madde uzunluğu. Dağılım eski tuzak kümesiyle karşılaştırılıp künyeye
yazılır.

### İstatistik notu (survey'de yok, bizim)

U2, U4, U5'in kırılımları küçük hücreler üretir (örn. ~200 temel soruda dört görev tipi → tip başına ~50;
%10'luk oranın güven aralığı genişliği n=50'de n=80'deki 13,4 puandan geniş). Bunlar yalnız betimsel
raporlanır, hipotez testi kurulmaz; hangi kırılımın raporlanacağı dondurma ADR'sinde önceden yazılır.
Birincil metrik ve birincil karşılaştırma (§2.5.5) değişmez.

### Makaleye girecek atıflar (F5)

Survey'in kendisi: "medeni hukuk ↔ common law" farkı (§4.2.1 Future Direction) ADR-0016'nın gerekçesini
dış kaynağa bağlar; üç ana sorun (§1) giriş motivasyonu. İlgili çalışma için survey'in işaret ettiği
birincil kaynaklar (tam metinleri okunmadı): CiteLaw (atıflı hukuki cevap — M1'e en yakın) · LawBench,
LexEval, LAiW, LegalBench (görev taksonomisi) · OR-Bench (aşırı ret — en büyük kaybımız) · JudgeBench
(hakem tutarlılığı) · FActScore (iddia düzeyi doğrulama) · FreshQA (bayat bilgi) · PromptRobust (istem
duyarlılığı).

---

## Aktarılamayanlar / çekinceler

1. **Ezber konusunda survey ile ters yöndeyiz.** Survey hukuki desteğin "kısa kanun metinlerini
   ezberlemeyi" gerektirdiğini yazıyor ve LawBench/LexEval ezberi birinci bilişsel düzey sayıyor
   (§4.2.1). HakHukuk'ta ezber (M5) **anti-hedeftir** (güncellik kütüphanede, ADR-0027). Bu çelişki
   makalede bir cümleyle gerekçelendirilmeli; bu gelenekten gelen bir hakem HMGS benzeri bir ezber
   ölçümü isteyebilir.
2. **Dinamik / yaşayan küme idealine bilerek uymuyoruz.** Survey canlı, sürekli yenilenen kümeleri
   öneriyor (§3.1.2, §3.3.4, §5.1.5); bizim kuralımız "bir kez dondur, bir kez aç" ve turlar arası kıyas
   için sabit küme (`data/README.md`). Mühürlü parça, survey'in "kamuya açık olmayan küme" fikrinin
   statik bir karşılığıdır.
3. **Sınav tabanlı dış çıpa.** Survey sınav kümelerini insana göre yorumlanabilir buluyor (§3.2.2) ama
   çoktan seçmeli biçimin belirsizliği kabul etmeyi ölçemediğini de söylüyor (§3.2.3). HMGS'nin dışarıda
   kalması (§1) ikinci gerekçeyle uyumlu; bedeli dış çıpa yokluğudur (`MODEL_CARD.md` §3 bunu zaten yazıyor).
   HMGS'yi açık-kitap modda kullanmak düşünüldü, önerilmiyor: ÖSYM sorularının lisansı lisans-temiz veri
   kuralına takılabilir ve çoktan seçmeli biçim üretken çekinme tasarımıyla uyuşmaz.
4. **Hakem çoğulluğu ↔ kesme sırası.** Survey hakem topluluklarını öneriyor (§3.1.3); plan gecikmede ilk
   olarak ikinci hakemi kesiyor (§5). 10,71 puanlık hakem kayması düşünülünce bu sıra yeniden tartılmalı
   ya da U6 telafi olarak kurulmalı.
5. **Survey'de olmayanlar** — buralarda survey'e atıf yapılmaz: istatistik (güven aralığı, örneklem,
   seed, bootstrap) · soru belirsizliği (bizim %22 bulgumuz) · madde uzunluğu katmanlaması (ADR-0069) ·
   RAG'e özgü çekinme ve cevaplanamaz soru kümeleri (RGB, FaithEval, AbstentionBench). Survey'deki "red"
   kümeleri güvenlik reddidir; kanıt yetersizliğinden çekinmeyle aynı yapı değildir, ilgili çalışmada
   karıştırılmamalı.
6. **Zamansal eksen planda yok.** Survey hukukun değişimini (LexEval) ve bayat bilgiyi (FreshQA,
   RealtimeQA, §5.1.5) önemli sayıyor. Planda bu eksen yok; korpus Checkpoint 2'ye kadar sabit (§4.4) ve
   korpusta tarih alanı yok (`data/corpus/KUNYE.json` notu). "Kesimden sonra değişmiş madde" dilimi
   (bağlam ↔ ezber çatışması) korpus turu ya da Makale 2 adayıdır; Makale 1'de sınırlılık olarak yazılır.
7. **Gerçek kullanıcı sorusu yok.** Survey hukuk kümelerinde gerçek belgeleri en önemli kaynak, hukukçu
   üretimini sızıntıya karşı güvenli sayıyor (§4.2.1). Bizim test sorularımızın tamamı LLM üretimi. Koşullu
   seçenek: gönüllü hukuk öğrencileri maddeyi görmeden vatandaş ağzıyla ~30-50 soru yazar, altın madde
   sonra işaretlenir. Gönüllü bulunması belirsiz (§5'te tetik Mayıs 2027, test dondurma ondan önce) — plan
   buna dayanamaz; olmazsa dış geçerlilik sınırlılığı (CLAUDE.md'nin kabul edilmiş bedeli) olarak kalır.
8. **Survey'in kalitesi.** Tablolarda iç tutarsızlık var (GPQA 448 ↔ 1,1k); bazı açıklamalar özet
   düzeyinde (LegalBench beş tip olarak özetlenmiş). Bir sayı ya da tanım makaleye girecekse birincil
   kaynaktan okunur. Survey Ağustos 2025 tarihli; sonraki benchmark'ları kapsamaz.
9. **Kayıtta iki farklı yüzde.** DEV↔TEST farkı için ADR-0069 "bileşim farkın %81'ini açıklıyor" diyor;
   `MODEL_CARD.md` §5.4 "16,87 / 22,07 puan (%76) arama tavanıyla açıklanır" diyor. İkisi farklı
   ayrıştırmalardır; makalede hangisinin kullanılacağı ve tanımı tek yerde sabitlenmeli. (Survey'le ilgisi
   yok; okurken çıktı.)
