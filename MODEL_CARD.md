# HakHukuk-4B

## Summary

HakHukuk-4B is a 4B-parameter Turkish legal assistant that runs on a consumer laptop GPU
(Q4_K_M, about 3 GiB VRAM). Given a question and the text of the relevant statutes, it either
answers and cites the article it relied on, or says that the provided sources do not cover the
question. It is built on `Qwen/Qwen3.5-4B` from two LoRA branches (grounding and abstention)
merged as task vectors with TIES. Scope: Turkish statutes in force (a 2026-08-06 snapshot).
The reported numbers require the retrieval layer that ships with it; without sources the model
produces confident but wrong legal content. It is not legal advice. Weights, code, data and the
full research record are released under Apache-2.0.

## Özet

HakHukuk-4B, tüketici sınıfı bir dizüstü GPU'sunda (Q4_K_M, yaklaşık 3 GiB VRAM) çalışan 4B
parametreli bir Türkçe hukuk asistanıdır. Bir soru ve ilgili mevzuat metni verildiğinde ya
cevaplar ve dayandığı maddeyi belirtir, ya da verilen kaynakların soruyu kapsamadığını söyler.
`Qwen/Qwen3.5-4B` üzerine iki LoRA kolunun (temellendirme ve çekinme) görev vektörü olarak TIES
ile birleştirilmesiyle elde edilmiştir. Kapsam: yürürlükteki Türkiye Cumhuriyeti kanunları
(2026-08-06 anlık görüntüsü). Ağırlık, kod, veri ve araştırma kaydının tamamı Apache-2.0
lisansıyla açıktır.

