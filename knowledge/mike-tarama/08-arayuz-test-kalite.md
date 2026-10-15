# Mike: arayüz, test ve kalite disiplini

Bu not, açık kaynak hukuk yapay zekâ uygulaması Mike'ın (TypeScript, AGPL-3.0) ön yüzünü, test piramidini ve olay kayıtlarını inceler. Amaç, HakHukuk için tasarlanan tek kullanıcılı yerel uygulamada nelerin alınabileceğini belirlemektir. Kod kopyalanmamış, tasarım kendi cümlelerimle anlatılmıştır. Tüm yollar `mike-main/` köküne görecelidir ve `yol:satır` biçimindedir.

## Kapsam ve okunan dosyalar

Bütünüyle veya büyük bölümüyle okunanlar:

- `AGENTS.md` (270 satır), `CONTRIBUTING.md` (127), `docs/design-system.md` (528), `docs/frontend-testing.md` (235), `docs/test-depth.md` (183), `docs/testing-coverage.md` (141), `docs/e2e-ci.md` (215), `docs/backend-architecture.md` (355).
- `docs/incidents/` altındaki iki dosyanın ikisi de.
- `loadtest/sse-stream.js` (ilk 140 satır), `playwright.config.ts` (105 satır), `e2e/critical-path.spec.ts`, `e2e/anthropic-stub.mjs` (ilk 40 satır), `e2e/assistant-streaming.spec.ts` (ilk 60 satır).
- `packages/contracts/README.md` ve `packages/contracts/index.d.ts` (ilk 75 satır, 195-216 ve 295-395. satırlar).
- Ön yüz: `frontend/package.json`, `frontend/next.config.ts` (ilk 60 satır), `frontend/Dockerfile` (ilk 50 satır), `frontend/vitest.config.mts` (ilk 70 satır), `frontend/src/app/lib/sse.ts` (tamamı), `lib/assistantTurnStream.ts` (1-470 ve 1240-1343), `lib/assistantTurns.ts` (1-200), `hooks/useAssistantChat.ts` (1-140), `lib/mikeApi.ts` (yalnızca akış fonksiyonları, 2770-2810), `components/assistant/EditCard.tsx` (tamamı), `components/assistant/message/citationVerification.tsx` (tamamı), `components/assistant/message/citationUtils.ts` ve `MarkdownContent.tsx` (ilk 50-60 satır), `components/tabular/TabularReviewView.tsx` (595-700), `components/tabular/columnPresets.ts` (ilk 50), `components/shared/types.ts` (380-460, 684-755), `(pages)/layout.tsx` (ilk 60), `components/shared/AppSidebar.tsx` (66-84), `(pages)/ide/page.tsx` (ilk 40), `contexts/WorkspaceContext.tsx` (ilk 60), `contexts/AuthContext.tsx` (ilk 60), `hooks/useSelectedModel.ts` (ilk 60), `shared/lib/modelCatalog.ts` (ilk 60).
- `docs/superpowers/specs/2026-06-29-legal-workflows-design.md` (ilk 120 satır), `word-addin/README.md` (ilk 80 satır), `word-addin/package.json` (ilk 60 satır), `docs/docx-preview-engines.md` (ilk 40 satır).
- Dizin listeleri: `frontend/src/app/**` (rota ve bileşen envanteri), `e2e/`, `word-addin/e2e/`, `packages/`, kökteki yapılandırma dosyaları.

Not: `docs/` altında ayrıca `docs/superpowers/` yalnızca `specs/` alt dizinini içerir; `plans/` dizini yoktur (dizin listesi, `docs/superpowers`).

## Nasıl çalışıyor

### 1. Depo yapısı ve monorepo araçları

- Depo üç uygulama içerir: `frontend/` (Next.js), `backend/` (Express) ve `word-addin/` (Word görev paneli). Kökteki `e2e/` dizini web uygulamasının Playwright testlerini barındırır (`AGENTS.md:9-16`).
- Ayrıca `packages/` altında üç küçük paket vardır: `byok-validation`, `contracts`, `pdf-text-order` (dizin listesi). `desktop/` Electron sarmalayıcıdır (`frontend/next.config.ts:6-12`: standalone çıktı masaüstü uygulaması içindir).
- Kök `package.json` yalnızca Playwright betiklerini ve geliştirme bağımlılıklarını tanımlar; `workspaces` alanı yoktur (`package.json:1-24`). Kökte `pnpm-workspace.yaml`, `turbo.json`, `lerna.json` veya `nx.json` bulunmadı (kök dizin listesi ve `find` çıktısı boş). Üç uygulama ve `desktop/` kendi `package-lock.json` dosyasını taşır (kök listeleme; `AGENTS.md:249-251`: bağımlılık değişince "etkilenen paketin" lock dosyası güncellenir).
- Komutlar `npm run ... --prefix <dizin>` biçiminde çalıştırılır (`AGENTS.md:207-226`). Paketler arası paylaşım yalnızca tip düzeyindedir: `@mike/contracts` bir `.d.ts` dosyasıdır; çalışma zamanı bağımlılığı ve derleme çıktısı yoktur, her uygulama TypeScript `paths` ile aynı dosyaya çözümler (`packages/contracts/README.md:3-5`). Docker bağlamı depo köküdür; ön yüz imajı yalnızca `packages/contracts` dizinini ek olarak kopyalar (`frontend/Dockerfile:1-17,22-23`). Bu kuralı bir mimari test denetler (`AGENTS.md:100-105`; `frontend/Dockerfile:9-11`).
- Sonuç: Mike bir "npm klasör çoklu deposu"dur; görev önbelleği veya paralel görev orkestrasyonu aracı kullanmaz.

### 2. Ön yüz yığını

`frontend/package.json:21-82` bağımlılıklarından:

- Çatı: Next.js `^16.4.0`, React `19.3.0`, React Compiler (`babel-plugin-react-compiler`, ve `next.config.ts:13` `reactCompiler: true`). Uygulama App Router kullanır (`frontend/src/app/(pages)/...`).
- Stil: Tailwind v4 + shadcn `new-york` ilkelleri + Radix (`dropdown-menu`, `popover`) + `lucide-react` + `clsx` + `tailwind-merge` (`docs/design-system.md:3-4`; `package.json:29-31,44,39,56`).
- Belge görüntüleme: DOCX için `@docx-editor.dev/*` (EigenPal) 2.27.0; elektronik tablo için `@fortune-sheet/*` 1.0.4 ve `luckyexcel`, `exceljs`; PDF için `pdfjs-dist` 6.4.299 (`package.json:23-27,40,42,48`). Fortune-sheet sürümü bilinçli olarak sabitlenmiştir, çünkü görüntüleyici iç DOM kaydırma uzantılarını değiştirmektedir (`docs/frontend-testing.md:21-24`).
- Metin: `react-markdown`, `remark-gfm`, `remark-math`, `rehype-katex`, `katex`, `marked`, `dompurify`; zengin düzenleyici olarak TipTap (`package.json:33-37,41,45-46,51-53`).
- Hata izleme: `@sentry/nextjs` (`package.json:32`).
- Dağıtım: Cloudflare için `@opennextjs/cloudflare` betikleri (`package.json:16-18`); Docker imajı ise `node:22-slim` üzerinde `npm start` çalıştırır (`frontend/Dockerfile:12,49`).
- Katalog: Ladle ile bileşen kataloğu (`package.json:11-13`; `docs/design-system.md:496-524`).
- Eksik olanlar: Redux, Zustand, SWR veya React Query bağımlılığı yoktur (`frontend/package.json:21-82`).

Sürüm numaralarının bir kısmı (ör. Next 16, React 19.3, Vitest 5, TypeScript 7) benim bilgi birikimimin ötesindedir; dosyadan olduğu gibi aktarılmıştır, doğrulamadım.

### 3. Rotalar ve ekran envanteri

`frontend/src/app/` altındaki `page.tsx` dosyalarından (komutla listelendi):

- Kimlik: `/login`, `/login/sso`, `/signup`, `/signup/check-email`, `/forgot-password`, `/reset-password`, `/verify-mfa`, `/auth/callback`, `/onboarding/{profile,practice,invitations}`, `/support`.
- Ana kabuk (`(pages)` grubu): `/assistant` ve `/assistant/chat/[id]`; `/ide`; `/projects`, `/projects/[id]` (alt rotalar: `assistant`, `assistant/chat/[chatId]`, `folders/[folderId]`, `tabular-reviews`, `tabular-reviews/[reviewId]`); `/library` (alt rotalar: `files`, `folders/[folderId]`, `templates`, `templates/presets` ve klasör altı varyantlar); `/tabular-reviews` ve `/tabular-reviews/[id]`; `/workflows` (alt rotalar: `assistant/[id]`, `tabular-review/[id]`, `addons`, `addons/packs/[packKey]`); `/history` (yalnızca `/settings/my-activity` adresine yönlendirir, `(pages)/history/page.tsx:1-5`); `/organizations` ve `[id]` ile ayarları (üyeler, denetim kaydı, sağlayıcılar, gizlilik, özel içerik).
- Ayarlar: `/settings/{appearance, byok, connectors, features, memory, models, my-activity, organizations, personalisation, privacy-data, security}`.
- Kenar çubuğu gezinmesi altı öğedir: Assistant, IDE, Projects, Library, Tabular Review, Workflows (`components/shared/AppSidebar.tsx:70-81`). Yenilenen ayrı bir API proxy rotası vardır: `app/api/[...path]/route.ts`, tarayıcıdan gelen `/api/*` isteklerini `API_BASE_URL` ile belirtilen arka uca iletir, gövdeyi akış olarak aktarır (`route.ts:11-17,39-52`).

Mike'ın ayrıca "IDE" ekranı vardır: bir proje seçildikten sonra proje sohbetine açılan, belge görüntüleyici + sohbet + gezgin çok panelli çalışma alanı (`(pages)/ide/page.tsx:17-26`; `docs/design-system.md:244-259`).

### 4. Durum yönetimi

