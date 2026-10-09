# M5 anti-hedef ölçümü — durum, 2026-09-07

## Zaman çizgisi

| ne | sonuç |
| :--- | :--- |
| 2026-09-07 01:05 · pilde başlatıldı | ⏸️ durduruldu — GPU 180 MHz'e kısılıyordu (4,8 saat) |
| 2026-09-07 08:12 · **şarjda** koşuldu | ✅ 80/80 üretildi, **21 dakika** (tahmin 57 dk) |
| geçerlilik kapısı (ADR-0040) | 🚨 **KALDI** — kesik **5/80 = %6,2 > %5**, `EXIT=2` |
| hakem | **çağrılmadı** — kapı parayı korudu |
| base çıpası | ⏸️ 2 kalemde durduruldu (bkz. aşağıda, `GECERSIZ-kesik6.2-drysiz/_YARIM_base_dry_yok.jsonl`) |

## Kapı neden kaldı — ve reçetesi neden uymuyor

Beş kesik kalem **gözle okundu** ([KESIK_GOZLE_OKUMA.md](KESIK_GOZLE_OKUMA.md)) ve
deterministik bir kuyruk-tekrarı dedektörüyle **bağımsız olarak doğrulandı**; ikisi **aynı
hükmü** verdi:

| id | kanun/madde | sınıf | kanıt |
| :-- | :--- | :--- | :--- |
| 27 | KAT MÜLKİYETİ K. 33 | bütçe kesilmesi | düşünce 1536'nın tamamını yaktı, cevap **3 karakter** (`"Kat"`) |
| 43 | CMK 174 | bütçe kesilmesi | cümle ortasında gerçek kesilme |
| 28 | TBK 230 | 🚨 **yozlaşmış tekrar** | ibare **×21** |
| 74 | İİK 79/a | 🚨 **yozlaşmış tekrar** | ibare **×19** |
| 54 | İŞ K. 31 | 🚨 **yozlaşmış tekrar** | *"askeri hizmet süresince"* **×82** |

ADR-0040 *"kesik > %5 → MAXTOK büyütülüp tekrar koşulur"* diyor. Bu **2 kalem** için doğru,
**3 kalem** için ölçülmüş biçimde **etkisiz**: `temperature=0` açgözlü kod çözmede döngüye
girmiş model matematiksel olarak çıkamaz — bütçeyi büyütmek **daha uzun bir döngü** üretir.
[#42](../../../docs/record/research_log/2026-07-29-cp0-dusunce-modu-sonlanmama.md) aynı sınıfta
bütçeyi **8× artırmış (4096 → 32768) ve hiçbir şey değişmemişti**.

⭐ **Belirleyici sayı:** üç döngü kalemi kırılırsa kesiklik **2/80 = %2,5** ⇒ **kapı geçilir**.

## Şu an koşan: döngü kaldıracı ablasyonu ($0, hakem YOK)

`ablasyon-dongu/` · 5 suçlu kalem · üç kol, **aynı GGUF, aynı seed, aynı bütçe**:

| kol | sunucu bayrağı |
| :--- | :--- |
| `kontrol` | yok — çıpayı yeniden üretir |
| `dry` | `--dry-multiplier 0.8 --dry-base 1.75 --dry-allowed-length 2` |
| `rep11` | `--repeat-penalty 1.1` |

✅ **Kontrol kapısı GEÇTİ: 5/5 bayt-bayt aynı** — alt küme çıpayı üretiyor, kollar okunabilir.

⭐ İki ceza katmanı da logit'i **seçimden önce** değiştirir ⇒ `temperature=0`'da çalışırlar ⇒
**determinizm ve seed ile yeniden üretilebilirlik korunur**. `temp 0.6` bunu bozardı.
⛔ `repeat_penalty` beklenti dışı: hukuk metninde madde numarası ve terim **meşru olarak**
tekrarlar; DRY tekrarlayan **dizileri** cezalandırır, ki döngünün deseni budur.

## ⛔ Açık kalan — İNSAN KARARI gerekiyor

Ablasyon DRY'nin döngüyü kırdığını gösterirse, M5'in ölçüm rejimine DRY eklemek
**yeni bir rejim kararıdır** (ADR-0057 eşit sınav: rejim değişirse kıyas kolları da değişir).
Kapı **oynatılmıyor** (ADR-0050); sorulan şey **aletin** değişip değişmeyeceği.
