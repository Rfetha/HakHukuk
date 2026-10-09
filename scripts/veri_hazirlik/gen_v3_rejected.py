#!/usr/bin/env python3
"""v3 ADIM 2 — ORPO 'rejected' üretimi: v2b modelinin ZOR near-miss bağlamda GERÇEK fabrikasyonu.

v3_recipe Q4: rejected = v2b'nin zor-bağlamda örneklenmiş gerçek fabrikasyonu (on-policy zor-negatif).
build_sft_v3 pack çıktısını (packed_v3.jsonl) alır, her trap bağlamını EVAL M2 ile AYNI biçimde
(RAG_MULTI system + clip_sources_block 900 + soru) v2b adapter'a verir, greedy üretir:
  · REJECT_RE eşleşir  → model ÇEKİMSER kaldı → ORPO için kontrast YOK → ELE (funnel'da say).
  · eşleşmez          → model FABRİKE etti → 'rejected' olarak TUT.

Bu ADIM aynı zamanda v2b'nin eval-eşli zor-trap'te fabrikasyon oranını ÖLÇER (K3/paper-değerli funnel).
Lokal RTX 5070 inference, $0. Dirençli (resume): çıktıdaki id'leri atlar. --target ile hedef fabrikasyon.

Kullanım:
  source ~/code/global_venv/bin/activate
  python scripts/veri_hazirlik/gen_v3_rejected.py --limit 20                    # SMOKE (yükleme+hız+çıktı denetimi)
  python scripts/veri_hazirlik/gen_v3_rejected.py --target 2500                 # hedef 2500 fabrikasyon
"""
import argparse
import json
import os
import random
import sys
import time

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

import torch
from unsloth import FastModel

from raft_pack import SYSTEM_PROMPT_RAG_MULTI
from build_sft_v2b import clip_sources_block, _norm
from score_abstention import REJECT_RE   # deterministik red-ifadesi (eval ile AYNI)

# EVAL M2 = ORACLE tek-kaynak framing (bench_m2_v2b_detail mode="oracle"). SYSTEM_PROMPT_RAG
# "çekimser kal" DEMEZ → fabrikasyonu tetikler (eval'de v2b fab=0.654). RAG_MULTI ise açıkça
# reddi teşvik eder → over-abstain. v3 abstain-çifti eval M2'yi hedeflediği için ORACLE kullanılır.
from hakhukuk.cekirdek.istem import SISTEM_TEK_KAYNAK as SYSTEM_PROMPT_RAG

PACKED = "data/_ham_ve_ara/orpo_packed.jsonl"
OUT = "data/_ham_ve_ara/orpo_rejected.jsonl"


def build_model(model_name, adapter, max_seq_len):
    model, tokenizer = FastModel.from_pretrained(
        model_name=model_name, max_seq_length=max_seq_len,
        load_in_4bit=True, full_finetuning=False,
    )
    if adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, adapter)
        print(f"[v3-rej] adapter yüklendi: {adapter}", flush=True)
    FastModel.for_inference(model)
    return model, tokenizer


def _build_conv(soru, oracle_source, sources_block, clip):
    if oracle_source is not None:      # EVAL M2 oracle: tek-kaynak + SYSTEM_PROMPT_RAG
        sys = SYSTEM_PROMPT_RAG
        user = f"KAYNAK MADDE:\n{oracle_source[:clip]}\n\nSORU: {soru}"
    else:                              # RAG_MULTI çok-kaynak
        sys = SYSTEM_PROMPT_RAG_MULTI
        user = f"KAYNAKLAR:\n{sources_block}\n\nSORU: {soru}"
    return [{"role": "system", "content": sys}, {"role": "user", "content": user}]


