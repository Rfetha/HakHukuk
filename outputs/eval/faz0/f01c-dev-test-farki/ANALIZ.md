# DEV ↔ TEST erişim farkı — teşhis edildi ve %81'i açıklandı

**Tarih:** 2026-09-06 · **kaynak:** `data/eval/*/core_hard.jsonl(.v1-2026-09-06)` ·
indeks `data/index/mevzuat_bge_m3_s2` (değişmedi) · **LLM yok, $0**

## Soru

Donmuş TEST'in `recall@10`'u DEV'inkinden **~15 puan** düşük çıktı. Tesadüf mü (n=40), yoksa
yapısal mı? Bu, `v1` kabul testinin tavanını belirlediği için yayımdan önce cevaplanmalıydı.

## 1 · Fark gerçek — ama tek başına n=40 kesin konuşturmuyor

**Temiz kıyas** (her iki set de dokunulmamış v1 soruları, `RRF_K=60`):

| | oran | %95 Wilson |
| :--- | ---: | :--- |
| DEV | 70/80 = **0,8750** | [0,785 · 0,931] |
| TEST | 29/40 = **0,7250** | [0,572 · 0,839] |

fark **+15,0 p** · `z=2,04` · **`p=0,0415`** → α=0,05'te anlamlı, **ama Wilson aralıkları
örtüşüyor.** ⇒ Anlamlılık sınırda; hüküm tek başına bu testten kurulmaz.

## 2 · Setler soru bakımından değil, ALTIN MADDE bakımından farklı

| | DEV (80) | TEST (40) |
| :--- | ---: | ---: |
| soru uzunluğu (ort) | 52,6 | 53,4 — **fark yok** |
| kanun dağılımı | 10 kanun × 8 | 10 kanun × 4 — **birebir 2:1, kusursuz katmanlı** |
| **`_complexity` (medyan)** | **7** | **15** |
| **`_src_len` (medyan)** | **1.286** | **2.421** |

⇒ Ayrım **kanuna göre katmanlanmış, uzunluğa/karmaşıklığa göre katmanlanmamış.**

## 3 · Mekanizma: erişim, madde uzunluğunda U BİÇİMLİ

Havuzlanmış (n=120, `RRF_K=10`, v1 sorular), `_src_len` çeyrekleri:

| dilim | `_src_len` | `recall@10` |
| :--- | :--- | ---: |
| Q1 (en kısa) | 272–680 | 0,8000 |
| Q2 | 746–1.505 | **0,9333** |
| Q3 | 1.529–2.277 | **0,9333** |
| **Q4 (en uzun)** | 2.350–5.935 | **0,6667** |

Hem çok kısa hem çok uzun maddeler zor; en kötüsü uzun kuyruk.
⚠️ Doğrusal korelasyon bu yüzden **zayıf** görünüyor: `_src_len ↔ bulundu` `r=−0,166` (p≈0,068),
`_complexity ↔ bulundu` `r=−0,117` (p≈0,199). **İlişki doğrusal değil, U biçimli** — korelasyona
bakıp *"uzunluğun etkisi yok"* demek bu veride yanlış olurdu.

**Neden:** chunk = **tam madde** (ADR-0054/K2). Uzun madde çok konuyu birden kapsar; tek gömme
vektörü seyrelir ve BM25'in uzunluk normalizasyonu onu cezalandırır. Kısa madde ise eşleşecek
yeterli metin taşımaz. **Bu, ADR-0054/K2 kararının ilk kez ölçülen bedelidir.**

## 4 · ⭐ Kapatıcı: bileşim farkın %81'ini açıklıyor

Q4 payı: **DEV %12 ↔ TEST %50** — dört kat yoğunlaşma.

| set | bileşimden **beklenen** `recall@10` | **gözlenen** | artık |
| :--- | ---: | ---: | ---: |
| DEV | 0,8617 | 0,8875 | +0,0258 |
| TEST | 0,7767 | 0,7500 | −0,0267 |

TEST, DEV'in uzunluk bileşimine **standardize edilseydi ≈ 0,8617**.
Gözlenen fark **0,1375**; bileşimin açıkladığı **0,1118** ⇒ **%81**. Kalan ±2,6 puan artık.

⇒ **Hüküm: TEST "daha zor sorular" içerdiği için değil, en zor uzunluk diliminden 4 kat fazla
pay aldığı için düşük.** Fark yer-gerçeğinin ya da soruların kalitesinden değil, **ayrımın
katmanlanmamış olmasından** geliyor.

## 5 · Sonuçları

1. 🚨 **`v1` kabul testinin kütle tavanı ≈ %75'tir, DEV'in %95'i değil.** İki sayı **aynı metrik
   değildir** ve yan yana konurken tavan farkı damgalanmak zorundadır. Aksi hâlde
   *"%73 duyurduk, kabul testinde %58 çıktı"* tablosu **gerileme** gibi okunur — oysa model
   kötüleşmemiş olacaktır.
2. ✅ **Rakip kıyası etkilenmiyor:** kapı DEV'de kuruluyor ve üç özne de aynı harness'ı, aynı
   `recall`'u görüyor — eşit sınav bozulmuyor (ADR-0057).
3. 🆕 **Yeni borç: uzun madde chunk'lama.** Q4'te `recall@10 = 0,6667`. B9'dan (tablo/cetvel
   parçaları) **ayrıdır**: burada sorun bozuk chunk değil, **doğru ama çok uzun** chunk.
4. ⚠️ **Ayrımın kendisi katmanlanmamış.** Yeniden ayırmak donmuş TEST'i açmak demektir; bugün
   yapılmıyor. Yapılabilecek olan: kabul testi sonucunu **uzunluk-standardize** de raporlamak.

## Kaynaklar
`standardizasyon.txt` (bu klasör) · `docs/adr/0068-rrf-k-60-to-10.md` ·
`outputs/eval/f01b-soru-onarimi/SONUC_recall_v1_v2.md`
