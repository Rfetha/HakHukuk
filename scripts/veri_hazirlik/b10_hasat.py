#!/usr/bin/env python3
"""B10 hasadı — altın madde BAĞLAMDAYKEN üretilen gerçek aşırı-redler (`τ_a` v2'nin `rejected`'ı).

`τ_a` v1'in eğitim setinde "altın varken CEVAPLA" yönünde tek bir tercih baskısı yok
(703 çiftin tamamı çekinme yönünde; 142 grounding replay `is_pref=0` → OR maskeli). Bu betik
eksik sınıfın negatif tarafını toplar: model altın maddeyi görüp yine de çekindiyse, o çekinme
`rejected` olur; `chosen` aynı kalemin `raft_scrubbed` grounded hedefidir.

⚠️ ÜRETİM YOLU `gen_eval_grounded.generate_http` — yeniden yazılmaz (ikinci bir üretim gövdesi
tam olarak sessiz protokol sapması üretir).

⚠️ KABUL ÖLÇÜTÜ `exact_reject(cevap, "data")` — `harness_tablo.py:111`'in B10'u saydığı BİREBİR
aynı çağrı. Tuzak 4.7: hasadın kabul ölçütü, o veriyle eğitilen kolun RAPORLANACAĞI metrikle
aynı olmalı.

⚠️ İSTEM ÖNSÖZSÜZ — BİLİNÇLİ SAPMA, iki tarafı da burada duruyor (ADR-0059 §sapma-1).
  · LEHTE (tercih edilen): mevcut 703 çekinme çifti önsözsüz hasat edildi. İki istemi karıştırmak
    modele "önsöz varsa cevapla, yoksa çekin" kısayolunu öğretir — tam ters kalibrasyon, ve
    hiçbir yerde hata vermez.
  · ALEYHTE (kayda geçiyor, gizlenmiyor): B10'un RAPORLANAN değeri (14/80) ÖNSÖZLÜ ölçüldü
    (ADR-0058 ana protokolü). Yani eğitim bir dağılımdan, ölçüm başka bir dağılımdan okunuyor.
    `generate_http` `sufficiency=` parametresini zaten taşıyor → teknik engel yok, bu saf bir
    tasarım tercihi. Görev 7'nin kol kapısı bu asimetriyi BİLEREK okumalı.
  Künyeye `sufficiency_preamble: false` olarak yazılır — künyeye yazılmayan parametre koşulmuş
  sayılmaz (tuzak 6.12).

⚠️ CANON sızıntı süzgeci için AÇILIYOR — kasıtlı ve künyeye yazılır. `DEV_YOLLARI`
`data/eval/canon/core_hard.jsonl`'i de okur, ama yalnız SORU metnini ve altın madde numarasını;
amacı o kalemleri eğitimden DIŞLAMAK. Kural çiğnenmiyor, korunuyor. CANON'un cevabına/sonucuna
bakılmaz (test: `test_sizinti_suz_dev_altin_CEVABINI_okumaz`).

Kullanım:
  # PİLOT
  python scripts/veri_hazirlik/b10_hasat.py --limit 150 --out data/_ham_ve_ara/b10_pilot.jsonl
  # ÜRETİM
  python scripts/veri_hazirlik/b10_hasat.py --target 250 --out data/_ham_ve_ara/b10_kabul.jsonl
"""
import argparse
import json
import os
import random
import re
import sys
import threading
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

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

from gen_eval_grounded import generate_http          # noqa: E402  — TEK üretim gövdesi
from madde_anahtar import madde_anahtari             # noqa: E402  — TEK madde normalleştirici
from score_abstention import exact_reject            # noqa: E402  — TEK regex kaynağı

HAVUZ = "data/train/raft_scrubbed/train.jsonl"
DEV_YOLLARI = ["data/eval/dev/core_hard.jsonl", "data/eval/canon/core_hard.jsonl"]
MODE = "data"                                        # harness_tablo.py:111 ile birebir
CANON_NOTU = ("CANON yalnız dışlama listesi olarak okundu (soru metni + altın madde no); "
              "hiçbir CANON cevabı/sonucu görülmedi.")

_BAGLAM_BASLIGI = re.compile(r"^(KAYNAKLAR|KAYNAK MADDE):", re.M)


