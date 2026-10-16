#!/usr/bin/env python3
"""Kütle — dondurulmuş kümeye karşı TEK hesap (F0.5 a·c, ADR-0098 m.1).

NEDEN TEK YER: depoda iki formül vardı ve sıfır iddialı cevaplanmış bir kalemde ayrıştılar
(`harness_tablo.py` kapsama × A1 ↔ `uc_okuma_kutle.py` toplam ÷ n; `olcum-bi` 0,6838 ↔ 0,6734,
tuzak 2.22). Paydaları da dosyanın satır sayısından geliyordu: eksik dosya eksik paydayla,
hata vermeden puanlanırdı.

İki kapı, ikisi de puanlamayı durdurur (`OlcumKapisiHatasi`):
  (c) tamlık  satır sayısı = küme boyutu · id'ler tekil ve 0…n-1 · soru listesi kümeyle aynı
  (a) payda   cevap sayılan her kalemin hakem puanı var ya da kalem sıfır iddialı; hakem
              satırı eksik ya da `durum: hakem_hata` ise durur

kütle = kapsama × A1 (bugünkü alette = Σ puan(cevap sayılan) / küme boyutu). Sıfır iddialı
cevaplanmış kalemin puanı `OlcumAleti.sifir_iddia`'ya göre 0'dır ya da A1'den çıkarılır; A1'in
tanımı `OlcumAleti.a1_tanimi`'ye göre yalnız cevaplananlar ya da (eski alet) puanlı bütün kalemler.
"""
import collections
import hashlib
import json
from dataclasses import dataclass

from olcum_aleti import A1Tanimi, OlcumAleti, SifirIddia

_HAKEM_HATASI = {"hakem_hata", "bos_girdi"}


class OlcumKapisiHatasi(Exception):
    """Girdi eksik ya da tutarsız; sayı üretilmez."""


def _kume_sorusu(satir):
    # gen_eval_grounded.extract ile aynı tanım: ilk kullanıcı mesajı.
    return next((m["content"] for m in satir.get("messages", []) if m["role"] == "user"), None)


@dataclass(frozen=True)
class DondurulmusKume:
    yol: str
    sha256: str
    sorular: tuple

    @property
    def boyut(self) -> int:
        return len(self.sorular)

    @classmethod
    def yukle(cls, yol: str) -> "DondurulmusKume":
        ham = open(yol, "rb").read()
        satirlar = [json.loads(l) for l in ham.decode("utf-8").splitlines() if l.strip()]
        return cls(yol=yol, sha256=hashlib.sha256(ham).hexdigest(),
                   sorular=tuple(_kume_sorusu(s) for s in satirlar))

    def kunye(self) -> dict:
        return {"yol": self.yol, "sha256": self.sha256, "boyut": self.boyut}


@dataclass(frozen=True)
class Kalem:
    id: int
    cevaplandi: bool
    puan: float | None        # kalemin puanı; sıfır iddialı cevaplanmışta kurala göre 0 ya da None
    sifir_iddia: bool


@dataclass(frozen=True)
class KutleSonucu:
    kalemler: tuple
    n: int
    alet: OlcumAleti

    @property
    def n_cevaplanan(self) -> int:
        return sum(1 for k in self.kalemler if k.cevaplandi)

    @property
    def n_puanli_cevaplanan(self) -> int:
        return sum(1 for k in self.kalemler if k.cevaplandi and not k.sifir_iddia)

    @property
    def n_sifir_iddia(self) -> int:
        return sum(1 for k in self.kalemler if k.cevaplandi and k.sifir_iddia)

    def _a1_ham(self):
        ham_makro = self.alet.a1_tanimi is A1Tanimi.HAM_MAKRO
        p = [k.puan for k in self.kalemler if (k.cevaplandi or ham_makro) and k.puan is not None]
        return sum(p) / len(p) if p else None

    @property
    def kapsama(self) -> float | None:
        return round(self.n_cevaplanan / self.n, 4) if self.n else None

    @property
    def A1(self) -> float | None:
        a1 = self._a1_ham()
        return round(a1, 4) if a1 is not None else None

    @property
    def kutle(self) -> float | None:
        if not self.n:
            return None
        a1 = self._a1_ham()
        if a1 is None:
            return 0.0
        if self.alet.sifir_iddia is SifirIddia.ORTALAMADAN_CIKAR:
            # Why: eski harness_tablo kapsama ve A1'i ÖNCE 4 haneye yuvarlayıp çarpıyordu;
            # eski alet kayıttaki sayıyı birebir üretmeli (s3-harness-k10: 0,6914, tek
            # yuvarlamayla 0,6913).
            return round(self.kapsama * self.A1, 4)
        return round(self.n_cevaplanan / self.n * a1, 4)

    def alt_kume(self, idler) -> "KutleSonucu":
        s = set(idler)
        return KutleSonucu(kalemler=tuple(k for k in self.kalemler if k.id in s), n=len(s),
                           alet=self.alet)

    def ozet(self) -> dict:
        return {"n": self.n, "n_cevaplanan": self.n_cevaplanan,
                "n_puanli_cevaplanan": self.n_puanli_cevaplanan,
                "n_sifir_iddia": self.n_sifir_iddia, "kapsama": self.kapsama, "A1": self.A1,
                "kutle": self.kutle}


