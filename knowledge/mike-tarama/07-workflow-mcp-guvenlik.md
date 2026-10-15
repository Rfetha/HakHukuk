# Mike: workflow'lar, MCP/bağlayıcılar ve güvenlik

Tarama notu. Kaynak ağacı: `mike-main/` (AGPL-3.0). Aşağıdaki tüm yollar bu kökün altındadır; `yol:satır` biçimindedir. Kod kopyalanmamıştır, tasarım kendi cümlelerimle özetlenmiştir.

## Kapsam ve okunan dosyalar

Tamamı satır satır okunan dosyalar:

- `backend/src/lib/workflowCatalogSource.ts` (791 satır), `workflowCatalogSync.ts` (98), `workflowCatalog.ts` (169)
- `backend/src/modules/workflows/workflows.addons.ts` (346); `workflows.types.ts`, `workflows.crud.ts` ve `workflows.submissions.ts` kısmen
- `backend/src/lib/mcp/client.ts` (609), `types.ts` (165), `servers.ts` (862), `providers.ts` (147); `oauth.ts` yalnız 600-846. satırlar; `errors.ts` yalnız başlık/yorum düzeyinde
- `backend/src/lib/mcpConnectors.ts`, `blockedDestination.ts`, `privateIp.ts`, `connectorSettings.ts`
- `backend/src/modules/chat/engine/tools/connectorApprovals.ts` (150); `toolDispatcher.ts` ilgili bölgeler (455-560, 757-812); `contextBuilders.ts` ilgili bölgeler (40-290, 405-550, 975-1160, 1488-1580); `prompts.ts` 19-22 ve 85-101
- `packages/contracts/index.d.ts` 60-220 (onay kartı tipleri)
- `backend/src/lib/audit.ts` (220), `auditExport.ts` başı, `modules/audit/audit.routes.ts` başı, `manifestSigning.ts` başı, `downloadTokens.ts` başı, `origins.ts`, `middleware/trustedOrigin.ts`
- `backend/schema.sql` içindeki ilgili tablo ve fonksiyonlar (satır numaraları metinde)
- Dokümanlar: `docs/connectors.md`, `docs/google-workspace.md`, `docs/google-drive.md` (ilk 80 satır), `docs/preset-templates.md`, `docs/safe-local-testing.md`, `docs/sentry-data-audit.md` (ilk 120 satır), `docs/observability.md` (seçili bölümler), `docs/tamper-evident-exports.md`, `SECURITY.md`, `CONTRIBUTING.md` 40-95, `docs/templates/PRD.md` (yalnız başlık: katkıcılar için boş PRD şablonu, bu konuyla ilgisiz)
- Masaüstü kabuğu: `desktop/src/local/workflows.js`, `secrets.js`, `environment.js`, `gateway.js` (başı), `config.js` (başı)
- `backend/src/modules/tabular/tabular.prompt.ts` ve `tabular.extract.ts` (sütun biçimlerinin kullanımı)

Önemli sınırlama: **varsayılan workflow'ların gerçek içerikleri bu ağaçta yoktur.** Workflow metinleri ayrı bir depoda tutulur (`Open-Legal-Products/mike-workflows`, bkz. `backend/src/lib/workflowCatalogSource.ts:8`, `CONTRIBUTING.md:44-46`). Bu yüzden "varsayılan workflow'ların konu ve talimat yapısı" bölümü yalnız anahtar adlarından ve kod politikasından çıkarılabilmiştir; talimat metinleri okunmamıştır (bkz. Okunmadı).

## Nasıl çalışıyor

### 1. Workflow dosya biçimi

Bir workflow, depoda bir dizindir; zorunlu dosya `SKILL.md`, isteğe bağlı `assets/` ve (tablo türünde zorunlu) `table-columns.yaml`.

- **Koleksiyonlar ve tür.** İki üst dizin kabul edilir: `assistant-workflows/` ve `tabular-review-workflows/`; dizin adı türü belirler (`workflowCatalogSource.ts:388-395`, `:446-450`). Derinlik 3 (düz) veya 4 (paket içinde) olmalıdır (`:440-445`). Anahtar (`workflow_key`) dizin adıdır ve `küçük-harf-tire` kalıbına uymalıdır; arşivde yinelenen anahtar hata verir (`:12`, `:451-460`).
- **`SKILL.md` = YAML ön yüz + markdown gövde.** Ön yüz `---` ile ayrılır (`:182-190`). Zorunlu alanlar: `name` (dizin adına eşit olmalı), `license`, `description`, ve `metadata` altında `mike-display-name`, `mike-type` (dizin türüyle eşleşmeli), `version`, `author`, `language`, `practice`, `jurisdictions` (virgülle ayrılmış metin) (`:482-503`, `:506-509`, `:564-604`). `mike-availability` kabul edilir ama kullanılmaz; varsayılan/ek ayrımı koddaki sabit listeden gelir (`:494-504`, `CONTRIBUTING.md:66-68`).
- **Gövde = talimat.** Gövde boşsa hata; `# ` ile başlamıyorsa başa görünen ad başlığı eklenir (`:510-512`). Tek bir "prompt şablonu" alanı vardır (`prompt_md`); değişken yerleştirme veya şablon motoru yoktur, gövde olduğu gibi modele okutulur (bkz. 5. bölüm).
- **`table-columns.yaml`** yalnız tablo türünde okunur; asistan türünde bulunması hata sayılır (`:514-529`). Sütun doğrulaması: boş olmayan dizi; her öğe için tamsayı `index`, boş olmayan `name` ve `prompt`, isteğe bağlı metin `format`, isteğe bağlı metin dizisi `tags` (`:153-170`). Çalışma zamanındaki sütun tipi aynı alanlardır (`backend/src/lib/workflowCatalog.ts:10-16`).
- **Sütun `format` değerleri** çıkarım sırasında modele ek talimat olarak eklenir: `text`, `bulleted_list`, `number`, `percentage`, `monetary_amount`, `currency`, `yes_no`, `date`, `tag` (`backend/src/modules/tabular/tabular.prompt.ts:16-41`, `:73-83`). `yes_no`, `date` ve `tag` için gerekçe alanına alıntı zorunluluğu getirilir. Her hücre için tek bir model çağrısı yapılır ve çıktı `{summary, flag, reasoning}` biçiminde JSON olarak beklenir; `flag` değerleri `green|grey|yellow|red` (`tabular.extract.ts:27-45`).
- **Eklenti dosyaları (`assets/`).** Yalnız doğrudan alt dosyalar (iç içe dizin ve nokta ile başlayanlar hariç), workflow başına en çok 50 (`workflowCatalogSource.ts:531-544`). Her biri için SHA-256 hesaplanır ve geçici dosyaya yazılır (`:545-562`). Çalışma zamanında bunlar "değiştirilemez şablon" olarak sunulur: model, düzenlemeden önce `replicate_document` ile kopya almak zorundadır (`backend/src/modules/chat/engine/prompts.ts:19-22`).
- **Paket (`pack.yaml`).** Dört alan zorunlu: `id`, `title`, `description`, `version`, ve `workflows` listesi. Liste, dizindeki gerçek workflow'larla birebir örtüşmelidir; eksik veya fazla olan hata verir (`:407-437`, `:463-476`, `:641-649`).

Doğrulama sonucu: ilk özet ("markdown prompt şablonu + sütun tanımı") doğrudur ama eksiktir. Eksik kalan parçalar: meta veri alanları (dil, uygulama alanı, yargı bölgesi), referans dosyaları (`assets`), paket kavramı ve hızlı eylem ayarlarının dosyada değil kodda olması.

### 2. Katalog indirme, doğrulama, sürümleme

Akış tek yönlü ve toplu bir "yayın işi"dir; arka uç başlarken indirme yapmaz (`CONTRIBUTING.md:80-83`, `backend/src/jobs/syncWorkflows.ts:1-12`).

