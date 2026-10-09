# G2 — Gemini Flash-Lite, harness AÇIK · ADR-0057 kademe tablosu

**Tarih:** 2026-08-06 · **üretim git_sha:** `d88786c` *(koşu başına: [`KUNYE.json`](KUNYE.json) →
`git_sha_KOSU_BASINA`)* · **puanlama git_sha:** `ff64682` · **künye:** [`KUNYE.json`](KUNYE.json)

> 🚨 **BU BELGE 2026-08-06 AKŞAMI BAĞIMSIZ İNCELEMEDEN SONRA DÜZELTİLDİ.** Altı ayrı sayı/hüküm
> yanlıştı ve düzeltmelerin **yönü tek taraflı değil**: bazıları bizim, bazıları rakibin lehine.
> Düzeltilenler: **K1** muhakeme ortalamaları (`None` ↔ `0` karışmış) · **K2** muhakeme bütçesi
> rakipte UYGULANMIYOR · **K3** M2b paydası modele bağımlıydı · **Ö1** kesiklik şerhinin yönü
> tersti · **Ö7** `$/cevap` yalnız çıktıydı · **Ö8** kendi karşıolgumuzda TAVAN damgası yoktu.
> Her satırın altında önceki değer **silinmedi**, `~üstü çizili~` olarak duruyor.

> **Bu tablo, projenin tarihinde rakibin İLK KEZ ürün rejiminde (harness AÇIK) ölçüldüğü yerdir.**
> Bugüne kadar *"FL'ı geçtik/geçemedik"* cümlesi kurulamıyordu: bizim sayımız harness AÇIK,
> FL'ınki KAPALI'ydı — iki ayrı sınav.
>
> ⚠️ **Birim: "puan" = YÜZDE PUANI.** Hakem gürültü tabanı **0,3 puan**. Bundan küçük fark
> **yorumlanmaz**.

## Sınavın gerçekten eşit olduğunun kanıtı

| eksen | BİZ | 3.1 FL | 3.5 FL | durum |
| :--- | :--- | :--- | :--- | :--- |
| sorular | `core_hard.jsonl` n=80 | aynı | aynı | ✅ |
| kaynak sayısı (h1) | 10 | 10 | 10 | ✅ |
| kaynak sayısı (h2b) | 4 | 4 | 4 | ✅ |
| **recall@10** | **0,875** | **0,875** | **0,875** | ✅ **birebir aynı** |
| altın sızması (h2b) | 0 | 0 | 0 | ✅ |
| seed · klip · bütçe | 3407 · 900 · 1024+512 | aynı | aynı | ✅ |
| yeterlilik önsözü (h1) | AÇIK | AÇIK | AÇIK | ✅ |
| hakem yığını | `openai/gpt-4o-mini` · `openrouter` · `[OpenAI]` | aynı | aynı | ✅ |

⭐ **`recall@10`'un üç öznede de birebir 0,875 çıkması tesadüf değil, kanıttır:** erişim modelden
bağımsızdır, yani üç özne de **aynı bağlamı** gördü. Harness'ın aynı olduğu varsayılmadı, ölçüldü.

---

## Kademe tablosu — her satırda hüküm

