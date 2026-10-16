import json

import pytest
from eslesmis_a1 import eslesmis_a1, ikili


RED = "Verilen kaynaklarda bu konuyu düzenleyen madde bulunmuyor."
# Kör modda sistem isteminin EMRETTİĞİ feragat cümlesi — `data`'da red, `blind`'da değil.
FERAGAT = "Güncel mevzuat için bir avukata danışmanızı öneririm."


def _yaz(tmp_path, ad, kayitlar):
    p = tmp_path / ad
    p.write_text("\n".join(json.dumps(k, ensure_ascii=False) for k in kayitlar), encoding="utf-8")
    return str(p)


def test_eslesmis_a1_yalnizca_ikisinin_de_cevapladigi_kalemleri_sayar(tmp_path):
    # id=1 ikisi de cevapladı · id=2 yalnız A cevapladı · id=3 yalnız B cevapladı
    da = _yaz(tmp_path, "da.jsonl", [{"id": "1", "cevap": "Süre on gündür."},
                                     {"id": "2", "cevap": "Süre beş gündür."},
                                     {"id": "3", "cevap": RED}])
    ga = _yaz(tmp_path, "ga.jsonl", [{"id": "1", "faithfulness": 1.0},
                                     {"id": "2", "faithfulness": 0.5},
                                     {"id": "3", "faithfulness": 0.0}])
    db = _yaz(tmp_path, "db.jsonl", [{"id": "1", "cevap": "Süre on gündür."},
                                     {"id": "2", "cevap": RED},
                                     {"id": "3", "cevap": "Süre üç gündür."}])
    gb = _yaz(tmp_path, "gb.jsonl", [{"id": "1", "faithfulness": 0.8},
                                     {"id": "2", "faithfulness": 0.0},
                                     {"id": "3", "faithfulness": 1.0}])
    r = ikili(da, ga, db, gb, mode="data")
    assert r["n_kesisim"] == 1
    assert r["id_listesi"] == ["1"]
    assert r["a1_a"] == 1.0
    assert r["a1_b"] == 0.8
    assert abs(r["fark"] - 0.2) < 1e-9


def test_eslesmis_a1_kesisim_bossa_patlar(tmp_path):
    da = _yaz(tmp_path, "da.jsonl", [{"id": "1", "cevap": "Süre on gündür."}])
    ga = _yaz(tmp_path, "ga.jsonl", [{"id": "1", "faithfulness": 1.0}])
    db = _yaz(tmp_path, "db.jsonl", [{"id": "1", "cevap": RED}])
    gb = _yaz(tmp_path, "gb.jsonl", [{"id": "1", "faithfulness": 0.0}])
    with pytest.raises(ValueError, match="kesişim"):
        ikili(da, ga, db, gb, mode="data")


def test_eslesmis_a1_gnd_kaydi_eksikse_patlar(tmp_path):
    # detail'da var, gnd'de yok → sessizce atlamak yerine PATLAMALI (bu hattın hata sınıfı
    # sessiz yanlışlık; eksik puanlanmış kalemi görmezden gelmek paydayı kaydırır).
    da = _yaz(tmp_path, "da.jsonl", [{"id": "1", "cevap": "Süre on gündür."},
                                     {"id": "2", "cevap": "Süre beş gündür."}])
    ga = _yaz(tmp_path, "ga.jsonl", [{"id": "1", "faithfulness": 1.0}])
    db = _yaz(tmp_path, "db.jsonl", [{"id": "1", "cevap": "Süre on gündür."},
                                     {"id": "2", "cevap": "Süre üç gündür."}])
    gb = _yaz(tmp_path, "gb.jsonl", [{"id": "1", "faithfulness": 0.8},
                                     {"id": "2", "faithfulness": 0.9}])
    # ⚠️ match=r"2" zayıftı: "(toplam 2)" de eşleşiyordu, yani test id listesini SINAMIYORDU.
    with pytest.raises(KeyError, match=r"\['2'\]"):
        ikili(da, ga, db, gb, mode="data")


def test_eslesmis_a1_b_kolunun_gnd_kaydi_eksikse_de_patlar(tmp_path):
    # `i not in ga or i not in gb` ifadesinin İKİNCİ dalı — eksiklik B kolundayken.
    da = _yaz(tmp_path, "da.jsonl", [{"id": "1", "cevap": "Süre on gündür."},
                                     {"id": "2", "cevap": "Süre beş gündür."}])
    ga = _yaz(tmp_path, "ga.jsonl", [{"id": "1", "faithfulness": 1.0},
                                     {"id": "2", "faithfulness": 0.5}])
    db = _yaz(tmp_path, "db.jsonl", [{"id": "1", "cevap": "Süre on gündür."},
                                     {"id": "2", "cevap": "Süre üç gündür."}])
    gb = _yaz(tmp_path, "gb.jsonl", [{"id": "1", "faithfulness": 0.8}])
    with pytest.raises(KeyError, match=r"\['2'\]"):
        ikili(da, ga, db, gb, mode="data")