> **Kullanmadan önce.**
> 1. **Hukuki tavsiye değildir.** Ürettiği her madde numarası
>    [mevzuat.gov.tr](https://www.mevzuat.gov.tr) üzerinden doğrulanması gereken bir iddiadır.
>    Gerçek bir hukuki mesele için avukata danışılmalıdır. Bu ibarenin nihai metni hukukçu
>    görüşü beklemektedir (açık karar S10).
> 2. **Model tek başına bildirilen sonucu üretmez.** Aşağıdaki sayılar, bir arama katmanının
>    ilgili maddeleri bulup modele verdiği koşulda ölçülmüştür. Kaynaksız kullanımda model
>    yüksek güvenle yanlış hukuki içerik üretir (§5.6).

| Geliştirme kümesi, n=80, arama katmanı açık | |
| :--- | ---: |
| Sadık cevap kütlesi (iki hakem ailesi) | 0,694 – 0,801 |
| Uydurulmuş madde numarası | 0 / 114 |
| Kaynak elindeyken gereksiz çekinme | 4 / 80 |
| Yanlış maddeye dayanan cevap | 8 / 80 |
| VRAM (4.096 bağlam) | 3,09 GiB |
| Cevap başına maliyet | $0 (yerel) |

Kütle tek bir sayı olarak değil, aralık olarak bildirilir: aynı 80 cevabı iki bağımsız hakem
ailesi puanlamış, `gpt-4o-mini` 0,8011, `claude-sonnet-5` 0,6940 vermiştir
([ADR-0084](docs/adr/kararlar-0064-0085.md#adr-0084)).

---

## 1. Model nedir

Modele bir soru ve kaynak madde metinleri verilir. Model ya cevaplar ve dayandığı maddeyi
belirtir, ya da kaynakların soruyu kapsamadığını söyler. İkinci davranış bu projenin varlık
sebebidir: hukukta kendinden emin bir yanlış madde numarası, "bilmiyorum" demekten daha
zararlıdır. Model iki beceri için ayrı ayrı eğitilmiştir: verilen metne dayanmak ve metin
yetmediğinde susmak.

Sade dil bir eğitim hedefi değildir. Sade ve kısa cevaba doğru eğitmek önceki hatta denenmiş,
isabeti düşürmüş ve çekinmeyi çökertmiştir
([ADR-0010](docs/adr/gemma4-12b-dersler.md#adr-0010)). Eğitim doğruluk ve çekinmeyi hedefler;
sadeleştirme istem katmanında yapılır.

| | |
| :--- | :--- |
| Temel model | `Qwen/Qwen3.5-4B`, commit `851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`, Apache-2.0 |
| Yöntem | 2 × LoRA (SFT + ORPO), eşzamanlı ham TIES birleştirmesi |
| Dosya | `HakHukuk-4B-v0.5-Q4_K_M.gguf`, 2.783.446.720 bayt (2,59 GiB) |
| `sha256` | `755e15e92e9f7021934f2d5eada6c1f02fcc92be23f0536b0c2a0a9586e7bffc` |
| Ağırlıklar | [`Rfetha/HakHukuk-4B-GGUF`](https://huggingface.co/Rfetha/HakHukuk-4B-GGUF) |
| Arama indeksi | [`Rfetha/HakHukuk-mevzuat-bge-m3-s2`](https://huggingface.co/datasets/Rfetha/HakHukuk-mevzuat-bge-m3-s2) |
| Kod | [github.com/Rfetha/HakHukuk](https://github.com/Rfetha/HakHukuk) |
| Dil | Türkçe |
| Lisans | Apache-2.0 |

**Sürüm numaraları** ([ADR-0065](docs/adr/kararlar-0064-0085.md#adr-0065); 2026-10-10'dan beri dosya
adı ürün sürümünü taşır):

| numara | değer | neyi adlandırır |
| :--- | :--- | :--- |
| artefakt | `HakHukuk-4B-v0.1` (iç ad `tgta_v1`) | ağırlıkların kendisi; kalıcıdır |
| dosya adı | `HakHukuk-4B-v0.5-Q4_K_M.gguf` | yayımlanan GGUF; 2026-10-10'a kadar `HakHukuk-4B-v0.3-Q4_K_M.gguf` adıyla yayımlandı, bayt ve `sha256` değişmedi |
| ürün sürümü | `v0.5` (2026-09-13; 2026-10-10'a kadar `v1.0` adıyla) | ölçüm düzeneğinin ulaştığı doğrulama düzeyi (§4.1) |

`v1` adı bir sonraki eğitim turunun sonundaki sürüme ayrıldı. `v0.5` modelin iyileştiği anlamına gelmez. Ağırlıklar `v0.3`'ten beri bayt bayt aynıdır;
değişen, sürüm kapısının ikinci ve bağımsız bir hakem ailesi altında da geçmiş olmasıdır.

**Kapsam.** Yalnız yürürlükteki Türkiye Cumhuriyeti kanunları: 892 kanun, 40.496 madde,
2026-08-06 anlık görüntüsü. Yönetmelik, tüzük, KHK ve tebliğ kapsam dışıdır. Mevzuat değişir,
ağırlıklar değişmez: güncellik arama katmanının sorumluluğundadır, modelin belleğinin değil.

## 2. Eğitim hattı ve yöntemler

```
Qwen3.5-4B (ham) ──┬── LoRA SFT   (temellendirme) ──► τ_g
                   └── LoRA ORPO  (çekinme)       ──► τ_a
                                                       │
            eşzamanlı 2-yollu TIES, norm dengeleme kapalı ◄┘
            trim_k 0,2 · λ 1,0 · 224/224 tensör · bf16
                                                       │
            llama.cpp ile Q4_K_M kuantizasyonu ──► GGUF
```

| kol | yöntem | veri | ayar |
| :--- | :--- | :--- | :--- |
| `τ_g` temellendirme | SFT | RAFT biçimi: soru + altın madde + aynı kanundan komşu maddeler (zor çeldiriciler). 17.323 eğitim satırı; cevaplar uydurma-alıntı süzgecinden geçmiş, öğretmen etiketleri temizlenmiş (`data/train/raft_scrubbed/`) | 1.083 adım · lr 1e-4 |
| `τ_a` çekinme | ORPO | 726 tercih çifti (kaynak soruyu kapsamıyorken *seçilen* = çekinme, *reddedilen* = temel modelin aynı tuzakta ürettiği gerçek hatalı cevap) + 145 temellendirme tekrar satırı (`data/train/orpo_abstain_cp2c/`) | 70 adım (5 epoch) · lr 1e-5 · β 0,1 · etkin batch 64 |

İki kolda ortak: QLoRA (NF4), `r=16`, `α=32`, tüm doğrusal katmanlar, dropout 0,05, seed 3407.
`τ_g`'nin eğitim koşusu künye disiplininden önce yapıldığı için veri dizini doğrudan kayıtlı
değildir; `raft_scrubbed` davranışsal kanıtla desteklenen okumadır. Ayrıntılı künye:
[`docs/record/kollar.md`](docs/record/kollar.md).

**Neden iki kol ayrı eğitildi.** Görev vektörü `τ = θ_ft − θ_base` olarak tanımlanır; bu tanım
iki kolun aynı `θ_base`'den çıkmasını şart koşar. Bir kolu diğerinin üstüne eğitmek ardışık SFT
olurdu. Aynı sebeple birleştirme eşzamanlıdır: TIES kırpma, işaret seçimi ve ortalamayı bütün
vektörler üzerinde birlikte yapar ([ADR-0027](docs/adr/kararlar-0027-0044.md#adr-0027)).

**Neden ham TIES.** Kolların ölçeği çok farklıdır (`‖τ_g‖` 10,47 ↔ `‖τ_a‖` 1,18, oran 8,87×).
Başta, dengelenmezse küçük kolun silineceği varsayılmış ve norm dengeleme ana ayar olarak
ön-kayıtlanmıştı. Ölçüm bunu tersine çevirdi
([ADR-0052](docs/adr/kararlar-0045-0063.md#adr-0052)):

| varyant | M1 kütle | M2b red | sonuç |
| :--- | ---: | ---: | :--- |
| ham TIES | %71,6 | 0,766 | yayımlanan |
| norm dengeli (`min`) | %53,4 | 0,987 | temellendirme ezildi |
| norm dengeli (`ortalama`) | — | — | dejenere, geçersiz |

Ham TIES çekinme kolunu silmemiş, temellendirme kolunun M2b'deki düşüşünü kısmen onarmıştır
(0,506 → 0,766). Bu tablo arama katmanı kapalı, eski soru setiyle ölçülmüştür; §5'teki
sayılarla karşılaştırılamaz.

**Arama katmanı.** BM25 ve `BAAI/bge-m3` yoğun arama sonuçları RRF ile birleştirilir
(`RRF_K=10`), ilk 10 madde modele verilir, yürürlükten kalkmış maddeler elenir. Gömücü CPU'da,
indeks CPU belleğinde ve diskte çalışır; GPU'ya yalnız model girer. İstemde önsöz yoktur.
Üretim bütçesi 1024 düşünce + 512 cevap belirtecidir.

## 3. Benchmarklarımız

Ölçümler kendi kümemizde yapılmıştır. LegalBench, BigLaw-Bench ve MMLU gibi dış ölçütler
koşulmamıştır: bunlar İngilizce ve common-law temellidir, bir Türk hukuku modelinde düşük not
modelin mi sınavın mı kusuru olduğunu ayırmaz
([ADR-0016](docs/adr/gemma4-12b-dersler.md#adr-0016)). Bunun bedeli, üçüncü taraf bir çıpa
üzerinde koşulmuş bir sayının olmamasıdır.

**Altı mod (CANON, [ADR-0011](docs/adr/gemma4-12b-dersler.md#adr-0011)).** Bu karttaki
sayıların çoğu `h1` ve M5'ten gelir.

| mod | sorduğu soru |
| :--- | :--- |
| M1 / `h1` | Kaynak verildiğinde doğru cevaplıyor ve dayandığı maddeyi belirtiyor mu? (`h1`: kaynakları arama katmanı seçer) |
| M4 | Altın madde kesin olarak verildiğinde tavan nedir? |
| M2 | Yanlış bir madde verildiğinde reddedebiliyor mu? |
| M2b / `h2b` | Yalnız ilgisiz maddeler verildiğinde susabiliyor mu? |
| M3 | Bağlam boşken susabiliyor mu? |
| M5 | Kaynak verilmeden ne kadar konuşuyor? Düşük olması istenir. |

**Kümeler.** Geliştirme kümesi (DEV) `data/eval/dev/core_hard.jsonl`, 80 soru; bütün seçimler
burada yapılır. Donmuş test kümesi (TEST) `data/eval/canon/`; seçim için kullanılmaz, yalnız
sürüm kabulünde ve insan onayıyla bir kez açılır.

**Metrikler.**

| metrik | tanım |
| :--- | :--- |
| Sadık cevap kütlesi | `coverage × A1`. Soruların ne kadarına hem cevap verip hem doğru kaynağa dayandığı. Bağlayıcı metrik budur: cevapsız soru kullanıcı için değersiz, yanlış cevap tehlikelidir |
| `coverage` | Cevaplanan soru oranı. Tek başına yanıltıcıdır: her şeye cevap veren model 1,00 alır |
| `A1` (cevaplanan) | Cevaplanan sorularda iddiaların kaynağa sadakati. Çekinmeyi ödüllendirmemek için yalnız cevaplananlarda hesaplanır |
| `A1` (altın getirilen) | Aynı ölçü, yalnız altın maddenin bağlama girdiği sorularda. Arama hatasını model hatasından ayırır |
| `recall@10` | Altın madde ilk 10 kaynağa girdi mi. Kütlenin tavanıdır |
| Gereksiz çekinme | Altın madde bağlamdayken modelin yine de sustuğu soru sayısı |
| Yanlış maddeye dayanma | Cevabın gerçek ama soruya oturmayan bir maddeye dayanması. 80 sorunun tamamı gözle taranır |
| Uydurulmuş madde numarası | Korpusta karşılığı olmayan kanun/madde atfı. Deterministik doğrulanır; payda doğrulanan atıf sayısıdır |
| Ezber kütlesi (M5) | Kaynak verilmeden üretilen sadık cevap kütlesi. Düşük olması istenir; çıpası temel modeldir |

**Rakipler.** `gemini-3.1-flash-lite`, `gemini-3.5-flash-lite`, `gemini-3.5-flash`,
`claude-sonnet-5`. Sınav eşittir ve bu ölçülmüştür: beş özne aynı 80 soruyu, bayt bayt aynı
kaynaklarla ve aynı bütçeyle almıştır
([ADR-0057](docs/adr/kararlar-0045-0063.md#adr-0057)). Bizim kolumuz yerelde `llama-server`
ile, rakipler kendi API'leri üzerinden koşmuştur.

**Puanlama.** Çekinme tespiti ve atıf doğrulaması hakemsizdir (düzenli ifade ve korpusa karşı
deterministik kontrol). Sadakat gibi yargı gerektiren eksenleri LLM hakemler puanlar: bağlayıcı
hakem `gpt-4o-mini`, ikinci aile `claude-sonnet-5`. Bildirilen sayılarda hiçbir özne kendi
ailesinin hakemiyle puanlanmamıştır. Her sayım adımında kalemler ayrıca gözle okunur.

## 4. Testler

### 4.1 Ölçüm kapıları

**Sürüm kapısı (`v0.5`; ön-kayıttaki adı `v1.0`).** Üç madde, hiçbir rakip sayısı görülmeden 2026-09-06'da ön-kayıtlanmıştır
([ADR-0064](docs/adr/kararlar-0064-0085.md#adr-0064)):

1. Kütle, çıpanın (`gemini-3.5-flash`) kütlesinin en fazla 2 puan altında olabilir.
2. Yanlış maddeye dayanma gerilemez.
3. Ezber kütlesi (M5) temel modele göre yükselmez.
4. Her sayım adımında gözle okuma zorunludur.

Kapı önce `gpt-4o-mini` ile geçmiş, 2026-09-12'de `claude-sonnet-5` altında yeniden okunmuş ve
yine geçmiştir ([ADR-0084](docs/adr/kararlar-0064-0085.md#adr-0084)). Sonuçlar §5.2'de.

**Geçerlilik kapıları.** Bir koşu bunları geçmeden puanlanmaz:

- Kesik cevap oranı en fazla %5 ([ADR-0040](docs/adr/kararlar-0027-0044.md#adr-0040)).
- `recall@10` bilinen değerden sapmaz; sapma arama katmanının değiştiğini gösterir.

**Çekinme dedektörünün kalibrasyonu.** Her rakip ailede çekinme sayılan bütün kalemler gözle
okunmuştur. Dedektör hem Gemini hem Anthropic cevaplarında fazla çekinme saymış (doğru ve atıflı
cevapları şerh cümlesi yüzünden çekinme saymış), bizim kolumuzda ise yanlış pozitif
bulunmamıştır. Karttaki değerler bu düzeltmeden sonraki değerlerdir; ham araç okumaları
[`docs/yontem/OLCUM.md`](docs/yontem/OLCUM.md) §3.5'tedir.

**Donmuş test kabul testi.** TEST 2026-09-09'da insan onayıyla, bir kez açılmıştır. Rejim
geliştirme koşusuyla aynıdır.

**Ürün yolu ölçümü.** Kullanıcının fiilen kuracağı yol (konteynerin HTTP API'si) 80 soruyla
ayrıca ölçülmüş ve ölçüm hattının hakemiyle puanlanmıştır.

### 4.2 Yazılım testleri

`pytest` paketinde 337 test vardır: 335 geçer, 2'si bilinen ve işaretlenmiş başarısızlıktır
(`xfail`). Testler yalnız kodu değil ölçüm rejimini de kapıya çevirir:

- `docker/compose.yaml` ayrıştırılır ve `llama-server` bayraklarının ölçüldükleri değerde olduğu
  sınanır (`test_konteyner.py`).
- Atıf doğrulayıcı, çekinme dedektörü ve dört durumlu sınıflandırıcı kendi testleriyle korunur
  (`test_atif_dogrula.py`, `test_score_abstention.py`, `test_terazi.py`).
- Bulunan her kusur bir regresyon testine dönüştürülmüştür (`test_kusurlar.py`).
- Belgelerdeki bütün göreli bağlantılar ve bu kartın Hugging Face sürümünün üretimi sınanır
  (`test_belgeler.py`, `test_hf_kart.py`).

## 5. Sonuçlar

Aksi belirtilmedikçe: DEV, n=80, arama katmanı açık, k=10, önsözsüz istem, seed 3407, bütçe
1536 belirteç, bağlayıcı hakem `gpt-4o-mini`, KV önbelleği `q8_0`.

### 5.1 Skor kartı

| eksen | HakHukuk-4B | gemini-3.1-flash-lite | gemini-3.5-flash-lite | gemini-3.5-flash | claude-sonnet-5 |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Sadık cevap kütlesi ↑ | 0,6940 – 0,8011 | 0,7058 | 0,7622 | 0,7425 | **0,8348** |
| `coverage` ↑ | **0,9375** | 0,8750 | 0,8750 | 0,8375 | 0,9000 |
| `A1`, cevaplanan ↑ | 0,8545 | 0,7710 | 0,8199 | 0,8269 | **0,8790** |
| `A1`, altın getirilen ↑ | 0,8902 | 0,7900 | 0,8449 | 0,8523 | **0,9031** |
| `recall@10` | 0,9500 | 0,9500 | 0,9500 | 0,9500 | 0,9500 |
| Gereksiz çekinme ↓ | 4/80 | 5/80 | 5/80 | 7/80 | **3/80** |
| Yanlış maddeye dayanma ↓ | 8/80 | 8/80 | **7/80** | 8/80 | **7/80** |
| Uydurulmuş madde numarası ↓ | **0/114** | **0/153** | 4/130 | 4/133 | 2/161 |
| Ezber kütlesi (M5) ↓ | **0,3899** | 0,6710 | 0,7013 | 0,8241 | 0,7772 |
| Cevap başına maliyet ↓ | **$0** | $0,001895 | $0,001152 | $0,009914 | $0,014915 |
| Ortalama belirteç / cevap ↓ | 782,5 | 861,5 | **171,1** | 699,4 | 706,6 |

- `claude-sonnet-5` kütlede, `A1`'de, gereksiz çekinmede ve yanlış maddeye dayanmada öndedir.
  HakHukuk cevaplama oranında, uydurulmuş madde numarasında, ezber kütlesinde ve maliyette
  öndedir.
- Rakip sütunları tek hakemlidir; HakHukuk sütunundaki kütle iki hakem ailesinin aralığıdır.
  Rakip değerleri üç okumanın rakip lehine olanıdır ([`docs/yontem/OLCUM.md`](docs/yontem/OLCUM.md) §3.5).
- Yanlış maddeye dayanma sayıları gözle tam taramadır ve alt sınırdır.
- Maliyet OpenRouter fiyatlarıyla ölçülmüştür (2026-09-07); bizim kolumuz yerelde koştuğu için
  çıkarım bedeli sıfırdır. Hakem bedeli dahil değildir.
- Temel model (`Qwen3.5-4B`) tabloda yoktur: geçerlilik kapısından kalmıştır (kesik cevap
  16/80 = %20, eşik %5). Kaynaklar eklendiğinde uzun, alıntı yapan cevaplar yazıp bütçeye
  sığmamaktadır; aynı model kaynaksız modda yalnız 2/80 kesik verir.

Kaynak: [`KALIBRASYON_ve_OZET.md`](outputs/eval/faz0/f04-rakip-onsozsuz/KALIBRASYON_ve_OZET.md) ·
[`MALIYET.json`](outputs/eval/faz0/f09-maliyet/MALIYET.json) ·
[`BULGU.md`](outputs/eval/gorev/g22-rakip-yeniden-puanlama/BULGU.md).

### 5.2 Sürüm kapısı

| madde | hüküm | değer |
| :--- | :--- | :--- |
| (1) kütle | geçti | 0,8011 ↔ eşik 0,7225, marj +5,86 puan (`gpt-4o-mini`); +7,57 puan (`claude-sonnet-5`) |
| (2) yanlış maddeye dayanma | sağlanıyor | çıpa aynı birimde 8/80 |
| (3) M5 | geçti | temel modele göre −6,82 puan (gözle) / −7,98 puan (araç) |
| (4) gözle okuma | yapıldı | üç sayım adımında; ikisinde araç yanılmıştı |

İkinci hakem altında kendi kütlemiz 10,71 puan, çıpanınki 12,42 puan düşmüştür; kapı çıpaya
göre tanımlandığı için marj genişlemiştir. Mutlak bir eşik bu okumada kapıyı düşürürdü.

### 5.3 Hakem duyarlılığı

| | `gpt-4o-mini` | `claude-sonnet-5` |
| :--- | ---: | ---: |
| Sadık cevap kütlesi | 0,8011 | 0,6940 |
| `coverage` | 0,9375 | 0,9375 |

- Fark tamamen sadakat puanından gelir; `coverage` hakemden bağımsızdır.
- Kayma tek yönlüdür: ikinci hakem 24/80 kalemde daha düşük, 8/80 kalemde daha yüksek not
  vermiştir. Bu rastgele gürültü değil, sistematik katılıktır.
- Uyum zayıftır: Cohen κ 0,534 (tam sadakat) / 0,409 (atıf temizliği), aracın 0,6 eşiğinin
  altında; Pearson r 0,705.
- Hakemin yeniden koşma gürültüsü yaklaşık 0,3 `A1` puanıdır; bundan küçük farklar yorumlanmaz.

Kaynak: [`KAPPA.md`](outputs/eval/hp/hp-hakem-paneli/KAPPA.md).

### 5.4 Geliştirme kümesi ve donmuş test

| | TEST (40) | DEV (80) |
| :--- | ---: | ---: |
| Sadık cevap kütlesi | 0,5804 | 0,8011 |
| Tavan (`recall@10`) | 0,7500 | 0,9500 |
| Tavan kullanımı | 0,7739 | 0,8433 |
| Uydurulmuş madde numarası | 0/52 | 0/114 |
| Yanlış atıf oranı (mikro) | 0,2424 | 0,0769 |
| Gereksiz çekinme | 5/40 | 4/80 |

Düşüş 22,07 puandır. Bunun 16,87 puanı (%76) arama tavanının düşüklüğüyle açıklanır: iki küme
kanuna göre katmanlıdır ama madde uzunluğuna göre değildir; en uzun madde diliminin payı DEV'de
%12, TEST'te %50'dir ve arama uzun maddelerde zayıflar. Kalan 5,20 puan (%24) açıklanmaz; model
görmediği veride tavanını da daha az kullanmaktadır. Koşunun kesiklik oranı
%2,5'tir.

Kaynak: [`OZET.md`](outputs/eval/gorev/g16-kabul-testi/OZET.md) ·
[ADR-0069](docs/adr/kararlar-0064-0085.md#adr-0069) ·
[ADR-0077](docs/adr/kararlar-0064-0085.md#adr-0077).

### 5.5 Ürün yolu

| | ölçüm hattı | ürün yolu (konteyner API) |
| :--- | ---: | ---: |
| Sadık cevap kütlesi | 0,8011 | 0,7792 |
| `coverage` | 0,9375 | 0,9375 |
| `A1`, cevaplanan | 0,8545 | 0,8312 |
| Uydurulmuş madde numarası | 0/114 | 0/142 |
| Boş cevap | 0/80 | 0/80 |
| Kesik cevap | 4/80 | 4/80 |

Fark −2,19 puandır (n=80'de bir adım 1,25 puan). Kaynak:
`outputs/eval/gorev/g24-urun-yolu-kutle-6.3b/`.

### 5.6 Kaynaksız kullanım (M5)

| özne | ezber kütlesi ↓ |
| :--- | ---: |
| HakHukuk-4B | 0,3899 |
| `Qwen3.5-4B` (temel model) | 0,4697 |
| `gemini-3.1-flash-lite` | 0,6710 |
| `gemini-3.5-flash-lite` | 0,7013 |
| `claude-sonnet-5` | 0,7772 |
| `gemini-3.5-flash` | 0,8241 |

M5 bir anti-hedeftir; çıpası rakipler değil temel modeldir. Sorulan, eğitimin modeli ezberden
konuşmaya itip itmediğidir; itmemiştir (gözle okuma da aynı yönde: 0,4057 ↔ 0,4739). Bu
tablodan "rakipleri yendik" sonucu çıkmaz: rakipler Türk hukukunu kaynaksızken bizden iyi
bilmektedir. Bu bilgi arama ıskaladığında bir emniyet ağı da olmamaktadır: HakHukuk ve üç
Gemini kolu altın maddenin gelmediği aynı 4 soruyu kaçırır ve bu sorularda rakiplerin sadakati
0,13-0,20'dir; ezberden bildikleri hukuku yanlış kanuna bağlarlar. Kör mod `llama.cpp`'nin DRY
örnekleyicisiyle koşulduğu için hüküm yalnız HakHukuk ile temel model arasında kurulur
([ADR-0073](docs/adr/kararlar-0064-0085.md#adr-0073)).

### 5.7 Kuantizasyon

| taşıyıcı | sadık cevap kütlesi |
| :--- | ---: |
| `Q4_K_M` (yayımlanan) | 0,8011 |
| `Q5_K_M` | 0,8673 |
| `Q8_0` | 0,7909 |

Eğri monoton değildir ve mekanizması ölçülmemiştir; bu yüzden yayımlanan taşıyıcı
değiştirilmemiştir. Kaynak:
[`OZET.md`](outputs/eval/sprint2-olcum/s17-kuantizasyon-egrisi/OZET.md).

### 5.8 Donanım

`llama-server`, Q4_K_M, KV önbelleği `q8_0`, tek slot:

| bağlam | VRAM | tepe |
| ---: | ---: | ---: |
| 4.096 | 3,09 GiB | 4.068 MiB |
| 32.768 | 3,70 GiB | 4.684 MiB |
| 131.072 | 5,76 GiB | 6.796 MiB |

Kaynak: [`vram_stack_tgta_v1.json`](outputs/eval/_artefakt/vram_stack_tgta_v1.json).

## 6. Sınırlar

**Bilinen kusurlar.**

| sınır | değer | not |
| :--- | :--- | :--- |
| Bağlamdaki yanlış maddeye dayanabiliyor | 8/80 | Atıf gerçektir ve doğrulanır, ama cevap soruya oturmaz. Otomatik bir ölçüsü yoktur; süzgeçler 3-4 bulurken gözle tarama 8 bulur |
| Yalnız ilgisiz kaynak verildiğinde yine cevaplayabiliyor | M2b 0,766 | En zayıf eksen; arama katmanı kapalı birimde ölçülmüştür |
| Altın madde bağlamdayken susabiliyor | 4/80 | Aramanın çözemeyeceği, modelin kendi kararı |
| Uzun maddelerde arama zayıflıyor | en uzun dilimde `recall@10` 0,6667 | Parçalama stratejisi borcu |
| Canlı mevzuata bağlı değil | — | Korpus 2026-08-06 anlık görüntüsüdür |

**Davranış özellikleri.** Model cevaptan önce düşünür (ortalama 782,5 belirteç). Çekinmesi kısa
ve kalıplıdır (medyan 58 karakter). Soruların 4/80'i 1536 belirteçlik bütçeye sığmaz. Cevapların
7/80'i atıf taşımaz; bunlar doğru olabilir ama denetlenemez. Sadakat tek bir altın maddeye göre
puanlanır; başka gerçek bir maddeden doğru cevap vermek ölçümde sadakatsiz sayılır.

**Hakem.** Yargı eksenlerindeki bütün değerler LLM hakem puanıdır. İki hakem ailesi aynı yönde
hükmeder ama uyumları zayıftır (κ < 0,6), panel hedeflenen üç aile yerine iki ailedir ve
öz-tercih genel olarak ölçülmemiştir. Bu sayılar mutlak doğruluk değil, modeller arası sıralama
olarak okunmalıdır.

**Tek boyut noktası.** Yalnız ~4B ölçülmüştür. Bulguların bu temel modele özgü olup olmadığı ve
kapasite büyüdükçe nasıl değiştiği açık sorudur.

**Bu karttan kurulmayan cümleler.**

1. "TEST'te de aynı başarım." Ölçüm DEV'dedir; TEST'te kütle 0,5804'tür (§5.4).
2. "Üç aileli bir hakem panelinden geçmiş hüküm." Panel iki ailelidir ve κ eşiğin altındadır.
3. "`v0.5` modelin iyileştiği anlamına gelir." Ağırlıklar değişmemiştir.
4. "Maliyete göre normalize edilmiş eşdeğerlik." Maliyet ölçülmüştür, ama eşdeğerlik bir maliyet
   satırından değil, bir başarım-maliyet eğrisinden kurulur.
5. "Kaynaksız da iyi çalışır." Tersi ölçülmüştür (§5.6).
6. "M5'te rakipleri yendik." M5'in çıpası temel modeldir (§5.6).
7. "Rakip havuzu sektörü temsil eder." Rakipler iki sağlayıcıdandır (Google, Anthropic).

## 7. Çalıştırma

### 7.1 Konteyner (önerilen)

```bash
git clone https://github.com/Rfetha/HakHukuk && cd HakHukuk
docker compose -f docker/compose.yaml up
```

`indir` kutusu GGUF'u ve arama indeksini sabitlenmiş bir revizyondan indirir, bayt sayısı ve
`sha256` ile doğrular; doğrulama tutmazsa iki servis de başlamaz
([ADR-0078](docs/adr/kararlar-0064-0085.md#adr-0078)). Konteyner aşağıdaki bayrakları zorunlu
kılar; elle kurulumda bunları kullanıcı yazmak zorundadır.

| | |
| :--- | :--- |
| API | `127.0.0.1:8000` |
| `llama-server` | `127.0.0.1:8080` |
| `HF_TOKEN` | isteğe bağlı; depolar herkese açık |
| Gereksinim | NVIDIA GPU, Docker, compose v2.30+ |
| İmajlar | `hakhukuk:1.0.0` 2,08 GB · `llama.cpp:server-cuda-b10902` 6,99 GB |

Servisler yalnız `127.0.0.1` arayüzüne açılır; kimlik doğrulama ve hız sınırı yoktur (açık
karar S9).

### 7.2 Sunucu bayrakları sonucu değiştirir

Bildirilen değerler şu yapılandırmayla üretilmiştir:

```bash
llama-server -m HakHukuk-4B-v0.5-Q4_K_M.gguf \
  -ngl 99 -fa on --no-context-shift \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  -c 8192 --host 127.0.0.1 --port 8080
```

Bayraklar belgelendirme ayrıntısı değildir. Aynı soru, aynı seed ve sıcaklık 0 ile yalnız KV
önbelleği `q8_0`'dan varsayılan fp16'ya alındığında 80 cevabın 65'i değişmiş, kütle
0,8011'den 0,7932'ye inmiş ve yanlış atıf oranı 0,0769'dan 0,1553'e çıkmıştır. Varsayılan KV ile
bildirilen başarımın korunacağı iddia edilmez
([`KARSILASTIRMA.md`](outputs/eval/gorev/g22-kv-fp16/KARSILASTIRMA.md)).
Konteyner bunlara `--reasoning-format deepseek` ekler. Bu bayrak, ölçüm sırasında varsayılan
olan `auto`'nun davranışını değiştirmez, sabitler (ikisinin aynı çıktıyı verdiği ölçülmüştür);
paketin düşünce kanalını ikinci geçişte kapatması bu biçime dayanır
([ADR-0080](docs/adr/kararlar-0064-0085.md#adr-0080)). Elle kurulumda da eklenmelidir.

### 7.3 Python paketi

Paket `llama-server`'ı `127.0.0.1:8080`'de bekler (§7.2) ve arama indeksini depo kökünden
`data/index/mevzuat_bge_m3_s2/` olarak okur; ikisi de `HAKHUKUK_SUNUCU` ve `HAKHUKUK_INDEKS`
ortam değişkenleriyle değiştirilebilir.

```bash
pip install -e .
hakhukuk "Askerlik nedeniyle iş sözleşmesi ne olur?"   # komut satırı
hakhukuk-tui                                           # tek ekran arayüz
pip install -e ".[api]" && hakhukuk-api                # HTTP API
```

```python
from hakhukuk.cekirdek import servis

cevap = servis.answer("Kat malikleri kurulu hangi çoğunlukla karar alır?")
cevap.durum      # Durum.CEVAP | CEKINCELI | SUSKUNLUK | KESIK
cevap.atiflar    # her atıf için: getirilen kaynakta doğrulandı mı
cevap.kaynaklar  # modele verilen maddeler
```

Paket her durumda şunları garanti eder:

- Doğrulanamayan atıf gizlenmez, uyarıyla gösterilir.
- Bütçeye sığmayan cevap `KESIK` durumuyla işaretlenir.
- Arama hiç kaynak bulamazsa model çağrılmaz.
- Yürürlükten kalkmış maddeler modele verilmez.
- Sorumluluk ibaresi her cevapta basılır.

## 8. Yeniden üretim, lisans, atıf

**Yeniden üretim.** `bash scripts/yeniden_uret.sh` bildirilen tek-hakem okumasını (kütle 0,8011)
üretir: ön koşul denetimi, üretim, iki geçerlilik kapısı, puanlama ve çıpadan sapma kontrolü.
Ayrıntı: [`docs/yontem/YENIDEN_URETIM.md`](docs/yontem/YENIDEN_URETIM.md). Değişmezler:

```
seed 3407 · parça kırpma 900 karakter · düşünce açık · bütçe 1024 + 512 · n 80
soru seti data/eval/dev/core_hard.jsonl · indeks mevzuat_bge_m3_s2 · k 10 · RRF_K 10 · önsözsüz
```

Bu değerlerden biri değişirse koşu hata vermez, yalnız karşılaştırma geçersiz olur.

Birleştirme:

```bash
python scripts/egitim/birlestirme/merge_ties.py --base Qwen/Qwen3.5-4B \
       --adapter tg=outputs/tg_v1 --adapter ta=outputs/ta_v1 \
       --no-norm-balance --out models/merged/tgta_v1
```

LoRA adaptörleri git'te değildir (GitHub'ın 100 MB sınırı) ve yedeklenmez; veri, reçete ve seed
sabit olduğu için yeniden üretilebilirler.

**Veri ve lisans.** Lisans Apache-2.0'dır ve ağırlıkları, kodu, veriyi ve araştırma kaydını
kapsar; temel model `Qwen/Qwen3.5-4B` de Apache-2.0'dır. Yalnız kamuya açık ve lisansı uygun
kaynaklar kullanılmıştır (Mevzuat.gov.tr, Resmî Gazete, Yargıtay açık portalı, açık lisanslı veri
setleri); ticari hukuk veritabanları kullanılmamıştır. Eğitim ve ölçüm kümelerindeki soruların ve
dayanaklı cevapların çoğu, bu kaynaklardaki madde metninden `gpt-4o-mini` (OpenAI) ile üretilmiştir;
çekinme cevapları şablondur, reddedilen cevaplar modellerin kendi çıktısıdır. Her veri seti kullanılmadan önce örneklenip
gözle denetlenir. Eğitim verisinde kişisel veriler maskelenmiştir. Örnek cevaplar ağırlık
deposundaki `ORNEK_CEVAPLAR.md` dosyasındadır.

**Daha fazlası.** Ayrıntılı ölçüm tabloları: [`docs/yontem/OLCUM.md`](docs/yontem/OLCUM.md) · kararlar ve
elenen seçenekler: [`docs/adr/`](docs/adr/README.md) · kronolojik ölçüm kaydı:
[`docs/record/`](docs/record/README.md).

```bibtex
@software{hakhukuk2026,
  title   = {HakHukuk-4B: A Turkish legal assistant built by task-vector merging},
  year    = {2026},
  url     = {https://github.com/Rfetha/HakHukuk},
  license = {Apache-2.0}
}
```
