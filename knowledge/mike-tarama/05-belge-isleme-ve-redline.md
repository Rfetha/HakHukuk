# Mike: belge işleme, redline (izlenen değişiklik) ve dışa aktarım bütünlüğü

Kaynak: Mike (TypeScript, AGPL-3.0), salt-okunur kopya. Aşağıdaki yollar kaynak kökünden (`mike-main/`) başlar. Kod kopyalanmamıştır; tasarım kendi cümlelerimizle anlatılmıştır, alıntılar en çok 3 satırdır. "Tahmin" ve "çalıştırılmadı" etiketleri, kaynaktan doğrudan okunmayan veya denenmemiş çıkarımları gösterir.

## Kapsam ve okunan dosyalar

Tamamı okunan dosyalar:

- `backend/src/lib/docxTrackedChanges.ts` (1135 satır)
- `backend/src/lib/pdfText.ts` (371), `pdfTextOrder.ts` (başı ve sabitler, 1-140), `pdfjs.ts`
- `backend/src/lib/convert.ts`, `documentTypes.ts`, `officeText.ts`, `spreadsheet.ts`, `documentVersions.ts`, `manifestSigning.ts`, `documentDisplay.ts`
- `backend/src/modules/chat/engine/tools/documentOps.ts` (1952; tamamı, üretim kısmı hızlı)
- `backend/src/modules/chat/engine/tools/toolSchemas.ts` (read/find/generate/edit/replicate kısımları)
- `backend/src/modules/chat/engine/tools/toolDispatcher.ts` (read_document 563-622 ve edit_document 1429-1604)
- `backend/src/modules/documents/documents.edits.ts`, `documents.versions.ts`, `documents.lifecycle.ts`, `documents.textJobs.ts`, `documents.conversion.ts`, `documents.download.ts` (başı), `documents.routes.ts` (rota listesi)
- `backend/src/modules/uploads/uploads.processing.ts` (1-780), `uploads.manifest.ts` (limitler ve tür denetimi), `uploads.shared.ts`
- `backend/src/lib/storage.ts` (sürücü seçimi ve anahtar yardımcıları)
- `backend/src/modules/user/user.dataExport.ts` (300-411, proje manifesti)
- `docs/docx-preview-engines.md`, `docs/tamper-evident-exports.md`
- İlgili ek dosyalar: `backend/src/modules/chat/engine/verifyCitations.ts` (1-135), `tools/wordClientTools.ts` (60-200, Word eklentisinin sade edit şeması), `contextBuilders.ts` (575-615), `frontend/src/app/components/shared/views/highlightQuote.ts` (1-80)
- Test: `backend/src/lib/__tests__/docxTrackedChanges.test.ts` (başı ve `it(...)` başlıkları)

Doğrulanan sürümler: arka uç `docx ^9.10.0`, `jszip ^3.10.2`, `fast-xml-parser ^5.11.2`, `mammoth ^1.13.0`, `pdfjs-dist ^6.4.299`, `xlsx` (SheetJS 0.20.3, cdn.sheetjs.com tarball), `libreoffice-convert ^1.6.0` (`backend/package.json:37-52`).

## Nasıl çalışıyor

### 1. Desteklenen biçimler ve yükleme

- İzinli türler yalnızca şunlardır: `pdf, docx, doc, xlsx, xlsm, xls, pptx, ppt` (`backend/src/lib/documentTypes.ts:1-13`). UDF, RTF, ODT, TXT, görüntü (JPG/PNG/TIFF) kabul edilmez.
- Tür denetimi yalnızca dosya adı uzantısına bakar (`backend/src/modules/uploads/uploads.manifest.ts:219-224`). İçerik türü de uzantıdan türetilir (`uploads.manifest.ts:244`). Sihirli bayt (magic byte) denetimi bu yolda görülmedi; yalnızca okuma sırasında ilk 8 bayt günlüğe yazılır (`documentOps.ts:1557-1564`).
- Sınırlar: dosya başına 100 MB, oturum başına 50 dosya, oturum toplamı 2 GB (`uploads.manifest.ts:22-24`).
- Yükleme iki aşamalıdır: tarayıcı doğrudan nesne depolamaya yazar, arka uç "mühürlü" nesneyi işçi süreci (worker) ile işler. İşçi nesneyi geçici dizine akıtırken SHA-256 ve bayt sayısını aynı geçişte hesaplar; beklenen boyutla uyuşmazsa reddeder (`uploads.processing.ts:285-327`).
- Depolama sürücüsü S3/R2 uyumludur; `STORAGE_DRIVER=fs` ile yerel dosya sistemine geçilir (masaüstü/tek düğüm için tasarlanmış) (`backend/src/lib/storage.ts:32-48`). Anahtar şeması: `documents/<kullanıcı>/<belge>/source.<uzantı>`, sürümler için `.../versions/<slug>.<uzantı>`, üretilenler için `generated/...`, dönüştürülmüş PDF için `converted-pdfs/...`, önbellek metni için `extracted-text/<sürüm>.txt` (`storage.ts:743-776`, `convert.ts:273-281`).

Önceki yüzeysel okumaya düzeltme/ek: işçi yalnızca hash ve sayfa sayısı hesaplamaz. Üç şey daha yapar: (a) PDF için sayfa sayısı (`uploads.processing.ts:161-185`, `:451-452`), (b) PDF için metin katmanı olmayan sayfa sayısı `textless_page_count` (`:189-201`, `:453-457`) ve (c) Word/PowerPoint için LibreOffice ile PDF "rendition" üretimi (`:203-248`). Sayfa sayısı yalnızca PDF'te doldurulur; DOCX için `page_count` null kalır (`:451-452`, `documentOps.ts:1242`, `:1279`).

### 2. Metin çıkarımı (istek anında, depolanmaz)

Yükleme sırasında metin çıkarılıp dizinlenmez. `read_document` aracı her çağrıda baytları depolamadan indirir ve türe göre çıkarır (`documentOps.ts:1517-1656`):

