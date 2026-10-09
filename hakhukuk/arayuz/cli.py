"""`hakhukuk "soru"` — `servis.answer()` üstünde ince kabuk. Kendi mantığı yoktur.

Çıktı dört şeyi ayrı ayrı gösterir ve hiçbirini gizlemez:
durum rozeti · cevap · atıflar (doğrulanmamışlar ⚠️ ile) · kaynaklar · sorumluluk ibaresi.
"""
import argparse
import json
import pathlib
import re
import sys

from hakhukuk.cekirdek.tipler import Cevap, Durum

# ⚠️ GEÇİCİ METİN — açık karar S10. Nihai hukuki ibare hukukçu görüşüne bağlı; geldiğinde
# BURADAN, tek yerden güncellenir. `tui.py` bu sabiti IMPORT eder, kopyalamaz: S18'in dersi
# aynı metnin iki yerde sessizce ayrışmasıydı.
SORUMLULUK_IBARESI = (
    "⚖️  Bu yanıt hukuki tavsiye değil, bilgilendirme amaçlıdır. Bağlayıcı bir karar "
    "vermeden önce güncel mevzuatı doğrulayın ve bir avukata danışın."
)

# ⚠️ Görev 21 Adım 7: sayılar KUNYE.json'dan OKUNUR, koda gömülmez — künye değişince
# bu satır da (yeniden okunarak) değişmeli, elle güncellenmemeli.
#
# ⚠️ KUSUR B DÜZELTMESİ (g20 imaj ölçümü, 2026-09-11): yol REPO KÖKÜNE göreli
# (`__file__.parent.parent / "data/corpus/..."`) çözülüyordu. Editable kurulumda
# (host, `pip install -e .`) `hakhukuk/` repo içinde kaldığı için bu YANLIŞ görünmüyordu;
# paket NORMAL kurulunca (konteyner, `pip install ".[api]"`) `hakhukuk/` site-packages'a
# taşınır ama `data/` ONUNLA BİRLİKTE TAŞINMAZ — yol bulunamayan bir yere düşer ve
# `kapsam_satiri()` sessizce "künye okunamadı" dalına düşer (`except OSError` yutar).
#
# Üç seçenek tartıldı: (a) künyeyi PAKETİN İÇİNE taşı, importlib.resources ile oku —
# kurulumdan bağımsız çalışır; (b) arama sırası (paket içi → repo köküne göreli); (c) ortam
# değişkeni. **Seçilen: (a), importlib.resources yerine düz `Path(__file__).parent` ile**
# (paket zaten dizin olarak kurulur, `resources` API'sinin zip-güvenli soyutlamasına gerek
# yok — YAGNI). (b) ELENDİ: iki arama yolu, künyenin HANGİ kopyadan okunduğunu çağrı yerinde
# belirsizleştirir ve "repo köküne göreli" dalı yalnız bugünkü kusuru sessizce geri getirir.
# (c) ELENDİ: tek kullanıcılı yerel bir CLI için fazladan bir kurulum adımı (env değişkeni
# unutulursa AYNI sessiz düşüş).
#
# ⛔ İKİNCİ KOPYA YOK: `hakhukuk/veri/KUNYE.json` bir SEMBOLİK BAĞ (symlink), gerçek dosya
# `data/corpus/KUNYE.json`'da durmaya devam eder — künye üreten kod tek yerden (korpus
# hattı) yazar. Geliştirme/editable kurulumda bağ CANLI çözülür (iki yer asla ayrışmaz,
# S18); `pip install` (normal kurulum, konteyner) paketi paketlerken bu bağı OTOMATİK
# olarak içeriğiyle birlikte bir gerçek dosyaya döker (`shutil.copytree`/wheel inşası
# symlink'i İZLER, hedefi kopyalar) — build zamanında üretilen TEK kopya budur, elle
# bakımı gereken bir ikinci künye DEĞİLDİR. `pyproject.toml`'un `package-data` ayarı bu
# dosyayı taşınacak paket verisi olarak işaretler.
_KUNYE_YOLU = pathlib.Path(__file__).resolve().parent.parent / "veri" / "KUNYE.json"


