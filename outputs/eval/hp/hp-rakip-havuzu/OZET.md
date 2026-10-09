# G4 — Rakip havuzu genişledi: `anthropic/claude-sonnet-5` ÖZNE olarak girdi

**Tarih:** 2026-09-09 · **veri:** `data/eval/dev/core_hard.jsonl` v2 (ADR-0067) ·
indeks `mevzuat_bge_m3_s2` · `RRF_K=10` (ADR-0068) · k=10 · seed 3407 · 900 klip ·
bütçe **1536** (`--reasoning-budget 1024` + `--max-new-tokens 512`, ADR-0070) · **önsözsüz** ·
hakem `openai/gpt-4o-mini` (aile dışlaması: Anthropic özne ↔ OpenAI hakem) · n=80

⛔ **Bu koşu `v1.0` kapısını KURMAZ** — ADR-0072 m.2: eşik oynamaz, çıpa `3.5 Flash` kalır.
Sonnet-5 yalnız **raporlanır**.

## Sınavın eşit olduğunun KANITI (varsayılmadı, ölçüldü)

| eksen | BİZ `tgta_v1` | 3.5 Flash | **Sonnet-5** |
| :--- | ---: | ---: | ---: |
| `recall@1 / @3 / @5 / @10` | 0,5250 / 0,7625 / 0,8250 / **0,9500** | aynı | 0,5250 / 0,7625 / 0,8250 / **0,9500** |
| `finish_reason='length'` | **4/80** | **4/80** | **4/80** |
| ort. `completion_tokens` | 782,5 | 699,4 | 706,6 |
| istem · bütçe | önsözsüz · 1536 | aynı | aynı |

`altin_dusuruldu` = **0** ⇒ mülga süzgeci altını düşürmedi. ⇒ Hüküm kurulabilir (ADR-0057).

## 🚨 ZORUNLU ÖN ADIM: red dedektörünün YENİ AİLEDE kalibrasyonu

Sekiz "çekinme" kaleminin sekizi de gözle okundu →
[`GOZLE_KALIBRASYON_sonnet_5.json`](GOZLE_KALIBRASYON_sonnet_5.json).

| kol | alet | temiz çekinme | çekinceli cevap | **açık yanlış pozitif** |
| :--- | ---: | ---: | ---: | ---: |
| **BİZ** | 4 | 4 | 0 | **0** |
| 3.1 Flash-Lite | 8 | 5 | 0 | **3** |
| 3.5 Flash-Lite | 9 | 5 | 2 | **2** |
| 3.5 Flash | 11 | 7 | 3 | **1** |
| **Sonnet-5** | **8** | **4** | **1** | **3** — id 17 · 35 · 41 |

Kusur **ADR-0061'in birebir aynı sınıfı**, yalnız aile değişti: dedektör **son esaslı ibareyi**
tarıyor, bu ailenin şablonu cevabı bir **şerh cümlesiyle** kapatıyor.
En açık örnek **id 35** — *"nafaka davaları **basit yargılama usulüne** tabidir"* diye açıp
*"kanunlarda açıkça başka bir usul **belirtilmediği** sürece…"* diye kapanıyor; **olumlu hükmün
içindeki olumsuzlama** red sayılmış. ⛔ `REJECT_RE`'ye DOKUNULMADI (F0.4'teki gibi) — düzeltme
GÖZ okumalarında yapılır.

## Üç okuma altında kütle — BAĞLAYICI TABLO

| kol | ALET (ham) | GÖZ-orta | GÖZ-katı |
| :--- | ---: | ---: | ---: |
| **BİZ (`tgta_v1`)** | **0,8011** | **0,8011** | **0,8011** |
| 3.1 Flash-Lite | 0,6746 | 0,7058 | 0,7058 |
| 3.5 Flash-Lite | 0,7174 | 0,7403 | 0,7622 |
| 3.5 Flash | 0,6925 | 0,7050 | 0,7425 |
| **Sonnet-5** | 0,7911 | **0,8223** | **0,8348** |

| okuma | BİZ ↔ Sonnet-5 | hüküm |
| :--- | ---: | :--- |
| ALET | 0,8011 ↔ 0,7911 | +1,00 p **bize** |
| GÖZ-orta | 0,8011 ↔ 0,8223 | **−2,12 p** |
| **GÖZ-katı** | 0,8011 ↔ 0,8348 | **−3,37 p** |

