#!/bin/bash
# Apply macOS support patches to DeepFaceLive repo.
# Run from /Applications/face-live or pass path to DeepFaceLive as first argument.

set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FACE_LIVE="$(cd "$SCRIPT_DIR/.." && pwd)"
DFL="${1:-$FACE_LIVE/DeepFaceLive}"

if [[ ! -d "$DFL" ]]; then
  echo "DeepFaceLive not found at: $DFL"
  echo "Clone or extract the repo first (see README_MAC.md)."
  exit 1
fi

echo "Applying macOS patches to: $DFL"

CAMERA_SOURCE="$DFL/apps/DeepFaceLive/backend/CameraSource.py"
if [[ -f "$CAMERA_SOURCE" ]]; then
  python3 "$SCRIPT_DIR/apply_camera_patch.py" "$CAMERA_SOURCE"
else
  echo "  Skipping CameraSource.py (file not found)."
fi

echo "Done. Run: python main.py run DeepFaceLive --no-cuda"
