# ADIM 6.4 — Tabakalanmış duman koşusu → para kapısı — KÜNYE

> **Bu koşu TABAKALANMIŞTIR** (tuzak 1.11'in korunması). Puanlar hiçbir hükme girmez —
> yalnız 6.5'in ($3.5$ Flash'ın Anthropic hakemle tam koşusu) maliyet kapısını türetmek içindir.

## 1. Girdi ve hakem

| alan | değer |
| :--- | :--- |
| puanlanacak kol | `outputs/eval/f04-rakip-onsozsuz/h1_3_5_flash_nb_detail.jsonl` (n=80) |
| hakem | `anthropic/claude-sonnet-5` (OpenRouter) — doğrulandı 2026-09-12, `/api/v1/models`: girdi $2,00/M · çıktı $10,00/M (`llm_client.PRICE` ile birebir) |
| sağlayıcı pin | `LLM_PROVIDER_ORDER=Anthropic` — 2026-09-10 `hp-hakem-paneli` duman koşusundan miras (`gnd_h1_tgta_v1_anthropic_duman_summary.json: judge_providers=["Anthropic"]`); körü körüne `OpenAI` YAZILMADI |
| bütçe kilidi | `OPENAI_BUDGET_USD` süreç düzeyinde her çağrıda kuruldu (kısa=$3, orta=$3, uzun=$3, doğrulama=$6) |
| plan ön-tahmini | $2,81 (ADR-0074, düz varsayım) |

## 2. Bakiye — koşudan ÖNCE okundu

`GET /api/v1/credits`: `total_credits=$30,00`, `total_usage=$18,12395798`
⇒ **kullanılabilir bakiye = $11,87604202** — 6.5'in tahmini faturasına ($2,81 ön-tahmin, aşağıda
$1,97 olarak yeniden türetildi) ve $8,00 tavanına **rahatça yeter**. DUR ① bakiye sebebiyle
**tetiklenmedi**.

## 3. Tabakalama ölçütü

`h1_3_5_flash_nb_detail.jsonl`'deki 80 kalem `completion_tokens`'a göre artan sırayla dizildi;
alt/orta/üst **tercile**'a bölündü (80/3 tam bölünmüyor ⇒ 26/26/28). Her dilimde, dilim içi
sırada **1/3 ve 2/3 konumundaki** kalemler seçildi (uç değerler değil, dilimi temsil eden ara
noktalar):

| dilim | n (popülasyon) | `completion_tokens` aralığı | ort. `completion_tokens` | seçilen id (token) |
| :--- | ---: | :--- | ---: | :--- |
| kısa | 26 | 60–420 | 237,3 | **id 4** (149) · **id 70** (289) |
| orta | 26 | 449–855 | 650,4 | **id 65** (598) · **id 68** (728) |
| uzun | 28 | 876–1532 | 1173,9 | **id 58** (1007) · **id 2** (1220) |

n=6 toplam. Girdi kopyaları: `duman_kisa.jsonl` · `duman_orta.jsonl` · `duman_uzun.jsonl`
(bu klasörde), tam 6'lık birleşik kopya: `h1_3_5_flash_nb_detail_duman6.jsonl`.

## 4. Gerçek fatura — dilim başına

Her dilim (2 kalem) **ayrı** `groundedness.py` çağrısıyla puanlandı ki dilim başına gerçek
maliyet ölçülebilsin (tek birleşik çağrı yalnız toplam verir):

| dilim | çıktı dosyası | n | gerçek maliyet | ort./kalem |
| :--- | :--- | ---: | ---: | ---: |
| kısa | `gnd_h1_3_5_flash_anthropic_duman_kisa_summary.json` | 2 | **$0,0477** | $0,02385 |
| orta | `gnd_h1_3_5_flash_anthropic_duman_orta_summary.json` | 2 | **$0,0613** | $0,03065 |
| uzun | `gnd_h1_3_5_flash_anthropic_duman_uzun_summary.json` | 2 | **$0,0395** | $0,01975 |
| **toplam (dilimli)** | | 6 | **$0,1485** | — |

**Çapraz-doğrulama (n=6 birleşik koşu):** `gnd_h1_3_5_flash_anthropic_duman6_summary.json` →
`judge_cost_usd=$0,1475` (dilimli toplamla $0,001 fark, ~%0,7). Bakiye farkıyla da doğrulandı:
koşu sonrası `total_usage=$18,41997598` ⇒ harcama `$18,41997598−$18,12395798=$0,29600000`,
tam olarak birleşik ($0,1475) + dilimli ($0,1485) = **$0,2960** — iki bağımsız ölçüm yöntemi
(`judge_cost_usd` toplamı ↔ bakiye farkı) **birebir örtüşüyor**.