1. **Kaynak ayarı.** Depo (`MIKE_WORKFLOWS_REPOSITORY`, varsayılan `Open-Legal-Products/mike-workflows`) `sahip/depo` kalıbıyla, ref (`MIKE_WORKFLOWS_REF`, varsayılan `main`) en çok 200 karakterle doğrulanır (`workflowCatalogSource.ts:8-9`, `:200-217`).
2. **Ref'in değişmez commit'e çözülmesi.** Ref zaten 40 onaltılık karakterse olduğu gibi kullanılır; değilse GitHub API'den commit SHA'sı sorulur ve yine 40 karakter doğrulanır (`:230-252`). Yani "sabit commit" yalnızca *çözüm anında* sabitlenir; varsayılan ref `main` olduğu için işletici açıkça SHA vermezse her çalıştırmada farklı içerik gelebilir. CI bunu bilinçli olarak SHA'ya sabitliyor (`.github/workflows/e2e.yml:350`).
3. **İndirme.** `codeload.github.com/<depo>/zip/<sha>` adresinden, 30 sn zaman aşımıyla; sıkıştırılmış 10 MB sınırı hem `content-length` ile hem akış sırasında sayılarak uygulanır; dosya `wx` kipinde ve `0o600` izniyle yazılır (`:13`, `:18`, `:254-313`).
4. **Zip güvenliği.** Tek kök dizin zorunlu; `..` içeren veya `/` ile başlayan yol reddedilir (`:315-337`). Dosya başına 5 MB, toplam açılmış 50 MB, en çok 1000 workflow sınırı vardır; bildirilen boyut ile gerçek boyut ayrı ayrı denetlenir (`:13-17`, `:339-378`, `:396-400`).
5. **Zorunlu varsayılanlar.** Beş anahtar kodda sabittir ve arşivde yoksa tüm içe aktarma başarısız olur (`:24-34`, `:633-639`).
6. **İçerik özeti.** Her workflow için, meta veri + gövde + asset özetlerinden oluşan JSON'un SHA-256'sı `content_hash` olur (`:623-630`). Bu özet *yerel olarak* üretilir; depo sahibinin imzaladığı veya yayımladığı bir özetle karşılaştırılmaz. Dolayısıyla bütünlük güvencesi yalnız "GitHub'dan gelen sabit commit" ile sınırlıdır; imza veya bağımsız doğrulama yoktur (okunan kodda bulunamadı).
7. **Ara belge ve ikinci doğrulama.** Katalog geçici bir JSON'a yazılır, geri okunur ve `validateWorkflowCatalogDocument` ile yeniden doğrulanır (anahtar kalıbı, tür, 64 karakterlik özet, asset adında `/`, `\`, baştaki nokta yasağı, boyut sınırı) (`:659-751`, `:753-785`). Hata olursa geçici dizin silinir (`:781-784`).
8. **Veritabanına yazma.** Asset'ler nesne deposuna `mike-workflows/<anahtar>/<özet>/<dosya>` yoluyla yüklenir; asset varsa depo yapılandırması zorunludur (`workflowCatalogSync.ts:47-51`, `:56-77`). Ardından tek bir RPC ile katalog atomik olarak değiştirilir (`:84-88`). Bu RPC önce tüm satırları pasif yapar, sonra gelenleri `(workflow_key, content_hash)` çiftine göre ekler/günceller (`backend/schema.sql:1925-1926`, `:1974`); aynı anahtardan yalnız bir aktif sürüm olabilir (`:1832-1834`). Eski içerik özetli satırlar pasif olarak kalır; böylece eski sohbet eklerinin kimlikleri çözülebilir (`backend/src/modules/chat/engine/contextBuilders.ts:1506-1511`). Kaynak commit 40 karakter kontrolünden geçer (`schema.sql:1918-1920`, tablo kısıtı `:1826-1827`).
9. **Kullanıcıya dağıtım.**
   - *Varsayılan (default)* beş workflow: kullanıcının ilk kullanımında, kullanıcıya özel, düzenlenebilir bir kopya olarak kurulur; kurulum kaydı tutulur ve işlem ikinci kez yapılmaz (`workflowCatalog.ts:149-169`; SQL `schema.sql:2034-2128`). Kopya, katalogdan bağımsızdır: sonradan katalog güncellense de kullanıcının kopyası değişmez (`CONTRIBUTING.md:53-57`).
   - *Ek (add-on)* workflow'lar: kullanıcı katalogdan seçip "içe aktarır"; satır `workflows` tablosuna kopyalanır, asset'ler kullanıcının kütüphanesine belge olarak çoğaltılır. Asset kopyalama yarıda kesilirse workflow satırı silinir ve yazılan nesneler dayanıklı bir temizlik işine devredilir (`workflows.addons.ts:214-346`, geri alma `:325-343`).
   - Hızlı eylem (quick action) adı ve istemi dosyada değil kodda sabittir: iki sabit cümle ("seçili belgelerde bu workflow'u çalıştır" ve Word karşılığı) (`workflowCatalogSource.ts:20-23`, `:612-620`). Hangi beş workflow'un hızlı eylem olduğu da kodda belirlenir (`:24-34`).
10. **Çevrimdışı paketleme (masaüstü).** Masaüstü sürümü kataloğu *derleme anında* indirip doğrular ve uygulamaya gömer; çalışma anında ağ okuması yoktur. Kurulumda her asset'in boyutu ve SHA-256'sı yeniden doğrulanır, uyuşmazlıkta "yeniden kurun" hatası verilir (`desktop/src/local/workflows.js:5-10`, `:36-81`; derleme betiği `desktop/scripts/bundle-workflows.js:5-14`). Bu, yerel-önce ürün için doğrudan örnek bir kalıptır.

Doğrulama sonucu: özet doğru ama iki ayrıntı düzeltilmeli. (a) "Sabit commit" varsayılan olarak yoktur; `main` SHA'ya çözülür. (b) Sürümleme iki katmanlıdır: workflow başına `metadata.version` ve paket başına `pack.yaml.version` gösterim içindir; gerçek kimlik `(anahtar, içerik özeti)` çiftidir.

### 3. Kullanıcı workflow'ları, paylaşım ve açık kaynak önerisi

- Kullanıcı kendi workflow'unu oluşturup düzenleyebilir; `columns_config` ve `prompt_md` güncellemede **doğrulanmaz** (yalnız `!= null` denetimi), doğrulama yalnız katalog içe aktarımındadır (`workflows.crud.ts:175-177` ile `workflowCatalogSource.ts:153-170` karşılaştırması).
- Başka kullanıcıların paylaştığı asistan workflow'ları da aynı depoya katılır ve model tarafından okunabilir (`contextBuilders.ts:1548-1571`, "Shared assistant workflows" bloğu). Yani paylaşılmış bir workflow'un metni, "yarı güvenilir talimat" çiti içinde modele verilir (aşağıda).
- Açık kaynağa öneri akışı bir özellik bayrağıyla kapalıdır (`workflows.types.ts:88-89`); anlık görüntü yalnız metadata, `skill_md` ve `columns_config` içerir (`workflows.submissions.ts:37-50`). Yerel tek kullanıcılı üründe gerekli değil.

### 4. Ön ayar sözleşme şablonları (`docs/preset-templates.md`)

Bu, workflow kataloğundan ayrı ikinci bir yerleşik içerik kanalıdır: 81 PDF/DOCX şablonu ve üç markdown başvuru dosyası, ön yüz `public/` dizinine gömülür; her dosya için yol, yayıncı, biçim, bayt ve SHA-256 içeren bir manifest tutulur; çalışma anında yayıncıya istek atılmaz (`docs/preset-templates.md:13-24`, `:34-37`). İçe aktarma, var olan yükleme API'sini kullanır ve yeni arka uç uç noktası gerektirmez (`:38-42`). Lisanslar yayıncıya göre ayrıdır (CC0, CC BY 4.0, bazı belgelerde CC BY-ND 4.0) ve değiştirilmeden saklanır (`:79-92`). Katalog güncellemesi kullanıcının içe aktardığı kopyaların üzerine yazmaz (`:46-47`).

