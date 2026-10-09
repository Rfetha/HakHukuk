#!/usr/bin/env python
"""v2b SFT veri inşası — RAFT paketleme + kalite kapısı + replay + split (V2_PLAN §5.2).

İki alt-komut (Adım 2 = teacher-LLM cevap üretimi ARADA, ayrı/compute):

  pack      Adım 1 → soru↔gold tohumundan RAFT context paketle, P-dilimine ata.
            Çıktı = teacher-LLM GİRDİSİ (cevaplar henüz YOK).
            data/_ham_ve_ara/raft_packed.jsonl

  (— ARADA: B2 teacher-LLM packed.jsonl'a cevap üretir → answers.jsonl —)

  assemble  Adım 3/4/5 → cevapları al, DETERMİNİSTİK kapılardan geçir (verbatim⊂gold,
            atıf eşleşme, abstention-ifadesi), replay karıştır, split + chat-template yaz.
            data/train/raft/{train,validation,test}.jsonl

Hedge mekanizması = context-yeterliliği (V2_PLAN §5.2): P dilimi gold'u context'e koyar
(grounded), (1-P) dilimi gold'u ÇIKARIR (abstention). Base-prob YOK; tek knob = P.

NOT: Adım 3'teki faithfulness≥0.95 (LLM-judge) kapısı = B3, ayrı script (mevcut groundedness
hattı). Buradaki kapılar DETERMİNİSTİK (string/regex) — ucuz ön-eleme.

Kullanım:
  python scripts/veri_hazirlik/build_sft_v2b.py pack --p 0.8 --distractors 4 --seed 3407
  # (B2 cevap üretir → data/_ham_ve_ara/raft_answers.jsonl)
  python scripts/veri_hazirlik/build_sft_v2b.py assemble --answers data/_ham_ve_ara/raft_answers.jsonl \
         --replay data/train/replay_tr.jsonl --replay-frac 0.03
"""
import argparse
import json
import os
import random
import re

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

SEED_PATH = "data/train/grounded_qa/train.jsonl"   # soru↔gold tohumu (v1 CEVAPLARI kullanılmaz)
MADDE_PATH = "data/corpus/mevzuat_maddeler.jsonl"
OUT_DIR = "data/train/raft"

ABSTAIN_RE = re.compile(
    r"düzenle(?:m[ie]yor|nmemiş|nmemekte)|yer al(?:m[ıi]yor|mamakta)|bulunma(?:maktadır|z|yor)|"
    r"kapsama(?:maktadır|z)|içerme(?:mektedir|z|miyor)|kaynak(?:lar)?da (?:bu|yok)",
    re.IGNORECASE)
QUOTE_RE = re.compile(r"##begin_quote##(.+?)##end_quote##", re.DOTALL)


def _norm(v):
    return "" if v is None else str(v).strip()


# Kaynak chunk'ı (madde metni) etiketi koruyarak kırp. Tek bir maddenin 12K token olması
# truncation'a yol açıyordu (%11.6 örnek >2048; cevap kesiliyordu, B-smoke 2026-06-24). Gerçek
# RAG retriever tam kanunu değil CHUNK döner → kırpmak deployment'a DAHA sadık. Gold chunk'ta
# cevabın ##begin_quote## span'i pencere içinde KORUNUR (yoksa "context'te olmayanı alıntıla"
# = halüsinasyon öğretiriz). Cevap (target) ASLA kırpılmaz.
_KAYNAK_SPLIT = re.compile(r"\n\n\[KAYNAK \d+\]\n")


