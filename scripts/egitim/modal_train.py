#!/usr/bin/env python
"""
HakHukuk — Modal sarmalayıcı (bulut eğitim). **Base-agnostik.**

`scripts/egitim/train_sft.py` / `scripts/egitim/train_orpo.py`'a DOKUNMADAN onları Modal GPU'sunda
subprocess ile koşar. Yerel kart sadece prototip/eval; gerçek eğitim burada.

⚠️ **Model adı bu dosyada YOK.** `--model` zorunlu parametre; verilmezse hata verir.
Sessizce yanlış base'e düşmek, saatler süren bir koşuyu çöpe çevirir.

⚠️ GPU da parametre: `HUKUK_GPU` env (varsayılan `A100`). Küçük base'de `L4`/`A10G` yeter,
büyükte `A100-80GB`/`H100`. Modal'da GPU dekoratör-zamanlı → env ile seçilir:
    HUKUK_GPU=L4 modal run scripts/egitim/modal_train.py::spawn_sft --model <repo> --data /data/<set>

⚠️ **`--data` KONTEYNER İÇİ YOLDUR, volume yolu DEĞİL.** `hukuk-data` volume'ü `/data`'ya
bağlanır (aşağıdaki VOLUMES), yani volume'deki `/<set>` konteynerde `/data/<set>` olur.
`--data /<set>` yazmak `FileNotFoundError: Unable to find '/<set>/train.jsonl'` verir — ve bu hata
(düzeltilmeden önce) model yüklendikten SONRA patlıyordu, yani ~10 dk GPU yakıyordu. Artık
`train_sft.py` veriyi model yüklemeden önce denetliyor.

Kullanım:
  # 0) Veriyi bir kez volume'a yükle  (volume kökü → /<set>)
  modal volume put hukuk-data data/train/<set> /<set>

  # 1) Önce SMOKE (~50 step, config+loss doğrulama)   ← DİKKAT: /data/<set>
  modal run --detach scripts/egitim/modal_train.py::spawn_sft --model <hf-repo> --data /data/<set> --smoke \
      --user-part '<|turn>user\n' --assistant-part '<|turn>model\n'

  # 2) Loss düşüyorsa tam koşu (aynı --user-part/--assistant-part ile)
  modal run --detach scripts/egitim/modal_train.py::spawn_sft --model <hf-repo> --data /data/<set> --run-name r1 \
      --epochs 1 --user-part '...' --assistant-part '...'

  # 3) Bitince adapter'ı yerele çek
  modal volume get hukuk-outputs /r1 ./outputs/r1
"""
import os

import modal

app = modal.App("hukuk-sft")

# GPU seçimi — base'e göre değişir, bu yüzden env'den. Dekoratör import-zamanı okur.
GPU = os.environ.get("HUKUK_GPU", "A100")

# --- Ortam: requirements.lock.txt'teki pinli sürümler ---
# ⚠️ --no-deps ZORUNLU: lock zaten tam-çözülmüş düz liste (tüm transitive pinli). Resolver'ı
# atlar → unsloth'un eski `transformers<=…` metadata kısıtı çakışmaz. (Yerel env de fiilen
# bu durumda: lock'taki transformers runtime'da unsloth ile çalışıyor.)
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install_from_requirements("requirements.lock.txt", extra_options="--no-deps")
    .env({
        "HF_HUB_ENABLE_HF_TRANSFER": "1",   # büyük/gated ağırlıklar için hızlı indirme
        "HF_HOME": "/cache/hf",             # model cache → kalıcı volume (her koşuda yeniden indirme yok)
        "PYTHONUNBUFFERED": "1",            # loss canlı görünsün
        "UNSLOTH_DISABLE_STATISTICS": "1",  # açılış telemetri çağrısı hang/timeout'unu önle
    })
    # ⚠️ Qwen3.5 HİBRİT linear-attention: 32 katmanın 24'ü linear-attention. Triton çekirdeği yoksa
    # transformers torch reference fallback'e düşer (özyineli durumu her timestep materyalize eder)
    # → A100-40GB'de ~36 s/it (ölçüldü, #39) = tam koşu ~10 sa.
    #
    # 🚨 **`fla-core` ZORUNLU — `flash-linear-attention` TEK BAŞINA İŞE YARAMAZ, HATTA ZARARLI.**
    # Paket 0.5.x'te İKİYE BÖLÜNDÜ (ölçüldü 2026-07-25, CP4): `flash-linear-attention` yalnız
    # `fla/layers` + `fla/models` taşıyor; ÇEKİRDEKLER (`fla.ops.gated_delta_rule`, `fla.modules`)
    # `fla-core`'da ve oraya `Requires-Dist: fla-core==<sürüm>` ile bağlanıyor. `--no-deps` bu bağı
    # kesiyor → konteynerde `import fla` ÇALIŞIYOR (dolayısıyla transformers'ın
    # `is_flash_linear_attention_available()` kapısı **True** dönüyor) ama `fla.modules` YOK
    # → `from fla.modules import FusedRMSNormGated` çöküyor ve model HİÇ yüklenmiyor.
    # Yani eksik `fla-core`, fla'nın hiç olmamasından KÖTÜ: yavaş-ama-çalışır yerine hiç-çalışmaz.
    # (Hata `transformers`'ın tembel-modül sarmalayıcısı yüzünden kök nedeni gizleyen tek satıra
    #  dönüşüyor: "Could not import module 'Qwen3_5ForConditionalGeneration'". Teşhis: modal_diag.py)
    #
    # Sürüm uyumu ÖLÇÜLDÜ: `fla-core` yalnız `torch>=2.7` + `triton>=3.3` istiyor; lock'ta
    # torch 2.10.0 + triton 3.6.0 var → **yeterli.** ⚠️ Devir notundaki *"fla torch>=2.11 istiyor,
    # ayrı bir Modal image kurulmalı"* teşhisi YANLIŞTI — pinli lock korunuyor, ayrı image gerekmiyor.
    #
    # `causal-conv1d` BİLEREK YOK: fla'nın opsiyonel extra'sı (`extra == "conv1d"`), derleme ister.
    # Yokluğunda yalnız depthwise conv torch'a düşer; PAHALI çekirdek (`chunk_gated_delta_rule`)
    # fla'dan gelir. ⚠️ Bu yüzden "fast path is not available" UYARISI YİNE BASILIR — uyarıyı
    # başarısızlık sanma, ölçüt **s/it**.
    .pip_install("einops", "fla-core", "flash-linear-attention", extra_options="--no-deps")
    .add_local_dir("scripts", remote_path="/root/scripts")
)

