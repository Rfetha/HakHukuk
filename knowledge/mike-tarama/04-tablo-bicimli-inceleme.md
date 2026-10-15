# Mike: Tablo Biçimli Toplu İnceleme (Tabular Review)

Kaynak kök: `mike-main/` (aşağıda yollar bu köke göredir; `backend/src/modules/tabular/` kısaca `tab/` yazıldı). AGPL-3.0 nedeniyle kod kopyalanmadı; tasarım kendi cümlelerimle anlatıldı.

## Kapsam ve okunan dosyalar

Tam okunanlar (backend, `tab/`): `tabular.prompt.ts`, `tabular.extract.ts`, `tabular.extractRow.ts`, `tabular.extraction.ts`, `tabular.extractionJobs.ts`, `tabular.service.ts`, `tabular.shared.ts`, `tabular.generate.ts`, `tabular.generateStream.ts`, `tabular.rows.ts`, `tabular.cells.ts`, `tabular.maintenance.ts`.
Kısmen okunanlar: `tabular.reviews.ts` (120-345 arası satır/hücre oluşturma, 405-585 oluşturma, 855-1110 güncelleme), `tabular.chats.ts` (1-330 ve 560-868), `tabular.routes.ts` (1-148, 340-760, 906-1000, 1090-1180).
Destek: `backend/src/lib/queue/extractionQueue.ts`, `backend/src/workers/extractionWorker.ts` (yalnızca yeniden-export), `backend/src/lib/streamRuns.ts` (ilk 60 satır), `backend/migrations/20260822_01_tabular_generation_lease.sql`, `backend/schema.sql` (2994-3016, 3250-3300, 3610-3640), `backend/src/modules/chat/engine/tools/toolSchemas.ts` (70-100), `.../toolDispatcher.ts` (810-860), `.../engine/types.ts` (45-60).
Testler: yalnızca test adları (`it(` başlıkları) ve `tabular.idleProgress.test.ts` ilk 40 satır okundu. Dosyalar: `tab/__tests__/{extractRow,extract.sanitize,generateStream,idleProgress,generate.claim,cells}.test.ts`, `backend/src/workers/__tests__/extractionWorker.test.ts`.
Frontend (`frontend/src/app/components/tabular/`): `TabularCell.tsx` (1-250), `citation-utils.ts`, `columnFormat.ts`, `columnPresets.ts`, `pillUtils.ts`, `exportToExcel.ts` tam; `TabularReviewView.tsx` seçili bölümler (600-660, 720-830, 955-1100, 1260-1300); `TRTable.tsx` 1-120 ve yapı grep'i; `AddColumnModal.tsx` ve `TRSidePanel.tsx` yalnızca grep; `frontend/src/app/components/shared/types.ts` 684-744.

## Nasıl çalışıyor

### 1. Veri modeli

- Bir inceleme (`tabular_reviews`) kolon tanımlarını tek bir `columns_config` JSON alanında tutar; ayrıca `model`, `document_grouping` ve kira alanları (`active_generation_id`, `generation_lease_expires_at`) vardır (`backend/schema.sql:2994-3010`).
- Satır (`tabular_review_rows`) bir belge ya da bir klasördür (`row_type`); klasör satırı birden çok kaynak belgeyi `tabular_review_row_sources` ile bağlar (`schema.sql:3254-3280`; `tab/tabular.rows.ts:15-25`). Hücre (`tabular_cells`) satır x kolon kesişimidir: `content` metin, `status` serbest metin (varsayılan `pending`), `generation_id` damga, ayrıca bir `citations jsonb` kolonu (`schema.sql:3282-3292`).
- `citations` kolonunun `tab/` içinde yazıldığına dair bir kullanım bulamadım; atıflar hücre içeriğinin içine satır içi işaret olarak gömülüdür (bölüm 5). Bu "bulamadım" ifadesi yalnızca `tab/` ve okunan dosyalar için geçerli; repo genelinde aranmadı.
- Hücre içeriği `JSON.stringify({summary, flag, reasoning})` olarak yazılır (`tab/tabular.extractRow.ts:199-204`); frontend tipi aynı üçlüdür (`frontend/.../shared/types.ts:736-740`).
- Satırlar ve boş (`pending`) hücreler inceleme oluşturulurken toplu eklenir; belge listesi/gruplama değişirse satırlar silinip yeniden kurulur, yalnızca kolon değişirse `syncCellsForReviewRows` kaldırılan kolonların hücrelerini siler, eksik hücreleri ekler (`tab/tabular.reviews.ts:263-345`, `1085-1099`).

### 2. Sütun tanımı ve biçim türleri

- Bir kolon: `index`, `name`, `prompt`, isteğe bağlı `format` ve `tags` (`tab/tabular.shared.ts:309-315`; frontend `types.ts:695-701`).
- Dokuz biçim: `text`, `bulleted_list`, `number`, `currency`, `yes_no`, `date`, `tag`, `percentage`, `monetary_amount` (`frontend/.../shared/types.ts:684-693`; arayüz listesi `columnFormat.ts:3-13`).
- Sunucu tarafında kolon şeması doğrulanmıyor: PATCH gövdesindeki `columns_config` olduğu gibi `updates`'e atanıyor (`tab/tabular.reviews.ts:931-938`); oluşturmada da tip yalnızca TypeScript imzasıdır (`:416`). Yani `format` değerinin geçerliliği, `tags` dizisi vb. çalışma zamanında denetlenmiyor; bilinmeyen bir `format` sessizce "ek yönerge yok" olur (`formatPromptSuffix` varsayılan dalı, `tab/tabular.prompt.ts:36-37`).
- Kolon ekleme ekranında hazır şablonlar var (Parties, Governing Law, Effective Date, Term, Termination, Change of Control, Confidentiality, Assignment, Payment & Fees, Amendment, Indemnity, Warranties, Force Majeure; toplam 13), kolon adına regex ile eşleşip prompt+format dolduruyor (`columnPresets.ts:21-200`, `getPresetConfig` `:202-210`). Şablon metinleri İngilizce ve sözleşme (ticari hukuk) odaklıdır.
- "Prompt'u başlıktan üret" uç noktası: kolon başlığı, biçim ve etiketlerden büyük modelle 512 token'lık bir çağrı yapıp `{"prompt": ...}` JSON'u ister; fence kırpar, JSON.parse eder; her hata 502 olur (`tab/tabular.prompt.ts:57-135`, `maxTokens: 512` `:114`). Sistem istemi, üretilen prompt'un biçimden değil yalnızca "ne çıkarılacağı"ndan söz etmesini zorunlu kılar (`:111-113`), çünkü biçim yönergesi ayrıca eklenir.

