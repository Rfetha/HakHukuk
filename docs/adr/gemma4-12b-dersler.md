# Gemma 4 12B hattı — dersler ve karar kaydı (ADR-0001 … ADR-0026)

> **Bu belge ne:** emekli edilen Gemma 4 12B hattının **26 ADR'si + 38 `research_log` girdisinin**
> damıtılmış hâli. Tekil ADR dosyaları 2026-07-24'te **silindi**; kararları, elenen alternatifleri
> ve sonuçları buraya taşındı. Yeni hattın karar defteri **ADR-0027**'den başlar.
>
> **Neden tek dosya:** 26 ayrı dosya, yeni hatta başlayan için filtresiz bir yığındı — çoğu artık
> 12B'ye özgü. Karar (2026-07-24): okuma yüzeyi tek belgeye indirilsin, **içerik kaybolmasın.**
> Silinen dosyalar git geçmişinde duruyor (`4d70a77` ve öncesi).
>
> **Sayı uyarısı:** buradaki tüm rakamlar **Gemma 4 12B protokolüne** aittir — bf16/NF4,
> hakem gpt-4o-mini, seed 3407, n=40/35. **Dersler taşınır, sayılar taşınmaz.**
> Yeni base'de her şey yeniden ölçülür ve **eski tabloyla aynı tabloya karıştırılmaz.**
>
> **Atıf uyumu:** repo genelinde ~560 yerde `ADR-00NN` göndermesi var (`research_log`, spec'ler,
> `knowledge/`, script yorumları). Bu belge her ADR için bir **çapa** taşır — `#adr-0011` gibi —
> böylece o göndermeler çözülmeye devam eder.

