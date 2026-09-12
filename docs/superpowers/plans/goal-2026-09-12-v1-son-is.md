# GOAL — `v1-son-iş` (adım 4b)

> `/goal` olarak verilecek prompt. **Plan değil, planı işaret eder.** Sınır: <4000 krk.
> **v4 — 2026-09-12:** 5·6.1·6.2·6.3·6.3b·6.3c·6.4·6.5·6.6·6.6b kapandı; sıradaki **6.6c**.
> κ borcu ÖDENDİ. Bakiye ölçüldü: **$11,876** (eski $2,04 bayattı). Harcanan: **$4,8345**.

---

İCRA: `docs/superpowers/plans/2026-09-12-v1-son-is.md` — **70 kutucuk, 43'ü kapalı**.
`superpowers:subagent-driven-development` ile sür. Planı ve `.superpowers/sdd/progress.md`
defterini **oku**. **5 · 6.1 · 6.2 · 6.3 · 6.3b · 6.3c · 6.4 · 6.5 · 6.6 · 6.6b BİTTİ — yeniden koşma.**
Sıradaki **6.6c**. ⭐ **κ BORCU KAPANDI:** `3.5 Flash` GÖZ-katı `claude-sonnet-5` altında
**0,6183** → eşik **0,5983**; bizim **0,6940** ⇒ marj **+7,57 p çıpaya göre** (gpt-4o-mini'de
+5,86 p). **İki hakem de aynı yönde.** Hüküm yine de 6.7'nin işi (çözünürlük kuralı).
⭐ **6.6b KAPANDI:** öz-tercih (yalnız Anthropic) **ters yönde** — `Δ_sonnet` +20,03 p ↔
`Δ_biz` +10,71 p, fark>çözünürlük. Notlamaya girmez, `OZ_TERCIH.md`'de durur.

## Sıra — insan kilitli, DEĞİŞTİRME
**6.6c Sonnet-5 isabetsiz atıf ($0)** · **6.6d Sonnet-5 M5 (DUR ①)** ·
6.7 kapı · 6.8 ADR-0084+#68 · 7 push · 8 public · 9 HF görünürlüğü.
*(6.6c/6.6d: HF kartındaki iki `ölçülmedi` hücresi kapanır; ön-kayıtları **aleyhe açık**,
planda yazılı. Temel model sütunu (ᵇ) **kapanmaz** — "ölçülemedi", kapıdan kaldı.)*

## DUR — yalnız burada dur, insana sor
① para tavanı aşıldı: `min(tahmin×1,5 ; $8,00)` ya da kalemin alt-tavanı
② kapı `DÜŞTÜ` ya da `BELİRSİZ` (6.7.5)
③ HF public yapılmadan ÖNCE (9.1)
④ denklik/kimlik kanıtı tutmadı
Başka yerde durma.

## Ön-kayıt — DEĞİŞTİRİLEMEZ (plan §2)
- Kapı m.1 **her hakemin kendi içinde**: `kütle ≥ 3.5 Flash − 0,020`.
- ~~GÖZ-katı miras~~ — **uygulandı 6.5'te**; türetme `scripts/puanlama/uc_okuma_kutle.py`'de,
  kalibrasyon testli.
- Çözünürlük: `n=80` ⇒ adım **1,25 p**. `|marj|<1,25 p` ⇒ **BELİRSİZ**, her iki yönde bağlar.
  Sonuç `v0.4`, gerekçe *"ölçemedik"*.
- **6.6b yalnız Anthropic ailesi** (ÖLÇÜLDÜ, ters yönde); Google hücresi ölçülemez, hiçbir
  hükme girmez.

## Kaynaklı sayılar
κ 0,534 / 0,409 · eşik 0,6 — **κ DEĞİŞMEDİ**, kapanan şey eşit sınavın yokluğu.
BİZ: gpt-4o-mini **0,8011** ↔ sonnet-5 **0,6940** · `3.5 Flash`: **0,7425** ↔ **0,6183**
⇒ marj **+5,86 p** ↔ **+7,57 p** (ikisi de ÇIPAYA göre — eşiğe göre olanla karıştırma!)
Harcanan **$4,8345** (6.6b gerçek fatura $2,6212, tahmin $1,86'yı %41 aştı — tuzak 1.11).
Kalan: 6.6d **~$1,5-3**(≤$3) · 6.6c **$0**.
Üst sınır **$8,00**. Bakiye **$11,876** (ölçüldü).
⚠️ Para kapıları **bakiye farkıyla** doğrulanır — `llm_client` liste fiyatı sayıyor (%4,1 sapma).
Donmuş TEST **0,5804** (n=40) — **DOKUNMA**, tek hakemli kalır
Ağırlık `sha256 755e15e9…` değişmiyor; depo adı `HakHukuk-4B-v0.3-Q4_K_M` **aynı kalır**
İndeks deposu: `Rfetha/HakHukuk-mevzuat-bge-m3-s2` (dataset, **baştan public**)

## Kurallar
- **Üretim yeniden koşulmaz** — aynı cevaplar, yalnız hakem (ADR-0017).
- Hakem çağrısı **bir kez**; `harness_tablo.py` aynı jsonl'den **iki kez**, çıktı bayt-bayt
  aynı olmalı (kusur 23, $0). Ayrışırsa sayı yayımlanmaz.
- Manşet **koşulsuz ARALIK**: *"%69,4-80,1 (sonnet-5 ↔ gpt-4o-mini)"* — geçse de düşse de.
  Dört yer: `CLAUDE.md` · `MODEL_CARD.md` · iki `README`. Üç rakip kolu tek hakemli kalır.
- Kapı geçerse `v1.0`, `DÜŞTÜ`/`BELİRSİZ` ise `v0.4` — HF **her hâlükârda açılır**.
- Kusur 25: tüm paydalar `DOGRULANDI`; yalnız Sonnet-5 hücresi yeniden ifade edilir.
- Künye alanları **koşan süreçten** okunur (`/proc/<pid>/cmdline`) — sabit dize kanıt değil.
- Gözle okuma bir kapıdır — bu turda **dokuz** ölçülmüş bulgu çıkardı.
- Her bulgu anında `research_log` (#68) + ADR (**0084**). Türkçe yaz.
- `scripts/` değişirse `tests/conftest.py` **birlikte** değişir.

## YAPILMAZ
korpus büyütme (kendi turu) · model eğitimi · üçüncü hakem ailesi · donmuş TESTi 2. hakemle
puanlama · kusur 5a/27 (→v2) · `api.py` `HOST` · indeksi yeniden kurmak · artefaktı değiştirmek.

Kapanışta açık kalan **her** kusur **adıyla** devredilir, yoksa kapanış geçersizdir.
