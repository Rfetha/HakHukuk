#!/usr/bin/env python3
"""Eşleştirilmiş alt kümede A1 — tuzak 2.4'ün aleti.

Coverage kollar arasında farklıysa ham A1 kıyası elmayla armuttur: az cevaplayan kol, kendi
seçtiği KOLAY dilimde ölçülür. base soruların %57,5'ini, `tgta_v1` %78,75'ini cevaplıyor — yani
"base'in A1'i daha yüksek" cümlesi bu kontrol yapılmadan kurulamaz.

⚠️ Kol başına İKİ dosya gerekir: `cevap` yalnız `*_detail.jsonl`'de, `faithfulness` yalnız
`gnd_*.jsonl`'de. `id` üzerinden birleştirilir; `gnd`'de karşılığı olmayan bir `detail` kaydı
SESSİZCE ATLANMAZ, KeyError verir (payda kaymasın).

Bu hattın hata sınıfı **sessiz yanlışlık**. Üç kapı buna karşı:
  1. **Hakem yığını** — kolların `gnd_*_summary.json`'undaki `(judge_model, judge_gateway)`
     çiftleri karşılaştırılır (ADR-0029 · tuzak 2.7). Uyuşmazlık çıktıya
     `hakem_yigini_uyusuyor: false` damgası basar + stderr'e uyarı yazar. Patlatmaz: bu bir
     post-hoc analiz aleti, ham veriyi görmek meşru — ama **damgasız sayı raporlanamaz.**
  2. **`faithfulness = None`** kesişime girerse ValueError (id'leri yazarak). Sessizce paydadan
     düşürmek YASAK — `rescore_answered.macro()` düşürüyor, iki A1 yolu ayrışır (tuzak 2.16).
  3. **`mode` kayıttan okunur** (`rescore_answered` kalıbı, ADR-0044). `--mode` yalnız
     doğrulama/üzerine-yazmadır; kayıttakiyle çelişirse uyarı üretir.

⚠️ `n_kesisim` **ayırt ediciliği ölçmez.** Mutlak A1'ler tavana yakınken (0,93-0,99) n=40'ın
36'sı berabere olabilir — asıl büyüklük `n_ayrisan` ("etkin n"). Kapıyı ona kur.

Kullanım (ikili — geriye uyum):
  python scripts/erisim_korpus/eslesmis_a1.py \\
    --detail-a outputs/eval/cp/cp09-butceli-1024-512/m1_base_th_detail.jsonl \\
    --gnd-a    outputs/eval/gorev/g1-eslesmis-a1/gnd_m1_base_th_or.jsonl \\
    --detail-b outputs/eval/cp/cp3-supurme-ham/m1_tg_ta_ham_th_detail.jsonl \\
    --gnd-b    outputs/eval/cp/cp3-supurme-ham/gnd_m1_tg_ta_ham_th.jsonl \\
    --etiket-a base --etiket-b tgta_v1

Kullanım (k kollu — TEK PAYDA, Görev 9 Adım 9.5'in istediği satır):
  python scripts/erisim_korpus/eslesmis_a1.py \\
    --kol d_base.jsonl:g_base.jsonl:base \\
    --kol d_v2.jsonl:g_v2.jsonl:BİZ_v2 \\
    --kol d_fl.jsonl:g_fl.jsonl:FL_ACIK
"""
import argparse
import datetime
import itertools
import json
import os
import statistics
import subprocess
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
from score_abstention import exact_reject  # noqa: E402  — TEK kaynak (tuzak 2.9)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _id_sirasi(x):
    return (len(x), x)


def _yukle(yol):
    kayitlar = {}
    with open(yol, encoding="utf-8") as f:
        for satir in f:
            if satir.strip():
                k = json.loads(satir)
                kayitlar[str(k["id"])] = k
    return kayitlar


def _hakem_yigini(gnd_yol):
    """`gnd_X.jsonl` → `gnd_X_summary.json`'daki `(judge_model, judge_gateway)` çifti.

    Özet dosyası yoksa `None` — **bilinmiyor ≠ uyuşuyor.** Model kimliği normalize EDİLMEZ
    (`compare_runs.judge_stack` precedent'i): `gpt-4o-mini` ile `openai/gpt-4o-mini` farklı
    yığınlardır ve tam olarak bu fark yakalanmak istenir.
    """
    if not gnd_yol.endswith(".jsonl"):
        return None
    yol = gnd_yol[: -len(".jsonl")] + "_summary.json"
    if not os.path.exists(yol):
        return None
    with open(yol, encoding="utf-8") as f:
        ozet = json.load(f)
    return (ozet.get("judge_model"), ozet.get("judge_gateway"))


