# Mike: atıf üretimi ve doğrulama, bağlam oluşturma, hafıza

Kaynak: Mike (TypeScript, AGPL-3.0), salt-okunur kopya. Tüm yollar `mike-main/` köküne göredir. Kod kopyalanmamıştır; tasarım kendi cümlelerimle anlatılmıştır, alıntılar 3 satırı aşmaz. "Tahmin" yazılan yerler ölçülmemiş çıkarımlardır.

## Kapsam ve okunan dosyalar

Tamamı okunanlar:

- `backend/src/modules/chat/engine/verifyCitations.ts` (447 satır)
- `backend/src/modules/chat/engine/citations.ts` (347 satır)
- `backend/src/modules/chat/engine/tools/courtlistenerTools.ts` (139 satır)
- `backend/src/modules/chat/engine/tools/courtlistenerTurnState.ts` (246 satır; atanmış değildi, doğrulama zincirinin parçası olduğu için okundu)
- `backend/src/lib/memory/files.ts`, `prompt.ts`, `schedule.ts`, `archive.ts`, `bulk.ts`
- `backend/src/modules/memory/memory.service.ts`, `memory.routes.ts` (60-228)
- `docs/memory.md`, `docs/courtlistener.md`

Kısmen okunanlar (okunan aralıklar belirtilmiştir):

- `backend/src/modules/chat/engine/contextBuilders.ts` (1605 satır): 1-330 (spotlighting, kişiselleştirme), 360-470 ve 520-575 (önceki tur özeti), 575-800 (Word bağlamı, `buildMessages`, zaman damgası), 806-836, 1200-1605 (belge ve proje bağlamı, workflow deposu). Atlanan: 330-360 ve 470-520 (muhakeme tekrarı, `ask_inputs` özet satırları), 836-1200 (ask_inputs yükü ayrıştırma, mesaj ekleme yardımcıları).
- `backend/src/lib/courtlistener.ts` (1205 satır): 1-130, 160-260, 436-560, 740-800, 955-1205. Atlanan: HTML temizleme (260-436), toplu veri (bulk) içi ayrıntılar (560-740, 800-955).
- `backend/src/modules/memory/memory.curator.ts` (1536 satır): 1-217, 218-330, 381-452, 620-952, 1085-1536. Atlanan: 453-620 (`loadConversation`), 953-1085 (durum yardımcıları).

Doğrulama için ek olarak bakılan, atanmamış yerler (yalnız ilgili aralık):

- `backend/src/modules/chat/engine/tools/documentOps.ts` 42-61, 1412-1445, 1447-1680 (`normalizeWithMap`, `citationReminder`, `readDocumentContent`)
- `backend/src/modules/chat/engine/streaming.ts` 290-376, 380-450, 780-850
- `backend/src/modules/chat/engine/tools/toolDispatcher.ts` 555-640, 929-1089, 1090-1304, 1305-1420
- `backend/src/modules/chat/engine/prompts.ts` 1-119
- `backend/src/lib/pdfText.ts` 225-280, `frontend/.../pdfTextOrder.ts` 1-40
- `frontend/src/app/components/assistant/message/citationVerification.tsx`, `frontend/src/app/components/shared/types.ts` 355-410 ve 580-680
- `backend/src/modules/tabular/tabular.chats.ts` 60-145
- `backend/schema.sql` 6384-6560 (`write_memory_file` SQL gövdesi)
- `backend/src/modules/chat/chat.routes.ts` 700-780, 895-970

Bu dosyada önceki yüzeysel okumanın içeriği bilinmediğinden, "düzeltme" olarak işaretlenen maddeler doğrudan dokümantasyon ile kodun çeliştiği yerlerdir.

---

## Nasıl çalışıyor

### 1. Atıf biçimi ve ayrıştırma

**Model çıktısı.** Model, cevabın gövdesinde `[1]`, `[2]` gibi sıralı işaretler koyar ve cevabın en sonuna `<CITATIONS>` etiketleri arasında bir JSON dizisi ekler (`backend/src/modules/chat/engine/prompts.ts:27-52`). Her kayıt `ref`, `doc_id` ve en çok 3 adet `{page, quote}` içerir. `doc_id` sohbete özgü etikettir (`doc-0`); dosya adı veya UUID yasaktır (prompts.ts:44). Alıntı için yönerge: kısa (ideal olarak 25 kelime veya daha az, prompts.ts:46), kelimesi kelimesine, tek bir sayfa için. İki sayfaya yayılan alıntı için `page: "N-M"` ve metin içinde `[[PAGE_BREAK]]` sentineli kullanılır (prompts.ts:50). Elektronik tabloda sayfa yerine `sheet` + `cell` (A1 adresi veya aralık) kullanılır (prompts.ts:48-49). Boş atıf varsa blok hiç yazılmaz (prompts.ts:52).

**Yönergenin tekrarı.** Model bir belgeyi `read_document` ile okuduğunda, araç sonucunun başına belgeye özel bir "atıf hatırlatması" eklenir; hatırlatma doğru `doc_id` ve JSON şeklini yeniden söyler (documentOps.ts:42-61; eklendiği yer toolDispatcher.ts:608-615). Yani biçim kuralı yalnız sistem isteminde değil, her okumanın hemen yanında da bulunur. Bu, küçük modelde kuralın uzak bağlamda unutulmasına karşı bir önlemdir (tahmin: tasarım niyeti buydu).

**Ayrıştırma.** `parseCitationsWithDiagnostics` tek bir düzenli ifadeyle bloğu yakalar, `JSON.parse` yapar ve dizi değilse veya ayrıştırma çökerse boş liste döndürür; ayrıca neyin ters gittiğini söyleyen bir tanı nesnesi verir (citations.ts:185-226). Başarısız ayrıştırma hata fırlatmaz: sessizce "atıf yok" sonucu çıkar, yalnızca geliştirici günlüğüne (`devLog`) yazılır (streaming.ts:~850 civarı, `devLog("[chat/stream] final citations"...)`). Kullanıcıya "atıf bloğu bozuktu" diye bir sinyal gitmez (bu okuduğum aralıkta böyle bir sinyal yok; tüm arayüz kodu taranmadı).

**Normalleştirme (`normalizeCitation`).** Esnek kabul: `ref` sayı veya `marker: "[3]"` biçimi; `quote` yerine `text` anahtarı; `cluster_id` sayı veya sayı-metni; `quotes` yoksa üst düzey `quote`/`page` tek elemanlı diziye çevrilir (citations.ts:46-101). Sayfa değeri sayı, `"41-42"` biçimi veya çözümlenemezse 1'dir (citations.ts:113-123): yani sayfa yanlışsa sessizce 1 olur. Alıntı sayısı 3 ile kırpılır (citations.ts:130, 152). `cluster_id` pozitif sayı ise kayıt "içtihat" türüne, aksi halde `doc_id` metinse "belge" türüne gider; ikisi de yoksa kayıt atılır (citations.ts:72-81).

**Akış sırasında kısmi atıf.** Model akarken görünür metin ile atıf bloğu ayrılır: `<CITATIONS>` etiketinin yarısının bir parçada gelme ihtimaline karşı son (etiket uzunluğu - 1) karakter bir "kuyruk tamponunda" tutulur (streaming.ts:421-453). Etiket görülünce görünür akış kesilir, sonrası gizli tampona gider; tamponda tamamlanmış her JSON nesnesi (tırnak ve kaçış durumunu izleyen elle yazılmış bir ayrıştırıcıyla, citations.ts:232-268) çıkarılıp `status: "partial"` olay çerçevesi olarak istemciye gönderilir (streaming.ts:400-419). Bu kısmi atıflar henüz doğrulanmamıştır; sonunda doğrulanmış `status: "final"` çerçevesi bunları değiştirir (streaming.ts:848).

**Atıf kaydının zenginleştirilmesi (`createCitation`).** Ayrıştırılmış kayıt, `doc_id`'yi sohbet içi indeks aracılığıyla gerçek `document_id`, dosya adı, sürüm numarasına bağlar (citations.ts:278-347). İçtihat kaydı için tur içi önbellekten dava adı, künye, URL, tarih eklenir (citations.ts:284-308).

### 2. Doğrulama algoritması (adım adım)

