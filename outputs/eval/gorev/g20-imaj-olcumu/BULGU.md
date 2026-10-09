# Görev 20 · Adım 6 — imaj **BUILD** ve **ÖLÇÜM** bulgusu

> **Tarih:** 2026-09-11 · **Maliyet: $0** — hakem YOK, model çağrısı YOK, HF'ten indirme YOK.
> Adım 6'nın *"imaj boyutu ÖLÇÜLÜR ve buraya yazılır — tahmin yazılmaz"* şartının
> **token gerektirmeyen yarısı**. `docker compose up` **KOŞULMADI** (`indir` kutusu `HF_TOKEN`
> ister, token yok; `HAKHUKUK_INDEKS_DEPO` bilerek boş). Servisler ayağa kaldırılmadı.
>
> ⛔ Hiçbir dosya değiştirilmedi: `hakhukuk/**` · `tests/**` · `docs/**` · `compose.yaml` ·
> `Dockerfile` · `scripts/**` **okundu, dokunulmadı**. Aşağıdaki iki kusur **raporlanmıştır,
> onarılmamıştır** — onarım Adım 4'ün işidir ve kendi turunu ister.

---

## 0. Ortam — doğrulandı, varsayılmadı

| şey | değer | nasıl ölçüldü |
| :--- | :--- | :--- |
| Docker istemci | **28.4.0**, build `d8eb465` | `docker --version` |
| Docker sunucu | **28.4.0** | `docker info --format '{{.ServerVersion}}'` |
| imaj deposu | **containerd snapshotter**, `overlayfs` | `docker info --format '{{.DriverStatus}} {{.Driver}}'` |
| boş disk | **834 GB** (`/`, 1007 GB'ın %13'ü dolu) | `df -h /var/lib/docker` |

⚠️ **containerd deposu boyut okumasını ikiye böler** ve bu, sayıları karşılaştırırken ilk tuzaktır:
`docker images` sütunu **açılmış (unpacked) boyutu**, `docker image inspect .Size` ise
**sıkıştırılmış içerik boyutunu** verir. Aşağıda **ikisi de** yazılıdır; bağlayıcı olan,
diskte gerçekten yer kaplayan **açılmış** sayıdır.

---

## 1. Hangi imaj hangi servisin — koda bakıldı

`compose.yaml` üç servis tanımlar, **iki** imaj kullanır (ADR-0078: *3 kutu, 2 daemon, 2 imaj*):

| servis | imaj | `build:` var mı | komut |
| :--- | :--- | :--- | :--- |
| `indir` | `hakhukuk:0.3.0` | **evet** (`build: .`, satır 28-29) | `python -m hakhukuk.indir /artefakt` |
| `llama` | `ghcr.io/ggml-org/llama.cpp:server-cuda-b10902` | hayır — hazır, pinli (satır 47) | bayrak kümesi (rejim kilidi) |
| `app` | `hakhukuk:0.3.0` | **evet** (`build: .`, satır 93-94) | `uvicorn hakhukuk.api:uygulama` |

**Cevap: `indir` ve `app` AYNI imajı paylaşır.** Tek `Dockerfile` vardır; `indir` yalnız farklı
bir `command` ile koşar. `Dockerfile`'ın kendi başlığı gerekçeyi yazıyor: *"Ayırsaydık `sha256`
kapısı iki entrypoint'e dağılırdı — kapı TEK yerde durur."* Ölçüm bunu doğruluyor:
`docker build` **tek** imaj üretti ve iki servis de onu etiketliyor.

---

## 2. Build bağlamı — ÖNCE ölçüldü, sonra build edildi

Endişe haklıydı: repo kökü **75 GB `models/`** taşıyor (`du -sh models` → `75G`; toplam repo `76G`).

| ölçüm | değer | nasıl |
| :--- | :--- | :--- |
| `.dockerignore` süzgecinden geçen ağaç (tahmin) | **422.408.435 bayt = 402,8 MiB** | `du -sb` ile ignore listesindeki dizinler dışlanarak |
| **BuildKit'in GERÇEKTEN aktardığı bağlam** | **77,42 MB** | build çıktısı `#4 [internal] load build context / transferring context: 77.42MB 0.8s done` |
| `Dockerfile` bağlamı | 926 B | `#3 transferring context: 926B done` |
| dışlanan `models/**` | 75 GB | `du -sh models` |
| dışlanan `*.npy` (2 dosya) | 165.871.872 bayt = 158,2 MiB | `find data/index -name '*.npy' -printf '%s'` |

