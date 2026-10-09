#!/usr/bin/env python
"""HakHukuk Eval — #1 OOD held-out dilimi (v3-görülmemiş kanunlar). TRAIN'e DOKUNMAZ.

Sorun (build_eval_ood.py raporladı): held-out (v3-eğitiminde geçmeyen) kanunlarda SORU yok;
test.jsonl SADECE 11 görülen kanun içeriyor → trap_ood mevcut kaynaklarla kurulamıyordu.

ÇÖZÜM (bu script): held-out kanunlar için GROUNDED-SENTETİK soru üret (gerçek madde → gpt-4o-mini
Q&A + faithfulness hakemi), cevaplanamayanı ELE, sonra AYNI held-out kanunun kardeşlerinden
MAX-Jaccard eval-mirror tuzağı kur (build_eval_sets.py:138 birebir). expected=abstain.

Şema canon trap.jsonl ile uyumlu (gen_eval_grounded idx[kanun_no|madde_no] JOIN edebilsin):
  {messages, kanun_adi, kanun_no, madde_no(=TUZAK), gold_madde_no, expected, _overlap, _set, ...}

Sızıntı=0: held-out kanunlar yapısal olarak 11-dışı; AYRICA üretilen gold + tuzak madde metni
train/dev/canon-trap/core'da distractor/gold olarak GÖRÜLMÜŞ mü diye seen_txt ile de dışlanır.
Deterministik seed=3407. Kanon DEĞİL — DRAFT.

Kullanım:
  python scripts/veri_hazirlik/build_eval_ood_qa.py --per-law 7 --keep-per-law 5 --min-dogruluk 8
Çıktı: data/eval/genelleme/ood_qa.jsonl (üretilen sorular) + data/eval/genelleme/trap_ood.jsonl (eval-mirror tuzak)
"""
import argparse
import collections
import json
import os
import random
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

from build_eval_sets import toks, load_madde, MADDE_PATH
from build_eval_ood import (
    is_gecici, mnum, jacc, norm,
    build_exclusion, seen_chunk_keys, seen_laws, _tkey,
)
from gen_grounded import (
    usable, GEN_SYSTEM, GEN_TEMPLATE, parse_gen, clean_text,
    PRICE_IN, PRICE_OUT, MAX_MADDE_CHARS,
)

# v3-görülen 11 kanun (held-out = bunların DIŞI). seen_laws() ile de teyit edilir.
SEEN_LAWS = {"1475", "2004", "4721", "4857", "5237", "5271",
             "6098", "6100", "6284", "634", "6502"}

# Held-out + vatandaş/uzman-ilgili + usable madde bol, FARKLI hukuk alanları (çeşitlilik).
HELDOUT_LAWS = [
    "2918",  # KARAYOLLARI TRAFİK KANUNU        (trafik — vatandaş)
    "5510",  # SOSYAL SİGORTALAR VE GSS         (emeklilik/sağlık — vatandaş)
    "6458",  # YABANCILAR VE ULUSLARARASI KORUMA(oturma/koruma — vatandaş)
    "5846",  # FİKİR VE SANAT ESERLERİ          (telif — vatandaş)
    "6769",  # SINAİ MÜLKİYET KANUNU            (marka/patent)
    "5275",  # CEZA VE GÜVENLİK TEDBİRLERİNİN İNFAZI (infaz)
    "1136",  # AVUKATLIK KANUNU                 (avukat-müvekkil — uzman)
]

GEN_MODEL = os.environ.get("GEN_MODEL", "gpt-4o-mini")

# faithfulness hakemi (gen_grounded ile AYNI ölçek; JSON dogruluk/sadelik)
JUDGE_SYSTEM = (
    "Bir vatandaş hukuk sorusu, kaynak kanun maddesi ve bir cevap verilecek. İKİ eksende "
    "1-10 puanla:\n"
    "1) dogruluk: Cevap KAYNAK MADDEYE sadık mı, uydurma/çelişki var mı? "
    "(10=tam sadık, 1=çelişkili/uydurma)\n"
    "2) cevaplanabilir: Soru YALNIZCA bu kaynak maddeden tam cevaplanabiliyor mu? "
    "(10=madde soruyu tam karşılıyor, 1=madde soruyu cevaplamıyor)\n"
    'SADECE JSON: {"dogruluk": <1-10>, "cevaplanabilir": <1-10>, "gerekce": "<tek cümle>"}'
)


def gen_gpt(client, model, prompt):
    r = client.chat.completions.create(
        model=model, temperature=0.7,
        messages=[{"role": "system", "content": GEN_SYSTEM},
                  {"role": "user", "content": prompt}])
    u = r.usage
    return r.choices[0].message.content, u.prompt_tokens, u.completion_tokens