Doğrulama, modelin bitmiş cevabı üzerinde, sunucuda, akış bittikten sonra bir kez yapılır (streaming.ts:798-846). Belge türü için kaynak metin `readDocumentContent` ile, olay yayını kapalı biçimde (`emitEvents:false`, streaming.ts:825), doc_id başına en çok bir kez (Promise önbelleği, streaming.ts:817-830) okunur. Bu, modelin gördüğü metnin aynısıdır: aynı çıkarıcı kullanılır (docx için model ile aynı düzleştirme; documentOps.ts:~1578-1585 yorumu; PDF için `extractPdfTextForModel`, documentOps.ts:1568).

**Yapılan şey:** "model alıntısı kaynak metinde bulunuyor mu". Yapılmayan şey: "iddia alıntı tarafından destekleniyor mu" (bunu hiçbir yerde ölçmüyor; aşağıda 2.7).

Her alıntı için `verifyQuoteAgainstSource` (verifyCitations.ts:162-253) şu sırayı izler:

1. **Kaynak yok kapısı.** Kaynak boşsa veya okuma hatası sentinel'i ("Document could not be read." / "Document not found.") ise alıntı doğrudan `verified:false` olur, yanlış eşleşme aramaz (verifyCitations.ts:19-25, 166-168). Sentinel metinleri `readDocumentContent` döndürür (documentOps.ts:1551, 1677). Bu kapı, hata dizesinin kendisine yanlış-negatif eşleşmeyi önler.
2. **Sayfa sınırı dalı.** Alıntıda `[[PAGE_BREAK]]` varsa parçalara bölünür, her parça ayrı doğrulanır (özyinelemeli). Hepsi bulunduysa ikinci bir sınama gelir: tüm parçaların (üç noktalı alt parçalar dahil) belgede **sırayla** ve ardışık parçalar arası **en çok 5 000 karakter** boşlukla bulunması gerekir (verifyCitations.ts:13, 170-212). Sınama geri izlemelidir: bir parçanın ilk geçişi zinciri tamamlamıyorsa sonraki geçişe geçilir; toplam deneme sayısı 64 ile sınırlıdır, aşılırsa "bulunamadı" (fail-closed) (verifyCitations.ts:17, 102-135). Not: 64 sayacı tüm zincir için ortaktır, parça başına değil (verifyCitations.ts:107, 117-118).
3. **Üç nokta dalı.** `...` veya `…` içeren alıntı parçalara bölünür, harf/rakam içermeyen artıklar atılır, her parça **bağımsız** aranır (verifyCitations.ts:218-242). Burada sıra ve yakınlık denetimi **yoktur** (yalnız sayfa sınırı dalında vardır). Bulunan kesitler `" ... "` ile birleştirilip `source_excerpt` olur.
4. **Tek parça.** `locateQuote` üç kademeli arama yapar ve ilk isabette durur (verifyCitations.ts:41-58):
   - Kademe 1: birebir alt dize (`indexOf`).
   - Kademe 2: boşluk daraltma + küçük harf.
   - Kademe 3: boşluk daraltma + küçük harf + **noktalama atma**; noktalama "harf, rakam veya boşluk olmayan her karakter"dir ve tamamen silinir, yerine boşluk konmaz (documentOps.ts:1684-1686, 1716-1721). Örnek yorumda: "U.S." -> "us".
5. **Konum geri eşleme.** Normalleştirilmiş metin, normalleştirilmiş karakter -> özgün indeks haritasıyla birlikte üretilir (`normalizeWithMap`, documentOps.ts:1700-1727). Kaynakta eşleşen aralık haritadan özgün aralığa çevrilir ve **kaynaktan** kesit alınır (verifyCitations.ts:137-154). Böylece modelin sapmış metni değil, belgenin kendi cümlesi `source_excerpt` olarak döner.
6. **Kayma düzeltme.** Kesit, modelin yazdığı alıntıdan farklıysa `needs_correction` true olur (verifyCitations.ts:248). Sonraki adımda ekranda gösterilecek `quote` alanı modelin yazdığı metin yerine kaynak kesitiyle **değiştirilir**: "kayan alıntı hiçbir zaman kaynağın sözü gibi sunulmaz" (verifyCitations.ts:403-408; içtihat için 348-351). `needs_correction` bayrağı istemciye gitmez, kullanılıp atılır (verifyCitations.ts:402).
7. **Bayraklar.** Alıntı başına `verification = {verified, source_excerpt?, start_char?, end_char?}`. Karakter ofsetleri yalnız tek parçalı (bitişik) alıntılarda eklenir (verifyCitations.ts:156-161, 246-252). Atıf düzeyinde `verified` = tüm alıntıların `verified` değerinin VE'si (verifyCitations.ts:412, 419-425). Belge kaydının içindeki `document.quotes[i]` de aynı doğrulama ve düzeltilmiş metinle güncellenir (verifyCitations.ts:274-295).
8. **Hata durumları.** (a) Kaynak okunamazsa atıfın tüm alıntıları `verified:false` (verifyCitations.ts:393-398). (b) Atıfta `doc_id` yoksa veya alıntı yoksa kayıt dokunulmadan döner, yani `verified` alanı **hiç eklenmez** (verifyCitations.ts:383-391). (c) İçtihat atıfında `cluster_id` yoksa veya alıntı yoksa yine dokunulmadan döner (verifyCitations.ts:315-329). (d) Kaynak alma hata fırlatırsa içtihat için boş fıkra listesi, belge için boş metin kullanılır, yani fail-closed `false` (verifyCitations.ts:331-336, 393-398).

**İçtihat için fark.** Alıntı, yalnız o tur içinde `courtlistener_get_cases` ile önbelleğe alınmış fıkra metinlerine karşı doğrulanır (`getCachedCaseOpinionTexts`, courtlistenerTurnState.ts:240-246; verifyCitations.ts:309-366). `opinion_id` verilmişse yalnız o fıkraya, verilmemişse tüm fıkraların `\n` ile birleşimine karşı bakılır (verifyCitations.ts:338-346). Modelin o tur çağırmadığı bir `cluster_id` önbellekte yoktur, dolayısıyla tüm alıntılar `false` olur: uydurma `cluster_id` ile doğrulanmış görünmek imkânsızdır.

**Arayüze aktarım.** Doğrulanmış atıflar `{type:"citations", status:"final", citations}` SSE çerçevesiyle gider (streaming.ts:848) ve aynı liste mesajla birlikte veritabanına yazılır (chat.routes.ts:~770-782). Arayüz tek kural uygular: atıf (veya alıntı) düzeyinde `verified === false` ise kırmızı "Could not verify quote" rozeti ve "Quote not found in document" açılır penceresi gösterir; açıklama, alıntıyı halüsinasyon sayıp ilgili bölümü belgeyle tekrar kontrol etmeyi söyler (frontend/src/app/components/assistant/message/citationVerification.tsx:25-35, 57-94). Bayrak **hiç yoksa** durum "verified" sayılır (aynı dosya satır 28 ve 34, `=== false` karşılaştırması).

**Bulgu: fail-open görüntü ve doğrulamasız yollar.** Rozet üç durumlu değildir (doğrulandı / doğrulanamadı / denetlenmedi); "denetlenmedi" yeşil gösterilir. Doğrulamasız çıkan yollar şunlardır:
- Doğrulama bu iki durumda hiç çalışmaz: `buildCitations` verilmişse (tablo incelemesi; streaming.ts:802-804, tabular.chats.ts:60-98: atıf `satır/sütun` ve alıntıdır, hücreye karşı doğrulanmaz).
- İptal edilen veya hata veren turlarda saklanan atıflar `extractCitations` ile üretilir ve doğrulamadan geçmez (chat.routes.ts:902-908, 951; contextBuilders.ts:783-791).
- Kısmi (partial) SSE çerçeveleri (streaming.ts:400-419).

**Bulgu: sayfa/hücre doğrulanmaz.** Doğrulayıcı yalnız `quote` alanına bakar; `page`, `sheet`, `cell` hiçbir kademede denetlenmez (verifyCitations.ts:400-401). Kaynak metin tüm belgedir; alıntı, yazdığı sayfada olmasa bile belgenin herhangi bir yerinde bulunursa "doğrulanmış" olur. Sayfa yalnızca sayfa sınırı dalındaki yakınlık sınamasına dolaylı etki eder. Arayüzdeki "Page N" etiketi (shared/types.ts:644-660) bu yüzden doğrulanmamış bir bilgidir. İlk geçiş: tek parçalı alıntıda ofset ilk eşleşmeyi gösterir (`indexOf`), aynı cümle belgede iki kez geçiyorsa hangisi olduğu belirsiz kalır.

