# vLLM geçişi uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sunucu tarafında (ölçüm, benchmark, hasat kapısı) vLLM'in toplu üretim hızını, ürünü (Q4_K_M GGUF + llama.cpp) bozmadan kullanıma almak; her işte hangi aracın kazandığını pilotla ölçmek.

**Architecture:** Eğitim çıktısı bf16 safetensors asıl kayıt olur; seçim işleri vLLM bf16'da, nihai sayı Q4_K_M + llama.cpp'de ölçülür. Pilot üç koşuyu (Q4_K_M llama.cpp referansı, Q4'ten açılmış ağırlık vLLM'de, orijinal bf16 vLLM'de) beş kapıyla karşılaştırır; kapılar geçmezse iş eski aracında kalır. Tasarım: [`../specs/2026-10-15-vllm-gecis-tasarim.md`](../specs/2026-10-15-vllm-gecis-tasarim.md).

**Tech Stack:** Python 3.11 (`~/code/global_venv`), pytest, Modal (A10), vLLM 0.30.0, llama.cpp b10902, DeepSeek V4.1 Flash hakem (OpenRouter), `gguf`, `safetensors`.

## Global Constraints

Bu bölüm her görevin gereksinimidir.

- Dil: belgeler, yorumlar, commit mesajları Türkçe; kod tanımlayıcıları mevcut betiklerdeki gibi Türkçe-ASCII (`kutle`, `agirlik`). Yayımlanan belgelerde emoji yok.
- **Önce sun, sonra değiştir:** mevcut bir dosyaya dokunan her belge değişikliği önce "dosya · bölüm · şimdi → olacak" listesi olarak sunulur, kullanıcının açık "işle" onayıyla yapılır. Karar onayı düzenleme onayı değildir. Yeni dosya yazmak (kod, test) planın kendi onayı altındadır.
- **Para harcayan ya da dışarı giden her iş** (Modal koşusu, hakem çağrısı, yükleme) başlamadan önce `AskUserQuestion` ile onay alınır. Faz 2 toplam sınırı $5; aşılırsa durulur ve kullanıcıya dönülür.
- **Commit yalnız kullanıcı isteyince; push yok.** Planda "Commit" adımları kullanıcı istediğinde yapılır.
- Anahtarlar: `.env` içeriği asla basılmaz ve kayda geçmez; kiralık makineye hakem ya da API anahtarı gönderilmez; künyeye TOKEN/SECRET/KEY içeren değişken yazılmaz.
- Hugging Face anahtarı yalnız `Rfetha/HakHukuk-yedek` deposunu okuyup yazabilir; başka bir HF işi gerekirse önce sorulur. Bu plan HF'ye hiçbir şey yüklemez.
- Aynı oturumda numara almadan önce `git log` ve `git show HEAD:<dosya>` ile başka oturumun numara alıp almadığına bakılır. Sıradaki kronoloji girdisi #86, sıradaki ADR 0106 (bu planın Görev 1'i alır).
- Ölçüm rejimi: seed 3407 · 900 karakter kırpma · düşünme açık, 1024 + 512 bütçe · h1 (k=10, RRF_K=10) · n=80 · dondurulmuş bağlam `data/eval/dev/baglam/h1-k10.json` (sha256 `02666800…f213e6135`). Rejim `scripts/olcum_uretim/olcum_karti.py::REJIM`'de tek yerdedir; kopyalanmaz.
- Kapı ölçütleri bu planda ve spec'te pilot sonucunu görmeden kilitlidir: G2 ≤ 640,6 s ÷ 3, G3 ≤ 0,6 puan, kesik ≤ %5. Sonuç görüldükten sonra değiştirilmez (değiştirmek ayrı ADR ister).
- 4-bit safetensors yapılmaz; Docker ürün compose'u (`docker/compose.yaml`, `tests/test_konteyner.py`) değişmez; bf16 açık HF yayını bu planın dışındadır.
- Testler: `source ~/code/global_venv/bin/activate && python -m pytest -q -p no:cacheprovider -m "not slow"`. Başlangıç durumu 550 geçti, 0 kaldı.

## Alt-ajan notu

Görev 5 (para ve yükleme) ve Görev 8 (mevcut belgeleri düzenleme) **ana oturumda**, kullanıcı onayıyla yapılır. Alt-ajanlara yalnız kod görevleri verilir: Görev 2, 3, 4, 6, 7. Görev 1 (ADR-0106 ve plan kuralı belge düzenlemeleri) ana oturumda yapılır.

## Dosya haritası

| dosya | sorumluluk | görev |
| :-- | :-- | :-- |
| `docs/adr/kararlar-0064-0085.md` | ADR-0106 bloğu | 1 |
| `scripts/olcum_uretim/bf16_yukle.py` (yeni) | bf16 dosya listesi, sha256 manifesti, `modal volume put` komutları | 2 |
| `scripts/olcum_uretim/modal_pilot_vllm.py` (yeniden yazılır) | Modal A10: aşama A ve B, iki ağırlık | 3 |
| `scripts/olcum_uretim/vllm_kapilari.py` (yeni) | G1-G5 değerlendirmesi (saf fonksiyonlar) | 4 |
| `scripts/olcum_uretim/vllm_ozetle.py` (yeni) | dosyalardan kapı girdisi toplar, `OZET.json` yazar | 4 |
| `outputs/eval/f0/f016-vllm-pilot/kos.sh` (yeni) | pilot cevaplarının hakem puanlaması | 4 |
| `scripts/olcum_uretim/makine_kapisi_puan.py` (yeni) | makine geçiş kapısının puan düzeyi dalı | 6 |
| `scripts/olcum_uretim/hasat_ortusme.py` (yeni) | hasat kapısı: Q4 hataları bf16'da da var mı | 7 |

---

### Görev 1: Karar kaydı (ADR-0106) ve plan kuralı

**Files:**
- Modify: `docs/adr/kararlar-0064-0085.md` (sona ADR-0106 bloğu)
- Modify: `docs/adr/README.md` (0106 satırı, numaralandırma satırı)
- Modify: `CLAUDE.md` (iki yer: dosya ağacı satırı ve "Documentation discipline" madde; işaretçi satırı)
- Modify: `docs/superpowers/specs/2026-10-15-vllm-gecis-tasarim.md` (iki sapma notu)

**Interfaces:**
- Produces: `ADR-0106` bağlantı çapası `#adr-0106`; sonraki görevler bu numarayı kullanır.

- [ ] **Step 1: Numara çakışması kontrolü**

Run: `git log --oneline -5 && grep -n 'id="adr-010[6-9]"' docs/adr/kararlar-0064-0085.md; git show HEAD:docs/adr/README.md | grep -n "0106"`
Expected: yeni commit yok ya da yalnız bu oturumunkiler; `adr-0106` çapası YOK. Varsa durulur, numara bir sonraki boş olana çekilir ve bu planda `0106` her yerde değiştirilir.

- [ ] **Step 2: Değişiklik listesini kullanıcıya sun**

Aşağıdaki listeyi metin olarak yaz, sonra `AskUserQuestion` ile "işle" onayı iste:

| dosya · bölüm | şimdi → olacak |
| :-- | :-- |
| `docs/adr/kararlar-0064-0085.md` sonu | (yok) → ADR-0106 bloğu (aşağıda tam metin) |
| `docs/adr/README.md` ADR tablosu, 0105 satırından sonra | (yok) → 0106 satırı |
| `docs/adr/README.md` "Numaralandırma" satırı | "**0106**'dan devam" → "**0107**'den devam" |
| `docs/adr/README.md` ilgili kardeş-dosya satırı (`kararlar-0064-0085.md` tablosu, "uygulama hattı (0104-0105)") | → "… · vLLM geçişi (0106)" eklenir |
| `docs/adr/README.md` ADR-0056 satırı | sonuna "*(plan kuralı 0106'da: vLLM planı F0 planıyla birlikte canlı)*" |
| `CLAUDE.md` satır ~54 (dosya ağacı) | "at most one live plan (ADR-0056)" → "at most one live plan (ADR-0056; ADR-0106 lets the vLLM plan run beside F0 until it closes)" |
| `CLAUDE.md` satır ~141 ("Doc types") | "**at most one live plan**, ADR-0056)" → "**at most one live plan**, ADR-0056; exception ADR-0106)" |
| `CLAUDE.md` satır ~74 (ADR işaretçisi) | "ledger runs to **0105**, next is **0106**" → "ledger runs to **0106**, next is **0107**" |
| spec §4 "ölçüm hattı" satırı | "`gen_eval_grounded.py` toplu yola alınır" → "`gen_eval_grounded.py` değişmez; resmî toplu yol `toplu_uret.py` (aynı kayıt biçimi); `makine_kapisi_puan.py` eklenir" |
| spec §7 faz 4 satırı | "hasat kapısı ve uyarlama" → "hasat kapısı (uyarlama, kapı geçerse ayrı plan)" |

ADR-0106 bloğunun tam metni (sona eklenir; `---` ayracıyla):

```markdown
<a id="adr-0106"></a>
## ADR-0106 — vLLM geçişi: planı F0 planıyla birlikte canlı; araç seçimi iş başına

**Karar (insan, 2026-10-15):** [ADR-0056](kararlar-0045-0063.md#adr-0056)'nın "aynı anda en fazla bir canlı plan" konvansiyonu bir istisna alır: F0 zemin planı (`2026-10-11-F0-zemin.md`) ve vLLM geçiş planı (`2026-10-15-vllm-gecis.md`) birlikte canlıdır. vLLM planı kapanınca (Görev 9) kayda dönüşür ve silinir (ADR-0083 emsali); konvansiyon yeniden "en fazla bir canlı plan" olur.

**Gerekçe.** vLLM planı F0.10'dan önce yürür ve F0.8–F0.15'in ölçüm hattını etkiler. F0 planına bölüm olarak eklemek F0'ı iki katına çıkarır; F0'ı kapatıp yeni plan açmak F0.8–F0.15'i taşımayı gerektirir. Kullanıcı ayrı dosyayı seçti. Tasarım ve ilke ("araç seçimi iş başınadır; bir iş vLLM'e yalnız ilgili kapıyı geçerse taşınır") [spec](../superpowers/specs/2026-10-15-vllm-gecis-tasarim.md)'te.

**Elenen:** F0 planına yeni bölüm · F0'ı kapatıp yeni plan açmak.

**Değiştirdiği kayıt:** ADR-0056 konvansiyonu (metnine dokunulmaz); `CLAUDE.md` dosya ağacı ve belge türleri satırları.
```

- [ ] **Step 3: Onaydan sonra değişiklikleri yap**

ADR bloğunu `docs/adr/kararlar-0064-0085.md` sonuna ekle (bağlantı yolları o dosyanın konumuna göre yukarıda yazılı). CLAUDE.md ve README satırlarını yukarıdaki tabloya göre değiştir.

- [ ] **Step 4: Bağlantı testi**

Run: `source ~/code/global_venv/bin/activate && python -m pytest -q -p no:cacheprovider tests/test_belgeler.py`
Expected: `4 passed`.

- [ ] **Step 5: Commit (kullanıcı isterse)**

```bash
git add docs/adr/kararlar-0064-0085.md docs/adr/README.md CLAUDE.md docs/superpowers/specs/2026-10-15-vllm-gecis-tasarim.md docs/superpowers/plans/2026-10-15-vllm-gecis.md
git commit -m "docs: ADR-0106 vLLM geçişi planı, spec ve uygulama planı"
```

---

### Görev 2: bf16 yükleme betiği ve manifesti

**Files:**
- Create: `scripts/olcum_uretim/bf16_yukle.py`
- Create: `tests/test_bf16_yukle.py`
- Create (üretilir): `outputs/eval/f0/f016-vllm-pilot/bf16_manifest.json`

**Interfaces:**
- Produces:
  - `bf16_yukle.dosyalar(dizin: str) -> list[str]` (sıralı dosya adları; `.safetensors` yoksa `SystemExit`)
  - `bf16_yukle.manifest(dizin: str, adlar: list[str] | None = None) -> dict` → `{"dizin": str, "dosyalar": {ad: {"bayt": int, "sha256": str}}}`; olmayan dosya sessizce atlanır (eksiklik `farklar`'da görünür)
  - `bf16_yukle.farklar(beklenen: dict, eldeki: dict) -> list[str]` (boş liste = aynı)
  - `bf16_yukle.put_komutlari(dizin: str) -> list[list[str]]`
  - `bf16_yukle.HACIM_YOLU = "/f016-vllm-pilot/bf16"`
- Görev 3 `manifest` ve `farklar` kullanır.

- [ ] **Step 1: Başarısız testi yaz**

`tests/test_bf16_yukle.py`:

```python
"""Orijinal bf16 ağırlıkların Modal hacmine yüklenmesi: dosya seçimi, sha256 manifesti, fark raporu."""
import hashlib

import pytest

import bf16_yukle as by  # noqa: E402


def _klasor(tmp_path):
    (tmp_path / "model-00001.safetensors").write_bytes(b"a" * 10)
    (tmp_path / "model-00002.safetensors").write_bytes(b"b" * 20)
    (tmp_path / "model.safetensors.index.json").write_text("{}")
    (tmp_path / "config.json").write_text("{}")
    (tmp_path / "LICENSE").write_text("x")
    (tmp_path / "README.md").write_text("x")
    return str(tmp_path)


def test_dosyalar_yalniz_agirlik_yapilandirma_ve_tokenizer_dosyalarini_secer(tmp_path):
    assert by.dosyalar(_klasor(tmp_path)) == [
        "config.json", "model-00001.safetensors", "model-00002.safetensors", "model.safetensors.index.json"]


def test_safetensors_yoksa_durur(tmp_path):
    (tmp_path / "config.json").write_text("{}")
    with pytest.raises(SystemExit, match="safetensors"):
        by.dosyalar(str(tmp_path))


def test_manifest_bayt_ve_sha256_icerir(tmp_path):
    m = by.manifest(_klasor(tmp_path))
    assert m["dosyalar"]["model-00001.safetensors"] == {"bayt": 10, "sha256": hashlib.sha256(b"a" * 10).hexdigest()}


def test_farklar_ayni_klasorde_bos_degisen_ve_eksik_dosyada_dolu(tmp_path):
    k = _klasor(tmp_path)
    beklenen = by.manifest(k)
    assert by.farklar(beklenen, by.manifest(k)) == []
    (tmp_path / "model-00002.safetensors").write_bytes(b"c" * 20)          # aynı boyut, farklı içerik
    f = by.farklar(beklenen, by.manifest(k))
    assert len(f) == 1 and "model-00002.safetensors" in f[0] and "sha256" in f[0]
    (tmp_path / "config.json").unlink()
    f = by.farklar(beklenen, by.manifest(k, adlar=list(beklenen["dosyalar"])))
    assert any("config.json" in x and "eksik" in x for x in f)


def test_put_komutlari_her_dosya_icin_modal_volume_put_uretir(tmp_path):
    komutlar = by.put_komutlari(_klasor(tmp_path))
    assert len(komutlar) == 4
    assert komutlar[0][:4] == ["modal", "volume", "put", "hukuk-outputs"]
    assert komutlar[0][-1] == "/f016-vllm-pilot/bf16/config.json"
```

- [ ] **Step 2: Testin başarısız olduğunu doğrula**

Run: `source ~/code/global_venv/bin/activate && python -m pytest -q -p no:cacheprovider tests/test_bf16_yukle.py`
Expected: FAIL, `ModuleNotFoundError: No module named 'bf16_yukle'`.

- [ ] **Step 3: Minimal gerçeklemeyi yaz**

`scripts/olcum_uretim/bf16_yukle.py`:

```python
#!/usr/bin/env python3
"""Orijinal bf16 ağırlıkların Modal hacmine yüklenmesi (vLLM pilotu, spec 2026-10-15 bölüm 4).

  manifest  yerel dosyaların bayt ve sha256 tablosunu JSON'a yazar (konteyner hacimdeki dosyaları bununla karşılaştırır)
  put       `modal volume put` komutlarını BASAR. Çalıştırmak dışarı giden iştir; kullanıcı onayıyla elle yapılır.

Kullanım:
  python scripts/olcum_uretim/bf16_yukle.py manifest --dizin models/merged/tgta_v1 \\
      --cikti outputs/eval/f0/f016-vllm-pilot/bf16_manifest.json
  python scripts/olcum_uretim/bf16_yukle.py put --dizin models/merged/tgta_v1
"""
import argparse
import glob
import hashlib
import json
import os
import shlex

HACIM = "hukuk-outputs"
HACIM_YOLU = "/f016-vllm-pilot/bf16"
DESENLER = ("*.safetensors", "model.safetensors.index.json", "config.json", "generation_config.json",
            "tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt", "chat_template.jinja",
            "preprocessor_config.json", "video_preprocessor_config.json")


def dosyalar(dizin: str) -> list[str]:
    bulunan = sorted({os.path.basename(y) for d in DESENLER for y in glob.glob(os.path.join(dizin, d))})
    if not any(a.endswith(".safetensors") for a in bulunan):
        raise SystemExit(f"[bf16-yukle] 🚫 {dizin} içinde .safetensors dosyası yok")
    return bulunan


def _sha256(yol: str) -> str:
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for parca in iter(lambda: f.read(1 << 20), b""):
            h.update(parca)
    return h.hexdigest()


def manifest(dizin: str, adlar: list[str] | None = None) -> dict:
    sonuc = {}
    for ad in (adlar if adlar is not None else dosyalar(dizin)):
        yol = os.path.join(dizin, ad)
        if os.path.exists(yol):
            sonuc[ad] = {"bayt": os.path.getsize(yol), "sha256": _sha256(yol)}
    return {"dizin": os.path.basename(os.path.normpath(dizin)), "dosyalar": sonuc}


def farklar(beklenen: dict, eldeki: dict) -> list[str]:
    cikti = []
    for ad, b in beklenen["dosyalar"].items():
        e = eldeki["dosyalar"].get(ad)
        if e is None:
            cikti.append(f"{ad}: eksik")
        elif e["bayt"] != b["bayt"]:
            cikti.append(f"{ad}: bayt {e['bayt']} ≠ {b['bayt']}")
        elif e["sha256"] != b["sha256"]:
            cikti.append(f"{ad}: sha256 farklı")
    return cikti


def put_komutlari(dizin: str) -> list[list[str]]:
    return [["modal", "volume", "put", HACIM, os.path.join(dizin, ad), f"{HACIM_YOLU}/{ad}"]
            for ad in dosyalar(dizin)]


def main(argv=None):
    p = argparse.ArgumentParser(description="bf16 ağırlıkların Modal hacmine yüklenmesi")
    p.add_argument("komut", choices=("manifest", "put"))
    p.add_argument("--dizin", required=True)
    p.add_argument("--cikti", help="manifest için JSON yolu")
    a = p.parse_args(argv)
    if a.komut == "manifest":
        if not a.cikti:
            raise SystemExit("[bf16-yukle] 🚫 manifest için --cikti zorunlu")
        m = manifest(a.dizin)
        os.makedirs(os.path.dirname(a.cikti), exist_ok=True)
        with open(a.cikti, "w", encoding="utf-8") as f:
            json.dump(m, f, ensure_ascii=False, indent=2)
        print(f"[bf16-yukle] {len(m['dosyalar'])} dosya → {a.cikti}")
    else:
        for k in put_komutlari(a.dizin):
            print(shlex.join(k))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Testin geçtiğini doğrula**

Run: `source ~/code/global_venv/bin/activate && python -m pytest -q -p no:cacheprovider tests/test_bf16_yukle.py`
Expected: `5 passed`.

- [ ] **Step 5: Gerçek manifesti üret ($0, yerel)**

Run: `source ~/code/global_venv/bin/activate && python scripts/olcum_uretim/bf16_yukle.py manifest --dizin models/merged/tgta_v1 --cikti outputs/eval/f0/f016-vllm-pilot/bf16_manifest.json`
Expected: `[bf16-yukle] N dosya → outputs/eval/f0/f016-vllm-pilot/bf16_manifest.json` (N ≥ 4; iki `.safetensors` dahil). Manifestte `model-0000?-of-00002.safetensors` ikisi de bulunmalı: `python -c "import json;print(list(json.load(open('outputs/eval/f0/f016-vllm-pilot/bf16_manifest.json'))['dosyalar']))"`.

- [ ] **Step 6: Commit (kullanıcı isterse)**

```bash
git add scripts/olcum_uretim/bf16_yukle.py tests/test_bf16_yukle.py outputs/eval/f0/f016-vllm-pilot/bf16_manifest.json
git commit -m "feat: bf16 ağırlıkların Modal hacmine yüklenmesi için manifest ve komut üreticisi"
```

---

### Görev 3: Modal pilotunu iki ağırlık için yeniden düzenle

**Files:**
- Modify (baştan yazılır): `scripts/olcum_uretim/modal_pilot_vllm.py`
- Modify: `tests/test_modal_pilot_vllm.py`

**Interfaces:**
- Consumes: `bf16_yukle.manifest(dizin, adlar)` ve `bf16_yukle.farklar(beklenen, eldeki)` (Görev 2); `toplu_uret.py` CLI (`--server-url --server-model --data --donmus-baglam --tokenizer-dizini --es-zamanli --etiket --cikti-dizini [--ilk-n]`); `gguf_hf_cevir.py` CLI.
- Produces: Modal komutları
  - `modal run --detach scripts/olcum_uretim/modal_pilot_vllm.py::baslat --asama kontrol --agirlik bf16-orijinal`
  - `... --asama pilot --agirlik q4-acilmis` ve `... --agirlik bf16-orijinal`
  - Hacim çıktıları: `/f016-vllm-pilot/kontrol-<agirlik>/KUNYE.json` ve `/f016-vllm-pilot/A10/<agirlik>/{KUNYE.json,h1_tgta_v1_vllm_<agirlik>_t{1,2}_detail.jsonl}`.
  - Künye alanları: `kosular[].{etiket,sure_s,s_cevap,usd_cevap,gecerlilik}`, kontrol: `sekiz_soru.birebir_ayni_cevap`.

- [ ] **Step 1: Testleri güncelle (önce kırmızı)**

`tests/test_modal_pilot_vllm.py` içinde:
(a) `_sabit` yardımcısı değişmez. (b) Aşağıdaki iki testi dosyanın sonuna ekle:

```python
def test_vllm_pilotu_iki_agirlik_destekler_ve_batch_invariant_kullanmaz():
    """GDN katmanlarında batch-invariant desteklenmiyor (LMCache belgesi); pilot G4 ile belirlenimciliği ölçer,
    modu zorlamaz."""
    assert _sabit("AGIRLIKLAR") == ("q4-acilmis", "bf16-orijinal")
    assert "VLLM_BATCH_INVARIANT" not in _kaynak()


def test_vllm_pilotu_bf16_klasorunu_manifestle_dogrular():
    k = _kaynak()
    assert "bf16_manifest.json" in k and "bf16_yukle" in k
    assert _sabit("ES_ZAMANLI") == 32
```

- [ ] **Step 2: Kırmızıyı doğrula**

Run: `source ~/code/global_venv/bin/activate && python -m pytest -q -p no:cacheprovider tests/test_modal_pilot_vllm.py`
Expected: iki yeni test FAIL (`StopIteration` ya da `AssertionError`).

- [ ] **Step 3: `modal_pilot_vllm.py` dosyasını baştan yaz**

Dosyanın tam yeni içeriği:

```python
"""F0.16 vLLM pilotu, Modal A10 — vLLM ile toplu üretim ölçümü, iki ağırlıkla (spec 2026-10-15).

Ağırlıklar:
  q4-acilmis    yayımlanmış Q4_K_M GGUF, konteynerde `gguf_hf_cevir.py` ile bf16 HF biçimine açılır (aynı sayılar)
  bf16-orijinal eğitimin sıkıştırılmamış çıktısı (`models/merged/tgta_v1`), dizüstünden hacme yüklenmiştir
vLLM'in GGUF eklentisi Qwen3.5'i tanımıyor (`Unknown gguf model_type: qwen3_5`, 2026-10-15); GGUF doğrudan okunmaz.
Her iki klasör de içerik sha256'sıyla yerelde doğrulanmış kayda bağlıdır (CEVIRI_KUNYE.json, bf16_manifest.json).

Aşamalar (her biri ayrı onayla):
  kontrol  vLLM açılıyor mu? Düşünce hangi alan adıyla geliyor? 8 soru tek tek ↔ aynı anda: hız, cevap eşitliği (G1, G4)
  pilot    80 soru, vLLM'de iki üretim koşusu (G1, G2 ve puanlama için cevaplar)

Konteynere hiçbir anahtar gitmez (secret bağlanmaz; GGUF deposu herkese açık).

Kullanım (repo kökünden; para harcar, kullanıcı onayıyla):
  modal run --detach scripts/olcum_uretim/modal_pilot_vllm.py::baslat --asama kontrol --agirlik bf16-orijinal
  modal run --detach scripts/olcum_uretim/modal_pilot_vllm.py::baslat --asama pilot --agirlik q4-acilmis
  modal volume get hukuk-outputs /f016-vllm-pilot/A10 outputs/eval/f0/f016-vllm-pilot/A10
"""
import hashlib
import os

import modal

VLLM_SURUMU = "0.30.0"        # PyPI 2026-09-22; varsayılan tekerlek CUDA 13.0
HF_HUB_SURUMU = "1.33.0"      # PyPI 2026-09-24; vLLM 0.30.0 >=1.31.0 ister
TABAN_IMAJ = "nvidia/cuda:13.0.1-devel-ubuntu24.04"
VERI = "data/eval/dev/core_hard.jsonl"
DONMUS = "data/eval/dev/baglam/h1-k10.json"
TOKENIZER = "models/merged/tgta_v1"
TOKENIZER_DOSYALARI = ("tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt",
                       "chat_template.jinja", "config.json")
CEVIRI_KUNYE_YEREL = "outputs/eval/f0/f016-vllm-pilot/cevirme/CEVIRI_KUNYE.json"
BF16_MANIFEST_YEREL = "outputs/eval/f0/f016-vllm-pilot/bf16_manifest.json"
AGIRLIKLAR = ("q4-acilmis", "bf16-orijinal")
CIKTI_KOK = "/outputs/f016-vllm-pilot"
SAATLIK_USD = {"A10": 1.10}   # modal.com/pricing, okundu 2026-10-15 (#82)
ES_ZAMANLI = 32               # aynı anda gönderilen istek; sunucuda --max-num-seqs ile aynı
PORT = 8000

app = modal.App("hakhukuk-olcum-pilot-vllm")
out_vol = modal.Volume.from_name("hukuk-outputs")

image = (
    modal.Image.from_registry(TABAN_IMAJ, add_python="3.12")
    .pip_install(f"vllm=={VLLM_SURUMU}", "openai==2.41.0", "pyyaml==6.0.3", f"huggingface_hub=={HF_HUB_SURUMU}",
                 "gguf>=0.17.0")
    .env({"PYTHONUNBUFFERED": "1"})
    .add_local_dir("scripts", remote_path="/root/scripts")
    .add_local_dir("hakhukuk", remote_path="/root/hakhukuk")
    .add_local_file(VERI, remote_path=f"/root/{VERI}")
    .add_local_file(DONMUS, remote_path=f"/root/{DONMUS}")
    .add_local_file(CEVIRI_KUNYE_YEREL, remote_path="/root/cevirme_kunye.json")
    .add_local_file(BF16_MANIFEST_YEREL, remote_path="/root/bf16_manifest.json")
)
for _dosya in TOKENIZER_DOSYALARI:
    image = image.add_local_file(f"{TOKENIZER}/{_dosya}", remote_path=f"/root/tok/{_dosya}")


def _sha256(yol: str) -> str:
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for parca in iter(lambda: f.read(1 << 20), b""):
            h.update(parca)
    return h.hexdigest()


def _paket_surumu(ad: str):
    from importlib import metadata
    try:
        return metadata.version(ad)
    except metadata.PackageNotFoundError:
        return None


def _hf_klasoru(gguf: str) -> str:
    """GGUF → HF klasörü (hacimde önbellekli). Her tensörün sha256'sı yerelde doğrulanmış çeviriyle aynı olmalı."""
    import json
    import subprocess
    import sys
    hedef = f"{CIKTI_KOK}/hf_q4km"
    kayit = f"{hedef}/CEVIRI_KUNYE.json"
    if not os.path.exists(kayit):
        subprocess.run([sys.executable, "/root/scripts/olcum_uretim/gguf_hf_cevir.py", "--gguf", gguf,
                        "--yapilandirma-dizini", "/root/tok", "--cikti", hedef], check=True)
        out_vol.commit()
    beklenen = {t["hf"]: t["sha256"] for t in json.load(open("/root/cevirme_kunye.json", encoding="utf-8"))["tensorler"]}
    elde = {t["hf"]: t["sha256"] for t in json.load(open(kayit, encoding="utf-8"))["tensorler"]}
    if elde != beklenen:
        farkli = sorted(k for k in beklenen if elde.get(k) != beklenen[k])[:5]
        raise RuntimeError(f"çeviri yerelde doğrulanmışla aynı değil: {len(elde)} ↔ {len(beklenen)} tensör, "
                           f"farklı ilk beşi {farkli}")
    return hedef


def _bf16_klasoru() -> str:
    """Hacimdeki orijinal bf16 klasörü; her dosyanın sha256'sı yerel manifestle aynı olmalı (bf16_yukle.py)."""
    import json
    import sys
    sys.path[:0] = ["/root/scripts/olcum_uretim"]
    import bf16_yukle
    hedef = f"{CIKTI_KOK}/bf16"
    beklenen = json.load(open("/root/bf16_manifest.json", encoding="utf-8"))
    fark = bf16_yukle.farklar(beklenen, bf16_yukle.manifest(hedef, adlar=list(beklenen["dosyalar"])))
    if fark:
        raise RuntimeError("hacimdeki bf16 yerel manifestle aynı değil: " + "; ".join(fark[:5]))
    return hedef


def _model_klasoru(agirlik: str):
    """→ (vLLM'in okuyacağı klasör, künyedeki model kaydı)."""
    if agirlik == "q4-acilmis":
        from hakhukuk.dagitim.indir import indir_model
        gguf = str(indir_model("/tmp/model"))
        return _hf_klasoru(gguf), {"gguf": os.path.basename(gguf), "gguf_sha256": _sha256(gguf)}
    if agirlik == "bf16-orijinal":
        return _bf16_klasoru(), {"bf16_manifest_sha256": _sha256("/root/bf16_manifest.json")}
    raise ValueError(f"bilinmeyen ağırlık: {agirlik} (beklenen {AGIRLIKLAR})")


def _sunucu_ac(model_dizini: str, gunluk_yolu: str):
    """vLLM sunucusunu açar, /health bekler → (süreç, koşan komut). Açılamazsa günlüğün sonuyla durur."""
    import subprocess
    import time
    import urllib.request
    komut = ["vllm", "serve", model_dizini, "--served-model-name", "local", "--dtype", "bfloat16",
             "--max-model-len", "8192", "--max-num-seqs", str(ES_ZAMANLI), "--reasoning-parser", "qwen3",
             "--seed", "3407", "--host", "127.0.0.1", "--port", str(PORT)]
    gunluk = open(gunluk_yolu, "w")
    srv = subprocess.Popen(komut, stdout=gunluk, stderr=subprocess.STDOUT)
    for _ in range(300):
        if srv.poll() is not None:
            raise RuntimeError(f"vllm öldü (kod {srv.returncode}): " + open(gunluk_yolu).read()[-3000:])
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/health", timeout=2).read()
            return srv, open(f"/proc/{srv.pid}/cmdline").read().split("\0")[:-1]
        except Exception:
            time.sleep(2)
    srv.terminate()
    raise RuntimeError("vllm 600 s'te açılmadı: " + open(gunluk_yolu).read()[-3000:])


def _sunucu_kapat(srv):
    srv.terminate()
    try:
        srv.wait(timeout=30)
    except Exception:
        srv.kill()


def _ortak_kunye(tip: str, hesap: str) -> dict:
    import subprocess
    kart = subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version,uuid,memory.total",
                           "--format=csv,noheader"], capture_output=True, text=True).stdout.strip()
    return {
        "platform": {"ad": "Modal", "hesap": hesap, "tip": tip, "saatlik_usd": SAATLIK_USD.get(tip),
                     "ortam": {k: v for k, v in os.environ.items() if k.startswith("MODAL_")
                               and not any(y in k for y in ("TOKEN", "SECRET", "KEY"))}},
        "nvidia_smi": kart,
        "yazilim": {"vllm": VLLM_SURUMU, "taban_imaj": TABAN_IMAJ,
                    "kurulan": {p: _paket_surumu(p) for p in ("vllm", "torch", "transformers", "huggingface_hub",
                                                              "openai", "gguf", "safetensors")}},
        "baglam": {"dosya": DONMUS, "sha256": _sha256(f"/root/{DONMUS}")},
    }