### 3. Prompt kurgusu

Biçim eki (suffix) kolon prompt'una çalışma anında eklenir; kayıtlı prompt'ta tutulmaz (`tab/tabular.prompt.ts:16-39`).
- `bulleted_list`: "* " ile madde işaretli liste, düzyazı yok. `number`, `percentage`, `monetary_amount`: tek değer, açıklama yok. `currency`: kodlar `[[USD]]` biçiminde çift köşeli parantezle. `yes_no`: `[[Yes]]` ya da `[[No]]`; ayrıca `reasoning` içinde `[[document:ID||page:N||quote:...]]` biçiminde atıf zorunlu. `date`: "DD Month YYYY", aralıksa em tire; atıf `reasoning` içinde zorunlu. `tag`: verilen etiket listesinden tam bir tanesi `[[etiket]]` olarak; atıf `reasoning` içinde zorunlu; etiket listesi boşsa ek boş döner (`:33-35`). `text` için ek yok.
- Tek-hücre yolu (`queryTabularCell`): sistem istemi tek bir JSON nesnesi ister: `summary`, `flag` (green/grey/yellow/red), `reasoning`. Kullanıcı mesajı "Document: dosya adı + belge metni + --- + Instruction: kolon prompt'u + biçim eki + bulunamazsa 'Not Found' de" biçimindedir (`tab/tabular.extract.ts:25-52`). Çıktı üst sınırı 2048 token (`:50`).
- Çok-kolon yolu (`queryTabularAllColumns`, asıl üretim yolu): sistem istemi her kolon için tek satırlık minify JSON nesnesi ister (`column_index`, `summary`, `flag`, `reasoning`), kolonları sırayla, her biri bitince hemen yazmasını söyler; kod çiti ve ön söz yasak (`:137-149`). Kullanıcı mesajı belge + "Columns to extract:" altında "Column N — "ad": prompt+ek+'Not Found'" satırlarıdır (`:129-151`). Bu çağrıda `maxTokens` verilmiyor (`:189-211`); varsayılan sağlayıcı katmanında (okunmadı).
- Sıcaklık/örnekleme parametresi `tab/` dosyalarında hiçbir yerde verilmiyor.
- Atıf sözdizimi: `[[document:KAYNAK_ID||page:N||quote:birebir alıntı <=25 kelime]]`; elektronik tablolar için `[[document:ID||sheet:AD||cell:A1||quote:...]]` (`:42`, `:145`). Kural: summary'deki her olgusal iddiadan hemen sonra atıf; alıntılar dar ve her iddia için ayrı olmalı.
- Çelişki (küçük model için risk): tek-hücre sistem istemi "summary'deki her iddiadan sonra atıf" der (`:42`), ama `yes_no`/`date`/`tag` ekleri summary'nin yalnızca `[[Yes]]` gibi tek simge olmasını ve atfın `reasoning`'e konmasını ister (`prompt.ts:29-34`). İki yönerge aynı istemde birbirine ters.
- "Bulunamadı" için üç ayrı sabit dize var: model "Not Found" demeye yönlendiriliyor (`extract.ts:35`, `:132`); boş summary ayrıştırmada "Not addressed" olur (`:71-72`, `:170`); Effective Date şablonu "Not specified" ister (`columnPresets.ts:138`). Bunların hiçbirini ayrı bir durum olarak ayıran kod okumadım: hücre `done` olur, `flag` çoğunlukla `grey` ("neutral/not found" tek sepet: `:146`).
- Belge bağlamı: tüm belgenin metni kısaltma, parçalama ya da bütçeleme olmadan prompt'a girer (`tab/tabular.rows.ts:144-177`, `extract.ts:49`, `:151`). PDF için her sayfa "## Page N" başlığıyla ayrılır (`extract.ts:276`); DOCX HTML'e çevrilip düz metne indirgenir (`:284-318`); elektronik tablo SheetJS ile, PPTX özel çıkarıcıyla, diğer ofis türleri LibreOffice->PDF yoluyla (`:234-260`). Klasör satırında birden çok belge `## Source document: ad / Source document ID: id` başlıklarıyla birleştirilip `---` ile ayrılır (`rows.ts:172-176`) ki model atıfta doğru kimliği yazabilsin.

### 4. Çıktı biçimi, ayrıştırma ve hata toleransı