⚠️ **Küçük determinizm notu (script'in kendi uyarısı, docstring satır 26-27):** `temperature=0`
"tam deterministik değil". id=65 birleşik koşuda 17 iddia/`faithfulness=0,5294`, dilimli koşuda
16 iddia/`faithfulness=0,5000` verdi — aynı kalem, aynı hakem, farklı grup bağlamı, küçük ama
gerçek bir fark. Diğer 5 kalemde iki koşu **birebir** örtüştü (id 4, 70, 68, 58, 2).

`judge_providers` **dört çağrının hepsinde tek eleman** (`["Anthropic"]`) — sağlayıcı yönlendirme
pinlenmiş durumda, tuzak 2.7 tetiklenmedi.

## 5. Tam koşu tahmini — dilim AĞIRLIKLARIYLA, düz çarpımla DEĞİL

```
tahmin = Σ (dilimin ort. maliyeti × dilimdeki GERÇEK kalem sayısı)
       = 0,02385 × 26  +  0,03065 × 26  +  0,01975 × 28
       = 0,6201        +  0,7969        +  0,5530
       = $1,9700
```

**Bu $1,97, ADR-0074'ün düz ön-tahmini $2,81'in ~%30 altında.** Şaşırtıcı ve kayda değer:
dilim ortalamaları `kısa $0,0239 < orta $0,0307`'ye kadar beklenen yönde artıyor ama **uzun
dilimde $0,0198'e düşüyor** — cevabın kendi `completion_tokens`'ı ile hakemin ÜRETTİĞİ token
sayısı (iddia çıkarımı + doğrulama JSON'u, asıl fatura kalemi) **düz orantılı değil**; uzun
cevaplarda (id 58, id 2) hakem az sayıda temiz/desteklenmiş iddia çıkarıp hızlı doğruladı, orta
dilimde (id 65) tek bir düşük-sadakatli, çok-iddialı (16-17 iddia) cevap ortalamayı yukarı çekti.
⇒ **Tuzak 1.11'in dersi ikinci kez doğrulandı, farklı bir yönden:** "cevap uzunluğu → hakem
maliyeti" varsayımı bile düz değil, tabakalama içindeki dilim SEÇİMİ (hangi 2 kalem) sonucu
etkiliyor — n=6 hâlâ küçük bir örneklem, tahmin bir **aralık** değil nokta değeri.

## 6. KAPI

```
tavan = min(tahmin × 1,5 ; $8,00) = min($2,9550 ; $8,00) = $2,9550
tahmin ($1,9700) ≤ tavan ($2,9550)  →  GEÇTİ
```

⚠️ **Formülün kendine referans doğası, açıkça yazılıyor:** `tavan` `tahmin`den türediği için
(`1,5×tahmin`, $8,00 tavanlı), `tahmin > tavan` yalnız `tahmin > $8,00` olduğunda mümkündür —
yani bu adımın fiili kapı testi *"tahmin $8,00'i aşıyor mu"* sorusudur. $1,97 bu eşiğin çok
altında (sağlıklı marj: $6,03). **DUR ① ateşlenmedi.**

Bu $1,97, plandaki (`docs/superpowers/plans/2026-09-12-v1-son-is.md` §2.3 tablosu) 6.5 kalemi
için **alt-tavan** olarak miras alınır — 6.5'in kendi koşusu bu sayıyı (ya da ondan türeyen bir
payı) aşarsa 6.5 kendi içinde durmalıdır; bu, 6.4'ün değil 6.5'in görevidir.

## 7. Künye özeti

- **tabakalanmış**: evet — `completion_tokens` tercile'ları (26/26/28), dilim başına 2 kalem (1/3, 2/3 konumu)
- seçilen id'ler: kısa `4, 70` · orta `65, 68` · uzun `58, 2`
- dilim başına gerçek maliyet: kısa $0,0477 · orta $0,0613 · uzun $0,0395 (n=2'şer)
- türetilen tahmin (tam koşu, 80 kalem): **$1,9700** (yöntem: §5, ağırlıklı toplam)
- tavan: **$2,9550** (`min(1,97×1,5; 8,00)`)
- hüküm: **KAPI GEÇTİ** — 6.5 çalıştırılabilir (ayrı bir insan onayı/adımla)
- bu adımın toplam gerçek harcaması: **$0,2960** (judge_cost_usd toplamı = bakiye farkı, birebir)
- 6.5'te aynı 6 kalem (id 4, 70, 65, 68, 58, 2) yeniden puanlanacak — bu koşunun
  `faithfulness` değerleri (id4=1,0 · id70=0,0 · id65=0,5294/0,5000 · id68=1,0 · id58=1,0 ·
  id2=1,0, birleşik/dilimli koşu farkı id65'te) **tekrarlanıp tekrarlanmadığının** sınanması
  için burada saklıdır — kapı hükmüne girmez.

## 8. Kapsam dışı bırakılan (bu adımda yapılMAYAN)

- Kalan 74 kalem puanlanmadı — 6.5'in işi, ayrı bir insan onayıyla.
- Donmuş TEST, bizim kolumuz, diğer üç rakip kolu, ağırlık deposu, `hakhukuk/` kodu — bu adımın
  şartnamesi gereği dokunulmadı.
