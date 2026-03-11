#!/usr/bin/env python3
"""
odoo_verify_modules.py - Verify modules are installed in Odoo

Usage:
    ODOO_MODULES=ipai_workos_core,ipai_finance_ppm ./scripts/run_odoo_shell.sh scripts/odoo_verify_modules.py

Environment Variables:
    ODOO_MODULES - Comma-separated list of modules to verify (required)

Exit Codes:
    0 - All modules installed/upgradable
    2 - Missing or bad state modules found
"""

import os
import sys

# Get modules from environment
mods = os.getenv("ODOO_MODULES", "")
wanted = [m.strip() for m in mods.split(",") if m.strip()]

print("=" * 60)
print("Odoo Module Verification")
print("=" * 60)

if not wanted:
    print("\nERROR: No modules specified")
    print("Set ODOO_MODULES environment variable")
    sys.exit(1)

print(f"\nModules to verify: {', '.join(wanted)}")

Module = env["ir.module.module"].sudo()
rows = Module.search([("name", "in", wanted)])
found = {r.name: r.state for r in rows}

missing = [m for m in wanted if m not in found]
bad = {m: s for m, s in found.items() if s not in ("installed", "to upgrade")}

print("\n" + "-" * 40)
print("Results:")
print("-" * 40)

for mod in wanted:
    if mod in missing:
        status = "❌ MISSING"
    elif mod in bad:
        status = f"⚠️  {found[mod].upper()}"
    else:
        status = f"✅ {found[mod]}"
    print(f"  {mod}: {status}")

print("\n" + "-" * 40)
print("Summary:")
print("-" * 40)
print(f"  Found: {len(found)}/{len(wanted)}")
print(f"  Missing: {len(missing)}")
print(f"  Bad state: {len(bad)}")

if missing:
    print(f"\n⚠️  Missing modules: {', '.join(missing)}")

if bad:
    print(f"\n⚠️  Bad state modules: {bad}")

if missing or bad:
    print("\n❌ VERIFICATION FAILED")
    sys.exit(2)

print("\n✅ OK: All modules present and installed/upgradable")