data_vol = modal.Volume.from_name("hukuk-data")
out_vol = modal.Volume.from_name("hukuk-outputs")
hf_cache = modal.Volume.from_name("hukuk-hf-cache", create_if_missing=True)
VOLUMES = {"/data": data_vol, "/outputs": out_vol, "/cache/hf": hf_cache}
SECRETS = [modal.Secret.from_name("huggingface-secret")]   # HF_TOKEN → gated indirme


def _require(name: str, value):
    """Sessiz yanlış-base'e düşmeyi engelle: kritik parametre boşsa erken patla."""
    if not value:
        raise SystemExit(
            f"[modal] 🚫 --{name} ZORUNLU. Base/veri bu dosyada gömülü DEĞİL "
            f"(bilerek: yanlış modele sessizce düşmek bir koşuyu çöpe çevirir)."
        )
    return value


def _run_with_commits(cmd, vols, every_s: int):
    """Alt süreci koştur + periyodik commit. Kesinti olursa son commit'li checkpoint'ten
    resume edilir (train_sft/train_orpo `get_last_checkpoint` ile otomatik).
    Tek-seferlik son commit YETMEZ — kesinti commit'ten önce olursa checkpoint uçar."""
    import subprocess
    import time

    print("[modal] çalıştırılıyor:", " ".join(cmd), flush=True)
    proc = subprocess.Popen(cmd)
    while proc.poll() is None:
        time.sleep(every_s)
        for v in vols:
            try:
                v.commit()
            except Exception as e:
                print(f"[modal] ara commit atlandı (önemsiz): {e}", flush=True)
        print("[modal] ara commit → checkpoint kalıcı (resume güvencesi)", flush=True)
    if proc.returncode != 0:
        raise SystemExit(f"[modal] HATA çıkış kodu={proc.returncode}")
    for v in vols:
        v.commit()


# ── SFT (QLoRA) ───────────────────────────────────────────────────────────────
@app.function(image=image, gpu=GPU, volumes=VOLUMES, secrets=SECRETS,
              timeout=6 * 60 * 60)
def train(model: str, data_path: str, run_name: str, user_part: str, assistant_part: str,
          epochs: float = 1.0, max_steps: int = -1, extra_args: list[str] | None = None):
    import sys
    cmd = [
        sys.executable, "/root/scripts/egitim/train_sft.py",
        "--model", model,
        "--data", data_path,
        "--run-name", run_name,
        "--output-dir", f"/outputs/{run_name}",
        "--epochs", str(epochs),
        # Maskeleme sınırları — train_sft.py bunları render'a karşı ASSERT eder;
        # yanlışsa eğitim başlamadan patlar (sessizce bozuk eğitmekten iyidir).
        "--user-part", user_part,
        "--assistant-part", assistant_part,
    ]
    if max_steps and max_steps > 0:
        cmd += ["--max-steps", str(max_steps)]
    if extra_args:
        cmd += extra_args
    _run_with_commits(cmd, [out_vol, hf_cache], every_s=900)
    print(f"[modal] SFT bitti → adapter: hukuk-outputs:/{run_name}", flush=True)


# ── ORPO (tercih öğrenmesi; adapter-continuation veya taze) ───────────────────
@app.function(image=image, gpu=GPU, volumes=VOLUMES, secrets=SECRETS,
              timeout=6 * 60 * 60)
def train_orpo(model: str, data_path: str, run_name: str, adapter: str | None = None,
               epochs: float = 1.0, max_steps: int = -1, beta: float = 0.1,
               lr: float = 1e-5, grad_accum: int = 64, save_steps: int = 100,
               bf16_base: bool = False, lora_dropout: float = -1.0,
               target_modules: str = ""):
    import sys
    cmd = [
        sys.executable, "/root/scripts/egitim/train_orpo.py",
        "--model", model,
        "--data", data_path,
        "--run-name", run_name,
        "--output-dir", f"/outputs/{run_name}",
        "--epochs", str(epochs), "--beta", str(beta), "--lr", str(lr),
        "--grad-accum", str(grad_accum), "--save-steps", str(save_steps),
    ]
    # ⚠️ REJİM EŞLEŞMESİ (τ_g ile merge edilebilirlik şartı) — sessizce ayrışırsa iki task-vector
    # farklı θ_base'den türer ve kıyaslanamaz olur. Bkz. docs/open_questions.md #13.
    if bf16_base:
        cmd += ["--bf16-base"]
    if lora_dropout >= 0:            # 0.0 geçerli DEĞER → `if lora_dropout:` yazılamaz (falsy tuzağı)
        cmd += ["--lora-dropout", str(lora_dropout)]
    if target_modules:               # varsayılan liste `in_proj_*` içermez → 24 katman LoRA'sız kalır
        cmd += ["--target-modules", *target_modules.split()]
    # adapter verilirse continuation (önceki turun kazanımı taşınır), yoksa base'e taze adapter.
    cmd += ["--adapter", adapter] if adapter else ["--fresh-adapter"]
    if max_steps and max_steps > 0:
        cmd += ["--max-steps", str(max_steps)]
    _run_with_commits(cmd, [out_vol, hf_cache], every_s=900)
    print(f"[modal] ORPO bitti → adapter: hukuk-outputs:/{run_name}", flush=True)


