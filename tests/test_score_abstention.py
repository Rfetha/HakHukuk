"""`exact_reject` — çekinme dedektörünün kalibrasyon davranışı.

Her test bir ÖLÇÜLMÜŞ yanlış sınıflandırmayı kilitliyor; hiçbiri varsayımsal değil.
Kaynak: G2 Adım 2.1 + 2.4b + 2.6 (2026-08-06), Gemini ailesi kalibrasyonu.
"""
import sys

import pytest
from score_abstention import exact_reject  # noqa: E402


# ── ADR-0058 açılış yeterlilik hükmü — kural İKİ KUTUPLU ────────────────────
# Ölçülen sapma iki yönlüydü: h1'de red=kötü (yanlış-pozitif rakibi kötü gösterir),
# h2b'de red=iyi (aynı hata rakibi iyi gösterir). Bu yüzden "muhafazakâr" savunması yok.

def test_exact_reject_olumlu_acilis_karsitlikla_cozulen_olumsuzlamaya_kanmaz():
    """YANLIŞ-POZİTİF kutbu — `h2b_fl35_k4` id=18'in GERÇEK metni.

    Olumsuzlama "ancak ... m.80 kapsamında yer almaktadır" ile ÇÖZÜLÜYOR: bu dolu bir
    cevap. Son esaslı ibare olumsuzlama değil, çözüm cümlesidir."""
    cevap = ("Verilen kaynaklar soruyu doğrudan cevaplamaktadır.  Verilen kaynaklarda zorla "
             "fuhşa sevketme fiilinin insanlığa karşı bir suç olarak düzenlendiğine dair bir "
             "ifade bulunmamaktadır; ancak bu fiil insan ticareti suçunu düzenleyen Türk Ceza "
             "Kanunu Madde 80 kapsamında yer almaktadır. (TÜRK CEZA KANUNU, Madde 80)")
    assert exact_reject(cevap, "data") is False


def test_exact_reject_olumlu_acilis_govdedeki_kaynak_yoklugu_beyanina_yenilir():
    """YANLIŞ-NEGATİF kutbu — `h2b_fl35_k4` id=5'in GERÇEK metni.

    Kural 334880d'de olumlu açılışı BAĞLAYICI saymıştı; bu, modelin kendi (yanlış) beyanını
    gerçek davranışının önüne koyuyordu. Cevap kendi açılışını cümle sonunda yalanlıyor."""
    cevap = ("Verilen kaynaklar soruyu cevaplamaktadır.   Verilen kaynaklarda bir çocuğu fuhşa "
             "teşvik eden kişiye verilecek cezayı doğrudan düzenleyen özel bir madde "
             "bulunmamaktadır. Bu nedenle verilen kaynaklarda bu konuyu düzenleyen yeterli "
             "madde bulunmuyor.")
    assert exact_reject(cevap, "data") is True


def test_exact_reject_son_esasli_ibare_salt_atif_parantezini_atlar():
    """`h2b_fl35_k4` id=76: cevap bir atıf paranteziyle bitiyor. Atıf hüküm taşımaz;
    son ibare sayılırsa gerçek sonuç (kaynak-yokluğu beyanı) görünmez olur."""
    cevap = ("Verilen kaynaklar soruyu cevaplamaktadır.  Verilen kaynaklarda borçlunun beyan "
             "yükümlülüğü düzenlenmiştir; ancak kaynaklarda borçlu ile başka birinin malı "
             "birlikte elinde bulundurması durumunda kimin mal sahibi sayılacağına dair bir "
             "düzenleme bulunmamaktadır.   (İCRA VE İFLAS KANUNU, Madde 85)")
    assert exact_reject(cevap, "data") is True


def test_exact_reject_olumsuz_yeterlilik_acilisi_red_sayilir():
    """Simetrinin öbür yarısı: bu kalıp REJECT_RE'nin HİÇBİR desenine uymuyordu,
    3 kalem sessizce 'cevapladı' sayılıyordu (h2b_fl35_k4'te 1)."""
    assert exact_reject("Verilen kaynaklar soruyu cevaplamamaktadır.", "data") is True
    assert exact_reject("Verilen kaynak metni soruyu cevaplamaz.", "data") is True


def test_exact_reject_acilis_hukmu_yoksa_govde_taranir():
    assert exact_reject("Verilen kaynaklarda bu konuyu düzenleyen madde bulunmuyor.",
                        "data") is True
    assert exact_reject("Mahkeme lehine karar verirse icra emri tebliğ edilir "
                        "(İİK m.32).", "data") is False


@pytest.mark.xfail(strict=True, reason=(
    "🔴 AÇIK BORÇ (kusur Ö-E, 2026-08-06). `_son_esasli_ibare` yalnız SON esaslı ibareye "
    "bakıyor; çekinme beyanı sonuç konumunda olup ARKASINDAN sonuç-dışı bir tavsiye cümlesi "
    "gelirse kural onu göremez. ÖLÇÜLDÜ ve kapatılmadı: tüm `outputs/eval`'da olumlu açılışlı "
    "96 cevabın **0'ı** bu şekle uyuyor (gövdede red + son ibarede red yok = 3 vaka, üçü de "
    "GERÇEKTEN dolu cevap; son ibaresi tavsiye/başvuru kalıbıyla biten 4 vaka, dördü de "
    "gerçekten dolu). Yani kuralı bugün onarmanın ölçülmüş bir dayanağı YOK ve körlemesine "
    "genişletmek yeni yanlış-pozitif üretir (ADR-0050 ruhu). Bu test kusuru KİLİTLEMEZ, "
    "SINIRI çizer: kural düzelirse strict=True ile PATLAR ve damga kaldırılmak zorunda kalır."))
