#!/usr/bin/env python
"""Yarış koruması — aynı çıktı dosyasına iki süreç yazmasın.

⚠️ NEDEN VAR (2026-07-25, sprint1 CP7 dersi — sessiz-bozulma sınıfının BEŞİNCİ vakası):
aynı `--label` ile iki skorlama süreci paralel koştuğunda (ana kabuktaki bir yetim süreç +
ikinci bir koşu) ikisi de `gnd_{label}.jsonl`'i `"w"` modunda açtı ve satırları birbirinin
üstüne, yarıda kesilmiş hâlde yazdı. **Hiçbir aşamada hata olmadı:** koşu tamamlandı, özet
JSON yazıldı, tablo doldu — yalnız detay dosyası bozuktu (`gnd_m4_gem.jsonl` 74/80 geçerli +
3 bozuk satır; `gnd_m5_gem.jsonl` 81 satırın 1'i bozuk). Bozukluk ancak bir sonraki adım
(`rescore_answered.py`) `json.loads` ile patlayınca görüldü — o da A1'i kaybetmek demekti.

ADR-0026'nın ruhu: **sessizce bozulmaktansa erken dur.** Bu modül çıktı dosyasının yanında
bir `.lock` tutar; kilit başka bir canlı süreçteyse ikinci koşu YAZMADAN ÖNCE patlar.

Kullanım (çıktı dosyası açılmadan hemen önce, `os.makedirs`'ten sonra):

    import runlock
    runlock.acquire(out_path, tag="gnd m4_gem")
    with open(out_path, "w", ...) as f:
        ...

Notlar:
- `fcntl.flock` (Linux) advisory kilit: yalnız bu modülü kullanan süreçler birbirini görür —
  amaç zaten bu, dış araçları engellemek değil.
- Kilit süreç ömrü boyunca tutulur; süreç NASIL biterse bitsin (çıkış, exception, SIGKILL)
  çekirdek fd'yi kapatınca kilit düşer → bayat kilit dosyası kalmaz.
- Aynı süreç içinde aynı yolu iki kez kilitlemek serbesttir (idempotent).
"""
import atexit
import fcntl
import os

# Süreç ömrü boyunca AÇIK kalmalı: fd kapanırsa flock düşer. Modül düzeyinde tutuluyor ki
# GC toplamasın.
_HELD: dict[str, "object"] = {}


def acquire(out_path: str, tag: str = "") -> str:
    """`out_path` için özel (exclusive) kilit al; başkası tutuyorsa ERKEN PATLA.

    Döner: kilit dosyasının yolu. Kilit süreç bitene kadar tutulur.
    """
    lock_path = os.fspath(out_path) + ".lock"
    if lock_path in _HELD:          # aynı süreç, aynı yol → zaten bizde
        return lock_path

    d = os.path.dirname(lock_path)
    if d:
        os.makedirs(d, exist_ok=True)

    # ⚠️ "w" ile AÇMA: truncate flock'tan ÖNCE olur → kilidi tutan sürecin pid satırını sileriz
    # ve "kim tutuyor" mesajı boş çıkar. "a+" açar ama kesmez; kesme kilit ALINDIKTAN sonra.
    fh = open(lock_path, "a+", encoding="utf-8")
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        try:
            fh.seek(0)
            other = fh.read().strip() or "(sahip bilgisi yazılmamış)"
        except OSError:
            other = "(okunamadı)"
        fh.close()
        raise SystemExit(
            f"\n[runlock] 🚫 KİLİTLİ: {out_path}\n"
            f"  Bu çıktıya ŞU AN başka bir süreç yazıyor → {other}\n"
            f"  {'İş: ' + tag if tag else ''}\n"
            f"  İki süreç aynı dosyayı 'w' modunda yazarsa dosya SESSİZCE bozulur "
            f"(sprint1 CP7'de üç kez oldu, hata vermedi, sayı üretti).\n"
            f"  Yap: diğer koşunun bitmesini bekle · ya da farklı --label kullan · "
            f"ya da yetim süreci öldür (ps aux | grep score).\n"
        )

    fh.seek(0)
    fh.truncate()
    fh.write(f"pid={os.getpid()} tag={tag or '-'} out={out_path}\n")
    fh.flush()
    _HELD[lock_path] = fh
    atexit.register(_release, lock_path)
    return lock_path


def _release(lock_path: str) -> None:
    fh = _HELD.pop(lock_path, None)
    if fh is None:
        return
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        fh.close()
        os.unlink(lock_path)
    except OSError:
        pass        # temizlik başarısızsa önemsiz: bir sonraki flock zaten doğru karar verir