**İki ayrı süzgeç çalışıyor, ikisi de tuttu:**
1. `.dockerignore` **74 GB'lık `models/**`'ı kesti** — beklenen bağlam 76 GB değil 402,8 MiB'e indi.
2. BuildKit ayrıca **yalnız `COPY` yönergelerinin gösterdiği yolları** senkronize etti, bu yüzden
   gerçek aktarım 402,8 MiB değil **77,42 MB** oldu. Aradaki fark, hiçbir `COPY`'nin dokunmadığı
   `data/train/` (169 MB) · `docs/` (1,9 MB) · `tests/` (880 KB).

⚠️ Bu ikinci süzgece **güvenilmemelidir**: `.dockerignore`'dan `models/**` düşerse ve ileride
biri `COPY . .` yazarsa bağlam **saatlik** hale gelir. Bugün koruyan satır `.dockerignore`'dakidir.

**Beklenmedik bir büyüklük çıkmadı ⇒ DURULMADI, build edildi.**

---

## 3. `hakhukuk:0.3.0` — build ve boyut

```
docker build --progress=plain -t hakhukuk:0.3.0 -f Dockerfile .
```

| ölçüm | değer | nasıl |
| :--- | :--- | :--- |
| çıkış kodu | **0** (başarılı) | build log `EXIT=0` |
| build süresi | **234 saniye** | `date +%s` farkı (başlangıç/bitiş damgası) |
| **boyut — açılmış** | **2,13 GB** | `docker images hakhukuk --format '{{.Size}}'` |
| boyut — sıkıştırılmış içerik | 452.747.745 bayt = **452,7 MB** | `docker image inspect --format '{{.Size}}'` |
| imaj `Id` | `sha256:9105f22dfa371e53977c4edbdef4eb52ab4feb206e75df6283feca29308097e5` | `docker image inspect --format '{{.Id}}'` |
| `RepoDigests` | `hakhukuk@sha256:9105f22d…8097e5` (yerel, kayda girmedi) | `docker image inspect --format '{{json .RepoDigests}}'` |

**74 GiB'e yaklaşmadı: 2,13 GB, yani hedefin ~%2,9'u.**

### En büyük 5 katman

`docker history hakhukuk:0.3.0 --no-trunc --format '{{.Size}}\t{{.CreatedBy}}'`