def test_exact_reject_cekinme_sonrasi_tavsiye_kuyrugu_kacar():
    """Sınır vakası — kural bugün bunu 'cevapladı' sayıyor, oysa çekinmedir."""
    cevap = ("Verilen kaynaklar soruyu cevaplamaktadır. Kaynaklarda bu konu düzenlenmiyor. "
             "Bu konuda güncel mevzuata başvurmanız gerekir.")
    assert exact_reject(cevap, "data") is True


# ── Kanunun kendi KOŞUL kipi red değildir (#39'un `(?!sa)` ilkesi) ──────────

def test_exact_reject_kosul_kipi_red_sayilmaz():
    """Gemini bu iki kalıbı DOLU cevabın ortasında kullanıyordu; 998 ve 1904
    karakterlik tam cevaplar çekinme sayılıyordu."""
    assert exact_reject("ilamda belirtilen süre içinde (süre belirtilmemişse işin "
                        "mahiyetine göre belirlenen sürede) işin yapılması emredilir.",
                        "data") is False
    assert exact_reject("Yapı bölümleri mevcut değilse, hava hakkı kendiliğinden kat "
                        "irtifakına çevrilir (Kat Mülkiyeti Kanunu, Madde 52).",
                        "data") is False
    # #39'un asıl vakası korunuyor
    assert exact_reject("kanunda hüküm bulunmazsa hâkim karar verir.", "data") is False


def test_exact_reject_koşul_kipi_olmayan_olumsuzlama_red_kalir():
    """Daraltma fazla geniş olmasın: koşul eki YOKSA red tespiti sürmeli."""
    assert exact_reject("Bu konu kaynakta belirtilmemiştir.", "data") is True
    assert exact_reject("Bu bilgi mevcut değildir.", "data") is True
    assert exact_reject("Bu husus söz konusu değildir.", "data") is True


# ── Mod duyarlılığı (ADR-0044) korunuyor ───────────────────────────────────

def test_exact_reject_kor_modda_feragat_cumlesi_red_sayilmaz():
    cevap = ("Türk Ceza Kanunu'na göre ceza verilir. Güncel mevzuat için "
             "bir avukata danışmanızı öneririm.")
    assert exact_reject(cevap, "blind") is False
    assert exact_reject(cevap, "data") is True


# ── K3: payda (valid_trap) CEVAPTAN BAĞIMSIZ olmalı ─────────────────────────
# Ölçülen kusur: `judge()` soruyu, kaynağı ve CEVABI tek çağrıda veriyordu; aynı sınavda
# 80 kalemin 19'unda üç kol farklı `source_answers` alıyor, `valid_traps` 45/56/50 oluyordu.

def test_gecerlilik_anahtari_cevaptan_bagimsiz():
    """Anahtar yalnız (soru, kaynak) üzerinden — cevap girmiyor, giremez."""
    from score_abstention import gecerlilik_anahtari
    assert (gecerlilik_anahtari("Soru?", "KAYNAK metni")
            == gecerlilik_anahtari("Soru?", "KAYNAK metni"))
    assert (gecerlilik_anahtari("Soru?", "KAYNAK metni")
            != gecerlilik_anahtari("Soru?", "BAŞKA kaynak"))


def test_gecerlilik_anahtari_HAKEM_ISTEMINE_ESIT():
    """⭐ KARAR-4 m.1 (2026-08-06) — anahtar, hakemin GERÇEKTEN gördüğü metnin fonksiyonu.

    K-1 anahtarı TAM metne taşımıştı; ölçüm o onarımın **sayısal** karşılığı olmadığını
    gösterdi (15/15 aynı hüküm) ve bir gürültü yolu açtı: hakemin AYIRT EDEMEDİĞİ bir
    farka göre bölünen anahtar, *aynı istem → aynı cevap* değişmezini kırar. Ölçüldü:
    5.363 ayrı istemin **65'i** birden fazla anahtara düşüyor, **83** çağrı garanti
    gereksiz, ve aynı istem iki kayda dönerse `Rej*` ~1,5 p oynar (saf gürültü).

    Sınanan şey vekil DEĞİL: hakeme giden metin `hakem_kaynagi()`'ndan çıkıyor ve anahtar
    da aynı fonksiyondan besleniyor — ikisi ayrışırsa bu test düşer.
    """
    from score_abstention import gecerlilik_anahtari, hakem_kaynagi, SOURCE_CLIP
    onek = "A" * SOURCE_CLIP
    # Hakem ikisini AYIRT EDEMEZ (istem bayt-bayt aynı) → anahtar da ayırmamalı.
    assert hakem_kaynagi(onek + "kuyruk-A") == hakem_kaynagi(onek + "kuyruk-B")
    assert gecerlilik_anahtari("S", onek + "kuyruk-A") == gecerlilik_anahtari("S", onek + "kuyruk-B")
    # Klip İÇİNDE ayrışan metinler farklı istem → farklı anahtar (kural tek yöne bozulmasın).
    assert gecerlilik_anahtari("S", "KAYNAK bir") != gecerlilik_anahtari("S", "KAYNAK iki")
    assert gecerlilik_anahtari("S", "KAYNAK bir") != gecerlilik_anahtari("T", "KAYNAK bir")