def judge_gpt(client, model, soru, madde, cevap):
    user = f"SORU:\n{soru}\n\nKAYNAK MADDE:\n{madde[:MAX_MADDE_CHARS]}\n\nCEVAP:\n{cevap}"
    r = client.chat.completions.create(
        model=model, temperature=0, response_format={"type": "json_object"},
        messages=[{"role": "system", "content": JUDGE_SYSTEM},
                  {"role": "user", "content": user}])
    d = json.loads(r.choices[0].message.content)
    u = r.usage
    return (float(d.get("dogruluk", 0)), float(d.get("cevaplanabilir", 0)),
            d.get("gerekce", ""), u.prompt_tokens, u.completion_tokens)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--per-law", type=int, default=7, help="kanun başına ÜRETİLECEK aday soru")
    p.add_argument("--keep-per-law", type=int, default=5, help="kanun başına TUTULACAK (kalite sonrası)")
    p.add_argument("--min-dogruluk", type=float, default=8.0)
    p.add_argument("--min-cevaplanabilir", type=float, default=8.0)
    p.add_argument("--seed", type=int, default=3407)
    p.add_argument("--out-dir", default="data/eval")
    p.add_argument("--budget", type=float, default=float(os.environ.get("OPENAI_BUDGET_USD", "3")))
    a = p.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    rng = random.Random(a.seed)

    by_key, by_law = load_madde(MADDE_PATH)  # by_law: kanun_no -> [(madde_no, text≥250char)]
    # law name + usable madde havuzu (held-out kanunlar için)
    law_name = {}
    usable_pool = collections.defaultdict(list)  # kanun_no -> [(madde_no, text)]
    for line in open(MADDE_PATH, encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        kn, mn = norm(r.get("kanun_no")), norm(r.get("madde_no"))
        law_name.setdefault(kn, r.get("kanun_adi"))
        if kn in HELDOUT_LAWS and not is_gecici(mn) and usable(r):
            usable_pool[kn].append((mn, (r.get("text") or "").strip()))

    seen = seen_laws()
    excl = build_exclusion()
    seen_txt = seen_chunk_keys()
    heldout = [kn for kn in HELDOUT_LAWS if kn not in seen]
    assert set(heldout) == set(HELDOUT_LAWS), "Seçilen kanunlar v3-görülende çıktı!"

    print(f"[envanter] v3 GÖRÜLEN kanun: {len(seen)} -> {sorted(seen)}")
    print(f"[envanter] held-out seçilen: {len(heldout)} -> "
          f"{[(kn, law_name[kn][:30]) for kn in heldout]}")
    print(f"[envanter] sızıntı-dışlama (kanun,madde) çifti: {len(excl)}")
    print(f"[envanter] eğitimde görülen madde-metni anahtarı: {len(seen_txt)}")
    for kn in heldout:
        print(f"    kn={kn} usable madde havuzu: {len(usable_pool[kn])}")
    print()

    from openai import OpenAI
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit("[ood] OPENAI_API_KEY yok (.env yükle)")
    client = OpenAI(api_key=key)

    spent = 0.0
    kept_qa = []   # her biri: dict (ood_qa.jsonl satırı)
    for kn in heldout:
        pool = list(usable_pool[kn])
        rng.shuffle(pool)
        # gold olarak seçilen madde de sızıntı/seen_txt kontrolünden geçmeli
        cand = [(mn, t) for (mn, t) in pool
                if (kn, mnum(mn)) not in excl and _tkey(t) not in seen_txt]
        picked = 0
        law = law_name[kn]
        for (mn, text) in cand:
            if picked >= a.keep_per_law:
                break
            if spent >= a.budget:
                print(f"[ood] BÜTÇE doldu (${spent:.3f}) → durdu")
                break
            prompt = GEN_TEMPLATE.format(kanun=law, madde_no=mn, text=text[:MAX_MADDE_CHARS])
            try:
                raw, it, ot = gen_gpt(client, GEN_MODEL, prompt)
                spent += it * PRICE_IN + ot * PRICE_OUT
            except Exception as e:
                print(f"[ood] kn={kn} {mn} ÜRETİM HATA: {e}")
                continue
            soru, cevap = parse_gen(raw)
            if not soru or not cevap:
                print(f"[ood] kn={kn} {mn} parse başarısız, atla")
                continue
            try:
                dog, cev, ger, it, ot = judge_gpt(client, GEN_MODEL, soru, text, cevap)
                spent += it * PRICE_IN + ot * PRICE_OUT
            except Exception as e:
                print(f"[ood] kn={kn} {mn} hakem hata: {e}")
                continue
            ok = dog >= a.min_dogruluk and cev >= a.min_cevaplanabilir
            flag = "✓KEEP" if ok else "✗drop"
            print(f"[ood] kn={kn} {law[:24]:24s} {str(mn):10s} dog={dog:.0f} cev={cev:.0f} {flag}")
            if not ok:
                continue
            kept_qa.append({
                "messages": [{"role": "user", "content": soru},
                             {"role": "assistant", "content": clean_text(cevap)}],
                "kanun_adi": law, "kanun_no": kn, "gold_madde_no": mn,
                "gold_text": text,
                "_dogruluk": dog, "_cevaplanabilir": cev, "_gerekce": ger,
                "_set": "ood_qa",
            })
            picked += 1
        # per-law aday tükendiyse per_law sınırını da dene (keep_per_law > picked ise devam)
        # (yukarıdaki döngü zaten cand'ı sırayla dener; keep_per_law kadar tutar)

    # ---------- ood_qa.jsonl yaz ----------
    qa_path = os.path.join(a.out_dir, "ood_qa.jsonl")
    with open(qa_path, "w", encoding="utf-8") as f:
        for r in kept_qa:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\n[ood] üretilen+doğrulanan soru: {len(kept_qa)} → {qa_path}")
    print(f"[ood] GPT maliyet: ${spent:.4f}")

    # ---------- trap_ood.jsonl: eval-mirror (AYNI held-out kanunun kardeşi, max-Jaccard) ----------
    trap = []
    used_trap = set()
    for r in kept_qa:
        kn = r["kanun_no"]
        gold_mn = r["gold_madde_no"]
        gold_tok = toks(r["gold_text"])
        if not gold_tok:
            continue
        # AYNI kanunun kardeşleri (≥250char havuz), gold DEĞİL, geçici DEĞİL, sızıntı/seen_txt DIŞI
        sibs = [(mn, t) for (mn, t) in by_law.get(kn, [])
                if mnum(mn) != mnum(gold_mn)
                and not is_gecici(mn)
                and (kn, mnum(mn)) not in excl
                and (kn, mnum(mn)) not in used_trap
                and _tkey(t) not in seen_txt]
        if not sibs:
            print(f"[trap_ood] kn={kn} {gold_mn}: kardeş tuzak bulunamadı, atla")
            continue
        # build_eval_sets:138 birebir — gold ile en yüksek Jaccard-örtüşen kardeş
        wmn, wsrc = max(sibs, key=lambda s: jacc(toks(s[1]), gold_tok))
        ov = jacc(toks(wsrc), gold_tok)
        trap.append({
            "messages": r["messages"],
            "kanun_adi": r["kanun_adi"], "kanun_no": kn,
            "madde_no": wmn,               # TUZAK madde (gen_eval enjekte eder) → idx JOIN
            "gold_madde_no": gold_mn,      # asıl doğru madde
            "expected": "abstain",
            "_overlap": round(ov, 3), "_set": "trap_ood",
            "_trap_text": wsrc, "_gold_text": r["gold_text"],
        })
        used_trap.add((kn, mnum(wmn)))

    trap_path = os.path.join(a.out_dir, "trap_ood.jsonl")
    with open(trap_path, "w", encoding="utf-8") as f:
        for t in trap:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")

    ovs = sorted(t["_overlap"] for t in trap)
    med = ovs[len(ovs) // 2] if ovs else 0
    law_dist = collections.Counter(t["kanun_adi"] for t in trap)
    # SIZINTI kontrol
    leak = [t for t in trap if (norm(t["kanun_no"]), mnum(t["madde_no"])) in excl]
    leak_txt = [t for t in trap if _tkey(t["_trap_text"]) in seen_txt]
    print(f"\n[trap_ood] {len(trap)} örnek → {trap_path}")
    print(f"[trap_ood] _overlap med={med} min={ovs[0] if ovs else 0} max={ovs[-1] if ovs else 0}")
    print(f"[trap_ood] kanun dağılım: {dict(law_dist)}")
    print(f"[trap_ood] SIZINTI (yapısal kanun,madde): {len(leak)} | (metin seen_txt): {len(leak_txt)}")

    # ---------- EDA: 8 tam örnek EKRANA BAS ----------
    print("\n" + "=" * 74)
    print("EDA — trap_ood tam örnekler (SORU / GOLD-madde / TUZAK-madde / _overlap)")
    print("=" * 74)
    for i, t in enumerate(trap[:8]):
        print(f"\n--- Örnek {i+1} | {t['kanun_adi']} (kn={t['kanun_no']}) | _overlap={t['_overlap']} ---")
        print(f"SORU : {t['messages'][0]['content']}")
        print(f"GOLD-CEVAP: {t['messages'][1]['content'][:220]}")
        print(f"GOLD  [{t['gold_madde_no']}]: {t['_gold_text'][:300]}")
        print(f"TUZAK [{t['madde_no']}]: {t['_trap_text'][:300]}")


if __name__ == "__main__":
    main()
