#!/usr/bin/env python
"""v3 ADIM 6b — ORPO eğitim (MaskedORPOTrainer): near-miss abstention fix (v3_recipe).

Unsloth FastModel + TRL 0.24 ORPOTrainer subclass.

⚠️ BAYAT SATIR DÜZELTİLDİ (2026-09-06). Eskiden burada *"base = v2b ADAPTER'dan DEVAM
(grounding taşınır)"* yazıyordu; bu, 12B hattının v3 reçetesiydi ve BUGÜNKÜ KURALA AYKIRIDIR.
Bugün her kol HAM BASE'den bağımsız eğitilir (ADR-0027): task-vector tanımı `τ = θ_ft − θ_base`
tek bir θ_base şart koşar. `--adapter` yolu ARDIŞIK SFT üretir, task-vector DEĞİL.
Yürürlükteki artefakt `τ_a v1` **`--fresh-adapter`** ile ham base'den koştu
(`docs/record/kollar.md`:64). `--adapter` yolu yalnız 12B-hattı yeniden üretimi için durur.
MaskedORPOTrainer: her satır `is_pref` taşır → grounding-replay satırında (is_pref=0) OR-terimi
NaN-safe SIFIRLANIR (torch.where), yalnız NLL(chosen) akar = SFT-replay. abstain-çiftinde (is_pref=1)
tam ORPO. Kaynak-doğrulandı: trl/trainer/orpo_trainer.py 0.24.0 (loss=policy_nll_loss−losses.mean()
satır 830; odds_ratio_loss per-örnek `losses` satır 675; is_pref collator else-dalında list, satır 79).

⚠️ ADIM 7 Modal smoke DOĞRULAYACAK: (a) v2b-continuation (PeftModel is_trainable) Unsloth'la çalışıyor mu,
(b) is_pref batch'te list olarak geliyor mu, (c) OOM/loss. Offline sadece syntax + tasarım doğru.

Kullanım (Modal):
  modal run scripts/egitim/modal_train.py::spawn_v3 --smoke      # önce ~50 step (para-kapısı)
  modal run scripts/egitim/modal_train.py::spawn_v3 --run-name v3 --epochs 1
"""
import argparse
import os

# Unsloth ÖNCE (patch'ler). PatchDPOTrainer → TRL DPO/ORPO trainer'larını Unsloth'a uyarlar.
from unsloth import FastModel, PatchDPOTrainer
PatchDPOTrainer()

import torch
from datasets import load_dataset
from transformers.trainer_utils import get_last_checkpoint
from transformers import TrainerCallback
from trl import ORPOTrainer, ORPOConfig

from ortam_kilidi import kilidi_uygula, kunye_tamamla  # F0.4 — eğitim ortamı kilidi (aynı dizin)


class _AdimdaDur(TrainerCallback):
    """`--durdur-adim N`: N. adımda durur; takvim (warmup + cosine) tam koşuya göre kurulu kalır.
    Why `max_steps` değil: max_steps takvimi N adıma sıkıştırır ve kayıp ta_v1'inkiyle
    (70 adımlık takvim) adım adım kıyaslanamaz olur."""

    def __init__(self, adim):
        self.adim = adim

    def on_step_end(self, args, state, control, **kwargs):
        if state.global_step >= self.adim:
            control.should_training_stop = True
        return control


