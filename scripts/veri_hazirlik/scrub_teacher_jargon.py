#!/usr/bin/env python
"""Teacher jargonunu eğitim hedeflerinden temizle (research_log #16 · #39).

SORUN. RAFT paketini üreten teacher, `GOLD` / `DISTRACTOR` etiket uzayında promptlanmıştı ve
o etiketleri **cevabına** taşıdı. Öğrenci bu terimleri girdisinde (system+user) **hiç görmüyor**
— ölçüldü: 0/17.323. Yani model, karşılığı olmayan bir jetonu üretmeyi ezberler.

ÖLÇÜLEN (2026-07-24, `data/train/raft/`):
  train      1301/17323 (%7,51)   ·  validation 62/962 (%6,44)  ·  test 72/962 (%7,48)
  GOLD 991 (%5,72) · DISTRACTOR 357 (%2,06) · NEGATIVE 2 · LABEL 1
`data/train/grounded_qa/` TEMİZ (0/19.305) — o set scrub'lanmıştı, `raft/` scrub'lanmamıştı.
`sprint1.md`'nin *"(Mevcut set scrub'lı.)"* notu yalnız `grounded_qa` için doğruydu.

YAKLAŞIM. Silme değil **çeviri**: teacher'ın etiketi, öğrencinin gördüğü kelime dağarcığına
eşlenir (`GOLD`→"ilgili kaynak", `DISTRACTOR`→"ilgisiz"). Satır DÜŞÜRÜLMEZ — düşürmek rastgele
olmaz, sistematik kapsama deliği açar (#14 topik-skew dersi).

GÜVENLİK. `##begin_quote## … ##end_quote##` blokları **dokunulmaz**: onlar kanun metninin birebir
alıntısı ve harness'ın atıf doğrulayıcısı (TASARIM §5) onları korpusa karşı sınayacak. Bir terim
alıntı içinde geçiyorsa script DURUR ve rapor eder.

Kullanım:
  python scripts/veri_hazirlik/scrub_teacher_jargon.py --in-dir data/train/raft --out-dir data/train/raft_scrubbed
  python scripts/veri_hazirlik/scrub_teacher_jargon.py --in-dir data/train/raft --check-only
"""
import argparse
import json
import os
import re

# Sıra ÖNEMLİ — özelden genele. Türkçe ekler yüzünden düz kelime değişimi yetmiyor.
#
# ⚠️ İki ayrı dilbilgisel konum, iki ayrı işlem:
#   (a) SIFAT konumu — "…içeren GOLD metnidir", "GOLD madde olan TCK 194'tür".
#       Burada etiket SİLİNİR. Çevirmek tekrar üretir: cümle zaten "İlgili kaynak," diye
#       başlıyor, "ilgili kaynak" koyunca "İlgili kaynak, … ilgili kaynak metnidir" oluyor.
#   (b) BAĞIMSIZ ad konumu — "yalnızca GOLD dikkate alınmıştır". Burada çevrilir.
RULES = [
    (re.compile(r"DISTRACTOR['’]?lar[ıi]", re.I), "ilgisiz kaynakları"),
    (re.compile(r"DISTRACTOR['’]?lar", re.I), "ilgisiz kaynaklar"),
    (re.compile(r"\bDISTRACTOR\b", re.I), "ilgisiz"),
    (re.compile(r"\(\s*GOLD\s*\)", re.I), ""),                     # "kaynak 1 (GOLD)" → "kaynak 1"
    # (a1) "GOLD metni/metnidir/metninde" — iyelik eki bir SAHİP ister; etiketi silmek
    #      "…açıklayan metnidir" gibi sahipsiz bir ek bırakır. Geçerli bir ad konur.
    (re.compile(r"\bGOLD\s+(?=metn)", re.I), "doğru kaynak "),
    # (a2) "GOLD madde/kaynak/belge/hüküm/kanun" — burada ek yok, etiket SİLİNİR
    (re.compile(r"\bGOLD\s+(?=(madde|kaynak|belge|hüküm|kanun))", re.I), ""),
    # (b) bağımsız ad konumu → çevir
    (re.compile(r"\bGOLD\b", re.I), "doğru kaynak"),
    (re.compile(r"\bhard[- ]negative\b", re.I), "ilgisiz"),
    (re.compile(r"\bground[- ]?truth\b", re.I), "doğru kaynak"),
]
# Sızıntı tespiti (öğrencinin girdisinde geçmeyen teacher terimleri)
LEAK = re.compile(r"(?<![A-Za-zÇĞİÖŞÜçğıöşü])(GOLD|DISTRACTOR|HARD[- ]NEGATIVE|GROUND[- ]?TRUTH)"
                  r"(?![A-Za-zÇĞİÖŞÜçğıöşü])", re.I)
