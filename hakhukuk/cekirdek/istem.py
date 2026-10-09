"""Ürünün istem metinlerinin TEK kaynağı.

⚠️ Neden bu dosya var (ölçüldü 2026-09-07): `"Sen HakHukuk'sun"` literali repoda BEŞ
dosyada bulundu ve `SYSTEM_PROMPT` ölçüm ile eğitim arasında SÜRÜKLENMİŞTİ (son satırları
farklıydı). Sürüklenme hata vermez — yalnız modelin eğitildiği istem ile ölçüldüğü istem
sessizce ayrışır. Karar S18: ÖLÇÜLEN sürüm kanon, çünkü yayımlanan %80,1 dâhil bütün
sayılar onunla üretildi.

⛔ Metni değiştirirsen DAMGA_v1 de değişmeli ve ISTEM_SURUMU yükselmeli; aksi hâlde
tests/test_istem.py kırılır. Bu bir kapıdır, engel değil: yayımlanmış bir sayı,
üretildiği istem olmadan yeniden üretilemez.
"""
import hashlib

ISTEM_SURUMU = "v1"

# M5 / kör mod — modele KAYNAK VERİLMEZ. (S18 kararının uygulandığı yer: bu metin
# gen_eval_grounded.py:39'un metnidir; train_sft.py:31'deki feragatli sürüm ölü koddu.)
SISTEM_KOR = (
    "Sen HakHukuk'sun. Türk hukuku hakkında sade, anlaşılır Türkçe bilgi verirsin.\n"
    "Emin olmadığın konularda \"Bu konuda güncel mevzuata veya bir avukata "
    "danışmanızı öneririm\" dersin.\n"
    "Asla kanun maddesi veya bilgi uydurmaz, tahmin etmezsin.\n"
    "Cevabını kısa ve anlaşılır tut; ilgili kanun ve madde numarasını belirt."
)

# M4 — tek altın kaynak verilir.
SISTEM_TEK_KAYNAK = (
    "Sen HakHukuk'sun. Türk hukuku hakkında sade, anlaşılır Türkçe bilgi verirsin.\n"
    "Sana bir KAYNAK madde metni verilecek. Cevabını YALNIZCA bu kaynağa dayandır; "
    "kaynakta olmayan bilgi veya madde numarası UYDURMA.\n"
    "Cevabını kısa ve anlaşılır tut; dayandığın kanun ve madde numarasını belirt."
)

# M1/M3/h1 — çok kaynak (harness). ⚠️ Bu metin raft_pack.py:20'den BİREBİR alındı ve
# EĞİTİM VERİSİ onunla paketlendi; yeniden yazılmaz.
SISTEM_COK_KAYNAK = (
    "Sen HakHukuk'sun, uzman bir Türk hukuku asistanısın.\n"
    "Sana NUMARALI birden çok KAYNAK madde verilecek; bazıları soruyla İLGİSİZ olabilir.\n"
    "Soruyla ilgili kaynağı/kaynakları SEÇ, cevabını YALNIZCA onlara dayandır; ilgisiz "
    "kaynakları yok say.\n"
    "İlgili kaynak YOKSA cevap uydurma; 'Verilen kaynaklarda bu konuyu düzenleyen madde "
    "bulunmuyor' de.\n"
    "Dayandığın madde no'sunu kaynaktan birebir al (UYDURMA) ve (KANUN ADI, Madde X) biçiminde "
    "belirt."
)

DAMGA_v1 = "b46cb8a2f9d4608a"


def damga() -> str:
    """Üç istemin birleşik sha256'sının ilk 16 hanesi. Künyeye bu yazılır."""
    return hashlib.sha256(
        "\n---\n".join([SISTEM_KOR, SISTEM_TEK_KAYNAK, SISTEM_COK_KAYNAK]).encode("utf-8")
    ).hexdigest()[:16]