def _tamlik_kapisi(detay, kume):
    if len(detay) != kume.boyut:
        raise OlcumKapisiHatasi(
            f"satır sayısı {len(detay)} ≠ küme boyutu {kume.boyut} ({kume.yol}) — eksik ya da "
            f"fazla cevap dosyası puanlanmaz")
    idler = [r.get("id") for r in detay]
    yinelenen = sorted(i for i, c in collections.Counter(idler).items() if c > 1)
    if yinelenen:
        raise OlcumKapisiHatasi(f"yinelenen id: {yinelenen[:10]} — dosya iki koşudan birleşmiş olabilir")
    if set(idler) != set(range(kume.boyut)):
        raise OlcumKapisiHatasi(f"id kümesi 0…{kume.boyut - 1} değil")
    if collections.Counter(r.get("soru") for r in detay) != collections.Counter(kume.sorular):
        raise OlcumKapisiHatasi(f"soru listesi kümeyle aynı değil ({kume.yol}) — başka bir "
                                f"soru setiyle üretilmiş cevaplar")


def kutle_hesapla(detay, gnd, kume: DondurulmusKume, alet: OlcumAleti,
                  goz_ekle=frozenset()) -> KutleSonucu:
    """`detay` (üreticinin satırları) + `gnd` (hakem satırları) → kütle; iki kapı önce çalışır.

    `goz_ekle`: gözle okumada cevap sayılan kalem id'leri; dedektörün kümesine eklenir."""
    _tamlik_kapisi(detay, kume)
    disarida = sorted(set(goz_ekle) - set(range(kume.boyut)))
    if disarida:
        raise OlcumKapisiHatasi(f"göz listesinde kümede olmayan id: {disarida}")
    gnd_map = {}
    for g in gnd:
        if g.get("id") in gnd_map:
            raise OlcumKapisiHatasi(f"hakem dosyasında yinelenen id: {g.get('id')}")
        gnd_map[g.get("id")] = g

    # Why: ham makro A1 çekinmeleri de ortalar; o tanımda çekinmenin eksik hakem satırı da sayıyı kaydırır.
    ham_makro = alet.a1_tanimi is A1Tanimi.HAM_MAKRO
    kalemler, hata = [], []
    for r in sorted(detay, key=lambda r: r["id"]):
        i = r["id"]
        g = gnd_map.get(i)
        if not (alet.cevap_mi(r.get("cevap", "")) or i in goz_ekle):
            if ham_makro and (g is None or g.get("durum") in _HAKEM_HATASI):
                hata.append(i)
            kalemler.append(Kalem(i, False, g.get("faithfulness") if g else None, False))
            continue
        if g is None or g.get("durum") in _HAKEM_HATASI:
            hata.append(i)
        elif g.get("faithfulness") is not None:
            kalemler.append(Kalem(i, True, g["faithfulness"], False))
        elif g.get("durum") == "sifir_iddia" or g.get("n_claims") == 0:
            puan = 0.0 if alet.sifir_iddia is SifirIddia.SIFIR_PUAN else None
            kalemler.append(Kalem(i, True, puan, True))
        else:
            hata.append(i)
    if hata:
        raise OlcumKapisiHatasi(
            f"{len(hata)} kalemin hakem puanı yok (hakem hatası ya da eksik satır): "
            f"id={hata[:10]} — puanlama durur; hakem o kalemler için yeniden koşulur")
    return KutleSonucu(kalemler=tuple(kalemler), n=kume.boyut, alet=alet)
