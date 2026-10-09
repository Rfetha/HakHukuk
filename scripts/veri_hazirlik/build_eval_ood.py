#!/usr/bin/env python
"""HakHukuk Eval — GENELLEME dilimleri (v3 karnesi). TRAIN'e DOKUNMAZ, sadece yeni sınav kâğıdı üretir.

Mevcut `build_eval_sets.py` TRAP metodu tek-aile kör: hem train hem eval SADECE
"aynı-kanun leksik-komşu" tuzağını içerir. Bu script iki YENİ genelleme dilimi kurar:

  A) trap_xkanun : ÇAPRAZ-KANUN near-miss. Tuzak madde AYNI kanundan değil, TÜM havuzdan
                   FARKLI bir kanundan (kanun_no != sorunun kanunu) MAX-Jaccard ile seçilir.
                   = "başka kanunun konu-yakın maddesi" tuzağı. expected=abstain.

  B) trap_ood    : GÖRÜLMEMİŞ-KANUN held-out (aynı-kanun metodu, ama v3 eğitiminde HİÇ geçmeyen
                   kanunlardan). FEASIBILITY-FIRST: soru kaynağı test.jsonl held-out kanun
                   içermiyorsa KURULMAZ, blok raporlanır.

Şema mevcut trap.jsonl ile aynı (downstream eval scriptleri bu alanları okur):
  {messages, kanun_adi, kanun_no, madde_no(=TUZAK), gold_madde_no, expected, _overlap, _set, ...}

Sızıntı-dışlama: yeni tuzaklar train/dev/mevcut-trap/core_hard'da GEÇMEZ (kanun,madde bazında).
Deterministik: seed=3407. Kanon DEĞİL — DRAFT.

Kullanım:
  python scripts/veri_hazirlik/build_eval_ood.py --xkanun-n 35 --ood-n 35
Çıktı: data/eval/genelleme/trap_xkanun.jsonl (+ mümkünse data/eval/genelleme/trap_ood.jsonl)
"""
import argparse
import collections
import json
import os
import random
import re

# build_eval_sets'ten reuse (mevcut dosyayı DEĞİŞTİRMEDEN)
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

from build_eval_sets import norm, q_of, toks, load_madde, MADDE_PATH, TEST_PATH

# v3 eğitim-türevi + kanon eval dosyaları (sızıntı-dışlama + "görülen kanun" kaynağı)
V3_STRUCT = [
    "data/_ham_ve_ara/orpo_packed.jsonl",
    "data/_ham_ve_ara/orpo_rejected.jsonl",
    "data/train/orpo_abstain/dev.jsonl",
]
CANON_EVAL = ["data/eval/canon/trap.jsonl", "data/eval/canon/core_hard.jsonl"]


def load(f):
    return [json.loads(l) for l in open(f, encoding="utf-8") if l.strip()]


def mnum(s):
    """madde_no -> kanonik numara ('Madde 40'|'MADDE 40' -> '40'); eşleştirme için."""
    m = re.search(r"(\d+)", str(s or ""))
    return m.group(1) if m else str(s or "").strip().upper()


def jacc(a, b):
    return len(a & b) / (len(a | b) + 1)


def build_exclusion():
    """train/dev/mevcut-eval'de geçen (kanun_no, madde-num) çiftleri = kullanılamaz."""
    excl = set()
    for f in V3_STRUCT:
        for r in load(f):
            kn = norm(r.get("gold_kanun_no"))
            excl.add((kn, mnum(r.get("gold_madde_no"))))
            excl.add((kn, mnum(r.get("trap_madde_no"))))  # v3 tuzağı aynı kanundan
    for r in load("data/eval/canon/trap.jsonl"):
        kn = norm(r.get("kanun_no"))
        excl.add((kn, mnum(r.get("madde_no"))))
        excl.add((kn, mnum(r.get("gold_madde_no"))))
    for r in load("data/eval/canon/core_hard.jsonl"):
        excl.add((norm(r.get("kanun_no")), mnum(r.get("madde_no"))))
    excl.discard(("", ""))
    return excl


_WS = re.compile(r"\s+")


def _tkey(t):
    """madde metni → normalize edilmiş ilk-100-char anahtarı (seen-text eşleştirme)."""
    return _WS.sub(" ", (t or "").strip().lower())[:100]