# ── CP2-c HASAT: llama.cpp taşıyıcısı (ADR-0047 m.2) ──────────────────────────
# ⚠️ Aşağıdaki `harvest_rejected` CP2'nin hasadı DEĞİLDİR (eski `gen_v3_rejected.py`'yi çağırır).
# CP2-c `cp2_harvest.py` kullanır: bütçeli düşünce · iki tip · eş zamanlı. Giriş: `spawn_cp2c`.
#
# 🚨 TAŞIYICI YERELLE BİREBİR OLMAK ZORUNDA. Hasat, kolların dağıtılacağı kiple aynı kipte
# yapılır (ADR-0042 on-policy gerekçesi + ADR-0047 m.2): **Q4_K_M GGUF + llama.cpp**, KV q8_0,
# `-fa on`, `--no-context-shift`, slot başına 8192 ctx — hepsi `cp0_thinking_gen.sh` ile aynı.
# Değişen YALNIZ ikisi: `-np` ve kart. **vLLM/bf16 YASAK** — bf16'da üretilen negatifler
# dağıtılan modelin hataları olmaz, ADR-0042'nin kendi gerekçesi künyesince çürür.
harvest_image = (
    # llama.cpp'nin resmî CUDA server imajı — yerelde derlenen ikilinin karşılığı.
    modal.Image.from_registry("ghcr.io/ggml-org/llama.cpp:server-cuda", add_python="3.11")
    # ⚠️ İmajın ENTRYPOINT'i `/app/llama-server`; temizlenmezse Modal'ın çalıştırıcısı ona
    # argüman olarak geçer ve konteyner `invalid argument: python` ile ölür (ölçüldü).
    .entrypoint([])
    # Python ortamı eğitim imajıyla AYNI lock'tan: `cp2_harvest.py` üretim yolunu
    # `gen_eval_grounded.generate_http`ten import eder (ikinci bir üretim gövdesi = sessiz
    # protokol sapması), o da modül düzeyinde unsloth/torch çeker.
    .pip_install_from_requirements("requirements.lock.txt", extra_options="--no-deps")
    .pip_install("einops", "fla-core", "flash-linear-attention", extra_options="--no-deps")
    # `openai` lock'ta YOK (lock eğitim içindi) — hasadın HTTP istemcisi bu. Sürüm yerelle
    # eşitlendi: üretim yolu yerelde ölçülen pilotla aynı istemci gövdesinden geçsin.
    .pip_install("openai==2.41.0")
    .env({"PYTHONUNBUFFERED": "1", "UNSLOTH_DISABLE_STATISTICS": "1"})
    .add_local_dir("scripts", remote_path="/root/scripts")
)


