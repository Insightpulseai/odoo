#!/usr/bin/env python3
# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""Mark the TBWA\\SMP company and enforce OMC user scoping — deterministically.

After this script runs successfully:
  - ir.config_parameter "ipai.company.tbwa_company_id" = <company id>
  - res.company.ipai_is_tbwa_smp = True  (on the marked company)
  - Every @omc.com user: company_id = TBWA, company_ids = [TBWA]
  - Every @omc.com user: in group ipai_company_scope_omc.group_omc_restricted

The config param is the primary source of truth — name matching is never
needed again once it is set.

Run INSIDE the Odoo container:

    docker cp scripts/company/mark_tbwa_smp_company.py odoo-prod:/tmp/
    docker exec odoo-prod python3 /tmp/mark_tbwa_smp_company.py

    # Prefer by ID (most deterministic — avoids name matching entirely):
    docker exec -e TBWA_COMPANY_ID=1 odoo-prod python3 /tmp/mark_tbwa_smp_company.py

    # Or by name:
    docker exec -e TBWA_COMPANY_NAME="TBWA SMP" odoo-prod python3 /tmp/mark_tbwa_smp_company.py

    # Dry-run (show what would change, no writes):
    docker exec -e DRY_RUN=1 odoo-prod python3 /tmp/mark_tbwa_smp_company.py

Exits:
    0 — All changes applied (or dry-run completed)
    1 — No company matched — manual intervention required
    2 — Unexpected error

Environment:
    ODOO_DB            — database name (default: odoo_prod)
    TBWA_COMPANY_ID    — preferred: exact res.company id to mark
    TBWA_COMPANY_NAME  — fallback: exact or ilike name match (default: "TBWA\\SMP")
    DRY_RUN            — set to "1" for dry-run (no writes)
    DB_PASSWORD        — override ${DB_PASSWORD} in odoo.conf

Resolution order (most to least deterministic):
    1. TBWA_COMPANY_ID env var (skip all name matching)
    2. ir.config_parameter ipai.company.tbwa_company_id (already set)
    3. TBWA_COMPANY_NAME exact match
    4. TBWA_COMPANY_NAME ilike match
    5. List all companies and exit 1 (user must re-run with correct ID)
