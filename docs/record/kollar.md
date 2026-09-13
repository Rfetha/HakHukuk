# Kol kaydı — her `τ_X` versiyonunun künyesi

> **Bu belge ne:** eğitilmiş her kolun (task-vector dalının) **tek kayıt yeri**. Bir artefakt
> diskte duruyorsa burada bir satırı vardır; satırı yoksa o artefakt **kimliksizdir ve kullanılmaz.**
>
> **Neden var:** bu hattın hata sınıfı sessiz yanlışlık. *"Bu sayı hangi kolun, hangi versiyonun
> sayısı"* sorusu **dosya adından** cevaplanabilmeli — o yüzden versiyon zincirin her halkasında
> taşınır: adaptör → merge → GGUF → eval etiketi.
>
> **Kural (2026-07-29):** repo dışı artefakt **yok**. Her şey repo kökü altında.
> Adaptörler git'te **değil** (`.gitignore: outputs/**/*.safetensors`, ayrıca 114 MB > GitHub'ın
> 100 MB dosya sınırı) ve **yedeklenmiyor** — bilinçli karar: adaptör veri + reçete + seed sabitken
> yeniden üretilebilir, yeri doldurulamaz varlıklar (veri · belgeler · eval çıktıları) zaten metin
> ve git'te. *(12B hattının adaptörleri bu kararın bedelini gösterdi: repo dışı devir paketi
> silindi, adaptörler kalıcı kayıp — kasıtlı, çünkü o hat emekli.)*

---

## ♻️ Yeniden üretilebilir artefaktlar — diskte tutulmaz (2026-08-03)

`models/merged/<ad>/` (bf16, ~8,8 GB/adet) **adaptör + base'den yeniden üretilir**:

```bash
python scripts/merge_lora.py --base Qwen/Qwen3.5-4B --adapter outputs/<kol> --out models/merged/<kol>
python scripts/merge_ties.py --base Qwen/Qwen3.5-4B --adapter tg=outputs/tg_v1 --adapter ta=outputs/ta_v1 \
       --no-norm-balance --out models/merged/tgta_v1     # ham TIES, ADR-0052
```

OSS geçişinde silinenler (~26 GB): `ta_v1` · `tg_ta_min` · `tg_ta_normdengeli` bf16
dizinleri. **GGUF'ları ve künyeleri duruyor** — ölçüm kaydı etkilenmedi.
Diskte tutulan: `tgta_v1` (yayımlanacak) · `tg_v1` (aktif kol).

**Asıl artefakt adaptördür** (`outputs/<kol>/`, ~114 MB) — o silinmez.

### 2026-09-13 — depo temizliği, 85 GB → 28 GB (~57 GB silindi)

