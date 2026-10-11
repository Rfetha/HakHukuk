#!/usr/bin/env python3
"""Ölçüm aletinin ayarı — RQ2'nin anahtarları tek nesnede (F0.5 b).

Her anahtar iki (ya da daha çok) adlı değerden birini alır; açık/kapalı bayrağı yoktur. Bir
koşunun künyesine `OlcumAleti.kunye()` yazılır: "bu sayı hangi aletle üretildi" sorusunun
cevabı oradan okunur (tuzak 1.12). `GUNCEL` bugünkü aleti tarif eder.

Anahtarlar:
  dedektor     çekinme dedektörü, mod "data": ADR-0061 onarımı (`score_abstention.exact_reject`) ya
               da ondan önceki hâli (`eski_aletler.exact_reject`, bundle'dan birebir)
  sifir_iddia  cevap sayılıp hakemin hiç iddia çıkaramadığı kalem: 0 puan (kullanıcı kararı
               2026-10-11) ya da A1 ortalamasından çıkarılır (2026-10-11 öncesi
               `harness_tablo.py`; tuzak 2.22, kronoloji #72)
  a1_tanimi    A1 yalnız cevaplanan kalemlerin ortalaması (#54 düzeltmesi, `67ff585`) ya da puanlı
               bütün kalemlerin (çekinmeler dahil) ham ortalaması (öncesi; tuzak 2.16)
  kaynak_kirpma  çekinme hakemine giden kaynak metni 12000 karakter (`ef440d6`, 2026-09-07) ya da
               3500 (öncesi); önbellek anahtarı da bu metin üzerinde
  payda        tuzak geçerliliği cevaba KÖR, kalem düzeyinde yargılanır (K3, `80b1f64`) ya da cevabı
               gören pay hakeminin `source_answers`'ından gelir (öncesi; tuzak 2.14)
  altin_kirpma doğruluk hakemine giden altın madde 3500 karakterde kesilir (`groundedness.py`, hiç
               değişmedi) ya da kesilmez — etkisi ölçülecek (#72)
"""
from dataclasses import dataclass
from enum import Enum

# Why sys.path bloğu yok: bu modül komut olarak koşulmaz, yalnız içe aktarılır; çağıran
# betiğin yol bloğu (ya da tests/conftest.py) kardeş modülleri zaten bulunur kılar.
import eski_aletler


class Dedektor(Enum):
    ADR0061 = "adr0061"                    # 2026-09-06 onarımı (`aa0b85a`)
    ADR0061_ONCESI = "adr0061-oncesi"      # `aa0b85a^` — RQ2'nin eski aleti


class A1Tanimi(Enum):
    CEVAPLANAN = "cevaplanan"              # #54 düzeltmesi (`67ff585`, 2026-08-05)
    HAM_MAKRO = "ham-makro"                # öncesi: çekinmeler de ortalamada


class SifirIddia(Enum):
    SIFIR_PUAN = "sifir-puan"
    ORTALAMADAN_CIKAR = "ortalamadan-cikar"


class KaynakKirpma(Enum):
    K12000 = 12000
    K3500 = 3500


class Payda(Enum):
    KOR = "kor"
    CEVAPLI = "cevapli"


class AltinKirpma(Enum):
    K3500 = "3500"
    KIRPMASIZ = "kirpmasiz"

    def kirp(self, metin: str) -> str:
        return metin[:3500] if self is AltinKirpma.K3500 else metin


@dataclass(frozen=True)
class OlcumAleti:
    dedektor: Dedektor
    sifir_iddia: SifirIddia
    a1_tanimi: A1Tanimi
    kaynak_kirpma: KaynakKirpma
    payda: Payda
    altin_kirpma: AltinKirpma

    def reddet(self, cevap: str, mode: str) -> bool:
        """Çekinme mi (dedektör anahtarına göre; `mode` zorunlu, ADR-0044)."""
        if self.dedektor is Dedektor.ADR0061_ONCESI:
            return eski_aletler.exact_reject(cevap or "", mode)
        # Why burada içe aktarılır: score_abstention bu modülü kullanıyor; modül düzeyinde döngü olurdu.
        from score_abstention import exact_reject
        return exact_reject(cevap or "", mode)

    def cevap_mi(self, cevap: str) -> bool:
        """Kalem cevap mı sayılıyor (çekinme değil mi), mod "data"."""
        return not self.reddet(cevap, "data")

    def kunye(self) -> dict:
        return {"dedektor": self.dedektor.value, "sifir_iddia": self.sifir_iddia.value,
                "a1_tanimi": self.a1_tanimi.value, "kaynak_kirpma": self.kaynak_kirpma.value,
                "payda": self.payda.value, "altin_kirpma": self.altin_kirpma.value}


GUNCEL = OlcumAleti(dedektor=Dedektor.ADR0061, sifir_iddia=SifirIddia.SIFIR_PUAN,
                    a1_tanimi=A1Tanimi.CEVAPLANAN, kaynak_kirpma=KaynakKirpma.K12000,
                    payda=Payda.KOR, altin_kirpma=AltinKirpma.K3500)


def argparse_ekle(p):
    """Anahtarları bir komut satırına ekler; varsayılanlar `GUNCEL`'dir ve künyeye yazılır."""
    p.add_argument("--dedektor", choices=[d.value for d in Dedektor], default=GUNCEL.dedektor.value)
    p.add_argument("--sifir-iddia", choices=[s.value for s in SifirIddia],
                   default=GUNCEL.sifir_iddia.value)
    p.add_argument("--a1-tanimi", choices=[t.value for t in A1Tanimi], default=GUNCEL.a1_tanimi.value)
    p.add_argument("--kaynak-kirpma", type=int, choices=[k.value for k in KaynakKirpma],
                   default=GUNCEL.kaynak_kirpma.value)
    p.add_argument("--payda", choices=[d.value for d in Payda], default=GUNCEL.payda.value)
    p.add_argument("--altin-kirpma", choices=[k.value for k in AltinKirpma],
                   default=GUNCEL.altin_kirpma.value)


def argumanlardan(a) -> OlcumAleti:
    return OlcumAleti(dedektor=Dedektor(a.dedektor), sifir_iddia=SifirIddia(a.sifir_iddia),
                      a1_tanimi=A1Tanimi(a.a1_tanimi), kaynak_kirpma=KaynakKirpma(a.kaynak_kirpma),
                      payda=Payda(a.payda), altin_kirpma=AltinKirpma(a.altin_kirpma))
