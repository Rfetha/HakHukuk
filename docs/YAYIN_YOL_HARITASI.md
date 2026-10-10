# Yayın yol haritası — Makale 1, Makale 2, tez

> **Bu belge ne:** HakHukuk'tan hakemli yayına ve yüksek lisans tezine giden yolun yön belgesi.
> 2026-10-10'da bir danışmanlık oturumunda, her bölüm tek tek konuşularak ve onaylanarak yazıldı.
> **Bir plan değildir** (kutucuk taşımaz); her aşama başlarken kendi planı yazılır (ADR-0056: en çok
> bir canlı plan). Ürün yol haritası ayrı belgedir (`docs/ROADMAP.md`).
>
> **Bu belgedeki kararlar henüz ADR değildir.** Kullanıcı bu oturumda mevcut dosyalara
> dokunulmamasını seçti; kararlar F0'ın ilk işinde karar defterine **ADR-0089** ve sonrası olarak
> işlenir. Mevcut belgelerle çelişkiler §9'da işaretlidir.
>
> **Sayı kuralı:** kayıttan gelen her sayı dosyasıyla birlikte yazılıdır. "Tahmin" yazan her sayı
> kayıttaki koşu sürelerinden ya da web fiyatlarından türetilmiş bir **hesaptır, ölçüm değildir**;
> her bloğun ilk işi o birim maliyeti küçük bir pilotla ölçmektir.

---

## 0 · Bir bakışta

| | Makale 1 | Makale 2 | Tez |
| :--- | :--- | :--- | :--- |
| **soru** | Çatışan iki beceriyi (temellendirme ↔ çekinme) tek modelde toplamanın en iyi yolu hangisi, ve bu hükümlerden hangileri ölçüm düzeltmesine dayanıklı? | Doğrulanabilir ödülle RL (GRPO) isabetsiz atıfı ve M2b'yi, çekinmeyi ve düşünceyi bozmadan düzeltiyor mu; düşünce hedefe hizalanıyor mu? | Makale 1 (+ Makale 2) + sistem + ölçüm dersleri |
| **yöntem** | SFT + ORPO; **RL yok** | GRPO, isabet terimli ödül | — |
| **temel model** | Qwen3.5-4B (3 seed) + Gemma 4 E4B (1 seed; yedek Ministral 3 3B Reasoning) | Makale 1'in Qwen'deki kazananı | — |
| **hedef yer** | ARR → ana konferans / Findings → sonraki döngü → dergi | ARR ya da COLM (2. yılda karar) | DEÜ Fen Bilimleri Enstitüsü |
| **gönderime hazır** | ~Eylül 2027 | ~Haziran 2028 | savunma ~yaz 2028 |
| **GPU** | ~$60-70 (tahmin), Modal aylık kredisinden | ~$75-130 (tahmin), paket pilottan sonra seçilir | — |
| **nakit** | ~$30-35 hakem (tahmin) | ~$30-50 rakipler + hakem (tahmin) | — |
| **senin saatin** | ~75-110 (tahmin) | ~60-85 (tahmin) | — |

**Mezuniyet güvencesi:** RL hiç olmasa bile tez malzemesi Eylül 2027'de tamamdır (§6.4). Çalışan
uygulama (`v1.0`, konteyner) hiçbir aşamada bozulmaz.

---

## 1 · Hedef, kısıtlar ve oturumda alınan kararlar

### 1.1 Kısıtlar

| kısıt | değer |
| :--- | :--- |
| kariyer hedefi | endüstride LLM post-training araştırmacısı; ACL ailesi / COLM düzeyinde hakemli yayın |
| yazarlık | **tek yazar** (kullanıcı kararı) |
| süre | dönem içinde haftada **5 saatten az**; yoğun okuma/yazma tatillere |
| bütçe | **$100-500** (GPU + API + gerekirse hukukçu) |
| insan okuyucu | önce kullanıcı · gönüllü hukuk öğrencileri · şirket aracılığıyla bir hukukçu (zor) |
| tez | HakHukuk + RL devamı; mezuniyet **~2028 yazı** (2 yıl) |
| olumsuz sonuç | **yayımlanır** — iterasyon serbest, ama DEV'de ve önceden yazılmış durma noktasına kadar (§3.4) |
| ilke | **eldekini olabildiğince kullan; sıfırdan başlama** |

ACL 2026'nın kabul listelerinde tek yazarlı makale oranı (sitedeki yazar listelerinden sayıldı,
2026-10-10): ana konferans 31/2.304 (%1,3) · Findings 27/2.163 (%1,2) · Industry 9/153 (%5,9).
Bu bir **kabul oranı değildir** (tek yazarlı gönderim sayısı bilinmiyor); ARR çift-kördür, yazar
sayısı hakeme görünmez. Tek yazarlığın bedeli iç hakem yokluğudur → dış okuyucu adımı (§5).

### 1.2 Karar günlüğü (2026-10-10, kullanıcı)

