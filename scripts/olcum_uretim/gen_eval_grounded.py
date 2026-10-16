#!/usr/bin/env python
"""Grounded eval üretici — base vs v1 karşılaştırması için MODEL cevabı + GERÇEK madde referansı.

Boşluk: `eval.py` referans=avukat-cevabı koyar; `groundedness.py --mode data` ise referans=
GERÇEK madde metni ister. `score_grounded_corpus.py` o madde-join köprüsünü yapar ama KORPUSU
(gold cevap) skorlar, model çıktısını değil. Bu script ikisini birleştirir:

  test.jsonl sorusu → model (base VEYA base+adapter, 4-bit) cevap üret
    → (kanun_no|madde_no) ile data/corpus/mevzuat_maddeler.jsonl'den GERÇEK madde metnini join et
    → detail.jsonl {soru, referans=madde metni, cevap=model çıktısı} → groundedness.py --mode data

Böylece base ve v1 TAM AYNI grounded sorularla, gerçek maddeye karşı ölçülür (dürüst kapı).
Örneklem deterministik (sabit seed) → base ve v1 aynı soruları görür.

Kullanım:
  # Base (referans):
  python scripts/olcum_uretim/gen_eval_grounded.py --label eval_base --n 40
  # v1 adapter:
  python scripts/olcum_uretim/gen_eval_grounded.py --label eval_v1 --adapter outputs/<tur> --n 40
  # Smoke (üretim+join testi, hızlı):
  python scripts/olcum_uretim/gen_eval_grounded.py --label smoke --n 2 --adapter outputs/<tur>

Sonra:
  python scripts/puanlama/groundedness.py --details outputs/eval/eval_v1_detail.jsonl --label eval_v1 --mode data
"""
import argparse
import json
import os
import random
import time
import urllib.request
from typing import NamedTuple

# `unsloth` ve `torch` yalnız yerel model yükleme yolunda, `build_model` içinde içe aktarılır (unsloth
# torch'tan ÖNCE — train_sft.py/eval.py ile aynı kural). Why: kiralık kartta üretim HTTP taşıyıcısıyla koşar
# ve küçük sunucu imajında bu paketler yok (ADR-0102); en tepedeki içe aktarma orada betiği açılmadan düşürürdü.



# M1/M3 — çok-kaynak (RAFT/distractor) sistem promptu: ortak modülden (eğitim ile AYNI, ADR-0013).
# ── scripts/ yol köprüsü (T5 2026-09-07 · ADR-0112 2026-10-16) ───────────────
# Kardeş modüller iç içe alt klasörlerde de bulunsun diye scripts/ kökü, altındaki HER
# derinlikteki klasör ve repo kökü sys.path'e girer. Uzantısız `import X` bu köprü olmadan
# taşımada SESSİZCE kırılır: ImportError çalışma zamanında, bazen GPU koşusunun ortasında.
# ⚠️ 39 dosyada BİREBİR aynı; değiştirirsen hepsinde değiştir (grep: "yol köprüsü").
import os, sys
_K = os.path.abspath(__file__)
_K = _K[:_K.rindex(os.sep + "scripts" + os.sep)] + os.sep + "scripts"  # dışarıda: ValueError
_Y = []
for _y, _alt, _f in os.walk(_K):
    _alt[:] = sorted(_a for _a in _alt if _a[0] not in "_.")
    _Y.append(_y)
sys.path[:0] = [*_Y, os.path.dirname(_K)]
# ─────────────────────────────────────────────────────────────────────────────

# İstem metinleri ürün paketinden gelir — TEK KAYNAK (plan Görev 5 / S18).
from hakhukuk.cekirdek.istem import (
    SISTEM_KOR as SYSTEM_PROMPT,
    SISTEM_TEK_KAYNAK as SYSTEM_PROMPT_RAG,
)

import raft_pack
SYSTEM_PROMPT_RAG_MULTI = raft_pack.SYSTEM_PROMPT_RAG_MULTI

# EVAL-MIRROR (2026-07-02, ADR-0013): eğitimin 900-char chunk clip'ini eval tarafında AYNEN
# kullan. Yoksa v2b, eğitildiğinden UZUN context'le ölçülür (haksız). clip_sources_block eğitimle
# birebir aynı fonksiyon → dağılım garantili eşleşir. (build_sft_v2b saf stdlib, torch/unsloth yok.)
from build_sft_v2b import clip_sources_block

from madde_anahtar import madde_anahtari  # harness izi: altın getirildi mi, kaçıncı sırada

import runlock  # aynı label'a paralel yazım = sessiz bozulma (bkz. runlock.py)
from part_dosya import part_ile_yaz  # yarım üretim `.part` kalır, puanlanmaz (F0.5 c)


def altin_ablasyonu(parcalar, altin_anahtar, k):
    """Altın maddeyi getirilen parçalardan DÜŞÜR, ilk k'yı döndür (ADR-0056 Karar 1).

    `m2b`'nin harness-AÇIK karşılığı budur: aynı 80 soru, aynı retriever, ama altın
    madde bağlamda YOK. Tek değişken "çeldiricileri kim seçti" olsun diye k+1 getirilip
    biri düşürülür — bağlam uzunluğu normal k=10 koşusuyla AYNI kalır.

    ⚠️ Why yeniden numaralama: `sira` 0-indeksli ve aşağı akıştaki recall hesabı onu
    okuyor. Düşürme sonrası boşluk bırakmak sessiz kayma üretir (tuzak 7.5'in ikizi).
    """
    kalan = [p for p in parcalar
             if madde_anahtari(p.get("kanun_no"), p.get("madde_no")) != altin_anahtar]
    return [dict(p, sira=yer) for yer, p in enumerate(kalan[:k])]


def ornekle(rows, idx, seed, n):
    """Madde metni JOIN olanlardan deterministik örneklem (kapsam=%100 garanti) → [(rec, soru, src)].
    ⚠️ Küresel `random`'u tohumlar (önceki satır içi hâliyle aynı yan etki)."""
    pool = []
    for r in rows:
        k = f"{norm(r.get('kanun_no'))}|{norm(r.get('madde_no'))}"
        src = idx.get(k, "")
        soru = extract(r)
        if src and soru:
            pool.append((r, soru, src))
    random.seed(seed)
    random.shuffle(pool)
    return pool[:n], len(pool)