def _yaz(kunye: dict, dizin: str) -> None:
    import json
    with open(f"{dizin}/KUNYE.json", "w", encoding="utf-8") as f:
        json.dump(kunye, f, ensure_ascii=False, indent=2)
    out_vol.commit()
    print(json.dumps(kunye, ensure_ascii=False, indent=2), flush=True)


@app.function(image=image, gpu="A10", volumes={"/outputs": out_vol}, timeout=60 * 60, retries=0)
def kontrol(tip: str, hesap: str, agirlik: str) -> dict:
    """Aşama A: vLLM açılıyor mu · ham cevap alanları · 8 soru tek tek ↔ aynı anda (G1, G4)."""
    import json
    import subprocess
    import sys
    import urllib.request
    sys.path[:0] = ["/root/scripts/olcum_uretim", "/root/scripts/puanlama", "/root"]
    dizin = f"{CIKTI_KOK}/kontrol-{agirlik}"
    os.makedirs(dizin, exist_ok=True)
    kunye = {"is": "F0.16 vLLM pilotu · aşama A (kontrol)", "agirlik": agirlik, **_ortak_kunye(tip, hesap)}
    try:
        hf, kunye["model"] = _model_klasoru(agirlik)
        kunye["model_klasoru"] = hf
        srv, komut = _sunucu_ac(hf, f"{dizin}/vllm.log")
    except (RuntimeError, subprocess.CalledProcessError) as h:
        kunye["acildi"], kunye["hata_sonu"] = False, str(h)[-3000:]
        _yaz(kunye, dizin)
        return kunye
    kunye["acildi"], kunye["kosan_komut"] = True, komut
    try:
        ham = json.loads(urllib.request.urlopen(urllib.request.Request(
            f"http://127.0.0.1:{PORT}/v1/chat/completions",
            data=json.dumps({"model": "local", "max_tokens": 200, "temperature": 0, "seed": 3407,
                             "messages": [{"role": "user", "content": "2+2 kaçtır? Kısa düşün."}],
                             "chat_template_kwargs": {"enable_thinking": True}}).encode(),
            headers={"Content-Type": "application/json"}), timeout=120).read())
        kunye["ham_cevap_mesaj_alanlari"] = sorted(ham["choices"][0]["message"].keys())
        kunye["ham_cevap_ornek"] = ham["choices"][0]["message"]
        sonuc = {}
        for ad, es in (("tek_tek", 1), ("ayni_anda", 8)):
            r = subprocess.run([sys.executable, "/root/scripts/olcum_uretim/toplu_uret.py",
                                "--server-url", f"http://127.0.0.1:{PORT}/v1", "--server-model", "local",
                                "--data", f"/root/{VERI}", "--donmus-baglam", f"/root/{DONMUS}",
                                "--tokenizer-dizini", hf, "--es-zamanli", str(es), "--ilk-n", "8",
                                "--etiket", f"kontrol_{ad}", "--cikti-dizini", dizin],
                               capture_output=True, text=True)
            sonuc[ad] = {"cikis": r.returncode, "son_satirlar": (r.stdout + r.stderr).strip().splitlines()[-6:]}
        kunye["sekiz_soru"] = sonuc
        if all(s["cikis"] == 0 for s in sonuc.values()):
            a = [json.loads(l) for l in open(f"{dizin}/kontrol_tek_tek_detail.jsonl", encoding="utf-8")]
            b = [json.loads(l) for l in open(f"{dizin}/kontrol_ayni_anda_detail.jsonl", encoding="utf-8")]
            kunye["sekiz_soru"]["birebir_ayni_cevap"] = sum(x["cevap"] == y["cevap"] for x, y in zip(a, b))
    finally:
        _sunucu_kapat(srv)
    _yaz(kunye, dizin)
    return kunye