@app.function(image=harvest_image, gpu=GPU, volumes=VOLUMES, timeout=12 * 60 * 60)
def harvest_cp2(gguf: str, packed: str, madde: str, out_dir: str, types: list[str],
                limit: int = 0, target: int = 0, np_slots: int = 32,
                ctx_per_slot: int = 8192, gate_after_s: int = 600,
                gate_max_s: float = 2.88, seed: int = 3407, commit_every_s: int = 120,
                skip_first: int = 0):
    """CP2-c üretim hasadı — `llama-server` (-np) + `cp2_harvest.py`, iki tip sırayla.

    Hasat HTTP üzerinden çalışır (doğrudan transformers değil), o yüzden sunucu bu
    konteynerin içinde ayağa kalkar. Çıktı `out_dir`e yazılır ve periyodik commit'lenir —
    koşu kesilirse `load_done` kaldığı yerden devam eder.
    """
    import hashlib
    import json
    import os
    import shutil
    import subprocess
    import sys
    import time
    import urllib.request

    # ── VERİ KAPISI: hiçbir şey yüklenmeden önce (tuzak 6.2) ──────────────────
    for etiket, yol in (("gguf", gguf), ("packed", packed), ("madde", madde)):
        if not os.path.isfile(yol):
            raise SystemExit(f"[cp2c] 🚫 {etiket} yok: {yol} — volume'a yüklendi mi?")
    binary = shutil.which("llama-server") or "/app/llama-server"
    if not os.path.isfile(binary):
        raise SystemExit(f"[cp2c] 🚫 llama-server bulunamadı ({binary}) — imaj değişti mi?")
    os.makedirs(out_dir, exist_ok=True)

    ctx = np_slots * ctx_per_slot
    with open(gguf, "rb") as fh:                      # taşıyıcı kimliği künyeye girer
        h = hashlib.sha256()
        for blok in iter(lambda: fh.read(1 << 24), b""):
            h.update(blok)
    gguf_sha = h.hexdigest()
    # ⚠️ Modal'ın "A100" takma adı 40GB **ya da** 80GB verebilir (ikisi de görüldü) ve bant
    # genişlikleri 1,55 ↔ 2,03 TB/s. Kart künyeye yazılmazsa iki koşunun hız farkı yanlış
    # nedene atfedilir — bu hattın sessiz-yanlışlık sınıfı.
    kart = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                          capture_output=True, text=True).stdout.strip()
    surum = subprocess.run([binary, "--version"], capture_output=True, text=True)
    surum_s = (surum.stderr or surum.stdout).strip().splitlines()[0] if (surum.stderr or surum.stdout) else "?"

    print(f"[cp2c] künye · gguf={os.path.basename(gguf)} sha256={gguf_sha[:16]}… "
          f"-np {np_slots} · ctx {ctx} ({ctx_per_slot}/slot) · {surum_s} · kart={kart}", flush=True)

    log_yolu = os.path.join(out_dir, "llama_server.log")
    log = open(log_yolu, "w")
    srv = subprocess.Popen(
        [binary, "-m", gguf, "-ngl", "99", "-fa", "on", "--no-context-shift",
         "--cache-type-k", "q8_0", "--cache-type-v", "q8_0",
         "-c", str(ctx), "-np", str(np_slots),
         "--host", "127.0.0.1", "--port", "8080"],
        stdout=log, stderr=subprocess.STDOUT)
    try:
        for _ in range(180):                          # 6 dk: ağırlık yükleme + KV ayırma
            if srv.poll() is not None:
                print(open(log_yolu).read()[-4000:], flush=True)
                raise SystemExit(f"[cp2c] 🚫 llama-server öldü (kod {srv.returncode})")
            try:
                urllib.request.urlopen("http://127.0.0.1:8080/health", timeout=2).read()
                break
            except Exception:
                time.sleep(2)
        else:
            print(open(log_yolu).read()[-4000:], flush=True)
            raise SystemExit("[cp2c] 🚫 sunucu 360 s'te açılmadı")
        print(f"[cp2c] ✅ llama-server hazır · log {log_yolu}", flush=True)

        huniler = {}
        for tip in types:
            out = os.path.join(out_dir, f"cp2c_{tip}.jsonl")
            cmd = [sys.executable, "-u", "/root/scripts/veri_hazirlik/cp2_harvest.py",
                   "--type", tip, "--packed", packed, "--madde-path", madde,
                   "--out", out, "--seed", str(seed),
                   "--server-url", "http://127.0.0.1:8080/v1",
                   "--concurrency", str(np_slots),
                   "--gate-after-s", str(gate_after_s),
                   "--gate-max-s-per-uretim", str(gate_max_s)]
            cmd += ["--limit", str(limit)] if limit else ["--target", str(target)]
            if skip_first:
                cmd += ["--skip-first", str(skip_first)]
            print(f"\n[cp2c] ==================== {tip} ====================", flush=True)
            _run_with_commits(cmd, [data_vol], every_s=commit_every_s)
            fp = out.replace(".jsonl", "_funnel.json")
            huniler[tip] = json.load(open(fp, encoding="utf-8")) if os.path.exists(fp) else None
    finally:
        srv.terminate()
        try:
            srv.wait(timeout=30)
        except Exception:
            srv.kill()
        log.close()

    kunye = {
        "checkpoint": "CP2-c", "karar": "ADR-0047 · ADR-0045 m.4",
        "tasiyici": {"runtime": "llama.cpp/llama-server", "surum": surum_s,
                     "gguf": os.path.basename(gguf), "gguf_sha256": gguf_sha,
                     "quant": "Q4_K_M", "kv_cache": "q8_0", "flash_attn": True,
                     "context_shift": False, "np": np_slots,
                     "ctx_toplam": ctx, "ctx_slot": ctx_per_slot,
                     "gpu_etiket": GPU, "gpu_gercek": kart},
        "rejim": {"dusunce_butcesi": 1024, "cevap_butcesi": 512, "seed": seed,
                  "max_chunk_chars": 900, "kaynak": "ADR-0043 rejim değişmezi"},
        "uretim_butcesi": {"limit_per_tip": limit or None, "target_per_tip": target or None,
                           "skip_first": skip_first or None},
        "verim_kapisi": {"gate_after_s": gate_after_s, "esik_s_per_uretim": gate_max_s},
        "huni": huniler,
    }
    with open(os.path.join(out_dir, "KUNYE.json"), "w", encoding="utf-8") as f:
        json.dump(kunye, f, ensure_ascii=False, indent=2)
    data_vol.commit()
    print("\n[cp2c] KÜNYE: " + json.dumps(kunye["huni"], ensure_ascii=False), flush=True)
    print(f"[cp2c] bitti → hukuk-data:{out_dir}", flush=True)


@app.function(image=harvest_image, gpu=GPU, volumes=VOLUMES, timeout=900, retries=0)
def diag_cp2_tasiyici():
    """Taşıyıcı kapısı — hasat imajında llama-server GPU'yu GERÇEKTEN kullanıyor mu?

    Why: CP2-c duman testi 11,5 tok/s/slot verdi ve sunucu logunda tek bir CUDA satırı yoktu.
    Çıplak imajda `--list-devices` CUDA0'ı görüyor; fark pip katmanında olabilir. GPU belleği
    ayrılmıyorsa model CPU'da koşuyordur — hata vermez, yalnız 5× yavaşlar ve fatura akar.
    """
    import os
    import subprocess

    def kos(*cmd, **kw):
        print(f"\n$ {' '.join(cmd)}", flush=True)
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300, **kw)
        print((r.stdout or "") + (r.stderr or ""), flush=True)

    print("LD_LIBRARY_PATH =", os.environ.get("LD_LIBRARY_PATH"), flush=True)
    kos("/app/llama-server", "--list-devices")
    # Gerçek yükleme: 30 s sonra nvidia-smi'de bellek var mı?
    srv = subprocess.Popen(["/app/llama-server", "-m", "/data/gguf/q35-4b-q4_k_m.gguf",
                            "-ngl", "99", "-fa", "on", "-c", "8192",
                            "--host", "127.0.0.1", "--port", "8080"],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    import time
    for _ in range(20):                        # 5 dk: yükleme + KV ayırma bitene kadar izle
        time.sleep(15)
        r = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader"],
                           capture_output=True, text=True)
        print(f"  GPU bellek: {r.stdout.strip()}", flush=True)
        if srv.poll() is not None:
            break
    srv.terminate()
    cikti = srv.communicate(timeout=60)[0] or ""
    print("\n--- sunucu ilk 60 satır ---\n" + "\n".join(cikti.splitlines()[:60]), flush=True)


@app.local_entrypoint()
def diag_tasiyici():
    diag_cp2_tasiyici.remote()


