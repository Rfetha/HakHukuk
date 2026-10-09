# Gemma 4 12B hattı — araştırma kaydı (kronoloji + sayılar)

> **Bu belge ne:** emekli edilen Gemma 4 12B hattının **38 `research_log` girdisinin** birleştirilmiş
> hâli. Tekil dosyalar 2026-07-24'te silindi; içerikleri buraya taşındı. Yeni hattın kronolojisi
> **#39'dan devam eder** ve ayrı dosyalar hâlinde tutulur.
>
> **Pazarlıksız kural: sayılar birebir korundu.** Damıtma *anlatıda* yapıldı, rakamlarda değil.
> Bu belge paper'ın **Results** ve **Discussion** bölümlerinin ham maddesidir — bir sayı burada yoksa
> hiçbir yerde yok demektir. Silinen dosyalar git geçmişinde duruyor (`4d70a77` ve öncesi).
>
> **Damıtılmış dersler ayrı belgede:** [`../adr/gemma4-12b-dersler.md`](../adr/gemma4-12b-dersler.md)
> Bölüm A. Burada *ne oldu ve kaç çıktı* var; orada *bundan ne öğrendik* var.
>
> ⚠️ **Bu sayılar yeni base'e taşınmaz.** Protokol satırı ayrı tutulur; yeni hattın rakamları bu
> tabloyla **aynı tabloya karıştırılmaz** (ADR-0025/0027).

---

## Künye — protokol sabitleri

| | |
| :--- | :--- |
| **Model** | Gemma 4 12B (`gemma-4-12B-it-qat-q4_0-unquantized`) + QLoRA |
| **Eğitim** | Modal A100-40GB · **Eval** lokal ($0, OpenAI hakem) |
| **Hakem** | gpt-4o-mini (paper hedefi: cross-family) · **seed 3407** |
| **n** | core_hard 40 · trap 35 · genelleme dilimleri 35 |
| **A1 kuralı** | **cevaplanan-only macro** (çekinme ayrı sayılır, `rescore_answered.py`) |
| **Eval-mirror** | 900-char chunk clip — eğitimdeki kırpma eval'de birebir |
| **Birincil kitle** | UZMAN (2026-06-13 reframe) |

**Mod sözlüğü.** **KÖR** = madde prompt'ta yok, model ezberden cevaplar (parametrik test).
**MADDE-VERİLİ / oracle** = doğru madde metni elle prompt'a konur. ⚠️ **Bu gerçek RAG değil** —
retriever yok; "mükemmel getirme" simülasyonu, yani gerçek RAG'ın **iyimser tavanı.**
Sonradan 6 moda genişledi: M1 gold+distractor · M2 near-miss tek yanlış kaynak · M2b çok-distractor
gold-yok · M3 boş bağlam · M4 temiz oracle · M5 kör.

---

# I. Çerçeve ve v0 — kaynaksız verinin bedeli

### #01 · ~2026-05/06 — Çerçeve + planlama
Private repo + proprietary lisans · base Gemma 4 12B · eğitim Modal A100 · veri kuralı: yalnız güncel
TC mevzuatı, Lexpera/Kazancı **asla**, EDA-doğrula (`newmindai/EuroHPC-Legal` reddedildi — çöp).

### #02 · 2026-06-07/08 — ⭐ v0 (forum verisi) → BAŞARISIZ
**Veri:** 29K, `turkish_law_qa_dataset` + `turkish-law-chatbot` (forum).
**Sonuç:** modeli batırdı — `legal_acc 0.362 → 0.124`.
**Post-mortem (2026-06-13 kanıtlandı):** *"7 Kasım 1982'de yürürlüğe girmiştir."* cevabı
**154 farklı soruya birebir** yapıştırılmış; atıf oranı **%13.6** (sıkı ölçüt).
**Ders:** kaynaksız QA verisi doğruluğu öğretmez, **halüsinasyon hattı ezberletir.**

### #03 · 2026-06-08 — Grounded pivot → v1 verisi + kalite kapısı
**Hamle:** doğruluğu gerçek kanun maddesinden imal et (madde → gpt-4o-mini Q&A → doğrula).
**Veri:** **21.458** grounded Q&A (train 19.305 / val 1.131 / test 1.022), **~$1.16**.
Kaynak = **2.759 madde**, **10 çekirdek kanun** (TMK, TBK, İİK, İş, TKHK, Aile, HMK, KatMülk, TCK, CMK).
Filtre `usable()` ham 40K → 21K → çekirdek 2.759.
**Eğitim-öncesi kalite kapısı, n=40:** faithfulness **0.984** · hallucination 0.016 ·
cit_precision **1.00** · wrong_ref **0.00**. *(İlk ölçüm 0.947'ydi; skorlayıcıdaki meta-iddia
artefaktı düzeltilince 0.984'e çıktı — gerçek hata 0.0'da kaldı, yani 0.947 bir **alt sınırdı**.)*

### #04 · 2026-06-09 — v1 SFT eğitimi
1 epoch · **1207 step** · ~3.5 saat · **~$10**. Adapter → `outputs/v1/`.
**Başlatma dersi:** `train.remote` client'a bağlı bekler → WSL kapanınca cancel → **4 koşu yandı.**
Çözüm `spawn()` + `--detach`.

### #05 · 2026-06-12 — Dış analiz raporu → fabrikasyon çıktı
Rapor *"filtre gevşek, %3 değişiklik dili kaçıyor"* dedi. Gerçek `usable()` import edilip 40K'da
koşuldu: kaçak **%0**, önerilen fix **no-op**. Filtreye dokunulmadı.
Yan ürün: **404 şüpheli kaynak** (341 kısa + 65 mülga-gövde) → hedefli audit listesi.
**Ders:** bir agent *"çalıştırıp ölçtüm"* dese bile gerçek modülü import edip doğrula.

---

# II. Ölçüm krizi — SFT abstention'ı yok ediyor

### #06 · 2026-06-13 — ⭐ base vs v1: KÖR vs MADDE-VERİLİ (n=20)

| metrik | KÖR base | KÖR v1 | oracle base | oracle v1 |
| :--- | ---: | ---: | ---: | ---: |
| faithfulness | 0.571 | 0.520 | **0.980** | **0.971** |
| hallucination | 0.429 | 0.480 | 0.020 | 0.029 |
| cit_precision | 0.833 | 0.200 | 0.950 | 0.850 |
| wrong_ref | 0.125 | 0.800 | 0.050 | 0.150 |
| cit_recall | 0.900 | 0.450 | 1.000 | 0.900 |

> ⚠️ Bu n=20 keşif koşusunun detay dosyaları eval temizliğinde **silindi**; sayılar yalnız bu tabloda.

