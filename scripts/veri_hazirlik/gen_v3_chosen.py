#!/usr/bin/env python3
"""v3 ADIM 3 — ORPO 'chosen' (muhakemeli-red şablonu). ORACLE-uyumlu (eval M2 = abstain-çifti framing).

v3_recipe Q4: chosen = muhakemeli-red şablonu (yanlış-madde KONUSUNU adlandırır → çekimser),
teacher'sız $0, rejected fabrikasyonuyla KIYASLANABİLİR UZUNLUK (format/uzunluk-bias↓).

Her satır için chosen = "Sağlanan {kanun} {madde}, {konu} düzenlemektedir; sorulan husus bu
maddede yer almamaktadır ..." → yanlış maddeyi ADIYLA + KONUSUYLA reddeder (muhakemeli),
uydurmadan çekimser kalır. ABSTAIN_RE + REJECT_RE'yi GEÇER (gate uyumlu). Uzman register.

Girdi: data/_ham_ve_ara/orpo_packed.jsonl (trap_text/trap_kanun_adi/trap_madde_no/soru).
Çıktı: data/_ham_ve_ara/orpo_chosen.jsonl  (id + "chosen" alanı; ADIM 6 paketleme id ile join).

Kullanım:
  python scripts/veri_hazirlik/gen_v3_chosen.py
  python scripts/veri_hazirlik/gen_v3_chosen.py --packed ... --out ...
"""
import argparse
import json
import os
import re
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
from build_sft_v2b import ABSTAIN_RE
from score_abstention import REJECT_RE

PACKED = "data/_ham_ve_ara/orpo_packed.jsonl"
OUT = "data/_ham_ve_ara/orpo_chosen.jsonl"

# Muhakemeli-red şablonları — {kanun} {madde} {konu} doldurulur. Hepsi ABSTAIN_RE+REJECT_RE geçer.
# Kıyaslanabilir uzunluk: fabrikasyonlar ~50-90 token → şablonlar 2 cümle ~45-70 token.
TEMPLATES = [
    "Sağlanan {kanun} {madde}, {konu} hususunu düzenlemektedir; sorulan konu bu maddede yer "
    "almamaktadır. Doğru bir atıf için ilgili hükmün ayrıca temini gerekir.",
    "Verilen {kanun} {madde} {konu} ile ilgilidir ve soruyu karşılayan bir hüküm içermemektedir. "
    "Bu maddeye dayanarak cevap vermem yanıltıcı olur; ilgili düzenlemenin sağlanması gerekir.",
    "Elimdeki {kanun} {madde} {konu} konusunu ele almakta olup sorulan hususu kapsamamaktadır. "
    "Güvenilir bir atıf için doğru hükmün temini gerekmektedir.",
    "{kanun} {madde} {konu} bakımından bir düzenleme getirmektedir; ancak bu kaynak sorulan konuya "
    "ilişkin bir hüküm içermemektedir. İlgili maddenin ayrıca sağlanması gerekir.",
    "Sunulan {kanun} {madde}, {konu} hususuna dairdir ve soruyla doğrudan ilgili değildir; aranan "
    "düzenleme bu maddede bulunmamaktadır. Doğru hükmün temini gerekir.",
]

# Konu çıkarmada atılacak baş-işaretler (madde metni başları).
_LEAD = re.compile(r"^\s*(?:[–\-—]\s*)?(?:\(\d+\)\s*)?(?:MADDE\s*\d+[\s\-–—]*)?(?:\d+[\.\)]\s*)?", re.I)
_PAREN_EK = re.compile(r"\((?:Değişik|Ek|Mülga)[^)]*\)", re.I)


def extract_konu(trap_text):
    """Yanlış maddenin KONUSUNU kısa bir ifadeyle çıkar (paraphrase, alıntı DEĞİL → cevap sızmaz).
    İlk cümle/clause'un ilk ~9 kelimesi, baş-işaretler ve (Değişik: ...) ekleri temizlenmiş."""
    t = _PAREN_EK.sub("", trap_text or "").strip()
    t = _LEAD.sub("", t).strip()
    # ilk clause sınırı (virgül dahil → daha temiz, dilbilgisel-yarım kalmasın)
    m = re.search(r"[.,;\n]", t)
    clause = t[:m.start()] if m else t
    words = clause.split()
    if len(words) < 3:                      # clause çok kısa → 9 kelimeye kadar uzat (virgülsüz)
        words = t.split()[:9]
    konu = " ".join(words[:9]).strip().rstrip(",;:").lower()
    if len(konu) < 8:
        return "farklı bir hususu"
    return konu


def build_chosen(row):
    kanun = (row.get("trap_kanun_adi") or "").strip()
    madde = (row.get("trap_madde_no") or "").strip()
    konu = extract_konu(row.get("trap_text", ""))
    tmpl = TEMPLATES[row["id"] % len(TEMPLATES)]
    return tmpl.format(kanun=kanun, madde=madde, konu=konu)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--packed", default=PACKED)
    p.add_argument("--out", default=OUT)
    a = p.parse_args()

    rows = [json.loads(l) for l in open(a.packed, encoding="utf-8") if l.strip()]
    n_gate_fail = 0
    with open(a.out, "w", encoding="utf-8") as f:
        for r in rows:
            chosen = build_chosen(r)
            # Gate teyidi: chosen mutlaka çekinme-ifadesi taşımalı (yoksa ORPO'ya yanlış sinyal).
            if not (ABSTAIN_RE.search(chosen) or REJECT_RE.search(chosen)):
                n_gate_fail += 1
            f.write(json.dumps({"id": r["id"], "chosen": chosen,
                                "trap_kanun_adi": r.get("trap_kanun_adi"),
                                "trap_madde_no": r.get("trap_madde_no")},
                               ensure_ascii=False) + "\n")
    # uzunluk istatistiği (kıyaslanabilirlik denetimi)
    import statistics
    lens = [len(build_chosen(r).split()) for r in rows[:2000]]
    print(f"[v3-chosen] → {a.out}: {len(rows)} chosen | gate_fail={n_gate_fail} "
          f"(0 olmalı) | kelime uzunluğu med={statistics.median(lens):.0f} "
          f"min={min(lens)} max={max(lens)}")
    if n_gate_fail:
        print(f"[v3-chosen] ⚠️ {n_gate_fail} chosen gate'i geçmedi → şablon/konu düzelt")


if __name__ == "__main__":
    main()
