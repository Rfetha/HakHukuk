#!/usr/bin/env python3
"""Eğitim ortamı kilidi — betik başı kontrolü (F0.4, docs/EGITIM_ORTAMI.md §1).

NEDEN KODDA: kilit belgeye yazıldığında kapı değildi (ADR-0030 m.3, ADR-0078). Burada
`train_sft.py` / `train_orpo.py` model yüklenmeden önce `kilidi_uygula`yı çağırır; yaml'daki
(`configs/egitim_ortami.yaml`) her değer koşunun argümanları, verisi ve gerçek ortamıyla
karşılaştırılır. Uymayan her alan listelenir ve koşu para harcamadan durur. Geçerse künye
(`KUNYE.json`, EGITIM_ORTAMI §5) çıktı dizinine yazılır; her alan bir değişkenden ya da ölçümden
gelir (tuzak 1.12).

Bu modül torch/unsloth'u modül düzeyinde içe aktarmaz: kurallar GPU'suz test edilir.
"""
import datetime
import hashlib
import importlib.metadata as md
import json
import os
import subprocess
from dataclasses import dataclass

import yaml


@dataclass(frozen=True)
class OrtamKilidi:
    yol: str
    veri: dict

    @classmethod
    def yukle(cls, yol: str) -> "OrtamKilidi":
        with open(yol, encoding="utf-8") as f:
            return cls(yol=yol, veri=yaml.safe_load(f))


@dataclass(frozen=True)
class OrtamGozlemi:
    gpu_adi: str
    hesaplama_surumu: tuple
    surumler: dict          # paket → kurulu sürüm ya da None
    fla_hatasi: str         # boş = `from fla.modules import FusedRMSNormGated` çalıştı


def _yerel_eksiz(surum):
    return surum.split("+", 1)[0] if surum else surum


def tarif_ihlalleri(kilit: OrtamKilidi, tarif_adi: str, args) -> list:
    """Koşunun argümanları ↔ kilidin tarifi. `max_steps` ve `durdur_adim` serbesttir (duman ve
    eşdeğerlik koşuları), künyeye yazılır."""
    v, t, lora = kilit.veri, kilit.veri["tarifler"][tarif_adi], kilit.veri["lora"]
    karsilastir = [
        ("model", args.model, v["model"]),
        ("hassasiyet", args.hassasiyet, v["hassasiyet"]),
        ("veri", os.path.basename(args.data.rstrip("/")), t["veri"]),
        ("batch", args.batch, t["batch"]),
        ("grad_accum", args.grad_accum, t["grad_accum"]),
        ("lr", args.lr, t["lr"]),
        ("warmup_ratio", args.warmup_ratio, t["warmup_ratio"]),
        ("epochs", args.epochs, t["epochs"]),
        ("lora_r", args.lora_r, lora["r"]),
        ("lora_alpha", args.lora_alpha, lora["alpha"]),
        ("lora_dropout", args.lora_dropout, lora["dropout"]),
        ("target_modules", sorted(args.target_modules or []), sorted(lora["hedef_moduller"])),
    ]
    if tarif_adi == "sft":
        karsilastir += [
            ("max_seq_len", args.max_seq_len, t["max_seq_len"]),
            ("grad_checkpoint", not args.no_grad_checkpoint, t["grad_checkpoint"]),
            ("sistem_istemi", not args.no_system, t["sistem_istemi"]),
            ("user_part", args.user_part, v["tur_isaretleri"]["user_part"]),
            ("assistant_part", args.assistant_part, v["tur_isaretleri"]["assistant_part"]),
            ("allow_high_lr", args.allow_high_lr, False),
        ]
    else:
        karsilastir += [
            ("max_length", args.max_length, t["max_length"]),
            ("max_prompt_length", args.max_prompt_length, t["max_prompt_length"]),
            ("beta", args.beta, t["beta"]),
            ("taze_adaptor", bool(args.fresh_adapter) and not args.adapter, t["taze_adaptor"]),
        ]
    ihlal = [f"{ad}: koşu {gercek!r} ≠ kilit {beklenen!r}"
             for ad, gercek, beklenen in karsilastir if gercek != beklenen]
    if args.seed not in v["seedler"]:
        ihlal.append(f"seed: {args.seed} kilidin listesinde değil {v['seedler']}")
    return ihlal


