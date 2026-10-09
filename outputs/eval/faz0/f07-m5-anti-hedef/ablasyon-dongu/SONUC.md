# M5 döngü kaldıracı — ablasyon sonucu (2026-09-07)

**Bedel: $0** — yerel GPU, **hakem çağrılmadı**. Döngü tespiti **deterministik**
(kuyruk n-gram tekrarı), hüküm için para gerekmedi.

**Kurulum:** 5 "suçlu" kalem (resmî koşuda `finish_reason=length` olanlar) · aynı GGUF
(`tgta_v1-q4_k_m`) · aynı seed 3407 · aynı bütçe 1536 · aynı istem · **değişen yalnız
sunucunun örnekleme bayrakları**.

## ✅ Kontrol kapısı — alt küme çıpayı üretiyor mu?

**5/5 BAYT-BAYT AYNI.** Alt küme, 80 kalemlik resmî koşunun bu beş kalemini birebir
yeniden üretti (146 ↔ 146 · 1791 ↔ 1791 · 1667 ↔ 1667 · 2040 ↔ 2040 · 3 ↔ 3 karakter).
⇒ Diğer kolların farkı **kola aittir**, alt küme kurulumuna değil.

## Sonuç

| kol | sunucu bayrağı | kesik | döngü | ort token |
| :--- | :--- | ---: | ---: | ---: |
| `kontrol` | — *(bugünkü rejim)* | **5/5** | **3** | 1843 |
| **`dry`** | `--dry-multiplier 0.8 --dry-base 1.75 --dry-allowed-length 2` | **0/5** ✅ | **0** ✅ | 1553 |
| `rep11` | `--repeat-penalty 1.1` | 1/5 | 0 | 1508 |

Kontrol kolundaki döngü uzunlukları: id 28 **×21** · id 74 **×19** · id 54 **×82**.

**Hüküm: DRY.** İkisi de döngüyü kırıyor; DRY kesikliği de sıfırlıyor.

### DRY neden bu iş için doğru araç
```
ceza = çarpan × taban^(eşleşen_dizi_uzunluğu − serbest_uzunluk) = 0,8 × 1,75^(n−2)
```
Tekrarlanan **dizinin uzunluğuyla üstel** büyür ⇒ 2 token'a kadar tekrar **serbest**.
Hukuk metninde *"madde"*, *"kanun"*, kanun numaraları **meşru olarak** tekrarlar ve ceza
almaz; 20+ token'lık döngü anında ezilir. `repeat_penalty` ise yakın penceredeki **her**
token'ı bağlamına bakmadan cezalandırır — bu alanda yan hasarı vardır.

⭐ **Determinizm korunuyor:** iki ceza da logit'i **seçimden önce** değiştirir, yani
`temperature=0` bozulmaz ve koşu seed ile yeniden üretilebilir kalır. `temp 0.6` (#42'nin
yarısını kurtaran çare) bunu **bozardı** — ucuz kaldıraç aynı zamanda metodolojik olarak
temiz olan.

## 🚨 Ama ölçümün ANLAMI değişiyor — bu şerh sayıdan ayrılamaz

DRY modeli **doğru** yapmadı, **akıcı** yaptı. Kör modda üretilen cevaplar artık tam ve
akıcı — ve **yanlış**:

| id | altın | DRY'nin atfı | |
| :-- | :--- | :--- | :-- |
| 3 | İŞ K. **31** | *"4857 – **35. ve 36.** Maddeler"* | ❌ yanlış madde |
| 2 | İİK **79/a** | *"**110.** Madde"* | ❌ yanlış madde |
| 4 | KMK **33** | *"Kanun No **633**, **10.** Madde"* | ❌ yanlış kanun **ve** madde |
| 1 | TBK **230** | *"**6502** Sayılı Tüketicinin Hakları Kanunu"* | ❌ tamamen yanlış kanun |

`repeat_penalty` kolu da aynı sınıf (İş K. *"Madde 40"* · KMK *"Madde 10"*).

M5'in **ölçmek için var olduğu şey budur**: kaynak verilmeyince model kendinden emin,
akıcı ve yanlış hukuk üretir. Ama ölçüm açısından sonucu şu: **döngü kalemi ile
akıcı-yanlış kalem hakemden aynı notu almaz.** DRY yalnız kesikliği düzeltmiyor, M5
sayısının **neyi ölçtüğünü** de değiştiriyor ⇒ DRY'li M5 ile DRY'siz M5 **aynı birimde
değildir** ve kıyaslanamaz.

## ⛔ Buradan sonrası İNSAN KARARI

DRY'yi M5'in ölçüm rejimine almak **yeni bir rejim kararıdır**:
- ADR-0057 (eşit sınav): rejim değişirse **bütün kollar** aynı rejimde koşulmalı
- ADR-0050: kapı **oynatılmıyor** — sorulan şey **aletin** değişip değişmeyeceği
- Bedeli: bizim kol + base çıpası **yeniden** (~40 dk GPU, **$0**) + hakem (~**$0,08**)

Ürün tarafında (Hat A / A2) DRY'nin **açık olması** ayrı ve daha kolay bir karardır —
orada kıyas yükümlülüğü yoktur. Bkz. spec §5 *"A2'nin üretim ayarları"*.
