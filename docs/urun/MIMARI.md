# Mimari — `v1` zinciri

> `referans-design-doc.md`'nin işlevini devralır. **Her kutu ya var olan bir dosyaya ya da
> bir [`ROADMAP_v1.md`](../yol_haritasi/ROADMAP_v1.md) adımına işaret eder** — döngüyle sınanır, gözle değil
> (`tests/depo/test_belgeler.py`).

## Bir bakışta

```
                    EĞİTİM (bir kez, Modal)                    ÇALIŞMA ZAMANI (her soruda)
  ┌──────────────────────────────────────┐        ┌──────────────────────────────────────┐
  │ Qwen3.5-4B  (ham base, PARAMETRE)    │        │  soru                                │
  │        │                             │        │    │                                 │
  │        ├──► LoRA τ_g  (1.083 adım)   │        │    ▼                                 │
  │        └──► LoRA τ_a  (70 adım)      │        │  getirici.py  (CPU · GPU'ya GİRMEZ)  │
  │                İKİSİ DE ham base'den │        │    · BM25 + bge-m3, RRF (K=10)       │
  │                BAĞIMSIZ              │        │    · yürürlük süzgeci (mülga elenir) │
  │        ▼                             │        │    ▼                                 │
  │  ham TIES (eşzamanlı 2-yollu)        │        │  istem.py  (TEK kaynak + sha256)     │
  │        ▼                             │        │    ▼                                 │
  │  tgta_v1  ──► GGUF Q4_K_M (2,59 GiB) │───────►│  llama-server  (GPU)                 │
  └──────────────────────────────────────┘        │    ▼                                 │
                                                   │  terazi.py  (4 durum + atıf doğrula) │
                                                   │    ▼                                 │
                                                   │  Cevap ──► cli.py / tui.py           │
                                                   └──────────────────────────────────────┘
```