def veri_ozeti(dizin: str) -> dict:
    """train/validation satır sayısı ve özeti — künyeye ve veri kontrolüne."""
    ozet = {"dizin": dizin}
    for bolum in ("train", "validation"):
        ham = open(os.path.join(dizin, f"{bolum}.jsonl"), "rb").read()
        ozet[bolum] = {"satir": sum(1 for l in ham.splitlines() if l.strip()),
                       "sha256": hashlib.sha256(ham).hexdigest()}
    return ozet


def veri_ihlalleri(kilit: OrtamKilidi, tarif_adi: str, ozet: dict) -> list:
    beklenen = kilit.veri["tarifler"][tarif_adi]["satir"]
    gercek = ozet["train"]["satir"]
    return [] if gercek == beklenen else [f"veri satir: train.jsonl {gercek} ≠ kilit {beklenen}"]


def ortam_ihlalleri(kilit: OrtamKilidi, g: OrtamGozlemi) -> list:
    gpu, paket = kilit.veri["gpu"], kilit.veri["paketler"]
    ihlal = []
    if not g.gpu_adi.startswith(gpu["ad_oneki"]) or list(g.hesaplama_surumu) != gpu["hesaplama_surumu"]:
        ihlal.append(f"GPU: {g.gpu_adi} (cc {tuple(g.hesaplama_surumu)}) ≠ kilit {gpu['ad_oneki']} "
                     f"cc {tuple(gpu['hesaplama_surumu'])} — Makale 1 kollarında başka mimari yasak")
    for p, s in {**paket["surumler"], **paket["ek"]}.items():
        if _yerel_eksiz(g.surumler.get(p)) != s:
            ihlal.append(f"{p}: kurulu {g.surumler.get(p)!r} ≠ kilit {s}")
    for p in paket["yasak"]:
        if g.surumler.get(p) is not None:
            ihlal.append(f"{p}: kurulu ({g.surumler[p]}) ama kilitte yasak")
    if g.fla_hatasi:
        ihlal.append(f"fla: `from fla.modules import FusedRMSNormGated` çalışmadı ({g.fla_hatasi}) — "
                     f"eksik fla-core, fla'nın hiç olmamasından kötü (ADR-0033)")
    return ihlal


def _surum(paket):
    try:
        return md.version(paket)
    except md.PackageNotFoundError:
        return None


def gozlemle(kilit: OrtamKilidi) -> OrtamGozlemi:
    """Gerçek ortamı okur. Why bu sırada: betik unsloth'u zaten içe aktarmış olmalı — fla
    transformers'ı çeker ve unsloth'tan önce gelirse yamaları uygulanmayabilir."""
    import torch
    paket = kilit.veri["paketler"]
    try:
        from fla.modules import FusedRMSNormGated  # noqa: F401
        fla_hatasi = ""
    except ImportError as e:
        fla_hatasi = f"{type(e).__name__}: {e}"
    return OrtamGozlemi(
        gpu_adi=torch.cuda.get_device_name(0),
        hesaplama_surumu=tuple(torch.cuda.get_device_capability(0)),
        surumler={p: _surum(p) for p in [*paket["surumler"], *paket["ek"], *paket["yasak"]]},
        fla_hatasi=fla_hatasi)


def _nvidia_smi():
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
                            "--format=csv,noheader"], capture_output=True, text=True, timeout=30)
        return r.stdout.strip() or f"BİLİNMİYOR (çıkış {r.returncode})"
    except (OSError, subprocess.TimeoutExpired) as e:
        return f"BİLİNMİYOR ({type(e).__name__})"


