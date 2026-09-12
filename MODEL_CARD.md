# HakHukuk-4B-v0.1

> Türkçe mevzuat için, tüketici sınıfı bir dizüstü GPU'sunda çalışan **4B**'lik bir hukuk
> asistanı. İki LoRA kolu ham base'den **bağımsız** eğitildi ve **görev vektörü** olarak
> **ham TIES** ile birleştirildi.
>
> **Ağırlıklar yayımlandı (2026-09-09):** [`Rfetha/HakHukuk-4B-v0.3-Q4_K_M`](https://huggingface.co/Rfetha/HakHukuk-4B-v0.3-Q4_K_M) ·
> `HakHukuk-4B-v0.3-Q4_K_M.gguf` · 2.783.446.720 bayt ·
> `sha256 755e15e9…86e7bffc`. Örnek çıktılar aynı depoda `ORNEK_CEVAPLAR.md`.
>
> **Not (2026-09-09):** depo, açık kusurlar giderilene kadar geçici olarak **ÖZEL**dir.

> ## BU HUKUKİ TAVSİYE DEĞİLDİR
>
> HakHukuk, hukuk metnini **anlaşılır kılmak** için yapılmış bir araştırma artefaktıdır.
> Avukat **değildir**, çıktısı hukuki tavsiye **değildir**. Gerçek bir hukuki mesele
> hakkında karar vermek için kullanmayın; nitelikli bir avukata danışın.
>
> **Mevzuat değişir, ağırlıklar değişmez.** Modelin ağırlıklarındaki bilgi eğitim verisinde
> donmuştur; güncellik **kütüphanenin** (retriever + indeks) işidir. Ürettiği her madde
> numarasını [mevzuat.gov.tr](https://www.mevzuat.gov.tr) üzerinden **doğrulanması gereken
> bir iddia** olarak görün.
>
> **Bu ibarenin NİHAİ metni henüz kararlaştırılmadı.** Avukatlık Kanunu ve hukuki
> sorumluluk sınırı repoda **hiç değerlendirilmedi** ve **hukukçu görüşü gerektiriyor** —
> açık karar **S10** — soruyu taşıyan plan 2026-09-12'de kapandı ve silindi; soru
> [ADR-0083](docs/adr/0083-kusur-sicili-adrye-tasindi.md) §EK'te grill'e giren maddeler arasında
> **açık** duruyor.
> Yukarıdaki metin bir **taslaktır**, hukuki olarak denetlenmiş bir feragatname değildir.

---

## 1 · Kimlik

| | | kaynak |
| :--- | :--- | :--- |
| **Dış ad** | `HakHukuk-4B-v0.1` | [`kollar.md`](docs/record/kollar.md) |
| **İç ad** | `tgta_v1` = `tg_v1` + `ta_v1` | [`kollar.md`](docs/record/kollar.md) |
| **Base** | `Qwen/Qwen3.5-4B` · commit `851bf6e8…` · Apache-2.0 | [`KUNYE_tgta_v1.json`](outputs/eval/cp3d-merge/KUNYE_tgta_v1.json) (`base` alanı) |
| **Yöntem** | 2 × LoRA (r=16, α=32) → eşzamanlı 2-yollu **ham TIES** | [`KUNYE_tgta_v1.json`](outputs/eval/cp3d-merge/KUNYE_tgta_v1.json) |
| **Taşıyıcı** | GGUF **Q4_K_M** · **2,59 GiB** (2.783.446.720 bayt) | `models/gguf/tgta_v1-q4_k_m.gguf` · [ADR-0071](docs/adr/0071-v1-release-artefakti-tek-gguf.md) |
| **Dil** | Türkçe | — |
| **Lisans** | Apache-2.0 | [`LICENSE`](LICENSE) · [`NOTICE`](NOTICE) |

### İki ad, iki ayrı iş — ikisi de kalır

[`kollar.md`](docs/record/kollar.md)'de yazılı ve yürürlükte olan kural:

| ad | işi |
| :--- | :--- |
| `tgta_v1` | **iç izlenebilirlik** — *"bu sayı hangi kolun, hangi sürümün sayısı?"* sorusu **dosya adından** cevaplanabilsin diye. Versiyon zincirin her halkasında taşınır: adaptör → merge → GGUF → eval etiketi. |
| `HakHukuk-4B-v0.1` | **dışa dönük ad** — model kartı, yayın, anlatım. |

**Yayın artefaktının adı karara bağlandı** ([ADR-0071](docs/adr/0071-v1-release-artefakti-tek-gguf.md)):
adaptörleri merge edilmiş **TEK** GGUF, adı **model + boyut + sürüm + kuantizasyon** taşır →

```
HakHukuk-4B-v1.0-Q4_K_M.gguf
```

> **Bu ad HENÜZ KULLANILMIYOR.** Bugünkü artefakt `v0.1`'dir; `v1.0` **verilmedi**.
> ADR-0071 adı *kararlaştırır*, sürümü *vermez* — `v1.0` adı ADR-0064'ün kapısı **donmuş TEST
> kabul testinde** koşulmadan kullanılmaz ([ADR-0065](docs/adr/0065-bolunmus-surumleme.md) ·
> [ADR-0071](docs/adr/0071-v1-release-artefakti-tek-gguf.md) *"Açık kalan"*). Bkz. §5.

---

## 2 · Yöntem

```
ham base ──┬── LoRA SFT   (grounding)   → τ_g
           └── LoRA ORPO  (çekinme)     → τ_a
                                           │
                    eşzamanlı 2-yollu TIES ┘
                    HAM (norm dengeleme KAPALI) · trim_k 0,2 · λ 1,0 · 224/224 tensör
```

*(şemadaki her parametre: [`KUNYE_tgta_v1.json`](outputs/eval/cp3d-merge/KUNYE_tgta_v1.json) —
`norm_dengeleme` · `trim_k` · `lam` · `birlesik_tensor` / `ortak_lora_hedefi`)*

| nicelik | değer | kaynak |
| :--- | ---: | :--- |
| `‖τ_g‖_F` (merge anında, bf16 ΔW'den) | **10,4722** | [`KUNYE_tgta_v1.json`](outputs/eval/cp3d-merge/KUNYE_tgta_v1.json) |
| `‖τ_g‖_F` (bağımsız artefaktan) | **10,4589** | [`kollar.md`](docs/record/kollar.md) |
| `‖τ_a‖_F` | **1,1806** | [`KUNYE_tgta_v1.json`](outputs/eval/cp3d-merge/KUNYE_tgta_v1.json) · [`kollar.md`](docs/record/kollar.md) |
| norm oranı `‖τ_g‖ / ‖τ_a‖` | **8,87×** | yukarıdaki ikisinden |
| çatışan parametre oranı | 0,022541 | [`KUNYE_tgta_v1.json`](outputs/eval/cp3d-merge/KUNYE_tgta_v1.json) |
| sıfır kalan oran | 0,645798 | [`KUNYE_tgta_v1.json`](outputs/eval/cp3d-merge/KUNYE_tgta_v1.json) |

**`τ_g` için iki norm değeri de DOĞRUDUR, biri diğerinin düzeltmesi değildir.** İlki merge
anında bf16'da materyalize edilen ΔW'den, ikincisi bağımsız artefakttan ölçüldü; %0,13'lük fark
bf16'dan gelir ve kayda **bağımsız çapraz kontrol** olarak geçti
([#47](docs/record/research_log/2026-07-30-cp2s-boru-hatti.md)). İkisinden biri "düzeltilmez".

### Neden iki kol BAĞIMSIZ eğitildi — geçerlilik şartı, üslup tercihi değil

Görev vektörünün tanımı **`τ = θ_ft − θ_base`**'dir. Bu tanım bütün kolların **tek ve aynı
`θ_base`**'den çıkmasını şart koşar. Bir kolu diğerinin **üstüne** eğitmek görev vektörü değil
**ardışık SFT** üretir — yani ölçmek için kurulan şeyi yok eder. Aynı sebeple merge **eşzamanlı
k-yollu**'dur, iteratif değil: `TIES(TIES(τg,τa),τr) ≠ TIES(τg,τa,τr)`, çünkü TIES kırpma,
işaret seçimi ve ortalamayı **bütün vektörler üzerinde aynı anda** yapar.
([ADR-0027](docs/adr/0027-tasarim-kilitleri-paralel-kol-merge.md) · [`kollar.md`](docs/record/kollar.md))

### Neden HAM TIES — hüküm ölçülerek TERSİNE döndü

Norm dengeleme **KAPALI**'dır (`norm_dengeleme: false`,
[`KUNYE_tgta_v1.json`](outputs/eval/cp3d-merge/KUNYE_tgta_v1.json)).

[ADR-0036](docs/adr/0036-tau-norm-asimetrisi-ve-norm-dengeli-merge.md) norm dengelemeyi **ana ayar** olarak ön-kayıtlamıştı; gerekçesi *"kollar 8,87× farklı
ölçekte, TIES'in işaret seçimi kütle-ağırlıklı, dengelenmezse küçük kol silinir"* idi.
**Öncül doğrulandı ve hâlâ geçerli; çıkarım ölçülerek yanlış çıktı**
([ADR-0052](docs/adr/0052-merge-norm-dengeleme-hukmu-tersine.md)):

| varyant | M1 kütle | M2b Rej | hüküm | kaynak |
| :--- | ---: | ---: | :--- | :--- |
| **ham TIES** (`tgta_v1`) | **%71,6** | **0,766** | ana sonuç | [`kollar.md`](docs/record/kollar.md) |
| norm-dengeli `min` (`tg_ta_min`) | %53,4 | 0,987 | ablasyon — grounding ezildi | [`kollar.md`](docs/record/kollar.md) |
| norm-dengeli `ortalama` (`tg_ta_nb`) | — | — | dejenere, koşu geçersiz | [`kollar.md`](docs/record/kollar.md) |

Ham TIES `τ_a`'yı **silmedi**: `τ_g`'nin M2b çöküşünün **%57,1**'ini onardı
(0,506 → 0,766, sıçrama **+0,26**); dengeleme ise `τ_g`'yi ezdi (%71,4 → %53,4).
*(merge M2b: [`abst_m2b_tg_ta_ham_th_summary.json`](outputs/eval/cp3-supurme-ham/abst_m2b_tg_ta_ham_th_summary.json)
`rejection_rate` · `τ_g` M2b ve onarım oranı: [`kollar.md`](docs/record/kollar.md) ᴷ³ bölümü ·
yeniden puanlama: [#57](docs/record/research_log/2026-08-06-cekinme-aleti-onarimi.md))*
**Bu satırdaki sayılar `v1` birimindedir** (harness **KAPALI**, v1 soru seti, 1024 bütçe) ve
§3'ün manşet sayılarıyla **KIYASLANAMAZ** — §7.1'e bakın.

---

## 3 · SKOR KARTI

**Tek tablo, tek rejim.** Dört özne aynı sınava girdi: v2 soru seti (n=80, DEV) · **önsözsüz**
istem · harness **AÇIK** (`k=10`) · üretim bütçesi **1536** · seed 3407 · hakem `gpt-4o-mini`.
Sınavın eşit olduğu **varsayılmadı, ölçüldü** — kanıt §4'te.

| eksen | **HakHukuk-4B-v0.1** | `gemini-3.1-flash-lite` | `gemini-3.5-flash-lite` | `gemini-3.5-flash` | `Qwen3.5-4B` (base) | kaynak |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| **sadık-cevap kütlesi** ↑ ᵃ | **0,8011** | 0,7058 | 0,7622 | 0,7425 | ölçülemedi ᵇ | [`KALIBRASYON_ve_OZET.md`](outputs/eval/f04-rakip-onsozsuz/KALIBRASYON_ve_OZET.md) |
| `coverage` (cevaplama oranı) | **0,9375** | 0,8750 | 0,8750 | 0,8375 | ölçülemedi ᵇ | [`harness_tablo*.json`](outputs/eval/f02-biz-onsozsuz/harness_tablo.json) |
| `A1` · cevaplanan ↑ | **0,8545** | 0,7710 | 0,8199 | 0,8269 | ölçülemedi ᵇ | ↑ |
| `A1` · altın getirilen ↑ | **0,8902** | 0,7900 | 0,8449 | 0,8523 | ölçülemedi ᵇ | ↑ |
| `recall@10` (erişim) | 0,9500 | 0,9500 | 0,9500 | 0,9500 | ölçülemedi ᵇ | ↑ |
| **aşırı-red** ↓ ᶜ | **4/80** | 8/80 | 9/80 | 11/80 | ölçülemedi ᵇ | ↑ (`altin_geldi_cekindi`) |
| **isabetsizlik** ↓ ᵈ | 8/80 | 8/80 | **7/80** | 8/80 | ölçülemedi ᵇ | [`GOZLE_OKUMA_80.md`](outputs/eval/f02-biz-onsozsuz/GOZLE_OKUMA_80.md) · [`GOZLE_ISABETSIZLIK_*.md`](outputs/eval/f04-rakip-onsozsuz/GOZLE_ISABETSIZLIK_3_5_FLASH.md) |
| **uydurulmuş madde** ↓ ʰ | **0/114** | **0/153** ʰ | 4/130 | 4/133 | ölçülemedi ᵇ | [`harness_tablo*.json`](outputs/eval/f02-biz-onsozsuz/harness_tablo.json) · [yeniden puanlama](outputs/eval/g22-rakip-yeniden-puanlama/BULGU.md) |
| **M5 ezber kütlesi** ↓ ᵉ | **0,3899** | 0,6710 | 0,7013 | 0,8241 | **0,4697** | [`f07/KUNYE.json`](outputs/eval/f07-m5-anti-hedef/KUNYE.json) · [`f10/KUNYE.json`](outputs/eval/f10-rakip-m5/KUNYE.json) |
| **$ / cevap** ↓ ᵍ | **$0** | $0,001895 | **$0,001152** | $0,009914 | **$0** | [`MALIYET.json`](outputs/eval/f09-maliyet/MALIYET.json) |
| ort. **token / cevap** ↓ | 782,5 | 861,5 | **171,1** | 699,4 | ölçülemedi ᵇ | [`KALIBRASYON_ve_OZET.md`](outputs/eval/f04-rakip-onsozsuz/KALIBRASYON_ve_OZET.md) |

ʰ **ESKİ ALETİN sayısıydı; 2026-09-11'de doğrulayıcı ONARILDI ve bu satır YENİDEN PUANLANDI.**
Kusur: `atif_dogrula.Dogrulayici` kanun adını gevşek eşleştirip **yanlış kanuna** çözebiliyordu;
parantezli adlı 16 kanunun **7'sinde** yanlış kanuna `DOGRULANDI` basıyordu (onarım sonrası
**0/16**). Yayımlanan boru hattıyla (`scripts/puanlama/harness_tablo.py`) beş kol da yeniden
puanlandı; **kalibrasyon kapısı geçildi** — bizim kolumuzun `harness_tablo.json`'u **alan alan
birebir** yeniden üretildi (kütle `0,8011` · `coverage` `0,9375` · `A1` `0,8545` dâhil).
**702 atfın YALNIZ 1'i değişti** ve o da **rakip aleyhine yanlış basılmış** bir damgaydı:
`gemini-3.1-flash-lite`, soru id 25, *"Gelir Vergisi Kanunu Madde 73"* — eski `1319 Emlak
Vergisi → MADDE_YOK`, yeni `193 GELİR VERGİSİ KANUNU (G.V.K.) → DOGRULANDI` (gözle okundu,
korpus tanığı var, mülga değil). ⇒ **`1/152` → `0/153`.**
**Bu değişim ALEYHİMİZEDİR ve öyle yazılmıştır:** rakiplerin tamamının üstünde olduğumuz tek
deterministik eksende `3.1 Flash-Lite` artık bizimle **eşittir**. Karşılığında **eşit sınav**
sağlandı (ADR-0057): beş kolun beşi de **aynı aletle** puanlanmış durumda. Diğer üç kolun sayısı
**oynamadı**. Her kol **iki kez** koşuldu ve iki koşu **bayt bayt** aynı çıktı.
⚠️ **Bu satırın birimi:** pay = `MADDE_YOK + KANUN_YOK`, payda = **`DOGRULANDI`** (toplam atıf
DEĞİL). Bu ayrım daha önce hiçbir yerde yazılı değildi ve bir ön sondayı yanıltmıştı —
*"3.5 FL 4 → 3"* diye okunan şey **birim kaymasıydı**, o kolda hiçbir atıf değişmedi.
⚠️ **Sonnet-5 hücresi (`2/163`) FARKLI BİR BİRİM kullanıyor:** paydası **toplam atıf**.
Aynı satırda iki kesir birimi duruyor — sayısı oynamadığı için hüküm etkilenmedi, açık kusur
**25** olarak kaydedildi.

**Dipnotlar — hepsi bir ölçüm hükmüdür, süsleme değildir:**

- **ᵃ** Rakip sütunlarında **bağlayıcı GÖZ-katı** okuması yazılıdır — üç okumanın **en
  muhafazakârı**, yani rakip lehine olanı. Üçü birden aşağıdaki küçük tabloda.
- **ᵇ** **"ölçülmedi" değil, ÖLÇÜLEMEDİ — ve sebebi bir bulgudur.** Base bu sınava
  **sokuldu ve geçerlilik kapısından kaldı**: kesik **16/80 = %20** ↔ eşik %5
  ([ADR-0040](docs/adr/0040-dusunce-modu-olculecek-on-kayitli-kural.md)) ⇒ **hakem çağrılmadı**,
  hiçbir hüküm-ekseni sayısı üretilmedi
  ([`f08-base-harness/`](outputs/eval/f08-base-harness/h1_base_h1_v2_detail.jsonl)).
  16 kesiğin **15'i gerçek kesilme, 1'i döngü** ⇒ [ADR-0073](docs/adr/0073-m5-rejimine-dry-eklendi.md)'ün
  `DRY` kaldıracı burada **işe yaramaz**; sebep şu: base **uzun, kaynak alıntılayan** cevaplar
  yazıyor ve **1536'ya sığmıyor**.
  Karşılaştırma bir bulgudur: aynı base **kör modda** yalnız **2/80** kesik veriyor
  ([`f07/KUNYE.json`](outputs/eval/f07-m5-anti-hedef/KUNYE.json)) ⇒ şişiren şey **kaynakların
  kendisi**. Bu, [#42](docs/record/research_log/2026-07-29-cp0-dusunce-modu-sonlanmama.md)'nin
  *"ince ayar muhakemeyi stabilize etti"* bulgusunun **harness AÇIKKEN** ölçülmüş hâlidir.
  **Yer tutucu:** base şu anda Modal'da **daha büyük bir bütçeyle** yeniden koşuluyor. Sonuç
  gelince **ayrı bir satır** olarak, **"EŞİT SINAV DEĞİL — bütçe 2048 ↔ 1536"** damgasıyla
  eklenecek. **O satırın sayısı bugün YOKTUR ve buraya tahmin yazılmamıştır.**
- **ᶜ** Tanım dört öznede de **aynı**: *altın madde bağlama girdi, model yine de sustu*
  (`erisim_davranis_caprazi.altin_geldi_cekindi`). Bunlar **ALET** sayılarıdır.
  Gözle okuma bizim kolumuzda **farkı sıfır** buldu (alet 5 çekinme dedi, 1'i *altın gelmedi*
  olduğu için doğru davranıştı ⇒ **4**), rakip kollarda ise dedektörün **fazla red saydığını**
  buldu — kalibrasyon §4'te. Gözle düzeltilmiş aşırı-red: 3.5 Flash **7/80**
  ([`GOZLE_ISABETSIZLIK_3_5_FLASH.md`](outputs/eval/f04-rakip-onsozsuz/GOZLE_ISABETSIZLIK_3_5_FLASH.md) §2).
- **ᵈ** **BU SATIRDA "BİZ İYİYİZ" CÜMLESİ KURULMAZ.** Dört öznenin de **80/80'i**, f02'nin §2
  tanımıyla **birebir aynı** ölçütle, **gözle tam tarandı** (örneklem değil). Sonuç: **ikisiyle
  berabere, biriyle geride** — `3.5 Flash-Lite` **7/80** ile bizden **iyi** ve bu **olduğu gibi**
  raporlanır.
  **Ve taban aynı değil.** Çekinen kalem sınanamaz; her kolun **cevapladığı** kalem sayısı farklı:

  | kol | isabetsizlik | çekinme (gözle) | **cevaplanan tabanda** |
  | :--- | ---: | ---: | ---: |
  | BİZ | 8/80 | 5/80 | 8/75 = **%10,7** |
  | 3.1 FL | 8/80 | 7/80 | 8/73 = **%11,0** *(türetildi)* |
  | 3.5 FL | 7/80 | 9/80 | 7/71 = **%9,9** *(türetildi)* |
  | 3.5 Flash | 8/80 | 9/80 | 8/71 = **%11,3** |

  *(%10,7 ve %11,3 dosyada yazılı; diğer ikisi aynı dosyaların çekinme sayılarından **türetildi**.)*
  **Ek bulgu, kendi aleyhimize:** f02'de **bizim** isabetsiz olduğumuz id **32 · 41** rakipte
  **isabetli**; ve **27 · 42** — öz-denetimde *"soru yazımım komşu maddeye kaydırdı"* dediğimiz
  iki kalem (§7.7) — rakip o tuzağa **düşmemiş**. ⇒ Kusurun kaynağı soru değil, **model** olabilir.
- **ᵉ** **"M5'te rakipleri yendik" CÜMLESİ KURULMAZ** — sebebi §6'da, ve iki yüzü birden orada.
  Satır **ALET** okumasıdır (dört öznede kıyaslanabilir tek okuma). Bizim iki kolumuzun **GÖZ**
  okuması da var: biz **0,4057** ↔ base **0,4739**; hüküm **iki okumada da aynı**.
- **ᵍ** **Ölçüldü, tahmin edilmedi** — ölçüm bedeli $0,0487
  ([`MALIYET.json`](outputs/eval/f09-maliyet/MALIYET.json), fiyatlar OpenRouter `/api/v1/models`,
  2026-09-07). Bizim iki kolumuz **yerelde** koştu (`llama-server`, RTX 5070) ⇒ çıkarım bedeli **$0**.
  **Eşit sınavın maliyet tarafındaki kanıtı:** girdi token'ı üç öznede de **birebir aynı —
  193.042** (ort. 2.413/kalem), çünkü istem **80/80 bayt-bayt özdeş**. Fark tümüyle **çıktı
  token'ı ve birim fiyattan** geliyor.
  **Kapı çıpası `3.5 Flash`, `3.5 Flash-Lite`'ın 8,6 katı** ($0,009914 ↔ $0,001152).
  **Yöntem şerhi:** üç Gemini **aynı tokenizer**'ı kullanıyor (3 kalemde sınandı, `prompt_tokens`
  birebir: 2842 · 2681 · 2343) ⇒ sayım yalnız **en ucuz** modelde yapıldı, fiyatlar ayrı uygulandı.
  Hakem bedeli bu satıra **dâhil değil**, ayrıca kayıtlı: biz $0,0417 · 3.1 FL $0,0452 ·
  3.5 FL $0,0410 · 3.5 Flash $0,0434 *(`gnd_*_summary.json`)*.
  **Maliyet-normalize parite iddiası yine de KURULMAZ** — ADR-0017'nin istediği ölçüm bir
  Pareto eğrisidir, tek satır değil.

### Rakip sütunlarının üç okuması

Ana tabloda **yalnız bağlayıcı olan** (GÖZ-katı) var; üçü birden burada. Kaynak:
[`KALIBRASYON_ve_OZET.md`](outputs/eval/f04-rakip-onsozsuz/KALIBRASYON_ve_OZET.md).

| kol | ALET (ham) | GÖZ-orta *(yanlış pozitif düzeltildi)* | **GÖZ-katı (BAĞLAYICI)** |
| :--- | ---: | ---: | ---: |
| **BİZ (`tgta_v1`)** | **0,8011** | **0,8011** | **0,8011** |
| `gemini-3.1-flash-lite` | 0,6746 | 0,7058 | 0,7058 |
| `gemini-3.5-flash-lite` | 0,7174 | 0,7403 | **0,7622** |
| `gemini-3.5-flash` | 0,6925 | 0,7050 | 0,7425 |

> **Neden bağlayıcı olan EN MUHAFAZAKÂR okuma** (insan kararı,
> [ADR-0064](docs/adr/0064-v1-kapisi-uc-maddeli-on-kayit.md)): GÖZ-katı'da rakiplerin
> *çekinceli cevapları* da **cevap** sayılır ⇒ onların kütlesi **en yüksek**, bizim farkımız
> **en dar** çıkar. Seçim gerekçesi tam olarak budur — *"kendi lehine okudun"* denemesin diye.
> **BİZ üç okumada da aynıyız**, çünkü kendi kolumuzda yanlış pozitif ve çekinceli cevap **yok**
> (80 kalem gözle okundu, alet ↔ göz farkı **sıfır**).

---

## 3.1 · Bu satırlar ne ölçüyor

> **BUNLAR STANDART BENCHMARK DEĞİLDİR.** Yukarıdaki her sayı **kendi CANON setimizden**
> gelir: **6 mod**, `n=80` **DEV** kalemi, Türkçe, güncel TC mevzuatı.
> **MMLU · LegalBench · BigLaw-Bench gibi hiçbir dış benchmark koşulmadı** ve bu bir eksiklik
> değil, **kayıtlı bir karardır** ([ADR-0016](docs/adr/gemma4-12b-dersler.md#adr-0016)):
> BigLaw/LegalBench **İngilizce/ABD common-law** setleridir ve *"yanlış sınavda düşük not model
> kötü demek değildir"* — TR medeni-hukuk modelinde **yorumlanamazlar**, o yüzden yalnız
> Related Work atfı olarak kalırlar. `alibayram/turkish_mmlu` ise **lisans zehri** (CC BY-NC +
> telif beyanı) diye dışarıda. ADR-0016'nın kendi tespiti: *"üretken TR hukuki cevabın
> grounding/abstention/citation kalitesini ölçen tanınmış benchmark **YOK**"* — bu boşluk
> projenin katkı alanıdır, ama aynı zamanda **dış karşılaştırılabilirliğin neden olmadığıdır**
> (§11).

**CANON'un 6 modu** ([ADR-0011](docs/adr/gemma4-12b-dersler.md#adr-0011), ADR-0027 ile
DEV/TEST ayrımı eklendi) — bu kartın sayıları **`h1`**'den (M1'in harness-AÇIK karşılığı) ve
**M5**'ten gelir:

| mod | ne sorar |
| :--- | :--- |
| **M1** / **`h1`** | Kaynak verildiğinde doğru cevaplıyor ve **dayandığı maddeyi belirtiyor** mu? (`h1` = bağlamı elle değil **retriever** kuruyor) |
| M4 | Altın madde **garantili** verildiğinde tavan nedir? |
| M2 | **Yanlış** bir madde verildiğinde reddedebiliyor mu? |
| M2b / `h2b` | **Yalnız distractor** verildiğinde, altın yokken susabiliyor mu? |
| M3 | Bağlam **boşken** susabiliyor mu? |
| **M5** | **Kaynak verilmeden** ne kadar konuşuyor — **ANTİ-HEDEF**, yükselmemeli |

**Eksenlerin tanımı — her biri tek cümle:**

| eksen | ne ölçer | neden bu |
| :--- | :--- | :--- |
| **sadık-cevap kütlesi** = `coverage × A1` | *"Sorulan 80 sorunun ne kadarına **hem cevap verdi hem de doğru kaynağa dayandı**?"* | **Manşet ve bağlayıcı metrik budur:** cevaplamamak vatandaş için değersizdir, yanlış cevaplamak tehlikelidir — tek sayı ikisini birden cezalandırmalı |
| `coverage` | Cevapladığı kalem oranı (çekinmediği) | Tek başına **yanıltıcıdır**: her şeye cevap veren model burada 1,00 alır |
| `A1` · cevaplanan | **Yalnız cevapladığı** kalemlerde iddialarının kaynağa sadakati | Çekinmeyi ödüllendirmesin diye **cevaplanan-only** hesaplanır ([ADR-0011](docs/adr/gemma4-12b-dersler.md#adr-0011)) |
| `A1` · altın getirilen | Aynı şey, ama **yalnız altın maddenin bağlama girdiği** kalemlerde | ON ↔ OFF ve özneler arası **tek dürüst kıyas satırı** — erişim şansını denklemden çıkarır |
| `recall@10` | Altın madde ilk 10 kaynağın içine girdi mi | **Kütlenin tavanıdır**: girmemişse doğru cevap üretilemez ⇒ kütle bunu **aşamaz** |
| **aşırı-red** | Altın madde **bağlamdayken** yine de sustuğu kalem sayısı | Erişimin **çözemeyeceği**, modelin kendi kusuru. Vatandaş için: *"kaynak elindeydi ve yine de yardım etmedi"* |
| **isabetsizlik** | **Yanlış maddeye** dayanarak cevaplaması (atıf doğrulanır, cevap yine de soruya oturmaz) | Vatandaş için **en tehlikeli** kusur sınıfı — doğrulayıcı bunu yakalayamaz |
| **uydurulmuş madde** | Var olmayan kanun/madde numarası üretmesi | **Deterministik** olarak doğrulanır (hakem gerekmez); sınıfın **boş** çıkması bir bulgudur (§7.5) |
| **M5 ezber kütlesi** | Kaynak **verilmeden** ne kadar konuşup ne kadar tutturduğu | **ANTİ-HEDEF** — yükselmesi *"bilgi ağırlığa kaçtı"* demektir; ilke: **güncellik kütüphanede, ağırlıkta değil** |
| **$ / cevap** · **token / cevap** | Çıkarım bedeli | Ürünün **erişilebilirlik** ekseni: dizüstünde çalışmak bir tasarım şartıdır |

---

## 4 · Sınavın eşit olduğu VARSAYILMADI, ölçüldü

Kural: [ADR-0057](docs/adr/0057-harness-rekabet-kapisi-esit-sinav.md) — bir kıyas **yalnız
eşleşmiş eksenlerde** hüküm verir; eşleşmeyen eksen **TAVAN/tanımsız** damgası alır ve o eksende
*"şu geride"* cümlesi **kurulmaz**.

| eksen | BİZ | 3.1 FL | 3.5 FL | 3.5 Flash |
| :--- | :--- | :--- | :--- | :--- |
| **`recall@10`** | **0,9500** | **0,9500** | **0,9500** | **0,9500** |
| **`context_shown`** | — | **80/80 bayt-bayt aynı** | **80/80** | **80/80** |
| soru seti · istem · bütçe · hakem | v2 · önsözsüz · 1536 · `gpt-4o-mini` | aynı | aynı | aynı |

### Rejim künyesi

| değişmez | değer | kaynak |
| :--- | :--- | :--- |
| soru seti | `data/eval/dev/core_hard.jsonl` **v2**, n=80 | [`KUNYE.json`](outputs/eval/f02-biz-onsozsuz/KUNYE.json) · [ADR-0067](docs/adr/0067-soru-onarimi-dev-test-v2.md) |
| indeks | `data/index/mevzuat_bge_m3_s2` · 40.496 madde · 80 MB | [`KUNYE.json`](data/index/mevzuat_bge_m3_s2/KUNYE.json) |
| erişim | hibrit BM25 + `BAAI/bge-m3`, RRF · **k=10** · `RRF_K=10` | [ADR-0068](docs/adr/0068-rrf-k-60-to-10.md) |
| istem | **önsözsüz** (künyede `ekstra : <yok>`) | [ADR-0063](docs/adr/0063-yeterlilik-onsozu-kaldirildi.md) |
| üretim bütçesi | **1536** = `think 1024 + cevap 512`, **tek formül** | [ADR-0070](docs/adr/0070-uretim-butcesi-esitlendi.md) |
| seed · klip · düşünce | 3407 · 900 karakter · `thinking on` | [`KUNYE.json`](outputs/eval/f02-biz-onsozsuz/KUNYE.json) |
| taşıyıcı (bizim kol) | `llama-server`, Q4_K_M, ctx 8192, KV `q8_0/q8_0`, **yerel** | [`KUNYE.json`](outputs/eval/f02-biz-onsozsuz/KUNYE.json) |
| hakem | `openai/gpt-4o-mini` · OpenRouter, `OpenAI` pinli · **runs=1** | [`gnd_…_summary.json`](outputs/eval/f02-biz-onsozsuz/gnd_h1_tgta_v1_f02_nb_summary.json) |

### Zorunlu ön adım: red dedektörü rakip ailelerde kalibre edildi

`CLAUDE.md` kuralı gereği **28 rakip çekinme kalemi tek tek gözle okundu**. Dedektörün Gemini
şablonunda **sistematik olarak fazla red saydığı** bulundu:

| kol | alet | temiz çekinme | çekinceli cevap | **açık yanlış pozitif** |
| :--- | ---: | ---: | ---: | ---: |
| **BİZ** | 4 | **4** | 0 | **0** |
| 3.1 Flash-Lite | 8 | 5 | 0 | **3** |
| 3.5 Flash-Lite | 9 | 5 | 2 | **2** |
| 3.5 Flash | 11 | 7 | 3 | **1** |

Örnek (3.1 FL id 38): *"**TCK 235'e göre** … cezalandırılır."* — altın maddeden verilmiş **doğru
cevap**, alet çekinme saymış. ⇒ **Üstünlüğümüzün bir kısmı aletin eseriydi**; §3'ün GÖZ-katı
sütunu bunu düzeltir.

### Geçerlilik kapıları — koşu bunlardan GEÇTİ

| kapı | değer | eşik | hüküm |
| :--- | ---: | ---: | :--- |
| kesiklik ([ADR-0040](docs/adr/0040-dusunce-modu-olculecek-on-kayitli-kural.md)) | **%5,0** | ≤ %5 | **TAM EŞİKTE, payı yok** |
| `recall@10` sapması | 0,9500 | 0,9500 | birebir — harness oynamamış |
| zorla kapatma | 3/80 | — | (önceki koşuda 5/80) |
| doğrulanan atıf / atıfsız geçen | 114 / **7 kalem** | — | atıfsızlık ayrı bir borç (§7.6) |
| `recall@1 / @3 / @5` | 0,5250 / 0,7625 / 0,8250 | — | tavan kullanımı **0,8433** |

*(hepsi [`KUNYE.json`](outputs/eval/f02-biz-onsozsuz/KUNYE.json) ·
[`harness_tablo.json`](outputs/eval/f02-biz-onsozsuz/harness_tablo.json) ·
[ADR-0069](docs/adr/0069-kabul-testi-tavan-kullanimi-raporlamasi.md))*

### Bu skor kartından KURULMAYAN cümleler

1. **"TEST'te de geçeriz."** Ölçüm **DEV**'de; TEST'in erişim tavanı **≈%75**
   ([ADR-0069](docs/adr/0069-kabul-testi-tavan-kullanimi-raporlamasi.md)) ve kabul testi **koşulmadı** (§5).
2. **"Hakem panelinden geçmiş bir hüküm."** Hâlâ **tek aile** (`gpt-4o-mini`), κ yok,
   öz-tercih **genel olarak** ölçülmedi — yalnız Anthropic ailesi için tek hücrelik bir gösterge
   var, ters yönde (§7.2).
3. **"3.1 FL için kesikliğe duyarlı hüküm."** %6,2 ile bizim kolumuzu düşüren eşiğin üstünde;
   [ADR-0040](docs/adr/0040-dusunce-modu-olculecek-on-kayitli-kural.md) simetrik uygulanmalı.
4. **"Model bu kadar iyileşti."** Bkz. §7.1 — kazancın büyük kısmı **ölçümden** geldi.
5. **"Maliyet-normalize parite."** `$/cevap` artık **ölçüldü** (dipnot ᵍ), ama parite bir
   **Pareto eğrisi** iddiasıdır ([ADR-0017](docs/adr/gemma4-12b-dersler.md#adr-0017)); tek bir
   maliyet satırından **kurulmaz**.
6. **Rakip havuzu tek sağlayıcıdan.** `v1.0`'da en az bir başka sağlayıcı eklenir; ön koşulu
   hakem panelidir ([ADR-0072](docs/adr/0072-v1-rakip-havuzu-genisler.md), açık karar **S16**).

---

## 5 · `v1.0` kapısı — üç madde

Ön-kayıt: **formül 2026-09-06 öğleden önce**, hiçbir rakip sayısı görülmeden yazıldı; çıpa
(`3.5 Flash`) o an **hiç ölçülmemişti**. Sayılar 2026-09-07'de mekanik olarak türedi.
([ADR-0064](docs/adr/0064-v1-kapisi-uc-maddeli-on-kayit.md))

```
(1) kütle ≥ (3.5 Flash'ın kütlesi) − 2,0 puan     ← ASIL KAPI
(2) isabetsizlik GERİLEMEZ
(3) M5 (kör/parametrik) YÜKSELMEZ                  ← ANTİ-HEDEF
(*) her sayım adımında GÖZLE OKUMA zorunlu
```

| madde | hüküm | sayı | kaynak |
| :--- | :--- | :--- | :--- |
| **(1)** kütle | **GEÇTİ** (üç okumanın üçünde de) | GÖZ-katı: **0,8011 ↔ eşik 0,7225** → **+5,86 p** | [`KALIBRASYON_ve_OZET.md`](outputs/eval/f04-rakip-onsozsuz/KALIBRASYON_ve_OZET.md) |
| **(2)** isabetsizlik | *(tanım gereği)* | çıpa yeni birimde **8/80**'e çivilendi | [`GOZLE_OKUMA_80.md`](outputs/eval/f02-biz-onsozsuz/GOZLE_OKUMA_80.md) |
| **(3)** M5 | **GEÇTİ** (iki okumada da) | ezber kütlesi **−6,82 p** (GÖZ) / **−7,98 p** (ALET) | [`f07/KUNYE.json`](outputs/eval/f07-m5-anti-hedef/KUNYE.json) |
| **(*)** gözle okuma | Evet | üç sayım adımında da yapıldı; **ikisinde alet yanıldı** | ↑ |

**Madde (1) üç okumada da geçiyor** — hüküm okuma seçimine bağlı değil:

| okuma | 3.5 Flash | eşik = Flash − 0,020 | BİZ | fark |
| :--- | ---: | ---: | ---: | ---: |
| ALET | 0,6925 | 0,6725 | 0,8011 | +10,86 p |
| GÖZ-orta | 0,7050 | 0,6850 | 0,8011 | +9,61 p |
| **GÖZ-katı (bağlayıcı)** | **0,7425** | **0,7225** | **0,8011** | **+5,86 p** |

*(kaynak: [`KALIBRASYON_ve_OZET.md`](outputs/eval/f04-rakip-onsozsuz/KALIBRASYON_ve_OZET.md) ·
[`harness_tablo.json`](outputs/eval/f02-biz-onsozsuz/harness_tablo.json) · formül
[ADR-0064](docs/adr/0064-v1-kapisi-uc-maddeli-on-kayit.md))*

**Madde (2) hakkında dürüst not:** çıpa spec'te *"≤ 7/80"* yazıyordu, ama o sayı **v1 soru
setinden** geliyordu ve **hiç gözle sayılmamıştı**. v2 biriminde ilk kez tam gözle sayıldı:
**8/80** ([`GOZLE_OKUMA_80.md`](outputs/eval/f02-biz-onsozsuz/GOZLE_OKUMA_80.md) §2 — 75 cevaplanan
kalemin tamamı tarandı). Eşik **gevşetilmedi, birimi düzeltildi** — `7/80` ile `8/80` **aynı
birimde değildir** ([ADR-0064](docs/adr/0064-v1-kapisi-uc-maddeli-on-kayit.md) madde (2)).
Madde bugün tanım gereği sağlanıyor; **bağlayıcı olduğu yer bir sonraki eğitim turudur (B1)**.

### Kapı DEV'de geçildi · donmuş TEST **KOŞTU 2026-09-09** — ama `v1.0` **VERİLMEDİ**

| set | `recall@10` | ⇒ **kütle tavanı** | kaynak |
| :--- | ---: | ---: | :--- |
| **DEV** (80) | 0,9500 | **≈%95** | [ADR-0069](docs/adr/0069-kabul-testi-tavan-kullanimi-raporlamasi.md) · [`harness_tablo.json`](outputs/eval/f02-biz-onsozsuz/harness_tablo.json) |
| **TEST** `core_hard` (40) | 0,7500 | **≈%75** | [ADR-0069](docs/adr/0069-kabul-testi-tavan-kullanimi-raporlamasi.md) · [ADR-0068](docs/adr/0068-rrf-k-60-to-10.md) |

Kütle `= coverage × A1`'dir ve altın madde bağlama girmediyse doğru cevap üretilemez ⇒
**kütle `recall@10`'u aşamaz**. İki sayı **aynı metrik değildir**. Fark setin daha zor sorular
içermesinden değil **bileşimden** geliyor: ayrım kanuna göre katmanlı ama **madde uzunluğuna
göre katmanlanmamış**; en zor uzunluk diliminde DEV'in payı %12, TEST'in **%50** — bileşim
farkın **%81**'ini açıklıyor ([ANALIZ](outputs/eval/f01c-dev-test-farki/ANALIZ.md)).

#### Kabul testi KOŞTU — ham sonuç ([ADR-0077](docs/adr/0077-v1-0-verilmedi-v0-3.md) · [koşu](outputs/eval/g16-kabul-testi/OZET.md))

Donmuş TEST **2026-09-09'da açık insan onayıyla, tek kez** açıldı. Rejim DEV koşusuyla her
eksende birebir, **araçsız** (ADR-0076 m.4). Geçerlilik kapısı geçildi (kesiklik **%2,5**).

| | **TEST** (40) | **DEV** (80) |
| :--- | ---: | ---: |
| **ham kütle — MANŞET** *(ADR-0069 m.1)* | **0,5804** | 0,8011 |
| tavan (`recall@10`) | 0,7500 | 0,9500 |
| **tavan kullanımı** | **0,7739** | 0,8433 |
| **uydurulmuş madde numarası** | **0/52** | 0/114 |
| `wrong_ref_rate_micro` | 0,2424 | 0,0769 |
| aşırı-red | 5/40 [0,055–0,261] | 4/80 [0,020–0,122] *aralıklar örtüşüyor* |

**Düşüşün ayrıştırılması** — süslenmedi: toplam **−22,07 p**; tavan-eşdeğer beklenti 0,6324 ⇒
tavanın açıkladığı **−16,87 p (%76)**, **AÇIKLAMADIĞI −5,20 p (%24)**. ADR-0069'un öngörüsü
doğrulandı **ama tam değil**: model görülmemiş veride tavanını da daha kötü kullanıyor.
*"Hepsi bileşim"* **denmiyor**.

**Gözle okuma kapısı:** 9/40 çekinmenin dokuzu da okundu, açık yanlış pozitif **0** ⇒ ALET = GÖZ.

**`v1.0` VERİLMEDİ; ürün sürümü `v0.3`.** Gerekçe yeni bir eşik değil — donmuş TEST için
**ön-kayıtlı sayısal eşik yoktu** ve sayı görüldükten sonra eşik yazmak ADR-0050'nin yasağıdır.
Hüküm [ADR-0064](docs/adr/0064-v1-kapisi-uc-maddeli-on-kayit.md)'ün **kendi metnine** dayanır:
orada `v1.0` için eksik iki şey sayılı — **(a) kabul testi koşmadı → BUGÜN KAPANDI**,
**(b) her sayı tek hakem ailesinin hükmü → HÂLÂ AÇIK** (κ **0,534** < 0,6, üçüncü hakem
bütçe kararıyla atlandı — §7.2).
⇒ **`v1.0`'ı bloke eden model değil, ölçüm aygıtıdır.**

---

## 6 · M5 anti-hedefi — ezber YÜKSELMEDİ

Kör mod: kaynak **verilmiyor**, harness kapalı. Çıpa **BASE**'dir, rakip değil
([ADR-0039](docs/adr/0039-kapi-6-parametrik-sizinti.md) §2).
Kaynak: [`f07-m5-anti-hedef/KUNYE.json`](outputs/eval/f07-m5-anti-hedef/KUNYE.json).

| kol | okuma | `coverage` | `A1` | **ezber kütlesi** |
| :--- | :--- | ---: | ---: | ---: |
| **BİZ** | ALET | 0,9500 | 0,4105 | **0,3899** |
| **BİZ** | **GÖZ** | 1,0000 | 0,4057 | **0,4057** |
| base | ALET | 0,9750 | 0,4818 | **0,4697** |
| base | **GÖZ** | 1,0000 | 0,4739 | **0,4739** |

**Kapı okuması (biz ↔ base):** model kaynaksızken base'den **daha az** isabetli ve gözle
bakıldığında **iki kol da hiç susmuyor** (80/80 konuşuyor). ⇒ **Kazanç ezberden gelmiyor** —
istenen yön budur: *güncellik kütüphanede, ağırlıkta değil.*

### Rakipler de aynı kör sınavda ölçüldü — ve sayının İKİ YÜZÜ var

Kaynak: [`f10-rakip-m5/KUNYE.json`](outputs/eval/f10-rakip-m5/KUNYE.json) (hakem bedeli $0,1418).

| kol | `coverage` | `A1` | **ezber kütlesi** |
| :--- | ---: | ---: | ---: |
| **BİZ** (ALET) | 0,9500 | **0,4105** | **0,3899** |
| `Qwen3.5-4B` base | 0,9750 | 0,4818 | 0,4697 |
| `gemini-3.1-flash-lite` | 0,9875 | 0,6795 | 0,6710 |
| `gemini-3.5-flash-lite` | 1,0000 | 0,7013 | 0,7013 |
| `gemini-3.5-flash` | 1,0000 | **0,8241** | **0,8241** |

> # *"M5'te rakipleri yendik"* CÜMLESİ KURULMAZ
>
> **Sebep 1 — bu bir ANTİ-HEDEF ve çıpası BASE'dir, rakip değil.**
> [ADR-0039](docs/adr/0039-kapi-6-parametrik-sizinti.md) §2 rakip çıpasını **değerlendirip
> REDDETTİ**: ölçülmek istenen şey *"modeli aldığımız noktadan kötüye götürmedik mi"*dir.
> Rakibin M5'i bizim kapımızda **hiçbir hüküm üretmez**.
>
> **Sebep 2 — aynı sayının ikinci yüzü aleyhimizedir, ve yazılmadan geçilmez.**
> Düşük M5 **bizim için** *"kaynağa dayanıyoruz, ezbere konuşmuyoruz"* demektir. **Ama tam olarak
> aynı sayı** şu anlama da gelir: **Gemini, Türk hukukunu kaynaksızken bizden çok daha iyi
> biliyor.** Kör moddaki `A1`: `3.5 Flash` **0,8241** ↔ biz **0,4105** — **iki katı**.
> Bu bir parametrik bilgi farkıdır ve **gerçektir**; ürün kararımız (bilgiyi ağırlığa değil
> kütüphaneye koymak) onu **ortadan kaldırmaz, sadece ürün için önemsizleştirir**.

**DRY şerhi — ölçüldü ki gerekmiyor.** `DRY` rakiplere **uygulanamadı** (bir `llama.cpp`
örnekleyicisidir). Ama üç rakip kolda da **döngü YOK** ve kesiklik **%0 · %0 · %2,5** — hepsi
eşiğin altında. Yani DRY'nin bizim kolumuzda kırdığı kusur rakiplerde **zaten gözlenmiyor**;
bu, kıyası geçersiz kılmıyor ama **damgalanıyor**.

> **M5 rejimi ayrıdır ve kendi birimindedir.** Koşu `--dry-multiplier 0.8 --dry-base 1.75
> --dry-allowed-length 2` ile yapıldı ([ADR-0073](docs/adr/0073-m5-rejimine-dry-eklendi.md));
> kapsam **yalnız M5** — DRY bir `llama.cpp` örnekleyicisidir, Gemini'ye uygulanamaz, dolayısıyla
> rakip içeren hiçbir modda eşitlenemez. **DRY'li M5, DRY'siz M5 ile aynı birimde DEĞİLDİR**
> (DRY modeli doğru değil **akıcı** yapar; döngü kalemi ile akıcı-yanlış kalem hakemden aynı notu
> almaz) ⇒ `cp09`'un M5 sayılarıyla kıyas **kurulmaz**. Hüküm yalnız yukarıdaki iki kol arasında
> kurulur; iki kol da **aynı** GGUF kuantizasyonu, taşıyıcı, seed, bütçe, istem ve soru setiyle
> koştu — değişen tek şey **model ağırlıkları**. Rakip kolları bu şerhin **dışındadır**: onlar
> DRY'siz koştu (uygulanamıyor) ve yukarıdaki tabloda **ayrı** okunur.

---

## 7 · Sınırlar

### 7.1 Kazancın büyük kısmı MODELDEN DEĞİL, ÖLÇÜMDEN geldi

Faz 0'da (2026-09-06/07) **beş alet kusuru** bulundu. **Eğitim koşusu: SIFIR.**
`tgta_v1`'in ağırlıkları **hiç değişmedi** — bugünkü artefakt, turun başındaki artefaktın aynısı.
Kütle **%68,4 → %80,1**'e bu şekilde çıktı.
([#62](docs/record/research_log/2026-09-06-faz0-olcum-zinciri.md), harcanan ~$1,38)

| # | kusur | ne bulundu | etkisi | ADR |
| :-- | :--- | :--- | :--- | :--- |
| **1** | **Soru seti** | Kaçırılan 10 kalemin **5'inde soru altın maddeyi belirlemiyordu** — sorular altın maddenin *içinden* üretilmiş, bağlamları sökülmüştü. En ağırı: İİK 31/a **gemi sicili** hakkında, sorusu *"Mahkeme benim lehime karar verirse ne olur?"* | DEV 13 + TEST 2 soru yeniden yazıldı (insan onaylı). `recall@10` **0,8750 → 0,9375** | [0067](docs/adr/0067-soru-onarimi-dev-test-v2.md) |
| **2** | **RRF füzyonu** | Kusur BM25'te değil **füzyondaydı**: dört kalemde bir kol altını **0. sırada** bulmuştu, `RRF_K=60` ikisini toplayınca ilk 10'un dışına itiyordu. *"İki kolda vasat olmak, bir kolda mükemmel olmayı yeniyor."* | `RRF_K` **60 → 10** (plato ortası). `recall@10` **0,9375 → 0,9500**. Genelleme **donmuş TEST'te, seçimden SONRA** doğrulandı (+2,5 p, DEV'dekinin iki katı) | [0068](docs/adr/0068-rrf-k-60-to-10.md) |
| **3** | **DEV ↔ TEST bileşimi** | TEST'in `recall@10`'u ~15 p düşük; sebep zorluk değil **bileşim** — ayrım madde **uzunluğuna göre katmanlanmamış**, en zor dilimde DEV %12 ↔ TEST %50. Bileşim farkın **%81**'ini açıklıyor | Kabul testinin kütle tavanı **≈%75**, DEV'in %95'i değil. Raporlama biçimi kabul testi **koşmadan önce** ön-kayıtlandı | [0069](docs/adr/0069-kabul-testi-tavan-kullanimi-raporlamasi.md) |
| **4** | **Üretim bütçesi rakiple EŞİT DEĞİLDİ** | Rakip `1536` bütçeyle koşuyordu, **biz yaygın durumda `1024`** ile. Kod ADR-0043'e **sadıktı**; kusur protokolün kendisindeydi. Sapma **bizim aleyhimizeydi** (3.1 FL'nin 36/80 kalemi 1024'ü fiilen aşıyordu). Bu, **yayımlanmış bir hükmü çürüttü** (`g2-fl-harness/OZET.md` §K2) | Tek formül: `max_tokens = (reasoning_budget or think_budget or 0) + max_new_tokens` = **1536**, iki tarafta da | [0070](docs/adr/0070-uretim-butcesi-esitlendi.md) |
| **5** | **Kapı maddesinin ÇIPASI YOKTU** | Madde (3) *"M5 ≤ **bugünkü**"* diyordu, ama `tgta_v1`'in M5'i **hiçbir birimde hiç ölçülmemişti** — madde **kendi kendine referans veriyordu** ve hiçbir hüküm üretemezdi. Ön-kayıt kuralına uyduğu için denetimden geçmişti. Ayrıca ADR-0040'ın *"MAXTOK büyüt"* reçetesi yozlaşmış tekrarda **ölçülmüş biçimde etkisiz** çıktı | Çıpa ADR-0039 §2'den okundu (**base**), base aynı birimde yeniden koşuldu; M5 rejimine **DRY** eklendi. Yeni tuzak sınıfı **2.17** | [0073](docs/adr/0073-m5-rejimine-dry-eklendi.md) |

> **Ders:** beş kusurun beşi de *"hata vermeden yanlış sayı üreten"* sınıftandı. **Sayısal
> kapılar beşini de geçirdi**; hepsini **gözle okuma** ya da *"bu sayıyı neyle, hangi birimde
> kıyaslayacağım?"* sorusu yakaladı.

**Ayrıca dedektör üç kez yanıldı, üçünde de aynı yönde (fazla red):**

| # | nerede | alet → göz | kaynak |
| :-- | :--- | :--- | :--- |
| 1 | bizim şablon, önsözsüz | 14 → **8** | [ADR-0061](docs/adr/0061-cekinme-dedektoru-istem-rejimi-bagimliligi.md) |
| 2 | Gemini şablonu, F0.4 | 11 → **7** | [`KALIBRASYON_ve_OZET.md`](outputs/eval/f04-rakip-onsozsuz/KALIBRASYON_ve_OZET.md) |
| 3 | kör mod, iki kol | 6 → **0** | [`GOZLE_OKUMA_CEKINME.md`](outputs/eval/f07-m5-anti-hedef/GOZLE_OKUMA_CEKINME.md) |

Açık borç: `exact_reject`'in **kör mod dalı**. Bugün düzeltilmedi — kapının sayısı
üretildikten sonra aleti değiştirmek [ADR-0050](docs/adr/0050-verim-kapisi-tahmin-edici-duzeltmesi.md)'nin
yasakladığı hareketin sınırındadır. Doğru sıra: ölç → iki okumayı da raporla → **sonraki turda,
koşudan ÖNCE** düzelt.

### 7.2 Her sayı hâlâ TEK hakem ailesinin hükmü

Bu karttaki **bütün** hüküm-ekseni sayıları (`A1`, kütle, `Rej`) tek bir LLM hakem ailesinden
gelir: `openai/gpt-4o-mini`, **runs=1**
([`gnd_…_summary.json`](outputs/eval/f02-biz-onsozsuz/gnd_h1_tgta_v1_f02_nb_summary.json)).

- **κ ÖLÇÜLDÜ 2026-09-07 ve EŞİĞİN ALTINDA ÇIKTI.** İkinci hakem ailesi
  (`anthropic/claude-sonnet-5`) **aynı 80 cevabı** yeniden puanladı (üretim yeniden koşulmadı,
  ADR-0017): `tam_sadık` κ = **0,534** · `atıf_temiz` κ = **0,409** — aracın kendi *"makul"*
  eşiği **0,6**'nın altında. `faithfulness` Pearson r = 0,705.
- **Kayma TEK YÖNLÜ:** Anthropic **24/80** kalemde daha düşük, **8/80**'de daha yüksek not
  verdi ⇒ rastgele gürültü değil, **sistematik katılık**. A1 farkı **11,33 puan** = gürültü
  tabanının (0,3) **38 katı**.
- **Manşet hakem seçimine duyarlı:** kütle **0,8011** (`gpt-4o-mini`) ↔ **0,6940**
  (`sonnet-5`). `coverage` kıpırdamadı (hakemden bağımsız); farkın tamamı `A1`'den.
- **Ama bu ikinci sayı YAYIMLANMIYOR ve kapıya girmiyor** — çünkü kapının eşiği çıpa rakip
  `3.5 Flash`'ın kütlesinden türetildi ve **o da `gpt-4o-mini`'nin hükmüdür**. İki tarafı
  farklı hakemlerle kıyaslamak [ADR-0057](docs/adr/0057-harness-rekabet-kapisi-esit-sinav.md)'nin
  *eşit sınav* kuralının yasakladığı şeydir. Bağlayıcı hakem **`gpt-4o-mini` kaldı** — tercih
  değil, kuralın sonucu ([ADR-0074](docs/adr/0074-hakem-paneli-kuruldu-baglayici-hukum.md)).
- **Panel İKİ aileli kaldı** ([ADR-0032](docs/adr/0032-hakem-paneli-uc-aile-ve-aile-dislama.md)
  üç öngörüyordu) — sapmanın sebebi sayıyla: bakiye **$3,45**, rakip kolunun ikinci hakemle
  puanlanmasının tahmini gerçek faturası **$2,81**, ve donmuş TEST kabul koşusu da aynı
  bakiyeden ödenecekti. **İnsan kararı: harcanmadı.**
- **Öz-tercih artık genel olarak değil, yalnız Anthropic ailesi için ÖLÇÜLDÜ** (ADIM 6.6b,
  2026-09-12): `claude-sonnet-5` rakip havuzuna özne olarak girdiği için aynı-aile hücresi
  (özne=Sonnet-5, hakem=Sonnet-5) kuruldu. Sonuç **kayırma LEHİNE değil**: Anthropic hakem
  kendi ailesinin cevaplarını, `gpt-4o-mini`'ye göre, bizim (çapraz-aile) kolumuzdan **DAHA
  BÜYÜK** bir düşüşle cezalandırdı (**20,03 p ↔ 10,71 p**, çözünürlüğün — 1,25 p — çok üstünde
  bir fark) ⇒ bu tek hücrede **ek katılık** ölçüldü, kayırma değil
  ([`OZ_TERCIH.md`](outputs/eval/hp-oz-tercih-anthropic/OZ_TERCIH.md)). Tek özne/tek hakem/tek
  koşu ⇒ **gösterge**, kanıt değil; bu kartın hiçbir sayısına girmez. Google özne ↔ Google
  hakem hücresi **aile dışlaması gereği hiçbir bütçeyle ölçülemez** ⇒ *"öz-tercih ölçüldü"*
  cümlesi **genel olarak hâlâ kurulmaz**.
- **İnsan-κ kapsam dışı** (DESCOPED).
- Hakemin yeniden-koşum **gürültü tabanı ~0,3 `A1` puanı**; bundan küçük hiçbir fark
  yorumlanmaz. Bu taban **yalnız `A1` için** ölçüldü — **kütle** `= coverage × A1` ve
  `coverage`'ın varyansı o tabanda **yok** ([ADR-0064](docs/adr/0064-v1-kapisi-uc-maddeli-on-kayit.md) §δ).

⇒ Bu sayılar **mutlak doğruluk değil, model-vs-model sıralaması** olarak okunmalıdır — ve
artık *"tek hakem"* bir usul borcu değil, **büyüklüğü ölçülmüş bir kırılganlıktır**: manşet
hakem değiştiğinde **11 puan** oynuyor.
[`KAPPA.md`](outputs/eval/hp-hakem-paneli/KAPPA.md) · [#64](docs/record/research_log/2026-09-07-hakem-paneli-iki-aile.md)

### 7.3 Kabul edilen üç bedel — "gelecek çalışma" değil, KALICI maliyet

Tek boyut noktası (~4B) ve tek base kararının bedelleri; `CLAUDE.md` bunları
*"Limitations'da görünecek, gelecek çalışma diye geçiştirilmeyecek"* diye bağlıyor:

| # | bedel | anlamı |
| :-- | :--- | :--- |
| **a** | **Dış geçerlilik boşluğu KAPANMIYOR** | *"Bu bulgular bu base'e mi özgü?"* sorusu **cevapsız kalır**. |
| **b** | **Kapasite sorusu ÖLÇÜLEMEZ** | *"Beceri çatışması kapasite büyüdükçe küçülüyor mu?"* tek boyut noktasında **sorulamaz** bile. |
| **c** | **[ADR-0018](docs/adr/gemma4-12b-dersler.md#adr-0018)'in EĞRİSİ yok** | Maliyet-başarım **eğrisi** yerine **tek işaretli nokta** raporlanıyor. |

### 7.4 ARA KAPI DÜŞTÜ — iddia sürümü buna bağlı

**2026-08-06:** ön-kayıtlı olan **formüldü** (`merge M2b ≥ 0,90 × base'in cevaba-kör M2b'si`),
sayı değil. Tek onarılmış aletle yeniden türetildi:

| nicelik | değer | kaynak |
| :--- | ---: | :--- |
| eşik | **0,8649** | [ADR-0045](docs/adr/0045-ara-kapi-merge-onarim-kontrolu.md) |
| merge M2b | **0,766** | [`abst_m2b_tg_ta_ham_th_summary.json`](outputs/eval/cp3-supurme-ham/abst_m2b_tg_ta_ham_th_summary.json) |
| **fark** | **−9,9 puan** | [#58](docs/record/research_log/2026-08-06-payda-tekillesmesi.md) |

Paydalar eşit (77 ↔ 77); eski 0,887 eşiğini de geçemiyor. [ADR-0050](docs/adr/0050-verim-kapisi-tahmin-edici-duzeltmesi.md)
gereği **alet** düzeltildi, **eşik oynatılmadı**.

**Sonucu:** bu kapı CP4-CP5 taban harcamasını yetkilendiren kapıydı — **o yetki yok**.
Dolayısıyla *"merge, çatışan becerileri ardışık/karışık SFT'den daha iyi koruyor"* iddiası
**KANITLANMAMIŞTIR**.

Sürüm bu yüzden **ikiye ayrıldı** ([ADR-0065](docs/adr/0065-bolunmus-surumleme.md)):

```
ÜRÜN sürümü    v0.2 → v1.0    "çalışıyor, indirilebilir, yayımlanan sayı yeniden üretilebilir"
İDDİA sürümü   ARA KAPI'ya bağlı kalır — CP4-CP5 yetkisi geri gelmeden ilerlemez
```

**Düşmüş kapı düşmüş kalır.** Gevşetilmedi, yeniden tanımlanmadı.

### 7.5 Açık borçlar

| borç | bugünkü değer | not | kaynak |
| :--- | :--- | :--- | :--- |
| **isabetsizlik (B1)** — **birinci sıra eksen** | **8/80** | Model **yanlış maddeye** dayanıyor; atıf doğrulanıyor, kapı geçiriyor, cevap yine de soruya oturmuyor. **Otomatik vekil metrik YOK ve bu ölçüldü:** `faith<0,6` süzgeci 4, *"altın atıflarda yok"* süzgeci 3, **gözle tam tarama 8** buluyor. [ADR-0055](docs/adr/0055-isabet-denetimi-ekseni.md)'in kodu hiç açılmadı | [`GOZLE_OKUMA_80.md`](outputs/eval/f02-biz-onsozsuz/GOZLE_OKUMA_80.md) §2 |
| **uzun madde chunk'lama** | ölçülmedi | Erişim madde uzunluğunda **U biçimli** (Q4 dilimi `recall@10` **0,6667**). B9'dan ayrı bir borç: orada **bozuk** chunk, burada **doğru ama çok uzun** chunk ([ADR-0054](docs/adr/0054-harness-tasarim-kararlari-k2-k5.md)/K2'nin ilk ölçülen bedeli) | [ADR-0069](docs/adr/0069-kabul-testi-tavan-kullanimi-raporlamasi.md) · [ANALIZ](outputs/eval/f01c-dev-test-farki/ANALIZ.md) |
| **DEV/TEST ayrımı katmanlanmamış** | — | Ayrım kanuna göre kusursuz katmanlı (2:1) ama **madde uzunluğuna göre değil**. Donmuş TEST'i yeniden katmanlamak **reddedildi** — usulü kırar | [ADR-0069](docs/adr/0069-kabul-testi-tavan-kullanimi-raporlamasi.md) |
| **M2b — en zayıf eksen; planlanan çözüm ÖLÇÜLEREK ÖLDÜ** | **0,766** | Yalnız distractor verildiğinde model yine de cevaplıyor. **Red kapısı** bu kusurun çözümü olarak kurulmuştu; 2026-08-05'te **eşleşmiş sınavda** koşuldu ve **ekseni kötüleştirdi: 0,735 ↔ 0,766** (işaret ᴷ³ yeniden puanlamasından sonra da aynı). Mekanizması da **ölçülerek boş** çıktı: `KANUN_YOK 0` · `MADDE_YOK 0` — model etiketi bağlamdan **kopyalıyor**, dolayısıyla atıfları doğrulanıyor ve kapı onları geçiriyor. ⇒ Deterministik kod bu rejimde M2b'yi **kapatamaz**; borç **eğitime** taşındı | [#56](docs/record/research_log/2026-08-05-olcum-bosluklari.md) · [`abst_h2b_…_summary.json`](outputs/eval/g2b-m2b-onsozlu/abst_h2b_tgta_v1_onsozlu_k4_summary.json) |
| **aşırı-red küçüldü, ÇÖZÜLMEDİ** | 4/80 | B10 turu **eğitimsiz** kapandı; *"eğitim bunu ne kadar aşağı çekerdi"* **hiç ölçülmedi** | [ADR-0062](docs/adr/0062-b10-turu-kapatildi-hedef-egitimsiz-karsilandi.md) |
| **`exact_reject` kör mod dalı** | — | §7.1'de damgalandı; sonraki turda **koşudan önce** düzeltilir | [`GOZLE_OKUMA_CEKINME.md`](outputs/eval/f07-m5-anti-hedef/GOZLE_OKUMA_CEKINME.md) |
| ~~**kuantizasyon eğrisi**~~ | ~~ölçülmedi~~ | ~~`Q5_K_M`/`Q8_0`'ın kütle kaybı **bilinmiyor**; [ADR-0031](docs/adr/0031-precision-inference-q4km-egitim-bf16-lora.md) hassasiyeti *seçti*, **kaybı ölçmedi**. Açık karar **S17**~~ | [ADR-0071](docs/adr/0071-v1-release-artefakti-tek-gguf.md) |
| **kuantizasyon eğrisi** — **S17 KAPANDI 2026-09-12** | ölçüldü | `Q4_K_M`(yayımlanan) 0,8011 · `Q4_K_M`@bugün 0,7921 (araç zinciri farkı **çözünürlük altında**, −0,90 p) · `Q5_K_M` 0,8673 (+6,0 adım) · `Q8_0` 0,7909 (−0,1 adım vs Q4) — eğri **monoton değil**, mekanizma **ölçülmedi** (açık soru, hüküm kurulmadı). Artefakt kararı **ayrı**: ADR-0071 yürürlükte, `Q4_K_M` yayımlı kalır | [ADR-0071](docs/adr/0071-v1-release-artefakti-tek-gguf.md) · [`outputs/eval/s17-kuantizasyon-egrisi/OZET.md`](outputs/eval/s17-kuantizasyon-egrisi/OZET.md) · [#68](docs/record/research_log/2026-09-12-kuantizasyon-egrisi.md) |
| **ürün paketi (CLI/TUI)** | yok | Yayımlanan sayı bugün yalnız **eval koşucusuyla** yeniden üretilebilir; paketleme Hat A'nın işi (`v0.2`). **2026-09-12'de `hakhukuk/` paketi doğdu** (CLI · TUI · HTTP API · araç katmanı); kalan borç paketin `scripts/`'e bağımlılığıdır — açık kusur **11** | [ADR-0083](docs/adr/0083-kusur-sicili-adrye-tasindi.md) · [#67](docs/record/research_log/2026-09-12-konteyner-ve-alet-onarimlari.md) |
| **bedesten canlı mevzuat API'si** | bağlanmadı | Sözleşme doğrulandı (4/4) ama **ürün henüz kullanmıyor** — borç **B6** | [`BEDESTEN_API.md`](docs/BEDESTEN_API.md) |

> **Harness'ın kendi gerekçelerinden İKİSİ de çürütüldü, ve bu kartın okunma biçimini
> değiştirir.** (1) *"Atıf doğrulayıcı isabetsizliği kapatır"* — **ölü**: uydurulmuş madde
> numarası **0/114**, yani sınıf **boş**; doğrulayıcının kapattığı kusur zaten olmuyordu.
> (2) *"Red kapısı M2b'yi kapatır"* — **sınandı ve kapı düştü** (yukarıdaki satır).
> Ayakta kalan gerekçe *"retriever olmadan ürün olmaz"* ve ölçülmüş bir dizi mekanizmadır.

### 7.6 Modelin kendi davranış kusurları

| # | kusur | ölçüm | kaynak |
| :-- | :--- | :--- | :--- |
| 1 | **Akıl yürütme izi İNGİLİZCE** | 8/8 | [`kollar.md`](docs/record/kollar.md) |
| 2 | **`τ_a` bir ŞABLON öğrendi** — tipik çekinmesi sabit bir cümle (medyan cevap **58 karakter**) | ölçüldü, risk olarak ön-kayıtlandı | [`kollar.md`](docs/record/kollar.md) |
| 3 | **Model cevaptan önce düşünüyor** — ort. **782,5** completion token | ücretsiz değil; 3.5 FL **171,1** token'da bitiriyor | [`KALIBRASYON_ve_OZET.md`](outputs/eval/f04-rakip-onsozsuz/KALIBRASYON_ve_OZET.md) |
| 4 | **Kesiklik tam eşikte** — %5,0 ↔ eşik %5 | payı yok; 4 kalem 1536'ya da sığmıyor, **izleniyor** | [`KUNYE.json`](outputs/eval/f02-biz-onsozsuz/KUNYE.json) |
| 5 | **7/80 cevap hiç atıf taşımıyor** | denetlenebilirlik vaadinin doğrudan bedeli | [`harness_tablo.json`](outputs/eval/f02-biz-onsozsuz/harness_tablo.json) |
| 6 | **`A1` TEK altın maddeye göre puanlanıyor** | başka **gerçek** bir maddeden doğru cevaplamak **sadakatsiz** sayılır ⇒ ON/OFF kıyasında **altın getirilen alt küme** satırı kullanılır | [`harness_tablo.json`](outputs/eval/f02-biz-onsozsuz/harness_tablo.json) `not` |

### 7.7 Kendi aleyhimize iki kayıt

1. **8 isabetsizliğin 2'si (id 27 · 42) BENİM yeniden yazdığım sorularda.** Durumu tarif
   ederken **komşu maddenin dilini** kullanmışım (KMK 25'in açılışı · TBK 214'ün ifadesi) —
   [ADR-0067](docs/adr/0067-soru-onarimi-dev-test-v2.md)'nin yanlılık koruması **ters yönde**
   işledi. Sayıyı şişirmedi, **aleyhimize** çalıştı. Sorular **düzeltilmedi**: geri almak,
   eval sorusunu sonucu gördükten sonra ayarlamak olurdu.
2. **Bir erişim kaybı geri ALINMADI (id 79).** Eski soru öncülsüzdü ama içindeki *"eğitim"*
   sözcüğü maddeyle eşleşiyordu; yeni soru o sözcüksel çıpayı kaybetti ve kalem
   **bulunuyorken kaçtı**.

*(ikisi de [`GOZLE_OKUMA_80.md`](outputs/eval/f02-biz-onsozsuz/GOZLE_OKUMA_80.md) ·
[#62](docs/record/research_log/2026-09-06-faz0-olcum-zinciri.md))*

---

### 7.8 Parametrik bilgide gerideyiz — **ama emniyet ağı iddiası ÖLÇÜLDÜ ve ÇÜRÜDÜ**

Kör modda (kaynak verilmeden) `A1`: biz **0,4105** ↔ `3.5 Flash` **0,8241** — **iki katı**
([`f10/KUNYE.json`](outputs/eval/f10-rakip-m5/KUNYE.json) · [`f07/KUNYE.json`](outputs/eval/f07-m5-anti-hedef/KUNYE.json)).
Gemini hattı Türk hukukunu **kaynaksızken bizden çok daha iyi biliyor**. Bu doğru.

**Bu karttaki bir önceki sürüm buradan şu sonucu çıkarıyordu:** *"retriever'ın ıskaladığı
yerde arkamızda parametrik emniyet ağı yok ⇒ erişim kalitesi bizde daha kritik."* Cümle
**mantıklı görünüyordu; ölçüldü ve VERİ ONU DESTEKLEMEDİ.**

**Ölçüm (2026-09-07):** dört öznenin **dördü de aynı 4 kalemi** kaçırıyor (id **10 · 21 · 51 · 79**)
— harness özdeş olduğu için (`recall@10 = 0,9500`, dördünde de aynı). O 4 kalemde hakem sadakati:

| özne | kaçan 4 kalemde `A1` | altın **geldiğinde** `A1` |
| :--- | ---: | ---: |
| **biz** | **0,000** | **0,885** |
| 3.1 Flash-Lite | 0,125 | 0,756 |
| 3.5 Flash-Lite | 0,196 | 0,836 |
| 3.5 Flash | 0,167 | 0,861 |

⇒ **Parametrik üstünlük, harness'ın kaçırdığı yerde işe yaramıyor.** Rakiplerin oradaki sadakati
**0,13-0,20** — pratikte hepsi başarısız. Ezberden bildikleri hukuku o kalemlerde **yanlış kanuna**
bağlıyorlar; gözle okuma bunu tek tek gösteriyor: id 10 → altın 6284/10 yerine **HMK 393**,
id 21 → altın TBK 99 yerine **VUK 215 + Euro Kanunu**
([`GOZLE_ISABETSIZLIK_3_5_FLASH.md`](outputs/eval/f04-rakip-onsozsuz/GOZLE_ISABETSIZLIK_3_5_FLASH.md)).

**Ve altın geldiğinde tablo tersine dönüyor: kaynağı en iyi kullanan BİZ'iz** (0,885 ↔ 0,861 ↔
0,836 ↔ 0,756). Ürün rejimi tam olarak bu rejimdir.

**Doğru sınır cümlesi şudur:** parametrik bilgi eksikliği **bir emniyet ağı kaybı değildir** —
çünkü ölçüldüğünde kimsede öyle bir ağ **çalışmıyor**. Gerçek sınır, **erişimin kendisidir** ve o
sınır **dört özne için de aynıdır**. ⇒ Kaldıraç parametrik bilgi değil, **retriever** ve
**getirilemediğinde susma** davranışıdır (bugün 1/4 susuyoruz; rakipler 1-2/4 — fark 4 kalemde,
**gürültü içinde**).

**Bu düzeltmenin kendisi kayda geçer:** makul görünen bir çıkarım, ölçülünce çürüdü. Bu kartta
*"ölçülmemiş bir çıkarımı sınır olarak yazmak"* hatası **bir kez yapıldı ve düzeltildi**.

---

### 7.9 Ürün yolu ile ölçüm hattı aynı şeyi çalıştırmıyor — cevapların %5'i BOŞ

**Ölçüldü 2026-09-09**, 80 kalemlik DEV kümesinde, `hakhukuk.servis.answer()` ile.
Bu, bu kartın manşet sayısının üretildiği hat **değildir**.

| | ürün yolu | ölçüm hattı *(0,8011 buradan)* |
| :--- | ---: | ---: |
| kesik veya boş cevap | **7/80 = %8,75** | 4/80 = %5,0 |
| **tamamen boş metin** | **4/80 = %5,0** (id 7 · 64 · 65 · 66) | **0** |
| suskunluk kümesi | [10, 34, 63] | [15, 37, 45, 66, 79] |

Yedi kesik kalemin **yedisi de** ölçüm hattında `finish=stop` ile tamamlanıyor (485-892
belirteç) ⇒ sorun soruların zorluğu değil, **bütçe mimarisi**. Ölçüm hattı düşünceyi 1024'te
zorla kapatıp cevaba ayrı 512 veriyor; ürün yolu ikisini tek havuzda (1536) yarıştırıyor.
Sonuç [#42](docs/record/research_log/2026-07-29-cp0-dusunce-modu-sonlanmama.md)'nin ölçtüğü
**sonlanmama**: model `</think>` etiketini kapatmıyor, bütçeyi düşünce kanalında bitiriyor,
HTTP 200 ile **boş içerik** dönüyor.

Boş cevap **gizlenmiyor** — durum `KESIK` damgalanır, arayüzde *"cevap YARIM"* uyarısı çıkar.
Ama kullanıcı için sonuç boş ekrandır. **ADR-0040'ın geçerlilik kapısı %5'tir; ölçüm hattı tam
eşikte geçmekte, ürün yolu %8,75 ile geçememektedir.**

Düzeltilmedi: ürün yoluna zorunlu kapatma koymak bir **rejim değişikliğidir** ve yeniden ölçüm
ister. Açık borç olarak kayıtlıdır. Ölçüm artefaktları:
[`aracsiz_yol_80.json`](outputs/eval/g18-arac-katmani/aracsiz_yol_80.json) ·
[`ORNEK_CEVAPLAR.md`](outputs/eval/g18-arac-katmani/ORNEK_CEVAPLAR.md).

---

### 7.10 Sunucu bayrakları sonucu DEĞİŞTİRİR — yayımlanan artefakt için bağlayıcı

**Ölçüldü 2026-09-09**, kontrollü deney: aynı soru, aynı kod, seed 3407, sıcaklık 0; değişen
tek etken `llama-server`'ın KV önbelleği kuantizasyonu.

| KV önbelleği | durum sınıfı | cevap `sha256` | uzunluk |
| :--- | :--- | :--- | ---: |
| `q8_0` *(bütün ölçümlerin yapıldığı)* | SUSKUNLUK | `79b6915a…` | 201 |
| varsayılan (fp16) | ÇEKİNCELİ | `e97a2b85…` | 622 |

Aynı yapılandırmada üretim **yinelenebilir** (iki koşu, özdeş `sha256`) ⇒ bu belirsizlik değil,
**yapılandırmanın sonucudur**. `servis.py`'nin *"aynı soru aynı cevabı verir"* değişmezi
yapılandırma sabitken geçerlidir; bu şerh oraya da düşmelidir.

Bağlayıcı yapılandırma: `-ngl 99 -fa on --no-context-shift --cache-type-k q8_0
--cache-type-v q8_0 -c 8192`. HF kartının 3. bölümüne yazıldı.

~~**Farkın 80 kalemdeki toplam etkisi ÖLÇÜLMEDİ.**~~ → **ÖLÇÜLDÜ 2026-09-11** (Görev 22 Adım 1-2).
Kaynak: [`KARSILASTIRMA.md`](outputs/eval/g22-kv-fp16/KARSILASTIRMA.md) · [`KUTLE.md`](outputs/eval/g22-kv-fp16/KUTLE.md).
80 kalemin **65'i** (%81,2) fp16'da **bayt olarak değişti**, ama hiçbir sayaç birden fazla kalem
oynamadı (kesik 4→3 · tamamen boş 0→0 · çekinme 5→5 · uydurulmuş madde 0→0). **Kütle
0,8011 → 0,7932** (−0,79 p) — gürültü tabanının 2,8 katı, **ama tek yönlü hükme yetmiyor**:
o taban *aynı cevaplara* hakemi yeniden koşmanın gürültüsüdür ve burada cevaplar da değişti;
bu koşu çiftinin **kendi tabanı ölçülmedi**. Tabanın **açıkça** üstündeki tek eksen atıf
isabetidir ve **kötüleşti**: `wrong_ref_rate_micro` **0,0769 → 0,1553 (2,0×)**.
⇒ **İnsan kararı 2026-09-11: taşıyıcı rejim `q8_0` KALIR** — aşağıdaki bağlayıcı yapılandırma
artık bir **karardır**, tercih değil. *(Bu paragraf, eski "ölçülmedi" cümlesini geçersiz kılar;
cümle silinmedi, üstü çizildi — çelişki damgalanır, gizlenmez.)*

**Eski cümlenin devamı, kaydı bozmamak için aynen:** Dolayısıyla varsayılan KV ile 0,8011'in
korunacağı **iddia edilmiyor**. Açık borç; ölçümü $0 ve ~1 saat GPU.

---

## 8 · Kullanım

### Ürün katmanı — `hakhukuk/` *(2026-09-07)*

Model artık **elle kurulan bir boru hattı değil**; retriever, istem ve atıf doğrulama tek bir
arayüzün arkasında:

```bash
llama-server -m models/gguf/tgta_v1-q4_k_m.gguf -ngl 99 -fa on \
             --cache-type-k q8_0 --cache-type-v q8_0 -c 8192 --port 8080 &

hakhukuk "Askerlik nedeniyle iş sözleşmesi ne olur?"   # CLI
hakhukuk-tui                                            # tek ekran TUI
```

```python
from hakhukuk import servis
cevap = servis.answer("Kat malikleri kurulu hangi çoğunlukla karar alır?")
cevap.durum      # Durum.CEVAP | CEKINCELI | SUSKUNLUK | KESIK
cevap.atiflar    # her atıfta dogrulandi: getirilen kaynakta VAR mı
cevap.kaynaklar  # modele hangi maddeler verildi
```

Dört şey **kullanıcı yüzünde** garanti edilir:

| garanti | nasıl |
| :--- | :--- |
| Doğrulanmamış atıf **uyarıyla** gösterilir, gizlenmez | `terazi.siniflandir()` — kimlikler `madde_anahtari` ile normalleştirilerek karşılaştırılır |
| **Kesik** cevap kesik olduğunu söyler | `finish_reason="length"` → `Durum.KESIK`; sessizce yutulmaz |
| Kaynak bulunamazsa **model çağrılmaz** | `servis.answer()` — üründe M5 (kaynaksız ezber) koşulu **oluşmamalı** |
| **Mülga madde gösterilmez** | `retriever.getir()` varsayılanı `Yururluk.YALNIZ_YURURLUKTE` — ölçüldü: sızıntı 2 → 0, `recall@10` değişmedi |

Sorumluluk ibaresi **koşulsuz** basılır (durum ne olursa olsun) ve metni tek kaynakta durur
(`hakhukuk/cli.py::SORUMLULUK_IBARESI`). **Nihai hukuki metin hâlâ açık — S10.**

### Konteyner yolu — `docker compose up` *(2026-09-11)*

> ✅ **UÇTAN UCA DOĞRULANDI — 2026-09-11.** `docker compose up` **koştu** ve ürün konteynerin
> içinden soru cevapladı. Gözlenenler (tahmin değil, ölçüm):
>
> | ölçü | değer | kaynak |
> | :--- | :--- | :--- |
> | `indir` çıkış kodu | **0** — `sha256` + bayt kapısı **ateşlendi ve tuttu** | `docker logs hakhukuk-indir-1` |
> | `llama` / `app` | **healthy** / **Up** | `docker inspect` |
> | uçtan uca | **HTTP 200**, iki farklı soru; boş sorgu **422** | [`g20-imaj-olcumu/BULGU.md`](outputs/eval/g20-imaj-olcumu/BULGU.md) |
> | `hakhukuk:0.3.0` | ~~2,13 GB~~ → **2,08 GB** (2026-09-12) | `docker images` |
> | `llama.cpp:server-cuda-b10902` | **6,99 GB** | ″ |
> | imajdaki `torch` | **`2.14.0+cpu`** · `version.cuda = None` | imajın içinde koşularak |
>
> **`hakhukuk:0.3.0` boyutu 2026-09-12'de düştü (kusur 29 KAPANDI):** `.dockerignore`'a
> `data/corpus/*.yedek-*` eklendi (commit `b78d142`) — ürünün hiç okumadığı 36,1 MiB korpus
> yedeği artık imaja girmiyor. Eski sayı silinmedi, üstü çizili bırakıldı (bkz.
> [`ADR-0083`](docs/adr/0083-kusur-sicili-adrye-tasindi.md) kusur 29).
>
> Ağırlık ve indeks **imajda YOK** (`find / -xdev` ile `.gguf`/`gomme.npy` **0 eşleşme**).
>
> ⚠️ **Üç şerh, hiçbiri giderilmedi ve *"gelecek işi"* diye geçiştirilmiyor.**
> **(a)** `git clone` sonrası **indeks dizinini insan doldurmak zorunda** — `G8` bekletiliyor,
> indeks ne HF'te ne imajda; `indir` bu durumda **kasten** sıfırdan farklı kodla çıkar ve iki
> daemon da **hiç başlamaz**. Kusur kapanmadı, **görünür** oldu.
> **(b)** Korpus artık **üç yerde**: repo · imaj · volume. `indir` imaj↔volume `sha256`
> eşitliğini **her koşuda** sınar ve tutmazsa erken patlar; ama **repo↔imaj** ayrışması
> **sınanmaz** — kalıcı çare paketin `scripts/`'ten kurtulmasıdır (açık kusur 11).
> **(c)** ~~Uçtan uca doğrulama **iki soru** ile yapıldı. §7.9'un **boş cevap** kusuru
> (ürün yolunda ~%5) bu koşuyla **ölçülmedi** ve konteynerde de **giderilmiş değildir**.~~
> **ÖLÇÜLDÜ 2026-09-12 (Adım 6.3.4) — cümle artık YANLIŞ, üstü çizili bırakılıyor, silinmiyor.**
> 80 DEV sorusu konteynerin HTTP API'sinden (`127.0.0.1:8000/sor`, `hakhukuk.servis` host'tan
> ÇAĞRILMADI) koşuldu: boş cevap **0/80**, HTTP 200 **80/80**, kesiklik **4/80 = %5,00**
> (ADR-0040 eşiğinde tam — **GEÇTİ, payı yok**; çıpa koşusu `f02-biz-onsozsuz`'un kesikliği de
> aynı orandaydı, iki farklı hat aynı sayıya düştü). ADR-0080'in ürün-yolu onarımı **konteynerde
> de tutuyor**. Künye [`g23-konteyner-urun-yolu-80/KUNYE.json`](outputs/eval/g23-konteyner-urun-yolu-80/KUNYE.json)
> (bayraklar koşan süreçten okundu, tuzak 1.12); 80 cevabın kendisi
> `outputs/eval/g23-konteyner-urun-yolu-80/urun_yolu_80.json`'da saklı — **kütlesi henüz
> puanlanmadı**, bu ölçüm yalnız boş/kesik sayar (6.3b'nin girdisi).

Paketleme bir **rejim kilididir**, kolaylık değil: §7.10'un ölçtüğü bayraklar düz metin olarak
üç belgede duruyordu ve hiçbiri kapı değildi. Üç kutu, iki daemon, iki imaj
([ADR-0078](docs/adr/0078-konteyner-dagitimi-rejim-kilidi.md) ·
[ADR-0082](docs/adr/0082-app-kutusu-host-sapmasi.md)): `indir` kutusu GGUF'u **pinlenmiş
revizyondan** `sha256` + bayt sayısı kapısının arkasından çeker; kapı tutmazsa çıkış kodu ≠ 0
olur ve **iki daemon da hiç başlamaz**.

```bash
export HF_TOKEN=...                # ağırlık deposu ÖZEL — tokensız 401
export HAKHUKUK_INDEKS_DEPO=...    # varsayılanı bilerek BOŞ (aşağıya bakın)
docker compose up
```

| | |
| :--- | :--- |
| API | `127.0.0.1:8000` |
| `llama-server` | `127.0.0.1:8080` |
| `HF_TOKEN` | **zorunlu** — depo bugün **özeldir**; tanımsızsa compose hiçbir şey başlatmadan **önce** hata verir |
| `HAKHUKUK_INDEKS_DEPO` | **bilerek boş** — `G8` (indeks dağıtımı) bekletiliyor ⇒ yayımlanmış indeks deposu **yok**. İndeks ya volume'e elle konur ya depo adı verilir; aksi hâlde `indir` kutusu **kasten** patlar |
| gereksinim | NVIDIA GPU + Docker. Ölçülen ortam: Docker **28.4.0** · compose **v2.39.4-desktop.1** · RTX 5070 Ti Laptop **12227 MiB** · sürücü **591.97**. `gpus: all` anahtarı compose **v2.30+** ister |
| imaj etiketi | `hakhukuk:0.3.0` — **ürünün** sürümü ([`pyproject.toml`](pyproject.toml)). Bu kartın öznesi olan model artefaktı hâlâ **`HakHukuk-4B-v0.1`**'dir; sürümleme **bölünmüştür** ([ADR-0065](docs/adr/0065-bolunmus-surumleme.md)) |

İki daemon da yalnız host'un `127.0.0.1`'ine yayımlar; kimlik doğrulama ve hız sınırı **yoktur**
(`S9` açılmadı).

**Bayraklar karardır, tercih değil.** §7.10 aynı soruda cevabın yalnız KV kuantizasyonu
değişince değiştiğini ölçtü; 2026-09-11'de fp16 KV'nin **kütlesi** de ölçüldü ve
`wrong_ref_rate` **0,0769 → 0,1553 (2,0×)** kötüleşti
([`KUTLE.md`](outputs/eval/g22-kv-fp16/KUTLE.md)). `compose.yaml` `q8_0` KV dahil bağlayıcı
bayrakları **zorlar**; `llama-server`'ı elle açan kişi onları **kendi** yazmak zorundadır.

#### ⚠️ Konteyner yayımlanan `0,8011`'i **ÜRETMEZ**

`0,8011` **ölçüm hattının** sayısıdır: harness AÇIK, `k=10`, önsözsüz, iki geçişli zorunlu
düşünce kapatması, `q8_0` KV önbelleği. Konteyner **ürün yolunu** taşır — §7.9'un anlattığı
hat. Ürün yolu 2026-09-11'de ölçüm hattının rejimine geldi
([ADR-0080](docs/adr/0080-urun-yolu-zorunlu-dusunce-kapatmasi.md)) ve tamamen boş cevap
**4/80 → 0/80** oldu. ~~ama **kütlesi ölçülmedi** (hakem ister, o turun bütçesi $0)~~
→ **ÖLÇÜLDÜ 2026-09-12.** `0,8011` yine de **ürün yolunun sayısı değildir**;
ürün yolunun kendi sayısı artık **var** ve aşağıdadır.
Kaynak: [`KARSILASTIRMA.md`](outputs/eval/g22-rejim/KARSILASTIRMA.md).

##### 📐 Ürün yolunun KENDİ sayısı — ilk kez ölçüldü (2026-09-12)

80 DEV sorusu **konteynerin HTTP API'sinden** koşuldu (vatandaşın fiilen kuracağı yol),
cevaplar ölçüm hattının hakemiyle (`gpt-4o-mini`, n=80) puanlandı.

| eksen | ölçüm hattı (`f02`) | **ürün yolu** (`g24`) | fark |
| :--- | ---: | ---: | ---: |
| **sadık cevap kütlesi** | 0,8011 | **0,7792** | **−2,19 p** |
| coverage | 0,9375 | **0,9375** | 0,00 p |
| A1 (cevaplanan) | 0,8545 | **0,8312** | −2,33 p |
| uydurulmuş madde | 0/114 | **0/142** | — |
| tamamen boş cevap | 0/80 | **0/80** | — |
| kesiklik | 4/80 (%5,0) | **4/80 (%5,0)** | — |

Fark **1,75 çözünürlük adımı** (`n=80` ⇒ adım = 1,25 p): ölçülebilir, ama **dar**.

> ⚠️ **Bu farkın sebebi AYRIŞTIRILAMIYOR ve bunu saklamıyoruz.** Bu koşuda hakem
> `judge_providers = ["Azure","OpenAI"]` ile servis edildi; çıpa (`f02`) ise
> `LLM_PROVIDER_ORDER=OpenAI` ile **pinlenmişti** — ve bu pin hiçbir yerde yazılı değildi.
> Kalem düzeyinde sağlayıcı dağılımı **ölçülemiyor** (`llm_client.note_provider()` sağlayıcıyı
> global bir kümede tutuyor, kalem kimliği taşımıyor). ⇒ *"−2,19 p'nin ne kadarı ürün
> yolundan, ne kadarı hakem taşıyıcısından"* sorusunun cevabı **yoktur**. Koşu para harcandığı
> için tekrarlanmadı; bundan sonraki koşularda sağlayıcı **pinlenir**.

Kaynak: `outputs/eval/g24-urun-yolu-kutle-6.3b/` (künye · ham hükümler · tablo) ·
üretim `outputs/eval/g23-konteyner-urun-yolu-80/`.

### Model, harness'ıyla birlikte gelir

**Yayımlanan sayı retriever + indeks + istem olmadan YENİDEN ÜRETİLEMEZ.** `%80,1` bir
*harness AÇIK* sayısıdır: bağlamı elle kurulmuş değil, **retriever** seçmiştir. Modeli
tek başına indirip aynı sayıyı beklemek **kategori hatasıdır**.

| bileşen | değer | kaynak |
| :--- | :--- | :--- |
| ağırlık | `HakHukuk-4B-…-Q4_K_M.gguf` · 2,59 GiB | [ADR-0071](docs/adr/0071-v1-release-artefakti-tek-gguf.md) |
| indeks | `data/index/mevzuat_bge_m3_s2` · **40.496 madde** · **80 MB** | [`KUNYE.json`](data/index/mevzuat_bge_m3_s2/KUNYE.json) |
| erişim | hibrit BM25 + `BAAI/bge-m3`, RRF · `RRF_K=10` · **k=10** | [ADR-0068](docs/adr/0068-rrf-k-60-to-10.md) |
| istem | **önsözsüz** | [ADR-0063](docs/adr/0063-yeterlilik-onsozu-kaldirildi.md) |
| bütçe | 1536 (`think 1024 + cevap 512`) | [ADR-0070](docs/adr/0070-uretim-butcesi-esitlendi.md) |

**Harness GPU'ya HİÇ girmez** — gömücü CPU'da, indeks CPU RAM/diskte. Dizüstüne sığmakla
sığmamak arasındaki fark budur. *(Vektör veritabanı ölçülüp **reddedildi**: kaba kuvvet
**8,2 ms/sorgu**, CPU, 50 sorgu ortalaması — **S2 ÖNCESİ** indekste ölçüldü, S2 indeksinde
yeniden ölçülmedi: [#49](docs/record/research_log/2026-08-04-s3a-on-prob.md))*

### Donanım — ÖLÇÜLDÜ, hesaplanmadı

`llama-server` · Q4_K_M · KV cache `q8_0` · tek slot ·
[`vram_stack_tgta_v1.json`](outputs/eval/_artefakt/vram_stack_tgta_v1.json) — **bu artefaktın
kendisinde** (`tgta_v1-q4_k_m.gguf`) ölçüldü:

| ctx | sunucu VRAM | tepe |
| ---: | ---: | ---: |
| 4.096 | **3,09 GiB** | 4.068 MiB |
| 32.768 | 3,70 GiB | 4.684 MiB |
| 131.072 | 5,76 GiB | 6.796 MiB |

⇒ `CLAUDE.md`'nin **≤8 GB yumuşak kapısı 128K bağlamda bile geçiliyor.**
Çıktı dosyasında **GPU modeli kayıtlı değil** — yalnız pstate, saat, güç ve sıcaklık var.

### Ne için — ve ne için DEĞİL

Modele **bir soru** ve **kaynak hukuk metni** verilir; model ya

1. cevaplar ve **dayandığı maddeyi belirtir**, ya da
2. *"verilen kaynaklar bunu kapsamıyor"* der.

**İkinci yarı işin zor kısmıdır ve bu projenin varlık sebebidir.** Her şeye cevap veren bir
model hukukta işe yaramazdan da kötüdür: kendinden emin **yanlış bir madde numarası**,
*"bilmiyorum"*dan daha tehlikelidir.

**Sade dil bir EĞİTİM HEDEFİ DEĞİL, doğru cevabın sunum katmanıdır.** Sade/kısa cevaba
doğru eğitmek denendi ve **isabeti düşürdü**; vatandaş-register turu base'i yakalarken çekinme
çöktü ([ADR-0010](docs/adr/gemma4-12b-dersler.md#adr-0010), yürürlükte). Eğitim hedefi
**doğruluk ve çekinme**; sadeleştirme **istem katmanında** yapılır.

---

## 9 · Lisans ve veri

| | |
| :--- | :--- |
| **Lisans** | **Apache-2.0** — ağırlık + kod + veri + araştırma kaydı, **tamamı açık** ([`LICENSE`](LICENSE) · [`NOTICE`](NOTICE)) |
| **Base lisansı** | `Qwen/Qwen3.5-4B` · Apache-2.0 |
| **Kapsam** | **yalnız güncel Türkiye Cumhuriyeti mevzuatı** |
| **Yer gerçeği** | Mevzuat.gov.tr |
| **İzinli kaynaklar** | Mevzuat.gov.tr · Resmî Gazete · Yargıtay açık portalı · açık Kaggle/HF setleri |
| **YASAK** | **Lexpera · Kazancı — ASLA.** Telif zehri. |
| **PII** | eğitim verisinde maskelenir |

**Veri sertliği, pahalı öğrenilmiş:** her veri seti kullanılmadan önce **EDA ile doğrulanır**.
`newmindai/EuroHPC-Legal` kâğıt üstünde mükemmeldi (43K kalem, Apache-2.0) ama örnekleme
**uyuşmayan soru-cevaplar, uydurma kanunlar ve Osmanlı dönemi içerik** gösterdi ⇒ **reddedildi**.
Eksik veri (sade dil, vatandaş nişi, senaryo→kanun) **temellendirilmiş sentetik üretimle**
karşılanır: gerçek madde metni → LLM çift üretir → **doğrulanır**
([`VERI_PLANI.md`](docs/VERI_PLANI.md)).

---

## 10 · Yeniden üretilebilirlik

> **Tek komut (2026-09-07):** `bash scripts/yeniden_uret.sh` — ön koşul denetimi → üretim →
> **iki geçerlilik kapısı** (kesiklik %5 · `recall@10` 0,9500) → puanlama → manşet tablo →
> çıpadan sapma kontrolü. Belgesi: [`docs/YENIDEN_URETIM.md`](docs/YENIDEN_URETIM.md).
> Bu tarihe kadar manşet **%80,1'i modeli indiren hiç kimse yeniden üretemiyordu**: istem
> `gen_eval_grounded.py`'nin içindeydi (çözüldü, `hakhukuk/istem.py`), komut zinciri hiçbir
> yerde tek parça yazılı değildi (çözüldü), indeks **git'te yok** (**hâlâ açık**).

Her şey bu repoda: kronolojik araştırma kaydı (**negatif sonuçlar ve geçersiz koşular dâhil**),
**ADR defteri `0001`-`0074`** (`0059` rezerve, henüz yazılmadı; `0001`-`0026` tek dosyada:
[`gemma4-12b-dersler.md`](docs/adr/gemma4-12b-dersler.md)), seed ve hash taşıyan koşu künyeleri, ve değerlendirme koşucusu.

```
docs/record/research_log/   ne oldu, hangi sayıyla        (kronolojik, bağlayıcı)
docs/adr/                   niye böyle, hangi alternatif elendi
docs/record/kollar.md       artefakt sicili — her kol ve her merge
docs/record/yurutme-tuzaklari.md   "hata vermeden yanlış sayı üretir" listesi (17 tuzak)
outputs/eval/               ham değerlendirme çıktıları
```

**Merge yeniden üretimi** ([`kollar.md`](docs/record/kollar.md)):

```bash
python scripts/merge_ties.py --base Qwen/Qwen3.5-4B \
       --adapter tg=outputs/tg_v1 --adapter ta=outputs/ta_v1 \
       --no-norm-balance --out models/merged/tgta_v1     # ham TIES, ADR-0052
```

`models/merged/` ve `models/gguf/` **yeniden üretilebilir**; asıl artefakt **adaptördür**
(`outputs/<kol>/`). Adaptörler git'te **değil** (114 MB > GitHub'ın 100 MB sınırı) ve
**yedeklenmiyor** — bilinçli karar: veri + reçete + seed sabitken yeniden üretilebilirler.

**Rejim değişmezleri — uyuşmazlık HATA VERMEZ, kıyası GEÇERSİZ kılar:**
`seed 3407` · `max-chunk-chars 900` · `thinking on` · toplam bütçe **1536** · `n 80` ·
veri `data/eval/dev/core_hard.jsonl` **v2** · indeks `mevzuat_bge_m3_s2` · `harness-k 10` ·
`RRF_K 10` · **önsözsüz**. **Donmuş TEST'e (`data/eval/canon/`) dokunulmaz.**

---

## 11 · İleriye not: benchmark'larımızı geliştirmeli miyiz?

> **Bu bölüm bir SORU bölümüdür, cevap değil.** Hiçbiri burada karara bağlanmıyor; hepsi
> **ölçülmüş** ya da **açıkça türetilmiş** açık kalemlerdir. Karar mercii insandır.

**1 · Set küçük ve dar: `n=80`, tek dil, tek alan.**
Güven aralıkları buna göre geniştir. Bugünkü iki oranın **Wilson %95** aralığı
*(burada hesaplandı: `z=1,96`, `n=80`; dosyadan okunmadı)*:

| oran | nokta tahmin | Wilson %95 | genişlik |
| :--- | ---: | :--- | ---: |
| **isabetsizlik 8/80** | 0,1000 | **[0,0515 – 0,1851]** ≈ **[4/80 – 15/80]** | **13,4 puan** |
| aşırı-red 4/80 | 0,0500 | [0,0196 – 0,1216] ≈ [2/80 – 10/80] | 10,2 puan |

⇒ *"8/80 ↔ 6/80"* gibi farklar bu genişliğin **çok altındadır**. **Soru:** kaç kalem, hangi
çeşitlilikte yeterlidir? İkili oranların çözünürlük sınırı zaten **açık karar S5**'tir
(soruyu taşıyan plan 2026-09-12'de kapandı ve silindi; ilgili kusur **5a** açık kalır —
[ADR-0083](docs/adr/0083-kusur-sicili-adrye-tasindi.md) · [ADR-0079](docs/adr/0079-zayif-eslesme-rozeti-eklenmedi.md));
aynı sınıfta ölçülmüş ikinci bir
örnek: M2'nin kuantumu `1/66 = 1,52 puan`, yani `+0,000` ile `±1 kalem` **ayırt edilemiyor**
([#59](docs/record/research_log/2026-08-06-m2-paydasi-ve-karar-4.md) · [`kollar.md`](docs/record/kollar.md)).

**2 · DEV ile TEST aynı sınav değil.**

| set | `recall@10` | ⇒ kütle tavanı |
| :--- | ---: | ---: |
| DEV (80) | 0,9500 | **≈%95** |
| TEST `core_hard` (40) | 0,7500 | **≈%75** |

Fark setin zorluğundan değil **bileşiminden**: ayrım kanuna göre kusursuz katmanlı (2:1) ama
**madde uzunluğuna göre katmanlanmamış**; bileşim farkın **%81**'ini açıklıyor
([ADR-0069](docs/adr/0069-kabul-testi-tavan-kullanimi-raporlamasi.md) ·
[ANALIZ](outputs/eval/f01c-dev-test-farki/ANALIZ.md)). **Soru:** ayrım **uzunluğa göre de**
katmanlanmalı mı — ve bu, donmuş TEST'i açmadan nasıl yapılır?
(Yeniden katmanlama [ADR-0069](docs/adr/0069-kabul-testi-tavan-kullanimi-raporlamasi.md)'da
*"donmuş TEST'i açar, usulü kırar"* diye **reddedilmişti** — soru bu redde rağmen açıktır.)

**3 · Her sayı tek hakem ailesinin hükmü.**
`openai/gpt-4o-mini`, `runs=1`, **κ yok**, öz-tercih **genel olarak** ölçülmedi — yalnız
Anthropic ailesi için ölçüldü, ters yönde (§7.2). Üç aileli panel
([ADR-0032](docs/adr/0032-hakem-paneli-uc-aile-ve-aile-dislama.md)) **hiç kurulmadı**.
`HP` turu bunu kapatmak için planlandı ve **rakip havuzunun genişlemesinin ön koşuludur**
([ADR-0072](docs/adr/0072-v1-rakip-havuzu-genisler.md)). **Soru:** κ hangi eşiğin altında
kalırsa bu kartın sayıları **yeniden koşulur**?

**4 · Manşet metriğin kendisi bir çarpım: `kütle = coverage × A1`.**
İki çarpan **farklı örnekleme birimlerinden** gelir — `coverage` **kalem** başına (80 kalem),
`A1` **iddia** başına ve **yalnız cevaplanan** kalemler üzerinden makro. ⇒ Çarpıma **ikili bir
güven aralığı doğrudan uygulanamaz**. Aynı sebep `v1.0` kapısının δ'sının **ölçümden değil insan
kararından** gelmesinin gerekçesidir: hakem gürültü tabanı (**0,3 puan**) yalnız `A1` için
ölçüldü, **`coverage`'ın varyansı o tabanda yok**
([ADR-0064](docs/adr/0064-v1-kapisi-uc-maddeli-on-kayit.md) §δ). **Soru:** kütle için savunulabilir
bir belirsizlik ifadesi (bootstrap? kalem-başına birleşik skor?) kurulmalı mı?

**5 · Dış karşılaştırılabilirlik YOK.**
Sayılarımız kendi CANON setimizde üretiliyor (§3.1) ve **kimse bu sette koşamaz** — ne set
tamamen yayımlandı ne de üçüncü taraf bir çıpa var. Dış benchmark'lara gitmemek
[ADR-0016](docs/adr/gemma4-12b-dersler.md#adr-0016)'nın **kayıtlı kararıdır** ve gerekçesi
sağlamdır (yanlış sınav yorumlanamaz), ama bedeli de gerçektir: **doğrulanabilirlik**.
**Seçeneklerden biri** — karar değil, seçenek — CANON'un **kamuya açık bir alt kümesini
yayımlamak**. Bunun bedeli de ölçülü: donmuş TEST bir **kabul testidir** ve yayımlanması
onu yakar; DEV ise **seçim yapılmış** settir. Hangi alt kümenin, hangi lisansla, hangi anda
yayımlanacağı **açık**.

**6 · Bir ALTIN ETİKET şüphesi kayda geçti — id 46.**
İki **bağımsız** gözle okuma, **birbirinden habersiz**, aynı kalemi işaretledi: KMK **14** lafzen
*"Kat mülkiyetine geçişte ayrıca yönetim plânı istenmez"* diyor ⇒ soruyu, altın etiketlenen
KMK **53**'ten (1965 öncesi geçiş hükmü) **daha iyi karşılıyor**
([`GOZLE_ISABETSIZLIK_3_1_FL.md`](outputs/eval/f04-rakip-onsozsuz/GOZLE_ISABETSIZLIK_3_1_FL.md) §3 ·
[`GOZLE_ISABETSIZLIK_3_5_FL.md`](outputs/eval/f04-rakip-onsozsuz/GOZLE_ISABETSIZLIK_3_5_FL.md) ·
[`GOZLE_ISABETSIZLIK_3_5_FLASH.md`](outputs/eval/f04-rakip-onsozsuz/GOZLE_ISABETSIZLIK_3_5_FLASH.md) §5).
Üç kolda da **sınır durum** sayıldı ve **hiçbirinde sayıya katılmadı** ⇒ **üç isabetsizlik
sayısı da ALT SINIRDIR.** Etiket **bugün değiştirilmedi**: sonucu gördükten sonra yer-gerçeğini
oynatmak, [ADR-0067](docs/adr/0067-soru-onarimi-dev-test-v2.md)'nin yanlılık korumasının doğrudan
ihlalidir. **Soru:** yer-gerçeği denetimi ayrı, **kör** ve **koşudan önce** yapılan bir adım
olmalı mı?

**7 · Ölçüm aleti hâlâ onarım altında.**
Faz 0'da **beş alet kusuru** bulundu ve hiçbiri sayısal kapıya takılmadı (§7.1); dedektör **üç
kez** yanıldı (§7.1) ve `exact_reject`'in **kör mod dalı bugün de açık borç**. **Soru:** *"gözle
okuma"* kalıcı bir kapı mı, yoksa aletin olgunlaşmasıyla azalması beklenen bir maliyet mi?

---

## 12 · Atıf

```bibtex
@software{hakhukuk2026,
  title   = {HakHukuk: göreve-vektörü birleştirilmiş bir Türkçe hukuk asistanı},
  year    = {2026},
  url     = {https://github.com/Rfetha/Hukuk-SLM},
  license = {Apache-2.0}
}
```
