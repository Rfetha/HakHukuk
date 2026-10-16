# Reinforcement Learning for LLM Post-Training: A Survey (arXiv 2407.16216)

> **Literatür özeti.** Bu belgeden çıkan proje kararları `docs/adr/` ve `docs/yol_haritasi/YAYIN_YOL_HARITASI.md` içindedir. Burada yalnız öneri vardır, karar yoktur.
>
> *Yazım notu (ana oturum):* metni bir alt ajan üretti; alt ajanların dosya yazması araç tarafından engellendiği için ana oturum ajanın metnini olduğu gibi yazdı.

**Okundu:** 2026-10-10 · TeX kaynak (`\title` doğrulandı) · TMLR önbaskı biçimi · yazarlar Z. Wang, K. Ramnath, B. Bi ve ark. (Salesforce, AWS AI Labs, Airbnb).
**Sürüm uyarısı:** İndirilen kaynak yeni bir derlemedir (2026). Bu arXiv numarasının eski sürümleri başka başlık ve kapsam taşıyabilir. Atıf yaparken sürüm numarası kaydedilmeli.
**Bölüm numaraları** TeX'teki `\section` sırasından türetilmiştir: 2 temeller · 3 istem örnekleme · 4 cevap örnekleme · 5 gradyan katsayısı · 6 çevrimiçi RLHF/RLAIF/yinelemeli DPO/Nash · 7 çevrimdışı DPO ailesi · 8 gelecek yönler.

## TL;DR

Makale bir derlemedir (survey) ve deney içermez. Bütün art-eğitim yöntemlerini (MLE/SFT, RFT, REINFORCE, PPO, DPO ve türevleri, GRPO ve türevleri) tek bir **birleşik politika gradyanı** biçiminde yazar. Her yöntem, token başına bir **gradyan katsayısı** `GC(x,y,t)` ile `∇log π(y_t|x,y_<t)` çarpımıdır (§2.1).

HakHukuk için değeri üç yerdedir:

1. §7.4, SFT ile tercih kaybını **tek koşuda** birleştirmeyi (ORPO, UFT, SLiC-HF, RRHF/PRO) ve **paralel eğit + birleştir** yolunu (PAFT) yan yana koyar.
2. §5, GRPO tasarım eksenlerini ayrıştırır: dinamik örnekleme, çoklu ödül normalizasyonu, KL/entropi, hibrit SFT+RL.
3. §6.2 ve §8, kural tabanlı çekinme ödülünü, ödül suistimalini ve aşırı reddi yöntem sorusu olarak ele alır.

## Ana katkılar

1. **Birleşik çerçeve (§2.1).** Ön-eğitim, SFT, RFT, PPO, DPO ve GRPO aynı gradyan biçiminin özel durumlarıdır.
   - SFT için `GC = 1`.
   - RFT için `GC = I(y = y*)` (§2.2.1-2.2.2).
   - DPO için `GC_w = β σ(r_l − r_w)` ve `GC_l` bunun eksilisidir. Katsayı yanıt içinde sabittir (§2.4.4).
   - GRPO için `c·ρ·A + β(π_ref/π_θ − 1)` (§2.5.1).
2. **Çevrimdışı DPO ailesinin dört eksenli sınıflandırması (§7).** Yanıt biçimi (çift/tek/liste) · ödül türü · düzenlileştirme · SFT ile birleştirme.
3. **RLVR (doğrulanabilir ödül) için üç eksen (§3-5).** İstem seçimi, cevap örnekleme/seçimi ve gradyan katsayısı. Gradyan katsayısı IS oranı, avantaj biçimlendirme, normalizasyon, uzunluk normalizasyonu ve düzenlileştirmeden oluşur.
4. **Ortak gösterim.** Her makalenin güncelleme kuralı aynı `GC` sözlüğüyle yazılmıştır. Ek tablolar temel model, veri, KL ve entropi tercihlerini listeler.
5. **Açık sorular listesi (§8).** Ödül suistimali, uzunluk yanlılığı, çeşitlilik çöküşü, çevrimdışı-çevrimiçi yakınsama ve SFT-RL boru hattı entegrasyonu.

