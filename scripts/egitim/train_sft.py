#!/usr/bin/env python
"""
HakHukuk — QLoRA SFT eğitim script'i. **Base-agnostik.**

Unsloth QLoRA (NF4 4-bit) → Türk hukuku SLM. Tüm turlar aynı script; `--data` ile değişir.

⚠️ Base bir PARAMETRE, gömülü karar değil: `--model`, `--user-part`, `--assistant-part`
ve `--target-modules` zorunlu/ayarlanabilir. `--user-part`/`--assistant-part` render'a karşı
assert edilir (bkz aşağıdaki "SESSİZ-BOZULMA KAPISI").

Kullanım:
  python scripts/egitim/train_sft.py --model <hf-repo> --run-name r1 \
      --data data/train/<set> --epochs 1 \
      --user-part '<|turn>user\n' --assistant-part '<|turn>model\n'

Not: dar VRAM → batch=1 + gradient_checkpointing ZORUNLU.
"""
import argparse
import os
import time

# Unsloth, torch'tan ÖNCE import edilmeli (patch'leri uygular).
from unsloth import FastModel
from unsloth.chat_templates import train_on_responses_only

import torch
from datasets import load_dataset
from transformers.trainer_utils import get_last_checkpoint
from trl import SFTTrainer, SFTConfig

# TEKNIK_PLAN Adım 6 — her örneğe eklenen kimlik+davranış system prompt'u.
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

from hakhukuk.cekirdek.istem import SISTEM_KOR as SYSTEM_PROMPT
from ortam_kilidi import kilidi_uygula, kunye_tamamla, lora_hedefi, lora_yerlesim_kapisi, maske_kapisi, yukleme_secenekleri  # F0.4 — eğitim ortamı kilidi

