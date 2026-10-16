"""F0.5 (b) — RQ2'nin anahtarları puanlayıcılara bağlı (ADR-0099 m.1). Ağ yok, para yok.

Kütle tarafındaki anahtarların kayıttaki sayılarla çıpası `test_kutle.py`'de; burada hakeme giden
girdiyi değiştiren anahtarların (kaynak kırpması · kör payda · altın madde kırpması) ve
dedektörün çekinme puanlayıcısına bağlandığı sınanır.
"""
import json
import os
import subprocess
import sys
from dataclasses import replace

import pytest

import groundedness  # noqa: E402
import score_abstention as sa  # noqa: E402
from olcum_aleti import GUNCEL, AltinKirpma, Dedektor, KaynakKirpma  # noqa: E402

_KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# olcum-bi id 53 — ADR-0061'in vakası: şablonun eleme gerekçesi eski dedektörde çekinme sayılıyordu.
_ID53 = ("KAYNAK 1, zincirleme suçlarda yetkili mahkeme hakkında bilgi vermektedir. Diğer kaynaklar, "
         "zincirleme suçlarla ilgili spesifik hükümler içermemektedir.\n\n**Cevap:** Zincirleme "
         "suçlarda yetkili mahkeme, son suçun işlendiği yer mahkemesidir. (CEZA MUHAKEMESİ KANUNU, "
         "Madde 12)")


def test_dedektor_anahtari_kipli_reddet():
    eski = replace(GUNCEL, dedektor=Dedektor.ADR0061_ONCESI)
    assert GUNCEL.reddet(_ID53, "data") is False
    assert eski.reddet(_ID53, "data") is True
    assert eski.cevap_mi(_ID53) is False


def test_kaynak_kirpma_anahtari_hakem_istemini_ve_onbellek_anahtarini_degistirir():
    kaynak = "a" * 5000 + "b" * 10000
    yeni = sa.gecerlilik_istemi("S?", kaynak, KaynakKirpma.K12000.value)
    eski = sa.gecerlilik_istemi("S?", kaynak, KaynakKirpma.K3500.value)
    assert yeni.count("a") == 5000 and yeni.count("b") == 7000
    assert eski.count("a") == 3500 and "b" not in eski
    assert (sa.gecerlilik_anahtari("S?", kaynak, 3500) != sa.gecerlilik_anahtari("S?", kaynak, 12000))
    # Why: 3500 anahtarı, 2026-09-07 öncesi önbellek kayıtlarına birebir düşer (aynı formül).
    assert sa.gecerlilik_anahtari("S?", kaynak, 3500) == sa.gecerlilik_anahtari("S?", kaynak[:3500], 12000)


def test_altin_kirpma_anahtari_dogrulama_istemini_degistirir():
    altin = "x" * 3600
    kirpik = groundedness.dogrulama_istemi("S?", altin, "G", "C", ["i"], AltinKirpma.K3500)
    tam = groundedness.dogrulama_istemi("S?", altin, "G", "C", ["i"], AltinKirpma.KIRPMASIZ)
    assert kirpik.count("x") == 3500 and tam.count("x") == 3600


def test_dogrulama_istemi_sirasi_onbellege_uygun():
    """F0.6: talimat, soru ve kaynaklar başta; cevap ve iddialar sonda (önbellek öneki ortak)."""
    i = groundedness.dogrulama_istemi("SORUM", "KAYNAGIM", "ALTINIM", "CEVABIM", ["IDDIAM"],
                                      GUNCEL.altin_kirpma)
    yer = [i.index(x) for x in ("SORUM", "KAYNAGIM", "ALTINIM", "CEVABIM", "IDDIAM")]
    assert yer == sorted(yer)


def _kos_abst(tmp_path, *ek, onceki=None):
    d = tmp_path / "kosu"
    d.mkdir()
    detay = [{"id": i, "soru": f"Soru {i}?", "cevap": "Verilen kaynaklarda bu konu yok.",
              "mode": "oracle", "referans": f"Madde {i} metni."} for i in range(4)]
    with open(d / "m2_t_detail.jsonl", "w", encoding="utf-8") as f:
        f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in detay)
    # Önceki pay hakeminin kaydı: cevabı görerek verdiği `source_answers` (denetim izi).
    json.dump(onceki or [{"id": i, "verdict": "ABSTAIN", "used_parametric": False, "reason": "x",
                          "valid_trap_anahtari": "k", "source_answers_cevapli": i == 0}
                         for i in range(4)],
              open(d / "abst_m2_t.jsonl", "w", encoding="utf-8"))
    ortam = {k: v for k, v in os.environ.items() if k not in ("OPENAI_API_KEY", "OPENROUTER_API_KEY")}
    p = subprocess.run(
        [sys.executable, "scripts/puanlama/skorlayici/score_abstention.py", "--details", str(d / "m2_t_detail.jsonl"),
         "--label", "m2_t", "--out-dir", str(d), "--pay-kaynagi", "onceki",
         "--gecerlilik-onbellek", str(tmp_path / "onbellek.json"), *ek],
        capture_output=True, text=True, env=ortam, cwd=_KOK)
    assert p.returncode == 0, p.stdout + p.stderr
    return json.load(open(d / "abst_m2_t_summary.json", encoding="utf-8"))


