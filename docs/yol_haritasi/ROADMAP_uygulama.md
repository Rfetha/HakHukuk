# ROADMAP uygulama: ajan uygulaması hattı

> **Bu belge ne:** [ADR-0104](../adr/kararlar-0064-0085.md#adr-0104) ve [ADR-0105](../adr/kararlar-0064-0085.md#adr-0105)'in kararlarını iş adımlarına çevirir.
> *Neden* ADR'de ve [`tasarım taslağında`](../superpowers/specs/2026-10-15-uygulama-hatti-tasarim.md), *ne zaman ve
> hangi sırayla* burada. Girdi: [`knowledge/mike-tarama/`](../../knowledge/mike-tarama/README.md).
> Makale hattı ([`ROADMAP_v1.md`](ROADMAP_v1.md)) ayrıdır; bu hat onu bozmaz.
>
> **Biçim:** her iş `iş → doğrulama`; doğrulaması geçmeyen iş bitmiş sayılmaz. Tarihler hedeftir, ölçüm değildir.

## Kurallar

1. **Çakışmada kağıt hattı kazanır.** Kullanıcı kapasitesi haftada 5 saatin altındadır ve Mayıs–Haziran 2027'de yük
   zaten bu sınıra dayanır, Haziran–Eylül 2027 Makale 1'in yazımıdır ([`YAYIN_YOL_HARITASI.md`](YAYIN_YOL_HARITASI.md) §5),
   Ocak–Haziran 2028 tez ve Makale 2'nin yazımıdır (§3.6). Bu hat aradaki boşlukta, Ekim–Aralık 2027'de yürür. Takvim
   geriye kayarsa ilk kesilen bu hattır.
2. **Ürün yolu = ölçüm yolu** ([ADR-0080](../adr/kararlar-0064-0085.md#adr-0080)); araçlı koşu kapı koşusuna girmez
   ([ADR-0076](../adr/kararlar-0064-0085.md#adr-0076) Karar 4) ve hiçbir yayımlanan sayıya karışmaz.
3. **Araç kullanımının eğitimi Checkpoint 2'den sonra ayrı bir ürün turudur** ve yalnız araç çağırma ölçümü (U1.0)
   açık bir boşluk gösterirse açılır; Makale 2'nin ödülüne girmez ([ADR-0105](../adr/kararlar-0064-0085.md#adr-0105)).
4. **Model bir parametredir:** uygulama Checkpoint 1'in kazananına bağlanır (F3.6, F3b); hedef şimdilik `tgta_v1`.
5. Her dilim başlarken kendi uygulama planı yazılır (`docs/superpowers/plans/`, en çok bir canlı plan,
   [ADR-0056](../adr/kararlar-0045-0063.md#adr-0056)); makale hattının canlı planıyla aynı anda iki plan olmaz.
6. **Dilimler sıralıdır:** A → B → C. Hiçbir dilim başka bir dilimle ya da tez yazımıyla aynı anda yürümez. Ocak
   2028'de tez yazımı başlayınca hat nerede kaldıysa durur, savunmadan sonra (yaz 2028) kaldığı yerden devam eder
   ([ADR-0105](../adr/kararlar-0064-0085.md#adr-0105)).

## Kontrol listesi

**U0 · Zemin** *(Ekim 2026; yalnız tasarım)*

- [x] U0.1 Mike taraması `knowledge/mike-tarama/` altında (sekiz alan + sentez)
- [x] U0.2 ADR-0104 ve tasarım taslağı
- [x] U0.3 Kararların denetimi: ADR-0105 (takvim, araç çağırma ölçümünün yeri, araç RL'i)

**U1 · Dilim A: omurga** *(Ekim–Aralık 2027, Makale 1 gönderildikten sonra; kullanıcı ~8-12 saat, tahmin)*

- [ ] U1.0 Araç çağırma ölçüm modu (eski F1.12): Checkpoint 1'in kazananı, omurganın araç tanımları; sonuç kayda geçti; taslağın açık soruları (araç sayısı, araç turlarında düşünme) ve ayrı araç RL turunun açılıp açılmayacağı yazıldı
- [ ] U1.1 `apps/api` iskeleti: FastAPI, `cekirdek` import, SQLite + Alembic, dosya deposu
- [ ] U1.2 Model profili ve OpenAI-uyumlu uç nokta arayüzü (Qwen tam, Gemma iskelet), `count_tokens` ve `slots`
- [ ] U1.3 Ajan döngüsü ve araç seti (`cekirdek.araclar`'ın beş aracı + `kullaniciya_sor` + `sure_hesapla`); sınırlı döngü, `ARAMA_TUKENDI`
- [ ] U1.4 Atıf KAPI'sı: üç durum, fail-closed; Türkçe normalizasyon modülü ve ortak test vektörleri
- [ ] U1.5 İş kuyruğu ve slot muhasebesi; iptal, yeniden deneme, açılışta yetim kurtarma
- [ ] U1.6 `apps/web` + `packages/contracts`: sohbet, proje, atıf gösterimi, SSE ve yeniden bağlanma

**U2 · Dilim B: belgeler** *(U1 bitince, sıralı; tez yazımına denk gelirse savunmadan sonra)*

- [ ] U2.1 Belge yükleme ve sohbet; metin çıkarımı hattı (DOCX, PDF, metinsiz PDF uyarısı)
- [ ] U2.2 Sözleşme inceleme
- [ ] U2.3 Tablo biçimli toplu inceleme (hücre başına küçük çağrı, ayrı hücre durumları)

**U3 · Dilim C: üretim** *(U2 bitince, sıralı; tez yazımına denk gelirse savunmadan sonra)*

- [ ] U3.1 Redline (kimlikli paragraflar, tekil ve birebir eşleştirme, kabul/ret)
- [ ] U3.2 Dilekçe ve sözleşme taslağı (kalite ölçülmeden yayımlanmaz)
- [ ] U3.3 Vatandaş dili özeti (sunum katmanı)

**Dilim D (içtihat arama, MCP)** bu listede yok: kapsam ADR'si gerekir (CLAUDE.md "yalnız güncel mevzuat"), sonra eklenir.

## İşler

| # | iş → doğrulama |
| :-- | :--- |
| U1.0 | **Araç çağırma ölçüm modu** (eski F1.12; `scripts/olcum_uretim/`, künyeli, ayrı `outputs/eval/<grup>/`), Checkpoint 1'in kazananı üzerinde, omurganın araç tanımlarıyla; deterministik puan: geçerli araç adı · şemaya uyum · doğru `(kanun_no, madde_no)` · tur sayısı · tekrar çağrı · atıf durumu, hakem yok; 5 ve 7 araç, kısıtlı çözüm açık ve kapalı → koştu, künye yazıldı, mühürlü kümeye dokunmadı, hiçbir yayımlanan sayıya karışmadı |
| U1.1 | **API iskeleti:** boş veritabanından başlar, Alembic yükseltmesi çalışır → testli |
| U1.3 | **Ajan döngüsü:** bozuk araç argümanı sessizce boşaltılmaz, modele açık hata döner; aynı argümanla ikinci çağrı kesilir → testli |
| U1.4 | **Atıf KAPI'sı:** bayrak boşsa `denetlenmedi`; `İSTANBUL ISPARTA`, `ığüşöç`, `1.500` / `15,00` vektörleri geçer → testli |
| U1.5 | **Kuyruk:** iki eşzamanlı iş ve bir etkileşimli sohbet slot sınırı altında çökmeden biter; iptalde uçuştaki iş yazamaz → testli |
| U2.3 | **Tablo inceleme:** `stale`, `not_found`, `unparseable` ayrı sayılır; sütun değişince eski hücreler `stale` → testli |
| U3.1 | **Redline:** eşleşmeyen `find` reddedilir; DOCX kabul/ret turu belgeyi bozmaz → testli |

Diğer işlerin doğrulaması dilimin kendi planında yazılır.

## Bağımlılıklar

| bağımlılık | etkisi |
| :--- | :--- |
| F0.9 (Gemma kapısı) | Gemma model profili yalnız kapıyı geçerse doldurulur |
| F3.6 / F3b (kazanan) | U1.0 ve U1.2 kazananla yapılır |
| Makale 1 gönderimi (F5, Eylül 2027) | U1 ondan sonra başlar |
| tez yazımı (Ocak 2028) | hat nerede kaldıysa durur, savunmadan sonra devam eder |

## Bu hattın dışında

Canlı `bedesten` API (B6), tazelik boru hattı, barındırma (S9), kapsam genişlemesi (40.496 → ~288 bin madde) ve
araç kullanımının eğitimi: Checkpoint 2'den sonra ([`ROADMAP_v1.md`](ROADMAP_v1.md) §9, [ADR-0105](../adr/kararlar-0064-0085.md#adr-0105)).
