#!/usr/bin/env bash
# Build aristotle-lean.plugin from the repo root.
# Produces ./aristotle-lean.plugin (a zip of .claude-plugin/ + skills/ + README.md + LICENSE).
set -euo pipefail

cd "$(dirname "$0")"

NAME="$(python3 -c "import json; print(json.load(open('.claude-plugin/plugin.json'))['name'])")"
OUT="${NAME}.plugin"

rm -f "$OUT"
zip -r "$OUT" \
  .claude-plugin \
  mcp \
  skills \
  README.md \
  LICENSE \
  -x "*.DS_Store" "*.plugin" "build-plugin.*"

echo "Built: $OUT"