⛔ **HÜKÜM: Sonnet-5 ÖNDE.** Öne geçtiğimiz tek okuma (ALET), önde olmadığımızı bildiğimiz
okumadır: aletin Sonnet lehine **3 yanlış pozitifi** var, bizde **0**. Aynı düzeltmeyi F0.4'te
Gemini ailesinin **lehine** yapmıştık; burada kendi **aleyhimize** uygulandı.
⚠️ Hakemin yeniden-koşu gürültü tabanı ~0,3 A1 puanı; −2,12 ve −3,37 puanlık farklar **üstünde**.

## Eksen eksen

| eksen | BİZ | Sonnet-5 | önde |
| :--- | ---: | ---: | :--- |
| kütle (GÖZ-katı) | 0,8011 | 0,8348 | Sonnet |
| `A1_cevaplanan` | 0,8545 | 0,8790 | Sonnet |
| `A1_altin_getirilen_alt_kume` | 0,8902 | 0,9031 | Sonnet |
| `coverage` (ALET) | 0,9375 | 0,9000 | BİZ |
| `cit_precision_micro` | 0,9231 | 0,9752 | Sonnet |
| **`wrong_ref_rate_micro`** | **0,0769** | **0,0083** | **Sonnet — 9,3×** |
| `cit_recall_macro` | 0,9000 | 0,9875 | Sonnet |
| **uydurma madde no** (deterministik) | **0/114** | **2/163** | **BİZ** |
| üretilen iddia | 273 | 526 | — (Sonnet 1,9×) |

🚨 **İki alet farklı yöne işaret ediyor ve ikisi de doğru — ayrımı yazmadan okunmamalı.**
Deterministik atıf doğrulayıcı *"var olmayan madde"* sayar: bizde **0**, Sonnet'te **2**.
Hakemin `wrong_ref_rate`'i *"iddiayı yanlış kaynağa bağladı"* sayar: bizde **0,0769**,
Sonnet'te **0,0083**. ⇒ **Madde uydurmuyoruz; var olan YANLIŞ maddeye atıf yapıyoruz.**
Bu, hiç çalışılmamış **B1 (isabetsizlik)** borcunun ta kendisidir.

## 🚨 B1 hakkındaki cümlemiz DEĞİŞTİ — iki yerde damgalanır

Bugüne kadar: *"B1'de rakiplerden GERİDE DEĞİLİZ (8/80 ↔ 8·8·7·8)"*. O kıyas **yalnız Gemini
ailesineydi**. Frontier sınıfı bir özneye karşı ilk ölçüm bunu **çürütüyor**: `wrong_ref`
0,0769 ↔ 0,0083. ⇒ *"geride değiliz"* cümlesi **havuza bağlıdır** ve yeni havuzda **geçmiyor**.
B1 borç olarak **açık kalır** ve `v2`'nin gerekçesi güçlendi.

## Bedel

| | |
| :--- | ---: |
| tahmin (duman koşusu ×16) | $0,82 |
| **gerçekleşen (bakiye farkı)** | **$1,1932** |
| hakem (`judge_cost_usd`, liste fiyatı) | $0,0588 |
| bakiye | $3,3968 → **$2,2036** |

🚨 **$1 kapısı AŞILDI (+%45).** Sebep: 5 kalemlik duman koşusundan ×16 doğrusal ekstrapolasyon,
cevap uzunluğu soruya göre değişen bir özne için kapı kurmaya yetmiyor (gerçekleşen 706,6
completion token/cevap × $10,00/M çıktı). Bir sonraki yeni özne için duman koşusu
**tabakalanmış** seçilir ya da kapıya **%50 emniyet payı** konur. (Plan, Görev 4 Adım 2b.)

## Ne KURULMAZ

- `v1.0` eşiği bu koşudan **kurulmaz** (ADR-0072 m.2).
- Bu **kaynak verilmiş** bir kıyastır; "frontier'a karşı çıplak model" değildir.
- Hakem **tek aile** (`gpt-4o-mini`); κ ölçüldü ve aracın 0,6 eşiğinin **altında** (ADR-0074).
- Boyut farkı (2,59 GiB Q4 yerel ↔ frontier) **raporlanır**, farkı açıklamak için **kullanılmaz**.
