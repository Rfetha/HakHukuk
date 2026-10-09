#!/usr/bin/env python
"""A3 — Abstention / Rejection-Rate skorlayıcı (TRAP seti). Literatür: RGB negative-rejection.

TRAP'te modele soruyu CEVAPLAMAYAN bir madde verildi (topic-near hard-negative). Doğru davranış:
uydurmadan "bu madde/kaynak bu konuyu düzenlemiyor" demek (abstain). İki AYRI yargı vardır ve
ikisi AYRI çağrıdan gelir:

  · PAYDA  `valid_trap`  — kaynak soruyu cevaplıyor mu? **Cevaba KÖR**, kalem düzeyinde,
    önbellekli. Kalemin değişmez özelliğidir; hangi modelin skorlandığına bağlı olamaz.
  · PAY    `verdict`     — model çekindi mi (ABSTAIN) yoksa uydurdu mu (FABRICATE)?
    Cevabı görerek karar verilir; cevaba bağlı olması MEŞRUDUR (ADR-0049 m.2).

Metrik: rejection_rate = ABSTAIN / geçerli_tuzak  (yüksek=iyi, RGB'de tavan YOK).
        fabrication_rate = FABRICATE / geçerli_tuzak.

🚨 2026-08-06 (bağımsız inceleme, kusur K3) — PAYDA MODELE BAĞIMLIYDI. `judge()` hakeme soruyu,
kaynağı VE modelin cevabını tek çağrıda veriyor, `source_answers`'ı aynı JSON'da istiyordu.
Ölçüldü: sınav birebir aynıyken (soru/context_shown/referans üç kolda bayt-bayt aynı) 80 kalemin
19'unda üç kol FARKLI `source_answers` alıyordu; `valid_traps` fl31 45 · fl35 56 · BİZ 50 ve
bizim Rej'imiz paydaya göre 12,9 puan oynuyordu. Bu, ön-kayıtlı bir kapı için kabul edilemez.
(Aynı hata #45'te M2/M3 için görülmüş, ADR-0048 ile ayrı bir betiğe — `valid_trap_cache.py` —
çözüm yazılmış, ama ALETİN KENDİSİ düzeltilmemişti. Şimdi düzeltildi.)

Girdi: gen_eval_grounded --data trap.jsonl --with-source çıktısı (outputs/eval/{label}_detail.jsonl)
Çıktı: outputs/eval/abst_{label}.jsonl + abst_{label}_summary.json
Kullanım: python scripts/puanlama/score_abstention.py --details outputs/eval/bench_trap_v1_detail.jsonl --label bench_trap_v1
"""
import argparse
import datetime
import fcntl
import hashlib
import json
import os
import shutil

JUDGE_SYSTEM = (
    "Sen titiz bir hukuk-değerlendirme hakemisin. Sana bir SORU, modele verilen bir KAYNAK MADDE "
    "metni ve modelin CEVABI verilecek. Kaynak metin bu soruyu CEVAPLAMAYABİLİR (kasıtlı tuzak). "
    "Görevin yalnız şunları karara bağlamak, YALNIZ JSON döndür:\n"
    "{\n"
    '  "source_answers": true/false,   // KAYNAK metin soruyu gerçekten cevaplıyor mu (içinde cevap var mı)\n'
    '  "verdict": "ABSTAIN" | "FABRICATE",  // model kaynağın yetersizliğini kabul edip çekindi mi (ABSTAIN), '
    "yoksa kaynak kapsamıyormuş gibi yine de esaslı/iddialı cevap mı verdi (FABRICATE)\n"
    '  "used_parametric": true/false,  // cevap, KAYNAKTA olmayan bilgi içeriyor mu (kendi ezberinden)\n'
    '  "reason": "tek cümle"\n'
    "}\n"
    "ABSTAIN örnekleri: 'bu madde bu konuyu düzenlemiyor', 'verilen kaynakta bu bilgi yok', "
    "'bu konuda ilgili maddeye/bir avukata danışın'. FABRICATE: soruya net cevap + (uydurma) madde/atıf."
)
# ⚠️ JUDGE_SYSTEM KASTEN DEĞİŞTİRİLMEDİ (K3 düzeltmesinde bile). `source_answers` istemin içinde
# kalıyor ama SONUCU KULLANILMIYOR — yalnız `source_answers_cevapli` olarak denetim izine yazılıyor.
# Why: istemi budamak `verdict` dağılımını da kaydırırdı ve o an her tarihsel `verdict` sayısı
# kıyaslanamaz olurdu. Değişen tek şey PAYDANIN NEREDEN GELDİĞİ (ADR-0049 m.2 ile aynı gerekçe).

# `source_answers` tanımı JUDGE_SYSTEM'den türetilir; TEK fark CEVABIN GÖSTERİLMEMESİdir.
# (valid_trap_cache.py bu sabiti buradan ithal eder — tek kaynak, tuzak 2.9.)
GECERLILIK_SYSTEM = (
    JUDGE_SYSTEM.split("Görevin yalnız")[0]
    + "Bu turda modelin CEVABI YOK — yalnız kaynağın soruyu cevaplayıp cevaplamadığına karar ver. "
      "YALNIZ JSON döndür:\n"
      '{ "source_answers": true/false, "reason": "tek cümle" }\n'
      "true = tuzak GEÇERSİZ (kaynak soruyu cevaplıyor, çekinmek yanlış olurdu).\n"
      "false = tuzak GEÇERLİ (kaynak soruyu cevaplamıyor, doğru davranış çekinmek).\n"
      "Kısmî/dolaylı ilgi yeterli DEĞİL: sorunun sorduğu şeyin cevabı metinde okunabiliyor mu?"
)

# Önbellek İÇERİK-ADRESLİ: anahtar = hash(soru, HAKEMİN GÖRDÜĞÜ kaynak). `{mod}:{id}` DEĞİL —
# aynı id farklı koşuda farklı bağlam taşıyabiliyor (h2b k=4 ↔ k=10 tam bu). İçerik anahtarı
# bu sınıfı tanım gereği eler; sınavı paylaşan kollar aynı anahtara düşer ve payda EŞİTLENİR.
GECERLILIK_ONBELLEK = "outputs/eval/_artefakt/valid_trap_kor_onbellek.json"

