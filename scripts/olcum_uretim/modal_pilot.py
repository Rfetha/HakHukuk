"""F0.16 — ölçüm kartı pilotu, Modal (ADR-0097 m.3 · ADR-0098 m.3 · ADR-0102).

Bir kart tipinde iki makine açar (eş zamanlı iki konteyner → iki ayrı GPU): ilk makine 80 DEV cevabını iki kez,
ikinci makine bir kez üretir. Ölçülenler: cevap başına süre (→ maliyet) · aynı makinede ve makineler arasında
birebir aynı cevap oranı (`makine_kapisi.py`) · kesik oranı. İlk makinenin ilk tekrarı tipin REFERANS
cevaplarıdır (makine geçiş kapısı, F0.6'nın girdisi).

Rejimin tamamı tek yerden gelir, burada yalnız makine açılır:
  sunucu   `ghcr.io/ggml-org/llama.cpp:server-cuda-b10902`, bayraklar `docker/compose.yaml`'dan (olcum_karti)
  model    yayımlanmış GGUF, `hakhukuk.dagitim.indir.indir_model` (sabit revizyon + bayt + sha256 kapısı)
  bağlam   `data/eval/dev/baglam/h1-k10.json` (dondurulmuş; sha256 yerelde hesaplanır, konteynerde sınanır)
  üretim   `gen_eval_grounded.py`, `olcum_karti.REJIM` (h1, 1024 + 512, seed 3407, 900 kırpma)
Konteynere hiçbir anahtar gitmez (secret bağlanmaz; GGUF deposu herkese açık).

Kullanım (repo kökünden; para harcar, kullanıcı onayıyla):
  modal run --detach scripts/olcum_uretim/modal_pilot.py::spawn_pilot --tip A10
  # bitince:
  modal volume get hukuk-outputs /f016-pilot outputs/eval/f0/f016-pilot
"""
import hashlib
import os

import modal

SUNUCU_IMAJI = "ghcr.io/ggml-org/llama.cpp:server-cuda-b10902"   # ADR-0102 m.1; `latest` yasak
VERI = "data/eval/dev/core_hard.jsonl"
DONMUS = "data/eval/dev/baglam/h1-k10.json"
CIKTI_KOK = "/outputs/f016-pilot"
# Modal'ın saatlik liste fiyatı (modal.com/pricing, okundu 2026-10-15, #82) — maliyet künyede bundan türer.
SAATLIK_USD = {"T4": 0.59, "L4": 0.80, "A10": 1.10, "L40S": 1.95, "A100-40GB": 2.10}

app = modal.App("hakhukuk-olcum-pilot")
out_vol = modal.Volume.from_name("hukuk-outputs")

image = (
    modal.Image.from_registry(SUNUCU_IMAJI, add_python="3.11")
    # İmajın ENTRYPOINT'i `/app/llama-server`; temizlenmezse Modal'ın çalıştırıcısı ona argüman olur.
    .entrypoint([])
    # Üretim HTTP taşıyıcısıyla koşar: torch/unsloth gerekmez (gen_eval_grounded içe aktarmıyor).
    .pip_install("openai==2.41.0", "pyyaml==6.0.3", "huggingface_hub==1.18.0")
    .env({"PYTHONUNBUFFERED": "1"})
    .add_local_dir("scripts", remote_path="/root/scripts")
    .add_local_dir("hakhukuk", remote_path="/root/hakhukuk")
    .add_local_file("docker/compose.yaml", remote_path="/root/docker/compose.yaml")
    .add_local_file(VERI, remote_path=f"/root/{VERI}")
    .add_local_file(DONMUS, remote_path=f"/root/{DONMUS}")
)


def _sha256(yol: str) -> str:
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for parca in iter(lambda: f.read(1 << 20), b""):
            h.update(parca)
    return h.hexdigest()