| # | karar |
| :-- | :--- |
| K1 | Tek büyük makale; yukarıdan aşağı gönderim. Ara yayın **plan dışı**, yalnız ek saat istemiyorsa (§5) |
| K2 | Çerçeve: kontrollü post-training çalışması + ölçüm düzeltmesinin bu hükümlere etkisi (A yolu) |
| K3 | Makale 1'de RL yok; RL Makale 2 ve tezin ikinci yarısı |
| K4 | Kapsam kesintileri: ucuz birlikte-eğitim (karışık SFT) **atıldı** · on-policy kontrol **atıldı** · `h1` satırları **atıldı** · DEV iterasyonu aile başına **2** yapılandırma · ikinci hakem yalnız birincil karşılaştırma, 1 seed |
| K5 | Korunanlar: ardışık eğitim · Qwen'de **3 seed** · test **200 + 100** · ikinci temel model (1 seed, kesin değil) · genel yetenek kontrolü |
| K6 | Donanım: **Modal A100-40GB** ana yol; kredi ay içinde biterse **Vast A100**, kurallı (§5.2, [`EGITIM_ORTAMI.md`](EGITIM_ORTAMI.md)) |
| K7 | İkinci temel model: **Gemma 4 E4B** birincil aday, **Ministral 3 3B Reasoning** yedek; seçim kapıdan sonra kesinleşir (§3.5) |
| K8 | Düşünce: Makale 1 **korur ve ölçer**; düşüncenin hedefe **hizalanması** Makale 2'nin işi |
| K9 | Eldekini kullan: `v1` kolları **1. seed**; eski donmuş TEST son teste **katılır**; birleştirme ailesinin DEV iterasyonu **yapılmış sayılır** |
| K10 | HMGS Makale 1'de **yok**; rakip (kapalı) modeller **Makale 2'de**; Makale 1'de bütçe kalırsa tek ucuz referans çizgisi |
| K11 | Korpus turu (40.496 → ~288 bin madde) **Makale 2 bitene kadar bekler** |
| K12 | Tek nüsha iki şey **yedeklenir**: eski git geçmişi bundle'ı ve `v1` adaptörleri |
| K13 | Eğitim ortamı kilidi **üç parça**: md + yaml + betik başı kontrolü |
| K14 | Yeni test üretilirken ~100 soruluk **mühürlü parça** ayrılır |
| K15 | Makale 2'nin ödülü **isabet terimli**; GRPO paketi pilottan sonra seçilir |

**Burs (Modal startup/akademik kredisi) gelirse geri eklenecekler:** on-policy kontrol · iterasyonda
aile başına 4 yapılandırma · bütün kollarda ikinci hakem · Gemma'da 3 seed. Plan bursa dayanmaz.

---

## 2 · Makale 1 — iddia ve hedef yer

### 2.1 Sorular