def test_kor_payda_anahtari_cevapli_kipte_payda_pay_hakeminin_kaydindan(tmp_path):
    """Eski alet (K3 öncesi): payda, cevabı gören pay hakeminin `source_answers`'ından gelir.
    `--pay-kaynagi onceki` ile hiçbir hakem çağrılmaz (anahtar yok → çağrı olsaydı test çökerdi)."""
    ozet = _kos_abst(tmp_path, "--payda", "cevapli")
    assert (ozet["valid_traps"], ozet["invalid_traps"]) == (3, 1)
    assert ozet["judge_cost_usd"] == 0.0
    assert ozet["olcum_aleti"]["payda"] == "cevapli"


# ── üretim tarafı: RRF_K anahtarı (eski hâl 60, ADR-0068 öncesi) ─────────────────────────

def test_getir_rrf_k_parametresini_fuzyona_iletir(tmp_path, monkeypatch):
    import retriever
    from test_retriever import _korpus_yaz, _sahte_gomucu
    idx = str(tmp_path / "indeks")
    retriever.Retriever.kur(_korpus_yaz(tmp_path), idx, gomucu=_sahte_gomucu)
    r = retriever.Retriever.yukle(idx, gomucu=_sahte_gomucu)
    gorulen = []
    asil = retriever.rrf_birlestir
    monkeypatch.setattr(retriever, "rrf_birlestir",
                        lambda skorlar, rrf_k: gorulen.append(rrf_k) or asil(skorlar, rrf_k))
    r.getir("işçi", k=2, rrf_k=60)
    r.getir("işçi", k=2)
    assert gorulen == [60, retriever.RRF_K]


def test_gen_eval_rrf_k_harness_izine_yaziliyor():
    """Tuzak 6.12: bayrak çağrı zincirinin ucuna (koşu satırına) kadar izlenir."""
    import ast
    agac = ast.parse(open(os.path.join(_KOK, "scripts/olcum_uretim/uretim/gen_eval_grounded.py"),
                          encoding="utf-8").read())
    argumanlar = [n.args[0].value for n in ast.walk(agac) if isinstance(n, ast.Call)
                  and getattr(n.func, "attr", None) == "add_argument"]
    assert "--rrf-k" in argumanlar
    izler = [n for n in ast.walk(agac) if isinstance(n, ast.Dict)
             and any(isinstance(k, ast.Constant) and k.value == "rrf_k" for k in n.keys)]
    assert izler, "harness izi `rrf_k` alanını taşımıyor"
    getir = [n for n in ast.walk(agac) if isinstance(n, ast.Call) and getattr(n.func, "attr", None) == "getir"]
    assert getir and all(any(k.arg == "rrf_k" for k in n.keywords) for n in getir)


@pytest.mark.slow
@pytest.mark.parametrize("kume,rrf_k,beklenen", [
    ("data/eval/dev/core_hard.jsonl", 60, 0.9375),               # #62 Bulgu 2: v2 sorular, eski füzyon
    ("data/eval/dev/core_hard.jsonl", 10, 0.9500),               # bugünkü
    ("data/eval/dev/core_hard.jsonl.v1-2026-09-06", 60, 0.8750),  # v1 sorular, eski füzyon
])
def test_rrf_k_anahtari_62_cipasi_gercek_indeksle(kume, rrf_k, beklenen):
    """Gerçek indeks + bge-m3, CPU. Çıpa: faz0/f01b-soru-onarimi/SONUC_recall_v1_v2.md."""
    from madde_anahtar import madde_anahtari
    from retriever import Retriever
    r = Retriever.yukle(os.path.join(_KOK, "data/index/mevzuat_bge_m3_s2"))
    dev = [json.loads(l) for l in open(os.path.join(_KOK, kume), encoding="utf-8") if l.strip()]
    isabet = sum(
        any(madde_anahtari(g["kanun_no"], g["madde_no"]) == madde_anahtari(d["kanun_no"], d["madde_no"])
            for g in r.getir(d["messages"][0]["content"], k=10, rrf_k=rrf_k))
        for d in dev)
    assert round(isabet / len(dev), 4) == beklenen


def test_onsoz_anahtari_metni_aa04c78_ile_birebir():
    """Üretim tarafının eski hâli (`--sufficiency-preamble`): metin ADR-0058'in koştuğu hâlle aynı.
    Kaynak: bundle `aa04c78:scripts/gen_eval_grounded.py` (2026-10-11'de karşılaştırıldı)."""
    import ast
    agac = ast.parse(open(os.path.join(_KOK, "scripts/olcum_uretim/uretim/gen_eval_grounded.py"),
                          encoding="utf-8").read())
    atama = next(n for n in agac.body if isinstance(n, ast.Assign)
                 and getattr(n.targets[0], "id", None) == "SUFFICIENCY_PREAMBLE")
    assert ast.literal_eval(atama.value) == (
        "\nCevabına başlamadan ÖNCE, verilen kaynağın soruyu cevaplayıp cevaplamadığını "
        "tek cümleyle belirt. Kaynak soruyu cevaplamıyorsa bunu söyle ve cevap uydurma.")


def test_kor_payda_cevapli_kipte_k3_oncesi_kayittan_okur(tmp_path):
    """K3 öncesi dosyada `source_answers` alanı yok; `valid_trap` zaten cevaplı paydanın kendisidir
    (`valid = not source_answers`). Ayırt eden: K3 sonrası kayıtlar `valid_trap_anahtari` taşır."""
    eski = [{"id": i, "verdict": "ABSTAIN", "used_parametric": False, "reason": "x",
             "valid_trap": i != 0} for i in range(4)]
    ozet = _kos_abst(tmp_path, "--payda", "cevapli", onceki=eski)
    assert (ozet["valid_traps"], ozet["invalid_traps"]) == (3, 1)
