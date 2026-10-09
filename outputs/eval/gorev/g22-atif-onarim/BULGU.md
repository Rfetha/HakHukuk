# Kusur 18 — atıf doğrulayıcı ONARILDI, çıpalar YENİDEN PUANLANDI

**Tarih:** 2026-09-11 · **Koşu:** `outputs/eval/g22-atif-onarim/` · **Maliyet:** $0
(hakem çağrılmadı, GPU kullanılmadı, ağa çıkılmadı) · **Künye:** [`KUNYE.json`](KUNYE.json)

> ⛔ **DONMUŞ TEST'E YENİ SORU SORULMADI, YENİ ÜRETİM YAPILMADI.** Model çağrılmadı,
> `llama-server` açılmadı. Diskte **zaten duran** cevaplara **düzeltilmiş alet** yeniden
> uygulandı — bu ADR-0050'nin kalıbıdır (*alet düzelir, eşik oynamaz*).
> İnsan kararı: 2026-09-11, iki parça da onaylı.

Kusurun ölçümü: [`../g22-atif-cozum/BULGU.md`](../g22-atif-cozum/BULGU.md) ·
tuzak metni: `docs/record/yurutme-tuzaklari.md` **1.13**.

---

## 1. Onarım — TDD

### 1.1 Önce KIRMIZI (kod yazılmadan)

`tests/test_atif_dogrula.py`'ye 8 test eklendi; onarımdan **önce** koşuldu:

```
FAILED tests/test_atif_dogrula.py::test_dogrula_parantezli_son_ekli_kanun_adini_dogru_cozer
FAILED tests/test_atif_dogrula.py::test_dogrula_gelir_vergisini_emlak_vergisine_COZMEZ
FAILED tests/test_atif_dogrula.py::test_dogrula_cift_gevsek_eslesmede_kanun_SECMEZ
FAILED tests/test_atif_dogrula.py::test_hukum_cozulen_kanunun_ADINI_tasir
4 failed, 25 passed in 1.31s
```

Kalan 4 test **ilk koşuda da yeşildi** — bunlar bilerek konmuş **regresyon çıpalarıdır**,
onarımın *eski doğruları bozmadığını* çivilerler:

| test | neyi çivilyor |
| :--- | :--- |
| `test_CIPA_114_atfin_tamami_DOGRULANDI_kalir` | yayımlanan **0/114** manşetinin kaynağı |
| `test_dogrula_kucuk_harfli_VE_ile_kesilen_adi_hala_cozer` | *"İcra **ve** İflas Kanunu"* → `2004` |
| `test_dogrula_sapkali_harfle_kesilen_adi_hala_cozer` | *"Sina**î** Mülkiyet Kanunu"* → `6769` |
| `test_dogrula_ayni_adli_iki_kanunda_YURURLUKTEKINI_secer` | `İş Kanunu` m.111 → **4857** (1475 değil) |

### 1.2 Çözüm kuralı (tek cümle)

> **Ad çözümünde EN ÇOK TEK gevşemeye izin verilir:** ya atıftaki adın **tamamı** bir kanun
> adının (sondaki parantezi atılmış hâli dahil) ≥2 sözcüklü **soneki** olur, ya da
> ayrıştırıcının ada kattığı **baştaki sözcükler** atılır ve kalan **BİREBİR** bir kanun adı
> olur — **ikisi birden asla**; ikisi birden gerekiyorsa hüküm **`AYRISTIRILAMADI`**'dır ve
> sessizce bir kanun **seçilmez**.

İki dayanak noktası:

1. **Sondaki parantez ada dahil sayılmaz.** Korpusta 16 kanunun adı parantez taşıyor, **7'sinde
   parantez sonda** (`GELİR VERGİSİ KANUNU (G.V.K.)`). Model parantezsiz yazar; artık birebir
   eşleşir. (`_ad_varyantlari`)
