# `docs/record/` — araştırma kaydı

Bu klasör **ne olduğunu** tutar; kararların *neden*i [`../adr/`](../adr/)'de, yapılacaklar
[`../../TODO.md`](../../TODO.md)'de, yön [`../../ROADMAP.md`](../../ROADMAP.md)'de.
*(`TASARIM.md` 2026-09-06'da silindi — ölçüm protokolü `adr/` + bu klasörde yaşıyor.)*

| ne | nerede |
| :--- | :--- |
| **Koşudan önce okunacak tek liste** — 85 sessiz-bozulma kalıbı | [`yurutme-tuzaklari.md`](yurutme-tuzaklari.md) |
| **Artefakt künyesi** — her kol ve merge'in kimliği ⛔ *dokunulmaz* | [`kollar.md`](kollar.md) |
| Yeni hat, girdi **#39 … #52** | [`kronoloji-39-52.md`](kronoloji-39-52.md) |
| Yeni hat, girdi **#53 … #62** | [`kronoloji-53-62.md`](kronoloji-53-62.md) |
| Yeni hat, girdi **#63 … #71** | [`kronoloji-63-71.md`](kronoloji-63-71.md) |
| Emekli **Gemma 4 12B** hattı, girdi **#01 … #38** | [`gemma4-12b-kronoloji.md`](gemma4-12b-kronoloji.md) |
| Emekli hattın **damıtılmış dersleri** + ADR-0001…0026 | [`../adr/gemma4-12b-dersler.md`](../adr/gemma4-12b-dersler.md) |
| Karar defteri, ADR-0027…0086 | [`../adr/README.md`](../adr/README.md) |

**Yeni girdi #72'den devam eder** → `kronoloji-63-71.md`'nin sonuna yazılır; dosya 12 girdiyi
aşarsa `kronoloji-72-….md` açılır. Her girdi bir `<a id="NN"></a>` çapası taşır, atıf biçimi
`kronoloji-63-71.md#70`.

## Hangi belge ne işe yarar

**`yurutme-tuzaklari.md` — koşudan ÖNCE.** *"Hata vermeden yanlış sonuç üreten"* kalıpların listesi;
85 satırın hepsi bu hatta **fiilen ısırdı**. Bu hattın hata sınıfı çökme değil **sessiz yanlışlıktır**.

**`kollar.md` — artefakt kimliği.** Satırı olmayan artefakt **isimsizdir ve kullanılmaz**.

**`kronoloji-*.md` — ne oldu ve kaç çıktı.** Her girdi: künye · tam skor kartı · ölçüm dosyalarının
yolları · ders. **Sayılar birebir korunur**; olumsuz ve çürütülmüş bulgular da kalır — bu hattın en
değerli bulgularının bir kısmı **kendi planlarının çürütülmesidir**.

**`../adr/gemma4-12b-dersler.md` — bundan ne öğrendik.** Base-bağımsız dersler + 26 ADR'nin karar
kaydı. **Yeni hatta başlayan önce Bölüm A'yı okur.**

---

> ⚠️ **Birleştirme notu — iki kez yapıldı, ikisi de insan kararı.**
> **2026-07-24:** 38 tekil `research_log` girdisi + 26 tekil ADR ikişer belgede toplandı
> (`4d70a77` ve öncesi).
> **2026-09-13:** kayıt katmanı **103 dosyadan 12'ye** indirildi — `research_log/` (33 girdi) üç
> kronoloji dosyasında, `adr/` (58 ADR) üç karar dosyasında birleşti; dört fazlalık belge silindi
> ([ADR-0086](../adr/kararlar-0064-0085.md#adr-0086)). Geri alma noktası **`301a82f`**.
>
> İkisi de ADR-0024'ün *"`research_log/` ve `adr/` yerinde kalır"* kuralından **bilinçli sapmadır**.
> Gerekçe aynı: yüzlerce belgelik okuma yüzeyi, yeni hatta başlayan için filtresiz bir yığındır.
> Kuralın özü — **içerik silinmez, sayılar kaybolmaz, çapalar korunur** — ikisinde de tutuldu.