def _nokta(sayi: int) -> str:
    """Binlik ayracı Türkçe yazımla: 37949 → "37.949"."""
    return f"{sayi:,}".replace(",", ".")


def kapsam_satiri() -> str:
    """Statik kapsam satırı — SINIFLANDIRICI YOK (karar 3, brief Adım 7).

    Bir soru sınıflandırıcısı yanılır ve yanıldığında vatandaşa "bu konu kapsam
    dışı" diyerek cevabı olan soruyu öldürür. Ucuz ve dürüst alternatif: kapsamı
    HER ZAMAN, aynı statik satırla göstermek. Künye dosyası bulunamazsa uygulamanın
    AÇILMAMASI kabul edilebilir bir karar DEĞİL (brief); bu yüzden sayısız ama
    dürüst bir satırla devam edilir, patlanmaz.

    ⚠️ Gösterilen sayı `n_madde` DEĞİL, `n_madde - n_mulga`: `n_madde` TOPLAMdır ve
    `retriever.getir()` varsayılanı (`Yururluk.YALNIZ_YURURLUKTE`) mülga maddeleri eler —
    vatandaşın içinde arama yapılan madde sayısı budur. Toplam ve mülga sayısı da yazılır
    ki fark GÖRÜNÜR olsun; üçü de künyeden TÜRETİLİR, hiçbiri koda gömülmez.

    ⚠️ Burası `tui.py`'de DEĞİL `cli.py`'de duruyor (`SORUMLULUK_IBARESI` emsali): metnin
    ikinci bir kopyası çıkarsa iki yüzey sessizce ayrışır (S18) ve `cli`/`api` bu satırı
    almak için `textual` bağımlılığını içeri çekmek zorunda kalırdı.
    """
    try:
        kunye = json.loads(_KUNYE_YOLU.read_text(encoding="utf-8"))
        n_kanun, n_madde, n_mulga = kunye["n_kanun"], kunye["n_madde"], kunye["n_mulga"]
        return (
            f"Kapsam: {n_kanun} kanun · yürürlükteki {_nokta(n_madde - n_mulga)} madde "
            f"(toplam {_nokta(n_madde)}, mülga {_nokta(n_mulga)} elenir) "
            f"· {kunye.get('anlik_goruntu_tarihi', '?')} itibarıyla. "
            "Yönetmelik · tüzük · KHK · tebliğ YOK."
        )
    except (OSError, KeyError, json.JSONDecodeError):
        return ("Kapsam: yürürlükteki kanunlar (künye okunamadı — sayı belirsiz). "
                "Yönetmelik · tüzük · KHK · tebliğ YOK.")


ROZET = {
    Durum.CEVAP: "✅ CEVAP — dayanağı getirilen kaynaklarda",
    Durum.CEKINCELI: "⚠️ ÇEKİNCELİ — kısmen dayanaklı; atıfları kendiniz doğrulayın",
    Durum.SUSKUNLUK: "🤐 SUSKUNLUK — kaynaklarda karşılık bulunamadı",
    Durum.KESIK: "✂️ KESİK — üretim bütçesi bitti, cevap YARIM",
    # ⛔ KESİK'ten AYRI (ADR-0076): orada cümle yarım, burada cümle tam ama DAYANAĞI eksik.
    Durum.ARAMA_TUKENDI: "🔍 ARAMA TÜKENDİ — arama sınırına dayanıldı, dayanak EKSİK olabilir",
    # ⛔ SUSKUNLUK'tan AYRI (ADR-0081): orada arandı ve bulunamadı, burada HİÇ ARANMADI.
    Durum.BOS_SORGU: "⌨️ BOŞ SORU — soru yazılmadı; arama YAPILMADI",
}


_ALINTI_DESENI = re.compile(r"##begin_quote##(.*?)##end_quote##", re.DOTALL)

# Model işaretlerin İÇİNE çoğu zaman kendi düz tırnağını da yazıyor (göz kapısında
# 2026-09-11 görüldü). Yalnız SARAN çifti soyarız — ortada geçen bir iç alıntı silinmez.
# Kapsam bilinçli dar tutuldu (YAGNI): raporlanan kusur düz `"` ile; Türkçe „…” ve
# guillemet «…» aynı sınıfta olduğu için eklendi, tek tırnak `'…'` kapsam dışı bırakıldı.
_DIS_TIRNAK_CIFTLERI = (('"', '"'), ('„', '”'), ('«', '»'))


