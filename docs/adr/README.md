# Mimari/Metodoloji Karar Kayıtları (ADR)

Bu klasör **neden** belirli bir yol seçtiğimizi kaydeder — sadece *ne* yaptığımızı değil.
Amaç tek: *"şunu neden böyle yaptık, hangi alternatifi neden eledik, sonuç ne oldu"* sorusu
**kanıtla** cevaplanabilsin.

> **Gerekçe 2026-08-03'te değişti, kural aynı kaldı.** Eskiden *"paper yazılırken lazım olacak"*
> diyordu. Tez yok. Yerine geçen sebep **daha güçlü**: bu **aralıklı, tek kişilik açık kaynak** bir
> proje — oturumlar arasında haftalar geçiyor ve **hatırlayan tek şey repo**.

## Dosyalar

| dosya | kapsam |
| :--- | :--- |
| [`kararlar-0027-0044.md`](kararlar-0027-0044.md) | tasarım kilitleri · base seçimi · precision · merge/norm · Kapı 6 · düşünce modu |
| [`kararlar-0045-0063.md`](kararlar-0045-0063.md) | ara kapı · CP2 hasat · hakem · harness · eşit sınav · faz 0 ölçüm zinciri |
| [`kararlar-0064-0085.md`](kararlar-0064-0085.md) | `v1.0` kapısı · hakem paneli · ürün yolu · konteyner · kusur sicili · κ · tek kart |
| [`gemma4-12b-dersler.md`](gemma4-12b-dersler.md) | emekli 12B hattı: **(A) dersler** (base-bağımsız — *yeni hatta başlayan burayı okur*) · **(B) 26 ADR'nin karar kaydı** · (C) ham kayda giriş |

**Atıf uyumu.** Repo genelinde ~2.100 `ADR-00NN` göndermesi var ve hepsi **çapayla** çözülür:
`kararlar-0045-0063.md#adr-0052` · `gemma4-12b-dersler.md#adr-0011`.
Hangi dosya olduğu numaradan aritmetikle bulunur.

**Numaralandırma.** Yeni karar = yeni numara, **0087**'den devam. ⛔ **0059 REZERVE** — turun
`τ_a` v2 veri-simetrisi ADR'si; altı yer `ADR-0059 §sapma-1` diye atıf veriyor.

---

## Dizin — yeni hat (Qwen3.5-4B)

🟢 yürürlükte · 🟡 kısmen süperseded · 🔴 hükmü tersine döndü / aşıldı