**Bulgu: PDF okuma sırası.** Doğrulama "bitişik alt dize" aradığı için PDF'in düzenlenmesi önemlidir. Backend çıkarıcı çok sütunlu sayfalarda XY-kesimiyle sütunları ayırır ve arayüz görüntüleyicisi aynı sıralamayı **birebir yansıtır**; iki kopya `packages/pdf-text-order/cases.json` ortak test verisiyle senkron tutulur. Gerekçe, yorumda açıkça yazılı: sütunlar birbirine karışırsa iki satırlık alıntı kaynakta bitişik olmaz ve doğrulama başarısız olur (frontend/.../views/pdfTextOrder.ts:1-23; backend karşılığı `backend/src/lib/pdfTextOrder.ts` dosyası açılmadı, adı yorumdan alındı). Her sayfa metni `[Page N]` işaretiyle başlar (pdfText.ts:~274); işaretin kendisi kaynak metnin parçasıdır, bu yüzden `[[PAGE_BREAK]]` sentineli olmadan sayfa sınırından geçen bir alıntı eşleşmez.

### 3. Türkçe/Unicode açısından doğrulayıcının sınırları (kendi deneyimle doğrulandı)

Kod çalıştırılmadı; `normalizeWithMap` ve `locateNormalized` mantığı bir betikte yeniden kuruldu ve Node 24 ile denendi. Bu bir yeniden üretimdir; Mike'ın kendi testlerinde (`verifyCitations.test.ts`, yalnız başlıklar listelendi) bu durumlar yok.

1. **`toLowerCase` yerel ayardan bağımsızdır.** "İ" (noktalı büyük I) küçük harfe "i" + birleştirici nokta (iki kod birimi) olarak çevrilir. "Isparta" ve "ısparta" aynı anahtara inmez. Deneme: kaynakta "Isparta Barosu", alıntıda "ısparta barosu" -> eşleşme yok; kaynakta "İstanbul Barosu kararı", alıntıda "istanbul barosu" -> eşleşme yok. Yani İ/ı içeren çok sayıda Türkçe özel ad kademe 2 ve 3'te de bulunamaz (yanlış negatif).
2. **Haritalama kayar.** Her karakter haritaya tek giriş açarken küçük harfli karşılığı iki kod birimli olabilir (kod: documentOps.ts:1713-1716). Kaynakta bir "İ" geçtikten sonra normalleştirilmiş indeksler özgün indekslere bir kaymayla eşlenir. Denemede "Madde 5 İSTANBUL Barosu kararı gereğince yetkilidir..." kaynağından "gereğince yetkilidir" aranınca dönen kesit "ereğince yetkilidir " oldu (bir harf düştü, bir boşluk eklendi). `needs_correction` true olduğundan bu bozuk kesit ekranda **modelin doğru alıntısının yerine** gösterilir ve `verified:true` kalır. Yani bu durumda doğrulayıcı doğru bir alıntıyı bozuk bir metinle değiştirir.
3. **Noktalama silme sayıları birleştirebilir.** Kademe 3 noktalamayı tamamen kaldırdığı için "1.500" ile "15,00" ikisi de "1500" olur. Hukuk metninde tutar, süre, oran gibi rakamlarda tolerans, anlam değiştiren bir alıntıyı doğrulanmış gösterebilir (bu çıkarım koddan; ayrı sınanmadı).
4. **Üç noktalı alıntıda sıra denetimi yok** (yukarıda 2. adım 3); parçalar belgede ters sırada veya çok uzakta olsa da geçer.

### 4. Bağlam oluşturma (belge ve proje bağlamının prompt'a girişi)

**Belge içeriği prompt'a önceden girmez; araçla gelir.** Sistem istemine yalnız "AVAILABLE DOCUMENTS" listesi (`doc-N: dosya adı`) yazılır ve model her turda belgeyi `read_document` / `fetch_documents` ile yeniden okumak zorunda bırakılır; sistem istemi "turlar arası belge içeriği tutmazsın" der (contextBuilders.ts:630-660 civarı; `buildMessages` 613-700, özellikle docAvailability bloğu). Gerekçe yorumda: okumazsa eski veya halüsinasyonlu içerik üretir.

**Belge etiketleri.** `buildDocContext` mesaj ekleri ve önceki asistan olaylarından (`doc_created`, `doc_edited`, `doc_replicated`) belge kimliklerini toplar (contextBuilders.ts:1205-1260), erişim yetkisini **kap (container) başına bir kez** sorar (proje/iş akışı/kuruluş; belge başına değil; contextBuilders.ts:1262-1340) ve `doc-0`, `doc-1`... etiketlerini üretir (contextBuilders.ts:1342-1356). Proje bağlamında proje belgeleri `doc-N`, doğrudan ekler `attachment-doc-N` adını alır (contextBuilders.ts:1373-1486); klasör yolu etikete eklenir.

**Okuma bütçesi ve tekrar kapısı.** Aynı belge/sürüm bir cevap içinde yalnız bir kez tam okunabilir; ikinci çağrıya "metin atlandı" yanıtı döner. Bu yanıtın içeriği, modelin onu hata sanıp döngüye girmemesi için özel olarak tasarlanmıştır: yorumda, bir Gemini turunun aynı dosyayı 29 kez okuduğu yazılı (documentOps.ts:1412-1445; toolDispatcher.ts:561-577). Bu, küçük model için de dersli bir bulgudur.

**Kesme/bütçe.** `read_document` tam metni olduğu gibi döndürür; backend'de belge metni için bir karakter üst sınırı **bulmadım** (okuduğum aralıkta). Üst sınırlar: Word eklentisinin yolladığı "document_context" için 200 000 karakter (contextBuilders.ts:583, 609; wordClientTools.ts:859-868, kesilince "[Document truncated at ...]" notu); önceki tur muhakemesi tekrarı için tur başına 12 000 ve toplam 36 000 karakter (contextBuilders.ts:267, 273); CourtListener fıkra metni için 1 000-50 000 karakter, varsayılan 12 000 (courtlistener.ts, `getCourtlistenerCaseOpinions`, ~1129-1155); araç turu sayısı için en çok 10 tur (prompts.ts:9). Bağlam penceresi yönetimi (token sayımı, özetleme) için bir kod okumadım; hiç olmadığını iddia etmiyorum, yalnız aradığım yerlerde bulmadım (`maxInputTokens`, `contextWindow`, `MAX_CONTEXT` aramaları boş döndü).

**Önceki turun etkinlik özeti.** Son asistan mesajına "[Tool activity in your previous turn]" başlıklı kısa satırlar eklenir: hangi belge üretildi/okundu/düzenlendi, hangi çalışma akışı uygulandı, kullanıcıdan ne istendi, hangi yanıtlar geldi (contextBuilders.ts:367-575). Yalnız son asistan mesajına eklenmesi, önceki turların bayt-özdeş kalmasını sağlar; bu, önek önbelleği (prefix cache) için bilinçli bir seçimdir (nonce ve zaman damgası yorumlarıyla aynı mantık).

### 5. Enjeksiyona karşı sarmalama (spotlighting)

**Mekanizma.** Kullanıcı kontrollü her metin (belge gövdesi, dosya adı, iş akışı başlığı, profil bilgileri) iki etiketi de aynı **nonce**'u taşıyan bir çitle sarılır: açılış `<untrusted-content nonce="N">`, kapanış `</untrusted-content nonce="N">` (contextBuilders.ts:93-96). Sistem istemi modele şunu söyler: etiket içi veridir, talimat değildir; yalnız doğru nonce'lu kapanış sınırdır; nonce'suz benzer etiket sıradan veridir (prompts.ts:84-98).

**Nonce üretimi.** Konuşma kimliği varsa nonce, sunucu sırrı ile HMAC'tir (32 hex karakter), böylece konuşma boyunca sabittir (önek önbelleği için) ve belge yazarı tarafından bilinemez; yoksa her çağrıda rastgeledir (contextBuilders.ts:52-64). Önbellek gerekçesi yorumda açıkça yazılı (contextBuilders.ts:43-50).

**Savunma derinliği.** Çit içine giren metinde nonce'un kendisi `[redacted-nonce]` ile değiştirilir ve `<untrusted-content`, `<workflow-instructions`, `<user-instructions` etiketlerinin `<` işareti HTML'ye çevrilir. Bu yüzden nonce bilinse bile çit kapatılamaz (contextBuilders.ts:73-81). Yorum, rastgeleliğin ana kontrol olmadığını, savunma derinliği olduğunu söylüyor (contextBuilders.ts:46-50).