def test_hakem_isteminden_TASAN_METIN_ANAHTARA_GIRMEZ():
    """Uçtan uca değişmez: `gecerlilik_istemi` AYNI iken anahtar da AYNI olmalı.
    İstem metni ile anahtar arasına klip farkı giremez.

    🚨 SENARYO DEĞİŞTİ 2026-09-07 — bu test eskiden bir KUSURU belgeliyordu.
    `SOURCE_CLIP = 3500` iken `k=4` bağlamı `k=10`'unkinin ÖNEKİ olduğu için ikisi TEK
    önbellek kaydına düşüyordu; bedeli "kabul edilmiş" sayılıp `k=10`'un paydası
    **TANIMSIZ** damgalanmıştı (KARAR-4 m.2). **F0.5 o bedeli ÖDEDİ** (2026-09-07,
    açık soru S4 / borç YB3): `SOURCE_CLIP` **3500 → 12000**, gözlenen en büyük bağlam
    10.549 + %14 pay. Ölçülen sonuç: `gecerlilik_devralinan` **65 → 0**, 80/80 kalem
    kendi bağlamıyla hükme bağlandı (`outputs/eval/faz0/f05-source-clip/SONUC.md`).

    ⇒ Test artık çakışmayı DEĞİL, çakışmanın YOKLUĞUNU korur. Aşağıdaki ilk blok
    F0.5'in satın aldığı şeydir ve geri gelirse bu test düşer.
    """
    from score_abstention import SOURCE_CLIP, gecerlilik_anahtari, gecerlilik_istemi
    soru = "Kat maliki ortak gideri ödemezse ne olur?"
    kaynak = lambda a, b: "".join(f"[KAYNAK {i}]\n{'m' * 900}\n" for i in range(a, b))
    k4, k10 = kaynak(1, 5), kaynak(1, 11)

    # (1) F0.5'İN SATIN ALDIĞI: k=4 ↔ k=10 artık AYRI kayıtlar.
    assert k10.startswith(k4), "gerçek şekil korunuyor: k4, k10'un önekidir"
    assert len(k10) < SOURCE_CLIP, "k=10 bağlamı klibin İÇİNDE kalmalı (12000)"
    assert gecerlilik_istemi(soru, k4) != gecerlilik_istemi(soru, k10)
    assert gecerlilik_anahtari(soru, k4) != gecerlilik_anahtari(soru, k10)

    # (2) DEĞİŞMEZ YERİNDE: klibi AŞAN fark hakeme görünmez ⇒ anahtara da girmez.
    tasan = kaynak(1, 20)
    assert len(tasan) > SOURCE_CLIP, "bu blok ancak klip aşılırsa anlamlı"
    assert gecerlilik_istemi(soru, tasan) == gecerlilik_istemi(soru, tasan + "KUYRUK")
    assert gecerlilik_anahtari(soru, tasan) == gecerlilik_anahtari(soru, tasan + "KUYRUK")


# ── KARAR-2: BOŞ BAĞLAMDA PAYDA TANIM GEREĞİ 80/80 (ADR-0048 m.2) ──────────
# Ölçülen kusur: cp09'un AYNI M3 sınavında üç kol 54 · 56 · 39 payda gösterdi. Kural
# aletin dışında (`valid_trap_cache.py`) durduğu için skorlama varsayılan
# `--source-field referans` ile ALTIN maddeyi hakeme gösteriyor, hakem "kaynak
# cevaplıyor" deyip tuzağı geçersiz sayıyordu. Üç sayı da yanlıştı.

def test_payda_tanimdan_gecerli_yalniz_bos_baglam_modunda():
    from score_abstention import payda_tanimdan_gecerli
    assert payda_tanimdan_gecerli("empty") is True
    assert payda_tanimdan_gecerli("oracle") is False
    assert payda_tanimdan_gecerli("distractor_nogold") is False
    assert payda_tanimdan_gecerli("harness") is False
    assert payda_tanimdan_gecerli(None) is False


