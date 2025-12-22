#!/usr/bin/env bash
# Generate repo snapshot JSON for audit evidence
set -euo pipefail

OUT="${1:-docs/REPO_SNAPSHOT.json}"
mkdir -p "$(dirname "$OUT")"

python3 - <<'PY' > "$OUT"
import json
import os
import subprocess
from datetime import datetime

def sh(cmd):
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""

data = {
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "git": {
        "sha": sh(["git", "rev-parse", "HEAD"]),
        "branch": sh(["git", "branch", "--show-current"]),
        "dirty": bool(sh(["git", "status", "--porcelain"])),
        "remotes": sh(["git", "remote", "-v"]).split("\n") if sh(["git", "remote", "-v"]) else [],
    },
    "submodules": sh(["git", "submodule", "status", "--recursive"]),
    "env": {
        "ODOO_RC": os.getenv("ODOO_RC", ""),
        "ODOO_ADDONS_PATH": os.getenv("ODOO_ADDONS_PATH", ""),
    },
    "python_version": sh(["python3", "--version"]),
    "addons": sorted([d for d in os.listdir("addons") if os.path.isdir(f"addons/{d}") and not d.startswith(".")]) if os.path.isdir("addons") else [],
}
print(json.dumps(data, indent=2))
PY

echo "Wrote $OUT"
