# Plan — kayıt katmanı kompaktlama

**Tasarım:** [`specs/2026-09-13-kayit-katmani-kompaktlama-design.md`](../specs/2026-09-13-kayit-katmani-kompaktlama-design.md)
**Geri dönüş noktası:** `301a82f` (temiz ağaç) · **Başlangıç:** 103 dosya · 1,40 MB · ~466 bin token

---

## Adım 1 — Çöp

- [x] 1.1 `docs/record/2026-09-10-hp-hat-a-hat-b-kapanan-gorevler.md` sil → *verify:* dosya yok
- [x] 1.2 `docs/record/sprint2/` sil → *verify:* dizin yok
- [x] 1.3 `docs/record/sprint1/` sil → *verify:* dizin yok
- [x] 1.4 `gemma4-12b-dersler.md` Bölüm C kesilir → *verify:* `grep -c '^## C' == 0`, Bölüm A ve B duruyor

## Adım 2 — `docs/adr/` birleştirme + damıtma

- [x] 2.1 `kararlar-0027-0044.md` (18 ADR, 2105 satır) → *verify:* 18 çapa (`<a id="adr-00NN">`) var
- [x] 2.2 `kararlar-0045-0063.md` (18 ADR, 2206 satır) → *verify:* 18 çapa var
- [x] 2.3 `kararlar-0064-0085.md` (22 ADR, 2704 satır) → *verify:* 22 çapa var
- [x] 2.4 58 tekil ADR dosyası silinir → *verify:* `ls docs/adr/[0-9]*.md` boş
- [x] 2.5 `adr/README.md` yeniden yazılır → *verify:* ≤ 100 B/satır, 58 satır dizin

## Adım 3 — `docs/record/` birleştirme + damıtma

- [x] 3.1 `kronoloji-39-52.md` (#39-#52) → *verify:* 14 çapa
- [x] 3.2 `kronoloji-53-62.md` (#53-#62) → *verify:* 10 çapa
- [x] 3.3 `kronoloji-63-71.md` (#63-#71) → *verify:* 9 çapa
- [x] 3.4 33 tekil log dosyası + `docs/record/` dizini silinir → *verify:* dizin yok
- [x] 3.5 `yurutme-tuzaklari.md` damıtılır → *verify:* **85/85 tuzak numarası duruyor** · ⚠️ **52 → 44 KB, `≤ 25 KB` TUTTURULMADI** (aşağıya bak)
- [x] 3.6 `record/README.md` yeniden yazılır → *verify:* ölü işaretçi yok

## Adım 4 — Bağ onarımı

- [x] 4.1 `adr/NNNN-….md` yol göndermeleri (~235) → `kararlar-XXXX-YYYY.md#adr-NNNN`
- [x] 4.2 `research_log/YYYY-MM-DD-….md` yol göndermeleri (~153) → `kronoloji-A-B.md#NN`
- [x] 4.3 Silinen 5 hedefe gönderme elden geçirilir (CLAUDE.md · kollar.md · configs/ · data/ · outputs/eval/)
- [x] 4.4 → *verify:* `docs/`, kök, `scripts/`, `knowledge/`, `configs/`, `data/` içinde var-olmayan
      `.md` hedefi kalmadı (elle betik)

## Adım 5 — Doğrulama + kapanış

- [x] 5.1 `pytest tests/test_belgeler.py -q` → *verify:* yeşil
- [x] 5.2 Ölçüm: **12 dosya · 608 KB · ~208 bin token** → ✅ ≤15 dosya · ⚠️ 200 bin token hedefi **%4 aşıldı**
- [x] 5.3 ADR-0086 yazılır (ADR-0024'ten bilinçli sapma, ikinci kez)
- [x] 5.4 CLAUDE.md işaretçileri güncellenir (sayı değil, işaretçi — CLAUDE.md'nin kendi kuralı)


---

## Kapanış bloğu — 2026-09-13

**Sonuç: 103 dosya · 1,40 MB · ~466 bin token → 12 dosya · 608 KB · ~208 bin token.**
Dosya sayısı **%88**, hacim **%55** azaldı. `pytest tests/` **335 geçti, 2 xfail**.
Bağlantı denetimi: **ölü bağlantı 0**, çözülen çapa **297**.

**İki kapı tutturulamadı, ikisi de olduğu gibi yazılır:**

1. **`yurutme-tuzaklari.md` ≤ 25 KB tutturulamadı (44 KB).** Sebep ölçüldü, tahmin edilmedi: bu
   dosyada **kesilecek anlatı yok** — 85 satırın her biri ayrı bir derstir ve `ne olur` sütunu
   dersin kendisidir. Damıtma kuralı 1-2 (*her sayı, her ders korunur*) bayt hedefinin önünde
   tutuldu. 202 benzersiz sayının tamamı denetlendi, **hiçbiri düşmedi**.
2. **~200 bin token hedefi %4 aşıldı (208 bin).** Aynı sebep: kalan hacmin tamamı sayı ve ders.

**Tasarımdan iki sapma, ikisi de ölçümle gerekçelendirildi:**

- **`gemma4-12b-dersler.md` Bölüm B SİLİNMEDİ.** Tasarım silmeyi öngörüyordu; silmeden önce gelen
  gönderme sayıldı: `ADR-0001..0026`'ya **319 atıf** var ve **10'u CLAUDE.md'de yürürlükte** diye
  anılıyor (`0003 · 0010 · 0011 · 0016 · 0017 · 0018 · 0019 · 0023 · 0025 · 0026`). Silmek
  yürürlükteki on kararın metnini yok ederdi.
- **`gemma4-12b-kronoloji.md` SİLİNMEDİ.** Bir dosya ve 38 KB kazandırırdı; karşılığında 38
  girdinin numarası ölürdü. Risk/fayda tutmuyor.

**Bilinçli olarak onarılmayan bağlantılar.** `outputs/eval/**` içindeki eski `research_log/` ve
`adr/NNNN-*.md` yolları **dokunulmadan bırakıldı** — orası ölçüm kaydıdır ve *"o gün bu yoldan
koşuldu"*yu kaydeder (emsal: ADR-0083 §D). Çeviri kuralı: `ADR-00NN` → `kararlar-*.md#adr-00NN`,
log `#NN` → `kronoloji-*.md#NN`.

**Bir hata yapıldı ve geri alındı.** Toptan yol değiştirme, ADR-0024'ün **kendi kural cümlesindeki**
`research_log/` dizesini de değiştirdi — yani bir alıntıyı yeniden yazdı. Fark edildi, geri alındı.
*Alıntı, yol onarımının kapsamı değildir.*
