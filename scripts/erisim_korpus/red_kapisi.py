#!/usr/bin/env python3
"""Red kapısı — [ADR-0038](../docs/adr/kararlar-0027-0044.md#adr-0038) (sprint3 Adım 3).

**Yürürlükteki politika `KATI`:** doğrulanamayan **tek** atıf cevabın tamamını
reddettirir. İkili — geçti / reddedildi, ara durum yok. Gerekçesi üç katmanlı:
ürün vaadi denetlenebilirlik · hukukta kısmi doğruluk sıfır güvenle aynı iş yükünü
üretir · katı politika **parametresiz**, eşik taranabilir bir serbestlik derecesi
olmuyor (ADR-0037).

`COGUNLUK` ve `CERRAHI` **elenmedi, ablasyona alındı**: ADR-0038 üçünün **aynı cevap
kümesinde post-hoc** koşulmasını şart koşuyor — yeniden üretim gerekmez, maliyet ~0,
coverage/precision eğrisi üç nokta olarak çizilir.

⚠️ **Kabul edilen bedel:** coverage düşer; tek biçim hatası doğru cevabı çöpe atabilir.
Gizlenmiyor — ADR-0011 gereği **kütle = coverage × A1** yan yana raporlanır.

⚠️ **Doğrulayıcının yanlış-negatifi doğrudan coverage kaybıdır** ve katı politika onu
affetmez (ADR-0038 son bölüm). Adım 2'de gerçek veriye karşı dört yanlış-alarm hatası
bu yüzden düzeltildi.

⚠️ **ADR-0038'in kapsamadığı hâl — atıfsız cevap.** Hiç atıf yoksa reddedilecek bir
şey de yoktur ve kapı geçirir. Bu, çekinme cevapları için doğru; ama iddia içerip hiç
kaynak göstermeyen bir cevap da buradan geçer. Politika **uydurulmadı**: `n_atif = 0`
ayrı sayılıyor ki harness-AÇIK tablosunda *"atıfsız geçti"* kendi sınıfı olarak görünsün
ve karar veriye bakılarak verilebilsin.
"""
import re
from dataclasses import dataclass

# ── scripts/ yol köprüsü (T5, 2026-09-07) ────────────────────────────────────
# Kardeş modüller alt klasörlere bölündükten SONRA da bulunsun diye scripts/ kökü, tüm
# alt klasörleri ve repo kökü sys.path'e girer. Uzantısız `import X` bu köprü olmadan
# taşımada SESSİZCE kırılır: ImportError çalışma zamanında, bazen GPU koşusunun ortasında.
# ⚠️ 26 dosyada BİREBİR aynı; değiştirirsen hepsinde değiştir (grep: "yol köprüsü").
import os, sys
_K = os.path.dirname(os.path.abspath(__file__))
_K = _K if os.path.basename(_K) == "scripts" else os.path.dirname(_K)
sys.path[:0] = [_K, *(os.path.join(_K, _d) for _d in sorted(os.listdir(_K))
                      if os.path.isdir(os.path.join(_K, _d)) and _d[0] not in "_."),
                os.path.dirname(_K)]
# ─────────────────────────────────────────────────────────────────────────────

from atif_dogrula import DOGRULANDI

KATI = "kati"
COGUNLUK = "cogunluk"
CERRAHI = "cerrahi"
POLITIKALAR = (KATI, COGUNLUK, CERRAHI)

_CUMLE = re.compile(r"[^.!?\n]+[.!?]?\s*")


@dataclass(frozen=True)
class Karar:
    gecti: bool
    cevap: str
    gerekce: str
    n_atif: int
    n_dogrulanan: int


def kapi(cevap: str, hukumler, politika: str = KATI) -> Karar:
    """Atıf hükümlerine göre cevabı geçir ya da reddet."""
    n = len(hukumler)
    kotu = [h for h in hukumler if h.hukum != DOGRULANDI]
    iyi = n - len(kotu)

    if politika == KATI:
        gecti = not kotu
        return Karar(gecti, cevap if gecti else "", "tüm atıflar doğrulandı" if gecti
                     else f"{len(kotu)} atıf doğrulanamadı ({kotu[0].hukum})", n, iyi)

    if politika == COGUNLUK:
        gecti = n == 0 or iyi * 2 > n
        return Karar(gecti, cevap if gecti else "",
                     f"doğrulanan {iyi}/{n}", n, iyi)

    if politika == CERRAHI:
        kalan = "".join(c for c in _CUMLE.findall(cevap)
                        if not any(h.atif.ham in c for h in kotu)).strip()
        gecti = bool(kalan)
        return Karar(gecti, kalan if gecti else "",
                     f"{len(kotu)} atıflı cümle çıkarıldı" if kotu else "değişiklik yok", n, iyi)

    raise SystemExit(f"[kapı] 🚫 bilinmeyen politika {politika!r} — {POLITIKALAR}")