@app.function(image=image, gpu="A10", volumes={"/outputs": out_vol}, timeout=3 * 60 * 60, retries=0)
def pilot(tip: str, hesap: str, baglam_sha: str, agirlik: str) -> dict:
    """Aşama B: 80 soru, vLLM'de iki üretim koşusu (aynı sunucuda arka arkaya)."""
    import subprocess
    import sys
    import time
    sys.path[:0] = ["/root/scripts/olcum_uretim", "/root/scripts/puanlama", "/root"]
    from part_dosya import tamamlanmis_jsonl
    import olcum_karti as ok
    if _sha256(f"/root/{DONMUS}") != baglam_sha:
        raise SystemExit("[pilot-vllm] 🚫 dondurulmuş bağlam yerelde hesaplanan sha256'yla aynı değil")
    dizin = f"{CIKTI_KOK}/{tip}/{agirlik}"
    os.makedirs(dizin, exist_ok=True)
    hf, model_kaydi = _model_klasoru(agirlik)
    kunye = {"is": "F0.16 vLLM pilotu · aşama B", "agirlik": agirlik, **_ortak_kunye(tip, hesap),
             "model": model_kaydi, "model_klasoru": hf, "es_zamanli": ES_ZAMANLI, "rejim": ok.REJIM, "kosular": []}
    saatlik = SAATLIK_USD.get(tip)
    srv, kunye["kosan_komut"] = _sunucu_ac(hf, f"{dizin}/vllm.log")
    try:
        for t in (1, 2):
            etiket = f"h1_tgta_v1_vllm_{agirlik}_t{t}"
            t0 = time.time()
            r = subprocess.run([sys.executable, "/root/scripts/olcum_uretim/toplu_uret.py",
                                "--server-url", f"http://127.0.0.1:{PORT}/v1", "--server-model", "local",
                                "--data", f"/root/{VERI}", "--donmus-baglam", f"/root/{DONMUS}",
                                "--tokenizer-dizini", hf, "--es-zamanli", str(ES_ZAMANLI),
                                "--etiket", etiket, "--cikti-dizini", dizin])
            sure = time.time() - t0
            if r.returncode != 0:
                raise SystemExit(f"[pilot-vllm] 🚫 {etiket} üretimi başarısız (kod {r.returncode})")
            satirlar = tamamlanmis_jsonl(f"{dizin}/{etiket}_detail.jsonl")
            kunye["kosular"].append({"etiket": etiket, "sure_s": round(sure, 1), "s_cevap": round(sure / len(satirlar), 2),
                                     "usd_cevap": round(sure / len(satirlar) * saatlik / 3600, 5) if saatlik else None,
                                     "gecerlilik": ok.gecerlilik(satirlar)})
            out_vol.commit()
    finally:
        _sunucu_kapat(srv)
    _yaz(kunye, dizin)
    return kunye