def parse_args():
    p = argparse.ArgumentParser()
    # ⚠️ Default YOK (bilerek): yanlış base'e sessizce düşmek saatlerce süren bir koşuyu
    # çöpe çevirir. Base bir PARAMETRE, gömülü karar değil.
    p.add_argument("--model", required=True, help="HF repo id veya yerel yol")
    # ⚠️ Responses-only maskeleme sınırları — BASE'E GÖRE DEĞİŞİR ve yanlışsa SESSİZ BOZULUR:
    # maske hiç tutmaz, loss user/system tokenlarından da akar, eğitim gürültüye döner.
    # Bu yüzden default yok + aşağıda render'a karşı assert ediliyor.
    # (Örn. Gemma 4: `<|turn>user\n` / `<|turn>model\n` — eski Gemma'nın `<start_of_turn>`i DEĞİL.)
    p.add_argument("--user-part", required=True,
                   help=r"chat şablonundaki kullanıcı turu başlangıcı, ör. '<|turn>user\n'")
    p.add_argument("--assistant-part", required=True,
                   help=r"asistan turu başlangıcı, ör. '<|turn>model\n'")
    p.add_argument("--data", required=True,
                   help="train.jsonl + validation.jsonl içeren dizin (ör. data/train/raft)")
    p.add_argument("--run-name", default="v0")
    p.add_argument("--output-dir", default=None, help="varsayılan: outputs/<run-name>")
    p.add_argument("--max-seq-len", type=int, default=2048)
    p.add_argument("--epochs", type=float, default=2.0)
    p.add_argument("--batch", type=int, default=1)
    p.add_argument("--grad-accum", type=int, default=16)
    p.add_argument("--lr", type=float, default=2e-4)
    p.add_argument("--lora-r", type=int, default=16)
    p.add_argument("--lora-alpha", type=int, default=32)
    p.add_argument("--lora-dropout", type=float, default=0.05)
    # ⚠️ VARSAYILAN YOK — bilerek. Eski varsayılan (q/k/v/o + gate/up/down) Qwen3.5'in
    # 24 linear-attention katmanındaki `in_proj_*` projeksiyonlarını KAÇIRIYORDU ve bu
    # sessiz bir kayıptı: hata vermez, eğitim koşar, adaptasyonun bir kısmı hiç öğrenilmez.
    # ÖLÇÜLDÜ (τ_grounding, outputs/eval/tau_norm_tg.json): `in_proj_*` ‖τ‖'nin **%26.8'i**.
    # ADR-0026'nın kuralı: base bir parametredir, tanımsız kalırsa ERKEN patlamalı.
    p.add_argument("--target-modules", nargs="+", default=None,
                   help="ZORUNLU. LoRA takılacak lineer katmanlar — mimariye göre değişir, "
                        "varsayılanı YOK. Base'in modül adlarını doğrulamadan verme.")
    p.add_argument("--warmup-ratio", type=float, default=0.03,
                   help="warmup oranı (v2b reçete §5.1-C: %3-5; sweep'lenebilir)")
    p.add_argument("--seed", type=int, default=3407)
    p.add_argument("--no-system", action="store_true",
                   help="system prompt ekleme (ablation; v2b ZORUNLU — veri system'i zaten taşır)")
    p.add_argument("--allow-high-lr", action="store_true",
                   help="lr≥3e-4 kilidini aç (NORMALDE KULLANMA — v1 abstention çöküşü rejimi, §5.1-C)")
    # ⚠️ ADR-0031: BİRİNCİL precision = bf16 taban (donuk) + bf16 LoRA — QLoRA DEĞİL.
    # Merge iddiasının aleti (TIES/DARE ΔW üzerinde eleman-bazlı budama) NF4 kuantizasyon
    # gürültüsünden arınır. VARSAYILAN YOK (F0.4): eski `--bf16-base` bayrağı verilmeyince
    # koşu SESSİZCE NF4'e düşüyordu (EGITIM_ORTAMI §3).
    p.add_argument("--hassasiyet", required=True, choices=["bf16-taban", "nf4"],
                   help="bf16-taban = donuk bf16 taban + LoRA (ADR-0031 birincil) · nf4 = QLoRA")
    p.add_argument("--ortam-kilidi", required=True,
                   help="eğitim ortamı kilidi (configs/egitim_ortami.yaml); model yüklenmeden "
                        "önce argümanlar, veri ve ortam buna karşı denetlenir")
    # ⚠️ ADR-0033 (hız kaldıracı, YALNIZ geniş VRAM'de): gradient checkpointing aktivasyonları
    # yeniden hesaplayarak bellek kazanır — bedeli hesap gücü. Aşağıdaki varsayılan `"unsloth"`
    # YEREL 12 GB kart için konmuştu; A100-40GB'de bf16 4.57B ağırlık ~9.1 GB + LoRA gradyanı
    # 29.9M → ihtiyacımız olmayan bir tasarruf için hız ödüyoruz. ÖLÇÜM: CP4 smoke, 10.5 s/it
    # (checkpointing AÇIK) çıpasına karşı kıyaslanır.
    # 🚫 Yerel kartta (12 GB) BU BAYRAĞI KULLANMA — OOM.
    p.add_argument("--no-grad-checkpoint", action="store_true",
                   help="gradient checkpointing'i KAPAT (yalnız geniş VRAM: A100/H100). Yerelde OOM eder.")
    p.add_argument("--wandb", action="store_true", help="W&B'ye logla")
    p.add_argument("--max-steps", type=int, default=-1, help="smoke test için sınırla")
    return p.parse_args()


def _decode_marker(s: str) -> str:
    r"""Turn işareti CLI'dan literal '\n' (iki karakter) olarak gelebilir; render edilmiş
    şablonda ise GERÇEK newline var. Kaçış dizilerini çöz ki sessiz-bozulma assert'i doğru
    kıyaslasın. İşaretler saf ASCII kontrol token'ı (`<|im_start|>user\n`) → unicode_escape güvenli.
    Zaten gerçek newline gelirse de aynı sonuca iner (idempotent)."""
    import codecs
    return codecs.decode(s, "unicode_escape")


def _require_target_modules(target_modules):
    """ADR-0026: base bir parametredir; tanımsızsa ERKEN patla, sessizce varsayma.

    Why bu ayrı bir kapı: yanlış/eksik modül listesi exception ATMAZ — eğitim koşar,
    loss düşer, adaptörün bir kısmı hiç öğrenilmez. Ölçülen bedel: Qwen3.5-4B'de
    `in_proj_*` modülleri ‖τ‖'nin %26.8'ini taşıyor (outputs/eval/tau_norm_tg.json).
    """
    if target_modules:
        return
    raise SystemExit(
        "🚫 --target-modules ZORUNLU (varsayılanı yok — ADR-0026).\n"
        "   Base'in lineer projeksiyon adlarını doğrulayıp AÇIKÇA ver.\n"
        "   Qwen3.5-4B için (ölçüldü, 224 LoRA çifti):\n"
        "     --target-modules q_proj k_proj v_proj o_proj \\\n"
        "         in_proj_qkv in_proj_z in_proj_a in_proj_b \\\n"
        "         gate_proj up_proj down_proj\n"
        "   ⚠️ in_proj_* düşerse 24 linear-attention katmanı LoRA'sız kalır — HATA VERMEDEN."
    )


