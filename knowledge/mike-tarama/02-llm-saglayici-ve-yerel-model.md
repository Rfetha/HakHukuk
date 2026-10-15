# Mike: LLM sağlayıcı soyutlaması ve yerel model yolu

Tüm yollar kaynak köküne göredir (`mike-main/`). Kod kopyalanmamıştır; tasarım kendi cümlelerimizle anlatılmıştır. Sayılar dosyadan alınmıştır; çıkarım olan yerler "tahmin" veya "çıkarım" diye işaretlidir.

## Kapsam ve okunan dosyalar

Tamamı satır satır okundu:
`backend/src/lib/llm/` altında `providers.ts` (758 satır), `aiSdk.ts` (694), `registry.ts` (274), `localModelMiddleware.ts` (353), `toolCallParsing.ts` (466), `providerDeadlines.ts` (105), `providerErrors.ts` (97), `apiKeyErrors.ts` (97), `types.ts` (206), `models.ts` (449), `index.ts` (22). Kısmen: `cloudProviders.ts` (yalnız `normalizeCustomBaseUrl` ve `customEndpointCredentials`), `rawStreamLog.ts` (ilk 60 satır).
Ayrıca: `backend/src/modules/models/models.compatible.ts`, `models.service.ts`; `docs/configured-models.md`, `docs/direct-provider-models.md` (ilk 60 satır), `packages/byok-validation/README.md` ve `cases.json` (ilk 40 satır); bağlantı noktaları için `backend/src/lib/runtimeConfig.ts` (129-145), `backend/src/modules/user/user.apiKeyStore.ts` (190-240), `backend/src/modules/chat/engine/contextBuilders.ts` (255-330), `backend/src/modules/chat/engine/streaming.ts` (480-560), test dosyalarının yalnızca test adları (`backend/src/lib/__tests__/localModelMiddleware.test.ts`, `toolCallParsing.test.ts`, `backend/src/lib/llm/aiSdk*.test.ts`).

Önceki yüzeysel okumaya göre düzeltmeler ve eklemeler "Doğrulama notları" bölümünde toplandı.

## Nasıl çalışıyor

### 1. Genel mimari: AI SDK üzerinde ince bir katman

Mike kendi HTTP/SSE istemcisini yazmaz; Vercel AI SDK (`ai` ^7, `backend/package.json`) üzerine kuruludur ve çağıran koda tek bir sözleşme sunar: OpenAI biçiminde araç şemaları, `{role, content}` mesajları, bir `runTools(calls)` geri çağrısı ve içerik/akıl yürütme/araç-başlangıcı geri çağrıları (`backend/src/lib/llm/types.ts:307-344, 391-420`). Dışarıya açık yüzey iki fonksiyondur: `streamChatWithTools` ve `completeText` (`backend/src/lib/llm/index.ts:7-16`).

Her sağlayıcı bir "adaptör yapılandırması" (`AiSdkAdapterConfig`: model nesnesi, etiket, akıl yürütme destekli mi, geri oynatma açık mı) döndüren bir fabrika fonksiyonudur (`backend/src/lib/llm/aiSdk.ts:211-231`; fabrikalar `backend/src/lib/llm/providers.ts:152-525`). Tüm sağlayıcıların ortak döngüsü tek yerde, `streamAiSdk` içinde yaşar (`aiSdk.ts:439-650`).

### 2. Sağlayıcı seçimi ve model kaydı

- Sağlayıcı, model kimliğinin ön ekinden çıkarılır: `ollama`, `openrouter/`, `vercel/`, `opencode-go/`, `bedrock/`, `azure/`, `azure-foundry/`, `vertex/`, `xai/`, `custom/`, sonra `claude`, `gemini`, `gpt-`, `mistral-` (`models.ts:161-181`). Tanınmayan kimlik hata fırlatır (`models.ts:180`). Toplam 15 sağlayıcı etiketi vardır (`types.ts:279-294`).
- Operatör bildirimli modeller ön ek kurallarından önce kazanır (`models.ts:164-165`). Bu kayıt, tek bir ortam değişkeni `MIKE_MODEL_CONFIG_JSON` içinden okunur ve süreç başına bir kez önbelleğe alınır; geçersiz JSON yüklenirken gürültülü biçimde hata verir, geçersiz tek tek girdiler sessizce atlanır (`registry.ts:23-59, 200-256`). Kaydedilebilen tek sağlayıcı türü `openai-compatible`'dır (`registry.ts:159-162, 216`). Alanlar: `id`, `location` (`cloud`|`local`), `baseUrl`, `apiModel`, `apiKey`/`apiKeyEnv`/`apiKeyProvider`, `tolerateTextToolCalls`, `maxTokensField`, `replayReasoning` (`types.ts:435-460`; belge: `docs/configured-models.md:37-50`).
- Kimlik çözümleme (`resolveModel`) sabit katalog, kayıtlı modeller, `ollama/`, yönlendirici ön ekleri ve "güvenli hesap-modeli" biçimi dışındakini reddedip bir yedeğe düşer (`models.ts:309-336`). Hesaba özgü kimlikler (Bedrock, Azure, Vertex, xAI, custom) URL'ye girebildiği için sıkı bir dilbilgisiyle doğrulanır: nokta/boş/`..` segmentleri, `?`, `#`, `%`, ters eğik çizgi, boşluk ve kontrol karakterleri yasaktır (`models.ts:235-287`). Aynı kural ön yüzde de kopyalanır ve `packages/byok-validation/cases.json` ile iki tarafın uyumu test edilir (`packages/byok-validation/README.md:7-20`). Bu paket yalnızca veri/conformance dosyasıdır; çalışma zamanında hiçbir şey onu içe aktarmaz (aynı README, satır 3-5).
- Statik katalog tamamen bulut modelleridir (Claude, Gemini, GPT, Mistral kimlikleri, `models.ts:8-44`). Yerel model için katalog yoktur; Ollama'da `GET {OLLAMA_BASE_URL}/models` canlı sorgulanır, ulaşılamazsa boş liste döner (`modules/models/models.service.ts:257-273`), kayıtlı modeller ise `GET /models/configured` ile gizli bilgisiz özet olarak sunulur; anahtar kaynağı bildirilmişse ama çözülemiyorsa model listeden gizlenir (`registry.ts:128-140`, `models.service.ts:276-294`, `docs/configured-models.md:52-55`).
- "Komite" (`CommitteeModel`: üyeler + başkan modeli, "synthesize" stratejisi) tipi ve doğrulayıcı vardır (`types.ts:466-480`, `registry.ts:258-274`), ancak bu bölümde (`backend/src` içinde test dışı grep) onu çalıştıran bir kod bulunamadı. Durum: yalnızca tip/kayıt iskeleti; çalıştırıcı bu taramada görülmedi.

