#!/usr/bin/env python3
"""CP2-r — cevaba KÖR `valid_trap` DAMGASI, `{mod}:{id}` görünümüyle (ADR-0048 · ADR-0049 m.2).

🚨 EMEKLİ EDİLDİ 2026-08-06 (bağımsız inceleme, kusur K-3). Bu betik artık KENDİ ölçümünü
YAPMIYOR: kör hakem çağrısı, önbellek anahtarı ve klip `score_abstention.py`'den ithal
ediliyor. Kaldığı tek iş, `cp2c_kabul.sh`'in beklediği `{mod}:{id}` **görünümünü** üretmek.

NİYE EMEKLİ — iki alet vardı ve AYNI koşularda ÇELİŞEN sayı üretiyorlardı:

    cp09 m2b Rej   cevaba bağlı   #46 kör (klip 900)   K3 kör (klip 3500)   fark
    base              0,986            0,949                0,961           1,2 p
    Gemini            1,000            0,861                0,883           2,2 p
    `τ_g`             0,607            0,519                0,506           1,3 p

Hepsi hakem gürültü tabanının (0,3 p) 4-7 katı → tuzak 2.9 ihlali: çekinme ölçümünün TEK
kaynağı olmalı.

🚨 İKİ KLİP AYNI ŞEY DEĞİL — ve 900 bir KATEGORİ HATASIYDI (ölçüldü 2026-08-06):

  · **900** = ADR-0011'in eval-ayna klipi, `gen_eval_grounded --max-chunk-chars 900`.
    ÜRETİM zamanında, **her `[KAYNAK]` parçasına AYRI AYRI** uygulanır (satır 543/575);
    `context_shown` zaten kırpılmış parçaların BİRLEŞİMİdir.
  · **3500** = SKORLAMA zamanında, hakeme giden **kaynak metninin tamamına** uygulanan
    ayrı bir klip (`score_abstention.SOURCE_CLIP`).

Bu betik parça sabitini birleşime uyguluyordu. Ölçülen bedel (cp09 m2b, n=80, `[KAYNAK`
sayımı): tam metinde **320** kaynak · klip 900 ile hakem **147**'sini görüyor (**%46**) ·
klip 3500 ile **320**'sini (**%100**). Yani #46'nın kör paydası bağlamın yarısından karar
vermiş. #46'nın sayıları **silinmedi, damgalandı** — kayıt tahrif edilmez.

⚠️ `--onceki-onbellek` KALDIRILDI: önbellek artık içerik-adresli, devralma zaten otomatik.
Eski `{mod}:{id}` önbellekleri (cp2c, $3,68) devralınamaz — onlar klip 900 ile üretildi,
yani hakem girdileri farklı; devralmak 900 hatasını taşımak olurdu.

Kullanım:
  python scripts/puanlama/valid_trap_cache.py --run-dir outputs/eval/cp/cp09-butceli-1024-512 \
      --out outputs/eval/cp/cp2-r-kor-payda/valid_trap_cache.json
"""
import argparse
import json
import os
import sys

# ── scripts/ yol köprüsü (T5, 2026-09-07) ────────────────────────────────────
# Kardeş modüller alt klasörlere bölündükten SONRA da bulunsun diye scripts/ kökü, tüm
# alt klasörleri ve repo kökü sys.path'e girer. Uzantısız `import X` bu köprü olmadan
# taşımada SESSİZCE kırılır: ImportError çalışma zamanında, bazen GPU koşusunun ortasında.
# ⚠️ 26 dosyada BİREBİR aynı; değiştirirsen hepsinde değiştir (grep: "yol köprüsü").
import os, sys
_K = os.path.dirname(os.path.abspath(__file__))
_K = _K if os.path.basename(_K) == "scripts" else os.path.dirname(_K)
sys.path[:0] = [_K, *(os.path.join(_K, _d) for _d in sorted(os.listdir(_K))
                      if os.path.isdir(os.path.join(_K, _d)) and _d[0] not in "_."),
                os.path.dirname(_K)]
# ─────────────────────────────────────────────────────────────────────────────

from llm_client import gateway_of, make_client, resolve, seen_providers  # noqa: E402
# TEK KAYNAK (tuzak 2.9): kör istem, anahtar, klip ve hakem çağrısı — hepsi oradan.
from score_abstention import (GECERLILIK_ONBELLEK, SOURCE_CLIP,  # noqa: E402
                              gecerlilik_anahtari, judge_gecerlilik, onbellek_isabeti,
                              onbellek_kaydi, onbellek_oku, onbellek_yaz)

