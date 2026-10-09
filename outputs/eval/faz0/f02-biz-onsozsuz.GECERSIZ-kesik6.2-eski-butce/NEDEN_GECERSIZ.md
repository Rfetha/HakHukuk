# 🚫 GEÇERSİZ KOŞU — saklanıyor, çünkü ADR-0070'in kanıtı bu

**Tarih:** 2026-09-06 · **etiket:** `h1_tgta_v1_f02_nb` · **rejim:** v2 soru · `RRF_K=10` · önsözsüz

**Neden geçersiz:** kesik-cevap **5/80 = %6,2 > %5** (ADR-0040 geçerlilik ön şartı).
Script kapıyı uyguladı ve **hakem parası harcanmadan** durdu (`EXIT=2`).

**Kesikliğin sebebi bulundu ve kesiklik yalnız BELİRTİYDİ:** 5 kesikten **4'ü tam 1024
token'da** ve `forced_close=False` — yani cevap payını hiç almadan. Bizim kol
`max_tokens=think_budget=1024` alıyordu, rakip **1536**. → [ADR-0070](../../../docs/adr/0070-uretim-butcesi-esitlendi.md)

**Bu klasör SİLİNMEZ:** ADR-0070'in dayandığı ölçüm burada (`completion_tokens` tavanının
zorla kapatılmayan kalemlerde tam 1024'te durduğu). Yeni koşu `f02-biz-onsozsuz/` altında.