Gerekçe [ADR-0075](../adr/kararlar-0064-0085.md#adr-0075) m.3'tür: ADR-0027'nin
task-vector/merge hattı `v1`'de **donduruldu** ve `v2`'ye taşınmıyor, dolayısıyla
norm-dengeleme ablasyonları **konusuz** kaldı. Sayıları bu belgede (:221-222) ve
[ADR-0052](../adr/kararlar-0045-0063.md#adr-0052) · [ADR-0053](../adr/kararlar-0045-0063.md#adr-0053)'te metin olarak duruyor.

**Diskte tutulanlar (v2/GRPO'nun ihtiyacı, ~19 GiB):** `models/merged/tgta_v1/` — ADR-0075'in
adıyla gösterdiği **GRPO başlangıç noktası** · `models/merged/tg_v1/` · GGUF olarak
`tgta_v1-q4_k_m` (yayımlanan artefakt, `sha256` silme sonrası yeniden doğrulandı:
`755e15e9…86e7bffc`, HF'teki dosyayla birebir) · `q35-4b-q4_k_m` (base kolu, M5/Kapı 6 çıpası) ·
`tg_v1-q4_k_m` · `ta_v1-q4_k_m` (B4 kol çıpaları).

**Silinen GGUF'ların künyesi** — dosya gitti, kimliği burada kalır:

| dosya | bayt | `sha256` | neden silindi |
| :--- | ---: | :--- | :--- |
| `tg_ta_min-q4_k_m.gguf` | 2.783.446.720 | `8fc3e5b0…dda02055` | merge ablasyonu, hat donduruldu |
| `tg_ta_nb-q4_k_m.gguf` | 2.783.446.720 | `f0a963cb…0b7b576e` | dejenere, koşu zaten geçersiz |
| `tg_ta_modulmin-q4_k_m.gguf` | 2.783.446.720 | `9c73bae0…02332a0c` | ADR-0053 ile reddedildi |
| `q35-4b-f16.gguf` | 8.665.620.192 | `20e59ec0…0fc4afee` | kuantizasyon zincirinin ara ürünü |
| `cp2s-ties-smoke-q4_k_m.gguf` | 2.783.446.720 | `7d6389d4…eeb11a66` | duman artefaktı, hiçbir belgede geçmiyor |
| `q35-4b-q5_k_m.gguf` | 3.161.425.632 | `733ff786…1462007a` | base kuantizasyon merdiveni, tablosu [#39](kronoloji-39-52.md#39)'da |
| `q35-4b-q6_k.gguf` | 3.563.028.192 | `e7a4a038…d308828c` | aynı |
| `q35-4b-q8_0.gguf` | 4.610.580.192 | `a831d9f3…ef97c6d6` | aynı |
| `tgta_v1-q4_k_m-20260912.gguf` | 2.783.446.688 | `9becf362…adb482d6` | S17 eğrisi; künyesi `outputs/eval/s17-kuantizasyon-egrisi/OZET.md`'de |
| `tgta_v1-q5_k_m.gguf` | 3.161.425.568 | `2afa0ea3…a0f6b8b0` | aynı |
| `tgta_v1-q8_0.gguf` | 4.610.580.128 | `a7991f36…58a1354b` | aynı |

Kısaltma baştan 8 + sondan 8 hane; bu dosyalar silindiği için tam değer başka bir yerde
tutulmuyor, kısaltılmış hâli kimliği ayırt etmeye yeter (tek istisna
`tgta_v1-q4_k_m-20260912`, tam `sha256`'sı `outputs/eval/s17-kuantizasyon-egrisi/OZET.md`'de).

Silinen iki bf16 dizini: `tg_ta_globalmin` (bu belgede **satırı hiç olmadı** — kendi kuralına
göre kimliksizdi; künyesi `outputs/eval/cp3f-modul-norm/KUNYE_globalmin.json`) ·
`tg_ta_modulmin` (ADR-0053). Her ikisinin eval çıktısı `outputs/eval/` altında duruyor.

⚠️ **Yeniden üretilebilirliğin ölçülmüş sınırı:** yayımlanan `Q4_K_M`, bugünkü araç zinciriyle
`models/merged/tgta_v1/`'den **bayt-bayt üretilemiyor** (−32 bayt, farklı `sha256` — S17
BULGU-G). O yüzden `tgta_v1-q4_k_m.gguf` yeniden üretilebilir sayılmaz ve silinmez;
yedeği HF'teki pinli revizyondur (`hakhukuk/indir.py`).

---

## Adlandırma

```
outputs/<kol>_v<N>/                      LoRA adaptörü        (asıl artefakt)
models/merged/<kol>_v<N>/                merge edilmiş bf16   (yeniden üretilebilir)
models/gguf/<kol>_v<N>-<QUANT>.gguf      taşıyıcıya giden     (yeniden üretilebilir)
eval etiketi: <mod>_<kol>_v<N>           ör. m1_tg_v1
```

**Kol kısaltmaları:** `tg` = `τ_grounding` · `ta` = `τ_abstention` · `base_a` = Taban A (karışık SFT) ·
`base_b1`/`base_b2` = Taban B'nin iki aşaması (ardışık SFT).

**Yeni versiyon ne zaman açılır:** eğitim rejiminde (veri · adım · lr · `r`/`alpha` · dropout ·
`target_modules` · precision · seed) **herhangi bir** değişiklik. Rejim aynıysa yeni versiyon
açılmaz — aynı artefakttır.

> ⚠️ **Versiyon karıştırma = merge geçersizliği.** `τ = θ_ft − θ_base` tanımı bütün kolların
> **aynı θ_base**'den ve **eşleşen rejimden** gelmesini şart koşar (`TASARIM.md` §4.1.1, ADR-0036).
> Farklı versiyonları birleştirmek hata vermez, sadece ölçtüğün şeyi yok eder.

---

## Kollar

| kol | ver | tarih | durum | rejim | `‖τ‖_F` | eval etiketi | kayıt |
| :--- | :-- | :--- | :--- | :--- | ---: | :--- | :--- |
| `τ_grounding` | **v1** | 2026-07-28 | 🟢 aktif | 1.083 adım · lr 1e-4 · r=16/α=32 · dropout 0.05 · 224 LoRA çifti · seed 3407 · veri `train/raft_scrubbed/` ⁽¹⁾ | **10.4589** | `*_tg` *(Sprint 1; v1 demektir)* | [#41](kronoloji-39-52.md#41) |
| `τ_abstention` | **v1** | 2026-08-03 | 🟢 aktif | **70 adım (5 epoch)** · lr 1e-5 · beta 0.1 · etkin batch 64 · r=16/α=32 · dropout 0.05 · 224 LoRA çifti · `--fresh-adapter` · seed 3407 · veri `data/train/orpo_abstain_cp2c/` (726 çift + 145 replay) | **1.1806** | `*_ta_v1_th` | [#48 §16](kronoloji-39-52.md#48) |
| **`τ_g+τ_a` merge**<br>`HakHukuk-4B-v0.1` | **v1** | 2026-08-03 | 🟢 **ANA SONUÇ** | `tg_v1` + `ta_v1` · **ham TIES** (norm dengeleme **KAPALI**, [ADR-0052](../adr/kararlar-0045-0063.md#adr-0052)) · trim_k 0,2 · λ 1,0 · eşzamanlı 2-yollu · 224/224 tensör | — *(merge, kol değil)* | `*_tg_ta_ham_th` ⚠️ | [#48 §24](kronoloji-39-52.md#48) |

> ⁽¹⁾ **Düzeltme 2026-08-06 — bu hücre `train/raft/` yazıyordu.** Kayıt kendi içinde çelişiyordu:
> [#47](kronoloji-39-52.md#47) ve
> [#48](kronoloji-39-52.md#48) `raft_scrubbed`, bu hücre ile
> `TASARIM.md` *(silindi 2026-09-06)* §planlama tablosu ham `raft/` diyordu. **Adım aritmetiği ayırt
> etmiyor** — iki dizin de 17.323 satır (17.323 ÷ 16 = 1.083 adım, ikisi için de doğru).
> Ayırt eden **davranışsal kanıt:** ham `raft/`'ın eğitim hedeflerinin **%7,51'i** teacher etiketi
> (`GOLD`/`DISTRACTOR`) taşıyor ([#39](kronoloji-39-52.md#39),
> `scripts/scrub_teacher_jargon.py`); `τ_g`'nin **30 koşu dosyasındaki ≈2.000 üretiminde bu
> etiketler 0 kez** geçiyor. Ham veriyle eğitilmiş olsaydı sıfır beklenmezdi → `raft_scrubbed`.
> ⚠️ **Kesin değil, en iyi desteklenen okuma:** `tg_v1`'in eğitim koşusu KUNYE disiplininden
> önce (2026-07-28) koştu, `--data` argümanını **birebir gösteren bir künye yok**. Ham `raft/`
> silinmedi; iki dizin de duruyor.

### `τ_grounding` v1 — açık kalemler *(2026-07-29 gecesi, bütçeli kipte YENİDEN YAZILDI)*

⚠️ Aşağıdaki tablo **CP0.9'dan sonra baştan yazıldı**. Eski hâli thinking-off ölçümünden geliyordu
ve o protokol artık canlı değil (ADR-0043 m.4). Kaynak:
[`research_log` #43](kronoloji-39-52.md#43).

| # | sebep | thinking-off | **bütçeli** | durum |
| :-- | :--- | :--- | :--- | :--- |
| 1 | **M5 anti-hedef ihlali** | 36.9 → **44.2** ❌ | 42.5 → **39.2** | ✅ **KAPANDI** — Kapı 6'yı bugün `τ_g` geçiyor, base geçemiyor |
| 2 | **A1 düşüşü** (cevapladığında hata) | 0.973 → 0.847 | 0.986 → **0.866** | 🟡 **duruyor** — ne kadarı meta-iddia artefaktı, CP1 söyleyecek |
| 3 | **RAFT şablonunun meta-iddiaları** (desteksiz iddiaların %58'i) | — | — | 🟡 hakem tarafında (ADR-0041, CP1) |
| 4 | **Akıl yürütme izi İngilizce** | 8/8 | 8/8 | 🟡 ürün vaadi *"okunabilir muhakeme"* karşılanmıyor; izli eğitim verisi gerektirir |
| 5 | 🆕 **M2b çöküşü** — gold yokken distractor'lardan cevap uyduruyor | 1.000 ✅ | **0.506** ᴷ³ (fabrikasyon **0.494**) ~~0.607 / 0.393~~ | 🔴 **EN GÜÇLÜ sebep** — üstelik tam kendi eğitim ailesinde (RAG_MULTI) |

> ⚠️ **ᴷ³ 2026-08-06 (kusur Ö4) — bu satır aynı belgenin `τ_g v1` satırıyla ÇELİŞİYORDU.**
> Burada `τ_g`'nin bütçeli M2b'si **0.607** (damgasız, eski alet), aşağıdaki kol tablosunda
> **0.506ᴷ³**; aynı belge, aynı nicelik, iki alet. Artefakt sicili *"adı olmayan artefakt
> kullanılamaz"* diyen belgedir — kendi içinde çelişemez. Yürürlükteki değer
> `outputs/eval/cp09-butceli-1024-512/abst_m2b_tg_v1_th_summary.json`'dan okundu
> (payda 77/80). Eski sayılar denetim izi olarak duruyor; çeviri tablosu :193'te.
> ⚠️ **`thinking-off` sütununa DOKUNULMADI**: o ayrı bir rejim (ADR-0043 m.4 ile emekli) ve
> yeniden puanlanmadı — ᴷ³ yalnız bütçeli sütunu kapsar.

**Ne değişti:** eski tablonun *"en güçlü sebep"*i (M5 ihlali) bütçeli kipte **ortadan kalktı**;
yerine M2b geldi. Yani `τ_g` v2'nin gerekçesi artık *"ezberi azalt"* değil **"kaynak yokken sus"**.
Bu aynı zamanda `τ_a`'nın hedefiyle çakışıyor — v2 mi `τ_a` mı sorusu Sprint 2'nin açık kararı
(`_arsiv/sprint2.md` ARA KAPI bölümü — *silindi 2026-09-06; `git show 301a82f^:…`*).

> **Kural (değişmedi):** v2 açılırsa **bütün açık kalemler aynı anda** kapatılır. Ayrı ayrı
> eğitmek iki kat para (~$5.5) ve iki kat kafes yeniden ölçümü demektir. ADR-0040 m.4 gereği
> yeniden eğitilen her kol **düşünme yeteneğini koruyacak** biçimde eğitilir.

### `τ_grounding` v1 — düşünce modu davranışı *(n=470'te DÜZELTİLDİ, 2026-07-29)*

⚠️ CP0'ın n=36'lık ölçümü *"`τ_g` düşünüyor ve duruyor, 35/36"* diyordu ve bu **genel bir kazanç**
sanılmıştı. n=470'te kazanç **eğitim istemi ailesine özgü** çıktı:

| istem ailesi | modlar | base zorunlu kapatma | `τ_g` | ort token base→`τ_g` |
| :--- | :--- | --: | --: | :--- |
| **RAG_MULTI** ← `τ_g`'nin eğitim biçimi | m1 · m2b · m3 | %91.7 | **%5.8** | 1098 → **476** |
| RAG_tek | m4 · m2 | %96.7 | %79.3 | 1116 → 1046 |
| BLIND | m5 | %100.0 | %95.0 | 1284 → 1146 |

Kendi ailesinde etki muazzam (token **yarıya**, kendi kendine kapanma %94); dışında marjinal.
CP0'ın örneklemi o aileden geldiği için genel görünmüştü. Ayrıntı: `research_log` #43 Bulgu 2.

**Maliyet ekseni:** `τ_g` toplamda **772 tok/cevap** (base 1135, Gemini 543) — kendi istem
ailesinde **476**, yani orada rakipten ucuz.

---

## `τ_g+τ_a` merge v1 — künye

**Ürün adı: `HakHukuk-4B-v0.1`** (insan kararı, 2026-08-03)

```
HakHukuk-4B-v0.1  ==  tgta_v1  ==  tg_v1 + ta_v1, ham TIES
```

İki ad **ayrı iş görür ve ikisi de kalır**: `tgta_v1` **iç izlenebilirlik** içindir (dosya
adından *"bu sayı hangi kolun, hangi sürümün"* sorusu cevaplanabilsin — bu belgenin varlık
sebebi); `HakHukuk-4B-v0.1` **dışa dönük** addır (model kartı · makale · anlatım).

⚠️ **Neden `v0.1`, `v1.0` değil:** bu yapılandırma **DEV'de 3 varyant arasından seçildi** ve
**tabanlara karşı henüz sınanmadı**. `v1.0` Kapı 5 geçildikten sonra açılır — geçilmezse zaten
açılmaz.

🆕 **2026-09-07 — `v1.0` yayın artefaktının adı karara bağlandı ([ADR-0071](../adr/kararlar-0064-0085.md#adr-0071)):**
adaptörleri merge edilmiş **TEK** GGUF, dosya adı **model + boyut + sürüm + kuantizasyon** taşır →
`HakHukuk-4B-v1.0-Q4_K_M.gguf`. İç ad `tgta_v1-q4_k_m.gguf` **korunur** — yukarıdaki
*"iki ad ayrı iş görür"* kuralının doğrudan uygulanmasıdır, ona bir istisna değil.

🆕 **2026-09-09 — yayın adı BELİRLENDİ ve artefakt kimliği ÖLÇÜLDÜ (Görev 17 Adım 1).**
`v1.0` kapısı geçilmedi ([ADR-0077](../adr/kararlar-0064-0085.md#adr-0077)) ⇒ ürün sürümü
**`v0.3`** ve yayın adı **`HakHukuk-4B-v0.3-Q4_K_M.gguf`**.
⚠️ Plan bu dalda *"`v0.2`"* yazıyordu; o ad **yazıldığı gün** güncel olan ürün sürümüydü ve
`v0.2` git'te **zaten etiketli** ⇒ bugün yapılan yayına verilemez. Sapma burada damgalıdır.

| | değer |
| :--- | :--- |
| **yayın adı** | `HakHukuk-4B-v0.3-Q4_K_M.gguf` |
| iç ad *(korunur)* | `tgta_v1-q4_k_m.gguf` |
| **`sha256`** | `755e15e92e9f7021934f2d5eada6c1f02fcc92be23f0536b0c2a0a9586e7bffc` |
| boyut | **2.783.446.720 bayt = 2,592 GiB** (ADR-0071'in *"2,59 GiB"*i ile tutuyor) |

⛔ Dosya **kopyalanmadı/yeniden adlandırılmadı** — 2,6 GB'lık ikinci bir kopya diskte
karşılığı olmayan bir maliyettir; ad, yükleme anında verilir. Bağlayıcı kimlik **`sha256`**.

**Artefakt kimliği** (`tgta_v1`):

```
models/merged/tgta_v1/                   merge edilmiş bf16 (8,8 GB)
models/gguf/tgta_v1-q4_k_m.gguf          taşıyıcı, 2,59 GiB (base ile aynı boyut)
                                         sha256 755e15e9…86e7bffc (ölçüldü 2026-09-09)
outputs/eval/cp3d-merge/KUNYE_tgta_v1.json   merge künyesi (normlar, TIES istatistikleri)
```

⚠️ **Eval çıktıları `*_tg_ta_ham_th` etiketiyle duruyor** (`outputs/eval/cp3-supurme-ham/`).
Yeniden adlandırılmadı: dosyaların içinde `"label"` alanları var ve ölçüm o etiketle koşuldu.
Sonradan düzeltmek, koşulan şeyi daha derli toplu göstermek için **ölçüm kaydını yeniden
yazmak** olurdu. Eşleme burada kayıtlı ve bağlayıcı olan budur:

```
tgta_v1  ==  outputs/eval/cp3-supurme-ham/*_tg_ta_ham_th_*          harness KAPALI
tgta_v1  ==  outputs/eval/s3-harness-acik/*_tgta_v1_h1_*            harness AÇIK (2026-08-04)
```

⚠️ **Aynı artefaktın iki ölçümü var, karıştırma.** `cp3-supurme-ham` harness KAPALI
(bağlam elle kuruluyor), `s3-harness-acik` harness AÇIK (bağlamı retriever seçiyor,
k=5). Rejim değişmezleri ikisinde de aynı; **tek fark bağlamın nereden geldiği** —
kıyas bu yüzden kurulabiliyor. Sayılar:
[#51](kronoloji-39-52.md#51) ·
[#54](kronoloji-53-62.md#54) ·
[#55](kronoloji-53-62.md#55) · kütle
**%71,6 (kapalı) ↔ ~~%58,7~~ %56,9 (açık, k=5) ↔ %59,5 (açık, k=10) ↔ %61,3 (açık, k=10 +
onarılmış korpus) ↔ %62,8 (açık, k=10 + onarılmış korpus + önsöz, ADR-0058 — ⭐ ürünün ayarı;
önsözsüz ablasyon: %61,3)**, altın getirilen alt kümede A1 **~~0,934~~ 0,923 >
0,909** (k=5) ama **0,843** (k=10) → **0,8705** (k=10 + S2 + yeterlilik önsözü; önsözsüz: 0,8616).
⚠️ Eski sayılar `A1` yerine ham makro kullanıyordu (tuzak 2.16).
Koşular: `outputs/eval/s3-harness-k10/` (k=10) · `outputs/eval/s2-harness-k10-etiketli/`
(k=10 + S2 — **önsözsüz ablasyon** koşusu; ADR-0058'e kadar "nihai" diye etiketliydi) ·
**`outputs/eval/olcum-bi/` (ANA PROTOKOL — önsözlü, resmî çıpa;
[#56](kronoloji-53-62.md#56) §5 (D1) ·
[ADR-0058](../adr/kararlar-0045-0063.md#adr-0058))**.

**Harness artefaktı** (modelin parçası değil, ama ölçümün parçası):

```
data/index/mevzuat_bge_m3/               hibrit indeks · BAAI/bge-m3 · 40.496 madde · 83 MB
data/index/mevzuat_bge_m3/KUNYE.json     yöntem · model · pencere · korpus imzası
⭐ data/index/mevzuat_bge_m3_s2/          S2 sonrası indeks (onarılmış korpus) · 80 MB
                                         ürünün ayarı BUDUR; eskisi S2-öncesi sayıların
                                         yeniden üretilebilmesi için KASTEN silinmedi
```

**Neden `v1` = ham TIES:** üç varyant DEV'de denendi, kazanan bu ([ADR-0052](../adr/kararlar-0045-0063.md#adr-0052)).
Diğer ikisi **ablasyon**, versiyon numarası almazlar:

| varyant | geri ölçek | artefakt | M1 kütle | M2 Rej | M2b Rej | durum |
| :--- | ---: | :--- | ---: | ---: | ---: | :--- |
| **ham TIES** | — | `tgta_v1` | **71,6%** | **0,833** ᴷ⁴ ~~0,893~~ | **0,766** ᴷ³ | 🟢 **ANA SONUÇ** |
| norm-dengeli `min` | 1,181 | `tg_ta_min` | 53,4% | **0,909** ᴷ⁴ ~~0,934~~ | 0,987 ᴷ³ *(değişmedi)* | ablasyon |
| norm-dengeli `ortalama` | 5,826 | `tg_ta_nb` | — | — | — | 🛑 dejenere, koşu geçersiz |

ᴷ³ **M2b 2026-08-06'da yeniden puanlandı.** Eski sayılar, hakemin **modelin cevabına bakarak**
verdiği bir paydayla üretilmişti — yani aynı sınav her modelde farklı payda veriyordu. Payda artık
cevaba kör ve kollarda birebir aynı (`valid_traps` bu sınavda 61…80 → **77**). Eski değerler
[`#57`](kronoloji-53-62.md#57)'de duruyor; çeviri tablosu orada:
base `0,986 → 0,961` · biz `0,877 → 0,766` · Gemini FL `1,000 → 0,883`.
ᴷ⁴ **M2 sütunu 2026-08-06'da yeniden puanlandı** (KARAR-3, hakem ≈$0,11): aynı 70 kalemlik
sınavda on kol **55-63** arası payda gösteriyordu, artık hepsi **66/70**. ⚠️ **Düzeltme BİZİM
LEHİMİZE ve öyle raporlanıyor** — en çok kayan özne RAKİP (Gemini −8,2 p ↔ biz −6,0 p),
açıklık 3,7 → **1,5 puana** daralıyor. Kaynak:
[`outputs/eval/karar3-m2-payda/m2_payda_2026-08-06.json`](../../outputs/eval/karar3-m2-payda/m2_payda_2026-08-06.json).
⚠ **A1 sütunu yeniden puanlanmadı** — `valid_trap`ten etkilenmiyor, ayrı eksen.

> 🚨 **ᴷ³ DAMGASININ KAPSAMI — TÜRETİLMİŞ NİCELİKLER DE DÂHİL** (netleştirildi 2026-08-06,
> kusur K2). Damga *"bu sayı yeni aletle üretildi"* demektir ve **ondan hesaplanan her orana
> da uzanır**. Kusur tam buradan çıktı: girdiler (0,986→0,961 · 0,607→0,506 · 0,877→0,766)
> yerinde güncellenmiş, onlardan türeyen **onarım oranı** (%71,2 → %57,1) güncellenmemiş, ama
> satır yine de ᴷ³ taşıyordu — yani "gözden geçirildi" diye tasdik edilmiş bir yanlış sayı.
> **Kural: bir girdiye ᴷ³ vururken, o girdiden hesaplanan oran/fark/yüzdeleri `grep` ile tara.**

**Ölçülen — hepsi aynı protokol, hepsi geçerli koşu** (thinking on · 1024+512 · seed 3407 ·
chunk 900 · Q4_K_M + llama-server · DEV havuzu · hakem gpt-4o-mini):

> 🚨 **Künye düzeltmesi (2026-08-06):** yukarıdaki satır *"kapı openrouter/`OpenAI` pinli"* diyordu;
> **yanlıştı.** `çıplak base` ve `Gemini 3.1 FL` satırları **openai-doğrudan** kapıda ve
> **ADR-0041 öncesi** hakem istemiyle puanlanmış; `tgta_v1` · `τ_g` · `τ_a` satırları openrouter'da
> ve muafiyet **sonrası**. **A1 sütunu yığın-eşleşmesiz.** Aynı cevaplar güncel protokolle yeniden
> puanlandığında: **base 0,9864 → 0,9587** (−2,77 puan) · **FL 0,9561 → 0,9592** (+0,31). Kayma
> **asimetrik**, dolayısıyla salt kapı gürültüsü diye yazılamaz; kapı ↔ istem-sürümü ayrıştırması
> **açık kalem** (eski yığın erişilemez, OpenAI kredisi yok). Kaynak: `outputs/eval/g1-eslesmis-a1/`.
> ⚠️ **Coverage-eşleşmiş** alt kümede (n=40, tek payda, üç yığın eşleşmiş) A1 ekseni base ile bizi
> **ayırmıyor**: base **0,9525** · biz **0,9563** · FL **0,9813**; 40 kalemin **33'ü berabere**.

```
                 M1 kütle  aşırı-red      A1   M2 Rej  M2b Rej   tok/cevap (M1)
çıplak base        56,7%      0,425   0,9864   0,803ᴷ⁴  0,961ᴷ³      1192
tgta_v1 (BİZ)      71,6%      0,212   0,9087   0,833ᴷ⁴  0,766ᴷ³       714
Gemini 3.1 FL      72,9%      0,237   0,9561   0,848ᴷ⁴  0,883ᴷ³         —
τ_g v1             71,4%      0,175   0,8658   0,833ᴷ⁴  0,506ᴷ³         —
τ_a v1             41,2%      0,575   0,9697   0,955ᴷ⁴  0,987          ~1084

ᴷ⁴ eski (özneye bağlı payda 55-63): base 0,814 · biz 0,893 · Gemini 0,930 · τ_g 0,873 · τ_a 0,984
```

**Ne başardı:** `τ_g`'nin grounding'ini **tamamen** korurken (71,4% → 71,6%) onun M2b
çöküşünün **%57'sini** ~~%71'ini~~ onardı (0,506 → 0,766 ᴷ³; sıçrama **+0,26**, değişmedi).

> ⚠️ **Onarım oranı neden oynadı ama sıçrama oynamadı** (düzeltildi 2026-08-06, kusur K2):
> oran `(merge − τ_g) / (base − τ_g)`, yani **üç girdinin herhangi biri** yeniden puanlanınca
> kayar. Kör-payda onarımı (ᴷ³) üçünü de yeniledi: eski `(0,877−0,607)/(0,986−0,607) = %71,2`
> → yürürlükteki `(0,766−0,506)/(0,961−0,506) = **%57,1**`. Girdiler yerinde güncellenmişti,
> bu **türetilmiş** nicelik güncellenmemişti — üstelik "gözden geçirildi" diye tasdik eden
> ᴷ³ damgasının **altında** duruyordu. Damgasız olmaktan zararlıydı.

**Ne BAŞARAMADI — M2'de hiçbir şey taşımıyor** *(kaydedilmemişti, 2026-08-06 eklendi · kusur Ö2 m.3)*:

```
τ_g v1    55/66 = 0,833 ᴷ⁴        merge'in M2'ye katkısı:  ~~+0,020~~ → +0,000
tgta_v1   55/66 = 0,833 ᴷ⁴        iki kol BİREBİR EŞİT (aynı 55 kalem)
τ_a v1    63/66 = 0,955 ᴷ⁴        ← tek başına o eksende çok önde
```

Emekli alette merge `τ_g`'yi M2'de **+0,020** geçiyor görünüyordu; o fark tümüyle **paydaların
özneye bağlı olmasından** geliyordu (`τ_g` 55'lik, `tgta_v1` 56'lık payda — **farklı sınav**).
Payda 66'ya eşitlenince fark **sıfırlandı**. ⭐ Bu, ARA KAPI'nın *"merge `τ_a`'yı taşımıyor"*
teşhisini **ikinci, bağımsız bir eksenden** doğruluyor — o teşhis M2b'den (`0,987 → 0,766`)
türetilmişti. ⚠️ M2'nin kuantumu `1/66 = 1,52 p`, yani `+0,000` ile `±1 kalem` arasında ayrım
kurulamaz (çözünürlük borcu: `docs/open_questions.md`). Kaynak: [#59](kronoloji-53-62.md#59) §2.

Ayrıca öz-sonlandırma geri geldi (M1'de 25/80
zorunlu kapatma, base 80/80) ve cevap başına maliyet base'e göre **%40 düştü**.

> 🛑 **Bu bir PARİTE İDDİASI DEĞİLDİR.** Gemini sütunu **çıpa**dır: harness KAPALI (retriever ·
> atıf doğrulayıcı · red kapısı yok — ADR-0019 bunları teze dahil ediyor), maliyet normalize
> edilmedi, ölçüm **DEV** havuzunda ve **merge yapılandırması DEV'de 3 varyant arasından
> seçildi**. Frozen TEST (`data/eval/canon/`) görülmedi. Aynı disiplin:
> `sprint1/sprint1-sonuc-tablosu.md` *(silindi 2026-09-13, ADR-0086; `git show 301a82f:docs/record/sprint1/sprint1-sonuc-tablosu.md`)*.
>
> ⚠️ Açıkça geride olduğumuz eksen **M2b: 0,766 ↔ 0,883** ᴷ³. Raporda böyle geçer.