- Şema zorlaması yok: sağlayıcının yapılandırılmış çıktı/JSON-schema özelliği kullanılmıyor; yalnızca istemle JSON istenir. Ayrıştırma istemci tarafında (sunucuda) elle yapılır.
- Çok-kolon akışı: gelen metin parçaları bir tamponda birikir, her `\n` görüldüğünde tamamlanan satır ayrı ayrıştırılır; satır `JSON.parse` edilir, `column_index` sayı değilse ya da tanımsız kolonsa atlanır, JSON bozuksa satır sessizce atlanır (`tab/tabular.extract.ts:153-181`, `:198-210`, yorum `:179`). Akış bitince kalan tampon da bir satır olarak denenir (`:219`).
- Alan normalizasyonu: `summary` boşsa "Not addressed"; `flag` dört değerden biri değilse `grey`; `reasoning` yoksa boş dize (`:169-177`).
- Sonuçlanmayan kolon = "missing". `extractRowColumns` modelin dönmediği kolonları `missing` listesinde bildirir ve karar çağırana bırakılır (`tab/tabular.extractRow.ts:230-233`, üst yorum `:11-15`). Eşzamanlı yolda bunlar `error` (durdurulduysa `pending`) yapılır (`tabular.generateStream.ts:645-657`); kuyruklu yolda iş hata fırlatır ve yeniden denenir (`tabular.extraction.ts:184-189`).
- Gövde tek satırda değil de "pretty-print" çok satırlı JSON olarak gelirse hiçbir satır geçerli JSON olmaz ve tüm kolonlar `missing` olur; satır bölme `\n`'e bağlı (çıkarım; test edilmedi). Kod çiti yalnızca tek-hücre yolunda soyuluyor (`extract.ts:57-62`); çok-kolon yolunda çit satırları geçersiz satır olarak atlanır ama çit içindeki çok satırlı JSON kaybolur.
- Tek-hücre yolunda geri düşüş (silent fallback): JSON bozuksa ham metnin ilk 500 karakteri `summary` yapılır, `flag` `grey`, hücre yine `done` olur; ham metin boşsa `null` döner (hata) (`extract.ts:80-88`). Çok-kolon yolunda böyle bir geri düşüş yok.
- Tek-hücre çağrısı sağlayıcı hatasında `null` döndürür (`extract.ts:53-56`); `null` hücreyi `error`'a çevirir (`tab/tabular.cells.ts` regenerate bölümü, "if (!result)" dalı).
- Çıktı biçimi sunucuda doğrulanmıyor: örneğin `number` kolonunda sayı olmayan değer, `tag` kolonunda listede olmayan etiket, `date` kolonunda geçersiz tarih olduğu gibi kaydedilir. Tek istisna istemcide `getPillClass`: `yes_no`/`tag` değerleri etiket renklendirmesi için eşleştirilir, eşleşmeyen gri olur (`pillUtils.ts:39-58`).

### 5. Kaynak parçası ve atıf saklama

- Atıf, `summary` (ve `reasoning`) metninin içinde `[[...]]` işaretleridir; ayrı yapılandırılmış alan yok. Sayfa numarası ve alıntı model tarafından yazılır.
- Sunucu tarafında alıntının belgede gerçekten bulunduğunu doğrulayan bir adım görmedim (`quote`, `verbatim` aramaları `tab/` içinde yalnızca istem metinlerinde çıktı; repo genelinde "verifyQuote" benzeri tablo atfına dair eşleşme bulunmadı).
- Ön yüz atıf ayrıştırıcısı: `[[...]]` işaretini iki desenle dener: `(document:ID||)page:N||(quote:)alıntı` ve elektronik tablo için `sheet/cell/row/col` + `quote` (`citation-utils.ts:17-83`). Eşleşmeyen `[[...]]` yer tutucuya çevrilmeden bırakılır ve sonra "etiket hapı"na dönüştürülür (`TabularCell.tsx:44-60`, `:150-162`). Yani `[[Yes]]` etiket olarak, `[[document:...]]` atıf numarası olarak çizilir. Aynı köşeli parantez sözdiziminin iki farklı işlev için kullanılması, ayrıştırma sırasına bağımlı bir tasarımdır.
- Atıf tıklanınca belge görüntüleyicide ilgili sayfa/alıntı vurgulanır (`TabularCell.tsx:126-145`; `onCitationClick` zinciri `TRTable.tsx:76-84`). Alıntı yerini bulamama davranışı görüntüleyici bileşeninde; okunmadı.
- Dışa aktarımda (Excel) atıflar atılır, `[[x]]` içeriği düz metin olur (`exportToExcel.ts:11-22`); atıf bilgisi Excel'e taşınmıyor.

### 6. Hücre durum makinesi

Durumlar: `pending`, `generating`, `done`, `error` (`frontend types.ts:741`; sunucuda sabit enum yok, `status` serbest metin: `schema.sql:3290`).

| Geçiş | Tetikleyen | Yer |
|---|---|---|
| (yok) -> pending | satır/kolon oluşturma, kolon senkronu | `tab/tabular.reviews.ts:226-234`, `:333-343` |
| pending/error -> pending(+damga) | üretim başlarken hücreler "sahiplenilir": `generation_id` yazılır, eksik hücre `pending` eklenir | `tabular.generateStream.ts:106-154` |
| pending -> generating | satır işlenirken, içerik temizlenerek | `tabular.extractRow.ts:161-186` |
| generating -> done | model o kolonun satırını döndürünce, damga temizlenerek | `:197-213` |
| generating -> error | eksik kolon (eşzamanlı), kuyruk denemeleri tükenince, süpürücü | `generateStream.ts:645-657`; `extraction.ts:256-320`; `maintenance.ts:89-183` |
| generating -> pending | kullanıcı durdurdu | `generateStream.ts:647-656` |
| herhangi -> pending | "clear-cells" | `tabular.cells.ts:~94-135` |
| done -> generating | tek hücre yeniden üretim | `tabular.cells.ts` regenerate bölümü |

- "Bitti" ölçütü hep `status==done` VE `content` dolu birlikte aranır; durum `done` olup içerik boşsa hücre hâlâ bekliyor sayılır (`generateStream.ts:80`; testi `generateStream.test.ts:46`).
- `done` hücreler yeniden çalıştırmada atlanır (idempotans): `extractRowColumns` yalnızca bitmemiş kolonları işler (`extractRow.ts:129-132`); testi `extractRow.test.ts:120`.
- Kolon prompt'u düzenlenince mevcut `done` hücreler geçersiz kılınmıyor: `handleUpdateColumn` yalnızca yapılandırmayı kaydediyor (`TabularReviewView.tsx:999-1013`), sunucu senkronu mevcut indeksli hücreleri koruyor (`tab/tabular.reviews.ts:299-309`). Eski içerik yeni prompt'a ait gibi görünür; kullanıcının "Clear" ya da yeniden üretim yapması gerekir (okuduğum kodda otomatik geçersizleştirme yok).

### 7. Eşzamanlılık, kira (lease), damga, iptal, yeniden deneme

İki yürütme kipi var; seçim ortam değişkeniyle: `ASYNC_TABULAR_EXTRACTION` (`backend/.env.example:222`, varsayılan `false`).

