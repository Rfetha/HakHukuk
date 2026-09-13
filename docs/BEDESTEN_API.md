> ## ✅ SÖZLEŞME CANLI API'YE KARŞI DOĞRULANDI — 2026-08-04
>
> Üç çağrının **dördü de** (arama · `getDocumentContent` · `mevzuatMaddeTree`) **GEÇERLİ**
> döndü ([#49](record/kronoloji-39-52.md#49) · `outputs/eval/s3a-on-prob/`).
>
> 🚨 **Ve bu belgeye güvenmek doğru çıktı.** Prob betiği önce *"sözleşme bozuk"* raporladı;
> hata **API'de değil betikteydi** — belge kimliğini `documentId`/`id` ile arıyordu, oysa
> API'nin alanı **`mevzuatId`** ve §48 en baştan doğruydu. Ters yöndeki bu yanlış, güncellik
> iddiasını gereksiz yere düşürüp `ROADMAP`/`MODEL_CARD`'da yanlış düzeltme yaptıracaktı.
> → **tuzak 7.1**: *"sözleşme bozuk" sonucu, ham yanıt gözle okunmadan kayda geçmez.*
>
> ⚠️ **Sözleşme çalışıyor, ürün onu HENÜZ KULLANMIYOR** — canlı katman bilinçli ertelendi
> (ADR-0054 K3: ölçüm tekrarlanabilirliği). Güncellik iddiası **ayakta ama kanıtlanmamış**
> (borç **B6**).

# Bedesten API — Reverse-Engineered Referans

> ## 🚨 SÖZLEŞME 2026-06-07'DEN BERİ DOĞRULANMADI
>
> **Güncellik iddiamızın tek dayanağı bu API.** *"Kapalı ağırlıklı rakiplerin yapamadığı şey"*
> cümlesi buraya bağlı — ve sözleşme iki aydır sınanmadı.
>
> Sprint 3'ün **ön-probunda** `recall@k` ile birlikte sınanacak (`scripts/erisim_korpus/bedesten_probe.py`,
> maliyet sıfır). ⚠️ **Türk IP gerekiyor** — gov firewall yurtdışı/VPN'i engelliyor.
>
> Değişmişse: retriever statik korpusla çalışmaya devam eder, ama **güncellik iddiası düşer**
> ve [`ROADMAP.md`](../ROADMAP.md) *(2026-09-06'da silinmişti, 2026-09-07'de yeniden yazıldı)* ile [`MODEL_CARD.md`](../MODEL_CARD.md) düzeltilir.

> `saidsurucu/mevzuat-mcp` (MIT) reposundan çıkarıldı + canlı test edildi (2026-05-29, çalışıyor).
> **Amaç:** MCP'yi kurmadan, mevzuat (ve ileride içtihat) verisini doğrudan bu temiz JSON API'den çekmek.
> Çalışan minimal istemci: `scripts/erisim_korpus/bedesten_probe.py`.

## Genel
- **BASE:** `https://bedesten.adalet.gov.tr/mevzuat`
- **Auth/Playwright/cookie:** YOK (saf httpx/urllib yeter).
- **Erişim notu:** Adalet Bakanlığı backend'i; TR IP gerekebilir (mevzuat.gov.tr gibi — VPN kapalıyken test edildi, çalıştı).
- **Headers (zorunlu):**
  ```
  Content-Type: application/json
  Origin:  https://mevzuat.adalet.gov.tr
  Referer: https://mevzuat.adalet.gov.tr/
  User-Agent: Mozilla/5.0 ... (tarayıcı UA)
  ```
- **Sarmalama:** her POST gövdesi → `{"data": <inner>, "applicationName": "UyapMevzuat"}`. Aramada ek: `"paging": true`.
- **Başarı kontrolü:** `body.metadata.FMTY == "SUCCESS"` (hata: `FMTE` mesajı).

## Uçlar (hepsi POST)

### 1. `/searchDocuments` — mevzuat ara/listele
inner alanları:
```jsonc
{
  "pageSize": 5, "pageNumber": 1,
  "sortFields": ["RESMI_GAZETE_TARIHI"], "sortDirection": "desc",
  "mevzuatNo": "4857",                 // opsiyonel: kanun no
  "mevzuatAdi": "İş Kanunu",           // opsiyonel: ada göre
  "phrase": "...",                      // opsiyonel: tam-metin (Solr)
  "mevzuatTurList": ["KANUN","KHK"],   // opsiyonel: tür filtresi
  "basliktaAra": true, "tamCumle": false
}
```
→ `paging:true` ile sar. Yanıt: `body.data.mevzuatList[]`, `body.data.total`.
Her doküman: **`mevzuatId`** (asıl id, örn "103054"), `mevzuatNo`, `mevzuatAdi`, `mevzuatTur{id,name}`, `mevzuatTertip`, `resmiGazeteSayisi`, `url`, `gerekceId`.

### 2. `/getDocumentContent` — tam metin
```jsonc
{"documentType": "MEVZUAT", "id": "<mevzuatId>"}   // tüm kanun
{"documentType": "MADDE",   "id": "<maddeId>"}     // tek madde
```
→ `body.data.content` **base64** (genelde `text/html`), `body.data.mimeType`. Decode + HTML tag temizle.

### 3. `/mevzuatMaddeTree` — madde ağacı (TOC)
```jsonc
{"mevzuatId": "<mevzuatId>"}
```
→ kanun→bölüm→madde hiyerarşisi (her madde için id'ler; #2 ile tek tek metin çekilebilir).

### 4. Diğer
- `/getGerekceContent` → `{"id": "<gerekceId>"}` — kanun gerekçesi.
- `/mevzuatTypes` → `{}` — tür listesi (KANUN, KHK, YÖNETMELİK…).

## Mevzuat türleri (`mevzuatTurList`)
KANUN, CB_KARARNAME (Cumhurbaşkanlığı Kararnamesi), KHK, TUZUK, YONETMELIK, CB_KARAR, CB_GENELGE, TEBLIG, KKY, vb. (kesin liste için `/mevzuatTypes`).

## Bizim için kullanım planı
1. `mevzuatTurList:["KANUN"]` + sayfalama ile **tüm kanunları listele** → `mevzuatId` topla.
2. Her biri için `/getDocumentContent` (MEVZUAT) → tam metin; veya `/mevzuatMaddeTree` + madde-bazlı çekim.
3. Çıkar → temizle → `data/raw/` (grounding korpusu). Canlı = hep güncel.
4. (Faz 2) İçtihat: aynı backend `bedesten.adalet.gov.tr` (yargi-mcp contract'ı ayrıca çıkarılacak).
