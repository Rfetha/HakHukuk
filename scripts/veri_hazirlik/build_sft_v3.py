#!/usr/bin/env python
"""v3 ORPO veri inşası — ADIM 1: zor near-miss TRAP aday havuzu (v3_recipe §5.1).

v2b/v2c'ye DOKUNMAZ (negatif-kanıt olarak dokunulmadan kalsın, kayıt disiplini). v2b'nin
raft_pack + seed/gold-join yardımcılarını IMPORT ederek reuse eder.

v2c RED'inin iki kök-sebebinden BİRİNİ (Bulgu-2, veri-sertliği) düzeltir:
  · v2c `pick_wrong_neighbor` = soruyla EN DÜŞÜK örtüşen yanlış madde → KOLAY-reddedilir.
  · eval M2 = gold-KAYNAKla EN YÜKSEK örtüşen kardeş → ZOR-reddedilir.
  · v3 `pick_hard_neighbor` = EVAL-AYNASI: gold-kaynakla EN YÜKSEK örtüşen kardeş
    (build_eval_sets.py:138 ile BİREBİR aynı seçim) → eğitim-negatifi eval-sertliğiyle ÖZDEŞ.

⚠️ KARAR (2026-07-03, veri-doğrulamalı, kullanıcı onaylı): recipe Q3 sertliği SORU'ya çıpalıyordu
ama ölçüm gösterdi ki soru-çıpası eval M2'nin gold-çıpasıyla örtüşmüyor (yalnız %6.6 kapsama →
v2c Bulgu-2 hatasının başka eksende tekrarı). Çözüm: sertlik ÇIPASI eval ile HİZALANDI
(gold-kaynak MAX). Geçerlilik ise artık lexical DEĞİL → ADIM 4 judge'a taşındı (aşağı bkz).
Ayrıntı: research_log v3 ADIM 1 girişi + ADR-0015.

Geçerlilik kapısı (v3_recipe Q5, EVAL-AYNASI için revize):
  · SERTLİK = overlap(yanlış, GOLD-KAYNAK)↑  → eval M2 ile özdeş (yanlış madde doğruya benzer, zor)
  · GEÇERLİLİK = "yanlış madde soruyu GERÇEKTEN cevaplıyor mu?" → SEMANTİK judge (ADIM 4).
    Lexical ov_gold TEK BAŞINA geçerlilik ölçemez (o artık sertlik ekseni) → yüksek-örtüşme
    kazara-cevaplama İHTİMALİNİ artırır ama garanti etmez (kardeş madde farklı hüküm olabilir);
    judge karar verir. `hi_overlap` bayrağı = judge-önceliği (funnel, geri bildirim-3).

Bu ADIM cevap ÜRETMEZ. Çıktı = zor-near-miss TRAP bağlamları + ov_gold/ov_q/hi_overlap metadata:
  · rejected (v2b fabrikasyonu)  → ADIM 2 (gen_v3_rejected.py, lokal model inference)
  · chosen   (muhakemeli-red)    → ADIM 3 (şablon)
  · τ kalibrasyonu               → ADIM 4 (judge)

Kullanım:
  python scripts/veri_hazirlik/build_sft_v3.py pack \
      --seeds data/train/grounded_qa/train.jsonl \
      --out-dir data/train/orpo_abstain --seed 3407
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

import raft_pack
# v2b'den reuse (v2b'yi ÇALIŞTIRMAZ — __main__ guard'lı, import güvenli).
from build_sft_v2b import (
    _norm, _tok, extract_seed, load_madde_index,
)

SEED_PATH = "data/train/grounded_qa/train.jsonl"
MADDE_PATH = "data/corpus/mevzuat_maddeler.jsonl"
OUT_DIR = "data/train/orpo_abstain"


def jaccard(a_toks, b_toks):
    """Jaccard örtüşme (eval build_eval_sets:138 ile AYNI metrik → eğitim-eval kıyaslanabilir)."""
    if not a_toks or not b_toks:
        return 0.0
    inter = len(a_toks & b_toks)
    return inter / (len(a_toks | b_toks) + 1)


def pick_hard_neighbor(gold_rec, gold_text, pool_by_kanun):
    """EVAL-AYNASI (build_eval_sets.py:138 ile BİREBİR): aynı kanunun TÜM kardeşleri içinden,
    gold-KAYNAK metnine EN YÜKSEK Jaccard örtüşen maddeyi seç (madde-mesafe penceresi YOK →
    eval ile aynı). Deterministik max → eval'in tuzak dağılımıyla özdeş.

    Dönüş: (wrong_rec, ov_gold) veya (None, 0.0). ov_gold = sertlik ekseni (eval M2 _overlap ile aynı).
    """
    gk = _norm(gold_rec.get("kanun_no"))
    gm = _norm(gold_rec.get("madde_no"))
    cands = [r for r in pool_by_kanun.get(gk, [])
             if r["madde_no"] != gm and r["text"] != gold_text]
    if not cands:
        return None, 0.0
    gtok = _tok(gold_text)
    if not gtok:
        return None, 0.0
    # eval build_eval_sets:138: max(sibs, key=Jaccard(sib_text, gold_source))
    best, best_ov = None, -1.0
    for r in cands:
        ov = jaccard(gtok, _tok(r["text"]))
        if ov > best_ov:
            best, best_ov = r, ov
    return best, best_ov


def build_trap_context(wrong_rec, pool_recs, gk, n_far, prng):
    """Tek yanlış-kaynak AĞIRLIKLI bağlam (v3_recipe Q8, eval M2 oracle yapısına eş).
    n_far=0 → yalnız yanlış madde (eval M2 birebir); n_far>0 → yanlış + uzak distractor."""
    chunks = [raft_pack.labeled_chunk(wrong_rec)]
    if n_far > 0:
        others = [r for r in pool_recs if r["kanun_no"] != gk]
        prng.shuffle(others)
        chunks += [raft_pack.labeled_chunk(d) for d in others[:n_far]]
        prng.shuffle(chunks)
    return chunks


def judge_flag(ov_gold, tau_hi):
    """EVAL-AYNASI revizesi: ov_gold artık SERTLİK ekseni (yüksek=zor, istenen). Geçerlilik
    lexical DEĞİL → judge (ADIM 4). Bu bayrak yalnız judge-ÖNCELİĞİ: çok-yüksek örtüşenler
    (τ_hi üstü) kazara-cevaplama ihtimali en yüksek → önce onları judge'la (funnel, geri bildirim-3)."""
    return "hi_overlap" if ov_gold > tau_hi else "ok"


