# Atıf çözümü denetimi — tuzak 1.13'ün **TERS YÖNÜ** ölçüldü

**Tarih:** 2026-09-11 · **Koşu:** `outputs/eval/g22-atif-cozum/` · **Maliyet:** $0 (hakem çağrılmadı,
GPU kullanılmadı, ağa çıkılmadı) · **Künye:** [`KUNYE.json`](KUNYE.json)

> **İnsan kararı (2026-09-11):** *"1.13 onarılmadan ÖNCE ters yön ölçülsün."*
> `scripts/erisim_korpus/atif_dogrula.py` **DEĞİŞTİRİLMEDİ**. Bu belge bir **ölçümdür**;
> manşet yeniden yazılmadı, hüküm insanındır.

## 1. Ölçülen soru

`Dogrulayici` atıftaki kanun adını **gevşek** (en uzun ≥2 sözcüklü sonek) eşleştirir. Bilinen
yön — *yanlış-pozitif* — şudur: doğru atıf yanlış kanuna çözülür, o kanunda madde yoktur,
`MADDE_YOK` = **uydurma** damgası yer. Çıpada bu yön **boştur** (114/114 `DOGRULANDI`).

**Burada ölçülen ters yöndür:** atıf yanlış kanuna çözülüyor **ama o kanunda aynı numaralı bir
madde bulunduğu için** `DOGRULANDI` damgası alıyor mu? Gerçekleşiyorsa yayımlanan
**"uydurulmuş madde numarası 0/114"** manşeti **iyimser** okunuyor demektir.

Ölçüm aleti: [`scripts/erisim_korpus/atif_cozum_denetle.py`](../../../scripts/erisim_korpus/atif_cozum_denetle.py).
Ad karşılaştırması denetlenen modülden **bağımsız** yazıldı (Türkçe `I→ı` / `İ→i` eşlemesi +
`casefold`); `str.upper()`/`lower()` Türkçe'de yanıltır ve **aletin kendisi yanlış sayı üretir**.

## 2. Çıpa koşusu (yayımlanan 0/114'ün kaynağı)

Kaynak: `outputs/eval/f02-biz-onsozsuz/h1_tgta_v1_f02_nb_detail.jsonl` (80 cevap, 7'si atıfsız).

| ölçü | sayı | kaynak |
| :--- | ---: | :--- |
| atıf | 114 | `atif_dogrula.py --details …` (yeniden koşuldu, birebir tuttu) |
| `DOGRULANDI` | 114 | aynı |
| ad **birebir** uyuşan (`TAM`) | 105 | `atif_cozum.jsonl` |
| ad **sonek** uyuşan (`SONEK`) | 9 | `atif_cozum.jsonl` |
| ad **uyuşmayan** (`UYUSMAZ`) | **0** | `atif_cozum.jsonl` |
| atıftaki ada **birebir uyan başka bir kanun varken oraya gitmeyen** | **0** | `kosu.log` |
| adı birden çok kanuna uyan (çoklu aday) | 15 | `kosu.log` |

### 2.1 Gözle okuma — `TAM` olmayan 9 atfın hepsi (kapı)

Dördü ayrı kalıp; tekrarlar ×N ile verildi. Hüküm **gözle**, cevabın ham metnine bakılarak
verildi (`kosu.log` + `atif_cozum.jsonl`).

| # | atıftaki ad (ayrıştırıcının gördüğü) | modelin **yazdığı** ad | çözülen | hüküm | **gözle karar** |
| :-- | :--- | :--- | :--- | :--- | :--- |
| ×5 | «İflas Kanunu» | *İcra ve İflas Kanunu* | `2004` İCRA VE İFLAS KANUNU | `DOGRULANDI` | **DOĞRU** |
| ×2 | «Sanat Eserleri Kanunu» | *Fikir ve Sanat Eserleri Kanunu* | `5846` FİKİR VE SANAT ESERLERİ KANUNU | `DOGRULANDI` | **DOĞRU** |
| ×1 | «Mülkiyet Kanunu» | *Sinaî Mülkiyet Kanunu* | `6769` SINAİ MÜLKİYET KANUNU | `DOGRULANDI` | **DOĞRU** |
| ×1 | «Yayın Hizmetleri Hakkında Kanun» | *Radyo ve Televizyonların Kuruluş ve Yayın Hizmetleri Hakkında Kanun* | `6112` (aynı kanun) | `DOGRULANDI` | **DOĞRU** |

**BELİRSİZ: 0 · YANLIŞ: 0.** Dokuzunun da ortak mekanizması aynı ve ayrıştırıcıdadır, çözümde
değil: ad içindeki **küçük harfli `ve`** ya da **`î` harfi** başlık-sözcüğü zincirini kırıyor,
kanun adının yalnız **kuyruğu** yakalanıyor. Sonek çözümü bu kesilmeyi **doğru** onarıyor.
(*Not: id=29 ve id=69'da model altın kanundan **başka** bir kanuna atıf yapıyor — bu
**B1 yanlış atıf** eksenidir, doğrulayıcının çözüm hatası değildir; bu ölçümün konusu değil.*)

### 2.2 Çoklu aday (15 atıf)

Onbeşinin **tamamı** `İŞ KANUNU` / `İş Kanunu` — ad 3 kanuna birden uyuyor (`4857` yürürlükte,
`1475` mülga dahil). Onbeşi de **`4857`**'ye çözülmüş, ad uyuşması `TAM`, hüküm `DOGRULANDI`.
Bu, `_hukum`'un yürürlükteki taşıyıcıyı seçme kuralının **çalıştığı** hâlidir (ADR kaydı:
donmuş TEST id=32). **Gözle karar: DOĞRU.**