2. **Çift gevşeme kapatıldı.** Eski alet *"Gelir Vergisi Kanunu"*nun başındaki `GELİR`i atıp
   `VERGİSİ KANUNU` sonekine düşüyor ve **EMLAK VERGİSİ KANUNU**'na (1319) gidiyordu.
   (`_ad_adaylari` + `_gevsek_adaylar`)

Ayrıca `Hukum` artık **çözülen kanunun ADINI** taşıyor (`kanun_adi`) — tuzak 1.13'ün
*"yanlış çözüm gözle görülebilsin"* şartı.

### 1.3 Dokunulan dosyalar

| dosya | ne oldu |
| :--- | :--- |
| `scripts/erisim_korpus/atif_dogrula.py` | onarım: `KanunDizini` · `_ad_varyantlari` · `_dizin_kur` · `_ad_adaylari` · `_gevsek_adaylar` · `Hukum.kanun_adi` |
| `tests/test_atif_dogrula.py` | +8 test (4'ü kırmızı görüldü, 4'ü regresyon çıpası) |
| `scripts/erisim_korpus/atif_cozum_denetle.py` | tek satır: `d._adlar` → `d._dizin` (çağıran onarımı) |
| `scripts/veri_hazirlik/b8_tolerans_supurme.py` | iki satır: `dog._adlar` → `dog._dizin.sonek` (çağıran onarımı) |

`cevabi_dogrula` / `Hukum` kullanan diğer çağıranlar (`harness_tablo.py` · `kv_kiyas.py` ·
`red_kapisi.py`) **alan çıkarılmadığı** için dokunulmadan çalışıyor.
⚠️ `hakhukuk/araclar.py` **kendi bağımsız ad indeksini** taşıyor (`_adlar`, `_ad_normal`) —
bu onarım oraya **geçmedi**; ürün yüzeyi hâlâ eski çözümü kullanıyor (tuzak 2.18 kalıbı:
*aynı ölçümün ikinci bir aleti*). Görev tanımı `hakhukuk/**`'a dokunmayı yasakladığı için
**kayda geçirildi, onarılmadı.**

---

## 2. Çıpaların yeniden puanlanması (öncesi ↔ sonrası)

Alet: [`yeniden_puanla.py`](yeniden_puanla.py) — eski sürüm `git show HEAD:` ile geçici
dosyaya alınır, çalışma ağacına dokunulmaz (tuzak 5.9: denetim için `git stash` **kullanılmaz**).
Ham çıktı: [`yeniden_puanlama.json`](yeniden_puanlama.json).

| küme | n cevap | n atıf | hüküm | **ÖNCE** | **SONRA** |
| :--- | ---: | ---: | :--- | ---: | ---: |
| **DEV çıpa** `f02-biz-onsozsuz` | 80 | 114 | `DOGRULANDI` | **114** | **114** |
| | | | `MADDE_YOK` · `KANUN_YOK` · `MULGA` · `AYRISTIRILAMADI` | 0 · 0 · 0 · 0 | 0 · 0 · 0 · 0 |
| **donmuş TEST** `g16-kabul-testi` | 40 | 52 | `DOGRULANDI` | **52** | **52** |
| | | | `MADDE_YOK` · `KANUN_YOK` · `MULGA` · `AYRISTIRILAMADI` | 0 · 0 · 0 · 0 | 0 · 0 · 0 · 0 |
| **fp16 koşusu** `g22-kv-fp16` | 80 | 152 | `DOGRULANDI` | 149 | **150** |
| | | | `MADDE_YOK` | **1** | **0** |
| | | | `KANUN_YOK` · `MULGA` · `AYRISTIRILAMADI` | 0 · 0 · 2 | 0 · 0 · 2 |

**Hükmü değişen atıf: 1** (üç kümenin toplamında).

### 2.1 Hükmü değişen atfın GÖZLE okunması (kapı)