**Kira (tek üretim kuralı).** Bir incelemede aynı anda tek üretim çalışabilir. `begin_tabular_review_generation` SQL fonksiyonu satırı `for update` ile kilitler; geçerli bir kira varsa `running`, istemcinin bildirdiği `expected_updated_at` farklıysa `stale`, aksi halde kirayı alıp `started` döner (`migrations/20260822_01_tabular_generation_lease.sql:8-49`). Kira süresi 60 ile 3600 saniye arasına sıkıştırılır (`:44`); varsayılan istek 300 sn (`tab/tabular.shared.ts:337`), yenileme (heartbeat) 60 sn'de bir (`:339`). Yenileme yalnızca `active_generation_id` eşleşirse başarılı olur (migration `:51-67`); başarısız yenileme "kaybettim, dur" sinyalidir (`shared.ts:345-389`). Bitirme yalnızca kendi kimliğiyle kirayı bırakır (migration `:69-84`). `stale` koruması: istemci eski kolon yapısıyla üretim başlatamaz; PATCH `updated_at`'i değiştirir (`reviews.ts:887`). Aynı kira clear-cells ve regenerate-cell için de alınır (`cells.ts` her iki fonksiyon).

**Damga (`generation_id`).** Üretim, hedeflediği tüm hücrelere kira kimliğini yazar; sonraki tüm hücre yazmaları `.eq("generation_id", ...)` ile korunur (`generateStream.ts:106-154`; `extractRow.ts` üst yorum `:17-25`, yazmalar `:165-185`, `:199-212`). Kira devralınmış bir koşu, kazananın sonuçlarını ezemez: yazmalar hiçbir satırla eşleşmez. "Üretim işareti temizlendi mi" kontrolü aynı zamanda "koşu bitti" testidir: son işçi, damgalı hücre kalmadığını görünce kirayı bırakır (`shared.ts:421-440`). Testler: `extractRow.test.ts:194`, `:271`; `extractionWorker.test.ts:680`, `:746`, `:779`.

**Eşzamanlı (varsayılan) yol.** İstek kirayı alır, sunucu sahipli bir "run" kaydeder (`startStreamRun`, anahtar `review:<id>`), kare tamponlanır; istemci bağlantısı kopsa iş sürer, yalnızca `POST /generate/stop` iptal eder (`tab/tabular.routes.ts:392-470` civarı, `:682-715`). Satırlar üç işçiyle paralel işlenir: sabit `TABULAR_GENERATION_CONCURRENCY = 3` (`generateStream.ts:554`; işçi döngüsü `:660-672`). Her satırda tek bir LLM çağrısı tüm eksik kolonları üretir (aşağıda "satır başına tek çağrı" doğrulaması). Aynı koşunun yeniden bağlanması: `GET /generate/stream?from=N` tamponlanmış kareleri sıra numarasından tekrar oynatır (`routes.ts:720-757`; `streamRuns.ts` başlık yorumu `:1-31`). Boşta zaman aşımı 5 dk, azami ömür 4 saat (`streamRuns.ts:41-42`); model akışı canlı kaldıkça `onActivity` ile zamanlayıcı yenilenir (`extract.ts:197`, `idleProgress.test.ts` ilk 40 satır).

**Asenkron yol (bayrak açıkken, Redis/BullMQ ya da Postgres kuyruğu).** İş birimi bir satırdır: `(review, row)`; deterministik iş kimliği `extract_<review>_<row>` (tek hücre için `_<kolon>` eki) olduğundan çift gönderim aynı işe birleşir (`extractionQueue.ts:82-90`, `:96-99`). Deneme sayısı 3, üstel geri çekilme taban 2000 ms (`:119-125`; Postgres kuyruğunda `maxAttempts: 3`, `:109-114`). İş yükü minimumdur: gizli anahtar kuyruğa girmez, işçi model/anahtarı çalışma anında yeniden çözer (`extractionQueue.ts:8-18`; `extraction.ts:116-136`). Her işçi kirayı yeniler ve "son çıkan ışığı söndürür" (`extraction.ts:38-69`, `:191-210`). Tüm denemeler tükenince `markExtractionFailed` yalnızca hâlâ kendi damgasını taşıyan hücreleri `error` yapar; başka koşunun ya da clear-cells'in sahip olduğu hücrelere dokunmaz (`:256-320`). Ön yüz akışı Redis yayın kanalını dinler ve her 3 sn'de DB'yi tarayarak kaçan mesajları telafi eder; akışın tavanı 15 dk (`generateStream.ts:55-58`, `:273-313`).

**Kuyruktan iptal.** `clear-cells`, kirayı aldıktan sonra o satırların bekleyen işlerini siler; aktif işi silemez, `canceled: true` işaretini kalıcı yazar, sonraki deneme erken döner; uçuştaki deneme damgası silindiği için yazamaz (`extractionQueue.ts:129-207`; `extraction.ts:77-80`).

**Süpürücü.** Yalnızca asenkron kipte çalışır: `generating` durumunda, kirası bitmiş ve kuyrukta canlı işi olmayan hücreleri `error` yapar; tek turda en çok 500 hücre (`maintenance.ts:44-46`, `:89-183`). Eşzamanlı kipte öksüz hücreyi ayırt edecek yaş bilgisi olmadığı için süpürme kasıtlı olarak yok; "tekrar tıkla" ile düzeltilir (`:16-20`).

**Hatalı kullanıcı anahtarı** hataları (`invalid_api_key`) akışa ayrı `error` karesi olarak taşınır (`routes.ts` onError; `extraction.ts:169-174`).

### 8. İlerleme akışı (SSE)

