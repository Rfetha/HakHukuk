# data/ — veri haritası

Projenin **en pahalı ve en taşınabilir varlığı.** Base modelden, tokenizer'dan ve eğitim
yığınından bağımsız: hangi modele geçilirse geçilsin bu dosyalar aynen kullanılır.

**Yerleşim mantığı:** `corpus/` = yer-gerçeği · `eval/` = ölçüm (dondurulmuş) ·
`train/` = eğitim setleri (**yönteme göre adlandırılmış, tur numarasına göre değil**) ·
`_ham_ve_ara/` = ara/yeniden-üretilebilir dosyalar.

---

## `corpus/` — yer-gerçeği

| dosya | satır | ne |
| :--- | ---: | :--- |
| `mevzuat_maddeler.jsonl` | **40.496** | Yürürlükteki TC mevzuatının madde madde ham metni. Her grounded üretimin, her eval join'inin ve her distractor havuzunun kaynağı. |

```json
{"kanun_no": "7524", "kanun_adi": "VERGİ KANUNLARI İLE …", "madde_no": "MADDE 1", "text": "…"}
```

Join anahtarı her yerde `(kanun_no | madde_no)`. Kaynak: Mevzuat.gov.tr / bedesten API
(`docs/BEDESTEN_API.md`, `scripts/erisim_korpus/bedesten_probe.py` — ⚠️ Türk IP'si gerekir).

---

## `eval/` — ölçüm setleri 🔒 DONDURULMUŞ

> **Kural: bunlar değişmez.** Turlar arası kıyas ancak set sabit kalırsa anlamlıdır.
> Yeni bir eksen gerekirse **yeni dosya** ekle, mevcudu düzenleme.

### `eval/canon/` — CANON çekirdeği (ADR-0011)

| dosya | satır | hangi modlar |
| :--- | ---: | :--- |
| `core_hard.jsonl` | **40** | M1 (distractor grounding) · M4 (oracle tavan) · M2b (çok-kaynak ıska) · M5 (kör/ezber) |
| `trap.jsonl` | **35** | M2 (near-miss yanlış-kaynak reddi) |

`core_hard` alanları: `messages` · `kanun_adi` · `kanun_no` · `madde_no` · `_complexity` ·
`_src_len` · `_set`
`trap` alanları: yukarıdakiler + `gold_madde_no` (doğru madde) · **`expected: "abstain"`** ·
`_overlap` (tuzak↔gold leksik örtüşme)

> **Tuzağın mantığı:** `madde_no` modele *gösterilen* (yanlış) madde, `gold_madde_no` gerçek
> cevabın olduğu madde. Doğru davranış = cevap uydurmak değil, **reddetmek**.

### `eval/genelleme/` — aile-ötesi genelleme dilimleri

| dosya | satır | ne test eder |
| :--- | ---: | :--- |
| `trap_xkanun.jsonl` | 35 | **çapraz-kanun** tuzağı (yapısal, görece kolay-red). Ek alan: `gold_kanun_adi/no`, `_trap_text`, `_gold_text` |
| `trap_ood.jsonl` | 35 | **görülmemiş kanun** tuzağı |
| `ood_qa.jsonl` | 35 | held-out **novel soru** (en zor eksen: ilke mi, kalıp mı?). Alanlar: `gold_madde_no`, `gold_text`, `_dogruluk`, `_cevaplanabilir`, `_gerekce` |

**M3 (boş bağlam, n=40)** ayrı dosya değil — `gen_eval_grounded.py --empty-context` ile
`core_hard`'dan türetilir.

### `eval/dev/` — DEV havuzu (seçim burada yapılır; TEST `canon/`'dur)

| dosya | satır | ne |
| :--- | ---: | :--- |
| `core_hard.jsonl` | **80** | DEV v2; önceki sürüm `core_hard.jsonl.v1-2026-09-06`, onarım künyesi `eval/KUNYE_soru_onarimi_2026-09-06.json` |
| `trap.jsonl` | 70 | M2 tuzakları |
| `baglam/h1-k10.json` | 80 | dondurulmuş bağlam, sha256 `02666800…f213e6135` ([#82](../docs/record/kronoloji-75-86.md#82)) |

### CANON sabitleri (hepsi ortak)
seed **3407** · hakem **gpt-4o-mini** (cross-judge gpt-4o) · eval-mirror **900 char** chunk clip ·
A1 = cevaplanan-only macro.

---

## `train/` — eğitim setleri

Her dizin `train.jsonl` + `validation.jsonl` (+ varsa `test.jsonl`) taşır → `--data <dizin>`
ile doğrudan verilir.

### `train/grounded_qa/` — gerçek maddeye dayalı Q&A (temel havuz)
| bölüm | satır |
| :--- | ---: |
| train | **19.305** |
| validation | 1.131 |
| test | 1.022 |

`{"messages": [...], "source": ..., "kanun_adi": ..., "madde_no": ..., "kanun_no": ...}`

Sonraki her şeyin **tohumu**: soru↔gold madde eşleşmesi buradan gelir (RAFT paketleme ve ORPO
tuzak üretimi bu setin sorularını kullanır).
⚠️ Bu setin *cevapları* düz SFT'de kullanıldığında **abstention'ı yok etti** (bkz aşağıdaki uyarı) —
değerli olan **soru↔madde eşleşmesi**, cevaplar değil.

### `train/raft/` — gold + hard-negative distractor (RAFT)
| bölüm | satır |
| :--- | ---: |
| train | **17.323** |
| validation / test | 962 / 962 |

`{"messages": [...], "slice": ..., "gold_madde_no": ..., "gold_kanun_no": ...}`
`assemble_report.json`: girdi 19.305 → **kabul 18.670 / red 635** (630'u "uydurma alıntı:
quote gold'da yok", 5'i atıf no eşleşmiyor) + 577 replay.

Distractor seçimi **hard-negative**: aynı kanun, komşu madde no öncelikli (gerçek retriever'ı
taklit eder). Rastgele distractor eval'i kolaylaştırdığı için reddedildi (ADR-0013).
Paketleyici `scripts/veri_hazirlik/raft_pack.py` — **eval ve eğitim aynı modülü kullanır**, dağılım sapmasın.

### `train/raft_scrubbed/` — `raft/`'ın öğretmen jargonundan temizlenmiş hâli
| bölüm | satır |
| :--- | ---: |
| train | **17.323** |
| validation / test | 962 / 962 |

`scripts/veri_hazirlik/scrub_teacher_jargon.py` ile üretildi; ham `raft/`'ta cevapların 1.301/17.323'ünde
`GOLD`/`DISTRACTOR` etiketi vardı ([#39](../docs/record/kronoloji-39-52.md#39)). **`τ_g` v1 bu setle eğitildi**
([`kollar.md`](../docs/record/kollar.md)).

### `train/orpo_abstain/` — tercih çiftleri (abstention)
| bölüm | satır |
| :--- | ---: |
| train | **1.741** |
| validation / dev | 53 / 80 |

`{"prompt", "chosen", "rejected", "is_pref", "_kind", "_hi_overlap"}`

`orpo_report.json`: abstain-çifti **1.495** + grounding-replay **299** (replay_frac 0.20,
interleave 6). Atlanan: 224 "kontrast yok", 9 dev.

> **`is_pref` alanı kritik:** `1` = gerçek tercih çifti (tam ORPO), `0` = grounding-replay
> (yalnız NLL akar = SFT-replay). `scripts/egitim/train_orpo.py:MaskedORPOTrainer` bu maskeyi
> NaN-safe uygular. Bu olmadan replay satırları OR-terimini zehirler.

⚠️ `rejected` tarafı **12B'nin ürettiği gerçek fabrikasyonlardır.** Yeni base ile çalışırken
seti olduğu gibi kullanmak "başka bir modelin hatalarını" öğretir. Doğrusu: `--rejected`
havuzunu **yeni base ile yeniden hasat et** (`scripts/veri_hazirlik/gen_v3_rejected.py`), `chosen` ve
tuzak kurgusu yeniden kullanılabilir.

### `train/orpo_abstain_cp2c/` — Qwen'in kendi hasadından tercih çiftleri
| bölüm | satır |
| :--- | ---: |
| train | **845** |
| validation | 26 |

`orpo_report.json`: abstain-çifti **726** (m2 538 · m2b 188) + grounding-replay **145** = 871; hasat
kaynakları cp2c 3 · cp2c-64 357 · cp2c-ek1 366. **`τ_a` v1 bu setle eğitildi** ([`kollar.md`](../docs/record/kollar.md)).

### `train/replay_tr.jsonl`
Genel Türkçe replay havuzu (`{"messages": [...]}`) — hukuk sızıntısı regex'le elenmiş.
Katastrofik unutmayı bastırmak için eğitim setine %3-20 oranında karıştırılır.

---

## `index/` — retriever indeksleri

`mevzuat_bge_m3_s2/` canlı indekstir (S2: yürürlük alanı + alt madde kimliği). `mevzuat_bge_m3/` S2 öncesidir;
yalnız eski sayıları yeniden üretmek için ve `tests/test_retriever.py` kullandığı için duruyor. `gomme.npy`
git'te yok (`.gitignore:150`); HF `Rfetha/HakHukuk-mevzuat-bge-m3-s2`'den `python -m hakhukuk.dagitim.indir`
ile `sha256` kapısıyla iner.

---

## `_ham_ve_ara/` — ara ve yeniden-üretilebilir

Hattın ara çıktıları. Silinebilir (script'le yeniden üretilir) ama pahalı olduğu için duruyor.

| dosya | satır | ne |
| :--- | ---: | :--- |
| `grounded_qa_raw_pool.jsonl` | 21.648 | filtre öncesi ham havuz |
| `raft_packed.jsonl` | 19.305 | cevap üretilmeden önceki paketlenmiş bağlam |
| `raft_answers.jsonl` | 19.305 | + `answer` alanı (kalite filtresinden önce) |
| `orpo_packed.jsonl` | 19.284 | tuzak kurgusu (`trap_text`, `ov_gold`, `n_far` …) |
| `orpo_chosen.jsonl` | 19.284 | red cevapları (gpt-4o-mini üretimi) |
| `orpo_rejected.jsonl` | **1.728** | 12B'nin gerçek fabrikasyonları (`model_answer`, `abstained`, `judge_flag`) |
| `SUPERSEDED_*.jsonl` | — | CANON öncesi eval setleri; **kıyasa girmez**, tarihsel |

---

## ⚠️ Bu veriyle çalışırken bilinmesi gerekenler

1. **Kaynaksız QA verisi kullanma.** Forum verisiyle eğitilen ilk tur battı: tek bir cevap
   154 farklı soruya birebir yapıştırılmıştı. ⚠️ Setin kendisi (`sft_v0_KIRLI_forum`) **artık
   yok** — git'e hiç girmemişti ve emekli hat ağacıyla birlikte silindi (ADR-0034). Dersin kaydı
   duruyor: [`gemma4-12b-kronoloji.md` #02](../docs/record/gemma4-12b-kronoloji.md).
2. **Düz SFT abstention'ı yok eder.** `grounded_qa` cevaplarıyla düz SFT: red oranı
   0.741 → 0.000. Grounding kazanılırken "bilmiyorum deme" siliniyor.
3. **Eval-mirror şart.** Eğitimde uygulanan chunk kırpması (900 char) eval'de **birebir**
   uygulanmalı; yoksa model eğitildiğinden uzun bağlamla ölçülür (haksız kıyas).
4. **Her yeni set EDA ile doğrulanır.** `newmindai/EuroHPC-Legal` kağıt üstünde mükemmeldi
   (43K, Apache-2.0); örnekleme eşleşmeyen Q&A, uydurma kanunlar ve Osmanlı içeriği çıkardı → reddedildi.
5. **Kapsam:** yalnız **yürürlükteki TC mevzuatı.** Ticari kaynak (Lexpera, Kazancı) asla —
   telif zehiri.

## Git politikası (2026-07-24 kararı)

**`data/` tamamı versiyonlanır** — veri + ölçüm çıktısı araştırma repro'sunun kendisi.
Toplam ~403 MB, GitHub'ın 1 GB önerisinin altında.

⚠️ **Tek sert kural: hiçbir dosya 100 MB'ı aşmasın.** GitHub o eşikte push'u **reddeder** (uyarı
değil, blok). Şu an en büyük dosya `_ham_ve_ara/raft_answers.jsonl` = **98.2 MB — sınıra 1.8 MB kala.**
Bu dosya yeniden üretilir de biraz büyürse push kırılır. O gün üç seçenek var:
böl · Git LFS'e al · `_ham_ve_ara/`'yı takipten çıkar (zaten yeniden-üretilebilir ara dosyalar).

Model ağırlıkları (`*.safetensors`, `*.gguf`, `*.pt`) **hiçbir zaman** git'e girmez — bir adapter
250 MB, bir GGUF 6-15 GB.

## Geçmiş turların sayıları
`git show a19fc25^:old-version-gemma4-12b/record/SCORECARD.md` (12B protokolü, tarihsel — repo dışı
devir paketi 2026-07-29'da silindi, ADR-0034 üst notu; `RECETELER_12B.md` **kayıp**) ·
repo içi kronoloji: [`docs/record/gemma4-12b-kronoloji.md`](../docs/record/gemma4-12b-kronoloji.md)