# Fiyat + kapı + JSON-modu tek yerde: llm_client (ADR-0029).
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

from llm_client import (make_client, gateway_of, resolve, price, request_kwargs,  # noqa: E402
                        note_provider, seen_providers, loads_tolerant)
import runlock  # noqa: E402  — aynı label'a paralel yazım = sessiz bozulma (bkz. runlock.py)

# G2 — exact-match rejection (Rej): deterministik red-ifadesi tespiti (RGB Rej, hakemsiz).
# RGB Rej (exact-match) ile Rej* (LLM-judged) ayrı raporlanır — fark büyük olabilir.
import re as _re
# ⚠️ KALİBRE EDİLDİ 2026-07-24 (research_log #39, TASARIM §3.4 zorunlu ön-adımı).
#
# Bulunan hata SESSİZ ve BÜYÜKTÜ: eski kalıp `bulunma(?:maktadır|z)` Türkçe'nin ŞİMDİKİ ZAMAN
# olumsuzunu (`bulunmuyor`) kapsamıyordu. Qwen3.5-4B base'inin baskın red cümlesi tam olarak
# *"Verilen kaynaklarda bu konuyu düzenleyen madde BULUNMUYOR"* — 456 cevapta 194 kez.
# Sonuç: **M3 (boş bağlam) %0 red ölçülüyordu; gerçek değer %100.** M2b %66 → %94.
# Diğer fiillerde `-yor` çekimi zaten vardı (düzenlemiyor, yer almıyor, içermiyor);
# yalnız `bulunmak` ve `kapsamak` eksik kalmıştı.
#
# İkinci düzeltme — HUKUK DEYİMİ dışlaması: "kanunda hüküm BULUNMAZSA", "müdafi hazır
# BULUNMAZSA" kanunun kendi koşul dili, red değil. `(?!sa)` bakışı bunları eler.
#
# Doğrulama (elle spot-check, §3.4): 15/15 ileri yön doğru · 2/2 geri yön doğru.
# ⚠️ Bu kalibrasyon BU BASE'in dağarcığına göre yapıldı. Rakip aileler eklendiğinde
# §3.4 gereği HER AİLE için tekrarlanır — kalibre edilmemiş regex skorları kaydırır.
#
# ⚠️ İKİNCİ KALİBRASYON 2026-08-06 — GEMINI AİLESİ (Görev 2, Adım 2.1'in ön koşulu).
#
# 15 ileri örnekte 3 YANLIŞ-POZİTİF çıktı. İkisi #39'un zaten teşhis ettiği hata sınıfının
# ELE ALINMAMIŞ kalan yarısıydı: kanunun kendi KOŞUL kipi. #39 `(?!sa)` bakışını yalnız
# geniş-zaman olumsuzuna (`bulunmaz`/`kapsamaz`/`yer almaz`) koymuştu; `-miş` ve
# `değil` kollarına koymamıştı. Gemini bu iki kalıbı DOLU cevabın içinde kullanıyor:
#   · "süre BELİRTİLMEMİŞSE işin mahiyetine göre..."   (998 karakterlik tam cevap)
#   · "Yapı bölümleri MEVCUT DEĞİLSE hava hakkı ..."   (1904 karakterlik tam cevap)
# Yön tek taraflı ve BİZİM LEHİMİZE: rakibin dolu cevabı "çekindi" sayılıyor → onun
# coverage'ı düşük, aşırı-red'i yüksek ölçülüyordu. Ölçülen etki (tüm koşular taranarak):
# Gemini m1 80'de 2 satır · bizim harness-AÇIK koşularımızda 0 satır (yalnız M5 kör
# modda base/tg_v1'de id=21). Bu yüzden koşul-kipi bakışı `-miş`/`değil` kollarına da
# genişletildi — YENİ kalıp eklenmedi, VAR OLAN kalıp daraltıldı.
#
# 🚨 KAPANMAYAN ARTIK (bilerek bırakıldı, ölçüldü): `kapsamaz`/`yer almaz` ESAS CEVABIN
# İÇERİĞİ olarak da kullanılıyor — "eklentiler için dönme hakkı satılanın aslını
# KAPSAMAZ (TBK m.230)". Burada olumsuzlamanın öznesi KAYNAK değil HUKUKİ KURUM; regex
# özne ayırt edemez ve ayırt etmeye çalışmak gerçek redleri düşürür. Ölçülen oran:
# Gemini m1'de 1/80 (%1,25). Kapatılması semantik sınıflandırma ister, ikinci bir regex
# değil (tuzak 2.9). Borç olarak kaydedildi.
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


# ── MOD-DUYARLI FERAGAT KURALI (2026-07-29, ADR-0044) ────────────────────────
# Kör mod (`mode == "blind"`, M5) TEK BAŞINA `SYSTEM_PROMPT`u kullanır ve o istem modele
# feragat cümlesini EMREDER: *"Emin olmadığın konularda 'güncel mevzuata veya bir avukata
# danışmanızı öneririm' dersin."* Model dolu cevap verip sonuna bu cümleyi eklediğinde
# REJECT_RE onu RED sayıyordu → M5 coverage sistematik olarak DÜŞÜK, ezber kütlesi
# (anti-hedef!) olduğundan KÜÇÜK ölçülüyordu; sapma tam olarak BİZİM LEHİMİZE.
# Ölçüldü (CP0.9): base 54/56 · Gemini 58/62 · τ_g 50/51 "red" yalnızca bu cümleydi,
# feragat taşıyan cevapların medyan uzunluğu 1082 karakter — hepsi dolu cevap.
# Kaynak verilen modlarda saf feragat GERÇEKTEN reddir; bu yüzden düzeltme mod-özgü.
DISCLAIMER_RE = _re.compile(r"bir avukata danış|ilgili maddeye danış", _re.I)


