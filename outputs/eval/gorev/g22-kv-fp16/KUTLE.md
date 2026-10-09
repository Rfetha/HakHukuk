# G22 · Adım 2 — fp16 KV koşusunun KÜTLESİ (hakemle ölçüldü)

**Tarih:** 2026-09-11 · **Özne:** `tgta_v1` = `HakHukuk-4B-v0.1` (**ağırlıklar DEĞİŞMEDİ**)
**Ölçülen:** faithful-answer mass (kütle) = `coverage × A1_cevaplanan` — çıpanın **0,8011**'i ile
**aynı birimde**.

> ⛔ **YAYIMLANAN 0,8011 DEĞİŞMEZ.** Bu belge yalnız *"fp16 KV rejiminde kütle şudur"* der.
> Ürünün ya da modelin manşetini **yeniden yazmaz**: manşet, üründe kullanılan `q8_0/q8_0` KV
> rejiminin sayısıdır ve o koşu (`outputs/eval/f02-biz-onsozsuz/`) olduğu gibi durur.
> Burada ölçülen şey bir **taşıyıcı ayarının** kütle üzerindeki etkisidir.

---

## 1 · Sonuç — tek tablo

| eksen | ÇIPA `q8_0/q8_0` | fp16 (bu koşu) | fark | kaynak dosya |
| :--- | ---: | ---: | ---: | :--- |
| **kütle (`kutle_tum`)** | **0,8011** | **0,7932** | **−0,79 puan** | çıpa `f02-biz-onsozsuz/harness_tablo.json` · yeni `g22-kv-fp16/harness_tablo_gnd.json` |
| `coverage` | 0,9375 | 0,9375 | 0,00 | aynı dosyalar |
| `A1_cevaplanan` | 0,8545 | 0,8461 | −0,84 puan | aynı dosyalar |
| `faith_macro_tum` (çekinme dahil) | 0,8499 | 0,8350 | −1,49 puan | aynı dosyalar |
| `A1_altin_getirilen_alt_kume` | 0,8902 | 0,8693 | −2,09 puan | aynı dosyalar |
| `recall@10` | 0,9500 | 0,9500 | 0,00 | aynı dosyalar |
| `faithfulness_micro` | 0,8315 | 0,8106 | −2,09 puan | `gnd_*_summary.json` |
| `cit_precision_micro` | 0,9231 | 0,8252 | **−9,79 puan** | `gnd_*_summary.json` |
| `wrong_ref_rate_micro` | 0,0769 | 0,1553 | **+7,84 puan (kötüleşme)** | `gnd_*_summary.json` |
| `total_claims` | 273 | 301 | +28 | `gnd_*_summary.json` |
| çekinme (`exact_reject`, mod=data) | 5/80 | 5/80 | 0 | `a1_*.txt` · `rescore_answered.py` |

**Kütle formülü** (`harness_tablo.py:220`): `kutle_tum = coverage × A1_cevaplanan`.
Çıpa: `0,9375 × 0,8545 = 0,8011` · fp16: `0,9375 × 0,8461 = 0,7932`. **Doğrulandı.**

---

## 2 · Gürültü tabanı şerhi — fark SİNYAL Mİ?

CLAUDE.md'nin kaydettiği hakem **yeniden-koşma gürültü tabanı ≈ 0,3 A1 puanı**; bundan küçük
hiçbir fark yorumlanmaz.

| büyüklük | değer | taban | oran |
| :--- | ---: | ---: | ---: |
| ΔA1 | **−0,84 puan** | 0,30 puan | **2,8×** |
| Δkütle | **−0,79 puan** | 0,30 × 0,9375 ≈ **0,28 puan** | **2,8×** |

**Hüküm: fark tabanın ÜSTÜNDE — ama YALNIZ 2,8× ve tek yönlü bir hükme yetmez. Üç sebep:**

