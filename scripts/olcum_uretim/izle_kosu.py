#!/usr/bin/env python3
"""Bir üretim koşusunun çıktısını CANLI izler ve kalemlerini GÖZLE okunur kılar.

  python scripts/olcum_uretim/izle_kosu.py <çıktı-dosyası> [--n 80]   # canlı pano
  python scripts/olcum_uretim/izle_kosu.py <çıktı-dosyası> --liste    # tek satır özet
  python scripts/olcum_uretim/izle_kosu.py <çıktı-dosyası> --kalem 11 # tam soru+cevap
  python scripts/olcum_uretim/izle_kosu.py <çıktı-dosyası> --bir-kez  # panoyu bir kez bas

Why: bu hattın kapıları koşu BİTTİKTEN sonra okunursa saatler yanar. Kesik oranı >%5 koşuyu
geçersiz kılar (ADR-0040) ve boş cevap oranı ürün yolunun kendi kusurudur (§7.9) — ikisi de
üretim sürerken görülebilir. `watch_run.sh`/`watch_cp09.sh` uzun koşular için tek satır log
basar; bu betik tamamlayıcıdır: **kalemin kendisini** okutur.

Why (gözle okuma): "gözle okuma bir kapıdır" — sayısal kapı testin körlüğünü görmez. Bu betiğin
`--kalem` kipi o kapının aletidir: sayı yeşilken metin yanlış olabilir.

Biçim: JSON dizisi ya da JSONL, ikisi de okunur. Alan adları koşudan koşuya değişiyor
(`sunum`/`metin`/`cevap` · `gecen_sn`/`sure`), bu yüzden aday listeleriyle çözülür — eksik alan
sessizce atlanır, UYDURULMAZ.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter

# Why: rozetler `hakhukuk/cli.py`'nin sözlüğüyle UYUMLU tutulur ama ondan İTHAL EDİLMEZ —
# bu betik pakete bağlı olmamalı ki paketten ÖNCE üretilmiş koşular da okunabilsin.
# Bilinmeyen durum sessizce "·" alır; uydurma etiket basılmaz.
ROZET = {"cevap": "✅", "cekinceli": "🟡", "suskunluk": "🤐", "cekinme": "⛔",
         "kesik": "✂️", "bos": "␀", "bos_sorgu": "␀", "hata": "💥"}

# Why: alan adları koşu ailesine göre değişiyor; tek isim dayatmak eski çıktıları okunmaz kılar.
ADAYLAR = {
    "id": ("id", "soru_id", "idx"),
    "soru": ("soru", "question", "prompt"),
    "cevap": ("sunum", "metin", "cevap", "answer", "content"),
    "durum": ("durum", "status", "label"),
    "sure": ("gecen_sn", "sure_sn", "elapsed_s", "latency_s"),
    "http": ("http", "status_code"),
    "kaynaklar": ("kaynaklar", "sources", "context"),
}


def alan(kayit: dict, ad: str):
    """Mantıksal alanı kayıttan çöz. Bulunamazsa None — varsayılan UYDURULMAZ."""
    for aday in ADAYLAR[ad]:
        if aday in kayit:
            return kayit[aday]
    return None


def oku(yol: str) -> list[dict]:
    """JSON dizisi ya da JSONL oku. Dosya yazılırken yakalanırsa BOŞ döner, patlamaz.

    Why: canlı izlerken üretici dosyayı yeniden yazıyor olabilir; yarım JSON bir sonraki
    turda tam okunur. Burada patlamak izlemeyi kullanılmaz kılardı.
    """
    try:
        with open(yol, encoding="utf-8") as f:
            ham = f.read()
    except FileNotFoundError:
        return []
    ham = ham.strip()
    if not ham:
        return []
    try:
        veri = json.loads(ham)
        return veri if isinstance(veri, list) else [veri]
    except json.JSONDecodeError:
        pass
    kayitlar = []
    for satir in ham.splitlines():                     # JSONL: yarım son satır atlanır
        satir = satir.strip()
        if not satir:
            continue
        try:
            kayitlar.append(json.loads(satir))
        except json.JSONDecodeError:
            continue
    return kayitlar


def ozetle(kayitlar: list[dict], n: int) -> dict:
    """Panonun bastığı bütün sayılar — saf fonksiyon, testten çağrılır."""
    sureler = [s for s in (alan(k, "sure") for k in kayitlar) if isinstance(s, (int, float))]
    bos = [alan(k, "id") for k in kayitlar if not str(alan(k, "cevap") or "").strip()]
    httpler = [alan(k, "http") for k in kayitlar]
    hatali = [alan(k, "id") for k, h in zip(kayitlar, httpler) if h is not None and h != 200]
    ort = sum(sureler) / len(sureler) if sureler else 0.0
    return {
        "uretilen": len(kayitlar),
        "toplam": n,
        "yuzde": (100 * len(kayitlar) // n) if n else 0,
        "durumlar": dict(Counter(alan(k, "durum") for k in kayitlar)),
        "ortalama_sn": ort,
        "kalan_dk": (n - len(kayitlar)) * ort / 60 if n > len(kayitlar) else 0.0,
        "bos": bos,
        "http_hatali": hatali,
        "bitti": len(kayitlar) >= n,
    }


def kirp(s, uzunluk: int) -> str:
    s = " ".join(str(s or "").split())
    return s if len(s) <= uzunluk else s[: uzunluk - 1] + "…"


def pano(kayitlar, n, yol, temizle=True):
    o = ozetle(kayitlar, n)
    if temizle:
        os.system("clear")
    dolu = int(40 * o["uretilen"] / n) if n else 0
    print(f"╔══ {kirp(yol, 62):<64}╗")
    print(f"║ [{'█'*dolu}{'░'*(40-dolu)}] {o['uretilen']:>3}/{n}  %{o['yuzde']:<3}"
          f"{'':>15}║")
    if o["uretilen"]:
        durum = "  ".join(f"{ROZET.get(k, '·')} {k}: {v}" for k, v in o["durumlar"].items())
        print(f"║ {kirp(durum, 66):<67}║")
        print(f"║ ortalama {o['ortalama_sn']:>5.1f} sn · kalan ≈ {o['kalan_dk']:>5.1f} dk{'':>28}║")
        # Why: bu iki satır koşunun GEÇERLİLİK kapıları — ADR-0040 (%5 kesiklik) ve §7.9
        # (boş cevap). Bitişte değil, koşarken görülmeleri gerekiyor.
        print(f"║ BOŞ cevap: {len(o['bos']):<3} {kirp(o['bos'], 18):<18}"
              f"HTTP≠200: {len(o['http_hatali']):<3} {kirp(o['http_hatali'], 11):<11}║")
    print("╚" + "═" * 68 + "╝")
    if kayitlar:
        son = kayitlar[-1]
        print(f"\n── kalem {alan(son,'id')} {ROZET.get(alan(son,'durum'),'·')} "
              f"{alan(son,'durum')} ──")
        print(f"SORU   {kirp(alan(son,'soru'), 200)}\n")
        print("CEVAP")
        for satir in str(alan(son, "cevap") or "")[:900].splitlines():
            print("  " + kirp(satir, 100))
    return o


def kalem_bas(kayitlar, kalem_id):
    kayit = next((k for k in kayitlar if alan(k, "id") == kalem_id), None)
    if kayit is None:
        print(f"kalem {kalem_id} yok (üretilen: {len(kayitlar)})")
        return 1
    print("=" * 72)
    print(f"KALEM {kalem_id}  {ROZET.get(alan(kayit,'durum'),'·')} {alan(kayit,'durum')}  "
          f"HTTP {alan(kayit,'http')}  {alan(kayit,'sure')} sn")
    print("=" * 72)
    print(f"\nSORU\n{alan(kayit,'soru')}\n")
    print(f"CEVAP\n{alan(kayit,'cevap')}\n")
    kaynaklar = alan(kayit, "kaynaklar") or []
    print(f"KAYNAKLAR ({len(kaynaklar)})")
    for k in kaynaklar:
        if isinstance(k, dict):
            print("  -", kirp(f"{k.get('kanun_adi','?')} {k.get('madde_no','?')}", 90))
        else:
            print("  -", kirp(k, 90))
    return 0


def liste_bas(kayitlar):
    for k in kayitlar:
        print(f"{str(alan(k,'id')):>4} {ROZET.get(alan(k,'durum'),'·')} "
              f"{str(alan(k,'durum')):<10} {str(alan(k,'sure')):>6} sn  "
              f"{kirp(alan(k,'soru'), 58)}")


def main(argv=None) -> int:
    a = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    a.add_argument("yol", help="koşunun çıktı dosyası (JSON dizisi ya da JSONL)")
    a.add_argument("--n", type=int, default=80, help="beklenen kalem sayısı (varsayılan 80)")
    a.add_argument("--kalem", type=int, help="tek kalemin tam soru+cevabını bas")
    a.add_argument("--liste", action="store_true", help="tek satır özet listesi")
    a.add_argument("--bir-kez", action="store_true", help="panoyu bir kez bas, bekleme")
    a.add_argument("--aralik", type=float, default=5.0, help="yenileme aralığı (sn)")
    x = a.parse_args(argv)

    if x.kalem is not None:
        return kalem_bas(oku(x.yol), x.kalem)
    if x.liste:
        liste_bas(oku(x.yol))
        return 0
    if x.bir_kez:
        pano(oku(x.yol), x.n, x.yol, temizle=False)
        return 0
    try:
        while True:
            o = pano(oku(x.yol), x.n, x.yol)
            if o["bitti"]:
                print(f"\n✅ KOŞU BİTTİ — {o['uretilen']}/{x.n}")
                return 0
            print(f"\n({x.aralik:g} sn'de bir yenilenir · Ctrl+C ile çık · "
                  f"tek kalem: --kalem <id>)")
            time.sleep(x.aralik)
    except KeyboardInterrupt:
        print("\nçıkıldı")
        return 0


if __name__ == "__main__":
    sys.exit(main())
