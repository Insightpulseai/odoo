#!/usr/bin/env python3
# Copyright 2026 InsightPulseAI
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""Verify OMC user company scope is correctly enforced.

Run INSIDE the Odoo container:

    docker cp scripts/company/verify_omc_scope.py odoo-prod:/tmp/
    docker exec odoo-prod python3 /tmp/verify_omc_scope.py

Exits:
    0 — All @omc.com users correctly scoped; config param present; record rule confirmed
    1 — One or more checks failed (see JSON output)
    2 — Unexpected error / module not installed

Checks performed:
    A. ir.config_parameter "ipai.company.tbwa_company_id" is set and valid
    B. Exactly one company has ipai_is_tbwa_smp=True
    For each @omc.com user:
    C. company_id == TBWA company
    D. company_ids == [TBWA company] only
    E. User is in group ipai_company_scope_omc.group_omc_restricted
    F. Non-sudo res.company search (as that user) returns only TBWA company
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
PARAM_KEY = "ipai.company.tbwa_company_id"


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
            env = api.Environment(cr, 1, {})

            # ── Check A: module field exists ───────────────────────────────
            try:
                _ = env["res.company"]._fields.get("ipai_is_tbwa_smp")
                if _ is None:
                    _logger.error(
                        "Field ipai_is_tbwa_smp not found on res.company. "
                        "Is ipai_company_scope_omc installed?"
                    )
                    return 2
            except Exception as exc:
                _logger.error("Module check failed: %s", exc)
                return 2

            # ── Check A: config param ──────────────────────────────────────
            icp = env["ir.config_parameter"].sudo()
            param_val = icp.get_param(PARAM_KEY)
            param_ok = False
            tbwa = None

            if param_val:
                try:
                    candidate = env["res.company"].sudo().browse(int(param_val))
                    if candidate.exists():
                        tbwa = candidate
                        param_ok = True
                        _logger.info("✅ Check A: %r = %d (%r)", PARAM_KEY, tbwa.id, tbwa.name)
                    else:
                        _logger.error("❌ Check A: %r = %r but company does not exist", PARAM_KEY, param_val)
                        failures.append({"check": "A_param", "detail": f"company id={param_val} missing"})
                except (ValueError, TypeError):
                    _logger.error("❌ Check A: %r = %r is not a valid integer", PARAM_KEY, param_val)
                    failures.append({"check": "A_param", "detail": f"invalid value {param_val!r}"})
            else:
                _logger.error(
                    "❌ Check A: ir.config_parameter %r not set. "
                    "Run scripts/company/mark_tbwa_smp_company.py.",
                    PARAM_KEY,
                )
                failures.append({"check": "A_param", "detail": "param not set"})

            # ── Check B: unique flag ───────────────────────────────────────
            flagged = env["res.company"].sudo().search([("ipai_is_tbwa_smp", "=", True)])
            if len(flagged) == 0:
                _logger.error("❌ Check B: No company has ipai_is_tbwa_smp=True.")
                failures.append({"check": "B_flag", "detail": "no company flagged"})
            elif len(flagged) > 1:
                _logger.warning(
                    "⚠️  Check B: %d companies have ipai_is_tbwa_smp=True: %s. "
                    "Only one should be marked.",
                    len(flagged), [f"id={c.id} name={c.name!r}" for c in flagged],
                )
                failures.append({"check": "B_flag", "detail": f"{len(flagged)} companies flagged"})
            else:
                _logger.info("✅ Check B: Exactly one company flagged: %r (id=%d)", flagged.name, flagged.id)
                if tbwa is None:
                    tbwa = flagged  # fall back if param wasn't set

            # If we still have no TBWA company, we can't check users
            if tbwa is None:
                _logger.error("Cannot resolve TBWA company — aborting user checks.")
                return _emit_result(failures, tbwa, 0)

            if param_ok and tbwa.id != flagged[:1].id:
                _logger.warning(
                    "⚠️  Config param points to id=%d but flagged company is id=%d. "
                    "Re-run mark_tbwa_smp_company.py.",
                    tbwa.id, flagged[0].id,
                )

            # ── OMC restricted group ───────────────────────────────────────
            try:
                omc_group = env.ref("ipai_company_scope_omc.group_omc_restricted")
                _logger.info("OMC restricted group: id=%d", omc_group.id)
            except Exception:
                omc_group = None
                _logger.warning("group_omc_restricted not found — skipping group checks.")

            # ── Per-user checks ────────────────────────────────────────────
            omc_users = env["res.users"].sudo().search(
                [("login", "=ilike", f"%{OMC_DOMAIN}")]
            )
            _logger.info("Checking %d @omc.com user(s)...", len(omc_users))

            user_results = []
            for user in omc_users:
                checks = {}

                # C: company_id
                checks["C_company_id"] = user.company_id.id == tbwa.id
                # D: company_ids
                checks["D_company_ids"] = set(user.company_ids.ids) == {tbwa.id}
                # E: group membership
                checks["E_group"] = (
                    omc_group is not None and omc_group in user.groups_id
                )
                # F: non-sudo res.company search as this user
                user_env = env(user=user.id)
                visible = user_env["res.company"].search([])
                checks["F_record_rule"] = (
                    len(visible) == 1 and visible[0].id == tbwa.id
                )

                ok = all(v is True for v in checks.values())
                icon = "✅" if ok else "❌"
                _logger.info(
                    "%s user=%r  company_id=%r  company_ids=%r  "
                    "visible_companies=%d  in_group=%s",
                    icon, user.login,
                    user.company_id.name,
                    user.company_ids.mapped("name"),
                    len(visible),
                    checks["E_group"],
                )

                detail = {
                    "login": user.login,
                    "status": "ok" if ok else "fail",
                    "company_id": user.company_id.name,
                    "company_ids": user.company_ids.mapped("name"),
                    "visible_companies": visible.mapped("name"),
                    "checks": checks,
                }
                user_results.append(detail)
                if not ok:
                    failures.append({"check": "user", "login": user.login, "checks": checks})

            return _emit_result(failures, tbwa, len(omc_users), user_results)

    except Exception as exc:
        _logger.exception("Unexpected error: %s", exc)
        return 2


def _emit_result(failures, tbwa, users_checked, user_results=None):
    overall = "PASS" if not failures else "FAIL"
    summary = {
        "status": overall,
        "tbwa_company": {"id": tbwa.id, "name": tbwa.name} if tbwa else None,
        "param_key": PARAM_KEY,
        "omc_users_checked": users_checked,
        "failures": len(failures),
        "failure_details": failures,
        "users": user_results or [],
        "stamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    print(json.dumps(summary, indent=2), flush=True)

    if failures:
        _logger.error(
            "❌ %d check(s) failed. Run scripts/company/mark_tbwa_smp_company.py to fix.",
            len(failures),
        )
        return 1

    _logger.info("✅ All checks passed — OMC users correctly scoped to %r.", tbwa.name if tbwa else "?")
    return 0


if __name__ == "__main__":
    sys.exit(main())
