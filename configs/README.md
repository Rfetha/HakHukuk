# configs/ — base'e özgü ayar dosyaları

Boş başlıyor. Yeni base seçildiğinde **buraya konacaklar:**

## Chat şablonu yaması — `<base-adi>.jinja`

llama.cpp'nin minja motoru bazı gömülü chat şablonlarını **yanlış render eder.** Somut vaka
(2026-07-24, Gemma 4): `enable_thinking is defined` dalı yanlış değerlendirildi → üretim
isteminin sonundaki boş düşünce kanalı yazılmadı → **model durmadı, girdiyi tekrarladı.**
Hata vermez; bir CANON koşusunu sessizce çöpe çevirir.

Gömülü şablon bozuksa düzeltilmiş `.jinja` buraya konur ve şöyle verilir:

```bash
CHAT_TEMPLATE=configs/<base-adi>.jinja bash scripts/olcum_uretim/smoke_llamacpp.sh <gguf>
CHAT_TEMPLATE=configs/<base-adi>.jinja bash scripts/olcum_uretim/diag_abstain.sh <gguf>
```

Örnek (emekli hat): `git show a19fc25^:old-version-gemma4-12b/configs/gemma4_nothink.jinja`
— repo'dan silindi (ADR-0034), repo dışı kopya da yok.

---

## ✅ Yeni base kabul kontrol listesi

Bir base bunları geçmeden **hiçbir eğitim/eval sayısına güvenme.**

| # | kontrol | nasıl | neden |
| :--- | :--- | :--- | :--- |
| 1 | Tokenizer yükleniyor mu | `AutoTokenizer.from_pretrained` | `extra_special_tokens` LİSTE gelirse transformers 4.x patlar → `setup_llamacpp.sh` `FIX_TOKENIZER=1` |
| 2 | GGUF üretiliyor + boyut makul mu | `bash scripts/egitim/setup_llamacpp.sh <repo> <etiket>` | quantize yarıda kesilirse çıktı bozuk kalır (E4B böyle 70 MB çıktı); script artık <100 MB'da durdurur |
| 3 | **Şablon render'ı GÖZLE doğru mu** | `bash scripts/olcum_uretim/diag_chat_template.sh <gguf>` → `/apply-template` çıktısını oku | ⚠️ en kritik adım; yukarıdaki tuzak |
| 4 | Model DURUYOR mu | `bash scripts/olcum_uretim/smoke_llamacpp.sh <gguf>` → `finish_reason=stop`, girdi tekrarı yok | durmayan model tüm eval'i geçersiz kılar |
| 5 | **Turn işaretleri ne** | 3. adımdaki render'dan `user_part` / `assistant_part` dizilerini çıkar | responses-only maskeleme bunlara dayanır; yanlışsa **eğitim sessizce bozulur**. `train_sft.py` render'a karşı assert eder ama doğru değeri sen vermelisin |
| 6 | `target_modules` tutuyor mu | `--target-modules` ile ver, LoRA param sayısını logdan doğrula | farklı mimaride (MoE, linear-attention) isimler tutmaz → "0 LoRA takıldı" |
| 7 | `--pure` doğru mu | QAT-Q4_0 base ise `PURE=1`, değilse `PURE=0` | QAT olmayanda `--pure` embedding'i gereksiz kaybettirir (ADR-0023) |
| 8 | Bağlam tavanı + VRAM | `smoke_llamacpp.sh <gguf> <ctx>` VRAM payını basar | erişilebilirlik ekseni (≤8 GB soft-gate, ADR-0018) |

Ayrıntılı gerekçeler: [kronoloji #38](../docs/record/gemma4-12b-kronoloji.md) ·
[`ADR-0023`](../docs/adr/gemma4-12b-dersler.md#adr-0023) (dağıtım config) ·
[`ADR-0025`](../docs/adr/gemma4-12b-dersler.md#adr-0025) (eval yolu) ·
[`ADR-0027`](../docs/adr/kararlar-0027-0044.md#adr-0027) (yeni hat) ·
`TASARIM.md` ⚰️ *(2026-09-06'da silindi; ölçüm protokolü `docs/adr/` + `docs/record/` içinde yaşıyor)* §8 (base doğrulama kapısı — bu kontrol listesinin otoritesi)
