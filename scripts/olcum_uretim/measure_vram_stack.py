#!/usr/bin/env python3
"""Yığının GPU ayak izini ÖLÇ — kuantizasyon × bağlam matrisi.

Neden: TASARIM §12 açık borç — *"VRAM tahminleri ölçülmedi"*. ADR-0018'in erişilebilirlik
ekseni (≤8 GB yumuşak kapı) ölçülmüş sayı ister; hesap yeterli değil.

Neyi ölçer: llama-server'ın GERÇEK VRAM payı = (server yüklüyken) − (server öncesi taban).
Taban ölçümü şart: masaüstü/compositor zaten ~1 GB tutuyor, onu modele yazmak yanlış olur.

Neyi ölçMEZ: harness. TASARIM §5 gereği harness GPU'ya GİRMEZ (embedder CPU'da, graf +
vektör indeksi CPU RAM/disk'te) — yığının o yarısı ayrı raporlanır ve bugün ölçülemez,
çünkü TR embedding modeli henüz seçilmedi (TASARIM §13, açık soru 1).

⚠️ GÜÇ DURUMU KAYDA GEÇER. 2026-07-24: laptop pilde/tasarruf modundayken decode 7.9 t/s,
şarjda 134 t/s ölçüldü — 17× fark, hiçbir hata vermeden (research_log #39). Güç durumu
yazılmayan bir performans sayısı tekrarlanabilir değildir.

Kullanım:
  python scripts/olcum_uretim/measure_vram_stack.py --ggufs models/gguf/*.gguf --ctxs 4096 32768 131072
"""
import argparse
import json
import os
import subprocess
import time
import urllib.request

BIN = os.path.expanduser("~/code/llama.cpp/build-cuda/bin/llama-server")


def nvsmi(fields):
    out = subprocess.run(
        ["nvidia-smi", f"--query-gpu={','.join(fields)}", "--format=csv,noheader,nounits"],
        capture_output=True, text=True, check=True).stdout.strip().splitlines()[0]
    return [v.strip() for v in out.split(",")]


def gpu_used_mib():
    return int(nvsmi(["memory.used"])[0])


def power_state():
    p, sm, mem, w, t = nvsmi(["pstate", "clocks.sm", "clocks.mem", "power.draw", "temperature.gpu"])
    return {"pstate": p, "clocks_sm_mhz": int(sm), "clocks_mem_mhz": int(mem),
            "power_w": float(w), "temp_c": int(t)}


def measure(gguf, ctx, kv_type, port=8097, timeout_s=300):
    base = gpu_used_mib()
    proc = subprocess.Popen(
        [BIN, "-m", gguf, "-ngl", "99", "-fa", "on", "--no-context-shift",
         "--cache-type-k", kv_type, "--cache-type-v", kv_type,
         "-c", str(ctx), "--host", "127.0.0.1", "--port", str(port)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        t0 = time.time()
        while time.time() - t0 < timeout_s:
            if proc.poll() is not None:
                return {"error": f"server öldü (rc={proc.returncode}) — ctx={ctx} sığmamış olabilir"}
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2)
                break
            except Exception:
                time.sleep(2)
        else:
            return {"error": "server açılmadı"}
        time.sleep(3)                                    # buffer'lar otursun
        loaded = gpu_used_mib()
        # tek token üret → decode buffer'ları da tahsis olsun (yükleme anı tepe değil)
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/v1/chat/completions",
            data=json.dumps({"model": "local", "max_tokens": 8, "temperature": 0,
                             "chat_template_kwargs": {"enable_thinking": False},
                             "messages": [{"role": "user", "content": "Merhaba"}]}).encode(),
            headers={"Content-Type": "application/json"})
        try:
            urllib.request.urlopen(req, timeout=120).read()
        except Exception:
            pass
        peak = max(loaded, gpu_used_mib())
        return {"base_mib": base, "peak_mib": peak, "server_mib": peak - base,
                "server_gib": round((peak - base) / 1024, 2), "power": power_state()}
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill()
        time.sleep(3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ggufs", nargs="+", required=True)
    ap.add_argument("--ctxs", nargs="+", type=int, default=[4096])
    ap.add_argument("--kv-type", default="q8_0")
    ap.add_argument("--out", default="outputs/eval/vram_stack.json")
    a = ap.parse_args()

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    print(f"### güç durumu (başlangıç): {power_state()}")
    rows = []
    for g in a.ggufs:
        size_gib = round(os.path.getsize(g) / 2**30, 2)
        for ctx in a.ctxs:
            r = measure(g, ctx, a.kv_type)
            r.update({"gguf": os.path.basename(g), "file_gib": size_gib,
                      "ctx": ctx, "kv_type": a.kv_type})
            rows.append(r)
            if "error" in r:
                print(f"  {os.path.basename(g):28} ctx={ctx:>7}  ❌ {r['error']}")
            else:
                print(f"  {os.path.basename(g):28} ctx={ctx:>7}  dosya {size_gib:5.2f} GiB  "
                      f"→ VRAM {r['server_gib']:5.2f} GiB  "
                      f"(KV+tavan {r['server_gib']-size_gib:+.2f})  "
                      f"[{r['power']['pstate']} {r['power']['clocks_sm_mhz']}MHz "
                      f"{r['power']['power_w']:.0f}W]")
    json.dump(rows, open(a.out, "w"), ensure_ascii=False, indent=1)
    print(f"\n### → {a.out}")


if __name__ == "__main__":
    main()