**RQ1 (post-training).** Temellendirme (RAFT biçimli SFT) ile çekinme (ORPO) küçük modelde
çatışıyor. Dört yol aynı ölçümde karşılaştırılır: tek kollar · ayrı kollar + birleştirme (ham TIES)
· tek eğitimde birlikte öğretme · ardışık eğitim.
Çatışmanın öncülü ölçülmüş: τ_g tek başına M2b **0,506**, τ_a tek başına kütle **%41,2**
([`kollar.md`](record/kollar.md) satır 303-304). Karar kuralı ön-kayıtlı: **Kapı 5** — `min(temellendirme,
çekinme)` bileşiği, her iki taban da geçilmeli ([ADR-0037](adr/kararlar-0027-0044.md#adr-0037)). Formül
korunur, sayılar yeni birimde yeniden türetilir (emsal [ADR-0061](adr/kararlar-0045-0063.md#adr-0061)
Karar 2).

**RQ2 (ölçüm).** RQ1'in hükümlerinden hangileri eski alet ↔ düzeltilmiş alet arasında yön
değiştiriyor? Kayıtta dört vaka hazır: önsözün etkisi +1,5 → −4,6 p
([ADR-0058](adr/kararlar-0045-0063.md#adr-0058)) · `k=10` kapı hükmü ret → kabul
([#54](record/kronoloji-53-62.md#54)) · ara kapının 2. gözlemi geçti → düştü
([ADR-0045](adr/kararlar-0045-0063.md#adr-0045)) · birleştirmenin M2 katkısı +0,020 → +0,000
([`kollar.md`](record/kollar.md) satır 319-332).

### 2.2 Varılacak yer: iki tablo

```
TABLO 1 — tek modelde iki beceri: hangi yol?
(yeni test · Qwen'de 3 seed ortalaması · Gemma'da 1 seed)

yol                                     kütle  çekinme(M2/M2b)  gereksiz red  yanlış madde  ezber(M5)↓  düşünce koruma
yalnız τ_g (SFT)                        ...
yalnız τ_a (ORPO)                       ...
ayrı kollar + ham TIES   (bugünkü yol)  ...
birlikte eğitim (SFT+ORPO tek koşu)     ...    ← bugün yok
ardışık (SFT → ORPO)                    ...    ← bugün yok

TABLO 2 — eski aletle ölçseydik ne derdik?
hüküm                                   eski alet      düzeltilmiş alet
birleştirme M2'ye katkı                  +0,020         +0,000
önsözün kütleye etkisi                   +1,5 p         −4,6 p
... Tablo 1'in yeni hükümleri
```

### 2.3 Kapsam dışı

"Türkçe hukuk asistanı" anlatısı (yalnız deney ortamı) · rakip modellere karşı "geçtik" iddiası
(Makale 2, K10) · konteyner, araç katmanı, ürün yolu · korpus turu (K11) · HMGS (§4.6) ·
RS-FT ([ADR-0035](adr/kararlar-0027-0044.md#adr-0035)) · `τ_register`.

### 2.4 Hedef yer ve düşme merdiveni

1. ARR → ACL / EMNLP / NAACL / EACL ana konferansı; **Findings kabul edilebilir sonuç**.
2. Ret → hakem yorumlarıyla **sonraki ARR döngüsü**.
3. Yine ret → **dergi**: TMLR · Natural Language Engineering · Language Resources and Evaluation.

COLM ayrı bir alternatiftir; aynı makale aynı anda iki yere gönderilemez. Tarihler bu belgede
**yoktur** → §8'deki kontrol listesi.

---

## 3 · Makale 1 — deney blokları

### 3.1 Eldekinin kullanımı (K9)

| eldeki | nasıl kullanılıyor |
| :--- | :--- |
| `tg_v1`, `ta_v1`, `tgta_v1` | **1. seed**, aynen; yeniden eğitilmez. `tgta_v1` yalnız güncel DEV biriminde **yeniden ölçülür** (13 soru onarıldı, [ADR-0067](adr/kararlar-0064-0085.md#adr-0067); bütçe 1536'ya eşitlendi, [ADR-0070](adr/kararlar-0064-0085.md#adr-0070)) — dizüstünde, $0. τ_g'nin veri klasörü künyede yok; davranışsal kanıt `raft_scrubbed`'ı gösteriyor ([`kollar.md`](record/kollar.md) satır 109-120) — makalede açıkça yazılır |
| birleştirme varyantları (ham, min, ortalama, modül-başına) | birleştirme ailesinin DEV iterasyonu **yapılmış** ([ADR-0052](adr/kararlar-0045-0063.md#adr-0052), [ADR-0053](adr/kararlar-0045-0063.md#adr-0053)); silinen ara dosyalar adaptörlerden $0'a yeniden üretilir |
| eski donmuş TEST (40 + 35) | son testin **bir parçası**; yalnız `tgta_v1` için bir kez açıldı ([ADR-0077](adr/kararlar-0064-0085.md#adr-0077)), hiçbir seçim üzerinde yapılmadı. Sonuçlar iki parça için ayrıca da raporlanır |
| DEV (80 + 70), arama katmanı, ölçüm hattı, hakem altyapısı | olduğu gibi |
| dört "hüküm döndü" vakası | Tablo 2'nin ilk satırları |
| ajanın eski "göz" okumaları | insan doğrulamasının karşılaştırma tarafı (§4.3) |
| konteyner, paket, kart hattı | çalışan uygulama; `v1.0` yedek kalır |
| ADR'ler, kronoloji | yöntem eki ve tezin "ölçüm dersleri" bölümü |

**İstisna (düşük ihtimal):** F0'da τ_g v1'in hassasiyet rejimi yeniden üretilemezse `v1` makalede 1.
seed olamaz; yeni bir 1. seed eğitilir (~$6, tahmin), `v1` ürün olarak kalır.

### 3.2 Yeni olanlar

güçlü birlikte eğitim · ardışık eğitim · 2. ve 3. seed'ler · Gemma (1 seed) · ~200-225 yeni test
sorusu + ~100 mühürlü soru · insan doğrulama okuması.

### 3.3 Kollar

```
1. temel model (Qwen3.5-4B) — her seed için:
  ham Qwen ── SFT (raft_scrubbed) ──► τ_g ┐
  ham Qwen ── ORPO (orpo_abstain_cp2c) ► τ_a ┴─► ham TIES ─► birleştirme kolu
  ham Qwen ── TEK eğitim: aynı SFT verisi + aynı ORPO çiftleri ──► birlikte-eğitim kolu   (yeni kod)
  ham Qwen ── SFT ──► τ_g ── üstüne ORPO ──► ardışık kol

seed:  1 = v1 (3407) · 2 ve 3 = yeni (değerleri EGITIM_ORTAMI.md'de koşudan önce sabit)
2. temel model (Gemma 4 E4B): aynı dört kol, 1 seed, dondurulmuş reçete AYARSIZ taşınır
```

**Birlikte eğitimin neden "güçlü" olduğu:** senin yönteminin kullandığı bilginin tamamını (ORPO'nun
reddedilen tarafı dahil) kullanır. Atılan ucuz sürüm (düz karışık SFT) reddedilen tarafı
kullanmıyordu ve 12B hattında düz SFT çekinmeyi sıfırlamıştı
([`gemma4-12b-dersler.md`](adr/gemma4-12b-dersler.md) A2.1) — hakem onu "kasten zayıf rakip" sayardı.

### 3.4 DEV iterasyonu ve dondurma

- İterasyon **yalnız DEV'de**; son hüküm hiç bakılmamış testte **bir kez** okunur.
- **Eşit bütçe:** birlikte eğitim ve ardışık eğitim aileleri ikişer yapılandırma (örn. karışım oranı,
  öğrenme hızı); birleştirmenin iterasyonu zaten yapılmış. Denenen **her** yapılandırmanın DEV sonucu
  eke girer ([ADR-0037](adr/kararlar-0027-0044.md#adr-0037): "aynı prosedür tabanlara da uygulanır").
  Şerh: birleştirme ailesi 3 geçerli varyantla iterasyon görmüş, diğerleri 2 ile — bu asimetri
  makalede yazılır.
- **Dondurma ADR'si koşudan önce:** seçilen yapılandırmalar · düşünce koruma eşiği · istatistik planı
  · birincil metrik ve birincil karşılaştırma.
- Test açıldıktan sonra gelen yeni fikir **yeni hipotezdir**; aynı testte denenmez.

### 3.5 İkinci temel model kapısı (K7)

CLAUDE.md'nin altı maddelik kapısı + bu turun iki ek maddesi:

| madde | Gemma 4 E4B için not |
| :--- | :--- |
| lisans | HF duyurusu "Apache 2" diyor; **kayıt çelişiyor**: Gemma 4 için "Apache-2.0'ın üstüne Prohibited Use Policy" ([#39](record/kronoloji-39-52.md#39)). Lisans dosyası okunarak çözülür |
| şablon render'ı gözle | bu ailenin `enable_thinking` dalı 12B hattında sessizce bozulmuştu ([`gemma4-12b-dersler.md`](adr/gemma4-12b-dersler.md) A4.2) |
| düşünce kapatma | zorunlu kapatma bugün `</think>`'e göre yazılı; Gemma'nın kapanış işareti farklı → base'e göre parametre |
| LoRA hedefleri | yalnız metin kulesi (görüntü ve ses kuleleri dışarıda; Qwen'deki `all-linear` tuzağının eşi, [ADR-0030](adr/kararlar-0027-0044.md#adr-0030)) |
| maliyet | gömme tablolarıyla 8B → koşu başına Qwen'in ~1,5-2 katı (tahmin) |
| **düşünce davranışı (ek)** | ham modelin kendi kapatma ve döngü oranı eğitimden önce ölçülür; Gemma'nın kendi çıpası |
| **Türkçe taban (ek)** | ham E4B ile DEV'de tek M1 koşusu (~$0,2); tabana yapışıksa yedeğe geçilir |

Aile dışlaması: özneler Qwen ve Gemma, hakemler OpenAI ve Anthropic — çakışma yok.
Gemma da Ministral de kalırsa Makale 1 tek temel modelle yazılır, sınırlılık açıkça yazılır
([ADR-0028](adr/kararlar-0027-0044.md#adr-0028) (a)) ve gerçekçi hedef Findings ya da dergidir.

### 3.6 Maliyet kalemleri ve kararlar

Birim fiyatlar §10'daki kaynaklardan; koşu süreleri kayıttan: SFT A100'de ~2,1 sa
([ADR-0033](adr/kararlar-0027-0044.md#adr-0033)), ORPO 36,5 dk ([#48](record/kronoloji-39-52.md#48)).
Bütün tutarlar **tahmin**, Modal A100-40GB ($2,10/sa) fiyatıyla.

| # | kalem | karar | ~$ |
| :-- | :--- | :--- | ---: |
| 1 | pilot | atılamaz | 2 |
| 2 | temel düzeltmeler (hassasiyet, bundle erişimi) | atılamaz | 0 |
| 3 | τ_g + τ_a, Qwen, seed 2-3 | atılamaz | ~11 |
| 4 | güçlü birlikte eğitim, Qwen, 3 seed | atılamaz | ~17 |
| 5 | `gpt-4o-mini` hakem, bütün kollar (×1,6 dahil) | atılamaz | 13-19 (nakit) |
| 6-7 | test üretimi + kör payda + RQ2 | atılamaz | 3-5 (nakit) |
| 8 | insan doğrulaması | atılamaz | 0 (saat) |
| 9 | ardışık eğitim, 3 seed | tutuldu | ~4 |
| 10 | Qwen'de 3 seed | tutuldu | (3-4'e dahil) |
| 11 | DEV iterasyonu | **kısıldı** → aile başına 2 | ~14 |
| 12 | ikinci hakem | **kısıldı** → birincil karşılaştırma, 1 seed | ~9 (nakit) |
| 13 | test 200 + 100 | tutuldu | <1 |
| 14 | on-policy kontrol | **atıldı** — sınırlılık: "ardışık taban ham base'den toplanan negatiflerle eğitildi; sapma lehimize" ([ADR-0042](adr/kararlar-0027-0044.md#adr-0042)) | (−25) |
| 15 | Gemma, 1 seed | tutuldu | ~19-25 |
| 16 | `h1` satırları | **atıldı** | (−2) |
| 17 | genel yetenek kontrolü | tutuldu | 0 |

Kaydın ölçtüğü gerçek API faturası hesaplanan tutarın **1,596 katı** çıkmış
([#64](record/kronoloji-63-71.md#64)); hakem kalemleri bu payla yazıldı.

---

## 4 · Makale 1 — ölçüm

### 4.1 Test kümesi

- **Bileşim:** eski TEST (40 + 35) + **~200-225 yeni** soru (toplam ~200 temel + ~100 tuzak) +
  **~100 mühürlü** soru (K14; 2. yılın sonuna kadar açılmaz).
- **Yeni sorular eski kusurları taşımaz:** kanun **ve madde uzunluğuna** göre katmanlı (DEV↔TEST
  farkının %81'i katmanlama eksikliğindendi, [ADR-0069](adr/kararlar-0064-0085.md#adr-0069)) · tek
  başına anlaşılır (eski soruların ~%22'si belirsizdi, [#53](record/kronoloji-53-62.md#53)) · eğitim
  verisiyle örtüşme denetimi.
- LLM üretir (<$1); **kullanıcı netlik için tek tek okur** (~4-7 sa yeni + ~2-3 sa mühürlü, F2).
- Bir kez dondurulur, bir kez açılır.
- Güven aralığı genişliği (%10'luk oran, hesap): n=80'de 13,4 puan
  ([ADR-0083](adr/kararlar-0064-0085.md#adr-0083) EK-2) → n=200'de ~8 puan.

### 4.2 Hakemler

`gpt-4o-mini` bütün kolları puanlar (bağlayıcı). `claude-sonnet-5` yalnız **birleştirme ↔ güçlü
birlikte eğitim**, 1 seed (gerçek maliyet 80 cevapta ~$1,86, [#64](record/kronoloji-63-71.md#64)).
`:batch` varyantı bu yoldan kullanılamaz (senkron çağrıya 404). Rakip yok → Claude ailesinden ajan
Claude cevabı okumaz; aile dışlaması bu katmanda da sağlanır.

### 4.3 İnsan doğrulaması

Eski "göz" katmanını **ajan** okumuştu (kullanıcı, 2026-10-10). Makaledeki yer-gerçeği insandır:

- **Protokol önceden yazılır:** cevap ↔ çekinme · altın bağlamdayken susma · isabetsiz atıf ·
  iz ↔ cevap tutarlılığı.
- **Kör:** okuyucu kolu görmez, sıra karışık.
- **Örneklem ~300 cevap**, kollara yayılmış; ajanın eski okuduğu kalemleri de içerir.
  Kullanıcı hepsini okur (~10-12 sa, F4) · gönüllü öğrenciler ~üçte birini bağımsız ikinci kez okur ·
  hukukçu **yalnız** isabetsiz atıf anlaşmazlıklarına bakar (~1-2 sa).
- **Raporlanan:** insan↔insan uyumu · insan↔dedektör · insan↔hakem · insan↔ajan uyumu. Kalan binlerce
  cevabı bu aletler puanlar.
- İsabetsiz atıfın otomatik vekili **yok** ve bu ölçülmüş ([ADR-0066](adr/kararlar-0064-0085.md#adr-0066));
  o eksende ajan-okuyucu kullanılır, insanla uyumu raporlanır.

### 4.4 Düşünce koruma ekseni (K8)

| ölçü | ne söyler | alet |
| :--- | :--- | :--- |
| kendi kapatma oranı | düşünceyi kendi bitirebiliyor mu | var (zorunlu kapatma sayacı) |
| döngü oranı | iz tekrar döngüsüne giriyor mu | var (kuyruk-tekrarı dedektörü, [ADR-0073](adr/kararlar-0064-0085.md#adr-0073)) |
| iz ↔ cevap tutarlılığı | iz bir kaynağı seçip cevap başkasına mı dayanıyor | yeni (~$5 hakem, tahmin; insan örneklemine dahil) |
| iz dili | Türkçe mi İngilizce mi | deterministik |
| genel akıl yürütme kaybı | eğitim genel düşünmeyi bozdu mu | §4.6 |

**Çıpa her temel modelin kendi ham hâlidir** ("modeli aldığımız noktadan kötüye götürmemeliyiz",
[ADR-0039](adr/kararlar-0027-0044.md#adr-0039)). Eşik dondurma ADR'sinde koşudan önce yazılır. Eşiği
geçemeyen yöntem **final model olamaz**, ama raporlanır.
Kayıtta risk zaten görünür: τ_a düşüncesini **hiç** kendi kapatmıyor (230/230 zorla,
[#48](record/kronoloji-39-52.md#48)); birleştirme kısmen geri kazanıyor (M1'de 25/80 zorla, ham model
80/80, [`kollar.md`](record/kollar.md) satır 334-335); iz İngilizce, cevap Türkçe.

### 4.5 İstatistik (önceden yazılır)

Birincil metrik **kütle**; birincil karşılaştırma **birleştirme ↔ güçlü birlikte eğitim**; diğerleri
"ikincil" etiketli. Kütle için soru × seed üzerinde **eşleştirilmiş bootstrap** (kütle iki farklı
birimin çarpımı olduğu için hazır aralığı yoktu, [ADR-0083](adr/kararlar-0064-0085.md#adr-0083) EK-2
madde 4). Sayımlar için Wilson aralığı.

### 4.6 Genel yetenek kontrolü · HMGS · rakipler

- **Genel yetenek:** açık lisanslı, küçük bir genel akıl yürütme kümesi; düşünce açık; yerelde, $0.
  Kümenin seçimi F0'da, lisansı okunarak.
- **HMGS yok:** kapalı-kitap sınav ezberi ölçer, ezber anti-hedeftir
  ([ADR-0027](adr/kararlar-0027-0044.md#adr-0027) elenenler tablosu).
- **Rakip yok** (K10). Bütçe kalırsa F3'te tek ucuz referans çizgisi: `gemini-3.1-flash-lite`
  (cevap başına ~$0,0019, [`MODEL_CARD.md`](../MODEL_CARD.md) §5.1; yeni testte ~$2 + hakem ~$0,3 +
  dedektör kalibrasyonu için ~1 sa).

---

## 5 · Takvim ve bütçe (1. yıl)

Takvim bir teslim tarihine değil **"gönderime hazır"** noktasına bağlıdır. Ay sınırları kabadır;
DEÜ takvimine göre kaydırılır.

| aşama | zaman | ne olur | saat (tahmin) | para (tahmin) |
| :--- | :--- | :--- | :--- | :--- |
| **F0 zemin** | Ekim sonu–Kasım 2026 | **yedekler (K12)** · kararları ADR-0089+ olarak deftere işle · τ_g v1 hassasiyetini bundle geçmişi ve Modal günlüklerinden çöz · eski aletlere bundle'dan erişim · **ortam kilidinin yaml'ı + betik kontrolü + testi** ([`EGITIM_ORTAMI.md`](EGITIM_ORTAMI.md)) · birlikte-eğitim kodu + Modal pilotu · Gemma kapısı · **literatür taraması** (birleştirme ↔ birlikte eğitim; RLVR + çekinme) · ön-kayıt taslağı · mevcut kolların güncel DEV'de yeniden ölçümü | ~10-14 (literatür ~5-8 dahil) | Modal ~$4 · hakem ~$2 |
| **F1 DEV iterasyonu** | Kasım–Aralık | birlikte + ardışık, ikişer yapılandırma · **dondurma ADR'si** | ~3-4 | Modal ~$14 |
| paralel | Kasım–Aralık | ajan test sorularını üretir, okuma protokolünü taslaklar | ~1 | <$1 |
| **F2 seed + Gemma + test** | Ocak–Şubat 2027 (ara tatil) | yeni + mühürlü soruları oku, test dondur · Qwen seed 2-3 · Gemma 1 seed | ~7-10 | Modal ~$25 (Ocak) + ~$20-25 (Şubat) |
| **F3 son ölçüm** | Mart–Nisan | test **bir kez** açılır · bütün kollar dizüstünde (~120 sa GPU, geceleri) · Tablo 2'nin yeni satırları · ikinci hakem | ~2-3 | hakem ~$15-20 · Sonnet ~$9 |
| **F3b uygulama** | Mayıs, **yalnız kazanan birleştirme değilse** | kazananın Qwen sürümü → GGUF → konteyner kilidi ([ADR-0078](adr/kararlar-0064-0085.md#adr-0078)) → model kartı | ~2 | $0 |
| **F4 insan doğrulaması** | Haziran–Temmuz | ~300 cevap kör okuma · öğrenciler · hukukçu · uyum istatistikleri | ~12-15 | $0 |
| **F5 yazım** | Temmuz–Eylül | yazım · **1-2 dış okuyucu** · arXiv (ARR kuralına göre) · ilk uygun ARR döngüsü | ~40-60 (en belirsiz) | — |

**1. yıl toplamı (tahmin):** saat ~75-110 · Modal GPU ~$60-70 (her ay $30 kredinin altında) ·
nakit ~$30-35 + OpenRouter kredi ücreti.

### 5.1 Modal kredisinin kullanımı

Modal'ın sayfası Starter planındaki $30'ı **aylık** yazıyor; hesabında yenilenip yenilenmediği
kontrol edilecek (§8). Eğitimler ayda ≤$30 olacak biçimde F0-F2'ye bölündü. Tek seferlikse nakit
~$55-70'e çıkar (yine bütçe içinde). Akademik kredi başvurusu yapılır, plan ona dayanmaz.

### 5.2 Kredi ay içinde biterse (K6)

1. **Bekleyebiliyorsan** yeni ayı bekle ($0).
2. **Bekleyemiyorsan** Vast'a geç: **yalnız A100** (5090 değil) · **blok sınırında** (en doğal sınır:
   Gemma bloğunun tamamı; bir koşu asla iki platforma bölünmez) · ilk Vast koşusundan önce **50
   adımlık eşdeğerlik kontrolü** (~$1) · aynı Docker imajı · API anahtarı kiralık makineye gitmez ·
   koşu bitince makine silinir. Ayrıntı: [`EGITIM_ORTAMI.md`](EGITIM_ORTAMI.md).
3. Makalenin ekine **donanım tablosu**: hangi kol nerede eğitildi.

---

## 6 · Makale 2 (RL) ve tez

### 6.1 Makale 2

- **Başlangıç noktası:** Makale 1'in Qwen'deki kazananı (birleştirme çıkarsa `tgta_v1`). Birleştirme
  hattı ürün için `v1`'de dondurulmuştur; RL ardışık bir eğitimdir
  ([ADR-0075](adr/kararlar-0064-0085.md#adr-0075)).
- **Ödül (K15).** Atıf doğrulayıcı **tek başına isabetsiz atıfı göremez**: madde gerçek, yalnız soruya
  ait değil ("deterministik atıf doğrulaması onu yakalayamaz",
  [ADR-0066](adr/kararlar-0064-0085.md#adr-0066)). Yalnız doğrulayıcıyla ödül verilirse model
  "bağlamdaki herhangi bir gerçek maddeye atıf" öğrenebilir. Eğitim sorularının altın maddesi
  bilindiği için hakemsiz ödül: **altına atıf +** · **başka gerçek maddeye 0/−** · **altın yokken
  susma +** · **altın varken susma −**. ADR-0075'in formülünün isabet terimiyle güçlendirilmiş hâli.
  Ödül, hedef bant ve **durma kuralı** RL başlamadan ADR'ye yazılır. Korunacak tabanlar: uydurulmuş
  madde 0/114 · gereksiz red 4/80 · kütle 0,8011.
- **Düşünce hizalaması:** iz ↔ karar tutarlılığı · iz kaynağın yeterliliğini tartıyor mu · iz dili.
  Türkçe iz için ayrı ödül terimi ön-kayıtta ayrıca karara bağlanır (ana hedefle yarışabilir).
- **Rakip karşılaştırması burada** (K10): o günün aynı sınıfları, tarihli sürümler
  ([ADR-0020](adr/gemma4-12b-dersler.md#adr-0020)); eşit sınav
  ([ADR-0057](adr/kararlar-0045-0063.md#adr-0057)); her yeni ailede dedektör kalibrasyonu; aile
  dışlaması (Claude rakipse Anthropic olmayan ikinci hakem; GPT sınıfı rakip bugünkü hakemle çakışır,
  [ADR-0072](adr/kararlar-0064-0085.md#adr-0072)). Maliyet ~1.100 cevaplık testte kabaca Flash-Lite
  ~$2 · Flash ~$11 · Sonnet ~$16 + hakem (tahmin, [`MODEL_CARD.md`](../MODEL_CARD.md) §5.1).
- **Son sınav:** mühürlü ~100 soru (K14).
- **Okunması zorunlu önceki çalışmalar** (ACL 2026 listesinde başlıkları görüldü, içerik okunmadı):
  ana konferans *"Mitigating Lost in Multi-turn Conversation via Curriculum RL with Verifiable Accuracy
  and Abstention Rewards"* · Findings *"Pause or Fabricate? Training Language Models for Grounded
  Reasoning"*.

### 6.2 GRPO maliyeti

Ölçülmüş değil. Hesap: eğitim verimi A100'de 2.619 token/sn
([ADR-0033](adr/kararlar-0027-0044.md#adr-0033)) · cevap ~800 token · soru başına 8 cevap · LoRA'lı
GRPO (referans = adaptörü kapalı model).

| senaryo | adım | istem | süre | Modal | Vast A100-80GB |
| :--- | ---: | :--- | ---: | ---: | ---: |
| küçük | 250 | RAFT biçimi (≤2048) | ~5-6,5 sa | ~$11-14 | ~$4,5-7 |
| orta | 500 | RAFT biçimi | ~10-13 sa | ~$22-28 | ~$9-14 |
| uzun istem | 500 | ürün biçimi (10 kaynak) | ~19-24 sa | ~$40-50 | ~$16-25 |

| paket | içerik | Modal (orta) |
| :--- | :--- | ---: |
| en az | pilot + ana GRPO 2 seed + 1 ablasyon (yalnız doğrulayıcı ödülü) | ~$75-80 |
| önerilen | pilot + ana GRPO 3 seed + 2 ablasyon (isabet terimsiz · çekinme terimsiz) | ~$120-130 |

**Paket seçilmedi** (kullanıcı kararı): 2. yılın ilk işi ~$2-5'lik pilot; vLLM'in Qwen3.5-4B'yi
çalıştırıp çalıştırmadığını ve adım süresini ölçer, paket ondan sonra seçilir. vLLM çalışmazsa üretim
`transformers` ile yapılır ve maliyet birkaç katına çıkabilir.

### 6.3 2. yıl takvimi

| zaman | iş | saat (tahmin) |
| :--- | :--- | :--- |
| Ekim–Aralık 2027 | iki makaleyi oku · ödül ve ön-kayıt ADR'si · GRPO pilotu · Makale 1'in hakem yorumları gelirse yeniden gönderim | ~10-15 |
| Kasım 2027 – Mart 2028 | GRPO koşuları, ayda kabaca bir (kredi içinde) | ~5 |
| Mart–Nisan 2028 | mühürlü parçada son ölçüm · rakipler | ~5 |
| Nisan–Haziran 2028 | tez yazımı (makale metinleri yeniden kullanılır) · Makale 2 yazımı | ~40-60 |
| yaz 2028 | savunma | — |

### 6.4 Tez

En kötü durumda (RL yok): 1 giriş ve ilgili çalışmalar · 2 **sistem** (eldeki iş) · 3 **ölçüm
dersleri** (eldeki kayıt) · 4 **post-training karşılaştırması** (Makale 1) · 5 sonuç ve gelecek
çalışma. RL gelirse 5. bölüm Makale 2 olur. DEÜ'de kontrol edilecekler §8'de.

---

## 7 · Riskler, karar kuralları, ürün ile ilişki

### 7.1 Ürün yol haritasıyla ilişki

| aday (`superpowers/00-IS-SIRASI.md`) | yeni yeri |
| :--- | :--- |
| `v2-RL-GRPO` | **Makale 2** (2. yıl) |
| korpus turu (~288 bin madde) | **Makale 2 bitene kadar bekler** (K11): korpus değişince eşit sınav ve yayımlanan sayılar askıya alınır ([ADR-0083](adr/kararlar-0064-0085.md#adr-0083) §E.6); CLAUDE.md'nin "ürün yolu ölçülen yola eşit olmalı" kuralı ayrı ilerlemeye izin vermez |
| açık kusurlar 5a · 23 · 27 · 31 | ürün iş listesinde kalır |

### 7.2 Önceden yazılan karar kuralları

| ne olursa | ne yapılır |
| :--- | :--- |
| F0: `v1` hassasiyeti yeniden üretilemiyor | yeni 1. seed (~$6); `v1` ürün olarak kalır |
| Gemma kapıdan kalıyor | Ministral; o da kalırsa tek temel model + sınırlılık + hedef Findings/dergi |
| birlikte-eğitim kodu F1 sonuna kadar çalışmıyor | son çare karışık SFT tabanı, zayıflığı yazılır |
| Modal pilotunda birim maliyet tahminin 1,5 katını aşıyor | bütçe yeniden hesaplanır; Vast A100-80GB |
| Mayıs 2027'ye kadar gönüllü öğrenci yok | okuma kullanıcı + hukukçu; insan↔insan uyumu raporlanamaz, sınırlılık |
| kazanan düşünce korumasından kalıyor | final ürün eşiği geçen en iyi yöntem; yoksa `tgta_v1` |
| F3 sonunda takvim >1 ay geride | **kesme sırası:** (1) referans çizgisi → (2) ikinci hakem → (3) Gemma. **Asla kesilmez:** güçlü birlikte eğitim · Qwen'de 3 seed · insan doğrulaması · test kümesi |
| ret | sonraki ARR döngüsü → dergi; her adım hakem yorumları okunduktan sonra |

### 7.3 Riskler

1. **Yazım saati (F5).** Gecikirse bir döngü kayar; mezuniyet etkilenmez.
2. **Tek yazarlık.** Dış okuyucular; ARR yorumları ek geri bildirim turu.
3. **Ajan kullanımı beyanı.** ACL ve enstitü kuralları kontrol edilecek (§8); kayıttaki "insan kararı"
   damgaları kararların insana ait olduğunun kanıtıdır, ama her karar savunulabilmeli.
4. **Özgünlük.** F0'daki literatür taraması para harcanmadan önce; örtüşme çıkarsa çerçeve dondurmadan
   önce düzeltilir.
5. **Tek nüsha (K12).** `~/yedek/HakHukuk-2026-10-10.bundle` eski git geçmişinin tek kopyası
   ([ADR-0088](adr/kararlar-0064-0085.md#adr-0088)); RQ2'nin eski aletleri ve kayıttaki commit
   atıfları ona bağlı. `outputs/tg_v1` (115 MB) ve `outputs/ta_v1` (134 MB) yedeklenmiyor
   ([`kollar.md`](record/kollar.md)) ve artık yeniden üretilemez araştırma kanıtıdır. Kayıt bu
   riskin bedelini bir kez ödedi: 12B adaptörleri kalıcı kayıp
   ([ADR-0034](adr/kararlar-0027-0044.md#adr-0034)). → F0'ın ilk işi; ADR-0034'ü değiştiren yeni ADR.
6. **Dizüstünün ~120 saatlik ölçümü.** Şarjda olmalı (pilde hız 17× düşüyor,
   [#39](record/kronoloji-39-52.md#39)).

---

## 8 · Kontrol edilecekler (bu belge tahmin etmez)

| # | ne | nerede |
| :-- | :--- | :--- |
| 1 | ARR 2027 döngü tarihleri · ön baskı (arXiv) kuralı | aclrollingreview.org |
| 2 | ACL/ARR yapay zekâ yardımı politikası ve gönderim kontrol listesi | ACL / ARR sayfaları |
| 3 | COLM 2027/2028 çağrısı (Makale 2 için) | COLM sitesi |
| 4 | DEÜ FBE: tez dili · mezuniyet için yayın şartı · yayımlanmış makalenin tezde kullanımı · tezden üretilen yayında danışman adı · programa başlamadan önceki işin teze sayılması · üretken YZ kuralı | enstitü yönetmeliği ve tez yazım kılavuzu |
| 5 | Modal $30 kredisinin hesapta **aylık** yenilenmesi · akademik kredi başvurusu | Modal faturalama sayfası |
| 6 | Vast'ta o günkü A100 fiyatı ve sürücü sürümü | Vast konsolu |
| 7 | Gemma 4 E4B lisans dosyası (kayıtla çelişki, §3.5) | HF model deposu |
| 8 | vLLM'in Qwen3.5-4B desteği | GRPO pilotu |
| 9 | genel yetenek kümesinin lisansı | F0 |
| 10 | OpenRouter fiyatları (gönderim anında) | OpenRouter model sayfaları |

---

## 9 · Çelişki ve bayatlık işaretleri

Kullanıcı bu oturumda mevcut dosyalara dokunulmamasını seçti; çelişkiler **yalnız burada** işaretli,
karşı tarafları F0'da ADR ile damgalanır.

| nerede | ne diyor | gerçek / bu belge |
| :--- | :--- | :--- |
| [`MODEL_CARD.md`](../MODEL_CARD.md) §2 | iki kol için "QLoRA (NF4)" | [ADR-0031](adr/kararlar-0027-0044.md#adr-0031) "bf16 taban + LoRA (QLoRA değil)"; τ_a `--bf16-base` ile eğitildi ([#48](record/kronoloji-39-52.md#48)); τ_g bilinmiyor; betiklerin varsayılanı **sessizce NF4** ([`EGITIM_ORTAMI.md`](EGITIM_ORTAMI.md)) → F0 |
| `superpowers/00-IS-SIRASI.md` | iki aday, sıra "insan kararı" | sıra burada verildi (§7.1) |
| `superpowers/00-IS-SIRASI.md` "Bakım kuralı" | "yeni ADR 0087'den" | 0087 ve 0088 yazılı; sıradaki **0089** |
| [ADR-0028](adr/kararlar-0027-0044.md#adr-0028) | tek boyut noktası | Makale 1 ikinci bir **temel model** (aynı boy, başka aile) ekliyor |
| [ADR-0034](adr/kararlar-0027-0044.md#adr-0034) | adaptörler yedeklenmez | `v1` adaptörleri yedeklenir (K12) |
| [ADR-0075](adr/kararlar-0064-0085.md#adr-0075) m.3 | task-vector hattı `v1`'de donduruldu | ürün için geçerli; Makale 1 **araştırma için** aynı reçeteyle yeni seed üretir. Ürünün `v2`'si yine RL |
| [ADR-0037](adr/kararlar-0027-0044.md#adr-0037) | Kapı 5 "ayar: norm-dengeli" | ana sonuç ham TIES ([ADR-0052](adr/kararlar-0045-0063.md#adr-0052)); Kapı 5 ham TIES için yeniden türetilir |

---

## 10 · Kaynaklar (web, erişim 2026-10-10)

Fiyatlar ve model bilgileri o günün sayfalarından; değişir, kullanmadan önce yeniden bakılır.

- ACL 2026 kabul listeleri: [ana konferans](https://2026.aclweb.org/program/accepted_papers/) ·
  [Findings](https://2026.aclweb.org/program/findings/) · [Industry](https://2026.aclweb.org/program/industry/)
- [Modal Pricing](https://modal.com/pricing) — A100-40GB $0,000583/sn; Starter $30/ay; akademik kredi
- Vast fiyatları: [hostalu](https://hostalu.com/en/gpu-cloud/) ·
  [gpuperhour](https://gpuperhour.com/) · [computecomparison](https://computecomparison.com/provider/vast-ai) ·
  [getdeploying RTX 5090](https://getdeploying.com/gpus/nvidia-rtx-5090) ·
  [Vast pricing docs](https://docs.vast.ai/documentation/instances/pricing)
- OpenRouter: [claude-sonnet-5](https://openrouter.ai/anthropic/claude-sonnet-5) ·
  [gpt-4o-mini](https://openrouter.ai/openai/gpt-4o-mini) ·
  [ücretler — TrueFoundry](https://www.truefoundry.com/blog/openrouter-pricing)
- Temel model adayları: [Gemma 4 — HF blog](https://huggingface.co/blog/gemma4) ·
  [Ministral 3 3B Reasoning](https://huggingface.co/mistralai/Ministral-3-3B-Reasoning-2512) ·
  [Phi-4-mini-reasoning](https://huggingface.co/microsoft/Phi-4-mini-reasoning)
- GRPO / vLLM: [Qwen3.5 — LMCache](https://docs.lmcache.ai/recipes/qwen3_5.html) ·
  [RLVR low-rank dynamics](https://arxiv.org/pdf/2605.06523) ·
  [Goldilocks RL](https://arxiv.org/pdf/2602.14868)
