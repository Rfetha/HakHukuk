import hashlib
import json
import os
import shutil

import numpy as np
import pytest
from retriever import ONEK, Retriever, rrf_birlestir  # noqa: E402


KORPUS = [
    {"kanun_no": "5271", "kanun_adi": "CEZA MUHAKEMESİ KANUNU", "madde_no": "Madde 161",
     "text": "Cumhuriyet savcısı soruşturmayı bizzat yapar."},
    {"kanun_no": "4857", "kanun_adi": "İŞ KANUNU", "madde_no": "Madde 21",
     "text": "İşe iade davası açan işçi işverene başvurur."},
    {"kanun_no": "634", "kanun_adi": "KAT MÜLKİYETİ KANUNU", "madde_no": "Geçici Madde 1",
     "text": "Ortak giderlere katılmayan kat maliki gecikme tazminatı öder."},
]


def _korpus_yaz(tmp_path):
    yol = tmp_path / "korpus.jsonl"
    yol.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in KORPUS) + "\n",
                   encoding="utf-8")
    return str(yol)


def _sahte_gomucu(metinler):
    """Deterministik sahte gömme: karakter histogramı. Gerçek model indirmez."""
    M = np.zeros((len(metinler), 32), dtype=np.float32)
    for i, m in enumerate(metinler):
        for ch in m.lower():
            M[i, ord(ch) % 32] += 1.0
    M /= np.linalg.norm(M, axis=1, keepdims=True) + 1e-9
    return M


def test_kur_yukle_getir_tur_donusu(tmp_path):
    korpus = _korpus_yaz(tmp_path)
    idx = str(tmp_path / "indeks")
    Retriever.kur(korpus, idx, gomucu=_sahte_gomucu)
    r = Retriever.yukle(idx, gomucu=_sahte_gomucu)
    sonuc = r.getir("Cumhuriyet savcısı soruşturmayı bizzat yapar", k=2)
    assert len(sonuc) == 2
    assert sonuc[0]["madde_no"] == "Madde 161"
    assert sonuc[0]["sira"] == 0 and sonuc[1]["sira"] == 1
    assert sonuc[0]["skor"] >= sonuc[1]["skor"]


def test_getir_k_korpustan_buyukse_korpusla_sinirli(tmp_path):
    korpus = _korpus_yaz(tmp_path)
    idx = str(tmp_path / "indeks")
    Retriever.kur(korpus, idx, gomucu=_sahte_gomucu)
    assert len(Retriever.yukle(idx, gomucu=_sahte_gomucu).getir("işçi", k=99)) == len(KORPUS)


def test_getir_tam_madde_metnini_dondurur_kirpmaz(tmp_path):
    # ⚠️ ADR-0054/K2: 900 karakter kırpması retriever'da DEĞİL, bağlam modele
    # verilirken uygulanır. Retriever kırparsa kural sessizce ihlal edilir.
    uzun = dict(KORPUS[0], text="A" * 3000)
    yol = tmp_path / "uzun.jsonl"
    yol.write_text(json.dumps(uzun, ensure_ascii=False) + "\n", encoding="utf-8")
    idx = str(tmp_path / "indeks")
    Retriever.kur(str(yol), idx, gomucu=_sahte_gomucu)
    assert len(Retriever.yukle(idx, gomucu=_sahte_gomucu).getir("A", k=1)[0]["text"]) == 3000


def test_yukle_korpus_degistiyse_erken_patlar(tmp_path):
    # ⚠️ Bayat indeks SESSİZ yanlışlıktır: sorgular eski korpusa göre cevaplanır,
    # hiçbir yerde hata çıkmaz.
    korpus = _korpus_yaz(tmp_path)
    idx = str(tmp_path / "indeks")
    Retriever.kur(korpus, idx, gomucu=_sahte_gomucu)
    with open(korpus, "a", encoding="utf-8") as f:
        f.write(json.dumps(KORPUS[0], ensure_ascii=False) + "\n")
    # ⚠️ ADIM 6.1 kural 3: (b) adayı VAR ama hash tutmuyorsa bu mesaj KORUNUR —
    # (c)'nin "denenen yollar" mesajına sessizce düşmemeli.
    with pytest.raises(SystemExit, match="DEĞİŞTİ"):
        Retriever.yukle(idx)


def test_kunye_olcum_degismezlerini_yazar(tmp_path):
    korpus = _korpus_yaz(tmp_path)
    idx = str(tmp_path / "indeks")
    Retriever.kur(korpus, idx, gomucu=_sahte_gomucu, model_adi="sahte/model")
    k = json.load(open(f"{idx}/KUNYE.json", encoding="utf-8"))
    assert k["model"] == "sahte/model"
    assert k["n"] == len(KORPUS)
    assert k["yontem"] == "hibrit_bm25+yogun_rrf"
    assert k["chunk"] == "tam madde (ADR-0054/K2)"