### 5. Workflow metni modele nasıl verilir (istem-enjeksiyonu açısından)

- Seçilen workflow, kullanıcı mesajına `[Workflow: başlık (id: ...)]` biçiminde etiket olarak eklenir; başlık "güvenilmeyen içerik" çitine alınır (`contextBuilders.ts:669-674`). Sistem istemi, modele bu etiketi görünce hemen `read_workflow` çağırıp talimatı izlemesini söyler (`prompts.ts:19-20`).
- `read_workflow` aracı gövdeyi **`<workflow-instructions>`** adlı yarı güvenilir çitle döndürür; çit etiketleri her istek için sabit bir tek kullanımlık-benzeri değer (nonce) taşır ve içerideki çit benzeri etiketler etkisizleştirilir (`toolDispatcher.ts:771-812`, `contextBuilders.ts:261-264`, `:73-82`). Sistem istemi bu çitin içindekini "kullanıcının seçtiği talimat" sayıp izlemesini, ancak sistem kurallarını aşmaması, veri sızdırmaması ve diğer çitli içeriği yeniden yorumlamamasını ister (`prompts.ts:94-98`).
- Belgeler, dosya adları, sohbetteki harici içerik ise **`<untrusted-content>`** çitine alınır ve "yalnız veri" sayılır (`prompts.ts:85-93`, `contextBuilders.ts:93-95`, `toolDispatcher.ts:606`, `:734`).
- Nonce üretimi: sohbet kimliğinden ve bir sırdan HMAC ile türetilir; sabit olması istem önbelleğinin bozulmamasını sağlar. Yorumda açıkça yazıldığı gibi nonce'un tahmin edilemezliği ikincil savunmadır; asıl denetim, çit etiketlerinin veri içinde etkisizleştirilmesidir (`contextBuilders.ts:40-64`).
- Kullanıcının kalıcı "özel talimat" alanı ayrı bir `<user-instructions>` çitiyle verilir ve sistem kurallarını aşamayacağı belirtilir (`contextBuilders.ts:199-215`, `prompts.ts:100-101`).
- Savunmanın doğası: tamamı **istem düzeyinde** (modelden uymasını isteme) ve etiket-temizleme düzeyindedir. Araç çağrısını doğrulayan ayrı bir "çıktı denetleyicisi" okunan kodda yoktur; asıl bağlayıcı denetim, yazma eylemlerinde sunucu onayıdır (aşağıda).

Küçük model açısından not: tabular çıkarım istemindeki belge metni, okunan kodda çit içine alınmamış görünüyor (`tabular.extract.ts:49` ve `:151`: belge metni doğrudan "Document:" başlığı altında, çitsiz). Tablo modülünün tamamı okunmadığı için kesin söylenemez; bkz. Açık sorular.

### 6. MCP istemcisi

- **Taşıma ve kapsam.** Yalnız "streamable HTTP" taşıması vardır (`lib/mcp/types.ts:3`); yerel `stdio` sunucusu desteği yoktur. Kimlik doğrulama türleri: yok, taşıyıcı jeton (bearer), OAuth (`:4`). İstemci, yetenek bildirmez ve katı yetenek denetimi açıktır (`servers.ts:79-82`). Her işlem için yeni bağlantı açılır ve iş bitince kapatılır (`:51-105`); kalıcı oturum yoktur.
- **Bağlayıcı kaydı.** Kullanıcı ad, URL, isteğe bağlı jeton ve en çok 20 özel başlık verir (`types.ts:141-142`; `servers.ts:213-249`). Ad 80 karaktere kısaltılır. Özel başlık adları geçerli HTTP başlık adı olmalı, `Host` yasak, değer 4096 karakter sınırlı (`client.ts:359-387`).
- **Araç önbelleği.** Araç listesi yalnızca *açık yenileme* veya OAuth tamamlanması anında sunucudan alınır ve `user_mcp_connector_tools` tablosuna yazılır (ad, açıklama, giriş/çıkış şeması, ek açıklamalar, açık/kapalı, "yazma mı" bayrağı, son görülme) (`servers.ts:354-416`, `schema.sql:915-932`). Listede artık olmayan araçlar silinir. Model adı `mcp_<bağlayıcı>_<araç>_<kimliğin ilk 8'i>` biçimine çevrilir (`client.ts:159-173`). Sohbet başlarken araç tanımları doğrudan bu önbellekten üretilir, sunucuya gidilmez (`servers.ts:439-486`). Her araç açıklamasının sonuna "bu yanıtlar güvenilmeyen dış bağlamdır" notu eklenir (`:481`).
- **Önbellek tutarlılığı ve boşluk.** Yeni keşfedilen araçlar varsayılan olarak **açık** gelir (`schema.sql:925`). Önbellek, çağrı sırasında sunucudaki tanımla karşılaştırılmaz; onay bağı araç *kimliğini* (`tool_id`) ve bağlantı parmak izini kapsar, araç *tanımının* özetini kapsamaz (`servers.ts:582-597`). Bir sunucu yenilemeler arasında araç anlamını değiştirirse (tanım zehirleme) bunu yakalayan bir mekanizma okunan kodda yok.
- **Yazma sınıflandırması.** Bir araç yalnızca sunucu onu açıkça "salt-okunur" ve "yıkıcı değil" olarak işaretlediyse okuma sayılır; ek açıklama yoksa yazma sayılır (muhafazakâr varsayım) (`client.ts:187-210`). Sınıflandırma sunucunun beyanına dayanır ve belge bunu açıkça belirtir (`docs/connectors.md:123-125`).
- **Sonuç işleme.** Sonuç `{result, note}` JSON'una sarılır ve 60 000 karaktere kırpılır (`servers.ts:512-523`, `types.ts:137`). Hata yolları da aynı "güvenilmeyen veri" sarmalıyla geçer; yorumda gerekçe verilmiş: düşman sunucu hata kanalından istem enjekte edemesin (`servers.ts:795-814`). Zaman aşımı 30 sn (`types.ts:138`).
- **Sağlayıcı farklılıkları.** Google ve Slack için tek tabloda özel davranış kaydı var (zorunlu önceden yapılandırılmış OAuth istemcisi, Google için çevrimdışı erişim parametreleri, yanlış uç nokta ipuçları) (`providers.ts:56-123`). Küçük bir yerel üründe bu tablo gereksizdir.

### 7. Kimlik bilgisi saklama

- **Yöntem.** AES-256-GCM, her kayıt için rastgele 12 baytlık IV, ayrı kimlik doğrulama etiketi; anahtar, ortam değişkenindeki sırdan `scrypt` ile türetilir ve süreç içinde önbelleğe alınır (`client.ts:27-53`, `:65-99`). Sır yoksa istemci başlamaz (`:31-35`). Sabit tuz kullanılır (`:39`), yani sır tek koruma katmanıdır.
- **Neyin şifrelendiği.** Taşıyıcı jeton ve özel başlıklar tek JSON olarak; OAuth erişim/yenileme jetonları ve istemci sırrı ayrı sütunlarda (`client.ts:389-403`; `types.ts:76-99`). Kullanıcıya dönen özette yalnız başlık *adları* ve "yapılandırılmış mı" bayrağı gider, değerler gitmez (`client.ts:283-285`).
- **Şifre çözme hatası.** Hata günlüğe yalnız mesajla yazılır ve boş yapılandırma döner; çözülemeyen kayıt "kimlik bilgisi yok" gibi davranır (`client.ts:119-124`, `:150-156`).
- **OAuth durumu.** PKCE kullanılır; `state` yalnızca özeti (SHA-256) olarak saklanır, doğrulayıcı ve yönlendirme adresi şifrelenir, süre 10 dakikadır; geri çağrı tamamlanınca durum satırı silinir (`oauth.ts:605-646`, `:791-846`; `types.ts:139`). Geri çağrı adresi `API_PUBLIC_URL`'den türetilir ve üretimde zorunludur (`client.ts:55-63`).
- **Masaüstü.** Her kurulum ilk çalıştırmada kendi sırlarını (JWT sırrı, veritabanı parolası, indirme imza sırrı, kullanıcı API anahtarı şifreleme sırrı) üretir; dosya `0o600` izniyle, önce geçici dosyaya yazılıp yeniden adlandırılarak kaydedilir; var olan dosya asla sessizce yeniden üretilmez, çünkü şifreli veriye erişim kaybolurdu. Dosya düz JSON'dur; işletim sistemi anahtar zinciri kullanılmaz (kendi yorumunda "aynı güven sınırı" gerekçesi var) (`desktop/src/local/secrets.js:1-13`, `:52-61`, `:63-109`). Plan belgesi `safeStorage` kullanımını "ideal" olarak anıyor ama uygulanmamış (`desktop/docs/self-contained-plan.md:61-62`).
- **Kullanıcı model API anahtarları** aynı şemayla ayrı bir depoda tutulur (`backend/src/modules/user/user.apiKeyStore.ts:196-232`).

