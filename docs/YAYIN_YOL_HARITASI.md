# Yayın yol haritası

> HakHukuk'tan iki hakemli makaleye ve yüksek lisans tezine giden proje planı. Checkpoint 1'in iş
> adımları, doğrulamaları ve kontrol listesi: [`ROADMAP_v1.md`](ROADMAP_v1.md). Eğitim ortamının
> kilitli değerleri:
> [`EGITIM_ORTAMI.md`](EGITIM_ORTAMI.md). Her aşama başlarken kendi uygulama planı yazılır
> (en çok bir canlı plan, [ADR-0056](adr/kararlar-0045-0063.md#adr-0056)); bu belgedeki kararlar
> F0'da karar defterine ADR-0089 ve sonrası olarak işlenir.
>
> "Tahmin" yazan sayılar kayıttaki koşu sürelerinden ve 2026-10-10 tarihli web fiyatlarından
> hesaplanmıştır; her bloğun ilk işi birim maliyeti küçük bir pilotla ölçmektir.

---

## 0 · Özet

| | **Checkpoint 1 — Makale 1** | **Checkpoint 2 — Makale 2 ve tez** |
| :--- | :--- | :--- |
| tarih | Eylül 2027 | yaz 2028 |
| soru | Çatışan iki beceriyi (temellendirme ↔ çekinme) tek modelde toplamanın en iyi yolu hangisi, sonuç temel modele göre değişiyor mu, ve hangi hükümler ölçüm düzeltmesine dayanıklı? | Doğrulanabilir ödülle RL, isabetsiz atıfı ve M2b'yi çekinmeyi ve düşünceyi bozmadan düzeltiyor ve düşünceyi hedefe hizalıyor mu? |
| yöntem | SFT + ORPO; ayrı kollar + ham TIES ↔ birlikte eğitim ↔ ardışık eğitim | GRPO, isabet terimli doğrulanabilir ödül |
| temel model | **Qwen3.5-4B ve Gemma 4 E4B, her biri 3 seed** | Checkpoint 1'in **kazananı** |
| çıktı | Makale 1 gönderime hazır · uygulama kazananla güncel · tez malzemesi tamam | Makale 2 gönderime hazır · tez savunması |
| GPU (tahmin) | ~$130-155, Modal aylık kredisinden | ~$120-130 |
| nakit (tahmin) | ~$68-76 (hakem API) | ~$30-50 (rakipler + hakem) |
| kullanıcı saati (tahmin) | ~80-115 | ~60-85 |

Checkpoint 2 hiç gerçekleşmese bile Checkpoint 1 mezuniyete yeterli tez malzemesi üretir (§2.9).
Çalışan uygulama hiçbir aşamada bozulmaz; `v1.0` her zaman yedek olarak durur.

---

## 1 · Amaç ve kapsam

**Amaç.** Endüstride LLM post-training araştırmacısı olma hedefine hizmet eden iki tek yazarlı,
hakemli makale (ACL ailesi / COLM düzeyi) ve bunların üzerine kurulan yüksek lisans tezi
(DEÜ Fen Bilimleri Enstitüsü, mezuniyet ~2028 yazı).

**Çalışma koşulları.** Tek yazar · dönem içinde haftada 5 saatten az kullanıcı zamanı, yoğun okuma ve
yazma tatillerde · toplam bütçe $100-500 · eğitim Modal'da (aylık $30 kredi), ölçüm kullanıcının
dizüstünde · icrayı ajan yürütür, kararları kullanıcı verir.

**İlkeler.**
- Eldeki her şey kullanılır; hiçbir aşama sıfırdan başlamaz.
- İterasyon yalnız geliştirme kümesinde (DEV) yapılır; son hüküm hiç bakılmamış testte bir kez okunur.
- Karşılaştırılan bütün kollar eşit ayar emeği alır; denenen her yapılandırma raporlanır.
- Sonuç ne çıkarsa çıksın yayımlanır; kutsal olan hipotez değil prosedürdür.
- Ürün yolu ölçülen yolla aynıdır.

**Kapsam dışı.** "Türkçe hukuk asistanı" anlatısı (yalnız deney ortamıdır) · Checkpoint 1'de rakip
(kapalı) modeller · HMGS ve kapalı-kitap sınavlar (ezberi ölçer; ezber anti-hedeftir,
[ADR-0027](adr/kararlar-0027-0044.md#adr-0027)) · RS-FT ([ADR-0035](adr/kararlar-0027-0044.md#adr-0035))
· korpus genişletme turu (Checkpoint 2'den sonra, §4.4) · ara yayın.

---

## 2 · Checkpoint 1 — Makale 1

### 2.1 Araştırma soruları

**RQ1 — post-training.** Temellendirme (RAFT biçimli SFT) ile çekinme (ORPO) küçük modelde çatışır:
τ_g tek başına M2b'de 0,506, τ_a tek başına kütlede %41,2 ([`kollar.md`](record/kollar.md) satır
303-304). Aynı veriyle dört yol karşılaştırılır — tek kollar · ayrı kollar + ham TIES · tek eğitimde
birlikte öğretme · ardışık eğitim — ve bu karşılaştırma **iki temel modelde** (Qwen3.5-4B, Gemma 4 E4B)
tekrarlanır. Alt soru: yöntemlerin sıralaması temel modele göre değişiyor mu?
Karar kuralı ön-kayıtlıdır: Kapı 5, `min(temellendirme, çekinme)` bileşiği
([ADR-0037](adr/kararlar-0027-0044.md#adr-0037)); formül korunur, eşikler yeni birimde yeniden
türetilir.

**RQ2 — ölçüm.** RQ1'in hükümlerinden hangileri eski alet ile düzeltilmiş alet arasında yön
değiştirir? Kayıttaki dört vaka Tablo 2'nin ilk satırlarıdır: önsözün etkisi +1,5 → −4,6 puan
([ADR-0058](adr/kararlar-0045-0063.md#adr-0058)) · `k=10` kapı hükmü ret → kabul
([#54](record/kronoloji-53-62.md#54)) · ara kapının ikinci gözlemi geçti → düştü
([ADR-0045](adr/kararlar-0045-0063.md#adr-0045)) · birleştirmenin M2 katkısı +0,020 → +0,000
([`kollar.md`](record/kollar.md) satır 319-332).

### 2.2 Çıktılar

```
TABLO 1 — tek modelde iki beceri: hangi yol, hangi temel model?
(yeni test · her hücre 3 seed ortalaması ve aralığı)

                                      Qwen3.5-4B                    Gemma 4 E4B
yol                                   kütle  M2/M2b  red  madde  M5   kütle  M2/M2b  red  madde  M5   düşünce
yalnız τ_g (SFT)
yalnız τ_a (ORPO)
ayrı kollar + ham TIES
birlikte eğitim (SFT+ORPO tek koşu)
ardışık (SFT → ORPO)

TABLO 2 — eski aletle ölçseydik ne derdik?
hüküm                                 eski alet       düzeltilmiş alet
birleştirmenin M2'ye katkısı           +0,020          +0,000
önsözün kütleye etkisi                 +1,5 p          −4,6 p
… Tablo 1'in hükümleri
```

Ayrıca: insan doğrulama tablosu (§2.5.3) · kazanan (temel model, yöntem) çiftiyle güncellenmiş
uygulama · tezin 4. bölümünün malzemesi.

### 2.3 Deney tasarımı

**Temel modeller.** Qwen3.5-4B (bugünkü ürün) ve Gemma 4 E4B (Google; ~4,5B etkin, gömme
tablolarıyla 8B). İkisi de 3 seed alır. Gemma, F0'daki kapıyı (§2.4) geçemezse yerini **Ministral 3
3B Reasoning** alır, aynı tasarımla.

**Kollar** (her temel model ve her seed için):

```
ham model ── SFT (data/train/raft_scrubbed) ──────────► τ_g ┐
ham model ── ORPO (data/train/orpo_abstain_cp2c) ─────► τ_a ┴─► ham TIES ─► birleştirme kolu
ham model ── tek eğitim: aynı SFT verisi + aynı ORPO çiftleri ──────────────► birlikte-eğitim kolu
ham model ── SFT ──► τ_g ── üstüne ORPO ─────────────────────────────────────► ardışık kol
```

Birlikte eğitim, birleştirmenin kullandığı bilginin tamamını (ORPO'nun reddedilen tarafı dahil)
kullanır; bu yüzden adil bir rakiptir. Bunun için yeni eğitim kodu yazılır.

**Seed'ler.** 3407 · 3408 · 3409 ([`EGITIM_ORTAMI.md`](EGITIM_ORTAMI.md)). Qwen'de 3407 seed'inin τ_g
ve τ_a kolları eldeki `tg_v1` ve `ta_v1` adaptörleridir, yeniden eğitilmez; τ_g'nin veri klasörü
künyede kayıtlı olmadığı, davranışsal kanıtın `raft_scrubbed`'ı gösterdiği
([`kollar.md`](record/kollar.md) satır 109-120) makalede yazılır. F0'da τ_g v1'in hassasiyet rejimi
yeniden üretilemezse 3407 seed'i de yeniden eğitilir ve `v1` yalnız ürün olarak kalır.

**Tarif.** τ_g ve τ_a tarifi iki temel modelde aynıdır (`v1` tarifi). Birlikte eğitim ve ardışık
eğitim, her temel modelde DEV'de ikişer yapılandırmayla ayarlanır. Birleştirme ailesinin DEV
iterasyonu Qwen'de yapılmıştır (ham, norm-min, norm-ortalama, modül-başına;
[ADR-0052](adr/kararlar-0045-0063.md#adr-0052), [ADR-0053](adr/kararlar-0045-0063.md#adr-0053));
Gemma'da birleştirme ham TIES ve norm-min ile denenir. Denenen bütün yapılandırmaların DEV sonuçları
eke girer.

**Dondurma.** DEV iterasyonu bitince, test açılmadan önce bir ADR yazılır: seçilen yapılandırmalar ·
düşünce koruma eşiği · istatistik planı · birincil metrik ve birincil karşılaştırma · kazanan seçim
kuralı. Testten sonra gelen yeni fikir yeni bir hipotezdir ve aynı testte denenmez.

**Kazanan seçimi.** Kazanan, testte **kütlesi en yüksek** (temel model, yöntem) çiftidir; ancak
şu dört kapıyı geçmesi şarttır:
1. düşünce koruma eşiğini kendi ham modeline göre geçer (§2.5.4);
2. yanlış maddeye dayanma, `tgta_v1`'in aynı testteki değerinden kötü değildir;
3. Q4_K_M'de 4.096 bağlamda **≤8 GB VRAM** ([ADR-0018](adr/gemma4-12b-dersler.md#adr-0018));
4. lisansı açık ve ürünün Apache-2.0 dağıtımıyla uyumludur.

İki aday güven aralıkları içinde berabereyse mevcut ürün (`tgta_v1`) kalır. Kazanan, testte seçildiği
için Makale 2'nin son sınavı ayrı ve mühürlü parçadır (§2.5.1).

### 2.4 İkinci temel model kapısı

CLAUDE.md'nin altı maddelik base kapısı, artı üç madde. Gemma için bilinen notlar:

| madde | not |
| :--- | :--- |
| llama.cpp desteği | metin ve görüntü desteği duyuruda var (HF blog) |
| şablon render'ı gözle | bu ailenin `enable_thinking` dalı 12B hattında sessizce bozulmuştu ([`gemma4-12b-dersler.md`](adr/gemma4-12b-dersler.md) A4.2) |
| turn işaretleri | assert edilir ([ADR-0026](adr/gemma4-12b-dersler.md#adr-0026)) |
| eğitim yığını | Unsloth ve TRL desteği duyuruda var; A100'de pilotla doğrulanır |
| kuantizasyon | Q4_K_M; dosya boyutu ve VRAM ölçülür (kazanan kapısı 3) |
| lisans | HF duyurusu "Apache 2" diyor, kayıt "Apache-2.0'ın üstüne Prohibited Use Policy" diyor ([#39](record/kronoloji-39-52.md#39)); lisans dosyası okunarak çözülür (kazanan kapısı 4) |
| düşünce davranışı | ham modelin kendi kapatma ve döngü oranı eğitimden önce ölçülür; zorunlu kapatma Gemma'nın kapanış işaretine göre parametrelenir |
| LoRA hedefleri | yalnız metin kulesi; görüntü ve ses kuleleri dışarıda ([ADR-0030](adr/kararlar-0027-0044.md#adr-0030)'daki `all-linear` tuzağının eşi) |
| Türkçe taban | ham modelle DEV'de tek M1 koşusu; tabana yapışıksa yedek modele geçilir |

Özneler Qwen ve Gemma, hakemler OpenAI ve Anthropic: aile dışlaması sağlanır.

### 2.5 Ölçüm

#### 2.5.1 Test kümesi

- **Bileşim:** eski donmuş TEST (40 temel + 35 tuzak; yalnız `tgta_v1` için bir kez açıldı,
  [ADR-0077](adr/kararlar-0064-0085.md#adr-0077), üzerinde hiçbir seçim yapılmadı) + ~200-225 yeni
  soru; toplam ~200 temel + ~100 tuzak. Sonuçlar iki parça için ayrıca da raporlanır.
- **Mühürlü parça:** ~100 soru, Checkpoint 2'nin sonuna kadar açılmaz. Açık depoya girmez; depoda
  yalnız `sha256` özeti ve satır sayısı durur, bir test dosyanın git tarafından izlenmediğini sınar.
- **Yeni soruların kuralları:** kanun ve madde uzunluğuna göre katmanlı (DEV↔TEST arama tavanı
  farkının %81'i madde uzunluğu bileşiminden geliyordu, [ADR-0069](adr/kararlar-0064-0085.md#adr-0069);
  kabul testinde kütle düşüşünün %76'sı bu tavanla açıklandı, [`MODEL_CARD.md`](../MODEL_CARD.md)
  §5.4) · tek başına anlaşılır (eski soruların ~%22'si belirsizdi,
  [#53](record/kronoloji-53-62.md#53)) · eğitim verisiyle örtüşme denetimi üç düzeyde: soru
  yakın-kopyası, altın maddenin eğitim verisinde altın olarak geçmesi, üretici şablonu.
- **Etiketler ve dilimler:** görev tipi (madde ne diyor · koşul/istisna · vaka uygulaması ·
  sayı/süre) · ~50 sorunun hukuk terimi kullanmayan vatandaş dilinde yeniden ifadesi (ikincil eksen) ·
  "eğitimde görülmüş / görülmemiş" kırılımı (ikincil, betimsel). Zorluk modelden bağımsız
  özelliklerle kurulur; sorular hiçbir modelin çıktısına göre süzülmez.
- **Üretim:** LLM üretir. Üretici, eğitim verisini üreten modelden farklıdır ve ne özne ne Makale 2
  rakibi olan bir ailedendir; modeli, sürümü ve istemi künyeye yazılır. Kullanıcı her soruyu netlik
  için okur. Küme bir kez dondurulur, bir kez açılır.
- **Çözünürlük:** %10'luk bir oran için güven aralığı genişliği n=80'de 13,4 puan
  ([ADR-0083](adr/kararlar-0064-0085.md#adr-0083) EK-2), n=200'de ~8 puan (hesap).

#### 2.5.2 Hakemler

- `gpt-4o-mini` bütün kolları puanlar ve bağlayıcı hakemdir.
- `claude-sonnet-5` iki temel modelde birincil karşılaştırmayı (birleştirme ↔ birlikte eğitim)
  1 seed'de puanlar; iki aile arasındaki uyum (κ) raporlanır.
- Hiçbir özne kendi ailesinin hakemiyle puanlanmaz.
- Ajan-okuyucu (Claude ailesi) yalnız Qwen ve Gemma cevaplarını okur.
- **Sürüm ve kayma:** hakemlerin tarihli model kimliği ve sağlayıcısı künyeye yazılır. `tgta_v1`'in
  80 DEV cevabı F0'da ve F3'te aynı hakemlerle puanlanır; fark gürültü tabanını aşarsa puanlama durur.
- **Payda kapısı:** puanlanan cevaplanan kalem sayısı cevaplanan kalem sayısına eşit olmalıdır; hakem
  hatası ve sıfır iddialı cevap ayrı sayılır.
- **Önyargı sondası (F1):** DEV cevaplarına tek değişkenli bozmalar (uzatma · soruya ait olmayan
  gerçek madde atfı · şerh cümlesi · "Düşünce süreci:" açılışı · kaynak sırası) ve etiketi bilinen
  kontrol kalemleri; her hakemin ve çekinme dedektörünün karar değişim oranı Tablo 2'nin ekidir.
- **İz ↔ cevap tutarlılığı:** önce izdeki kaynak seçimi ile cevaptaki atıf deterministik eşlenir;
  hakem yalnız kalan kalemlere katı JSON ile ve kaynaklar iki sırada verilerek bakar.
- Kol başına cevap uzunluğu ve atıf yoğunluğu raporlanır.

#### 2.5.3 İnsan doğrulaması

Depodaki eski "göz" okumalarını bir AI ajanı yapmıştır; makalenin yer-gerçeği insandır.

- **Protokol** cevaplar okunmadan yazılır: cevap ↔ çekinme · altın bağlamdayken susma · isabetsiz
  atıf · sadakat (iddia düzeyinde; doğrulanabilir iddia ↔ yorum) · düşünce izi ↔ cevap tutarlılığı ·
  "belirsiz". Protokol F1'de ~40-60 DEV cevabında kullanıcının okumasıyla denenir; hakemin insanla
  uyumu test açılmadan bilinir.
- **Kör okuma:** okuyucu kolu görmez, sıra karışıktır.
- **Örneklem:** kollara ve iki temel modele yayılmış ~300 cevap; zorunlu tabakalar bütün isabetsiz
  atıf kalemleri, hakemlerin ayrıştığı kalemler ve ajanın eski okuduğu kalemlerdir. Kullanıcı hepsini okur; gönüllü hukuk öğrencileri yaklaşık üçte birini bağımsız ikinci kez
  okur; bir hukukçu yalnız isabetsiz atıf anlaşmazlıklarını karara bağlar.
- **Rapor:** insan↔insan (κ, Krippendorff α) · insan↔hakem · insan↔çekinme dedektörü · insan↔ajan
  uyumu (yüzde uyum, κ, sınıf başına precision/recall). Kalan cevapları
  bu aletler puanlar. İsabetsiz atıfın otomatik vekili olmadığı ölçülmüştür
  ([ADR-0066](adr/kararlar-0064-0085.md#adr-0066)); bu eksende ajan-okuyucu kullanılır ve insanla
  uyumu raporlanır.

#### 2.5.4 Düşünce koruma

| ölçü | alet |
| :--- | :--- |
| kendi kapatma oranı | zorunlu kapatma sayacı |
| döngü oranı | kuyruk-tekrarı dedektörü ([ADR-0073](adr/kararlar-0064-0085.md#adr-0073)) |
| düşünce izi ↔ cevap tutarlılığı | hakem; insan örnekleminde doğrulanır |
| iz dili | deterministik |
| genel akıl yürütme kaybı | açık lisanslı küçük iki genel küme (Türkçe, İngilizce), düşünce açık, yerelde |

Çıpa her temel modelin kendi ham hâlidir ([ADR-0039](adr/kararlar-0027-0044.md#adr-0039)). Eşik
dondurma ADR'sinde yazılır. Risk kayıtta görünür: τ_a düşüncesini hiç kendi kapatmıyor (230/230 zorla,
[#48](record/kronoloji-39-52.md#48)); birleştirme bunu kısmen geri kazanıyor (M1'de 25/80 zorla, ham
model 80/80, [`kollar.md`](record/kollar.md) satır 334-335).

#### 2.5.5 İstatistik

Birincil metrik **kütle**; birincil karşılaştırma **birleştirme ↔ birlikte eğitim**, her temel modelde
ayrı; diğer karşılaştırmalar ikincil olarak etiketlenir. Kütle için soru × seed üzerinde eşleştirilmiş
bootstrap; sayımlar için Wilson aralığı.

#### 2.5.6 Ölçüm ortamı

Bütün üretimler aynı dizüstünde (RTX 5070 Laptop), aynı llama.cpp sürümüyle ve konteynerin kilitli
bayraklarıyla koşar ([ADR-0078](adr/kararlar-0064-0085.md#adr-0078)); bilgisayar şarja takılıdır
(pilde hız 17 kat düşer, [#39](record/kronoloji-39-52.md#39)). KV önbelleği ayarı bile cevapların
%81'ini değiştirdiği için ([#66](record/kronoloji-63-71.md#66)) ölçüm başka donanıma taşınmaz.

### 2.6 Takvim

| aşama | zaman | iş | kullanıcı saati (tahmin) |
| :--- | :--- | :--- | :--- |
| **F0 — zemin** | Ekim sonu–Kasım 2026 | bundle ve `v1` adaptörlerinin yedeği · kararların ADR'ye işlenmesi · τ_g v1 hassasiyetinin bundle geçmişi ve Modal günlüklerinden çözülmesi · eski aletlere bundle'dan erişim · eğitim ortamı kilidinin yaml'ı, betik kontrolü ve testi · birlikte-eğitim kodu ve Modal pilotu · Gemma kapısı · literatür taraması (birleştirme ↔ birlikte eğitim; RLVR ve çekinme) · ön-kayıt taslağı · mevcut kolların güncel DEV'de yeniden ölçümü | ~10-14 |
| **F1 — DEV iterasyonu** | Aralık 2026–Ocak 2027 | iki temel modelde birlikte ve ardışık eğitim, ikişer yapılandırma · Gemma'da birleştirme · insan↔hakem pilotu · hakem önyargı sondası · test sorularının üretimi ve okuma protokolü · **dondurma ADR'si** | ~6-8 |
| **F2 — test ve seed'ler** | Şubat–Nisan 2027 | test sorularının okunması (vatandaş dili dilimi dahil) ve dondurulması (Şubat ara tatili) · bütün kolların bütün seed'leri | ~8-12 |
| **F3 — son ölçüm** | Mayıs–Haziran | test bir kez açılır · ~30 kolun dizüstünde ölçümü (~200 saat, geceleri) · Tablo 2 · ikinci hakem · kazanan seçimi | ~3-4 |
| **F3b — uygulama** | Haziran–Temmuz | kazanan → GGUF → konteyner kilidi → model kartı; kazanan `tgta_v1` ise değişiklik yok | ~2-4 |
| **F4 — insan doğrulaması** | Temmuz | ~300 cevap kör okuma · öğrenciler · hukukçu · uyum istatistikleri | ~12-15 |
| **F5 — yazım** | Ağustos–Eylül | yazım · 1-2 dış okuyucu · arXiv (ARR kuralına göre) · ilk uygun ARR döngüsüne gönderim | ~40-60 |

Her aşamanın iş adımları ve doğrulamaları: [`ROADMAP_v1.md`](ROADMAP_v1.md) §2-§7.

### 2.7 Bütçe

| kalem | tahmin |
| :--- | ---: |
| F0 pilotları ve Gemma kapısı | ~$5 |
| DEV iterasyonu: Qwen / Gemma | ~$14 / ~$21-28 |
| seed'ler: Qwen (3407'nin τ_g ve τ_a'sı hariç) / Gemma | ~$32 / ~$57-76 |
| **GPU toplamı** | **~$130-155** |
| hakem `gpt-4o-mini`, bütün kollar (kayıttaki ×1,6 fatura payı dahil) | ~$20-28 |
| ikinci hakem, iki temel modelde birincil karşılaştırma | ~$19 |
| düşünce izi ↔ cevap tutarlılığı hakemi | ~$8 |
| test üretimi, kör payda, RQ2 yeniden puanlaması | ~$5 |
| F0: hakem kayma çıpası ve mevcut kolların DEV ölçümü · F3: kayma çıpasının tekrarı | ~$8 |
| F1: DEV iterasyonunun puanlanması · önyargı sondası · insan pilotunun hakem tarafı | ~$8 |
| **nakit toplamı** | **~$68-76** + OpenRouter kredi ücreti |

GPU giderleri Modal'ın aylık $30 kredisine göre Kasım 2026–Nisan 2027'ye bölünür; bir ay yetmezse
eğitim aynı ay Vast'ta A100 ile, [`EGITIM_ORTAMI.md`](EGITIM_ORTAMI.md) §4'teki kurala göre sürer.
Birim fiyatlar: Modal A100-40GB $2,10/saat; SFT A100'de ~2,1 saat
([ADR-0033](adr/kararlar-0027-0044.md#adr-0033)), ORPO 36,5 dakika ([#48](record/kronoloji-39-52.md#48));
Gemma koşuları Qwen'in 1,5-2 katı varsayıldı. Gerçek API faturasının hesaplanan tutarın 1,596 katı
çıktığı ölçülmüştür ([#64](record/kronoloji-63-71.md#64)).

### 2.8 Gönderim

ARR üzerinden ACL / EMNLP / NAACL / EACL ana konferansı hedeflenir; Findings kabul edilebilir
sonuçtur. Ret hâlinde hakem yorumlarıyla sonraki ARR döngüsüne, o da olmazsa sırasıyla TMLR, Natural
Language Engineering ve Language Resources and Evaluation dergilerine gönderilir. Tek yazarlığın
iç hakem eksiği, gönderimden önce 1-2 dış okuyucuyla kapatılır.

### 2.9 Checkpoint 1'in tez karşılığı

Checkpoint 1 bittiğinde tezin dört bölümü yazılabilir durumdadır: 1 giriş ve ilgili çalışmalar ·
2 sistem (HakHukuk; arama katmanı, düşünce bütçesi, konteyner — eldeki iş) · 3 ölçüm dersleri
(eldeki kayıt) · 4 post-training karşılaştırması (Makale 1). Checkpoint 2, 5. bölümü ekler.

---

## 3 · Checkpoint 2 — Makale 2 ve tez

### 3.1 Başlangıç noktası

Checkpoint 1'in kazananı (temel model ve yöntem). Kazanan Gemma ise ürün de Gemma'ya geçer.
Birleştirme hattı ürün için `v1`'de dondurulmuştur; RL, kazananın üstüne ardışık bir eğitimdir
([ADR-0075](adr/kararlar-0064-0085.md#adr-0075)).

### 3.2 Ödül

Atıf doğrulayıcı tek başına isabetsiz atıfı göremez: atıf yapılan madde gerçektir, yalnız soruya ait
değildir ([ADR-0066](adr/kararlar-0064-0085.md#adr-0066)). Eğitim sorularının altın maddesi bilindiği
için ödül hakemsiz kurulur:

| durum | ödül |
| :--- | :--- |
| altın maddeye doğrulanmış atıf | + |
| başka bir gerçek maddeye atıf | 0 ya da − |
| uydurulmuş madde | − |
| altın bağlamda yokken susma | + |
| altın bağlamdayken susma | − |

Ödül katsayıları, hedef bant ve durma kuralı RL başlamadan bir ADR'ye yazılır. Korunacak tabanlar,
kazananın Checkpoint 1'deki değerleridir (uydurulmuş madde, gereksiz red, kütle).

### 3.3 Düşünce hizalaması

Makale 1'in düşünce koruma ölçülerine ek olarak: iz kaynağın soruyu karşılayıp karşılamadığını
tartıyor mu, iz ile karar tutarlı mı, iz Türkçe mi. Türkçe iz için ayrı bir ödül terimi ön-kayıtta
karara bağlanır.

### 3.4 Koşu planı ve maliyet

İlk iş ~$2-5'lik bir pilottur: kazanan model için vLLM üretiminin çalıştığını ve adım süresini ölçer.
Ardından **pilot + ana GRPO 3 seed + 2 ablasyon** (isabet terimsiz ödül · çekinme terimsiz ödül)
koşulur; tahmini ~$120-130. Pilotta birim maliyet orta senaryonun 1,5 katını aşarsa plan **2 seed +
1 ablasyon** (isabet terimsiz) olur, ~$75-80.

| senaryo (koşu başına, tahmin) | adım | süre | Modal |
| :--- | ---: | ---: | ---: |
| küçük, RAFT biçimli istem | 250 | ~5-6,5 sa | ~$11-14 |
| orta, RAFT biçimli istem | 500 | ~10-13 sa | ~$22-28 |
| uzun, ürün biçimli istem | 500 | ~19-24 sa | ~$40-50 |

Dayanak: eğitim verimi A100'de 2.619 token/sn ([ADR-0033](adr/kararlar-0027-0044.md#adr-0033)) · cevap
~800 token · soru başına 8 cevap · LoRA'lı GRPO. Koşular Modal kredisiyle ayda kabaca bir tane olmak
üzere Kasım 2027–Mart 2028'e yayılır.

**İzleme ve ödül tasarımı ilkeleri** (ön-kayıt ADR'sine girer;
[`knowledge/summary_rl_posttraining_survey.md`](../knowledge/summary_rl_posttraining_survey.md) §C):
ödül bileşenleri (isabet · uydurma cezası · çekinme) ayrı fonksiyonlar olarak hesaplanır ve GDPO
biçiminde ayrı ayrı normalize edilir · bütün cevapları aynı ödülü alan grupların oranı adım başına
günlüğe yazılır, dinamik örnekleme eşiği ön-kayıttadır · referans modele KL çıpası korunur; KL ve
entropi izlenir · eğitim ödülü ile DEV'deki hakemli ölçüm (kütle, isabetsiz atıf, aşırı red) yan yana
çizilir, ayrışma durma kuralının girdisidir · birden çok madde sayarak altını tutturma ödülde
kapatılır · düşünce uzunluğu ödüllendirilmez · SFT ile RL'yi karıştıran geçit (HPT) yalnız pilot
çekinmede gradyan boşluğu gösterirse denenir.

### 3.5 Rakip karşılaştırması ve son sınav

Kapalı modellerle karşılaştırma burada yapılır: o günün aynı sınıfları (Gemini Flash-Lite, Flash,
Claude Sonnet), tarihli sürümler ([ADR-0020](adr/gemma4-12b-dersler.md#adr-0020)), eşit sınav
([ADR-0057](adr/kararlar-0045-0063.md#adr-0057)), her yeni ailede çekinme dedektörünün kalibrasyonu,
aile dışlaması ([ADR-0072](adr/kararlar-0064-0085.md#adr-0072)). Tahmini maliyet ~1.100 cevaplık
testte Flash-Lite ~$2, Flash ~$11, Sonnet ~$16 + hakem ([`MODEL_CARD.md`](../MODEL_CARD.md) §5.1).
Son sınav mühürlü ~100 soruluk parçadır.

Konumlanmanın dayanacağı iki önceki çalışma Ekim 2027'de okunur (ACL 2026): *"Mitigating Lost in
Multi-turn Conversation via Curriculum RL with Verifiable Accuracy and Abstention Rewards"* (ana
konferans) · *"Pause or Fabricate? Training Language Models for Grounded Reasoning"* (Findings).

### 3.6 Takvim

| zaman | iş | kullanıcı saati (tahmin) |
| :--- | :--- | :--- |
| Ekim–Aralık 2027 | iki önceki çalışmanın okunması · ödül ve ön-kayıt ADR'si · GRPO pilotu · Makale 1 hakem yorumlarına göre yeniden gönderim | ~10-15 |
| Kasım 2027–Mart 2028 | GRPO koşuları | ~5 |
| Mart–Nisan 2028 | mühürlü parçada son ölçüm · rakipler | ~5 |
| Nisan–Haziran 2028 | tez yazımı (makale metinleri yeniden kullanılır) · Makale 2 yazımı | ~40-60 |
| yaz 2028 | tez savunması | — |

---

## 4 · Altyapı ve kurallar

### 4.1 Eğitim ortamı

Bütün eğitimler A100'de, kilitli paket sürümleri ve tarifle yapılır:
[`EGITIM_ORTAMI.md`](EGITIM_ORTAMI.md). Ana platform Modal'dır; kredi bir ay içinde biterse ya yeni ay
beklenir ya da eğitim aynı Docker imajıyla Vast'ta A100'e, blok sınırında ve eşdeğerlik kontrolünden
sonra taşınır. Makalenin ekinde hangi kolun nerede eğitildiği yazılır.

### 4.2 Yedekler

Eski git geçmişinin tek kopyası olan `~/yedek/HakHukuk-2026-10-10.bundle`
([ADR-0088](adr/kararlar-0064-0085.md#adr-0088)) ile Makale 1'in 3407 seed'i olan `outputs/tg_v1` ve
`outputs/ta_v1` adaptörleri F0'ın ilk işinde ikinci bir kopyaya alınır (harici disk ya da özel HF
deposu). Bu, adaptörlerin yedeklenmeyeceğini söyleyen [ADR-0034](adr/kararlar-0027-0044.md#adr-0034)'ü
değiştiren yeni bir ADR ile kayda geçer. Yeni seed'lerin adaptörleri de aynı biçimde yedeklenir.

### 4.3 Kayıt disiplini

Her aşama kronolojiye #72'den itibaren bir girdi, her karar bir ADR üretir; her koşunun künyesi
(`KUNYE.json`) [`EGITIM_ORTAMI.md`](EGITIM_ORTAMI.md) §5'teki alanları taşır.

### 4.4 Ürün yol haritasıyla ilişki

| ürün işi (`superpowers/00-IS-SIRASI.md`) | yeri |
| :--- | :--- |
| `v2-RL-GRPO` | Checkpoint 2 (Makale 2) |
| korpus turu (40.496 → ~288 bin madde) | Checkpoint 2'den sonra; korpus değişince eşit sınav ve yayımlanan sayılar askıya alınır ([ADR-0083](adr/kararlar-0064-0085.md#adr-0083) §E.6) ve mühürlü test aynı korpusa bağlıdır |
| açık kusurlar 5a · 23 · 27 · 31 | ürün iş listesinde |

---

## 5 · Riskler ve karşılıkları

| risk | tetik | karşılık |
| :--- | :--- | :--- |
| τ_g v1'in hassasiyeti yeniden üretilemiyor | F0 | Qwen'de 3407 seed'i de yeniden eğitilir (~$6) |
| Gemma kapıdan kalıyor | F0 | Ministral 3 3B Reasoning aynı tasarımla girer; o da kalırsa Makale 1 tek temel modelle yazılır ve hedef Findings ya da dergi olur |
| birlikte-eğitim kodu çalışmıyor | F1 sonu | karışık SFT tabanı son çare olarak girer, zayıflığı makalede yazılır |
| birim maliyet tahminin 1,5 katı | herhangi bir pilot | bütçe yeniden hesaplanır; eğitim Vast A100-80GB'a geçer |
| gönüllü öğrenci bulunamıyor | Mayıs 2027 | okuma kullanıcı ve hukukçuyla yapılır; insan↔insan uyumu sınırlılık olarak yazılır |
| kazanan dört kapıdan birinden kalıyor | F3 | kapıları geçen en iyi çift kazanır; hiçbiri geçmezse ürün `tgta_v1`'de kalır |
| takvim bir aydan fazla geride | F3 sonu | kesme sırası: ikinci hakem → Gemma'da üçüncü seed. Kesilmeyenler: birlikte eğitim · Qwen'de 3 seed · insan doğrulaması · test kümesi |
| yazım yetişmiyor | F5 | gönderim bir ARR döngüsü kayar; tez etkilenmez |
| makale reddediliyor | hakem kararı | sonraki ARR döngüsü → dergi |
| özgünlük örtüşmesi | F0 literatür taraması | çerçeve dondurmadan önce düzeltilir |
| dizüstünün ~200 saatlik ölçüm yükü | F3 | ölçüm Mayıs–Haziran'a yayılır; başka donanıma taşınmaz |

---

## 6 · Doğrulanacak dış bilgiler

| ne | nerede | ne zaman |
| :--- | :--- | :--- |
| ARR 2027 döngü tarihleri ve ön baskı (arXiv) kuralı | aclrollingreview.org | F0 |
| ACL/ARR yapay zekâ yardımı politikası · gönderim kontrol listesi · karşılıklı hakemlik şartı | ACL / ARR | F0 |
| DEÜ FBE: tez dili · mezuniyet için yayın şartı · yayımlanmış makalenin tezde kullanımı · tezden üretilen yayında danışman adı · programa başlamadan önceki işin teze sayılması · üretken YZ kuralı | enstitü yönetmeliği ve tez yazım kılavuzu | F0 |
| Modal $30 kredisinin hesapta aylık yenilenmesi · akademik kredi başvurusu | Modal faturalama sayfası | F0 |
| Gemma 4 E4B lisans dosyası | HF model deposu | F0 |
| genel yetenek kümesinin lisansı | küme deposu | F0 |
| Vast'ta A100 fiyatı ve sürücü sürümü | Vast konsolu | gerektiğinde |
| vLLM'in kazanan modeli desteklemesi | GRPO pilotu | Ekim 2027 |
| COLM 2028 çağrısı | COLM sitesi | Ekim 2027 |

---

## 7 · Mevcut kayıtla ilişki

Bu plan aşağıdaki kayıtlarla çelişir ya da onları günceller; karşı tarafları F0'da ADR ile
damgalanır.

| kayıt | kayıttaki ifade | bu plan |
| :--- | :--- | :--- |
| [`MODEL_CARD.md`](../MODEL_CARD.md) §2 | iki kol "QLoRA (NF4)" | [ADR-0031](adr/kararlar-0027-0044.md#adr-0031) "bf16 taban + LoRA"; τ_a `--bf16-base` ile eğitildi ([#48](record/kronoloji-39-52.md#48)); τ_g bilinmiyor; betiklerin varsayılanı NF4 → F0'da çözülür |
| [ADR-0028](adr/kararlar-0027-0044.md#adr-0028) | tek boyut noktası | ikinci bir temel model (aynı boy, başka aile) eklenir |
| [ADR-0034](adr/kararlar-0027-0044.md#adr-0034) | adaptörler yedeklenmez | `v1` ve yeni seed adaptörleri yedeklenir |
| [ADR-0037](adr/kararlar-0027-0044.md#adr-0037) | Kapı 5 "ayar: norm-dengeli" | ana sonuç ham TIES ([ADR-0052](adr/kararlar-0045-0063.md#adr-0052)); Kapı 5 ham TIES için türetilir |
| [ADR-0075](adr/kararlar-0064-0085.md#adr-0075) m.3 | task-vector hattı `v1`'de donduruldu | ürün için geçerli; Makale 1 araştırma için aynı tarifle yeni seed üretir |
| `superpowers/00-IS-SIRASI.md` | iki aday, sıra insan kararı · "yeni ADR 0087'den" | sıra §4.4'te verildi · sıradaki ADR 0089 |

---

## 8 · Kaynaklar (erişim 2026-10-10)

- [Modal Pricing](https://modal.com/pricing)
- Vast fiyatları: [hostalu](https://hostalu.com/en/gpu-cloud/) · [gpuperhour](https://gpuperhour.com/) ·
  [computecomparison](https://computecomparison.com/provider/vast-ai) ·
  [Vast pricing docs](https://docs.vast.ai/documentation/instances/pricing)
- OpenRouter: [claude-sonnet-5](https://openrouter.ai/anthropic/claude-sonnet-5) ·
  [gpt-4o-mini](https://openrouter.ai/openai/gpt-4o-mini)
- Temel modeller: [Gemma 4 — HF blog](https://huggingface.co/blog/gemma4) ·
  [Ministral 3 3B Reasoning](https://huggingface.co/mistralai/Ministral-3-3B-Reasoning-2512)
- ACL 2026 kabul listeleri: [ana konferans](https://2026.aclweb.org/program/accepted_papers/) ·
  [Findings](https://2026.aclweb.org/program/findings/)
- GRPO ve vLLM: [Qwen3.5 — LMCache](https://docs.lmcache.ai/recipes/qwen3_5.html) ·
  [RLVR low-rank dynamics](https://arxiv.org/pdf/2605.06523)
- Literatür özetleri (`knowledge/`): [LLM-as-judge](../knowledge/summary_llm_as_judge_survey.md) ·
  [benchmark](../knowledge/summary_llm_benchmark_survey.md) ·
  [LLM değerlendirmesi](../knowledge/summary_llm_eval_survey_chang.md) ·
  [halüsinasyon](../knowledge/summary_hallucination_survey.md) ·
  [instruction tuning](../knowledge/summary_instruction_tuning_survey.md) ·
  [bilgi damıtma](../knowledge/summary_kd_llm_survey.md) ·
  [RL post-training](../knowledge/summary_rl_posttraining_survey.md)