## Teknik ayrıntılar

**Tercih kayıpları (§2.4.4, §7).**
- **DPO:** `−log σ(β[log π_θ(y_w)/π_ref(y_w) − log π_θ(y_l)/π_ref(y_l)])`. Ödül modeli ve RL döngüsü yoktur, referans model gerekir. Veri sabit olduğu için IS oranı yoktur.
- **ORPO (§7.4.1):** Referanssızdır. `J = log π_θ(y_w|x) + λ log σ(log OR_θ)`, burada `OR = odds(y_w)/odds(y_l)` ve `odds(y) = π/(1−π)`.
  - Makalenin aktardığı gerekçe: SFT yalnız istenen cevaba uygulandığında istenmeyen cevabın olasılığı da artar.
  - SFT terimi kaybın içindedir. ORPO zaten "SFT + tercih"in tek koşusudur.
- **SLiC-HF (§7.1.1):** `−max(0, δ_m − log π(y_w) + log π(y_l)) + λ_sft log π(y_sft)`. Örneklem-sıralama (sample-rank) varyantı modelin kendi çıktısından çift kurar ve daha kararlı yakınsar.
- **DPOP (§7.1.1):** DPO, küçük düzenleme mesafeli çiftlerde tercih edilen cevabın olasılığını da düşürebilir. `λ_pos·max(0, log π_ref(y_w)/π_θ(y_w))` terimi bunu önler.
- **IPO (§7.1.1):** Tercih deterministikse (`P(y_w>y_l)=1`) DPO'nun log-oran farkı sonsuza gider ve `β`'nın KL etkisi zayıflar. IPO kare kayıpla farkı `1/(2β)` hedefine bağlar.
- **KTO, DRO, UNA (§7.1.2):** Eşleşmiş çift gerekmez. KTO ikili geri bildirimle kayıp-kaçınmalı fayda fonksiyonu kullanır. UNA puan, ikili ve çift verisini tek MSE kaybında toplar. Çift veride DPO'ya eşdeğerdir.
- **SimPO, R-DPO (§7.3.3-7.3.4):**
  - SimPO referanssızdır. Uzunluk-normalize ödül (`α/|y|·log π(y|x)`) ve marj `γ` kullanır, böylece eğitimi çıkarım metriğiyle hizalar.
  - R-DPO uzunluğu ödülden `α|y|` ile çıkarır.
- **NPO, D²O (§7.2.5):** Yalnız olumsuz örnek kullanır. NPO, gradyan çıkışının yıkıcılığını yavaşlatır. D²O olumlu tarafı modelin kendi üretimiyle değiştirir.
- **f-DPO (§7.3.2):** Ters KL ödülü yüksek, çeşitliliği düşük tutar. JS ve ileri KL daha çeşitlidir. JS, ters KL'nin ödülünü yakalar.

**SFT ile birleştirme (§7.4).**
- *Veri birleştirme:*
  - ORPO.
  - UFT: SFT çiftini `r_max` puanlı örnek sayıp UNA MSE ile karışık veri kümesinde eğitir.
  - RRHF/PRO: `J = J_SFT + α J_align`.
- *Model birleştirme:* **PAFT**, SFT ve DPO'yu aynı ön-eğitimli modelde **paralel** LoRA olarak eğitir. Sonra TIES gibi bir yöntemle birleştirir.
  - Gözlem: DPO delta'ları doğal olarak seyrek, SFT delta'ları değil. Bu yüzden birleştirmede girişim olur.
  - Çare: SFT kaybına `λ‖δ_sft‖₁` eklemek.
- Gerekçe olarak "alignment tax" anılır: ardışık SFT → hizalama, SFT'de kazanılan yeteneği unutturur.