def _cevaplayanlar(detail, mode_override, etiket, uyarilar):
    """Cevaplayanlar kümesi + fiilen kullanılan modlar. Mod KAYITTAN okunur (ADR-0044)."""
    cevaplayan, modlar = set(), set()
    for i, k in detail.items():
        kayit_mod = k.get("mode")
        if mode_override is not None and kayit_mod is not None and mode_override != kayit_mod:
            uyarilar.append(f"{etiket}: id={i} kayıt modu {kayit_mod!r} ≠ --mode {mode_override!r}"
                            f" → --mode uygulandı")
        mod = mode_override if mode_override is not None else kayit_mod
        modlar.add(mod)
        if not exact_reject(k.get("cevap", ""), mod):
            cevaplayan.add(i)
    return cevaplayan, modlar


def _ayrisma(va, vb):
    """Eşleştirilmiş farkların dağılımı — `n_kesisim`in gizlediği "etkin n"."""
    d = [x - y for x, y in zip(va, vb)]
    return {
        "n_ayrisan": sum(1 for x in d if x != 0),
        "n_berabere": sum(1 for x in d if x == 0),
        "a_lehine": sum(1 for x in d if x > 0),
        "b_lehine": sum(1 for x in d if x < 0),
        "fark_sd": statistics.stdev(d) if len(d) > 1 else None,
    }


def eslesmis_a1(kollar, mode=None):
    """k kolun HEPSİNİN cevapladığı kalemlerde A1 makrosu — tek payda.

    `kollar`: `(detail_yolu, gnd_yolu, etiket)` üçlülerinden oluşan liste (k ≥ 2).
    Çekinme tespiti tek kaynaktan (`score_abstention.exact_reject`) gelir; regex kopyası
    çoğaltmak tuzak 2.9'dur.
    """
    kollar = list(kollar)
    if len(kollar) < 2:
        raise ValueError(f"en az İKİ kol gerekir, {len(kollar)} verildi")
    etiketler = [e for _, _, e in kollar]
    if len(set(etiketler)) != len(etiketler):
        raise ValueError(f"kol etiketleri benzersiz olmalı: {etiketler}")

    d = {e: _yukle(dp) for dp, _, e in kollar}
    g = {e: _yukle(gp) for _, gp, e in kollar}

    uyarilar, cevaplayan, modlar = [], {}, set()
    for _, _, e in kollar:
        cevaplayan[e], m = _cevaplayanlar(d[e], mode, e, uyarilar)
        modlar |= m

    ortak = sorted(set.intersection(*(set(d[e]) for e in etiketler)), key=_id_sirasi)
    kesisim = [i for i in ortak if all(i in cevaplayan[e] for e in etiketler)]
    if not kesisim:
        raise ValueError("eşleştirilmiş kesişim BOŞ — kıyas kurulamaz")

    eksik = sorted({i for i in kesisim for e in etiketler if i not in g[e]}, key=_id_sirasi)
    if eksik:
        raise KeyError(f"gnd kaydı olmayan id'ler: {eksik[:5]} (toplam {len(eksik)}) "
                       f"— kollar: {etiketler}")

    # Ö1 · sessizce düşürmek YASAK: payda kayar ve `rescore_answered` yolundan ayrışır.
    bos = sorted({i for i in kesisim for e in etiketler
                  if g[e][i].get("faithfulness") is None}, key=_id_sirasi)
    if bos:
        raise ValueError(f"faithfulness=None olan id'ler kesişimde: {bos[:5]} "
                         f"(toplam {len(bos)}) — kollar: {etiketler}. Sessizce düşürülmez "
                         f"(payda kayar, tuzak 2.16); önce gnd kaydını düzelt.")

    degerler = {e: [g[e][i]["faithfulness"] for i in kesisim] for e in etiketler}
    a1 = {e: statistics.fmean(degerler[e]) for e in etiketler}

    farklar, ayrisma = {}, {}
    for x, y in itertools.combinations(etiketler, 2):
        farklar[f"{x}−{y}"] = a1[x] - a1[y]
        ayrisma[f"{x}−{y}"] = _ayrisma(degerler[x], degerler[y])

    yiginlar = {e: _hakem_yigini(gp) for _, gp, e in kollar}
    kume = set(yiginlar.values())
    uyusuyor = None if None in kume else len(kume) == 1

    r = {
        "n_kesisim": len(kesisim),
        "n_ortak_id": len(ortak),
        "n_cevaplayan": {e: len(cevaplayan[e]) for e in etiketler},
        "a1_kollar": a1,
        "farklar": farklar,
        "ayrisma": ayrisma,
        "hakem_yigini": {e: (list(v) if v else None) for e, v in yiginlar.items()},
        "hakem_yigini_uyusuyor": uyusuyor,
        "mode": sorted(str(m) for m in modlar),
        "girdiler": {e: {"detail": dp, "gnd": gp} for dp, gp, e in kollar},
        "git_sha": subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                                  capture_output=True, text=True).stdout.strip(),
        "uretildi": datetime.datetime.now().isoformat(timespec="seconds"),
        "uyarilar": uyarilar,
        "id_listesi": kesisim,
    }
    if len(kollar) == 2:
        a, b = etiketler
        r.update({
            "n_cevaplayan_a": len(cevaplayan[a]), "n_cevaplayan_b": len(cevaplayan[b]),
            "a1_a": a1[a], "a1_b": a1[b], "fark": a1[a] - a1[b],
            **ayrisma[f"{a}−{b}"],
        })

    if uyusuyor is not True:
        durum = "BİLİNMİYOR (özet dosyası yok)" if uyusuyor is None else "UYUŞMUYOR"
        print(f"[eslesmis_a1] 🚨 hakem yığını {durum}: "
              f"{ {e: v for e, v in yiginlar.items()} }\n"
              f"  Farklı hakem/gateway ile üretilmiş sayılar kıyaslanamaz (ADR-0029 · tuzak 2.7).\n"
              f"  Çıktı damgalandı: hakem_yigini_uyusuyor={uyusuyor} — damgasız raporlama YASAK.",
              file=sys.stderr)
    for u in uyarilar[:5]:
        print(f"[eslesmis_a1] ⚠️ mod çelişkisi — {u}", file=sys.stderr)
    return r