| kademe | eksen | kaynak | BİZ (AÇIK) | 3.1 FL | 3.5 FL | hüküm |
| :--: | :--- | :--: | ---: | ---: | ---: | :--- |
| **2** | **M1 kütle** (cov × A1) | 10 ↔ 10 | **%62,8** | %61,7 | **%69,5** | ✅ **EŞLEŞMİŞ** — 3.1 FL'ı **+1,0 puan** geçtik *(gürültünün 3,4 katı — dar)*; 3.5 FL bizi **−6,7 puan** geçiyor *(22 katı — sağlam)* |
| **2** | **A1 · altın getirilen** | 10 ↔ 10 | **0,8705** | 0,7835 | 0,8607 | ✅ **EŞLEŞMİŞ** — **her ikisini de geçtik** (+8,7 puan sağlam · +1,0 puan **dar**) |
| **2** | **A1 · cevaplanan** | 10 ↔ 10 | **0,8229** | 0,7054 | 0,7940 | ✅ **EŞLEŞMİŞ** — **her ikisini de geçtik** (+11,8 · +2,9 puan) |
| **2** | **aşırı-red** (↓ iyi) | 10 ↔ 10 | **%23,75** | **%12,5** | **%12,5** | ✅ **EŞLEŞMİŞ** — 🚨 **iki rakibin de ~2 KATI. Turun ana borcu (B10) doğrulandı.** |
| **2** | coverage (↑ iyi) | 10 ↔ 10 | 0,7625 | 0,8750 | 0,8750 | ✅ EŞLEŞMİŞ — aşırı-red'in aynası |
| **2** | altın geldi ama çekindi | 10 ↔ 10 | **14/80** | 8/80 | 6/80 | ✅ EŞLEŞMİŞ — B10'un çekirdeği: bağlamda altın **var**, model yine susuyor |
| **2** 🆕 | ⭐ **M2b Rej\*** — **ÖNSÖZLÜ, eksen EŞLEŞTİ** | 4 ↔ 4 | **0,809** | **0,809** | **0,926** | ✅ **EŞLEŞMİŞ** — 3.1 FL ile **BİREBİR EŞİT**; 3.5 FL **+11,7 puan** önde. 🚨 **KESİKLİK ŞERHİ (tuzak 1.9):** 3.5 FL bu koşuda **8/80 = %10,0** kesik (`finish_reason=length`), kapının **2 katı**; 3.1 FL ve BİZ **0/80**. Ortak kesiksiz geçerli alt kümede (**n=60**) BİZ **0,800** · 3.1 FL **0,817** · 3.5 FL **0,950** → açıklık **11,7 → 15,0 puana GENİŞLİYOR**, daralmıyor. **Hüküm sağlam**, ama kesiklik yazılmadan kurulamaz |
| **3** | M2b Rej\* — önsöz**süz** çıpa | 4 ↔ 4 | **0,735** ~~0,840~~ | **0,809** ~~0,978~~ | **0,926** ~~0,982~~ | ⛔ **TANIMSIZ** (istem ekseni eşleşmiyor) — yalnız kayıt sürekliliği |
| **3** | M2b fabrication (↓ iyi) | 4 ↔ 4 | **0,191** (önsözlü) · 0,265 (önsözsüz) | **0,191** ~~0,022~~ | **0,074** ~~0,018~~ | ✅ önsözlü satır EŞLEŞMİŞ |
| **3** | M2b Rej (regex) | 4 ↔ 4 | **0,559** (önsözlü) · 0,647 (önsözsüz) | **0,632** ~~0,911~~ | **0,662** ~~0,768~~ | ⚠️ regex ekseni ayrı kalibrasyon taşır |
| **—** | muhakeme (reasoning tok) | — | **ölçülemiyor** | **769,6** ort · **735** med ~~789,4~~ | **445,2** ort · **198** med ~~868,8~~ | ⛔ **TANIMSIZ (K1+K2).** Ortalamalar düzeltildi; **etkin bütçe EŞLEŞMİYOR** |
| **—** | completion tok/cevap | 10 ↔ 10 | 803,9 | 970,5 | 573,6 | ⚠️ vekil eksen (düşünce iki tarafta da dâhil) |
| **—** | kesik oranı | 10 ↔ 10 | %3,8 | %3,8 | **%10,0** | ⚠️ **sebebi K2'dir** (rejim), 3.5 FL'ın özelliği değil — aşağıdaki şerh |
| **—** | **$/cevap** (liste, **girdi+çıktı**) | 10 ↔ 10 | **$0** (yerel) | **$0,002074** | **$0,002175** | ✅ ADR-0017. ⚠️ **3.5 FL %4,9 PAHALI** — yalnız çıktıya bakan eski satır sıralamayı TERS gösteriyordu |
| **—** | ~~$/cevap (yalnız çıktı)~~ | — | ~~$0~~ | ~~$0,001456~~ | ~~$0,001434~~ | 🚫 **GEÇERSİZ (Ö7)** — girdi yok sayılmış |