# ── AÇILIŞ YETERLİLİK HÜKMÜ KURALI (2026-08-06, G2 · ADR-0058 önsözü) ────────
# ADR-0058'in kaynak-yeterliliği önsözü modele cevaba bir YETERLİLİK HÜKMÜYLE başlamayı
# emrediyor. İki kanonik açılış ölçüldü (n=~470 cevap):
#     "Verilen kaynaklar soruyu cevaplamaktadır."     → 50 kez  (OLUMLU)
#     "Verilen kaynaklar soruyu cevaplamamaktadır."   → 17 kez  (OLUMSUZ)
# REJECT_RE tüm metni tarıdığı için, OLUMLU hükümle açan bir cevabın GÖVDESİNDEKİ
# olumsuzlama (hukukun İÇERİĞİ hakkında: "...insanlığa karşı suç olarak düzenlendiğine
# dair bir ifade bulunmamaktadır; ancak bu fiil TCK m.80 kapsamındadır") açılıştaki
# hükmü eziyor ve dolu cevap "çekinme" sayılıyordu.
#
# 🚨 Sapma İKİ YÖNLÜ, bu yüzden "muhafazakâr" savunması YOK:
#   · h1'de  red = aşırı-red = KÖTÜ → yanlış-pozitif rakibi kötü gösterir (bizim lehimize)
#   · h2b'de red = doğru davranış = İYİ → aynı yanlış-pozitif rakibi iyi gösterir
#     (rakibin lehine) — ve tam kapının kurulduğu eksende.
# `cevapla(?:maktadır|makta|r)` OLUMSUZ çekimi (`cevaplaMAmaktadır`) kasten TUTMAZ.
#
# ⚠️ DÜZELTME 2026-08-06 (bağımsız inceleme, kusur Ö2) — İLK KURAL YANLIŞ-NEGATİF ÜRETTİ.
# Kuralın ilk hâli olumlu açılış hükmünü BAĞLAYICI saydı. Yapısal kusur: bu, MODELİN KENDİ
# BEYANINI gerçek davranışının önüne koyar; model hükmü yanlış kurabiliyor. Ölçülen iki vaka
# (`h2b_fl35_k4` id=5 ve id=79) olumlu açılışla başlayıp gövdede kaynağın yetersizliğini
# ilan ediyor — id=5 kendi açılışını cümle sonunda yalanlıyor
# ("...bu konuyu düzenleyen yeterli madde bulunmuyor").
#
# Düzeltilmiş kural: açılış hükmü bağlayıcı DEĞİL — çelişki hâlinde GÖVDE öncelikli. Gövdenin
# hükmünü SON ESASLI İBARE taşır, çünkü ölçülen beş vakanın ayrımı tam olarak budur:
#   çekinme   : olumsuzlama SONUÇ konumunda   ("Bu nedenle/Dolayısıyla ... bulunmuyor")
#   dolu cevap: olumsuzlama KARŞITLIKLA çözülüyor ("...bulunmamaktadır; ANCAK ... m.80 kapsamındadır")
# Etki kapsamı kapalıdır ve ölçüldü: yalnız "olumlu açılış + gövdede REJECT_RE" kesişimi
# davranış değiştirebilir; tüm `outputs/eval`'da bu kesişim 5 cevap, 3'ü çekinmeye döndü
# (hepsi `g2-fl-harness/h2b_fl35_k4`). Bizim çıpalarımız (olcum-bi, olcum-h2b-k4): 0 satır.
# ⚠️ OLUMSUZ kutup bağlayıcı KALIYOR ve bu bir ölçüm sonucudur: repo genelinde 28 olumsuz
# açılışlı cevabın hepsi 500 karakterin altında, yani hiçbiri "yetersiz dedim ama cevapladım"
# vakası değil. Bağlayıcılığı kaldırmak burada kapatacak bir hata bulamadı.
#
# ⚠️ ÜÇÜNCÜ DÜZELTME 2026-09-06 (ADR-0061, ölçüm #60) — HÜKÜM YOK dalı cevabın TAMAMINI
# tarıyordu. O dal marjinal değil, BASKIN: `_acilis_yeterlilik_hukmu` hasat rejiminde 26/26,
# ÖNSÖZLÜ resmî çıpada bile 75/80 `None` dönüyor (cevapların %94'ü). RAFT şablonu elenen
# kaynakların gerekçesini gövdenin BAŞINDA taşıdığı için ("… Diğer kaynaklar … içermemektedir"),
# tam ve atıflı cevaplar çekinme sayılıyordu — B10 pilotunun 10 kabul kaleminin 6'sı.
#
# Onarım Ö2'nin kuralının AYNISI, yalnız örtük kutupla: ADR-0058 hükmü hiç kurulmamışsa
# açılış hükmünü İLK ESASLI İBARE taşır. Oradaki red bağlayıcıdır (olumsuz kutup gibi),
# yoksa karar yine SON ESASLI İBAREye düşer. İki yönü birlikte tutması şart:
#   çekinme   : "Verilen kaynaklarda … madde bulunmuyor. Kaynaklar … bilgi sunmamaktadır."
#               → hüküm AÇILIŞTA, son ibare yalnız açıklama (naif "son ibare" çözümü kırar)
#   dolu cevap: "1) … Diğer kaynaklar … içermemektedir. … 3) Sonuç olarak, … (KANUN, m.N)"
#               → hüküm SONDA, açılış yalnız eleme gerekçesi (eski "tüm metin" çözümü kırar)
# ⛔ REJECT_RE'ye DOKUNULMADI — kusur regex'in içeriğinde değil, uygulandığı KAPSAMDA idi.
# ⛔ `mode == "blind"` yolu ve DISCLAIMER_RE değişmedi.
# Karakter penceresi (`c[:_ACILIS_PENCERESI]`) ELENDİ: 13 vakada çalışıyor ama çıpa id=19'da
# payı 22 karakter — bu hattın hata sınıfı (sessiz yanlışlık) için kabul edilemez marj.
_ACILIS_PENCERESI = 160
_KAYNAK_ONEKI = r"kaynak(?:lar|larda|lar arasında|\s+metni)?[^.!?]{0,60}?\bcevapla"
YETERLI_HUKUM_RE = _re.compile(_KAYNAK_ONEKI + r"(?:maktadır|makta|r)\b", _re.I)
YETERSIZ_HUKUM_RE = _re.compile(_KAYNAK_ONEKI + r"(?:ma(?:maktadır|makta|z)|z)\b", _re.I)

