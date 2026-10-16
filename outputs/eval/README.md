# `outputs/eval/` — ölçüm çıktıları, **koşu klasörü** düzeninde

> **Kural (2026-07-29):** her ölçüm turu **kendi klasörüne** yazar ve klasörün içinde bir
> **`KUNYE.json`** bulunur. Düz `outputs/eval/` köküne dosya yazılmaz.
> **Düzen (ADR-0087):** koşu klasörleri, kökte düz durmak yerine **ölçüm dönemine göre gruplanır**
> (`<grup>/<koşu>/`); klasör adları değişmedi, yalnız bir üst klasör eklendi.
>
> Gerekçe `docs/record/yurutme-tuzaklari.md`'nin tek kuralı: *"bir sayı üretildiğinde 'bu sayı
> neyin sayısı' sorusunun cevabı **künyeden** okunabilmeli. Okunamıyorsa sayı yoktur."* Düz
> dizinde iki protokolün dosyaları yalnız `_th` ekiyle ayrılıyordu; bir ekin düşmesi sessizce
> yanlış protokolün sayısını verirdi.

## Koşular

| klasör | protokol | özneler | n | durum |
| :--- | :--- | :--- | --: | :--- |
| [`sprint1-thinking-off/`](sprint1/sprint1-thinking-off/KUNYE.json) | `--thinking off` | base · `τ_g` v1 · Gemini 3.1 FL | 470/özne | 🔴 **çıpa değil** (ADR-0043) — kayıt olarak durur |
| [`cp09-butceli-1024-512/`](cp/cp09-butceli-1024-512/KUNYE.json) | thinking **on**, bütçe 1024+512, zorunlu kapatma | aynı üç özne | 470/özne | 🟢 **yürürlükteki çıpa** |
| [`cp09-ab-ayrimi/`](cp/cp09-ab-ayrimi/KUNYE.json) | thinking **off** + kaynak-yeterliliği önsözü | base | 70 + 80 | ⚗️ **ABLASYON** — ana tabloya girmez |
| [`cp1-hakem-meta-iddia/`](cp/cp1-hakem-meta-iddia/KUNYE.json) | **üretim yok** — CP0.9 cevapları, YENİ hakem istemi (ADR-0041) | base · `τ_g` v1 · Gemini 3.1 FL | 80/özne (M1) | 🟢 **yürürlükteki M1 groundedness** — CP0.9'un `gnd_m1_*` dosyaları artık **ham/kontrol** |
| [`cp2-rejected-hasat/`](cp/cp2-rejected-hasat/KUNYE.json) | hasat pilotu, bütçeli düşünce | base (çıplak) | 120 + 120 | 🔴 **PİLOT** — üretim hasadı başlamadı; kabul ölçütü ADR-0046/0048 ile değişti |
| [`cp2-on-eleme/`](cp/cp2-on-eleme/KUNYE.json) | **üretim yok** — 2×2 hakem tasarımı (mini/gpt-4o × cevap gizli/görünür) | pilotun 36 etiketli adayı | 36 | 🟡 **teşhis** — ön-eleme net zararlı bulundu, koşulmadı → ADR-0048 |
| [`cp2-s-boru-hatti-smoke/`](cp/cp2-s-boru-hatti-smoke/KUNYE.json) | **MEKANİK smoke** — `τ_a` 50 adım → norm-dengeli TIES → GGUF → 3 cevap | `τ_g` + SENTETİK kol | 3 | 🟡 **SAYI ÜRETMEZ** — ADR-0049 m.4; hiçbir değeri çıpa olarak kullanılmaz |
| [`cp2-r-kor-payda/`](cp/cp2-r-kor-payda/KUNYE.json) | **üretim yok** — cevaba KÖR `valid_trap` önbelleği + 9 koşunun aritmetikle yeniden puanlanması | base · `τ_g` v1 · Gemini 3.1 FL | 230 kalem | 🟢 **YÜRÜRLÜKTEKİ ÇEKİNME PAYDASI** — `cp09`'un `abst_*` özetleri artık **ham/kontrol**. ARA KAPI eşikleri burada türetildi (`ara_kapi_esikleri.json`) |
| `_artefakt/` | — | ölçüm dışı artefaktlar | — | `tau_norm_tg` · `vram_stack` · `token_budget` · eski smoke |

## Düzen: grup → koşu