# Hangi modun geçerliliği nereden okunur. `alan=None` → hakeme GİTMEZ, sabit.
MOD_KAYNAK = {
    "m2":  {"alan": "referans",       "sabit": None},
    "m2b": {"alan": "context_shown",  "sabit": None},
    "m3":  {"alan": None,             "sabit": True},   # ADR-0048 m.2 — bağlam boş
}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--run-dir", required=True,
                   help="detay dosyalarının bulunduğu koşu klasörü (m{mod}_{etiket}_detail.jsonl)")
    p.add_argument("--out", required=True)
    p.add_argument("--tags", nargs="+", default=["base_th", "tg_v1_th", "gem_th"],
                   help="bağlam-aynılığı doğrulaması için özne etiketleri")
    p.add_argument("--modes", nargs="+", default=["m2", "m2b", "m3"])
    p.add_argument("--sadece-teyit", default=None,
                   help="koşu dizini — yalnız `abst_{mod}_{tag}_teyit.jsonl` içinde verdict="
                        "FABRICATE olan id'ler damgalanır. Gerekçe: kabul ölçütü `teyit ∧ kör`, "
                        "yani teyitten düşen kalemin damgası HİÇBİR yerde kullanılmıyor. "
                        "⚠️ Bedeli: havuz geneli geçerlilik oranı ölçülmez (yalnız kabul "
                        "adaylarınınki). O oran gerekiyorsa bu bayrak VERİLMEZ.")
    p.add_argument("--judge-model", default="gpt-4o")
    p.add_argument("--gecerlilik-onbellek", default=GECERLILIK_ONBELLEK)
    p.add_argument("--budget-usd", type=float,
                   default=float(os.environ.get("OPENAI_BUDGET_USD", "5") or "5"))
    return p.parse_args()


def load_detail(run_dir, mode, tag):
    p = f"{run_dir}/{mode}_{tag}_detail.jsonl"
    if not os.path.exists(p):
        return None
    return {json.loads(l)["id"]: json.loads(l) for l in open(p, encoding="utf-8") if l.strip()}


def collect_items(run_dir, mode, tags, alan):
    """Kalemleri topla VE bağlamın özneler arası aynı olduğunu doğrula.

    Doğrulama zorunlu: `{mod}:{id}` GÖRÜNÜMÜ 'bağlam kalemin özelliğidir' varsayımına
    dayanıyor. Varsayım bozulursa görünüm sessizce yanlış olur — bu hattın hata sınıfı.
    Karşılaştırma TAM metin üzerinde: klipli karşılaştırma klipten sonraki ayrışmayı
    göremez (K-1 ile aynı hata sınıfı).
    """
    per_tag = {t: load_detail(run_dir, mode, t) for t in tags}
    per_tag = {t: d for t, d in per_tag.items() if d}
    if not per_tag:
        return None, None
    ids = sorted(set.intersection(*[set(d) for d in per_tag.values()]))
    if alan is None:
        return {i: None for i in ids}, []
    items, sapan = {}, []
    for i in ids:
        vals = {(per_tag[t][i].get(alan) or "") for t in per_tag}
        if len(vals) > 1:
            sapan.append(i)
        items[i] = next(iter(vals))
    return items, sapan