def _soru(rec):
    """Soru metni. İKİ şekil var ve karıştırmak süzgeci sessizce NO-OP yapar.

    · `raft_scrubbed`: user = `KAYNAKLAR:\\n…\\n\\nSORU: <soru>` → `SORU:` sonrası.
    · `data/eval/{dev,canon}/core_hard.jsonl`: messages = **[user, assistant]** ve user mesajı
      **DOĞRUDAN sorudur** — `KAYNAKLAR:`/`SORU:` işareti YOKTUR (ölçüldü 2026-08-06: 0/80 ve
      0/40), `soru` diye bir alan da yoktur (anahtarlar: messages · kanun_adi · kanun_no ·
      madde_no · _complexity · _src_len · _set).

    🚨 Görev 3 briefinin sürümü yalnız `SORU:` işaretli mesajı tanıyor, sonra `rec.get("soru")`
    boş dönünce her GERÇEK DEV kaleminde `ValueError` atıyordu — süzgeç hiç koşamıyordu.
    Ters tuzak da gerçek: `.get("soru", "")` yazılsa süzgeç sessizce NO-OP olur ve sızıntı
    fark edilmeden eğitime girer. Bu yüzden çıkarılamayan soru = HATA, atlama değil.
    """
    for m in rec.get("messages") or []:
        if m.get("role") != "user":
            continue
        c = m.get("content") or ""
        if "SORU:" in c:
            s = c.split("SORU:")[-1].strip()
            if s:
                return s
            break
        if _BAGLAM_BASLIGI.search(c):
            # Bağlam bloğu var ama soru işareti yok: bloğun tamamını soru saymak çöp anahtar
            # üretir, hiçbir şey eşleşmez ve süzgeç sessizce hiçbir şey atmaz.
            raise ValueError(f"bağlam bloğu var ama SORU: işareti yok: anahtarlar={sorted(rec)}")
        s = c.strip()
        if s:
            return s
        break
    s = (rec.get("soru") or "").strip()
    if not s:
        raise ValueError(f"soru metni çıkarılamadı: anahtarlar={sorted(rec)}")
    return s


def _baglam(rec):
    """KAYNAKLAR bloğu — `raft_scrubbed` onu ZATEN 900-klipli kurmuş (ADR-0013 eval aynası)."""
    u = rec["messages"][1]["content"]
    return u.split("KAYNAKLAR:\n", 1)[1].rsplit("\n\nSORU:", 1)[0]


def _anahtar(kanun, madde):
    """(kanun_no, tip, numara) — repo'nun TEK madde normalleştiricisi (`madde_anahtar`).

    # Why ikinci bir normalleştirici yazılmadı: brief'in `.upper()` tabanlı sürümü Türkçe
    # büyük harfte ayrışıyor — `'Geçici'.upper() == 'GEÇICI' != 'GEÇİCİ'` — ve külliyatta HER
    # İKİ yazım da var (166 `Geçici Madde N` · 88 `GEÇİCİ MADDE N`). Ayrı sayılan iki yazım
    # sızıntıyı kaçırır ve hiçbir yerde hata vermez. `madde_anahtari` sayı grubunu alıp
    # geçici/normal ayrımını tip alanında taşıyor, bu sınıfa karşı bağışık ve zaten test edilmiş.
    # Ölçüldü (2026-08-06): iki normalleştirici bu veride AYNI sonucu veriyor (atılan 436).
    """
    return madde_anahtari(kanun, madde)


def sizinti_suz(satirlar, dev_yollari):
    """DEV/CANON'a değen kalemleri at — SORU metni VE ALTIN MADDE düzeyinde.

    # Why madde düzeyi de: soru düzeyinde kesişim ölçüldü ve 0, ama ALTIN MADDE düzeyinde
    # 67/70 örtüşüyor. `τ_g` v1'de bu hijyen yok (pre-existing, düzeltilmiyor); yeni kol için
    # bedeli ~%3 havuz kaybı, karşılığı temiz bir DEV ölçümü.
    """
    yasak_soru, yasak_madde = set(), set()
    for yol in dev_yollari:
        if not os.path.exists(yol):
            raise FileNotFoundError(f"sızıntı süzgeci kaynağı yok: {yol}")
        with open(yol, encoding="utf-8") as f:
            for satir in f:
                if not satir.strip():
                    continue
                d = json.loads(satir)
                yasak_soru.add(_soru(d))          # boş dönerse ValueError — no-op süzgeç YASAK
                yasak_madde.add(_anahtar(d.get("kanun_no"), d.get("madde_no")))
    return [r for r in satirlar
            if _soru(r) not in yasak_soru
            and _anahtar(r.get("gold_kanun_no"), r.get("gold_madde_no")) not in yasak_madde]


def kayit(rec, i, g):
    """Hasat kaydı. `chosen` kalemin KENDİ grounded hedefi — dış model kullanılmaz (ADR-0051 m.2)."""
    return {
        "id": f"raft{i}", "tip": "m1_yeterli", "soru": _soru(rec),
        "chosen": rec["messages"][2]["content"],
        "rejected": g.text,
        "context_shown": _baglam(rec),
        "mode": MODE,
        "gold_kanun_no": rec.get("gold_kanun_no"), "gold_madde_no": rec.get("gold_madde_no"),
        "finish_reason": g.finish_reason, "completion_tokens": g.completion_tokens,
        "forced_close": g.forced_close, "reasoning_len": g.reasoning_len,
    }


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--havuz", default=HAVUZ)
    p.add_argument("--out", required=True)
    p.add_argument("--limit", type=int, default=0, help="kaç ÜRETİM denenecek (pilot)")
    p.add_argument("--target", type=int, default=0, help="kaç KABUL edilene kadar (üretim)")
    p.add_argument("--seed", type=int, default=3407)
    p.add_argument("--server-url", default="http://127.0.0.1:8080/v1")
    p.add_argument("--server-model", default="local")
    p.add_argument("--think-budget", type=int, default=1024)   # ADR-0043 rejim değişmezi
    p.add_argument("--max-new-tokens", type=int, default=512)  # ADR-0043 rejim değişmezi
    p.add_argument("--concurrency", type=int, default=1, help="sunucunun -np değeriyle ESLESMELI")
    p.add_argument("--not", dest="not_", default="",
                   help="künyeye aynen yazılacak serbest not (ör. sarj durumu, gguf yolu)")
    return p.parse_args()