### 2.3 Manşet cümlesi

> **Yanlış kanuna çözülüp yine de `DOGRULANDI` almış atıf: 0 / 114.**

## 3. fp16 koşusu (152 atıf) — karşılaştırma

Kaynak: `outputs/eval/g22-kv-fp16/h1_tgta_v1_g22_fp16_detail.jsonl`.

| ölçü | sayı |
| :--- | ---: |
| atıf | 152 (`DOGRULANDI` 149 · `MADDE_YOK` 1 · `AYRISTIRILAMADI` 2) |
| `TAM` · `SONEK` · `UYUSMAZ` · `COZUMSUZ` | 125 · 24 · **1** · 2 |
| **yanlış çözülüp `DOGRULANDI` almış** | **0 / 152** |

Tek `UYUSMAZ`, tuzak 1.13'ün belgelenmiş vakasının ta kendisidir ve **ters yönde değil,
bilinen yöndedir**:

| id | atıf | çözülen | hüküm | birebir adı taşıyan kanun |
| ---: | :--- | :--- | :--- | :--- |
| 25 | «Gelir Vergisi Kanunu Madde 73» | `1319` EMLAK VERGİSİ KANUNU | `MADDE_YOK` | `193` (doğru olan) |

Yani bu atıf **uydurma sayıldı**, oysa madde korpusta var (`193/Madde 73`). Yanlış-pozitif;
manşeti **kötümser** yönde kirletir, iyimser yönde değil.

## 4. Parantezli adlı 16 kanun — sentetik prob ($0)

Korpusta adında parantez taşıyan **16** kanun var. Her biri için, o kanunun ilk NORMAL maddesiyle
iki istem kuruldu: **(a)** ad **birebir** (parantezli), **(b)** ad **parantezsiz** — modelin
fiilen yazdığı biçim. Ham çıktı: [`parantezli_prob.json`](parantezli_prob.json).

| sonuç | (a) birebir ad | (b) parantezsiz ad |
| :--- | ---: | ---: |
| **doğru** kanuna çözdü (`DOGRULANDI`) | **8 / 16** | **0 / 16** |
| **YANLIŞ** kanuna çözdü ve yine `DOGRULANDI` aldı | 0 / 16 | **7 / 16** |
| `AYRISTIRILAMADI` (ad hiç ayrıştırılamadı) | 7 / 16 | 9 / 16 |
| `KANUN_YOK` | 1 / 16 | 0 / 16 |

