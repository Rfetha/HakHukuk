# ADIM 6.6d — Sonnet-5 M5 tabakalanmış duman koşusu → para kapısı — KÜNYE

> Bu koşu **TABAKALANMIŞTIR** (tuzak 1.11'in korunması). Puanlar hiçbir hükme girmez —
> yalnız tam koşunun ($80 kalem) maliyet kapısını türetmek içindir.

## 1. Tabakalama ölçütü

Sonnet-5'in M5-blind (kör) modda **hiç önceki koşusu yoktu**, dolayısıyla o modun kendi
completion-token dağılımı elde mevcut değildi. Proxy olarak Sonnet-5'in **kendi** RAG-modu
(h1, `outputs/eval/hp-rakip-havuzu/h1_sonnet_5_nb_detail.jsonl`) completion_tokens tercilleri
kullanıldı (26/26/28, 6.4'ün yöntemiyle aynı: her dilim içi 1/3 ve 2/3 konumu):

| dilim | seçilen id (h1'deki completion_tokens) |
| :--- | :--- |
| kısa | id 19 (314) · id 12 (410) |
| orta | id 22 (590) · id 33 (694) |
| uzun | id 42 (907) · id 24 (1226) |

⚠️ **Bu bir PROXY'dir, aynı özneden ama FARKLI moddan türetildi** — tuzak 1.11'in üçüncü
yüzünün (6.6b'de "başka öznenin faturasından tahmin") bir varyasyonu, burada "aynı öznenin
farklı moddan tahmini". Sonuç: **proxy doğrulanmadı** — M5-blind'ın gerçek completion_tokens'ı
(853, 831, 1046, 853, 812, 906) üç dilimde de **810-1050 aralığında sıkıştı**, h1'in
kısa/orta/uzun ayrımı M5-blind modunda **yansımadı**. Bu kayda değer bir bulgudur: RAG-modu
uzunluğu, blind-mod uzunluğunu **öngörmüyor**.

## 2. Üretim (n=6) — gerçek maliyet

`gen_eval_grounded.py --server-model anthropic/claude-sonnet-5 --thinking on
--reasoning-budget 1024 --max-new-tokens 512 --data duman6.jsonl --n 6 --seed 3407`

Bakiye (`GET /api/v1/credits`) üretimden ÖNCE: `total_usage=22,86879198`.
Üretimden SONRA: `total_usage=22,89744798` ⇒ **görünen** üretim maliyeti $0,028656.

## 3. Puanlama (n=6) — gerçek maliyet

`groundedness.py --mode data`, hakem `openai/gpt-4o-mini`, `LLM_GATEWAY=openrouter`,
`LLM_PROVIDER_ORDER=OpenAI`, `OPENAI_BUDGET_USD=1.00`.
İç muhasebe: `judge_cost_usd=$0,0043`. Puanlamadan SONRA bakiye: `total_usage=22,92627763` ⇒
**görünen** puanlama maliyeti $0,028830.

## 4. 🚨 Bulgu — iki checkpoint'in atıfı LEDGER GECİKMESİYLE bozulmuş

Görünen üretim ($0,028656) ve görünen puanlama ($0,028830) **neredeyse eşit** çıktı — ama bu
YANLIŞ bir atıf. `anthropic/claude-sonnet-5`'in OpenRouter liste fiyatı ($10,00/M çıktı,
`llm_client.PRICE`) ile n=6'nın toplam `completion_tokens`'ı (5301) çarpılırsa üretim tek
başına **~$0,0530-0,0548** tutmalı (girdi payı dahil) — ölçülenin **yaklaşık iki katı**.
Buna karşılık `gpt-4o-mini`'nin iç muhasebesi ($0,0043) gerçekçi. ⇒ **En olası açıklama:**
OpenRouter'ın `/api/v1/credits` uç noktası üretim maliyetini **gecikmeli** yazıyor; "üretim
sonrası" okuması gerçek maliyetin yalnız bir kısmını yakalamış, kalanı "puanlama sonrası"
okumasına SIZMIŞ. **İKİ AYRI checkpoint'in FARKINI bileşene atfetmek burada YANLIŞ** —
yalnız TOPLAM (başlangıç→son) güvenilir:

```
toplam (n=6, gen+hakem) = 22,92627763 − 22,86879198 = $0,05748565
```

Bu, $10/M çıktı fiyatıyla hesaplanan üretim tahmini (~$0,053) + hakemin iç muhasebesi
($0,0043) ≈ $0,057-0,059 ile **uyumlu**. ⇒ **Tam koşu ekstrapolasyonu TOPLAM üzerinden
yapıldı**, gen/hakem bileşenlerine ayrıştırılarak DEĞİL. *(Yeni bir tuzak adayı — bu turun
kaydına düşülür, numaralandırma 6.8'in işi.)*

## 5. Tam koşu tahmini

```
kişi başı ort. gerçek maliyet (n=6) = 0,05748565 / 6 = $0,00958094
n=80 tahmini (düz ortalama; tabakalama M5-blind'da ayrışma göstermediği için
              ağırlıklandırmanın faydası yok, §1'deki bulgu)
   = 80 × 0,00958094 = $0,76648
×1,5 emniyet payı (tuzak 1.11'in kendi önerdiği pay) = $1,1497
```

## 6. KAPI

```
alt-tavan (bu kalem) = $3,00
tahmin (emniyet paylı) = $1,1497 ≤ $3,00  →  GEÇTİ
```

**DUR ① ateşlenmedi.** Tam koşu (n=80) çalıştırıldı — sonuç ve gerçek fatura
`outputs/eval/f10-rakip-m5/KUNYE.json` (`sonnet_5` girdisi) içinde.

## 7. Kapsam dışı

Bu klasördeki 6 kalemin puanları (`gnd_smoke_sonnet5_m5_summary.json`, `faithfulness_macro
0,8903`) **hiçbir hükme girmez** — n=6, yalnızca maliyet ölçümü için koşuldu. Bağlayıcı sayı
(n=80) `f10-rakip-m5/gnd_m5_anthropic_claude-sonnet-5_m5_summary.json`'dadır.
