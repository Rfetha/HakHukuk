"""GGUF → Hugging Face çevirisi (vLLM pilotu): ağırlıkların llama.cpp dizilişi geri çevrilir ve her tensör
orijinal (sıkıştırılmamış) ağırlıkla karşılaştırılır. Yanlış diziliş hata vermeden çalışan ama bozuk bir model
üretir; bu yüzden kapı sayısaldır: sıkıştırma gürültüsü dışında fark kalmamalı."""
import glob
import os

import numpy as np
import pytest

import gguf_hf_cevir as gc  # noqa: E402

_KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GGUF = os.path.join(_KOK, "models", "gguf", "tgta_v1-q4_k_m.gguf")
ORIJINAL = os.path.join(_KOK, "models", "merged", "tgta_v1")
VAR = os.path.exists(GGUF) and os.path.isdir(ORIJINAL)


def test_baslar_llama_cpp_dizilisinden_hf_dizilisine_geri_cevrilir():
    # HF: v-başı h = k*vpk + j (her k-başına vpk ardışık v-başı). llama.cpp "döşemeli": gguf[j*NK + k].
    nk, nv, blok = 2, 4, 3
    hf = np.arange(nv * blok * 5, dtype=np.float32).reshape(nv * blok, 5)
    g = np.empty_like(hf)
    for k in range(nk):
        for j in range(nv // nk):
            g[(j * nk + k) * blok:(j * nk + k + 1) * blok] = hf[(k * (nv // nk) + j) * blok:(k * (nv // nk) + j + 1) * blok]
    assert (gc.ters_baslar(g, k_bas=nk, v_bas=nv, eksen=0, blok=blok) == hf).all()
    # aynı diziliş sütunlarda (out_proj girdi boyutu başlara göre)
    assert (gc.ters_baslar(g.T, k_bas=nk, v_bas=nv, eksen=1, blok=blok) == hf.T).all()


def test_bilinmeyen_tensor_adi_sessizce_dusmez():
    with pytest.raises(SystemExit, match="bilinmeyen"):
        gc.hedef_ad("blk.3.yok_boyle_bir_tensor.weight")


def test_mtp_katmani_acikca_yok_sayilir_digerleri_eslenir():
    assert gc.hedef_ad("blk.32.nextn.eh_proj.weight") is None
    assert gc.hedef_ad("blk.3.attn_q.weight") == "model.layers.3.self_attn.q_proj.weight"
    assert gc.hedef_ad("blk.0.attn_gate.weight") == "model.layers.0.linear_attn.in_proj_z.weight"
    assert gc.hedef_ad("token_embd.weight") == "model.embed_tokens.weight"
    assert gc.hedef_ad("output_norm.weight") == "model.norm.weight"


@pytest.mark.parametrize("tip,hata,gecer", [("F32", 0.0, True), ("F32", 0.05, False), ("Q4_K", 0.0716, True),
                                            ("Q4_K", 0.9, False), ("Q6_K", 0.0183, True), ("Q6_K", 0.2, False)])
def test_dogrulama_kapisi_sikistirma_gurultusunu_gecirir_yanlis_dizilisi_reddeder(tip, hata, gecer):
    if gecer:
        gc.hata_kapisi("x", tip, hata)
    else:
        with pytest.raises(SystemExit, match="doğrulama"):
            gc.hata_kapisi("x", tip, hata)


def test_bilinmeyen_sikistirma_tipi_icin_kapi_durur():
    with pytest.raises(SystemExit, match="eşik tanımlı değil"):
        gc.hata_kapisi("x", "IQ2_XS", 0.01)


@pytest.mark.skipif(not VAR, reason="yerel GGUF ve orijinal ağırlıklar yok (models/ git dışı)")
def test_gguf_bir_dogrusal_ve_bir_tam_dikkat_katmaninin_butun_tensorleri_dogrulanir():
    dosya = gc.GGUFDosyasi(GGUF)
    orij = gc.OrijinalAgirliklar(ORIJINAL)
    boyut = gc.boyutlar(orij.config)
    n = 0
    for ad in dosya.adlar():
        if not ad.startswith(("blk.0.", "blk.3.")):
            continue
        hf_ad, y, _ = gc.cevir_tensor(ad, dosya, boyut)
        gc.dogrula(hf_ad, y, dosya.tip(ad), orij)
        n += 1
    assert n == 14 + 11


@pytest.mark.skipif(not VAR, reason="yerel GGUF ve orijinal ağırlıklar yok (models/ git dışı)")
def test_baslari_karistirilmis_tensor_dogrulamadan_gecmez():
    dosya = gc.GGUFDosyasi(GGUF)
    orij = gc.OrijinalAgirliklar(ORIJINAL)
    hf_ad, y, _ = gc.cevir_tensor("blk.0.attn_gate.weight", dosya, gc.boyutlar(orij.config))
    karisik = y.reshape(32, 128, -1)[::-1].reshape(y.shape)       # v-başlarının sırası bozuldu
    with pytest.raises(SystemExit, match="doğrulama"):
        gc.dogrula(hf_ad, karisik, dosya.tip("blk.0.attn_gate.weight"), orij)