| alan | değer |
| :--- | :--- |
| küme · soru | fp16 · `id=25` — *"Kira bedelini nasıl belirliyoruz?"* |
| atıf | «Gelir Vergisi Kanunu Madde 73» (cevabın 8. maddesi: *"KAYNAK 8 — … kira bedellerinin vergi açısından değerlendirilmesi"*) |
| **eski** | `MADDE_YOK` · `1319` **EMLAK VERGİSİ KANUNU** |
| **yeni** | `DOGRULANDI` · `193` **GELİR VERGİSİ KANUNU (G.V.K.)** |
| korpus tanığı | `193/Madde 73` VAR, `mulga=False`, metni *"Kiraya verilen mal ve hakların kira bedelleri **emsal kira bedelinden** düşük olamaz…"* |

> **Gözle karar: YENİ HÜKÜM DOĞRU.** Model gerçekten GVK m.73'e (emsal kira bedeli) atıf yapmış,
> madde korpusta var ve yürürlükte. Eski hüküm **yanlış pozitifti**: doğru bir atfa *"uydurulmuş
> madde numarası"* damgası basıyordu. Onarım bir yanlışı düzeltirken **yeni bir yanlış üretmedi**
> (aynı kümede başka hiçbir hüküm oynamadı).

---

## 3. Onarım başka bir yeri bozdu mu? — geniş süpürme

Üç küme yetmez: aynı alet 94 koşu dosyasında kullanılıyor. Alet:
[`genis_supurme.py`](genis_supurme.py) · ham: [`genis_supurme.json`](genis_supurme.json).

| ölçü | değer |
| :--- | ---: |
| taranan dosya (`outputs/eval/**/*_detail.jsonl`) | 94 |
| taranan atıf | 11.634 |
| **hükmü/çözümü değişen** | **41** (%0,35) |

| geçiş | adet | ne demek |
| :--- | ---: | :--- |
| `DOGRULANDI` → `AYRISTIRILAMADI` | 22 | çoğu **yanlış kanuna basılmış DOGRULANDI**'nın kalkması (tehlikeli yön) |
| `MADDE_YOK` → `AYRISTIRILAMADI` | 16 | çözülemeyen addan **"uydurma" damgasının** kalkması |
| `MADDE_YOK` → `DOGRULANDI` | 2 | GVK m.73 vakası (fp16 + rakip 3.1 Flash-Lite) |
| `DOGRULANDI` → `MULGA` | 1 | *"Türk İş Kanunu m.33"*: `854` **DENİZ İŞ KANUNU** → `4857` **İŞ KANUNU** (m.33 mülga) |

### 3.1 22 kaybın gözle okunması — çoğu KAZANÇ, biri gerçek kayıp

Tekilleştirilmiş 15 kalıp okundu; eski çözümün gittiği kanunun **gerçek adı** yanına yazıldı:

| atıftaki ad | eski çözüm | gözle karar |
| :--- | :--- | :--- |
| *Ceza Muhakemeleri Kanunu* (×7) | `6100` **HUKUK MUHAKEMELERİ KANUNU** | eski **YANLIŞ** (kastedilen 5271) → onarım kazanç |
| *Tüketici Korunması Kanunu* (×2) | `6698` **KİŞİSEL VERİLERİN KORUNMASI KANUNU** | eski **YANLIŞ** → kazanç |
| *Tüketicinin Hakkı Kanunu* | `4982` **BİLGİ EDİNME HAKKI KANUNU** | eski **YANLIŞ** → kazanç |
| *Türk Medeni Usul Kanunu* | `213` **VERGİ USUL KANUNU** | eski **YANLIŞ** → kazanç |
| *Perakende Ticaret Kanunu* | `6102` **TÜRK TİCARET KANUNU** | eski **YANLIŞ** (gerçeği 6585) → kazanç |
| *DERNEKLER HAKKINDA KANUN* | `1135` **TÜRK VATANDAŞLARINA AİT OLUP YUGOSLAV…** | eski **YANLIŞ** (gerçeği 5253) → kazanç |
| *Ona Bağlı Müesseselerde… Kanun* | `168` **YABANCI MEMLEKETLERDE… ÖĞRETMENLERE SOSYAL YARDIM…** | eski **YANLIŞ** (gerçeği 6772; adın tamamı korpus adının soneki DEĞİL) → kazanç |
| *Türk İş Kanunu m.33* | `854` **DENİZ İŞ KANUNU** | eski **YANLIŞ** → yeni `4857` **MULGA** doğru |
| **HLI KUVVETLERİ PERSONEL KANUNU m.125** | `926` **TÜRK SİLÂHLI KUVVETLERİ PERSONEL KANUNU** | eski **DOĞRUYDU** → ⚠️ **GERÇEK KAYIP** |

