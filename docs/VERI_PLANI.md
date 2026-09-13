# HakHukuk — Veri Planı (Faz 1)

> ## ⚠️ ÇERÇEVE GÜNCELLENDİ (2026-08-03)
>
> Bu belge **tez** döneminde yazıldı. Veri kaynakları, EDA kararları ve *"lisans-temiz"*
> kuralı **aynen geçerli** — hatta OSS'e geçiş bu kural sayesinde sonradan temizlik
> gerektirmedi. Değişenler:
>
> | | eski | yeni |
> | :--- | :--- | :--- |
> | proje | tez, private+proprietary | **OSS, Apache-2.0** ([`ROADMAP.md`](../ROADMAP.md) *(2026-09-06'da silinmişti, 2026-09-07'de yeniden yazıldı)*) |
> | `TEKNIK_PLAN.md` atıfları | aktif plan | **arşive** alınmıştı; `docs/_arsiv/` 2026-09-06'da **silindi** — yerine geçen yön belgesi [`ROADMAP.md`](../ROADMAP.md) |
> | hedef kitle | uzman (ADR-0010) | **vatandaş** — ama ADR-0010 **hâlâ yürürlükte**: sade dille *eğitmek* doğruluğu düşürdü, sadeleştirme **istem katmanında** yapılır |
> | "tez kapsamı dışı" ibareleri | tez sınırı | artık **kapsam kararı** — graph-RAG ve içtihat katmanı yeniden açılabilir (ADR-0019 kilidi kalktı) |

> Faz 1 SFT verisinin **ne**, **nereden**, **nasıl** sorularının cevabı. `TEKNIK_PLAN.md` Adım 3-4'ün detaylandırılmış hali.
>
> **Altın kural (acı tecrübeyle sabit):** Hiçbir hazır veri setine bakmadan güvenme. Kullanmadan önce örnek çekip **EDA (göz denetimi)** yap. Asıl güvenilir zemin = **otoriter/resmi kaynak** (Mevzuat.gov.tr güncel kanunlar). Kapsam: **güncel Türkiye Cumhuriyeti mevzuatı** — Osmanlı/mülga/eski-dil metinler dışarıda.

---

## 1. Hangi veri tiplerine ihtiyacımız var

> ⚠️ **REVİZE (2026-06-13/14, ADR-0010 + V2_PLAN):** birincil register = uzman; "sade cevap" hedefi app-layer'a taşındı. Aktif v2b verisi = **RAFT** (gold+distractor + verbatim alıntı + abstention dilimi), uzman-register. Aşağıdaki tablo Faz-1 ilk kapsamı, iz olarak korunuyor.

| # | Veri tipi | Format | Kaynak yaklaşımı |
| :-- | :--- | :--- | :--- |
| 1 | Genel hukuk Q&A | soru → cevap | Hazır (doğrulanmış) + üretim |
| 2 | Terim sadeleştirme | terim/cümle → ~~sade dil~~ *(app-layer)* | **Üretim** (grounded) |
| 3 | Madde özetleme | kanun metni → özet | **Üretim** (Mevzuat + LLM) |
| 4 | Senaryo → ilgili madde | olay → madde atıfı | **Üretim** (grounded) |
| 5 | Niş (kira/iş/tüketici) | senaryo → ~~sade cevap~~ **uzman-register cevap**/dilekçe (app-layer sadeleştirir) | **Üretim** + niş hazır setler |
| 6 | Eval seti | soru → doğru cevap | Kendi setimiz (CORE-HARD + TRAP) + hakem |

---

## 2. Kaynak Envanteri (EDA bulgularıyla — 2026-05-29 taraması)

`scripts/_legacy/scan_hf_datasets.py` ile tarandı (72 aday). Durum işaretleri göz denetimine dayanır. *(Not: v0-era EDA scriptleri artık `scripts/_legacy/` altında.)*

