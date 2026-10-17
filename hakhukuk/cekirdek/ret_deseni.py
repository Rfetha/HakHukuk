"""Deterministik red ifadesi deseni — ürün (`terazi.py`) ve ölçüm hattı (`score_abstention.py`)
aynı nesneyi buradan alır; kopyalanmaz (kusur 11, 2026-10-17).
"""
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
