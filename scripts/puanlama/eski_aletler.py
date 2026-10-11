#!/usr/bin/env python3
"""Eski aletler — RQ2 için, eski geçmişten BİREBİR (F0.5 b, ADR-0099 m.1).

Buradaki kod satırları bundle'daki dosyadan kopyalandı; yalnız yorumlar atıldı, isimlere
`_eski`/`ESKI_` öneki eklenmedi ki fark gözle karşılaştırılabilsin. Kaynak:
  ~/yedek/HakHukuk-2026-10-10.bundle · commit 28910d87868799976ceefbdb7f7b663d28312ab4 (`aa0b85a^`)
  · scripts/score_abstention.py · blob 792738dcdc8d14cf59bc7f41fc6dac58c9538f04
  · REJECT_RE … exact_reject (ADR-0061 onarımından ÖNCEKİ çekinme dedektörü)
Doğrulama gerçek veriyle (`tests/test_kutle.py`): `olcum-bi` 0,6275 · `s2-harness-k10-etiketli`
0,6132 (#61) · `s3-harness-acik` / `s3-harness-k10` (#54) birebir.
Bu modül ölçümün bugünkü yoluna girmez; yalnız `olcum_aleti.Dedektor.ADR0061_ONCESI` çağırır.
"""
import re as _re


REJECT_RE = _re.compile(
    r"düzenle(?:m[ie]yor|nmemiş|nmemekte|nmiş değil)|"
    r"yer al(?:m[ıi]yor|mamakta|maz\b(?!sa))|"
    r"bulun(?:muyor|muyordu|mamaktadır|maz\b(?!sa)|mamış)|"
    r"kapsa(?:m[ıi]yor|mamaktadır|maz\b(?!sa))|"
    r"içer(?:m[ei]yor|memektedir|mez\b(?!se))|"
    r"belirtilme(?:miş(?!se)|mekte|di(?!yse))|değinilme(?:miş(?!se)|mekte|di(?!yse))|"
    r"geçme(?:mektedir|miyor)|"
    r"bilgi (?:yok|bulunmamakta|bulunmuyor)|"
    r"mevcut değil(?!se)|söz konusu değil(?!se)|bir avukata danış|ilgili maddeye danış", _re.I)


DISCLAIMER_RE = _re.compile(r"bir avukata danış|ilgili maddeye danış", _re.I)


_ACILIS_PENCERESI = 160
_KAYNAK_ONEKI = r"kaynak(?:lar|larda|lar arasında|\s+metni)?[^.!?]{0,60}?\bcevapla"
YETERLI_HUKUM_RE = _re.compile(_KAYNAK_ONEKI + r"(?:maktadır|makta|r)\b", _re.I)
YETERSIZ_HUKUM_RE = _re.compile(_KAYNAK_ONEKI + r"(?:ma(?:maktadır|makta|z)|z)\b", _re.I)

_IBARE_SINIRI = _re.compile(
    r"[.!?;]+|\b(?:ancak|fakat|ama|bununla birlikte|buna karşılık|öte yandan)\b", _re.I)


def _acilis_yeterlilik_hukmu(c):
    """ADR-0058 önsözünün emrettiği AÇILIŞ yeterlilik hükmü: True=yeterli / False=yetersiz
    / None=hüküm yok. Yalnız açılış penceresine bakar."""
    bas = c[:_ACILIS_PENCERESI]
    if YETERSIZ_HUKUM_RE.search(bas):
        return False
    if YETERLI_HUKUM_RE.search(bas):
        return True
    return None


def _son_esasli_ibare(c):
    """Cevabın SON esaslı ibaresi — salt atıf parantezleri ve kırıntılar atılır.

    Why: gövdenin hükmünü sonuç cümlesi taşır, ama cevaplar sık sık `(TÜRK CEZA KANUNU,
    Madde 80)` gibi bir atıfla biter; o atıf hüküm değildir ve son ibare sayılırsa gerçek
    sonuç görünmez olur (ölçülen vaka: `h2b_fl35_k4` id=76).
    """
    parcalar = [p.strip() for p in _IBARE_SINIRI.split(c) if p and p.strip()]
    esasli = [p for p in parcalar
              if len(p.split()) >= 4 and not (p.startswith("(") and p.endswith(")"))]
    return esasli[-1] if esasli else c


def exact_reject(cevap, mode):
    """Deterministik red tespiti. `mode` ZORUNLU (varsayılan yok — ADR-0026 ruhu):
    kör modda feragat cümlesi red sinyali DEĞİLDİR, diğer modlarda öyledir.

    Açılışta OLUMSUZ yeterlilik hükmü varsa çekinmedir. OLUMLU hüküm bağlayıcı değildir:
    gövdeyle çelişebilir, o zaman gövdenin SON ESASLI İBARESİ karar verir. Hüküm yoksa
    gövdenin tamamı REJECT_RE ile taranır."""
    c = cevap or ""
    if mode == "blind":
        c = DISCLAIMER_RE.sub(" ", c)
    hukum = _acilis_yeterlilik_hukmu(c)
    if hukum is False:
        return True
    if hukum is True:
        return bool(REJECT_RE.search(_son_esasli_ibare(c)))
    return bool(REJECT_RE.search(c))
