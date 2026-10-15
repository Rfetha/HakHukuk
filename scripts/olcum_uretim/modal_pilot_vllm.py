"""F0.16 vLLM pilotu, Modal A10 — vLLM ile toplu üretim ölçümü, iki ağırlıkla (spec 2026-10-15).

Ağırlıklar:
  q4-acilmis    yayımlanmış Q4_K_M GGUF, konteynerde `gguf_hf_cevir.py` ile bf16 HF biçimine açılır (aynı sayılar)
  bf16-orijinal eğitimin sıkıştırılmamış çıktısı (`models/merged/tgta_v1`), dizüstünden hacme yüklenmiştir
vLLM'in GGUF eklentisi Qwen3.5'i tanımıyor (`Unknown gguf model_type: qwen3_5`, 2026-10-15); GGUF doğrudan okunmaz.
Her iki klasör de içerik sha256'sıyla yerelde doğrulanmış kayda bağlıdır (CEVIRI_KUNYE.json, bf16_manifest.json).

Aşamalar (her biri ayrı onayla):
  kontrol  vLLM açılıyor mu? Düşünce hangi alan adıyla geliyor? 8 soru tek tek ↔ aynı anda: hız, cevap eşitliği (G1, G4)
  pilot    80 soru, vLLM'de iki üretim koşusu (G1, G2 ve puanlama için cevaplar)

Konteynere hiçbir anahtar gitmez (secret bağlanmaz; GGUF deposu herkese açık).

Kullanım (repo kökünden; para harcar, kullanıcı onayıyla):
  modal run --detach scripts/olcum_uretim/modal_pilot_vllm.py::baslat --asama kontrol --agirlik bf16-orijinal
  modal run --detach scripts/olcum_uretim/modal_pilot_vllm.py::baslat --asama pilot --agirlik q4-acilmis
  modal volume get hukuk-outputs /f016-vllm-pilot/A10 outputs/eval/f0/f016-vllm-pilot/A10
"""
import hashlib
import os

import modal

VLLM_SURUMU = "0.30.0"        # PyPI 2026-09-22; varsayılan tekerlek CUDA 13.0
HF_HUB_SURUMU = "1.33.0"      # PyPI 2026-09-24; vLLM 0.30.0 >=1.31.0 ister
TABAN_IMAJ = "nvidia/cuda:13.0.1-devel-ubuntu24.04"
VERI = "data/eval/dev/core_hard.jsonl"
DONMUS = "data/eval/dev/baglam/h1-k10.json"
TOKENIZER = "models/merged/tgta_v1"
TOKENIZER_DOSYALARI = ("tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt",
                       "chat_template.jinja", "config.json")
CEVIRI_KUNYE_YEREL = "outputs/eval/f0/f016-vllm-pilot/cevirme/CEVIRI_KUNYE.json"
BF16_MANIFEST_YEREL = "outputs/eval/f0/f016-vllm-pilot/bf16_manifest.json"
AGIRLIKLAR = ("q4-acilmis", "bf16-orijinal")
CIKTI_KOK = "/outputs/f016-vllm-pilot"
SAATLIK_USD = {"A10": 1.10}   # modal.com/pricing, okundu 2026-10-15 (#82)
ES_ZAMANLI = 32               # aynı anda gönderilen istek; sunucuda --max-num-seqs ile aynı
PORT = 8000

app = modal.App("hakhukuk-olcum-pilot-vllm")
out_vol = modal.Volume.from_name("hukuk-outputs")

image = (
    modal.Image.from_registry(TABAN_IMAJ, add_python="3.12")
    .pip_install(f"vllm=={VLLM_SURUMU}", "openai==2.41.0", "pyyaml==6.0.3", f"huggingface_hub=={HF_HUB_SURUMU}",
                 "gguf>=0.17.0")
    .env({"PYTHONUNBUFFERED": "1"})
    .add_local_dir("scripts", remote_path="/root/scripts")
    .add_local_dir("hakhukuk", remote_path="/root/hakhukuk")
    .add_local_file(VERI, remote_path=f"/root/{VERI}")
    .add_local_file(DONMUS, remote_path=f"/root/{DONMUS}")
    .add_local_file(CEVIRI_KUNYE_YEREL, remote_path="/root/cevirme_kunye.json")
    .add_local_file(BF16_MANIFEST_YEREL, remote_path="/root/bf16_manifest.json")
)
for _dosya in TOKENIZER_DOSYALARI:
    image = image.add_local_file(f"{TOKENIZER}/{_dosya}", remote_path=f"/root/tok/{_dosya}")