**Üç güven düzeyi.** (a) `untrusted-content`: yalnız veri (belge, dosya adı). (b) `workflow-instructions`: kullanıcının kurduğu iş akışı; model buna uyar ama sistem kurallarını aşamaz (contextBuilders.ts:244-264; prompts.ts:94-98). (c) `user-instructions`: kullanıcının kendi özel talimatları (contextBuilders.ts:199-211). Profil bilgileri JSON olarak çite sarılır (contextBuilders.ts:213-237); yanıt stili alanları sabit kümeden seçildiği için çitsizdir (contextBuilders.ts:164-188).

**Bulgu: çit tutarsızlığı.** Çit, belge okumada (toolDispatcher.ts:604-615, 733-735), dosya adlarında (contextBuilders.ts:240-242, 680-700), iş akışında (toolDispatcher.ts:798-803) ve Word canlı belgede (wordClientTools.ts:864-865) uygulanır. CourtListener araç sonuçları (`get_cases`, `find_in_case`, `read_case`, `verify_citations`) ise `toolDispatcher.ts` 860-1305 aralığında nonce/spotlight **içermiyor** (aralıkta `nonce|spotlight|untrusted` araması boş döndü); hakem metni ve kısa parçacıklar JSON olarak çitsiz modele gider. Bu, olası bir enjeksiyon açığıdır (dış kaynaklı metin); kullanım etkisi sınanmadı.

**Yetenek kısıtı, çitten daha sert bir kontrol.** Modelin görmediği araç, çağrılsa da çalıştırılmaz: "reklamı yapılmayan" ile "çağrılabilir olmayan" ayrımı iki katmanda uygulanır, şemadan çıkarma ve `runTools` içinde yeniden reddetme (streaming.ts:216-225 ve 320-326 yorumları). Hafıza için de aynı ilke geçerli: canlı model hafızaya yazmaz (docs/memory.md:18-19) ve hafıza düzenleyicisi (curator) tek bir sunucuya bağlı araç görür (aşağıda 8).

### 6. İçtihat doğrulama akışı (CourtListener)