@app.local_entrypoint()
def spawn_cp2c(gguf: str = "", packed: str = "", madde: str = "", out_dir: str = "",
               types: str = "m2 m2b", limit: int = 0, target: int = 0,
               np_slots: int = 32, ctx_per_slot: int = 8192,
               gate_after_s: int = 600, gate_max_s: float = 2.88, seed: int = 3407,
               commit_every_s: int = 120, skip_first: int = 0):
    """CP2-c hasadı — fire-and-forget.

    ⚠️ `modal run --detach` ZORUNLU (tuzak 6.1): efemer app, yerel giriş noktası dönünce
    kapanır ve `spawn()` ile kuyruğa atılan iş **onunla birlikte ölür** — hata vermeden.

    `--limit` ÜRETİM bütçesidir (tip başına), `--target` KABUL sayısı. CP2-c `--limit` ile
    koşar: maliyet böyle sınırlı kalır, verim ise ölçülen bir sayı olur — tersi (`--target`)
    verim tahminden kötüyse koşuyu sessizce uzatır.

    `--skip-first N`: ek tur. Çıktı yalnız KABUL edilenleri saklıyor, bu yüzden `load_done`
    "zaten denendi"yi ifade edemez — taze dizinde koşan ek tur sırayı 0'dan başlatıp aynı
    kalemleri yeniden üretir (tuzak 6.11). Önceki turun künyesindeki `denenen` sayısını ver.
    """
    _require("gguf", gguf); _require("packed", packed)
    _require("madde", madde); _require("out-dir", out_dir)
    # tuzak 3.6: yollar KONTEYNER yoludur (`hukuk-data` → /data). Yerel yol verilirse koşu,
    # GPU ayrıldıktan sonra yanar. Yerelde saniyede patla.
    for ad, yol in (("gguf", gguf), ("packed", packed), ("madde", madde), ("out-dir", out_dir)):
        if not yol.startswith("/data/"):
            raise SystemExit(f"[cp2c] 🚫 --{ad} konteyner yolu olmalı (/data/…), verilen: {yol}")
    if bool(limit) == bool(target):
        raise SystemExit("[cp2c] 🚫 --limit (üretim bütçesi) YA DA --target (kabul sayısı), biri.")
    call = harvest_cp2.spawn(gguf=gguf, packed=packed, madde=madde, out_dir=out_dir,
                             types=types.split(), limit=limit, target=target,
                             np_slots=np_slots, ctx_per_slot=ctx_per_slot,
                             gate_after_s=gate_after_s, gate_max_s=gate_max_s, seed=seed,
                             commit_every_s=commit_every_s, skip_first=skip_first)
    print(f"[cp2c] SPAWNED ✓ {call.object_id} | tipler={types} limit={limit} target={target} "
          f"skip_first={skip_first} -np {np_slots} gpu={GPU}", flush=True)
    print("[cp2c] ⚠️ 'SPAWNED' işin KOŞTUĞUNU KANITLAMAZ (tuzak 6.1). Doğrula:\n"
          f"       modal app logs hukuk-sft   ·   modal volume ls hukuk-data {out_dir}", flush=True)


# ── REJECTED HARVEST (ESKİ — v3 hattı; CP2-c bunu KULLANMAZ, bkz. harvest_cp2) ─
# Bir modeli zor near-miss tuzaklarında koşturup GERÇEK fabrikasyonları toplar (ORPO rejected).
@app.function(image=image, gpu=GPU, volumes=VOLUMES, secrets=SECRETS,
              timeout=3 * 60 * 60)
def harvest_rejected(model: str, packed: str, out: str, adapter: str | None = None,
                     target: int = 1500, batch: int = 16, max_new_tokens: int = 96):
    import sys
    cmd = [
        sys.executable, "/root/scripts/veri_hazirlik/gen_v3_rejected.py",
        "--model", model, "--packed", packed, "--out", out,
        "--oracle", "--batch", str(batch), "--target", str(target),
        "--max-new-tokens", str(max_new_tokens),
    ]
    if adapter:
        cmd += ["--adapter", adapter]
    _run_with_commits(cmd, [data_vol, hf_cache], every_s=300)
    print(f"[modal] harvest bitti → hukuk-data:{out}", flush=True)


# ── Yerel giriş noktaları ─────────────────────────────────────────────────────
# ⚠️ HEPSİ spawn() kullanır, remote() DEĞİL (ADR-0008): remote() client'a bağlı BEKLER →
# PC/WSL kapanınca client SIGTERM alıp Modal'a cancel yollar (bu 4 koşuyu öldürdü).
# spawn() job'ı kuyruğa atıp hemen döner — client kapanması işi ETKİLEMEZ.