def seen_chunk_keys():
    """v3 eğitiminde modele GÖSTERİLEN her madde metnini (gold + distractor + trap) yakala.
    packed_v3/rejected sources_block içindeki [KAYNAK] gövdelerini + dev trap/gold metinlerini
    normalize-prefix olarak toplar. Böylece çapraz-kanun tuzağı eğitimde distractor olarak
    geçmiş bir maddeye denk gelirse elenir (yapısal (kanun,madde) dışlaması distractor'ı kaçırır)."""
    keys = set()
    for f in ("data/_ham_ve_ara/orpo_packed.jsonl", "data/_ham_ve_ara/orpo_rejected.jsonl"):
        for r in load(f):
            sb = r.get("sources_block", "") or ""
            for chunk in re.split(r"\[KAYNAK[^\]]*\]", sb):
                lines = chunk.strip().split("\n", 1)
                body = lines[1] if len(lines) > 1 else ""   # 1. satır = "KANUN ADI MADDE X" başlığı
                if body.strip():
                    keys.add(_tkey(body))
            for fld in ("gold_text", "trap_text"):
                if r.get(fld):
                    keys.add(_tkey(r[fld]))
    for r in load("data/train/orpo_abstain/dev.jsonl"):
        if r.get("trap_text"):
            keys.add(_tkey(r["trap_text"]))
    keys.discard("")
    return keys


def seen_laws():
    """v3 eğitiminde GÖRÜLEN kanunlar (gold_kanun_no union)."""
    s = set()
    for f in V3_STRUCT:
        for r in load(f):
            s.add(norm(r.get("gold_kanun_no")))
    s.discard("")
    return s


def is_gecici(mn):
    """geçici (transitional) madde = değişiklik-tarihçesi boilerplate; eval için zayıf +
    tarih-listesi örtüşmesi tuzağı kirletir → hem soru hem tuzak havuzundan çıkar."""
    return "geçici" in (mn or "").lower() or "geçi̇ci" in (mn or "").lower()


def load_test_items(by_key):
    """test sorularını gold-madde metniyle eşle (geçici maddeler hariç)."""
    items = []
    for r in load(TEST_PATH):
        kn, mn = norm(r.get("kanun_no")), norm(r.get("madde_no"))
        if is_gecici(mn):
            continue
        src = by_key.get(f"{kn}|{mn}", "")
        q = q_of(r)
        if src and q:
            items.append({"rec": r, "kn": kn, "mn": mn, "src": src, "q": q,
                          "law": r.get("kanun_adi")})
    return items