def _devam(yol):
    if not os.path.exists(yol):
        return set()
    with open(yol, encoding="utf-8") as f:
        return {json.loads(l)["id"] for l in f if l.strip()}


def main():
    a = parse_args()
    if not (a.limit or a.target):
        raise SystemExit("--limit (pilot) ya da --target (üretim) ver")

    with open(a.havuz, encoding="utf-8") as f:
        satirlar = [json.loads(l) for l in f if l.strip()]
    grounded = [r for r in satirlar if r.get("slice") == "grounded"]
    temiz = sizinti_suz(grounded, DEV_YOLLARI)
    print(f"[b10] havuz {len(grounded)} → sızıntı süzgecinden sonra {len(temiz)} "
          f"(atılan {len(grounded) - len(temiz)})")

    isler = list(enumerate(temiz))
    random.Random(a.seed).shuffle(isler)
    gorulen = _devam(a.out)
    isler = [(i, r) for i, r in isler if f"raft{i}" not in gorulen]

    from openai import OpenAI
    client = OpenAI(base_url=a.server_url, api_key=os.environ.get("OPENAI_API_KEY", "none"),
                    max_retries=int(os.environ.get("LLM_MAX_RETRIES", "8")),
                    timeout=float(os.environ.get("LLM_TIMEOUT_S", "300")))

    kilit = threading.Lock()
    denenen = kabul = 0
    t0 = time.time()
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    cikti = open(a.out, "a", encoding="utf-8")

    def uret(is_):
        nonlocal denenen, kabul
        i, rec = is_
        try:
            g = generate_http(client, a.server_model, _soru(rec), a.max_new_tokens,
                              sources_block=_baglam(rec), thinking="on",
                              think_budget=a.think_budget, server_url=a.server_url)
        except Exception as e:
            print(f"  id=raft{i} üretim hatası: {e}", flush=True)
            return None
        with kilit:
            denenen += 1
            n = denenen
        # KABUL: model altın bağlamdayken ÇEKİNDİYSE bu bir B10 örneğidir.
        if not exact_reject(g.text, MODE):
            if n % 25 == 0:
                print(f"  denenen={n} kabul={kabul} oran={kabul/n:.3f} "
                      f"| {(time.time()-t0)/n:.2f} s/üretim", flush=True)
            return None
        return kayit(rec, i, g)

    limit = a.limit or len(isler)
    with ThreadPoolExecutor(max_workers=a.concurrency) as ex:
        kuyruk, sira = set(), iter(isler[:limit])
        for _ in range(a.concurrency):
            nxt = next(sira, None)
            if nxt is not None:
                kuyruk.add(ex.submit(uret, nxt))
        while kuyruk:
            bitti, kuyruk = wait(kuyruk, return_when=FIRST_COMPLETED)
            for f in bitti:
                r = f.result()
                if r:
                    with kilit:
                        kabul += 1
                    cikti.write(json.dumps(r, ensure_ascii=False) + "\n")
                    cikti.flush()
            if a.target and kabul >= a.target:
                break
            for _ in bitti:
                nxt = next(sira, None)
                if nxt is not None:
                    kuyruk.add(ex.submit(uret, nxt))
    cikti.close()

    kunye = {
        "denenen": denenen, "kabul": kabul,
        "kabul_orani": round(kabul / denenen, 4) if denenen else 0.0,
        "havuz_ham": len(grounded), "havuz_temiz": len(temiz),
        "seed": a.seed, "think_budget": a.think_budget, "max_new_tokens": a.max_new_tokens,
        "server_model": a.server_model, "mode": MODE, "sufficiency_preamble": False,
        "sizinti_suzgeci_kaynaklari": DEV_YOLLARI, "canon_notu": CANON_NOTU,
        "s_uretim": round((time.time() - t0) / denenen, 3) if denenen else 0.0,
        "not": a.not_,
    }
    with open(a.out.replace(".jsonl", "_KUNYE.json"), "w", encoding="utf-8") as f:
        json.dump(kunye, f, ensure_ascii=False, indent=2)
    print(f"[b10] BİTTİ · {json.dumps(kunye, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