Parantezsiz adla **yanlış kanuna çözülüp `DOGRULANDI` alan 7 kanun:**

| gerçek | ad (kısaltılmış) | çözülen |
| ---: | :--- | :--- |
| `193` | GELİR VERGİSİ KANUNU (G.V.K.) | `1319` EMLAK VERGİSİ KANUNU |
| `3806` | ONÜÇ İLÇE VE İKİ İL KURULMASI HAKKINDA KANUN (…) | `3335` |
| `3824` | BAZI VERGİ KANUNLARINDA DEĞİŞİKLİK YAPILMASI HAKKINDA KANUN (…) | `4481` |
| `4447` | İŞSİZLİK SİGORTASI KANUNU (…) | `5510` |
| `4568` | BAZI FONLARIN TASFİYESİNE İLİŞKİN KANUN (…) | `1606` |
| `4646` | DOĞAL GAZ PİYASASI KANUNU (…) | `5015` |
| `4737` | ENDÜSTRİ BÖLGELERİ KANUNU (…) | `2565` |

**Bu tablo mekanizmanın GERÇEK olduğunu kanıtlar:** ters yön kuramsal değil, sentetik olarak
üretilebiliyor — 16 kanunun **7'sinde** yanlış kanun + `DOGRULANDI` rozeti. Ayrıca (a) sütunu
ikinci bir kusuru gösteriyor: **parantezli ad ayrıştırıcının kalıbına oturmuyor** (7/16
`AYRISTIRILAMADI`), yani doğru yazılmış bir atıf bile atıf sayılmayabiliyor.

## 5. Bu ölçümün KAPSAMADIĞI şey (sayı uydurulmadı)

- **Maddenin İÇERİĞİ sorgulanmadı.** Ad doğru, numara korpusta var — maddenin soruyla ilgili
  olup olmadığı bu eksende (B1) ölçülür, burada değil.
- **Eş adlı kanunlarda "yanlış ama aynı adlı" seçim** yalnız dolaylı ölçüldü (çoklu aday = 15,
  hepsi `İŞ KANUNU`, hepsi yürürlükteki `4857`). Adı birebir aynı iki kanun arasında yapılan
  seçimin **anlamca** doğruluğu ölçülmedi — ölçmek için altın kanun gerekir, 15'inin gözle
  okunması bu turda yapıldı ve hepsi yürürlükteki kanuna gitti.
- **Örneklem iki koşudur** (114 + 152 atıf, aynı 80 DEV sorusu). Donmuş TEST'e bakılmadı.

## 6. HÜKÜM (ölçülen)

> **Yayımlanan `0/114` manşeti bu yönden KİRLENMEMİŞTİR:** çıpadaki 114 atfın **0'ı** yanlış
> kanuna çözülüp `DOGRULANDI` almıştır (ad uyuşmayan atıf **0**, sonek uyuşan 9 atfın
> **9'u da gözle DOĞRU**, atıftaki ada birebir uyan başka kanun varken oraya gitmeyen **0**).
>
> **Ama kusur gerçektir ve manşeti tesadüfen ıskalamıştır:** aynı alet, parantezli adlı 16
> kanunun **7'sinde** yanlış kanuna çözüp `DOGRULANDI` basıyor (§4) ve fp16 koşusunda bir
> atfı yanlış kanuna çözüp `MADDE_YOK` = uydurma saymıştır (§3). Çıpanın temiz çıkmasının
> sebebi aletin doğruluğu değil, **çıpadaki 114 atfın hiçbirinin parantezli adlı bir kanuna
> denk gelmemesidir.**

Onarım ayrı turdur (tuzak 1.13'ün önerdiği yön: birebir ad ya da kanun numarası; gevşek
eşleşme `AYRISTIRILAMADI` dönmeli, sessizce kanun **seçmemeli**).