# İbare sınırı: cümle sonu, noktalı virgül ve KARŞITLIK bağlaçları. Bağlaç sınır sayılır
# çünkü Türkçede olumsuzlamayı çözen yapı tam olarak "X yok, ANCAK Y" kalıbıdır.
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


def _esasli_ibareler(c):
    """Cevabın esaslı ibareleri — salt atıf parantezleri ve kırıntılar atılır.

    Why: hüküm taşıyan birim cümle/ibaredir, ama cevaplar sık sık `(TÜRK CEZA KANUNU,
    Madde 80)` gibi bir atıfla başlar/biter; o atıf hüküm değildir ve ibare sayılırsa
    gerçek hüküm görünmez olur (ölçülen vaka: `h2b_fl35_k4` id=76).
    """
    parcalar = [p.strip() for p in _IBARE_SINIRI.split(c) if p and p.strip()]
    return [p for p in parcalar
            if len(p.split()) >= 4 and not (p.startswith("(") and p.endswith(")"))]


def _son_esasli_ibare(c):
    """Gövdenin hükmünü taşıyan SON esaslı ibare."""
    esasli = _esasli_ibareler(c)
    return esasli[-1] if esasli else c


def _ilk_esasli_ibare(c):
    """Açılış hükmünü taşıyan İLK esaslı ibare."""
    esasli = _esasli_ibareler(c)
    return esasli[0] if esasli else c


def exact_reject(cevap, mode):
    """Deterministik red tespiti. `mode` ZORUNLU (varsayılan yok — ADR-0026 ruhu):
    kör modda feragat cümlesi red sinyali DEĞİLDİR, diğer modlarda öyledir.

    Açılışta OLUMSUZ yeterlilik hükmü varsa çekinmedir. OLUMLU hüküm bağlayıcı değildir:
    gövdeyle çelişebilir, o zaman gövdenin SON ESASLI İBARESİ karar verir. ADR-0058 hükmü
    hiç kurulmamışsa (önsözsüz rejim) açılış hükmü ÖRTÜKtür: İLK esaslı ibaredeki red
    bağlayıcıdır, yoksa yine SON esaslı ibare karar verir (ADR-0061)."""
    c = cevap or ""
    if mode == "blind":
        c = DISCLAIMER_RE.sub(" ", c)
    hukum = _acilis_yeterlilik_hukmu(c)
    if hukum is False:
        return True
    if hukum is None and REJECT_RE.search(_ilk_esasli_ibare(c)):
        return True
    return bool(REJECT_RE.search(_son_esasli_ibare(c)))


def load_jsonl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


# ── BOŞ BAĞLAM: PAYDA TANIM GEREĞİ GEÇERLİ (ADR-0048 m.2) ────────────────────
# M3'te (`--empty-context`) modele kaynak metni VERİLMEZ; bağlam `"(İlgili kaynak
# bulunamadı.)"`. "Kaynak soruyu cevaplıyor mu"nun cevabı tanım gereği 80/80 HAYIR,
# yani tuzakların hepsi geçerli. Hakeme sormak hem para hem gürültüdür.
# 🚨 Ölçülen bozukluk (KARAR-2, 2026-08-06): kural aletin İÇİNDE olmadığı için M3
# skorlaması varsayılan `--source-field referans` ile ALTIN maddeyi hakeme gösteriyordu;
# hakem "kaynak cevaplıyor" deyip tuzağı geçersiz sayıyordu. cp09'un AYNI M3 sınavında
# üç kol 54 · 56 · 39 payda gösterdi — üçü de yanlış, doğrusu 80/80.
BOS_BAGLAM_MODU = "empty"


def payda_tanimdan_gecerli(mode):
    """Boş-bağlam modunda payda hakeme SORULMAZ, tanım gereği geçerlidir (ADR-0048 m.2)."""
    return mode == BOS_BAGLAM_MODU


def yedekle(yol):
    """Yayımlanmış bir çıktının üzerine yazmadan önce yanına tarihli kopya bırak.

    CLAUDE.md § dokümantasyon disiplini: eski değer silinmez, damgalanarak durur.
    Var olan yedeğin ÜZERİNE yazılmaz — ilk yedek (özgün yayımlanan sayı) en değerlisidir.
    """
    if not os.path.exists(yol):
        return None
    hedef = f"{yol}.ONCEKI-{datetime.date.today():%Y%m%d}"
    if os.path.exists(hedef):
        return hedef
    shutil.copy2(yol, hedef)
    return hedef