### 8. SSRF ve çıkış denetimi

- **URL ön denetimi.** Yalnız HTTPS; kullanıcı adı/parola/parça temizlenir; `localhost`, `*.localhost` ve bulut meta veri adları engellenir; ana makine adı DNS ile çözülür ve çözülen **herhangi bir** adres yasaklı aralıktaysa reddedilir (`client.ts:303-344`; `types.ts:143-165`).
- **Yasaklı aralıklar.** IPv4: 0/8, 10/8, 100.64/10, 127/8, 169.254/16, 172.16/12, 192.0.0/24, 192.0.2/24, 192.88.99/24, 192.168/16, 198.18/15, 198.51.100/24, 203.0.113/24, çok noktaya yayın ve ayrılmış aralıklar (`privateIp.ts:221-240`). IPv6: yalnız 2000::/3 genel tek-yönlü adres kabul edilir; IPv4-eşlenmiş/uyumlu, Teredo, 6to4, belgeleme vb. engellenir; NAT64'te gömülü IPv4 ayrıca denetlenir (`:243-353`). Ayrıştırılamayan her girdi engellenir (varsayılan ret) (`:359-364`).
- **DNS yeniden bağlama (TOCTOU) savunması.** Paylaşılan bir bağlantı havuzunun DNS araması, soket açılırken yeniden denetim yapar ve yalnızca doğrulanmış adresleri döndürür; yani doğrulanan adres ile bağlanılan adres aynıdır (`client.ts:405-441`).
- **Yönlendirmeler.** Otomatik izleme kapalı; yalnız GET/HEAD için en çok 5 sıçrama elle izlenir ve her sıçrama yeniden doğrulanır. Başka kökene geçildiğinde yalnız `accept`/`accept-language` başlıkları kalır, yetki ve özel başlıklar kalıcı olarak atılır (`:443-582`).
- **Kapsam.** Aynı koruyucu, MCP aktarımı, OAuth keşfi/kaydı/yenilemesi ve kullanıcının girdiği OpenAI-uyumlu model uç noktası için kullanılır (`lib/llm/providers.ts:416-440`, `modules/models/models.compatible.ts:144`). Dikkat: Ollama adresi sunucu ortam değişkeninden gelir ve **korumadan geçmez**; varsayılanı `localhost:11434`'tür (`providers.ts:533-537`). Yani yerel model uç noktası bilinçli olarak korumasız, kullanıcının girdiği uzak uç noktalar korumalı.
- **Yerel-önce için sonuç.** Bu koruma `localhost` ve özel ağı kesin olarak yasaklar. Bir yerel uygulamada yerel MCP sunucusunu (ör. aynı makinedeki araç) bağlamak istenirse bu kural doğrudan çakışır (bkz. değerlendirme).

### 9. Onay (consent) modeli: adım adım

Kapsam: MCP bağlayıcıları ile Google Drive/Gmail/Takvim aynı akışı paylaşır (`connectorApprovals.ts:41-54`).

Ön koşullar ve varsayılanlar:
- Her bağlayıcıda iki anahtar vardır: **Salt okunur** (tüm yazma araçlarını kapatır) ve **Yazma eylemleri için izin iste** (`types.ts:17-20`, `docs/connectors.md:105-140`). Veritabanı varsayılanı ikisi için de `false`'tur (`schema.sql:856-857`).
- **Düzeltme:** yazma onayı varsayılan olarak *kapalıdır*. Belge de açıkça "bir bağlayıcı kurulur kurulmaz asistan veri değiştiren araçları kullanabilir" der (`docs/connectors.md:108-112`; Google için `docs/google-workspace.md:13`). İlk özette "yazma araçları için onay kartı" doğru bir niteleme ama varsayılan davranışı yanlış sezdirebilir.

