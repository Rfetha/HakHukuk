# Görev 22 · Adım 1 — KV önbelleği `q8_0` ↔ `fp16` kıyası (HAKEMSİZ, $0)

**Tarih:** 2026-09-11 · **özne:** `tgta_v1` = HakHukuk-4B-v0.1 (`models/gguf/tgta_v1-q4_k_m.gguf`)
**Üretici:** `scripts/olcum_uretim/kv_kiyas.py` (genişletildi) → ham çıktı
[`KARSILASTIRMA.json`](KARSILASTIRMA.json)

⛔ **Bu belgede KÜTLE (faithful-answer mass) YOKTUR.** Kütle hakem ister; hakem para ister;
para kapısı Adım 2'nin **insan kararıdır**. Aşağıdaki her sayı deterministik ve hakemsizdir.

## 0 · Kıyaslanan iki koşu

| | çıpa | yeni |
| :--- | :--- | :--- |
| etiket | `h1_tgta_v1_f02_nb` | `h1_tgta_v1_g22_fp16` |
| detay dosyası | `outputs/eval/f02-biz-onsozsuz/h1_tgta_v1_f02_nb_detail.jsonl` | `outputs/eval/g22-kv-fp16/h1_tgta_v1_g22_fp16_detail.jsonl` |
| `sha256` | `e0536489…a08a0aad` | `8e5b89aa…83583c455` |
| KV önbelleği | **q8_0 / q8_0** | **f16 / f16** (llama.cpp varsayılanı) |
| tarih | 2026-09-06 | 2026-09-11 14:55 → 15:37 |

**Rejim eşitliği — iki sunucu günlüğünden okundu, birebir aynı:**
`n_slots = 4` · `n_ctx_slot = 8192` · `kv_unified = 'true'` · `ctx 8192` · `-ngl 99` · `-fa on` ·
`seed 3407` · `thinking on` · düşünce 1024 + cevap 512 (toplam 1536) · `max_chunk_chars 900` ·
`n = 80` · `data/eval/dev/core_hard.jsonl` · indeks `mevzuat_bge_m3_s2` · `k = 10` · **önsözsüz** ·
taşıyıcı yerel `llama-server` · güç **ŞARJDA**.

### ⚠️ Bulgu 0.1 — `kosu.log` künyesi YALAN SÖYLÜYOR (tuzak 1.12)

`outputs/eval/g22-kv-fp16/kosu.log` künyesinde `KV q8_0/q8_0` yazıyor. **Bu satır yanlıştır.**
Sebep: `scripts/olcum_uretim/cp0_thinking_gen.sh:89` bu alanı **sabit dize** olarak basıyor —
aynı satırdaki `$CTX` · `$NGL` · `$PORT` · `$EXTRA_ARGS` değişkenken KV değil. Betik dış bir
sunucuya bağlandığında (*"var olan sunucu kullanılıyor"*) sunucunun KV ayarını **hiç okumuyor**.
Gerçek rejim koşu sırasında `/proc/<pid>/cmdline` okunarak doğrulandı: süreç
`-ngl 99 -fa on --no-context-shift -c 8192 --host 127.0.0.1 --port 8080` idi, `--cache-type-*`
**yoktu** ⇒ f16. Tuzak `docs/record/yurutme-tuzaklari.md` **1.12** olarak kayıtlı.

**Sunucu kapandıktan sonra da duran ikinci kanıt** (`cp0_server_*.log`, `alloc` satırları):

| | çıpa q8_0 | yeni f16 | oran |
| :--- | ---: | ---: | ---: |
| atılan istem önbelleği girdisi, medyan (MiB) | 257,2 | 306,8 | **×1,19** |
| aynı, ortalama (MiB) | 255,3 | 304,1 | ×1,19 |

Yeni koşunun önbellek girdileri sistematik olarak **daha büyük**. Bu, f16 KV ile tutarlıdır;
tek başına kanıt değil, `/proc` okumasının **bağımsız doğrulamasıdır** (kaynak: iki sunucu günlüğü).

