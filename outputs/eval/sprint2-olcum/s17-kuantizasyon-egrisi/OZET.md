# ADIM 6.3c — S17 kapanışı: kuantizasyon eğrisi

> Şartname: plan `2026-09-12-v1-son-is.md` §3 ADIM 6/6.3c. Kapatılan açık karar: **S17**
> (`MODEL_CARD.md:628`, ADR-0031 hassasiyeti seçti-ama-ölçmedi boşluğu).

## Ön koşullar — doğrulandı

```
bf16 merge   models/merged/tgta_v1/                         8,8 GB
f16 GGUF     models/gguf/tgta_v1-f16.gguf                    8.665.620.128 bayt
             sha256 d9a8a28e6bc1ff5f4c4da2d0739dc65b4ab6221d68d5afb86798403a889fb369
             441/441 tensör, exit 0
```

## Dört kol — GGUF künyeleri (boyut + `sha256`, çıkış kodu)

| kol | dosya | bayt | `sha256` | exit |
| :--- | :--- | ---: | :--- | :--- |
| `Q4_K_M` @2026-08-03 (**yayımlanan**) | `models/gguf/tgta_v1-q4_k_m.gguf` | 2.783.446.720 | `755e15e92e9f7021934f2d5eada6c1f02fcc92be23f0536b0c2a0a9586e7bffc` | — (önceden üretilmiş) |
| `Q4_K_M` @2026-09-12 (bugünkü zincir) | `models/gguf/tgta_v1-q4_k_m-20260912.gguf` | 2.783.446.688 | `9becf3620b49a88805f88b6bd2bea1b2c18611df79ac92ab72b3f092adb482d6` | 0 (441/441) |
| `Q5_K_M` @2026-09-12 | `models/gguf/tgta_v1-q5_k_m.gguf` | 3.161.425.568 | `2afa0ea321b404c654faa56d698965fc664e229d539bb3ee555d0a04a0f6b8b0` | 0 (441/441) |
| `Q8_0` @2026-09-12 | `models/gguf/tgta_v1-q8_0.gguf` | 4.610.580.128 | `a7991f365269e50b79264363a96c2c868a34cce638136e3a2fc22fac58a1354b` | 0 (441/441) |

`Q4`@ağustos ↔ `Q4`@bugün: **−32 bayt**, `sha256` **farklı**. → **BULGU-G** (aşağıda).

## Rejim — çıpayla (`f02-biz-onsozsuz`) birebir

```
seed 3407 · max_chunk_chars 900 · thinking on · think_budget 1024 · max_new_tokens 512
ctx 8192 · ngl 99 · flash_attn on · KV q8_0/q8_0 (tüm kollarda — kuantizasyon TEK değişken, ADR-0017)
harness data/index/mevzuat_bge_m3_s2 · k=10 · n=80 · mod h1
taşıyıcı: llama.cpp llama-server, YEREL, port 8090 (8080 çakışıyordu — bkz. BULGU-E)
üretici: scripts/yeniden_uret.sh (GGUF/ETIKET/OUT_DIR/OPENAI_BUDGET_USD override edildi)
```

Her sunucu ayağa kalktığında `/v1/models` ile **hangi GGUF'un servis edildiği doğrulandı**
(ftype + tam yol) — 8080'deki karıştırıcının ardından zorunlu hâle gelen kontrol.

## Geçerlilik kapıları — dört kol, ayrı ayrı

| kol | n | kesiklik | eşik | recall@10 | beklenen | sonuç |
| :--- | ---: | :--- | :--- | :--- | :--- | :--- |
| `Q4_K_M` @ağustos (çıpa) | 80 | 4/80 = %5,0 (tam eşikte) | %5 | 0,9500 | 0,9500 | ✅ (önceden geçmiş, yeniden koşulmadı) |
| `Q4_K_M` @bugün | 80 | 4/80 = %5,0 | %5 | 0,9500 | 0,9500 | ✅ |
| `Q5_K_M` | 80 | 2/80 = %2,5 | %5 | 0,9500 | 0,9500 | ✅ |
| `Q8_0` | 80 | 1/80 = %1,2 | %5 | 0,9500 | 0,9500 | ✅ |

`recall@10` üçünde de **birebir 76/80** — indeks/harness oynamadı, tek değişken kuantizasyon.
Hesap `scripts/olcum_uretim/recall_kapisi.py::recall_at_10` ile (kusur 33 düzeltmesi) bağımsız
olarak da doğrulandı.

## Puanlama — hakem yığını çıpayla aynı, sağlayıcı pinli

`gpt-4o-mini` · `LLM_GATEWAY=openrouter` · `LLM_PROVIDER_ORDER=OpenAI` (üç puanlamanın **hepsinde**
export edildi) · `OPENAI_BUDGET_USD=0.20` süreç kilidi.