def _sha256(yol: str) -> str:
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for parca in iter(lambda: f.read(1 << 20), b""):
            h.update(parca)
    return h.hexdigest()


def _paket_surumu(ad: str):
    from importlib import metadata
    try:
        return metadata.version(ad)
    except metadata.PackageNotFoundError:
        return None


def _hf_klasoru(gguf: str) -> str:
    """GGUF → HF klasörü (hacimde önbellekli). Her tensörün sha256'sı yerelde doğrulanmış çeviriyle aynı olmalı."""
    import json
    import subprocess
    import sys
    hedef = f"{CIKTI_KOK}/hf_q4km"
    kayit = f"{hedef}/CEVIRI_KUNYE.json"
    if not os.path.exists(kayit):
        subprocess.run([sys.executable, "/root/scripts/olcum_uretim/gguf_hf_cevir.py", "--gguf", gguf,
                        "--yapilandirma-dizini", "/root/tok", "--cikti", hedef], check=True)
        out_vol.commit()
    beklenen = {t["hf"]: t["sha256"] for t in json.load(open("/root/cevirme_kunye.json", encoding="utf-8"))["tensorler"]}
    elde = {t["hf"]: t["sha256"] for t in json.load(open(kayit, encoding="utf-8"))["tensorler"]}
    if elde != beklenen:
        farkli = sorted(k for k in beklenen if elde.get(k) != beklenen[k])[:5]
        raise RuntimeError(f"çeviri yerelde doğrulanmışla aynı değil: {len(elde)} ↔ {len(beklenen)} tensör, "
                           f"farklı ilk beşi {farkli}")
    return hedef


def _bf16_klasoru() -> str:
    """Hacimdeki orijinal bf16 klasörü; her dosyanın sha256'sı yerel manifestle aynı olmalı (bf16_yukle.py)."""
    import json
    import sys
    sys.path[:0] = ["/root/scripts/olcum_uretim"]
    import bf16_yukle
    hedef = f"{CIKTI_KOK}/bf16"
    beklenen = json.load(open("/root/bf16_manifest.json", encoding="utf-8"))
    fark = bf16_yukle.farklar(beklenen, bf16_yukle.manifest(hedef, adlar=list(beklenen["dosyalar"])))
    if fark:
        raise RuntimeError("hacimdeki bf16 yerel manifestle aynı değil: " + "; ".join(fark[:5]))
    return hedef


def _model_klasoru(agirlik: str):
    """→ (vLLM'in okuyacağı klasör, künyedeki model kaydı)."""
    if agirlik == "q4-acilmis":
        from hakhukuk.dagitim.indir import indir_model
        gguf = str(indir_model("/tmp/model"))
        return _hf_klasoru(gguf), {"gguf": os.path.basename(gguf), "gguf_sha256": _sha256(gguf)}
    if agirlik == "bf16-orijinal":
        return _bf16_klasoru(), {"bf16_manifest_sha256": _sha256("/root/bf16_manifest.json")}
    raise ValueError(f"bilinmeyen ağırlık: {agirlik} (beklenen {AGIRLIKLAR})")


def _sunucu_ac(model_dizini: str, gunluk_yolu: str):
    """vLLM sunucusunu açar, /health bekler → (süreç, koşan komut). Açılamazsa günlüğün sonuyla durur."""
    import subprocess
    import time
    import urllib.request
    komut = ["vllm", "serve", model_dizini, "--served-model-name", "local", "--dtype", "bfloat16",
             "--max-model-len", "8192", "--max-num-seqs", str(ES_ZAMANLI), "--reasoning-parser", "qwen3",
             "--seed", "3407", "--host", "127.0.0.1", "--port", str(PORT)]
    gunluk = open(gunluk_yolu, "w")
    srv = subprocess.Popen(komut, stdout=gunluk, stderr=subprocess.STDOUT)
    for _ in range(300):
        if srv.poll() is not None:
            raise RuntimeError(f"vllm öldü (kod {srv.returncode}): " + open(gunluk_yolu).read()[-3000:])
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/health", timeout=2).read()
            return srv, open(f"/proc/{srv.pid}/cmdline").read().split("\0")[:-1]
        except Exception:
            time.sleep(2)
    srv.terminate()
    raise RuntimeError("vllm 600 s'te açılmadı: " + open(gunluk_yolu).read()[-3000:])