Akış:
1. **Planlama.** Model bir bağlayıcı aracı çağırınca dağıtıcı önce `plan` aşamasını çalıştırır (`toolDispatcher.ts:466-479`). MCP için: araç etkin ve bağlayıcı etkin değilse "kullanılamaz" yanıtı; araç yazma değilse veya onay ayarı kapalıysa doğrudan `run` (`servers.ts:550-563`).
2. **Boyut sınırı.** Argümanlar 200 000 karakteri aşarsa inceleme yapılamayacağı için çağrı reddedilir (`servers.ts:543`, `:564-572`).
3. **Bağlantı parmak izi.** Hedef sunucu URL'si, taşıma, kimlik doğrulama türü ve kimlik bilgilerinden bir SHA-256 üretilir. Kimlik bilgisi kısmı (OAuth izin kimliği, jeton, başlıklar) önce yavaş bir `scrypt` ile ve uygulama anahtarıyla türetilir ki parmak izinden çevrimdışı tahmin yapılamasın. OAuth için "izin kimliği" kullanılır; böylece rutin jeton yenilemesi parmak izini değiştirmez, ama kullanıcı yeniden yetkilendirirse değişir (`client.ts:212-250`, `types.ts:78`). OAuth bağlayıcıda izin kimliği yoksa onay hiç üretilmez ("yeniden bağlanın") (`servers.ts:657-667`, `:573-581`).
4. **Onay kartı.** Sunucu bir "onay" öğesi üretir: bağlayıcı adı, araç adı, okunur başlık, **tam argümanlar**, isteğe bağlı mevcut durum (`before`), hesap, ve bağ (`connector_id`, `tool_id`, `connection_fingerprint`) (`contracts/index.d.ts:111-142`). Öğenin kimliğini model değil sunucu verir (`toolDispatcher.ts:480-484`). Modelin kendi "soru sor" aracı onay öğesi üretemez; sözleşme bunu açıkça belirtir (`index.d.ts:111-116`).
5. **Tur duraklatma.** Model araca "onay bekleniyor, hiçbir şey çalışmadı" cevabını görür; tur durur (`toolDispatcher.ts:480-494`). Onay öğeleri asistan mesajının içinde kalıcı olarak saklanır, yani sayfa yenilemesinden sağ çıkar (`docs/google-workspace.md:13`).
6. **Karar.** İstemci yalnız `approve` veya `reject` gönderir (`index.d.ts:204-208`). Sunucu, gelen cevabı mesajda saklanan öğelerle birebir eşleştirir: sayı, kimlik, tür; fazla/eksik/yinelenen kimlik reddedilir; onay öğesi için yalnız karar alınır, istemcinin gönderdiği başka alan yok sayılır (`contextBuilders.ts:1005-1030`). Mesajın yazarı olmayan biri cevap veremez (`:1096-1112`).
7. **Tek kullanımlık kayıt.** Yanıt, `append_chat_ask_inputs_response` adlı veritabanı fonksiyonuyla *satır kilidi altında* eklenir; aynı soruya ikinci cevap, yanıtı bulunan olay veya yazar uyuşmazlığı "stale/forbidden" döner (`schema.sql:2818-2874`; `contextBuilders.ts:1114-1124`). Çalıştırma yalnız bu ekleme "appended" döndüğünde yapılır (`connectorApprovals.ts:65-69`; `chat.prepare.ts:373-409`). Bu, çift tıklama ve yeniden oynatmaya karşı korumadır.
8. **Yürütme.** Onaylanan öğeler *saklanan olaydan* okunur, istemciden gelen argüman kullanılmaz (`connectorApprovals.ts:77-105`). `executeApprovedMcpToolCall` şu koşulların hepsi sağlanırsa çağırır: araç hâlâ çözülebiliyor (kullanıcıya ait, etkin, salt-okunur modda yazma engeli yok), bağlayıcı kimliği ve araç kimliği aynı, kayıtlı parmak izi şimdiki parmak izine eşit (`servers.ts:625-655`). Aksi halde "değiştirildi, kapatıldı veya kaldırıldı" cevabı döner. Çağrı anında bir kez daha aynı denetim tekrarlanır ve onay gerekiyorsa onaysız çağrı reddedilir (`:686-707`).
9. **Sonuç.** Sonuç mesaja eklenir; kullanıcıya ham sunucu hatası gösterilmez, sabit bir ileti gösterilir; modele dönen sonuç 4000 karaktere kırpılır (`connectorApprovals.ts:38-39`, `:106-113`).
10. **Çökme güvenliği.** Onay verilip sonuç yazılmadan süreç ölürse, bir sonraki turda modele "sonuç kaydı yok; kullanıcıdan hizmeti kontrol etmesini iste, kendin yeniden deneme" denir. Reddedilen eylem için "kullanıcı yeniden istemedikçe tekrar deneme" yönergesi eklenir (`contextBuilders.ts:540-550`). Google belgesi bunu "en çok bir kez" (at-most-once) semantiği olarak adlandırır ve belirsiz sonucun otomatik yeniden denenmediğini belirtir (`docs/google-workspace.md:78`).
11. **Onayın mümkün olmadığı yüzeyler.** Word eklentisi ve tablo incelemesinde onay penceresi yoktur; onay gereken yazma işlemi açıklamayla reddedilir (`docs/connectors.md:136-139`; `toolDispatcher.ts:497-520`; Word sohbeti `includeAskInputs: false`, `word-chat/wordChat.routes.ts:836`).
12. **Google'a özgü ek korumalar.** Onay öğesi `grant_id`'ye bağlanır; takvim güncellemelerinde ETag ile `If-Match` kullanılarak onay anından sonra değişen öğeye yazma reddedilir; Gmail'de taslak değişimi için kısmi kontrol var ve yarış koşulunun kalabileceği belgede dürüstçe yazılı (`docs/google-workspace.md:77`). Silme için kalıcı silme aracı yoktur; yalnız çöp kutusu (`:20`).

Doğrulama sonucu: ilk özet ("sunucu üretimli onay kartı + bağlantı parmak izi") doğru. Eksikler: argümanların da sunucuda saklanıp yürütmede yalnız oradan okunması, DB düzeyinde tek-kullanımlık ekleme, çağrı anında ikinci denetim ve onayın varsayılan kapalı olması.

### 10. Denetim izi (audit)

İki ayrı iz vardır:

- **Genel denetim (`audit_events`).** Eylem, durum, başlık (300 karakter), yüzey, proje/sohbet/belge/inceleme kimlikleri, model ve serbest `detail` JSON'u saklanır (`lib/audit.ts:10-24`, `:31-51`; `schema.sql:5401-5416`). Bir sohbet turu bir `chat.message` satırı ve her üretilen/düzenlenen/kopyalanan belge ile uygulanan workflow için birer satır üretir (`audit.ts:104-171`). Yazma "ateşle ve unut"tur; hata kullanıcı yolunu bozmaz (`:1-3`, `:53-59`). Dayanıklılık için bir iş kuyruğuna tek kayıt eklenir ve çalışan kayıtları dağıtır; en az bir kez semantiği vardır (çift satır olabilir, boşluk olmaz) (`:173-219`). Okuma uç noktası kişinin kendi eylemleriyle sınırlıdır, kurum denetimi serviste uygulanır (`modules/audit/audit.routes.ts:1-8`); CSV dışa aktarma bir arka plan işi olarak yapılır ve 2000 satırla sınırlıdır (`lib/auditExport.ts:1-16`). Tabloda silinmezlik/zincirleme özet yoktur (okunan şemada bulunmadı); kullanıcı silinince satırlar da silinir (`schema.sql:5404`).
- **MCP araç çağrı izi (`user_mcp_tool_audit_logs`).** Her çağrı için kullanıcı, bağlayıcı, araç, durum (`ok`/`error`), hata iletisi, süre ve sonuç boyutu (karakter) yazılır; **argümanlar ve sonuç içeriği yazılmaz** (`servers.ts:736-774`, `:815-825`, `:842-862`; `schema.sql:939-951`). Onay kararı bu tabloda ayrı bir alan değildir; karar sohbet mesajının içindeki olay olarak durur (`contextBuilders.ts:486-515`).
- **Dışa aktarma bütünlüğü.** Belge sürümleri yazılırken SHA-256 alınır; proje dışa aktarma bildirimi sıralı anahtarlı JSON üzerinden özet taşır ve isteğe bağlı olarak Ed25519 ile imzalanır; imza bağlamı sabit bir alan ayracı içerir; imza anahtarı yanlışsa sessizce imzasız moda düşmek yerine hata verir; genel anahtar ayrı bir uç noktadan alınmalıdır (`docs/tamper-evident-exports.md:3-66`; `manifestSigning.ts:1-70`).
- **İndirme bağlantıları.** Depolama yolu ve dosya adı HMAC-SHA256 ile imzalı, süresi dolmayan bir belirteçte taşınır; karşılaştırma sabit zamanlıdır (`downloadTokens.ts:1-60`). Süresiz bağlantı, sohbet geçmişinde saklanabilsin diye bilinçli bir tercihtir.

### 11. Web yüzeyi savunmaları (kısa)

Durum değiştiren isteklerde `Origin` başlığı izin verilen kökenler kümesinde değilse (veya yoksa) 403 döner (`middleware/trustedOrigin.ts:6-24`, `lib/origins.ts:1-37`). Genel hız sınırları ortam değişkenleriyle ayarlanır (`app.ts:92-118`). Masaüstünde Supabase vekil kapısı tarayıcı kökenli ve `sec-fetch-site` başlıklı istekleri reddeder, anahtar ister, `access-control-*` başlıklarını siler (`desktop/src/local/gateway.js:1-6`, `:15-24`, `:44-49`). Ham LLM akış günlüğü üretimde donanımsal olarak reddedilir (`lib/llm/rawStreamLog.ts:10-17`).

### 12. Telemetri ve gizlilik

