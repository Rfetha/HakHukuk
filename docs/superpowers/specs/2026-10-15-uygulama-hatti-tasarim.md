# Uygulama hattı: tasarım taslağı

> **Durum:** taslak, kod yok. Karar çerçevesi [ADR-0104](../../adr/kararlar-0064-0085.md#adr-0104); takvim, araç çağırma ölçümünün yeri ve araç RL'i [ADR-0105](../../adr/kararlar-0064-0085.md#adr-0105).
> Girdi: [`knowledge/mike-tarama/`](../../../knowledge/mike-tarama/README.md) (Mike taraması; AGPL-3.0, yalnız tasarım okundu, kod kopyalanmadı).
> Bu belge öneri içerir; "öneri" etiketli yerler ölçülmeden bağlayıcı değildir.

## 1. Amaç ve sınırlar

**Amaç.** Tek kullanıcılı, yerel, çevrimdışı çalışabilen bir hukuk ajanı: HakHukuk modeli (4B) ile mevzuat arama, madde okuma, çok adımlı soru çözme, belge inceleme ve taslak üretme; birden çok işin aynı anda koşması.

**Kapsam dışı (bu taslakta).** İçtihat arama (kapsam ADR'si ayrı, Dilim D) · çok kullanıcılı hesap, organizasyon, paylaşım · bulut barındırma · Word eklentisi · masaüstü kabuğu · hafıza (LLM'li) · canlı `bedesten` API (B6).

**Değişmezler.**
- Ürün yolu = ölçüm yolu ([ADR-0080](../../adr/kararlar-0064-0085.md#adr-0080)): uygulama modele `hakhukuk.cekirdek` üzerinden gider, `llama-server`'ı kendi bayraklarıyla doğrudan sürmez.
- Sessiz yanlışlık yok ([`yurutme-tuzaklari.md`](../../record/yurutme-tuzaklari.md)): bozuk model çıktısı hücreye ya da mesaja yazılmaz, hata durumuna düşer.
- Çakışmada kağıt hattı (Makale 1 ve 2) kazanır; uygulama kesilir.

## 2. Yerleşim

```
apps/
  api/            FastAPI; hakhukuk.cekirdek'i import eder; SQLite + iş kuyruğu + dosya deposu
  web/            TypeScript ön yüz (framework: açık soru 1)
packages/
  contracts/      FastAPI OpenAPI şemasından üretilen tipler (tek paylaşılan TS paketi)
hakhukuk/         mevcut ürün paketi; arayuz/api'ye dokunulmaz
```

Turborepo yok (Mike de kullanmıyor; [08](../../../knowledge/mike-tarama/08-arayuz-test-kalite.md)). TS tarafı için tek bir workspace yöneticisi yeter; ikinci TS uygulaması (Word eklentisi, masaüstü) gelirse yeniden bakılır.

```
web ──HTTP/SSE──> apps/api ──> cekirdek (retriever, answer, terazi)
                      │              │
                      │              └──> OpenAI-uyumlu uç nokta (llama-server)
                      └──> SQLite · dosya deposu · işçi süreci (jobs)
```

## 3. Model profili

Temel model bir parametredir ([ADR-0026](../../adr/gemma4-12b-dersler.md#adr-0026)); uygulama kazananı bilmeden yazılır ([ADR-0104](../../adr/kararlar-0064-0085.md#adr-0104)). Modele özgü her şey bir profilde durur:

| alan | Qwen3.5-4B | Gemma 4 E4B |
|---|---|---|
| sohbet şablonu ve tur işaretleri | tam | iskelet |
| araç çağrısı biçimi (sunucu tarafı ayrıştırıcı ya da kısıtlı çözüm) | tam | iskelet |
| düşünmeyi zorla kapatma (1024 + 512) | `answer()`'daki kural | Gemma'nın kapanış işaretine göre |
| kısıtlı kod çözme ayarı (GBNF / `json_schema`) | tam | iskelet |

Gemma profili yalnız F0.9 kapısını geçip DEV'de önde çıkarsa doldurulur. Çıkarım katmanı bir `Protocol`: `complete(messages, tools, constraint) -> Result`, `count_tokens(text) -> int`, `slots() -> int`. Uç nokta profili (llama.cpp, vLLM, SGLang) hangi kısıt biçiminin (GBNF ya da `json_schema`) kullanılacağını söyler. Mike'da bunların hiçbiri yok ([02](../../../knowledge/mike-tarama/02-llm-saglayici-ve-yerel-model.md)).

## 4. Ajan döngüsü ve araçlar

**Kurallar (öneri, ölçümle ayarlanır).**
- Sert tur sınırı küçük (3-4); sistem prompt'u ile kod aynı sayıyı söyler (Mike'da 10 ve 16 çelişiyor).
- Adım başına tek araç çağrısı; sunucu sırayla yürütür.
- Aynı argümanla aynı araç ikinci kez çağrılırsa sunucu keser ve kısa, yapılandırılmış bir durum döner (düzyazı açıklama değil).
- Araç argümanı şemaya uymazsa `{}` yapılmaz: modele açık hata döner, en çok 2 düzeltme hakkı, sonra tur `hata` ile biter.
- Retrieval modele sorulmaz: sunucu hibrit erişimi (BM25 + `bge-m3`, RRF; `getir()` yalnız yürürlükteki maddeler) ön adım olarak koşar, sonuç bağlama girer.
- Belirsizlikte `kullaniciya_sor`: araç sonucu üretilmeden tur biter, yanıt yeni istek olur (stateless).
- Belge ve mevzuat metinleri nonce'lı etikette sarılır; içerideki sahte etiketler etkisizleştirilir.

**KAPI ↔ KALDIRAÇ ([ADR-0076](../../adr/kararlar-0064-0085.md#adr-0076)) korunur.** Atıf doğrulama, mülga süzgeci ve durum sınıflandırma KAPI'dır: koşulsuz çalışır, araç yapılmaz (model çağırmayı unutursa garanti kaybolur). Modelin çağırdığı araçlar deterministik KALDIRAÇ'tır ve hiçbiri LLM çağırmaz. Araç döngüsü sınırlıdır; sınıra dayanmak görünür kalır (`ARAMA_TUKENDI`). Madde kimliği `(kanun_no, madde_no)`dur; adlar paketin kendi adlarıdır (Türkçe).

**Araç seti (öneri; Dilim A).** Başlangıç noktası `hakhukuk/cekirdek/araclar.py`'de **zaten bulunan** beş araçtır; yenisi yalnız belge, kullanıcı ve süre için eklenir.

| araç | durum | parametre | döner |
|---|---|---|---|
| `ara` | var | `sorgu`, `k` | en çok `k` kaynak (kanun, madde, yürürlük) |
| `madde_getir` | var | `kanun_no`, `madde_no` | madde metni ya da yok |
| `madde_var_mi` | var | `kanun_no`, `madde_no` | evet/hayır |
| `kanun_bul` | var | `ad` | `(kanun_no, ad)` adayları |
| `yururlukte_mi` | var | `kanun_no`, `madde_no` | yürürlük durumu |
| `belge_ara` | yeni (B) | `belge_id`, `sorgu` | eşleşen parçalar (parça kimliği + metin) |
| `belge_oku` | yeni (B) | `belge_id`, `sayfa` | tek sayfa metin; tekrar okuma kesilir |
| `kullaniciya_sor` | yeni (A) | `soru`, `secenekler` (2-4) | kullanıcı yanıtı (yeni istek) |
| `sure_hesapla` | yeni (A) | `baslangic`, `tur` (enum), `gun` | tarih; model hesaplamaz |

Şemalar düz (iç içe dizi yok). Dilim A'nın araç sayısı 7 (beş mevcut + `kullaniciya_sor` + `sure_hesapla`); araç çağırma ölçümünde 5 ve 7 araç karşılaştırılır. Retriever her zaman koşar (ön adım); `ara` yalnız recall kaybında modelin yeniden denemesi içindir.

## 5. Atıf akışı

1. Model cevap metninde satır içi `[kanun_no/madde_no]` işaretleri yazar; alıntı metnini **yazmaz**. Çıktı kısıtlı çözümle (kimlik kümesi) sınırlanır.
2. Sunucu her kimliği korpusa karşı çözer, alıntıyı **kaynaktan çeker**. Bu adım bir KAPI'dır (ADR-0076): araç değil, her cevapta koşulsuz çalışır.
3. Üç durum, varsayılan kapalı (fail-closed): `verified` (kimlik var, yürürlükte, alıntı kaynakta bitişik) · `unverified` (kimlik yok ya da alıntı eşleşmedi) · `unchecked` (doğrulama koşmadı: iptal, hata, tablo). Bayrak boşsa `unchecked`; Mike'ın boş bayrağı "doğrulandı" sayması bizde hata sayılır ([03](../../../knowledge/mike-tarama/03-atif-baglam-hafiza.md), [08](../../../knowledge/mike-tarama/08-arayuz-test-kalite.md)).
4. Gövdedeki "m. N" ve "N. madde" anmaları atıf kümesiyle karşılaştırılır; kümede olmayan anma `unverified` olarak işaretlenir.
5. Arayüz `unverified` ve `unchecked` atıfı tıklanamaz ve vurgusuz gösterir.

Doğrulama algoritması mevcut deterministik atıf doğrulamasını yeniden kullanır (`hakhukuk/cekirdek`); yeniden yazılmaz.

## 6. Türkçe normalizasyon

Tek yerde (`cekirdek` içinde bir modül), yerel ayara duyarlı (`tr`): `İ`↔`i`, `I`↔`ı` ayrımı, konum haritasında 1:1 indeks (Unicode küçük harfleme uzunluk değiştirebilir, harita bunu taşımaz), noktalama silmede sayısal ifadeler (`1.500`, `15,00`) korunur. Atıf doğrulama, redline eşleştirme ve ön yüz vurgusu **aynı** modülü (ya da aynı test vektörlerini) kullanır. Test vektörleri: `İSTANBUL ISPARTA`, `ığüşöç`, `1.500` / `15,00`. Mike'da üç yerde ayrı ve kusurlu ([03](../../../knowledge/mike-tarama/03-atif-baglam-hafiza.md), [05](../../../knowledge/mike-tarama/05-belge-isleme-ve-redline.md)).

## 7. Veri modeli (SQLite, tablo ve alan düzeyi)

SQLAlchemy/SQLModel + Alembic (batch). Dosyalar yerel dosya sisteminde; veritabanı yalnız yolu ve özeti tutar. Tek kullanıcı: organizasyon, rol, RLS, paylaşım yok.

| tablo | ana alanlar |
|---|---|
| `project` | `id`, `name`, `created_at` (dava dosyası / matter) |
| `document` | `id`, `project_id`, `current_version_id`, `status` |
| `document_version` | `id`, `document_id`, `version_no`, `storage_path`, `content_sha256`, `source` (`upload` / `assistant_edit` / `user_accept` / `user_reject`), `textless_pages`, `deleted_at`; değişmez, yeni değişiklik yeni sürümdür |
| `document_edit` | `id`, `version_id`, `paragraph_id`, `find`, `replace`, `status` (`pending` / `accepted` / `rejected`), `message_id` |
| `chat` | `id`, `project_id`, `title`, `model_profile` |
| `message` | `id`, `chat_id`, `role`, `content`, `citations` (durumlarıyla), `run_id` |
| `workflow` | `id`, `kind` (`assistant` / `review`), `source_path`, `content_sha256` (dosyadan yüklenir) |
| `review` | `id`, `project_id`, `spec_hash`, `columns` |
| `review_row` | `id`, `review_id`, `document_id`, `sort_index` |
| `review_cell` | `review_id`, `row_id`, `column_index`, `status`, `value`, `evidence`, `run_id`; `status` ∈ `found`, `not_found`, `unparseable`, `unverified`, `stale`, `pending`, `error` |
| `setting` | anahtar-değer (model profili, uç nokta, slot sayısı) |
| `job` | aşağıda |

`not_found` ayrı bir durumdur: aşırı ret (modelin ana kaybı, [CLAUDE.md](../../../CLAUDE.md)) hücre düzeyinde ayrıca ölçülür.

## 8. İş kuyruğu ve eşzamanlılık

Mike'ın `db_jobs` deseninden alınanlar ([06](../../../knowledge/mike-tarama/06-veri-modeli-is-kuyrugu-yerel-paket.md)): tek ifadede talep, `dedupe_key` kısmi benzersiz indeks, çit belirteci, üstel geri çekilme, kalıcı hata ayrımı, başarısızlık kancası.

`job`: `id`, `kind`, `payload`, `status` (`pending` / `running` / `done` / `failed` / `cancelled`), `lane` (`interactive` / `batch`), `priority`, `slots` (kaç LLM yuvası ister), `attempts`, `max_attempts`, `run_at`, `claim_token`, `lease_until`, `heartbeat_at`, `boot_id`, `dedupe_key`, `cancel_requested`, `last_error`, `result`.

- Talep: `BEGIN IMMEDIATE` içinde koşullu `UPDATE ... RETURNING`; SQLite tek yazar olduğu için `skip locked` gerekmez.
- Bitiş yazmaları `id + claim_token` ile adreslenir (zombi işçi sonradan alınmış işin üstüne yazamaz).
- Kalp atışı: uzun satır işi `lease_until`'i yeniler; Mike'da kalp atışı yok, yalnız yaş eşiği (600 sn).
- Açılışta `boot_id` farklı olan `running` işler hemen kurtarılır (süre beklenmez).
- **Eşzamanlılık = sunucu yuva sayısı.** `slots()` (`llama-server -np`) bir kaynak olarak muhasebelenir; öneri: `interactive` tüm yuvaları, `batch` en çok G-1 yuvayı kullanır; LLM çağrısı başına öncelikli semafor. Tasarım önerisi, ölçülmedi.
- Sohbet koşuları bellek içi ve sunucu sahipli (SSE `id:` numaralı kare tamponu, `from=` ile yeniden bağlanma, ayrı durdurma ucu); kuyruğa girmezler.
- Hücre yazmaları `run_id` ile korunur: iptal = damgayı düşürmek, uçuştaki iş yazamaz. Bitmiş hücreler yeniden denemede atlanır.

## 9. Belgeler (Dilim B)

**Çıkarım hattı (öneri).** DOCX ve PDF için metin çıkarımı sürüm özetiyle anahtarlı önbellek; sayfa/madde bölümlemesi; metin katmanı olmayan PDF'te modele sessiz boş metin değil açık uyarı. UDF çıkarımı ve taranmış PDF için ayrı OCR ön işlemcisi (CLAUDE.md: VLM OCR değil); ikisi de Mike'da yok, bu yüzden tasarım burada özgün ve ölçülecek (açık soru 4).

**Belge sohbeti.** Belge tam metin olarak bağlama konmaz; token bütçesi altında `belge_ara` / `belge_oku` (sayfalı).

**Sözleşme inceleme ve tablo biçimli toplu inceleme.** Hücre başına küçük çağrı: girdi hibrit erişimle seçilmiş madde/parça, çıktı `json_schema` ile `{status, value, evidence_id}`; sütun tanımı değişince `spec_hash` ile eski hücreler `stale`. Doğrulama kapısı: tür, parça kimliği, alıntının parçada alt dize olması, yürürlük. Mike'ın "satır başına NDJSON" ve "bozuk JSON'da ham metni `done` yaz" davranışları alınmaz ([04](../../../knowledge/mike-tarama/04-tablo-bicimli-inceleme.md)).

## 10. Üretim (Dilim C)

**Redline.** Model tam metin yazmaz. Belge paragraflara bölünür ve kimlik alır (`[p12]`); model `{paragraph_id, find, replace}` üretir (bağlam alanı yok; Mike'ın 40 karakterlik bağlamı 4B için kırılgan). Sistem belgede `find`'ı tekil ve birebir (§6 normalizasyonu) arar, bulamazsa reddeder ve modele hata döner. DOCX'te `w:ins` / `w:del` üretimi, kabul/ret `w:id` düzeyinde, sonuç yeni değişmez sürüm olarak yazılır (atomik karşılaştır-ve-değiştir). Koşu aralığındaki sekme, satır sonu ve dipnot göndermesi yeniden kurulumda kaybolabilir (Mike'da koddan çıkarım, [05](../../../knowledge/mike-tarama/05-belge-isleme-ve-redline.md)); bizde testle kilitlenir.

**Dilekçe ve sözleşme taslağı.** Şablon + kullanıcı parametresi; model yalnız boşlukları doldurur ve bağlayıcı madde metnini kaynaktan alır (model yazmaz). Kalite ayrıca ölçülmeden yayımlanmaz ([ADR-0010](../../adr/gemma4-12b-dersler.md#adr-0010): sadeleştirme doğruluğu düşürdü).

**Vatandaş dili özeti.** Uzman cevabın üstünde sunum katmanı (prompt); eğitim hedefi değildir.

**Workflow.** Kullanıcı düğmeyle seçer; model araçla seçmez. Dosya olarak sürümlenir (YAML ön yüz + markdown, `content_sha256`).

## 11. Onay ve güvenlik (öneri)

| eylem sınıfı | onay |
|---|---|
| okuma (mevzuat, belge) | yok |
| yerel yazma (taslak, yeni belge sürümü) | sürüm değişmez; kabul/ret kartı |
| mevcut belgede değişiklik | kart, tek tek kabul/ret |
| dış bağlayıcı okuma (MCP, Dilim D) | bağlayıcı açıkça etkinleştirilir; yeni araçlar kapalı başlar |
| dış bağlayıcı yazma | her çağrı için sunucu üretimli kart + bağlantı parmak izi; varsayılan açık |

Hash zincirli, yalnız-ekleme denetim kaydı; telemetri kapalı; SSRF koruması dış bağlayıcılar için ([07](../../../knowledge/mike-tarama/07-workflow-mcp-guvenlik.md)).

## 12. Ölçüm: araç çağırma modu

Ölçüm hattına yeni mod (`scripts/olcum_uretim/`, KUNYE.json'lu, ayrı `outputs/eval/<grup>/<run>/`); mühürlü test kümesine ve puanlamaya dokunmaz. Mod omurganın ilk işidir (U1.0, Ekim 2027; [ADR-0105](../../adr/kararlar-0064-0085.md#adr-0105)).

- Birim: araç çağırma görevi (soru + beklenen araç dizisi); deterministik puan: geçerli araç adı, şemaya uyum, doğru madde kimliği, tur sayısı, tekrar çağrı, atıf durumu. Hakem gerekmez (judge-free omurga).
- Karşılaştırmalar: 5 ve 7 araç; kısıtlı çözüm açık ve kapalı.
- Model: Checkpoint 1'in kazananı (F3.6), omurganın kesinleşen araç tanımlarıyla; bir kez ölçülür.
- **Araçlı koşu kapı koşusuna girmez** (ADR-0076 Karar 4): eşit sınav kuralı, bizim kol araç kullanır, rakip kullanamaz. Bu mod ayrı bir `outputs/eval/<grup>/` altında koşar ve hiçbir yayımlanan sayıya karışmaz.
- Çıktı: sonuç kayda (kronoloji); açık soruların (araç sayısı, araç turlarında düşünme, §14) ve ayrı araç RL turunun açılıp açılmayacağının kararına girdi. Araç kullanımının eğitimi Makale 2'ye girmez, Checkpoint 2'den sonra ayrı bir ürün turudur ([ADR-0105](../../adr/kararlar-0064-0085.md#adr-0105)); karar bu belgede verilmez.

## 13. Dilimler ve çıkış ölçütleri

| dilim | içerik | çıkış ölçütü (verify) |
|---|---|---|
| **A: omurga** | `apps/api` + `apps/web` iskeleti, SQLite + Alembic, model profili ve uç nokta arayüzü, ajan döngüsü, yedi araç (beş mevcut + `kullaniciya_sor` + `sure_hesapla`), atıf akışı (§5), iş kuyruğu ve slot muhasebesi, proje yapısı, sohbet, yerel önbellek, süre hesabı | iki eşzamanlı iş + bir etkileşimli sohbet slot sınırı altında çökmeden biter; iptalde uçuştaki iş yazamaz; atıf durumları testle kilitli; `İSTANBUL ISPARTA` vektörleri geçer |
| **B: belgeler** | yükleme + sohbet, sözleşme inceleme, tablo biçimli toplu inceleme | `stale` / `not_found` / `unparseable` ayrı sayılır; taranmış PDF'te açık uyarı |
| **C: üretim** | redline, dilekçe ve sözleşme taslağı, vatandaş özeti | eşleşmeyen `find` reddedilir; DOCX kabul/ret turu belgeyi bozmaz; taslak kalitesi ölçülmeden yayımlanmaz |
| **D: içtihat + MCP** | kapsam ADR'si sonrası | ayrı ADR |

Takvim ([ADR-0105](../../adr/kararlar-0064-0085.md#adr-0105)): tasarım şimdi; omurga kodu Ekim–Aralık 2027, Makale 1 gönderildikten sonra, ilk işi §12 ölçüm modu; dilimler sıralı (A → B → C), tez yazımı başlayınca (Ocak 2028) durur, savunmadan sonra devam eder; çakışmada kağıt hattı kazanır.

## 14. Açık sorular

1. Ön yüz çerçevesi (Next.js mi, daha hafif bir şey mi); yerel tek kullanıcı için SSR gerekir mi?
2. Araç turlarında düşünme kanalı: `answer()` ikinci geçişte kanalı kapatıyor; araç turlarında nasıl kapatılacak ve araç çağrısı kaç token düşünmeyle koşacak?
3. UDF çıkarımı ve OCR ön işlemcisi: hangi kütüphane, ölçüm nasıl?
4. İzin verilen yazma yolu: model yalnız önerir, kullanıcı kabul eder; hangi eylemler bu kuralın dışında kalabilir?
5. vLLM/SGLang'a geçiş ölçümünün tanımı: hangi tablo geçiş kararını verir?
6. Mike'ın varsayılan workflow metinleri taranmadı (ayrı depo); Türk hukuku workflow katalogu nasıl başlayacak?
7. `cekirdek.araclar`'ın döngüsü CLI/TUI için yazıldı; uygulamada eşzamanlı işlerde sınırlı döngü ve `ARAMA_TUKENDI` nasıl taşınacak?
