# Mecellem Models — Turkish Legal LLMs (arXiv:2601.16018, NewmindAI, Ocak 2026)

> ⚠️ **LİTERATÜR ÖZETİ — tez döneminde alındı.** Kaynak makalelerin bulguları geçerli; bunlardan çıkarılan **proje kararları** [`../docs/adr/`](../docs/adr/) ve [`ROADMAP_v1.md`](../docs/ROADMAP_v1.md) *(eski adı `ROADMAP.md`)*'de olabilir ve **değişmiş olabilir** (ör. base artık Qwen3.5-4B, proje OSS).

## TL;DR
NewmindAI'ın Türk hukuk alanı için geliştirdiği açık kaynak model ailesi. İki ana katkı: (1) sıfırdan eğitilmiş ModernBERT-tabanlı Türkçe **encoder/embedding** modelleri (Mursit, 155M & 403M) — Türkçe hukuk retrieval'da top-3; (2) Qwen3-1.7B ve Qwen3-4B üzerine **continual pre-training (CPT)** ile Türkçe hukuka uyarlanmış **decoder** modelleri (Mecellem-Qwen3-TR) — hukuk metninde %36-43 perplexity düşüşü. Hepsi HF'te açık. **Bizim projemizin en yakın komşusu ve potansiyel temel taşı.**

## Çekirdek katkılar
- **Mursit encoder'ları** (sıfırdan, 112.7B token): `Mursit-Base-TR-Retrieval` (155M) ve `Mursit-Large-TR-Retrieval` (403M). Türkçe retrieval leaderboard'da 1. ve 2. Legal Score. → **Faz 2 RAG embedding'i için doğrudan aday.**
- **Mecellem-Qwen3-TR decoder'ları** (CPT): `Mecellem-Qwen3-1.7B-TR` (4 fazlı curriculum) ve `Mecellem-Qwen3-4B-TR` (tek faz, 270B token). Perplexity: 4B base 7.65 → CPT 4.88 (%36.2 ↓); 1.7B base 9.22 → 5.24 (%43.1 ↓). 11 hukuk alt-alanında (rekabet, vergi, iş, KVKK, fikri mülkiyet…) ölçülmüş.
- **Muhakim** (`newmindai/Muhakim`): Skywork-Reward-Llama-3.1-8B tabanlı, MoE-gating'li Türkçe hukuk **ödül/değerlendirme modeli**. 5 boyut: kanun atıfı, hukuki doğruluk, içtihat atıfı, dil tutarlılığı, derinlik. Apache 2.0. → **Bizim eval adımı için hazır Türkçe-hukuk hakemi.**
- **EuroHPC-Legal** (`newmindai/EuroHPC-Legal`): 116 soru-referans çifti, alt-alan etiketli. → **Hazır değerlendirme seti.**
- Kod + benchmark: `github.com/newmindai/mecellem-models`. Koleksiyonlar: `hf.co/collections/newmindai/mecellem-models`, `.../mleb-dataset`.

## Hatırlanması gereken teknik detaylar
- **Donanım:** MareNostrum 5, 100 düğüm × 4 H100 64GB. CPT için 270B token (4B). **Bu ölçek bizim 12 GB'de (RTX 5070) tekrarlanamaz** — onların yaptığı pahalı işi biz yapamayız, hazır kullanırız.
- **Veri kaynakları (bizim de kullanabileceğimiz, kamu):** Yargıtay (3.43B token), Danıştay, YÖKTEZ tezleri (9.61B), FineWeb2 + CulturaX (genel Türkçe). OCR için Tesseract yerine **DotsOCR (VLM)** kullanmışlar (tablo/formül/çok-sütun sorunları nedeniyle).
- **Veri temizleme reçetesi:** exact-hash dedup (~%5) → SemHash semantik dedup (eşik 0.75) → FineWeb kalite filtresi → GlotLID dil tespiti → **Türkçe-özel morfolojik filtre** (Zemberek: suffix entropy >%75, lemma diversity >%50). Bizim Adım 4 (veri temizleme) için birebir şablon.
- **CPT'de curriculum:** küçük modelde (1.7B) 4-fazlı curriculum büyük etki; 4B'de tek faz curriculum'a yakın sonuç → "model büyüdükçe curriculum'un önemi azalıyor".
- **Önemli uyarı (decoder→encoder):** Qwen3'ü embedding'e çevirmek (Mursit-Embed) kötü sonuç verdi; amaca-özel encoder (Mursit-Base 155M) 4B converted modeli geçti. → Faz 2'de embedding için encoder kullan, decoder'ı embedding'e çevirme.
- **Karışık hassasiyet:** uzun CPT için BF16-FP8 öneriliyor (bizim QLoRA'da doğrudan ilgili değil ama bulut koşusu için not).

## Bu projeye ilişkisi (somut)
- **Baz model adayı:** `Mecellem-Qwen3-4B-TR` zaten Türkçe hukuka derinlemesine uyarlanmış bir **base** (instruction-tuned/SFT değil). Bizim işimiz onun üstüne **vatandaş-dili SFT** (sade dil + dilekçe) eklemek — bu, 12 GB'de QLoRA ile yapılabilen ucuz kısım. Pahalı CPT'yi onlar yapmış.
- **Eval (Adım 8):** `Muhakim` + `EuroHPC-Legal` ile GPT-4o'ya bağımlılığı azaltırız; Türkçe-hukuk-native ölçüm.
- **Faz 2 RAG:** `Mursit-Base-TR-Retrieval` (155M) embedding olarak hazır; `bge-m3-stsb` alternatif.
- **Veri pipeline (Adım 3-4):** kaynak listesi (Yargıtay/Danıştay/YÖKTEZ/Mevzuat) + temizleme reçetesi doğrudan benimsenebilir.

## Açık sorular / dikkat
- **Lisans doğrulanmalı:** Makale "açık kaynak" diyor ama decoder modellerin/veri setlerinin tam lisansını (Apache/araştırma-kısıtlı?) HF koleksiyonundan birebir kontrol etmeliyiz (lisans-temizlik katı kuralımız).
- **Base ≠ asistan:** Mecellem-Qwen3-TR bir CPT base'dir; vatandaş sorusuna sohbet formatında cevap vermez. SFT şart — bu zaten bizim katkımız.
- **Hedef kitle farkı:** Mecellem hukukçu/retrieval'a bakıyor; biz **vatandaş** (sade dil) hedefliyoruz. Çakışmıyoruz, üstüne biniyoruz — farklılaşma noktamız net.
- **"Newer base" gerilimi:** Qwen3 artık bir nesil eski (Qwen3.5, Gemma 4 çıktı). Ama daha yeni bir genel modeli biz hukuka CPT ile uyarlayamayız (süperbilgisayar ister). Trade-off: *yeni ama hukuka uyarlanmamış genel base* vs *bir nesil eski ama hukuka uyarlı Mecellem*.
