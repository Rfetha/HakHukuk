# G22 · Kusur 22 — rakip kolları YAYIMLANAN BORU HATTIYLA yeniden puanlandı

**Tarih:** 2026-09-11 · **Bedel:** $0 (hakem çağrılmadı · GPU kullanılmadı · ağa çıkılmadı ·
model çağrılmadı) · **Onarım commit'i:** `0031976` (*"Kusur 18 ONARILDI"*)

**İnsan kararı 2026-09-11:** *"Sonuç aleyhimize çıksa bile yazılır: bugün tabloda iki farklı
aletin sayısı yan yana duruyor ve bu ADR-0057'nin eşit sınav kuralını ihlal ediyor."*

**HÜKÜM (özet):** Rakip kolları onarılmış aletle yeniden puanlandı. **Dört kolun üçü oynamadı.**
Tek değişen `gemini-3.1-flash-lite`: **1/152 → 0/153**. Değişim **aleyhimizedir** — bugüne kadar
önde olduğumuz tek deterministik eksende rakiplerden biri bizimle **eşitlendi** (`0`).
Bizim kolumuz **birebir aynı** kaldı (`0/114`), yani eşit sınav artık **sağlanmıştır**.

---

## 1 · Yayımlanan sayıyı üreten boru hattı — tahmin değil, okundu

| soru | cevap |
| :--- | :--- |
| hangi betik | **`scripts/puanlama/harness_tablo.py`** (`--details <h1_*_detail.jsonl> [--gnd …]`) |
| atıf hükmü nereden | `scripts/erisim_korpus/atif_dogrula.py` → `Dogrulayici(korpus).cevabi_dogrula(kayit["cevap"])` |
| korpus | `data/corpus/mevzuat_maddeler.jsonl` (betiğin varsayılanı; kollarda **aynı**) |
| sayaç | `atif_dagilimi = {DOGRULANDI, MADDE_YOK, KANUN_YOK, AYRISTIRILAMADI, MULGA}` — **her bir atıf** birer kez sayılır |
| yayımlanan JSON | `outputs/eval/f04-rakip-onsozsuz/harness_tablo_*.json` · `outputs/eval/hp-rakip-havuzu/harness_tablo_sonnet_5_nb.json` · `outputs/eval/f02-biz-onsozsuz/harness_tablo.json` |

### `MODEL_CARD` satırının **birimi** (kritik)

`MODEL_CARD.md` satır 144'teki `x/y` gösterimi `atif_dagilimi`'nden **iki ayrı alanla** kuruluyor.
Kaynak, `outputs/eval/f04-rakip-onsozsuz/KALIBRASYON_ve_OZET.md` satır 64-65'te **iki AYRI satır**
olarak duruyor ve `MODEL_CARD`'da tek kesire sıkıştırılmış:

```
pay   ("uydurulmuş madde")  = MADDE_YOK + KANUN_YOK
payda ("doğrulanan atıf")   = DOGRULANDI            ← TOPLAM ATIF DEĞİL
```