def build_xkanun(items, by_law, law_name, excl, seen_txt, n, cap, rng):
    """Her soru için TÜM havuzdan FARKLI kanunun max-Jaccard maddesi = çapraz-kanun tuzak."""
    # tüm havuz maddelerinin token setlerini önceden hesapla (kanun bazında)
    pool = []  # (kanun_no, madde_no, tokens, text)
    for kn, lst in by_law.items():
        for mn, t in lst:
            if is_gecici(mn):                        # geçici madde tuzak havuzundan da çıkar
                continue
            pool.append((kn, mn, toks(t), t))
    rng.shuffle(items)
    out, seen_qlaw, used_trap = [], collections.Counter(), set()
    for it in items:
        if len(out) >= n:
            break
        if seen_qlaw[it["law"]] >= cap:
            continue
        gold_tok = toks(it["src"])
        if not gold_tok:
            continue
        best = None  # (ov, kn, mn)
        for (kn, mn, tk, t) in pool:
            if kn == it["kn"]:                       # farklı kanun şartı
                continue
            if (kn, mnum(mn)) in excl:               # yapısal sızıntı-dışlama
                continue
            if (kn, mnum(mn)) in used_trap:          # dosya-içi tekrar yok (aynı tuzağı 2 kez kullanma)
                continue
            if _tkey(t) in seen_txt:                 # eğitimde distractor/gold olarak görülmüş metin
                continue
            ov = jacc(tk, gold_tok)
            if best is None or ov > best[0]:
                best = (ov, kn, mn)
        if best is None:
            continue
        ov, tkn, tmn = best
        tsrc = next(t for (mn, t) in by_law[tkn] if mn == tmn)
        # ŞEMA (canon trap.jsonl ile aynı): kanun_adi/kanun_no/madde_no = TUZAK.
        # gen_eval_grounded idx["{kanun_no}|{madde_no}"] ile tuzak metnini JOIN eder ve
        # "{kanun_adi} {madde_no}" etiketiyle modele gösterir → burada TUZAK kanunu (farklı).
        # gold_* = sorunun ASIL (farklı kanundaki) doğru maddesi (enjekte edilmez, referans).
        out.append({
            "messages": it["rec"]["messages"],
            "kanun_adi": law_name.get(tkn, ""),       # TUZAK kanun adı (etiket)
            "kanun_no": tkn,                           # TUZAK kanun no  → idx JOIN
            "madde_no": tmn,                           # TUZAK madde     → idx JOIN
            "gold_kanun_adi": it["law"],              # sorunun asıl (farklı) kanunu
            "gold_kanun_no": it["kn"],
            "gold_madde_no": it["mn"],                 # asıl doğru madde
            "expected": "abstain",
            "_overlap": round(ov, 3), "_set": "trap_xkanun",
            "_trap_text": tsrc,                       # EDA/inceleme için (referans)
            "_gold_text": it["src"],
        })
        seen_qlaw[it["law"]] += 1
        used_trap.add((tkn, mnum(tmn)))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--xkanun-n", type=int, default=35)
    p.add_argument("--ood-n", type=int, default=35)
    p.add_argument("--seed", type=int, default=3407)
    p.add_argument("--out-dir", default="data/eval")
    a = p.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)

    by_key, by_law = load_madde(MADDE_PATH)
    law_name = {}
    for l in open(MADDE_PATH, encoding="utf-8"):
        if not l.strip():
            continue
        r = json.loads(l)
        law_name.setdefault(norm(r.get("kanun_no")), r.get("kanun_adi"))

    excl = build_exclusion()
    seen_txt = seen_chunk_keys()
    seen = seen_laws()
    items = load_test_items(by_key)
    test_laws = set(it["kn"] for it in items)
    heldout_laws_with_q = test_laws - seen

    print(f"[envanter] havuz kanun (>=250 madde): {len(by_law)}")
    print(f"[envanter] test soru öğesi: {len(items)} | test kanun: {len(test_laws)}")
    print(f"[envanter] v3 GÖRÜLEN kanun: {len(seen)} -> {sorted(seen)}")
    print(f"[envanter] held-out (soru olan görülmemiş) kanun: {len(heldout_laws_with_q)} -> {sorted(heldout_laws_with_q)}")
    print(f"[envanter] sızıntı-dışlama (kanun,madde) çifti: {len(excl)}")
    print(f"[envanter] eğitimde görülen madde-metni (gold+distractor+trap) anahtarı: {len(seen_txt)}")
    print()

    # ---------- A) trap_xkanun ----------
    cap = max(1, a.xkanun_n // 5)
    rng = random.Random(a.seed)
    xk = build_xkanun(items, by_law, law_name, excl, seen_txt, a.xkanun_n, cap, rng)
    with open(os.path.join(a.out_dir, "trap_xkanun.jsonl"), "w", encoding="utf-8") as f:
        for r in xk:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    ovs = sorted(r["_overlap"] for r in xk)
    med = ovs[len(ovs) // 2] if ovs else 0
    p90 = ovs[int(len(ovs) * 0.9)] if ovs else 0
    qlaw = collections.Counter(r["gold_kanun_adi"] for r in xk)
    tlaw = collections.Counter(r["kanun_adi"] for r in xk)
    print(f"[trap_xkanun] {len(xk)} örnek | _overlap med={med} p90={p90} min={ovs[0]} max={ovs[-1]}")
    print(f"[trap_xkanun] soru-kanun cap={cap} dağılım: {dict(qlaw)}")
    print(f"[trap_xkanun] tuzak-kanun dağılım (top): {tlaw.most_common(8)}")
    # sızıntı kontrol (tuzak = kanun_no|madde_no)
    leak = [r for r in xk if (norm(r['kanun_no']), mnum(r['madde_no'])) in excl]
    print(f"[trap_xkanun] SIZINTI (dışlamada olan tuzak): {len(leak)}")

    # ---------- B) trap_ood (feasibility) ----------
    if not heldout_laws_with_q:
        print()
        print("[trap_ood] BLOKLU: held-out (v3-görülmemiş) kanunlar için SORU yok.")
        print("           test.jsonl kanun kümesi == v3-görülen kanun kümesi (11=11).")
        print("           -> mevcut kaynaklarla kurulamaz. trap_ood.jsonl YAZILMADI.")
    else:
        print("[trap_ood] held-out kanunlarda soru VAR -> kurulabilir (bu dalda değiliz).")

    # 6-8 tam örnek EKRANA BAS (EDA-verify)
    print("\n" + "=" * 70)
    print("EDA — trap_xkanun tam örnekler (soru / gold-madde / TUZAK-madde / _overlap)")
    print("=" * 70)
    for i, r in enumerate(xk[:7]):
        print(f"\n--- Örnek {i+1} | _overlap={r['_overlap']} ---")
        print(f"SORU: {r['messages'][0]['content']}")
        print(f"GOLD  [{r['gold_kanun_adi']} (kn={r['gold_kanun_no']}) / {r['gold_madde_no']}]:")
        print(f"      {r['_gold_text'][:350]}")
        print(f"TUZAK [{r['kanun_adi']} (kn={r['kanun_no']}) / {r['madde_no']}]:")
        print(f"      {r['_trap_text'][:350]}")


if __name__ == "__main__":
    main()
