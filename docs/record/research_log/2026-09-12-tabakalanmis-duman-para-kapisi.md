# 2026-09-12 — ADIM 6.4 kapandı: tabakalanmış duman koşusu, para kapısı GEÇTİ

> ADIM 6.4 (plan `docs/superpowers/plans/2026-09-12-v1-son-is.md`), **6.5'in ön koşulu**.
> Kapatılan risk: tuzak **1.11** (n=5 doğrusal ekstrapolasyonla kapının %45 aşılması,
> 2026-09-09). Tam döküm: [`outputs/eval/hp-rakip-anthropic-duman/KUNYE.md`](../../../outputs/eval/hp-rakip-anthropic-duman/KUNYE.md).

## Ne yapıldı

`3.5 Flash` kolunun (`outputs/eval/f04-rakip-onsozsuz/h1_3_5_flash_nb_detail.jsonl`, n=80)
tam koşusu 6.5'te `anthropic/claude-sonnet-5` hakemle puanlanacak — ADR-0074'ün açık borcunu
kapatan adım (`KAPPA.md`'deki eşiti-olmayan-sınav `0,6940`'ı düzeltecek karşılaştırma). Önce
maliyeti ölçmek için **tabakalanmış** bir duman koşusu koşuldu: 80 kalem `completion_tokens`'a
göre tercile'landı (26/26/28), her dilimden dilim-içi 1/3 ve 2/3 konumundaki kalemler seçildi
(n=6: id 4·70 kısa, id 65·68 orta, id 58·2 uzun). Sağlayıcı `LLM_PROVIDER_ORDER=Anthropic`
pinlendi (2026-09-10 `hp-hakem-paneli` duman koşusundan miras alınan pin — körü körüne
`OpenAI` yazılmadı, `judge_providers` ile doğrulandı). Bakiye koşudan önce okundu ($11,876,
30−18,124).

## Bulgu — tahmin plan ön-tahmininden ~%30 düşük çıktı

Dilim başına gerçek maliyet (ayrı `groundedness.py` çağrılarıyla ölçüldü, n=2'şer):

| dilim | ort. `completion_tokens` | gerçek maliyet (n=2) | ort./kalem |
| :--- | ---: | ---: | ---: |
| kısa | 237,3 | $0,0477 | $0,02385 |
| orta | 650,4 | $0,0613 | $0,03065 |
| uzun | 1173,9 | $0,0395 | $0,01975 |

Ağırlıklı tahmin: `0,02385×26 + 0,03065×26 + 0,01975×28 = **$1,9700**` — ADR-0074'ün düz
ön-tahmini ($2,81)'in **~%30 altında**. Şaşırtıcı yön: **uzun** dilim en **düşük** ortalama
maliyeti verdi — cevabın kendi `completion_tokens`'ı ile hakemin ürettiği token sayısı (asıl
fatura kalemi: iddia çıkarımı + doğrulama JSON'u) düz orantılı değil. Tuzak 1.11'in dersi
(*"cevap uzunluğu ile hakem maliyeti temsili örneklem gerektirir"*) burada ikinci kez, farklı
yönden doğrulandı: tabakalama bile tam düz bir ilişki vermiyor, n=6 bir aralık değil nokta
tahmini üretiyor.

**Çapraz doğrulama:** 6'lık birleşik koşu (`judge_cost_usd=$0,1475`) ile 3 dilimli koşunun
toplamı (`$0,1485`) örtüştü; bakiye farkı (`$0,29600000`) ikisinin toplamıyla (`$0,2960`)
**birebir** eşleşti — iki bağımsız ölçüm yöntemi aynı sayıyı verdi. Küçük bir determinizm notu:
id 65, birleşik koşuda 17 iddia/`faithfulness=0,5294`, dilimli koşuda 16 iddia/`0,5000` verdi
(`temperature=0` "tam deterministik değil", script'in kendi uyarısı) — diğer 5 kalem birebir
örtüştü.

## Kapı

`tavan = min($1,97×1,5; $8,00) = $2,955` ⇒ `tahmin ≤ tavan` → **GEÇTİ**, DUR ① ateşlenmedi.
(Formülün kendine-referans doğası not edildi: `tavan` `tahmin`den türediği için bu kapı fiilen
*"tahmin $8,00'i aşıyor mu"* sorusuna indirgeniyor — $1,97 bunun çok altında.) $1,97, 6.5'in
kendi alt-tavanı olarak plana (§2.3 tablosu) miras bırakılıyor.

**Yan not:** plan dosyasının 6.4.4 maddesi hâlâ eski `$6,00` tavanını taşıyordu; §2.3'ün ve
DUR-tablosunun güncel `$8,00`'ı (2026-09-12 insan kararı, kapsam büyümesi) bağlayıcı alındı ve
plan metnindeki tutarsızlık düzeltildi.

## Harcama

Bu adımın toplamı: **$0,2960** (duman ölçümü, hiçbir hükme girmiyor). 6.5'in kendi harcaması
ayrı ölçülecek.
