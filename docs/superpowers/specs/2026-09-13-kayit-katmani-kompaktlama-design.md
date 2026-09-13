# Kayıt katmanı kompaktlama — tasarım

**Tarih:** 2026-09-13 · **Tür:** spec (tasarım) · **Durum:** onaylandı (insan, 2026-09-13)
**Kapsam:** `docs/adr/**` + `docs/record/**`

## Sorun — ölçüldü, tahmin edilmedi

| | değer |
| :--- | ---: |
| dosya | **103** (`adr/` 60 · `record/` 5 · `record/*/` 38) |
| bayt | **1,40 MB** |
| kaba token | **~466 bin** |

Şişkinlik iki ayrı sınıfta ve ikisi farklı iş:

**(1) Dizin/kayıt tabloları — az satır, devasa bayt.** En sık okunan dosyalar bunlar:

| dosya | satır | bayt | B/satır |
| :--- | ---: | ---: | ---: |
| `record/README.md` | 106 | 71 KB | **672** |
| `record/yurutme-tuzaklari.md` | 169 | 48 KB | **286** |
| `adr/README.md` | 135 | 37 KB | **273** |

`README.md`'nin `Kanca` sütunu her girdinin içeriğini tekrar taşıyor — index değil,
**ikinci kopya**.

**(2) Anlatı gövdeleri — çok satır, normal genişlik (60 B/satır).** `cp2c-modal-koprusu.md`
1654 satır/94 başlık · `hp-hat-a-hat-b-kapanan-gorevler.md` 1203 · `sprint2/defter.md` 1075.

Kod fence'i toplamın yalnız **%6'sı** (507/8473 satır) → kısaltma **düzyazıdan** çıkacak.

## Çarpışan kural — bilinçli sapma

ADR-0024'ün iki pazarlıksız kuralından biri: *"`research_log/` ve `adr/` yerinde kalır — makaleyi
haftalar sonra yeniden kurabilme garantisi kronolojik kayıt taşınırsa kırılır."* CLAUDE.md bunu
tekrarlıyor.

**Bu tur o kuraldan bilinçli olarak sapar (insan kararı, 2026-09-13)** — tıpkı 2026-07-24'te
26 ADR → 1 dosya ve 38 log girdisi → 1 dosya birleştirmesinde sapıldığı gibi. Kuralın özü
(**içerik silinmez, sayılar kaybolmaz**) damıtma kuralıyla korunur; silinenler git geçmişinde
`301a82f` ve öncesinde durur.

## Hedef yapı — 103 → 12 dosya

### `docs/adr/` (60 → 5)

| dosya | taşıdığı |
| :--- | :--- |
| `README.md` | dizin — 58 ADR tek satır (273 → ~90 B/satır) |
| `kararlar-0027-0044.md` | tasarım kilitleri · base seçimi · precision · merge/norm · Kapı 6 · düşünce modu |
| `kararlar-0045-0063.md` | ara kapı · CP2 hasat · hakem · harness · eşit sınav · faz 0 zinciri |
| `kararlar-0064-0085.md` | v1 kapısı · hakem paneli · ürün yolu · konteyner · kusur sicili · κ · tek kart |
| `gemma4-12b-dersler.md` | Bölüm A (dersler) + **B (26 ADR kaydı)**; Bölüm C silinir |

**Numara aralığı ile gruplama seçildi, tema ile gruplama ELENDİ.** Gerekçe: *"ADR-0057 hangi
dosyada"* sorusu aritmetikle cevaplanır; tema okumada iyi, aramada kötü. Her ADR
`<a id="adr-0057"></a>` çapasını taşır → repo genelindeki **2117** metin göndermesi yaşar.

> ⛔ **Bölüm B silinemez.** Emekli hattın `ADR-0001..0026` numaralarına repoda **319** gönderme var
> ve **10'u CLAUDE.md'de yürürlükte** anılıyor (`0003 · 0010 · 0011 · 0016 · 0017 · 0018 · 0019 ·
> 0023 · 0025 · 0026`). Bölüm B o göndermelerin tek çözüm yeri.