1. **Taban yanlış sınıftan.** ~0,3 puanlık taban *aynı cevaplara* hakemi yeniden koşmanın
   gürültüsüdür. Burada **cevaplar da değişti** (Adım 1: 65/80 kalem bayt olarak farklı). Yani
   gözlenen fark iki gürültü kaynağını **birlikte** taşıyor ve *bu koşu çifti için* aynı-cevap
   tabanı **ÖLÇÜLMEDİ**. Ölçmek ikinci bir hakem koşusu ister (≈$0,044) — **koşulmadı**.
2. **Kalem düzeyi, toplulaştırmanın gizlediği kadar çalkantılı.** 80 kalemin **18'inde**
   `faithfulness` değişti ve değişim **iki yönlü**: id 30 `0,00 → 0,875` · id 9 `0,50 → 1,00`
   yukarı; id 1 `0,833 → 0,00` · id 39 `1,00 → 0,00` aşağı. Toplam fark bu ±0,5-1,0'lık
   salınımların **neredeyse birbirini götürmesinden** artakalandır.
3. **Kontrol değişkeni zaten düşmüştü** (Adım 1, `KUNYE.json → KONTROL_DEGISKENI_DUSTU`):
   id 7 ve 63'te retriever farklı kaynak getirdi — sebep KV değil, çıpadan sonra gelen
   **yürürlük süzgeci** (commit `63b691e`). Temiz alt kümede de sonuç değişmiyor:

   | küme | çıpa kütle | fp16 kütle | fark |
   | :--- | ---: | ---: | ---: |
   | tüm n=80 | 0,8011 | 0,7932 | −0,79 puan |
   | **temiz n=78 (7·63 hariç)** | 0,7960 | 0,7879 | **−0,81 puan** |

**Söylenebilecek cümle:** *"fp16 KV'ye geçmek kütleyi ölçülebilir biçimde YÜKSELTMEDİ; en iyi
tahmin ≈1 puan aşağıda ve bu, gürültü tabanının ~3 katı."*
**Söylenemeyecek cümle:** *"fp16 modeli 0,8 puan bozar."* — aynı-cevap tabanı ölçülmediği için
farkın ne kadarının hakem gürültüsü olduğu **bilinmiyor**.

---

## 3 · Tabanın çok üstünde olan TEK eksen: atıf isabeti

`cit_precision_micro` **0,9231 → 0,8252** ve `wrong_ref_rate_micro` **0,0769 → 0,1553** —
yanlış-madde oranı **iki katına** çıktı. Bu, 0,3 puanlık tabanın **26 katı** bir hareket ve
Adım 1'in hakemsiz bulgusuyla **aynı yönde**: fp16 kolu daha çok atıf yaptı (114 → 152 atıf,
`atif_dagilimi`) ve katı atıf kapısının reddi `0 → 3` çıktı.

⚠️ Bu eksen **B1 (yanlış atıf)** ekseniyle aynı eksendir ve planın bir sonraki birinci-derece
işidir. Burada **hüküm kurulmuyor** — n=80'de mikro oran, 116 ↔ 161 atıf paydası üzerinden
hesaplanıyor ve tek koşu. Kayda geçiriliyor.

---

## 4 · Çapraz doğrulama — tuzak 2.16 (`A1` = cevaplanan-only)

`harness_tablo.py`'nin `A1_cevaplanan`'ı, bağımsız betik `rescore_answered.py` ile **iki kolda da**
karşılaştırıldı:

| kol | `harness_tablo.json → A1_cevaplanan` | `rescore_answered.py → A1_faithfulness_macro_answered` | tuttu mu |
| :--- | ---: | ---: | :--- |
| çıpa | 0,8545 | **0,8545** | ✅ BİREBİR |
| fp16 | 0,8461 | **0,8461** | ✅ BİREBİR |

