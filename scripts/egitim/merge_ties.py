#!/usr/bin/env python3
"""Norm-dengeli **k-yollu eşzamanlı** TIES merge (ADR-0027 · ADR-0036).

Sprint 3'ün 8 kafes hücresi ve ARA KAPI'nın 2. gözlemi (ADR-0045 merge onarım kontrolü) bu
betiğin üstünde duruyor.

## Neden `merge_lora.py` yetmiyor

O betik **tek** adaptörü base'e katıyor. TIES üç şeyi **bütün vektörler üzerinde birden** yapar:
kırpma (trim) → işaret seçimi (sign election) → ayrık ortalama (disjoint mean). Bu yüzden
`TIES(TIES(τg,τa),τr) ≠ TIES(τg,τa,τr)` — iteratif uygulamak farklı bir operatördür.

## Neden norm-dengeleme (ADR-0036)

Kollar çok farklı ölçekte eğitiliyor (`τ_g` 1.083 adım @1e-4 · `τ_a` ~73 adım @1e-5). TIES'in
işaret seçimi ve ayrık ortalaması **kütle-ağırlıklı**: normalize edilmezse küçük-normlu kol tam
da becerilerin **gerçekten çakıştığı** parametrelerde silinir — ve *"abstention korunmadı"* sonucu
bir **ölçek artefaktından** okunur. DARE bunu çözmez (beklentiyi korur, oranı korumaz).

Bu yüzden her `τ` **birim Frobenius normuna** indirilir, TIES uygulanır, sonuç girdi normlarının
**ortalamasıyla** yeniden ölçeklenir (tek bir kolla kıyaslanabilir büyüklükte kalsın).
`--no-norm-balance` ham TIES ablasyonunu koşar (ADR-0036 gereği ikisi de raporlanır).

⚠️ **Normalizasyon KAPSAMI seçilebilir** (`--norm-kapsam`): `global` tüm τ için tek `‖τ‖_F`
(ADR-0036'nın birebir okunuşu, varsayılan) · `modul` her modül yüzeyi ayrı normalize edilir.
Modül-başına kapsam sprint3 Adım 0'da ölçülüyor: iki kolun da en büyük normu **aynı MLP
yüzeyinde** (`gate_proj` τ_g 6,150 ↔ τ_a 0,621 · `up_proj` 5,047 ↔ 0,628) ve global norm bunu
göremiyor — `τ_a` tam becerilerin çakıştığı yerde siliniyor olabilir.

## Değişmezler

- ΔW **bf16**'da materyalize edilir, **tam ağırlık uzayında** birleştirilir (TIES delta üzerinde
  eleman-bazlı çalışır; LoRA uzayında birleştirme yalnız düz doğrusal toplam için geçerlidir).
- **Ana RAM'de, tensör tensör akıtmalı** — asla GPU'da. Base + tüm kollar bf16'da tam
  materyalize edilse onlarca GB olur.
- Nicemleme **en son** (bu betikten sonra, llama.cpp ile Q4_K_M).
- `‖τ‖_F` her kol için **koşulsuz** ölçülür ve künyeye yazılır (ADR-0036).

Kullanım:
  python scripts/egitim/merge_ties.py --base <hf-repo-ya-da-dizin> \
      --adapter tg=outputs/tg_v1 --adapter ta=outputs/ta_v1 \
      --out models/merged/tg_ta_normdengeli --kunye outputs/eval/.../merge_kunye.json
  # ham TIES ablasyonu:
  ... --no-norm-balance --out models/merged/tg_ta_hamties
"""
import argparse
import json
import os
import shutil

import torch
from safetensors import safe_open
from safetensors.torch import save_file

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

from merge_lora import SKIP_NAMES, SKIP_SUFFIX, load_deltas, resolve_base