**GRPO ve çevresi (§2.5, §5).**
- `A = (r − μ_grup)/σ_grup`. Avantaj cevap düzeyindedir ve her token'a aynı verilir.
  - KL, PPO'nun aksine ödüle gömülmez. Ayrı ve kırpılmamış bir terimdir (Schulman k3 kestirimcisi).
  - Rollout başına tek gradyan adımı atılır.
- **RLOO:** Baz çizgisi, kendisi hariç grup ortalamasıdır. σ = 1.
- **Dinamik örnekleme (DAPO, ProRL, Reinforce-Rej; §5.4.2, §5.5.1):** Tüm cevapları aynı ödülü alan istemler atılır, çünkü avantaj sıfırdır ve sinyal yoktur. Reinforce-Rej'in savı, GRPO'nun REINFORCE'a üstünlüğünün normalizasyondan değil bu süzmeden geldiğidir.
- **DAPO'nun diğer parçaları:** Clip-higher (`ε_high > ε_low`), token düzeyi kayıp (`1/Σ|y_i|`) ve aşırı uzunluk ödül biçimlendirmesi.
- **ProRL (§5.5.1):** Sabit referansa göre birikimli KL, yüzlerce adım sonra amaca baskın olur. Çare, referans ilkesini periyodik olarak güncel anlık görüntüye sıfırlamaktır.
- **Entropi (§5.5.2):** Entropi çöküşü erken RL'de yaygındır.
  - MAGIC eşik tabanlı uyarlamalı entropi bonusu kullanır.
  - "Entropy perspective" yaklaşımı avantaja kırpılmış, ayrık (detached) bir entropi terimi ekler.
  - KL'siz yöntemler (DAPO, Dr. GRPO) kırpma ve süzmeyle idare eder.
- **Çoklu ödül (§5.3.1-5.3.2):** Ödülleri toplayıp sonra grup normalizasyonu uygulamak, farklı bileşen birleşimlerini aynı avantaja çökertir ("reward collapse").
  - **GDPO** her ödülü ayrı normalize edip toplar, sonra yığın düzeyinde yeniden normalize eder.
  - BNPO bileşen başına Beta normalizasyonu yapar.
- **Uzunluk/biçim (§5.2.2):**
  - Uzunluk cezalı ödül erken ve ani doğruluk çöküşü getirebilir (GRPO-λ).
  - Yalnız doğruluk ödülü en doğru biçimi (uzun CoT) tek biçime çöktürür. Ada-GRPO bunu biçim sıklığıyla ters orantılı, kosinüsle sönümlenen ödül ölçeğiyle düzeltir.
  - GRPO-LEAD yanlışa −1 vererek tahminle şanslı doğruyu caydırır.
- **Hibrit SFT+RL (§2.6, §5.2.8):**
  - HPT, istem başına grup ortalaması `μ(x) > κ` ise RL, değilse SFT kaybını kullanır. Gerekçe: model hiç doğru üretemiyorsa RL çöker, SFT ise keşfi bastırır.
  - SRFT demonstrasyonu rollout grubuna katar ve SFT ile RL ağırlıklarını entropiyle dengeler.

**Ödül modelleme ve suistimal (§2.4.3, §6, §8).**
- Ters KL "zero-forcing"dir. `π_θ` referansın desteği dışına çıkınca sonsuza gider. Ödül suistimalini ve dejenere çıktıyı bastıran sabit çıpa budur (§2.4.3).
- Anthropic RLHF'de politika "train" ödül modeline karşı eğitilir ve ayrı bir "test" ödül modeliyle ölçülür. Yüksek ödülde ikisi ayrışır, yani aşırı eniyileme ölçülebilir. Ödül yaklaşık `√KL` ile doğrusal artar.
- **OpenAI RBR (§6.2):** Güvenlik davranışları önermelere (ikili ifadeler) ayrılır. Hakem LLM her önermeyi sınıflar. Ağırlıklar sıralı sentetik veriyle uydurulur ve `r_tot = r_RM + r_rbr` olur.
  - Bulgu: yalnız yardımseverlik ödül modeli "iyi red" ile "kötü red"i ayıramıyordu, RBR ayırdı.
  - Davranış sınıfları: sert red, yumuşak red, uyma.
