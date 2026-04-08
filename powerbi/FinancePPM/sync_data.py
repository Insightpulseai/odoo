#!/usr/bin/env python3
"""
Sync Odoo PostgreSQL data to Power BI Push dataset.

Pulls data from pg-ipai-odoo and pushes to the Power BI dataset
via the Push Rows REST API. Run on a schedule (e.g., cron, Azure Functions).

Usage:
  # Full sync (clear + push all tables)
  python sync_data.py

  # Incremental (push only, no clear)
  python sync_data.py --incremental

  # Specific tables only
  python sync_data.py --tables Project,Task

  # Status check
  python sync_data.py --status
"""

import argparse
import json
import os
import subprocess
import sys
import time

import psycopg2
import requests


# Constants
WORKSPACE_ID = "8cde337e-26e9-40d7-826e-4b30172b494e"
DATASET_ID = "e93b4f4c-e073-4a47-b404-1a8336ec9718"
PBI_BASE = "https://api.powerbi.com/v1.0/myorg"

PG_SERVER = "pg-ipai-odoo.postgres.database.azure.com"
PG_DATABASE = "odoo"
PG_PORT = 5432
PG_USER = "odoo_readonly"


def get_pbi_token():
    """Get Power BI API token via Azure CLI."""
    result = subprocess.run(
        ["az", "account", "get-access-token",
         "--resource", "https://analysis.windows.net/powerbi/api",
         "--query", "accessToken", "-o", "tsv"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Error getting PBI token: {result.stderr}")
        sys.exit(1)
    return result.stdout.strip()


def get_pg_connection():
    """Connect to Odoo PostgreSQL."""
    pg_password = os.environ.get("PG_READONLY_PASSWORD")
    if not pg_password:
        print("Error: PG_READONLY_PASSWORD env var required")
        sys.exit(1)

    return psycopg2.connect(
        host=PG_SERVER, port=PG_PORT, dbname=PG_DATABASE,
        user=PG_USER, password=pg_password, sslmode="require",
    )


def extract_name(val):
    """Extract string from Odoo 18 translatable dict or plain string."""
    if isinstance(val, dict):
        return val.get("en_US", str(next(iter(val.values()), "")))
    return str(val) if val else ""


def push_rows(token, table_name, rows, batch_size=10000):
    """Push rows to Power BI Push dataset."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    total = 0
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        resp = requests.post(
            f"{PBI_BASE}/groups/{WORKSPACE_ID}/datasets/{DATASET_ID}/tables/{table_name}/rows",
            headers=headers,
            json={"rows": batch},
        )
        if resp.status_code != 200:
            print(f"    Error pushing {table_name}: {resp.status_code} — {resp.text[:150]}")
            return total
        total += len(batch)
    return total


def clear_table(token, table_name):
    """Clear all rows from a Push dataset table."""
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.delete(
        f"{PBI_BASE}/groups/{WORKSPACE_ID}/datasets/{DATASET_ID}/tables/{table_name}/rows",
        headers=headers,
    )
    return resp.status_code == 200


def sync_projects(cursor):
    """Fetch project data from PostgreSQL."""
    cursor.execute("""
        SELECT id, name, active, company_id, COALESCE(account_id, 0)
        FROM project_project
    """)
    return [{
        "ProjectID": int(r[0]),
        "ProjectName": extract_name(r[1]),
        "BudgetAmount": 0.0,
        "CostCenter": "",
        "IsActive": bool(r[2]) if r[2] is not None else True,
        "CompanyID": int(r[3]) if r[3] else 0,
        "AnalyticAccountID": int(r[4]) if r[4] else 0,
    } for r in cursor.fetchall()]


def sync_tasks(cursor):
    """Fetch task data from PostgreSQL."""
    cursor.execute("""
        SELECT id, name, project_id, stage_id, date_deadline,
               create_date, priority, active
        FROM project_task
    """)
    return [{
        "TaskID": int(r[0]),
        "TaskName": extract_name(r[1]),
        "ProjectID": int(r[2]) if r[2] else 0,
        "StageID": int(r[3]) if r[3] else 0,
        "DateDeadline": r[4].isoformat() if r[4] else None,
        "CreateDate": r[5].isoformat() if r[5] else None,
        "Priority": str(r[6]) if r[6] else "0",
        "IsActive": bool(r[7]) if r[7] is not None else True,
    } for r in cursor.fetchall()]


def sync_stages(cursor):
    """Fetch stage data from PostgreSQL."""
    cursor.execute("SELECT id, name, sequence, fold FROM project_task_type")
    return [{
        "StageID": int(r[0]),
        "StageName": extract_name(r[1]),
        "Sequence": int(r[2]) if r[2] is not None else 0,
        "IsFolded": bool(r[3]) if r[3] is not None else False,
    } for r in cursor.fetchall()]


def sync_analytic_accounts(cursor):
    """Fetch analytic account data from PostgreSQL."""
    cursor.execute("SELECT id, name, plan_id FROM account_analytic_account")
    return [{
        "AnalyticAccountID": int(r[0]),
        "AccountName": extract_name(r[1]),
        "PlanID": int(r[2]) if r[2] else 0,
    } for r in cursor.fetchall()]


def sync_expenses(cursor):
    """Fetch expense data from PostgreSQL."""
    cursor.execute("""
        SELECT id, name, total_amount_currency, date,
               employee_id, state, analytic_distribution
        FROM hr_expense
    """)
    rows = []
    for r in cursor.fetchall():
        analytic_id = 0
        if r[6] and isinstance(r[6], dict):
            keys = list(r[6].keys())
            if keys:
                try:
                    analytic_id = int(keys[0])
                except (ValueError, TypeError):
                    pass
        rows.append({
            "ExpenseID": int(r[0]),
            "ExpenseName": extract_name(r[1]),
            "TotalAmount": float(r[2]) if r[2] else 0.0,
            "ExpenseDate": r[3].isoformat() if r[3] else None,
            "AnalyticAccountID": analytic_id,
            "EmployeeID": int(r[4]) if r[4] else 0,
            "State": str(r[5]) if r[5] else "",
        })
    return rows


TABLE_SYNCS = {
    "Project": sync_projects,
    "Task": sync_tasks,
    "Stage": sync_stages,
    "AnalyticAccount": sync_analytic_accounts,
    "Expense": sync_expenses,
}


def main():
    parser = argparse.ArgumentParser(description="Sync Odoo data to Power BI")
    parser.add_argument("--incremental", action="store_true",
                        help="Don't clear tables before push")
    parser.add_argument("--tables", help="Comma-separated table names to sync")
    parser.add_argument("--status", action="store_true", help="Show sync status")
    args = parser.parse_args()

    token = get_pbi_token()

    if args.status:
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(
            f"{PBI_BASE}/groups/{WORKSPACE_ID}/datasets/{DATASET_ID}",
            headers=headers,
        )
        ds = resp.json()
        print(f"Dataset: {ds.get('name')} ({DATASET_ID})")
        print(f"  Owner: {ds.get('configuredBy')}")
        print(f"  Refreshable: {ds.get('isRefreshable')}")
        return

    tables = args.tables.split(",") if args.tables else list(TABLE_SYNCS.keys())

    conn = get_pg_connection()
    cursor = conn.cursor()
    start = time.time()

    print(f"Syncing {len(tables)} tables from pg-ipai-odoo → Power BI...")
    print()

    total_rows = 0
    for table_name in tables:
        if table_name not in TABLE_SYNCS:
            print(f"  Unknown table: {table_name}")
            continue

        print(f"  {table_name}:", end=" ")

        # Clear existing rows
        if not args.incremental:
            clear_table(token, table_name)

        # Fetch and push
        rows = TABLE_SYNCS[table_name](cursor)
        pushed = push_rows(token, table_name, rows)
        total_rows += pushed
        print(f"{pushed} rows")

    cursor.close()
    conn.close()

    elapsed = int(time.time() - start)
    print()
    print(f"Sync complete: {total_rows} rows in {elapsed}s")
    print(f"Dataset: {DATASET_ID}")


if __name__ == "__main__":
    main()