| # | boyut | katman | ne |
| ---: | ---: | :--- | :--- |
| 1 | **943 MB** | `RUN pip install --index-url .../whl/cpu … torch` | **CPU** torch tekerleği (§5) |
| 2 | **504 MB** | `RUN pip install ".[api]"` | `sentence-transformers` + `transformers` + `scipy` + `sklearn` + `fastapi`/`uvicorn` |
| 3 | **85,3 MB** | `debian.sh --arch amd64 … bookworm` | temel Debian katmanı (`python:3.11.16-slim-bookworm`) |
| 4 | **76,7 MB** | `COPY data/corpus/ data/corpus/` | korpus (§7'de bir kusur var) |
| 5 | **52,4 MB** | `RUN … make install` (CPython 3.11.16 derlemesi) | temel imajın Python'u |

Katman toplamı ≈ 1,67 GB ↔ `docker images` 2,13 GB: fark, containerd'ın açılmış anlık
görüntüsünün dosya sistemi ek yükü ve `history`'de `0B` görünen meta katmanlardır.

### Kurulu paketler — en büyük 12 (imajın içinden ölçüldü)

`docker run --rm hakhukuk:0.3.0 sh -c "du -sm /usr/local/lib/python3.11/site-packages/* | sort -rn | head -12"`

| paket | MiB |
| :--- | ---: |
| `torch` | **773** (bunun **455**'i `torch/lib`) |
| `transformers` | 118 |
| `scipy` | 113 |
| `sympy` | 80 |
| `sklearn` | 51 |
| `numpy` | 45 |
| `scipy.libs` | 30 |
| `numpy.libs` | 28 |
| `networkx` | 19 |
| `pip` | 15 |
| `tokenizers` | 12 |
| `hf_xet` | 12 |

Sürümler: `torch 2.14.0+cpu` · `sentence-transformers 6.0.1` · `transformers 5.17.0` · `numpy 2.4.6`.

---

## 4. `ghcr.io/ggml-org/llama.cpp:server-cuda-b10902` — boyut (yalnız `pull`, GPU kullanılmadı)

| ölçüm | değer | nasıl |
| :--- | :--- | :--- |
| **boyut — açılmış** | **6,99 GB** | `docker images … --format '{{.Size}}'` |
| boyut — sıkıştırılmış içerik | 2.589.343.668 bayt = **2,59 GB** | `docker image inspect --format '{{.Size}}'` |
| katman toplamı (`history`) | 4,40 GB | `docker history … --format '{{.Size}}'` toplandı |
| imaj `Id` | `sha256:82de60bb2ba6e66d750f4b7db8752bc3071a2ed3999700d0b21c8b5c709b5513` | `docker image inspect` |
| `RepoDigest` | `ghcr.io/ggml-org/llama.cpp@sha256:82de60bb…09b5513` | `docker image inspect` |

### En büyük 5 katman

| # | boyut | ne |
| ---: | ---: | :--- |
| 1 | **3,11 GB** | `apt-get install cuda-libraries-12-8 … libcublas … libnccl2` — **CUDA 12.8 çalışma zamanı** |
| 2 | **766 MB** | `apt-get install libgomp1 curl ffmpeg` (+ llama.cpp derleme artıkları) |
| 3 | **214 MB** | `COPY /app/lib/ /app` — llama.cpp paylaşılan kütüphaneleri |
| 4 | 266 kB | `apt-mark hold` (cuBLAS/NCCL sabitleme) |
| 5 | 90,1 kB | `COPY /app/full/llama /app/full/llama-server /app` — **sunucunun kendisi** |

⚠️ Not: imajın `ENTRYPOINT`'i `/app/llama-server`'dır (katman #5'te `HEALTHCHECK`'ten hemen
sonra okunur) — `compose.yaml`'ın *"ENTRYPOINT imaj yapılandırmasından OKUNDU, varsayılmadı"*
yorumu **imajın kendisinden doğrulandı**. Ayrıca `ENV LLAMA_ARG_HOST=0.0.0.0` katmanda var.

**İki imajın toplamı: 2,13 + 6,99 = 9,12 GB** (açılmış). Buna **ağırlık (2,592 GiB GGUF) ve
indeks dâhil değildir** — onlar volume'e iner.

---

## 5. 🚨 torch tekerleği — G20 ajanının endişesi **ÇÜRÜTÜLDÜ**

**Endişe:** *"`sentence-transformers` torch'u kurulu bulmazsa PyPI'nin CUDA tekerleğine düşer ve
imaj ~5 GB şişer."*

```
$ docker run --rm hakhukuk:0.3.0 python -c "import torch; print(torch.__version__, torch.version.cuda)"
torch 2.14.0+cpu | version.cuda = None
```

| ölçülen | değer | hüküm |
| :--- | :--- | :--- |
| `torch.__version__` | **`2.14.0+cpu`** | `+cpu` son eki = `download.pytorch.org/whl/cpu` tekerleği |
| `torch.version.cuda` | **`None`** | **CUDA tekerleği ÇEKİLMEMİŞ** |
| `torch` katmanı | **943 MB** | CUDA tekerleği ~2,5-5 GB olurdu |
| `site-packages/torch` | 773 MiB | — |

**Sonuç: CPU tekerleği. İmaj şişmemiştir.** `Dockerfile`'ın torch'u `pip install ".[api]"`'den
**önce** ve açık `--index-url`'le kurma kararı işini yapmış; ikinci `pip` çağrısı gereksinimi
karşılanmış bulup üzerine yazmamıştır (`+cpu` son eki hâlâ yerinde — ölçüldü, varsayılmadı).

---

## 6. Duman denetimi — ağsız (`--network none`), modelsiz

⛔ `servis.answer` **çağrılmadı** (llama-server ve indeks imajda yok).

### (1) import kapısı — **GEÇTİ**
```
$ docker run --rm --network none hakhukuk:0.3.0 \
    python -c "import hakhukuk, hakhukuk.api, hakhukuk.cli, hakhukuk.tui; print('import OK')"
import OK
```

### (2) giriş noktası — **GEÇTİ** (çıkış kodu 0)
```
$ docker run --rm --network none hakhukuk:0.3.0 hakhukuk --kuru-calisma "duman testi"
🤐 SUSKUNLUK — kaynaklarda karşılık bulunamadı

(kuru çalışma) soru alındı: duman testi

Kapsam: yürürlükteki kanunlar (künye okunamadı — sayı belirsiz). Yönetmelik · tüzük · KHK · tebliğ YOK.

⚖️  Bu yanıt hukuki tavsiye değil, bilgilendirme amaçlıdır. Bağlayıcı bir karar vermeden önce
    güncel mevzuatı doğrulayın ve bir avukata danışın.
cikis=0
```
**Açık kusur 28 imajda TEKRARLAMIYOR:** `hakhukuk` giriş noktası imajda **oluşmuş ve koşuyor**.
`pyproject.toml`'un `requires = ["setuptools>=77"]` düzeltmesi yalıtımlı build'de işini görüyor.
⚠️ Ama çıktının içinde **yeni bir kusur var** — §7.

### (3) `indir` modülü — **GEÇTİ** (indirme ÇALIŞTIRILMADI)
```
$ docker run --rm --network none hakhukuk:0.3.0 python -c "from hakhukuk.indir import *; print('indir modülü OK')"
indir modülü OK
```
Ağ kapalıyken bile import ediliyor — `huggingface_hub` içe aktarması bilerek fonksiyon
gövdesinde (`noqa: PLC0415`), modül seviyesinde değil. Tasarım tuttu.

**3/3 GEÇTİ.**

---

## 7. Ağırlık/indeks imajda YOK — ama korpus katmanında ölü yük var

```
$ docker run --rm hakhukuk:0.3.0 sh -c "ls -la /app/models /app/data/index 2>&1 | head"
ls: cannot access '/app/models': No such file or directory
ls: cannot access '/app/data/index': No such file or directory
```
```
$ docker run --rm hakhukuk:0.3.0 sh -c "find / -xdev \( -name '*.gguf' -o -name 'gomme.npy' -o -name '*.safetensors' \) -print | head; echo TARAMA_BITTI"
TARAMA_BITTI          ← tek satır: HİÇBİR eşleşme yok
```

`/app` ağacı (imajın içinden, `du -sh`):

| yol | boyut |
| :--- | ---: |
| `/app/data` | **74 MB** (yalnız `data/corpus/`) |
| `/app/scripts` | 840 KB |
| `/app/hakhukuk` | 84 KB |
| `/app/hakhukuk.egg-info` | 48 KB |
| `/app/README.md` | 24 KB |
| `/app/build` | 96 KB |

**`.dockerignore` işini yaptı.** GGUF yok, `gomme.npy` yok, `safetensors` yok, `models/` yok.
İmaj **2,13 GB** — 74 GiB'in yanına yaklaşmıyor.

### ⚠️ KUSUR A — imaja giren yedek dosya (36,1 MiB ölü yük)

```
$ docker run --rm hakhukuk:0.3.0 sh -c "ls -la /app/data/corpus/"
KUNYE.json                               902
mevzuat_maddeler.jsonl              38751499
mevzuat_maddeler.jsonl.yedek-2026-08-05   37903062   ← 36,1 MiB
```
`COPY data/corpus/ data/corpus/` dizinin **tamamını** alıyor; `.dockerignore` bu yedeği
dışlamıyor. **76,7 MB'lık korpus katmanının %49'u ürünün hiç okumadığı bir yedek.**
Onarım tek satırlık bir `.dockerignore` eklemesidir — **yapılmadı**, `.dockerignore`'a dokunmak
bu turun kapsamı dışında.

### ⚠️ KUSUR B — künye yolu konteynerde SESSİZCE kırık (*"hata vermeden yanlış"* sınıfı)

Duman denetimi (2)'nin çıktısındaki `künye okunamadı — sayı belirsiz` bir tesadüf değil.
`hakhukuk/cli.py:24`:
```python
_KUNYE_YOLU = pathlib.Path(__file__).resolve().parent.parent / "data/corpus/KUNYE.json"
```
Bu **repo köküne göreli** bir yoldur ve imajda paket iki yerde durur. Ölçüldü:

| nasıl koşulur | `cli.py` nereden gelir | künye yolu | var mı |
| :--- | :--- | :--- | :--- |
| `cd /app && python -c "import hakhukuk.cli"` | `/app/hakhukuk/cli.py` | `/app/data/corpus/KUNYE.json` | **True** |
| **`hakhukuk` konsol betiği** (kullanıcının koştuğu) | `/usr/local/lib/python3.11/site-packages/hakhukuk/cli.py` | `/usr/local/lib/python3.11/site-packages/data/corpus/KUNYE.json` | **False** |

Konsol betiği `sys.path[0]`'ı `/usr/local/bin` yapar, bu yüzden **kurulu** paketi alır ve künye
`site-packages` altında aranır. Dosya imajda **vardır** (`/app/data/corpus/KUNYE.json`, 902 bayt,
host'takiyle birebir) — bulunamayan yol yanlıştır. Sonuç: **kapsam cümlesi patlamadan bozulur**,
vatandaş *"892 kanun · 40.496 madde"* yerine *"sayı belirsiz"* okur.

⛔ **Onarılmadı.** `hakhukuk/**` bu turda dokunulmazdır ve düzeltme (`importlib.resources` ya da
korpusu pakete taşımak) yapısal bir karardır — kendi turunu ister.

---

## HÜKÜM

**`hakhukuk:0.3.0` build edildi (çıkış 0, 234 saniye) ve ölçüldü: açılmış 2,13 GB** (sıkıştırılmış
içerik 452,7 MB), build bağlamı **77,42 MB** — `.dockerignore` 74 GB'lık `models/**`'ı kesti ve
imajda tek bir `.gguf`, `gomme.npy` ya da `safetensors` yok, yani ağırlık/indeks **imaja
gömülmedi**. **Hazır `llama` imajı 6,99 GB** (sıkıştırılmış 2,59 GB), ve bunun **3,11 GB'ı tek
bir CUDA 12.8 kütüphane katmanı**dır — iki imaj toplamı **9,12 GB**. **G20 ajanının torch
endişesi çürütüldü: `torch 2.14.0+cpu`, `torch.version.cuda = None` ⇒ CPU tekerleği, katman
943 MB**; CUDA tekerleği çekilseydi bu katman birkaç GB olurdu, olmadı. **Duman denetiminin üç
komutu da geçti** — `import OK`, `hakhukuk --kuru-calisma` çıkış 0 ile koştu (açık kusur 28
imajda **tekrarlamıyor**: giriş noktası oluşmuş), `indir modülü OK` (ağ kapalı, indirme
çalıştırılmadı). İki kusur **ölçüldü ve raporlandı, onarılmadı**: (A) `COPY data/corpus/` 36,1
MiB'lık bir `.yedek-2026-08-05` dosyasını imaja sokuyor — korpus katmanının yarısı ölü yük;
(B) `cli.py`'nin künye yolu repo köküne göreli olduğu için **konsol betiğiyle koşulduğunda
sessizce kırılıyor** ve kapsam cümlesi *"sayı belirsiz"*e düşüyor — bu tam olarak bu hattın
*"hata vermeden yanlış"* sınıfıdır. **Adım 6'nın kalan yarısı hâlâ `HF_TOKEN` bekliyor:**
`docker compose up` koşulmadı, dolayısıyla `indir` kutusunun `sha256`/bayt kapısı (2.783.446.720
bayt, revizyon `902ace67…`) **hiç denenmedi**, `llama` daemon'u hiç ayağa kalkmadı, uçtan uca
`app → llama` yolu **doğrulanmadı**; ayrıca `HAKHUKUK_INDEKS_DEPO` bilerek boş olduğu için
`indir_indeks()` token gelse bile Görev 8 kapanmadan **`KimlikHatasi` ile patlayacaktır** —
yani tam bir `compose up` için **iki** eksik vardır, biri değil.
