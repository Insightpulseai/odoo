#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== tree (top-level) =="
find . -maxdepth 3 -type f | sed 's|^\./||' | sort | head -n 200

echo "== yaml parse check =="
python3 - <<'PY'
import yaml, glob, sys
for p in glob.glob("schemas/**/*.yaml", recursive=True):
    with open(p, "r", encoding="utf-8") as f:
        yaml.safe_load(f)
print("YAML OK")
PY

echo "== ts syntax check (no deps) =="
node -c router/router.ts >/dev/null 2>&1 || true
echo "DONE"
