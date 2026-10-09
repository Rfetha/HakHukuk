#!/usr/bin/env python
"""RAFT context paketleme — gold madde + N hard-negative distractor (ORTAK MODÜL).

Hem eval (`gen_eval_grounded.py --distractors`) hem eğitim verisi (`build_sft_v2b.py`) AYNI
paketlemeyi kullanır → eval dağılımı = eğitim dağılımı (ADR-0013 / V2_PLAN §5.2). Tek yerden
değişsin, ikisi sapmasın.

Distractor seçimi = HARD-NEGATIVE: aynı kanun, komşu madde no öncelikli (gerçek retriever'ı
taklit eder; rastgele distractor eval'i kolaylaştırır → reddedildi, ADR-0013). Yetmezse rastgele
başka-kanun ile tamamlanır.

⚠️ k=4 distractor ve hard-negative yaklaşıklığı RAFT'ın İngilizce-QA setlerinden ekstrapolasyon
(V2_PLAN §5.1-A). Gerçek RAG retriever kurulunca (Adım 0) dağılımı onunla kalibre et.
"""
import json
import re

# Çok-kaynak (RAFT/distractor) sistem promptu — TEK KAYNAK. Hem eval (gen_eval_grounded M1/M3)
# hem eğitim (build_sft_v2b) bunu kullanır → eğitim ve eval AYNI talimatı görür (ADR-0013).
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

from hakhukuk.cekirdek.istem import SISTEM_COK_KAYNAK as SYSTEM_PROMPT_RAG_MULTI


def madde_ord(madde_no):
    """'MADDE 24' / 'Madde 24/A' → 24 (sıralama için ilk sayı); yoksa None."""
    m = re.search(r"\d+", str(madde_no or ""))
    return int(m.group()) if m else None


def _norm(v):
    return "" if v is None else str(v).strip()


def load_madde_pool(path):
    """mevzuat_maddeler.jsonl → (recs:list, by_kanun:dict[kanun_no -> list[rec]]).

    rec = {kanun_no, kanun_adi, madde_no, text}. Boş text atlanır.
    """
    recs, by_kanun = [], {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            t = (r.get("text") or "").strip()
            if not t:
                continue
            rec = {
                "kanun_no": _norm(r.get("kanun_no")),
                "kanun_adi": _norm(r.get("kanun_adi")),
                "madde_no": _norm(r.get("madde_no")),
                "text": t,
            }
            recs.append(rec)
            by_kanun.setdefault(rec["kanun_no"], []).append(rec)
    return recs, by_kanun


def labeled_chunk(rec, text=None):
    """Kaynağı ETİKETLE (Kanun adı + Madde no) → model atıf no'sunu uydurmasın, etiketten
    kopyalasın (gen_eval_grounded ile aynı mantık)."""
    t = text if text is not None else rec.get("text", "")
    return f"{_norm(rec.get('kanun_adi'))} {_norm(rec.get('madde_no'))}\n{t}".strip()


def sample_distractors(gold, recs, by_kanun, n, rng):
    """gold (kanun_no/madde_no/text) için n hard-negative distractor rec döndür.

    1) aynı kanun, farklı madde, madde-no yakınlığına göre sırala (komşu öncelik)
    2) yetmezse rastgele başka-kanun ile tamamla
    """
    gk = _norm(gold.get("kanun_no"))
    gm = _norm(gold.get("madde_no"))
    gtext = gold.get("text", "")
    same = [r for r in by_kanun.get(gk, [])
            if r["madde_no"] != gm and r["text"] != gtext]
    go = madde_ord(gm)
    if go is not None:
        same.sort(key=lambda r: abs((madde_ord(r["madde_no"]) or 10**9) - go))
    else:
        rng.shuffle(same)
    picked = same[:n]
    if len(picked) < n:                       # fallback: başka kanun
        others = [r for r in recs if r["kanun_no"] != gk]
        rng.shuffle(others)
        seen = {id(r) for r in picked}
        for r in others:
            if id(r) in seen:
                continue
            picked.append(r)
            if len(picked) >= n:
                break
    return picked[:n]


def pack_context(gold_rec, gold_text, recs, by_kanun, n_distractors, rng, include_gold=True):
    """RAFT context paketle.

    gold_rec  : {kanun_no, kanun_adi, madde_no} (soru tohumundan)
    gold_text : gold madde GERÇEK metni (mevzuat join'inden)
    include_gold=True  → M1/grounded dilim (gold context'TE)
    include_gold=False → M2-M3/abstention dilim (gold ÇIKARILMIŞ, sadece distractor)

    Dönüş: (chunks: list[str] etiketli+karışık, gold_in_context: bool)
    """
    gold = {
        "kanun_no": gold_rec.get("kanun_no"),
        "kanun_adi": gold_rec.get("kanun_adi"),
        "madde_no": gold_rec.get("madde_no"),
        "text": gold_text,
    }
    distractors = sample_distractors(gold, recs, by_kanun, n_distractors, rng)
    chunks = [labeled_chunk(d) for d in distractors]
    if include_gold:
        chunks.append(labeled_chunk(gold_rec, text=gold_text))
    rng.shuffle(chunks)
    return chunks, include_gold


def format_sources_block(chunks):
    """Etiketli chunk listesini NUMARALI tek kaynak bloğuna çevir (prompt'a gömülür)."""
    if not chunks:
        return "(İlgili kaynak bulunamadı.)"
    return "\n\n".join(f"[KAYNAK {i+1}]\n{c}" for i, c in enumerate(chunks))