Entegrasyon ABD içtihadı içindir (docs/courtlistener.md:1-3). Üç yol vardır: global belirteç (`COURTLISTENER_API_TOKEN`), kullanıcının ayarlardaki kendi anahtarı ve isteğe bağlı yerel toplu veri (`COURTLISTENER_BULK_DATA_ENABLED=true`: Supabase indeks tabloları + R2'deki hazır fıkra JSON'ları; yoksa canlı API'ye düşülür; docs/courtlistener.md:17-26, 40-46). İstekler 15 saniyelik zaman aşımıyla yapılır (courtlistener.ts:59-90). 429 yanıtı ayrıştırılıp bekleme süresi söylenir (courtlistener.ts:31-57).

Model için dört araç tanımlıdır (courtlistenerTools.ts:34-139) ve sistem istemi aşağıdaki iş akışını zorunlu kılar (courtlistenerTools.ts:14-32):

1. `courtlistener_verify_citations`: **temiz kitap künyeleri** dizisi (en çok 250; "467 U.S. 837" gibi). Dava adı verilmesi yasak. Sonuç: her künye için durum (`found`/`not_found`/`invalid` vb.), eşleşen "cluster"lar ve tıklanabilir bağlantılar (`citationLinks`). Önce yerel toplu veriye bakılır; `not_found`/`invalid` olanlar için belirteç varsa canlı API'ye düşülür ve sonuçlar **künye anahtarıyla** (noktalama/boşluk duyarsız) eşleştirilip birleştirilir; pozisyonla değil, çünkü API her tespit ettiği künye için bir satır döner (courtlistener.ts:960-1068; 535-542). Eşleşen küme önbelleğe alınır, arayüze `case_citation` olayı gider (toolDispatcher.ts:1305-1370). Bağlantı metni modele `us-case-<id>` biçiminde yeniden yazılarak verilir (toolDispatcher.ts:1347-1352).
2. `courtlistener_get_cases`: küme kimliğiyle fıkraları çeker. Modele yalnız **metinsiz meta veri** (fıkra sayısı, tür, yazar, karakter sayısı) döner; fıkra metni "yalnız sunucuda önbellekte" tutulur ve model bir sonraki adım olarak `find_in_case`/`read_case`'e yönlendirilir (toolDispatcher.ts:929-1089; courtlistenerTurnState.ts:186-217).
3. `courtlistener_find_in_case`: önbellekteki metinde 1-3 kelimelik aramalar (tur başına en çok 3; varsayılan 20 sonuç, 160 karakter çevre bağlam) (courtlistenerTools.ts:20, 58-88; toolDispatcher.ts:230-249, 1090-1196). Eşleştirme `findTextMatches` ile, doğrulayıcıyla aynı `normalizeWithMap` üzerinden yapılır (documentOps.ts:1752-1800).
4. `courtlistener_read_case`: yalnız istenen fıkra(lar)ın metni; çok fıkralı davada `opinion_id` seçmek zorunlu, aksi halde hata döner (toolDispatcher.ts:1198-1304).

Atıf kuralı: nihai cevapta içtihat, hem tıklanabilir bağlantı hem `[N]` işaretiyle anılır; `<CITATIONS>` içinde `{ref, cluster_id, quotes:[{opinion_id, quote}]}` bulunur; model hafızadan, üst veriden, arama sonucundan veya yalnız künye doğrulamasından atıf yapamaz, bu tur içinde alınmış metin gerekir (courtlistenerTools.ts:23-29). Şiddetli sınır: herhangi bir çağrı oran sınırına takılırsa o tur tüm CourtListener çağrıları durur (courtlistenerTools.ts:31-32). OpenAI uyarlayıcısı ek olarak araç kullanımından sonra aynı atıf hatırlatmasını bir kez daha enjekte eder (aiSdk.ts:195-208, `COURTLISTENER_CITATION_REMINDER`).

**Düzeltme / gözlem.** `searchCourtlistenerCaseLaw` (courtlistener.ts:1070-1127) ve ona ait dispatcher dalı (toolDispatcher.ts:867-928) kodda var, ancak `COURTLISTENER_TOOLS` dizisi onu **içermiyor** (courtlistenerTools.ts:34-139, yalnız dört araç); dolayısıyla model bu aracı görmüyor. `docs/courtlistener.md:3` "targeted opinion search" ifadesi, bu bağlamda `find_in_case`'e işaret ediyor olmalı. Ayrıca `verifyCourtlistenerCitations` hata iletisi "citation or case name" der (courtlistener.ts:~968), araç tanımı ise dava adını yasaklar: küçük bir tutarsızlık.

**İki aşamalı koruma.** Modelin atfı iki bağımsız kanaldan geçer: (i) `case_citation` olayıyla gelen künye doğrulaması (bu bir "var olan dava" kanıtıdır), (ii) `verifyCaseCitationAnnotation` ile alıntının fıkra metninde bulunması (bu bir "gerçekten bu sözleri söylüyor" kanıtıdır). Bu ikisi birbirinden ayrı tutuludur ve (ii) ilk olarak (i)'in doldurduğu tur içi önbelleğe dayanır.

### 7. Doğrulayıcının ölçtüğü ve ölçmediği

Ölçtüğü: biçim (JSON ayrıştırılabilir mi), kimlik (`doc_id` bu tur indeksinde mi; `cluster_id` bu tur önbelleğinde mi), metin (alıntı kaynakta bitişik olarak geçiyor mu, kademeli toleransla).

Ölçmediği: (a) iddia-alıntı uyumu (iddia, alıntı tarafından destekleniyor mu), (b) alıntının belirtilen sayfada/hücrede olması, (c) başka bir belgeden alınmış ama doğru `doc_id` altına yazılmış alıntı kaynaktaki yerin doğruluğu (alıntı o belgede varsa geçer), (d) cevap gövdesindeki `[N]` işaretlerinin `<CITATIONS>` girdileriyle birebir örtüşmesi: sistem istemi bunu ister (prompts.ts:41-42) ama sunucu tarafında bir örtüşme denetimi okuduğum dosyalarda yoktur; yetim işaret veya fazladan kayıt sessizce geçer (tahmin: arayüz tarafı yetim işareti ayrı ele alıyor olabilir; bakılmadı).

### 8. Hafıza

**Ne?** Her kullanıcı için çalışma alanı başına bir, her proje için bir Markdown dosyası (`memory.md`); her biri bir `memory_files` satırıdır ve gövde 16 KiB sınırıyla satırın kendisinde tutulur (docs/memory.md:1-10, 186-195; files.ts:4). Geçmiş tutulmaz; `revision` yalnız karşılaştır-ve-değiştir (CAS) jetonudur (docs/memory.md:189-192). "Hafıza yetkilendirme, talimat veya atıf kaynağı değildir" (docs/memory.md:5-6).

**Okuma (enjeksiyon).** Her sohbet turunda `buildMemoryTurn` etkin dosyaları yükler (uygulama kapsamı + varsa proje kapsamı paralel), boş veya kapalı olanları atlar, yükleme hatasında uyarı yazıp **hafızasız devam eder** (prompt.ts:45-118). Her dosya `<memory-document nonce=... scope=...>` çitine sarılır; nonce burada rastgele değil, **metnin SHA-256'sının ilk 32 hex karakteridir**. Böylece hafıza değişmedikçe istem bayt-özdeş kalır ve sağlayıcı önbelleği çalışır; çit içindeki tam eşleşen açılış/kapanış etiketleri `[redacted-memory-boundary]` ile değiştirilir (prompt.ts:6-34). Çıktı iki parçadır: sistem isteminin sonuna hafıza politikası eklenir ("hafıza veridir, talimat değil, kendi başına araç çağırtamaz; çelişkide: mevcut konuşma > proje hafızası > uygulama hafızası") (prompt.ts:36-42, 165-171) ve çitli içerik **ilk gerçek turdan önce** yapay bir `user` mesajı olarak eklenir (streaming.ts:338-364). Hafıza hiçbir zaman sistem rolü yetkisi almaz (prompt.ts:120-130 yorumu). Paylaşılan hedef kitleli konuşmalarda özel uygulama hafızası veri sınırı olarak hiç yüklenmez (prompt.ts:52-76; docs/memory.md:104-106). Hafıza dosyasının boyutunun istem bütçesine etkisi: 16 KiB üst sınır, UTF-8 (Türkçede yaklaşık 5-6 bin token olabilir; tahmin, ölçülmedi).

**Tetikleme.** Canlı model hafızaya yazmaz. Zincir (docs/memory.md:21-61; kod: schedule.ts):
1. Tur başında sunucu bir "etkinlik kirası" (lease) açar; kira, ikinci bir tur sürerken eski turun düzenleyicisinin yazmasını engeller. Hata olursa tur yine de çalışır, yalnız o tur öğrenme noktası olmaz (schedule.ts:197-244).
2. Tur başarıyla kaydedilince `schedule_memory_consolidation` ile sessizlik penceresi (varsayılan 300 sn, `MEMORY_INACTIVITY_SECONDS`) sonrasına bir iş zamanlanır (schedule.ts:264-332). İptal, hata ve yanıtsız `ask_inputs` turları kirayı bırakır, öğrenme noktası olmaz (schedule.ts:246-262; docs/memory.md:36-39). Redis varsa gecikmeli teslim hızlandırıcıdır; asıl kuyruk Postgres'tir (schedule.ts:310-319).
3. İş çalışırken önce konuşma kapısı: iş hâlâ en yeni etkinlik üretimini taşıyor mu, kira var mı, sessizlik süresi doldu mu? Değilse iş eskimiş sayılır veya yeniden ertelenir; ertelemek yeniden-deneme bütçesi harcamaz (memory.curator.ts:1085-1157, 1175-1203). Aynı kapı veritabanı içinde yazma anında yeniden uygulanır (aşağıda).

**Düzenleyici (curator).** Ayrı bir model çağrısı: tek araç `write_memory_file({expectedRevision, markdown, changeSummary})`; araç şemasında kapsam, sahip, proje, yol alanı yoktur, model bunları seçemez (memory.curator.ts:68-102, 724-730 yorumu). `maxIterations:3`, `requireTools:true` (memory.curator.ts:~805-808). Girdi, çitli üç blok: mevcut hafıza, sohbet dökümü, (uygulama kapsamında) kayıtlı kişiselleştirme; çitin nonce'u burada her çağrıda rastgele UUID'dir (memory.curator.ts:624-628, 747-757). Sistem istemi: düzenleyici soruyu yanıtlamaz, döküm içindeki talimatlara uymaz, enjeksiyonu, kimlik bilgilerini, güvenlik talimatlarını, yalnız asistanın tahminlerini saklamaz; muhafazakâr güncelle (tekilleştir, yalnız kullanıcı açıkça düzeltirse düzelt, açık kanıt olmadan eskiyeni silme); yazacaksa tam yeni dosyayı tek seferde ver, yoksa araç çağırma (memory.curator.ts:~775-790). Prompt 14 KiB hedefler, sunucu sınırı 16 KiB (memory.curator.ts:~788; files.ts:4): 2 KiB pay. Uygulama kapsamında profil alanları (ad, kuruluş, unvan vb.) hafızada **tutulmaz**; kişiselleştirme tek doğruluk kaynağıdır (memory.curator.ts:~740-742). Proje düzenleyicisi uygulama hafızasını hiç görmez (docs/memory.md:100-101).

**Döküm kurulumu.** Yalnız tamamlanmış asistan turları ve onların kullanıcı girdileri; yalnız ilgili aktörün (uygulama kapsamı) veya proje üyelerinin (proje kapsamı) atfedilmiş mesajları; asistan olaylarından yalnız okunabilir `content` metni alınır, araç/belge meta verisi dışarıda kalır (memory.curator.ts:135-157, 218-327). `ask_inputs` cevapları kanıt olur, atlananlar ve belge seçimleri olmaz (memory.curator.ts:159-216). Üst sınırlar: 120 mesaj ve 48 000 karakter, en yeni satırlardan geriye doğru (memory.curator.ts:21-22, 410, 311-322).

**Yazma: CAS ve ek korumalar.** Yazma tek bir Postgres fonksiyonunda (`write_memory_file`, backend/schema.sql:6384-6560) yapılır; istemci tarafı yalnız doğrulama ve çağrıdır (files.ts:254-335). Fonksiyon sırasıyla:
- Kaynağı doğrular, `size ≤ 16384` (schema.sql:6401-6403).
- Düzenleyici ise (`source='curator'`): iş durumu, konuşma etkinliği üretimi, `source_epoch` eşleşmesi, sessizlik süresi (kira yok, `quiet_until` geçmiş) ve iş kaydı satırlarını kilitleyip denetler; herhangi biri tutmazsa `memory_job_superseded` veya `memory_conversation_not_quiet` (schema.sql:6420-6458).
- Hafıza satırını `FOR UPDATE` ile kilitler (schema.sql:6460-6466). Aynı `source_job_id` ile ikinci çağrı "uygulandı=false" döner: yeniden denenen iş bir kez uygulanır (schema.sql:6468-6475).
- Düzenleyici ise çalışma alanı (`org_id`) ve uygulama-hafızasına uygunluğu veritabanında doğrular (`memory_source_org_id`); bu yüzden kuruluş sohbeti Kişisel hafızaya, tersi de, yazamaz (schema.sql:6477-6497).
- Sıra: devre dışı mı (`memory_disabled`), epoch (`memory_epoch_conflict`), revision (`memory_revision_conflict`) (schema.sql:6499-6507).
- Gövde SHA-256'sı değişmediyse yazılmaz (revision yakılmaz) ama iş makbuzu damgalanır (schema.sql:6509-6529).
- Aksi halde gövdeyi yazar ve `revision + 1` yapar; hatasız yazımda `last_error_code` temizlenir (schema.sql:6531-6546).
Normalleştirme (LF, boşluk temizliği, kontrol karakteri ve çalıştırılabilir HTML reddi, 16 KiB) sunucu tarafında, SQL'den önce yapılır (files.ts:61-96).

**Elle düzenleme.** Kullanıcı ayarlardan `PUT /` ile `expected_revision` + `content` gönderir; çakışmada 409 `memory_revision_conflict` ve güncel dosya döner (memory.routes.ts:99-128, 150-175). Yetkiler: kullanıcı hafızası sahibine özel; proje hafızasını görüntüleme `project.view`, düzenleme `content.edit`, açma/kapama `access.manage` (memory.routes.ts:~210-228; memory.service.ts:63-96).

**Kapatma = yıkıcı.** Kapatmak gövdeyi boşaltır, `epoch`'u ve öğrenme kesim zamanını ilerletir; böylece bekleyen veya uçuştaki düzenleyici işi artık yazamaz. Yeniden açma boş dosya ile başlar (docs/memory.md:203-220; files.ts:337-403). `revision` boş yazımda da ilerler, yani yıkımdan önce yüklenmiş bir taslak silinmiş içeriği geri getiremez (files.ts:236-244 yorumu).

**Düzeltme (dokümantasyon ile kod arasında).** docs/memory.md:55-57 "çakışan düzenleyici daha yeni dosyayı yeniden yükler ve yeniden üretir" der. Kodda `MemoryRevisionConflictError`, `runMemoryCuratorScope` içinde ayrıca yakalanmaz; yazma hatası olarak yeniden fırlatılır (memory.curator.ts:~890-905), kapsam hatası sayılır ve iş başarısız olarak döner (memory.curator.ts:1448-1455 civarı: `scopeFailures`, `memoryScopeFailure`). Yeniden yükleme ve yeniden üretme, **iş düzeyinde yeniden denemeyle** olur: bir sonraki denemede `getMemoryCurrentForFile` güncel dosyayı yeniden okur (memory.curator.ts:1388-1400). Kaç kez yeniden deneneceği (`maxAttempts`) bu dosyalarda değil, kuyruk/SQL tarafında; okunmadı. Aynı turda iki kapsamdan biri başarısız olursa diğerinin sonucu iş makbuzuyla korunur ve yeniden denemede atlanır (memory.curator.ts:1388-1393, schema.sql:6509-6529).

**Başarısızlık gizliliği.** Her düzenleyici hatası sabit bir "Memory curator scope failed" iletisine çevrilir; çünkü sağlayıcı/depolama hataları istemi, anahtarı veya dökümü yankılayabilir. Yalnız izin verilen `name`, `code` ve HTTP durum kodu hatanın "neden" kısmı olarak taşınır (memory.curator.ts:678-722).

**Dışa aktarma ve toplu silme.** ZIP: `app/memory.md`, `organizations/<ad>--<id>/memory.md`, `projects/<ad>--<id>/memory.md`; iş kuyrukta beklerken erişim kaybolabileceğinden her proje dosyasından önce erişim yeniden denetlenir (archive.ts:104-136). Toplu silme tek RPC (`delete_user_private_memories`) ile yapılır (bulk.ts:1-19).

---

## HakHukuk için değerlendirme

Genel ilke: Mike'ın **mekaniği** (sunucu tarafı denetim, çit, CAS, yetenek kısıtı) taşınır; **bağlam varsayımları** (tüm belgeyi bağlama koymak, modelin uzun kelimesi kelimesine alıntı yazması, 16 KiB düzenleyici çıktısı) 4B modele taşınmaz.

### Taşınır

1. **Sunucu tarafı, akış sonrası, fail-closed alıntı doğrulaması.** Modelin metni değil, sunucunun elindeki kaynak metin gerçektir; kaynak okunamadığında "doğrulandı" değil "doğrulanamadı" denir (verifyCitations.ts:19-25, 166-168, 393-398). Gerekçe: bizim ölçüm omurgamız zaten deterministik atıf doğrulaması; bu, aynı felsefenin ürün katmanındaki karşılığıdır.
2. **Kaynak metinden kesit geri okuma (kayma düzeltme).** Alıntı gösterimi için modelin metni değil, belgenin kendi cümlesi kullanılır (verifyCitations.ts:403-408). Biz bunu daha da ileri götürüp alıntıyı hiç modele yazdırmayacağız (aşağıda, önerilen akış).
3. **Önbellek-tabanlı varlık kapısı (içtihat).** Alıntı, yalnız o tur sunucunun çektiği metne karşı doğrulanır; çekilmemiş kimlik ile doğrulanmış görünmek imkânsızdır (courtlistenerTurnState.ts:240-246; verifyCitations.ts:338-346). Bizim madde-kimliği tabanlı akışımızda "bu tur retriever'ın döndürdüğü madde kümesi" aynı rolü oynar.
4. **Metni modele vermeden meta veri + arama (find_in_case deseni).** `get_cases` metinsiz meta veri döndürür, metin sunucuda kalır; model 1-3 kelimelik arama veya seçilmiş fıkra okumasıyla küçük parçalar alır (toolDispatcher.ts:1038-1075; courtlistenerTools.ts:20-21). 4B bağlam için en kritik desen: Yargıtay/Danıştay kararları uzundur, tamamı bağlama konamaz.
5. **Tur başına tek okuma kapısı ve "tekrar okuma" yanıtının tasarımı** (documentOps.ts:1412-1445). Küçük modeller döngüye daha yatkındır; yanıtın "bu bir hata değildir, yeniden deneme işe yaramaz" demesi doğrudan taşınır.
6. **Kısmi akış sırasında atıf ayrıştırma ve etiket kuyruk tamponu** (streaming.ts:400-453). Yerel llama.cpp akışında da aynı kesilme sorunu olur; ayrıştırma mantığı dilden bağımsız bir durum makinesidir (yeniden yazılır, kopyalanmaz).
7. **Nonce'lu çit + HTML kaçışı + içerik-türetilmiş nonce (hafıza).** İçerik-türetilmiş nonce, önek önbelleğini korur (prompt.ts:6-18); yerel sunucularda (llama.cpp prompt cache, vLLM prefix caching) aynı kazanç var. Ancak nonce'u gizli sır olarak değil, ayrıştırma sınırı olarak düşünmek gerek (kod yorumu da bunu söylüyor).
8. **Yetenek kısıtlaması: tek sunucuya-bağlı yazma aracı, kapsam alanı olmayan şema, "reklamı yapılmayan araç çalıştırılmaz" ikinci kapı** (memory.curator.ts:68-102; streaming.ts:216-225). Tek kullanıcılı yerel uygulamada bile aynı agent işlerinin birbirinin dosyasına yazmasını engeller.
9. **CAS + epoch + iş makbuzu ile hafıza yazımı.** SQLite'ta tek yazar olduğundan çok daha basit gerçeklenir (`UPDATE ... WHERE revision = ?`), ama bizde birden çok eşzamanlı agent işi olduğu için revision CAS yine gerekir; epoch (yıkıcı kapatma/silme sonrası eski taslakların yazamaması) ve iş makbuzu (yeniden denenen işin bir kez uygulanması) bire bir taşınır (schema.sql:6468-6475, 6499-6507).
10. **Hafızanın "talimat değil veri" konumu: araya gerçek turlardan önce yapay `user` mesajı olarak girmesi, sistem rolü almaması** (streaming.ts:364; prompt.ts:120-130).
11. **Çelişkide öncelik sırası** (mevcut konuşma > proje > uygulama) ve **profilin hafızada tekrarlanmaması** (kişiselleştirme tek doğruluk kaynağı).

### Yeniden tasarlanmalı

1. **Alıntıyı modelin yazması.** Mike modelin kelimesi kelimesine alıntı yazmasını bekler ve sonra bulur (prompts.ts:46). Küçük modellerde bu, hem uzun çıktı üretimi (token maliyeti), hem kayma kaynağıdır. Bizde madde kimliği + sunucunun çektiği metin (aşağıda önerilen akış).
2. **Bitişik alt dize eşleşmesi ve toleranslı kademeler, Türkçe/Unicode ve rakam güvenliği ile.** Bölüm 3'teki üç kusur giderilmeden aynen alınamaz: (a) küçük harfe çevirme yerine tek bir "eşleştirme anahtarı" (NFC, İ/ı/I/i -> tek harf, büyük/küçük harf yok sayma), (b) harita **kod noktası** başına (veya kaynak karakter başına) tutulmalı, küçük harfli karşılığın uzunluğuna bağımlı olmamalı, (c) noktalama atma, iki rakam arasındaki `.` ve `,` karakterlerini korumalı (veya sayıları ayrı jetonla karşılaştırmalı). Bu bir öneri ve ölçülmemiş; Mike'ın testlerine benzer birim testleriyle (Türkçe İ/ı, "1.500" vs "15,00", çok-sütunlu PDF) kilitlenmeli.
3. **Üç durumlu doğrulama durumu.** Mike "bayrak yok = doğrulandı" gösterir (citationVerification.tsx:28, 34) ve bazı yollar doğrulamaz (iptal/hata turları, tablo). Bizde `verified | unverified | unchecked` ayrık olmalı ve "unchecked" asla yeşil gösterilmemeli (CLAUDE.md'deki "sessiz yanlış sayı" sınıfına denk).
4. **Doğrulama kapsamı: sayfa/hücre yerine madde ve fıkra.** Mike sayfayı doğrulamaz; bizde "madde numarası" doğrulaması deterministik ve ucuzdur ve bizim ana ölçütümüzdür (madde metninde ya da korpus kaydında).
5. **Atıf bloğunun biçimi (4B için).** Cevabın sonuna uzun bir JSON dizisi yazdırmak küçük modelde kırılgandır: Mike'ın ayrıştırıcısı çökerse "atıf yok" olarak sessizce geçilir (citations.ts:216-224). Seçenekler (bir karar gerektirir): (A) Mike gibi sonda JSON bloğu + kısmi ayrıştırma; (B) satır içi kimlik etiketi (`[m:TBK-49/1]`) + gramer kısıtlı çıktı (llama.cpp GBNF veya vLLM/SGLang yapılandırılmış çıktı), kimlik alanı yalnız bu turda getirilen madde kimliklerinden oluşan bir sıralama (enum); (C) atıf için ayrı bir araç çağrısı (`cite(madde_id)`) ve sunucu numaralandırır. Öneri: B (aşağıda); gerekçe: model hiçbir zaman var olmayan bir kimlik üretemez, ayrıştırma hatası yapısal olarak elenir ("hatayı tip düzeyinde eleme").
6. **Çit politikasının sistem isteminde uzun anlatımı** (prompts.ts:84-98, yaklaşık 300-400 token; tahmin) 4B için pahalıdır ve 4B bu soyut kuralı güvenilir uygulamaz. Çit biçimi kısa tutulmalı ve asıl güvence yetenek kısıtlarına (araç izinleri, onay) bağlanmalı.
7. **Belge bağlamının tam metin olarak tool sonucuna konması.** Burada üst sınır yok (documentOps.ts:1447-1680). 4B Q4 ile 8-32K bağlam varsayımında parçalı okuma (sayfa/madde aralığı) ve bütçe-kırpma gerekir; `[Page N]` benzeri konum işaretleri iyi bir fikirdir, bizde "madde numarası" işaretine dönüşür.
8. **Hafıza düzenleyicisi 4B modelle.** Mike, tam bir 16 KiB dosyayı yeniden yazan bir model çağrısı varsayar (memory.curator.ts:68-102). 4B bu kadar uzun, yapılandırılmış ve muhafazakâr bir yeniden yazımı güvenle yapamaz (tahmin, ölçülmedi). Bizde: hafıza üst sınırını küçük tutmak (ör. 2-4 KiB; öneri), çıktıyı gramerle kısıtlamak, yazımı "ekle/sil/değiştir madde" satır işlemleriyle sınırlamak ve her yazımı sunucuda sayısal/biçimsel denetimden geçirmek.
9. **Beş dakikalık sessizlik zamanlayıcısı.** Tek GPU'da düzenleyici, canlı cevapla aynı yuvayı paylaşır. Zamanlayıcı yerine "kuyruk boş ve GPU boş" koşulu daha uygun olur; CAS ve kira mantığı korunur.
10. **Çok kiracılı kapsam (kuruluş/proje/paylaşılan kitle) ve ona bağlı bütün veri sınırı mantığı.** Tek kullanıcılı yerel uygulamada gereksizdir (docs/memory.md:63-106). Gereken tek sınır: iş (agent) başına hafıza kapsamı gerekirse "kullanıcı" ve "proje/dava dosyası" olmak üzere iki kapsam. Proje hafızasında sızma yok (tek kullanıcı), ama bir önerilen kural: dava dosyasına özgü hafıza (müvekkil bilgileri) genel kullanıcı hafızasına kopyalanmaz.
11. **İçtihat kimliklendirmesi (Yargıtay/Danıştay).** CourtListener'ın `verify_citations` aracı **standart bir kitap künyesini** (cilt-rapor-sayfa) tek bir kimliğe çözer. Türkçe karar künyesi (daire + esas + karar + tarih) biçim açısından çok daha değişkendir (yazım "E." / "Esas", "K." / "Karar", tarih biçimleri, "2019/1234" gibi). Bu çözümleyici bizim yazmamız gereken yeni bileşendir: künye ayrıştır -> normalleştir -> korpusta ara -> eşleşmeyi tek kayıt kimliğine bağla; eşleşme yoksa "bulunamadı" (uydurma karar riski). Bu çıkarım koddan değil Türk içtihat biçimi bilgisinden; hangi açık içtihat kaynağının kullanılacağı karar bekleyen bir konudur (CLAUDE.md: lisans-temiz veri, Lexpera/Kazancı yasak).

### Taşınmaz

1. **Büyük bağlama ve uzun kelimesi kelimesine alıntıya dayanan "belge sohbeti" modeli** (tam metin okuma, 25 kelimelik alıntı, çok parçalı PAGE_BREAK zincirleri) 4B'ye olduğu gibi taşınmaz; yalnız fikri (sunucu doğrular) kalır.
2. **Çok sağlayıcılı uyarlayıcı davranışları** (OpenAI için ek hatırlatma, Gemini döngü bulgusu): yerel tek model için doğrudan geçerli değil, ama "tek bir turdaki hata biçimlerini araç yanıtlarıyla yönetme" dersi geçerli.
3. **Mike'ın Supabase/RLS/R2 tabanlı depolama ve toplu içtihat indeksi** (courtlistener.ts toplu veri yolu): bizde SQLite + yerel dosya; bu katman yeniden yazılır, tasarımdan yalnız "önce yerel, sonra uzak" sırası kalır.
4. **Kuruluş/ekip sınırları, proje paylaşımı, dışa aktarma ZIP'i, hesap silme zinciri** (archive.ts, bulk.ts, memory.service.ts izin kontrolleri): tek kullanıcılı yerel uygulamada karşılığı yok.
5. **CourtListener API'si ve ABD kitap künyeleri** doğrudan: kullanılamaz; yalnız akış şekli (künye çözümle -> kayıt çek -> parça ara -> alıntı doğrula) alınır.

---

## Önerilen atıf akışı (madde tabanlı korpus)

Hedef: modelin kelimesi kelimesine alıntı yazma yükünü ve kayma sınıfını yapısal olarak ortadan kaldırmak; deterministik denetimi korumak. Bu bir tasarım önerisidir; ölçülmemiştir, 4B üzerinde sınanmamıştır.

**0. Kimlik.** Korpustaki her atıf birimi kalıcı bir `madde_id` taşır (ör. `kanun_no/madde/fıkra` bileşik anahtarı; mevcut S2 indeksinde yürürlük alanı ve alt-madde kimliği zaten var, CLAUDE.md "Corpus and index"). Atıf birimi: madde veya fıkra.

**1. Getirme.** Retriever bu tur için N aday madde döndürür. Sunucu bu kümeyi **tur durumunda** (`getirilen_kimlikler`) saklar (Mike'ın `casesByClusterId` önbelleğinin karşılığı). Modele aday metinler, kısa tur-yerel tutamaçlarla (`[K1]`, `[K2]`...) ve madde başlığı/numarasıyla verilir. Uzun mevzuat metni parçalanır; model her turda yalnız bütçeye sığan parçaları görür.

**2. Üretim.** Model cevabın gövdesine, tutamaç kullanarak atıf işareti koyar. Çıktı, kısıtlı gramerle (llama.cpp GBNF veya vLLM/SGLang yapılandırılmış çıktı) sınırlanır: izin verilen kimlikler yalnız `getirilen_kimlikler` kümesinden gelir. Böylece "var olmayan madde" üretimi ve atıf bloğu JSON biçim hatası yapısal olarak elenir.

**3. Ayrıştırma ve çözümleme (sunucu).** İşaretler cevaptan çıkarılır, ilk görünüş sırasına göre 1..N numaralanır (modelin numara atlaması sorunu ortadan kalkar; Mike'da model numaralandırır ve atlayabilir, prompts.ts:30, 41-42). Tutamaç -> `madde_id` -> korpus kaydı çözülür.

**4. Alıntıyı sunucu çeker.** Kullanıcıya gösterilen alıntı, modelin yazdığı değil, korpus kaydından alınan metindir (madde veya fıkra; uzunsa cümle dizinleriyle). Model isterse yalnız **cümle/fıkra dizini** seçer (örn. "1. fıkra, 2. cümle"); sunucu o dilimi çıkarır. Böylece Mike'ın `source_excerpt` mantığı (verifyCitations.ts:403-408) kuralın kendisi olur, istisna değil.

**5. Deterministik denetimler (judge-free).**
   a. **Varlık:** `madde_id` korpusta var mı; yürürlük durumu (yürürlükte / mülga) kayıttan okunur ve arayüze taşınır (bizde Mike'da yok; avantaj).
   b. **Küme üyeliği:** `madde_id` bu turun `getirilen_kimlikler` kümesinde mi (modelin hafızadan atıf yapması engellenir; Mike'ın "bu tur alınmış metin gerekir" kuralının yapısal karşılığı, courtlistenerTools.ts:24).
   c. **Gövde-numara tutarlılığı:** cevap metninde geçen "m. N" / "N. madde" ifadeleri çıkarılır (düzenli ifade; Türkçe varyantlar: "md.", "madde", "m."), atıf kümesi veya getirilen küme dışında bir madde numarası anılıyorsa uyarı. Bu, Mike'ın yapmadığı bir denetimdir ve bizim ölçüm çizgimizdeki "atıf doğrulaması"nın ürün katmanına taşınmasıdır.
   d. **Serbest alıntı (isteğe bağlı mod):** model yine de metin alıntılarsa, Mike'ın üç kademeli eşleşmesi kullanılır, ancak Türkçe-güvenli anahtar ve rakam korumalı noktalama toleransıyla (Değerlendirme > Yeniden tasarlanmalı > 2). Eşleşme madde kaydının metnine karşı yapılır; bütün belgeye değil, böylece "başka yerde geçiyor" sorunu (sayfa doğrulanmaması) doğal olarak çözülür.
   e. **Etiket bütünlüğü:** her işaret bir kayıt, her kayıt en az bir işaretle eşleşir; yetim olan olduğu gibi kaydedilir ve `unchecked`/`invalid` olarak işaretlenir (Mike'da bu denetim görülmedi).

**6. Durum ve arayüz.** Her atıf için üç durumlu `durum`: `dogrulandi | dogrulanamadi | denetlenmedi`; ayrıca `yururluk` alanı. `denetlenmedi` yeşil gösterilmez. İptal edilen/hata veren turlarda saklanan atıflar da aynı doğrulayıcıdan geçer veya açıkça `denetlenmedi` damgalanır (Mike'da bu yol atlanır, chat.routes.ts:951).

**7. İçtihat (Yargıtay/Danıştay) uyarlaması.** Aynı iskelet: (i) `kunye_coz(metin)` -> (daire, esas, karar, tarih) normalleşmiş kimlik, korpusta tek kayıt veya "yok"; (ii) kararlar metinsiz meta veriyle (daire, tarih, özet alanı varsa) modele verilir, metin sunucuda kalır; (iii) `karar_icinde_ara(kimlik, 1-3 kelime)` parçacık döndürür (Mike'ın find_in_case karşılığı, bellek içi `findTextMatches`'in aynısı); (iv) model karar kimliğiyle atıf yapar, alıntı sunucudan çekilir veya seçilen parçacığın dizinidir; (v) karar korpusu yoksa model kararlara atıf **yapamaz**, yalnız "bulunamadı" der. CourtListener'daki "temiz künye / dava adı yasak" ilkesinin karşılığı: model serbest metinle karar adı uyduramaz, yalnız çözümlenmiş kimlik kullanır.

**8. Hafıza ile ilişkisi.** Atıflar hafızaya kopyalanmaz (Mike: "hafıza atıf kaynağı değildir", docs/memory.md:5-6). Kullanıcı tercihi ve dava-özgü gerçekler (taraflar, tarihler) hafızada tutulabilir; hukuki hüküm metni ve madde içeriği korpustan gelir (güncellik kütüphanede, CLAUDE.md "Currency lives in the library").

---

## Açık sorular

1. Bir turda tek atıf için kaç madde/fıkra bağlama alınır, 4B ile bütçe nedir? Mike'da böyle bir sayı yok; bizim retriever çıktısı ve bağlam bütçesi ölçümüyle belirlenmeli.
2. Gramer kısıtlı satır içi kimlik üretimi (öneri B) 4B'nin cevap kalitesini (bizim "kütle/faithful-answer mass" ölçütümüzü) düşürür mü? Bu bir deney konusudur; pre-registered kapı gerektirir (CLAUDE.md belge disiplini).
3. Türkçe-güvenli eşleştirme anahtarı tam olarak hangi katlama kuralıyla yazılmalı (İ/ı/I/i hepsi tek harfe mi, yoksa yalnız büyük-küçük eşleşmesi mi)? Yanlış-pozitif ve yanlış-negatif dengesi test verisiyle ölçülmeli.
4. Hafıza düzenleyicisi 4B ile hiç kullanılacak mı, yoksa hafıza yalnız elle mi düzenlenecek? Düzenleyici gerekçesi kullanıcı yararı (tercihlerin otomatik öğrenilmesi) ile güvenlik riski (yanlış öğrenme, enjeksiyon) arasındadır.
5. Mike'da cevap işaretleriyle `<CITATIONS>` girdileri arasında örtüşme denetimi sunucuda var mı? Okuduğum kodda görmedim; arayüz kodu (AssistantMessage.tsx vb.) bu açıdan taranmadı.
6. Mike CourtListener sonuçlarında çit eksikliğini bilinçli mi bırakıyor (kamu kaynaklı güvenilir metin varsayımı) yoksa bir gözden kaçma mı? Kodda gerekçe yorumu yok.
7. İçtihat korpusu: Yargıtay/Danıştay için hangi açık veri kaynağı lisans bakımından kullanılabilir ve künye ayrıştırma için hangi kimlik alanları güvenilir biçimde bulunur? (Mevzuat için `docs/BEDESTEN_API.md` var; içtihat kapsamı o belgede doğrulanmadı.)
8. Düzenleyici işlerin yeniden-deneme sayısı (`maxAttempts`) ve çakışmada davranışın tam hâli kuyruk/SQL tarafındadır ve okunmadı; "dokümantasyon: yeniden üretir" ile "kod: iş düzeyinde yeniden dener" farkı bu yüzden kesin değil.

---

## Okunmadı

Bu çalışmada açılmadı ya da yalnız başlık düzeyinde görüldü:

- `backend/src/lib/courtlistener.ts` içinde: HTML temizleme ve izinli etiket/öznitelik listesi (260-436), toplu veri (bulk) künye araması ve R2 fıkra okuma ayrıntıları (560-740, 800-955), `compactCluster`/`compactBulkCluster` gövdeleri (130-160, 466-480). Toplu veri yolunun davranışı yalnız `docs/courtlistener.md` ve çağıran kodun üstünden anlatıldı.
- `backend/src/modules/chat/engine/contextBuilders.ts` içinde: 330-360 ve 470-520 (muhakeme tekrarı eşleştirmesi, `ask_inputs` özet satırları), 836-1200 (ask_inputs yük ayrıştırma, mesaj ekleme yardımcıları).
- `backend/src/modules/memory/memory.curator.ts` içinde: 453-620 (`loadConversation`, uygunluk kuralları), 953-1085 (durum yazma yardımcıları).
- Test dosyaları (`verifyCitations.test.ts`, `__tests__/*`): yalnız `it(...)` başlıkları listelendi, gövdeler okunmadı. Dolayısıyla Bölüm 3'teki kusurların test kapsamı dışı olduğu iddiası "başlıklarda yok" düzeyindedir.
- SQL: `schedule_memory_consolidation`, `begin_memory_conversation_turn`, `lock_memory_conversation_source`, `memory_source_allows_app_memory`, `memory_source_org_id`, `wipe_memory_file`, `enable_memory_file` gövdeleri. Yalnız `write_memory_file` (schema.sql:6384-6560) okundu.
- `backend/src/lib/pdfTextOrder.ts` (arayüzdeki aynalı dosyanın başlığı üzerinden bahsedildi), `packages/pdf-text-order/cases.json`.
- Arayüz: `AssistantMessage.tsx` ve `CitationQuotesSection.tsx` gövdeleri; atıf tıklamasının belge görüntüleyicide nasıl vurgulandığı (`DocxView.tsx`, PDF görüntüleyici) okunmadı. Yalnız `citationVerification.tsx` ve `shared/types.ts` ilgili aralıkları okundu.
- Word eklentisi atıf akışı (`wordPrompt.ts:86-92`, 200 karakter sınırı ve "Word'ün bulabileceği kadar benzersiz" kuralı) yalnız `grep` satırlarından biliniyor; Word istemcisi tarafındaki doğrulama okunmadı.
- `docs/superpowers`, `docs/incidents`, `docs/test-evidence` içindeki olası hafıza/atıf olay raporları.
- Kuyruk/iş altyapısı (`lib/dbq`, `lib/queue`): iş yeniden-deneme politikası, `DbJobDeferredError` semantiği ayrıntıları.
