# Araştırma kaydı — #87 …

> **Ne bu:** Checkpoint 1'in F0 aşamasının devamı. Önceki dosya [`kronoloji-75-86.md`](kronoloji-75-86.md) 12 girdiye
> ulaştı (#75-#86); kural [`README.md`](README.md)'de. Çapa: `kronoloji-87-98.md#87`. **#88 F0.14'e ayrıldı (2026-10-17'de yazılmadı); yeni girdi #90'dan devam eder.**

| # | tarih | başlık | kanca |
| :-- | :--- | :--- | :--- |
| [87](#87) | 2026-10-16 | vLLM üretim gürültüsü: aynı Q4 ağırlığı vLLM'de 3,6 p düşük, koşudan koşuya ±2,25 p | G3 en şanslı çekilişte geçmişti · ölçüm llama.cpp'de kalır (ADR-0109) |
| [89](#89) | 2026-10-17 | Hakem faturası: kapalı modda fatura listenin 0,713'ü (önbellek); GLM-5.3-Flash ön ölçümü 0,65 p | ×1,6 kalktı · R3 uygulanır · bağlayıcı hakem kapalı (ADR-0113, ADR-0114) |

<a id="87"></a>
## #87 — vLLM üretim gürültüsü: aynı Q4 ağırlığı vLLM'de llama.cpp'den 3,6 puan düşük ve koşudan koşuya ±2,25 puan oynuyor; ölçüm llama.cpp'de kalır

**2026-10-16 · Modal A10, vLLM 0.30.0 · hakem `deepseek/deepseek-v4.1-flash-20260910`, `deepinfra/fp8`, hakemin düşünmesi açık
· kullanıcı onayları: t2 puanlaması "Evet, kapanıştan önce", ek ölçüm "Biraz daha ölç" (t3-t5), karar "Ölçüm llama.cpp'de
kalsın", kayıt "yeni girdi + yeni ADR" · karar [ADR-0109](../adr/kararlar-0064-0085.md#adr-0109) · kart #11** · kanıt:
`outputs/eval/f0/f016-vllm-pilot/` (`A10/q4-acilmis/` t1-t2 · `A10/q4-acilmis_u345/` t3-t5 · `puanlama/` · `puanlama/u2/` ·
`puanlama/u345/` · `kos-gurultu-u2.sh` · `kos-gurultu-u345.sh` · `birlestir.py`)

**1 · Neden.** [#86](kronoloji-75-86.md#86)'nın G3'ü (motor etkisi ≤ 0,6 puan) yalnız 1. üretim koşusunun (t1) puanıyla 0,18 puanda geçti. vLLM
aynı soruya her koşuda farklı cevap verdiği için (iki toplu koşu arasında 80'de 25 aynı) bu tek bir çekilişti; vLLM kodunun son
incelemesi bunu "üretim gürültüsü ölçülmedi" diye işaretledi.

**2 · Ölçüm.** Q4'ten açılmış ağırlıkla vLLM'de beş üretim koşusu: aynı 80 DEV sorusu, aynı dondurulmuş bağlam, aynı hakem
ayarı. t1 ve t2 üçer, t3-t5 birer hakem tekrarıyla puanlandı (hakemin kendi oynaması ±0,2-0,26 p, üretim oynamasından çok küçük).

| üretim koşusu | kütle | hakem tekrarı | A1 | kapsama | kesik | not |
| :-- | --: | --: | --: | --: | --: | :-- |
| t1 | 0,7496 | 3 | 0,7891 | 0,95 | 4/80 | #86'da G3'ü geçiren koşu |
| t2 | 0,7256 | 3 | 0,7638 | 0,95 | 1/80 | |
| t3 | 0,6936 | 1 | 0,7301 | 0,95 | 7/80 | **geçersiz** (kesik %8,75 > %5) |
| t4 | 0,7089 | 1 | 0,7462 | 0,95 | 1/80 | |
| t5 | 0,7001 | 1 | 0,7569 | 0,925 | 4/80 | |
| **vLLM, 5 koşu** | **0,7156** | | | | | ss **2,25 p**, uç iki koşu arası 5,60 p |
| **llama.cpp, referans** | **0,7515** | 5 | 0,8016 | 0,9375 | 0/80 | her koşuda aynı cevap ([#85](kronoloji-75-86.md#85)) |

**3 · Sonuç.** vLLM, aynı ağırlıkla llama.cpp'den **3,59 puan düşük** (5 koşunun ortalaması; standart hata 1,01 p, fark 3,6 standart
hata). t3 dışarıda bırakılırsa 3,04 puan. Tek koşunun oynaması ±2,25 puan; llama.cpp'de yalnız hakemden gelen oynamanın (±0,26 p)
~9 katı. t1 beş çekilişin en yükseğiydi; t2 ölçülseydi G3 2,59 puanla düşerdi.

**4 · Olay: hız sınırı ve bütçe.** t3-t5'in puanlamasında (24 süreç) DeepInfra'nın üst hız sınırına (429) takıldı: 4 parçada 5
kalem 8 yeniden denemeden sonra hakem hatası aldı (ikisinde sağlayıcı boş döndü). `birlestir.py`'nin tamlık kapısı birleştirmeyi
durdurdu, hatalı dosyadan sayı çıkmadı; yalnız o 4 parça yeniden puanlandı (ilk deneme `…ilk-deneme-429.txt`). Ayrıca #86'daki
`kos-parcali.sh`'ta parça başına bütçe sınırı varsayılan $5'tı, 48 süreçte fiilen ~$240 tavan demekti (gerçek harcama $1,58'de
kaldı); ek ölçümlerde parça başına $0,2'ye indirildi.

**5 · Karar (kullanıcı, [ADR-0109](../adr/kararlar-0064-0085.md#adr-0109)).** Seçim ve nihai ölçüm llama.cpp + Q4_K_M'de kalır; hız için makine
çoğaltılır ([ADR-0103](../adr/kararlar-0064-0085.md#adr-0103)). vLLM ölçümde kullanılmaz; yalnız GRPO'nun cevap üretimi için, Haziran 2027'de ayrı
ölçümle. [ADR-0107](../adr/kararlar-0064-0085.md#adr-0107)'nin 1. ve 3. maddeleri geri alındı; hasat zaten llama.cpp'de kalıyordu.

**6 · Maliyet.** Bu girdi: t2 puanlaması $0,78 · t3-t5 üretimi ~$0,2 · puanlaması $0,79 + yeniden $0,13. Pilotun toplamı (#86 dahil)
~$4,1 (sınır $5). Fatura: OpenRouter sayacı gecikmeli, Modal panelden okunmadı.

**Okuma:** nedeni bilinmiyor. Adaylar: ağırlıkların bf16'ya yuvarlanması (son inceleme ölçtü: değerlerin ~%97'si değişiyor, göreli
hata %0,17), aritmetiğin farkı (vLLM'de bf16 etkinlikler ↔ llama.cpp'de 8-bit tamsayı çarpım), doğrusal dikkat (GDN) çekirdekleri,
KV önbelleği hassasiyeti. vLLM'in daha uzun düşünmesi ve daha sık kesik üretmesi (1-7/80 ↔ 0/80) bununla tutarlı. Nedeni
araştırmak elendi: bulunsa bile koşudan koşuya oynama kalır.

**Ders.** *Kapıyı gürültülü bir motorda tek koşuya bağlamak, tek çekilişle gürültü ölçmektir* ([#85](kronoloji-75-86.md#85)'in dersinin üretim
tarafı). Ön-kayıtlı kapı doğru çalıştı ama yanlış soruya cevap verdi; belirlenimci olmayan bir motorun kapısı en az beş üretim
koşusu ister.

<a id="89"></a>
## #89 — Hakem faturası ölçüldü: kapalı modda fatura listenin 0,713'ü (önbellek); GLM-5.3-Flash ikinci hakem ön ölçümünü 0,65 p ile geçti; düşünmesi kapatılamıyor

**2026-10-17 · kart #74 · hakem DeepSeek V4.1 Flash (`deepinfra/fp8`, kapalı) ve GLM-5.3-Flash (`novita/fp8`, `dusuk`) ·
kullanıcı onayları: Durak 1 ("İşle" · Novita fp8 · R4 "Uygula, varsayılan kapalı" · "Geniş sınır"), GLM düzeyi "low düzeyle
ölç", Durak 2 ("İşle" × 3 · R3 "Koşu kuralı, kod yok") · "Kapalı mod şimdi seçilsin" · kararlar [ADR-0113](../adr/kararlar-0064-0085.md#adr-0113) ·
[ADR-0114](../adr/kararlar-0064-0085.md#adr-0114) · kod `3b46f54` · `89ef2f9` · `7529bf1`** · kanıt:
`outputs/eval/f0/k74-fatura-glm/` (`KUNYE.json` · `OZET.json` · `kos.sh` · `ozetle.py` · `r3_sirala.py` · `hesap_kullanimi.txt`)

**1 · Neden.** #74: yol haritasındaki hakem bütçesi (~$61-67) ölçümlerden önce yazılmıştı ve iki varsayımı tutmuyordu
(×1,6 fatura payı; "açık mod 2-3 kat"). Fatura hiçbir koşuda okunmamıştı (#86, #87 "fatura okunmadı").

**2 · Kod.** `groundedness.py` artık OpenRouter'ın her yanıtta döndürdüğü gerçek maliyeti, önbellekten okunan girdiyi ve
düşünce token'ını kaleme ve özete yazıyor (`fatura` bloğu; alan yoksa boş, eksik sayılır). Sonuç deposu (`--sonuc-deposu`,
varsayılan kapalı). GLM'in kimliği; GLM'de düşünme kapatılamadığı için `dusuk` modu.

**3 · Ölçümler** (girdi: F0.6'nın 80 DEV cevabı, sha256 `c5035eb3…bb7cd093`):

| koşu | kütle | fatura / liste | önbellek (girdi) | not |
| :-- | --: | --: | --: | :-- |
| DeepSeek kapalı, tek koşu | 0,7146 | $0,0363 / $0,0509 = **0,713** | %45 | F0.6 bandı 0,6993-0,7342 (ort ± 2 ss) içinde |
| R3 testi: A10 ↔ vLLM q4 t1 soru soru (160) | — | $0,0578 / $0,1043 | %72 | ikinci kolun doğrulama çağrısı %65 ↔ bugünkü sırada %37 |
| GLM `low`, 5 tekrar | 0,7268 (ort) | ~$0,020 / $0,024 | %20-41 | ss **0,65 p** (eşik 0,9) · aralık 1,80 p · DeepSeek kapalıdan +1,01 p |
| GLM `kapali`, 3 kalem | — | $0 | — | 3/3 400: "Reasoning is mandatory for this endpoint" |

Hakem hatası her koşuda 0; sağlayıcı her koşuda tek (DeepInfra · Novita). R1'in topladığı günlük tutar ($0,1956) OpenRouter'ın
günlük sayacıyla birebir ($0,195617; `GET /api/v1/key`).

**4 · Fatura ve geçmiş günler.**
- Gerçek maliyet = liste fiyatı, önbellekten okunan girdi önbellek fiyatından ($0,0042/M). OpenRouter'ın gösterdiği fiyattan
  indirim zaten düşülmüş: GLM'in altı uç noktasında taban × (1 − `discount`) = liste (ADR-0102'nin doğrulanmamış maddesi).
  Kapalı modda önbellek yalnız sistem istemini tutuyor (çıkarımda %61, doğrulamada %37).
- 15 Ekim: $1,234 fatura / $1,748 liste = 0,706; 16 Ekim: $3,199 / $3,143 = 1,018 (haftalık sayaç − 15 Ekim'in günlüğü). İki
  gün birlikte, kapalı mod 0,713 ve `gpt-4o-mini` ~0,9 düşülünce açık modun oranı **~0,92** (t). Günlük ayrım sayaç gecikmesiyle
  bozulmuş olabilir (v; #87 "sayaç gecikmeli"); 16 Ekim'de ayrıca kayda geçmemiş ~$0,13'lük yarım koşu var (#87 §4).
- Önbellek en az ~20 dakika yaşıyor: R3 testinin birinci kolu, ~20 dakika önce aynı cevapları puanlayan koşunun önbelleğinden
  %78 aldı.

**5 · Kararlar (karttaki önceden yazılı kurallarla).**
- **R3 uygulanır** (kural: bugünkü sırada doğrulamanın soru + kaynak kısmı önbellekten gelmiyor — %37 yalnız sistem istemi).
  Ölçülen kazanç: ikinci ve sonraki kollarda kapalı modda koşu başına ~%16 (t). Uygulama koşu kuralıdır, kod değişmez (kullanıcı kararı): aynı soru kümesinin kolları eş zamanlı ve aynı sırayla başlatılır, paralellik ≤ 10 (DeepInfra'nın hız sınırı, #87).
- **R4 uygulandı** (kural: aynı (soru, kaynak, cevap) üçlüsü mevcut 112 cevap dosyasında %25,7, eşik %10; F0 dosyalarında
  %40,9). Tekrarların çoğu aynı modelin yeniden üretimi (belirlenimcilik ve motor denemeleri), farklı kollar arasında aynı
  çekinme cümlesi %7,9 — kazanç F1-F3'te bu oranın altında kalabilir.
- **GLM kabul şartı (a) geçti** → ADR-0113. (b) insan uyumu #24'e, (c) kontrol kalemleri #25'e.
- **Bağlayıcı hakem kapalı modda** (kullanıcı kararı, [ADR-0114](../adr/kararlar-0064-0085.md#adr-0114)): bütçe ölçülen fiyatla yeniden hesaplanınca Checkpoint 1 hakem nakdi kapalı modda ~$28-31, açık modda ~$157-180 (t) çıktı; F1.4 insan uyumunu iki modda ölçer ve raporlar, modu belirlemez.

**6 · Dış bilgiler** (okundu 2026-10-17): GLM-5.3-Flash `z-ai/glm-5.3-flash-20260826`, ağırlık fp8, MIT (HF
`zai-org/GLM-5.3-Flash`); OpenRouter'da düşünme zorunlu, düzeyler low · high · max; Novita fp8 $0,084 / $0,28 (%44 indirimli,
taban $0,15 / $0,50). Kredi yükleme ücreti kartla %5,5, en az $0,80 (openrouter.ai/pricing; $5'lık yüklemede %16). Üretici
adayları: Kimi K3 `moonshotai/kimi-k3-20260715` $0,304 / $11,936, lisans MIT benzeri ($20M üstü hizmet geliri ve 100M
kullanıcı şartlı); MiniMax M3 `minimax/minimax-m3-20260531` $0,30 / $1,20, "MiniMax Community License": temel izin ticari olmayan
kullanım, ticari kullanımda "Built with MiniMax M3" ve bildirim. Bakiye: yüklenen $40, harcanan $28,35.

**7 · Duman testinde göze çarpan.** DEV id 1'de GLM, kaynakta olmayan bir çıkarımı (ilk derece mahkemesi kararı ↔ kaynağın
düzenlediği bölge adliye kararı) desteklenmiş saydı; DeepSeek bunu F0.6'nın 5 koşusunda ve bugün yakaladı. Tek kalem;
kontrol kalemlerinde (F1.5) ölçülecek.

**8 · Maliyet.** Bu girdinin koşuları $0,196 (fatura).

**Ders.** *Faturayı okumadan yazılan bütçe, ölçüm değil varsayımdır.* ×1,6 payı başka bir kapının marjından gelmişti
(#64); OpenRouter'da marj yok, asıl belirleyen önbellek. Ayrıca *bir modelin "kapalı modu" olduğunu varsaymak* — 3 kalemlik
duman testi bunu paradan önce yakaladı.