- **Hata raporlama varsayılan açıktır.** `SENTRY_DISABLED` ayarlanmadıkça, kendi DSN verilmediyse, olaylar Mike projesinin Sentry'sine gider (`docs/observability.md:14-45`). Bu yüzden self-host edenlerin kapatması gerekir.
- **Veri azaltma.** Taşıma katmanında bir "gizlilik sınırı" tüm zarfı yeniden kurar: yalnız hata olayları geçer; oturum (kullanıcı kimliği dahil), istemci raporu, izleme, günlük, metrik, ek dosya ve tekrar oynatma kaydı yerelde düşürülür; hata metni kontrollü bir tanıma çevrilir; istek adresi, başlıklar, gövde, kullanıcı nesnesi, kırıntılar, serbest alanlar atılır; yalnız UUID biçimindeki bağıntı kimlikleri ve belirli etiketler kalır; dakikada 60 olay üst sınırı vardır (`docs/sentry-data-audit.md:5-37`, `docs/observability.md:200-240`). Belge, bunun "anonimlik" değil "veri azaltma" olduğunu ve kaynak haritası yüklemelerinin ayrı bir kaynak kodu aktarımı olduğunu açıkça söyler.
- **Tarihsel bulgu:** önceki sürümde oturum zarfındaki `did` alanı oturum açmış kullanıcının uygulama kimliğini sızdırıyordu ve istek sorgu değerleri hata olaylarında kalıyordu; bu, sonradan taşıma katmanı sınırıyla kapatıldı (`docs/sentry-data-audit.md:49-58`, `:73-83`). Ders: olay-düzeyi temizleyici yetmez, taşıma düzeyinde izin listesi gerekir.
- **Masaüstü varsayılanı.** Yerel kabuk, çocuk süreçlere ortamdan yalnız birkaç işletim sistemi değişkeni geçirir; Sentry'yi ve Next.js telemetrisini zorla kapatır; kabuğu başlatan terminaldeki bulut API anahtarlarının yanlışlıkla devralınmasını engeller (`desktop/src/local/environment.js:1-17`; test `environment.test.js:8-18`).
- **Üçüncü taraf veri çıkışı.** Belgeler ve bağlayıcı sonuçları seçilen modele ve sohbet geçmişine girer (`docs/google-drive.md`, "Data access" maddesi); bulut model kullanılırsa bu içerik sağlayıcıya gider. Güvenli test belgesi yalnız sentetik veri kullanılmasını ve sınıflandırılmış içeriğin yüklenmemesini önerir (`docs/safe-local-testing.md:3-6`, `:47-53`).
- `SECURITY.md` kapsamında istem enjeksiyonu açıkça kabul edilen bir rapor türüdür (`SECURITY.md:35-39`); tek bakımcılı proje, 7 gün yanıt hedefi (`:21-23`).

## HakHukuk için değerlendirme

Genel çerçeve: Mike'ın güvenlik tasarımı çok kiracılı, buluttan model çağıran ve üçüncü taraf hizmetlere bağlanan bir ürün için yazılmıştır. Tek kullanıcılı, yerel 4B model, çevrimdışı çalışan HakHukuk'ta tehdit yüzeyi küçüktür; ancak iki alan yine kritiktir: (1) modelin belge içeriğinden etkilenmesi (istem enjeksiyonu) ve (2) modelin dış eylem yapabilmesi. Aşağıda taşınabilirlik gerekçelidir.

### Taşınır

1. **Workflow = SKILL.md benzeri tek dosya + isteğe bağlı sütun dosyası.** Ön yüz alanları ve doğrulama kuralları (anahtar kalıbı, ad=dizin adı, tür eşleşmesi, boş gövde reddi, sütun şeması) küçük modelden bağımsızdır, deterministiktir ve kolay test edilir. Gerekçe: katalog doğrulaması model gerektirmez. Türk hukuku için `language: tr`, `practice`, `jurisdictions` (ör. "TR") alanları aynen kullanılabilir; `practice` kümesi (iş hukuku, borçlar, ticaret, tüketici vb.) Türk uyarlaması için daha anlamlı olur.
2. **Tablo incelemesi sütun şeması ve biçim sınıfları.** `text`, `yes_no`, `date`, `number`, `tag` gibi *kapalı küme* çıktılar küçük modeller için uygundur çünkü çıktı daraltılabilir ve sunucu tarafında doğrulanabilir. Hücre başına tek çağrı, yapılandırılmış JSON ve alıntı zorunluluğu 4B için doğru yön (yerel model bağlamı kısa tutar). Bayraklar (`green|grey|yellow|red`) yerine bizim ölçüm çizgimizdeki "cevap vermeme" ve alıntı doğrulamasıyla birleştirilmesi daha tutarlı olur.
3. **Çevrimdışı gömülü katalog + bütünlük kontrolü.** Masaüstü kalıbı (derleme anında indir/doğrula, çalışma anında ağ yok, kurulumda boyut+SHA-256 kontrolü) HakHukuk'un "yerel-önce" ilkesine birebir uyar. Depoya sabit commit ile gömme ve `KUNYE.json` benzeri bir manifest uyumludur. Not: yerel üründe commit sabitlemek zorunlu olmalı; `main`'e çözümleme yerine sürümlü yayın kullanılmalı.
4. **Çıkış (SSRF) denetimi mantığı.** Aralık tablosu, "çözülen herhangi bir adres yasaklıysa ret", bağlanma anında doğrulama (DNS yeniden bağlamaya karşı), elle yönlendirme izleme ve çapraz kökende başlık atma kuralları tasarım olarak taşınır. Python'da `httpx` taşıma katmanı veya özel çözümleyici ile aynı mantık yazılabilir. Yalnızca *uzak* bir hizmete bağlanılacaksa gereklidir.
5. **Sırların şifreli saklanması ve çözümde hata davranışı.** AES-GCM + rastgele IV deseni küçük bir `cryptography` bağımlılığıyla taşınır; ancak anahtar ortam değişkeninden değil işletim sistemi anahtar zincirinden gelmelidir (aşağıda).
6. **Telemetri ilkeleri.** Yerel masaüstü kabuğunun yaptığı gibi: dış raporlama kapalı, ortamdan sır devralma yok, ham istem/yanıt günlüğü yok. Taşınır ve daha da sıkılaştırılabilir (aşağıda).
7. **Tek kullanımlık, sunucuda saklanan onay.** Onay öğesinin sunucuda saklanması, yürütmede yalnız oradan okunması, bir kez çalışması ve "sonucu bilinmeyen" durumu modele dürüstçe bildirmesi küçük modelden bağımsız, doğrudan taşınabilir bir desen. SQLite'ta tek bir `UPDATE ... WHERE status='pending'` ile (satır sayısı 1 mi diye bakarak) aynı atomikliği sağlayabiliriz.
8. **Hak sahibi ve lisans notu taşıyan ön ayar şablon manifesti** (yol, yayıncı, bayt, SHA-256). Türk sözleşme şablonları için aynı manifest deseni uygundur.

### Yeniden tasarlanmalı

