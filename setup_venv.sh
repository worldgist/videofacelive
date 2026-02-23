#!/bin/bash
# Use Python 3.12 for this project (PyTorch has no macOS wheels for 3.14)
set -e
cd "$(dirname "$0")"

echo "Installing Python 3.12 via Homebrew (if needed)..."
brew install python@3.12

PY312=$(brew --prefix python@3.12)/bin/python3.12
echo "Creating venv with $PY312..."
rm -rf .venv
"$PY312" -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "Done. Activate with: source .venv/bin/activate"
