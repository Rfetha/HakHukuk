# Araştırma kaydı — #39 … #52

> **Ne bu:** yeni hattın (Qwen3.5-4B) ilk 14 günlük girdisi, **birleştirilmiş ve damıtılmış**.
> Tekil dosyalar 2026-09-13'te silindi ([ADR-0086](../adr/kararlar-0064-0085.md#adr-0086));
> **sayılar birebir korundu** — damıtma yalnız anlatıda yapıldı. Silinenler git geçmişinde
> `301a82f` ve öncesinde duruyor.
>
> **Atıf uyumu:** her girdi bir çapa taşır → `kronoloji-39-52.md#48`.
> Emekli 12B hattının #01-#38'i: [`gemma4-12b-kronoloji.md`](gemma4-12b-kronoloji.md).

| # | tarih | başlık | kanca |
| :-- | :--- | :--- | :--- |
| [39](#39) | 2026-07-24 | Faz A: base kapısı (Qwen3.5-4B) + CP2 çıpaları | 6/6 kapı · **dört sessiz-bozulma** · Kapı 0: `τ_register` düşüyor |
| [40](#40) | 2026-07-25 | CP4: Faz B'nin kapısı bir **paket bölünmesiydi** | `fla-core` · 36 → 5,4 s/it (6,4×) · teşhis yanlıştı |
| [41](#41) | 2026-07-29 | CP6: `τ_grounding` ölçümü — kör red kırıldı | coverage %43,8 → **%85,0** · kütle %42,6 → **%72,0** · ❌ M5 anti-hedef ihlali |
| [42](#42) | 2026-07-29 | CP0: düşünce modu **ölçülemedi — model DURMUYOR** | sonlanmama, kesilme değil · 8× bütçe çözmedi · ama **kol çözüyor** |
| [43](#43) | 2026-07-29 | CP0.9: üç çıpa bütçeli kipte · **anti-hedef 3,4× yanlış ölçülüyormuş** | ADR-0044 · düşünce **biçimden değil muhakemeden** kazandırıyor |
| [44](#44) | 2026-07-30 | CP0.5 · CP1 · CP2 zemini — bir kapı kapandı, bir ölçüt çürüdü | `causal-conv1d` tavanı **1,254×** · hasat verimi **%5,0**, ölçütün altıda biri |
| [45](#45) | 2026-07-30 | CP2-a: ön-eleme çürüdü · `valid_trap` **öznenin cevabına bakıyor** | çapalanma −22,3 p (mini) ↔ −8,4 p (4o) · κ 0,097 |
| [46](#46) | 2026-07-30 | CP2-r: cevaba kör payda · üç eşik türetildi | düzeltme **4/6 kıyasta ALEYHİMİZE** · $0,23 |
| [47](#47) | 2026-07-30 | CP2-s: smoke **yazılmamış bir kodu buldu** · TIES'te işaret hatası | norm-dengeli k-yollu TIES'in implementasyonu **hiç yoktu** |
| [48](#48) | 2026-08-02 | CP2-c: Modal köprüsü · `τ_a` eğitildi · **ADR-0036 tersine** | dört eksik köprü · 728 negatif · ham TIES `τ_a`'yı **silmedi** |
| [49](#49) | 2026-08-04 | S3a ön-prob: hibrit retriever `recall@10` **0,875** | bedesten ✅ 4/4 · DEV kümesi erişim ölçümü için **yetersiz belirlenmiş** |
| [50](#50) | 2026-08-04 | Modül-başına norm: gerekçe **bedava çürüdü** | profiller orantılı (7,18-10,08) · kabul ölçütü kütlede düştü |
| [51](#51) | 2026-08-04 | Harness AÇIK ilk ölçüm | iki gerekçeden **biri çürüdü** (uydurma madde 0/118), biri **hiç sınanmadı** |
| [52](#52) | 2026-08-05 | Korpus bütünlüğü — S2 alanı | mülga maddeler vatandaşa gidiyordu |

---

<a id="39"></a>
## #39 — CP0: base doğrulama kapısı (Qwen3.5-4B) · dört sessiz-bozulma vakası

**2026-07-24 · Sprint 1 / Faz A** · Kararlar: [ADR-0030](../adr/kararlar-0027-0044.md#adr-0030) · [0031](../adr/kararlar-0027-0044.md#adr-0031) · [0032](../adr/kararlar-0027-0044.md#adr-0032)

**Künye.** base `Qwen/Qwen3.5-4B` sha `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a` · llama.cpp `0cea362` CUDA (`sm_120`) · RTX 5070 Ti Laptop 12226 MiB, WSL2 · torch 2.10.0+cu130 · transformers 5.10.2 · unsloth 2026.6.1 · **seed 3407**.
**Mimari — üç yapısal özellik.** **Hibrit dikkat:** 32 katman = **24 `linear_attention` + 8 `full_attention`** (interval 4) ⇒ KV yalnız 8 katmanda bağlamla büyür; *12B'nin KV matematiği taşınmaz.* **VLM:** `vision_config` depth 24 (~0.4B) — metin görevinde ölü ağırlık. **MTP:** `mtp_num_hidden_layers: 1`, kullanılmıyor. Diğer: `hidden_size` 2560 · heads 16/4 · `head_dim` 256 · **`vocab_size` 248320** · `max_position_embeddings` 262144.

**Kapı 6/6 ✅** — llama.cpp mimari (`LLM_ARCH_QWEN35`) · şablon render'ı **gözle** · turn işaretleri · Unsloth+sm_120 (⚠️ koşullu, 3 açık kalem) · kuantizasyon (`PURE=0`) · **saf Apache-2.0** (201 satır; *Gemma 4'ün durumundan **farklı** — orada Apache-2.0'ın üstüne Prohibited Use Policy katmanlanıyordu; burada `prohibit|use policy|must not` kalıplarının **hiçbiri geçmiyor***).

**Şablon render'ı — gözle okunan çıktı.** `--jinja` var/yok **aynı** render (bu sürüm gömülü jinja'yı zaten kullanıyor) · `enable_thinking` true/false **farklı** render ⇒ **bayrak gerçekten çalışıyor**. ⚠️ *Qwen3.5'in şablonu #38'i patlatan dalı **birebir taşıyor** (`{%- if enable_thinking is defined and enable_thinking is false %}`) — risk aynıydı, sonuç farklı çıktı. **Varsayılmadı, ölçüldü.***
Eğitim tarafı: şablon, **akıl yürütme izi olmayan** assistant mesajına `<think>\n\n</think>` **boş düşünce bloğu** ekliyor ⇒ SFT verimiz izsiz olduğu için **eğitim modele doğal olarak düşünce-kapalı şekli öğretiyor.**

**🚨 Bulgu 1 — düşünce kanalı `content`'i boşaltıyor.**

| koşul | `finish_reason` | completion_tok | `content` | `reasoning_content` | hız |
| :--- | :--- | ---: | ---: | ---: | ---: |
| varsayılan · 220 | `length` | 220 | **0** | 830 kar | 88.8 t/s |
| varsayılan · 1024 | `length` | 1024 | **0** | 3823 kar | 109.6 t/s |
| kapalı · 220 | `length` | 220 | 676 | 0 | 91.6 t/s |
| **kapalı · 1024** | **`stop`** | **249** | 773 | 0 | 84.7 t/s |

**Mekanizma:** `add_generation_prompt` `<think>\n` açar; bütçe içinde kapanmazsa llama-server ürettiğin **her şeyi** `reasoning_content`'e koyar, `content` **boş** döner — HTTP **200**, geçerli JSON, **hiçbir katmanda hata yok.**
**Neden kritik:** regex boş string üzerinde çalışır ve **sayı üretir**; CP2 = 480 çağrı, hepsi boş, **tablo dolar, koşu "başarılı" görünür, her sayı geçersizdir.** *#38 ile aynı sınıf, farklı mekanizma: şablon yanlış render edilmiyor — doğru render ediliyor ve model bütçeyi tüketiyor.*
**Önlem:** `--thinking {none,off,on}` · **boş cevapta `SystemExit`** (teşhis mesajı sebebi adlandırır) · detaya `finish_reason` + `reasoning_len` · **kesik cevap sayacı** (*yarım cevap hakeme yarım gider; bugüne kadar hiç raporlanmıyordu*).
**Ek gözlem:** akıl yürütme **İngilizce** üretiliyor — Türkçe görevde.

**🚨 Bulgu 2 — güç durumu performans sayılarını 17× bozuyor.** Aynı ikili, aynı build; **tek fark pil ↔ şarj**:

| model | koşul | pp512 | tg |
| :--- | :--- | ---: | ---: |
| Qwen3.5-4B Q4_K_M `-fa on` | **tasarruf** | 836.39 ± 65.47 | **7.45 ± 0.26** |
| Qwen3.5-4B Q4_K_M `-fa on` | **şarj** | **4789.35 ± 813.79** | **134.34 ± 3.30** |
| Gemma 4 12B Q4_0 (referans) | tasarruf | 487.10 | 5.50 |
| Gemma 4 12B Q4_0 (referans) | **şarj** | **1766.89** | **63.81** |

GPU: tasarruf **P4 · SM 180-225 MHz · 33 W** ↔ şarj **P0 · SM 1515 MHz · 130 W**. Decode **17×**, prefill **5,7×**.
⚠️ **Yanlış teşhis kaydı (dürüstlük gereği).** İlk ölçüm tasarruf modundaydı ve *"hibrit dikkatin decode yolu llama.cpp'de optimize değil"* diye yorumlandı; **referans 12B ölçümü de aynı tasarruf modunda alındığı için hipotezi çürütmek yerine gürültüyle örttü.** Doğru okuma *"ikisi de 15-20× yavaş → makine seviyesi"* olmalıydı.
**Sağlık kontrolü (şarj):** 134,34 t/s × 2,58 GiB ≈ **346 GB/s** — bu donanım için normal. **Hibrit dikkat decode yolunda sorun yok.**
> **Kural (bağlayıcı):** *hiçbir performans sayısı güç durumu kaydedilmeden raporlanmaz* — her ölçüme `pstate` · `clocks.sm` · `clocks.mem` · `power.draw` yazılır.

**🚨 Bulgu 3 — red-regex `bulunmuyor`u görmüyordu.** Türkçe'nin **şimdiki-zaman olumsuzu** kapsanmıyordu ve o, base'in **baskın red kalıbı**: 456 cevapta **194 kez**.

| mod | eski | kalibre |
| :--- | ---: | ---: |
| **M3** boş bağlam | **0.000** | **1.000** |
| M2b | 0.662 | 0.938 |
| M2 | 0.486 | 0.500 |
| M4 | 0.062 | 0.050 |

İkinci düzeltme: hukuk deyimi (`hüküm BULUNMAZSA`) kanunun kendi **koşul dili**, red değil → `(?!sa)` eledi. Doğrulama: **15/15 ileri + 2/2 geri** yön elle spot-check.

**🚨 Bulgu 4 — teacher jargonu `raft/` eğitim verisinde (#16 tekrarı).** `data/train/raft/` **scrub'lı DEĞİLDİ**: cevaplarda `GOLD`/`DISTRACTOR` etiketi **1301/17.323 (%7,51)**, öğrencinin girdisinde **0/17.323** ⇒ *model, karşılığı olmayan bir jetonu üretmeyi ezberleyecekti.* Onarım: etiketi **silmek yerine** öğrencinin dağarcığına çevir, satır **düşürme** (düşürmek #14 topik-skew'ü tekrarlardı); `##begin_quote##` blokları **dokunulmadı**. Sonuç **1435 satır onarıldı, kalıntı 0**, alıntılar bayt-bayt korundu.
**Bulgu 5 (küçük).** `.env`'de `BASE_MODEL=google/gemma-4-12B-…` (emekli hat) duruyordu — ADR-0026'nın tam uyardığı tuzak. *Script'ler `--model` gerektirdiği için koşular kurtuldu — **şans, tasarım değil.***

**CP2 — base çıpaları.** Hakem `gpt-4o-mini` (tek aile, iç kıyas) · DEV havuzu · seed 3407 · `--thinking off` · harness **KAPALI**.

| mod | doğru davranış | faith_macro (ALL) | **A1 (cevaplanan)** | coverage | Rej(regex) | Rej(LLM) | register |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| **M1** distractor | cevapla | 0.839 | **0.972** | **34/80 = %42.5** | — | — | 0.973 |
| **M4** oracle (tavan) | cevapla | 0.981 | 0.980 | 75/80 = %93.8 | — | — | 0.961 |
| **M2** near-miss | reddet | — | — | — | 0.567 | 0.633 | 0.964 |
| **M2b** çok-kaynak-ıska | reddet | — | — | — | 0.987 | 0.973 | 0.981 |
| **M3** boş bağlam | reddet | — | — | — | **1.000** | 1.000 | — |
| **M5** kör (anti-hedef) | — | 0.399 | — | — | — | — | 0.566 |

**Ana okuma — 12B'nin "kör red" deseni yeni base'de tekrarladı.** M1'de 80 sorunun **46'sını reddetti**, yalnız 34'ünü cevapladı; **ama cevapladığında çok sadık** (A1 **0.972** ↔ ALL 0.839) — *A1 kuralının neden zorunlu olduğunun kanıtı.*
⚠️ **Ve yüksek M2/M2b/M3 reddi bu körlüğün yan ürünü, "iyi kalibrasyon" değil.** `τ_grounding`'in işi **coverage'ı yükseltirken sadakati korumak**; ancak o zaman M2/M2b'nin körlükten arınmış değerini görebiliriz.
**M2 regex (0.567) < LLM (0.633):** hakem, *"reddedip ARDINDAN doğru cevabı da veren"* cevapları ABSTAIN sayıyor. **İki sayı birlikte okunur.**

**Kapı 0 — KARAR: `τ_register` düşüyor.** Register proxy RAG modlarında **0,96-0,98**; ön-kayıtlı kural *"yüksekse `τ_register` düşer"* → **kol 3→2, kafes 7→3 hücre, FT bütçesi 6→5.**
**CP3 — veri hazırlığı.** Token bütçesi: etkilenen **%0,06** (10/17.323 kesik, 0 düşen) → `max_seq_len=2048` korundu. Cevap medyanı 195 token (12B'de 196). Aykırı değer: bir maddede **307.687 karakter** (ek/cetvel).
**Kuantizasyon merdiveni.** f16 **8.07 GiB** · Q8_0 4.29 · Q6_K 3.32 · Q5_K_M 2.94 · **Q4_K_M 2.59 GiB** (5,13 BPW, duman testinde **3.09 GiB VRAM** @ctx 4096).
**Korpus.** 36,1 MiB · **40.496 madde** · 28,4 MiB metin; madde uzunluğu medyan **314** · p90 **1.598** · **max 307.687** karakter; 900-kar granülerlikte **60.297 chunk**.
**Ortam — açık üç kalem.** ① `fla` + `causal-conv1d` kurulu değil ② **`all-linear` görüntü kulesine LoRA takıyor** (38.756.352/2.642.481.664 = %1,467; `linear_fc1/linear_fc2/qkv/proj/out_proj` = `Qwen3_5VisionModel`) — *merge'i bozmaz (ΔW=0) ama **CP4'ün "param makul mü" kontrolünün yakalayamayacağı** bir yanlışlık: sayı 0 değil, **yanlış yere dağılmış*** ③ Unsloth `Processor` döndürüyor.
**Base davranışı — CP2'ye taşınan.** Tek örnekte: *"Verilen kaynakta bu bilgi yer almıyor. **Açıklama:** … genel zamanaşımı süresinin **10 yıl** olduğunu belirtmektedir…"* ⇒ **model hem reddediyor hem doğru cevaplıyor** ve regex bunu RED sayıyor. *Kalibrasyon **kendi öznemizde de** zorunlu.*

**Ders.** ① Kapı işini yaptı — iki tuzak da CP0'da yakalandı; **CP2'de yakalansalardı geriye dönük fark edilemezdi.** ② ***"Aynı jinja yapısı" ≠ "aynı sonuç"*** — risk aynı, sonuç farklı; **her base için tekrar ölçülmeli.** ③ ***Referans ölçümü de aynı koşulda alınırsa hipotezi çürütmez, örter*** — kontrol grubunun **kontrol edilmeyen değişkeni paylaşması.** ④ **Ortam borcu tahmin edilmez, ölçülür** — *"bir haftayı yiyebilir"* denen kalem tek satırdı.

---

<a id="40"></a>
## #40 — CP4: Faz B'nin kapısı bir paket bölünmesiydi · 36 → 5,4 s/it

**2026-07-25** · Karar: [ADR-0033](../adr/kararlar-0027-0044.md#adr-0033)

**Özet.** Faz B ~36 s/it'lik bir hız engeliyle bloke edilmişti ve teşhis *"`fla` torch ≥2.11 istiyor"* idi. **Bu teşhis yanlıştı.** Gerçek sebep bir **paket bölünmesi**ydi; düzeltmesi pinli ortama hiç dokunmuyor. **36 → 5,4 s/it (6,4×)**, ~11 sa/$25 → **~1,6 sa/~$4**, reçetede değişen hiçbir şey yok.

**Bulgu 1 — `flash-linear-attention` bölünmüş; `fla-core` olmadan fla'sız durumdan KÖTÜ.** 0.5.x'te `flash-linear-attention` yalnız `fla/layers`+`fla/models`, **`fla-core`** ise **çekirdekleri** taşıyor; image `--no-deps` kullandığı için (pinli lock'u korumak adına, **doğru bir tercih**) `fla-core` hiç kurulmadı.
**Sessiz-bozulmanın "kötüden de kötü" biçimi:** `import fla` **çalışıyor** → `is_flash_linear_attention_available()` yalnız **dağıtım sürümüne** bakıyor → **True**; ama `from fla.modules import FusedRMSNormGated` **çöküyor** → **model hiç yüklenmiyor.** Ve hata mesajı kök nedeni **gizliyor**: `ModuleNotFoundError: Could not import module 'Qwen3_5ForConditionalGeneration'` — ve bu satır A100'de **model indirildikten sonra** görülüyordu (her deneme ~25 dk A100).
→ **`modal_diag.py` yazıldı:** aynı image'ı en ucuz GPU'da açıp import zincirini deneyen ve **gerçek istisnayı** basan teşhis koşusu.
**Sürüm teşhisi çürütüldü:** `fla-core` yalnız `torch>=2.7.0` + `triton>=3.3` istiyor; lock'ta 2.10.0 + 3.6.0 ⇒ **fazlasıyla yeterli, ayrı image gereksizdi.**
⚠️ **Uyarı tuzağı:** `is_fast_path_available` **her ikisini** istediği için `causal_conv1d` yokken *"fast path is not available"* uyarısı **fla çalışıyorken de basılır**. **Uyarı ölçüt değildir; ölçüt `s/it`.**

**Bulgu 2 — hız kaldıraçları.** A100-40GB · bf16 donuk taban + LoRA r=16 α=32 · **11 modül** (`in_proj_*` dahil) · **29.908.992 eğitilebilir param (%0,65)** · seq 2048 · lr 1e-4 cosine · `adamw_8bit` · seed 3407 · 17.323 train · 50 adım smoke.

| konfigürasyon | s/it | tam koşu (1083 adım) |
| :--- | ---: | ---: |
| fla YOK | ~36 | ~11 sa · ~$25 |
| `fla-core` + checkpointing AÇIK + 1×16 | **10.5** | ~3,2 sa · ~$7,6 |
| **`fla-core` + checkpointing KAPALI + 2×8** | **5.4** | **~1,6 sa · ~$4** |

`fla-core` tek başına **3,4×**; ikisi birlikte **6,4×**. ⚠️ Devir notunun *"~4-5 s/it beklenir"* ifadesi bir **projeksiyondu, ölçüm değildi** — gerçek 10,5 çıktı. ***Projeksiyon ile ölçümü aynı cümlede kullanmamak gerekiyor.***
**İki kaldıracın da kökü aynı:** `train_sft.py`'nin varsayılanları **yerel 12 GB kart için** konmuştu ve yorumları bunu açıkça yazıyordu (*"12GB için zorunlu"*, *"dar VRAM → batch=1 ZORUNLU"*) ama **bulut koşusuna olduğu gibi taşınmıştı.**

**Bulgu 3 — kalite-nötrlük iddiası ÖLÇÜLDÜ.** `lora_dropout = 0` **REDDEDİLDİ**; red sebebi kaybın büyüklüğü değil **atfedilebilirlik**.

| | adım 10 loss | adım 50 loss |
| :--- | ---: | ---: |
| çıpa (checkpointing açık, 1×16) | **0.788** | — |
| seçilen (kapalı, 2×8) | **0.7987** | **0.3537** |

Fark **0,011** = batching/padding sırasından beklenen sapma. Artefakt doğruluyor: `r=16 · α=32 · dropout=0.05 · use_rslora=False · 11 modül`. **`use_rslora=False`** ⇒ `ΔW=(α/r)·BA` bozulmadı, **task-vector tanımı sağlam.**

**Bulgu 4 — iki yol tuzağı bir koşu yaktı.** ① **`--data` konteyner yoludur, volume yolu değil**; docstring yanlış yönlendiriyordu ve hata **model yüklendikten sonra** patlıyordu (~10 dk A100) → **veri kapısı model yüklemesinin önüne alındı**. ② **`--target-modules` verilmezse `in_proj_*` düşer** → **24 linear-attention katmanı LoRA'sız kalır, hata vermeden.**

**Yan iş — iki kod düzeltmesi.** **Yarış koruması (`runlock.py`):** aynı `--label` ile paralel iki skorlama çıktı dosyasını sessizce bozuyordu (`gnd_m4_gem.jsonl` 6 satıra, `gnd_m5_gem.jsonl` **0 satıra** düşmüştü) → artık `.lock` alınıyor ve ikinci süreç **para harcamadan erken patlıyor**. **`rescore_answered.py` kalibrasyonu ithal ediyor:** kendi KOPYA regex'ini taşıyordu ve docstring'i *"AYNI"* diyordu, ama kalibrasyon yalnız `score_abstention.py`'ye işlenmişti; ölçülen fark **3 ayrışma, üçü de kopyanın YANLIŞ-POZİTİFİ** — **yön tek taraflı: coverage olduğundan düşük görünüyordu**, ve coverage `τ_grounding`'in hedef metriği.

**Ders.** ① **Bir bağımlılık "kurulu" olabilir ve yine de yok olabilir** — denetim **dağıtım adına** bakıyorsa gerçek ölçüt **import zincirini denemektir.** ② **Tembel-modül sarmalayıcıları kök nedeni yutar** → **ucuz bir teşhis koşusu yaz.** ③ ***Varsayılanlar taşındıkları bağlamı taşımaz*** — yorum satırları sebebi zaten yazıyordu, **okunmadı.** ④ **Hız ile ölçüm geçerliliğini takas etme.** ⑤ **Ucuz denetimi pahalı adımın önüne koy.**

---

<a id="41"></a>
## #41 — CP6: `τ_grounding` ölçümü — kör red kırıldı, bedeli cevap başına sadakat

**2026-07-29 · Sprint 1 / CP6**

> **Bir cümlede:** `τ_grounding` base'in kör reddini kırdı (M1 coverage **%43,8 → %85,0**) ve sadık cevap kütlesini **%42,6 → %72,0** çıkardı — Gemini 3.1 Flash-Lite'ın (%74,2) 2 puan altı; **ama** cevap başına sadakat düştü (**A1 0,973 → 0,847**) ve düşüşün yarısı **gerçek**, yarısı hakem tarafındaki bir **biçim artefaktı**.

**Künye.** `τ_g` = Qwen3.5-4B + LoRA(r=16,α=32) **merge**, Q4_K_M GGUF · llama.cpp `-c 4096`, KV q8_0 · `--thinking off` · 512 tok · seed **3407** · klip **900** · DEV havuzu (TEST **görülmedi**) · n = **470 cevap** · hakem `gpt-4o-mini` tek aile · harness **KAPALI** · hakem **$0,1506**, GPU **$0**.
**CP5 künyesi:** 1.083 adım · A100-40GB · **6,8-7,0 s/it** *(ADR-0033'ün 5,4'ü smoke projeksiyonuydu)* · 2.619 tok/s · MFU ≈ %15 · **`‖τ_g‖_F = 10,4589`** · **224 LoRA çifti** (`8×4 + 24×4 + 32×3` — **mimari varsayımını birebir doğruladı**).

**Eksik halka kapandı — adaptör → GGUF.** `merge_lora.py` **akıtmalı** (tensör-tensör), `merge_and_unload()` **değil**; `ΔW=(α/r)·B@A` float32'de toplanıp özgün dtype'a dönüyor. 41 sn, tepe RSS 9,86 GB.
**İki teyit kapısı:** `‖merged − base‖_F` beklenen 10,4589 ↔ ölçülen **10,4966** (+%0,36, bf16 yuvarlama) · GGUF boyutu **2,59 GiB** = base ✅ · görüntü kulesi/`mtp`/embed **Δ = tam olarak 0** (metin kulesi dışına sızma yok).
⚠️ `setup_llamacpp.sh`'ta **`set -e`, `snap=$(ls …)` atamasında mesajsız öldürüyordu** — hattın klasik sessiz-ölüm deseni.

**Sonuç — üçlü tablo.**

| eksen | base | Gemini 3.1 FL | **`τ_g`** | ön-kayıt | tuttu mu |
| :--- | ---: | ---: | ---: | :---: | :---: |
| **M1** coverage | 35/80 = %43.8 | 61/80 = %76.2 | **68/80 = %85.0** | ↑↑ | ✅ |
| **M1 A1** | 0.9730 | 0.9729 | **0.8472** | ↑↑ | ❌ **düştü** |
| M1 faith_macro (ALL) | 0.8385 | 0.8734 | 0.8371 | ↑↑ | → |
| M1 cit_precision | 0.9775 | 0.9900 | 0.9500 | — | ↓ *(gürültü bandında)* |
| **M4** A1 / coverage | 0.9800 / %95.0 | 0.9793 / %97.5 | 0.9794 / %96.2 | → | ✅ tavan |
| **M2** Rej (LLM) | 0.6330 | 0.8420 | **0.4580** | ↓↓ | ✅ |
| **M2b** Rej (LLM) | 0.9730 | 0.9700 | **1.0000** | ↑ | ✅ |
| **M3** Rej | 1.0000 | 1.0000 | 1.0000 | → | ✅ tavan |
| **M5 A1** *(ANTİ-HEDEF)* | 0.2852 | 0.6213 | **0.4018** | ↓/→ | ❌ **yükseldi** |
| M5 coverage | %37.5 | %23.8 | %36.2 | ↓/→ | ✅ |
| register proxy | 0.961-0.981 | 0.919-0.988 | **0.945-1.000** | → | ✅ |

⚠️ `Rej` paydaları modele göre değişir (`valid_traps`: M2 60/57/**59** · M2b 75/67/**80** · M3 57/57/**50**) — **oran payda ile birlikte okunur.** ⚠️ Gemini'nin **regex-red sayıları raporlanamaz** (o aile için kalibrasyon yapılmadı).

**4.1 Kör red kırıldı — hattın ana kazancı.** Sadık-cevap kütlesi: base **%42,6** ↔ Gemini **%74,2** ↔ `τ_g` **%72,0**. *Base'i ikiye katladı ve rakibin 2 puan altına geldi.*
**4.2 A1 düşüşü seçim yanlılığı DEĞİL.** Her ikisinin de cevapladığı **ortak 27 soruda**: base **0.9774** · Gemini **0.9795** · **`τ_g` 0.8778** ⇒ **kolay sorularda da ~0,10 düşük, gerileme gerçek.**
**4.3 Düşüşün yarısı hakem tarafında bir biçim artefaktı — ⚠️ kafesin tamamını etkiler.**

| M1, cevaplanan iddialar | base | **`τ_g`** |
| :--- | ---: | ---: |
| toplam iddia | 147 | 242 |
| `CONTRADICTED` *(gerçek hata)* | **1** | **11** |
| `NOT_IN_SOURCE` | 3 | **31** — **18'i (%58) meta-iddia** |
| hatalı iddia oranı | %2.7 | **%17.4** |
| meta-iddia düşülürse | %2.7 | **%9.9** |

Meta-iddia = RAFT'ın **1. adımı**; cümle **kaynak hakkında**, kaynaktan değil — hakem haklı olarak `NOT_IN_SOURCE` diyor, **ama `τ_g` onu yazmak zorunda** (eğitim verisinin %77'si bu biçimde). ⇒ Kafesin **8 eval koşusunda `τ_g` içeren her hücre sistematik ceza alacak, `τ_a` tekili almayacak** → **Kapı 5'in kıyası bozulur.** Sayılar **düzeltilmedi**; düzeltme ön-kayıtlı olur ve **tüm kollara** uygulanır ([ADR-0041](../adr/kararlar-0027-0044.md#adr-0041)).
**4.4 M2 düştü — ön-kayıtlı, panik değil; ama M2b 1.000.** M2 **0,633 → 0,458**; bu şekil eğitim verisinde **hiç yok**. M2b **0,973 → 1,000** ve M3 **1,000** sabit ⇒ ***model "gold yoksa reddet"i öğrendiği çerçevede kusursuz yapıyor, öğrenmediği çerçevede kaybediyor*** — **`τ_abstention`'ın ve merge'ün varlık gerekçesi tam olarak bu.** ⚠️ M2b'nin **paydası da büyüdü** (75 → 80) ⇒ 1,000 **daha zor bir paydada** alınmış.
**4.5 ❌ ANTİ-HEDEF İHLALİ — M5 yükseldi.** Coverage sabit (kör cevaplama artmamış) ama **cevapladığında daha doğru**: A1 **+0,117**, atıf kesinliği **+0,120** — hakem gürültü bandının çok üstünde. ⇒ **RAFT eğitimi kanun metnini bol gösterdi; bir kısmı ağırlıklara yerleşti.** *"Güncellik kütüphanede yaşar"* kısıtı bu eksende **kısmen delindi.**

**Yan bulgu — hakem gürültü bandı (bedava tahmin).** Aynı cevaplar üzerinde ikinci hakem koşusu: M4 faith_macro fark **0,0002** · M5 faith_macro **0,0046** · M5 **`cit_precision` 0,0442** ⇒ `faithfulness_macro` **tekrar-kararlı (≤0,005)**; **`cit_precision` tavan dışı bölgede ±0,04 oynuyor** ⇒ M1'deki cit_precision düşüşü **sinyal sayılmadı**.
**Kesiklik `τ_g` aleyhine yanlılık yaratmıyor:** M1 base 3/80 → **0/80** · M2b 4/80 → **0/80** · M5 12/80 → 10/80.
**Belge çelişkileri işaretlendi, sessizce üzerine yazılmadı:** `sprint1.md`'nin CP2 tablosu artefakt JSON'larla **dört yerde** uyuşmuyor (M1 coverage %56 ↔ **%43,8**; M2 Rej 0.500 ↔ **0.567**…). #39 ile artefakt arasındaki 1 örneklik fark **açıklanmadı ve doğrulanmadı.**

---

<a id="42"></a>
## #42 — CP0: düşünce modu ölçülemedi, çünkü model DURMUYOR — ve bunu kol çözüyor

**2026-07-29 · Sprint 2 / CP0** · [ADR-0040](../adr/kararlar-0027-0044.md#adr-0040) → [ADR-0043](../adr/kararlar-0027-0044.md#adr-0043)

> **Bir cümlede:** `--thinking on` altında çıplak base **6 moddan 3'ünde hiç cevap üretmiyor** — kesilme değil **sonlanmama**: model cevaplamak ile çekinmek arasında karar veremeyip aynı muhakemeyi **219 kez** tekrarlıyor; bütçeyi **8× artırmak**, örneklemeyi değiştirmek ve kuantizasyonu yükseltmek **üçü de çözmedi** — **ama `τ_grounding` aynı istemlerde düşünüp duruyor** (35/36, medyan 510 token), yani eğitim düşünmeyi öldürmemiş, **kararlı hâle getirmiş.**

**Künye.** base (Q4_K_M ve Q8_0) + `τ_g` v1 · `-ngl 99 -fa on --no-context-shift`, KV q8_0 · ctx **8192-40960** *(Sprint 1'in 4096'sı düşünce bütçesinin yanına sığmıyor — sapma bilinçli, istem birebir aynı)* · temp 0 · seed 3407 · klip 900 · n = mod başına **1-8 örnek** (mekanizma tespiti, kapı ölçümü değil) · hakem **çağrılmadı** · **$0**.
**Referans (thinking-off):** M2 Rej **0,6330** · M1 kütle **%42,6** · M5 ezber kütlesi **%10,7** · **249 token**/cevap.

**🚨 Bulgu 1 — `</think>` hiç kapanmıyor: kesilme değil sonlanmama.** İlk smoke **ilk örnekte** patladı (`finish_reason='length'`, `reasoning_content=15125 kar`). Bütçe **32768'e (8×)** çıkarıldığında da `content` **0**, iz 108.568 / 119.114 karakter.
**Mekanizma bütçe değil, DÖNGÜ.** İz satır analizi: örnek 0 → 1.456 satır, **225 benzersiz (%15,5)**; örnek 1 → 994 satır, 216 (%21,7). En çok tekrarlananlar:
```
219× *  Okay, I will check the instruction again. "İlgili kaynak YOKSA cevap uydurma".
112× *  If I say "Verilen kaynaklarda bu konuyu düzenleyen madde bulunmuyor", it is the most accurate…
111× *  So I will use **KAYNAK 2**.
111× *  Wait, I need to check if I should say "…bulunmuyor"…
```
⇒ **Döngünün çekim merkezi bizim sistem istemimizdeki çekimserlik talimatı.** Model *"kaynaktan cevapla"* ile *"kaynakta yoksa 'bulunmuyor' de"* arasında salınıyor; `temperature=0` greedy decoding'de **kaçış yok**.
> ⚠️ #38/#39 ile **aynı sınıf** ama **üçüncü bir mekanizma**: şablon doğru render ediliyor, model bütçeyi tüketmiyor — **hiç bitirmiyor.**

**Bulgu 2 — döngü BELİRSİZLİKLE geliyor, modla değil.**

| mod | ne soruyor | sonuç | ort completion_tok |
| :--- | :--- | :--- | ---: |
| **M4** oracle | cevap **açıkça** var | ✅ 3/3 sonlandı | **3.932** |
| **M3** boş bağlam | red **açıkça** doğru | ✅ 3/3 sonlandı, 3/3 temiz red | **1.126** |
| **M2** yakın-ıska | cevaplasam mı, reddetsem mi? | ❌ düştü | — |
| **M5** kör | ezberden mi konuşsam? | ❌ düştü | — |
| **M1** 5 kaynak | hangisi ilgili? | ❌ 0/2 (32k'da bile) | — |

**Örüntü:** cevabın ya da reddin **açık** olduğu modlarda sorun yok; **karar belirsizse model duramıyor.** Ve bu tam olarak ADR-0040'ın karar eksenlerinin bulunduğu yer ⇒ ***ölçülemeyen üç sayı, tam da karar için gereken üç sayıydı.***

**Bulgu 3 — üç alternatif açıklama ELENDİ.** "bütçe yetersiz" → 4096→**32768 (8×)**, ❌ 2/2 yine düştü · "greedy decoding suçlu" → `temp 0.6/top_p 0.95/top_k 20`, 🟡 **yarısı** (sonlanan örnek **6.918 tok**) · "Q4_K_M artefaktı" → **Q8_0** (2× hassasiyet), ❌ **2/2 düştü**.
*Örneklemenin yarısını kurtarması dikkate değer ama çözüm değil: %50 başarısızlık kalıyor, sonlanan örnek 6.918 token yakıyor ve **protokolü kirletiyor** — Sprint 1'in üç çıpası `temperature=0` ile üretildi.* Sonlanan `temp 0.6` örneğinin cevabı da öğretici: gold kaynak **promptta VARken** *"…bulunmamasına rağmen"* diye başlıyor.

**⭐ Bulgu 4 — `τ_g` v1 düşünüyor VE duruyor.** ADR-0040'ın "hasar sensörü" hasar aramaya gitti, **tersini buldu.** Aynı M1 istemleri, temp 0, 8192 bütçe, n=8: **7/8 sonlandı**, sağlıklı 7'de **medyan 452, ort 463 token** (aralık 429-563, **çok dar**) · düşünce izinde **tekrar döngüsü YOK** (benzersiz/toplam **8/8 dosyada 1.000**) · erken kapatma da yok (iz 819-1.568 kar).

| aynı iki istem | base | **`τ_g` v1** |
| :--- | ---: | ---: |
| örnek 0 iz | **108.568 kar**, kapanmadı | **955 kar**, kapandı |
| örnek 1 iz | **119.114 kar**, kapanmadı | **1.568 kar**, kapandı |

**İzin kalitesi yapılı** — istenen eleme davranışının ta kendisi (*"KAYNAK 1: …not directly about… KAYNAK 3: Specifically addresses… this is the most relevant"*).
**Yorum.** `τ_g`'nin eğitim verisinde akıl yürütme izi **yok**; ADR-0040 *"izsiz veriyle eğitmek yeteneği aktif bastırır"* diye korkuyordu — **ölçümde tersi çıktı.** RAFT eğitimi modele **kararlı bir prosedür** verdi ve döngünün beslendiği kararsızlık ortadan kalktı ⇒ *"reçete fazla sertti"* hipotezi **desteklenmedi.**
**Ek gözlem — asimetri:** iz **8/8 İngilizce**, cevap **8/8 Türkçe.** *Eğitim cevap kanalını Türkçeleştirmiş, düşünce kanalına dokunmamış.*

**🚨 Bulgu 5 — yeni sessiz bozulma: 900-kar klip numaralı listeyi ortadan kesiyor.** `τ_g`'nin tek başarısız örneği düşünce arızası **değil** (iz kusursuzdu): klip KAYNAK 3'ü (CMK m.153) **numaralı suç listesinin ortasında** kesmiş (`"…Karşı Suçlar (madde 309, 310, 311,"`) ve model *"birebir alıntıla"* talimatı altında yarım diziyi **kendisi sürdürüyor** (`…1682, 1683, 1684`) — 8192 sınırına kadar. **Cevabın ilk %12,3'ü sağlıklı, gerisi çöp.**
**Neden tehlikeli:** hata yok, cevap dolu, **hakem onu puanlar** — ve **satır-bazlı döngü metriği kaçırıyor** (2 satır, 8.625 karakter). Yakalayan tek şey `finish_reason='length'` sayacı. → tuzak **1.9**.

**Çözüm — bütçeli düşünce (zorunlu kapatma).** ① düşünceye **N token** izin ver ② `content` boşsa **ham istem + iz + `</think>\n\n`** ③ `/completions` ile devam → *model o noktadan sonra cevabı **yazmak zorunda**.* Doğrulama (base, 1024+512, n=2): **2/2 zorla kapatıldı**, cevaplar **tutarlı, atıflı, biçimli** ⇒ **kesilmiş düşünceden çöp çıkmıyor.**

**Maliyet ekseni.** thinking-off **249** (1×) · bütçeli 1024+512 **~1.198 (~4,8×)** · `τ_g` doğal sonlanma **~463 (~1,9×)** · bütçesiz M3 1.126 (4,5×) · bütçesiz M4 **3.932 (15,8×)** · `temp 0.6` sonlanan **6.918 (27,8×)**. ⇒ **`τ_g` base'in bütçesinin yarısından azını harcıyor — düşünce maliyeti de kolla düşüyor.**
**ADR-0040'ın kuralına ne oldu.** Üç sayı da **üretilemedi**; geçerlilik ön şartı *"kesik > %5 → bütçeyi artır"* diyordu ama **kesilme değil sonlanmama** — kural bu dalı **öngörmemişti.** Sonuç 🟢🟡🔴 değil, *"ölçüm bu kipte üretilemiyor"* + mekanizma; karar **ölçümle değil ürün gereksinimiyle** alındı.

---

<a id="43"></a>
## #43 — CP0.9: üç çıpa bütçeli düşünce kipinde · anti-hedef ekseni 3,4× yanlış ölçülüyormuş

**2026-07-29** · [ADR-0043](../adr/kararlar-0027-0044.md#adr-0043) · [**ADR-0044**](../adr/kararlar-0027-0044.md#adr-0044) (bu turda doğdu) · `outputs/eval/cp09-butceli-1024-512/`

**Neden koşuldu.** ADR-0043 protokolü değiştirdi ⇒ Sprint 1'in üç çıpası **artık çıpa değil**; `τ_a` bunlara karşı ölçülürse ARA KAPI **yanlış okunur.**
**Künye.** DEV (80 core_hard + 70 trap) · n = **470 × 3 özne = 1.410** · düşünce **1024** + cevap **512** (ön-kayıtlı) · seed 3407 · klip 900 · temp 0 · rakip `gemini-3.1-flash-lite` @OpenRouter, provider **pinli**.
**Rakip tarafı düşünce bütçesi — yeni karar.** ADR-0043 bütçeyi *"bütün rakipler"* için rejim değişmezi ilan ettiğine göre Gemini de **1024+512** koşar. ***Rakibi düşüncesiz koşmak sapmayı bizim lehimize kaydırırdı.*** `reasoning_tokens` **ayrı alana** yazılır (Google izi **metin olarak vermiyor**; karakter sayacıyla aynı alana yazmak **sessiz yanlışlık** üretirdi).
**Geçerlilik kapıları — üçü de geçti.** base 17 kesik (**%3,6**), ort **1135** tok, 445/470 zorla · `τ_g` 17 (%3,6), **772** tok, 209/470 · Gemini **0 (%0,0)**, **543** tok. Düşünce kanalı **470/470** kullanıldı.

**Bulgu 1 ⭐ — anti-hedef ekseni 3,4× yanlış ölçülüyormuş.** Rakip kalibrasyonu **temiz çıktı**, ama ileri yön denetimi başka bir şey buldu: **kör mod (M5) `SYSTEM_PROMPT`u kullanır ve o istem feragat cümlesini EMREDER**; `REJECT_RE` onu red kalıbı sayıyordu ⇒ **model dolu cevap verip sonuna feragati ekleyince çekinmiş sayılıyordu.**

| dosya | RED etiketli | yalnızca feragat | gerçek red |
| :--- | --: | --: | --: |
| `m5_base` (off) | 50/80 | **45** | 5 |
| `m5_base_th` | 56/80 | **54** | 2 |
| `m5_tg` (off) | 51/80 | **50** | 1 |
| `m5_gem_th` | 62/80 | **58** | 4 |

Feragatli cevapların medyan uzunluğu **1082 karakter**, içerikleri dolu — üstelik sık sık uydurma.
**Düzeltilmiş Kapı 6 çıpası** (hakem çağrısı **yapılmadan**): base cov 37.5%→**93.8%**, A1 0.285→0.394, kütle **10.7% → 36.9%** · `τ_g` 36.2%→98.8%, 0.402→0.448, **14.6% → 44.2%** · Gemini 23.8%→98.8%, 0.621→0.578, **14.8% → 57.1%**.
**Üç sonuç:** ① sapma **bizim lehimizeydi** ② `τ_g`'nin ihlali **artefakt değil, büyüdü** (+3,9 → **+7,3 puan**) ③ hata **rastgele değil** — A1 düzeltmeden sonra **yükseldi**, yani **paydayı da payı da** kaydırıyordu. **Etki alanı yalnız M5.**

**Bulgu 2 ⭐ — sonlanma kararlılığı EĞİTİM İSTEMİ AİLESİNE ÖZGÜ.** #42 n=36'da *"`τ_g` düşünüyor ve duruyor"* demişti; n=470'te bu **yalnız kendi istem ailesinde** doğru:

| istem ailesi | modlar | base zorla | `τ_g` zorla | ort tok base→`τ_g` |
| :--- | :--- | --: | --: | :--- |
| **RAG_MULTI** ← `τ_g`'nin eğitim biçimi | m1·m2b·m3 | %91.7 | **%5.8** | 1098 → **476** |
| RAG_tek | m4·m2 | %96.7 | %79.3 | 1116 → 1046 |
| BLIND | m5 | %100.0 | %95.0 | 1284 → 1146 |

*Kendi ailesinde etki muazzam, dışında marjinal. #42'nin örneklemi o aileden geldiği için genel bir kazanç gibi görünmüştü.*
**Bulgu 3 — maliyet ekseni rakibin lehine.** base **1135** · `τ_g` **772** · Gemini **543** tok/cevap; rakip 1024'lük bütçeyi **doldurmuyor** (ort 444 düşünce token'ı) ve **kendi duruyor**. Base rakibin **2,09 katı**, `τ_g` bunu **1,42**'ye indiriyor.
**Bulgu 4 — base n=3'te sonlanıyor görünüyordu, n=80'de sonlanmıyor.** M4 3/3 → **76/80 zorla**; M3 3/3 → **60/80**. ⇒ *Sonlanmama belirsizliğe özgü bir kenar durum değil, base'in bu ailelerdeki **genel davranışı*** — bütçeli kapatma kararı **göründüğünden daha zorunluymuş**. → **yeni tuzak: n=3 smoke, n=470'i temsil etmiyor.**

**Puanlama sonuçları.** Hakem `gpt-4o-mini` · `runs=1` · **$0,447** (+ablasyon $0,046).

| ölçüt | yön | base off | **base bütçeli** | `τ_g` off | **`τ_g` bütçeli** | Gemini off | **Gemini bütçeli** |
| :--- | :-: | --: | --: | --: | --: | --: | --: |
| **M1** sadık-cevap kütlesi % | ↑ | 42.6 | **56.7** | 72.0 | **71.4** | 74.2 | **72.9** |
| M1 coverage % | · | 43.8 | 57.5 | 85.0 | 82.5 | 76.2 | 76.2 |
| M1 A1 | ↑ | 0.973 | 0.986 | 0.847 | 0.866 | 0.973 | 0.956 |
| **M4** oracle kütlesi % | ↑ | 93.1 | 95.9 | 94.3 | 94.7 | 95.5 | 93.7 |
| **M2** Rej (LLM) | ↑ | 0.633 | **0.814** | 0.458 | **0.873** | 0.842 | **0.930** |
| M2 geçerli tuzak (payda) | · | 60 | 59 | 59 | 55 | 57 | 57 |
| M2 fabrikasyon | ↓ | 0.367 | 0.186 | 0.542 | 0.127 | 0.158 | 0.070 |
| **M2b** Rej (LLM) | ↑ | 0.973 | 0.986 | 1.000 | **0.607** 🔴 | 0.970 | 1.000 |
| **M3** Rej (LLM) | ↑ | 1.000 | 1.000 | 1.000 | 0.923 | 1.000 | 1.000 |
| **M5** ezber kütlesi % *(ANTİ-HEDEF)* | ↓ | 36.9 | 42.5 | 44.2 | **39.2** | 57.1 | 54.4 |
| **ort token/cevap** | ↓ | — | 1135 | — | **772** | — | 543 |
| zorunlu kapatma % | · | 0 | 94.7 | 0 | 44.5 | 0 | 0 |

> ⚠️ **ÇELİŞKİ İŞARETİ (2026-07-30, [#45](#45)).** Bu tablodaki **M2/M2b/M3 Rej** paydası (`valid_trap`) hakem tarafından **özne başına yeniden yargılanıyor** ve hakem **öznenin cevabını görüyor**. Aynı 80 M3 kaleminde `valid_trap` = base 54 · Gemini 56 · `τ_g` **39**; **M3'te bağlam boş** olduğundan doğru payda **80/80**'dir ⇒ doğru okunuş base **1.000** · Gemini **1.000** · `τ_g` **0.800** — yukarıdaki **0.923 fazla iyimser.** Filtresiz: M2 base 0.786 · `τ_g` 0.800 · Gemini 0.814; M2b base 0.950 · `τ_g` 0.525 · Gemini 0.850. **Sapma tek yönlü değil: M2b'de aleyhimize ~7p, M3'te lehimize ~12p.** ADR-0040'ın 🟡 hükmü değişmiyor (0.786 ≥ 0.78). Sayılar **üzerine yazılmadı.**

**ADR-0040 hükmü: 🟡 SARI — muhafız düştü, eşik geçti.** M2 Rej 0.633 → **0.814** ≥ 0,78 ✅ (+18,1p) · M1 kütle %42,6 → **%56,7**, eşik %57,6 ❌ (**0,9 puan kaldı**) · M5 ezber kütlesi %36,9 → **%42,5** ❌ **İHLAL** (+5,6p). Hüküm **ADR-0044'ten bağımsız sağlam** (muhafız hem eski hem düzeltilmiş referansta ihlal ediliyor) ⇒ **RS-FT Sprint 2 kapsamına GİRMİYOR.**
> ⚠️ **Ön okumam yanlış gerekçeyle doğru çıktı.** 🟡 tahmin etmiştim ama **M2 bacağının düşeceğini sanarak**: regex→LLM farkını +13,3 p varsaymıştım, gerçekte **+20,4 p**. Hükmü belirleyen **M5 muhafızı** oldu.

**Bulgu 5 ⭐ — düşünce AYIRT ETME yeteneğini artırıyor, biçim yanlılığı değil.** M2'de **11 `FABRICATE→ABSTAIN`** kazancı, 2 ters kayıp (n=57). İki mekanizma adayı: (A) muhakeme gerçekten karşılaştırıyor · (B) zorunlu kapatma şablonu reddi kolaylaştırıyor. Bu koşu ikisini **ayıramaz** (70 örneğin 69'u zorla kapatıldı). **Ama (B) tek başına elendi:** aynı protokol M1'de **ters yöne** gidiyor (red %56,2 → %42,5) — ***saf bir şablon yanlılığı iki eksende zıt yönde hareket üretemez.***

**Bulgu 5-b ⭐ — ablasyon: kazanç BİÇİMDEN gelmiyor ($0,046).** Sistem istemine yeterlilik satırı eklenip **thinking-off** koşuldu:

| kol | M1 kütle ↑ | M1 coverage | M2 Rej ↑ | ort token |
| :--- | --: | --: | --: | --: |
| base thinking-off | 42.6% | 43.8% | 0.633 | ~249 |
| base **bütçeli düşünce** | **56.7%** | 57.5% | **0.814** | 1116 |
| base **önsöz + thinking-off** | **28.2%** 🔴 | 31.3% | **0.968** | **116** |

Önsöz M2'de **0,968**'e çıkıyor — düşünceden de Gemini'den de yüksek — ama **aşırı-red oranı 0,6875**: M1'de 80 sorunun yalnız **25'ini** cevaplıyor.
**Ayrım tamamlandı:** önsöz **tek eksende kaydırıyor** (M2'de +33,5p, M1'de −14,4p) — *bu ayırt etme değil, **red eşiğini indirmek***; **bütçeli düşünce iki ekseni aynı anda yukarı taşıyor** — *bir eşik kaydırması tanım gereği bunu yapamaz.*
⇒ **Mekanizma (A) doğrulandı: düşünce gerçekten ayırt etme yeteneğini artırıyor, 4,5× token'ın karşılığı var.** İkincil sonuç: ***`τ_a`'nın işi de bir istem satırıyla yapılamaz — kör red ucuz, ayırt etme pahalı.***

---

<a id="44"></a>
## #44 — CP0.5 · CP1 · CP2: Sprint 3'ün zemini (hız kaldıracı · hakem taraflılığı · hasat boyutu)

**2026-07-30 · GPU yerel ($0)** · [ADR-0041](../adr/kararlar-0027-0044.md#adr-0041) · [ADR-0046](../adr/kararlar-0045-0063.md#adr-0046)

### CP0.5 — `causal-conv1d`: kapı KALDI, eklenmiyor

Önce **kaynak okundu**: çekirdekler **bağımsız** ikame ediliyor ve `fla-core` kurulu olduğu için **pahalı özyineli çekirdek zaten hızlı yolda** (kimlik kontrolü `modeling.chunk_gated_delta_rule is fla.ops…` → **True**). `is_fast_path_available` yalnız bir `warning_once` tetikliyor, **başka hiçbir şeyi kapatmıyor** ⇒ *uyarı ölçüt değil.* `causal-conv1d` yokluğunda fallback'e düşen **tek şey** depthwise conv.
**Ölçüm — derlenmeden, kazancın TAVANI ölçüldü.** Hızlı yol dalına **bedeli sıfır bir saplama** kondu (`x → x`); gerçek çekirdek bundan hızlı olamaz ⇒ oran kazancın **matematiksel üst sınırı**:

| batch × seq | A: bugün (torch) | B: ideal çekirdek, bedel 0 | conv payı | **tavan** |
| :--- | --: | --: | --: | --: |
| **2 × 2048** *(Modal eğitim koşusu)* | 35.11 ms | 28.00 ms | %20.3 | **1.254×** |
| 1 × 2048 | 17.78 | 14.63 | %17.7 | 1.216× |
| 2 × 1024 | 17.68 | 14.70 | %16.9 | 1.203× |
| 4 × 512 | 16.49 | 13.78 | %16.4 | 1.196× |

Dört şekilde de kararlı ⇒ **tek-şekil artefaktı değil.** **Neden katman-seviyesi ölçüm yeterli (ve model-seviyesinden güçlü):** conv yalnız **24/32** katmanda; kalan 8 full-attention, 32 MLP ve 248.320'lik `lm_head` **paydaya eklenir, paya eklenmez** ⇒ model-seviyesi tavan **kesinlikle küçüktür**.
> 🔴 **Ön-kayıtlı kapı: ≥2× yoksa eklenmez → KALDI.** Tavan **1,254×**. `requirements.lock.txt` korunuyor.

**Sapma kontrolü yapıldı:** `fla` yerelde bozuk olsaydı payda şişer, conv payı **olduğundan küçük** ölçülür ve **sapma tam da verilen kararın lehine olurdu.** ⚠️ Ölçüm yerel karttadır, çıpa A100'de — **taşınan şey oran**, mutlak s/it değil.
> **`fla-core` dersi (#40) uygulandı:** kazanç ölçülmeden yazılmadı — **ama bu kez ölçüm negatif çıktı ve paket eklenmedi.** Fark: ölçümün **para harcanmadan önce** yapılması.

### CP1 — RAFT meta-iddia muafiyeti: `τ_g`'nin A1 açığının %59'u artefaktmış

Hakem **$0,113**. Üretim **yeniden yapılmadı** — değişen tek şey groundedness hakeminin **AŞAMA-1 (iddia çıkarımı) istemi**; ADR-0041 m.1 gereği **üç özneye aynı anda**.
**Kapsam ölçülerek daraltıldı:** meta-cümle (`KAYNAK\s*\d`) **yalnız M1'de** var — base **36/80** · `τ_g` **58/80** · Gemini **0/80**; M4 ve M5'te üçünde de 0/80. *Tek kaynak varken "hangi kaynak ilgili" cümlesi kurulmuyor.* ⚠️ Gemini 0/80 ⇒ **düzeltmeden yapısal olarak yalnız bizim öznelerimiz yararlanabilir**; kural yine de üçüne uygulandı ki sayılar **aynı hakem sürümünden** gelsin.

| ölçüt | base ESKİ→YENİ | `τ_g` ESKİ→YENİ | Gemini ESKİ→YENİ |
| :--- | :--- | :--- | :--- |
| toplam iddia | 309 → 275 | 287 → **228** | 301 → 271 |
| `CONTRADICTED` | 10 → 4 | 15 → 10 | 8 → 4 |
| `NOT_IN_SOURCE` | 26 → 17 | 37 → **12** | 21 → 14 |
| **hatalı iddia oranı** | %11.7 → **%7.6** | %18.1 → **%9.6** | %9.6 → **%6.6** |
| `faith_micro` | 0.8835 → 0.9236 | 0.8188 → **0.9035** | 0.9037 → 0.9336 |
| **M1 A1** | 0.9864 → **0.9777** | 0.8658 → **0.9283** | 0.9561 → **0.9421** |
| coverage | 46/80 → 46/80 | 66/80 → 66/80 | 61/80 → 61/80 |

**ADR-0041'in öngörüsü tuttu** (*"meta-iddialar düşülürse %9,9"* ↔ ölçülen **%9,6**). `τ_g`'nin base'e karşı A1 açığı **0,120 → 0,049** ⇒ **açığın %59'u biçim artefaktıymış.** Coverage üçünde de **değişmedi** (beklenen).
**Kalan açık maskelenmiyor:** `τ_g`'nin hatalı iddia oranı düzeltmeden sonra da base'in **1,26 katı** ve `CONTRADICTED` hâlâ 10 ↔ 4.

**⚠️ Bulgu — ADR-0041 m.2'nin kontrolü TEMİZ ÇIKMADI.** Cevaplar meta-cümle **taşıyan/taşımayan** diye bölündü: `τ_g`'de kural **tam hedefe isabet ediyor** (meta VAR −%28 ✅ · meta YOK **+%6** ✅); **base ve Gemini'de ise ters** (base meta YOK **−%22** ⚠️ · Gemini hepsi meta-yok **−%10** ⚠️).
**Ayırt etme koşusu** — Gemini'de muafiyet **mantıken uygulanamaz**, aynı istemle **ikinci kez** koşuldu ($0,037):
```
saf hakem gürültüsü (yeni1 → yeni2) : −10 iddia  ·  faith ±0,012
istem etkisi        (eski → yeni1)  : −30 iddia  ·  faith +0,030
```
⇒ **Hedef-dışı etki gerçek ama küçük: gürültünün ~3 katı.** Kural üç özneye de uygulandığı için **sıralama kıyası geçerli kalır**; ama **mutlak sadakat sayıları üç öznede birden yukarı kaymıştır** ve CP0.9 tablosuyla **doğrudan kıyaslanamaz.**
⚠️ `cp1_spotcheck.py`'ın ham sayaçları **yanıltıcıdır**: hakem iddiaları sık sık **yeniden ifade ediyor** ve tam-string kıyası bunu "silinmiş" sayıyor ⇒ muafiyet sınırının denetimi **gözle** yapıldı.
**ARA KAPI muhafızına etkisi — sayı DEĞİŞTİRİLMEDİ.** `0,90 × 0,9864 = 0,888` (yazılı) ↔ `0,90 × 0,9777 = 0,880` (yeni hakem). Fark **bizim lehimize** olduğu için sayı kendiliğinden değiştirilmedi: **`τ_a` iki eşiğe karşı birden raporlanacak**; karar ancak sonuç `0,880 ≤ A1 < 0,888` aralığına düşerse bağlayıcı olur.

### CP2 — 🔴 PİLOT DURDURDU: hasadın kabul ölçütü yanlış tarafı seçiyor

**Önce temiz olanlar:** sızıntı **yok** (DEV kesişimi 0, CANON kesişimi 0) · protokol sapması yok (ikinci bir üretim gövdesi yazılmadı) · üretim sağlıklı (120/120, kesik 0, boş 0, **11,12 s/üretim**).
**Ön-kayıtlı ölçütün verdiği sayı:** M2-tipi 36/120 = **0,300** · M2b-tipi 25/120 = 0,208.
**🚨 Ama kabul edilenler denetlenince** (M2-tipi n=36): geçersiz tuzak **15 (%42)** · geçerli tuzaklarda LLM hakemi **ABSTAIN 15/21 (0,714)** · gerçek fabrikasyon **6/21 (0,286)** ⇒ **gerçek verim 6/120 = %5,0, ölçütün bildirdiğinin altıda biri.**
**M2b-tipi (n=25) — sonuç NİTELİKSEL, sayı olarak okunmaz:** hakem **24'ünü "geçersiz"** saydı. İki okuma ve bu koşu **ikisini ayıramaz**: **(a) seçim etkisi** (denetlenen küme tanım gereği *modelin cevapladığı* örnekler) · **(b) gerçek yapı sorunu** (`--no-gold` bağlamı **cevaplanamaz olmayabiliyor**; distractor'lar aynı kanundan ve komşu maddeler soruyu fiilen cevaplıyor olabilir) ⇒ *"gold çıkarıldı" ≠ "cevap yok".* **(b) doğruysa bu M2b'nin metrik olarak kendisini ilgilendirir** — ve ADR-0045'in merge onarım eşiği onun üstünde duruyor. *(→ #46'da **çürütüldü**: kirli hakem artefaktıydı, kurgu tabanı 79/80.)*
**İki bağımsız bulaşma kaynağı:** ① **reddedip açıklayan cevaplar** (regex red saymıyor, LLM **ABSTAIN** sayıyor — tuzak 2.5; CP0.9'da aynı fark base M2'de **20 puan** ölçülmüştü, *sinyal ortadaydı, hasat ölçütüne bağlanmamıştı*) ② **geçersiz tuzaklar**.
**Kaçışın anatomisi — regex'i genişletmek ÇÖZMEZ.** 15 kaçak elle ayrıştırıldı: **(a) morfolojik boşluk 10/15** (`bilgi vermemektedir` · `yer verilmemiştir` · `içermediği için`) ✅ kapanır — *`REJECT_RE` yüzey biçimlerini tek tek sayıyor ama Türkçe eklemeli; desen her genişletildiğinde bir sonraki eki kaçırır — bu bir kalibrasyon eksiği değil **yöntem sınırı*** · **(b) leksik işaretsiz 5/15** ❌ **hiçbir desenle kapanmaz** — *çekinme sözcükte değil anlamda.*
> 🔴 **Neden bu "yavaş" değil, YANLIŞ.** Havuzun %71'i **doğru çekinme** örneğiyken `τ_a` eğitimi modele **çekinmeyi cezalandırmayı** öğretir — kolun var oluş amacının tam tersi. **Ve hiçbir aşamada hata vermez:** eğitim koşar, loss düşer, adaptör yazılır.

**Çevrimdışı tuzak filtresi ÇALIŞMIYOR — ölçüldü, elendi.** `ov_gold` yönü doğru ama ayrım zayıf: eşiği %42 → %30'a indirmek geçerli tuzakların **%24'ünü** kurban ediyor, net verim **%5,0 → ~%6,0**. `judge_flag` bu ayrımda **tamamen bilgisiz**.
> **Düzeltme:** bu ölçümden önce filtrenin verimi %5 → %8,6 yapacağı **tahmin edilmişti — yanlıştı**; o tahmin filtrenin **kusursuz ayırdığını** varsayıyordu.

**Yapısal sınır:** `1.495 ÷ 0,050 = 29.900 üretim ≈ 92 saat`, havuzda **19.284** kalem var ⇒ **29.900 > 19.284**. *Sorun zamanlama değil yapısal: mevcut havuz bu verimle hedeflenen negatif sayısını **üretemez**.*
⚠️ **Kod borcu (düzeltildi):** `cp2_harvest.py` `context_shown`'u saklamıyordu — ***denetlenemeyen bir eğitim örneği, ölçülemeyen bir sayıdır.***

---

<a id="45"></a>
## #45 — CP2-a: ön-eleme uyum kapısı · ve `valid_trap` öznenin cevabına bakıyor

**2026-07-30 · GPU yok · $0,122** · → [ADR-0048](../adr/kararlar-0045-0063.md#adr-0048)
Ortak değişmezler: seed **3407** · trap_clip **900** · n **36**.

**Kapı net sonuç vermedi ve altındaki zemini çürüttü. Üretim ön-elemesi başlatılmadı.**

**1) Kapı: ön-eleme güvenli ama zayıf.** uyum **0,778** · κ **0,505** · ön-eleme kaçırdı 8 · **geçerliyi kesti 0** ⇒ **FN=0**, *bedeli sıfır*. Ama 15 geçersizin yalnız 7'sini yakalıyor; verim %5 → **%6,2** (*#44'ün "%42 kalkar, %8,6 olur" tahmini **yüksekti***).
**2) Ayrışan 8 vakada hakem KENDİ GEREKÇESİYLE ÇELİŞİYOR.** 3'ünde denetim hakeminin serbest-metin gerekçesi etiketinin **tersini** söylüyor:
```
id=13937  soru     : Mirasçı olamayan kimlerdir?
          ön-eleme : "Kaynak metin … belirtmiyor"        → geçerli tuzak
          denetim  : "Verilen kaynakta … belirtilmemiştir" → etiket: GEÇERSİZ
```
*Aynı cümle, zıt etiket.* ⇒ **"%42 geçersiz tuzak" — ADR-0046'nın premisi — tek bir n=36 `gpt-4o-mini` koşusundan geliyor ve o hakem bu eksende kendisiyle tutarlı değil.**

**3) Tie-break: çapalanma ölçüldü ve HAKEME ÖZGÜ** (2×2, tek değişkenli):

| hakem | cevabı görüyor mu | geçerli tuzak |
| :--- | :-: | ---: |
| `gpt-4o-mini` | ❌ | 29/36 = **80,6%** |
| `gpt-4o-mini` | ✅ | 21/36 = **58,3%** |
| `gpt-4o` | ❌ | 33/36 = **91,7%** |
| `gpt-4o` | ✅ | 30/36 = **83,3%** |

**Cevabı görmek mini'yi 22,3 puan, `gpt-4o`'yu 8,4 puan kaydırıyor** ⇒ çapalanma gerçek ama büyük ölçüde **küçük hakeme özgü bir zayıflık** (`gpt-4o` iki kip arasında **%86,1** aynı kararı veriyor). κ(4o kör ↔ mini görür) = **0,097** — neredeyse sıfır uyum. **Bu ayrışmada zayıf halka ön-eleme değil, referansın kendisi.**
**Ön-eleme, güçlü hakem referans alındığında NET ZARARLI:** kestiği 7 kalemin isabeti `gpt-4o`-kör referansında **0,14 (1/7)**, boşa atılan geçerli tuzak **6**. Havuz da korkulandan çok temiz: geçersiz oranı %42 değil **%8,3-16,7**. ⇒ **Karar: üretim ön-elemesi KOŞULMUYOR.**

**4) ⭐ Asıl bulgu: `valid_trap` KALEMİN DEĞİL, ÖZNENİN özelliği olmuş.** İç kontrol (hakem karşılaştırması gerektirmeyen kanıt) — M3, üç özne, **id kümeleri birebir aynı**: base **54** · gem **56** · `τ_g` **39** ⇒ aynı 80 kalemin **19'unda etiket özneye göre değişiyor.**
**Ve M3'te doğru cevap tanım gereği biliniyor:** `--empty-context` altında bağlam `"(İlgili kaynak bulunamadı.)"` — kaynak metni **yok** ⇒ `valid_trap` **80/80 olmalıydı.** Ölçülen 54/56/39 ⇒ **bu etiket M3'te sadece gürültülü değil, tanımsal olarak yanlış.**
Sistematik: `valid_trap=False` etiketli **172** kalemin **37'sinde (%22)** gerekçe *"kaynak bu bilgiyi vermiyor"* diyor.

**Metriğe etkisi — payda özneye göre kayıyor, hem de tek yönde değil** (`RED` raporlanan ↔ filtresiz): m2b **gem +0,150** ↔ `τ_g` +0,082 ⇒ `gem`↔`τ_g` açığı 0,325 iken **0,393** raporlanmış (**aleyhimize 7 puan**); m3 `τ_g` **+0,123** ↔ base/gem +0,000 ⇒ açık 0,200 iken **0,077** raporlanmış (**lehimize 12 puan**).
⇒ ***Sapma tek yönlü bir bias değil, yön değiştiren gürültü*** — ön-kayıtlı bir karar kuralı için daha kötüsü, çünkü **kapının hangi tarafa kaydığı önceden bilinemez.**
> 🚨 **DAMGA 2026-08-06 (Ö3):** bu tablonun **her iki sütunu da emekli birimde.** Bulgu tam olarak doğrulandı ve **iki ayrı onarımla** kapatıldı (**ᴷ³** payda cevaba **kör**, [#57](kronoloji-53-62.md#57) · **ᴷ⁴** `m2` paydası **66**'ya eşitlendi, [#59](kronoloji-53-62.md#59)). Yürürlükteki: m2 base **0,803** · gem **0,848** · `τ_g` **0,833** (payda 66) · m2b **0,961** / **0,883** / **0,506** (payda 77). *"Filtresiz" sütunu bir **karşıolgudur**, yürürlükteki ölçüm değil.*

**Etkilenen kayıtlar:** **22 çekinme koşusunun 21'i** cevabı gören kipte puanlandı. **Doğrudan düzelen:** M3 → base **1,000** · gem **1,000** · `τ_g` **0,800** (#43'te 0,923 yazılmıştı — **çelişki iki yerde işaretlendi**).

**Ders.** ***Hakemin ürettiği bir filtre etiketi, özne başına yeniden yargılanırsa metriğin paydasını sessizce özneye bağlar.*** Hata vermez, dosyalar dolu görünür, oranlar makul çıkar ⇒ **bir kez, cevaba kör, kalem düzeyinde** hesaplanıp önbelleğe alınmalı.
**İkinci ders:** **küçük hakem, yargısını gördüğü cevaba çapalıyor** (22,3 p ↔ 8,4 p). Dört katmanlı savunma *"hakem cevabı görüyor mu"* eksenini **kapsamıyordu** — yeni eksen.
**Yeni tuzaklar.** **2.14** özne başına yeniden yargılanan filtre etiketi (kontrol: aynı id kümesinde `len({...})==1` olmalı) · **2.15** tanım gereği bilinen etiketi hakeme sorma · **4.8 güncellendi**.
⚠️ **Bu olgu tamamen yeni değil:** tuzak **2.6** paydanın kaydığını **zaten kaydetmişti**, ama korunması *"oranı paydayla yaz"*dı — **kirliliği görünür kılmak, gidermek değil.** #45'in kattığı üç şey: **nedeni** · **tanımsal kanıt** · **yönü**. 2.6 **yetersiz** işaretlendi.

---

<a id="46"></a>
## #46 — CP2-r: cevaba kör payda · üç eşik türetildi · düzeltme 6 kıyasın 4'ünde aleyhimize

**2026-07-30 · GPU yok · $0,2298** · Girdi: CP0.9'un mevcut dosyaları — **hiçbir hedef model çağrılmadı**

> 🚨 **DAMGA 2026-08-06 (kusur K-3) — bu girişin kör payda sayıları EMEKLİ BİR ALETİN sayılarıdır. Silinmedi, ama yürürlükte değil.**
> **Sebep ölçüldü — 900 bir KATEGORİ HATASIYDI.** ADR-0011'in 900'ü `gen_eval_grounded`'ın **her `[KAYNAK]` parçasına AYRI** uyguladığı üretim-zamanı klipi; `context_shown` ise zaten kırpılmış parçaların **BİRLEŞİMİ**. Bu tur o **parça sabitini birleşime** uyguladı. cp09 m2b'de (n=80): tam metinde **320** kaynak · klip 900 ile hakem **147**'sini görüyor (**%46**) · klip 3500 ile **320**'sini (**%100**) ⇒ **bu girişin kör paydası bağlamın yarısından karar vermiş.**
> **Ayakta kalanlar:** (a) paydanın cevaba **kör** olması hükmü (b) M3'ün **80/80** tanımı (c) m2b kurgu tabanının geçildiği (79/80 ↔ yürürlükteki 77/80, **ikisi de ≫ 40**).
> ⛔ Bu girişteki **eşikler de emekli**: ARA KAPI 2. gözlemi 2026-08-06'da yeniden türetildi ve **hükmü değişti**.

**Ön koşul doğrulandı:** eval bağlamı üç modda da özneler arası **bit-birebir aynı** (m2 70/70 · m2b 80/80 · m3 80/80) → `id` anahtarlı önbellek meşru; betik bunu her koşuda yeniden doğrular ve **ayrışmada durur.**
**Maliyet neden bu kadar düşük:** `verdict` yeniden hesaplanmadı — *o **cevap hakkındadır**, cevaba bağlılığı meşrudur* ⇒ düzeltme = önbellek ($0,23) + **saf aritmetik ($0)**. M3 hakeme **hiç gitmedi**.

**1) Payda her modda yukarı çıktı.** m2 `55/57/59 → **66/70**` · m2b `61/65/72 → **79/80**` · m3 `39/54/56 → **80/80**` *(tanım, hakem yok)*. **Kirli hakem geçerli tuzakları sistematik olarak geçersiz sayıyordu.**
**2) ⭐ M2b kurgu tabanı fena hâlde geçildi — ve bir bulgu çürüdü.** Ön-kayıtlı taban **40/80**, ölçülen **79/80** ⇒ merge onarım kontrolü ARA KAPI'nın 2. gözlemi olarak **kalır**. Bu, pilottaki *"25 adayın 24'ü geçersiz"* bulgusunu **çürütüyor — o da kirli hakem artefaktıydı.** ⚠️ Şerh: pilot **havuz** kalemlerinde, bu ölçüm **DEV** kalemlerinde.
**3) Üç eşik türetildi — hareket tahminden çok küçük.** `τ_a` tekil M2 Rej ≥ 0.934 → **0.923** (`base 0.803 + 0.12`) · merge M2b ≥ 0.887 → **0.8541** (`base 0.949 × 0.90`) · muhafız M1 A1 ≥ 0.888 → **0.8799**. *Tahmin ~0,91'di; gerçek 0,923 — yalnız **1,1 puan** kolaylaşma.* Ve açık bırakılan soru kapandı: muhafız **0,880** (kayma `valid_trap`'ten **bağımsız** — CP1'in istem değişikliğinden).

**4) ⭐⭐ Düzeltme TEK YÖNLÜ DEĞİL — 6 karşılaştırmanın 4'ü aleyhimize.**

| karşılaştırma | eski açık | yeni açık | kayma | kim lehine |
| :--- | --: | --: | --: | :--- |
| m3 base − `τ_g` | 0,077 | **0,200** | **+0,123** | 🔴 aleyhimize |
| m3 Gemini − `τ_g` | 0,077 | **0,200** | **+0,123** | 🔴 aleyhimize |
| m2b base − `τ_g` | 0,379 | **0,430** | **+0,051** | 🔴 aleyhimize |
| m2 base − `τ_g` | −0,059 | −0,030 | **+0,029** | 🔴 aleyhimize |
| m2b Gemini − `τ_g` | 0,393 | 0,342 | −0,051 | 🟢 lehimize |
| m2 Gemini − `τ_g` | 0,057 | 0,015 | −0,042 | 🟢 lehimize |

**En çok kayan özne RAKİP:** Gemini M2 **−0,082**, M2b **−0,139** — *kirli paydadan en çok o yararlanıyordu* (M2b'de 1.000 raporlanmıştı, gerçek **0,861**).
> 🚨 **DAMGA 2026-08-06 (Ö3):** bu tablonun **sağ tarafı da emekli** (klip 900 aleti K-3'te **kategori hatası** olarak çürüdü). Yürürlükteki: `m2` **0,803 / 0,848 / 0,833** payda **66** *(ᴷ⁴ — **iki alet aynı hükümde birleşti**)* · `m2b` **0,961 / 0,883 / 0,506** payda **77** (ᴷ³). ⭐ *900 klipinin zararı yalnız **birleştirilmiş çok-kaynaklı** bağlamda (`m2b`, `h2b`) doğuyor.*

**5) `τ_g` hakkında yeni gerçek: açık raporlanandan BÜYÜK.** M2b 0,607 → **0,519**, base'e açık 0,379 → **0,430** ⇒ *`τ_a`'nın hedefi daha da acil.* M3 0,923 → **0,800**.

**Ders.** ***Bir ölçüm hatası düzeltildiğinde yönünü önceden bilmek mümkün değil — ve tam bu yüzden düzeltme sonucu görmeden yapılmalı.*** Burada eşik **lehimize 1,1 puan** kaydı ama `τ_g`'nin karşılaştırmalı açıkları **dört yerde büyüdü**; net etki **aleyhimize.** *Aynı düzeltme sonuç görüldükten sonra yapılsaydı hangi yöne çekildiği asla ayrıştırılamazdı.*
**İkinci ders:** ***kirli bir payda en çok, o paydada en iyi görünen özneyi kayırır.*** Rakip lehine sapma, kendi lehimize sapmadan **daha tehlikeliydi** çünkü parite iddiasını **sessizce zorlaştırıyordu.**
**Etkilenmeyen / bilinçli dokunulmayan:** `sprint1-thinking-off/` ve `cp09-ab-ayrimi/` **düzeltilmedi** — thinking-off canlı rejim değil, **tarihsel kayıt olarak kalıyor.**

---

<a id="47"></a>
## #47 — CP2-s: boru hattı smoke'u, yazılmamış bir kodu buldu · TIES'te işaret hatası

**2026-07-30 · Modal ~$0,20 · Hakem $0** · [ADR-0049](../adr/kararlar-0045-0063.md#adr-0049) m.4
> 🚨 **Bu turun hiçbir sayısı performans çıpası DEĞİLDİR.** Smoke kasten *mekanik* tanımlandı: ölçtüğü **"çalışıyor mu"**, *"iyi mi"* değil. *Okunabilir bir performans sayısı üretmemesi **tasarım gereğidir** — eşikler yeniden türetilmişken böyle bir sayı çıpalama riski taşır.*

**⭐ Asıl bulgu: ikinci halka HİÇ YOKTU.** `merge_lora.py` **tek** adaptörü katıyor; **norm-dengeli k-yollu TIES yazılmamıştı.** ⇒ *Sprint 3'ün kafesi ve ARA KAPI'nın merge onarım kontrolü **var olmayan bir koda** dayanıyordu — ve bu, `τ_a` eğitilip ~$4 harcandıktan sonra fark edilecekti.*
`merge_ties.py` yazıldı: **eşzamanlı k-yollu** (kırp → işaret seç → ayrık ortalama, hepsi k vektörün tamamı üzerinde **bir kerede**) · ΔW **bf16**, **tam ağırlık uzayında** · **ana RAM'de tensör tensör akıtmalı, asla GPU'da** · `‖τ‖_F` **koşulsuz** ölçülür · **iki sessiz-bozulma kapısı** (kolların LoRA hedefleri ayrışırsa DUR · eksik uygulama varsa DUR).

**Operatörün doğrulanması — biri BAŞARISIZ çıktı** (sentetik tensörler, seed 3407, **$0**):

| # | özellik | sonuç |
| :-- | :--- | :--- |
| 1 | `TIES(τ,τ)` ≈ kırpılmış τ | ✅ sıfırdışı **0,199** (beklenen 0,20) · max sapma bf16 yuvarlaması |
| 2 | `TIES(τ,−τ) = 0` | ❌ → ✅ **hata bulundu ve düzeltildi** |
| 3 | norm-dengeleme küçük kolu kurtarıyor | ✅ **0,656 → 0,734** |
| 4 | eşzamanlı ≠ iteratif | ✅ max fark **2,9766** |

**2. testin anatomisi — gerçek bir tasarım hatası.** İşaret toplamı **tam sıfır** olduğunda keyfî `sign=+1` atanıyordu ⇒ tam çakışan kollarda birbirini götürmesi gereken parametrelerde **sıfır yerine `|τ|`** = **sistematik pozitif sapma** (`|ortalama| = 1,023`). Düzeltme: seçilmiş işaret yoksa **güncelleme de yok**.
> *Gerçek delta'larda tam eşitlik pratikte olmaz — ama **keyfî bir kırılımın sapması ölçülemez, sıfırın sapması ölçülebilir.** Bu yüzden düzeltildi, "nadir" diye bırakılmadı.*

**3. test, ADR-0036'yı teoriden çıkarıp koda soktu:** norm-dengeleme küçük kolun işaretini izleme oranını **0,656 → 0,734** çıkarıyor.
**Zincirin diğer üç halkası ✅:** `τ_a` eğitimi (Modal A100, 50 adım, **29.908.992 / 4.569.174.528 = %0,65**, 11 modül) · GGUF (f16 8,07 → **Q4_K_M 2,59 GiB**, 63 s) · servis (**3/3 istek dolu cevap**).

**Norm değerleri + çapraz doğrulama.** `‖τ_tg‖_F = 10.472179` ↔ kayıtlı artefakt **10.458926** — **%0,13 fark = bf16'da ΔW materyalize etmekten** ⇒ ***norm ölçümü BAĞIMSIZ olarak doğrulandı.*** Merge: `trim_k=0,20` · geri ölçek 5,526 · çatışan parametre **%0,16** · sıfır kalan **%67,3**.
> ⚠️ **Bir tahmin, CP3'te ölçülecek.** Çatışma oranı **%0,16** düşük çıktı çünkü sentetik kol `τ_g`'nin ölçeklenmiş kopyası (yüksek korelasyon). **Gerçek `τ_g` ↔ `τ_a` çatışma oranı çok daha yüksek olmalı ve ADR-0036'nın asıl merak ettiği sayı O.** Norm asimetrisi de: sentetikte **18×**, gerçekte `adım × lr` kabası **~148×**.

**İki yeni yürütme tuzağı — ikisi de "hata vermeden yanlış/hiç sonuç".**
**6.1 — `modal run` efemer app + `spawn()` = iş HİÇ KOŞMAZ.** Terminal *"✓ App completed"* yazdı, log yalnızca *"Stopping app"* içeriyordu: **hiçbir iş başlamamıştı, hata da yoktu.** `--detach` **zorunlu**; *"spawned" mesajı iş koştuğunu **kanıtlamaz**.*
**6.2 — Veri kapısı model yüklemeden ÖNCE olmalı.** `train_sft.py` doğru yapıyordu, `train_orpo.py` yapmıyordu (boşa giden GPU ≈ $0,10).

**🔴 Yan bulgu: eğitim hızı kayıtlının 10 katı yavaş — CP3 bütçesi değişti.** Smoke medyanı ~**70 s/it** ↔ kayıtlı **6,8-7,0**.
> ⚠️ **DÜZELTME (2026-08-02, [#48](#48)):** *"kayıtlı 7 s/it yanlıştı"* ifadesi **iki farklı rejimi** kıyaslıyor. **Yanlış olan kayıt değil, kıyas:** 6,8-7,0 = **SFT, efektif batch 16** ↔ ~70 = **ORPO, efektif batch 64**. ⇒ **SFT tahminleri AYAKTA**; yalnız ORPO kalemleri ~**4×** pahalılaştı.

CP3 ~73 adım: ~9 dk/$0,85 → **~85 dk/~$3,2**. Smoke **6/50 adımda durduruldu** (~$0,35): *mekanik soru zaten cevaplanmıştı — model yüklendi, LoRA doğru uygulandı, veri okundu, ORPO kaybı hesaplandı, optimizer adım attı; **50. adıma gitmek hiçbir mekanik bilgi eklemiyordu.***
**Bütçe etkisi:** Modal'da kalan $7,27; yeni toplam **$6,55** ⇒ sığıyor ama **payı $0,7'ye** düşürüyor — *bu pay, ilk 10 dakika kapısı tetiklenirse yeniden koşmaya **yetmez**.*

**🔴 Yerel hasat ölçüldü ve ELENDİ.** seri **11,12** ↔ `-np 8` **8,23 s/üretim = 1,35×** (beklenen 4-6×).
**Sebep ölçüldü: zorunlu kapatma 9/9.** Her "üretim" **iki istek**; ikincisi **3.933 karakterlik izi baştan prefill ediyor** ve prefill compute-bound, slotlar arası **iyi ölçeklenmiyor**. Düzeltilebilir bir kusur **değil** (base'in `</think>`'i kapatmaması #42'de ölçülmüş bir özellik, zorunlu kapatma **rejim değişmezi**). Üretim başına ~2.150 token, verim **~260 token/s**.
Yerelde **750 hedef = 17,1 saat** ⇒ **yerel hasat elendi**, ADR-0047 m.2 **doğrulandı**.

**Ders.** ***Bir smoke'un işi çalışan şeyi doğrulamak değil, olmayan şeyi bulmaktır.*** Bu tur dört halkanın üçünü doğruladı ve **birinin hiç var olmadığını** ortaya çıkardı — üstelik o halka **Sprint 3'ün tamamının ve bir ön-kayıtlı kapının dayanağıydı.** Maliyeti **$0,20 ve 25 dakika**.
**İkinci ders:** ***operatörün matematiksel özellikleri sınanabilir ve sınanmalı*** — `TIES(τ,−τ)=0` gibi bir özellik, gerçek ağırlıklarda **asla fark edilmeyecek** bir işaret hatasını üç satırda yakaladı, **çünkü gerçek ağırlıklarda çıktı *makul görünür*.**

---

<a id="48"></a>
## #48 — CP2-c: Modal köprüsü · `τ_a` eğitildi · merge süpürmesi · ADR-0036 tersine döndü

**2026-08-02 → 08-03** · Yazılan: `modal_train.py::harvest_cp2` + `spawn_cp2c` · ⭐ `cp2c_kabul.sh` · ⭐ `merge_ties.py` · `cp2c_birlestir.py`
> ⚠️ Başlıktaki *"`-np` ölçeklemesi çalışmadı"* ibaresi **aynı gün çürüdü**; sabahki bölümler **değiştirilmedi** (kayıt = o anki bilgi durumu).
> 🚨 **DOSYA ÇAPINDA BİRİM DAMGASI 2026-08-06 (kusur Ö3-c) — buradaki HER `M2 Rej` ve `M2b Rej` EMEKLİ BİRİMDEDİR.** Hiçbiri silinmedi; çeviri:
> ```
> özne             M2 Rej (emekli → 66)   M2b Rej (emekli → 77)
> base                0,814 → 0,803          0,986 → 0,961
> Gemini 3.1 FL       0,930 → 0,848          1,000 → 0,883
> τ_g v1              0,873 → 0,833          0,607 → 0,506
> τ_a v1              0,984 → 0,955          0,987 → 0,987  (değişmedi)
> MERGE min           0,934 → 0,909          0,987 → 0,987  (değişmedi)
> MERGE ham (tgta_v1) 0,893 → 0,833          0,877 → 0,766
> ```
> **Türetilen oran/fark da damgalıdır** (turun kendi kuralı): merge onarım oranı ~~%71~~ → **%57** · merge'in M2'ye katkısı ~~+0,020~~ → **+0,000** · ARA KAPI 2. gözlem ✅ → **🔴**. A1 · M1 kütle · aşırı-red · token sütunları **etkilenmedi**. ⭐ Yürürlükteki çıpa tek yerde: [`kollar.md`](kollar.md).

### Köprüler — dördü de eksikti, dördü de "GPU parası yandıktan sonra" sınıfı

**① `modal_train.py` CP2'yi hiç tanımıyordu** (mevcut `harvest_rejected` **eski** betiği çağırıyor). Yazıldı: `harvest_cp2` + `spawn_cp2c` (`spawn()` + `--detach`).
**Taşıyıcı künyesi — ADR-0047 m.2 birebir:** `ghcr.io/ggml-org/llama.cpp:server-cuda` 10223 · `q35-4b-q4_k_m.gguf` **sha256 214826aa…** · `-fa on · KV q8_0 · --no-context-shift` · ctx 8192/slot. **vLLM/bf16 kullanılmadı.**
**Üç kırılma:** hazır imajın `ENTRYPOINT`'i (`.entrypoint([])`; belirti: konteyner saniyeler içinde ölür, **GPU logu hiç açılmaz**) · `requirements.lock.txt` bir **eğitim** lock'u (`openai` yok → `ModuleNotFoundError`, **GPU ayrıldıktan sonra**) · **öbekli istemci slotları boş bekletiyordu** (iş **10.220** slot-sn ↔ kapasite **14.496** ⇒ doluluk **%70**) → sürekli besleme; *gönderilen istek, sıra, seed ve örnekleme **aynı** — değişen yalnız zamanlama.*
**② kabul zincirinin sürücüsü yoktu** → `cp2c_kabul.sh`. **③ m2b için `chosen` tarafı yok** (§7). **④ `--skip-first` Modal tarafına hiç geçmemişti** (§12).
> **Genel ders (üç kez tekrarlandı, artık kalıp):** *bir bayrak **script'e** eklendiğinde iş bitmiyor; **çağrı zinciri uçtan uca izlenmeden** ekleme tamamlanmış sayılmaz.* Üçü de aynı sessiz-yanlışlık sınıfı.

**Hız ölçümleri.** smoke m2 `-np 32` öbekli: kümülatif **3,65** · **smoke2** `-np 32` **sürekli**: **1,98** (marjinal 1,58) ⇒ **sürekli besleme kazancı 1,84×** · np64 sürekli: 2,93 (marjinal 2,09).
**🔴 Sabahki negatif bulgu — ve nasıl çürüdü.** *"Slot sayısını ikiye katlamak %32 kötüleştirdi"* denmişti; **iki ayrı hatanın toplamıydı**: (a) **kart karıştırıcısı** — Modal'ın `gpu="A100"` takma adı hem 40GB hem 80GB verebiliyor, bant genişliği oranı **1,31×**, gözlenen fark **1,32×** (tuzak **6.7**) · (b) **kümülatif ortalamanın yanlılığı** (tuzak 6.8). Künyeye `gpu_gercek` eklendikten sonra **aynı kartta**: `-np 32` m2 ~**2,4** ↔ `-np 64` m2 ~**2,09** ⇒ **slot artışı YARDIM EDİYOR.**
> **Ders:** ***künye disiplini geriye dönük ödüyor*** — `gpu_gercek` sabah bir negatif bulgu **okunamaz hâle geldiği için** eklenmişti; öğleden sonra aynı alan o bulgunun karıştırıcısını **çözdü**.

### ⭐ Verim kapısı olayı — büyüklük ↔ tahmin edici ayrımı ([ADR-0050](../adr/kararlar-0045-0063.md#adr-0050))

Kapı **iki tipte de** tetiklendi (m2 `DURDU: 2,97 > 2,88` · m2b `2,95 > 2,88`) ve **doğru çalıştı** — *sorun kapının varlığında ya da eşiğinde değil, **ölçme aletindeydi**.* Marjinal hız pencere pencere: `0→25` **5,70** (açılış dalgası) · `100→200` **2,38** (gerçek kararlı) · `200→225` 2,90 (kapı sonrası **boşalma**).
> 🔍 **Doğrudan kanıt — kapının kendi logu kendini çürütüyor:** kapı **600. saniyede** `2,97` ile durdurdu, **aynı koşu 673. saniyede zaten `2,89`'daydı** ⇒ *ölçülen büyüklük kararlı hâline doğru **hâlâ inerken** karar verilmişti.*

**Karar (insan): şık A — eşiğe dokunulmadı, tahmin edici düzeltildi.** ❌ **B (eşiği 3,2'ye gevşetmek):** *sonucu gördükten sonra ön-kayıtlı bir eşiği oynatmak, ön-kayıt kurumunun kendisini geçersiz kılar; bu hattın dersi ters yöndeydi — kapı ölçemez hâle gelince **kapı bölünür**.* ❌ **C (negatif bulgu olarak kapatmak):** *ölçüm aracının yanlılığını "sonuç" diye kaydetmek, kayda geçen sayıyı **kalıcı olarak yanlış** yapar.*
**İkinci kusur:** kapı `--limit` kontrolüne takılıp **hiç değerlendirilmeden atlanabiliyordu** ⇒ huniye **hak edilmemiş "geçildi"** damgası. Artık `limit`ten **önce** değerlendiriliyor.
> ⚠️ **AÇIK OLAY — iki detached iş aynı anda koşuyor ve aynı dosyaya yazıyor.** Çözüm 17:05'te; **seçim ölçütü ilerlemedir, başlangıç saati değil** (durdurulan iş ~200 üretim geride ⇒ tutmak **yanmış GPU'yu bir kez daha yakmak** olurdu). Bedel ~$0,8. Kalıcı iz endişesi (§5) **gerçekleşmedi** — ne yinelenen id ne yarım satır; *yine de onarım adımı boşa değil: iki dizin arasındaki **82 gerçek çakışmayı** o yakaladı.*

### ✅ Hasat kapandı — 728 temiz negatif, hedefin %97'si

1. tur (3,4 sa): m2 3.813 denendi → **1.205** kabul (%31,6), kararlı **1,43 s/üretim** · m2b → **708** (%18,6), **1,59**. **Tahmin tam isabet** (ADR-0047 m.3 tahmini 1,44 ↔ fiili 1,43).
Ek tur (3,15 sa, `--skip-first 3813`): m2 **1.192** (%31,3) · m2b **731** (%19,2). **⭐ `--skip-first` DOĞRULANDI — sıfır çakışma:** ek turun **1.923 kaydının tamamı yeni**; birleşim **3.867 tekil**, yarım satır 0.

```
        regex  →  mini        →  teyit        →  kör damga
1. tur  1944     735            385             362    $5,11
ek tur  1923     727            398             366    $2,86
                                       TOPLAM   728    $7,97
```

**⚠️ Nerede kaybettik — huni ADR-0049'un varsaydığından İKİ KAT dar.** temiz/regex adayı: m2 **%22,2** · m2b **%12,5**; **temiz/ÜRETİM** (kapasite planlaması için **tek doğru sayı**): m2 **%7,13** · m2b **%2,36**.
Ayrışmanın kaynağı teyit katmanının **geçersiz** alt kümedeki davranışı: geçerli tuzaklarda iki mod da **~%87** (tutarlı); geçersizde m2 **%38** ↔ m2b **%4**.
**⭐ ADR-0048 LEHİNE KANIT — teyit ile kör damga güçlü örtüşüyor.** Havuz geneli geçerlilik m2 **%82,5** / m2b **%79,5** ↔ **teyitten geçmiş uydurmalarda** m2 **%92,2** / m2b **%100** ⇒ *"bu cevap uydurma" (cevaba bakan) ile "bu tuzak geçerli" (cevaba kör) **bağımsız değil, uyumlu*** — iki bağımsız ölçümün aynı yöne bakması damganın **gürültü değil sinyal** ölçtüğünü gösteriyor. ⚠️ **Karşı okuma kayda geçsin:** örtüşme **aynı hakem ailesinin** iki çağrısı arasında ölçüldü — *öz-tutarlılık ile doğruluk burada ayrıştırılamaz.*
> **Planlama dersi: kapasite planı `regex kabul` üzerinden YAPILAMAZ.** 1.944 aday *"hedefin %26 altındayız"* gibi görünüyordu; gerçek **362 = hedefin %52 altı**. *Aday sayısı hakem huninin **girdisidir**, çıktısı değil; planlama birimi **temiz negatif / üretim** olmalı.* ⇒ ADR-0047'nin *"koş, verimi ölç"* kararı doğru çıktı — **ama ölçülmesi gereken hasat verimi değil, zincir sonu verimiymiş.**

**Ek tur — insan kararı A.** ❌ **B (362 ile devam):** 362 → **35 adım**, ADR-0047'nin reddettiği 29-adım bölgesine bitişik ⇒ *`τ_a` öğrenmezse CP3 ölçülemez olur.* ❌ **C (`grad-accum` 64→32):** bedava, ama efektif batch yarıya iner ⇒ ***"kollar aynı reçeteyle eğitildi" iddiası düşer.***
**OpenAI kredisi tükendi → kapı OpenRouter'a alındı.** Yanan para **$0** (ilk hakem çağrısında düşüldü). ⚠️ **Sessiz sapma çıktı:** `LLM_GATEWAY=openrouter` ile `gpt-4o` → sağlayıcı **Azure** (1. tur OpenAI'ydi); pin mekanizması **kodda zaten vardı, yalnız kullanılmamıştı** → ek tur **pinli** koştu. *Değişen faturalama yolu; küratörlük etiketi olduğu için risk sınırlı, ama huni oranları kıyaslanırken **anılmalıdır**.*
**💰 Kör damga daraltıldı — ölçülen bir israf kesildi:** teyitten düşen kalemin kör damgası **hiçbir yerde kullanılmıyordu**; 1. turda **1.944 damga, gereken 385** ⇒ $2,85'in ~**$2,25'i boşa**. `--sadece-teyit` eklendi; ek turda damga **398** kaleme koştu (**$0,570** ↔ $2,849). **Kaybedilen bilgi künyeye yazıldı** (`sadece_teyitten_gecenler`) *ki oranın **neden yok** olduğu sonradan cevapsız kalmasın.*
**İki turun huni oranları örtüşüyor** (m2 mini %35,1 ↔ %33,6 · m2b %42,5 ↔ %44,6) ⇒ **kapı değişikliği sayıyı kaydırmadı.**
**🔴 Bir tuzak daha:** `sprint2.md`'de aylardır *"ateşe hazır"* duran CP3 komutu **yerel yol** kullanıyordu, `train_orpo` **konteyner yolu** bekliyor. ***Ders: "hazır komut" bloğu, koşulmadığı sürece doğrulanmamış koddur; belgede durması onu sınanmış yapmaz.***

### ✅ CP3 · 3a — `τ_abstention` eğitildi (36,5 dk)

845 train / 26 validation · 5 epoch · lr 1e-5 · beta 0.1 · grad-accum 64 · `--fresh-adapter --bf16-base` · **70 adım** (ön-kayıtlı ~73'ün %96'sı) · **29.908.992 / 4.569.174.528 = %0,65** (ön-kayıtlı sayı **birebir**).
**⛔ Kapı log satırından değil ARTEFAKTTAN kuruldu** (`modal app logs` kayan pencere döndürüyor): `τ_g` ↔ `τ_a` tensör **448/448** · parametre **29.908.992** ✅ · r/α/dropout **16/32/0,05** ✅ · target_modules **11** ✅.
> ***Ders: bir kapının ölçütü mümkünse ARTEFAKT olmalı, log satırı değil. Log kaybolur, kayar, tamponlanır; dosya kalır ve tekrar ölçülebilir.***

**⭐⭐ ADR-0036'NIN GEREKÇESİ ÖLÇÜLDÜ — 8,87× norm asimetrisi:** `‖τ_g‖ = 10,4722` (1.083 adım @1e-4) ↔ `‖τ_a‖ = 1,1806` (70 adım @1e-5).
**Eğitim eğrisi — çekinme öğrenilirken cevaplama unutulmadı:** `nll_loss` **2,434 → 1,636** baştan sona düştü (%20 replay'in görevi buydu ve yaptı).
**⚠️ NOT DÜŞÜLECEK BULGU — tercih sıralaması hiç dönmedi.** `rewards/accuracies` 5 epoch boyunca **0,14-0,20** bandında, 0,5'i hiç geçmedi. Marj kapandı (−0,104 → −0,033, %68) ama **işaret değişmedi**. İki okuma, **3c bunları ayırır**: (1) yetersiz eğitim (2) **metrik yanıltıcı** — *ORPO'nun hedeflediği davranış düşük-olasılıklı bir cümleyi **seçmek** değil, uydurmanın olasılığını **bastırmak**; `log_odds_chosen` −1,573 → −0,626 (%60) tam bunu gösteriyor olabilir.* ⚠️ **Ön-kayıt niteliğinde** — sayı görülmeden bu yorum yapılmayacak.

### Üç ön-kayıt, üçü de tuttu

**§17 (üretim sürerken, n=42, hakem koşmadan):** `τ_a` **şablon ezberlemiş görünüyor** — M1'de kaba red işareti **22/42 (%52,4)**, cevap medyanı **58 karakter** = ADR-0051 şablonunun uzunluğu. **Kalıp ezberinin kanıtı:** model şablonu **çekimleyerek** kullanıyor (*"…madde **bulunuyor**"*) ⇒ cümleyi bir *muhakeme sonucu* olarak değil **bir kalıp** olarak öğrenmiş.
**🚨 MUHAFIZIN KENDİSİNDE KUSUR:** muhafız **M1 A1 ≥ 0,880**, ama **A1 = cevaplanan-only makro** ⇒ *model M1'de %52 çekinip kalan %48'i doğru cevaplarsa **A1 yüksek çıkar ve muhafız GEÇER** — oysa kol kullanılamaz hâldedir.* **Sonuç: kapı okumasında A1 tek başına alınmayacak, `coverage` yanında raporlanacak.** ⚠️ *Bu, ön-kayıtlı eşiğin **değiştirilmesi değildir** — eklenen şey, aynı gözlemin **ikinci bir eksende** raporlanması zorunluluğu.*
**Koşu DURDURULMADI** (tuzak 6.8: *ara çıktıya bakıp koşuyu iptal etmek sağlıklı bir koşuyu öldürür ve parayı iki kez yakar*).
**✅ §17 doğrulandı (n=80):** M1 kaba red — base 34 (%42,5) · `τ_g` **2 (%2,5)** · `τ_a` **46 (%57,5)**, medyan cevap **58 karakter** ⇒ ***`τ_a` tek başına grounding'i çıplak base'den bile kötü hâle getirmiş.***
**⭐ Bu, iç iddianın ÖNCÜLÜNÜ doğruluyor — çatışma gerçek.** İki negatif artık **simetrik**: #07 *plain SFT çekinmeyi sıfırladı* ↔ **#48 §17 ORPO çekinme kolu grounding'i base'in altına indirdi.** *`τ_g`'nin aynı modda %2,5'te durması, iki kolun **gerçekten çatıştığını** gösteriyor: bu bir eğitim kusuru değil, **becerilerin birbirini itmesi**.* **Öncül ölçüldü ve doğrulandı.**

### 3c — `τ_a` tekil: iki ölçüt de geçti, kol yine de bozuk

`M2 Rej 0,984 ≥ 0,923` ✅ · `M1 A1 0,9697 ≥ 0,880` ✅ · kesik %1,4 ✅
> 🚨 ᴷ⁴ **BU KIYAS KARIŞIK BİRİMDEYDİ — hüküm AYNI, gerekçesi onarıldı.** `0,984`'ün paydası **özneye bağlıydı** (63/70), eşiğin çıpası ise [#46](#46)'nın **cevaba kör** ölçümünden geliyordu — *iki taraf iki ayrı aletten okunmuş; hata vermez, sayı yanlış çıkar.* Bugün iki taraf da aynı yerden: **0,955 ≥ 0,923** ✅ hüküm **ayakta**.
> 🚨 **BİRİM DÜZELTMESİ (kusur Ö1):** yayımlanan ~~*"marj +18,1 → +3,2 puan"*~~ **iki farklı referans noktasından** okunmuştu. Eşleşen okumalar: **eşiğin üstü** +6,1 → **+3,2 p** (~1,9× daraldı) · **çıpanın üstü** +18,1 → **+15,2 p** (~1,2×). *"Payda onarımı marjı 5,7 kat eritti"* okuması **yanlıştır**; öyle bir kıyas yoktur. **Kusur sınıfı: bir marj yazarken referans noktası cümlede söylenmemiş.**

**🚨 Ama muhafız §17'nin işaret ettiği kör noktaya düştü:**

| özne | cevaplanan | coverage | aşırı-red | A1 | **kütle** |
| :--- | ---: | ---: | ---: | ---: | ---: |
| base | 46/80 | 57,5% | 0,425 | 0,9864 | 56,7% |
| Gemini 3.1 FL | 61/80 | 76,2% | 0,237 | 0,9561 | 72,9% |
| `τ_g` | 66/80 | 82,5% | 0,175 | 0,8658 | 71,4% |
| **`τ_a`** | 34/80 | 42,5% | 0,575 | **0,9697** | **41,2%** ← kütle EN DÜŞÜK, A1 EN YÜKSEK |

***Kapı geçti, kol bozuldu.*** `τ_a`'nın A1'i tüm öznelerin en yükseği — **çünkü yalnız emin olduğunda konuşuyor.** *Tek sayıya bakılsaydı görünmezdi.*
**⭐ §16'nın ön-kaydı da doğrulandı — `rewards/accuracies` yanıltıcıymış.** Ölçüm **(2)'yi seçti**: `accuracies` hiç dönmedi ama davranışsal çekinme **0,803 → 0,984**. ⇒ ***Ders: ORPO'da `rewards/accuracies`, davranışsal çekinmenin vekili DEĞİLDİR.***
**⭐⭐ İki kol da tek başına sakat — iddianın tam kurulduğu yer.** `τ_g` cevaplıyor ama çekinmiyor (kütle 71,4%); `τ_a` çekiniyor ama cevaplamıyor (41,2%). **Hiçbiri tek başına kullanılabilir değil.**
`τ_a` düşünceyi **hiç kendi kapatmıyor** (230/230 zorunlu, ~1084 tok/cevap); `τ_g` kapatıyordu (35/36).

### Merge süpürmesi — üç varyant, DEV'de

**3d — norm-dengeli TIES (k=2).** `‖τ_tg‖ 10,472 → katsayı 0,0955` · `‖τ_ta‖ 1,1806 → 0,8470` · geri ölçek **5,826** = ortalama.
**⭐ TIES istatistikleri — çatışmanın NİCELİĞİ:** çatışan parametre **%2,245** · sıfır kalan **%64,56**. *İki beceri parametre düzeyinde gerçekten çarpışıyor ama **dar bir yüzeyde**; norm dengelenmeseydi bu yüzeyin tamamında `τ_g` kazanırdı.* Modül kırılımı: iki kolun da en büyük normu **aynı MLP yüzeyinde** (`gate_proj` 6,150 ↔ 0,621 · `up_proj` 5,047 ↔ 0,628) ⇒ **çatışma rastgele dağılmıyor, aynı alt-uzayda yoğunlaşıyor.**

**§20 ÖN-KAYIT (sayı görülmeden):** ARA KAPI'nın 2. gözlemi **yalnız M2b'ye** bakar ⇒ *merge M2b'yi geçip M1'de `τ_a` gibi çökerse tablo **"güçlü yeşil → CP4-CP5 koşulur"** der, oysa merge de kullanılamaz hâlde olur ve ~$12 harcanır.* Önlem: 3e'ye **M1 ve M2 de** dahil edildi. ⚠️ *Eşikler DEĞİŞMİYOR — eklenen tek şey ölçümü tamamlamak.*

**🛑 3e — MERGE KOŞUSU GEÇERSİZ (kesik %5,2 > %5).** Ön-kayıtlı tablo üç satırla ✅✅ *"güçlü yeşil"* derdi — **ama merge 80 sorudan 2'sini cevaplıyor** (`A1 = 1,0` çünkü model neredeyse hiç konuşmuyor; **kütle %2,5**). ***Muhafız metriği tavanda, model çöp.*** §17 ve §20'de sayı görülmeden yazılan kör nokta **en uç hâliyle gerçekleşti.**
**⭐ TEŞHİS — geri ölçek, dengeleme değil YÜKSELTME yapıyor.** Her `τ` birim norma iniyor, sonra **5,826** ile geri ölçekleniyor; ama `τ_a`'nın eğitilmiş genliği **1,181** ⇒ ***`τ_a`'nın yönü kendi eğitildiği büyüklüğün ~4,9 katına çıkarılıyor.***
**⭐⭐ KESİKLER "UZUN CEVAP" DEĞİL — MODEL DEJENERE OLUYOR.** 12 kesiğin **tamamı** `forced_close=True`, `completion_tokens=1536`: *"İlgili madde madde 53 madde 53 madde 53…"* ⇒ **`MAXTOK` büyütmek çözmez, daha uzun döngü üretir** ve **ADR-0043 rejim değişmezini kırar**. *#42'deki base'in sonlanmama kalıbının merge'de yeniden belirmesi — ve aşırı-yükseltme teşhisiyle **tutarlı**.* **Kapı işini yaptı:** bozuk bir modelin sayılarına güvenilmeden önce yakaladı.
> ***Ders: cevaplanan-only metrikler çekinerek kazanmayı ödüllendirir. Bir kapı bu ailedense, yanında mutlaka bir kütle/coverage ekseni taşımalıdır — yoksa kapı, ölçmek için kurulduğu şeyin tam tersini onaylar.***

**§22 — DENEY 1: geri ölçek `min` (1,181). Dejenerasyon çözüldü, grounding çözülmedi.** kesik **%5,2 → %0,6** ✅ ⇒ **teşhis doğrulandı.** MERGE(min): cevaplanan 43/80 · A1 **0,9940** · kütle **53,4%** · M2 **0,934** · M2b **0,987**. **Çekinme tam korundu** (`τ_g` 0,607 → **0,987**), **grounding korunmadı** (kütle **çıplak base'in 56,7%'sinin altında**).
**⭐ GEOMETRİ ANLAŞILDI — sorun ÖLÇEK değil ORAN.** Geri ölçek **toplam gücü** ayarlıyor, **oranı değil**: `eşit oran + ölçek 1,18 → çekinme ✅, grounding zayıf` ↔ `eşit oran + ölçek 5,83 → dejenerasyon`. ***Eşit oranla grounding geri getirilemiyor.*** ⚠️ Bu, önerilen *"deney 2 = geri ölçek `‖τ_g‖`"*'yi **geçersiz kılar** — o da eşit oran, sadece daha yüksek ölçek.
**§23 — ham TIES artık kontrol değil HİPOTEZ.** ⭐ Norm dengeleme, çatışan parametrelerin **kimliğini neredeyse hiç değiştirmiyor** (%2,2451 ↔ %2,2541); değiştirdiği şey **ayrık ortalamanın ağırlığı** ⇒ ***ADR-0036'nın "küçük kol silinir" ifadesi mekanizma olarak işaret seçiminde değil AYRIK ORTALAMADA işliyor. Bu ayrım ADR'de yoktu; ölçümle ortaya çıktı.***

### 🟢 §24 — DENEY 2: ham TIES iki kazanımı BİRDEN taşıdı

| özne | cevaplanan | aşırı-red | A1 | **M1 kütle** | M2 Rej | M2b Rej |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| base | 46/80 | 0,425 | 0,9864 | 56,7% | 0,814 | 0,986 |
| Gemini 3.1 FL | 61/80 | 0,237 | 0,9561 | 72,9% | 0,930 | 1,000 |
| `τ_g` | 66/80 | 0,175 | 0,8658 | 71,4% | 0,873 | 0,607 🔴 |
| `τ_a` | 34/80 | 0,575 | 0,9697 | 41,2% 🔴 | 0,984 | 0,987 |
| MERGE ortalama | — | — | — | — | — | — 🛑 dejenere |
| MERGE min | 43/80 | 0,463 | 0,9940 | 53,4% | 0,934 | 0,987 |
| **MERGE ham** | **63/80** | **0,212** | **0,9087** | **71,6%** ✅ | 0,893 | 0,877 ✅ |

```
GROUNDING     τ_g 71,4%  →  merge 71,6%   TAMAMEN korundu (%100,3)
ÇEKİNME M2b   τ_g 0,607  →  merge 0,877   ← ᴷ³: 0,506 → 0,766, onarım %57 (~~%71~~)
ÇEKİNME M2    τ_g 0,873  →  merge 0,893   ← ᴷ⁴: 0,833 → 0,833, **+0,000**
```
> 🚨 **TÜRETİLMİŞ NİCELİK DAMGASI (Ö3-c):** §18'in ᴷ⁴ bloğu **girdileri** damgalamıştı, onlardan hesaplanan **oran/fark** damgasız kalmıştı — **turun kendi kuralının ihlali.** *`:1500`'de kaybolan işaret değil, **kazancın varlığıdır**: düzeltilmiş aletle `τ_g` v1 ile `tgta_v1` M2'de **birebir eşit** (ikisi de 55/66) — **merge M2'ye hiçbir şey taşımıyor.** Bu, ARA KAPI'nın "merge taşımıyor" teşhisini bağımsız olarak güçlendirir.*

**Yan kazanım — öz-sonlandırma geri geldi.** zorunlu kapatma: `τ_a` 230/230 · MERGE min 160/160 · **MERGE ham 115/230** ✅; ort token **1084 → 784** (**%27 düşüş**).

**🔴🟢 ARA KAPI — o günün aletiyle KAPATILABİLİR görünüyordu.**
> 🚨 **DAMGA 2026-08-06 (kusur K-2) — 2. GÖZLEM YENİDEN TÜRETİLDİ, HÜKÜM TERSİNE DÖNDÜ.** Düzeltilmiş cevaba-kör paydayla **aynı ön-kayıtlı formül**: `eşik = 0,90 × 0,961 = 0,8649` · `merge = 0,766` → **🔴 DÜŞTÜ (−9,9 puan)**; eski 0,887 eşiğine karşı da düşüyor, **paydalar eşit (77 ↔ 77)**. ⛔ Eşik/çarpan/formül **değiştirilmedi**. ***"Güçlü yeşil" ve "CP4-CP5 koşulabilir" cümleleri bugünkü ölçümle GEÇERSİZDİR.***

**⚠️⚠️ ADR-0036'NIN HÜKMÜ TERSİNE DÖNÜYOR:**

| ADR-0036'nın öncülü | durum |
| :--- | :--- |
| Kollar çok farklı ölçekte eğitiliyor | ✅ **DOĞRULANDI** — **8,87×** |
| TIES kütle-ağırlıklı | ✅ **DOĞRULANDI** — ama işaret seçiminde değil, **ayrık ortalamada** |
| Dengelenmezse küçük kol **silinir** | ❌ **ÇÜRÜTÜLDÜ** — ham TIES'te `τ_a` silinmedi (ᴷ³: **0,506 → 0,766**, sıçrama **+0,26**) |
| Bu yüzden dengeleme **gerekli** | ❌ **TERSİ** — dengeleme `τ_g`'yi eziyor (71,4% → 53,4%) |

**Mekanizma: norm, etkinin iyi bir vekili değil.** *`τ_a` yalnız 1,18 normla M1 reddini %42,5 → %57,5 çıkarabiliyor; dengeleme onu `τ_g` ile **eşit ağırlığa** getirince **aşırı temsil ediliyor** ve grounding eziliyor.*
**Kayıt için:** ADR-0036'nın *gerekçesi* ayakta; çürütülen şey **çıkarımı** — eski ADR silinmez, **hükmü tadil edilir**.
⚠️ **Seçim DEV'de yapıldı ve raporda böyle geçmeli:** *"merge yapılandırması DEV'de 3 varyant arasından seçildi"*; frozen TEST'e dokunulmadı. **Süpürmenin toplam bedeli: GPU $0 · hakem ~$0,11 · ~2 saat.**
**Artefakt kimliği: `tgta_v1`.** ⚠️ Eval çıktıları `*_tg_ta_ham_th` etiketiyle bırakıldı — *sonradan düzeltmek, koşulan şeyi daha derli toplu göstermek için **ölçüm kaydını yeniden yazmak** olurdu.*

**Bu turun yeni tuzakları:** **6.4** hazır imajın `ENTRYPOINT`'i · **6.5** lock dosyası iş türüne göredir · **6.6** öbekli eş zamanlı istemci slotları boş bekletir · **6.7** `gpu="A100"` iki farklı kart verir · **6.8** kümülatif ortalamayı erken okuyup karar verme · **6.9** *ön-kayıtlı bir kapıyı kümülatif ortalamayla beslemek* (6.8'in **kod tarafındaki kardeşi**) · **6.11** deterministik havuz sırasında `--skip-first` olmadan ek tur · **6.12** belgedeki "hazır komut" doğrulanmamış koddur.

---

<a id="49"></a>
## #49 — S3a ön-prob: retriever altın maddeyi bulabiliyor mu · bedesten hâlâ ayakta mı

**2026-08-04 · Bedel $0** (model çağrısı yok, hakem yok)
> **Neden bu prob var:** harness'a 1-2 ay yatırmadan önce planın iki temel varsayımını sınamak.

**Kurulum.** Korpus **40.496 madde** · DEV 80 soru (donmuş TEST **açılmadı**) · gömülen metin `kanun_adi + madde_no + text` · dense pencere **512, her modelde eşit** · 10 test geçiyor.
**Madde anahtarı kendi testleriyle geldi, çünkü buradaki hata sessizdir:** `Geçici Madde 1` ile `Madde 1` aynı sayılırsa 40.496 madde **27.706 anahtara** düşüyor ve `recall@k` **hiçbir yerde hata vermeden şişiyor.** DEV altınlarının **80/80'i** korpusa bağlanıyor.

**Prob 2 — bedesten sözleşmesi ✅ GEÇERLİ.** Türk IP doğrulandı; **4/4 `SUCCESS`** (arama · tam metin · madde ağacı · **madde-bazlı çekim** — sonuncusu retriever'ın asıl kullanacağı yol). ⇒ **güncellik iddiası ayakta.**
**⚠️ Ama prob betiğinin kendisi bozuktu — ve API'yi suçlu gösteriyordu.** Betik belge kimliğini `documentId`/`id` ile arıyordu; API'nin alanı **`mevzuatId`** ve sözleşme belgesi **en baştan doğruydu**. *İlk koşuda tablo "sözleşme değişmiş" diye doldurulacaktı ve sonucu **güncellik iddiasını gereksiz yere düşürmek** olurdu.* Betik ayrıca sözleşmenin 3. çağrısını **hiç sınamıyordu** — listenin **üçte biri ölçülmeden ✅ alacaktı.** → **tuzak 7.1:** *ölçüm aracının kendisi de sessizce yanlış olabilir; **negatif sonuç, araç aklanmadan kayda geçmez**.*

**Prob 1 — `recall@k`** (ön-kayıtlı merdiven, ucuzdan pahalıya):

| yöntem | @1 | @5 | @10 | @20 | kaçan (80'de) | süre |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| BM25 | 0,275 | 0,537 | **0,625** | 0,750 | 20 | 10 sn |
| `multilingual-e5-base` | 0,388 | 0,637 | **0,700** | 0,750 | 20 | 212 sn |
| `BAAI/bge-m3` | 0,487 | 0,725 | **0,800** | 0,863 | 11 | 617 sn |
| **hibrit** (BM25 + bge-m3, RRF) | 0,450 | 0,750 | **0,875** | **0,925** | **6** | 633 sn |

**Yoğun gömme BM25'i her k'da geçti** (+0,175 @10) ve **hibrit ikisini de geçti** — kaçan 20 → **6**. *BM25 tek başına en zayıf olmasına rağmen bge-m3'e **+0,075** ekliyor: **iki yöntem farklı soruları kaçırıyor**, aynı soruları değil.*

**⭐ Asıl bulgu: kaçan sorular retriever'ın değil, SORU KÜMESİNİN sorunu.** BM25 ile e5 **aynı 20 soruyu** kaçırıyor; desen tek — *"Başvurum kabul edilirse ne olur?"* · *"Mahkeme ne zaman davayı sona erdirir?"* ⇒ **bu sorular hangi kanuna ait olduklarını söylemiyor.** *`core_hard` altın madde elde tutularak üretildi; soru o bağlamda doğal okunuyor ama **tek başına erişim sorgusu olarak cevabı belirlemiyor**.*
İki tanı eklendi: BM25 **oracle-kanun** (havuz altının kendi kanunuyla sınırlı) `recall@10` **0,625 → 0,875** · `bge-m3` oracle-kanun **0,937** · hibrit **kanun-düzeyi** @10 0,912.
**Üç okuma:** ① **kanun bilinirse madde bulunuyor** — *BM25'in asıl derdi madde seçmek değil; altın madde 40.496 adayın arasında **boğuluyor***. ② kanun-düzeyi recall madde-düzeyinden hep yüksek ⇒ iki aşamalı kurgunun tavanı daha yüksek. ③ **hibrit bu açığın çoğunu tek aşamada kapattı**; iki aşamalı kurgunun **hesaplanmış tavanı** (0,950 × 0,962 ≈ **0,914**) hibritin fiilen ölçülen **0,925**'inin **altında** — *ve bu, hata birikimini **iyimser** sayan bir tavan.* ⇒ **S3 tek aşamalı hibritle başlar.**
→ **tuzak 7.4:** *`recall@k`'yı erişim kabiliyeti sanmak.* **Bu, tek-eksenle-okuma yasağının (A1 ↔ kütle) erişim tarafındaki karşılığı.**

**Ölçüm geçerliliği — üçü de "hata vermeden yanlış sayı" üretecekti, ikisi K1 kararını çarpıtırdı.** **7.3** e5 önekleri (`query:`/`passage:` ile **eğitildi**; öneksiz kod **çökmez, yalnız e5'i sistematik düşük gösterir**) · **7.2** bağlam penceresi eşitlendi (**e5 512, bge-m3 8192** — doğrulandı, varsayılmadı; *sabitlenmezse "hangi model daha iyi" ile "hangisi daha çok metin gördü" karışır ve fark **hiçbir yerde görünmez***) · RRF, **ham skor toplamı değil** (BM25 sınırsız ↔ kosinüs −1..1; ham toplam BM25'e **görünmeyen bir ağırlık** verirdi), 3 testle çivilendi.
**Cihaz — bir değişmezden bilinçli sapma:** *"harness CPU'da"* kuralı **servis anını** korur, bir kerelik çevrimdışı indeksi değil. CPU maliyeti ölçüldü: e5 **4,1 madde/sn** → ~**2 sa 45 dk** (GPU'da 3,5 dk).

**Eşik kararı (ön-kayıtlı, sayı görülmeden):** `≥%90 → aynen koş · %70-90 → hibrit eklenir · <%70 → DUR`. Hibrit **0,875** → 🟡 **hibrit gerekir.** ⚠️ **Eşik gevşetilmedi** — düzeltilen şeyler **alet** tarafındaydı ve *sayıyı yükseltmedi de: e5 öneki e5'i yukarı çekti ama e5 kazanan değil; pencere eşitleme bge-m3'ü **aleyhine** kısıtladı.*
**K1 ✅ ÇÖZÜLDÜ: `BAAI/bge-m3` + BM25 RRF hibriti.** *"Türkçe" etiketi değil, **ölçüm** karar verdi.*

**Açık kalanlar → insana.** ① ⭐ **DEV soru kümesi erişim ölçümü için yetersiz belirlenmiş** — soruların ~%25'i kendi başına kanununu söylemiyor; ⚠️ *bunu **sayıyı gördükten sonra** yapmak dışarıdan "kümeyi cilaladılar" diye okunur* ⇒ **orta yol: küme değiştirilmez, "ayırt edici mi" etiketi eklenir.** ② K2 chunk birimi açık ③ **K5 için erken sinyal:** `recall@10 0,875` ⇒ katı kapı soruların **~%12'sinde** doğru maddeyi **hiç görmeden** cevap üretmeye çalışacak ⇒ kütle ekseninin ölçülmesi **zorunlu** ④ iki aşamalı retriever ölçülmedi.

**Reddedilen alternatif — vektör veritabanı.** **Ölçüldü:** 40.496 × 1024 indekste **kaba kuvvet** kosinüs + top-20 = **8,2 ms/sorgu** (CPU); indeks **166 MB** fp32 / **83 MB** fp16 ⇒ **bu ölçekte ANN indeksine bile gerek yok.** Reddedildi: (a) çözdüğü problem bizde yok (b) **erişilebilirlik kısıtı** — barındırılan servis ağ bağımlılığı, vatandaş çevrimdışı koşamaz (c) *dışarıdan değişen bir parça ölçüme girmemeli.* **Alınan fikir:** hibrit (BM25+vektör) — **yön doğrulanıyor.**

---

<a id="50"></a>
## #50 — Adım 0: modül-başına norm kapsamı 🔴 · gerekçe çürüdü, kütle ekseni kararı $0'a verdi

**2026-08-04 · GPU yerel · hakem $0** · [ADR-0053](../adr/kararlar-0045-0063.md#adr-0053)
**Ön-kayıtlı kabul:** M2b > 0,877 **ve** M1 kütlesi ≥ %71,6 — **ikisi birden.**
> 🚨 **ᴷ³ BU GİRİŞİN M2b EŞİĞİ EMEKLİ BİRİMDEDİR.** Ön-kayıtlı `0,877` hakemin **modelin cevabını görerek** verdiği paydayla üretilmişti; yürürlükteki alette aynı hücre **0,766** ölçüyor. ⛔ **Eşiğe DOKUNULMADI**, yalnız **birimi** damgalandı.
> **Neden kritik:** ADR-0052 alternatif D'yi açık bırakıyor. Yeniden denenirse M2b örneğin `0,80` ölçülür — bu **bugünkü 0,766'ya göre İYİLEŞMEDİR**, ama emekli birimdeki `> 0,877` eşiğine bakan okuyucu **BAŞARISIZ** ilan eder. ***Damgasız bırakmak, ölçümü tersine okutan bir tuzaktır.***

**1. Önce bedava kısım: gerekçe ölçümde durmuyor.** Adım 0'ın metni *"iki kolun da en büyük normu aynı MLP yüzeyinde; **global norm bunu göremiyor**"* diyordu. Kayıtlı norm kırılımından **hiçbir ağırlık yüklenmeden** okundu: `τ_g/τ_a` oranı **11 yüzeyin hepsinde 7,18-10,08**; global normalleştirmeden sonra modül payları **zaten eşitleniyor** (0,88-1,24). ⇒ ***"global norm bunu göremiyor" önermesi yanlış: profil orantılı olduğu için görüyor.*** `τ_a` bir **kapsam artefaktı** yüzünden silinmiyor.
> **Ders:** *"iki kolun da en büyük normu aynı yüzeyde"* gözlemi **tek başına** bir kapsam sorunu kanıtlamıyor — **kanıtlayan şey profillerin ORANTISIZ olması olurdu ve o ölçülmemişti.** Ayırt eden **oran sütunu**.

**2. Ama kapsam değişikliği no-op da değil.** *Gerekçe çürüdü diye deney iptal edilmedi — bu repoda kararı ölçüm verir.* `‖W_modül − W_global‖ / ‖W_global − base‖ = **0,272**` ⇒ **yön %27,2 farklı, genlik aynı (%0,2)**; fark TIES'in **doğrusal-olmayan işaret seçiminden** geliyor.
**3. Eval: kabul ölçütü 🔴 DÜŞTÜ — ve hakem hiç çağrılmadı.** Geçerlilik kapısı geçildi (kesik %1,2). Kabul bir **VE** koşulu ve genlik `min` ile aynı olduğu için **düşmesi beklenen eksen kütleydi** ⇒ önce yalnız **m1** koşuldu, çekinme tespiti **regex tabanlı (hakem gerekmez)**:
```
cevaplanan 45/80 → coverage %56,2
kütle ≤ %56,2  (A1 = 1,000 olsa BİLE)   gereken ≥ %71,6
```
**Kütle tavanı ölçütün 15,4 puan altında** ⇒ A1'i ölçmek sonucu değiştiremezdi → **toplam hakem maliyeti $0.**
Modül-başına kapsam global `min`'i **tekrarladı** (43 → 45 cevap). *%27'lik yön farkı aşırı-reddi kurtarmadı — çünkü **aşırı-reddi yaratan yön değil genlik**: her iki kapsamda da `τ_g` kendi eğitim genliğinin ~1/9'una iniyor.*

**Kalan açık.** ⚠️ `τ_a`'nın merge'de seyrelmesi **hâlâ açık**; kalan adaylar: trim eşiği · λ · farklı operatör · ya da **en doğrudan olanı — `τ_a`'yı daha yüksek genlikte eğitmek** (70 adım @1e-5 çok kısaydı) — *sonuncusu merge parametresi değil **eğitim** parametresi ve muhtemelen doğru yer orası.*
**⭐ Genelleştirilebilir ders — bileşik kabul ölçütünde sıralama.** Kabul `A ve B` biçimindeyse **önce en ucuz ve düşmesi en muhtemel ayağı ölç.** *Sıralama tersine olsaydı: m2b hakemle ölçülür (~$0,3), muhtemelen 0,98 çıkar, "bir eksen geçti" hissi doğar, sonra m1 koşulur ve zaten düşerdi. **Aynı sonuç, artı para, artı tek-eksenle-okuma riski.***

---

<a id="51"></a>
## #51 — ⭐ HARNESS AÇIK ilk ölçüm: ürün sayısı ilk kez görüldü

**2026-08-04 · GPU $0 · hakem $0,038** · Özne `tgta_v1`, harness KAPALI çıpasıyla **aynı artefakt**

> 🚨 **DÜZELTME 2026-08-05 — bu girdinin A1 ve kütle sayıları YANLIŞ metrikle üretilmişti.** `harness_tablo.py` `A1` diye **cevaplanan-only** değil **puanlanan tüm kalemlerin** makrosunu yazıyordu (tuzak **2.16**); çekinmeler de puan alıyor ve bu koşuda **0,9091** alarak makroyu yukarı çekmişler ⇒ **ON/OFF kıyası elmayla armuttu.**
> | eksen | bu girdide yazan | **doğrusu** |
> | :--- | ---: | ---: |
> | A1 (cevaplanan-only), AÇIK | 0,7823 | **0,7591** |
> | kütle, AÇIK | %58,7 | **%56,9** |
> | A1 · altın getirilen, AÇIK | 0,9344 | **0,9230** |
>
> **Metin olduğu gibi bırakıldı.** Üç okumanın **hükmü değişmedi**: düşüş **daha da büyük**; ⭐ manşet bulgu **ayakta** (0,9230 > 0,9087, marj +2,6 → **+1,4** p) **ama k'ya bağlı** — k=10'da **0,8426 ile tersine dönüyor**; kapının sınırı aynen geçerli.

> **Bu sayı hiç görülmemişti.** Bugüne kadarki her ölçüm harness KAPALI'ydı: modele altın madde **elle** veriliyordu. Harness AÇIK'ta bağlamı **retriever** seçiyor — *yani ürünün gerçekte yapacağı şey.*

**Kurulum.** hibrit BM25+bge-m3 RRF · indeks 40.496 · **k=5** · **tam madde indekslenir**, 900 kırpma bağlam **modele verilirken** · rejim birebir · **tek fark m1 ile h1 arasında SADECE bağlamın nereden geldiği** · geçerlilik ✅ kesik %2,5.

| eksen | harness **KAPALI** (m1) | harness **AÇIK** (h1, k=5) |
| :--- | ---: | ---: |
| altın madde bağlamda | **garanti** (kurgu) | **60/80** — `recall@5` 0,750 |
| coverage | 63/80 = 0,7875 | 60/80 = 0,7500 |
| A1 (cevaplanan-only) | **0,9087** | 0,7823 *(→ **0,7591**)* |
| **kütle** | **%71,6** | %58,7 *(→ **%56,9**)* |
| ⭐ A1 · **altın getirilen** | 0,9087 | **0,9344** *(→ **0,9230**)* |
| atıf: doğrulanan/toplam | 87/89 | **89/89** |
| **uydurulmuş madde numarası** | **0** | **0** |
| katı kapı reddi | 2/80 | **1/80** |

**Üç okuma.**
**1. Ürün sayısı oracle sayısından düşük — ve olması gereken bu.** Düşüşün tamamı erişimden. *Bu, harness'ın kusuru değil **ölçümün dürüstleşmesi**.*
**2. ⭐ Retriever doğru maddeyi bulduğunda model DAHA sadık** (0,9344 > 0,9087). Olası açıklama: m1 bağlamı **4 hard-negative çeldirici** + altın; retriever bağlamı ise konusal olarak yakın **5 gerçek madde** ve **çeldiriciler kadar tuzaklı değil.** ⇒ *"gerçek retriever daha gürültülü bağlam verir"* varsayımı — **S3'e girerken yazdığımız gerekçelerden biri — bu ölçümde doğrulanmadı.**
**3. ⚠️ Kapı fabrikasyona karşı çalışıyor ama ASIL HATAYI yakalayamıyor.**
```
altın geldi   → cevapladı   46        altın GELMEDİ → cevapladı  14  ← A1'i düşüren sınıf
altın geldi   → çekindi     14        altın GELMEDİ → çekindi     6
```
**14 soruda model altın gelmeden cevapladı** — muhtemelen getirilen *başka* bir maddeden; **o atıf gerçek, korpusta var, doğrulanır, kapıdan geçer.** ⇒ *atıf doğrulayıcısı **"uydurulmuş atıf"**ı çözüyor ama **"gerçek ama soruya uymayan madde"**yi çözmüyor.* **Tasarımın sınırı, hatası değil.**
⛔ **Bu, Sprint 3'ün varlık gerekçesinin YARISINI ÇÜRÜTÜYOR.** *"Atıf doğrulayıcı uydurulan madde numarasını yakalar"* deniyordu — **uydurulan madde numarası YOK**, dolayısıyla A1'e katkısı **ölçülebilir biçimde sıfır**. *A1'in açığı fabrikasyondan değil **isabetsizlikten** geliyor ve o deterministik kodla çözülmüyor.* Aynı maddenin `M2b` ayağı **çürümedi, SINANMADI.** Aynı bölümün 3. maddesi de **zayıfladı** (2. okuma).

**Doğrulayıcı kalibrasyonu — ADR-0038'in adını koyduğu borç ödendi.** Katı kapıda **her yanlış negatif doğrudan coverage kaybıdır.** İlk koşuda 5 `KANUN_YOK`; **gözle** okununca **beşinin de yanlış negatif** olduğu görüldü — model resmî adın yaygın **kısa hâlini** yazıyor ve o hâl resmî adın **soneki** (`İflas Kanunu` ↔ `İCRA VE İFLAS KANUNU`). Ad indeksi ≥2 sözcüklü sonekleri taşıyacak şekilde düzeltildi (**1 sözcüklü sonek her kanuna uyar, dışlandı — testi var**): `KANUN_YOK` **5 → 0**, katı kapı reddi **6 → 1**. ⚠️ Bu **alet** düzeltmesi, eşik değil.
Aynı disiplin Adım 2'de **dört hata daha** yakalamıştı, **hepsi yanlış alarm yönünde**: ad çakışması (`İŞ KANUNU` = 4857 **ve** 1475) · yalnız BÜYÜK harfli adı tanıma · **Python `upper()`'ın Türkçe olmaması** (`Medeni` → `MEDENI` ≠ `MEDENİ`) · ada kaçan önceki sözcük.

**🚨 Koşu sonrası bulunan açık — mülga maddeye atıf kapıdan geçiyor (borç B7).**
```
cevap : "İşçinin hakları İŞ KANUNU Madde 15 hükmüne göre belirlenir."
atıf  : DOGRULANDI (kanun_no = 1475) · kapı GEÇTİ ✅
korpustaki metin: "110- (Mülga: 22/5/2003/4857/120 md.) Ek"
```
Sebep yapısal: **korpusta yürürlük alanı yok** ve aynı ad iki kanuna ait olabiliyor. ⚠️ Bu, *"denetlenebilir"* ürün vaadindeki **en somut açık** ve **B1'den farklı bir sınıf**: *B1'de atıf gerçek ama soruya uymuyor; burada atıf soruya **uyabilir** ama **hüküm yürürlükte değil**.*
**⭐ Ve bu, graph-RAG'in ilk ÖLÇÜLMÜŞ gerekçesi.** *Ölçüm graf'ı beklenen yerlerde **gereksiz** buluyor (erişim, cevap kalitesi) — ama **yürürlük/ilga/tadil/atıf zinciri** sınıfında düz vektör benzerliğinin okuyamayacağı bir boşluk açık.* ⚠️ **Acil çözüm yine de graf değil:** korpusa **yürürlük alanı** eklemek tek başına B7'yi kapatır ve bir **veri** işidir.

**Şerhler.** ⚠️ **A1 tek-altın yer-gerçeğine göre** — harness AÇIK'ta model **başka** bir maddeden doğru cevaplasa bile sadakatsiz sayılıyor; kıyaslanabilir olan **A1 · altın getirilen** · ⚠️ soru kümesi erişim için yetersiz belirlenmiş · ⚠️ **k=5 seçildi, süpürülmedi** · ⚠️ hakem insan-κ kalibresiz.

---

<a id="52"></a>
## #52 — Korpusun kendisi bozuk: satırların %22,7'si yinelenen anahtar

**2026-08-05 · Bedel $0** (salt-okunur korpus ölçümü)
> S2 için `(Mülga: …)` kalıbını ayrıştırmaya hazırlanırken ölçüldü. **Aranan şey bulundu ama yanında aranmayan bir şey çıktı:** korpusun **madde kimliği güvenilir değil.**

**1. Anahtar bütünlüğü.** satır **40.496** · benzersiz anahtar **31.304** · yinelenen anahtar 4.188 · **fazladan satır 9.192 = %22,7** · `text` < 60 karakter **7.289 (%18,0)**, bunlardan `(Mülga` içeren 1.321.
En çok yinelenen: `3520/Geçici 1` **×162** · `3520/1` ×135 · `2004/309` ×27.

**2. İki ayrı bozulma sınıfı — aynı sayının içinde.**
**A) Tablo parçalanması — SAHTE MADDE üretiyor.** `3520` özünde bir **tablodur** (eski madde no ↔ yeni madde no); ayrıştırıcı **1.166 tablo hücresini "madde" sanmış** (tüm korpusun **%2,9'u, TEK kanundan**): `len=12 '2.1.1961 203'` · `len=22 '9.7.1953 6124 Muvakkat'`. *İndekste yer kaplıyorlar ve retriever'ın top-k yuvalarında gerçek maddelerle yarışıyorlar.*
**B) Alt-madde soneki kayboluyor — GERÇEK maddelerin kimliği çakışıyor.** `2004/Madde 309` **27 kez**; bunlar çöp değil, **gerçek ve farklı** maddeler — sonek `madde_no` alanında değil **metnin içinde** (`309` · `309/a` · `309/b` · `309/c` · `309/ç`). *Bu sınıf daha sinsi: **atıf doğrulayıcısı `Madde 309` ile `Madde 309/a`'yı ayırt edemez**, ve `recall@k`'da altın `309/a` iken getirilen `309` **isabet sayılır**.*

**3. ⭐ S1'in sayılarını kirletiyor mu — HAYIR, ölçüldü.** 80 sorunun **5'inde** yinelenen anahtar var; temiz alt küme (n=75) `recall@5` **0,7467** ↔ tüm küme **0,7500** (Δ = 0,0033) ⇒ **S1 ayakta**, ölçüm bu kusurdan **sistematik yarar görmüyor.**

**4. 🚨 B7'nin mekanizması — #51'e düzeltme.** #51 *"yürürlük alanı yok"* demişti — **doğru ama eksik.** Doğrulayıcının *"DOGRULANDI"* dediği kayıt (`1475/Madde 15`) **39 karakterlik yanlış ayrıştırılmış bir parça**: `madde_no` "Madde 15" diyor, metin **"110-"** ile başlıyor. ⇒ **İki kusur üst üste binmiş:** (a) yürürlük alanı yok (b) **eşleşilen kaydın kimliği zaten yanlış.** ***`mulga` alanı eklemek (a)'yı kapatır, (b)'yi kapatmaz.*** Ayrıca **9 `kanun_adi` birden fazla `kanun_no` taşıyor.**

**5. S2'nin aday kuralı ölçüldü.** Naif kural (*"metinde `(Mülga` geçiyorsa mülga"*) **yanlış** — madde bütün olarak yürürlükte olup yalnız bir **fıkrası** mülga olabiliyor: `(Mülga` **geçiyor** 3.652 ↔ `(Mülga` ile **başlıyor** **2.496** ⇒ **naif kuralın yanlış pozitifi 1.156.**

**6. Ders — ölçüm aracının kendisi de sessizce yanlış olabilir (tuzak 7.1'in tekrarı).** Bu turda **kendi kontrol betiğim** yanlış sayı üretti: `(altin_sirasi or 99) < 5` yazıldı; **`altin_sirasi == 0` falsy** olduğu için **1. sıradaki her isabet kaçırılmış sayıldı**. Temiz alt kümenin `recall@5`'i **0,2933** çıktı (gerçek 0,7467) ve bu sayı *"kirlilik recall'ı şişiriyor"* diye okunabilirdi — ***yani bulguyu TERS YÖNDE doğrulamış görünürdü.*** Yakalanma sebebi **aritmetik tutarsızlık** (22 + 5 ≠ 60). **Hata vermedi, uyarı vermedi.** → **tuzak 7.5**.

**7. ⭐ Kapsam ölçümü — "bozuk satırlar modele fiilen ULAŞIYOR mu?"** (`context_shown` üzerinde, yani **modele giden metnin kendisi**):

| bozulma sınıfı | korpusta | **modele ulaşan blok** | altın etiketi bozuyor mu |
| :--- | ---: | :--- | :--- |
| **A — tablo/cetvel parçası** | ~7.966 satır | **0 / 800** ❌ | hayır |
| **B — alt-madde soneki kaybı** | **98 satır** | **7 / 800 · 6 soru** ✅ | ✅ **3/80 soru** |

⚠️ **Anahtar üzerinden saymak yanılttı:** anahtar eşleşmesiyle *"26/80 soru bozuk parça görüyor"* çıkıyordu; `context_shown`'a bakınca **6/80**. *Fark şu: anahtar yinelenmiş olsa bile retriever o anahtarın **doğru** satırını getiriyor.* ⇒ ***Yinelenme ≠ kirlenme*** — biri korpusun, diğeri bağlamın özelliği. **Sayının hangi nesne üzerinde ölçüldüğü, sayının kendisinden önemli.**
**Sınıf A neden ulaşmıyor:** parçalar çok kısa (`", Ek"` = 4 karakter); ne BM25 ne yoğun vektör onları üste çıkarıyor ⇒ **korpusu şişiriyorlar ama ölçülmüş erişim etkileri sıfır.**
**🚨 Sınıf B'nin asıl zararı: korpus, DOĞRULANABİLİR-AMA-YANLIŞ atıf ÜRETİYOR.** Model `Madde 31` diyor, doğrulayıcı *"var"* diyor, katı kapı geçiriyor — **ama doğru numara `31/a`.** ***Ve metriğimiz bunu göremiyor, çünkü altın etiket de aynı yanlış numarayı taşıyor.*** *B7/B8 ile aynı aileden ama **kaynağı model değil korpus**: hata **veri katmanında** üretiliyor, **ölçüm katmanında görünmez** oluyor.* Manşetteki *"0 uydurma madde no"* **ayakta kalıyor** (model gerçekten uydurmuyor) ama **yanına bu şerh düşülmeli.**

**Hüküm ve sıra.** S1 etkilenmiyor · **S2'nin kapsamı ölçüme göre seçildi: `mulga` + sınıf B; sınıf A ERTELENDİ** — *gerekçe menüden değil sayıdan geldi: sınıf A'nın **ölçülmüş erişim etkisi sıfır**, tek yapacağı indeksi değiştirip bugünkü sayıları geçersiz kılmak olurdu — **ölçülemez bir kazanç için ölçülmüş bir sayıyı harcamak*** ⇒ borç **B9** · ⚠️ indeks yine de yeniden kurulacak (`madde_no` düzeltilince **gömülen metin değişiyor**; 98/40.496 = %0,24) · ⚠️ **eval altın etiketleri de düzelecek** — *bu, soru kümesini **değiştirmek değil**, etiketin korpustaki karşılığını **doğrultmak**.*
