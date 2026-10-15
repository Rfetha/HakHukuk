# Mike: agent döngüsü, araçlar ve akış katmanı

Kaynak: Mike (AGPL-3.0, TypeScript). Aşağıdaki tüm yollar kaynak köküne göredir (`backend/src/...`). Kod kopyalanmamıştır; tasarım kendi cümlelerimizle anlatılmış, tırnak içi alıntılar en çok 3 satırdır. Sayılar dosyadan alınmıştır; tahmin olanlar "tahmin" diye işaretlidir.

## Kapsam ve okunan dosyalar

Tamamı okunanlar:

- `backend/src/modules/chat/engine/prompts.ts` (119 satır)
- `backend/src/lib/assistantTurnRuns.ts` (188 satır)
- `backend/src/lib/streamRuns.ts` (413 satır)
- `backend/src/modules/chat/engine/streaming.ts` (859 satır)
- `backend/src/modules/chat/engine/tools/toolSchemas.ts` (521 satır)
- `backend/src/modules/chat/engine/tools/courtlistenerTools.ts` (139 satır)
- `backend/src/modules/chat/engine/tools/connectorApprovals.ts` (150 satır)
- `backend/src/lib/llm/aiSdk.ts` (694 satır; asıl döngü burada, `streaming.ts` yalnızca sarmalayıcı)
- `backend/src/lib/llm/localModelMiddleware.ts` (353 satır)
- `backend/src/lib/llm/providerDeadlines.ts` (105 satır)
- `backend/src/lib/sseHeartbeat.ts` (29 satır)

Kısmen okunanlar (okunan aralık belirtilmiştir):

- `backend/src/modules/chat/engine/tools/toolDispatcher.ts`: 1-760, 757-900, 1429-1660, 1950-2080 (courtlistener dalları 867-1428 yalnızca başlık düzeyinde tarandı)
- `backend/src/modules/chat/engine/tools/documentOps.ts`: `citationReminder` (42-62), `runEditDocument` (1123-1366), `getTurnReadIdentity`/`duplicateReadDocumentResult` (1367-1446), `readDocumentContent` başı ve log satırları, `findTextMatches`/`findInDocumentContent` (1733-1906)
- `backend/src/modules/chat/chat.routes.ts`: 150-290 ve 440-1008 (POST /chat, GET turn/stream, POST turn/stop)
- `backend/src/modules/chat/chat.prepare.ts`: 340-551
- `backend/src/modules/chat/engine/contextBuilders.ts`: 380-576 (önceki tur özeti), 580-860 (`buildMessages`, zaman damgası, textless-tur sınıflaması), 860-1000 (ask_inputs yanıt ayrıştırma), nonce üretimi (56-64) ve `spotlight` (66-96)
- `backend/src/lib/llm/toolCallParsing.ts`: 1-466 (tamamı, kısmen göz gezdirme)
- `backend/src/lib/llm/registry.ts` (125-175), `providers.ts` (480-545), `runtimeConfig.ts` (100-145)
- `backend/src/modules/chat/engine/tools/wordClientTools.ts`: yalnızca sabitler, köprü ve bekleme mantığı (60-330, 676-760)
- `backend/src/modules/chat/engine/verifyCitations.ts`: 1-60, 162-256, 376-447
- `backend/src/modules/chat/engine/wordPrompt.ts`: yalnızca 1-60
- Test dosyalarının `describe/it` başlıkları: `lib/llm/aiSdk.toolErrors.test.ts`, `modules/chat/engine/__tests__/streamingToolGating.test.ts`, `routeStreaming.test.ts`. Test gövdeleri okunmadı.
- Frontend: `frontend/src/app/lib/mikeApi.ts` (2765-2800, 3180-3215) yalnızca yeniden bağlanma uçları için.

Önceki yüzeysel okumadan düzeltmeler (kısaca): (1) Tur sınırı sistem promptunda "en çok 10 tur" yazıyor, ama kod sınırı 16; ikisi tutarsız (aşağıda 2.1). (2) Döngü Mike'ın kendi yazdığı bir döngü değil, Vercel AI SDK'nın `streamText` adım döngüsü; Mike yalnızca araç yürütücüsünü ve durdurma koşulunu veriyor. (3) Sunucu tarafı araçlar paralel değil, sıralı çalışıyor.

## Nasıl çalışıyor

### 1. Katmanlar

İstek akışı şöyle: `POST /chat` (`modules/chat/chat.routes.ts:485`) önce `prepareChatStream` ile sohbeti, belge dizinini (`docIndex`/`docStore`), iş akışı deposunu ve sistem mesajını hazırlar (`chat.prepare.ts:449-534`). Sonra bir "tur çalıştırması" (run) kaydeder (`chat.routes.ts:598`), `runLLMStream`'i çağırır (`chat.routes.ts:707`), `runLLMStream` de `streamChatWithTools`'u (`streaming.ts:524`), o da AI SDK'nın `streamText`'ini (`lib/llm/aiSdk.ts:499`) çalıştırır. Araç çağrıları SDK tarafından `runTools` geri çağrısına (`streaming.ts:572`) ve oradan `runToolCalls`'a (`tools/toolDispatcher.ts:276`) gider.

Bu yapının sonucu: araç çağrısı ayrıştırma, şema doğrulama ve model-araç mesaj biçimlendirmesi büyük ölçüde SDK'ya bırakılmış. Bizim Python tarafında bunların hepsini kendimiz yazmamız gerekecek (bkz. değerlendirme).

### 2. Tur sınırı ve bütçe

#### 2.1 Tur (adım) sınırı

- `DEFAULT_MAX_ITERATIONS = 16` (`lib/llm/aiSdk.ts:53`). Yorum satırları (46-52) gerekçeyi açıklıyor: belge ağırlıklı turlar ilk birkaç turu salt okumaya harcıyor; sınır dolduğunda koşu hatasız ve cevapsız bitiyor, bu yüzden "çoğunlukla yeter" bir değer görünmez biçimde başarısız oluyor.
- `streaming.ts:533` aynı sayıyı (16) bilinçli olarak sabit yazıyor; modül import'u yerine literal kullanılmış çünkü testlerde `../llm` mock'lanıyor (529-532 yorumu). Word ve hafıza küratörü `maxIterations` ile üzerine yazabiliyor: Word 16 (`modules/word-chat/wordChat.routes.ts:849`), hafıza küratörü 3 (`modules/memory/memory.curator.ts:770`).
- Durdurma koşulu SDK'nın `stepCountIs(maxIterations)` ifadesi (`aiSdk.ts:514`). Bir "adım" = bir model çağrısı + o adımın araç çağrıları.
- Sistem promptu modele "en çok 10 araç turu kullan; bağımsız çağrıları toplu ver ve son cevap için yer bırak" diyor (`prompts.ts:9`). Yani modele söylenen bütçe (10) ile zorlanan bütçe (16) farklı; 6 turluk tampon var. Bu bir tasarım kararı gibi duruyor ama dosyada gerekçesi yazılı değil (tahmin: modele sıkı, sistemde gevşek sınır vermek).
- Sınır dolunca model sonuçsuz kesilmesin diye `stopNotice` (`aiSdk.ts:63-78`) cevaba bir not ekliyor. İki durum: `finishReason === "length"` (çıktı sınırı) ve `iterations >= maxIterations && finishReason !== "stop"` (adım sınırı). Not metni modele değil kullanıcıya gidiyor ve `onContentDelta` ile akışa sokuluyor (631-635).

#### 2.2 Token/çıktı bütçesi