def _ic_tirnagi_soy(icerik: str) -> str:
    icerik = icerik.strip()
    for ac, kapa in _DIS_TIRNAK_CIFTLERI:
        if len(icerik) >= 2 and icerik[0] == ac and icerik[-1] == kapa:
            return icerik[1:-1].strip()
    return icerik


def alinti_isaretlerini_tirnaga_cevir(metin: str) -> str:
    """`##begin_quote##…##end_quote##` iskelesini SUNUM katmanında tipografik tırnağa çevirir.

    ⚠️ İşaret gürültü DEĞİL: modele eğitim verisinden "GOLD metinden kelimesi kelimesine
    alıntıla" diye öğretildi (B11) — taşıdığı bilgi *"burası kanunun kendi cümlesidir"*
    sınırıdır. Silinirse birebir kanun metni ile modelin kendi yorumu tipografik olarak
    ayırt edilemez hâle gelir; hukuk ürününde güven tam bu ayrıma dayanır.
    Eşleşmeyen tek başına kalan işaret SİLİNİR: kapanışı olmayan bir tırnak açmak,
    alıntının nerede bittiğine dair YANLIŞ bir sınır uydurmak olurdu.
    Model işaretlerin içine kendi tırnağını da yazdığında (göz kapısı, 2026-09-11) baştaki/
    sondaki boşluk kırpılır ve içeriği SARAN düz/„…”/«…» tırnak çifti soyulup tek
    tipografik tırnağa iner — çift tırnak + kaçak boşluk oluşmaz, ortadaki iç alıntı dokunulmaz kalır.

    ⛔ Yalnız sunum katmanında: `Cevap.metin` modelin ham çıktısıdır, `score_register.py:41`
    aynı işareti register göstergesi olarak SAYIYOR — ham alanı değiştirmek ölçümü bozar.
    `tui.py` bu fonksiyonu IMPORT eder, KOPYALAMAZ (S18'in dersi).
    """
    tirnakli = _ALINTI_DESENI.sub(lambda e: f"“{_ic_tirnagi_soy(e.group(1))}”", metin)
    return tirnakli.replace("##begin_quote##", "").replace("##end_quote##", "")


# Ölçülmüş sızıntı (2026-09-11, fp16 koşusu · `outputs/eval/gorev/g22-kv-fp16/`): model
# `istem.SISTEM_COK_KAYNAK`'ın son satırındaki yer tutucuyu — `(KANUN ADI, Madde X)` —
# harfiyen basıyor. 2/80 kalem (id 23 · 36); çıpa rejiminde 0/80.
_YER_TUTUCU_DESENI = re.compile(r"\(\s*KANUN ADI\s*(?=[,)])")


def yer_tutucu_atiflarini_isaretle(metin: str) -> str:
    """İstem yer tutucusunu (`(KANUN ADI, …`) DÜRÜST bir eksiklik işaretine çevirir.

    ⚠️ Niçin SİLMEK değil: parantezin içinde modelin ürettiği GERÇEK bir bilgi var —
    madde numarası. Parantezi tümden atmak vatandaşın doğrulayabileceği tek adresi yok
    ederdi. Olduğu gibi bırakmak ise daha kötüsüdür: `KANUN ADI` büyük harfli bir kanun
    ADI gibi okunur (korpustaki adlar da büyük harflidir — "İŞ KANUNU") ve vatandaş
    olmayan bir kanuna atıf yapıldığını sanır. İkisi de vatandaşa yalandır.
    Dürüst orta yol: numara KALIR, eksiklik AÇIKÇA yazılır — kusur GÖRÜNÜR olur, gizlenmez.

    ⛔ Yalnız sunum katmanında: `Cevap.metin` ham çıktıdır ve `scripts/` ölçüm hattı onu
    sayar (kusur 12a'nın emsali). Desen `istem.SISTEM_COK_KAYNAK`'taki BİREBİR literale
    çivilidir — büyük harfli biçim ölçülen biçimdir; uydurulmuş bir genelleme yapılmaz.
    """
    return _YER_TUTUCU_DESENI.sub("(kanun adı belirtilmemiş", metin)


