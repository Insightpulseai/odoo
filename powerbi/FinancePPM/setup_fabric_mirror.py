#!/usr/bin/env python3
"""
Set up Fabric Mirroring for Azure PostgreSQL → OneLake.

Replicates Odoo PostgreSQL tables into OneLake as Delta Lake tables,
enabling Direct Lake mode for Power BI (no Import refresh needed).

Prerequisites:
  pip install requests azure-identity
  az login  (or set AZURE_CLIENT_ID/AZURE_TENANT_ID/AZURE_CLIENT_SECRET)

Usage:
  # Full setup: create mirrored database, configure, start mirroring
  python setup_fabric_mirror.py \
    --pg-server pg-ipai-odoo.postgres.database.azure.com \
    --pg-database odoo \
    --pg-user odoo_readonly \
    --pg-password "$PG_READONLY_PASSWORD"

  # Check mirroring status
  python setup_fabric_mirror.py --status

  # Stop mirroring
  python setup_fabric_mirror.py --stop

  # Start mirroring (after stop)
  python setup_fabric_mirror.py --start
"""

import argparse
import json
import os
import subprocess
import sys
import time


# Constants
WORKSPACE_ID = "8cde337e-26e9-40d7-826e-4b30172b494e"
FABRIC_BASE = "https://api.fabric.microsoft.com/v1"

# Tables to mirror (Odoo PostgreSQL → OneLake)
MIRROR_TABLES = [
    {"schema": "public", "table": "project_project"},
    {"schema": "public", "table": "project_task"},
    {"schema": "public", "table": "project_task_type"},
    {"schema": "public", "table": "account_analytic_account"},
    {"schema": "public", "table": "hr_expense"},
]

# Display name for the mirrored database item
MIRROR_DISPLAY_NAME = "odoo-mirror"
MIRROR_DESCRIPTION = "Fabric Mirror of pg-ipai-odoo PostgreSQL (Odoo CE 18)"

# T-SQL view for the SQL analytics endpoint (auto-created by mirroring).
# Extracts analytic_account_id from the hr_expense.analytic_distribution JSON.
# Run this in: Fabric workspace → odoo-mirror → SQL analytics endpoint → New query
SQL_ANALYTICS_VIEW = """
CREATE VIEW dbo.v_hr_expense_ppm AS
SELECT
    id,
    name,
    total_amount_currency,
    date,
    employee_id,
    state,
    is_pulser_draft,
    TRY_CAST(
        JSON_VALUE(
            '["' + REPLACE(
                SUBSTRING(
                    analytic_distribution,
                    2,
                    CHARINDEX(':', analytic_distribution) - 3
                ),
                '"', ''
            ) + '"]',
            '$[0]'
        ) AS INT
    ) AS analytic_account_id
FROM dbo.hr_expense;
"""


