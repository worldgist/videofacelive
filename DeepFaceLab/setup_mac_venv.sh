#!/usr/bin/env bash
# DeepFaceLab macOS venv setup (Python 3.9).
# Run in Terminal. If "brew install python@3.9" fails with permission errors, run first:
#   sudo chown -R $(whoami) /Users/$(whoami)/Library/Logs/Homebrew /usr/local/Cellar /usr/local/Frameworks /usr/local/Homebrew /usr/local/bin /usr/local/etc /usr/local/include /usr/local/lib /usr/local/opt /usr/local/sbin /usr/local/share /usr/local/var/homebrew
# Then run this script again.

set -e
PY39="$(brew --prefix python@3.9 2>/dev/null)/bin/python3.9"
if [[ ! -x "$PY39" ]]; then
  echo "Installing Python 3.9..."
  brew install python@3.9
  PY39="$(brew --prefix python@3.9)/bin/python3.9"
fi
echo "Using: $PY39"
"$PY39" -m venv /Applications/face-live/DeepFaceLab_venv
source /Applications/face-live/DeepFaceLab_venv/bin/activate
cd /Applications/face-live/DeepFaceLab
pip install --upgrade pip
pip install -r requirements-mac.txt
echo "Done. Activate with: source /Applications/face-live/DeepFaceLab_venv/bin/activate"
echo "Then run DeepFaceLab with --cpu-only as in README_MAC.md"