### 🚨 K3 — M2b'nin PAYDASI modele bağımlıydı, onarıldı

`score_abstention.judge()` hakeme soruyu, kaynağı **ve modelin cevabını** tek çağrıda veriyor,
`source_answers`'ı (tuzağın geçerli olup olmadığı) aynı JSON'da istiyordu. Oysa bu yargı
`(soru, bağlam)`'ın fonksiyonudur; hangi modelin skorlandığına bağlı olamaz.

Ölçüldü: sınav **birebir aynı** (`soru`, `context_shown`, `referans` üç kolda da bayt-bayt aynı),
buna rağmen **`valid_traps` fl31 45 · fl35 56 · BİZ 50**. Payda artık **cevaba kör** bir çağrıdan
ve içerik-adresli bir önbellekten geliyor:

| | valid_traps ESKİ → YENİ | Rej\* ESKİ → YENİ |
| :--- | :--- | :--- |
| BİZ (`olcum-h2b-k4`) | 50 → **68** | 0,840 → **0,735** |
| 3.1 FL | 45 → **68** | 0,978 → **0,809** |
| 3.5 FL | 56 → **68** | 0,982 → **0,926** |

⭐ **Doğrulama: üç kolun paydası artık EŞİT (68).** Düzeltmenin yönü **iki taraflı da değil,
herkesin aleyhine** — üç kol da düştü, en çok düşen 3.1 FL (−16,9 puan).

⚠️ **Bu, `ROADMAP`/plan'daki `M2b ≥ 0,840` eşiğini ilgilendirir:** o eşik **eski aletin
birimiyle** yazılmıştı. ADR-0050 kuralı gereği sonucu gördükten sonra **eşik değil ALET**
düzeltilir — burada alet düzeltildi, dolayısıyla eşik **yeni çıpadan yeniden türetilmelidir.**
Yeni çıpa yazıldı; **eşik değiştirilmedi, insan kararına bırakıldı.**

### ✅ M2b ekseni EŞLEŞTİ — TANIMSIZ damgası KALKTI (Ö5)

Bizim M2b çıpamız `--sufficiency-preamble` **olmadan** koşulmuştu, FL kolları **önsözle**.
Önsöz tam olarak *"kaynak yetersizse söyle"* diyen istemdir — ölçülen eksenin kendisini
değiştirir, dolayısıyla satır ADR-0057 gereği **TANIMSIZ** damgalıydı.

**Kapatıldı, $0:** `outputs/eval/g2b-m2b-onsozlu/` — önsözlü `h2b@k=4`, 80/80, **kesik %0,0**
(geçerlilik kapısı geçildi), zorunlu kapanış 55/80, aynı hakem yığını, aynı kör payda.

```
BİZ önsözSÜZ   Rej* 0,735      ← eski çıpa, artık yalnız kayıt sürekliliği
BİZ ÖNSÖZLÜ    Rej* 0,809      ← EŞLEŞMİŞ sayı  (valid_traps 68, Rej regex 0,559)
3.1 FL         Rej* 0,809      ← BİREBİR EŞİT
3.5 FL         Rej* 0,926
```

⭐ **İlk kez kurulabilen hüküm:** önsöz eklenince M2b'de **3.1 FL ile başa baş** geliyoruz
(0,809 ↔ 0,809), 3.5 FL **11,7 puan** önde. Önsözün bize kazandırdığı **+7,4 puan**
(0,735 → 0,809) — istem katmanının M2b'de ölçülmüş getirisi.

⚠️ **Bu, planın Görev 9 kapısının (`M2b Rej ≥ 0,840`) yeniden türetileceği çıpadır.**
Eşiğe **dokunulmadı** (insan kararı).

