# Yayımlanan sayıyı yeniden üretme

> **Tek komut:** `bash scripts/yeniden_uret.sh`
> Bu script **tek hakem okumasını** (`gpt-4o-mini`, GÖZ-katı, bağlayıcı) üretir: **kütle
> %80,1** — `outputs/eval/f02-biz-onsozsuz/KUNYE.json` (2026-09-06). ⚠️ **Bugünkü manşet
> ARALIKTIR** (`%69,4-80,1`, `claude-sonnet-5` ↔ `gpt-4o-mini` — ADR-0084); bu sayı aralığın
> yalnız üst ucudur, tek başına manşet değildir.

## Neden bu belge var

2026-09-07'ye kadar bu sayıyı **modeli indiren hiç kimse yeniden üretemiyordu.** Üç sebep vardı,
üçü de ölçüldü:

| engel | durum |
| :--- | :--- |
| İstem `gen_eval_grounded.py`'nin içindeydi, beş kopyası vardı ve biri **sürüklenmişti** | ✅ çözüldü — `hakhukuk/istem.py`, tek kaynak + `sha256` damgası |
| Komut zinciri hiçbir yerde **tek parça** yazılı değildi | ✅ çözüldü — `scripts/yeniden_uret.sh` |
| İndeks **git'te yok** (`.gitignore:166`, 80 MB ikili) | ⛔ **AÇIK** — plan Görev 8, korpus kararı beklendiği için bekletiliyor |

## Ön koşullar

```
models/gguf/tgta_v1-q4_k_m.gguf        ← ⛔ HF'den indirilir (Görev 8'de otomatikleşecek)
data/index/mevzuat_bge_m3_s2/          ← ⛔ git'te YOK, bugün elle üretilir (CPU ~2 sa 45 dk)
data/corpus/mevzuat_maddeler.jsonl     ← ✅ git'te var (37 MB)
.env                                    ← OPENROUTER_API_KEY
llama-server                            ← ⛔ PATH'te DEĞİL, ölçüldü 2026-09-10:
                                          llama.cpp/build-cuda/bin/llama-server
source ~/code/global_venv/bin/activate
```

İndeksi bugün elle üretmek:
```bash
python scripts/erisim_korpus/retriever.py kur \
  --korpus data/corpus/mevzuat_maddeler.jsonl \
  --indeks data/index/mevzuat_bge_m3_s2
```

## Rejim — değiştirilemez sabitler

⚠️ **Uyuşmazlık hata VERMEZ, yalnız kıyası geçersiz kılar.** Script bunları sabitler:

| | değer | kaynak |
| :--- | :--- | :--- |
| seed | 3407 | ADR-0043 |
| düşünce + cevap bütçesi | 1024 + 512 = **1536** | ADR-0070 (rakiple **birebir aynı formül**) |
| kaynak klipi | 900 karakter | eval-mirror, ADR-0011 |
| harness k · `RRF_K` | 10 · 10 | ADR-0068 |
| indeks | `mevzuat_bge_m3_s2` | S2 — yürürlük alanı taşır |
| veri | `data/eval/dev/core_hard.jsonl` (v2) | ADR-0067 |
| önsöz | **YOK** (`ekstra : <yok>`) | ADR-0063 |
| hakem | `openai/gpt-4o-mini` | **ADR-0074 — bağlayıcı** |

## Geçerlilik kapıları — sayı üretilmeden ÖNCE

Script iki kapıyı otomatik koşar ve düşerse **çıkar**:

1. **kesiklik ≤ %5** (ADR-0040) — üstündeyse koşu geçersiz
2. **`recall@10` = 0,9500** — oynadıysa harness değişmiş, kıyas geçersiz

Sonda üçüncü bir kontrol var: üretilen kütle çıpadan (0,8011) **0,30 puandan** fazla saparsa
uyarı basılır. 0,30 hakemin yeniden-koşum gürültü tabanıdır ve **yalnız A1 için** ölçülmüştür.

## ⚠️ Bilinen sapma kaynakları — ölçüldü

- **Üretim tam deterministik değil.** Aynı girdi (bayt-bayt aynı istem ve bağlam) iki koşuda
  farklı çıktı verebiliyor; gözlenen fark noktalama düzeyindeydi. Bu yüzden "birebir aynı" değil
  **gürültü tabanı içinde** aranır.
- **Retriever yürürlük süzgeci 2026-09-07'de eklendi** (mülga maddeler elenir). `recall@10`
  değişmedi (0,9500 ↔ 0,9500) ama getirilen kaynak listesi bazı kalemlerde oynadı ⇒ o tarihten
  **önceki** çıktılarla birebir metin karşılaştırması yapılamaz.
- **Modal taşıyıcısı kullanılmaz.** Paralel slot (`-np`) çıktıyı değiştiriyor (S12/KARAR-6:
  Jaccard 0,5278, birebir metin 3/19). Manşet sayı **yerel** llama-server'da doğdu.

## Bedel

| adım | bedel |
| :--- | ---: |
| üretim (80 kalem, yerel GPU, şarjda) | **$0** · ~25 dk |
| puanlama (`gpt-4o-mini`) | **~$0,04** raporlanan · ~$0,07 gerçek fatura |

⚠️ Gerçek fatura raporlanandan **~1,6 kat** yüksektir (OpenRouter marjı — ölçüldü 2026-09-07).