@app.local_entrypoint()
def baslat(asama: str = "", agirlik: str = "", tip: str = "A10"):
    if asama not in ("kontrol", "pilot"):
        raise SystemExit("[pilot-vllm] 🚫 --asama kontrol|pilot zorunlu")
    if agirlik not in AGIRLIKLAR:
        raise SystemExit(f"[pilot-vllm] 🚫 --agirlik {'|'.join(AGIRLIKLAR)} zorunlu")
    import sys
    sys.path.insert(0, "scripts/egitim")
    from modal_train import _baslatan_hesap   # ADR-0101 m.4: hesap profilden, elle yazılmaz
    hesap = _baslatan_hesap()
    if asama == "kontrol":
        c = kontrol.with_options(gpu=tip).spawn(tip, hesap, agirlik)
    else:
        c = pilot.with_options(gpu=tip).spawn(tip, hesap, _sha256(DONMUS), agirlik)
    print(f"[pilot-vllm] SPAWNED ✓ aşama={asama} ağırlık={agirlik} tip={tip} hesap={hesap} · {c.object_id}\n  bitince: "
          f"modal volume get hukuk-outputs /f016-vllm-pilot/<alt klasör> outputs/eval/f0/f016-vllm-pilot/<alt klasör>",
          flush=True)
```

> *Sapma (2026-10-16, kullanıcı kararı "Düzelt"): inceleme `pilot`'un hata verince künye yazmadığını buldu; `pilot` `try/except/finally` ile sarıldı, künye `finally` içinde yazılır (`acildi`, `hata_sonu`, o ana kadarki `kosular`). Commit `7f885e5`, test `test_pilot_hata_verse_de_kunye_yazar`.*

- [ ] **Step 4: Testlerin yeşil olduğunu ve Modal dosyasının yüklendiğini doğrula**

Run:
```bash
source ~/code/global_venv/bin/activate && python -m pytest -q -p no:cacheprovider tests/test_modal_pilot_vllm.py tests/test_bf16_yukle.py
python - <<'EOF'
import importlib.util
spec = importlib.util.spec_from_file_location("m", "scripts/olcum_uretim/modal_pilot_vllm.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
print(sorted(m.app.registered_functions), sorted(m.app.registered_entrypoints))
EOF
```
Expected: testler geçer; ikinci komut `['kontrol', 'pilot'] ['baslat']` basar. (Önkoşul: Görev 2 Step 5'teki `bf16_manifest.json` var; yoksa `FileNotFoundError`.)

- [ ] **Step 5: Hızlı takımı çalıştır**

Run: `source ~/code/global_venv/bin/activate && python -m pytest -q -p no:cacheprovider -m "not slow" 2>&1 | grep -E "passed|failed"`
Expected: `0 failed`.

- [ ] **Step 6: Commit (kullanıcı isterse)**

```bash
git add scripts/olcum_uretim/modal_pilot_vllm.py tests/test_modal_pilot_vllm.py
git commit -m "feat: vLLM pilotu iki ağırlık (Q4'ten açılmış, orijinal bf16) ve batch-invariant'sız akış"
```

---

### Görev 4: Kapı değerlendirmesi, özet betiği ve puanlama betiği

**Files:**
- Create: `scripts/olcum_uretim/vllm_kapilari.py`
- Create: `tests/test_vllm_kapilari.py`
- Create: `scripts/olcum_uretim/vllm_ozetle.py`
- Create: `tests/test_vllm_ozetle.py`
- Create: `outputs/eval/f0/f016-vllm-pilot/kos.sh`

**Interfaces:**
- Produces:
  - `vllm_kapilari.AGIRLIKLAR = ("q4-acilmis", "bf16-orijinal")`
  - `vllm_kapilari.degerlendir(girdi: dict) -> dict` — `girdi` biçimi:
    ```
    {"q4_acilmis": {"kosular": [{"sure_s": float, "gecerlilik": {"n","kesik_orani","dusunen",...}}, ...],
                    "kutle_ort": float, "iki_toplu_kosu_ayni": int},
     "bf16_orijinal": {aynı biçim},
     "referans_kutle_ort": float,
     "sekiz_soru": {"ayni": int, "n": int}}
    ```
    çıktı: `{"g1","g2","g3","g4","g5": {...,"gecti": bool}, "ilerle": bool}`; `g4["dal"]` ∈ {"bayt","puan"}.
  - `vllm_ozetle.girdi_olustur(kok, referans_ozet) -> dict` (yukarıdaki `girdi`), `vllm_ozetle.main(argv)` → `OZET.json` yazar, `ilerle` ise çıkış 0, değilse 1.

- [ ] **Step 1: `vllm_kapilari` için başarısız testleri yaz**

`tests/test_vllm_kapilari.py`:

```python
"""vLLM pilotunun kapıları (spec 2026-10-15 bölüm 5): ölçütler pilot sonucunu görmeden kilitlidir."""
import pytest

import vllm_kapilari as vk  # noqa: E402


def _g(n=80, kesik=0, dusunen=80):
    return {"n": n, "kesik_orani": kesik / n if n else None, "dusunen": dusunen}


def _agirlik(sure=150.0, kutle=0.7540, g=None):
    return {"kosular": [{"sure_s": sure, "gecerlilik": g or _g()}, {"sure_s": sure, "gecerlilik": g or _g()}],
            "kutle_ort": kutle, "iki_toplu_kosu_ayni": 80}


def _girdi(**d):
    base = {"q4_acilmis": _agirlik(), "bf16_orijinal": _agirlik(sure=160.0, kutle=0.7700),
            "referans_kutle_ort": 0.7515, "sekiz_soru": {"ayni": 8, "n": 8}}
    base.update(d)
    return base


def test_esikler_spec_ile_ayni():
    assert vk.LLAMA_SURE_S == 640.6 and vk.ESIK_HIZ_ORAN == pytest.approx(1 / 3)
    assert vk.ESIK_KUTLE_PUAN == 0.6 and vk.KESIK_ESIGI == 0.05 and vk.N_KALEM == 80


def test_hepsi_gecerse_ilerle():
    s = vk.degerlendir(_girdi())
    assert s["ilerle"] is True and s["g3"]["fark_puan"] == pytest.approx(0.25)


@pytest.mark.parametrize("sure,gecer", [(213.0, True), (214.0, False)])
def test_hiz_kapisi_llama_cpp_suresinin_ucte_birinde_kesilir(sure, gecer):
    s = vk.degerlendir(_girdi(q4_acilmis=_agirlik(sure=sure)))
    assert s["g2"]["gecti"] is gecer and s["ilerle"] is gecer


def test_motor_etkisi_0_6_puani_asarsa_ilerlemez():
    s = vk.degerlendir(_girdi(q4_acilmis=_agirlik(kutle=0.7580)))      # fark 0,65 puan
    assert s["g3"]["gecti"] is False and s["ilerle"] is False


def test_motor_etkisi_tam_0_6_puanda_gecer():
    assert vk.degerlendir(_girdi(q4_acilmis=_agirlik(kutle=0.7575)))["g3"]["gecti"] is True


def test_kesik_orani_yuzde_besi_asarsa_g1_duser():
    s = vk.degerlendir(_girdi(bf16_orijinal=_agirlik(g=_g(kesik=5))))   # 5/80 = %6,25
    assert s["g1"]["gecti"] is False and s["ilerle"] is False


def test_dusunce_kanali_hic_kullanilmadiysa_g1_duser():
    assert vk.degerlendir(_girdi(q4_acilmis=_agirlik(g=_g(dusunen=0))))["g1"]["gecti"] is False


@pytest.mark.parametrize("ayni,dal", [(8, "bayt"), (7, "puan"), (0, "puan")])
def test_belirlenimcilik_dali_bayt_ya_da_puan_ama_ilerlemeyi_etkilemez(ayni, dal):
    s = vk.degerlendir(_girdi(sekiz_soru={"ayni": ayni, "n": 8}))
    assert s["g4"]["dal"] == dal and s["ilerle"] is True


def test_q4_etkisi_yalniz_raporlanir_kapi_degildir():
    s = vk.degerlendir(_girdi(bf16_orijinal=_agirlik(kutle=0.5000)))
    assert s["g5"]["fark_puan"] == pytest.approx(25.4) and s["ilerle"] is True
```

- [ ] **Step 2: Kırmızıyı doğrula**

Run: `source ~/code/global_venv/bin/activate && python -m pytest -q -p no:cacheprovider tests/test_vllm_kapilari.py`
Expected: FAIL, `ModuleNotFoundError: No module named 'vllm_kapilari'`.

- [ ] **Step 3: `vllm_kapilari.py` yaz**

```python
#!/usr/bin/env python3
"""vLLM pilotunun kapıları G1-G5 (spec 2026-10-15 bölüm 5). Saf fonksiyonlar; dosya okumaz.

Ölçütler pilot sonucunu görmeden kilitlidir; değiştirmek ayrı ADR ister.
  G1 açılıyor     iki ağırlığın bütün koşularında n=80, kesik <= %5, düşünce kanalı kullanılmış
  G2 hız          koşu başına süre <= llama.cpp süresi ÷ 3
  G3 motor etkisi |kütle(Q4'ten açılmış, vLLM) − kütle(referans, llama.cpp)| <= 0,6 puan
  G4 belirlenimcilik  8 soru tek tek ↔ toplu aynı mı (bilgi; dal: bayt | puan)
  G5 Q4 etkisi    |kütle(bf16 orijinal) − kütle(Q4'ten açılmış)| (yalnız rapor)
"""
AGIRLIKLAR = ("q4-acilmis", "bf16-orijinal")
N_KALEM = 80
LLAMA_SURE_S = 640.6          # A10 referansı: outputs/eval/f0/f016-pilot/A10/m1/KUNYE.json, 1. tekrar
ESIK_HIZ_ORAN = 1 / 3
ESIK_KUTLE_PUAN = 0.6
KESIK_ESIGI = 0.05            # olcum_karti.KESIK_ESIGI ile aynı


def _gecerli(g: dict) -> bool:
    return (g["n"] == N_KALEM and g["kesik_orani"] is not None and g["kesik_orani"] <= KESIK_ESIGI
            and g["dusunen"] > 0)


def degerlendir(girdi: dict) -> dict:
    ag = {"q4_acilmis": girdi["q4_acilmis"], "bf16_orijinal": girdi["bf16_orijinal"]}
    sonuc = {"g1": {"esik": f"n={N_KALEM}, kesik<={KESIK_ESIGI}, dusunen>0",
                    "gecti": all(_gecerli(k["gecerlilik"]) for a in ag.values() for k in a["kosular"])}}
    sureler = {ad: sum(k["sure_s"] for k in a["kosular"]) / len(a["kosular"]) for ad, a in ag.items()}
    limit = LLAMA_SURE_S * ESIK_HIZ_ORAN
    sonuc["g2"] = {"ortalama_sure_s": sureler, "esik_s": limit, "gecti": all(s <= limit for s in sureler.values())}
    fark3 = round(abs(ag["q4_acilmis"]["kutle_ort"] - girdi["referans_kutle_ort"]) * 100, 6)
    sonuc["g3"] = {"fark_puan": fark3, "esik_puan": ESIK_KUTLE_PUAN, "gecti": fark3 <= ESIK_KUTLE_PUAN}
    s8 = girdi["sekiz_soru"]
    sonuc["g4"] = {"ayni": s8["ayni"], "n": s8["n"], "dal": "bayt" if s8["ayni"] == s8["n"] else "puan",
                   "gecti": True}
    sonuc["g5"] = {"fark_puan": round(abs(ag["bf16_orijinal"]["kutle_ort"] - ag["q4_acilmis"]["kutle_ort"]) * 100, 6),
                   "gecti": True}
    sonuc["ilerle"] = sonuc["g1"]["gecti"] and sonuc["g2"]["gecti"] and sonuc["g3"]["gecti"]
    return sonuc
```

- [ ] **Step 4: Yeşili doğrula**

Run: `source ~/code/global_venv/bin/activate && python -m pytest -q -p no:cacheprovider tests/test_vllm_kapilari.py`
Expected: `12 passed` (parametreli testler dahil).

- [ ] **Step 5: `vllm_ozetle` için başarısız testi yaz**

`tests/test_vllm_ozetle.py`:

```python
"""vLLM pilotunun dosyalardan kapı girdisi toplayan yapıştırıcısı (ağ yok, GPU yok)."""
import json
import os

import vllm_kapilari as vk
import vllm_ozetle as vo  # noqa: E402

SHA = "a" * 64


def _yaz(yol, nesne):
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(nesne, f)


def _satirlar(yol, n=80, degisen=()):
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    with open(yol, "w", encoding="utf-8") as f:
        for i in range(n):
            f.write(json.dumps({"id": i, "cevap": f"c{i}" + ("x" if i in degisen else ""),
                                "harness": {"donmus_baglam": SHA}}) + "\n")


def _kur(tmp_path):
    kok = str(tmp_path / "pilot")
    g = {"n": 80, "kesik_orani": 0.0, "dusunen": 80}
    for ad, kutle, degisen in (("q4-acilmis", 0.7540, ()), ("bf16-orijinal", 0.7700, (3,))):
        _yaz(f"{kok}/A10/{ad}/KUNYE.json", {"kosular": [{"sure_s": 150.0, "gecerlilik": g},
                                                         {"sure_s": 152.0, "gecerlilik": g}]})
        _satirlar(f"{kok}/A10/{ad}/h1_tgta_v1_vllm_{ad}_t1_detail.jsonl")
        _satirlar(f"{kok}/A10/{ad}/h1_tgta_v1_vllm_{ad}_t2_detail.jsonl", degisen=degisen)
        for r in (1, 2, 3):
            _yaz(f"{kok}/puanlama/harness_tablo_{ad}_t{r}.json", {"kutle_ekseni": {"kutle_tum": kutle}})
    _yaz(f"{kok}/kontrol-bf16-orijinal/KUNYE.json", {"sekiz_soru": {"birebir_ayni_cevap": 8}})
    ref = str(tmp_path / "f06" / "OZET.json")
    _yaz(ref, {"modlar": {"ds-acik": {"kutle_ort": 0.7515}}})
    return kok, ref


def test_girdi_dosyalardan_toplanir_ve_kapilar_degerlendirilir(tmp_path):
    kok, ref = _kur(tmp_path)
    g = vo.girdi_olustur(kok, ref)
    assert g["referans_kutle_ort"] == 0.7515 and g["sekiz_soru"] == {"ayni": 8, "n": 8}
    assert g["q4_acilmis"]["kutle_ort"] == 0.7540 and g["q4_acilmis"]["iki_toplu_kosu_ayni"] == 80
    assert g["bf16_orijinal"]["iki_toplu_kosu_ayni"] == 79            # id 3'ün cevabı iki koşuda farklı
    assert vk.degerlendir(g)["ilerle"] is True


def test_main_ozet_json_yazar_ve_cikis_kodu_ilerlemeyi_yansitir(tmp_path):
    kok, ref = _kur(tmp_path)
    assert vo.main(["--kok", kok, "--referans-ozet", ref]) == 0
    assert json.load(open(f"{kok}/OZET.json", encoding="utf-8"))["ilerle"] is True
    _yaz(f"{kok}/puanlama/harness_tablo_q4-acilmis_t1.json", {"kutle_ekseni": {"kutle_tum": 0.60}})
    assert vo.main(["--kok", kok, "--referans-ozet", ref]) == 1
```

İkinci testteki son beklenti: q4 kütle ortalaması (0.60+0.7540+0.7540)/3 = 0.7027, fark 4,9 puan → `ilerle` False → çıkış 1.

- [ ] **Step 6: Kırmızıyı doğrula**

Run: `source ~/code/global_venv/bin/activate && python -m pytest -q -p no:cacheprovider tests/test_vllm_ozetle.py`
Expected: FAIL, `ModuleNotFoundError: No module named 'vllm_ozetle'`.

- [ ] **Step 7: `vllm_ozetle.py` yaz**

```python
#!/usr/bin/env python3
"""vLLM pilotu: dosyalardan kapı girdisini toplar, G1-G5'i değerlendirir, OZET.json yazar.

Beklenen dosya düzeni (`modal volume get` ve `kos.sh` sonrası):
  <kok>/A10/<ağırlık>/KUNYE.json, h1_tgta_v1_vllm_<ağırlık>_t{1,2}_detail.jsonl
  <kok>/kontrol-bf16-orijinal/KUNYE.json
  <kok>/puanlama/harness_tablo_<ağırlık>_t{1,2,3}.json
  referans: outputs/eval/f0/f06-hakem-gecisi/OZET.json (DeepSeek-açık, A10 referansı, 5 tekrar)
"""
# ── scripts/ yol köprüsü (T5, 2026-09-07) ────────────────────────────────────
# Kardeş modüller alt klasörlere bölündükten SONRA da bulunsun diye scripts/ kökü, tüm
# alt klasörleri ve repo kökü sys.path'e girer. Uzantısız `import X` bu köprü olmadan
# taşımada SESSİZCE kırılır: ImportError çalışma zamanında, bazen GPU koşusunun ortasında.
# ⚠️ 26 dosyada BİREBİR aynı; değiştirirsen hepsinde değiştir (grep: "yol köprüsü").
import os, sys
_K = os.path.dirname(os.path.abspath(__file__))
_K = _K if os.path.basename(_K) == "scripts" else os.path.dirname(_K)
sys.path[:0] = [_K, *(os.path.join(_K, _d) for _d in sorted(os.listdir(_K))
                      if os.path.isdir(os.path.join(_K, _d)) and _d[0] not in "_."),
                os.path.dirname(_K)]
# ─────────────────────────────────────────────────────────────────────────────
import argparse  # noqa: E402
import json  # noqa: E402

import makine_kapisi  # noqa: E402
import vllm_kapilari as vk  # noqa: E402
from part_dosya import tamamlanmis_jsonl  # noqa: E402

KOK = "outputs/eval/f0/f016-vllm-pilot"
REFERANS_OZET = "outputs/eval/f0/f06-hakem-gecisi/OZET.json"
HAKEM_TEKRARI = 3


def _json(yol: str):
    with open(yol, encoding="utf-8") as f:
        return json.load(f)


def _kutle_ort(kok: str, ad: str) -> float:
    d = [_json(f"{kok}/puanlama/harness_tablo_{ad}_t{r}.json")["kutle_ekseni"]["kutle_tum"]
         for r in range(1, HAKEM_TEKRARI + 1)]
    return sum(d) / len(d)


def girdi_olustur(kok: str = KOK, referans_ozet: str = REFERANS_OZET) -> dict:
    girdi = {}
    for ad in vk.AGIRLIKLAR:
        kunye = _json(f"{kok}/A10/{ad}/KUNYE.json")
        t1 = tamamlanmis_jsonl(f"{kok}/A10/{ad}/h1_tgta_v1_vllm_{ad}_t1_detail.jsonl")
        t2 = tamamlanmis_jsonl(f"{kok}/A10/{ad}/h1_tgta_v1_vllm_{ad}_t2_detail.jsonl")
        girdi[ad.replace("-", "_")] = {
            "kosular": [{"sure_s": k["sure_s"], "gecerlilik": k["gecerlilik"]} for k in kunye["kosular"]],
            "kutle_ort": _kutle_ort(kok, ad),
            "iki_toplu_kosu_ayni": makine_kapisi.karsilastir(t1, t2)["ayni"]}
    girdi["referans_kutle_ort"] = _json(referans_ozet)["modlar"]["ds-acik"]["kutle_ort"]
    girdi["sekiz_soru"] = {"ayni": _json(f"{kok}/kontrol-bf16-orijinal/KUNYE.json")["sekiz_soru"]["birebir_ayni_cevap"],
                           "n": 8}
    return girdi


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="vLLM pilotu kapı özeti")
    p.add_argument("--kok", default=KOK)
    p.add_argument("--referans-ozet", default=REFERANS_OZET)
    a = p.parse_args(argv)
    girdi = girdi_olustur(a.kok, a.referans_ozet)
    sonuc = vk.degerlendir(girdi)
    with open(f"{a.kok}/OZET.json", "w", encoding="utf-8") as f:
        json.dump({"girdi": girdi, "kapilar": sonuc}, f, ensure_ascii=False, indent=2)
    print(json.dumps(sonuc, ensure_ascii=False, indent=2))
    return 0 if sonuc["ilerle"] else 1