`faith_macro_tum` (çekinme dahil) **ayrı alan** olarak raporlanıyor ve **farklı** bir sayı
(çıpa 0,8499 · fp16 0,8350) — tuzak 2.16'nın istediği ayrım korundu.
Çıktı: `a1_h1_tgta_v1_g22_fp16.txt`.

**Çekinme kümesi — sayı aynı, BİLEŞİM farklı** (Adım 1 §6 ile tutarlı):
çıpa `{15, 37, 45, 66, 79}` ↔ fp16 `{15, 45, 51, 66, 79}`. id 37 fp16'da **cevapladı**,
id 51 **çekindi**. `coverage` bu yüzden sayısal olarak aynı (5/80) ama **aynı kalemler değil**.

---

## 5 · Önbellek davranışı — tuzak 2.17

**Bu boru hattında hakem önbelleği YOKTUR ve hiçbir sayı çıpadan DEVRALINMADI.**

| kontrol | bulgu |
| :--- | :--- |
| `groundedness.py` içinde önbellek | **yok** — `grep -n "cache\|önbellek"` → 0 eşleşme |
| `llm_client.py` içinde önbellek | **yok** — 0 eşleşme |
| `harness_tablo.py` içinde önbellek | **yok** — 0 eşleşme; `valid_trap_cache.py` yalnız `score_abstention` hattında (M2/M2b) kullanılır, bu koşuda **çağrılmadı** |
| `gecerlilik_onbellekten` alanı | üretilen hiçbir çıktıda **yok** (alan bu boru hattına ait değil) |
| **davranışsal kanıt** | 80 kalemin **hepsi** için taze hakem çağrısı yapıldı ve **para harcandı** ($0,0438 · aşağıda ölçüldü). Önbellek devralınsaydı bedel ≈$0 olurdu. |
| **ikinci kanıt** | duman koşusunda id 43 çıpada `faith=0,6 claims=5`, fp16'da `faith=0,5 claims=2` — çıpanın değeri **yeniden kullanılmadı** |

---

## 6 · Bedel — tahmin ↔ ÖLÇÜM

### 6.1 Duman koşusu (5 kalem, tabakalanmış)

