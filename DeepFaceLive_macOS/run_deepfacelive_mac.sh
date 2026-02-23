#!/bin/bash
# Run DeepFaceLive on macOS (CPU only). Uses venv if present.
# Uses face-live/workspace as userdata so DFM models live in workspace/dfm_models/*.dfm
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DFL="${SCRIPT_DIR}/../DeepFaceLive"
VENV="${SCRIPT_DIR}/../DeepFaceLive_venv"
WORKSPACE="${SCRIPT_DIR}/../workspace"

if [[ ! -d "$DFL" ]]; then
  echo "DeepFaceLive not found at $DFL. See DeepFaceLive_macOS/README_MAC.md"
  exit 1
fi

if [[ -d "$VENV" ]]; then
  source "$VENV/bin/activate"
fi

mkdir -p "$WORKSPACE/dfm_models"

cd "$DFL"
python main.py run DeepFaceLive --no-cuda --userdata-dir "$WORKSPACE" "$@"