| grup | ne |
| :--- | :--- |
| `sprint1/` | Sprint 1 — ilk üç özne, `--thinking off` (çıpa değil, kayıt) |
| `cp/` | CP hattı — CP0.9 bütçeli düşünce, hakem, hasat (`cp2*`), merge (`cp3*`) |
| `sprint2-olcum/` | Sprint 2 ölçümleri — `s2*`/`s3*` etiket + harness, `olcum-*`, `s17`, `karar3` |
| `faz0/` | Faz 0 ölçüm zinciri — `f01…f11`, `a1-*` |
| `gorev/` | Görev turları — `g1…g24` |
| `hp/` | `hp` hattı — hakem paneli, rakip havuzu |
| `f0/` | Checkpoint 1 · F0 (2026-10) — `rq2-dogrulama` (RQ2 anahtarlarının yeniden puanlaması, #76) · `f014-f016-dis-bilgiler` (DeepSeek ve kart fiyatlarının ham anlık görüntüsü, #81-#82) · `f016-pilot` (ölçüm kartı pilotu, Modal A10; m1'in 1. tekrarı A10 referansı, #83) · `f06-hakem-gecisi` (DeepSeek V4.1 Flash ↔ `gpt-4o-mini`, aynı gün aynı cevaplar, F0.6) · `f016-vllm-pilot` (vLLM pilotu: GGUF çevirisi, üçlü karşılaştırma, kapılar G1-G5, hasat kapısı, #86; `A10/q4-acilmis_u345`, `puanlama/u2`, `puanlama/u345`: üretim gürültüsü, #87). `faz0/` ile karışmasın: o Eylül 2026'nın Faz 0'ı |
| `_artefakt/` | ölçüm dışı artefaktlar (düz kaldı) |

Bir koşunun grubu adının önekinden bellidir (`g22-…` → `gorev/`, `cp3d-…` → `cp/`, `hp-…` → `hp/`).
Eski düz yol → yeni yol: `outputs/eval/<koşu>` → `outputs/eval/<grup>/<koşu>`; tam eşleme [ADR-0087](../../docs/adr/kararlar-0064-0085.md#adr-0087)'de.

## Dosya adı şeması (klasör içinde)

```
{mod}_{özne}_detail.jsonl        üretim: soru · referans · context_shown · cevap · künye alanları
gnd_{mod}_{özne}.jsonl           groundedness hakemi, satır satır
gnd_{mod}_{özne}_summary.json    aynısının özeti
abst_{mod}_{özne}.jsonl          abstention hakemi, satır satır  (JSON dizisi, .jsonl adına rağmen)
abst_{mod}_{özne}_summary.json   Rej(LLM) · Rej(regex) · geçerli tuzak paydası · fabrikasyon
reg_{mod}_{özne}*                register proxy
a1_{mod}_{özne}.txt              A1 = cevaplanan-only + coverage (ADR-0011)
```

`{özne}`: `base` · `tg` / `tg_v1_th` · `gem` — protokol eki (`_th`) **tarihsel**; protokolün
asıl kaynağı artık **klasördür**.

## ⚠️ Sprint 1 klasöründe iki A1 sürümü var

`a1_m5_*.txt` **eski** (mod-bağımsız) red kuralıyla, `a1_m5_*_adr0044.txt` **düzeltilmiş**
(mod-duyarlı) kuralla hesaplandı — bkz. [ADR-0044](../../docs/adr/0044-mod-duyarli-feragat-kurali.md).
**Okunacak olan `_adr0044` sürümüdür**; eskisi audit için duruyor ve sayı olarak kullanılmaz.
M1/M4 dosyalarında iki sürüm birebir aynıdır (kural yalnız kör modu etkiliyor).

## Eski yollar → yeni yollar

Kapalı belgeler (`sprint1.md`, `research_log` #39/#41, ADR-0031, eski planlar) düz yolları
gösteriyor ve **bilerek değiştirilmedi** — audit trail'e dokunulmaz. Eşleme:

| eski | yeni |
| :--- | :--- |
| `outputs/eval/{m,gnd_,abst_,reg_,a1_}*_{base,tg,gem}*` | `outputs/eval/sprint1/sprint1-thinking-off/…` |
| `outputs/eval/*_{base_th,tg_v1_th,gem_th}*` | `outputs/eval/cp/cp09-butceli-1024-512/…` |
| `outputs/eval/{vram_stack,token_budget_*,tau_norm_*}.json` | `outputs/eval/_artefakt/…` |

## Yeni koşu açarken

1. Klasörü **koşunun kimliğiyle** adlandır (checkpoint + protokolün ayırt edici parametresi):
   `cp3-tau-abstention/`, `cp09-butceli-1024-512/` gibi. Tarih değil — tarih künyede.
2. `OUT_DIR=outputs/eval/<grup>/<klasör>` ver (grup yukarıdaki tablodan) (18 betik `--out-dir`/`OUT_DIR` alıyor).
3. Koşu biter bitmez **`KUNYE.json`** yaz: protokol · değişmezler (seed · klip · n · bütçe) ·
   özneler ve taşıyıcıları · hakem + gateway · geçerlilik kapısı sonucu · güç durumu · şerhler.
4. `.log` dosyaları klasörde durur ama **git'e girmez** (`*.log` kuralı `!outputs/**`
   negasyonundan sonra geldiği için yok sayılır — sıra önemli, bkz. `.gitignore`).
