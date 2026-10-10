# Eğitim ortamı kilidi

> **Bu belge ne:** Makale 1 ve Makale 2 için yapılacak **her** eğitim koşusunun (Modal ya da Vast)
> uymak zorunda olduğu donanım, yazılım ve tarif değerleri. Amaç: platform değişse bile kolların
> aynı ortamda eğitilmiş olması — aksi hâlde kollar arası fark "yöntem mi, ortam mı" diye
> ayrıştırılamaz. Yol haritası: [`YAYIN_YOL_HARITASI.md`](YAYIN_YOL_HARITASI.md) (K6, K13).
>
> **DURUM (2026-10-10): bu belge henüz bir kilit DEĞİLDİR.** Depo bunu iki kez öğrendi: kapıyı
> belgeye değil koda koy ([ADR-0030](adr/kararlar-0027-0044.md#adr-0030) m.3); `llama-server`
> bayrakları üç belgede düz metin olarak yazılıydı ve "hiçbiri kapı değildi"
> ([ADR-0078](adr/kararlar-0064-0085.md#adr-0078)). Kilit üç parçayla tamamlanır; ikisi F0'da yazılır.

## 1 · Üç parça

| parça | ne | durum |
| :--- | :--- | :--- |
| `docs/EGITIM_ORTAMI.md` | insan için: ne kilitli, neden, platform değişince ne yapılır | **bu belge** |
| `configs/egitim_ortami.yaml` | aynı değerlerin makine okunur **tek kaynağı** | F0 |
| betik başı kontrolü + test | `train_sft.py` ve `train_orpo.py` **model yüklenmeden önce** yaml'ı okur; GPU mimarisi, paket sürümleri, `fla-core`'un gerçekten içe aktarılabilmesi ve hassasiyetin **açıkça** verilmiş olması doğrulanır; uymazsa koşu para harcamadan durur; gerçek değerler künyeye yazılır. Bir test, kontrolün betiklerde durduğunu sınar (`tests/test_konteyner.py`'nin eğitim tarafındaki eşi) | F0 |

Bu belge ile yaml çelişirse **yaml bağlayıcıdır** ve belge düzeltilir.

## 2 · Kilitli değerler

| alan | değer | kaynak / durum |
| :--- | :--- | :--- |
| GPU | **NVIDIA A100**, compute capability 8.0; 40 GB ya da 80 GB; gerçek model künyeye yazılır | Makale 1 kollarında RTX 5090 ve H100 **yasak** (farklı mimari kollar arasına değişken sokar) |
| Modal kart dizesi | `A100-40GB`, **açıkça** | yalnız `"A100"` yazılırsa 40 ya da 80 GB gelebilir (tuzak 6.7, [#48](record/kronoloji-39-52.md#48)) |
| Python | 3.11 | `scripts/egitim/modal_train.py:50` |
| paketler | `requirements.lock.txt`, `sha256 6b5209e6a293f3c72f5d6c1dfa64591128f48dd8e3c0e07cdc3141c733c6ebb0` — torch 2.10.0 · triton 3.6.0 · transformers 5.10.2 · peft 0.19.1 · trl 0.24.0 · unsloth 2026.6.1 · unsloth_zoo 2026.6.1 · accelerate 1.13.0 · bitsandbytes 0.49.2 · datasets 4.3.0; kurulum `--no-deps` | dosyadan okundu, 2026-10-10 |
| `einops` · `fla-core` · `flash-linear-attention` | **sürümleri F0'da sabitlenecek** | bugün **sürümsüz** kuruluyor (`modal_train.py:81`) → imaj farklı günlerde kurulursa farklı sürüm gelir, hata vermez |
| `fla-core` | **zorunlu**; ölçüt `import fla` değil `from fla.modules import FusedRMSNormGated` | eksikliği fla'nın hiç olmamasından kötü ([ADR-0033](adr/kararlar-0027-0044.md#adr-0033)) |
| `causal-conv1d` | **yok** | tavanı 1,254× ölçüldü, ≥2× kapısından kaldı ([#44](record/kronoloji-39-52.md#44)) |
| hassasiyet | **açıkça verilir, varsayılan YOK.** Değer τ_g v1'in rejimine göre F0'da seçilir; bütün kollar aynı rejimde | bugün betikler bayraksız çağrılınca **sessizce 4-bit NF4**'e düşüyor (§3) |
| LoRA | r=16 · α=32 · dropout 0,05 · `use_rslora=False` · hedef modüller: `q_proj k_proj v_proj o_proj in_proj_qkv in_proj_z in_proj_a in_proj_b gate_proj up_proj down_proj` (11) | `outputs/tg_v1` ve `outputs/ta_v1` `adapter_config.json` dosyalarında birebir doğrulandı |
| SFT tarifi | veri `data/train/raft_scrubbed/` (17.323 satır) · 2048 token · cihaz başı batch 2 × biriktirme 8 · gradient checkpointing **kapalı** · lr 1e-4 cosine · `adamw_8bit` · 1 epoch = 1.083 adım · packing **yok** | [ADR-0033](adr/kararlar-0027-0044.md#adr-0033), [#40](record/kronoloji-39-52.md#40) |
| ORPO tarifi | veri `data/train/orpo_abstain_cp2c/` (845 satır = 726 çift + 145 tekrar; 26 doğrulama) · lr 1e-5 · beta 0,1 · biriktirme 64 · 5 epoch = 70 adım · **taze adaptör** (`--fresh-adapter`) | [#48](record/kronoloji-39-52.md#48), [`kollar.md`](record/kollar.md) |
| seed | 1. seed **3407** (`v1`) · 2. seed **3408** · 3. seed **3409** | 2-3 bu belgeyle, sonuç görülmeden önerildi; yaml'a yazılınca kesinleşir |
| GPU üzerinde yalnız eğitim | ölçüm, hakem ve API anahtarları **eğitim makinesine gitmez** | Vast için zorunlu |

## 3 · Bilinen sessiz tehlikeler

| tehlike | nerede | karşılık |
| :--- | :--- | :--- |
| `--bf16-base` verilmezse **sessizce QLoRA (NF4)** | `train_sft.py:173-180` · `train_orpo.py:164-172` · Modal'da `bf16_base = False` (`modal_train.py:440`) | hassasiyet zorunlu argüman olur ([ADR-0026](adr/gemma4-12b-dersler.md#adr-0026) ilkesi) |
| `--target-modules` verilmezse `in_proj_*` düşer, 24 linear-attention katmanı LoRA'sız kalır | [#40](record/kronoloji-39-52.md#40) | hedef modül listesi yaml'dan gelir, sayısı (11) kontrol edilir |
| `--data` konteyner yolu ↔ yerel yol karışıyor | [#40](record/kronoloji-39-52.md#40), [#48](record/kronoloji-39-52.md#48) | veri kapısı model yüklemesinden önce; satır sayısı künyeye |
| `--batch` ve `--grad-accum` ayrı verilip çarpım sessizce kayıyor | [ADR-0033](adr/kararlar-0027-0044.md#adr-0033) | etkin batch yaml'da; çarpım kontrol edilir |
| `lora_dropout=0.0` Python'da falsy, bayrak sessizce yok sayılıyor | [ADR-0033](adr/kararlar-0027-0044.md#adr-0033) | değer yaml'dan, eşitlikle kontrol |
| `causal-conv1d` yokken "fast path not available" uyarısı | [ADR-0033](adr/kararlar-0027-0044.md#adr-0033) | uyarı ölçüt değildir; ölçüt `s/adım` |

## 4 · Platform değişimi (Modal → Vast)

1. **Önce bekle:** Modal kredisi aylık yenileniyorsa yeni ayı beklemek $0'dır.
2. **Aynı imaj:** Modal ile Vast'a aynı Docker imajı, aynı özetle (digest) verilir; imaj F0'da
   `requirements.lock.txt` + sabitlenmiş `fla-core` sürümüyle bir kez kurulur.
3. **Yalnız A100**, **blok sınırında** (bir koşu asla iki platforma bölünmez; en doğal sınır Gemma
   bloğunun tamamı).
4. **Eşdeğerlik kontrolü** (~$1): Modal'da koşulmuş bir yapılandırmanın ilk 50 adımı Vast'ta aynı
   seed'le tekrarlanır, kayıp eğrileri kıyaslanır. **Tolerans sayısı uydurulmaz:** F0'da aynı
   platformda aynı seed'le iki kısa koşu yapılır (~$1-2), aradaki fark **gürültü tabanıdır**;
   platformlar arası fark bu tabanın içinde kalmalı. Kalmazsa o blok tamamen tek platformda
   yeniden koşulur. (Emsal: batch değişince adım-10 kaybı 0,788 ↔ 0,7987 ölçülmüştü,
   [ADR-0033](adr/kararlar-0027-0044.md#adr-0033).)
5. **Vast kuralları:** API anahtarı kiralık makineye gitmez · koşu bitince makine **silinir**
   (depolama, makine silinene kadar faturalanır) · kesilebilir kiralamada `save_steps` + otomatik
   devam ([ADR-0008](adr/gemma4-12b-dersler.md#adr-0008)).
6. Makalenin ekine **donanım tablosu**: hangi kol nerede eğitildi.

## 5 · Her koşunun künyesine yazılacaklar

gerçek GPU adı ve belleği (`nvidia-smi`) · sürücü ve CUDA sürümü · imaj özeti · bütün paket
sürümleri (`importlib.metadata`) · `requirements.lock.txt` özeti · hassasiyet · LoRA ayarları ve
hedef modüller · veri yolu, satır sayısı ve `sha256` · seed · adım sayısı · etkin batch · platform.
Künyedeki her alan **ya bir değişkenden ya bir ölçümden** gelir; elle yazılmış alan künyeyi kanıt
olmaktan çıkarır (tuzak 1.12, [#66](record/kronoloji-63-71.md#66)).

## 6 · F0'da doldurulacak açık maddeler

1. τ_g v1'in hassasiyeti (bundle'daki commit geçmişi + Modal günlükleri) → §2 hassasiyet satırı.
2. `einops` · `fla-core` · `flash-linear-attention` sürümleri.
3. Docker imajı ve özeti; imajın CUDA sürümünün istediği en düşük sürücü.
4. `configs/egitim_ortami.yaml` + betik başı kontrolü + test.
5. Gürültü tabanı ölçümü (§4.4).
6. Gemma 4 E4B için ayrı bir bölüm: hedef modüller (yalnız metin kulesi) ve düşünce kapanış işareti.