| Tür | Yöntem | Kanıt |
| :--- | :--- | :--- |
| PDF | `pdfjs-dist` (legacy build), sayfa sayfa `getTextContent` + form alanları (`getAnnotations`) | `pdfText.ts:244-293` |
| DOCX | Kendi `fast-xml-parser` tabanlı "kabul edilmiş görünüm" çıkarıcısı; boş dönerse `mammoth.extractRawText` yedeği | `documentOps.ts:1572-1591`, `docxTrackedChanges.ts:691-722` |
| XLSX/XLSM/XLS | SheetJS; hücre biçimli gösterim metni (`cell.w`), sayfa başına hücre adresli markdown tablosu, birleştirilmiş hücre etiketi | `spreadsheet.ts:19-109` |
| PPTX | JSZip ile `ppt/slides/slideN.xml` içindeki `<a:t>` etiketlerini regex ile toplar; `## Slide N` başlığı | `backend/src/lib/officeText.ts:36-53` |
| DOC, PPT | LibreOffice ile PDF'e dönüştürüp pdfjs; sonuç `extracted-text/<sürüm>.txt` olarak önbelleğe alınır (`document.precompute_text` işi) | `documentOps.ts:1604-1643`, `documents.textJobs.ts:20-80`, `documentTypes.ts:49-62` |
| Bilinmeyen tür | `mammoth` | `documentOps.ts:1644-1656` |

Boyut kırpması: depolanmış belgelerde `read_document` çıktısına karakter üst sınırı uygulandığı görülmedi (tüm metin tek araç sonucu olarak döner). 200.000 karakterlik sınır yalnızca Word eklentisinin satır içi bağlamı içindir (`contextBuilders.ts:583-609`). Araç açıklaması "tam metni oku, yanıt başına en çok bir kez" der (`toolSchemas.ts:252-254`); aynı sürüm ikinci kez istenirse metin yerine "zaten döndü" bildirimi gelir (`documentOps.ts:1412-1435`). Parçalama (chunking), embedding, OCR ya da arama dizini bu yolda yoktur (aramayla doğrulandı: `ocr|tesseract|embedding` için yalnızca `pdfText.ts` içindeki kullanıcı bildirimi metinleri belirgin; `chunk` ile eşleşen diğer dosyalar ayrıntılı incelenmedi, akış kodu olduğu tahmin).

`find_in_document` aracı da aynı `readDocumentContent` çıktısı üzerinde çalışır: boşluk daraltma + küçük harfe çevirme ile ilk 20 eşleşmeyi bağlamıyla (varsayılan 80 karakter) döndürür (`documentOps.ts:1739-1780`, `:1786-1905`; şema `toolSchemas.ts:271-299`). Yani "arama", belgeyi tekrar çıkarıp düz metinde dize aramasıdır; indeks yoktur.

### 3. PDF metin çıkarımı ayrıntıları

- Sayfa başına çıktı `[Page N]` işaretiyle başlar (`pdfText.ts:274`); sayfa numarası konum modelinin tek temelidir. Alıntı doğrulaması da bu metin üzerindedir (`verifyCitations.ts:41-58`); sayfalar arası alıntılar `[[PAGE_BREAK]]` ayracıyla ve en çok 5.000 karakterlik aralıkla birleştirilir (`verifyCitations.ts:7-13`).
- Yerleşim yeniden kurulumu (`pdfText.ts:139-216`): pdfjs öğeleri (x, y, genişlik, yükseklik) taban çizgisine göre satırlara gruplanır; satır yüksekliğinin 1,7 katını aşan dikey boşluk paragraf sonu sayılır; satır başı girinti sayfanın sol kenarına göre ölçülür (en çok 24 karakter); yatay boşluk satır yüksekliğinin 2,5 katını aşarsa 4-16 boşluk (sütun/imza bloğu korunur), 0,15 katını aşarsa tek boşluk, daha azsa bitişik yazılır.
- Okuma sırası: içerik akışı çizim sırasındadır, okuma sırası değildir. `pdfTextOrder.ts` önce XY-kesme ile sütunları ayırır (en az 12 pt ve 1,2 em genişlikte oluk, en az 4 satır, sütun başına en az 3 satır, en çok 4 özyineleme; `pdfTextOrder.ts:57-73`), sonra her sütunda satırlara gruplar. Aynı dosyanın bir kopyası ön yüzde de vardır ve ortak test vakaları (`packages/pdf-text-order/cases.json`) ile eşitlenir (`pdfTextOrder.ts:18-27`). Sayfa dönüklüğü (`/Rotate`) hesaba katılmaz; iki tarafta da aynı biçimde yanlış olduğu için vurgulama tutarlıdır (`pdfTextOrder.ts:38-42`).
- AcroForm alanları `[ad: değer]` biçiminde konumlu öğe olarak metne eklenir; parola alanları ve seçili olmayan radyo düğmeleri atlanır; konumu olmayanlar `[Page N form fields]` bölümüne gider (`pdfText.ts:37-130`, `:262-279`).

### 4. Taranmış PDF davranışı

OCR yoktur. Tarama tespiti yalnızca "metin katmanı yok" sezgisidir: bir sayfada hiçbir metin öğesi ve form alanı yoksa o sayfa "boş" sayılır (`pdfText.ts:281-284`). Yükleme anında sayısı `textless_page_count` olarak saklanır, böylece belge listesi taramaları işaretleyebilir (`uploads.processing.ts:187-201`). Modele giderken (`extractPdfTextForModel`): tüm sayfalar boşsa yalnızca "metin katmanı yok, büyük olasılıkla taranmış belge, OCR gerekir" bildirimi döner; bazı sayfalar boşsa bildirim metnin önüne eklenir (`pdfText.ts:325-353`). Gerekçe kodda açıktır: bildirim yoksa model boş sayfa işaretlerinden belgeyi "boş" sanabilir (`pdfText.ts:338-344`). Bu iyi bir koruma desenidir; biz de aynısını kullanabiliriz.

### 5. Sürümleme ve değişmezlik

