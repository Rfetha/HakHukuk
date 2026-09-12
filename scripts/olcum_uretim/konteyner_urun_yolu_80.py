"""ADIM 6.3.4/6.3.5 — konteynerin HTTP API'sinden 80 DEV sorusunu koşar, cevapları saklar.

⛔ Puanlama YOK burada — hakem çağrılmaz. Bu betik yalnız ÜRETİR ve boş/kesik sayar; puanlama
6.3b'nin işidir ve saklanan JSON'u girdi olarak okur.

⚠️ `hakhukuk.servis`'i host'ta İTHAL ETMEZ — vatandaşın fiilen kuracağı yol konteynerin
HTTP API'sidir (`127.0.0.1:8000/sor`), bu yüzden istekler ona gider.

⚠️ Künye bayrakları KOŞAN SÜREÇTEN okunur (`docker top` / konteyner içi `/proc/1/cmdline`),
sabit dize YAZILMAZ — tuzak 1.12 tam bunun tersini yaparak ısırmıştı.
"""
import json
import subprocess
import time
import urllib.error
import urllib.request

API_URL = "http://127.0.0.1:8000/sor"
DEV_YOLU = "data/eval/dev/core_hard.jsonl"
CIKTI_DIZIN = "outputs/eval/g23-konteyner-urun-yolu-80"
ISTEK_ZAMAN_ASIMI = 700  # saniye — iki geçişli üretim + araç döngüsü göz önünde bol pay


def _calistir(komut: list[str]) -> str:
    return subprocess.run(komut, capture_output=True, text=True, check=True).stdout.strip()


def _konteyner_sureci(ad: str) -> str:
    """Konteynerin PID 1'inin GERÇEK komut satırı — konteyner içinden okunur."""
    return _calistir(["docker", "exec", ad, "sh", "-c", "tr '\\0' ' ' < /proc/1/cmdline"]).strip()


def _konteyner_imaji(ad: str) -> str:
    return _calistir(["docker", "inspect", ad, "--format", "{{.Config.Image}}"])


def _dosya_sha256(konteyner: str, yol: str) -> str:
    cikti = _calistir(["docker", "exec", konteyner, "sha256sum", yol])
    return cikti.split()[0]


def kunye_topla() -> dict:
    """Künyeyi KOŞAN süreçlerden/imajlardan toplar — hiçbir alan elle yazılmaz (tuzak 1.12)."""
    llama_komut = _konteyner_sureci("hakhukuk-llama-1")
    app_komut = _konteyner_sureci("hakhukuk-app-1")
    return {
        "ne": "ADIM 6.3.4/6.3.5 — konteynerin HTTP API'sinden 80 DEV sorusu, puanlama YOK",
        "tarih": time.strftime("%Y-%m-%d"),
        "api_url": API_URL,
        "dev_seti": DEV_YOLU,
        "imajlar": {
            "app/indir": _konteyner_imaji("hakhukuk-app-1"),
            "llama": _konteyner_imaji("hakhukuk-llama-1"),
        },
        "llama_sureci_gercek_cmdline": llama_komut,
        "app_sureci_gercek_cmdline": app_komut,
        "artefakt_sha256": {
            "gguf": _dosya_sha256("hakhukuk-llama-1", "/artefakt/HakHukuk-4B-v0.3-Q4_K_M.gguf"),
            "korpus_volume": _dosya_sha256("hakhukuk-app-1", "/artefakt/corpus/mevzuat_maddeler.jsonl"),
            "korpus_imaj": _dosya_sha256("hakhukuk-app-1", "/app/data/corpus/mevzuat_maddeler.jsonl"),
            "indeks_gomme": _dosya_sha256("hakhukuk-app-1", "/artefakt/index/mevzuat_bge_m3_s2/gomme.npy"),
        },
        "kunye_kaynagi": "docker exec ... sha256sum / /proc/1/cmdline — sabit dize YOK (tuzak 1.12)",
    }


def _sor(soru: str) -> dict:
    govde = json.dumps({"soru": soru}).encode("utf-8")
    istek = urllib.request.Request(
        API_URL, data=govde, headers={"Content-Type": "application/json"}, method="POST")
    baslangic = time.monotonic()
    try:
        with urllib.request.urlopen(istek, timeout=ISTEK_ZAMAN_ASIMI) as y:
            gecen = time.monotonic() - baslangic
            return {"http": y.status, "gecen_sn": round(gecen, 1), **json.load(y)}
    except urllib.error.HTTPError as e:
        gecen = time.monotonic() - baslangic
        govde_metin = e.read().decode("utf-8", errors="replace")
        return {"http": e.code, "gecen_sn": round(gecen, 1), "detay": govde_metin}


def main() -> int:
    dev = [json.loads(satir) for satir in open(DEV_YOLU, encoding="utf-8") if satir.strip()]
    assert len(dev) == 80, f"DEV seti 80 değil: {len(dev)}"

    kunye = kunye_topla()
    print(json.dumps(kunye, ensure_ascii=False, indent=1))

    kayit = []
    for i, d in enumerate(dev):
        soru = d["messages"][0]["content"]
        r = _sor(soru)
        satir = {"id": i, "soru": soru, **r}
        kayit.append(satir)
        durum = r.get("durum") or f"HTTP {r.get('http')}"
        print(f"  [{i + 1}/80] {durum} ({r.get('gecen_sn')} sn)", flush=True)
        with open(f"{CIKTI_DIZIN}/urun_yolu_80.json", "w", encoding="utf-8") as f:
            json.dump(kayit, f, ensure_ascii=False, indent=1)

    tamamen_bos = [r["id"] for r in kayit if r.get("http") == 200 and not r.get("metin", "").strip()]
    bos_503 = [r["id"] for r in kayit if r.get("http") == 503]
    kesik = [r["id"] for r in kayit if r.get("durum") == "kesik"]
    dagilim = {}
    for r in kayit:
        anahtar = r.get("durum") or f"http_{r.get('http')}"
        dagilim[anahtar] = dagilim.get(anahtar, 0) + 1

    ozet = {
        "n": len(kayit),
        "http_200": sum(1 for r in kayit if r.get("http") == 200),
        "http_503_bos_cevap": bos_503,
        "http_diger": [r["id"] for r in kayit if r.get("http") not in (200, 503)],
        "tamamen_bos_metin_200_icinde": tamamen_bos,
        "kesik": kesik,
        "durum_dagilimi": dagilim,
    }
    with open(f"{CIKTI_DIZIN}/OZET.json", "w", encoding="utf-8") as f:
        json.dump(ozet, f, ensure_ascii=False, indent=1)
    with open(f"{CIKTI_DIZIN}/KUNYE.json", "w", encoding="utf-8") as f:
        json.dump(kunye, f, ensure_ascii=False, indent=1)

    print("\n=== ÖZET ===")
    print(json.dumps(ozet, ensure_ascii=False, indent=1))
    print("\nPuanlama YAPILMADI — bu betik yalnız üretir ve boş/kesik sayar (6.3b'nin girdisi).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
