"""Belge katmanının kapı testleri (plan Görev 13).

⚠️ Neden test: doküman katmanı 2026-09-06'da silindi ve geriye ONLARCA kırık işaretçi kaldı
(`ROADMAP.md` 10 yerde, `TODO.md` 4 yerde…). Gözle taramak bunu kaçırır; döngü kaçırmaz.
⛔ `docs/record/**` ve `docs/adr/**` KAPSAM DIŞI — onlar tarihsel kayıttır, "o gün şu belge
şunu diyordu" bilgisini taşırlar ve kırık link onarımında bile DEĞİŞTİRİLMEZ.
"""
import pathlib
import re

KOK = pathlib.Path(__file__).resolve().parents[2]
# Canlı belgeler — tarihsel kayıt (docs/record, docs/adr) ve planlar hariç.
CANLI = ["CLAUDE.md", "README.md", "docs/README.tr.md", "MODEL_CARD.md",
         "docs/README.md", "docs/PRODUCT.md", "docs/ROADMAP_v1.md", "docs/MIMARI.md",
         "docs/YENIDEN_URETIM.md", "docs/YAYIN_YOL_HARITASI.md", "docs/EGITIM_ORTAMI.md"]
# Markdown bağlantısı; http(s), mailto ve saf çapa (#…) atlanır.
_LINK = re.compile(r"\[[^\]]*\]\((?!https?://|mailto:|#)([^)\s]+)\)")


def _kirik_baglantilar(belge: pathlib.Path) -> list[str]:
    kirik = []
    for hedef in _LINK.findall(belge.read_text(encoding="utf-8")):
        yol = (belge.parent / hedef.split("#", 1)[0]).resolve()
        if not yol.exists():
            kirik.append(hedef)
    return kirik


def test_canli_belgelerde_kirik_baglanti_yok():
    rapor = {}
    for ad in CANLI:
        p = KOK / ad
        if not p.exists():
            rapor[ad] = ["BELGENİN KENDİSİ YOK"]
            continue
        if kirik := _kirik_baglantilar(p):
            rapor[ad] = kirik
    assert not rapor, "kırık bağlantılar:\n" + "\n".join(
        f"  {a}: {', '.join(k)}" for a, k in rapor.items())


def test_uc_belge_de_var():
    """Faz 3'ün varlık sebebi: bu üçü 2026-09-06'da silinmişti ve yerine hiçbir şey yoktu."""
    for ad in ("docs/PRODUCT.md", "docs/ROADMAP_v1.md", "docs/MIMARI.md"):
        assert (KOK / ad).exists(), f"{ad} yok"


def test_mimari_her_urun_modulunu_var_olan_dosyaya_baglıyor():
    """MIMARI.md'nin ürün tablosu gerçek dosyaları göstermeli — kutu ≠ niyet."""
    metin = (KOK / "docs" / "MIMARI.md").read_text(encoding="utf-8")
    for alt, modul in (("cekirdek", "istem.py"), ("cekirdek", "tipler.py"), ("cekirdek", "terazi.py"),
                       ("cekirdek", "servis.py"), ("arayuz", "cli.py"), ("arayuz", "tui.py")):
        assert modul in metin, f"MIMARI.md {modul}'yi anmıyor"
        assert (KOK / "hakhukuk" / alt / modul).exists(), f"hakhukuk/{alt}/{modul} yok"


def test_build_system_license_bicimiyle_TUTARLI():
    """`pyproject.toml` PEP 639 dize lisansı kullanıyorsa setuptools>=77 İSTEMELİ.

    ⚠️ Ölçüldü 2026-09-11: dosya `license = "Apache-2.0"` (PEP 639 dize biçimi) yazıyor ama
    `build-system.requires` yalnız `setuptools>=68` diyordu. Kurulu setuptools **70.2.0** o
    biçimi REDDEDİYOR:
        configuration error: `project.license` must be valid exactly by one definition

    Bugün `pip install -e .` çalışıyor çünkü **build yalıtımı** pip'e en yeni setuptools'u
    çektiriyor ve o biçimi anlıyor. Yalıtım kapatılırsa (`--no-build-isolation`, CI'da ya da
    çevrimdışı kurulumda yaygın) kurulum **patlar** ve `hakhukuk-api` gibi giriş noktaları
    hiç oluşmaz — 2026-09-11'de tam olarak bu görüldü (açık kusur 28).

    Bu test bir KAPI: beyan edilen gereksinim, kullanılan biçimi karşılamalı.
    """
    import re
    import tomllib
    kok = __import__("pathlib").Path(__file__).resolve().parents[2]
    veri = tomllib.loads((kok / "pyproject.toml").read_text(encoding="utf-8"))
    lisans = veri["project"]["license"]
    if not isinstance(lisans, str):
        return  # tablo biçimi (`{text = …}`) eski setuptools ile de çalışır
    gerekli = veri["build-system"]["requires"]
    st = [r for r in gerekli if r.replace(" ", "").startswith("setuptools")]
    assert st, f"build-system.requires setuptools taşımıyor: {gerekli}"
    eslesme = re.search(r">=\s*(\d+)", st[0])
    assert eslesme, f"setuptools sürüm alt sınırı yok: {st[0]}"
    assert int(eslesme.group(1)) >= 77, (
        f"`license` PEP 639 dize biçiminde ({lisans!r}) ama build-system "
        f"{st[0]!r} istiyor; PEP 639 dize lisansı setuptools>=77 ister. "
        "Yalıtımsız kurulumda metadata üretimi PATLAR.")