### ✅ Kullanılabilir (doğrulandı, temiz — `scripts/_legacy/eda_datasets.py` ile tam EDA)
| Kaynak | Lisans | Hacim | EDA bulgusu |
| :-- | :-- | :-- | :-- |
| `OrionCAF/turkish_law_qa_dataset` | Apache 2.0 | 18.305 | %0.7 mükerrer, 0 boş. Soru ~11 / cevap ~19 kelime (kısa-öz). İş K./TCK/idari geniş, düzgün noktalama. **Birincil hazır Q&A.** |
| `Renicames/turkish-law-chatbot` | Apache 2.0 | 14.854 | %0 mükerrer. Anayasa ağırlıklı. **Uyarı:** metin küçük-harfli, %4.3 cevap <5 kelime → temizlikte normalize + kısa-cevap süz. |
| **`muhammetakkurt/mevzuat-gov-dataset`** | MIT (metin kamu) | 907 kanun / **40.853 madde** | **OTORİTER KANUN ZEMİNİ.** Yapılı (kanun→madde→metin), Eylül 2024'e dek. Boş madde %0.9. **Tüm nişler var:** İş 4857, Tüketici 6502, Borçlar 6098, Medeni 4721, Anayasa 2709. Grounded üretimin kaynağı + Faz 2 RAG. |
| Mevzuat.gov.tr (direkt) | Kamu | tüm mevzuat | Gerekirse genişletme. **NOT: yabancı IP'yi (VPN) firewall'da engelliyor — TR IP'den erişilir.** PDF metin-tabanlı (`%PDF-1.7`), OCR genelde gerekmez. |

> **EDA notu (2026-05-29):** İki hazır set birleşince ~33K temiz güncel-TC Q&A. İkisinde de cevaplar **uzman dilinde** (sade değil) → sadeleştirme katmanı üretimle eklenecek. İki set arası çapraz-mükerrer kontrolü birleştirmede yapılacak.

### ⚠️ Doğrulanacak / işlenecek (umut var, dikkat)
| Kaynak | Lisans | Not |
| :-- | :-- | :-- |
| `kilicai/tbk-...`, `tmk-...`, `tapu-...` SFT setleri | cc-by-4.0 | Niş (Borçlar=kira, Medeni). Viewer kapalı; indirip EDA yapılacak |
| `abdullah-altunkaynak/Turkish-Labor-Law-Dataset` | Apache 2.0 | İş hukuku nişi; viewer hatası, indirilip bakılacak |
| `yusufbaykaloglu/University_Mevzuat_QA(_v2)` | Apache 2.0 | Üniversite mevzuatı — niş dışı olabilir |
| `erdem-erdem/Turkish-Law-Documents-700k-clustered` | ? | Yargıtay/Danıştay — **Faz 2 RAG** için, Faz 1 SFT değil |

### ❌ Reddedildi
| Kaynak | Sebep |
| :-- | :-- |
| `newmindai/EuroHPC-Legal` | **EDA'da çöp çıktı:** soru-cevap eşleşmiyor, rastgele isimler, uydurma kanun ("Veyra Lojistik Kanunu"), Osmanlı/alakasız içerik. Sentetik ama grounding'siz. |
| `tuncgulec1979/Kanunlar` | Satır-parçalı + eski-dil mülga metinler karışık; Mevzuat'tan temiz çekmek daha iyi |
| Lexpera / Kazancı vb. ticari | Telif — katı yasak |

### ⏸️ Değerlendirildi → **Faz 2'ye ertelendi** (tez kapsamı dışı)

