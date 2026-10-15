"""F0.16 ölçüm kartı koşucusunun saf parçaları (ADR-0097, ADR-0102): sunucu komutu compose'dan, sunucu
kimliği koşan süreçten, üretim rejimi tek yerden, geçerlilik kapısı. Ağ yok, GPU yok."""
import os

import yaml

import olcum_karti as ok  # noqa: E402

_KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPOSE = os.path.join(_KOK, "docker", "compose.yaml")


def _bayraklar(komut):
    """`-x deger` çiftleri ve tek bayraklar → sözlük (değersiz bayrağın değeri None)."""
    s, i = {}, 0
    while i < len(komut):
        if i + 1 < len(komut) and not komut[i + 1].startswith("-"):
            s[komut[i]] = komut[i + 1]
            i += 2
        else:
            s[komut[i]] = None
            i += 1
    return s


def test_sunucu_komutu_compose_bayraklarini_birebir_tasir_yalniz_model_ve_adres_degisir():
    compose = yaml.safe_load(open(COMPOSE, encoding="utf-8"))["services"]["llama"]["command"]
    komut = ok.sunucu_komutu(COMPOSE, "/m/model.gguf", port=8080)
    assert komut[0] == "/app/llama-server"
    beklenen = dict(_bayraklar(compose), **{"-m": "/m/model.gguf", "--host": "127.0.0.1", "--port": "8080"})
    assert _bayraklar(komut[1:]) == beklenen
    assert "-np" not in komut and "--parallel" not in komut        # ADR-0102 m.1


def test_sunucu_kimligi_surumu_ve_slot_sayisini_kosan_surecten_okur():
    surum = "version: 0.4.0-dev (build 10902, commit df03399b8)\nbuilt with GNU 14.2.0 for Linux x86_64\n"
    gunluk = ("0.13.757.121 I srv    load_model: initializing, n_slots = 4, n_ctx_slot = 8192, "
              "kv_unified = 'true'\n")
    k = ok.sunucu_kimligi(surum, gunluk)
    assert (k["build"], k["commit"], k["n_slots"], k["kv_unified"]) == (10902, "df03399b8", 4, True)


def test_uretim_komutu_rejim_degismezlerini_ve_donmus_baglami_tasir():
    komut = ok.uretim_komutu("python", "/k/gen.py", "http://127.0.0.1:8080/v1", veri="/d/core_hard.jsonl",
                             donmus_baglam="/d/h1-k10.json", etiket="h1_x", cikti_dizini="/o")
    b = _bayraklar(komut[2:])
    for bayrak, deger in {"--thinking": "on", "--think-budget": "1024", "--max-new-tokens": "512",
                          "--max-chunk-chars": "900", "--seed": "3407", "--harness-k": "10",
                          "--rrf-k": "10", "--n": "80", "--data": "/d/core_hard.jsonl",
                          "--donmus-baglam": "/d/h1-k10.json", "--server-model": "local"}.items():
        assert b.get(bayrak) == deger, bayrak
    assert "--harness-indeks" not in b and "--sufficiency-preamble" not in b


def test_gecerlilik_kesik_orani_yuzde_besi_asarsa_kosu_gecersiz():
    satir = lambda fr, rl=10, fc=False: {"finish_reason": fr, "reasoning_len": rl, "forced_close": fc}
    iyi = ok.gecerlilik([satir("stop")] * 76 + [satir("length")] * 4)          # %5,0 — eşikte geçer
    kotu = ok.gecerlilik([satir("stop")] * 75 + [satir("length")] * 5)         # %6,25
    assert (iyi["kesik"], iyi["gecerli"]) == (4, True)
    assert (kotu["kesik"], kotu["gecerli"]) == (5, False)


def test_gecerlilik_hic_dusunce_yoksa_kosu_gecersiz():
    g = ok.gecerlilik([{"finish_reason": "stop", "reasoning_len": 0, "forced_close": False}] * 80)
    assert g["gecerli"] is False and g["dusunen"] == 0