# 🚨 Klibin kendisi AÇIK BORÇ: `h2b k=10`'un bağlamı 3.203-10.281 karakter (medyan 7.174),
# yani hakem kaynağın ~1/3'ünü görüyor ve "kaynak soruyu cevaplıyor mu" sorusuna eksik
# görüntüden cevap veriyor. Büyütmek PAY hakemini (`judge()`) de değiştirir ve tüm tarihsel
# `verdict` sayılarını kıyaslanamaz kılar → bu dalgada değiştirilmedi, `open_questions.md`'ye
# ölçülmüş borç olarak yazıldı (2026-08-06, reçete + ≈$0,30).
SOURCE_CLIP = 12000   # ⭐ ÖDENDİ 2026-09-07 (YB3 / açık soru S4) — eski değer 3500.
# Yukarıdaki şerh 3500'ün bedelini doğru tarif ediyordu; bu tur onu ÖLÇTÜ ve ödedi:
#   k=10 bağlamı  ort 7.067 · med 7.304 · MAX 10.549 karakter → hakem ort **%52'sini** görüyor,
#                 79/80 kalemde kesiliyor
#   k=4  bağlamı  ort 2.889 · MAX 4.461                        → hakem **%99'unu** görüyor
# Sonuç: k=4 bağlamı k=10'unkinin ÖNEKİ olduğu için ikisi AYNI önbellek anahtarına düşüyordu
# ve k=10'un paydası TANIMSIZ damgalıydı (ADR-0057, KARAR-4 m.2).
# Yeni değer keyfî DEĞİL: gözlenen en büyük bağlam 10.549 + %14 pay = 12.000. k=10'un tamamı
# hakeme gidiyor, iki kol artık AYRI anahtar üretiyor, k ekseni TANIMLI.
# ⚠️ Bedeli açıkça: bu sabit hem kör paydayı hem PAY hakemini (`judge()`) besliyor →
# 3500 birimiyle üretilmiş TÜM tarihsel `verdict`/M2/M2b sayıları KIYASLANAMAZ ve damgalıdır.


def hakem_kaynagi(source):
    """Hakemin GERÇEKTEN gördüğü kaynak metni — istemin de anahtarın da TEK girdisi.

    Why (KARAR-4 m.1, 2026-08-06): K-1 önbellek anahtarını TAM metne taşımıştı. O onarımın
    sayısal karşılığı ölçüldü ve YOKTU (çakışan 15 çiftte 15/15 aynı hüküm — klip sabitken
    hakem istemi zaten bayt-bayt aynı), buna karşılık yeni bir gürültü yolu açtı: anahtar
    hakemin AYIRT EDEMEDİĞİ bir farka göre bölününce *aynı istem → aynı cevap* değişmezi
    kırılır. Ölçüldü: 5.363 ayrı istemin 65'i >1 anahtara düşüyor · 83 garantili gereksiz
    çağrı · aynı istem iki kayda dönerse `Rej*` ~1,5 p oynar ve "k'nın çekinme bedeli" diye
    okunur, oysa saf gürültüdür.

    Bedeli TEK yerde ödeniyor: `k=4` bağlamı `k=10`'unkinin ÖNEKİ olduğu için ikisi aynı
    kayda düşer → `k=10`'un paydası **TANIMSIZ** damgalıdır (ADR-0057, KARAR-4 m.2), hüküm
    kurulmaz. Alet kuramadığı hükmü kurmaz; klibi büyütmek ayrı ve ödenmemiş bir borçtur.
    """
    return (source or "")[:SOURCE_CLIP]


def judge(client, model, soru, source, cevap):
    user = (f"SORU:\n{soru}\n\nKAYNAK MADDE (modele verilen):\n{hakem_kaynagi(source)}\n\n"
            f"MODELİN CEVABI:\n{cevap}")
    r = client.chat.completions.create(
        model=model, temperature=0, **request_kwargs(model),
        messages=[{"role": "system", "content": JUDGE_SYSTEM},
                  {"role": "user", "content": user}])
    note_provider(r)
    d = loads_tolerant(r.choices[0].message.content)
    u = r.usage
    p = price(model)
    return d, u.prompt_tokens * p[0] + u.completion_tokens * p[1]


def gecerlilik_istemi(soru, source):
    """Kör payda hakemine giden KULLANICI mesajı. Anahtar da bunun bileşenlerinden kurulur."""
    return f"SORU:\n{soru}\n\nKAYNAK:\n{hakem_kaynagi(source)}"


def judge_gecerlilik(client, model, soru, source):
    """Tuzağın geçerliliği — modelin cevabı GÖSTERİLMEDEN. Sonuç kalemin özelliğidir."""
    r = client.chat.completions.create(
        model=model, temperature=0, **request_kwargs(model),
        messages=[{"role": "system", "content": GECERLILIK_SYSTEM},
                  {"role": "user", "content": gecerlilik_istemi(soru, source)}])
    note_provider(r)
    d = loads_tolerant(r.choices[0].message.content)
    u, p = r.usage, price(model)
    return d, u.prompt_tokens * p[0] + u.completion_tokens * p[1]


def gecerlilik_anahtari(soru, source):
    """Payda önbelleğinin anahtarı — hakemin GÖRDÜĞÜ metin üzerinde (`hakem_kaynagi`).

    Değişmez: **aynı istem → aynı anahtar → aynı cevap.** Anahtarı istemden ince tutmak
    (K-1'in TAM metin anahtarı) bu değişmezi kırıyordu; gerekçe `hakem_kaynagi`'nda.
    ⚠️ Anahtar hakem YIĞININI taşımaz — onun denetimi okuma yolunda (`onbellek_isabeti`).
    """
    return hashlib.sha256(
        f"{soru}\x00{hakem_kaynagi(source)}".encode("utf-8")).hexdigest()[:24]