class MaskedORPOTrainer(ORPOTrainer):
    """Per-satır is_pref maskesi: is_pref=0 (grounding-replay) → OR-terimi sıfırlanır (NaN-safe),
    yalnız NLL(chosen) = SFT-replay. TRL 0.24 get_batch_loss_metrics'in OR-agregasyonu değiştirilmiş
    kopyası (loss = policy_nll_loss − maskeli_mean(losses))."""

    def get_batch_loss_metrics(self, model, batch, train_eval="train"):
        metrics = {}
        # is_pref collator else-dalında list olarak gelir; concatenated_forward'a girmeden ÇIKAR.
        is_pref_raw = batch.pop("is_pref", None)

        forward_output = self.concatenated_forward(model, batch)
        (policy_chosen_logps, policy_rejected_logps, policy_chosen_logits,
         policy_rejected_logits, policy_nll_loss) = forward_output[:5]
        if self.aux_loss_enabled:
            aux_loss = forward_output[5]

        losses, chosen_rewards, rejected_rewards, log_odds_ratio, log_odds_chosen = self.odds_ratio_loss(
            policy_chosen_logps, policy_rejected_logps
        )

        # --- MASKELİ OR-AGREGASYON (NaN-safe) ---
        if is_pref_raw is not None:
            is_pref = torch.as_tensor([bool(x) for x in is_pref_raw],
                                      device=losses.device, dtype=torch.bool)
            # ⚠️ losses*mask DEĞİL: OR-loss log1p(-exp(...)) NaN üretebilir, nan*0=nan zehirler.
            # torch.where seçilmeyen daldan NaN taşımaz.
            losses = torch.where(is_pref, losses, torch.zeros_like(losses))
            or_term = losses.sum() / is_pref.sum().clamp(min=1)
        else:
            or_term = losses.mean()

        loss = policy_nll_loss - or_term        # tam ORPO loss (maskeli OR)

        reward_accuracies = (chosen_rewards > rejected_rewards).float()
        prefix = "eval_" if train_eval == "eval" else ""
        g = self.accelerator.gather_for_metrics
        metrics[f"{prefix}rewards/chosen"] = g(chosen_rewards).mean()
        metrics[f"{prefix}rewards/rejected"] = g(rejected_rewards).mean()
        metrics[f"{prefix}rewards/accuracies"] = g(reward_accuracies).mean()
        metrics[f"{prefix}rewards/margins"] = g(chosen_rewards - rejected_rewards).mean()
        metrics[f"{prefix}logps/rejected"] = g(policy_rejected_logps).detach().mean()
        metrics[f"{prefix}logps/chosen"] = g(policy_chosen_logps).detach().mean()
        metrics[f"{prefix}logits/rejected"] = g(policy_rejected_logits.detach().mean()).mean()
        metrics[f"{prefix}logits/chosen"] = g(policy_chosen_logits.detach().mean()).mean()
        # forget-vekili: grounding NLL trendi M1-risk göstergesi (v3_recipe ADIM 8).
        metrics[f"{prefix}nll_loss"] = g(policy_nll_loss).detach().mean()
        metrics[f"{prefix}log_odds_ratio"] = g(log_odds_ratio).detach().mean()
        metrics[f"{prefix}log_odds_chosen"] = g(log_odds_chosen).detach().mean()
        for k, v in metrics.items():
            metrics[k] = v.item()
        if self.aux_loss_enabled:
            loss += self.aux_loss_coef * aux_loss
        return loss, metrics


