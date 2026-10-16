#!/usr/bin/env python3
"""CP2 — tuzak havuzunun ÜRETİMDEN ÖNCE hakemle elenmesi.

Pilot ölçtü: `abstain_trap_v3` diliminin **%42'si geçersiz tuzak** — tuzak diye verilen madde
soruyu gerçekten cevaplıyor (`outputs/eval/cp/cp2-rejected-hasat/KUNYE.json`). Bu, hasadın verimini
%5'e düşürdüğü gibi, aynı dilimden üretilmiş `chosen` tarafını da ("çekiniyorum" diyor ama kaynak
cevaplıyor) zehirliyor.

Geçerlilik **cevaba bakmadan**, yalnız `(soru, tuzak madde)` çiftinden sorulabilir — yani GPU'ya
girmeden. Ölçülen birim maliyet ≈ $0.0001/kalem: 8.000 kalemlik eleme ≈ $0.85, buna karşılık
hasat verimi %5,0 → %8,6 ve yerel GPU süresi ~%42 kısalır.

🚨 SEMANTİK KİLİT — bu betiğin var oluş sebebiyle ilgili:
`score_abstention.py`'nin hakemi geçerliliğe **cevabı da görerek** karar verir; buradaki hakem
göremez. İkisi ayrışırsa havuzu bir ölçütle eler, sonucu başkasıyla raporlarız — `yurutme-tuzaklari`
**4.7**'nin ta kendisi, bir katman yukarıda. Bu yüzden:
  1. Geçerlilik sorusu `score_abstention.JUDGE_SYSTEM`den **birebir** alınır (kopyalanmaz, import
     edilir — sürüklenmesin).
  2. Eleme koşulmadan ÖNCE `--against` ile etiketli pilot kümesinde **uyum ölçülür**.

Kullanım:
  # 1) DOĞRULAMA (önce bu — ~$0.004): pilotun 36 etiketli örneğinde uyum
  python scripts/veri_hazirlik/cp2_prefilter.py --against outputs/eval/cp/cp2-rejected-hasat/abst_kontrol_m2.jsonl \\
      --out outputs/eval/cp/cp2-on-eleme/dogrulama_m2.jsonl
  # 2) ELEME (uyum yeterliyse): havuzu sırayla etiketle
  python scripts/veri_hazirlik/cp2_prefilter.py --limit 8000 --out data/_ham_ve_ara/cp2_prefilter_m2.jsonl
"""
import argparse
import json
import os
import random
import sys

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

from llm_client import (make_client, resolve, price, request_kwargs,  # noqa: E402
                        note_provider, seen_providers, loads_tolerant)
from score_abstention import JUDGE_SYSTEM  # noqa: E402  — semantik kilit, bkz. modül başlığı

PACKED = "data/_ham_ve_ara/orpo_packed.jsonl"
TRAP_CLIP = 900          # build_orpo_v3 / cp2_harvest ile BİREBİR

# `source_answers` tanımı JUDGE_SYSTEM'den alınır; buradaki tek fark CEVABIN OLMAMASI.
# Hakemin yalnız o alanı döndürmesi isteniyor — verdict/used_parametric cevap gerektirir.
SYSTEM = (
    JUDGE_SYSTEM.split("Görevin yalnız")[0]
    + "Bu turda modelin CEVABI YOK — yalnız kaynağın soruyu cevaplayıp cevaplamadığına karar ver. "
      "YALNIZ JSON döndür:\n"
      "{\n"
      '  "source_answers": true/false,   // KAYNAK metin soruyu gerçekten cevaplıyor mu '
      "(içinde cevap var mı)\n"
      '  "reason": "tek cümle"\n'
      "}\n"
      "true = tuzak GEÇERSİZ (kaynak soruyu cevaplıyor, çekinmek yanlış olurdu).\n"
      "false = tuzak GEÇERLİ (kaynak soruyu cevaplamıyor, doğru davranış çekinmek).\n"
      "Kısmî/dolaylı ilgi yeterli DEĞİL: sorunun sorduğu şeyin cevabı metinde okunabiliyor mu?"
)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--against", default="",
                   help="DOĞRULAMA kipi: bu abst_*.jsonl'deki id'ler yargılanır ve `valid_trap` "
                        "etiketiyle uyum raporlanır. Eleme kipiyle birlikte verilmez.")
    p.add_argument("--limit", type=int, default=0, help="ELEME kipi: kaç kalem yargılanacak")
    p.add_argument("--packed", default=PACKED)
    p.add_argument("--seed", type=int, default=3407)   # cp2_harvest ile aynı karıştırma
    p.add_argument("--judge-model", default=os.environ.get("GND_JUDGE", "gpt-4o-mini"))
    p.add_argument("--budget-usd", type=float,
                   default=float(os.environ.get("OPENAI_BUDGET_USD", "5") or "5"))
    a = p.parse_args()
    if bool(a.against) == bool(a.limit):
        raise SystemExit("--against (doğrulama) YA DA --limit (eleme) — tam olarak biri")
    return a


