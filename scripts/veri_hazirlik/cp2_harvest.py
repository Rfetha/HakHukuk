#!/usr/bin/env python3
"""CP2 — `rejected` havuzunun ÇIPLAK BASE'den yeniden hasadı (ADR-0042 · ADR-0045 m.4).

Mevcut havuz emekli 12B hattının fabrikasyonları; yeni modele **başka bir modelin hatalarını**
öğretir. Yeniden hasat: çıplak base, **bütçeli düşünce (1024+512)** — ADR-0043 gereği hasat,
kolların eğitileceği ve dağıtılacağı kiple AYNI olmalı, yoksa ADR-0042'nin kendi *on-policy*
gerekçesi kendi künyesi tarafından çürütülür.

**İKİ TİP** (ADR-0045 m.4 — `τ_a`'nın iki eksende de çalışması gerekiyor):

  m2   tuzak madde VERİLMİŞ, kaynak soruyu cevaplamıyor  → ARA KAPI'nın ön-kayıtlı ekseni
       istem = build_orpo_v3 ORACLE framing (SYSTEM_PROMPT_RAG + trap_text[:900]) — BİREBİR,
       çünkü havuzdaki `chosen` bu isteme karşı üretildi; istem kayarsa çift tutarsızlaşır.
  m2b  gold HİÇ YOK, yalnız distractor                   → `τ_g`'nin gerçek açığı (M2b 0.607)
       istem = eval m2b ile birebir (RAG_MULTI + pack_context(include_gold=False) + 900 klip)

**Kabul ölçütü:** `score_abstention.exact_reject` RED SAYMIYOR → model tuzağa düşmüş, gerçek
bir negatif örnek. Reddettiyse ORPO için kontrast yok → elenir (huniye yazılır).

🚨 Üretim yolu `gen_eval_grounded.generate_http` — yeniden yazılmaz. Bu hattın hata sınıfı
sessiz protokol sapması; ikinci bir üretim gövdesi tam olarak onu üretir.

Kullanım:
  # PİLOT (kabul oranı + hız ölçümü — hasat boyutlandırması buradan çıkar)
  python scripts/veri_hazirlik/cp2_harvest.py --type m2  --limit 150 --out data/_ham_ve_ara/cp2_pilot_m2.jsonl
  python scripts/veri_hazirlik/cp2_harvest.py --type m2b --limit 150 --out data/_ham_ve_ara/cp2_pilot_m2b.jsonl
  # ÜRETİM: --target N (N kabul edilen negatife ulaşınca durur), dirençli (resume)
"""
import argparse
import json
import os
import random
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

import raft_pack
from build_sft_v2b import clip_sources_block
from gen_eval_grounded import generate_http
from score_abstention import exact_reject

PACKED = "data/_ham_ve_ara/orpo_packed.jsonl"
MADDE_PATH = "data/corpus/mevzuat_maddeler.jsonl"
TRAP_CLIP = 900          # build_orpo_v3 ile BİREBİR (havuzdaki `chosen` bu istemle üretildi)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--type", choices=["m2", "m2b"], required=True,
                   help="m2 = tuzak verilmiş (ARA KAPI ekseni) · m2b = gold hiç yok (τ_g'nin açığı)")
    p.add_argument("--packed", default=PACKED)
    p.add_argument("--madde-path", default=MADDE_PATH)
    p.add_argument("--out", required=True)
    p.add_argument("--limit", type=int, default=0, help="kaç ÜRETİM denenecek (pilot)")
    p.add_argument("--target", type=int, default=0, help="kaç KABUL edilene kadar (üretim)")
    p.add_argument("--skip-first", type=int, default=0,
                   help="havuz sırasındaki ilk N uygun kalemi ATLA — ek tur için. "
                        "Gerekçe: çıktı dosyası yalnız KABUL edilenleri saklıyor, bu yüzden "
                        "`load_done` 'zaten denendi'yi ifade edemez; taze dizinde koşan bir ek "
                        "tur sırayı 0'dan başlatıp aynı kalemleri yeniden üretir. Önceki turun "
                        "künyesindeki `denenen` sayısını buraya ver.")
    p.add_argument("--seed", type=int, default=3407)
    p.add_argument("--server-url", default="http://127.0.0.1:8080/v1")
    p.add_argument("--server-model", default="local")
    p.add_argument("--think-budget", type=int, default=1024)   # ADR-0043, rejim değişmezi
    p.add_argument("--max-new-tokens", type=int, default=512)  # ADR-0043, rejim değişmezi
    p.add_argument("--distractors", type=int, default=4)
    p.add_argument("--max-chunk-chars", type=int, default=900)
    # ⚠️ Sunucudaki `-np` ile EŞLEŞMELİ. llama-server tek slotla açıldıysa (`-np` yok) burada
    # 8 vermek kuyruk yapar, hızlandırmaz: 11,12 s/üretim bir GECİKME sayısıdır, verim değil.
    p.add_argument("--concurrency", type=int, default=1,
                   help="eş zamanlı üretim isteği (sunucunun --parallel/-np değeriyle eşleşmeli)")
    # ADR-0047 m.3 — ön-kayıtlı VERİM KAPISI. Bulut koşusunda para insan bakmadan akıyor;
    # tahmin tutmazsa koşu kendi kendini durdurur ve sayı negatif bulgu olarak yazılır.
    p.add_argument("--gate-after-s", type=int, default=0,
                   help="bu saniyeden sonra gerçek s/üretim denetlenir (0 = kapalı)")
    p.add_argument("--gate-max-s-per-uretim", type=float, default=0.0,
                   help="ADR-0047 m.3: tahminin 2 katı. Aşılırsa koşu DURUR")
    return p.parse_args()