- **Constitutional AI (§6.2):** Hedef "zararsız ama kaçamak olmayan" davranıştır. Modelin her şeyi reddetmesine karşı açıkça tasarlanmıştır.
- **§8 açık soruları:**
  - Hakem ve ödül modelleri uzunluk ve biçim kısayolu öğrenir.
  - Politika iyileştikçe hakemin dağılımı eskir.
  - Değerlendirmede aşırı red ve kalibrasyon dahil asgari eksenler gerekir.
  - Doğrulanabilir ödülün matematik/kod dışına nasıl genişleyeceği belirsizdir.

**Çevrimiçi ↔ çevrimdışı (§6.3, §7, §8).**
- Yinelemeli DPO, güncel politikadan cevap üretip çift kurarak DPO'yu çevrimiçileştirir. Örnekler: RSO (ödül modeliyle reddetme örneklemesi), Self-Rewarding, Meta-Rewarding (hakemi de eğitir) ve CRINGE.
- Nash-tabanlı yöntemler (NLHF, SPPO, DNO) skaler ödül yerine kazanma olasılığı kullanır.
- Açık soru (§8): Yinelemeli çevrimdışı DPO hangi koşulda çevrimiçi RLVR ile aynı politikaya yakınsar?

## HakHukuk için somut uygulamalar

Her madde için makale bölümü ve aşama verilmiştir. Makalede olmayan çıkarımlar **[çıkarım]** ile işaretlidir.

### A. Makale 1: birlikte-eğitim kolunun kayıp tasarımı (RQ1)

**A1. Temel kayıp: iki veri akışı, tek koşu, toplanmış kayıp** (§7.4.1 ORPO; §7.1.1 SLiC-HF; §7.1.3 RRHF/PRO; aşama: Makale 1, birlikte-eğitim kolu).
`L = L_SFT(raft_scrubbed) + λ · L_ORPO(orpo_abstain_cp2c çiftleri)`.

ORPO'nun kendi kaybı seçilen cevap üzerinde zaten NLL içerir (§7.4.1 denklemindeki `log π(y_w|x)`). Bu yüzden "SFT + ORPO" iki NLL kaynağına sahip olur: RAFT cevapları ve çekinme cevapları.

Açık bırakılmaması gereken karar: ORPO'nun iç NLL'si korunur mu, yoksa yalnız odds-oran terimi mi alınır? Makale ikisini ayırt eden bir deney sunmaz. Bu **DEV'de iki yapılandırma** olarak denenmeli. Yol haritasının "her temel modelde DEV'de ikişer yapılandırma" kuralıyla uyumludur.
- *Yapılandırma I:* tam ORPO (iç NLL dahil) + RAFT SFT.
- *Yapılandırma II:* yalnız `λ log σ(log OR)` + RAFT SFT. Çekinme cevabının NLL'si çıkarılır. **[çıkarım]**

**A2. Kayıp ağırlığı `λ` ve karışım oranı** (§7.4.1; §7.1.1 SLiC-HF `λ_sft`; PRO `α`).
- Makale her yöntemde tek bir skaler ağırlık gösterir ve değer önermez.
- Ölçülmesi gerekenler: `λ` ve iki veri akışının yığın içi oranı.
- Mevcut `τ_a` rejimindeki `beta 0,1`, ORPO'nun `λ` ağırlığına karşılık gelir. [makale dışı bilgi: TRL `ORPOConfig` adlandırması, makale bu eşlemeyi yapmaz]
- SFT ile birlikteyken aynı değer geçerli sayılmamalıdır. İki yapılandırmalık DEV bütçesinde tek bir `λ` ekseni (örn. 0,1 ve 0,3) yeterli olur.