def harness_baglami(rec, soru, retriever, ayar):
    """HARNESS AÇIK: bağlamı retriever seçer → (sources_block, harness_izi).
    `ayar`: `harness_k`, `rrf_k`, `harness_no_gold`, `max_chunk_chars` alanlarını taşıyan nesne
    (komut satırı argümanları ya da `baglam_dondur.Ayar`) — dondurulmuş bağlam aynı fonksiyondan üretilir."""
    altin = madde_anahtari(rec.get("kanun_no"), rec.get("madde_no"))
    if ayar.harness_no_gold:                    # ADR-0056: m2b'nin AÇIK karşılığı
        parcalar = altin_ablasyonu(
            retriever.getir(soru, ayar.harness_k + 1, rrf_k=ayar.rrf_k), altin, ayar.harness_k)
    else:
        parcalar = retriever.getir(soru, ayar.harness_k, rrf_k=ayar.rrf_k)
    sources_block = raft_pack.format_sources_block(
        [f"{p.get('kanun_adi','')} {p.get('madde_no','')}\n{p.get('text','')}"
         for p in parcalar])
    if ayar.max_chunk_chars > 0:                # EVAL-MIRROR: M1 ile AYNI kırpma
        gold_label = f"{rec.get('kanun_adi','')} {rec.get('madde_no','')}"
        ref_msgs = rec.get("messages") or []
        ref_answer = next(
            (m.get("content", "") for m in ref_msgs
             if m.get("role") in ("assistant", "model")), "")
        sources_block = clip_sources_block(
            sources_block, ref_answer, gold_label, ayar.max_chunk_chars)
    # Why kayda geçiyor: harness-AÇIK tablosunun ayırt etmesi gereken üç hâl
    # var — altın getirilmedi · getirildi ve cevaplandı · getirildi ama cevap
    # 900-char kırpmasının ötesindeydi (ADR-0054/K2'nin kabul edilen bedeli).
    harness_izi = {
        "k": ayar.harness_k,
        "rrf_k": ayar.rrf_k,
        "altin_dusuruldu": bool(ayar.harness_no_gold),
        "altin_sirasi": next(
            (p["sira"] for p in parcalar
             if madde_anahtari(p.get("kanun_no"), p.get("madde_no")) == altin), None),
        "getirilen": [f"{p.get('kanun_adi','')}|{p.get('madde_no','')}"
                      for p in parcalar],
    }
    return sources_block, harness_izi


MADDE_PATH = "data/corpus/mevzuat_maddeler.jsonl"