def test_bos_baglam_kosusu_paydayi_HAKEMSIZ_ve_TAM_verir(tmp_path, monkeypatch):
    """Uçtan uca: `mode=empty` + `--pay-kaynagi onceki` → SIFIR ağ çağrısı, payda n/n.

    Bu test hem KARAR-2'yi (payda 80/80) hem `--pay-kaynagi onceki` sözleşmesini
    kilitler. Ağ çağrısı olursa `make_client` kimlik ister ve test çöker — yani
    "hakeme gitmedi" iddiası gerçekten sınanıyor, varsayılmıyor.
    """
    import json
    import subprocess

    d = tmp_path / "kosu"
    d.mkdir()
    # `referans` DOLU: eski kusurun tam koşulu — hakem görseydi "cevaplıyor" derdi.
    detay = [{"id": i, "soru": f"Soru {i}?", "cevap": "Verilen kaynaklarda bu konu yok.",
              "mode": "empty", "context_shown": "",
              "referans": "Madde 1 — Bu madde soruyu tam olarak cevaplar."} for i in range(4)]
    with open(d / "m3_test_detail.jsonl", "w", encoding="utf-8") as f:
        for r in detay:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump([{"id": i, "verdict": "ABSTAIN", "used_parametric": False, "reason": "x"}
               for i in range(4)],
              open(d / "abst_m3_test.jsonl", "w", encoding="utf-8"))

    ortam = {k: v for k, v in __import__("os").environ.items()
             if k not in ("OPENAI_API_KEY", "OPENROUTER_API_KEY")}
    ortam["OPENAI_BUDGET_USD"] = "0.01"
    p = subprocess.run(
        [sys.executable, "scripts/puanlama/score_abstention.py",
         "--details", str(d / "m3_test_detail.jsonl"), "--label", "m3_test",
         "--out-dir", str(d), "--pay-kaynagi", "onceki",
         "--gecerlilik-onbellek", str(tmp_path / "onbellek.json")],
        capture_output=True, text=True, env=ortam)
    assert p.returncode == 0, p.stdout + p.stderr
    ozet = json.load(open(d / "abst_m3_test_summary.json", encoding="utf-8"))
    assert ozet["valid_traps"] == 4, "boş bağlamda payda TANIM gereği n/n olmalı"
    assert ozet["invalid_traps"] == 0
    assert ozet["gecerlilik_tanimdan"] == 4
    assert ozet["judge_cost_usd"] == 0.0, "hiçbir hakem çağrılmamalıydı"
    assert not (tmp_path / "onbellek.json").exists() or \
        json.load(open(tmp_path / "onbellek.json", encoding="utf-8"))["cache"] == {}, \
        "TANIM kararı içerik-adresli önbelleğe SIZMAMALI"


def test_pay_kaynagi_onceki_verdict_dosyasi_yoksa_ERKEN_PATLAR(tmp_path):
    """Sessizce boş verdict'le devam etmek yerine dur (ADR-0026 ruhu)."""
    import json
    import subprocess
    d = tmp_path / "kosu"
    d.mkdir()
    with open(d / "x_detail.jsonl", "w", encoding="utf-8") as f:
        f.write(json.dumps({"id": 0, "soru": "S?", "cevap": "C", "mode": "empty"}) + "\n")
    p = subprocess.run(
        [sys.executable, "scripts/puanlama/score_abstention.py", "--details", str(d / "x_detail.jsonl"),
         "--label", "x", "--out-dir", str(d), "--pay-kaynagi", "onceki"],
        capture_output=True, text=True)
    assert p.returncode != 0
    assert "abst_x.jsonl" in (p.stdout + p.stderr)


# ── K1: ÖNBELLEK KAYDI HAKEM YIĞINIYLA BİRLİKTE OKUNUR (tuzak 2.7 · ADR-0029) ──
# Ölçülen kusur: anahtar (soru, kaynak) taşıyor, hakem yığınını taşımıyor; okuma yolunda tek
# kontrol `if anahtar in onbellek`, kayıttaki `hakem` alanı HİÇ okunmuyordu. `cp2c_kabul.sh`
# `LLM_GATEWAY=openai` ile koşuyor → ortak önbelleğe openai damgası yazılıyor, sonraki
# openrouter ölçümü onu sessizce devralıp `judge_gateway: "openrouter"` yazıyordu.

def _onbellek_yaz_ham(yol, cache):
    import json
    json.dump({"n": len(cache), "cache": cache}, open(yol, "w", encoding="utf-8"),
              ensure_ascii=False)


def _m2_kosusu_kur(tmp_path, soru, kaynak):
    """`mode=data` + `--pay-kaynagi onceki` → payda dışında HİÇBİR çağrı yok."""
    import json
    d = tmp_path / "kosu"
    d.mkdir(exist_ok=True)
    with open(d / "m2_x_detail.jsonl", "w", encoding="utf-8") as f:
        f.write(json.dumps({"id": 0, "soru": soru, "cevap": "Cevap.", "mode": "data",
                            "referans": kaynak}, ensure_ascii=False) + "\n")
    json.dump([{"id": 0, "verdict": "FABRICATE", "used_parametric": False, "reason": "x"}],
              open(d / "abst_m2_x.jsonl", "w", encoding="utf-8"))
    return d


def _kosur(d, onbellek, kapi):
    import os
    import subprocess
    ortam = {k: v for k, v in os.environ.items()
             if k not in ("OPENAI_API_KEY", "OPENROUTER_API_KEY")}
    ortam["LLM_GATEWAY"] = kapi
    return subprocess.run(
        [sys.executable, "scripts/puanlama/score_abstention.py", "--details", str(d / "m2_x_detail.jsonl"),
         "--label", "m2_x", "--out-dir", str(d), "--pay-kaynagi", "onceki",
         "--gecerlilik-onbellek", str(onbellek)], capture_output=True, text=True, env=ortam)


