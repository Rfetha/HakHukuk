"""İstem artefaktının kapı testleri (plan Görev 5).

Bu dosya bir KAPIDIR: istem metni damgayı güncellemeden değiştirilemez. Yayımlanmış bir
sayı, üretildiği istem olmadan yeniden üretilemez.
"""
import hashlib

from hakhukuk.cekirdek import istem


def test_istem_surumu_ve_damgasi_sabittir():
    """İstem değişirse damga değişir → yayımlanan sayı yeniden üretilemez hâle gelir."""
    assert istem.ISTEM_SURUMU == "v1"
    assert istem.damga() == istem.DAMGA_v1


def test_uc_istem_de_bos_degil_ve_farklidir():
    metinler = [istem.SISTEM_KOR, istem.SISTEM_TEK_KAYNAK, istem.SISTEM_COK_KAYNAK]
    assert all(m.strip() for m in metinler)
    assert len(set(metinler)) == 3


def test_damga_metinlerin_sha256si():
    beklenen = hashlib.sha256(
        "\n---\n".join(
            [istem.SISTEM_KOR, istem.SISTEM_TEK_KAYNAK, istem.SISTEM_COK_KAYNAK]
        ).encode("utf-8")
    ).hexdigest()[:16]
    assert istem.damga() == beklenen