**Bulgular.** (1) **KÖR test yanıltıcıydı** — madde verilince faithfulness 0.52→0.97, halüsinasyon
0.48→0.03; v1'in "felaketi" (KÖR wrong_ref 0.80) **test artefaktı.** (2) **Etiket hatası:** madde
*metni* verilip *etiketi* verilmeyince model numarayı yine uydurdu → **RAG dersi: getirilen chunk
atıf metadatasını taşımalı.** (3) Oracle'da **v1 ≈ base** — SFT ana metrikte base'i geçmedi.

### #07 · 2026-06-13 (akşam) — ⭐⭐ BENCHMARK RUN: base/v0/v1, n=40/35

| eksen | metrik | base | v0 | v1 |
| :--- | :--- | ---: | ---: | ---: |
| **A1** (CORE) | faithfulness | **0.976** | 0.920 | 0.960 |
| | hallucination | 0.024 | 0.080 | 0.041 |
| | wrong_ref | 0.000 | 0.000 | 0.026 |
| **A3** (TRAP) ⭐ | **Rej\*(LLM)↑** | **0.786** | **0.000** | **0.000** |
| | Rej(exact)↑ | 0.679 | 0.000 | 0.000 |
| | fabrication↓ | 0.214 | 1.000 | 1.000 |
| | param_leak | 0.286 | 0.769 | **1.000** |
| | valid_traps | 28/35 | 26/35 | 26/35 |
| **A4** (CORE) | cite_present | 0.925 | 0.125 | 0.975 |
| | paren_cite | 0.025 | 0.000 | **0.975** |
| | med_len (karakter) | 308 | 152 | 152 |

**1. ⭐ SFT abstention'ı YOK ETTİ — öngörüden çok sert.** Literatür "~%24 bozar" diyordu;
ölçülen **0.786 → 0.000 tam çöküş**, tuzakların %100'ünde uydurdu. **v1 param_leak = 1.000** =
verilen yanlış kaynağı tamamen yok sayıp ezberden cevapladı.
**2. v1'in tek kazanımı atıf FORMATI** (`paren_cite` 0.025→0.975). Ama A1'de base'i geçmedi
(0.960 < 0.976) ve wrong_ref'i sıfırdan 0.026'ya çıkardı. **Takas berbat.**
**3. v0 ayrıca bozuk:** cite_present 0.125, med_len 152 → forum-register çöküşü A4'te de net.
**4. A1 oracle tavanı:** üçü de 0.92-0.98 → **ayırmıyor**; SFT etkisi A3 (yıkıcı) + A4'te görünür.
**5. Payda notu:** `valid_traps` < 35 çünkü hakem "yanlış kaynak aslında cevaplıyor" derse tuzak
elenir. base 7, v0/v1 9 elendi — fark küçük, başlığı değiştirmez.