def parse_args():
    p = argparse.ArgumentParser()
    # ⚠️ Default YOK (bilerek) — yanlış base'e sessizce düşmek koşuyu çöpe çevirir.
    p.add_argument("--model", required=True, help="HF repo id veya yerel yol")
    p.add_argument("--adapter", default=None,
                   help="DEVAM edilecek adapter (önceki turun kazanımı taşınır). "
                        "Yoksa --fresh-adapter ile base'e taze adapter.")
    p.add_argument("--data", required=True, help="train.jsonl + validation.jsonl içeren dizin")
    p.add_argument("--run-name", default="v3")
    p.add_argument("--output-dir", default=None)
    p.add_argument("--beta", type=float, default=0.1, help="ORPO OR ceza ağırlığı (recipe λ; {0.05,0.1,0.25})")
    p.add_argument("--lr", type=float, default=1e-5, help="v2b'den devam → düşük (5e-6–1e-5)")
    p.add_argument("--epochs", type=float, default=1.0)
    p.add_argument("--batch", type=int, default=1)
    p.add_argument("--grad-accum", type=int, default=64, help="per_device×grad_accum≥64 (OR-sinyali stabil)")
    # ⚠️ ÖLÇÜLDÜ (2026-07-28, n=1741): eski 1536/1152 ayarında prompt'ların **%4.4'ü** ve
    # prompt+chosen'ın %2'si sessizce kırpılıyordu (ort 406 tok ama p95 1120, max 1703).
    # Yeni değerler kırpmayı ~%0'a indiriyor VE τ_grounding'in 2048 tavanına oturuyor
    # (rejim eşleşmesi — docs/open_questions.md #13).
    p.add_argument("--max-length", type=int, default=2048)
    p.add_argument("--max-prompt-length", type=int, default=1536)
    p.add_argument("--warmup-ratio", type=float, default=0.05)
    p.add_argument("--lora-r", type=int, default=16)
    p.add_argument("--lora-alpha", type=int, default=32)
    p.add_argument("--seed", type=int, default=3407)
    p.add_argument("--max-steps", type=int, default=-1, help="smoke için sınırla")
    p.add_argument("--save-steps", type=int, default=100,
                   help="checkpoint aralığı; 2-epoch koşuda ~1-epoch ara-checkpoint için düşür (ör. 28)")
    # ⚠️ VARSAYILAN YOK — train_sft.py ile aynı gerekçe (rejim eşleşmesi, #13).
    # Eski varsayılan `in_proj_*`'ı kaçırıyordu; ölçüldü: ‖τ‖'nin %26.8'i orada.
    p.add_argument("--target-modules", nargs="+", default=None,
                   help="ZORUNLU (--fresh-adapter yolunda). Mimariye göre değişir, varsayılanı YOK.")
    p.add_argument("--fresh-adapter", action="store_true",
                   help="continuation yerine base'e YENİ adapter (önceki turun kazanımını kaybeder)")
    # ⚠️ Aşağıdaki iki bayrak `train_sft.py` ile REJİM EŞLEŞMESİ içindir, stil tercihi değil:
    # τ_g ve τ_a merge edilecekse ikisi de AYNI θ_base'den ve aynı LoRA rejiminden türemeli
    # (task-vector tanımı ortak base şart koşar). Eskiden ikisi de burada sabit kodluydu ve
    # sessizce `train_sft.py`'den ayrışıyordu — sayı üretir, sayı kıyaslanamaz olurdu.
    p.add_argument("--hassasiyet", required=True, choices=["bf16-taban", "nf4"],
                   help="bf16-taban = donuk bf16 taban + LoRA (ADR-0031) · nf4 = QLoRA. VARSAYILAN YOK (F0.4)")
    p.add_argument("--ortam-kilidi", required=True,
                   help="eğitim ortamı kilidi (configs/egitim_ortami.yaml); model yüklenmeden önce denetlenir")
    p.add_argument("--durdur-adim", type=int, default=None,
                   help="eğitimi bu adımda kes ama öğrenme oranı takvimini TAM koşuya göre kur "
                        "(eşdeğerlik koşusu: ta_v1'in 70 adımlık takviminin ilk N adımı)")
    p.add_argument("--lora-dropout", type=float, default=0.05,
                   help="ADR-0033 `dropout=0`'ı REDDETTİ (yan-hasar ölçümünde atfedilebilirliği bozar). "
                        "train_sft.py ile aynı tutulur.")
    return p.parse_args()


