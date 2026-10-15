# Mike: veri modeli, iş kuyruğu, çalışan süreçler ve yerel paketleme

Bu not, Mike (TypeScript, AGPL-3.0) kaynağının dördüncü dilimini inceler: veritabanı şeması, kalıcı iş kuyruğu, çalışan süreçler ve masaüstü (Electron) paketi. Amaç, HakHukuk için tek kullanıcılı, yerel, SQLite tabanlı bir uygulamanın tasarım girdilerini çıkarmaktır. Kod kopyalanmamıştır; tasarım kendi cümlelerimizle anlatılmıştır. Yol:satır gönderimleri, kaynak ağacının köküne (`mike-main/`) göredir; aksi belirtilmedikçe `backend/schema.sql` için yalnızca `schema.sql:NNN` yazılmıştır.

Önceki yüzeysel okumaya göre başlıca düzeltmeler (ayrıntıları aşağıda):

1. "Çit belirteci" ayrı bir sütun değil; çalıştırıcı, sonuç yazarken satırı `id + status='running' + attempts + claimed_at` dörtlüsüyle adresliyor (`runner.ts:132-154`). Yani `claimed_at` ile `attempts` birlikte fiilî belirteç.
2. `db_jobs` için kalp atışı (heartbeat) yok. Zombi tespiti yalnızca `claimed_at` yaşına bakıyor (600 sn). Kalp atışı ve kira (lease) başka iki yerde var: `upload_processing_jobs` ve tabular inceleme "üretim kirası".
3. Öncelik (priority) alanı hiçbir kuyrukta yok; talep sırası yalnızca `run_at`.
4. "Belge sürümü değişmez" doğru değil ya da yalnızca yarı doğru: değişmezlik veritabanında zorlanmıyor, uygulama kuralı. Sürüm satırının `storage_path`, `pdf_storage_path`, `deleted_at`, `content_sha256` alanları güncellenebiliyor ve bunları izleyen bir tetikleyici temizlik işi üretiyor (`schema.sql:8013-8017`).
5. RLS "açık ama politikasız": 47 tabloda `enable row level security`, sıfır `create policy`; erişim denetimi backend'de, servis rolüyle (`schema.sql:5395-5400`).
6. `desktop/docs/self-contained-plan.md` eskimiş: "ana dalda Redis/BullMQ/işçi yok" diyor (plan:47-48 civarı, tablo satırı "backend"); oysa kodda `db_jobs` kuyruğu, BullMQ taşıyıcısı ve işçi iş parçacığı var. Gerçeği anlatan belge `desktop/README.md` ve `desktop/src/local/supervisor.js`.

## Kapsam ve okunan dosyalar

Tamamı okunan:

- `backend/src/lib/dbq/` içindeki tüm dosyalar: `types.ts`, `driver.ts`, `enqueue.ts`, `runner.ts` (492 satır), `storageCleanup.ts`, `jobError.ts`, `lifecycleGuard.ts`.
- `backend/migrations/20260829_01_db_jobs.sql` (kuyruğun ilk tanımı) ve `schema.sql`'deki güncel hali.
- `backend/src/workers/index.ts`, `registry.ts`, `appJobsWorker.ts`, `conversion.transport.ts`; `backend/src/lib/queue/appJobsQueue.ts`, `extractionQueue.ts`, `runProgress.ts`.
- `backend/src/index.ts` (süreç/iş parçacığı modları, kapanış), `backend/src/workerRuntime.ts`, `backend/src/jobs/registry.ts`, `backend/src/jobs/maintenance.ts`.
- `desktop/docs/self-contained-plan.md`, `desktop/README.md`, `desktop/src/local/{config,supervisor,schema,environment,gateway}.js`, `secrets.js` (ilk 60 satır), `desktop/src/main.js` (yerel mod ve kapanış bölümleri), `electron-builder.local.json`.
- `docs/local-development.md`, `docs/deployment.md` (veritabanı kurulumu ve "Background jobs" bölümleri), `docker-compose.yml` (db, db-init, backend, redis, worker bölümleri).
- `backend/scripts/migrate.sh` (ilk 120 satır ve belgelenen davranış).

Kısmen okunan (ilgili parçalar):

- `schema.sql` (10426 satır): çekirdek tablolar (projects, documents, document_versions, document_edits, chats, chat_messages, word_*, workflows ailesi, tabular_*, upload_*, db_jobs, memory_files, audit_events, schema_migrations), kuyruk/kira fonksiyonları, sürüm yaşam döngüsü fonksiyonları. Çok kiracılı ve bağlayıcı bölümler yalnızca listelendi.
- `backend/src/modules/uploads/uploads.processing.ts` (satır 85-100, 690-1290: iş işleme, kalp atışı, talep döngüsü, temizlik).
- `backend/src/modules/tabular/tabular.shared.ts` (kira sabitleri ve kalp atışı), `tabular.extraction.ts` (başlangıç), `documents.maintenance.ts`, `tabular.maintenance.ts` (bayat süpürme).
- `backend/src/lib/storage.ts` (dosya sistemi sürücüsü başlığı, anahtar üreticileri), `streamRuns.ts` (başlık yorumu), `runtimeConfig.ts` (yükleme işleme yapılandırması).

## Nasıl çalışıyor

### 1. Şemanın genel boyutu ve yapısı

Sayılar `grep` ile dosyadan alınmıştır (satır sayımıdır; çok satırlı ifadelerde küçük sapma olabilir):

| Ölçü | Değer | Kaynak |
| --- | --- | --- |
| Toplam satır | 10426 | `schema.sql` |
| `create table` | 66 | `schema.sql` |
| `create or replace function` | 154 | `schema.sql` |
| `create trigger` | 40 | `schema.sql` |
| `enable row level security` | 47 | `schema.sql` |
| `create policy` | 0 | `schema.sql` |
| `references auth.users` | 56 | `schema.sql` |
| Eklentiler | `pgcrypto`, `pg_trgm` | `schema.sql:6-7` |
| Taşıma dosyası | 136 `.sql` | `backend/migrations/` |
| Backend'in çağırdığı ayrı RPC adı | 66 | `grep '.rpc("...")'` (ölçüm) |
| `.from("tablo")` çağrı yeri | 558, 58 ayrı tablo | `grep` (ölçüm; çok satırlı çağrılar kaçmış olabilir) |

Mimari karar: backend veritabanına yalnızca Supabase istemcisiyle (PostgREST üzerinden) ve servis rolüyle bağlanıyor (`backend/src/lib/supabase.ts:25-44`). Tarayıcı tablolara doğrudan erişmiyor; ilgili izinler geri alınmış (`schema.sql:5395-5400`). Bu yüzden iş mantığı iki yere dağılmış: uygulama kodu ve 154 SQL fonksiyonu (çoğu `security definer`, `set search_path` ile). Ek olarak desktop planı, çağrı yerlerini 436 `.from()` + 12 RPC diye sayıyor (`desktop/docs/self-contained-plan.md`, "rest" satırı); bugünkü ölçümümüz bundan büyük, yani plan eski.

Çok kiracılı parçalar (yalnızca liste, HakHukuk için gereksiz): `organizations`, `org_members`, `org_invitations`, `org_api_keys`, `org_router_models`, `org_logos`, `org_departure_archives`, `org_departure_events`, `org_private_content_access`, `project_access_grants`, `project_org_access_overrides`, `chat_access_grants`, `tabular_review_access_grants`, `tabular_review_legacy_shares`, `workflow_shares`, `workflow_org_access_overrides`, `hidden_workflows`, `auth_handoff_tickets`, `user_profiles`, `user_api_keys`, `user_router_models`, `user_mcp_*`, `user_google_workspace_tokens`, `google_workspace_oauth_states`, `courtlistener_*` (ABD içtihat indeksleri). Çekirdek tablolarda `org_id` (RESTRICT) ve `user_id` (çoğunlukla `on delete set null`, çünkü kurum içeriği yazarın hesabından uzun yaşar; `schema.sql:962-985`, `1234-1252`) bu katmandan geliyor.

### 2. Çekirdek tabloların ER özeti

Notasyon: `A 1-N B` = bir A'nın çok B'si. Tüm anahtarlar `uuid` (`gen_random_uuid()`), zaman damgaları `timestamptz`. Alan listeleri okunan `create table` bloklarındandır; çok kiracılı alanlar (`org_id`, erişim hibeleri) atlanmıştır.

**projects** (`schema.sql:962`): `id`, `user_id` (null olabilir), `org_id`, `name`, `cm_number` (dosya/dava numarası), `practice`, `visibility` (`private`/`organization`), `archived_at`, `created_at`, `updated_at`.
- 1-N `project_subfolders` (`schema.sql:1190`), `documents`, `chats`, `tabular_reviews`; 1-1 proje belleği `memory_files` (`schema.sql:5462`).

**documents** (`schema.sql:1234`): `id`, `project_id` (cascade), `user_id`, `status` (varsayılan `pending`; kodda `processing`/`error` görülüyor), `folder_id`, `library_kind` (`file`/`template`/`workflow_asset`), `library_folder_id`, `workflow_id` (sonradan eklenmiş, `schema.sql:~1850`), `archived_at`, zaman damgaları. `current_version_id` sonradan `alter table` ile eklenmiş ve `document_versions`'a işaret eder, `on delete set null` (`schema.sql:1474-1476`). Belge adı ve dosya türü artık belge satırında değil, sürümde; liste sorguları sürümle birleştirip `coalesce(filename,'Untitled document')` kullanıyor (`schema.sql:3734-3747`). Migrasyon geçmişi bunu doğruluyor: `20260602_03_drop_documents_file_metadata.sql`, `20260602_04_drop_documents_filename.sql`.

**document_versions** (`schema.sql:1265`): `id`, `document_id` (cascade), `storage_path`, `pdf_storage_path`, `source` (`upload`/`user_upload`/`assistant_edit`/`user_accept`/`user_reject`/`generated`), `version_number`, `filename`, `file_type`, `size_bytes`, `page_count`, `textless_page_count` (metin katmanı olmayan PDF sayfası; taranmış belge göstergesi), `content_sha256`, `deleted_at`, `deleted_by`, `created_at`. `(document_id, version_number)` tekil (`schema.sql:1466-1469`). Kısmi indeks: yalnızca silinmemiş sürümler (`deleted_at is null`).

