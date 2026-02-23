#!/usr/bin/env bash
# Set up git and connect to https://github.com/worldgist/videofacelive.git
# Run from project root: bash scripts/git_setup_and_push.sh
set -e
cd "$(dirname "$0")/.."
REMOTE="https://github.com/worldgist/videofacelive.git"

if [[ ! -d .git ]]; then
  git init
  echo "Git initialized."
fi

git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE"
echo "Remote 'origin' set to $REMOTE"

echo ""
echo "Next steps (run these yourself):"
echo "  1. git add ."
echo "  2. git status   # review what will be committed"
echo "  3. git commit -m \"Initial commit\""
echo "  4. git branch -M main   # if you want main as default branch"
echo "  5. git push -u origin main"