def _sunucu_kapat(srv):
    srv.terminate()
    try:
        srv.wait(timeout=30)
    except Exception:
        srv.kill()


def _ortak_kunye(tip: str, hesap: str) -> dict:
    import subprocess
    kart = subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version,uuid,memory.total",
                           "--format=csv,noheader"], capture_output=True, text=True).stdout.strip()
    return {
        "platform": {"ad": "Modal", "hesap": hesap, "tip": tip, "saatlik_usd": SAATLIK_USD.get(tip),
                     "ortam": {k: v for k, v in os.environ.items() if k.startswith("MODAL_")
                               and not any(y in k for y in ("TOKEN", "SECRET", "KEY"))}},
        "nvidia_smi": kart,
        "yazilim": {"vllm": VLLM_SURUMU, "taban_imaj": TABAN_IMAJ,
                    "kurulan": {p: _paket_surumu(p) for p in ("vllm", "torch", "transformers", "huggingface_hub",
                                                              "openai", "gguf", "safetensors")}},
        "baglam": {"dosya": DONMUS, "sha256": _sha256(f"/root/{DONMUS}")},
    }


def _yaz(kunye: dict, dizin: str) -> None:
    import json
    with open(f"{dizin}/KUNYE.json", "w", encoding="utf-8") as f:
        json.dump(kunye, f, ensure_ascii=False, indent=2)
    out_vol.commit()
    print(json.dumps(kunye, ensure_ascii=False, indent=2), flush=True)


@app.function(image=image, gpu="A10", volumes={"/outputs": out_vol}, timeout=60 * 60, retries=0)
def kontrol(tip: str, hesap: str, agirlik: str) -> dict:
    """Aşama A: vLLM açılıyor mu · ham cevap alanları · 8 soru tek tek ↔ aynı anda (G1, G4)."""
    import json
    import subprocess
    import sys
    import urllib.request
    sys.path[:0] = ["/root/scripts/olcum_uretim", "/root/scripts/puanlama", "/root"]
    dizin = f"{CIKTI_KOK}/kontrol-{agirlik}"
    os.makedirs(dizin, exist_ok=True)
    kunye = {"is": "F0.16 vLLM pilotu · aşama A (kontrol)", "agirlik": agirlik, **_ortak_kunye(tip, hesap)}
    try:
        hf, kunye["model"] = _model_klasoru(agirlik)
        kunye["model_klasoru"] = hf
        srv, komut = _sunucu_ac(hf, f"{dizin}/vllm.log")
    except (RuntimeError, subprocess.CalledProcessError) as h:
        kunye["acildi"], kunye["hata_sonu"] = False, str(h)[-3000:]
        _yaz(kunye, dizin)
        return kunye
    kunye["acildi"], kunye["kosan_komut"] = True, komut
    try:
        ham = json.loads(urllib.request.urlopen(urllib.request.Request(
            f"http://127.0.0.1:{PORT}/v1/chat/completions",
            data=json.dumps({"model": "local", "max_tokens": 200, "temperature": 0, "seed": 3407,
                             "messages": [{"role": "user", "content": "2+2 kaçtır? Kısa düşün."}],
                             "chat_template_kwargs": {"enable_thinking": True}}).encode(),
            headers={"Content-Type": "application/json"}), timeout=120).read())
        kunye["ham_cevap_mesaj_alanlari"] = sorted(ham["choices"][0]["message"].keys())
        kunye["ham_cevap_ornek"] = ham["choices"][0]["message"]
        sonuc = {}
        for ad, es in (("tek_tek", 1), ("ayni_anda", 8)):
            r = subprocess.run([sys.executable, "/root/scripts/olcum_uretim/toplu_uret.py",
                                "--server-url", f"http://127.0.0.1:{PORT}/v1", "--server-model", "local",
                                "--data", f"/root/{VERI}", "--donmus-baglam", f"/root/{DONMUS}",
                                "--tokenizer-dizini", hf, "--es-zamanli", str(es), "--ilk-n", "8",
                                "--etiket", f"kontrol_{ad}", "--cikti-dizini", dizin],
                               capture_output=True, text=True)
            sonuc[ad] = {"cikis": r.returncode, "son_satirlar": (r.stdout + r.stderr).strip().splitlines()[-6:]}
        kunye["sekiz_soru"] = sonuc
        if all(s["cikis"] == 0 for s in sonuc.values()):
            a = [json.loads(l) for l in open(f"{dizin}/kontrol_tek_tek_detail.jsonl", encoding="utf-8")]
            b = [json.loads(l) for l in open(f"{dizin}/kontrol_ayni_anda_detail.jsonl", encoding="utf-8")]
            kunye["sekiz_soru"]["birebir_ayni_cevap"] = sum(x["cevap"] == y["cevap"] for x, y in zip(a, b))
    finally:
        _sunucu_kapat(srv)
    _yaz(kunye, dizin)
    return kunye


