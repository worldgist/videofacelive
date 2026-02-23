#!/usr/bin/env bash
# Run DeepFaceLab pipeline: extract (workspace/src_images, workspace/dst_images) -> sort -> optional train -> export.
# Usage:
#   ./run_pipeline.sh              # extract + sort only
#   ./run_pipeline.sh train        # extract + sort + train
#   ./run_pipeline.sh train export # extract + sort + train + export
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [[ -d ".venv" ]]; then
  source .venv/bin/activate
elif [[ -d "DeepFaceLab_venv" ]]; then
  source DeepFaceLab_venv/bin/activate
fi

if [[ "$1" == "train" && "$2" == "export" ]]; then
  python run.py --pipeline --train --export-only
elif [[ "$1" == "train" ]]; then
  python run.py --pipeline --train
else
  python run.py --pipeline
  echo ""
  echo "Put SRC images in workspace/src_images and DST images in workspace/dst_images if not done."
  echo "Then run:  ./run_pipeline.sh train"
  echo "When training is done:  python run.py --train --export-only"
fi
