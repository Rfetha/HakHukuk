# ADR-0083 — Kapanan planın **kusur sicili** ADR'ye taşındı; `docs/superpowers/` boşaltıldı

**Tarih:** 2026-09-12
**Statü:** yürürlükte
**Karar:** **insan** (2026-09-12) — `hp-hat-a-hat-b` planı 115/115 kapandı ve kayda dönüştü;
`docs/superpowers/` **tek bir yeni plan** için boşaltılıyor. Planın gövdesi **silinir**;
plandan **bağımsız** iki kayıt — kusur sicili ve devir tablosu — bu ADR'ye taşınır.
**Bağlı:** [ADR-0062](0062-b10-turu-kapatildi-hedef-egitimsiz-karsilandi.md) (emsal: kapanan
plan **yeniden işletilmez**, kapanış bloğu ADR'de yaşar) ·
[ADR-0079](0079-zayif-eslesme-rozeti-eklenmedi.md) (kusur 5a'nın hükmü) ·
[ADR-0080](0080-urun-yolu-zorunlu-dusunce-kapatmasi.md) (kusur 1'in hükmü) ·
[ADR-0081](0081-altinci-durum-bos-sorgu.md) (kusur 16'nın hükmü) ·
[ADR-0078](0078-konteyner-dagitimi-rejim-kilidi.md) (madde 5: kusur 11 **kendi turunu** hak eder) ·
[ADR-0075](0075-v1-sft-kapanir-v2-sequential-rl.md) (kusur 6 → borç **B1**, kusur 12b → borç **B11**) ·
[ADR-0057](0057-harness-rekabet-kapisi-esit-sinav.md) (kusur 22'nin gerekçesi: **eşit sınav**) ·
[ADR-0050](0050-verim-kapisi-tahmin-edici-duzeltmesi.md) (kusur 18/22'nin kalıbı: **alet
düzeltilir, eşik oynatılmaz**; aynı cevaplara düzeltilmiş aleti uygulamak **yeni sınav değildir**) ·
[ADR-0077](0077-v1-0-verilmedi-v0-3.md) (`v0.3`; `v1.0` verilmedi)
**Kaynak:** silinen `docs/superpowers/plans/2026-09-07-hp-hat-a-hat-b.md` — `AÇIK KUSURLAR —
kayıt ve devir` bölümü (satır 1512-1886) ve `DEVİR — kapanış kuralının şartı` bloğu (satır 39-80).
Bu ADR o iki bölümün **taşınmış hâlidir**; plan gövdesinin geri kalanı taşınmadı.
**Kayıt:** [#64](../record/research_log/2026-09-07-hakem-paneli-iki-aile.md) ·
[#65](../record/research_log/2026-09-09-kabul-testi-ve-frontier-kiyasi.md) ·
[#66](../record/research_log/2026-09-11-urun-yuzeyi-ve-aygit-kusurlari.md) ·
[#67](../record/research_log/2026-09-12-konteyner-ve-alet-onarimlari.md) ·
kapanan görevlerin tam metni [`docs/record/2026-09-10-hp-hat-a-hat-b-kapanan-gorevler.md`](../record/2026-09-10-hp-hat-a-hat-b-kapanan-gorevler.md)

---

## Bağlam — niçin taşınıyor

`hp-hat-a-hat-b` planı **2026-09-12'de 115/115 kapandı**. Deponun kendi kuralı bağlayıcıdır:
*"kapanan plan yeniden işletilmez; kapandığı gün **kayda dönüşür**."* İnsan kararıyla
`docs/superpowers/` **tek bir yeni plan** için boşaltılıyor ve kapanan planın gövdesi siliniyor.

Planın içeriğinin **çoğu zaten başka yerde durur**: ölçümler ve kararlar ADR **0074-0082**'de,
anlatı kayıt **#64-#67**'de, 2026-09-10'da kapanan on dört görevin tam metni
`docs/record/2026-09-10-hp-hat-a-hat-b-kapanan-gorevler.md`'de. Silme bu üçünün hiçbirine
dokunmaz.

Yalnız **iki şey** o dosyadan başka hiçbir yerde yoktur:

1. **32 kusurun sicili** — hangi kusur ne zaman, hangi commit'le, hangi gerekçeyle kapandı.
2. **Devir tablosu** — kapanış anında açık kalan kusurların **adıyla** nereye gittiği.

Kusur sicili **plandan bağımsız** bir kayıttır: bir sonraki turun **girdisidir**, geçmiş bir
işin ilerleme çizelgesi değil. Bir plan dosyasının içinde durması tarihsel bir kazadır
(2026-09-10'da ayrı bir `post-hp-hat-b-tickets.md` dosyasından **oraya taşınmıştı**). Bu yüzden
silme öncesinde kurtarılan tek içerik budur.

---

## Karar

Kusur sicili ve devir tablosu **bu ADR'nin gövdesine** taşınır. Plan dosyası silinir. Devir
kuralı **aynen** yürürlükte kalır:

> **Kapanış anında açık kalan her kusur, adıyla bir sonraki plana devredilir; hiçbir yere
> devredilmemiş açık kusur varsa kapanış GEÇERSİZDİR.**

Sebebi değişmedi: plan kapandığı gün kayda dönüşür; devir kuralı olmazsa açık kusurlar
**kapalı bir kaydın içinde donar** — ki bu, silinen bakım kuralının önlemek için var olduğu
şeyin ta kendisidir.

---

## (A) 33 kusurun tam sicili

**Sayım (2026-09-12, bu ADR yazıldığı an):** 34 satır (`5a/5b` ve `12a/12b` ayrık sayılır) ⇒
**23 KAPANDI · 3 DEVREDİLDİ · 8 AÇIK**. Kusur **10**'un iki yarısı vardır ve yalnız biri
kapandı; satır **açık** sayılır. *(Bu ilk sayım kusur 33 doğmadan ÖNCEki hâldir — bkz. canlı
sayım.)*

> 🔄 **CANLI SAYIM — `v1-son-iş` turu KAPANDI 2026-09-13, 71/71:** **28 KAPANDI · 3 DEVREDİLDİ ·
> 4 AÇIK** (5a · 23 · 27 · 31).
> Turda kapananlar: **24** (`b077f13`) · **29** (adım 6.3.1) · **33** (`cc12b6e`, recall@10
> kapısı var olmayan alanı okuyup her zaman düşüyordu) · **25** (Adım 8, tüm paydalar
> `DOGRULANDI`'ya çevrildi, sayı oynamadı) · **10** (Adım 9, HF görünürlüğü **PUBLIC** —
> insan onayıyla açıldı, `sha256` token'sız bir alt süreçte doğrulandı).
> ⚠️ Kusur **24** bu sicilde 2026-09-12'ye kadar *"AÇIK"* göründü — kapanışı `00-IS-SIRASI`'ya
> işlenmiş, **buraya işlenmemişti**. Tutarlılık denetiminde yakalandı ve damgalandı.
> Ders: *kapanış **iki** yere birden yazılmazsa sicil sessizce bayatlar* — ve sicil bir sonraki
> turun **girdisidir**.
> **İkinci kez sınanan ama AÇIK kalan: 23** (adım 6.6, $0) — deterministik taraf (`harness_tablo.py`
> + `uc_okuma_kutle.py`, ikişer koşu) `sha256` **birebir**, üçüncü kez temiz; ama id65'te canlı
> bir "aynı girdi farklı sayı" örneği bulundu ve kökeni **kusur 23'ten AYRI** çıktı (hakem-katmanı
> `temp=0` gürültüsü, kod değil) — bkz. §Kusur 23. Sayaç **değişmedi**.

| # | kusur | durum | nerede kapandı / nereye devredildi |
| :-- | :--- | :--- | :--- |
| 1 | ürün yolunda 4/80 cevap **tamamen boş** dönüyor (sonlanmama) | **KAPANDI** 2026-09-11 | G22 Adım 4 + insan rejim onayı: **0/80**, kesik %8,75 → %3,75, ADR-0040 kapısı GEÇTİ ([ADR-0080](0080-urun-yolu-zorunlu-dusunce-kapatmasi.md)). Şerh: B10'a +2 kalem, ve kusur **20** doğdu |
| 2 | KV ayarının 80 kalemdeki etkisi ölçülmedi | **KAPANDI** 2026-09-11 | iki aşama. **Hakemsiz ($0):** %81 bayt değişimi, sayaçlar ±1 kalem. **Hakemli (insan bedel kapısı, $0,045067):** kütle **0,8011 → 0,7932**; fark gürültü tabanının 2,8 katı ama tek yönlü hükme yetmiyor. Tabanın açıkça üstündeki tek eksen `wrong_ref_rate` ve **2,0× kötüleşti** ⇒ **insan kararı: taşıyıcı rejim `q8_0` KALIR** |
| 3 | TUI soru sorulunca donuyor (`answer()` olay döngüsünü bloke ediyor) | **KAPANDI** 2026-09-11 | G21 Adım 6 — çağrı çalışan iş parçacığına alındı |
| 4 | boş sorgu reddedilmiyor, sabit bir gürültü kümesi dönüyor | **KAPANDI** 2026-09-11 | G21 Adım 3 — `servis.answer`'da **kapı**, döngü dışında |
| **5a** | zayıf eşleşme sinyali kullanıcıya verilmiyor | **AÇIK** | **ölçüldü, ayrışma YOK, rozet EKLENMEDİ** ([ADR-0079](0079-zayif-eslesme-rozeti-eklenmedi.md)): altı göstergenin hiçbiri ayırmıyor, en iyi adayda 4 kaçık için **23 yanlış alarm**. Ölçüm `outputs/eval/g21-zayif-eslesme/BULGU.md`. **Devir → `v2`** · yeni bir gösterge ya da daha büyük `n` gerektirir |
| 5b | kapsam bildirimi yok (kullanıcı korpusun sınırını bilmiyor) | **KAPANDI** 2026-09-11 | G21 Adım 7 — **statik** satır, sınıflandırıcı **YOK** (yanılan bir kapsam sınıflandırıcısı cevabı olan soruyu öldürür); sayılar `data/corpus/KUNYE.json`'dan okunuyor |
| **6** | `wrong_ref` frontier'ın **9,3×** gerisinde (0,0769 ↔ 0,0083) | **DEVREDİLDİ** | **`v2` · borç `B1`** ([ADR-0075](0075-v1-sft-kapanir-v2-sequential-rl.md)). ⚠️ **Bu turda AĞIRLAŞTI:** fp16 rejiminde `wrong_ref_rate` **2,0×** kötüleşiyor (`outputs/eval/g22-kv-fp16/KUTLE.md`) — `q8_0` kararının gerekçesi budur |
| 7 | duman koşusundan doğrusal maliyet tahmini kapı kurmuyor (0,82 $ tahmin ↔ 1,1932 $ gerçek) | **KAPANDI** 2026-09-11 | G21 Adım 9 — **kural yazıldı, kod değil**: tuzak **1.11** + Global kısıtlara bir cümle |
| 8 | arayüz açılışında yönlendirme yok (boş ekran) | **KAPANDI** 2026-09-11 | G21 Adım 7 |
| 9 | SIRA 2 (TUI göz) kapısı açık | **KAPANDI** | G12 Adım 6-7 — üç soruda rozet + atıf + kaynak + sorumluluk ibaresi **ekranda görüldü**, **insan teyit etti**. Kapı çalışırken bir ürün kusuru yakaladı (`python -m hakhukuk.tui` hiçbir şey yapmıyordu: `__main__` bloğu yoktu) |
| **10** | dağıtım kararları: commit'ler push edilmedi · HF deposu **özel** | ✅ **KAPANDI 2026-09-13** | **`push` KAPANDI 2026-09-12** — 62 commit `origin/master`'a gitti. **HF görünürlüğü KAPANDI 2026-09-13** (ADIM 9, insan onayı): depo `Rfetha/HakHukuk-4B-v0.3-Q4_K_M` **public** yapıldı (`repo_info(...).private` okunarak doğrulandı: `False`); token'sız bir alt süreçte dosya indirilip `sha256`'sı `755e15e9…86e7bffc` ile bayt bayt eşleşti (kusur 32'nin dersi: token'lı erişimle karıştırılmadı). Depo **adı** değişmedi (grill kararı 6) — sürümü kart anlatır. ⛔ **BU CÜMLE 2026-09-13'te GEÇERSİZ KALDI** ([ADR-0085](0085-tek-kart-ve-yeniden-adlandirma.md)): insan kararıyla depo `Rfetha/HakHukuk-4B-GGUF`'a taşındı ve GitHub deposu `Rfetha/HakHukuk` oldu. Grill kararı 6'nın **gerekçesi korundu** — değişen **depo** adıdır, **dosya** adı (`HakHukuk-4B-v0.3-Q4_K_M.gguf`) değişmedi. Ayrıca `docs/HF_KARTI.md` **silindi**: tek kart `MODEL_CARD.md`'dir, HF sürümü ondan üretilir |
| **11** | `hakhukuk` paketi tek başına kurulamıyor — `servis.py` çalışma anında `sys.path`'e `scripts/` ekliyor | **DEVREDİLDİ** | **kendi turu** ([ADR-0078](0078-konteyner-dagitimi-rejim-kilidi.md) m.5). Kusur **21**'in onarımı importu birden **ikiye** çıkardı; kalıcı çare `madde_anahtar` + `atif_dogrula` + `score_abstention` üçlüsünün **pakete taşınması**. Yapısal değişiklik: aynı dosyayı 26 dosyanın yol köprüsü ve tüm ölçüm hattı kullanıyor |
| 12a | eğitim verisinin `##begin_quote##` işaretleri **vatandaşa gidiyor** | **KAPANDI** 2026-09-11 | G21 Adım 4 — **yalnız sunum katmanında** süzülür. ⛔ Ölçüm hattına **girmedi**: `scripts/puanlama/score_register.py:41` aynı işareti bir **register göstergesi** sayıyor, orada süzmek o metriği sessizce değiştirirdi |
| **12b** | işaretlerin **kaynağı** eğitim verisidir (`gen_v2b_answers.py:36-37` öğretmene böyle söylüyor, `build_sft_v2b.py:57` bloğu koruyor) | **DEVREDİLDİ** | **`v2` · borç `B11`** — düzeltmesi **yeniden eğitimdir** |
| 13 | `Atif.madde_no` ile `Kaynak.madde_no` biçimi tutmuyor (`Madde 330` ↔ `MADDE 330`) | **KAPANDI** 2026-09-11 | G21 Adım 5 — türetilmiş alan, ham veri korundu. ⚠️ Alan sonradan **silindi** (kusur **14**, ölü koddu); **gösterim** tutarsızlığı ayrı kalır ⇒ kusur **27** |
| **14** | `madde_sayisi` **ölü alan**; asıl kıyas yeri zaten `madde_anahtari` kullanıyor | **KAPANDI** 2026-09-11 | **insan kararı: SİL** (ölü kod, YAGNI; bağlanacağı yer yok) — alan + yardımcı + 4 test silindi, üretimde sıfır çağrı `grep` ile doğrulandı. Commit `7d1af54` (yapısal) |
| **15** | kapsam satırı **yalnız TUI'de**; CLI ve HTTP göstermiyor | **KAPANDI** 2026-09-11 | **insan kararı: CLI ve HTTP'ye de EKLE** — `bicimle()`'ye kondu ⇒ **CLI · TUI · HTTP üçü birden**. Üç yüzeyde de **çalıştırılarak** görüldü. Commit `61162d0` |
| **16** | boş sorguda rozet *"kaynaklarda karşılık bulunamadı"* ↔ gövde *"soru boş"* — çelişik | **KAPANDI** 2026-09-11 | **tip düzeyi** değişiklik, ADR istedi: altıncı `Durum` = **`BOS_SORGU`**, beş yüzey güncellendi ([ADR-0081](0081-altinci-durum-bos-sorgu.md)). Commit `d79c01b` |
| **17** | `tui.py` `bicimle()`'yi çağırmıyor — **iki paralel sunum katmanı** | **KAPANDI** 2026-09-11 | Bu turdaki iki sızıntının (iskele işareti · kapsam satırı) **kök nedeni**. **insan kararı: BİRLEŞTİR** — tek katman `cli.bicimle(cevap, rozet=…)`, rozet **parametre** (bool bayrak yok), TUI ince kabuk kaldı. Commit `613e3ba` (yapısal) |
| **18** | ⭐ **atıf doğrulayıcı kanun adını YANLIŞ kanuna çözüyor** — *"Gelir Vergisi Kanunu"* → **1319 Emlak Vergisi**, ve `DOGRULANDI` basıyor | **KAPANDI** 2026-09-11 | Alet **manşet `0/114`'ü üretenin ta kendisi**. Onarıldı ve çıpalar yeniden puanlandı: parantezli adlı kanunlarda yanlış-kanun + `DOGRULANDI` **7/16 → 0/16**. Commit `0031976`. Yan etkisi **kusur 22**. Ayrıntı aşağıda |
| **19** | fp16 rejiminde model **istem yer tutucusunu harfiyen basıyor** (*"(KANUN ADI, Madde 13)"*), `0/80 ↔ 2/80` | **KAPANDI** 2026-09-11 | **insan kararı: KAPATILSIN** — sunumda `(KANUN ADI, Madde 13)` → `(kanun adı belirtilmemiş, Madde 13)`. **Silinmedi, dürüstçe işaretlendi**: madde numarası vatandaşın doğrulayabileceği tek adrestir. Commit `5398c66` |
| **20** | ürün yolunun 2. geçişi `reasoning_content` alanına bağımlı; sunucunun `--reasoning-format` varsayılanı değişirse **sessizce tek geçişe düşer** (boş cevap kusuru geri gelir) | **KAPANDI** 2026-09-11, **iki yarısı da** | **insan kararı: İKİSİ DE** — kod: `servis._reasoning_kapisi()`, sessiz düşüş yerine **erken ve gürültülü** `RuntimeError` (commit `3a8109e`); `compose.yaml`'da `--reasoning-format deepseek` açıkça pinlendi ve **mutasyon denetimiyle** çivilendi (commit `1d0c616`). ⛔ Kapı **gözlem** kapısıdır, açılış yoklaması değil: düşünce üretmeyen **meşru** sunucuyu öldürmez |
| **21** | `hakhukuk/araclar.py` **kendi ikinci ad indeksini** taşıyor — kusur 18'in onarımı ürün yüzeyine GEÇMEDİ | **KAPANDI** 2026-09-11 | Tuzak **2.18** kalıbı (*aynı ölçümün ikinci bir aleti*): vatandaşa giden atıf doğrulaması ile yayımlanan sayıyı üreten doğrulama **AYRI**ydı. Ayrışma gerçekti: 892 kanun adında **19**, parantezli 16'da **7**, çıpanın gerçek atıflarında **24/114** fark. **insan kararı: ONARIMI ÜRÜN YÜZEYİNE DE TAŞI** — `araclar.py` artık `atif_dogrula`'dan import ediyor, kopya indeks silindi. Eşdeğerlik kanıtlandı: 94 dosya · 11.634 hüküm, iki kolun çıktısı `sha256` **birebir**. Sonrası **0/892 · 0/16 · 0/114**. Commit `f6908e3` |
| **22** | rakip kollarının uydurma-madde sayıları **onarılmamış aletle** üretildi | **KAPANDI** 2026-09-11 | **insan kararı: YENİDEN PUANLA** — yayımlanan boru hattıyla, payda **birebir** olsun diye. Sonuç **aleyhimize** çıktı ve **yazıldı**: `3.1 Flash-Lite` **`1/152` → `0/153`**. Ayrıntı aşağıda |
| **23** | ilk yeniden-puanlama koşusu **eski sayıyı verdi ve tekrarlanamadı** | **AÇIK — ikinci kez sınandı, KAPATILMADI** | Modül gölgeleme arandı, **bulunamadı**. Yayımlanan sayılar 4 ardışık koşuda bayt-bayt aynı + bağımsız probla teyitli. **İkinci sınama** (adım 6.6, 2026-09-12, $0): `harness_tablo.py` + `uc_okuma_kutle.py` 6.5'in Anthropic çıktısında **ikişer kez** koştu, ikisi de `sha256` **birebir** — deterministik taraf üçüncü kez de temiz çıktı. Aynı adım ayrıca **canlı bir "aynı girdi farklı sayı" örneği** buldu (id65, 6.4'ün duman koşusu) ama kökeni **AYRI**: hakem-çağrısı (LLM) düzeyinde bilinen, belgelenmiş `temp=0` gürültüsü — kod tarafında determinizm ihlali değil. **Bu yüzden kapatılmadı**: taraflardan biri temiz ama orijinal olayın kök nedeni hâlâ bulunamadı. Ayrıntı aşağıda (§Kusur 23). **Devir → `v2`** sürüyor |
| **24** | iki README'nin *"Bugün kurup çalıştırabilir miyim? — HAYIR"* tablosu **BAYAT** | ✅ **KAPANDI** 2026-09-12 (`b077f13`) | *"`hakhukuk/` dizini yok"* ve *"ağırlıklar hiçbir yerde yayımlanmadı"* diyordu — **ikisi de YANLIŞtı**. `HAYIR` → `KISMEN`, dört satır yeniden yazıldı. ⚠️ **Bu sicil 2026-09-12'ye kadar "AÇIK" demeye devam etti** (kapanış `00-IS-SIRASI`'ya işlendi, buraya işlenmedi) — damga `v1-son-iş` turunda, 6.3 sonrası yapılan tutarlılık denetiminde vuruldu |
| **25** | `MODEL_CARD` *uydurulmuş madde* satırında **iki farklı kesir birimi** | ✅ **KAPANDI** 2026-09-13 | **İnsan kararı: tüm paydalar `DOGRULANDI` olur.** Sonnet-5 hücresi `2/163` (payda toplam atıf) → `2/161` (payda `DOGRULANDI`); yeniden puanlama yok, aynı sayımın (`DOGRULANDI` 161 · `MADDE_YOK` 2 · `KANUN_YOK` 0) başka ifadesi. Gemini/base sayıları **oynamadı**. Birim artık `MODEL_CARD.md` ve `docs/HF_KARTI.md`'de satıra açıkça yazılı (kusurun kökü buydu). Adım 8, `v1-son-iş` |
| **26** | ⭐ sunumda **çift tırnak**: model işaretlerin içine kendi düz tırnağını yazınca `“ "…" ”` çıkıyor | **KAPANDI** 2026-09-11 | **İNSAN GÖZÜ KAPISINDA yakalandı**; kusuru **aynı gün biz eklemiştik** (kusur 12a/19 süzgeci) ve testler **tırnaksız** alıntıyla yazıldığı için görmemişti. Commit `6a58d72` (+6 test): sarmalayan tırnak soyulur, tırnaksız girdi **aynen** korunur, metnin **ortasındaki** iç alıntı **bozulmaz** |
| **27** | Kaynaklar listesinde **madde biçimi tutmuyor** — `MADDE 349` · `Madde 8` · `MADDE 16` yan yana | **AÇIK** | Aynı göz kapısında görüldü. Korpusun **ham** tutarsızlığının (kusur 13) vatandaş ekranına yansıması; veri bozulmasın diye ham alan **korunuyor**. **Gösterim** katmanı işi. **Devir → `v2`** |
| **28** | ⭐ `hakhukuk-api` / `hakhukuk-tui` / `hakhukuk` komutları **ÇALIŞMIYOR** — paket kurulu değil, üstelik **belgeler o komutu öneriyordu** | **KAPANDI** 2026-09-11 | Göz kapısı **hazırlanırken** yakalandı. İki ayrı sebep: (1) paket venv'e **hiç kurulmamıştı** (`pip install -e .`); (2) **latent kusur** — `license = "Apache-2.0"` PEP 639 **dize** biçimidir, `build-system.requires` yalnız `setuptools>=68` diyordu ve kurulu 70.2.0 o biçimi **reddediyordu**; yalıtımlı kurulum çalışıyordu çünkü pip en yeni setuptools'u çekiyor, `--no-build-isolation` ile **patlıyordu**. `setuptools>=77` yazıldı, `tests/test_belgeler.py::test_build_system_license_bicimiyle_TUTARLI` bunu **kapı** olarak çiviledi (kırmızı görüldü). ⚠️ Kusur **11** bundan **bağımsız olarak AÇIK kalır** |
| **29** | imaja ürünün **okumadığı** 36,1 MiB korpus yedeği giriyor | **KAPANDI** 2026-09-12 | Adım 6.3.1: `.dockerignore`'a `data/corpus/*.yedek-*` eklendi (commit `b78d142`). Ölçüldü: `hakhukuk:0.3.0` **2,13 GB → 2,08 GB** (`docker images`); `docker run --rm hakhukuk:0.3.0 ls -la /app/data/corpus/` artık yalnız `KUNYE.json` + `mevzuat_maddeler.jsonl` gösteriyor, yedek **YOK**. Aynı turda `docker compose up` **temiz volume'le** (kusur 31'in dersi: `hakhukuk_artefakt` silinip yeniden kuruldu) uçtan uca doğrulandı — GGUF · korpus (imaj↔volume) · **indeks** (G8'in yeni kapısı) `sha256` kapılarının **üçü de** bağımsız doğrulandı; konteynerde 80 DEV sorusu HTTP API'sinden koşuldu, boş cevap **0/80** (bkz. MODEL_CARD §7.9 kutusu (c), `outputs/eval/g23-konteyner-urun-yolu-80/`) |
| **30** | ⭐ `cli.py` künye yolunu **repo köküne göreli** çözüyor — kurulu pakette BULUNAMIYOR | **KAPANDI** 2026-09-11 | **İmajın İÇİNDE** ölçüldü. **Sessiz bozulma:** patlamıyor, `except` dalına düşüyor, vatandaş *"892 kanun · 37.949 madde"* yerine *"künye okunamadı — sayı belirsiz"* okuyor. ⚠️ Kusuru **aynı tur biz ekledik** (G21 Adım 7); host'ta görünmüyordu çünkü paket **editable** kurulu. TDD ile onarıldı: künye **paketin kendi ağacına** göre çözülüyor (`hakhukuk/veri/KUNYE.json`, **sembolik bağ** ⇒ ikinci kopya yok) + `package-data`. Commit `91cd0af` |
| **31** | `compose` volume adını **proje adından** türetiyor (`hakhukuk_artefakt`), dizin adından değil | **AÇIK (kayıt)** | **Kusur değil, kayda değer davranış:** hazırlıkta `hukuk-slm_artefakt` doldurulmuştu ve **kullanılmadı**. ⇒ **İyi ki öyle oldu** — artefakt elle konsaydı `sha256` kapısı **hiç ateşlenmeyecek**, Adım 6'nın asıl şartı sınanmamış olacaktı. **Devir → kayıt** |
| **32** | 🚨 **KONTEYNER UÇTAN UCA ÇALIŞMIYOR** — her soruda HTTP 500 | **KAPANDI** 2026-09-11 | `docker compose up` ile **ölçüldü**. Kök sebep bir **onarımın ters yüzü**; ayrıntı aşağıda. Commit `0e2a470`: yerleşim repo ağacını aynalıyor + `sha256` eşitlik kapısı |
| **33** | 🚨 `yeniden_uret.sh`'ın recall@10 geçerlilik kapısı **var olmayan alanı** okuyordu, HER ZAMAN düşüyordu | **KAPANDI** 2026-09-12 | Kapı `gold_retrieved`/`altin_getirildi` okuyordu — detay kayıtlarında yok, gerçek şekil `harness.altin_sirasi` (0-tabanlı) + `harness.altin_dusuruldu`. `recall@10` her koşuda **0,0000** okunuyor, kapı **hiçbir koşuda geçemezdi** — çıpanın kendi verisinde bile (f02: gerçek 76/80=0,9500 ↔ kapının hesabı 0/80). TDD ile onarıldı: `scripts/olcum_uretim/recall_kapisi.py` (yeni, `erisim_korpus/recall_olc.recall_at_k`'yi çağırır — hesap tekrar edilmez), `harness` alanı eksikse **gürültülü** `KeyError`. Kalibrasyon: f02 çıpasında ve s17 `Q5_K_M` koşusunda recall@10 = 0,9500, kapı **GEÇTİ**. Commit `cc12b6e` |

---

## (B) Taşıyıcı gerekçeler — tek cümlelik özetle kaybolan dört bulgu

Yukarıdaki tablo **sicildir**. Aşağıdaki dördü bu turun en değerli bulgularıdır ve satır
uzunluğuna sığmaz.

### Kusur 18 — korunma **aletten değil, ÖRNEKLEMDEN** geliyordu

Atıf doğrulayıcı kanun adını **gevşek** eşleştiriyordu: *"Gelir Vergisi Kanunu Madde 1"*
sorgusu **1319 Emlak Vergisi Kanunu**'na çözülüyor ve oraya `DOGRULANDI` damgası basılıyordu.
Bu alet, **manşet `0/114`'ü üretenin ta kendisiydi**.

Onarımdan sonra çıpalar yeniden puanlandı ve **manşet `0/114` ile donmuş TEST'in `0/52`'si
OYNAMADI**. Bu bir aklanma **değildir**: 114 atfın hiçbiri **parantezli adlı** bir kanuna denk
gelmemişti. Alet, parantezli adlı **16 kanunun 7'sinde** yanlış kanuna `DOGRULANDI` basıyordu
(onarım sonrası **0/16**). Yani yayımlanmış sayı doğruydu — ama **doğruluğunu aletin
sağlamlığına değil, örneklemin rastlantısına borçluydu**. Bu ayrım yazılmazsa kayıt,
*"alet kusurluydu ama sayı tuttu, demek ki kusur önemsizdi"* diye okunur ve bu **yanlıştır**.

⚠️ Donmuş TEST'in `0/52`'si de aynı aletle üretilmişti ve onarımdan önce **ölçülmemişti**.
Yeniden **puanlamak** yeni sınav açmak değildir — aynı cevaplara düzeltilmiş aleti uygulamaktır
(ADR-0050 kalıbı, insan kararı).

### Kusur 22 — rakipler yeniden puanlandı; sonuç **ALEYHİMİZE** çıktı ve yazıldı

Kusur 18'in onarımının yan etkisi: rakip kollarının uydurma-madde sayıları **onarılmamış
aletle** üretilmişti. Tabloda **iki farklı aletin** sayısı yan yana duruyordu ve bu ADR-0057'nin
*eşit sınav* kuralını ihlal ediyordu. İnsan kararıyla beş kol da **yayımlanan** boru hattıyla
(`scripts/puanlama/harness_tablo.py`) yeniden puanlandı; **kalibrasyon geçti** — kendi
`harness_tablo.json`'umuz **alan alan** yeniden üretildi. Her kol **iki kez** koştu, bayt bayt aynı.

**702 atfın tam olarak 1'i değişti** ve o damga **rakip aleyhine yanlış** basılmıştı:
`gemini-3.1-flash-lite` **`1/152` → `0/153`**.

⇒ Tek deterministik üstünlüğümüzde artık **eşitiz**. Karşılığında alınan şey **eşit sınavdır**:
beş kol da aynı aletle puanlanıyor. Sayı `MODEL_CARD` ve `CLAUDE.md`'de **değiştirildi** ve
şerhle **iki yerde** damgalandı. Diğer üç kol oynamadı.

### Kusur 23 — ikinci sınama: alet tarafı TEMİZ, hakem tarafı AYRI bir gürültü kaynağı

Adım 6.6 (2026-09-12, **$0**, hakem çağrılmadı) kusur 23'ü ikinci kez sınadı.
`scripts/puanlama/harness_tablo.py` ve `scripts/puanlama/uc_okuma_kutle.py`, 6.5'in Anthropic
hakem çıktısı (`outputs/eval/hp-rakip-anthropic-tam/gnd_h1_3_5_flash_anthropic.jsonl`, girdi
detay `outputs/eval/f04-rakip-onsozsuz/h1_3_5_flash_nb_detail.jsonl`) üzerinde **ikişer kez**
koşuldu; her ikisinin `--out` çıktısı `sha256` **birebir** (`harness_tablo` `77467479…`,
`uc_okuma` `12506544…` — tek fark stdout'taki dosya-adı satırıydı). Bu, kusur 22'nin kendi
ikinci sınamasıyla (#67: *"her kol iki kez koştu, bayt bayt aynı"*) birlikte **üçüncü**
bağımsız doğrulama: yayımlanan deterministik puanlama boru hattı tekrar tekrar bayt-bayt aynı
çıkıyor.

Görev ayrıca 6.4'ün duman koşusundaki **id65**'i gündeme getirdi: birleşik 6-kalemlik çağrıda
(`duman6`) 17 iddia/`faithfulness=0,5294`, dilimli 2-kalemlik çağrıda (`duman_orta`) 16
iddia/`faithfulness=0,5000` — aynı kalem, aynı hakem modeli, aynı gün, **iki farklı sayı**.
`groundedness.py::score_record` her kalemi **tek başına**, kendi `cevap` metniyle çağırır
(`extract_claims`/`verify_claims` yalnız o kalemin cevabını görür) — iki koşu arasında
paylaşılan bir prompt/bağlam **yoktur**, dolayısıyla *"farklı grup bağlamı"* ifadesi
yanıltıcıdır: fark, **aynı prompt'un iki ayrı API çağrısında** farklı çıktı vermesinden gelir.
Bu, betiğin kendi docstring'inin (satır 26) baştan yazdığı şey: *"claim sınırı hakem-öznel +
temp=0 tam deterministik değil"* — tam bunun için `--runs N` parametresi ve *"paper için
runs≥3"* önerisi zaten vardır.

**Bu, kusur 23'ün canlı bir örneği DEĞİLDİR.** Kusur 23 kendi kodumuzun (puanlama/doğrulama
boru hattı) aynı, sabit girdide farklı sayı vermesiydi — bugünkü ikinci sınama bu tarafın
**temiz** olduğunu bir kez daha gösterdi. id65'in farkı **hakem modelinin kendisinde**, LLM
çağrısı düzeyinde, zaten bilinen ve belgelenmiş bir kaynaktan geliyor; kod tarafında hiçbir
determinizm ihlali yok. İkisini karıştırmak, çözülmüş bir aletin üstüne çözülmemiş bir
hakem-gürültüsü sorununu bindirir.

⇒ **Hüküm: kusur 23 KAPATILMADI.** Deterministik taraf art arda üç kez (yayımlanan sayılar ·
#67'nin rescoring'i · bugünkü 6.6) bayt-bayt aynı çıktı — bu taraf **temiz** sayılır. Ama
orijinal olayın (*"ilk koşu eski sayı verdi"*) **kök nedeni hâlâ bulunamadı**; kapatmak için
kendimizi zorlamadık. **Devir → `v2`** aynen sürüyor, yalnız artık şu netlikle: `v2`'nin işi
kod-tarafı bir hata aramak değil, hakem-katmanı gürültüsünü `--runs N` havuzlamasıyla
azaltmaktır — bu ayrım bugüne kadar yazılı değildi.

### Kusur 32 — onarımın **ters yüzü**: `git clone`'u düzeltti, konteyneri kırdı

Konteynerde üç kutu da ayağa kalkıyordu (`indir` çıkış **0**, `llama` **healthy**, `app` **Up**),
boş sorgu **422** dönüyordu — ama **gerçek soru 500 veriyordu**. Kök sebep: indeksin
`KUNYE.json`'u korpus yolunu **indeks dizinine göreli** tutuyor (`../../corpus/…`). Repo ağacında
bu `data/corpus/…`'a çözülür; konteynerde indeks **volume'de** olduğu için `/corpus/`'a çözülür
ve korpus orada değildir.

Bu, **`G8 Adım 1b`'nin taşınabilirlik onarımının TERS YÜZÜDÜR**: mutlak yol → göreli yol
değişikliği `git clone`'u onardı, ama indeksin **repo ağacının dışına** taşındığı tek düzeni
(konteyner) **kırdı**. Bu hattaki kural şudur ve bu kusur onun yeni kanıtıdır:
***onarım da bir değişikliktir ve kendi regresyonunu ister.***

Tek tesellisi: **sessiz değildi** — `SystemExit` ile gürültülü patlıyordu.

### Kusur 26 · 27 · 28 · 30 — üç insan gözü kapısının **süit yeşilken** yakaladığı dört kusur

Dördü de sayısal kapıların göremediği yerden geldi ve **ikisi (26 · 30) aynı gün bizim
yazdığımız koddandı**. Testler kusurun *görülmediği* varsayımla yazılmıştı: tırnaksız alıntı ·
editable kurulum · repo ağacı.

⚠️ **DÜZELTME:** kapanış bloğunda önce *"273 test yeşilken"* yazılmıştı ve **yanlıştı** — dördü
aynı ana ait değil. Commit sırasından okunan doğrusu: **26 · 27** → süit **267**
(`faad932` ↔ `063330c`) · **28** → **273** · **30** → **274**.

⇒ **Sayısal kapı, TESTİN KÖRLÜĞÜNÜ görmez.** İnsan gözü kapısının bu hattaki bedelini bir kez
daha ödediği yer burasıdır: süit yeşildi ve dört kusur **ekranda** yakalandı.

---

## (C) DEVİR — kapanış kuralının şartı

Kapanış anında **on bir** kusur açıktı. Tablo **nereye gittiklerini** söyler; kusurun tam metni
yukarıdaki sicildedir.

| # | kusur | DEVREDİLDİ |
| :-- | :--- | :--- |
| **5a** | zayıf eşleşme sinyali — **ölçüldü, ayrışma YOK**, rozet eklenmedi | **`v2`** · yeni bir gösterge ya da daha büyük `n` gerektirir ([ADR-0079](0079-zayif-eslesme-rozeti-eklenmedi.md)) |
| **6** | `wrong_ref` frontier'ın **9,3×** gerisinde | **`v2` · borç `B1`** ([ADR-0075](0075-v1-sft-kapanir-v2-sequential-rl.md)) — **bu turda ağırlaştı**: fp16'da 2,0× kötüleşiyor |
| **10** | HF **görünürlüğü** (ağırlıklar ÖZEL) | **insan kararı**, iş değil. `push` yarısı **2026-09-12'de KAPANDI** (62 commit `origin/master`'a gitti) *(KAPANDI 2026-09-13, ADIM 9 — görünürlük yarısı da PUBLIC yapıldı, insan onayıyla; bu tablo kapanış anının SNAPSHOT'ıdır, geriye dönük düzeltilmez)* |
| **11** | paket `scripts/`'e bağımlı, tek başına kurulamıyor | **kendi turu** — kusur **21** onarımı importu birden **ikiye** çıkardı; kalıcı çare `madde_anahtar` + `atif_dogrula` + `score_abstention` üçlüsünün **pakete taşınması** |
| **12b** | iskele işaretlerinin **kaynağı** eğitim verisi | **`v2` · borç `B11`** |
| **23** | bir yeniden-puanlama koşusu **eski sayıyı verdi, tekrarlanamadı** | **`v2`** · modül gölgeleme arandı **bulunamadı**; **ikinci sınama** (6.6) deterministik tarafı bir kez daha temiz buldu ama kök neden hâlâ yok — kapanmadı, `v2`'nin işi artık hakem-katmanı gürültüsünü `--runs N` ile azaltmak (§Kusur 23) |
| **24** | iki README'nin *"Bugün kurup çalıştırabilir miyim? — HAYIR"* tablosu **BAYAT** | **kendi turu** · *"`hakhukuk/` dizini yok"* ve *"ağırlıklar yayımlanmadı"* **ikisi de YANLIŞ** *(KAPANDI 2026-09-12 `b077f13` — bu tablo kapanış anının SNAPSHOT'ıdır, geriye dönük düzeltilmez)* |
| **25** | `MODEL_CARD` *uydurulmuş madde* satırında **iki farklı kesir birimi** | **`v2`** · Sonnet-5 hücresi **toplam atıf**, Gemini sütunları **`DOGRULANDI`** paydası kullanıyor *(KAPANDI 2026-09-13, Adım 8 — tüm paydalar `DOGRULANDI`'ya çevrildi; bu tablo kapanış anının SNAPSHOT'ıdır, geriye dönük düzeltilmez)* |
| **27** | Kaynaklar listesinde **madde biçimi tutmuyor** (`MADDE 349` ↔ `Madde 8`) | **`v2`** · korpusun **ham** tutarsızlığının vatandaş ekranına yansıması; **gösterim** katmanı işi |
| **29** | imaja ürünün **okumadığı** 36,1 MiB korpus yedeği giriyor | **G20'nin devamı** · tek satırlık `.dockerignore` düzeltmesi *(KAPANDI 2026-09-12, adım 6.3.1 — bu tablo kapanış anının SNAPSHOT'ıdır, geriye dönük düzeltilmez)* |
| **31** | `compose` volume adını **proje adından** türetiyor | **kayıt** — kusur değil, **kayda değer davranış**: artefaktı elle koymak `sha256` kapısını **hiç ateşlemeyecekti** |

**Devredilmemiş açık kusur YOKTUR** ⇒ `hp-hat-a-hat-b` planının kapanışı **geçerlidir**.

---

## (D) Ölü bağlantılar — **kayıt, onarım değil**

`docs/adr/**` ve `docs/record/**` içinde `docs/superpowers/` yollarına **29 bağlantı** vardır
(2026-09-12'de `grep` ile sayıldı). Bunların **19'u 2026-09-06 doküman temizliğinden ZATEN
ölüydü** ve hiçbir yerde yazılı değildi. Silme **9 yenisini** ekler.

| hedef | sayı | durum |
| :--- | ---: | :--- |
| `plans/2026-09-07-hp-hat-a-hat-b.md` *(2'si `#açık-kusurlar…`, 1'i `#kapanış-ve-devir-kuralı…` çıpalı)* | **9** | **VARDI** ⇒ bu silmeyle **ÖLÜYOR** |
| `plans/2026-08-06-asiri-red-tau-a-v2.md` | 5 | 2026-09-06'dan beri **ÖLÜ** |
| `plans/2026-08-05-olcum-bosluklari.md` | 4 | 2026-09-06'dan beri **ÖLÜ** |
| `specs/2026-09-06-v1-v2-roadmap-taslak.md` | 2 | 2026-09-06'dan beri **ÖLÜ** |
| `plans/2026-08-03-s3a-on-prob.md` | 2 | 2026-09-06'dan beri **ÖLÜ** |
| `specs/2026-07-17-tez-cercevesi-design.md` | 1 | 2026-09-06'dan beri **ÖLÜ** |
| `.superpowers/sdd/g21/*` | 5 | `gitignore`'lu — bu yolda depoda **hiç var olmadı** |
| `docs/superpowers/plans/` *(dizin kuralı, dosya bağlantısı değil — ADR-0056)* | 1 | **canlı kalır**; yeni plan oraya yazılacak |

**Toplam 29.** Silme öncesi ölü: **19**. Silmeyle ölecek: **9**. Bağlantı olmayan dizin
kuralı: **1**.

**Etkilenen dosyalar** — `plans/2026-09-07-hp-hat-a-hat-b.md`'ye işaret eden **9 dosya**
(5 ADR + 4 kayıt):

| ADR | kayıt |
| :--- | :--- |
| `docs/adr/0074-hakem-paneli-kuruldu-baglayici-hukum.md` | `docs/record/2026-09-10-hp-hat-a-hat-b-kapanan-gorevler.md` |
| `docs/adr/0078-konteyner-dagitimi-rejim-kilidi.md` | `docs/record/research_log/2026-09-07-hakem-paneli-iki-aile.md` |
| `docs/adr/0079-zayif-eslesme-rozeti-eklenmedi.md` | `docs/record/research_log/2026-09-11-urun-yuzeyi-ve-aygit-kusurlari.md` |
| `docs/adr/0081-altinci-durum-bos-sorgu.md` | `docs/record/research_log/2026-09-12-konteyner-ve-alet-onarimlari.md` |
| `docs/adr/0082-app-kutusu-host-sapmasi.md` | — |

Önceden ölü 19 bağlantının bulunduğu **8 dosya**: `docs/adr/0027` · `0056` · `0057` · `0061` ·
`0062` ve `docs/record/research_log/2026-08-04-s3a-on-prob.md` · `2026-08-05-olcum-bosluklari.md` ·
`2026-09-06-hasat-kabul-olcutu-coktu.md`.

⛔ **Bu bağlantılar ONARILMAZ.** `docs/adr/**` ve `docs/record/**` yeniden yazılmaz — onlar
*"o gün bu belge şunu diyordu"* kaydıdır ve kural bağlayıcıdır. **Ölü bağlantı belgelenmiştir,
onarılmayacaktır; sessiz kalmasındansa yazılı olması yeğlenmiştir.** Bu ADR, o 29 bağlantının
nereye işaret ettiğinin **tek yazılı kaydıdır**.

---

## (E) Elenen seçenekler

**(1) Planı `docs/record/`'a taşımak.** Gövde korunurdu, ölü bağlantı 9 yerine 0 olurdu.
**İnsan reddetti**, gerekçe: *"plan formatı ajanları yanıltır"* — kutucuklu bir dosya
`record/` altında bile **yürütülebilir** sanılır, ve deponun kendi belge-türü tablosu
*"'sırada ne var' diyen bir belge **plandır** ve `record/` altında duramaz"* der. Kapanan
görevlerin tam metni zaten `docs/record/2026-09-10-…-kapanan-gorevler.md`'ye taşınmıştı;
oraya ikinci bir plan gövdesi koymak o ayrımı bozardı.

**(2) Eski yolda bir yönlendirme kütüğü (stub) bırakmak.** *"Bu plan kapandı, sicili
ADR-0083'tedir"* diyen tek sayfalık bir dosya, **0 ölü bağlantı** verirdi. **İnsan sadeliği
yeğledi** ve ölü bağlantıyı **kabul edilmiş bedel** olarak aldı: `docs/superpowers/` **tek bir
canlı plan** taşıyacaktır, ve dizinde duran bir mezar taşı o kuralın ilk istisnası olurdu.

---

## Ne KURULMAZ

- Bu ADR *"plan içeriği yedeklendi"* **DEMEZ**. Planın **gövdesi silindi**; kurtarılan yalnız
  **kusur sicili** ve **devir tablosudur**. Görev metinleri, `verify:` şartları, kutucuk
  gerekçeleri ve ara turların anlatısı **gitti**.
- Bu ADR, ADR **0074-0082**'nin ve kayıt **#64-#67**'nin **yerine geçmez**. Ölçümler,
  hükümler ve anlatı **zaten orada** durur; buradaki sicil onlara **işaret eder**, onları
  **tekrarlamaz**.
- Bu ADR *"kusurlar çözüldü"* demez. Sekiz kusur **AÇIK**tır ve bir sonraki plana **adıyla**
  devredilmiştir.
- Bu ADR ölü bağlantıları **onarmaz** ve onarılabilir olduğunu iddia etmez.

## Bedel

Bir okur, `docs/adr/**` ya da `docs/record/**` içindeki **9 bağlantıyı** tıkladığında **404**
alacaktır ve dosya geri gelmeyecektir. Bedel bilinerek ödendi; karşılığında `docs/superpowers/`
**tek bir canlı plan** taşır ve *"hangisi güncel"* sorusu ortadan kalkar. Bu ADR, o 9 bağlantının
neye işaret ettiğini bilen **tek belgedir**.

---

## EK — silinen *"mevzuat kapsamı ve tazelik"* tasarımının taşıyıcı özü

**Niçin bu ek bu ADR'de.** `docs/superpowers/` boşaltılırken yalnız kapanan plan değil,
**koşulmamış** bir tasarım da siliniyor: `2026-09-07-mevzuat-kapsam-ve-tazelik-design.md`
(294 satır, "spec B") ve onun uygulama planı `2026-09-08-mevzuat-kapsam-ve-tazelik.md`
(2.465 satır · **9 görev** · **62 kutucuk**, hiçbiri işaretli değil — `grep -c "^- \[ \]"`
2026-09-12). İş sırası o spec'i **grill'e sokmayı** öngörüyor; spec silinirse grill
**tasarım gerekçesi olmadan** koşar. 2026-09-12 tarihli inceleme
(`.superpowers/sdd/spec-incelemesi.md`) şu hükmü verdi: ***"mimarisi sağlam ve ölçülmüş;
yeniden yazılmasını gerektiren bir tasarım hatası yok — ama önce dokuz madde güncellenmeli."***
Korunması gereken şey tam da o mimaridir.

**Bu bölüm spec'in YERİNE GEÇMEZ ve *"tasarım onaylandı"* DEMEZ** — grill'in **girdisidir**.
Dokuz madde **açık** durur. Silinen dosyalara bağlantı verilmez; adları düz metindir.

---

### E.1 · Amaç — tek paragraf

Korpusu kat kat büyütmek **ve** korpusu *tarihi belli, tazelenebilir, geri alınabilir bir
anlık görüntüye* çevirmek; ürün bunu yaparken **ağa dokunmadan** çalışmaya devam ederken.
Canlılık **ürünün dışına** alınır: korpus sürümlenmiş bir anlık görüntüdür, tarihi künyede
yazılıdır, tazeleme **ayrı bir iştir**. Ürün her zaman *tarihi belli* bir korpusla çalışır —
canlı hukukla değil. Takas bilerek **tekrarlanabilirlik lehine** yapılmıştır: her soruda canlı
API sorgusu (a) her kullanıcıdan **TR IP** ister, (b) API düşerse **ürünü düşürür**,
(c) kullanıcının **sorusunu dışarı sızdırır**, (d) ölçümü **yeniden üretilemez** kılar.

---

### E.2 · Mimari — üç zaman ölçeği, dört dar birim

```
  bedesten API  (canlı, TR IP şart)
        │
        │  1. TAZELİK — periyodik; bizde VE (TR IP varsa) kullanıcıda
        │     66 istek → kayitTarihi farkı → yalnız değişeni indir
        ▼
  data/corpus/   ← SÜRÜMLENMİŞ ANLIK GÖRÜNTÜ · tarihi künyede
        │
        │  2. İNDEKSLEME — yalnız değişen maddeler yeniden gömülür
        ▼
  data/index/    ← korpus künyesine BAĞLI
        │
        │  3. ERİŞİM — kullanıcının makinesinde, ağa DOKUNMAZ
        ▼
     answer()
```

Üç sorumluluk **üç farklı zaman ölçeğinde** koşar: 1 haftalar · 2 tazelemeden sonra ·
3 her soruda. Sınır buradadır: **erişim katmanı ağı hiç görmez.**

`hakhukuk/mevzuat/` **bugün YOKTUR** (`ls hakhukuk/` 2026-09-12: `api · araclar · cli · indir ·
istem · servis · terazi · tipler · tui` — `mevzuat/` yok). Aşağıdaki dört birim spec'in
kurmayı öngördüğü **yeni** alt pakettir; adları ve sorumlulukları spec §4 ile planın dosya
tablosundan birebir alınmıştır.

| birim | tek sorumluluğu | bağımlılığı |
| :--- | :--- | :--- |
| `hakhukuk/mevzuat/kaynak.py` | **bedesten sözleşmesi**: `listele(tur) -> [Kayit]` · `metin(mevzuatId) -> str`. Sayfalama (`pageSize` max 20), `{"data": …, "applicationName": …}` sarmalaması, TR IP tespiti, geri çekilmeli retry **burada gizli** | stdlib HTTP |
| `hakhukuk/mevzuat/tazelik.py` | **fark taraması**: yerel künye ↔ uzak `kayitTarihi` → `Fark(yeni, degisen, kaybolan)`. **Kendisi ağa dokunmaz** — `kaynak`'ı tüketir, bu yüzden sahte `kaynak` ile **ağsız** sınanır | `kaynak` · `tipler` |
| `hakhukuk/mevzuat/anlik.py` | **anlık görüntü**: sürümleme · künye · `sha256` · **atomik yazma** · geri alma | `tazelik` |
| `hakhukuk/mevzuat/indeksle.py` | **artımlı gömme**: yalnız değişen `madde_id`'ler; indeks künyesini korpus künyesine bağlar | `anlik` · numpy |

İki yardımcı dosya: `tipler.py` (`Kayit · Fark · Kunye · Rapor · Tazelik · TrIpGerekli` —
donmuş veri tipleri) ve `__init__.py` (paketin **tek** dış yüzü: `tazele() · Tazelik · Rapor`).

**Ana arayüz:** `tazele(mod: Tazelik = Tazelik.SOR) -> Rapor`. `Tazelik` enum'u
**`SOR`** (varsayılan — *"14 belge değişmiş, güncelleyeyim mi"*) · `OTOMATIK` · `KAPALI`.
**Bool bayrak yok** (CLAUDE.md §4): *"sor"* hâli bir `bool` ile ifade edilemez.

**Niçin ayrı `kaynak.py`** *(POSD silme testi)*: silinirse bedesten'in tuhaflıkları —
`pageSize` max 20, `guncellemeTarihi` **60/60 örnekte boş**, TR IP şartı, gövde sarmalaması —
**dört çağırana birden** yayılır.

**Niçin `tazelik.py` ağa dokunmaz:** saf fark aritmetiği testlenebilir kalsın diye. Sahte
`kaynak` ile *yeni · değişen · kaybolan* senaryoları ağsız ve **$0** koşar.

---

### E.3 · İki sert kural — spec'in kendi değişmezleri, yumuşatılmadan

**1 · TR IP yoksa cihaz içi fallback YOKTUR.** `kaynak.py` `TrIpGerekli` atar; `tazele()`
onu **yutmaz**, `Rapor.durum = IP_YOK` döner ve kullanıcıya *"tazeleme yapılamadı; korpusun
tarihi …"* denir. **Sessiz düşürme bu repoda hata sınıfının kendisidir.** Sistemin tamamında
kullanıcı **asla tarihsiz kalmaz**: TR IP'si olmayan kullanıcı **bizim** tazelediğimiz anlık
görüntüyü indirir.

**2 · Kısmi tazeleme diske YAZILMAZ — hepsi ya da hiçbiri.** 14 belgeden 9'u inip ağ koparsa
korpus **bayt bayt eski hâlinde** kalır. Aksi hâlde künyedeki tarih ile içerik ayrışır ve
**o ayrışma hata vermez, yalnız sessizce yanlış olur.**

Buna bağlı mahremiyet hükmü: tazelik çağrısı **soruyu taşımaz**. `searchDocuments` yalnız
*"şu türde hangi belgeler var, `kayitTarihi` ne"* diye sorar; kullanıcının ne merak ettiğine
dair **tek bit** bilgi gitmez. Sızan tek şey *"bu IP korpusunu tazeliyor"*.

---

### E.4 · KAT MERDİVENİ ve kapısı — DÜZELTİLMİŞ hâliyle

Kapsam **kat kat** girer; her kattan sonra **aynı 80 soruyla** `recall@10` yeniden ölçülür.
**Hakem gerekmez, $0.** Eşik koşudan **önce** yazılmıştır (ADR-0050 kalıbı: *"sonucu gördükten
sonra eşik değil alet düzeltilir"*):

```
recall@10 ≥ 0,9500  →  kat GİRER
recall@10 <  0,9500  →  kat GİRMEZ, sebebi bulunana kadar
```

| kat | eklenen tür | yeni belge | ≈ madde |
| :--- | :--- | ---: | ---: |
| 1 | `KHK` + `CB_KARARNAME` | 119 | ~33.000 |
| 2 | `TUZUK` | 110 | ~4.000 |
| 3 | `YONETMELIK` | 172 | ~8.000 |
| 4 | `CB_KARAR` | 4.361 | ~76.317 |
| 5 | `KKY` | 4.043 | ~126.343 |
| | **eklenen toplam** | **8.805** | **247.660** |
| | bugünkü korpus | 892 | **40.496** |
| | **beş kat sonrası** | **9.697** | **288.156** |

**En değerli bulgu: merdiven baştan DOĞRUYMUŞ; hedefi kaydıran tek bir satırdı.**
Spec §7b hedefi **340.303** ilan ediyordu ve merdivenle arasında **52.147** madde açık
kalıyordu. Farkın kaynağı ölçüldü: §7b'nin `KANUN` satırı **917 belge × 102,7 madde =
94.145** sayıyor. Gerçek oran **45,3991 madde/belge**'dir — `data/corpus/KUNYE.json`'un
`n_madde` **40.496** ÷ `n_kanun` **892**, aynı değer korpus dosyası satır satır sayılarak
2026-09-12'de doğrulandı. **Sapma 2,26×** (102,7 ÷ 45,3991).

Düzeltme aritmetiği:

```
340.303 − 94.145 (spec'in KANUN satırı) + 41.631 (917 × 45,3991) = 287.789
```

Aynı sayı ikinci yoldan da çıkar: bugünkü 40.496 madde **korunur**, eksik 25 kanun
(917 − 892) ölçülen oranla eklenir → 246.158 + 40.496 + 1.135 = **287.789**.

| | madde |
| :--- | ---: |
| kat merdiveninin verdiği toplam | **288.156** |
| düzeltilmiş hedef | **287.789** |

⚠️ **ÜÇÜNCÜ bir tutarsızlık, aynı tabloda ve ayrıca kayda geçer:** spec'in `KKY` satırı **kendi
içinde çarpmıyor** — `4.043 × 31,2 = 126.141,6` iken tablo **126.343** ilan ediyor (**−201,4**).
Diğer üç satır tutuyor (`CB_KARARNAME` tam, `CB_KARAR` +0,5, `KANUN` +30,9 yuvarlama).
Bu yüzden düzeltilmiş hedef **iki değer** alabiliyor: spec'in *ilan ettiği* satır toplamlarıyla
**287.789**, `belge × oran`dan *yeniden hesaplanınca* **287.589**. Fark **200** ve **tamamı bu
satırdan** geliyor. Hüküm değişmiyor — merdivenin **288.156**'sıyla örtüşme her iki okumada da
**%0,13-0,20** bandında. Grill bu satırı da düzeltmeli (9 maddenin **birincisine** dâhildir).
| **fark** | **367 · %0,13** |

Yani merdiven ile hedef **%0,13 farkla örtüşür**; 52.147'lik açık **merdivenin değil,
`KANUN` satırının** eseriydi. Hedef **~288 bin madde** olarak okunmalıdır, 340.303 olarak
değil — ve **340.303'ün bütün türevleri** (697 MB indeks · 2,1 GB RAM · ~803 ms sorgu ·
~1,5 sa gömme) aynı oranda yeniden hesaplanmalıdır.

**Diğer türlerin oranları DOĞRULANAMAZ — ve şüphelidir.** §7b'nin bütün madde/belge
oranları **tür başına 6 belgelik** bir örneklemden geliyor; örneklemin **tabakalanmış olup
olmadığı spec'te yazmıyor**. Doğrulayabildiğimiz **tek** türde (`KANUN`) yöntem **2,26×**
şişti. `CB_KARAR` 17,5 · `KKY` 31,2 · **`CB_KARARNAME` 564,0** madde/belge sayıları
korpusumuzda o türler **bulunmadığı için** karşılaştırılamadı; özellikle `CB_KARARNAME`'in
`KANUN`'un 5,5 katı olan **564,0** değeri tek bir doğrulaması olmadan duruyor.
Bu **tuzak 1.11'in tam sınıfıdır** (*"küçük örneklemden doğrusal ekstrapolasyon; hata
vermez, kapı geçilmiş görünür"*, `docs/record/yurutme-tuzaklari.md`).

**Kapının kendi sınırı — spec'in en dürüst cümlesi, aynen korunur:** kapı yalnız
***"eskiyi bozmadı"*** der; ***"yeniyi buluyor"* DEMEZ.** 80 sorunun hepsi kanun
düzeyindedir; yönetmelik düzeyinde eval sorumuz **yoktur**. Kat 3 geçse bile *"yönetmelik
eklemek işe yaradı"* **kurulamaz**. Yeni soru yazmak **ayrı bir turdur**, insan onayı ister
(ADR-0067 usulü) ve donmuş TEST'i de ilgilendirir.

---

### E.5 · GRİLL'E GİRECEK DOKUZ MADDE

İncelemenin hükmü. Her madde **açık** durur; hiçbiri bu ADR'de kapatılmıyor.

| # | madde | niçin |
| :-- | :--- | :--- |
| **1** | **Hedef sayı düzeltilsin** — beş kat **288.156** veriyor, 340.303 değil | fark **52.147**, kaynağı `KANUN` satırının 2,26× şişkin oranı (E.4). Ya altıncı bir *"`KANUN` yeniden hasadı"* katı kendi kapısı ve bedeliyle yazılır, ya hedef **~288k** olur; `697 MB · 2,1 GB · ~803 ms · ~1,5 sa` türevleri yeniden hesaplanır |
| **2** | **n=6 örneklemi damgalansın ya da yenilensin** | ölçülebilen tek satırda **2,26×** sapma; tabakalanma yazılı değil. Tuzak 1.11'in reçetesi: ya tabakalanmış örneklem, ya **%50 emniyet payı**. `CB_KARARNAME 564,0` tek başına sorgulansın |
| **3** | **Eşit sınav faturası spec'e YAZILSIN** | silinen tasarım spec'inin (yeni belge katmanı) kendi hükmü: *"eşit sınavın kanıtı — rakipler **bizim indeksimizi** görüyor; indeksi sonradan değiştirmek o kanıtı **bozar** ve kolların yeniden ölçülmesini gerektirir (~$1,35)"*. Spec B indeksi kat kat değiştiriyor ve bu bedeli **ne anıyor, ne bütçeliyor, ne de kabul edilmiş maliyet olarak yazıyor** (E.6) |
| **4** | **Mülga kapısı SAHTE — gerçek kapı yapılsın** | plan yeni korpus satırlarına `"mulga": False` **sabitini** basıyor (plan satır 1914, `turu_indir`); bedesten `mevzuatMaddeTree` mülga bilgisi vermiyor. Spec §6'nın *"getirilen hiçbir kaynak `mulga=True` olmamalı"* testi bu zeminde **her zaman geçer** — boş bir tekrardır. Bu, 2026-09-07'de kapatılan *"vatandaşa mülga madde gidiyor"* kusurunun **ölçekte ve sessizce** geri gelmesidir (o gün ölçülen etki: getirilen mülga **2 → 0**, `data/index/mevzuat_bge_m3_s2/KUNYE.json` → `yururluk.olculen_etki`). Alan ya **ölçülsün** ya `None` bırakılıp süzgeç dışına alınsın |
| **5** | **Künye sözleşmesi bugünkü biçime çekilsin — plan kusur 32'yi YENİDEN ÜRETİYOR** | bugünkü sözleşme `_korpus_imzasi` (`scripts/erisim_korpus/retriever.py:94-104`): **{indekse göreli yol, bayt, sha256}**, `mtime` **kasten yok**. Plan iki yerde (satır 1001 ve 1961) `update(bayt=…, mtime=int(st.st_mtime))` yazıyor — **`G8 Adım 1b` onarımından ÖNCEKİ biçim**: `sha256` yenilenmiyor, `mtime` geri geliyor ⇒ sonraki `Retriever.yukle` **`SystemExit`** ile düşer. Gürültülü, sessiz değil — ama plan **çalışmayan kod** taşıyor. Ayrıca plan korpus için **ikinci bir künye dosyası** kuruyor (`mevzuat_maddeler.KUNYE.json`, plan satır 1341) — ürün `data/corpus/KUNYE.json`'u okuyor (`hakhukuk/cli.py:81`, `anlik_goruntu_tarihi`) ⇒ ayrışırsa **vatandaşın gördüğü tarih sessizce donar**. Tek dosyada birleştirilsin |
| **6** | **Kapının ÇÖZÜNÜRLÜĞÜ yazılsın** | `recall@10` **n=80**'de ölçülüyor ⇒ adım genişliği **1/80 = 0,0125** ve `0,9500 = 76/80`. `≥ 0,9500` eşiği **gürültü payı SIFIR** demektir: tek bir sorunun düşmesi 0,9375 verir ve kat **reddedilir**. Spec bunu hiçbir yerde yazmıyor. Dahası dayandığı çözünürlük sorusu — *"ikili oran çözünürlük sınırı"*, **S5** — hâlâ **AÇIK bir karardır**. Eşik `≥ 0,9500` mü, `≥ 76/80` mi, `≥ 75/80` (bir kalem gürültü payı) mı: **üçü farklı kapıdır** ve hangisi olduğu koşudan **önce** yazılmalı (tuzak 2.17'nin ikinci katmanı) |
| **7** | **Atıf doğrulayıcı ölçeğe karşı yeniden ölçülsün + `kanun_no = UUID` kararı geri alınsın** | tuzak 1.13'ün onarımı sağlam (`atif_dogrula` gevşek eşleşmede artık `AYRISTIRILAMADI` dönüyor), **ama tuzağın kendi cümlesi** şudur: *"temiz çıkmasının sebebi 114 atfın hiçbirinin parantezli adlı bir kanuna denk gelmemesidir — korunma aletten değil, ÖRNEKLEMDEN geliyor."* Kapsam 892 → ~9.700 belgeye çıkınca (a) sonek/parantez çakışma yüzeyi büyür, (b) `AYRISTIRILAMADI` artışı **`DOGRULANDI` paydasını küçültür** ve manşet `0/114` ile donmuş TEST `0/52` **kıyaslanamaz hâle gelir** (bu kesrin birimi zaten kusur 25'in konusudur). (c) Plan yeni satırlara **`"kanun_no": kayit.mevzuat_id`** yazıyor (plan satır 1911) — bedesten **UUID**'si kanun-numarası ad alanına giriyor; `hakhukuk/cli.py:180` atfı `{kanun_no}/{madde_no}` diye **vatandaş ekranına basıyor** ⇒ ekranda UUID. Spec `atif_dogrula`'dan **hiç söz etmiyor** |
| **8** | **Dokuz bayat satır damgalansın** | §1: *"korpusun güncellik tarihi YOK"* (`data/corpus/KUNYE.json` 2026-09-07'de eklendi, `anlik_goruntu_tarihi: 2026-08-06`, ürün basıyor) · *"`mulga` bayrağı retriever'da kullanılmıyor"* (2026-09-07'de kapandı) · *"800 kaynağın 2'si mülga"* (**0**'landı) · *"büyüme ~1,5×"* iki yerde (yalnız çekirdek katmanların **belge** sayısıdır; insan kararından sonra kapsam çok daha büyük) · *"340k'da ~51 ms"* tablosu ve onu savunan cümle (aynı bölümde **16× iyimser** diye düzeltilmiş, ~0,8 sn; tablo güncellenmemiş) · *"indeks ~120 MB"* (`CB_KARAR`/`KKY` eklendi ⇒ ölü) · aynı dosya için **79,1 MB ↔ 83 MB** (biri MiB biri MB, ikisi de "MB" etiketli; `gomme.npy` = **82.935.936 bayt**, `ls` 2026-09-12) |
| **9** | **İki isim/arayüz kararı yazılsın** | (a) plan `hakhukuk/mevzuat/tipler.py` içine **kendi `Durum` enum'unu** koyuyor (plan satır 503-507: `GUNCEL · TAZELENDI · IP_YOK · HATA`) — ürünün `hakhukuk/tipler.py` `Durum`'uyla (**altı üye**, ADR-0081) **aynı adda, aynı paket ağacında, farklı kapalı küme**. Plan bunu docstring'le uyarıyor ama **adı değiştirmiyor**; CLAUDE.md §7 *"isim yorum gerektiriyorsa yanlış isimdir"* ⇒ öneri **`TazelikDurumu`**. (b) `_gomulecek_metin` `retriever.py`'den **kopyalanıyor** — bu bir **karar** olarak yazılsın (*"S18 ayrışma riski kabul edildi, çünkü import **kusur 11**'i büyütürdü"*), docstring uyarısı olarak değil. Ayrıca planın `indeksle.py` başlığı *"Tüketir: `retriever.Retriever`"* diyor, kodu ise yalnız numpy kullanıyor — **başlık ile kod çelişiyor** ve başlığa göre uygulanırsa **kusur 11 büyür** |

Bağımlılık sırası (planın kendi grafiği; dokuz görev, 62 kutucuk):

```
G1 kapsam kapısının aleti + ÇIPASI   ← her şeyden ÖNCE (tuzak 2.17)
 ├── G2 kaynak.py (bedesten)                    ─┐
 ├── G3 korpus kimliği (mevzuat_id · madde_id)   │  G4 ile paralel
 └── G4 tipler + tazelik.py (saf, ağsız)        ─┘
        └── G5 anlik.py (atomik anlık görüntü + kayitTarihi sinyal testi)
              └── G6 indeksle.py (artımlı) + ÖLÇEK KAPISI
                    └── G7 kapsam kat kat girer      >$1 ⇒ DUR ve SOR
                          └── G8 tazele() ana arayüz + CLI
                                └── G9 ADR + kayıt + kapanış
```

**G1'in birinci olmasının tek sebebi** tuzak 2.17'dir: spec'in kapısı `recall@10 ≥ 0,9500`
diyor ama *"bu sayı hangi dosyada, hangi aletle, hangi birimde ölçüldü"* **spec'te yazılı
değil**. Plan bunu onarıyor — çıpa dosyası üretiliyor ve `recall_olc.py`'nin **`rrf_k=60`**
birim farkı açıkça reddediliyor (ürün `retriever.py:44` **`RRF_K = 10`**, ADR-0068).
Bu, planın en iyi görevidir ve **korunmalıdır**. Not: indeks künyesinde `rrf_k` bugün hâlâ
**60** yazıyor (`data/index/mevzuat_bge_m3_s2/KUNYE.json`) — künye kodla uyuşmuyor.

**G5 ve G6 bir kapı değil, gözlem taşır:** `kayitTarihi`'nin gerçekten bir **değişim sinyali**
olduğu **kanıtlanmadı** (100/100 benzersiz ama kümeleniyor; toplu yeniden alım da olabilir).
Testi *"`kayitTarihi` değişen belgenin metni de gerçekten değişmiş mi"* diye sorar ve
**çıkmazsa tasarım değişir** — o zaman içerik `sha256` karşılaştırması, yani **her belgeyi
indirmek** gerekir.

---

### E.6 · BÜTÇE GERÇEĞİ — mesele para değil, SIRA KARARI

| kalem | değer | kaynak |
| :--- | ---: | :--- |
| Modal bakiyesi | **$29,19** | [ADR-0066](0066-b1-yontemi-reddetme-orneklemesi.md) satır 49 |
| OpenRouter bakiyesi | **$2,041996** | `outputs/eval/g22-kv-fp16/KUTLE.md:147` |
| κ borcu (`3.5 Flash` kolu, aynı ikinci hakem) | **$2,81** | [ADR-0074](0074-hakem-paneli-kuruldu-baglayici-hukum.md) |
| **açık** | **−$0,77** | 2,041996 − 2,81 |

**Yazılı bedel koşulabilir.** G1-G6, G8, G9 **$0** (hakem yok, GPU yok); kapsam kapısının
her kattaki `recall@10` ölçümü **$0** — spec'in en iyi tasarım kararı budur. Gömme koşusu
**Modal**'dan ödenir ve bakiye yeter.

**Yazılmayan bedel koşulamaz.** İndeks değişince eşit sınav (ADR-0057) **yeniden kurulmak
zorundadır**: **~$1,35 (3 kol) … $2,5+ (5 kol)** — havuzda ADR-0072'den beri **beş** kol var
ve tek başına Sonnet-5 kolu **$1,1932** tuttu (ölçüldü, [#65](../record/research_log/2026-09-09-kabul-testi-ve-frontier-kiyasi.md);
tahmin $0,82 idi, tuzak 1.11). O fatura **OpenRouter**'dan ödenir ve bakiye zaten κ borcunu
karşılamıyor.

> **Bu bir *"önce para"* meselesi değil, *"önce SIRA"* meselesidir ve insan kararı ister:**
> **(a)** κ borcu ödenip `v1.0` kapatılana kadar bu iş **beklesin** (bugünkü sayılar korunur);
> **(b)** iş önce koşsun, ama *"yayımlanan kütle ve ADR-0057'nin eşit sınav kanıtı, korpus
> değiştiği anda **ASKIYA ALINIR**"* cümlesi tasarıma **kabul edilmiş bedel** olarak yazılsın.
> Bugün tasarım **ikisini de** söylemiyor.

Planın içinde ayrıca bir bütçe çelişkisi var ve grill'de kapatılmalı: DUR-SOR kapısı
*"Modal GPU ~1,5 sa, **>$1**"* diyor (plan satır 48 ve 1779) ama fiilî komutlar
`--cihaz cuda` ile **yerel RTX 5070'te** koşuyor (**$0**) ve planda **hiçbir Modal taşıyıcısı
yaratılmıyor**. Kapı, koşulmayacak bir harcamayı soruyor. Ayrıca *"~1,5 sa"* **340.303
maddenin** sayısıdır (65 madde/sn üzerinden) ama plan onu **kat 4-5'in 202.660 maddesine**
uyguluyor; gerçeği ~0,87 sa'dir — yön emniyetli, **tahmin gerekçesiz taşınmış**.

---

### E.7 · Ne KURULMAZ

- Bu bölüm silinen tasarım spec'inin **yerine geçmez**. Spec'in ölçüm tabloları, reddedilen
  seçeneklerin tam gerekçeleri, `fp16` reddinin ölçüm detayı ve bedesten sözleşmesinin tam
  alan listesi **taşınmadı**; burada yalnız **taşıyıcı tasarım** vardır.
- Bu bölüm *"tasarım onaylandı"* **DEMEZ**. Grill'in **girdisidir**; E.5'teki **dokuz madde
  AÇIK** durur ve grill'den önce hiçbiri kapatılmış sayılmaz.
- Bu bölüm bir **iş emri değildir**. E.6'nın sıra kararı **insan kararıdır** ve verilmemiştir.
- **Bedesten sayıları doğrulanmadı** — 917 `KANUN` · 4.361 `CB_KARAR` · 4.043 `KKY` ·
  `pageSize` max 20 · `guncellemeTarihi` 60/60 boş. Bunlar spec'in *"ölçüldü 2026-09-07,
  canlı sorgu"* kaydıdır; bu tur **$0 / ağsız** koştuğu için yeniden ölçülmedi —
  **çürütülmedi de**. Kat merdiveninin belge sayıları bu ölçüme dayanır.
- **Modal bakiyesi bugün doğrulanmadı**: $29,19 ADR-0066'nın 2026-08 tarihli kaydıdır.

---

## EK-2 — model kartından çıkarılan ÖLÇÜM AÇIK SORULARI (2026-09-13)

`MODEL_CARD.md` 2026-09-13'te akademik/manuel forma yeniden yazıldı (insan kararı: kart
yürürlükteki hâli anlatır, onarım günlüğü tutmaz). Kartın *"Açık sorular"* bölümü **dışa
dönük belgede durmamalı** diye çıkarıldı; içeriği **kaybolmasın diye** buraya alındı.

⚠️ **Burada ölçüm bedeli olan bir şey var:** 1. maddedeki Wilson aralıkları **kartın içinde
hesaplanmıştı** (`z=1,96`, `n=80`) ve başka hiçbir dosyada yoktu. Kart silinseydi bu sayılar
kaybolacaktı.

**1 · Set küçük ve dar: `n=80`, tek dil, tek alan.**

| oran | nokta tahmin | Wilson %95 | genişlik |
| :--- | ---: | :--- | ---: |
| **isabetsizlik 8/80** | 0,1000 | **[0,0515 – 0,1851]** ≈ **[4/80 – 15/80]** | **13,4 puan** |
| aşırı-red 4/80 | 0,0500 | [0,0196 – 0,1216] ≈ [2/80 – 10/80] | 10,2 puan |

⇒ *"8/80 ↔ 6/80"* gibi farklar bu genişliğin **çok altındadır**. Aynı sınıfta ölçülmüş ikinci
örnek: M2'nin kuantumu `1/66 = 1,52 puan`, yani `+0,000` ile `±1 kalem` **ayırt edilemiyor**
([#59](../record/research_log/2026-08-06-m2-paydasi-ve-karar-4.md)).
**Soru:** kaç kalem, hangi çeşitlilikte yeterlidir? (İkili oranların çözünürlük sınırı açık
karar **S5**; ilgili kusur **5a** bu ADR'nin §(A) sicilinde açık.)

**2 · DEV ile TEST aynı sınav değil.** Ayrım kanuna göre kusursuz katmanlı (2:1) ama **madde
uzunluğuna göre katmanlanmamış**; bileşim farkın **%81**'ini açıklıyor
([ADR-0069](0069-kabul-testi-tavan-kullanimi-raporlamasi.md)). Yeniden katmanlama ADR-0069'da
*"donmuş TEST'i açar, usulü kırar"* diye **reddedilmişti**. **Soru:** ayrım uzunluğa göre de
katmanlanmalı mı — ve bu, donmuş TEST'i açmadan nasıl yapılır?

**3 · Her sayı tek hakem ailesinin hükmü.** Üç aileli panel
([ADR-0032](0032-hakem-paneli-uc-aile-ve-aile-dislama.md)) hiç kurulmadı; genişleme rakip
havuzunun da ön koşulu ([ADR-0072](0072-v1-rakip-havuzu-genisler.md), açık karar **S16**).
**Soru:** κ hangi eşiğin altında kalırsa kartın sayıları yeniden koşulur?

**4 · Manşet ölçüt bir çarpım:** `kütle = coverage × A1`. İki çarpan **farklı örnekleme
birimlerinden** gelir — `coverage` **kalem** başına (80 kalem), `A1` **iddia** başına ve yalnız
cevaplanan kalemler üzerinden makro ⇒ çarpıma ikili bir güven aralığı **doğrudan uygulanamaz**.
Aynı sebep `v1.0` kapısının δ'sının **ölçümden değil insan kararından** gelmesinin
gerekçesidir: gürültü tabanı (0,3 puan) yalnız `A1` için ölçüldü, `coverage`'ın varyansı o
tabanda yok ([ADR-0064](0064-v1-kapisi-uc-maddeli-on-kayit.md) §δ). **Soru:** kütle için
savunulabilir bir belirsizlik ifadesi (bootstrap? kalem-başına birleşik skor?) kurulmalı mı?

**5 · Dış karşılaştırılabilirlik yok.** Sayılar kendi CANON setimizde üretiliyor ve **kimse bu
sette koşamaz**. Dış benchmark'lara gitmemek [ADR-0016](gemma4-12b-dersler.md#adr-0016)'nın
kayıtlı kararı ve gerekçesi sağlam, ama bedeli **doğrulanabilirliktir**. **Seçeneklerden biri**
— karar değil — CANON'un kamuya açık bir alt kümesini yayımlamak. Bedeli de ölçülü: donmuş
TEST bir **kabul testidir**, yayımlanması onu yakar; DEV ise **seçim yapılmış** settir.

**6 · Yer-gerçeği denetimi.** Üç kolda da **sınır durum** sayıldı ve hiçbirinde sayıya
katılmadı ⇒ üç isabetsizlik sayısı da **alt sınırdır**. Etiketler **değiştirilmedi**: sonucu
gördükten sonra yer-gerçeğini oynatmak [ADR-0067](0067-soru-onarimi-dev-test-v2.md)'nin
yanlılık korumasının doğrudan ihlalidir. **Soru:** yer-gerçeği denetimi ayrı, **kör** ve
koşudan **önce** yapılan bir adım olmalı mı?

**7 · Ölçüm aleti hâlâ onarım altında.** Faz 0'da beş alet kusuru bulundu ve **hiçbiri sayısal
kapıya takılmadı**; dedektör üç kez yanıldı ve `exact_reject`'in **kör mod dalı açık borç**.
**Soru:** *"gözle okuma"* kalıcı bir kapı mı, yoksa aletin olgunlaşmasıyla azalması beklenen
bir maliyet mi?
