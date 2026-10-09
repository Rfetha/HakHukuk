from recall_olc import recall_at_k


def test_recall_at_k_bulunanlari_sayar():
    # sıra = altının kaçıncı sırada geldiği (0-tabanlı), None = hiç gelmedi
    assert recall_at_k([0, 1, 2, None], k=3) == 0.75


def test_recall_at_k_k_disindakini_saymaz():
    assert recall_at_k([0, 5], k=3) == 0.5


def test_recall_at_k_bos_liste_sifir():
    assert recall_at_k([], k=10) == 0.0


def test_rrf_en_yuksek_skoru_sifirinci_siraya_koyar():
    # ⚠️ Sıra hesabı ters dönerse RRF sessizce EN KÖTÜ adayı öne alır.
    from recall_olc import rrf_birlestir
    import numpy as np
    r = rrf_birlestir([np.array([0.1, 0.9, 0.5])], rrf_k=60)
    assert int(np.argmax(r)) == 1


def test_rrf_iki_kaynakta_da_ustte_olan_kazanir():
    from recall_olc import rrf_birlestir
    import numpy as np
    # RRF'in füzyon değeri buradan gelir: 1. aday ikisinde de 1. sırada;
    # 0. aday bir kaynakta 1. ama diğerinde sonuncu.
    a = np.array([9.0, 8.0, 1.0])
    b = np.array([1.0, 9.0, 8.0])
    r = rrf_birlestir([a, b], rrf_k=60)
    assert int(np.argmax(r)) == 1


def test_rrf_tek_kaynak_sirayi_korur():
    from recall_olc import rrf_birlestir
    import numpy as np
    s = np.array([3.0, 1.0, 2.0])
    r = rrf_birlestir([s], rrf_k=60)
    assert list(np.argsort(r)[::-1]) == list(np.argsort(s)[::-1])
