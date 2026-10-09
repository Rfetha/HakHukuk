"""Ürün yolunun (`servis.answer`) 80 DEV sorusundaki davranışını kaydeder.

Kullanımı: bir değişiklikten ÖNCE ve SONRA koşulur, iki JSON birebir karşılaştırılır.
Kapı ölçütü budur — tek bir koşunun çıktısı tek başına bir hüküm kurmaz.

⚠️ Bu betiğin ilk sürümü suskunluk kümesini planın ön-kayıtlı `[15, 37, 45, 66, 79]`
kümesiyle karşılaştırıyordu ve KIRMIZI yandı. Karşılaştırma yanlıştı: o küme ÖLÇÜM
HATTININ (`gen_eval_grounded.py` + `exact_reject`) kümesidir. İki hat aynı şeyi
çalıştırmaz — ölçüm hattı düşünceyi iki geçişte zorla kapatır, ürün yolu kapatmaz — ve
sınıflandırma kuralları da farklıdır. Değişiklik öncesi/sonrası koşusu (2026-09-09) bunu
kesinleştirdi: 80/80 kalem birebir aynı çıktı, yani fark koddan değil hatlar arasındaki
kalıcı farktan geliyor. Ölçüldüğü yer: `outputs/eval/gorev/g18-arac-katmani/`.
"""
import json, os, sys
sys.path.insert(0, "/home/ersoy/code/Hukuk-SLM")
from hakhukuk.cekirdek.servis import answer          # noqa: E402
from hakhukuk.cekirdek.tipler import Durum           # noqa: E402

dev = [json.loads(l) for l in open("data/eval/dev/core_hard.jsonl", encoding="utf-8") if l.strip()]
kayit = []
for i, d in enumerate(dev):
    c = answer(d["messages"][0]["content"])
    kayit.append({"id": i, "durum": c.durum.name,
                  "atif": [[a.kanun_no, a.madde_no, a.dogrulandi] for a in c.atiflar],
                  "kaynak": [s.kimlik for s in c.kaynaklar], "metin": c.metin})
    print(f"  [{i+1}/{len(dev)}] {c.durum.name}", flush=True)

json.dump(kayit, open("outputs/eval/gorev/g18-arac-katmani/aracsiz_yol_80.json", "w",
                      encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"\nSUSKUNLUK : {sorted(r['id'] for r in kayit if r['durum'] == 'SUSKUNLUK')}")
print(f"KESIK     : {sorted(r['id'] for r in kayit if r['durum'] == 'KESIK')}")
print(f"BOŞ METİN : {sorted(r['id'] for r in kayit if not r['metin'].strip())}")
print(f"dağılım   : { {d.name: sum(1 for r in kayit if r['durum'] == d.name) for d in Durum} }")
print("\nKapı hükmü bu çıktıdan KURULMAZ — öncesi/sonrası iki JSON karşılaştırılır.")
