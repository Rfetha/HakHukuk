# F0.1 — erişim teşhisi: `recall@10`'un kaçırdığı 10 kalem

**Tarih:** 2026-09-06 · **kaynak:** `outputs/eval/s2-harness-k10-etiketli/h1_tgta_v1_h1_k10_et_detail.jsonl`
(alan `harness.altin_sirasi`) · **n=80** · indeks `data/index/mevzuat_bge_m3_s2` · k=10 ·
retriever hibrit BM25 + `BAAI/bge-m3` + RRF · **yeni ölçüm koşulmadı, üretim koşusundan okundu ($0)**

## Çıpa kapısı ✅

`recall@10` = **0,8750** (70/80) — `outputs/eval/g2-fl-harness/KUNYE.json`'daki
`recall_at_10` ile **birebir**. Çıpa kaymamış; eşit sınav zemini sağlam.

| | değer |
| :--- | ---: |
| `recall@1` | 0,6250 |
| `recall@3` | 0,6875 |
| `recall@5` | 0,7875 |
| **`recall@10`** | **0,8750** |

Altın sıra dağılımı (0 = ilk sıra): `0:36 · 1:14 · 2:2 · 3:3 · 4:5 · 5:3 · 6:2 · 7:4 · 9:1`
⇒ altın getirilen 70 kalemin **36'sında birinci sırada**; kuyruk 5-9 arasına dağılmış.

## 🚨 Asıl bulgu: kaybın YARISI erişim değil, SORU

10 kalem gözle okundu. Uygulanan ölçüt: *"soruyu tek başına okuyan bir hukukçu, altın maddeyi
adlandırabilir mi?"* Adlandıramıyorsa kusur retriever'da değil, **yer-gerçeğinin sorusundadır.**

| sınıf | kalem | sayı |
| :--- | :--- | ---: |
| **(e) soru altın maddeyi belirlemiyor** | 0 · 6 · 27 · 33 · 58 | **5/10** |
| **(d) yakın-komşu / sözcük tuzağı** — gerçek erişim hatası | 21 · 28 · 42 · 51 · 61 | **5/10** |
| (a) sorgu-madde örtüşmesi yok *(saf)* | — | 0 |
| (b) tablo/chunk bölünmesi (borç B9) | — | 0 |
| (c) yürürlük / alt-madde kimliği (S2) | — | 0 |

### (e) — soru altın maddeyi belirlemiyor · 5 kalem

| id | soru | altın | neden ölçüt karşılanmıyor |
| :-- | :--- | :--- | :--- |
| 0 | *"Mahkeme benim lehime bir karar verirse ne olur?"* | İİK 31/a | soruda ne icra, ne haciz, ne ilam geçiyor |
| 6 | *"İhbar ettikten sonra ne olacak?"* | 6284 md 7 | hangi ihbar, hangi kanun — hiçbir bağlam yok |
| 27 | *"Mahkeme hangi kurallara göre karar verir?"* | Kat Mülkiyeti K. 33 | kat mülkiyetine dair tek kelime yok |
| 33 | *"Başvurum kabul edilirse ne olur?"* | 6284 md 10 | hangi başvuru belirsiz |
| 58 | *"Birisi silah bulunduruyorsa ne olur?"* | 6284 md 6 | retriever **Ateşli Silahlar Kanunu**'nu getirdi — sözlük olarak doğru; altın ise aile içi şiddet tedbiri, soruda o bağlam yok |

### (d) — gerçek erişim hatası · 5 kalem

| id | soru | altın | getirilen 1 | teşhis |
| :-- | :--- | :--- | :--- | :--- |
| 21 | para birimi belirtme | TBK 99 | *Para Birimi Hakkında Kanun md 1* | başlık eşleşmesi doğru maddeyi eziyor |
| 28 | eklenti ayıplıysa ana ürün | TBK 230 | *Ürün Güvenliği K. 19* | **"ürün"** sözcük tuzağı; altının dili *"satılan/ayıp"* |
| 42 | ürünüm elimden alınırsa | TBK 217 (zapt) | *Ürün Güvenliği K. 19* | aynı **"ürün"** tuzağı |
| 51 | birden fazla kişiye zarar | TCK 89 | *TCK 85* · *TCK 43* | en yakın komşu; sıralama meselesi, aday havuzu doğru |
| 61 | soruşturmaya yer olmadığına itiraz | CMK 158 | *CMK 172* | kardeş hüküm; ⚠️ yer-gerçeğinin kendisi de tartışmalı olabilir |

## Karar önerisi

**Erişim onarımının tavanı ölçüldü ve küçük: en çok 5 kalem = kütlede ~6,25 puanlık *tavan*.**
(e) sınıfındaki 5 kalem hiçbir retriever iyileştirmesiyle kazanılamaz — kusur soruda.

**En ucuz müdahale:** (d) sınıfının 3'ü (21 · 28 · 42) **aynı kalıba** düşüyor — genel sözlük
terimi ("ürün", "para birimi") aynı adı taşıyan **başka bir kanunun başlığıyla** eşleşiyor ve
BM25 kolunu ele geçiriyor. RRF ağırlığı ya da kanun-başlığı alanının ayrı ele alınması denenebilir.
**Beklenen kazanç: `recall@10` 0,875 → ~0,913 (73/80)** — üst sınır, ölçülmedi.

⚠️ **Ama:** indeks/erişim değişirse eşit sınavın kanıtı bozulur ve **üç rakip kolu yeniden
koşulmalıdır (~$1,35)**. Bu maliyet ~3 kalemlik bir kazanç için ödenecek mi — insan kararı.

⚠️ **İkinci ve daha büyük soru (bu tur açtı):** DEV setinin **5/80 kaleminde soru, altın maddeyi
belirlemiyor.** Sınav üç öznede de aynı olduğu için **eşit sınav bozulmuyor** — ama bu kalemler
hem bizim hem rakibin tavanını birlikte düşürüyor ve *"model bunu bilemedi"* diye okunuyorlar.
Bu bir **yer-gerçeği kalitesi** borcudur; DEV setine dokunmak ayrı bir karardır ve
`data/eval/canon/` (donmuş TEST) **aynı üretimden geliyorsa oraya da bulaşmış olabilir.**
