#!/usr/bin/env bash
# llama.cpp'yi KALICI olarak kur + CUDA ile derle + GGUF üret.
#
# Neden kalıcı: scratchpad oturum-kapsamlı, temizleniyor (2026-07-24'te 22 GiB
# build+GGUF kaybedildi). Kurulum ~/code/llama.cpp, çıktılar models/gguf/ (gitignored).
#
# **Base-agnostik**: model gömülü DEĞİL, argümandan gelir.
#
# Kullanım:
#   bash scripts/egitim/setup_llamacpp.sh <hf-repo-id|yerel-dizin> [etiket]
#     <hf-repo-id>  ör. <org>/<model>          (HF cache'te indirilmiş olmalı)
#     <yerel-dizin> ör. models/merged/tg_v1    (merge_lora.py çıktısı — adaptör zinciri)
#     [etiket]      GGUF dosya adı öneki (varsayılan: yolun son parçası)
#
#   Sadece derleme (dönüştürme yok):
#     bash scripts/egitim/setup_llamacpp.sh
#
# Ayarlanabilir env:
#   QUANT=Q4_0       hedef quantization
#   PURE=1           token_embd YÜKSELTİLMEZ. ⚠️ Bu QAT-Q4_0 base'ler için doğrudur
#                    (ADR-0023). QAT OLMAYAN base'de PURE=0 kullan — yoksa embedding
#                    gereksiz yere kaybeder.
#   FIX_TOKENIZER=1  extra_special_tokens LİSTE→DICT yaması (Gemma 4 gibi tokenizer'lar
#                    için; transformers 4.x DICT bekler). Gerekmiyorsa 0.
#   KEEP_F16=1       ara f16 GGUF'u silme (varsayılan sil — 15-22 GiB)
set -euo pipefail

LC="$HOME/code/llama.cpp"
VENV="$HOME/code/llamacpp_venv"          # global_venv'den AYRI — onu asla kirletme
OUT="$(cd "$(dirname "$0")/.." && pwd)/models/gguf"
HUB="$HOME/.cache/huggingface/hub"

REPO="${1:-}"                             # ör. <org>/<model> ya da yerel dizin
# ⚠️ Mutlaklaştır: aşağıda `cd "$LC"` var, göreli yol oradan çözülmez.
[ -d "$REPO" ] && REPO="$(cd "$REPO" && pwd)"
TAG="${2:-}"
QUANT="${QUANT:-Q4_0}"
PURE="${PURE:-1}"
FIX_TOKENIZER="${FIX_TOKENIZER:-1}"
KEEP_F16="${KEEP_F16:-0}"

mkdir -p "$OUT"

# ── 1. izole venv ────────────────────────────────────────────────────────────
if [ ! -d "$VENV" ]; then
  echo "### izole venv kuruluyor (global_venv'e DOKUNULMAZ)"
  python3 -m venv "$VENV"
fi
"$VENV/bin/pip" install -q --upgrade pip cmake ninja 2>&1 | tail -1

# ── 2. llama.cpp ─────────────────────────────────────────────────────────────
if [ ! -d "$LC/.git" ]; then
  echo "### llama.cpp klonlanıyor → $LC"
  git clone --depth 1 https://github.com/ggml-org/llama.cpp.git "$LC" 2>&1 | tail -1
fi
cd "$LC" && echo "llama.cpp @ $(git log --oneline -1)"

# ── 3. CUDA derleme (sm_120 / Blackwell) ─────────────────────────────────────
CUDA_HOME="$HOME/code/cuda-12.9"
if [ ! -x "$LC/build-cuda/bin/llama-server" ]; then
  # nvcc: pip'teki nvidia-cuda-nvcc-cu12 YALNIZ ptxas içeriyor (nvcc yok), sistemde
  # CUDA toolkit kurulu değil, Linux için hazır llama.cpp CUDA binary'si de yok.
  # → NVIDIA resmî redistributable tarball'ları, sudo'suz (scripts/egitim/setup_cuda_toolkit.sh).
  [ -x "$CUDA_HOME/bin/nvcc" ] || bash "$(dirname "$0")/setup_cuda_toolkit.sh"
  NVCC="$CUDA_HOME/bin/nvcc"
  echo "nvcc: $("$NVCC" --version | tail -1)"
  echo "### CUDA build — sm_120 / Blackwell (uzun sürer)"
  # -L + -rpath ZORUNLU: libcudart/libcublas sistemde değil, sudo'suz tarball dizininde.
  # Olmadan link "undefined reference to cudaFree@libcudart.so.12" ile patlar (ld onları
  # bulamaz), rpath olmadan da çalışma anında "not found" gelir.
  LDF="-L$CUDA_HOME/lib -Wl,-rpath,$CUDA_HOME/lib"
  "$VENV/bin/cmake" -B build-cuda -DGGML_CUDA=ON -DCMAKE_BUILD_TYPE=Release \
      -DLLAMA_CURL=OFF -DCMAKE_CUDA_COMPILER="$NVCC" \
      -DCMAKE_CUDA_ARCHITECTURES=120 -DCUDAToolkit_ROOT="$CUDA_HOME" \
      -DCMAKE_EXE_LINKER_FLAGS="$LDF" -DCMAKE_SHARED_LINKER_FLAGS="$LDF" 2>&1 | tail -5
  "$VENV/bin/cmake" --build build-cuda --config Release -j "$(nproc)" \
      --target llama-server llama-cli llama-quantize 2>&1 | tail -5