**A3. UFT yedek olarak kalsın, kolu olmasın** (§7.4.1 UFT).
- UFT, SFT örneklerini `r_max` puanlı örnek sayıp UNA MSE kaybında tek akışta eğitir. Ancak **referans model** ister (`β log π_θ/π_ref`).
- `τ_a` hattı referanssız ORPO kullandığı için UFT yeni bir kayıp ve referans maliyeti getirir.
- Öneri: Makale 1 kapsamına almamak. Hakem yorumunda "neden başka birleşik kayıp yok" sorusu gelirse savunma notu olarak tutmak (Rule of Three).

**A4. Ardışık kol için çift kaynağı** (§6.3 yinelemeli DPO/RSO; §7.1.1 SLiC-HF sample-rank, sDPO).
- Ardışık kolda ORPO aşamasının "reddedilen" tarafı **ham modelin** hatalarıdır. Bu aşamada eğitilen politika ise `τ_g` uygulanmış modeldir.
- Makalenin dayandığı ilke: çiftler eğitilen politikanın kendi dağılımından geldiğinde eğitim daha kararlıdır.
- Yol haritası "aynı veriyle" karşılaştırma kuralını koyduğu için varsayılan olarak çiftler değişmez.
- Öneri: ardışık kol için **tek ek DEV yapılandırması** olarak, `τ_g` modelinin aynı tuzaklarda ürettiği hatalarla yeniden kurulan çiftleri denemek. Sonuç eke konur, ana tabloya alınmaz. **[çıkarım; adillik gerekçesiyle ana tabloda aynı veri korunur]**

**A5. Birleştirme kolu için PAFT hipotezi** (§7.4.2 PAFT).
- PAFT'ın temel savı: SFT delta'ları seyrek olmadığı için TIES'te girişim olur. Çare, SFT adaptörüne L1 eklemektir.
- Projedeki B4 bulgusu ("`τ_a` merge'de seyreliyor, 0,987 → 0,766", ADR-0075) bu savla uyumlu bir **açıklama adayıdır**, kanıtı değildir. Makale yalnız DPO delta'larının seyrek olduğunu bildirir. ORPO için aynı ölçüm yapılmamıştır.
- Ucuz test (eğitim gerekmez, eldeki `tg_v1` ve `ta_v1` adaptörleri): `τ_g` ve `τ_a` için büyüklük ve seyreklik istatistikleri. ‖τ‖ zaten raporlanıyor.
- Ardından yalnız DEV'de `τ_g`'ye L1 ekli yeniden eğitim denenebilir.
- Dikkat: CLAUDE.md birleştirme hattının `v1`'de dondurulduğunu söyler. L1'li kol ürün kararını değil, Makale 1'in "ayrı kollar + ham TIES" satırının yorumunu besler. Yalnız RQ1'in açıklayıcı bir ablasyonu olarak anlamlıdır.
- Önerilen öncelik: seyreklik ölçümü (maliyetsiz) evet. L1 yeniden eğitimi yalnız ölçüm destekliyorsa.