def parse_args():
    p = argparse.ArgumentParser()
    # ⚠️ ADR-0026: base'in varsayılanı YOK — tanımsızsa ERKEN patla.
    p.add_argument("--base", required=True)
    p.add_argument("--adapter", action="append", required=True, metavar="AD=DIZIN",
                   help="kol adı ve adaptör dizini; k kez verilir (eşzamanlı k-yollu merge)")
    p.add_argument("--out", required=True)
    p.add_argument("--kunye", default="", help="ölçüm künyesi (norm'lar, TIES istatistikleri)")
    p.add_argument("--trim-k", type=float, default=0.20,
                   help="TIES kırpma: her τ'da büyüklüğe göre üstteki oran korunur (Yadav ve ark.)")
    p.add_argument("--lam", type=float, default=1.0,
                   help="birleştirilmiş vektöre uygulanan λ ölçeği")
    p.add_argument("--geri-olcek", default="ortalama",
                   help="norm dengelemeden sonra birleşik vektörün geri ölçeklendiği kural: "
                        "`ortalama` (varsayılan) · `min` · `max` · bir kol adı (ör. `tg`). "
                        "⚠️ Why: her τ birim norma iniyor ve sonuç bu ölçekle geri büyütülüyor. "
                        "Normlar çok eşitsizse `ortalama` KÜÇÜK kolu kendi eğitim genliğinin "
                        "çok üstüne çıkarır — ölçüldü: ‖τ_a‖=1,18 iken ortalama 5,83, yani "
                        "4,9× aşırı yükseltme; model dejenere oldu (research_log #48 §21).")
    p.add_argument("--no-norm-balance", action="store_true",
                   help="HAM TIES ablasyonu (ADR-0036) — norm-dengeleme uygulanmaz")
    p.add_argument("--norm-kapsam", default="global", choices=["global", "modul"],
                   help="normalleştirmenin KAPSAMI: `global` tek ‖τ‖_F (ADR-0036'nın birebir "
                        "okunuşu) · `modul` her modül yüzeyi (gate_proj, up_proj, ...) ayrı "
                        "normalize edilir. Why: iki kolun da en büyük normu AYNI MLP yüzeyinde "
                        "(τ_g gate_proj 6,150 ↔ τ_a 0,621) ve global norm bunu göremiyor — "
                        "τ_a tam çakışma noktasında siliniyor olabilir.")
    return p.parse_args()


def olcek_kurali(kural: str, degerler: dict) -> float:
    """Geri ölçek: `ortalama` · `min` · `max` ya da bir kol adı."""
    if kural == "ortalama":
        return sum(degerler.values()) / len(degerler)
    if kural == "min":
        return min(degerler.values())
    if kural == "max":
        return max(degerler.values())
    if kural in degerler:
        return degerler[kural]
    raise SystemExit(f"[ties] 🚫 --geri-olcek {kural!r} tanınmadı — "
                     f"`ortalama` · `min` · `max` ya da kol adı: {sorted(degerler)}")


def modul_adi(tensor_adi: str) -> str:
    """`model.layers.0.mlp.gate_proj.weight` → `gate_proj`. kol_normlari ile AYNI kural."""
    return tensor_adi.split(".")[-2]


def dw(A: torch.Tensor, B: torch.Tensor, scale: float) -> torch.Tensor:
    """ΔW = (α/r)·B·A, bf16'da materyalize (ADR-0031)."""
    return ((B.float() @ A.float()) * scale).to(torch.bfloat16)


def kol_normlari(adapters: dict[str, str]) -> tuple[dict, dict]:
    """1. geçiş: her kolun global ‖τ‖_F'i + modül kırılımı.

    ADR-0036 bunu KOŞULSUZ ister — norm-dengeleme kapalı olsa bile ölçülür ve raporlanır,
    çünkü *"kollar farklı ölçekte"* iddiası bu sayıyla ayakta duruyor.
    """
    normlar, kirilim = {}, {}
    for ad, d in adapters.items():
        deltas, scale = load_deltas(d)
        kare, per_mod = 0.0, {}
        for name, (A, B) in deltas.items():
            n2 = dw(A, B, scale).float().pow(2).sum().item()
            kare += n2
            mod = name.split(".")[-2]
            per_mod[mod] = per_mod.get(mod, 0.0) + n2
        normlar[ad] = kare ** 0.5
        kirilim[ad] = {m: round(v ** 0.5, 6) for m, v in sorted(per_mod.items())}
        print(f"[ties] ‖τ_{ad}‖_F = {normlar[ad]:.6f}  ({len(deltas)} LoRA çifti, α/r={scale})")
    return normlar, kirilim


