# Eval/Benchmark Metodolojisi — Literatür Özeti (RAG faithfulness + abstention + legal)

> ⚠️ **LİTERATÜR ÖZETİ — tez döneminde alındı.** Kaynak makalelerin bulguları geçerli; bunlardan çıkarılan **proje kararları** [`../docs/adr/`](../docs/adr/) ve [`ROADMAP.md`](../ROADMAP.md) *(2026-09-06'da silinmişti, 2026-09-07'de yeniden yazıldı)*'de olabilir ve **değişmiş olabilir** (ör. base artık Qwen3.5-4B, proje OSS).

> **Kaynak:** deep-research taraması (2026-06-13), 23 çapraz-doğrulanmış (3-0 oylu) bulgu.
> Sentez adımı socket hatasıyla çöktü → sentez elle yapıldı (ana ajan). **Amaç:** HakHukuk
> eval setini (CORE-HARD + TRAP) literatüre dayandırmak. İlgili: `docs/record/README.md`.

## Bağlam (neden tarandı)
RAG modunda faithfulness TAVANA çarpıyor (base≈v1≈0.97) → mevcut kolay held-out set modelleri
ayırt edemiyor. Tavan yapmayan, ayırt edici eksenler + zor/dengeli set + abstention seti lazım.

## Anahtar bulgular → tasarım kararları

### Zorluk = KARMAŞIKLIK, uzunluk değil
- Dahl et al. "Large Legal Fictions" (academic.oup.com/jla/16/1/64): hukukta halüsinasyon **görev
  karmaşıklığıyla** ölçekleniyor — düşük (dava var mı) düşük; yüksek (holdings, doktrin) **%59-92**.
  → CORE-HARD'ı **çok-koşullu/istisnalı/sentez** maddelerden seç, salt uzunluktan DEĞİL.
- Uzun-context RAG: pasaj eklendikçe kalite önce artıp sonra DÜŞER; **hard-negative'ler** ana sebep
  (arxiv 2410.05983).

### Tuzak/abstention = TOPIC-NEAR HARD-NEGATIVE, rastgele değil
- RGB (arxiv 2309.01431): negative-rejection distractor'ları **konu-ilgili hard-negative** (cevap
  içermeyen ama konuya yakın); doğru davranış = **sabit red dizesi**, skor = **Rejection Rate**.
- FaithEval (openreview UeVx6L59fg): unanswerable alt-küme = orijinal bağlamı LLM ile düzenleyip
  **cevap-taşıyan kanıtı çıkararak** kuruluyor (topic-near). Doğru cevap = "unknown" (explicit abstain).
- AbstentionBench (arxiv 2506.09038): abstention taksonomisi — unknown / underspecified / false-premise
  / subjective / outdated.

### Tavan YAPMAYAN ayırt edici eksenler
- **Rejection Rate** (abstention): en iyi modeller %43-45'te [RGB] → tavan yok, keskin ayırır.
- Faithfulness, abstention/counterfactual'da çöküyor: 76.8% → **7.4%** unanswerable'da [FaithEval];
  GPT-4o counterfactual %47.5.
- **Span/word-level halüsinasyon** taksonomisi (Evident/Subtle × Conflict/Baseless) [RAGTruth,
  arxiv 2401.00396]: response-level tavan yaparken bu yapmıyor. Halüsinasyon %9.3 (GPT-4)–%57.6 (Mistral).
- RAGBench TRACe (arxiv 2407.11005): tek faithfulness yerine 4 eksen (Utilization/Relevance/
  Adherence/Completeness); Adherence=groundedness.

### Boyut + judge geçerliliği (insan-annotation olmadan savunma)
- RGB: 600+200+200 soru, exact-match, ChatGPT-asistanlı, insan-doğrulamalı, **cutoff-sonrası içerik**
  (parametrik-ezber kirlenmesini önlemek).
- RAGBench: GPT-4 hakem insanla **%93/%95 uyum**; **n=40 yazar-etiketli** alt-küme ile doğrulama.
- RAGTruth: 2 etiketçi + 3. hakem, **%91.8** response / %78.8 span uyum.
- → Küçük set (n=40-100) **savunulabilir** AMA: cross-judge + ~30-40 yazar-etiketli alt-küme + uyum raporla.

## 🎯 v2 için doğrudan bulgu
- **AbstentionBench (claim 23):** *Reasoning fine-tuning abstention'ı ortalama **%24 BOZUYOR*** — eğitilen
  domeninde bile. → v1 (%1.1 hedge verisi) TRAP/abstention ekseninde **base'den kötü** çıkmalı (öngörü,
  benchmark'ta test edilecek). **v2 MUTLAKA hedge/abstention dilimi içermeli** yoksa SFT abstention'ı bozar.

## HakHukuk'a benimsenen yöntemler
| Karar | Benimsenen standart | Kaynak |
|---|---|---|
| Zorluk | karmaşıklık (fıkra/bent/istisna sayısı), uzunluk değil | Dahl |
| Tuzak | topic-near hard-negative (konu-yakını kardeş veya gold'dan kanıt-çıkarma) | RGB, FaithEval |
| Abstention skoru | Rejection Rate (sabit red + uydurma reddi) | RGB |
| Boyut | n≈40 CORE-HARD + ~35 TRAP + cross-judge + ~30 yazar spot-check | RAGBench, RAGTruth |
| Contamination | RAG modda sorun değil; KÖR modda limitation işaretle | RGB |
| İleride | span-level halüsinasyon taksonomisi | RAGTruth |

## TR hukuk benchmark manzarası + dış-benchmark konumlama (2026-07-08)

> Kaynak: dış-benchmark tarama oturumu (web-search + HF kartları). Karar: **ADR-0016**. Anlatı: research_log #35.

**Üretken TR hukuki grounding/abstention/citation + register ölçen tanınmış benchmark YOK** → bu boşluk katkımız. Mevcut TR setleri başka eksende:

| Set | Tip | Bize |
|---|---|---|
| TR-MMLU / TurkishMMLU / MMLU-Pro-TR | genel MC (hukuk alt-kategorili) | on-language sanity — ⚠️ alibayram sürümü **CC BY-NC + copyright poison**, kullanma |
| Cetvel / TurkBench / TARA / TrGLUE | genel Türkçe LLM | genel-yetenek regresyon kontrolü |
| HukukBERT | encoder Legal Cloze | üretken değil |
| LEXam | 340 sınav, İngilizce+Almanca | TR değil |
| Mecellem (NewMind) | retrieval/embedding + CPT decoder | rakip değil; Mecellem-4B=baseline (koşulu), Mursit=Faz-2 retriever |

**Dış İngilizce benchmark (BigLaw-Bench / LegalBench) = off-axis → cite-only.** İngilizce + US/UK common-law; TR medeni-hukuk üretken modelinde düşük skor yorumlanamaz (model mi kötü, sınav mı yanlış — ayrılamaz). Frontier kıyası **kendi canon setinde** yapılır (frontier + Mecellem-4B + Llama-8B baseline + cross-family judge — ADR-0011/TODO).

**Muhakim (newmindai reward model, 5 eksen)** = cite-only, judge olarak koşulmaz (EuroHPC-Legal kirliliği + cross-family judge zaten var). ADR-0016 §3.

**Piyasa boşluğu (2026-07):** open-weight + TR-hukuk + instruction-tuned + edge-deploy bir hazır asistan YOK. En yakın open-weight hukuk = Mecellem-4B (CPT base, asistan değil); genel TR-instruct (Cosmos Turkish-Llama-8B, WiroAI-9B, Trendyol) hukuk-uzmanı değil.
