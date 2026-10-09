# F0.5 — `SOURCE_CLIP` ödendi: `k` ekseni TANIMSIZ'dan çıktı

**Tarih:** 2026-09-07 · **karar:** insan (açık soru **S4** / borç **YB3**)
**Değişiklik:** `score_abstention.SOURCE_CLIP` **3500 → 12000**
**Gerçek bedel: $0,78** *(tahmin $0,30 — sapmanın sebebi aşağıda ve o sebep borcun kendisi)*

## Yeni değer neden 12000 — ölçümden türetildi, keyfî değil

| bağlam | ort | medyan | **max** | klip 3500'ü aşan | hakemin gördüğü ort oran |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `k=10` | 7.067 | 7.304 | **10.549** | **79/80 (%99)** | **%52** |
| `k=4` | 2.889 | 3.059 | 4.461 | 15/80 (%19) | %99 |

Gözlenen en büyük bağlam **10.549** + %14 pay = **12.000**.

## ⭐ Kusurun çıplak kanıtı

Eski koşuda `k=10`'un paydasının **65'i `gecerlilik_devralinan`**'dı — yani k=4'ün önbellek
kayıtlarından **devralınmıştı**. Sebep: k=4 bağlamı k=10'unkinin **öneki** ve anahtar
`sha256(soru + NUL + kaynak[:3500])` olduğu için ikisi **aynı kayda düşüyordu**.
⇒ `k=10`'un paydası kendi bağlamından değil, **k=4'ünkinden** geliyordu. TANIMSIZ damgası buydu.

Yeni kliple: `gecerlilik_devralinan = 0`, 80/80 kalem **kendi bağlamıyla** hükme bağlandı.

| eksen | k=10 eski | **k=10 yeni** | k=4 eski | **k=4 yeni** |
| :--- | ---: | ---: | ---: | ---: |
| `valid_traps` (payda) | 65 *(65 devralınmış)* | **62** *(0 devralınmış)* | 68 | **69** |
| `invalid_traps` | 15 | **18** | 12 | **11** |
| `rejection_rate` (Rej\*) | 0,723 | **0,726** | 0,735 | **0,739** |
| `rejection_exact` | 0,523 | **0,548** | 0,559 | **0,551** |
| `fabrication_rate` | 0,277 | **0,274** | 0,265 | **0,261** |
| `parametric_leak` | 0,215 | **0,210** | 0,132 | **0,130** |
| hakem maliyeti | $0,056 | **$0,522** | $0,257 | **$0,259** |

**Yön:** tam bağlamı gören hakem `k=10`'da **3 tuzağı daha geçersiz** sayıyor (65 → 62) —
beklenen yön: 10 kaynağın tamamını görünce *"kaynak soruyu cevaplıyor"* daha sık doğru çıkıyor.

## Maliyet sapması bir bulgudur

Tahmin $0,30 idi, gerçek **$0,78**. Sebep: eski koşuda `k=10` hakemi **neredeyse hiç
çağırmıyordu** (65/80 devralınmıştı, maliyet $0,056). Yeni kliple 80'i de çağrıldı ($0,522).
⇒ **Tahminin düşük çıkması, borcun tam olarak neyi gizlediğinin ölçüsüdür.**

## ⚠️ Damgalar

- `SOURCE_CLIP` hem **kör paydayı** hem **PAY hakemini** (`judge()`) besliyor ⇒ **3500 birimiyle
  üretilmiş TÜM tarihsel `verdict`/M2/M2b sayıları KIYASLANAMAZ.** Buna **ARA KAPI'nın eşiği
  (0,8649)** ve **merge M2b (0,766)** dâhildir.
- Eski özet dosyaları **silinmedi**: `*.ONCEKI-20260907` olarak duruyor.
- Önbellek ayrı dosyada: `_artefakt/valid_trap_kor_onbellek_clip12000.json` — eski önbellek
  (klip 3500) karışmasın diye devralınmadı.
- Bu koşu **v1 soru setiyle** üretilmiş h2b kollarında yapıldı (v2'de h2b hiç koşulmadı);
  amaç sayı üretmek değil **ekseni tanımlı kılmaktı**.


## 🆕 Yan etki, 2026-09-07'de fark edildi: bir TEST eski kusuru koruyordu

`tests/test_score_abstention.py::test_hakem_isteminden_TASAN_METIN_ANAHTARA_GIRMEZ`,
klip **3500** iken `k=4` ↔ `k=10` çakışmasını **değişmez olarak** doğruluyordu
(docstring: *"bedeli KABUL EDİLDİ… aleti değil damgayı taşıyoruz"*). Bu değişiklik o
bedeli **ödediği** için test düştü — ve **bu koşudan sonra `pytest` koşulmadığı için
görülmedi**; ancak ertesi gün T5'in taban ölçümünde ortaya çıktı.

**Düzeltme:** test **tersine çevrildi** — artık çakışmanın **yokluğunu** koruyor:
`gecerlilik_istemi(k4) != gecerlilik_istemi(k10)`. Değişmezin kendisi (*"klibi AŞAN fark
anahtara girmez"*) ikinci bir blokla **yerinde** tutuldu.

⚠️ **Ders:** aleti değiştiren bir ölçüm turu, o aletin **testlerini** de çalıştırmalı.
`SOURCE_CLIP` bir sabit değil, **davranış sözleşmesiydi**; sözleşmeyi değiştirmek onu
belgeleyen testi de değiştirmeyi gerektiriyordu.