### ⚠️ 3.5 FL kesik şerhi — YÖNÜ ÖLÇÜLDÜ VE ŞERH TERSİNE ÇEVRİLDİ (Ö1)

Önceki şerh *"kesiklik 3.5 FL'in aleyhine, dolayısıyla hüküm muhafazakâr"* diyordu. **Bu
ölçülmeden yazılmıştı ve tersi doğru.** Üç kolda da kesik olmayan **ortak alt kümede (n=68)**:

| | kütle (80) | kütle (n=68) | Δ | A1·cevaplanan (80 → 68) |
| :--- | ---: | ---: | ---: | :--- |
| BİZ | 0,6275 | **0,6579** | **+3,0 p** | 0,8229 → 0,8603 |
| 3.1 FL | 0,6172 | 0,6516 | +3,4 p | 0,7054 → 0,7640 |
| 3.5 FL | 0,6948 | 0,7002 | **+0,5 p** | 0,7940 → 0,8210 |

Kesikliği kaldırmak **bize 3.5 FL'dan 6 kat çok yarıyor**; BİZ ↔ 3.5 FL farkı
**6,7 → 4,2 puana daralıyor**. Yani hüküm muhafazakâr değil, **bizim aleyhimize** eğilimliydi.

**Kesiklik hükmü — kol DÜŞÜRÜLMEDİ, gerekçesiyle:** planın *"oynuyorsa kol geçersiz"* ölçütü
katı uygulansa fl35 düşerdi (A1 ±1,65 p oynuyor). Düşürülmedi çünkü **K2 kesikliğin fl35'in
kusuru değil REJİMİN kusuru olduğunu gösteriyor** ve aynı kusur fl31'de de var (3 kalem).
Doğru davranış: **her sayıyı hem tam 80'de hem ortak kesiksiz n=68'de raporlamak** ve rejim
uyuşmazlığını damgalamak. Yapılan budur.

### 🚨 K2 — muhakeme bütçesi rakip tarafında UYGULANMIYOR

Kesik kalemlerin muhakeme token'ları: `fl35 [1473,1103,1475,1405,1472,1473,1470,1472]` ·
`fl31 [1157,1267,1222]` — **hepsi 1024'ün üstünde**; görülen en büyük değer **1475**.
`extra["reasoning"]={"max_tokens":1024}` sağlayıcı tarafından **yok sayılıyor**; tek bağlayıcı
sınır `max_tokens=1536`. Yani **rakipte muhakeme cevabın 512'lik payını yiyor**; ~~bizde ADR-0043
gereği ayrık bütçe + zorunlu kapanış var.~~