def main():
    args = parse_args()
    _require_target_modules(args.target_modules)
    args.user_part = _decode_marker(args.user_part)
    args.assistant_part = _decode_marker(args.assistant_part)
    out = args.output_dir or f"outputs/{args.run_name}"

    # 🚫 GÜVENLİK KİLİDİ (v2b reçete §5.1-C): 3e-4 re-warming = v1 abstention çöküşü rejimi
    # (continual-PRETRAINING reçetesi, 2403.08763/2503.02844). Davranışsal SFT'de YASAK.
    if args.lr >= 3e-4 and not args.allow_high_lr:
        raise SystemExit(
            f"[train] 🚫 lr={args.lr} ≥ 3e-4 = v1 abstention-çöküşü rejimi (§5.1-C). "
            f"Davranışsal SFT için lr≈1e-4 (LoRA, full-FT'nin 10x'i) kullan. "
            f"Bilerek istiyorsan --allow-high-lr ekle.")
    os.environ["WANDB_PROJECT"] = "hakhukuk-sft"
    report_to = "wandb" if args.wandb else "none"

    # 🚫 VERİ KAPISI — model YÜKLENMEDEN ÖNCE. Bu denetim eskiden `load_dataset` sırasında,
    # yani ~10 dakikalık model indirme/yüklemesinden SONRA patlıyordu; Modal'da bu doğrudan
    # yanlış yazılmış bir yol için A100 dakikası demek (2026-07-25 CP4'te bir kez yaşandı:
    # `--data /raft_scrubbed` verildi, oysa volume konteynerde `/data`'ya bağlı → `/data/raft_scrubbed`).
    # Ucuz denetim önce: saniyede patla, saatte değil.
    data_files = {"train": os.path.join(args.data, "train.jsonl"),
                  "validation": os.path.join(args.data, "validation.jsonl")}
    missing = [p for p in data_files.values() if not os.path.isfile(p)]
    if missing:
        parent = os.path.dirname(args.data.rstrip("/")) or "/"
        try:
            komsu = sorted(os.listdir(parent))[:20]
        except OSError:
            komsu = ["(üst dizin okunamadı)"]
        raise SystemExit(
            f"[train] 🚫 VERİ BULUNAMADI: {', '.join(missing)}\n"
            f"  --data={args.data!r}\n"
            f"  ⚠️ Modal'da volume yolu ≠ konteyner yolu: `hukuk-data` **/data**'ya bağlanır,\n"
            f"     yani volume'deki /<set> konteynerde **/data/<set>** olur.\n"
            f"  {parent!r} içeriği: {komsu}")

    # 🚫 EĞİTİM ORTAMI KİLİDİ (F0.4) — model YÜKLENMEDEN: argüman · veri · GPU · paket sürümü.
    kilidi_uygula(args, "sft", out)

    # --- Model + tokenizer ---
    bf16_taban = args.hassasiyet == "bf16-taban"
    print(f"[train] precision = {'bf16 taban + LoRA (ADR-0031 birincil)' if bf16_taban else 'QLoRA NF4 4-bit'}")
    model, tokenizer = FastModel.from_pretrained(
        model_name=args.model,
        max_seq_length=args.max_seq_len,
        load_in_4bit=not bf16_taban,
        dtype=torch.bfloat16 if bf16_taban else None,
        full_finetuning=False,
        **yukleme_secenekleri(args),
    )

    # --- LoRA adapter ---
    model = FastModel.get_peft_model(
        model,
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        # ⚠️ Mimariye bağlı: bu isimler base'in lineer projeksiyonlarıyla eşleşmeli.
        # Farklı mimaride (MoE, linear-attention) tutmaz → "0 LoRA takıldı" veya exception.
        target_modules=lora_hedefi(args.target_modules),
        bias="none",
        # "unsloth" = 12 GB yerel kart için zorunlu; A100/H100'de --no-grad-checkpoint ile kapatılır
        # (ADR-0033). Kapatma kararı ÖLÇÜLÜR, varsayılmaz: smoke s/it çıpasıyla kıyasla.
        use_gradient_checkpointing=False if args.no_grad_checkpoint else "unsloth",
        random_state=args.seed,
    )
    lora_yerlesim_kapisi(model, args, out)
    print(f"[train] gradient_checkpointing = "
          f"{'KAPALI (ADR-0033 hız kaldıracı — geniş VRAM)' if args.no_grad_checkpoint else 'unsloth (bellek tasarrufu)'}"
          f" | lora_dropout = {args.lora_dropout}"
          # Etkin batch REÇETE SABİTİ (16). batch/grad_accum ayrı ayrı değişebilir ama çarpımları
          # değişirse öğrenme rejimi kayar ve bu HİÇBİR YERDE hata vermez → gözle denetlenebilsin.
          f" | etkin batch = {args.batch}×{args.grad_accum} = {args.batch * args.grad_accum}")

    # --- Veri: messages → Gemma chat-template metni ---
    def to_text(example):
        msgs = example["messages"]
        if not args.no_system:
            msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + msgs
        text = tokenizer.apply_chat_template(
            msgs, tokenize=False, add_generation_prompt=False,
        )
        return {"text": text}

    ds = load_dataset("json", data_files=data_files)   # yollar yukarıda doğrulandı
    ds = ds.map(to_text, remove_columns=[c for c in ds["train"].column_names])

    # 🚨 SESSİZ-BOZULMA KAPISI: maske sınırları render'da GERÇEKTEN var mı?
    # Yoksa train_on_responses_only hiçbir şeyi maskelemez, loss tüm diziden akar ve
    # eğitim sessizce bozulur — hata da vermez. Yeni base'de İLK kırılan yer burasıdır.
    sample = ds["train"][0]["text"]
    for name, part in (("--user-part", args.user_part),
                       ("--assistant-part", args.assistant_part)):
        if part not in sample:
            raise SystemExit(
                f"[train] 🚫 {name}={part!r} render edilmiş şablonda BULUNAMADI.\n"
                f"  Bu base'in chat şablonu farklı turn işareti kullanıyor demektir.\n"
                f"  Maskeleme sessizce çalışmaz → eğitim çöpe gider. Render örneği (ilk 300 char):\n"
                f"  {sample[:300]!r}")
    print(f"[train] ✓ maske sınırları render'da doğrulandı "
          f"({args.user_part!r} / {args.assistant_part!r})")

    # --- Trainer ---
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=ds["train"],
        eval_dataset=ds["validation"],
        args=SFTConfig(
            dataset_text_field="text",
            max_seq_length=args.max_seq_len,
            per_device_train_batch_size=args.batch,
            gradient_accumulation_steps=args.grad_accum,
            warmup_ratio=args.warmup_ratio,
            num_train_epochs=args.epochs,
            max_steps=args.max_steps,
            learning_rate=args.lr,
            lr_scheduler_type="cosine",
            optim="adamw_8bit",
            bf16=True,
            logging_steps=10,
            # Ara checkpoint: kesintide sıfırdan değil son checkpoint'ten devam (resume).
            # (save_strategy="epoch" idi → epoch bitmeden hiç checkpoint yoktu = kesinti = tam kayıp.)
            save_strategy="steps",
            save_steps=200,
            save_total_limit=3,
            eval_strategy="epoch",
            output_dir=out,
            seed=args.seed,
            report_to=report_to,
            run_name=f"hakhukuk-{args.run_name}",
        ),
    )

    # Sadece model cevabından loss (user/system tokenları maskelenir).
    trainer = train_on_responses_only(
        trainer,
        instruction_part=args.user_part,
        response_part=args.assistant_part,
    )
    maske_kapisi(trainer.train_dataset, tokenizer, args, out)

    # Otomatik resume: out'ta checkpoint varsa kaldığı yerden, yoksa baştan (idempotent).
    ckpt = get_last_checkpoint(out) if os.path.isdir(out) else None
    if ckpt:
        print(f"[train] RESUME → {ckpt} (kaldığı yerden devam)")
    print(f"[train] GPU: {torch.cuda.get_device_name(0)} | "
          f"adapter r={args.lora_r} | data={args.data} | out={out} | resume={bool(ckpt)}")
    ilk_adim = int(ckpt.rsplit("-", 1)[-1]) if ckpt else 0   # checkpoint-<adım>
    t0 = time.perf_counter()
    trainer.train(resume_from_checkpoint=ckpt)
    sure_s = time.perf_counter() - t0
    trainer.save_state()            # Why: kayıp geçmişi (eşdeğerlik kıyası) çıktı dizininde kalsın
    kunye_tamamla(out, trainer.state.global_step, sure_s, ilk_adim)

    # --- Adapter kaydet ---
    model.save_pretrained(out)
    tokenizer.save_pretrained(out)
    print(f"[train] bitti → adapter: {out}")


if __name__ == "__main__":
    main()
