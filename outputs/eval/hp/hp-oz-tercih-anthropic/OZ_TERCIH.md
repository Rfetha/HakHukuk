# ADIM 6.6b — Öz-tercih ölçüldü, **yalnız Anthropic ailesi için** — BULGU

> Plan: `docs/superpowers/plans/2026-09-12-v1-son-is.md` §3 ADIM 6 / 6.6b.
> ⛔ **Bu dosya hiçbir hükme girmez, `harness_tablo` rakip tablosuna yazılmaz, Sonnet-5'in
> yayımlanan kütlesi (`0,8348`) oynamaz** (ADR-0032 aile dışlaması, notlamada yürürlükte).

## 1. Niçin

Üç yerde yazılı *"Öz-tercih ÖLÇÜLMEDİ ⇒ 'hakem kendi ailesini kayırmıyor' cümlesi kurulmaz"*
(ADR-0064 m.2 · ADR-0074 (c) · `KAPPA.md` §2/§6.4) — panelde yalnız Google özneler vardı ve
Google hakem kurulamıyor (aile dışlaması). 2026-09-09'da `claude-sonnet-5` rakip havuzuna
**özne** olarak girdi ve aynı model panelde **hakem** ⇒ aynı-aile hücresi elimize geçti.

## 2. Girdi, hakem, üretim yeniden koşulmadı

