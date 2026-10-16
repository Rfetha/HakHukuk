"""TUI'nin İNCE KABUK olduğunu sınayan kapı (plan Görev 12)."""
import inspect

from hakhukuk.arayuz import tui


def test_tui_kendi_mantigi_yok_yalnizca_answer_cagirir():
    """TUI ince kabuktur. Sınıflandırma/atıf mantığı BURAYA sızarsa iki yerde bakım olur."""
    kaynak = inspect.getsource(tui)
    for yasak in ("REJECT_RE", "re.compile", "siniflandir(", "_getir(", "_uret("):
        assert yasak not in kaynak, f"TUI'ye mantık sızmış: {yasak}"
    assert "answer(" in kaynak


def test_sorumluluk_ibaresi_TEK_kaynaktan_geliyor():
    """S18'in dersi: aynı metin iki yerde durursa sessizce ayrışır.

    ⚠️ GÜNCELLENDİ 2026-09-11 (kusur 17): TUI ibareyi artık AYRICA import etmiyor —
    sunumun tamamını `cli.bicimle()`'den alıyor ve ibare oradan geliyor. Sınanan şart
    değişmedi: ibare TUI ekranına TEK kaynaktan ulaşmalı.
    """
    from hakhukuk.arayuz import cli
    from hakhukuk.cekirdek.tipler import Cevap, Durum
    assert tui.bicimle is cli.bicimle
    bos = Cevap(metin="x", durum=Durum.CEVAP, atiflar=(), kaynaklar=())
    assert cli.SORUMLULUK_IBARESI in tui.bicimle(bos, rozet=tui.ROZET)


def test_modul_calistirilinca_uygulama_GERCEKTEN_baslar(monkeypatch):
    """`python -m hakhukuk.arayuz.tui` HİÇBİR ŞEY YAPMIYORDU — gözle yakalandı 2026-09-09.

    `main()` tanımlıydı ama `if __name__ == "__main__":` bloğu yoktu; modül içe aktarılıp
    sessizce çıkıyordu. `cli.py`'de bu blok vardı, TUI'de yoktu.

    Yukarıdaki kaynak-denetimi testi bunu YAKALAYAMAZ: o, mantığın sızmadığına bakar,
    programın çalıştığına değil. Ürün yüzünün insan gözüyle hiç görülmemiş olması, kusurun
    aylarca fark edilmemesinin sebebidir — bu test o boşluğu kapatıyor.
    """
    import runpy

    from textual.app import App

    baslatildi = []
    monkeypatch.setattr(App, "run", lambda self, *a, **k: baslatildi.append(type(self).__name__))
    runpy.run_module("hakhukuk.arayuz.tui", run_name="__main__")
    assert baslatildi == ["HakHukukTUI"], "modül koşturuldu ama uygulama başlamadı"
