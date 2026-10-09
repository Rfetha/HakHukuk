#!/usr/bin/env python
"""Tanı — llama.cpp imajında GPU gerçekten görünüyor mu?

Neden: CP2-c duman testinde llama-server **11,5 tok/s/slot** verdi ve 4.366 satırlık sunucu
logunda **tek bir CUDA/cihaz satırı yok**. CUDA derlemesi açılışta cihazı listeler; listelemiyorsa
ya cihaz yok ya derleme CPU. İkisi de "hata vermeden yavaş çalışır" sınıfı.

İmaj burada BİLEREK sade (pip katmanı yok): sorulan soru yalnız taşıyıcının GPU'yu görüp
görmediği. Kurulum katmanları cevabı değiştirmez, yalnız tanıyı yavaşlatır.

Kullanım:  modal run scripts/olcum_uretim/diag_modal_gpu.py
"""
import os

import modal

GPU = os.environ.get("HUKUK_GPU", "A100")
image = (
    modal.Image.from_registry("ghcr.io/ggml-org/llama.cpp:server-cuda", add_python="3.11")
    .entrypoint([])
)
app = modal.App("hukuk-diag-gpu")


@app.function(image=image, gpu=GPU, timeout=600, retries=0)
def diag():
    import os
    import subprocess

    def kos(*cmd):
        print(f"\n$ {' '.join(cmd)}", flush=True)
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            print((r.stdout or "") + (r.stderr or ""), flush=True)
        except Exception as e:
            print(f"!! {e}", flush=True)

    print("LD_LIBRARY_PATH =", os.environ.get("LD_LIBRARY_PATH"), flush=True)
    print("PATH =", os.environ.get("PATH"), flush=True)
    kos("/app/llama-server", "--list-devices")               # düz: bugünkü hâl
    os.environ["GGML_BACKEND_PATH"] = "/app/libggml-cuda.so"  # backend'i doğrudan göster
    kos("/app/llama-server", "--list-devices")
    del os.environ["GGML_BACKEND_PATH"]
    os.environ["LD_LIBRARY_PATH"] = "/app:" + os.environ.get("LD_LIBRARY_PATH", "")
    kos("/app/llama-server", "--list-devices")


@app.local_entrypoint()
def main():
    # Tanı KISA (saniyeler) ve çıktısı buraya gerekiyor → remote() burada doğru şık;
    # ADR-0008'in `spawn()` kuralı SAATLERCE koşan işler içindir.
    diag.remote()