def parse_args():
    p = argparse.ArgumentParser()
    # ⚠️ Gömülü base default'u YOK (bilerek): sessizce yanlış modeli ölçmek, bir CANON
    # koşusunu fark edilmeden geçersiz kılar. --server-url yolunda gerekmez (HTTP taşıyıcı).
    p.add_argument("--model", default=os.environ.get("BASE_MODEL"),
                   help="HF repo id veya yerel yol (yerel yükleme yolu için zorunlu; "
                        "--server-url verildiyse kullanılmaz)")
    p.add_argument("--adapter", default=None,
                   help="LoRA adapter dizini (ör. outputs/<tur>); yoksa ham base")
    p.add_argument("--data", default="data/train/grounded_qa/test.jsonl")
    p.add_argument("--madde-path", default=MADDE_PATH)
    p.add_argument("--label", required=True, help="çıktı etiketi (eval_base / eval_v1)")
    p.add_argument("--n", type=int, default=40)
    p.add_argument("--seed", type=int, default=3407)
    p.add_argument("--max-seq-len", type=int, default=2048)
    p.add_argument("--max-new-tokens", type=int, default=512)
    p.add_argument("--out-dir", default="outputs/eval")
    p.add_argument("--with-source", action="store_true",
                   help="M4 RAG-modu: TEK gold madde metnini prompt'a koy (temiz Oracle, iyimser tavan)")
    p.add_argument("--distractors", type=int, default=0, metavar="N",
                   help="M1: gold + N hard-negative distractor (RAFT çok-kaynak). v2b grounding manşeti.")
    p.add_argument("--max-chunk-chars", type=int, default=900, metavar="N",
                   help="eval-mirror: her [KAYNAK] chunk'ını N char'a kırp — eğitim §5.1 truncation "
                        "fix ile AYNI (900≈243 tok; 5 chunk 2048'e sığar). 0=kapalı. v2b'yi eğitildiği "
                        "context uzunluğuyla ölçmek için ŞART (ADR-0013). Sadece --distractors modunda etkin.")
    p.add_argument("--empty-context", action="store_true",
                   help="M3 (E-set): hiç kaynak verme (boş bağlam) → doğru davranış=abstention")
    p.add_argument("--harness-indeks", default="", metavar="DIZIN",
                   help="HARNESS AÇIK (sprint3 Adım 4): bağlamı distractor kurgusu değil "
                        "RETRIEVER belirler. Kaynak bloğu, kırpma, sistem promptu ve üretim "
                        "rejimi M1 ile AYNI kalır — tek değişen bağlamın NEREDEN geldiği.")
    p.add_argument("--rrf-k", type=int, default=None, metavar="N",
                   help="HARNESS AÇIK: BM25 + bge-m3 füzyon sabiti. Verilmezse retriever.RRF_K "
                        "(10, ADR-0068); 60 = RQ2'nin üretim tarafındaki eski hâli. Değer her "
                        "satırın harness izine yazılır.")
    p.add_argument("--harness-k", type=int, default=5, metavar="N",
                   help="retriever'dan alınacak parça sayısı (S3a eğrisi: recall@5 0,750 · "
                        "@10 0,875 · @20 0,925). 900 char kırpma her parçaya ayrı uygulanır.")
    p.add_argument("--completion-fewshot", action="store_true",
                   help="chat-template YERİNE few-shot completion (foundation rakip: Mecellem CPT)")
    p.add_argument("--server-url", default=os.environ.get("LLAMA_SERVER_URL"),
                   help="OpenAI-uyumlu endpoint (llama-server veya OpenRouter). Verilirse "
                        "model YEREL yüklenmez, HTTP üzerinden üretilir (ADR-0025). "
                        "Ör: http://127.0.0.1:8080/v1")
    p.add_argument("--server-model", default="local",
                   help="--server-url ile gönderilecek model adı (llama-server'da önemsiz, "
                        "OpenRouter'da rakip model id'si)")
    # ── Düşünce kanalı (2026-07-24, CP0 / Qwen3.5) ──────────────────────────────
    # Düşünen modeller `add_generation_prompt` ile `<think>` açar. Bütçe içinde
    # `</think>` kapanmazsa llama-server ürettiğin HER ŞEYİ `reasoning_content`e koyar
    # ve `message.content` BOŞ döner: HTTP 200, geçerli JSON, hata yok — ve red-regex
    # o boş stringlerden sayı üretir. Qwen3.5-4B'de ölçüldü: varsayılan modda 1024
    # token'da bile content='' (research_log #39).
    #   none = bayrak GÖNDERİLMEZ (düşünmeyen modeller; 12B hattının davranışı)
    #   off  = enable_thinking=false  |  on = enable_thinking=true
    p.add_argument("--thinking", choices=("none", "off", "on"), default="none",
                   help="chat_template_kwargs.enable_thinking (yalnız HTTP taşıyıcı)")
    # ── Bütçeli düşünce (2026-07-29, CP0 / research_log #42) ────────────────────
    # Base M1/M2/M5'te `</think>`'i HİÇ kapatmıyor (32k token'da bile) → cevap üretilemiyor.
    # Kesilme değil SONLANMAMA; bütçe büyütmek çare değil. Bu bayrak modeli N token sonra
    # zorla kapatır → ölçüm üretilebilir hâle gelir. Bütçe ÖN-KAYITLI seçilir, sonuca göre
    # değiştirilmez; künyeye ve maliyet muhasebesine (ADR-0017) yazılır.
    p.add_argument("--think-budget", type=int, default=0, metavar="N",
                   help="N>0: düşünceye N token izin ver, kapatmazsa `</think>` yapıştırıp "
                        "cevabı --max-new-tokens ile ürettir (yalnız --thinking on + HTTP)")
    # ── Rakip tarafı düşünce bütçesi (2026-07-29, CP0.9 / ADR-0043 m.3) ─────────
    # Bütçe REJİM DEĞİŞMEZİ: "bütün özneler, bütün kollar, bütün rakipler aynı bütçeyle".
    # Bizim tarafta zorunlu kapatma gerekiyor (Qwen sonlanmıyor); rakip tarafta sunucu
    # bütçeyi kendi uyguluyor → OpenRouter `reasoning.max_tokens`. Aynı sayı, farklı
    # mekanizma; ikisi de künyeye `reasoning_tokens` olarak yazılır.
    p.add_argument("--reasoning-budget", type=int, default=0, metavar="N",
                   help="N>0: OpenRouter `reasoning.max_tokens=N` gönder ve toplam bütçeyi "
                        "N+--max-new-tokens yap (rakip tarafı; --think-budget'ın karşılığı)")
    p.add_argument("--sufficiency-preamble", action="store_true",
                   help="ABLASYON KOLU (2026-09-06'dan beri): sistem istemine 'önce kaynağın "
                        "soruyu cevaplayıp cevaplamadığını belirt' satırını ekle. "
                        "⚠️ ADR-0058 bunu ANA PROTOKOL yapmıştı; S14 kararıyla gerekçesi TERSİNE "
                        "DÖNDÜ ve ürünün varsayılanı BAYRAKSIZ (önsözsüz) oldu. Eski çıpa "
                        "kütle %%62,8 · A1 0,8229 — dedektör onarımı ÖNCESİ ve v1 soru seti "
                        "biriminde; bugünkü hiçbir sayıyla KIYASLANMAZ.")
    p.add_argument("--donmus-baglam", default="", metavar="DOSYA",
                   help="F0.16 / ADR-0097 m.6 — bağlamı retriever yerine `baglam_dondur.py`'nin "
                        "dosyasından oku (kiralık kartta retriever koşmaz). Dosyanın rejimi bu "
                        "koşununkiyle (soru dosyası, seed, n, k, rrf_k, kırpma) uyuşmazsa durur.")
    p.add_argument("--harness-no-gold", action="store_true",
                   help="ADR-0056 Karar 1 — `m2b`'nin harness-AÇIK karşılığı: retriever "
                        "k+1 getirir, ALTIN madde düşürülür, ilk k kalır. Bağlam uzunluğu "
                        "normal koşuyla AYNI. Yalnız --harness-indeks ile anlamlı.")
    p.add_argument("--no-gold", action="store_true",
                   help="M2 training-matched: --distractors ile gold'u ÇIKAR (sadece distractor, "
                        "RAG_MULTI prompt) → RAG-ıska abstention. v2b eğitim abstain dilimiyle AYNI mod.")
    return p.parse_args()


def norm(v):
    return "" if v is None else str(v).strip()


def load_madde_index(path):
    """(kanun_no|madde_no) → en dolu madde metni (score_grounded_corpus ile aynı mantık)."""
    idx = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            k = f"{norm(r.get('kanun_no'))}|{norm(r.get('madde_no'))}"
            t = (r.get("text") or "").strip()
            if t and len(t) > len(idx.get(k, "")):
                idx[k] = t
    return idx


def extract(rec):
    msgs = rec.get("messages", [])
    soru = next((m["content"] for m in msgs if m["role"] == "user"), None)
    return soru


