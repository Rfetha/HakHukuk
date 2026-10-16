# Araştırma kaydı — #87 …

> **Ne bu:** Checkpoint 1'in F0 aşamasının devamı. Önceki dosya [`kronoloji-75-86.md`](kronoloji-75-86.md) 12 girdiye
> ulaştı (#75-#86); kural [`README.md`](README.md)'de. Çapa: `kronoloji-87-98.md#87`. **Yeni girdi #88'den devam eder.**

| # | tarih | başlık | kanca |
| :-- | :--- | :--- | :--- |
| [87](#87) | 2026-10-16 | vLLM üretim gürültüsü: aynı Q4 ağırlığı vLLM'de 3,6 p düşük, koşudan koşuya ±2,25 p | G3 en şanslı çekilişte geçmişti · ölçüm llama.cpp'de kalır (ADR-0109) |

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
