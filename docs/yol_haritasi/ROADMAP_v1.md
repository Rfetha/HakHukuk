# ROADMAP v1 — Checkpoint 1'e giden yol

## Durum

İşlerin durumu yalnız [`law-slm-board`](https://github.com/users/Rfetha/projects/3) panosunda tutulur
([ADR-0108](../adr/kararlar-0064-0085.md#adr-0108)); bu belgede durum notu yoktur. Aşağıdaki tablolardaki
her iş bir kart, her aşama bir epic; doğrulaması geçen kartı ajan kapatır (`gh issue close N -c <commit>`).

---

> **Bu belge ne:** [`YAYIN_YOL_HARITASI.md`](YAYIN_YOL_HARITASI.md)'nın Checkpoint 1'ini (Makale 1 ·
> uygulamanın kazananla güncellenmesi · tez malzemesi) iş adımlarına çevirir. *Neden* ve *ne* yol
> haritasındadır; *nasıl* ve *hangi sırayla* burada. Plan isteğe bağlıdır (`docs/superpowers/plans/`);
> koşudan önce belirlenen eşik ve tolerans koşudan önce commit'lenir. Eğitim ortamı: [`EGITIM_ORTAMI.md`](../yontem/EGITIM_ORTAMI.md).
>
> **Biçim:** her iş `iş → doğrulama` olarak yazılır; doğrulaması geçmeyen iş bitmiş sayılmaz.
> "Tahmin" yazan saat ve para değerleri ölçüm değildir; her bloğun ilk işi birim maliyeti ölçmektir.
>
> Literatür girdisi: `knowledge/` altındaki yedi derleme özeti (LLM-as-judge, benchmark, değerlendirme,
> halüsinasyon, instruction tuning, bilgi damıtma, RL post-training). Bu belgede bir önerinin hangi
> özetten geldiği köşeli parantezle belirtilir: [hakem] · [benchmark] · [halüsinasyon] · [damıtma] ·
> [RL] · [IT].
>
> Ajan uygulaması ayrı bir hattır ve bu belgenin kapsamı dışındadır: [`ROADMAP_uygulama.md`](ROADMAP_uygulama.md)
> ([ADR-0104](../adr/kararlar-0064-0085.md#adr-0104)). Araç çağırma ölçümü de o hattadır, omurganın ilk işi
> ([ADR-0105](../adr/kararlar-0064-0085.md#adr-0105)).

---

## 0 · Checkpoint 1 ne zaman tamamdır

Aşağıdaki altı madde doğrulanınca (hedef Eylül 2027):

1. **Tablo 1 dolu:** 2 temel model × 5 kol, yeni testte; iki beceriyi toplayan üç yol (ayrı kollar +
   ham TIES · birlikte · ardışık) 3 seed'le, soru × seed eşleştirilmiş bootstrap aralıklarıyla; tek
   kollar (τ_g, τ_a) seed 3407 ile.
2. **Tablo 2 dolu:** kayıttaki dört "hüküm döndü" vakası + Tablo 1 hükümlerinin eski ve düzeltilmiş
   aletle karşılaştırması.
3. **İnsan doğrulama tablosu:** ~300 cevap; insan↔insan ve insan↔hakem/dedektör/ajan uyumu.
4. **Kazanan seçildi** (üç yoldan, dört kapı; yol haritası §2.3) ve uygulama kazananla güncel; ya da `tgta_v1`
   gerekçesiyle kaldı.
5. **Makale 1 metni gönderime hazır.**
6. Makale 1 tezin 4. bölümüdür; 2. ve 3. bölüm üründen ve kayıttan yazılır.

---

## 1 · Başlangıç zemini (eldeki)

- `v0.5` etiketli ve çalışıyor (2026-09-13'te `v1.0` adıyla etiketlendi, 2026-10-10'da yeniden adlandırıldı; `v1` Checkpoint 1'in sonundaki sürümdür); ağırlıklar ve indeks HF'te public; konteyner rejim kilidi
  ([ADR-0078](../adr/kararlar-0064-0085.md#adr-0078)).
- Ölçüm zinciri onarılmış: kütle %68,4 → %80,1, ağırlıklar değişmeden
  ([#62](../record/kronoloji-53-62.md#62)); iki aileli hakem paneli
  ([ADR-0084](../adr/kararlar-0064-0085.md#adr-0084)).
- Makale 1'e doğrudan girenler: `tg_v1` · `ta_v1` · `tgta_v1` (Qwen'de 3407 seed'i) · birleştirme
  ailesinin DEV iterasyonu ([ADR-0052](../adr/kararlar-0045-0063.md#adr-0052),
  [ADR-0053](../adr/kararlar-0045-0063.md#adr-0053)) · eski donmuş TEST (son testin bir parçası) · DEV
  (80 + 70) · dört "hüküm döndü" vakası · ajanın eski okumaları (insan doğrulamasının karşılaştırma
  tarafı) · kusur sicili ([ADR-0083](../adr/kararlar-0064-0085.md#adr-0083), tarih; açık kusurlar panoda).

---

## 2 · F0 — Zemin *(Ekim sonu–Kasım 2026)*

**Amaç:** hiçbir eğitim parası harcanmadan önce ortamı, aletleri ve kararları sağlamlaştırmak.

| # | iş → doğrulama |
| :-- | :--- |
| F0.1 | **Yedekler:** `~/yedek/HakHukuk-2026-10-10.bundle` (140 MB), `outputs/tg_v1` (115 MB), `outputs/ta_v1` (134 MB) özel HF deposuna (`Rfetha/HakHukuk-yedek`); yüklemeden önce bundle gizli anahtar için taranır; yerel kopya kalır → depodan indirilen kopyanın `sha256`'sı kaynakla birebir |
| F0.2 | **Kararları deftere işle:** yol haritasının kararları ADR-0089 ve sonrası olarak (yayın yolu · ikinci temel model ve teknik kapı kuralı · yedekleme, ADR-0034'ü değiştirir · eğitim ortamı kilidi · bağlayıcı hakem değişikliği · korpus turunun ertelenmesi · `00-IS-SIRASI.md`'nin silinmesi · sürüm adı `v1.0` → `v0.5` ve GGUF dosya adı `v0.3` → `v0.5` (ADR-0065'in dosya adı kuralını tersine çevirir; `v1` = Checkpoint 1 sonu) · Makale 2 ödül ilkesi · 2026-10-10 fizibilite kararları — iki Modal hesabı ve kredi kuralı, τ_g/τ_a seed'lerinin dondurmayı beklememesi, tek kolların testte tek seed'i, kazananın üç yoldan seçilmesi, vatandaş dili kapsamı, takvimin öne çekilmesi, GRPO'nun 2027 yazında başlaması, yeni kesme sırası) · `ROADMAP.md` → `ROADMAP_v1.md` yeniden adlandırmasının kırdığı bağlantılar düzeltilir (CLAUDE.md, README.md, docs/README.md, docs/README.tr.md, docs/urun/MIMARI.md, `tests/depo/test_belgeler.py`) → `tests/depo/test_belgeler.py` yeşil, çapalar çözülüyor |
| F0.3 | **τ_g v1'in hassasiyeti:** eski geçmişte belge kanıtı bulundu (2026-10-10): τ_g için hazırlanan koşu komutu `--bf16-base` taşıyor (`9f4b43d`), ORPO kolu τ_g'ye bf16 olarak eşlendi (`64073b4`; `b995182`'de de duruyor); `requirements.lock.txt` 2026-06-07'den beri değişmedi; `fla-core` sürümü bilinmiyor → hüküm `kollar.md`'de ve [`EGITIM_ORTAMI.md`](../yontem/EGITIM_ORTAMI.md) §2'de "belge kanıtı, künye değil" damgasıyla; ölçüm kanıtı F0.4'teki eşdeğerlik kontrolünden gelir |
| F0.4 | **Eğitim ortamı kilidi:** `configs/egitim_ortami.yaml` + `train_sft.py`/`train_orpo.py` başında kontrol + test; `fla-core`, `flash-linear-attention`, `einops` sürümleri sabitlenir; hassasiyet zorunlu argüman olur · **eski ortamla eşdeğerlik:** yeni kilitte τ_g seed 3407 ile 50 adım, ORPO ile 10 adım (~$1) → yanlış GPU, yanlış paket sürümü ya da bayraksız çağrıda koşu model yüklenmeden durur (test kırmızı→yeşil); τ_g'nin 10. ve 50. adım kaybı [#40](../record/kronoloji-39-52.md#40)'taki 0,7987 / 0,3537'den en çok ~0,02 sapar, ORPO kaybı `ta_v1/trainer_state-checkpoint70.json` ile örtüşür; geçmezse Qwen'in 3407 kolları yeni kilitte yeniden eğitilir (~$6) |
| F0.5 | **Ölçüm aleti kapıları:** (a) "puanlanan cevaplanan kalem = cevaplanan kalem" kapısı; özete `n_hakem_hata` ve `n_sifir_iddia` [hakem]; geçmiş koşularda kaç kalemin bu yoldan düştüğü sayılır · (b) eski aletlere bundle'dan erişim (RQ2): puanlama tarafındaki düzeltmeler (çekinme dedektörü · hakeme giden kaynak kırpması · kapı çıpası · hakem) tek tek açılıp kapatılabilir; üretim tarafındaki eski hâl (`RRF_K` 60 + yeterlilik önsözü) üretilebilir · (c) **tamlık kapısı** ([ADR-0098](../adr/kararlar-0064-0085.md#adr-0098)): kütlenin paydası cevap dosyasının satır sayısından değil dondurulmuş kümenin boyutundan gelir; satır sayısı = küme boyutu ve id'ler tekil; üretici `.part` adıyla yazar, iş bitince dosyayı yeniden adlandırır → (a) eksik kalemde puanlama durur; (b) eski aletle eski bir koşu yeniden puanlanınca kayıttaki sayı, hakemi çağırmayan düzeltmelerde (çekinme dedektörü, kapı çıpası) birebir, hakeme giden girdiyi değiştirenlerde (kaynak kırpması, hakem) o hakemin gürültü tabanı içinde çıkar; (c) eksik ya da yinelenen satırlı dosyada puanlama durur, `.part` dosyası puanlanmaz |
| F0.6 | **Hakem geçişi ve kayma çıpası:** bağlayıcı hakem DeepSeek V4.1 Flash (`deepseek-v4.1-flash-20260910`; OpenRouter'da sağlayıcı sabit, yedek sağlayıcıya düşme kapalı). İstem sırası önbelleğe uygundur: talimat, soru ve kaynaklar başta, cevap sonda; gürültü tabanı gerçek çağrı koşullarında, önbellek dahil, ölçülür. `tgta_v1`'in F0.16 pilotunda kiralık kartta üretilen 80 DEV cevabı (bu yüzden F0.16'dan sonra; [ADR-0098](../adr/kararlar-0064-0085.md#adr-0098)) DeepSeek ile, hakemin kendi düşünme modu açık ve kapalıyken, her modda iki kez ve `gpt-4o-mini` ile puanlanır [hakem] → hakem değişikliğinin etkisi ve DeepSeek'in gürültü tabanı kronolojide; künyede tarihli model kimliği ve sağlayıcı |
| F0.7 | **Seyreklik ölçümü:** `tg_v1` ve `ta_v1` ağırlık değişimlerinin büyüklük ve seyreklik istatistikleri ($0) — τ_a'nın birleştirmede zayıflamasının (B4) olası mekanizması [RL] → tablo kronolojide; L1'li yeniden eğitim yalnız ölçüm desteklerse ve yalnız DEV'de |
| F0.8 | **Birlikte-eğitim kodu:** SFT verisi + ORPO çiftleri tek koşuda; çiftlerde tam ORPO kaybı (τ_a ile aynı biçim, iç NLL dahil), λ parametre [RL]; SFT ve tercih kayıpları ayrı günlüğe [IT]; `rewards/accuracies` yerine seçilen cevabın log-olasılığı ve odds-oran marjı izlenir [RL]; **eşit maruziyet:** SFT 1 epoch + çiftler 5 epoch aynı koşuda (çiftler örneklerin ~%20'si), ayrı kolların gördüğü veri ve gösterim sayısıyla aynı → Modal'da 50 adımlık künyeli pilot; iki kayıp eğrisi ayrı görünür; birim maliyet ölçüldü |
| F0.9 | **Gemma kapısı (yalnız teknik):** kalma sebepleri — llama.cpp çalıştıramıyor · şablon ve tur işareti gözle doğrulanamıyor · A100'de eğitim ya da Q4_K_M kurulamıyor · lisans açık değil · 1024+512 zorla kapatma uygulanamıyor · DEV cevaplarının %90'ından azı Türkçe. Yalnız kaydedilenler: Türkçe M1 tabanı · düşüncenin kendi kapanması · döngü · 8 GB üstü VRAM. LoRA hedefleri yalnız metin kulesi. Gemma başka paket sürümü isterse Qwen'in kilidine dokunulmaz → kapı tablosu kronolojide; kalırsa yedek model o gün aynı kapıyla seçilir (adaylar: Phi ailesi, Ministral 3 3B Reasoning), Makale 1 sonuçlarına bakılmadan |
| F0.10 | **`tgta_v1`'in kimliği** ([ADR-0098](../adr/kararlar-0064-0085.md#adr-0098)): adaptörlerden yeniden birleştirilen GGUF'un `sha256`'sı yayımlanmış dosyanınkiyle (`755e15e9…86e7bffc`) karşılaştırılır; tutmazsa ağırlıklar tek tek karşılaştırılır (fark yalnız dosya başlığındaysa tek model); ağırlıklar farklıysa Makale 1'in kolu yeni hattan gelir, ürün kıyası yayımlanmış dosyayla yapılır, fark kayda geçer · **Mevcut kolların güncel DEV ölçümü:** `tg_v1`, `ta_v1`, `tgta_v1` ve birleştirme varyantları (adaptörlerden $0 yeniden üretilir) güncel DEV biriminde, F0.16'da seçilen kartta · **kol başına mod kümesi:** kodda her kol için hangi modların üretildiği kontrol edilir; Tablo 1'de raporlanmayan mod yalnız 3407'de üretilir → `recall@10` 0,9500 çıpası tutar; her koşunun künyesi var; kol başına mod listesi ve üretim süresi künyede; test üretim yükü (ADR-0096'daki ~200 dizüstü saati) ve ölçüm kartının maliyeti bu sürelerle yeniden hesaplanır |
| F0.11 | **Literatür taraması:** `knowledge/` özetleri + kilit 3-5 birincil makale (birleştirme ↔ birlikte eğitim; RLVR ve çekinme; atıflı hukuki cevap) → not `knowledge/ozgunluk/` altında (kart #15'in yorumundaki prompt); örtüşme varsa çerçeve F1 dondurmasından önce düzeltilir |
| F0.12 | **Veri notu:** `MODEL_CARD.md` §8 ve `data/README.md`'ye `gpt-4o-mini` notu (soruların ve cevapların üreticisi) → iki belgede not |
| F0.13 | **Kazanan kuralının boşlukları:** Kapı 2'nin ölçüsü · kazanan yoksa · beraberlik · ürün dosyası sırası, DEV sonucu görülmeden → [yol haritası](YAYIN_YOL_HARITASI.md) §2.3 |
| F0.14 | **Dış bilgiler:** ARR 2027 kuralları · OpenAI şartları · OSF · Modal kredisi okunur → yayını etkileyen bulgu [yol haritası](YAYIN_YOL_HARITASI.md) §2.8'de |
| F0.15 | **Qwen'de τ_g/τ_a seed'leri (3408 · 3409):** `v1` tarifiyle, F0.4 kilidi geçtikten sonra; tarif sabit olduğu için DEV dondurmasını beklemez, boştaki krediyle eğitilir; tek kol olarak testte ölçülmez (yalnız birleştirme bileşeni) → künyeler; ham TIES birleştirmeleri (CPU, $0) `kollar.md`'de; adaptörler özel HF deposunda |
| F0.16 | **Ölçüm kartı pilotu** (F0.6 ve F0.10'dan önce; [ADR-0097](../adr/kararlar-0064-0085.md#adr-0097), [ADR-0098](../adr/kararlar-0064-0085.md#adr-0098)): konteyner aday kart tiplerinde (Modal ve Vast'ın veri merkezi sunucuları) kurulur; `tgta_v1`'in 80 DEV cevabı her tipte aynı makinede iki kez ve aynı tipte iki ayrı makinede üretilir; getirilen bağlamlar `sha256`'sıyla dondurulur → cevap başına süre ve maliyet · aynı makinede ve iki makine arasında birebir aynı cevap oranı · `recall@10` 0,9500 çıpası tutar · platform ve kart tipi ADR-0097'nin kuralıyla seçildi; tahmini toplam $75'i aşıyorsa durulur ve kullanıcıya dönülür · **makine geçiş kapısı:** üretime giren her yeni makine önce pilotun 80 referans cevabını (en uzun bağlamlılar dahil) birebir yeniden üretir; tutmazsa o makine kullanılmaz; sürücü sürümü künyeye yazılır |
| F0.17 | **vLLM geçişi** ([ADR-0106](../adr/kararlar-0064-0085.md#adr-0106), [ADR-0107](../adr/kararlar-0064-0085.md#adr-0107), [ADR-0109](../adr/kararlar-0064-0085.md#adr-0109)): sunucuda seçim ölçümleri için vLLM pilotu; kapılar G1 geçerlilik · G2 80 cevap ≤ 213 s · G3 motor etkisi ≤ 0,6 puan, ölçütler pilottan önce kilitli; hasat kapısı örtüşme ≥ %70 → **sonuç:** G1-G3 tek koşuda geçti, ama beş koşuda vLLM aynı ağırlıkla 3,6 p düşük ve ±2,25 p; vLLM ölçüme alınmadı, hasat llama.cpp'de ([#86](../record/kronoloji-75-86.md#86), [#87](../record/kronoloji-87-98.md#87)) |

**Kullanıcı kararları:** eşdeğerlik sonucu (F0.4) · Gemma kapı sonucu (F0.9).
**Tahmin:** §8 (kullanıcı saatine literatür okuması ~5-8 dahil; Modal: pilotlar ~$6 + Qwen τ_g/τ_a seed'leri ~$11).

---

## 3 · F1 — DEV iterasyonu ve ölçüm aletinin doğrulanması *(Aralık 2026–Ocak 2027)*

**Amaç:** her yöntem ailesinin en iyi yapılandırmasını DEV'de seçmek ve hakemin insanla uyumunu test
açılmadan önce bilmek.

| # | iş → doğrulama |
| :-- | :--- |
| F1.1 | **Birlikte eğitim:** her temel modelde tam ORPO, λ 0,1 ve 0,3, SFT öğrenme hızıyla (1e-4), seed 3407 → DEV sonuçları ve künyeler; iki kayıp ayrı izlendi |
| F1.2 | **Ardışık eğitim:** τ_g tabana gömülür (CPU, $0), ORPO τ_a'nın tarifiyle taze adaptörle; β 0,1 ve 0,3, seed 3407. Reddedilen havuz ham modelden ([ADR-0042](../adr/kararlar-0027-0044.md#adr-0042)), ardışık kolun aleyhine sınırlılık → aynı |
| F1.3 | **Gemma'nın tek kolları ve birleştirmesi:** τ_g, τ_a, ham TIES ve norm-min · ayrıca 3408 ve 3409 seed'lerinin τ_g/τ_a'sı (dondurmayı beklemez; Gemma'nın 3407 τ_g/τ_a'sı DEV'de ölçülüp gözle okunduktan sonra, Aralık–Ocak kredisi) → aynı; ‖τ‖ koşulsuz raporlandı |
| F1.4 | **İnsan↔hakem pilotu:** ~80 DEV cevabı, kollara ve iki temel modele yayılmış, kör, kullanıcı okur (~4 saat); DeepSeek iki modda (düşünme açık/kapalı) puanlar. Bağlayıcı mod kapalı; uyum iki modda ölçülür ve raporlanır, modu belirlemez ([ADR-0114](../adr/kararlar-0064-0085.md#adr-0114)) [hakem] → uyum (yüzde, κ, sınıf başına P/R); uyum düşükse hakem istemi dondurmadan önce düzeltilir |
| F1.5 | **Hakem önyargı sondası ve kontrol kalemleri:** ~40 DEV cevabına tek değişkenli bozmalar — uzatma · gerçek ama soruya ait olmayan madde atfı ekleme · şerh/kesinlik cümlesi ekleme-çıkarma · "Düşünce süreci:" açılışı · kaynak sırasını ters çevirme; etiketi bilinen bozuk cevaplar hakem partisine kör karışır [hakem][benchmark] → her hakem ve çekinme dedektörü için karar değişim oranı; Tablo 2'ye ek satır. Tek bir bozma bir hakemin kararlarının %20'sinden fazlasını çevirirse hakem istemi dondurmadan önce düzeltilir ve sonda yeniden koşulur |
| F1.6 | **Okuma aracı:** `judge_agreement.py` kör (hakem kararı okuyucuya gösterilmez) ve katmanlı örnekleme yapar; metrikler: yüzde uyum, Cohen κ, sınıf başına precision/recall, Krippendorff α (insan↔insan), "belirsiz" kategorisi [hakem] → testli |
| F1.7 | **İz↔cevap hakemi:** önce izdeki `KAYNAK n` seçimi ile cevaptaki atıf deterministik eşlenir; kalan kalemlere katı JSON yargı, kaynak sırası iki yönde verilerek ; hakem DeepSeek V4.1 Flash, bağlayıcı hakemle aynı [hakem][halüsinasyon] → F1.4 pilotunda insanla uyumu ölçüldü |
| F1.8 | **Test sorusu üretimi:** üretici Kimi K3 ya da MiniMax M3, seçim bu işin başında ([ADR-0113](../adr/kararlar-0064-0085.md#adr-0113)). İlk 20 soru Türkçe kalitesi için okunur (~30 dk); kötüyse üretici o gün yeniden seçilir. Sonra yeni ~200-225 + ~100 mühürlü, %20 fazlasıyla; kurallar aşağıda (§3.1) → taslak küme ve künyesi; kullanıcı okumasına hazır |
| F1.9 | **İnsan okuma protokolü:** etiket tanımları — cevap ↔ çekinme · altın bağlamdayken susma · isabetsiz atıf · sadakat (iddia düzeyinde; doğrulanabilir iddia ↔ yorum ayrımı) [benchmark] · iz ↔ cevap tutarlılığı · "belirsiz" → protokol F1.4 pilotunda denendi |
| F1.10 | **Genel yetenek kümeleri:** Global-MMLU Türkçe 100 + GSM8K 100; hakemsiz, düşünce açık, ölçüm kartında. F1 ayarlarında da koşulur (DEV seçimi koruma kapısına bakar); F2'de, test üretiminin parçası olarak, üç yolda bütün seed'ler ve tek kollarda 3407 [benchmark] → lisanslar dosyadan okundu, iki ham modelle çıpa koşuldu |
| F1.11 | **DONDURMA ADR'si:** seçilen yapılandırmalar (kural: DEV kütlesi yüksek olan, koruma kapısını DEV'de geçmesi şart; fark gürültü tabanından küçükse 0,1) · düşünce koruma eşiği (genel kayıp ≤5 puan, döngü artışı ≤2 puan; yol haritası §2.5.4) · istatistik planı (birincil ve önceden listelenmiş ikincil kırılımlar; tek kollarla ikincil karşılaştırmalar ve Kapı 5 yalnız seed 3407'de, aynı sorularda eşleştirilir) · kazanan kuralı (kazanan yalnız üç yoldan; ürün yalnız %95 eşleştirilmiş bootstrap'ta `tgta_v1`'i geçerse değişir; ürüne seed 3407) · hakem sürümleri ve modu · kesme sırası ([yol haritası](YAYIN_YOL_HARITASI.md) §5) → ADR test açılmadan commit'lenir; bundan sonra yapılandırma değişmez |

### 3.1 Test sorularının kuralları

- **Katman:** kanun ve madde uzunluğu ([ADR-0069](../adr/kararlar-0064-0085.md#adr-0069)).
- **Tek başına anlaşılır** soru ([#53](../record/kronoloji-53-62.md#53)).
- **Örtüşme denetimi üç düzeyde:** soru yakın-kopyası · altın maddenin eğitim verisinde altın olarak
  geçip geçmediği · üretici şablonu; "eğitimde görülmüş / görülmemiş" kırılımı ikincil, betimsel
  [benchmark][damıtma].
- **Üretici:** yasak aileler OpenAI (eğitim verisinin öğretmeni) · Qwen, Gemma (özneler) · Gemini,
  Claude (Makale 2 rakipleri) · DeepSeek (bağlayıcı hakem) · Zhipu (ikinci hakem) · Mistral (yedek özne). Üretici
  Kimi K3 ya da MiniMax M3 (F1.8, [ADR-0113](../adr/kararlar-0064-0085.md#adr-0113)); modeli,
  sürümü, istemi ve ailesi künyeye yazılır [benchmark].
- **Görev tipi etiketi** (madde ne diyor · koşul/istisna · vaka uygulaması · sayı/süre); katman değil,
  etiket [benchmark].
- **Vatandaş dili dilimi:** ~50 sorunun hukuk terimi kullanmayan birer yeniden ifadesi; ikincil eksen;
  yalnız kazanan ve `tgta_v1` cevaplar (F3.6'dan sonra) [benchmark].
- **Zorluk modelden bağımsız özelliklerle** (tuzak↔altın sözcük örtüşmesi, aynı kanundan komşu madde,
  madde uzunluğu) kurulur; sorular hiçbir modelin çıktısına göre süzülmez [benchmark].
- **Mühürlü parça açık depoya girmez:** depoda yalnız `sha256` özeti ve satır sayısı durur; bir test,
  dosyanın git tarafından izlenmediğini sınar [benchmark].
- **Künye:** odak · dil · kaynak (mevzuat anlık görüntüsü ve `sha256`) · üretim yöntemi · değerlendirme
  türü · göstergeler · miktar · katmanlar · üretici [benchmark].

**Kullanıcı kararları:** F1.4 okuması · F1.11 dondurma.
**Tahmin:** §8 (Modal: Qwen ~$14 + Gemma ~$21-28 + Gemma τ_g/τ_a seed'leri ~$17-23).

---

## 4 · F2 — Test kümesi ve seed'ler *(Şubat–Nisan 2027)*

| # | iş → doğrulama |
| :-- | :--- |
| F2.1 | **Soru okuması (yalnız ret):** kullanıcı yeni ve mühürlü soruları okur (DEV dondurmasından hemen sonra, test açılmadan önce: Ocak sonu–Şubat; vatandaş dili dilimi dahil); düzeltmez, yalnız reddeder. Ret ölçütleri önceden yazılı: soru altın maddeyi tek başına belirlemiyor · cevap altın maddenin dışında bilgi istiyor · Türkçesi bozuk ya da anlaşılmaz · tuzak maddesi soruyu aslında cevaplıyor. Hedef boya katman korunarak rastgele inilir → her ret gerekçesiyle künyede |
| F2.2 | **Test dondurma:** asıl test ve mühürlü parça ayrı, parolalı şifreli arşiv; özel HF deposunda ve yerelde → depoda yalnız düz metnin `sha256`'sı ve satır sayısı; kapı testi yeşil; düz metin git tarafından izlenmiyor |
| F2.3 | **Seed'ler:** τ_g/τ_a seed'leri F0.15 ve F1.3'te eğitildi. Dondurmadan sonra yalnız birlikte ve ardışık seed'ler kalır, sırayla Qwen 3408 → Qwen 3409 → Gemma 3408 → Gemma 3409 (Şubat–Mart kredisi; 3407 kolları Qwen'de `v1` ve F1'den, Gemma'da F1'den). Gemma 3409 kesme sırasında olduğu için sonda. Hepsi A100'de, kilitli ortamda. Test dondurulunca hazır kollardan başlayarak test cevapları ölçüm kartında, kollar hazır oldukça şifreli üretilir (Şubat–Nisan), okunmaz ve puanlanmaz; tek kollar için yalnız 3407; `tgta_v1`'in test cevapları testin tamamında (eski 75 soru dahil) ölçüm kartında yeniden üretilir, eski dizüstü cevapları kullanılmaz; F0.10'da ağırlıkları farklı çıkan iki dosya varsa ikisinin de ([ADR-0098](../adr/kararlar-0064-0085.md#adr-0098)) → her koşunun künyesi ortam kilidini geçti; kredi yetmezse [`EGITIM_ORTAMI.md`](../yontem/EGITIM_ORTAMI.md) §4 |
| F2.4 | **Birleştirmeler ve GGUF:** her seed için ham TIES (CPU, $0) ve Q4_K_M → her artefaktın `kollar.md`'de satırı var |
| F2.5 | **Yeni adaptörlerin yedeği** → kopya `sha256` eşleşmesi |
| F2.6 | **Makalenin giriş ve ilgili çalışmalar bölümleri** (F0.11'in `knowledge/ozgunluk/` notundan) → taslak |

**Tahmin:** §8 (kullanıcı saatine giriş ve ilgili çalışmalar ~7-10 dahil; Modal Şubat–Mart kredisinden).

---

## 5 · F3 — Son ölçüm *(Mayıs 2027)*

| # | iş → doğrulama |
| :-- | :--- |
| F3.1 | **Kayma çıpasının tekrarı:** F0.6'daki 80 DEV cevabı aynı hakemlerle → fark gürültü tabanını aşarsa puanlama durur ve kayda geçer |
| F3.2 | **Test bir kez açılır** (kullanıcı kararı; "açıldı" anı puanlamanın başladığı andır). Bütün cevaplar F2'de tek tip ölçüm kartında, kilitli llama.cpp bayraklarıyla üretilmiştir (künyede kart ve makine) → kesik oranı ≤%5; `recall@10` künyede |
| F3.3 | **Puanlama:** DeepSeek V4.1 Flash bütün kollar · GLM-5.3-Flash ([ADR-0113](../adr/kararlar-0064-0085.md#adr-0113); kabul şartları tutmazsa `claude-sonnet-5`) iki temel modelde birincil karşılaştırma, seed 3407 · iz↔cevap hakemi · düşünce koruma ölçüleri · genel yetenek kümeleri · kol başına cevap uzunluğu ve atıf yoğunluğu [hakem][IT] → F0.5 kapısı geçti; her koşunun künyesi var |
| F3.4 | **RQ2:** puanlama tarafındaki düzeltmeler bütün kollarda tek tek; üretim tarafındaki eski hâl (`RRF_K` 60 + önsöz) birincil karşılaştırmada, iki temel model × 1 seed (F2'deki üretimin parçası) → Tablo 2 |
| F3.5 | **İstatistik:** soru × seed eşleştirilmiş bootstrap · Wilson aralıkları · iki birincil karşılaştırmaya Holm düzeltmesi · "temel modele bağlı" hükmü yalnız farkların farkı %95 güvenle 0'dan ayrılırsa, yoksa "bağımlılığa kanıt yok" · dondurma ADR'sinde listelenen ikincil kırılımlar, betimsel → Tablo 1 |
| F3.6 | **Kazanan seçimi:** üç yoldan, dört kapı; ürün yalnız kazananın kütlesi (seed ortalaması) `tgta_v1`'i eşleştirilmiş bootstrap'ta %95 güvenle geçerse değişir; ürüne kazananın seed 3407 ağırlıkları gider (3407 bir kapıda kalırsa 3408, o da kalırsa 3409; üçü de kalırsa `tgta_v1`; dört boşluğun kararı [yol haritası](YAYIN_YOL_HARITASI.md) §2.3) → tek kayıt (kronoloji): kuralın uygulanışı, sayılar, ürüne giden dosyanın `sha256`'sı; ardından vatandaş dili dilimi kazanan ve `tgta_v1` için üretilip puanlanır |

**Kullanıcı kararları:** testi açma (F3.2) · kazanan (F3.6).
**Tahmin:** §8 (kullanıcı saatinin ~3-4'ü F3'te).

### 5.1 F3b — Uygulamanın kazananla güncellenmesi *(Haziran 2027; yalnız kazanan değişirse)*

| iş | doğrulama |
| :--- | :--- |
| GGUF (Q4_K_M), `sha256`, HF'te pinli revizyon ([ADR-0071](../adr/kararlar-0064-0085.md#adr-0071)) | `indir` kimlik kapısı yeni dosyayı kabul eder, eskisini reddeder |
| konteyner rejim kilidi | `tests/depo/test_konteyner.py` yeni modelin bayraklarıyla yeşil |
| düşünce kapatma | `servis.answer()`'ın iki geçişli kapatması ([ADR-0080](../adr/kararlar-0064-0085.md#adr-0080)) temel modelin kapanış işaretine göre parametreli; boş cevap 0/80 |
| ürün yolu ölçümü | konteyner API'si üzerinden 80 DEV sorusu; ölçüm hattıyla fark raporlandı (emsal [#70](../record/kronoloji-63-71.md#70)) |
| VRAM tablosu | 4.096 · 32.768 · 131.072 bağlamda ölçüldü; 4.096'da ≤8 GB |
| model kartı | `MODEL_CARD.md` güncel; HF sürümü `scripts/hf_kart.py` ile üretildi |

`v0.5` yedek olarak durur. Kazanan `tgta_v1` ise bu adımda iş yoktur.

---

## 6 · F4 — İnsan doğrulaması *(Mayıs–Haziran 2027)*

| # | iş → doğrulama |
| :-- | :--- |
| F4.1 | **Örneklem:** ~300 cevap; kollara ve iki temel modele yayılmış; zorunlu tabakalar: bütün isabetsiz atıf kalemleri · hakemlerin ayrıştığı kalemler · ajanın eski okuduğu kalemler [hakem] → örneklem dosyası ve künyesi |
| F4.2 | **Okuma:** etik kurul F5.2'de ele alınır · kullanıcı hepsini kör okur · gönüllü öğrenciler (ücretsiz; yazılı bilgilendirme ve onam, makalede teşekkür, kişisel veri yok) yaklaşık üçte birini bağımsız ikinci kez okur · hukukçu yalnız isabetsiz atıf anlaşmazlıklarını karara bağlar → etiket dosyaları ve onam formları |
| F4.3 | **Uyum tabloları:** insan↔insan (κ, Krippendorff α) · insan↔hakem, dedektör ve ajan (yüzde uyum, κ, sınıf başına P/R), "belirsiz" ayrı → tablo; isabetsiz atıf ekseninde ajan-okuyucunun insanla uyumu raporlandı |

**Tahmin:** §8.

---

## 7 · F5 — Yazım ve gönderim *(Haziran–Eylül 2027)*

| # | iş → doğrulama |
| :-- | :--- |
| F5.0 | **DEÜ FBE kuralları** (yazıma geçerken): tez dili · mezuniyet için yayın şartı · yayımlanmış makalenin tezde kullanımı · tezden üretilen yayında danışman adı (zorunluysa "tek yazar" planı değişir) · programa başlamadan önceki işin teze sayılması · üretken YZ kuralı → çıkan şart ilgili belgeye tek satır |
| F5.1 | **Makale taslağı:** yöntem bölümü (F1.11'in dondurma ADR'sinden) yazılır; giriş ve ilgili çalışmaların (F2.6) üstüne Tablo 1-2, insan doğrulaması, sınırlılıklar (tek dil, LLM üretimi sorular, ikinci hakemin kapsamı, τ_g'nin künyesizliği, ardışık tabanın negatif kaynağı, tek kolların tek seed'le ölçülmesi) → tam metin |
| F5.2 | **Ekler ve beyanlar:** tekrar üretim eki (ortam kilidi, künyeler, hangi kolun nerede eğitildiği) · ARR'nin sorumlu araştırma kontrol listesi · sınırlılıklar ve etik bölümü · YZ yardımı beyanı → kontrol listesinin her maddesi cevaplı |
| F5.3 | **Anonim sürüm:** proje adı, depo ve HF bağlantıları anonimleştirilir; kod ve veri anonim bir kopyadan sunulur → metinde, PDF üst verisinde ve eklerde kimlik yok; anonim kopya dışarıdan açılıyor |
| F5.4 | **Dış okuyucular:** 1-2 kişi → yorumlar işlendi |
| F5.5 | **arXiv:** ARR'nin ön baskı kuralına uygun zamanda (ARR: isimli ön baskı serbest; gönderimde "no non-anonymous preprint" seçilirse meta-hakem raporlarına kadar yok; aclrollingreview.org/cfp, 2026-10-17) → yüklendi |
| F5.6 | **ARR gönderimi:** ilk uygun döngü; OpenReview profili (Ekim 2026'dan bütün yazarlara, ORCID'li) ve hizmet katkıcısı şartı ([yol haritası](YAYIN_YOL_HARITASI.md) §2.8) → gönderildi |
| F5.7 | **Kapanış:** `develop` → `master` birleştirmesi ([ADR-0111](../adr/kararlar-0064-0085.md#adr-0111)) · birleştirme commit'i **`v1`** olarak etiketlenir; model kartı, HF kartı ve GGUF dosya adı `v1`'e geçer → Checkpoint 1 tamam (§0) |

**Tahmin:** §8 (kullanıcı saatine yöntem bölümü ~3-4 dahil; giriş ve ilgili çalışmalar F2.6'da yazılır).

---

## 8 · Özet takvim ve bütçe

| aşama | zaman | kullanıcı saati | Modal plan | Modal harcanan | nakit plan | nakit harcanan |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| F0 | Ekim sonu–Kasım 2026 | ~10-14 | ~$17 + ölçüm kartı pilotu ~$3-5 | $5,15 | ~$4,7 + F0.10 ~$2 | ~$4,7 |
| F1 | Aralık 2026–Ocak 2027 | ~7-9 | ~$52-65 | — | ~$4,7 + test sorusu üreticisi | — |
| F2 | Şubat–Nisan 2027 | ~15-22 | ~$42-49 | — | — | — |
| F3 + F3b | Mayıs–Haziran 2027 | ~5-8 | — | — | ~$17-20 | — |
| F4 | Mayıs–Haziran 2027 | ~12-15 | — | — | — | — |
| F5 | Haziran–Eylül 2027 | ~33-49 | — | — | — | — |
| **TOPLAM** | | **~82-117** | **~$111-131** + ölçüm kartı | **$5,15** | **~$28-31** + test sorusu üreticisi + ölçüm kartı (Modal kredisine sığmazsa ≤$75) + OpenRouter kredi ücreti | **~$4,7** |

Nakit plan, hakem çağrılarının ölçülen koşu fiyatıyla hesabıdır ([#89](../record/kronoloji-87-98.md#89)); toplam ~$28-31
F0'da harcanan ~$4,7'yi içerir, [YAYIN](YAYIN_YOL_HARITASI.md) §2.7'nin kalem satırları (hesap yöntemi orada) yalnız kalan
koşuları (~$24-27) sayar. Koşu sayıları F0.10'un kol × mod listesiyle kesinleşir. Modal harcanan: Modal paneli, hesap `rfetha`,
Ekim 2026 ([#83](../record/kronoloji-75-86.md#83)'teki 2026-10-17 notu). Bağlayıcı hakem kapalı modda
([ADR-0114](../adr/kararlar-0064-0085.md#adr-0114)); açık mod seçilseydi hakem nakdi ~$157-180 olurdu.
Her iş paketi başında bir harcama tavanı konur (onay, kart yorumuna); paket kapanınca gerçek harcama bu tabloya yazılır.

Modal giderleri iki hesabın aylık $30'ar kredisiyle Kasım 2026–Mart 2027'ye yayılır; kredi yetmezse
[`EGITIM_ORTAMI.md`](../yontem/EGITIM_ORTAMI.md) §4. Eylül hedefi korunur; takvimin öne gelmesiyle kazanılan
~1-2 ay tampondur. Riskler ve kesme sırası: [yol haritası](YAYIN_YOL_HARITASI.md) §5.

---

## 9 · Checkpoint 1 dışında kalanlar

| iş | yeri |
| :--- | :--- |
| `v2` — kazananın üstüne GRPO | Checkpoint 2 ([yol haritası](YAYIN_YOL_HARITASI.md) §3); pilot ve ödül ADR'si Haziran 2027'de, koşular Temmuz–Ekim 2027'de, Makale 1'in yazımıyla paralel |
| mevzuat kapsam + tazelik (40.496 → ~288 bin madde) | Checkpoint 2'den sonra ([ADR-0083](../adr/kararlar-0064-0085.md#adr-0083) §EK) |
| canlı `bedesten` API (B6) · tazelik boru hattı · barındırma (S9) · tablo satırları (B9) | Checkpoint 2'den sonra |
| ajan uygulaması (omurga, belgeler, üretim) ve web arayüzü | ayrı hat; omurga Ekim–Aralık 2027, dilimler sıralı, tez yazımında durur ([`ROADMAP_uygulama.md`](ROADMAP_uygulama.md), [ADR-0104](../adr/kararlar-0064-0085.md#adr-0104), [ADR-0105](../adr/kararlar-0064-0085.md#adr-0105)); barındırma (S9) ve canlı `bedesten` yine Checkpoint 2'den sonra |
| araç kullanımının eğitimi (RL) | Checkpoint 2'den sonra, ayrı ürün turu; yalnız araç çağırma ölçümü açık bir boşluk gösterirse açılır; Makale 2'nin ödülüne girmez ([ADR-0105](../adr/kararlar-0064-0085.md#adr-0105)) |
| açık ürün kusurları | panoda `bug` etiketli kartlar (6 → #76, 12b → #77; [ADR-0083](../adr/kararlar-0064-0085.md#adr-0083)'ün sicili tarihtir) |
| `recall_taban.json` · korpus bütünlüğü (`4857/Madde 111` yinelenmesi) · `terazi` yinelenen atıf · `models/` temizliği · TUI gözle doğrulama | ucuz işler; boş zamanda |
| S10: sorumluluk ibaresinin nihai hukuki metni | hukukçu görüşü bekliyor |
| S12: paralel slot (`-np`) | ertelendi; paralel slot cevap metnini değiştiriyor ([ADR-0062](../adr/kararlar-0045-0063.md#adr-0062)) ve ölçüm ortamı Checkpoint 1 ve 2 boyunca kilitli |