if __name__ == "__main__":
    sys.exit(main())
```

Not: `vllm_kapilari.degerlendir` `OZET.json`'a yalnız `kapilar` olarak yazılır; testteki `["ilerle"]` beklentisini `OZET.json` içinde `["kapilar"]["ilerle"]` yapacak şekilde test düzeltilir. Step 8'de test bu biçime göre güncellenir.

- [ ] **Step 8: Testi `OZET.json` biçimine göre düzelt ve yeşili doğrula**

`tests/test_vllm_ozetle.py` içinde `json.load(open(f"{kok}/OZET.json", encoding="utf-8"))["ilerle"]` ifadesini `json.load(open(f"{kok}/OZET.json", encoding="utf-8"))["kapilar"]["ilerle"]` yap.

Run: `source ~/code/global_venv/bin/activate && python -m pytest -q -p no:cacheprovider tests/test_vllm_ozetle.py tests/test_vllm_kapilari.py`
Expected: `14 passed`.

- [ ] **Step 9: Puanlama betiğini yaz**

`outputs/eval/f0/f016-vllm-pilot/kos.sh`:

```bash
#!/usr/bin/env bash
# F0.16 vLLM pilotu puanlaması (kullanıcı onayıyla): iki ağırlık x 3 hakem tekrarı, DeepSeek V4.1 Flash, hakemin düşünmesi açık.
# Altı koşu eş zamanlı (~2 saat, tahmini ~$1,6). Girdi: her ağırlığın 1. üretim koşusu.
set -uo pipefail
cd "$(dirname "$0")/../../../.."
source ~/code/global_venv/bin/activate
set -a; . ./.env; set +a
export OPENAI_API_KEY="$OPENROUTER_API_KEY" LLM_GATEWAY=openrouter
K=outputs/eval/f0/f016-vllm-pilot
O=$K/puanlama
mkdir -p "$O"
for a in q4-acilmis bf16-orijinal; do
  D=$K/A10/$a/h1_tgta_v1_vllm_${a}_t1_detail.jsonl
  for r in 1 2 3; do
    python scripts/puanlama/groundedness.py --details "$D" --mode data --label "vllm-${a}_t$r" --out-dir "$O" \
      --judge-model deepseek-v4.1-flash --hakem-saglayici deepinfra/fp8 --hakem-dusunme acik \
      > "$O/log_vllm-${a}_t$r.txt" 2>&1 &
  done
done
wait
for a in q4-acilmis bf16-orijinal; do
  D=$K/A10/$a/h1_tgta_v1_vllm_${a}_t1_detail.jsonl
  for r in 1 2 3; do
    python scripts/puanlama/harness_tablo.py --details "$D" --gnd "$O/gnd_vllm-${a}_t$r.jsonl" \
      --kume data/eval/dev/core_hard.jsonl --out "$O/harness_tablo_${a}_t$r.json" \
      > "$O/log_tablo_${a}_t$r.txt" 2>&1
  done