### `docs/record/` (43 → 7)

| dosya | taşıdığı |
| :--- | :--- |
| `README.md` | yön tabelası |
| `kollar.md` | ⛔ **dokunulmaz** — canlı artefakt sicili ("satırı olmayan artefakt isimsizdir") |
| `yurutme-tuzaklari.md` | damıtılır (48 → ~20 KB); her koşu öncesi okunan canlı liste |
| `gemma4-12b-kronoloji.md` | **korunur** — emekli hattın 38 girdisinin tüm sayıları |
| `kronoloji-39-52.md` · `kronoloji-53-62.md` · `kronoloji-63-71.md` | 33 log girdisi, `#39`-`#71` çapalarıyla |

## Damıtma kuralı — pazarlıksız beş madde

1. **Her sayı birebir korunur** — metrik · n · hakem · seed · kaynak dosya yolu (`outputs/eval/...`).
   CLAUDE.md: *"Numbers are sourced, not remembered."*
2. **Her `Ders` bloğu korunur.**
3. **Her negatif/çürütülmüş bulgu korunur** — bu hattın en değerli bulguları kendi planlarının
   çürütülmesidir.
4. **Her elenen alternatif + gerekçesi korunur** (ADR'lerde).
5. **Kesilen:** oturum-oturum anlatı · tekrar eden bağlam kutuları · komut dökümleri · aynı sayının
   üçüncü tekrarı · ölü işaretçiler.

**Hedef:** ~466 bin → ~190 bin token.

## Çöp listesi — onaylandı

| # | ne | boyut | gerekçe | karar |
| :-: | :--- | ---: | :--- | :-- |
| 1 | `record/2026-09-10-hp-hat-a-hat-b-kapanan-gorevler.md` | 67 KB | kendi başlık kutusu: *"bu bulguların sayıları `docs/record/` ve `docs/adr/` içinde zaten vardı"* | **SİL** |
| 2 | `record/sprint2/defter.md` | 69 KB | kapanmış sprint; icra dokümanı `_arsiv/sprint2.md` zaten silinmiş → yarım kayıt. Kaynak girdiler #42-#47 duruyor | **SİL** |
| 3 | `record/sprint1/` (3 dosya) | 38 KB | kapanmış sprint; sonuç tablosu zaten *"parite iddiası değil"* damgalı | **SİL** |
| 4 | `record/gemma4-12b-kronoloji.md` | 38 KB | emekli hat, adaptörler kalıcı kayıp | **KALSIN** — tek dosya kazandırır, 38 girdinin tüm sayılarını götürür; risk/kazanç kötü |
| 5 | `adr/gemma4-12b-dersler.md` Bölüm C | ~4 KB | ham log giriş noktaları | **SİL** |

## Bağ onarımı

| sınıf | adet | çözüm |
| :--- | ---: | :--- |
| `ADR-00NN` **metin** göndermesi | 2117 | çapa taşınır → kendiliğinden çözülür |
| `adr/NNNN-….md` **yol** göndermesi | ~235 | toplu `sed` → `kararlar-XXXX-YYYY.md#adr-NNNN` |
| `research_log/YYYY-MM-DD-….md` yol göndermesi | ~153 | toplu `sed` → `kronoloji-A-B.md#NN` |
| silinen 5 dosyaya gönderme | — | tek tek elden geçirilir |

⚠️ `tests/test_belgeler.py` **bu iki klasörü kapsam dışı bırakıyor** (satır 5) → testler kırılmaz,
**ama kırık bağı da kimse yakalamaz.** Onarım elle doğrulanır.

## Dokunulmayanlar

`outputs/eval/**` · `docs/superpowers/**` · `scripts/**` · `knowledge/**` içindeki tarihsel yol
göndermeleri **onarılır** (silinmez); `docs/record/kollar.md` hiç değişmez.
