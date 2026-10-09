#!/usr/bin/env python
"""Ayırt-edicilik etiketi — ADR-0054/K4'ün şart koştuğu KÖR etiketleme turu (borç B2).

NE YAPAR
    Her DEV sorusuna *"kendi başına ayırt edici mi"* etiketi atar. Harness sayıları
    (recall@k · coverage · kütle) bu etiketin iki alt kümesinde AYRI raporlanabilsin diye.

⚠️ NEDEN VAR (tuzak 7.4, research_log #49)
    `core_hard.jsonl` **grounded QA kümesi, retrieval kümesi değil** — sorular altın madde
    elde tutularak yazıldı, bu yüzden ~%25'i tek başına hangi kanuna ait olduğunu
    söylemiyor (*"Başvurum kabul edilirse ne olur?"*). Böyle bir soruda tek-altın
    `recall@k` düşük çıkar ve bu **retriever zayıflığı gibi okunur**. Etiket, kümeyi
    değiştirmeden aleti keskinleştirir: tek sayı yerine iki eksen.

🚨 KÖRLÜK — dürüstlük şartı (ADR-0054/K4)
    Hakem YALNIZ soru metnini görür. Altın maddeyi, hangi kanundan üretildiğini ve
    retriever'ın onu bulup bulmadığını GÖRMEZ. Bu betik altın alanları hakeme giden
    yükte hiç taşımaz — `_istem()` tek argüman alır ve o argüman sorudur.
    Aynı sınıfın tersi tuzak 2.14'te ısırdı: etiket, öznenin cevabıyla aynı çağrıda
    istendiği için hakem cevaba çapalandı ve etiket kalemin değil öznenin özelliği oldu.

Kullanım:
  python scripts/erisim_korpus/ayirt_edicilik_etiketle.py \
      --details outputs/eval/sprint2-olcum/s3-harness-acik/h1_tgta_v1_h1_detail.jsonl \
      --out-dir outputs/eval/sprint2-olcum/s3-ayirt-edicilik
"""
import argparse
import hashlib
import json
import os
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

# ⛔ ÖN-KAYITLI İSTEM — ölçüt ADR-0054/K4'ten BİREBİR alındı ve etiketleme koşulmadan
# önce research_log #53'e yazıldı. Sonuç görüldükten sonra DEĞİŞTİRİLMEZ.
OLCUT = ("Soru tek başına okunduğunda, hangi kanun/konu alanına ait olduğu anlaşılıyor mu? "
         "(Bir hukukçu soruyu görüp 1-2 kanuna daraltabiliyorsa EVET.)")

SISTEM = (
    "Sen Türk hukukunda deneyimli bir hukukçusun. Sana YALNIZCA bir soru metni verilecek. "
    "Sorunun cevabını vermen istenmiyor; sorunun kendisi hakkında tek bir yargıda bulunacaksın.\n\n"
    f"ÖLÇÜT: {OLCUT}\n\n"
    "Kurallar:\n"
    "- Soruda kanun adı, kurum adı ya da alana özgü terim geçiyorsa (ör. 'kıdem tazminatı', "
    "'tutuklama', 'kira sözleşmesi') daraltma mümkündür → EVET.\n"
    "- Soru genel bir usul cümlesiyse ve konusu belirtilmemişse (ör. 'Başvurum kabul edilirse "
    "ne olur?', 'Süresi ne kadardır?') daraltma mümkün değildir → HAYIR.\n"
    "- Kararını yalnız soru metnine dayandır. Tahmin ettiğin bir bağlam varsayma.\n\n"
    'Yanıtı SADECE şu JSON ile ver: {"ayirt_edici": true|false, "alan": "<daraltabildiğin '
    'kanun/alan, en fazla 2 tane; daraltamıyorsan boş string>", "gerekce": "<tek cümle>"}'
)


def _istem(soru):
    """Hakeme giden TEK yük. Altın madde/kanun buraya asla girmez (körlük şartı)."""
    return [{"role": "system", "content": SISTEM},
            {"role": "user", "content": f"SORU:\n{soru}"}]


def soru_anahtari(soru):
    """Koşudan bağımsız birleştirme anahtarı — id'ler örneklem sırasına bağlı, metin değil."""
    return hashlib.sha1(" ".join(soru.split()).lower().encode("utf-8")).hexdigest()[:16]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--details", required=True, help="harness koşusunun *_detail.jsonl'i (soru alanı okunur)")
    p.add_argument("--out-dir", default="outputs/eval/sprint2-olcum/s3-ayirt-edicilik")
    p.add_argument("--judge-model", default=os.environ.get("GND_JUDGE", "gpt-4o-mini"))
    a = p.parse_args()

    kayitlar = [json.loads(l) for l in open(a.details, encoding="utf-8") if l.strip()]
    os.makedirs(a.out_dir, exist_ok=True)
    out_path = os.path.join(a.out_dir, "etiketler.jsonl")

    client, gateway = make_client()
    model = resolve(a.judge_model, gateway)
    gin, gout = price(a.judge_model)
    spent = 0.0

    with open(out_path, "w", encoding="utf-8") as f:
        for r in kayitlar:
            soru = r["soru"]
            resp = client.chat.completions.create(
                model=model, temperature=0, **request_kwargs(model), messages=_istem(soru))
            note_provider(resp)
            d = loads_tolerant(resp.choices[0].message.content)
            u = resp.usage
            spent += (u.prompt_tokens or 0) * gin + (u.completion_tokens or 0) * gout
            satir = {
                "id": r["id"], "soru_anahtari": soru_anahtari(soru), "soru": soru,
                "ayirt_edici": bool(d.get("ayirt_edici")),
                "alan": d.get("alan", ""), "gerekce": d.get("gerekce", ""),
            }
            f.write(json.dumps(satir, ensure_ascii=False) + "\n")
            print(f"  [{r['id']+1}/{len(kayitlar)}] {'AYIRT EDİCİ' if satir['ayirt_edici'] else 'belirsiz   '}"
                  f" | {satir['alan'][:40]:<40} | {soru[:52]}")

    n_ae = sum(1 for l in open(out_path, encoding="utf-8") if json.loads(l)["ayirt_edici"])
    ozet = {
        "n": len(kayitlar), "ayirt_edici": n_ae, "belirsiz": len(kayitlar) - n_ae,
        "judge_model": a.judge_model, "judge_gateway": gateway,
        "judge_providers": seen_providers(), "judge_cost_usd": round(spent, 4),
        "kor": "hakem yalnız soru metnini gördü — altın madde/kanun ve erişim sonucu gönderilmedi",
        "olcut": OLCUT,
    }
    json.dump(ozet, open(os.path.join(a.out_dir, "ozet.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"\n{json.dumps(ozet, ensure_ascii=False, indent=2)}")


if __name__ == "__main__":
    main()