def load_done(path):
    """Dirençli: yarıda kesilen koşu baştan başlamaz (hasat saatler sürüyor)."""
    if not os.path.exists(path):
        return set(), 0
    ids, n = set(), 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                ids.add(r["id"])
                n += 1
    return ids, n


def main():
    a = parse_args()
    if not (a.limit or a.target):
        raise SystemExit("--limit (pilot) ya da --target (üretim) ver — ikisi de yoksa sınırsız koşar")

    rows = [json.loads(l) for l in open(a.packed, encoding="utf-8") if l.strip()]
    rows = [r for r in rows if r.get("slice") == "abstain_trap_v3"]
    random.seed(a.seed)
    random.shuffle(rows)

    pool_recs = pool_by_kanun = None
    if a.type == "m2b":
        pool_recs, pool_by_kanun = raft_pack.load_madde_pool(a.madde_path)
        print(f"[cp2] distractor havuzu: {len(pool_recs)} madde ({len(pool_by_kanun)} kanun)")

    from openai import OpenAI
    client = OpenAI(base_url=a.server_url, api_key=os.environ.get("OPENAI_API_KEY", "none"),
                    max_retries=int(os.environ.get("LLM_MAX_RETRIES", "8")),
                    timeout=float(os.environ.get("LLM_TIMEOUT_S", "300")))

    seen_ids, n_prev = load_done(a.out)
    tried = kept = 0
    tok_sum = forced = 0
    t0 = time.time()
    # Açılış geçicisi: `concurrency` kalem aynı anda başlar ve birlikte iner, yani boru hattı
    # dolana kadar geçen süre ölçekte amortize olur (7.500 üretimde toplam sürenin ~%0,6'sı).
    # Verim kapısı bu yüzden t0'dan DEĞİL, boru hattı dolduktan sonradan ölçer.
    t_warm = n_warm = 0
    mode = "oracle" if a.type == "m2" else "distractor_nogold"

    print(f"[cp2] tip={a.type} · mod={mode} · havuz={len(rows)} · düşünce {a.think_budget}"
          f"+{a.max_new_tokens} · seed {a.seed} · devam={n_prev} kayıt")

    def baglam(i, rec):
        """Kalemin istemini kur. `None` → atlanır (eksik alan)."""
        if a.type == "m2":
            # build_orpo_v3 ORACLE framing ile BİREBİR
            source = (rec.get("trap_text") or "")[:TRAP_CLIP]
            return (source, None) if source else None
        gold = rec.get("gold_text") or ""
        if not gold:
            return None
        grec = {"kanun_adi": rec.get("gold_kanun_adi", ""),
                "madde_no": rec.get("gold_madde_no", ""),
                "kanun_no": rec.get("gold_kanun_no", ""),
                "messages": []}
        # ⚠️ RNG kalemin SIRA İNDEKSİNDEN türer (seed + i) — eş zamanlılık bunu değiştirmez,
        # yani üretilen bağlam iş parçacığı sırasından BAĞIMSIZ ve tekrarlanabilir.
        rng = random.Random(a.seed + i)
        chunks, _ = raft_pack.pack_context(
            grec, gold, pool_recs, pool_by_kanun, a.distractors, rng,
            include_gold=False)              # gold HİÇ YOK — M2b tanımı
        sources_block = raft_pack.format_sources_block(chunks)
        if a.max_chunk_chars > 0:            # eval-mirror klip (ADR-0011 değişmezi)
            gold_label = f"{grec['kanun_adi']} {grec['madde_no']}"
            sources_block = clip_sources_block(sources_block, "", gold_label, a.max_chunk_chars)
        return (None, sources_block)

    kilit = threading.Lock()

    def kararli_hiz():
        """Açılış geçicisi HARİÇ s/üretim — verim kapısının ölçtüğü büyüklük.

        # Why: t0'dan kümülatif ortalama, boru hattı dolarken geçen ~1 dalga süresini her
        # kaleme paylaştırır ve erken okumada hızı sistematik olarak KÖTÜ gösterir. 2026-08-02'de
        # bu, gerçek hızı ~2,4 s/üretim olan bir koşuyu 600. saniyede 2,97 ile durdurdu
        # (eşik 2,88). Eşik değişmedi; yanlı olan tahmin ediciydi.
        """
        if t_warm and tried > n_warm:
            return (time.time() - t_warm) / (tried - n_warm)
        return (time.time() - t0) / tried if tried else 0.0

    def uret(arg):
        """Tek kalem: üret → kabul ölçütünü uygula. Sayaçlar kilit altında."""
        nonlocal tried, kept, tok_sum, forced, t_warm, n_warm
        i, rec, source, sources_block = arg
        try:
            g = generate_http(client, a.server_model, rec["soru"], a.max_new_tokens,
                              source=source, sources_block=sources_block,
                              thinking="on", think_budget=a.think_budget,
                              server_url=a.server_url)
        except Exception as e:
            print(f"  id={rec['id']} üretim hatası: {e}", flush=True)
            return None
        with kilit:
            tried += 1
            tok_sum += g.completion_tokens or 0
            forced += 1 if g.forced_close else 0
            n = tried
            if n == a.concurrency:          # boru hattı doldu → geçici bitti
                t_warm, n_warm = time.time(), n
        # KABUL ÖLÇÜTÜ: regex ön-filtre — RED değilse aday (ADR-0046 m.1: kabul kararı
        # hakemde, bu yalnız bedava ön-eleme).
        if exact_reject(g.text, mode):
            if n % 25 == 0:
                el = time.time() - t0
                print(f"  denenen={n} kabul={kept} oran={kept/n:.3f} | {el/n:.2f} s/üretim "
                      f"(kararlı {kararli_hiz():.2f}) | ort tok={tok_sum/n:.0f}", flush=True)
            return None
        return {
            "id": rec["id"], "tip": a.type, "soru": rec["soru"],
            "rejected": g.text, "mode": mode,
            # Hakeme GERÇEKTEN gösterilen bağlam saklanır: yoksa kabul edilen negatifin
            # denetimi (LLM red hakemi) bağlamı yeniden üretmek zorunda kalır ve o yol
            # kırılgandır. Denetlenemeyen bir eğitim örneği, ölçülemeyen bir sayıdır.
            "context_shown": sources_block if sources_block is not None else source,
            "finish_reason": g.finish_reason, "completion_tokens": g.completion_tokens,
            "forced_close": g.forced_close, "reasoning_len": g.reasoning_len,
        }

    # Uygun kalemleri sırayla hazırla (üretim değil, yalnız istem kurulumu — ucuz).
    isler = []
    for i, rec in enumerate(rows):
        if rec["id"] in seen_ids:
            continue
        b = baglam(i, rec)
        if b is None:
            continue
        isler.append((i, rec, b[0], b[1]))

    if a.skip_first:
        if a.skip_first >= len(isler):
            raise SystemExit(f"--skip-first {a.skip_first} ≥ uygun kalem {len(isler)} — havuz bitti")
        isler = isler[a.skip_first:]
        print(f"[cp2] --skip-first {a.skip_first} → sıra {a.skip_first}. kalemden başlıyor", flush=True)

    print(f"[cp2] {len(isler)} uygun kalem · eş zamanlılık={a.concurrency}", flush=True)

    kapi = None
    kapi_bakildi = False
    kararli_dururken = None      # besleme kesildiği andaki kararlı hız (boşalma fazı hariç)

    def durmali():
        """Durma koşulları. VERİM KAPISI (ADR-0047 m.3) ÖNCE bakılır: bütçe dolduğu için erken
        dönülürse kapı hiç değerlendirilmez ve huniye hak edilmemiş bir 'geçildi' damgası düşer
        — `-np 64` testi 2,93 s/üretim ile tam bunu yaptı (eşik 2,88)."""
        nonlocal kapi, kapi_bakildi, kararli_dururken

        def dur():
            nonlocal kararli_dururken
            if kararli_dururken is None:
                kararli_dururken = round(kararli_hiz(), 2)
            return True

        if a.gate_after_s and tried and (time.time() - t0) >= a.gate_after_s:
            kapi_bakildi = True
            hiz = kararli_hiz()          # açılış geçicisi hariç — eşik 2,88 değişmedi
            if hiz > a.gate_max_s_per_uretim and kapi is None:
                kapi = (f"DURDU: {hiz:.2f} s/üretim (kararlı) > {a.gate_max_s_per_uretim:.2f} "
                        f"(ADR-0047 m.3, {tried} üretimde)")
                print(f"\n🔴 VERİM KAPISI {kapi}", flush=True)
            if kapi is not None:
                return dur()
        if a.limit and tried >= a.limit:
            return dur()
        if a.target and (n_prev + kept) >= a.target:
            return dur()
        return False

    # ⚠️ SÜREKLİ BESLEME, öbek DEĞİL. Öbekli sürümde her öbek en yavaş kalemini bekliyordu:
    # CP2-c duman testinde slot doluluğu **%70** ölçüldü (10.220 slot-saniye iş / 14.496 kapasite).
    # Kalemler bağımsız olduğu için bariyerin hiçbir işlevi yoktu — yalnız GPU'yu boş bekletiyordu.
    # Gönderilen istek, sıra, seed ve örnekleme AYNI; değişen yalnız zamanlama.
    with open(a.out, "a", encoding="utf-8") as f, \
            ThreadPoolExecutor(max_workers=max(1, a.concurrency)) as pool:
        sira = iter(isler)
        bekleyen = set()

        def besle():
            while len(bekleyen) < a.concurrency and not durmali():
                try:
                    bekleyen.add(pool.submit(uret, next(sira)))
                except StopIteration:
                    return

        besle()
        while bekleyen:
            biten, kalan = wait(bekleyen, return_when=FIRST_COMPLETED)
            bekleyen.clear()
            bekleyen.update(kalan)
            for fut in biten:
                rec_out = fut.result()
                if rec_out is None:
                    continue
                with kilit:
                    kept += 1
                    f.write(json.dumps(rec_out, ensure_ascii=False) + "\n")
                    f.flush()
            besle()

    el = time.time() - t0
    funnel = {
        "tip": a.type, "mod": mode,
        "denenen": tried, "kabul": kept, "elenen_red": tried - kept,
        "kabul_orani": round(kept / tried, 4) if tried else None,
        "saniye_per_uretim": round(el / tried, 2) if tried else None,
        # Kapının okuduğu büyüklük: açılış geçicisi hariç, besleme kesildiği anda.
        "saniye_per_uretim_kararli": kararli_dururken,
        "ort_completion_tokens": round(tok_sum / tried, 1) if tried else None,
        "zorunlu_kapatma": f"{forced}/{tried}",
        "dusunce_butcesi": a.think_budget, "cevap_butcesi": a.max_new_tokens,
        "seed": a.seed, "toplam_kayit": n_prev + kept, "gecen_sure_s": round(el, 1),
        "es_zamanlilik": a.concurrency,
        "skip_first": a.skip_first,          # ek turda hangi sıradan başlandığı — provenans
        "verim_kapisi": kapi or ("kapalı" if not a.gate_after_s else
                                 f"geçildi (eşik {a.gate_max_s_per_uretim:.2f} s/üretim)"
                                 if kapi_bakildi else
                                 f"değerlendirilmedi (koşu {a.gate_after_s}s'den kısa bitti)"),
    }
    print("\n[cp2] HUNİ: " + json.dumps(funnel, ensure_ascii=False))
    fp = a.out.replace(".jsonl", "_funnel.json")
    with open(fp, "w", encoding="utf-8") as f:
        json.dump(funnel, f, ensure_ascii=False, indent=2)
    print(f"[cp2] → {a.out}\n[cp2] huni → {fp}")


if __name__ == "__main__":
    main()