@app.local_entrypoint()
def spawn_sft(model: str = "", data: str = "", run_name: str = "r1",
              user_part: str = "", assistant_part: str = "",
              epochs: float = 1.0, smoke: bool = False,
              lr: float = 0.0, lora_r: int = 0, lora_alpha: int = 0,
              warmup_ratio: float = 0.0, no_system: bool = False,
              bf16_base: bool = False, target_modules: str = "",
              lora_dropout: float = -1.0, no_grad_checkpoint: bool = False,
              batch: int = 0, grad_accum: int = 0):
    """QLoRA SFT — fire-and-forget. Önce --smoke (para-kapısı), sonra tam koşu.

    --user-part / --assistant-part: base'in chat şablonundaki turn işaretleri.
    ⚠️ Bunlar base'e göre DEĞİŞİR ve yanlışsa responses-only maskeleme sessizce çalışmaz
    (loss tüm diziden akar = eğitim çöpe gider). Doğrusunu `diag_chat_template.sh` ile
    /apply-template render'ından oku. train_sft.py ayrıca render'a karşı assert eder.
    """
    _require("model", model); _require("data", data)
    _require("user-part", user_part); _require("assistant-part", assistant_part)
    extra = []
    if no_system:            # veri system prompt'unu zaten taşıyorsa çift-system'i önle
        extra += ["--no-system"]
    if lr:                   # ⚠️ lr ≥ 3e-4 train_sft.py'de kilitli (abstention çöküşü rejimi)
        extra += ["--lr", str(lr)]
    if lora_r:
        extra += ["--lora-r", str(lora_r)]
    if lora_alpha:
        extra += ["--lora-alpha", str(lora_alpha)]
    if warmup_ratio:
        extra += ["--warmup-ratio", str(warmup_ratio)]
    if bf16_base:            # ⚠️ ADR-0031 birincil: bf16 donuk taban + LoRA (QLoRA değil)
        extra += ["--bf16-base"]
    if target_modules:       # ⚠️ Qwen3.5 VLM: all-linear görüntü kulesine takar (#39) → metin kulesi listesi
        extra += ["--target-modules", *target_modules.split()]
    # ⚠️ ADR-0033 hız kaldıraçları. `lora_dropout` varsayılanı -1.0 = "dokunma" (script'in 0.05'i
    # kalır); 0.0 geçerli bir DEĞER olduğu için `if lora_dropout:` yazılamaz — 0.0 falsy'dir ve
    # bayrak sessizce yok sayılırdı. Tam da kaçınmaya çalıştığımız sessiz-yok-sayma sınıfı.
    if lora_dropout >= 0:
        extra += ["--lora-dropout", str(lora_dropout)]
    if no_grad_checkpoint:   # yalnız A100/H100 — yerel 12 GB kartta OOM
        extra += ["--no-grad-checkpoint"]
    # ⚠️ batch × grad_accum ÇARPIMI SABİT TUTULMALI (etkin batch = 16, reçete sabiti).
    # batch=1 varsayılanı YEREL 12 GB kartın kuralıydı; A100'de GPU boş çalışıyor.
    # İkisi birlikte verilir ki çarpım gözle denetlenebilsin.
    if batch:
        extra += ["--batch", str(batch)]
    if grad_accum:
        extra += ["--grad-accum", str(grad_accum)]
    if bool(batch) != bool(grad_accum):
        raise SystemExit("[modal] 🚫 --batch ve --grad-accum BİRLİKTE verilir "
                         "(etkin batch = çarpımları; tek başına vermek onu sessizce kaydırır).")

    parts = dict(user_part=user_part, assistant_part=assistant_part)
    if smoke:
        print(f"[modal] SMOKE: 50 step (config+loss doğrulama) · gpu={GPU}", flush=True)
        call = train.spawn(model=model, data_path=data, run_name=f"{run_name}-smoke",
                           epochs=1.0, max_steps=50, extra_args=extra, **parts)
    else:
        call = train.spawn(model=model, data_path=data, run_name=run_name,
                           epochs=epochs, extra_args=extra, **parts)
    print(f"[modal] SPAWNED ✓ {call.object_id} | model={model} data={data} "
          f"run={run_name} epochs={epochs} gpu={GPU} smoke={smoke}", flush=True)
    print(f"[modal] Bağımsız koşuyor. İzle: modal app logs hukuk-sft | "
          f"Bitince: modal volume get hukuk-outputs /{run_name} ./outputs/{run_name}", flush=True)


@app.local_entrypoint()
def spawn_orpo(model: str = "", data: str = "", run_name: str = "orpo1",
               adapter: str = "", epochs: float = 3.0, smoke: bool = False,
               beta: float = 0.1, lr: float = 1e-5, grad_accum: int = 64,
               save_steps: int = 100, bf16_base: bool = False,
               lora_dropout: float = -1.0, target_modules: str = ""):
    """ORPO tercih öğrenmesi — fire-and-forget.

    --adapter verilirse o turun kazanımı taşınır (continuation); boşsa base'e taze adapter.
    İzlenecek metrik: nll_loss trendi = forget-vekili (tırmanırsa grounding riski).

    ⚠️ τ_abstention KOLU olarak koşarken: `--adapter` VERİLMEZ (taze = ham base'den) ve
    `--bf16-base --lora-dropout 0.05 --target-modules '<τ_g ile aynı liste>'` verilir.
    Aksi hâlde τ_g ile merge edilemez — bkz. docs/open_questions.md #13.

    ⚠️ `epochs` varsayılanı 1.0 DEĞİL 3.0 (2026-07-28 kararı). Why: 1.741 çift ÷ etkin batch 64
    = epoch başına yalnız **27 optimizer adımı**. 12B hattında ORPO continuation'dı, dürtmesi
    yetiyordu; HAM BASE'den yeni davranış öğretmek 27 adımda lr 1e-5 ile olmuyor. 3 epoch = 82
    adım. Kıyas: τ_grounding 1.083 adım koşuyor.
    """
    _require("model", model); _require("data", data)
    common = dict(bf16_base=bf16_base, lora_dropout=lora_dropout,
                  target_modules=target_modules)
    if smoke:
        print(f"[modal] ORPO SMOKE: 50 step (format+loss+OOM doğrulama) · gpu={GPU}", flush=True)
        call = train_orpo.spawn(model=model, data_path=data, run_name=f"{run_name}-smoke",
                                adapter=adapter or None, epochs=1.0, max_steps=50,
                                beta=beta, lr=lr, grad_accum=grad_accum, **common)
    else:
        call = train_orpo.spawn(model=model, data_path=data, run_name=run_name,
                                adapter=adapter or None, epochs=epochs, beta=beta,
                                lr=lr, grad_accum=grad_accum, save_steps=save_steps, **common)
    print(f"[modal] ORPO SPAWNED ✓ {call.object_id} | model={model} "
          f"adapter={adapter or '(taze)'} beta={beta} lr={lr} ga={grad_accum} gpu={GPU}", flush=True)


@app.local_entrypoint()
def spawn_harvest(model: str = "", packed: str = "", out: str = "", adapter: str = "",
                  target: int = 1500, batch: int = 16, max_new_tokens: int = 96):
    """Fabrikasyon (rejected) toplama — inference, ucuz. Bitince yerele çek:
      modal volume get hukuk-data <out> ./data/...
    """
    _require("model", model); _require("packed", packed); _require("out", out)
    call = harvest_rejected.spawn(model=model, packed=packed, out=out,
                                  adapter=adapter or None, target=target,
                                  batch=batch, max_new_tokens=max_new_tokens)
    print(f"[modal] HARVEST SPAWNED ✓ {call.object_id} | target={target} gpu={GPU}", flush=True)