def ties(taus: torch.Tensor, trim_k: float) -> tuple[torch.Tensor, dict]:
    """Eşzamanlı k-yollu TIES: kırp → işaret seç → ayrık ortalama.

    `taus`: (k, ...) — k kolun aynı tensör için delta'ları, ÜST ÜSTE.
    Sırayla uygulanmaz; üç adım da k vektörün tamamı üzerinde bir kerede çalışır.
    """
    k = taus.shape[0]
    flat = taus.reshape(k, -1).float()

    # 1) KIRP — her kolda büyüklüğe göre üstteki trim_k oranı kalır, gerisi sıfır.
    n = flat.shape[1]
    tut = max(1, int(round(n * trim_k)))
    esik = flat.abs().kthvalue(n - tut + 1, dim=1, keepdim=True).values
    kirpilmis = torch.where(flat.abs() >= esik, flat, torch.zeros_like(flat))

    # 2) İŞARET SEÇ — kütle-ağırlıklı toplamın işareti (normalize edilmişse kollar eşit ağırlıklı).
    # ⚠️ Toplam TAM SIFIR ise işaret SEÇİLMEMİŞTİR ve o parametre güncellenmez (merged=0).
    # Neden: sign=+1 gibi keyfi bir kırılım, tam çakışan kollarda (τ ve −τ) |τ| üretir — yani
    # birbirini götürmesi gereken yerde SİSTEMATİK POZİTİF sapma. Ölçüldü: TIES(τ,−τ) sıfır
    # yerine |τ| veriyordu. Kolların gerçek delta'larında tam eşitlik pratikte olmaz, ama
    # keyfi bir kırılımın sapması ölçülemez; sıfırın sapması ölçülebilir.
    isaret = torch.sign(kirpilmis.sum(dim=0))

    # 3) AYRIK ORTALAMA — yalnız seçilen işaretle uyuşan değerler ortalanır.
    uyusan = (torch.sign(kirpilmis) == isaret.unsqueeze(0)) & (kirpilmis != 0) \
        & (isaret != 0).unsqueeze(0)
    toplam = (kirpilmis * uyusan).sum(dim=0)
    sayi = uyusan.sum(dim=0).clamp(min=1)
    merged = toplam / sayi

    ist = {
        "catisan_parametre_orani": round(
            ((uyusan.sum(0) > 0) & (((torch.sign(kirpilmis) != isaret.unsqueeze(0))
                                     & (kirpilmis != 0)).sum(0) > 0)).float().mean().item(), 6),
        "sifir_kalan_oran": round((merged == 0).float().mean().item(), 6),
    }
    return merged.reshape(taus.shape[1:]).to(torch.bfloat16), ist


