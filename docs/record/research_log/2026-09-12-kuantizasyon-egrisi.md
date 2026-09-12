# 2026-09-12 — S17 kapandı: kuantizasyon eğrisi ölçüldü, monoton çıkmadı

> ADIM 6.3c. Kapatılan açık karar: **S17** (`MODEL_CARD.md`, ADR-0031 hassasiyeti seçti-ama-
> ölçmedi boşluğu). Tam döküm: [`outputs/eval/s17-kuantizasyon-egrisi/OZET.md`](../../../outputs/eval/s17-kuantizasyon-egrisi/OZET.md).

## Ne yapıldı

`models/merged/tgta_v1` (bf16, 8,8 GB) → f16 GGUF (`convert_hf_to_gguf.py`) → `llama-quantize`
ile `Q5_K_M` ve `Q8_0`. Ayrıca yayımlanan `Q4_K_M`'nin **bugünkü** araç zinciriyle bit-bazında
yeniden üretilip üretilemediği sınandı (dördüncü kol). Dört kol da `scripts/yeniden_uret.sh`
ile aynı rejimde (h1, k=10, seed 3407, think_budget 1024 + maxtok 512, KV q8_0/q8_0, ctx 8192)
üretildi, geçerlilik kapılarından geçirildi, `gpt-4o-mini` ile (`LLM_PROVIDER_ORDER=OpenAI`
pinli) puanlandı.

## Eğri

| kol | dosya boyutu | kütle | coverage | A1 | kesiklik | recall@10 |
| :--- | ---: | ---: | ---: | ---: | :--- | :--- |
| `Q4_K_M` @2026-08-03 (yayımlanan çıpa) | 2.783.446.720 | 0,8011 | 0,9375 | 0,8545 | %5,0 | 0,9500 |
| `Q4_K_M` @2026-09-12 | 2.783.446.688 | 0,7921 | 0,9375 | 0,8449 | %5,0 | 0,9500 |
| `Q5_K_M` @2026-09-12 | 3.161.425.568 | 0,8673 | 0,9750 | 0,8895 | %2,5 | 0,9500 |
| `Q8_0` @2026-09-12 | 4.610.580.128 | 0,7909 | 0,9250 | 0,8550 | %1,2 | 0,9500 |

n=80 ⇒ çözünürlük adımı 1,25 p. `Q4`@ağustos↔`Q4`@bugün fark −0,90 p (0,7 adım, **belirsiz**);
`Q4`↔`Q8` −0,12 p (0,1 adım, **belirsiz**); `Q4`↔`Q5` +7,52 p (6,0 adım, ölçülebilir); `Q5`↔`Q8`
−7,64 p (6,1 adım, ölçülebilir). **Eğri monoton değil**: `Q4 ≈ Q8`, `Q5` ikisinin de belirgin
üstünde. Mekanizma coverage ekseninde (cevaplanan kalem 75/80 → 78/80 → 74/80), A1 dar bantta
(0,845-0,890) sıkışık — kuantizasyon burada doğruluğu değil çekinme eşiğini oynatıyor gibi
görünüyor, ama **bu bir gözlem, açıklama değil**; mekanizma hipotezi ölçülmedi, hüküm
kurulmadı (n=80, tek koşu, üç kalemlik fark).

## BULGU-G — araç zinciri sapması var ama davranışsal fark ölçülemez düzeyde

Yayımlanan `tgta_v1-q4_k_m.gguf` (2026-08-03, o günkü `llama.cpp`) ile bugünkü araç zinciriyle
aynı f16'dan üretilen kopya **bayt-bayt aynı değil** (−32 bayt, farklı `sha256`). Bu, deponun
"yayımlanan artefakt yeniden üretilebilir" iddiasına karşı ölçülmüş bir sınav ve **sonucu
kısmi**: dosya farklı ama davranış (kütle −0,90 p) çözünürlük altında, üretim tarafı ise
neredeyse örtüşüyor (ort. completion token 782,5 ↔ 782,4, zorla-kapatma 3/80 ↔ 3/80). İki
bulgu birlikte yazılıyor, biri diğerini geçersiz kılmıyor.

## Kusur 33 bu turda canlı yakalandı

`yeniden_uret.sh`'ın (eski hâli) recall@10 kapısı var olmayan alanları okuyup **her koşuda**
0,0000 basıyordu — `Q5_K_M` kolunun ilk denemesi bu yüzden geçerli bir üretimi (n=80, kesiklik
%2,5) GEÇERSİZ sayıp attı. Eş zamanlı kapatıldı (`cc12b6e`, `scripts/olcum_uretim/
recall_kapisi.py`, `harness.altin_sirasi`/`altin_dusuruldu`'dan okuyor, 6/6 test yeşil).
Kalibrasyon: hem çıpanın kendi verisinde (gerçek 76/80) hem bu turun üç kolunda düzeltilmiş
kapı doğru sonuç verdi. Bkz. `docs/record/yurutme-tuzaklari.md` §7.7.

## BULGU-E — yeni tuzak: sağlık kontrolü başka bir sürecin sunucusuna 200 alıyor

Port 8080, işi bitmiş ama 2 saattir kapatılmamış bir konteyner çiftini (`hakhukuk-app-1`/
`hakhukuk-llama-1`, yayımlanan ürün) tutuyordu. Yeni `llama-server` bu portu bağlayamadan
öldü, ama `curl .../health` döngüsü eski sunucudan `200 OK` aldığı için betik "hazır" deyip
devam etti — 8 kalem **yanlış model** karşısında sessizce üretildi. Yakalanma: `ps -p <pid>`
ile başlatılan sürecin gerçekten yaşayıp yaşamadığı ve `/v1/models`'ın beklenen GGUF'u
göstermediği kontrol edildi. Kirli çıktı silindi, temiz port (8090) ile yeniden koşuldu;
sonraki her sunucu başlatmasında `/v1/models` doğrulaması zorunlu hale getirildi. Konteyner
çifti durduruldu. Bkz. `docs/record/yurutme-tuzaklari.md` §7.8.

## Maliyet

Üç puanlama (`Q4`@bugün, `Q5`, `Q8`) × `gpt-4o-mini`, `LLM_PROVIDER_ORDER=OpenAI` pinli:
$0,0414 + $0,0402 + $0,0394 = **$0,1210** gerçekleşen, tahmin ~$0,12, alt-tavan $0,20 — kapı
geçti. `Q4_K_M`@ağustos yeniden puanlanmadı (çıpanın kendi sayısı alındı). GPU üretimi yerel,
$0.

## Karar — ALINMADI

ADR-0071 (v1 sürüm artefaktı tek GGUF) yürürlükte. `Q5_K_M`'nin daha yüksek kütle vermesi
artefakt değişikliğini **tetiklemiyor** — bu turun ön-kaydı böyleydi ve korundu. Eğri bir
ifşadır: *"bu hassasiyeti seçtik, bedeli/kazancı şu kadarmış."* Erişilebilirlik ekseni
(ADR-0018), sabitlenmiş `sha256`/`indir.py` bağımlılığı ve v1.0 kapısının `Q4_K_M` çıpasıyla
ön-kayıtlı olması ayrı gerekçelerdir; hiçbiri bu turda yeniden açılmadı.
