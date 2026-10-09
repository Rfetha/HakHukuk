# Görev 22 · Adım 4 — ürün yolunda iki geçişli zorunlu düşünce kapatması

**Öncesi** (çıpa): `outputs/eval/g18-arac-katmani/aracsiz_yol_80.json` — 2026-09-09, tek geçiş, bütçe TEK havuz (1536).
**Sonrası**: `outputs/eval/g22-rejim/aracsiz_yol_80_zorunlu_kapatma.json` — 2026-09-11, iki geçişli zorunlu kapatma.
Aynı 80 DEV kalemi (`data/eval/dev/core_hard.jsonl`), aynı sunucu yapılandırması (q8_0 KV), aynı tohum 3407.

⛔ **Kütle (faithful-answer mass) HESAPLANMADI** — hakem ister, bu işin bütçesi $0. Yayımlanan 0,8011 ölçüm hattının sayısıdır ve bu koşuyla DEĞİŞMEZ.

## 1. Kapı sayıları

| ölçüt | öncesi | sonrası | kapı | hüküm |
| :--- | ---: | ---: | :--- | :--- |
| tamamen boş metin | 4/80 | **0/80** | hedef 0/80 | GEÇTİ |
| kesik (`Durum.KESIK`) | 7/80 (%8.75) | **3/80 (%3.75)** | ADR-0040 · %5 ⇒ ≤4/80 | GEÇTİ |

- boş kalem kimlikleri — öncesi `[7, 64, 65, 66]` · sonrası `[]`
- kesik kalem kimlikleri — öncesi `[7, 11, 30, 64, 65, 66, 68]` · sonrası `[11, 30, 68]`
  - kesiklikten ÇIKAN: `[7, 64, 65, 66]` · kesikliğe GİREN: `[]`

## 2. Suskunluk kümesi — ⛔ fark GİZLENMEZ

- öncesi: `[10, 34, 63]` (3 kalem)
- sonrası: `[7, 10, 34, 63, 64]` (5 kalem)
- **GİREN** (yeni suskunluk): `[7, 64]`
- **ÇIKAN** (artık suskun değil): `[]`

| id | öncesi durum | sonrası durum | yön |
| ---: | :--- | :--- | :--- |
| 7 | KESIK | SUSKUNLUK | GİRDİ |
| 64 | KESIK | SUSKUNLUK | GİRDİ |

## 3. Durum sınıfı dağılımı

| durum | öncesi | sonrası | fark |
| :--- | ---: | ---: | ---: |
| CEKINCELI | 1 | 1 | +0 |
| CEVAP | 69 | 71 | +2 |
| KESIK | 7 | 3 | -4 |
| SUSKUNLUK | 3 | 5 | +2 |

## 4. Kalem kalem durum değişimi

Durum sınıfı değişen kalem: **4/80**

| id | öncesi | sonrası |
| ---: | :--- | :--- |
| 7 | KESIK | SUSKUNLUK |
| 64 | KESIK | SUSKUNLUK |
| 65 | KESIK | CEVAP |
| 66 | KESIK | CEVAP |

## 5. Metin değişimi (`sha256`)

- `sha256` olarak **değişen kalem: 4/80**
- birebir aynı kalan: 76/80
- değişen kimlikler: `[7, 64, 65, 66]`

| cevap uzunluğu (karakter) | öncesi | sonrası |
| :--- | ---: | ---: |
| ortalama | 786.4 | 798.9 |
| ortanca | 720.5 | 725.0 |
| en kısa | 0 | 58 |
| en uzun | 3291 | 3291 |
| toplam | 62.911 | 63.909 |

## 6. Kaynak kümesi muhafızı

Getirilen kaynak kümesi değişen kalem: **0/80** — retriever'a DOKUNULMADI, değişmemesi beklenir. ✅ sıfır.

## 7. Atıf muhafızı (uydurma madde kapısı)

- öncesi: 171 atıf, 10 doğrulanamayan
- sonrası: 173 atıf, 10 doğrulanamayan