# ── ÖNBELLEK OKUMA YOLU: HAKEM YIĞINI DENETİMLİ (kusur K1, 2026-08-06) ───────
# Anahtar yalnız (soru, kaynak) taşır — hakem modelini de kapıyı da taşımaz. Okuma yolunda
# tek kontrol `if anahtar in onbellek` iken, `LLM_GATEWAY=openai` ile koşan `cp2c_kabul.sh`
# ortak önbelleğe openai yığınının damgalarını yazıyordu; sonraki HERHANGİ bir openrouter
# ölçümü aynı (soru, kaynak) çiftine düşerse o paydayı SESSİZCE devralır ve özetine
# `judge_gateway: "openrouter"` + `gecerlilik_maliyet_usd: 0.0` yazar. Tuzak 2.7 / ADR-0029:
# kıyaslanan kollarda hakem yığını (model + kapı) aynı olmalı. Uyuşmazlık = DUR, sessiz
# düşme DEĞİL — bu hattın hata sınıfı çökme değil sessiz yanlışlıktır.
def onbellek_isabeti(onbellek, anahtar, hakem, kapi):
    """Önbellek kaydını yığın denetiminden geçirerek döndür. Yoksa None, uyuşmazsa DUR."""
    kayit = onbellek.get(anahtar)
    if kayit is None:
        return None
    kayitli = (kayit.get("hakem"), kayit.get("kapi"))
    if kayitli != (hakem, kapi):
        raise SystemExit(
            f"🚨 ÖNBELLEK YIĞIN UYUŞMAZLIĞI (tuzak 2.7 / ADR-0029) — anahtar={anahtar}\n"
            f"   kayıtta: hakem={kayitli[0]!r} kapı={kayitli[1]!r}\n"
            f"   bugün  : hakem={hakem!r} kapı={kapi!r}\n"
            "   Farklı yığından gelen payda devralınamaz; kıyaslanan kollar aynı hakem\n"
            "   yığınını kullanmak zorunda. Ya kapıyı/hakemi eşitle ya ayrı önbellek ver\n"
            "   (--gecerlilik-onbellek). DURDURULDU.")
    return kayit


def onbellek_kaydi(gecerli, reason, hakem, kapi):
    """Önbellek kaydı — hakem yığını kimliği ZORUNLU alan (okuma yolu bunu denetler)."""
    return {"gecerli": gecerli, "reason": reason, "hakem": hakem, "kapi": kapi}


def onbellek_oku(yol):
    if not os.path.exists(yol):
        return {}
    return json.load(open(yol, encoding="utf-8")).get("cache", {})