- Bir belgenin birçok sürümü olabilir (`document_versions` tablosu; sürüm no, kaynak, dosya adı, tür, boyut, sayfa sayısı, `content_sha256`, `deleted_at`). Etkin sürüm `documents.current_version_id` ile gösterilir; sürüm yükleme, etkinleştirme ve numara atama tek işlemde bir veritabanı RPC'sinde yapılır (`documents.lifecycle.ts:29-48`, `documentVersions.ts:70-108`). RPC gövdeleri bu depoda yok (`supabase/` yalnızca `gateway.conf` içeriyor), bu yüzden numaralama ve silme mantığı okunmadı.
- Sürüm kaynakları: `upload`, `user_upload`, `assistant_edit`, `generated` (`uploads.processing.ts:464,562`, `documentOps.ts:1274`, `:996`). Asistan düzenlemesi her turda yeni sürüm açar; aynı turdaki birden çok `edit_document` çağrısı tek sürüme çökertilir (aynı dosya üzerine yazılır, satır korunur; `documentOps.ts:1134-1145`, `:1231-1245`).
- "Değişmezlik" kısmidir. Hash, yazılan baytlardan her yazımda yeniden hesaplanır (`documentVersions.ts:16-21`). Ama iki yerde sürüm satırının bayt göstergesi yerinde değiştirilir: tur içi yeniden kullanım (hash önce null yapılır, dosya yazılır, yeni hash yazılır; `documentOps.ts:1238-1244`) ve editör kaydı/kabul-ret (aşağıda). Depo yorumu da bunu açıkça söyler: sürümler "iki yerinde yeniden yazım dışında" değişmezdir (`storage.ts:768-773`).
- Eşzamanlılık: kabul/ret ve editör kaydı önce yeni bir nesneye yazar, sonra `storage_path` (ve editör kaydında içerik hash'i) beklenen değerle eşleşirse tek güncellemede yolu, hash'i, boyutu ve PDF rendition'ı değiştirir; kayıp yarışta 409 döner ve yetim nesne silinir (`documents.edits.ts:165-193`, `documentVersions.ts`/`documents.lifecycle.ts:82-115`, `uploads.processing.ts:621-692`; `docs/docx-preview-engines.md:69-76`).
- Editör kaydında `created_at` yeniden yazılır (`uploads.processing.ts:684`), yani kaydedilen sürümün zaman damgası ilk oluşturma değil son kayıttır (manifestteki `created_at` bu nedenle ilk yazımı kanıtlamaz; gözlem).
- Sürüm silme yumuşaktır (`deleted_at`), son sürüm silinemez; temizlik işi nesneleri sonradan siler (`documents.versions.ts:372-460`, `documents.cleanupJobs.ts` başı).
- Önizlemede sürüm menüsü yalnızca birden çok silinmemiş sürüm varsa görünür; sürüm seçmek sunucudaki etkin sürümü değiştirmez (`docs/docx-preview-engines.md:34-39`).

### 6. Tracked-change (redline) üretimi: adım adım

Mike'ın DOCX düzenlemesi `edit_document` aracı ile `applyTrackedEdits` işlevidir. Kapsam kuralı: yalnızca gövdedeki `w:p` içindeki `w:r` / `w:t` metni düşünülür; üstbilgi, altbilgi, yorum ve dipnotlara dokunulmaz (`docxTrackedChanges.ts:9-15`).

Araç şeması (model tarafı): `doc_id` ve `edits[]`; her düzenleme `find`, `replace`, `context_before`, `context_after` (dördü de zorunlu) ve isteğe bağlı `reason` (`toolSchemas.ts:472-519`). Yalnızca `.docx` kabul edilir (`toolDispatcher.ts:1491`). Şablon/iş akışı varlıkları doğrudan düzenlenemez, önce `replicate_document` gerekir (`toolDispatcher.ts:1463-1474`).

Algoritma (`docxTrackedChanges.ts:759-1006`):

1. DOCX bir ZIP olarak açılır (JSZip); `word/document.xml` okunur. Eski Windows arşivlerindeki ters eğik çizgili yollar için hem okuma hem yazma yedeği vardır (`:31-50`). Yoksa hata fırlatılır (`:768-769`).
2. XML, sıra korunarak (`preserveOrder`) bir ağaca çözülür (`:628-638`). Paragraflar tablo, satır, hücre ve `w:sdt` içine inilerek toplanır (`:782-800`).
3. Her paragraf düzleştirilir: `w:r` altındaki `w:t` metinleri art arda eklenir ve her karakter için hangi koşuya ve metin düğümüne ait olduğu kaydedilir (`:207-268`). "Kabul edilmiş görünüm": var olan `w:ins` içindeki koşular normal metin sayılır, `w:del` tamamen yok sayılır (`:250-258`). `w:tab`, `w:br`, `w:sym` gibi metin olmayan koşu çocukları karakter akışına girmez (`:240`). Doğrudan `w:p` çocuğu olmayan koşular (örn. `w:hyperlink`, `w:fldSimple` içindekiler) hiç taranmaz; kodda yalnızca `w:r` ve `w:ins` işlenir (`:248-257`). Bu bir çıkarım; çalıştırılmadı.
4. Her paragraf için bir "normalleştirilmiş" kopya üretilir: akıllı tırnaklar düz tırnağa, uzun/kısa tireler `-`, NBSP ve sıfır genişlikli boşluk boşluğa, ardışık boşluklar tek boşluğa. Küçük/büyük harf duyarlılığı korunur (büyük/küçük harf katlama yok). Normalleştirilmiş konumdan özgün konuma harita tutulur (`:513-550`).
5. Her düzenleme için doğrulama: hem `find` hem `replace` boşsa hata; `find` boşken (salt ekleme) iki bağlam da boşsa hata (`:830-840`).
6. Eşleştirme kademeleri. Kodun kendi yorumu "üç" der (`:846-849`) ama dizi dört denemedir (`:883-888`): (1) `find` + önceki bağlam + sonraki bağlam; (2) `find` + yalnızca önceki bağlam; (3) `find` + yalnızca sonraki bağlam; (4) yalnızca `find`. Her deneme tüm paragraflarda aranır; başarı için tam olarak bir paragrafta tam olarak bir eşleşme gerekir. Birden fazla eşleşme "belirsiz" sayılır, o deneme atlanır, bir sonrakine geçilir; hiçbiri tekil sonuç vermezse hata (belirsizse "bağlamı uzat", yoksa "belgeyi yeniden oku, bağlamı birebir kopyala") (`:859-910`). Önemli: bu bulanık (fuzzy) bir eşleştirme değildir. Normalleştirmeden sonra birebir dize eşitliği aranır; bağlam kademeleri yalnızca belirsizliği çözmek içindir (`findUniqueAnchor`, `:559-602`). Eşleşme tek bir paragraf içinde olmalıdır; paragraflar arası `find` bulunamaz (`:802-804`).
7. Eşleşen aralık özgün metne geri haritalanır; silinecek metin olarak belgedeki gerçek metin (model değil) kullanılır, böylece belgenin tırnak/boşluk biçimi korunur (`:916-929`).
8. Asgari fark: `find` ile `replace` arasında yalnızca ortak önek ve sonek kırpılır, ortası tek parça silme + tek parça ekleme olur; karakter düzeyinde tam diff yoktur (`:300-315`, `:931-935`). Örnek test: "ten dollars" → "five dollars" yalnızca "ten" → "five" olarak izlenir (`__tests__/docxTrackedChanges.test.ts:88-118`).
9. Çakışma: aynı paragrafta daha önce planlanmış bir düzenlemeyle aralık kesişirse "Overlaps a previous edit" hatası (`:954-965`).
10. Kimlikler: belgedeki en büyük `w:ins`/`w:del` `w:id` değerinin üstünden numaralanır (`:665-682`, `:818`, `:950-951`). Yazar adı kullanıcı profilinden gelir, yoksa "Mike" (`documentOps.ts:1200-1205`); tarih ISO zamanıdır (`:765`).
11. Paragraf yeniden kurulumu (`:326-493`): etkilenen en küçük ve en büyük koşu aralığı belirlenir; bu aralıktaki tüm koşular atılır ve yerine metinden yeniden üretilmiş koşular konur: dokunulmayan parçalar normal koşu, silinen parça `w:del` içinde `w:delText`, eklenen `w:ins` içinde `w:t`. Biçim (`w:rPr`) kaynak koşudan klonlanır; ekleme, bulunduğu konumdaki koşunun biçimini miras alır. Eklenen metindeki satır sonları `w:br` olur (`:163-177`). Çıktıda önce `w:ins`, sonra `w:del` yazılır (`:461-464`). Aralık içindeki eski `w:del` sarmalayıcıları atılır, yani önceki silmeler sessizce kabul edilmiş olur; aralığa düşen eski `w:ins` sarmalayıcısı da düşer (ekleme kabul edilir) (`:469-483`, başlık yorumu `:11-14`).
12. Yan etki (çıkarım, çalıştırılmadı): atılan koşular yalnızca metinden yeniden üretildiği için, dokunulan koşu aralığındaki sekme, `w:br`, `w:sym`, dipnot göndermesi ve gömülü nesneler kaybolabilir (`:388-410`, `:472-475`).
13. Çıktı: `XMLBuilder` ile seri hâle getirilir, XML bildirimi eklenir, ZIP DEFLATE ile yeniden paketlenir (`:996-1005`).

Sunucu tarafı sarmal (`runEditDocument`, `documentOps.ts:1123-1361`):

1. Belgeyi bulur, `content.edit` izni ister (`:1186-1191`). Kullanıcıya düzenleme izni yoksa `replicate_document` yönlendirmesi döner.
2. Etkin sürümün baytlarını indirir, `applyTrackedEdits` çağırır (`:1197-1211`).
3. Hiç değişiklik uygulanamadıysa ilk hata mesajıyla başarısız olur (`:1213-1220`). Bazıları uygulanır, bazıları olmazsa başarı döner ve `errors[]` modele iletilir (`toolDispatcher.ts:1564-1582`); yani kısmi başarı kabul edilir.
4. Yeni sürüm: nesne `documents/<kullanıcı>/<belge>/edits/<uuid>.docx` anahtarına yazılır, sürüm satırı `assistant_edit` kaynağıyla ve `activate:false` ile açılır (`:1246-1287`); sonra her değişiklik için `document_edits` satırı (`change_id`, `del_w_id`, `ins_w_id`, silinen/eklenen metin, bağlamlar, `status='pending'`) eklenir (`:1289-1311`); en sonda sürüm etkinleştirilir (`:1313-1316`). Sıralama, yarım kalan yazıma karşı bir geri alma kapısıdır, ama `document_edits` ekleme hatasında yazılmış nesne ve etkin olmayan sürüm satırı için temizlik çağrısı görülmedi (gözlem).
5. Modele "düzenlenen belgeyi yeniden oku ve [N] atıflarıyla kanıtla" talimatı verilir; indirme bağlantısı yanıta yazılmaz (`toolDispatcher.ts:1575-1580`).

### 7. Kabul / ret mekaniği

İki yol vardır.

1. Sunucu yolu (düzenleme kartları): `POST /single-documents/:id/edits/:editId/accept|reject` (`documents.routes.ts:386-424`), işlev `resolveEdit` (`documents.edits.ts:21-229`). Kayıt zaten çözülmüşse yanıt eşdeğer ve hata vermez (`:52-91`). Aksi hâlde: etkin sürüm baytları indirilir, `w:id` kimlikleri `document_edits` satırından alınır, `resolveTrackedChange` ağacı dolaşır (`docxTrackedChanges.ts:1016-1121`). Kurallar: ekleme kabulü sarmalayıcıyı kaldırıp içeriği tutar; silme reddi sarmalayıcıyı kaldırıp `w:delText` etiketlerini `w:t`'ye çevirir; silme kabulü ve ekleme reddi sarmalayıcıyı içeriğiyle birlikte atar (`:1040-1064`, `:1080-1096`). Kimlik belgede bulunamazsa yalnızca durum güncellenir (başka bir kabul/ret turu tüketmiş olabilir) (`documents.edits.ts:137-163`). Sonuç yeni nesneye yazılır ve yol/hash/boyut tek koşullu güncellemeyle değiştirilir, PDF rendition null yapılır (`:165-193`).
2. Editör yolu (EigenPal): tarayıcı içi DOCX editörü "Suggesting" kipinde değişiklikleri `w:ins`/`w:del` olarak kendi çekirdeğiyle seri hâle getirir; sağ tık ile kabul/ret revizyon kimliği, yazar, tarih ve belge parçasıyla eşlenir; otomatik kayıt 1,5 sn sonra olur ve içerik hash'iyle koşullu sürüm değiştirme kullanır (`docs/docx-preview-engines.md:57-76`, `:101-106`, `:139-143`).

Önemli ayrım: model tarafından üretilen redline'ın kabul/ret'i kendi XML kodumuza, kullanıcı tarafından üretilenin ise editör motoruna aittir. Dokümantasyona göre editör sürümü 2.21.1'e sabitlenmiştir (`docs/docx-preview-engines.md:86`), ancak `frontend/package.json:23-25` 2.27.0 gösterir; belge ile paket arasında tutarsızlık var.

### 8. Belge üretimi (DOCX / XLSX / PPTX)

Ortak son aşama `persistGeneratedFile` (`documentOps.ts:918-1042`): dosya adı başlıktan türetilir (Unicode harf/rakam/işaret, 64 birim sınırı, grapheme güvenli; `:554-575`), nesne yüklenir, PPTX için PDF rendition (zaman uyumlu ya da kuyruğa ertelenmiş) üretilir, `documents` ve `document_versions` (`source='generated'`, `version_number=1`, hash) satırları yazılır; üretilen belge de sonradan `edit_document` ile düzenlenebilir.

- DOCX (`generateDocx`, `documentOps.ts:69-531`): `docx` kütüphanesi. Girdi şeması: `title`, `landscape`, `numberSections`, `sections[]` ve her bölümde `heading`, `level`, `content`, `pageBreak`, `table{headers, rows}` (`toolSchemas.ts:304-377`). Sabit yazı tipi Times New Roman 11 pt, başlık büyük harf (`:101-102`, `:113`). `content` tek satır sonuna göre bölünür, boş satırlar atlanır; araç açıklaması ise "çift satır sonu" der (`toolSchemas.ts:342` ile `documentOps.ts:434-436` arası tutarsızlık). `-`, `•`, `*` ile başlayan satırlar madde işareti olur; `numberSections` açıkken "1.", "1.2", "(a)", "(i)" biçimli elle numaralar Word çok düzeyli numaralamasına çevrilir (`:229-253`, `:434-478`). Üretimden sonra paketin `[Content_Types].xml`, `word/document.xml`, `word/_rels/document.xml.rels` parçalarını içerdiği denetlenir (`:499-512`).
- XLSX (`buildXlsxWorkbook`, `:613-732`): kütüphane yok; JSZip ile elle OOXML yazılır. Şema: `sheets[{name, columns[], rows[][]}]`; tüm hücreler `inlineStr` metindir (sayı/tarih/formül/stil yok); sayfa adı 31 karakterle ve yasaklı karakterler temizlenerek sınırlanır (`:597-600`). Başlık satırı dışında biçimlendirme yoktur.
- PPTX (`buildPptxPresentation`, `:755-916`): yine elle OOXML. Şema: `slides[{title, bullets[]}]` (`notes` şemada var ama kullanılmaz; `toolSchemas.ts:455-458`). Her slayt boş bir düzen ve iki metin kutusundan oluşur (başlık 32 pt kalın, maddeler 20 pt), 16:9. Tema/yazı tipi "Aptos" sabit.

### 9. Ön izleme motorları

- DOCX: yalnızca EigenPal (`@docx-editor.dev/react|core|fonts`) tarayıcı içi editörü; motor seçici yok; yazı tipleri paketlenmiş ve metrik uyumlu; yükleme gecikmeli (lazy). Salt-okunur/düzenle/öneri (Suggesting) kipleri, yorum sütunu, gezinme paneli, otomatik kayıt, sürüm menüsü vardır. Tam Word uyumluluğu iddia edilmez; yazı tipi ikamesi satır sonlarını ve sayfalamayı değiştirebilir (`docs/docx-preview-engines.md:1-4`, `:84-92`, `:153-157`). Yalnızca Apache-2.0 çekirdek paketleri kullanılır (`:94-99`).
- PDF: pdfjs-dist ile `PdfView`; alıntı vurgulama için ön yüzde de aynı okuma sırası modülünün kopyası kullanılır (`highlightQuote.ts`, `pdfTextOrder.ts`).
- XLSX: `@fortune-sheet` ile ham bayttan yerel ızgara; PDF rendition kullanılmaz çünkü geniş sayfaları kırpıyordu (`documentTypes.ts:39-47`).
- PPTX ve DOC/PPT: LibreOffice ile PDF'e dönüştürülmüş rendition gösterilir; yoksa istek anında dönüştürülür (`documentDisplay.ts:69-100`). Dönüştürme: `libreoffice-convert` ya da doğrudan `soffice --headless --convert-to pdf`, kullanıcı profili geçici dizinde, zaman aşımıyla öldürme (`convert.ts:144-267`).

### 10. Tamper-evident (kurcalamaya açık) dışa aktarım

(`docs/tamper-evident-exports.md`, `backend/src/modules/user/user.dataExport.ts:318-411`, `backend/src/lib/manifestSigning.ts`)

- `GET /projects/:projectId/export` bir manifest döndürür: proje, bellek, her belge için etkin sürüm kimliği, tüm sürümler (kimlik, sürüm no, kaynak, dosya adı, tür, boyut, `content_sha256`, `deleted_at`, `created_at`) ve her `document_edits` kaydı için yalnızca `id, version_id, change_id, status, created_at, resolved_at`. Düzenlemenin metni manifestte yoktur (`user.dataExport.ts:380-410`).
- Yumuşak silinmiş sürümler manifestte kalır; dosya adı ve zaman damgası sızar, bunu belge bilerek yazar (`docs/tamper-evident-exports.md:17-22`).
- Hash'i olmayan eski sürümler `null` olur; "doğrulanamaz" sayılır, yanlış biçimde doğrulanmış gösterilmez (`docs/tamper-evident-exports.md:14-15`, `user.dataExport.ts:314-316`).
- Gövde özeti: nesne anahtarları sıralı, dizi sırası korunmuş, boşluksuz kurallı JSON üzerinde SHA-256. NaN/Infinity ve düz olmayan nesneler hata fırlatır (`manifestSigning.ts:134-171`).
- İsteğe bağlı imza: `MANIFEST_SIGNING_KEY` 32 baytlık Ed25519 tohumu (hex). İmzalanan veri: `"mike-project-manifest-v1"` + NUL + özet baytları (alan ayrımı; `:37-44`, `:182-199`). Anahtar yanlış biçimliyse sessizce imzasız çıkmak yerine hata fırlatır (`:67-78`). Doğrulayıcı açık anahtarı manifestten değil `GET /manifest-signing-key` uç noktasından almalıdır (`app.ts:357`, belge `docs/tamper-evident-exports.md:62`); anahtar döndürmek eski dışa aktarımları geçersiz kılmaz ama doğrulayıcının o günkü açık anahtarı bilmesi gerekir (`docs/tamper-evident-exports.md:66-67`).
- Sınırlar (gözlem): hash zinciri yoktur, sürümler birbirine bağlanmaz; yerinde değiştirilen bir sürümün önceki baytlarının hash'i manifestte tutulmaz; yalnızca o anki durum kanıtlanır. Kabul/ret kayıtlarında kimin yaptığı alanı manifestte yoktur (seçilen alanlar yukarıda). Denetim günlüğü (`audit`) ayrı bir modüldür, bu bölümde okunmadı.

## HakHukuk için değerlendirme

### Taşınır

- Yükleme ardışık düzeni deseni: mühürlenmiş nesne, akış sırasında SHA-256 ve boyut denetimi, sonra türe özel işlem, içerik hash'iyle kaydetme (`uploads.processing.ts:285-327`). SQLite + yerel dosya sisteminde tek kullanıcı için daha da sade yazılır.
- Taranmış PDF için "metin katmanı yok" tespiti ve modele açık bildirim (`pdfText.ts:281-284`, `:325-353`) ve yükleme anında sayfa sayısı/metinsiz sayfa sayısı saklama.
- PDF'te `[Page N]` işaretli, okuma sırası düzeltilmiş (XY-kesme sütun ayrımı) metin; bu, 4B modelin sayfa+alıntı biçiminde atıf vermesini ve sunucunun doğrulamasını mümkün kılar. Python'da `pdfplumber`/`PyMuPDF` ile aynı fikir uygulanır; algoritmayı yeniden yazmak gerekir (kod kopyalanmaz).
- İzlenen değişiklik üretiminin temel fikri: paragraf içi düz metin üzerinde arama, eşleşen karakter aralığını koşulara geri haritalama, `w:del`/`w:ins` üretme, `rPr`'yi koşudan miras alma, ortak önek/sonek kırpma. Python'da `python-docx` + `lxml` ile aynı yapılabilir.
- Kabul/ret kuralları (dört durumun tablosu) ve "zaten çözülmüş ise idempotent yanıt" (`documents.edits.ts:52-91`).
- Eşleştirmede belge metnini "doğruluk kaynağı" alma: silinen metin modelin değil belgenin metni olarak saklanır (`docxTrackedChanges.ts:923-929`).
- Salt okunur açıklamalı sürüm: etkin sürüm göstergesi + `assistant_edit` kaynağı + düzenleme kayıtları; SQLite'ta aynı tablolar.
- Hash'li sürüm satırı ve imzalı manifest: tek kullanıcılı yerel uygulamada kullanıcıya "bu dosya bu hâlde" kanıtı veren hafif bir mekanizma; Ed25519 imzası isteğe bağlı bırakılabilir.
- Üretim: DOCX için `python-docx`; XLSX/PPTX gereksinimi HakHukuk için düşük öncelikli.

### Yeniden tasarlanmalı

- `edit_document` komut şeması 4B için ağırdır: dört zorunlu alan, ~40 karakterlik bağlam kopyalama (`toolSchemas.ts:488-513`). Küçük model bağlamı birebir kopyalayamaz veya halüsinasyon yapar. Aşağıda "Sadeleştirilmiş komut şeması" önerilmiştir.
- Tam metni tek araç sonucu olarak dönmek (kırpma yok; `documentOps.ts:1447-1679`) 4B'nin dar bağlamı (tipik 8-32 K) için uygun değildir. Sayfa/paragraf/madde bazlı sayfalama ve hedefli getirme gerekir; Mike'ın "belgeyi bir kez tam oku" varsayımı bulut modeline göredir.
- Türkçe büyük/küçük harf: `normalizeWithMap` her karakteri `toLowerCase()` ile ekler ama indeks dizisine tek eleman yazar (`documentOps.ts:1721-1723`). `İ` küçük harfe iki karakter (`i` + birleştirici nokta) dönüşür; çalıştırılarak doğrulandı: "İSTANBUL ISPARTA" uzunluğu 16'dan 17'ye çıkıyor. Sonuç: normalleştirilmiş dize ile `origIdx` aynı uzunlukta kalmaz, `İ` sonrası tüm konum eşlemeleri kayar (`find_in_document` alıntısı ve alıntı doğrulama etkilenir, `verifyCitations.ts:140-143`). Ayrıca `I`→`i` (Türkçede `ı`) ve `İ`→`i` kuralları farklıdır: "ISPARTA" ile "ısparta" büyük/küçük duyarsız eşleşmez. Bizde konum haritalı, Türkçe duyarlı katlama (`İ→i`, `I→ı`, NFC) gerekir.
- Ön yüzde alıntı vurgulama yalnızca `[a-zA-Z0-9]` karakterlerini tutar (`highlightQuote.ts:17-20`, `:33-41`). Türkçe harfler (ç ğ ı ö ş ü İ) silinir; "ağır" ile "ar" aynı hâle gelir, yanlış yerde vurgulama veya sahte eşleşme riski doğar. Kendi vurgulayıcımızda Unicode harf sınıfı (`\p{L}`) kullanılmalı.
- DOCX üretiminde İngilizce varsayımlar: başlık normalleştirme yalnızca ASCII (`documentOps.ts:254-259`), numarasız başlık tespiti İngilizce kelimelere bağlı (`agreement|contract|deed|terms|policy|notice|nda|disclosure`, "signatures"; `:269`, `:278`, `:286`), `toUpperCase()` Türkçe `i→İ` yapmaz (`:113`, `:339`). Türk hukuk metni hiyerarşisi (madde, fıkra, bent) için ayrı numaralama şablonu yazılmalı; "MADDE 1 –" biçimi elle numara regex'lerince tanınmaz (`:232`, `:243`).
- DOCX çıkarımının kapsamı: hiperbağlantı, alan kodu, metin kutusu içindeki metin, üst/alt bilgi ve dipnotlar okunmaz; sekme ve satır sonu metne yansımaz (örn. "Madde 1<sekme>metin" yapışık okunabilir; kodtan çıkarım, çalıştırılmadı) (`docxTrackedChanges.ts:240`, `:248-257`, `:9-10`). Türk sözleşmelerinde numara sonrası sekme yaygındır; çıkarımda sekme, `w:br` ve hiperbağlantı metni açıkça işlenmeli.
- Yeniden kurulumda metin dışı koşu çocuklarının kaybı riski (bkz. adım 12) bir hukuk belgesinde kabul edilemez; dokunulan aralık koşuları yerine, yalnızca gerçekten silinen/eklenen karakter aralığı bölünmeli, dokunulmayan koşular olduğu gibi bırakılmalı.
- Sayfa modeli: DOCX'te sayfa yoktur; Mike atıfta `page` ister ama DOCX için `page_count` null. HakHukuk'te mevzuat atfı zaten madde/fıkra/bent adresli olduğu için DOCX'te paragraf kimliği, PDF'te sayfa+blok kimliği kullanılmalı.
- Sürüm değişmezliği: yerinde bayt göstergesi değiştirme ve `created_at` ezme (yukarıda) yerine "her yazım yeni sürüm, eskiler kalır" modeli daha sadedir; tek kullanıcıda depolama maliyeti ihmal edilebilir. Yalnızca kayıt anında değil sürüm zinciri için önceki hash'i de içeren zincirleme hash eklenebilir (Mike'da yok).
- İzin/ekip/organizasyon denetimleri (`ensureDocAccess`, `can(...)`) tek kullanıcı için gereksizdir.

