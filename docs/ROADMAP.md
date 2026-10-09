# ROADMAP — ne, neden, hangi ölçülmüş boşluk

> **Yön belgesi.** Her adım bir **ölçülmüş boşluğa** bağlıdır; hiçbir satır *"iyi olurdu"*
> gerekçesiyle burada değil. Sıradaki işin sırası: [`superpowers/00-IS-SIRASI.md`](superpowers/00-IS-SIRASI.md)
> (hangisinin önce olduğu **insan kararıdır**). Biten işin ayrıntısı `docs/record/` ve `docs/adr/`'dedir.

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
SIRADA    v2          tgta_v1 üstüne GRPO + düşünce ayarı          ADR-0075 · plan yazılmadı
SIRADA    kapsam      mevzuat kapsam + tazelik                     ayrı plan · grill'de 9 madde açık
AÇIK      borçlar     kusur 5a · 23 · 27 · 31 ; B1 ; ucuz işler
```

### 1 · `v2` — RL (model) + uygulama katmanı *(ADR-0075, insan kararı 2026-09-08)*

```
v1   ham base ──► SFT (τ_g) + ORPO (τ_a) ──► ham TIES ──► tgta_v1 ──► YAYIN   (task-vector hattı DONDURULDU)
v2   tgta_v1 (bf16) ──► GRPO + düşünce (thinking) ayarı ──► v2.0
```

`v2` sequential RL'dir: `tgta_v1`'i yeni başlangıç almak `τ = θ_ft − θ_base` tanımını bozar; iddia
merge değil **RL kazancıdır**. Mümkün çünkü **doğrulanabilir ödül hazır**: `hakhukuk/cekirdek/terazi.py`
atıf doğrulamasını deterministik yapıyor (reward model ve hakem bedeli yok).

- **Ödül çekinmeyi korumak ZORUNDA** (ADR-0075 m.4): düz SFT abstention'ı yok etti (ADR-0010), RL'de risk
  daha keskin. Korunacak taban: uydurulmuş madde **0/114** · aşırı-red **4/80** · kütle **0,8011**.
- **Tur başlamadan ön-kayıt:** ödül fonksiyonu + hedef bant + **durma kuralı** (ADR-0050).
- **Devralınanlar:** `B1` (misattribution — fp16 rejiminde `wrong_ref_rate_micro` 0,0769 → 0,1553, 2,0× ağırlaştı,
  [#66](record/kronoloji-63-71.md#66)) · `B11` (iskele işaretlerinin kaynağı eğitim verisi) · araç kullanımının
  öğrenilmesi (ödüle *"doğru aracı doğru anda çağırdı mı"* girer).
- **Uygulama tarafı:** canlı `bedesten` API (**B6**, TR IP şart) · tazelik boru hattı · HTTP API + barındırma
  (**S9**) · tablo/cetvel satırları (**B9**, ~7.966 satır) · web arayüzü.

**`B1`/`B4` eğitim turları `v1`'de koşulmadı** ([ADR-0075](adr/kararlar-0064-0085.md#adr-0075)): `B1`'de
rakiplerden geride değildik (8/80 ↔ 8·8·7·8) ve vekil metrik yok (her tur 80 kalem gözle okuma); `B4` bir
**merge** kaybı, `v2`'de merge olmadığı için konusuz. İkisi borç olarak açık — ne verecekleri bilinmiyor.

### 2 · Mevzuat kapsam + tazelik *(ayrı plan, grill sonrası)*

**Ölçülmüş boşluk:** korpus **892 kanun · 40.496 madde** — yönetmelik/tüzük/KHK **yok**. Tarih alanı
2026-09-07'de eklendi (`data/corpus/KUNYE.json`).
**Hedef:** **~287,6-287,8 bin** madde (ölçülen oran 45,4 madde/belge); indeks ≈ 8× büyür.
Eski ~340.303 hedefi **yanlıştı** (`917 × 102,7` sayımı) — düzeltilmiş kat merdiveni ve mimari öz
[ADR-0083](adr/kararlar-0064-0085.md#adr-0083) §EK'te; plana girecek **dokuz açık soru** §EK E.5'te.
**Bağımlılık:** indeks dağıtımının son hâli ve temiz-makine kapısı (`git clone` çalışan ürün vermiyor:
indeks git'te yok) bu işi bekliyor.

### 3 · Açık borçlar ve ucuz işler

| iş | not |
| :--- | :--- |
| kusur **5a · 23 · 27 · 31** | [ADR-0083](adr/kararlar-0064-0085.md#adr-0083) sicili (31 kusur değil, kayıt) |
| üçüncü **hakem ailesi** · rakip kolunun ikinci hakemle puanlanması | bütçe — tahmini $2,81 ([ADR-0074](adr/kararlar-0064-0085.md#adr-0074)) |
| TUI gözle doğrulama | `python -m hakhukuk.arayuz.tui`, üç soru, gözle gör · $0 |
| `recall_taban.json` yazılsın | Faz 0'ın tek *"kaynaklanmadı"* ihlali · $0, ~15 dk |
| korpus bütünlüğü | `4857/Madde 111` **yineleniyor**, iki kopyanın `mulga` alanı çelişiyor (ölçüldü 2026-09-07) |
| `terazi` yinelenen atıf | 1. soruda aynı atıf iki kez üretiliyor → kullanıcıya iki uyarı |
| `models/` ~20 GB temizliği (T1) | yalnız merge GGUF yayımlanır (S7 kapandı) |

Kabul testinin erişim tavanı **≈0,75** (DEV 0,95 değil) — raporlaması zorunlu (ADR-0069); donmuş TEST
yeniden açılırsa yine **insan onayıyla, tek kez**.

## Açık kararlar

| # | soru | durum |
| :-- | :--- | :--- |
| **S9** | `v2` nasıl barındırılır? | açık |
| **S10** | sorumluluk ibaresinin **nihai hukuki metni** | geçici metin yürürlükte, hukukçu görüşü bekliyor |
| **S12** | KARAR-6 paralel slot (`-np`) | ertelendi — `τ_a` v2 turuna |
