# B10 çıpası — 80 kalemin GÖZLE OKUNMASI

- **Tarih:** 2026-09-06 · **Dayanak:** [ADR-0061](../../../docs/adr/0061-cekinme-dedektoru-istem-rejimi-bagimliligi.md) Karar 1 · ölçüm [#60](../../../docs/record/research_log/2026-09-06-hasat-kabul-olcutu-coktu.md)
- **Koşu:** `outputs/eval/olcum-bi/h1_tgta_v1_bi_k10_detail.jsonl` — resmî ana protokol, n=80, harness AÇIK, k=10, yeterlilik önsözlü (ADR-0058)
- **Yöntem:** her kalemin `cevap` alanı TAM METİN okundu. ⛔ Programatik sonda ölçüt DEĞİLDİR — #60 onun **her iki yönde** yanıldığını ölçtü.
- **Maliyet:** hakem **$0**, GPU **$0** (yalnız okuma).

## Sayılar

| ölçüt | çekinme | coverage | **B10** (altın geldi **ve** çekindi) | altın gelmedi + çekindi |
| :--- | ---: | ---: | ---: | ---: |
| ⭐ **gözle okuma (ölçüt budur)** | **13 / 80** | **0,8375** | **8 / 80** | 5 |
| onarılmış alet (`exact_reject` v4) | 14 / 80 | 0,8250 | 9 / 80 | 5 |
| eski alet (v3, yayımlanmış sayı) | 19 / 80 | 0,7625 | **14 / 80** | 5 |

`recall@10 = 70/80` — üç ölçütte de aynı (erişim `exact_reject`'ten bağımsız).

### Ürün sayısının üç ölçütteki karşılığı (`kütle = coverage × A1_cevaplanan`)

| ölçüt | coverage | A1 (cevaplanan) | **kütle** |
| :--- | ---: | ---: | ---: |
| ⭐ gözle okuma | 0,8375 | 0,8314 | **0,6963** |
| onarılmış alet v4 | 0,8250 | 0,8288 | **0,6838** |
| eski alet v3 (yayımlanmış) | 0,7625 | 0,8229 | **0,6275** |

⛔ Bu satırlar **yalnız sayıdır, hüküm değildir.** Eşiklerin yeni birimde yeniden
türetilmesi [ADR-0061 Karar 2](../../../docs/adr/0061-cekinme-dedektoru-istem-rejimi-bagimliligi.md)
gereği **ayrı iştir ve insan onayı ister**; burada dokunulmadı.

**Eski aletin 14 B10'unun 6'sı yanlış pozitiftir:** `id` 19 · 32 · 44 · 53 · 65 · 77.
Altısında da tetikleyen ibare cevabın hükmü değil, **elenen kaynakların gerekçesi**
(`Diğer kaynaklar … içermemektedir`). ⛔ Yanlış NEGATİF yok: gözle okunan 13 çekinmenin
13'ünü eski alet de yakalamıştı.

## Onarılmış alet ↔ gözle okuma uyuşmazlığı: **1 / 80**

**`id=32`** — alet ÇEKİNME diyor, gözle okuma CEVAP.

> "Verilen kaynaklarda bu konuyu düzenleyen madde bulunmuyor. … **KAYNAK 2**, duruşmaya
> katılmama durumunda … açıkça belirtmektedir. **Bu nedenle, mazeret bildirmezseniz ve
> duruşmaya katılmazsanız, mahkeme duruşmaya devam edecektir ve yapılan işlemlere itiraz
> edemeyeceksiniz.**"

Model açılışta reddediyor, sonra **kendi açılışını yalanlayıp** KAYNAK 2'den tam cevabı
veriyor. Bu, [#57/Ö2](../../../docs/record/research_log/2026-08-06-cekinme-aleti-onarimi.md)
vakasının **ayna görüntüsüdür** (orada olumlu açılış gövdede yalanlanıyordu).

⛔ **KAPATILMADI, bilerek.** Tüm `outputs/eval`'da ölçülen örnek sayısı **1**; Rule of Three
gereği tek örnekte kural kurulmaz ve ADR-0050'nin ruhu ("sonucu görüp aleti kurcalama")
buna karşıdır. Sınırı `tests/test_score_abstention.py`'daki
`test_exact_reject_acilis_reddini_YALANLAYAN_govde_kacar` **xfail(strict)** testi çiziyor:
kural bir gün genişletilirse o test **patlar** ve bu damga kaldırılmak zorunda kalır.

## Kalem kalem

`ilk` / `son` sütunları REJECT_RE'nin **ilk** ve **son esaslı ibarede** eşleşen deseni;
`altın` sütunu altın maddenin bağlama getirilip getirilmediği (B10'un payı). 🚩 = uyuşmazlık.

| id | gözle | alet v4 | alet v3 | ilk ibare | son ibare | altın | gerekçe |
| ---: | :--- | :--- | :--- | :--- | :--- | :-: | :--- |
| 0 | **ÇEKİNME** | ÇEKİNME | ÇEKİNME | `bulunmuyor` | `bulunmuyor` | ✘ | Tek cümlelik kaynak-yokluğu beyanı; başka içerik yok.  |
| 1 | **cevap** | cevap | cevap | — | — | ✔ | Eleme gerekçesi + alıntı + `Sonuç olarak … temyiz edilebilir` (CMK 286).  |
| 2 | **cevap** | cevap | cevap | — | — | ✔ | Yedi bentlik suç listesi sayılmış (CMK 153).  |
| 3 | **cevap** | cevap | cevap | — | — | ✔ | TBK 35 alıntısı; `tazminat istenemez` hükmü verilmiş.  |
| 4 | **cevap** | cevap | cevap | — | — | ✔ | El konulan gönderilerin akıbeti CMK 129 ile açıklanmış.  |
| 5 | **cevap** | cevap | cevap | — | — | ✔ | TCK 227 ceza aralığı verilmiş.  |
| 6 | **cevap** | cevap | cevap | — | — | ✘ | İhbar sonrası usul anlatılmış, atıflı (3628 s.K. m.18).  |
| 7 | **ÇEKİNME** | ÇEKİNME | ÇEKİNME | `bulunmamaktadır` | — | ✔ | Açılışta kaynak-yokluğu hükmü; devamı kaynak DIŞI maddeye (İş K. 21) işaret ediyor, kaynaklardan cevap YOK.  |
| 8 | **cevap** | cevap | cevap | — | — | ✔ | TMK 313 evlât edinme şartları sayılmış.  |
| 9 | **cevap** | cevap | cevap | — | — | ✔ | TBK 139 alıntısıyla takas koşulu verilmiş.  |
| 10 | **cevap** | cevap | cevap | — | — | ✔ | `Evet … kendiliğinden kalkar` (HMK 393).  |
| 11 | **cevap** | cevap | cevap | — | — | ✔ | TCK 184 ceza aralığı.  |
| 12 | **cevap** | cevap | cevap | — | — | ✔ | İş K. 4; `geçerli değildir` olumsuzlaması HUKUKUN içeriği, kaynağın değil.  |
| 13 | **cevap** | cevap | cevap | — | — | ✔ | TMK 313 metni; beş yıllık süre okunabiliyor.  |
| 14 | **ÇEKİNME** | ÇEKİNME | ÇEKİNME | `bulunmuyor` | `bulunmuyor` | ✔ | Tek cümlelik kaynak-yokluğu beyanı.  |
| 15 | **cevap** | cevap | cevap | — | — | ✔ | TMK 403 vasi yükümlülüğü.  |
| 16 | **cevap** | cevap | cevap | — | — | ✔ | `Hakem kararında karşı oy yazısı yer alabilir` (HMK 436).  |
| 17 | **cevap** | cevap | cevap | — | — | ✔ | İş K. 24 fesih hakkı.  |
| 18 | **cevap** | cevap | cevap | — | — | ✔ | TCK 77 metni; `zorla fuhşa sevketme` bendi gösterilmiş.  |
| 19 | **cevap** | cevap | ÇEKİNME | — | — | ✔ | Tetikleyici `içermemektedir` ELENEN kaynakların gerekçesinde; hüküm TKHK 53 ile verilmiş. #60'ta doğrulanmış yanlış pozitif.  |
| 20 | **ÇEKİNME** | ÇEKİNME | ÇEKİNME | `bulunmamaktadır` | — | ✔ | Açılışta kaynak-yokluğu; gövde kaynak dışı maddeyi tarif edip yine `düzenlememektedir` diyor.  |
| 21 | **cevap** | cevap | cevap | — | — | ✘ | EURO dönüşümü açıklanmış. (Atıf `KANUN ADI` — atıf kusuru, çekinme değil.)  |
| 22 | **cevap** | cevap | cevap | — | — | ✔ | KMK 35 yönetici görevleri.  |
| 23 | **cevap** | cevap | cevap | — | — | ✔ | `ikinci toplantı en geç on beş gün sonra` — atıf kırpılmış ama hüküm var.  |
| 24 | **ÇEKİNME** | ÇEKİNME | ÇEKİNME | `bulunmuyor` | `bulunmuyor` | ✔ | Tek cümlelik kaynak-yokluğu beyanı.  |
| 25 | **cevap** | cevap | cevap | — | — | ✔ | TBK 344 kira artış ölçütü.  |
| 26 | **cevap** | cevap | cevap | — | — | ✔ | AATUHK 58 alıntısı.  |
| 27 | **ÇEKİNME** | ÇEKİNME | ÇEKİNME | `bulunmuyor` | `içermemektedir` | ✘ | Kaynak-yokluğu + kaynakların neyi kapsadığının açıklaması; esaslı hüküm yok.  |
| 28 | **ÇEKİNME** | ÇEKİNME | ÇEKİNME | `bulunmuyor` | `bulunmuyor` | ✘ | Tek cümlelik kaynak-yokluğu beyanı.  |
| 29 | **cevap** | cevap | cevap | — | — | ✔ | TKHK 24; on dört gün.  |
| 30 | **cevap** | cevap | cevap | — | — | ✔ | TBK 139 takas koşulları.  |
| 31 | **cevap** | cevap | cevap | — | — | ✔ | ⚠️ ZAYIF: `KAYNAK 1 toplu yapı tanımını içermektedir` + KMK 66 atfı. Tanım metni verilmemiş ama RED de yok — cevap sayıldı.  |
| 32 | **cevap** | ÇEKİNME | ÇEKİNME | `bulunmuyor` | — | ✔ | 🚩 UYUŞMAZLIK: açılışta red var, model kendini YALANLAYIP KAYNAK 2'den tam cevap veriyor (`mahkeme duruşmaya devam edecektir … itiraz edemeyeceksiniz`). 🚩 |
| 33 | **cevap** | cevap | cevap | — | — | ✘ | AYM K. 49; başvurunun Adalet Bakanlığına gönderilmesi.  |
| 34 | **cevap** | cevap | cevap | — | — | ✔ | Bankacılık K. 166.  |
| 35 | **cevap** | cevap | cevap | — | — | ✔ | HMK 316 basit yargılama usulü.  |
| 36 | **cevap** | cevap | cevap | — | — | ✔ | ⚠️ BOZUK ÇIKTI: KMK 12 belgeleri alıntılanmış, (b)-(o) bentleri döngüye girmiş. Red YOK.  |
| 37 | **cevap** | cevap | cevap | — | — | ✔ | TMK 401 güvence şartı.  |
| 38 | **cevap** | cevap | cevap | — | — | ✔ | TCK 235 ceza aralığı.  |
| 39 | **cevap** | cevap | cevap | — | — | ✔ | TMK 425.  |
| 40 | **cevap** | cevap | cevap | — | — | ✔ | TCK 184 metni.  |
| 41 | **cevap** | cevap | cevap | — | — | ✔ | İİK 31.  |
| 42 | **ÇEKİNME** | ÇEKİNME | ÇEKİNME | `bulunmuyor` | — | ✘ | Kaynak-yokluğu + `bu kaynaklar sorunuzla doğrudan ilgili değildir`.  |
| 43 | **cevap** | cevap | cevap | — | — | ✔ | CMK 174 iade koşulları.  |
| 44 | **cevap** | cevap | ÇEKİNME | — | — | ✔ | Tetikleyici `içermemektedir` eleme gerekçesinde; hüküm TMK 72 ile verilmiş.  |
| 45 | **ÇEKİNME** | ÇEKİNME | ÇEKİNME | `bulunmuyor` | `içermemektedir` | ✔ | Kaynak-yokluğu + KAYNAK 4'ün neden yetmediği; hüküm yok.  |
| 46 | **cevap** | cevap | cevap | — | — | ✔ | `zorunlu değildir` (KMK 14) — olumsuzlama HUKUKUN içeriği.  |
| 47 | **cevap** | cevap | cevap | — | — | ✔ | TCK 91; iki-beş yıl.  |
| 48 | **cevap** | cevap | cevap | — | — | ✔ | TKHK 35; bir yıl.  |
| 49 | **cevap** | cevap | cevap | — | — | ✔ | TKHK 52; bedel ödenmez.  |
| 50 | **cevap** | cevap | cevap | — | — | ✔ | TBK 414 metni.  |
| 51 | **cevap** | cevap | cevap | — | — | ✘ | TCK 43 fıkrası.  |
| 52 | **cevap** | cevap | cevap | — | — | ✔ | CMK 101 alıntısı + merci açıklaması.  |
| 53 | **cevap** | cevap | ÇEKİNME | — | — | ✔ | Tetikleyici eleme gerekçesinde; hüküm CMK 12 ile verilmiş.  |
| 54 | **ÇEKİNME** | ÇEKİNME | ÇEKİNME | `bulunmuyor` | `bulunmuyor` | ✔ | Tek cümlelik kaynak-yokluğu beyanı.  |
| 55 | **cevap** | cevap | cevap | — | — | ✔ | İİK 171.  |
| 56 | **ÇEKİNME** | ÇEKİNME | ÇEKİNME | `bulunmuyor` | `bulunmuyor` | ✔ | Tek cümlelik kaynak-yokluğu beyanı.  |
| 57 | **cevap** | cevap | cevap | — | — | ✔ | ⚠️ BOZUK ÇIKTI: aynı eleme paragrafı 6 kez tekrarlanıp kırpılmış. KAYNAK 1'in konuyu düzenlediği söyleniyor; RED yok, ama esaslı hüküm de yok.  |
| 58 | **cevap** | cevap | cevap | — | — | ✘ | 6136 s.K. 9 metni.  |
| 59 | **cevap** | cevap | cevap | — | — | ✔ | TKHK 56.  |
| 60 | **cevap** | cevap | cevap | — | — | ✔ | HMK 342.  |
| 61 | **ÇEKİNME** | ÇEKİNME | ÇEKİNME | `bulunmamaktadır` | — | ✘ | Kaynak-yokluğu + `sunulan kaynaklar bu konuya doğrudan değinmemektedir`.  |
| 62 | **cevap** | cevap | cevap | — | — | ✔ | KMK 22; kanuni ipotek.  |
| 63 | **cevap** | cevap | cevap | — | — | ✔ | İş K. 66; `Evet …`.  |
| 64 | **cevap** | cevap | cevap | — | — | ✔ | HMK 364 metni + özet.  |
| 65 | **cevap** | cevap | ÇEKİNME | — | — | ✔ | Tetikleyici eleme gerekçesinde; hüküm HMK 303 alıntısıyla verilmiş.  |
| 66 | **ÇEKİNME** | ÇEKİNME | ÇEKİNME | `bulunmuyor` | `içermemektedir` | ✔ | Kaynak-yokluğu + KAYNAK 7'nin neden yetmediği.  |
| 67 | **cevap** | cevap | cevap | — | — | ✔ | TKHK 66.  |
| 68 | **cevap** | cevap | cevap | — | — | ✔ | ⚠️ ZAYIF: `KAYNAK 1 … açıkça belirtmektedir` + İİK 85 atfı; RED yok.  |
| 69 | **cevap** | cevap | cevap | — | — | ✔ | TMK 406 alıntısı.  |
| 70 | **cevap** | cevap | cevap | — | — | ✔ | İİK 85 metni.  |
| 71 | **cevap** | cevap | cevap | — | — | ✔ | HMK 124 alıntısı.  |
| 72 | **cevap** | cevap | cevap | — | — | ✔ | İş K. 30; %3 / %4 oranları.  |
| 73 | **cevap** | cevap | cevap | — | — | ✔ | 6284 s.K. 13; süreler.  |
| 74 | **cevap** | cevap | cevap | — | — | ✔ | İİK 79/a.  |
| 75 | **cevap** | cevap | cevap | — | — | ✔ | HMK 315.  |
| 76 | **cevap** | cevap | cevap | — | — | ✔ | İİK 97/a metni.  |
| 77 | **cevap** | cevap | ÇEKİNME | — | — | ✔ | Tetikleyici eleme gerekçesinde; hüküm TCK 102 ile verilmiş.  |
| 78 | **cevap** | cevap | cevap | — | — | ✔ | İİK 85.  |
| 79 | **cevap** | cevap | cevap | — | — | ✔ | TCK 103 alıntısı.  |

## Not — sınır vakaları (çekinme SAYILMADI, ama cevap da sayılmayı zor hak ediyor)

`id=31` · `id=68` yalnız "KAYNAK N bunu düzenlemektedir" + atıf veriyor, hükmün metnini
vermiyor. `id=36` · `id=57` üretim döngüsüne girip kırpılmış. Dördünde de **red yok**, bu
yüzden çekinme sayılmadılar — ama **B10'un değil, sadakat/kalite ekseninin** kalemleridir.

## Değişmeyen

`recall@k` · atıf dağılımı · K2 bedeli · hakem yargıları (`rejection_rate`, `faithfulness`)
bu okumadan **etkilenmez**; `exact_reject` yalnız *cevapladı mı / çekindi mi* ayrımını kurar.