def test_onbellek_BASKA_KAPIDAN_yazilmis_paydayi_DEVRALMAZ(tmp_path):
    """🚨 K1 — openai kapısının damgası openrouter koşusuna SESSİZCE geçmemeli."""
    from score_abstention import gecerlilik_anahtari
    soru, kaynak = "Kira sözleşmesi nasıl feshedilir?", "Madde 1 — alakasız hüküm."
    onbellek = tmp_path / "onbellek.json"
    _onbellek_yaz_ham(str(onbellek), {gecerlilik_anahtari(soru, kaynak): {
        "gecerli": True, "reason": "x", "hakem": "gpt-4o", "kapi": "openai"}})
    p = _kosur(_m2_kosusu_kur(tmp_path, soru, kaynak), onbellek, "openrouter")
    assert p.returncode != 0, "farklı kapıdan gelen payda sessizce devralındı"
    assert "YIĞIN UYUŞMAZLIĞI" in (p.stdout + p.stderr)


def test_onbellek_AYNI_YIGINDAN_yazilmis_paydayi_DEVRALIR(tmp_path):
    """Denetim fazla katı olmasın: yığın aynıysa devralma çalışmaya devam eder ($0)."""
    import json
    from score_abstention import gecerlilik_anahtari
    soru, kaynak = "Kira sözleşmesi nasıl feshedilir?", "Madde 1 — alakasız hüküm."
    onbellek = tmp_path / "onbellek.json"
    _onbellek_yaz_ham(str(onbellek), {gecerlilik_anahtari(soru, kaynak): {
        "gecerli": True, "reason": "x", "hakem": "openai/gpt-4o", "kapi": "openrouter"}})
    d = _m2_kosusu_kur(tmp_path, soru, kaynak)
    p = _kosur(d, onbellek, "openrouter")
    assert p.returncode == 0, p.stdout + p.stderr
    ozet = json.load(open(d / "abst_m2_x_summary.json", encoding="utf-8"))
    assert ozet["gecerlilik_maliyet_usd"] == 0.0
    assert ozet["gecerlilik_onbellekten"] == 1


def test_onbellek_YIGIN_DAMGASIZ_kaydi_DEVRALMAZ(tmp_path):
    """Damgasız (eski şema) kayıt da uyuşmazlıktır — 'bilinmiyor' sessizce 'uyuyor' olamaz."""
    from score_abstention import gecerlilik_anahtari
    soru, kaynak = "Kira sözleşmesi nasıl feshedilir?", "Madde 1 — alakasız hüküm."
    onbellek = tmp_path / "onbellek.json"
    _onbellek_yaz_ham(str(onbellek), {gecerlilik_anahtari(soru, kaynak): {
        "gecerli": True, "reason": "x", "hakem": "openai/gpt-4o"}})     # `kapi` YOK
    p = _kosur(_m2_kosusu_kur(tmp_path, soru, kaynak), onbellek, "openrouter")
    assert p.returncode != 0
    assert "YIĞIN UYUŞMAZLIĞI" in (p.stdout + p.stderr)


# ── Ö5: `gecerlilik_devralinan` İKİ AYRI ŞEYİ SAYIYORDU ─────────────────────
# `--payda-kaynagi onceki` devralması (kendi eski skorlamasından toptan) ile önbellek isabeti
# (başka koşuyla sınav paylaşımı) aynı sayacı artırıyordu; anlamları taban tabana zıt ve
# tuzak 2.17'nin kontrolü (*"devralınan >0 ise hangi koşuyla sınav paylaştığı gösterilebilmeli"*)
# tam bu alana dayanıyordu — koşulamıyordu. Ölçülen karışım: `olcum-h2b-k10` 65 (önbellek)
# ↔ `cp09-ab-ayrimi` 70 (önceki koşu).

def test_ozet_onbellek_isabetini_ONCEKI_KOSU_devralmasindan_AYIRIR(tmp_path):
    import json
    d = _m2_kosusu_kur(tmp_path, "Soru?", "Madde 1 — alakasız.")
    json.dump([{"id": 0, "verdict": "FABRICATE", "valid_trap": True, "reason": "x",
                "valid_trap_anahtari": "ESKI", "valid_trap_reason": "y"}],
              open(d / "abst_m2_x.jsonl", "w", encoding="utf-8"))
    import os
    import subprocess
    ortam = {k: v for k, v in os.environ.items()
             if k not in ("OPENAI_API_KEY", "OPENROUTER_API_KEY")}
    p = subprocess.run(
        [sys.executable, "scripts/puanlama/score_abstention.py", "--details", str(d / "m2_x_detail.jsonl"),
         "--label", "m2_x", "--out-dir", str(d), "--pay-kaynagi", "onceki",
         "--payda-kaynagi", "onceki", "--gecerlilik-onbellek", str(tmp_path / "yok.json")],
        capture_output=True, text=True, env=ortam)
    assert p.returncode == 0, p.stdout + p.stderr
    ozet = json.load(open(d / "abst_m2_x_summary.json", encoding="utf-8"))
    assert ozet["gecerlilik_onceki_kosudan"] == 1
    assert ozet["gecerlilik_onbellekten"] == 0, "iki sayaç aynı kutuya düşmemeli"


def test_onbellek_yazimi_diskteki_kalemleri_silmez(tmp_path):
    """İki skorlama aynı önbelleğe yazıyor; ikincisi birincinin kalemini silmemeli."""
    from score_abstention import onbellek_yaz, onbellek_oku
    yol = str(tmp_path / "onbellek.json")
    onbellek_yaz(yol, {"a": {"gecerli": True}})
    onbellek_yaz(yol, {"b": {"gecerli": False}})
    okunan = onbellek_oku(yol)
    assert set(okunan) == {"a", "b"}