def test_rrf_iki_kaynakta_da_ustte_olan_kazanir():
    a = np.array([9.0, 8.0, 1.0])
    b = np.array([1.0, 9.0, 8.0])
    assert int(np.argmax(rrf_birlestir([a, b], rrf_k=60))) == 1


# ── Taşınabilirlik kilidi (G8 Adım 1b) ───────────────────────────────────────
# ⚠️ Bu blok bir ÜRÜN hatasını çiviler: künye MUTLAK YOL + `mtime` damgalıyordu.
# `git clone` sonrası mtime checkout zamanı olur ⇒ retriever HER MAKİNEDE SystemExit
# veriyordu. Sessiz değil ama ölümcül: indeks 83 MB ve yeniden kurmak CPU'da ~2 sa 45 dk.

def test_kunye_korpus_yolu_gorelidir_mutlak_degil(tmp_path):
    korpus = _korpus_yaz(tmp_path)
    idx = str(tmp_path / "indeks")
    Retriever.kur(korpus, idx, gomucu=_sahte_gomucu)
    imza = json.load(open(f"{idx}/KUNYE.json", encoding="utf-8"))["korpus"]
    assert not os.path.isabs(imza["yol"])
    assert "mtime" not in imza
    assert imza["sha256"] == hashlib.sha256(open(korpus, "rb").read()).hexdigest()


def test_yukle_indeks_baska_dizine_kopyalaninca_calisir(tmp_path):
    # verify ölçütünün küçük ölçekli hâli: ağaç OLDUĞU GİBİ başka yere kopyalanır.
    korpus = _korpus_yaz(tmp_path)
    kaynak = tmp_path / "repo"
    kaynak.mkdir()
    os.rename(korpus, kaynak / "korpus.jsonl")
    idx = str(kaynak / "indeks")
    Retriever.kur(str(kaynak / "korpus.jsonl"), idx, gomucu=_sahte_gomucu)

    hedef = tmp_path / "baska" / "repo"
    shutil.copytree(kaynak, hedef)
    r = Retriever.yukle(str(hedef / "indeks"), gomucu=_sahte_gomucu)
    assert r.getir("Cumhuriyet savcısı", k=1)[0]["madde_no"] == "Madde 161"


def test_yukle_icerigi_degismemis_korpusa_yanlis_alarm_vermez(tmp_path):
    # ⚠️ 2026-08-06'da BİREBİR bu oldu: `git checkout` mtime'ı değiştirdi, bayt ve
    # içerik aynıydı, retriever "korpus DEĞİŞTİ" dedi. Vekil yanlıştı, indeks değil.
    korpus = _korpus_yaz(tmp_path)
    idx = str(tmp_path / "indeks")
    Retriever.kur(korpus, idx, gomucu=_sahte_gomucu)
    os.utime(korpus, (0, 0))
    assert Retriever.yukle(idx, gomucu=_sahte_gomucu).getir("işçi", k=1)


def test_yukle_onek_sozlesmesi_uymazsa_patlar(tmp_path):
    # Önek DÜŞERSE hata çıkmaz, yalnız recall düşer — sessiz yanlışlık sınıfı.
    korpus = _korpus_yaz(tmp_path)
    idx = str(tmp_path / "indeks")
    Retriever.kur(korpus, idx, gomucu=_sahte_gomucu)
    assert json.load(open(f"{idx}/KUNYE.json", encoding="utf-8"))["onek"] == ONEK
    _kunye_yaz(idx, onek={"sorgu": "query: ", "belge": "passage: "})
    with pytest.raises(SystemExit, match="önek"):
        Retriever.yukle(idx, gomucu=_sahte_gomucu)


def test_yukle_eski_bicim_kunyeyi_acikca_reddeder(tmp_path):
    # data/index/mevzuat_bge_m3/ bugün bu biçimde; KeyError yerine okunur hüküm.
    korpus = _korpus_yaz(tmp_path)
    idx = str(tmp_path / "indeks")
    Retriever.kur(korpus, idx, gomucu=_sahte_gomucu)
    _kunye_yaz(idx, korpus={"yol": os.path.abspath(korpus), "bayt": 1, "mtime": 2})
    with pytest.raises(SystemExit, match="eski biçim"):
        Retriever.yukle(idx, gomucu=_sahte_gomucu)


# ── Korpus KİMLİKLE bulunur (ADIM 6.1) ───────────────────────────────────────
# ⚠️ Kusur 32: künye korpusu indeks dizinine GÖRELİ tutuyordu, indeks HF'ten dataset
# olarak inince (G8) indeks dizininin iki üstünde `corpus/` OLMAYACAK. Çözüm merdiveni:
# (a) HAKHUKUK_KORPUS ortam değişkeni · (b) künyedeki göreli yol (bugünkü davranış) ·
# (c) bilinen köklerde sha256 ile arama. Her basamakta kimlik (sha256) doğrulanır.

