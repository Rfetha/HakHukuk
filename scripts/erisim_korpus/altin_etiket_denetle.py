#!/usr/bin/env python3
"""Altın etiketi belirsiz eval kalemlerini KÖR hakemle denetler (sprint3 S2 ardılı).

Neden var: korpusta alt-madde soneki `madde_no`'ya değil metne düşmüştü, bu yüzden
`Madde 97` ile `Madde 97/a` **aynı anahtarı** paylaşıyordu. Eval kümesinin altın
etiketleri o bozuk korpustan türetildi → soru `97/a`'dan üretilip etiket `Madde 97`
kalabiliyor. Onarım sonrası (research_log #55) bu kalemler **yanlış ıskalanmış** sayılıyor.

⚠️ Bu denetim SAYI GÖRÜLDÜKTEN SONRA yapılıyor ve düzeltmesi bizim lehimize. Bu yüzden:
  · şüpheli kalemler ELLE SEÇİLMEZ — kuralla bulunur (altın anahtarın sonekli kardeşi var mı)
  · hakem KÖRDÜR — madde numaralarını görmez, yalnız iki metni görür
  · istem koşudan ÖNCE research_log'a yazılır
  · hakem "belirsiz" diyebilir; belirsizde etiket DEĞİŞMEZ (mevcut hâl korunur)

Kullanım:
    python scripts/erisim_korpus/altin_etiket_denetle.py --details <detail.jsonl> --out <dizin>
    python scripts/erisim_korpus/altin_etiket_denetle.py --details ... --out ... --uygula <eval.jsonl>
"""
from __future__ import annotations

import argparse
import collections
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
from llm_client import (make_client, resolve, price, request_kwargs,  # noqa: E402
                        note_provider, seen_providers, loads_tolerant)

KORPUS = "data/corpus/mevzuat_maddeler.jsonl"
SONEK_KEY = re.compile(r"^(.*?)/([A-Za-zÇĞİIÖŞÜçğıöşü])$")

ISTEM_SYS = """Sen Türk hukukunda deneyimli bir hukukçusun. Sana bir SORU ve iki KANUN METNİ
verilecek. Görevin soruyu cevaplamak değil; soruyu HANGİ metnin karşıladığını söylemek.

ÖLÇÜT: Soruda sorulan bilgi hangi metinde AÇIKÇA düzenlenmiştir?

Kurallar:
- Yalnız verilen iki metne bak. Dışarıdan bilgi ekleme.
- İkisi de karşılıyorsa, soruyu DOĞRUDAN ve TAM karşılayanı seç.
- Hiçbiri karşılamıyorsa ya da ayırt edemiyorsan "belirsiz" de. Emin değilsen "belirsiz".

Yanıtı SADECE şu JSON ile ver:
{"secim": "A" | "B" | "belirsiz", "gerekce": "<tek cümle>"}"""


def _istem(soru: str, metin_a: str, metin_b: str) -> list[dict]:
    """Hakem yükü. Madde numarası, kanun adı ve mevcut altın etiket BU YÜKTE YOKTUR."""
    return [
        {"role": "system", "content": ISTEM_SYS},
        {"role": "user", "content": f"SORU:\n{soru}\n\n[KAYNAK A]\n{metin_a}\n\n[KAYNAK B]\n{metin_b}"},
    ]


def _soru_anahtari(soru: str) -> str:
    """Koşudan bağımsız eşleme anahtarı — `id` örneklem sırasına bağlı, soru metni değil."""
    return " ".join(soru.split()).lower()


def _eval_sorusu(kayit: dict) -> str:
    """Eval kaleminin soru metni: ilk `user` turu."""
    return next((m["content"] for m in kayit["messages"] if m["role"] == "user"), "")


