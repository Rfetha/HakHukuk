# `docs/superpowers/` — iş sırası

> Bu klasörün **giriş dosyası** ve **tek durum kaynağı**. Neyin şimdi, neyin sonra olduğunu
> söyleyen tek yer.
>
> **Bu dosya bir HARİTA, bir plan değildir.** Kutucuk taşımaz. Bir işi sıradan çıkarmak ya da
> araya sokmak **insan kararıdır** — kendi başına yapma.
>
> **Bugün klasörde bir tek bu dosya var** — canlı plan **yok**. Kapanan planlar
> **silinir**, kayda dönüşür ([ADR-0083](../adr/kararlar-0064-0085.md#adr-0083) emsali;
> son dört dosya 2026-09-13'te silindi, bulguları
> [ADR-0086](../adr/kararlar-0064-0085.md#adr-0086)'ya taşındı). Konvansiyon (ADR-0056):
> **aynı anda en çok bir canlı plan.**

---

## Bir bakışta — iki aday, ikisi de DURUYOR

| # | iş | durum |
| :-- | :--- | :--- |
| **1** | **`v2-RL-GRPO`** — `tgta_v1` üstüne GRPO + düşünce ayarı | ⏸️ **DURUYOR** · plan yazılmadı · **sıradaki aday** → §1 |
| **2** | **korpus turu** — mevzuat kapsam + tazelik (40.496 madde → **~288 bin**) | ⏸️ **DURUYOR** · plan yazılmadı; girdisi [ADR-0083](../adr/kararlar-0064-0085.md#adr-0083) §EK'te, **grill'e girecek 9 madde açık** · **sıradaki aday** |

**Hangisinin önce olduğu yazılı değil — bu bir insan kararıdır.** İkisi de `v1.0`'dan sonraya
alınmıştı: korpus turu grill kararı 1/9 ile bu turun **dışında** bırakıldı, `v2` ise hiç açılmadı.

⭐ **v2 STARTER PROMPT — henüz yazılmadı, bkz. `v2-devir-prompt.txt` İŞ 4.**

---

## 1 · `v2-RL-GRPO` — DURUYOR, planlanmadı

```
v1   ham base ──► SFT (τ_g) + ORPO (τ_a) ──► ham TIES ──► tgta_v1 ──► YAYIN
v2   tgta_v1 (bf16) ──► GRPO + düşünce (thinking) ayarı ──► v2.0
```

**`v1` SFT ile KAPANIR** ([ADR-0075](../adr/kararlar-0064-0085.md#adr-0075)) —
`B1`/`B4` eğitim turları **koşulmaz**. İkisinin gerekçesi ayrıdır ve ölçülmüştür: `B1`'de
rakiplerden **geride değildik** (8/80 ↔ 8·8·7·8); `B4` bir **merge** kaybıdır ve `v2`'de merge
olmadığı için **konusuz** kalır.

**Bedeli yazılıdır:** `τ = θ_ft − θ_base` tanımı tüm kolların **aynı base'i** paylaşmasını şart
koşar ⇒ `tgta_v1`'i yeni başlangıç almak bunu bozar ⇒ **task-vector hattı `v1`'de DONDURULUR**,
`v2`'ye taşınmaz. `v2`'nin iddiası merge değil **RL kazancıdır**.

**`v2`'ye devredilenler:** `B1` (misattribution — ⚠️ son turda **ağırlaştı**: fp16 rejiminde
`wrong_ref_rate_micro` **0,0769 → 0,1553**, yani **2,0×**,
[#66](../record/kronoloji-63-71.md#66)) · `B11` (iskele işaretlerinin **kaynağı** eğitim
verisi) · araç kullanımının **öğrenilmesi** (GRPO ödülüne *"doğru aracı doğru anda çağırdı mı"*
girer) · **S9** (barındırma) · web arayüzü · açık kusur **5a** · **23** · **27**
([ADR-0083](../adr/kararlar-0064-0085.md#adr-0083) sicili; **31** kusur değil, **kayıt**).

---

## Durum künyesi — 2026-09-13

```
sürüm      v1.0 (ürün, 2026-09-13 etiketlendi) · artefakt HakHukuk-4B-v0.1 (tgta_v1)
           ağırlıklar ve indeks HF'te PUBLIC
test       335 geçti, 2 xfail                     (kaynak: pytest -q)
dal        master · ağaç temiz
kayıt      ADR 0001-0086, yeni karar 0087'den     (kaynak: docs/adr/README.md)
           kronoloji #01-#38 emekli hat · #39-#71 yeni hat, yeni girdi #72'den
                                                  (kaynak: docs/record/README.md)
           tuzak defteri 85 satır (1.1-7.8 · 2.19 · 2.20 · 2.21)
                                                  (kaynak: yurutme-tuzaklari.md başlığı)
katman     docs/record + docs/adr = 12 dosya · 608 KB   (ADR-0086)
indeks     Rfetha/HakHukuk-mevzuat-bge-m3-s2 — dataset, PUBLIC
ağırlık    Rfetha/HakHukuk-4B-GGUF — PUBLIC (dosya adı bilerek v0.3, ADR-0065)
```

⛔ **`v1.0` bir MODEL İYİLEŞMESİ DEĞİL.** Ağırlıklar hiç değişmedi (`sha256` birebir), κ
**değişmedi** (0,534/0,409, aracın eşiği 0,6), panel hâlâ **iki** aileli. Kapanan şey κ değil,
**eşit sınavın yokluğuydu** ([ADR-0084](../adr/kararlar-0064-0085.md#adr-0084)).
Manşet koşulsuz bir **ARALIK**: `%69,4-80,1` (`claude-sonnet-5` ↔ `gpt-4o-mini`).

---

## Kapanan turlar — işaretçi, anlatı değil

| tur | payda | nerede okunur |
| :--- | :--- | :--- |
| `v1-son-iş` (2026-09-13) | **71/71** | [ADR-0084](../adr/kararlar-0064-0085.md#adr-0084) · [#70](../record/kronoloji-63-71.md#70) — *(planı 2026-09-13'te silindi, [ADR-0086](../adr/kararlar-0064-0085.md#adr-0086))* |
| kayıt katmanı kompaktlama (2026-09-13) | — | [ADR-0086](../adr/kararlar-0064-0085.md#adr-0086) — *(planı ve spec'i aynı gün silindi; kapanış bulguları ADR'ye taşındı)* |
| `hp` → Hat A → Hat B (2026-09-12) | **115/115** | [#66](../record/kronoloji-63-71.md#66) · [#67](../record/kronoloji-63-71.md#67) · [ADR-0083](../adr/kararlar-0064-0085.md#adr-0083) |
| `faz0-ölçüm-zinciri` (2026-09-06/07) | **48/48** | [#62](../record/kronoloji-53-62.md#62) |

---

## Bakım kuralı

Bir iş kapandığında **iki yer** güncellenir: işin kendi kapanış kaydı ve **bu dosyanın
"Bir bakışta" tablosu**. Sıra değişirse **gerekçe buraya yazılır** — sıra değişikliğinin *niçin*i
başka hiçbir yerde durmuyor.

**Kapanan plan yeniden işletilmez.** Kapanış anında açık kalan **her** kusur **adıyla** devredilir;
devredilmemiş açık kusur varsa **kapanış geçersizdir**. Sicil ve devir
[ADR-0083](../adr/kararlar-0064-0085.md#adr-0083)'te.

**Çapa atıf biçimi** (kayıt katmanı 2026-09-13'te kompaktlandı, tekil dosyalar yok):
`ADR-00NN` → `../adr/kararlar-*.md#adr-00NN` · kronoloji `#NN` → `../record/kronoloji-*.md#NN`.
Eski metinde geçen *"research_log #42"* = *"kronoloji #42"*.
**Yeni kronoloji girdisi #72'den, yeni ADR 0087'den devam eder.**
