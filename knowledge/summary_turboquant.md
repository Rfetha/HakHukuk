# TurboQuant: Online Vector Quantization with Near-optimal Distortion Rate

> ⚠️ **LİTERATÜR ÖZETİ — tez döneminde alındı.** Kaynak makalelerin bulguları geçerli; bunlardan çıkarılan **proje kararları** [`../docs/adr/`](../docs/adr/) ve [`ROADMAP_v1.md`](../docs/yol_haritasi/ROADMAP_v1.md) *(eski adı `ROADMAP.md`)*'de olabilir ve **değişmiş olabilir** (ör. base artık Qwen3.5-4B, proje OSS).

**Kaynak:** arXiv:2504.19874 — Zandieh, Daliri, Hadian, Mirrokni (Google Research / DeepMind / NYU)  
**GitHub (community port):** [0xSero/turboquant](https://github.com/0xSero/turboquant)

---

## TL;DR

TurboQuant, KV-cache'i **eğitim gerektirmeden, online (token-by-token)** şekilde 2.5–3.5 bit'e sıkıştıran bir vektör quantization algoritması. Llama-3.1-8B üzerinde 4.5× sıkıştırma ile full-precision performansını koruyor. **Ağırlık quantization değil** — sadece inference sırasındaki KV-cache'i etkiliyor.

---

## Core Contributions

- **MSE-optimal TurboQuant:** Vektörleri random rotate et → Beta dağılımlı koordinatlar → Lloyd-Max optimal scalar quantizer → teorik alt sınıra sadece 2.7× uzak distortion
- **Inner-product TurboQuant:** MSE quantizer bias'lı; residual'a 1-bit QJL (Quantized Johnson-Lindenstrauss) uygulayarak unbiased inner-product estimator elde et
- **Shannon lower bound kanıtı:** Herhangi bir b-bit quantizer için D_mse ≥ 1/4^b — TurboQuant buna 2.7× fark ile ulaşıyor
- **Indexing süresi sıfıra yakın:** PQ = 240s, RabitQ = 2267s, TurboQuant = 0.0013s (1536-dim, 4-bit)

---

## Key Technical Details

### Algoritma özeti

```
Quant(x):
  1. y = Π · x          # random rotation (sabit, pre-generated)
  2. idx_j = nearest centroid(y_j)  # per-coordinate Lloyd-Max
  3. r = x - DeQuant(idx)           # residual
  4. qjl = sign(S · r)              # 1-bit QJL on residual (inner-prod variant)
  return (idx, qjl, ||r||)
```

### Bit-width seçimi

| Bit | MSE distortion | Pratik kullanım |
|-----|---------------|-----------------|
| 2   | 0.117         | agresif sıkıştırma |
| 3   | 0.030         | **önerilen (kalite/boyut dengesi)** |
| 4   | 0.009         | full-precision'a çok yakın |

Pratikte: 32 outlier kanal → 3-bit, 96 normal → 2-bit → efektif **2.5-bit**

### LongBench sonuçları

- TurboQuant 3.5-bit: 50.06 avg (= Full Cache 50.06) ✓
- TurboQuant 2.5-bit: 49.44 avg (Full Cache 50.06'ya karşı küçük kayıp)
- Needle-in-Haystack (104K context): TurboQuant 0.997 vs Full 0.997 ✓

---

## Bu Projeye Relevans

### Nereye oturur

**Phase 1 (SFT/fine-tune):** İlgisiz. Training'de KV-cache önemli değil.

**Phase 2–3 (RAG + API serving):** Ana kullanım yeri tam burası:
- Türk mevzuatı sorgularında 256K context (Gemma 4 12B) → KV-cache patlar
- TurboQuant ile 4.5× sıkıştırma → aynı VRAM'da 4.5× daha uzun context
- Mahkeme kararı (içtihat) + kanun metni + kullanıcı sorusu kombine edilebilir

**Phase 3 (agent API):** vLLM backend üzerinde çalışıyor → serving altyapısına entegre edilebilir

### Nasıl entegre edilir

```python
# 0xSero/turboquant — vLLM 0.18.0+ üzerinde
pip install -e turboquant/
# vLLM'e TurboQuant KV-cache backend olarak ekleniyor
# 3-bit keys, 2-bit values konfigürasyonu
```

### Ne zaman değil

- Fine-tuning pipeline'ında (scripts/build_sft_dataset.py, training) — bu aşamada KV-cache küçük, gerek yok
- Model ağırlıklarını küçültmek için — bu iş QAT/GPTQ/AWQ'nun işi

---

## Open Questions / Caveats

1. **0xSero/turboquant community port** — Google'ın resmi implementasyonu değil. `validate_paper.py` / `audit_claims.py` scriptleri var ama üretim kalitesi belirsiz. Phase 3'te kullanmadan önce kararlılığı test edilmeli.
2. **GPU gereksinimi:** RTX 3090/5090 + CUDA 12.8 + vLLM 0.18.0+ — RTX 5070 Laptop (Blackwell, sm_120) uyumlu olmalı ama test edilmemiş.
3. **Multimodal KV-cache:** Gemma 4 12B'nin vision token'larının KV-cache'i text'ten farklı dağılım gösterebilir — outlier kanalları farklı olabilir.
4. **Outlier channel detection:** Uygulamada hangi 32 kanal "outlier" belirlenmesi gerekiyor; bu genellikle küçük kalibrasyon verisi gerektiriyor (online, eğitimsiz ama kalibrasyon adımı var).
