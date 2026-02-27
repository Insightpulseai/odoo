#!/usr/bin/env python3
# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""Verify OMC user company scope is correctly enforced.

Run INSIDE the Odoo container:

    docker cp scripts/company/verify_omc_scope.py odoo-prod:/tmp/
    docker exec odoo-prod python3 /tmp/verify_omc_scope.py

Exits:
    0 — All @omc.com users correctly scoped; record rule confirmed
    1 — One or more users have incorrect scope (check output)
    2 — Unexpected error / module not installed

Checks performed (for each @omc.com user):
    1. company_id == TBWA\\SMP (ipai_is_tbwa_smp=True)
    2. company_ids == [TBWA\\SMP] only
    3. User is in group ipai_company_scope_omc.group_omc_restricted
    4. res.company non-sudo search (as that user) returns only TBWA\\SMP
"""

import json
import logging
import os
import sys
import time

_logger = logging.getLogger("verify_omc_scope")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

ODOO_DB = os.environ.get("ODOO_DB", "odoo_prod")
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

    failures = []

    try:
        with registry.cursor() as cr:
            env = api.Environment(cr, 1, {})  # admin context for setup checks

            # ── Check module is installed ──────────────────────────────────
            try:
                tbwa = env["res.company"].sudo().search(
                    [("ipai_is_tbwa_smp", "=", True)], limit=1
                )
            except Exception as exc:
                _logger.error(
                    "ipai_is_tbwa_smp field not found — is ipai_company_scope_omc installed? %s", exc
                )
                return 2

            if not tbwa:
                _logger.error(
                    "No company has ipai_is_tbwa_smp=True. "
                    "Run scripts/company/mark_tbwa_smp_company.py first."
                )
                return 1

            _logger.info("TBWA\\SMP company: id=%d name=%r", tbwa.id, tbwa.name)

            # ── Get OMC restricted group ───────────────────────────────────
            try:
                omc_group = env.ref("ipai_company_scope_omc.group_omc_restricted")
            except Exception:
                _logger.warning("group_omc_restricted not found — skipping group membership check.")
                omc_group = None

            # ── Check each @omc.com user ───────────────────────────────────
            omc_users = env["res.users"].sudo().search(
                [("login", "=ilike", f"%{OMC_DOMAIN}")]
            )
            _logger.info("Checking %d @omc.com user(s)...", len(omc_users))

            user_results = []
            for user in omc_users:
                checks = {}

                # Check 1: company_id
                checks["company_id_ok"] = user.company_id.id == tbwa.id
                # Check 2: company_ids
                checks["company_ids_ok"] = set(user.company_ids.ids) == {tbwa.id}
                # Check 3: group membership
                checks["in_omc_group"] = (
                    omc_group is not None and omc_group in user.groups_id
                )
                # Check 4: non-sudo res.company search as this user
                user_env = env(user=user.id)
                visible_companies = user_env["res.company"].search([])
                checks["record_rule_ok"] = (
                    len(visible_companies) == 1
                    and visible_companies[0].id == tbwa.id
                )

                ok = all(v is True for v in checks.values())
                status = "✅ OK" if ok else "❌ FAIL"

                details = {
                    "login": user.login,
                    "status": "ok" if ok else "fail",
                    "company_id": user.company_id.name,
                    "company_ids": user.company_ids.mapped("name"),
                    "visible_companies_count": len(visible_companies),
                    "checks": checks,
                }
                user_results.append(details)

                _logger.info(
                    "%s user=%r company_id=%r company_ids=%r visible=%d in_group=%s",
                    status, user.login,
                    user.company_id.name,
                    user.company_ids.mapped("name"),
                    len(visible_companies),
                    checks.get("in_omc_group"),
                )

                if not ok:
                    failures.append(details)

            # ── Summary ────────────────────────────────────────────────────
            overall = "PASS" if not failures else "FAIL"
            summary = {
                "status": overall,
                "tbwa_company": {"id": tbwa.id, "name": tbwa.name},
                "omc_users_checked": len(omc_users),
                "failures": len(failures),
                "users": user_results,
                "stamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            print(json.dumps(summary, indent=2), flush=True)

            if failures:
                _logger.error(
                    "❌ %d user(s) have incorrect OMC scope. "
                    "Run scripts/company/mark_tbwa_smp_company.py to fix.",
                    len(failures),
                )
                return 1

            _logger.info("✅ All @omc.com users are correctly scoped to TBWA\\SMP.")
            return 0

    except Exception as exc:
        _logger.exception("Unexpected error: %s", exc)
        return 2


if __name__ == "__main__":
    sys.exit(main())