- Kare biçimi: `{type:"cell_update", row_id, column_index, content, status}`; akış `[DONE]` ile biter. Hem POST hem GET-yeniden bağlanma aynı kare şeklini yayar (`generateStream.ts:601-610`, `:228-239`).
- Ön yüz üretim başlarken, bitmemiş tüm hücreleri iyimser olarak `generating` gösterir, `done` hücrelere dokunmaz (`TabularReviewView.tsx:794-820`); sonra `cell_update` karelerini tek tek işler (`:602-650`). Son kare numarasını tutup kopmada kaldığı yerden devam eder (`:213-217`, `:672-713`). Durdur düğmesi `POST /generate/stop` çağırır ve bekleyen hücreleri hemen `pending` gösterir (`:900-935`; `mikeApi.ts:3215`).
- Sürüm uyuşmazlığı ve çakışma durumları kullanıcıya "çalışıyor" / "yeni sürüm var" kodlarıyla (`review_running`, `review_stale`) döner (`TabularReviewView.tsx:763-777`).

### 9. "Satır başına tek çağrı" doğrulaması ve düzeltmeler

Önceki yüzeysel okumadaki üç iddia doğrulandı, iki ek ayrıntı gerekli:
- Doğrulandı: üretimde birim satırdır; satırın tüm eksik kolonları tek LLM çağrısındadır (`extractRow.ts:188-217`, `extract.ts:119-222`). Ayrıca doğrulandı: çıktı NDJSON benzeri satır satır JSON'dur, şema zorlaması yoktur, kira + `generation_id` koruması vardır.
- Ek: tek-hücre çağrısı da vardır ve farklı sistem istemi/ayrıştırma yolu kullanır (`queryTabularCell`). Yalnızca "Regenerate cell" ile tetiklenir (`cells.ts` regenerate bölümü). İki yol arasında sistem istemi, atıf kuralı ve geri düşüş davranışı farklıdır (bölüm 3-4).
- Ek: asenkron kipte satır işi hatalı ise yeniden denemede yalnızca eksik kolonlar yeniden istenir ama belge metni her denemede yeniden indirilir ve yeniden çıkarılır (`extractRow.ts:145`); önbellek yok.
- Düzeltme (ihtimalen yüzeysel okumada eksik): "iptal" yalnızca kullanıcı durdurması değildir; iptal sinyali istemci kopmasından ayrıştırılmıştır (eşzamanlı yolda istek soketi kapanması iptal etmez, `routes.ts:392-470` yorumları). Durdurma `pending`'e döner, hata olarak yazılmaz.

### 10. Hücreden/inceleme üzerinden sohbet (tabular chat)

- Sohbet inceleme düzeyindedir (`POST /:reviewId/chat`, `routes.ts:906`), hücre düzeyi değildir. Sistem istemi satırları ("ROW:i dosya adı") ve kolonları ("COL:i ad") listeler, hücre içeriğini vermez; model `read_table_cells` aracıyla istediği kolon/satır alt kümesini okur (`tab/tabular.chats.ts:101-120`; `toolSchemas.ts:76-100`; `toolDispatcher.ts:818-860`). Araç çıktısı hücre başına `Summary`, `Flag`, `Reasoning` satırları ya da "(not yet generated)" döner (`toolDispatcher.ts:841-848`).
- Atıf kuralı: yanıt metnine `[1]`, `[2]` yer işaretleri; yanıtın sonunda `<CITATIONS>` bloğu içinde JSON dizi: `{ref, col_index, row_index, quote}` (`chats.ts:122-141`). Ayrıştırma: regex ile blok bulunur, `JSON.parse` başarısız olursa boş dizi döner (sessiz) (`chats.ts:52-63`). Eşleme kolon adı/dosya adı arama ile yapılır (`:65-78`); bir hücrenin gerçekten okunup okunmadığı ya da alıntının hücre metninde olup olmadığı doğrulanmıyor.
- Sohbet oturumu: kullanıcı iletisi önce kaydedilir, asistan turu sunucu sahipli run olarak sürer, durdurulursa kısmi mesaj kaydedilir (`routes.ts:1100-1180`, `chats.ts:760-800`). Başlık üretimi ayrı küçük bir model çağrısıdır (`extract.ts:91-117`). Sohbet yalnızca görünür satırları (kullanıcının tüm kaynak belgeleri okuyabildiği satırlar) görür (`chats.ts:586-598`, `rows.ts:76-100`).
- Tabular sohbette `includeResearchTools: false` ve ek araç olarak yalnızca `TABULAR_TOOLS` verilir (`routes.ts:1048-1050`). Genel motorun diğer yerleşik araçları (belge okuma vb.) bu modda hangi ölçüde açık: okunmadı.

### 11. Kullanıcıya sunum (grid UX)