# ── B10 HASADI: aşırı-red toplama (Görev 3 pilot · Görev 4 üretim) ────────────
# Taşıyıcı gerekçesi `harvest_cp2` ile AYNI (ADR-0047 m.2): dağıtılan kiple hasat.
# `b10_hasat.py`'nin `DEV_YOLLARI`'sı GÖRELİ ve CLI argümanı yok — sızıntı süzgeci
# kaynağı bulunamazsa `FileNotFoundError` atar (b10_hasat.py:129). Bu yüzden
# `data/eval` imaja gömülür ve süreç `/root`ta koşar.
b10_image = harvest_image.add_local_dir("data/eval", remote_path="/root/data/eval")


@app.function(image=b10_image, gpu=GPU, volumes=VOLUMES, timeout=12 * 60 * 60)
def harvest_b10(gguf: str, havuz: str, out_dir: str, np_list: list[int],
                limit: int = 0, target: int = 0, ctx_per_slot: int = 8192,
                seed: int = 3407, commit_every_s: int = 120, notu: str = ""):
    """B10 aşırı-red hasadı — `-np` kolu başına bir koşu, sunucu kol arası yeniden kurulur.

    Birden fazla `-np` verilirse KARAR-6'nın kıyası üretilir: aynı kart, aynı seed, aynı
    kalemler; değişen YALNIZ `-np`. ⛔ Bu fonksiyon HÜKÜM KURMAZ — sayıları yazar.
    """
    import hashlib
    import json
    import os
    import shutil
    import subprocess
    import sys
    import time
    import urllib.request

    # ── VERİ KAPISI: GPU ayrılmışken patlamak pahalı, önce dosyalar (tuzak 6.2) ──
    for etiket, yol in (("gguf", gguf), ("havuz", havuz)):
        if not os.path.isfile(yol):
            raise SystemExit(f"[b10] 🚫 {etiket} yok: {yol} — volume'a yüklendi mi?")
    os.chdir("/root")                      # DEV_YOLLARI göreli — cwd BURASI olmak zorunda
    for yol in ("data/eval/dev/core_hard.jsonl", "data/eval/canon/core_hard.jsonl"):
        if not os.path.isfile(yol):
            raise SystemExit(f"[b10] 🚫 sızıntı süzgeci kaynağı imajda yok: /root/{yol}")
    binary = shutil.which("llama-server") or "/app/llama-server"
    if not os.path.isfile(binary):
        raise SystemExit(f"[b10] 🚫 llama-server bulunamadı ({binary}) — imaj değişti mi?")
    os.makedirs(out_dir, exist_ok=True)

    with open(gguf, "rb") as fh:                      # taşıyıcı kimliği künyeye girer
        h = hashlib.sha256()
        for blok in iter(lambda: fh.read(1 << 24), b""):
            h.update(blok)
    gguf_sha = h.hexdigest()
    kart = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                          capture_output=True, text=True).stdout.strip()
    # Why: `--version` probu da ikilinin kütüphanesine muhtaç; düzeltilmiş env olmadan
    # çağrılırsa künyeye sürüm yerine linker hatası yazılır (ölçüldü 2026-09-05, pilot koşusu).
    bin_dir = os.path.dirname(binary) or "/app"
    srv_env = dict(os.environ)
    srv_env["LD_LIBRARY_PATH"] = bin_dir + os.pathsep + srv_env.get("LD_LIBRARY_PATH", "")
    surum = subprocess.run([binary, "--version"], capture_output=True, text=True,
                           cwd=bin_dir, env=srv_env)
    surum_s = (surum.stderr or surum.stdout).strip().splitlines()[0] if (surum.stderr or surum.stdout) else "?"
    print(f"[b10] künye · gguf={os.path.basename(gguf)} sha256={gguf_sha[:16]}… "
          f"kollar -np {np_list} · {surum_s} · kart={kart}", flush=True)

    # Sunucu ikilinin dizininde koşar (cwd /root'ta, sızıntı süzgecinin göreli yolu için).
    kollar = {}
    for np_slots in np_list:
        ctx = np_slots * ctx_per_slot
        etiket = f"np{np_slots}"
        out = os.path.join(out_dir, f"b10_{etiket}.jsonl")
        log_yolu = os.path.join(out_dir, f"llama_server_{etiket}.log")
        log = open(log_yolu, "w")
        srv = subprocess.Popen(
            [binary, "-m", gguf, "-ngl", "99", "-fa", "on", "--no-context-shift",
             "--cache-type-k", "q8_0", "--cache-type-v", "q8_0",
             "-c", str(ctx), "-np", str(np_slots),
             "--host", "127.0.0.1", "--port", "8080"],
            stdout=log, stderr=subprocess.STDOUT, cwd=bin_dir, env=srv_env)
        try:
            for _ in range(180):                      # 6 dk: ağırlık yükleme + KV ayırma
                if srv.poll() is not None:
                    print(open(log_yolu).read()[-4000:], flush=True)
                    raise SystemExit(f"[b10] 🚫 llama-server öldü (kod {srv.returncode}) · -np {np_slots}")
                try:
                    urllib.request.urlopen("http://127.0.0.1:8080/health", timeout=2).read()
                    break
                except Exception:
                    time.sleep(2)
            else:
                print(open(log_yolu).read()[-4000:], flush=True)
                raise SystemExit(f"[b10] 🚫 sunucu 360 s'te açılmadı · -np {np_slots}")
            print(f"\n[b10] ========== -np {np_slots} · ctx {ctx} ==========", flush=True)

            cmd = [sys.executable, "-u", "/root/scripts/veri_hazirlik/b10_hasat.py",
                   "--havuz", havuz, "--out", out, "--seed", str(seed),
                   "--server-url", "http://127.0.0.1:8080/v1",
                   "--concurrency", str(np_slots),
                   "--not", f"Modal · kart={kart} · -np {np_slots} · gguf_sha={gguf_sha[:16]} · {notu}"]
            cmd += ["--limit", str(limit)] if limit else ["--target", str(target)]
            t0 = time.time()
            _run_with_commits(cmd, [data_vol], every_s=commit_every_s)
            sure = time.time() - t0
        finally:
            srv.terminate()
            try:
                srv.wait(timeout=30)
            except Exception:
                srv.kill()
            log.close()

        kp = out.replace(".jsonl", "_KUNYE.json")
        kollar[etiket] = {"kunye": json.load(open(kp, encoding="utf-8")) if os.path.exists(kp) else None,
                          "duvar_saati_s": round(sure, 1), "np": np_slots, "ctx": ctx,
                          "out": out}

    # ── KARAR-6 kıyası — SAYILAR, hüküm YOK ──────────────────────────────────
    kiyas = None
    if len(np_list) > 1:
        def _yukle(yol):
            with open(yol, encoding="utf-8") as f:
                return {json.loads(l)["id"]: json.loads(l)["rejected"]
                        for l in f if l.strip()}
        adlar = [f"np{n}" for n in np_list]
        kumeler = {ad: _yukle(kollar[ad]["out"]) for ad in adlar}
        a, b = adlar[0], adlar[1]
        A, B = set(kumeler[a]), set(kumeler[b])
        kesisim = A & B
        birebir = sum(1 for i in kesisim if kumeler[a][i] == kumeler[b][i])
        kiyas = {
            "kollar": [a, b],
            f"n_kabul_{a}": len(A), f"n_kabul_{b}": len(B),
            "n_kesisim": len(kesisim), f"yalniz_{a}": len(A - B), f"yalniz_{b}": len(B - A),
            "jaccard": round(len(kesisim) / len(A | B), 4) if (A | B) else None,
            "cevap_metni_birebir_ayni": birebir,
            "kesisimde_metin_farkli": len(kesisim) - birebir,
            "not": "⛔ Hüküm KURULMADI — yorumu insan yapar (KARAR-6).",
        }
        with open(os.path.join(out_dir, "b10_np_karsilastirma.json"), "w", encoding="utf-8") as f:
            json.dump(kiyas, f, ensure_ascii=False, indent=2)

    kunye = {
        "gorev": "B10 hasadı", "karar": "KARAR-6 · ADR-0047 m.2 (taşıyıcı birebir)",
        "tasiyici": {"runtime": "llama.cpp/llama-server", "surum": surum_s,
                     "gguf": os.path.basename(gguf), "gguf_sha256": gguf_sha,
                     "quant": "Q4_K_M", "kv_cache": "q8_0", "flash_attn": True,
                     "context_shift": False, "ctx_slot": ctx_per_slot,
                     "gpu_etiket": GPU, "gpu_gercek": kart},
        "rejim": {"dusunce_butcesi": 1024, "cevap_butcesi": 512, "seed": seed,
                  "kaynak": "ADR-0043 rejim değişmezi"},
        "butce": {"limit": limit or None, "target": target or None},
        "kollar": kollar, "np_karsilastirma": kiyas, "not": notu,
    }
    with open(os.path.join(out_dir, "KUNYE.json"), "w", encoding="utf-8") as f:
        json.dump(kunye, f, ensure_ascii=False, indent=2)
    data_vol.commit()
    for ad, k in kollar.items():
        ky = k["kunye"] or {}
        print(f"[b10] {ad}: denenen={ky.get('denenen')} kabul={ky.get('kabul')} "
              f"oran={ky.get('kabul_orani')} · {k['duvar_saati_s']} s", flush=True)
    if kiyas:
        print("[b10] KIYAS: " + json.dumps(kiyas, ensure_ascii=False), flush=True)
    print(f"[b10] bitti → hukuk-data:{out_dir}", flush=True)