**Nereden devam edilir:** `TASARIM.md` *(silindi 2026-09-06 — yön [`ROADMAP.md`](../../ROADMAP.md)'de)* ·
[`0027`](kararlar-0027-0044.md#adr-0027) (yeni hattın ilk kararı) ·
[`../record/README.md`](../record/README.md) (kronoloji, kesintisiz)

---

# BÖLÜM A — Dersler

> Yeni hatta başlayan burayı okur. Her ders kaynağıyla yazılı: `#NN` = `research_log` kronoloji
> numarası, `ADR-00NN` = bu belgedeki bölüm.

## A1. Veri — en pahalı dersler burada

**A1.1 Kaynaksız QA verisi ezberletir, öğretmez.** İlk tur forum verisiyle eğitildi ve battı:
tek bir cevap **154 farklı soruya birebir** yapıştırılmıştı; model "7 Kasım 1982"yi ezberledi.
`legal_acc 0.362 → 0.124`. ⚠️ Setin kendisi (`sft_v0_KIRLI_forum`) **artık yok** — git'e hiç
girmemişti, emekli hat ağacıyla birlikte silindi ([ADR-0034](kararlar-0027-0044.md#adr-0034)).
Ders yalnız bu kayıtta yaşıyor. → `#02`, [ADR-0002](#adr-0002)

**A1.2 Kâğıt üstündeki mükemmellik yalan söyler — her seti EDA ile örnekle.**
`newmindai/EuroHPC-Legal`: 43K satır, Apache-2.0, kusursuz görünüyordu. Örnekleme eşleşmeyen Q&A,
uydurma kanunlar ve Osmanlı dönemi içerik çıkardı → **reddedildi.** Bu, "EDA-doğrula" kuralının
doğuş anıdır. → [ADR-0005](#adr-0005)

**A1.3 Eğitimden ÖNCE veri-üstü kalite kapısı koy.** Modal'da bir epoch ~$11.5; veriyi
kanıtlamak 40 örnekte ~$0.01. v1 verisi kapıdan geçirildi: faithfulness **0.947 → (skorlayıcı
düzeltmesinden sonra) 0.984**. RAFT paketlemesinde 19.305 girdiden **635'i reddedildi** —
630'u *"uydurma alıntı: quote gold'da yok"*. Kapı olmasa bu 630 satır sessizce eğitime girerdi.
→ `#03`, [ADR-0002](#adr-0002)

**A1.4 Eval örneğini cherry-pick edip düzeltmek YASAK.** Düzeltme daima **sınıf düzeyinde**
yapılır (üretim filtresi veya skorlayıcı), tekil örnekte değil — yoksa metrik geçersizleşir.
Doğrulama yöntemi: düzeltme sonrası **gerçek hata hâlâ 0.0 kalmalı**; yalnız ölçüm gürültüsü
temizlenmeli. → [ADR-0002](#adr-0002)

**A1.5 Dış rapor iddialarını modülü import ederek doğrula.** Bir dış agent *"filtreyi çalıştırdım,
%3 kaçak var"* dedi. Gerçek `usable()` import edilip 40K ham veride koşuldu: kaçak **%0**, önerilen
"fix" **no-op**. İddia fabrikasyondu. → `#05`, [ADR-0009](#adr-0009)

**A1.6 Grounded veride değerli olan cevaplar değil, soru↔madde eşleşmesi.**
`grounded_qa`'nın *cevaplarıyla* düz SFT abstention'ı yok etti (A2.1). Ama aynı setin soru↔gold
eşleşmesi RAFT paketlemesinin ve tuzak üretiminin tohumu oldu. → `data/README.md`

**A1.7 Tercih verisinde `rejected` modele özgüdür.** Mevcut `rejected` satırları 12B'nin **gerçek
fabrikasyonları.** Yeni base'de olduğu gibi kullanmak *başka bir modelin hatalarını* öğretir —
yeniden hasat edilir (`scripts/gen_v3_rejected.py`).

## A2. Eğitim davranışı — hattın merkezi bulgusu

**A2.1 ⭐ Düz SFT abstention'ı YOK EDER.** Grounded SFT sonrası TRAP red oranı **0.741 → 0.000**.
Grounding kazanılırken "bilmiyorum deme" siliniyor. → `#07`

**A2.2 ⭐⭐ Grounding-Abstention paradoksu.** İkisi antagonist. v2c, M2'yi (yanlış-kaynak reddi)
düzeltmek için eğitildi; sonuç: M2 = **0.407** (kapı 0.90) *ve* M1 **0.920 → 0.832** regresyon →
**tur REDDEDİLDİ.** Ders: SFT coverage kazandırır (over-refusal↓) ama **near-miss ayrımını bozar**;
near-miss abstention **SFT-tek-başına çözülemez.** → `#24`, [ADR-0014](#adr-0014)

**A2.3 ⭐ Ardışık tur unutma üretir — ve kayıp habersiz olur.** v3 (ORPO, v2b-continuation)
M1'i **0.737 → 0.881**'e çıkardı (base 0.662'yi de geçti) ve M2'yi **0.346 → 0.593** onardı;
**ama** M2 base'in altında kaldı (0.593 < 0.704) ve **M2b 0.96 → 0.529 çöktü.**
→ `#32`, [ADR-0015](#adr-0015)

**A2.4 ⭐ Abstention tek beceri değil, bir AİLE.** v3'ün M2b çöküşünün kökü teşhis edildi:
ORPO'nun öğrettiği muhakemeli-red şablonu *"kaynakları değerlendir → en ilgilisini SEÇ"* adımını
içeriyordu. M2'de (tek yanlış kaynak) doğru; M2b'de (çok distractor, doğrusu yok) model
*"hiçbiri değil → reddet"* yerine en yakın distractor'ı seçip uyduruyor — 34 geçerli tuzağın
16'sında, birebir aynı örüntüyle. **Tek-aile preference eğitimi komşu aileyi bozabilir.**
→ [ADR-0015](#adr-0015)

> **A2.1–A2.4 yeni hattın iç iddiasının doğduğu yerdir:** çatışan becerileri *zaman içinde*
> (ardışık eğitim) değil *ağırlık uzayında* (task-vector merge) çözmeyi denemek. → `TASARIM.md` §1.2

**A2.5 SFT üslup öğretir, bilgi değil.** Register/atıf formatı SFT ile hızla kazanılıyor
(register-proxy **1.000**'e oturdu ve turlar boyunca orada kaldı); doğruluk ve güncellik RAG'in işi.
Kanıt: kör modda v1 ≈ base (0.300 vs 0.225, CI çakışık) → FT kanun gömmüyor.
→ `#09`, `#17`, [ADR-0010](#adr-0010), [ADR-0012](#adr-0012)

**A2.6 ORPO grounding'i bozmaz — yükseltir.** SFT-terimi (chosen grounding) + preference birlikte
forgetting yapmadı: nll 7.65 → 2.96, margin −0.31 → ~0, M1 yükseldi. → `#30`, [ADR-0015](#adr-0015)

**A2.7 Replay katastrofik unutmayı bastırır.** Genel TR replay havuzu eğitim setine %3-20 oranında
karıştırılır (hukuk sızıntısı regex'le elenmiş). → `#15`, `#30`

## A3. Değerlendirme — ölçüm aracının kendisi yanıltır

**A3.1 ⭐ KÖR test artefakt üretir.** Kaynak verilmeden ölçülen faithfulness **0.52**; madde
verilince **0.97**. Kaynak yokken "kaynağa sadakat" ölçmek **tanımsızdır** — sabahki ölçüm hatasıydı,
CANON'da A1 kör modda hiç raporlanmaz. → `#06`, [ADR-0011](#adr-0011)

**A3.2 ⭐ Eval-mirror şart.** Eğitimde uygulanan chunk kırpması (900 char) eval'de **birebir**
uygulanmalı; yoksa model eğitildiğinden uzun bağlamla ölçülür = haksız kıyas. Uzun-madde kırpması
%11.6 → %0.03. → `#15`

**A3.3 Eval dağılımı = deployment dağılımı.** Her SFT hedefi için bir mod olmalı. v2b RAFT ile
1 gold + 4 distractor eğitilirken eval yalnız temiz oracle veriyordu → *öğretilen beceri
ölçülmüyordu.* Mod matrisi bu ilkeden doğdu. → [ADR-0013](#adr-0013)

**A3.4 Hard-negative dağılımını eval ile eşle.** Eğitim tuzaklarının eval dağılımına kapsaması
**%6.6 → %66.3**'e çıkarıldı. Eşleşmeyen dağılım, öğrenilen beceriyi ölçülemez kılar. → `#25`

**A3.5 Framing sonucu belirler.** Aynı soru "tek kaynak + sıkı istem" (oracle) ile "çok kaynak +
red teşviki" altında **taban tabana zıt** davranış üretiyor: birincisi fabrikasyonu tetikliyor
(v2b fab = 0.654), ikincisi over-abstain yapıyor. Eval'in hangi framing'i kullandığı bir detay
değil, **sonucun kendisi.** → `#26`

**A3.6 Aşırı-red de bir patoloji.** M2 = 1.000 iyi haber değil; hedef **korunmuş grounding ile
birlikte** ~0.8-0.9 bandı. Her şeyi reddeden model kullanışsızdır. → `#31`

**A3.7 Ana metriği conditional yapma.** Payda = tüm sorular; "yalnız cevaplananlarda doğruluk"
over-refusal'ı gizler. Coverage ayrı raporlanır. → [ADR-0011](#adr-0011)

**A3.8 Eksenleri tek skora ezme.** Groundedness (kaynağa sadakat) ve correctness (gerçeğe uygunluk)
**dik eksenler** — literatür ayrı raporluyor (ALCE, RAGBench-TRACe, Wallat *"Correctness is not
Faithfulness"*). Ortalamak zıt sinyalleri siler. → [ADR-0011](#adr-0011)

**A3.9 Hakem aynı aileyse self-preference giderilmez.** Cross-judge **cross-family** olmalı;
gpt-4o-mini ↔ gpt-4o aynı ailedir ve sorunu kapatmaz (Wataoka). → [ADR-0011](#adr-0011)

**A3.10 Red-tespit regex'i kalibre edilmeli.** Regex tek bir model ailesinin çıktısına göre
yazılmışsa diğerlerinin reddini eksik sayar → onların skorunu düşürür → **bizim lehimize kayar.**
Ölçüm aracının kendi modeline kalibre olması, savunmada bulunması en kolay hatadır.

**A3.11 n=40/35 pilot ölçektir.** Fark testi için sınırda, eşdeğerlik (parite) iddiası için
yetersiz. Paper cetveli daha büyük. → [ADR-0011](#adr-0011), [ADR-0017](#adr-0017)

## A4. Operasyonel tuzaklar — hepsi **sessizce** başarısız olur

> Bu bölümün ortak özelliği: hiçbiri hata vermez. Koşu tamamlanır, çıktı üretilir, sayı raporlanır —
> ve yanlıştır.

**A4.1 ⭐ Modal'da `spawn()` kullan, `remote()` değil.** `remote()` eğitim bitene kadar bekleyen bir
client bırakır; WSL/PC/IDE kapanışı ona **SIGTERM** yollar, modal client bunu graceful shutdown sayıp
Modal'a **cancel** gönderir. `--detach` tek başına yetmez (bekleyen client hâlâ var). Doğrusu
`spawn()` + `--detach`. Bu ders **4 koşu ve ~$5 yakarak** öğrenildi. → [ADR-0008](#adr-0008)

**A4.2 ⭐ Şablon render'ını GÖZLE doğrula.** minja bir şablon dalını (`enable_thinking`) yanlış
render etti → model **durmadı**, girdiyi tekrarladı → bir CANON koşusu sessizce çöpe gitti.
**Her yeni base'de `/apply-template` çıktısına bakılır.** → `#38`

**A4.3 ⭐ Turn işareti maskelemesi.** `train_on_responses_only`'ye yanlış turn işareti verilirse
**hiçbir şey maskelenmez**, loss tüm diziden akar, eğitim sessizce bozulur. `train_sft.py` artık
işaretleri render'a karşı **assert ediyor**. → [ADR-0026](#adr-0026)

**A4.4 Batched üretimde pad token'ı önemli.** Left-pad ile batched generation'da `eos` ile doldurmak
baş-token mojibake üretiyordu (batch=8'de **%26**, tekilde %0). Gerçek `<pad>` (id 0) ile temiz. → `#26`

**A4.5 Sessiz veri bozukluğu smoke ile yakalanır.** `gold_text` alanına provenance-tag yazılmıştı;
hata vermiyordu, smoke koşusu yakaladı. **Her veri üretiminden sonra küçük bir smoke.** → `#14`

**A4.6 Kuantizasyon yarıda kesilebilir ve dosya "var" görünür.** Bir GGUF 666 tensörün 4'ünde
kesilmişti; 70 MB dosya diskte duruyordu. `setup_llamacpp.sh` artık boyut kapısı uyguluyor.

**A4.7 gitignore satır-sonu yorum desteklemez.** `path/ # açıklama` yazılırsa `#` ve öncesi desenin
parçası olur ve kural **sessizce çalışmaz.** 153 MB gereksiz dosya bu yüzden sızdı. → `data/README.md`

**A4.8 Bağlam kaydırma (context shift) groundedness'ı sessizce boşaltır.** llama.cpp varsayılanı,
bağlam dolunca en eski token'ları atıp devam eder. RAG'de bağlamın başında **getirilen maddeler**
durur; shift onları atar, model kaynağı görmeden cevap üretir ve **hiçbir hata çıkmaz.** Kural:
`--no-context-shift` + harness'ta bağlam bütçesi kontrolü — sığmayan girdi **kesilmez, reddedilir.**
→ [ADR-0023](#adr-0023)

**A4.9 Modal image'da resolver'ı açma.** `pip_install_from_requirements(..., extra_options="--no-deps")`
şart; lock tam-çözülmüş düz liste, resolver açılırsa unsloth'un `transformers` metadata kısıtı çakışır.
→ [ADR-0004](#adr-0004)

## A5. Metodoloji — paper'ı ayakta tutan alışkanlıklar

**A5.1 Kapı eşikleri veriyi görmeden yazılır.** Sonradan yazılırsa çıkan sonuç rasyonalize edilir.
v2 stratejisi ön-kayıtlıydı: karar kuralları pilot ÖNCESİ yazıldı, pilot hangi dalı ateşlerse o
uygulandı. → [ADR-0012](#adr-0012)

**A5.2 Negatif bulgular birinci sınıf.** v0'ın çöküşü, "SFT abstention'ı bozar", v2c'nin reddi,
v3'ün M2b regresyonu — bunlar kayıp değil, paper'ın **K3 damarı.** Reddedilen tur da tam rigorla
kaydedilir.

**A5.3 Negatif bulguyu literatüre yanlış bağlama.** *"SFT abstention'ı bozar"* bulgusu yayınlı
FT-harm literatürünün **replikasyonu değil**: onlar abstention-odaklı tuning'den **over**-refusal
belgeliyor, bizimki generic-SFT'den **under**-refusal — zıt yön. Yanlış atıf, özgün bulguyu
başkasının tekrarı gibi gösterir. → [ADR-0011](#adr-0011)

**A5.4 Karar eski bir belgeyle çelişiyorsa, çelişkiyi HER İKİ yerde işaretle.** Sessizce üzerine
yazma. Eski gerekçe yanlış çıksa bile *neden öyle düşündüğümüz* paper malzemesi.

**A5.5 Süperseded ≠ silinmiş.** [ADR-0021](#adr-0021)'in base gerekçesi düştü ama içindeki ölçülmüş
analiz (QAT zinciri, bağlam tavanı, KV matematiği) yeni base seçiminde **kriter listesi** olarak
hâlâ çalışıyor.

**A5.6 Kategori farkı olan modelle "geçtim" iddiası kurma.** Mecellem bir CPT foundation base,
asistan değil. İnce-ayarlı asistanın onu register'da geçmesi beklenen şeydir — korkuluk dövmek olur.
→ [ADR-0016](#adr-0016), `#31`

**A5.7 Yanlış sınavda düşük not "model kötü" demek değil.** İngilizce/US common-law benchmark'ları
(BigLaw, LegalBench) TR medeni-hukuk modelinde **yorumlanamaz.** → [ADR-0016](#adr-0016)

**A5.8 Sunk cost'u sıfırlayarak yeniden karar verebilmek.** Base kararı bir kez "bugün sıfırdan
seçiyor olsaydık?" sorusuyla yeniden açıldı; 5 koşu ve ~35 judge hücresi yok sayıldı. Karar
değişmedi ama **gerekçe düzeldi** — ve kendi eski iddiam ("18× KV avantajı") çürütüldü.
→ [ADR-0021](#adr-0021)

---

# BÖLÜM B — Karar kaydı (ADR-0001 … 0026)

> Her bölüm: karar · elenen alternatifler · sonuç · yeni hattaki statü.
> **🟢 taşınıyor** = ilkesi yeni hatta geçerli · **🔵 tarihsel** = 12B'ye özgü, dersi Bölüm A'da ·
> **⚫ düştü** = yerini yenisi aldı.

<a id="adr-0001"></a>
### ADR-0001 — Groundedness ana eval metriği · 🟢 taşınıyor

**Karar.** Ana eval kapısı = **groundedness / kaynağa sadakat**: FactScore (claim-level: cevabı
atomik iddialara böl → her birini kaynağa karşı SUPPORTED/CONTRADICTED/NOT_IN_SOURCE etiketle) +
ALCE atıf precision/recall + **wrong_ref_rate** (doğru kanun yanlış madde — hukuken en tehlikeli
hata). **Sadelik model kapısı DEĞİL** → app katmanına. **İnsan-κ DESCOPE** (annotatör yok) →
yerine hakem-uyumu + tekrar kararlılığı.

**Elenenler.** *Muhakim'i ana kapı yapmak* → kısa-sade-doğru cevapları yanlı cezalıyor (elle
doğrulandı) — bu körlük K3'ün otomatik kanıtı, ikincil sinyal olarak kalır. *GPT-4o-mini serbest
1-10 puanı* → gürültülü, kalibresiz. *Avukat-anotasyonlu mutlak doğruluk* → kapasite yok; ayrıca
iddia "kaynağa sadakat + göreli üstünlük", mutlak hukuki geçerlilik değil.

**Sonuç.** faithfulness 0.97 / hallucination 0.03 / wrong_ref 0.04. **Dürüstçe kabul edilen iki
açık:** hakem self-preference (üreten ve yargılayan aynı aile) ve insan altın-standardı yokluğu →
sayılar **göreli**, mutlak değil.

**Yeni hatta:** çekirdeği [ADR-0011](#adr-0011)'e taşındı; insan-κ descope kararı ve iki açık
`TASARIM.md` §3.3'te dört katmanlı hakem savunmasıyla karşılanıyor.

<a id="adr-0002"></a>
### ADR-0002 — v1 verisi: eğitim-öncesi kalite kapısı · 🔵 tarihsel (ders: A1.3, A1.4)

**Karar.** Eğitimden önce veri-üstü groundedness kapısı: train örneğini gerçek madde metniyle join
et → skorla. Geçme eşiği **faithfulness ≥ 0.80** + sistematik bozukluk yok. Eval örneğini
cherry-pick edip düzeltmek **yasak**; düzeltme sınıf düzeyinde.

**Sonuç.** faith 0.947 (kapı geçildi). Düşük uçtaki 3 örnek **üç ayrı sınıf** çıkardı: gerçek veri
hatası (~%2.5, izole) · bulanık aktarım (sınırda) · **skorlayıcı artefaktı** (meta-iddialar olgu
sayılıyordu). Üçüncüsü prensipli bir kuralla çözüldü → faith **0.947 → 0.984**. Doğrulama: artefakt
örnekleri 0.5 → 1.0 çıkarken **gerçek hata 0.0'da kaldı** — fix hatayı maskelemiyor.

<a id="adr-0003"></a>
### ADR-0003 — Base model: Gemma 4 12B · ⚫ düştü → [ADR-0026](#adr-0026)/0027

**Karar.** Base = Gemma 4 12B QAT-unquantized. Hat: QLoRA (NF4) → bf16 merge → Q4_0 GGUF → 8 GB
son kullanıcı. 8 GB hedefi **quantization'la** sağlanır, eğitimi 4B'ye kısarak değil.

**Elenenler.** *Qwen3.5-4B* → 12B'nin kapasitesi üstün, Q4_0 ile zaten 8 GB'a sığıyor → küçük
modelin tek avantajı ortadan kalkıyor. *Gemma 4 26B A4B MoE* → erişilebilirlik kısıtını ihlal eder.
*Encoder-ekli multimodal yığın* → gereksiz.

**⚠️ Gerekçe kayması, kayda geçti:** multimodal/OCR bu listede **yoktur ve olmamalıdır** — yalnız
reddedilen alternatifi gerekçelendirirken geçer, bir **seçim nedeni değildir.** `TEKNIK_PLAN` ve
eski `VISION` bunu gerekçeye kaydırmıştı; düzeltildi.

<a id="adr-0004"></a>
### ADR-0004 — Eğitim altyapısı: Modal serverless · 🟢 taşınıyor

**Karar.** Gerçek eğitim Modal'da (A100 40GB); yerel makine prototip/smoke + **eval** + veri
üretimi için. `modal_train.py`, `train_sft.py`'a **dokunmadan** onu subprocess ile sarar.

**Elenenler.** *Colab/Kaggle/RunPod* → Modal saniye-başı ödeme + kalıcı volume (model cache) +
kod-olarak-altyapı. *H100* → QLoRA compute-bound değil. *L4* → aynı $/epoch, ~3× yavaş.
*Eval'i de Modal'da koşmak* → GPU saati israfı; eval yerelde $0.

**Sonuç.** ~11 sn/step, 1 epoch ≈ 5.5 saat ≈ ~$11.5. Image kritik detayı: bkz. A4.9.

**Yeni hatta:** ilke aynı; ama tek boyut noktası ~4B olduğu için koşuların çoğu **yerelde, $0**
(ADR-0028). Modal artık zorunlu değil — CP3 smoke'unun `s/it` ölçümü karar verir.

<a id="adr-0005"></a>
### ADR-0005 — Veri stratejisi · 🟢 taşınıyor

**Karar.** Yalnız açık/kamu kaynak (Mevzuat.gov.tr, Resmi Gazete, Yargıtay açık portal, Apache-2.0
HF setleri) · **PII maskele** · her seti güvenmeden önce **EDA ile örnekle-doğrula** (sert kural) ·
eksik veri = **grounded sentetik üretim** (gerçek madde → LLM → doğrula) · canlı kaynak =
`bedesten.adalet.gov.tr` (auth-free, **TR IP şart**).

**Elenenler.** *EuroHPC-Legal* → EDA çöp gösterdi (A1.2). *v0'ın 32K forum verisi* → doğruluğu
düşürdü + kaynaksız olduğu için **puanlanamıyordu bile.** *Osmanlı/Mecelle içerik* → kapsam dışı;
scope = yürürlükteki TC mevzuatı. *Yerel modelle sentetik üretim bake-off'u* → gereksiz.

<a id="adr-0006"></a>
### ADR-0006 — Akademik hedef: sistem paper'ı · ⚫ düştü → [ADR-0017](#adr-0017)

**Karar (o gün).** Ana = sistem paper'ı; benchmark yan iş. Katkılar: K1 uçtan-uca ablasyon ·
K2 verimlilik · **K3 erişilebilirlik↔doğruluk gerilimi.**

**Neden düştü.** "Sistem kurduk" bir *inşa* iddiası, ölçülebilir bir *bilimsel* iddia değil.
Ana iddia maliyet-normalize pariteye taşındı.

**Ayakta kalan iki çıkarım.** (a) *"Benchmark headline değil"* — yeni çerçevede de benchmark
birincil katkı değil, **parite iddiasının ölçüm altyapısı.** (b) *"Rakibin benchmark'ında geçmek
anlamsız → kendi terazimizde ölç"* — aynen geçerli.

<a id="adr-0007"></a>
### ADR-0007 — Repo & lisans: private + proprietary · 🟢 taşınıyor

**Karar.** Repo private + proprietary; ticari haklar sahibinde. Ağırlıklar + model kartı ileride
opsiyonel HF yayını. **Akademik yayın kapısı açık** → rigor baştan korunur.

**Elenenler.** *Proje için OSS/Apache-2.0* → ticari hakları korumak öncelik. ⚠️ **Base modelin
Apache-2.0 olması projeyi OSS yapmaz** ama **atıf zorunludur.** *Tam kapalı, paper yok* → yayın
opsiyonu değerli, maliyeti sadece disiplin.

<a id="adr-0008"></a>
### ADR-0008 — Modal: fire-and-forget `spawn` · 🟢 taşınıyor

Bkz. **A4.1** — ders tam metniyle orada. Ek dayanıklılık: `save_steps=200` + `save_total_limit=3`
ara checkpoint + `get_last_checkpoint` oto-resume + periyodik volume commit → spawn tutmasa bile
checkpoint'ten devam edilebilir. **Reproducibility kuralı:** uzun GPU koşuları daima `spawn` ile.

<a id="adr-0009"></a>
### ADR-0009 — Filtre doğrulandı, dokunulmadı · 🔵 tarihsel (ders: A1.5)

**Karar.** (1) Filtreye **dokunulmaz** — önerilen "fix" no-op + yanlış-pozitif riski taşıyor.
`head`-only mülga kontrolü **kasıtlı doğru**: gövde ortasındaki "mülga" çoğunlukla başka maddeye
atıf ya da kısmen-mülga (örn. bir maddenin 6-7. fıkraları mülga ama 1-5 canlı) — bunları elemek
iyi kaynağı çöpe atmaktır. (2) Kör tarama yerine **hedefli audit**: 404 şüpheli kaynak işaretlendi.

<a id="adr-0010"></a>
### ADR-0010 — Birincil register = uzman · 🟢 taşınıyor

**Karar.** Birincil kitle = **uzman (avukat/hukukçu)**; çıktı hassas, atıflı, uzman register'ında.
**Vatandaş sadeleştirmesi = app-layer prompt modu**, model eğitim hedefi **değil.**
Correctness/grounding **RAG'den** gelir; SFT bilgi gömmez, davranış öğretir.

**Neden.** İki ampirik bulgu eski çerçeveyi çürüttü: v0'da sade/kısa cevaba doğru eğitim doğruluğu
düşürdü; v1'de (vatandaş register'ı) oracle modda v1 ≈ base, tek kazanım kozmetik atıf formatıydı
ve abstention çöktü. **Sade dil, doğru cevabın sunum katmanıdır — eğitim hedefi değil.**

**Elenenler.** *Vatandaş register'ını model hedefi tutmak* → plainness'i ağırlığa gömmek
correctness'i bozuyor. *İki ayrı model* → tek grounded model + prompt-zamanı sadeleştirme daha ucuz.
*Ayrı sadeleştirici model* → ertelendi (app katmanı).

<a id="adr-0011"></a>
### ADR-0011 — CANON eval metodolojisi · 🟢 taşınıyor (0027 ile **genişletildi**)

**Karar — dört eksen, AYRI raporlanır.** A1 groundedness (yalnız kaynak verili modda; **kör modda
TANIMSIZ**) · A2 correctness (**referans = gerçek madde metni**, sentetik gold değil) ·
A3 abstention · A4 format. A1∧A2 türetilmiş **ikincil diagnostik**, manşet değil.
Sabitler: **seed 3407**, paired (aynı sorular), mod-stratifiye hücreler.

**Elenenler.** *A1+A2'yi tek skora ezmek* → dik eksenler (A3.8). *A2 referansı = sentetik gold* →
"GPT'ye benzedi mi" ölçer. *Kör modda A1* → tanımsız. *Conditional accuracy ana metrik* →
over-refusal'ı gizler (A3.7).

**Literatür doğrulaması dört düzeltme getirdi.** A1∧A2 manşetten indirildi · abstention çöküşü
**özgün K3 bulgusu, replikasyon değil** (A5.3) · cross-judge **cross-family** olmalı (A3.9) ·
bootstrap CI + paired test eklendi.

**Yeni hatta:** modlar ve sabitler aynen korunuyor; ADR-0027 üzerine **DEV/TEST ayrımı** ekledi —
merge hiperparametreleri DEV'de seçilir, dondurulmuş CANON nihai raporda bir kez görülür.

<a id="adr-0012"></a>
### ADR-0012 — v2 stratejisi (ön-kayıtlı) · 🔵 tarihsel (ders: A5.1)

**Yöntem.** Karar **kuralları** pilot ÖNCESİ yazıldı: "kör modda v1 ≈ base çıkarsa Ürün A
(doğruluk RAG'dan), v1 > base çıkarsa Ürün B (bilgi ağırlığa gömülü)". Pilot sonrası yorumu eğip
*"zaten böyle diyecektim"* denemesin diye.

**Pilot doldurdu.** Kör A2: base 0.225 vs v1 0.300, CI çakışık → **v1 ≈ base → Ürün A.**
Üstelik v1 oracle'da bile base'den kötü → SFT **net-negatif.** TRAP'te v1 cevaplarının %88'i
yanlış → halüsinasyon baskın → yüksek hedge dozajı dalı.

**Sonuç.** SFT'nin işi dar: **davranış** (grounding + abstention + format), bilgi değil.
[ADR-0010](#adr-0010) doğrulandı.

<a id="adr-0013"></a>
### ADR-0013 — Eval mod matrisi · 🟢 taşınıyor

**Karar — 5 eval modu (deployment durumları).** M1 gold+distractor (**manşet**) · M2
distractor-only = TRAP · M3 boş bağlam · M4 temiz oracle (**iyimser tavan, manşet DEĞİL**) ·
M5 kör (parametrik ezber). Eksenlere **A-register** eklendi.
*(Sonradan M2b — çok-kaynak-gold-yok — altıncı mod olarak katıldı.)*

**İlke.** *Eval dağılımı = deployment dağılımı + her SFT hedefi için bir mod.* (A3.3)

**Elenenler.** *M4'ü manşet tutmak* → deployment'tan kolay, distractor-robustluğunu gizler.
*Distractor'ı rastgele örneklemek* → gerçek retriever **hard-negative** döndürür; rastgele eval'i
kolaylaştırır. *Register'ı A4'e gömmek* → format ≠ register. *E-set'i TRAP'e katmak* → farklı
tetik (yanlış kaynak ≠ kaynak yok), ayrı raporlanmalı.

<a id="adr-0014"></a>
### ADR-0014 — v2c RED kararı + K3 · 🔵 tarihsel (ders: A2.2)

**Karar.** v2c **REDDEDİLDİ** — iki bağımsız kapı birden düştü (M2 0.407 « 0.90 *ve* M1 0.832 <
0.904 regresyon). **K3 negatif bulgusu kabul edildi:** *"near-miss reddi ucuz SFT counterfactual
ile öğretilir"* hipotezi **çürük.**

**Fix yönü bilinçli AÇIK bırakıldı** ve altı seçenek havuzu kaydedildi: P1 tercih-optimizasyonu
(ORPO/DPO) · P2 knowledge-boundary hizalaması (DTA) · P3 contrastive/hard-negatif SFT ·
P4 abstention/calibration · P5 RAFT/loss-masking (**⚠️ uyarılı**: RAFT'ın no-golden kolu abstain
değil ezber öğretiyor, fabrikasyonu besleyebilir) · P6 FT-dışı kaldıraçlar (veri kompozisyonu,
eval gücü, tuzak kalitesi).

**Ortak kısıt.** Hiçbir yöntem near-miss ile off-topic ayrımını *otomatik* yapmıyor → hepsi
kendi negatif dağılımını kurmayı gerektiriyor. **Bu bir veri-kompozisyon sorusu, salt-algoritma
değil.**

<a id="adr-0015"></a>
### ADR-0015 — v3 ORPO kapı kararı: KISMİ · 🔵 tarihsel (ders: A2.3, A2.4, A2.6)

**Karar.** v3 **teslim adayı değil** (M2 base-altı + M2b regresyonu) **ama v2c gibi RED de değil —
KISMİ.** K3 büyük ölçüde tersine çevrildi ve grounding yükseldi. P1 hipotezi (ORPO düz-SFT'den iyi
öğretir) **doğrulandı**, sadece base-üstüne taşımadı.

**Tam skorkart (12B protokolü).**

| eksen | base | v2b | v2c | **v3** |
| :--- | ---: | ---: | ---: | ---: |
| M1 grounding | 0.662 | 0.737 | 0.681 | **0.881** |
| M4 oracle | 0.978 | 0.968 | 0.974 | **1.000** |
| M2 near-miss red | 0.704 | 0.346 | 0.407 | **0.593** |
| M2b çok-kaynak ıska | 1.0 | 0.96 | 0.973 | **0.529** |
| M3 boş bağlam | 1.0 | 1.0 | 1.0 | **1.000** |
| M5 (anti-hedef) | 0.225 | 0.175 | 0.125 | **0.075** |
| register | 1.0 | 1.0 | 1.0 | **0.975** |

Genelleme: xkanun base 0.968 / v3 0.656 · ood base 0.889 / v3 0.483.

**Elenenler.** *v3'ü teslim kabul et* → M2b regresyonu prod riski (çok-kaynak RAG asıl mod).
*Teşhissiz hemen v4 yaz* → kör atış; önce M2b'nin kökü bulundu (forced-source-selection).
*1-epoch checkpoint'i tercih* → final M2 daha iyi.

**Yasak olarak kaydedildi:** *"v2b-SFT ile düzeltme"* — K3 tuzağı; **abstention hep preference'ın
işi.**

<a id="adr-0016"></a>
### ADR-0016 — Dış benchmark kapsamı · 🟢 taşınıyor

**Karar.** BigLaw-Bench + LegalBench **koşulmaz**, yalnız Related Work atfı (A5.7) · frontier
kıyası **kendi canon setimizde** · Muhakim **cite-only, hakem olarak koşulmaz** (cross-family
zaten var + reddettiğimiz sete bağlı = kalibrasyon kirliliği) · `alibayram/turkish_mmlu` **dışarıda**
(CC BY-NC + telif beyanı = poison).

**Katkı konumlaması.** Üretken TR hukuki cevabın grounding/abstention/citation kalitesini ölçen
**tanınmış benchmark YOK** (mevcut TR stack retrieval/embedding'e odaklı) → **bu boşluk katkımız.**

<a id="adr-0017"></a>
### ADR-0017 — ⭐ Tez çerçevesi: maliyet-normalize parite · 🟢 taşınıyor (0027 ile **teyit**)

**Karar.** Ana iddia = **maliyet-normalize parite**: *dar bir domainde SLM+harness, kapalı ticari
modellerin dağıtım sınıfına maliyet-normalize paritede ne kadar yaklaşır — ve bunun ne kadarını FT,
ne kadarını harness sağlar?* Ölçüm iki boyutlu: **kalite × maliyet** (Pareto).
Cümle: *"bu maliyetle, buraya kadar çıkıyoruz."*

**Parite bir eşdeğerlik iddiasıdır** (D ≈ B), fark iddiası değil — ve eşdeğerlik testi fark
testinden **daha çok örnek ister.** Bu yüzden benchmark **birincil katkı değil, iddianın ön koşulu.**

**Elenenler.** *Başka aileye geçiş* → confounded (hem aile hem boyut değişir) + koşuların
tekrarı. *Çok-base replikasyon kolu* → kapsam dışı; sonuç: **dış geçerlilik kapatılmayan sınır.**
*CPT* → ayrı bir tez; kaynak gelse bile hayır.

**⚠️ Bu ADR'nin "base SABİT" kısmı [ADR-0026](#adr-0026) ile düştü.** Çerçevenin kendisi ayakta.

<a id="adr-0018"></a>
### ADR-0018 — 8 GB = soft gate, eğri · 🟢 taşınıyor (0027 ile **somutlaştı**)

**Karar.** ≤8 GB **tercih bandı**, yasak değil. Aşan yapılandırmalar (12/16/24 GB) da raporlanır,
erişilebilirlik ekseninde **kayıpla**. 8 GB, maliyet-performans **eğrisi** üzerinde işaretli bir
bant — eğrinin sonu değil. **Boyut/bellek bir karar değil ölçümdür.**

**⚠️ Bu ADR'nin 3. maddesi ("darboğaz ağırlık değil KV-cache") 12B için ölçümle YANLIŞ çıktı:**
128K'da KV = 1.16 GB vs ağırlık ~6.5 GB → KV, ağırlığın yalnız **%18'i.** Darboğaz **ağırlık.**
Kararın kendisi (soft gate + eğri) ayakta; TurboQuant'ın rolü *bellek çözücü*den **bağlam tavanı
kaldıracı**na döndü. **Ders: bu oran base'e göre değişir, asla varsayılmaz — ölçülür.**

**Yeni hatta:** eğri = **iki boyut noktası** (birincil + karşıtlık).

<a id="adr-0019"></a>
### ADR-0019 — Faz sırası istisnası · 🟢 taşınıyor

**Karar.** *"Faz 1 bitmeden Faz 2'ye atlama"* kuralı **tek bir istisnayla** esnetilir: Faz 2'nin
**retriever + atıf doğrulayıcı + red kapısı** dilimi **teze dahildir** — çünkü maliyet-normalize
parite iddiası harness olmadan kurulamaz (adil kıyas = "rakip + aynı harness").

**Adalet kuralı (pazarlıksız).** Harness tüm öznelere **birebir aynı** uygulanır. Sadece kendi
modelimize verirsek tez ölür.

*(Graf yasağı [ADR-0022](#adr-0022) ile daraltıldı.)*

<a id="adr-0020"></a>
### ADR-0020 — Rakip seti + tavan referansı · 🟢 taşınıyor

**Karar.** **Rakipler = kapalı ticari, dağıtım sınıfı** (ölçekte gerçekten koşulan katman — kimse
her sorguya en üst-ucu ödemiyor). **Tavan referansı** (en güçlü modeller) rakip değil, grafikte
**tek referans çizgisi**; parite iddia edilmez, ama ölçülmezse *"neden en güçlüsüyle
kıyaslamadınız?"* savunmada açık kalır. **Terminoloji: "frontier" denmez, maliyet bandı denir.**
**Tarihli snapshot pin zorunlu** (tez rampası ≥2 yıl).

**Elenenler.** *Açık modelleri rakip saymak* → rakip tanımı = kapalı ticari lablar; "açık modeli
yerelde koşsak yetmez mi" sorusunu **base + Mecellem hücreleri zaten cevaplıyor.**
*Mecellem'i ızgaraya sokmak* → cite-only, yeni koşu yok, kategori farkı (A5.6).

<a id="adr-0021"></a>
### ADR-0021 — Base teyidi (ölçülmüş gerekçe) · ⚫ düştü → [ADR-0026](#adr-0026)

**Karar (o gün).** Base teyit — ama **gerekçeler ölçüldü ve biri düzeltildi.** Sunk cost
sıfırlanarak yeniden karar verildi (A5.8).

**Ölçülen gerekçeler.** (1) Resmî QAT Q4_0 checkpoint — maliyet iddiasının en kırılgan halkası
quantization kaybı, QAT onu garantiliyor. (2) 8 GB'da **bağlam tavanı 176.128 vs 90.982 token**
(~1.9×) — *"bandı biz değil kullanıcı seçer, kuyruğa tasarlanır."* (3) Mimari: 48 katmanın 40'ı
sliding attention → bağlamla büyümüyor. (4) **Asimetrik risk:** yanlış seçimin bedeli bir yanda
~1 GB boşuna ağırlık, diğer yanda *ürün çalışmıyor.*

**⚠️ Kendi iddiamın çürütülmesi, kayda geçti.** İlk sözlü iddia *"18× KV avantajı"* **yanlıştı** —
o rakam rakip ailenin **hibrit-öncesi** mimarisinden geliyordu; gerçek fark **2.5–3.7×**.
Karar değişmedi ama gerekçe doğru büyüklüğe indi.

**⚠️ İkinci düzeltme, kararı devirdi.** *"8 GB'a sığıyor"* iddiası **masaüstü yükünü saymıyordu.**
Kullanıcı itirazı: *"o PC'de illaki başka VRAM yiyen app olacak."* Haklı — 8 GB kartın 8 GB'ı
kullanıcıya ait değil; compositor + tarayıcı 0.5–1.5 GB yer. Sabit 6.97 GB → tipik masaüstünde
KV'ye ~0.03 GB kalır = kullanılamaz. **Düşen:** *mutlak* iddia. **Ayakta kalan:** *göreli* iddia.
Bu düzeltme küçültme kolunu açtı ve nihayetinde hattın emekliliğine giden yolu döşedi.

**Yeni hatta:** karar düştü, **ölçüm yöntemi ve kriter listesi kaldı** — QAT varlığı, gerçek
kullanımda ağırlık+KV toplamı, bağlam tavanı, asimetrik risk. Bunlar `TASARIM.md` §8'in
doğrulama kapısının atasıdır.

<a id="adr-0022"></a>
### ADR-0022 — Graf kapsamı · 🟢 taşınıyor (0027 ile **revize**)

**Karar.** *"Graph-RAG"* adı altında **iki farklı iş** var; [ADR-0019](#adr-0019) ikisini ayırmadan
yasaklamıştı. **(a) Yapısal/deterministik graf** (hiyerarşi + atıf ağı + mülga/değişik zincirleri,
parse ile, **LLM yok**) → **teze dahil, manşet konfigürasyon.** **(b) LLM-indeksli/çok-ajanlı
GraphRAG** → manşet dışı.

**Neden (a) içeride.** Zaten gerekiyordu (atıf doğrulamak "Kanun X Madde Y"yi bir yapıya karşı
çözmektir; **Türk mevzuatı zaten bir graf**) · maliyet iddiasıyla hizalı (marjinal ~0) ·
determinizmi korur · **bedava eksen: zamansallık** (mülga/değişik zincirleri CANON'da yok,
rakiplerin yapamadığı kulvar) · temiz ablasyon açar.

**Neden (b) dışarıda.** Sorgu başına ek çıkarım **doğrudan manşet metrikten düşer**; üstelik
adalet kuralı gereği rakiplere de verilecek → maliyet iki taraflı katlanır.

**⭐ Ve kapsam sınırının nasıl çizileceği ilkeye bağlandı.** Kullanıcı *"neden net çiviliyoruz,
flu bırakamaz mıyız?"* diye sordu. Cevap: flu sınır üç şeyi bozar — adalet kuralını çürütülemez
kılar, maliyet metriğini tekrar-üretilemez yapar, ön-kaydı delerek kale direğini kaydırır.
**Çözüm: flu sınır değil, etiketli ikinci nokta.** Tez zaten bir Pareto eğrisi; genişlemeler
**kendi maliyet etiketiyle ayrı bir nokta** olarak ölçülür, manşetin içine sessizce karışmaz.

**Ön-çalışma.** SAT-Graph RAG (hiyerarşik + zamansal + deterministik; Work/Expression ayrımı Türk
mevzuatına birebir oturuyor) · Citation Grounding (deterministik atıf grafı; halüsinasyonu
*var mı / bağlama uygun mu / o tarihte yürürlükte miydi* diye ayırıyor) · LegalGraphRAG
(= (b); SOTA iddiası var, **maliyet raporu yok**).

**Yeni hatta:** (b) *"kesin dışarıda"*dan **kapılı Katman-1 koluna** yumuşadı — iki eski itiraz
(air-gapped'i deler, non-deterministik) yeniden incelenince düştü; ayakta kalan itiraz
**halüsinatif kenar ucuza doğrulanamaz.**

<a id="adr-0023"></a>
### ADR-0023 — Dağıtım konfigürasyonu · ⚫ kısmen düştü (QAT'e özgüydü)

**Karar (o base için).** Saf Q4_0 (token_embd yükseltilmez — QAT tam Q4_0 için kalibre) +
flash-attention + **KV q8_0**. Dört kaldıraç, en önemlisinden: **harness GPU'ya girmez** (−1.06 GB,
*sığar/sığmaz farkı*) · saf Q4_0 (−0.23 GB) · flash-attention (−0.15 GB) · KV q8_0 (2.2× bağlam).

**Ölçüm doğrulandı:** projeksiyon 6.27 GB vs gerçek **6.26 GiB** (−0.2% sapma).

**⚠️ A4.8 (context shift) bu ADR'de bulundu** — dağıtım konfigürasyonunu incelerken ortaya çıkan,
groundedness'ı sessizce boşaltan tuzak. Red kapısına yeni bir görev ekledi: **sığmayan girdi
kesilmez, reddedilir.**

**CPU offload ilkesi.** Retriever/embedder CPU'ya → bedava. Model katmanı veya KV → yasak değil
ama **tezin para birimiyle ödenir**: üretim hızı düşer → GPU-saat başına daha az cevap → birim
maliyet artar → doğrudan parite metriğinden düşer. Rakip API'ler bu cezayı ödemiyor.

**Yeni hatta:** `--pure` Q4_0 **QAT'e özgüydü, taşınmaz** → QAT checkpoint'i olmayan base'de
**Q4_K_M** doğru varsayılan. Harness'ın GPU'ya girmemesi ve CPU-offload ilkesi **taşınıyor.**
**Ve işaretlenen delik açık kalıyor:** CANON bf16/NF4'te koşuyor, dağıtım artefaktı kuantize →
*ölçtüğümüz ≠ dağıttığımız*; en az bir hizalama koşusu gerekiyor.

<a id="adr-0024"></a>
### ADR-0024 — Hat emekliliği · 🟡 uygulandı, **kısmen süperseded → [ADR-0034](kararlar-0027-0044.md#adr-0034)**

**Karar — bölme çizgisi: base'e bağlı mı, değil mi.** Base'e bağlı artefaktlar (LoRA adaptörleri,
eval çıktıları, tur belgeleri, SCORECARD) arşive **taşınır, silinmez**; base'den bağımsız olanlar
(`data/`, `scripts/`, `knowledge/`) yerinde kalır.

> **⚠️ Süperseded (2026-07-28, ADR-0034):** *"taşınır, **silinmez**"* yarısı artık geçerli değil —
> `old-version-gemma4-12b/` ağacı repo'dan silindi. Gerekçe: kronoloji + dersler belgeleri
> damıtıldıktan ve repo dışı devir paketi (`~/code/hukuk-devir/`) kurulduktan sonra ağaç üçüncü
> kopyaya dönüşmüştü. **Bölme çizgisinin kendisi** (base'e bağlı / bağımsız) aynen doğru kaldı;
> değişen yalnız base'e bağlı tarafın nereye gittiği. Kurtarma: `git show a0575e6:…` + devir paketi.

**İki pazarlıksız kural.** (1) **`research_log/` ve `adr/` yerinde kalır** — *"makaleyi repo'dan
haftalar sonra yeniden kurabilmek"* garantisi kronolojik kayıt taşınırsa kırılır. Tarih
**kesintisiz akar**, yalnız artefaktlar ayrışır. (2) **`scripts/` sıfırdan yazılmaz** — eval
harness'ı 5 turda doğrulandı ve içinde **bulunmuş hataların düzeltmeleri gömülü** (gold sızıntısı,
mojibake fix, regex kalibrasyonu, A1 cevaplanan-only macro). Sıfırdan yazmak o hataları yeniden
bulmayı gerektirir.

> **Not (2026-07-24):** kural (1)'in `adr/` kısmı, kullanıcı kararıyla bu belge lehine değiştirildi
> — ADR'ler tek dosyada toplandı. `research_log/` kısmı **aynen yürürlükte.**

<a id="adr-0025"></a>
### ADR-0025 — Eval yolu: llama.cpp / GGUF · 🟢 taşınıyor

**Karar.** Eval üretimi Unsloth/NF4 yerine **llama.cpp + GGUF**, OpenAI-uyumlu HTTP üzerinden
(`llama-server`). Gerekçe: ölçülen artefakt dağıtılan artefakta yaklaşır, ve yerel ortam kırılganlığı
(Blackwell wheel'leri) eval yolundan çıkar.

**Yeni hatta rol değişimi:** bu karar artık aynı zamanda bir **base seçim kriteri** — llama.cpp
mimariyi desteklemiyorsa o base eval edilemez. `TASARIM.md` §8 doğrulama kapısının 1. maddesi.

<a id="adr-0026"></a>
### ADR-0026 — Base bir PARAMETRE · 🟢 taşınıyor

**Karar.** Hiçbir script'te base default'u **YOK**; tanımsızsa **erken hata** — yanlış modele
sessizce düşmek saatlerce süren bir koşuyu fark edilmeden çöpe çevirir. 33 nokta / 14 dosya
parametreleştirildi.

**Koşulsuz olan üç şey koşullu hale getirildi:** `llama-quantize --pure` (QAT'e özgüydü) ·
tokenizer yaması (o aileye özgüydü) · GPU seçimi (12B'ye göreydi).

**Sessiz-bozulma kapısı.** Turn işareti sabitleri repodaki **en tehlikeli bağımlılıktı** (A4.3).
Artık zorunlu argüman **ve render'a karşı assert ediliyor.**

**`data/` yönteme göre yeniden yapılandırıldı** — tur numarası (`sft_v2b`) yerine yöntem adı
(`raft`, `orpo_abstain`, `grounded_qa`): yeni hat "hangi tur" bilmez, "hangi yöntem" bilir.

---

# BÖLÜM C — Ham kayda giriş noktaları

**12B hattının tam sayıları:** [`docs/record/gemma4-12b-kronoloji.md`](../record/gemma4-12b-kronoloji.md)
(en kritik altı girdi `#02` kaynaksız veri · `#07` SFT abstention'ı yok etti · `#08` CANON'un doğuşu ·
`#24` Grounding-Abstention paradoksu · `#36` çerçeve değişimi · `#38` sessiz şablon tuzağı) ·
ham SCORECARD: `git show a19fc25^:old-version-gemma4-12b/record/SCORECARD.md`

⚠️ **Repo dışı devir paketi 2026-07-29'da silindi** ([ADR-0034](#adr-0034) üst notu): **LoRA
adaptörleri (v0/v1/v2b/v2c/v3) ve `RECETELER_12B.md` kalıcı kayıp** — kasıtlı, o hat emekli.
Tek kurtarma yolu **git geçmişi**; metin artefaktları orada tam.
