# ROADMAP v1 — ürün yol haritası

> **Yön belgesi.** Her adım bir **ölçülmüş boşluğa** bağlıdır; hiçbir satır *"iyi olurdu"*
> gerekçesiyle burada değil. Ürünün sırası artık araştırma takvimine bağlıdır:
> [`YAYIN_YOL_HARITASI.md`](YAYIN_YOL_HARITASI.md) (Checkpoint 1 → Checkpoint 2 → korpus turu).
> Biten işin ayrıntısı `docs/record/` ve `docs/adr/`'dedir; iş sırası girişi
> [`superpowers/00-IS-SIRASI.md`](superpowers/00-IS-SIRASI.md).

## Bitenler

- `v1.0` etiketlendi (2026-09-13) — model iyileşmesi değil, **ölçüm aletinin ikinci bir hakem ailesi altında geçmesi** ([ADR-0084](adr/kararlar-0064-0085.md#adr-0084)).
- Ölçüm zinciri onarıldı: kütle %68,4 → **%80,1**, ağırlıklar değişmeden ([#62](record/kronoloji-53-62.md#62)).
- Hakem paneli iki aileye çıktı.
- Ürün paketi kuruldu: `hakhukuk/` (CLI · TUI · HTTP API) + Docker.
- Belge katmanı yeniden kuruldu.
- Araç katmanı eklendi ([ADR-0076](adr/kararlar-0064-0085.md#adr-0076)).
- Donmuş TEST kabul testi bir kez koşuldu ([#66-#67](record/kronoloji-63-71.md#66)).
- Ağırlıklar ve indeks HF'te public.
- Kusur sicili ve devir tablosu: [ADR-0083](adr/kararlar-0064-0085.md#adr-0083).

## Yapılacaklar

```
CP1   Eylül 2027   Makale 1 · ürün, Qwen ↔ Gemma karşılaştırmasının kazananıyla güncellenir
CP2   yaz 2028     Makale 2 · kazananın üstüne GRPO = ürün v2.0
CP2'den sonra      mevzuat kapsam + tazelik (korpus turu)
sürekli            açık kusurlar 5a · 23 · 27 · 31 · ucuz işler
```

`v1.0` (`tgta_v1`, `HakHukuk-4B-v0.3-Q4_K_M.gguf`) bütün süre boyunca çalışan yedek ürün olarak durur.

### 1 · Checkpoint 1 — ürüne etkisi *(Eylül 2027)*

Makale 1, iki temel modelde (Qwen3.5-4B, Gemma 4 E4B; her biri 3 seed) dört eğitim yolunu
karşılaştırır: tek kollar · ayrı kollar + ham TIES · tek eğitimde birlikte öğretme · ardışık eğitim
([`YAYIN_YOL_HARITASI.md`](YAYIN_YOL_HARITASI.md) §2). Testte kütlesi en yüksek (temel model, yöntem)
çifti **ürünün yeni modeli olur**, şu dört kapıyı geçmek şartıyla:

1. düşünce koruma eşiğini kendi ham modeline göre geçer;
2. yanlış maddeye dayanma, `tgta_v1`'in aynı testteki değerinden kötü değildir;
3. Q4_K_M'de 4.096 bağlamda **≤8 GB VRAM** ([ADR-0018](adr/gemma4-12b-dersler.md#adr-0018));
4. lisansı açık ve ürünün Apache-2.0 dağıtımıyla uyumludur.

İki aday güven aralıkları içinde berabereyse ürün `tgta_v1`'de kalır.

**Kazanan değişirse ürün işleri** (Haziran–Temmuz 2027):

| iş | not |
| :--- | :--- |
| GGUF (Q4_K_M), `sha256`, HF'te pinli revizyon | adlandırma [ADR-0071](adr/kararlar-0064-0085.md#adr-0071); `indir` kimlik kapısı yeni dosyaya bağlanır ([ADR-0078](adr/kararlar-0064-0085.md#adr-0078)) |
| konteyner rejim kilidi | `docker/compose.yaml` bayrakları yeni modelde yeniden doğrulanır; `tests/test_konteyner.py` |
| düşünce kapatma | `servis.answer()`'ın iki geçişli zorunlu kapatması `</think>`'e göre yazılı ([ADR-0080](adr/kararlar-0064-0085.md#adr-0080)); Gemma'nın kapanış işaretine ve `--reasoning-format` davranışına göre parametrelenir |
| ürün yolu ölçümü | konteyner API'si üzerinden 80 DEV sorusu, ölçüm hattıyla kıyas (emsal: kütle 0,7792 ↔ 0,8011, [#70](record/kronoloji-63-71.md#70)) |
| VRAM tablosu | 4.096 · 32.768 · 131.072 bağlamda yeniden ölçülür |
| model kartı | `MODEL_CARD.md` güncellenir, HF sürümü `scripts/hf_kart.py` ile üretilir |

Arama katmanı ve korpus değişmez (S2 indeksi, 40.496 madde).

**Checkpoint 1'in ürün deposuna getirdiği altyapı** (F0, Ekim–Kasım 2026):

- **Eğitim ortamı kilidi:** [`EGITIM_ORTAMI.md`](EGITIM_ORTAMI.md) + `configs/egitim_ortami.yaml` +
  eğitim betiklerinin başında kontrol ve test. Bugün `--bf16-base` verilmezse eğitim sessizce
  4-bit NF4'e düşüyor ve `fla-core` sürümsüz kuruluyor.
- **Yedekler:** eski git geçmişinin bundle'ı ve `outputs/tg_v1`, `outputs/ta_v1` adaptörleri ikinci
  kopyaya alınır; [ADR-0034](adr/kararlar-0027-0044.md#adr-0034)'ü değiştiren ADR ile.
- **Ölçüm ortamı:** bütün ölçümler aynı dizüstünde, aynı llama.cpp sürümü ve konteynerin kilitli
  bayraklarıyla koşar.

### 2 · Checkpoint 2 — `v2.0`: kazananın üstüne GRPO *(yaz 2028)*

```
v1    ham base ──► SFT (τ_g) + ORPO (τ_a) ──► ham TIES ──► tgta_v1 ──► v1.0 (yayında)
CP1   Qwen ↔ Gemma × dört eğitim yolu ──► kazanan ──► ürün (kazanan değişirse)
CP2   kazanan (bf16) ──► GRPO + düşünce hizalaması ──► v2.0
```

`v2` ardışık RL'dir; iddia birleştirme değil **RL kazancıdır** ([ADR-0075](adr/kararlar-0064-0085.md#adr-0075)).
Ödül hakemsizdir ve atıf doğrulayıcının göremediği isabetsiz atıfı da kapsar
([`YAYIN_YOL_HARITASI.md`](YAYIN_YOL_HARITASI.md) §3.2): altın maddeye atıf + · başka gerçek maddeye
0/− · uydurulmuş madde − · altın yokken susma + · altın varken susma −.

- **Korunacak tabanlar:** kazananın Checkpoint 1'deki uydurulmuş madde, gereksiz red ve kütle değerleri.
- **Tur başlamadan ön-kayıt:** ödül katsayıları + hedef bant + **durma kuralı** (ADR-0050).
- **Devralınanlar:** `B1` (isabetsiz atıf — ödülün doğrudan hedefi; fp16 rejiminde `wrong_ref_rate_micro`
  0,0769 → 0,1553, [#66](record/kronoloji-63-71.md#66)) · `B11` (iskele işaretlerinin kaynağı eğitim
  verisi) · araç kullanımının öğrenilmesi.
- **Rakip karşılaştırması** (Gemini Flash-Lite, Flash, Claude Sonnet sınıfı) Checkpoint 2'de, mühürlü
  test parçasında yapılır.
- **Uygulama tarafı:** canlı `bedesten` API (**B6**, TR IP şart) · tazelik boru hattı · HTTP API +
  barındırma (**S9**) · tablo/cetvel satırları (**B9**, ~7.966 satır) · web arayüzü.

`B4` (τ_a'nın birleştirmede seyrelmesi, 0,987 → 0,766) Makale 1'in RQ1'i içinde, birlikte ve ardışık
eğitimle karşılaştırılarak ölçülür.

### 3 · Mevzuat kapsam + tazelik *(Checkpoint 2'den sonra)*

**Ölçülmüş boşluk:** korpus **892 kanun · 40.496 madde** — yönetmelik/tüzük/KHK **yok**. Tarih alanı
2026-09-07'de eklendi (`data/corpus/KUNYE.json`).
**Hedef:** **~287,6-287,8 bin** madde (ölçülen oran 45,4 madde/belge); indeks ≈ 8× büyür.
Eski ~340.303 hedefi **yanlıştı** (`917 × 102,7` sayımı) — düzeltilmiş kat merdiveni ve mimari öz
[ADR-0083](adr/kararlar-0064-0085.md#adr-0083) §EK'te; plana girecek **dokuz açık soru** §EK E.5'te.
**Neden Checkpoint 2'den sonra:** korpus değişince arama sonuçları değişir; eşit sınav ve yayımlanan
sayılar askıya alınır (§EK E.6) ve Makale 2'nin mühürlü testi bugünkü korpusa bağlıdır.
**Bağımlılık:** indeks dağıtımının son hâli ve temiz-makine kapısı (`git clone` çalışan ürün vermiyor:
indeks git'te yok).

### 4 · Açık borçlar ve ucuz işler

| iş | not |
| :--- | :--- |
| kusur **5a · 23 · 27 · 31** | [ADR-0083](adr/kararlar-0064-0085.md#adr-0083) sicili (31 kusur değil, kayıt) |
| üçüncü **hakem ailesi** | Checkpoint 2'deki rakip karşılaştırmasıyla birlikte ele alınır ([ADR-0074](adr/kararlar-0064-0085.md#adr-0074)) |
| TUI gözle doğrulama | `python -m hakhukuk.arayuz.tui`, üç soru, gözle gör · $0 |
| `recall_taban.json` yazılsın | Faz 0'ın tek *"kaynaklanmadı"* ihlali · $0, ~15 dk |
| korpus bütünlüğü | `4857/Madde 111` **yineleniyor**, iki kopyanın `mulga` alanı çelişiyor (ölçüldü 2026-09-07) |
| `terazi` yinelenen atıf | 1. soruda aynı atıf iki kez üretiliyor → kullanıcıya iki uyarı |
| `models/` ~20 GB temizliği (T1) | yalnız merge GGUF yayımlanır (S7 kapandı) |

Eski donmuş TEST'in erişim tavanı **≈0,75** (DEV 0,95 değil) — raporlaması zorunlu (ADR-0069). Makale
1'de bu küme, yeni sorularla birlikte son testin bir parçası olur ve sonuçlar iki parça için ayrıca
raporlanır.

## Açık kararlar

| # | soru | durum |
| :-- | :--- | :--- |
| **S9** | `v2` nasıl barındırılır? | açık |
| **S10** | sorumluluk ibaresinin **nihai hukuki metni** | geçici metin yürürlükte, hukukçu görüşü bekliyor |
| **S12** | KARAR-6 paralel slot (`-np`) | ertelendi — paralel slot cevap metnini değiştiriyor ([ADR-0062](adr/kararlar-0045-0063.md#adr-0062)); ölçüm ortamı Checkpoint 1 ve 2 boyunca kilitli |