def get_token():
    """Get Fabric API token via Azure CLI."""
    result = subprocess.run(
        ["az", "account", "get-access-token",
         "--resource", "https://api.fabric.microsoft.com",
         "--query", "accessToken", "-o", "tsv"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Error getting token: {result.stderr}")
        sys.exit(1)
    return result.stdout.strip()


def api(method, path, token, json_data=None, long_running=False):
    """Make Fabric REST API call."""
    import requests

    url = f"{FABRIC_BASE}/{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    resp = requests.request(method, url, headers=headers, json=json_data)

    if resp.status_code == 429:
        retry = int(resp.headers.get("Retry-After", 60))
        print(f"  Rate limited — waiting {retry}s")
        time.sleep(retry)
        return api(method, path, token, json_data, long_running)

    # Long-running operation (202 Accepted)
    if resp.status_code == 202 and long_running:
        location = resp.headers.get("Location")
        retry_after = int(resp.headers.get("Retry-After", 10))
        if location:
            print(f"  Long-running operation started, polling every {retry_after}s...")
            return poll_operation(location, token, retry_after)

    return resp


def poll_operation(url, token, interval=10, timeout=300):
    """Poll a long-running Fabric operation until complete."""
    import requests

    headers = {"Authorization": f"Bearer {token}"}
    start = time.time()

    while (time.time() - start) < timeout:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            body = resp.json()
            status = body.get("status", "Unknown")
            if status in ("Succeeded", "Completed"):
                print(f"  Operation completed: {status}")
                return resp
            elif status in ("Failed", "Cancelled"):
                print(f"  Operation failed: {status}")
                print(f"  Error: {json.dumps(body.get('error', {}), indent=2)}")
                return resp
            else:
                elapsed = int(time.time() - start)
                print(f"  Status: {status} ({elapsed}s elapsed)")
        time.sleep(interval)

    print(f"  Timeout after {timeout}s")
    return None


def find_mirrored_database(token):
    """Find existing mirrored database item in workspace."""
    resp = api("GET", f"workspaces/{WORKSPACE_ID}/items?type=MirroredDatabase", token)
    if resp.status_code != 200:
        return None

    items = resp.json().get("value", [])
    for item in items:
        if item.get("displayName") == MIRROR_DISPLAY_NAME:
            return item
    return None


def create_mirrored_database(token, pg_server, pg_database, pg_user, pg_password, pg_port="5432"):
    """Create a mirrored database item in the Fabric workspace."""
    print("Step 1: Creating mirrored database item...")

    # Check if already exists
    existing = find_mirrored_database(token)
    if existing:
        mirror_id = existing["id"]
        print(f"  Already exists: {mirror_id}")
        return mirror_id

    # Create the mirrored database item
    # The definition includes the PostgreSQL connection and table selection
    mirror_definition = {
        "properties": {
            "source": {
                "type": "AzureDatabaseForPostgreSql",
                "typeProperties": {
                    "connection": {
                        "serverName": pg_server,
                        "databaseName": pg_database,
                        "port": int(pg_port),
                    }
                }
            },
            "target": {
                "type": "OneLake",
                "typeProperties": {
                    "format": "Delta",
                }
            }
        }
    }

    resp = api("POST",
        f"workspaces/{WORKSPACE_ID}/items",
        token,
        {
            "displayName": MIRROR_DISPLAY_NAME,
            "type": "MirroredDatabase",
            "description": MIRROR_DESCRIPTION,
            "definition": {
                "parts": [
                    {
                        "path": "mirroring.json",
                        "payload": json.dumps(mirror_definition),
                        "payloadType": "InlineBase64",
                    }
                ]
            }
        },
        long_running=True,
    )

    if resp and resp.status_code in (200, 201):
        mirror_id = resp.json().get("id")
        print(f"  Created mirrored database: {mirror_id}")
        return mirror_id
    elif resp:
        print(f"  Create response: {resp.status_code} — {resp.text[:300]}")
        # If item creation doesn't support inline definition, try two-step approach
        return create_mirrored_database_two_step(token, pg_server, pg_database, pg_user, pg_password, pg_port)
    return None


def create_mirrored_database_two_step(token, pg_server, pg_database, pg_user, pg_password, pg_port="5432"):
    """Alternative: Create mirrored database item, then configure connection."""
    print("  Trying two-step creation...")

    # Step 1: Create empty mirrored database item
    resp = api("POST",
        f"workspaces/{WORKSPACE_ID}/items",
        token,
        {
            "displayName": MIRROR_DISPLAY_NAME,
            "type": "MirroredDatabase",
            "description": MIRROR_DESCRIPTION,
        },
        long_running=True,
    )

    if resp and resp.status_code in (200, 201):
        mirror_id = resp.json().get("id")
        print(f"  Created item: {mirror_id}")
        return mirror_id
    elif resp:
        print(f"  Two-step create response: {resp.status_code} — {resp.text[:300]}")
    return None


def configure_mirroring(token, mirror_id, pg_server, pg_database, pg_user, pg_password, pg_port="5432"):
    """Configure the mirrored database connection and table selection."""
    print("Step 2: Configuring mirroring connection...")

    # Get current definition
    resp = api("GET", f"workspaces/{WORKSPACE_ID}/mirroredDatabases/{mirror_id}/getDefinition", token)

    if resp.status_code == 200:
        print("  Retrieved current definition")
    else:
        print(f"  Get definition: {resp.status_code}")

    # Build table selection
    tables_config = []
    for t in MIRROR_TABLES:
        tables_config.append({
            "sourceSchemaName": t["schema"],
            "sourceTableName": t["table"],
            "targetTableName": t["table"],  # same name in OneLake
        })

    # Update mirroring definition with connection + tables
    import base64

    mirror_config = {
        "properties": {
            "source": {
                "type": "AzureDatabaseForPostgreSql",
                "typeProperties": {
                    "connection": {
                        "serverName": pg_server,
                        "databaseName": pg_database,
                        "port": int(pg_port),
                        "authentication": {
                            "type": "Basic",
                            "username": pg_user,
                            "password": pg_password,
                        }
                    },
                    "tables": tables_config,
                }
            }
        }
    }

    payload_b64 = base64.b64encode(json.dumps(mirror_config).encode()).decode()

    resp = api("POST",
        f"workspaces/{WORKSPACE_ID}/mirroredDatabases/{mirror_id}/updateDefinition",
        token,
        {
            "definition": {
                "parts": [
                    {
                        "path": "mirroring.json",
                        "payload": payload_b64,
                        "payloadType": "InlineBase64",
                    }
                ]
            }
        },
        long_running=True,
    )

    if resp and resp.status_code in (200, 202):
        print("  Mirroring configured")
        return True
    elif resp:
        print(f"  Configure response: {resp.status_code} — {resp.text[:300]}")
    return False


def start_mirroring(token, mirror_id=None):
    """Start mirroring (initial snapshot + continuous replication)."""
    if not mirror_id:
        existing = find_mirrored_database(token)
        if not existing:
            print("No mirrored database found in workspace")
            return False
        mirror_id = existing["id"]

    print("Step 3: Starting mirroring...")

    resp = api("POST",
        f"workspaces/{WORKSPACE_ID}/mirroredDatabases/{mirror_id}/startMirroring",
        token,
        long_running=True,
    )

    if resp and resp.status_code in (200, 202):
        print("  Mirroring started")
        return True
    elif resp:
        print(f"  Start response: {resp.status_code} — {resp.text[:300]}")
    return False


def stop_mirroring(token, mirror_id=None):
    """Stop mirroring."""
    if not mirror_id:
        existing = find_mirrored_database(token)
        if not existing:
            print("No mirrored database found in workspace")
            return False
        mirror_id = existing["id"]

    print("Stopping mirroring...")

    resp = api("POST",
        f"workspaces/{WORKSPACE_ID}/mirroredDatabases/{mirror_id}/stopMirroring",
        token,
    )

    if resp and resp.status_code in (200, 202):
        print("  Mirroring stopped")
        return True
    elif resp:
        print(f"  Stop response: {resp.status_code} — {resp.text[:300]}")
    return False


def get_mirroring_status(token, mirror_id=None):
    """Get mirroring status and table replication details."""
    if not mirror_id:
        existing = find_mirrored_database(token)
        if not existing:
            print("No mirrored database found in workspace")
            return None
        mirror_id = existing["id"]
        print(f"Mirrored database: {MIRROR_DISPLAY_NAME} ({mirror_id})")

    # Get mirroring status
    resp = api("GET",
        f"workspaces/{WORKSPACE_ID}/mirroredDatabases/{mirror_id}/getMirroringStatus",
        token,
    )

    if resp.status_code == 200:
        status = resp.json()
        print(f"  Status: {status.get('status', 'Unknown')}")
        print(f"  Last sync: {status.get('lastSyncDateTime', 'Never')}")

        tables = status.get("tableStatuses", [])
        if tables:
            print(f"\n  Table replication ({len(tables)} tables):")
            for t in tables:
                print(f"    {t.get('sourceSchemaName', '?')}.{t.get('sourceTableName', '?')}")
                print(f"      Status: {t.get('status', '?')}")
                print(f"      Last sync: {t.get('lastSyncDateTime', 'Never')}")
                metrics = t.get('metrics', {})
                if metrics:
                    print(f"      Rows: {metrics.get('processedCount', '?')}")
                    print(f"      Size: {metrics.get('processedBytes', '?')} bytes")
        return status
    elif resp.status_code == 404:
        print("  Mirrored database not found or mirroring not configured")
    else:
        print(f"  Status response: {resp.status_code} — {resp.text[:300]}")
    return None


def show_status(token):
    """Show full Fabric Mirroring status."""
    print(f"Workspace: Finance PPM ({WORKSPACE_ID})")
    print()

    # List all mirrored databases
    resp = api("GET", f"workspaces/{WORKSPACE_ID}/items?type=MirroredDatabase", token)
    if resp.status_code == 200:
        items = resp.json().get("value", [])
        print(f"Mirrored databases: {len(items)}")
        for item in items:
            print(f"  {item.get('displayName')} ({item.get('id')})")
            print(f"    Description: {item.get('description', 'N/A')}")
            print()
            get_mirroring_status(token, item["id"])
            print()
    else:
        print(f"  List response: {resp.status_code} — {resp.text[:200]}")

    # Also show SQL analytics endpoint if available
    resp = api("GET", f"workspaces/{WORKSPACE_ID}/items?type=SQLEndpoint", token)
    if resp.status_code == 200:
        endpoints = resp.json().get("value", [])
        print(f"SQL Analytics Endpoints: {len(endpoints)}")
        for ep in endpoints:
            print(f"  {ep.get('displayName')} ({ep.get('id')})")
    print()

    # Show semantic models
    resp = api("GET", f"workspaces/{WORKSPACE_ID}/items?type=SemanticModel", token)
    if resp.status_code == 200:
        models = resp.json().get("value", [])
        print(f"Semantic Models: {len(models)}")
        for m in models:
            print(f"  {m.get('displayName')} ({m.get('id')})")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Set up Fabric Mirroring for Odoo PostgreSQL → OneLake"
    )
    parser.add_argument("--pg-server", default="pg-ipai-odoo.postgres.database.azure.com",
                        help="PostgreSQL server hostname")
    parser.add_argument("--pg-database", default="odoo", help="Database name")
    parser.add_argument("--pg-port", default="5432", help="PostgreSQL port")
    parser.add_argument("--pg-user", help="PostgreSQL username")
    parser.add_argument("--pg-password",
                        help="PostgreSQL password (or set PG_READONLY_PASSWORD env)")
    parser.add_argument("--status", action="store_true", help="Show mirroring status")
    parser.add_argument("--start", action="store_true", help="Start mirroring")
    parser.add_argument("--stop", action="store_true", help="Stop mirroring")
    parser.add_argument("--print-views", action="store_true",
                        help="Print SQL analytics endpoint views (run in Fabric)")

    args = parser.parse_args()
    token = get_token()

    if args.print_views:
        print("-- Run in: Fabric workspace → odoo-mirror → SQL analytics endpoint → New query")
        print(SQL_ANALYTICS_VIEW)
        return

    if args.status:
        show_status(token)
        return

    if args.start:
        start_mirroring(token)
        return

    if args.stop:
        stop_mirroring(token)
        return

    # Full setup
    pg_password = args.pg_password or os.environ.get("PG_READONLY_PASSWORD")
    if not all([args.pg_user, pg_password]):
        print("Error: --pg-user and --pg-password (or PG_READONLY_PASSWORD env) required")
        print()
        print("Example:")
        print("  python setup_fabric_mirror.py \\")
        print("    --pg-user odoo_readonly \\")
        print("    --pg-password $PG_READONLY_PASSWORD")
        sys.exit(1)

    # 1. Create mirrored database item
    mirror_id = create_mirrored_database(
        token, args.pg_server, args.pg_database,
        args.pg_user, pg_password, args.pg_port,
    )

    if not mirror_id:
        print("Failed to create mirrored database")
        sys.exit(1)

    # 2. Configure connection and table selection
    configure_mirroring(
        token, mirror_id, args.pg_server, args.pg_database,
        args.pg_user, pg_password, args.pg_port,
    )

    # 3. Start mirroring
    start_mirroring(token, mirror_id)

    # 4. Wait and check initial status
    print()
    print("Waiting 30s for initial snapshot to begin...")
    time.sleep(30)
    get_mirroring_status(token, mirror_id)

    print()
    print("=" * 60)
    print("Fabric Mirroring configured.")
    print(f"  Mirrored DB: {MIRROR_DISPLAY_NAME} ({mirror_id})")
    print(f"  Source: {args.pg_server}/{args.pg_database}")
    print(f"  Tables: {len(MIRROR_TABLES)} tables → OneLake (Delta)")
    print()
    print("Next steps:")
    print("  1. Monitor: python setup_fabric_mirror.py --status")
    print("  2. Once snapshot completes, semantic model auto-binds to mirrored tables")
    print("  3. Power BI report uses Direct Lake mode (near real-time, no refresh needed)")
    print("=" * 60)


if __name__ == "__main__":
    main()