def generate_batch(model, tokenizer, convs, max_new_tokens):
    """Batched greedy üretim (left-pad → tek input_len slice). attention_mask set (warning yok).
    ⚠️ pad = GERÇEK <pad>(0), eos(1) DEĞİL: eos ile left-pad batched üretimde baş-token mojibake
    yapıyordu (batch=8'de %26; tekilde %0). <pad> ile temiz (2026-07-04)."""
    tokenizer.padding_side = "left"
    pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id
    enc = tokenizer.apply_chat_template(
        convs, tokenize=True, add_generation_prompt=True, return_tensors="pt",
        padding=True, return_dict=True,
    ).to(model.device)
    with torch.no_grad():
        out = model.generate(
            input_ids=enc["input_ids"], attention_mask=enc["attention_mask"],
            max_new_tokens=max_new_tokens, do_sample=False,
            temperature=None, top_p=None, top_k=None,
            pad_token_id=pad_id,
        )
    ilen = enc["input_ids"].shape[1]
    return [tokenizer.decode(o[ilen:], skip_special_tokens=True).strip() for o in out]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--packed", default=PACKED)
    p.add_argument("--out", default=OUT)
    p.add_argument("--adapter", default=None, help="LoRA adapter dizini; yoksa ham base")
    # ⚠️ Default YOK (bilerek) — fabrikasyonlar hangi modelden toplandığı ÖNEMLİ.
    p.add_argument("--model", required=True, help="HF repo id veya yerel yol")
    p.add_argument("--target", type=int, default=2500, help="hedef fabrikasyon (rejected) sayısı; 0=tümü")
    p.add_argument("--max-candidates", type=int, default=0, help="işlenecek aday tavanı (0=sınırsız)")
    p.add_argument("--max-new-tokens", type=int, default=96,
                   help="fabrikasyon ilk ~20 token'da belli → 96 yeterli + hızlı")
    p.add_argument("--max-chunk-chars", type=int, default=900, help="eval-mirror clip (v2b eğitildiği uzunluk)")
    p.add_argument("--max-seq-len", type=int, default=2048)
    p.add_argument("--seed", type=int, default=3407)
    p.add_argument("--limit", type=int, default=0, help="ilk N aday (SMOKE)")
    p.add_argument("--oracle", action="store_true",
                   help="EVAL M2 ile BİREBİR: tek yanlış-kaynak + SYSTEM_PROMPT_RAG (fab tetikler)")
    p.add_argument("--batch", type=int, default=8, help="aynı anda üretilen prompt (throughput)")
    a = p.parse_args()

    rows = [json.loads(l) for l in open(a.packed, encoding="utf-8") if l.strip()]
    # Deterministik karıştır → eval-eşli dağılımı korurken çeşitli işle (fixed seed).
    random.Random(a.seed).shuffle(rows)
    if a.limit:
        rows = rows[:a.limit]

    done = set()
    if os.path.exists(a.out):                       # resume
        for l in open(a.out, encoding="utf-8"):
            if l.strip():
                done.add(json.loads(l)["id"])
    todo = [r for r in rows if r["id"] not in done]
    print(f"[v3-rej] toplam aday={len(rows)} tamamlanan={len(done)} kalan={len(todo)} "
          f"| hedef fabrikasyon={a.target or '∞'}", flush=True)

    model, tokenizer = build_model(a.model, a.adapter, a.max_seq_len)

    f = open(a.out, "a", encoding="utf-8")
    n_fab = sum(1 for l in open(a.out, encoding="utf-8") if l.strip() and not json.loads(l)["abstained"]) \
        if os.path.exists(a.out) else 0
    n_proc = n_abst = 0
    t0 = time.time()
    try:
        for bs in range(0, len(todo), a.batch):
            if a.target and n_fab >= a.target:
                print(f"[v3-rej] hedef {a.target} fabrikasyon ULAŞILDI → dur.", flush=True)
                break
            if a.max_candidates and n_proc >= a.max_candidates:
                print(f"[v3-rej] aday tavanı {a.max_candidates} → dur.", flush=True)
                break
            batch = todo[bs:bs + a.batch]
            convs, meta = [], []
            for r in batch:
                oracle_src = r["trap_text"] if a.oracle else None
                sb = clip_sources_block(r["sources_block"], "", "", a.max_chunk_chars)
                convs.append(_build_conv(r["soru"], oracle_src, sb, a.max_chunk_chars))
                meta.append((r, sb))
            answers = generate_batch(model, tokenizer, convs, a.max_new_tokens)
            for (r, sb), ans in zip(meta, answers):
                abstained = bool(REJECT_RE.search(ans)) or len(ans) < 8
                out = {
                    "id": r["id"], "soru": r["soru"], "sources_block": sb,
                    "oracle": bool(a.oracle),
                    "ov_gold": r["ov_gold"], "ov_q": r["ov_q"], "judge_flag": r["judge_flag"],
                    "n_far": r["n_far"],
                    "gold_kanun_adi": r["gold_kanun_adi"], "gold_madde_no": r["gold_madde_no"],
                    "gold_kanun_no": r["gold_kanun_no"], "gold_text": r["gold_text"],
                    "trap_kanun_adi": r["trap_kanun_adi"], "trap_madde_no": r["trap_madde_no"],
                    "trap_text": r["trap_text"],
                    "model_answer": ans, "abstained": abstained,
                }
                f.write(json.dumps(out, ensure_ascii=False) + "\n")
                n_proc += 1
                if abstained:
                    n_abst += 1
                else:
                    n_fab += 1
            f.flush()
            spd = (time.time() - t0) / n_proc
            print(f"  [{n_proc}] fab={n_fab} abst={n_abst} | fab_oranı={n_fab/max(1,n_proc):.2f} "
                  f"| {spd:.1f}s/örnek (batch={a.batch})", flush=True)
    finally:
        f.close()

    fr = n_fab / max(1, n_proc)
    print(f"[v3-rej] → {a.out}  işlenen={n_proc} fabrikasyon(rejected)={n_fab} çekimser={n_abst}", flush=True)
    print(f"[v3-rej] v2b zor-trap FABRİKASYON ORANI = {fr:.3f}  (K3 funnel; eval M2 fabrication ~0.593 ile kıyasla)")


if __name__ == "__main__":
    main()
