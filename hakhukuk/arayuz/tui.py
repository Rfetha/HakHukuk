"""Tek ekranlı terminal arayüzü. answer() üstünde İNCE KABUK — kendi mantığı YOKTUR.

⚠️ Sınıflandırma/atıf mantığı buraya sızarsa iki yerde bakım olur ve ikisi sessizce
ayrışır (bkz. istem sürüklenmesi, S18: aynı metin beş dosyada, ikisi farklıydı).
tests/test_tui.py bunu bir KAPI olarak sınar.
"""
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Footer, Header, Input, Static

from hakhukuk.arayuz.cli import bicimle, kapsam_satiri
from hakhukuk.cekirdek.servis import answer
from hakhukuk.cekirdek.tipler import Durum

ROZET = {
    Durum.CEVAP: "🟢 CEVAP",
    Durum.CEKINCELI: "🟡 ÇEKİNCELİ CEVAP — doğrudan hüküm bulunamadı",
    Durum.SUSKUNLUK: "⚪ SUSKUNLUK — dayanak bulunamadı",
    Durum.KESIK: "🟠 KESİK — üretim bütçesi bitti, cevap YARIM",
    # ⛔ KESİK'ten AYRI (ADR-0076): cümle tam, DAYANAĞI eksik olabilir.
    Durum.ARAMA_TUKENDI: "🔵 ARAMA TÜKENDİ — arama sınırına dayanıldı, dayanak EKSİK olabilir",
    # ⛔ SUSKUNLUK'tan AYRI (ADR-0081): orada arandı ve bulunamadı, burada HİÇ ARANMADI.
    Durum.BOS_SORGU: "⚫ BOŞ SORU — soru yazılmadı, arama yapılmadı",
}


class HakHukukTUI(App):
    TITLE = "HakHukuk"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(
            "Hukuki sorunuzu yazıp Enter'a basın.\n" + kapsam_satiri(), id="yonerge")
        yield Input(placeholder="Hukuki sorunuzu yazın…", id="soru")
        yield VerticalScroll(Static("", id="cikti"))
        yield Footer()

    # ⚠️ DOM'a dokunan HER ŞEY bu iki metotta — çalışan iş parçacığı onları yalnız
    # `call_from_thread` ile çağırır (`query_one` da ana döngüde kalsın diye).
    def _ciz(self, metin: str) -> None:
        self.query_one("#cikti", Static).update(metin)

    def _mesgul(self, mesgul: bool) -> None:
        girdi = self.query_one("#soru", Input)
        girdi.disabled = mesgul
        girdi.placeholder = ("⏳ cevap bekleniyor…" if mesgul
                             else "Hukuki sorunuzu yazın…")
        if not mesgul:
            girdi.focus()

    def on_input_submitted(self, olay: Input.Submitted) -> None:
        if self.query_one("#soru", Input).disabled:
            return          # koşu sürüyor — ikinci Enter YOK SAYILIR
        self._mesgul(True)
        self._ciz("⏳ kaynaklar taranıyor…")
        # ⚠️ İki çalışan aynı anda koşarsa ekranı SON BİTEN kazanır: yavaş biten 1. soruysa
        # vatandaş 2. sorusunun altında 1. sorunun cevabını görür ve hiçbir hata çıkmaz.
        # `servis`'in modül düzeyi `_retriever`/`_araclar` tekilleri de KİLİTSİZ (api.py
        # aynı riski `_KILIT` ile kapatıyor). İki kapı birden: girdi yukarıda devre dışı
        # bırakıldı, `exclusive` de önceki çalışanı iptal eder.
        self.run_worker(lambda: self._soruyu_yanitla(olay.value),
                        thread=True, exclusive=True, group="sorgu")

    # ⚠️ kusur 3: `answer()` ağ + retriever I/O yapar, olay döngüsünde çağrılırsa
    # arayüz 30-60 sn DONAR; bu yüzden çalışan iş parçacığında koşar (thread=True).
    def _soruyu_yanitla(self, soru: str) -> None:
        try:
            try:
                c = answer(soru)
            except Exception as hata:
                # ⚠️ Savunmacı fazlalık DEĞİL: sunucunun kapalı olması (llama-server elle
                # açılıyor) ya da indeksin yüklenememesi bu üründe OLASI bir senaryodur —
                # ekran sessizce donuk kalırsa boş ekrandan ayırt edilemez.
                self.call_from_thread(self._ciz, f"⛔ Hata: {hata}")
                return
            # ⛔ Kendi sunum dizesi KURULMAZ (kusur 17): tek fark rozet sözlüğüdür ve o da
            # `bicimle()`'ye PARAMETRE olarak geçer. Buradan bir `f"…"` kurmak, birinci
            # turun iki sızıntısını (iskele işareti · kapsam satırı) yeniden açar.
            self.call_from_thread(self._ciz, bicimle(c, rozet=ROZET))
        finally:
            # ⚠️ Hata yolunda da açılmalı: açılmazsa tek bir hata arayüzü KALICI kilitler.
            self.call_from_thread(self._mesgul, False)


def main() -> None:
    HakHukukTUI().run()


# ⚠️ Bu blok olmadan `python -m hakhukuk.arayuz.tui` modülü içe aktarıp SESSİZCE çıkıyordu:
# `main()` tanımlıydı ama çağrılmıyordu. `cli.py`'de vardı, burada yoktu ve hiçbir test
# yakalamadı — kaynak denetimi mantığın sızmadığına bakar, programın çalıştığına değil.
# Gözle doğrulama kapısında yakalandı (2026-09-09); `tests/test_tui.py` artık çiviliyor.
if __name__ == "__main__":
    main()
