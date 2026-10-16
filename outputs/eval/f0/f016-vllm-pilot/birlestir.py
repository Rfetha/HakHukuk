"""vLLM pilotu puanlaması, parçalı koşu (kullanıcı kararı 2026-10-16: 8 parça) — parça çıktılarını birleştirir.

Her (ağırlık, tekrar) için 8 parçanın `gnd_*.jsonl` dosyasını kalem sırasıyla tek dosyada birleştirir ve özetlerini
toplar. Durur (dosya yazmadan): parça eksik ya da `.part` kalmışsa · kalem kümesi 0..79 değilse ya da yineleniyorsa ·
hakem hatası satırı varsa. Hakem her kalemi bağımsız puanladığı için birleşik dosya tek seferlik puanlamayla aynı
ölçümdür.

Kullanım (repo kökünden): python outputs/eval/f0/f016-vllm-pilot/birlestir.py
"""
import argparse
import json
import os
import sys

K = "outputs/eval/f0/f016-vllm-pilot/puanlama"
P = f"{K}/parcalar"
AGIRLIKLAR = ("q4-acilmis", "bf16-orijinal")
TEKRAR, PARCA, N = 3, 8, 80


def birlestir(a: str, r: int, k: str = K, p: str = P, ek: str = "") -> dict:
    """`ek`: etiket eki (ör. `-u2` = 2. üretim koşusunun puanlaması, 2026-10-16 gürültü ölçümü)."""
    satirlar, ozetler = [], []
    for j in range(1, PARCA + 1):
        etiket = f"vllm-{a}{ek}_t{r}_p{j}"
        yol = f"{p}/gnd_{etiket}.jsonl"
        if not os.path.exists(yol):
            raise SystemExit(f"[birlestir] 🚫 {yol} yok (parça bitmemiş ya da .part kalmış)")
        satirlar += [json.loads(l) for l in open(yol, encoding="utf-8") if l.strip()]
        ozetler.append(json.load(open(f"{p}/gnd_{etiket}_summary.json", encoding="utf-8")))
    idler = [s["id"] for s in satirlar]
    if sorted(idler) != list(range(N)):
        raise SystemExit(f"[birlestir] 🚫 {a} t{r}: {len(idler)} satır, {len(set(idler))} tekil id; beklenen 0..{N - 1}")
    hatali = [s["id"] for s in satirlar if s.get("durum") == "hakem_hata"]
    if hatali:
        raise SystemExit(f"[birlestir] 🚫 {a} t{r}: hakem hatası olan kalemler {hatali}")
    satirlar.sort(key=lambda s: s["id"])
    with open(f"{k}/gnd_vllm-{a}{ek}_t{r}.jsonl", "w", encoding="utf-8") as f:
        for s in satirlar:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    ozet = {"label": f"vllm-{a}{ek}_t{r}", "parca": PARCA, "n": len(satirlar),
            "hakem": ozetler[0].get("hakem"), "judge_model": ozetler[0].get("judge_model"),
            "judge_providers": sorted({p for o in ozetler for p in o.get("judge_providers", [])}),
            "judge_cost_usd": round(sum(o.get("judge_cost_usd", 0) for o in ozetler), 4),
            "total_claims": sum(o.get("total_claims", 0) for o in ozetler),
            "n_hakem_hata": sum(o.get("n_hakem_hata") or 0 for o in ozetler),
            "n_sifir_iddia": sum(o.get("n_sifir_iddia") or 0 for o in ozetler)}
    with open(f"{k}/gnd_vllm-{a}{ek}_t{r}_summary.json", "w", encoding="utf-8") as f:
        json.dump(ozet, f, ensure_ascii=False, indent=2)
    return ozet


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--kok", default=K)
    ap.add_argument("--parca-dizini", default=P)
    ap.add_argument("--ek", default="")
    ap.add_argument("--agirlik", nargs="+", default=list(AGIRLIKLAR))
    ap.add_argument("--tekrar", type=int, default=TEKRAR)
    arg = ap.parse_args()
    toplam = 0.0
    for a in arg.agirlik:
        for r in range(1, arg.tekrar + 1):
            o = birlestir(a, r, arg.kok, arg.parca_dizini, arg.ek)
            toplam += o["judge_cost_usd"]
            print(f"{o['label']}: n={o['n']} iddia={o['total_claims']} sağlayıcı={o['judge_providers']} "
                  f"${o['judge_cost_usd']}")
    print(f"toplam tahmini hakem maliyeti ${toplam:.4f}")
    sys.exit(0)