**Tek gerçek kayıp** ve bedeli: korpus adı **`SİLÂHLI`** (şapkalı **â**) yazıyor, ayrıştırıcının
sözcük sınıfı `â` taşımıyor, bu yüzden ad *"HLI KUVVETLERİ PERSONEL KANUNU"* diye kesiliyor.
Eski gevşek çözüm bu **yazım farkını** tesadüfen kurtarıyordu; yeni kural kurtarmıyor
(`AYRISTIRILAMADI`). Ölçüldü: `Türk Silâhlı…` **`DOGRULANDI 926`**, `Türk Silahlı…`
**`AYRISTIRILAMADI`**. Bu, doğrulayıcının **yazım-hatası toleransı** borcudur (**B8**) ve bu turda
**kapatılmadı**. ⚠️ Bu atıf **yalnız `f02-biz-onsozsuz.GECERSIZ-kesik6.2-eski-butce`** koşusunda
geçiyor — **geçersiz ilan edilmiş** bir koşu; canlı çıpada ve donmuş TEST'te **yok**.

### 3.2 Rakip sayısı da oynadı — lehimize DEĞİL, aleyhimize

| özne | dosya | uydurulmuş madde **önce** | **sonra** |
| :--- | :--- | ---: | ---: |
| **3.1 Flash-Lite** | `f04-rakip-onsozsuz/h1_3_1_flash_lite_nb` | **1** / 154 | **0** / 154 |
| 3.5 Flash-Lite | `f04-rakip-onsozsuz/h1_3_5_flash_lite_nb` | 3 (+1 `KANUN_YOK`) | değişmedi |
| 3.5 Flash | `f04-rakip-onsozsuz/h1_3_5_flash_nb` | 4 | değişmedi |
| claude-sonnet-5 | `hp-rakip-havuzu/h1_sonnet_5_nb` | 2 | değişmedi |

3.1 Flash-Lite'ın **tek** uydurma atfı, bizimkiyle **aynı** GVK m.73 vakasıydı — yani aletin
kendi yanlış pozitifi. `MODEL_CARD` / `CLAUDE.md`'deki *"uydurulmuş madde 0/114 ↔ rakipler
**1** · 4 · 4"* cümlesindeki **1**, artık **0**'dır. **Bu düzeltme bizim aleyhimizedir ve
bu yüzden özellikle yazılmıştır.**

---

## 4. Kusur sınıfının kapandığının kanıtı — parantezli prob (sentetik, $0)

`g22-atif-cozum` §4'ün ölçümü **birebir** tekrarlandı (aynı alet, `atif_cozum_denetle.py`).
Ham: [`denetim-sonrasi/parantezli_prob.json`](denetim-sonrasi/parantezli_prob.json).

| sonuç (ad **parantezsiz** verildiğinde) | **ÖNCE** | **SONRA** |
| :--- | ---: | ---: |
| **doğru** kanuna çözdü (`DOGRULANDI`) | 0 / 16 | **7 / 16** |
| **YANLIŞ** kanuna çözüp yine `DOGRULANDI` aldı | **7 / 16** | **0 / 16** |
| `AYRISTIRILAMADI` | 9 / 16 | 9 / 16 |