Sürüm yaşam döngüsü nasıl işliyor (tümü servis-rolü fonksiyonları):
- `create_document_version` (`schema.sql:8022-8067`): önce üst belgeyi `for update` kilitler; aynı `id` ile ikinci çağrı mevcut satırı olduğu gibi döndürür (yükleme yeniden denemesi sürümü ezmez, eski sürümü yeniden etkinleştirmez); numara verilmezse `source in (upload,user_upload,assistant_edit)` içinde `max+1`; `p_activate` ise `documents.current_version_id` güncellenir.
- `delete_document_version` (`schema.sql:8072-8103`): yumuşak silme. Tek sürüm kaldıysa reddeder (`only_version`); silinen sürüm geçerliyse bir sonrakine geçer; satırda `storage_path`/`pdf_storage_path` boşaltılır, `deleted_at` ve `deleted_by` yazılır.
- `activate_document_version` (`schema.sql:8131-8143`): silinmemiş sürümü geçerli yapar.
- Tetikleyici `document_version_cleanup` (`schema.sql:8013-8017`, işlev `schema.sql:7969-8010`): sürüm satırı silindiğinde ya da `storage_path`, `pdf_storage_path`, `deleted_at`, `content_sha256` değiştiğinde, aynı işlem içinde bir `document.cleanup` iş satırı (`max_attempts=8`) ekler; yük, silinecek nesne anahtarlarını taşır (`schema.sql:8004-8008`). Bu, "transactional outbox" kalıbıdır: veritabanı satırı kaybolurken baytların nerede olduğuna dair tek kayıt iş satırında kalır.

Sonuç: sürümler fiilen "ekle-yalnızca" (her düzenleme yeni sürüm) ama bu veritabanında zorlanmıyor. Kod yorumu da bunu doğruluyor: sürümler "iki yerinde yeniden yazma noktası dışında değişmez" (`backend/src/lib/storage.ts:769-773`). Depolama anahtarı düzeni: `documents/<kullanıcı>/<belge>/source<uzantı>`, sürümler `documents/<k>/<b>/versions/<slug><uzantı>`, çıkarılmış metin önbelleği `extracted-text/<sürüm>.txt`, dönüştürülmüş PDF `converted-pdfs/<k>/<b>/...` (`storage.ts:743-775`, `backend/src/lib/convert.ts:273-280`).

**document_edits** (`schema.sql:1478`): `id`, `document_id` (cascade), `chat_message_id` (set null; sonradan FK, `schema.sql:2975-2990` civarı), `version_id` (cascade), `change_id` (belgedeki `w:id`; izlenen değişiklik çifti Kabul/Ret için bulunur), `del_w_id`, `ins_w_id`, `deleted_text`, `inserted_text`, `context_before`, `context_after`, `status` (`pending`/`accepted`/`rejected`), `created_at`, `resolved_at`. Word eklentisi için ayrı bir aile var: `word_documents`, `word_chats`, `word_chat_messages`, `word_document_edits` (`schema.sql:2882-2965`), HakHukuk'a gerekmez.

**chats** (`schema.sql:2457`): `id`, `project_id` (cascade, null = projesiz sohbet), `user_id`, `title`, `model`, `reasoning_level` (`none..max`), `archived_at`, zaman damgaları. `updated_at` iki tetikleyiciyle güncelleniyor: başlık/model/muhakeme değişince ve mesaj eklenince (`schema.sql:2735-2780` civarı).
**chat_messages** (`schema.sql:2709`): `id`, `chat_id` (cascade), `author_user_id`, `role`, `content jsonb`, `files jsonb`, `workflow jsonb`, `citations jsonb`, `created_at`, ve bellek damıtma işaretleri (`memory_input_message_id`, `memory_eligible_at`, `memory_app_eligible_at`). Sıralama anahtarı `(chat_id, created_at, id)` (`schema.sql:2727-2728`); tamsayı sıra numarası yok. `tabular_review_chat_messages` benzer ama `annotations jsonb` taşır (`schema.sql:3631`).

