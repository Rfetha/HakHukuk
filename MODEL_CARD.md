# HakHukuk-4B — Model Kartı

Türkçe mevzuat için, tüketici sınıfı bir dizüstü GPU'sunda çalışan 4B parametreli bir hukuk
asistanı. İki LoRA kolu ham temel modelden bağımsız eğitilmiş, görev vektörü olarak ham TIES
ile birleştirilmiş ve Q4_K_M'e kuantize edilmiştir.

Bu kart ölçülen değerleri ve ölçülmeyen sınırları birlikte bildirir. Her sayının yanında
üretildiği dosya anılır; hiçbir değer hatırlanarak yazılmamıştır. Kararların gerekçesi ve
elenen alternatifler [`docs/adr/`](docs/adr/), kronolojik ölçüm kaydı
[`docs/record/research_log/`](docs/record/research_log/README.md) altındadır.

## Künye

| | | kaynak |
| :--- | :--- | :--- |
| **Dışa dönük ad** | `HakHukuk-4B-v0.1` | [`kollar.md`](docs/record/kollar.md) |
| **İç ad** (izlenebilirlik) | `tgta_v1` = `tg_v1` + `ta_v1` | [`kollar.md`](docs/record/kollar.md) |
| **Temel model** | `Qwen/Qwen3.5-4B` · commit `851bf6e8…` · Apache-2.0 | [`KUNYE_tgta_v1.json`](outputs/eval/cp3d-merge/KUNYE_tgta_v1.json) |
| **Yöntem** | 2 × LoRA (r=16, α=32) → eşzamanlı 2-yollu ham TIES | [`KUNYE_tgta_v1.json`](outputs/eval/cp3d-merge/KUNYE_tgta_v1.json) |
| **Taşıyıcı** | GGUF **Q4_K_M** · 2,59 GiB (2.783.446.720 bayt) | [ADR-0071](docs/adr/0071-v1-release-artefakti-tek-gguf.md) |
| **Ağırlıklar** | [`Rfetha/HakHukuk-4B-v0.3-Q4_K_M`](https://huggingface.co/Rfetha/HakHukuk-4B-v0.3-Q4_K_M) — herkese açık | ADIM 9, 2026-09-13 |
| **Ürün / iddia sürümü** | **`v1.0`** (2026-09-13) | [ADR-0084](docs/adr/0084-kappa-borcu-kapandi-kapi-yeni-birimde-gecti.md) |
| **Dil** | Türkçe | — |
| **Lisans** | Apache-2.0 — ağırlık, kod, veri ve araştırma kaydı | [`LICENSE`](LICENSE) · [`NOTICE`](NOTICE) |

**Üç ayrı sürüm numarası vardır ve birbirinin yerine geçmez**
([ADR-0065](docs/adr/0065-bolunmus-surumleme.md), bölünmüş sürümleme):

| numara | bugünkü değer | neyi adlandırır |
| :--- | :--- | :--- |
| artefakt kimliği | `HakHukuk-4B-v0.1` / `tgta_v1` | ağırlıkların kendisi; **kalıcıdır**, değişmez |
| dosya adı | `HakHukuk-4B-v0.3-Q4_K_M.gguf` | yayımlanan GGUF; içerik değişmediği için **adı da değişmez** |
| ürün / iddia sürümü | `v1.0` | ölçüm aygıtının ulaştığı doğrulama düzeyi (§3.1) |

---

## 1. Sorumluluk reddi ve ön koşullar

### 1.1 Bu hukuki tavsiye değildir

HakHukuk, hukuk metnini anlaşılır kılmak amacıyla geliştirilmiş bir **araştırma
artefaktıdır**. Avukat değildir ve çıktısı hukuki tavsiye niteliği taşımaz. Gerçek bir hukuki
mesele hakkında karar vermek için kullanılmamalı, nitelikli bir avukata danışılmalıdır.

Ürettiği her madde numarası, [mevzuat.gov.tr](https://www.mevzuat.gov.tr) üzerinden
**doğrulanması gereken bir iddia** olarak değerlendirilmelidir. Mevzuat değişir, ağırlıklar
değişmez: güncellik erişim katmanının sorumluluğundadır, modelin belleğinin değil.

> Bu ibarenin nihai metni henüz kararlaştırılmamıştır. Avukatlık Kanunu ve hukuki sorumluluk
> sınırı bu depoda değerlendirilmemiş olup **hukukçu görüşü gerektirmektedir** (açık karar
> **S10**, [ADR-0083](docs/adr/0083-kusur-sicili-adrye-tasindi.md) §EK). Yukarıdaki metin bir
> taslaktır, hukuken denetlenmiş bir feragatname değildir.

### 1.2 Model tek başına bildirilen başarımı üretmez

Bildirilen kütle değerleri **erişim katmanı etkin** (harness açık) koşulda ölçülmüştür: model
cevaplamadan önce bir retriever ilgili mevzuat maddelerini bulup bağlama yerleştirmektedir.
Modelin tek başına indirilmesi, ölçümün yapıldığı rejimi vermez; kaynaksız koşulda modelin
yüksek güvenle yanlış hukuki içerik ürettiği ayrıca ölçülmüştür (§4.5).

| Bileşen | Durum | kaynak |
| :--- | :--- | :--- |
| Ağırlıklar | Yayımlandı, herkese açık | [Hugging Face](https://huggingface.co/Rfetha/HakHukuk-4B-v0.3-Q4_K_M) |
| Kod (retriever, servis, sınıflandırma) | Yayımlandı | [github.com/Rfetha/Hukuk-SLM](https://github.com/Rfetha/Hukuk-SLM) |
| Arama indeksi (`bge-m3`, 40.496 madde, ~80 MB) | **Yayımlanmadı** | açık borç **G8** |

İndeksin dağıtımı açık bir iştir. Korpusun kapsamı yaklaşık 8,4 kat genişleyeceğinden,
bugünkü indeksin paketlenmesi kısa ömürlü olacaktır.

Erişim katmanının künyesi:

| bileşen | değer | kaynak |
| :--- | :--- | :--- |
| indeks | `data/index/mevzuat_bge_m3_s2` · 40.496 madde · 80 MB | [`KUNYE.json`](data/index/mevzuat_bge_m3_s2/KUNYE.json) |
| erişim | hibrit BM25 + `BAAI/bge-m3`, RRF füzyonu · `RRF_K=10` · **k=10** | [ADR-0068](docs/adr/0068-rrf-k-60-to-10.md) |
| istem | önsözsüz | [ADR-0063](docs/adr/0063-yeterlilik-onsozu-kaldirildi.md) |
| üretim bütçesi | 1536 = düşünce 1024 + cevap 512 | [ADR-0070](docs/adr/0070-uretim-butcesi-esitlendi.md) |

Erişim katmanı **GPU'ya hiç girmez** — gömücü CPU'da, indeks CPU belleğinde ve diskte çalışır.
Modelin dizüstüne sığmasıyla sığmaması arasındaki fark budur. Vektör veritabanı ölçülmüş ve
reddedilmiştir: kaba kuvvet arama 8,2 ms/sorgu (CPU, 50 sorgu ortalaması, S2 öncesi indekste).

### 1.3 Sunucu bayrakları sonucu değiştirir

Bildirilen bütün değerler aşağıdaki `llama-server` yapılandırmasıyla üretilmiştir. Bu bir
belgelendirme ayrıntısı değil, **bağlayıcı bir karardır**: farklı yapılandırmanın farklı cevap
ürettiği kontrollü deneyle ölçülmüştür.

```bash
llama-server -m HakHukuk-4B-v0.3-Q4_K_M.gguf \
  -ngl 99 -fa on --no-context-shift \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  -c 8192 --host 127.0.0.1 --port 8080
```

Aynı soru, aynı kod, seed 3407, sıcaklık 0; değişen tek etken KV önbelleğinin kuantizasyonu:

| KV önbelleği | durum sınıfı | cevap `sha256` | uzunluk |
| :--- | :--- | :--- | ---: |
| `q8_0` (bütün ölçümlerin yapıldığı) | SUSKUNLUK | `79b6915a…` | 201 |
| varsayılan (fp16) | ÇEKİNCELİ CEVAP | `e97a2b85…` | 622 |

Farkın 80 kalemlik kümedeki toplam etkisi de ölçülmüştür: fp16 ile 80 cevabın **65'i (%81,2)**
bayt olarak değişmiş, ancak hiçbir sayaç birden fazla kalem oynamamıştır (kesik 4→3, tamamen
boş 0→0, çekinme 5→5, uydurulmuş madde 0→0). Kütle **0,8011 → 0,7932** (−0,79 puan) — hakem
gürültü tabanının 2,8 katı, **ama tek yönlü hükme yetmez**: o taban aynı cevaplara hakemi
yeniden koşmanın gürültüsüdür, burada ise cevaplar da değişmiştir ve bu koşu çiftinin kendi
tabanı ölçülmemiştir. Tabanın açıkça üstündeki tek eksen atıf isabetidir ve **kötüleşmiştir**:
yanlış kaynağa atıf oranı **0,0769 → 0,1553 (2,0 kat)**.

⇒ Taşıyıcı rejim `q8_0` KV ile sabitlenmiştir (insan kararı, 2026-09-11). Varsayılan KV ile
bildirilen kütlenin korunacağı **iddia edilmemektedir**.
Kaynak: [`KARSILASTIRMA.md`](outputs/eval/g22-kv-fp16/KARSILASTIRMA.md) ·
[`KUTLE.md`](outputs/eval/g22-kv-fp16/KUTLE.md).

Aynı yapılandırmada üretim yinelenebilirdir (iki koşu, özdeş `sha256`). `servis.py`'nin
*"aynı soru aynı cevabı verir"* değişmezi, yapılandırma sabit tutulduğunda geçerlidir.

---

## 2. Kurulum ve kullanım

### 2.1 Konteyner — önerilen yol

Paketleme bir **rejim kilididir**, kolaylık değil. §1.3'ün ölçtüğü bayraklar daha önce üç
belgede düz metin olarak duruyordu ve hiçbiri kapı değildi. `compose.yaml` bu bayrakları
`q8_0` KV dâhil **zorlar**; `llama-server`'ı elle açan kişi onları kendisi yazmak zorundadır.

```bash
export HF_TOKEN=...                # opsiyonel — depo herkese açık
export HAKHUKUK_INDEKS_DEPO=...    # varsayılanı bilerek boş (aşağıya bakınız)
docker compose up
```

`indir` kutusu GGUF'u **pinlenmiş bir revizyondan**, `sha256` ve bayt sayısı kapısının
arkasından çeker; kapı tutmazsa çıkış kodu sıfırdan farklı olur ve **iki daemon da hiç
başlamaz** ([ADR-0078](docs/adr/0078-konteyner-dagitimi-rejim-kilidi.md) ·
[ADR-0082](docs/adr/0082-app-kutusu-host-sapmasi.md)).

| | |
| :--- | :--- |
| API | `127.0.0.1:8000` |
| `llama-server` | `127.0.0.1:8080` |
| `HF_TOKEN` | opsiyonel; tanımsız kalması yalnız hız sınırını düşürür |
| `HAKHUKUK_INDEKS_DEPO` | **bilerek boş** — indeks dağıtımı (**G8**) bekletildiğinden yayımlanmış bir indeks deposu yoktur. İndeks ya volume'e elle konur ya depo adı verilir; aksi hâlde `indir` kutusu **kasten** durur |
| gereksinim | NVIDIA GPU + Docker. Ölçülen ortam: Docker 28.4.0 · compose v2.39.4 · RTX 5070 Ti Laptop 12.227 MiB · sürücü 591.97. `gpus: all` anahtarı compose v2.30+ ister |
| imaj etiketi | `hakhukuk:1.0.0` — **ürünün** sürümü ([`pyproject.toml`](pyproject.toml)) |
| imaj boyutu | `hakhukuk` **2,08 GB** · `llama.cpp:server-cuda-b10902` **6,99 GB** |

İki daemon da yalnız host'un `127.0.0.1` arayüzüne yayımlar; **kimlik doğrulama ve hız sınırı
yoktur** (açık karar **S9**). Ağırlık ve indeks imajın içinde **bulunmaz**.

Korpus üç yerde durur: repo, imaj ve volume. `indir` imaj ↔ volume `sha256` eşitliğini her
koşuda sınar ve tutmazsa erken durur; ancak **repo ↔ imaj** ayrışması sınanmaz (açık kusur 11).

### 2.2 Python paketi ve komut satırı

Retriever, istem ve atıf doğrulama tek bir arayüzün arkasındadır:

```bash
llama-server -m models/gguf/tgta_v1-q4_k_m.gguf -ngl 99 -fa on \
             --cache-type-k q8_0 --cache-type-v q8_0 -c 8192 --port 8080 &

hakhukuk "Askerlik nedeniyle iş sözleşmesi ne olur?"   # komut satırı
hakhukuk-tui                                           # tek ekran arayüz
```

```python
from hakhukuk import servis

cevap = servis.answer("Kat malikleri kurulu hangi çoğunlukla karar alır?")
cevap.durum      # Durum.CEVAP | CEKINCELI | SUSKUNLUK | KESIK
cevap.atiflar    # her atıfta dogrulandi: getirilen kaynakta var mı
cevap.kaynaklar  # modele hangi maddeler verildi
```

### 2.3 Kullanıcı yüzünde garanti edilenler

| garanti | nasıl |
| :--- | :--- |
| Doğrulanmamış atıf **uyarıyla** gösterilir, gizlenmez | `terazi.siniflandir()`; kimlikler `madde_anahtari` ile normalleştirilerek karşılaştırılır |
| **Kesik** cevap kesik olduğunu söyler | `finish_reason="length"` → `Durum.KESIK`; sessizce yutulmaz |
| Kaynak bulunamazsa **model çağrılmaz** | `servis.answer()`; üründe kaynaksız-ezber koşulu oluşmamalıdır |
| **Mülga madde gösterilmez** | `retriever.getir()` varsayılanı `Yururluk.YALNIZ_YURURLUKTE` — ölçüldü: sızıntı 2 → 0, `recall@10` değişmedi |

Sorumluluk ibaresi, durum ne olursa olsun **koşulsuz** basılır.

### 2.4 Donanım

`llama-server` · Q4_K_M · KV önbelleği `q8_0` · tek slot; **bu artefaktın kendisinde** ölçüldü
([`vram_stack_tgta_v1.json`](outputs/eval/_artefakt/vram_stack_tgta_v1.json)):

| bağlam | sunucu VRAM | tepe |
| ---: | ---: | ---: |
| 4.096 | 3,09 GiB | 4.068 MiB |
| 32.768 | 3,70 GiB | 4.684 MiB |
| 131.072 | 5,76 GiB | 6.796 MiB |

⇒ Projenin ≤ 8 GB yumuşak kapısı **128K bağlamda bile** geçilmektedir. Çıktı dosyasında GPU
modeli kayıtlı değildir; yalnız pstate, saat, güç ve sıcaklık vardır.

### 2.5 Ne için — ve ne için değil

Modele bir soru ve kaynak hukuk metni verilir; model ya

1. cevaplar ve **dayandığı maddeyi belirtir**, ya da
2. *"verilen kaynaklar bunu kapsamıyor"* der.

**İkinci yarı işin zor kısmıdır ve bu projenin varlık sebebidir.** Her şeye cevap veren bir
model hukukta işe yaramazdan da kötüdür: kendinden emin yanlış bir madde numarası,
*"bilmiyorum"*dan daha tehlikelidir.

Sade dil bir **eğitim hedefi değil**, doğru cevabın sunum katmanıdır. Sade ve kısa cevaba
doğru eğitmek denenmiş ve isabeti **düşürmüştür**; vatandaş-register turunda model temel
modeli yakalarken çekinme çökmüştür ([ADR-0010](docs/adr/gemma4-12b-dersler.md#adr-0010),
yürürlükte). Eğitim hedefi doğruluk ve çekinmedir; sadeleştirme istem katmanında yapılır.

---

## 3. Başarım, sürüm ve karşılaştırma

### 3.1 Sürüm `v1.0` ne der, ne demez

`v1.0` etiketi 2026-09-13'te **insan onayıyla** verilmiştir. Hükmü tek cümleyle şudur:

> *Ölçüm aygıtı artık iki bağımsız hakem ailesiyle aynı yönde hükmediyor ve ağırlıklar
> herkese açık.*

**Söylemediği dört şey, bu cümle kadar bağlayıcıdır:**

| `v1.0` şunu demez | çünkü |
| :--- | :--- |
| *"Model iyileşti."* | Ağırlıklar bu turda **hiç değişmedi**. Yayımlanan dosyanın `sha256`'sı ve bayt sayısı `v0.3` etiketiyle yayımlanan dosyayla **birebir aynıdır**. |
| *"Ölçüm kesinleşti."* | Manşet hâlâ **koşulsuz bir aralıktır**: `%69,4-80,1`. `v1.0` bu aralığı tek sayıya indirmez. |
| *"Hakem uyumu düzeldi."* | κ **0,534** (`tam_sadık`) / **0,409** (`atıf_temiz`) — ikisi de bu turda yeniden ölçülmedi ve aracın **0,6** eşiğinin altında kalmaya devam ediyor. Kapanan şey κ değil, **eşit sınavın yokluğuydu**. |
| *"Panel tamam."* | Panel hâlâ **iki** ailelidir, üç değil. Üçüncü aile (Google) bütçe nedeniyle eklenmedi; sapma [ADR-0032](docs/adr/0032-hakem-paneli-uc-aile-ve-aile-dislama.md)'den **eksiklik olarak** kayıtlıdır. |

Ayrıntı: [ADR-0084](docs/adr/0084-kappa-borcu-kapandi-kapi-yeni-birimde-gecti.md) ·
[#70](docs/record/research_log/2026-09-13-on-dort-bulgu-kappa-kapisi-gecti.md).

**Dosya adı ile sürüm etiketi aynı şey değildir.** Yayımlanan dosyanın adı
`HakHukuk-4B-v0.3-Q4_K_M.gguf` olarak **kalmıştır** ve kasten değişmeyecektir: içeriği
değişmemiş bir dosyaya yeni sürüm adı vermek, dosya adının içerik hakkında yanlış bir şey
iddia etmesi olur. Sürümü artık **kart anlatır**, dosya adı değil.

#### Sürüm kapısının üç maddesi

Ön-kayıt 2026-09-06 öğleden önce, **hiçbir rakip sayısı görülmeden** yazılmıştır; çıpa
(`gemini-3.5-flash`) o an hiç ölçülmemişti. Sayılar 2026-09-07'de mekanik olarak türemiştir
([ADR-0064](docs/adr/0064-v1-kapisi-uc-maddeli-on-kayit.md)).

```
(1) kütle ≥ (3.5 Flash'ın kütlesi) − 2,0 puan     ← asıl kapı
(2) isabetsizlik gerilemez
(3) M5 (kör/parametrik) yükselmez                  ← anti-hedef
(*) her sayım adımında gözle okuma zorunlu
```

| madde | hüküm | sayı |
| :--- | :--- | :--- |
| **(1)** kütle | **GEÇTİ** — üç okumanın üçünde de | bağlayıcı okuma: **0,8011 ↔ eşik 0,7225** → **+5,86 puan** |
| **(2)** isabetsizlik | sağlanıyor | çıpa yeni birimde **8/80**'e çivilendi |
| **(3)** M5 | **GEÇTİ** — iki okumada da | ezber kütlesi **−6,82 puan** (göz) / **−7,98 puan** (alet) |
| **(\*)** gözle okuma | yapıldı | üç sayım adımında da; **ikisinde alet yanıldı** |

Madde (1) okuma seçimine bağlı değildir:

| okuma | 3.5 Flash | eşik = Flash − 0,020 | HakHukuk | fark |
| :--- | ---: | ---: | ---: | ---: |
| ALET | 0,6925 | 0,6725 | 0,8011 | +10,86 p |
| GÖZ-orta | 0,7050 | 0,6850 | 0,8011 | +9,61 p |
| **GÖZ-katı (bağlayıcı)** | **0,7425** | **0,7225** | **0,8011** | **+5,86 p** |

Kapı 2026-09-12'de **ikinci bir hakem ailesi altında** yeniden okunmuş ve üç madde de yeniden
geçmiştir. Kendi kütlemiz ikinci hakemde **10,71 puan** düşmüş, ancak çıpa **12,42 puan**
düştüğü için çıpaya göre marj **genişlemiştir**: **+5,86 p** (`gpt-4o-mini`) → **+7,57 p**
(`claude-sonnet-5`). Mutlak bir eşik bu sınavı **düşürürdü**; kapı çıpaya göre tanımlandığı
için geçmiştir — bu, kapının tasarımının ölçülmüş bir sonucudur.

> **Madde (2) hakkında dürüst not.** Çıpa ön-kayıtta *"≤ 7/80"* yazıyordu, ancak o sayı **v1
> soru setinden** geliyordu ve hiç gözle sayılmamıştı. v2 biriminde ilk kez tam gözle sayıldığında
> **8/80** çıktı. Eşik **gevşetilmedi, birimi düzeltildi**: `7/80` ile `8/80` aynı birimde
> değildir. Madde bugün tanım gereği sağlanmaktadır; **bağlayıcı olacağı yer bir sonraki eğitim
> turudur**.

### 3.2 Ölçüm rejimi

Beş özne aynı sınava girmiştir. Sınavın eşit olduğu **varsayılmamış, ölçülmüştür**
([ADR-0057](docs/adr/0057-harness-rekabet-kapisi-esit-sinav.md): bir kıyas yalnız eşleşmiş
eksenlerde hüküm verir; eşleşmeyen eksen tavan/tanımsız damgası alır).

| değişmez | değer | kaynak |
| :--- | :--- | :--- |
| soru seti | `data/eval/dev/core_hard.jsonl` **v2**, n=80 (geliştirme kümesi) | [ADR-0067](docs/adr/0067-soru-onarimi-dev-test-v2.md) |
| istem | önsözsüz | [ADR-0063](docs/adr/0063-yeterlilik-onsozu-kaldirildi.md) |
| erişim | harness açık · k=10 · `RRF_K=10` | [ADR-0068](docs/adr/0068-rrf-k-60-to-10.md) |
| üretim bütçesi | 1536 (düşünce 1024 + cevap 512), tek formül | [ADR-0070](docs/adr/0070-uretim-butcesi-esitlendi.md) |
| seed · klip · düşünce | 3407 · 900 karakter · açık | [`KUNYE.json`](outputs/eval/f02-biz-onsozsuz/KUNYE.json) |
| hakem | `openai/gpt-4o-mini` · OpenRouter, `OpenAI` pinli · runs=1 | [`summary.json`](outputs/eval/f02-biz-onsozsuz/gnd_h1_tgta_v1_f02_nb_summary.json) |
| taşıyıcı (bizim kol) | `llama-server` · Q4_K_M · ctx 8192 · KV `q8_0` · yerel | [`KUNYE.json`](outputs/eval/f02-biz-onsozsuz/KUNYE.json) |

**Eşitliğin kanıtı:**

| eksen | HakHukuk | Gemini kolları | Sonnet-5 |
| :--- | ---: | ---: | ---: |
| `recall@1 / @3 / @5 / @10` | 0,5250 / 0,7625 / 0,8250 / **0,9500** | aynı | aynı |
| `context_shown` | — | **80/80 bayt-bayt aynı** | 80/80 |
| kesik cevap | 4/80 | 4/80 | 4/80 |
| girdi belirteci (toplam) | **193.042** | **193.042** | ölçülmedi |
| istem · bütçe · soru seti | önsözsüz · 1536 · v2 | aynı | aynı |

Girdi belirteci üç öznede **birebir aynıdır** (ortalama **2.413/kalem**) çünkü istem 80/80
bayt-bayt özdeştir; maliyet
farkı tümüyle çıktı belirtecinden ve birim fiyattan gelmektedir.

**Geçerlilik kapıları — koşu bunlardan geçmiştir:**

| kapı | değer | eşik | hüküm |
| :--- | ---: | ---: | :--- |
| kesiklik ([ADR-0040](docs/adr/0040-dusunce-modu-olculecek-on-kayitli-kural.md)) | %5,0 | ≤ %5 | **tam eşikte, payı yok** |
| `recall@10` sapması | 0,9500 | 0,9500 | birebir — erişim katmanı oynamamış |
| doğrulanan atıf / atıfsız geçen | 114 / **7 kalem** | — | atıfsızlık ayrı bir borçtur (§4.2) |

**Zorunlu ön adım — red dedektörü rakip ailelerde kalibre edildi.** 28 rakip çekinme kalemi
tek tek gözle okunmuş ve dedektörün Gemini şablonunda **sistematik olarak fazla red saydığı**
bulunmuştur:

| kol | araç | temiz çekinme | çekinceli cevap | açık yanlış pozitif |
| :--- | ---: | ---: | ---: | ---: |
| **HakHukuk** | 4 | **4** | 0 | **0** |
| `gemini-3.1-flash-lite` | 8 | 5 | 0 | **3** |
| `gemini-3.5-flash-lite` | 9 | 5 | 2 | **2** |
| `gemini-3.5-flash` | 11 | 7 | 3 | **1** |

Örnek (3.1 FL, id 38): *"**TCK 235'e göre** … cezalandırılır."* — altın maddeden verilmiş doğru
bir cevap, araç çekinme saymış. ⇒ **Üstünlüğümüzün bir kısmı aracın eseriydi**; aşağıdaki skor
kartı bunu düzeltir.

### 3.3 Skor kartı

Değerler **gözle düzeltilmiş** birimdedir; ham araç okumaları dipnot ᶜ'dedir.

| Eksen | **HakHukuk-4B** | `gemini-3.1-flash-lite` | `gemini-3.5-flash-lite` | `gemini-3.5-flash` | `claude-sonnet-5` |
| :--- | ---: | ---: | ---: | ---: | ---: |
| **Sadık cevap kütlesi** ↑ ᵃ | **0,6940-0,8011** aralık ⁱ | 0,7058 | 0,7622 | 0,7425 | **0,8348** |
| Cevaplama oranı (`coverage`) ↑ | **0,9375** | 0,8750 | 0,8750 | 0,8375 | 0,9000 |
| `A1`, cevaplanan ↑ | 0,8545 | 0,7710 | 0,8199 | 0,8269 | **0,8790** |
| `A1`, altın getirilen ↑ | 0,8902 | 0,7900 | 0,8449 | 0,8523 | **0,9031** |
| `recall@10` (erişim) | 0,9500 | 0,9500 | 0,9500 | 0,9500 | 0,9500 |
| Aşırı çekinme ↓ ᶜ | **4/80** | 5/80 | 5/80 | 7/80 | **4/80** |
| İsabetsiz atıf ↓ ᵈ | 8/80 | 8/80 | **7/80** | 8/80 | **7/80** |
| Uydurulmuş madde numarası ↓ ᶠ | **0/114** | **0/153** | 4/130 | 4/133 | 2/161 |
| Ezber kütlesi (M5) ↓ ᵉ | **0,3899** | 0,6710 | 0,7013 | 0,8241 | 0,7772 |
| Cevap başına maliyet ↓ ᵍ | **$0** | $0,001895 | $0,001152 | $0,009914 | $0,014915 |
| Ortalama belirteç / cevap ↓ | 782,5 | 861,5 | **171,1** | 699,4 | 706,6 |

**Okunuşu.** Sonnet-5 kütle, `A1` ve atıf kalitesi eksenlerinde **öndedir**. HakHukuk cevaplama
oranında ve uydurulmuş madde numarasında öndedir; aşırı çekinmede iki model eşittir. Fark,
**kaynak verilen** bir sınavda ölçülmüştür; kaynaksız bir karşılaştırma değildir (§4.5).

**Temel model (`Qwen3.5-4B`) bu tabloda yoktur — ve yokluğu bir bulgudur.** Sınava sokulmuş ve
**geçerlilik kapısından kalmıştır**: kesik cevap **16/80 = %20** ↔ eşik %5, dolayısıyla hakem
hiç çağrılmamış ve hiçbir hüküm-ekseni sayısı üretilmemiştir
([`f08-base-harness/`](outputs/eval/f08-base-harness/h1_base_h1_v2_detail.jsonl)). 16 kesiğin
**15'i gerçek kesilme, 1'i döngüdür**; sebep ölçülmüştür: temel model **uzun, kaynak
alıntılayan** cevaplar yazmakta ve 1536 belirtece sığmamaktadır. Karşılaştırma bulgunun
kendisidir: aynı model **kör modda** yalnız **2/80** kesik vermektedir ⇒ şişiren etken
**kaynakların kendisidir**. Bu, ince ayarın muhakemeyi stabilize ettiği bulgusunun
([#42](docs/record/research_log/2026-07-29-cp0-dusunce-modu-sonlanmama.md)) erişim katmanı
açıkken ölçülmüş hâlidir. Temel modelin M5 (ezber) değeri ayrıca ölçülebilmiştir: **0,4697**
(§4.5).

#### Dipnotlar

- **ᵃ** Rakip sütunlarında **bağlayıcı GÖZ-katı** okuması yazılıdır — üç okumanın en
  muhafazakârı, yani rakip lehine olanı (§3.5).
- **ᶜ** Tanım beş öznede de aynıdır: *altın madde bağlama girdi, model yine de sustu*. Tablodaki
  değerler **gözle düzeltilmiş temiz çekinme** sayılarıdır (§3.2 kalibrasyon tablosu). Ham araç
  okumaları: HakHukuk 4 · 3.1 FL 8 · 3.5 FL 9 · 3.5 Flash 11 · Sonnet-5 7.
  ⚠️ **Açık kalem:** bu eksenin gözle düzeltilmiş sayıları depo içinde **üç farklı yerde üç
  farklı biçimde** kayıtlıdır; bağlayıcı kabul edilen, türetmesi yazılı olan §3.2 kalibrasyon
  tablosudur. Sonnet-5 kolu o tabloda yoktur, hücresi ayrı bir gözle okumadan gelir. Eksenin
  tek bir birime oturtulması **açık borçtur** (§4.1).
- **ᵈ** **Bu satırda *"biz iyiyiz"* cümlesi kurulmaz.** Beş öznenin de **80/80 kalemi**, aynı
  ölçütle, örneklem değil **tam** olarak gözle taranmıştır. Sonuç: ikisiyle berabere, ikisiyle
  geride. Taban da aynı değildir — çekinen kalem sınanamaz, ve her kolun cevapladığı kalem
  sayısı farklıdır:

  | kol | isabetsizlik | cevaplanan tabanda |
  | :--- | ---: | ---: |
  | HakHukuk | 8/80 | 8/75 = **%10,7** |
  | 3.1 Flash-Lite | 8/80 | 8/73 = %11,0 *(türetildi)* |
  | 3.5 Flash-Lite | 7/80 | 7/71 = %9,9 *(türetildi)* |
  | 3.5 Flash | 8/80 | 8/71 = **%11,3** |

  **Kendi aleyhimize ek bulgu:** bizim isabetsiz olduğumuz id **32 · 41** rakipte isabetlidir;
  id **27 · 42** — öz-denetimde *"soru yazımım komşu maddeye kaydırdı"* dediğimiz iki kalem
  (§4.2) — rakip o tuzağa **düşmemiştir**. ⇒ Kusurun kaynağı soru değil, **model** olabilir.
  Üç kolda da **sınır durum** sayılmış ve hiçbirinde sayıya katılmamıştır ⇒ **üç isabetsizlik
  sayısı da alt sınırdır**.
- **ᵉ** **Bu satırdan *"M5'te rakipleri yendik"* cümlesi kurulmaz.** Sebebi ve sayının ikinci
  yüzü §4.5'tedir.
- **ᶠ** **Birim tüm kolonlarda ortaktır:** pay = `MADDE_YOK + KANUN_YOK`, payda =
  **`DOGRULANDI`** (o koldaki toplam atıf sayısı değil). Bu ayrım daha önce hiçbir yerde yazılı
  değildi ve bir ön sondayı yanıltmıştı. `gemini-3.1-flash-lite` hücresi 2026-09-11'de yeniden
  puanlanmıştır (atıf doğrulayıcı, parantezli adlı 16 kanunun 7'sinde **yanlış kanuna**
  `DOGRULANDI` basıyordu; onarım sonrası 0/16): `1/152` → `0/153`. **Bu değişim aleyhimizedir
  ve öyle yazılmıştır** — rakiplerin tamamının üstünde olduğumuz tek deterministik eksende
  3.1 Flash-Lite artık bizimle eşittir. Karşılığında **eşit sınav** sağlanmıştır: beş kolun
  beşi de aynı araçla puanlanmaktadır. 702 atfın yalnız 1'i değişmiş, diğer üç kol
  oynamamıştır; her kol iki kez koşulmuş ve iki koşu bayt bayt aynı çıkmıştır.
  Kaynak: [`BULGU.md`](outputs/eval/g22-rakip-yeniden-puanlama/BULGU.md).
- **ᵍ** **Ölçüldü, tahmin edilmedi** — ölçüm bedeli $0,0487
  ([`MALIYET.json`](outputs/eval/f09-maliyet/MALIYET.json), fiyatlar OpenRouter, 2026-09-07).
  Bizim kolumuz **yerelde** koştuğu için çıkarım bedeli sıfırdır. Üç Gemini aynı tokenizer'ı
  kullanmaktadır (3 kalemde sınandı, `prompt_tokens` birebir) ⇒ sayım yalnız en ucuz modelde
  yapılmış, fiyatlar ayrı uygulanmıştır. **Kapı çıpası `3.5 Flash`, `3.5 Flash-Lite`'ın 8,6 katıdır**
  ($0,009914 ↔ $0,001152). Hakem bedeli bu satıra **dâhil değildir**, ayrıca kayıtlıdır:
  HakHukuk $0,0417 · 3.1 FL $0,0452 · 3.5 FL $0,0410 · 3.5 Flash $0,0434; kör mod koşusunun
  hakem bedeli $0,1418. **Maliyet-normalize parite iddiası yine de kurulmaz** — ADR-0017'nin istediği
  ölçüm bir Pareto eğrisidir, tek satır değil.
- **ⁱ** **Manşet koşulsuz bir aralıktır, sonuca göre biçimlendirilmemiştir** (insan kararı,
  [ADR-0084](docs/adr/0084-kappa-borcu-kapandi-kapi-yeni-birimde-gecti.md)). İki bağımsız hakem
  ailesi aynı 80 cevabı puanlamıştır: `gpt-4o-mini` **0,8011** ↔ `claude-sonnet-5` **0,6940**.
  Bu belgedeki tekil `0,8011` değerleri **GÖZ-katı, bağlayıcı** okumadır. Üç Gemini kolu ve
  Sonnet-5 **tek hakemli** kalmıştır; asimetri bilinçlidir, gizlenmemiştir.

### 3.4 Eksenler ne ölçüyor

| Eksen | Tanım | Neden bu |
| :--- | :--- | :--- |
| **Sadık cevap kütlesi** = `coverage × A1` | Sorulan 80 sorunun ne kadarına **hem cevap verdi hem de doğru kaynağa dayandı** | **Manşet ve bağlayıcı ölçüt budur:** cevaplamamak vatandaş için değersiz, yanlış cevaplamak tehlikelidir; tek sayı ikisini birden cezalandırmalıdır |
| `coverage` | Cevapladığı kalem oranı | Tek başına **yanıltıcıdır**: her şeye cevap veren model burada 1,00 alır |
| `A1`, cevaplanan | Yalnız cevapladığı kalemlerde iddialarının kaynağa sadakati | Çekinmeyi ödüllendirmesin diye **cevaplanan-only** hesaplanır |
| `A1`, altın getirilen | Aynı ölçüt, yalnız altın maddenin bağlama **girdiği** kalemlerde | Erişim başarısızlığını modelin kusurundan ayırır; özneler arası **en dürüst kıyas satırı** |
| `recall@10` | Altın madde ilk 10 kaynağa girdi mi | **Kütlenin tavanıdır**: girmemişse doğru cevap üretilemez |
| Aşırı çekinme | Altın madde **bağlamdayken** yine de sustuğu kalem sayısı | Erişimin çözemeyeceği, modelin kendi kusuru: *"kaynak elindeydi ve yine de yardım etmedi"* |
| İsabetsiz atıf | **Yanlış maddeye** dayanarak cevaplaması (atıf doğrulanır, cevap yine de soruya oturmaz) | Vatandaş için **en tehlikeli** kusur sınıfı; doğrulayıcı bunu yakalayamaz |
| Uydurulmuş madde numarası | Var olmayan kanun/madde numarası üretmesi | **Deterministik** doğrulanır, hakem gerekmez |
| Ezber kütlesi (M5) | Kaynak **verilmeden** ne kadar konuşup ne kadar tutturduğu | **Anti-hedeftir** — yükselmesi *"bilgi ağırlığa kaçtı"* demektir |
| Maliyet ve belirteç | Çıkarım bedeli | Ürünün **erişilebilirlik** ekseni; doğruluk ölçütü değildir |

**Bu ölçütlerin hiçbiri standart bir ölçüt kümesinden gelmez.** Tümü, Türkçe ve güncel Türkiye
Cumhuriyeti mevzuatı üzerine kurulmuş **kendi CANON kümemizden** üretilmiştir: 6 mod, n=80
geliştirme kalemi. MMLU, LegalBench ve BigLaw-Bench gibi dış ölçütler **koşulmamıştır**; bu bir
eksiklik değil, kayıtlı bir karardır ([ADR-0016](docs/adr/gemma4-12b-dersler.md#adr-0016)): söz
konusu kümeler İngilizce ve ABD common-law temellidir ve *"yanlış sınavda düşük not, model kötü
demek değildir"*. Bedeli gerçektir ve §4.4'te sayılmıştır.

CANON'un altı modu ([ADR-0011](docs/adr/gemma4-12b-dersler.md#adr-0011)); bu kartın sayıları
`h1` ve `M5`'ten gelir:

| mod | ne sorar |
| :--- | :--- |
| **M1** / **`h1`** | Kaynak verildiğinde doğru cevaplıyor ve dayandığı maddeyi belirtiyor mu? (`h1` = bağlamı **retriever** kurar) |
| M4 | Altın madde **garantili** verildiğinde tavan nedir? |
| M2 | **Yanlış** bir madde verildiğinde reddedebiliyor mu? |
| M2b / `h2b` | **Yalnız distractor** verildiğinde, altın yokken susabiliyor mu? |
| M3 | Bağlam **boşken** susabiliyor mu? |
| **M5** | **Kaynak verilmeden** ne kadar konuşuyor — **anti-hedef** |

### 3.5 Kütlenin üç okuması

Skor kartında **yalnız bağlayıcı olan** (GÖZ-katı) yer alır; üçü birlikte:

| Kol | ALET (ham) | GÖZ-orta *(yanlış pozitif düzeltildi)* | **GÖZ-katı (bağlayıcı)** |
| :--- | ---: | ---: | ---: |
| **HakHukuk-4B** | **0,8011** | **0,8011** | **0,8011** |
| `gemini-3.1-flash-lite` | 0,6746 | 0,7058 | 0,7058 |
| `gemini-3.5-flash-lite` | 0,7174 | 0,7403 | **0,7622** |
| `gemini-3.5-flash` | 0,6925 | 0,7050 | 0,7425 |
| `claude-sonnet-5` | 0,7911 | 0,8223 | **0,8348** |

**Bağlayıcı okuma olarak en muhafazakâr olan seçilmiştir** (insan kararı,
[ADR-0064](docs/adr/0064-v1-kapisi-uc-maddeli-on-kayit.md)): GÖZ-katı'da rakiplerin çekinceli
cevapları da **cevap** sayılır ⇒ onların kütlesi en yüksek, bizim farkımız **en dar** çıkar.
Seçimin gerekçesi tam olarak budur — *"kendi lehine okudun"* denmesin diye.

HakHukuk üç okumada da aynıdır, çünkü kendi kolunda yanlış pozitif ve çekinceli cevap yoktur
(80 kalem gözle okunmuş, araç ile göz arasındaki fark **sıfır** bulunmuştur).

**Aracın ham okuması HakHukuk'u Sonnet-5'in önünde gösterir (0,8011 ↔ 0,7911). Bu okuma
kullanılmamıştır:** çekinme dedektörü Sonnet-5 kolunda sekiz çekinmenin üçünü yanlış saymakta
(tam ve atıflı üç doğru cevap), HakHukuk kolunda ise yanlış pozitif bulunmamaktadır. Düzeltme
uygulandığında **sıralama değişmektedir** ve bu kart değişen sıralamayı yazar.

Kaynak: [`KALIBRASYON_ve_OZET.md`](outputs/eval/f04-rakip-onsozsuz/KALIBRASYON_ve_OZET.md).

### 3.6 Geliştirme kümesi ↔ donmuş test

Donmuş TEST **2026-09-09'da, açık insan onayıyla ve tek kez** açılmıştır. Rejim, geliştirme
koşusuyla her eksende birebir ve **araçsızdır**. Geçerlilik kapısı geçilmiştir (kesiklik %2,5).

| | **TEST** (40) | **DEV** (80) |
| :--- | ---: | ---: |
| **Ham kütle — manşet** | **0,5804** | 0,8011 |
| Tavan (`recall@10`) | 0,7500 | 0,9500 |
| **Tavan kullanımı** | **0,7739** | 0,8433 |
| Uydurulmuş madde numarası | **0/52** | 0/114 |
| `wrong_ref_rate_micro` | 0,2424 | 0,0769 |
| Aşırı çekinme | 5/40 [0,055–0,261] | 4/80 [0,020–0,122] *(aralıklar örtüşüyor)* |

**İki değer aynı ölçüt değildir** ve fark setin daha zor sorular içermesinden değil
**bileşiminden** gelir: ayrım kanuna göre kusursuz katmanlıdır (2:1) ama **madde uzunluğuna
göre katmanlanmamıştır**; en zor uzunluk diliminde DEV'in payı %12, TEST'in **%50**'dir.

**Düşüşün ayrıştırılması — süslenmemiştir.** Toplam **−22,07 puan**; tavan-eşdeğer beklenti
0,6324 ⇒ tavanın açıkladığı **−16,87 puan (%76)**, **açıklamadığı −5,20 puan (%24)**.
ADR-0069'un öngörüsü doğrulanmış **ama tam değildir**: model görülmemiş veride **tavanını da
daha kötü kullanmaktadır**. *"Hepsi bileşim"* denmemektedir.

Gözle okuma kapısı: 9/40 çekinmenin dokuzu da okunmuş, açık yanlış pozitif **0** bulunmuştur.

Kaynak: [ADR-0069](docs/adr/0069-kabul-testi-tavan-kullanimi-raporlamasi.md) ·
[ADR-0077](docs/adr/0077-v1-0-verilmedi-v0-3.md) · [koşu](outputs/eval/g16-kabul-testi/OZET.md).

### 3.7 Ürün yolunun kendi sayısı

Yukarıdaki kütle değerleri **ölçüm hattının** sayılarıdır. Vatandaşın fiilen kuracağı yol
(konteynerin HTTP API'si) 2026-09-12'de ilk kez ayrıca ölçülmüştür: 80 DEV sorusu konteynerden
koşulmuş, cevaplar ölçüm hattının hakemiyle puanlanmıştır.

| eksen | ölçüm hattı | **ürün yolu** | fark |
| :--- | ---: | ---: | ---: |
| **Sadık cevap kütlesi** | 0,8011 | **0,7792** | **−2,19 p** |
| `coverage` | 0,9375 | 0,9375 | 0,00 p |
| `A1` (cevaplanan) | 0,8545 | 0,8312 | −2,33 p |
| Uydurulmuş madde | 0/114 | **0/142** | — |
| Tamamen boş cevap | 0/80 | **0/80** | — |
| Kesiklik | 4/80 (%5,0) | 4/80 (%5,0) | — |

Fark **1,75 çözünürlük adımıdır** (n=80 ⇒ adım 1,25 puan): ölçülebilir, ama dar.

> ⚠️ **Bu farkın sebebi ayrıştırılamamaktadır ve bu saklanmamaktadır.** Bu koşuda hakem
> `judge_providers = ["Azure","OpenAI"]` ile servis edilmiş, çıpa koşusu ise
> `LLM_PROVIDER_ORDER=OpenAI` ile pinlenmişti — ve bu pin hiçbir yerde yazılı değildi. Kalem
> düzeyinde sağlayıcı dağılımı ölçülememektedir (`llm_client` sağlayıcıyı global bir kümede
> tutar, kalem kimliği taşımaz). ⇒ *"−2,19 puanın ne kadarı ürün yolundan, ne kadarı hakem
> taşıyıcısından"* sorusunun cevabı **yoktur**. Koşu para harcandığı için tekrarlanmamıştır;
> bundan sonraki koşularda sağlayıcı pinlenir.

Kaynak: `outputs/eval/g24-urun-yolu-kutle-6.3b/` · üretim `outputs/eval/g23-konteyner-urun-yolu-80/`.

### 3.8 Bu skor kartından kurulmayan cümleler

1. **"TEST'te de geçeriz."** Ölçüm DEV'dedir; TEST'in erişim tavanı ≈%75'tir ve ham kütle
   0,5804'tür (§3.6).
2. **"Üç aileli tam bir hakem panelinden geçmiş bir hüküm."** İki aile aynı yönde hükmetmektedir,
   ama κ zayıftır ve değişmemiştir (0,534/0,409 < 0,6); üçüncü aile eklenmemiştir; öz-tercih
   genel olarak ölçülmemiştir (§4.3).
3. **"Model bu kadar iyileşti."** Kazancın büyük kısmı **ölçümden** gelmiştir (§4.6).
4. **"3.1 Flash-Lite için kesikliğe duyarlı hüküm."** O kolun kesikliği **%6,2**'dir, yani
   bizim kolumuzu tam eşikte tutan sınırın **üstünde**; ADR-0040 simetrik uygulanmalıdır.
5. **"Maliyet-normalize parite."** `$/cevap` ölçülmüştür, ama parite bir **Pareto eğrisi**
   iddiasıdır ve tek bir maliyet satırından kurulmaz.
6. **"Kaynaksız da iyiyiz."** Tam tersi ölçülmüştür (§4.5).
7. **Rakip havuzu iki sağlayıcıdandır** (Google · Anthropic); genişlemesinin ön koşulu hakem
   panelidir ([ADR-0072](docs/adr/0072-v1-rakip-havuzu-genisler.md), açık karar **S16**).

---

## 4. Kusurlar ve sınırlar

### 4.1 Açık borçlar

| borç | bugünkü değer | not |
| :--- | :--- | :--- |
| **İsabetsiz atıf (B1)** — **birinci sıra eksen** | **8/80** | Model yanlış maddeye dayanmakta; atıf doğrulanmakta, kapı geçirmekte, cevap yine de soruya oturmamaktadır. **Otomatik vekil ölçüt yoktur ve bu ölçülmüştür:** `faith<0,6` süzgeci 4, *"altın atıflarda yok"* süzgeci 3, **gözle tam tarama 8** bulmaktadır. Hakem tabanlı vekil ölçüt `wrong_ref_rate_micro` bizde **0,0769**, Sonnet-5'te **0,0083**'tür — vekil ölçüt ile göz sayımı **ayrı eksenlerdir**, biri diğerini geçersiz kılmaz |
| **Aşırı çekinme eksenine birim** | — | Gözle düzeltilmiş sayılar depoda üç farklı biçimde kayıtlıdır (§3.3 dipnot ᶜ); tek birime oturtulması gerekir |
| **M2b — en zayıf eksen** | **0,766** | Yalnız distractor verildiğinde model yine de cevaplamaktadır. **Red kapısı** bu kusurun çözümü olarak kurulmuş, 2026-08-05'te eşleşmiş sınavda koşulmuş ve ekseni **kötüleştirmiştir** (0,735 ↔ 0,766). Mekanizması da boş çıkmıştır: `KANUN_YOK 0` · `MADDE_YOK 0` — model etiketi bağlamdan **kopyalamakta**, atıfları doğrulanmakta, kapı onları geçirmektedir ⇒ deterministik kod bu rejimde M2b'yi kapatamaz; borç **eğitime** taşınmıştır |
| **Uzun madde parçalama** | ölçülmedi | Erişim, madde uzunluğunda **U biçimlidir** (en uzun dilimde `recall@10` **0,6667**) |
| **DEV/TEST ayrımı katmanlanmamış** | — | Ayrım kanuna göre kusursuz katmanlıdır ama **madde uzunluğuna göre değil**. Donmuş TEST'i yeniden katmanlamak **reddedilmiştir** — usulü kırar |
| **Aşırı çekinme küçüldü, çözülmedi** | 4/80 | B10 turu **eğitimsiz** kapanmıştır; *"eğitim bunu ne kadar aşağı çekerdi"* hiç ölçülmemiştir |
| **`exact_reject` kör mod dalı** | — | Bugün düzeltilmemiştir: kapının sayısı üretildikten sonra aracı değiştirmek [ADR-0050](docs/adr/0050-verim-kapisi-tahmin-edici-duzeltmesi.md)'nin yasakladığı hareketin sınırındadır. Doğru sıra: ölç → iki okumayı da raporla → **sonraki turda, koşudan önce** düzelt |
| **Arama indeksi yayımlanmadı** | — | Açık borç **G8**; §1.2 |
| **Ürün paketinin `scripts/` bağımlılığı** | — | Açık kusur **11** |
| **Canlı mevzuat API'si** | bağlanmadı | Sözleşme 4/4 doğrulanmış, ürün henüz kullanmamaktadır — borç **B6** |

**Kuantizasyon eğrisi ölçülmüştür** (2026-09-12): `Q4_K_M` (yayımlanan) **0,8011** ·
`Q4_K_M` bugünkü araç zinciriyle **0,7921** (fark −0,90 puan, **çözünürlüğün altında**) ·
`Q5_K_M` **0,8673** (+6,0 adım) · `Q8_0` **0,7909** (−0,1 adım). Eğri **monoton değildir** ve mekanizması
**ölçülmemiştir** — hüküm kurulmamıştır, açık soru olarak durmaktadır. Artefakt kararı ayrıdır:
[ADR-0071](docs/adr/0071-v1-release-artefakti-tek-gguf.md) yürürlüktedir, `Q4_K_M` yayımlı
kalır. Kaynak: [`OZET.md`](outputs/eval/s17-kuantizasyon-egrisi/OZET.md) ·
[#68](docs/record/research_log/2026-09-12-kuantizasyon-egrisi.md).

> **Erişim katmanının kendi gerekçelerinden ikisi de çürütülmüştür, ve bu kartın okunma
> biçimini değiştirir.** (1) *"Atıf doğrulayıcı isabetsizliği kapatır"* — **ölü**: uydurulmuş
> madde numarası 0/114, yani sınıf **boştur**; doğrulayıcının kapattığı kusur zaten
> olmuyordu. (2) *"Red kapısı M2b'yi kapatır"* — **sınandı ve kapı düştü** (yukarıdaki satır).
> Ayakta kalan gerekçe *"retriever olmadan ürün olmaz"* ve ölçülmüş bir dizi mekanizmadır.

### 4.2 Modelin kendi davranış kusurları

| # | kusur | ölçüm |
| :-- | :--- | :--- |
| 1 | **Akıl yürütme izi İngilizce** | 8/8 |
| 2 | **`τ_a` bir şablon öğrendi** — tipik çekinmesi sabit bir cümle | medyan cevap **58 karakter**; risk olarak ön-kayıtlandı |
| 3 | **Model cevaptan önce düşünüyor** | ortalama **782,5** belirteç; `3.5 Flash-Lite` **171,1** belirteçte bitirmektedir |
| 4 | **Kesiklik tam eşikte** | %5,0 ↔ eşik %5; payı yoktur, 4 kalem 1536'ya da sığmamaktadır |
| 5 | **7/80 cevap hiç atıf taşımıyor** | denetlenebilirlik vaadinin doğrudan bedeli |
| 6 | **`A1` tek altın maddeye göre puanlanıyor** | başka **gerçek** bir maddeden doğru cevaplamak sadakatsiz sayılır ⇒ özneler arası kıyasta *"altın getirilen"* satırı kullanılır |

**Kapanmış kusur — boş cevap.** Ürün yolu 2026-09-09'da soruların **%5'inde tamamen boş metin**
döndürüyordu (4/80); sebebi ölçülmüştü: düşünce modu etkinken model `</think>` etiketini
kapatmıyor, bütçenin tamamını düşünce kanalında harcıyor ve HTTP 200 ile boş içerik
döndürüyordu. Bu bir **sonlanmama** sorunudur, bütçe yetersizliği değildir. Ölçüm hattı iki
geçişli **zorunlu kapatma** uygulayarak bunu baştan beri engelliyordu; **ürün yolunda bu koruma
yoktu**. 2026-09-11'de aynı koruma ürün yoluna da eklenmiştir
([ADR-0080](docs/adr/0080-urun-yolu-zorunlu-dusunce-kapatmasi.md), rejim değişikliği, insan
kararı): tamamen boş metin **4/80 → 0/80**, kesiklik **7/80 (%8,75) → 3/80 (%3,75)**.
Değişiklik **cerrahidir**: 80 cevabın yalnız 4'ü bayt olarak değişmiş — tam da bozuk olan
dördü — kalan 76 kalem birebir aynı kalmış, getirilen kaynak kümesi hiçbir kalemde
oynamamıştır. Onarım 2026-09-12'de **konteynerde bağımsız olarak** doğrulanmıştır (boş cevap
0/80, HTTP 200 80/80, kesiklik 4/80).

> **Kalan şerh:** onarım `hakhukuk/servis.py` içinde yaşamaktadır. `llama-server`'ı bu paketi
> kullanmadan **doğrudan** süren bir çağıran, hâlâ özgün kusuru alır.

**Kendi aleyhimize iki kayıt.** (1) Sekiz isabetsizliğin ikisi (id 27 · 42) **yeniden
yazdığımız sorulardadır**: durumu tarif ederken komşu maddenin dili kullanılmış, ADR-0067'nin
yanlılık koruması **ters yönde** işlemiştir. Sayıyı şişirmemiş, aleyhimize çalışmıştır. Sorular
**düzeltilmemiştir**: geri almak, eval sorusunu sonucu gördükten sonra ayarlamak olurdu.
(2) Bir erişim kaybı **geri alınmamıştır** (id 79): eski soru öncülsüzdü ama içindeki
*"eğitim"* sözcüğü maddeyle eşleşiyordu; yeni soru o sözcüksel çıpayı kaybetmiş ve kalem
bulunuyorken kaçmıştır.

### 4.3 Her hüküm-ekseni sayısı tek hakem ailesinin hükmüdür

Bu karttaki bütün hüküm-ekseni değerleri (`A1`, kütle) `openai/gpt-4o-mini`, runs=1'den
gelmektedir. Manşet ekseni ayrıca ikinci bir aileyle okunmuştur; **diğer satırlar
okunmamıştır**.

- **κ ölçülmüş ve eşiğin altında çıkmıştır.** İkinci hakem ailesi (`claude-sonnet-5`) aynı 80
  cevabı yeniden puanlamıştır (üretim yeniden koşulmadı): `tam_sadık` κ = **0,534** ·
  `atıf_temiz` κ = **0,409** — aracın kendi *"makul"* eşiği **0,6**'nın altında.
  `faithfulness` Pearson r = 0,705.
- **Kayma tek yönlüdür:** Anthropic **24/80** kalemde daha düşük, **8/80**'de daha yüksek not
  vermiştir ⇒ rastgele gürültü değil, **sistematik katılık**. `A1` farkı 11,33 puan = gürültü
  tabanının **38 katı**.
- **Manşet hakem seçimine duyarlıdır:** kütle **0,8011** ↔ **0,6940**. `coverage`
  kıpırdamamıştır (hakemden bağımsızdır); farkın tamamı `A1`'den gelmektedir.
- **Öz-tercih genel olarak ölçülmemiştir.** Yalnız Anthropic ailesi için tek hücrelik bir
  gösterge vardır ve **kayırma lehine değildir**: Anthropic hakem kendi ailesinin cevaplarını,
  bizim çapraz-aile kolumuzdan **daha büyük** bir düşüşle cezalandırmıştır (20,03 p ↔ 10,71 p).
  Tek özne, tek hakem, tek koşu ⇒ **gösterge**, kanıt değil; bu kartın hiçbir sayısına
  girmemektedir. Google özne ↔ Google hakem hücresi **aile dışlaması gereği hiçbir bütçeyle
  ölçülemez** ⇒ *"öz-tercih ölçüldü"* cümlesi genel olarak **kurulmaz**.
- **Panel iki ailelidir**, üç değil. Sapmanın sebebi sayıyla kayıtlıdır: bakiye $3,45, ikinci
  hakemle puanlamanın tahmini faturası $2,81, ve donmuş TEST koşusu da aynı bakiyeden
  ödenecekti. **İnsan kararı: harcanmadı.**
- **İnsan-κ kapsam dışıdır.**
- Hakemin yeniden-koşum **gürültü tabanı ~0,3 `A1` puanıdır**; bundan küçük hiçbir fark
  yorumlanmaz. Bu taban **yalnız `A1` için** ölçülmüştür — kütle `= coverage × A1`'dir ve
  `coverage`'ın varyansı o tabanda **yoktur**.

⇒ Bu sayılar **mutlak doğruluk değil, model-vs-model sıralaması** olarak okunmalıdır. *"Tek
hakem"* artık bir usul borcu değil, **büyüklüğü ölçülmüş bir kırılganlıktır**: manşet hakem
değiştiğinde **11 puan** oynamaktadır.
Kaynak: [`KAPPA.md`](outputs/eval/hp-hakem-paneli/KAPPA.md) ·
[#64](docs/record/research_log/2026-09-07-hakem-paneli-iki-aile.md).

### 4.4 Kapsam ve kabul edilen kalıcı bedeller

**Kapsam yalnız yürürlükteki Türkiye Cumhuriyeti kanunlarıdır:** 892 kanun, 40.496 madde.
Yönetmelik, tüzük, KHK ve tebliğ **kapsam dışıdır**. Bu mevzuat bir **anlık görüntüdür**
(`data/corpus/KUNYE.json` → **2026-08-06**); mevzuat değişir, korpus ve ağırlıklar değişmez.

Tek boyut noktası (~4B) ve tek temel model kararının bedelleri — bunlar *"gelecek çalışma"*
diye geçiştirilmez, **kalıcı maliyettir**:

| # | bedel | anlamı |
| :-- | :--- | :--- |
| **a** | **Dış geçerlilik boşluğu kapanmıyor** | *"Bu bulgular bu temel modele mi özgü?"* sorusu **cevapsız kalır** |
| **b** | **Kapasite sorusu ölçülemez** | *"Beceri çatışması kapasite büyüdükçe küçülüyor mu?"* tek boyut noktasında **sorulamaz** |
| **c** | **[ADR-0018](docs/adr/gemma4-12b-dersler.md#adr-0018)'in eğrisi yok** | Maliyet-başarım **eğrisi** yerine tek işaretli **nokta** raporlanmaktadır |
| **d** | **Dış karşılaştırılabilirlik yok** | Sayılar kendi CANON setimizde üretilmektedir ve **kimse bu sette koşamaz**: ne set tamamen yayımlanmıştır ne de üçüncü taraf bir çıpa vardır |

### 4.5 Parametrik bilgide gerideyiz — ve emniyet ağı iddiası ölçülüp çürümüştür

Kör modda (kaynak verilmeden) `A1`: biz **0,4105** ↔ `3.5 Flash` **0,8241** — **iki katı**.
Gemini hattı Türk hukukunu kaynaksızken **bizden çok daha iyi bilmektedir**. Bu doğrudur.

Kör moddaki tam tablo (anti-hedef; **düşük olması istenir**):

| kol | `coverage` | `A1` | **ezber kütlesi** |
| :--- | ---: | ---: | ---: |
| **HakHukuk** | 0,9500 | **0,4105** | **0,3899** |
| `Qwen3.5-4B` (temel) | 0,9750 | 0,4818 | 0,4697 |
| `gemini-3.1-flash-lite` | 0,9875 | 0,6795 | 0,6710 |
| `gemini-3.5-flash-lite` | 1,0000 | 0,7013 | 0,7013 |
| `claude-sonnet-5` | — | — | 0,7772 |
| `gemini-3.5-flash` | 1,0000 | **0,8241** | **0,8241** |

Tablo **araç** okumasıdır — dört öznede kıyaslanabilir tek okuma budur. Bizim kolumuzun ve
temel modelin **gözle** okuması da vardır ve **hüküm iki okumada da aynıdır**: biz **0,4057** ↔
temel model **0,4739**; gözle bakıldığında iki kol da **hiç susmamaktadır** (80/80 konuşur).

**Bu tablodan *"M5'te rakipleri yendik"* cümlesi kurulmaz, iki sebeple.**

**(1) Bu bir anti-hedeftir ve çıpası temel modeldir, rakip değil.**
[ADR-0039](docs/adr/0039-kapi-6-parametrik-sizinti.md) §2 rakip çıpasını değerlendirip
**reddetmiştir**: ölçülmek istenen şey *"modeli aldığımız noktadan kötüye götürmedik mi"*dir.
Kapı okuması budur — biz kaynaksızken temel modelden **daha az** isabetliyiz (ezber kütlesi
0,3899 ↔ 0,4697) ⇒ **kazanç ezberden gelmemektedir**, ki istenen yön tam olarak budur:
*güncellik kütüphanede, ağırlıkta değil.*

**(2) Aynı sayının ikinci yüzü aleyhimizedir ve yazılmadan geçilmez.** Düşük M5 bizim için
*"kaynağa dayanıyoruz"* demektir; ama **tam olarak aynı sayı**, Gemini'nin Türk hukukunu
kaynaksızken bizden çok daha iyi bildiği anlamına da gelir.

**Buna rağmen, buradan çıkarılan makul görünen sonuç ölçülmüş ve çürümüştür.** Kartın bir
önceki sürümü şunu yazıyordu: *"retriever'ın ıskaladığı yerde arkamızda parametrik emniyet ağı
yok ⇒ erişim kalitesi bizde daha kritik."* Ölçüm (2026-09-07) bunu **desteklememiştir**. Dört
öznenin dördü de **aynı 4 kalemi** kaçırmaktadır (id 10 · 21 · 51 · 79) ve o kalemlerde:

| özne | kaçan 4 kalemde `A1` | altın **geldiğinde** `A1` |
| :--- | ---: | ---: |
| **HakHukuk** | **0,000** | **0,885** |
| 3.1 Flash-Lite | 0,125 | 0,756 |
| 3.5 Flash-Lite | 0,196 | 0,836 |
| 3.5 Flash | 0,167 | 0,861 |

⇒ **Parametrik üstünlük, erişimin kaçırdığı yerde işe yaramamaktadır.** Rakiplerin oradaki
sadakati 0,13-0,20'dir — pratikte hepsi başarısızdır; ezberden bildikleri hukuku o kalemlerde
**yanlış kanuna** bağlamaktadırlar (id 10 → altın 6284/10 yerine HMK 393; id 21 → altın TBK 99
yerine VUK 215). **Altın geldiğinde tablo tersine dönmekte, kaynağı en iyi kullanan biz
olmaktayız** (0,885 ↔ 0,861 ↔ 0,836 ↔ 0,756) — ve ürün rejimi tam olarak bu rejimdir.

**Doğru sınır cümlesi şudur:** parametrik bilgi eksikliği bir **emniyet ağı kaybı değildir**,
çünkü ölçüldüğünde kimsede öyle bir ağ çalışmamaktadır. Gerçek sınır **erişimin kendisidir** ve
o sınır dört özne için de aynıdır.

> **DRY şerhi.** Kör mod koşusu `--dry-multiplier 0.8 --dry-base 1.75 --dry-allowed-length 2`
> ile yapılmıştır ([ADR-0073](docs/adr/0073-m5-rejimine-dry-eklendi.md)); kapsam **yalnız
> M5**'tir. DRY bir `llama.cpp` örnekleyicisidir ve Gemini'ye uygulanamaz, dolayısıyla rakip
> içeren hiçbir modda eşitlenemez. **DRY'li M5, DRY'siz M5 ile aynı birimde değildir.** Hüküm
> yalnız bizim kolumuz ile temel model arasında kurulur; iki kol da aynı kuantizasyon,
> taşıyıcı, seed, bütçe, istem ve soru setiyle koşmuş, değişen tek şey **ağırlıklar**
> olmuştur. Rakip kolları bu şerhin dışındadır (DRY'siz koşmuşlardır) ve ayrı okunur — ancak üç
> rakip kolda da döngü **yoktur** ve kesiklik %0 · %0 · %2,5'tir, hepsi eşiğin altındadır.

### 4.6 Kazancın büyük kısmı modelden değil, ölçümden gelmiştir

Faz 0'da (2026-09-06/07) **beş araç kusuru** bulunmuştur. **Eğitim koşusu: sıfır.**
`tgta_v1`'in ağırlıkları hiç değişmemiştir. Kütle **%68,4 → %80,1**'e bu şekilde çıkmıştır.

| # | kusur | ne bulundu | etkisi |
| :-- | :--- | :--- | :--- |
| **1** | **Soru seti** | Kaçırılan 10 kalemin **5'inde soru altın maddeyi belirlemiyordu** — sorular altın maddenin *içinden* üretilmiş, bağlamları sökülmüştü | 13+2 soru yeniden yazıldı; `recall@10` **0,8750 → 0,9375** |
| **2** | **RRF füzyonu** | Kusur BM25'te değil **füzyondaydı**: dört kalemde bir kol altını 0. sırada bulmuştu, `RRF_K=60` ikisini toplayınca ilk 10'un dışına itiyordu | `RRF_K` **60 → 10**; `recall@10` **0,9375 → 0,9500**. Genelleme donmuş TEST'te, **seçimden sonra** doğrulandı |
| **3** | **DEV ↔ TEST bileşimi** | TEST'in `recall@10`'u ~15 puan düşük; sebep zorluk değil **bileşim** | Kabul testinin kütle tavanı ≈%75; raporlama biçimi koşudan **önce** ön-kayıtlandı |
| **4** | **Üretim bütçesi rakiple eşit değildi** | Rakip 1536 ile koşuyordu, biz yaygın durumda **1024** ile. Kod ADR-0043'e sadıktı; kusur protokolün kendisindeydi ve **bizim aleyhimizeydi** (3.1 FL'nin **36/80** kalemi 1024'ü fiilen aşıyordu) | Tek formül, iki tarafta da **1536**. Bu, yayımlanmış bir hükmü **çürüttü** |
| **5** | **Kapı maddesinin çıpası yoktu** | Madde (3) *"M5 ≤ bugünkü"* diyordu, ama `tgta_v1`'in M5'i hiçbir birimde hiç ölçülmemişti — madde **kendi kendine referans veriyordu** | Çıpa ADR-0039'dan okundu (temel model), aynı birimde yeniden koşuldu |

> **Ders:** beş kusurun beşi de *"hata vermeden yanlış sayı üreten"* sınıftandı. **Sayısal
> kapılar beşini de geçirdi**; hepsini **gözle okuma** ya da *"bu sayıyı neyle, hangi birimde
> kıyaslayacağım?"* sorusu yakaladı.

Ayrıca **dedektör üç kez yanılmış, üçünde de aynı yönde** (fazla red): bizim şablonumuzda
14 → **8**, Gemini şablonunda 11 → **7**, kör modda 6 → **0**.

### 4.7 Ara kapı düşmüştür — iddia sürümü buna bağlıdır

2026-08-06'da ön-kayıtlı olan **formüldü** (`merge M2b ≥ 0,90 × temel modelin cevaba-kör
M2b'si`), sayı değil. Tek onarılmış araçla yeniden türetilmiştir:

| nicelik | değer |
| :--- | ---: |
| eşik | **0,8649** |
| merge M2b | **0,766** |
| **fark** | **−9,9 puan** |

Paydalar eşittir (77 ↔ 77) ve eski 0,887 eşiğini de geçememektedir.
[ADR-0050](docs/adr/0050-verim-kapisi-tahmin-edici-duzeltmesi.md) gereği **araç** düzeltilmiş,
**eşik oynatılmamıştır**.

**Sonucu:** bu kapı CP4-CP5 taban harcamasını yetkilendiren kapıydı — **o yetki yoktur**.
Dolayısıyla *"merge, çatışan becerileri ardışık/karışık SFT'den daha iyi koruyor"* iddiası
**kanıtlanmamıştır**. Sürüm bu yüzden ikiye ayrılmıştır
([ADR-0065](docs/adr/0065-bolunmus-surumleme.md)):

```
ÜRÜN sürümü    v1.0            "çalışıyor, indirilebilir, yayımlanan sayı yeniden üretilebilir"
İDDİA sürümü   ara kapıya bağlı kalır — CP4-CP5 yetkisi geri gelmeden ilerlemez
```

**Düşmüş kapı düşmüş kalır.** Gevşetilmemiş, yeniden tanımlanmamıştır.

### 4.8 Açık sorular

Bunlar karara bağlanmamış kalemlerdir; karar mercii insandır.

1. **Set küçük ve dardır: n=80, tek dil, tek alan.** Güven aralıkları buna göre geniştir —
   isabetsizlik 8/80'in Wilson %95 aralığı **[0,0515 – 0,1851]**, yani ≈ **[4/80 – 15/80]**,
   genişlik **13,4 puan**; aşırı çekinme 4/80 için **[0,0196 – 0,1216]** ≈ [2/80 – 10/80],
   genişlik 10,2 puan. *(Burada hesaplandı: `z=1,96`, `n=80`; dosyadan okunmadı.)* Aynı sınıfta
   ölçülmüş ikinci bir örnek: M2'nin kuantumu `1/66 = 1,52 puan`, yani `+0,000` ile `±1 kalem`
   **ayırt edilememektedir**.
   ⇒ *"8/80 ↔ 6/80"* gibi farklar bu genişliğin **çok altındadır**. **Soru:** kaç kalem, hangi
   çeşitlilikte yeterlidir?
2. **DEV ile TEST aynı sınav değildir** (§3.6). **Soru:** ayrım madde uzunluğuna göre de
   katmanlanmalı mı — ve bu, donmuş TEST'i açmadan nasıl yapılır?
3. **Her sayı tek hakem ailesinin hükmüdür** (§4.3). **Soru:** κ hangi eşiğin altında kalırsa
   bu kartın sayıları yeniden koşulur?
4. **Manşet ölçüt bir çarpımdır:** `kütle = coverage × A1`, ve iki çarpan **farklı örnekleme
   birimlerinden** gelir — `coverage` kalem başına, `A1` iddia başına ve yalnız cevaplanan
   kalemler üzerinden makro. ⇒ Çarpıma ikili bir güven aralığı **doğrudan uygulanamaz**.
   **Soru:** kütle için savunulabilir bir belirsizlik ifadesi kurulmalı mı?
5. **Dış karşılaştırılabilirlik yoktur** (§4.4/d). **Seçeneklerden biri** — karar değil —
   CANON'un kamuya açık bir alt kümesini yayımlamaktır. Bedeli de ölçülüdür: donmuş TEST bir
   **kabul testidir** ve yayımlanması onu yakar; DEV ise **seçim yapılmış** settir.
6. **Yer-gerçeği denetimi.** Etiketler sonucu gördükten sonra **değiştirilmemiştir**; bu
   ADR-0067'nin yanlılık korumasının gereğidir. **Soru:** yer-gerçeği denetimi ayrı, **kör** ve
   koşudan **önce** yapılan bir adım olmalı mı?
7. **Ölçüm aracı hâlâ onarım altındadır** (§4.6). **Soru:** *"gözle okuma"* kalıcı bir kapı mı,
   yoksa aracın olgunlaşmasıyla azalması beklenen bir maliyet mi?

---

## 5. Yöntem, dosya ve yeniden üretilebilirlik

### 5.1 Eğitim ve birleştirme

```
ham temel model ──┬── LoRA SFT   (grounding)  → τ_g
                  └── LoRA ORPO  (çekinme)    → τ_a
                                                 │
                          eşzamanlı 2-yollu TIES ┘
                          HAM (norm dengeleme kapalı) · trim_k 0,2 · λ 1,0 · 224/224 tensör
```

| nicelik | değer |
| :--- | ---: |
| `‖τ_g‖_F` (merge anında, bf16 ΔW'den) | **10,4722** |
| `‖τ_g‖_F` (bağımsız artefakttan) | **10,4589** |
| `‖τ_a‖_F` | **1,1806** |
| norm oranı `‖τ_g‖ / ‖τ_a‖` | **8,87×** |
| çatışan parametre oranı | 0,022541 |
| sıfır kalan oran | 0,645798 |

`τ_g` için **iki norm değeri de doğrudur**, biri diğerinin düzeltmesi değildir: ilki merge
anında bf16'da materyalize edilen ΔW'den, ikincisi bağımsız artefakttan ölçülmüştür. %0,13'lük
fark bf16'dan gelir ve kayda **bağımsız çapraz kontrol** olarak geçmiştir. İkisinden biri
"düzeltilmez".

**Neden iki kol bağımsız eğitildi — geçerlilik şartı, üslup tercihi değil.** Görev vektörünün
tanımı `τ = θ_ft − θ_base`'dir ve bu tanım bütün kolların **tek ve aynı `θ_base`**'den
çıkmasını şart koşar. Bir kolu diğerinin **üstüne** eğitmek görev vektörü değil **ardışık SFT**
üretir — yani ölçmek için kurulan şeyi yok eder. Aynı sebeple merge **eşzamanlı k-yollu**dur,
iteratif değil: `TIES(TIES(τg,τa),τr) ≠ TIES(τg,τa,τr)`, çünkü TIES kırpma, işaret seçimi ve
ortalamayı **bütün vektörler üzerinde aynı anda** yapar
([ADR-0027](docs/adr/0027-tasarim-kilitleri-paralel-kol-merge.md)).

**Neden ham TIES — hüküm ölçülerek tersine dönmüştür.**
[ADR-0036](docs/adr/0036-tau-norm-asimetrisi-ve-norm-dengeli-merge.md) norm dengelemeyi **ana
ayar** olarak ön-kayıtlamıştı; gerekçesi *"kollar 8,87× farklı ölçekte, TIES'in işaret seçimi
kütle-ağırlıklı, dengelenmezse küçük kol silinir"* idi. **Öncül doğrulanmış ve hâlâ geçerlidir;
çıkarım ölçülerek yanlış çıkmıştır** ([ADR-0052](docs/adr/0052-merge-norm-dengeleme-hukmu-tersine.md)):

| varyant | M1 kütle | M2b Rej | hüküm |
| :--- | ---: | ---: | :--- |
| **ham TIES** (`tgta_v1`) | **%71,6** | **0,766** | **ana sonuç** |
| norm-dengeli `min` | %53,4 | 0,987 | ablasyon — grounding ezildi |
| norm-dengeli `ortalama` | — | — | dejenere, koşu geçersiz |

Ham TIES `τ_a`'yı **silmemiştir**: `τ_g`'nin M2b çöküşünün **%57,1**'ini onarmıştır
(0,506 → 0,766, sıçrama **+0,26**); dengeleme ise `τ_g`'yi ezmiştir (%71,4 → %53,4).
**Bu satırdaki sayılar `v1` birimindedir** (erişim katmanı **kapalı**, v1 soru seti, 1024
bütçe) ve §3'ün sayılarıyla **kıyaslanamaz**.

**Dağıtım zinciri:** kol başına QLoRA (NF4) → ΔW'yi bf16'da materyalize et → k-yollu merge (tam
ağırlık uzayında, host belleğinde, tensör tensör) → llama.cpp ile **Q4_K_M**'e kuantize et →
GGUF. **Kuantizasyon en sondadır.**

### 5.2 Dosya künyesi

| | |
| :--- | :--- |
| Dosya | `HakHukuk-4B-v0.3-Q4_K_M.gguf` |
| `sha256` | `755e15e92e9f7021934f2d5eada6c1f02fcc92be23f0536b0c2a0a9586e7bffc` |
| Boyut | 2.783.446.720 bayt (2,592 GiB) |
| İç ad (izlenebilirlik) | `tgta_v1-q4_k_m.gguf` |
| Depo | [`Rfetha/HakHukuk-4B-v0.3-Q4_K_M`](https://huggingface.co/Rfetha/HakHukuk-4B-v0.3-Q4_K_M) |

Deponun herkese açık olduğu, **token'sız bir alt süreçte** doğrulanmıştır: dosya inmiş ve
`sha256` bayt bayt tutmuştur (token'lı erişimle **karıştırılmamıştır**).

### 5.3 Yeniden üretilebilirlik

**Tek komut:** `bash scripts/yeniden_uret.sh` — ön koşul denetimi → üretim → **iki geçerlilik
kapısı** (kesiklik %5 · `recall@10` 0,9500) → puanlama → manşet tablo → çıpadan sapma kontrolü.
Belgesi: [`docs/YENIDEN_URETIM.md`](docs/YENIDEN_URETIM.md).

> 2026-09-07'ye kadar manşet değeri **modeli indiren hiç kimse yeniden üretemiyordu**: istem
> üretim betiğinin içindeydi (çözüldü, `hakhukuk/istem.py`), komut zinciri hiçbir yerde tek
> parça yazılı değildi (çözüldü), indeks git'te yok (**hâlâ açık**, borç G8).

**Merge yeniden üretimi:**

```bash
python scripts/merge_ties.py --base Qwen/Qwen3.5-4B \
       --adapter tg=outputs/tg_v1 --adapter ta=outputs/ta_v1 \
       --no-norm-balance --out models/merged/tgta_v1     # ham TIES, ADR-0052
```

`models/merged/` ve `models/gguf/` yeniden üretilebilir; **asıl artefakt adaptördür**
(`outputs/<kol>/`). Adaptörler git'te **değildir** (114 MB > GitHub'ın 100 MB sınırı) ve
yedeklenmemektedir — bilinçli karar: veri, reçete ve seed sabitken yeniden üretilebilirler.

**Rejim değişmezleri — uyuşmazlık hata vermez, kıyası geçersiz kılar:**

```
seed 3407 · max-chunk-chars 900 · thinking on · toplam bütçe 1536 · n 80
veri data/eval/dev/core_hard.jsonl v2 · indeks mevzuat_bge_m3_s2
harness-k 10 · RRF_K 10 · önsözsüz
```

**Donmuş TEST'e (`data/eval/canon/`) dokunulmaz.**

Kaydın tamamı bu depodadır:

```
docs/record/research_log/          ne oldu, hangi sayıyla (kronolojik, bağlayıcı)
docs/adr/                          niye böyle, hangi alternatif elendi
docs/record/kollar.md              artefakt sicili — her kol ve her merge
docs/record/yurutme-tuzaklari.md   "hata vermeden yanlış sayı üretir" listesi
outputs/eval/                      ham değerlendirme çıktıları
```

Araştırma kaydı **negatif ve şaşırtıcı sonuçları da** aynı titizlikle taşır; bu hattın en
yararlı bulgularının birkaçı kendi planlarının çürütülmesidir.

---

## 6. Lisans, veri ve atıf

| | |
| :--- | :--- |
| **Lisans** | **Apache-2.0** — ağırlık + kod + veri + araştırma kaydı, tamamı açık |
| **Temel model lisansı** | `Qwen/Qwen3.5-4B` · Apache-2.0 |
| **Kapsam** | yalnız güncel Türkiye Cumhuriyeti mevzuatı |
| **Yer gerçeği** | Mevzuat.gov.tr |
| **İzinli kaynaklar** | Mevzuat.gov.tr · Resmî Gazete · Yargıtay açık portalı · açık Kaggle/HF setleri |
| **Yasak** | **Lexpera · Kazancı — asla.** Telif zehri |
| **PII** | eğitim verisinde maskelenir |

**Veri sertliği, pahalı öğrenilmiştir:** her veri seti kullanılmadan önce **EDA ile
doğrulanır**. `newmindai/EuroHPC-Legal` kâğıt üstünde mükemmeldi (43K kalem, Apache-2.0), ancak
örnekleme **uyuşmayan soru-cevaplar, uydurma kanunlar ve Osmanlı dönemi içerik** gösterdi ⇒
**reddedildi**. Eksik veri (sade dil, vatandaş nişi, senaryo→kanun) **temellendirilmiş sentetik
üretimle** karşılanır: gerçek madde metni → LLM çift üretir → **doğrulanır**
([`VERI_PLANI.md`](docs/VERI_PLANI.md)).

Örnek soru-cevap çıktıları için ağırlık deposundaki `ORNEK_CEVAPLAR.md` dosyasına bakınız.

```bibtex
@software{hakhukuk2026,
  title   = {HakHukuk: göreve-vektörü birleştirilmiş bir Türkçe hukuk asistanı},
  year    = {2026},
  url     = {https://github.com/Rfetha/Hukuk-SLM},
  license = {Apache-2.0}
}
```