def test_yukle_ortam_degiskeniyle_yalitik_indekste_calisir(tmp_path, monkeypatch):
    # Kırmızı test: indeks `corpus/` komşuluğu OLMAYAN bir dizine taşınır, korpus
    # bambaşka bir yere konur, yalnız HAKHUKUK_KORPUS ile gösterilir.
    (tmp_path / "kaynak").mkdir()
    korpus = _korpus_yaz(tmp_path / "kaynak")
    idx_kaynak = str(tmp_path / "kaynak" / "indeks")
    Retriever.kur(korpus, idx_kaynak, gomucu=_sahte_gomucu)

    yalitik = tmp_path / "yalitik" / "indeks"
    shutil.copytree(idx_kaynak, yalitik)
    korpus_baska_yer = tmp_path / "hic-ilgisiz" / "yer" / "korpus.jsonl"
    korpus_baska_yer.parent.mkdir(parents=True)
    shutil.copy(korpus, korpus_baska_yer)

    monkeypatch.setenv("HAKHUKUK_KORPUS", str(korpus_baska_yer))
    r = Retriever.yukle(str(yalitik), gomucu=_sahte_gomucu)
    assert r.getir("Cumhuriyet savcısı", k=1)[0]["madde_no"] == "Madde 161"


def test_yukle_c_basamagi_indeks_ustundeki_corpus_dizininde_bulur(tmp_path):
    # (c) basamağı: env YOK, (b) göreli yolu ÇÖZÜLEMİYOR (indeksin yanında corpus/
    # yok), ama kimliği tutan bir dosya `<indeks_dizini>/../corpus/` altında duruyor.
    (tmp_path / "kaynak").mkdir()
    korpus = _korpus_yaz(tmp_path / "kaynak")
    idx_kaynak = str(tmp_path / "kaynak" / "indeks")
    Retriever.kur(korpus, idx_kaynak, gomucu=_sahte_gomucu)

    hedef_indeks = tmp_path / "yeni" / "indeks"
    hedef_indeks.parent.mkdir(parents=True)
    shutil.copytree(idx_kaynak, hedef_indeks)
    hedef_corpus_dizin = tmp_path / "yeni" / "corpus"
    hedef_corpus_dizin.mkdir()
    shutil.copy(korpus, hedef_corpus_dizin / "mevzuat_maddeler.jsonl")

    r = Retriever.yukle(str(hedef_indeks), gomucu=_sahte_gomucu)
    assert r.getir("Cumhuriyet savcısı", k=1)[0]["madde_no"] == "Madde 161"


def test_yukle_icerigi_farkli_aday_kullanilmaz_denenenler_listelenir(tmp_path):
    # Kimlik kapısı: bir aday VAR ama içeriği (dolayısıyla sha256'sı) farklı →
    # kullanılmaz, arama sürer; hiçbir aday tutmazsa SystemExit denenen yolları listeler.
    (tmp_path / "kaynak").mkdir()
    korpus = _korpus_yaz(tmp_path / "kaynak")
    idx_kaynak = str(tmp_path / "kaynak" / "indeks")
    Retriever.kur(korpus, idx_kaynak, gomucu=_sahte_gomucu)

    hedef_indeks = tmp_path / "yeni" / "indeks"
    hedef_indeks.parent.mkdir(parents=True)
    shutil.copytree(idx_kaynak, hedef_indeks)
    yanlis_dizin = tmp_path / "yeni" / "corpus"
    yanlis_dizin.mkdir()
    (yanlis_dizin / "mevzuat_maddeler.jsonl").write_text("başka içerik\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="denenen"):
        Retriever.yukle(str(hedef_indeks), gomucu=_sahte_gomucu)


def test_yukle_bugunku_repo_yerlesimi_b_basamagi_degismeden_calisir(tmp_path):
    # Gerileme: bugünkü repo yerleşimi (künyedeki göreli yol, basamak (b)) hâlâ
    # ortam değişkeni ya da arama gerekmeden doğrudan çözülüp çalışmalı.
    korpus = _korpus_yaz(tmp_path)
    idx = str(tmp_path / "indeks")
    Retriever.kur(korpus, idx, gomucu=_sahte_gomucu)
    r = Retriever.yukle(idx, gomucu=_sahte_gomucu)
    assert r.getir("işçi", k=1)[0]["madde_no"] == "Madde 21"


def _kunye_yaz(idx, **alanlar):
    yol = f"{idx}/KUNYE.json"
    k = json.load(open(yol, encoding="utf-8"))
    k.update(alanlar)
    json.dump(k, open(yol, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