def ikili(detail_a, gnd_a, detail_b, gnd_b, mode=None, etiket_a="A", etiket_b="B"):
    """İki kollu çağrı — `eslesmis_a1`'in özel hâli (geriye uyum)."""
    return eslesmis_a1([(detail_a, gnd_a, etiket_a), (detail_b, gnd_b, etiket_b)], mode)


def _kol_ayristir(s):
    parca = s.split(":")
    if len(parca) != 3:
        raise argparse.ArgumentTypeError(
            f"--kol biçimi DETAIL:GND:ETİKET olmalı, alınan: {s!r}")
    return tuple(parca)


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--kol", action="append", default=[], type=_kol_ayristir,
                   metavar="DETAIL:GND:ETİKET",
                   help="tekrarlanabilir — k kollu tek-payda eşleştirme")
    for ad in ("a", "b"):
        p.add_argument(f"--detail-{ad}")
        p.add_argument(f"--gnd-{ad}")
        p.add_argument(f"--etiket-{ad}")
    p.add_argument("--mode", default=None,
                   help="ADR-0044 — YALNIZ doğrulama/üzerine-yazma. Varsayılan: KAYITTAN okunur")
    p.add_argument("--out", default="")
    a = p.parse_args()

    kollar = list(a.kol)
    if not kollar:
        alan = ("detail_a", "gnd_a", "etiket_a", "detail_b", "gnd_b", "etiket_b")
        eksik = [f"--{f.replace('_', '-')}" for f in alan if not getattr(a, f)]
        if eksik:
            p.error(f"ya --kol (≥2 kez) ya da ikili bayrakların tamamı gerekir; eksik: {eksik}")
        kollar = [(a.detail_a, a.gnd_a, a.etiket_a), (a.detail_b, a.gnd_b, a.etiket_b)]

    r = eslesmis_a1(kollar, a.mode)
    cev = " · ".join(f"{e} {n}" for e, n in r["n_cevaplayan"].items())
    print(f"eşleştirilmiş n = {r['n_kesisim']}  (ortak id {r['n_ortak_id']} · cevaplayan {cev})")
    print(f"  mod = {', '.join(r['mode'])}  ·  hakem yığını uyuşuyor = {r['hakem_yigini_uyusuyor']}")
    genislik = max(len(e) for e in r["a1_kollar"])
    for e, v in r["a1_kollar"].items():
        print(f"  A1 {e:<{genislik}} = {v:.4f}")
    for cift, fark in r["farklar"].items():
        ay = r["ayrisma"][cift]
        x, y = cift.split("−")
        sd = "—" if ay["fark_sd"] is None else f"{ay['fark_sd']:.4f}"
        print(f"  fark ({cift}) = {fark:+.4f}")
        # ⚠️ n_kesisim değil, AYIRT EDİCİ büyüklük bu satırdır.
        print(f"    etkin n = {ay['n_ayrisan']}  (berabere {ay['n_berabere']} · "
              f"{x} lehine {ay['a_lehine']} · {y} lehine {ay['b_lehine']} · fark_sd {sd})")

    if a.out:
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=2)
            f.write("\n")


if __name__ == "__main__":
    main()
