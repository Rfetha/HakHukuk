# `docs/record/` — araştırma kaydı

Bu klasör **ne olduğunu** tutar; kararların *neden*i [`../adr/`](../adr/)'de, yapılacaklar ve yön [`ROADMAP_v1.md`](../yol_haritasi/ROADMAP_v1.md)'de.

| ne | nerede |
| :--- | :--- |
| **Koşudan önce okunacak tek liste** — sessiz-bozulma kalıpları | [`yurutme-tuzaklari.md`](yurutme-tuzaklari.md) |
| **Artefakt künyesi** — her kol ve merge'in kimliği ⛔ *dokunulmaz* | [`kollar.md`](kollar.md) |
| Yeni hat, girdi **#39 … #52** | [`kronoloji-39-52.md`](kronoloji-39-52.md) |
| Yeni hat, girdi **#53 … #62** | [`kronoloji-53-62.md`](kronoloji-53-62.md) |
| Yeni hat, girdi **#63 … #74** | [`kronoloji-63-71.md`](kronoloji-63-71.md) |
| Checkpoint 1 · F0, girdi **#75 … #86** | [`kronoloji-75-86.md`](kronoloji-75-86.md) |
| Checkpoint 1 · F0 (devam), girdi **#87 …** | [`kronoloji-87-98.md`](kronoloji-87-98.md) |
| Emekli **Gemma 4 12B** hattı, girdi **#01 … #38** | [`gemma4-12b-kronoloji.md`](gemma4-12b-kronoloji.md) |
| Emekli hattın **damıtılmış dersleri** + ADR-0001…0026 | [`../adr/gemma4-12b-dersler.md`](../adr/gemma4-12b-dersler.md) |
| Karar defteri, ADR-0027 ve sonrası | [`../adr/README.md`](../adr/README.md) |

Yeni girdi en yeni `kronoloji-*.md`'nin sonuna yazılır; **numara = son çapa + 1** (#88 kullanılmadı). Dosya
büyüyünce aşama adıyla yenisi açılır. Her girdi bir `<a id="NN"></a>` çapası taşır, atıf biçimi
`kronoloji-63-71.md#70`.

## Hangi belge ne işe yarar

**`yurutme-tuzaklari.md` — koşudan ÖNCE.** *"Hata vermeden yanlış sonuç üreten"* kalıpların listesi;
satırların hepsi bu hatta **fiilen ısırdı**. Bu hattın hata sınıfı çökme değil **sessiz yanlışlıktır**.

**`kollar.md` — artefakt kimliği.** Satırı olmayan artefakt **isimsizdir ve kullanılmaz**.

**`kronoloji-*.md` — ne oldu ve kaç çıktı.** Girdi yalnız makaleye ya da model kartına girecek sayı için
yazılır: ne ölçüldü · sayılar · dosya yolu / `KUNYE.json` · tek paragraf ders; oturum anlatısı ve onay
alıntısı yazılmaz. **Sayılar birebir korunur**; olumsuz ve çürütülmüş bulgular da kalır — bu hattın en
değerli bulgularının bir kısmı **kendi planlarının çürütülmesidir**.

**`../adr/gemma4-12b-dersler.md` — bundan ne öğrendik.** Base-bağımsız dersler + 26 ADR'nin karar
kaydı. **Yeni hatta başlayan önce Bölüm A'yı okur.**