1. **Workflow gövdesinin modele sunumu.** Mike, serbest biçimli, uzun talimatı tek bir yarı güvenilir çit içinde verir ve modelin "çiti saygı göstererek" izlemesine güvenir. 4B model için bu zayıf bir güvencedir: çit etiketlerini ve nonce'ları anlayıp çıkarım yapma yeteneği sınırlıdır ve uzun talimatı sadakatle izleyemez. Önerilen: workflow'u *adımlara ayrılmış* (ör. "oku → çıkar → doğrula → yaz") ve her adımda uygulama tarafından tek tek çalıştırılan bir şemaya çevirmek; çit, savunma olarak değil yalnızca iyi bir alışkanlık olarak kalmalı. Bu, ilk özetin "markdown prompt şablonu" varsayımından bilinçli bir sapmadır ve ADR gerektirir.
2. **Güvenilmeyen içerik savunması.** Mike'ın savunması neredeyse tamamen istem düzeyindedir. Yerel 4B modelde bu yeterli değildir; savunma *yetki ayrımına* dayanmalı: belge içeriğiyle çalışan tur, yazma/dış eylem araçlarını hiç görmemeli (araç kümesi çalışma türüne göre statik daraltılır). Yani "belge oku ve özetle" modunda dosya yazma, ağ ve bağlayıcı araçları kapalı olmalı; etkin olduğu modda belge bağlamı sınırlı olmalı.
3. **Onay kartı.** Mantığı taşınır, ama varsayılan tersine çevrilmeli: Mike'ta yazma onayı varsayılan kapalı, HakHukuk'ta **varsayılan açık ve ürün genelinde zorunlu** olmalı; "Her zaman izin ver" bir ayar olmalı ve yalnızca eylem *sınıfı* başına (aşağıdaki çerçeve). Ayrıca onay kartı, eylemin etkisini kullanıcının dilinde (Türkçe), argümanların sade özetiyle göstermeli; küçük modelin ürettiği argümanlar daha hatalı olabileceğinden "tam argümanlar" ekranı zorunlu kalır.
4. **Araç önbelleği ve tanım zehirleme.** Mike araç tanımlarını yenileme anında kaydeder ama değişikliği saptamaz. HakHukuk'ta araç tanımının özeti (ad+açıklama+şema) onay bağına ve kaydedilmiş kullanıcı kararına dahil edilmeli; tanım değişirse araç yeniden "yeni araç" olarak onay beklemeli. Ayrıca yeni keşfedilen araçlar varsayılan olarak *kapalı* gelmeli (Mike'ta açık).
5. **MCP taşıması.** Mike yalnız uzak HTTPS destekler. Yerel-önce üründe en olası kullanım yerel süreçlerdir (stdio veya loopback HTTP). Bu durumda SSRF kuralı ("loopback yasak") tersine döner: yerel MCP için *izin listesi* (kullanıcının açıkça eklediği komut/port) ve uzak MCP için mevcut kural geçerli olmalı. Bu, yeni bir güvenlik kararıdır ve ayrıca değerlendirme gerektirir. Yerel stdio sunucusunun yürütülebilir yolu da onay gerektiren bir eylemdir.
6. **Denetim izi.** Mike'ta MCP izi argüman ve karar içermez, genel iz ise zincirleme özet taşımaz. Yerel tek kullanıcıda amaç hesap verebilirlik değil, "ne olduğunu sonradan görebilme"dir; SQLite'ta yalnız-ekleme (append-only) bir tablo ve her satırda önceki satırın özeti (hash zinciri) tutmak ucuzdur ve eşleşmeyen değişikliği fark etmeyi sağlar. Argümanlar olduğu gibi değil, kısaltılmış ve kişisel veriden arındırılmış biçimde saklanmalı (hukuki metin içerir).
7. **Telemetri.** Kapalı olmalı; "varsayılan açık, opt-out" modelinin tersi. Hata raporlaması istenirse yerel dosyaya yazılan, kullanıcı elle gönderen bir "tanı paketi" olmalı. Mike'ın taşıma-katmanı izin listesi yaklaşımı, böyle bir paketi üretirken bile kullanışlıdır.
8. **Masaüstü sır dosyası.** Düz JSON; işletim sistemi anahtar zincirine alternatif düşünülmeli (Python `keyring`) veya en azından dosya izni 0600 ve veri dizininin kullanıcı hesabıyla sınırlı olması denetlenmeli. Mike belgesi bunu "aynı güven sınırı" diye gerekçelendirir; yerel tek kullanıcıda kabul edilebilir ama belgeye "kabul edilen risk" olarak yazılmalı.
9. **Yerel dosya sistemi araçları.** Mike'ta yok (belgeler depoda, bulut). HakHukuk'ta "dosya aç/kaydet" doğrudan yerel dosya sistemine dokunur; bu Mike'ta karşılığı olmayan yeni bir yüzey ve yol gezinmesi (`..`, simge bağlantısı) denetimi gerektirir. Zip yol denetimi bir başlangıçtır (`workflowCatalogSource.ts:327-333`) ama yeterli değildir.

### Taşınmaz

1. **Kurum/ekip özellikleri**: paylaşılan workflow'lar, açık kaynağa öneri, kurum denetim erişimi, API anahtarları, kullanıcı başına hız sınırları. Tek kullanıcıda karşılığı yok (`workflows.sharing.ts`, `workflows.submissions.ts`, `orgs.*`).
2. **Google Drive/Gmail/Takvim bağlayıcıları ve Slack/Google OAuth istemci yönetimi.** Bunlar bulut hesaplarına erişim içindir; çevrimdışı yerel ürünün kapsamında değildir ve OAuth istemci sırrı barındırma yükü getirir. İstenirse sonraki bir turda, ayrı bir güvenlik değerlendirmesiyle düşünülür.
3. **GitHub'dan canlı katalog çekme işi** (çalışma anında veya sunucu yayın işi olarak). Yerel üründe katalog sürüm içinde gömülür; ağ erişimi gerekmez.
4. **Sentry tabanlı uzak hata toplama** ve kaynak-haritası yükleme: ürün çevrimdışı ve gizlilik odaklı; dışarı veri çıkışı yok.
5. **Büyük modele özgü yarı güvenilir çit disiplini** (uzun istem, çoklu çit türü, nonce): 4B için güvenilir değil (bkz. Yeniden tasarlanmalı 1-2); biçim olarak korunabilir ama güvenlik kontrolü sayılmamalı.
6. **Supabase/RLS/çok kiracılı veritabanı fonksiyonları.** SQLite'ta rol/RLS yok; tek kullanıcıda gerekli değil. Yalnız atomiklik (tek-kullanımlık onay) deseni taşınır.
7. **Hızlı eylem ve workflow'un Word eklentisi yüzeyleri.**

### Önerilen minimal güvenlik ve onay çerçevesi (yerel, tek kullanıcı)

İlke: modelin ürettiği her şey "öneri"dir; **etkisi geri alınamayan veya uygulama dışına çıkan her eylem kullanıcının görünür onayını ister**. Onay istemi sunucuda (FastAPI) üretilir, argümanlar sunucuda saklanır, istemci yalnız karar gönderir, bir onay bir kez geçerlidir. Belge içeriği ile araç yetkisi birbirinden yapısal olarak ayrılır.

