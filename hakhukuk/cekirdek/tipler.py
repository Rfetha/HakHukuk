"""Ürün yüzeyinin veri tipleri. Donmuş — cevap üretildikten sonra değiştirilemez.

⚠️ Neden `Durum` bir enum, `bool` değil (ölçüldü 2026-09-06/07): çekinme dedektörü ÜÇ kez
yanıldı çünkü dünya ikili değil. `suskunluk_terazisi` üç hâl buldu (cevap · çekinceli cevap ·
suskunluk); Faz 0 dördüncüyü ölçtü (kesik). Vatandaş için en tehlikelisi ORTADAKİdir:
"doğrudan madde yok, bununla birlikte…" — cevap gibi görünür, değildir.
"""
from dataclasses import dataclass
from enum import Enum


class Durum(Enum):
    """Bir cevabın vatandaşa ne söylediği. Kapalı küme."""

    CEVAP = "cevap"            # dayanağı var, atıflı
    CEKINCELI = "cekinceli"    # kısmen dayanaklı — rozetle gösterilir
    SUSKUNLUK = "suskunluk"    # dürüst "bilmiyorum"
    KESIK = "kesik"            # üretim bütçesi bitti — YARIM cevap, gizlenmez
    ARAMA_TUKENDI = "arama_tukendi"   # araç döngüsü SINIRA dayandı — dayanak eksik OLABİLİR
    BOS_SORGU = "bos_sorgu"    # soru yazılmadı — ARAMA YAPILMADI (ADR-0081)

    # ⛔ BOS_SORGU, SUSKUNLUK ile BİRLEŞTİRİLMEZ (ADR-0081). İkisi vatandaşa FARKLI şey söyler:
    #   SUSKUNLUK  = "aradım, kaynaklarda karşılık YOK"  → soru geçerli, cevap yok
    #   BOS_SORGU  = "soru yazılmadı, ARAMA YAPILMADI"   → cevaplanacak bir şey yok
    # Birleştirilmiş hâlde rozet ile gövde farklı şey söylüyordu (rozet "kaynaklarda
    # karşılık bulunamadı", gövde "soru boş") ve boş sorgular suskunluk sayımına giriyordu.

    # ⛔ ARAMA_TUKENDI, KESIK ile BİRLEŞTİRİLMEZ (ADR-0076). İkisi vatandaşa FARKLI şey söyler:
    #   KESIK          = "cümle yarım kaldı"        → metne güvenme
    #   ARAMA_TUKENDI  = "cümle tam, dayanağı eksik" → metne güven, DAYANAĞINA güvenme
    # Tek hâle indirmek, sınırın GÖRÜNÜR olması şartını (ADR-0076) sessizce kaldırırdı.


class Yururluk(Enum):
    """Getirilen maddelerin yürürlük süzgeci.

    ⛔ Public API'de bool bayrak yok (CLAUDE.md §4): `getir(..., mulga_dahil=True)`
    çağrı yerinde okunmaz olurdu. Varsayılan YALNIZ_YURURLUKTE — çünkü mülga bir maddeyi
    vatandaşa göstermek eksik özellik değil, YANLIŞ CEVAPtır.
    """

    YALNIZ_YURURLUKTE = "yalniz_yururlukte"   # varsayılan
    MULGA_DAHIL = "mulga_dahil"               # soru tam da mülga maddeyle ilgiliyse


@dataclass(frozen=True)
class Kaynak:
    """Retriever'ın getirdiği tek madde."""

    kanun_adi: str
    kanun_no: str
    madde_no: str
    metin: str
    sira: int

    @property
    def kimlik(self) -> str:
        """`kanun_no/madde_no` — korpustaki anahtar (bkz. tuzak 7.6: %22,7 yineleniyor)."""
        return f"{self.kanun_no}/{self.madde_no}"


@dataclass(frozen=True)
class Atif:
    """Modelin cevapta andığı madde. `dogrulandi` deterministik olarak doldurulur."""

    kanun_no: str
    madde_no: str
    dogrulandi: bool = False


@dataclass(frozen=True)
class Cevap:
    metin: str
    durum: Durum
    atiflar: tuple[Atif, ...]
    kaynaklar: tuple[Kaynak, ...]