### Taşınmaz

- LibreOffice hattı (PDF rendition, DOC/PPT metni): ağır bağımlılık; yerel masaüstünde kurulum yükü ve çalışma süresi var. İstenirse yalnızca isteğe bağlı eklenti olmalı; `.doc` için daha hafif bir yol (örn. `antiword`/`catdoc` benzeri, tahmin) değerlendirilebilir.
- EigenPal tarayıcı içi DOCX editörü ve yorum/inceleme paneli: kapsamlı ön yüz yatırımı; kendi frontend'imizde aynı derinlikte yeniden kurmak gerekmez. Paket 2.x sürümüne ve hızlı değişen bir API'ye bağlı (belgeyle paket sürümü tutarsız, bkz. adım 7 notu).
- Kuyruk/BullMQ/dbq tabanlı işçi, çok kiracılı depolama yönetimi, imzalı URL ve indirme belirteçleri: tek kullanıcılı yerel uygulamada FastAPI arka plan görevi ve yerel dosya yolu yeter.
- Elle yazılmış XLSX/PPTX OOXML üretimi: kırılgan; ihtiyaç doğarsa hazır kütüphane (`openpyxl`, `python-pptx`) tercih edilir.

## Türkçe belgeler için önerilen çıkarım hattı

Not: Bu bölüm Mike'dan okunmayan kısımlar içerir (UDF, OCR); bunlar öneri/tahmindir ve gerçek örneklerle doğrulanmalıdır.

