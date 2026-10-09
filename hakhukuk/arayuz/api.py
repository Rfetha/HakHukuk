"""`hakhukuk-api` — `servis.answer()` üstünde ince kabuk. Kendi mantığı yoktur.

`cli.py` ve `tui.py` ile aynı ilke: sınıflandırma, atıf doğrulama ve kaynak seçimi
`answer()`'ın içindedir; bu modül yalnız TAŞIR.

⚠️ YEREL ve TEK KULLANICI (`AÇIK KARAR S9` açılmadı): `127.0.0.1`, kimlik yok, hız sınırı yok.
Barındırma, mahremiyet vaadi ve TR IP kısıtı soruları `v2`'de açık duruyor.

⛔ Bu kabuk ÜRÜN YOLUNU taşır, ölçüm hattını değil. Yayımlanan `%80,1` iki geçişte düşünceyi
zorla kapatan ölçüm hattının sayısıdır; ürün yolunda cevapların ~%5'i BOŞ döner (ticket 1) ve
burada **503** olarak GÖRÜNÜR — giderilmez.
"""
import threading

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from hakhukuk.cekirdek import servis
from hakhukuk.arayuz.cli import SORUMLULUK_IBARESI, bicimle
from hakhukuk.cekirdek.tipler import Cevap

HOST = "127.0.0.1"   # ⛔ S9 açılmadı; buranın değişmesi ürünün vaadini değiştirir
PORT = 8000

# Tekilin (`servis`'in modül düzeyi `_retriever`/`_araclar` önbellekleri) evre güvenliği
# ÖLÇÜLMEDİ; bütün ölçümler sıralı istekle yapıldı. Kilit, o rejimi HTTP'de de korur.
_KILIT = threading.Lock()

uygulama = FastAPI(
    title="HakHukuk",
    description="Türk hukuku asistanı — yerel, tek kullanıcı. Hukuki tavsiye değildir.",
)


class Soru(BaseModel):
    # `min_length=1` YALNIZ boş dizeyi eler. Yalnız-boşluktan ibaret girdiyi eleyen şey
    # aşağıdaki açık `soru.strip()` kontrolüdür (422) — burada `strip_whitespace` YOKTUR;
    # o kontrolü "gereksiz tekrar" sanıp silmek 422 kapısını sessizce kaldırır.
    # ⛔ UYDURULMUŞ uzunluk eşiği YOK: "kira?" geçerli bir sorudur.
    soru: str = Field(min_length=1)
    k: int | None = Field(default=None, ge=1)


class AtifCevabi(BaseModel):
    kanun_no: str
    madde_no: str
    dogrulandi: bool


class KaynakCevabi(BaseModel):
    kanun_adi: str
    kanun_no: str
    madde_no: str
    metin: str
    sira: int


class Yanit(BaseModel):
    """Yapısal alanlar + HAZIR `sunum` dizesi.

    `sunum` yedek değil SÖZLEŞMEdir: tembel bir tüketici tek alanı bassa bile rozet, atıflar,
    kaynaklar ve sorumluluk ibaresi kullanıcıya gider. Dürüstlük sözleşmesi HTTP'de düşmez.
    """

    metin: str
    durum: str
    atiflar: list[AtifCevabi]
    kaynaklar: list[KaynakCevabi]
    sunum: str
    sorumluluk: str


def _yanit(cevap: Cevap) -> Yanit:
    return Yanit(
        metin=cevap.metin,
        durum=cevap.durum.value,
        atiflar=[AtifCevabi(kanun_no=a.kanun_no, madde_no=a.madde_no,
                            dogrulandi=a.dogrulandi) for a in cevap.atiflar],
        kaynaklar=[KaynakCevabi(kanun_adi=k.kanun_adi, kanun_no=k.kanun_no,
                                madde_no=k.madde_no, metin=k.metin, sira=k.sira)
                   for k in cevap.kaynaklar],
        sunum=bicimle(cevap),
        sorumluluk=SORUMLULUK_IBARESI,
    )


@uygulama.post("/sor", response_model=Yanit)
def sor(istek: Soru) -> Yanit:
    if not istek.soru.strip():
        raise HTTPException(status_code=422, detail="soru boş olamaz")

    with _KILIT:
        cevap = servis.answer(istek.soru, **({"k": istek.k} if istek.k else {}))

    # ⛔ "HTTP 200 ile boş içerik" bu hattın #42'de ölçtüğü kusurun ADIDIR; sınırı geçmez.
    # KESİK ama DOLU bir cevap 200 döner: yarım bir cümle bilgidir, rozetiyle birlikte gider.
    if not cevap.metin.strip():
        raise HTTPException(status_code=503,
                            detail="model boş içerik döndürdü (sonlanmama); ticket 1")
    return _yanit(cevap)


def main(argv: list[str] | None = None) -> int:
    import uvicorn  # noqa: PLC0415 — yalnız sunucu açılırken gerekir

    uvicorn.run(uygulama, host=HOST, port=PORT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