done
for f in "$O"/log_vllm-*.txt; do echo "== $f"; tail -2 "$f"; done
```

Run: `chmod +x outputs/eval/f0/f016-vllm-pilot/kos.sh && bash -n outputs/eval/f0/f016-vllm-pilot/kos.sh && echo sözdizimi-tamam`
Expected: `sözdizimi-tamam`.

- [ ] **Step 10: Hızlı takım ve commit (kullanıcı isterse)**

Run: `source ~/code/global_venv/bin/activate && python -m pytest -q -p no:cacheprovider -m "not slow" 2>&1 | grep -E "passed|failed"` → `0 failed`.

```bash
git add scripts/olcum_uretim/vllm_kapilari.py scripts/olcum_uretim/vllm_ozetle.py tests/test_vllm_kapilari.py tests/test_vllm_ozetle.py outputs/eval/f0/f016-vllm-pilot/kos.sh
git commit -m "feat: vLLM pilotu kapıları (G1-G5), özet betiği ve puanlama betiği"
```

---

### Görev 5: Pilotu yürüt (ana oturum, para ve yükleme, her adım ayrı onay)

**Files:**
- Create (indirilir): `outputs/eval/f0/f016-vllm-pilot/A10/**`, `outputs/eval/f0/f016-vllm-pilot/kontrol-bf16-orijinal/**`
- Create (üretilir): `outputs/eval/f0/f016-vllm-pilot/puanlama/**`, `outputs/eval/f0/f016-vllm-pilot/OZET.json`, `outputs/eval/f0/f016-vllm-pilot/KUNYE.json`

**Interfaces:**
- Consumes: Görev 2-4'ün çıktıları.
- Produces: `OZET.json` (`kapilar.ilerle`, `kapilar.g4.dal`) — Görev 6, 7 ve 8 bu dosyaya bakar.

Her alt adım **ayrı `AskUserQuestion`** ile onaylanır; onay metni tahmini maliyeti ve dışarı giden veriyi içerir. Hacimden **yalnız** `A10/` ve `kontrol-bf16-orijinal/` indirilir (hacimde 8-9 GB'lık `hf_q4km/` ve `bf16/` klasörleri var, indirilmez).

- [ ] **Step 1: bf16'yı Modal hacmine yükle (dışarı giden, ~9 GB, $0)**

Onay sor: "Orijinal bf16 ağırlıkları (`models/merged/tgta_v1`, ~9 GB) Modal hacmi `hukuk-outputs`'a yüklensin mi? Anahtar gitmez; yalnız `rfetha` hesabının hacmi."

Run (onaydan sonra, komutları basıp çalıştır):
```bash
source ~/code/global_venv/bin/activate
python scripts/olcum_uretim/bf16_yukle.py put --dizin models/merged/tgta_v1 > /tmp/bf16_put.sh
bash /tmp/bf16_put.sh
modal volume ls hukuk-outputs /f016-vllm-pilot/bf16
```
Expected: `ls` çıktısı manifestteki dosyaların hepsini listeler (iki `.safetensors` dahil). Bütünlük kontrolü pilot açılışında konteynerde yapılır (`_bf16_klasoru`).

- [ ] **Step 2: Aşama A, bf16-orijinal (~$0,2-0,4)**

Onay sor. Run:
```bash
source ~/code/global_venv/bin/activate
modal run --detach scripts/olcum_uretim/modal_pilot_vllm.py::baslat --asama kontrol --agirlik bf16-orijinal 2>&1 | tail -5
```
Expected: `SPAWNED ✓` satırı. `Monitor` ile hacimde `/f016-vllm-pilot/kontrol-bf16-orijinal/KUNYE.json` belirmesini bekle:
```bash
until modal volume ls hukuk-outputs /f016-vllm-pilot/kontrol-bf16-orijinal 2>/dev/null | grep -q KUNYE.json; do sleep 20; done
```
İndir ve oku:
```bash
modal volume get hukuk-outputs /f016-vllm-pilot/kontrol-bf16-orijinal outputs/eval/f0/f016-vllm-pilot/
python3 -c "import json;k=json.load(open('outputs/eval/f0/f016-vllm-pilot/kontrol-bf16-orijinal/KUNYE.json'));print({x:k.get(x) for x in ('acildi','ham_cevap_mesaj_alanlari')});print(k.get('sekiz_soru',{}).get('birebir_ayni_cevap'));print((k.get('hata_sonu') or '')[-1500:])"
```
Karar: `acildi` False ise (G1 fiilen düştü): hata günlüğünden nedeni çıkar. Olası ve izinli düzeltmeler: `vllm serve` bayrakları (örn. görüntü girdisini kapatan bayrak) ya da metin-yalnız yapılandırma. Düzeltme `modal_pilot_vllm.py::_sunucu_ac`'a işlenir (test + kod), yeniden denemeden önce yeni onay alınır, ve her deneme kronolojide not edilir. İki düzeltmeden sonra da açılmazsa pilot G1 ile biter: Görev 6-7 atlanır, Görev 8 "vLLM ölçümde kullanılmadı: neden" kaydına dönüşür.
`sekiz_soru.birebir_ayni_cevap` değerini not et (G4 girdisi).

- [ ] **Step 3: Aşama B, iki ağırlık (~$0,5-1 toplam)**

Onay sor. Run (iki ayrı konteyner, eş zamanlı):
```bash
source ~/code/global_venv/bin/activate
modal run --detach scripts/olcum_uretim/modal_pilot_vllm.py::baslat --asama pilot --agirlik q4-acilmis 2>&1 | tail -3
modal run --detach scripts/olcum_uretim/modal_pilot_vllm.py::baslat --asama pilot --agirlik bf16-orijinal 2>&1 | tail -3
```
Bekle:
```bash
until modal volume ls hukuk-outputs /f016-vllm-pilot/A10/q4-acilmis 2>/dev/null | grep -q KUNYE.json && modal volume ls hukuk-outputs /f016-vllm-pilot/A10/bf16-orijinal 2>/dev/null | grep -q KUNYE.json; do sleep 30; done
modal volume get hukuk-outputs /f016-vllm-pilot/A10 outputs/eval/f0/f016-vllm-pilot/
find outputs/eval/f0/f016-vllm-pilot/A10 -name 'KUNYE.json'
```
Expected: iki `KUNYE.json` ve her ağırlıkta iki `_detail.jsonl`. `python3 -c` ile iki künyenin `kosular[].gecerlilik` ve `sure_s` alanlarını yazdır.

- [ ] **Step 4: Puanla (hakem harcaması ~$1,6, ~2 saat)**

Onay sor: "6 hakem koşusu, DeepSeek V4.1 Flash (açık düşünme), OpenRouter, tahmini $1,6 ve ~2 saat; `.env` anahtarı yalnız yerelde kullanılır."
Run:
```bash
bash outputs/eval/f0/f016-vllm-pilot/kos.sh
```
(arka planda çalıştır, bitince bildirim bekle). Expected: `puanlama/` altında altı `gnd_vllm-*_t?_summary.json` ve altı `harness_tablo_*.json`; hiçbir günlükte `Traceback` yok:
```bash
grep -l Traceback outputs/eval/f0/f016-vllm-pilot/puanlama/log_*.txt || echo temiz
```
Expected: `temiz`.

- [ ] **Step 5: Kapıları değerlendir**

Run:
```bash
source ~/code/global_venv/bin/activate
python scripts/olcum_uretim/vllm_ozetle.py; echo "çıkış: $?"
```
Expected: `kapilar` JSON'u ve `OZET.json`; çıkış 0 (G1-G3 geçti) ya da 1 (en az biri düştü). Sonucu kullanıcıya G1-G5 tablosuyla sun.

- [ ] **Step 6: Gerçek faturayı oku**

OpenRouter: `GET /api/v1/key` (bugünkü `usage_daily`; F0.6'daki yöntemle, anahtar basılmaz). Modal: kullanıcıdan panel değerini iste. Tahmin ($2-4) ile karşılaştır; $5 aşıldıysa kullanıcıya bildir.

- [ ] **Step 7: Künye yaz**

`outputs/eval/f0/f016-vllm-pilot/KUNYE.json`: girdi dosyalarının sha256'ları (bf16 manifesti, CEVIRI_KUNYE, bağlam), vLLM sürümü ve kurulan paket sürümleri (Modal künyelerinden), hakem kimliği (`deepseek/deepseek-v4.1-flash-20260910`, `deepinfra/fp8`, açık), onay anları, gerçek fatura, `OZET.json` yolu. Şablon `outputs/eval/f0/f06-hakem-gecisi/KUNYE.json`'dan alınır.

- [ ] **Step 8: Karar noktası**

`AskUserQuestion`: "Pilot sonucu: G1 <geçti/düştü>, G2 <…>, G3 <…>, G4 dalı <bayt/puan>. Ne yapalım?" Seçenekler: (1) Görev 6 ve 7'ye geç (yalnız `ilerle` ise); (2) pilot düştü: ölçüm llama.cpp'de kalır, Görev 8'e kayıt olarak geç; (3) başka (not).

- [ ] **Step 9: Commit (kullanıcı isterse)**

```bash
git add outputs/eval/f0/f016-vllm-pilot
git commit -m "data: vLLM pilotu sonuçları ve kapı değerlendirmesi"
```

---

### Görev 6: Ölçüm hattı (yalnız G1-G3 geçtiyse)

**Files:**
- Create: `scripts/olcum_uretim/makine_kapisi_puan.py`
- Create: `tests/test_makine_kapisi_puan.py`

**Interfaces:**
- Produces: `makine_kapisi_puan.puan_kapisi(referans_kutle_ort: float, aday_kutle_ort: float, esik_puan: float = 0.6) -> dict` → `{"fark_puan","esik_puan","gecti"}`; CLI çıkış 0 geçti, 1 düştü. G4 dalı "puan" ise vLLM hattında yeni makine bu kapıyla, "bayt" ise `makine_kapisi.py` ile geçer.
- Sorumluluk notu: `gen_eval_grounded.py` değişmez; vLLM hattının resmî toplu üretim yolu `toplu_uret.py`'dir (aynı kayıt biçimi, spec sapması Görev 1'de kaydedildi).

- [ ] **Step 1: Başarısız testi yaz**

`tests/test_makine_kapisi_puan.py`:

```python
"""Makine geçiş kapısının puan düzeyi dalı (vLLM hattı, G4 'puan' dalı): bayt eşitliği aranmaz, kütle farkı bakılır."""
import pytest

import makine_kapisi_puan as mp  # noqa: E402


def test_fark_esigin_icindeyse_gecer():
    s = mp.puan_kapisi(0.7515, 0.7540)
    assert s["gecti"] is True and s["fark_puan"] == pytest.approx(0.25)


def test_fark_esigi_asarsa_duser():
    assert mp.puan_kapisi(0.7515, 0.7600)["gecti"] is False        # 0,85 puan


def test_tam_esikte_gecer():
    assert mp.puan_kapisi(0.7500, 0.7560)["gecti"] is True          # 0,6 puan


def test_cikis_kodu_kapiyi_yansitir():
    assert mp.main(["--referans-kutle", "0.7515", "--aday-kutle", "0.7540"]) == 0
    assert mp.main(["--referans-kutle", "0.7515", "--aday-kutle", "0.7700"]) == 1
```

- [ ] **Step 2: Kırmızıyı doğrula**

Run: `source ~/code/global_venv/bin/activate && python -m pytest -q -p no:cacheprovider tests/test_makine_kapisi_puan.py`
Expected: FAIL, `ModuleNotFoundError`.

- [ ] **Step 3: Gerçekle**

`scripts/olcum_uretim/makine_kapisi_puan.py`:

```python
#!/usr/bin/env python3
"""Makine geçiş kapısının puan düzeyi dalı (vLLM hattı; spec 2026-10-15 bölüm 5, G4 'puan').

vLLM'de aynı soru toplu gönderilince aynı cevabı vermeyebilir (Qwen3.5 GDN katmanlarında batch-invariant yok).
Bayt eşitliği yerine, yeni makinenin referans koşusuyla aynı hakemle puanlanmış kütle farkı gürültü bandının
içinde mi diye bakılır. Eşik G3 ile aynıdır (0,6 puan).

Kullanım:
  python scripts/olcum_uretim/makine_kapisi_puan.py --referans-kutle 0.7515 --aday-kutle 0.7540
  → çıkış kodu 0: kapı geçti · 1: düştü
"""
import argparse
import sys

ESIK_PUAN = 0.6


def puan_kapisi(referans_kutle_ort: float, aday_kutle_ort: float, esik_puan: float = ESIK_PUAN) -> dict:
    fark = round(abs(aday_kutle_ort - referans_kutle_ort) * 100, 6)
    return {"fark_puan": fark, "esik_puan": esik_puan, "gecti": fark <= esik_puan}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="makine kapısı, puan düzeyi")
    p.add_argument("--referans-kutle", type=float, required=True)
    p.add_argument("--aday-kutle", type=float, required=True)
    p.add_argument("--esik-puan", type=float, default=ESIK_PUAN)
    a = p.parse_args(argv)
    s = puan_kapisi(a.referans_kutle, a.aday_kutle, a.esik_puan)
    print(f"[makine-kapisi-puan] fark {s['fark_puan']:.3f} puan, eşik {s['esik_puan']} → "
          f"{'GEÇTİ' if s['gecti'] else 'DÜŞTÜ'}")
    return 0 if s["gecti"] else 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Yeşili doğrula ve hızlı takımı çalıştır**

Run: `source ~/code/global_venv/bin/activate && python -m pytest -q -p no:cacheprovider tests/test_makine_kapisi_puan.py && python -m pytest -q -p no:cacheprovider -m "not slow" 2>&1 | grep -E "passed|failed"`
Expected: `4 passed`; hızlı takım `0 failed`.

- [ ] **Step 5: Commit (kullanıcı isterse)**

```bash
git add scripts/olcum_uretim/makine_kapisi_puan.py tests/test_makine_kapisi_puan.py
git commit -m "feat: makine geçiş kapısının puan düzeyi dalı (vLLM hattı)"
```

---

### Görev 7: Hasat kapısı (yalnız G1-G3 geçtiyse)

**Files:**
- Create: `scripts/olcum_uretim/hasat_ortusme.py`
- Create: `tests/test_hasat_ortusme.py`

**Interfaces:**
- Consumes: `outputs/eval/f0/f06-hakem-gecisi/gnd_ds-acik_t{1..5}.jsonl` (Q4_K_M + llama.cpp cevaplarının DeepSeek-açık puanı) ve `outputs/eval/f0/f016-vllm-pilot/puanlama/gnd_vllm-bf16-orijinal_t{1..3}.jsonl` (orijinal bf16 + vLLM cevaplarının aynı hakemle puanı). Satır alanları: `id`, `faithfulness` (float ya da `None`).
- Produces: `hasat_ortusme.yanlis_kalemler(gnd_tekrarlari: list[list[dict]], esik: float = 0.5) -> set[int]`; `hasat_ortusme.ortusme(q4: set[int], bf16: set[int]) -> dict` → `{"q4_yanlis","bf16_yanlis","ortak","oran"}` (`oran` = ortak ÷ q4_yanlis, q4_yanlis=0 ise `None`).

- [ ] **Step 1: Başarısız testleri yaz**

`tests/test_hasat_ortusme.py`:

```python
"""Hasat kapısı (spec bölüm 6): Q4_K_M'in yanlış yaptığı kalemlerin ne kadarı bf16'da da yanlış?"""
import pytest

import hasat_ortusme as ho  # noqa: E402


def _tekrar(puanlar):
    return [{"id": i, "faithfulness": p} for i, p in enumerate(puanlar)]


def test_yanlis_kalem_tekrar_ortalamasi_esigin_altinda_olandir():
    t = [_tekrar([1.0, 0.0, 0.4]), _tekrar([1.0, 0.2, 0.8])]       # ortalamalar: 1,0 · 0,1 · 0,6
    assert ho.yanlis_kalemler(t, esik=0.5) == {1}


def test_puansiz_kalem_yanlis_sayilmaz():
    t = [_tekrar([None, 0.0]), _tekrar([None, 0.0])]
    assert ho.yanlis_kalemler(t) == {1}


def test_ortusme_orani_ortak_bolu_q4_yanlis():
    s = ho.ortusme({1, 2, 3, 4}, {3, 4, 5})
    assert s == {"q4_yanlis": 4, "bf16_yanlis": 3, "ortak": 2, "oran": pytest.approx(0.5)}


def test_q4_hic_yanlis_yapmadiysa_oran_tanimsiz():
    assert ho.ortusme(set(), {1})["oran"] is None
```

- [ ] **Step 2: Kırmızıyı doğrula**

Run: `source ~/code/global_venv/bin/activate && python -m pytest -q -p no:cacheprovider tests/test_hasat_ortusme.py`
Expected: FAIL, `ModuleNotFoundError`.

- [ ] **Step 3: Gerçekle**

`scripts/olcum_uretim/hasat_ortusme.py`:

```python
#!/usr/bin/env python3
"""Hasat kapısı (spec 2026-10-15 bölüm 6): Q4_K_M'in yanlış yaptığı kalemlerin ne kadarı orijinal bf16'da da yanlış?

Hasat (hard-negative üretimi) vLLM bf16'ya taşınırsa negatifler bf16 modelin hatalarıdır; ADR-0047 bunun gönderdiğimiz
Q4_K_M'in hatalarıyla örtüşmesini gerekçe yapmıştı. "Yanlış" = tekrar ortalaması `faithfulness` < esik (varsayılan 0,5);
puansız kalem (sıfır iddia, çekinme) sayılmaz. Eşik değeri (örtüşme oranı için geçme çizgisi) ölçümden önce plana yazılır.

Kullanım:
  python scripts/olcum_uretim/hasat_ortusme.py \\
      --q4 outputs/eval/f0/f06-hakem-gecisi/gnd_ds-acik_t{1,2,3,4,5}.jsonl \\
      --bf16 outputs/eval/f0/f016-vllm-pilot/puanlama/gnd_vllm-bf16-orijinal_t{1,2,3}.jsonl
"""
import argparse
import json


def yanlis_kalemler(gnd_tekrarlari: list[list[dict]], esik: float = 0.5) -> set[int]:
    toplam: dict[int, list[float]] = {}
    for tekrar in gnd_tekrarlari:
        for r in tekrar:
            if r.get("faithfulness") is not None:
                toplam.setdefault(r["id"], []).append(r["faithfulness"])
    return {i for i, v in toplam.items() if sum(v) / len(v) < esik}


def ortusme(q4: set[int], bf16: set[int]) -> dict:
    ortak = q4 & bf16
    return {"q4_yanlis": len(q4), "bf16_yanlis": len(bf16), "ortak": len(ortak),
            "oran": len(ortak) / len(q4) if q4 else None}


def _oku(yollar: list[str]) -> list[list[dict]]:
    return [[json.loads(l) for l in open(y, encoding="utf-8") if l.strip()] for y in yollar]


def main(argv=None):
    p = argparse.ArgumentParser(description="hasat kapısı: Q4 hataları bf16'da da var mı")
    p.add_argument("--q4", nargs="+", required=True)
    p.add_argument("--bf16", nargs="+", required=True)
    p.add_argument("--esik", type=float, default=0.5)
    a = p.parse_args(argv)
    s = ortusme(yanlis_kalemler(_oku(a.q4), a.esik), yanlis_kalemler(_oku(a.bf16), a.esik))
    print(json.dumps(s, ensure_ascii=False))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Yeşili doğrula**

Run: `source ~/code/global_venv/bin/activate && python -m pytest -q -p no:cacheprovider tests/test_hasat_ortusme.py`
Expected: `4 passed`.

- [ ] **Step 5: Geçme çizgisini kullanıcıyla belirle (ölçümden önce)**

`AskUserQuestion`: "Hasat kapısı: Q4_K_M'in yanlış yaptığı kalemlerin en az yüzde kaçı bf16'da da yanlış olmalı?" Seçenekler: %60 · %70 · %80 (önerilen: %70; Q4 hataları bf16'nın alt kümesi olmadığında, sıkıştırmaya özgü hatalar eğitim negatiflerine girmez) · başka. Cevabı bu adıma `*2026-10-..: eşik %X (kullanıcı kararı)*` biçiminde, **ölçümden önce** yaz.

- [ ] **Step 6: Ölçümü çalıştır ($0, mevcut puanlardan)**

Run:
```bash
source ~/code/global_venv/bin/activate
python scripts/olcum_uretim/hasat_ortusme.py \
  --q4 outputs/eval/f0/f06-hakem-gecisi/gnd_ds-acik_t1.jsonl outputs/eval/f0/f06-hakem-gecisi/gnd_ds-acik_t2.jsonl outputs/eval/f0/f06-hakem-gecisi/gnd_ds-acik_t3.jsonl outputs/eval/f0/f06-hakem-gecisi/gnd_ds-acik_t4.jsonl outputs/eval/f0/f06-hakem-gecisi/gnd_ds-acik_t5.jsonl \
  --bf16 outputs/eval/f0/f016-vllm-pilot/puanlama/gnd_vllm-bf16-orijinal_t1.jsonl outputs/eval/f0/f016-vllm-pilot/puanlama/gnd_vllm-bf16-orijinal_t2.jsonl outputs/eval/f0/f016-vllm-pilot/puanlama/gnd_vllm-bf16-orijinal_t3.jsonl \
  | tee outputs/eval/f0/f016-vllm-pilot/HASAT_ORTUSME.json
```
Expected: `{"q4_yanlis": N, "bf16_yanlis": M, "ortak": K, "oran": ...}`. `oran` seçilen çizgiyi geçiyorsa kapı geçti; `None` ise (Q4 hiç yanlış yapmadı) kapı tanımsız, kullanıcıya sorulur.

- [ ] **Step 7: Sonucu kullanıcıya sun**

Kapı geçerse: hasat uyarlaması (`scripts/egitim/modal_train.py::harvest_b10` vLLM'e) F1'in hasat turundan önce **ayrı bir plan** olarak yazılır; bu plan yalnız kapıyı ölçer (spec sapması, Görev 1'de kaydedildi). Geçmezse: hasat llama.cpp Q4_K_M'de kalır ve ADR-0107 bunu kaydeder.

- [ ] **Step 8: Commit (kullanıcı isterse)**

```bash
git add scripts/olcum_uretim/hasat_ortusme.py tests/test_hasat_ortusme.py outputs/eval/f0/f016-vllm-pilot/HASAT_ORTUSME.json
git commit -m "feat: hasat kapısı — Q4 hatalarının bf16'da örtüşmesi"
```

---

### Görev 8: Kayıt, ADR-0107 ve belgeler (ana oturum, "önce sun, sonra değiştir")

**Files:**
- Modify: `docs/record/kronoloji-75-86.md` (sona #86)
- Create: ADR-0107 bloğu `docs/adr/kararlar-0064-0085.md` sonuna; `docs/adr/README.md` satırı
- Modify: not bloğu eklenecek ADR'ler: 0047 (`docs/adr/kararlar-0045-0063.md`), 0080, 0097, 0098, 0104 m.3 (`docs/adr/kararlar-0064-0085.md`)
- Modify: `CLAUDE.md`, `docs/ROADMAP_v1.md`, `docs/YAYIN_YOL_HARITASI.md` (§3.4), `docs/EGITIM_ORTAMI.md`, `docs/OLCUM.md`, `docs/YENIDEN_URETIM.md`, `docs/MIMARI.md`, `MODEL_CARD.md`, `docs/record/yurutme-tuzaklari.md`, `docs/record/README.md`, `outputs/eval/README.md`, `docs/superpowers/plans/2026-10-11-F0-zemin.md` (F0.16 notu)

**Interfaces:**
- Consumes: `outputs/eval/f0/f016-vllm-pilot/OZET.json` (`girdi`, `kapilar`), `HASAT_ORTUSME.json` (varsa), `KUNYE.json` (fatura, sürümler).

Her belge için Step 1-3 döngüsü uygulanır: değişiklik listesi sun (dosya · bölüm · şimdi → olacak) → `AskUserQuestion` "işle" → yaz → `tests/test_belgeler.py`. Sayılar yalnız `OZET.json` ve künyeden kopyalanır, hafızadan yazılmaz. Sonuç **geçti** ya da **düştü** olsun, kayıt yazılır; olumsuz sonuç aynı titizlikle kaydedilir.

- [ ] **Step 1: Numaraları yeniden doğrula**

Run: `git log --oneline -5; git show HEAD:docs/record/kronoloji-75-86.md | grep -c '<a id="86"'; grep -c 'id="adr-0107"' docs/adr/kararlar-0064-0085.md`
Expected: kronoloji #86 ve ADR-0107 hâlâ boş; değilse bir sonraki numaralar kullanılır.

- [ ] **Step 2: Kronoloji #86**

Sun ve onayla, sonra `docs/record/kronoloji-75-86.md` sonuna `<a id="86"></a>` ile ekle. İçerik iskeleti (her başlık altı sayılar `OZET.json` alanlarından):
- Başlık bloğu: tarih, Modal A10, vLLM 0.30.0, hakem kimliği, kullanıcı onayları, kanıt yolu `outputs/eval/f0/f016-vllm-pilot/`.
- **1 · Eklenti denemesi:** `Unknown gguf model_type: qwen3_5` (kanıt `kontrol-eklenti/`).
- **2 · Çeviri:** `cevirme/CEVIRI_KUNYE.json` (F32 0,0000 · Q4_K 0,0715-0,0790 · Q6_K 0,0179-0,0193; 426 tensör, 15 MTP atlandı).
- **3 · Kapılar tablosu:** G1-G5 (`OZET.json: kapilar`), her satırda ölçüt ↔ değer ↔ sonuç.
- **4 · Üçlü karşılaştırma:** referans (0,7515) ↔ Q4'ten açılmış ↔ orijinal bf16 kütle ortalamaları (`girdi.*.kutle_ort`).
- **5 · Belirlenimcilik:** 8 soru tek tek ↔ toplu (`girdi.sekiz_soru`), iki toplu koşu arası aynı cevap sayısı (`iki_toplu_kosu_ayni`), dal (`g4.dal`).
- **6 · Hız ve maliyet:** koşu başına süre, 80 cevap/s, tahmini ↔ gerçek fatura.
- **7 · Hasat:** `HASAT_ORTUSME.json` (yapıldıysa).
- **Okuma ve Ders** (olumlu ya da olumsuz).

- [ ] **Step 3: ADR-0107**

Bloğun içeriği: spec bölüm 2 kararları (tablo biçiminde özet), pilot sonuçları (kapı tablosu, #86'ya bağlantı), belirlenimcilik dalı, hasat kapısı sonucu, kapı düştüyse "vLLM hangi işte kullanılmadı ve neden". Çapa `<a id="adr-0107"></a>`. `docs/adr/README.md` tablosuna 0107 satırı, "Numaralandırma" satırı "**0108**'den devam".

- [ ] **Step 4: Önceki ADR'lere not**

Her birinin sonuna, `ADR-0103` sonundaki **Not (2026-10-15, #85)** biçimiyle, "**Not (2026-10-..., [#86](…), [ADR-0107](…)):**" bloğu. Metinlere dokunulmaz. İçerik:
- ADR-0047: "vLLM/bf16 yasağı hasat için `<HASAT_ORTUSME oranına göre: kaldırıldı | korundu>`".
- ADR-0080: "nihai sayı Q4_K_M + llama.cpp'de ölçülür; seçim işleri vLLM bf16'da".
- ADR-0097 ve 0098: "makine geçiş kapısı vLLM hattında `<bayt | puan>` düzeyinde (G4); `makine_kapisi_puan.py`".
- ADR-0104 m.3: "vLLM geçiş ölçümü yapıldı: #86".

- [ ] **Step 5: CLAUDE.md ve işaretçiler**

Sun ve onayla. `CLAUDE.md`: (a) "Eval" paragrafında rejim değişmezlerine "two-stage measurement: selection work on vLLM bf16, headline numbers on Q4_K_M + llama.cpp (ADR-0107)" cümlesi; (b) "Deploy" paragrafına "server-side generation: vLLM 0.30.0 pinned (ADR-0107); product stays llama-server + GGUF"; (c) hasat dersi (B10) kapı sonucuna göre; (d) işaretçiler: "entries #39-#86 … continue at **#87**", "ledger runs to **0107**, next is **0108**". `docs/record/README.md`: "**Yeni girdi #87'den devam eder**". Kapı düştüyse (a)-(c) yerine tek cümle: "vLLM was piloted and not adopted for measurement (ADR-0107)".

- [ ] **Step 6: docs/ dosyaları**

Her biri için ayrı sun-onayla-işle:
- `docs/ROADMAP_v1.md`: kontrol listesine "F0.17 vLLM geçişi" satırı ve fazlar tablosuna F0.17 satırı (kapılar G1-G3, ölçüt, Görev 9 kapanışı).
- `docs/YAYIN_YOL_HARITASI.md` §3.4 ("İlk iş ~$2-5'lik bir pilottur: … vLLM üretimi"): "Sunucu ölçümü için vLLM pilotu yapıldı (#86); GRPO vLLM pilotu Haziran 2027'de kalır" notu. §5-§7 tablolarına satır eklenirse `<details>` bloğunun içine.
- `docs/EGITIM_ORTAMI.md`: vLLM sürüm kilidi (`0.30.0`, `huggingface_hub 1.33.0`, taban imaj) satırı.
- `docs/OLCUM.md`: "iki aşamalı ölçüm" kısa bölümü (hangi iş hangi motorda).
- `docs/YENIDEN_URETIM.md`: vLLM yolunun yeniden üretim komutları (`modal_pilot_vllm.py`, `kos.sh`, `vllm_ozetle.py`) ve belirlenimcilik dalı.
- `docs/MIMARI.md`: iki hat şeması (spec bölüm 3).
- `MODEL_CARD.md`: ölçüm motoru notu (nihai sayı Q4_K_M + llama.cpp; vLLM bf16 sayısı ve fark yan sütunda). Yayımlanan belge: emoji yok.
- `outputs/eval/README.md`: `f0` satırına `f016-vllm-pilot`.
- `docs/superpowers/plans/2026-10-11-F0-zemin.md` F0.16 bölümüne tek satırlık not: "vLLM ölçüm pilotu ayrı planda (`2026-10-15-vllm-gecis.md`), sonuç #86".

- [ ] **Step 7: Tuzaklar**

`docs/record/yurutme-tuzaklari.md` içine yeni satırlar. Önce `grep -n "^| 1\.[0-9]* \|^| 5\.[0-9]* " docs/record/yurutme-tuzaklari.md | tail -4` ile sıradaki numaraları bul; satırlar:
- Bölüm 1 (Üretim/eval): "**vLLM bf16 sayısı ürün sayısı sanılır**: ... nihai sayı Q4_K_M + llama.cpp'de; G5 farkı #86" ve "**vLLM'de bayt eşitliği varsayılır**: GDN katmanlarında batch-invariant yok; G4 dalı".
- Bölüm 5 (Artefakt): "**Q4'ten açılmış bf16 orijinal sanılır**: açılmış ağırlık Q4 hatasını taşır (%7,2 Q4_K, %1,8 Q6_K); yayımlanmaz, yalnız motor etkisi koşusu için".
- Bölüm 5: "**Çeviride yanlış baş dizilişi hata vermez**: doğrusal dikkat tensörlerinde v-başı sırası yanlışsa model açılır ve bozuk çalışır; tensör başına orijinalle göreli hata kapısı (`gguf_hf_cevir.py`, eşikler Q4_K 0,09 · Q6_K 0,025 · F32 1e-3)".
Başlık sayısı: dosyada "87 sessiz-bozulma kalıbı" yazıyorsa (`docs/record/README.md:8`) yeni sayıya güncelle.

- [ ] **Step 8: Bağlantı testi ve hızlı takım**

Run: `source ~/code/global_venv/bin/activate && python -m pytest -q -p no:cacheprovider tests/test_belgeler.py && python -m pytest -q -p no:cacheprovider -m "not slow" 2>&1 | grep -E "passed|failed"`
Expected: `4 passed`; hızlı takım `0 failed`.

- [ ] **Step 9: Commit (kullanıcı isterse)**

Üç commit önerilir: (1) kayıt ve ADR (#86, 0107, notlar) · (2) CLAUDE.md ve işaretçiler · (3) docs/ dosyaları ve tuzaklar. Mesajlar Türkçe, `docs:` öneki.

---

### Görev 9: Kapanış ve ROADMAP'e dönüş

**Files:**
- Modify: `docs/superpowers/plans/2026-10-11-F0-zemin.md` (F0.10 bölümü)
- Delete: `docs/superpowers/plans/2026-10-15-vllm-gecis.md` (kapanış bloğu yazıldıktan sonra, ADR-0083 emsali)
- Modify: `docs/ROADMAP_v1.md` (F0.17 işareti)

- [ ] **Step 1: Bitti kanıtını topla**

Run:
```bash
source ~/code/global_venv/bin/activate
awk '/^### Görev/{g=$0} /- \[ \]/{print g": "$0}' docs/superpowers/plans/2026-10-15-vllm-gecis.md | grep -v "Commit (kullanıcı isterse)" | head
python -m pytest -q -p no:cacheprovider -m "not slow" 2>&1 | grep -E "passed|failed"
git status --short | wc -l
```
Expected: açık kutu yok (atlanan görevler "atlandı: G1/G2/G3 düştü" notuyla kapalı), `0 failed`, `git status` yalnız kullanıcının commit etmediği dosyaları gösterir.

- [ ] **Step 2: F0.10 bölümünü yeni hatta göre güncelle**

Sun ve onayla. `docs/superpowers/plans/2026-10-11-F0-zemin.md` F0.10 bölümünde ölçüm kutularına şu notu ekle: "Seçim ölçümleri vLLM bf16'da (kapılar geçtiyse; #86), nihai sayı Q4_K_M + llama.cpp'de; makine geçişi `<bayt|puan>` kapısıyla; maliyet tahmini `OZET.json` hız sonucuyla yeniden hesaplanır." Kapılar düştüyse: "Ölçüm mevcut llama.cpp yolundadır (vLLM pilotu #86)".

- [ ] **Step 3: Kapanış**

Bu plan dosyasının sonuna "Kapanış" bloğu yaz (kapılar, harcama, öğrenilenler, #86 ve ADR-0107 bağlantıları), kullanıcı onayıyla dosyayı sil ve `CLAUDE.md` dosya ağacı satırındaki ADR-0106 istisna ifadesini, istisna bittiği için, "(ADR-0056; ADR-0106 exception closed)" olarak güncelle. `docs/ROADMAP_v1.md`'de F0.17 satırını `[x]` yap. Plana verilen bağlantıların (`ADR-0106` bloğundaki plan yolu, spec içindeki plan yolu) ölü kalmaması için bağlantıları kayda (`kronoloji #86`) yönlendir.

- [ ] **Step 4: Bağlantı testi**

Run: `source ~/code/global_venv/bin/activate && python -m pytest -q -p no:cacheprovider tests/test_belgeler.py`
Expected: `4 passed`.

- [ ] **Step 5: ROADMAP'e dön**

Kullanıcıya sun: "vLLM geçişi kapandı. Sıradaki: F0.10 (mevcut kolların DEV ölçümü), yeni hatla." `AskUserQuestion` ile başlatma onayı al.

- [ ] **Step 6: Commit (kullanıcı isterse)**

```bash
git add -A docs CLAUDE.md MODEL_CARD.md outputs/eval/README.md
git commit -m "docs: vLLM geçişi planı kapandı; F0.10 yeni hatla"
```

---

## Öz-denetim (plan yazarı)

**Spec kapsamı:** bölüm 2 kararları → Görev 1 (ADR-0106), 8 (ADR-0107); bölüm 3 mimari → Görev 8 Step 6 (MIMARI); bölüm 4 birimler → Görev 2, 3, 4, 6; vllm_sunucu.py "üç kullanım olunca çıkarılır" (kural: pilot, ölçüm, hasat) ve hasat uyarlaması ayrı plana ertelendi, spec sapması Görev 1'de kayda geçer; bölüm 5 pilot ve kapılar → Görev 3-5 (kod) ve `vllm_kapilari.py` (ölçütler testle kilitli); bölüm 6 hasat kapısı → Görev 7; bölüm 7 fazlar → Görev 1 (faz 0), 2-4 (faz 1), 5 (faz 2), 6 (faz 3), 7 (faz 4), 8 (faz 5), 9 (faz 6); bölüm 8 belge listesi → Görev 8; bölüm 9 riskler → Görev 5 Step 2 (açılış hatası dalı), Görev 5 Step 6 ($5 sınırı); bölüm 10 kapsam dışı → Global Constraints.

**Bilinçli boşluk:** hasat geçme çizgisi (Görev 7 Step 5) ölçümden önce kullanıcıdan alınır; bu bir "TBD" değil, spec bölüm 6'nın zorunlu karar adımıdır.

**Tür tutarlılığı:** `AGIRLIKLAR = ("q4-acilmis", "bf16-orijinal")` hem `modal_pilot_vllm.py` hem `vllm_kapilari.py` içinde aynı; `degerlendir` girdi anahtarları alt çizgili (`q4_acilmis`), dosya adları tireli ve `vllm_ozetle.girdi_olustur` ikisini `ad.replace("-", "_")` ile bağlar.