def cmd_pack(a):
    os.makedirs(a.out_dir, exist_ok=True)
    seeds = [json.loads(l) for l in open(a.seeds, encoding="utf-8") if l.strip()]
    pool_recs, pool_by_kanun = raft_pack.load_madde_pool(a.madde_path)
    madde_idx = load_madde_index(a.madde_path)

    out_path = os.path.join(a.out_dir, "packed_v3.jsonl")
    kinds = collections.Counter()
    ov_q_all, ov_gold_all = [], []
    n_skip = n_no_neighbor = 0

    with open(out_path, "w", encoding="utf-8") as f:
        for i, rec in enumerate(seeds):
            soru, gold_text, meta = extract_seed(rec, madde_idx)
            if not soru or not gold_text:
                n_skip += 1
                continue
            gold_rec = {"kanun_no": meta["kanun_no"], "kanun_adi": meta["kanun_adi"],
                        "madde_no": meta["madde_no"]}
            # EVAL-AYNASI: yanlış-komşu = gold-kaynağa MAX örtüşen kardeş (deterministik, eval:138).
            wrong, ov_gold = pick_hard_neighbor(gold_rec, gold_text, pool_by_kanun)
            if wrong is None:
                n_no_neighbor += 1
                continue

            ov_q = jaccard(_tok(soru), _tok(wrong["text"]))   # diagnostik (sertlik değil)
            flag = judge_flag(ov_gold, a.tau_hi)

            # Tek-kaynak ağırlıklı bağlam (Q8): p_single olasılıkla yalnız yanlış madde.
            crng = random.Random(a.seed * 7919 + i)
            prng = random.Random(a.seed + i)
            n_far = 0 if crng.random() < a.p_single else (a.distractors)
            chunks = build_trap_context(wrong, pool_recs, meta["kanun_no"], n_far, prng)

            kinds[flag] += 1
            ov_q_all.append(ov_q)
            ov_gold_all.append(ov_gold)
            row = {
                "id": i, "soru": soru,
                "sources_block": raft_pack.format_sources_block(chunks),
                "slice": "abstain_trap_v3",
                "judge_flag": flag,              # "hi_overlap"=judge-önceliği (ADIM 4), "ok"=normal
                "ov_gold": round(ov_gold, 4),    # SERTLİK ekseni (eval M2 _overlap ile aynı metrik)
                "ov_q": round(ov_q, 4),          # diagnostik (soru-örtüşme)
                "n_far": n_far,
                "gold_kanun_adi": meta["kanun_adi"], "gold_madde_no": meta["madde_no"],
                "gold_kanun_no": meta["kanun_no"], "gold_text": gold_text,
                "trap_kanun_adi": wrong["kanun_adi"], "trap_madde_no": wrong["madde_no"],
                "trap_text": wrong["text"],
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    def pct(xs, p):
        if not xs:
            return 0.0
        s = sorted(xs)
        return round(s[min(len(s) - 1, int(len(s) * p))], 4)

    n = sum(kinds.values())
    print(f"[v3-pack] {out_path}: {n} trap adayı | judge_flag={dict(kinds)} "
          f"| skip={n_skip} no_neighbor={n_no_neighbor}")
    print(f"[v3-pack] ov_gold (SERTLİK = eval M2 _overlap ekseni): "
          f"p10={pct(ov_gold_all,.1)} p25={pct(ov_gold_all,.25)} med={pct(ov_gold_all,.5)} "
          f"p75={pct(ov_gold_all,.75)} p90={pct(ov_gold_all,.9)} max={pct(ov_gold_all,1.0)}")
    print(f"[v3-pack] ov_q (diagnostik, soru-örtüşme): "
          f"med={pct(ov_q_all,.5)} p90={pct(ov_q_all,.9)} max={pct(ov_q_all,1.0)}")
    print(f"[v3-pack] EVAL-AYNASI hedefi: ov_gold dağılımı eval M2 (_overlap med≈0.123 p90≈0.253) ile örtüşmeli.")
    print(f"[v3-pack] τ_hi={a.tau_hi} üstü = 'hi_overlap' judge-önceliği ({kinds.get('hi_overlap',0)} aday).")
    print(f"[v3-pack] sıradaki: ADIM 2 gen_v3_rejected.py (v2b fabrikasyonu) + ADIM 3 chosen şablon")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    pp = sub.add_parser("pack", help="ADIM 1 — zor near-miss trap aday havuzu + geçerlilik bant")
    pp.add_argument("--seeds", default=SEED_PATH)
    pp.add_argument("--madde-path", default=MADDE_PATH)
    pp.add_argument("--out-dir", default=OUT_DIR)
    pp.add_argument("--seed", type=int, default=3407)
    pp.add_argument("--p-single", type=float, default=0.7,
                    help="tek-kaynak (yalnız yanlış madde) olasılığı; kalanı yanlış+uzak-distractor (Q8)")
    pp.add_argument("--distractors", type=int, default=3,
                    help="çok-kaynak durumunda uzak distractor sayısı")
    pp.add_argument("--tau-hi", type=float, default=0.35,
                    help="judge-önceliği eşiği (ov_gold>τ_hi → 'hi_overlap', kazara-cevaplama şüphesi); ADIM 4")
    pp.set_defaults(func=cmd_pack)

    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
