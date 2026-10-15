# Eğitim ortamı kilidi

> **Bu belge ne:** Makale 1 ve Makale 2 için yapılacak **her** eğitim koşusunun (Modal ya da ~~Vast~~ RunPod, [ADR-0101](adr/kararlar-0064-0085.md#adr-0101))
> uymak zorunda olduğu donanım, yazılım ve tarif değerleri. Amaç: platform değişse bile kolların
> aynı ortamda eğitilmiş olması — aksi hâlde kollar arası fark "yöntem mi, ortam mı" diye
> ayrıştırılamaz. Yol haritası: [`YAYIN_YOL_HARITASI.md`](YAYIN_YOL_HARITASI.md) §4.1.
>
> **DURUM (2026-10-11): kilit kodda ve eski ortamla eşdeğer ([#75](record/kronoloji-75-86.md#75)).** Depo bunu iki kez öğrendi: kapıyı
> belgeye değil koda koy ([ADR-0030](adr/kararlar-0027-0044.md#adr-0030) m.3); `llama-server`
> bayrakları üç belgede düz metin olarak yazılıydı ve "hiçbiri kapı değildi"
> ([ADR-0078](adr/kararlar-0064-0085.md#adr-0078)). Kilit üç parçadır ve üçü de yazıldı
> ([#74](record/kronoloji-63-71.md#74)); eski ortamla eşdeğerliği F0.4'ün Modal koşuları ölçtü (§6 m.1).

## 1 · Üç parça

| parça | ne | durum |
| :--- | :--- | :--- |
| `docs/EGITIM_ORTAMI.md` | insan için: ne kilitli, neden, platform değişince ne yapılır | **bu belge** |
| `configs/egitim_ortami.yaml` | aynı değerlerin makine okunur **tek kaynağı** | yazıldı (2026-10-11) |
| betik başı kontrolü + test | `train_sft.py` ve `train_orpo.py` **model yüklenmeden önce** yaml'ı okur; GPU mimarisi, paket sürümleri, `fla-core`'un gerçekten içe aktarılabilmesi ve hassasiyetin **açıkça** verilmiş olması doğrulanır; uymazsa koşu para harcamadan durur; gerçek değerler künyeye yazılır. Bir test, kontrolün betiklerde durduğunu sınar (`tests/test_konteyner.py`'nin eğitim tarafındaki eşi) | yazıldı (2026-10-11): `scripts/egitim/ortam_kilidi.py` · `tests/test_egitim_ortami.py` |

Bu belge ile yaml çelişirse **yaml bağlayıcıdır** ve belge düzeltilir.

## 2 · Kilitli değerler

| alan | değer | kaynak / durum |
| :--- | :--- | :--- |
| GPU | **NVIDIA A100**, compute capability 8.0; 40 GB ya da 80 GB; gerçek model künyeye yazılır | Makale 1 kollarında RTX 5090 ve H100 **yasak** (farklı mimari kollar arasına değişken sokar) |
| Modal kart dizesi | `A100-40GB`, **açıkça** | yalnız `"A100"` yazılırsa 40 ya da 80 GB gelebilir (tuzak 6.7, [#48](record/kronoloji-39-52.md#48)) |
| Python | 3.11 | `scripts/egitim/modal_train.py:50` |
| paketler | `requirements.lock.txt`, `sha256 6b5209e6a293f3c72f5d6c1dfa64591128f48dd8e3c0e07cdc3141c733c6ebb0` — torch 2.10.0 · triton 3.6.0 · transformers 5.10.2 · peft 0.19.1 · trl 0.24.0 · unsloth 2026.6.1 · unsloth_zoo 2026.6.1 · accelerate 1.13.0 · bitsandbytes 0.49.2 · datasets 4.3.0; kurulum `--no-deps` | dosyadan okundu, 2026-10-10 |
| `einops` · `fla-core` · `flash-linear-attention` | **einops 0.8.2 · fla-core 0.5.1 · flash-linear-attention 0.5.1**; kurulum `--no-deps`, sürümler yaml'dan | 2026-10-11: Modal'daki önbellekli imaj katmanından okundu (kurulum 2026-07-25 06:03 UTC; τ_g ve τ_a bu katmanla eğitildi, [#74](record/kronoloji-63-71.md#74)). Önceden **sürümsüz** kuruluyordu: imaj farklı günde kurulsaydı farklı sürüm gelirdi (fla 0.5.2 2026-07-27'de çıktı), hata vermezdi |
| `fla-core` | **zorunlu**; ölçüt `import fla` değil `from fla.modules import FusedRMSNormGated` | eksikliği fla'nın hiç olmamasından kötü ([ADR-0033](adr/kararlar-0027-0044.md#adr-0033)) |
| `causal-conv1d` | **yok** | tavanı 1,254× ölçüldü, ≥2× kapısından kaldı ([#44](record/kronoloji-39-52.md#44)) |
| hassasiyet | **açıkça verilir, varsayılan YOK.** Değer **bf16 taban + LoRA**: τ_g v1 için belge kanıtı bu (eski geçmişte koşu komutu `9f4b43d`, rejim eşleşmesi `64073b4`, `b995182`'de de duruyor; künye yok), τ_a künyeli. Bütün kollar aynı rejimde | bugün betikler bayraksız çağrılınca **sessizce 4-bit NF4**'e düşüyor (§3) |
| LoRA | r=16 · α=32 · dropout 0,05 · `use_rslora=False` · hedef modüller: `q_proj k_proj v_proj o_proj in_proj_qkv in_proj_z in_proj_a in_proj_b gate_proj up_proj down_proj` (11) | `outputs/tg_v1` ve `outputs/ta_v1` `adapter_config.json` dosyalarında birebir doğrulandı |
| SFT tarifi | veri `data/train/raft_scrubbed/` (17.323 satır) · 2048 token · cihaz başı batch 2 × biriktirme 8 · gradient checkpointing **kapalı** · lr 1e-4 cosine · `adamw_8bit` · 1 epoch = 1.083 adım · packing **yok** | [ADR-0033](adr/kararlar-0027-0044.md#adr-0033), [#40](record/kronoloji-39-52.md#40) |
| ORPO tarifi | veri `data/train/orpo_abstain_cp2c/` (845 satır = 726 çift + 145 tekrar; 26 doğrulama) · lr 1e-5 · beta 0,1 · biriktirme 64 · 5 epoch = 70 adım · **taze adaptör** (`--fresh-adapter`) | [#48](record/kronoloji-39-52.md#48), [`kollar.md`](record/kollar.md) |
| ısınma (warmup) | iki tarifte de 0,05 | τ_g komutu (`9f4b43d:docs/record/sprint1/NEXT-SESSION.md:63`) · `train_orpo.py` varsayılanı; 2026-10-11'de yaml'a yazılırken eklendi |
| ORPO uzunlukları ve bellek | `max_length` 2048 · `max_prompt_length` 1536 · gradient checkpointing **açık** (`train_orpo.py`'de koda gömülü, `"unsloth"`) | `train_orpo.py` varsayılanları; τ_a'nın koşu satırı bunları değiştirmiyor (#48) |
| SFT sistem istemi | **yok** (`--no-system`): veri sistem istemini taşımıyor, betik eklemez | τ_g komutu (`9f4b43d:…NEXT-SESSION.md:62`) |
| birlikte-eğitim tarifi | SFT tarifi (lr 1e-4) + ORPO çiftleri aynı koşuda; çiftlerde tam ORPO kaybı, λ 0,1 / 0,3; çiftler 5 epoch (örneklerin ~%20'si) | F0/F1 sorgulaması, 2026-10-10; kod F0.8'de |
| ardışık tarif | τ_g tabana bf16'da gömülür; ORPO tarifi taze adaptörle, β 0,1 / 0,3 | aynı |
| seed | **3407 · 3408 · 3409**, iki temel modelde (Qwen3.5-4B, Gemma 4 E4B) aynı liste. Qwen'de 3407'nin τ_g ve τ_a kolları `v1` adaptörleridir | sonuç görülmeden seçildi; yaml'a yazılınca kesinleşir |
| GPU üzerinde yalnız eğitim | ölçüm, hakem ve API anahtarları **eğitim makinesine gitmez** | ~~Vast için zorunlu~~ Modal dışı platformda (RunPod) zorunlu, [ADR-0101](adr/kararlar-0064-0085.md#adr-0101) |

## 3 · Bilinen sessiz tehlikeler

| tehlike | nerede | karşılık |
| :--- | :--- | :--- |
| `--bf16-base` verilmezse **sessizce QLoRA (NF4)** | `train_sft.py:173-180` · `train_orpo.py:164-172` · Modal'da `bf16_base = False` (`modal_train.py:440`) | hassasiyet zorunlu argüman olur ([ADR-0026](adr/gemma4-12b-dersler.md#adr-0026) ilkesi) → **kapandı 2026-10-11:** `--hassasiyet {bf16-taban,nf4}` zorunlu ve varsayılansız, `--bf16-base` kaldırıldı; Modal zinciri de zorunlu tutuyor |
| `--target-modules` verilmezse `in_proj_*` düşer, 24 linear-attention katmanı LoRA'sız kalır | [#40](record/kronoloji-39-52.md#40) | hedef modül listesi yaml'dan gelir, sayısı (11) kontrol edilir |
| `--data` konteyner yolu ↔ yerel yol karışıyor | [#40](record/kronoloji-39-52.md#40), [#48](record/kronoloji-39-52.md#48) | veri kapısı model yüklemesinden önce; satır sayısı künyeye |
| `--batch` ve `--grad-accum` ayrı verilip çarpım sessizce kayıyor | [ADR-0033](adr/kararlar-0027-0044.md#adr-0033) | etkin batch yaml'da; çarpım kontrol edilir |
| `lora_dropout=0.0` Python'da falsy, bayrak sessizce yok sayılıyor | [ADR-0033](adr/kararlar-0027-0044.md#adr-0033) | değer yaml'dan, eşitlikle kontrol |
| `causal-conv1d` yokken "fast path not available" uyarısı | [ADR-0033](adr/kararlar-0027-0044.md#adr-0033) | uyarı ölçüt değildir; ölçüt `s/adım` |

## 4 · Hesaplar ve platform değişimi

1. **İki Modal hesabı** (2026-10-10) aynı imajla aynı `A100-40GB`'ı kullanır; **aynı platform** sayılır, aralarında
   eşdeğerlik kontrolü gerekmez. Künyeye hangi hesap olduğu yazılır; adaptör, koşu biter bitmez özel
   HF deposuna kopyalanır — hiçbir artefakt yalnız bir hesabın depolama alanında kalmaz.
   **2026-10-14 ([ADR-0101](adr/kararlar-0064-0085.md#adr-0101) m.4):** bir koşu başladığı hesapta biter (checkpoint'ler o hesabın volume'ünde
   durur, öbür hesap göremez); hesap yalnız iki koşu arasında değişir. Hesap künyeye başlatıcıdan
   kendiliğinden yazılır (`MODAL_HESAP`); o güne kadar künyeye hiç yazılmıyordu.
2. **Kredi yetmezse:** iş takvimi geciktirmeden bekleyebiliyorsa yeni ayın kredisi beklenir ($0);
   ~~geciktirecekse Modal'da ödenir. **Vast yalnız Modal kesintisinde** kullanılır.~~ **2026-10-14'te
   değişti ([ADR-0101](adr/kararlar-0064-0085.md#adr-0101)):** geciktirecekse iş **RunPod**'da koşulur; Modal kesintisinde de yedek RunPod'dur,
   Vast eğitimden çıktı. Ölçüm kartının kuralı ayrıdır: [ADR-0097](adr/kararlar-0064-0085.md#adr-0097).
3. **Aynı imaj:** ~~Modal hesaplarına ve Vast'a aynı Docker imajı, aynı özetle (digest) verilir; imaj F0'da
   `requirements.lock.txt` + sabitlenmiş `fla-core` sürümüyle bir kez kurulur.~~ **2026-10-11'de değişti
   ([ADR-0099](adr/kararlar-0064-0085.md#adr-0099)):** Modal hesapları Modal'ın kendi imajını kullanır
   (`modal_train.py`, sürümlerin tamamı kilitten); her koşunun künyesine imaj kimliği ve kurulu bütün paket
   sürümleri yazılır. İmajın bir kayıt deposuna (registry) itilmesi, ~~Vast gerçekten gerektiğinde (yalnız
   Modal kesintisinde, m.2)~~ RunPod gerçekten gerektiğinde (m.2, [ADR-0101](adr/kararlar-0064-0085.md#adr-0101)) o gün yapılır.
4. **Yalnız A100**, **blok sınırında:** bir koşu asla iki platforma bölünmez ve platform **yöntemle
   değil seed'le** değişir — bir temel modelin bir seed'ine ait bütün kollar (τ_g, τ_a, birlikte,
   ardışık) aynı platformdadır; aksi hâlde birincil karşılaştırmada yöntem farkı platform farkından
   ayrılamaz. τ_g ve τ_a seed'leri dondurmadan önce Modal'da eğitildiği için Checkpoint 1'de ~~Vast'a~~
   RunPod'a ([ADR-0101](adr/kararlar-0064-0085.md#adr-0101)) ancak yepyeni bir seed bloğu geçebilir.
5. **Eşdeğerlik kontrolü** (~$1): Modal'da koşulmuş bir yapılandırmanın ilk 50 adımı ~~Vast'ta~~
   RunPod'da ([ADR-0101](adr/kararlar-0064-0085.md#adr-0101)) aynı seed'le tekrarlanır, kayıp eğrileri kıyaslanır. **Tolerans sayısı uydurulmaz:** F0'da aynı
   platformda aynı seed'le iki kısa koşu yapılır (~$1-2), aradaki fark **gürültü tabanıdır**;
   platformlar arası fark bu tabanın içinde kalmalı. Kalmazsa o blok tamamen tek platformda
   yeniden koşulur. (Emsal: batch değişince adım-10 kaybı 0,788 ↔ 0,7987 ölçülmüştü,
   [ADR-0033](adr/kararlar-0027-0044.md#adr-0033).)
6. **~~Vast~~ RunPod kuralları ([ADR-0101](adr/kararlar-0064-0085.md#adr-0101)):** API anahtarı kiralık makineye gitmez (yalnız yedek deposuna
   yazabilen HF token) · koşu bitince pod **silinir** (depolama, pod silinene kadar faturalanır) ·
   network volume durdurulmuş pod'da da faturalanır, adaptör yedek deposuna kopyalanınca silinir ·
   kesilebilir kiralamada `save_steps` + otomatik devam ([ADR-0008](adr/gemma4-12b-dersler.md#adr-0008)) ·
   künyenin platform alanı `RUNPOD_*` değişkenlerinden yazılır (kod geçiş günü eklenir).
7. Makalenin ekine **donanım tablosu**: hangi kol nerede (platform ve hesap) eğitildi.

## 5 · Her koşunun künyesine yazılacaklar

gerçek GPU adı ve belleği (`nvidia-smi`) · sürücü ve CUDA sürümü · imaj özeti · bütün paket
sürümleri (`importlib.metadata`) · `requirements.lock.txt` özeti · hassasiyet · LoRA ayarları ve
hedef modüller · veri yolu, satır sayısı ve `sha256` · seed · adım sayısı · etkin batch · platform ve hesap.
Künyedeki her alan **ya bir değişkenden ya bir ölçümden** gelir; elle yazılmış alan künyeyi kanıt
olmaktan çıkarır (tuzak 1.12, [#66](record/kronoloji-63-71.md#66)).

## 6 · F0'da doldurulacak açık maddeler

1. ~~τ_g v1'in hassasiyeti~~ → belge kanıtı bulundu (2026-10-10, §2). Ölçüm kanıtı: yeni kilitte τ_g seed
   3407 ile 50 adım ([#40](record/kronoloji-39-52.md#40)'taki 0,7987 / 0,3537'den en çok ~0,02 sapma) ve
   ORPO ile 10 adım (`ta_v1/trainer_state-checkpoint70.json`); geçmezse Qwen'in 3407 kolları yeniden
   eğitilir. → **2026-10-11 geçti:** τ_g 10. adım 0,7992 / 0,7990, 50. adım 0,3545 / 0,3524; ORPO 5. adım
   2,6399 / 2,6395, 10. adım 2,4895 / 2,4874 — en büyük sapma 0,0032; 3407 kolları yeniden eğitilmedi
   (kullanıcı kararı, [#75](record/kronoloji-75-86.md#75)).
2. ~~`einops` · `fla-core` · `flash-linear-attention` sürümleri.~~ → 2026-10-11, §2.
3. ~~Docker imajı ve özeti; imajın CUDA sürümünün istediği en düşük sürücü.~~ → ADR-0099 ile değişti
   (§4 m.3): Modal'ın imaj kimliği ve sürücü sürümü (`nvidia-smi`) künyede.
4. ~~`configs/egitim_ortami.yaml` + betik başı kontrolü + test.~~ → 2026-10-11, §1.
5. ~~Gürültü tabanı ölçümü (§4.5).~~ → 2026-10-11: aynı seed'le iki koşu arasındaki kayıp farkı en çok
   0,0021 (τ_g 50. adım 0,0020 · ORPO 10. adım 0,0021); koşular dört ayrı veri merkezine ve iki sürücü
   sürümüne düştü ([#75](record/kronoloji-75-86.md#75)).
6. Gemma 4 E4B için ayrı bir bölüm. **Kilit ve kod yazıldı (2026-10-15); gerçek eğitim denenmedi** (F0.9
   smoke'u bunun için). Bulgular: [#78](record/kronoloji-75-86.md#78) ve [#79](record/kronoloji-75-86.md#79).
   - **Ayrı kilit, ayrı imaj:** `configs/egitim_ortami_gemma.yaml` + `requirements.gemma4.lock.txt` (Qwen'inkinden
     yalnız `unsloth` ve `unsloth_zoo` 2026.10.1 farklı; kilitteki 2026.6.1 Gemma 4 yapılandırmasını yüklemiyor).
     Qwen'in kilidine dokunulmadı. Tarifler, seedler, GPU ve hassasiyet iki yaml'da aynıdır; bir test bunu sınar.
     Gemma imajında `fla-core` ve `flash-linear-attention` yok (Gemma'da doğrusal-dikkat katmanı yok); yalnız `einops`.
   - **Modal:** `spawn_sft` / `spawn_orpo` `--ortam-kilidi configs/<kilit>.yaml` ister (varsayılansız); kilidin
     modeli `--model`le uyuşmazsa hiçbir şey başlamadan durur. Kilit hangi imajı çalıştıracağını seçer.
   - **Model kimliği:** `use_exact_model_name: true`. Yoksa Unsloth `google/gemma-4-E4B-it` yerine
     `unsloth/gemma-4-E4B-it`'i yükler; ağırlık aynı, ama `config.json`, `tokenizer_config.json` ve sohbet
     şablonu farklı (eos `<turn|>` yerine `<eos>`).
   - **LoRA hedefi:** yalnız dil kulesi. Düz 7 adlık liste görüntü (112) ve ses (36) kulesindeki
     `Gemma4ClippableLinear`lere de takılıyor; kilitteki desen 258 modül seçer. `get_peft_model` sonrası takılan
     modül sayısı ve kule dışı sayısı denetlenir, tutmazsa koşu başlamadan durur; sayılar künyeye yazılır.
     Gemma'ya özgü `per_layer_input_gate` ve `per_layer_projection` bilerek dışarıda (Qwen'le eşit tasarım).
   - **Tur işaretleri:** `<|turn>user\n` ve `<|turn>model\n`. Qwen'in şablonu cevabın önüne boş düşünce bloğu
     koyuyor, Gemma'nınki koymuyor; iki modelde de kayıp asistan işaretinden hemen sonra başlıyor (#78).
   - **Smoke ölçtü (2026-10-15, 50 adım, A100-40GB, [#80](record/kronoloji-75-86.md#80)):** Gemma bf16'da
     `grad_checkpoint: false` ile **sığdı**: tepe rezerve 34,39 GB / 42,41 GB (%81,1), 10,55 s/adım; LoRA 258 modül,
     kule dışı 0. Qwen: tepe rezerve 22,31 GB, 10,69 s/adım. Tarif değişmedi. Hâlâ açık: 2048 token tavanına yakın
     örneklerde tepenin ne olacağı (50 adım en uzun örneği görmemiş olabilir) ve Gemma'da TRL'nin ek bitiş işareti
     ekleyip eklemediği.