fi
ls -la "$LC/build-cuda/bin/llama-server"

# ── 4. dönüştürme bağımlılıkları ─────────────────────────────────────────────
"$VENV/bin/pip" install -q -r "$LC/requirements/requirements-convert_hf_to_gguf.txt" 2>&1 | tail -1

# ── 5. tokenizer yaması + dönüştürme ─────────────────────────────────────────
# Bazı tokenizer_config'lerde `extra_special_tokens` LİSTE gelir; transformers 4.x DICT
# bekler → AttributeError. Snapshot'ı symlink'le kopyalayıp alanı düzelt (FIX_TOKENIZER=1).
prep() {
  local ref="$1" dst="$2"
  local snap
  if [ -d "$ref" ]; then                      # yerel HF dizini (ör. merge_lora.py çıktısı)
    snap="$ref/"
  else
    # `|| true`: ls başarısızlığı `set -e` ile mesajsız ölüme yol açıyordu.
    snap=$(ls -d "$HUB/models--${ref//\//--}"/snapshots/*/ 2>/dev/null | head -1 || true)
  fi
  [ -n "$snap" ] || { echo "❌ ne yerel dizin ne HF cache: $ref"; exit 1; }
  rm -rf "$dst"; mkdir -p "$dst"
  for f in "$snap"*; do ln -sf "$(readlink -f "$f")" "$dst/$(basename "$f")"; done
  if [ "$FIX_TOKENIZER" = "1" ]; then
    rm -f "$dst/tokenizer_config.json"
    "$VENV/bin/python" - "$snap" "$dst" <<'PY'
import json, sys
snap, dst = sys.argv[1], sys.argv[2]
d = json.load(open(f"{snap}/tokenizer_config.json"))
est = d.get("extra_special_tokens")
if isinstance(est, list):
    d["extra_special_tokens"] = {t.strip("<|>").replace("|", "_") + "_token": t for t in est}
    print("[prep] extra_special_tokens LİSTE→DICT yaması uygulandı")
json.dump(d, open(f"{dst}/tokenizer_config.json", "w"), ensure_ascii=False, indent=1)
PY
  fi
}

convert() {
  local repo="$1" tag="$2"
  local suffix; suffix="$(echo "$QUANT" | tr 'A-Z' 'a-z')"
  [ "$PURE" = "1" ] && suffix="$suffix-pure"
  local final="$OUT/$tag-$suffix.gguf"
  [ -f "$final" ] && { echo "### $(basename "$final") zaten var, atlanıyor"; return; }

  echo "### $tag: hazırlık + dönüştürme (quant=$QUANT pure=$PURE fix_tokenizer=$FIX_TOKENIZER)"
  prep "$repo" "/tmp/gguf-prep-$tag"
  cd "$LC"
  "$VENV/bin/python" convert_hf_to_gguf.py "/tmp/gguf-prep-$tag" \
      --outfile "$OUT/$tag-f16.gguf" --outtype f16 2>&1 | tail -6

  # --pure = token_embd YÜKSELTİLMEZ. QAT-Q4_0 base'ler için doğru (ADR-0023);
  # QAT olmayan base'de PURE=0 ver.
  local qargs=(); [ "$PURE" = "1" ] && qargs+=(--pure)
  "$LC/build-cuda/bin/llama-quantize" "${qargs[@]}" \
      "$OUT/$tag-f16.gguf" "$final" "$QUANT" 2>&1 | tail -4

  # ⚠️ Ara f16 15-22 GiB. Quantize YARIDA kesilirse (oturum sonu SIGTERM) çıktı bozuk
  # kalır — f16'yı silmeden önce hedefin makul boyutta olduğunu doğrula.
  local sz; sz=$(stat -c%s "$final" 2>/dev/null || echo 0)
  if [ "$sz" -lt 100000000 ]; then
    echo "❌ $final sadece $((sz/1024/1024)) MB — quantize yarıda kesilmiş. f16 KORUNUYOR."
    exit 1
  fi
  [ "$KEEP_F16" = "1" ] || rm -f "$OUT/$tag-f16.gguf"
  rm -rf "/tmp/gguf-prep-$tag"
}

if [ -n "$REPO" ]; then
  [ -n "$TAG" ] || TAG="$(basename "$REPO")"
  convert "$REPO" "$TAG"
else
  echo "### model verilmedi — sadece llama.cpp derlendi."
  echo "### Dönüştürmek için: bash $0 <hf-repo-id> [etiket]"
fi

echo
echo "### SONUÇ — $OUT"
ls -la "$OUT"/*.gguf 2>/dev/null | awk '{printf "%-40s %7.2f GiB\n", $9, $5/1073741824}'
