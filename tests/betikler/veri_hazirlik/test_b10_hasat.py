import json
import sys
from b10_hasat import _anahtar, _baglam, _soru, kayit, sizinti_suz

DEV_GERCEK = "data/eval/dev/core_hard.jsonl"


def _raft(soru, kanun, madde):
    """`raft_scrubbed` grounded satırı — system·user·assistant, user'da KAYNAKLAR:/SORU:."""
    return {
        "messages": [
            {"role": "system", "content": "sys"},
            {"role": "user", "content": f"KAYNAKLAR:\n[KAYNAK 1]\nX\n\nSORU: {soru}"},
            {"role": "assistant", "content": "1) İlgili kaynak KAYNAK 1'dir. 3) Sonuç."},
        ],
        "slice": "grounded", "gold_kanun_no": kanun, "gold_madde_no": madde,
    }


def _dev(tmp_path, ad, kalemler):
    p = tmp_path / ad
    p.write_text("\n".join(json.dumps(k, ensure_ascii=False) for k in kalemler), encoding="utf-8")
    return str(p)


def _dev_kalem(soru, kanun, madde, altin_cevap="Altın cevap. (X KANUNU, Madde 1)"):
    """GERÇEK DEV/CANON şekli — 2026-08-06'da `data/eval/{dev,canon}/core_hard.jsonl`'e karşı ölçüldü.

    🚨 `messages` = **[user, assistant]** ve user mesajı **DOĞRUDAN sorudur**: ne `system` rolü,
    ne `KAYNAKLAR:` bloğu, ne `SORU:` işareti vardır (ikisinin de sayımı 0/80 ve 0/40).
    Görev 3 briefinin bu yardımcısı `SORU:` işaretli bir user mesajı uyduruyordu; o kurgu
    testleri yeşil tutarken `sizinti_suz`'ü gerçek veride ilk kalemde `ValueError`'a düşürüyordu.
    Fixture gerçek şekli taşımazsa test kusuru kilitler.
    """
    return {"messages": [{"role": "user", "content": soru},
                         {"role": "assistant", "content": altin_cevap}],
            "kanun_adi": "X KANUNU", "kanun_no": kanun, "madde_no": madde,
            "_complexity": 20, "_src_len": 1000, "_set": "core_hard"}


def test_sizinti_suz_dev_sorusunu_atar(tmp_path):
    dev = _dev(tmp_path, "dev.jsonl",
               [_dev_kalem("Vasiliğe atanma kararı kesinleşince ne yapılmalı?", "4721", "MADDE 413")])
    satirlar = [_raft("Vasiliğe atanma kararı kesinleşince ne yapılmalı?", "9999", "MADDE 1"),
                _raft("Kira artışı nasıl hesaplanır?", "6098", "MADDE 344")]
    kalan = sizinti_suz(satirlar, [dev])
    assert len(kalan) == 1
    assert "Kira" in kalan[0]["messages"][1]["content"]


def test_sizinti_suz_dev_altin_MADDESINI_de_atar(tmp_path):
    # Soru farklı ama altın madde DEV'in altın maddesi → sızıntı (madde düzeyinde 67/70 örtüşüyor)
    dev = _dev(tmp_path, "dev.jsonl", [_dev_kalem("başka bir soru", "4721", "MADDE 413")])
    satirlar = [_raft("Tamamen farklı bir soru?", "4721", "Madde 413")]   # büyük/küçük harf farklı
    assert sizinti_suz(satirlar, [dev]) == []


def test_sizinti_suz_dev_kaleminde_soru_bulunamazsa_patlar(tmp_path):
    # 🚨 Sessiz-yanlışlık kapısı: `soru` alanı aranıp boş dönerse süzgeç NO-OP olur ve
    # sızıntı fark edilmeden eğitime girer. Boş soru = hata, atlama değil.
    dev = _dev(tmp_path, "dev.jsonl", [{"kanun_no": "4721", "madde_no": "MADDE 413"}])
    try:
        sizinti_suz([_raft("Soru?", "6098", "MADDE 344")], [dev])
    except ValueError as e:
        assert "soru" in str(e).lower()
    else:
        raise AssertionError("soru metni çıkarılamayan DEV kaleminde ValueError bekleniyordu")


