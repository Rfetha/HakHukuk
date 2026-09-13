---
license: apache-2.0
language:
  - tr
base_model: Qwen/Qwen3.5-4B
pipeline_tag: text-generation
library_name: llama.cpp
tags:
  - legal
  - turkish
  - rag
  - gguf
  - task-arithmetic
---

# HakHukuk-4B v0.3 (Q4_K_M)

Türkçe mevzuat için, tüketici sınıfı bir dizüstü GPU'sunda çalışan 4B parametreli bir hukuk
asistanı. İki LoRA kolu ham temel modelden bağımsız eğitilmiş, görev vektörü olarak ham TIES
ile birleştirilmiş ve Q4_K_M'e kuantize edilmiştir.

> **Dosya adı `v0.3` — sürüm etiketi `v1.0`. İkisi AYNI ŞEY DEĞİLDİR.** Bu depodaki dosya
> (`HakHukuk-4B-v0.3-Q4_K_M.gguf`, `sha256 755e15e9…86e7bffc`) **hiç değişmedi** ve adı
> **kasten değişmeyecek** — değişmemiş bir dosyaya yeni sürüm adı vermek yanıltıcıdır. Buna
> karşın **ürün/iddia sürümü artık `v1.0`'dır** (2026-09-13): sürüm kapısının üç maddesi
> **ikinci, bağımsız bir hakem ailesi altında da** yeniden okundu ve geçti. Bu, **modelin
> iyileştiği anlamına gelmez** — bkz. §6.

Bu kart, ölçülen değerleri ve ölçülmeyen sınırları birlikte bildirmek üzere yazılmıştır.
Aşağıdaki üç bölüm, modeli indirmeden önce okunması gereken kısıtları içerir.

## 1. Model tek başına bildirilen başarımı üretemez

Sadık cevap kütlesi erişim katmanı etkin (harness açık) koşulda ölçülmüştür: model
cevaplamadan önce bir retriever ilgili mevzuat maddelerini bulup bağlama yerleştirmektedir.
⚠️ **Manşet artık tek sayı değil, ARALIKTIR: %69,4-80,1** (`claude-sonnet-5` ↔ `gpt-4o-mini`
hakem ailesi, [ADR-0084](adr/0084-kappa-borcu-kapandi-kapi-yeni-birimde-gecti.md)) — bkz.
§6. GÖZ-katı, bağlayıcı okuma **%80,1**'dir ve bu belgedeki tekil değerler o okumadır.

