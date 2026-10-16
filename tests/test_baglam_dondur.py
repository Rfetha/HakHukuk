"""F0.16 bağlam dondurma (ADR-0097 m.6): her sorunun getirilen bağlamı bir kez üretilir, bütün koşular
aynı dosyayı okur. Gerçek retriever, sahte gömücü (model indirmez), üç maddelik korpus."""
import json
import os
import subprocess
import sys
from dataclasses import replace

import pytest

import baglam_dondur as bd  # noqa: E402
import gen_eval_grounded as geg  # noqa: E402
from retriever import Retriever  # noqa: E402
from test_retriever import _korpus_yaz, _sahte_gomucu  # noqa: E402

_KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEV = [
    ("Cumhuriyet savcısı soruşturmayı kim yapar?", "Savcı bizzat yapar.", "5271", "Madde 161",
     "CEZA MUHAKEMESİ KANUNU"),
    ("İşe iade davası açan işçi ne yapar?", "İşverene başvurur.", "4857", "Madde 21", "İŞ KANUNU"),
    ("Ortak gidere katılmayan kat maliki ne öder?", "Gecikme tazminatı öder.", "634",
     "Geçici Madde 1", "KAT MÜLKİYETİ KANUNU"),
]


def _ortam(tmp_path):
    korpus = _korpus_yaz(tmp_path)
    idx = str(tmp_path / "indeks")
    Retriever.kur(korpus, idx, gomucu=_sahte_gomucu)
    veri = tmp_path / "dev.jsonl"
    veri.write_text("".join(json.dumps(
        {"messages": [{"role": "user", "content": s}, {"role": "assistant", "content": c}],
         "kanun_no": kn, "madde_no": mn, "kanun_adi": ka}, ensure_ascii=False) + "\n"
        for s, c, kn, mn, ka in DEV), encoding="utf-8")
    retr = Retriever.yukle(idx, gomucu=_sahte_gomucu)
    ayar = bd.Ayar(seed=3407, n=3, harness_k=2, rrf_k=10, max_chunk_chars=900, harness_no_gold=False)
    return str(veri), korpus, retr, ayar


def _dondur_yaz(tmp_path, ad="baglam.json"):
    veri, madde, retr, ayar = _ortam(tmp_path)
    yol = str(tmp_path / ad)
    sha = bd.yaz(bd.dondur(veri, madde, retr, ayar, indeks="indeks"), yol)
    return yol, sha, veri, madde, retr, ayar


def test_dondur_iki_kez_bayt_bayt_ayni_dosya(tmp_path):
    veri, madde, retr, ayar = _ortam(tmp_path)
    a, b = str(tmp_path / "a.json"), str(tmp_path / "b.json")
    sha_a = bd.yaz(bd.dondur(veri, madde, retr, ayar, indeks="indeks"), a)
    sha_b = bd.yaz(bd.dondur(veri, madde, retr, ayar, indeks="indeks"), b)
    assert open(a, "rb").read() == open(b, "rb").read()
    assert sha_a == sha_b == bd.sha256_dosya(a)
    assert not os.path.exists(a + ".part")


def test_donmus_baglam_canli_getirme_ile_ayni_baglami_ve_izi_verir(tmp_path):
    yol, sha, veri, madde, retr, ayar = _dondur_yaz(tmp_path)
    kalemler = bd.oku(yol, ayar, veri_sha256=bd.sha256_dosya(veri))

    rows = [json.loads(l) for l in open(veri, encoding="utf-8")]
    canli, _ = geg.ornekle(rows, geg.load_madde_index(madde), ayar.seed, ayar.n)
    assert [k["soru"] for k in kalemler] == [s for _, s, _ in canli]
    for kalem, (rec, soru, src) in zip(kalemler, canli):
        blok, iz = geg.harness_baglami(rec, soru, retr, ayar)
        assert kalem["sources_block"] == blok
        assert kalem["referans"] == src
        assert {k: v for k, v in kalem["harness"].items() if k != "donmus_baglam"} == iz
        assert kalem["harness"]["donmus_baglam"] == sha
        assert (kalem["kanun_no"], kalem["madde_no"]) == (rec["kanun_no"], rec["madde_no"])


@pytest.mark.parametrize("alan,deger", [
    ("seed", 3408), ("n", 2), ("harness_k", 5), ("rrf_k", 60), ("max_chunk_chars", 0),
    ("harness_no_gold", True),
])
def test_donmus_baglam_parametre_uyusmazliginda_durur(tmp_path, alan, deger):
    yol, _, veri, _, _, ayar = _dondur_yaz(tmp_path)
    with pytest.raises(SystemExit, match=alan):
        bd.oku(yol, replace(ayar, **{alan: deger}), veri_sha256=bd.sha256_dosya(veri))


def test_donmus_baglam_soru_dosyasi_degistiyse_durur(tmp_path):
    yol, _, _, _, _, ayar = _dondur_yaz(tmp_path)
    with pytest.raises(SystemExit, match="veri_sha256"):
        bd.oku(yol, ayar, veri_sha256="0" * 64)


@pytest.mark.parametrize("bozma", ["eksik", "yinelenen"])
def test_donmus_baglam_eksik_ya_da_yinelenen_kalemde_durur(tmp_path, bozma):
    yol, _, veri, _, _, ayar = _dondur_yaz(tmp_path)
    d = json.load(open(yol, encoding="utf-8"))
    if bozma == "eksik":
        d["kalemler"].pop()
    else:
        d["kalemler"][2] = dict(d["kalemler"][1])
    json.dump(d, open(yol, "w", encoding="utf-8"), ensure_ascii=False)
    with pytest.raises(SystemExit, match="kalem"):
        bd.oku(yol, ayar, veri_sha256=bd.sha256_dosya(veri))


def test_gen_eval_donmus_baglam_canli_getirme_bayraklariyla_birlikte_verilemez(tmp_path):
    """Dondurulmuş bağlamla canlı getirme aynı koşuda olamaz — hangisinin kullanıldığı belirsizleşir.
    Kontrol model/sunucu açılmadan önce yapılır."""
    yol, _, veri, _, _, _ = _dondur_yaz(tmp_path)
    r = subprocess.run(
        [sys.executable, os.path.join(_KOK, "scripts/olcum_uretim/uretim/gen_eval_grounded.py"),
         "--donmus-baglam", yol, "--harness-indeks", str(tmp_path / "indeks"), "--data", veri,
         "--label", "x", "--out-dir", str(tmp_path / "out"), "--server-url", "http://127.0.0.1:9"],
        capture_output=True, text=True, cwd=_KOK)
    assert r.returncode != 0
    assert "birlikte verilemez" in r.stdout + r.stderr


def test_gen_eval_iceri_aktarilinca_torch_ve_unsloth_yuklenmez():
    """Kiralık kartta üretim yalnız HTTP taşıyıcısıyla koşar (ADR-0102): küçük sunucu imajında torch ve
    unsloth yok. Model yükleme yolu (dizüstü) bu paketleri kendi fonksiyonunda içe aktarır."""
    kod = ("import sys; sys.path.insert(0, 'scripts/olcum_uretim/uretim'); import gen_eval_grounded; "
           "print('torch' in sys.modules, 'unsloth' in sys.modules)")
    r = subprocess.run([sys.executable, "-c", kod], capture_output=True, text=True, cwd=_KOK)
    assert r.returncode == 0, r.stderr[-800:]
    assert r.stdout.strip().splitlines()[-1] == "False False"