def test_sizinti_suz_dev_altin_CEVABINI_okumaz(tmp_path):
    """CANON/DEV'den yalnız SORU metni + altın madde okunur; `assistant` içeriği okunmaz.

    Falsifiable: süzgeç yanlışlıkla tüm `messages`'ı tarasaydı, altın cevabın metnine eşit
    soruya sahip raft satırı da atılırdı. Sevk damgası: "CANON yalnız dışlama listesi".
    """
    altin = "Altın cevap metni burada. (X KANUNU, Madde 7)"
    dev = _dev(tmp_path, "dev.jsonl", [_dev_kalem("dev sorusu", "4721", "MADDE 413", altin)])
    kalan = sizinti_suz([_raft(altin, "6098", "MADDE 344")], [dev])
    assert len(kalan) == 1


def test_soru_gercek_DEV_semasindan_cikarilir():
    """🚨 Kusur regresyonu (2026-08-06): brief'in `_soru`'su gerçek DEV kaleminde patlıyordu.

    Gerçek dosyaya karşı koşar — kurgu fixture bu sınıfı yakalayamaz, çünkü kusurun kendisi
    fixture ile gerçek şekil arasındaki farktı.
    """
    kalemler = [json.loads(l) for l in open(DEV_GERCEK, encoding="utf-8") if l.strip()]
    assert kalemler, "DEV dosyası boş"
    for k in kalemler:
        s = _soru(k)                        # ValueError atarsa test düşer — istenen budur
        assert s == k["messages"][0]["content"].strip()
        assert s


def test_soru_baglam_blogu_var_ama_SORU_isareti_yoksa_patlar():
    # NO-OP süzgeç kapısı: bağlam bloğunun tamamı "soru" sayılırsa anahtar çöp olur,
    # hiçbir şey eşleşmez ve süzgeç sessizce hiçbir şey atmaz.
    bozuk = {"messages": [{"role": "user", "content": "KAYNAKLAR:\n[KAYNAK 1]\nX"}]}
    try:
        _soru(bozuk)
    except ValueError as e:
        assert "soru" in str(e).lower()
    else:
        raise AssertionError("bağlam bloğu var ama SORU: yokken ValueError bekleniyordu")


def test_anahtar_gecici_maddeyi_normal_maddeden_ayirir():
    assert _anahtar("634", "Geçici Madde 1") != _anahtar("634", "Madde 1")


def test_anahtar_turkce_buyuk_harf_farkini_yutmaz():
    """🚨 Kusur regresyonu: brief'in `.upper()` tabanlı `_anahtar`'ı bu ikisini AYRI sayıyordu.

    `'Geçici'.upper() == 'GEÇICI' != 'GEÇİCİ'` — külliyatta HER İKİ yazım da var
    (166 `Geçici Madde N` · 88 `GEÇİCİ MADDE N`). Ayrı sayılırlarsa sızıntı süzgeci o
    kalemleri kaçırır ve hiçbir yerde hata vermez.
    """
    assert _anahtar("634", "Geçici Madde 1") == _anahtar("634", "GEÇİCİ MADDE 1")
    assert _anahtar("5271", "Madde 161") == _anahtar("5271", "MADDE 161")


def test_kayit_semasi_tam():
    class G:
        text = "Verilen kaynaklarda bu konuyu düzenleyen madde bulunmuyor."
        finish_reason = "stop"; completion_tokens = 42; forced_close = False; reasoning_len = 10
    r = kayit(_raft("Soru?", "6098", "MADDE 344"), 7, G())
    assert r["tip"] == "m1_yeterli"
    assert r["mode"] == "data"
    assert r["id"] == "raft7"
    assert r["soru"] == "Soru?"
    assert r["chosen"].startswith("1) İlgili kaynak")
    assert r["rejected"].startswith("Verilen kaynaklarda")
    assert r["context_shown"].startswith("[KAYNAK 1]")
    assert set(r) >= {"id", "tip", "soru", "chosen", "rejected", "context_shown", "mode",
                      "gold_kanun_no", "gold_madde_no", "finish_reason", "completion_tokens",
                      "forced_close", "reasoning_len"}


def test_soru_ve_baglam_raft_user_mesajini_BIREBIR_geri_kurar():
    """Protokol sapması kapısı: `chosen` bu isteme karşı yazıldı; `rejected` de aynı isteme
    karşı üretilmeli. `build_messages(soru, sources_block=baglam)` raft user mesajını birebir
    geri kurmuyorsa çift tutarsızdır ve bu hiçbir yerde hata vermez (cp2_harvest dersi)."""
    from gen_eval_grounded import build_messages

    rec = _raft("Kira artışı nasıl hesaplanır?", "6098", "MADDE 344")
    m = build_messages(_soru(rec), sources_block=_baglam(rec))
    assert m[1]["content"] == rec["messages"][1]["content"]