@app.function(image=image, gpu="A10", volumes={"/outputs": out_vol}, timeout=3 * 60 * 60, retries=0)
def pilot(tip: str, hesap: str, baglam_sha: str, agirlik: str) -> dict:
    """Aşama B: 80 soru, vLLM'de iki üretim koşusu (aynı sunucuda arka arkaya)."""
    import subprocess
    import sys
    import time
    sys.path[:0] = ["/root/scripts/olcum_uretim", "/root/scripts/puanlama", "/root"]
    from part_dosya import tamamlanmis_jsonl
    import olcum_karti as ok
    if _sha256(f"/root/{DONMUS}") != baglam_sha:
        raise SystemExit("[pilot-vllm] 🚫 dondurulmuş bağlam yerelde hesaplanan sha256'yla aynı değil")
    dizin = f"{CIKTI_KOK}/{tip}/{agirlik}"
    os.makedirs(dizin, exist_ok=True)
    hf, model_kaydi = _model_klasoru(agirlik)
    kunye = {"is": "F0.16 vLLM pilotu · aşama B", "agirlik": agirlik, **_ortak_kunye(tip, hesap),
             "model": model_kaydi, "model_klasoru": hf, "es_zamanli": ES_ZAMANLI, "rejim": ok.REJIM, "kosular": []}
    saatlik = SAATLIK_USD.get(tip)
    srv, kunye["kosan_komut"] = _sunucu_ac(hf, f"{dizin}/vllm.log")
    try:
        for t in (1, 2):
            etiket = f"h1_tgta_v1_vllm_{agirlik}_t{t}"
            t0 = time.time()
            r = subprocess.run([sys.executable, "/root/scripts/olcum_uretim/toplu_uret.py",
                                "--server-url", f"http://127.0.0.1:{PORT}/v1", "--server-model", "local",
                                "--data", f"/root/{VERI}", "--donmus-baglam", f"/root/{DONMUS}",
                                "--tokenizer-dizini", hf, "--es-zamanli", str(ES_ZAMANLI),
                                "--etiket", etiket, "--cikti-dizini", dizin])
            sure = time.time() - t0
            if r.returncode != 0:
                raise SystemExit(f"[pilot-vllm] 🚫 {etiket} üretimi başarısız (kod {r.returncode})")
            satirlar = tamamlanmis_jsonl(f"{dizin}/{etiket}_detail.jsonl")
            kunye["kosular"].append({"etiket": etiket, "sure_s": round(sure, 1), "s_cevap": round(sure / len(satirlar), 2),
                                     "usd_cevap": round(sure / len(satirlar) * saatlik / 3600, 5) if saatlik else None,
                                     "gecerlilik": ok.gecerlilik(satirlar)})
            out_vol.commit()
    finally:
        _sunucu_kapat(srv)
    _yaz(kunye, dizin)
    return kunye


@app.local_entrypoint()
def baslat(asama: str = "", agirlik: str = "", tip: str = "A10"):
    if asama not in ("kontrol", "pilot"):
        raise SystemExit("[pilot-vllm] 🚫 --asama kontrol|pilot zorunlu")
    if agirlik not in AGIRLIKLAR:
        raise SystemExit(f"[pilot-vllm] 🚫 --agirlik {'|'.join(AGIRLIKLAR)} zorunlu")
    import sys
    sys.path.insert(0, "scripts/egitim")
    from modal_train import _baslatan_hesap   # ADR-0101 m.4: hesap profilden, elle yazılmaz
    hesap = _baslatan_hesap()
    if asama == "kontrol":
        c = kontrol.with_options(gpu=tip).spawn(tip, hesap, agirlik)
    else:
        c = pilot.with_options(gpu=tip).spawn(tip, hesap, _sha256(DONMUS), agirlik)
    print(f"[pilot-vllm] SPAWNED ✓ aşama={asama} ağırlık={agirlik} tip={tip} hesap={hesap} · {c.object_id}\n  bitince: "
          f"modal volume get hukuk-outputs /f016-vllm-pilot/<alt klasör> outputs/eval/f0/f016-vllm-pilot/<alt klasör>",
          flush=True)
