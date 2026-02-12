#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DC="${ROOT}/.devcontainer/devcontainer.json"
SSOT="../sandbox/dev/compose.yml"

test -f "$DC" || { echo "ERROR: missing $DC" >&2; exit 1; }

python3 - <<PY
import json, sys
p="${DC}"
ssot="${SSOT}"
d=json.load(open(p,"r",encoding="utf-8"))
files=d.get("dockerComposeFile") or []
if isinstance(files, str): files=[files]
if ssot not in files:
  print(f"ERROR: devcontainer.json must reference SSOT compose: {ssot}")
  print("dockerComposeFile =", files)
  sys.exit(1)
print("devcontainer SSOT: OK")
PY
