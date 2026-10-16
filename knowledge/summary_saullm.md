# SaulLM-7B: A pioneering LLM for Law (arXiv 2403.03883)

> ⚠️ **LİTERATÜR ÖZETİ — tez döneminde alındı.** Kaynak makalelerin bulguları geçerli; bunlardan çıkarılan **proje kararları** [`../docs/adr/`](../docs/adr/) ve [`ROADMAP_v1.md`](../docs/yol_haritasi/ROADMAP_v1.md) *(eski adı `ROADMAP.md`)*'de olabilir ve **değişmiş olabilir** (ör. base artık Qwen3.5-4B, proje OSS).

**Okundu:** 2026-06-14 · TeX kaynak · Equall.ai, ACL formatı · MIT lisans.

## TL;DR
Mistral-7B üzerine **iki aşamalı** hukuk uzmanlaştırması: (1) **30B token İngilizce hukuk korpusunda continued pre-training (CPT)** → bilgiyi ağırlığa gömer; (2) genel + hukuk **instruction fine-tuning (IFT)** → davranışı verir. Sonuç: LegalBench'te **7B/13B açık modeller arasında** SOTA (en iyi açık instruct modeline göre %11 göreli iyileşme). **Frontier'ı (GPT-4) yendiklerini İDDİA ETMEZLER** — rakip = peer açık modeller (Mistral-Instruct, Llama2-chat, Zephyr).

## Çekirdek katkılar
- **SaulLM (base)** + **SaulLM-IFT** (instruction-tuned) model ailesi, MIT lisans.
- **LegalBench-Instruct**: LegalBench'in temizlenmiş/format-düzeltilmiş versiyonu (orijinal promptlar 7B'leri format yüzünden haksız cezalandırıyor — birebir bizim "format ezberi correctness'i gölgeler" bulgumuz).
- Hukuk perplexity benchmark'ı (CPT cut-off sonrası taze belgeler — kontaminasyon önleme).

## Hatırlanacak teknik detaylar (REÇETE)
1. **CPT korpusu:** 94B ham → agresif temizlik+dedup → **30B token**. Kaynaklar: FreeLaw/Pile, MultiLegal Pile (ticari-lisanslı alt-küme), EDGAR, EuroParl, GovInfo, USPTO… (lisans-temiz olanlar).
2. **Replay ~%2** genel veri (Wikipedia, StackExchange, GitHub; SlimPajama'dan) → CPT sırasında catastrophic forgetting'i azaltır. → *bizim FT-reçete deep-research'ündeki "küçük replay %1-5" bulgusunu BİREBİR doğrular.*
3. **Instruction'ı PRE-TRAINING'e karıştırma:** SuperNatural Instructions + FLAN, CPT verisine dahil → IFT'siz base SaulLM'in bile güçlü çıkmasının sebebi olarak spekülasyon.
4. **IFT mix'i:** 600K **genel** instruction (SlimOrca/FLAN, MetaMathQA, UltraChat, Glaive-code) + **hukuk** instruction. Genel+hukuk birlikte şart; sadece hukuk yetmiyor.
5. **Hukuk instruction = SENTETİK 3-turlu üretim** (bizim zaten alıntıladığımız SaulLM şablonu): gerçek belge+metadata → Mistral-7B-instruct ile (1) kullanıcı isteği, (2) asistan metadata'yı yeniden ifade eder, (3) kullanıcı gerekçe ister → user-model + assistant-model ile konuşmayı uzat. Test-set hariç tutulur.
6. **DPO denendi, FAYDA YOK → bırakıldı** ("generic alignment OOD hukuk task'lerine uymuyor"). → *bizim "DPO daha-az-yıkıcı çürüdü" bulgusuyla uyumlu.*
7. **Compute:** CPT = 256× MI250 AMD GPU; IFT = 16× MI250. (Bizim ölçeğimizin çok üstü — bu yüzden bize EntiGraph/sentetik-CPT lazım.)

## En kritik BULGU (bizim için)
- **CPT bilgiyi gömdü; IFT davranışı verdi — ayrı işler.** Base SaulLM (IFT'siz) zaten Llama2-7B-chat'le başa baş (0.38 vs 0.39) → kazanç **CPT'den**, IFT üstüne +davranış.
- **Conclusion (saf tümdengelim akıl yürütme) task'lerinde hukuk-CPT ZARAR verdi** — generic Mistral daha iyi. **Hukuk bilgisi ≠ akıl yürütme.** Çözüm önerileri: math/reasoning verisi karıştır. → *naive CPT genel-reasoning'i bozar uyarımızı doğrular; genel-veri karışımı şart.*

## Bu projeye İLGİSİ (HakHukuk)
- **Doğrudan "SFT vs CPT" cevabı:** SaulLM bilgiyi **CPT ile** gömdü, SFT ile değil. Bizim v1 pilotunun "SFT kanun gömmüyor" bulgusu bununla tam tutarlı. Ağırlık-temelli bilgi = CPT yolu (bizde **v2c = EntiGraph sentetik-CPT**, çünkü 30B token + 256 GPU bütçemizde yok).
- **v2b (RAFT-SFT) için şablon:** SaulLM'in sentetik 3-turlu instruction üretimi = bizim davranış-hedefli veri şablonumuz (`V2_PLAN §5`). Gerçek madde → çok-turlu instruction.
- **Replay %2 doğrulaması:** `V2_PLAN §5.1 D` bandını destekler (küçük replay).
- **LegalBench-Instruct dersi:** format katı promptların 7B'leri haksız cezalandırması = bizim canon eval'de A4-format'ı A1/A2-correctness'ten AYIRMA kararımızı (ADR-0011) doğrular.
- **Rakip seçimi gerçeği:** SaulLM bile frontier'ı değil **peer açık modelleri** yendi. Bizim "frontier'ı yen" hedefimiz ancak **dar eksende** (grounded-accuracy + abstention + lokal/offline) gerçekçi — genel yetenekte değil.

## Açık sorular / taşınmazlıklar
- **Ölçek uçurumu:** 30B token CPT + 256 GPU bizde yok → SaulLM'in CPT'sini birebir kopyalayamayız; sentetik-CPT (EntiGraph) ekstrapolasyon, Türkçe/hukukta doğrulanmadı.
- **İngilizce/common-law + civil-law karışık** korpus; bizimki sadece TC mevzuatı (civil law). Transfer kısıtlı.
- **Güncellik:** SaulLM bilgiyi ağırlığa gömüyor → bayatlar. Bizim CLAUDE.md çekirdek kısıtı "güncellik kütüphanede (RAG), modelde değil" → biz CPT'yi minimuma indirip RAG'a yaslanmalıyız. SaulLM bu açıyı ele almıyor (RAG yok).
- **Frontier kıyası yok:** GPT-4 vs SaulLM kıyaslaması makalede yok → "küçük model frontier'ı yener mi" sorusuna SaulLM cevap vermiyor; sadece peer-open SOTA gösteriyor.