def main():
    args = parse_args()
    # ⚠️ Yalnız fresh-adapter yolunda gerekli: continuation'da LoRA yapısı adaptörden gelir.
    if (args.fresh_adapter or not args.adapter) and not args.target_modules:
        raise SystemExit(
            "🚫 --target-modules ZORUNLU (fresh-adapter yolunda, varsayılanı yok — ADR-0026).\n"
            "   τ_g ile MERGE edilebilmesi için liste onunkiyle AYNI olmalı (open_questions #13).\n"
            "   Qwen3.5-4B: q_proj k_proj v_proj o_proj in_proj_qkv in_proj_z in_proj_a "
            "in_proj_b gate_proj up_proj down_proj\n"
            "   ⚠️ in_proj_* düşerse 24 linear-attention katmanı LoRA'sız kalır — HATA VERMEDEN."
        )
    out = args.output_dir or f"outputs/{args.run_name}"

    # 🚫 VERİ KAPISI — model YÜKLENMEDEN ÖNCE (train_sft.py ile aynı kalıp).
    # Why: `--data` bir DİZİN bekler (train.jsonl + validation.jsonl). Dosya yolu verilirse
    # `load_dataset` `<dosya>/train.jsonl` arar ve patlar — ama bu, model A100'e yüklendikten
    # SONRA olur, yani boşa GPU dakikası. Ölçüldü (2026-07-30, CP2-s): bir smoke koşusu tam
    # böyle kaybedildi. Kapı burada, yükleme öncesi.
    data_files = {"train": os.path.join(args.data, "train.jsonl"),
                  "validation": os.path.join(args.data, "validation.jsonl")}
    missing = [p for p in data_files.values() if not os.path.isfile(p)]
    if missing:
        raise SystemExit(
            f"🚫 --data bir DİZİN olmalı (train.jsonl + validation.jsonl içeren).\n"
            f"   verilen: {args.data}\n   bulunamayan: {missing}")

    # 🚫 EĞİTİM ORTAMI KİLİDİ (F0.4) — model YÜKLENMEDEN: argüman · veri · GPU · paket sürümü.
    kilidi_uygula(args, "orpo", out)

    bf16_taban = args.hassasiyet == "bf16-taban"
    print(f"[orpo] precision = {'bf16 taban + LoRA (ADR-0031 birincil)' if bf16_taban else 'QLoRA NF4 4-bit'}"
          f" | lora_dropout = {args.lora_dropout}", flush=True)

    model, tokenizer = FastModel.from_pretrained(
        model_name=args.model, max_seq_length=args.max_length,
        load_in_4bit=not bf16_taban,
        dtype=torch.bfloat16 if bf16_taban else None,
        full_finetuning=False,
    )

    if args.fresh_adapter or not args.adapter:
        # Base'e yeni adapter — önceki turun kazanımı (grounding) TAŞINMAZ.
        model = FastModel.get_peft_model(
            model, r=args.lora_r, lora_alpha=args.lora_alpha, lora_dropout=args.lora_dropout,
            target_modules=args.target_modules,
            bias="none", use_gradient_checkpointing="unsloth", random_state=args.seed,
        )
        print("[orpo] ⚠️ FRESH adapter (base'den) — önceki turun kazanımı taşınmadı", flush=True)
    else:
        # CONTINUATION: önceki turun LoRA'sını trainable yükle (kazanım taşınır).
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, args.adapter, is_trainable=True)
        print(f"[orpo] continuation: {args.adapter} (is_trainable) — kazanım taşındı", flush=True)

    data_files = {"train": os.path.join(args.data, "train.jsonl"),
                  "validation": os.path.join(args.data, "validation.jsonl")}
    ds = load_dataset("json", data_files=data_files)

    cfg = ORPOConfig(
        beta=args.beta,
        max_length=args.max_length,
        max_prompt_length=args.max_prompt_length,
        per_device_train_batch_size=args.batch,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        num_train_epochs=args.epochs,
        max_steps=args.max_steps,
        warmup_ratio=args.warmup_ratio,
        lr_scheduler_type="cosine",
        optim="adamw_8bit",
        bf16=True,
        logging_steps=5,
        save_strategy="steps",
        save_steps=args.save_steps,
        save_total_limit=3,
        eval_strategy="steps" if args.max_steps < 0 else "no",
        eval_steps=100,
        output_dir=out,
        seed=args.seed,
        report_to="none",
        remove_unused_columns=False,      # is_pref sütunu KORUNSUN (ORPO zaten False set eder)
    )

    trainer = MaskedORPOTrainer(
        model=model,
        args=cfg,
        train_dataset=ds["train"],
        eval_dataset=ds["validation"],
        processing_class=tokenizer,
        callbacks=[_AdimdaDur(args.durdur_adim)] if args.durdur_adim else None,
    )

    ckpt = get_last_checkpoint(out) if os.path.isdir(out) else None
    if ckpt:
        print(f"[orpo] RESUME → {ckpt}", flush=True)
    print(f"[orpo] GPU={torch.cuda.get_device_name(0)} | beta={args.beta} lr={args.lr} "
          f"grad_accum={args.grad_accum} | data={args.data} | out={out}", flush=True)
    trainer.train(resume_from_checkpoint=ckpt)
    trainer.save_state()            # Why: kayıp geçmişi (eşdeğerlik kıyası) çıktı dizininde kalsın
    kunye_tamamla(out, trainer.state.global_step)

    model.save_pretrained(out)
    tokenizer.save_pretrained(out)
    print(f"[orpo] bitti → adapter: {out}", flush=True)


if __name__ == "__main__":
    main()