@app.function(image=image, gpu="A10", volumes={"/outputs": out_vol}, timeout=3 * 60 * 60, retries=0)
def pilot_makine(tip: str, makine: str, tekrar: int, baglam_sha: str, hesap: str) -> dict:
    import json
    import subprocess
    import sys
    import time
    import urllib.request

    sys.path[:0] = ["/root/scripts/olcum_uretim", "/root/scripts/puanlama", "/root"]
    import olcum_karti as ok
    from hakhukuk.dagitim.indir import indir_model
    from part_dosya import tamamlanmis_jsonl

    dizin = f"{CIKTI_KOK}/{tip}/{makine}"
    os.makedirs(dizin, exist_ok=True)
    # ── VERİ KAPISI: GPU'da iş başlamadan (tuzak 6.2) ────────────────────────────────────
    if _sha256(f"/root/{DONMUS}") != baglam_sha:
        raise SystemExit(f"[pilot] 🚫 dondurulmuş bağlam yerelde hesaplanan sha256'yla aynı değil")
    gguf = str(indir_model("/tmp/model"))
    kart = subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version,uuid,memory.total",
                           "--format=csv,noheader"], capture_output=True, text=True).stdout.strip()
    surum = subprocess.run([ok.SUNUCU_IKILISI, "--version"], capture_output=True, text=True)

    gunluk_yolu = f"{dizin}/llama_server.log"
    komut = ok.sunucu_komutu("/root/docker/compose.yaml", gguf, port=8080)
    gunluk = open(gunluk_yolu, "w")
    srv = subprocess.Popen(komut, stdout=gunluk, stderr=subprocess.STDOUT)
    kosular = []
    try:
        for _ in range(180):
            if srv.poll() is not None:
                raise SystemExit(f"[pilot] 🚫 llama-server öldü (kod {srv.returncode}): "
                                 + open(gunluk_yolu).read()[-3000:])
            try:
                urllib.request.urlopen("http://127.0.0.1:8080/health", timeout=2).read()
                break
            except Exception:
                time.sleep(2)
        else:
            raise SystemExit("[pilot] 🚫 sunucu 360 s'te açılmadı")
        # Tuzak 7.8: port dinliyor olması kanıt değil — hangi GGUF'un servis edildiği okunur.
        modeller = json.loads(urllib.request.urlopen("http://127.0.0.1:8080/v1/models", timeout=10).read())
        servis = modeller["data"][0]["id"]
        if os.path.basename(gguf) not in servis:
            raise SystemExit(f"[pilot] 🚫 sunucu başka bir model servis ediyor: {servis}")
        kosan_komut = open(f"/proc/{srv.pid}/cmdline").read().split("\0")[:-1]

        for t in range(1, tekrar + 1):
            etiket = f"h1_tgta_v1_{tip}_{makine}_t{t}"
            t0 = time.time()
            r = subprocess.run(ok.uretim_komutu(sys.executable, "/root/scripts/olcum_uretim/gen_eval_grounded.py",
                                                "http://127.0.0.1:8080/v1", veri=f"/root/{VERI}",
                                                donmus_baglam=f"/root/{DONMUS}", etiket=etiket,
                                                cikti_dizini=dizin), cwd="/root")
            sure = time.time() - t0
            if r.returncode != 0:
                raise SystemExit(f"[pilot] 🚫 {etiket} üretimi başarısız (kod {r.returncode})")
            satirlar = tamamlanmis_jsonl(f"{dizin}/{etiket}_detail.jsonl")
            tok = [x["completion_tokens"] for x in satirlar if x.get("completion_tokens")]
            kosular.append({"etiket": etiket, "sure_s": round(sure, 1), "s_cevap": round(sure / len(satirlar), 2),
                            "ort_completion_tokens": round(sum(tok) / len(tok), 1) if tok else None,
                            "gecerlilik": ok.gecerlilik(satirlar)})
            out_vol.commit()
    finally:
        srv.terminate()
        try:
            srv.wait(timeout=30)
        except Exception:
            srv.kill()
        gunluk.close()

    kimlik = ok.sunucu_kimligi((surum.stdout or "") + (surum.stderr or ""), open(gunluk_yolu).read())
    saatlik = SAATLIK_USD.get(tip)
    kunye = {
        "is": "F0.16 ölçüm kartı pilotu (ADR-0097 m.3, ADR-0102)",
        "platform": {"ad": "Modal", "hesap": hesap, "tip": tip, "saatlik_usd": saatlik,
                     "ortam": {k: v for k, v in os.environ.items() if k.startswith("MODAL_")
                               and not any(y in k for y in ("TOKEN", "SECRET", "KEY"))}},
        "makine": {"ad": makine, "nvidia_smi": kart},
        "sunucu": {"imaj": SUNUCU_IMAJI, **kimlik, "kosan_komut": kosan_komut, "v1_models": servis},
        "model": {"gguf": os.path.basename(gguf), "sha256": _sha256(gguf)},
        "baglam": {"dosya": DONMUS, "sha256": baglam_sha},
        "rejim": ok.REJIM,
        "kosular": [dict(k, usd_cevap=round(k["s_cevap"] * saatlik / 3600, 5) if saatlik else None)
                    for k in kosular],
    }
    with open(f"{dizin}/KUNYE.json", "w", encoding="utf-8") as f:
        json.dump(kunye, f, ensure_ascii=False, indent=2)
    out_vol.commit()
    print(json.dumps(kunye, ensure_ascii=False, indent=2), flush=True)
    return kunye


@app.local_entrypoint()
def spawn_pilot(tip: str = ""):
    if not tip:
        raise SystemExit("[pilot] 🚫 --tip zorunlu (ADR-0102: A10)")
    import sys
    sys.path.insert(0, "scripts/egitim")
    from modal_train import _baslatan_hesap   # ADR-0101 m.4: hesap profilden, elle yazılmaz

    baglam_sha = _sha256(DONMUS)
    hesap = _baslatan_hesap()
    f = pilot_makine.with_options(gpu=tip)
    # İki çağrı eş zamanlı açılır → iki ayrı konteyner, iki ayrı GPU (künyede nvidia-smi uuid'leri).
    c1 = f.spawn(tip, "m1", 2, baglam_sha, hesap)
    c2 = f.spawn(tip, "m2", 1, baglam_sha, hesap)
    print(f"[pilot] SPAWNED ✓ tip={tip} hesap={hesap} bağlam={baglam_sha[:12]}… · m1 {c1.object_id} (×2) · "
          f"m2 {c2.object_id} (×1)\n  bitince: modal volume get hukuk-outputs /f016-pilot "
          f"outputs/eval/f0/f016-pilot", flush=True)
