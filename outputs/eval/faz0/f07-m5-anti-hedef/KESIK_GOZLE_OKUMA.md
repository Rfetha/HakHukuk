# F0.7 — M5 kesik kalemlerinin GÖZLE OKUNMASI

> ⛔ **Bu okuma GEÇERSİZ ilan edilen koşuya dayanır** (kesik %6,2 > %5) — ham dosya artık
> [`GECERSIZ-kesik6.2-drysiz/`](GECERSIZ-kesik6.2-drysiz/NEDEN_GECERSIZ.md) altında.
> Okuma **silinmiyor**: [ADR-0073](../../../docs/adr/0073-m5-rejimine-dry-eklendi.md)'ün
> gerekçesinin kanıtı budur.

**Tarih:** 2026-09-07 · **koşu:** `m5_tgta_v1_m5_v2` · **ara kayıt:** 62/80 kalem işlenmişken

**Neden:** kesiklik geçerlilik kapısının (%5, ADR-0040) sınırında seyrediyor. Kapı bir
SAYI; o sayının **hangi kusur sınıfını** saydığını yalnız gözle okuma söyler.

## Ölçüm: `finish_reason='length'` = **4/62** (%6.5)

| id | kanun/madde | tok | zorla | cevap | **GÖZ hükmü** | okunan kanıt |
| :-- | :--- | --: | :-- | --: | :--- | :--- |
| 27 | KAT MÜLKİYETİ KANUNU Madde 33 | 1536 | hayır | 3 kar | **kesilme (bütçe)** | düşünceye 1536 token yakıp cevaba 3 karakter kaldı: `"Kat"` |
| 28 | TÜRK BORÇLAR KANUNU MADDE 230 | 2048 | evet | 1791 kar | **🚨 yozlaşmış tekrar** | *"…bilgi verilmediği durumlarda"* ibaresi cevabın sonunda 4 kez arka arkaya |
| 43 | CEZA MUHAKEMESİ KANUNU Madde 174 | 1536 | hayır | 146 kar | **kesilme (bütçe)** | cümle ortasında gerçek kesilme: *"…mahkeme tarafından kabul edilirse"* |
| 54 | İŞ KANUNU Madde 31 | 2048 | evet | 2040 kar | **🚨 yozlaşmış tekrar** | *"askeri hizmet süresince"* ibaresi 12 kez arka arkaya |

**Sınıf dağılımı (göz):** yozlaşmış tekrar **2** · bütçe kesilmesi **2**

> ⚠️ **Alet ↔ göz çelişkisi, bu turun ana dersinin küçük tekrarı.** İlk yazımda sınıfı
> otomatik bir tekrar-sezgisi atadı ve **id 28'i "bütçe kesilmesi" saydı**; tam metin okununca
> tekrar döngüsü olduğu görüldü (pencere/adım seçimi ibareyi kaçırmış). **Hüküm gözündür**,
> sezgi kayda **yanlış hâliyle** girmedi ama çelişki burada duruyor.

## 🚨 Bulgu: kapının düzeltme reçetesi kusurun YARISINA uymuyor

ADR-0040'ın geçerlilik ön şartı: *"kesik > %5 → **MAXTOK büyütülüp tekrar koşulur**;
puanlamaya para harcanmaz."* Bu reçete **bütçe kesilmesi** için doğrudur (id 27 · 43).
**Yozlaşmış tekrarda değildir** (id 28 · 54): bütçeyi büyütmek yalnız **daha uzun bir döngü**
üretir — GPU yanar, oran düşmez.

Bu, [#42](../../../docs/record/research_log/2026-07-29-cp0-dusunce-modu-sonlanmama.md)'nin
*"kesilme değil **sonlanmama**"* bulgusunun **merge kolunda, kör modda** tekrarı. Orada bütçe
**8× artırılmış (4096 → 32768) ve hiçbir şey değişmemişti**; yarısını kurtaran şey `temp 0.6`
olmuştu, bütçe değil.

⛔ **Kapı OYNATILMIYOR** (ADR-0050). Burada yapılan tek şey, kapının saydığı sayının **neyi
saydığını** kayda geçirmek. Koşu bitişte de %5'i aşarsa hüküm **insana sorulur**: ön-kayıtlı
düzeltme yolu bu kusur sınıfında **ölçülmüş biçimde etkisizdir**, dolayısıyla ne yapılacağı
ADR-0040'ın kapsamadığı **yeni bir rejim kararıdır**.

## Kör mod bunu neden yapıyor
M5'te modele **hiç kaynak verilmiyor** (`context_shown` boş, 80/80). Dayanacağı metin yokken
üretim serbest çağrışıma düşüyor. Bu, M5'in **anti-hedef** ilan edilme gerekçesiyle aynı yöne
bakar: ürün rejiminde modele **her zaman** kaynak verilir; M5 koşulları üründe hiç oluşmaz
([ADR-0039](../../../docs/adr/0039-kapi-6-parametrik-sizinti.md) §4 madde 3).

## 🚨 Ters etki: yozlaşma bizi anti-hedefte OLDUĞUMUZDAN İYİ gösterebilir

Yozlaşmış cevap **çekinme değildir** — `exact_reject` onu red saymaz, dolayısıyla
**"cevaplandı" sayılır** ve `coverage`'ı **yükseltir**. Hakem ise içeriğine düşük sadakat
verir, yani **A1'i düşürür**. Anti-hedefin metriği:

```
ezber kütlesi = coverage × A1
```

⇒ Bir döngü kalemi paydaya girip A1'i aşağı çektiği için **ezber kütlesini düşürür** ve
kapı maddesi (3) *"M5 yükselmedi ✅"* der — oysa sebep modelin ezberlememesi değil,
**cümleyi bitirememesi**. Bu, [ADR-0044](../../../docs/adr/0044-mod-duyarli-feragat-kurali.md)'ün
yakaladığı *"sapma **bizim lehimize**"* sınıfının aynısıdır ve orada ezber kütlesi
**3,4× küçük** ölçülmüştü.

**Dengeleyen şey:** base çıpası **birebir aynı ayarlarla** koşuluyor (aynı GGUF kuantizasyonu,
aynı `temperature=0`, aynı 1536 bütçe, aynı 80 soru, aynı taşıyıcı). İki kol da aynı kusura
maruz ⇒ **fark** hâlâ okunabilir. Okunamaz olan **mutlak** değerdir.

⛔ Bu yüzden madde (3)'ün hükmü yayımlanırken şu şerh **zorunlu**: *"M5'in mutlak değeri
kör-modda yozlaşma tarafından aşağı çekiliyor; hüküm yalnız **base'e göre fark** üzerinden
kurulur."*