- Genel durum, React Context'lerle taşınır: `AuthContext`, `UserProfileContext`, `WorkspaceContext`, `ChatHistoryContext`, `SidebarContext`, `PageChromeContext` (`contexts/` dizin listesi). Kök sağlayıcı sırası: Auth, UserProfile, MFA kapısı, onboarding kapısı, toast (`components/providers.tsx:12-27`).
- Kimlik doğrulama tarayıcı depolamasında token tutmaz; oturum arka uç tarafından yönetilen HttpOnly çerezdir, ön yüz `getAuthSession` ile oturumu sorgular (`word-addin/README.md:6-8`; `contexts/AuthContext.tsx:13-20`). Birden çok sekme arasında oturum durumu `BroadcastChannel` ve `localStorage` anahtarıyla eşitlenir (`AuthContext.tsx:41-52`).
- "Çalışma alanı" kavramı (kişisel veya kurum) yalnızca listeleri süzer; yetki vermez, sunucu her istekte üyeliği yeniden doğrular (`WorkspaceContext.tsx:3-10`). Seçim `localStorage` anahtarı `mike.activeWorkspace.` ile saklanır (`WorkspaceContext.tsx:28`).
- Sunucu verisi için önbellek kütüphanesi yok; veri `mikeApi.ts` fonksiyonlarıyla çekilir, sayfalama `usePaginated*` kancalarıyla yapılır (`hooks/` listesi). `mikeApi.ts` tek dosyada 3871 satırdır (`wc -l`). AGENTS.md, backend çağrılarının yalnızca bu dosyada toplanmasını şart koşar (`AGENTS.md:95-97`).
- Uçuş halindeki sohbet turları, React dışı bir "tur kaydı"nda (modül düzeyinde `Map`) tutulur ve `useSyncExternalStore` ile bileşenlere bağlanır (`lib/assistantTurns.ts:1-20,52-53`; `hooks/useAssistantChat.ts:98-103`). Amaç: sayfa veya kanca değişse bile yanıtın tek bir yerde yaşaması.
- Kenar çubuğu açık/kapalı tercihi `localStorage` içinde tutulur (`(pages)/layout.tsx:44-49`). Kanca düzeyinde yan etki yönetimi için "yerel kalıcı durum" kancası da vardır (`hooks/useRemountPersistentState.ts`, yalnızca adı görüldü).

### 5. Akış (SSE) tüketimi ve yeniden bağlanma

Bu, incelenen bölümün en değerli parçasıdır.

**Çerçeveleme katmanı (`lib/sse.ts`).**
- Arka uç `data: <json>\n\n` kayıtları yollar; ağ parçaları kayıt sınırına denk gelmeyebilir. Okuyucu kısmi satırları tamponlar, gövde bittiğinde kod çözücüyü boşaltır ve kalan tamponu da ayrıştırır; el yazması döngülerin son kaydı kaybettiği not edilmiştir (`sse.ts:1-10,82-93`).
- Hatalı JSON uyarıyla atlanır, akış sürer (`sse.ts:114-123`). `id:` satırı kendinden sonraki kayda aittir ve çağırana bildirilir (`sse.ts:75-76,98-101,124`).
- `data: [DONE]` sonlandırıcıdır. Sonrasında okuyucu iptal edilmez, EOF'a kadar (2 saniye bütçeyle) boşaltılır; çünkü iptal, tarayıcıda normal biten isteği `net::ERR_ABORTED` olarak kaydettirir ve izleme gürültüsü yaratır (`sse.ts:22-31,131-138`). Yorum satırları (`: ...`) `data:` ile başlamadığı için sessizce atlanır (`sse.ts:102`); sunucudaki `: tool-wait` canlı tutma satırları bu sayede ön yüzü etkilemez (`docs/backend-architecture.md:55-58`).

**Sunucu sahipli çalıştırma (run) modeli.**
- Üretim, HTTP yanıtına değil sunucuya aittir: bir "run" kaydı çerçeve tamponunu tutar; istek kapanırsa yalnızca ayrılma olur, üretim sürer. Her çerçevenin `id:` satırında sıra numarası vardır; istemci yeniden bağlanırken `from=<son id + 1>` ister (`docs/backend-architecture.md:41-53`).
- Uç noktalar: `GET /chat/:chatId/turn/:turnId/stream?from=<seq>`, `POST .../stop`, `GET /chat/:chatId` yanıtında `active_turn`; aynı sohbette ikinci POST `409 turn_in_progress` döner (`backend-architecture.md:62-82`). Biten run 60 sn saklanır, beş dakika ilerleme olmazsa veya dört saat dolarsa durdurulur; çalıştırmalar süreç belleğindedir ve yeniden bağlanma aynı kopyaya ulaşmalıdır (`backend-architecture.md:167-177`).
- Ön yüz tarafı: `streamChatTurn` bu GET'i `Accept: text/event-stream` ile çağırır (`lib/mikeApi.ts:2777-2789`); `stopChatTurn` durdurmanın tek yoludur, akışı kapatmak yalnızca bu istemciyi ayırır (`mikeApi.ts:2791-2800`).