def test_eslesmis_a1_faithfulness_none_kesisimdeyse_patlar(tmp_path):
    # `statistics.fmean` bunu TANISIZ TypeError ile patlatırdı; `rescore_answered.macro()` ise
    # sessizce paydadan düşürüyor → iki A1 yolu tanım olarak ayrışır (tuzak 2.16).
    da = _yaz(tmp_path, "da.jsonl", [{"id": "1", "cevap": "Süre on gündür."},
                                     {"id": "2", "cevap": "Süre beş gündür."}])
    ga = _yaz(tmp_path, "ga.jsonl", [{"id": "1", "faithfulness": 1.0},
                                     {"id": "2", "faithfulness": 0.5}])
    db = _yaz(tmp_path, "db.jsonl", [{"id": "1", "cevap": "Süre on gündür."},
                                     {"id": "2", "cevap": "Süre üç gündür."}])
    gb = _yaz(tmp_path, "gb.jsonl", [{"id": "1", "faithfulness": 0.8},
                                     {"id": "2", "faithfulness": None, "n_claims": 0}])
    with pytest.raises(ValueError, match=r"faithfulness=None.*\['2'\]"):
        ikili(da, ga, db, gb, mode="data")


def test_eslesmis_a1_ayrisma_sayaclari_etkin_n_verir(tmp_path):
    # n_kesisim=4 ama üçü BERABERE → etkin n = 1. `n_kesisim ≥ 30` kapısının ölçmediği şey bu.
    cevaplar = [{"id": str(i), "cevap": "Süre on gündür."} for i in range(1, 5)]
    da = _yaz(tmp_path, "da.jsonl", cevaplar)
    db = _yaz(tmp_path, "db.jsonl", cevaplar)
    ga = _yaz(tmp_path, "ga.jsonl", [{"id": "1", "faithfulness": 1.0},
                                     {"id": "2", "faithfulness": 1.0},
                                     {"id": "3", "faithfulness": 0.5},
                                     {"id": "4", "faithfulness": 0.5}])
    gb = _yaz(tmp_path, "gb.jsonl", [{"id": "1", "faithfulness": 1.0},
                                     {"id": "2", "faithfulness": 1.0},
                                     {"id": "3", "faithfulness": 0.5},
                                     {"id": "4", "faithfulness": 1.0}])
    r = ikili(da, ga, db, gb, mode="data")
    assert r["n_kesisim"] == 4
    assert r["n_ayrisan"] == 1
    assert r["n_berabere"] == 3
    assert r["a_lehine"] == 0
    assert r["b_lehine"] == 1
    assert abs(r["fark_sd"] - 0.25) < 1e-9


def test_eslesmis_a1_mod_kayittan_okunur_blind_feragati_cevap_sayar(tmp_path):
    # ADR-0044: kör modda feragat cümlesi çekinme DEĞİLDİR. Mod kayıttan okunur — küresel
    # varsayılan `data` olsaydı bu kalem sessizce paydadan düşer, sayı bizim lehimize kayardı.
    def dosyalar(mode):
        d = _yaz(tmp_path, f"d_{mode}.jsonl",
                 [{"id": "1", "cevap": "Süre on gündür.", "mode": mode},
                  {"id": "2", "cevap": FERAGAT + " Süre beş gündür.", "mode": mode}])
        return d

    g = _yaz(tmp_path, "g.jsonl", [{"id": "1", "faithfulness": 1.0},
                                   {"id": "2", "faithfulness": 0.4}])
    d_blind, d_data = dosyalar("blind"), dosyalar("distractor")

    r_blind = ikili(d_blind, g, d_blind, g)
    assert r_blind["n_kesisim"] == 2 and r_blind["mode"] == ["blind"]

    r_data = ikili(d_data, g, d_data, g)
    assert r_data["n_kesisim"] == 1 and r_data["id_listesi"] == ["1"]
    assert r_data["mode"] == ["distractor"]


def test_eslesmis_a1_mode_override_kayitla_celisirse_uyarir(tmp_path):
    d = _yaz(tmp_path, "d.jsonl", [{"id": "1", "cevap": "Süre on gündür.", "mode": "distractor"}])
    g = _yaz(tmp_path, "g.jsonl", [{"id": "1", "faithfulness": 1.0}])
    r = ikili(d, g, d, g, mode="blind")
    assert r["mode"] == ["blind"]
    assert any("kayıt modu" in u for u in r["uyarilar"])


