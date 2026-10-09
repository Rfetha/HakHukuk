"""Künye kabuk-ayrıştırma testleri — tuzak 1.12 (`cp0_thinking_gen.sh`).

⚠️ NEDEN VAR: künyeye elle yazılmış bir alan künyeyi KANIT olmaktan çıkarır. 2026-09-11'de
ısırdı: `echo` satırı `KV q8_0/q8_0` diye sabit dize basıyordu, koşu fp16 KV ile yapılmıştı ve
kıyasın ölçmek için var olduğu tek değişken künyede YANLIŞ görünüyordu (yürütme tuzağı 1.12).

Bu testler llama-server ÇAĞIRMAZ: betiğin KV bloğu ile sunucu komutu metinden ayıklanıp sahte
değişkenlerle koşturulur. Sunucu komutu, onarımdan ÖNCEKİ argüman dizisine karşı sınanır —
yani "davranış değişmedi" iddiası bir çıpaya bağlıdır, göze değil.
"""
import os
import re
import subprocess

BETIK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "scripts", "olcum_uretim", "cp0_thinking_gen.sh")
METIN = open(BETIK, encoding="utf-8").read()

# Onarımdan ÖNCEKİ (2026-09-11) sunucu argümanları — davranış çıpası. Bu dizi değişirse
# koşunun kendisi değişmiştir; test o zaman DÜŞMELİ, "güncellenmemeli".
CIPA_ARGV = ("-m /tmp/sahte.gguf -ngl 99 -fa on --no-context-shift "
             "--cache-type-k q8_0 --cache-type-v q8_0 -c 8192 "
             "--host 127.0.0.1 --port 8080")


def _kv_blogu() -> str:
    m = re.search(r"^# --- KV kimliği.*?^# --- /KV kimliği.*?$", METIN, re.S | re.M)
    assert m, "KV bloğu işaretçileri kayboldu — test ile betik ayrıştı"
    return m.group(0)


def _sunucu_komutu() -> str:
    m = re.search(r'^\s*"\$BIN" -m "\$GGUF".*?2>&1 &$', METIN, re.S | re.M)
    assert m, "sunucu komutu bulunamadı — test ile betik ayrıştı"
    return m.group(0)


def _kabuk(govde: str, ortam: str = "") -> str:
    r = subprocess.run(["bash", "-uo", "pipefail", "-c", f"{ortam}\n{govde}"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def test_kunye_satiri_sabit_kv_dizesi_tasimiyor():
    satir = next(s for s in METIN.splitlines() if s.startswith('echo "  sunucu'))
    assert "q8_0" not in satir and "fp16" not in satir, f"künye sabit KV dizesi taşıyor: {satir}"
    assert "$KV_KUNYE" in satir


def test_kv_kunyesi_dis_sunucuda_bilinmiyor_yazar():
    cikti = _kabuk(_kv_blogu() + '\necho "$KV_KUNYE"', 'SERVER_URL="http://10.0.0.5:9000/v1"')
    assert cikti == "BİLİNMİYOR (dış sunucu)"


def test_kv_kunyesi_kendi_sunucusunda_bayrak_degiskenlerinden_turer():
    cikti = _kabuk(_kv_blogu() + '\necho "$KV_KUNYE"; echo "$KV_K/$KV_V"', 'SERVER_URL=""')
    kunye, bayraklar = cikti.splitlines()
    assert kunye == bayraklar, "künye, bayrak değişkenlerinden türemiyor"


def test_sunucu_komutu_kv_bayraklarini_kunyeyle_ayni_degiskenden_alir():
    assert '--cache-type-k "$KV_K" --cache-type-v "$KV_V"' in _sunucu_komutu()


def test_sunucu_argumanlari_onarimdan_once_ile_birebir_ayni(tmp_path):
    stub = tmp_path / "sahte-llama-server"
    stub.write_text('#!/usr/bin/env bash\necho "$@"\n')
    stub.chmod(0o755)
    ortam = "\n".join([
        f'BIN="{stub}"', 'GGUF="/tmp/sahte.gguf"', 'NGL="99"', 'CTX="8192"', 'PORT="8080"',
        'SERVER_EXTRA=""', f'LOG="{tmp_path}/srv.log"', 'SERVER_URL=""',
    ])
    _kabuk(_kv_blogu() + "\n" + _sunucu_komutu() + "\nwait", ortam)
    assert (tmp_path / "srv.log").read_text().strip() == CIPA_ARGV


def test_betik_sozdizimi_gecerli():
    assert subprocess.run(["bash", "-n", BETIK], capture_output=True).returncode == 0
