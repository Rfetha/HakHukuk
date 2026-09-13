# HakHukuk

> **Türkçe bir hukuk asistanı: dizüstünde koşacak kadar küçük, "bu kaynaklarda yok" demeyi öğrenmiş 4B'lik bir model.**
> Açık kaynak **ürün** — ağırlık + kod + veri + **araştırma kaydının tamamı**. Tez değil.

[Model kartı](MODEL_CARD.md) · [English](README.md) · [Yol haritası](ROADMAP.md) · [İş sırası](docs/superpowers/00-IS-SIRASI.md) · [Hugging Face'te ağırlıklar](https://huggingface.co/Rfetha/HakHukuk-4B-GGUF) · [Lisans](LICENSE)

## Ağırlıklar

> ~~**Not (2026-09-09):** ağırlık deposu, açık kusurlar giderilene kadar geçici olarak **özeldir**. Aşağıdaki bağlantı yeniden herkese açılana dek 404 verecektir.~~ → **2026-09-13'te PUBLIC yapıldı** (`v1-son-iş` turunun 9. adımı, kusur 10 kapandı — [ADR-0083](docs/adr/0083-kusur-sicili-adrye-tasindi.md)). Token'sız bir alt süreçle doğrulandı: `sha256` bayt bayt tuttu.

2026-09-09'da yayımlandı: [`Rfetha/HakHukuk-4B-GGUF`](https://huggingface.co/Rfetha/HakHukuk-4B-GGUF) — tek GGUF,
`HakHukuk-4B-v0.3-Q4_K_M.gguf`, 2.783.446.720 bayt (2,592 GiB),
`sha256 755e15e92e9f7021934f2d5eada6c1f02fcc92be23f0536b0c2a0a9586e7bffc`.

```bash
hf download Rfetha/HakHukuk-4B-GGUF HakHukuk-4B-v0.3-Q4_K_M.gguf --local-dir models/gguf
```

Kullanmadan önce oradaki model kartı okunmalıdır. İki kısıt kartın ilk ekranında
bildirilmiştir: model tek başına bildirilen başarımı üretemez (arama indeksi henüz
dağıtılmamıştır) ve ürün yolu **80 sorunun 4'ünde** boş cevap döndürüyordu — kaydedilmiş,
gizlenmemiş bir sonlanmama kusuruydu. **2026-09-11'de giderildi**
([ADR-0080](docs/adr/0080-urun-yolu-zorunlu-dusunce-kapatmasi.md)): ürün yolu artık düşünce
kanalını ikinci geçişte zorla kapatıyor; boş cevap **4/80 → 0/80**, kesiklik %8,75'ten %3,75'e
indi. ⚠️ Onarım `hakhukuk/servis.py` içindedir — `llama-server`'ı bu paket olmadan doğrudan
süren biri **özgün kusuru yaşamaya devam eder**. Örnek çıktılar aynı depodaki `ORNEK_CEVAPLAR.md`
dosyasındadır.

Bir hukuk asistanının işinin büyük kısmı cevap vermek değil, **kaynak desteklemiyorken
cevap vermemektir.** Kendinden emin ve yanlış bir madde numarası sessizlikten kötüdür —
bir hukuk aracını tehlikeli yapan hata biçimi budur. `HakHukuk-4B-v0.1` (iç ad `tgta_v1`)
bu işin iki yarısı için de eğitildi: cevabı verilen mevzuata **dayandır**, mevzuat soruyu
kapsamıyorsa **çekin**.

**Kime hitap ediyor:** hukukçu olmayan Türk vatandaşı (ürün hedefi) · Türkçe hukuk NLP'si
üzerine çalışan araştırmacı (kayıt hedefi).

---

## Bugün kurup çalıştırabilir miyim? — **KISMEN**

İlk sorunun dürüst cevabı budur ve 2026-09-11'de değişti: **ürün artık koşan kod olarak
vardır.** Eksik olan şey **dağıtımdır** — aşağıdaki dört parçanın ikisi henüz bir yabancıya
teslim edilebilir durumda değildir.

| parça | durum | kanıt (ölçüldü, 2026-09-12) |
| :--- | :--- | :--- |
| Model ağırlıkları (Q4_K_M GGUF, **2,59 GiB**) | 2026-09-09'da **yayımlandı**, depo **2026-09-13'ten beri PUBLIC** — `HF_TOKEN` gerekmez | `Rfetha/HakHukuk-4B-GGUF`, tek dosya, **2.783.446.720 bayt**, `sha256 755e15e9…86e7bffc`. Kimlik kapısı [`hakhukuk/indir.py`](hakhukuk/indir.py)'dir (`GGUF_SHA256` · `GGUF_BAYT`) ve konteyner koşusunda **ateşlendi ve tuttu** · [ADR-0071](docs/adr/0071-v1-release-artefakti-tek-gguf.md) |
| Erişim indeksi (**40.496** madde) | **tek gerçek tıkaç.** Yerelde var, **git'te yok** ve **hiçbir yerde yayımlanmadı**: dağıtım kararı verildi (HF dataset) ama **koşulmadı**, çünkü korpus 8,4× büyümek üzere | `git ls-files data/index` → **2 `KUNYE.json`, başka hiçbir şey**; `du -sh data/index/mevzuat_bge_m3_s2` → **80 MB**. İki yollu indeks (önce volume, sonra HF) [ADR-0078 madde 4](docs/adr/0078-konteyner-dagitimi-rejim-kilidi.md)'tür; ikisi de yoksa `indir` **kasten** sıfırdan farklı kodla çıkar ve tam yolu yazar |
| Servis katmanı (API / CLI / TUI) | **kod olarak var ve çalışıyor.** `pip install -e .` üç komut üretir; konteyner yolu uçtan uca gerçek soru cevapladı | `git ls-files hakhukuk/` → **11 dosya** (`cli.py` · `tui.py` · `api.py` · `servis.py` · `araclar.py` · `terazi.py` · `istem.py` · `tipler.py` · `indir.py`) · [`pyproject.toml`](pyproject.toml) `[project.scripts]` → `hakhukuk` · `hakhukuk-tui` · `hakhukuk-api` · `pytest tests/` → **281 passed, 2 xfailed** |
| İstem (prompt) | **dağıtılabilir artefakt**; artık ölçüm script'lerinin içindeki bir kopya değil: [`hakhukuk/istem.py`](hakhukuk/istem.py) **tek kaynaktır** | ölçüm hattı da onu içe aktarır (`scripts/olcum_uretim/gen_eval_grounded.py:55` → `from hakhukuk.istem import …`); [`tests/test_istem.py`](tests/test_istem.py) bir kapıdır — metni `ISTEM_SURUMU` / `DAMGA_v1` yükseltmeden değiştirirsen düşer |

**Yani tek başına `git clone` çalışan ürün ELDE ETMEZ.** İndeks içinde değildir ve bu durumda
`indir` **kasten** patlar; vatandaşa yarım kurulmuş bir erişim katmanı sunmaz. Bir `HF_TOKEN`
ve kendi indeks dizininizle aşağıdaki konteyner yolu koşar.

**Ve `0,8011`'i yeniden üretmez.** O sayı **ölçüm hattınındır**; konteyner **ürün yolunu**
taşır (aşağıya bakın). Paketlemenin kendisi bitmiştir: **ürün sürümü `v1.0`**'dur
(2026-09-13'te etiketlendi, [`pyproject.toml`](pyproject.toml)), model artefaktı ise hâlâ
`HakHukuk-4B-v0.1`'dir — sürümleme bilerek bölünmüştür
([ADR-0065](docs/adr/0065-bolunmus-surumleme.md)). ⚠️ **`v1.0` "model iyileşti" DEMEZ** —
ağırlıklar hiç değişmedi (`sha256` `v0.3` ile birebir aynı). Kapanan şey, kapının üç
maddesinin **ikinci, bağımsız bir hakem ailesi altında da** yeniden okunup GEÇMESİdir
([ADR-0084](docs/adr/0084-kappa-borcu-kapandi-kapi-yeni-birimde-gecti.md)); κ'nın kendisi
**değişmedi** (`0,534`/`0,409`, aracın `0,6` eşiğinin hâlâ altında) ve hakem paneli hâlâ
**iki** aileli, üç değil (ADR-0032). Kapanan ve kapanmayan her şeyin tam dökümü
[`MODEL_CARD.md`](MODEL_CARD.md) §5'te.

→ **Konteyner yolu:** [`docker compose up`](#konteynerle-çalıştırma--docker-compose-up).
**Uçtan uca DOĞRULANDI 2026-09-11:** `indir` **çıkış 0** ile bitti, `llama` **healthy** oldu,
`app` ayağa kalktı, API **iki farklı soruyu** HTTP **200** ile cevapladı ve boş sorgu **422**
döndü ([kayıt #67](docs/record/research_log/2026-09-12-konteyner-ve-alet-onarimlari.md)).

---

## Konteynerle çalıştırma — `docker compose up`

> ✅ **UÇTAN UCA DOĞRULANDI — 2026-09-11.** `docker compose up` **koştu**: `indir` kutusu
> **çıkış 0** ile bitti (`sha256` + bayt kapısı **ateşlendi ve tuttu**), `llama` **healthy**
> oldu, `app` ayağa kalktı ve API **iki farklı soruyu** HTTP **200** ile cevapladı; boş sorgu
> **422** döndü. İmaj **ölçüldü** (tahmin değil): `hakhukuk:0.3.0` **2,13 GB** ·
> `llama.cpp:server-cuda-b10902` **6,99 GB** · imajdaki `torch` **`2.14.0+cpu`**
> (CUDA tekerleği çekilmemiş). Ağırlık ve indeks **imajda YOK**.
> Ölçüm: [`g20-imaj-olcumu/BULGU.md`](outputs/eval/g20-imaj-olcumu/BULGU.md).
>
> ⚠️ **Üç şerh, hiçbiri giderilmedi.** (1) `git clone` sonrası **indeks dizinini insan
> doldurmak zorunda** — `G8` bekletiliyor, indeks ne HF'te ne imajda; `indir` bu durumda
> **kasten patlar** ve tam yolu **ve** derinlik şartını yazar. (2) Korpus artık **üç yerde**
> (repo · imaj · volume); `indir` imaj↔volume `sha256` eşitliğini **her koşuda sınar**, ama
> repo↔imaj ayrışması **sınanmaz**. (3) Uçtan uca doğrulama **iki soru** ile yapıldı; ürün
> yolunun bilinen **boş cevap** kusuru (§7.9) bu koşuyla **ölçülmedi**.

Üç kutu, iki daemon, iki imaj
([ADR-0078](docs/adr/0078-konteyner-dagitimi-rejim-kilidi.md) ·
[ADR-0082](docs/adr/0082-app-kutusu-host-sapmasi.md)): GGUF'u **pinlenmiş revizyondan**
`sha256` + bayt sayısı kapısının arkasından çeken tek seferlik `indir` kutusu, GPU'daki `llama`
daemon'u ve CPU'daki `app` daemon'u. Kapı tutmazsa `indir` sıfırdan farklı kodla çıkar ve
**iki daemon da hiç başlamaz**.

```bash
export HF_TOKEN=...                # 2026-09-13'ten beri OPSİYONEL — ağırlık deposu artık PUBLIC
export HAKHUKUK_INDEKS_DEPO=...    # aşağıya bakın — varsayılanı bilerek BOŞ
docker compose up
```

| | |
| :--- | :--- |
| API | `127.0.0.1:8000` |
| `llama-server` | `127.0.0.1:8080` |
| `HF_TOKEN` | **opsiyonel.** [`Rfetha/HakHukuk-4B-GGUF`](https://huggingface.co/Rfetha/HakHukuk-4B-GGUF) **2026-09-13'ten beri public**; tanımsız kalması yalnız hız sınırını düşürür, hata vermez |
| `HAKHUKUK_INDEKS_DEPO` | **bilerek boş.** `G8` (indeks dağıtımı) bekletiliyor ⇒ **yayımlanmış indeks deposu yok**. İndeks ya volume'e elle konur ya depo adı verilir; aksi hâlde `indir` kutusu **kasten** patlar |
| gereksinim | NVIDIA GPU + Docker. Ölçülen ortam: Docker **28.4.0** · compose **v2.39.4-desktop.1** · RTX 5070 Ti Laptop **12227 MiB** · sürücü **591.97**. `gpus: all` anahtarı compose **v2.30+** ister |
| imaj etiketi | `hakhukuk:1.0.0` — bu **ürünün** sürümüdür ([`pyproject.toml`](pyproject.toml)). Model artefaktı hâlâ `HakHukuk-4B-v0.1`'dir: sürümleme **bölünmüştür** ([ADR-0065](docs/adr/0065-bolunmus-surumleme.md)) |

**İki daemon da yalnız host'un `127.0.0.1`'ine yayımlar.** Kimlik doğrulama ve hız sınırı
**yoktur**: bu yerel ve tek kullanıcılık bir kurulumdur; barındırma `S9` olarak açık durur.

### Konteyner yayımlanan `0,8011`'i **ÜRETMEZ**

`0,8011` **ölçüm hattının** sayısıdır: harness AÇIK, `k=10`, önsözsüz, iki geçişli zorunlu
düşünce kapatması, `q8_0` KV önbelleği. Konteyner **ürün yolunu** taşır. Ürün yolu
2026-09-11'de ölçüm hattının rejimine geldi
([ADR-0080](docs/adr/0080-urun-yolu-zorunlu-dusunce-kapatmasi.md)) ve boş cevap
**4/80 → 0/80** oldu — ama **kütlesi ölçülmedi** ve `0,8011` **ürün yolunun sayısı değildir**
([karşılaştırma](outputs/eval/g22-rejim/KARSILASTIRMA.md)).

### Bayraklar bir **karardır**, tercih değil

KV önbelleğinin `q8_0` kuantizasyonu bir insan kararıdır (2026-09-11): fp16 KV'de
`wrong_ref_rate` **0,0769 → 0,1553 (2,0×)** kötüleşir
([ölçüm](outputs/eval/g22-kv-fp16/KUTLE.md)). [`compose.yaml`](compose.yaml) bu bayrakları
**zorlar**; `llama-server`'ı elle açan kişi onları **kendi** yazmak zorundadır
([MODEL_CARD §7.10](MODEL_CARD.md)).

---

## Manşet sayılar

**Rejim:** DEV kümesi, `n=80` · harness **AÇIK** (hibrit BM25 + `bge-m3`, `k=10`,
`RRF_K=10`, tamamı CPU'da) · **önsözsüz** · seed 3407 · 900 karakter klip ·
üretim bütçesi **1536** · hakem `openai/gpt-4o-mini`.

| eksen | değer | kaynak dosya |
| :--- | ---: | :--- |
| **sadık-cevap kütlesi** | **%69,4-80,1** (`claude-sonnet-5` ↔ `gpt-4o-mini`) | [`outputs/eval/f02-biz-onsozsuz/KUNYE.json`](outputs/eval/f02-biz-onsozsuz/KUNYE.json) · [ADR-0084](docs/adr/0084-kappa-borcu-kapandi-kapi-yeni-birimde-gecti.md) |
| `coverage` | 0,9375 | aynı künye |
| A1 · cevaplanan | 0,8545 | aynı künye |
| A1 · altın getirilen alt küme | 0,8902 | aynı künye |
| `recall@10` | 0,9500 | aynı künye |
| **uydurulmuş madde numarası** | **0 / 114** | aynı künye |
| aşırı-red (altın bağlamdayken sustu) | **4 / 80** | aynı künye |
| isabetsizlik (*başka bir gerçek maddeden* cevapladı) | **8 / 80** — **gözle tam tarama** | [`outputs/eval/f02-biz-onsozsuz/GOZLE_OKUMA_80.md`](outputs/eval/f02-biz-onsozsuz/GOZLE_OKUMA_80.md) |
| kesik kalem | 4 / 80 (%5,0 — geçerlilik eşiği tam sınırda) | aynı künye |
| ortalama completion token | 782,5 | [`outputs/eval/f04-rakip-onsozsuz/KALIBRASYON_ve_OZET.md`](outputs/eval/f04-rakip-onsozsuz/KALIBRASYON_ve_OZET.md) |
| VRAM (ctx 4.096 / 32.768 / 131.072) | 3,09 / 3,70 / 5,76 GiB | `outputs/eval/_artefakt/vram_stack_tgta_v1.json` ([ADR-0071](docs/adr/0071-v1-release-artefakti-tek-gguf.md)) |

⚠️ **Manşet, sonuç görüldükten sonra seçilmiş tek bir sayı değil, koşulsuz bir aralıktır.**
İki bağımsız hakem ailesi aynı 80 cevabı puanladı — `gpt-4o-mini` (0,8011) ve `claude-sonnet-5`
(0,6940) — ve ikisi de yan yana raporlanıyor
([ADR-0084](docs/adr/0084-kappa-borcu-kapandi-kapi-yeni-birimde-gecti.md)); manşeti sonuca göre
biçimlendirmek (kapı geçince tek sayı, emin olmayınca aralık) bu projenin reddettiği bir
kendini-kandırma kalıbıdır. Yukarıdaki diğer satırlar hâlâ yalnız `gpt-4o-mini`'nindir. Üç
rakip kolu **tek hakemli** kalır ve aşağıdaki kıyas tablosunda **öyle damgalanır** (ADR-0057) —
ortaya çıkan asimetri **bilinçlidir**.

**Harness KAPALI ("tavan") rejimi bu birimde YENİDEN ÖLÇÜLMEDİ.** Eski `v1` birimindeki
tavan sayısı bugünküyle kıyaslanamaz ve bu belgede tekrarlanmıyor.

---

## Rakip kıyası — **eşit sınav**, üç okuma

Aynı 80 soru, aynı bağlam, aynı bütçe, aynı hakem. **Eşitlik varsayılmadı, ölçüldü:**
dört öznede de `recall@10` = **0,9500** ve `context_shown` **80/80 bayt-bayt aynı**
([`f04-rakip-onsozsuz/KALIBRASYON_ve_OZET.md`](outputs/eval/f04-rakip-onsozsuz/KALIBRASYON_ve_OZET.md)).

Zorunlu kalibrasyon adımı (28 rakip çekinme kalemi gözle okundu) çekinme dedektörünün
**Gemini şablonunda fazla red saydığını** buldu — yani üstünlüğümüzün bir kısmı aletin
eseriydi. Aşağıdaki üç okuma bunu düzeltiyor; **bağlayıcı olan en muhafazakârı: GÖZ-katı**
([ADR-0064](docs/adr/0064-v1-kapisi-uc-maddeli-on-kayit.md)).

| sadık-cevap kütlesi | ALET (ham) | GÖZ-orta | **GÖZ-katı (bağlayıcı)** |
| :--- | ---: | ---: | ---: |
| **HakHukuk-4B-v0.1** | **0,8011** | **0,8011** | **0,8011** |
| Gemini 3.1 Flash-Lite | 0,6746 | 0,7058 | 0,7058 |
| Gemini 3.5 Flash-Lite | 0,7174 | 0,7403 | 0,7622 |
| Gemini 3.5 Flash | 0,6925 | 0,7050 | 0,7425 |

*(Bizim kolumuz üç okumada da aynı: 80 kalem gözle okundu, **alet ↔ göz farkı sıfır**.)*

Diğer eksenler (ham alet sayıları, aynı dosya):

| eksen | BİZ | 3.1 FL | 3.5 FL | 3.5 Flash |
| :--- | ---: | ---: | ---: | ---: |
| A1 · altın getirilen | **0,8902** | 0,7900 | 0,8449 | 0,8523 |
| **uydurulmuş madde** | **0** | 1 | 4 | 4 |
| kesik kalem | 4 (%5,0) | 5 (%6,2) | 0 | 4 (%5,0) |
| ort. completion token | 782,5 | 861,5 | **171,1** | 699,4 |

### Bu tablodan **kurulmayan** cümleler

1. **"TEST'te de geçeriz."** Ölçüm **DEV**'de. Donmuş TEST'in erişim tavanı ≈%75
   ([ADR-0069](docs/adr/0069-kabul-testi-tavan-kullanimi-raporlamasi.md)) ve kabul testi
   **koşulmadı**.
2. **"Üç aileli tam bir hakem panelinden geçmiş bir hüküm."** İki aile artık **aynı yönde**
   hükmediyor (`gpt-4o-mini` ve `claude-sonnet-5`,
   [ADR-0084](docs/adr/0084-kappa-borcu-kapandi-kapi-yeni-birimde-gecti.md)), ama uyumun
   kendisi (κ) **zayıf ve değişmedi** (0,534 / 0,409, aracın 0,6 eşiğinin altında) ve üçüncü
   aile (Google) bütçe nedeniyle hiç eklenmedi — kayıtlı bir eksiklik, gözden kaçma değil.
   Öz-tercih **yalnız Anthropic ailesi için** ölçüldü ve **ters yönde** çıktı (hakem kendi
   ailesini bizden daha sert cezalandırdı). İkisi de manşeti "panelden geçti" seviyesine
   çıkarmıyor — bu hâlâ açık bir borç.
3. **"Model bu kadar iyileşti."** Kazancın büyük kısmı eğitimden değil **ölçümden** geldi
   (aşağı bak).

---

## Kazanç nereden geldi: **ağırlıklar hiç değişmedi**

Faz 0'da **tek bir eğitim koşusu yapılmadı** ve sayı %68,4'ten **%80,1**'e çıktı.
Bulunan şey model değil, **ölçüm aletinin kusurlarıydı** — beşi de *"hata vermeden yanlış
sayı üretir"* sınıfından, beşi de **sayısal kapıdan geçmişti** ve ancak **gözle okuma** ya da
künyeyi açıp okumakla yakalandı.

| # | kusur | etkisi | kaynak |
| :-- | :--- | :--- | :--- |
| 1 | Soruların **bağlamı sökülmüştü** — 5/10 erişim ıskası aslında soruyu tek başına okuyanın altın maddeyi adlandıramamasıydı | `recall@10` 0,8750 → **0,9375** | [ADR-0067](docs/adr/0067-soru-onarimi-dev-test-v2.md) |
| 2 | Kusur BM25'te değil **füzyondaydı**: `RRF_K=60`, "iki kolda vasat"ı "bir kolda mükemmel"e tercih ediyordu | `RRF_K` 60 → 10; `recall@10` 0,9375 → **0,9500** | [ADR-0068](docs/adr/0068-rrf-k-60-to-10.md) |
| 3 | DEV ↔ TEST farkının **%81'i set bileşiminden** (madde uzunluğu katmanlanmamış) | kabul testinin tavanı ≈**%75** olarak ön-kayıtlandı | [ADR-0069](docs/adr/0069-kabul-testi-tavan-kullanimi-raporlamasi.md) |
| 4 | **Üretim bütçesi rakiple eşit değildi ve aleyhimizeydi** — biz 1024, rakip fiilen 1532 | tek formüle geçildi: bütçe **1536**, dört öznede aynı | [ADR-0070](docs/adr/0070-uretim-butcesi-esitlendi.md) |
| 5 | **Kapı maddesinin ÇIPASI YOKTU** — `v1.0` kapısı madde (3) *"M5 ≤ bugünkü"* diyordu, ama `tgta_v1`'in M5'i **hiçbir birimde hiç ölçülmemişti**; madde kendi kendine referans veriyordu | çıpa ADR-0039'dan okundu (**base**, rakip değil), M5 iki kolda birden yeniden koşuldu | [ADR-0073](docs/adr/0073-m5-rejimine-dry-eklendi.md) · tuzak **2.17** |

*(Bu beşi **Faz 0'ın** bulgusudur. Altıncı bir alet kusuru **bir gün önce**, B10 turunda
bulunmuştu: çekinme dedektörü istem rejimine bağımlı çıktı ([ADR-0061](docs/adr/0061-cekinme-dedektoru-istem-rejimi-bagimliligi.md),
[#61](docs/record/research_log/2026-09-06-dedektor-onarimi-b10-yeniden.md)). Onun **rakip
tarafındaki** yansıması Faz 0 içinde ölçüldü — F0.4 kalibrasyonunda rakip kollarında **6 açık
yanlış pozitif**, bizim kolda **0**; bu yüzden bağlayıcı okuma **en muhafazakâr** olan seçildi
([`f04 kalibrasyonu`](outputs/eval/f04-rakip-onsozsuz/KALIBRASYON_ve_OZET.md)). Ve aynı dedektör
2026-09-07'de **üçüncü** kez yanıldı, bu kez kör modda: 6 işaretin **6'sı da yanlış pozitif**.)*

Tam anlatı: [`research_log #62`](docs/record/research_log/2026-09-06-faz0-olcum-zinciri.md)

---

## `v1.0` kapısı — üç madde, ön-kayıtlı formül

Formül **rakip sayıları görülmeden** yazıldı; sayılar mekanik olarak türedi
([ADR-0064](docs/adr/0064-v1-kapisi-uc-maddeli-on-kayit.md)).

| madde | hüküm | sayı | kaynak |
| :--- | :--- | :--- | :--- |
| **(1)** kütle ≥ 3.5 Flash − 2,0 puan | **GEÇTİ** | GÖZ-katı: **0,8011 ↔ eşik 0,7225** → **+5,86 p** | [`f04 özeti`](outputs/eval/f04-rakip-onsozsuz/KALIBRASYON_ve_OZET.md) |
| **(2)** isabetsizlik gerilemez | (bugün tanım gereği) | çıpa yeni birimde **8/80**'e çivilendi; bağlayıcı olduğu yer **sonraki eğitim turu** | [`GOZLE_OKUMA_80.md`](outputs/eval/f02-biz-onsozsuz/GOZLE_OKUMA_80.md) |
| **(3)** M5 (kör/parametrik) **yükselmez** — anti-hedef | **GEÇTİ** | ezber kütlesi **0,3899 ↔ base 0,4697** (ALET) · **0,4057 ↔ 0,4739** (GÖZ) | [`outputs/eval/f07-m5-anti-hedef/KUNYE.json`](outputs/eval/f07-m5-anti-hedef/KUNYE.json) · [`GOZLE_OKUMA_CEKINME.md`](outputs/eval/f07-m5-anti-hedef/GOZLE_OKUMA_CEKINME.md) |

**2026-09-12'de ikinci, bağımsız bir hakem ailesi altında yeniden okundu**
([ADR-0084](docs/adr/0084-kappa-borcu-kapandi-kapi-yeni-birimde-gecti.md)): ADR-0074'ün tek
cümlelik koşulu (`3.5 Flash`'ın aynı ikinci hakemle — `claude-sonnet-5` — puanlanması)
karşılandı ve kapının üç maddesi **yeniden GEÇTİ** — marj çıpaya göre **+7,57 p** (madde 1).
κ'nın kendisi **değişmedi** (hâlâ 0,534 / 0,409, 0,6 eşiğinin altında) — kapanan şey κ değil,
**eşit sınavın yokluğuydu**. Bu hâlâ `v1.0` **değildir**.

**Sürüm yine de `v0.1`.** Sürümleme bilerek ikiye ayrıldı
([ADR-0065](docs/adr/0065-bolunmus-surumleme.md)): **ürün sürümü** `v0.2 → v1.0` ürünün kendi
kapısından geçer; **iddia sürümü** ise 2026-08-06'da **düşen ARA KAPI'ya** bağlı kalır
([ADR-0045](docs/adr/0045-ara-kapi-merge-onarim-kontrolu.md)). Düşmüş kapı düşmüş kalır;
gevşetilmedi, yeniden tanımlanmadı.

---

## Ne vaat **etmiyor**

- **Hukuki tavsiye değildir.** Avukat değildir; çıktısı hukuki tavsiye yerine geçmez.
  Ürettiği her madde numarasını [mevzuat.gov.tr](https://www.mevzuat.gov.tr) üzerinden doğrulayın.
- **%100 doğruluk değildir.** 80 soruluk DEV kümesinde **8 isabetsizlik** ve **4 aşırı-red**
  ölçüldü (yukarıdaki tablo). Ölçüm **tek hakem ailesinin** hükmüdür.
- **Güncellik ağırlıkta değil, kütüphanededir.** Mevzuat değişir, ağırlıklar değişmez;
  güncellik erişim (RAG) katmanının işidir. Bu bir tasarım kararıdır, eksiklik değil.
- **Kapsam: yalnız güncel Türkiye Cumhuriyeti mevzuatı.** Osmanlı dönemi, içtihat yorumu
  ve yabancı hukuk kapsam dışı.
- **Parite iddiası yok.** Yukarıdaki kıyas **DEV**'de, tek hakem ailesiyle, maliyet
  normalize edilmeden yapıldı.

---

## Nasıl kuruldu

```
ham base ──┬── LoRA SFT   (dayanaklandırma) → τ_g
           └── LoRA ORPO  (çekinme)         → τ_a
                                              │
              eşzamanlı 2-yollu ham TIES ─────┘  → HakHukuk-4B-v0.1 (tgta_v1)
```

Birbiriyle **fiilen çatışan** iki beceri: dayanaklandırma için eğitmek çekinmeyi çökertiyor,
çekinme için eğitmek dayanaklandırmayı çökertiyor. **Hiçbir kol tek başına kullanılabilir
değil**; merge ikisini de geri getiriyor. Her kol **ham base'den bağımsız** eğitilir — görev
vektörü tanımı (`τ = θ_ft − θ_base`) bunu zorunlu kılar.

Bu bölümdeki oranlar **eski (`v1`) birimde** ölçüldü ve yukarıdaki manşet sayılarla
kıyaslanamaz; kol kol dökümü ve künyeler: [`docs/record/kollar.md`](docs/record/kollar.md).

---

## Yol haritası

Sırası **bağlayıcıydı** (insan kararı 2026-09-07). O tur 2026-09-12'de **115/115** kapandı ve
planı silindi; kusur sicili ile devir tablosu
[ADR-0083](docs/adr/0083-kusur-sicili-adrye-tasindi.md)'te, sıradaki iş
[iş sırası](docs/superpowers/00-IS-SIRASI.md) dosyasındadır:

| faz | ne | çıktı |
| :--- | :--- | :--- |
| **`HP`** — hakem paneli | ikinci + üçüncü hakem ailesi, κ, öz-tercih ölçümü | her sayı tek ailenin hükmü olmaktan çıkar |
| **Hat A** — paketleme (`HP`'ye paralel) | `hakhukuk/` paketi: istem artefaktı · tipler · servis · CLI · TUI · indeks dağıtımı | **kurulabilir ürün** |
| **Faz C** — belge katmanı | [`PRODUCT.md`](PRODUCT.md) · [`ROADMAP.md`](ROADMAP.md) · [`TODO.md`](TODO.md) · [`docs/MIMARI.md`](docs/MIMARI.md) — yazıldı 2026-09-07 | **`v0.2` YAYIN** |
| **Hat B** — model | B1 (isabetsizlik) · `τ_a` genliği · kapı koşusu + donmuş TEST kabul testi | **`v1.0` kapısı** |

`v2` = bu modelin üstündeki uygulama/API katmanı. arxiv bir **yan üründür**, hedef değildir.

---

## Repo haritası

| yer | ne |
| :--- | :--- |
| [`hakhukuk/`](hakhukuk/) | **ürün paketi** — istem · tipler · terazi · servis · CLI · TUI · HTTP API · indirici (git'te 11 dosya) |
| [`scripts/`](scripts/) | **ölçüm aleti** (üründen ayrı, bilinçli). Beş alt klasör: [`egitim/`](scripts/egitim/) · [`olcum_uretim/`](scripts/olcum_uretim/) · [`puanlama/`](scripts/puanlama/) · [`erisim_korpus/`](scripts/erisim_korpus/) · [`veri_hazirlik/`](scripts/veri_hazirlik/) |
| [`docs/record/research_log/`](docs/record/research_log/) | **araştırma kaydı** — ne olduğu, kronolojik, her sayıyla; son giriş **#62** |
| [`docs/adr/`](docs/adr/) | **karar defteri** — 46 numaralı dosya, numaralandırma **0073**'e kadar (`0001-0026` tek dosyada: [`gemma4-12b-dersler.md`](docs/adr/gemma4-12b-dersler.md); **0059 rezerve**) |
| [`docs/record/kollar.md`](docs/record/kollar.md) | **artefakt kaydı** — her kol ve merge, künyesiyle. *Satırı olmayan artefakt isimsizdir ve kullanılmaz.* |
| [`docs/record/yurutme-tuzaklari.md`](docs/record/yurutme-tuzaklari.md) | **hata vermeden yanlış sayı üreten** kalıpların listesi — her biri fiilen ısırdı |
| [`outputs/eval/`](outputs/eval/) | ham ölçüm çıktıları ve koşu künyeleri (`KUNYE.json`) |
| [`data/corpus/mevzuat_maddeler.jsonl`](data/corpus/) | 40.496 maddelik mevzuat korpusu |
| [`tests/`](tests/) | `pytest` birim testleri |
| [`CLAUDE.md`](CLAUDE.md) | depo haritası + bağlayıcı kurallar |

---

## Araştırma kaydının kendisi bir değer

Bu depoda **negatif bulgular birinci sınıftır** ve yayımlanmış iddiaların çürütüldüğü yerler
kayıtta **damgalı** durur: kendi ön-kayıtlı kapısına takılıp geçersiz sayılan koşular · ölçüm
çeliştiği için **tersine çevrilen** bir normalizasyon kararı
([ADR-0052](docs/adr/0052-merge-norm-dengeleme-hukmu-tersine.md)) · **düşmüş** bir ara kapı
([ADR-0045](docs/adr/0045-ara-kapi-merge-onarim-kontrolu.md)) · ve *"kazanç eğitimden değil,
ölçümden geldi"* itirafı ([#62](docs/record/research_log/2026-09-06-faz0-olcum-zinciri.md)).

Sayılar **hatırlanmaz, kaynaklanır**: her sonucun metriği, `n`'i, hakemi, seed'i ve çıktı
dosyası koşu künyesinde (`KUNYE.json`) sabitlenmiştir.

---

## Veri ve lisans

- **Kaynaklar:** [mevzuat.gov.tr](https://www.mevzuat.gov.tr) · Resmî Gazete · Yargıtay açık
  portalı · `bedesten.adalet.gov.tr` JSON API
  ([sözleşme](docs/BEDESTEN_API.md)) · iki Apache-2.0 Hugging Face veri seti ·
  gerçek mevzuat metninden üretilip **doğrulanmış** sentetik çiftler.
  Veri planı: [`docs/VERI_PLANI.md`](docs/VERI_PLANI.md) · eğitim reçetesi:
  [`docs/FINE_TUNING.md`](docs/FINE_TUNING.md).
- **Hiçbir aşamada ticari hukuk veritabanı kullanılmadı** (Lexpera, Kazancı vb.) — telif
  zehri. Bu, sonradan yapılan bir temizlik değil, ilk günden konmuş bir kuraldı.
- Eğitim verisinde PII maskelenir.
- **Lisans: Apache-2.0** ([`LICENSE`](LICENSE)). Base model `Qwen/Qwen3.5-4B` Apache-2.0'dır;
  tam atıf zinciri [`NOTICE`](NOTICE) dosyasındadır.

## Katkı

Katkı, eleştiri ve **yeniden üretme denemeleri** — özellikle yeniden üretme denemeleri —
memnuniyetle karşılanır. Bir sayıyı yeniden üretemiyorsanız bu bir hata raporudur.