def _clip_chunk(chunk, cap_chars, quote=None):
    nl = chunk.find("\n")
    if nl < 0:
        return chunk[:cap_chars]
    head, body = chunk[:nl], chunk[nl + 1:]
    if len(body) <= cap_chars:
        return chunk
    if quote:                                    # gold: alıntı span'ini pencerede tut
        q = re.sub(r"\s+", " ", quote).strip().strip("\"“”„«»'‘’")[:50]
        pos = body.find(q)
        if pos < 0:                              # normalize farkı → boşluksuz dene
            pos = re.sub(r"\s+", " ", body).find(q)
        if pos >= 0:
            start = max(0, pos - cap_chars // 2)
            end = start + cap_chars
            return (head + "\n" + ("…" if start > 0 else "") + body[start:end]
                    + ("…" if end < len(body) else ""))
    return head + "\n" + body[:cap_chars] + "…"  # distractor: baştan kırp


def clip_sources_block(sources_block, answer, gold_label, cap_chars):
    """Her [KAYNAK i] chunk'ını cap_chars'a kırp; gold chunk'ta answer'ın quote'unu koru.
    gold_label = '{gold_kanun_adi} {gold_madde_no}' (chunk baş satırı ile eşleşir)."""
    chunks = [re.sub(r"^\[KAYNAK \d+\]\n", "", c) for c in _KAYNAK_SPLIT.split(sources_block)]
    m = QUOTE_RE.search(answer or "")
    quote = m.group(1) if m else None
    gl = _norm(gold_label)
    out = []
    for c in chunks:
        is_gold = bool(gl) and c.split("\n", 1)[0].strip() == gl   # baş satır TAM eşleşme
        out.append(_clip_chunk(c, cap_chars, quote=quote if is_gold else None))
    return "\n\n".join(f"[KAYNAK {i+1}]\n{c}" for i, c in enumerate(out))


def load_madde_index(path):
    """(kanun_no|madde_no) → en dolu GERÇEK madde metni (gen_eval_grounded ile AYNI mantık).

    DİKKAT: sft_v1 kayıtlarındaki `source` alanı madde metni DEĞİL, provenance etiketi
    ('grounded_gpt-4o-mini'). Gerçek gold metni bu index'ten join edilir — yoksa gate
    her grounded örneği 'alıntı gold'da değil' ile reddeder (B1 bug, 2026-06-14).
    """
    idx = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            k = f"{_norm(r.get('kanun_no'))}|{_norm(r.get('madde_no'))}"
            t = (r.get("text") or "").strip()
            if t and len(t) > len(idx.get(k, "")):
                idx[k] = t
    return idx


def extract_seed(rec, madde_idx):
    """sft_v1 kaydından (soru, gold_text, meta) çıkar. gold_text madde index'ten JOIN."""
    msgs = rec.get("messages", [])
    soru = next((m["content"] for m in msgs if m.get("role") == "user"), None)
    meta = {"kanun_no": rec.get("kanun_no"), "kanun_adi": rec.get("kanun_adi"),
            "madde_no": rec.get("madde_no")}
    k = f"{_norm(meta['kanun_no'])}|{_norm(meta['madde_no'])}"
    gold_text = madde_idx.get(k, "")
    return soru, gold_text, meta


# ============================================================ v2c yeni dilimler
# İki dilim eklenir (v2c, roadmap §7 AÇ-KOŞ-2/3): counterfactual (anti-parametric-leak) ve
# abstain_trap (yanlış-ama-makul TEK kaynak → gerekçeli red). İkisi de TEACHER-LLM'siz
# (deterministik + ablasyon-temiz, §3-E). Ana rng akışını BOZMAMAK için dönüşüm kararı AYRI
# crng ile verilir → dönüşmeyen grounded/abstain satırlar v2b ile birebir aynı kalır (reuse+regresyon).

# --- A2 counterfactual: gold'daki somut olguyu sistematik boz → model KAYNAĞA uysun, ezbere değil.
# NOT: Türk hukuk metni sayıları çoğunlukla KELİME yazar ("otuz gün", "yüzde yirmi") — digit
# regex tek başına ~%0.3 tutar (ampirik 2026-07-02). Kelime-sayı desteği ŞART (grounded'ın ~%32'si).
_NUM_WORDS = ["bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz", "on",
              "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan", "yüz"]
_NUM_SET = "|".join(_NUM_WORDS)
_FACT_PATTERNS = [
    (re.compile(r"\b(\d+)\s*(gün|ay|yıl|hafta|saat)\b"), "int"),
    (re.compile(r"%\s*(\d+)"), "int"),
    (re.compile(r"\b(\d[\d.]*)\s*(TL|lira)\b", re.IGNORECASE), "para"),
    (re.compile(r"\b(on\s?sekiz|onsekiz|yirmi\s?bir|\d+)\s*yaş", re.IGNORECASE), "yas"),
    (re.compile(r"\byüzde\s+(" + _NUM_SET + r")\b", re.IGNORECASE), "word"),
    (re.compile(r"\b(" + _NUM_SET + r")\s+(gün|ay|yıl|hafta|saat)\b", re.IGNORECASE), "word"),
]
_YAS_MAP = {"on sekiz": "yirmi bir", "onsekiz": "yirmi bir", "yirmi bir": "on sekiz"}


def _alt_int(n, crng):
    """n'i akla-yatkın ama FARKLI bir tam sayıya çevir (deterministik, crng seed'li)."""
    cands = [n * 2, n + 15, n + 30, max(1, n - 7), max(1, n // 2)]
    cands = [c for c in cands if c != n and c > 0]
    return crng.choice(cands) if cands else n + 1


def _alt_word(w, crng):
    """Kelime-sayıyı akla-yatkın ama FARKLI bir kelime-sayıya çevir (liste-içi kaydırma)."""
    wl = w.lower()
    if wl not in _NUM_WORDS:
        return None
    idx = _NUM_WORDS.index(wl)
    offs = [2, 3, -2, 4, -3, 5]
    crng.shuffle(offs)
    for o in offs:
        cand = _NUM_WORDS[(idx + o) % len(_NUM_WORDS)]
        if cand != wl:
            return cand
    return None


def make_counterfactual(gold_text, crng):
    """gold_text'teki İLK somut olguyu boz. Dönüş: (cf_gold_text, cf_quote) veya (None, None).
    cf_quote = değiştirilmiş değeri içeren cümle parçası (cf_gold_text'ten BİREBİR → gate ⊂ geçer)."""
    for rx, kind in _FACT_PATTERNS:
        m = rx.search(gold_text)
        if not m:
            continue
        orig = m.group(0)
        if kind == "yas":
            val = m.group(1).lower()
            key = "on sekiz" if "sekiz" in val else ("yirmi bir" if "bir" in val else None)
            if key:
                new = orig.replace(m.group(1), _YAS_MAP[key]) if not m.group(1).isdigit() \
                    else orig.replace(m.group(1), str(_alt_int(int(m.group(1)), crng)))
            else:
                new = orig.replace(m.group(1), str(_alt_int(int(m.group(1)), crng)))
        elif kind == "int":
            n = int(m.group(1))
            new = orig.replace(m.group(1), str(_alt_int(n, crng)), 1)
        elif kind == "word":
            nw = _alt_word(m.group(1), crng)
            if not nw:
                continue
            new = orig.replace(m.group(1), nw, 1)
        else:  # para (ondalık olabilir) → tam kısmı 2×
            num = m.group(1)
            try:
                base = int(float(num.replace(".", "")))
                new = orig.replace(num, str(base * 2), 1)
            except ValueError:
                continue
        if new == orig:
            continue
        start, end = m.span()
        cf_gold = gold_text[:start] + new + gold_text[end:]
        # cf_quote: yeni değeri içeren cümleyi cf_gold'dan çıkar (nokta/satır sınırı), ≤200 char.
        npos = start
        left = max(cf_gold.rfind(". ", 0, npos), cf_gold.rfind("\n", 0, npos)) + 1
        right = min([p for p in (cf_gold.find(". ", npos + len(new)),
                                 cf_gold.find("\n", npos + len(new))) if p != -1] or [len(cf_gold)])
        quote = cf_gold[left:right].strip()
        if len(quote) > 200:
            # yeni-değer merkezli 200'lük pencere
            c = npos - left
            s = max(0, c - 100)
            quote = quote[s:s + 200].strip()
        if new.split()[0] not in quote and new not in quote:
            quote = new + " — " + quote           # değer kesinlikle quote'ta olsun (⊂ garanti)
        return cf_gold, quote
    return None, None


# --- A1 abstain_trap: gold'u çıkar, aynı kanunun KONU-KOMŞUSU yanlış maddesini koy → gerekçeli red.
def _tok(s):
    return set(re.findall(r"[a-zçğıöşü]{4,}", (s or "").lower()))


def pick_wrong_neighbor(gold_rec, gold_text, soru, pool_by_kanun, crng, K=20):
    """Aynı kanun_no içinde 2≤|Δmadde|≤K, soruyla EN DÜŞÜK leksik örtüşen maddeyi seç (yanlış-ama-makul).
    Dönüş: wrong_rec veya None (kanun tek-maddeli/yetersizse)."""
    gk = _norm(gold_rec.get("kanun_no"))
    gm = _norm(gold_rec.get("madde_no"))
    go = raft_pack.madde_ord(gm)
    cands = [r for r in pool_by_kanun.get(gk, [])
             if r["madde_no"] != gm and r["text"] != gold_text]
    if not cands:
        return None
    if go is not None:
        near = [r for r in cands
                if raft_pack.madde_ord(r["madde_no"]) is not None
                and 2 <= abs(raft_pack.madde_ord(r["madde_no"]) - go) <= K]
        pool = near or cands
    else:
        pool = cands
    qtok = _tok(soru)
    crng.shuffle(pool)                                   # eşit-örtüşmede deterministik çeşitlilik
    pool.sort(key=lambda r: (len(qtok & _tok(r["text"][:400])),
                             abs((raft_pack.madde_ord(r["madde_no"]) or 10**9) - (go or 0))))
    return pool[0]


def build_trap_context(wrong_rec, pool_recs, gk, n_far, prng):
    """wrong madde (aynı kanun, yanlış) + n_far UZAK distractor (başka kanun), karıştır."""
    others = [r for r in pool_recs if r["kanun_no"] != gk]
    prng.shuffle(others)
    chunks = [raft_pack.labeled_chunk(wrong_rec)] + \
             [raft_pack.labeled_chunk(d) for d in others[:n_far]]
    prng.shuffle(chunks)
    return chunks


# ---------------------------------------------------------------- pack (Adım 1)
def cmd_pack(a):
    os.makedirs(a.out_dir, exist_ok=True)
    seeds = [json.loads(l) for l in open(a.seeds, encoding="utf-8") if l.strip()]
    pool_recs, pool_by_kanun = raft_pack.load_madde_pool(a.madde_path)
    madde_idx = load_madde_index(a.madde_path)   # GERÇEK gold metni için JOIN tablosu
    rng = random.Random(a.seed)

    out_path = os.path.join(a.out_dir, "packed.jsonl")
    from collections import Counter
    kinds = Counter()
    n_skip = n_cf_miss = n_trap_miss = 0
    with open(out_path, "w", encoding="utf-8") as f:
        for i, rec in enumerate(seeds):
            soru, gold_text, meta = extract_seed(rec, madde_idx)
            if not soru or not gold_text:
                n_skip += 1
                continue
            gold_rec = {"kanun_no": meta["kanun_no"], "kanun_adi": meta["kanun_adi"],
                        "madde_no": meta["madde_no"]}
            include_gold = rng.random() < a.p          # P → grounded, (1-P) → abstain
            prng = random.Random(a.seed + i)           # örnek-başına deterministik distractor
            chunks, gold_in = raft_pack.pack_context(
                gold_rec, gold_text, pool_recs, pool_by_kanun, a.distractors, prng,
                include_gold=include_gold)
            slice_kind = "grounded" if gold_in else "abstain"
            extra = {}                                  # dilime-özel alanlar

            # v2c dönüşüm — AYRI crng (ana rng/prng akışı BOZULMAZ → v2b grounded/abstain reuse geçerli)
            crng = random.Random(a.seed * 7919 + i)
            if gold_in and a.cf_frac > 0 and crng.random() < a.cf_frac:
                cf_gold, cf_quote = make_counterfactual(gold_text, crng)
                if cf_gold:                             # gold chunk'ı cf_gold ile yeniden paketle
                    chunks, _ = raft_pack.pack_context(
                        gold_rec, cf_gold, pool_recs, pool_by_kanun, a.distractors,
                        random.Random(a.seed + i), include_gold=True)
                    slice_kind = "counterfactual"
                    extra = {"cf_gold_text": cf_gold, "cf_quote": cf_quote}
                else:
                    n_cf_miss += 1                      # olgu bulunamadı → grounded kalır
            elif (not gold_in) and a.trap_frac > 0 and crng.random() < a.trap_frac:
                wrong = pick_wrong_neighbor(gold_rec, gold_text, soru, pool_by_kanun, crng, a.trap_k)
                if wrong:
                    chunks = build_trap_context(
                        wrong, pool_recs, meta["kanun_no"], a.distractors - 1,
                        random.Random(a.seed + i))
                    slice_kind = "abstain_trap"
                    extra = {"trap_kanun_adi": wrong["kanun_adi"], "trap_madde_no": wrong["madde_no"]}
                else:
                    n_trap_miss += 1                    # uygun komşu yok → abstain (RAG-ıska) kalır

            kinds[slice_kind] += 1
            row = {
                "id": i, "soru": soru,
                "sources_block": raft_pack.format_sources_block(chunks),
                "slice": slice_kind,
                "gold_kanun_adi": meta["kanun_adi"], "gold_madde_no": meta["madde_no"],
                "gold_kanun_no": meta["kanun_no"], "gold_text": gold_text,
                # teacher-LLM/şablon (B2) 'answer' alanını doldurur
            }
            row.update(extra)
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"[pack] {out_path}: {dict(kinds)} skip={n_skip} "
          f"(P={a.p}, k={a.distractors}, cf_frac={a.cf_frac}, trap_frac={a.trap_frac}; "
          f"cf_miss={n_cf_miss} trap_miss={n_trap_miss})")
    print(f"[pack] sıradaki (B2): teacher-LLM/şablon her satıra 'answer' üret → answers.jsonl")
    print(f"[pack]   grounded       → CoT + ##begin_quote## [gold'dan birebir] + (KANUN, Madde X)  [API]")
    print(f"[pack]   counterfactual → şablon: cf_quote'u alıntıla + atıf (kaynağa uy, ezbere değil) [API'siz]")
    print(f"[pack]   abstain        → 'Verilen kaynaklarda ... bulunmuyor' (RAG-ıska)               [şablon]")
    print(f"[pack]   abstain_trap   → 'Sağlanan {{yanlış madde}} farklı hususu düzenler...' (red)    [şablon]")


# ------------------------------------------------------------ assemble (Adım 3/4/5)
def _gate(row):
    """DETERMİNİSTİK kapı (Adım 3) — geçen örnek + ret sebebi döndür."""
    ans = (row.get("answer") or "").strip()
    if not ans:
        return False, "boş cevap"
    slc = row["slice"]
    if slc in ("grounded", "counterfactual"):
        # counterfactual: referans = cf_gold_text (bozulmuş gold) — gerçek gold'a bakılırsa
        # "alıntı gold'da değil" ile HAKSIZ reddedilir (roadmap §7 AÇ-KOŞ-2.4).
        ref = row.get("cf_gold_text") if slc == "counterfactual" else row.get("gold_text")
        m = QUOTE_RE.search(ans)
        if not m:
            return False, "verbatim-quote yok"
        quote = re.sub(r"\s+", " ", m.group(1)).strip()
        quote = quote.strip("\"“”„«»'‘’").strip()    # teacher metni tırnağa sarabilir → soyut
        ref_norm = re.sub(r"\s+", " ", ref or "")
        if quote and quote[:60] not in ref_norm:     # alıntı gerçekten kaynakta mı (⊂)
            return False, "alıntı kaynakta değil (uydurma quote)"
        gold_ord = raft_pack.madde_ord(row.get("gold_madde_no"))
        if gold_ord is not None and str(gold_ord) not in ans:
            return False, "atıf madde no eşleşmiyor"
        return True, "ok"
    else:  # abstain / abstain_trap dilimi
        if not ABSTAIN_RE.search(ans):
            return False, "abstention ifadesi yok (uydurmuş olabilir)"
        return True, "ok"


def cmd_assemble(a):
    os.makedirs(a.out_dir, exist_ok=True)
    rows = [json.loads(l) for l in open(a.answers, encoding="utf-8") if l.strip()]
    kept, rejected = [], []
    for r in rows:
        ok, reason = _gate(r)
        (kept if ok else rejected).append((r, reason))

    # chat-template (Adım 5 format)
    def to_chat(r):
        sb = r["sources_block"]
        if a.max_chunk_chars > 0:                # uzun-madde truncation fix (2026-06-24)
            gold_label = f"{_norm(r.get('gold_kanun_adi'))} {_norm(r.get('gold_madde_no'))}"
            sb = clip_sources_block(sb, r.get("answer", ""), gold_label, a.max_chunk_chars)
        return {
            "messages": [
                {"role": "system", "content": raft_pack.SYSTEM_PROMPT_RAG_MULTI},
                {"role": "user", "content": f"KAYNAKLAR:\n{sb}\n\nSORU: {r['soru']}"},
                {"role": "assistant", "content": r["answer"]},
            ],
            "slice": r["slice"],
            "gold_madde_no": r.get("gold_madde_no"),
            "gold_kanun_no": r.get("gold_kanun_no"),
        }

    examples = [to_chat(r) for r, _ in kept]

    # Adım 4 — replay karıştır (forgetting'e karşı, §5.1-D: %1-5)
    n_replay = 0
    if a.replay and os.path.exists(a.replay):
        rep = [json.loads(l) for l in open(a.replay, encoding="utf-8") if l.strip()]
        n_replay = int(len(examples) * a.replay_frac / max(1e-9, (1 - a.replay_frac)))
        random.Random(a.seed).shuffle(rep)
        for r in rep[:n_replay]:
            r["slice"] = "replay"
            examples.append(r)
    elif a.replay:
        print(f"[assemble] ⚠️ replay yolu yok ({a.replay}) → replay ATLANDI (forgetting riski, §5.1-D)")

    # Adım 5 — split (deterministik)
    random.Random(a.seed).shuffle(examples)
    n = len(examples)
    n_test = max(1, int(n * a.test_frac))
    n_val = max(1, int(n * a.val_frac))
    test, val, train = examples[:n_test], examples[n_test:n_test + n_val], examples[n_test + n_val:]

    for name, part in [("train", train), ("validation", val), ("test", test)]:
        p = os.path.join(a.out_dir, f"{name}.jsonl")
        with open(p, "w", encoding="utf-8") as f:
            for ex in part:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    # kapı raporu (B3 deterministik kısmı)
    from collections import Counter
    rej_reasons = Counter(reason for _, reason in rejected)
    report = {
        "in": len(rows), "kept": len(kept), "rejected": len(rejected),
        "reject_reasons": dict(rej_reasons), "replay_added": n_replay,
        "split": {"train": len(train), "validation": len(val), "test": len(test)},
    }
    json.dump(report, open(os.path.join(a.out_dir, "assemble_report.json"), "w",
                           encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"[assemble] → {a.out_dir}/{{train,validation,test}}.jsonl  (+ assemble_report.json)")
    print("[assemble] NOT: faithfulness≥0.95 LLM-judge kapısı (B3) AYRI: groundedness hattı.")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    pp = sub.add_parser("pack", help="Adım 1 — RAFT context paketle (teacher-LLM girdisi)")
    pp.add_argument("--seeds", default=SEED_PATH)
    pp.add_argument("--madde-path", default=MADDE_PATH)
    pp.add_argument("--out-dir", default=OUT_DIR, help="çıktı dizini (v2c: data/train/<yeni-set>)")
    pp.add_argument("--p", type=float, default=0.8, help="grounded oranı (gold context'te); (1-P)=abstention")
    pp.add_argument("--distractors", type=int, default=4, help="örnek başına distractor (k)")
    pp.add_argument("--seed", type=int, default=3407)
    # v2c yeni dilimler (roadmap §7). Default 0 → v2b davranışı (geriye uyumlu). v2c: --cf-frac 0.10 --trap-frac 0.40
    pp.add_argument("--cf-frac", type=float, default=0.0,
                    help="grounded'ın counterfactual'a dönüşen oranı (A2 anti-parametric-leak, ~0.10)")
    pp.add_argument("--trap-frac", type=float, default=0.0,
                    help="abstain'in abstain_trap'e dönüşen oranı (A1 yanlış-kaynak red, ~0.40)")
    pp.add_argument("--trap-k", type=int, default=20,
                    help="abstain_trap yanlış-komşu madde arama penceresi (2≤|Δmadde|≤K)")
    pp.set_defaults(func=cmd_pack)

    ap2 = sub.add_parser("assemble", help="Adım 3/4/5 — kapı + replay + split")
    ap2.add_argument("--answers", required=True, help="B2 çıktısı (packed + 'answer' alanı)")
    ap2.add_argument("--out-dir", default=OUT_DIR, help="çıktı dizini (v2c: data/train/<yeni-set>)")
    ap2.add_argument("--replay", default=None, help="genel TR instruction jsonl (chat-template)")
    ap2.add_argument("--replay-frac", type=float, default=0.03, help="replay oranı (§5.1-D: %1-5)")
    ap2.add_argument("--max-chunk-chars", type=int, default=900,
                     help="kaynak madde başına char tavanı (uzun-madde truncation fix; 0=kapalı). "
                          "900≈243 tok → 5 chunk 2048'e sığar, gold quote span korunur (2026-06-24)")
    ap2.add_argument("--val-frac", type=float, default=0.05)
    ap2.add_argument("--test-frac", type=float, default=0.05)
    ap2.add_argument("--seed", type=int, default=3407)
    ap2.set_defaults(func=cmd_assemble)

    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