### #08 · 2026-06-13 (gece) — ⭐ CANON metodolojisi kilitlendi
**Tetik:** kullanıcı itirazı (*"model çıplak kanunu bilmeli"*) + sabahki **metrik hatası**
(kaynaksız cevabı "kaynağa sadakatsiz" diye cezalamak → faithfulness KÖR'de **TANIMSIZ**).
8 tasarım kararı grill ile çözüldü → **22 kaynaklı literatür doğrulaması** → 4 düzeltme:
1. A1∧A2 manşetten **ikincil diagnostiğe** indi (alan ayrı raporlar; ortalamak zıt sinyali siler).
2. **A3 çöküşü = ÖZGÜN bulgu, replikasyon DEĞİL** — yayınlı FT-harm literatürü **over**-refusal
   belgeliyor, bizimki **under**-refusal (zıt yön).
3. Cross-judge **CROSS-FAMILY** olmalı (aynı aile self-preference'ı gidermez).
4. Bootstrap GA + paired McNemar; OOD unseen-statute dilimi paper öncesi.

Kod: `score_correctness.py` (yeni), `bench_scorecard.py` canon'a güncellendi. CI [0.625, 0.875] @ n=40.

### #09 · 2026-06-13 (gece) — ⭐⭐⭐ CANON PİLOT → Product A

| hücre | metrik | base | v1 |
| :--- | :--- | ---: | ---: |
| CORE-KÖR | A2 doğru (CI95) | 0.225 [.10,.35] | 0.300 [.17,.45] |
| | A2 lenient | **0.850** | 0.675 |
| CORE-Oracle | A1 faith | 0.977 | 0.960 |
| | A2 doğru | **0.925** | 0.800 |
| | **A1∧A2** | **0.875** | 0.775 |
| | A4 paren | 0.025 | **0.975** |
| TRAP | **A3 Rej\*** | **0.741** | **0.000** |
| | fabrication | 0.259 | 1.000 |
| | TRAP-A2 (diag) | 0.114 | 0.114 |

**1. Scope A/B → PRODUCT A.** Kör modda v1 ≈ base (CI çakışık, lenient base lehine) →
**FT kanun gömmüyor.** İkisi de kör hukukta kötü (~%25).
**2. v1 oracle'da bile base'den KÖTÜ** (A1∧A2 0.775 < 0.875) → SFT **aktif zarar** verdi.
**3. TRAP-A2 ikisi de 0.114 ama farklı sebep:** base çekiniyor, v1 cevaplıyor ama **%88 yanlış**
= halüsinasyon baskın → hedge dozajı büyük.
**4. Kök ders:** SFT bilgi değil **üslup** öğretir; base = güçlü okuyucu + kalibre model.

---

# III. v2b — RAFT ve ilk gerçek kazanım

### #10-12 · 2026-06-14 — Üç deep-research → reçete kartı
**(1) v2-teknik (24 kaynak):** RAFT (context-grounding) + R-Tuning boundary-refusal, cevaplanabilir
dilimle dengeli (yalnız-belirsizlik known-acc'yi %52'ye çökertir). **Register loss'a girmez.**
*"DPO daha az yıkıcı"* iddiası **çürüdü.**
**(2) hukuk-veri (12 bulgu):** **CPT bilgi gömer, SFT gömmez** — SaulLM +%7 ama 54B/540B-token.
**(3) FT-reçete (26 kaynak, 109 iddia → 21 doğru / 4 çürük):**
- RAFT k=5 (1 gold + 4 distractor); **P=%80 evrensel optimum DEĞİL** (alan-bağımlı %40-100).
- **Keyfi %15/%25 hedge oranı ÇÜRÜTÜLDÜ** — veri-güdümlü olmalı.
- **K3 destek:** v1 çöküşü literatürdeki over-refusal mekaniğiyle akraba (known-acc %16-37 düşer).
- Forgetting: LoRA az unutur ama sıfırlamaz; `all-linear` şart; LoRA LR ≈ full-FT × 10.
- **Replay %1-5** yeterli. 🚫 **3e-4 re-warming YASAK** — v1 çöküşü rejimi.

### #13-14 · 2026-06-14 — v2b altyapı + 🔴 sessiz veri bozukluğu
**Bug (smoke yakaladı):** B2 smoke → gate **16/16 RED**. Kök neden: pack, `source` alanını gold
metni sanıyordu — o alan **provenance etiketi** (`'grounded_gpt-4o-mini'`), madde metni değil.
JOIN eklendi (`kanun_no|madde_no`), kapsam **%100** (19.305/19.305). Smoke tekrar → **19/20 geçti**
(1 ret = teacher distractor'dan alıntı yapmıştı, gate **doğru** eledi).
**Ders:** ~16 çağrılık smoke, ~15K çağrılık (~$9) koşudan önce bozukluğu yakaladı.

**Base baseline (n=40) — v2b'nin yeneceği çıpalar:**
**M1** faithfulness_micro **0.879** · hallucination 0.122 · cit_precision 0.905 · wrong_ref 0.095 ·
macro 0.742. **M3** rejection **1.000** (40/40), fabrication 0.000 → **base boş bağlamda kusursuz.**
**Okuma:** base zaten iyi bir RAG-okuyucu + çekinici; v2b'nin işi yeni yetenek eklemek değil,
bu ikisini **koruyabildiğini** göstermek.

**🔴 Topik-skew dersi:** seed dosyası kanuna göre **sıralı**, shuffle değil → ilk 14.800'ü almak
rastgele örnek değil: **İİK (2.727, ~%14) ve Kat Mülkiyeti üretilende SIFIR.** "Eldekiyle eğit"
iptal, tam set zorunlu. **Ders:** partial-tolerant hat için seed'ler pack'te shuffle'lanmalı.

**Tier-1 RPD duvarı:** ~10K çağrı/gün limiti → B2 14.800/19.305'te durdu.
**Paralelizasyon bug'ları:** timeout'suz client paralel koşuda kilitliyor (`timeout=30, max_retries=0`);
6 worker TPM tavanına biniyor → default 4.

### #15 · 2026-06-24 — v2b veri tamamlandı + replay + truncation fix
**B2 tam set:** 19.305/19.305 (grounded 15.458 / abstain 3.847, 0 boş). İİK **2.727**, Kat Mülkiyeti
**552** — topik-skew deliği kapandı. Assemble: **kept 18.670 / red 635** (630 "alıntı gold'da değil"
+ 5 atıf-no) = %3.3 deterministik ret.
**Replay:** kaynak `AlicanKiraz0/Turkish-SFT-Dataset-v1.0` (**MIT**), EDA: 5.579 satır, %99.8 TR,
0 İngilizce. Süzme → havuz 662 → **600 örnek** (token median 725) → mix'e **577 replay**.

**🔴 Uzun-madde truncation (smoke yakaladı):** `max_seq_len=2048` ile Unsloth **1.421/17.323 (%8.2)**
örneği "tüm label −100" diye düşürdü; toplam **2.010 (%11.6)** örnek >2048 = cevap kısmen kesik.
**Kök neden ölçüldü:** suçlu cevap değil — grounded answer token median **196** (max 873), ama
**kaynak bloğu median 1.030, max 12.805.** Tek bir maddenin tam metni 12K token olabiliyor.
**Çözüm: 900-char chunk clip** → %11.6 → **%0.03.** Gerçek RAG retriever tam kanunu değil **chunk**
döner; yani clip bir eval artefaktı değil, **üretimi simüle ediyor.**

### #16 · 2026-07-02 — ⭐ v2b tam eğitim BİTTİ + GOLD sızıntısı
**Eğitim:** lr=1e-4, r=16/α=32, all-linear, warmup=0.05, `--no-system`, 3e-4 yasak.
**1.083/1.083 step · 4h19m (12.72 s/it) · train_loss 0.30 · OOM/hata yok.**
Truncation fix teyit: **17.323 örnek / 0 düşürüldü.** Adapter 65.5M param / 262 MB.
*(Modal kart dersi: A100/H100 için hesaba kart eklemek şart — kredi olsa bile kapı.)*

**🔴 GOLD sızıntısı.** v2b bazı cevaplarda *"İlgili kaynak … GOLD metnidir"* diyor — ama öğrenci
context'te kaynakları `[KAYNAK N]` diye görür, "GOLD" diye etiket **yok**.
**Kök neden ölçüldü:** eğitim hedeflerinin **%5.7'si (990/17.323)** cevabında birebir "GOLD" taşıyor.
Suçlu teacher prompt'u: talimat baştan sona "GOLD" sözcüğünü kullanıyor ve gold kaynağı teacher'a
`GOLD madde (…)` diye etiketle veriyor. **Teacher iç-jargonu öğrenci çıktısına sızdı.**
**Ders:** teacher, öğrencinin gördüğü **etiket uzayında** promptlanmalı.

**🔑 Retriever-kalitesi ayrımı (kavramsal netleşme).** Model = RAG'ın **generator** yarısı; işi
"verilen chunk'ta cevap varsa dayan, yoksa çekin". Clip yöntemi = **simüle edilen retriever kalitesi**:
first-900 clip = *aptal retriever* (ilgili fıkra ortadaysa kaçırır → modeli olduğundan kötü gösterir);
**answer-anchored pencere** = *akıllı retriever* → modelin gerçek grounding yeteneğini ölçer.
**M1 çekinme teşhisi (n=30):** 6 abstain → **3 haklı** (benchmark kötü soru↔madde eşleşmesi),
**2 over-refusal**, **1 clip kurbanı.** → clip baskın değil.

**D1 · 6-mod canon sonucu (n=40/35/30):**

| Mod | Eksen | **v2b** | base | v1 |
| :--- | :--- | ---: | ---: | ---: |
| M1 gold+distractor | A1 (cevaplanan) | **0.904** | 0.879 | — |
| M2 TRAP (yanlış kaynak) | A3 Rej\* | 0.346 | 0.786 | 0.000 |
| M2b distractor-only | A3 Rej\* | **0.96** (n=30) | — | — |
| M3 boş kaynak | A3 Rej\* | **1.000** | 1.000 | — |
| M4 temiz oracle | A1 | **0.975** | 0.977 | 0.960 |
| M5 KÖR | A2 | **0.175** [.075,.30] | 0.225 | 0.300 |

**Manşet:** v2b **tüm kapıları geçti.** **⭐ Off-distribution dersi:** M2-oracle 0.346, v2b'yi
**eğitilmediği tek-kaynak promptunda** ölçtü; training-matched **M2b = 0.96.** Deployment RAG
çok-kaynak → 0.96 **adil A3**, 0.346 cross-mode artefaktı. Abstention v1 0.000 → **0.96 dirildi.**
**A1 çekinme ayrımı:** çekinme faith=0 alıp micro'yu çeker (ham 0.737); cevaplanan-only kuralıyla
gerçek **0.904.**
**Product A teyidi:** M4 oracle 0.975 vs M5 blind 0.175 = **%80 uçurum** → bilgi ağırlıkta değil.

---

# IV. v2c — düz SFT'nin duvarı (K3)

### #17-19, #21 · 2026-07-02 — v2c hazırlığı
**Register ölçümü:** v2b M1 üzerinde `register_mean` **1.000**, expert_frac **1.000**,
citizen_frac **0.000** — 40/40 satır `expert_hits ≥ 1` (min 1 · medyan 3 · max 5), citizen_hits=0.
**Regresyon alt-sınırı.** ⚠️ Proxy leksik; kanonik metrik LLM-judge rubriği (hâlâ açık).

**Position-bias: yok.** Gold `[KAYNAK n]` dağılımı **{1:9, 2:9, 3:9, 4:9, 5:4}** (40/40 eşleşti)
→ 5 slota düzgün yayılmış; "gold hep aynı slotta → etiket ezberi" maskesi de dışlandı. Kod değişmedi.

**GOLD-scrub:** ölçülen sızıntı **1157/19305 = %5.99** (tahmin %5.7'yi doğruladı). Baskın kalıplar:
"GOLD metnidir" 603 · "GOLD madde metnidir" 94 · "GOLD maddesidir" 28 · "GOLD kaynağıdır" 27.
Sıralı regex → **1157 → 0**, cümleler korundu. Teacher prompt'una yasak eklendi.

**core_hard kötü eşleşme:** kesin vaka **#28 & #29** (ikisi Kat Mülkiyeti Md4'e bağlı, gold "ortak
yerler" tanımı; sorular uyumsuzluk-yaptırımı/pay-iptali = ilgisiz). Kaldırma **ertelendi** —
şimdi düzenlenirse koşan batch elmayla-elma olmaktan çıkar.

**v2c verisi.** ⭐ **Türk hukuk metni sayıları KELİME yazar:** digit-regex counterfactual olgusu
grounded'ın yalnız **%0.3'ünü** (49/15447) tuttu; kelime-sayı desteği ("otuz gün", "yüzde yirmi")
eklenince tespit **%17.6'ya** çıktı.
**Kompozisyon:** grounded 14.742 (76%) · counterfactual 716 (3.7%) · abstain 2.339 (12%) ·
abstain_trap 1.508 (7.8%) → abstain+trap **%19.9**, trap/abstain **39/61**.
**gen_answers API maliyeti = $0** (14.742 grounded'ın hepsi v2b'nin scrub'lı cevaplarından reuse).
**Assemble:** kept 18.701 / red 604 (601 quote + 3 atıf) — red'lerin **tamamı grounded**, CF'te 0,
trap'te 0. train **17.353** / val 963 / test 963.

### #20, #22-23 · 2026-07-02 — base vs v2b vs Mecellem tam tablo

| Mod | Eksen | **base** | **v2b** | **Mecellem** |
| :--- | :--- | ---: | ---: | ---: |
| **M1** | A1 @ coverage | 0.886 @ **47.5%** (19/40) | **0.920 @ 72.5%** (29/40) | 0.918 @ **35.0%** |
| **M4** | A1 oracle @ cov | 0.983 @ 95% | 0.975 @ **100%** | 0.921 @ **45.0%** |
| **M2** | yanlış-kaynak red | **0.704** | **0.346** ❌ | 1.0\* |
| **M2b** | RAG-ıska red | 1.0 (n=40) | 0.96 (n=30) | 0.919 |
| **M3** | boş-kaynak red | 1.0 | 1.0 | 1.0 |
| **M5** | KÖR (düşük=iyi) | 0.225 | 0.175 | **0.35** |
| **A4** | cit_precision | 1.0 | 0.931 | — |
| **register** | expert_frac | 1.0 | 1.0 | **0.2** (mean 0.6) |

**🔑 Üç ana bulgu.**
1. **base BÜTÜN over-refuse ediyor** — M1'de gold prompt'ta VAR ama base **21/40 = %52.5**
   *"Verilen kaynaklarda bu konuyu düzenleyen madde bulunmuyor"* diyor. Gerçek red, regex artefaktı
   değil (spot-check teyitli). v2b %27.5.
2. **base'in yüksek M2/M2b/M3'ü bu körlüğün YAN ÜRÜNÜ** — yanlış kaynağı da reddediyor çünkü
   her şeyi reddediyor. base M2=0.704 "iyi kalibrasyon" değil **kör red** — ama geçilmesi gereken sayı yine bu.
3. **v2b'nin tek gerçek açığı M2=0.346.** Bilgi (M4 ~0.98 ikisinde) eşit → fark tamamen **davranışsal.**

**🔧 Mecellem checkpoint'i SIFIR `lm_head` taşıyor.** İlk çıktı garbage ("!!!!"). Tanı:
`lm_head.weight std = 0.0`, `embed_tokens std = 0.0245` (sağlıklı). Config `tie_word_embeddings=True`
diyor ama checkpoint ayrı (sıfır) bir head de taşıdığı için transformers tie etmiyor → tüm logitler eşit.
**Fix:** yüklemeden sonra `lm_head.weight = embed_tokens.weight` elle bağla.
**Metodoloji notu:** rakibi kırık kurup "biz kazandık" demek geçersiz olurdu.

**⚠️ M2 = 1.0 yorumu.** Mecellem'in 1.0'ı mükemmel kalibrasyon **değil** — coverage çöküşünün diğer
yüzü (M1 cov %35, M4 %45). Aynı mekanizma base'in M2b=1.0'ında da var.
**Trade-off bulgusu:** yanlış-kaynak reddi ↔ coverage gerilimi. Rakip "hepsini reddet" köşesinde,
v2b "yanlışı da cevapla" köşesinde. **M2'yi tek başına kıyaslama; M2 × coverage birlikte oku.**

**Mecellem künyesi (arXiv 2601.16018):** Qwen3-4B, tek-fazlı **CPT 270.8B token**, instruction-tuned
**DEĞİL** → completion-style few-shot kurulumu doğru. **Onların eval'i yalnız perplexity** (%36.2
düşüş) + MTEB-TR retrieval; hiç QA/grounding/abstention eval'i yok → **generatif eksende ilk ölçen biziz.**

### #24 · 2026-07-03 — ⭐⭐ v2c TAM SKORKART + ❌ RED + K3

| Eksen | base | v2b | Mecellem | **v2c** | Kapı | Sonuç |
| :--- | ---: | ---: | ---: | ---: | :--- | :--- |
| M2 yanlış-kaynak red | 0.704 | 0.346 | 1.0\* | **0.407** | ≥0.90 | ❌ birincil çöktü |
| M1 grounding A1 @ cov | 0.886@47.5% | 0.920@72.5% | 0.918@35% | **0.832@80%** | ≥0.904 | ❌ regresyon |
| M4 oracle | 0.983 | 0.975 | 0.921 | **0.977** | ≥0.975 | ✅ |
| M2b RAG-ıska red | 1.0 | 0.96 | 0.919 | **0.973** | ≥0.96 | ✅ |
| M3 boş-kaynak red | 1.000 | 1.000 | 1.000 | **1.000** | 1.0 | ✅ |
| M5 KÖR (anti-hedef) | 0.225 | 0.175 | 0.35 | **0.125** | base-altı | ✅ |
| register | — | 1.0 | — | **1.0** | koru | ✅ |

**RED gerekçesi:** iki bağımsız kapı birden düştü — birincil hedef M2 = 0.407 « 0.90 (v2b'den
yalnız +0.06, base'in altında) **ve** regresyon M1 = 0.832 < 0.904.

**🔴 K3 NEGATİF BULGU.** *"M2 reddi ucuz SFT counterfactual + abstain_trap ile öğretilir"* hipotezi
**çürüdü.** Tier A veri-kolu M2'yi 0.346 → 0.407'ye taşıdı, üstelik M1'i 0.920 → 0.832 düşürdü.
**Mekanizma = "Grounding-Abstention paradoksu":** SFT modeli cevap-üretmeye koşulladı → coverage ↑
(47.5 → 80%, over-refusal ↓ **iyi**) ama near-miss **ayrım gücü** köreldi. Hukukta yüksek semantik
örtüşme → konusal-komşu yanlış kaynak latent-space'i aktive edip fabrikasyona sürüklüyor
(**27 tuzağın 16'sı**); bariz off-topic (M2b) tetiklemediği için reddediliyor.
→ **near-miss discrimination SFT-tek-başına çözülemez.**

---

# V. v3 — ORPO ve kısmi onarım

### #25 · 2026-07-03 — Near-miss trap havuzu + EVAL-AYNASI kararı
İlk kod tuzak sertliğini **soru**-örtüşmesine çıpalıyordu; ölçüldü → eval ile örtüşmüyor:
`ov_gold` med **0.047**, eval-med üstü kapsama **%6.6** = eğitim negatifi eval'den **kolay**.
**Düzeltme: EVAL-AYNASI** — aynı kanunun tüm kardeşleri içinden gold'a **max Jaccard** (eval ile birebir).

| dağılım | med | p90 | eval-med üstü kapsama |
| :--- | ---: | ---: | ---: |
| Eval M2 `_overlap` (n=35) | 0.123 | 0.253 | — |
| v3 `ov_gold` (n=19.284) | **0.141** | **0.277** | **%66.3** (önce %6.6) |

**Geçerlilik ekseni ayrıldı:** `ov_gold` = **sertlik** (yüksek = zor = istenen). "Yanlış madde
soruyu gerçekten cevaplıyor mu?" lexical ile ölçülemez → **semantik judge'a** taşındı.
Gözle doğrulama: yüksek-örtüşmeli çiftler (CMK 140 teknik-izleme vs CMK 135 iletişim-tespiti;
TCK 197 sahte-para vs TCK 199 kıymetli-damga) farklı hüküm → **yüksek lexical örtüşme ≠ cevaplıyor.**

### #26 · 2026-07-04 — 🔴 FRAMING keşfi + mojibake
**Bulgu-3 (kritik): eval M2 = ORACLE framing.** Rejected üretimi için v2b çok-kaynak framing'de
koşturulunca **%85 çekindi** (fab 0.15). Eval M2 detayı okununca sebep çıktı: eval M2 **tek-kaynak
oracle** framing kullanıyor ("çekimser kal" **demez**), çok-kaynak RAG_MULTI değil. Oracle'a geçince
v2b **fab = 0.79-0.875.**
→ v3 abstain çiftleri **oracle** framing kullanır; grounding-replay RAG_MULTI kalır. Karışık framing
bilinçli — **her çift kendi sınav moduna eşlenir.**
**Paper notu:** train/eval framing uyumsuzluğu = v2b'nin zayıf M2'sinin (0.346) muhtemel ek sebebi.

**Mühendislik:** lokal RTX 5070'te 12B-4bit greedy ~**30 s/örnek**, batching kırmadı → Modal'a taşındı.
**Mojibake bug'ı:** batched left-pad'de `pad_token=eos` baş-token bozuyor ("Eğer"→"트에ğer"),
**batch=8'de %26**, tekilde %0. Fix: gerçek `<pad>` (id 0).

### #27 · 2026-07-05 — Harvest KOŞTU (K3 funnel)
**Modal kalıbı düzeltmesi:** sade `.spawn()` + `--detach`siz → ephemeral app kapanınca job **iptal**.
Doğru kalıp: `modal run --detach … ::harvest_rejected`.

| ölçüm | değer |
| :--- | ---: |
| toplam üretilen | 1.728 |
| **fabrikasyon** | **1.504** |
| çekimser | 224 |
| **fab oranı** | **0.870** |
| baş-mojibake (pad-fix sonrası) | 4/1504 = **%0.3** |

→ **K3 funnel ölçekte doğrulandı:** v2b, "makul komşu yanlış madde + oracle framing"de **%87 uyduruyor.**
(n=24 smoke tahmini 0.79'du; tam koşuda 0.870.) **pad-fix tuttu:** %26 → %0.3.

**ORPO paketleme:** abstain çifti (is_pref=1) **1.495** · grounding-replay (is_pref=0, frac 0.20) **299**
→ toplam 1.794 → **train 1.741 / validation 53.** interleave_step 6. Elenen: 224 kontrast-yok + 9 dev.
hi_overlap 108 (dahil).

### #28-29 · 2026-07-05 — Genelleme dilimleri + 🔴 OOD bloğu
**`trap_xkanun.jsonl` (35):** çapraz-kanun near-miss; 35/35 benzersiz, **sızıntı 0** (2.914 yapısal
çift + 14.618 metin anahtarı), `_overlap` med **0.103**, tek-kanun cap 7, **27 farklı tuzak-kanun**.
Geçici-madde guard eklendi (17/1022 soru etkilendi).

**🔴 OOD BLOKLU (paper-değerli sınır bulgusu):** held-out kanunlar için **hiç soru yok.**
Madde havuzu **892 kanun**, soru kaynağı yalnız **11 kanun** — ve bu 11, eğitimde görülen 11'le
**birebir aynı** (`test_laws == seen_laws`).
→ **Mevcut eval'imiz eğitimle özdeş 11 kanuna hapsedilmiş.**

**Blok AÇILDI (#29):** 7 held-out kanun × 5 soru = **35** — 2918 Karayolları Trafik · 5510 SGK ·
6458 Yabancılar · 5846 FSEK · 6769 Sınai Mülkiyet · 5275 İnfaz · 1136 Avukatlık.
Yöntem: gerçek held-out madde → grounded Q&A → faithfulness hakemi (`doğruluk ≥8 ∧ cevaplanabilir ≥8`,
2 aday düştü) → eval-mirror max-Jaccard tuzak. **Sızıntı 0**, join 35/35, `_overlap` med **0.131**
(0.064-0.554). **GPT maliyeti $0.0107.**

**Defer (gereksinim yazıldı):** **temporal** — ham şema `{kanun_adi, kanun_no, madde_no, text}`,
yürürlük tarihi/versiyon/mülga-flag alanı **yok** (serbest metinde "mülga" **4.828**, "(Değişik"
**4.879**, parse edilmemiş). **çok-hop** — **6.772** madde içi-atıf içeriyor ama ağırlıkla değişiklik
gürültüsü; temiz graf değil. Guardrail: *temiz kurgu çıkmadıysa uydurma dilim ÜRETME.*

### #30 · 2026-07-05 — ⭐ ORPO eğitim BİTTİ: forget yok, M2 öğrenildi
`--epochs 2 --beta 0.1 --lr 1e-5 --save-steps 28` · **56/56 step, 2 epoch** · crash/OOM/NaN yok.
Efektif batch 64. Base = **v2b-continuation** (v2c'yi değil — o başarısız yan-daldı).

| step | epoch | nll_loss | | step | margins | accuracies |
| ---: | ---: | ---: | :-- | ---: | ---: | ---: |
| 5 | 0.18 | 7.645 | | 5 | −0.3123 | 0.1562 |
| 10 | 0.37 | 6.394 | | 15 | −0.1635 | 0.1844 |
| 15 | 0.55 | 5.385 | | 40 | −0.02354 | 0.1688 |
| 20 | 0.74 | 4.646 | | 50 | **+0.02627** | **0.2281** |
| 40 | 1.44 | 3.147 | | 55 | −0.007193 | 0.1906 |
| 50 | 1.81 | 2.970 | | | | |
| 55 | 1.99 | **2.956** | | | | |

nll **7.645 → 2.956** monoton → **v2b grounding'i korundu** (v2c'yi öldüren forget bu koşuda yok).
margins **−0.31 → ~0**, log_odds_ratio **−4.789 → −1.319.** val: eval_loss 3.364, acc 0.125,
margins −0.047.
**NET: nll düşerken (grounding korunuyor) margin/accuracy yükseldi (abstention öğreniliyor).**
İki checkpoint saklandı: final (2 epoch) + checkpoint-28 (~1 epoch).

### #32 · 2026-07-06 — ⭐⭐ v3 SONUÇ: KISMİ + M2b regresyon teşhisi

| Eksen | base | v2b | v2c ❌ | **v3** | Kapı | Sonuç |
| :--- | ---: | ---: | ---: | ---: | :--- | :--- |
| **M1** grounding A1 | 0.662 | 0.737 | 0.681 | **0.881** | regresyon yok | ✅ base'i de geçti |
| **M4** oracle | 0.978 | 0.968 | 0.974 | **1.000** | tavan koru | ✅ |
| **M2** yanlış-kaynak red | 0.704 | 0.346 | 0.407 | **0.593** | ≥0.704 | ❌ base-altı |
| **M2b** çok-kaynak ıska | 1.0 | 0.96 | 0.973 | **0.529** | tavan koru | ❌ **REGRESYON** |
| **M3** boş bağlam | 1.0 | 1.0 | 1.0 | **1.000** | tavan koru | ✅ |
| **M5** kör (anti-hedef) | 0.225 | 0.175 | 0.125 | **0.075** | base-altı | ✅ |
| **register** | 1.0 | 1.0 | 1.0 | **0.975** | koru | ✅ |

**1-epoch (ck28) vs 2-epoch:** M2 0.519 → **0.593** · M1 0.899 → 0.881 · register 1.0 → 0.975.
**Final tercih edildi.**

**Genelleme (held-out):** xkanun base 0.968 / v2b 0.387 / **v3 0.656** · ood base 0.889 / v2b 0.115 /
**v3 0.483.** Örüntü tutarlı: **v3 ≫ batık-SFT her yerde · v3 < base her yerde · OOD en kırılgan**
→ *ilke değil kalıp.*

**Proxy → judge farkı (metodolojik ders):**

| dilim | ham proxy | kalibre | **gerçek judge** |
| :--- | ---: | ---: | ---: |
| m2_v3 | 0.429 | ~0.55 | **0.593** |
| m2_v3ck28 | 0.400 | 0.52 | **0.519** 🎯 |
| xkanun_v3 | 0.657 | 0.79 | **0.656** (judge ≈ ham) |
| ood_v3 | 0.286 | 0.39 | **0.483** |
| ood_base | 0.686 | 0.82 | **0.889** |

**Neden judge ≥ proxy:** (1) **semantik red** — proxy keyword'süz reddi kaçırır; (2) **invalid-trap
paydası** — proxy ham 35'e böler, judge geçerli tuzağa böler (m2_v3'te 27 valid); (3) **kalibrasyon
transfer etmedi.** **Ders: ham proxy güvenilir TABAN; kalibre sabiti slice-family'ye özel, taşınmaz.**

**🔬 M2b REGRESYON — kök teşhis.** v3, **34 geçerli tuzağın 16'sında FABRICATE** etti.
Fabrikasyon örüntüsü **birebir aynı:**
> *"İlgili kaynak, KAYNAK 3'tür çünkü bu kaynak … içermektedir. Diğer kaynaklar … elenmiştir."*

**Mekanizma:** ORPO'nun muhakemeli-red şablonu modele *"kaynakları değerlendir → en ilgilisini SEÇ"*
adımını öğretti. M2'de (tek yanlış kaynak) doğru; **M2b'de (çok distractor, doğrusu yok)** aynı
"seç" refleksi ateşleniyor → "hiçbiri değil → reddet" yerine en yakın distractor'ı seçip bağ uyduruyor.
**Ders: abstention tek beceri değil AİLE.** Bir aileyi eğitmek diğerini garanti etmez, **bozabilir.**
Eval'in mod-ayrışması (M2/M2b/M3) tam bu yüzden vazgeçilmez.

---

# VI. v4 tasarımı (koşulmadı) ve çerçeve değişimi

### #31 · 2026-07-06 — Mecellem konumlama

| Eksen | base | v2b | v2c ❌ | Mecellem | **v3** |
| :--- | ---: | ---: | ---: | ---: | ---: |
| M4 oracle | 0.978 | 0.968 | 0.974 | **0.783** ↓ | **1.000** 🏆 |
| register | 1.0 | 1.0 | 1.0 | **0.2** ↓↓ | **0.975** |
| M2b | 1.0 | 0.96 | 0.973 | 0.919 | **0.529** ⬇ |
| M3 | 1.0 | 1.0 | 1.0 | 1.0 | **1.000** |
| M1 | 0.662 | 0.737 | 0.681 | 0.713 | **0.881** 🏆 |
| M2 | 0.704 | 0.346 | 0.407 | **1.0\*** | **0.593** |
| M5 (düşük=iyi) | 0.225 | 0.175 | 0.125 | **0.35** | **0.075** |

**B1 — İki farklı makine.** Biz = grounding + register makinesi; Mecellem = parametrik-ezber makinesi.
Güçlü/zayıf yanlar **simetrik.**
**B3 — Mecellem'in M5 üstünlüğü borç, varlık değil.** 270B token'a gömülü statik bilgi; mevzuat
değişince **yanlışa döner.** Biz o bilgiyi çıkarımda RAG ile kiralıyoruz.
**B4 — M2 = 1.0 yanlış yıldız.** M2 ile M4 birbirini çeker; 1.0'ın en kolay yolu aşırı reddetme.
Ayrıca sette **invalid trap** var (base'te 27/35 valid) → mükemmel kalibre model 1.0 *almamalı*.
**Hedef 1.0 değil: M2 ≥ 0.704 + M4/register korunmuş.**
**B5 — CPT ekonomisi asimetrik.** ~270B token / GPU-ayları vs QLoRA ~milyon token / A100-saatleri —
**3-4 büyüklük mertebesi.** CPT'yi geçmeye çalışmak "ucuz" değer önermesini siler.
**Doğru hamle:** o sahayı **RAG ile alakasızlaştır**, kendi sahamızda bileşik üstünlüğü büyüt.

### #33 · 2026-07-06 — v4 tasarım tezi: tek answerability-dedektörü
**Tez:** CANON'daki 9 ölçüm ayrı hedefler değil, çoğunlukla **tek latent beceriye** iner.
*Grup 1* (cevap var → kullan): M4, M1. *Grup 2* (cevap yok → reddet): M2, M2b, M3, xkanun, ood.
İkisi **aynı becerinin iki yüzü** = *"verilen bağlam bu soruyu cevaplıyor mu?"* — **answerability
discrimination.** Register ortogonal; M5 = üçüncü beceri değil, **iyi ayrımın gölgesi.**
**Çıkarım:** tek becerinin iç takası olmaz → **"grounding-abstention frontier" doğa kanunu DEĞİL**,
mevcut dedektörün **kusur artefaktı.** base = "her şeyi reddet" köşesi; Mecellem = "hep ezberden
cevapla" köşesi; biz = merkezdeki gerçek dedektör.
**Kabul edilen aksiyomlar:** mutlak mükemmellik hedef değil (**~0.90 yeterli**) · anlamlı hedef
**"berabere-tavan VEYA lider"** · 1 numaralı kaldıraç **veri kompozisyonu** (algoritma değil).

### #34 · 2026-07-06 — v4 deep-research: DTA / Sufficient-Context sentezi
16 kaynak, 70 iddia → 23 confirmed / 2 killed.
**⭐ Baş bulgu: M2b regresyonumuz İSİMLİ, GENEL bir başarısızlık modu — bug değil.**
- **Sufficient Context (ICLR 2025):** RAG paradoksal olarak abstention'ı **bastırır** — bir frontier
  modelin abstain oranı RAG'la **%84.1 → %52.** *Tam bizim M2b'miz (0.96 → 0.53).*
- **RefusalBench:** çok-belge reddi tek-belgeden dramatik zor — **tüm frontier modeller multi-doc'ta
  <%50**; bir model tek→çok belgede **73.0 → 36.1** çöküyor. → v3 regresyonu **yapısal-genel.**
  *(Yan sonuç: base'in M2b=1.0'ı, frontier bile %50 yapamazken, kesin **over-refuse**.)*

**Soru-1 · ölçek ⚠️ TEZ DÜZELTİLDİ.** DTA 10.000 çift kullanıyor (bizde 1.741) **ama ham ölçek tek
başına çalışmaz:** optimal çift *iyi-ayrık ama maksimal-ayrık değil*; küçük marjlı çiftler underfit
(%34.6 vs %48.2). → **"veri ölçeği 1 numara" eksikti; doğrusu "kurgu-kaliteli ölçek."**
**Soru-2 · gold-absent oranı TUNED knob.** DTA IDK-ratio ~0.7 optimum; **✘✘'i tamamen çıkarınca
abstention SIFIRA çöküyor** (bizim v3'ün tam hikâyesi). RAFT'ta gold oranı veri-setine bağlı
(%40-100) → evrensel sabit yok. Bizde sweep **0.3-0.5** (grounding tacını koruma önceliği).
**Soru-3 · OOD.** Abstention-SFT domain-ötesi kötü genelliyor; **DTA bile refusal örüntülerini
ezberliyor.** ERA OOD Answer-F1'i **2×**'liyor. → OOD zayıflığımız (0.483) **bilinen kusur.**
**Soru-4 · zemin.** DTA'da chosen'a **auxiliary SFT-loss ŞART** — çıkarınca answer-quality
**63.7 → 38.8.** **ORPO bunu doğuştan yapıyor** → mimarimiz zaten doğru; continuation kalır.
**Soru-5 · chosen yapısı.** CoT-chosen düz cevabı yeniyor (+9.66 / +14.93). **Fix keskinleşti:**
*"en ilgili kaynağı SEÇ"* (forced-selection bug'ının kökü) → **"herhangi bir kaynak yeterli mi?
değilse IDK"**; gold-absent çiftlerde **doğru cevabı rejected'a koy.**
**Soru-6 · DTA dört-kadran = çekirdek mekanizma.** RAFT modeli üstüne uygulanınca
**abstain-F1 0.0 → 63.3, acc 42.2 → 64.1 — grounding'i çökertmeden.**
**Frontier notu:** *"hiçbir frontier ikisinde birden >%80"* iddiası adversarial-refuted →
**doğa kanunu değil**; ama ampirik olarak henüz kimse yapmamış → hedefimiz **iddialı ama duvar değil.**

### #35 · 2026-07-08 — Dış benchmark manzarası
BigLaw-Bench / LegalBench / LEXam = İngilizce + common-law → **off-axis, yorumlanamaz** → cite-only.
**TR'de üretken grounding/abstention benchmark'ı YOK** (mevcut setler genel-MC ya da encoder cloze)
→ **boşluk = katkımız.** `alibayram/turkish_mmlu` **CC BY-NC + telif beyanı** = poison, dışarıda.
**NewMind stack:** Mursit = retriever ailesi (Faz-2 adayı) · Mecellem = CPT foundation (koşuldu) ·
**Muhakim = reward/judge** (Skywork-Reward-V2-Llama-3.1-8B, 5 eksen) → **cite-only**, çünkü hakem
geçerliliği cross-family panelle karşılanıyor **ve** Muhakim reddettiğimiz `EuroHPC-Legal` ile
eğitilmiş (kalibrasyon kirliliği).
**Compute/grant istihbaratı:** NewMind MareNostrum 5'i EuroHPC project + TRUBA ile kullanmış —
grant, cepten para değil. Bize açık yollar: TRUBA (yerli, en gerçekçi) · MN5 ulusal çağrı
(özel-sektör PI **kabul**, kurumsal e-posta zorunlu). ⚠️ Zayıf noktalar: HPC track-record yok +
12B QLoRA tek GPU → pre-exascale'i hak etmiyor. **Faz-1 için gereksiz.**

### #36 · 2026-07-17 — ⭐⭐⭐ Tez çerçeve değişimi: maliyet-normalize parite
İçeri dönük (*"FT base'i geçiyor mu?"*) → **dışarı dönük** (*"kapalı ticari modellerin dağıtım
sınıfına maliyet-normalize paritede ne kadar yaklaşıyoruz — ve ne kadarı FT, ne kadarı harness?"*).
v0→v3 = **proof-of-concept / FT kolu.** Benchmark birincil katkı olmaktan çıkıp **ölçüm altyapısı** oldu
(parite bir **eşdeğerlik** iddiası; eşdeğerlik testi fark testinden çok örnek ister).
Rakip = dağıtım sınıfı kapalı modeller + tavan referansı. 8 GB **soft gate.**
**Harness dilimi teze DAHİL, graph-RAG hariç** (sonradan ADR-0022 ile revize).
2×2+E ızgarası; **E = base+harness = ana ablasyon.**

### #37 · 2026-07-23 — Base kararı sunk-cost sıfırlanarak yeniden açıldı
Karar **değişmedi ama gerekçe değişti.** Ölçülenler: 8 GB'da bağlam tavanı **176.128 vs 90.982 token**
(~1.9×) · KV @128K **1.16 GB** vs ağırlık ~6.5 GB → **KV, ağırlığın %18'i, darboğaz AĞIRLIK**
(ADR-0018'in tersi) · multimodal gerekçesi **ağırlıkla çürütüldü** (audio = **1 tensör / 2.46M param**,
vision 49.9M, decoder 11.91B → **korunacak encoder yok**).
**⚠️ Kendi iddiam çürütüldü:** *"18× KV avantajı"* yanlıştı (rakip ailenin **hibrit öncesi**
mimarisinden geliyordu); gerçek fark **2.5-3.7×.**
**Lisans dipnotu:** Gemma 4 gerçekten Apache-2.0 **ama** üstüne Prohibited Use Policy katmanlı.

### #38 · 2026-07-24 — ⭐⭐ llama.cpp hattı + SESSİZ ŞABLON TUZAĞI
**1. CUDA link hatası** (script'in `tail -5`'i asıl satırı gizliyordu): `libggml-cuda.so`
sistemde olmayan CUDA kütüphanelerine referans veriyor → ~200 `undefined reference`.
Fix: `-L$CUDA_HOME/lib -Wl,-rpath,$CUDA_HOME/lib` (rpath **çalışma anı** için de şart). sm_120 çalışıyor.

**2. ⭐⭐ Sessiz şablon tuzağı — bir CANON koşusunu fark edilmeden çöpe çevirecekti.**
Belirti: model **hiç durmuyor**, cevaptan sonra kendi kendine soru-cevap oynuyor (`finish_reason=length`).
Kök neden: resmî şablon, düşünme kapalıyken üretim isteminin sonuna **boş bir düşünce kanalı**
iliştiriyor; llama.cpp'nin **minja** motoru tanımsız `enable_thinking`'i "tanımlı ve doğru" sayıyor
→ sonuç tersine dönüyor (sistem turuna `<|think|>` **giriyor**, ön-doldurma **yazılmıyor**).

| istem biçimi | çıktı | duruş |
| :--- | :--- | :--- |
| yamasız | `<\|channel>` açıp girdiyi tekrarlıyor | `limit` |
| **ön-doldurmalı** | **doğru cevap** | **`eos`** ✅ |

**Model, GGUF ve saf Q4_0 SAĞLAM** — hata tamamen araç tarafında (`--pure` şüphe altındaydı, **aklandı**).
**Neden *sessiz*:** hiçbir aşamada hata yok — server açılıyor, 200 dönüyor, JSON geliyor; sadece
**içerik** bozuk. Regex omurgası bu çıktılar üzerinde **sayı üretir ve tablo dolar.**
> **Dosya-okuma kanıtı:** `--chat-template-file` gerçekten okunuyor — sahte işaret şablonuyla test
> edildi. *"Bayrak sessizce yok sayılıyor"* ihtimali elendi.

**3. ⭐ Çekimserlik talimatı M4'ü kırıyor.** Kademeli izolasyon (aynı soru/kaynak, temperature=0):

| sistem istemi | cevap |
| :--- | :--- |
| A) yok · B) sadece rol · C) + "yalnızca kaynağa dayan" | ✅ doğru |
| **D) + "kaynakta yoksa 'yer almıyor' de"** (CANON istemi) | ❌ **yanlış çekimser** |

Tetikleyen tek bileşen **çekimserlik talimatı.** Bu araç hatası değil, **ölçülecek davranış** —
Grounding-Abstention paradoksunun base modeldeki karşılığı. ⚠️ n=1 anekdot, sayı olarak raporlanmaz.
**Açılan protokol borcu: düşünme modu kararsız** — düzeltmemiz reasoning'i **kapatıyor**; bu eksen
e2e sayıları ve **rakip adaleti** için kritik.

**4. VRAM: gerçek > projeksiyon.** Projeksiyon 6.97 GB vs ölçüm **7.86-8.52 GiB**
(⚠️ kirli ölçüm — paralel iş vardı). Fark compute buffer + CUDA bağlam ek yükünden.
Boştaki masaüstü bile karttan **1.2 GB** yiyor (12226 toplam / 11026 boş) → **8 GB kartta 12B için
pratikte yer yok.** Üretilen artefakt `g4-12b-q4_0-pure.gguf` = **6.26 GiB** (referansla birebir).
Hız ~22-48 tok/s (gösterge).

---

## Paper eşlemesi

**K1 — ablasyon.** base → +SFT → +oracle tablosu. ⚠️ Faithfulness'la ölçülürse "+SFT" satırı
**boş çıkar** (tavan); SFT katkısını wrong_ref / hedge / format eksenlerinde göster.

**K3 — ayrışma ve negatif bulgular.** (a) v0 forum çöküşü (154× ezber) · (b) KÖR-vs-oracle:
parametrik madde-no ezberi imkânsız, oracle tavanı SFT'yi faithfulness'ta gereksizleştiriyor ·
(c) etiketsiz chunk → uydurma atıf · (d) **Grounding-Abstention paradoksu** (v2c) ·
(e) **M2b forced-source-selection** (v3) — *"preference-opt tek-aile negatifle eğitilince komşu aile
abstention'ı bozabilir"* · (f) **frontier kusur-artefaktı tezi** (#33).

**Methodology.** Grounded veri imali · eğitim-öncesi kalite kapısı · dış-iddia import-doğrulama ·
eval-mirror ilkesi · mod matrisi (eval dağılımı = deployment dağılımı) · eval-aynası hard-negative
kalibrasyonu · proxy→judge transfer sınırı · rakibi düzgün kurma (lm_head fix) · araç-kaynaklı
sessiz bozulma yüzeyleri (#38).

**Limitations.** Oracle ≠ gerçek RAG · hakem = LLM, insan-κ descoped · eval kanun kapsamı =
train kanun kapsamı (OOD ile kısmen aşıldı) · n=40/35 pilot ölçek · dış geçerlilik (tek base).
