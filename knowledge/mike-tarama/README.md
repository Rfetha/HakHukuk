# Mike taraması: dizin ve sentez

Kaynak: `Open-Legal-Products/mike` (TypeScript, AGPL-3.0, `main` dalının tarball'ı; tarama günü 2026-10-15). Amaç: HakHukuk için yerel, tek kullanıcılı, 4B modelli bir ajan uygulamasının tasarımına girdi çıkarmak.

**Lisans notu.** Mike AGPL-3.0, bu repo Apache-2.0. Aşağıdaki dosyalar tasarımı anlatır, kod içermez (en fazla 3 satırlık alıntı). Uygulama kodu Mike'a bakılarak değil, buradaki tasarım tarifinden yazılır.

**Güvenilirlik notu.** Satır numaralarının bir kısmı yaklaşık (dosyalarda işaretli). Hiçbir davranış gerçek bir modelle çalıştırılmadı. Türkçe normalizasyon iddialarından biri Node ile doğrulandı, kalanı koddan çıkarımdır. Okunmayan kısımlar her dosyanın "Okunmadı" başlığında sayılıdır.

## Dosyalar

| Dosya | Konu |
|---|---|
| [01-agent-dongusu-ve-araclar.md](01-agent-dongusu-ve-araclar.md) | tur sınırı, araç kataloğu, sistem prompt'u, duraklatma, akış |
| [02-llm-saglayici-ve-yerel-model.md](02-llm-saglayici-ve-yerel-model.md) | sağlayıcı katmanı, yerel model middleware'i, bizim sağlayıcı arayüzü önerisi |
| [03-atif-baglam-hafiza.md](03-atif-baglam-hafiza.md) | atıf doğrulama algoritması, bağlam, enjeksiyon çiti, hafıza |
| [04-tablo-bicimli-inceleme.md](04-tablo-bicimli-inceleme.md) | hücre durum makinesi, eşzamanlılık, hücre başına küçük çağrı tasarımı |
| [05-belge-isleme-ve-redline.md](05-belge-isleme-ve-redline.md) | metin çıkarımı, sürümleme, tracked-change eşleştirme, dışa aktarım |
| [06-veri-modeli-is-kuyrugu-yerel-paket.md](06-veri-modeli-is-kuyrugu-yerel-paket.md) | ER özeti, kuyruk katmanları, masaüstü paketleme, önerilen SQLite şeması |
| [07-workflow-mcp-guvenlik.md](07-workflow-mcp-guvenlik.md) | workflow biçimi, MCP onay akışı, güvenlik, onay çerçevesi |
| [08-arayuz-test-kalite.md](08-arayuz-test-kalite.md) | ön yüz yığını, ekran listesi, test disiplini, olay dersleri |

## Sentez

### 1. Mike ne
Çok kiracılı, buluta bağımlı bir platform: Next.js + Express + Supabase Postgres (66 tablo, RLS) + S3 uyumlu depolama. Ajan döngüsü Mike'ın kendisinin değil, Vercel AI SDK'nın `streamText` döngüsüdür (sert sınır 16 tur; prompt modele "10" der). 14+ araç, ~12 bin karakterlik sistem prompt'u, belgenin tamamı bağlama konur (parçalama, embedding, OCR, token sayımı yok). Yerel model desteği sonradan eklenmiş: metne sızan araç çağrılarını kurtaran bir tolerans katmanı var, araç turları akışsız çalışır.

### 2. Taşınır
- Değişmez belge sürümü + içerik özeti (SHA-256); redline için model yalnız kısa bir `find/replace` komutu üretir, sistem eşleşmeyeni reddeder (05).
- Hücre yazmasını `generation_id` ile korumak, bitmiş hücreleri atlayan yeniden başlatılabilir satır işi (04).
- Kuyruk deseni: tek ifadede talep, `dedupe_key` kısmi benzersiz indeks, çit belirteci, üstel geri çekilme, kalıcı hata ayrımı (06).
- Sıra numaralı SSE, sunucu sahipli tur, `from=` ile yeniden bağlanma, tek durdurma ucu (01, 08).
- Atıfı sunucuda deterministik doğrulamak (fikir olarak; algoritması bizde zaten omurga) (03).
- Yazma eylemleri için sunucunun ürettiği onay kartı, saklı eylem, bağlantı parmak izi (07).
- Workflow'u dosya olarak sürümlemek (YAML ön yüz + markdown), masaüstünde derleme anında gömüp kurulumda özet doğrulamak (07).
- Enjeksiyon çiti (nonce'lı sahte-etiket temizliği) ucuz ve modelden bağımsız (03).

### 3. 4B için yeniden tasarlanmalı
- **Araç yüzeyi:** 14+ araç yerine 5 düz şemalı araç: `mevzuat_ara`, `madde_getir`, `belge_ara`, `belge_oku` (sayfalı), `kullaniciya_sor`. Adım başına tek çağrı, tekrar kesici, açık hata mesajı ve en çok 2 düzeltme hakkı (01).
- **Retrieval sunucu işi:** hibrit erişim sonucu, modele sormadan bağlama girer; ölçülen yol korunur (01, 03).
- **Kısıtlı kod çözme:** araç çağrısı ve hücre çıktısı GBNF / `json_schema` ile zorlanır; metinden araç kurtaran tolerans katmanı yalnız üçüncül yedek (02).
- **Atıf:** model yalnız `madde_id` seçer, alıntıyı sunucu kaynaktan çeker; üç durumlu doğrulama (doğrulandı, doğrulanamadı, denetlenmedi); gövdedeki "m. N" anmaları atıf kümesiyle denetlenir (03).
- **Tablo inceleme:** hücre başına küçük çağrı; durumlar `bulundu`, `bulunamadi`, `ayristirilamadi`, `dogrulanamadi` ayrı; aşırı ret ayrıca ölçülür; sütun tanımı değişince `spec_hash` ile hücreler `stale` olur (04).
- **Redline şeması:** kimlikli paragraflar (`[p12]`), `{p, bul, yerine}`, bağlam alanları yok (05).
- **Bağlam bütçesi:** token sayımı ve kırpma bizde baştan olmalı (Mike'da yok) (02).
- **Model profili:** temel model bir parametre olduğu için (Qwen ve Gemma'nın sohbet şablonu, araç çağrısı biçimi ve düşünmeyi kapatma işareti farklı) bunlar tek bir model profili arkasında durur; Qwen profili tam, Gemma profili iskelet (02).
- **Eşzamanlılık:** sınır sunucunun paralel slot sayısıdır; etkileşimli iş tüm yuvaları, toplu iş en çok G-1 yuvayı kullanır; açılışta `boot_id` ile yetim işler kurtarılır. Tasarım önerisi, ölçülmedi (06).
- **Workflow:** model araçla seçmesin, kullanıcı düğmeyle seçsin; şablon doğrudan prompt'a girsin (04, 07).
- **Onay çerçevesi:** yazma onayı varsayılan açık, yeni araçlar kapalı başlar, araç tanım özeti onaya bağlı, hash zincirli yalnız-ekleme denetim kaydı, telemetri kapalı (07).

### 4. Taşınmaz
Çok kiracılı katman (organizasyon, RLS, izin tabloları), Redis/BullMQ, Postgres'e özgü özellikler (`skip locked`, `security definer`, `pg_trgm`), 12 KB prompt, serbest 16 turluk planlama, modelin `<CITATIONS>` JSON'unu hatasız yazması, LLM tabanlı hafıza düzenleyicisi, Electron içinde Postgres + GoTrue + PostgREST süreç ağacı.

### 5. Mike'ın "sessiz yanlışlık" tuzakları (bizim tuzak listemizle aynı sınıf)
- Doğrulama bayrağı boş atıf "doğrulandı" görünür (fail-open); iptal/hata turlarındaki ve tablo atıfları hiç doğrulanmaz (03, 08).
- Bozuk JSON'da ham metnin ilk 500 karakteri `done` hücre olarak yazılır (04).
- Bozuk araç argümanı sessizce `{}` olur (01).
- "Bulunamadı" üç ayrı dizeyle ve gri bayrakla karışır; sütun prompt'u düzenlenince eski hücreler geçersiz sayılmaz (04).
- Belge sürümü değişmezliği veritabanında değil, uygulama kuralıyla sağlanır; hash zinciri yok (05, 06).

### 6. Türkçe'ye özgü kusurlar (ADR'ye girecek)
`toLowerCase` ile `İ` iki karakter olur ve konum haritasını kaydırır; `İ`/`ı` birbiriyle eşleşmez; noktalama silme "1.500" ile "15,00" değerlerini aynı yapar; ön yüz vurgulayıcı ç ğ ı ö ş ü harflerini siler; belge üretimi ASCII varsayar (03, 05). Bizde normalizasyon yerel ayara duyarlı, tek bir yerde ve testle kilitli olmalı.

## Ölçülmeden karar verilemeyecekler
1. Uygulamanın modeli Checkpoint 1'in kazananı olacak (Qwen3.5-4B ya da Gemma 4 E4B; roadmap F3.6 ve F3b); bugünkü yayımlı sürüm `tgta_v1`. Kendi araç şemamızla araç çağırma doğruluğu ölçülmedi. Mevcut eğitim tarifinde (τ_g, τ_a, ORPO) araç çağırma dalı yok; eklenip eklenmeyeceği açık soru ve F1.11 dondurmasını etkiler.
2. llama.cpp slot sayısına karşı vLLM/SGLang geçişinin gerçek kazancı; geçiş ürün yolu kilidini (ADR-0078, ADR-0080) etkiler.
3. Türkçe belge hattı: UDF çıkarımı ve taranmış PDF için OCR (Mike'da yok, bizde ayrı ön işlemci).
4. Mike'ın varsayılan workflow metinleri ayrı depoda (`mike-workflows`) ve taranmadı; Türk hukuku uyarlaması yalnız adlardan tahmin edildi.
