# TODO — bugün koşulabilir olanlar

> Her satır bir [`ROADMAP.md`](ROADMAP.md) adımına bağlıdır. Bir satırın burada olması için
> **bugün koşulabilir** olması gerekir: bekleyen bir karara ya da bitmemiş bir işe bağlıysa
> buraya değil, ROADMAP'e yazılır.
> Kutucuk yalnız `verify:` çıktısı **gerçekten alındıktan sonra** işaretlenir.

## Şimdi — Faz 4, LİNEER SIRA → `v1.0` RELEASE

- [x] **1 · `KUNYE` taşınabilirlik** **2026-09-09** — yol artık indeks dizinine göreli,
      `mtime` vekili yerine **içerik hash'i**; künye `onek` sözleşmesini de taşıyor.
      `verify:` kopyalanmış ağaçtan yüklendi, `recall@10` **0,9500** (76/80) · **$0**
      → plan `hp-hat-a-hat-b` Görev 8 Adım 1b *(2026-09-12'de kapandı ve silindi)* ·
      [#65](docs/record/kronoloji-63-71.md#65)
- [ ] **2 · TUI gözle doğrulama** — `python -m hakhukuk.tui`, üç soru, gözle gör ·
      **$0** (GPU) → [ROADMAP · Faz 4](ROADMAP.md)
- [x] **3 · Sonnet-5 öznesi** **2026-09-09** — **Sonnet-5 ÖNDE**: kütle **0,8348** ↔
      bizim **0,8011** (GÖZ-katı). Sınav eşit (`recall@10` 0,9500 birebir). Kapı
      **etkilenmedi**, çıpa `3.5 Flash` kaldı (ADR-0072 m.2). Bedel **$1,1932**
      *(tahmin $0,82 idi)* → [OZET](outputs/eval/hp-rakip-havuzu/OZET.md)
- [x] **4 · Kabul testi** **2026-09-09** — donmuş TEST insan onayıyla **tek kez** açıldı.
      Ham kütle **0,5804** (tavan 0,7500) ↔ DEV 0,8011 (tavan 0,9500); uydurma madde **0/52**
      korundu. **`v1.0` VERİLMEDİ → `v0.3`** ([ADR-0077](docs/adr/kararlar-0064-0085.md#adr-0077)):
      engel model değil, **tek hakem ailesi** (κ 0,534 < 0,6) · **$0,0195**
      → [OZET](outputs/eval/g16-kabul-testi/OZET.md)
- [ ] **5 · Araç katmanı** — 5 deterministik kaldıraç (`ara` · `madde_getir` ·
      `madde_var_mi` · `kanun_bul` · `yururlukte_mi`) + **sınırlı** döngü + yeni durum
      `ARAMA_TUKENDI`. KAPI'lar tool değildir, döngü dışında koşulsuz çalışır ·
      **$0** → [ADR-0076](docs/adr/kararlar-0064-0085.md#adr-0076)
- [ ] **6 · Modeli YAYINLA** — ağırlıklar bugün **hiçbir yerde yayında değil**;
      HF model reposu + kart + üç belgede indirme yolu · **$0** → [ROADMAP · Faz 4](ROADMAP.md)

## Sırada — `v2` *(plan henüz yazılmadı)*

- [ ] `v2` spec + planı: **`tgta_v1` üstüne GRPO + düşünce ayarı**
      → [ADR-0075](docs/adr/kararlar-0064-0085.md#adr-0075) · [ROADMAP · v2](ROADMAP.md)
- [ ] **Ön koşul:** ödül fonksiyonu + hedef bant + **durma kuralı** tur başlamadan
      ön-kayıtlanır (ADR-0050). Korunacak taban: uydurulmuş madde **0/114** ·
      aşırı-red **4/80** · kütle **0,8011**

## Ucuz ve bağımsız — herhangi bir sırada

- [ ] `recall_taban.json` yazılsın — Faz 0'ın tek *"kaynaklanmadı"* ihlali · **$0**, ~15 dk
- [ ] `models/` ~20 GB temizliği (T1) — S7 kapandı (yalnız merge GGUF yayımlanır) · **$0**
- [ ] **Korpus bütünlüğü:** `4857/Madde 111` **yineleniyor** ve iki kopyanın `mulga` alanı
      **çelişiyor** (biri `True`, biri `False`) — ölçüldü 2026-09-07 · **$0**
- [ ] `terazi` 1. soruda **aynı atfı iki kez** üretiyor; yinelenen atıf kullanıcıya iki
      uyarı gösterir · **$0**

## Bekliyor — bugün koşulamaz, sebebi yazılı

| iş | neyi bekliyor |
| :--- | :--- |
| **Görev 8** · indeks dağıtımı (HF dataset) | mevzuat kapsam planı — bugünkü 79 MB'ı paketlemek boşa iş (8,4× büyüyecek) |
| **Görev 11 Adım 2** · temiz makine kapısı | Görev 8 — indeks git'te yok, `git clone` çalışan ürün vermiyor |
| Üçüncü **hakem** ailesi · rakip kolunun ikinci hakemle puanlanması | bütçe — tahmini fatura $2,81 ([ADR-0074](docs/adr/kararlar-0064-0085.md#adr-0074)) |
| **B1 · B4 eğitim turları** | **atlandı, ertelenmedi** — `v1` SFT ile kapanıyor ([ADR-0075](docs/adr/kararlar-0064-0085.md#adr-0075)); `B4` `v2`'de **konusuz** kalıyor |
| Sorumluluk ibaresinin nihai metni | hukukçu görüşü (**S10**) |