| kol | `judge_providers` | fatura (USD) |
| :--- | :--- | ---: |
| `Q4_K_M` @bugün | `["OpenAI"]` | 0,0414 |
| `Q5_K_M` | `["OpenAI"]` | 0,0402 |
| `Q8_0` | `["OpenAI"]` | 0,0394 |
| **toplam** | | **0,1210** |

Tahmin $0,0834 idi (iki kol için); dördüncü kolun eklenmesiyle güncellenen tahmin ~$0,12 —
gerçekleşen **$0,1210**, alt-tavan **$0,20**'nin altında. Para kapısı **GEÇTİ**, durulmadı.
`Q4_K_M`@ağustos **yeniden puanlanmadı** — çıpanın kendi sayısı (`f02-biz-onsozsuz/KUNYE.json`)
olduğu gibi alındı (kural: 6.3c şartnamesi, ⭐ ders bölümü).

## Eğri — dört satır

| kol | dosya boyutu | kütle | coverage | A1 | kesiklik | ort. completion tok | zorla kapatma | VRAM (ctx 8192, KV q8_0) |
| :--- | ---: | ---: | ---: | ---: | :--- | ---: | :--- | ---: |
| `Q4_K_M` @ağustos (**yayımlanan çıpa**) | 2.783.446.720 | 0,8011 | 0,9375 | 0,8545 | %5,0 | 782,5 | 3/80 | 3,18 GiB |
| `Q4_K_M` @bugün | 2.783.446.688 | 0,7921 | 0,9375 | 0,8449 | %5,0 | 782,4 | 3/80 | 3,18 GiB *(aynı GGUF sınıfı, ayrıca ölçülmedi)* |
| `Q5_K_M` @bugün | 3.161.425.568 | 0,8673 | 0,9750 | 0,8895 | %2,5 | 876,6 | 8/80 | 3,55 GiB |
| `Q8_0` @bugün | 4.610.580.128 | 0,7909 | 0,9250 | 0,8550 | %1,2 | 967,5 | 17/80 | 4,92 GiB |

VRAM kaynağı: `scripts/olcum_uretim/measure_vram_stack.py --ggufs tgta_v1-q4_k_m.gguf
tgta_v1-q5_k_m.gguf tgta_v1-q8_0.gguf --ctxs 8192 --kv-type q8_0` →
`outputs/eval/s17-kuantizasyon-egrisi/vram_stack.json`. `Q4`@bugün için ayrı ölçülmedi (aynı
kuantizasyon sınıfı, `Q4`@ağustos'un ölçümü kullanıldı) — **uydurulmadı, açıkça not edildi**.
Güç durumu: ŞARJDA; GPU P-state ölçüm sırasında düşük saat hızında kilitliydi (180 MHz SM) —
mutlak VRAM sayısı etkilenmez, hız etkilenir (bu turda hız ölçülmedi).

## Okuma — çözünürlük kuralı uygulanmış (n=80 ⇒ 1 adım = 1/80 = 1,25 p)

| karşılaştırma | fark | adım | hüküm |
| :--- | ---: | ---: | :--- |
| `Q4`@ağustos ↔ `Q4`@bugün (**araç zinciri**, aynı kuantizasyon) | −0,90 p | 0,7 | **BELİRSİZ** — çözünürlük altında |
| `Q4` ↔ `Q8` @bugün | −0,12 p | 0,1 | **BELİRSİZ** — çözünürlük altında |
| `Q4` ↔ `Q5` @bugün | +7,52 p | 6,0 | **ölçülebilir** |
| `Q5` ↔ `Q8` @bugün | −7,64 p | 6,1 | **ölçülebilir** |

**İki cümle, hükümsüz:**

1. **Araç zinciri sapması ölçülemez düzeyde.** `Q4_K_M`'nin 32 baytlık dosya farkı (bugünkü
   `llama.cpp` sürümüyle üretilen f16→Q4_K_M yolu) davranışa çözünürlük üstünde yansımıyor
   (−0,90 p < 1 adım). Ayrıca **üretim tarafı** neredeyse örtüşüyor: ort. completion token
   782,5 (çıpa) ↔ 782,4 (bugün), zorla-kapatma 3/80 ↔ 3/80 — fark tamamen hakem puanlamasının
   normal gürültü bandında (0,30 p noktası, bkz. yurutme-tuzaklari.md §2.8). Karıştırıcı
   **ölçülerek** etkisiz bulundu, varsayılarak değil.
