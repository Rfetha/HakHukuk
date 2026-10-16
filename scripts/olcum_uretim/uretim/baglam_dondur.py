#!/usr/bin/env python3
"""F0.16 — bağlam dondurma (ADR-0097 m.6): DEV sorularının getirilen bağlamı bir kez, CPU'da üretilir.

NEDEN: ölçüm kiralık kartlarda koşacak. Retriever (bge-m3 + BM25) her makinede yeniden koşarsa farklı
bir işlemcideki yuvarlama farkı kaynak sırasını sessizce değiştirebilir; o zaman iki makinenin
cevap farkı modelin değil bağlamın farkı olur. Bağlam bir kez üretilir, `sha256`'sıyla dondurulur,
bütün koşular `gen_eval_grounded.py --donmus-baglam` ile aynı dosyayı okur.

Bağlam `gen_eval_grounded.harness_baglami` ile üretilir — canlı üretimle aynı fonksiyon. Dosya
künye + kalemlerden oluşan tek bir JSON'dur; anahtarlar sıralı yazılır, tarih taşımaz → aynı girdi
bayt bayt aynı dosyayı verir.

Kullanım (bütün rejim bayrakları zorunlu; varsayılan yok, tuzak 1.1):
  python scripts/olcum_uretim/uretim/baglam_dondur.py --data data/eval/dev/core_hard.jsonl \\
      --harness-indeks data/index/mevzuat_bge_m3_s2 --harness-k 10 --rrf-k 10 \\
      --seed 3407 --n 80 --max-chunk-chars 900 --out data/eval/dev/baglam/h1-k10.json
"""
# ── scripts/ yol köprüsü (T5 2026-09-07 · ADR-0112 2026-10-16) ───────────────
# Kardeş modüller iç içe alt klasörlerde de bulunsun diye scripts/ kökü, altındaki HER
# derinlikteki klasör ve repo kökü sys.path'e girer. Uzantısız `import X` bu köprü olmadan
# taşımada SESSİZCE kırılır: ImportError çalışma zamanında, bazen GPU koşusunun ortasında.
# ⚠️ 39 dosyada BİREBİR aynı; değiştirirsen hepsinde değiştir (grep: "yol köprüsü").
import os, sys
_K = os.path.abspath(__file__)
_K = _K[:_K.rindex(os.sep + "scripts" + os.sep)] + os.sep + "scripts"  # dışarıda: ValueError
_Y = []
for _y, _alt, _f in os.walk(_K):
    _alt[:] = sorted(_a for _a in _alt if _a[0] not in "_.")
    _Y.append(_y)
sys.path[:0] = [*_Y, os.path.dirname(_K)]
# ─────────────────────────────────────────────────────────────────────────────
import argparse  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
from dataclasses import asdict, dataclass  # noqa: E402

from gen_eval_grounded import MADDE_PATH, harness_baglami, load_madde_index, ornekle  # noqa: E402
from part_dosya import part_ile_yaz  # noqa: E402


@dataclass(frozen=True)
class Ayar:
    """Bağlamı belirleyen rejim. Dondurulmuş dosyayı okuyan koşu kendi değerlerini buna karşı sınar."""
    seed: int
    n: int
    harness_k: int
    rrf_k: int
    max_chunk_chars: int
    harness_no_gold: bool


def sha256_dosya(yol: str) -> str:
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for parca in iter(lambda: f.read(1 << 20), b""):
            h.update(parca)
    return h.hexdigest()


