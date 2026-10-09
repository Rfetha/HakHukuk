# Citation Grounding + hukuk graf-RAG literatürü — proje notu

> ⚠️ **LİTERATÜR ÖZETİ — tez döneminde alındı.** Kaynak makalelerin bulguları geçerli; bunlardan çıkarılan **proje kararları** [`../docs/adr/`](../docs/adr/) ve [`ROADMAP.md`](../docs/ROADMAP.md) *(2026-09-06'da silinmişti, 2026-09-07'de yeniden yazıldı)*'de olabilir ve **değişmiş olabilir** (ör. base artık Qwen3.5-4B, proje OSS).

> **Ne:** 2026-07-23 taraması. Üç makale, iki soruya cevap arıyordu: (1) graf teze girsin mi ve
> hangi biçimde (→ ADR-0022), (2) v4 reçetesinin negatif-üretim yöntemi doğru mu (→ v4 güncellemesi).
> **Kaynak:** arXiv/Sage abstract + landing sayfaları (tam metin okunmadı — aşağıdaki "belirsiz"
> notlarına dikkat).

---

## 1. Citation Grounding (arXiv 2606.00898) — **en alakalı**

*Detecting and Reducing LLM Citation Hallucinations via Legal Citation Graphs*

**Problem:** LLM'ler uydurma atıf üretiyor — var olmayan madde, mülga hüküm, yanlış yargı çevresi.
Ölçeklenebilir bir ölçüm/azaltma yöntemi yoktu.

**Yöntem:**
- **Deterministik** atıf grafı: 100.8M Ukrayna mahkeme kararı → **502M kenar, 21.736 mevzuat düğümü.**
  Graf mevcut karar verisinden çıkarılıyor — LLM ile inşa **edilmiyor**.
- Halüsinasyonu **üç bileşene** ayırıyor:
  1. **precision** — atıf var mı?
  2. **relevance** — bağlama uygun mu?
  3. **temporality** — atıf yapılan tarihte **yürürlükte miydi?**
- **Citation Grounding DPO:** gerçek kararlardaki doğrulanmış atıflar **algoritmik olarak bozularak**
  tercih çiftleri üretiliyor — 4 hedefli bozma stratejisi, **insan anotasyonu yok.**

**Sonuçlar:**
- 5 LLM sisteminde Citation Grounding **0.791–0.873**; atıfların **%13–21'i halüsinasyon.**
- Fine-tune edilmiş **Qwen2.5-7B**, doğru/bozuk atıfı **%98.5** doğrulukla ayırıyor.

**Bizim için üç sonuç:**

1. **v4 reçetesinin bağımsız doğrulaması.** Bizim yönümüz (preference/ORPO + negatif-aile
   çeşitliliği) aynı fikir; onlar yayınlamış ve çalıştığını göstermiş.
2. **Negatif üretimi bizde daha pahalı.** `docs/record/v4/recipe.md` ADIM 3 rejected'ları
   **modelden hasat** ediyor (Modal A100, ~$5-15 — turun en pahalı adımı) + iki-taraflı filtre.
   Onlarınki **algoritmik bozma**: model hasadı yok, insan yok, marj daha kontrollü.
   → Reçete §2-A/E ve ADIM 3 revize edilmeli.
3. **Zamansal eksen bizde HİÇ YOK.** Onların 3. bileşeni (temporality) ne CANON'da ne v4
   reçetesinde var. TR mevzuatında `mülga`/`değişik` zincirleri mevcut, Bedesten veriyi sunuyor,
   ve ADR-0022 (a) yapısal grafı bu zincirleri **zaten taşıyacak** → bedava duran, rakiplerin
   beceremediği bir kulvar.

⚠️ **Belirsiz:** ne kadarının Ukrayna hukuk sistemine özgü olduğu; TR'ye taşınırken korpus farkı
(bizde 100M karar yok — Bedesten mevzuat + içtihat).

---

## 2. SAT-Graph RAG (FAIA251598, 2025)

*An Ontology-Driven Graph RAG for Legal Norms: A Hierarchical, Temporal, and Deterministic Approach*

- Hukuk normlarının **biçimsel yapısını ve zaman içindeki değişimini** açıkça modelliyor.
- Soyut **"Work"** (kanunun kendisi) ile sürümlenmiş **"Expression"** (belirli tarihteki hâli)
  ayrımı → **TR mevzuatına birebir oturuyor:** kanun = Work, `değişik`/`mülga` sonrası hâlleri =
  Expression, değişiklik zincirleri = sürüm kenarları.
- **Deterministik** — LLM ile indeksleme yok.

→ ADR-0022 (a)'nın ontoloji tarafı için doğrudan referans.

---

## 3. LegalGraphRAG (arXiv 2605.28120) — **bizim seçmediğimiz yol**

- Üç ajan: **Researcher** (kanıt getir) → **Auditor** (kaynağa karşı doğrula) → **Adjudicator**
  (sentezle).
- Hiyerarşik hukuk grafı: vaka / madde / yorum çok-granülerliğini ayırıyor
  ("flat graph hukuk korpusunun çok-granülerliğini yakalayamaz").
- **En güçlü baseline'ların %6.3–19.1 üstünde** (SOTA iddiası).

**Neden almadık (ADR-0022):** kazanç gerçek, ama sorgu başına ~3 LLM çağrısı → çıkarım maliyeti
~3× → **doğrudan maliyet-normalize parite metriğinden düşer.** Üstelik adalet kuralı gereği aynı
harness rakiplere de verilecek → onların maliyeti de 3×. Yani (b) kaliteyi artırırken tezin
ölçtüğü şeyi bozuyor.

⚠️ **Kritik boşluk:** makale **maliyet/gecikme yükünü hiç raporlamıyor** — abstract'ta ne token
maliyeti ne latency var. Karşılaştırma yaparken bu eksiklik not edilmeli.
⚠️ **Belirsiz:** graf inşasının chunk başına LLM çağrısı gerektirip gerektirmediği abstract'tan
okunamadı (muhtemelen evet).

---

## Projeye bağlanış

| Bulgu | Nereye |
| :--- | :--- |
| Deterministik graf + zamansallık işe yarıyor | **ADR-0022** (a) kararının ön-çalışması |
| Çok-ajanlı hat pahalı, maliyet raporlanmamış | **ADR-0022** (b) reddinin gerekçesi |
| Algoritmik negatif üretimi > model hasadı | **v4 reçetesi** §2-A/E + ADIM 3 revizyonu |
| Zamansal eksen (mülga/değişik) | **CANON'a yeni kulvar adayı** + v4 negatif ailesi |
| Frontier'da %13-21 atıf halüsinasyonu | **KAPI 1** rakip baseline beklentisi |

## Kaynaklar

- arXiv **2606.00898** — Citation Grounding
- Sage/FAIA **251598** — SAT-Graph RAG (Ontology-Driven Graph RAG for Legal Norms)
- arXiv **2605.28120** — LegalGraphRAG
- (yan) arXiv 2506.22165 — Joint Legal Citation Prediction via Heterogeneous Graph Enrichment
- (yan) arXiv 2605.17639 — Temporal Decay of Co-Citation Predictability (20-yıl mevzuat getirme benchmark'ı)