### 3. Üç ayrı "yerel" yol ve hangisine neyin uygulandığı

Bu, önceki okumada karışmış olabilecek en önemli ayrımdır.

| Yol | Nasıl seçilir | Taban URL | Tolerans middleware'i | Akıl yürütme parametresi |
| --- | --- | --- | --- | --- |
| Ollama | `ollama...` ön eki (`models.ts:166`) | `OLLAMA_BASE_URL`, varsayılan `http://localhost:11434/v1` (`providers.ts:533-537`) | Yok (`providers.ts:655-668`, sarmalama yok) | Gönderilmez (`supportsReasoning:false`, 667) |
| Kayıtlı openai-compatible | `MIKE_MODEL_CONFIG_JSON` girdisi | girdideki `baseUrl` | Var, `location:"local"` ise varsayılan açık (`providers.ts:515-520`, `registry.ts:146-148`) | Gönderilmez (522) |
| BYOK `custom/` | kullanıcı anahtarı + taban URL | yalnız https ve genel adres (`cloudProviders.ts:214-243`) | Yok | Gönderilmez (466) |

Sonuçlar:
- Tolerans middleware'i yalnızca kayıtlı modellere bağlanır. Ollama yolu ve BYOK `custom/` yolu ham AI SDK openai-compatible istemcisini kullanır. Ollama için tek özel durum: araç desteklemeyen modelde "does not support tools" hatası gelirse ve `requireTools` yoksa, tek bir ek denemeyle araçsız yeniden çalıştırılır (`providers.ts:697-709`).
- BYOK `custom/` uç noktası https zorunludur, özel/yerel/metadata adreslerini ve noktasız ana makine adlarını reddeder ve DNS sabitlemeli "guarded fetch" ile gider (`cloudProviders.ts:230-241`, `providers.ts:419-439`). Dolayısıyla kullanıcı arayüzünden `localhost` llama.cpp bağlanamaz; yerel model için tek yollar ortam değişkeni (Ollama) ve `MIKE_MODEL_CONFIG_JSON`'dur. Kayıtlı modelin `baseUrl` doğrulaması yalnızca http/https ve kimlik bilgisi/sorgu/parça yokluğunu denetler (`registry.ts:184-198`); aiSdkFetch kullanır, korumalı fetch kullanmaz (`providers.ts:508`). Yani operatörün bildirdiği iç ağ adresleri serbesttir (tasarım gereği, güven sınırı operatördür).
- Kayıtlı modeller `max_tokens` yerine `max_completion_tokens` isteyebilir; bu, istek gövdesi dönüştürülerek yapılır (`providers.ts:498-507`).

### 4. Tolerans middleware'inin tam işleyişi

Amaç: yapılandırılmış araç çağrısı üretmeyen veya üretirken metinle karıştıran uç noktaları SDK'nın sağlayıcı sözleşmesine uydurmak. Taşıma, yeniden deneme ve SSE ayrıştırması SDK'ya bırakılır; middleware yalnızca "modelin söylediğini" yeniden yazar (`localModelMiddleware.ts:12-23`). Üç iş yapar: (a) `<think>` düzyazısını akıl yürütme parçasına çevirir, (b) metin akışındaki araç işaretlemesini gizler, (c) düzyazıda anlatılan araç çağrılarını gerçek araç-çağrısı parçalarına dönüştürür.

**Üç modda çalışır:**

1. Araç bildirilmiş akış isteği (`wrapStream`, `params.tools?.length`): akış HİÇ kullanılmaz; `doGenerate()` ile tam yanıt alınır ve sonra yapay olarak akış gibi yeniden oynatılır (`localModelMiddleware.ts:291-298`, `replayAsStream` 85-162). Gerekçe yorumu: bu modeller araç işaretlemesini düzyazıyla iç içe geçirir, kısmi akıştan güvenle yeniden kurulamaz (293-294; belge `docs/configured-models.md:104-106`).
2. Araçsız akış isteği: gerçek akış alınır ve `tolerantTransform` içinden geçirilir (`localModelMiddleware.ts:299-300`, `164-284`).
3. Akışsız üretim (`wrapGenerate`, 303-351): aynı süzgeçler toplu metne uygulanır.

**Think etiketi ayırma** (`toolCallParsing.ts:26-81`): `ThinkTagFilter` durumlu bir ayrıştırıcıdır. İçeride mi dışarıda mı olduğuna göre `<think>` veya `</think>` arar; etiket parçalar arasında bölünebileceği için, tamponun sonunda etiketin olası bir öneki varsa o kısım bekletilir (74-80). Biçim kesinlikle `<think>`/`</think>` sabitleridir (19-21). Yeniden oynatmada ek olarak sağlayıcının kendi `reasoning` içerik parçaları da birleştirilir (`localModelMiddleware.ts:72-83, 98-100`). Araç çağrısı kurtarma, düşünce bloğu çıkarıldıktan SONRA kalan görünür metin üzerinde yapılır (123, 317); yani düşünce içinde geçen sahte araç çağrıları işlenmez.

**Araç işaretlemesini gizleme** (`toolCallParsing.ts:83-141`): `TextToolMarkupFilter`, büyük/küçük harfe duyarsız şu işaretçilerden biri görüldüğü an, o noktadan itibaren her şeyi bastırır ve öncesini görünür bırakır: `<tool_call`, `<toolcall`, `<|tool_call`, `<function=`, `<function name=`, `<｜dsml｜tool_calls`, `<｜dsml｜invoke` ve `|` ASCII varyantları (83-93). Parça sınırında bölünen işaretçi başlangıçları da bekletilir (118-129). Bu nedenle işaretçiden sonra gelen meşru metin kullanıcıya hiç gösterilmez (çıkarım: araç çağrısı sonrasındaki bir cevap kuyruğu düşer).

**Metinden araç çağrısı kurtarma** (`parseTextToolCalls`, `toolCallParsing.ts:170-267`), sırasıyla:

1. DSML: `<｜DSML｜invoke name=...>` blokları ve `parameter` alt etiketleri; değerler `parseToolScalar` ile türlenir (sayı, true/false, null/none, `[`/`{` ile başlıyorsa JSON onarımı) (269-291, 405-422). Bulunursa doğrudan döner (174-175).
2. Hızlı ön kontrol regex'i: `<tool_call>`/`<toolcall>`, `<|tool_call|>` ailesi, `<function=`/`<function name=`, ya da satır başında `tool|function|name` ile başlayıp `:`/`=` gelen satır (176-181). Hiçbiri yoksa "sıradan cevap" sayılıp boş döner.
3. Gövde çıkarımı: açılış etiketlerinden bir sonraki açılışa ya da kapanışa kadar (kapanış etiketi `</tool_call>` veya `<|tool_call_end|>`; kapanış eksikse segment sonuna kadar) bir "gövde" alınır (183-194). Kapanış etiketinin eksik olması bu yüzden tolere edilir.
4. Her gövde için sırayla: (a) XML tarzı `<function=ad>` + `<alan>değer</alan>` (384-403); (b) JSON: kod çiti sökülür, ilk `{`/`[`'den dengeli kapanışa kadar tırnak ve kaçış izlenerek kesilir (430-466), OpenArc benzeri çift tırnak/çift iki nokta ("`{""ad"::`") düzeltilir (424-428, test: `__tests__/toolCallParsing.test.ts:35`), sonra `jsonrepair` kütüphanesi ile bozuk JSON onarılır (200-201; Python tarzı tırnak, sondaki virgül, eksik kapanış etiketi testte kanıtlı, `toolCallParsing.test.ts:24`).
5. JSON satırından üç şekil kabul edilir: `{name, arguments|input|parameters}`, `{function:{name, arguments}}` ve tek anahtarlı harita `{"aracAdı": {...argümanlar}}` (206-241). Kimlik yoksa `call_text_<tur>_<gövde>_<satır>` biçiminde sentetik kimlik üretilir (229-233).
6. JSON başarısız olursa "gevşek" kurtarma: yalnızca `name|tool|function : değer` kalıbıyla ad, `arguments|input|parameters :` sonrasında JSON aranır; argüman çözülemezse bile ad ve boş argümanla çağrı döndürülür ki araç kendi doğrulama hatasını versin (344-382, yorum 372-375).
7. Hiçbiri olmazsa iki ayrı hata: "yerel model kurtarılamayan bir araç çağrısı döndürdü" (256-259) veya "çalıştırılabilir bir araç tanımadı" (262-265). Mesajlar ürünün alana özgü bir moduna ("deterministic Trademark Monitor mode") yönlendirir, yani genel değildir. `DEBUG_LLM_TOOL_CALLS=1` ham gövdeyi 4000 karaktere kadar loglar (250-255).
8. Aynı ad+girdi çiftli çağrılar tekilleştirilir (158-168).

Bu hata türleri akışta `error` parçası olarak yayımlanır ve akış kapatılır (`localModelMiddleware.ts:122-128, 262-266`). Yani kurtarılamayan bir çağrı, turu yeniden denemeden bitirir.

**Alana özgü kalıntı:** `collapseTrademarkOwnerCalls`, adı `mcp_` ile başlayıp `tm_search_trademarks` içeren ve `owner_name` taşıyan birden çok çağrıyı tek `owner_names` listeli çağrıya birleştirir (293-342). Bu, marka izleme MCP aracına özgü bir yardımcıdır, HakHukuk'a ilgisi yoktur; ama "aynı araca art arda N benzer çağrı yerine toplu çağrı" deseni 4B için ilginçtir (aşağıda).

**Sonuç parçası:** Kurtarılan araç çağrısı olduğunda bitiş nedeni "tool-calls" olarak yeniden yazılır, sağlayıcının ham nedeni korunur (`localModelMiddleware.ts:36-40`).

### 5. Araç turları neden akışsız ve sonuçları

Neden (dosyadan): araç bildirilmiş her istek `doGenerate` ile yürür (`localModelMiddleware.ts:295-298`). Gerekçe yalnızca yorumdadır: karışık işaretleme kısmi akıştan güvenle kurulamaz. Bu bir ölçüm değil, tasarım varsayımıdır.

Sonuçlar (kodla gösterilebilenler):
- Araç turlarında kullanıcıya token akışı yoktur; tüm yanıt bitince metin/akıl yürütme/araç çağrıları tek seferde "akış" olarak yayımlanır (`replayAsStream`, 91-161). Çok adımlı araç döngüsünde her adım bir bütün olarak bekletilir.
- Zaman aşımı etkileşimi (çıkarım, test edilmedi): `providerDeadlines` bir dış katman olarak `doStream` çağırır ve ilk parça için 120 sn, sonraki parçalar için 60 sn bekler (`runtimeConfig.ts:129-145`, `providerDeadlines.ts:520, 554`). Araç turunda içerideki middleware tüm üretimi bitirmeden ilk parçayı yayımlamadığı için, ilk-parça zaman aşımı fiilen tek bir adımın TOPLAM üretim süresine bir üst sınır koyar. Düşük tüketim sınıfı bir GPU'da uzun bir 4B yanıtı için bu sınır aşılabilir; env ile 30 dakikaya kadar yükseltilebilir (`runtimeConfig.ts:134-138`, sınırlar 10 sn-30 dk). Bu sıralama `aiSdk.ts:499-505` (providerDeadlines'ın `config.model`'i sarması) ve `providers.ts:515-520` (config.model'in zaten tolerans middleware'li olması) ile çıkarılmıştır.
- `onActivity` (canlı göstergesi) yalnızca akış parçası geldiğinde tetiklenir (`providerDeadlines.ts:548-556`); akışsız adımda üretim süresince etkinlik sinyali yoktur.
- Araçsız son yanıt turu akışlıdır (299-300); yani akışlı kullanıcı deneyimi yalnızca "araç bildirilmemiş" çağrılarda vardır. Sohbet motoru araçları her turda bildirdiği için (`modules/chat/engine/streaming.ts:524-531`, `tools: activeTools`; sistem istemi tarafı ayrı rapora ait), yerel kayıtlı bir modelle bütün sohbet yolu akışsız olur (çıkarım).

### 6. Araç döngüsü, SDK'ya bırakılanlar ve sınırlar

