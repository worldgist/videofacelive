#!/usr/bin/env bash
# After initial commit: pull remote changes (e.g. README) and push.
# Run from project root: bash scripts/git_pull_and_push.sh
set -e
cd "$(dirname "$0")/.."

echo "Pulling remote main (merge, allow unrelated histories)..."
git pull origin main --allow-unrelated-histories --no-rebase --no-edit

echo ""
echo "Pushing to origin main..."
git push -u origin main

echo "Done."
