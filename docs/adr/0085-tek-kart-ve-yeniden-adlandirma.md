# ADR-0085 — Tek model kartı, ürün tonu, ve iki yeniden adlandırma (grill kararı 6 TERSİNE ÇEVRİLDİ)

**Tarih:** 2026-09-13 · **Statü:** ✅ yürürlükte · **Karar:** insan
**Bağlı:** [ADR-0065](0065-bolunmus-surumleme.md) (bölünmüş sürümleme — bu kararın dayanağı) ·
[ADR-0071](0071-v1-release-artefakti-tek-gguf.md) (yayın artefaktının adlandırma kalıbı) ·
[ADR-0078](0078-konteyner-dagitimi-rejim-kilidi.md) (pinli revizyon + `sha256` kimlik kapısı) ·
[ADR-0083](0083-kusur-sicili-adrye-tasindi.md) §(A) kusur 10 *(grill kararı 6 — **bu ADR onu
tersine çevirir**)* · [ADR-0084](0084-kappa-borcu-kapandi-kapi-yeni-birimde-gecti.md) (`v1.0`)
**Kaynak:** [#71](../record/research_log/2026-09-13-asiri-red-birimi-sonnet5-onde.md) ·
tuzak **2.21** · commit `9e3d9bc` · `6483c36` · `61bae1b`

## Bağlam — iki kart iki kez sessizce ayrıştı

Depo iki model kartı taşıyordu: `MODEL_CARD.md` (depo içi, derin) ve `docs/HF_KARTI.md`
(HF'e `README.md` olarak yüklenen). İkisi **elle** güncelleniyordu ve ayrışma **ölçülebilir
hâle geldi**:

| bayat yer | ne diyordu | gerçek |
| :--- | :--- | :--- |
| `HF_KARTI` §2 | *"soruların yaklaşık %5'inde cevap boş dönmektedir"* · *"ürün yolunda bu koruma yoktur"* | [ADR-0080](0080-urun-yolu-zorunlu-dusunce-kapatmasi.md) bunu **2026-09-11'de kapattı** (4/80 → 0/80); konteynerde 2026-09-12'de bağımsız doğrulandı |
| `HF_KARTI` §3 | *"Bu farkın 80 kalemdeki toplam etkisi **ölçülmemiştir**"* | **2026-09-11'de ölçüldü** (`g22-kv-fp16`): 65/80 bayt değişti, kütle 0,8011 → 0,7932, `wrong_ref_rate` 0,0769 → 0,1553 |
| `MODEL_CARD` §7.9 ↔ §8 | §7.9 *"düzeltilmedi, açık borç"*, §8 aynı kusurun **0/80** ölçüldüğünü | dosya **kendi içinde çelişiyordu** |
| `MODEL_CARD` (5 yer) | *"arama indeksi **yayımlanmadı**, açık borç G8"* | `Rfetha/HakHukuk-mevzuat-bge-m3-s2` **public dataset**; `indir.py` onu zaten **varsayılan** olarak kullanıyor |

Birinci ve ikinci satır **HF'te yayındaydı**: depo, düzeltilmiş bir kusuru herkese açık biçimde
*"açık"* diye ilan etmeye devam ediyordu.

## Karar 1 — TEK KART, ve HF sürümü ÜRETİLİR

`MODEL_CARD.md` **tek kaynaktır**. `docs/HF_KARTI.md` **silindi**.

Kalan dosya `MODEL_CARD.md` seçildi çünkü: konvansiyonel ad · GitHub kökünde görünür ·
**82 atıf** taşıyordu (16'sı temizlenmeyen `docs/adr/` + `docs/record/` içinde) ·
`tests/test_belgeler.py`'ın `CANLI` listesinde. `HF_KARTI`'ya **canlı atıf yoktu** — hepsi
kayıt katmanındaydı, dolayısıyla silinmesi ölü bağlantı üretmedi.

**Ayrışma yapısal olarak imkânsızlaştırıldı:** `scripts/hf_kart.py` HF'in `README.md`'sini
`MODEL_CARD.md`'den **üretir** — YAML ön bilgisini ekler, göreli bağlantıları mutlaklaştırır
(HF deposunda `docs/` ve `outputs/` yoktur; göreli bağlantı orada **sessizce ölür**).
Dört testle korunur (`tests/test_hf_kart.py`).

### Elenen seçenekler

- **`HF_KARTI` kalsın, `MODEL_CARD` silinsin** — ilk insan tercihiydi, **ölçüm sonrası
  değişti**: 82 atıfın 16'sı temizlenmeyen katmanda, ve `tests/test_belgeler.py` kırmızıya
  düşerdi.
- **İkisi de kalsın** — ayrışmanın kendisi bu kararın sebebi.

## Karar 2 — Kart ÜRÜN BELGESİDİR, onarım günlüğü değil

Kart, **yürürlükteki hâli** anlatır. Üstü çizili düzeltmeler, *"ONARILDI 2026-09-11"* damgaları
ve *"eski cümle silinmedi"* şerhleri karttan **çıkarıldı**; tarihçe `docs/adr/` ve
`docs/record/`'da **tam olarak durur**.

⚠️ Bu, `CLAUDE.md`'nin *"çelişkiyi iki yerde damgala, sessizce üzerine yazma"* kuralına
**aykırı değildir**: kural **araştırma kaydını** bağlar. Damga defterde kalır; kart okunacak
bir belgedir. Kartın iki yerde sessizce bayatlaması zaten **bu yığılmanın** sonucuydu — 1.200
satırlık üstü çizili tarihçe içinde iki yanlış cümle kimsenin gözüne çarpmadı.

Karttan çıkarılan her bölümün yeni evi **yazılı olarak** doğrulandı; yalnız biri hiçbir yerde
yoktu ve **taşındı**: *"Açık sorular"* bölümünün Wilson %95 aralıkları (`z=1,96`, `n=80`)
**kartın içinde hesaplanmıştı** ⇒ [ADR-0083](0083-kusur-sicili-adrye-tasindi.md) **EK-2**.

## Karar 3 — İKİ YENİDEN ADLANDIRMA

| | eski | yeni |
| :--- | :--- | :--- |
| GitHub deposu | `Rfetha/Hukuk-SLM` | **`Rfetha/HakHukuk`** |
| HF model deposu | `Rfetha/HakHukuk-4B-v0.3-Q4_K_M` | **`Rfetha/HakHukuk-4B-GGUF`** |
| GGUF **dosya adı** | `HakHukuk-4B-v0.3-Q4_K_M.gguf` | **değişmedi** |

**Gerekçe.** GitHub adı bir **proje evresi** adıydı (*"hukuk SLM'i"*), HF ise ürün adını
taşıyordu; iki ad buluşturuldu. HF tarafında sürüm+kuantizasyon **depo adından dosya adına**
indi — ADR-0071'in *"model + boyut + sürüm + kuantizasyon"* kalıbı **dosya** için geçerlidir,
depo için değil; depo adının tek bir kuanta kilitlenmesi S17'de ölçülen `Q5_K_M`/`Q8_0`
varyantlarına yer bırakmıyordu.

**Ürün adı `HakHukuk` DEĞİŞMEDİ** ve değişmesi önerilmedi: ad kod düzeyinde gömülüdür
(`pyproject.toml` `name`, paket dizini `hakhukuk/`, üç konsol komutu) — onu değiştirmek depo
adı değil **paket** yeniden adlandırmasıdır.

### Doğrulandı, varsayılmadı

- `gh api repos/Rfetha/Hukuk-SLM` → `Rfetha/HakHukuk` (**eski ad yönlendiriyor**)
- HF pinli revizyon `902ace67…` **yeni ad altında çözülüyor** ⇒ `indir.py`'nin kimlik kapısı
  (`GGUF_REVIZYON` · `GGUF_SHA256` · `GGUF_BAYT`) **etkilenmedi**
- `repo_info(...).private` = `False` her iki depoda
- Kart ve dataset kartı yüklendikten sonra **token'sız** bir süreçle geri okundu

### ⛔ Bu karar GRILL KARARI 6'YI TERSİNE ÇEVİRİR

`docs/superpowers/plans/2026-09-12-v1-son-is.md` kararı 6 ve
[ADR-0083](0083-kusur-sicili-adrye-tasindi.md) §(A) kusur 10 satırı şunu yazıyordu:

> *"HF deposunun **ADI aynı kalır** (`Rfetha/HakHukuk-4B-v0.3-Q4_K_M`)"*

**O karar artık yürürlükte değildir.** Gerekçesi — *"değişmemiş bir dosyaya yeni sürüm adı
vermek bu hattın kendi kuralına aykırı"* — **hâlâ geçerlidir ve korunmuştur**: değişen şey
**depo** adıdır, **dosya** adı değil. Grill kararı ikisini ayırmamıştı; bu ADR ayırır.

## Karar 4 — Aşırı-red ekseni TEK BİRİME çivilendi

Eksen depoda **dört ayrı belgede dört ayrı sayıyla** yazılıydı. Kök sebep: **koşullu ölçütün
koşulu adında yoktu.** *"Temiz çekinme"* adı üç Gemini kolunda yalnız **altın-gelmiş**
kalemleri sayıyordu (8+9+11 = **28**, kalibrasyon dosyasının kendi cümlesi), bizim ve Sonnet-5
kolunda **tüm** çekinmeleri (5 ve 8).

Bağlayıcı birim: **altın geldi ve model yine de sustu.** Altın hiç getirilmemişken susmak
**doğru davranıştır** ve bu eksende sayılmaz.

| kol | aşırı çekinme (gözle, tek birim) |
| :--- | ---: |
| HakHukuk | 4/80 |
| `gemini-3.1-flash-lite` | 5/80 |
| `gemini-3.5-flash-lite` | 5/80 |
| `gemini-3.5-flash` | 7/80 |
| **`claude-sonnet-5`** | **3/80** |

⇒ **Yayımlanan bir sayı değişti ve aleyhimize:** kart *"aşırı çekinmede iki model eşittir"*
diyordu; **Sonnet-5 öndedir**. Düzeltmeyi mümkün kılan şerh
`GOZLE_KALIBRASYON_sonnet_5.json`'un gerekçe metninde **zaten yazılıydı** (*"id 79'da altın
zaten getirilmemişti ⇒ o kalemde çekinme DOĞRU davranış"*) ama **satıra hiç yansımamıştı**.
Ayrıntı [#71](../record/research_log/2026-09-13-asiri-red-birimi-sonnet5-onde.md) · tuzak
**2.21**.

## Karar 5 — README'ler KISALTILDI ve karta işaret eder hâle geldi

Kart tek kaynak olunca `README.md` (380 satır) ve `README.tr.md` (372 satır) onun büyük bir
kısmını **tekrarlıyordu** — ve tekrarladığı için de bayatlamıştı: `G8`'in kapandığını görmeyen
dört satır, `281 passed` test sayısı, `#62`'de duran araştırma kaydı, `0073`'te duran ADR
sayacı, yeniden puanlanmadan önceki rakip tablosu, ve kapanmış bir yol haritası.

İkisi de **~125 satıra** indirildi (insan kararı): ne olduğu · nasıl koşulacağı · manşet
sayılar · ne vaat etmediği · sürümleme · repo haritası. Rakip kıyası, ölçüm rejimi, eksen
tanımları ve sınırlar **karta işaret edilerek** çıkarıldı. README'nin işi kartı tekrarlamak
değil, ona götürmektir.

## Ne KURULMAZ

- Bu ADR *"kart artık bayatlamaz"* **DEMEZ**. Üretim betiği yalnız **HF ile depo arasındaki**
  ayrışmayı kapatır; `MODEL_CARD.md`'nin kendisi ölçümün gerisinde kalabilir. Bu turda üç bayat
  iddia bulundu ve üçü de **elle** yakalandı — otomatik bir kapı **yoktur**.
- Bu ADR *"ürün adı tartışıldı ve `HakHukuk` seçildi"* **DEMEZ**. Ad zaten yürürlükteydi;
  ölçülen şey **değiştirme maliyetiydi** ve değiştirilmedi.
