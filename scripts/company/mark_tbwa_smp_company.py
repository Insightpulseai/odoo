#!/usr/bin/env python3
# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""Mark the TBWA\\SMP company and enforce OMC user scoping.

Run INSIDE the Odoo container:

    docker cp scripts/company/mark_tbwa_smp_company.py odoo-prod:/tmp/
    docker exec odoo-prod python3 /tmp/mark_tbwa_smp_company.py

    # Dry-run (show what would change, no writes):
    docker exec -e DRY_RUN=1 odoo-prod python3 /tmp/mark_tbwa_smp_company.py

    # Specify company by name:
    docker exec -e TBWA_COMPANY_NAME="TBWA SMP" odoo-prod python3 /tmp/mark_tbwa_smp_company.py

Exits:
    0 — All changes applied (or dry-run completed)
    1 — No company matched — manual intervention required
    2 — Unexpected error

Environment:
    ODOO_DB            — database name (default: odoo_prod)
    TBWA_COMPANY_NAME  — exact company name to mark (default: "TBWA\\SMP")
    DRY_RUN            — set to "1" for dry-run (no writes)
    DB_PASSWORD        — override ${DB_PASSWORD} in odoo.conf

Actions:
    1. Find company by TBWA_COMPANY_NAME; set ipai_is_tbwa_smp=True
    2. Find all users with login ending @omc.com
    3. For each OMC user: add to group_omc_restricted
    4. For each OMC user: enforce company_id/company_ids = [TBWA\\SMP]
    5. Emit structured summary
"""

import json
import logging
import os
import sys
import time

_logger = logging.getLogger("mark_tbwa_smp")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

ODOO_DB = os.environ.get("ODOO_DB", "odoo_prod")
TBWA_COMPANY_NAME = os.environ.get("TBWA_COMPANY_NAME", r"TBWA\SMP")
DRY_RUN = os.environ.get("DRY_RUN", "0") == "1"
OMC_DOMAIN = "@omc.com"


def main():
    try:
        import odoo.tools.config
        db_password = os.environ.get("DB_PASSWORD", "")
        parse_args = ["--config=/etc/odoo/odoo.conf"]
        if db_password:
            parse_args.append(f"--db_password={db_password}")
        odoo.tools.config.parse_config(parse_args)
        from odoo.modules.registry import Registry
        from odoo import api
        registry = Registry(ODOO_DB)
    except Exception as exc:
        _logger.error("Failed to initialise Odoo registry: %s", exc)
        return 2

    try:
        with registry.cursor() as cr:
            env = api.Environment(cr, 1, {})

            # ── Step 1: Locate TBWA\SMP company ───────────────────────────
            company = env["res.company"].sudo().search(
                [("name", "=", TBWA_COMPANY_NAME)], limit=1
            )
            if not company:
                # Try case-insensitive ilike as fallback
                company = env["res.company"].sudo().search(
                    [("name", "ilike", TBWA_COMPANY_NAME)], limit=1
                )
            if not company:
                companies = env["res.company"].sudo().search([], order="id")
                _logger.error(
                    "No company named %r found. Available companies: %s",
                    TBWA_COMPANY_NAME,
                    [f"{c.id}:{c.name}" for c in companies],
                )
                _logger.error(
                    "Set TBWA_COMPANY_NAME env var to one of the names above and re-run."
                )
                return 1

            _logger.info(
                "Found company id=%d name=%r  ipai_is_tbwa_smp=%s",
                company.id, company.name, company.ipai_is_tbwa_smp,
            )

            if not company.ipai_is_tbwa_smp:
                if DRY_RUN:
                    _logger.info("[DRY_RUN] Would set ipai_is_tbwa_smp=True on company id=%d", company.id)
                else:
                    company.sudo().write({"ipai_is_tbwa_smp": True})
                    _logger.info("✅ Set ipai_is_tbwa_smp=True on company id=%d", company.id)
            else:
                _logger.info("Company already marked ipai_is_tbwa_smp=True — no change needed.")

            # ── Step 2: Locate OMC restricted group ───────────────────────
            group_xmlid = "ipai_company_scope_omc.group_omc_restricted"
            try:
                omc_group = env.ref(group_xmlid)
                _logger.info("OMC restricted group: id=%d", omc_group.id)
            except Exception:
                _logger.warning(
                    "Group %r not found — module may not be installed yet. "
                    "Skipping group assignment.",
                    group_xmlid,
                )
                omc_group = None

            # ── Step 3: Locate @omc.com users ─────────────────────────────
            omc_users = env["res.users"].sudo().search(
                [("login", "=ilike", f"%{OMC_DOMAIN}")]
            )
            _logger.info("Found %d @omc.com user(s).", len(omc_users))

            results = []
            for user in omc_users:
                before = {
                    "login": user.login,
                    "company_id": user.company_id.name,
                    "company_ids": user.company_ids.mapped("name"),
                    "in_omc_group": omc_group and omc_group in user.groups_id,
                }

                if DRY_RUN:
                    _logger.info("[DRY_RUN] Would enforce scope for user %r", user.login)
                    results.append({**before, "action": "dry_run"})
                    continue

                # Add to OMC restricted group
                if omc_group and omc_group not in user.groups_id:
                    user.sudo().write({"groups_id": [(4, omc_group.id)]})

                # Enforce company_id/company_ids
                user.sudo().write({
                    "company_id": company.id,
                    "company_ids": [(6, 0, [company.id])],
                })
                user.invalidate_recordset()

                after = {
                    "company_id": user.company_id.name,
                    "company_ids": user.company_ids.mapped("name"),
                    "in_omc_group": omc_group and omc_group in user.groups_id,
                }
                _logger.info(
                    "✅ User %r — company: %r → %r  in_omc_group: %s → %s",
                    user.login,
                    before["company_ids"], after["company_ids"],
                    before["in_omc_group"], after["in_omc_group"],
                )
                results.append({
                    "login": user.login,
                    "before": before,
                    "after": after,
                })

            if not DRY_RUN:
                cr.commit()
                _logger.info("Changes committed.")

            # ── Emit summary ───────────────────────────────────────────────
            summary = {
                "status": "DRY_RUN" if DRY_RUN else "COMPLETE",
                "tbwa_company": {"id": company.id, "name": company.name},
                "omc_users_found": len(omc_users),
                "users": results,
                "stamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            print(json.dumps(summary, indent=2), flush=True)
            return 0

    except Exception as exc:
        _logger.exception("Unexpected error: %s", exc)
        return 2


if __name__ == "__main__":
    sys.exit(main())