> 🚨 **BU CÜMLENİN İKİNCİ YARISI 2026-09-06'DA ÖLÇÜLDÜ ve ÇÜRÜDÜ ([ADR-0070](../../../docs/adr/0070-uretim-butcesi-esitlendi.md)).**
> Bizde de **ayrık bütçe yoktu**: `gen_eval_grounded` bizim kolda `max_tokens = think_budget`
> (**1024**) gönderiyordu; ayrı 512 payını **yalnız `content` boş kalan** (zorla kapatılan)
> kalemler alıyordu. Ölçüm, üç koşumuzda da aynı: zorla kapatılmayan kalemlerde tavan **tam 1024**
> (YENİ 75/80 · ESKİ 76/80 · ÇIPA 59/80), rakipte **1532** ve **36/80 (3.1 FL) · 18/80 (3.5 FL)**
> kalem 1024'ü **fiilen aşmış**.
> ⇒ **Sapmanın yönü bu şerhin söylediğinin TERSİ ve bizim aleyhimizeydi**: rakip 1536 toplam
> bütçeyle koşarken biz yaygın durumda 1024 ile koştuk. ADR-0043 §3 (*"bütün rakipler aynı
> bütçeyle koşar; sapma kıyası geçersiz kılar"*) gereği **bu tablodaki bütçe-duyarlı hükümler
> bu eksende damgalıdır.** Bütçe ADR-0070 ile eşitlendi (iki tarafta da tek formül, 1536);
> bu tablonun sayıları **eski rejimde** kalır.

**Künyedeki *"Bütçe EŞLEŞİK (1024 iki tarafta da)"* ifadesi YANLIŞTI:** *nominal* bütçe aynı,
**etkin** bütçe değil. Bu ADR-0057 anlamında bir **eksen uyuşmazlığıdır** — maliyet ve muhakeme
duyarlı hiçbir hüküm bu eksende kurulmaz. Ve **3.5 FL'ın %10 kesikliğinin gerçek sebebi budur**,
modelin özelliği değil.

---

## ⭐ 3.1 FL ↔ 3.5 FL: giriş katmanı 16 günde ne kadar kaydı

Bu kıyas **tam eşleşmiştir** — aynı gün, aynı sorular, aynı harness, aynı istem, aynı bütçe,
aynı hakem yığını. Tek değişen model sürümü.

| eksen | 3.1 FL | 3.5 FL | fark | yorum |
| :--- | ---: | ---: | ---: | :--- |
| **M1 kütle** (80) | %61,7 | **%69,5** | **+7,8 puan** | gürültü tabanının ≤26 katı — **üst sınır**, aşağıya bak |
| **M1 kütle** (n=68, kesiksiz) | %65,2 | **%70,0** | **+4,9 puan** | kesiklik çıkarılınca fark **daralıyor** |
| **A1 · cevaplanan** (80 → 68) | 0,7054 → 0,7640 | **0,7940 → 0,8210** | +8,9 → **+5,7 p** | sadakat belirgin yükseldi |
| **A1 · altın getirilen** | 0,7835 | **0,8607** | **+7,7 puan** | — |
| aşırı-red (toplam) | %12,5 | %12,5 | **0** | ⚠️ toplam eşit, **kalem düzeyinde değil** — aşağıya bak |
| M2b Rej\* *(kör payda)* | 0,809 | 0,926 | +11,7 puan | ⛔ TANIMSIZ eksen — hüküm kurulmuyor |
| kesik | %3,8 | %10,0 | +6,2 puan | **sebebi K2** (etkin bütçe), model farkı değil |
| **muhakeme tok/cevap** | **769,6** (med 735) | **445,2** (med 198) | **−324 (−%42)** | 🚨 **eski satır tersini söylüyordu**: 3.5 FL **daha AZ** muhakeme harcıyor |
| liste fiyatı (girdi/çıktı) | $0,25 / $1,50 /M | $0,30 / $2,50 /M | — | **$/cevap: $0,002074 → $0,002175 (+%4,9)** |

⚠️ **"Çekinme milimetre oynamadı" cümlesi TOPLAM EŞİTLİĞİNDEN kurulmuştu — kalem düzeyinde
yanlış.** Ölçüldü: aşırı-red kümeleri `3.1 FL {1,15,28,38,43,45,56,59,61,66}` ·
`3.5 FL {0,1,15,21,28,38,45,56,61,66}` → **örtüşme 8/10** (Jaccard 0,667); yalnız 3.1 FL
`[43, 59]`, yalnız 3.5 FL `[0, 21]`. Doğru okuma: *aşırı-red **oranı** değişmedi, **hangi
kalemlerde** olduğu değişti.*

⚠️ **Gürültü tabanı eksen karıştırıyor — çarpanlar ÜST SINIRDIR.** `0,3 puan` gürültü tabanı
**A1** için ölçüldü. Yukarıdaki *"26 katı"* / *"22 katı"* çarpanları **kütle** üzerinde kuruluyor;
kütle = coverage × A1 ve **coverage'ın kendi varyansı bu tabanda yok**. Dolayısıyla bu çarpanlar
gerçek anlamlılığın **üst sınırıdır**, ölçüsü değil.

**Okuma:** Google'ın giriş katmanı 16 günde **kütlede +7,8 puan** (kesiksiz alt kümede +4,9)
kazandı ve kazanç **sadakat** ekseninden geldi. Bu, `ROADMAP` §"Bakım halkası"nın *"belirgin
daha iyi bir base var mı"* sorusunun doğrudan verisidir: **rakip hareketli bir hedef.**
🚨 Ve muhakeme ekseninde kazanç **daha az düşünerek** geldi (769,6 → 445,2 token/cevap) — önceki
özet bunun tersini söylüyordu.

⚠️ **Şerh:** iki modeli **farklı upstream sağlayıcı** servis etti (3.1 FL → `Google AI Studio`,
3.5 FL → `Google`). Üretim tarafında sağlayıcı **pinlenmiyor** (`LLM_PROVIDER_ORDER` yalnız hakem
kapısında etkili). Farkın bir kısmı sağlayıcı kaynaklı **olabilir**; bu ihtimal elenmedi.

---

## Bu turun asıl bulgusu

**Sadakatte öndeyiz, çekinmede iki katı geridiyiz.**

```
A1 · altın getirilen     BİZ 0,8705  >  3.5 FL 0,8607  >  3.1 FL 0,7835     ✅ birinciyiz
aşırı-red                BİZ %23,75  «  3.1 FL %12,5   =  3.5 FL %12,5      🚨 iki katı
altın bağlamda ama sustu BİZ 14/80   «  3.1 FL 8/80    «  3.5 FL 6/80       🚨 B10
```

Model, altın maddeyi **görüyor**, gördüğünde **rakiplerden daha sadık** cevaplıyor — ama
**gördüğü hâlde 14 kez susuyor**, rakip aynı bağlamda 6-8 kez susuyor. Kütledeki kaybımızın
kaynağı sadakat değil, **çekinme**. Bu, B10'un rakip karşısında ilk kez **sayıyla**
doğrulanmasıdır.

### ⚠️ TAVAN / VARSAYIMSAL — kendi karşıolgumuz (Ö8)

> *"Aşırı-red kapatılabilse kütlemiz `0,875 × 0,8229 = %72,0`'a çıkar ve 3.5 FL'ı geçerdi."*

**Bu cümle bir ÖLÇÜM DEĞİL, bir TAVANDIR** ve damgası eksikti. İki varsayıma dayanıyor,
ikisi de iyimser:

1. **Çekindiği 19 kalem, cevapladıklarıyla AYNI sadakatte cevaplanacak.** Oysa o 19, modelin
   *cevaplamayı seçmediği* kalemler — yani sınavın **en zor** ucu. Cevaplanan A1'i (0,8229)
   onlara uygulamak, seçim yanlılığını yok saymak demektir.
2. **`0,875` paydası altın GELMEYEN 10 kalemde de doğru cevaplamayı gerektirir.** Tek-altın
   yer-gerçeğinde o kalemler tanım gereği **0** alır.

Rakibe TAVAN damgası basan bir belgede kendi karşıolgumuz damgasız kalamaz (ADR-0057 ruhu).
**Damga: TAVAN / VARSAYIMSAL — rakiple kıyas cümlesi bu satırdan KURULMAZ.**
Kurulabilecek cümle şudur ve o ölçülmüştür: *aşırı-red bizde rakibin iki katı, ve altın
bağlamdayken 14 kez susuyoruz (rakip 6-8).*

---

## Kaynak dosyalar

| sayı | dosya |
| :--- | :--- |
| BİZ h1 (çıpa) | `outputs/eval/olcum-bi/harness_tablo.json` · `a1_h1_tgta_v1_bi_k10.txt` |
| BİZ M2b (çıpa, önsözSÜZ) | `outputs/eval/olcum-h2b-k4/abst_h2b_tgta_v1_h2b_k4_summary.json` |
| BİZ M2b (**önsözlü**, eksen eşleştirme) | `outputs/eval/g2b-m2b-onsozlu/` |
| kör payda önbelleği | `outputs/eval/_artefakt/valid_trap_kor_onbellek.json` |
| K3 öncesi puanlamalar | her klasörde `abst_*_summary.json.ONCEKI-PAYDA` |
| 3.1 FL | `harness_tablo_h1_fl31.json` · `a1_h1_fl31.txt` · `abst_h2b_fl31_k4_summary.json` |
| 3.5 FL | `harness_tablo_h1_fl35.json` · `a1_h1_fl35.txt` · `abst_h2b_fl35_k4_summary.json` |
| hakem ham çıktısı | `gnd_h1_fl31.jsonl` · `gnd_h1_fl35.jsonl` · `abst_h2b_*_k4.jsonl` |

⛔ **`cp09-butceli-1024-512`'deki eski FL sayıları (%72,9 · A1 0,9561) bu tabloya GİRMEZ** —
eski hakem yığınında (`gpt-4o-mini` / doğrudan `openai`, ADR-0041 öncesi istem) ve harness
KAPALI üretilmişlerdir. Aşağıdaki satır **yalnız kayıt sürekliliği** içindir:

| damga | koşu | kütle | A1 (cevaplanan) | hüküm |
| :--- | :--- | ---: | ---: | :--- |
| 🚫 **eski hakem yığını — HÜKÜM YOK** | 3.1 FL, harness **KAPALI**, cp09 | %72,9 | 0,9561 | kıyaslanamaz |
| ⚠️ güncel yığın, harness **KAPALI** | 3.1 FL, `g1-eslesmis-a1` gnd + yeni regex | %75,6 | 0,9605 | **TAVAN** — rejim eşleşmiyor, hüküm YOK |

⚠️ Harness KAPALI sayılar **TAVAN**dır, rakip değil: KAPALI'da altın madde bağlamda **garanti**
verilir. AÇIK'ta erişim onu %87,5 oranında bulur. İki ayar **aynı şeyi ölçmez**.

---

## 🚨 Ö-C · Kesiklik kapısı SİMETRİK uygulandı (tuzak 1.9) — 2026-08-06

Repo kendi `tg_ta_nb` varyantını **%5,2** kesiklikle *"koşu geçersiz"* saymıştı
([#48](../../../docs/record/research_log/2026-08-02-cp2c-modal-koprusu.md)). Emsal ters
yönde uygulanmamış: `h2b_fl35_k4` **%10,0** kesikle manşet hükmün kurulduğu koldur ve
şerhi yoktu. Ölçüm (`finish_reason == "length"`, `forced_close` DEĞİL — o bizim bütçeli
zorla kapatmamız, kesiklik değil):

```
h2b_fl31_k4          kesik 0/80  (%0,0)
h2b_fl35_k4          kesik 8/80  (%10,0)   ← kapının 2 katı
h2b_tgta_v1_onsozlu  kesik 0/80  (%0,0)
```

**Simetrik okuma — ortak kesiksiz ∧ geçerli alt küme (n=60 = 68 geçerli − 8 kesik):**

| kol | tam (n=68) | alt küme (n=60) | fark |
| :--- | ---: | ---: | ---: |
| BİZ (önsözlü) | 0,809 | 0,800 | −0,009 |
| 3.1 FL | 0,809 | 0,817 | +0,008 |
| **3.5 FL** | **0,926** | **0,950** | **+0,024** |

**Sonuç: açıklık daralmıyor, GENİŞLİYOR** (11,7 → 15,0 puan). 3.5 FL'ın üstünlüğü
kesikliğin eseri **değil**; kesilen kalemler onun daha zayıf olduğu kalemlermiş.
Hüküm **ayakta ve güçlenmiş** — ama şerh olmadan kurulamazdı.

*(İnceleme n=59 · 0,949 demişti; buradaki yeniden hesap n=60 · 0,950 veriyor — fark
kesiklik ölçütünün tanımından. Yön ve büyüklük aynı.)*