1. Tür belirleme: uzantıya değil içerik imzasına bak (ZIP `PK`, `%PDF`, OLE `D0CF11E0`). Mike yalnızca uzantıya bakar.
2. UDF (UYAP Doküman Formatı): Mike desteklemez. Bilgiye dayalı öneri (kaynakta yok, doğrulanmalı): UDF'nin ZIP kapsayıcı olduğu ve içinde `content.xml` ile metin ve biçim aralıklarının bulunduğu bilinmektedir; salt metin çıkarımı için ZIP açıp `content.xml` içinden metni almak yeterli olabilir. Üretilen çıktı UDF değil DOCX/PDF olmalı. UDF örnekleriyle (gerçek UYAP çıktıları) deneme yapılmadan ayrıntı verilmemelidir.
3. DOCX: Mike gibi kabul edilmiş görünüm + paragraf düzleştirme, ama paragraf kimliği (sıra numarası), tablo hücresi bağlamı, sekme, hiperbağlantı ve dipnot desteğiyle; çıktı "[¶12]" öneki taşıyan satırlar.
4. Metin katmanlı PDF: pdfjs yerine Python'da `PyMuPDF` ya da `pdfplumber`; Mike'ın [Page N] + sütun ayrımı fikri korunur. Eski UYAP/e-imzalı PDF'lerde yazı tipi kodlamasından kaynaklanan bozuk Türkçe karakter (ToUnicode eksikliği) riski vardır (tahmin); bir örnek korpusla ölçülmeli.
5. Taranmış PDF: Mike gibi önce metin katmanı tespiti (sayfa bazında), yoksa OCR hattına yönlendir. Önerilen OCR adayları (kaynakta yok, denenmemiş): Tesseract `tur` modeli, PaddleOCR, docTR; doğruluk Türkçe hukuki taramalarda ölçülmeli. OCR çıktısı "kaynak: OCR, güven: x" etiketiyle saklanmalı ve atıf doğrulamasında düşük güvenli sayfa işaretlenmeli. OCR ve vektörleme yükü yerel GPU/CPU için ayrı bir iş kuyruğunda çalışmalı (bkz. proje CLAUDE.md: kiralık GPU ilkesi).
6. Kanonik gösterim: tüm türler için aynı ara biçim: `{belge, sürüm, sayfa|bölüm, paragraf_no, metin}` kayıtları; model bu kayıtların kimlikleriyle konuşur. Mevzuat atıfları (madde/fıkra/bent) için ayrı ayrıştırıcı.
7. Normalleştirme: NFC, Türkçe duyarlı katlama (`İ→i`, `I→ı`), NBSP, akıllı tırnak ve kısa/uzun tireleri Mike gibi eşleme; ayrıca Türkçe hukuk metinlerinde sık "–"/"-" ve "…" varyantları.
8. Sayfalama: modele bir seferde belge değil, kimlikli paragraf pencereleri ver (örn. 2-4 K token), `find_in_document` ile hedefli getirme; Mike'ın "bir kez tam oku" kuralı küçük modelde bırakılmalı.

