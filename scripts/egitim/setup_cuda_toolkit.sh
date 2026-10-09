#!/usr/bin/env bash
# CUDA toolkit'i sudo'suz kur (NVIDIA resmî redistributable tarball'ları).
# Gerekçe: pip'teki nvidia-cuda-nvcc-cuXX yalnız ptxas içeriyor, nvcc YOK;
# sistemde CUDA toolkit kurulu değil; Linux için hazır llama.cpp CUDA binary'si yok.
# GPU (RTX 5070 Ti, sm_120) ve sürücü zaten çalışıyor — eksik olan sadece DERLEYİCİ.
#
# ⚠️ SÜRÜM BİR PARAMETREDİR (2026-07-24, ADR-0026 ruhu).
# Sebep somut: `causal-conv1d` derlemesi *toolkit 12.9 ↔ torch cu130* uyuşmazlığından düştü
# (`CUDA_MISMATCH_MESSAGE`). CUDA uzantısı derleyen her paket, torch'un derlendiği CUDA
# ana sürümünü ister. Torch sürümü değişince toolkit de değişmeli — o yüzden gömülü değil.
#
# Kullanım:
#   bash scripts/egitim/setup_cuda_toolkit.sh              # torch'un CUDA sürümünü otomatik seçer
#   bash scripts/egitim/setup_cuda_toolkit.sh 13.0.2       # açık sürüm (redist manifest sürümü)
#   CUDA_ROOT=~/code/cuda-13.0 bash scripts/egitim/setup_cuda_toolkit.sh 13.0.2
#
# Farklı sürümler AYRI dizinlere kurulur ve birbirini ezmez — llama.cpp'nin build'i
# 12.9'a rpath'lenmiş durumda, onu bozmamak şart.
set -euo pipefail

BASE="https://developer.download.nvidia.com/compute/cuda/redist"
VER="${1:-}"

# ── sürüm belirle ────────────────────────────────────────────────────────────
if [ -z "$VER" ]; then
  TORCH_CUDA=$(python -c "import torch;print(torch.version.cuda or '')" 2>/dev/null || true)
  [ -n "$TORCH_CUDA" ] || { echo "❌ torch bulunamadı; sürümü argüman olarak ver (ör. 13.0.2)"; exit 1; }
  echo "### torch.version.cuda = $TORCH_CUDA → uyumlu redist manifesti aranıyor"
  for patch in 2 1 0 3 4; do
    cand="${TORCH_CUDA}.${patch}"
    if curl -sfI "$BASE/redistrib_${cand}.json" >/dev/null 2>&1; then VER="$cand"; break; fi
  done
  [ -n "$VER" ] || { echo "❌ $TORCH_CUDA için redist manifesti bulunamadı"; exit 1; }
fi

MAJMIN="${VER%.*}"
CUDA_ROOT="${CUDA_ROOT:-$HOME/code/cuda-$MAJMIN}"
echo "### CUDA $VER → $CUDA_ROOT"

# ── torch ile ana sürüm uyumu (sessiz uyuşmazlık = saatler sonra derleme hatası) ──
TORCH_CUDA=$(python -c "import torch;print(torch.version.cuda or '')" 2>/dev/null || true)
if [ -n "$TORCH_CUDA" ] && [ "${TORCH_CUDA%%.*}" != "${VER%%.*}" ]; then
  echo "⚠️  UYARI: torch CUDA $TORCH_CUDA ↔ toolkit $VER — ANA SÜRÜMLER FARKLI."
  echo "    CUDA uzantısı derleyen paketler (causal-conv1d, flash-attn…) bu farkta DÜŞER."
fi

TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
curl -sfL "$BASE/redistrib_${VER}.json" -o "$TMP/manifest.json" \
  || { echo "❌ manifest indirilemedi: redistrib_${VER}.json"; exit 1; }

# cuda_crt / libnvptxcompiler: CUDA 13'te AYRI paketler (12.x'te cuda_nvcc'nin içindeydiler).
# cuda_crt olmadan `crt/host_config.h` bulunamaz ve HER nvcc derlemesi düşer.
# Manifestte olmayan ad ölümcül değil — sürümler arası paket bölünmesi normal.
# libnvvm de CUDA 13'te ayrıldı; içinde nvvm/bin/cicc var — o olmadan nvcc "cicc: not found" der.
PKGS="cuda_nvcc cuda_crt libnvvm cuda_cudart libcublas cuda_cccl cuda_nvrtc libnvptxcompiler"
REQUIRED="cuda_nvcc cuda_cudart"
mkdir -p "$CUDA_ROOT"
for name in $PKGS; do
  rel=$(python - "$TMP/manifest.json" "$name" <<'PY'
import json,sys
d=json.load(open(sys.argv[1])).get(sys.argv[2]) or {}
print((d.get("linux-x86_64") or {}).get("relative_path",""))
PY
)
  if [ -z "$rel" ]; then
    case " $REQUIRED " in *" $name "*) echo "❌ zorunlu paket manifestte yok: $name"; exit 1;; esac
    echo "### $name — bu sürümün manifestinde yok, atlanıyor"; continue
  fi
  echo "### $name ← $(basename "$rel")"
  curl -sL "$BASE/$rel" -o "$TMP/$name.tar.xz"
  tar -xf "$TMP/$name.tar.xz" -C "$TMP"
  d=$(find "$TMP" -maxdepth 1 -type d -name "${name}-linux*" | head -1)
  cp -rn "$d"/* "$CUDA_ROOT/" 2>/dev/null || true
done

# Redistributable tarball'lar kütüphaneleri lib/ altına koyar, nvcc ise lib64/ arar.
ln -sfn "$CUDA_ROOT/lib" "$CUDA_ROOT/lib64"

echo "### doğrulama — gerçek derleme+link testi (sm_120)"
"$CUDA_ROOT/bin/nvcc" --version | tail -2
T=$(mktemp -d)
echo '__global__ void k(){} int main(){return 0;}' > "$T/t.cu"
"$CUDA_ROOT/bin/nvcc" -arch=sm_120 "$T/t.cu" -o "$T/t.out"
[ -x "$T/t.out" ] && echo "✅ nvcc derleme+link OK" || { echo "❌ link başarısız"; exit 1; }
rm -rf "$T"
echo "CUDA_ROOT=$CUDA_ROOT"
echo "Kullanım: export CUDA_HOME=$CUDA_ROOT; export PATH=\$CUDA_HOME/bin:\$PATH"