def test_onbellek_es_zamanli_yazimda_kalem_KAYBETMEZ(tmp_path):
    """🚨 KAYIP GÜNCELLEME kapısı — kilitsiz oku-birleştir-yaz'da bu test DÜŞER.

    Sekiz süreç aynı önbelleğe farklı anahtar yazıyor; hepsi diskteki hâli kilitten ÖNCE
    okumuş olsa bile hiçbiri diğerinin kalemini silmemeli. Ödenmiş hakem kaleminin sessizce
    yok olması bu hattın en pahalı hata sınıfı."""
    import json
    import multiprocessing as mp
    from score_abstention import onbellek_oku

    yol = str(tmp_path / "onbellek.json")
    json.dump({"n": 0, "cache": {}}, open(yol, "w", encoding="utf-8"))

    def yaz(anahtar):
        import sys
        import time
        from score_abstention import onbellek_yaz, onbellek_oku
        onbellek_oku(yol)            # bayat kopya: herkes önce okusun
        time.sleep(0.05)             # ...sonra hep birlikte yazsın
        onbellek_yaz(yol, {anahtar: {"gecerli": True}})

    ctx = mp.get_context("fork")
    isciler = [ctx.Process(target=yaz, args=(f"k{i}",)) for i in range(8)]
    for p in isciler:
        p.start()
    for p in isciler:
        p.join(timeout=30)
    assert all(p.exitcode == 0 for p in isciler)
    assert set(onbellek_oku(yol)) == {f"k{i}" for i in range(8)}
    assert not list(tmp_path.glob("*.tmp*")), "atomik replace sonrası geçici dosya kalmamalı"


# ── ADR-0061 Karar 1 — ÖNSÖZSÜZ REJİMDE AÇILIŞ HÜKMÜ ────────────────────────
# Ölçülen kusur (#60, 2026-09-06): önsözsüz rejimde ADR-0058 yeterlilik hükmü hiç
# oluşmuyor (`_acilis_yeterlilik_hukmu` → None: hasatta 26/26, ÖNSÖZLÜ resmî çıpada
# bile 75/80). O dalda `exact_reject` cevabın TAMAMINI tarıyordu; havuzun cevap şablonu
# ise elenen kaynakların gerekçesini ("Diğer kaynaklar … içermemektedir") gövdenin
# BAŞINDA taşıyor → tam ve atıflı cevaplar "çekinme" sayılıyordu (10 kabul kaleminin 6'sı).
#
# ⚠️ Naif "yalnız son ibareye bak" çözümü TERS yönde kırıyor: gerçek çekinmelerin hükmü
# AÇILIŞTA ("Verilen kaynaklarda bu konuyu düzenleyen madde bulunmuyor. Kaynaklar …")
# ve son ibare açıklama cümlesidir. Aşağıdaki 13 vaka iki yönü BİRLİKTE kilitliyor;
# hepsi #60'ta GÖZLE OKUNDU, hiçbiri varsayımsal değil.