| Bileşen | Durum |
| :--- | :--- |
| Ağırlıklar (bu depo) | Yayımlandı |
| Kod (retriever, servis, sınıflandırma) | [github.com/Rfetha/Hukuk-SLM](https://github.com/Rfetha/Hukuk-SLM) |
| Arama indeksi (`bge-m3`, 40.496 madde, ~80 MB) | Yayımlanmadı |

Modelin tek başına indirilmesi, ölçümün yapıldığı rejimi vermez. Kaynaksız koşulda modelin
yüksek güvenle yanlış hukuki içerik ürettiği ölçülmüştür. İndeksin dağıtımı açık bir iştir;
korpusun kapsamı yaklaşık 8,4 kat genişleyeceğinden bugünkü indeksin paketlenmesi kısa
ömürlü olacaktır.

## 2. Bilinen kusur: soruların yaklaşık %5'inde cevap boş dönmektedir

80 soruluk geliştirme kümesinde, ürün yolunda (`hakhukuk/servis.py`) 2026-09-09 tarihinde
ölçülmüştür:

| | Ürün yolu | Ölçüm hattı (bildirilen %80,1 bu hattan) |
| :--- | ---: | ---: |
| Kesik veya boş cevap | 7/80 (%8,75) | 4/80 (%5,0) |
| Tamamen boş metin | 4/80 (%5,0) | 0 |

Nedeni ölçülmüştür: düşünce modu etkinken model bazı örneklerde `</think>` etiketini
kapatmamakta, üretim bütçesinin tamamını düşünce kanalında harcamakta ve HTTP 200 ile boş
içerik döndürmektedir. Bu bir sonlanmama sorunudur, bütçe yetersizliği değildir. Ölçüm hattı
iki geçişli zorunlu kapatma uygulayarak bunu engellemektedir; ürün yolunda bu koruma yoktur.

Boş cevap gizlenmemektedir: durum `KESIK` olarak damgalanır ve arayüzde "cevap yarım"
uyarısı gösterilir. Bununla birlikte kullanıcı açısından sonuç boş bir ekrandır. Bu kusur
açık borç olarak kaydedilmiştir; düzeltilmesi ürün davranışını değiştireceğinden yeniden
ölçüm yapılmadan uygulanmayacaktır.

## 3. Nasıl koşulmalı — sunucu bayrakları sonucu DEĞİŞTİRİR

Bildirilen değerler aşağıdaki `llama-server` yapılandırmasıyla üretilmiştir. Bayraklar
belgelendirme ayrıntısı değildir: ölçülmüştür ki farklı bir yapılandırma **farklı cevap**
üretmektedir.

```bash
llama-server -m HakHukuk-4B-v0.3-Q4_K_M.gguf \
  -ngl 99 -fa on --no-context-shift \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  -c 8192 --host 127.0.0.1 --port 8080
```

Kontrollü ölçüm (2026-09-09, aynı soru, aynı kod, seed 3407, sıcaklık 0):

| KV önbelleği | Durum sınıfı | Cevap `sha256` | Uzunluk |
| :--- | :--- | :--- | ---: |
| `q8_0` (bildirilen değerlerin ölçüldüğü) | SUSKUNLUK | `79b6915a…` | 201 |
| varsayılan (fp16) | ÇEKİNCELİ CEVAP | `e97a2b85…` | 622 |

Aynı yapılandırmada üretim yinelenebilirdir (iki koşu, özdeş `sha256`). Değişen tek etken
KV önbelleğinin kuantizasyonudur. Bu farkın 80 kalemlik kümedeki toplam etkisi
**ölçülmemiştir**; dolayısıyla varsayılan KV ile bildirilen %80,1'in korunacağı
**iddia edilmemektedir**.

## 4. Hukuki tavsiye değildir

HakHukuk, hukuk metnini anlaşılır kılmak amacıyla geliştirilmiş bir araştırma artefaktıdır.
Avukat değildir ve çıktısı hukuki tavsiye niteliği taşımaz. Ürettiği her madde numarası,
[mevzuat.gov.tr](https://www.mevzuat.gov.tr) üzerinden doğrulanması gereken bir iddia olarak
değerlendirilmelidir. Mevzuat değişir, ağırlıklar değişmez; güncellik erişim katmanının
sorumluluğundadır.

## 5. Ölçüm sonuçları

Geliştirme kümesi (n=80, erişim katmanı etkin, k=10, önsözsüz istem, hakem `gpt-4o-mini`):

| Ölçüt | Değer |
| :--- | ---: |
| Sadık cevap kütlesi (`gpt-4o-mini`, bağlayıcı) ⁱ | 0,8011 |
| `recall@10` (kütlenin üst sınırı) | 0,9500 |
| Uydurulmuş madde numarası | 0/114 |
| Aşırı çekinme (gözle sayım) | 4/80 |
| İsabetsiz atıf (gözle sayım) | 8/80 |

Donmuş test kümesi (n=40, tek kez açıldı, 2026-09-09):

| Ölçüt | TEST | DEV |
| :--- | ---: | ---: |
| Ham kütle | 0,5804 | 0,8011 |
| `recall@10` (üst sınır) | 0,7500 | 0,9500 |
| Üst sınır kullanımı | 0,7739 | 0,8433 |
| Uydurulmuş madde numarası | 0/52 | 0/114 |

İki değer aynı ölçüt değildir; kümelerin erişim üst sınırları farklıdır. Düşüşün %76'sı küme
bileşiminden kaynaklanmakta, %24'ü kaynaklanmamaktadır. Model, görülmemiş veride üst sınırını
da daha düşük oranda kullanmaktadır.

- **ⁱ** **Manşet artık koşulsuz ARALIKTIR, tek sayı değil:** `%69,4-80,1` (§6). İki bağımsız
  hakem ailesi aynı 80 cevabı puanladı: `gpt-4o-mini` **0,8011** ↔ `claude-sonnet-5` **0,6940**.
  Bu belgedeki tüm tekil `0,8011` değerleri **GÖZ-katı, bağlayıcı** okumadır (`gpt-4o-mini`);
  ikinci ailenin okuması aralığın alt ucudur, ayrı yazılır.

## 6. Sürüm artık v1.0 — ne değişti, ne değişmedi

Sürüm kapısının üç maddesi geliştirme kümesinde geçilmiş ve kabul testi koşulmuştur.
**2026-09-13'te `v1.0` etiketi insan onayıyla verildi** — ama hüküm *"ölçüm aygıtı iki
bağımsız hakem ailesiyle de aynı yönde hükmediyor ve ağırlıklar herkese açık"*tır,
*"model iyileşti"* **değildir**. Aşağıdaki dört sınır birlikte okunmalı — hiçbiri `v1.0` ile
ortadan kalkmadı:

- **Manşet hâlâ koşulsuz bir ARALIKTIR: `%69,4-80,1`** (`claude-sonnet-5` ↔ `gpt-4o-mini`,
  [ADR-0084](adr/0084-kappa-borcu-kapandi-kapi-yeni-birimde-gecti.md)). İki bağımsız hakem
  ailesi aynı 80 cevabı puanladığında kütle **0,8011 → 0,6940** düşüyor; sayının **hakem
  seçimine duyarlı olduğu ölçülmüştür** ve `v1.0` bu aralığı tek sayıya indirmez.
- **İki hakem ailesi aynı yönde hükmediyor, ama uyum hâlâ zayıf:** κ **0,534/0,409**
  (`tam_sadık`/`atıf_temiz`) — **hiç yeniden ölçülmedi** ve aracın **0,6** eşiğinin altında
  kalmaya devam ediyor. Kapanan şey κ'nın kendisi değil, ADR-0074'ün dar koşuluydu (`3.5
  Flash`'ın aynı ikinci hakemle puanlanması — bu koşuldu ve karşılandı).
- **Panel hâlâ İKİ aileli, üç değil** ([ADR-0032](adr/0032-hakem-paneli-uc-aile-ve-aile-dislama.md)
  üçüncü aileyi — Google — öngörüyordu); sapmanın sebebi bütçe ve `v1.0` bunu gidermedi. Öz-tercih
  **genel olarak ölçülmedi** — yalnız Anthropic ailesi için tek hücrelik bir gösterge var (kayırma
  **lehine değil**, ters yönde).
- **Donmuş TEST tek hakemli kaldı** (`gpt-4o-mini`, κ ölçülmedi): kabul testi koşuldu (ham
  kütle 0,5804, tavan `recall@10` 0,7500) ama ikinci bir hakem ailesiyle **doğrulanmadı** ve
  bu turda da doğrulanmadı (insan kararı — donmuş TEST tek hakemli kalır).

Ağırlıklar bu turda **hiç değişmedi** — bu depodaki dosyanın `sha256`'sı `v0.3` etiketiyle
yayımlanan dosyayla **birebir aynıdır** (bkz. bölüm 9). `v1.0`, model performansındaki bir
ilerlemeyi değil, ölçüm aygıtının güvenilirliğindeki bir ilerlemeyi bildirir — ve o
güvenilirlik hâlâ κ eşiğinin altındadır.

## 7. Karşılaştırma — skor kartı

Karşılaştırma tek bir ölçüt üzerinden yapılmamıştır. Beş özne aynı sınava girmiştir: v2 soru
seti (n=80, geliştirme kümesi), önsözsüz istem, erişim katmanı etkin (k=10), üretim bütçesi
1536 belirteç, seed 3407, hakem `gpt-4o-mini`. Sınavın eşit olduğu varsayılmamış, ölçülmüştür
(bölüm 7.3).

| Eksen | **HakHukuk-4B** | `gemini-3.1-flash-lite` | `gemini-3.5-flash-lite` | `gemini-3.5-flash` | `claude-sonnet-5` | `Qwen3.5-4B` (temel) |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Sadık cevap kütlesi ↑ ᵃ ⁱ | 0,6940-0,8011 aralığı | 0,7058 | 0,7622 | 0,7425 | **0,8348** | ölçülemedi ᵇ |
| Cevaplama oranı (`coverage`) | **0,9375** | 0,8750 | 0,8750 | 0,8375 | 0,9000 | ölçülemedi ᵇ |
| `A1`, cevaplanan ↑ | 0,8545 | 0,7710 | 0,8199 | 0,8269 | **0,8790** | ölçülemedi ᵇ |
| `A1`, altın getirilen ↑ | 0,8902 | 0,7900 | 0,8449 | 0,8523 | **0,9031** | ölçülemedi ᵇ |
| `recall@10` (erişim) | 0,9500 | 0,9500 | 0,9500 | 0,9500 | 0,9500 | ölçülemedi ᵇ |
| Aşırı çekinme ↓ ᶜ | **4/80** | 7/80 | 9/80 | 7/80 | **4/80** | ölçülemedi ᵇ |
| İsabetsiz atıf ↓ ᵈ | 8/80 | 8/80 | **7/80** | 8/80 | **7/80** ᵈ | ölçülemedi ᵇ |
| **Uydurulmuş madde numarası** ↓ ᶠ | **0/114** | **0/153** ᶠ | 4/130 | 4/133 | 2/161 ᶠ | ölçülemedi ᵇ |
| Ezber kütlesi (M5) ↓ ᵉ | **0,3899** | 0,6710 | 0,7013 | 0,8241 | 0,7772 ᵉ | 0,4697 |
| Cevap başına maliyet ↓ | **$0** | $0,001895 | $0,001152 | $0,009914 | $0,014915 | **$0** |
| Ortalama belirteç / cevap | 782,5 | 861,5 | **171,1** | 699,4 | 706,6 | ölçülemedi ᵇ |

Sonnet-5 kütle, `A1` ve atıf kalitesi eksenlerinde öndedir. HakHukuk cevaplama oranında ve
uydurulmuş madde numarasında öndedir; aşırı çekinmede iki model eşittir. Fark, kaynak verilen
bir sınavda ölçülmüştür; kaynaksız bir karşılaştırma değildir.

### 7.1 Eksenler ne ölçüyor

| Eksen | Tanım |
| :--- | :--- |
| **Sadık cevap kütlesi** | `cevaplama oranı × A1`. Tüm soru kümesine oranla, model tarafından üretilmiş **ve** kaynaklarca desteklenen cevapların payı. Bağlayıcı ölçüt budur: cevaplanmayan soru vatandaş için değersizdir, bu yüzden çekinmeler de paydada kalır. |
| **Cevaplama oranı** (`coverage`) | 80 sorunun kaçında modelin çekinmek yerine cevap ürettiği. Tek başına bir başarı ölçütü değildir; yanlış cevap da bu oranı yükseltir. |
| **`A1`, cevaplanan** | Yalnız cevap verilen kalemler üzerinde hakemin ölçtüğü sadakat makro ortalaması: cevaptaki iddiaların verilen kaynaklarca desteklenme oranı. Çekinmeler bu ortalamaya **girmez** — girerse ölçüt çekinmeyi ödüllendirir. |
| **`A1`, altın getirilen** | Aynı ölçüt, yalnız doğru maddenin bağlama **girdiği** kalemlerde. Erişim başarısızlığını modelin kusurundan ayırır. |
| **`recall@10`** | Doğru maddenin, erişim katmanının getirdiği ilk on kaynak arasında bulunma oranı. Modelden bağımsızdır ve **kütlenin üst sınırıdır**: bağlama girmeyen maddeden doğru cevap üretilemez. |
| **Aşırı çekinme** | Doğru madde bağlamda olduğu hâlde modelin cevap vermediği kalem sayısı. Erişim kusuru değildir; modelin kendi kararıdır. Değerler gözle sayılmıştır. |
| **İsabetsiz atıf** | Cevabın, bağlamdaki **yanlış** maddeye dayandırıldığı kalem sayısı. Madde uydurma ile karıştırılmamalıdır: atfedilen madde gerçektir, ancak soruyu karşılamaz. Beş öznede 80/80 kalem tek tek gözle okunarak sayılmıştır. |
| **Uydurulmuş madde numarası** | Cevapta anılan ve korpusta **karşılığı bulunmayan** madde numarası sayısı. Hakem değil, deterministik doğrulama sayar. Payda **`DOGRULANDI`** sayısıdır (bölüm 7.4, dipnot ᶠ) — kolun toplam atıf sayısı değil. |
| **Ezber kütlesi (M5)** | Modele **kaynak verilmeden** ölçülen kütle. Anti-hedeftir: yüksek değer, modelin ezberden hüküm kurduğunu gösterir ve mevzuat değiştiğinde sessizce yanlışa döner. |
| **Cevap başına maliyet** | Bir cevabın çıkarım bedeli. Yerel model tüketici sınıfı bir GPU'da koştuğu için sıfırdır; rakiplerde OpenRouter liste fiyatından ölçülmüştür. Hakem bedeli bu satıra dâhil değildir. |
| **Ortalama belirteç / cevap** | Cevap başına üretilen belirteç sayısı, düşünce kanalı dâhil. Maliyet ve gecikme ekseni; doğruluk ölçütü değildir. |

Bu ölçütlerin hiçbiri standart bir ölçüt kümesinden gelmez; tanımları bu projeye aittir ve
kaynakları GitHub deposundaki `docs/adr/` ile `docs/record/` altındadır.

### 7.2 Kütlenin üç okuması

Ana tabloda bağlayıcı olan (GÖZ-katı) okuma yer almaktadır. Üçü birlikte:

| Kol | ALET (ham) | GÖZ-orta (yanlış pozitif düzeltilmiş) | GÖZ-katı (bağlayıcı) |
| :--- | ---: | ---: | ---: |
| HakHukuk-4B | 0,8011 | 0,8011 | 0,8011 |
| `gemini-3.1-flash-lite` | 0,6746 | 0,7058 | 0,7058 |
| `gemini-3.5-flash-lite` | 0,7174 | 0,7403 | 0,7622 |
| `gemini-3.5-flash` | 0,6925 | 0,7050 | 0,7425 |
| `claude-sonnet-5` | 0,7911 | 0,8223 | **0,8348** |

Bağlayıcı okuma olarak en muhafazakâr olan seçilmiştir; bu okumada rakiplerin çekinceli
cevapları da cevap sayılır, dolayısıyla onların kütlesi en yüksek, HakHukuk'un farkı en dar
çıkar. HakHukuk üç okumada da aynıdır: kendi kolunda yanlış pozitif ve çekinceli cevap yoktur
(80 kalem gözle okunmuş, araç ile göz arasındaki fark sıfır bulunmuştur).

Aletin ham okuması HakHukuk'u Sonnet-5'in önünde göstermektedir (0,8011'e karşı 0,7911). Bu
okuma kullanılmamıştır: çekinme dedektörü Sonnet-5 kolunda sekiz çekinmenin üçünü yanlış
saymaktadır (tam ve atıflı üç doğru cevap), HakHukuk kolunda ise yanlış pozitif yoktur.
Düzeltme uygulandığında sıralama değişmektedir.

### 7.3 Sınavın eşit olduğunun kanıtı

| Eksen | HakHukuk | Gemini kolları | Sonnet-5 |
| :--- | ---: | ---: | ---: |
| `recall@1 / @3 / @5 / @10` | 0,5250 / 0,7625 / 0,8250 / 0,9500 | aynı | 0,5250 / 0,7625 / 0,8250 / 0,9500 |
| Kesik cevap | 4/80 | 4/80 | 4/80 |
| Girdi belirteci (toplam) | 193.042 | 193.042 | ölçülmedi |
| İstem | önsözsüz | aynı | aynı |
| Üretim bütçesi | 1536 | 1536 | 1536 |

### 7.4 Dipnotlar

- **ᵃ** Rakip sütunlarında bağlayıcı GÖZ-katı okuması yazılıdır (bölüm 7.2).
- **ᵇ** Temel model ölçülmedi değil, **ölçülemedi**: sınava sokulmuş ve geçerlilik kapısından
  kalmıştır (kesik cevap 16/80 = %20, eşik %5), dolayısıyla hakem çağrılmamıştır. Nedeni
  ölçülmüştür: temel model uzun, kaynak alıntılayan cevaplar üretmekte ve 1536 belirtece
  sığmamaktadır. Aynı model kör modda yalnızca 2/80 kesik vermektedir; şişiren etken
  kaynakların kendisidir.
- **ᶜ** Tanım tüm öznelerde aynıdır: altın madde bağlama girmiş, model yine de çekinmiştir.
  Değerler gözle düzeltilmiştir; ham araç sayıları HakHukuk için 5/80, Sonnet-5 için 7/80,
  Gemini kolları için 8-11/80'dir.
- **ᵈ** İsabetsiz atıf, **beş** öznede 80/80 kalemin gözle taranmasıyla sayılmıştır.
  ~~Sonnet-5 kolunda bu tarama yapılmamıştır ve tahmin yazılmamıştır.~~ **2026-09-12'de tamamlandı
  (ADIM 6.6c):** Sonnet-5 kolunda **7/80** (5 sınır durum sayılmadı — gerekçesi
  [`GOZLE_ISABETSIZLIK_sonnet_5.md`](../outputs/eval/hp-rakip-havuzu/GOZLE_ISABETSIZLIK_sonnet_5.md)
  §2'de). Ön-kayıtlı beklenti tutmadı: hakem tabanlı vekil ölçüt (`wrong_ref_rate_micro`)
  Sonnet-5'i 0,0083 ile bizim 0,0769'umuzun çok altında gösteriyordu, göz sayımı ise Sonnet-5'i
  bizim **8/80**'imizin altında (7/80) buldu — vekil ölçüt ile göz sayımı burada **ayrı
  eksenlerdir**, biri diğerini geçersiz kılmaz. Bu eksen HakHukuk'un açık borcudur.
- **ᵉ** Ezber kütlesi, kaynak verilmeden ölçülen anti-hedeftir; düşük olması istenir.
  ~~Sonnet-5 bu modda koşulmamıştır.~~ **2026-09-12'de tamamlandı (ADIM 6.6d):** Sonnet-5
  **0,7772** — havuzun içinde, `3.5 Flash-Lite` (0,7013) ile `3.5 Flash` (0,8241) arasında;
  bizim **0,3899**'umuzun **çok üstünde** (fark 38,73 p, çözünürlük 1,25 p'nin çok üstünde
  ⇒ **BELİRSİZ değil**). ⇒ **Havuzun en düşüğü (en iyisi) hâlâ BİZ** — Sonnet-5 bizden düşük
  çıkmadı, ön-kayıtlı kaybetme senaryosu **gerçekleşmedi**. Aynı rejim (`f10-rakip-m5/KUNYE.json`),
  hakem `openai/gpt-4o-mini` · `LLM_PROVIDER_ORDER=OpenAI` (ADR-0032 aile dışlaması), n=80,
  kesiklik 3/80=%3,75 (geçerlilik eşiği %5'in altında). Kaynak: [`f10-rakip-m5/KUNYE.json`](../outputs/eval/f10-rakip-m5/KUNYE.json).
- **ᶠ** **Bu satırın birimi tüm kolonlarda ortaktır:** pay = `MADDE_YOK + KANUN_YOK`,
  payda = **`DOGRULANDI`** (o koldaki toplam atıf sayısı DEĞİL). `gemini-3.1-flash-lite`
  hücresi 2026-09-11'de **yeniden puanlandı** (atıf doğrulayıcı parantezli kanun adlarını
  yanlış kanuna çözüyordu): `1/152` → `0/153`. `claude-sonnet-5` hücresi **kusur 25 kapandı,
  2026-09-13**: eskiden paydası **toplam atıf** (163) idi, `2/163` yazıyordu; yeniden puanlama
  **yapılmadan**, aynı sayımın (`DOGRULANDI` 161 · `MADDE_YOK` 2 · `KANUN_YOK` 0) `DOGRULANDI`
  paydasıyla ifadesine çevrildi ⇒ `2/161`. Kaynaklar:
  [`g22-rakip-yeniden-puanlama/BULGU.md`](../outputs/eval/g22-rakip-yeniden-puanlama/BULGU.md) ·
  [`harness_tablo_sonnet_5_nb.json`](../outputs/eval/hp-rakip-havuzu/harness_tablo_sonnet_5_nb.json).

Bu değerlerin hiçbiri standart bir ölçüt kümesinden gelmemektedir. Tümü, Türkçe ve güncel
Türkiye Cumhuriyeti mevzuatı üzerine kurulmuş kendi CANON kümemizden üretilmiştir. MMLU,
LegalBench ve BigLaw-Bench gibi dış ölçütler koşulmamıştır; bu bir eksiklik değil kayıtlı bir
karardır (söz konusu kümeler İngilizce ve ABD common-law temellidir).

## 8. Yöntem

İki LoRA kolu ham temel modelden bağımsız eğitilmiştir; görev vektörü tanımı
(`τ = θ_ft − θ_base`) bunu zorunlu kılar. Birleştirme, eşzamanlı k-yollu ham TIES ile tam
ağırlık uzayında yapılmış, kuantizasyon en sona bırakılmıştır. Norm dengeleme ana sonuç değil
ablasyondur; ölçüm, önceki kararın çıkarımını tersine çevirmiştir.

## 9. Dosya

| | |
| :--- | :--- |
| Dosya | `HakHukuk-4B-v0.3-Q4_K_M.gguf` |
| `sha256` | `755e15e92e9f7021934f2d5eada6c1f02fcc92be23f0536b0c2a0a9586e7bffc` |
| Boyut | 2.783.446.720 bayt (2,592 GiB) |
| İç ad (izlenebilirlik) | `tgta_v1-q4_k_m.gguf` |

## 10. Sınırlar

- Kapsam yalnızca yürürlükteki Türkiye Cumhuriyeti kanunlarıdır (892 kanun, 40.496 madde).
  Yönetmelik, tüzük, KHK ve tebliğ kapsam dışıdır. **Bu mevzuat bir ANLIK GÖRÜNTÜdür**
  (`data/corpus/KUNYE.json` → **2026-08-06**); mevzuat değişir, korpus ve ağırlıklar
  değişmez.
- Tek boyut noktası (~4B) ölçülmüştür; bulguların bu temel modele özgü olup olmadığı sorusu
  açıktır.
- Yanlış kaynağa atıf oranı 0,0769'dur (Sonnet-5: 0,0083). Model madde numarası
  uydurmamakta, ancak mevcut ve yanlış maddeye atıf yapabilmektedir. Açık borç.
- Manşet ekseni (kütle) iki bağımsız hakem ailesiyle okunmuştur (§6); tablodaki diğer değerler
  hâlâ tek hakem ailesinin hükmüdür. Panel iki aileli kalmıştır, üç değil; κ **0,534/0,409**,
  aracın **0,6** eşiğinin altındadır ve bu turda yeniden ölçülmemiştir.

Örnek soru-cevap çıktıları için bu depodaki `ORNEK_CEVAPLAR.md` dosyasına bakınız. Tam
araştırma kaydı, reddedilen alternatifler ve her değerin kaynağı
[github.com/Rfetha/Hukuk-SLM](https://github.com/Rfetha/Hukuk-SLM) deposundadır.