**Ölçüm motoru ([ADR-0109](../adr/kararlar-0064-0085.md#adr-0109)).** Kullanıcıya giden yol da ölçülen yol da yukarıdaki llama-server + Q4_K_M'dir.
vLLM pilotlandı ve ölçüme alınmadı (aynı ağırlıkla −3,6 p, koşudan koşuya ±2,25 p; [#87](../record/kronoloji-87-98.md#87)); yalnız GRPO'nun cevap
üretimi için düşünülür.

## Dosya → sorumluluk

### Ürün — `hakhukuk/` *(pip ile kurulur, `scripts/`'e bağımlı değildir)*

| dosya | tek sorumluluğu |
| :--- | :--- |
| [`istem.py`](../../hakhukuk/cekirdek/istem.py) | İstem metinlerinin **TEK kaynağı** — sürümlü sabitler + `sha256` damgası. Damga değişmeden metin değişemez (test kapısı). |
| [`tipler.py`](../../hakhukuk/cekirdek/tipler.py) | `Durum` (4 hâl) · `Kaynak` · `Atif` · `Cevap` · `Yururluk` — donmuş `dataclass`'lar |
| [`terazi.py`](../../hakhukuk/cekirdek/terazi.py) | `siniflandir()` — cevabı dört duruma ayırır, atıfları kaynağa karşı **deterministik** doğrular |
| [`servis.py`](../../hakhukuk/cekirdek/servis.py) | **Derin modül:** `answer(soru) → Cevap`. Retriever + llama-server + istem + terazi **içeride gizli** |
| [`cli.py`](../../hakhukuk/arayuz/cli.py) | `hakhukuk "soru"` — ince kabuk. `SORUMLULUK_IBARESI`'nin **tek kaynağı** |
| [`tui.py`](../../hakhukuk/arayuz/tui.py) | `hakhukuk-tui` — `textual` tek ekran, ince kabuk (mantık sızıntısı **testle yasak**) |
| [`api.py`](../../hakhukuk/arayuz/api.py) | `hakhukuk-api` — ince kabuk; yerel, tek kullanıcı (S9 açılmadı) |
| [`getirici.py`](../../hakhukuk/cekirdek/getirici.py) | Hibrit arama (BM25 + `bge-m3`, RRF) ve mülga süzgeci; ölçüm hattı da aynı modülü kullanır |
| [`atif_dogrula.py`](../../hakhukuk/cekirdek/atif_dogrula.py) · [`madde_anahtar.py`](../../hakhukuk/cekirdek/madde_anahtar.py) · [`ret_deseni.py`](../../hakhukuk/cekirdek/ret_deseni.py) | atıf doğrulama · madde kimliği · deterministik red deseni; ölçüm hattıyla TEK kaynak |
| [`araclar.py`](../../hakhukuk/cekirdek/araclar.py) | 5 deterministik KALDIRAÇ — `ara` · `madde_getir` · `madde_var_mi` · `kanun_bul` · `yururlukte_mi`; [ADR-0076](../adr/kararlar-0064-0085.md#adr-0076) |
| [`indir.py`](../../hakhukuk/dagitim/indir.py) | Artefakt indirme KAPISI — pinli revizyon, `sha256` ve bayt; GGUF ve indeks |

**KAPI ↔ KALDIRAÇ:** `terazi.py`'nin kontrolleri (atıf doğrulama · durum sınıflandırma) ve
`retriever`'ın mülga süzgeci **KAPI**'dır — tool döngüsünün **dışında**, koşulsuz çalışır.
`araclar.py`'dekiler **KALDIRAÇ**'tır — model çağırır ya da çağırmaz. Karıştırılmaları
uydurulmuş madde **0/114** garantisini kaybettirir ([ADR-0076](../adr/kararlar-0064-0085.md#adr-0076)).

Ürünle ölçüm hattının paylaştığı dört parça (getirici · atıf doğrulama · madde kimliği · red deseni)
pakettedir; `scripts/` onları paketten içe aktarır. Kopyalanmazlar: kopya **sessizce ayrışır** (S18).

### Ölçüm aleti — `scripts/` *(ürün DEĞİL)*

| klasör | ne yapar |
| :--- | :--- |
| `egitim/` | eğitim · merge · GGUF · araç zinciri |
| `olcum_uretim/` | harness koşucuları · tek üretim gövdesi · tanılama |
| `puanlama/` | hakem · skorlama · tablolar · `llm_client` · `runlock` |
| `erisim_korpus/` | getirici ve atıf doğrulamanın komut satırları · recall · korpus bütünlüğü |
| `veri_hazirlik/` | SFT/ORPO/RAFT veri kurulumu · hasat zinciri |
| [`yeniden_uret.sh`](../../scripts/yeniden_uret.sh) | manşet sayıyı sıfırdan üretir — [`docs/yontem/YENIDEN_URETIM.md`](../yontem/YENIDEN_URETIM.md) |

Kardeş import'lar **uzantısız** ve birçok dosyada **aynı yol köprüsü** var
(`grep -rl "yol köprüsü" scripts/` listeler). `tests/conftest.py` aynı mantığı yansıtır —
**birini değiştiren ötekini de değiştirir**.

### Veri

| yol | ne | git'te mi |
| :--- | :--- | :--- |
| `data/corpus/mevzuat_maddeler.jsonl` | 892 kanun · 40.496 madde · 2.547 mülga | (37 MB) |
| `data/corpus/KUNYE.json` | **anlık görüntü künyesi** — tarih · kapsam · kapsam **dışı** · `sha256` | Evet |
| `data/index/mevzuat_bge_m3_s2/` | `bge-m3` gömme + `KUNYE.json` | **hayır** — `.gitignore:150` |
| `data/eval/dev/core_hard.jsonl` | DEV, 80 kalem (v2) | Evet |
| `data/eval/canon/` | **donmuş TEST** — tek kez açılır | Evet |

## Rejim değişmezleri — uyuşmazlık hata VERMEZ, kıyası geçersiz kılar

`seed 3407` · `max_chunk_chars 900` · `thinking on` · düşünce **1024** + cevap **512** = **1536**
· `harness_k 10` · `RRF_K 10` · **önsözsüz** · indeks `mevzuat_bge_m3_s2` ·
hakem `openai/gpt-4o-mini` ([ADR-0074](../adr/kararlar-0064-0085.md#adr-0074)).

## `v1` ↔ `v2` sınırı

**`v1` içinde:** yerel indeks · anlık görüntü korpus · CLI + TUI · yeniden üretim yolu.
**`v2`'ye kalan:** canlı `bedesten` API (B6, TR IP şart) · tam kapsam (yönetmelik/tüzük) ·
tazelik boru hattı · HTTP API + barındırma (**S9**) · tablo/cetvel satırları (B9).
