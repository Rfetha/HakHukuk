#!/usr/bin/env python3
"""Kusur 18 · PARÇA 2 — ÇIPALARI YENİDEN PUANLA ($0, deterministik, ağ yok, GPU yok).

⛔ Donmuş TEST'e YENİ SORU SORULMAZ: yalnız **diskte duran** cevaplara, onarılmış alet
yeniden uygulanır. Bu ADR-0050'nin kalıbıdır (alet düzelir, eşik oynamaz).

Eski alet HEAD'den (`git show`) geçici bir dosyaya alınır — çalışma ağacına dokunulmaz
(tuzak 5.9: denetim için `git stash` KULLANILMAZ).
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
_SCRIPTS = os.path.join(_REPO, "scripts")
sys.path[:0] = [_SCRIPTS, *(os.path.join(_SCRIPTS, d) for d in sorted(os.listdir(_SCRIPTS))
                            if os.path.isdir(os.path.join(_SCRIPTS, d)) and d[0] not in "_."),
                _REPO]

import atif_dogrula as yeni  # noqa: E402

KORPUS = os.path.join(_REPO, "data/corpus/mevzuat_maddeler.jsonl")
KUMELER = [
    ("DEV cipa (f02-biz-onsozsuz)", "outputs/eval/f02-biz-onsozsuz/h1_tgta_v1_f02_nb_detail.jsonl"),
    ("donmus TEST (g16-kabul-testi)", "outputs/eval/g16-kabul-testi/h1_tgta_v1_g16_test_nb_detail.jsonl"),
    ("fp16 kosusu (g22-kv-fp16)", "outputs/eval/g22-kv-fp16/h1_tgta_v1_g22_fp16_detail.jsonl"),
]
HUKUMLER = ["DOGRULANDI", "MULGA", "MADDE_YOK", "KANUN_YOK", "AYRISTIRILAMADI"]


def eski_modul():
    """HEAD'deki (onarım ÖNCESİ) atif_dogrula.py'yi ayrı bir modül olarak yükle."""
    kaynak = subprocess.run(["git", "-C", _REPO, "show", "HEAD:scripts/erisim_korpus/atif_dogrula.py"],
                            capture_output=True, text=True, check=True).stdout
    yol = os.path.join(tempfile.mkdtemp(), "atif_dogrula_eski.py")
    with open(yol, "w", encoding="utf-8") as f:
        f.write(kaynak)
    spec = importlib.util.spec_from_file_location("atif_dogrula_eski", yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha256(yol):
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


def main():
    eski = eski_modul()
    d_eski, d_yeni = eski.Dogrulayici(KORPUS), yeni.Dogrulayici(KORPUS)
    ad_no = {}
    with open(KORPUS, encoding="utf-8") as f:
        for satir in f:
            if satir.strip():
                r = json.loads(satir)
                ad_no.setdefault(str(r["kanun_no"]).strip(), r.get("kanun_adi", ""))

    rapor = {"kumeler": [], "degisen": []}
    for etiket, gor_yol in KUMELER:
        yol = os.path.join(_REPO, gor_yol)
        kayitlar = [json.loads(l) for l in open(yol, encoding="utf-8") if l.strip()]
        once = {h: 0 for h in HUKUMLER}
        sonra = {h: 0 for h in HUKUMLER}
        degisen = 0
        for r in kayitlar:
            cevap = r.get("cevap", "")
            he, hy = d_eski.cevabi_dogrula(cevap), d_yeni.cevabi_dogrula(cevap)
            assert len(he) == len(hy), "atıf AYIKLAMA değişmemeliydi"
            for a, b in zip(he, hy):
                once[a.hukum] += 1
                sonra[b.hukum] += 1
                if (a.hukum, a.kanun_no) != (b.hukum, b.kanun_no):
                    degisen += 1
                    rapor["degisen"].append({
                        "kume": etiket, "soru_id": r.get("id"),
                        "atif": a.atif.ham, "atif_kanun_adi": a.atif.kanun,
                        "atif_madde": a.atif.madde, "atif_tip": a.atif.tip,
                        "eski_hukum": a.hukum, "eski_kanun_no": a.kanun_no,
                        "eski_kanun_adi": ad_no.get(a.kanun_no, ""),
                        "yeni_hukum": b.hukum, "yeni_kanun_no": b.kanun_no,
                        "yeni_kanun_adi": b.kanun_adi,
                        "altin_kanun_no": str(r.get("kanun_no", "")),
                        "altin_kanun_adi": r.get("kanun_adi", ""),
                        "altin_madde_no": r.get("madde_no", ""),
                    })
        rapor["kumeler"].append({
            "kume": etiket, "dosya": gor_yol, "sha256": sha256(yol),
            "n_cevap": len(kayitlar), "n_atif": sum(once.values()),
            "once": once, "sonra": sonra, "hukmu_degisen_atif": degisen,
        })
    cikti = os.path.join(_REPO, "outputs/eval/g22-atif-onarim")
    with open(os.path.join(cikti, "yeniden_puanlama.json"), "w", encoding="utf-8") as f:
        json.dump(rapor, f, ensure_ascii=False, indent=2)
    print(json.dumps(rapor["kumeler"], ensure_ascii=False, indent=2))
    print(f"\nhükmü değişen atıf toplamı: {len(rapor['degisen'])}")


if __name__ == "__main__":
    main()
