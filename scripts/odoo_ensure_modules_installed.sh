#!/usr/bin/env bash
# ===========================================================================
# Odoo Ensure Modules Installed Script
# Reads desired modules from SSOT config and installs missing ones
# ===========================================================================
set -euo pipefail

# Configuration (override via environment)
ODOO_CONTAINER="${ODOO_CONTAINER:-odoo-core}"
ODOO_DB="${ODOO_DB:-odoo_core}"
ODOO_CONF="${ODOO_CONF:-/etc/odoo/odoo.conf}"
DESIRED_FILE="${DESIRED_FILE:-config/odoo/desired_modules.yml}"

# Logging
log() { echo "[odoo-ensure] $(date '+%Y-%m-%d %H:%M:%S') $*"; }

log "Ensuring desired modules are installed..."
log "Container: ${ODOO_CONTAINER}"
log "Database: ${ODOO_DB}"
log "Config file: ${DESIRED_FILE}"

# Verify config file exists
if [[ ! -f "${DESIRED_FILE}" ]]; then
    log "WARNING: Desired modules file not found: ${DESIRED_FILE}"
    log "Skipping module installation check"
    exit 0
fi

# Verify container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${ODOO_CONTAINER}$"; then
    log "ERROR: Container ${ODOO_CONTAINER} is not running"
    exit 1
fi

# Run Python script to ensure modules are installed
python3 - <<'PY'
import os
import subprocess
import sys

try:
    import yaml
except ImportError:
    print("[odoo-ensure] Installing PyYAML...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "pyyaml"])
    import yaml

desired_file = os.environ.get("DESIRED_FILE", "config/odoo/desired_modules.yml")
container = os.environ.get("ODOO_CONTAINER", "odoo-core")
db = os.environ.get("ODOO_DB", "odoo_core")
conf = os.environ.get("ODOO_CONF", "/etc/odoo/odoo.conf")

# Load desired modules
with open(desired_file, "r", encoding="utf-8") as f:
    doc = yaml.safe_load(f) or {}

mods = doc.get("modules") or []
mods = [m.strip() for m in mods if m and m.strip() and not m.strip().startswith("#")]

if not mods:
    print("[odoo-ensure] No desired modules listed; exiting.")
    sys.exit(0)

print(f"[odoo-ensure] Checking {len(mods)} desired modules...")

# Build Odoo shell script to install missing modules
odoo_py = f"""
modules = {repr(mods)}
installed = []
not_found = []
already_installed = []

for name in modules:
    m = env['ir.module.module'].search([('name', '=', name)], limit=1)
    if not m:
        not_found.append(name)
        print(f"[WARNING] Module not found in addons path: {{name}}")
        continue
    if m.state in ('installed', 'to upgrade'):
        already_installed.append(name)
        print(f"[OK] Already installed: {{name}}")
    else:
        print(f"[INSTALL] Installing: {{name}} (state={{m.state}})")
        try:
            m.button_immediate_install()
            installed.append(name)
            print(f"[OK] Installed: {{name}}")
        except Exception as e:
            print(f"[ERROR] Failed to install {{name}}: {{e}}")

print()
print(f"[SUMMARY] Already installed: {{len(already_installed)}}, Newly installed: {{len(installed)}}, Not found: {{len(not_found)}}")
if not_found:
    print(f"[WARNING] Modules not in addons path: {{not_found}}")
"""

cmd = [
    "docker", "exec", "-i", container,
    "odoo", "-d", db, "-c", conf,
    "--no-http", "--stop-after-init",
    "--shell"
]

print(f"[odoo-ensure] Executing Odoo shell...")
p = subprocess.run(cmd, input=odoo_py.encode(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
print(p.stdout.decode(errors="replace"))
sys.exit(p.returncode)
PY

log "Done."
