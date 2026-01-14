#!/usr/bin/env python3
"""
Canonical module audit generator.
Queries ir.module.module table and generates docs/deployment/MODULES_AUDIT.md
"""
import json
import os
import subprocess
from datetime import datetime, timezone

DB = os.environ.get("ODOO_DB", "odoo")
OUT = os.environ.get("OUT", "docs/deployment/MODULES_AUDIT.md")

def sh(cmd: str) -> str:
    return subprocess.check_output(cmd, shell=True, text=True)

def main():
    # Run inside odoo container or host where `odoo` binary is available.
    py = r"""
import json
mods = env['ir.module.module'].sudo()
installed = mods.search([('state','=','installed')])
names = sorted(installed.mapped('name'))
top = mods.search([('state','=','installed'),('auto_install','=',False)])
top_names = sorted(top.mapped('name'))
suspects = [m for m in names if any(k in m for k in ['iap','sms','mail_plugin','google','auth_oauth','payment_'])]
print(json.dumps({
  "installed_count": len(names),
  "top_level_count": len(top_names),
  "installed": names,
  "top_level": top_names,
  "suspects": sorted(set(suspects)),
}, indent=2))
"""
    payload = sh(f"odoo shell -d {DB} --no-http <<'PY'\n{py}\nPY")
    data = json.loads(payload)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    md = []
    md.append("# Production Installed Modules (Authoritative)")
    md.append("")
    md.append(f"**Generated**: {now}")
    md.append(f"**Database**: {DB}")
    md.append("**Source of Truth**: `ir.module.module` where `state = 'installed'`")
    md.append("")
    md.append("## Summary")
    md.append(f"- Installed modules: **{data['installed_count']}**")
    md.append(f"- Top-level modules (auto_install=false): **{data['top_level_count']}**")
    md.append("")
    md.append("## Policy: CE-Only with Optional IAP")
    md.append("")
    md.append("**Allowed**:")
    md.append("- `iap_*` modules installed but unused (no paid endpoints configured)")
    md.append("- `sms`, `*_sms` modules with external SMS provider (optional)")
    md.append("- `google_*`, `microsoft_account` OAuth integrations (optional)")
    md.append("- `mail_plugin`, `*_mail_plugin` external mail client integrations (optional)")
    md.append("")
    md.append("**Disallowed**:")
    md.append("- Any module requiring paid endpoints for core operations")
    md.append("- Any module with `web_enterprise` or `enterprise` dependencies")
    md.append("")
    md.append("**Enforcement**: CI drift gate fails if Enterprise dependencies detected.")
    md.append("")
    md.append("## Installed modules (all)")
    md.append("```json")
    md.append(json.dumps(data["installed"], indent=2))
    md.append("```")
    md.append("")
    md.append("## Top-level modules")
    md.append("```json")
    md.append(json.dumps(data["top_level"], indent=2))
    md.append("```")
    md.append("")
    md.append("## Suspects (review list)")
    md.append("")
    md.append("Modules requiring review for CE-only policy compliance:")
    md.append("")
    md.append("```json")
    md.append(json.dumps(data["suspects"], indent=2))
    md.append("```")
    md.append("")
    md.append("---")
    md.append("")
    md.append("**Regenerate**: `python3 scripts/audit_installed_modules.py`")
    md.append("")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print(f"✅ Wrote {OUT}")
    print(f"   Installed: {data['installed_count']}")
    print(f"   Top-level: {data['top_level_count']}")
    print(f"   Suspects: {len(data['suspects'])}")

if __name__ == "__main__":
    main()