def bicimle(cevap: Cevap, rozet: dict[Durum, str] = ROZET) -> str:
    """Cevabı insan okur biçime çevir. Yan etkisi yok — test edilebilsin diye ayrı.

    ⛔ **ÜRÜNÜN TEK SUNUM KATMANI** (kusur 17, insan kararı 2026-09-11). CLI · TUI · HTTP
    üçü de buradan geçer; `rozet` sözlüğü yüzeyler arasındaki TEK meşru farktır ve bu
    yüzden PARAMETREdir (bool bayrak değil — çağrı yerinde hangi sözlük olduğu okunur).
    ⚠️ Niçin böyle: `tui.py` kendi sunum dizesini kuruyordu ve birinci turda `bicimle()`'ye
    eklenen İKİ parça (iskele işareti süzgeci · kapsam satırı) TUI'de AYRI AYRI unutuldu.
    S18'in ölçülmüş dersi *"aynı metin iki yerde durursa sessizce ayrışır"* bir turda
    iki kez ısırdı. Buraya eklenen her parça artık üç yüzeye de KENDİLİĞİNDEN iner.
    """
    govde = yer_tutucu_atiflarini_isaretle(
        alinti_isaretlerini_tirnaga_cevir(cevap.metin.strip()))
    parcalar = [rozet[cevap.durum], "", govde, ""]
    if cevap.atiflar:
        parcalar.append("Atıflar:")
        for a in cevap.atiflar:
            isaret = "  ✓" if a.dogrulandi else "  ⚠️ DOĞRULANAMADI —"
            parcalar.append(f"{isaret} {a.kanun_no}/{a.madde_no}".rstrip())
        parcalar.append("")
    if cevap.kaynaklar:
        parcalar.append("Kaynaklar:")
        parcalar += [f"  [{k.sira}] {k.kanun_adi} {k.madde_no}" for k in cevap.kaynaklar]
        parcalar.append("")
    # ⚠️ Kapsam satırı KAYNAKLARIN hemen ardında, ibarenin ÜSTÜNDE (kusur 15, insan
    # kararı 2026-09-11). Gerekçe: kapsam bir OLGU şerhidir — "aranan korpus buydu" —
    # ve okunması gereken yer, cevabın dayandığı kaynak listesinin dibidir; sorumluluk
    # ibaresi ise HUKUKİ uyarıdır ve çıktının en güçlü cümlesi olarak SON satır kalır.
    # Buraya konduğu için üç yüzeye de (CLI · TUI · HTTP `sunum`) kendiliğinden iner.
    parcalar += [kapsam_satiri(), "", SORUMLULUK_IBARESI]
    return "\n".join(parcalar)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="hakhukuk", description="Türk hukuku asistanı")
    p.add_argument("soru", nargs="?", help="sorulacak soru")
    p.add_argument("-k", type=int, default=None, help="getirilecek kaynak sayısı")
    p.add_argument("--kuru-calisma", action="store_true",
                   help="model ve indeks olmadan çıktı biçimini göster (duman testi)")
    p.add_argument("--durumlari-listele", action="store_true",
                   help="dört durumu ve ne anlama geldiklerini yaz")
    a = p.parse_args(argv)

    if a.durumlari_listele:
        for d in Durum:
            print(f"{d.name:<10} {ROZET[d]}")
        return 0

    if not a.soru:
        p.error("soru gerekli (ya da --durumlari-listele)")

    if a.kuru_calisma:
        # Sunucu ve indeks GEREKMEZ: çıktı biçimi ve ibare, ağır bağımlılık olmadan sınanır.
        ornek = Cevap(metin=f"(kuru çalışma) soru alındı: {a.soru}",
                      durum=Durum.SUSKUNLUK, atiflar=(), kaynaklar=())
        print(bicimle(ornek))
        return 0

    from hakhukuk.cekirdek import servis  # noqa: PLC0415 — retriever ~2 GB, gecikmeli yüklenir
    cevap = servis.answer(a.soru, **({"k": a.k} if a.k else {}))
    print(bicimle(cevap))
    return 0


if __name__ == "__main__":
    sys.exit(main())