- Döngü AI SDK'nın `streamText` + `stopWhen: stepCountIs(n)` yapısıdır; varsayılan `DEFAULT_MAX_ITERATIONS = 16` (`aiSdk.ts:53, 514`). Sohbet motoru da 16 verir (`streaming.ts:531-534`). Sınıra ulaşılınca SDK sessizce durur; Mike bunu kullanıcıya bildirir: çıktı sınırına çarpma ("length") ve "adım sınırı" için ayrı iki uyarı metni vardır (`aiSdk.ts:63-78`, kullanımı 631-635).
- Araç yürütme: SDK aynı adımdaki tüm araç çağrılarını eşzamanlı yürütür; Mike bunları mikro-görev sırasında toplayıp `runTools`'a tek parti olarak verir (`aiSdk.ts:244-294`). Sonuç eksikse veya parti reddedilirse sonraki model isteği başlamadan döngü iptal edilir (`aiSdk.ts:449-457`, test: `aiSdk.toolErrors.test.ts:290-330`).
- Bozuk argümanlar: SDK kendi tool-error'ını üretip döngüyü sürdürür ki model düzeltsin (`aiSdk.ts:596-606`). Akış sonu denetimi (`aiSdkFetch`) SSE içindeki `tool_calls` argüman parçalarını izler; akış temiz bitmeden kesilmişse ve argüman eksik/bozuksa araç çalışmadan hata fırlatır; temiz biterse bozuk argümanı olduğu gibi bırakır ki SDK kurtarsın (`aiSdk.ts:85-196`, özellikle 102-134). Proxy'nin kapattığı son SSE olayını görünür kılmak için sona iki satır sonu ekler (187).
- Metinden kurtarılan araç çağrısında bozuk girdi `parseToolInput` ile sessizce `{}` olur (`toolCallParsing.ts:143-156`) ve araç kendi doğrulamasını yapar.
- Tüm araç şemaları `jsonSchema` ile SDK'ya aktarılır; SDK tarafında şemaya göre doğrulama yapılır (`aiSdk.ts:302-338`). Çıktıyı kısıtlayan (grammar/json_schema/response_format) hiçbir kullanım yoktur: `response_format|json_schema|grammar|generateObject` için `backend/src` taramasında test dışı eşleşme çıkmadı (yalnızca "dilbilgisi" anlamında yorumlar).

### 7. Akıl yürütme (reasoning) yönetimi ve geri oynatma