| # | | konu |
| :-- | :-: | :--- |
| [0027](kararlar-0027-0044.md#adr-0027) | 🟢 | ⭐⭐ Tasarım kilitleri: paralel kol + task-vector merge · iki matris · DEV/TEST ayrımı · dört katmanlı hakem savunması |
| [0028](kararlar-0027-0044.md#adr-0028) | 🟢 | Tek boyut noktası *(tez kısıtı 2026-08-03'te kalktı; bedelin üç maddesi limitations'ta)* |
| [0029](kararlar-0027-0044.md#adr-0029) | 🟢 | Tek model erişim kapısı + 🔒 maliyet muhasebesi (**liste fiyatı**, kapıya ödenen değil) |
| [0030](kararlar-0027-0044.md#adr-0030) | 🟡 | ⭐ **Base = `Qwen/Qwen3.5-4B`**, kapı 6/6 · *madde 2 (düşünce KAPALI) → 0043 ile düştü* |
| [0031](kararlar-0027-0044.md#adr-0031) | 🟢 | Precision: dağıtım **Q4_K_M** · eğitim **bf16 taban + LoRA** (QLoRA değil) |
| [0032](kararlar-0027-0044.md#adr-0032) | 🟡 | Hakem paneli üç aile + aile-dışlama *(pratikte iki aile — 0074/0084)* |
| [0033](kararlar-0027-0044.md#adr-0033) | 🟢 | Eğitim hızı: **`fla-core` zorunlu** (36 → 5,4 s/it) · checkpointing kapalı · batch 2×8 |
| [0034](kararlar-0027-0044.md#adr-0034) | 🟢 | Emekli hattın artefaktları repo'dan çıkarıldı · 🔴 12B adaptörleri **kalıcı kayıp** |
| [0035](kararlar-0027-0044.md#adr-0035) | 🟢 | `τ_reasoning` / RS-FT kapsam dışı — istenen davranış **zaten eğitiliyor** |
| [0036](kararlar-0027-0044.md#adr-0036) | 🔴 | ΔW norm asimetrisi → norm-dengeli merge · **hükmü 0052 ile tersine döndü** |
| [0037](kararlar-0027-0044.md#adr-0037) | 🟡 | İç iddianın karar kuralı: **Kapı 5** · *madde (d) → 0039* |
| [0038](kararlar-0027-0044.md#adr-0038) | 🟢 | Red kapısı: **katı** — tek doğrulanamayan atıf tüm cevabı reddettirir |
| [0039](kararlar-0027-0044.md#adr-0039) | 🟢 | **Kapı 6** — parametrik sızıntı kendi kapısına ayrıldı, çıpa **base** (rakip değil) |
| [0040](kararlar-0027-0044.md#adr-0040) | 🟡 | Düşünce modu **ölçülecek**: ön-kayıtlı 🟢🟡🔴 kuralı · geçerlilik kapısı **%5 kesiklik** |
| [0041](kararlar-0027-0044.md#adr-0041) | 🟢 | RAFT meta-iddiaları hakemde iddia sayılmaz — **tüm kollara aynı anda** |
| [0042](kararlar-0027-0044.md#adr-0042) | 🟢 | `rejected` havuzu **tek kaynaktan** (ham base) + on-policy kontrol koşusu |
| [0043](kararlar-0027-0044.md#adr-0043) | 🟢 | ⭐ Düşünce modu **AÇIK**, bütçeli zorunlu kapatma · bütçe bir **rejim değişmezidir** |
| [0044](kararlar-0027-0044.md#adr-0044) | 🟢 | Feragat cümlesi **kör modda** red sayılmaz · Kapı 6'nın çıpası yeniden yazıldı (kütle ~3,4× yanlış ölçülmüş) |
| [0045](kararlar-0045-0063.md#adr-0045) | 🟢 | ARA KAPI + merge onarım kontrolü · **2. gözlem 2026-08-06'da DÜŞTÜ** (−9,9 p) ⇒ CP4-CP5 yetkisi yok |
| [0046](kararlar-0045-0063.md#adr-0046) | 🟡 | CP2 kabul ölçütü **regex'ten hakeme** · *m.2/m.4 → 0048 ile süperseded* |
| [0047](kararlar-0045-0063.md#adr-0047) | 🟢 | CP2 hedefi **750 negatif** · hasat Modal'da, **taşıyıcı değişmeden** (vLLM/bf16 yasak) |
| [0048](kararlar-0045-0063.md#adr-0048) | 🟢 | ⭐ Tuzak geçerliliği **cevaba kör, kalem düzeyinde, bir kez** — `valid_trap` öznenin özelliği olmuştu |
| [0049](kararlar-0045-0063.md#adr-0049) | 🟢 | Sprint 2'nin kalan beş kararı kilitlendi (eşik türetme · önbellek hakemi · M2b tabanı · smoke · kabul tasarımı) |
| [0050](kararlar-0045-0063.md#adr-0050) | 🟢 | ⭐⭐ Verim kapısının **tahmin edicisi** düzeltildi — ***sonucu gördükten sonra EŞİK değil ALET düzeltilir*** |
| [0051](kararlar-0045-0063.md#adr-0051) | 🟢 | `τ_a`'nın M2b çiftleri: kalıp **eval aynası**, `chosen` **şablon** · *şablon çıktısı gözle okunmadan kabul edilmez* |
| [0052](kararlar-0045-0063.md#adr-0052) | 🟢 | ⭐ **Norm dengelemenin hükmü tersine: ana sonuç HAM TIES** (0036'nın çıkarımı ölçümle çürüdü) |
| [0053](kararlar-0045-0063.md#adr-0053) | 🟢 | Modül-başına norm kapsamı **reddedildi** — gerekçe çürüdü, ölçüm de geçmedi |
| [0054](kararlar-0045-0063.md#adr-0054) | 🟢 | Harness tasarımı **K2-K5**: tam madde indekslenir · statik korpus · ayırt-edicilik etiketi · katı kapı |
| [0055](kararlar-0045-0063.md#adr-0055) | 🟢 | İsabet denetimi ekseni (borç **B1**): **kaynak-yeterliliği** sinyali — tek sinyal iki hatayı birden hedefler |
| [0056](kararlar-0045-0063.md#adr-0056) | 🟢 | `m2b`'nin harness-AÇIK protokolü = **altın ablasyonu** · 📌 *en fazla **bir canlı plan*** |
| [0057](kararlar-0045-0063.md#adr-0057) | 🟢 | ⭐⭐ **Harness Rekabet Kapısı: eşit sınav** — üç kademe + 🔒 anti-gaming (KAPALI kolu dondurulur) |
| [0058](kararlar-0045-0063.md#adr-0058) | 🔴 | Kaynak-yeterliliği önsözü benimsendi · **gerekçesi tersine döndü → 0063 ile kaldırıldı** |
| **0059** | ⛔ | **REZERVE — kullanma** |
| [0060](kararlar-0045-0063.md#adr-0060) | 🟢 | Kör payda önbelleğinin anahtarı hakem istemine eşitlendi · `k=10`'un paydası **TANIMSIZ** (bir hüküm kaybedildi) |
| [0061](kararlar-0045-0063.md#adr-0061) | 🟢 | ⭐ Çekinme dedektörü **istem rejimine bağımlıydı** — *alet düzeltmesi aletin her dalında yapılır* |
| [0062](kararlar-0045-0063.md#adr-0062) | 🟢 | ⭐ B10 turu kapatıldı: hedef **eğitimsiz** karşılandı — *kaybın %43'ü aletin kendisiydi* |
| [0063](kararlar-0045-0063.md#adr-0063) | 🟢 | **Yeterlilik önsözü KALDIRILDI** — bağlayıcı metrik **kütle**: cevaplanmayan soru vatandaş için değersizdir |
| [0064](kararlar-0064-0085.md#adr-0064) | 🟢 | ⭐⭐ **`v1.0` kapısı: üç madde, δ = 2,0 p** — ön-kayıtlı formül, mekanik sayı, bağlayıcı okuma **GÖZ-katı** |
| [0065](kararlar-0064-0085.md#adr-0065) | 🟢 | Bölünmüş sürümleme: **ürün sürümü ↔ iddia sürümü** |
| [0066](kararlar-0064-0085.md#adr-0066) | 🟢 | B1 yöntemi: **reddetme-örneklemesi** · GRPO bütçe kapısıyla ertelendi · ⛔ otomatik vekil metrik **YOK** |
| [0067](kararlar-0064-0085.md#adr-0067) | 🟢 | DEV/TEST soru onarımı v1 → v2 · `recall@10` 0,8750 → 0,9375 · ⚠️ **#39-#61 arası her DEV sayısı v1 birimindedir** |
| [0068](kararlar-0064-0085.md#adr-0068) | 🟢 | `RRF_K` **60 → 10** — kusur BM25'te değil **füzyonda**; seçim gerekçesi **plato** · TEST'te bağımsız doğrulandı |
| [0069](kararlar-0064-0085.md#adr-0069) | 🟢 | Kabul testi raporlaması: **ham kütle manşet** + tavan kullanımı *(kapı DEĞİLDİR)* |
| [0070](kararlar-0064-0085.md#adr-0070) | 🟢 | Üretim bütçesi rakiple **EŞİTLENDİ** (tek formül, 1536) — sapma **bizim aleyhimizeydi** |
| [0071](kararlar-0064-0085.md#adr-0071) | 🟢 | `v1.0` artefaktı: **tek GGUF**, adında kuantizasyon · *dağıtılan şey ölçülen şey olmalı* |
| [0072](kararlar-0064-0085.md#adr-0072) | 🟡 | Rakip havuzu genişler · ⛔ **kapı eşiği oynamaz** · GPT sınıfı **usul gereği** dışarıda |
| [0073](kararlar-0064-0085.md#adr-0073) | 🟢 | M5 rejimine **DRY** eklendi (kapsam yalnız M5) · 🚨 *DRY modeli DOĞRU yapmadı, AKICI yaptı* |
| [0074](kararlar-0064-0085.md#adr-0074) | 🟢 | ⭐ **Hakem paneli kuruldu (iki aile)** · κ **0,534/0,409** (eşik 0,6) · bağlayıcı hakem = eşit sınavın hakemi |
| [0075](kararlar-0064-0085.md#adr-0075) | 🟢 | `v1` **SFT ile kapanır**; `v2` = `tgta_v1` üstüne **sequential RL** · 🚨 task-vector hattı `v1`'de **dondurulur** |
| [0076](kararlar-0064-0085.md#adr-0076) | 🟢 | **KAPI ↔ KALDIRAÇ** ayrımı + araç katmanı · 🚨 **KAPI'lar TOOL YAPILAMAZ** |
| [0077](kararlar-0064-0085.md#adr-0077) | 🔴 | Kabul testi koştu; `v1.0` **VERİLMEDİ**, `v0.3` *(→ 0084 ile aşıldı)* · ham kütle TEST **0,5804** |
| [0078](kararlar-0064-0085.md#adr-0078) | 🟢 | Konteyner dağıtımı bir **REJİM KİLİDİDİR** — KV bayrağı cevabı değiştiriyordu |
| [0079](kararlar-0064-0085.md#adr-0079) | 🟢 | Zayıf-eşleşme rozeti **EKLENMEZ** — *eşik ölçüme bağlanmıştı, ölçüm reddetti* |
| [0080](kararlar-0064-0085.md#adr-0080) | 🟢 | Ürün yoluna **iki geçişli zorunlu düşünce kapatması** · boş cevap 4/80 → **0/80** |
| [0081](kararlar-0064-0085.md#adr-0081) | 🟢 | Altıncı `Durum`: **`BOS_SORGU`** — kapalı küme, yeni hâl ölçülünce **ad ister** |
| [0082](kararlar-0064-0085.md#adr-0082) | 🟢 | `app` kutusu da `--host 0.0.0.0` — *kilit ancak kapsamadığı şeyi görünür kıldığı sürece kilittir* |
| [0083](kararlar-0064-0085.md#adr-0083) | 🟢 | ⭐⭐ **Kusur sicili** (33 kusur, **4 açık**: 5a·23·27·31) + devir tablosu + kapsam/tazelik tasarımının özü + **9 grill maddesi** |
| [0084](kararlar-0064-0085.md#adr-0084) | 🟢 | ⭐ **κ borcu kapandı; kapının üç maddesi yeni birimde GEÇTİ** — κ'nın kendisi **değişmedi** |
| [0085](kararlar-0064-0085.md#adr-0085) | 🟢 | Tek model kartı · ürün tonu · iki yeniden adlandırma · **aşırı-red ekseni tek birime çivilendi** (yayımlanan sayı aleyhimize değişti) |
| [0086](kararlar-0064-0085.md#adr-0086) | 🟢 | **Kayıt katmanı kompaktlandı** — 103 dosya → 12; ADR-0024'ten **ikinci bilinçli sapma** |

---

## Emekli hat — 12B (ADR-0001 … 0026)

26 ADR 2026-07-24'te [`gemma4-12b-dersler.md`](gemma4-12b-dersler.md) Bölüm B'de birleştirildi.
**Bölüm A (dersler) base-bağımsızdır ve yeni bir deney tasarlamadan önce okunur.**
Bugün hâlâ **yürürlükte** anılanlar: `0003` · `0010` (düz SFT abstention'ı yok etti) · `0011`
(6-mod CANON) · `0016` · `0017` · `0018` · `0019` · `0023` · `0025` · `0026`.
