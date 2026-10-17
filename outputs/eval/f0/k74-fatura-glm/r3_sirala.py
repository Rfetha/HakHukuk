"""#74 R3 testi: aynı sorunun iki kolunu (A10 llama.cpp ↔ vLLM q4 t1; aynı 80 DEV sorusu, aynı
kaynak) art arda dizer → tek dosya. İkinci kolun doğrulama çağrısı, birincininkiyle ortak olan
"sistem istemi + soru + kaynak + altın atıf" önekini önbellekten alıyor mu, onu ölçmek için.
Kullanım (repo kökünden): python outputs/eval/f0/k74-fatura-glm/r3_sirala.py"""
import json

A = "outputs/eval/f0/f016-pilot/A10/m1/h1_tgta_v1_A10_m1_t1_detail.jsonl"
V = "outputs/eval/f0/f016-vllm-pilot/A10/q4-acilmis/h1_tgta_v1_vllm_q4-acilmis_t1_detail.jsonl"
O = "outputs/eval/f0/k74-fatura-glm/r3_sirali_detail.jsonl"

a = [json.loads(s) for s in open(A, encoding="utf-8") if s.strip()]
v = [json.loads(s) for s in open(V, encoding="utf-8") if s.strip()]
assert len(a) == len(v) == 80
ayni = 0
with open(O, "w", encoding="utf-8") as f:
    for ra, rv in zip(a, v):
        for k in ("id", "soru", "referans", "kanun_adi", "madde_no", "kanun_no"):
            assert ra.get(k) == rv.get(k), (ra["id"], k)
        ayni += ra["cevap"].strip() == rv["cevap"].strip()
        f.write(json.dumps({**ra, "id": f"a-{ra['id']}"}, ensure_ascii=False) + "\n")
        f.write(json.dumps({**rv, "id": f"v-{rv['id']}"}, ensure_ascii=False) + "\n")
print(f"{O}: 160 kalem; iki kolun cevabı birebir aynı olan soru: {ayni}/80")
