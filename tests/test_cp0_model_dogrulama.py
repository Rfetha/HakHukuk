"""cp0_thinking_gen.sh model kimliği doğrulama testleri — tuzak 7.8.

⚠️ NEDEN VAR: 2026-09-12'de sağlık kontrolü BAŞKASININ sunucusunu (konteynerin llama-server'ı,
aynı $PORT'ta) kendi sunucusu sandı — 8 kalem YANLIŞ MODELE karşı üretildi ve hiçbir yerde hata
vermedi. Port dinliyor olması kanıt değildir; hangi GGUF'un servis edildiği yalnız
`/v1/models`'tan okunup betiğin BAŞLATMAK İSTEDİĞİ GGUF ile karşılaştırılarak bilinebilir.

Bu testler llama-server ÇAĞIRMAZ ve ağa çıkmaz: betiğin doğrulama fonksiyonu metinden ayıklanıp
sahte bir `curl` (PATH'e eklenmiş) ile koşturulur.
"""
import os
import re
import subprocess

BETIK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "scripts", "olcum_uretim", "cp0_thinking_gen.sh")
METIN = open(BETIK, encoding="utf-8").read()


def _dogrulama_blogu() -> str:
    m = re.search(r"^# --- model kimliği doğrulama.*?^# --- /model kimliği doğrulama.*?$",
                  METIN, re.S | re.M)
    assert m, ("model kimliği doğrulama bloğu yok — tuzak 7.8'in korunması KODA yazılmamış "
               "(yalnız /health'e bakmak port dinliyor olmayı kanıt sayar)")
    return m.group(0)


def _sahte_curl(tmp_path, models_json: str, cikis_kodu: int = 0):
    kutu = tmp_path / "kutu"
    kutu.mkdir(exist_ok=True)
    curl = kutu / "curl"
    curl.write_text(
        "#!/usr/bin/env bash\n"
        f"cat <<'JSON'\n{models_json}\nJSON\n"
        f"exit {cikis_kodu}\n"
    )
    curl.chmod(0o755)
    return str(kutu)


def _kabuk(govde: str, ortam: str, path_onek: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", "-uo", "pipefail", "-c", f"{ortam}\n{govde}\ndogrula_model_kimligi"],
        capture_output=True, text=True,
        env={**os.environ, "PATH": f"{path_onek}:{os.environ['PATH']}"},
    )


def test_dogru_model_servis_edilirken_GECER(tmp_path):
    kutu = _sahte_curl(tmp_path, '{"data":[{"id":"tgta_v1-q4_k_m.gguf"}]}')
    r = _kabuk(_dogrulama_blogu(), 'GGUF="/artefakt/tgta_v1-q4_k_m.gguf"; SERVER_URL="http://127.0.0.1:8080/v1"; die(){ echo "❌ $*" >&2; exit 1; }', kutu)
    assert r.returncode == 0, r.stderr


def test_BASKASININ_SUNUCUSU_servis_edilirken_PATLAR(tmp_path):
    """Tuzak 7.8'in bire bir tekrarı: port dinliyor ama başka bir GGUF servis ediyor."""
    kutu = _sahte_curl(tmp_path, '{"data":[{"id":"HakHukuk-4B-v0.3-Q4_K_M.gguf"}]}')
    r = _kabuk(_dogrulama_blogu(), 'GGUF="/artefakt/tgta_v1-q4_k_m.gguf"; SERVER_URL="http://127.0.0.1:8080/v1"; die(){ echo "❌ $*" >&2; exit 1; }', kutu)
    assert r.returncode != 0
    assert "7.8" in r.stderr or "BAŞKA" in r.stderr


def test_v1_models_erisilemezse_PATLAR(tmp_path):
    kutu = _sahte_curl(tmp_path, "", cikis_kodu=1)
    r = _kabuk(_dogrulama_blogu(), 'GGUF="/artefakt/tgta_v1-q4_k_m.gguf"; SERVER_URL="http://127.0.0.1:8080/v1"; die(){ echo "❌ $*" >&2; exit 1; }', kutu)
    assert r.returncode != 0


def test_dogrulama_HER_IKI_dalda_da_CAGRILIYOR():
    """Fonksiyon tanımlı olmak yetmez — tuzak 6.12'nin sınıfı: çağrı zincirine girmeli."""
    cagri_sayisi = METIN.count("dogrula_model_kimligi\n") + METIN.count("dogrula_model_kimligi;")
    tanimdan_sonraki = METIN[METIN.index("dogrula_model_kimligi()"):]
    assert tanimdan_sonraki.count("dogrula_model_kimligi") >= 3, (
        "doğrulama fonksiyonu tanımlanmış ama iki dalın (var olan sunucu / yeni açılan sunucu) "
        "ikisinden de çağrılmıyor")


def test_betik_sozdizimi_gecerli():
    assert subprocess.run(["bash", "-n", BETIK], capture_output=True).returncode == 0