@app.local_entrypoint()
def spawn_b10(gguf: str = "", havuz: str = "", out_dir: str = "", np_list: str = "",
              limit: int = 0, target: int = 0, ctx_per_slot: int = 8192,
              seed: int = 3407, commit_every_s: int = 120, notu: str = ""):
    """B10 hasadı — fire-and-forget.

    ⚠️ `modal run --detach` ZORUNLU (tuzak 6.1): efemer app, yerel giriş noktası dönünce
    kapanır ve `spawn()` ile kuyruğa atılan iş **onunla birlikte ölür** — hata vermeden.
    """
    _require("gguf", gguf); _require("havuz", havuz)
    _require("out-dir", out_dir); _require("np-list", np_list)
    # tuzak 3.6: yollar KONTEYNER yoludur (`hukuk-data` → /data). Yerelde saniyede patla.
    for ad, yol in (("gguf", gguf), ("havuz", havuz), ("out-dir", out_dir)):
        if not yol.startswith("/data/"):
            raise SystemExit(f"[b10] 🚫 --{ad} konteyner yolu olmalı (/data/…), verilen: {yol}")
    if bool(limit) == bool(target):
        raise SystemExit("[b10] 🚫 --limit (üretim bütçesi) YA DA --target (kabul sayısı), biri.")
    kollar = [int(x) for x in np_list.split()]
    if len(kollar) > 2:
        raise SystemExit("[b10] 🚫 en fazla iki kol — kıyas ikili kurulur.")
    call = harvest_b10.spawn(gguf=gguf, havuz=havuz, out_dir=out_dir, np_list=kollar,
                             limit=limit, target=target, ctx_per_slot=ctx_per_slot,
                             seed=seed, commit_every_s=commit_every_s, notu=notu)
    print(f"[b10] kuyruğa atıldı · call_id={call.object_id} · kollar -np {kollar}")
    print(f"[b10] izle: modal app logs {app.name}   ·   çıktı: hukuk-data:{out_dir}")