Tabakalama: 80 kalem cevap uzunluğuna göre sıralandı, **5 eşit tabakanın medyanı** seçildi →
id `43 · 61 · 47 · 13 · 22` (cevap uzunlukları 376 · 587 · 707 · 820 · 975 karakter).
Ölçek, kalem sayısı değil **hakem-istemi karakter yükü** üzerinden hesaplandı
(`2×len(cevap) + len(soru) + len(referans[:3500])`): seçilen 13.076 ↔ toplam 235.891 → **×18,04**
(naif 5/80 ölçeği ×16,0'dan daha muhafazakâr).

| kalem | değer |
| :--- | ---: |
| duman koşusu gerçek bedeli (n=5) | **$0,0027** |
| tabakalanmış ölçek | ×18,04 |
| **doğrusal tahmin (n=80)** | **$0,0487** |
| **+%50 emniyet payı (tuzak 1.11)** | **$0,0731** |
| **sert bütçe kapısı** | $0,15 |
| **kapı sonucu** | **GEÇTİ** — üst sınır kapının %49'u |

### 6.2 Gerçek harcama (ölçüldü)

| kalem | değer | kaynak |
| :--- | ---: | :--- |
| OpenRouter `total_usage` — koşudan ÖNCE | $17,91293753 | `GET /api/v1/credits` |
| OpenRouter `total_usage` — koşudan SONRA | $17,95800443 | `GET /api/v1/credits` |
| **GERÇEK HARCAMA (duman + tam koşu)** | **$0,045067** | fark |
| betiğin kendi hesabı: duman $0,0027 + tam $0,0438 | $0,0465 | `gnd_*_summary.json → judge_cost_usd` |
| bakiye — ÖNCE | $2,087062 | |
| **bakiye — SONRA** | **$2,041996** | |

**Tahmin ↔ gerçek:** doğrusal tahmin $0,0487 ↔ gerçek $0,0451 → tahmin **%8 YÜKSEK** (güvenli yön).
Emniyet paylı üst sınır $0,0731 hiçbir noktada zorlanmadı. **Sert kapı $0,15 aşılmadı**;
gerçek harcama kapının **%30'u**.

> 📌 `judge_cost_usd` betiğin `PRICE` tablosundan **hesapladığı** liste-fiyat rakamıdır;
> $0,045067 ise sağlayıcının **faturaladığı** rakamdır. İkisi %3 içinde uyuşuyor —
> bu turda liste fiyatı gerçeğe yakın. Kayda geçiriliyor.

---

## 7 · Birim eşitliği kontrol listesi

Kıyas, yalnız aşağıdaki 16 eksenin **hepsi** tuttuğu için geçerli. Uyuşmazlık hata vermez,
kıyası **geçersiz** kılar.

| # | eksen | çıpa | fp16 | ✓ |
| ---: | :--- | :--- | :--- | :---: |
| 1 | puanlama betiği | `scripts/puanlama/groundedness.py` | aynı | ✅ |
| 2 | betik içeriği | `sha256 4cedec3d…` | **aynı dosya** — çıpa günündeki `scripts/groundedness.py` ile `diff`: yalnız **docstring'deki yol dizesi** farklı, kod BİREBİR | ✅ |
| 3 | hakem modeli | `openai/gpt-4o-mini` | `openai/gpt-4o-mini` | ✅ |
| 4 | geçit | `openrouter` | `openrouter` | ✅ |
| 5 | `LLM_PROVIDER_ORDER` | `OpenAI` | `OpenAI` | ✅ |
| 6 | sıcaklık | `0` (kodda sabit, satır 150 · 165) | aynı | ✅ |
| 7 | `runs` | 1 | 1 | ✅ |
| 8 | `--mode` | `data` | `data` | ✅ |
| 9 | `--source-field` | `referans` (varsayılan) | aynı | ✅ |
| 10 | `--answer-field` | `cevap` (varsayılan) | aynı | ✅ |
| 11 | **`SOURCE_CLIP`** | `MAX_SOURCE_CHARS = 3500` | `3500` | ✅ |
| 12 | istem sürümü — `EXTRACT_SYSTEM` | `len 1584 · sha256 3b56942c67fe0b7309004a9c` | aynı | ✅ |
| 13 | istem sürümü — `VERIFY_SYSTEM` | `len 2006 · sha256 cf1a97e86c26b6784fe0bc9e` | aynı | ✅ |
| 14 | `A1` filtresi | cevaplanan-only makro (ADR-0011), `exact_reject(mode='data')` | aynı | ✅ |
| 15 | `n` | 80 | 80 | ✅ |
| 16 | kütle formülü | `coverage × A1_cevaplanan` (`harness_tablo.py:220`) | aynı | ✅ |

**Uyuşmayan kalem: YOK.**

**Tohum notu (şerh, uyuşmazlık değil):** `groundedness.py` hakeme **`seed` parametresi
GÖNDERMEZ** — belirlenimi yalnız `temperature=0` sağlar. İki kolda da aynı; yani birim eşitliği
bozulmuyor, ama *"hakem birebir tekrar eder"* garantisi **yoktur** ve §2'deki gürültü şerhinin
mekanik sebebi budur.

**Kodun çıpadan sonra değişip değişmediği — denetlendi:**
- `groundedness.py`: `35dac1f` (2026-09-07, T5 klasör bölünmesi) — `git mv`, içerik aynı, yalnız
  docstring yolu. **Hakemlik mantığı değişmedi.**
- `llm_client.py`: `94e79d8` (2026-09-07) — **yalnız** `PRICE` sözlüğüne `anthropic/claude-sonnet-5`
  satırı eklendi. `openai/gpt-4o-mini` yolu, geçit, sağlayıcı pinleme **değişmedi**.
- `harness_tablo.py` · `rescore_answered.py`: yalnız docstring yolu.
- `git status scripts/` → **temiz** (çalışma ağacında yamalı betik yok).

---

## 8 · Tam komutlar — YAN YANA

**ÇIPA** (kaynak: `faz0-olcum-zinciri` planı Görev 2 Adım 2 — plan 2026-09-12'de silindi; koşunun kaydı [#62](../../../docs/record/research_log/2026-09-06-faz0-olcum-zinciri.md)):

```bash
cd /home/ersoy/code/Hukuk-SLM && source ~/code/global_venv/bin/activate && \
set -a && . ./.env && set +a && LLM_PROVIDER_ORDER=OpenAI \
python scripts/puanlama/groundedness.py \
  --details outputs/eval/f02-biz-onsozsuz/h1_tgta_v1_f02_nb_detail.jsonl \
  --label h1_tgta_v1_f02_nb --mode data --judge-model openai/gpt-4o-mini \
  --out-dir outputs/eval/f02-biz-onsozsuz
```

**BU KOŞU** — değişen **yalnız** `--details` · `--label` · `--out-dir`:

```bash
cd /home/ersoy/code/Hukuk-SLM && source ~/code/global_venv/bin/activate && \
set -a && . ./.env && set +a && LLM_PROVIDER_ORDER=OpenAI \
python scripts/puanlama/groundedness.py \
  --details outputs/eval/g22-kv-fp16/h1_tgta_v1_g22_fp16_detail.jsonl \
  --label h1_tgta_v1_g22_fp16 --mode data --judge-model openai/gpt-4o-mini \
  --out-dir outputs/eval/g22-kv-fp16
```

**Tablo** — çıpa (plan Görev 2 Adım 3) ↔ bu koşu, değişen yalnız yollar:

```bash
python scripts/puanlama/harness_tablo.py \
  --details outputs/eval/g22-kv-fp16/h1_tgta_v1_g22_fp16_detail.jsonl \
  --gnd outputs/eval/g22-kv-fp16/gnd_h1_tgta_v1_g22_fp16.jsonl \
  --korpus data/corpus/mevzuat_maddeler.jsonl \
  --out outputs/eval/g22-kv-fp16/harness_tablo_gnd.json
```

> 📌 **Neden `harness_tablo_gnd.json`, neden `harness_tablo.json` değil:** Adım 1'in
> `KUNYE.json`'u hakemsiz `harness_tablo.json`'un `sha256 c723def7…` özetini kaydetmişti.
> O dosyanın üzerine yazmak kaydı bozardı. Yeni dosya yalnız `kutle_ekseni` bloğunu doldurur;
> `erisim` · `atif_dagilimi` · `kapi` · `erisim_davranis_caprazi` · `k2_bedeli` blokları
> **ikisinde de birebir aynı** (programla karşılaştırıldı).

---

## 9 · Ölçülmeyenler (uydurulmadı)

| istenen | durum | sebep |
| :--- | :--- | :--- |
| bu koşu çiftine ait **aynı-cevap** hakem gürültü tabanı | **ÖLÇÜLMEDİ** | ikinci bir hakem koşusu ister (≈$0,044); görevin kapsamı değil. ~0,3 puanlık taban CLAUDE.md'den **devralındı** |
| fp16 kolunun 80 kaleminin **gözle okunması** | **YAPILMADI** | Adım 2'nin kapsamı değil; çıpanın `GOZLE_OKUMA_80.md`'si fp16 cevaplarını **kapsamaz** |
| κ (hakemler arası uyum) | **HESAPLANMADI** | tek hakem ailesi; `v1.0` blokerinin kendisi (ADR-0077) ve bu koşu onu **oynatmaz** |
| atıf isabetindeki düşüşün sebebi | **AÇIKLANMADI** | §3'te kayda geçirildi, hüküm kurulmadı |