Doğrulaması (yayımlanan JSON'lardan):

| kol | DOGRULANDI | MADDE_YOK | KANUN_YOK | AYRISTIRILAMADI | toplam atıf | yayımlanan gösterim |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| BİZ | 114 | 0 | 0 | 0 | 114 | **0/114** |
| 3.1 FL | 152 | 1 | 0 | 1 | **154** | **1/152** |
| 3.5 FL | 130 | 3 | 1 | 0 | **134** | **4/130** |
| 3.5 Flash | 133 | 4 | 0 | 0 | **137** | **4/133** |
| Sonnet-5 | 161 | 2 | 0 | 0 | **163** | **2/163** ⚠️ |

⚠️ **Tabloda İKİNCİ bir birim tutarsızlığı var ve bu iş onu ortaya çıkardı.** Sonnet-5 hücresi
(`docs/HF_KARTI.md` satır 143 · `outputs/eval/hp-rakip-havuzu/OZET.md` satır 74) paydayı
**TOPLAM ATIF** (163) alıyor; Gemini sütunları ise **DOGRULANDI** (152/130/133) alıyor. Bu iki
hücre **aynı kesir değildir**. Sonnet'in sayısı bu turda **oynamadığı** için hüküm etkilenmedi,
ama birim farkı **kayda geçirilir** — düzeltmesi `MODEL_CARD`/`HF_KARTI` sahibinindir.

## 2 · Ön sondanın paydası NİÇİN tutmadı — sebep bulundu

Şerhte yazan sonda `154 ↔ 152` ve `134 ↔ 130` veriyordu. Sebep **iki ayrı birim hatasıdır**:

1. **Payda.** Sonda `atif_dogrula.py`'yi **CLI olarak** koşturmuş olmalı; o CLI `n_atif` alanında
   **toplam atfı** basar (`toplam = sum(sayac.values())` — `atif_dogrula.py` `main()`).
   Yayımlanan tablonun paydası ise **yalnız `DOGRULANDI`**. Fark tam olarak
   `AYRISTIRILAMADI + MADDE_YOK + KANUN_YOK` kadardır: 3.1 FL'de `152 + 1 + 1 = 154`,
   3.5 FL'de `130 + 3 + 1 = 134`. **Sondanın paydası yanlış değil, BAŞKA bir büyüklük.**
2. **Pay.** Sondanın *"3.5 Flash-Lite 4 → 3"* okuması **yeniden üretilemedi** ve bu turda
   **çürütüldü**: 3.5 FL'de onarım **hiçbir atfın hükmünü değiştirmedi** (aşağıda §4).
   `4 → 3` düşüşü, **eski payın** `MADDE_YOK + KANUN_YOK = 3 + 1 = 4` iken **yeni payın**
   yalnız `MADDE_YOK = 3` okunmasından doğan bir **birim kaymasıdır** — onarımın etkisi değil.
   ⇒ Sondanın *"aleyhimize oynadı"* okuması **3.1 FL için doğru, 3.5 FL için YANLIŞTI**.

## 3 · Kalibrasyon — kapı GEÇİLDİ

Aynı boru hattı önce **bizim** kolumuzda koşuldu. Yeniden üretilen JSON, yayımlanan
`outputs/eval/f02-biz-onsozsuz/harness_tablo.json` ile **alan alan BİREBİR AYNI** (`diff` boş):

```
$ python scripts/puanlama/harness_tablo.py \
    --details outputs/eval/f02-biz-onsozsuz/h1_tgta_v1_f02_nb_detail.jsonl \
    --gnd     outputs/eval/f02-biz-onsozsuz/gnd_h1_tgta_v1_f02_nb.jsonl \
    --out     outputs/eval/g22-rakip-yeniden-puanlama/ham/biz_kosu1.json
⇒ atif_dagilimi = {"DOGRULANDI": 114, "MADDE_YOK": 0, "KANUN_YOK": 0,
                   "AYRISTIRILAMADI": 0, "MULGA": 0}      ⇒ 0/114  BİREBİR
⇒ kütle 0,8011 · coverage 0,9375 · A1 0,8545 · recall@10 0,9500 — hepsi birebir
```

**Kapı geçti ⇒ rakiplere geçilebilir.**

## 4 · Dört kolun ÖNCESİ ↔ SONRASI

Bütün sayılar `outputs/eval/g22-rakip-yeniden-puanlama/ham/<kol>_kosu1.json` dosyasından;
"öncesi" sütunu yayımlanan JSON'lardan.

| kol | kaynak (yayımlanan) | `MADDE_YOK` önce→sonra | `KANUN_YOK` önce→sonra | `DOGRULANDI` önce→sonra | `MODEL_CARD` gösterimi önce→sonra |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **BİZ** `tgta_v1` | `f02-biz-onsozsuz/harness_tablo.json` | 0 → **0** | 0 → **0** | 114 → **114** | **0/114 → 0/114** (değişmedi) |
| `gemini-3.1-flash-lite` | `f04-rakip-onsozsuz/harness_tablo_3_1_flash_lite_nb.json` | **1 → 0** | 0 → 0 | **152 → 153** | **1/152 → 0/153** ⬅ **tek değişen** |
| `gemini-3.5-flash-lite` | `f04-rakip-onsozsuz/harness_tablo_3_5_flash_lite_nb.json` | 3 → **3** | 1 → **1** | 130 → **130** | **4/130 → 4/130** (değişmedi) |
| `gemini-3.5-flash` | `f04-rakip-onsozsuz/harness_tablo_3_5_flash_nb.json` | 4 → **4** | 0 → **0** | 133 → **133** | **4/133 → 4/133** (değişmedi) |
| `claude-sonnet-5` | `hp-rakip-havuzu/harness_tablo_sonnet_5_nb.json` | 2 → **2** | 0 → **0** | 161 → **161** | **2/163 → 2/163** (değişmedi) |

Bizim kol dahil beş kolun **tamamının** `harness_tablo` çıktısı yayımlananla **alan alan
birebir**; tek istisna 3.1 FL'nin `atif_dagilimi` + `kapi` blokları.

**Yan etki — YAYIMLANMAMIŞ bir alan da oynadı, kayda geçirilir:** 3.1 FL'de katı red kapısı
`gecen 78 → 79` · `reddedilen 2 → 1` · `kapi_sonrasi_coverage 0,8625 → 0,8750`. Bu alanlar
`MODEL_CARD`/`HF_KARTI`'nda **yayımlanmamıştır**, dolayısıyla düzeltilecek bir manşet yok;
ama `harness_tablo_3_1_flash_lite_nb.json` dosyasının kendisi artık eski aletin sayısını taşıyor.

## 5 · Hükmü DEĞİŞEN atıflar — tamamı GÖZLE OKUNDU

702 atfın (beş kol) **1'inin** hükmü değişti. Biri de gözden kaçmasın diye eski ve yeni alet
atıf-atıf karşılaştırıldı (`ham/atif_hukumleri_ESKI_ALET.json` ↔ `ham/atif_hukumleri_YENI_ALET.json`;
702 ↔ 702, atıf sırası birebir).

| # | kol | soru id | atıf metni | ESKİ `kanun_no` + ad | ESKİ hüküm | YENİ `kanun_no` + ad | YENİ hüküm |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | `gemini-3.1-flash-lite` | **25** | `GELİR VERGİSİ KANUNU, Madde 73` | `1319` **EMLAK VERGİSİ KANUNU** | `MADDE_YOK` (= uydurma damgası) | `193` **GELİR VERGİSİ KANUNU (G.V.K.)** | `DOGRULANDI` |

### Gözle okuma — kapı

**Soru (id 25):** *"Kira bedelini nasıl belirliyoruz?"* · altın madde `6098 / MADDE 344`.

Modelin yazdığı cümle:

> *"**Vergi Hukuku Açısından Emsal Kira Bedeli:** Kiraya verilen mal ve hakların kira bedelleri
> emsal kira bedelinden düşük olamaz. Emsal kira bedeli; yetkili özel mercilerce veya
> mahkemelerce takdir veya tespit edilmiş kira bedelidir. Böyle bir tespit yoksa, bina ve
> arazilerde emsal kira bedeli, Vergi Usul Kanunu'na göre belirlenen vergi değerinin %5'idir
> (GELİR VERGİSİ KANUNU, Madde 73)."*

Korpustaki `193 / Madde 73` (`mulga = False`):

> *"Kiraya verilen mal ve hakların kira bedelleri emsal kira bedelinden düşük olamaz. … Bina ve
> arazide emsal kira bedeli, yetkili özel mercilerce veya mahkemelerce takdir veya tespit edilmiş
> kirası, bu suretle takdir veya tespit edilmiş kira mevcut değilse Vergi Usul Kanununa göre
> belirlenen vergi değerinin % 5'idir…"*

**Hüküm: YENİ hüküm DOĞRU.** Madde korpusta **var**, **yürürlükte** ve modelin yazdığı içerikle
**birebir örtüşüyor**. Eski alet, *"Gelir Vergisi Kanunu"* adını çift gevşemeyle
`VERGİSİ KANUNU` sonekine düşürüp **1319 Emlak Vergisi Kanunu**'na çözüyor, orada 73. madde
bulunmayınca **`MADDE_YOK` = uydurma** damgası basıyordu. Bu, `yurutme-tuzaklari` **1.13**'ün
kanonik örneğidir ve damganın **rakip aleyhine yanlış** basıldığı hâlidir.

⛔ **Bu tek değişiklik bizim aleyhimizedir ve yazılır.**

## 6 · İki koşunun aynılığı (kusur 23'ün dersi)

Her kol **iki kez** koşuldu, çıktılar **bayt bayt** karşılaştırıldı (`cmp`):

| kol | `kosu1` sha256 | `kosu2` sha256 | sonuç |
| :--- | :--- | :--- | :--- |
| BİZ | `c2e71d74…b1994f9b481c5d` | `c2e71d74…b1994f9b481c5d` | **BİREBİR AYNI** |
| 3.1 FL | `f8527877…c60383c92afa` | `f8527877…c60383c92afa` | **BİREBİR AYNI** |
| 3.5 FL | `777c2a12…95ab50656b47` | `777c2a12…95ab50656b47` | **BİREBİR AYNI** |
| 3.5 Flash | `1a55fbcd…7a4fff6dffe1f9e`* | `1a55fbcd…7a4fff6dffe1f9e`* | **BİREBİR AYNI** |
| Sonnet-5 | `efeeecc3…851cd3c17f3d4` | `efeeecc3…851cd3c17f3d4` | **BİREBİR AYNI** |

\* tam sha256'lar `KUNYE.json`'da. Boru hattı bu girdilerde **deterministik**; kusur 23'ün
*"bir kez eski sayıyı verdi ve tekrarlanamadı"* olayı burada **görülmedi**.

## 7 · Kurulmayan cümleler

1. **"Rakipler onarımdan sonra da bizden kötü."** 3.1 FL artık bizimle **eşit** (`0`).
2. **"Onarım rakipleri genel olarak akladı."** 702 atfın **1'i** değişti; 3.5 FL · 3.5 Flash ·
   Sonnet-5 **hiç oynamadı**. Onarımın etkisi **dar ve ölçülmüştür**.
3. **"Bu, kütleyi/A1'i/isabetsizliği değiştirir."** Değiştirmez — onarım yalnız `atif_dagilimi`
   ve ondan türeyen **red kapısı** alanlarına dokunur; hakem eksenleri (`A1`, kütle) bu turda
   **yeniden hesaplanmadı, yalnız yayımlananla birebir doğrulandı**.
4. **"Sonnet-5 hücresi doğrulandı."** Sayısı oynamadı, ama **paydası diğer sütunlarla aynı birimde
   değil** (§1 ⚠️) — bu ayrı bir kusurdur ve bu iş onu kapatmaz.

## 8 · HÜKÜM

`MODEL_CARD.md` satır 144'teki **`0/114` · `1/152` · `4/130` · `4/133`** dizisi
**`0/114` · `0/153` · `4/130` · `4/133`** ile değişmelidir; `docs/HF_KARTI.md` satır 143'teki
Sonnet-5 hücresi **`2/163` olarak kalır** (ama birimi diğerlerinden farklıdır, §1). Değişim
**aleyhimizedir**: *"uydurulmuş madde"* bugüne kadar rakiplerin tamamının üstünde olduğumuz tek
deterministik eksendi ve `gemini-3.1-flash-lite` artık bu eksende bizimle **eşittir** (`0` ↔ `0`);
üstelik payda lehine büyüdü (`152 → 153`). Buna karşılık **eşit sınav artık sağlanmıştır**
(ADR-0057): tablodaki beş sütunun beşi de **aynı, onarılmış aletin** sayısıdır, ve *"bizimki
onarılmış aletle, rakipler onarılmamış aletle"* şerhi **kaldırılabilir**. İkincil olarak
şerhteki *"3.5 Flash-Lite 4 → 3"* iddiası **çürütülmüştür** — o kol hiç oynamadı; düşüş sondanın
**birim kaymasıydı** (§2).