# Kaynak: data/_ham_ve_ara/b10-pilot/b10_np1.jsonl · alan `rejected` (Görev 3 pilotu)
_HASAT_CEVAP = {
    "raft11188":
        "1) İtiraz süresi ile ilgili bilgi, yalnızca KAYNAK 1'de yer alan İcra ve İflas Kanunu Madde 225'te belirtilmiştir. Diğer kaynaklar, itiraz süresiyle ilgili doğrudan bir düzenleme içermemektedir.\n\n2) ##begin_quote## \"Alacaklılar toplanmasının kararlarından dolayı her alacaklı tarafından yedi gün içinde icra mahkemesine şikayet olunabilir.\" ##end_quote##\n\n3) Sonuç olarak, itiraz süresi yedi gündür (İCRA VE İFLAS KANUNU, Madde 225).",
    "raft12319":
        "1) KAYNAK 1, sosyal güvenlik ve sosyal yardım kurumlarından yapılan ödemelerin mal paylaşımına etkisini düzenleyen tek kaynak olarak belirgin bir şekilde konuya değinmektedir. Diğer kaynaklar, mal paylaşımı ile ilgili farklı konuları ele almakta olup, sosyal güvenlik tazminatı ile ilgili bir düzenleme içermemektedir.\n\n2) ##begin_quote## \"Eşlerden birine sosyal güvenlik veya sosyal yardım kurumlarınca yapılmış olan toptan ödemeler veya iş gücünün kaybı dolayısıyla ödenmiş olan tazminat, toptan ödeme veya tazminat yerine ilgili sosyal güvenlik veya sosyal yardım kurumunca uygulanan usule göre ömür boyunca irat bağlanmış olsaydı, mal rejiminin sona erdiği tarihte bundan sonraki döneme ait iradın peşin sermayeye çevrilmiş değeri ne olacak idiyse, tasfiyede o miktarda kişisel mal olarak hesaba katılır.\" ##end_quote##\n\n3) Sonuç olarak, sosyal güvenlikten alınan tazminat, mal paylaşımında kişisel mal olarak değerlendirilir ve tasfiye sırasında hesaba katılır (TÜRK MEDENİ KANUNU, Madde 228).",
    "raft1328":
        "1) KAYNAK 4, mahkemenin sanığı mahkeme salonundan çıkarıp tekrar getirme sürecini düzenleyen tek kaynak olarak sorunun cevabını doğrudan karşılamaktadır. Diğer kaynaklar, tercüman atama, sorgu ve dinleme, duruşma disiplini gibi konulara odaklanmakta olup, sanığın geri getirilmesiyle ilgili bilgi içermemektedir.\n\n2) ##begin_quote## \"Sanık tekrar getirildiğinde, tutanaklar okunur ve gerektiğinde içeriği anlatılır.\" ##end_quote##\n\n3) Sonuç olarak, mahkeme sanığı mahkeme salonundan çıkarıp tekrar getirebilir ve bu süreçte tutanaklar okunarak içeriği anlatılabilir (CEZA MUHAKEMESİ KANUNU, Madde 200).",
    "raft3230":
        "1) İcra takibi, askerlik hizmetinin devamı süresince belirli askerlik birimlerine ait erler için durdurulmaktadır. Bu durum, askerlik hizmetinin devamı süresince erlerin, onbaşıların ve kıta çavuşlarının icra takibiyle ilgili haklarını korumaktadır.\n\n2) İlgili kaynak, İcra ve İflas Kanunu Madde 54'tür. Bu madde, askerlik hizmetinin devamı süresince erlerin icra takibiyle ilgili haklarını düzenlemektedir. Diğer kaynaklar, icra takibiyle ilgili farklı konuları ele almakta olup, askerlik hizmetine dair bir düzenleme içermemektedir.\n\n3) Sonuç olarak, askerlik hizmetinin devamı süresince erler, onbaşılar ve kıta çavuşları icra takibiyle ilgili haklarını korumaktadır. (İCRA VE İFLAS KANUNU, Madde 54)",
    "raft5789":
        "Şans oyunları için dava açmanın bir yolu olup olmadığına dair en doğrudan bilgi, Türk Borçlar Kanunu'nun ilgili maddesinde yer almaktadır. Diğer kaynaklar, kumar ve bahis ile ilgili genel hükümler içermekte olup, şans oyunları ile doğrudan ilgili değildir.\n\n**Güncel Kaynak:**\nKAYNAK 5\n\n**Cevap:**\nŞans oyunları için dava açmanın bir yolu bulunmamaktadır; düzenlenmesine kanun veya yetkili makamlarca izin verilmiş olmadıkça, piyango ve diğer şans oyunlarından doğan alacaklar hakkında dava açılamaz ve takip yapılamaz. (TÜRK BORÇLAR KANUNU, Madde 606)",
    "raft10304":
        "Evet, devlet zararı karşıladıktan sonra kusurlu olanlardan birini dava edebilir. Bu durum, Türk Medeni Kanunu'nun ilgili maddesinde açıkça belirtilmiştir.\n\n**Güvenilir Kaynak:**\nKAYNAK 3\n\n**Gözden Geçirme:**\nKAYNAK 1, 2 ve 5, vasi ve vesayet organlarının sorumluluğu ile ilgili genel hükümler içermekte olup, devletin rücu hakkı ile ilgili doğrudan bir düzenleme içermemektedir. KAYNAK 4, rücu davasının mahkeme yetkisini düzenlemekte olup, madde 468'deki rücu hakkı ile doğrudan bağlantılıdır.\n\n**Cevap:**\nDevlet, vesayet dairelerinde görevli olanların hukuka aykırı olarak sebebiyet verdikleri zararlardan doğrudan doğruya sorumlu olduğu gibi; vasi, kayyım ve yasal danışmanlara tazmin ettirilemeyen zararlardan da sorumludur. Zararı tazmin eden Devlet, zararın meydana gelmesinde kusurlu olanlara rücu eder. (TÜRK MEDENİ KANUNU, Madde 468)",
}

_HASAT_CEKINME = {
    "raft8972":
        "Verilen kaynaklarda bu konuyu düzenleyen madde bulunmuyor. Kaynaklar, kat mülkiyeti ile ilgili tanımlar ve geçici düzenlemeler içermekte olup, yönetim planı değişikliği sonrası yeni yöneticilerin seçimi ile ilgili bilgi sunmamaktadır.",
    "raft3488":
        "Verilen kaynaklarda bu konuyu düzenleyen genel bir madde bulunmamaktadır; kaynaklar yalnızca belirli suçlar için hapis cezası sürelerini belirtmektedir.",
    "raft382":
        "Verilen kaynaklarda bu konuyu düzenleyen madde bulunmuyor.",
    "raft12744":
        "Verilen kaynaklarda bu konuyu düzenleyen madde bulunmuyor. Kaynaklar, konkordato projesinin değerlendirilmesiyle ilgili doğrudan bilgi sunmamaktadır.",
}