### ⚠️ Bulgu 0.2 — Rejim farkı TEK bayrak çifti DEĞİL: 2 kalemde erişim de değişti

Kontrol değişkeni (retriever KV'den bağımsızdır, getirilenler birebir olmalı) **2/80 kalemde saptı:**
`id 7` ve `id 63`. Sebep bulundu ve KV **değil**: iki koşu arasında `63b691e` (2026-09-07, A8b)
retriever'a **yürürlük süzgeci** ekledi.

| id | çıpada getirilen, yenide DÜŞEN kaynak | korpus hükmü |
| :-- | :--- | :--- |
| 7 | `İŞ KANUNU \| Madde 111` | kanun **1475**, `mulga = True` |
| 63 | `İŞ KANUNU \| Madde 87` | kanun **4857**, `mulga = True` |

Bunlar CLAUDE.md'nin *"800 getirilen kaynağın 2'si mülgaydı, sızıntı 2 → 0"* cümlesindeki **tam
o iki kalemdir**. Altın madde iki koşuda da ilk 10'da kaldı (`id 63` sıra 1 ↔ 1; `id 7` sıra 8 → 7),
`recall@10` iki koşuda da **0,9500**. ⇒ **78/80 kalemde sınav birebir aynı; 2 kalem KARIŞIKTIR**
ve bu ikisindeki cevap farkı KV'ye atfedilemez. Soru metni ve altın referans 80/80 birebir aynı.

## 1 · Bayt kimliği (`sha256(cevap)`)

| | değer | kaynak |
| :--- | ---: | :--- |
| **değişen cevap** | **65 / 80** | `KARSILASTIRMA.json → bayt_kimligi` |
| değişmeyen (bayt-bayt aynı) | **15 / 80** | aynı |

Değişmeyen 15 kalemin çoğu çok kısa cevaplardır (58 karakterlik tek cümlelik çekinme gibi).
⇒ KV kuantizasyonu **belirleyicilik açısından nötr değil**: aynı istem, aynı seed, farklı metin.

## 2 · Uzunluk

### 2.1 Toplulaştırılmış

| ölçü | çıpa q8_0 | yeni f16 | fark |
| :--- | ---: | ---: | ---: |
| karakter medyan | 715,0 | 706,5 | **−8,5 (−%1,2)** |
| karakter ortalama | 774,3 | 780,6 | +6,3 (+%0,8) |
| karakter min / maks | 58 / 3.352 | 58 / 3.824 | maks +472 |
| `completion_tokens` medyan | 731,0 | 718,5 | **−12,5 (−%1,7)** |
| `completion_tokens` ortalama | 782,5 | 779,1 | −3,4 (−%0,4) |
| `completion_tokens` toplam | 62.603 | 62.332 | −271 (−%0,4) |

Kaynak: iki `*_detail.jsonl`; `kosu.log` da yeni koşu için ort 779,1 / toplam 62.332 diyor.

### 2.2 Kalem başına farkın dağılımı

| eksen | uzayan | kısalan | aynı | \|fark\| medyan |
| :--- | ---: | ---: | ---: | ---: |
| karakter | 35 | 30 | 15 | **47,5** |
| `completion_tokens` | 33 | 41 | 6 | **18,5** |

**En büyük iki yönlü sapma** (yeni − çıpa):

| yön | karakter | token |
| :--- | :--- | :--- |
| en çok uzayan | `id 25` **+2.983** · `id 41` **+2.360** | `id 25` +898 · `id 41` +800 |
| en çok kısalan | `id 75` **−2.220** · `id 69` −1.627 | `id 51` −759 · `id 75` −654 |

⇒ Ortanca kalem **neredeyse hiç oynamıyor** (48 karakter, 19 token); toplam farkı **dört kalem**
taşıyor. Gözle okundu: `id 25` ve `id 41` yeni koşuda **yinelemeli döngüye** girip bütçeyi
tüketiyor (`41`'in sonu: *"…17) … 18) İcra ve İflas Kanunu Madde 30, borç…"*); `id 75` ise
çıpada aynı döngüdeyken yeni koşuda düzgün kapanıyor. **Döngü sınıfı iki rejimde de var;
değişen şey HANGİ kalemin döngüye girdiğidir.**

## 3 · Kesik / boş / zorla kapatma

| ölçü | çıpa q8_0 | yeni f16 |
| :--- | :--- | :--- |
| `finish_reason == "length"` | **4 / 80** (id 29 · 32 · 51 · 75) | **3 / 80** (id 25 · 29 · 41) |
| tamamen boş `cevap` | **0 / 80** | **0 / 80** |
| `forced_close == true` | **3 / 80** | **3 / 80** |

`forced_close` = düşünce kanalı 1024 token bütçesine dayandığı için `</think>` **zorla** kapatılan
kalem sayısı (ADR-0043). İki koşuda da **3** — yani düşünce kanalının bütçeye dayanma sıklığı KV
değişiminden **etkilenmedi**; değişen yalnız *cevap* kanalının bütçeye çarpma sıklığıdır (4 → 3).

ADR-0040 geçerlilik kapısı (kesiklik > %5 → koşu GEÇERSİZ): çıpa %5,0 (tam eşikte), yeni **%3,8**
⇒ **ikisi de geçerli**, yeni koşunun payı daha geniş. Kaynak: `kosu.log` GEÇERLİLİK KAPISI bloğu.

Kesiklik yön değiştiren kalemler: çıpada kesik → yenide değil `32 · 51 · 75`; çıpada değil →
yenide kesik `25 · 41`. Yani **net −1, ama 5 kalem taraf değiştirdi**.

## 4 · Çekinme / suskunluk

⚠️ **Bu hattın dedektörü üç kez yanıldı** (ADR-0061 · `terazi.py` başlığı). Kullanılan dedektör
tek ve açıkça yazılıyor:

> `scripts/puanlama/score_abstention.py` · fonksiyon **`exact_reject(cevap, mode="data")`**

`mode="data"` seçimi keyfi değil: resmî ölçüm hattı çekinmeyi bu modda sayıyor
(`scripts/puanlama/harness_tablo.py:122`) ve çıpanın **5/80**'i oradan doğdu. Başka bir mod
sessizce başka bir sayı üretir. **Aynı dedektör, aynı mod, iki koşuya da uygulandı.**

| | çıpa q8_0 | yeni f16 |
| :--- | :--- | :--- |
| `exact_reject` = RED | **5 / 80** | **5 / 80** |
| id'ler | 15 · **37** · 45 · 66 · 79 | 15 · 45 · **51** · 66 · 79 |

**Şerh (zorunlu):** bu dedektörün **bilinen yanlış-pozitif sınıfı vardır** — önsözsüz rejimde
RAFT şablonunun *"Diğer kaynaklar … içermemektedir"* eleme gerekçesi doğru-atıflı bir cevabı
çekinme saydırabiliyor (ADR-0061). Çıpa için bu risk **kapatıldı**: 80 kalemin tamamı gözle
okundu ve alet ↔ göz farkı **sıfır** çıktı (`f02-biz-onsozsuz/GOZLE_OKUMA_80.md` §1). Yeni koşu
**gözle okunmadı**; yalnız **taraf değiştiren iki kalem** okundu:

| id | çıpa | yeni | göz hükmü (deterministik, hakemsiz) |
| :-- | :--- | :--- | :--- |
| 37 | 58 karakter: *"Verilen kaynaklarda bu konuyu düzenleyen madde bulunmuyor."* — **gerçek aşırı-red** (altın TMK 398, sıra **1**) | 812 karakterlik tam, alıntılı cevap | **gerçek cevap**; ancak altın TMK **398** iken cevap kendini TMK **400**'e bağlıyor ⇒ B1 (isabetsizlik) ekseninde bir kalem |
| 51 | `finish_reason=length`, yarım kalmış cevap | 210 karakter: *"Verilen kaynaklarda bu konuyu düzenleyen madde bulunmuyor…"* | **gerçek çekinme — ve DOĞRU davranış**: altın madde iki koşuda da getirilmedi (`altin_sirasi = None`) |

⇒ Mutlak sayı iki koşuda da 5, ama **içerik farklı**: çıpada 5 reddin 4'ü altın bağlamdayken
(aşırı-red), yenide **3'ü** altın bağlamda. `harness_tablo.json` erişim-davranış çaprazı bunu
bağımsız olarak doğruluyor: `altin_geldi_cekindi` **4 → 3**, `altin_gelmedi_cekindi` **1 → 2**.
Sapma iki kolda da aynı dedektörden geçtiği için **fark anlamlıdır**, mutlak sayı şüpheli kalır.

## 5 · Uydurulmuş madde numarası (deterministik atıf doğrulama)

Araç: `scripts/erisim_korpus/atif_dogrula.py` (`Dogrulayici`), korpus
`data/corpus/mevzuat_maddeler.jsonl`. `MADDE_YOK` = kanun var, **madde korpusta yok** = uydurma.

| hüküm | çıpa q8_0 | yeni f16 |
| :--- | ---: | ---: |
| `DOGRULANDI` | 114 | 149 |
| **`MADDE_YOK` (uydurulmuş)** | **0** | **1** |
| `KANUN_YOK` | 0 | 0 |
| `MULGA` | 0 | 0 |
| `AYRISTIRILAMADI` | 0 | **2** (id 23 · 36) |
| **toplam atıf** | **114** | **152** |
| atıfsız cevap | 7 | 5 |
| **manşet** | **0 / 114** | **1 / 152** |

> 🚨 **DÜZELTME 2026-09-11 (bu rapor yazıldıktan SONRA, gözle doğrulandı).** Yukarıdaki
> **`MADDE_YOK` = 1** satırı **ALETİN YANLIŞ POZİTİFİDİR**; uydurma **YOKTUR**.
> `id 25`'in atfı *"Gelir Vergisi Kanunu Madde 73"* idi ve o madde korpusta **VARDIR**
> (`kanun_no 193` · `Madde 73` · `kanun_adi` = *"GELİR VERGİSİ KANUNU (G.V.K.)"*).
> Doğrulayıcı kanun adını **1319 = EMLAK VERGİSİ KANUNU** diye çözdü, sonra 73'ü orada
> aramadı bulamadı ve `MADDE_YOK` dedi. Doğrudan koşularak kanıtlandı:
> `Dogrulayici().cevabi_dogrula(...)` → `Hukum(atif=Atif(kanun='Gelir Vergisi Kanunu',
> madde='73'), hukum='MADDE_YOK', kanun_no='1319')`.
> ⇒ **Uydurulmuş madde ekseni: `0/114` ↔ `0/152`. Eksen AYAKTA, aleyhte kıpırdamadı.**
>
> Bu bir **alet kusurudur ve manşet `0/114`'ü üreten aletin içindedir** — açık kusur **18**
> olarak kayda geçti. Çıpa koşusunda `MADDE_YOK` **hiç yok** (114/114 `DOGRULANDI`), yani
> yayımlanan sayı bu yanlış pozitifle **kirlenmemiştir**; ama aynı gevşek ad eşleştirmesi
> ters yönde de çalışabilir (**yanlış `DOGRULANDI`**) ve o yön **ölçülmemiştir**. Çıpanın
> 114 atfının **2'si** (`id 69`) adı birebir tutmayan bir kanuna çözüldü
> (*"Mülkiyet Kanunu"* → `6769 SINAİ MÜLKİYET KANUNU`, *"Yayın Hizmetleri Hakkında Kanun"*
> → `6112`); ikisi de makul görünüyor ama **eşleştirme birebir değil**.

`id 25` ayrıca yeni koşuda **kesik** olan ve yinelemeli döngüye giren kalemdir.

**Atıf sayısındaki +38'in tamamı dört kalemde:** `id 41` (+16) · `id 75` (+11) · `id 25` (+9) ·
`id 1` (+9); 68 kalemde atıf sayısı **hiç değişmedi**, 3 kalemde azaldı.

**İkinci, bağımsız sayı** — `harness_tablo.json`, katı atıf kapısı (hakemsiz):

| | çıpa | yeni |
| :--- | :--- | :--- |
| katı kapıdan **geçen** | 80 / 80 | **77 / 80** |
| katı kapıda **reddedilen** | **0** | **3** |
| kapı sonrası coverage | 0,9375 | 0,9000 |

## 6 · Ürün durum sınıfı (`hakhukuk.terazi.siniflandir`)

Çağrı: `siniflandir(cevap, kaynaklar, finish_reason)`. `kaynaklar`, `harness.getirilen`
listesinden **yeniden kurulmuştur** — o alan `kanun_no` taşımıyor, korpustan eşlendi (ad+madde
birden çok kanuna düşüyorsa **yürürlükteki** tercih edildi, çünkü canlı retriever 2026-09-07'den
beri mülgayı eliyor). Ürün yolunda `kanun_no` doğrudan taşınır; buradaki yeniden kurulum kıyası
etkilemez çünkü **iki koşuya da aynı biçimde** uygulandı.

| durum | çıpa q8_0 | yeni f16 |
| :--- | ---: | ---: |
| `CEVAP` | 70 | **71** |
| `CEKINCELI` | 1 | 1 |
| `SUSKUNLUK` | 5 | 5 |
| `KESIK` | 4 | **3** |

**Sınıf değiştiren kalem: 6 / 80.**

| geçiş | id'ler | yön |
| :--- | :--- | :--- |
| `KESIK → CEVAP` | 32 · 75 | iyileşme |
| `SUSKUNLUK → CEVAP` | 37 | aşırı-red düştü (ama atfı altına gitmiyor, §4) |
| `CEVAP → KESIK` | 25 · 41 | **kötüleşme** |
| `KESIK → SUSKUNLUK` | 51 | iyileşme (altın gelmemişti, susmak doğru) |

Kusur 2'nin tek-soruluk gözlemi (`SUSKUNLUK → CEKINCELI`) **80 kalemin hiçbirinde tekrarlanmadı**;
gözlenen geçişler `KESIK` ekseninde toplanıyor. `CEKINCELI` sayısı **iki koşuda da 1** ve aynı kalem.

## 7 · Yan gözlem: hız (kıyas KONTROLLÜ DEĞİL, şerhli)

`cp0_server_*.log` `eval time` satırlarından üretim hızı: medyan **67,57 → 70,14 t/s** (+%3,8);
ortalama 68,08 → 65,36 t/s (dağılım çarpık, 83'er ölçüm). Duvar saati süresi çıpa ~17,6 dk ↔ yeni
~43,8 dk, **ama bu sayı kıyas için kullanılamaz**: iki koşu farklı günlerde, farklı makine yükü
altında koştu ve süre eksenini kimse kontrol etmedi. Kayda geçiriliyor, **hüküm kurulmuyor**.

## 8 · Ölçülemeyenler (uydurulmadı)

| istenen | durum | sebep |
| :--- | :--- | :--- |
| kütle (faithful-answer mass) | **ÖLÇÜLMEDİ** | hakem ister; Adım 2'nin insan bedel kapısı |
| `reasoning_tokens` kıyası | **ÖLÇÜLEMEDİ** | alan iki koşuda da `null` (llama-server doldurmuyor); vekili `forced_close`, o da raporlandı |
| yeni koşunun 80 kaleminin gözle okunması | **YAPILMADI** | Adım 1'in kapsamı değil; yalnız taraf değiştiren 2 çekinme kalemi okundu |
| KV bayrağının koşu anındaki `/proc` kanıtı | **KAYIT DIŞI** | sunucu kapandı; yerine iki dolaylı kanıt var (önbellek girdisi ×1,19 · koşu sırasındaki `/proc` okuması, tuzak 1.12'ye yazıldı) |

## HÜKÜM

**Sapma, toplulaştırılmış eksenlerde KÜÇÜK; kalem düzeyinde BÜYÜK — ve iki sert sayı geriledi.**
Dayandığım sayılar: dağılım hiç oynamadı (karakter medyanı **715,0 → 706,5**, yani **−%1,2**;
token medyanı 731,0 → 718,5, **−%1,7**; toplam token **−%0,4**; kalem başına mutlak fark medyanı
yalnız **47,5 karakter / 18,5 token**; çekinme **5 ↔ 5**; boş cevap **0 ↔ 0**; zorla kapatma
**3 ↔ 3**; kesik **4 → 3**; durum sınıfı dağılımı hiçbir sınıfta **1 kalemden fazla** oynamadı).
Buna karşılık cevapların **65/80'i bayt olarak değişti**, **6/80 kalem ürün durum sınıfı
değiştirdi** ve bir ölçü **aleyhte** kıpırdadı: katı atıf kapısının reddi **0 → 3**.
~~uydurulmuş madde numarası 0/114 → 1/152~~ — **DÜZELTİLDİ 2026-09-11:** o tek kalem aletin
yanlış pozitifiydi (bkz. §5 düzeltme kutusu); gerçek eksen **0/114 ↔ 0/152**, **taşınıyor**.
Buna karşılık fp16, çıpada **hiç görülmeyen** bir bozulma sınıfı üretti: model istem
**yer tutucusunu harfiyen bastı** — *"(KANUN ADI, Madde 13)"* — `0/80 ↔ 2/80` (id 23 · 36,
gözle doğrulandı). Yani *"KV kuantizasyonu manşet dağılımı bozmuyor"* denebilir;
*"cevaplar aynı kalıyor"* **denemez**.
⛔ Kütlenin ne kadar oynayacağına dair bir cümle **kurulmuyor** — ölçülmedi.

## Adım 2 için bedel girdisi (ÖLÇÜM, tahmin değil)

Çıpanın hakem bedeli **ölçülmüş** ve `outputs/eval/f02-biz-onsozsuz/hakem.log` ÖZET satırında duruyor:

```
"judge_model": "openai/gpt-4o-mini", "runs": 1, "n": 80, "judge_cost_usd": 0.0417
```

| kalem | değer | kaynak |
| :--- | ---: | :--- |
| çıpanın **gerçek** hakem bedeli (n=80, runs=1) | **$0,0417** | `f02-biz-onsozsuz/hakem.log` |
| hakem çağrısı sayısı (çıpa) | **156** = 76 kalem × 2 + 4 kalem × 1 | `groundedness.py`: kalem başına iddia-çıkarma + doğrulama; `claims=0` olanda tek çağrı |
| fp16 koşusu için beklenen çağrı | **~155** (5 çekinme × 1 + 75 × 2) | §4 |
| hakeme giden girdinin değişen kısmı | yalnız **cevap metni** (`--kaynak referans`, soru+altın birebir aynı) | `hakem.log` başlığı |
| cevap kütlesi farkı | 61.944 → 62.448 karakter (**+%0,8**) | §2.1 |
| iddia/atıf yükü farkı | atıf 114 → 152 (+%33) ⇒ çıktı token'ı (pahalı taraf) artar | §5 |
| **düz tahmin** | $0,0417 × 1,01 ≈ **$0,042** | — |
| **%50 emniyet paylı üst sınır (tuzak 1.11)** | **$0,063** | — |

**Bakiye $2,20'ye göre: üst sınır bakiyenin %2,9'u.** `--runs 3` istenirse üst sınır **$0,19**.
Bu bir **ÖLÇÜMdür** (aynı hakem, aynı betik, aynı n, aynı sınav girdisi), doğrusal bir duman-koşusu
ekstrapolasyonu değil — tuzak 1.11'in ısırdığı sınıf burada geçerli değil; emniyet payı yine de eklendi.
⛔ Harcama kararı **verilmedi**; bu tablo yalnız kapının girdisidir.

---

## SONUÇ SATIRI — kütle ÖLÇÜLDÜ (eklendi 2026-09-11, Adım 2)

§8'in *"kütle — **ÖLÇÜLMEDİ**"* satırı **kapandı**. İnsan bedel kapısı geçildi, hakem koşuldu,
**gerçek harcama $0,045067** (sert kapı $0,15 — kapının %30'u). Tam ölçüm, gürültü şerhi ve
16 kalemlik birim eşitliği listesi: [`KUTLE.md`](KUTLE.md) · künye: [`KUTLE_KUNYE.json`](KUTLE_KUNYE.json).

| eksen | ÇIPA `q8_0` | fp16 | fark | gürültü tabanı | taban üstünde mi |
| :--- | ---: | ---: | ---: | ---: | :--- |
| **kütle** | **0,8011** | **0,7932** | **−0,79 puan** | ≈0,28 puan | **evet, 2,8×** |
| `A1_cevaplanan` | 0,8545 | 0,8461 | −0,84 puan | 0,30 puan | evet, 2,8× |
| `coverage` | 0,9375 | 0,9375 | 0,00 | — | — |
| `cit_precision_micro` | 0,9231 | 0,8252 | **−9,79 puan** | 0,30 puan | **evet, ~26×** |
| `wrong_ref_rate_micro` | 0,0769 | 0,1553 | **2 katı (kötüleşme)** | — | evet |

Kaynak dosyalar: `harness_tablo_gnd.json` (yeni) ↔ `../f02-biz-onsozsuz/harness_tablo.json` (çıpa) ·
`gnd_h1_tgta_v1_g22_fp16_summary.json` ↔ `../f02-biz-onsozsuz/gnd_h1_tgta_v1_f02_nb_summary.json`.

**Şerhli hüküm.** Fark gürültü tabanının üstünde, ama **yalnız 2,8×** ve tek yönlü bir cümleye
yetmez: devralınan ~0,3 puanlık taban *aynı cevaplara* hakemi yeniden koşmanın gürültüsüdür,
oysa burada **cevaplar da değişti** (§2: 65/80 kalem bayt olarak farklı) ve bu koşu çiftine ait
aynı-cevap tabanı **ölçülmedi**. Kalem düzeyinde **18/80** kalemin `faithfulness`'ı **iki yönlü**
oynadı (id 30 `0,00 → 0,875` · id 9 `0,50 → 1,00` yukarı; id 1 `0,833 → 0,00` · id 39 `1,00 → 0,00`
aşağı) — toplam −0,79 puan bu ±0,5-1,0'lık salınımların **artakalanıdır**. Temiz alt kümede
(n=78, id 7·63 hariç — §5'teki kontrol değişkeni düşmesi) sonuç aynı: **0,7960 → 0,7879, −0,81 puan**.

Kurulabilen cümle: *"fp16 KV'ye geçmek kütleyi YÜKSELTMEDİ; en iyi tahmin ≈1 puan aşağıda."*
Kurulamayan cümle: *"fp16 modeli 0,8 puan bozar."*

**Tabanın açıkça üstündeki tek eksen atıf isabetidir** ve §5'in hakemsiz bulgusuyla aynı yöne
bakar: fp16 daha çok atıf yaptı (114 → 152) ve bunların daha büyük bir oranı yanlış maddeye
gitti (`wrong_ref_rate` 0,0769 → 0,1553). Bu, planın bir sonraki birinci-derece ekseni **B1** ile
aynı eksendir; burada **hüküm kurulmuyor**, kayda geçiriliyor.

⛔ **Yayımlanan 0,8011 DEĞİŞMEZ.** Ürünün taşıyıcı rejimi `q8_0/q8_0`'dır; manşet o koşunun
(`outputs/eval/f02-biz-onsozsuz/`) sayısıdır. Bu ölçüm bir **taşıyıcı ayarının** kütle üzerindeki
etkisini söyler, modelin ya da ürünün manşetini **yeniden yazmaz**.