**A6. `rewards/accuracies ≤ 0,5` ama davranış yükseliyor: tanı eksenleri** (§7.3.3 SimPO; §7.3.4 R-DPO; §7.1.1 DPOP, IPO).
- Makale ORPO'nun `rewards/accuracies` metriğini yorumlamaz. İlgili ilke yalnızca şudur: tercih kayıpları log-olasılığı uzunluk ve ölçeğe duyarlı biçimde karşılaştırır. SimPO ve R-DPO bu yüzden uzunluk düzeltmesi ekler.
- Projede seçilen cevap (çekinme) kısa, reddedilen (gerçek hatalı cevap) uzundur.
- Hipotez: doğruluk metriği, çiftin iki tarafı arasındaki uzunluk farkıyla karışıyor. Bu yüzden davranışsal ölçüm (0,803 → 0,984) tek doğru ilerleme göstergesidir. **[çıkarım]**
- Öneri: birlikte-eğitim kolunda `rewards/accuracies` yerine şunlar birlikte kaydedilsin:
  - (a) Seçilen cevabın mutlak log-olasılığı (DPOP'un izlediği nicelik).
  - (b) Odds-oran marjı.
  - (c) Çekinme davranış oranı (DEV).
- Böylece DPOP'un işaret ettiği "tercih edilenin olasılığı da düşüyor" riski ve IPO'nun işaret ettiği "deterministik tercihte marj sonsuza kaçıyor" riski gözlenebilir olur.

### B. `τ_a` tarifi: ne korunur, ne sınanır

**B1. Korunacak:** Referanssız ORPO, 726 çift, reddedilen = temel modelin aynı tuzakta ürettiği gerçek hata. Makale bu tasarımı destekler. Modelin kendi hatalarını olumsuz örnek yapmak çevrimiçi-benzeri çift kurmaktır (§6.3 RSO, §7.1.1 SLiC-HF sample-rank). Olumsuz-yalnız yöntemler (NPO, D²O; §7.2.5) kendi üretimini çapa alır.

**B2. Sınanabilir tek sapma (öncelik düşük):** Uzunluk düzeltmesi (SimPO tarzı ortalama log-olasılık, §7.3.3) veya marj.
- ORPO'da odds-oran zaten `π(y)` olasılığıyla çalışır. Uzunluk yanlılığı olup olmadığı makalede incelenmez.
- Davranış sonucu iyiyken tarifi değiştirmek için gerekçe yoktur (CLAUDE.md: reçete değişikliği yeni versiyon açar).
- Bu madde yalnız A6'daki tanı bir uzunluk karışıklığı gösterirse açılır.

**B3. Eşleşmemiş veri seçeneği (gelecek iş):** Altın-bağlamda-yok durumlarında "istenen = çekinme" etiketini çift olmadan vermek gerekirse KTO (§7.1.2) çift kurma ihtiyacını kaldırır. Mevcut 726 çift bu ihtiyacı karşıladığı için şimdi uygulanacak bir şey değildir.

### C. Makale 2: GRPO ödül ve ablasyon tasarımı

Aşama: ADR-0075 ve yol haritası §3.

**C1. Ödül bileşenlerini ayrı normalize et (GDPO)** (§5.3.2).
- Ödülü tek skaler toplayıp grup σ'sine bölmek, farklı bileşen birleşimlerini aynı avantaja çökertebilir.
- Projedeki ödülün bileşenleri (isabet, uydurma cezası, çekinme) bu yüzden **ayrı ödül fonksiyonları** olarak hesaplanmalı. GDPO biçiminde birleştirilmeli: her biri kendi `μ_n, σ_n` ile normalize, toplam, sonra yığın normalizasyonu.
- Ablasyon için ek yarar: "isabet terimsiz" ve "çekinme terimsiz" kollarında bir bileşeni sıfırlamak kalan bileşenlerin ölçeğini değiştirmez. Toplam-sonra-normalize edilirse değiştirir ve ablasyon iki şeyi birden değiştirmiş olur. **[çıkarım]**

**C2. Dinamik örnekleme zorunlu sayılmalı** (§5.4.2 DAPO; §5.5.1 ProRL; Reinforce-Rej; §3 ödül tabanlı süzme).
- Grubundaki tüm cevaplar aynı ödülü alan istemler sinyal vermez.
- Ablasyon kollarında bu daha da önemlidir. "İsabet terimsiz"de altın bağlamda olan istemlerde uydurma yapmayan her cevap aynı ödülü alır. "Çekinme terimsiz"de altın bağlamda olmayan istemlerde sıfır varyans olasılığı artar.
- Öneri: ödül şartnamesine, grup başına sıfır-varyans oranını her koşuda kaydetmeyi ve süzme eşiğini ön-kayda yazmayı ekle. Yol haritası §3.2'nin ADR şartıyla uyumludur.

**C3. Çekinmenin çöküşü, iki yönde** (ADR-0075 Karar 4).
- *"Hep sus" çöküşü* (aşırı red):
  - Altın varken susmaya −, altın yokken susmaya + verilmesi bunu hedefler.
  - Makale bu çöküşü doğrudan ele almaz. İlgili ilkeler GRPO-LEAD'in "yanlışa −1" ayrımı ve Ada-GRPO'nun tek biçime çöküşe karşı ters-sıklık ölçeğidir (§5.2.2). **[çıkarım: ikisi de uzunluk/biçim içindir, çekinme için değil]**
- *"Hiç susma" çöküşü* (ADR-0010: düz SFT çekinmeyi yok etti):
  - Karşılığı HPT/SRFT geçididir (§2.6, §5.2.8). `μ(x) ≤ κ` olan istemlerde, yani model altın yokken hiç susmuyor ve grup ödülü sıfır sinyal veriyorsa, RL yerine **ORPO/SFT kaybı** uygulanır. Böylece çekinme sinyali gradyan boşluğuna düşmez.
  - Makale HPT'yi doğruluk ödülü için tanımlar. Çekinme için kullanmak **[çıkarım]**.
  - Ek kod gerektirdiği için ancak pilot "altın yokken susma" istemlerinde sıfır sinyal gösterirse eklenmeli.

**C4. KL çıpası** (§2.4.3 ters KL zero-forcing; §5.5.1).
- Referans, kazanan modeldir.
- Makalenin argümanı: KL'siz yöntemler (DAPO, Dr. GRPO) kırpma ve süzmeye güvenir. ProRL ise KL'li yöntemin birikimli KL ile tıkandığını gösterir.
- Proje için güvenli varsayılan: KL tutulur (çekinme çöküşü ana risk) ve `β` küçük seçilir. Pilotta KL ve entropi izlenir. Durma kuralına KL tavanı ve entropi tabanı yazılır.
- ProRL tarzı referans sıfırlaması yalnız uzun koşuda (birkaç yüz adımdan fazla) tıkanma görülürse devreye alınır. Küçük (250-500 adım) planda gerekmez. **[çıkarım]**

**C5. Suistimal gözlemi: eğitim ödülü ile ayrı ölçüm** (§2.4.3 Anthropic train/test PM; §8 hakem kısayolları).
- Makale, ödül modeli olan RLHF için eğitim PM'si ile ayrı test PM'sini ayırmayı gösterir.
- Projede ödül hakemsiz ve deterministiktir, ölçüm tarafı hakem panelidir (CLAUDE.md dört katmanlı savunma). Bu ayrım zaten aynı ilkeyi taşır.
- Öneri: koşu boyunca eğitim ödülü ile DEV'deki hakemli ölçümü (kütle, sızıntı, aşırı red) yan yana çiz. Ayrışma suistimal sinyalidir ve durma kuralının girdisi olur. Hakemli ölçümün ödül eğrisinden ayrıştığı ilk adım kaydedilsin.

**C6. Çevrimdışı alt çizgi: çevrimiçi RFT** (§2.2.2-2.2.3 RFT/Online RFT; §6.3 RSO).
- ADR-0066'nın "reddetme örneklemesi" önerisi makalenin RFT'sidir (`GC = I(y=y*)`, yalnız doğru olanlar). GRPO'nun fazlası negatif örnek ve baz çizgisidir.
- Ucuz bir alt çizgi kolu olarak, aynı rollout'lardan yalnızca ödülü pozitif olanları SFT ile eğitmek, GRPO'nun getirisini negatif sinyalden ayırmak için bilgilendiricidir.
- Planlanan bütçe (3 seed + 2 ablasyon) bunu kapsamıyor. Yalnız pilot verisinden bedelsiz çıkarılabiliyorsa ekle.

**C7. Düşünme bütçesi ödülü** (§5.2.2 DAPO aşırı uzunluk biçimlendirmesi; GRPO-λ erken çöküş uyarısı).
- Düşünme 1024 token'da zorla kapanıyor (CLAUDE.md rejimi).
- Makale, uzunluk cezasının ani doğruluk çöküşüne yol açabileceğini bildirir.
- Öneri: düşünme uzunluğuna ödül terimi **ekleme**. Yol haritası §3.3'ün "Türkçe iz için ayrı ödül terimi ön-kayıtta karara bağlanır" maddesinde de aynı uyarı korunmalı: yeni bir ödül terimi, yeni bir çöküş yolu açar.

### D. Yol haritasına eklenmeye değer maddeler (özet)

| # | Madde | Bölüm | Hedef |
| :-- | :-- | :-- | :-- |
| 1 | `rewards/accuracies` yerine seçilen cevap log-olasılığı + odds-oran marjı + davranış oranı izle | §7.1.1 DPOP/IPO, §7.3.3 | Makale 1 birlikte-eğitim izleme |
| 2 | `τ_g` ve `τ_a` seyreklik/büyüklük ölçümü (PAFT hipotezi), gerekirse yalnız-DEV L1'li `τ_g` | §7.4.2 | Makale 1 RQ1 yorumu |
| 3 | GRPO ödülünü bileşenlere ayır, GDPO biçimi normalizasyon | §5.3.2 | Makale 2 ödül ADR'si |
| 4 | Sıfır-varyans grup oranı kaydı ve dinamik örnekleme eşiği ön-kayıtta | §5.4.2, §5.5.1 | Makale 2 ön-kayıt |
| 5 | Çekinme için HPT tarzı geçit (yalnız pilot gradyan boşluğu gösterirse) | §2.6, §5.2.8 | Makale 2 pilot sonrası |

## Aktarılamayanlar / çekinceler

- **Derleme makalesi, deney yok.** Hiçbir öneri bu makalede ölçülmüş bir sonuca dayanmaz. Makale her yöntemi kendi kaynağının iddiasıyla aktarır. Proje kuralı (ADR-0075): "RL daha iyi sonuç verir" ölçülmemiş bir hipotezdir.
- **ORPO tek denklem.** Makale ORPO'dan yalnız tanımını ve gerekçesini verir. `λ` seçimi, uzunluk duyarlılığı ve doğruluk metriğinin davranışla ilişkisi yoktur. A6 ve B2'deki uzunluk karışıklığı hipotezi **makalede yoktur**, **[çıkarım]**dır.
- **RLVR sonuçları matematik/kod, uzun düşünce zinciri ve çok daha büyük modeller içindir.** Çekinme, atıf doğrulama, RAG bağlamı, Türkçe ve 4B model + LoRA bu literatürün kapsamında değildir. DAPO/ProRL gibi sonuçların 4B LoRA rejimine aktarılması doğrulanmamıştır. Özellikle "KL'siz kararlı" bulguları uzun CoT içindir.
- **Çekinmeye özgü ödül tasarımı yok.** RBR (§6.2) sert/yumuşak red ve uymayı ayırır ama güvenlik bağlamındadır ("içerik politikası" ile "davranış politikası"). "Bağlamda altın var mı" koşullu ödülü, bu çerçevenin hukuk-RAG'a uyarlamasıdır. **[çıkarım]**
- **Makale dışı risk (not).** "Altın madde dahil birçok madde atıfla" tipi ödül suistimali (kapsama yoluyla isabet) makalede ayrıca tartışılmaz. Yol haritasındaki "başka gerçek maddeye 0/−" satırı bunu hedefliyor, ancak atıf sayısı sınırı veya kesinlik cezası ödül şartnamesinde açıkça yazılmalıdır. Bu bir hipotezdir, makale desteği yoktur.
- **Birleşik çerçeve bir tanımlama aracıdır, optimum bildirmez.** §8 bunu açıkça yazar: gradyan katsayısı eksenlerinin etkileşimi ve belirli bütçede en iyi birleşim bilinmiyor, yakınsama garantisi yok.
- **Çevrimiçi-çevrimdışı eşdeğerlik açık soru (§8).** Yinelemeli DPO'nun GRPO'yu ikame edip etmediğini bu makale cevaplamaz. ADR-0066'nın GRPO'yu ertelemesiyle uyumlu bir alternatif (yinelemeli ORPO/DPO) vardır, ama bu belgeden bir üstünlük çıkarılamaz.
- **Sürüm kayması.** Kaynağın tarihli bir derlemesi okundu. Atıf yaparken arXiv sürüm numarası kaydedilmeli.
