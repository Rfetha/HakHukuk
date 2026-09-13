> ## 📌 DURUM 2026-08-05 — harita geçerli, **hiçbiri çekilmedi**
>
> Bu harita 2026-05-29'da çıkarıldı ve **hâlâ doğru**; ama Faz 2'de bugüne kadar kurulan
> şey **mevzuat** tarafı: hibrit retriever + 40.496 maddelik indeks
> (`sprint3-part1.md` ⚰️ *(arşiv silindi; borç kuyruğu **`DEVIR-PROMPT.md` *(silindi)* §5**'e kurtarıldı)*). **İçtihat tarafına hiç dokunulmadı.**
>
> ⚠️ Aynı `bedesten` backend'i içtihadı da veriyor ([`BEDESTEN_API.md`](BEDESTEN_API.md)) ve
> sözleşmesi 2026-08-04'te doğrulandı — yani teknik yol açık, **iş yapılmadı**.
>
> İçtihadın grafa girip girmeyeceği hâlâ açık soru
> (açık kararlar *(soruları taşıyan `docs/open_questions.md` 2026-09-07'de, onları devralan plan da 2026-09-12'de silindi; grill'e girecek dokuz madde [ADR-0083](adr/kararlar-0064-0085.md#adr-0083) §EK E.5'te)*); graf'ın ölçülmüş gerekçesi ve
> **ölçülmüş riski** [`ROADMAP.md`](../ROADMAP.md) *(2026-09-06'da silinmişti, 2026-09-07'de yeniden yazıldı)*'de.

# Yargı/İçtihat Veri Kaynakları — Reverse-Engineered Harita (Faz 2)

> `saidsurucu/yargi-mcp` (MIT) reposu kaynak düzeyinde söküldü (2026-05-29). Her kurumun **gerçek veri kaynağı** çıkarıldı.
> **İlke (kilitli): %100 in-house.** OSS/akademik proje 3. parti MCP runtime'ına bağlı olamaz. Her kaynağı kendimiz çekeriz; 3. parti arama API'leri (Brave/Tavily) kendi index'imizle değiştirilir.
> Bu Faz 2 işidir; harita şimdi çıkarıldı ki "hepsini çekebilir halde" olalım.

## Kurum → kaynak haritası

| # | Kurum | Gerçek kaynak | Erişim | In-house |
| :- | :-- | :-- | :-- | :-- |
| 1 | **Yargıtay** | `karararama.yargitay.gov.tr` — POST `/aramadetaylist`, GET `/getDokuman?id=` | Kendi JSON API | ✅ |
| 2 | **Danıştay** | `karararama.danistay.gov.tr` | Kendi API | ✅ |
| 3 | **Bedesten** (mahkeme/emsal kararları) | `bedesten.adalet.gov.tr` — POST `/emsal-karar/searchDocuments`, `/emsal-karar/getDocumentContent` (sarmalama mevzuatla aynı: `{data, applicationName}`; `birimAdi`/`itemType` filtreleri) | Temiz API (zaten çözüldü) | ✅ |
| 4 | **Emsal (UYAP)** | `emsal.uyap.gov.tr` | UYAP API | ✅ |
| 5 | **AYM — bireysel başvuru** | `kararlarbilgibankasi.anayasa.gov.tr` | Kendi API | ✅ |
| 6 | **AYM — norm denetimi** | `normkararlarbilgibankasi.anayasa.gov.tr` | Kendi API | ✅ |
| 7 | **Uyuşmazlık Mahkemesi** | Bedesten / ilgili portal | API | ✅ |
| 8 | **GİB** (vergi özelgeleri, 18K+) | `gib.gov.tr/api` | Resmî API | ✅ |
| 9 | **KİK** (kamu ihale) | `ekapv2.kik.gov.tr` | Resmî API v2 | ✅ |
| 10 | **Rekabet Kurumu** | `rekabet.gov.tr` | Site | ✅ |
| 11 | **Sayıştay** | `sayistay.gov.tr` | Site | ✅ |
| 12 | **BDDK** | `bddk.org.tr/Mevzuat/DokumanGetir/...` | Site (belge); **arama**: MCP Tavily kullanıyor | ⚠️→✅ |
| 13 | **KVKK** | `kvkk.gov.tr/Icerik/...` | Site (belge); **arama**: MCP Brave kullanıyor | ⚠️→✅ |
| 14 | **Sigorta Tahkim** | Hakem Karar Dergisi PDF (2010–2025); **arama**: MCP Tavily | PDF; arama 3. parti | ⚠️→✅ |

## %100 in-house stratejisi (3. parti arama nasıl elenir)

12/14 kaynak zaten temiz (kendi API/site) — sıfır 3. parti.

3 kaynakta (BDDK, KVKK, Sigorta) **belgeler resmî sitede** (in-house erişilebilir); MCP yalnızca **arama/keşif** için Brave/Tavily kullanıyor (o sitelerde iyi arama API'si yok). %100 in-house için:
- Siteyi sistematik **crawl edip kendi index'imizi** kurarız (belge listesini enumerate), Brave/Tavily yerine kendi aramamız.
- Belge içeriği zaten resmî siteden iner. → Hiçbir 3. parti runtime'a bağımlılık kalmaz.

**Sonuç:** Tüm yargı datası kendi kodumuzla çekilebilir. MCP = sadece reverse-engineering kaynağıydı; runtime olarak kullanılmaz.

## Sıra (Faz 2)
Öncelik: Bedesten (mahkemeler) + Yargıtay + Danıştay + AYM (vatandaşa en yakın içtihat) → sonra kurum kararları (KVKK, Rekabet, vb.) niş ihtiyacına göre.