| Eylem sınıfı | Örnekler | Onay |
| --- | --- | --- |
| A. Salt-okunur, yerel, uygulama veri alanı içinde | mevzuat arama, yerel belge okuma, alıntı doğrulama, özetleme, tablo incelemesi hücre üretme | Onay yok. Günlüğe yaz (kısa kayıt). |
| B. Uygulama verisini oluşturan/değiştiren (geri alınabilir) | yeni belge üretme, belge kopyası, taslak kaydetme, workflow içe aktarma | İlk kullanımda tek seferlik "bu oturum için izin ver"; her yazma, sürüm geçmişiyle geri alınabilir olmalı. |
| C. Kullanıcının kendi dosya sisteminde, uygulama alanı dışında yazma/silme/üzerine yazma | "Kaydet ... klasörüne", dışa aktarma, dosya silme | Her seferinde onay kartı: tam yol, işlem, boyut/üzerine yazılacak mı. Silme ve üzerine yazma için "geri alınamaz" uyarısı. Yol, kullanıcı tarafından seçilen kök dizinin dışına çıkamaz (simge bağlantı çözümü sonrası denetim). |
| D. Ağa çıkış | uzak MCP sunucusu, uzak model uç noktası, canlı mevzuat kaynağı (ör. Bedesten) sorgusu, güncelleme denetimi | Bir hedefin ilk eklenmesinde kullanıcı onayı ve hedefin kalıcı kaydı; sonraki çağrılar ek onaysız ama **yalnız kayıtlı hedefe**. Hedef değişirse (URL, kimlik bilgisi, araç tanımı özeti) yeniden onay. Çıkışa giden içerik (belge parçaları) onay kartında özetlenir. Varsayılan: çevrimdışı mod, ağ kapalı. |
| E. Dış etkisi olan yazma (e-posta gönderme, takvim, mesaj, uzak API'ye yazma) | uzak MCP yazma araçları | Her seferinde onay; "her zaman izin ver" seçeneği sunulmaz. Onay kartı tam argümanları ve hedef hesabı gösterir. |
| F. Kod/komut çalıştırma, yerel MCP (stdio) sunucusu başlatma, eklenti kurma | araç sunucusu yürütülebilir dosyası | Her kurulumda onay + yürütülebilir dosya yolu ve özeti sabitlenir; değişirse yeniden onay. Varsayılan kapalı. |
| G. Ayar ve sır işlemleri | API anahtarı ekleme/silme, telemetri anahtarı, onay politikasını gevşetme | Her seferinde açık kullanıcı eylemi (model tarafından tetiklenemez); politikayı gevşetme değişiklikleri denetim izine yazılır. |

Destekleyici kurallar:

1. **Yetki ayrımı (en önemli kural).** Belge üzerinde çalışan turlarda yalnız A sınıfı araçlar sunulur. B-G sınıfı araçlar yalnızca kullanıcının açıkça başlattığı, araç kümesi sabit workflow adımlarında sunulur. Böylece belge içindeki enjeksiyon, araç çağırma yeteneğine ulaşamaz. Çit/nonce yalnız ikinci katmandır.
2. **Yeni araç = kapalı.** Yeni görülen araç, değişen tanım ve belirsiz ek açıklama yazma sayılır ve kapalı gelir. Tanım özeti onay bağına girer.
3. **Onay kaydı.** `pending → approved|rejected → executed|failed|unknown` durum makinesi; tek `UPDATE` ile geçiş; süreç çökerse `approved` kalan kayıt başlangıçta `unknown` olarak işaretlenir ve kullanıcıya gösterilir (otomatik yeniden deneme yok).
4. **Yalnız-ekleme denetim kaydı.** Sınıf, araç, hedef, argümanların kısaltılmış/arındırılmış özeti, karar, sonuç durumu, süre; satır zinciri özetiyle. Belge metni ve istem tam metni varsayılan olarak saklanmaz.
5. **Gizlilik varsayılanları.** Telemetri yok; bulut model yok (kullanıcı isterse eklenir ve ilk kullanımda "belge parçaları bu sağlayıcıya gidecek" uyarısı); sırlar işletim sistemi anahtar zincirinde; ham istem günlüğü yalnız geliştirme kipinde ve varsayılan kapalı.
6. **Kataloğun bütünlüğü.** Gömülü workflow ve şablonlar için sürüm başına manifest (SHA-256); kullanıcı kopyaları katalogdan bağımsız; katalog güncellemesi kopyaların üzerine yazmaz.

## Açık sorular

1. Varsayılan beş workflow'un (`proofread`, `compare-documents`, `extract-key-terms`, `draft-from-template`, `commercial-agreement-tabular-review`) gerçek talimat metinleri nasıl? Talimat uzunluğu ve adım yapısı 4B'ye uygun mu? Ayrı depodan okunması gerekir. Anahtar adlarına göre Türk hukuku için anlamlı olanlar: düzeltme/redaksiyon, iki belge karşılaştırma, anahtar terim çıkarma ve şablondan taslak üretme (sözleşme yazımı için doğrudan geçerli); "ticari sözleşme tablo incelemesi" Türk Borçlar Kanunu ve Türk Ticaret Kanunu kavramlarına uyarlanmalı (ör. cezai şart, fesih, yetkili mahkeme, rekabet yasağı, KVKK ve gizlilik hükümleri). Bu liste adlardan çıkarılmış tahmindir, metin okunmadı.
2. Tablo incelemesi hücre isteminde belge metni çit içine alınıyor mu? Okunan satırlarda görünmüyor (`tabular.extract.ts:49`, `:151`); `spotlight` yalnız sohbet katmanında aranırken bulundu (`chat.service.ts`, `projectChat.service.ts`, `toolDispatcher.ts`, `wordClientTools.ts`). Kesin için tabular modülünün tamamının okunması gerekir.
3. Mike'ın araç çağrısı doğrulaması: modelin ürettiği argümanlar araç şemasına karşı sunucuda doğrulanıyor mu (JSON şeması)? MCP yolunda şema yalnız modele veriliyor, çağrıdan önce doğrulama görmedim (`servers.ts:708-717`); yine de MCP sunucusunun kendi doğrulaması var. Okunmadı.
4. OAuth geri çağrı yolu ve çerez/oturum modeli (MFA, `docs/google-workspace.md:76`) yerel tek kullanıcıda gerekli mi? Muhtemelen değil; ama yerel arayüzün diğer yerel süreçlerden korunması (loopback port, `Origin` denetimi, rastgele oturum belirteci) için masaüstü kapısının tasarımı (`desktop/src/local/gateway.js`) ayrıca incelenmeli.
5. Onay kartı arayüzü (`AskInputPopup`) ve istemci tarafı davranışı (çift tıklama, yenileme) okunmadı; yalnız sunucu tarafı akış okundu.
6. Çıkarım hızı: `scrypt` ile parmak izi türetmenin yerel donanımda gecikmesi ölçülmedi. Bizim tasarımda parmak izi için daha hafif bir HMAC yeterli olabilir çünkü tehdit modeli farklı.
7. Yerel MCP (stdio) için hangi izin ve yalıtım modeli (alt süreç sınırlamaları, ortam değişkeni temizleme) kullanılacak? Mike'ın masaüstü ortam temizleme yaklaşımı (`environment.js`) bir başlangıç, ancak komut çalıştırma yüzeyi için yeterli değil.
8. Katalog için imza: Mike yalnız SHA'ya güveniyor. HakHukuk'un kendi yayın kanalı için Ed25519 imzalı manifest (Mike'ın dışa aktarma imza kalıbı `manifestSigning.ts` örnek) kullanılacak mı?

## Okunmadı

- Varsayılan ve ek workflow'ların **içerikleri** (`mike-workflows` deposu bu ağaçta yok). Fixture olarak `legal-starter` paket anahtarı yalnız bir arayüz test dosyasında geçiyor (`frontend/src/app/components/workflows/WorkflowList.test.tsx:154`); gerçek paket listesi bilinmiyor.
- `backend/src/lib/mcp/oauth.ts` 1-600. satırlar (keşif, jeton saklama, jeton yenileme ayrıntıları); `errors.ts` gövdesi (yalnız başlık ve yorumlar).
- `backend/src/lib/integrations/` içindeki Google Drive/Workspace kaynak dosyaları (yalnız ilgili dokümanlar okundu): `googleDrive.ts`, `googleWorkspace*.ts`, `googleDrive*.ts` yardımcıları. Bu dosyalar HakHukuk için taşınmaz sayıldığından derinlemesine okunmadı.
- `docs/google-drive.md` 80. satırdan sonrası, `docs/sentry-data-audit.md` 120. satırdan sonrası, `docs/observability.md` ve `docs/sentry-issue-review-2026-09-23.md` kalan bölümleri.
- `backend/src/lib/auditExport.ts` ve `modules/audit/audit.service.ts` gövdeleri; org düzeyindeki denetim erişim kuralları.
- `workflows.sharing.ts`, `workflows.overview.ts`, `workflows.listing.ts`, `workflows.assets.ts`, `workflowAddons.routes.ts`, `quickActions.*` (yalnız başlık/satır aralıkları).
- Tabular modülünün tamamı (yalnız `tabular.prompt.ts`, `tabular.extract.ts` başı ve seçili satırlar); tabular çıkarım iş akışı ve iş kuyruğu.
- Arayüz (`frontend/`) tarafı, Word eklentisi (`word-addin/`), `e2e/`, `loadtest/`; yalnız eşleşme aramalarıyla taranan dosyalar.
- `backend/src/lib/llm/` (yalnız `providers.ts` ilgili satırlar ve `localModelMiddleware.ts` başı): yerel model uç noktası ve araç çağrısı ayrıştırma ayrıntıları başka bölümün konusu.
- `backend/migrations/*.sql` dosyalarının ayrı ayrı içeriği; güncel şema `backend/schema.sql` üzerinden okundu.
- `middleware/auth.ts`, `app.ts` yapılandırması (yalnız hız sınırı satırları bakıldı), oturum/MFA kodu.
- Sistem istemlerinin tamamı: `prompts.ts` yalnız 19-22 ve 85-101 satırlarında okundu.
