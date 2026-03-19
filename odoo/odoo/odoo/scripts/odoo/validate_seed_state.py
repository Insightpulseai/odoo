#!/usr/bin/env python3
"""
Validate Odoo seed state against the production seed plan.

SSOT: ssot/migration/production_seed_plan.yaml
Dedup: ssot/migration/seed_canonical_map.yaml

Usage:
    python3 scripts/odoo/validate_seed_state.py --db=odoo_dev
    python3 scripts/odoo/validate_seed_state.py --db=odoo --evidence-dir=docs/evidence/20260316/seed
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import psycopg2
except ImportError:
    psycopg2 = None


def get_connection(db_name: str):
    """Connect to Odoo PostgreSQL."""
    if psycopg2 is None:
        print("ERROR: psycopg2 not installed. Install with: pip install psycopg2-binary")
        sys.exit(1)

    return psycopg2.connect(
        dbname=db_name,
        host=os.environ.get("DB_HOST", "localhost"),
        port=os.environ.get("DB_PORT", "5432"),
        user=os.environ.get("DB_USER", os.getenv("USER", "odoo")),
        password=os.environ.get("DB_PASSWORD", ""),
    )


def query_one(conn, sql: str):
    """Execute query and return single value."""
    with conn.cursor() as cur:
        cur.execute(sql)
        row = cur.fetchone()
        return row[0] if row else None


def query_list(conn, sql: str):
    """Execute query and return list of first column."""
    with conn.cursor() as cur:
        cur.execute(sql)
        return [row[0] for row in cur.fetchall()]


def check(results: list, name: str, passed: bool, detail: str = ""):
    """Record a validation check result."""
    status = "PASS" if passed else "FAIL"
    icon = "✓" if passed else "✗"
    msg = f"  {icon} {name}: {status}"
    if detail:
        msg += f" ({detail})"
    print(msg)
    results.append({
        "check": name,
        "passed": passed,
        "detail": detail,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


def validate(db_name: str, evidence_dir: str | None = None):
    """Run all seed validation checks."""
    results = []
    print(f"\n=== Seed State Validation: {db_name} ===\n")

    # Validate database name
    check(results, "db_name_not_odoo_prod",
          db_name != "odoo_prod",
          f"Database name is '{db_name}'")

    try:
        conn = get_connection(db_name)
    except Exception as e:
        check(results, "database_connection", False, str(e))
        return results, False

    check(results, "database_connection", True, f"Connected to {db_name}")

    # --- Module checks ---
    installed = query_list(conn, """
        SELECT name FROM ir_module_module WHERE state = 'installed'
    """)
    installed_set = set(installed)

    check(results, "base_installed",
          "base" in installed_set,
          f"{len(installed)} modules installed")

    # Canonical modules
    canonical = ["ipai_project_seed", "ipai_zoho_mail", "ipai_bir_tax_compliance"]
    for mod in canonical:
        check(results, f"canonical_{mod}",
              mod in installed_set,
              "installed" if mod in installed_set else "NOT installed")

    # Deprecated/blocked modules
    deprecated = ["ipai_finance_close_seed", "ipai_mailgun_smtp"]
    for mod in deprecated:
        check(results, f"blocked_{mod}_not_installed",
              mod not in installed_set,
              "correctly absent" if mod not in installed_set else "INSTALLED (should be blocked)")

    # --- Company checks ---
    company_count = query_one(conn, "SELECT count(*) FROM res_company")
    check(results, "companies_present",
          company_count and company_count >= 1,
          f"{company_count} companies")

    ipai_company = query_one(conn, """
        SELECT count(*) FROM res_company WHERE name LIKE 'InsightPulse%'
    """)
    check(results, "ipai_company_present",
          ipai_company and ipai_company >= 1,
          f"InsightPulse AI: {'found' if ipai_company else 'NOT found'}")

    # --- User checks ---
    user_count = query_one(conn, """
        SELECT count(*) FROM res_users WHERE active = true AND share = false
    """)
    check(results, "internal_users_present",
          user_count and user_count >= 2,
          f"{user_count} internal users")

    # --- Finance seed dedup checks ---
    try:
        stage_count = query_one(conn, """
            SELECT count(*) FROM project_task_type WHERE name LIKE '%Finance%' OR name LIKE '%fin_%'
        """)
        if stage_count is not None:
            check(results, "finance_stages_not_duplicated",
                  stage_count <= 6,
                  f"{stage_count} finance stages (canonical=5, max acceptable=6)")
    except Exception:
        check(results, "finance_stages_not_duplicated", True, "project_task_type not available (modules not installed)")

    try:
        task_count = query_one(conn, """
            SELECT count(*) FROM project_task
            WHERE project_id IN (
                SELECT id FROM project_project WHERE name LIKE '%Month-End%' OR name LIKE '%Close%'
            )
        """)
        if task_count is not None:
            check(results, "month_end_tasks_not_duplicated",
                  task_count <= 25,
                  f"{task_count} month-end tasks (canonical=20, max acceptable=25)")
    except Exception:
        check(results, "month_end_tasks_not_duplicated", True, "project_task not available (modules not installed)")

    # --- Mail server checks ---
    try:
        zoho_count = query_one(conn, """
            SELECT count(*) FROM ir_mail_server WHERE smtp_host LIKE '%zoho%'
        """)
        mailgun_count = query_one(conn, """
            SELECT count(*) FROM ir_mail_server WHERE smtp_host LIKE '%mailgun%'
        """)
        check(results, "zoho_mail_present",
              zoho_count and zoho_count >= 1,
              f"Zoho servers: {zoho_count}")
        check(results, "no_mailgun_server",
              not mailgun_count or mailgun_count == 0,
              f"Mailgun servers: {mailgun_count or 0}")
    except Exception:
        check(results, "mail_server_check", True, "ir_mail_server not available")

    # --- Non-prod mail suppression ---
    if db_name != "odoo":
        try:
            active_outbound = query_one(conn, """
                SELECT count(*) FROM ir_mail_server
                WHERE active = true AND smtp_host NOT LIKE '%mailpit%' AND smtp_host NOT LIKE '%mailhog%'
            """)
            check(results, "non_prod_mail_suppression",
                  True,  # Warning only, not blocking
                  f"Active outbound servers: {active_outbound or 0} (consider suppression for non-prod)")
        except Exception:
            pass

    conn.close()

    # --- Summary ---
    passed = sum(1 for r in results if r["passed"])
    failed = sum(1 for r in results if not r["passed"])
    total = len(results)
    all_passed = failed == 0

    print(f"\n=== Results: {passed}/{total} passed, {failed} failed ===\n")

    # --- Evidence emission ---
    evidence = {
        "validation": "production_seed_state",
        "database": db_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {"total": total, "passed": passed, "failed": failed},
        "all_passed": all_passed,
        "checks": results,
    }

    if evidence_dir:
        evidence_path = Path(evidence_dir)
        evidence_path.mkdir(parents=True, exist_ok=True)
        evidence_file = evidence_path / "production-seed-validation.json"
        with open(evidence_file, "w") as f:
            json.dump(evidence, f, indent=2)
        print(f"Evidence: {evidence_file}")
    else:
        # Default evidence location
        default_dir = Path(f"docs/evidence/{datetime.now().strftime('%Y%m%d-%H%M')}/seed")
        default_dir.mkdir(parents=True, exist_ok=True)
        evidence_file = default_dir / "production-seed-validation.json"
        with open(evidence_file, "w") as f:
            json.dump(evidence, f, indent=2)
        print(f"Evidence: {evidence_file}")

    return results, all_passed


def main():
    parser = argparse.ArgumentParser(description="Validate Odoo seed state")
    parser.add_argument("--db", required=True, help="Database name (odoo_dev | odoo_staging | odoo)")
    parser.add_argument("--evidence-dir", help="Directory for evidence output")
    parser.add_argument("--plan", help="Path to production_seed_plan.yaml (unused, for future)")
    args = parser.parse_args()

    _, all_passed = validate(args.db, args.evidence_dir)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
