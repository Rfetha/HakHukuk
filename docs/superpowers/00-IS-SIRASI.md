# `docs/superpowers/` — iş sırası

> Bu klasörün **giriş dosyası** ve **tek durum kaynağı**. Neyin şimdi, neyin sonra olduğunu
> söyleyen tek yer.
>
> **Bu dosya bir HARİTA, bir plan değildir.** Kutucuk taşımaz. Bir işi sıradan çıkarmak ya da
> araya sokmak **insan kararıdır** — kendi başına yapma.

---

## Bir bakışta

| # | iş | durum |
| :-- | :--- | :--- |
| **1** | **`v1-son-iş`** — `v1.0`'ı kapatan tur | ▶️ **İCRADA** · [plan](plans/2026-09-12-v1-son-is.md) **32/63** · [goal](plans/goal-2026-09-12-v1-son-is.md) · şu an **6.5** (κ borcu) · harcanan **$0,4608** |
| **2** | **`v2-RL-GRPO`** — `tgta_v1` üstüne GRPO + düşünce ayarı | ⏸️ **DURUYOR** · planlanmadı, açılmayacak |

**Klasör 2026-09-12'de boşaltıldı.** Kapanan iki plan ve iki spec **silindi**; taşıyıcı içerikleri
[ADR-0083](../adr/0083-kusur-sicili-adrye-tasindi.md)'e alındı — **32 kusurun sicili**, **devir
tablosu** ve silinen tasarımın **mimari özü**. Gerekçe ve kabul edilen bedel (29 bağlantının 9'u
öldü) o ADR'de yazılı.

---

## 1 · `v1-son-iş` — AÇIK, planı yazıldı

### `v1.0`'ı bugün ne engelliyor — **tek şey**

**Engel model değil, ÖLÇÜM AYGITI.** [ADR-0077](../adr/0077-v1-0-verilmedi-v0-3.md):
[ADR-0064](../adr/0064-v1-kapisi-uc-maddeli-on-kayit.md)'ün saydığı iki eksikten **(a) kabul
testi** 2026-09-09'da **kapandı**; geriye **(b)** kaldı — *her sayı hâlâ **tek hakem ailesinin**
hükmü*. κ `tam_sadık` **0,534** · `atıf_temiz` **0,409**, aracın eşiği **0,6**.

Borcun kapanma koşulu [ADR-0074](../adr/0074-hakem-paneli-kuruldu-baglayici-hukum.md)'te
**tek cümledir**:

> *"`3.5 Flash` kolunun **aynı ikinci hakemle** puanlanması."*