def test_eslesmis_a1_hakem_yigini_uyusmuyorsa_damgalanir(tmp_path):
    d = _yaz(tmp_path, "d.jsonl", [{"id": "1", "cevap": "Süre on gündür."}])
    ga = _yaz(tmp_path, "gnd_a.jsonl", [{"id": "1", "faithfulness": 1.0}])
    gb = _yaz(tmp_path, "gnd_b.jsonl", [{"id": "1", "faithfulness": 0.8}])
    (tmp_path / "gnd_a_summary.json").write_text(
        json.dumps({"judge_model": "gpt-4o-mini", "judge_gateway": "openai"}), encoding="utf-8")
    (tmp_path / "gnd_b_summary.json").write_text(
        json.dumps({"judge_model": "openai/gpt-4o-mini", "judge_gateway": "openrouter"}),
        encoding="utf-8")
    r = ikili(d, ga, d, gb, mode="data")
    assert r["hakem_yigini_uyusuyor"] is False
    assert r["hakem_yigini"]["A"] == ["gpt-4o-mini", "openai"]
    assert r["hakem_yigini"]["B"] == ["openai/gpt-4o-mini", "openrouter"]


def test_eslesmis_a1_hakem_yigini_ayniysa_gecer_ozet_yoksa_bilinmiyor(tmp_path):
    d = _yaz(tmp_path, "d.jsonl", [{"id": "1", "cevap": "Süre on gündür."}])
    ga = _yaz(tmp_path, "gnd_a.jsonl", [{"id": "1", "faithfulness": 1.0}])
    gb = _yaz(tmp_path, "gnd_b.jsonl", [{"id": "1", "faithfulness": 0.8}])
    # özet dosyası YOK → bilinmiyor, "uyuşuyor" değil
    assert ikili(d, ga, d, gb, mode="data")["hakem_yigini_uyusuyor"] is None

    for ad in ("gnd_a_summary.json", "gnd_b_summary.json"):
        (tmp_path / ad).write_text(
            json.dumps({"judge_model": "openai/gpt-4o-mini", "judge_gateway": "openrouter"}),
            encoding="utf-8")
    assert ikili(d, ga, d, gb, mode="data")["hakem_yigini_uyusuyor"] is True


def test_eslesmis_a1_uc_kol_tek_payda_uretir(tmp_path):
    # Görev 9 Adım 9.5: `base | BİZ v2 | FL` TEK satır → tek payda. İkili kıyaslarda base'in A1'i
    # iki farklı paydadan çıkıyordu (0,9844 ↔ 0,9861); o iki sayı aynı satıra KONULAMAZ.
    da = _yaz(tmp_path, "da.jsonl", [{"id": "1", "cevap": "x"}, {"id": "2", "cevap": "x"},
                                     {"id": "3", "cevap": "x"}])
    db = _yaz(tmp_path, "db.jsonl", [{"id": "1", "cevap": "x"}, {"id": "2", "cevap": "x"},
                                     {"id": "3", "cevap": RED}])
    dc = _yaz(tmp_path, "dc.jsonl", [{"id": "1", "cevap": "x"}, {"id": "2", "cevap": RED},
                                     {"id": "3", "cevap": "x"}])
    ga = _yaz(tmp_path, "ga.jsonl", [{"id": "1", "faithfulness": 1.0},
                                     {"id": "2", "faithfulness": 0.0},
                                     {"id": "3", "faithfulness": 0.0}])
    gb = _yaz(tmp_path, "gb.jsonl", [{"id": "1", "faithfulness": 0.5},
                                     {"id": "2", "faithfulness": 1.0},
                                     {"id": "3", "faithfulness": 1.0}])
    gc = _yaz(tmp_path, "gc.jsonl", [{"id": "1", "faithfulness": 0.25},
                                     {"id": "2", "faithfulness": 1.0},
                                     {"id": "3", "faithfulness": 1.0}])
    r = eslesmis_a1([(da, ga, "base"), (db, gb, "v2"), (dc, gc, "FL")], mode="data")
    assert r["n_kesisim"] == 1 and r["id_listesi"] == ["1"]
    assert r["a1_kollar"] == {"base": 1.0, "v2": 0.5, "FL": 0.25}
    assert set(r["farklar"]) == {"base−v2", "base−FL", "v2−FL"}
    assert abs(r["farklar"]["base−FL"] - 0.75) < 1e-9
    # k>2'de ikili-özel alanlar YOK — o alanlar payda ikili olduğunda anlamlı
    assert "a1_a" not in r and "fark" not in r


def test_eslesmis_a1_tek_kol_reddedilir(tmp_path):
    d = _yaz(tmp_path, "d.jsonl", [{"id": "1", "cevap": "x"}])
    g = _yaz(tmp_path, "g.jsonl", [{"id": "1", "faithfulness": 1.0}])
    with pytest.raises(ValueError, match="en az İKİ kol"):
        eslesmis_a1([(d, g, "tek")])


def test_eslesmis_a1_tekrarli_etiket_reddedilir(tmp_path):
    d = _yaz(tmp_path, "d.jsonl", [{"id": "1", "cevap": "x"}])
    g = _yaz(tmp_path, "g.jsonl", [{"id": "1", "faithfulness": 1.0}])
    with pytest.raises(ValueError, match="benzersiz"):
        eslesmis_a1([(d, g, "ayni"), (d, g, "ayni")])