"""

import json
import logging
import os
import sys
import time

_logger = logging.getLogger("mark_tbwa_smp")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

ODOO_DB = os.environ.get("ODOO_DB", "odoo_prod")
TBWA_COMPANY_ID = os.environ.get("TBWA_COMPANY_ID", "").strip()
TBWA_COMPANY_NAME = os.environ.get("TBWA_COMPANY_NAME", r"TBWA\SMP").strip()
DRY_RUN = os.environ.get("DRY_RUN", "0") == "1"
OMC_DOMAIN = "@omc.com"
PARAM_KEY = "ipai.company.tbwa_company_id"


def _resolve_company(env):
    """Resolve the TBWA company via TBWA_COMPANY_ID → param → name → list."""

    # Step 1: explicit ID from env
    if TBWA_COMPANY_ID:
        try:
            company = env["res.company"].sudo().browse(int(TBWA_COMPANY_ID))
            if company.exists():
                _logger.info("Resolved via TBWA_COMPANY_ID=%s: %r", TBWA_COMPANY_ID, company.name)
                return company
            _logger.error("TBWA_COMPANY_ID=%s does not exist.", TBWA_COMPANY_ID)
        except ValueError:
            _logger.error("TBWA_COMPANY_ID=%r is not a valid integer.", TBWA_COMPANY_ID)
        return None

    # Step 2: already-set config param
    icp = env["ir.config_parameter"].sudo()
    param_val = icp.get_param(PARAM_KEY)
    if param_val:
        try:
            company = env["res.company"].sudo().browse(int(param_val))
            if company.exists():
                _logger.info("Resolved via existing param %r=%s: %r", PARAM_KEY, param_val, company.name)
                return company
        except (ValueError, TypeError):
            pass
        _logger.warning("Existing param %r=%r is stale — re-resolving.", PARAM_KEY, param_val)

    # Step 3: exact name match
    company = env["res.company"].sudo().search([("name", "=", TBWA_COMPANY_NAME)], limit=1)
    if company:
        _logger.info("Resolved via exact name %r: id=%d", TBWA_COMPANY_NAME, company.id)
        return company

    # Step 4: ilike match
    company = env["res.company"].sudo().search([("name", "ilike", TBWA_COMPANY_NAME)], limit=1)
    if company:
        _logger.info(
            "Resolved via ilike name %r: id=%d name=%r (set TBWA_COMPANY_ID=%d to be explicit)",
            TBWA_COMPANY_NAME, company.id, company.name, company.id,
        )
        return company

    # Step 5: list all and exit
    all_companies = env["res.company"].sudo().search([], order="id")
    _logger.error(
        "No company matched. Available companies:\n%s\n"
        "Re-run with TBWA_COMPANY_ID=<id> or TBWA_COMPANY_NAME=<exact name>.",
        "\n".join(f"  id={c.id}  name={c.name!r}" for c in all_companies),
    )
    return None


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

            # ── Resolve company ────────────────────────────────────────────
            company = _resolve_company(env)
            if not company:
                return 1

            _logger.info(
                "Target: id=%d  name=%r  ipai_is_tbwa_smp=%s",
                company.id, company.name, company.ipai_is_tbwa_smp,
            )

            icp = env["ir.config_parameter"].sudo()

            if DRY_RUN:
                _logger.info("[DRY_RUN] Would set:")
                _logger.info("  %r = %d", PARAM_KEY, company.id)
                if not company.ipai_is_tbwa_smp:
                    _logger.info("  company.ipai_is_tbwa_smp = True")
            else:
                # Set config param (primary source of truth)
                icp.set_param(PARAM_KEY, str(company.id))
                _logger.info("✅ Set ir.config_parameter %r = %d", PARAM_KEY, company.id)

                # Set flag
                if not company.ipai_is_tbwa_smp:
                    company.sudo().write({"ipai_is_tbwa_smp": True})
                    _logger.info("✅ Set ipai_is_tbwa_smp=True on company id=%d", company.id)

            # ── Locate OMC restricted group ────────────────────────────────
            group_xmlid = "ipai_company_scope_omc.group_omc_restricted"
            try:
                omc_group = env.ref(group_xmlid)
                _logger.info("OMC restricted group: id=%d", omc_group.id)
            except Exception:
                _logger.warning(
                    "Group %r not found — module may not be installed. Skipping group assignment.",
                    group_xmlid,
                )
                omc_group = None

            # ── Locate @omc.com users ──────────────────────────────────────
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
                    "in_omc_group": bool(omc_group and omc_group in user.groups_id),
                }

                if DRY_RUN:
                    _logger.info("[DRY_RUN] Would enforce scope for user %r", user.login)
                    results.append({**before, "action": "dry_run"})
                    continue

                # Add to OMC restricted group
                if omc_group and omc_group not in user.groups_id:
                    user.sudo().write({"groups_id": [(4, omc_group.id)]})

                # Enforce company scope
                user.sudo().write({
                    "company_id": company.id,
                    "company_ids": [(6, 0, [company.id])],
                })
                user.invalidate_recordset()

                after = {
                    "company_id": user.company_id.name,
                    "company_ids": user.company_ids.mapped("name"),
                    "in_omc_group": bool(omc_group and omc_group in user.groups_id),
                }
                _logger.info(
                    "✅ User %r — company_ids: %r → %r  group: %s → %s",
                    user.login,
                    before["company_ids"], after["company_ids"],
                    before["in_omc_group"], after["in_omc_group"],
                )
                results.append({"login": user.login, "before": before, "after": after})

            if not DRY_RUN:
                cr.commit()
                _logger.info("Changes committed.")

            summary = {
                "status": "DRY_RUN" if DRY_RUN else "COMPLETE",
                "tbwa_company": {"id": company.id, "name": company.name},
                "param_set": not DRY_RUN,
                "param_key": PARAM_KEY,
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