| | |
| :--- | ---: |
| bedel (ADR-0074'te ölçülmüş) | **$2,81** |
| OpenRouter bakiyesi (2026-09-12) | **$2,0410** |
| **açık** | **−$0,77** |

⚠️ Tahmin **tabakalanmış duman koşusundan yeniden türetilmeli** — tuzak **1.11**: 2026-09-09'da
`n=5`'ten yapılan doğrusal tahmin **$0,82** dedi, gerçek **$1,1932** tuttu ve `$1` kapısı
**%45** aşıldı.

### Turun içeriği — grill BELİRLEDİ (2026-09-12)

**Plan yazıldı:** [`plans/2026-09-12-v1-son-is.md`](plans/2026-09-12-v1-son-is.md) — 46 kutucuk,
18 kilitli karar, ön-kayıtlı kapı ve dört maddelik DUR listesi. Girdileri:

| girdi | nerede |
| :--- | :--- |
| silinen tasarımın **mimari özü** + grill'e girecek **9 madde** | [ADR-0083](../adr/0083-kusur-sicili-adrye-tasindi.md) §EK |
| **8 açık kusur** — hepsi **yere bağlandı**, aşağıdaki tablo | [ADR-0083](../adr/0083-kusur-sicili-adrye-tasindi.md) |
| **3 devredilen** — **6** → `B1` · **11** → paket · **12b** → `B11` | ″ |
| κ borcu | ADR-0074 · ADR-0077 |

### 📊 Turun ölçülen sayıları — *(icra sürerken güncellenir)*

| ne | sonuç |
| :--- | :--- |
| ürün yolunda **boş cevap** | **0/80** — kartın *"ölçülmedi"* şerhi kapandı |
| ürün yolunun **kütlesi** | **0,7792** (ölçüm hattı 0,8011; −2,19 p, karıştırıcı var) |
| **S17** kuantizasyon eğrisi | `Q4` 0,7921 ↔ `Q5` **0,8673** ↔ `Q8` 0,7909 — **monoton değil** |
| araç zinciri sapması | **−0,90 p ⇒ BELİRSİZ** (32 bayt fark davranışsal değil) |
| κ borcu tahmini | **$1,97** (tabakalanmış; düz ön-tahmin $2,81'di) |

**Bu turda kapanan kusurlar:** **24** (bayat README) · **29** (imajdaki yedek) · **33** (yeniden
üretim kapısı hiç geçmiyordu). **Açık: 6** — 5a · 10 · 23 · 25 · 27 · 31.

**Yeni tuzaklar:** **7.7** (kapı var olmayan alanı okuyup her zaman düşüyor) · **7.8** (sağlık
kontrolü başkasının sunucusunu kendi sanıyor — 8 kalem yanlış modele üretildi).

### Açık kusurlar — **boşta duran YOK** *(insan kararı 2026-09-12)*

Kural: her açık kusur ya **bu turda biter** ya **`v2`'ye gider**. Üçüncü seçenek yok —
*"açık"* diye duran bir kusur, sahibi olmayan bir borçtur.

| # | kusur | nereye | niçin |
| :-- | :--- | :--- | :--- |
| **5a** | zayıf eşleşme sinyali — ölçüldü, **ayrışma YOK** (n=4) | ~~BU TUR~~ → **`v2`** | ⚠️ **GRILL'DE DEĞİŞTİ 2026-09-12.** Gerekçesi *"korpus büyürse ölçüm zaten yeniden koşulacak"*idi; grill **karar 1** korpus işini `v1.0`'dan **sonraya** aldı ve **karar 9** bu planın dışında bıraktı ⇒ tetikleyici **düştü**. Ölçüm `v2`'de korpusla birlikte yeniden koşar |
| **10** | **HF görünürlüğü** (`push` yarısı kapandı) | **BU TUR · adım 9** | Turun son adımı zaten bu |
| **23** | bir yeniden-puanlama koşusu **tekrarlanamadı** | **BU TUR** | κ borcu **puanlama** işidir; aynı boru hattı koşarken bu sınıf **ikinci kez** sınanır. Kural: bu sınıftan sayı **tek koşuya dayandırılmaz** |
| ~~24~~ | ~~bayat README tablosu~~ | ✅ **2026-09-12'de KAPANDI** | public açılışın ön koşuluydu |
| **25** | aynı satırda **iki kesir birimi** | **BU TUR · adım 8** | Public kontrolünde kapanır; kıyas tablosu vatandaşa gidiyor |
| **27** | Kaynaklar listesinde **madde biçimi tutmuyor** | **`v2`** | Korpusun **ham** tutarsızlığının gösterim katmanına yansıması. Veriyi bozmadan çözmek ayrı bir tasarım işi |
| **29** | imaja ürünün okumadığı **36,1 MiB** korpus yedeği giriyor | **BU TUR** | Tek satırlık `.dockerignore` düzeltmesi; imaj bu turda zaten elleniyor |
| **31** | `compose` volume adını **proje adından** türetiyor | **KAYIT** | Kusur değil, **kayda değer davranış**: artefaktı elle koymak `sha256` kapısını hiç ateşlemeyecekti. Kapanmaz, **hatırlanır** |

⇒ **BU TUR: 4** (10 · 23 · 25 · 29) · **`v2`: 2** (5a · 27) · **kayıt: 1** (31) · **kapandı: 1** (24).
✅ **Grill koştu 2026-09-12** ve bir kusuru yerinden aldı: **5a → `v2`**, gerekçesi yukarıda.
Diğer altısı yerinde kaldı.

⭐ **Grill'e girmeden bilinmesi gereken tek düzeltme:** silinen tasarımın hedef sayısı
(**340.303 madde**) **yanlıştı** — `KANUN` satırı `917 × 102,7` sayıyordu, oysa korpustan ölçülen
gerçek oran **45,4 madde/belge**. Düzeltilince hedef **~287,6-287,8 bin** oluyor ve tasarımın
kendi kat merdiveninin **288.156**'sıyla **%0,13-0,20** farkla örtüşüyor. **Merdiven baştan
doğruymuş**; hedefi kaydıran tek bir satırdı. Ayrıntı ve üçüncü tutarsızlık ADR-0083 §EK'te.

### Sıra — insan tarafından kilitli (2026-09-12)

```
1 · inceleme          BİTTİ
2 · tazeleme          BİTTİ — docs/superpowers boşaltıldı, işaretçiler onarıldı
3 · 00-IS-SIRASI      BİTTİ — bu dosya
4a· GRILL             BİTTİ 2026-09-12 — 18 karar kilitlendi → plans/2026-09-12-v1-son-is.md
4b· GOAL YAZILIR      BİTTİ — plans/goal-2026-09-12-v1-son-is.md (3.323 krk)
5 · master'a al, push  BİTTİ
6 · planı EXECUTE      ← İCRADA
     6.1 korpus kimlikle bulunuyor          BİTTİ
     6.2 G8 · indeks HF'te PUBLIC           BİTTİ
     6.3 kusur 29 + konteyner uçtan uca     BİTTİ
     6.3b ürün yolunun kütlesi  0,7792      BİTTİ  (plana sonradan eklendi)
     6.3c S17 kuantizasyon eğrisi           BİTTİ  (plana sonradan eklendi)
     6.4 tabakalanmış duman + para kapısı   BİTTİ  — kapı GEÇTİ
     6.5 3.5 Flash ikinci hakem             ← ŞU AN (κ borcu burada kapanır)
     6.6 kusur 23'ün ikinci sınaması
     6.6b öz-tercih (Anthropic ailesi)      (plana sonradan eklendi)
     6.7 kapının üç maddesi                 ← DUR ②
     6.8 ADR-0084 + #68 + manşet ARALIK
7 · bekleyen commit'leri push
8 · PUBLIC kontrolü   repo + HF
9 · her şey PUBLIC    HF görünürlüğü açılır ← DUR ③
```

**`4b` bir kutucuk değil, kapıdır:** grill planı doğurur, **goal o planı yürütür**. Prompt
**4.000 karakterin altında** olmalı (harness sınırı) ve **planla aynı yerde**, kendi `.md`
dosyasında durur (`docs/superpowers/plans/goal-<plan-adı>.md`). Emsali bu turda işledi: kapanan
planın goal'u 115 kutucuğu alt-ajan sürüşlü yürüttü ve yalnız **DUR listesinde** durdu.
Goal'un taşıması gerekenler: **sıra (4→9)** · **kilitli kararlar** · **kaynaklı sayılar** ·
**DUR listesi** · **kurallar**. ⚠️ Prompt **planın kopyası değildir** — planı *işaret eder*,
durum ve kapıları taşır.

---

## 2 · `v2-RL-GRPO` — DURUYOR, planlanmayacak

```
v1   ham base ──► SFT (τ_g) + ORPO (τ_a) ──► ham TIES ──► tgta_v1 ──► YAYIN
v2   tgta_v1 (bf16) ──► GRPO + düşünce (thinking) ayarı ──► v2.0
```

**`v1` SFT ile KAPANIR** ([ADR-0075](../adr/0075-v1-sft-kapanir-v2-sequential-rl.md)) —
`B1`/`B4` eğitim turları **koşulmaz**. İkisinin gerekçesi ayrıdır ve ölçülmüştür: `B1`'de
rakiplerden **geride değildik** (8/80 ↔ 8·8·7·8); `B4` bir **merge** kaybıdır ve `v2`'de merge
olmadığı için **konusuz** kalır.

**Bedeli yazılıdır:** `τ = θ_ft − θ_base` tanımı tüm kolların **aynı base'i** paylaşmasını şart
koşar ⇒ `tgta_v1`'i yeni başlangıç almak bunu bozar ⇒ **task-vector hattı `v1`'de DONDURULUR**,
`v2`'ye taşınmaz. `v2`'nin iddiası merge değil **RL kazancıdır**.

**`v2`'ye devredilenler:** `B1` (misattribution — ⚠️ bu turda **ağırlaştı**: fp16 rejiminde
`wrong_ref_rate` **2,0×** kötüleşiyor) · `B11` (iskele işaretlerinin **kaynağı** eğitim verisi) ·
araç kullanımının **öğrenilmesi** (GRPO ödülüne *"doğru aracı doğru anda çağırdı mı"* girer) ·
**S9** (barındırma) · web arayüzü.

---

## Durum künyesi — 2026-09-12

```
sürüm      v0.3 (ürün) · artefakt HakHukuk-4B-v0.1 · ağırlıklar HF'te ÖZEL
test       323 yeşil, 2 xfail
dal        master (docs-tazeleme birleştirildi) · commit'ler HENÜZ PUSH EDİLMEDİ → adım 7
kayıt      ADR 0001-0083 · research_log #1-#68 · tuzak defteri 1.1-7.8
indeks     Rfetha/HakHukuk-mevzuat-bge-m3-s2 — dataset, PUBLIC (G8 açıldı 2026-09-12)
bakiye     OpenRouter $11,876 (ölçüldü 2026-09-12; goal'deki $2,04 BAYATTI)
```

**Kapanan son tur** (`hp` → Hat A → Hat B, **115/115**, 2026-09-12): hakem paneli kuruldu ve κ
**ilk kez** ölçüldü · Sonnet-5 rakip havuzuna girdi ve **önde** (0,8348 ↔ 0,8011) · donmuş TEST
**tek kez** açıldı (0,5804) · `hakhukuk/` paketi doğdu (CLI · TUI · HTTP API · araç katmanı) ·
konteyner **uçtan uca çalışıyor** · ürün yolunda boş cevap **4/80 → 0/80**.
Anlatısı [#66](../record/research_log/2026-09-11-urun-yuzeyi-ve-aygit-kusurlari.md) ve
[#67](../record/research_log/2026-09-12-konteyner-ve-alet-onarimlari.md)'de.

### O turun üç dersi — sıradaki tur bunları taşır

**① Ürün yüzeyini temizlemek ÖLÇÜM AYGITINDA kusur bulur.** Atıf doğrulayıcı kanun adını gevşek
eşleştirip **yanlış kanuna `DOGRULANDI`** basıyordu (tuzak **1.13**). Onarıldı (**7/16 → 0/16**),
çıpalar yeniden puanlandı: `0/114` ve donmuş TEST `0/52` **oynamadı** — ama korunmanın **aletten
değil ÖRNEKLEMDEN** geldiği ortaya çıktı.

**② Aleyhe çıkan sonuç da yazılır.** Rakipler de yeniden puanlandı: `3.1 Flash-Lite`
**1/152 → 0/153**. Tek deterministik üstünlüğümüzde artık **eşitiz**; karşılığında **eşit sınav**
alındı ([ADR-0057](../adr/0057-harness-rekabet-kapisi-esit-sinav.md)).

**③ Sayısal kapı TESTİN KÖRLÜĞÜNÜ görmez.** Üç insan gözü kapısı, **süit yeşilken duran dört
kusuru** yakaladı (**26 · 27 · 28 · 30**) ve **ikisi aynı gün yazılan koddandı** — testler onları
görmedi çünkü kusurun *görülmediği* varsayımla yazılmışlardı.

---

## Bakım kuralı

Bir iş kapandığında **iki yer** güncellenir: işin kendi kapanış kaydı ve **bu dosyanın
"Bir bakışta" tablosu**. Sıra değişirse **gerekçe buraya yazılır** — sıra değişikliğinin *niçin*i
başka hiçbir yerde durmuyor.

**Kapanan plan yeniden işletilmez.** Kapanış anında açık kalan **her** kusur **adıyla** devredilir;
devredilmemiş açık kusur varsa **kapanış geçersizdir**. Sicil ve devir
[ADR-0083](../adr/0083-kusur-sicili-adrye-tasindi.md)'te.
