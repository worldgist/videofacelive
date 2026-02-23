#!/usr/bin/env bash
# DeepFaceLab training on macOS (CPU). Edit paths below, then:
#   source DeepFaceLab_venv/bin/activate
#   cd /Applications/face-live/DeepFaceLab
#   ./run_train_mac.sh

set -e
WORKSPACE="${WORKSPACE:-/Applications/face-live/workspace}"
SRC_FACES="${WORKSPACE}/src_faces"
DST_FACES="${WORKSPACE}/dst_faces"
MODEL_DIR="${WORKSPACE}/model"
MODEL_NAME="${MODEL_NAME:-Model_SAEHD}"   # or Model_Quick96 for faster

echo "Workspace: $WORKSPACE"
echo "Model: $MODEL_NAME"
echo "SRC faces: $SRC_FACES"
echo "DST faces: $DST_FACES"
echo "Model dir: $MODEL_DIR"

if [[ ! -d "$SRC_FACES" || ! -d "$DST_FACES" ]]; then
  echo "Create SRC and DST face dirs first (see TRAIN_MAC.md):"
  echo "  python main.py extract --input-dir <src_images> --output-dir $SRC_FACES --detector s3fd --cpu-only"
  echo "  python main.py extract --input-dir <dst_frames> --output-dir $DST_FACES --detector s3fd --cpu-only"
  exit 1
fi

python main.py train \
  --training-data-src-dir "$SRC_FACES" \
  --training-data-dst-dir "$DST_FACES" \
  --model-dir "$MODEL_DIR" \
  --model "$MODEL_NAME" \
  --cpu-only