# Kaynak: outputs/eval/sprint2-olcum/olcum-bi/h1_tgta_v1_bi_k10_detail.jsonl · alan `cevap` (resmî çıpa)
_CIPA = {
    7: (True, "Verilen kaynaklar arasında bu konuyu düzenleyen madde bulunmamaktadır. İlgili düzenleme İş Kanunu'nun 21. maddesinde yer almakta olup, bu madde kesinleşmiş bir kararın işçiye işe başlatma yükümlülüğünü ve tazminat haklarını düzenlemektedir."),
    19: (False, "KAYNAK 1, promosyon uygulamalarında hangi tür mal veya hizmet verilebileceğine dair doğrudan bilgi sunmaktadır. Diğer kaynaklar, promosyon uygulamalarıyla ilgili spesifik düzenlemeler içermemektedir.\n\n**Cevap:** Promosyon uygulamalarında, yönetmelikle belirlenen süreli yayıncılık amaçlarına uygun kültürel mal veya hizmetler dışında başka bir mal veya hizmet verilemez. (TÜKETİCİNİN KORUNMASI HAKKINDA KANUN, Madde 53)"),
    20: (True, "Verilen kaynaklar arasında bu konuyu düzenleyen madde bulunmamaktadır. İlgili düzenleme, yıllık ücretli izin hakkının hesaplanmasında çalışılmış gibi sayılan süreleri belirten İŞ KANUNU Madde 55'te yer almaktadır. Ancak bu madde, tatil günlerinin nasıl hesaplandığını açıklamakta, ancak doğrudan tatil günlerinin varlığını düzenlememektedir."),
}

@pytest.mark.parametrize("kalem", sorted(_HASAT_CEVAP))
def test_exact_reject_onsozsuz_hasat_atifli_cevabi_cekinme_saymaz(kalem):
    """🚨 #60'ın manşeti: `rejected` alanı tam ve doğru atıflı bir CEVAP.

    Tetikleyen ibare cevabın hükmü değil, ELENEN kaynakların gerekçesidir
    (`… Diğer kaynaklar … içermemektedir`). Hüküm `3) Sonuç olarak …` satırındadır.
    """
    assert exact_reject(_HASAT_CEVAP[kalem], "data") is False


@pytest.mark.parametrize("kalem", sorted(_HASAT_CEKINME))
def test_exact_reject_onsozsuz_hasat_gercek_cekinmeyi_kacirmaz(kalem):
    """Onarımın öbür yönü: red hükmü AÇILIŞTA, son ibare yalnız açıklama.

    `raft8972` · `raft3488` · `raft12744` son ibarelerinde REJECT_RE'nin hiçbir deseni
    YOK — "yalnız son esaslı ibareye bak" çözümü bu üçünü sessizce cevap sayardı.
    """
    assert exact_reject(_HASAT_CEKINME[kalem], "data") is True


@pytest.mark.parametrize("kimlik", sorted(_CIPA))
def test_exact_reject_resmi_cipa_gozle_okunan_kalemi_dogru_sinifla(kimlik):
    """Resmî B10 çıpası (`h1_tgta_v1_bi_k10`, n=80) — #60'ta gözle okunan üç kalem.

    `id=7` ve `id=20` kaynak-yokluğu hükmüyle AÇILIP sonra açıklama yapıyor (çekinme);
    `id=19` ise elenen kaynak gerekçesiyle açılıp tam atıflı cevap veriyor. Programatik
    sonda bu üçünde İKİ YÖNDE de yanıldı (#60) — bu yüzden kilitleniyorlar.
    """
    beklenen, cevap = _CIPA[kimlik]
    assert exact_reject(cevap, "harness") is beklenen


@pytest.mark.xfail(strict=True, reason=(
    "🔴 AÇIK BORÇ (ADR-0061, 2026-09-06). Ö2'nin AYNA vakası: model açılışta reddedip "
    "GÖVDEDE kendi reddini yalanlıyor ve tam cevabı veriyor. Onarılmış kural örtük açılış "
    "reddini BAĞLAYICI sayıyor, bu yüzden burada çekinme diyor. ÖLÇÜLDÜ ve kapatılmadı: "
    "çıpanın 80 kaleminin GÖZLE OKUNMASINDA bu şekle uyan tek kalem `id=32`. Rule of Three "
    "— tek örnekte kural kurulmaz; genişletmek ters yönde yanlış-pozitif üretir (ADR-0050 "
    "ruhu: sonucu gördükten sonra alet keyfî kurcalanmaz). Bu test kusuru KİLİTLEMEZ, "
    "SINIRI çizer: kural düzelirse strict=True ile PATLAR ve damga kaldırılmak zorunda kalır. "
    "Kaynak: outputs/eval/sprint2-olcum/olcum-bi/B10_GOZLE_OKUMA_80.md"))
def test_exact_reject_acilis_reddini_YALANLAYAN_govde_kacar():
    """Sınır vakası — kural bugün bunu 'çekindi' sayıyor, oysa dolu cevaptır."""
    cevap = "Verilen kaynaklarda bu konuyu düzenleyen madde bulunmuyor. İlgili kaynak, duruşmaya katılmama durumunu düzenleyen HUKUK MUHAKEMELERİ KANUNU MADDE 147'dir. Ancak bu madde, tarafların duruşmaya gelmemesi durumunda mahkemenin devam etmesi ve itiraz edemeyecekleri hususunu belirtmektedir. \n\nKAYNAK 2, duruşmaya katılmama durumunda tarafların mahkemede hazır bulunmadıkları takdirde duruşmaya yokluklarında devam edileceği ve yapılan işlemlere itiraz edemeyecekleri hususunu açıkça belirtmektedir. Bu nedenle, mazeret bildirmezseniz ve duruşmaya katılmazsanız, mahkeme duruşmaya devam edecektir ve yapılan işlemlere itiraz edemeyeceksiniz."
    assert exact_reject(cevap, "harness") is False