- Adım başına çıktı sınırı varsayılan olarak ayarlanmıyor (`aiSdk.ts:20-43`): her sağlayıcı kendi model-farkındalıklı tavanını uyguluyor. İsteğe bağlı `LLM_MAX_OUTPUT_TOKENS` ortam değişkeni geçerli pozitif tamsayıysa kullanılıyor; OpenCode Go için sabit 16.384 (42).
- Muhakeme düzeyi varsayılanı `high` (`streaming.ts:535`); OpenAI-uyumlu yerel uçlar için `supportsReasoning: false` (`lib/llm/providers.ts`, `createConfiguredAdapter` içinde, yaklaşık 515-525; kesin satır doğrulanmadı).
- Bağlam penceresi yönetimi yok: geçmiş mesajlar kırpılmıyor, özetlenmiyor (backend genelinde `contextWindow`, `compact`, `truncateHistory` aramaları bu amaçla bir şey vermedi; yalnızca Word belge bağlamı için 200.000 karakter sınırı var: `contextBuilders.ts:583`). `read_document` tam metni döndürüyor; `readDocumentContent` içinde kırpma görmedim (1447-1700 aralığında yalnızca log satırlarındaki `slice` var). HTTP gövde sınırı 50 MB (`app.ts:47`), dolayısıyla bağlam taşması yönetimi sağlayıcıya bırakılmış.
- Yinelenen okuma engeli bütçeyi koruyor: aynı belge/sürüm bir cevapta bir kez okunabiliyor (2.6'da).

#### 2.3 Süre sınırları

Üç katman var:

| Katman | Varsayılan | Yer | Ne yakalıyor |
| --- | --- | --- | --- |
| İlk parça zaman aşımı | 2 dk (alt 10 sn, üst 30 dk) | `lib/runtimeConfig.ts:129-136` | Model adımının ilk çıktısı (başlıklar dahil) |
| Parçalar arası zaman aşımı | 60 sn (5 sn - 30 dk) | `runtimeConfig.ts:137-143` | Metin/muhakeme/araç girdisi arasındaki sessizlik |
| Koşu boşta zaman aşımı | 5 dk (30 sn - 60 dk) | `lib/streamRuns.ts:41`, `runtimeConfig.ts:104-111` | Model ilerlemesi ya da veri çerçevesi olmaması |
| Koşu azami ömür | 4 saat (1 dk - 24 sa) | `streamRuns.ts:40`, `runtimeConfig.ts:112-118` | Sonsuza akan koşu |

Sağlayıcı saatleri yalnızca model adımını ölçüyor, yerel araç yürütmesini saymıyor (`runtimeConfig.ts:122-127` yorumu; `providerDeadlines.ts:8` "without timing the SDK's tools"). Parçalar arası saat `text-delta`, `reasoning-delta`, `tool-input-delta`, `tool-call`, `file` parçalarında yeniden kuruluyor ve her seferinde koşunun `touch`'ını tetikliyor (`providerDeadlines.ts:68-76`). Ortam değişkenleri: `STREAM_FIRST_CHUNK_TIMEOUT_MS`, `STREAM_CHUNK_TIMEOUT_MS`, `STREAM_IDLE_TIMEOUT_MS`, `STREAM_MAX_LIFETIME_MS`.

### 3. Araç çağrısı ayrıştırma ve doğrulama

#### 3.1 Normal (yapılandırılmış) yol

Araçlar OpenAI "function" şemasıyla tanımlı (`toolSchemas.ts`), SDK'ya `jsonSchema(...)` olarak veriliyor (`aiSdk.ts:302-338`). Yani Mike kendi doğrulayıcısını yazmıyor; geçersiz argüman ya da bilinmeyen araç durumunda SDK "dinamik" bir `tool-error` parçası üretiyor, sonucu o çağrının cevabı olarak sıraya koyuyor ve döngüyü sürdürüyor ki model toparlanabilsin (`aiSdk.ts:596-605` yorumu). Gerçek bir `execute()` hatası ise turu bitiriyor (606-607). Mike'ın şeması "required" listelerini taşıyor ama kodda ayrı bir şema doğrulaması yok; asıl savunma dağıtıcı içindeki elle yazılmış kontroller.

Dağıtıcıda argüman ayrıştırma: `JSON.parse(tc.function.arguments || "{}")`, hata olursa sessizce `{}` (`toolDispatcher.ts:461-467`). Yani bozuk JSON, "boş argümanlı çağrı"ya dönüşüyor ve sonuçta aracın kendi doğrulama hatası modele dönüyor (örn. `edit_document` için "edits array is required and must not be empty.", `toolDispatcher.ts:1483-1490`). Bu sessiz yutma 4B için riskli (3.3'te).

Akış düzeyinde ek bir koruma var: `aiSdkFetch` (`aiSdk.ts:85-196`) OpenAI-uyumlu SSE akışını izleyip kısmi araç çağrısı argümanlarını biriktiriyor. Akış temiz bir bitiş olayı olmadan kapanırsa ve argümanlar eksik/bozuksa araç çalışmadan önce hata fırlatıyor ("LLM stream ended with malformed JSON arguments..."). Temiz bitişte bozuk JSON'u olduğu gibi bırakıp SDK'nın kurtarılabilir hata yoluna bırakıyor (112-126 yorumu).

#### 3.2 Yerel/ayrık modeller için "tolerans" yolu (4B için en önemli kısım)

`lib/llm/registry.ts:143-146`: `location === "local"` olan model varsayılan olarak "tolerant" sayılıyor ve sarmalanıyor (`providers.ts:515-520`). Ara katman (`localModelMiddleware.ts`) üç şey yapıyor:

1. `<think>...</think>` bloklarını muhakeme kanalına ayırıyor (`toolCallParsing.ts:19-81`, `ThinkTagFilter`; etiket parçalara bölünse bile tampon tutuyor).
2. Metin akışındaki araç işaretlemesini kullanıcıya göstermeden bastırıyor (`TextToolMarkupFilter`, `toolCallParsing.ts:83-141`). Tanıdığı işaretçiler: `<tool_call`, `<toolcall`, `<|tool_call`, `<function=`, `<function name=` ve iki DeepSeek DSML biçimi.
3. Metne gömülü araç çağrılarını gerçek `tool-call` parçalarına çeviriyor (`parseTextToolCalls`, `toolCallParsing.ts:170-266`). Desteklenen "lehçeler": `<tool_call>` içinde JSON, XML benzeri `<function=ad>` blokları, DSML `invoke`, ve "tek anahtarı araç adı olan harita" biçimi. Bozuk JSON için `jsonrepair` kütüphanesi (3) ve Qwen'e özgü bir çift tırnak/çift iki nokta düzeltmesi (`normalizeQwenToolMapSyntax`, 175-179) kullanılıyor; bu da yetmezse "gevşek" ayrıştırıcı `name:`/`tool:` ve `arguments:` desenlerini regex ile arıyor (`parseLooseTextToolCall`, 95-133). Tekrar eden (ad+girdi aynı) çağrılar tek çağrıya indiriliyor (`deduplicateToolCalls`, 158-168). Sayısal/boolean/null değerler metinden tür çıkarımıyla dönüştürülüyor (`parseToolScalar`, 156-173).
4. Çağrı bulunamazsa: metin araç çağrısı gibi görünüyor ama ayrıştırılamıyorsa hata fırlatıyor (sessizce yutmamak için; `localModelMiddleware.ts:57-70`, `toolCallParsing.ts:247-258`); sağlayıcı kendi araç çağrısını bildirdiyse metni taramıyor (`localModelMiddleware.ts:118-129`).

Önemli bir tasarım kararı: araç tanımlı bir istekte tolerant model akışla değil, **akışsız uç noktayla** (`doGenerate`) çağrılıyor ve sonuç akış olarak yeniden oynatılıyor (`localModelMiddleware.ts:289-297`). Gerekçe yorumda: bu modeller araç işaretlemesini düzyazıyla iç içe akıtıyor ve kısmi akıştan güvenilir biçimde toparlanamıyor (292-294). Bedel: bu modda token-token akış yok; araç içeren her adım bir bütün olarak geliyor. Araçsız adımlarda ise gerçek akış kullanılıyor ve çıktı filtreden geçiriliyor (299-300).

Bu kodun `toolCallParsing.ts` içinde "Trademark Monitor" ve `collapseTrademarkOwnerCalls` (44-93) gibi Mike'a özgü, alakasız bir MCP birleştirme kuralı da var; bizim için ilgisiz.

#### 3.3 Dağıtıcıdaki araç düzeyi doğrulama

Argüman kontrolleri araç başına elle yazılı (şema dışı): `replicate_document` için `count` 1-20'ye sıkıştırılıyor (`toolDispatcher.ts:1611-1614`), `find_in_document` için `max_results`/`context_chars` sayı değilse varsayılan (643-644, 641-642), `ask_inputs` için normalleştirme ve kırpma (3.6'da). `generate_docx` için `numberSections === true` katı karşılaştırması bilinçli: eksik/null/bozuk değer numaralandırmayı açmasın diye (`toolDispatcher.ts:1960-1962`).

### 4. Paralel / sıralı yürütme

- Model aynı adımda birden fazla araç çağrısı verebilir. SDK bu çağrıları eşzamanlı başlatır; Mike bunları `ToolExecutionBatcher` ile aynı mikro-görev turunda toplayıp **tek bir `runTools(calls[])` çağrısına** indirger (`aiSdk.ts:239-294`). Yani sağlayıcıdan bağımsız sözleşme "adım başına tek parti".
- Parti içinde sunucu araçları **sıralı** çalışır (`toolDispatcher.ts:461` düz `for` döngüsü; `Promise.all` yalnızca depolamaya yükleme işlerinde, 1756). Yani "paralel çağrı" modele vardır ama yürütme paralel değil; sebep olarak kodda açık bir yorum yok. Tahmin: bir tur içinde `turnReadState`/`turnEditState` gibi değiştirilebilir ortak durum olması.
- İstemci araçları (Word eklentisi) sunucu araçlarından **önce** ve kendi aralarında sıralı yürütülür; gerekçe yorumda: her çağrı canlı belgeyi okur ya da değiştirir, sıra anlamın parçasıdır (`streaming.ts:578-604`). Sonuçlar modelin orijinal çağrı sırasıyla döndürülür (735-744).
- Hata/eksik sonuç davranışı: partideki herhangi bir çağrı için sonuç üretilmediyse (bilinmeyen araç adı, devre dışı depo, korumaya takılma) `streaming.ts:741-743` o çağrıya `{"error":"Tool '<ad>' is not available."}` biçiminde bir hata sonucu yazar; böylece her `tool_use`'un bir `tool_result`'ı olur (721-726 yorumu). Dağıtıcı zinciri son `else` içermez (`toolDispatcher.ts:2028`), bilinmeyen araç sessizce atlanır ve bu yedek devreye girer.
- `ToolExecutionBatcher.flush` içinde sonucu eksik bir çağrı olursa hata, kısmi partide ise sonraki model isteğinden önce durdurulur (`aiSdk.ts:277-288`; test başlığı `aiSdk.toolErrors.test.ts:290,302`).

### 5. Hata ve tekrar koruması

Koruma mekanizmaları (hepsi açık, kodda görülen):

| Koruma | Yer | Davranış |
| --- | --- | --- |
| Aynı belge/sürümü iki kez okuma | `toolDispatcher.ts:572-583`, `documentOps.ts:1412-1435` | İkinci `read_document` tam metin yerine "zaten döndürüldü" notu alır |
| Yazma araçlarını gizleme + zorla reddetme | `toolSchemas.ts:17-42`, `streaming.ts:324-326, 589-594` | Yetkisiz tur için şemadan çıkarılır, model yine de çağırırsa gönderilmez |
| Ardışık istemci zaman aşımı | `wordClientTools.ts:94` (`MAX_CONSECUTIVE_TIMEOUTS = 2`) | İki ardışık zaman aşımından sonra kesilir |
| İstemci çağrı bütçesi | `wordClientTools.ts:95` (`CLIENT_CALL_BUDGET = 12`) | Tur başına en çok 12 istemci çağrısı |
| Canlı okuma sınırı | `wordClientTools.ts:96` (`MAX_LIVE_READS_PER_TURN = 3`) | 200k karakterlik belgeyi bağlama defalarca basmayı önler |
| Adım sınırı | `aiSdk.ts:514` | 16 tur, ardından kullanıcıya not |
| Bozuk akış araç argümanları | `aiSdk.ts:102-134` | Çalıştırmadan önce hata |
| Hata mesajı sızıntısı | `streaming.ts:119-145`, `types.ts:128` | Araç hatası kullanıcıya sabit metinle gider: "This tool could not complete its request." |

Dikkat çeken, belgelenmiş bir dersi: `duplicateReadDocumentResult` (`documentOps.ts:1412-1435`) içindeki yorum, eski sürümde yinelenen okuma sonucuna İngilizce açıklama koyunca modellerin bunu "yer tutucu metin/bozuk araç" sanıp aynı okumayı tekrarladığını ve adım sınırına kadar döngüye girdiğini, bir Gemini turunun aynı dosyayı 29 kez okuduğunu anlatıyor. Çözüm: `content` anahtarı hiç yok; `status: "full_text_omitted_already_returned"`, bir açıklama ve "bu belge için `read_document`'i bir daha çağırma" yönergesi veren yapılandırılmış bir yanıt. Bu, 4B için doğrudan taşınabilir bir kanıt: tekrar koruması yalnızca engellemek değil, modelin neden ret aldığını açıkça söylemek zorunda.

Genel tekrar/döngü tespiti (aynı araç + aynı argümanla ardışık çağrı) dağıtıcıda yok; yalnızca `read_document`/`fetch_documents` için okuma-durumu ve `deduplicateToolCalls` (yalnız tolerans yolunda, aynı partideki kopyalar) var.

Hata yolu (`streaming.ts:747-794`): AskInputs duraklaması (sessiz), iptal (kısmi metni sakla, `AbortError` fırlat), diğer hatalar (kısmi turu boşalt, hata olayını biriktir, hatayı Sentry'e raporla, `AssistantStreamError` fırlat). Kullanıcıya gösterilebilir hata sadece `UserFacingError` ise (geçersiz anahtar, model yok) ayrıntılı gelir; aksi halde sabit "The response could not be completed. Please try again." (`streaming.ts:85-86, 776`).

### 6. İptal

- Kullanıcı iptali: `POST /chat/:chatId/turn/:turnId/stop` (`chat.routes.ts:219-243`). Yalnızca sohbetin yaratıcısı ya da proje düzenleyicisi durdurabilir. `run.stop()` koşunun `AbortSignal`'ını iptal eder.
- SSE soketinin kapanması iptal **değildir**: yanıt yalnızca ayrılır (`streamRuns.ts:370-407`, "Closing a response detaches it and nothing else").
- Sinyal zinciri: koşu sinyali, `runLLMStream({signal})` ve `streamAiSdk` içinde bir iç `AbortController`'a bağlanıyor (`aiSdk.ts:449-452`). İç iptal yalnızca kullanıcı iptalinde değil, araç hatasında da tetikleniyor ki SDK sonraki model isteğini göndermesin (`aiSdk.ts:444-457` yorumu).
- İptal benzeri hataların ayrımı: adı "AbortError" olan ama gerçekte iptal edilmemiş bir istisna, hata yoluna yönlendiriliyor (`guardAbortShaped`, `aiSdk.ts:461-470`); aksi halde sağlayıcı kesintisi sessiz "kullanıcı iptali" gibi görünürdü.
- Kısmi sonuç: iptalde `fullText` ve olaylar saklanıyor, `buildStoppedAssistantMessage` ile kalıcı hale getiriliyor ve istemciye `{"type":"cancelled"}` yazılıyor (`chat.routes.ts:885-940`; `streamRuns.ts:69-75`). Durdurma nedeni "user", "idle" ya da "max_lifetime" olabilir; ikincisi/üçüncüsü hata çerçevesi ve denetim kaydında `failed` olarak işlenir.
- İptalden sonra rota 30 sn içinde kendiliğinden bitmezse (`STOPPED_RUN_GRACE_MS = 30_000`, `streamRuns.ts:84`) kayıt defteri koşuyu zorla bitirir ve anahtarı serbest bırakır; aksi halde o sohbete sonraki tüm gönderimler 409 alırdı (76-83 yorumu).

### 7. Duraklatma deseni: `ask_inputs`

Mantık özeti:

1. Model `ask_inputs` çağırır. Şema: `items` (1-12 öğe), her öğe `kind` ∈ {`choice`, `multi_choice`, `text`, `documents`}; `choice` için en çok 8 seçenek, `documents` için en çok 8 belge türü etiketi (`toolSchemas.ts:169-247`).
2. Dağıtıcı çağrıyı normalleştirir (`normalizeAskInputsEvent`, `toolDispatcher.ts:104-201`): kimlik 80, soru 500, seçenek 500, öneki 200 karaktere kırpılır; boş seçenek listesi `[{"value":"Continue"}]` olur; boş soru için varsayılan metin gelir; en çok 12 öğe. Olay kimliği (`event_id`) rastgele UUID. Çağrı kendisi `continue` ile geçilir, yani araç sonucu **üretilmez** (557-561).
3. `runTools` bir `ask_inputs` olayı fark edince olayı yazar ve kaydeder, sonra `AssistantStreamAskInputsPause` fırlatır (`streaming.ts:703-719`). Bu istisna araç hatası yolundan geçip SDK'yı durdurur; `streaming.ts:748-751` bunu başarılı bir tur gibi ele alır ve modelin "lütfen yanıt verin" gibi gereksiz metin eklemesini engeller (749-751 yorumu). Böylece duraklama, **modele hiç sonuç döndürülmeden turu bitirmektir**; döngü korunmaz, yeniden kurulur.
4. Rota bu turun sonunda "ask_inputs" olduğu için hafıza konsolidasyonunu atlar (`chat.routes.ts:830-858`), cevabı kaydeder ve `[DONE]` yazar.
5. Kullanıcı yanıtlayınca istemci aynı uca yeni bir POST atar, gövdede `ask_inputs_response` (asistan mesaj kimliği, `ask_event_id`, yanıtlar) ile (`chat.routes.ts:511-526`; `requestValidation.ts:296-447`). Sunucu yanıtı tek kullanımlık atomik "append" ile asistan mesajına ekler; durumlar `forbidden` (turu başlatan kullanıcı değil), `invalid`, `stale` (409, kod `ask_inputs_stale`) (`chat.prepare.ts:372-406`). Yeni asistan satırı açılmaz; devam, önceki asistan satırına eklenir (`chat.routes.ts:526, 765-774`).
6. Model bağlamında araç sonucu replay'i yok. Bunun yerine bir sonraki isteğin son asistan mesajına metin olarak eklenen "[Tool activity in your previous turn]" özeti geçer (`contextBuilders.ts:556-575`): "kullanıcıya N girdi soruldu", "kullanıcı yanıtladı: ...", "kullanıcı atladı: ...", "kullanıcı belge ekledi: ...". Atlanan girdi varsa kural eklenir: "atlanan girdiyi bir daha sorma; belge yazıyorsan köşeli parantez içinde yer tutucu koy" (551-555).
7. Aynı mekanizma bağlayıcı (MCP, Google) yazma onayı için yeniden kullanılıyor: onay gerektiren çağrı sonuç olarak `awaiting_approval` taşıyan bir araç sonucu alır, onay öğeleri tek bir `ask_inputs` olayında modelin kendi soruları ile birleştirilir (`toolDispatcher.ts:480-494, 2050-2065`). Onaylanan eylemler yalnızca istemciden gelen "approve/reject" kararına değil, sunucuda kalıcı olayına dayanarak çalıştırılır (`connectorApprovals.ts:5-10, 61-110`); sonuç modele 4.000 karaktere kırpılarak aktarılır (`MAX_APPROVAL_RESULT_CHARS`, 36).

Sistem promptundaki ilgili kural (`prompts.ts:11`): tüm gereken sorular **tek** çağrıda; `choice` tek seçim, `multi_choice` çoklu, `text` serbest metin; belge isteniyorsa `document_types` dizisi; sorduktan sonra yanıt gelene kadar asıl işe devam etme; atlanan girdiyi bir daha sorma, belge yazılıyorsa köşeli parantezli yer tutucu bırak.

### 8. Akış (SSE) ve yeniden bağlanma

#### 8.1 Sunucu sahipli koşu

`streamRuns.ts` genel bir "koşu kayıt defteri"; `assistantTurnRuns.ts` bunun sohbet biçimli görünümü (anahtar `<yüzey>:<sohbetId>`, yüzey: chat/tabular/word; 44, 67). Tasarım:

- Üretim HTTP yanıtına değil koşuya bağlı. Rota çerçeveleri koşunun tamponuna yazar; istenildiği kadar yanıt (özgün istek, yenileme, ikinci sekme) ona bağlanabilir (`assistantTurnRuns.ts:11-32`).
- Her çerçeve `data: <json>\n\n` biçiminde ve önüne `id: <seq>` satırı eklenerek numaralanır (`streamRuns.ts:166-168, 264-267`). Yeniden bağlanan istemci `from=<son id + 1>` gönderir (`chat.routes.ts:189-213`; istemci tarafı `frontend/src/app/lib/mikeApi.ts:2773-2787`).
- `:` ile başlayan yorum satırları (canlı tutma) canlı dağıtılır ama tamponlanmaz ve numaralanmaz (246-263), aksi halde Word turu bir istemci aracı beklerken yüzlerce yorumu yeniden oynatmak zorunda kalırdı.
- Bir sohbette aynı anda yalnızca bir koşu olabilir; ikincisi `409 turn_in_progress` alır (`chat.routes.ts:607-612`; `streamRuns.ts:189-202`).
- Biten koşu 60 sn saklanır (`FINISHED_RUN_RETENTION_MS = 60_000`, `streamRuns.ts:32`), böylece bitişten hemen sonra bağlanan istemci son çerçeveleri alır. Süreç bellekte tutar; çok kopyalı kurulumda yapışkan yönlendirme gerekir (`streamRuns.ts:26-30`).
- Sayfa yüklenince `GET /chat/:chatId` yanıtındaki `active_turn: {id, seq, assistant_message_id}` ile istemci üretilmekte olan tura bağlanır (`assistantTurnRuns.ts:148-163`; `chat.routes.ts:182-186`).
- Boşta (5 dk) ve ömür (4 sa) süreleri 2.3'te. SSE yanıt başlıkları: `text/event-stream`, `no-cache`, `X-Accel-Buffering: no` (`streamRuns.ts:379-383`).
- Ana sohbet rotası `startSseHeartbeat` kullanmıyor (kullanan tek yer `modules/tabular/tabular.generateStream.ts:179`). 15 sn'lik canlı tutma yalnızca tabular ve (kendi 15 sn'lik `: tool-wait` döngüsüyle) Word istemci araç beklemesinde var (`wordClientTools.ts:217, 711-717`).

#### 8.2 Olay (çerçeve) türleri (bu bölümde görülenler)

`chat_id` (turnId, assistantMessageId taşır; `chat.routes.ts:654-661`), `content_delta`, `reasoning_delta`, `reasoning_block_end`, `tool_call_start` (yalnızca ad), `doc_read_start/doc_read`, `doc_find_start/doc_find`, `doc_created_start/doc_created`, `doc_edited_start/doc_edited`, `doc_replicate_start/doc_replicated`, `workflow_applied`, `ask_inputs`, `mcp_tool_start/mcp_tool_result`, `citations` (durum: `started`, `partial`, `final`), `chat_title`, `error`, `cancelled`, `[DONE]`. Kalıcı olay listesi (`events`) tur sonunda asistan mesajına yazılır; araç sonuçlarının kendisi veritabanına yazılmaz (yalnız olay özeti).

#### 8.3 Metin ve atıf akışı

- `<CITATIONS>` etiketi metin akışında görüldüğü anda sonrası görünür metinden ayrılıp "gizli atıf içeriği" olarak biriktirilir; ayrıştırılabilen her nesne için kısmi atıf anlık görüntüsü gönderilir (`streaming.ts:399-453`). Etiket parçalar arası bölünebileceği için `CITATIONS_OPEN_TAG.length - 1` karakterlik kuyruk tamponu tutulur (444-446).
- Tur sonunda atıflar sunucuda doğrulanır (`streaming.ts:796-852`, bkz. 10).

### 9. Araç kataloğu

Ana sohbette modele sunulan küme `TOOLS` + CourtListener (ABD içtihat, ayarla açılır) + `WORKFLOW_TOOLS` + bağlayıcı araçları (`streaming.ts:305-319`). `list_documents` ve `fetch_documents` yalnızca proje sohbetinde `extraTools` ile eklenir (`projectChat.routes.ts:252`); ana sohbet rotası `extraTools` geçmez, ama sistem promptu her iki sohbette de `fetch_documents`'u anar (`prompts.ts:10`). Küçük bir tutarsızlık: ana sohbette olmayan bir araç modele adıyla tarif ediliyor.

| Ad | Amaç | Parametre şeması (özet) | Çıktı biçimi | Yer |
| --- | --- | --- | --- | --- |
| `read_document` | Belgenin tam metnini oku. Yanıttan önce zorunlu, bir cevapta belge/sürüm başına en çok bir kez | `doc_id` (string, zorunlu; `doc-N`, dosya adı ya da UUID kabul edilir) | Düz metin: `[Citation requirement for doc-N]` başlığı + dosya adı + atıf kuralları + `<untrusted-content nonce>` içine alınmış gövde. PDF için sayfa başına `[Page N]` imleri. Tekrar okumada JSON `already_read` bildirimi | `toolSchemas.ts:252`, `toolDispatcher.ts:563-617`, `documentOps.ts:42-62, 1412` |
| `find_in_document` | Belge içinde Ctrl+F benzeri arama (büyük/küçük harf ve boşluk duyarsız) | `doc_id`, `query` (zorunlu); `max_results` (varsayılan 20), `context_chars` (varsayılan 80) | JSON: `{ok, filename, query, total_matches, returned, truncated, hits:[{index, excerpt, context}]}` | `toolSchemas.ts:271`, `documentOps.ts:1733-1906` |
| `fetch_documents` (proje) | Birden çok belgeyi tek çağrıda oku | `doc_ids` (string dizisi, zorunlu) | Düz metin: her belge `--- doc-N ---` başlığıyla, `\n\n` ile birleşik | `toolSchemas.ts:54-73`, `toolDispatcher.ts:695-756` |
| `list_documents` (proje) | Projedeki belgeleri listele | parametre yok | JSON dizi `[{doc_id, filename, file_type}]` | `toolSchemas.ts:45-53`, `toolDispatcher.ts:684-694` |
| `list_workflows` | Kullanıcının iş akışlarını listele | parametre yok | JSON dizi `[{id, title}]` | `toolSchemas.ts:106`, `toolDispatcher.ts:757-770` |
| `read_workflow` | Bir iş akışının talimat metnini ve varlıklarını oku | `workflow_id` (zorunlu) | Düz metin: `<workflow-instructions nonce>` içinde talimat + varsa değişmez varlık listesi (`workflow-asset-<id>-<n>` tutamaçları). Bulunamazsa "Workflow '...' not found." | `toolSchemas.ts:114-131`, `toolDispatcher.ts:771-817` |
| `replicate_document` | Belge/şablon/varlık kopyala (kaynak değişmez), `count` kopya | `doc_id` (zorunlu); `count` 1-20; `new_filename` (şablon ve varlıkta zorunlu) | JSON `{ok, ...}` ya da `{ok:false, error}`; yeni `doc_id` tutamaçları | `toolSchemas.ts:138-165`, `toolDispatcher.ts:1605-1956` |
| `edit_document` | `.docx` için izlenen değişiklik (tracked change) olarak minimal yerine koymalar öner | `doc_id`; `edits[]`: `find`, `replace`, `context_before`, `context_after` (dördü zorunlu), `reason` isteğe bağlı | JSON `{ok:true, doc_id, document_id, version_id, version_number, applied, errors:[{index, reason}], next_required_action}` ya da `{ok:false, error}` | `toolSchemas.ts:472-520`, `toolDispatcher.ts:1429-1604`, `documentOps.ts:1123-1366` |
| `generate_docx` | Word belgesi üret | `title`, `sections[]` (zorunlu); `landscape`, `numberSections`; her bölüm: `heading`, `level`(1-3), `content`, `pageBreak`, `table{headers, rows}` | JSON: üretilen dosya bilgisi + `doc_id` + `next_required_action` (yazmadan önce `read_document` çağır, indirme bağlantısı verme, atıf yap) | `toolSchemas.ts:304-376`, `toolDispatcher.ts:1957-1987, 384-459` |
| `generate_excel` | Excel çalışma kitabı üret | `title`, `sheets[]` {`name`, `columns[]`, `rows[][]`} | `generate_docx` ile aynı biçim | `toolSchemas.ts:381-423`, `toolDispatcher.ts:1988-2007` |
| `generate_ppt` | PowerPoint üret | `title`, `slides[]` {`title`, `bullets[]`, `notes`} | Aynı biçim | `toolSchemas.ts:428-467`, `toolDispatcher.ts:2008-2027` |
| `ask_inputs` | Kullanıcıdan karar/yanıt/belge iste (tur duraklar) | `items[]` (1-12) {`id`, `kind`, `question`, `options[]`(1-8), `allow_other`, `other_label`, `document_types[]`(1-8), `response_prefix`} | Araç sonucu yok; olay `ask_inputs` yayınlanır, tur biter | `toolSchemas.ts:169-247`, `toolDispatcher.ts:557-561` |
| `read_table_cells` (tabular) | Tablo incelemesindeki hücreleri oku | `col_indices[]`, `row_indices[]` (0 tabanlı, isteğe bağlı) | Düz metin: `[COL:i "ad" \| ROW:j "dosya"]` + `Summary:`/`Flag:`/`Reasoning:` satırları; üretilmemişse `(not yet generated)` | `toolSchemas.ts:80-101`, `toolDispatcher.ts:818-866` |
| `courtlistener_verify_citations` | ABD içtihat atıflarını doğrula | `citations[]` (yalnızca temiz rapor atıfları, en çok 250) | JSON | `courtlistenerTools.ts:119-138` (gövde 1305-1428 okunmadı) |
| `courtlistener_get_cases` | Kümeleri getir, önbelleğe al (yalnız üst veri) | `clusterIds[]` | JSON | `courtlistenerTools.ts:34-53` |
| `courtlistener_find_in_case` | Getirilmiş davada anahtar sözcük ara | `clusterId`, `query` (1-3 sözcük); `max_results` (20), `context_chars` (160) | JSON; tur başına en çok 3 çağrı (prompta yazılı kural) | `courtlistenerTools.ts:55-88` |
| `courtlistener_read_case` | Seçili görüş metnini oku | `clusterId`; `opinionId` ya da `opinionIds[]` | JSON/metin | `courtlistenerTools.ts:89-118` |
| `apply_word_edits`, `read_active_document` | Word eklentisinde yürütülen istemci araçları | `apply_word_edits`: en çok 50 düzenleme, `original` ≤200 karakter, `replacement` ≤10.000, `reason` ≤500; `read_active_document`: parametre yok | İstemciden dönen JSON; zaman aşımı sentinel'i 60 sn | `wordClientTools.ts:75-96, 102-197, 213` |
| Bağlayıcı araçlar (`mcp_*`, `google_drive_*`, Google Workspace) | Kullanıcının bağladığı harici servisler | Dinamik | Bağlayıcının içeriği; hata `TOOL_ERROR_MESSAGE` ile maskelenir | `toolDispatcher.ts:469-555` |

Yazma araçları kümesi: `edit_document`, `replicate_document`, `generate_docx`, `generate_excel`, `generate_ppt` (`toolSchemas.ts:17-23`); yetkisiz turda hem şemadan çıkarılır hem de çağrılırsa reddedilir.

### 10. Araç sonuçlarının modele biçimlendirilmesi

Genel kural: araç sonucu ya JSON dizgisi ya da düz metindir (`role: "tool"`, `tool_call_id`, `content` dizgisi; `toolDispatcher.ts:454-458` örneği); olaylar kullanıcı arayüzü içindir, modele ayrıca gitmez. Önemli kalıplar:

1. **Enjeksiyona karşı çit (spotlighting).** Kullanıcı kaynaklı her metin (belge gövdesi, dosya adı, iş akışı başlığı, MCP sonucu) `<untrusted-content nonce="N">...</untrusted-content nonce="N">` içine sarılır; nonce sohbet kimliğinden HMAC ile türetilir (`contextBuilders.ts:56-64`) ve çitin kendi belirteçleri metin içinde etkisizleştirilir (`neutralizeFenceTokens`, 73-81). İş akışı talimatları ise "izlenecek" olduğu için ayrı, yarı güvenilir bir çitte (`<workflow-instructions>`, `toolDispatcher.ts:796-803`). Sistem promptu bu çitleri açıklıyor (`prompts.ts:85-101`).
2. **Atıf hatırlatıcısı sonuçla birlikte.** `read_document` çıktısının başında, o belgenin `doc_id`'sini içeren atıf nesnesi şablonu verilir (`citationReminder`, `documentOps.ts:42-62`): `ref`, `doc_id`, `quotes[{page, quote}]` (elektronik tablo için `sheet`+`cell`). Yani atıf şeması hem sistem promptunda hem de her okuma sonucunda yinelenir.
3. **`next_required_action`.** Yazma araçlarının sonucu modele bir sonraki zorunlu adımı söyler: üretilen/düzenlenen belgeyi `read_document` ile geri oku, iddialarını bu okumaya dayandır, indirme bağlantısı yazma, atıf yap (`toolDispatcher.ts:444-452, 1575-1580`). Bu, "doğrula, sonra anlat" kuralını model belleğine değil araç sonucuna yazıyor.
4. **Hata biçimi.** Doğrulama hataları `{"error": "..."}` ya da `{"ok": false, "error": "..."}` olarak aynı sözleşmeyle gelir. Kullanıcıya hata mesajı maskelenir ama modele aracın kendi hata dizgisi gider.
5. **Geçmiş araç sonuçları yeniden oynatılmaz.** Sonraki isteğe yalnızca son asistan mesajına eklenen kısa bir "[Tool activity in your previous turn]" özeti girer (`contextBuilders.ts:556-575`): `read_document → doc-N (dosya)`, `edit_document → ...`, `generated_document → ...`, `replicate_document → ... (copy of ...)`, `applied workflow: ...`. Sistem promptu da modele bunu söylüyor: belge içeriği turlar arasında tutulmaz, her belgeli cevapta yeniden `read_document` zorunlu (`contextBuilders.ts:651-652`).
6. **Sunucuda atıf doğrulaması.** Model `<CITATIONS>` JSON'unu yazar; tur sonunda her alıntı belgenin çıkarılmış metnine karşı üç kademeyle aranır: birebir, boşluk+büyük/küçük harf normalize, noktalama da normalize (`verifyCitations.ts:41-60`). Eşleşen alıntı kaynak metnin gerçek parçasıyla değiştirilir (kayma düzeltmesi), eşleşmeyen `verified: false` işaretlenir (`verifyCitations.ts:376-447`; `streaming.ts:832-837`). Sayfa sınırını aşan alıntılar `[[PAGE_BREAK]]` ile, üç noktayla kesilmiş alıntılar segment segment doğrulanır (`verifyCitations.ts:162-256`). Doğrulama kararlı (deterministik), model çağrısı gerektirmez.

### 11. Sistem prompt'unun yapısı

Birleştirme (`prompts.ts:115-119`): `SYSTEM_PROMPT_BEFORE_RESEARCH` + (isteğe bağlı) `COURTLISTENER_SYSTEM_PROMPT` + `SYSTEM_PROMPT_AFTER_RESEARCH`. Sonra `buildMessages` (`contextBuilders.ts:613-654`) şunları sırayla ekler: kullanıcı kişiselleştirme bölümü (özel talimat, profil bilgileri, yanıt stili; nonce'lu), `MESSAGE_TIME_PROMPT` (zaman damgası kuralları, `lib/userTime.ts:92-96`), "AVAILABLE DOCUMENTS" listesi (her belge için `doc-N: <çitli dosya adı>`) ve "belge içeriğini turlar arasında hatırlamıyorsun, her cevapta bir kez oku" uyarısı. Ek olarak hafıza turu (`buildMemoryTurn`) geçmişin başına "salt-okunur, güvenilmez referans" olarak eklenir (`streaming.ts:338-364`); bu dosya okunmadı.

Boyut: sistem promptunun sabit kısmı yaklaşık 1.490 + 422 = 1.912 sözcük, 9.356 + 2.841 = 12.197 karakter (satır aralıklarından `wc` ile sayıldı: `prompts.ts:3-73` ve `75-107`). CourtListener bölümü +339 sözcük / 2.206 karakter. Token sayısı ölçülmedi; kaba tahmin (tahmin): sabit kısım 3.000-3.500 token, araç şemaları ayrıca (`toolSchemas.ts` 20.405 karakter dosya boyutu; şemaların kendisi bunun bir bölümü, bu dosya kodla karışık olduğu için token tahmini yapılmadı).

Bölümler (başlıklar kodda büyük harfli):

| Bölüm | İçerik | Satır |
| --- | --- | --- |
| Kimlik + CORE RULES | Hukuk asistanı; kesin ol; belge içeriği uydurma; kullanıcıya araç adı söyleme; en çok 10 araç turu, bağımsız çağrıları topla; belge/sürümü bir kez oku; `ask_inputs` kuralları | `prompts.ts:3-11` |
| RESPONSE FORMATTING | GFM; yalnızca boru tablo; tablo kod bloğu içinde olmaz; hücre tek satır; LaTeX yalnız zorunluysa ve `$$` ile | 13-17 |
| WORKFLOWS | `[Workflow: ...]` varsa ilk iş `read_workflow`; varlıkları `read_document` ile aç; varlıklar değişmez, düzenlemeden önce `replicate_document` | 19-22 |
| LIBRARY TEMPLATES | Şablon değişmez; kopyalamadan düzenleme yok | 24-25 |
| DOCUMENT CITATIONS | `[N]` imleri sıralı ve atlamasız; en sonda `<CITATIONS>` JSON dizisi; `doc_id` yalnızca `doc-N` etiketi; alıntı ≤ ~25 sözcük, bir imde en çok 3 alıntı; PDF sayfa imi `[Page N]`; elektronik tabloda `sheet`+`cell`; sayfa sınırı için `[[PAGE_BREAK]]` | 27-52 |
| DOCX GENERATION | "Belge yaz" denince `generate_docx`; başlık düzeyleri sırayla; varsayılan numarasız; sözleşmede imza bloğu yeni sayfada | 54-63 |
| DOCUMENT EDITING | `edit_document` için kurallar; numaralı madde eklenir/silinirse aşağı akış numaralandırma ve çapraz referansları aynı düzenlemede güncelle | 65-73 |
| DOCUMENT NAMES IN PROSE | `doc-N` etiketi kullanıcıya gösterilmez | 75-78 |
| REASONING TRACE SAFETY | Muhakeme özetlerinde kod/JSON/şema/araç argümanı yok | 80-83 |
| UNTRUSTED CONTENT POLICY | Çit içindekini veri say; talimatları yok say; kapanış etiketi nonce'lu olmalı | 85-92 |
| WORKFLOW / USER INSTRUCTIONS POLICY | Nonce'lu iş akışı ve kullanıcı talimatlarına uy ama sistem kurallarını aşamazlar | 94-101 |
| GENERAL GUIDANCE | Kanıta dayalı iddiayı belgeden atıfla; belge yoksa hukuki bilgiden cevapla; emoji yok | 103-106 |

Gözlem: bu prompt "yapı + biçim + atıf JSON + belge işleme + güvenlik çiti" üzerine kurulu ve alan bilgisi (hukuki yöntem, mevzuat hiyerarşisi, yetki) neredeyse içermiyor (tek hukuki-alan bloğu CourtListener bölümü). Davranış kurallarının çoğu, bir önceki yanlışlıktan doğmuş gibi duran "bunu yapma" kuralları (örn. sayfa numaralarını atlama, tekrar okuma, `doc-N` sızdırma).

Ek: Word için ayrı bir prompt var ve istemci araçları sürümünde "emit markup and hope" yerine "araç çağır, sonucu oku" mantığına geçilmiş (`wordPrompt.ts:25-60` yorumları); bu bölüm yalnızca üstten okundu.

### 12. Başka gözlemler

- Başlık üretimi paralel çalışır: ilk mesajdan sonra ayrı bir (genelde daha küçük) model çağrısıyla başlık yazılır, ana yanıtla yarışır ve iptalde atılır (`chat.routes.ts:679-705`). Başarısızlık ayrı günlüklenir ve ana cevabın başarısızlığından ayrıştırılır (797-804, 876-884).
- Boş cevap koruması: model temiz ama boş bitirirse ve araç çıktısı da yoksa kullanıcıya "The model returned an empty response" hatası yazılır (`chat.routes.ts:744-762`).
- Turun kalıcılığı önce "rezerve edilmiş asistan satırı" olarak başlar; kimlik kalıcı hale gelmeden istemciye verilmez (`chat.routes.ts:613-636`). Tur bitince satır olay listesiyle doldurulur (776-778).
- Önbellek ipuçları: OpenAI için `promptCacheKey = sohbet kimliği`, Anthropic için son mesaja `ephemeral` önbellek kesme noktası (`aiSdk.ts:402-437`). Prefix önbelleğini bozmamak için zaman damgaları kayıtlı gönderim zamanından üretiliyor (`contextBuilders.ts:487-494 yorumu`, `722-736`). Bu, llama.cpp/vLLM prefix cache'i için de geçerli bir ilke.
- Atıfın `hasToolOutput` / `COMPLETES_TEXTLESS_TURN` sınıflaması: her olay türü "metinsiz tur için yeterli çıktı mı" diye derleme zamanında sınıflandırılmak zorunda (`contextBuilders.ts:797-835`); yeni olay eklemeyi tip hatasına çeviren iyi bir kalıp.

## HakHukuk için değerlendirme

### Taşınır

1. **Sunucu sahipli koşu + numaralı çerçeve tamponu + `from=` ile yeniden bağlanma** (`streamRuns.ts`, `assistantTurnRuns.ts`). Model türünden bağımsız, saf altyapı. Yerel uygulamada "aynı anda birden çok agent işi" ve sayfa yenileme senaryosu için doğrudan karşılığı var. FastAPI'de `asyncio.Task` + her iş için sıralı olay günlüğü (bellek içi liste ya da SQLite tablosu) + `Last-Event-ID`/`from` ile `EventSourceResponse`. Bellek-içi tek süreç sınırı bizim tek kullanıcılı yerel uygulamada sorun değil. Bu kalıbın tek şartı: bağlantı kopması iptal anlamına gelmesin, iptal ayrı uç olsun. Boşta ve azami ömür saatleri ile "iptal sonrası 30 sn'de zorla bitir" koruması da taşınmalı (anahtar kilitlenmesini önlüyor).
2. **`read_document` yinelenen okuma korumasındaki ders** (`documentOps.ts:1412-1435` yorumu). 4B model "araç hata verdi mi" ayrımını daha da zor yapar; ret yanıtı yapılandırılmış, açıklayıcı ve "tekrar deneme" dese bile model bazen döngüye girebilir. Bizim için: ret yanıtı kısa, içerik anahtarı yok, sonraki adımı adıyla söylüyor olmalı. Ek olarak ardışık özdeş araç çağrısı için genel bir döngü kesici (3 özdeş çağrı sonrası zorla son cevap turu) eklemeliyiz; Mike'da yok.
3. **Spotlighting (nonce'lu çit)** (`contextBuilders.ts:56-96`). Kullanıcı belgelerinde istem enjeksiyonu riski modelden bağımsız; maliyeti birkaç token. Yerel tek kullanıcılı bir uygulamada bile web'den ya da dosyadan gelen metin için gerekli. Tolerans: 4B'nin çit sözdizimini ne kadar izlediği ölçülmeli (açık soru).
4. **Sunucu tarafı alıntı doğrulaması** (`verifyCitations.ts`, `streaming.ts:796-852`). Deterministik, model gerektirmiyor ve HakHukuk'un "uydurma madde numarası" derdine tam uyuyor. Üç kademeli eşleştirme (birebir, boşluk/harf, noktalama) ve kaynak metinle değiştirme (kayma düzeltmesi) doğrudan alınabilir. Türkçeye özgü: büyük/küçük harf katlamada `İ/ı` ve `I/i` ayrımı, "m." / "madde" / "md." kısaltma farkları normalize edilmeli (Mike İngilizce ağırlıklı).
5. **Zorunlu `ask_inputs` benzeri duraklatma deseni, tur biter + devam yeni istek** (`streaming.ts:154-176, 703-719`; `chat.prepare.ts:372-415`). Model durumu sunucuda tutmuyor: duraklama = turu bitir, yanıt gelince yeni isteğe önceki aktivite özetini koy. Bu, 4B için zaten doğru kalıp çünkü uzun bekleyen bir üretimi korumak gerekmiyor ve KV önbelleği serbest kalıyor. Yanıt tek kullanımlık atomik eklenmeli (`stale` 409). Şema sınırları da küçültülebilir: Mike 12 öğe/8 seçenek izin veriyor, 4B için tek çağrıda 1-3 soru yeter (öneri, ölçülmedi).
6. **Araç partisi sözleşmesi + her `tool_use` için mutlaka bir `tool_result`** (`aiSdk.ts:239-294`, `streaming.ts:721-744`). Eksik sonuç, bilinmeyen araç, devre dışı araç: hepsi aynı `{"error": "Tool 'x' is not available."}` biçimiyle modele söylenir. Bizim yürütücüde aynı değişmez kural olmalı.
7. **Yazma araçlarını kapsam-içi kapatma, ikili savunma** (`toolSchemas.ts:17-42`, `streaming.ts:324-326, 589-594`): şemadan gizle + gelirse reddet. Agent işlerinin bazıları salt okunur modda koşacağından doğrudan yararlı.
8. **Yerel model tolerans katmanı** (`toolCallParsing.ts`, `localModelMiddleware.ts`). `<think>` ayırma, metindeki `<tool_call>` JSON'unu ve XML bloklarını çıkarma, `jsonrepair`, ad+girdi tekilleştirme, işaretleme bastırma. Mike bunu zaten yerel modeller için yazmış ve bizim hedefimiz (Qwen3.5-4B, llama.cpp) tam bu sınıfta. Python karşılığı: `json_repair` paketi, aynı regex ailesi. Daha iyisi: llama.cpp'nin gömülü chat şablonu ve `--jinja` ile yapılandırılmış araç çağrısı çıktısını kullanıp bu katmanı yedek olarak tutmak. Bu seçim bir tasarım kararı gerektirir (açık sorular).
9. **Önceki turun etkinlik özeti yerine araç sonucu replay'i yok** (`contextBuilders.ts:556-575`). 4B için bağlam kısıtlı; her turda yalnızca bir satırlık etkinlik özeti ve belgeyi yeniden okumak, ham sonuçları taşımaktan çok daha ucuz ve KV önbelleğiyle uyumlu.
10. **`next_required_action` kalıbı** (araç sonucuna sonraki adım yazmak). 4B için sistem prompt'una güvenmekten daha güvenilir: talimat, modelin dikkatinin en taze olduğu yere (araç çıktısına) konur. Özellikle "yazdığın belgeyi geri oku" ve "indirme bağlantısı yazma" gibi kurallar için.
11. **Çıktı olaylarının derleme zamanı sınıflandırması** (`contextBuilders.ts:797-835`) ve sabit kullanıcıya-görünür hata metni + ayrıntı yalnızca günlüğe (`streaming.ts:119-145`). Python'da `Literal`/`Enum` + `match` ile kolay.

### Yeniden tasarlanmalı

1. **Sistem promptu (~12.200 karakter, ~3k token tahmin) 4B için çok büyük ve çok kural içeriyor.** 4B, 30'dan fazla "yapma" kuralını tutarlı izleyemez; araç şemaları (toplam 20 KB'ye yakın dosya içinde) de eklenince Q4 4B'nin etkin bağlamının önemli bölümü talimata gider. Yeniden tasarım: (a) prompt'u 400-700 token'a indir, yalnızca kimlik, temel kaçınmalar (uydurma yok, kaynak göster), atıf biçimi; (b) biçim, belge üretimi, DOCX numaralandırma, formül gibi blokları, ilgili araç çağrıldığında **araç sonucuna** ekle (Mike bunu zaten `citationReminder` ve `next_required_action` ile kısmen yapıyor; çizgiyi genişlet); (c) "RESPONSE FORMATTING" ve "DOCX GENERATION" gibi uygulamaya özgü blokları ilgili görev kipinde yükle (dinamik prompt). Bu bir bağlam bütçesi değil, güvenilirlik meselesi: Mike'ın uzun prompt'u frontier modelin talimat takibine güveniyor.
2. **Araç kataloğu 4B için fazla geniş; asgari kümeye indirilmeli** (bkz. "4B için asgari araç seti önerisi"). Mike'da 12+ araç, ayrıca MCP ve Google dinamik araçları var; 4B'nin araç seçim doğruluğu araç sayısıyla düşer (ölçülmeli, kaynak göstermiyorum).
3. **Atıf biçimi.** Model, cevabın sonunda iç içe JSON (`ref`, `doc_id`, `quotes[{page, quote}]`) yazmak zorunda ve `[N]` imlerini sıralı, atlamasız, tutarlı numaralamak zorunda. 4B için bu aynı anda hem biçim hem alıntı doğruluğu hem de sıra sayma yükü. Öneri: modelden yalnızca **kaynak tanımlayıcı + kısa alıntı** istenmeli (örn. `[K1: m.12]`), JSON'a çevirme, yeniden numaralama ve tam alıntıyı kaynak metinden çekme sunucuda yapılmalı (Mike zaten alıntıyı kaynak metinle değiştiriyor; bir adım daha ileri gidip modelin alıntıyı hiç yazmamasını sağlayabiliriz: model yalnızca madde/kaynak kimliği verir, alıntıyı sunucu çıkarır). Türk mevzuatında doğal atıf birimi (kanun no + madde + fıkra/bent) zaten tanımlayıcı olduğundan bu kolay.
4. **Akışsız çağrıya düşme (`localModelMiddleware.ts:289-297`).** Mike yerel modeller için araç içeren adımları `doGenerate` ile alıyor; bu, kullanıcıya token akışının kaybı demek. llama.cpp için akışlı araç çağrısı ayrıştırması (yerleşik) sağlıklı çalışıyorsa bunu kullan; çalışmıyorsa Mike'ın yaptığı gibi araçlı adımları akışsız çağır ama araçsız (son cevap) adımını akışla ver. Hangisinin 4B'de güvenilir olduğu ölçülmeden karar verilmemeli (açık soru).
5. **Tur sınırı ve bütçe.** Mike'ın 16 tur, 4 sa ömür, 5 dk boşta varsayılanları bulut modele göre. Yerel 4B'de tur başına gecikme farklı (ön dolum + üretim) ve eşzamanlı agent işleri aynı GPU'yu paylaşır: (a) sınırı **görev başına** değil **toplam token/zaman bütçesi** cinsinden de koy; (b) boşta zaman aşımını model hızına göre ayarla (60 sn parça arası bile uzun belge ön dolumunda tetiklenebilir; Mike'ın "ilk parça 2 dk" sınırı yerelde yetersiz kalabilir); (c) modele söylenen bütçeyi ve zorlananı aynı yap veya farkı kasıtlı ve ölçülmüş tut. Mike'ın "prompt 10, kod 16" ikilisi 4B için güvenli bir model olabilir ama gerekçesi yazılı değil; kendi ölçümümüzle seçilmeli.
6. **Bağlam yönetimi.** Mike bağlam taşmasını yönetmiyor (geçmiş kırpma, özet, ya da belge parçalama yok; `read_document` tam metni basıyor, Word için 200k karakter sınırı). 4B'de (8-32k etkin bağlam) bu çalışmaz. Gerekli: (a) `read_document` yerine **sayfalı/parçalı okuma** (örn. `read_document(doc_id, bölüm/aralık)`), (b) tam metni nadiren ver, aramayı (`find_in_document` ya da mevzuat arama) birincil yola çıkar, (c) araç sonuçlarında karakter üst sınırı (Mike yalnız onaylı bağlayıcı sonuçlarını 4.000 karaktere kırpıyor: `connectorApprovals.ts:36`), (d) geçmiş turlar için sürekli özet ya da kayan pencere.
7. **Sıralı yürütme + paralel çağrı.** Mike modelden "bağımsız çağrıları topla" der ama yürütmeyi sıralı yapar. 4B için paralel çağrı üretmek ek hata kaynağıdır; ilk sürümde adım başına **tek** araç çağrısına izin vermek (SDK'da `parallel_tool_calls=false` karşılığı, llama.cpp'de `parallel_tool_calls: false`) hem daha güvenilir hem de sıralı yürütmeyle tutarlı olur. Çoklu eşzamanlı agent işi ise **iş düzeyinde** (her iş kendi koşusu) paralel, **iş içinde** sıralı olmalı. GPU paylaşımı için iş kuyruğu/yarı-eşzamanlılık sınırı gerekir (Mike'da yok, çünkü sağlayıcı bulutta).
8. **Bozuk argümanı sessizce `{}` yapmak** (`toolDispatcher.ts:461-467`). 4B'de bozuk JSON sık olacak; boş argümanlı çağrının araç hatası olarak dönmesi kafa karıştırır ("edits array is required" gibi bir mesaj gerçek nedeni, yani bozuk JSON'u, gizler). Bizim yürütücü **ayrıştırma hatasını açıkça** söylemeli ("argümanlar geçerli JSON değil: ..., şemaya uygun yeniden gönder") ve bunu tekrar sayacıyla sınırlamalı (en çok 2 düzeltme denemesi, sonra pes).
9. **Muhakeme (thinking) yönetimi.** Mike `reasoning: "high"` varsayılanı ve `<think>` ayırmayı kullanıyor, ama muhakeme token bütçesi yok. Qwen3.5-4B'de düşünme sınırsız uzayabilir (projede "thinking ON with budgeted forced close" rejimi kayıtlı: 1024 düşünme + 512 cevap); araç döngüsünde her adım için ayrı bir düşünme bütçesi ve zorla kapatma gerekir. Mike'da bu mekanizma yok (yalnızca `maxOutputTokens` ve sağlayıcıya bağlı).
10. **Çok kiracılı izin sistemi.** `allowDocumentMutation`, `ensureDocAccess`, `can(role,"content.edit")`, organizasyon/proje rolleri; Mike'ın erişim kontrol ağırlığı tek kullanıcılı uygulamamızda gereksiz. Yalnızca "bu iş yazma yapabilir mi" bayrağı kalmalı (salt okunur agent işleri için).
11. **Veritabanı sözleşmesi.** Mike Supabase RPC'leri (`append_chat_ask_inputs_response`, `append_chat_assistant_events`) ve satır rezervasyonuna bağımlı. SQLite + SQLAlchemy'de aynı atomiklik (tek kullanımlık yanıt, rezerve edilmiş asistan satırı) tek işlemde `UPDATE ... WHERE status='pending'` ile sağlanabilir; ayrıca yeniden tasarım gerek.

### Taşınmaz

1. **AI SDK'ya yaslanan döngü.** Döngünün çekirdeği (adım yönetimi, şema doğrulama, geçersiz araç/argüman için dinamik hata sonucu, provider başlıkları) Mike'da `streamText`'te. Python'da eşdeğeri yok; kendi döngümüzü yazacağız. Mike'ın bunu AI SDK'dan aldığı davranışları (hatalı araç çağrısı → hata sonucu → model toparlanır) bilinçli yeniden uygulamalıyız.
2. **ABD içtihat araçları (CourtListener).** Alan olarak ilgisiz; yalnızca iki ders alınır: (a) tur başına sınır (örn. "en çok 3 `find_in_case`"), (b) "rate-limit görünce o tur için aracı bırak" kuralı (`courtlistenerTools.ts:32`). Türk mevzuatı için karşılığı mevzuat arama/madde getirme araçları olacak.
3. **Belge üretimi araç ailesi (`generate_docx/excel/ppt`)** ve `.docx` izlenen değişiklik düzenlemesi (`edit_document`, `docxTrackedChanges`, Word eklentisi araçları). Yoğun bir mühendislik (numaralandırma, imza bloğu kuralları, OOXML), 4B için çıktı şemasının iç içe derinliği (bölümler → tablo → satırlar) güvenilir değil; HakHukuk'un hedefi mevzuat sorusu cevaplamak olduğu sürece kapsam dışı. Gerekirse en sade biçimde (düz metin → `.docx`, sunucuda şablonla) ve modele yapı yazdırmadan.
4. **Bağlayıcı katmanı (MCP, Google Drive, Workspace) ve onay akışı.** Tek kullanıcılı yerel uygulamada ilk sürüm için gereksiz. (Onay deseninin kendisi, `ask_inputs` ile aynı mekanizma, 7. maddede taşınabilir diye not edildi; bağlayıcılar değil.)
5. **Word eklentisi köprüsü** (`client_tool_call`, `submitClientToolResult`, istemci araç sentinel'leri). Eklentiye özgü.
6. **Organizasyon/paylaşım/denetim/hafıza konsolidasyonu/Sentry.** Çok kullanıcılı SaaS bileşenleri.
7. **Prompt caching ipuçları sağlayıcıya özgü kısımlar** (`anthropic.cacheControl`, `bedrock.cachePoint`, `openai.promptCacheKey`). llama.cpp'de eşdeğeri `cache_prompt` / slot yeniden kullanımı; mantık (önek bayt bayt aynı kalsın) taşınır, kod taşınmaz.

## 4B için asgari araç seti önerisi

İlke: araç sayısını azalt, her aracın şemasını düz tut (iç içe nesne yok, mümkünse 1-3 alan), çıktı kısa ve kendi kendini açıklayan olsun, "sonraki adım" sonuçta yazsın. Aşağıdaki küme Mike'daki işlevlerin 4B'ye uygun bir alt kümesidir; ölçüm yapılana dek öneridir.

| Araç | Karşılığı Mike'da | Parametreler | Çıktı | Not |
| --- | --- | --- | --- | --- |
| `mevzuat_ara` | (yok; CourtListener arama/`find_in_document` karışımı) | `sorgu` (string), `adet` (1-5) | En çok `adet` kayıt: `[{kimlik: "6098/m.49", baslik, kisa_metin}]` | Bizim BM25+bge-m3 erişimi; Mike'da yok, HakHukuk'un çekirdeği |
| `madde_getir` | `read_document` (parçalı hali) | `kimlik` (örn. `"6098/m.49"`) | Madde metni, fıkra/bent yapısı, yürürlük durumu; üst sınır (örn. 3.000 karakter) | Tam belge yerine birim okuma; atıf buna dayanır |
| `belge_ara` | `find_in_document` | `belge`, `sorgu`, `adet` (varsayılan 5) | `[{sayfa, parca}]` | Kullanıcının yüklediği belge için; Mike'ın şemasının sadeleşmişi |
| `belge_oku` | `read_document` | `belge`, `bolum` (sayfa aralığı ya da parça no) | Sayfa/parça numaralı metin, üst sınırlı, kalan parça sayısı belirtilir | Tam metin yerine sayfalama; tekrar okuma korumasıyla |
| `kullaniciya_sor` | `ask_inputs` | `soru` (string), `secenekler` (0-4 string) | Yok (tur durur); devam yeni istekle | Tek soru; çoktan seçmeli/serbest metin ayrımı seçenek varlığıyla |
| `bitir` ya da son cevap | (Mike'da yok; model araç çağırmayı bırakarak bitiriyor) | — | — | İsteğe bağlı: 4B için "araç çağırma = bitmedi, metin = bitti" yeterince açık değilse açık bir bitiş sinyali |

Bilinçli olarak dışarıda bırakılanlar: belge üretme/düzenleme, iş akışı araçları, çoklu belge toplu okuma, bağlayıcılar. İhtiyaç doğarsa en öncelikli ek: `belge_olustur(baslik, metin)` (düz metin, sunucuda şablonlu).

Zorunlu çevre kuralları (araç dışı):

1. Adım başına tek araç çağrısı; ardışık özdeş (ad+argüman) çağrı en çok 2 kez, sonrasında zorla son cevap adımı.
2. Bozuk argüman = açık hata + en çok 2 düzeltme.
3. Tur sınırı ve token bütçesi kendi ölçümümüzle seçilecek (başlangıç önerisi: 6-8 tur, Mike'ın 10/16 değerleri başlangıç noktası değil üst sınır olarak okunmalı).
4. Araç sonuçlarında karakter üst sınırı; aşılırsa "kırpıldı, `bolum` ile devam et" notu.
5. Alıntı doğrulaması sunucuda deterministik; modelden yalnızca kaynak kimliği istenir.
6. Her `tool_use` için mutlaka sonuç; bilinmeyen araç `{"error": "Tool 'x' is not available."}` ile cevaplanır.

## Açık sorular

1. **Yapılandırılmış mı, metinsel mi araç çağrısı?** llama.cpp `--jinja` ile Qwen3.5-4B'nin yerleşik araç çağrısı şablonunu kullanırsak Mike'ın tolerans katmanına (`toolCallParsing.ts`) ne kadar ihtiyaç kalır? Bunu 4B ile ölçmek gerek (hata sınıfları: bozuk JSON, metne gömülü çağrı, yanlış araç adı).
2. **Akışlı araç çağrısı güvenilir mi?** Mike yerel modeller için akışsız yola düşmüş (`localModelMiddleware.ts:292-294`); gerekçesi "kısmi akıştan güvenilir toparlanamaz". llama.cpp'nin akışlı tool_call çıktısında aynı sorun 4B'de görülüyor mu?
3. **Prompt/kod tur sınırı farkının (10 vs 16) nedeni.** Dosyada gerekçe yok; test (`aiSdk.toolErrors.test.ts:59-100`) yalnızca 16 sınırını doğruluyor. 4B'de modele söylenen ve zorlanan sınır aynı mı olmalı?
4. **Mike'ın araç çağrılarındaki başarı oranı bilinmiyor.** Kod tabanında 4B ölçümü ya da başarı istatistiği yok; bütün tasarım frontier modele güveniyor. "Bu araçta 4B yüzde kaç doğru" sorusu kendi ölçümümüzle yanıtlanmalı.
5. **Yinelenen okuma korumasının genellemesi.** Mike yalnızca okumada koruma uyguluyor. 4B'de hangi araç çağrısı tekrar döngüsüne giriyor (arama? madde getirme?) ve genel bir (ad+argüman) tekrar sayacı yeterli mi?
6. **`ask_inputs` devamının geçmiş biçimi.** Mike önceki turun araç etkinliğini son asistan mesajına metin olarak ekliyor. 4B'nin bu biçimi ("- user answered: ...") doğru yorumlayıp yorumlamadığı ölçülmeli; alternatif: yanıtı doğrudan kullanıcı mesajı olarak vermek.
7. **Eşzamanlı agent işlerinde GPU paylaşımı.** Mike'da yok. llama.cpp slot sayısı ve vLLM/SGLang sürekli toplulaştırma ile iş içi sıralı, işler arası paralel yürütme için kuyruk tasarımı ayrı ele alınmalı.
8. **Atıf biçimi.** Modelden yalnızca kaynak kimliği alıp alıntıyı sunucuda çekmek hukuki "birebir alıntı" gereksinimini karşılar mı, yoksa modelin kendi ifadesiyle atıf yapması (özet + kaynak) ürün gereği mi? Ürün kararı.
9. **`<think>` içeriğinin geçmişte saklanması.** Mike `replayReasoning` ile yalnızca bazı modeller için muhakemeyi geçmişe geri koyuyor (`registry.ts` `replaysReasoning`, tolerateTextToolCalls'ın hemen altı, yaklaşık 150-153; `aiSdk.ts:383-400`). Qwen3.5-4B için geri koymak mı, atmak mı daha iyi (bağlam maliyeti vs tutarlılık)?

## Okunmadı

- `toolDispatcher.ts` içindeki CourtListener dalları (satır 867-1428) yalnızca başlık/imza düzeyinde tarandı, gövdeleri okunmadı.
- `documentOps.ts`: `generateDocx` (69-532), `generateExcel`/`generatePpt` gövdeleri, `readDocumentContent` içindeki belge türü çıkarım ayrıntıları (PDF, DOCX, tablo, sunum; yalnızca log satırlarından türler çıkarıldı), `loadCurrentVersionBytes`.
- `lib/docxTrackedChanges.ts`, `lib/pdfText.ts` (yalnızca `[Page N]` imleri için ilgili satırlara bakıldı), `lib/spreadsheet.ts`, `lib/officeText.ts`.
- `contextBuilders.ts`: `buildDocContext`, `buildWorkflowStore`, kişiselleştirme/profil ayrıntıları, `attachPriorReasoning`, `appendAskInputsResponseToAssistantMessage` gövdesi (1000-1605 aralığı).
- `modules/chat/engine/citations.ts` (347 satır; `parseCitations`, `createCitation`, kısmi ayrıştırma gövdeleri) yalnızca dışa aktarılan imzalar listelendi.
- `modules/chat/engine/requestValidation.ts` (451 satır): yalnızca ask_inputs ve mesaj ayrıştırma başı; mesaj sayısı/boyutu üst sınırı arandı, bulunamadı (sınırın hiç olmadığı kesin değil).
- `wordClientTools.ts` (919) ve `wordPrompt.ts` (117): yalnızca sabitler, bekleme köprüsü ve prompt'un başı; araç yürütme ayrıntıları ve `apply_word_edits` sonuç biçimi okunmadı. `modules/word-chat/*` okunmadı.
- `modules/project-chat/*`, `modules/tabular/*` (yalnızca `extraTools` geçişi ve heartbeat kullanımı için grep).
- `lib/memory/*` (`buildMemoryTurn`, hafıza konsolidasyonu), `lib/mcpConnectors.ts`, `lib/mcp/*`, `lib/integrations/*`.
- `lib/llm/providers.ts` (758 satır; yalnızca 480-545), `cloudProviders.ts`, `models.ts`, `providerErrors.ts`, `rawStreamLog.ts`.
- `lib/queue/*`, `lib/storage.ts` ve veri katmanı.
- Frontend: SSE ayrıştırma, yeniden bağlanma durum makinesi (`useAssistantChat.ts` yalnızca satır numarası grep'lendi), `AskInputPopup` arayüzü.
- Test dosyalarının gövdeleri (yalnızca `describe/it` başlıkları: `aiSdk.toolErrors.test.ts`, `streamingToolGating.test.ts`, `routeStreaming.test.ts`); diğer testler (`streamingClientTools`, `connectorApprovals`, `documentContext`, `prompts.test.ts` vb.) hiç açılmadı.
- `packages`, `docs`, `desktop`, `e2e`, `loadtest` dizinleri bu bölümde okunmadı.
- Gerçek çalıştırma yapılmadı; tüm davranışlar kaynak okumasına dayanıyor, bir model ile doğrulanmadı.