## Sadeleştirilmiş komut şeması (4B için öneri)

Mike'ın Word eklentisi için ayrıca daha sade bir şema kullandığı görüldü: `original`, `replacement`, `reason`, isteğe bağlı `formats` ve `occurrence:"all"`, bağlam alanı yok, `original` en çok 200 karakter, çağrı başına en çok 50 düzenleme ve belirsiz/bulunamaz hatalarını satır satır geri bildirme (`wordClientTools.ts:60-100`, `:102-178`). DOCX aracının dört zorunlu alanlı şemasına göre daha uygundur. Bizim için öneri:

- Okuma çıktısı her paragrafı kararlı bir kimlikle verir: `[p12] metin`. Tablo hücresi için `[p12.t3.r2.c1]` gibi.
- Tek tür komut, üç alan: `{"p": 12, "bul": "...", "yerine": "..."}`; `bul` yalnızca o paragrafta aranır (belirsizlik neredeyse ortadan kalkar; bağlam alanları gereksiz olur). `bul` boş ve `yerine` doluysa paragraf sonuna ekleme; `yerine` boşsa silme. Paragraf içinde aynı dize birden fazlaysa sunucu `"sira": 2` ister (isteğe bağlı sayısal alan), model uzun bağlam kopyalamaz.
- `neden` isteğe bağlı ve kısa (Mike'da zorunlu değil ama sunum için gerekli).
- Çağrı başına düşük sınır (örn. 5-10 düzenleme); hatalı olan düzenleme yalnızca kendi hata satırıyla dönsün (Mike'da zaten kısmi başarı var, `toolDispatcher.ts:1564-1582`).
- Sunucu doğrulama ve onarım sırası: (a) paragraf kimliği geçerli mi; (b) `bul` Türkçe duyarlı normalleştirmeden sonra bu paragrafta tam bir kez geçiyor mu; (c) geçmiyorsa en yakın benzer parçayı (kenar-uzaklığı) hata mesajına koy, modele "şunu mu kastettin" olarak geri ver; sessiz bulanık uygulama yapma (hukuk belgesinde yanlış düzenleme riski).
- llama.cpp'nin JSON şeması/GBNF kısıtlı çözümlemesi ile bu şemayı zorunlu kıl (Mike'dan bağımsız; kısıtlı çözümleme kullanımı bizim tasarım seçimimiz, burada denenmedi). Böylece geçersiz JSON üretimi ortadan kalkar.
- Tek paragrafın dışına taşan düzenleme (paragraf birleştirme/bölme) ilk sürümde desteklenmez; Mike da desteklemez (`docxTrackedChanges.ts:802-804`).

## Açık sorular

1. `create_document_version` ve `delete_document_version` RPC'lerinin SQL gövdeleri bu depoda yok; sürüm numaralama ve silme anındaki işlemsel garantiler doğrulanamadı.
2. Kabul/ret kararı kimin verdiğini tutuyor mu (denetim günlüğü)? `document_edits` seçilen alanlarında kullanıcı kimliği görülmedi; `audit` modülü bu bölümde okunmadı.
3. EigenPal çekirdeği DOCX'i seri hâle getirirken bizim `w:id` kimliklerimizle çakışmayı nasıl önler? İki yazıcı (sunucu ve editör) aynı belge üzerinde çalışıyor.
4. `highlightDocxQuote.ts` ve DOCX atıf konumlama (sayfa olmadan hangi konuma gidiyor) okunmadı.
5. Türkçe karakter içeren gerçek hukuk DOCX/PDF örnekleriyle `extractDocxBodyText` ve pdfjs çıktısının davranışı denenmedi; özellikle sekme/hiperbağlantı yapışması ve eski PDF'lerde bozuk karakter eşleme.
6. UDF yapısı ve en iyi çıkarım yöntemi gerçek UYAP örnekleriyle doğrulanmadı.
7. Ön yüz kabul/ret için hangi yolu ne zaman kullanıyor (sunucu `resolveEdit` ile editör içi kabul arasındaki geçiş) tam çıkarılmadı.

## Okunmadı

- `backend/src/modules/documents/documents.cleanupJobs.ts` (yalnızca başı), `documents.cleanup.ts`, `documents.copyFiles.ts`, `documents.rename.ts`, `documents.maintenance.ts`, `documents.access.ts`.
- `backend/src/modules/uploads/uploads.sessions.ts` ve `uploads.routes.ts` (yalnızca limit/tür denetimi için ilgili satırlar tarandı), `uploads.access.ts`; `uploads.processing.ts` 780 sonrası (işçi döngüsü, yeniden deneme, oturum durumu).
- `backend/src/lib/storage.ts` (S3/R2 istemci ve imza ayrıntıları), `downloadTokens.ts`, `zipExport.ts`, `auditExport.ts`, `audit.ts`.
- `backend/src/lib/pdfTextOrder.ts` 140 sonrası (XY-kesme gövdesi); `pdfjs.ts` yalnızca tür sarmalayıcı olarak okundu.
- Testler: `pdfText.test.ts`, `pdfText.integration.test.ts`, `documentOps.test.ts`, `documents*.routes.test.ts`, `uploadSessions*.test.ts`, `manifestSigning.test.ts` içerikleri okunmadı; `docxTrackedChanges.test.ts` yalnızca ilk 120 satırı ve `it(...)` başlıkları okundu. Bu testlerde çok koşulu biçim, sekme, tablo, üst/alt bilgi senaryosu görünmedi (başlıklardan çıkarım).
- Ön yüz: `DocxView.tsx`, `EigenpalDocxRenderer.tsx`, `DocxReview*.tsx`, `PdfView.tsx`, `SpreadsheetView.tsx`, `highlightDocxQuote.ts`, `DocumentContent.tsx` gövdeleri okunmadı; `highlightQuote.ts` yalnızca ilk 80 satırı okundu.
- `supabase/` altında yalnızca `gateway.conf` vardır; veritabanı şeması ve RPC tanımları depoda bulunamadı.
- `word-addin/`, `desktop/`, `e2e/`, `loadtest/` okunmadı (ilgili olduğu ölçüde yalnızca `backend/.../wordClientTools.ts` ve `wordPrompt.ts` anılması okundu).
- Hiçbir kod çalıştırılmadı (yalnızca `"İSTANBUL ISPARTA".toLowerCase()` uzunluğu Node ile ölçüldü); "çıkarım" ve "tahmin" olarak işaretlenen davranışlar çalıştırılarak doğrulanmamıştır.
