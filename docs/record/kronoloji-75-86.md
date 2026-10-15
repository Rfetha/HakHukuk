# Araştırma kaydı — #75 …

> **Ne bu:** Checkpoint 1'in F0 aşaması (2026-10-11'den). Önceki dosya
> [`kronoloji-63-71.md`](kronoloji-63-71.md) 12 girdiye ulaştı (#63-#74); kural
> [`README.md`](README.md)'de. Çapa: `kronoloji-75-86.md#75`. **Yeni girdi #80'den devam eder.**

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
`google/gemma-4-E4B-it@ee0ef6023621` · kapının kodu `778fc33` · Kanıt: bu girdi (komutlar aşağıda)

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

**Okuma:** [`YAYIN_YOL_HARITASI.md`](../YAYIN_YOL_HARITASI.md) §2.4'ün "paket kilidi" maddesi ve
[`EGITIM_ORTAMI.md`](../EGITIM_ORTAMI.md) §6 m.6'nın öngördüğü durum gerçekleşti: Gemma, Qwen'in
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

<a id="84"></a>
## #84 — Ajan uygulaması hattı: Mike taraması, ADR-0104 ve aynı gün denetimi (ADR-0105); ölçüm yok

**2026-10-15 · ölçüm yok, GPU yok, $0 · kullanıcı kararları
([ADR-0104](../adr/kararlar-0064-0085.md#adr-0104), [ADR-0105](../adr/kararlar-0064-0085.md#adr-0105))** · kanıt:
[`knowledge/mike-tarama/`](../../knowledge/mike-tarama/README.md) (sekiz dosya + sentez, 2.351 satır) · commit'ler
`e314613` … `aa5fd19` (`talk-think`)

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
  İngilizce araç adları, tek `article_id`, araç kullanımının eğitimi "açık soru" (`cd158c1`).
- `YAYIN_YOL_HARITASI.md`'yi güncellemedi; kullanıcı sordu (`6452276`).
- Numara çakışması: karar ayrı çalışma kopyasında 0103 diye yazıldı; ana çalışma kopyasında başka bir oturum 0102 ve
  0103'ü commit'lemeden almıştı. Birleştirmede 0104 oldu (`b6919fc`, `886fd6c`); diğer oturumun dosyaları ve karar
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
(`aa5fd19`); `YAYIN_YOL_HARITASI.md` §5–§7 tabloları aynı gün açılır kapanır yapıldı (`80ad755`).

**Okuma:** bu turda hiçbir sayı ölçülmedi; tasarımın 4B'de çalıştığına dair kanıt yok, Mike'tan çıkan her şey
öneridir. Karar kaydının kendisi de "hata vermeden yanlış" üretebiliyor: üç belge aynı soruya üç cevap verdi ve
bağlantı testi geçti, çünkü test bağlantının varlığına bakar, ne dediğine bakmaz. Bir ADR'nin gerekçe cümlesi, yol
haritasının saat tablosuyla yan yana okunmadan yazılmıştı. İki ders: yeni ADR'den önce konuyla ilgili eski ADR'ler
taranır (ADR-0076 kaçırıldı); paralel oturumlarda numara commit'li hâlden değil ana çalışma kopyasından alınır. ADR
numarası gibi kronoloji numarası da commit'lenmeden alınıyor; bu girdi bu yüzden #84 (#81–#83 diğer oturumun,
2026-10-15'te henüz commit'lenmemişti). Taramanın sentezindeki araç listesi (`mevzuat_ara` … `madde_id`) ve
"araç çağırma dalı F1.11 dondurmasını etkiler" maddesi ADR-0104 ve ADR-0105 ile aşıldı;
`knowledge/mike-tarama/` o günün hâliyle kalır.