def build_model(args):
    from unsloth import FastModel  # torch'tan ÖNCE
    import torch
    # Foundation rakip (Mecellem): düz transformers bf16. Unsloth 4-bit, Mecellem'in
    # UNTIED embed_tokens/lm_head'ini bozuyor (garbage "!!!!" çıktı) → 4B bf16 (~8GB, 12GB'a sığar).
    if getattr(args, "completion_fewshot", False):
        from transformers import AutoModelForCausalLM, AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(args.model)
        model = AutoModelForCausalLM.from_pretrained(
            args.model, torch_dtype=torch.bfloat16, device_map="cuda",
        )
        model.eval()
        # ⚠️ Mecellem checkpoint'i SIFIR bir lm_head taşıyor (std=0.0) + config tie=True →
        # transformers "ikisi farklı" deyip sıfır lm_head kullanıyor → garbage "!!!!".
        # Doğrusu: lm_head embed_tokens'a TIED olmalı → elle bağla (embed std=0.0245, sağlıklı).
        lm = model.get_output_embeddings().weight
        if lm.float().std().item() < 1e-6:
            model.get_output_embeddings().weight = model.get_input_embeddings().weight
            print("[gen-eval] ⚠️ sıfır lm_head tespit → embed_tokens'a TIED (Mecellem fix)")
        if tokenizer.pad_token_id is None:
            tokenizer.pad_token = tokenizer.eos_token
        print(f"[gen-eval] foundation bf16 yüklendi (transformers): {args.model}")
        return model, tokenizer
    model, tokenizer = FastModel.from_pretrained(
        model_name=args.model,
        max_seq_length=args.max_seq_len,
        load_in_4bit=True,
        full_finetuning=False,
    )
    if args.adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, args.adapter)
        print(f"[gen-eval] adapter yüklendi: {args.adapter}")
    FastModel.for_inference(model)
    return model, tokenizer


# ── COMPLETION-STYLE few-shot (C4 rakip baseline: Mecellem CPT/foundation, instruct DEĞİL) ──
# Mecellem-Qwen3-4B-TR chat-template'i güvenilir takip etmez (CPT ~270B token, instruction-tuned
# değil, roadmap §7·C4). ADİL kıyas = few-shot completion: 2 örnekle format öğret (biri atıflı-cevap,
# biri red), sonra gerçek KAYNAK+SORU ver, "CEVAP:" ile tamamlat. Örnekler elde-yazılı, eval'e
# sızmaz (genel maddeler). Skorlama AYNI (groundedness/score_abstention/score_correctness).
_FEWSHOT_RAG = (
    "Aşağıda, verilen KAYNAK metinlere dayanan Türk hukuku soru-cevap örnekleri vardır. "
    "Cevap YALNIZCA kaynağa dayanır; kaynakta bilgi yoksa reddedilir.\n\n"
    "KAYNAKLAR:\n[TÜRK BORÇLAR KANUNU Madde 146]\n"
    "Kanundan doğan alacaklar, aksine bir hüküm bulunmadıkça on yıllık zamanaşımına tabidir.\n"
    "SORU: Kanundan doğan alacaklarda genel zamanaşımı süresi ne kadardır?\n"
    "CEVAP: Sağlanan kaynağa göre kanundan doğan alacaklarda genel zamanaşımı süresi on yıldır "
    "(Türk Borçlar Kanunu, Madde 146).\n\n"
    "KAYNAKLAR:\n[TÜRK CEZA KANUNU Madde 125]\n"
    "Bir kimseye onur, şeref ve saygınlığını rencide edebilecek nitelikte fiil isnat eden kişi cezalandırılır.\n"
    "SORU: Yasal evlenme yaşı kaç yaşındır?\n"
    "CEVAP: Verilen kaynaklarda evlenme yaşına ilişkin bir düzenleme yer almamaktadır; "
    "bu konuda ilgili mevzuata başvurulması gerekir.\n\n"
)
_FEWSHOT_BLIND = (
    "Aşağıda Türk hukuku hakkında kısa soru-cevap örnekleri vardır. İlgili kanun ve madde belirtilir.\n\n"
    "SORU: Türk Medeni Kanunu'na göre kişilik ne zaman başlar?\n"
    "CEVAP: Kişilik, çocuğun sağ olarak tamamıyla doğduğu anda başlar (Türk Medeni Kanunu, Madde 28).\n\n"
    "SORU: Borçlar hukukunda genel zamanaşımı süresi kaç yıldır?\n"
    "CEVAP: Kanundan doğan alacaklarda genel zamanaşımı süresi on yıldır (Türk Borçlar Kanunu, Madde 146).\n\n"
)
_STOP_MARKERS = ("\nKAYNAKLAR:", "\nSORU:", "\nCEVAP:", "\n\n")


def generate_completion(model, tokenizer, soru, max_new_tokens, source=None, sources_block=None):
    """Completion-style few-shot üretim (chat-template YOK) — foundation rakip için."""
    if sources_block is not None:       # M1/M2b/M3
        ctx = f"KAYNAKLAR:\n{sources_block}\nSORU: {soru}\nCEVAP:"
        prompt = _FEWSHOT_RAG + ctx
    elif source:                        # M4/M2 tek kaynak
        ctx = f"KAYNAKLAR:\n{source[:3500]}\nSORU: {soru}\nCEVAP:"
        prompt = _FEWSHOT_RAG + ctx
    else:                               # M5 kör
        prompt = _FEWSHOT_BLIND + f"SORU: {soru}\nCEVAP:"
    import torch
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        out = model.generate(
            input_ids=inputs.input_ids, attention_mask=inputs.attention_mask,
            max_new_tokens=max_new_tokens, do_sample=False,
            temperature=None, top_p=None, top_k=None,
            pad_token_id=tokenizer.eos_token_id,
        )
    gen = tokenizer.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
    # İlk sınır işaretinde kes (model yeni Q&A üretmesin).
    cut = len(gen)
    for m in _STOP_MARKERS:
        j = gen.find(m)
        if j != -1:
            cut = min(cut, j)
    return gen[:cut].strip()