- Izgara: sol sapa yapışık sabit 332 px belge sütunu, 300 px veri sütunları, yatay/dikey kaydırma, yapışkan başlık (`TRTable.tsx:41-52`, `:155`, `:204-227`). Sanallaştırma (virtualization) görmedim (grep'te `virtual` eşleşmedi); çok büyük satır/kolon sayısında davranış bilinmiyor.
- Hücre: üretilirken iskelet (skeleton), hata için kırmızı uyarı simgesi, boşsa boş; dolu hücrede özetin ilk satırı görünür, tıklayınca yerinde genişler ya da yan panele açılır (`TabularCell.tsx:217-238`). Etiketler renkli hap olarak çizilir (`pillUtils.ts`), atıflar numaralı küçük düğmeler (`TabularCell.tsx:118-148`). `flag` rengi yan panelde rozet olarak (`TRSidePanel.tsx:625-640`); gerekçe (`reasoning`) ayrı bölümde atıflarıyla gösterilir (`:324-325`, `:658-675`).
- Dışa aktarım: Excel (`exceljs`), hücre başına yalnızca özet metni, durum `error` ise "Error", bekleyen/üretilen boş (`exportToExcel.ts:11-22`, `:51-91`).
- İşlemler: tek hücre yeniden üret, seçili satırların sonuçlarını temizle, kolon ekle/düzenle/sil, belge ekle/sil, iş akışı (workflow) uygulama (kolon kümesi değişir, sonuçlar temizlenir; `TabularReviewView.tsx:1260-1300`).

## HakHukuk için değerlendirme

### Taşınır

- Satır = belge, sütun = soru, hücre = {değer, bayrak, gerekçe, atıf} veri modeli ve "hücre durumu + tek üretim kirası + damga" kavramı. Gerekçe: model-bağımsız; tek kullanıcılı yerelde bile birden çok agent işinin aynı grid'i ezmemesi için damgalı yazma korumasına ihtiyaç var. SQLite'ta `generation_id` koşullu `UPDATE ... WHERE generation_id = ?` aynı koruma sağlar; Postgres `for update` kilidinin yerini tek yazar işlem (BEGIN IMMEDIATE) alır.
- Eksik-kolon/yarım sonuç raporlama ayrımı (`received`/`missing`) ve "politika çağırana ait" ilkesi (`extractRow.ts` başlık yorumu). Bunu hücre-başına çağrıda "hata mı, bulunamadı mı, atıf doğrulanamadı mı" üç çıktıya genişletmek mümkün.
- Idempotans kuralı: `done` + içerik doluysa atla; yalnızca eksikleri yeniden dene (`extractRow.ts:129-132`).
- Biçim eklerinin kolon tanımından ayrı tutulması ve çalışma anında eklenmesi (prompt'u biçimden bağımsız tutar). Türkçe karşılıkları (sayı, yüzde, tutar+TL, evet/hayır, tarih GG.AA.YYYY, etiket) HakHukuk için doğrudan geçerli.
- Süpürücü fikri (öksüz `generating` hücreleri sonlandırma) ve "durdurunca hata değil `pending`" kuralı. Yerelde daha önemli: llama.cpp süreci çökerse hücreler sonsuza dek dönmesin.
- Sunucu sahipli run + sıra numaralı kare tamponu + `from` ile yeniden bağlanma: SSE'yi kopma-dayanıklı yapar; FastAPI'de bellek içi ring buffer ile kolay.
- Hücre-sohbet katmanı: model hücre içeriğini önceden görmez, aletle okur; atıfı hücre koordinatı olarak verir. 4B için tüm gridi araçla okutmak yerine ilgili hücreleri sunucu tarafında seçip bağlama koymak daha güvenlidir (aşağıya bakın), ama "koordinat tabanlı atıf" fikri taşınır.

### Yeniden tasarlanmalı

- Satır başına çok-kolon tek çağrı: büyük bulut modeli varsayar (uzun bağlam, çok kolon, çok satırlı sıkı biçim, her kolon için ayrı atıf). 4B Q4 için sürekli NDJSON üretimi kırılgan: satır bölme `\n` varsayar, bozuk satır sessiz atlanır (`extract.ts:178-180`), bir hata tüm kolonları `missing` yapabilir. Çözüm: hücre-başına küçük çağrı (bölüm "Önerilen tasarım").
- Tüm belgeyi bağlama koyma (`rows.ts:144-177`): 4B için bağlam/KV bütçesi pahalı ve kalite düşer; HakHukuk'un zaten madde parçası (chunk) ve hibrit BM25+bge-m3 erişimi var. Girdi, belge yerine ilgili madde parçaları olmalı.
- Biçimin yalnızca istemle zorlanması ve sunucuda doğrulanmaması: yerelde llama.cpp GBNF/JSON-schema ile kısıtlı kodlama (grammar) kullanılabilir; sonuç doğrulaması (sayı mı, etiket listede mi, tarih parse ediliyor mu) deterministik katmanda yapılmalı. Bu, projedeki "yargıç-bağımsız sırt" ilkesiyle uyumlu.
- "Bulunamadı"nın üç farklı dizeyle ve `grey` bayrağıyla karışması (bölüm 3): ayrı bir durum alanı (`found`/`not_found`/`unparseable`/`unverified`) olmalı ki aşırı red (over-refusal) ölçülebilsin. Projenin en büyük kaybı bu; Mike bunu ayırmıyor.
- `flag` (green/yellow/red) modelin öznel değerlendirmesi ve belgesiz kalibrasyon: 4B'ye bırakılmamalı; kural tabanlı ya da kullanıcı tanımlı eşiğe bağlanmalı, ya da hiç üretilmemeli.
- Atıfın serbest metne `[[...]]` gömülmesi ve `[[Yes]]` ile aynı sözdizimini paylaşması: yapılandırılmış alan (`evidence: [{madde_id, alinti, span}]`) olmalı; atıf doğrulaması (alıntı verilen parçada alt dize mi) sunucuda yapılmalı. Mike'ta bu doğrulama okuduğum dosyalarda yok; sohbet atıfı da `JSON.parse` başarısızsa sessizce boş (`chats.ts:52-63`).
- İstem çelişkisi (summary'de atıf vs. yalnız simge, bölüm 3): hücre başına tek, açık bir çıktı şeması olmalı.
- Kolon düzenlenince eski hücrelerin geçersiz kılınmaması (bölüm 6): HakHukuk'ta her hücreye `column_spec_hash` (prompt+biçim+etiket+model+indeks sürümü) yazılıp uyuşmayan hücre `stale` sayılmalı. Bu, ölçüm hattının "`KUNYE.json` olmadan sayı güvenme" disiplinine de uyar.
- Dağıtık kuyruk/Redis/BullMQ katmanı ve çok-işçili kira devri: tek kullanıcılı yerelde gereksiz karmaşıklık. SQLite + süreç içi asyncio kuyruğu yeterli; damga ve kira korumasının sadeleştirilmiş hâli (tek `run_id`, `UPDATE ... WHERE run_id = ?`) korunmalı. Yeniden deneme: kuyruk/adaptör katmanında, üstel geri çekilme, azami 3 deneme (Mike'ın sayısı) makul.
- Eşzamanlılık 3 (sabit): yerelde tek GPU'da llama.cpp ile eşzamanlı istek sayısı `--parallel`/slot ve KV-önbellek belleğine bağlı; bu sayı ölçülerek seçilmeli (Mike'ın 3'ü bulut sağlayıcı varsayımıdır; yerel eşdeğer hesap yapılmadı).
- Çıktı üst sınırının belirsizliği: çok-kolon çağrısında `maxTokens` yok (`extract.ts:189-211`); yerelde bu sınır açıkça verilmeli.

### Taşınmaz

- İngilizce sözleşme (ticari hukuk) prompt şablonları ve "Governing Law / Change of Control" gibi kolonlar (`columnPresets.ts`): Türk mevzuat (madde/fıkra/bent) sorularına uymaz; yeni, mevzuata özgü şablon seti gerekir.
- PDF/DOCX/PPTX/XLSX yükleme ve çıkarma hattı, LibreOffice dönüşümü (`extract.ts:234-318`): HakHukuk'un kaynak kümesi önceden dizinlenmiş mevzuat maddeleridir; belge yükleme ilk sürümün kapsamında değil.
- Çok kullanıcı/organizasyon/erişim rolleri, denetim kaydı, kullanıcı başına BYOK anahtarları, sağlayıcı kataloğu (`shared.ts:110-250`): tek kullanıcılı yerel uygulamada karşılığı yok.
- Redis yayın/abone ve Postgres RPC tabanlı kira fonksiyonları (kod olarak); yalnızca kavramları taşınır.
- Büyük modelden "prompt'u başlıktan üret" (`prompt.ts:57-135`): 4B ile güvenilir değil; sabit şablon/liste tercih edilir (ancak bu yalnızca öneridir, ölçülmedi).

## Önerilen tasarım: 4B için hücre-başına küçük çağrı

Tüm sayısal değerler (bütçe, eşik) tahmindir ve ölçümle belirlenmelidir.

**Birim iş.** Bir hücre = (satır_id, kolon_id, sürüm_özeti). Bir satır, bir "konu" nesnesidir (ör. kanun, madde ya da belge); bir kolon, tek bir soru + tek bir çıktı türüdür. Hücreler birbirinden bağımsız çağrılır; bir kolonun hatası diğerlerini etkilemez (Mike'ta tek hata birden çok kolonu `missing` yapabilir).

**Girdi (madde parçaları).**
1. Erişimi sunucu yapar: satır kapsamında (ör. belirli kanun/madde kümesi) hibrit BM25 + bge-m3 ile en çok k parça (varsayılan k, tahmin: 3-6), `Yururluk.YALNIZ_YURURLUKTE` filtreli. Parça başına sabit kimlik (`madde_id`), 900 karakterlik klip (ölçüm rejimiyle aynı).
2. İstem: kolonun sorusu + parçalar `[P1] ... [P2] ...` biçiminde numaralı, her biri kimlikli. Belgenin tamamı konmaz.
3. Biçim eki Mike'ın yaklaşımındaki gibi çalışma anında eklenir ama kısıtlı kodlama ile eşlenir (aşağıda).

**Çıktı şeması (tek, sabit, kısa).**
`{"durum": "bulundu"|"bulunamadi", "deger": <türe göre>, "kanit": [{"parca": "P2", "alinti": "..."}]}`
- `deger` türleri: `metin | liste | sayi | yuzde | tutar+para_birimi | evet_hayir | tarih | etiket` (Mike'ın 9 biçimine karşılık).
- `gerekce` ve `bayrak` varsayılan olarak yok (4B'nin ürettiği öznel bayrağa güvenilmez); gerekirse ayrı, isteğe bağlı ikinci geçiş.
- Uygulama: llama.cpp GBNF ya da JSON-schema kısıtlı çözümleme ile şema zorlanır (ileride vLLM/SGLang için `guided_json` eşdeğeri). Mike şema zorlaması yapmıyor; burada yapılması 4B için en büyük güvenilirlik kazancı olması beklenir (varsayım; ölçülmeli).
- Çıktı kısa tutulur: `max_tokens` kolon türüne göre küçük sabit (tahmin: 128-256), böylece akış tamponu/satır bölme sorunu da ortadan kalkar (tek nesne, satır sınırı yok).

**"Bulunamadı"nın ayrı ölçülmesi.**
- `durum` ayrı bir alandır ve DB'de ayrı sütun: `bulundu`, `bulunamadi`, `ayristirilamadi`, `dogrulanamadi`. "Not Found"/"Not addressed" dize karışıklığı (Mike) oluşmaz.
- Ölçüm: altın küme (gold) maddesi bağlamda iken `bulunamadi` diyen oran = aşırı red; altın madde bağlamda yokken `bulundu` diyen oran = uydurma/yanlış atıf. Her ikisi ayrı sayılır; M1/M2/M3 modlarıyla aynı mantık (bağlamda var / yakın-ıska / boş bağlam). Uzunluk veya tür bazlı karışıklık matrisi `KUNYE.json` ile birlikte saklanır.
- Sağlık için üç ölçüm kaydı: (a) ayrıştırma başarısı (şema zorlamasıyla ~sıfır beklenir), (b) kanıt doğrulama başarısı, (c) `bulunamadi` oranı; hiçbiri tek bir "başarı" sayısına indirgenmez.
- Hücre durumu makinesine bu dört durumu ekleyin: `pending -> generating -> done(bulundu|bulunamadi) | needs_review(dogrulanamadi) | error(ayristirilamadi/altyapi)`.

**Doğrulama kapısı (deterministik, model dışı).** Hücre `done` olmadan önce sırayla:
1. Şema/tür: `deger` türe uyuyor mu (sayı parse, tarih parse, etiket verilen listede mi, evet/hayır kapalı küme).
2. Kanıt kimliği: `parca` gönderilen parça kümesinde mi.
3. Alıntı: `alinti` ilgili parçada alt dize mi (boşluk/noktalama normalleştirmesiyle). Alt dize değilse hücre `dogrulanamadi` olur, `done` olmaz; sessiz geri düşüş yok (Mike'ın tek-hücre yolunda ham metni `summary` yapması gibi davranış tam tersi).
4. `bulundu` ise en az bir doğrulanmış kanıt zorunlu; `bulunamadi` ise kanıt boş olmalı (tutarlılık).
5. Madde yürürlük durumu: kanıt gösterilen madde yürürlükte mi (indeks alanı), değilse uyarı.
Doğrulama başarısızsa yeniden deneme tek kez, farklı bağlam (daha fazla parça ya da bir üst madde) ile; ikinci başarısızlık `needs_review`. Yeniden deneme sorumluluğu iş kuyruğu katmanında, içeride `try/except + sleep` yok.

**Yürütme.**
- Her hücre bağımsız iş; iş kimliği `(review_id, row_id, column_id, spec_hash)`; çift gönderim aynı işe birleşir.
- Tek `run_id` damgası, koşullu yazma (`UPDATE ... WHERE run_id = :run_id`); kira süresi yerine süreç içi yaşam (tek süreç). Süreç yeniden başlarsa açılışta `generating` hücreleri `pending`'e alan süpürücü (Mike'ın süpürücüsüne karşılık, ama tek-süreç olduğundan yaş sinyaline ihtiyaç yok).
- Eşzamanlılık: llama.cpp slot sayısına bağlı küçük sabit; hücreler arası aynı satırın parçaları ortak olduğundan önek (prefix) önbelleğinden fayda beklenir (varsayım).
- İptal: bayrak hücre sınırında kontrol edilir; durdurma `pending`'e döner, hata değil.
- Kolon/prompt/model değişince `spec_hash` değişir; eski hücre `stale` işaretlenir (Mike'ta yok).
- İlerleme: hücre başına olay (`hucre_guncelle`), sıra numaralı ring buffer, `from` ile yeniden bağlanma; SSE.

**Hücre-sohbet.** Kullanıcı bir hücreye ya da hücre kümesine soru sorduğunda, sunucu o hücrelerin `deger + kanit(+parça metni)` içeriğini sabit bir blokla bağlama koyar (model aletle okumaz); yanıttaki atıflar yine `(satır, kolon, parca)` koordinatıyla ve aynı alt dize doğrulamasıyla denetlenir. Tüm gridi araçla okutmak 4B için bağlamı şişirir ve araç çağrısı güvenilirliği düşüktür (varsayım).

## Açık sorular

1. Mike'ın çok-kolon tek çağrı tasarımının doğruluk/gecikme avantajı, hücre-başına çağrıya göre hangi model boyutunda kayboluyor? 4B'de ölçülmeli (hücre-başına çağrı sayısı kolon sayısı kadar artar; önek önbelleği bunu ne kadar telafi eder?).
2. GBNF ile kısıtlı kodlama, alıntı (serbest metin) alanında alıntıyı bozmadan nasıl uygulanır; alıntıyı seçimli (parçadan konum aralığı) üretmek daha güvenilir mi?
3. `bulunamadi` kararı 4B'de nasıl kalibre edilir (eşik, ikinci geçiş, retriever skoru ile birleşim)? Mike'ın ortak "Not Found" dizesi bu ayrımı ölçmediği için referans yok.
4. Mike'ın `maxTokens` değerini çok-kolon çağrısında vermemesi (`extract.ts:189-211`) kasıtlı mı, sağlayıcı katmanında varsayılan var mı? (`lib/llm` okunmadı.)
5. Satır tanımı HakHukuk'ta ne olacak: kanun mu, madde mi, kullanıcı belgesi mi, soru-cevap çifti mi? Hücre-başına erişim kapsamını bu belirler.
6. Kolon sürümleme (`spec_hash`) kapsamına retriever indeks sürümü (`KUNYE.json`) de girmeli mi?
7. Eşzamanlı birden çok agent işinde (kullanıcı hedefi) tek `run_id` yeterli mi, yoksa satır/kolon alt kümesi başına ayrı koşu mu gerekir? Mike'ın "bir incelemede tek üretim" kuralı bu hedefle çelişebilir.

## Okunmadı

- `tabular.routes.ts` içinde satır 149-340 (liste, oluşturma, erişim, silme uçları), 760-905 (sohbet listesi/mesaj uçları), 1000-1090 ve 1180-1212 (sohbet akışının orta ve sonu, hata işleyici) okunmadı.
- `tabular.reviews.ts` içinde listeleme, ayrıntı (`getTabularReviewDetail`), kişi/erişim ve silme fonksiyonları (satır 345-405, 585-855, 1110-1142) okunmadı. `tabular.overview.ts` okunmadı.
- `tabular.chats.ts` satır 330-560 (sohbet kayıt/mesaj uçları ve `prepareTabularChat` başlangıcı) okunmadı.
- Testler: `tabular.modelSelection`, `tabular.prompt.draft`, `tabular.reviews.crud`, `tabular.overview`, `tabular.chats.service` ve `fakeDb.ts` içerikleri okunmadı; diğer testlerde yalnızca başlıklar (ve idleProgress ilk 40 satırı) okundu, gövdeler okunmadı.
- `backend/src/lib/streamRuns.ts` satır 60-413 (tampon/yeniden oynatma gerçeklemesi), `backend/src/workers/extraction.transport.ts` (iş yürütme/eşzamanlılık ayarı), `backend/src/lib/dbq/*` (Postgres kuyruğu), `backend/src/lib/llm/*` (`completeText`, `streamChatWithTools`, `maxTokens` ve sıcaklık varsayılanları) okunmadı.
- `backend/src/modules/chat/engine/streaming.ts` ve `runLLMStream` (sohbet araç döngüsü, azami yineleme) okunmadı.
- Frontend: `TRChatPanel.tsx`, `TRSidePanel.tsx` (yalnızca grep), `AddColumnModal.tsx` (yalnızca grep), `TREditColumnMenu.tsx`, `NewTRModal.tsx`, `ReviewsListTable.tsx`, `TabularReviewDetailsModal.tsx`, `TRFirstColumnCell.tsx`, `TabularReviewView.tsx` kalan bölümleri; `mikeApi.ts` ve `sse.ts` içeriği; frontend test dosyaları (başlık düzeyinde bile) okunmadı.
- `e2e/`, `loadtest/`, `desktop/`, `word-addin/`, `packages/`, `docs/` içinde tablo incelemeyle ilgili içerik aranmadı.
- Migration'lar: kira migration'ı dışında (ör. `20260419_tabular_chat_jsonb`, `20260726_01_tabular_reviews_pagination`, `20260724_02_tabular_folder_rows`) okunmadı.
