"""Araç katmanı — **KALDIRAÇ**'lar (ADR-0076).

🔒 **KAPI ↔ KALDIRAÇ ayrımı bağlayıcıdır.** Bu dosyada KALDIRAÇ'lar vardır: model
çağırabilir de çağırmayabilir de. **KAPI'lar buraya girmez** — atıf doğrulama, mülga
süzgeci ve durum sınıflandırma döngünün DIŞINDA, koşulsuz çalışır (`servis.py`).
Uydurulmuş madde numarasının **0/114** (DEV) ve **0/52** (donmuş TEST) olması oradan
geliyor; tool yapılırsa model çağırmayı unuttuğu an o garanti buharlaşır.

⛔ **Hiçbir araç LLM çağırmaz.** Deterministik kalırlar; model çağıran bir araç, ölçülmemiş
ikinci bir hata kaynağı olurdu. `tests/test_araclar.py` bunu bir KAPI olarak sınar.

🚨 **Bu katmanın gerekçesi ÖLÇÜLDÜ ve ÇÜRÜDÜ — burada yazılı durur (ADR-0076):**
isabetsizliğin **8/8**'inde ve aşırı-redin **4/4**'ünde altın madde **zaten bağlamdaydı**
⇒ sorun erişim değil **seçim**. Tek ölçülmüş hedef, altının hiç gelmediği **4/80**'lik
recall kaybıdır ve orada bile `ara` yalnız **deneyebilir**. Katman yine de konur, ama
gerekçesi **ürün yeteneğidir ve ÖLÇÜLMEMİŞTİR** ⇒ ⛔ kazancı yayımlanan **hiçbir sayıya
eklenmez**.
"""
import os
import sys

from hakhukuk.cekirdek.tipler import Kaynak, Yururluk

# ── scripts/ yol köprüsü ─────────────────────────────────────────────────────
_K = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "scripts")
sys.path[:0] = [_K, os.path.join(_K, "erisim_korpus", "atif")]
from madde_anahtar import madde_anahtari  # noqa: E402
# ⚠️ Ad çözümü TEK KAYNAK: yayımlanan sayıyı üreten doğrulayıcının ta kendisi.
# Kusur 18 onarımı (2026-09-11) burada kopyalanmış ikinci bir indekse çarpmıştı;
# tuzak 2.18 tam olarak budur — aynı ölçümün iki aleti sessizce ayrışır.
from atif_dogrula import _ad_adaylari, _dizin_kur  # noqa: E402


def _kaynak(kayit: dict, sira: int) -> Kaynak:
    return Kaynak(kanun_adi=kayit["kanun_adi"], kanun_no=str(kayit["kanun_no"]),
                  madde_no=kayit["madde_no"], metin=kayit["text"], sira=sira)


class Araclar:
    """Beş deterministik kaldıraç. Arayüz beş metot; korpus indeksi arkada gizli.

    `getir` verilmezse `ara` çalışmaz ve bunu **açıkça söyler** — sessiz boş liste,
    *"arama sonuç vermedi"* ile *"arama hiç çalışmadı"*yı vatandaş için aynı şeye çevirirdi.
    """

    def __init__(self, kayitlar, getir=None):
        self._getir = getir
        # Kimlik daima `madde_anahtari` ile: düz metin karşılaştırması korpusun %22'sinde
        # yanlış negatif veriyordu (`MADDE 21` ↔ `Madde 21`), ve `Geçici Madde 1` ile
        # `Madde 1` AYRI maddelerdir.
        self._indeks: dict = {}
        for r in kayitlar:
            self._indeks.setdefault(madde_anahtari(str(r["kanun_no"]), r["madde_no"]),
                                    []).append(r)
        self._dizin = _dizin_kur(kayitlar)

    # ── 1 · ara — TEK ölçülmüş hedefi olan araç (4/80 recall kaybı) ───────────
    def ara(self, sorgu: str, k: int = 10) -> tuple[Kaynak, ...]:
        if self._getir is None:
            raise RuntimeError(
                "[araclar] 🚫 `ara` çağrıldı ama retriever verilmedi — boş liste "
                "DÖNDÜRÜLMEZ: 'sonuç yok' ile 'arama çalışmadı' aynı şey değildir")
        ham = self._getir(sorgu, k, Yururluk.YALNIZ_YURURLUKTE)
        return tuple(_kaynak(h, i + 1) for i, h in enumerate(ham))

    # ── 2 · madde_getir ──────────────────────────────────────────────────────
    def madde_getir(self, kanun_no: str, madde_no: str) -> Kaynak | None:
        satirlar = self._indeks.get(madde_anahtari(str(kanun_no), madde_no))
        return _kaynak(satirlar[0], 1) if satirlar else None

    # ── 3 · madde_var_mi ─────────────────────────────────────────────────────
    def madde_var_mi(self, kanun_no: str, madde_no: str) -> bool:
        return madde_anahtari(str(kanun_no), madde_no) in self._indeks

    # ── 4 · kanun_bul ────────────────────────────────────────────────────────
    def kanun_bul(self, ad: str) -> tuple[tuple[str, str], ...]:
        """Ada uyan **BÜTÜN** kanunlar. ⛔ Tek numara dönmek yasak.

        🚨 Donmuş TEST'in dersi (2026-09-09): `İŞ KANUNU` hem **4857** (yürürlükte) hem
        **1475** (mülga) demektir; adayları alfabetik gezip ilkini seçen bir çözüm DOĞRU
        cevaba MÜLGA damgası vuruyordu. Aynı kusur burada tekrarlanmaz.

        ⚠️ Boş demet İKİ hâli birden anlatır: ad korpusta YOK **ya da** ad çözülemedi
        (`atif_dogrula` bu ikincisine `AYRISTIRILAMADI` der). Ayrımı buraya taşımak
        ADR-0076'nın araç imzasını değiştirirdi; taşınmadı — ama ikisinde de sessizce
        bir kanun **SEÇİLMEZ**, kusur 18'in kalıbı budur.
        """
        return tuple(sorted((no, self._dizin.adi.get(no, ""))
                            for no in _ad_adaylari(ad, self._dizin)))

    # ── 5 · yururlukte_mi ────────────────────────────────────────────────────
    def yururlukte_mi(self, kanun_no: str, madde_no: str) -> Yururluk | None:
        """`None` = madde YOK. ⚠️ *"yok"* ile *"mülga"* karıştırılmaz."""
        satirlar = self._indeks.get(madde_anahtari(str(kanun_no), madde_no))
        if not satirlar:
            return None
        # Yürürlükte TEK satır bile varsa madde yürürlüktedir (atif_dogrula.py ile aynı ilke).
        return (Yururluk.MULGA_DAHIL if all(r.get("mulga") for r in satirlar)
                else Yururluk.YALNIZ_YURURLUKTE)