def supheli_kalemler(kayitlar: list[dict], korpus: list[dict]) -> list[dict]:
    """Altın anahtarın sonekli bir kardeşi varsa kalem şüphelidir. Kural, seçim değil."""
    idx = collections.defaultdict(list)
    for r in korpus:
        idx[(r["kanun_no"], r["madde_no"])].append(r)
    kardesler = collections.defaultdict(list)
    for (kno, mno), satirlar in idx.items():
        if m := SONEK_KEY.match(mno):
            kardesler[(kno, m.group(1))].append((mno, satirlar[0]))
    cikti = []
    for r in kayitlar:
        anahtar = (r["kanun_no"], r["madde_no"])
        if anahtar in kardesler and idx.get(anahtar):
            for sonekli_no, sonekli in sorted(kardesler[anahtar]):
                cikti.append({"id": r["id"], "soru": r["soru"], "kanun_adi": r["kanun_adi"],
                              "kanun_no": r["kanun_no"], "altin_madde_no": r["madde_no"],
                              "aday_madde_no": sonekli_no,
                              "metin_altin": idx[anahtar][0]["text"],
                              "metin_aday": sonekli["text"]})
    return cikti


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--details", required=True)
    ap.add_argument("--korpus", default=KORPUS)
    ap.add_argument("--out", required=True)
    ap.add_argument("--uygula", help="eval jsonl — verilirse etiketler DÜZELTİLİR")
    ap.add_argument("--judge-model", default=os.environ.get("GND_JUDGE", "gpt-4o-mini"))
    # ⭐ KONUM YANLILIĞI KONTROLÜ. Hakem içeriğe değil KONUMA bakıyorsa (hep "A" diyorsa)
    # hükümler değersizdir. Bu bayrak A/B'yi ters çevirir; iki koşunun hükmü AYNI kalmalı.
    # Kalmıyorsa yanlılık ölçülmüştür ve etiketlere DOKUNULMAZ.
    ap.add_argument("--konum-ters", action="store_true", help="A/B yerlerini ters çevir (kontrol koşusu)")
    a = ap.parse_args()

    kayitlar = [json.loads(l) for l in open(a.details, encoding="utf-8") if l.strip()]
    korpus = [json.loads(l) for l in open(a.korpus, encoding="utf-8") if l.strip()]
    supheli = supheli_kalemler(kayitlar, korpus)
    print(f"[denetim] kuralla bulunan şüpheli kalem: {len(supheli)}/{len(kayitlar)}")

    os.makedirs(a.out, exist_ok=True)
    client, gateway = make_client()
    model = resolve(a.judge_model, gateway)
    gin, gout = price(a.judge_model)
    sonuc, maliyet = [], 0.0
    for s in supheli:
        # Konum yanlılığına karşı: tek id'de altın A'da, çift id'de B'de. --konum-ters tersler.
        altin_a = (s["id"] % 2 == 1) != a.konum_ters
        m_a, m_b = (s["metin_altin"], s["metin_aday"]) if altin_a else (s["metin_aday"], s["metin_altin"])
        resp = client.chat.completions.create(
            model=model, temperature=0, **request_kwargs(model),
            messages=_istem(s["soru"], m_a[:2500], m_b[:2500]))
        note_provider(resp)
        y = loads_tolerant(resp.choices[0].message.content)
        u = resp.usage
        maliyet += (u.prompt_tokens or 0) * gin + (u.completion_tokens or 0) * gout
        secim = (y or {}).get("secim", "belirsiz")
        if secim == "belirsiz":
            karar = "DEĞİŞMEZ"
        else:
            secilen_altin = (secim == "A") == altin_a
            karar = "DEĞİŞMEZ" if secilen_altin else "DÜZELT"
        sonuc.append({**{k: s[k] for k in ("id", "soru", "kanun_adi", "kanun_no",
                                           "altin_madde_no", "aday_madde_no")},
                      "altin_konumu": "A" if altin_a else "B", "hakem_secim": secim,
                      "gerekce": (y or {}).get("gerekce", ""), "karar": karar})
        print(f"  id={s['id']:<3} {s['altin_madde_no']} ↔ {s['aday_madde_no']}  "
              f"hakem={secim} (altın {'A' if altin_a else 'B'}) → {karar}")

    with open(os.path.join(a.out, "etiket_denetimi.jsonl"), "w", encoding="utf-8") as f:
        for r in sonuc:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    duzelt = [r for r in sonuc if r["karar"] == "DÜZELT"]
    with open(os.path.join(a.out, "ozet.json"), "w", encoding="utf-8") as f:
        json.dump({"n_supheli": len(sonuc), "n_duzelt": len(duzelt),
                   "judge_model": a.judge_model, "judge_gateway": gateway,
                   "judge_providers": seen_providers(), "judge_cost_usd": round(maliyet, 4)},
                  f, ensure_ascii=False, indent=2)
    print(f"[denetim] DÜZELT {len(duzelt)} · DEĞİŞMEZ {len(sonuc)-len(duzelt)} · hakem ${maliyet:.4f}")

    if not a.uygula:
        print("🔸 --uygula verilmedi: eval kümesi DEĞİŞMEDİ")
        return
    ev = [json.loads(l) for l in open(a.uygula, encoding="utf-8") if l.strip()]
    # ⚠️ Eşleme SORU metnine göre yapılır, madde anahtarına göre DEĞİL: aynı anahtarı
    # paylaşan iki kalem farklı maddelerden üretilmiş olabiliyor (id 0 → 31/a, id 41 → 31).
    # Anahtara göre eşlemek ikisini birden bozardı.
    hedef = {_soru_anahtari(r["soru"]): r["aday_madde_no"] for r in duzelt}
    n = 0
    for r in ev:
        yeni = hedef.get(_soru_anahtari(_eval_sorusu(r)))
        if yeni:
            r["madde_no"], n = yeni, n + 1
    if n != len(duzelt):
        sys.exit(f"❌ {len(duzelt)} düzeltme bekleniyordu, {n} kalem eşleşti — eval kümesi DEĞİŞMEDİ")
    gecici = a.uygula + ".tmp"
    with open(gecici, "w", encoding="utf-8") as f:
        for r in ev:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(gecici, a.uygula)
    print(f"✍️  {a.uygula}: {n} kalemin altın etiketi düzeltildi")


if __name__ == "__main__":
    main()
