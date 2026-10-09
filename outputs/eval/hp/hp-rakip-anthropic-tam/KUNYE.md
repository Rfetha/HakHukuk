# ADIM 6.5 — `3.5 Flash` kolu Anthropic hakemle (tam koşu) — KÜNYE

> κ borcunun kapanma koşulu (ADR-0074): *"`3.5 Flash` kolunun aynı ikinci hakemle
> puanlanması."* Bu koşu o koşulu üretir. **Hüküm kurmaz** (6.7'nin işi).

## 1. Girdi ve hakem

| alan | değer |
| :--- | :--- |
| puanlanan kol | `outputs/eval/f04-rakip-onsozsuz/h1_3_5_flash_nb_detail.jsonl` (n=80) — **üretim yeniden koşulmadı** (ADR-0017) |
| girdi `sha256` | `86bd40c993bba2b54b65c4b476417271858d118682a7d7c2cf7decbaa91242fb` — 6.4'ün künyesindeki dosyayla birebir aynı |
| hakem | `anthropic/claude-sonnet-5` (OpenRouter) |
| sağlayıcı pin | `LLM_PROVIDER_ORDER=Anthropic` — koşu sonrası `judge_providers=["Anthropic"]` (tek eleman, tuzak 2.7 tetiklenmedi) |
| mod | `--mode data` (tek-madde yer-gerçeği, f04'ün orijinal `gpt-4o-mini` koşusuyla birebir aynı rejim) |
| runs | 1 (f04'ün orijinal koşusuyla aynı) |
| bütçe kilidi | `OPENAI_BUDGET_USD=2.955` (süreç düzeyinde — 6.4'ün türettiği alt-tavan, aşılırsa betik kendiliğinden durur) |
| hakem çağrısı | **BİR KEZ** — tek `groundedness.py` çağrısı, 80 kalemin tamamı |
| tarih | 2026-09-12, 20:45–21:02 (+03), ~17 dk |
| çıktı | `gnd_h1_3_5_flash_anthropic.jsonl` (`sha256 500d55e0d6f3f64cffbc394c687a3221db8f7cd386b99f8bb3d5d3f4da757802`) + `_summary.json` |

## 2. Bakiye — koşudan ÖNCE ve SONRA okundu

```
öncesi   GET /api/v1/credits → total_usage = 18,41997598  (6.4'ün bitişiyle birebir aynı)
sonrası  GET /api/v1/credits → total_usage = 20,10307598
gerçek fatura (bakiye farkı)     = $1,6831
```

⚠️ **İkinci bir sayı, ve İKİSİ AYNI ŞEY DEĞİL (`llm_client.py`'nin kendi uyarısı):**
betiğin iç muhasebesi (`judge_cost_usd`, token sayısı × BİRİNCİL-KAYNAK liste fiyatı) = **$1,7525**.
Fark: **$0,0694 (~%4,1)** — betiğin iç muhasebesi gerçek faturadan yüksek. 6.4'ün duman
koşusunda bu iki yöntem ~%0,7 farkla örtüşmüştü; o örtüşme **rastlantıydı**, garanti bir
değişmez değil — `llm_client.py` bu ikisini kavramsal olarak ayrı sayılar olarak tanımlıyor
("kapıya ödenen tutar ayrı, operasyonel bir sayıdır; ödenen tutarı parite fiyatı sanmak..." ).
**Gerçek fatura = $1,6831** (bakiye farkı, ödenen tutar).

## 3. 6.4'ün tahminiyle karşılaştırma

```
6.4 tahmini (tabakalı)   $1,9700
gerçek fatura            $1,6831   → tahminin %14,56 ALTINDA
iç muhasebe (judge_cost) $1,7525   → tahminin %11,04 ALTINDA
tavan (6.4)              $2,9550   → gerçek fatura tavanın %57,0'inde, $1,2719 marj boşta
```

Sapmanın niçin'i (tuzak 1.11'in ikinci katmanının devamı): 6.4'ün n=6 tabakalı örneklemi
zaten "cevap uzunluğu ↔ hakem maliyeti düz orantılı değil" bulgusunu taşıyordu (uzun dilim
en düşük ort. maliyeti vermişti). Tam koşuda (n=80) bu değişkenlik ortalamaya daha çok
örnek katkısıyla süzülüyor ve gerçekleşen ortalama/kalem (**$1,6831/80 = $0,02104**),
duman'ın üç dilim ortalamasının ($0,0239 · $0,0307 · $0,0198) ağırlıklı ortalamasından biraz
düşük çıktı — n=6'nın küçük örneklem gürültüsü beklenen yönde.

## 4. Üç okuma — `scripts/puanlama/uc_okuma_kutle.py`

Küme üyeliği MİRAS ALINDI (id 28 + 15,24,27), puanlar Anthropic hakemden **yeniden** alındı:

| id | gpt-4o-mini `faithfulness` | Anthropic `faithfulness` |
| :-- | ---: | ---: |
| 28 | 1,0 | **1,0** |
| 15 | 1,0 | **0,0** |
| 24 | 1,0 | **0,5** |
| 27 | 1,0 | **0,0** |
| 79 *(beşinci kalem tuzağı — kümeye eklenMEDİ)* | 0,5 | 0,0 |

⛔ Dört kalemin puanı **1,0 varsayılmadı** — doğrulandı, ve üçü Anthropic altında **düştü**.
`id 79` kontrol amaçlı yeniden okundu: Anthropic altında da düşük (0,0), göz listesine dahil
edilMEDİ (doğru davranış korundu).

| okuma | n_cevaplanan | Σ faithfulness | kütle |
| :--- | ---: | ---: | ---: |
| ALET | 67 | 47,9645 | **0,5996** |
| GÖZ-orta (+id 28) | 68 | 48,9645 | **0,6121** |
| GÖZ-katı (+id 15·24·27) | 71 | 49,4645 | **0,6183** |

Kaynak: `outputs/eval/hp-rakip-anthropic-tam/uc_okuma_anthropic.json`.

## 5. Eşik ve marj

```
eşik = GÖZ-katı(Anthropic) − 0,020 = 0,6183 − 0,0200 = 0,5983
bizim kütlemiz (Anthropic, KAPPA.md:65, YENİDEN PUANLANMADI) = 0,6940
marj = 0,6940 − 0,5983 = +0,0957  (+9,57 puan)
```

⛔ **HÜKÜM KURULMADI.** Çözünürlük birimi `n=80` için 1,25 puandır; marjın büyüklüğü ile
karşılaştırma **6.7'nin işidir**.

## 6. Kalibrasyon kapısı

`scripts/puanlama/uc_okuma_kutle.py`, `gpt-4o-mini` verisiyle (`outputs/eval/f04-rakip-onsozsuz/gnd_h1_3_5_flash_nb.jsonl`)
koşulduğunda `0,6925 · 0,7050 · 0,7425`'i **birebir** üretir — `tests/test_uc_okuma_kutle.py`
(3 test, sıfır API çağrısı). Bu türetme 2026-09-12'ye kadar hiçbir betikte yoktu (BULGU-A).

## 7. Kusur 23'ün sınaması — 6.4'ün 6 kalemi tekrarlandı mı

`id 4·70·65·68·58·2` — 6.4'ün tabakalı duman koşusunda zaten puanlanmıştı. Tam koşuda
**altısı da `faithfulness` VE `n_claims` düzeyinde bayt-bayt aynı** çıktı:

| id | duman | tam koşu | aynı mı |
| :-- | ---: | ---: | :---: |
| 4 | 1,0 (5 iddia) | 1,0 (5 iddia) | ✅ |
| 70 | 0,0 (13 iddia) | 0,0 (13 iddia) | ✅ |
| 65 | 0,5294 (17 iddia, birleşik koşu) | 0,5294 (17 iddia) | ✅ |
| 68 | 1,0 (5 iddia) | 1,0 (5 iddia) | ✅ |
| 58 | 1,0 (7 iddia) | 1,0 (7 iddia) | ✅ |
| 2 | 1,0 (13 iddia) | 1,0 (13 iddia) | ✅ |

Kusur 23'ün sınıfı ("aynı girdi, aynı alet, farklı sayı") **bu koşuda tekrarlanmadı**.

## 8. Kapsam dışı bırakılan

Diğer üç rakip kolu (tek hakemli kalır), donmuş TEST, bizim kolumuz (yeniden puanlanmadı —
`0,8011` ve `0,6940` sabit kaldı), ağırlık deposu, `hakhukuk/` kodu, `retriever.py`, `indir.py`.
