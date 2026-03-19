#!/usr/bin/env bash
set -euo pipefail

DIR="templates/vendor/powerbi-desktop-samples/Sample Reports"
test -d "$DIR" || { echo "missing: $DIR" >&2; exit 1; }

# List PBIX/PBIT/JSON-ish assets (whatever exists in that folder)
find "$DIR" -maxdepth 2 -type f \( -iname "*.pbix" -o -iname "*.pbit" -o -iname "*.json" -o -iname "*.png" -o -iname "*.md" \) -print | sort
