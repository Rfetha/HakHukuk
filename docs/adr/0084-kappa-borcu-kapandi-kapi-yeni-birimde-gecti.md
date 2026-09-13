# ADR-0084 — κ borcu ADR-0074'ün koşuluyla kapandı; kapının üç maddesi **yeni birimde** okundu: GEÇTİ

**Tarih:** 2026-09-13 (yazım) · ölçüm 2026-09-12 · **Statü:** ✅ yürürlükte · **Karar:** mekanik
(ön-kayıtlı formül, ADR-0050 · ADR-0064)
**Bağlı:** [ADR-0064](0064-v1-kapisi-uc-maddeli-on-kayit.md) (kapının üç maddesi) ·
[ADR-0074](0074-hakem-paneli-kuruldu-baglayici-hukum.md) (κ borcunun tanımı ve tek cümlelik
kapanma koşulu) · [ADR-0077](0077-v1-0-verilmedi-v0-3.md) (`v1.0`'ın önündeki tek açık madde) ·
[ADR-0032](0032-hakem-paneli-uc-aile-ve-aile-dislama.md) (üç aile kuralı) · [ADR-0050](0050-verim-kapisi-tahmin-edici-duzeltmesi.md)
(alet değişirse eşik aynı formülle yeniden türetilir)
**Kaynak:** `outputs/eval/hp-hakem-paneli/KAPPA.md` · `outputs/eval/f04-rakip-onsozsuz/KALIBRASYON_ve_OZET.md`
· `outputs/eval/f07-m5-anti-hedef/KUNYE.json` · plan `docs/superpowers/plans/2026-09-12-v1-son-is.md`
Adım 6.5/6.7 · `.superpowers/sdd/progress.md` BULGU-I · BULGU-N

## Ön-kayıt (aynen alıntı, sayı görülmeden yazıldı)

ADR-0074'ün kapanma koşulu tek cümleydi ve bu ADR'nin koşusundan **önce** yazılmıştı:

> *"Borcun kapanma koşulu tektir: `3.5 Flash` kolunun **aynı ikinci hakemle** puanlanması."*

ADR-0064'ün kapı formülü de değişmeden, sonuç görülmeden önce yazılmış hâliyle yürürlüktedir:

```
(1) kütle ≥ (3.5 Flash'ın kütlesi) − 2,0 puan     ← ASIL KAPI, eşleşmiş rejim, aynı 80 soru
(2) isabetsizlik GERİLEMEZ                         ← vatandaş için en tehlikeli kusur sınıfı
(3) M5 (kör/parametrik) YÜKSELMEZ                  ← ANTİ-HEDEF, ezber kazancı kapıdan geçmez
(*) her sayım adımında GÖZLE OKUMA zorunlu         ← sayısal kapı bozuk ölçümü bir kez geçirdi
```

## Ölçülen (2026-09-12)

**Koşul karşılandı.** Rakip kolu (`3.5 Flash`, 80 cevap) **aynı ikinci hakemle**
(`claude-sonnet-5`) yeniden puanlandı — üretim yeniden koşulmadı, yalnız hakem değişkeni oynadı
(ADR-0017). Kapının üç maddesi, artık **eşleşmiş** iki hakem altında ayrı ayrı okundu.

### Sonuçlar — üç madde, iki hakem, marjlar **çıpaya göre**

| madde | ölçü | çıpa (`3.5 Flash`, GÖZ-katı) | eşik (çıpa − 2,0 p) | BİZ | marj **çıpaya göre** | marj **eşiğe göre** | hüküm |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| **(1)** kütle | `gpt-4o-mini` | 0,7425 | 0,7225 | **0,8011** | **+5,86 p** | +7,86 p | ✅ **GEÇTİ** |
| **(1)** kütle | `claude-sonnet-5` | 0,6183 | 0,5983 | **0,6940** | **+7,57 p** | +9,57 p (7,7 adım) | ✅ **GEÇTİ** |
| **(2)** isabetsizlik | *(hakemden bağımsız — bkz. altta)* | 8/80 | — | **8/80** | tanım gereği | — | ✅ |
| **(3)** M5 | *(hakemden bağımsız — bkz. altta)* | base 0,4697 (ALET) / 0,4739 (GÖZ) | — | 0,3899 / 0,4057 | **−7,98 p** / **−6,82 p** | — | ✅ **GEÇTİ** |

Çözünürlük bandı `n=80` için **1,25 puan/kalem**dir; marjların hepsi bu bandın **kat kat**
üstünde — hüküm okuma seçimine bağlı değil, **iki bağımsız hakem ailesi aynı yönde**.

**Madde (2) ve (3) neden hakemden bağımsız taşındı — "taşındı" ≠ "bakılmadı".** Bu turda
ağırlıklar **hiç değişmedi** (`tgta_v1` sabahki artefaktın aynısı) ve isabetsizlik/M5 sayıları
üretim yeniden koşulmadan **hakem-öncesi** deterministik/gözle-okuma katmanından geliyor —
ikinci hakem panelinin ölçtüğü eksen yalnız `faithfulness`'tır (madde 1). Madde (2) ve (3)
sayıları bu yüzden ADR-0064'ün kendi ölçümüyle **aynen** durur; kontrol edildi, yeniden ölçülmesi
gerekmiyordu.

## Karar

**(a) Kapı üç maddesiyle GEÇTİ — yeni birimde.** İki hakem ailesi de aynı yönde hükmetti ve
ikinci hakemde marj **daha geniş** çıktı (+7,57 p ↔ +5,86 p, çıpaya göre). `v1.0`'ın önündeki
madde (b) — ADR-0077'nin *"her sayı hâlâ tek hakem ailesinin hükmü"* engeli — **kapandı**:
eşit sınava sokulmuş **iki** aile artık aynı yönde hükmediyor.

**(b) κ DEĞİŞMEDİ — kapanan şey κ değil, eşit sınavın yokluğuydu.** ADR-0074'ün ölçtüğü
`tam_sadık` κ **0,534** ve `atıf_temiz` κ **0,409**, bu ADR'de **hiç yeniden ölçülmedi** ve
**aynı kalıyor**. *"κ düzeldi"* cümlesi **kurulmaz**. Kapanan borç, ADR-0074'ün kendi
tanımladığı **dar** koşuldu (*"3.5 Flash aynı ikinci hakemle puanlansın"*) — κ'nın kendisi
zayıf kalmaya devam ediyor; bu ADR onu **yükseltmiyor**, yalnızca **etrafında** eşit sınav
kurulduğunu ve o eşit sınavda hükmün değişmediğini kaydediyor.

**(c) ADR-0074 (b) ↔ ADR-0077 gerilimi — grill karar 4 ile çözülür, iki yerde damgalanır.**
ADR-0074 madde (b) κ < 0,6'yı *"geçersiz kılmaz, **kırılgan** yapar"* diyordu; ADR-0077 aynı
κ'yı `v1.0`'ın önündeki **açık madde/engel** saydı. İkisi de doğru okumaydı, farklı bağlamda:
ADR-0074 tek-hakemli haldeki yayımlanan sayının **durumunu** tarif ediyordu, ADR-0077 **sürüm
verme eşiğinin** kendisini tarif ediyordu. Bu ADR ikisini şöyle uzlaştırır: *kırılgan bir sayı,
ikinci bağımsız bir hakemle aynı yönde doğrulanınca artık yalnızca "tek ailenin hükmü" değildir
— kırılganlığın kaynağı (κ zayıf) durmaya devam eder, ama sürüm eşiğini bloke eden özel biçimi
(başka aileyle sorulsa hüküm değişir mi bilinmiyor) ortadan kalkar.* Çelişki **iki yerde**
damgalanır, biri diğerinin üstüne **yazılmaz** (ADR-0082'nin emsali): bu ADR'nin metni burada
duruyor, ve [ADR-0077](0077-v1-0-verilmedi-v0-3.md)'nin sonuna **tek satırlık işaretçi**
düşüldü — ADR-0077'nin kendi metni **değiştirilmedi**, yalnız bir güncelleme notu eklendi.

**(d) ADR-0032'nin üç aile kuralı hâlâ 2/3'te — açık gerilim, eksiklik olarak yazılır.** Panel
bu turda da **Google hakem** ailesiyle genişlemedi (bütçe nedeniyle — ADR-0074'ün kendi kararı).
Kapının hükmünü **değiştirmez** (madde 1 iki ailenin ikisinde de GEÇTİ), ama üç-aile kuralından
sapma **duruyor** ve bu, gelecekteki bir turun borcu olarak burada **açıkça yazılır**: panel
hâlâ **iki** aileli, üçüncüsü (Google) hiç ölçülmedi.

## Ne KURULMAZ

1. **"İki hakem geçti ⇒ sayı kesin."** İki bağımsız aile aynı yönü gösterdi, bu **güçlü bir
   sinyaldir** — ama κ zayıf kalmaya devam ediyor ve üçüncü aile (Google) hiç ölçülmedi
   (madde d). "Kesinlik" iddiası bu ADR'den **kurulmaz**.
2. **"κ düzeldi."** κ hiç yeniden ölçülmedi; **0,534 / 0,409 aynı kalıyor.**
3. **Ürün-yolunun kütlesi (0,7792, ADIM 6.3b) kapı maddesine girmez.** O sayı ölçüm hattında
   değil ürün yolunda ölçüldü ⇒ eşit sınav değil, kapının çıpasıyla **kıyaslanamaz** ([ADR-0064](0064-v1-kapisi-uc-maddeli-on-kayit.md)'in
   kendi ön-kaydı böyle koymuştu).
4. **S17 kuantizasyon eğrisi (ADIM 6.3c) hiçbir artefaktı değiştirmez.** Eğri bir **ifşadır**,
   sürüm önerisi değil (ön-kayıt, ADR-0071); bu ADR'nin kapı hükmü `Q4_K_M` yayımlanan artefaktı
   üzerinedir.
5. **Öz-tercih sonucu (ADIM 6.6b, Anthropic ailesi) hiçbir hükme girmez.** Tek özne/tek koşu
   göstergesidir; kapının GEÇTİ hükmünü **desteklemek için de kullanılmaz** — hakemin kendi
   ailesini bizden daha sert cezalandırması, bu ADR'nin madde-1 hükmünü **değiştirmiyor**, yalnız
   "hakem bizi kayırdı" itirazını bağımsız olarak zayıflatıyor (ayrı bulgu, ayrı kapsam).
6. **Bu ADR `v1.0` ETİKETİ VERMEZ.** Sürüm kararı adım 9'un işidir ve **DUR ③**'ü taşır
   ([ADR-0065](0065-bolunmus-surumleme.md)'in bölünmüş sürümlemesi gereği); bu ADR yalnız
   *"kapının üç maddesi yeni birimde GEÇTİ"* der, sürüm numarasına hükmetmez.
7. **"Rakip kolu her iki hakemle de aynı sayıyı verdi" denemez.** `3.5 Flash`'ın kendi kütlesi
   hakem değişince **düştü** (0,7425 → 0,6183); değişmeyen şey **kapının hükmüdür**, rakibin
   mutlak sayısı değil.

## Reddedilenler

| seçenek | niçin reddedildi |
| :--- | :--- |
| κ'yı yükseltmek için ek koşu/kalibrasyon yapmak | Kapsam dışı (ADIM 6.8 yalnız yazım); κ borcu ADR-0074'ün **dar** koşuluyla zaten kapandı |
| Üçüncü aileyi (Google) bu turda eklemek | Bütçe — ADR-0074'ün kendi kararı, bu turda yeniden açılmadı; madde (d)'de eksiklik olarak kayıtlı |
| ADR-0077'yi geriye dönük **düzenlemek** ("madde (b) artık kapandı" diye yeniden yazmak) | Audit trail ilkesi (`CLAUDE.md` "Documentation discipline"): eski karar olduğu gibi durur, işaretçi **eklenir**, üstüne yazılmaz |
| Bu ADR'de `v1.0` ilan etmek | Kapsam dışı — sürüm adım 9'un ve DUR ③'ün işi |
