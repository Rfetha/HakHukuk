#!/usr/bin/env python3
"""Kusur 18 · ek denetim — onarım BAŞKA bir koşuyu bozdu mu? ($0, ağ yok, GPU yok)

`outputs/eval/**` altındaki TÜM `*_detail.jsonl` dosyalarında eski ↔ yeni hüküm kıyası.
Üç çıpa kümesi `yeniden_puanla.py`'de ayrıca raporlanır; bu betik yan etkiyi arar.
"""
import glob
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter

_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
_S = os.path.join(_REPO, "scripts")
sys.path[:0] = [_S, *(os.path.join(_S, d) for d in sorted(os.listdir(_S))
                      if os.path.isdir(os.path.join(_S, d)) and d[0] not in "_."), _REPO]
import atif_dogrula as yeni  # noqa: E402


def main():
    src = subprocess.run(["git", "-C", _REPO, "show", "HEAD:scripts/erisim_korpus/atif_dogrula.py"],
                         capture_output=True, text=True, check=True).stdout
    yol = os.path.join(tempfile.mkdtemp(), "atif_dogrula_eski.py")
    open(yol, "w", encoding="utf-8").write(src)
    spec = importlib.util.spec_from_file_location("atif_dogrula_eski", yol)
    eski = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(eski)

    korpus = os.path.join(_REPO, "data/corpus/mevzuat_maddeler.jsonl")
    de, dy = eski.Dogrulayici(korpus), yeni.Dogrulayici(korpus)
    ad_no = {}
    for satir in open(korpus, encoding="utf-8"):
        if satir.strip():
            r = json.loads(satir)
            ad_no.setdefault(str(r["kanun_no"]).strip(), r.get("kanun_adi", ""))

    dosyalar = [y for y in sorted(glob.glob(os.path.join(_REPO, "outputs/eval/**/*_detail.jsonl"),
                                            recursive=True))
                if "g22-atif-onarim" not in y]
    toplam, degisen = 0, []
    for y in dosyalar:
        for satir in open(y, encoding="utf-8"):
            if not satir.strip():
                continue
            r = json.loads(satir)
            cevap = r.get("cevap", "")
            for a, b in zip(de.cevabi_dogrula(cevap), dy.cevabi_dogrula(cevap)):
                toplam += 1
                if (a.hukum, a.kanun_no) != (b.hukum, b.kanun_no):
                    degisen.append({
                        "dosya": os.path.relpath(y, _REPO), "soru_id": r.get("id"),
                        "atif": a.atif.ham[:120], "atif_kanun_adi": a.atif.kanun,
                        "atif_madde": a.atif.madde,
                        "eski_hukum": a.hukum, "eski_kanun_no": a.kanun_no,
                        "eski_kanun_adi": ad_no.get(a.kanun_no, ""),
                        "yeni_hukum": b.hukum, "yeni_kanun_no": b.kanun_no,
                        "yeni_kanun_adi": b.kanun_adi,
                    })
    ozet = {"n_dosya": len(dosyalar), "n_atif": toplam, "n_degisen": len(degisen),
            "gecisler": dict(Counter(f"{d['eski_hukum']}→{d['yeni_hukum']}" for d in degisen)),
            "degisen": degisen}
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "genis_supurme.json"),
              "w", encoding="utf-8") as f:
        json.dump(ozet, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in ozet.items() if k != "degisen"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
