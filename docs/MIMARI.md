# Mimari — `v1` zinciri

> `referans-design-doc.md`'nin işlevini devralır. **Her kutu ya var olan bir dosyaya ya da
> bir [`ROADMAP.md`](../ROADMAP.md) adımına işaret eder** — döngüyle sınanır, gözle değil
> (`tests/test_mimari.py`).

## Bir bakışta

```
                    EĞİTİM (bir kez, Modal)                    ÇALIŞMA ZAMANI (her soruda)
  ┌──────────────────────────────────────┐        ┌──────────────────────────────────────┐
  │ Qwen3.5-4B  (ham base, PARAMETRE)    │        │  soru                                │
  │        │                             │        │    │                                 │
  │        ├──► QLoRA τ_g  (1.083 adım)  │        │    ▼                                 │
  │        └──► QLoRA τ_a  (70 adım)     │        │  retriever.py  (CPU · GPU'ya GİRMEZ) │
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

## Dosya → sorumluluk

### Ürün — `hakhukuk/` *(pip ile kurulur, `scripts/`'e bağımlı değildir\*)*

| dosya | tek sorumluluğu |
| :--- | :--- |
| [`istem.py`](../hakhukuk/istem.py) | İstem metinlerinin **TEK kaynağı** — sürümlü sabitler + `sha256` damgası. Damga değişmeden metin değişemez (test kapısı). |
| [`tipler.py`](../hakhukuk/tipler.py) | `Durum` (4 hâl) · `Kaynak` · `Atif` · `Cevap` · `Yururluk` — donmuş `dataclass`'lar |
| [`terazi.py`](../hakhukuk/terazi.py) | `siniflandir()` — cevabı dört duruma ayırır, atıfları kaynağa karşı **deterministik** doğrular |
| [`servis.py`](../hakhukuk/servis.py) | **Derin modül:** `answer(soru) → Cevap`. Retriever + llama-server + istem + terazi **içeride gizli** |
| [`cli.py`](../hakhukuk/cli.py) | `hakhukuk "soru"` — ince kabuk. `SORUMLULUK_IBARESI`'nin **tek kaynağı** |
| [`tui.py`](../hakhukuk/tui.py) | `hakhukuk-tui` — `textual` tek ekran, ince kabuk (mantık sızıntısı **testle yasak**) |
| `araclar.py` | **YOK** — 5 deterministik KALDIRAÇ; [ADR-0076](adr/kararlar-0064-0085.md#adr-0076) |
| `kurulum.py` | **YOK** — indeks indirme; [ROADMAP · Görev 8](../ROADMAP.md) |

**KAPI ↔ KALDIRAÇ:** `terazi.py`'nin kontrolleri (atıf doğrulama · durum sınıflandırma) ve
`retriever`'ın mülga süzgeci **KAPI**'dır — tool döngüsünün **dışında**, koşulsuz çalışır.
`araclar.py`'dekiler **KALDIRAÇ**'tır — model çağırır ya da çağırmaz. Karıştırılmaları
uydurulmuş madde **0/114** garantisini kaybettirir ([ADR-0076](adr/kararlar-0064-0085.md#adr-0076)).

\* **Bugünkü tek istisna, bilinçli:** `terazi.py` iki normalizasyonu `scripts/`'ten
**import ediyor** (`score_abstention.REJECT_RE` · `madde_anahtar.madde_anahtari`).
Gerekçe: bunlar ölçüm hattının kalbi ve kopyalanırlarsa **sessizce ayrışırlar** — istem
sürüklenmesinin (S18) aynısı olurdu. **Bedeli:** ürün paketi bugün `scripts/`'siz tam
çalışmıyor; paketleme turunda ödenecek borç.

### Ölçüm aleti — `scripts/` *(72 dosya, ürün DEĞİL)*

| klasör | ne yapar |
| :--- | :--- |
| `egitim/` | eğitim · merge · GGUF · araç zinciri |
| `olcum_uretim/` | harness koşucuları · tek üretim gövdesi · tanılama |
| `puanlama/` | hakem · skorlama · tablolar · `llm_client` · `runlock` |
| `erisim_korpus/` | **`retriever.py`** · recall · korpus bütünlüğü · atıf doğrulama |
| `veri_hazirlik/` | SFT/ORPO/RAFT veri kurulumu · hasat zinciri |
| [`yeniden_uret.sh`](../scripts/yeniden_uret.sh) | manşet sayıyı sıfırdan üretir — [`docs/YENIDEN_URETIM.md`](YENIDEN_URETIM.md) |

Kardeş import'lar **uzantısız** ve **27 dosyada aynı yol köprüsü** var
(`grep -rl "yol köprüsü" scripts/`). `tests/conftest.py` aynı mantığı yansıtır —
**birini değiştiren ötekini de değiştirir**.

### Veri

| yol | ne | git'te mi |
| :--- | :--- | :--- |
| `data/corpus/mevzuat_maddeler.jsonl` | 892 kanun · 40.496 madde · 2.547 mülga | (37 MB) |
| `data/corpus/KUNYE.json` | **anlık görüntü künyesi** — tarih · kapsam · kapsam **dışı** · `sha256` | Evet |
| `data/index/mevzuat_bge_m3_s2/` | `bge-m3` gömme + `KUNYE.json` | **hayır** — `.gitignore:166` |
| `data/eval/dev/core_hard.jsonl` | DEV, 80 kalem (v2) | Evet |
| `data/eval/canon/` | **donmuş TEST** — tek kez açılır | Evet |

## Rejim değişmezleri — uyuşmazlık hata VERMEZ, kıyası geçersiz kılar

`seed 3407` · `max_chunk_chars 900` · `thinking on` · düşünce **1024** + cevap **512** = **1536**
· `harness_k 10` · `RRF_K 10` · **önsözsüz** · indeks `mevzuat_bge_m3_s2` ·
hakem `openai/gpt-4o-mini` ([ADR-0074](adr/kararlar-0064-0085.md#adr-0074)).

## `v1` ↔ `v2` sınırı

**`v1` içinde:** yerel indeks · anlık görüntü korpus · CLI + TUI · yeniden üretim yolu.
**`v2`'ye kalan:** canlı `bedesten` API (B6, TR IP şart) · tam kapsam (yönetmelik/tüzük) ·
tazelik boru hattı · HTTP API + barındırma (**S9**) · tablo/cetvel satırları (B9).
