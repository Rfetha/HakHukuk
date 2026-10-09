# Bedesten sözleşme sınaması — 2026-08-04

Son doğrulama: 2026-06-07. Aradan ~2 ay geçti; güncellik iddiamızın tek dayanağı bu.

**Koşum ortamı:** Türk IP doğrulandı (AS9121 Türk Telekom, İzmir) — gov firewall koşulu
sağlanıyor. Auth yok, Playwright yok, sadece `urllib`.

| çağrı | durum | not |
| :--- | :--- | :--- |
| `POST /searchDocuments` (arama) | ✅ | `mevzuatNo=4857` → `total: 1`, `FMTY: SUCCESS`, `mevzuatId = 103054` |
| `POST /getDocumentContent` (tam metin, `documentType=MEVZUAT`) | ✅ | `text/html`, 648.836 karakter base64 — İş Kanunu tam metni |
| `POST /mevzuatMaddeTree` (madde ağacı) | ✅ | `children` hiyerarşisi; her düğümde `maddeId · maddeNo · title · guncellemeTarihi` |
| `POST /getDocumentContent` (`documentType=MADDE`) | ✅ | tek madde metni — **retriever'ın asıl kullanacağı yol** |

**Sonuç: sözleşme GEÇERLİ.** `docs/BEDESTEN_API.md`'de yazan alan adları ve sarmalama
(`{"data": <inner>, "applicationName": "UyapMevzuat"}`) birebir tutuyor.

**Güncellik kanıtı:** İş Kanunu Madde 1 için `guncellemeTarihi: 2026-05-07`,
kayıt tarihi `2026-05-04` — statik korpusumuz (29 Temmuz anlık görüntüsü) ile aynı
düzlemde, API canlı besleniyor.

**Etkisi:** güncellik iddiası **ayakta**. `ROADMAP.md` ve `MODEL_CARD.md`'de düzeltme
gerekmiyor. Canlı katman S3'te planlanabilir (K3: statikle başla, canlıyı sonra ekle —
öneri değişmedi, çünkü ölçüm tekrarlanabilirliği statik korpusu gerektiriyor).

## ⚠️ Bulunan hata: prob betiği sözleşmeyle uyumsuzdu

`scripts/bedesten_probe.py` belge kimliğini `d.get("documentId") or d.get("id")` ile
arıyordu; API'nin alanı **`mevzuatId`**. Sonuç: arama SUCCESS dönerken `id: None`
basılıyor, ardından `getDocumentContent` `ERROR` veriyordu — yani **prob, API çalışırken
"bozuk" raporluyordu**. `docs/BEDESTEN_API.md` satır 48 en başından beri `mevzuatId`
diyor; hatalı olan betikti, sözleşme değil.

Betik ayrıca **madde ağacını hiç sınamıyordu** (sözleşmenin 3. çağrısı) — planın
"arama · tam metin · madde ağacı" listesinin üçte biri ölçülmeden kalıyordu.

İkisi de düzeltildi. Ders: *ölçüm aracının kendisi de sessizce yanlış olabilir* —
bu vaka `yurutme-tuzaklari.md` sınıfına giriyor (çökme değil, yanlış sonuç).