def main():
    a = parse_args()
    adapters = {}
    for spec in a.adapter:
        if "=" not in spec:
            raise SystemExit(f"[ties] 🚫 --adapter biçimi AD=DIZIN olmalı: {spec!r}")
        ad, d = spec.split("=", 1)
        adapters[ad] = d
    if len(adapters) < 2:
        raise SystemExit("[ties] 🚫 TIES en az 2 kol ister; tek kol için merge_lora.py kullan")

    base_dir = resolve_base(a.base)
    print(f"[ties] base={base_dir}")
    print(f"[ties] {len(adapters)} kol: {', '.join(adapters)} | trim_k={a.trim_k} λ={a.lam} | "
          f"norm-dengeleme={'KAPALI (ham TIES ablasyonu)' if a.no_norm_balance else 'AÇIK'}")

    normlar, kirilim = kol_normlari(adapters)

    yuk = {ad: load_deltas(d) for ad, d in adapters.items()}
    delta_setleri = {ad: v[0] for ad, v in yuk.items()}
    olcekler = {ad: v[1] for ad, v in yuk.items()}

    # 🚨 Kolların LoRA hedefleri AYNI olmalı; değilse bir kol bazı tensörlerde hiç yok demektir
    # ve TIES o parametrelerde tek-kollu olur. Sessiz geçersizlik — durdur.
    anahtar_kumeleri = {ad: set(d) for ad, d in delta_setleri.items()}
    ortak = set.intersection(*anahtar_kumeleri.values())
    tumu = set.union(*anahtar_kumeleri.values())
    if ortak != tumu:
        fark = {ad: sorted(tumu - k)[:3] for ad, k in anahtar_kumeleri.items() if k != tumu}
        raise SystemExit(f"[ties] 🚫 kolların LoRA hedefleri AYNI DEĞİL. Eksikler: {fark}\n"
                         "   → --target-modules rejimleri ayrışmış (bkz. TASARIM §4.1.1)")

    # Norm-dengeleme katsayıları — modül bazında tutulur; `global` kapsamda her modüle
    # aynı skaler yazılır. Tek temsil, merge döngüsünde tek arama yolu.
    moduller = sorted({modul_adi(n) for n in ortak})
    if a.no_norm_balance:
        katsayi = {ad: {m: 1.0 for m in moduller} for ad in adapters}
        geri_olcek = {m: 1.0 for m in moduller}
    elif a.norm_kapsam == "modul":
        for ad in adapters:
            for m in moduller:
                if kirilim[ad].get(m, 0.0) <= 0:
                    raise SystemExit(f"[ties] 🚫 ‖τ_{ad}‖ modülü {m!r} için 0 — bölme tanımsız. "
                                     f"Kol bu yüzeyde hiç eğitilmemiş demektir (sessiz tek-kolluluk)")
        katsayi = {ad: {m: 1.0 / kirilim[ad][m] for m in moduller} for ad in adapters}
        geri_olcek = {m: olcek_kurali(a.geri_olcek, {ad: kirilim[ad][m] for ad in adapters})
                      for m in moduller}
    else:
        g = olcek_kurali(a.geri_olcek, normlar)
        katsayi = {ad: {m: 1.0 / normlar[ad] for m in moduller} for ad in adapters}
        geri_olcek = {m: g for m in moduller}

    print(f"[ties] norm kapsamı={a.norm_kapsam} · geri ölçek kuralı={a.geri_olcek}")
    for m in moduller:
        kats = {ad: round(katsayi[ad][m], 6) for ad in adapters}
        print(f"[ties]   {m:14} katsayı={kats} geri_ölçek={geri_olcek[m]:.6f}")

    index = json.load(open(os.path.join(base_dir, "model.safetensors.index.json")))
    weight_map: dict[str, str] = index["weight_map"]
    shards: dict[str, list[str]] = {}
    for tn, sh in weight_map.items():
        shards.setdefault(sh, []).append(tn)

    os.makedirs(a.out, exist_ok=True)
    applied, ist_toplam = 0, {"catisan_parametre_orani": [], "sifir_kalan_oran": []}
    for shard, names in shards.items():
        out_tensors = {}
        with safe_open(os.path.join(base_dir, shard), "pt") as f:
            for name in names:
                w = f.get_tensor(name)
                if name in ortak:
                    mod = modul_adi(name)
                    yigin = []
                    for ad in adapters:
                        A, B = delta_setleri[ad][name]
                        if B.shape[0] != w.shape[0] or A.shape[1] != w.shape[1]:
                            raise SystemExit(
                                f"[ties] 🚫 şekil uyuşmazlığı {name} kol={ad}: W{tuple(w.shape)} "
                                f"vs B{tuple(B.shape)}@A{tuple(A.shape)}")
                        yigin.append(dw(A, B, olcekler[ad]) * katsayi[ad][mod])
                    merged, ist = ties(torch.stack(yigin), a.trim_k)
                    del yigin
                    w = (w.float() + merged.float() * geri_olcek[mod] * a.lam).to(w.dtype)
                    applied += 1
                    for kk in ist_toplam:
                        ist_toplam[kk].append(ist[kk])
                out_tensors[name] = w
        save_file(out_tensors, os.path.join(a.out, shard), metadata={"format": "pt"})
        print(f"[ties]   {shard}: {len(names)} tensör ({applied} birleşik)")
        del out_tensors

    # 🚨 Sessiz-bozulma kapısı — merge_lora.py ile aynı gerekçe: eksik uygulama = geçersiz merge,
    # ama dosya yine yazılır ve "oldu" görünür.
    if applied != len(ortak):
        raise SystemExit(f"[ties] 🚫 {applied}/{len(ortak)} uygulandı. "
                         f"Base'de bulunamayan: {sorted(ortak - set(weight_map))[:5]}")

    for fn in sorted(os.listdir(base_dir)):
        if fn.endswith(SKIP_SUFFIX) or fn in SKIP_NAMES:
            continue
        src = os.path.realpath(os.path.join(base_dir, fn))
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(a.out, fn))
    shutil.copy2(os.path.realpath(os.path.join(base_dir, "model.safetensors.index.json")),
                 os.path.join(a.out, "model.safetensors.index.json"))

    kunye = {
        "operator": "eşzamanlı k-yollu TIES (kırp → işaret seç → ayrık ortalama)",
        "karar_belgeleri": ["ADR-0027", "ADR-0036", "ADR-0031 (bf16 ΔW)"],
        "base": base_dir, "kollar": adapters,
        "norm_dengeleme": not a.no_norm_balance,
        "norm_kapsami": a.norm_kapsam,
        "tau_norm_fro": {k: round(v, 6) for k, v in normlar.items()},
        "tau_norm_modul_kirilimi": kirilim,
        "norm_katsayilari": {ad: {m: round(v, 8) for m, v in d.items()}
                             for ad, d in katsayi.items()},
        "geri_olcek": {m: round(v, 6) for m, v in geri_olcek.items()},
        "geri_olcek_kurali": (None if a.no_norm_balance else a.geri_olcek),
        "trim_k": a.trim_k, "lam": a.lam,
        "birlesik_tensor": applied, "ortak_lora_hedefi": len(ortak),
        "ties_istatistikleri": {k: round(sum(v) / len(v), 6) for k, v in ist_toplam.items() if v},
        "out": a.out,
        "not": "Nicemleme BU ADIMDAN SONRA (llama.cpp Q4_K_M). Merge ana RAM'de akıtmalı koştu.",
    }
    print("\n[ties] KÜNYE: " + json.dumps(kunye, ensure_ascii=False, indent=2))
    if a.kunye:
        os.makedirs(os.path.dirname(a.kunye) or ".", exist_ok=True)
        json.dump(kunye, open(a.kunye, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(f"[ties] künye → {a.kunye}")
    print(f"[ties] ✅ {applied} tensörde {len(adapters)}-yollu TIES → {a.out}")


if __name__ == "__main__":
    main()
