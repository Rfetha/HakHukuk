# vLLM geçişi: tasarım

> **Durum:** tasarım onaylandı (2026-10-15, kullanıcı bölüm bölüm onayladı), kod ve plan sırada. Bu belge karar çerçevesidir;
> uygulama planı ayrı dosyadır (`docs/superpowers/plans/`). Ölçütler pilot sonucunu görmeden bu belgede kilitlenmiştir.
> Kaynak oturum: `f0-1-7`. Pilot kodu: commit `d7d028d`.

## 1. Amaç

Sunucu tarafında (ölçüm, benchmark, hasat, eğitim içi üretim) vLLM'in sağladığı toplu üretim hızından yararlanmak;
kullanıcıya giden ürünü (Q4_K_M GGUF + llama.cpp) ve ölçülen yolla ürün yolunun aynılığı kuralını
([ADR-0080](../../adr/kararlar-0064-0085.md#adr-0080)) bozmamak.

Neden şimdi: 80 DEV sorusu A10'da llama.cpp ile tek tek 640 s sürüyor; Checkpoint 1'in toplam yükü yaklaşık 36.500 cevap
(~81 GPU saati, ~$89, [#83](../../record/kronoloji-75-86.md#83)). Sektör vLLM ve SGLang arasında şekilleniyor; geçiş yolunun açık
kalması projenin tercihi.

## 2. Kararlar

| konu | karar |
| :-- | :-- |
| ilke (1') | Araç seçimi iş başınadır. Hangi araç o işte ölçümle kazanıyorsa o kullanılır: vLLM'in kazandığı yerde vLLM, llama.cpp'nin ya da düz Unsloth'un kazandığı yerde o. Bir iş vLLM'e yalnız ilgili kapıyı geçerse taşınır. |
| ürün ve yayın | Q4_K_M GGUF + llama.cpp aynen kalır. Mevcut GGUF ve HF deposu atılmaz, yeniden yapılmaz. Docker ürün compose'u ve `tests/test_konteyner.py` kapısı değişmez. |
| eğitim | SFT, ORPO ve benzerleri Unsloth'ta kalır. GRPO'nun kütüphanesi (Unsloth ya da TRL; ikisi de cevap üretiminde vLLM'i içeriden kullanır) Haziran 2027 pilotunda seçilir. |
| asıl kayıt | Eğitim çıktısı bf16 safetensors. Yalnız özel yedek depoda (`Rfetha/HakHukuk-yedek`) ve Modal hacminde durur; açık yayın bu belgenin kapsamında değil. |
| 4-bit safetensors | Yapılmaz (AWQ, GPTQ, FP4 biçimleri olgunlaşmadı; ayrı bir sıkıştırma ayrı kalite ölçümü ister). |
| ölçüm | İki aşamalı. Seçim işleri (hangi kol kazandı, ablasyon, benchmark) vLLM bf16'da; makaledeki ve model kartındaki nihai sayı Q4_K_M + llama.cpp'de bir kez ölçülür ve vLLM bf16 sayısıyla farkı kayda geçer. |
| belirlenimcilik | Pilot belirler: 8 soru tek tek ve toplu aynı cevabı veriyorsa bayt kuralı sürer, vermiyorsa puan düzeyi kuralı. İki dal da planda yazılıdır. |
| hasat | vLLM'e taşınır; ayrı kapıyla (bölüm 6). [ADR-0047](../../adr/kararlar-0045-0063.md#adr-0047)'nin "vLLM/bf16 yasak" hükmü bu kapı geçerse değişir. |
| plan | Ayrı plan dosyası. [ADR-0056](../../adr/kararlar-0045-0063.md#adr-0056)'nın "en fazla bir canlı plan" kuralı bunun için ADR-0106 ile değişir. Plan hemen uygulanır, sonra ROADMAP'e dönülür (F0.10 bu planın arkasında bekler). |

## 3. Mimari

```
EĞİTİM (Modal, Unsloth)  ->  bf16 safetensors  -->  vLLM (A10): seçim ölçümü, benchmark, hasat
                                  | asıl kayıt
                                  | (Modal hacmi + özel yedek depo)
                                  v
                           llama.cpp convert + quantize
                                  v
                           Q4_K_M GGUF  -->  llama.cpp: nihai sayı, ürün, Docker, HF (GGUF deposu)
```

| iş | araç | kazandığı nasıl kanıtlanır |
| :-- | :-- | :-- |
| SFT, ORPO | Unsloth | değişmiyor |
| seçim ölçümü, benchmark | vLLM bf16 | pilot kapıları G1-G3 |
| hasat | vLLM | bölüm 6, ayrı kapı |
| GRPO cevap üretimi | Unsloth ya da TRL (içinde vLLM) | Haziran 2027 pilotu |
| nihai sayı, model kartı | llama.cpp Q4_K_M | ürünle ölçülen yol aynı (ADR-0080) |
| uygulama, Docker, GGUF yayını | llama.cpp Q4_K_M | değişmiyor |
| Q4_K_M üretimi | llama.cpp convert + quantize | değişmiyor |

## 4. Birimler

| birim | iş | durum |
| :-- | :-- | :-- |
| `scripts/olcum_uretim/toplu_uret.py` | dondurulmuş bağlamdan soruları aynı anda gönderir; kayıt biçimi sıralı üretimle aynı | yazıldı |
| `scripts/olcum_uretim/gguf_hf_cevir.py` | Q4_K_M'i bf16 HF biçimine açar (426 tensör orijinalle doğrulandı); yalnız "motor etkisi" koşusunda kullanılır | yazıldı |
| `scripts/olcum_uretim/modal_pilot_vllm.py` | üçlü koşuya göre yeniden düzenlenir; orijinal bf16 Modal hacminden okunur | değişecek |
| `scripts/olcum_uretim/bf16_yukle.py` | dizüstünden Modal hacmine orijinal bf16, sha256 kapılı | yazılacak; yükleme ayrı onayla |
| `scripts/olcum_uretim/vllm_sunucu.py` | pilot, ölçüm ve hasatın ortak "sunucuyu aç, kapat" parçası | üç kullanım olunca çıkarılır |
| ölçüm hattı | `gen_eval_grounded.py` değişmez; resmî toplu yol `toplu_uret.py` (aynı kayıt biçimi); `makine_kapisi_puan.py` eklenir | kapılar geçerse |
| hasat | Modal `harvest_b10` vLLM'e uyarlanır | bölüm 6 kapısı geçerse |

## 5. Pilot ve kapılar

Pilot üç koşuyu karşılaştırır. Üçü de 80 DEV kalemi, h1 rejimi, aynı dondurulmuş bağlam, Modal A10:

| koşu | ağırlık | motor | neyi ayırır |
| :-- | :-- | :-- | :-- |
| 1. referans | Q4_K_M | llama.cpp | bugünkü ölçü (A10 referansı, [#83](../../record/kronoloji-75-86.md#83)) |
| 2. motor etkisi | Q4'ten açılmış bf16 | vLLM | aynı ağırlıklar, yalnız motor farkı |
| 3. Q4 etkisi | orijinal bf16 | vLLM | sıkıştırmanın etkisi (2 ile 3 arası) |

Puanlama: DeepSeek V4.1 Flash, hakemin düşünmesi açık, koşu başına 3 tekrar (F0.6'da tek koşunun oynaması ±0,26 puan,
[#85](../../record/kronoloji-75-86.md#85)). Referans için mevcut 5 koşu kullanılır (kütle ortalaması 0,7515).

| kapı | ölçüt | geçmezse |
| :-- | :-- | :-- |
| G1 açılıyor | bf16 klasörü vLLM'de açılır; 80 cevap geçerli (kesik <= %5, düşünce kanalı kullanılmış, boş cevap yok) | vLLM bu modelde ölçüm için kullanılmaz; ölçüm llama.cpp'de kalır |
| G2 hız | 80 cevap, llama.cpp süresinin (640 s) üçte birinden kısa, yani <= ~213 s | kazanç yok; ölçüm llama.cpp'de kalır |
| G3 motor etkisi | koşu 2 ile koşu 1 arasında kütle farkı <= 0,6 puan | vLLM puanları llama.cpp ile kıyaslanamaz; yalnız göreli sıralamada kullanılır ya da hiç |
| G4 belirlenimcilik | 8 soru tek tek ve toplu: cevaplar aynı mı | bilgi kapısı. Aynıysa bayt kuralı, değilse puan düzeyi kuralı |
| G5 Q4 etkisi | koşu 2 ile koşu 3 arası fark | yalnız raporlanır |

Maliyet sınırı: faz 2 toplamı tahminen $2-4; $5'i aşarsa durulur ve kullanıcıya dönülür.

## 6. Hasat kapısı

Hasat vLLM bf16'ya taşınırsa negatif örnekler bf16 modelin hatalarıdır, gönderdiğimiz Q4_K_M'inkiler değil; ADR-0047'nin
on-policy gerekçesi buna dayanıyordu. Kapı: Q4_K_M'in yanlış yaptığı kalemlerin bf16'da da yanlış olma oranı ölçülür.
Eşik, hasat ölçümünden önce ve pilot sonuçları ışığında plana yazılır. Geçmezse hasat llama.cpp Q4_K_M'de kalır.

## 7. Fazlar

| faz | ne | maliyet |
| :-- | :-- | :-- |
| 0 | karar kaydı: ADR-0106 (plan kuralı) | $0 |
| 1 | hazırlık: `bf16_yukle.py`, `modal_pilot_vllm.py` üçlüye, kapıların plana kilidi | $0 |
| 2 | pilot: bf16 yükleme (onayla), aşama A, aşama B, puanlama | ~$2-4 |
| 3 | ölçüm hattı: `toplu_uret.py` resmî toplu yol, `makine_kapisi_puan.py` | $0-1; yalnız G1-G3 geçerse |
| 4 | hasat kapısı (uyarlama, kapı geçerse ayrı plan) | $0 (pilot verisinden) |
| 5 | belgeler ve ADR-0107 | $0 |
| 6 | ROADMAP'e dönüş: F0.10 yeni hatta, sonra F0.8, F0.9 | |

## 8. Belge ve ADR etkisi

Her değişiklik uygulama sırasında "dosya, bölüm, şimdi, olacak" listesiyle sunulur ve açık onayla yapılır.

| ne | değişiklik |
| :-- | :-- |
| ADR-0106 (yeni) | canlı plan kuralının değişmesi |
| ADR-0107 (yeni) | iş başına kazanan araç, iki aşamalı ölçüm, belirlenimcilik dalları |
| ADR-0047, 0080, 0097, 0098, 0104 m.3 | bu kararla ilişkiyi gösteren notlar; metinlerine dokunulmaz |
| `CLAUDE.md` | ölçüm rejimi, dağıtım, hasat, işaretçiler |
| `docs/` | ROADMAP_v1 (yeni satır), YAYIN_YOL_HARITASI §3.4, EGITIM_ORTAMI, OLCUM, YENIDEN_URETIM, MIMARI, MODEL_CARD |
| `docs/record/yurutme-tuzaklari.md` | yeni tuzaklar: Q4 ile bf16 karışması, batch-invariant yok, çeviri doğrulama |
| kronoloji | pilot ve ölçüm sonuçları |
| Docker | değişmez |

## 9. Riskler

| risk | önlem |
| :-- | :-- |
| Qwen3.5'in doğrusal dikkat (GDN) katmanlarında vLLM batch-invariant modu desteklenmiyor (LMCache belgesi, sürüm belirtilmemiş) | pilot G4 ölçer; iki dal planda yazılı |
| vLLM'in GGUF eklentisi Qwen3.5'i tanımıyor (`Unknown gguf model_type: qwen3_5`, kanıt: `outputs/eval/f0/f016-vllm-pilot/kontrol-eklenti/`) | GGUF yerine bf16 safetensors okunur |
| vLLM sürümü kayar | `0.30.0` sabit; künyede kurulan sürümler |
| bf16'nın Modal'a gidişi (~8 GB, dışarı giden iş) | anahtarsız, dizüstünden hacme, yüklemeden önce onay |
| hakem gürültüsü (tek koşu ~1 puan, `gpt-4o-mini`) | DeepSeek-açık hakem, tekrar ortalaması |
| hasatta Q4 hatalarının bf16'ya taşınmaması | bölüm 6 kapısı |

## 10. Kapsam dışı

4-bit safetensors sürümü · GRPO kütüphane seçimi (Haziran 2027) · Docker ürün compose değişikliği · bf16'nın açık HF
yayını · llama.cpp'nin kendi paralel slot (`-np`) modunun ölçüme alınması.

## 11. Dayanaklar

- vLLM GGUF belgesi: "highly experimental"; eklenti `vllm-gguf-plugin` 0.0.5 yalnız Qwen2.5, Qwen3, Phi 3.5 gibi
  aileleri test ediyor; Qwen3.5 yok.
- vLLM batch-invariant belgesi: doğrulanmış modeller arasında Qwen3.5 yok; donanım şartı compute capability 8.0+ (A10: 8.6).
- Unsloth `fast_inference=True` ve TRL `vllm_mode=colocate|server`: cevap üretiminde vLLM'i içeriden kullanır; Qwen3.5 için
  doğrulanmış kaynak bulunamadı.
- Yerel çeviri doğrulaması: `outputs/eval/f0/f016-vllm-pilot/cevirme/CEVIRI_KUNYE.json` (F32 0,0000 · Q4_K 0,0715-0,0790 ·
  Q6_K 0,0179-0,0193).