2. **Eğri monoton değil.** `Q4 ≈ Q8` (fark çözünürlük altında), `Q5` ikisinin de belirgin
   üstünde (+6-6,1 adım). Mekanizma coverage ekseninde görünüyor: cevaplanan kalem sayısı
   `Q4` 75/80 → `Q5` 78/80 → `Q8` 74/80; A1 üçünde de 0,845-0,890 dar bandında. Yani bu ölçümde
   kuantizasyon seviyesi cevabın **doğruluğunu** değil, modelin **çekinme eşiğini**
   (coverage) oynatıyor gibi görünüyor.

   ⚠️ **Bu ikinci cümle bir gözlemdir, açıklama DEĞİL.** Tek koşu, n=80, üç kalemlik coverage
   farkı — mekanizma hipotezi **ölçülmedi**. *"Q5 daha iyi"*, *"Q8'de bir şey bozuluyor"* gibi
   hükümler bilerek kurulmadı; bu **açık bir soru** olarak bırakılıyor.

## BULGU-E — port çakışması, sessiz-yanlış-sunucu (bu turda YAKALANDI)

`yeniden_uret.sh`'ın önkoşul denetimi `command -v llama-server` — PATH'te yoktu, ilk koşu
saniyede patladı (gürültülü, zararsız). PATH düzeltilip yeniden koşulunca `llama-server`
port 8080'e bağlanamadı (`couldn't bind HTTP server socket`) ama script'in `curl .../health`
döngüsü **başka bir süreçten** (6.3'ün konteyner çifti, `hakhukuk-app-1`/`hakhukuk-llama-1`,
iş bitmiş ama 2 saattir ayakta, 8080'i ve ~6 GB belleği tutuyordu) **200 OK** aldı ve
"✅ llama-server hazır" yazıp devam etti — 8 kalem **yanlış model** (`HakHukuk-4B-v0.3-Q4_K_M`,
yayımlanan ürün) karşısında üretildi, hiçbir yerde hata vermeden. Yakalanma yolu: `ps -p <pid>`
ile başlatılan sürecin **hâlâ yaşayıp yaşamadığı** kontrol edildi (yaşamıyordu) ve
`/v1/models` **beklenmeyen** bir yol gösterdi. Kirlenen 8 kalemlik çıktı **silinip** temiz
port (8090) ile yeniden koşuldu; sonraki üç sunucu başlatmasının **hepsinde** `/v1/models`
ile hedef GGUF doğrulandı. Konteyner çifti koordinatör tarafından durduruldu
(`docker stop hakhukuk-app-1 hakhukuk-llama-1`), 8080 boşaldı. Bu bulgu
`docs/record/yurutme-tuzaklari.md` §7.8'e işlendi (bu turda, kusur 33'ten ayrı).

## Kusur 33'ün bu turdaki canlı etkisi

`Q5_K_M` koşusunun ilk denemesinde `yeniden_uret.sh`'ın (o anki) recall@10 kapısı var olmayan
alanları (`gold_retrieved`/`altin_getirildi`) okuyup **her zaman** 0 sayıyordu; koşu
"`recall@10 0.0000 ≠ 0,9500 ⇒ harness OYNAMIŞ"` diyerek üretimi (geçerli, n=80, kesiklik %2,5
olan) atmaya kalktı. Kusur eş-zamanlı olarak `cc12b6e` ile kapatıldı
(`scripts/olcum_uretim/recall_kapisi.py`, `harness.altin_sirasi`/`altin_dusuruldu`'dan okuyor,
6/6 test yeşil). Bu adım kusuru **canlı** yakaladı; kalibrasyon kanıtı hem `f02` çıpasında
(gerçek 76/80) hem bu turun `Q5` kolunda (düzeltilmiş kapı: 0,9500) doğrulandı — üç kolun
(`Q4`@bugün, `Q5`, `Q8`) hepsinde gate script'i artık düzeltilmiş haldeydi ve doğru sonuç verdi.

## Kapsam dışına uyulan

Yayımlanan GGUF/HF deposu, indeks, korpus, `retriever.py`, `indir.py`, Modal, donmuş TEST,
rakip kollar, `yeniden_uret.sh`'ın kesiklik kapısı — hiçbiri değiştirilmedi/dokunulmadı.
`models/gguf/*.gguf` git'e girmez (`.gitignore`); bu klasördeki JSON/MD çıktılar git'e girer.

## Kalan şüpheler

- Coverage ekseninin kuantizasyona göre **monoton olmayışının mekanizması** ölçülmedi —
  açık soru, sonraki tura devredilebilir (tek koşu, n=80, düşük kalem sayısı farkı).
- `Q4`@bugün için VRAM **ayrıca ölçülmedi** (aynı kuantizasyon sınıfı varsayımıyla `Q4`@ağustos
  ölçümü kullanıldı) — dosya boyutu 32 bayt farklı olduğundan teorik olarak aynı, ama
  doğrudan ölçülmedi.
- GPU P-state ölçüm sırasında düşük saatte kilitliydi; hız (t/s) bu turda **hiç ölçülmedi**,
  yalnız VRAM.
- Hakem κ kalibresiz (Aşama C, `note_validity` her `gnd_*_summary.json`'da tekrarlanıyor) —
  eğri **model-vs-model sıralama**, mutlak değer değil.
