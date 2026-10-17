# Araştırma kaydı — #75 …

> **Ne bu:** Checkpoint 1'in F0 aşaması (2026-10-11'den). Önceki dosya
> [`kronoloji-63-71.md`](kronoloji-63-71.md) 12 girdiye ulaştı (#63-#74); kural
> [`README.md`](README.md)'de. Çapa: `kronoloji-75-86.md#75`. **Dosya doldu (#75-#86); devamı [`kronoloji-87-98.md`](kronoloji-87-98.md).**

| # | tarih | başlık | kanca |
| :-- | :--- | :--- | :--- |
| [75](#75) | 2026-10-11 | F0.4: yeni eğitim kilidi eski ortamla eşdeğer | en büyük sapma 0,0032 · gürültü ≤ 0,0021 · 15 dk boşta A100 sızıntısı kapandı |
| [76](#76) | 2026-10-11 | F0.5 (b) ve F0.6'nın kodu: RQ2 anahtarları | hakemsiz çıpaların hepsi birebir · `gpt-4o-mini` aynı istekte bir ayda −1,75 p kütle |
| [77](#77) | 2026-10-11 | F0.7: ham TIES'te τ_a'nın %32'si taşınıyor | τ_a'yı ezen seyreklik değil, normların 9 kat farkı |
| [78](#78) | 2026-10-14 | F0.9 ön kontrol: maske doğru, Gemma kilitle yüklenmiyor | iki modelde ihlal yok · `unsloth_zoo` 2026.6.1'in Gemma 4 yaması ayarı bozuyor, yükleyici yanlış teşhis veriyor |
| [79](#79) | 2026-10-14 | Gemma'nın kilidi, deposu ve LoRA hedefleri | `unsloth` 2026.10.1 yüklüyor · Unsloth `google/` → `unsloth/` sessiz değişim (ağırlık aynı, bitiş işareti farklı) · düz liste görüntü/ses kulesine 148 modül taşıyor |

---

<a id="75"></a>
## #75 — F0.4: yeni eğitim kilidi eski ortamla eşdeğer; boşta GPU sızıntısı kapandı

**2026-10-11 · Modal, ilk hesap · GPU'suz ön uçuş + 4 × A100-40GB** · tahmin ~$2 (eğitim 9-12 dk/koşu,
konteyner ~15 dk/koşu); gerçek tutar Modal panelinden okunur (tuzak 6.3) · Kanıt:
`outputs/egitim/f04-esdegerlik/` · Kilit: [#74](kronoloji-63-71.md#74), [ADR-0099](../adr/kararlar-0064-0085.md#adr-0099)

**Ön uçuş (GPU'suz, `on_ucus.json`).** `modal_train.py`'nin yeni imajı kuruldu (`im-7797E4ChjR4yWddVxxnJfW`);
konteynerde kilit dosyası `/root/configs/egitim_ortami.yaml`'dan okundu; 13/13 paket kilitteki sürümde;
`from fla.modules import FusedRMSNormGated` ve `hakhukuk.cekirdek.istem` içe aktarıldı; Modal birimindeki dört
veri dosyasının satır sayısı (17.323 / 962 · 845 / 26) ve `sha256`'sı yereldekiyle birebir.

**Koşular.** Hepsi seed 3407, `--hassasiyet bf16-taban`, `spawn()` + `--detach`, kilit kontrolü dört koşuda
da geçti (`KUNYE.json`). τ_g: #40'ın komutu, `--max-steps 50` (takvim 50 adım, #40 ile aynı). ORPO:
`ta_v1`'in tarifi, 70 adımlık takvim, `--durdur-adim 10`. Gürültü tabanı aynı koşulardan: her biri iki kez.

| | adım | koşu a | koşu b | referans | en büyük sapma | gürültü (a−b) | tolerans | hüküm |
| :-- | --: | --: | --: | --: | --: | --: | --: | :-- |
| τ_g | 10 | 0,7992 | 0,7990 | 0,7987 ([#40](kronoloji-39-52.md#40)) | 0,0005 | 0,0002 | ±0,02 | geçti |
| τ_g | 50 | 0,3545 | 0,3524 | 0,3537 (#40) | 0,0013 | 0,0020 | ±0,02 | geçti |
| ORPO | 5 | 2,6399 | 2,6395 | 2,6397 (`ta_v1`) | 0,0002 | 0,0004 | ±0,066 | geçti |
| ORPO | 10 | 2,4895 | 2,4874 | 2,4863 (`ta_v1`) | 0,0032 | 0,0021 | ±0,062 | geçti |

ORPO toleransı (%2,5 göreli) koşudan önce plana yazıldı (kullanıcı kararı). Dört koşu dört ayrı veri
merkezine düştü (OCI us-east · AWS us-west · AWS eu-north · OCI us-west) ve iki sürücü sürümü kullandı
(580.95.05 · 610.57.04; CUDA 12.8); sapma yine 0,003 içinde. Yeni τ_g koşusunun `adapter_config.json`'u
`tg_v1`'inkiyle aynı. ⇒ τ_g v1'in hassasiyeti için ölçüm kanıtı geldi (`kollar.md` ⁽²⁾).

**Kullanıcı kararı:** eşdeğerlik geçtiği için Qwen'in 3407 kolları (`tg_v1`, `ta_v1`) yeniden eğitilmedi.

**Bulgu — boşta GPU faturası (tuzak 6.13).** `modal_train._run_with_commits` alt süreci
`while proc.poll() is None: time.sleep(900)` ile izliyordu; eğitim bitince ana süreç uykusunun kalanını da
uyudu, konteynerler 15. dakikaya kadar açık kaldı (eğitim 9-12 dk). Bu turda ~15 dk boşta A100 (~$0,5).
Düzeltildi: `proc.wait(timeout=…)` alt süreç bitince hemen döner; testi `tests/test_egitim_ortami.py`.

**Ders.** *Kısa koşunun masrafını izleme döngüsünün uyku aralığı belirleyebilir.* Fatura kalemlerinden biri
hesapta değil, beklemedeydi.

---

<a id="76"></a>
## #76 — F0.5 (b) ve F0.6'nın kodu: RQ2 anahtarları birebir; `gpt-4o-mini` aynı istekte kaydı

**2026-10-11 · hakem $0,0826 (iki yeniden puanlama; ağ geçidi payı hariç) · GPU $0** · Kanıt:
`outputs/eval/f0/rq2-dogrulama/` (`KUNYE.json`) · Karar: [ADR-0099](../adr/kararlar-0064-0085.md#adr-0099) m.1

**Ne yazıldı.** `scripts/puanlama/olcum_aleti.py`'de yedi anahtar, her biri adlı iki değerle:
`dedektor` · `sifir_iddia` · `a1_tanimi` · `kaynak_kirpma` · `payda` · `altin_kirpma` (+ üç okuma, mevcut
`uc_okuma_kutle.py`). Eski dedektör bundle'dan kod satırları birebir alınarak
`scripts/puanlama/eski_aletler.py`'ye kondu (`aa0b85a^:scripts/score_abstention.py`, blob `792738dc…`).
Anahtarlar `kutle.py` · `harness_tablo.py` · `score_abstention.py` · `groundedness.py`'ye bağlı; her çıktının
özetine `olcum_aleti` künyesi yazılıyor. Üretim tarafı: `retriever.getir(…, rrf_k=)` ve
`gen_eval_grounded.py --rrf-k` (değer her satırın harness izinde); önsöz bayrağı zaten vardı.
K3 öncesi çekinme kayıtlarında `source_answers` alanı yok: orada `valid_trap` zaten cevaplı paydadır
(`valid_trap_anahtari` alanının yokluğu ayırt eder) — `--payda cevapli --pay-kaynagi onceki` bunu okur.

**F0.6'nın kodu.** `llm_client.HakemKimligi(model, saglayici, dusunme)`: düşünme modu olan ailede (bugün
`deepseek`) mod ve sabit sağlayıcı zorunlu ve varsayılansız; düşünme modu olmayan ailede mod verilemez;
geçersiz bileşim nesne kurulurken, ilk çağrıdan önce reddedilir. `groundedness.py`: `--hakem-saglayici`,
`--hakem-dusunme`; fiyatı kayıtsız hakem para harcanmadan reddedilir (önceden fiyat ilk çağrıdan **sonra**
soruluyordu); özetinde `hakem` künyesi. Doğrulama istemi ayrı fonksiyonda (`dogrulama_istemi`), sırası
önbelleğe uygun ve testle kilitli. `score_abstention.py`'ye bağlanmadı (DeepSeek ilk h1'de gerekiyor).
DeepSeek'in takma adı ve fiyatı F0.14'ün satırını bekliyor.

**Çıpalar — hakem çağırmayanlar, saklı hakem çıktılarından ($0):**

| anahtar | koşu | eski alet | düzeltilmiş | kayıt | hüküm |
| :-- | :-- | --: | --: | :-- | :-- |
| çekinme dedektörü | `olcum-bi` · `s2-harness-k10-etiketli` | 0,6275 · 0,6132 | 0,6838 · 0,7299 | [#61](kronoloji-53-62.md#61) | birebir |
| A1 tanımı | `s3-harness-acik` · `s3-harness-k10` | 0,5867 · 0,5844 | 0,5693 · 0,5953 | [#54](kronoloji-53-62.md#54) | birebir |
| üç okuma | `f04-rakip-onsozsuz` | — | 0,6925 · 0,7050 · 0,7425 | [#70](kronoloji-63-71.md#70) | birebir |
| `RRF_K` (gerçek indeks, CPU) | DEV v2 · DEV v1 | 0,9375 · 0,8750 (60) | 0,9500 (10) | [#62](kronoloji-53-62.md#62) | birebir |
| önsöz | istem metni | `aa04c78` | — | ADR-0058 | aynı |

#54'ün çıpası "o günün dedektörüyle" yazılmıştı; 2026-08-05 dedektörü ile ADR-0061 öncesi dedektör bu
dört koşuda aynı sonucu veriyor, tek eski dedektör yetti.

**Çıpalar — hakeme gidenler.** İkisi önbellekten ve önceki pay kayıtlarından $0'a, birebir üretildi
(önbellek anahtarı hakemin gördüğü metnin özeti olduğu için isabet, anahtarın tarihsel istemi aynen
kurduğunu da gösterir; API anahtarı verilmedi, çağrı imkânsızdı):

| anahtar | koşu | eski alet | düzeltilmiş | kayıt |
| :-- | :-- | :-- | :-- | :-- |
| kör payda | τ_g v1 · `tgta_v1` (M2) | 55 · 0,873 / 56 · 0,893 → katkı **+0,020** | 66 · 0,833 / 66 · 0,833 → **+0,000** | `karar3-m2-payda` |
| kaynak kırpması | `h2b` k=4 · k=10 | 3500: 68/12 · 0,735 · 65/15 · 0,723 | 12000: 69/11 · 0,739 · 62/18 · 0,726 | `f05-source-clip` |

**`gpt-4o-mini` yeniden çağrıldı — gürültü tabanı ölçütü TUTMADI.** `f02-biz-onsozsuz`'un 80 cevabı aynı
hakemle (OpenRouter, sağlayıcı OpenAI) iki kez yeniden puanlandı; hakeme giden istek gövdesi 80 kalemde
eski kodla bayt bayt aynı (sınandı):

| | `faithfulness_macro` | A1 | kütle | sıfır iddia |
| :-- | --: | --: | --: | --: |
| kayıt (2026-09-06) | 0,8499 | 0,8545 | 0,8011 | 0 |
| tekrar (2026-10-11, klip 3500) | 0,8314 | 0,8359 | 0,7836 | 0 |
| kırpmasız (2026-10-11) | 0,8380 | 0,8425 | 0,7898 | 0 |

Kayıt ↔ tekrar: 6 kalemin puanı, 10 kalemin iddia sayısı değişti; A1 −1,86 p, kütle −1,75 p. Aynı gün iki
koşu (tekrar ↔ kırpmasız) 5 kalemde ayrıştı; bunların hiçbiri 3.500 karakteri aşan üç altın maddeli kalem
(0 · 34 · 72) değil ⇒ **altın madde kırpmasının bu kümede etkisi 0**, aradaki 0,66 p A1 farkı aynı günün
hakem gürültüsü. Belgedeki gürültü tabanı (~0,3 A1, `faithfulness_macro` ±0,005; tuzak 2.8) aynı gün iki
koşudan ölçülmüştü; bugün aynı gün 0,66 p, bir ay arayla 1,86 p. ⇒ `yeniden_uret.sh`'ın "0,30 puanı aşarsa
DUR" kuralı bugünkü hakemle %80,1'i yeniden üretemez. Gürültü tabanı F0.6'da (DeepSeek ve `gpt-4o-mini`,
gerçek çağrı koşullarında) yeniden ölçülür; eşik o ölçümle aynı formülden yeniden türetilir (ADR-0050).
*2026-10-15: ölçüldü ([#85](#85)); bir ay arayla 1,86 p'lik fark, aynı gün aynı cevaplarda ölçülen oynamanın
içinde. Eşik F1.4'te bağlayıcı hakem moduyla birlikte konur (kullanıcı kararı).*

**Test.** Yeni: `test_rq2_anahtarlari.py` (+3 yavaş), `test_hakem_kimligi.py`, `test_kutle.py`'ye dört çıpa.
Hızlı takım 434, yavaş 3 yeşil.

**Ders.** *Önbellek ve önceki kayıtlar, hakeme giden anahtarları bile $0'a ve birebir sınamaya izin verdi;
para isteyen tek doğrulama, hakemin kendisini sınayan oldu — ve tutmadı.* Hakem bir alettir ve zamanla
kayar; çıpa sayısı, hakemin o günkü hâlinin sayısıdır.

---

<a id="77"></a>
## #77 — F0.7: ham TIES'te τ_a'nın %32'si taşınıyor; ezen seyreklik değil, norm farkı

**2026-10-11 · CPU, $0 (35 dk)** · `scripts/egitim/seyreklik_tablosu.py` · Kanıt:
`outputs/egitim/f07-seyreklik/seyreklik.json` · trim_k 0,2 (`tgta_v1`, `kollar.md`)

ΔW `merge_lora.load_deltas` + `merge_ties.dw` ile açıldı; kırpma ve işaret seçimi `merge_ties.ties` ile aynı
adımlar — 224 tensörün 224'ünde birleşik sonuç `ties()`'inkiyle bit düzeyinde aynı (koşu içinde denetlendi).
Normlar kayıtla aynı: ‖τ_g‖ 10,4722 · ‖τ_a‖ 1,1806. Oranlar kolun kare kütlesine göre; "taşınan" =
⟨birleşik, τ⟩ / ‖τ‖².

| kol | kırpmadan sonra | işaret seçiminden sonra | birleşmede taşınan |
| :-- | --: | --: | --: |
| τ_g | 0,722 | 0,722 | 0,678 |
| τ_a | 0,666 | 0,589 | 0,318 |

Modül türüne göre: τ_a'nın işaret seçiminden sonraki payı 11 türün hepsinde 0,584-0,595 (dar bant);
taşınan pay 0,194 (`in_proj_b`) ile 0,386 (`down_proj`) arası. τ_g işaret seçiminde hiçbir türde kayıp
vermiyor. Norm payları iki kolda benzer: en büyük pay `gate_proj` (0,345 / 0,276) ve `up_proj`
(0,232 / 0,283).

**Okuma (yorum, ölçüm değil):** kırpma iki kolu benzer budar (%28 ↔ %33); τ_a'ya özgü kayıp işaret
seçiminde (−7,7 p) ve iki kolun ortalandığı yerlerde 9 kat büyük τ_g'nin baskınlığında. L1'li yeniden
eğitim kırpma kaybını hedefler, asıl kaybı değil ⇒ plandaki kurala göre ("yalnız ölçüm desteklerse") L1
turu önerilmedi; karar kullanıcıda.

---

<a id="78"></a>
## #78 — F0.9 ön kontrol: kayıp maskesi iki modelde doğru; Gemma 4 kilitteki Unsloth'la yüklenmiyor

**2026-10-14 · yerel, $0** · ağırlık inmedi; yalnız tokenizer ve ayar dosyası · kilitteki sürümler
(`transformers` 5.10.2 · `unsloth` 2026.6.1 · `unsloth_zoo` 2026.6.1; yerel venv aynı sürümler, Python
3.12 — Modal'da 3.11) · tokenizer revizyonları `Qwen/Qwen3.5-4B@851bf6e806ef` ·
`google/gemma-4-E4B-it@ee0ef6023621` · kapının kodu `9c56cad` · Kanıt: bu girdi (komutlar aşağıda)

**1 · Şablon, gözle.** Aynı üç mesaj (sistem · kullanıcı · asistan) iki modelde eğitim render'ı:

```
Qwen   <|im_start|>system\nSİSTEM<|im_end|>\n<|im_start|>user\nSORU<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\nCEVAP<|im_end|>\n
Gemma  <bos><|turn>system\nSİSTEM<turn|>\n<|turn>user\nSORU<turn|>\n<|turn>model\nCEVAP<turn|>\n
```

Gemma'nın tur işaretleri `<|turn>user\n` / `<|turn>model\n` (`train_sft.py`'deki örnekle aynı), tur sonu
`<turn|>`. **Fark:** Qwen'in şablonu izsiz asistan cevabının önüne boş düşünce bloğu koyuyor (kayıtta
biliniyordu, [#39](kronoloji-39-52.md#39)); Gemma'nınki koymuyor. İki modelin SFT sinyali bu noktada
farklıdır: Qwen "boş düşünce + cevap", Gemma "doğrudan cevap" görür. Düşünce koruma kapısı (§2.5.4) ve
1024+512 zorla kapatma için not; ölçülmedi.

**2 · Kayıp maskesi.** `data/train/raft_scrubbed/train.jsonl`'ın ilk satırı, Unsloth'un kendi
`train_on_responses_only` fonksiyonu (`return_function=True`), kapının kuralları (`maske_ihlalleri`):

| model | token | kayıp alan | blok | ihlal |
| :-- | --: | --: | --: | :-- |
| Qwen3.5-4B | 1.102 | 53 | 2 | yok |
| Gemma 4 E4B-it | 1.058 | 46 | 2 | yok |

İki modelde de kayıp asistan işaretinin hemen ardından başlıyor ve tur sonu işaretini (`<|im_end|>\n` /
`<turn|>\n`) kapsıyor; kullanıcı tarafı tamamen maskeli. Aradaki 7 token Qwen'in boş düşünce bloğu.

**3 · Gemma kilitteki sürümlerle yüklenmiyor.** `import unsloth`'tan sonra
`AutoConfig.from_pretrained("google/gemma-4-E4B-it")` şu hatayı veriyor: `AttributeError: num_kv_shared_layers is 0 (no KV
sharing) -- hidden from the cache constructor …`. Unsloth içe aktarılmadan aynı çağrı geçiyor. Zincir:
`transformers` 5.10.2'nin `configuration_utils.py:859` satırı (`logger.info(f"Model config {config}")`)
günlük düzeyinden bağımsız olarak `repr`'i çağırıyor; `repr` varsayılan bir `Gemma4TextConfig` kuruyor;
`unsloth_zoo/temporary_patches/gemma4.py`'nin `_Gemma4KVSharedSafeProxy`'si onda patlıyor. Unsloth'un
yükleyicisi (`unsloth/models/loader.py:1085-1110`) hatayı yutup `RuntimeError: Unsloth: No config file
found` diye **yanlış teşhisle** duruyor (`FastModel.from_pretrained`, çevrimdışı kipte; ağırlık aranmadan).
Yani kilitteki sürümlerle Gemma `train_sft.py`'de model yüklemesinde durur — Modal'da ilk dakikada, sessiz
değil ama yanıltıcı mesajla. PyPI'da daha yeni sürümler var (`unsloth`/`unsloth_zoo` 2026.10.5,
`transformers` 5.19.0); hangisinin düzelttiği denenmedi.

```
# 3'ü tekrarlamak için (yerel, $0):
python -c "import unsloth; from transformers import AutoConfig; AutoConfig.from_pretrained('google/gemma-4-E4B-it')"
python -c "from transformers import AutoConfig; print(type(AutoConfig.from_pretrained('google/gemma-4-E4B-it')))"
# 2'yi tekrarlamak için: tokenizer'ı unsloth'tan ÖNCE yükle (3 yüzünden), sonra
# train_on_responses_only(None, instruction_part=U, response_part=A, tokenizer=t, return_function=True)
# ({"input_ids": [ids]}) ve ortam_kilidi.maske_bloklari / maske_ihlalleri
```

**Okuma:** [`YAYIN_YOL_HARITASI.md`](../yol_haritasi/YAYIN_YOL_HARITASI.md) §2.4'ün "paket kilidi" maddesi ve
[`EGITIM_ORTAMI.md`](../yontem/EGITIM_ORTAMI.md) §6 m.6'nın öngördüğü durum gerçekleşti: Gemma, Qwen'in
kilidiyle eğitilemiyor. Kural gereği Qwen'in kilidine dokunulmaz, Gemma'nın kilidi ayrı yazılır; bu da iki
modelin farklı paket sürümleriyle eğitilmesi demek ve makalede sınırlılık olarak yazılır. Hangi sürümün
seçileceği kullanıcı kararı (F0.9).

---

<a id="79"></a>
## #79 — Gemma'nın kilidi: `unsloth` 2026.10.1 yüklüyor; Unsloth depoyu sessizce değiştiriyor; düz hedef listesi kulelere taşıyor

**2026-10-14 · yerel, $0** · ağırlık inmedi (yükleme, ağırlık adımında kesildi) · aday paketler ayrı klasöre
`--no-deps` kuruldu, kilidin geri kalanı aynı · kullanıcı kararı: Gemma ve Qwen ayrı kilit, ayrı imaj

**1 · Sürüm.** PyPI'daki bağımlılık bildirimleri: `unsloth` 2026.6.1 … 2026.9.14'ün hepsi
`transformers<=5.5.0` istiyor; Qwen'in kilidi 2026.6.1'i `transformers` 5.10.2 ile `--no-deps` kurarak bu
aralığın **dışında** çalıştırıyor (F0.4 eşdeğerliği geçtiği için Qwen için işlem yok; not). 5.10.2'yi
resmen kapsayan ilk sürüm `unsloth`/`unsloth_zoo` **2026.10.1** (`transformers<=5.17.0`); kilidin geri
kalanı (torch 2.10.0 · trl 0.24.0 · peft 0.19.1 · datasets 4.3.0 · accelerate 1.13.0 · bitsandbytes 0.49.2)
onun bildirdiği aralıklara giriyor. 2026.10.1 ile `import unsloth` sonrası `AutoConfig` geçiyor ve
`FastModel.from_pretrained` ağırlık yükleme adımına ulaşıyor (#78'deki hata yok). **Gemma'nın kilit adayı:
Qwen'in kilidi + `unsloth`/`unsloth_zoo` 2026.10.1.**

**2 · Sessiz depo değişimi.** Unsloth `google/gemma-4-E4B-it` istenince ağırlıkları kendi kopyasından,
`unsloth/gemma-4-E4B-it`'ten yüklüyor (`unsloth/models/mapper.py`; `use_exact_model_name=False`
varsayılanı); künye ise `google/…` yazardı. Qwen3.5 bu listede yok, τ_g/τ_a `Qwen/Qwen3.5-4B`'den eğitildi.
İki deponun dosya özetleri: `model.safetensors` (15.992.595.884 bayt), `tokenizer.json`,
`processor_config.json`, `generation_config.json` **aynı**; `config.json`, `tokenizer_config.json`,
`chat_template.jinja` **farklı** — Unsloth'un kopyasında bitiş işareti `<eos>` (1) yerine `<turn|>` (106),
`pad_token_id` 0 ekli. `raft_scrubbed`'ın ilk 500 satırında iki şablonun render'ı ve token'ları birebir
aynı. Fark yalnız TRL bitiş işareti eklerse eğitime girer (TRL `add_eos`; Unsloth veri hazırlığını kendi
fonksiyonuyla değiştiriyor) — eğitimdeki maske dökümünde görülecek. Karar: kullanıcının seçtiği depo
(`google/…`) `use_exact_model_name=True` ile yüklenir.

**3 · LoRA hedefleri.** Ağırlıksız iskelet: Gemma `Gemma4ForConditionalGeneration`, 593 doğrusal katman —
dil kulesi 343, görüntü 113, ses 134. PEFT'in eşleştirme kuralıyla düz 7 adlık liste (`q_proj k_proj v_proj
o_proj gate_proj up_proj down_proj`) dil kulesinde 258 modüle ek olarak **görüntü kulesinde 112, ses
kulesinde 36** `Gemma4ClippableLinear`'a takılıyor ([ADR-0030](../adr/kararlar-0027-0044.md#adr-0030)'un
`all-linear` tuzağının eşi). Desen
`model\.language_model\.layers\.\d+\.(self_attn\.(q_proj|k_proj|v_proj|o_proj)|mlp\.(gate_proj|up_proj|down_proj))`
yalnız 258 dil modülü seçiyor (q 42 · k 24 · v 24 · o 42 · gate/up/down 42'şer; k/v'nin 24 olması KV paylaşan
katmanlardan). Dışarıda kalanlar: Gemma'ya özgü `per_layer_input_gate` / `per_layer_projection` (42'şer).
Qwen'in 11 adı görüntü kulesine takılmıyor (Qwen görüntü kulesinin adları `qkv`, `proj`, `linear_fc*`).
`unsloth` 2026.10.1 düz listeyi `finetune_*` bayraklarıyla bir desene çeviriyor (`vision.py` ~4296-4318);
hangi modüllere takıldığı LoRA kule kapısıyla smoke'ta görülecek.

**Okuma:** Gemma'nın kilidi, deposu ve hedefleri belli; kalan iş koddur (F0.9 kutuları).

<a id="80"></a>
## #80 — F0.9 smoke: iki model A100-40GB'da 50 adım koştu; Gemma bf16'da `grad_checkpoint: false` ile sığdı (tepe 34,4 GB / 42,4 GB); ilk Qwen denemesini kilit kapısı durdurdu

**2026-10-15 · Modal, hesap `rfetha`, `A100-40GB` (NVIDIA A100-SXM4-40GB, 42.405.855.232 bayt), bölge us-east** ·
50 adım SFT, seed 3407, `--hassasiyet bf16-taban`, `raft_scrubbed` (17.323 satır), batch 2 × grad_accum 8 =
etkin 16, `--no-grad-checkpoint`, lr 1e-4, warmup 0,05, r=16 α=32 dropout 0,05 · kullanıcı onayı: "başlat"
(2026-10-15) · kanıt: `outputs/egitim/f09/f09-qwen-smoke/` ve `outputs/egitim/f09/f09-gemma-smoke/`
(`KUNYE.json` · `maske_ornegi.txt` · `trainer_state.json` · `adapter_config.json` · `modal_log.txt`;
ağırlıklar ve `checkpoint-50` Modal'daki `hukuk-outputs` biriminde kaldı, repoya girmedi)

**1 · Ölçümler** (hepsi `KUNYE.json` ve `trainer_state.json`'dan; VRAM süreç başından, model yükleme dahil;
süre yalnız `trainer.train()`):

| | Qwen3.5-4B | Gemma 4 E4B |
| :--- | ---: | ---: |
| kilit dosyası (sha256 öneki) | `egitim_ortami.yaml` `21c42d23` | `egitim_ortami_gemma.yaml` `5d68f638` |
| künye `durum` · adım | bitti · 50/50 | bitti · 50/50 |
| tepe VRAM, ayrılan | 21.846.276.096 B (21,85 GB) | 29.443.661.824 B (29,44 GB) |
| tepe VRAM, rezerve | 22.309.502.976 B (22,31 GB) | 34.389.098.496 B (34,39 GB) |
| kartın bellek payı (rezerve/42,41 GB) | %52,6 | %81,1 |
| `trainer.train()` süresi · s/adım | 534,3 s · 10,686 | 527,5 s · 10,549 |
| maske: örnek token · kayıplı token | 1102 · 53 | 1058 · 46 |
| `lora_yerlesim` (takılan · kule dışı) | künyede yok (kilitte `yerlesim` tanımsız) | **258 · 0** |
| kayıp, adım 10 · 20 · 30 · 40 · 50 | 0,799 · 0,483 · 0,349 · 0,350 · 0,353 | 1,275 · 0,582 · 0,401 · 0,367 · 0,357 |
| `train_loss` (ortalama) | 0,467 | 0,596 |

Gemma'da eğitilebilir parametre 34.881.536 / 7.975.982.368 (%0,44, `modal_log.txt`). Gemma'nın ilk adımı 38,4 s
(ısınma), sonrakiler ~7 s; yukarıdaki 10,5 s/adım ortalaması ara değerlendirmeyi de içerir.

**2 · Maske dökümü, gözle okundu.** Qwen: kayıplı bölge `<|im_start|>assistant\n`'dan sonra
`<think>\n\n</think>\n\n` ile başlıyor (şablonun boş düşünce bloğu; #78'deki not doğrulandı), cevabı ve
`<|im_end|>\n`'ı kapsıyor. Gemma: `<bos><|turn>system … <turn|>` ile başlıyor, kayıplı bölge `<|turn>model\n`'dan
hemen sonra başlıyor (düşünce bloğu yok), cevap ve `<turn|>\n` ile bitiyor. İki modelde de sistem, kaynak ve
soru kayıpsız; `satir_maske_sonrasi` 17.323 = hiçbir satır maskeyle elenmedi. Gemma cevabı sonunda **tek**
`<turn|>` görünüyor; metin dökümü `<eos>` gibi ayrıca eklenen bir bitiş işaretini göstermez, #79 §2'deki
"TRL ek bitiş işareti ekliyor mu" sorusu bu dökümden **kapanmıyor** (açık, aşağıya bkz.).

**3 · Sığma sonucu.** Gemma bf16 taban ağırlıklarla, `grad_checkpoint: false` tarifiyle A100-40GB'a **sığdı**:
tepe rezerve 34,39 GB ile kartın 42,41 GB'ının %81,1'i; 8,0 GB pay kaldı. Tarif değişikliği gerekmedi, ADR-0102
açılmadı. Pay yalnız 50 adım ve bu veride ölçüldü: örnek uzunluğu `max_seq_len` 2048 tavanına yakın dizilerde
tepe daha yüksek olabilir; 50 adımın en uzun örneği görmüş olması garanti değil.

**4 · İlk Qwen denemesi kilit kapısına takıldı.** İlk komutu `--lr` ve `--warmup-ratio` vermeden yazdım;
`train_sft.py`'nin varsayılanları (lr 2e-4, warmup 0,03) kilidin tarifiyle (lr 1e-4, warmup 0,05) uyuşmuyor.
Kilit kapısı model yüklenmeden durdurdu (`[kilit] 2 alan … uymuyor`, çıkış kodu 1; uygulama
`ap-PKr0ehCaxkJCpkWWgfMx6I`); GPU'da eğitim başlamadı. Komutu kilit değerleriyle yeniden verdim
(`ap-KLyzlDID122EWAmWNqiw5K`), sonra Gemma'yı baştan o bayraklarla başlattım (`ap-s6GEejIsCbpaBsVwJaZEUn`).
Kaynağı: `modal_train.py::spawn_sft`'in `--lr`/`--warmup-ratio` varsayılanı yok ("dokunma"), kararı betiğin
varsayılanı veriyor; #79 sonundaki komut tarifi bu iki bayrağı anmıyordu. **Ders:** kilit kapısı tam bu sınıfı
yakalıyor (hata vermeden yanlış hiperparametre); koşu komutunun bayrakları kilit tarifinden **tek tek**
çıkarılmalı, hatırdan yazılmamalı.

**5 · Doğrulanamayan veya açık kalan.**
- 50 adımlık kayıp eğrisi bir sonuç değil, kapı denetimi: iki eğri de adım 30'dan sonra düzleşiyor; bu bir
  yakınsama kanıtı sayılmaz.
- Tepe VRAM, uzun örneklerle karşılaşmamış olabilir (yukarıda).
- Gemma'nın hedef kodu tam eğitim sırasında TRL'nin ek `<eos>` ekleyip eklemediği (#79 §2) bu çıktılardan
  okunamıyor; tokenizasyon sonrası ilk örneğin `input_ids`'inin dökümü gerekir (ayrı iş, F0.9 dışı).
- Modal'ın fatura tutarı bu belgede **ölçülmedi** (panele bakılmadı); iki koşu 534 s ve 528 s eğitim +
  yükleme süresi.

**Okuma:** F0.9'un kod kapısı iki modelde de geçti: kilit, maske ve (Gemma'da) LoRA kule kapısı gerçek
GPU'da çalıştı, Gemma A100-40GB'a sığıyor, adım süreleri iki modelde ~10,5-10,7 s. Gemma'nın teknik
kapısının kalan kutuları (llama.cpp, Q4_K_M, DEV Türkçe oranı, düşünce kapanışı) bu girdiyle kapanmadı.

<a id="81"></a>
## #81 — F0.14: DeepSeek V4.1 Flash'ın tarihli kimliği ve fiyatı; fiyat modelin değil sağlayıcının, düşünme modunda `temperature` yok sayılıyor

**2026-10-15 · $0 (anahtarsız okumalar) · kullanıcı onayı: dış okumalar "Hepsine izin", sağlayıcı "DeepInfra"
(2026-10-15, [ADR-0102](../adr/kararlar-0064-0085.md#adr-0102))** · kanıt:
`outputs/eval/f0/f014-f016-dis-bilgiler/` (ham yanıtlar ve sayfalar; `KUNYE.json`'da URL, erişim saati, sha256)

**1 · Kimlik.** OpenRouter `GET /api/v1/models` (14:39 UTC): `id` `deepseek/deepseek-v4.1-flash`,
`canonical_slug` **`deepseek/deepseek-v4.1-flash-20260910`** (oluşturma 2026-09-10 06:21 UTC), bağlam
1.048.576 token, girdi metin + görsel. Aynı slug'ı taşıyan bir `:batch` uç noktası da var; senkron istemciden
kullanılmaz (Sonnet `:batch`'ının 404'ü, `llm_client.py`). DeepSeek'in kendi fiyat sayfası `deepseek-flash`
adını "DeepSeek-V4.1-Flash"a bağlıyor; eski `deepseek-v4-flash` adı da V4.1 Flash'a gidiyor.

**2 · Fiyat: tek bir "liste fiyatı" yok.** Aynı model 33 sağlayıcıda satılıyor (`/endpoints`): girdi
$0,024-0,60/M, çıktı $0,18-2,40/M, önbellekli girdi $0,0029-0,03/M; hassasiyet fp8 15 · fp4 3 · fp32 2 ·
belirtilmemiş 13; `seed` 19 uç noktada var. Modelin üst düzey `pricing` alanı bugün en ucuz uç noktayı
(OpenInference, fp4) gösteriyor: $0,02376 / $0,72 / $0,0054. 2026-10-11'de aynı alan $0,30 / $1,20 / $0,006
okunmuştu (sohbette, kayda geçmemişti). Alan sabit bir liste fiyatı değil; maliyet tahmini sabitlenen
sağlayıcının fiyatıyla yapılır.

| sağlayıcı | hassasiyet | girdi · çıktı · önbellekli girdi ($/M) | `seed` | son 1 gün çalışırlık |
| :-- | :-- | :-- | :-: | --: |
| **DeepInfra** (seçilen, `deepinfra/fp8`) | fp8 | 0,14 · 0,42 · 0,0042 | var | %100 |
| DeepSeek (modelin sahibi) | belirtilmemiş | 0,15 · 0,60 · 0,003 (yoğun saatte ×2) | yok | %88,2 |
| CoreWeave | fp8 | 0,15 · 0,65 · 0,006 | var | %99,8 |
| Morph | fp8 | 0,033 · 0,60 · 0,009 | var | %100 |
| OpenInference (en ucuz) | fp4 | 0,024 · 0,72 · 0,0054 | var | %97,8 |

DeepSeek'in kendi sayfası: yoğun olmayan saatte $0,15 / $0,60 / $0,003; yoğun saatte (hafta içi UTC 01-04 ve
06-10) iki katı. DeepInfra'nın uç noktasında `discount: 0.3` işareti var; listelenen fiyatın indirimli olup
olmadığı yanıttan anlaşılmıyor, koşu günü yeniden okunur.

**3 · Düşünme modunda `temperature`.** DeepSeek'in belgesi (`guides/thinking_mode`): *"Thinking mode does not
support the temperature, presence_penalty, or frequency_penalty parameters … setting these parameters will
not trigger an error but will also have no effect."* `top_p` düşünme modunda yalnız 0,95-1,0 aralığında etkili.
Düşünme varsayılan olarak açık (effort `high`). OpenRouter'daki 33 uç noktanın hepsi `temperature`'ı
desteklenen parametreler arasında sayıyor; bu yalnız parametrenin kabul edildiğini söyler, etkisini değil.
`groundedness.py` hakemi `temperature=0` ile çağırıyor; hakemin düşünmesi açıkken bu sıfır, DeepSeek'in kendi
sunucusunda kesin olarak, DeepInfra'da belki hiçbir şeyi sabitlemiyor. F0.6'nın mod başına iki tekrarı tam
bu oynamayı ölçer.

**4 · Koda giren.** `llm_client.py`: takma ad `deepseek-v4.1-flash` → `deepseek/deepseek-v4.1-flash-20260910`;
fiyat (0,14, 0,42) $/M, kaynağı ve erişim saati satırında; önbellekli girdi fiyatı tabloda yok (tahmin
önbelleksiz, yani üstten). Test: `tests/test_hakem_kimligi.py` (fiyatsız hakem testi artık kayıtsız bir
kimlik kullanıyor; DeepSeek'in fiyatı kayıtlı).

**5 · Doğrulanmamış.** Tarihli slug'la yapılan çağrının OpenRouter'da kabul edildiği (F0.6'nın ilk çağrısında
görülür) · DeepInfra'nın düşünme modunda sıcaklığı uygulayıp uygulamadığı · indirim işaretinin anlamı.

**Okuma:** sağlayıcı sabitlenmeden fiyat da sabitlenemez. "Liste fiyatı" diye okunan alan dört günde
$0,30'dan $0,024'e indi; bugün en ucuz uç noktanın fiyatını gösteriyor.

<a id="82"></a>
## #82 — F0.16 ilk adımlar: DEV bağlamı donduruldu (recall@10 0,9500, iki üretim bayt bayt aynı); sunucu sürümleri farklı; manşet koşu 4 slotla koşmuştu; Modal'ın ölçüm yükü krediye sığmayabilir

**2026-10-15 · CPU ve okumalar, $0 · kullanıcı kararları (2026-10-15, [ADR-0102](../adr/kararlar-0064-0085.md#adr-0102)):
kiralık kartta `server-cuda-b10902` + compose bayrakları · pilot önce yalnız Modal'da, yalnız A10'da** · kanıt:
`data/eval/dev/baglam/h1-k10.json` · `outputs/eval/f0/f014-f016-dis-bilgiler/`

**1 · Bağlam dondurma (ADR-0097 m.6).** `scripts/olcum_uretim/baglam_dondur.py --data data/eval/dev/core_hard.jsonl
--harness-indeks data/index/mevzuat_bge_m3_s2 --harness-k 10 --rrf-k 10 --seed 3407 --n 80 --max-chunk-chars 900`
→ `data/eval/dev/baglam/h1-k10.json`, 80 kalem, 809.495 bayt, sha256
`026668000583d6e3d3988b97d1cb3c3a85d740594686901aa0e8da3f213e6135`. İkinci üretim `cmp` ile bayt bayt aynı;
recall@10 **0,9500** (`recall_kapisi.py`). Bağlam, canlı üretimin kullandığı fonksiyonla üretiliyor
(`gen_eval_grounded.harness_baglami`, bu iş için davranışı değiştirmeden ayrıldı); `gen_eval_grounded.py
--donmus-baglam DOSYA` bağlamı bu dosyadan okur. Dosyanın künyesindeki rejim (soru dosyasının sha256'sı, seed,
n, k, `rrf_k`, kırpma) koşununkinden farklıysa ya da kalem eksik veya yineleniyorsa üretim durur. Her cevap
satırının `harness` izine dosyanın sha256'sı yazılır (`tests/test_baglam_dondur.py`, 12 test).

Dizüstündeki eski koşuların modele gösterdiği bağlamla kalem kalem karşılaştırma (`context_shown`):

| koşu | tarih | aynı |
| :-- | :-- | --: |
| `hp/hp-rakip-havuzu` (Sonnet 5) | 2026-09-09 | 80/80 |
| `gorev/g22-kv-fp16` | 2026-09-11 | 80/80 |
| `sprint2-olcum/s17-kuantizasyon-egrisi` (q4 · q5 · q8) | 2026-09-12 | 80/80 |
| `faz0/f02-biz-onsozsuz` (manşet) ve aynı günün `f04`, `f08`, `f11` koşuları | 2026-09-06/07 | 78/80 |

f02'den ayrılan iki kalem id 7 ve 63: f02'nin bağlamında `İŞ KANUNU|Madde 111` ve `|Madde 87` vardı, ikisi de
mülga. Yürürlük süzgeci 2026-09-07'de eklendi; indeksin künyesindeki "getirilen mülga 2 → 0" kaydıyla aynı
iki kalem.

**2 · Sunucu sürümleri.** Ölçüm hattının yerel derlemesi `~/code/llama.cpp/build-cuda`: `version: 1 (0cea362)`,
commit 2026-07-24, GNU 13.3. Depo sığ klon olduğu için derleme numarası okunmuyor. Konteyner
`ghcr.io/ggml-org/llama.cpp:server-cuda-b10902`: build 10902, commit `df03399b8`, GNU 14.2. İki sürüm
**farklı**. İkisi de bayraksız açılınca **4 slot** açıyor (`n_slots = 4`, `kv_unified = 'true'`): konteynerde
dizüstünde CPU'da (`-ngl 0`) kısa bir açılışla, yerelde f02'nin sunucu günlüğünden okundu. **Manşet sayı
(f02, kütle 0,8011) 4 slotla üretildi**; istemci istekleri sırayla gönderdiği için aynı anda yalnız bir slot
çalışıyordu. Planın "tek paralel slot" ifadesi bu yüzden "istekler tek tek" diye okunur (ADR-0102).
Compose'un bayraklarında ölçüm betiğinde olmayan bir bayrak var: `--reasoning-format deepseek` (2026-09-11'de
ölçüldü: `b10902`'de varsayılanla aynı davranış). Kullanıcı kararı: kiralık kartta `b10902`, compose
bayraklarıyla. Dizüstüyle fark sürüm ve donanımı birlikte içerir; ikisi bu tasarımda ayrılmaz.

**3 · Aday kartların o günkü fiyatı.** Modal (`modal.com/pricing`, saatlik): T4 $0,59 · L4 $0,80 · A10 $1,10 ·
L40S $1,95 · A100-40GB $2,10 · A100-80GB $2,50 · H100 $3,95. Aylık ücretsiz kredi $30 (hesap başına). Vast,
herkese açık teklif listesi (veri merkezi, doğrulanmış, boşta, tek kart, isteğe bağlı): yalnız **34 teklif**.
En ucuzları RTX A5000 $0,23/sa (2 makine), RTX 3090 $0,32/sa (2), RTX 5060 Ti $0,16/sa (7, 16 GB).

**4 · Toplam yük tahmini (pilottan önce, kaba).** Ölçüm yükü dizüstü cinsinden ~185-190 saat (ADR-0096'nın
türetimi; kendi hesabı orada da doğrulanmamış). f02'de cevap başına ortalama 783 token üretildi; dizüstünde
çözme hızı ~64 token/s (f02 sunucu günlüğü). Bu yük ~30-45 milyon token eder. Cevaplar sırayla üretilmek
zorunda: paralel slot metni değiştiriyor (S12/KARAR-6, `docs/YENIDEN_URETIM.md`). Bu yüzden maliyeti
belirleyen tek şey kartın tek akıştaki hızı. Kartların hızı ölçülmedi; bellek bant genişliğinden, dizüstünün
oranıyla tahmin edildi.

| yol | milyon token başına (tahmin) | toplam (tahmin) |
| :-- | :-- | :-- |
| Modal (A10 · A100-40GB · T4 · L40S · L4) | ~$2,9-4,4 | ~$90-200, Modal kredisinden |
| Vast (RTX A5000 · RTX 3090) | ~$0,5-0,6 | ~$15-27, nakit |

Nakit tavanı ($75, ADR-0097 m.5) iki yolda da aşılmıyor. Modal'ın aylık kredisi eğitimle paylaşılıyor
(eğitim ortalama ~$22-26/ay, [ADR-0101](../adr/kararlar-0064-0085.md#adr-0101)). ~$100'ü aşan bir ölçüm
yükünün Şubat–Nisan'a takvimi geciktirmeden sığıp sığmadığı belirsiz; m.4'ün kuralı Vast'ı seçebilir. Vast'ta
veri merkezi teklifi az; aynı tipten iki makine bulmak bir risk. Sayılar pilottan sonra ölçülmüş hızla
yeniden hesaplanır.

**Okuma:** bağlam artık makineden bağımsız, birebir yeniden üretilebilir bir dosya. Plan "tek slot"
derken manşet sayının gerçekte 4 slotla, istekler sırayla gönderilerek üretildiğini bilmiyordu. Fiyat tahmini
Modal'ın krediye sığmayabileceğini gösteriyor; kararı pilotun ölçtüğü hız verecek.

<a id="83"></a>
## #83 — F0.16 pilotu: A10'da aynı makinede ve iki makine arasında 80/80 birebir aynı cevap; dizüstüyle yalnız 14/78; ölçüm kartı Modal A10

**2026-10-15 · Modal, hesap `rfetha`, `A10` (NVIDIA A10, 23.028 MiB, sürücü 610.57.04), iki konteyner eş zamanlı ·
kullanıcı onayı: pilot "Başlat", platform "Modal A10", F0.5 (b) ölçütü "aynı gün, aynı cevaplar" (2026-10-15,
[ADR-0103](../adr/kararlar-0064-0085.md#adr-0103))** · kanıt: `outputs/eval/f0/f016-pilot/A10/{m1,m2}/`
(`KUNYE.json` · cevap dosyaları; `llama_server.log` yerelde, `*.log` git dışı, okunan alanlar künyede) · kod: `scripts/olcum_uretim/modal_pilot.py`,
`olcum_karti.py`, `makine_kapisi.py` (testler `tests/test_olcum_karti.py`, `test_makine_kapisi.py`,
`test_modal_pilot.py`)

**1 · Kurulum.** Sunucu `ghcr.io/ggml-org/llama.cpp:server-cuda-b10902`; bayraklar `docker/compose.yaml`'dan
okundu, yalnız model yolu ve adres değişti (ADR-0102 m.1). Model yayımlanmış GGUF: `indir_model` ile sabit
revizyondan indirildi, bayt ve sha256 kapısından geçti (`755e15e9…86e7bffc`). Bağlam dondurulmuş dosyadan
(`02666800…f213e6135`, [#82](#82)). Rejim h1: düşünme açık, 1024 + 512, kırpma 900, seed 3407, n 80. m1 80 cevabı
iki kez, m2 bir kez üretti. Bilgisayarda önce `b10902` konteyneriyle 6 kalemlik bir kod denemesi yapıldı; ölçüm
değildi, yalnız dondurulmuş yolun uçtan uca çalıştığını gösterdi.

**2 · Sunucu, koşan süreçten.** İki makinede de `version: 0.4.0-dev (build 10902, commit df03399b8)`,
`n_slots = 4`, `kv_unified = true`. `/v1/models` doğru GGUF'u gösterdi. Koşan komut (`/proc/<pid>/cmdline`):
`-ngl 99 -fa on --no-context-shift --cache-type-k q8_0 --cache-type-v q8_0 -c 8192 --reasoning-format deepseek`
(+ model, adres, port).

**3 · Sonuçlar.**

| | m1 · 1. tekrar | m1 · 2. tekrar | m2 |
| :-- | --: | --: | --: |
| GPU (nvidia-smi `uuid`) | `GPU-b929d6c1…` | (aynı) | `GPU-3d352372…` |
| bölge (`MODAL_REGION`) | us-east | (aynı) | us-west |
| süre · cevap başına | 640,6 s · 8,01 s | 640,2 s · 8,00 s | 630,8 s · 7,88 s |
| cevap başına maliyet (Modal liste fiyatı $1,10/sa) | $0,00245 | $0,00244 | $0,00241 |
| ortalama üretilen token (düşünce dahil) | 747,3 | 747,3 | 747,3 |
| kesik · zorla kapatılan · düşünen | 0 · 4 · 80 | 0 · 4 · 80 | 0 · 4 · 80 |

- **Aynı makinede** (m1 1. ↔ 2. tekrar): **80/80 birebir aynı** (`makine_kapisi.py`).
- **İki makine arasında** (m1 ↔ m2): **80/80 birebir aynı**. İki makine farklı GPU'larda ve farklı bölgelerde
  koştu.
- Üç cevap dosyası bayt bayt aynı: sha256 `c5035eb390ed1835b28ed004164a5cdc16a1252838124567692c1081bb7cd093`.
  m1'in 1. tekrarı A10'un **referans cevaplarıdır** (makine geçiş kapısı; F0.6'nın girdisi).
- Kesik oranı %0. Pilotun GPU maliyeti ~$0,6 (240 cevap; model indirme ve sunucu açılışı hariç), Modal
  kredisinden. Fatura panelden okunmadı.

**4 · Dizüstüyle fark (ADR-0097 m.3: yalnız kayda geçer).** f02'nin cevapları (dizüstü, yerel derleme `0cea362`,
2026-09-06) ile pilotun referans cevapları, bağlamı aynı 78 kalemde karşılaştırıldı: **14/78 birebir aynı**.
Metin benzerliğinin medyanı 0,723, en düşüğü 0,022 (`difflib`). Bugünkü bilgisayar denemesinde aynı konteyner
sürümü ve aynı dondurulmuş bağlamla 6 kalemin **2'si** aynı; benzerlik 0,999 · 0,386 · 0,994 · 0,965. Fark sürümle
açıklanamıyor: aynı sürüm, farklı donanım da farklı cevap veriyor. Kesik oranı f02'de 4/80, pilotta 0/80. Ortalama
token f02'de 782,5, pilotta 747,3. Kütle düzeyindeki fark ölçülmedi; f02'nin puanı başka bir günün hakemiyle
alındı ([#76](#76)).

**5 · Yükün ölçülen hızla yeniden hesabı.** ~185-190 dizüstü saati ÷ dizüstünde ~18,75 s/cevap (80 cevap ~25 dk,
`docs/YENIDEN_URETIM.md`) ≈ 36.500 cevap. A10'da 8,0 s/cevap ile ≈ 81 saat ≈ **$89**, Modal kredisinden. Beş aya
yayılırsa ayda ~$18; testin payı (~147 dizüstü saati) Şubat–Nisan'da ayda ~$23. Eğitimin ortalaması ~$22-26/ay
([ADR-0101](../adr/kararlar-0064-0085.md#adr-0101)); toplam iki hesabın aylık $60 kredisinin altında kalıyor.
Bir ay krediyi aşarsa m.4'ün kuralı o ay için Vast'ı seçer. Doğrulanmamış: ~190 saatlik yükün kendi hesabı
(ADR-0096) ve yerelde yalnız bir Modal hesabının (`rfetha`) tanımlı olması.

**6 · Seçim (kullanıcı kararı, ADR-0103).** Ölçüm kartı **Modal A10**: DEV de test de bu tipte koşar
(ADR-0097 m.1). Pilotta iki makine birebir aynı çıktığı için tip içinde makine ve bölge serbest; her yeni makine
önce referansın 80 cevabını birebir yeniden üretir (ADR-0098 m.3, `makine_kapisi.py`). Üretim gerekirse birkaç
makineye paralel bölünebilir. Tek sunucuda paralel slot yine yasak.

**Okuma:** dondurulmuş bağlam ve sabit sunucuyla kiralık kartta üretim deterministik. "Aynı girdi farklı cevap
veriyor" notu ([`YENIDEN_URETIM.md`](../yontem/YENIDEN_URETIM.md)) dizüstü için kaydedilmişti; A10'da üç koşuda bir kez
bile görülmedi. Dizüstüyle fark büyük: kayıttaki dizüstü cevapları ile kiralık kart cevapları arasında kalem
düzeyinde kıyas yapılamaz. ADR-0097 m.1'in "tek kart tipi" kuralının neden zorunlu olduğu bu tabloda görülüyor.

**Not (2026-10-17, kart #20): Modal faturası okundu.** Kaynak: Modal paneli (hesap `rfetha`, Ekim döngüsü; okuma
2026-10-17) ve uygulama/gün ayrımı için `modal billing report`. Bu pilotun faturası **$0,73** (A10, iki konteyner,
2026-10-15); tahmin ~$0,6'ydı, fark model indirme ve sunucu açılışı. Ekim'in tamamı **$5,15**, hepsi `rfetha`'da
(kalan kredi $24,85): F0.4 dört koşu $2,37 ([#75](#75), tahmin ~$2; oradaki "ilk hesap" `rfetha`) · F0.9 duman $1,11
([#80](#80); kilit kapısının durdurduğu ilk deneme $0,08 dahil) · vLLM pilotu $0,97 ([#86](#86) $0,72, tahmin ~$0,64 ·
[#87](kronoloji-87-98.md#87) $0,24, tahmin ~$0,2). Ekim'de ikinci hesapta kayıtlı koşu yok. Raporun toplamı $5,17;
panelle $0,02'lik fark açıklanmadı, sayı panelden alındı (tuzak 6.3).

<a id="84"></a>
## #84 — Ajan uygulaması hattı: Mike taraması, ADR-0104 ve aynı gün denetimi (ADR-0105); ölçüm yok

**2026-10-15 · ölçüm yok, GPU yok, $0 · kullanıcı kararları
([ADR-0104](../adr/kararlar-0064-0085.md#adr-0104), [ADR-0105](../adr/kararlar-0064-0085.md#adr-0105))** · kanıt:
[`knowledge/mike-tarama/`](../../knowledge/mike-tarama/README.md) (sekiz dosya + sentez, 2.351 satır) · commit'ler
`13b0411` … `40c1ce8` (`talk-think`)

**1 · Mike taraması.** `Open-Legal-Products/mike` (TypeScript, AGPL-3.0), `main` dalının tarball'ı; yalnız tasarım
okundu, kod kopyalanmadı. Sekiz alan alt ajanlara bölündü: ajan döngüsü · sağlayıcı ve yerel model · atıf ve bağlam ·
tablo biçimli inceleme · belge ve redline · veri modeli ve kuyruk · workflow, MCP, güvenlik · arayüz ve test. Hiçbir
davranış gerçek bir modelle çalıştırılmadı; satır numaralarının bir kısmı yaklaşık.

- Ajan döngüsü Mike'ın kendisinin değil, Vercel AI SDK'nın `streamText` döngüsü: sert sınır 16 tur, prompt modele
  "10" diyor. 14+ araç, ~12 bin karakterlik sistem prompt'u; belgenin tamamı bağlama giriyor (parçalama, embedding,
  OCR, token sayımı ve kısıtlı çözüm yok).
- Taşınan iskelet: değişmez belge sürümü, `generation_id` ile korunan hücre yazması, `dedupe_key` ve çit belirteçli
  kuyruk, sıra numaralı SSE, sunucu üretimli onay kartı.
- 4B için yeniden tasarlanan orta katman: araç yüzeyi küçülür, retrieval sunucunun ön adımı olur, araç çağrısı şemaya
  zorlanır, model yalnız madde kimliği seçer ve alıntıyı sunucu çeker, tablo incelemesi hücre başına küçük çağrıdır.
- Mike'ın kendi sessiz-yanlışlık tuzakları [`yurutme-tuzaklari.md`](yurutme-tuzaklari.md) ile aynı sınıftan:
  doğrulama bayrağı boş atıf "doğrulandı" görünüyor; bozuk JSON'da ham metnin ilk 500 karakteri `done` hücre olarak
  yazılıyor; bozuk araç argümanı sessizce `{}` oluyor.
- Türkçe kusurları: `toLowerCase` ile `İ` iki karakter olup konum haritasını kaydırıyor; `İ`/`ı` eşleşmiyor;
  noktalama silme "1.500" ile "15,00"ı aynı yapıyor; ön yüz vurgulayıcı ç ğ ı ö ş ü harflerini siliyor. Biri Node ile
  doğrulandı, kalanı koddan çıkarım.

**2 · ADR-0104 ve aynı gün düzeltmeleri.** Kararın çekirdeği: uygulama iki makalenin de çıktısı değil, ürün hattı;
çakışmada kağıt hattı kazanır · llama.cpp + OpenAI-uyumlu tek uç nokta · `apps/api` + `apps/web` +
`packages/contracts`, Turborepo yok · içtihat Dilim D'ye ertelendi · model Checkpoint 1'in kazananı. İlk taslak üç
kusurla yazıldı ve aynı gün düzeltildi:

- [ADR-0076](../adr/kararlar-0064-0085.md#adr-0076)'yı ve `hakhukuk/cekirdek/araclar.py`'deki beş aracı yok saydı:
  İngilizce araç adları, tek `article_id`, araç kullanımının eğitimi "açık soru" (`2993aaf`).
- `YAYIN_YOL_HARITASI.md`'yi güncellemedi; kullanıcı sordu (`272e106`).
- Numara çakışması: karar ayrı çalışma kopyasında 0103 diye yazıldı; ana çalışma kopyasında başka bir oturum 0102 ve
  0103'ü commit'lemeden almıştı. Birleştirmede 0104 oldu (`a55ff9f`, `a92f677`); diğer oturumun dosyaları ve karar
  metni bayt bayt korundu.

**3 · Denetim (ADR-0105).** Kullanıcı kararları aynı gün denetime açtı. Bulunanlar:

| bulgu | nerede |
| :--- | :--- |
| araç kullanımının eğitimi için üç belge üç ayrı yer gösteriyor: GRPO ödülü · hiçbir yer · "Checkpoint 2'den sonra" | `PRODUCT.md` v2 · `YAYIN_YOL_HARITASI.md` §3.2 · `ROADMAP_uygulama.md` |
| `ROADMAP_uygulama.md`'nin göndermesi var olmayan bir satıra çıkıyor: `ROADMAP_v1.md` §9'da araç eğitimi satırı yoktu | bağlantı testi yakalamaz; dosya vardı, satır yoktu |
| omurganın takvim gerekçesi ("GRPO koşarken kullanıcı saati görece boş") yol haritasının kendi tablosuyla çelişiyor: Ağustos–Eylül 2027 F5'tir, Makale 1'in yazımı (~30-45 saat) | ADR-0104 Gerekçe ↔ `YAYIN_YOL_HARITASI.md` §2.6 |
| F1.12'nin "F1.11'den önce" şartının gerekçesi yok; planın en yoğun dönemine düşüyor ve F1'in saat tahminine girmemiş | `ROADMAP_v1.md` F1.12 |
| uygulama hattının hiçbir yerde kullanıcı saati tahmini yok | `ROADMAP_uygulama.md` |

Kararlar: araç kullanımının eğitimi Makale 2'ye girmez, Checkpoint 2'den sonra ayrı ürün turu (yalnız ölçüm boşluk
gösterirse) · omurga Ekim–Aralık 2027 · dilimler sıralı, tez yazımında durur · F1.12 `ROADMAP_v1`'den çıktı,
omurganın ilk işi oldu (U1.0, kazananla) · uygulamanın tezdeki yeri Ocak 2028'de. Yol haritalarına işlendi
(`40c1ce8`); `YAYIN_YOL_HARITASI.md` §5–§7 tabloları aynı gün açılır kapanır yapıldı (`f5ec8b1`).

**Okuma:** bu turda hiçbir sayı ölçülmedi; tasarımın 4B'de çalıştığına dair kanıt yok, Mike'tan çıkan her şey
öneridir. Karar kaydının kendisi de "hata vermeden yanlış" üretebiliyor: üç belge aynı soruya üç cevap verdi ve
bağlantı testi geçti, çünkü test bağlantının varlığına bakar, ne dediğine bakmaz. Bir ADR'nin gerekçe cümlesi, yol
haritasının saat tablosuyla yan yana okunmadan yazılmıştı. İki ders: yeni ADR'den önce konuyla ilgili eski ADR'ler
taranır (ADR-0076 kaçırıldı); paralel oturumlarda numara commit'li hâlden değil ana çalışma kopyasından alınır. ADR
numarası gibi kronoloji numarası da commit'lenmeden alınıyor; bu girdi bu yüzden #84 (#81–#83 diğer oturumun,
2026-10-15'te henüz commit'lenmemişti). Taramanın sentezindeki araç listesi (`mevzuat_ara` … `madde_id`) ve
"araç çağırma dalı F1.11 dondurmasını etkiler" maddesi ADR-0104 ve ADR-0105 ile aşıldı;
`knowledge/mike-tarama/` o günün hâliyle kalır.

<a id="85"></a>
## #85 — F0.6: hakem geçişi; DeepSeek V4.1 Flash `gpt-4o-mini`'den 8-11,5 p sert; aynı cevaplarda tek hakem koşusu ~1 p oynuyor, kayıttaki 0,3 tabanının 3-4 katı

**2026-10-15 · OpenRouter · hakemler: `deepseek/deepseek-v4.1-flash-20260910` (sağlayıcı `deepinfra/fp8` sabit,
yedeğe düşme kapalı; hakemin kendi düşünmesi açık ve kapalı) ve `openai/gpt-4o-mini` (sağlayıcı OpenAI) · kullanıcı
onayı: puanlama "Başlat", mod başına +3 tekrar "Başlat"; gürültü kuralı "şimdi işaretle, F1.4'te karar"
(2026-10-15)** · girdi: F0.16'nın A10 referansı
`outputs/eval/f0/f016-pilot/A10/m1/h1_tgta_v1_A10_m1_t1_detail.jsonl` (sha256 `c5035eb3…bb7cd093`; `tgta_v1`, h1,
80 DEV kalemi, [#83](#83)) · kanıt: `outputs/eval/f0/f06-hakem-gecisi/` (`KUNYE.json` · `OZET.json` · 15 `gnd_*`
dosyası · `kos.sh`, `kos2.sh`, `ozetle.py`)

**1 · Koşu.** Plan her modda iki koşu öngörüyordu. İlk iki çiftte aynı hakemin iki koşusu 1,5-1,9 p ayrışınca iki
koşunun tabanı ölçmeye yetmeyeceği görüldü; kullanıcı mod başına üç tekrar daha onayladı. 15 koşu eş zamanlı,
aynı 80 cevap üzerinde. Hepsi 80/80, hakem hatası 0, `judge_providers` her koşuda tek eleman (DeepInfra ya da
OpenAI). Kapalı mod ve `gpt-4o-mini` koşu başına ~6 dk, açık mod ~1 sa 50 dk–2 sa.

**2 · Sonuçlar** (mod başına 5 koşu; ss = tek koşunun standart sapması):

| hakem | kütle ort. | ss | en uzak iki koşu | A1 ort. | ss | iddia / koşu | sıfır iddialı | $/koşu (tahmin) |
| :-- | --: | --: | --: | --: | --: | :-- | :-- | --: |
| `gpt-4o-mini` | 0,8320 | 1,06 p | 2,77 p | 0,8875 | 1,13 p | 261-264 | 2 | 0,040 |
| DeepSeek, kapalı | 0,7168 | 0,87 p | 1,86 p | 0,7646 | 0,93 p | 313-325 | 3-4 | 0,051 |
| DeepSeek, açık | 0,7515 | 0,26 p | 0,58 p | 0,8016 | 0,28 p | 318-348 | 3 | 0,258 |

Kapsama 15 koşunun 15'inde 0,9375: onu hakemsiz çekinme dedektörü belirliyor. Oynamanın tamamı A1'den. 80 kalemden
puanı en az bir koşuda değişen: `gpt-4o-mini` 10, kapalı 15, açık 18.

**3 · Hakem değişikliğinin etkisi.** Kütlede DeepSeek açık −8,05 p, kapalı −11,52 p (`gpt-4o-mini`'ye göre). Farklı
hakemle puanlanmış iki sayı aynı tabloya girmez.

**4 · Gürültü tabanı.** Aynı gün, aynı cevaplarda, tek bir hakem koşusunun oynaması `gpt-4o-mini`'de ~1,1 p,
kapalı DeepSeek'te ~0,9 p, açık DeepSeek'te ~0,3 p. Kütlede on koşu çiftinin farkları:

- `gpt-4o-mini`: 0,41 · 0,42 · 0,48 · 0,83 · 0,89 · 1,31 · 1,46 · 1,88 · 2,29 · 2,77 p
- kapalı: 0,06 · 0,17 · 0,28 · 0,34 · 1,35 · 1,41 · 1,52 · 1,58 · 1,69 · 1,86 p

Yalnız iki koşuya bakan biri 0,06 p de görebilirdi, 2,77 p de. Kayıttaki taban (~0,3 A1:
`CLAUDE.md`, `OLCUM.md`, `YENIDEN_URETIM.md`; `faith_macro` ±0,005: tuzak 2.8) iki koşudan ölçülmüştü; bugünkü
ölçümle çelişiyor. Altı yerde işaretlendi (bu girdiyle aynı gün): `CLAUDE.md`, `docs/OLCUM.md` (iki yer),
`docs/YENIDEN_URETIM.md`, `scripts/yeniden_uret.sh` (yalnız yorum, eşik ve davranış aynı) ve tuzak 2.8. Kural
(kaç tekrar, hangi eşik) F1.4'te bağlayıcı hakem moduyla birlikte konur (kullanıcı kararı). `faithfulness_macro`
çekinme kalemlerini de içerdiği için açık modda A1'den fazla oynuyor (ss 0,78 p ↔ 0,28 p); bağlayıcı eksenler
A1 ve kütle.

**5 · #76'nın "bir ay arayla" farkı.** f02'nin cevaplarında 2026-09-06 ↔ 2026-10-11: A1 −1,86 p,
`faithfulness_macro` 0,8499 → 0,8314 ([#76](#76)). Bugün aynı gün, aynı cevaplarda `gpt-4o-mini`'nin aralığı A1'de
2,95 p, `faithfulness_macro`'da 2,84 p. Bu yüzden o fark gürültüden ayırt edilemiyor. ADR-0103 m.2'nin "hakem
kayması" adı desteklenmiyor; ADR'ye not düşüldü.

**6 · Maliyet.** Tahmin $1,75 (açık $1,29 · kapalı $0,25 · `gpt-4o-mini` $0,20). Tahmin `llm_client.PRICE`'tan
yapıldı; önbellekli girdi indirimi ve OpenRouter marjı hariç. **Fatura $1,23**: OpenRouter, bu anahtarın
2026-10-15 (UTC) kullanımı, `GET /api/v1/key`, okundu 18:27 UTC. Haftalık kullanım da aynı, yani bu hafta bu
anahtarla başka harcama yok. Açık modun ön tahmini (koşu başına $0,08-0,18, F0.6 maliyet kutusu) tutmadı:
$0,26. Hakem varsayılandan çok düşünce token'ı harcıyor.

**7 · Kod.** Yeni kod yok. `llm_client.py`'deki "F0.6'da doğrulanır" uyarısı "doğrulandı" oldu;
`yeniden_uret.sh`'a yorum eklendi. Hızlı takım 523 geçti, 0 kaldı.

**Okuma:** kiralık kartta üretim sabit ([#83](#83)) olduğundan bundan sonra koşudan koşuya oynamanın tek kaynağı
hakem. Hakemsiz eksenler (kapsama, çekinme) hiç oynamadı. Hakemli eksen tek koşuda ~1 p oynuyor. Gürültüyü
azaltmanın en ucuz yolu hakemi tekrarlamak: kapalı modda koşu başına $0,05, 80 cevabın üretimi ~$0,19
([#83](#83)). Açık düşünmeli DeepSeek en az oynayan hakem; koşu başına 5 kat pahalı ve ~20 kat yavaş. Bağlayıcı
modun seçimi (F1.4) için veri hazır.

**Ders.** *Gürültü tabanı tek çiftle ölçülmez.* Bütün yorum eşiği (0,3) iki koşudan geliyordu. Aynı hakemin
on çiftinden biri 0,06 p, biri 2,77 p gösterdi. #76'da "bir ay arayla" diye okunan fark da bu oynamanın
içinde kalıyor.

<a id="86"></a>
## #86 — vLLM pilotu: aynı Q4 ağırlığıyla vLLM, llama.cpp'yle aynı puanı veriyor (0,18 p) ve 4-5 kat hızlı; orijinal bf16 4,8 p düşük; hasat kapısı %69,2 ile geçmedi

**2026-10-15/16 · Modal A10 (hesap `rfetha`), vLLM 0.30.0 · hakem `deepseek/deepseek-v4.1-flash-20260910`, `deepinfra/fp8`,
hakemin düşünmesi açık · kullanıcı onayları: bf16 yükleme "Yükle", aşama A ve B "Başlat", puanlama "8 parça", hasat eşiği "%70"
(ölçümden önce); karar "seçim ölçümleri Q4'ten açılmış ağırlıkla" (2026-10-16) · plan `2026-10-15-vllm-gecis.md`
([ADR-0106](../adr/kararlar-0064-0085.md#adr-0106)), karar [ADR-0107](../adr/kararlar-0064-0085.md#adr-0107), kart #11** · kanıt:
`outputs/eval/f0/f016-vllm-pilot/` (`KUNYE.json` · `OZET.json` · `HASAT_ORTUSME.json` · `kontrol-eklenti/` · `cevirme/` ·
`kontrol-bf16-orijinal/` · `A10/` · `puanlama/`)

**1 · Soru.** A10'da llama.cpp ile 80 DEV cevabı 640,6 s sürüyor, istekler tek tek ([#83](#83)). vLLM toplu üretimle bu süreyi
kısaltır mı, puanı kaydırır mı? İlke (kullanıcı): araç seçimi iş başınadır; bir iş vLLM'e yalnız kapıyı geçerse taşınır.

**2 · GGUF eklentisi açamadı.** vLLM'in GGUF desteği ayrı bir eklentiye taşınmış (`vllm-gguf-plugin` 0.0.5). Yayımlanmış Q4_K_M
ile iki yapılandırma da düştü: `RuntimeError: Unknown gguf model_type: qwen3_5` (metin-yalnızda `qwen3_5_text`); eklenti
mimariyi gguf'taki `qwen35` adıyla eşleyemiyor (`kontrol-eklenti/`, ~$0,1).

**3 · Çeviri.** `scripts/olcum_uretim/gguf_hf_cevir.py` GGUF'u bf16 HF biçimine açar ve llama.cpp'nin dönüşümlerini geri alır:
norm ağırlıklarına eklenen +1, doğrusal dikkat (GDN) katmanlarında 32 değer başının "döşemeli" dizilişi, `ssm_a = -exp(A_log)`.
Her tensör orijinal (sıkıştırılmamış) ağırlıkla karşılaştırıldı: 426 tensör, göreli hata F32 0,0000 · Q4_K 0,0715-0,0790 ·
Q6_K 0,0179-0,0193; MTP katmanı (15 tensör) açıkça atlandı (`cevirme/CEVIRI_KUNYE.json`). Diziliş geri çevrilmeden doğrusal
dikkat tensörlerinde hata %90-136'ydı: yanlış diziliş hata vermez, modeli bozar.

**4 · Aşama A (orijinal bf16, 8 soru).** Açıldı; düşünce `reasoning` alanında dönüyor (`toplu_uret.py` eşliyor). Tek tek
148,9 s (49 token/s; llama.cpp Q4'te 105), 8'i aynı anda 34,8 s (206 token/s). Tek tek ↔ toplu cevaplardan **2/8 aynı**;
toplu koşuda 2/8 cevap bütçeye çarptı.

**5 · Aşama B (80 soru × 2 toplu koşu, 32 eş zamanlı).**

| | Q4'ten açılmış (vLLM) | orijinal bf16 (vLLM) | llama.cpp Q4 (referans) |
| :-- | --: | --: | --: |
| 80 cevap süresi | 130,3 · 129,5 s | 158,0 · 155,9 s | 640,6 s |
| cevap başına (Modal $1,10/sa) | $0,0005 | $0,0006 | $0,0024 |
| kesik | 4/80 · 1/80 | 3/80 · 1/80 | 0/80 |
| zorla kapatılan düşünce | 5 · 6 | 20 · 17 | 4 |
| ortalama token (düşünce dahil) | 807 | 1027 | 747 |
| iki toplu koşu arasında aynı cevap | 25/80 | 19/80 | 80/80 |
| llama.cpp cevabıyla aynı | 11/80 (benzerlik medyanı 0,688) | 2/80 (0,450) | — |

**6 · Puanlama.** Her ağırlığın 1. koşusu, 3 hakem tekrarı; her tekrar 8 parçaya bölündü (48 süreç, 18 dk; kullanıcı kararı,
`kos-parcali.sh`, `birlestir.py`); 480 kalem, hakem hatası 0, tamlık kapısı geçti. Referans: F0.6'da aynı hakemin aynı
cevaplara 5 tekrarı ([#85](#85)).

| | kütle ort. | tekrarlar | ss | A1 | kapsama |
| :-- | --: | :-- | --: | --: | --: |
| llama.cpp Q4 (referans) | 0,7515 | 5 tekrar | 0,26 p | 0,8016 | 0,9375 |
| vLLM, Q4'ten açılmış | 0,7496 | 0,7510 · 0,7511 · 0,7468 | 0,25 p | 0,7891 | 0,95 |
| vLLM, orijinal bf16 | 0,7017 | 0,6974 · 0,7048 · 0,7029 | 0,38 p | 0,7386 | 0,95 |

**7 · Kapılar** (spec bölüm 5; ölçütler pilottan önce kilitli; `OZET.json`):

| kapı | ölçüt | değer | sonuç |
| :-- | :-- | :-- | :-- |
| G1 geçerlilik | n=80, kesik ≤ %5, düşünce kanalı kullanılmış | 4 koşu geçerli (Q4 t1 kesik tam %5,0) | geçti |
| G2 hız | 80 cevap ≤ 640,6 s ÷ 3 = 213,5 s | 129,9 s · 157,0 s | geçti |
| G3 motor etkisi | ≤ 0,6 puan | 0,18 puan | geçti |
| G4 belirlenimcilik | bilgi | 2/8 | dal: puan düzeyi |
| G5 Q4 etkisi | yalnız rapor | orijinal bf16, Q4'ten 4,79 puan düşük | — |

**8 · Hasat kapısı.** Eşik ölçümden önce kullanıcıyla %70 kondu: llama.cpp Q4'ün yanlış yaptığı kalemlerin (tekrar ortalaması
faithfulness < 0,5) vLLM'de, aynı Q4 ağırlığıyla, de yanlış olma oranı. Ölçülen: llama.cpp 13 yanlış, vLLM 16, ortak 9 →
**9/13 = %69,2, geçmedi** (`HASAT_ORTUSME.json`). Ayrışan 11 kalemden yalnız 2'si 0,5'e 0,15'ten yakın; fark bir kalemlik şans
değil. Yalnız-vLLM hatalarının çoğu net (llama.cpp 1,0 ↔ vLLM 0,0-0,3: id 30, 34, 37, 32).

**9 · Kararlar (kullanıcı, [ADR-0107](../adr/kararlar-0064-0085.md#adr-0107)).** Seçim ölçümleri vLLM'de Q4'ten açılmış ağırlıkla (spec'teki
"bf16'da seç" değişti); nihai sayı llama.cpp Q4'te; vLLM hattında makine kapısı puan düzeyinde (`makine_kapisi_puan.py`);
hasat llama.cpp'de kalır.

**10 · Maliyet.** Tahmin: eklenti denemesi ~$0,1 · aşama A ~$0,17 · aşama B ~$0,37 · puanlama $1,58 (liste fiyatı) → ~$2,2
(sınır $5). Fatura: OpenRouter'ın kullanım sayacı 2026-10-16T10:24Z'de bugünü henüz göstermiyordu; Modal panelden okunmadı.

**Okuma:** motor, aynı ağırlıkla ortalama puanı değiştirmiyor ama cevapları değiştiriyor: iki motor arasında 80'de 11 cevap
aynı, hataların düştüğü kalemler %31 farklı. vLLM bu yüzden seçim ölçümüne uygun, kalem düzeyinde hata toplayan hasada değil.
Sıkıştırma da yalnız sayıları değil davranışı değiştiriyor: orijinal bf16 %27 daha uzun düşünüyor, 4 kat daha sık bütçeye
takılıyor ve 4,8 puan düşük alıyor. Doğrulanmamış: bu farkın ne kadarı ağırlıktan, ne kadarı yapılandırmadan geliyor (bf16 tam
görsel yapılandırmayla, Q4 metin-yalnız yapılandırmayla açıldı).

**Ders.** *Sıkıştırılmış model, sıkıştırılmamış atasının bir yaklaşığı değil, kendine ait bir model.* bf16'da seçilen kol Q4'te
kazanmayabilir; ölçüm gönderilen ağırlıkta yapılmalı. "Aynı ortalama puan" da "aynı hatalar" demek değil.

**Not (2026-10-16, [#87](kronoloji-87-98.md#87)):** G3'ün 0,18 puanı tek üretim çekilişiydi. Beş koşuda aynı Q4 ağırlığı vLLM'de 3,59 puan düşük
ve koşudan koşuya ±2,25 puan çıktı; vLLM ölçüme alınmadı ([ADR-0109](../adr/kararlar-0064-0085.md#adr-0109)).
