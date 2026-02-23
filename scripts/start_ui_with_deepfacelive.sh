#!/usr/bin/env bash
# Start the call UI with DeepFaceLive (face swap) in the background.
# From project root: bash scripts/start_ui_with_deepfacelive.sh
cd "$(dirname "$0")/.."
python3 run.py --ui --with-deepfacelive