**Yeniden bağlanma döngüsü (`readAssistantTurn`).**
- İlk yanıt `open()` ile alınır (POST veya devam GET'i). Bağlantı koparsa ve `chatId`, `turnId` biliniyorsa, en fazla 2 kez (varsayılan) `400 ms × (deneme+1)` bekleyip son görülen çerçeveden sonrasını ister. Durdurma (abort) asla yeniden denenmez; sunucunun artık tanımadığı tur (saklama süresi dolmuş 404) özgün hatayı yüzeye çıkarır (`lib/assistantTurnStream.ts:1275-1343`).
- Sayfa yenilenirse de aynı yol işler: yeni sayfa ham `GET` ile turu `id` ile yakalar, ayrı bir istek gerekmez (`assistantTurnStream.ts:10-26`; `docs/frontend-testing.md:199-201`).
- Sohbet isteği akıştan önce reddedilirse hata sınıflanabilsin diye durum kodu, `code` ve `request_id` taşıyan bir Error üretilir; 5xx'te kullanıcıya ham ayrıntı gösterilmez (`assistantTurnStream.ts:51-93`).

**Olay biçimi.** Tüketici çerçeveleri `type` alanına göre ayırır (`assistantTurnStream.ts` içindeki `data.type ===` satırları). Gözlenen türler: `chat_id` (373. satır; sohbet, tur ve asistan mesajı kimlikleri), `cancelled` (386), `chat_title` (394), `content_done` (402), `error` (407), `content_delta` (442), `reasoning_delta` (489), `reasoning_block_end` (526), `tool_call_start` (547), `workflow_applied` (562), `case_citation` (571), `case_opinions` (602), `mcp_tool_start`/`mcp_tool_result` (616/629), CourtListener için altı çift `*_start`/sonuç olayı (668-868), `doc_read_start`/`doc_read` (894/1024), `ask_inputs` (915), `doc_find_start`/`doc_find` (1057/1080), `doc_created`, `doc_download`, `doc_replicated`, `doc_edited` ve başlangıç karşılıkları (1118-1224), `citations` (1254). Tablo incelemesinde ayrı bir şema vardır: `cell_update` ve `error` (`components/tabular/TabularReviewView.tsx:615,628`).
- Seri hale getirilen yük tipleri `packages/contracts/index.d.ts` içinde yazılıdır (`AssistantEvent` birleşimi: 297-393); "akış göstergesi, React anahtarı" gibi istemci durumu bilinçli olarak sözleşmenin dışında tutulur (`packages/contracts/README.md:7-12`).

**Olay kapasitesi.**
- `content_delta` gelince bekleyen "Thinking" yer tutucuları kaldırılır, akan akıl yürütme bloğu kapatılır ve yeni bir akan içerik bloğu açılır; araya araç veya akıl yürütme olayı girerse içerik doğal olarak parçalara bölünür (`assistantTurnStream.ts:442-470`, `206-223`). Araç başlangıç ve düşünme göstergeleri, gerçek olay gelene kadar "takılmış" izlenimi vermesin diye geçici yer tutuculardır (`assistantTurnStream.ts:239-243`).
- İptalde "Cancelled by user." etiketi yalnızca bir kez eklenir; sunucu da kısmi yanıtı aynı etiketle saklar (`assistantTurnStream.ts:255-266,386-392`).
- `error` çerçevesi `safe_to_display` bayrağı taşır; yalnızca bu bayrak açıksa sunucu mesajı gösterilir, aksi halde genel bir cümle çıkar (`assistantTurnStream.ts:99-104,407-441`). `code === "invalid_api_key"` ayrı bir "anahtarını düzelt" sinyalidir (`assistantTurnStream.ts:416-419`).
- `citations` çerçevesinin durumu `started`, `partial` veya `final` olabilir; yalnızca `final` akışın bittiği sinyali sayılır (`assistantTurnStream.ts:1254-1288`).

### 6. Sohbet arayüzü

- Ana bileşenler: `ChatView` (1333 satır), `AssistantMessage` (1168), `ChatInput` (1069), `AssistantChatPane`, `InitialView`, `ModelToggle`, `AskInputPopup`, `EditCard` (`components/assistant/`, satır sayıları `wc -l`).
- Yanıt, düz metin değil bir "olay zaman çizelgesi"dir: `reasoning`, `content`, belge okuma/bulma/oluşturma/düzenleme, araç çağrısı, hata ve soru-isteme olayları sırayla çizilir (`contracts/index.d.ts:297-393`; `components/assistant/message/EventBlocks.tsx`, yalnızca adı görüldü).
- Yanıt metni `react-markdown` ile çizilir; `[N]` veya `[N, M]` biçimindeki satır içi işaretler, ayrıştırma öncesi regex ile iç belirteçlere çevrilip atıf kayıtlarıyla eşlenir (`message/citationUtils.ts:3-21`; `MarkdownContent.tsx:1-20`).
- Akışta metin, `useSmoothedReveal` ile ekranda yumuşatılarak gösterilir (`message/useSmoothedReveal.ts`; davranışı olay kaydından, aşağıda).
- Yan yana iki sohbet (`?side=<chatId>`) hem Assistant'ta hem IDE'de desteklenir; ikinci sohbet `md` altında gösterilmez (`docs/design-system.md:244-259`).
- Giriş kutusunda "/" ile iş akışı (workflow) çağırma menüsü vardır: iş akışı başlığından bir komut türetilir, önek eşleştirmesi yapılır (`assistant/workflowSlashCommands.ts:7-39`; `ChatInput.tsx:267-271`). Yanıttan metin seçip girişe "alıntı" olarak eklemek de mümkündür (`ExcerptPillUI`, `ChatInput.tsx:24-26`).
- `ask_inputs` olayı, modelin kullanıcıya yapılandırılmış soru sormasını sağlar; yanıt aynı asistan mesajının devamı olarak gönderilir (`contracts/index.d.ts:297-312`, `assistantTurns.ts:23-27`). Bağlayıcı eylemleri için "onay" öğesi vardır: araç adı, argümanlar ve bağlayıcı kimliği kontrol edilir (`assistantTurnStream.ts:106-143`).

### 7. Atıf gösterimi ve doğrulanmamış atıf işareti

- Atıf nesnesi belge veya dava türündedir. Her atıf, birden çok alıntı (`quotes`) taşıyabilir ve her alıntının `verification` alanı (doğrulandı mı, kaynak parçası, karakter aralığı) olabilir. Atıf düzeyindeki `verified`, yalnızca tüm alıntılar kaynakla eşleştiyse doğrudur (`components/shared/types.ts:394-446`; `contracts/index.d.ts:64-73`).
- Doğrulama sunucuda yapılır: alıntı, kaynak metne karşı denetlenir ("verified rozeti"ni bu işlev besler); bu işlev mutasyon testi kapsamındadır (`docs/test-depth.md:21-28`).
- Ön yüz kuralı: `verified === false` ise "doğrulanmamış", aksi halde (`undefined` dahil) "doğrulanmış" kabul edilir (`citationVerification.tsx:25-35`). Bu tasarım, eski kayıtların sahte alarm üretmemesini sağlar; fakat HakHukuk için ters seçilmeli (bkz. değerlendirme).
- Doğrulanmamış atıfın sunumu: kırmızı pill, `aria-label` içinde "Could not verify quote" eki ve açılır not. Not şu anlamdadır: model kaynakta bulunmayan bir alıntı üretti, halüsinasyon sayılmalı, yanıtın ilgili bölümü belgeyle karşılaştırılmadan güvenilmemeli (`citationVerification.tsx:18-23,50-55,57-93`). Mike, `CitationPillUI` için kırmızıyı "doğrulama hatası" renk rolü olarak tasarım sistemine kaydetmiştir (`docs/design-system.md:379`).
- Doğrulanmamış bir alıntı satırı tıklanamaz (`disabled`), belge görüntüleyicide vurgulanmaz ve seçili sayılmaz (`components/assistant/CitationQuotesSection.tsx:127-143,233-234,285`; `components/shared/DocumentContent.tsx:160`).
- Atıf pill'ine tıklayınca belge sağ panelde açılır, alıntı vurgulanır; elektronik tablo atıfları sayfa değil sayfa adı + hücre adresi ile konumlanır (`shared/types.ts:422-437`; `docs/docx-preview-engines.md:21-24`).

### 8. Belge görüntüleyici, redline (izlenen değişiklik) kartları

- Üç görüntüleyici: `DocxView` (EigenPal), `PdfView` (pdfjs), `SpreadsheetView` (fortune-sheet) (`components/shared/views/`). Ortak sarmalayıcı `DocumentContent` başlık satırı, atıf alıntıları, düzenleme kartları, yükleme/hata durumlarını ve dosya türüne göre görüntüleyiciyi taşır; asistan yan paneli ve IDE aynı bileşeni kullanır (`docs/docx-preview-engines.md:18-23`).
- Düzenleme yetkisi sunucudan gelir (`can_edit`, `can_delete`), yetkiler yüklenirken görüntüleyici kapalı kalır; paylaşılan sohbet okuyucuları düzenlemeyi açamaz (`docx-preview-engines.md:9-14`).
- Her belgenin tek sekmesi ve sürüm seçicisi vardır; çoklu sürüm varsa seçici menü açar, sürüm değişince önceki sürümün atıf/düzenleme bölümü temizlenir ve DOCX otomatik kaydı beklenir (`docx-preview-engines.md:34-39`).
- Redline kartı (`EditCard`, `EditCardUI`): model bir "izlenen değişiklik" önerir; kartta silinen metin, eklenen metin, gerekçe, değişiklik numarası ve Accept/Reject/View düğmeleri vardır (`EditCard.tsx:146-149,230-247`; `contracts/index.d.ts:200-216` EditAnnotation alanları: `deleted_text`, `inserted_text`, `context_before/after`, `status: pending|accepted|rejected`).
- İyimser güncelleme deseni: kullanıcı kabul/ret dediği anda, arka uç dönmeden, belgedeki ilgili ekleme/silme öğeleri DOM düzeyinde gizlenir veya normal görünüme çevrilir; çağrı başarısız olursa her stil ve sınıf geri alınır ve "Couldn't save accept — reverted." uyarısı verilir (`EditCard.tsx:10-93,193-224`). İstek sürerken aynı belgedeki diğer kartların düğmeleri devre dışı kalır, yarış engellenir (`EditCard.tsx:105-110`). Toplu çözümleme dışarıdan `resolvedStatus` ile kart durumunu ezer (`EditCard.tsx:98-104`).
- Kabul/ret sonrası sunucu yeni belge sürümü üretir ve `version_id`, `download_url` döner (`EditCard.tsx:194-208`). Yani "redline" Mike'da bir sürüm zinciridir; model değişikliği doğrudan dosyaya yazmaz.
- Görüntüleyici sürümleri için DOCX içindeki izlenen değişiklik öğeleri OOXML revizyon kimliğiyle bulunur; ekran dışı değişiklikler tekrarlayan metin yüzünden yanlış yere gitmesin diye metin değil kimlik kullanılır (`docx-preview-engines.md:30-32`).

### 9. Proje ve belge kütüphanesi

- Proje, belge kümesi + sohbet + tablo incelemesi kapsayıcısıdır: `/projects/[id]` altında `assistant`, `folders`, `tabular-reviews` rotaları vardır (rota listesi).
- `FileDirectory.tsx` (1364 satır), klasör/dosya gezgini ve seçicidir; `useDirectoryData` ile beslenir (`components/shared/`). Kütüphane (`/library`) klasörler, şablonlar ve hazır şablonlar (`presets`) içerir (rota listesi). Silme ve taşıma işlemleri için klasör ağacı doğrulaması sunucuda tek yerdedir (`docs/backend-architecture.md:279`).
- Belge ve sürüm yaşam döngüsü (oluşturma, etkinleştirme, silme) tek modülde (`modules/documents/`) toplanmıştır; ön yüz yalnızca sonuçları gösterir (`backend-architecture.md:287-304`).
- Yükleme doğrulaması (`documentUploadValidation.ts`) ve dizin yükleme (`documentDirectoryUpload.ts`) ayrı kütüphane dosyalarıdır (`lib/` listesi).

### 10. Tablo inceleme (tabular review) ızgarası

- Kavram: satır = belge (veya klasör), sütun = kullanıcı tanımlı soru/istem ve biçim; hücre = o belgeden çıkarılmış cevap. `ColumnConfig` alanları: `index`, `name`, `prompt`, `format`, `tags`. Biçimler: `text`, `bulleted_list`, `number`, `currency`, `yes_no`, `date`, `tag`, `percentage`, `monetary_amount` (`shared/types.ts:684-701`).
- Hücre: `content.summary`, `flag` (green|grey|yellow|red), `reasoning`; durum `pending|generating|done|error` (`shared/types.ts:730-743`). Yani her hücrede kısa cevap, renk bayrağı ve gerekçe vardır.
- Izgara (`TRTable.tsx`, 475 satır): ilk sütun 332 px yapışkan belge sütunu, veri sütunları 300 px (`TRTable.tsx:35-45`); iskelet satırları (4 sütun x 5 satır) yükleme durumunu verir (`TRTable.tsx:33-34`). Hücre ayrıntısı yan panelde (`TRSidePanel.tsx`) belgeye ve atıfa bağlanır; ızgara içinde de sohbet paneli vardır (`TRChatPanel.tsx`).
- Üretim akışı: `cell_update` çerçeveleri ilgili `row_id` ve `column_index` hücresinin içeriğini ve durumunu yerinde günceller; hatada `safe_to_display` bayrağıyla mesaj gösterilir (`TabularReviewView.tsx:602-657`). Aynı döngü hem `POST /generate` hem yeniden-bağlanma `GET` akışı için ortaktır; son çerçeve kimliği `lastFrameIdRef` ile tutulur (`TabularReviewView.tsx:603-612,665-690`).
- Sunucu tarafı: `POST /tabular-review/:id/generate` bir run açar, soket kapanırsa çıkarım sürer; `GET .../generate/stream?from=` devam ettirir; `POST .../generate/stop` durdurur ve durdurulan hücreler `pending`e döner; ikinci `generate` `409 review_running` verir (`backend-architecture.md:105-133`).
- Sütun hazır şablonları (`columnPresets.ts`): ad, eşleşme regex'i, istem ve biçim. Örnekler "Parties", "Governing Law", "Effective Date", "Term", "Termination" (`columnPresets.ts:11-50`). İstemler "yalnızca şunu yaz, başka metin yok" biçiminde dar çıktı ister.
- Dışa aktarma: Excel (`exportToExcel.ts`, yalnızca adı görüldü).

### 11. İş akışı (workflow) seçici

- İş akışı, başlık + istem gövdesi olan bir "beceri"dir. Sistem iş akışları ayrı bir `mike-workflows` deposunda `SKILL.md` (başlık bilgisi YAML ön madde, gövde talimat) ve tablo incelemesi için `table-columns.yaml` olarak tutulur; bir `pack.yaml` bunları paket olarak gruplar, doğrulama eksik veya fazla dizinde derlemeyi düşürür (`CONTRIBUTING.md:42-69`).
- Beş iş akışı varsayılandır; her kullanıcıya bağımsız, düzenlenebilir kopya olarak kurulur. Diğerleri "Add-ons" kataloğundadır ve içe aktarılınca bağımsız kopya olur. Katalog senkronu dağıtımda ayrı iş olarak çalışır: arşivi indirir, doğrular, varlıkları depoya yükler ve etkin satırları tek işlemde değiştirir (`CONTRIBUTING.md:53-63,70-85`).
- Arayüz: seçici modal (`WorkflowPickerContent.tsx`, 473 satır), iş akışı listesi, detay sayfası, iş akışı yazma modali, add-on önizleme, ZIP dışa aktarma (`components/workflows/`). Sohbette "/" komutu ve `workflow_applied` olayı iş akışının uygulandığını işaretler (`assistantTurnStream.ts:562`).
- Arşivlenmiş bir tasarım notu, iş akışlarının ilk halinin kodda tanımlı başlıklı istemler (`{ id, title, prompt_md }`) olduğunu ve modelin `list_workflows` ile `read_workflow` araçlarıyla bir iş akışından diğerine zincirleyebildiğini anlatır; belge artık güncel değildir ama fikir görünür (`docs/superpowers/specs/2026-06-29-legal-workflows-design.md:1-34,79-107`).

### 12. Ayarlar ve model seçimi

- Ayar sayfaları ayrı ayrı (rota listesi): görünüm, kendi anahtarını getir (BYOK), bağlayıcılar, özellikler, bellek, modeller, etkinlik, kurumlar, kişiselleştirme, gizlilik/veri, güvenlik.
- Model kataloğu hem web hem Word eklentisi tarafından kullanılan saf veri + fonksiyon modülüdür; statik katalog, eski-yeni kimlik eşlemesi, görünen adlar, yönlendirici (router) dilimleri ve anahtar tabanlı kullanılabilirlik içerir (`shared/lib/modelCatalog.ts:1-15`). `DEFAULT_MODEL_ID` bilinçli olarak boştur: ürün düzeyinde bir varsayılan model yoktur (`modelCatalog.ts:53`; `hooks/useSelectedModel.ts:50-52` "without a product default").
- Seçim çözümü sıralıdır: sohbet modeli, sonra profildeki son seçim; saklı değer katalogda yoksa, router seçimi kapalıysa veya anahtar yoksa atılır (`useSelectedModel.ts:23-60`). Dağıtım tarafından yapılandırılan modeller `GET /models/configured` ile gelir (`useSelectedModel.ts:22-24`). Yerel model (Ollama) için ayrı kanca vardır (`hooks/useOllamaModels.ts`, yalnızca adı görüldü; Mike'ın desteklediği yerel yol `CONTRIBUTING.md:11-13` içinde "Ollama" olarak geçer).
- Hata sunumu: bildirimler tek bir kart bileşeniyle çizilir; uyarılar için kapanana kadar duran `WarningPopup`, başarı ve bilgi için zamanlayıcıyla kapanan toast (`docs/design-system.md:456-494`). Ham arka uç, veritabanı veya sağlayıcı hatası kullanıcıya gösterilmez; bilinen 4xx iletiler eşlenir, beklenmeyenler `userFacingError.ts` yardımcılarıyla genel metne çevrilir (`AGENTS.md:107-109`).

### 13. Tasarım sistemi ilkeleri

(`docs/design-system.md`)

- Katmanlar: `components/ui/` (web ilkelleri, veri çekmez), `shared/ui/` (web + Word eklentisi ortak, `XxxUI.tsx` adı, `app/` içe aktaramaz), `components/shared/` (uygulama kabuğunu bilen yapı taşları), `components/<özellik>/` (satır 11-23). Yeni UI öncesi bu sırayla arama zorunludur (`AGENTS.md:35-51`).
- Belirteçler: iki aile bir arada. Mike'ın yüzey belirteçleri (`--app-background`, `--app-surface`, `--app-floating` vb., satır 63-78) ve shadcn anlamsal belirteçleri (satır 97-105); karanlık mod sınıf tabanlıdır, sistem tercihine değil `.dark` sınıfına bağlıdır (satır 124-131). Belirteçler tek bir CSS dosyasında bildirilir ve hem web hem eklenti içe aktarır; kopya bildirimi bir test yakalar (satır 57-61).
- Katı kurallar: ham onaltılık renk yerine belirteç; tip ölçeği ağırlıklı `text-xs`, başlıklar serif (satır 172-196); boşluk ölçeği Tailwind varsayılanı, "tek seferlik `px-[13px]` bu belgenin önlemek istediği sapmadır" (satır 198-210).
- İçerik sığdırma: e-posta ve izin metni kesilmez, ayrı satırlara konur, `min-w-0` ve uzun değerlerde sarma uygulanır; yükleme, bağlı, boş ve hata durumları aynı dış yerleşimi kullanır (satır 218-242). AGENTS.md aynı kuralı tekrarlar (`AGENTS.md:28-33`).
- "Cam" yüzey malzemeleri: düz, ince, yüzen, modal, yarı saydam (satır 277-286); durum sınıfları (hover, seçili, basılı) elevasyondan ayrıdır (satır 288-302). Menüler tek `dropdown` ilkelinden yapılır; elle konumlanmış div menüler klavye gezinmesi, rol ve odak dönüşünü kaybettirdiği için yasaktır (satır 320-325).
- Erişilebilirlik tabanı: her etkileşimli ögede görünür odak halkası (mavi), simge düğmelerinde `aria-label`, form içinde `type="button"`, durum yalnızca renkle değil ARIA ile, kontrast >= 3:1, süs simgeleri `aria-hidden` (satır 415-454). Bu tabanı otomatik denetleyen bir axe taraması vardır (aşağıda).
- Bileşen kataloğu: Ladle hikâyeleri `tsconfig` içindedir; bileşen özellikleri değişirse hikâye derlemeyi kırar (satır 496-513).
- Uyarı: "Bilgi amaçlı etiketler dekoratif hap (pill) rozeti olmak yerine düz metin olmalı" kuralı AGENTS.md'de açıkça yazılıdır (`AGENTS.md:23-26`).

### 14. Test piramidi

Katmanlar ve araçlar:

1. **Birim/bileşen testleri (Vitest 5 + jsdom + Testing Library).** Testler kodun yanına `*.test.ts(x)` olarak konur. `frontend/src` altında 310, `backend/src` altında 266 test dosyası vardır (`find` sayımı; yapılan sayım, Word eklentisi için 1 dosya `*.test.*`). Kural: gerçek ağ ve gerçek arka uç yok; `fetch` ve kimlik istemcisi taklit edilir, bir `describe` bloğu bir işlev veya kaygıya karşılık gelir (`docs/frontend-testing.md:26-31`). Yerel çalıştırmada işçi sayısı CPU ve RAM'e göre sınırlandırılmıştır; çünkü ön yüz çatalları jsdom başlatıyor ve bir meslektaşın dizüstüsünü çökertmiştir (`frontend/vitest.config.mts:6-20`).
2. **Mimari testler.** Arka uçta `architecture.test.ts` dizinleri dolaşıp içe aktarmaları regex ile okur, katman kurallarını denetler; ihlal "testi değil katmanı düzeltmek" demektir; izin listesi girişleri gerekçeli yorum ister, satır-içi sorgu sayısı yalnızca azalan bir "çıta"dır (`docs/backend-architecture.md:227-237`; `AGENTS.md:136-138`). Ön yüzde benzer bir test, üretim kodunun `frontend/` dışına yalnızca Docker'ın kopyaladığı `paths` takma adıyla uzanabileceğini zorlar (`AGENTS.md:100-105`).
3. **Kapsam çıtası ("ratchet").** Ön yüzde yalnızca `src/app/lib/**` için eşik vardır (ifade 99, dal 97, işlev 100, satır 100); bileşenler ve kancalar çalışır ama eşiğe bağlanmaz çünkü kapsamları "arayüz biçimli ve gürültülü"dür (`docs/frontend-testing.md:146-151,221-225`). Arka uçta tüm `src/**` için eşik: ifade 60, dal 51, işlev 64, satır 63; ölçülen genel kapsam %60,59 (`docs/testing-coverage.md:56-59,124-125`, dosya içi 239-242 ve 307-309 satırlarından). Kurallar: eşikler yalnızca yükselir, düşürmek yasak, testi ekleyen PR eşiği ölçülen değere yükseltir (`testing-coverage.md:134-141`, dosya içi 317-324). Eşiklerin CI'da uzun süre zorlanmadığı da kayda geçmiştir: 2026-07-22 ile 2026-09-14 arasında iş yalnızca `npm test` koşmuştur (`testing-coverage.md:128-133`, dosya içi 311-315).
4. **Mutasyon testi (Stryker).** Yalnızca güvenlik açısından kritik beş arka uç modülüne uygulanır: erişim kontrolü, indirme belirteçleri, atıf çıkarma, atıf doğrulama (alıntı kaynakta var mı) ve SSRF özel-IP koruması (`docs/test-depth.md:18-28`). Son ölçüm toplam 70,0 (atıf doğrulama 63,5, atıf çıkarma 79,2) (`test-depth.md:91-95`). Vitest 5 ile uyumsuzluk nedeniyle 2026-09-11'den beri gerçek skor üretilemiyor; iki kırılma belgelenmiş: TypeScript 7'de kaldırılan bir API nedeniyle çökme ve mutant başına sıfır test okunduğu için tüm mutantların "hayatta kaldı" sayılması (`test-depth.md:43-77`). Birleştirmeyi engellemez; aylık cron ile görünür tutulur.
5. **Gerçek yığın testleri.** `npm run test:stack`, gerçek Supabase gerektiren kimlik doğrulama ve erişim testlerini koşar; ortam yoksa temiz şekilde atlanır, düz `npm test` her zaman yeşil olmalıdır (`CONTRIBUTING.md:113-127`).
6. **Uçtan uca (Playwright).** Aşağıda.
7. **Yük testi (k6).** Aşağıda.

Disiplin kuralları (belgelerden):
- Regresyon testi "en düşük yararlı katmanda": önce birim, sonra rota entegrasyonu, tarayıcı yalnızca gerçekten gerekliyse (`AGENTS.md:246-247`; `CONTRIBUTING.md:119-121`).
- Test sınırı seçimi: önce yakalanması gereken somut hatayı belirle, ilgili kodu gerçek tut, en düşük gözlem katmanını kullan; test gözden geçirilirken "bu testi bozacak makul bir hatalı uygulama hangisi" sorusu sorulur (`docs/e2e-ci.md:149-166`).
- Bir sahte (fixture) sağlayıcı, gerçek modelin doğru aracı seçtiğini veya doğru cevap verdiğini kanıtlayamaz; bu sorular canlı sağlayıcı duman testleri ve beklenen olgu/atıflı belge değerlendirmeleri ister, CI'da otomatik canlı-model kalite kapısı yoktur (`e2e-ci.md:158-163`).
- PR öncesi: ilgili test, `git diff --check`, kapsam dışı değişiklik kontrolü, hangi doğrulamaların koşulduğunun raporu (`AGENTS.md:249-251`).

### 15. Uçtan uca testler (Playwright) ve CI

- Yapılandırma: iki ana proje, `chromium` (tam yığın) ve `synthetic` (tarayıcıda tüm `/api` çağrılarını taklit eden, arka uca ihtiyaç duymayan iki spec) (`playwright.config.ts:55-79`). İşçi başına ayrı kullanıcı hesabı; aynı dosyadaki testler sırayla çalışır; CI'da 2 yeniden deneme, stres modunda 0 yeniden deneme ve başarısızlıkta iz saklama (`playwright.config.ts:13-35,46-53`; `docs/e2e-ci.md:37-54`).
- Yığın: CI RustFS (S3 uyumlu depo) ve yerel Supabase başlatır, `backend/schema.sql` ile taze şemayı yükler (geçmiş geçişleri üst üste oynatmaz; eski işlev tanımlarını geri getirebilirlerdi), üretim derlemesini ve ayrıca `next dev` derlemesini sunar (`docs/e2e-ci.md:16-35`). Gece 03:47 UTC'de çalışır (`e2e-ci.md:10-14`).
- Spec dosyaları: erişilebilirlik, asistan akışı, kimlik akışları, sohbet yönetimi, bağlayıcı onayı/salt-okunur, kritik yol, Google Drive/Workspace, proje yönetimi, tablo incelemeleri, tablo sohbeti yaşam döngüsü, iş akışı ve ayarlar (`e2e/` listesi). `test(` çağrı sayısı dosya başına 1 ile 7 arasındadır (grep ile; döngüyle üretilen testler eksik sayılır, bu nedenle toplam vermiyorum). Word eklentisinin kendi `e2e/` dizininde 28 öğe vardır (`ls`).
- Belirleyici model sağlayıcı: `e2e/anthropic-stub.mjs`, yerel bir 4141 portunda Anthropic protokolünü taklit eder; kurallı iki senaryo vardır (tam cümleyi yankılama ve bir PDF'i `read_document` aracıyla okuma). Bilinmeyen istem sessizce makul cevap üretmek yerine hata verir; böylece düşen kullanıcı mesajı gizlenmez (`anthropic-stub.mjs:1-18,35-39`; `docs/e2e-ci.md:121-148`). Araç sonucunu yankılarken beklenen metin sunucuda değil tarayıcı doğrulamasında tutulur ki sahte sağlayıcı cevabı "ima etmesin" (`anthropic-stub.mjs:25-26`; `critical-path.spec.ts:38-40`).
- İki gerçek akış testi: sohbet yaşam döngüsü (gönder, tamamlanmış yanıtı bekle, yeniden yükle, yeniden adlandır, sil, silindiğini yeni isteğin 404 vermesiyle doğrula) ve proje belgesi (PDF yükle, soruyu sor, yalnızca PDF'te geçen metni tarayıcıda doğrula, yeniden yükleyip kayıtlı cevabı doğrula) (`docs/e2e-ci.md:129-141`). İyimser arayüz değişikliği tek başına testi geçirmez.
- Erişilebilirlik taraması: `/login`, `/assistant`, `/projects`, `/tabular-reviews` üzerinde axe-core; `critical` ihlal derlemeyi düşürür, `serious` yalnızca yazdırılır, kademeli sıkılaştırma planlıdır (`e2e-ci.md:98-106`).
- Stres işleri: React'in geliştirme sürümü 3-4 kat yavaştır; stres modu Chromium'da 4x CPU kısıtlaması uygular ve "maksimum güncelleme derinliği", aşırı çizim, önbelleksiz anlık görüntü ve ResizeObserver döngüsü tanılarında hata verir. Bu işler gece ve `stress` etiketli PR'larda koşar, zorunlu kontrol yapılmamalıdır (etiketsiz PR'larda hiç raporlanmazlar) (`e2e-ci.md:76-96`; `docs/frontend-testing.md:129-137`).
- Dal koruma: `e2e / playwright`, üç "Assistant streaming (production, ...)" kontrolü ve Word eklentisi kontrolü zorunlu önerilir; iş akışı tanımı tek başına depo ayarını zorlayamaz (`e2e-ci.md:179-198`).
- Diğer iş akışları (yalnızca dosya adları görüldü, içerikleri okunmadı): `ci`, `codeql`, `desktop`, `docker-images`, `e2e`, `gitleaks`, `mutation`, `schema-drift`, `scorecard`, `security`, `stack-tests`, `word-addin`. `docker-images` her PR'da üç imajı kökten derler, çünkü ana makine derlemesi eksik bağlam dosyasını yakalayamaz (`AGENTS.md:228-234`). `schema-drift` taze şema ile yükseltilmiş şemanın aynı yere varmasını denetler (`AGENTS.md:197-198`; `e2e-ci.md:19-23`).

### 16. Yük testi senaryosu (`loadtest/sse-stream.js`)

- Araç k6. Senaryo `ramping-vus`: başlangıç 0, 30 sn'de VUS'a (varsayılan 5) çıkış, 2 dk tutma, 15 sn inme; devam eden akışların bitmesi için 330 sn zarif inme (`sse-stream.js:59-74`). Her sanal kullanıcı yineleme başına bir tam akış açar, yani tepe VUS = eşzamanlı açık SSE akışı (`sse-stream.js:65-67`).
- Her akış için denetimler: durum 200, `text/event-stream`, `chat_id` olayı geldi (akış gerçekten başladı), `data: [DONE]` geldi (akış kesilmedi) (`sse-stream.js:127-140`; `docs/test-depth.md:114-122`). `[DONE]`'ın yokluğu, geçmiş olay sınıfı olan "uzun araç çağrılarında akışın zaman aşımına uğraması"nı tarar (`sse-stream.js:133-136`; `test-depth.md:114-116`).
- Metrikler: ilk bayt süresi (TTFB), tam akış süresi, tamamlanma oranı, akış içi `error` olayı oranı (`sse-stream.js:52-57`).
- Eşikler bilinçli olarak gevşektir: TTFB p95 < 15 sn, akışların >= %90'ı tamamlanır, akış içi hata olayı < %20, HTTP hata oranı < %10; "kabul edilmiş bir hizmet düzeyi hedefi yok, takılan/çöken yığını yakalamak amaç" (`sse-stream.js:75-91`).
- Dikkat: hız sınırı varsayılan olarak IP başına 15 dakikada 30 sohbettir, test için hedef yığında yükseltilmelidir; gerçek sohbet satırı yaratır ve gerçek sağlayıcı jetonu harcar, üretime yöneltilmemelidir (`sse-stream.js:6-10,36-39`; `test-depth.md:132-146`).
- Yük testi CI'a bağlanmamıştır: bir iş akışı 2026-08-12 ile 08-27 arasında vardı, hiç koşmadan kaldırıldı, çünkü ayrılmış bir hazırlık (staging) yığını ve gizli anahtar hiç var olmamıştı (`test-depth.md:161-169`). Birleştirmeyi engellemez (`test-depth.md:180-183`).

### 17. Olay kayıtlarından çıkan dersler

`docs/incidents/` altında iki belge vardır (2026-09-29).

**Olay 1: "Maksimum güncelleme derinliği" uyarısı** (`2026-09-29-assistant-update-depth.md`).
- Müşteri, bir konuşmada sekiz mesajdan sonra React geliştirme konsolu uyarısı bildirdi (satır 3-4). Kısa yanıtlarla yeniden üretilemedi; 8 kayıtlı alışveriş (her cevapta 100 paragraf), 4x CPU yavaşlatma ve 120 ayrı parçada gelen yanıtla üretildi (satır 15-19).
- Kök neden: `ChatView`, kaydırma dinleyicisi efektini tüm `messages` dizisine bağlamıştı; her akış parçası yeni dizi demek, efekt yeniden çalışıp `setShowScrollButton` çağırıyordu. Aynı değeri yazmak koruma sayılmaz, çünkü bekleyen eşzamanlı iş varsa React güncellemeyi kuyruğa alabilir (satır 27-33). React'in sınırı 50'dir; sayaç 51'e ulaştı (satır 22-25).
- Düzeltme: gerçek içerik ve görünüm alanı boyut değişimini ve kaydırmayı gözlemle, ölçümleri tek animasyon karesinde birleştir, durum ayarlayıcıyı çağırmadan önce görünürlüğü karşılaştır, temizlikte gözlemci/dinleyici/kareyi iptal et (satır 35-40).
- Ders: hata başlangıç içe aktarmasından beri vardı (satır 55-56); üretim derlemesinde uyarı yoktur ama hatalı efekt yine çalışır, uyarının üretimde yokluğu zararsızlık kanıtı değildir (satır 44-51).
- Gözlenebilirlik dersi: Sentry gizlilik sınırı serbest metin başlıklarını genelleştirdiği ve yığın işlev adlarını sildiği için özgün React uyarısını aramak olayı bulamayabilir (satır 98-102). Sınıflandırılmış, izin listesine alınmış bir hata kodu önerilir; ham konsol argümanı saklanmaz ve gizlilik sınırı gevşetilmez (satır 110-114).

**Olay 2: Akış etkileri sınıf denetimi** (`2026-09-29-streaming-effects-audit.md`). Altı ilgili hata bulundu:
1. Akıl yürütme açılır bloğu her metin parçasında durum ayarlıyordu (web ve Word kopyaları); ortak kancaya taşındı, açık/kapalı varsayılan türetildi, kullanıcı seçimi korundu (satır 11-37).
2. Akış parçaları, yüklenmiş geçmişin konumlandırılmasını aç bıraktı: efekt tüm diziye bağlıydı, her parça temizleyip işi yeniden başlatıyordu; devam eden bir konuşma iskelet veya sıfır saydamlıkta kalabiliyordu. Bu bir canlılık (liveness) hatasıdır, istisna değildir (satır 39-60). Düzeltme: efekti sohbet/yükleme durumu, mesaj var mı ve kullanıcı mesajı sayısına bağla; regresyon doğrulamaları `[DONE]`'dan önce yapılır, tamamlanmayı beklemek hatayı gizlerdi (satır 56-60).
3. Metin animasyonu geçen zamanı kaybediyor ve hiç uyumuyordu: 120 delta ile 1,92 sn sonunda 220 karakterden 42'si görünüyordu (satır 62-76).
4. Tabloda yenilenen veri, kullanıcının seçtiği belgeyi sıfırlıyordu (300 yenilemeli regresyon); efekt bağımlılığı nesne kimliğinden ilkel kimliklere çevrildi (satır 78-102).
5. Sırasız gelen tablo sohbet geçmişi, seçili konuşmayı eziyordu (A, B, A seçim senaryosu); her geçmiş isteğine "nesil" sayacı konup yalnızca güncel nesil yayımlayabilir hale getirildi, yeni sohbet/silme/ayrılma bekleyen istekleri emekli eder; yalnızca sohbet kimliğini kontrol etmek yetmez (satır 104-112).
6. Hızlı oturum yanıtı, kabuğun hidrasyon yarışına yol açıyordu; sayfa düzeni, kendisi bağlanana kadar sunucu yükleme kabuğunu korur (satır 114-127).
- Ek ders: tam stres paketi test kurulum yarışlarını da ortaya çıkardı; çözüm uyku eklemek değil gözlemlenebilir geometriyi beklemektir (satır 129-151).
- Envanter: 405 dosyada 375 efekt, yapay zekâ destekli AST taramasıyla; tüm etkileşimler kanıtlanmış sayılmaz (satır 155-158).
- Doğrulama ölçüsü: 217 paketlik 1.788 ön yüz birim testi yerelde 126 sn; tam web üretim yığını 50 test geçti, dördü canlı sağlayıcı anahtarı gerektirdiği için atlandı; Word paketi 360 vaka, 10,1 dk (satır 200-208).
- Sınırlama beyanı: sonlu bir test matrisi gelecekteki döngülerin yokluğunu kanıtlayamaz (satır 217).
- Süreç dersi: bu inceleme kuralları `docs/frontend-testing.md:79-106` bölümüne taşınmıştır (akış verisini yüksek frekanslı girdi say; efekt tetikleyicisini ve sonlanmasını açıkça belirle; görüntü varsayılanını render sırasında türet; gözlemci geri çağrılarını tek kareye topla; hiçbir zaman exhaustive-deps bastırılmaz veya rastgele debounce eklenmez).

Her iki belge de sentetik veri kullandığını ve hiçbir müşteri hesabı veya üretim veritabanına dokunmadığını belirtir (`...-streaming-effects-audit.md:6-7`).

### 18. Word eklentisi (yalnızca mimari özet)

- Aynı depoda ayrı bir Office görev paneli uygulaması: webpack, React 19, TipTap, Tailwind; kendi `package.json` ve `package-lock.json` (`word-addin/package.json:1-47`). Backend ile aynı HttpOnly çerez oturumunu, API'yi, model sağlayıcılarını ve iş akışı kitaplığını kullanır; sohbetler web geçmişinden ayrı tutulur ve istenirse yalnızca cihazda saklanır (`word-addin/README.md:6-8,57-65`).
- Web ile kod paylaşımı: `frontend/src/shared/ui/` ve `shared/lib/` dizinleri eklentiye derlenir; yeni ortak dosya eklenince eklentinin Tailwind taramasına `@source` girdisi eklenmelidir (`AGENTS.md:53-58`; `docs/design-system.md:20-27`). Tasarım belirteçleri tek dosyada olup iki hedef de içe aktarır (`design-system.md:57-61`).
- Testler: Playwright ile Chromium ve WebKit, Office taklidiyle (Word, sertifika, gerçek arka uç gerekmez); aynı akış regresyonları on altı alışverişle koşar (`docs/frontend-testing.md:114-127`). Düzenlemeler izlenen değişiklik olarak uygulanır, `WordApi 1.6` gerekir (`word-addin/README.md:62,67`).
- Bu eklenti HakHukuk kapsamının dışındadır; yalnızca ortak paylaşım tasarımı ve testi için not edilmiştir.

## HakHukuk için değerlendirme

Varsayımlar: tek kullanıcılı yerel uygulama; Python FastAPI + SQLite arka uç; TypeScript ön yüz, büyük olasılıkla Next.js; 4B parametreli yerel model (araç çağırma ve atıf doğruluğu sınırlı); Türk mevzuatı alanı.

### Taşınır

1. **SSE çerçeveleme + sıra numaralı yeniden bağlanma deseni.** Gerekçe: yerel bir 4B model yavaş üretir, sayfa yenileme veya sekme kapanması sık olur; `id:` ile `from=` devam ettirme, [DONE] sonrası EOF'a kadar boşaltma, yorum satırı canlı tutma, hatalı JSON'u atlama aynen geçerlidir. FastAPI tarafında tek işlemli bellek tamponu yeterlidir (Mike da süreç belleği kullanır, tek kopya şartı tek kullanıcıda sorun değildir) (`lib/sse.ts:82-138`, `lib/assistantTurnStream.ts:1275-1343`, `docs/backend-architecture.md:167-181`).
2. **Üretimi HTTP yanıtından ayırma + tek durdurma ucu.** Soket kapanışı "ayrılma" olur, "dur" ayrı bir `POST` olur. Bu, yerel modelin uzun üretimlerinde tarayıcı sekmesi kapanınca üretimin boşa gitmemesini sağlar; kısmi yanıt "iptal edildi" etiketiyle saklanır.
3. **Olay zaman çizelgesi modeli.** Yanıt tek metin değil sıralı olay listesi (akıl yürütme, içerik, araç, atıf, hata) olarak tutulup render edilir; içerik parçalarının araç olaylarıyla araya girmesi doğal olarak ayrı bloklara bölünür. Geçici "düşünüyor" yer tutucuları gerçek olay gelince silinir (`assistantTurnStream.ts:206-249`).
4. **`safe_to_display` bayrağı + yapılandırılmış hata kodu.** Sunucu mesajı yalnızca açıkça işaretliyse gösterilir; yoksa genel bir cümle. HakHukuk'ta model/GGUF yükleme hataları, bellek yetersizliği gibi durumlar için aynı ayrım yararlıdır.
5. **Doğrulanmamış atıf işareti (kavram) ve devre dışı bırakılmış vurgu.** Alıntı kaynak metinde bulunamazsa kırmızı, açıklamalı uyarı; tıklanamaz, belgede vurgulanmaz. Bu, hukuk alanında en kritik güvenlik özelliğidir. Mike'da doğrulama sunucuda yapılır; HakHukuk'un "kaynak maddede bu ifade geçiyor mu" denetimi de sunucuda, deterministik olarak yapılmalı (bu, CLAUDE.md'deki "judge-free backbone" ilkesiyle uyumludur). Mutasyon testi yalnızca bu doğrulayıcıya uygulanabilir (`docs/test-depth.md:21-28`).
6. **İyimser ret/kabul + geri alma deseni** (yalnızca belge düzenleme özelliği HakHukuk'a girerse): arka uç dönmeden DOM'da çöz, hatada her stili geri al ve uyarı ver.
7. **Test disiplini:** (a) `fetch` taklidiyle akış ayrıştırıcı testleri, parça sınırı ve sondaki satırsız kayıt (`useAssistantChat.sse.test.ts` kapsamı, `docs/frontend-testing.md:176-180`); (b) mimari testi: dizin yürüyüşü ve içe aktarma regex'i, izin listesi gerekçeli ve yalnızca azalan çıta (`backend-architecture.md:227-237`) — Python tarafında `import-linter` benzeri veya basit bir test olarak karşılığı yazılabilir; (c) yalnızca yükselen kapsam eşiği; (d) sahte model sağlayıcı: OpenAI/llama.cpp uyumlu yerel bir taklit sunucu, bilinmeyen istemde patlar; (e) akış testlerinde "[DONE]'dan önce" doğrulama; (f) axe-core erişilebilirlik taraması, önce `critical` seviyesinde engelle.
8. **Olay kayıtlarındaki React kuralları** (akış verisini yüksek frekanslı girdi say, tüm diziye bağlı efektten kaçın, gözlemciyi kareye topla, zamanlayıcıyı kare başına yeniden başlatma, istek nesli sayacıyla eskimiş yanıtı at). Next.js ön yüzünde aynen geçerlidir ve ucuza önlenebilir. `docs/incidents` biçimi (tekrarlama koşulu, kök neden, düzeltme, regresyon kanıtı, sınırlama beyanı) HakHukuk'un `docs/record/` kayıt kültürüyle uyumludur.
9. **Tasarım sistemi ilkelerinin çekirdeği:** tek belirteç dosyası; ham renk yok; ARIA ile durum; görünür odak; yüklenme durumunun yerleşimle birlikte güncellenmesi; uzun değerlerin kesilmeyip sarılması; her ilkel için bileşen kataloğu hikâyesi. Hepsi küçük bir uygulama için de ucuzdur.
10. **Tablo inceleme ızgarası fikri** (satır = belge/madde, sütun = soru + biçim, hücre = kısa cevap + bayrak + gerekçe + atıf; hücre hücre akış): HakHukuk için "bir kanun/yönetmeliği sütun soruları üzerinden tara" kullanımı doğal. Izgara biçimi taşınabilir.
11. **İş akışını "başlık + istem gövdesi + isteğe bağlı sütun tanımı" olarak dosyada saklama** ve sohbette "/" ile çağırma. Dosya biçimi (ön madde + gövde) 4B model için istem şablonu kitaplığı olarak yeterince basit.
12. **Yük testi mantığı:** k6 senaryosunu olduğu gibi almak gerekmez, ancak "akış başladı mı (`chat_id`), bitti mi (`[DONE]`), ilk bayt süresi, hata olayı oranı" dörtlüsü yerel model için de doğru ölçüdür. Tek kullanıcıda eşzamanlı akış yerine uzun üretim + istemci kopması senaryosu daha anlamlıdır.

### Yeniden tasarlanmalı

1. **Atıf doğrulama varsayılanı.** Mike `verified === undefined`'i "doğrulanmış" sayar (`citationVerification.tsx:25-35`). HakHukuk'ta varsayılan "doğrulanmamış" olmalı: doğrulayıcı çalışmadıysa güven verilmez. Üç durumlu (doğrulandı / doğrulanmadı / denetlenmedi) bir gösterim daha dürüsttür. Ayrıca "madde numarası mevzuatta var mı" ve "alıntı o maddede geçiyor mu" iki ayrı katman olmalı.
2. **Atıf kimliği.** Mike'ın atıfları belge/sayfa/alıntı veya ABD dava kümesi (CourtListener) odaklı (`shared/types.ts:422-446`). HakHukuk'ta kimlik: kanun/yönetmelik adı + madde (+ fıkra/bent) + yürürlük durumu (yürürlükte/mülga) ve gerekirse sürüm tarihi. Sayfa/hücre alanları gereksiz; `legislation` zaten sözleşmede bir `SourceDocumentType` (`contracts/index.d.ts:3-8`), fakat yürürlük alanı yok.
3. **Durum yönetimi.** Mike'ın React Context'leri ve tek dosyalık 3871 satırlık API istemcisi çok kullanıcılı, kurumlu bir uygulamaya uygundur. Tek kullanıcılı bir uygulamada Auth/Workspace/Organization katmanları gereksizdir; yalnızca bir "uçuştaki tur kaydı" (modül düzeyinde `Map` + `useSyncExternalStore`) ve küçük bir ayar/model bağlamı yeter. API istemcisi alan başına birkaç küçük dosya olmalı (Mike da bunun için "tek dosya" yerine bir arka uç modülerliği benimsemiştir, ön yüzde bunu yapmamıştır).
4. **Kimlik doğrulama ve proxy.** Mike'da HttpOnly çerez + `/api/[...path]` proxy rotası vardır (çok kullanıcılı, Supabase). Tek kullanıcılı yerel uygulamada kimlik doğrulama gerekmeyebilir; yalnızca `127.0.0.1`'e bağlı sunucu ve kaynak/Origin denetimi yeter. Proxy yerine `next.config` rewrites veya doğrudan CORS ile yerel FastAPI çağrısı daha basittir. Karar HakHukuk'un dağıtım biçimine bağlı (bkz. Açık sorular).
5. **Yeniden bağlanma sınırları.** Mike varsayılan 2 yeniden deneme, 400 ms x deneme gecikmesi kullanır (`assistantTurnStream.ts:1292-1295,1318-1321`). Yerel model için sunucu zaten aynı makinede olduğundan kopma nedeni çoğunlukla sekme yenilemedir; bu durumda sayfa yüklenince `active_turn` bakıp doğrudan yakalama yeterli, ağ yeniden denemesi ikincil kalır.
6. **Kapsam eşikleri.** Mike'ın arka uç eşiği %60 gibi düşük bir başlangıçtan ratchet ile yükseltiliyor ve hiçbir aşamada hedef yok. HakHukuk'ta ayrım: (a) atıf doğrulama ve mevzuat getirici gibi doğruluk-kritik modüller için yüksek eşik veya mutasyon testi; (b) arayüz için eşik yok (Mike'ın tercihi `docs/frontend-testing.md:146-151`).
7. **Model seçici.** Mike'ın bulut sağlayıcı kataloğu, BYOK, router, kurum anahtarı mantığı HakHukuk'ta yok. Yerine: yerel GGUF listesi (yüklü modeller), tek "HakHukuk-4B" varsayılanı ve "düşünme açık/kapalı" ve bütçe ayarı (CLAUDE.md'deki 1024 düşünme + 512 cevap rejimi). Mike'ın "ürün varsayılanı yok" kararı (`modelCatalog.ts:53`) HakHukuk için tersine çevrilmeli: ürün yolu ölçüm yoluyla aynı olmalı.
8. **Tasarım sistemi.** "Cam" malzeme sistemi, çoklu yüzey katmanları, serif başlıklar görsel kimlik meselesi; HakHukuk daha sade başlayabilir: bir belirteç dosyası, bir düğme/giriş/modal/uyarı kartı/dropdown ilkel seti. shadcn tabanı hazır bileşenlerin erişilebilirliğinden yararlanmak için mantıklıdır.
9. **Eşzamanlılık düzeni.** Mike'da bir sohbette en fazla bir run, ikinci POST 409 (`backend-architecture.md:81-82`). Tek kullanıcıda da aynı kural basit ve gereklidir: yerel GPU tek üretimi kaldırır.

### Taşınmaz

1. **Çok kiracılı ve kurumsal yüzeyler:** kurumlar, üyeler, denetim kaydı, personel ayrılığı, kurum gizlilik/özel içerik, davetler, MFA kapısı, SSO girişi, kurum logosu, sağlayıcı anahtarları (rota listesi: `/organizations/**`, `/login/sso`, `/verify-mfa`, `/onboarding/invitations`). Tek kullanıcıda karşılığı yok.
2. **Bulut model sağlayıcıları ve BYOK ekranları** (`/settings/byok`, `modelCatalog.ts` kataloğu). Yerel çıkarım için ilgisiz.
3. **Bağlayıcılar:** MCP, Google Drive/Gmail/Takvim ve onay kartları (`assistantTurnStream.ts:106-143`; `e2e/google-*.spec.ts`). Uygulama yerel ve kapalı; ileride ihtiyaç olursa ayrı bir karar.
4. **CourtListener (ABD içtihat) olayları ve kartları** (altı çift olay, `assistantTurnStream.ts:668-868`). Türk karşılığı Yargıtay/Bedesten olacaksa ayrı bir "içtihat" ayağı tasarlanmalı; mevcut kodun kendisi taşınmaz. (Not: CLAUDE.md, ürünün kapsamını yalnızca mevzuat olarak belirtir; içtihat kapsam dışı.)
5. **Word eklentisi,** masaüstü (Electron) paketi, Cloudflare dağıtımı, Sentry telemetri hattı: HakHukuk'un yerel ve veri göndermeyen ilkesiyle çelişir veya kapsam dışıdır (`frontend/package.json:16-18,32`; `desktop/`).
6. **DOCX düzenleme yığını** (EigenPal editörü, izlenen değişiklik sürüm zinciri, yorum kartları). HakHukuk'un ilk hedefi mevzuat soru-cevap ve atıf; belge düzenleme kapsamı yok. Redline kartı yalnızca ileride "dilekçe/sözleşme taslağı düzeltme" özelliği gelirse gündeme gelir. Elektronik tablo görüntüleyicisi (fortune-sheet) da aynı.
7. **Proje/kütüphane/klasör hiyerarşisi, paylaşım rolleri, yan yana iki sohbet, IDE çalışma alanı.** Tek kullanıcı için erken.
8. **Ödeme/kredi, bellek (memory), kurumsal silme/veri dışa aktarma işlemleri** gibi hesap yönetimi yüzeyleri.

### Önerilen HakHukuk web ekran listesi (öncelik sırasıyla)

1. **Sohbet/soru ekranı** (tek ana ekran): giriş kutusu, akan yanıt, atıf pill'leri, "durdur" düğmesi, hata kartı, yeniden bağlanma durumu. Mike'ın `InitialView` + `ChatView` işlevinin sade karşılığı.
2. **Kaynak paneli (atıf görüntüleyici):** pill'e tıklayınca yan panelde madde metni, vurgulanmış alıntı, yürürlük durumu ve doğrulama durumu (üç durumlu). Mike'ın `DocumentContent` panelinin yerine salt-okunur bir metin görüntüleyici yeter.
3. **Sohbet geçmişi** (yan çubuk listesi): aç, yeniden adlandır, sil; sayfa yenilenince uçuştaki tura bağlan.
4. **Ayarlar:** model/GGUF yolu, düşünme açık-kapalı ve bütçe, görünüm (açık/koyu), veri konumu. Mike'ın `/settings/models`, `/appearance` karşılıkları.
5. **Mevzuat arama/kütüphane ekranı:** kanun listesi, madde arama (BM25 + gömü hibrit), yürürlük süzgeci, madde detayı. Mike'daki `/library` gezgininin mevzuata uyarlanmış hali.
6. **Tablo inceleme ekranı** (sonraki aşama): bir mevzuat kümesi veya yüklenen belge üzerinde sütun soruları, hücre akışı, bayrak ve gerekçe yan paneli. Mike'ın `TRTable`/`TabularReviewView` modeli.
7. **İş akışı/istem şablonu seçici** ("/" menüsü + liste): önceden hazırlanmış soru kalıpları ("bu madde yürürlükte mi", "karşılaştır"...).
8. **Ölçüm/rapor ekranı** (isteğe bağlı, geliştirici modu): bir yanıtın KUNYE bilgisi, kullanılan kaynaklar, doğrulama sonucu. Mike'da karşılığı yok; HakHukuk'un "sayıya yalnızca KUNYE ile güven" ilkesine uygun.
9. **Kimlik ekranları (giriş, kayıt, onboarding)** yalnızca çok kullanıcılı veya ağa açık bir dağıtım kararı çıkarsa.

Not: Bu liste, Mike'ın 6 öğeli ana gezinmesinden (`AppSidebar.tsx:70-81`) bilinçli olarak daha dardır.

### Tüketilecek olay (SSE) türleri

Mike'ın gözlenen türlerinden (bölüm 5) HakHukuk'un 4B yerel modeli ve mevzuat alanı için bir alt küme; adlandırma Mike'dan bağımsız önerilir:

Zorunlu (ilk sürüm):
- `chat_id` (sohbet, tur, mesaj kimlikleri; yeniden bağlanma için tur kimliği şart),
- `content_delta` (akan yanıt metni),
- `reasoning_delta` ve `reasoning_block_end` (düşünme kanalı açıkken; Mike'da ayrı bir olay çifti olarak vardır),
- `citations` (durum: `started|partial|final`; her atıf `verified: true|false|unchecked` ve yürürlük durumuyla),
- `error` (`code`, `safe_to_display`, `message`),
- `cancelled` (durdurma sonrası etiket),
- `content_done`,
- `[DONE]` sonlandırıcısı ve her kayıtta `id:` sıra numarası.

Büyük olasılıkla gerekli:
- `tool_call_start` ve araç sonucu olayları (mevzuat getirici çağrıları: `retrieve_start`, `retrieve_result` olarak adlandırılabilir; "model neye baktı" şeffaflığı ve "takıldı" izlenimini önler),
- `chat_title` (başlık üretimi; yerel modelle ayrı bir küçük çağrı olabilir, isteğe bağlı).

İkinci aşama:
- `cell_update` (tablo inceleme hücre akışı),
- `ask_inputs` (modelin yapılandırılmış soru sorması; 4B için güvenilirliği ölçülmeden önermiyorum).

Taşınmayanlar: `doc_*`, `mcp_*`, `courtlistener_*`, `case_*`, `workflow_applied` (iş akışı seçimi ön yüzde yapılıyorsa gerekmez), `word_edit_block`.

Sunucu yorum satırları (`: keepalive`) bir olay türü değildir ama yerel model uzun ön-doldurma (prefill) aşamasında sessiz kalabileceğinden ön yüz tarafından yok sayılmalıdır (`sse.ts:102`).

### Turborepo gerekli mi? (kanıt)

Kanıt:
- Kökte `turbo.json`, `pnpm-workspace.yaml`, `lerna.json`, `nx.json` yok (dizin listesi ve `find` çıktısı boş).
- Kök `package.json`'da `workspaces` alanı yok (`package.json:1-24`); `grep workspaces` hiçbir `package.json` içinde sonuç vermedi.
- Her uygulama (`frontend/`, `backend/`, `word-addin/`, `desktop/`) kendi `package-lock.json` dosyasına sahip (dizin listeleri); komutlar `--prefix` ile çağrılır (`AGENTS.md:207-226`).
- Paketler arası paylaşım yalnızca bir tip-sadece paketle (`@mike/contracts`, `index.d.ts`) ve TypeScript `paths` takma adlarıyla yapılır; paylaşılan arayüz kodu ise `frontend/src/shared/` dizininden eklentiye derlenir (`packages/contracts/README.md:3-5`; `AGENTS.md:53-58`).
- Önbelleklenen görev orkestrasyonu yerine GitHub Actions iş akışları ve yol süzgeçleri kullanılır (`docs/e2e-ci.md:3-35`, iş akışı dosya listesi).

Sonuç: Mike üç uygulamalık, bir de tip paketli bir depoyu Turborepo'suz yönetiyor. HakHukuk'ta ön yüz tek uygulama olacaksa Turborepo gerekmez; gerekirse tek `frontend/` dizini + FastAPI tarafında Python projesi yeterlidir. Paylaşılan sözleşme için de Mike'ın yaklaşımı (yazılı `.d.ts`) işe yarar; Python tarafında ise sözleşmenin tek kaynağı pydantic modelleri olmalı ve TypeScript tipleri bunlardan üretilmeli (bu öneri Mike'dan değil benim çıkarımımdır; Mike tipleri elle yazar ve üretici ile tüketiciyi aynı PR'da güncellemeyi kural koyar, `packages/contracts/README.md:14-20`).

## Açık sorular

1. HakHukuk web uygulaması yalnızca yerel mi (`127.0.0.1`) yoksa ağda başkalarına da açılacak mı? Cevap, kimlik doğrulamanın ve proxy rotasının gerekip gerekmediğini belirler.
2. İlk sürümde tablo inceleme ve belge yükleme olacak mı, yoksa yalnızca mevzuat soru-cevap mı? Kapsam, ekran listesinin 5 ve 6. maddelerinin zamanını belirler.
3. Atıf doğrulama üç durumlu (doğrulandı/doğrulanmadı/denetlenmedi) mi olacak? Bu karar, sözleşmedeki alan tipini ve arayüzdeki üç görünümü etkiler.
4. 4B model için `ask_inputs` benzeri yapılandırılmış soru sorma ve araç çağırma güvenilir mi? Mike'ın akışı güçlü modellere göre yazılmıştır; yerel modelde bu olaylar belirsiz kalır.
5. Python tarafında mimari testi (katman kuralları) hangi araçla uygulanacak? Mike'ın "dizin yürü + import regex" yaklaşımı Python için de yeterli mi?
6. Mutasyon testi HakHukuk'ta gerekli mi, ve gerekirse hangi modüllere (atıf doğrulayıcı, yürürlük süzgeci)? Python ekosisteminde Mike'ın karşılaştığı Stryker/Vitest uyumsuzluğu yok ama başka bir aracın (örneğin `mutmut`) maliyeti ölçülmeli.
7. Next.js seçimi kesin mi? Mike'ın akış tüketimi framework'e bağımlı değildir (saf `fetch` + `ReadableStream`); tek sayfalık bir Vite uygulaması da yeterli olabilir. Next'in sunucu bileşenleri tek kullanıcılı yerel uygulamada fazlalık olabilir (tahmin).
8. Mike'ın React Compiler kullanımı (`next.config.ts:13`) olay raporlarındaki efekt hatalarını azaltıyor mu? Belgeler bunu söylemiyor; ölçülmemiş.

## Okunmadı

Aşağıdakiler bu taramada açılmadı veya yalnızca adı/boyutu görüldü; hakkında iddia ileri sürülmemelidir:

- Ön yüz bileşenlerinin iç gövdeleri: `ChatView.tsx` (1333 satır), `AssistantMessage.tsx` (1168), `ChatInput.tsx` (yalnızca içe aktarmalar ve bir kaç satır), `TRChatPanel.tsx`, `TRSidePanel.tsx`, `TRTable.tsx` (ilk 60 satır dışında), `TabularCell.tsx`, `FileDirectory.tsx`, `DocumentSidePanel.tsx`, `DocumentContent.tsx` (yalnızca bir satır), `PdfView.tsx`, `SpreadsheetView.tsx`, `DocxView.tsx`, `EventBlocks.tsx`, `useSmoothedReveal.ts`, `highlightQuote.ts` (PDF/DOCX alıntı vurgulama algoritması).
- `useAssistantChat.ts` 140. satırdan sonrası (gönderme, durdurma, yeniden deneme, `ask_inputs` yanıtı); `assistantTurnStream.ts` 470-1240 arası olay işleyicilerinin gövdeleri (yalnızca `type` satırları listelendi); `assistantTurns.ts` 200. satırdan sonrası; `lib/mikeApi.ts` akış fonksiyonları dışında (3871 satır).
- Ayar ve kimlik sayfalarının içeriği (`/settings/*`, `/organizations/*`, `/login`, `/onboarding/*`), `contexts/UserProfileContext.tsx`, `ChatHistoryContext.tsx`, `AuthContext.tsx` 60. satırdan sonrası.
- `frontend/src/shared/ui/*` bileşenlerinin kodları, `DesignTokensUI.css`, `ThemeTokensUI.css`, `LiquidGlassUI.css`.
- Test dosyalarının içeriği: `frontend` altındaki 310 ve `backend` altındaki 266 test dosyasından hiçbiri açılmadı; yalnızca sayıları ve belgelerdeki açıklamaları kullanıldı. Bu nedenle "testler şunu doğrular" ifadeleri belge iddiasıdır, kod doğrulaması değildir. E2E spec'lerinden yalnızca `critical-path.spec.ts` tam, `assistant-streaming.spec.ts` ilk 60 satır okundu; `anthropic-stub.mjs` ilk 40 satır.
- `loadtest/sse-stream.js` 140. satırdan sonrası (bitiş denetimleri ve `teardown`).
- Word eklentisi `src/` kodu, `server.mjs`, `manifest.xml`, `word-addin/e2e*`, `docs/word-addin-development.md`, `docs/word-addin-chat-scroll-report.md`.
- `desktop/` (Electron) dizini.
- `.github/workflows/*.yml` dosyalarının içeriği (yalnızca dosya adları; iş tanımı bilgileri belgelerden alındı).
- `docs/superpowers/specs/2026-06-29-legal-workflows-design.md` 120. satırdan sonrası (belgenin kendisi "arşivlenmiş" ve güncel değil olarak işaretli). `docs/superpowers/plans/` dizini yok.
- Diğer `docs/` dosyaları (`observability.md`, `sentry-*.md`, `memory.md`, `connectors.md`, `deployment.md`, `local-development.md`, `safe-local-testing.md`, `troubleshooting.md`, `test-evidence/`, `templates/` vb.).
- `backend/` kaynak kodu (bu bölümün kapsamı dışında; backend-architecture belgesi yalnızca belge olarak okundu).
- `docs/testing-coverage.md` ve `docs/test-depth.md` dosyalarındaki satır numaraları, tek bir komutla art arda yazdırıldığı için hesapla dönüştürülmüştür (testing-coverage satır numaraları, çıktıdaki sıra no'dan 183 çıkarılarak verildi); küçük sapma olabilir.
- Yinelenen not: bazı kütüphane ve sürüm adları (Next 16, React 19.3, Vitest 5, TypeScript 7, model adları) dosyadan aktarıldı; bilgi kesimimle doğrulanamadı.
