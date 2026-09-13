# ROADMAP — ne, neden, hangi ölçülmüş boşluk

> **Yön belgesi.** Her adım bir **ölçülmüş boşluğa** bağlıdır; hiçbir satır *"iyi olurdu"*
> gerekçesiyle burada değil. Kutucuklu iş listesi için: [`TODO.md`](TODO.md).
> Bu yönü yürüten tur (`hp` → Hat A → Hat B) 2026-09-12'de **115/115** kapandı ve planı silindi;
> kusur sicili ile devir tablosu [ADR-0083](docs/adr/kararlar-0064-0085.md#adr-0083)'te.
> Sıradaki iş ve sırası: [`docs/superpowers/00-IS-SIRASI.md`](docs/superpowers/00-IS-SIRASI.md)
> — **`v1-son-iş`**, planı **henüz yazılmadı**.

## Kritik yol

```
BİTTİ     Faz 0  ölçüm zinciri onarıldı          48/48 · $1,47
BİTTİ     Faz 1  hakem paneli (İKİ aile)         $3,155 · üçüncü aile ATLANDI (bütçe)
BİTTİ     Faz 2  Hat A — ürün paketleme          $0 · hakhukuk/ paketi, CLI + TUI
BİTTİ     Faz 3  belge katmanı                   $0 ──────────────►  sürüm v0.2
BİTTİ     Faz 4  v1.0 kapısı + YAYIN             ~$1 ─────────────►  sürüm v0.3
                                                 (v1.0 VERİLMEDİ — ADR-0077)
BEKLİYOR         mevzuat kapsam + tazelik        korpus 40.496 → ~340.303 · ayrı plan
BEKLİYOR  v2     tgta_v1 üstüne GRPO + düşünce RL ADR-0075 · plan yazılmadı
```

## `v1` ↔ `v2` — mimari çizgi *(ADR-0075, insan kararı 2026-09-08)*

```
v1   ham base ──► SFT (τ_g) + ORPO (τ_a) ──► ham TIES ──► tgta_v1 ──► YAYIN
v2   tgta_v1 (bf16, 8,8 GB) ──► GRPO + düşünce ayarı ──► v2.0
```

**`v1` SFT ile KAPANIR.** Eğitim turları (`B1` · `B4`) **koşulmaz** — gerekçe aşağıda, Faz 4'te.
**`v2` sequential RL'dir**, task vector değil: `tgta_v1`'i yeni başlangıç almak
`τ = θ_ft − θ_base` tanımını bozar ⇒ **ADR-0027'nin merge hattı `v1`'de DONDURULUR** ve
`v2`'ye taşınmaz. `v2`'nin iddiası merge değil, **RL kazancıdır**.

---

## Faz 0 — ölçüm zinciri *(kapandı 2026-09-07)*

**Ölçülmüş boşluk:** yayımlanan sayılar *"hata vermeden yanlış"* sınıfından **beş kusur**
taşıyordu. **Sonuç:** kütle %68,4 → **%80,1**, ağırlıklar hiç değişmeden.
`verify:` [ADR-0064](docs/adr/) · [#62](docs/record/kronoloji-53-62.md#62)

## Faz 1 — hakem paneli *(kapandı 2026-09-07)*

**Ölçülmüş boşluk:** her sayı `gpt-4o-mini`'nin **tek başına** hükmüydü; κ yok, öz-tercih
ölçülmemiş (ADR-0064 *"Ne KURULMAZ"* m.2).
**Sonuç:** κ **eşiğin altında** (0,534 · 0,409), kayma **tek yönlü**, manşet hakem seçimine
duyarlı (0,8011 ↔ 0,6940). Bağlayıcı hakem `gpt-4o-mini` **kaldı** — eşit sınav gereği.
**Bedel:** $3,155 gerçek fatura ($1,977 raporlanan · kapı marjı **1,6×**).
**Kapanmayan:** üçüncü aile (Google) ve rakip kolunun ikinci hakemle puanlanması —
insan kararı, bakiye $3,45.
`verify:` [ADR-0074](docs/adr/kararlar-0064-0085.md#adr-0074) · [#64](docs/record/kronoloji-63-71.md#64) · [`KAPPA.md`](outputs/eval/hp-hakem-paneli/KAPPA.md)

## Faz 2 — Hat A, ürün paketleme *(kapandı 2026-09-07, $0)*

**Ölçülmüş boşluk (2026-09-07):** servis katmanı **kod olarak yoktu**
(`grep -rlE "fastapi|uvicorn|flask|gradio" scripts/` → 0); modeli indiren kişi yayımlanan
sayıyı **üretemiyordu**; istem **beş dosyada** kopyalıydı ve biri **sürüklenmişti**.

| ne | neden | verify |
| :--- | :--- | :--- |
| `hakhukuk/istem.py` | istem 5 kopya, biri sürüklenmiş (S18) | `grep -rc "Sen HakHukuk'sun" scripts/` → **0** · sapma 0/10 |
| `hakhukuk/tipler.py` | `bool` üç durumu kaybediyordu | 4 durumlu enum, donmuş dataclass |
| `hakhukuk/terazi.py` | dedektör **üç kez** fazla-red saydı | 80 kalem: suskunluk **[15,37,45,66,79]** = gözle okunan kümeyle birebir |
| `hakhukuk/servis.py` | tek derin modül; boş getirmede model **çağrılmaz** | uçtan uca 3 soru: durum CEVAP/ÇEKİNCELİ, uydurma doğrulama **0** |
| `hakhukuk/cli.py` · `tui.py` | ürün yüzü; ibare **tek kaynakta** | 140 test yeşil |
| yürürlük süzgeci | 800 kaynağın **2'si mülgaydı** | sızıntı **2 → 0**, `recall@10` **0,9500** değişmedi |
| `scripts/yeniden_uret.sh` | manşeti **kimse** yeniden üretemiyordu | `bash -n` temiz · iki geçerlilik kapısı gömülü |

## Faz 3 — belge katmanı *($0)* → `v0.2`

**Ölçülmüş boşluk:** `PRODUCT.md` · `ROADMAP.md` · `TODO.md` · `docs/MIMARI.md` **yoktu**
(2026-09-06'da silinen doküman katmanının yerine hiçbir şey konmamıştı).
`verify:` dört belge var · kırık link kalmadı · `docs/record/**` ve `docs/adr/**`
**değişmedi** (`git diff --stat` → 0).

## Mevzuat kapsam + tazelik *(ayrı plan, 62 kutucuk)*

**Ölçülmüş boşluk:** korpus **892 kanun · 40.496 madde** — yönetmelik/tüzük/KHK **yok**; ve
korpusta **tek bir tarih alanı bile yoktu** (2026-09-07'de eklendi: `data/corpus/KUNYE.json`).
**Hedef:** ~**340.303** madde (**8,4×**), indeks 83 MB → **~697 MB**.
**Bağımlılık:** ana planın **Görev 8'i (indeks dağıtımı) bunu bekliyor** — bugünkü 79 MB'ı
paketlemek, birkaç hafta sonra atılacak bir iştir.
`verify:` planı `2026-09-08-mevzuat-kapsam-ve-tazelik` yazılmıştı, 2026-09-12'de **silindi**;
mimari özü ve **DÜZELTİLMİŞ kat merdiveni** [ADR-0083](docs/adr/kararlar-0064-0085.md#adr-0083) §EK'te.
⚠️ Yukarıdaki **340.303** hedefi **yanlıştır** — `KANUN` satırı `917 × 102,7` sayıyordu; korpustan
ölçülen gerçek oran **45,4 madde/belge** ve düzeltilmiş hedef **~287,6-287,8 bin**.

## Faz 4 — `v1.0` kapısı + **YAYIN** *(~$1)* → `v1.0` RELEASE

| sıra | ne | neden (ölçülmüş boşluk) | bedel |
| :--- | :--- | :--- | ---: |
| ~~1~~ | `KUNYE` taşınabilirlik | ~~`git clone` sonrası **her makinede** `SystemExit`~~ — **kapandı 2026-09-09**: yol göreli, `mtime` → içerik hash'i; `recall@10` **0,9500** | $0 |
| 2 | TUI gözle doğrulama | ürün yüzü **insan gözüyle hiç görülmedi** | $0 |
| ~~3~~ | **Sonnet-5 öznesi** | ~~frontier sınıfı hiç ölçülmedi~~ — **ölçüldü 2026-09-09: Sonnet-5 ÖNDE** (kütle 0,8348 ↔ 0,8011). Kapı etkilenmez | $1,1932 |
| ~~4~~ | **Kabul testi** *(ARAÇSIZ)* | ~~donmuş TEST hiç açılmadı~~ — **açıldı 2026-09-09**: ham kütle **0,5804** (tavan 0,7500). `v1.0` **verilmedi → `v0.3`**; engel **hakem paneli**, model değil (ADR-0077) | $0,0195 |
| 5 | **Araç katmanı** | model arayıp aramayacağına **karar vermiyor**; isabetsizlik 8/80'in bir kısmı iki maddeyi yan yana okuyamamaktan | $0 |
| 6 | **Modeli YAYINLA** | ağırlıklar **hiçbir yerde yayında değil** — *"açık kaynak model"* iddiası bugün **yarım** | $0 |

### Araç katmanı — KAPI ↔ KALDIRAÇ *([ADR-0076](docs/adr/kararlar-0064-0085.md#adr-0076))*

| sınıf | ne | kim karar verir |
| :--- | :--- | :--- |
| **KAPI** | atıf doğrulama · mülga süzgeci · durum sınıflandırma · kesiklik | **hiç kimse** — koşulsuz |
| **KALDIRAÇ** | `ara` · `madde_getir` · `madde_var_mi` · `kanun_bul` · `yururlukte_mi` | **model** |

`madde_var_mi` en değerlisi: bugün madde numarası ezberden yazılıyor ve hata ancak
**cevaptan sonra** kapıda anlaşılıyor — yakalanıyor ama **düzeltilmiyor**. Bu araçla model
**yazmadan önce** kendini denetler ⇒ atlanan `B1` turunun hedefine ikinci yoldan saldırır.

**Döngü sınırlı, sınıra dayanmak görünür:** `Durum.ARAMA_TUKENDI`. Sessiz tükenme, bu
hattın en pahalı hata sınıfını (*"hata vermeden yanlış"*, 17 tuzağın hepsi) büyütürdü.
**Kapı koşusuna girmez** — %80,1 ve eşik araçsız ölçüldü, rakipler araç kullanamaz
(ADR-0057 eşit sınav). Sıra: **kabul testi → araç katmanı → yayın.**

### `B1` ve `B4` eğitim turları ATLANDI — [ADR-0075](docs/adr/kararlar-0064-0085.md#adr-0075)

| tur | neden koşulmadı |
| :--- | :--- |
| **B1** isabetsizlik | Hedef eksende **geride değiliz**: biz **8/80** ↔ rakipler **8 · 8 · 7 · 8**. Ve otomatik vekil metrik **yok** (süzgeçler 4 ve 3, **göz 8**) ⇒ her tur **80 kalem gözle okuma** = insan saati |
| **B4** `τ_a` genliği | Bu bir **merge** kaybı, eğitim sorunu değil (`τ_a` tek başına **0,987**). `v2` sequential ⇒ **merge yok** ⇒ aynı **22,1 puan** ödenmeden geri gelir |

**İkisi de borç olarak AÇIK kalır** — koşulmadıkları için ne verecekleri **bilinmiyor**.
Bu bir **öncelik** kararıdır, ölçüm sonucu değil.

Kabul testinin erişim tavanı **≈0,75** (DEV 0,95 değil) — ADR-0069'un raporlaması **zorunlu**.
Donmuş TEST **tek kez** açılır.

## `v2` — model katmanı **RL** + uygulama katmanı

**Model tarafı (ADR-0075):** `tgta_v1` yeni başlangıç → **GRPO + düşünce (thinking) ayarı**.
Mümkün olmasının sebebi: **doğrulanabilir ödül hazır** — `hakhukuk/terazi.py` atıf
doğrulamasını **deterministik** yapıyor, reward model gerekmiyor, hakem bedeli yok.

**Ödül fonksiyonu çekinmeyi korumak ZORUNDA** (ADR-0075 m.4): ADR-0010 ölçtü, düz SFT
abstention'ı yok etti; RL'de risk daha keskindir çünkü model ödülü maksimize etmeyi öğrenir.
Korunacak taban: uydurulmuş madde **0/114** · aşırı-red **4/80** · kütle **0,8011**.

**Uygulama tarafı:** canlı `bedesten` API (**B6**, TR IP şart) · tam kapsam · tazelik boru
hattı · HTTP API + barındırma (**S9 açık**) · tablo/cetvel satırları (**B9**, ~7.966 satır).

---

## Açık kararlar

| # | soru | durum |
| :-- | :--- | :--- |
| **S9** | `v2` nasıl barındırılır? | açık — bu planın dışında |
| **S10** | sorumluluk ibaresinin **nihai hukuki metni** | açık — geçici metin yürürlükte, hukukçu görüşü bekliyor |
| **S12** | KARAR-6 paralel slot (`-np`) | ertelendi — `τ_a` v2 turuna |
| **S17** | kuantizasyon eğrisi ölçülsün mü? | açık — bu planın dışında |
| ~~S5·S7·S8·S16·S18~~ | — | kapandı 2026-09-07 |
