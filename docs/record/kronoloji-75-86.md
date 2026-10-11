# Araştırma kaydı — #75 …

> **Ne bu:** Checkpoint 1'in F0 aşaması (2026-10-11'den). Önceki dosya
> [`kronoloji-63-71.md`](kronoloji-63-71.md) 12 girdiye ulaştı (#63-#74); kural
> [`README.md`](README.md)'de. Çapa: `kronoloji-75-86.md#75`. **Yeni girdi #78'den devam eder.**

| # | tarih | başlık | kanca |
| :-- | :--- | :--- | :--- |
| [75](#75) | 2026-10-11 | F0.4: yeni eğitim kilidi eski ortamla eşdeğer | en büyük sapma 0,0032 · gürültü ≤ 0,0021 · 15 dk boşta A100 sızıntısı kapandı |
| [76](#76) | 2026-10-11 | F0.5 (b) ve F0.6'nın kodu: RQ2 anahtarları | hakemsiz çıpaların hepsi birebir · `gpt-4o-mini` aynı istekte bir ayda −1,75 p kütle |
| [77](#77) | 2026-10-11 | F0.7: ham TIES'te τ_a'nın %32'si taşınıyor | τ_a'yı ezen seyreklik değil, normların 9 kat farkı |

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
