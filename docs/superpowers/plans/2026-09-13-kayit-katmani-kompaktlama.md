# Plan — kayıt katmanı kompaktlama

**Tasarım:** [`specs/2026-09-13-kayit-katmani-kompaktlama-design.md`](../specs/2026-09-13-kayit-katmani-kompaktlama-design.md)
**Geri dönüş noktası:** `301a82f` (temiz ağaç) · **Başlangıç:** 103 dosya · 1,40 MB · ~466 bin token

---

## Adım 1 — Çöp

- [ ] 1.1 `docs/record/2026-09-10-hp-hat-a-hat-b-kapanan-gorevler.md` sil → *verify:* dosya yok
- [ ] 1.2 `docs/record/sprint2/` sil → *verify:* dizin yok
- [ ] 1.3 `docs/record/sprint1/` sil → *verify:* dizin yok
- [ ] 1.4 `gemma4-12b-dersler.md` Bölüm C kesilir → *verify:* `grep -c '^## C' == 0`, Bölüm A ve B duruyor

## Adım 2 — `docs/adr/` birleştirme + damıtma

- [ ] 2.1 `kararlar-0027-0044.md` (18 ADR, 2105 satır) → *verify:* 18 çapa (`<a id="adr-00NN">`) var
- [ ] 2.2 `kararlar-0045-0063.md` (18 ADR, 2206 satır) → *verify:* 18 çapa var
- [ ] 2.3 `kararlar-0064-0085.md` (22 ADR, 2704 satır) → *verify:* 22 çapa var
- [ ] 2.4 58 tekil ADR dosyası silinir → *verify:* `ls docs/adr/[0-9]*.md` boş
- [ ] 2.5 `adr/README.md` yeniden yazılır → *verify:* ≤ 100 B/satır, 58 satır dizin

## Adım 3 — `docs/record/` birleştirme + damıtma

- [ ] 3.1 `kronoloji-39-52.md` (#39-#52) → *verify:* 14 çapa
- [ ] 3.2 `kronoloji-53-62.md` (#53-#62) → *verify:* 10 çapa
- [ ] 3.3 `kronoloji-63-71.md` (#63-#71) → *verify:* 9 çapa
- [ ] 3.4 33 tekil log dosyası + `research_log/` dizini silinir → *verify:* dizin yok
- [ ] 3.5 `yurutme-tuzaklari.md` damıtılır → *verify:* her tuzak numarası duruyor, ≤ 25 KB
- [ ] 3.6 `record/README.md` yeniden yazılır → *verify:* ölü işaretçi yok

## Adım 4 — Bağ onarımı

- [ ] 4.1 `adr/NNNN-….md` yol göndermeleri (~235) → `kararlar-XXXX-YYYY.md#adr-NNNN`
- [ ] 4.2 `research_log/YYYY-MM-DD-….md` yol göndermeleri (~153) → `kronoloji-A-B.md#NN`
- [ ] 4.3 Silinen 5 hedefe gönderme elden geçirilir (CLAUDE.md · kollar.md · configs/ · data/ · outputs/eval/)
- [ ] 4.4 → *verify:* `docs/`, kök, `scripts/`, `knowledge/`, `configs/`, `data/` içinde var-olmayan
      `.md` hedefi kalmadı (elle betik)

## Adım 5 — Doğrulama + kapanış

- [ ] 5.1 `pytest tests/test_belgeler.py -q` → *verify:* yeşil
- [ ] 5.2 Ölçüm: dosya sayısı · bayt · token → *verify:* ≤ 15 dosya, ≤ 200 bin token
- [ ] 5.3 ADR-0086 yazılır (ADR-0024'ten bilinçli sapma, ikinci kez)
- [ ] 5.4 CLAUDE.md işaretçileri güncellenir (sayı değil, işaretçi — CLAUDE.md'nin kendi kuralı)