def main():
    a = parse_args()
    gateway = gateway_of()
    a.judge_model = resolve(a.judge_model, gateway)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    onbellek = onbellek_oku(a.gecerlilik_onbellek)
    kapi = {}

    def istemci():
        if not kapi:
            kapi["c"], _ = make_client()
        return kapi["c"]

    gorunum, meta, spent = {}, {}, 0.0
    print(f"[kör-payda] ortak önbellek: {a.gecerlilik_onbellek} ({len(onbellek)} kalem) · "
          f"klip {SOURCE_CLIP} (score_abstention'dan)")
    for mode in a.modes:
        cfg = MOD_KAYNAK[mode]
        items, sapan = collect_items(a.run_dir, mode, a.tags, cfg["alan"])
        if items is None:
            print(f"[kör-payda] {mode}: detay dosyası yok, atlandı"); continue
        if sapan:
            raise SystemExit(
                f"🚨 {mode}: bağlam {len(sapan)} kalemde özneler arası FARKLI (ör. {sapan[:5]}).\n"
                "   `{mod}:{id}` görünümü kurulamaz — geçerlilik kalem özelliği değil. DURDURULDU.")

        # Soruyu ilk öznenin detayından al (soru da kalem özelliği)
        first = load_detail(a.run_dir, mode, a.tags[0]) or \
            load_detail(a.run_dir, mode, next(t for t in a.tags if load_detail(a.run_dir, mode, t)))

        if a.sadece_teyit:
            tp = f"{a.sadece_teyit}/abst_{mode}_{a.tags[0]}_teyit.jsonl"
            if not os.path.exists(tp):
                raise SystemExit(f"🚨 --sadece-teyit verildi ama {tp} yok. Teyit adımı koştu mu?")
            tut = {r["id"] for r in json.load(open(tp, encoding="utf-8"))
                   if r.get("verdict") == "FABRICATE"}
            n0 = len(items)
            items = {i: v for i, v in items.items() if i in tut}
            print(f"[kör-payda] {mode}: --sadece-teyit → {n0} kalemden {len(items)}'i "
                  f"damgalanacak ({n0 - len(items)} kalem teyitten düştü, damgası kullanılmayacak)")

        if cfg["sabit"] is not None:
            for i in items:
                gorunum[f"{mode}:{i}"] = {"gecerli": cfg["sabit"], "kaynak": "TANIM",
                                          "reason": "bağlam boş — kaynak metni yok (ADR-0048 m.2)"}
            meta[mode] = {"n": len(items), "gecerli": len(items), "hakem": "YOK (tanım gereği)",
                          "maliyet_usd": 0.0}
            print(f"[kör-payda] {mode}: {len(items)}/{len(items)} GEÇERLİ — hakeme gitmedi (tanım)")
            continue

        n_valid, cost0, devralinan = 0, spent, 0
        for k, i in enumerate(items, 1):
            anahtar = gecerlilik_anahtari(first[i]["soru"], items[i])
            # 🚨 K1 (2026-08-06): bu betik ORTAK önbelleğe yazıyor ve `cp2c_kabul.sh` onu
            # `LLM_GATEWAY=openai` ile koşuyordu. Yığın denetimi `score_abstention`'dan
            # ithal ediliyor (tuzak 2.9 tek kaynak) — uyuşmazlıkta DUR, sessiz devralma yok.
            kayit = onbellek_isabeti(onbellek, anahtar, a.judge_model, gateway)
            if kayit is not None:
                devralinan += 1
            else:
                if spent >= a.budget_usd:
                    raise SystemExit(f"BÜTÇE doldu (${spent:.3f}) — görünüm YARIM, yazılmadı")
                d, c = judge_gecerlilik(istemci(), a.judge_model, first[i]["soru"], items[i])
                spent += c
                kayit = onbellek[anahtar] = onbellek_kaydi(
                    not d.get("source_answers"), d.get("reason"), a.judge_model, gateway)
            g = kayit["gecerli"]
            n_valid += 1 if g else 0
            gorunum[f"{mode}:{i}"] = {"gecerli": g, "kaynak": kayit["hakem"],
                                      "kapi": kayit["kapi"], "reason": kayit["reason"],
                                      "valid_trap_anahtari": anahtar}
            if k % 20 == 0:
                print(f"  {mode} {k}/{len(items)} geçerli={n_valid} ${spent:.4f}", flush=True)
        meta[mode] = {"n": len(items), "gecerli": n_valid,
                      "gecerli_orani": round(n_valid / len(items), 4),
                      "devralinan": devralinan, "yeni_hakem": len(items) - devralinan,
                      "hakem": a.judge_model, "maliyet_usd": round(spent - cost0, 4)}
        print(f"[kör-payda] {mode}: {n_valid}/{len(items)} GEÇERLİ "
              f"({n_valid/len(items):.3f}) ${spent-cost0:.4f}"
              + (f" · {devralinan} ortak önbellekten, {len(items)-devralinan} yeni hakem"
                 if devralinan else ""))
    onbellek_yaz(a.gecerlilik_onbellek, onbellek)

    out = {
        "olcum": "cevaba KÖR valid_trap — `{mod}:{id}` GÖRÜNÜMÜ (ADR-0048 · ADR-0049 m.2)",
        "alet": "score_abstention.py (TEK kaynak, tuzak 2.9) — bu betik yalnız görünüm üretir",
        "run_dir": a.run_dir, "judge_model": a.judge_model, "judge_gateway": gateway,
        "judge_providers": seen_providers(), "temperature": 0, "clip": SOURCE_CLIP,
        "ortak_onbellek": a.gecerlilik_onbellek,
        "baglam_ayniligi_dogrulandi": True,
        "sadece_teyitten_gecenler": a.sadece_teyit or None,
        "mod_ozet": meta, "toplam_maliyet_usd": round(spent, 4),
        "not": "Skorlama (PAY) hakemi gpt-4o-mini OLARAK KALIR; bu bir kürasyon etiketi. "
               "verdict yeniden hesaplanmaz — cevaba bağlılığı meşrudur.",
        "cache": gorunum,
    }
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\n[kör-payda] {len(gorunum)} kalem → {a.out}  (toplam ${spent:.4f})")


if __name__ == "__main__":
    main()