| alan | değer |
| :--- | :--- |
| puanlanan kol | `outputs/eval/hp-rakip-havuzu/h1_sonnet_5_nb_detail.jsonl` (n=80) — **üretim yeniden koşulmadı** (ADR-0017) |
| girdi `sha256` | `4f4f8fc9404709a5a02150bb697ef1b395060650dcf912720cf9ac71ccd9bd4c` |
| özne | `claude-sonnet-5` (aynı model, rakip havuzunda özne) |
| hakem | `anthropic/claude-sonnet-5` (OpenRouter) — **aynı özneyle AYNI aile** |
| sağlayıcı pin | `LLM_PROVIDER_ORDER=Anthropic` → koşu sonrası `judge_providers=["Anthropic"]` (tek eleman, tuzak 2.7 tetiklenmedi) |
| mod | `--mode data` (tek-madde yer-gerçeği, `hp-rakip-havuzu`'nun orijinal `gpt-4o-mini` koşusuyla birebir aynı rejim) |
| runs | 1 |
| bütçe kilidi | `OPENAI_BUDGET_USD=3.00` (süreç düzeyinde, brief'in alt-tavanı; aşılırsa betik kendiliğinden durur) |
| hakem çağrısı | **BİR KEZ** — tek `groundedness.py` çağrısı, 80 kalemin tamamı |
| tarih | 2026-09-12, 21:25–21:52 (+03), ~27 dk |
| çıktı | `gnd_h1_sonnet_5_oz_tercih.jsonl` (`sha256 6dbb27bd3e0c95f3a6b8fe8c54057a9691239371bbf83fffbbf25677a759ad67`) + `_summary.json` |

## 3. Bakiye — koşudan ÖNCE ve SONRA okundu

```
öncesi   GET /api/v1/credits → total_usage = 20,17249198
sonrası  GET /api/v1/credits → total_usage = 22,79369598
gerçek fatura (bakiye farkı)      = $2,6212
```

⚠️ **İkinci sayı, ve ikisi aynı şey değil** (6.5'in dersi, `llm_client.py`'nin kendi uyarısı):
betiğin iç muhasebesi (`judge_cost_usd`, liste fiyatı) = **$2,6963**. Fark: **$0,0751 (~%2,9)**,
iç muhasebe gerçek faturadan yüksek — aynı yönde, 6.5'teki %4,1'den biraz daha küçük bir sapma.
**Gerçek fatura = $2,6212** (bakiye farkı, ödenen tutar) kullanılır.

Alt-tavan **$3,00** — **aşılmadı** ($2,6212 tavanın **%87,4**'ü, $0,3788 marj boşta). **DUR ①
ateşlenmedi.**

## 4. Tahmin niçin şaştı — tuzak 1.11'in ÜÇÜNCÜ yüzü

```
brief tahmini (bizim kolun aynı hakem faturasından miras)   $1,86
token-oranıyla düzeltilmiş tahmin (706,6/782,5 tamamlama)   ≈ $1,68   (YANLIŞ YÖNDE düzeltti)
gerçek fatura                                                $2,6212
```

Koşu öncesi `completion_tokens` toplamı karşılaştırıldı (brief'in istediği ön-adım): Sonnet-5
öznesinin cevapları (706,6 tok/cevap) bizim kolumuzdan (782,5 tok/cevap) **daha KISA** —
oran 0,903. Bu, tahmini **aşağı** düzeltti (~$1,68), ama gerçek fatura bunun da **%56 üstünde**
çıktı.

**Sebep ölçüldü, tamamlama uzunluğunda değil:** hakem maliyeti **üretilen iddia sayısıyla**
ölçekleniyor (extract+verify iki aşamalı), tamamlama token sayısıyla değil. Sonnet-5'in
cevapları bizimkinden **daha az** tamamlama token'ı taşıyor ama **çok daha fazla iddia**
üretiyor: `total_claims` **665** ↔ bizim kolumuzda **~273** (`hp-rakip-havuzu/OZET.md`, "üretilen
iddia" satırı). ⇒ **Bir öznenin cevap uzunluğundan başka bir öznenin hakem faturasını türetmek,
doğrusal ekstrapolasyon kadar yanıltıcıdır** — tahmin öznenin **kendi** `total_claims`/iddia
yoğunluğu profilinden türetilmeli, bir önceki öznenin faturasından değil. Bu turda ölçülen
bedel ($2,6212), alt-tavanın ($3,00) altında kaldığı için **DUR tetiklenmedi**, ama marj
(%12,6) 6.4/6.5'teki kadar geniş değildi.

## 5. Üç okuma — Sonnet-5 hakem altında (`scripts/puanlama/uc_okuma_kutle.py`)

Küme üyeliği **miras alındı** (`GOZLE_KALIBRASYON_sonnet_5.json`, id 17·35·41 açık yanlış
pozitif → GÖZ-orta'ya eklenir; id 59 çekinceli cevap → GÖZ-katı'ya eklenir) — bu üyelik
**cevap metnine** dayanır, hangi hakemin puanladığına değil, bu yüzden aynen taşınır. Puanlar
1,0 varsayılmadı, Sonnet-5-hakem'in kendi `gnd` dosyasından okundu.

| okuma | n_cevaplanan | Σ faithfulness | kütle (Sonnet-5 hakem) | kütle (gpt-4o-mini hakem, `hp-rakip-havuzu`) |
| :--- | ---: | ---: | ---: | ---: |
| ALET | 72 | 47,962 | **0,5995** | 0,7911 |
| GÖZ-orta (+17,35,41) | 75 | 49,962 | **0,6245** | 0,8223 |
| **GÖZ-katı (+59)** | 76 | 50,762 | **0,6345** | **0,8348** |

`harness_tablo.py`'nin `kutle_tum` alanı (`0,5995`) ALET okumasıyla **birebir örtüşüyor** —
çapraz doğrulama tutar. Kaynak: `outputs/eval/hp-oz-tercih-anthropic/uc_okuma_oz_tercih.json` ·
`harness_tablo_oz_tercih.json`.

**GÖZ-katı, `hp-rakip-havuzu/OZET.md`'nin BAĞLAYICI TABLOSUNDA kalın yazılan (yayımlanan)
okumadır** — bu yüzden Δ hesabında GÖZ-katı kullanıldı; ALET okuması çapraz kontrol olarak
aşağıda ayrıca verildi.

## 6. Sapma — Δ_sonnet ↔ Δ_biz

⚠️ **Sign-convention notu (bu bulgunun en kolay yanlış okunacak yeri):** brief'in adım-3
formülü `Δ_sonnet = kütle(gpt-4o-mini) − kütle(sonnet-5 hakem)` (pozitif = Anthropic hakeme
geçince DÜŞÜŞ) yönünü kullanıyor. `KAPPA.md` §5'in kendi tablosu ise ters sırayla
(`sonnet-5 − gpt-4o-mini`) yazıp `Δ_biz = −10,71 p` diyor. **Büyüklük ikisinde de 10,71
puandır** — yön göstergesi farklı yazılmış. Karışıklığı önlemek için **tek ve tutarlı bir
yön** kullanıldı: `Δ = kütle(gpt-4o-mini) − kütle(sonnet-5 hakem)`, pozitif = *"Anthropic
hakeme geçince kütle bu kadar DÜŞTÜ"*.

```
Δ_biz    (BİZ kolu, çapraz-aile)      = 0,8011 − 0,6940 = +0,1071  →  +10,71 p düşüş
Δ_sonnet (Sonnet-5 kolu, AYNI aile,
          GÖZ-katı, bağlayıcı okuma)  = 0,8348 − 0,6345 = +0,2003  →  +20,03 p düşüş
Δ_sonnet (ALET, çapraz kontrol)       = 0,7911 − 0,5995 = +0,1916  →  +19,16 p düşüş
```

**Fark:** `|Δ_sonnet − Δ_biz|` (GÖZ-katı) = **9,32 p** · (ALET) = **8,45 p**.

## 7. Çözünürlük okuması

Çözünürlük adımı `n=80` için **1,25 p** (ön-kayıtlı). `9,32 p` ve `8,45 p`, her iki okumada
da eşiğin **çok üstünde** ⇒ **hüküm BELİRSİZ DEĞİL**, okunabilir bir sinyal var.

**Yön:** `Δ_sonnet > Δ_biz` (her iki okumada da) ⇒ ön-kayıtlı okuma kuralının üçüncü dalı:

> *"Δ_sonnet Δ_biz'den BÜYÜKSE → ters yönde; kayırma değil, ek katılık"*

## 8. HÜKÜM (bu hücre için, ölçekli)

**Öz-tercih LEHİNE kanıt YOK — tersine, TERS YÖNDE bir sinyal ölçüldü.** Anthropic hakem,
`gpt-4o-mini`'ye kıyasla **kendi ailesinin** cevaplarını (Sonnet-5), **başka bir ailenin**
cevaplarına (bizim Qwen-tabanlı kolumuz) göre **daha büyük bir düşüşle** cezalandırdı
(20,03 p ↔ 10,71 p, GÖZ-katı okumada). Bu, *"hakem kendi ailesini kayırıyor"* hipotezinin
**tam tersidir**: bu tek hücrede **ek katılık** ölçüldü, kayırma değil.

⚠️ **Bu bir HÜKÜM DEĞİL, bir GÖSTERGEDİR** (brief §"Güncel bütçe ve dersler" + ön-kayıt m.3):
tek özne, tek hakem, tek koşu, `n=80`. *"Anthropic hakemler öz-tercih yapmıyor"* ya da
*"Anthropic hakemler kendi ailesine karşı daha katı"* gibi genel bir cümle bu koşudan
**kurulmaz** — en fazla *"bu hücrede şu yönde ve şu büyüklükte bir sapma ölçüldü"* denir.

## 9. Kapsam şerhi — ZORUNLU

> *"Öz-tercih **yalnız Anthropic ailesi için** ölçüldü. `gpt-4o-mini` ve Google ailelerinin
> öz-tercihi **ölçülmedi** ve Google için **ölçülemez** (ADR-0032 aile dışlaması, hiçbir
> bütçeyle aşılamaz). Bu sayı, panelin öz-tercihe **bağışık olduğu** anlamına gelmez."*

`gpt-4o-mini` kendi ailesini yalnız `gpt-4o-mini`-tabanlı bir özneyle sınayabilirdi — böyle bir
özne panelde **yok**. Google özne × Google hakem hücresi **hiçbir bütçeyle** kurulamaz.
⇒ *"Öz-tercih ölçüldü"* cümlesi **genel olarak kurulmaz**, yalnız bu tek hücre için kurulur.

## 10. Tekrar-üretilebilirlik — kusur 23'ün sınıfı

Hakem çağrısı **bir kez**; hem `uc_okuma_kutle.py` hem `harness_tablo.py` aynı ham `gnd`
çıktısından **iki kez** kuruldu, iki çıktı da `sha256` **birebir aynı**:

```
uc_okuma_oz_tercih.json     sha256 a3e51e3236537bf95645bfbbba5da8c4a3fd3cf35eb7964b39ea5dc5a74f5b4b  (2× aynı)
harness_tablo_oz_tercih.json sha256 861d6e9d3b17d4e4a654a0f0c54d06484bc81948fa9f1796c9856f2e9f34f258  (2× aynı)
```

Deterministik taraf temiz — kusur 23'ün sınıfı bu koşuda **tekrarlanmadı**.

## 11. Ne KURULMAZ / kapsam dışı

- Bu hücre **notlamaya girmez** — `harness_tablo` rakip tablosuna **yazılmadı**.
- Sonnet-5'in yayımlanan kütlesi (**0,8348**, `hp-rakip-havuzu`) **oynamadı** — bu bulgu ayrı
  bir dosyada durur.
- Üçüncü hakem ailesi (Google) **kurulmadı** — bu turun YAPILMAZ listesinde.
- Donmuş TEST **ellenmedi**.
- Diğer üç rakip kolu **tek hakemli** kaldı (grill kararı 7).
- Bizim kolumuz **yeniden puanlanmadı** — `0,8011` ve `0,6940` (KAPPA.md §5) zaten elimizdeydi.
- `v1.0` kapı hükmü **kurulmadı** (6.7'nin işi) — bu bulgu kapının hiçbir maddesine girmez.
