"""Orijinal bf16 ağırlıkların Modal hacmine yüklenmesi: dosya seçimi, sha256 manifesti, fark raporu."""
import hashlib

import pytest

import bf16_yukle as by  # noqa: E402


def _klasor(tmp_path):
    (tmp_path / "model-00001.safetensors").write_bytes(b"a" * 10)
    (tmp_path / "model-00002.safetensors").write_bytes(b"b" * 20)
    (tmp_path / "model.safetensors.index.json").write_text("{}")
    (tmp_path / "config.json").write_text("{}")
    (tmp_path / "LICENSE").write_text("x")
    (tmp_path / "README.md").write_text("x")
    return str(tmp_path)


def test_dosyalar_yalniz_agirlik_yapilandirma_ve_tokenizer_dosyalarini_secer(tmp_path):
    assert by.dosyalar(_klasor(tmp_path)) == [
        "config.json", "model-00001.safetensors", "model-00002.safetensors", "model.safetensors.index.json"]


def test_safetensors_yoksa_durur(tmp_path):
    (tmp_path / "config.json").write_text("{}")
    with pytest.raises(SystemExit, match="safetensors"):
        by.dosyalar(str(tmp_path))


def test_manifest_bayt_ve_sha256_icerir(tmp_path):
    m = by.manifest(_klasor(tmp_path))
    assert m["dosyalar"]["model-00001.safetensors"] == {"bayt": 10, "sha256": hashlib.sha256(b"a" * 10).hexdigest()}


def test_farklar_ayni_klasorde_bos_degisen_ve_eksik_dosyada_dolu(tmp_path):
    k = _klasor(tmp_path)
    beklenen = by.manifest(k)
    assert by.farklar(beklenen, by.manifest(k)) == []
    (tmp_path / "model-00002.safetensors").write_bytes(b"c" * 20)          # aynı boyut, farklı içerik
    f = by.farklar(beklenen, by.manifest(k))
    assert len(f) == 1 and "model-00002.safetensors" in f[0] and "sha256" in f[0]
    (tmp_path / "config.json").unlink()
    f = by.farklar(beklenen, by.manifest(k, adlar=list(beklenen["dosyalar"])))
    assert any("config.json" in x and "eksik" in x for x in f)


def test_put_komutlari_her_dosya_icin_modal_volume_put_uretir(tmp_path):
    komutlar = by.put_komutlari(_klasor(tmp_path))
    assert len(komutlar) == 4
    assert komutlar[0][:4] == ["modal", "volume", "put", "hukuk-outputs"]
    assert komutlar[0][-1] == "/f016-vllm-pilot/bf16/config.json"