def load_pool(path, seed):
    """cp2_harvest ile BİREBİR aynı dilim + aynı karıştırma: id eşlemesi ve sıra korunur."""
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    rows = [r for r in rows if r.get("slice") == "abstain_trap_v3"]
    random.seed(seed)
    random.shuffle(rows)
    return rows


def load_done(path):
    if not os.path.exists(path):
        return set()
    return {json.loads(l)["id"] for l in open(path, encoding="utf-8") if l.strip()}


def judge(client, model, soru, source):
    r = client.chat.completions.create(
        model=model, temperature=0, **request_kwargs(model),
        messages=[{"role": "system", "content": SYSTEM},
                  {"role": "user", "content": f"SORU:\n{soru}\n\nKAYNAK MADDE:\n{source}"}])
    note_provider(r)
    d = loads_tolerant(r.choices[0].message.content)
    u, p = r.usage, price(model)
    return d, u.prompt_tokens * p[0] + u.completion_tokens * p[1]


def report_agreement(records, labels):
    """Doğrulama kipinin tek çıktısı: ön-eleme ile raporlanan ölçüt aynı şeyi mi diyor.

    Uyum düşükse eleme koşulmaz — yanlış ölçütle elenmiş havuz, elenmemiş havuzdan kötüdür:
    hangi örneklerin neden düştüğü artık bilinmez.
    """
    tp = tn = fp = fn = 0
    for r in records:
        pre, ref = r["gecerli"], labels[r["id"]]
        if pre and ref:
            tp += 1
        elif not pre and not ref:
            tn += 1
        elif pre and not ref:
            fp += 1          # ön-eleme geçirdi, denetim "geçersiz" dedi → filtre kaçırdı
        else:
            fn += 1          # ön-eleme eledi, denetim "geçerli" dedi → filtre geçerli tuzak kesti
    n = tp + tn + fp + fn
    po = (tp + tn) / n if n else 0.0
    pa1 = (tp + fp) / n * (tp + fn) / n if n else 0.0
    pa0 = (tn + fn) / n * (tn + fp) / n if n else 0.0
    pe = pa1 + pa0
    kappa = (po - pe) / (1 - pe) if pe < 1 else 1.0
    return {"n": n, "uyum": round(po, 3), "kappa": round(kappa, 3),
            "ikisi_de_gecerli": tp, "ikisi_de_gecersiz": tn,
            "on_eleme_kacirdi": fp, "on_eleme_gecerliyi_kesti": fn,
            "yorum": "on_eleme_gecerliyi_kesti = filtrenin BEDELİ (geçerli tuzak kaybı); "
                     "on_eleme_kacirdi = filtrenin FAYDASIZ kaldığı kalemler"}


def main():
    a = parse_args()
    client, gateway = make_client()
    a.judge_model = resolve(a.judge_model, gateway)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)

    rows = load_pool(a.packed, a.seed)
    labels = {}
    if a.against:
        labels = {r["id"]: r["valid_trap"]
                  for r in json.load(open(a.against, encoding="utf-8"))}
        rows = [r for r in rows if r["id"] in labels]
        print(f"[on-eleme] DOĞRULAMA kipi · {len(rows)}/{len(labels)} etiketli kalem bulundu")
    else:
        print(f"[on-eleme] ELEME kipi · havuz {len(rows)} · limit {a.limit}")

    done = load_done(a.out)
    out, spent, n_valid = [], 0.0, 0
    with open(a.out, "a", encoding="utf-8") as f:
        for r in rows:
            if a.limit and len(out) + len(done) >= a.limit:
                break
            if r["id"] in done:
                continue
            if spent >= a.budget_usd:
                print(f"[on-eleme] BÜTÇE doldu (${spent:.3f}) — kalan atlandı")
                break
            source = (r.get("trap_text") or "")[:TRAP_CLIP]
            if not source:
                continue
            d, c = judge(client, a.judge_model, r["soru"], source)
            spent += c
            gecerli = not d.get("source_answers")
            n_valid += 1 if gecerli else 0
            rec = {"id": r["id"], "gecerli": gecerli, "reason": d.get("reason")}
            out.append(rec)
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            if len(out) % 25 == 0:
                print(f"  yargılanan={len(out)} geçerli={n_valid} "
                      f"oran={n_valid/len(out):.3f} ${spent:.4f}", flush=True)

    summary = {
        "kip": "dogrulama" if a.against else "eleme",
        "n": len(out), "gecerli": n_valid,
        "gecerli_orani": round(n_valid / len(out), 4) if out else None,
        "judge_model": a.judge_model, "judge_gateway": gateway,
        "judge_providers": seen_providers(),
        "birim_maliyet_usd": round(spent / len(out), 6) if out else None,
        "toplam_maliyet_usd": round(spent, 4), "seed": a.seed, "trap_clip": TRAP_CLIP,
    }
    if a.against:
        summary["uyum"] = report_agreement(out, labels)
    sp = a.out.replace(".jsonl", "_summary.json")
    json.dump(summary, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("\n[on-eleme] ÖZET " + json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"[on-eleme] → {a.out}\n[on-eleme] özet → {sp}")


if __name__ == "__main__":
    main()