# ── ANA PROTOKOL: kaynak-yeterliliği önsözü (ADR-0058) ─────────────────────────
# Kökeni ABLASYON deneyiydi (2026-07-29, research_log #43 Bulgu 5); D1 ile benimsendi.
# Bütçeli düşünce M2'de tuzak reddini 0.633 → 0.814 çıkardı. İki mekanizma aday:
# (A) muhakeme kaynağı soruyla karşılaştırıyor · (B) zorunlu kapatma sonrası model kaynağın
# içeriğini SAYIP DÖKMÜŞ durumda, oradan doğal devam "kaynak bunu kapsamıyor" oluyor.
# CP0.9 ikisini ayıramadı (70 örneğin 69'u zorla kapatıldı → kendi duran kontrol grubu yok).
# Bu önsöz (B)'nin BİÇİM kısmını düşünce OLMADAN taklit eder: kazanç buradan geliyorsa aynı
# sonuç 1× token'la alınır (ADR-0017 maliyet ekseninde doğrudan kaldıraç).
# ✅ ADR-0058 (2026-08-06): ANA PROTOKOL yapılmıştı — çıpa kütle %62,8 · A1 0,8229.
# 🔄 TERSİNE DÖNDÜ (2026-09-06, açık soru S14): çekinme dedektörü onarılınca önsöz kütleyi
#    YÜKSELTMİYOR, DÜŞÜRÜYOR (önsözlü %68,4 ↔ önsözsüz %73,0 — v1 soru seti biriminde).
#    Ürünün varsayılanı artık ÖNSÖZSÜZ; bu bayrak ABLASYON kolunu üretir.
#    ⚠️ Eski satır SİLİNMEDİ, damgalandı. %62,8 dedektör onarımı ÖNCESİ sayıdır.
SUFFICIENCY_PREAMBLE = (
    "\nCevabına başlamadan ÖNCE, verilen kaynağın soruyu cevaplayıp cevaplamadığını "
    "tek cümleyle belirt. Kaynak soruyu cevaplamıyorsa bunu söyle ve cevap uydurma."
)


def build_messages(soru, source=None, sources_block=None, sufficiency=False):
    """Mod → (system, user) mesajları. Taşıyıcıdan (yerel/HTTP) BAĞIMSIZ — tek kaynak."""
    if sources_block is not None:  # M1/M3: çok-kaynak (distractor) veya boş bağlam
        sys = SYSTEM_PROMPT_RAG_MULTI
        user = f"KAYNAKLAR:\n{sources_block}\n\nSORU: {soru}"
    elif source:  # M4: tek gold kaynak
        sys = SYSTEM_PROMPT_RAG
        user = f"KAYNAK MADDE:\n{source[:3500]}\n\nSORU: {soru}"
    else:       # M5 kör mod: sadece soru (parametrik bilgi testi)
        sys = SYSTEM_PROMPT
        user = soru
    if sufficiency:
        sys = sys + SUFFICIENCY_PREAMBLE
    return [{"role": "system", "content": sys}, {"role": "user", "content": user}]


class GenOut(NamedTuple):
    """Tek üretimin künyesi. finish_reason/reasoning_len SESSİZ-BOZULMA kapısı için;
    completion_tokens maliyet-normalize parite muhasebesi için (ADR-0017)."""
    text: str
    finish_reason: str | None
    reasoning_len: int
    completion_tokens: int | None
    forced_close: bool = False
    # Sunucunun bildirdiği düşünce token'ı. Rakip (Gemini) izi METİN olarak vermiyor →
    # reasoning_len=0 gelir ama düşünce GERÇEKTEN harcanmıştır; karakter sayısıyla token
    # sayısını tek alanda karıştırmak sessiz-yanlışlık üretir, bu yüzden ayrı alan.
    reasoning_tokens: int | None = None


