# F0.3 — 80 kalemin GÖZLE OKUNMASI (kapı adımı)

**Tarih:** 2026-09-06 · **koşu:** `h1_tgta_v1_f02_nb` (v2 soru · `RRF_K=10` · önsözsüz · bütçe 1536)
**Neden kapı:** 2026-09-06'da sayısal kapı (`0,1733 > 0,10`) bozuk ölçümü **geçirdi**; yakalayan
şey bu adımdı. Önceki turda alet 14 aşırı-red demiş, göz **8** bulmuştu (6 yanlış pozitif).

## 1 · Çekinme ekseni — alet ↔ göz farkı **SIFIR**

Alet (`exact_reject`, mode=data) **5/80** dedi. Beşi de tam metin okundu:

| id | altın | altın sırası | göz hükmü |
| :-- | :--- | ---: | :--- |
| 15 | TMK 398 | 5 | ✅ gerçek çekinme → **aşırı-red** |
| 37 | TMK 398 | 1 | ✅ gerçek çekinme → **aşırı-red** |
| 45 | TKHK 73 | 1 | ✅ gerçek çekinme → **aşırı-red** |
| 66 | TKHK 66 | 1 | ✅ gerçek çekinme (gerekçeli red) → **aşırı-red** |
| 79 | TCK 103 | **gelmedi** | ✅ **DOĞRU davranış** — altın bağlamda yok, susmak doğru |

**Ters yön de tarandı:** aletin *"cevapladı"* dediği ama red ibaresi taşıyan **7 kalem**
(id 2 · 6 · 18 · 36 · 48 · 67 · 69) tek tek okundu — **yedisi de tam, atıflı cevap.**
Red ibaresi hepsinde *"**Diğer kaynaklar** … içermemektedir"* kalıbında, yani **eleme
gerekçesi**. Bu tam olarak ADR-0061'in yanlış pozitif üreten kalıbıydı; onarılmış dedektör
bunları doğru şekilde red saymıyor.

⇒ **yanlış pozitif 0 · yanlış negatif 0 · aşırı-red = 4/80 (çivilendi).**
⚠️ Örüntü: 4 aşırı-reddin **3'ünde altın madde 1. sırada** — erişim sorunu değil, **modelin
kendi kusuru** (B10'un çekirdeği).

## 2 · İsabetsizlik ekseni (B1) — **8/80**

⚠️ **ADR-0055'in ekseninde kod yok** (devir notu: *"eksen belirlendi, kod hiç açılmadı"*),
bu yüzden **75 cevaplanan kalemin tamamı** gözle tarandı: modelin dayandığı kaynak ilk cümlede
adlandırılıyor, o kaynak altın maddeyle karşılaştırıldı.

| id | altın | modelin dayandığı | not |
| :-- | :--- | :--- | :--- |
| 27 | KMK 33 | **KMK 25** | 🖊️ sorusu yeniden yazıldı |
| 29 | TKHK 49 | **TKHK 24** | |
| 30 | TBK 139 | **TBK 144** | |
| 32 | HMK 358 | **HMK 147** | kesik kalem |
| 36 | KMK 53 | **KMK 10/14** | |
| 41 | İİK 31 | **İİK 26** | |
| 42 | TBK 217 | **TBK 214** | 🖊️ sorusu yeniden yazıldı |
| 61 | CMK 158 | **AVUKATLIK KANUNU 60** | yanlış madde değil, **yanlış kanun** |

### ⭐ Metodoloji bulgusu: iki otomatik süzgecin de tek başına YETMEDİĞİ ölçüldü

| süzgeç | bulduğu | kaçırdığı |
| :--- | ---: | :--- |
| `faithfulness < 0,6` | 4 | 27 · 36 · 41 (faith 1,00 · 1,00 · 0,67) |
| altın madde atıflarda yok | 3 | 29 · 30 · 42 · 61 (cevap altını **başka yerde anıyor**) |
| **gözle tam tarama** | **8** | — |

⇒ B1 ekseni için otomatik bir vekil metrik **yoktur**; bu, borcun neden hâlâ açık olduğunun
mekanik açıklamasıdır ve B1 turu tasarlanırken bilinmelidir.

### ⚠️ Öz-denetim: 2/8 isabetsizlik BENİM yazdığım sorularda

| id | eski soru | yeni soru | mekanizma |
| :-- | :--- | :--- | :--- |
| 27 | *"Mahkeme hangi kurallara göre karar verir?"* | *"Kat maliklerinden biri **yükümlülüğünü yerine getirmediği** için…"* | ifadem **KMK 25'in açılışına** yakın (*"kendisine düşen borçları ve yükümleri yerine getirmemek suretiyle"*) |
| 42 | *"Ürünüm elimden alınırsa…"* | *"Satın aldığım mal **üçüncü bir kişi tarafından elimden alınırsa**…"* | ifadem **TBK 214'ün** diline yakın |

**Bu, ADR-0067'nin yanlılık korumasının TERS yönde işlemesidir:** durumu tarif ederken komşu
maddenin dilini kullanmışım. Sayıyı şişirmedi — **aleyhimize** çalıştı (isabetsizliği yükseltti).
Sorular **düzeltilmiyor**: geri almak, eval sorusunu sonucu gördükten sonra ayarlamak olurdu.
⇒ Yeni kural adayı: soru yeniden yazılırken **komşu maddelerin metni de okunmalı** ve onların
ayırt edici ifadelerinden de kaçınılmalıdır. (ADR-0067'ye şerh.)

## 3 · Özet — çivilenen sayılar

| eksen | değer |
| :--- | ---: |
| aşırı-red (altın bağlamda sustu) | **4/80** — alet = göz |
| doğru red (altın yok, sustu) | 1/80 |
| **isabetsizlik** | **8/80** — gözle tam tarama |
| uydurulmuş madde | **0/114** |
| atıfsız geçen | 7 |
