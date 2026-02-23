#!/usr/bin/env bash
# Train using only elonmusk.png (SRC and DST). Run from project root.
set -e
ROOT="/Applications/face-live"
VENV_PY="${ROOT}/DeepFaceLab_venv/bin/python3.9"
WORKSPACE="${ROOT}/workspace"

if [[ ! -f "${VENV_PY}" ]]; then
  echo "DeepFaceLab_venv not found. Create it and install deps first (see TRAINING.md)."
  exit 1
fi

# Ensure elonmusk.png is the only image used for both SRC and DST
SRC_IMG="${WORKSPACE}/src_images/elonmusk.png"
DST_DIR="${WORKSPACE}/dst_images"
if [[ -f "${SRC_IMG}" ]]; then
  cp -f "${SRC_IMG}" "${DST_DIR}/elonmusk.png"
  echo "Using elonmusk.png for both SRC and DST."
fi

cd "${ROOT}"

echo "[1/4] Extracting SRC faces from workspace/src_images..."
"${VENV_PY}" run.py --extract-src --input-dir workspace/src_images

echo "[2/4] Extracting DST faces from workspace/dst_images..."
"${VENV_PY}" run.py --extract-dst --input-dir workspace/dst_images

echo "[3/4] Sorting faces..."
"${VENV_PY}" run.py --sort-faces

echo "[4/4] Training (Model_Quick96, CPU)..."
"${VENV_PY}" run.py --train --quick

echo "Done. Export for DeepFaceLive: ${VENV_PY} run.py --train --export-only"