- Seviyeler: `none, low, medium, high, xhigh, max` (`types.ts:296-305`). Model ailesine göre desteklenen alt kümeye en yakın seviyeye normalleştirilir (`models.ts:46-109`). Sohbet motoru varsayılan olarak `high` ister (`streaming.ts:535`); toplu işler boş bırakırsa "none" gider (`aiSdk.ts:522`, tip yorumu `types.ts:407-411`).
- Yerel/özel yolda hiçbiri uygulanmaz: kayıtlı, Ollama ve custom adaptörleri `supportsReasoning:false` olduğundan `reasoning` parametresi `undefined` verilir (`aiSdk.ts:516-525`, `providers.ts:522, 667, 466`). Yani Mike yerel modelde "düşünmeyi aç/kapat/bütçele" yapmaz; model ne üretirse (`<think>` veya `reasoning_content`) yalnızca ayrıştırılır. Düşünme bütçesi (ör. llama.cpp'de `--reasoning-budget`, şablon `enable_thinking`) tamamen sunucu tarafı ayardır; Mike isteğe `chat_template_kwargs` benzeri bir alan eklemez (taramada eşleşme çıkmadı).
- Sağlayıcı reddederse yedek: hata iletisinde "supported values are: 'a','b'" kalıbı varsa en yakın desteklenen seviye ile bir kez yeniden denenir (`providers.ts:687-696, 719-749`). Bu OpenAI'ye özgü hata biçimine bağlı kırılgan bir yöntemdir.
- Geri oynatma (replay): `replayReasoning:true` olan kayıtlı modelde, önceki asistan turlarının saklanan akıl yürütmesi `reasoning_content` olarak geri gönderilir (`aiSdk.ts:383-400`; test: `aiSdk.fetch.test.ts:218-226`). Gerekçe: Qwen3.6'nın `preserve_thinking` şablonu ile turlar arası tutarlılık (`docs/configured-models.md:116-121`, `types.ts:453-459`). Sınırlar: tur başına son 12.000 karakter, tüm geçmişte en çok 36.000 karakter, yeniden eskiye doğru; sığmayan tur ve daha eskileri yalnız metin olarak gider (`modules/chat/engine/contextBuilders.ts:266-273`, `docs/configured-models.md:150-152`). Tur eşleştirmesi görünür metin üzerinden yapılır, çünkü istemci geçmişi yalnızca metin olarak yollar; belirsiz veya düzenlenmiş mesaj metin olarak kalır (`contextBuilders.ts:275-330`, `docs/configured-models.md:136-142`). Akıl yürütme istemci gövdesinden hiç alınmaz, DB'den okunur (`docs/configured-models.md:141`). Tek tur içindeki araç adımları arasında akıl yürütme ayarından bağımsız olarak aktarılır (`docs/configured-models.md:154-155`; mekanizma SDK'dadır, bu raporda ayrıca doğrulanmadı).
- Akış olayları: `reasoning-start/delta/end` parçaları geri çağrılara ve SSE'ye `reasoning_delta` olarak aktarılır (`aiSdk.ts:572-583`; `streaming.ts:545-553`).

### 8. Zaman aşımları

- İki katmanlı canlılık sınırı: ilk parça için `STREAM_FIRST_CHUNK_TIMEOUT_MS` (varsayılan 120.000, sınır 10.000-1.800.000), sonraki her parça için `STREAM_CHUNK_TIMEOUT_MS` (60.000; 5.000-1.800.000) (`runtimeConfig.ts:129-145`). Zamanlayıcı yalnızca metin/akıl yürütme/araç-girdi/araç-çağrısı/dosya parçalarında yeniden kurulur (`providerDeadlines.ts:548-556`); bitiş/hata parçasında temizlenir.
- Süre dolunca `AbortController` ile HTTP istek iptal edilir ve kullanıcı iptalinden ayırt edilebilen bir `UserFacingError` ("... yanıt vermeyi bıraktı") üretilir (`providerDeadlines.ts:501-514`, `providerErrors.ts:56-74`, `aiSdk.ts:610-617`). Cevaplanmayan "gecikmeli çözülen" istekler iptal edilir (`providerDeadlines.ts:526-533`).
- Toplam tur/istek süresi veya araç yürütme süresi için burada ayrı bir zaman aşımı yoktur; araçların kendisi bu katmanın dışındadır (dosya başlığı: "SDK'nın araçlarını zamanlamadan", `providerDeadlines.ts:487`). Model kataloğu istekleri 15 sn'dir (`models.compatible.ts:62-65`), Ollama listesinde zaman aşımı belirtilmemiştir (`models.service.ts:262`).
- `maxRetries` kodda ayarlanmamıştır (grep: yalnızca Redis/BullMQ eşleşmeleri); yeniden deneme SDK varsayılanına bırakılmıştır (SDK varsayılanı tahmin: 2; bu pakette doğrulanmadı). Ayrıca 429 durumları `RetryError.lastError` içinden okunur (`providerErrors.ts:8-18`), bu SDK'nın yeniden denediğini dolaylı doğrular.

### 9. Token ve bağlam yönetimi: büyük ölçüde YOK

- LLM katmanında tokenizer, bağlam penceresi, `num_ctx`, token sayımı veya geçmişi kesme mantığı yoktur (`backend/src` içinde `contextWindow|context_window|num_ctx|tokenizer|countTokens` aramasında test dışı eşleşme çıkmadı). `chat.prepare.ts` içinde de açık bir geçmiş kırpma bulunamadı (aramada yalnız bir uzunluk kontrolü, satır 287, ayrı konu). Bu doğrulama kısmidir, tüm sohbet hazırlığı okunmadı.
- Tek çıktı sınırı `LLM_MAX_OUTPUT_TOKENS` ortam değişkenidir; ayarlı değilse sağlayıcının kendi sınırına bırakılır. OpenCode Go için 16.384 sabittir; Bedrock-Claude için model tablosundan tavan alınır (`aiSdk.ts:36-43`, `providers.ts:292-302`). Kısa tamamlamalarda (başlık gibi) akıl yürütme için 4.096 token pay eklenir (`aiSdk.ts:662-694`). Kayıtlı yerel modelde çıktı sınırı yoksa üretim sunucu varsayılanına kalır; bağlam taşması durumunda yerel sunucunun hatası düz hata olarak iletilir (sınıflandırma yok, bkz. 10).
- Önbellek ipuçları: OpenAI için `promptCacheKey`, Anthropic için son mesaja `cacheControl` kesme noktası (`aiSdk.ts:402-437`). Bunlar uzak sağlayıcılara özgüdür; llama.cpp'nin KV/prompt cache'i ya da `cache_prompt` kullanılmaz.
- Akıl yürütme geri oynatma bütçesi (12.000/36.000 karakter) bağlam yönetimine en yakın tek mekanizmadır ve karakter tabanlıdır, token tabanlı değildir.

### 10. Hata sınıflandırması

`toProviderStreamError` sırasıyla: (1) zaman aşımı/duraksama, (2) geçersiz API anahtarı, (3) erişim hatası (402 kredi, 403/404 model erişilemez, 429 kota veya "limit: 0" ile plan kapsamında değil), (4) diğerleri olduğu gibi (`providerErrors.ts:84-97`, `31-47`). Durum kodu `statusCode` veya `lastError` zinciri üzerinden bulunur (`providerErrors.ts:11-18`). Anahtar hatası: 401 her zaman anahtar; 400/403 yalnızca ileti/gövde metni anahtarı adlandırıyorsa (regex `apiKeyErrors.ts:131-132`, mantık 176-181). Kullanıcıya gösterilen ileti kendi metnimizdir, sağlayıcı metni güvenilmez sayılır ve yalnız sınıflandırmada kullanılır (`apiKeyErrors.ts:100-107`). Araç hatası ile model hatası ayrıştırılır; araç kaynaklı 401 kullanıcının LLM anahtarını suçlamaz (`aiSdk.ts:596-607, 638-646`). "Abort şeklinde" ama gerçekten kullanıcı iptali olmayan hatalar iptal gibi sessizce yutulmasın diye yeniden adlandırılır (`aiSdk.ts:458-470`). `onError` boş geçilir; hata yalnızca `fullStream` üzerinden tek yerde sınıflanır (528-532).
Yerel sunucu hataları (bağlantı reddedildi, bağlam aşımı, GBNF hatası) için özel sınıf yoktur; doğrudan düz `Error` olarak iletilir (kodda yerel için bir dal yok).

### 11. API anahtarı saklama

Kullanıcı anahtarları veritabanında AES-256-GCM ile şifrelenir (rastgele 12 bayt IV, kimlik doğrulama etiketi ayrı sütun); şifreleme anahtarı `USER_API_KEYS_ENCRYPTION_SECRET` ortam değişkeninden sabit bir tuzla scrypt ile türetilir ve süreç belleğinde önbelleğe alınır (`modules/user/user.apiKeyStore.ts:196-226`, satır şeması 71-73). Tuz sabit ve kod içindedir (`:196-198`), yani gizlilik tümüyle ortam sırrına dayanır. Sağlayıcı kapatma, anahtarı silmeden isteği ve ortam anahtarına düşmeyi engeller (`docs/direct-provider-models.md:17-25`, `registry.ts:104`). Kullanıcı anahtarı kullanılamaz durumdaysa (bölge/URL doğrulanamıyor) dağıtım anahtarına da düşülmez (`types.ts:349-355`). Kayıtlı modellerde anahtar sırası: JSON'daki düz `apiKey`, kullanıcının kayıtlı anahtarı (`apiKeyProvider`), `apiKeyEnv` (`registry.ts:100-114`); anahtar bildirilmemişse Authorization başlığı hiç gönderilmez (`providers.ts:496-497`). Ham akış günlükleri istemci içeriği taşıdığı için `NODE_ENV=production`'da sert biçimde kapalıdır (`rawStreamLog.ts:13-23`).

### 12. Doğrulama notları (önceki okumaya göre)

- Düzeltme: tolerans middleware'i "yerel model" için değil, yalnızca `MIKE_MODEL_CONFIG_JSON` ile kayıtlı ve (varsayılan olarak) `location:"local"` olan modeller içindir; Ollama ve BYOK `custom/` bunu almaz (`providers.ts:515-520, 655-668`).
- Doğrulandı: araç içeren tur akışsızdır ve akış olarak yeniden oynatılır; ekleme: bunun zaman aşımı ile etkileşimi (bölüm 5).
- Ek bulgu (kod incelemesiyle, çalıştırılarak doğrulanmadı): metinde satır başında `name:`, `tool:` veya `function:` ile başlayan bir satır varsa ön kontrol regex'i (`toolCallParsing.ts:176-181`) eşleşir, ama hiçbir açılış etiketi olmadığı için `bodies` boş kalır ve satır 261-265 "çalıştırılabilir araç tanımadı" hatasını fırlatır. Tolerans modundaki bir modelin sıradan cevabında böyle bir satır olması akışı hataya düşürebilir (yanlış pozitif). Özellikle tablo/liste biçimli hukuki çıktılarda risk (tahmin).
- Ek bulgu (çıkarım): `ThinkTagFilter` yalnızca metin içinde `<think>` açılışı arar (`toolCallParsing.ts:37`). Sohbet şablonu açılış etiketini istemin içine koyuyorsa (üretim yalnızca `</think>` ile başlar), düşünce metni görünür içeriğe sızar. Bu durumda sunucu tarafında `reasoning_content` ayrıştırması (llama.cpp `--reasoning-format`) kullanılmalıdır.
- Ek: `ask_inputs` duraklaması ve istemci araçları gibi uygulama mantığı bu bölümün dışındadır.

## HakHukuk için değerlendirme

### Taşınır

1. Tek, küçük sağlayıcı sözleşmesi: OpenAI biçimli araç şemaları + `runTools(calls) -> results` + olay geri çağrıları (`types.ts:307-344, 391-420`). Python'da aynı sözleşme (async generator veya olay kuyruğu) kolayca kurulur. Gerekçe: sağlayıcıdan bağımsız tek yüzey, tek-kullanıcılı yerel uygulamada çok-agent işi için yeterli.
2. Parti halinde araç yürütme (`aiSdk.ts:244-294`): aynı adımın çağrılarını bir araya toplamak, bizim eşzamanlı agent işlerinde SQLite yazma sırasını ve tek GPU kuyruğunu kontrol etmeyi kolaylaştırır.
3. Hata sınıflaması ve "iletiyi biz yazarız, sağlayıcı metni yalnız sınıflama içindir" ilkesi (`apiKeyErrors.ts:100-107`). Yerel için yeni sınıflar eklemek gerekir (bağlam aşımı, model yüklenmedi, GBNF reddi, sunucu meşgul).
4. Canlılık zaman aşımı mantığı (ilk parça + parça arası, iptal ve duraklama ile kullanıcı iptalinin ayrımı, `providerDeadlines.ts`, `providerErrors.ts:56-74`). 4B için ilk-parça sınırı yüksek (ön doldurma uzun bağlamda dakikalar sürebilir) ayarlanmalı; ayrıca üst bir toplam süre sınırı eklenmeli.
5. Adım sınırı + "neden durdu" bildirimi (`aiSdk.ts:63-78`). 4B için daha düşük sınır ve daha net bildirim gerekir.
6. Tur başına akıl yürütme saklama ve sınırlı geri oynatma fikri (12.000/36.000 karakter, yeniden eskiye, `contextBuilders.ts:266-330`). Qwen3.5 gibi tabanlar için doğrudan geçerli; ama sınırı karakterden token'a çevirmek gerekir.
7. Akış sonu bütünlük denetimi (`aiSdk.ts:85-196`): yarım kalan araç argümanıyla aracı hiç çalıştırmama ilkesi yerel sunucuda da (bağlantı kopması, OOM) aynen gerekir.
8. Hesap-modeli kimliği doğrulaması gibi girdi sertleştirme yaklaşımı, özellikle kimliklerin URL'ye girdiği durumlar için; yerelde daha az kritik.
9. Düzeltici ayrıştırma yardımcıları (kod çiti sökme, dengeli JSON kesme, `jsonrepair` benzeri onarım, skaler türleme): bir "son çare" olarak değerli (`toolCallParsing.ts:405-466`), ama birincil yol olmamalı (aşağıya bakın).

### Yeniden tasarlanmalı

1. Araç çağrısı kurtarmayı birincil yol yapmak yerine kısıtlı kod çözmeyle ÖNLEMEK. Mike'ın tasarımı "model serbest metin üretir, biz sonradan çözeriz"dir; bunu yalnızca 7+ ayrı dialect ve onarımla taşır. HakHukuk'un hedef sunucuları (llama.cpp, vLLM, SGLang) araç çağrısını GBNF/json_schema ile zorunlu yapıya bağlayabilir; bu durumda ayrıştırma sorunu yapısal olarak ortadan kalkar ("hatayı tip düzeyinde yok et"). Mike'da bunun hiçbir izi yok (bölüm 6, son madde). Tolerans katmanı yalnızca yedek (ikinci savunma) olarak kalmalı.
2. Araç turlarını akışsız yapma kararı. Yerel 4B'de kullanıcı deneyimi ve zaman aşımı açısından zararlı (bölüm 5). Kısıtlı kod çözme ile araç çağrısı JSON'u tam şemaya uyduğunda, akış güvenle sürdürülebilir: sunucu `tool_calls` delta'larını verir veya biz yalnızca çağrı bloğunu arabelleğe alırız. Öneri: akışı varsayılan yap, gerekirse yalnızca bozuk çağrı için akışsız yeniden dene.
3. Bağlam ve token yönetimi sıfırdan tasarlanmalı. Mike'da yok; 4B için en kritik eksik (küçük bağlam, uzun mevzuat parçaları). Gerekenler: sunucudan gerçek bağlam uzunluğunu okuma (llama.cpp `/props`), model tokenizer'ı ile sayım (llama.cpp `/tokenize`), araç sonuçlarını kırpma/özetleme bütçesi, geçmiş sıkıştırma, çıktı için rezerv. Bunlar sağlayıcı katmanının sorumluluğu olmalı.
4. Zaman aşımı: yerel çıkarım için ön doldurma (prefill) ile üretim aşamaları ayrı izlenmeli; akışsız adım varsa süre sınırı üretim uzunluğuna göre ölçeklenmeli. Mike'ın sabit 120/60 sn varsayılanları bulut gecikmesine göre seçilmiş.
5. Akıl yürütme denetimi: Mike yerelde düşünmeyi hiç kontrol etmez. 4B için "düşünme aç/kapa/bütçe" birinci sınıf bir parametre olmalı (sunucuya `chat_template_kwargs`/akıl yürütme bütçesi bayrağı ile). Ölçüm hattımızdaki 1024 düşünme + 512 cevap bütçesi bu arayüzde karşılığını bulmalı (bütçeli zorla kapatma sunucuda değil, katmanımızda ya da sunucu bayrağıyla).
6. `<think>` ayrıştırması: yalnızca "metin içi" etiket varsayımı kırılgan. Birincil yol sunucudan ayrı `reasoning_content` almak; metin içi süzgeç, açılış etiketi şablonda olan durum için "başlangıçta düşünme içindeyim" modunu da desteklemeli.
7. Kayıt yapısı: Mike'ta tek ortam değişkeni içinde JSON; ayrıca ayrı Ollama, custom, configured yolları ile özellikler tutarsız dağılmış (tolerans yalnızca birinde). Bizim tasarımda tek "uç nokta profili" tipi (taban URL, sunucu türü, model adı, yetenek bayrakları, bağlam uzunluğu, kısıtlı kod çözme desteği) ve veritabanında/yapılandırma dosyasında saklama daha temiz olur. Tek kullanıcılı olduğumuz için anahtar şifrelemesi (AES-GCM + sabit tuz) gerekmeyebilir; yerel sunucu çoğunlukla anahtarsızdır, bulut yedekleri için işletim sistemi anahtar zinciri yeterli olabilir.
8. Hata sınıfları: yerel sunucu hataları (bağlantı reddedildi, modelin yüklenmesi sürüyor, bağlam aşımı, GBNF ayrıştırma hatası, KV önbellek dolu) ayrı, kullanıcıya eyleme dönük ileti ile sınıflanmalı.
9. Çok-agent eşzamanlılığı: Mike'da ayrı bir model yürütme kuyruğu bu katmanda görülmedi. Bizde tek yerel çıkarım sunucusuna paralel işler geleceği için sağlayıcı katmanı kuyruk, öncelik ve slot (llama.cpp `-np`) farkındalığına sahip olmalı. Bu, Mike'a göre yeni gereksinimdir.
10. Çoklu benzer çağrıyı tek toplu çağrıya katlama deseni (`collapseTrademarkOwnerCalls`): genel bir "araç argümanı toplulaştırma" kuralı olarak yeniden tasarlanabilir (ör. aynı arama aracına N kez çağrı yerine liste argümanı); yalnızca marka alanına sabitlenmiş hâli taşınmaz.

### Taşınmaz

1. 15 sağlayıcı fabrikası (Bedrock, Azure, Foundry, Vertex, xAI, OpenRouter, Vercel, OpenCode Go...) ve bunlara bağlı model kimliği/protokol çıkarımı, önbellek ipuçları, `max` akıl yürütme düzeltmeleri (`providers.ts:152-669`, `models.ts`). Hukuk verisini yerelde tutma amacıyla çelişir; yalnızca ihtiyaç varsa tek bir OpenAI-uyumlu bulut yedeği kalmalı.
2. Bulut modeli odaklı model kataloğu, fiyatlandırma ve sağlayıcı kataloğu listeleme (`models.service.ts`, `models.compatible.ts`).
3. BYOK doğrulama paketi ve https/özel adres engelleme (`packages/byok-validation`, `cloudProviders.ts:214-243`, `guardedFetch`): çok kiracılı/SSRF modeli içindir; tek kullanıcılı yerel uygulamada uç noktamız localhost olacaktır. (SSRF yalnızca uzak ek uç nokta eklenirse anlamlı.)
4. Çoklu kiracı anahtar şifreleme/organizasyon/devre dışı bırakma mantığı (`user.apiKeyStore.ts`, `UserApiKeys.disabledProviders` vb.).
5. Marka izleme (`tm_search_trademarks`) dalı ve hata iletilerindeki "Trademark Monitor" yönlendirmesi.
6. Komite (çoklu model sentezi) iskeleti: zaten çalıştırıcısı görülmedi ve 4B için maliyet/gecikme açısından uygun değil.
7. `fallbackReasoningLevelFromProviderError` (OpenAI hata metni ayrıştırma, `providers.ts:719-749`).

### Sağlayıcı katmanı arayüz önerisi (llama.cpp ve vLLM/SGLang)

Genel ilke: tek bir OpenAI-uyumlu uç nokta (`/v1/chat/completions`) + küçük bir "yetenek profili". Sunucuya özgü farklar (GBNF, `guided_json`, bağlam uzunluğu sorgusu) profil içinde saklanır, üst katmanlar bunları görmez.

**Python arayüzü (Protocol, ABC değil):**

```
class LlmEndpoint(Protocol):
    profile: EndpointProfile
    async def chat(self, req: ChatRequest) -> AsyncIterator[ChatEvent]: ...
    async def count_tokens(self, messages, tools) -> int: ...
    async def health(self) -> ServerState: ...   # yüklü model, bağlam uzunluğu, boş slot
```

`ChatEvent` ayrık birleşimdir: `ReasoningDelta | TextDelta | ToolCall(id,name,args:dict) | Finish(reason, usage) | Failure(kind, message)`. Tüm hata sınıfları `Failure.kind` sayımıyla (ör. `ContextOverflow, ServerBusy, ModelNotLoaded, GrammarRejected, Timeout, Cancelled, Network`) sunulur; çağıran istisna ayrıştırmaz.

**EndpointProfile (yapılandırma, kodda varsayılan yok; baz model parametredir):**
`base_url`, `server` (`llama_cpp|vllm|sglang|generic`), `model`, `context_tokens` (sunucudan okunur, yoksa zorunlu), `max_output_tokens`, `supports_tool_choice`, `constraint_mode` (`gbnf|json_schema|guided_json|none`), `reasoning_mode` (`separate_field|inline_think|none`), `thinking_budget` (düşünme token sınırı, 0 = kapalı), `slots` (eşzamanlı istek sayısı), `timeouts` (bağlantı, ilk token, token arası, toplam).

**ChatRequest:** `messages`, `tools` (araç şemaları), `tool_policy` (`required|auto|none`), `output_schema` (isteğe bağlı JSON şeması), `reasoning: Off | Budget(n)`, `max_tokens`, `seed` (ölçüm hattıyla uyumlu, 3407), `cancel` (iptal belirteci). Bayrak parametreleri yerine tür kullanılmalı (Mode enum / sum type).

**Kısıtlı kod çözme eşlemesi (sunucu başına, profilin içinde):**
- Araç çağrısı veya yapılandırılmış çıktı için tek kaynak JSON Schema. Katman, şemadan sunucuya göre şu biçimi üretir: llama.cpp için `response_format: {type:"json_schema", json_schema:{...}}` veya `grammar` (GBNF; şemadan GBNF dönüşümü sunucuda mevcut), vLLM için `guided_json`/`response_format` (yapılandırılmış çıktı arka ucu), SGLang için `json_schema`/`regex`/`ebnf` parametreleri. İstek alan adları sürüme göre değişir; bu yüzden alan adlarını katmanın içinde tek bir "dialect tablosu"nda tutmak ve profilde sürüm sınaması yapmak gerekir (burada alan adlarını kesin varsaymıyoruz; hedef sürümler kurulumda doğrulanmalı, tahmin).
- Araç seçimi için iki aşama modeli: (1) hangi araç (kapalı küme, `enum`), (2) o aracın argüman şeması. Küçük model için tek geniş `anyOf` şemasından daha dayanıklıdır (tahmin; ölçülmeli).
- Düşünme ve kısıtlama birlikte: önce serbest düşünme (bütçeli), `</think>` zorla kapatma, sonra kısıtlı cevap/araç çağrısı. Bütçeli zorla kapatma bizim ölçüm rejimimizle (1024 düşünme + 512 cevap) aynı davranışı sağlamalı; "ürün yolu ölçüm yoluna eşit olmalı" ilkesi bu arayüzün testi olmalı.
- Kısıt açıkken akış: şema uyumlu olduğundan `tool_calls` delta'ları güvenle işlenir; yalnızca bütünlük denetimi (Mike'ın `aiSdkFetch` fikri) sürdürülür.

**Savunma katmanları (Mike'ın tolerans katmanını yedek olarak koruma):**
1. Birincil: kısıtlı kod çözme (şema zorunlu).
2. İkincil: sunucunun yapısal `tool_calls` ve ayrı `reasoning_content` alanlarını kullan.
3. Üçüncül (yalnızca `constraint_mode=none` sunucuda): metinden kurtarma. Mike'dan fikir olarak alınabilecekler: dengeli JSON kesme, kod çiti sökme, tolerant JSON onarımı, skaler türleme, kesinleştirilmiş yanlış pozitif koruması (yalnızca bildirilmiş araç adları kabul edilir; satır başı `name:` gibi serbest kalıplar kullanılmaz). Kurtarma başarısızsa tüm akışı kesmek yerine modele bir düzeltme turu (hata iletisi) verilir ve sınırlı sayıda yeniden denenir.

**Bağlam ve bütçe (Mike'da olmayan, bizde zorunlu):** `count_tokens` ile istek göndermeden önce `istem + araç şemaları + geçmiş + rezerv çıktı <= context_tokens` denetlenir; aşılırsa kırpma politikası çağıran tarafın verdiği bir stratejiye devredilir (araç sonucu kırpma, geçmiş özetleme). Sunucu `ContextOverflow` döndürürse aynı sınıf hata yeniden yüzeye çıkar.

**Eşzamanlılık:** katman, profildeki `slots` kadar eşzamanlı akışa izin veren bir semafor ve öncelik kuyruğu içerir (etkileşimli sohbet > arka plan agent işi). llama.cpp'de `-np`/slot, vLLM/SGLang'de sürekli gruplama bunu doğal destekler; bizim yerelde ise tek GPU olduğundan kuyruk uygulama düzeyinde şarttır.

**Test yaklaşımı (Mike'ın test setinden alınacak fikir):** her sunucu için aynı sözleşme testleri: iptal, duraklama, yarım kalmış araç argümanı, bağlam taşması, bozuk şema. Mike'ın tolerans testleri (düşünce ayrımı, bölünmüş etiketler, çift kopya araç, bozuk JSON) birincil yol değil yedek yol için uyarlanabilir.

## Açık sorular

1. Qwen3.5-4B için hedef sunucu sürümlerinde tam hangi alan adları geçerli (llama.cpp `response_format`/`grammar`/`json_schema`, vLLM yapılandırılmış çıktı parametreleri, SGLang kısıtlama alanları) ve araç çağrısı ile birlikte kullanımı destekleniyor mu? Kurulumda denenmeli.
2. Kısıtlı kod çözme, düşünme kanalıyla (`<think>` serbest, ardından kısıtlı çıktı) aynı istekte nasıl birleşir; şablon `enable_thinking` + zorla kapatma + grammar sırası sunucularda desteklenir mi?
3. Araç turlarını akışlı yapmanın dayanıklılığı: Mike'ın "akışsız" kararı bir ölçüme mi dayanıyordu? Belgede ölçüm yok; belirli modellerle (Qwen, DeepSeek, GLM) deneyim notu gibi görünüyor. Bizim 4B kısıtlı çözümlemede bu sorunun yok olduğunu ölçmek gerekir.
4. Komite/çok-model sentezi çalıştırıcısı gerçekten yok mu yoksa bu taramanın kapsamı dışında başka dizinde mi? (Kapsam dışı; `backend/src` test dışı grep bulamadı.)
5. SDK varsayılan `maxRetries` değeri ve davranışı bu sürümde (`ai` ^7) tam olarak nedir; yerel sunucu için yeniden deneme politikasını nereye koyacağız (öneri: sağlayıcı katmanında, sınıflandırılmış hatalara göre).
6. `ThinkTagFilter` sızıntı senaryosu (açılış etiketi şablonda) ile `name:`/`tool:` satırı yanlış pozitifi gerçek modellerde ve gerçek hukuki çıktılarla yeniden üretilebiliyor mu? Burada çalıştırılmadı.
7. Replay sınırlarının (12.000/36.000 karakter) gerekçesi bir ölçüme mi dayanıyor? Belgede yok (tahmin: sezgisel).

## Okunmadı

- `backend/src/lib/llm/cloudProviders.ts` baştan sona (yalnızca özel uç nokta fonksiyonları okundu), `vertexAuth.ts`, `rawStreamLog.ts` 60. satırdan sonrası, tüm `*.test.ts` dosyalarının gövdeleri (yalnızca test adları ve birkaç örnek).
- `backend/src/modules/models/models.bedrock.ts`, `models.routes.ts` gövdesi (yalnızca imza taraması).
- `docs/direct-provider-models.md` 60. satırdan sonrası (Bedrock/Azure/Foundry/Vertex kurulumu).
- `packages/byok-validation/cases.json` 40. satırdan sonrası.
- `backend/src/modules/user/user.apiKeyStore.ts` yalnızca şifreleme bölümü; satır okuma/yazma, RLS, `getEffectiveApiKeys` ve `user.service.ts`.
- Sohbet motorunun geri kalanı (`chat.prepare.ts`, `streaming.ts` 560 sonrası, araç dağıtıcısı, sistem istemleri), `memory.curator.ts` ve `tabular.extract.ts`'in model çağrıları; geçmişin kırpılıp kırpılmadığı bu nedenle kesin değil.
- `ai`, `@ai-sdk/openai-compatible` paket kaynakları (SDK'nın `reasoning_content` işleme, `maxRetries` varsayılanı ve araç-girdi doğrulaması yalnızca Mike kodu ve testlerinden çıkarıldı).
- Frontend model seçici, `frontend/`, `desktop/`, `word-addin/`, `e2e/`, `loadtest/` (bu bölümün kapsamı dışı).