Yedisinin de doğru kanuna döndüğü tek tek görüldü:
`193←1319` · `3806←3335` · `3824←4481` · `4447←5510` · `4568←1606` · `4646←5015` · `4737←2565`.

Kalan **9 `AYRISTIRILAMADI`**, adında parantez **ortada** olan kanunlardır
(`… GAZLARI (LPG) PİYASASI …`). Bunlar **ayrıştırıcının** (regex) kusurudur, çözümün değil;
bu turda **kapsam dışıdır** ve açık kalmıştır.

### 4.1 Çözüm denetimi — üç küme, onarım sonrası

Ham: [`denetim-sonrasi/atif_cozum.jsonl`](denetim-sonrasi/atif_cozum.jsonl).

| küme | n atıf | `TAM` | `SONEK` | `UYUSMAZ` | `COZUMSUZ` | **yanlış çözülüp `DOGRULANDI`** |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| DEV çıpa | 114 | 105 | 9 | **0** | 0 | **0** |
| donmuş TEST | 52 | 51 | 1 | **0** | 0 | **0** |
| fp16 | 152 | 126 | 24 | **0** | 2 | **0** |

fp16'daki tek `UYUSMAZ` (§3 of `g22-atif-cozum`: GVK m.73) **kayboldu** — onarılan şey oydu.

---

## 5. Bu koşunun KAPSAMADIĞI (sayı uydurulmadı)

- **Ayrıştırıcı (regex) onarılmadı.** Şapkalı harf (`â`), ortada parantez, kesilen adlar
  duruyor. Ölçülen bedeli §3.1 ve §4'te yazılı.
- **Yazım-hatası toleransı (B8) kapatılmadı.** Onarım toleransı **daraltır**; eski gevşeklik
  tesadüfen kurtardığı bir doğru atfı artık kurtarmıyor (1 vaka, geçersiz koşuda).
- **`hakhukuk/araclar.py`'nin ikinci ad indeksi onarılmadı** (görev tanımı gereği) — ürün
  yüzeyi hâlâ eski çözümü kullanıyor.
- **Kütle/A1/hakem sayıları yeniden hesaplanmadı** — bu onarım yalnız **atıf hükmünü**
  değiştirir; hiçbir hakem çağrısı yapılmadı.
- **Donmuş TEST'e yeni soru sorulmadı.**

---

## 6. HÜKÜM

> **Onarım manşeti OYNATMADI.** Yayımlanan **uydurulmuş madde numarası `0/114` (DEV çıpa)** ve
> **`0/52` (donmuş TEST)** sayılarının **ikisi de aynen durmaktadır**: düzeltilmiş aletle
> yeniden puanlandıklarında 114/114 ve 52/52 atıf yine `DOGRULANDI` aldı, **hiçbir atfın hükmü
> değişmedi** (`yeniden_puanlama.json`). Bu bir **bulgudur**, boş bir sonuç değil: `g22-atif-cozum`
> *"manşet temiz ama tesadüfen temiz — korunma aletten değil örneklemden geliyor"* demişti;
> şimdi korunma **aletten** geliyor ve manşet aynı yerde duruyor. Oynayan sayılar çıpaların
> dışındadır: fp16 koşusunda uydurma **1 → 0** (gözle okundu, yeni hüküm doğru) ve — aleyhimize —
> rakip **3.1 Flash-Lite**'ın uydurma sayısı **1 → 0**; yani *"0/114 ↔ rakipler 1 · 4 · 4"*
> cümlesindeki **1 artık 0'dır**. Onarımın bedeli tek bir vakada ölçüldü (şapkalı `â` yüzünden
> kesilen bir adın artık çözülememesi, **geçersiz** bir koşuda) ve kusur sınıfının kapandığı
> sentetik probla kanıtlandı: parantezli adlı 16 kanunun **7'sinde yanlış kanun + `DOGRULANDI`**
> → **0/16**.