def dondur(veri_yolu: str, madde_yolu: str, retriever, ayar: Ayar, indeks: str) -> dict:
    """Örneklemi ve her kalemin bağlamını üretir → {"kunye", "kalemler"} (yazılmamış)."""
    rows = [json.loads(l) for l in open(veri_yolu, encoding="utf-8") if l.strip()]
    sample, _ = ornekle(rows, load_madde_index(madde_yolu), ayar.seed, ayar.n)
    kalemler = []
    for sira, (rec, soru, src) in enumerate(sample):
        blok, iz = harness_baglami(rec, soru, retriever, ayar)
        kalemler.append({"sira": sira, "soru": soru, "referans": src,
                         "kanun_adi": rec.get("kanun_adi"), "madde_no": rec.get("madde_no"),
                         "kanun_no": rec.get("kanun_no"), "sources_block": blok, "harness": iz})
    k = retriever._kunye
    kunye = {**asdict(ayar), "veri": veri_yolu, "veri_sha256": sha256_dosya(veri_yolu),
             "indeks": {"dizin": indeks, "model": k.get("model"), "n": k.get("n"),
                        "korpus_sha256": (k.get("korpus") or {}).get("sha256")},
             "yururluk": "yalniz_yururlukte"}
    return {"kunye": kunye, "kalemler": kalemler}


def yaz(donmus: dict, yol: str) -> str:
    """Bayt bayt tekrarlanabilir yazım (`.part` üzerinden) → dosyanın sha256'sı."""
    os.makedirs(os.path.dirname(yol) or ".", exist_ok=True)
    with part_ile_yaz(yol) as f:
        f.write(json.dumps(donmus, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
    return sha256_dosya(yol)


def oku(yol: str, ayar: Ayar, veri_sha256: str) -> list[dict]:
    """Dondurulmuş bağlamı okur; rejim ya da soru dosyası uyuşmazsa, kalem eksik ya da yineleniyorsa
    DURUR. Her kalemin harness izine dosyanın sha256'sı yazılır (`donmus_baglam`)."""
    sha = sha256_dosya(yol)
    d = json.load(open(yol, encoding="utf-8"))
    kunye = d["kunye"]
    beklenen = {**asdict(ayar), "veri_sha256": veri_sha256}
    farkli = [f"{a}: dosya {kunye.get(a)!r} ↔ koşu {v!r}" for a, v in beklenen.items()
              if kunye.get(a) != v]
    if farkli:
        raise SystemExit(f"[donmus-baglam] 🚫 {yol} bu koşunun rejimiyle üretilmemiş — "
                         + " · ".join(farkli))
    kalemler = d["kalemler"]
    siralar = [k["sira"] for k in kalemler]
    if sorted(siralar) != list(range(ayar.n)):
        raise SystemExit(f"[donmus-baglam] 🚫 {yol}: {len(kalemler)} kalem, {len(set(siralar))} "
                         f"tekil sıra; beklenen 0..{ayar.n - 1} (eksik ya da yinelenen kalem)")
    return [dict(k, harness={**k["harness"], "donmus_baglam": sha})
            for k in sorted(kalemler, key=lambda k: k["sira"])]


def main():
    p = argparse.ArgumentParser(description="F0.16 — bağlam dondurma (ADR-0097 m.6)")
    p.add_argument("--data", required=True)
    p.add_argument("--madde-path", default=MADDE_PATH)
    p.add_argument("--harness-indeks", required=True)
    p.add_argument("--harness-k", type=int, required=True)
    p.add_argument("--rrf-k", type=int, required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--max-chunk-chars", type=int, required=True)
    p.add_argument("--harness-no-gold", action="store_true")
    p.add_argument("--out", required=True)
    a = p.parse_args()

    from retriever import Retriever
    retriever = Retriever.yukle(a.harness_indeks)
    ayar = Ayar(seed=a.seed, n=a.n, harness_k=a.harness_k, rrf_k=a.rrf_k,
                max_chunk_chars=a.max_chunk_chars, harness_no_gold=a.harness_no_gold)
    donmus = dondur(a.data, a.madde_path, retriever, ayar, indeks=a.harness_indeks)
    if len(donmus["kalemler"]) != a.n:
        raise SystemExit(f"[donmus-baglam] 🚫 örneklem {len(donmus['kalemler'])} kalem, --n {a.n}")
    sha = yaz(donmus, a.out)
    print(f"[donmus-baglam] {len(donmus['kalemler'])} kalem → {a.out}\n  sha256 {sha}")


if __name__ == "__main__":
    main()
