#!/usr/bin/env bash
# Copy exported .dfm from DeepFaceLab workspace/model to workspace/dfm_models
# so DeepFaceLive can load them. Run after: python main.py exportdfm --model-dir workspace/model --model Model_SAEHD
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC="${SCRIPT_DIR}/model"
DST="${SCRIPT_DIR}/dfm_models"
if [[ ! -d "$SRC" ]]; then
  echo "No workspace/model dir. Train and export a model first (see DeepFaceLab/TRAIN_MAC.md)."
  exit 1
fi
mkdir -p "$DST"
count=0
for f in "$SRC"/*.dfm; do
  [[ -e "$f" ]] || continue
  cp -v "$f" "$DST/"
  ((count++)) || true
done
if [[ $count -eq 0 ]]; then
  echo "No .dfm files in $SRC. Run: python main.py exportdfm --model-dir $SRC --model Model_SAEHD"
  exit 1
fi
echo "Copied $count .dfm file(s) to $DST. Run DeepFaceLive: DeepFaceLive_macOS/run_deepfacelive_mac.sh"