| Kaynak | Ne · neden şimdi değil |
| :-- | :-- |
| [`erdem-erdem/Turkish-Law-Documents-700k-clustered`](https://huggingface.co/datasets/erdem-erdem/Turkish-Law-Documents-700k-clustered) *(2026-07-29)* | **İçtihat**, mevzuat değil: 702.295 satır · 1.75 GB · Yargıtay + Danıştay kararları (2006-2024), `fikriokan` repo'larından yeniden paketlenmiş; alanlar `text`/`source`/`esasNo`/`kararNo`/`kararTarihi` + 4 küme kimliği (e5 KNN/HDBSCAN). **Korpusumuzla kesişimi sıfır.** 🚫 **Lisans belirtilmemiş** → varsayılan "tüm hakları saklı"; kaynak portallar açık ama bu paketleme değil, kullanılacaksa kaynaktan çekilir. ⚠️ **EDA borcu** — kümeleme etiketleri metnin kalitesi hakkında hiçbir şey söylemez (EuroHPC dersi). **Tez için kullanım yeri yok:** eğitim değil (kapsam mevzuat; içtihat uzman-uzun kayıt, register'ı kaydırır) · harness retriever değil (ADR-0019 graph-RAG'i dışarıda bırakıyor, Sprint 4 mevzuat üzerinde) · distractor madenciliği değil (tür farkı distractor'ı fazla kolaylaştırır). **Gerçek değeri Faz 2/3 içtihat katmanı** — orada da muhtemelen bedesten API'sinden (`docs/BEDESTEN_API.md`), taze ve lisans zinciri temiz. *Bkz. açık kararlar *(soruları taşıyan `docs/open_questions.md` 2026-09-07'de, onları devralan plan da 2026-09-12'de silindi; grill'e girecek dokuz madde [ADR-0083](adr/kararlar-0064-0085.md#adr-0083) §EK E.5'te)** |

---

## 3. Üretme Pipeline'ı ("üretme pipeline bulamaz mıyız?" → evet)

Eksik veri tiplerini (2,3,4,5) üretmenin iki yolu var. **İkisini de kullanırız.**

### Yol A — Otoriter zemin (HAZIR — scraping gerekmiyor)
1. **Tercih (canlı):** **`bedesten.adalet.gov.tr/mevzuat` JSON API** — `mevzuat-mcp`'den reverse-engineer edildi + test edildi (çalışıyor). Auth/Playwright yok. Arama + tam metin + madde ağacı. **Hep güncel, tam kapsam.** Contract: **`docs/BEDESTEN_API.md`**, istemci: `scripts/erisim_korpus/bedesten_probe.py`. **TR IP gerekir.**
2. **Bulk/çevrimdışı:** `muhammetakkurt/mevzuat-gov-dataset` → 907 kanun / 40.853 madde (Eylül 2024 donmuş). Zaten indirildi: `data/raw/mevzuat_maddeler.jsonl`.
3. **Genişletme (gerekirse):** `mevzuat-gov-scraper` (MIT, Scrapy+Selenium).
4. (Faz 2) İçtihat: **aynı backend** `bedesten.adalet.gov.tr` (yargi-mcp); contract sırası gelince çıkarılır.

> **ℹ️ Bilgi — neden bu zemin kritik?** Üreteceğimiz her şeyin gerçek, güncel kanuna dayanması (grounding) şart. EuroHPC tam burada battı: gerçek metne bağlamadan üretmiş → halüsinasyon. Biz gerçek maddeyi alır, üretimi ona bağlarız.

### Yol B — Grounded sentetik üretim (asıl pipeline)
**Motor: GPT-4o-mini** (~$13 bulk, OpenAI API key hazır). Gemini plan dışı.

Gerçek kanun maddesini **kaynak** olarak ver, ürettir:
- Madde → vatandaş sorusu + **sade dil** cevap (Tip 1, 5)
- Hukuki terim → günlük dil karşılığı (Tip 2)
- Madde → kısa özet (Tip 3)
- Madde → gerçekçi senaryo + doğru atıf (Tip 4)
- **32K uzman cevabı → GPT-4o-mini ile sadeleştir** (mevcut Q&A'yı vatandaşlaştırma)

**Sıra (kilitli — S4):** Önce v0 baseline (32K uzman) → Muhakim ile açığı gör → üretimi açığa yönlendir. Körlemesine üretim yok.

**Kritik:** Her örnekte `kaynak_madde` alanı tut. Geri-doğrulama (Muhakim: "cevap maddeyle tutarlı mı?") ile süz. Tutmayan atılır.

### Yol C — Hazır setleri doğrula & süz
`OrionCAF`, `Renicames` EDA geçti ✅. Niş setleri (kilicai TBK/TMK, Labor Law) sırası gelince.

### Hazır araçlar (sıfırdan yazmıyoruz)
| İş | Araç |
| :-- | :-- |
| Üretim motoru | **GPT-4o-mini** (OpenAI API, ~$13 bulk) |
| Toplu temizleme/filtre/dedup | **datatrove** + **SemHash** |
| OCR (gerekirse) | **DotsOCR** (VLM tabanlı) |
| Türkçe morfoloji filtresi | **Zemberek** (suffix entropy, lemma diversity) |
| Üretilen veri geri-doğrulama | **Muhakim** (Apache 2.0) |

---

## 4. Temizleme & Format (Mecellem reçetesi)
exact-hash dedup → SemHash semantik dedup (0.75) → FineWeb kalite → GlotLID (sadece TR) → Zemberek morfoloji (suffix>%75, lemma>%50) → token ≤4096 → tek chat-template (`messages`, ~~Qwen~~ **Gemma 4 uyumlu**; base değişti ADR-0003) → PII maskeleme → train/val/test (test izole).

---

## 5. İlerleme & sıradaki iş

**✅ Tamamlandı (2026-05-29):**
- HF tarama (`scripts/_legacy/scan_hf_datasets.py`) → 72 aday, EuroHPC reddi.
- Tam EDA (`scripts/_legacy/eda_datasets.py`) → OrionCAF + Renicames doğrulandı.
- **SFT v0 inşa edildi** (`scripts/_legacy/build_sft_dataset.py`) → `data/processed/sft_v0/` : **32.234** temiz chat-template Q&A (train 29.028 / val 1.582 / test 1.624, hash-split). *Uzman dilinde. (Not: v0 SFT'yi batırdı → v1/v2b'ye KATILMADI.)*

**✅ Tamamlandı (devam, 2026-05-29):**
- Mevzuat erişimi çözüldü: mevzuat.gov.tr yabancı IP (VPN) engelliyor; TR IP'den PDF iniyor.
- **Otoriter kanun zemini bulundu & doğrulandı:** `muhammetakkurt/mevzuat-gov-dataset` (907 kanun / 40.853 madde, tüm nişler). Scraping/OCR gereği Faz 1'de kalktı.

> ⚠️ **SÜPERSED (2026-07-01) → aşağıdaki "Sıradaki" listesi TAMAMLANDI/İPTAL.** v0 koştu (başarısız), grounded v1 üretildi + eğitildi, v2b verisi (19.305, RAFT+replay+truncation-fix) hazır. **32K sadeleştirme (#3) İPTAL** (ADR-0010, app-layer). Güncel sıradaki iş: `docs/V2_PLAN.md §9` + `NEXT_SESSION.md`. Aşağı iz olarak korunuyor.

**⏭️ ~~Sıradaki (WSL2 ortamı kurulduktan sonra)~~ — TARİHSEL:**
1. **Bulk kanun çekimi:** Bedesten API ile 916 kanunu `data/raw/mevzuat/{TUR}/` altına kategorize kaydet (`scripts/erisim_korpus/bedesten_probe.py` → genişlet). *(Faz 2'ye ertelendi)*
2. **v0 baseline SFT:** 32K uzman veri ile eğit → Muhakim ölç → açığı belirle. ✅ *(başarısız, ders alındı)*
3. **~~32K sadeleştirme:~~ İPTAL (ADR-0010):** GPT-4o-mini ile uzman cevapları → sade dil (~$13). *(sadeleştirme app-layer)*
4. **Kanıt koşusu:** 50 örnekle grounded üretim (GPT-4o-mini + gerçek madde) → doğrulama. ✅
5. Ölçekle → sft_v1 → iteratif SFT. ✅ *(v1 + v2b)*
6. Niş setleri (kilicai TBK/TMK, Labor Law) EDA + entegre (sırası gelince).
