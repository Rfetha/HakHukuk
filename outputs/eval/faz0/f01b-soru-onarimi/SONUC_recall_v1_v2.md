# Soru onarımının erişime etkisi — v1 ↔ v2, aynı indekste

**Tarih:** 2026-09-06 · **indeks:** `data/index/mevzuat_bge_m3_s2` (değişmedi) ·
**retriever:** hibrit BM25 + `BAAI/bge-m3` + RRF · CPU · **LLM yok, $0**
**yöntem:** `Retriever.yukle().getir(soru, k=10)`; altın eşleşme `(kanun_no, madde_no)` normalize

## ⭐ Kontrol grubu çıpayı yeniden üretti

v1 soru setiyle **`recall@10` = 0,8750** — `g2-fl-harness/KUNYE.json` ve
`s2-harness-k10-etiketli` ile **birebir**. Ölçüm yolunun tamamı doğrulanmış oldu.

| eksen | v1 (eski sorular) | **v2 (onarılmış)** | fark |
| :--- | ---: | ---: | ---: |
| `recall@1` | 0,4500 | **0,5250** | +7,5 p |
| `recall@3` | 0,6500 | **0,7250** | +7,5 p |
| `recall@5` | 0,7500 | **0,8000** | +5,0 p |
| **`recall@10`** | **0,8750** | **0,9375** | **+6,25 p** |
| kaçırılan | 10/80 | **5/80** | −5 |

**Kütle tavanı `%87,5` → `%93,75`.**

## Kalem düzeyinde

**Kaçarken bulundu (6):** 24 (sıra 7) · 47 (0) · 49 (6) · 58 (2) · 71 (6) · 78 (0)
**Sırası yükseldi (4):** 41 (1→0) · 43 (5→0) · 57 (4→0) · 75 (7→0)
**🚨 Bulunuyorken kaçtı (1): id 79**

### id 79 — kayıp kayda geçti, soru DÜZELTİLMEDİ

Eski: *"Kolluk güçleri **bu** eğitimleri ne için alıyor?"* — öncülsüz "bu" yüzünden
**belirlenemez**di, ama içindeki **"eğitim"** sözcüğü 6284/11'in metniyle birebir eşleşiyordu.
Yeni: *"…kolluk personelinde hangi **nitelik** aranır?"* — belirlenebilir, ama sözcüksel çıpa yok.

⛔ **Geri alınmadı.** Soruyu retriever'ın bulabileceği hâle getirmek, **eval sorusunu ölçülen
sistemin lehine ayarlamaktır** — künyedeki 2. korumanın (*"maddenin ayırt edici ifadeleri
kopyalanmaz"*) doğrudan ihlali. Kayıp gerçek bir erişim hatasıdır ve öyle raporlanır.

## Kalan 5 kaçak — hepsi (d) sınıfı gerçek erişim hatası

| id | altın | teşhis |
| :-- | :--- | :--- |
| 1 | TCK 89 | onarılmış soruyla da kaçıyor — komşu maddeler (TCK 85/86) baskın |
| 12 | CMK 158 | kardeş hüküm CMK 172 öne geçiyor |
| **68** | TBK 99 | *"para birimi"* → **Para Birimi Hakkında Kanun** başlığı BM25'i ele geçiriyor |
| **72** | TBK 230 | *"ürün"* → **Ürün Güvenliği Kanunu** başlığı BM25'i ele geçiriyor |
| 79 | 6284/11 | yukarıda |

⭐ **68 ve 72 aynı kalıpta:** genel bir terim, aynı adı taşıyan **başka bir kanunun başlığıyla**
eşleşiyor. Erişim onarımının (RRF ağırlığı / kanun-başlığı alanının ayrı ele alınması) kalan
hedefi bu ikisidir. **Tavan artık 2 kalem = `recall@10` 0,9375 → 0,9625.**