def kilidi_uygula(args, tarif_adi: str, cikti_dizini: str) -> dict:
    """Kontrolü koşturur; ihlal varsa SystemExit (model yüklenmeden). Geçerse künyeyi yazar."""
    import torch
    kilit = OrtamKilidi.yukle(args.ortam_kilidi)
    ozet = veri_ozeti(args.data)
    gozlem = gozlemle(kilit)
    ihlal = (tarif_ihlalleri(kilit, tarif_adi, args) + veri_ihlalleri(kilit, tarif_adi, ozet)
             + ortam_ihlalleri(kilit, gozlem))
    if ihlal:
        raise SystemExit(f"[kilit] 🚫 {len(ihlal)} alan eğitim ortamı kilidine uymuyor "
                         f"({kilit.yol}) — model yüklenmedi:\n  · " + "\n  · ".join(ihlal))
    kunye = {
        "tarih": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "durum": "basladi",
        "tarif": tarif_adi,
        "kilit": {"yol": kilit.yol, "sha256": hashlib.sha256(open(kilit.yol, "rb").read()).hexdigest()},
        "gpu": {"ad": gozlem.gpu_adi, "hesaplama_surumu": list(gozlem.hesaplama_surumu),
                "bellek_bayt": torch.cuda.get_device_properties(0).total_memory,
                "nvidia_smi": _nvidia_smi(), "cuda": torch.version.cuda},
        "paketler": {d.metadata["Name"]: d.version for d in md.distributions()},
        "kilit_dosyasi_sha256_kilitte": kilit.veri["paketler"]["kilit_sha256"],
        "fla_ice_aktarma": "çalıştı",
        "argumanlar": {k: v for k, v in vars(args).items()},
        "etkin_batch": args.batch * args.grad_accum,
        "veri": ozet,
        "platform": {k: v for k, v in os.environ.items() if k.startswith("MODAL_")
                     and not any(s in k for s in ("TOKEN", "SECRET", "KEY"))} or "yerel",
    }
    os.makedirs(cikti_dizini, exist_ok=True)
    with open(os.path.join(cikti_dizini, "KUNYE.json"), "w", encoding="utf-8") as f:
        json.dump(kunye, f, ensure_ascii=False, indent=2, default=str)
    print(f"[kilit] ✓ eğitim ortamı kilidi geçti ({kilit.yol}) → {cikti_dizini}/KUNYE.json", flush=True)
    return kunye


def kunye_tamamla(cikti_dizini: str, global_step: int, sure_s: float, ilk_adim: int) -> None:
    """Koşu bitince gerçekleşen adım sayısını, tepe VRAM'i ve adım süresini künyeye ekler.

    Why `ilk_adim`: kaldığı yerden devam eden koşuda süre yalnız bu oturumundur; adım başına süre
    de yalnız bu oturumun adımlarına bölünür, yoksa önceki oturumların adımları onu küçültürdü."""
    import torch
    yol = os.path.join(cikti_dizini, "KUNYE.json")
    kunye = json.load(open(yol, encoding="utf-8"))
    adim = global_step - ilk_adim
    kunye.update(durum="bitti", adim_gerceklesen=global_step,
                 bitis=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                 olcum={"tepe_vram_ayrilan_bayt": torch.cuda.max_memory_allocated(),
                        "tepe_vram_rezerve_bayt": torch.cuda.max_memory_reserved(),
                        "oturum_sure_s": round(sure_s, 1),
                        "oturum_adim": adim,
                        "s_adim": round(sure_s / adim, 3) if adim else None,
                        "kapsam": "tepe VRAM süreç başından (model yükleme dahil); süre yalnız bu "
                                  "oturumun trainer.train() çağrısı (ara değerlendirme dahil)"})
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(kunye, f, ensure_ascii=False, indent=2, default=str)