**workflows** ailesi: iki ayrı kavram var.
- Kullanıcı iş akışları `workflows` (`schema.sql:1513`): `id`, `user_id`, `title`, `type` (`assistant`/`tabular`), `prompt_md`, `columns_config jsonb`, `language`, `practice`, `jurisdictions text[]`, `visibility`, `archived_at`. Varlıkları (referans dosyalar) artık `documents.workflow_id` ile belge olarak tutuluyor (`schema.sql:~1846`, taşıma `20260901_03_workflow_assets_as_documents.sql`).
- Katalog (Mike'ın dağıttığı hazır iş akışları) `mike_workflows` (`schema.sql:1791`): `workflow_key`, `distribution` (`default`/`addon`), `version`, `title`, `type`, `prompt_md`, `columns_config`, `pack_key...`, `content_hash` (64 hex, içerik adresli), `source_commit`, `active` (aktif anahtar başına tek: kısmi tekil indeks, `schema.sql:~1835`). Aktif katalog tek işlemde değiştiriliyor (`schema.sql:1925` `pg_advisory_xact_lock` ile). `workflow_addons` kullanımdan kalkmış, yalnızca geri dönüş için duruyor (`schema.sql:1869-1872` yorumu).
- Tabular iş akışları, sütun tanımını `columns_config` JSON'unda taşıyor; tablo ayrıştırması yok.

**tabular_reviews** (`schema.sql:2994`): `id`, `project_id`, `user_id`, `title`, `model`, `columns_config jsonb`, `document_ids jsonb`, `workflow_id`, `practice`, `document_grouping` (`document`/`folder`), `active_generation_id`, `generation_lease_expires_at`, `archived_at`, zaman damgaları.
**tabular_review_rows** (`schema.sql:3252`): `id`, `review_id` (cascade), `label`, `row_type` (`document`/`folder`), `folder_id`, `library_folder_id`, `document_id`, `sort_index`. **tabular_review_row_sources** (`3269`): `(row_id, document_id)` birleşik anahtar, `sort_index` (bir satırın kaynak belgeleri, klasör satırı için çoklu).
**tabular_cells** (`schema.sql:3282`): `id`, `review_id`, `row_id` (cascade), `document_id` (cascade, null olabilir), `column_index`, `content text`, `citations jsonb`, `status` (kontrol kısıtı yok; `pending`/`generating`/`done`/`error` kodda kullanılıyor, `runProgress.ts:24-25`), `generation_id`, `created_at`. İndeksler `(review_id, row_id, column_index)` ve `(review_id, document_id, column_index)` (`schema.sql:3373-3377`); hücre için tekillik kısıtı okunmadı (bkz. Açık sorular).

**Üretim kirası (generation lease)** `tabular_reviews` üzerinde: `begin_tabular_review_generation` (`schema.sql:3295`) satırı `for update` ile kilitler; kira sürüyorsa `'running'`, `updated_at` beklenenden farklıysa `'stale'` döndürür, aksi halde kirayı alır (60-3600 sn arasına sıkıştırılmış, varsayılan 300). `renew_...` (3338) ve `finish_...` (3356) yalnızca `active_generation_id = hedef` iken çalışır. Hücre yazmaları üretim kimliğiyle damgalı ve korumalı: üstünü geçen koşu kazananın sonucunu ezemez (`tabular.shared.ts` başlık yorumu; `tabular.shared.ts` 330 civarı). Yenileme 60 sn'de bir (`TABULAR_GENERATION_HEARTBEAT_MS`), kira 300 sn.

**upload_sessions / upload_session_files / upload_processing_jobs** (`schema.sql:1303`, `1380`, `1425`): doğrudan nesne depolamaya yükleme akışının durum makinesi. `upload_sessions`: `purpose` (5 değer), `destination jsonb`, `expected_file_count`, `expected_total_bytes`, `status` (`pending_upload`/`verifying`/`uploaded`/`processing`/...), `expires_at`, `cleaned_at`. `upload_session_files`: `staging_storage_path`, `sealed_storage_path` (her ikisi tekil), `expected_size_bytes` (1..104857600 = 100 MiB sınırı, `schema.sql:~1408`), `observed_size_bytes`, `etag`, `status`, `error_code`, `result jsonb`, `document_created_at`. `upload_processing_jobs`: ikinci bir kuyruk (aşağıda).

**Diğer HakHukuk'la ilgili tablolar**: `memory_files` (kullanıcı ve proje belleği, 16 KiB üst sınırı, `epoch`/`revision` ile karşılaştır-ve-değiştir; `schema.sql:5462-5500`), `memory_consolidation_states`, `memory_conversation_activity`, `memory_conversation_turn_leases`, `memory_consolidation_results` (`schema.sql:5517-5613`); `audit_events` (`schema.sql:5401`: `user_id`, `action`, `status`, `title`, `surface`, `project_id`, `chat_id`, `document_id`, `review_id`, `model`, `detail jsonb`); `schema_migrations` (`schema.sql:8871`).

### 3. Postgres'e özgü özelliklerin dökümü

Aşağıdaki sayılar `grep -ci` satır sayısıdır. Tabloda "SQLite karşılığı" HakHukuk için öneridir (kaynakta değil).

| Özellik | Mike'taki kullanım (satır sayısı) | SQLite'ta karşılığı / çözüm |
| --- | --- | --- |
| `uuid` + `gen_random_uuid()` | 61 | `TEXT` anahtar; uygulama tarafında UUIDv7/ULID üret (zaman sıralı, indeks dostu) |
| `timestamptz`, `now()`, `make_interval` | 22 `make_interval` | Tamsayı epoch-milisaniye (UTC) ya da ISO-8601 metin; aralık hesabı uygulamada, saat enjekte edilir |
| `jsonb` + `jsonb_*` işlevleri | 107 | `TEXT` + `json_valid` CHECK; `json_extract`, `->>` (3.38+); sık sorgulanan alan için ifade indeksi |
| `text[]`, `uuid[]` | 49, 20 | JSON dizi metni ya da birleştirme tablosu; `= any(...)` yerine `IN (SELECT value FROM json_each(?))` |
| `for update` kilitleri | 73 | SQLite'ta satır kilidi yok; yazan işlem veritabanı düzeyinde serileşir. Okuyup yazma gerektiren yollar `BEGIN IMMEDIATE` ile |
| `for update skip locked` | 5 (kuyruk talepleri) | Gerekmez: tek yazar. Atomik talep için tek `UPDATE ... WHERE ... RETURNING` ya da `BEGIN IMMEDIATE` içinde seç-güncelle |
| `pg_advisory_xact_lock`, `pg_try_advisory_xact_lock` | 16 | `BEGIN IMMEDIATE` (genel serileşme), ya da `locks(name PRIMARY KEY, owner, expires_at)` tablosu |
| `security definer` fonksiyonlar | 52 | Gerekmez: tek kullanıcı, rol yok. Uygulama servis katmanındaki fonksiyonlar |
| `plpgsql` / `language sql` fonksiyon | 82 / 72 | Python servis katmanı; atomik gereken yerlerde tek işlem |
| `set search_path` | 136 | Yok |
| RLS + `revoke/grant` | 47 tablo, 0 politika | Gerekmez |
| `auth.users` FK | 56 | `users` tek satır ya da hiç; `user_id` sütunları kaldırılabilir |
| Tetikleyiciler | 40 | SQLite tetikleyicisi var ama plpgsql yok; düz `INSERT/UPDATE` yapanlar taşınır (sürüm temizlik outbox'ı, `updated_at` güncelleme). Karmaşık olanlar servis katmanına |
| `pg_trgm` GIN (`lower(filename) gin_trgm_ops` vb.) | 4 indeks | FTS5 (`tokenize='trigram'`, SQLite 3.34+) ya da `LIKE` + indeks yok (veri küçük) |
| `on conflict`, `returning` | 30, 27 | Desteklenir (`ON CONFLICT` 3.24+, `RETURNING` 3.35+) |
| Kısmi indeks (`where ...`) | çok sayıda | Desteklenir; kısmi tekil indeksler de dahil |
| `lateral`, `unnest`, `array_agg` | 9, 4, 10 | `json_each`, `json_group_array`; yanal birleştirme yerine ilişkili alt sorgu |
| `materialized` | 5 (çoğu yorum olabilir) | Okunmadı; küçük veride önemsiz |
| `alter table ... drop constraint / alter column` | taşımalarda yaygın | SQLite'ta sınırlı: tabloyu yeniden kur ve kopyala (Alembic `batch` kipi) |
| `notify pgrst, 'reload schema'` | compose db-init | PostgREST yok, gerekmez |
| Eklentiler `pgcrypto`, `pg_trgm` | `schema.sql:6-7` | `gen_random_uuid` uygulamada; `pg_trgm` yerine FTS5 |

HakHukuk'a özel gözlem: Mike'ın Postgres özelliklerine bağımlılığının büyük kısmı çok kiracılık ve güvenlik (RLS, `security definer`, advisory lock, hibe tabloları) kaynaklı; tek kullanıcılı SQLite'a geçişte bu katmanın çıkması şemayı kayda değer biçimde küçültür (66 tablonun yarısından fazlası çok kiracılı ya da entegrasyon tabloları; tam oran sayılmadı, tahmin).

### 4. Kuyruk mimarisi: üç ayrı mekanizma

Mike'ta "iş kuyruğu" tek bir şey değil; üç katman var ve karıştırılmamalı.

**A. `db_jobs` ("DB kuyruğu"), varsayılan açık.** İlk tanım `backend/migrations/20260829_01_db_jobs.sql`, güncel hali `schema.sql:5426-5455` ve `6072-6215`. Amaç, kalıcı olması gereken işleri (denetim kaydı, hesap silme, depolama temizliği, dışa aktarma, MCP token yenileme, bellek damıtma, belge temizliği, metin ön hesaplama; bkz. `backend/src/jobs/registry.ts:11-22`) ek altyapı olmadan çalıştırmak (`20260829_01...sql` başlık yorumu).

Alanlar: `id`, `kind`, `payload jsonb`, `status` (`pending`/`running`/`done`/`failed`), `attempts`, `max_attempts` (varsayılan 5, en az 1), `run_at`, `claimed_at`, `finished_at`, `last_error`, `dedupe_key`, `result jsonb`, `created_at`. Kalp atışı, öncelik, çalışan kimliği, iptal durumu sütunu yok.

**B. `upload_processing_jobs`**: yükleme sonrası dosya işleme için ayrı, kira ve kalp atışı olan kuyruk (aşağıda 4.6).

**C. BullMQ (Redis) taşıyıcıları**: Redis varsa (`REDIS_URL` ya da eski `ASYNC_*` bayrakları) anında teslim için. `db_jobs` satırı gerçeğin kaynağı olarak kalır; BullMQ yalnızca satır kimliğini taşır (`appJobsQueue.ts` başlık yorumu; `appJobsWorker.ts:14-26`). Sürücü seçimi `driver.ts:20-28`: açık `QUEUE_DRIVER`, sonra `REDIS_URL`, sonra eski bayraklar, aksi halde `postgres`. Redis'siz kurulumlarda poll döngüsü tek teslim mekanizması. Compose tabanlı yeni kurulumlarda Redis ve `ASYNC_*` varsayılan olarak açık (`docker-compose.yml:304-307`); masaüstü sürümü bunların hiçbirini ayarlamıyor (`supervisor.js:318-351`; `grep ASYNC|REDIS|WORKERS` desktop'ta sonuç vermedi), dolayısıyla masaüstünde sürücü `postgres` ve belge dönüştürme ile tablo çıkarımı `ASYNC_*` kapalıyken istek yolunda eşzamanlı (örn. `tabular.routes.ts:404` `asyncPath` bayrağı) çalışır.

#### 4.1 Talep (claim)

`claim_db_jobs(p_limit, p_stale_seconds)` tek SQL ifadesidir (`schema.sql:6072-6140`). Üç adayı birleştirir: vadesi gelmiş `pending`; bayat `running` (talep zamanı `p_stale_seconds`'tan eski ve deneme hakkı kalmış); `failed` ama türü `storage.cleanup` olan (yeniden canlandırma). Adaylar `run_at` sırasına göre `limit` kadar, `for update skip locked` ile seçilir ve aynı ifadede `running` yapılıp `claimed_at = now()`, `attempts = attempts + 1` yazılır. Önemli: deneme sayısı talep anında artar, tamamlanmada değil; çalışırken çöken bir iş de hakkını harcar, sonsuz çökme döngüsü olmaz (`20260829_01...sql` açıklaması). Hakkı bitmiş bayat satırlar ayrı bir CTE ile `failed`'e çevrilir ("abandoned: worker died mid-run..."), çünkü onları çalıştırıcı kendisi `failed`'e çekemez (`schema.sql:6080-6093`).

Tek satırlık eşdeğer `claim_db_job(p_id, p_stale_seconds)` Redis teslim yolu içindir (`schema.sql:6147-6180`); yinelenen teslim sıfır satır eşleştirir ve yok sayılır.

Çalıştırıcı tarafı (`runner.ts`):
- `CLAIM_BATCH = 5` (satır 64); Redis'siz poll aralığı 5 sn, Redis'liyken 60 sn (yedek) (`runner.ts:40-43`); `DB_JOBS_POLL_MS` ile değişir (en az 250 ms).
- Tikler üst üste binmez: bir tik sürerken sonraki aralık atlanır (`runner.ts:455`). Talep edilen 5 iş `Promise.allSettled` ile paralel yürür, tik hepsi bitince tamamlanır (`runner.ts:345-348`). Sonuç: uzun bir iş aynı gruptaki kısa işlerin ardından sonraki talep turunu geciktirir (grup başı engellemesi); bu sonuç kodun okunmasından çıkarım, ayrıca ölçülmedi.
- Başlangıçta ilk tik 1 sn sonra, ilk temizlik süpürmesi 60 sn sonra (`runner.ts:469, 478`).
- Talep hatası (RPC yok, veritabanı erişilemiyor) için `PollFailureGate`: aynı hata sınıfı bir kez raporlanır, yoklama geri çekilir, tavan 60 sn (`runner.ts:37-62`).

#### 4.2 Kira ve kalp atışı

`db_jobs` için kira süresi diye ayrı bir kavram yok; yalnızca `STALE_SECONDS = 600` (`runner.ts:71`): talep zamanı 10 dakikadan eski `running` satır "çökmüş" sayılır. Kalp atışı yok. Sonuçları: 10 dakikadan uzun süren canlı bir işin yeniden talep edilip ikinci kez çalışması mümkündür; bunun hasarı çit belirteci ile sınırlandırılmıştır (4.3), ama işin kendisi (örn. yan etkili modül çağrısı) çift çalışabilir; tipi belgesi de bunu açık söyler: işlem yapıcılar "en az bir kez" semantiğiyle idempotent olmak zorunda (`types.ts:27-33`). Kalp atışı gerçekten şu iki yerde var:

- `upload_processing_jobs`: `locked_at` kira damgası, `locked_by` çalışan kimliği (`<hostname>:<pid>:<uuid>`, `uploads.processing.ts:1196`); kira 30 dk (`UPLOAD_JOB_LEASE_SECONDS`, satır 94); kalp atışı 60 sn'de bir `locked_at`'ı yeniler ve satır hâlâ `running` ve `locked_by` bizdeysa başarılı sayılır, yoksa `upload_job_lease_lost` fırlatır (`uploads.processing.ts:756-768`). Duvar saati bütçesi 15 dk (varsayılan, 1-60 dk): bütçe aşılınca kalp atışı durur ki takılmış iş çalınabilsin (`runtimeConfig.ts:87-96`, `uploads.processing.ts:858-875`). Sonuç yazmadan önce kira yeniden kanıtlanır (`heartbeatJob` ardışık çağrıları, satır 882-963).
- Tabular üretim kirası: yukarıda (300 sn kira, 60 sn yenileme); extraction işi kendi zamanlayıcısıyla yeniler (`tabular.extraction.ts` ilk 60 satır).

#### 4.3 Çit belirteci (fencing)

Çalıştırıcının sonuç yazan her güncellemesi, satırı "bu talebin bıraktığı haliyle" adresler: `id`, `status='running'`, `attempts = job.attempts`, `claimed_at = job.claimed_at` (`runner.ts:132-154`). Gerekçe yorumda: bayat talep nedeniyle aynı iş iki canlı çalıştırıcıda olabilir; "zombi" geri dönerse, yalnızca `id` ile yazmak, şu anda çalışan işi `done` yapabilir ya da bitmiş işi `pending`'e çekip ikinci kez koşturabilir. Dörtlü, talebi eşsiz tanımladığından yalnızca bir talep sahibi sonlandırabilir. Yani çit ayrı bir token sütunu değil; `attempts + claimed_at` bileşimi. (Önceki not "çit belirteci" demişti: kavram doğru, uygulaması bu.)

#### 4.4 Yeniden deneme, kalıcı hata, ertelenme

Bu davranışlar `processClaimedJob` içinde (`runner.ts:125-310`):
- İşleyici döner, başarılı: `done`, `finished_at`, `last_error=null`, varsa `result` yazılır.
- İşleyici fırlatır, hak kalmışsa: `pending`, `run_at = şimdi + gecikme`, `last_error`. Gecikme üstel: 30 sn × 3^(deneme-1), tavan 30 dk (`runner.ts:83-86`): 30 sn, 90 sn, 270 sn, 810 sn, sonra 30 dk.
- Hak bitmişse ya da `NonRetryableJobError`: `failed` (kalıcı hata). Kural ihlali ("yeniden denemek çözmez") için özel hata sınıfı (`runner.ts:109-114`).
- Bilinmeyen `kind`: hemen `failed` (`runner.ts:157-176`); sürümler arası geçişte yeni türü bilmeyen eski çalıştırıcı satırı bozmasın diye `storage.cleanup`/`document.cleanup` bu kuraldan muaf (`runner.ts:76`, `157`).
- "Ertelendi" (`DbJobDeferredError`): işleyici işi hak harcamadan başka zamana atar; `attempts` bir azaltılır, hata raporlanmaz (`types.ts:20-28`, `runner.ts:222-235, 295-300`).
- Kalıcı hatada alan temizliği için kancalar (`DB_JOB_FAILURE_HOOKS`): `conversion.convert` belgeyi `error`'a çeker, `extraction.extract` hücreleri, `memory.consolidate` bellek durumunu (`jobs/registry.ts:23-27`). Kanca hatası yutulur, satır yine `failed` kalır (`runner.ts:264-279`).
- "Başarana dek yeniden dene" türleri: `storage.cleanup` ve `document.cleanup`. Bunlarda `max_attempts` pratikte sonsuza (2147483647) çekilir, `failed` satırlar bile talep sırasında yeniden canlandırılır ve dedupe anahtarı boşaltılır (`runner.ts:76`, `schema.sql:6110-6128`). Gerekçe: bu iş satırı, meta verisi silinmiş nesnelerin tek kalıcı göstergesidir (`schema.sql:6068-6071` yorumu); silmek baytları sonsuza dek sızdırır.

#### 4.5 Tekilleştirme (dedupe) ve iptal

- Kısmi tekil indeks `db_jobs_dedupe_live_idx (dedupe_key) where dedupe_key is not null and status in ('pending','running')` (`schema.sql:5448-5450`). Biten işin anahtarı serbest kalır. Ekleme sırasında `23505` ihlali, anahtar varsa "zaten kuyrukta" sayılır ve başarı döner; mevcut işin kimliği bulunabilirse döndürülür (`enqueue.ts:52-64`). Yarışsız çünkü indeks zorluyor.
- Örnek anahtarlar: `extract_<review>_<row>[_<kolon>]` (`extractionQueue.ts:82-90`), `mcp.refresh:<connector>` (`workerRuntime.ts:73-78`). `liveDbJobExists` kuyruk varlığını "bu satırın sahibi var" sinyali olarak kullanır (bayat süpürme; `enqueue.ts:94-105`, `tabular.maintenance.ts:112-120`).
- İptal: `cancel_db_jobs(p_dedupe_keys[])`: bekleyenleri siler, çalışanların yüküne `canceled: true` yazar; işleyiciler her (yeniden) talepte bu işaretine bakar (`schema.sql:6192-6212`). Ayrı bir `canceled` durumu yok. Çalışan işi anında durduran bir mekanizma yok; yazma korumaları (üretim kimliği) yarım kalan işin sonuçlarını etkisiz kılar (`extractionQueue.ts:129-153` yorumu).
- Gecikmeli çalıştırma: ekleme sırasında `run_at` verilebilir (`enqueue.ts:11-12`).

#### 4.6 Yükleme işleme kuyruğu (ikinci kuyruk)

`upload_processing_jobs`: durumlar `queued`/`running`/`completed`/`error`, `attempts` 0-10 arası kontrol, ancak talepte `attempts < 3` aranır; `UPLOAD_JOB_MAX_ATTEMPTS = 3` (`uploads.processing.ts:93`). Talep `claim_upload_processing_job` içinde (`schema.sql:5256-5391`):
- Aday küme önce 32 ile sınırlanır; sonra kullanıcı başına adil dağıtım için "o kullanıcının çalışan sayısı" artan sırada seçilir; kullanıcı başı eşzamanlılık üst sınırı 1-64 arası parametre (varsayılan çağrı değeri `UPLOAD_PROCESSING_MAX_RUNNING_PER_USER`, varsayılan 2, işçi sayısını aşamaz; `runtimeConfig.ts:53-67`).
- Sayma ve talep kararı, kullanıcı başına `pg_try_advisory_xact_lock` ile serileşir; çakışma yalnızca bir sonraki yoklamaya erteler (`schema.sql:5337-5343`).
- İşçi sayısı varsayılan 8, üst sınır 64 (`runtimeConfig.ts:56-59`); her işçi bağımsız bir yoklama döngüsü, boştaysa 1 sn, hatada 30 sn'ye kadar geri çekilme, ilk işçi dakikada bir temizlik yapar (`uploads.processing.ts:1181-1290`).
- Yeniden deneme: başarısız dosya işinde `queued`'a döner, `available_at = şimdi + deneme × 5 sn` (`uploads.processing.ts:~978`); silinmiş belge ve değişmiş belge hataları yeniden denenmez (satır ~975).
- Temizlik: süresi dolan oturumlar, doğrulama zaman aşımı, hak bitmiş bayat işler `retry_limit_exceeded` ile `error`'a (`uploads.processing.ts:1040-1100`); 7 gün sonra oturum silinir (`UPLOAD_SESSION_RETENTION_MS`, satır 99).

#### 4.7 Temizlik / saklama

`runDbJobRetentionSweep` saatte bir (ve açılışta 60 sn sonra): biten `export.build` işlerinin dosyasını, 24 saat dolunca, satırdan önce siler (dosya silinemezse satır kalır, sonraki süpürme yeniden dener); `done` satırları 7 gün, `failed` 30 gün sonra silinir, ama `export.build` (yukarıdaki yolla silinir) ve `storage.cleanup`/`document.cleanup` (başarana dek tutulur) istisna; en son `memory_consolidation_results` makbuzları temizlenir (`runner.ts:359-432`). Sabitler: `DONE_RETENTION_MS` 7 gün, `FAILED_RETENTION_MS` 30 gün, `SWEEP_EVERY_MS` 1 saat (`runner.ts:73-75`).

Ayrıca bayat iş süpürmesi (`runStaleWorkSweep`, her 10 dk, açılıştan 30 sn sonra; `workerRuntime.ts:30-33, 108-125`, `jobs/maintenance.ts:8-26`): `processing` kalmış belgeleri ve `generating` kalmış tablo hücrelerini `error`'a çeker; kuyruk açıksa "bu iş için canlı bir iş satırı var mı?" diye sorar (`documents.maintenance.ts:63-100`, `tabular.maintenance.ts:92-120`). Hücre süpürmesi yalnızca `ASYNC_TABULAR_EXTRACTION=true` iken çalışır (`tabular.maintenance.ts:92`).

#### 4.8 Öncelik ve etkileşimli/toplu ayrımı

Öncelik yok. `db_jobs` talebi `order by run_at` (`schema.sql:6097`); `upload_processing_jobs` için `available_at, created_at` ve kullanıcı adaleti. Kaynaktaki `priority` araması `lib/dbq`, `lib/queue`, `workers`, `jobs` içinde sonuç vermedi.

Etkileşimli ile toplu ayrımı kuyrukla değil, yolla yapılıyor: sohbet yanıtları (etkileşimli) kuyruğa hiç girmez. "Sunucu sahipli akış koşuları" (`streamRuns.ts`) bellekte tutulur: koşu istekten bağımsızdır, kare tamponu yeniden bağlanana tekrar oynatılır, bitmiş koşu 60 sn tutulur, üst süre 4 saat, boşta zaman aşımı 5 dk, aynı anahtarla tek koşu (`chat:<id>`, `review:<id>`), kapsam tek süreç (`streamRuns.ts:1-45`). Kuyruk yalnızca arka plan işlerini taşır. Eşzamanlılık sınırları ayrıca: kullanıcı başı yükleme sınırı, dönüştürme işçisi eşzamanlılığı 2 ve app-jobs işçisi 5 (BullMQ'da; `conversion.transport.ts:26`, `appJobsWorker.ts:68`), LibreOffice işlem başı zaman aşımı 120 sn (varsayılan; 10-600 sn; `runtimeConfig.ts:73-82`), her dönüşüm için ayrı geçici profil dizini (`convert.ts:178-182`).

Çıkarım: GPU gibi kıt bir kaynağa bağlı eşzamanlılık denetimi Mike'ta yok (LLM'ler uzak API'ler); bu HakHukuk'un özgün tasarım ihtiyacıdır (bölüm "Önerilen tasarım").

### 5. Çalışan süreçler

`backend/src/index.ts:45-59`: çalışma konumu `WORKERS_MODE`:
- `thread` (varsayılan): arka plan işi, API sürecinin içinde bir `worker_thread`'de çalışır; CPU yoğun işin HTTP olay döngüsünü aç bırakmasını önler. Çökerse 5 sn sonra yeniden başlatılır (`index.ts:87-105`); dayanak, kalıcı durumun (db_jobs, Redis) kayıpsız olması.
- `inline`: ana iş parçacığında (eski davranış, kaçış kapısı).
- `none`: bağımsız süreç (`node dist/worker.js`); aynı Postgres/Redis'e bağlı birden çok örnek güvenle çalışır (`docs/deployment.md` "Background jobs" bölümü).

Başlatma sırası (`index.ts:110-140`): yapılandırma doğrulama; belge yaşam döngüsü taşımasının uygulandığını RPC ile kanıtla, yoksa süreci sonlandır (`lifecycleGuard.ts`; 6 deneme, 250 ms'den 4 sn'ye üstel bekleme; kanıtlanamazsa kapalı kalma); portu bağla; sonra işçileri başlat. Gerekçe: kod önce yayınlanırsa silmeler "başarılı" olur ama baytların yerini kaydeden tetikleyici olmadığından nesneler kayıtsız yetim kalır (`lifecycleGuard.ts` başlık yorumu). `REQUIRED_LIFECYCLE_VERSION = 2` (satır 56 civarı).

`startAllWorkers` (`workerRuntime.ts:84-137`): (1) BullMQ işçileri, yalnızca Redis sürücüsü ve ilgili bayrak açıksa (`registry.ts:42-69`); (2) `db_jobs` çalıştırıcısı her koşulda; (3) yükleme işleme işçileri; (4) bayat iş süpürmesi; (5) MCP token yenileme süpürmesi (5 dk). Kapanış: `SIGTERM/SIGINT`, yeni bağlantı kabulünü durdur, akışları boşalt, arka planı durdur (işçi iş parçacığına `shutdown` mesajı, 10 sn zaman aşımı), `exit 0` (`index.ts:144-176`). `stopDbJobRunner` zamanlayıcıları durdurur ve uçuştaki tik'i bekler (`runner.ts:486-494`); uçuştaki bir iş yarıda bırakılırsa bayat süresi dolana dek (600 sn) yeniden talep edilmez; bunun için kapanışta bir "serbest bırak" adımı okunan kodda yok.

Her işleyici `Db` ve `job` alır (`types.ts:30-33`); `kind -> işleyici` eşlemesi tek bir kayıt dosyasında (`jobs/registry.ts`). Yeni kuyruk eklemek için tek tanımlayıcı eklenir (`registry.ts:36-41` yorumu).

### 6. Taşıma (migration) stratejisi

- İki kaynak: `backend/schema.sql` (tam, güncel şekil) ve `backend/migrations/*.sql` (136 dosya, `YYYYMMDD_NN_ad.sql`, bayt sırasına göre). Taze kurulum `schema.sql` çalıştırır; o da kendi içerdiği her taşımayı `schema_migrations` defterine yazar (`docs/deployment.md` "Fresh install"; `schema.sql:8865-8878`).
- Defter: `schema_migrations(filename pk, checksum, applied_at)` (`schema.sql:8871-8875`); `migrate.sh` komutları `status`, `up`, `baseline`, `mark`; her dosya kendi işleminde defter satırıyla birlikte; danışma kilidi ile ikinci çalıştırıcı bekler; değişen/yeniden adlandırılan dosya uyarısı (`backend/scripts/migrate.sh:1-45`, `docs/deployment.md:18-90`). `create index concurrently` ya da `-- migrate:no-transaction` içeren dosyalar işlem dışı; başarısızlıkta kısmi uygulanma olabilir.
- Uyumluluk testi: CI'da "schema-drift" (sabit eski bir tabana `migrate.sh` ile yükseltilmiş veritabanı, taze kuruluma yakınsamalı; `docs/deployment.md:105-111`), ve `migrationLedger.test.ts` yeni taşıma dosyasının listeye eklenmesini zorunlu kılıyor (`schema.sql:8865-8869` yorumu).
- Masaüstü ayrı bir çalıştırıcı kullanıyor: `desktop/src/local/schema.js:84-137`. Kendi defteri `mike_schema_migrations(name, applied_at)`; taze veritabanında `schema.sql` + tüm taşımaları "uygulanmış" kaydeder; mevcut veritabanında eksik taşımaları sırayla uygular; `CONCURRENTLY` gibi işlem bloğunda reddedilen ifadeler için dosyayı ifade ifade yeniden dener (SQLSTATE 25001; `sql.js` başlık yorumu); sonra `service_role` izinlerini yeniden verir; son olarak kendi defterini `public.schema_migrations`'a yansıtır (`schema.js:128-135`). Bu çalıştırıcı her açılışta çalışır (`supervisor.js:281`). Önce yedek alma adımı bulunmadı (aşağıda).
- Veritabanı sürümü ile kod sürümü uyumsuzluğuna karşı iki koruma: açılışta yaşam döngüsü sürümü kontrolü (`lifecycleGuard.ts`), ve yeni taşımaların önceki taşımaya bağımlılığını kontrol edip "şu dosya eksik" diyerek durması (`docs/deployment.md:118-126`).

### 7. Masaüstü (Electron) paketi

**Ne olduğu.** Electron kabuğu aynı web uygulamasını ve backend'i, `docker-compose.yml`'in süreç ağacı olarak yeniden uygulanmış haliyle çalıştırıyor (`supervisor.js:1-14`). Kabuk tarayıcıya ayrıcalıklı API vermiyor.

**Yaşam döngüsü** (`supervisor.js:199-380`, `main.js:565-590, 795-840`):
1. Tek örnek kilidi: `app.requestSingleInstanceLock()`; ikinci başlatma ilk pencereyi öne alır (`main.js:795-806`). Pencere kapanınca uygulama dock'ta kalır (Mac geleneği); `Cmd+Q` çıkış.
2. Yerel mod seçimi: ilk açılışta karşılama ekranı (Bu Mac'te başlat / Bulut / kendi sunucum); seçim `userData/settings.json`'a kaydedilir (`README.md` "Overrides").
3. Başlatma sırası ve bekleme: Postgres, GoTrue, şema/taşıma ve paketli iş akışları, PostgREST, ağ geçidi (süreç içi Node proxy), backend, Next standalone frontend. Her adımdan sonra `waitFor` (varsayılan 60 sn, GoTrue 120 sn, 400 ms aralık); bir alt süreç beklerken ölürse hızlı hata ve hangi günlüğe bakılacağı (`supervisor.js:76-96`). Backend ve frontend, Electron'un kendi ikilisiyle `ELECTRON_RUN_AS_NODE=1` ile çalıştırılıyor; ayrı Node dağıtılmıyor (`supervisor.js:314-320, 357-361`). Backend `WORKERS_MODE` verilmediği için varsayılan `thread` kipinde çalışır (çıkarım: `supervisor.js` env bloğunda yok).
4. İlk çalıştırma: `initdb` (scram-sha-256, parola dosyası geçici ve 0600), sonra roller (`anon`, `authenticated`, `service_role` bypassrls, `supabase_auth_admin`, `authenticator`); GoTrue kendi taşımalarıyla `auth.users` oluşturur; sonra `schema.sql` (`supervisor.js:172-190, 232-290`; `schema.js:49-69`). README'ye göre ilk açılış yaklaşık bir dakika (`supervisor.js:36-38` yorumu: "about a minute").
5. Bayat `postmaster.pid`: süreç canlı değilse silinir (`supervisor.js:216-227`).
6. Port çakışması: sabit portlar 42810-42815 (postgres 42810, gotrue 42811, postgrest 42812, ağ geçidi 42813, backend 42814, frontend 42815; `config.js:9-16`); çakışmada başlatma hata verir (`config.js` başlık yorumu), ağ geçidinin `listen` hatası yukarı fırlatılır (`gateway.js:58-61`); alternatif port aranmaz. Tümü `127.0.0.1`'e bağlanır.
7. Kapanış: `before-quit` ilk çıkışı durdurur, `stopLocalStack` çağırır, bitince gerçekten çıkar (`main.js:824-836`). Ters sırayla: Postgres'e `SIGINT` (hızlı ve temiz kapanış), diğerlerine `SIGTERM`; 10 sn'de hâlâ canlı olana `SIGKILL` (`supervisor.js:382-408`). Açılış sürerken çıkış da çocukları durdurur (`aborted` bayrağı).
8. Açılış sonrası izleme: `running = true` olduktan sonra alt süreç ölümüne bakan bir dinleyici ya da yeniden başlatıcı okunan kodda yok (`supervisor.js` içinde `exit` olay dinleyicisi aranıp bulunmadı); `hasExited` yalnızca bekleme ve durdurma yollarında kullanılıyor. Yani çalışırken çöken bir alt süreç (örneğin Postgres) kullanıcıya yalnızca bozuk sayfa olarak yansır; bu bir gözlem, test edilmedi.

**Veri dizini.** `userData/local/` altında: `pgdata/` (Postgres), `storage/` (belgeler, düz dosya, backend `STORAGE_DRIVER=fs`, `STORAGE_FS_ROOT`), `logs/` (her servis ayrı günlük), `secrets.json` (kuruluma özgü JWT sırrı, anon/service anahtarları, veritabanı parolası, indirme imza sırları, yerel misafir kimlik bilgileri); `userData` macOS'ta `~/Library/Application Support/Mike` (`config.js:46-55`, `secrets.js` başlık yorumu, `desktop/README.md`). Test için `MIKE_USER_DATA_DIR`. Sır dosyası düz JSON; yorum, `pgdata` ile aynı güven sınırında olduğunu söylüyor (`secrets.js:11-13`).

**Depolama.** Dosya sistemi sürücüsü: S3 istemcisi yerine yerel dizin, aynı genel API (`storage.ts:32-47`); anahtar dizin dışına çıkamaz (`storage.ts:~84`); akış yazımı geçici dosyaya, başarıda `rename` (`storage.ts:~658-690`); indirme URL'leri süreli HMAC jetonlu backend yolu (S3 ön imza yerine).

**Güncelleme.** Okunan kodda otomatik güncelleme yok: `autoUpdater` / `electron-updater` araması hem `main.js` hem `electron-builder*.json` içinde sonuçsuz. Güncelleme = yeni uygulama paketiyle değiştirmek; veri `userData` altında kaldığından, yeni sürüm açılışta `schema.js` ile taşımaları uygular. Plan belgesinde "Back Up Local Data" menüsü ve `pg_dump` (Phase 3) öngörülmüş, ancak `desktop/src` ve `scripts` içinde `pg_dump`/`backup` araması sonuçsuz; yani uygulanmamış görünüyor. Postgres ana sürümünü uzun süre sabit tutma kararı planda geçiyor (`self-contained-plan.md` Phase 3), `pg_upgrade` yolu yok.

**Paketleme.** `electron-builder.local.json`: `local-stack` dizini `extraResources` olarak pakete konur, hedef `dir` ve imzasız (`identity: null`); imzalı yol için ayrıca üretilen yapılandırma gerekiyor, çünkü notarizasyon her iç içe Mach-O için ayrı imza ister (postgres + dylib'ler, gotrue, postgrest, `.node` modülleri; `desktop/README.md` "Signing the self-contained build"). Hedef platform Apple Silicon (`README.md`). Boyut bütçesi planda: Electron ~250 MB, kurulum 600-700 MB, DMG 250-350 MB (LibreOffice hariç; `self-contained-plan.md` Phase 2); bunlar plandaki tahminler, ölçüm değil. LibreOffice paketlenmez, `/Applications/LibreOffice.app` varsa kullanılır (`supervisor.js:192-195`, 350).

**Yerel mod davranış kararları** (`supervisor.js:243-266, 335-349`): e-posta onayı otomatik (SMTP yok, parola sıfırlama yok); hız sınırları pratik olarak kapatılmış (tek kullanıcı, loopback); kabuk ortamından kimlik bilgisi sızdırılmaz (`environment.js:4-17`: yalnızca HOME, PATH, TMPDIR, LANG vb. geçer; Sentry kapalı). Dikkat: `docs/local-development.md` tersine, Compose yığınında e-posta onayı varsayılan olarak zorunlu (satır 47-65), masaüstü planı ise otomatik onay diyor; ikisi farklı yığın.

## HakHukuk için değerlendirme

### Taşınabilir (kavram olarak, kod olarak değil)

- **Dayanıklı "outbox" kalıbı.** Veri satırı silinirken baytların yeri bilgisini aynı işlemde bir iş satırına yazmak (`schema.sql:8004-8017`) ve bu işi "başarana dek yeniden dene" sınıfına almak. HakHukuk'ta belge sürümü silme/ezme ile dosya silme arasında çökme olursa dosya sızmasın diye değerli. SQLite'ta düz `INSERT` yapan bir tetikleyiciyle ya da servis katmanında aynı işlemde yazarak karşılanır.
- **Çit belirteci ile sonlandırma.** `id + status + attempts + claimed_at` yerine, her talepte rastgele `claim_token` üretmek daha açık; ama kavram aynı: sonuç yazan yalnızca güncel talep sahibi olabilir (`runner.ts:132-154`).
- **Talepte deneme artırma.** Çöken işin hakkını harcaması, sonsuz çökme döngüsünü önler. Yerel LLM süreci OOM ile ölebileceğinden (VRAM sınırı) bu doğrudan geçerli.
- **Kısmi tekil indeksle dedupe**, SQLite'ta aynen çalışır.
- **Kalıcı hata sınıflaması** (`NonRetryableJobError`, bilinmeyen tür, "ertelendi" hata sınıfı).
- **Üstel geri çekilme** 30 sn × 3^n, tavan 30 dk, aynen kullanılabilir; yerel çalışmada başlangıcı daha kısa seçmek makul (öneri).
- **Tabular üretim kirası + hücre başına `generation_id` damgası.** Aynı incelemeyi iki koşunun ezmesini önler; SQLite'ta `UPDATE ... WHERE active_generation_id = ?` ve `changes()` ile birebir uygulanır.
- **Sürüm modeli:** her düzenleme yeni sürüm satırı, `current_version_id` işareti, yumuşak silme, `content_sha256`, `textless_page_count`. Hukuk metninde "asistan düzenlemesi / kullanıcı kabulü / reddi" kaynağı (`source`) izlenebilirlik için değerli.
- **`document_edits` modeli** (önerilen değişiklik başına bir satır, kabul/ret durumu) ve `document_versions.source` değerleri.
- **Sunucu sahipli koşu + tekrar oynatma tamponu** (`streamRuns.ts`): yenileme ya da ikinci sekme akışı kesmesin. Aynı anda birden çok ajan koşusu gereksinimimize uyuyor; ancak bellek içi olduğu için süreç yeniden başlayınca kaybolur (aşağıda yeniden tasarım).
- **Tek dosya depolama ilkeleri:** geçici dosyaya yaz + `rename`, anahtarın kök dışına çıkmasını engelleme, içerik adresli (sha256) denetim.
- **Taşıma defteri + açılışta uygulama + sürüm kapısı** disiplini.
- **Uzak LLM'e karşı yerel Ollama tarzı model keşfi** bu dilim dışında; not düşmek için anıldı.

### Yeniden tasarlanmalı

- **Kalp atışı/kira `db_jobs` düzeyinde.** Yerel LLM işleri dakikalarca sürebilir; 600 sn bayatlık eşiği ve kalp atışsızlık, canlı işin yeniden talep edilmesine yol açar. HakHukuk'ta her `running` iş `lease_until` taşımalı ve işçi kalp atışı atmalı (öneri, aşağıda).
- **Öncelik ve şeritler.** Mike'ta yok; HakHukuk'ta yerel GPU kıt olduğundan etkileşimli sohbet ile toplu iş (örn. çok belgelik tablo çıkarımı) arasında ayrım şart.
- **Kaynak kısıtı (GPU yuvası).** Mike'ın tek kısıtı kullanıcı başı yükleme sınırı ve işçi sayısı; bizim kısıt cihaz kaynağı.
- **Talep turunda grup başı engellemesi.** Mike'ta 5'lik grup bitene dek yeni talep yok (`runner.ts:345-348, 455`). Bizde işçi başına sürekli döngü (biten işçi hemen yeni iş çeker) daha uygun.
- **Süreç yeniden başlatmada koşu kaybı.** Bellek içi koşu tamponu ve "yalnızca tek süreç" varsayımı; HakHukuk'ta ajan koşusu durumu (adım, tool çağrıları, kare günlüğü) SQLite'ta tutulmalı ki uygulama çökmesinden sonra devam/yeniden oynatma mümkün olsun.
- **Çok kiracılı alt şema.** Kurum, hibe, davet, paylaşım, MCP/Google tabloları HakHukuk'ta yok; şemadan çıkarılır. Yerine yalnızca `settings` ve yerel model uç noktası kaydı gelir.
- **Yükleme oturumu (staging/sealed/etag).** S3'e doğrudan yükleme modeli; yerelde dosyayı doğrudan yazmak yeter. Korunacak olan "içerik özetiyle doğrulama" fikri; `upload_sessions` ailesi çıkar.
- **Taşıma aracı.** `psql` + `migrate.sh` yerine, SQLAlchemy kullanılıyorsa Alembic (SQLite için `batch` kipi), kendi defter tablosu ve sağlama toplamıyla. Mike'ın kayıtlı-kalıp "schema.sql tam + migrations artımlı + CI'da yakınsama testi" yaklaşımı iki kaynağı eşit tutma maliyeti getirir (136 dosya, 10 bin satır şema); tek kaynak (yalnızca artımlı taşıma, taze kurulum hepsini uygular) SQLite için daha ucuz.
- **Yükseltmeden önce yedek.** Mike masaüstünde bulunamadı; SQLite'ta tek dosya olduğundan `VACUUM INTO` ya da yedek API ile taşımadan önce otomatik kopya ucuz ve zorunlu olmalı.
- **Açılış sonrası süreç gözetimi.** Bizde tek süreç (FastAPI + SQLite) olacağı için çocuk-süreç ağacı gereksiz; ancak llama-server (ayrı süreç) gözetilmeli: sağlık yoklaması, ölünce yeniden başlatma, bağlı `running` işleri yeniden kuyruğa alma.

### Taşınmaz / gereksiz

- Postgres, GoTrue, PostgREST, Supabase istemcisi, ağ geçidi proxy'si, RLS/rol merdiveni, `security definer` fonksiyon katmanı, `auth.users` bağımlılığı.
- Redis/BullMQ teslim katmanı ve Redis pub/sub ilerleme akışı (tek süreçte bellek içi olay + SQLite günlüğü yeter).
- Kurum, paylaşım, hibe, davet, denetim dışa aktarımı, MCP bağlayıcıları, Google Workspace, CourtListener (ABD içtihadı) tabloları.
- Word eklentisi tabloları (`word_*`).
- Kod imzalama/notarizasyon ve üç parça ikili (postgres/gotrue/postgrest) paketleme yükü. HakHukuk masaüstü paketi, Python + SQLite ile belirgin biçimde daha hafif olur.

## Önerilen tasarım (SQLite, tablo ve alan düzeyinde)

Bu bölüm kaynaktan çıkarılan öneridir; kodu SQL olarak yazılmamıştır. Genel kurallar: tek veritabanı dosyası `veri_dizini/hakhukuk.db`; her bağlantıda `foreign_keys=ON`, `journal_mode=WAL`, `busy_timeout` (örn. 5 sn), `synchronous=NORMAL`; yazan işlemler kısa; talep ve kira işlemleri `BEGIN IMMEDIATE`; tablolar `STRICT`; kimlikler `TEXT` (UUIDv7/ULID); zamanlar tamsayı UTC epoch-milisaniye; JSON alanları `TEXT` + `json_valid` kontrolü; şema sürümü `PRAGMA user_version` ve `schema_migrations` tablosunda.

### Çekirdek tablolar

| Tablo | Alanlar (tür) | Notlar |
| --- | --- | --- |
| `schema_migrations` | `name` (text pk), `checksum` (text), `applied_at` (int) | Mike'ın defteriyle aynı fikir (`schema.sql:8871`) |
| `settings` | `key` (text pk), `value_json` (text) | model uç noktaları, GPU yuvası, dil vb. |
| `projects` | `id` (pk), `name`, `case_no` (null), `practice` (null), `created_at`, `updated_at`, `archived_at` (null) | Mike'taki `cm_number` karşılığı `case_no`; kurum/görünürlük yok |
| `folders` | `id` (pk), `project_id` (fk cascade, null = kütüphane), `parent_id` (fk null), `name`, `sort_index` | Mike'ta iki ayrı tablo (`project_subfolders`, `library_folders`); tek tabloya indirilebilir (öneri) |
| `documents` | `id`, `project_id` (null), `folder_id` (null), `kind` (`file`/`template`/`reference`), `status` (`pending`/`processing`/`ready`/`error`), `current_version_id` (fk null, set null), `created_at`, `updated_at`, `archived_at` | Ad ve tür sürümde (Mike gibi) |
| `document_versions` | `id`, `document_id` (fk cascade), `version_number` (int), `source` (`upload`/`assistant_edit`/`user_accept`/`user_reject`/`generated`), `rel_path` (dosya sistemi göreli yol), `pdf_rel_path` (null), `filename`, `file_type`, `size_bytes`, `page_count`, `textless_page_count`, `content_sha256`, `created_by_job_id` (null), `deleted_at` (null), `created_at` | tekil `(document_id, version_number)`; silinmemişler için kısmi indeks; yumuşak silme |
| `document_edits` | `id`, `document_id`, `version_id`, `message_id` (null), `change_id`, `deleted_text`, `inserted_text`, `context_before`, `context_after`, `status` (`pending`/`accepted`/`rejected`), `created_at`, `resolved_at` | `document_edits` modelinin aynısı |
| `chats` | `id`, `project_id` (null), `title`, `model`, `reasoning_level`, `created_at`, `updated_at`, `archived_at` | `updated_at` servis katmanında (ya da düz tetikleyici) |
| `chat_messages` | `id`, `chat_id` (cascade), `seq` (int), `role`, `content_json`, `files_json`, `citations_json`, `workflow_json` (null), `run_id` (null), `created_at` | tekil `(chat_id, seq)`; Mike zaman damgasına güveniyor, `seq` sıralamayı açık yapar (öneri) |
| `workflows` | `id`, `origin` (`builtin`/`user`), `type` (`assistant`/`tabular`), `title`, `prompt_md`, `columns_json`, `language`, `jurisdictions_json`, `content_hash`, `active`, `created_at` | `mike_workflows` ve `workflows` tek tabloya (öneri); yerleşikler `content_hash` ile eşitlenir |
| `workflow_assets` | `workflow_id`, `document_id` | Mike'ta varlıklar belge olarak (`documents.workflow_id`); burada birleştirme tablosu |
| `tabular_reviews` | `id`, `project_id` (null), `title`, `model`, `columns_json`, `workflow_id` (null), `grouping`, `active_generation_id` (null), `generation_lease_until` (null, int), `created_at`, `updated_at`, `archived_at` | kira alanları Mike'tan |
| `tabular_rows` | `id`, `review_id` (cascade), `label`, `row_type`, `folder_id` (null), `document_id` (null), `sort_index` | |
| `tabular_row_sources` | `row_id`, `document_id`, `sort_index` | pk `(row_id, document_id)` |
| `tabular_cells` | `id`, `review_id`, `row_id` (cascade), `column_index`, `content`, `citations_json`, `status` (`pending`/`generating`/`done`/`error`), `generation_id` (null), `updated_at` | tekil `(row_id, column_index)` (öneri; Mike'ta kısıt okunmadı) |
| `agent_runs` | `id`, `kind` (`chat_turn`/`tabular_cell`/`workflow`/...), `chat_id` (null), `review_id` (null), `job_id` (null), `status`, `model`, `started_at`, `finished_at`, `error` | koşu özeti; ayrıntı olaylarda |
| `run_events` | `run_id` (fk cascade), `seq` (int), `type`, `data_json`, `created_at` | pk `(run_id, seq)`; Mike'ın bellek içi kare tamponu yerine kalıcı günlük; yeniden bağlanana `seq > son görülen` oynatılır |
| `audit_events` | `id`, `created_at`, `action`, `status`, `project_id`, `chat_id`, `document_id`, `model`, `detail_json` | isteğe bağlı, Mike'taki gibi |
| `notes` / bellek | `id`, `scope` (`user`/`project`), `project_id` (null), `content`, `revision`, `updated_at` | Mike'ın `memory_files`'ı (üst sınır 16 KiB) isteğe bağlı; hukuk kullanımında önce gerekçe sorulmalı |

Hukuki metin kaynakları (mevzuat korpusu, indeks) bu veritabanında değil; ayrı salt-okunur korpus/indeks (HakHukuk CLAUDE.md'deki `data/index/...`) kalır. Mike şemasında karşılığı yok.

### `jobs` tablosu

Alanlar:

| Alan | Tür | Açıklama |
| --- | --- | --- |
| `id` | text pk | ULID/UUIDv7 |
| `kind` | text | işleyici seçici (`agent.chat_turn`, `tabular.cell`, `document.convert`, `document.cleanup`, `index.refresh`, `export.build`, ...) |
| `lane` | text | `interactive` ya da `batch` |
| `priority` | int | aynı şerit içinde büyük olan önce (varsayılan 0) |
| `resource` | text | `gpu`, `cpu`, `io` ya da `none` |
| `slots` | int | kaynaktan kaç yuva tutar (varsayılan 1) |
| `payload_json` | text | işe özgü girdi (sır içermez) |
| `status` | text | `pending`, `running`, `done`, `failed`, `canceled` |
| `attempts` | int | talepte artar (Mike gibi) |
| `max_attempts` | int | varsayılan 5; temizlik türleri için çok büyük |
| `run_at` | int | en erken çalışma zamanı (geri çekilme buraya yazılır) |
| `claim_token` | text null | her talepte yeni rastgele değer; sonuç yazarken çit |
| `claimed_by` | text null | işçi kimliği (`pid:önyükleme_kimliği:n`) |
| `boot_id` | text null | talep eden süreç örneği; yeniden başlatmada yetim tespiti |
| `claimed_at` | int null | |
| `heartbeat_at` | int null | |
| `lease_until` | int null | kira bitişi |
| `finished_at` | int null | |
| `last_error` | text null | |
| `error_class` | text null | `retryable`, `non_retryable`, `deferred` |
| `dedupe_key` | text null | |
| `cancel_requested` | int (0/1) | işbirlikçi iptal |
| `subject_type`, `subject_id` | text null | ilgili nesne (belge sürümü, tablo hücresi, sohbet); bayat süpürme ve arayüz için |
| `result_json` | text null | |
| `created_at` | int | |

İndeksler (kısmi): talep için `(lane, priority desc, run_at)` `where status='pending'`; `(lease_until)` `where status='running'`; tekil `(dedupe_key)` `where dedupe_key is not null and status in ('pending','running')`; saklama için `(finished_at)` `where status in ('done','failed','canceled')`; `(subject_type, subject_id)`.

Akış (öneri):
1. **Ekleme**: `INSERT`; dedupe ihlalinde (`IntegrityError`) "zaten kuyrukta", mevcut kimlik döner (Mike: `enqueue.ts:52-64`).
2. **Talep**: `BEGIN IMMEDIATE` içinde (a) süresi dolan kiralar için: `lease_until < şimdi` olan `running` satırlar, hak kaldıysa `pending` (`run_at` geri çekilmeli), değilse `failed`; (b) uygun adayı seç: `pending` ve `run_at <= şimdi`, `lane/priority/run_at` sırasıyla, kaynak yuvaları uygunsa (aşağıda), (c) `running` yap, `attempts+1`, yeni `claim_token`, `claimed_by`, `boot_id`, `claimed_at = heartbeat_at = şimdi`, `lease_until = şimdi + kira`. İşçi, biten işten hemen sonra yeni talep eder (grup beklemez); boştaysa kısa uyku ya da süreç içi olay (aynı süreçte yeni ekleme uyandırır; Mike'ın 5 sn yoklamasından farkı).
3. **Kalp atışı**: kira/3 aralıkla `lease_until` ileri alınır; `WHERE id=? AND claim_token=? AND status='running'`; satır sayısı 0 ise kira kaybedildi, işçi işi bırakır (Mike'ın `upload_job_lease_lost` kalıbı, `uploads.processing.ts:756-768`). Duvar saati üst sınırı Mike'ta olduğu gibi: sınırı aşan işte kalp atışı durur.
4. **Sonuç yazma**: aynı `claim_token` çiti; başarı `done` (+ `result_json`); hata `pending` + geri çekilme (30 sn × 3^(deneme-1), tavan 30 dk; Mike ile aynı) ya da `failed`; `deferred` hatası hak harcatmaz (`attempts-1`). Kalıcı hatada alan kancası (belgeyi `error`, hücreyi `error`).
5. **Açılışta yetim kurtarma**: tek süreçli kurulumda önceki `boot_id`'ye ait tüm `running` satırlar sahibi artık yok demektir; kira bitişini beklemeden hemen `pending`'e al (hak harcamadan ya da harcayarak; çökmeye neden olan iş için hak harcamak daha güvenli, Mike'ın gerekçesi). Bu, Mike'ın 600 sn bekleyişinden daha iyi bir yerel davranış (öneri).
6. **Zarif kapanış**: yeni talep dur; uçuştaki işlere süre ver; hâlâ süren `running` işleri hak harcatmadan `pending`'e geri koy.
7. **İptal**: `pending` ise `canceled`; `running` ise `cancel_requested=1`, işleyici iş birimi arasında bakar (hücre/belge/araç çağrısı sınırı). Önceden kesme yok (Mike'ta da yok).
8. **Saklama**: Mike değerleri başlangıç olarak makul (done 7 gün, failed 30 gün; `runner.ts:73-74`), ama `run_events` ve `result_json` içindeki yapıtlar için ayrı süre. Dosya yapıtı olan işlerde (dışa aktarma) dosya önce, satır sonra silinir (`runner.ts:359-401`).
9. **Outbox**: sürüm silme/güncelleme tetikleyicisi ya da servis katmanı, aynı işlemde `document.cleanup` işi ekler; bu tür "başarana dek" sınıfındadır ve `failed` kalsa bile süpürülmez.

### GPU yuvası sayısına bağlı eşzamanlılık sınırı

Mike'ta karşılığı yok; aşağısı tasarım önerisidir ve test edilmemiştir.

- Yapılandırma: `gpu_slots = G` (tamsayı). `G`, yerel çıkarım sunucusunun aynı anda yürüttüğü istek sayısıyla (llama-server için `--parallel`/yuva sayısı) eşitlenir; bağlam penceresi yuvalara bölündüğünden `G` büyüdükçe yuva başına bağlam küçülür (bunun tam modeli doğrulanmadı; CLAUDE.md'deki ~12 GB VRAM, 4B Q4_K_M ile `G` küçük, örn. 1-2, olmalı; kesin değer ölçümle belirlenir, tahmin).
- İki katmanlı sınır: (1) iş düzeyi: aynı anda çalışabilecek `running` iş sayısı, kaynak başına `SUM(slots) <= kapasite` (talep işleminin içinde sayılır, `BEGIN IMMEDIATE` yarışı kapatır). (2) istek düzeyi: bir ajan koşusu uzun süreli, ama GPU'yu yalnızca üretim çağrısı boyunca kullanır (araç çalıştırma, belge okuma sırasında kullanmaz). Bu yüzden koşu işinin kendisi `resource='none'` (ya da çok büyük bir "koşu sayısı" kapasitesi) tutsun; GPU yuvası, süreç içi öncelikli bir semafor ile her LLM çağrısında alınıp bırakılsın. Böylece 1 yuvalı donanımda bile birden çok ajan koşusu ilerler (aralarında sırayla), GPU boşta beklemez.
- Şerit kuralı (öneri): `interactive` istek tüm `G` yuvayı kullanabilir; `batch` istek en çok `max(G-1, 0)` yuva alır (`G=1` iken batch yalnızca etkileşimli bekleyen yokken başlar). Preemption yok: toplu iş küçük birimlere (bir hücre, bir belge) bölündüğü için etkileşimli isteğin bekleme üst sınırı bir birim süresidir. Mike'ın tabular çıkarımı satır başına iş, yani bu granülerlik zaten var (`extractionQueue.ts:9-17`).
- Toplu işler için kullanıcı başına adalet gerekmez (tek kullanıcı), ancak tür başına üst sınır gerekir (örneğin belge dönüştürme/OCR gibi CPU işleri GPU'dan bağımsız, `cpu` kaynağı, kapasite = çekirdek sayısına bağlı).
- Gözlemlenebilirlik: `GET /jobs` ile `running` iş, tutulan yuva, kuyruk derinliği; Mike'taki `last_error` ve `attempts` alanlarının kullanıcıya gösterimi.

Süreç modeli (öneri): FastAPI süreci içinde asyncio görevleri olarak işçiler (Mike'ın `thread` kipinin karşılığı); CPU yoğun ayrıştırma/OCR için `ProcessPoolExecutor` ya da alt süreç; llama-server ayrı süreç, sağlık yoklaması ve yeniden başlatma bağlı. Tek yazarlı SQLite ile birden çok işçi aynı bağlantı havuzunu paylaşabilir; yazma çekişmesi `BEGIN IMMEDIATE` + `busy_timeout` ile yönetilir. Çok işlemli (ayrı işçi süreci) ihtiyaç doğarsa tasarım zaten `claim_token`/kira ile hazırdır.

## Açık sorular

1. `tabular_cells` için `(row_id, column_index)` tekillik kısıtı var mı? `create table` bloğunda (`schema.sql:3282-3293`) yok; yerine `idx_tabular_cells_review_row` (tekil olmayan) görüldü. Kısıt başka bir yerde eklenmiş olabilir; `schema.sql:3373-3470` tamamı okunmadı.
2. `db_jobs` için yayın sonrası kalp atışı eklenmiş midir? Okunan en güncel taşıma/şema (`schema.sql` 2026-10-14 tarihli blokları dahil) böyle bir alan göstermiyor; ancak 136 taşıma dosyasının tamamı okunmadı, yalnızca `20260829_01`, `20260914`/`15` kuyruk değişiklikleri `schema.sql` üzerinden izlendi.
3. Masaüstünde belge dönüştürme ve tablo çıkarımı senkron yolu: `ASYNC_*` kapalıyken istek yolundaki çalışma süresi ve çökme davranışı (ör. `tabular.routes.ts:404` sonrası) ayrıntılı okunmadı.
4. `memory_*` (kullanıcı/proje belleği) alt sisteminin HakHukuk'a uygunluğu: 16 KiB sınırlı, curator işi ile güncellenen bellek dosyası; hukuk bağlamında gizlilik/kaynak gösterme açısından istenip istenmediği ürün kararı.
5. Aynı anda birden çok ajan koşusu için GPU yuvası semaforu ile iş düzeyi kaynak muhasebesinin ikisini birden tutmak gerekli mi, yoksa yalnızca semafor yeterli mi? (İki katmanlı öneri test edilmeden ileri sürüldü.)
6. llama-server'ın kendi yuva kuyruğunun davranışı (yuva doluyken gelen istek bekletiliyor mu, reddediliyor mu) ve yuva başına bağlam bölünmesi: doğrulanmadı; uygulama öncesi ölçülmeli.
7. `sql.js` ve `upgrade.test.js` taşıma yeniden deneme mantığı, SQLite için uygun mu? Alembic `batch` kipi yeterli mi, yoksa tabloyu yeniden kurma yardımcıları elle mi yazılmalı?
8. Mike desktop için "Back Up Local Data" öngörülmüş ama uygulanmamış görünüyor; HakHukuk'ta yükseltme öncesi otomatik yedek hangi saklama politikasıyla (kaç kopya) tutulmalı?
9. `schema-drift` CI iş akışı (`.github/workflows/...`) bu dilimde okunmadı; yalnızca `docs/deployment.md` ve `upgrade.test.js` yorumlarından biliniyor.

## Okunmadı

- `schema.sql`'in büyük bölümü: satır 40-330 (kullanıcı profili ayrıntıları), 365-960 (kurum/hibe/API anahtarı/MCP), 1029-1190 (proje erişim ve kurum geçersiz kılmaları), 1540-1790 ve 1900-2456 (iş akışı paylaşım/erişim fonksiyonları), 2488-2710 ve 2760-2880 (sohbet erişim fonksiyonları, genel bakış RPC'leri), 3030-3250, 3380-3700 (tabular erişim, liste/arama RPC'leri, CourtListener), 3700-5200 çoğu (listeleme/arama RPC'leri, yükleme oturumu fonksiyonlarının büyük kısmı), 5460-6040 (bellek alt sisteminin gövdeleri), 6215-7060, 7200-7980 (hibe/revoke blokları, kurum yaşam döngüsü, denetim), 8150-8870 (Google Workspace, belge yaşam döngüsü sürüm fonksiyonu gövdesi `8320+` kısmen), 8890-10426. Bu bölümler çok kiracılı/arayüz sorgularıdır ve istenmediği için listelenmekle yetinildi.
- 136 taşıma dosyasının hemen hepsi (yalnızca `20260829_01_db_jobs.sql` ve `20260421_01_docx_editing.sql` başı okundu).
- `backend/scripts/migrate.sh` 120. satırdan sonrası, `schema-fingerprint.sql`, `test-*.sh/.mjs/.sql` betikleri, `docker/db-init/*.sh`, `docker/db-init/roles.sql`.
- `backend/src/lib/queue/connection.ts`, `conversionQueue.ts`, `extraction.transport.ts`, `workers/*Worker.ts` (3 satırlık yönlendirmeler), `backend/src/worker.ts`, `workerThread.ts`, `lib/observability/pollFailureGate.ts` (yalnızca adı ve kullanımı).
- `backend/src/modules/*` içinde `documents.cleanupJobs.ts`, `documents.conversionJobs.ts`, `tabular.*` hücre/akış üretimi gövdeleri, `user.service.ts` (hesap silme/dışa aktarma işleyicileri), `memory.service.ts`, `audit.service.ts`, sohbet motoru ve araç dağıtıcı; kuyruk türlerinin işleyici gövdeleri okunmadı, yalnızca kayıt dosyası ve çağrı yerleri.
- `desktop/src/local/{secrets,sql,workflows}.js` tam metinleri (secrets ilk 60 satır, sql ilk 60 satır okundu), `*.test.js` dosyaları (yalnızca `upgrade.test.js` ilk 60 satırı), `desktop/e2e/*`, `desktop/scripts/*.sh`, `main.js`'in yerel mod dışı kısımları (menü, indirme, pencere durumu, OAuth açılır pencereleri).
- `docker-compose.yml` frontend, redis, workflow-sync, createbucket, storage, mailpit bölümleri (yalnızca port/servis listesi ve db, db-init, backend bölümleri okundu); `docs/deployment.md`'nin kimlik doğrulama, S3, Word eklentisi ve CourtListener bölümleri.
- `frontend/`, `word-addin/`, `packages/`, `e2e/`, `loadtest/`, `supabase/`: bu dilimin dışında.
- Hiçbir kod çalıştırılmadı; tüm davranış iddiaları kaynağın okunmasından çıkarımdır (test/ölçüm yok). Öneri bölümündeki sayılar (kira süreleri, `G` değeri, geri çekilme) Mike'tan alınanlar dışında tasarım önerisi ya da tahmindir ve ayrıca işaretlenmiştir.