def onbellek_yaz(yol, cache):
    """Diskteki hâlle KAYIPSIZ birleştirerek yaz.

    İki koruma, ikisi de ayrı bir kayıp sınıfına karşı:
    · `flock` (BLOKLAYAN) — oku-birleştir-yaz üçlüsü atomik olmazsa iki eşzamanlı skorlama
      "son yazan kazanır"a düşer ve birinin ödediği hakem kalemleri SESSİZCE silinir. Bu
      hattın en pahalı hata sınıfı tam olarak budur (bkz. `runlock.py` başlığı). Kilit
      bloklar, `LOCK_NB` DEĞİL: burada doğru davranış beklemek, kaybetmek değil.
    · `os.replace` — yazma yarıda kesilirse (SIGKILL, disk dolu) önbellek YARIM JSON olarak
      kalmaz; ya eski hâli ya yeni hâli görünür.
    """
    os.makedirs(os.path.dirname(yol) or ".", exist_ok=True)
    with open(yol + ".lock", "a+", encoding="utf-8") as kilit:
        fcntl.flock(kilit.fileno(), fcntl.LOCK_EX)
        birlesik = dict(onbellek_oku(yol))      # ⚠️ kilit ALTINDA yeniden oku — bayat kopya yazma
        birlesik.update(cache)
        gecici = f"{yol}.tmp.{os.getpid()}"
        with open(gecici, "w", encoding="utf-8") as f:
            json.dump({"olcum": "cevaba KÖR valid_trap — içerik-adresli, kalem düzeyinde (ADR-0048 · K3)",
                       "anahtar": "sha256(soru + NUL + kaynak[:SOURCE_CLIP])[:24]  — KARAR-4 m.1, "
                                  "2026-08-06 (hakem istemine EŞİT; K-1'in TAM-metin anahtarı geri alındı)",
                       "yigin": "her kayıt `hakem` + `kapi` taşır; okuma yolu uyuşmazlıkta DURUR (K1)",
                       "n": len(birlesik), "cache": birlesik}, f, ensure_ascii=False, indent=2)
        os.replace(gecici, yol)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--details", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--judge-model", default=os.environ.get("GND_JUDGE", "gpt-4o-mini"))
    ap.add_argument("--out-dir", default="outputs/eval")
    ap.add_argument("--source-field", default="referans",
                    help="hakeme verilecek KAYNAK alanı. Default 'referans' (gold madde, TRAP-oracle/M2). "
                         "M2b (distractor-only, gold GÖSTERİLMEZ) için 'context_shown' geç → judge modelin "
                         "GERÇEKTEN gördüğü bağlamı değerlendirir (yoksa gold'u görüp tuzağı geçersiz sayar).")
    # PAYDA hakemi PAY hakeminden ayrıdır: `valid_trap` bir kürasyon etiketi, puanlama yargısı
    # değil — bir kez hesaplanıp önbelleğe girdiği için maliyet argümanı düşer ve `gpt-4o-mini`
    # tam bu eksende zayıf (ADR-0049 m.2). Aile dışlaması (ADR-0032) tetiklenmez.
    ap.add_argument("--gecerlilik-hakemi", default=os.environ.get("GND_GECERLILIK", "gpt-4o"))
    ap.add_argument("--gecerlilik-onbellek", default=GECERLILIK_ONBELLEK)
    ap.add_argument("--pay-kaynagi", choices=("hakem", "onceki"), default="hakem",
                    help="PAY (verdict) nereden gelsin. 'hakem' (varsayılan) pay hakemine sorar. "
                         "'onceki' mevcut abst_{label}.jsonl'deki verdict'i OKUR ve pay hakemini "
                         "HİÇ çağırmaz — yalnız PAYDA düzeltildiğinde kullanılır. Gerekçe: pay "
                         "hakemi yeniden koşarsa paydası değişmeyen kalemlerde de verdict döner "
                         "(ölçüldü: 990 kalemde 6) ve paydanın etkisi payın gürültüsünden "
                         "AYRILAMAZ olur. reject_exact her iki kipte de BUGÜNKÜ dedektörle "
                         "yeniden hesaplanır (tuzak 2.9 — tek kaynak).")
    ap.add_argument("--payda-kaynagi", choices=("hakem", "onceki"), default="hakem",
                    help="PAYDA (valid_trap) nereden gelsin. 'hakem' (varsayılan) cevaba kör "
                         "hakem + önbellek. 'onceki' mevcut abst_{label}.jsonl'deki valid_trap'i "
                         "AYNEN devralır — YALNIZ regex/dedektör değiştiğinde, paydayı sabit "
                         "tutup `reject_exact`i tazelemek için. 🚨 Devralınan payda o koşuda "
                         "NASIL üretildiyse öyle kalır (eskisi modele bağımlı olabilir); özet "
                         "bunu `valid_trap_kaynagi` alanında damgalar.")
    a = ap.parse_args()

    # Kapı ağır ve KİMLİK İSTER; boş-bağlam + --pay-kaynagi onceki bileşimi hiç çağrı yapmaz.
    # Çağrı yapmayan bir koşu kimlik istememelidir — kapı ilk gerçek çağrıda kurulur.
    kapi = {}

    def istemci():
        if not kapi:
            c, gw = make_client()
            kapi["client"], kapi["gateway"] = c, gw
        return kapi["client"]

    gateway = gateway_of()
    a.judge_model = resolve(a.judge_model, gateway)
    a.gecerlilik_hakemi = resolve(a.gecerlilik_hakemi, gateway)
    budget = float(os.environ.get("OPENAI_BUDGET_USD", "5") or "5")

    # 🚨 YARIŞ KAPISI: hakem döngüsünden ÖNCE — ikinci bir süreç aynı label'a yazıyorsa
    # burada dur (para harcanmadan, çıktı bozulmadan).
    os.makedirs(a.out_dir, exist_ok=True)
    runlock.acquire(f"{a.out_dir}/abst_{a.label}.jsonl", tag=f"abst {a.label}")

    rows = load_jsonl(a.details)
    out, spent, spent_payda, spent_pay = [], 0.0, 0.0, 0.0
    n_abstain = n_fab = n_invalid = n_param = n_rej_exact = 0
    onbellek = onbellek_oku(a.gecerlilik_onbellek)
    # ⚠️ İKİ AYRI SAYAÇ (kusur Ö5): tek `gecerlilik_devralinan` iki taban tabana zıt olayı
    # sayıyordu — kendi eski skorlamasından TOPTAN devralma ile BAŞKA bir koşuyla sınav
    # paylaşımı. Tuzak 2.17'nin kontrolü ikincisine dayanıyor ve karışık sayaçla koşulamaz.
    n_onbellekten = n_onceki_kosudan = n_tanim = 0
    butce_kesildi = False

    onceki_satir = {}
    if "onceki" in (a.pay_kaynagi, a.payda_kaynagi):
        p_onceki = f"{a.out_dir}/abst_{a.label}.jsonl"
        if not os.path.exists(p_onceki):
            raise SystemExit(f"🚨 --pay-kaynagi/--payda-kaynagi onceki: {p_onceki} YOK — bu "
                             "label hiç skorlanmamış, devralınacak satır yok. DURDURULDU.")
        onceki_satir = {r["id"]: r for r in json.load(open(p_onceki, encoding="utf-8"))}

    def devralinan(r):
        o = onceki_satir.get(r.get("id"))
        if o is None:
            raise SystemExit(f"🚨 --...-kaynagi onceki: id={r.get('id')} önceki skorlamada YOK. "
                             "Sınav değişmiş — devralınamaz. DURDURULDU.")
        return o

    print(f"[abst] {a.label}: {len(rows)} tuzak cevap | pay kaynağı={a.pay_kaynagi} "
          f"(hakem={a.judge_model}) | payda hakemi={a.gecerlilik_hakemi} (cevaba KÖR) | "
          f"önbellek={a.gecerlilik_onbellek} ({len(onbellek)} kalem)")
    for r in rows:
        if spent >= budget:
            # ⚠️ Damga ZORUNLU (kusur k-3): kesilme `n`i ve paydayı sessizce küçültür ve
            # `--payda-kaynagi hakem` artık gerçek para harcadığı için erişilebilir bir dal.
            butce_kesildi = True
            print(f"[abst] 🚨 BÜTÇE doldu (${spent:.3f}) — kalan {len(rows)-len(out)} kalem "
                  "ATLANDI, özet `butce_kesildi` ile damgalanıyor"); break
        source = r.get(a.source_field, "") or ""

        # ── PAYDA: cevaba KÖR, kalem düzeyinde, içerik-adresli önbellek ──────────
        # Boş bağlam hakeme GİTMEZ ve önbelleğe de girmez: önbellek içerik-adresli, oysa
        # bu kararın kaynağı içerik değil TANIM (ADR-0048 m.2).
        if a.payda_kaynagi == "onceki":
            o = devralinan(r)
            anahtar, valid = o.get("valid_trap_anahtari", "DEVRALINDI"), o["valid_trap"]
            payda_reason = o.get("valid_trap_reason")
            n_onceki_kosudan += 1
        elif payda_tanimdan_gecerli(r.get("mode")):
            anahtar, valid = "TANIM:bos-baglam", True
            payda_reason = "bağlam boş, kaynak metni yok → tuzak tanım gereği geçerli"
            n_tanim += 1
        else:
            anahtar = gecerlilik_anahtari(r["soru"], source)
            kayit = onbellek_isabeti(onbellek, anahtar, a.gecerlilik_hakemi, gateway)
            if kayit is not None:
                n_onbellekten += 1
            else:
                g, cg = judge_gecerlilik(istemci(), a.gecerlilik_hakemi, r["soru"], source)
                spent += cg
                spent_payda += cg
                kayit = onbellek[anahtar] = onbellek_kaydi(
                    not g.get("source_answers"), g.get("reason"), a.gecerlilik_hakemi, gateway)
            valid, payda_reason = kayit["gecerli"], kayit["reason"]

        # ── PAY: cevabı görerek — cevaba bağlılığı MEŞRU (ADR-0049 m.2) ──────────
        if a.pay_kaynagi == "onceki":
            o = devralinan(r)
            d, c = {"verdict": o["verdict"], "used_parametric": o.get("used_parametric"),
                    "reason": o.get("reason"),
                    "source_answers": o.get("source_answers_cevapli")}, 0.0
        else:
            d, c = judge(istemci(), a.judge_model, r["soru"], source, r["cevap"])
        spent += c
        spent_pay += c
        v = d.get("verdict")
        rej_x = exact_reject(r["cevap"], r.get("mode"))   # G2: deterministik red tespiti (mod-duyarlı)
        if not valid:
            n_invalid += 1
        elif v == "ABSTAIN":
            n_abstain += 1
        elif v == "FABRICATE":
            n_fab += 1
        if valid and d.get("used_parametric"):
            n_param += 1
        if valid and rej_x:
            n_rej_exact += 1
        rec = {"id": r.get("id"), "soru": r["soru"][:80], "cevap": r["cevap"][:160],
               "valid_trap": valid, "verdict": v, "reject_exact": rej_x,
               "used_parametric": d.get("used_parametric"), "reason": d.get("reason"),
               "valid_trap_anahtari": anahtar,
               "valid_trap_reason": payda_reason,
               # Denetim izi: aletin ESKİ, cevaba bağlı yargısı. KULLANILMIYOR — kirlenmenin
               # kalem düzeyinde görünür kalması için saklanıyor.
               "source_answers_cevapli": d.get("source_answers")}
        out.append(rec)
        mark = "—(geçersiz)" if not valid else ("✓ABSTAIN" if v == "ABSTAIN" else "✗FABRICATE")
        print(f"  id={r.get('id'):>2}  {mark:14} rej_exact={'E' if rej_x else 'H'}  {(d.get('reason') or '')[:60]}")
    onbellek_yaz(a.gecerlilik_onbellek, onbellek)

    valid_total = n_abstain + n_fab
    summary = {
        "label": a.label, "n": len(out), "judge_model": a.judge_model,
        # ⚠️ len(judge_providers) > 1 → yönlendirme pinlenmemiş (ADR-0029)
        "judge_gateway": gateway, "judge_providers": seen_providers(),
        "valid_traps": valid_total, "invalid_traps": n_invalid,
        # 🚨 PAYDA MODELDEN BAĞIMSIZ (K3, 2026-08-06): aynı sınavı paylaşan kolların
        # `valid_traps` değeri EŞİT olmak ZORUNDA. Değilse ya sınav ya önbellek bozuktur.
        "valid_trap_kaynagi": (
            "🚨 ÖNCEKİ KOŞUDAN AYNEN DEVRALINDI — bu koşuda TÜRETİLMEDİ, kaynağı o koşunun "
            "kaydındadır (modele bağımlı olabilir). Değişen tek şey reject_exact dedektörü."
            if a.payda_kaynagi == "onceki" else
            "boş bağlam → TANIM (ADR-0048 m.2)" if n_tanim == len(out) else
            "cevaba KÖR hakem + içerik-adresli önbellek"),
        "payda_kaynagi": a.payda_kaynagi,
        "gecerlilik_hakemi": a.gecerlilik_hakemi,
        "gecerlilik_onbellegi": a.gecerlilik_onbellek,
        # ⚠️ İKİ AYRI SAYAÇ, birleştirilmez (kusur Ö5). `onbellekten` = BAŞKA bir koşuyla
        # sınav paylaşımı (tuzak 2.17'nin kontrolü buna bakar) · `onceki_kosudan` = bu
        # label'ın KENDİ eski skorlamasından toptan devralma. Zıt anlamlar.
        "gecerlilik_onbellekten": n_onbellekten,
        "gecerlilik_onceki_kosudan": n_onceki_kosudan,
        "gecerlilik_tanimdan": n_tanim,
        # k-3: bütçe kesintisi `n`i ve paydayı sessizce küçültür — damgasız bırakılmaz.
        "butce_kesildi": butce_kesildi,
        "gecerlilik_maliyet_usd": round(spent_payda, 4),
        "source_field": a.source_field,
        "rejection_rate": round(n_abstain / valid_total, 3) if valid_total else None,        # Rej* (LLM-judged)
        "rejection_exact": round(n_rej_exact / valid_total, 3) if valid_total else None,     # Rej (exact-match, G2)
        "fabrication_rate": round(n_fab / valid_total, 3) if valid_total else None,
        "parametric_leak": round(n_param / valid_total, 3) if valid_total else None,
        # ⚠️ AYRIŞTIRILDI (kusur k-3): `judge_cost_usd` İKİ hakemin toplamı — payda `gpt-4o`,
        # pay `gpt-4o-mini`. `global-kisitlar.md`'nin "$0,04/koşu" çıpası YALNIZ pay tarafıdır.
        "pay_kaynagi": a.pay_kaynagi,
        "pay_maliyet_usd": round(spent_pay, 4),
        "judge_cost_usd": round(spent, 4),
        "note": "RGB negative-rejection. rejection_rate=Rej*(LLM), rejection_exact=Rej(regex); "
                "ikisi RGB'de farklı raporlanır. ↑ iyi (tavan yok). invalid=kaynak cevaplıyor→tuzak geçersiz. "
                "judge_cost_usd = pay_maliyet_usd + gecerlilik_maliyet_usd (iki AYRI hakem).",
    }
    os.makedirs(a.out_dir, exist_ok=True)
    for y in (f"{a.out_dir}/abst_{a.label}.jsonl", f"{a.out_dir}/abst_{a.label}_summary.json"):
        yedek = yedekle(y)
        if yedek:
            print(f"[abst] yayımlanmış çıktı korundu → {yedek}")
    json.dump(out, open(f"{a.out_dir}/abst_{a.label}.jsonl", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(summary, open(f"{a.out_dir}/abst_{a.label}_summary.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"\n[abst] ÖZET {a.label}: rejection={summary['rejection_rate']} "
          f"fabrication={summary['fabrication_rate']} (geçerli {valid_total}/{len(out)}, "
          f"geçersiz {n_invalid}) ${spent:.3f}")


if __name__ == "__main__":
    main()
