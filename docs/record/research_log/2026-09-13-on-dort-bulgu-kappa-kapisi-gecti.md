# #70 — On dört ölçülmüş bulgu, κ borcu kapandı, kapının üç maddesi yeni birimde GEÇTİ

**Tarih:** 2026-09-12 (ölçüm) / 2026-09-13 (bu kayıt, ölçüm bittikten sonra yazım) ·
**Bedel:** ADIM 6.1-6.7'nin toplamı **≈$5,73** (00-IS-SIRASI durum künyesi) — dökümü:
6.3b `$0,0438` · 6.3c `$0,1210` · 6.4 `$0,2960` · 6.5 `$1,6831` · 6.6b `$2,6212` ·
6.6d `$0,8993` · 6.6/6.6c/6.7 `$0`. **Bu kaydın kendisi (ADIM 6.8, yazım) $0'dır** — yeni
ölçüm yapılmadı, hakem çağrılmadı.
**Kaynak:** `.superpowers/sdd/progress.md` (BULGU-A → BULGU-N, İnsan kararları, Denetimler,
Küçük bulgular) · `outputs/eval/f04-rakip-onsozsuz/` · `outputs/eval/g23-*` · `g24-urun-kutle` ·
`s17-kuantizasyon-egrisi` · `hp-hakem-paneli/KAPPA.md` · `hp-oz-tercih-anthropic/` ·
`hp-rakip-havuzu/GOZLE_ISABETSIZLIK_sonnet_5.md` · `f10-rakip-m5/`
**Kararlar:** [ADR-0084](../../adr/0084-kappa-borcu-kapandi-kapi-yeni-birimde-gecti.md) (bu
kaydın kapı hükmü) — ADR-0077'ye tek satırlık işaretçi düşüldü
**Plan:** [`plans/2026-09-12-v1-son-is.md`](../../superpowers/plans/2026-09-12-v1-son-is.md)
Adım 6.1-6.7 · **Commit aralığı:** `af7a178..12460d7` (6.1-6.7, **53 commit**) + bu kaydın
kendi commit'leri (6.8)

> **Önceki kayıt (#67) nerede bitiyordu:** *"kusurların dördü bizim aynı gün yazdığımız
> koddandı ve hiçbirini test yakalamadı."* **#70 turun geri kalanıdır:** korpus artık kimlikle
> bulunuyor, indeks HF'te public, ürün yolunun kendi kütlesi ilk kez ölçüldü, S17 kuantizasyon
> eğrisi çıkarıldı, κ borcu ADR-0074'ün koşuluyla kapandı ve kapının üç maddesi **iki bağımsız
> hakem ailesi altında da GEÇTİ**. Ağırlıklar bu turda da **hiç değişmedi**.

---

## 1 · Korpus ve indeks — kimlikle bulunma, HF'te public (6.1-6.3)

**BULGU-C — 🚨 en tehlikeli bulgu, henüz zarar vermeden yakalandı.** İki koşunun (`g23`
konteyner, `f02` ölçüm hattı) `id` alanları **farklı sıralamaları** gösteriyordu: soru
**metinleri** 80/80 birebir eşleşirken `id` ile eşleşen kalem **0/80**'di (`g23 id 0` →
`f02 id 34`). `id` üzerinden birleştirme yapılsaydı 6.3b'nin 80 kaleminin **80'i de** yanlış
altın maddeye karşı puanlanır, hata vermezdi. Korunma: birleştirme **normalize edilmiş soru
metni** üzerinden yapıldı ve 80↔80 birebir eşleşme birleştirmeden **önce** iddia edildi.

**BULGU-B — ürün yolunda boş cevap ilk kez ölçüldü: 0/80** (konteynerden, `g23`). `MODEL_CARD`
§7.9'un *"ölçülmedi"* şerhi kapandı; ADR-0080'in iki geçişli zorunlu düşünce kapatması
konteynerde de **tutuyor**. Kesiklik iki hatta **birebir aynı** (4/80 = %5,00, ADR-0040
eşiğinde, payı yok).

