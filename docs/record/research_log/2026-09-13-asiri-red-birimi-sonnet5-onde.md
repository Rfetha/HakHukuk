# #71 · Aşırı-red ekseni tek birime oturtuldu — yayımlanan bir sayı DEĞİŞTİ, aleyhimize

**Tarih:** 2026-09-13 · **Koşu yok, para harcanmadı** — mevcut çıktı dosyalarının yeniden
okunması · **Paper eşlemesi:** methodology + limitations

## Ne arandı

`MODEL_CARD.md` yeniden yazılırken *aşırı çekinme* satırının **karışık birimde** olduğu
görüldü: bizim hücremiz gözle düzeltilmiş sayıydı (**4/80**), rakip hücreleri ise ham araç
sayısıydı (**8 · 9 · 11**). Kusur 25'in birebir aynı sınıfı — *"aynı satırda iki farklı birim"*.

Satırı tek birime çekmeye çalışınca ikinci bir katman çıktı: eksenin gözle düzeltilmiş
sayıları depoda **dört ayrı yerde dört ayrı biçimde** kayıtlıydı.

| kaynak | yazdığı satır |
| :--- | :--- |
| `f04/KALIBRASYON_ve_OZET.md` *temiz çekinme* | 4 · 5 · 5 · 7 |
| eski `MODEL_CARD` ana satırı | 4 · 8 · 9 · 11 · 4 *(karışık birim)* |
| eski `MODEL_CARD` dipnot ᵈ *çekinme (gözle)* | 5 · 7 · 9 · 9 |
| eski `docs/HF_KARTI.md` ana satırı | 4 · 7 · 9 · 7 · 4 |

## Ne bulundu

**Birim çatışması gerçekti ve adı aynıydı: *"temiz çekinme"*.**

- `f04` kalibrasyonunda *temiz çekinme* = **altın gelmişken susulan** kalemler.
- `hp-rakip-havuzu/GOZLE_KALIBRASYON_sonnet_5.json`'da aynı ad = **tüm** çekinmeler.

Kapsam farkı ham alanlardan **birebir doğrulandı**
(`erisim_davranis_caprazi`, `harness_tablo*.json`):

| kol | altın geldi & sustu | altın yok & sustu | toplam | kalibrasyonun okuduğu |
| :--- | ---: | ---: | ---: | ---: |
| HakHukuk | 4 | 1 | 5 | **5** (tümü) |
| 3.1 Flash-Lite | 8 | 2 | 10 | **8** (yalnız altın-geldi) |
| 3.5 Flash-Lite | 9 | 1 | 10 | **9** (yalnız altın-geldi) |
| 3.5 Flash | 11 | 2 | 13 | **11** (yalnız altın-geldi) |
| Sonnet-5 | 7 | 1 | 8 | **8** (tümü) |

Üç Gemini kolunda 8+9+11 = **28**, ve kalibrasyon dosyasının kendi cümlesi *"28 rakip çekinme
kalemi tek tek gözle okundu"* diyor ⇒ o üç kolun *temiz çekinme*'si **tanım gereği** altın-geldi
biriminde. Bizim ve Sonnet-5'in kalibrasyonu ise **tüm** çekinmeleri okumuş ve ikisinde de
okunan kalemlerin **tam biri** altın hiç getirilmemiş kalem: **id 79** — dört öznenin dördünün
de kaçırdığı dört kalemden biri.

### Yayımlanan sayı değişti

`GOZLE_KALIBRASYON_sonnet_5.json` kendi gerekçesinde şunu **zaten yazmış**:

> *"id 79'da altın zaten getirilmemişti (`altin_sirasi=None`) ⇒ o kalemde çekinme DOĞRU
> davranış."*

Bu cümle dosyada duruyordu ama **satıra hiç yansımamıştı**. Sonnet-5'in dört temiz çekinmesinin
biri altınsız kalemdir ⇒ aşırı-red **4 değil 3**.

**Tek birimdeki doğru satır:**

| kol | aşırı çekinme (altın geldi & sustu, gözle) |
| :--- | ---: |
| HakHukuk | 4/80 |
| `gemini-3.1-flash-lite` | 5/80 |
| `gemini-3.5-flash-lite` | 5/80 |
| `gemini-3.5-flash` | 7/80 |
| **`claude-sonnet-5`** | **3/80** |

⇒ **Sonnet-5 bu eksende bizden İYİ, eşit değil.** Kart *"aşırı çekinmede iki model eşittir"*
diyordu; artık *"Sonnet-5 öndedir"* diyor. Değişim **aleyhimizedir** ve olduğu gibi yazıldı.

## Ders

**Bir kalibrasyon dosyasının gerekçe metninde duran şerh, satıra yansımadıysa yok hükmündedir.**
Doğru sayı türetilebilir hâldeydi — gereken tek şey dosyanın kendi cümlesini okumaktı; dört ayrı
belgeye dört ayrı sayı yazıldı ve hiçbiri bunu yapmadı.

**Koşullu ölçütlerde koşul metrik adına yazılmalı.** *"Temiz çekinme"* adı koşulu taşımıyor;
*"altın geldi & sustu"* taşıyor. Aynı ad iki farklı kapsamda kullanıldığında sayısal kapı
uyarmaz — bu yine *"hata vermeden yanlış"* sınıfıdır.

## Etki

- `MODEL_CARD.md` skor kartı satırı ve dipnot **ᶜ** düzeltildi; §3.2 kalibrasyon tablosuna
  Sonnet-5 satırı ve **kapsam sütunu** eklendi.
- `docs/HF_KARTI.md` bu turda zaten silindi (tek kart kararı); onun 4 · 7 · 9 · 7 · 4 satırı
  hiçbir ham alandan türetilemiyordu ve taşınmadı.
- Açık borç olarak açılan *"eksenin birimi"* kalemi **aynı turda kapandı**.

## Kaynaklar

- `outputs/eval/f02-biz-onsozsuz/harness_tablo.json`
- `outputs/eval/f04-rakip-onsozsuz/harness_tablo_{3_1_flash_lite,3_5_flash_lite,3_5_flash}_nb.json`
- `outputs/eval/f04-rakip-onsozsuz/KALIBRASYON_ve_OZET.md`
- `outputs/eval/hp-rakip-havuzu/harness_tablo_sonnet_5_nb.json`
- `outputs/eval/hp-rakip-havuzu/GOZLE_KALIBRASYON_sonnet_5.json`
- `outputs/eval/hp-rakip-havuzu/GOZLE_ISABETSIZLIK_sonnet_5.md` §3
