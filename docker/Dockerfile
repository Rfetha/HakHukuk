# HakHukuk — `indir` ve `app` kutularının ORTAK imajı (ADR-0078: 3 kutu, 2 daemon, 2 imaj).
# Üçüncü bir Dockerfile YOKTUR: `indir` aynı imajı farklı komutla koşar. Ayırsaydık `sha256`
# kapısı iki entrypoint'e dağılırdı — kapı TEK yerde durur.
#
# ⚠️ Temel imaj PİNLİ (`latest` yasak): etiketsiz bir temel, aynı Dockerfile'dan başka bir
# ikili üretir ve fark hata vermeden görünür.
# ⛔ CUDA KATMANI YOK ve gerekmiyor: `app` CPU'dur (gömücü CPU'da koşar, indeks CPU RAM/disk —
# "sığar/sığmaz" farkı budur). GPU yalnız `llama` kutusundadır.
FROM python:3.11.16-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# ⚠️ torch ÖNCE ve CPU tekerleğinden: PyPI'nin varsayılan tekerleği CUDA taşır (~5 GB) ve
# bu kutuda ÖLÜ YÜKtür. `--extra-index-url pypi` torch'un kendi bağımlılıkları için gerekir.
RUN pip install \
      --index-url https://download.pytorch.org/whl/cpu \
      --extra-index-url https://pypi.org/simple \
      torch

COPY pyproject.toml README.md ./
COPY hakhukuk/ hakhukuk/
RUN pip install ".[api]"

# KARAR 5 (ADR-0078 madde 5) ve kusur 11: 2026-10-17'den beri ürün `scripts/`'e ihtiyaç duymaz
# (getirici, atıf doğrulama, madde kimliği ve red deseni `hakhukuk/cekirdek/`'te). `scripts/` kopyası
# imaj bir sonraki kez yeniden kurulup doğrulanınca kaldırılabilir; korpus repo köküne göreli okunur.
COPY scripts/ scripts/
COPY data/corpus/ data/corpus/

# Varsayılan komut `app` kutusunundur; `indir` kutusu compose'da kendi komutunu verir.
CMD ["python", "-m", "uvicorn", "hakhukuk.arayuz.api:uygulama", "--host", "0.0.0.0", "--port", "8000"]