**BULGU-D — ürün yolunun kendi kütlesi ilk kez ölçüldü: 0,7792** (çıpa 0,8011, **−2,19 p**,
1,75 çözünürlük adımı). 🚨 **Ayrıştırılamayan karıştırıcı:** bu koşuda `judge_providers`
`["Azure","OpenAI"]`, çıpada `["OpenAI"]` — çıpa `LLM_PROVIDER_ORDER=OpenAI` ile pinlenmişti,
bu koşuda pinlenmedi (tuzak 2.7'nin tekrarı). Kalem düzeyinde dağılım **ölçülemiyor**
(`llm_client.note_provider()` kalem id'si taşımıyor, koddan doğrulandı). *"−2,19 p'nin ne
kadarı ürün yolundan, ne kadarı hakem taşıyıcısından"* sorusu **CEVAPSIZ** kalıyor ve öyle
yayımlanıyor. **Ürün yolunun kütlesi kapı maddesine GİRMEZ** (eşit sınav değil, ön-kayıtlı —
ADIM 6.3b insan kararı).

**BULGU-E — 🚨 yeni tuzak sınıfı (tuzak 7.8, defterde zaten kayıtlı): sağlık kontrolü
başkasının sunucusunu kendi sanıyor.** `cp0_thinking_gen.sh` port **8080**'e bağlanmaya
çalıştı, adres kullanımda olduğu için **başarısız oldu** — ama o portta zaten konteynerin
kendi `llama-server`'ı vardı, health-check ona `200` aldı ve *"sunucu ayakta"* diyerek devam
etti. **8 kalem yanlış modele karşı üretildi**, hiçbir yerde hata vermedi. Kök sebep: 6.3'ün
konteyneri işi bittikten **2 saat sonra da ayakta kalmıştı** ve 15 GB'ın 14'ünü tutuyordu.
Yakalayan şey `/v1/models` + `ps` ile hangi modelin servis edildiğinin doğrulanmasıydı, sayısal
bir kapı değil. Bu turda bir yayımlanmış sayıyı da vurabilirdi — `f02` çıpası aynı betikle
üretilmişti ve o koşuda korunma **aletten değil tesadüften** geldi (8080 boştu). Kod tarafındaki
kalıcı koruması ADIM 6.8.4b'de yazıldı (aşağıda).

**BULGU-F — kusur 33: yeniden üretim kapısı hiçbir koşuda geçmiyordu.** `yeniden_uret.sh`'ın
`recall@10` kapısı var olmayan alanları (`gold_retrieved`/`altin_getirildi`) okuyordu, sayaç
her zaman **0** kaldı ve kapı *"harness OYNAMIŞ"* diye **her zaman** düşüyordu — çıpanın kendi
verisinde bile (`f02`: gerçek 76/80=0,9500, kapının hesabı 0/80). **KAPANDI** (`cc12b6e..9345a2c`):
yeni `scripts/olcum_uretim/recall_kapisi.py`, `harness` eksikse gürültülü `KeyError`. Süit
317 → 323 yeşil. Tuzak **7.7** olarak kayıtlı, kusur **33** ADR-0083 §(A)'da kapandı.

**BULGU-G/H — yayımlanan GGUF bugünkü araç zinciriyle bit-eşit yeniden üretilemiyor (−32
bayt), ama S17 kuantizasyon eğrisi bunu davranışsal olarak ELEDİ.** Dört kollu eğri (aynı
merge, `Q4`@ağustos·`Q4`@bugün·`Q5`@bugün·`Q8`@bugün) ölçüldü: `Q4`@ağustos ↔ `Q4`@bugün fark
**−0,90 p** (0,7 çözünürlük adımı, **BELİRSİZ**) ⇒ 32 baytlık fark davranışa yansımıyor,
yayımlanan sayı çözünürlük içinde yeniden üretilebiliyor. **Eğri MONOTON DEĞİL** (`Q4≈Q8`,
`Q5` ikisinin de üstünde: 0,7921 · 0,8673 · 0,7909); mekanizma `coverage`'da (cevaplanan
78↔75↔74) — kuantizasyon cevabın doğruluğunu değil, **çekinme eşiğini** oynatıyor gibi
görünüyor. **Açıklanmadı, açık soru olarak yazıldı** (tek koşu, n=80). ⛔ Artefakt **değişmedi**
(ön-kayıt, ADR-0071) — eğri bir ifşadır, sürüm önerisi değil.

---

## 2 · κ borcu ve kapı — yeni birimde GEÇTİ (6.4-6.7)

**BULGU-I — κ BORCU KAPANDI.** ADR-0074'ün tek cümlelik koşulu (*"`3.5 Flash` kolunun aynı
ikinci hakemle puanlanması"*) karşılandı: `claude-sonnet-5` `3.5 Flash`'ın 80 cevabını yeniden
puanladı. Kapı **ikinci hakem altında da GEÇTİ**: eşik `0,5983` ↔ bizim `0,6940` ⇒ marj
**+9,57 p** (eşiğe göre) / **+7,57 p** (çıpaya göre). κ kendisi **değişmedi** (0,534/0,409) —
kapanan şey κ değil, **eşit sınavın yokluğuydu**. ⭐ Ön-kaydın en ince maddesi doğrulandı: göz
düzeltmesinden **miras alınan kümedir, puanlar değil** — dört miras kalemin üçü Anthropic
altında 1,0'dan düştü; puanlar da miras alınsaydı çıpa `0,7425 → 0,6496`'ya şişer, marj
`+5,86 p → +6,44 p`'ye inerdi (bu kez **lehimize** çıktı, ama kural koşudan önce yazılmıştı).
Maliyet: gerçek fatura **$1,6831** ↔ tabakalanmış tahmin $1,97 (**%14,6 fazla, güvenli yönde**)
↔ düz ön-tahmin $2,81 (**%60 fazla**) — tuzak 1.11'in ikinci yüzü, bkz. §4.
Tuzak defterine yeni satır: **GÖZ-katı düzeltmesi miras alınmaz** (2.20).

**BULGU-J — kusur 23 KAPATILMADI, ve bu doğru karar.** İki araç iki kez koşuldu, çıktılar
`sha256` **birebir**; deterministik taraf **üç bağımsız sınamada** temiz. Ama orijinal olayın
**kök nedeni hâlâ bulunamadı** ⇒ kapatmaya zorlanmadı, `v2`'ye devir sürüyor. `id65` farkı bu
turda **açıklandı ve kusur 23'ün sınıfı DEĞİL**: hakem katmanı `temp=0`'da bile bit-eşit değil
(betiğin kendi docstring'i zaten söylüyor); kesin kanıt değil, makul çıkarım.

**BULGU-K — öz-tercih ilk kez ölçüldü, sonuç beklenenin TERSİ.** `claude-sonnet-5` **kendi
ailesini** (Sonnet-5 özne) bizden **~2 kat** daha sert cezalandırdı: Δ_sonnet **−20,03 p**
↔ Δ_biz **−10,71 p** (fark 9,32 p = 7,5 çözünürlük adımı). **Kayırma lehine kanıt YOK, ters
yönde** — 6.5'in hükmünü güçlendiriyor. ⛔ Kapsam şerhi: tek özne/tek hakem/tek koşu ⇒
**gösterge, kanıt değil**; yalnız Anthropic ailesi (Google/OpenAI hücreleri aile dışlaması
gereği hiçbir bütçeyle ölçülemez). Tuzak 1.11'in üçüncü yüzü burada da ısırdı (bkz. §4).

**BULGU-L — Sonnet-5'in isabetsiz atfı gözle sayıldı: 7/80 (biz 8/80) — ön-kayıt ÇÜRÜDÜ, ve
çürümesi bulgunun kendisi.** Ön-kayıt *"vekil ölçüte göre aleyhimize belirgin çıkacak"*
diyordu; hakem-tabanlı vekil ölçüt (`wrong_ref_rate_micro`) Sonnet-5'i **0,0083** ile bizim
**0,0769**'umuzun **~9 kat** altında gösteriyordu, göz sayımı gerçek farkın **1 kalem** (1,25 p,
tam bir çözünürlük adımı) olduğunu buldu. ⇒ **Vekil ölçüt bu ekseni ciddi biçimde yanlış temsil
ediyor.** ⚠️ Fark kıl payı: 5 sınır durum sayılmadı, ikisi (id 55·61) insan gözden geçirirse
sayı 9/80'e çıkabilir ve **yön değişebilir** — şerh yayında kalmalı.

**BULGU-M — Sonnet-5'in ezber kütlesi (M5) ölçüldü; üstünlüğümüz KORUNDU.** Havuzda
`BİZ 0,3899` (en düşük/en iyi) · base `0,4697` · `3.1 FL 0,6710` · `3.5 FL-Lite 0,7013` ·
`Sonnet-5 0,7772` (yeni) · `3.5 Flash 0,8241`. Farkımız **38,73 p = 31 çözünürlük adımı** —
**BELİRSİZ değil**. Ön-kayıtlı *"Sonnet-5 altımıza inerse üstünlüğü kaybederiz"* senaryosu
**gerçekleşmedi**; sayı yalın yazıldı. Geçerlilik: kesiklik 3/80 (<%5) ✅.
Koordinatör hatası: şartnameye yanlış sağlayıcı pini yazılmıştı, ajan emsali (`f10/KUNYE.json`:
`gpt-4o-mini`·`OpenAI`) izledi ve varsayımını bildirdi — **doğru davranış** (bkz. §5).

**BULGU-N — 🎯 kapının üç maddesi yeni birimde okundu: GEÇTİ.**

| madde | çıpa | bugün | hüküm |
| :--- | ---: | ---: | :--- |
| (1) kütle · `gpt-4o-mini` | 0,7425 | **0,8011** | ✅ +5,86 p |
| (1) kütle · `claude-sonnet-5` | 0,6183 | **0,6940** | ✅ +7,57 p |
| (2) isabetsizlik | 8/80 | **8/80** | ✅ tanım gereği |
| (3) M5 (çıpa=base) | 0,4697 | **0,3899** | ✅ −7,98 p |

Marjlar çözünürlük bandının (1,25 p) kat kat üstünde; ajan üç maddeyi de **kaynak dosyadan**
okudu, şartnameden kopyalamadı. **DUR ② ateşlenmedi.** ⛔ **Bu `v1.0` DEĞİLDİR** — sürüm
etiketi adım 9'un işi. ⚠️ Açık gerilim ADR-0084'e taşındı: ADR-0032'nin üç aile kuralı hâlâ
2/3'te (Google hakem bütçe nedeniyle kurulmadı) — kapının hükmünü değiştirmiyor, eksiklik
olarak kayıtlı.

**İnsan kararı 2026-09-12 — `MODEL_CARD` kıyas tablosu 6 sütuna çıkarılır.** Bugün 5 sütunlu
ve `claude-sonnet-5`'i taşımıyor; eksik olan sütun **bizi geçen tek rakip** (0,8348 ↔ 0,8011).
Veri elde, $0. ADIM 6.8.3'te uygulandı (aşağıda).

---

## 3 · İki ön-kayıt ÇÜRÜDÜ — ve çürümeleri bulgunun kendisi

1. **6.6c'de vekil ölçüt yanıltıcı çıktı** (BULGU-L): ön-kayıt *"aleyhimize belirgin fark"*
   bekliyordu, gerçek fark **1 kalem**. Hakem tabanlı `wrong_ref_rate_micro` bu ekseni **~9 kat**
   yanlış temsil ediyordu.
2. **6.6d'de kaybetme senaryosu gerçekleşmedi** (BULGU-M): ön-kayıt *"Sonnet-5 altımıza inerse
   M5 üstünlüğünü kaybederiz"* diyordu; Sonnet-5 **0,7772** ile bizim **0,3899**'umuzun çok
   üstünde kaldı, havuzun en düşüğü (en iyisi) **hâlâ biziz**.

İki ön-kaydın da çürümesi kayıp değil, **bulgu**: ikisi de sonuç görülmeden yazılmıştı ve
aleyhe sonuca **açıktı** — sonucun lehimize çıkması, ön-kaydın gereksiz olduğu anlamına gelmez.

---

## 4 · Tuzak 1.11 bu turda DÖRT farklı biçimde ısırdı

| yüz | ne oldu | ölçülen sapma |
| :--- | :--- | ---: |
| **doğrusal ekstrapolasyon** | 2026-09-09'da `n=5`'ten `×16` ekstrapolasyonla κ borcu tahmini | gerçek **%45 eksik** çıkmıştı (önceki tur) |
| **düz ön-tahmin** | 6.5 için düz tahmin $2,81 ↔ gerçek $1,6831 | **%60 fazla** |
| **başka bir öznenin faturasından tahmin** | 6.6b tahmini bizim kolumuzun faturasından türetildi ($1,86); Sonnet-5 665 iddia üretti (bizimki ~273, 2,4×) ↔ gerçek $2,6212 | **%41 fazla** — hakem maliyeti tamamlama uzunluğuyla değil **iddia sayısıyla** ölçekleniyor |
| **farklı bir moddan tabakalama** | 6.6d duman koşusu h1-modunun token profilinden tabakalandı, ama M5-kör modda gerçek uzunluklar üç dilimde de 810-1050'ye sıkıştı | proxy ayrışma **göstermedi** — tabakalama anlamsızlaştı |

Ortak ders: bir maliyet tahmini, **puanlanacak öznenin kendi profilinden** ve **aynı moddan**
türetilmediği sürece — ekstrapolasyon, düz tahmin, başka özne, başka mod, dördü de aynı hatanın
yüzleri.

---

## 5 · Koordinatör hataları — bunlar da yazılır

- **`git add -A` ile yarım dosya commit'i, İKİ KEZ.** İlkinde (`b78d142`) uygulayıcının uçuştaki
  `.dockerignore` düzeltmesi + yarım `urun_yolu_80.json` (65/80 kalem) izleyici commit'e karıştı.
  İkincisinde (`2c4b9fa`, 6.3c) `q8_0` detay dosyasının **43/80 satırlık yarım hâli** yakalandı;
  ajanın kendi commit'i (`a81e9c5`) üzerine tam 80 satırla yazdı, kalıcı zarar yok — ama **aynı
  ders ikinci kez** verilmek zorunda kaldı. Sonuç: **sert kural** — alt ajan koşarken asla
  `git add -A`, dosyalar adıyla eklenir, `outputs/eval/**`'e koordinatör hiç dokunmaz.
- **Şartnameye yanlış sağlayıcı pini yazıldı** (6.6d): `LLM_PROVIDER_ORDER=Anthropic` yazılmıştı,
  emsal `gpt-4o-mini`·`OpenAI` diyordu. Ajan çelişkiyi gördü, emsali izledi, varsayımını açıkça
  bildirdi — **doğru davranış**, ama yanlış pin kullanılsaydı beşinci kol diğer dördüyle
  kıyaslanamaz olurdu.
- **`00-IS-SIRASI.md` yedi adım güncellenmedi** — 6.3b/6.3c/6.4/6.5/6.6/6.6b/6.6c/6.6d planlara
  sonradan eklendiği için iş sırası dosyasının "Sıra" bloğu birkaç kez geriden takip etti; her
  seferinde bir sonraki belge senkron commit'inde yakalandı, kalıcı sapma yok.

---

## 6 · ADIM 6.8.4b — tuzak 7.8'in korunması KODA yazıldı (TDD)

`cp0_thinking_gen.sh` yalnız `/health`'e bakıyordu; tuzağın kendisi bu turda **fiilen ısırdı**
(BULGU-E) ve defterdeki *"korunma"* satırı koda **karşılıksız** kalmıştı. Önce kırmızı test
(ağsız, sahte `curl`): tuzağın bire bir tekrarı (port başka bir modeli servis ediyor) 4/5 testte
reprodüklendi, sonra `dogrula_model_kimligi()` eklenip her iki dala (var olan sunucu / yeni
açılan sunucu) bağlandı — sunucu ayağa kalktıktan sonra `/v1/models` okunur, beklenen GGUF'un
basename'iyle karşılaştırılır, uyuşmazsa gürültülü `die()`. Süit **326 → 331 yeşil**, 2 xfail
(`tests/test_cp0_model_dogrulama.py`, 5 test).

---

## 7 · Turun sayıları

| eksen | değer | kaynak |
| :--- | :--- | :--- |
| test | **331 yeşil, 2 xfail** (6.1-6.7 sonrası 326, 6.8.4b'nin 5 testiyle 331) | `python -m pytest -q` |
| commit | 6.1-6.7: **53** (`af7a178..12460d7`) · 6.8 bu kayda kadar **3** | `git rev-list` |
| harcanan (6.1-6.7) | **≈$5,73** / tavan $8,00 | 00-IS-SIRASI durum künyesi |
| harcanan (6.8, bu kayıt) | **$0** | yeni ölçüm yok, hakem çağrılmadı |
| kapanan kusurlar | **24 · 29 · 33** | ADR-0083, plan `AÇIK KUSURLAR` |
| açık kusurlar | **6** — 5a (`v2`) · 10 · 23 · 25 · 27 (`v2`) · 31 (kayıt) | ADR-0083 §(A) |
| yeni tuzak | **7.7 · 7.8** (önceki turdan) · **2.19 · 2.20** (bu ADIM) | `docs/record/yurutme-tuzaklari.md` |
| ADR | **0084** (yeni) · 0077'ye işaretçi | `docs/adr/` |
| κ | **0,534 / 0,409** — değişmedi | ADR-0074, ADR-0084 |
| ağırlıklar | **değişmedi** | — |

---

## 8 · Ders

Bu turun 14 bulgusunun **hiçbiri eğitimden gelmedi** — üçü ölçüm aygıtının kendi kusuruydu
(BULGU-C'nin `id` çakışması, BULGU-F'nin var-olmayan-alan kapısı, BULGU-E'nin sağlık kontrolü),
biri kalıcı bir tuzak sınıfının **dördüncü tekrarıydı** (1.11'in dört yüzü, §4) ve ikisi
ön-kaydın **aleyhe sonuca açık olduğunu kanıtlayan** çürümelerdi (§3). #67'nin dersi
*"kusurların çoğu bizim aynı gün yazdığımız koddandı"* idi; #70'in dersi bir adım öteye gidiyor:
**bir ölçüm aygıtının güvenilirliği, ikinci bağımsız bir hakemle sınandığında bile, hâlâ kendi
iç tutarlılığından (id eşleşmesi, alan adları, sağlayıcı pinlemesi) ayrı bir eksendir** — κ
borcu kapandı ve kapı iki ailede de geçti, ama bu turda bulunan üç aygıt kusurunun hiçbiri o
κ ölçümüyle **yakalanamazdı**; hepsini yakalayan şey göz okuması, birebir eşleşme iddiası ve
"bu sayı hiçbir koşuda geçmiyorsa şüphe eşiğe değil alete düşer" kuralıydı.