QUOTE = re.compile(r"##begin_quote##(.*?)##end_quote##", re.S)


def msgs(rec):
    a = i = None
    for k, m in enumerate(rec["messages"]):
        if m["role"] in ("assistant", "model"):
            a, i = m["content"], k
    seen = " ".join(m["content"] for m in rec["messages"] if m["role"] in ("system", "user"))
    return a, i, seen


def scrub(text):
    """Alıntı bloklarını KORUYARAK kalanı temizle."""
    parts, last = [], 0
    for m in QUOTE.finditer(text):
        parts.append(("free", text[last:m.start()]))
        parts.append(("quote", m.group(0)))
        last = m.end()
    parts.append(("free", text[last:]))
    out = []
    for kind, seg in parts:
        if kind == "quote":
            out.append(seg)
        else:
            for pat, rep in RULES:
                seg = pat.sub(rep, seg)
            seg = re.sub(r"[ \t]{2,}", " ", seg)
            seg = re.sub(r"\s+([,.;:])", r"\1", seg)
            out.append(seg)
    return "".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-dir", required=True)
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--splits", nargs="+", default=["train", "validation", "test"])
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args()
    if not a.check_only and not a.out_dir:
        raise SystemExit("[scrub] --out-dir gerekli (orijinal ASLA üzerine yazılmaz)")
    if a.out_dir:
        os.makedirs(a.out_dir, exist_ok=True)

    grand = {"rows": 0, "leaky": 0, "fixed": 0, "residual": 0, "in_quote": 0, "seen_by_student": 0}
    for split in a.splits:
        src = os.path.join(a.in_dir, f"{split}.jsonl")
        if not os.path.exists(src):
            print(f"[scrub] {split}: dosya yok, atlanıyor")
            continue
        rows = [json.loads(l) for l in open(src, encoding="utf-8") if l.strip()]
        leaky = fixed = residual = in_quote = seen = 0
        out_rows = []
        for rec in rows:
            ans, idx, student_sees = msgs(rec)
            if ans is None:
                out_rows.append(rec); continue
            if LEAK.search(ans):
                leaky += 1
                # terim öğrencinin girdisinde de geçiyorsa "sızıntı" değildir — dokunma
                if LEAK.search(student_sees):
                    seen += 1
                    out_rows.append(rec); continue
                for q in QUOTE.findall(ans):
                    if LEAK.search(q):
                        in_quote += 1
                        break
                new = scrub(ans)
                if new != ans:
                    fixed += 1
                    rec = json.loads(json.dumps(rec))          # kopya — girdiyi mutasyona uğratma
                    rec["messages"][idx]["content"] = new
                if LEAK.search(rec["messages"][idx]["content"]):
                    residual += 1
            out_rows.append(rec)

        print(f"[scrub] {split:<11} n={len(rows):>6} · sızıntılı {leaky:>5} (%{100*leaky/max(1,len(rows)):.2f})"
              f" · onarılan {fixed:>5} · KALAN {residual} · alıntı-içi {in_quote} · öğrenci-görüyor {seen}")
        if in_quote:
            print(f"[scrub] ⚠️ {split}: {in_quote} satırda terim ALINTI İÇİNDE — alıntılar korundu, "
                  f"elle bakılmalı (alıntı birebir kanun metni olmalıydı)")
        if a.out_dir:
            dst = os.path.join(a.out_dir, f"{split}.jsonl")
            with open(dst, "w", encoding="utf-8") as f:
                for r in out_rows:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            print(f"[scrub]   → {dst}")
        for k, v in (("rows", len(rows)), ("leaky", leaky), ("fixed", fixed),
                     ("residual", residual), ("in_quote", in_quote), ("seen_by_student", seen)):
            grand[k] += v

    print(f"\n[scrub] TOPLAM n={grand['rows']} · sızıntılı {grand['leaky']} "
          f"(%{100*grand['leaky']/max(1,grand['rows']):.2f}) · onarılan {grand['fixed']} "
          f"· KALAN {grand['residual']}")
    if grand["residual"]:
        raise SystemExit(f"[scrub] 🚫 {grand['residual']} satırda sızıntı KALDI — kural seti eksik.")
    print("[scrub] ✅ kalıntı yok.")


if __name__ == "__main__":
    main()