def render_prompt(server_url, messages, thinking):
    """llama-server /apply-template — şablonun ürettiği HAM istem.
    Zorunlu kapatmanın devam edeceği metin bu; sohbet API'si mid-mesaj devam ettiremez."""
    root = server_url.rstrip("/")
    if root.endswith("/v1"):
        root = root[:-3].rstrip("/")
    body = {"messages": messages}
    if thinking != "none":
        body["chat_template_kwargs"] = {"enable_thinking": thinking == "on"}
    req = urllib.request.Request(
        root + "/apply-template", data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["prompt"]


def _reasoning_tokens(resp):
    """`usage.completion_tokens_details.reasoning_tokens` — sunucu bildirirse (OpenRouter)."""
    det = getattr(getattr(resp, "usage", None), "completion_tokens_details", None)
    if det is None:
        return None
    if not isinstance(det, dict):
        det = getattr(det, "model_dump", dict)()
    return det.get("reasoning_tokens")


def generate_http(client, model_name, soru, max_new_tokens, source=None, sources_block=None,
                  thinking="none", think_budget=0, server_url=None, reasoning_budget=0,
                  sufficiency=False):
    """llama-server / OpenRouter üzerinden üretim (ADR-0025).

    Rakiplerle BİREBİR aynı kod yolu → adalet kuralı (spec §5.2) yapısal garanti.
    Deterministik: temperature=0, seed sabit.

    `think_budget > 0` → **BÜTÇELİ DÜŞÜNCE** (iki geçiş): model `think_budget` token içinde
    `</think>` kapatmazsa istemin sonuna izi + `</think>` yapıştırılır ve üretim `/completions`
    üzerinden sürdürülür — model o noktadan sonra cevabı yazmak ZORUNDA kalır.
    Neden gerekli: Qwen3.5-4B base'i M1/M2/M5'te hiç kapatmıyor (32k token'da bile), `content`
    boş dönüyor ve ölçüm ÜRETİLEMİYOR — kesilme değil, sonlanmama (research_log #42).
    """
    msgs = build_messages(soru, source, sources_block, sufficiency)
    extra = {}
    if thinking != "none":
        extra["chat_template_kwargs"] = {"enable_thinking": thinking == "on"}
    if reasoning_budget:
        # Rakip tarafı: bütçeyi sunucu uyguluyor, zorunlu kapatmaya gerek yok.
        # ⚠️ K2 (2026-08-06): OpenRouter bu ipucunu YOK SAYIYOR; tek bağlayıcı sınır max_tokens.
        # ⚠️ DÜZELTME (ADR-0070, 2026-09-06): buradaki eski şerh "bizde 1024|512 ayrı" diyordu —
        # ÖLÇÜLDÜ ve YANLIŞTI. Bizde de düşünce cevabın payını yiyordu; üstelik toplamımız
        # 1024 iken rakibinki 1536'ydı. Artık iki taraf da tek formülle 1536 alıyor.
        extra["reasoning"] = {"max_tokens": reasoning_budget}
    # ⚠️ GEÇİCİ SAĞLAYICI HATASI (2026-08-06, G2): OpenRouter/Google AI Studio bazen
    # HTTP **200** döner ama `finish_reason='error'` + BOŞ content verir. SDK'nın kendi
    # retry'ı (max_retries=8) bunu GÖRMEZ — HTTP katmanında hata yok. Sonuç: 80 kalemlik
    # ücretli bir koşu 22./32. kalemde ölüyordu (aynı koşu iki kez, FARKLI kalemde →
    # içeriğe bağlı değil, geçici).
    # §5 hata felsefesi: geçici altyapı hatası → GERİ-ÇEKİLMELİ RETRY. Deneme hakkı
    # tükenirse fonksiyon boş metni döndürür ve çağıranın "boş cevap → koşuyu durdur"
    # kapısı devreye girer — sessiz düşürme YOK, yanlış sayı YOK.
    # Ölçüm rejimi değişmez: aynı istem, aynı temperature=0, aynı seed.
    r = None
    for deneme in range(4):
        r = client.chat.completions.create(
            model=model_name,
            messages=msgs,
            # ADR-0070 (2026-09-06): TEK FORMÜL, rakiple birebir aynı.
            # Eskiden bizim kol `max_tokens=think_budget` (1024) alıyordu → model `</think>`'i
            # kendi kapatınca cevap 1024'ün KALANINA sığmak zorundaydı ve ayrı 512 payını
            # YALNIZ zorla kapatılanlar alıyordu. Ölçüldü: 75/80 kalemde tavan 1024, rakipte
            # 1536 (ve 36/80 · 18/80 kalemde 1024 fiilen AŞILMIŞ) → ADR-0043 §3'ün
            # "bütün rakipler aynı bütçeyle koşar" şartı TUTMUYORDU, sapma bizim aleyhimize.
            max_tokens=(reasoning_budget or think_budget or 0) + max_new_tokens,
            temperature=0.0,
            seed=3407,
            extra_body=extra or None,
        )
        _ch = r.choices[0]
        if _ch.finish_reason != "error" or (_ch.message.content or "").strip():
            break
        bekle = 2 ** deneme
        print(f"    ↻ sağlayıcı geçici hatası (finish_reason='error', boş içerik) — "
              f"{bekle}s sonra yeniden denenecek ({deneme + 1}/4)", flush=True)
        time.sleep(bekle)
    ch = r.choices[0]
    msg = ch.message
    # reasoning_content OpenAI şemasında yok; llama-server/OpenRouter ekliyor.
    reasoning = getattr(msg, "reasoning_content", None) or ""
    comp_tok = getattr(getattr(r, "usage", None), "completion_tokens", None) or 0
    text = (msg.content or "").strip()
    if text or not think_budget or not reasoning:
        return GenOut(text, ch.finish_reason, len(reasoning), comp_tok,
                      reasoning_tokens=_reasoning_tokens(r))

    # ── 2. geçiş: zorunlu kapatma ────────────────────────────────────────────
    prompt = render_prompt(server_url, msgs, thinking) + reasoning + "\n</think>\n\n"
    r2 = client.completions.create(
        model=model_name, prompt=prompt, max_tokens=max_new_tokens,
        temperature=0.0, seed=3407, stop=["<|im_end|>"],
    )
    c2 = r2.choices[0]
    tok2 = getattr(getattr(r2, "usage", None), "completion_tokens", None) or 0
    return GenOut(c2.text.strip(), c2.finish_reason, len(reasoning), comp_tok + tok2, True,
                  reasoning_tokens=_reasoning_tokens(r))


def generate(model, tokenizer, soru, max_new_tokens, source=None, sources_block=None,
             sufficiency=False):
    msgs = build_messages(soru, source, sources_block, sufficiency)
    inputs = tokenizer.apply_chat_template(
        msgs, tokenize=True, add_generation_prompt=True,
        return_tensors="pt",
    ).to(model.device)
    import torch
    with torch.no_grad():
        out = model.generate(
            input_ids=inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,            # deterministik — tekrar-üretilebilir eval
            temperature=None, top_p=None, top_k=None,
            pad_token_id=tokenizer.eos_token_id,
        )
    gen = out[0][inputs.shape[1]:]
    return tokenizer.decode(gen, skip_special_tokens=True).strip()


def main():
    a = parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    # 🚨 YARIŞ KAPISI: aynı label'a yazan ikinci bir üretim süreci varsa modeli yüklemeden dur.
    runlock.acquire(os.path.join(a.out_dir, f"{a.label}_detail.jsonl"), tag=f"gen {a.label}")

    donmus = None
    if a.donmus_baglam:
        if a.harness_indeks or a.distractors or a.with_source or a.empty_context or a.no_gold:
            raise SystemExit(
                "[gen-eval] 🚫 --donmus-baglam; --harness-indeks, --distractors, --with-source, "
                "--empty-context ve --no-gold ile birlikte verilemez — bağlam ya dosyadan ya canlı "
                "gelir, ikisi birden gelirse hangisinin kullanıldığı belirsizleşir")
        from baglam_dondur import Ayar, oku, sha256_dosya
        if a.rrf_k is None:
            from retriever import RRF_K
            a.rrf_k = RRF_K
        donmus = oku(a.donmus_baglam,
                     Ayar(seed=a.seed, n=a.n, harness_k=a.harness_k, rrf_k=a.rrf_k,
                          max_chunk_chars=a.max_chunk_chars, harness_no_gold=a.harness_no_gold),
                     veri_sha256=sha256_dosya(a.data))
        print(f"[gen-eval] DONMUŞ BAĞLAM · {a.donmus_baglam} · {len(donmus)} kalem · k={a.harness_k} · "
              f"rrf_k={a.rrf_k} · sha256 {donmus[0]['harness']['donmus_baglam']}", flush=True)

    _retriever = None
    if a.harness_indeks:
        # Veri kapısı model yüklenmeden ÖNCE (tuzak 6.2) — bayat/eksik indeks burada patlar.
        from retriever import RRF_K, Retriever
        _retriever = Retriever.yukle(a.harness_indeks)
        if a.rrf_k is None:
            a.rrf_k = RRF_K
        print(f"[gen-eval] HARNESS AÇIK · indeks={a.harness_indeks} · k={a.harness_k} · "
              f"rrf_k={a.rrf_k} · "
              f"model={_retriever._kunye['model']} · korpus n={_retriever._kunye['n']:,}",
              flush=True)

    if a.think_budget and not (a.thinking == "on" and a.server_url):
        raise SystemExit("[gen-eval] 🚫 --think-budget yalnız `--thinking on` + `--server-url` ile "
                         "anlamlı (zorunlu kapatma /apply-template + /completions gerektirir).")
    if a.reasoning_budget and not a.server_url:
        raise SystemExit("[gen-eval] 🚫 --reasoning-budget yalnız `--server-url` ile anlamlı "
                         "(sunucu-taraflı düşünce bütçesi).")
    if a.reasoning_budget and a.think_budget:
        raise SystemExit("[gen-eval] 🚫 --think-budget (istemci-taraflı zorunlu kapatma) ile "
                         "--reasoning-budget (sunucu-taraflı bütçe) aynı koşuda kullanılmaz: "
                         "iki farklı mekanizma, bütçe iki kez sayılır.")

    pool_recs = pool_by_kanun = None
    if donmus is not None:                      # örneklem dosyada; madde dosyası yüklenmez
        sample = [(k, k["soru"], k["referans"]) for k in donmus]
        print(f"[gen-eval] {a.label}: örneklem={len(sample)} (dondurulmuş) | adapter={a.adapter or '—'}")
    else:
        rows = [json.loads(l) for l in open(a.data, encoding="utf-8") if l.strip()]
        idx = load_madde_index(a.madde_path)

        # M1 distractor modu → ortak RAFT paketleyici (build_sft_v2b ile AYNI; ADR-0013).
        if a.distractors > 0:
            pool_recs, pool_by_kanun = raft_pack.load_madde_pool(a.madde_path)
            print(f"[gen-eval] distractor havuzu: {len(pool_recs)} madde "
                  f"({len(pool_by_kanun)} kanun) | k={a.distractors} hard-negative")

        sample, n_havuz = ornekle(rows, idx, a.seed, a.n)
        print(f"[gen-eval] {a.label}: havuz={n_havuz} (madde eşleşen) → örneklem={len(sample)} "
              f"| adapter={a.adapter or '—'}")

    # ADR-0025: --server-url verilirse yerel yükleme YOK — HTTP taşıyıcı.
    http_client = None
    if a.server_url:
        from openai import OpenAI
        # Timeout'ta oto-retry+backoff (llm_client ile aynı gerekçe): tek asılı istek koca
        # üretim koşusunu kırmasın. Ortamla ezilebilir (LLM_MAX_RETRIES / LLM_TIMEOUT_S).
        http_client = OpenAI(
            base_url=a.server_url, api_key=os.environ.get("OPENAI_API_KEY", "none"),
            max_retries=int(os.environ.get("LLM_MAX_RETRIES", "8")),
            timeout=float(os.environ.get("LLM_TIMEOUT_S", "120")))
        model, tokenizer = None, None
        print(f"[gen-eval] HTTP taşıyıcı: {a.server_url} (model={a.server_model})")
    else:
        if not a.model:
            raise SystemExit(
                "[gen-eval] 🚫 --model (veya BASE_MODEL env) ZORUNLU — yerel yükleme yolunda "
                "base gömülü değil. HTTP taşıyıcı için --server-url kullan (ADR-0025).")
        model, tokenizer = build_model(a)

    import random as _rnd
    n_truncated = n_forced = 0
    tok_sum = tok_n = rt_sum = rt_n = 0
    detail = os.path.join(a.out_dir, f"{a.label}_detail.jsonl")
    with part_ile_yaz(detail) as f:
        for i, (rec, soru, src) in enumerate(sample):
            # RAG-modu: kaynağı ETİKETLE (Kanun adı + Madde no) → model atıf no'sunu
            # uydurmasın, verilen etiketten kopyalasın (Faz 2 RAG: chunk atıf taşır).
            labeled_src = f"{rec.get('kanun_adi','')} {rec.get('madde_no','')}\n{src}"
            sources_block = None
            context_shown = ""
            mode = "blind"
            harness_izi = None
            if donmus is not None:                      # HARNESS AÇIK, bağlam dondurulmuş dosyadan
                sources_block, harness_izi = rec["sources_block"], rec["harness"]
                context_shown = sources_block
                mode = "harness"
            elif a.harness_indeks:                      # HARNESS AÇIK: bağlamı retriever seçer
                sources_block, harness_izi = harness_baglami(rec, soru, _retriever, a)
                context_shown = sources_block
                mode = "harness"
            elif a.empty_context:                       # M3 (E-set): hiç kaynak
                sources_block = "(İlgili kaynak bulunamadı.)"
                context_shown = ""
                mode = "empty"
            elif a.distractors > 0:                     # M1: gold+distractor · M2(no-gold): distractor-only
                rng = _rnd.Random(a.seed + i)           # örnek-başına deterministik
                chunks, _ = raft_pack.pack_context(
                    rec, src, pool_recs, pool_by_kanun, a.distractors, rng,
                    include_gold=not a.no_gold)         # --no-gold → gold ÇIKAR (M2 abstain, training-matched)
                sources_block = raft_pack.format_sources_block(chunks)
                if a.max_chunk_chars > 0:               # EVAL-MIRROR: eğitim clip'i (§5.1, ADR-0013)
                    # gold baş satırı = "{kanun_adi} {madde_no}" (labeled_chunk ile aynı _norm).
                    # ref cevap ##begin_quote## taşımaz (core_hard sade) → gold da baştan kırpılır;
                    # kritik olan context UZUNLUĞUNUN eğitimle eşleşmesi (v2b haksız uzun görmesin).
                    gold_label = f"{rec.get('kanun_adi','')} {rec.get('madde_no','')}"
                    ref_msgs = rec.get("messages") or []
                    ref_answer = next(
                        (m.get("content", "") for m in ref_msgs
                         if m.get("role") in ("assistant", "model")), "")
                    sources_block = clip_sources_block(
                        sources_block, ref_answer, gold_label, a.max_chunk_chars)
                context_shown = sources_block
                mode = "distractor_nogold" if a.no_gold else "distractor"
            elif a.with_source:                         # M4: tek gold
                context_shown = labeled_src
                mode = "oracle"

            src_arg = labeled_src if (a.with_source and not a.distractors and not a.empty_context) else None
            if http_client is not None:               # ADR-0025 HTTP taşıyıcı
                g = generate_http(
                    http_client, a.server_model, soru, a.max_new_tokens,
                    source=src_arg, sources_block=sources_block, thinking=a.thinking,
                    think_budget=a.think_budget, server_url=a.server_url,
                    reasoning_budget=a.reasoning_budget, sufficiency=a.sufficiency_preamble)
            else:
                gen_fn = generate_completion if a.completion_fewshot else generate
                g = GenOut(gen_fn(model, tokenizer, soru, a.max_new_tokens,
                                  source=src_arg, sources_block=sources_block), None, 0, None)
            cevap, finish_reason, reasoning_len, comp_tok = (
                g.text, g.finish_reason, g.reasoning_len, g.completion_tokens)
            if g.forced_close:
                n_forced += 1

            # 🚨 SESSİZ-BOZULMA KAPISI (research_log #39): boş cevap = hata değil, sessiz çöp.
            # Düşünen model bütçe içinde </think> kapatmazsa content='' gelir, HTTP 200 döner,
            # ve score_abstention.py o boş stringten SAYI ÜRETİR. Erken patla (ADR-0026 ruhu).
            if not cevap:
                raise SystemExit(
                    f"[gen-eval] 🚫 BOŞ cevap — örnek {i} ({mode}), finish_reason={finish_reason!r}, "
                    f"reasoning_content={reasoning_len} kar.\n"
                    + ("  → Model düşünce kanalını KAPATMADI. Bu bir düşünen model: "
                       "`--think-budget N` ile zorla kapat (ölçülebilir kip), `--thinking off` "
                       "ver, ya da --max-new-tokens büyüt.\n"
                       if reasoning_len else
                       "  → reasoning_content da boş; sunucu/şablon tarafına bak (diag_chat_template.sh).\n")
                    + "  Boş cevaplar üzerinde ÜRETİLEN HER SAYI GEÇERSİZDİR — koşu durduruldu.")

            out = {
                "id": i,
                "soru": soru,
                "referans": src,                       # GERÇEK gold madde = yer-gerçeği (groundedness/correctness)
                "context_shown": context_shown,        # modele GERÇEKTEN gösterilen bağlam (abstention için)
                "mode": mode,
                "cevap": cevap,
                "finish_reason": finish_reason,        # 'length' = kesilmiş cevap (kalite uyarısı)
                "reasoning_len": reasoning_len,        # >0 = düşünce kanalı kullanıldı
                "completion_tokens": comp_tok,         # düşünce DAHİL üretilen token (maliyet ekseni)
                "reasoning_tokens": g.reasoning_tokens,  # sunucu bildirdiyse: düşünceye giden pay
                "forced_close": g.forced_close,        # `</think>` bütçe dolunca ZORLA kapatıldı mı
                "kanun_adi": rec.get("kanun_adi"),
                "madde_no": rec.get("madde_no"),
                "kanun_no": rec.get("kanun_no"),
            }
            if harness_izi is not None:
                out["harness"] = harness_izi
            f.write(json.dumps(out, ensure_ascii=False) + "\n")
            if finish_reason == "length":
                n_truncated += 1
            if comp_tok:
                tok_sum += comp_tok
                tok_n += 1
            if g.reasoning_tokens is not None:
                rt_sum += g.reasoning_tokens
                rt_n += 1
            print(f"  [{i+1}/{len(sample)}] ({mode}) {rec.get('kanun_adi')} {rec.get('madde_no')} "
                  f"→ {len(cevap)} kar"
                  + (f"  ⚠️ KESİK ({finish_reason})" if finish_reason == "length" else ""))

    if n_truncated:
        pct = 100.0 * n_truncated / max(1, len(sample))
        print(f"[gen-eval] ⚠️ {n_truncated}/{len(sample)} (%{pct:.1f}) cevap max_new_tokens'a ÇARPTI "
              f"(finish_reason='length') — yarım cevaplar hakeme yarım gidiyor. "
              f"--max-new-tokens büyüt ya da sebebini kayda geç.")
    if tok_n:
        print(f"[gen-eval] completion_tokens: ort {tok_sum / tok_n:.1f}/cevap "
              f"(toplam {tok_sum}, n={tok_n}) — düşünce token'ı DAHİL (ADR-0017 maliyet ekseni)")
    if a.think_budget:
        print(f"[gen-eval] bütçeli düşünce: {n_forced}/{len(sample)} cevapta `</think>` ZORLA "
              f"kapatıldı (bütçe={a.think_budget} tok) — künyeye yazılır")
    if a.reasoning_budget:
        print(f"[gen-eval] rakip düşünce bütçesi: reasoning.max_tokens={a.reasoning_budget} "
              f"(toplam {a.reasoning_budget + a.max_new_tokens}) | ort reasoning_tokens "
              f"{rt_sum / max(1, rt_n):.1f}/cevap (bildirilen n={rt_n}/{len(sample)}) — künyeye yazılır")
    # Why: bayrak künyeye yazılmıyor — log'daki bu satır koşunun hangi kolda olduğunun
    # TEK izi. İki dalda da basılır ki ana protokol koşusu POZİTİF kanıt bıraksın.
    if a.sufficiency_preamble:
        print("[gen-eval] ⚠️ bu koşu ABLASYON kolu: kaynak-yeterliliği önsözü AÇIK — "
              "ADR-0058'in gerekçesi 2026-09-06'da TERSİNE DÖNDÜ (S14); ürünün varsayılan "
              "rejimi artık ÖNSÖZSÜZ, bu koşu ana tabloya girmez")
    else:
        print("[gen-eval] ✅ ANA PROTOKOL: kaynak-yeterliliği önsözü KAPALI — "
              "ürünün varsayılan rejimi budur (S14, 2026-09-06)")
    print(f"[gen-eval] taşıyıcı={'http' if http_client else 'yerel'} | thinking={a.thinking} "
          f"| max_new_tokens={a.max_new_tokens} | seed={a.seed}")
    print(f"[gen-eval] detay → {detail}")
    print(f"[gen-eval] sıradaki: python scripts/puanlama/groundedness.py "
          f"--details {detail} --label {a.label} --mode data")


if __name__ == "__main__":
    main()
