#!/usr/bin/env python3
"""
Configure Power BI Service dataset credentials and trigger refresh.
All programmatic — no UI clicks needed.

Usage:
  # Configure PostgreSQL credentials and refresh
  python configure_and_refresh.py \
    --pg-server pg-ipai-odoo.postgres.database.azure.com \
    --pg-database odoo \
    --pg-user odoo_readonly \
    --pg-password "$PG_READONLY_PASSWORD"

  # Just trigger refresh (credentials already configured)
  python configure_and_refresh.py --refresh-only

  # Check status
  python configure_and_refresh.py --status
"""

import argparse
import json
import os
import subprocess
import sys
import time


# Constants
WORKSPACE_ID = "8cde337e-26e9-40d7-826e-4b30172b494e"
DATASET_ID = "78451e30-71ba-4f33-8709-ef971b8be41c"
REPORT_ID = "5263af02-7379-4043-aa32-5ea82eac49be"
BASE = "https://api.powerbi.com/v1.0/myorg"

# Secure embed URL (already wired in Odoo config)
EMBED_URL = (
    f"https://app.powerbi.com/reportEmbed"
    f"?reportId={REPORT_ID}&groupId={WORKSPACE_ID}&w=2"
)


def get_token():
    """Get Power BI API token via Azure CLI."""
    result = subprocess.run(
        ["az", "account", "get-access-token",
         "--resource", "https://analysis.windows.net/powerbi/api",
         "--query", "accessToken", "-o", "tsv"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Error getting token: {result.stderr}")
        sys.exit(1)
    return result.stdout.strip()


def api(method, path, token, json_data=None):
    """Make Power BI REST API call."""
    import requests

    url = f"{BASE}/{path}"
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.request(method, url, headers=headers, json=json_data)

    if resp.status_code == 429:
        retry = int(resp.headers.get("Retry-After", 60))
        print(f"  Rate limited — waiting {retry}s")
        time.sleep(retry)
        return api(method, path, token, json_data)

    return resp


def update_parameters(token, pg_server, pg_database, pg_port="5432"):
    """Update dataset M query parameters (OdooServer, OdooDatabase, OdooPort)."""
    print("Step 1: Updating dataset parameters...")

    resp = api("POST",
        f"groups/{WORKSPACE_ID}/datasets/{DATASET_ID}/Default.UpdateParameters",
        token,
        {
            "updateDetails": [
                {"name": "OdooServer", "newValue": pg_server},
                {"name": "OdooDatabase", "newValue": pg_database},
                {"name": "OdooPort", "newValue": pg_port},
            ]
        },
    )

    if resp.status_code == 200:
        print("  Parameters updated")
    elif resp.status_code == 400 and "No parameters found" in resp.text:
        print("  No parameters in dataset — using direct datasource binding")
    else:
        print(f"  Response: {resp.status_code} — {resp.text[:200]}")


def discover_gateway_datasources(token):
    """Discover gateway and datasource IDs after parameter update."""
    print("Step 2: Discovering datasources...")

    resp = api("GET",
        f"groups/{WORKSPACE_ID}/datasets/{DATASET_ID}/Default.DiscoverGateways",
        token,
    )

    if resp.status_code == 200:
        gateways = resp.json().get("value", [])
        print(f"  Found {len(gateways)} gateway(s)")
        for gw in gateways:
            print(f"    Gateway: {gw['id']} ({gw.get('name', 'unnamed')})")
        return gateways
    else:
        print(f"  Response: {resp.status_code} — {resp.text[:200]}")
        return []


def configure_credentials(token, pg_server, pg_database, pg_user, pg_password, pg_port="5432"):
    """Configure PostgreSQL credentials on the dataset datasource."""
    print("Step 3: Configuring datasource credentials...")

    # First, get the datasources
    resp = api("GET",
        f"groups/{WORKSPACE_ID}/datasets/{DATASET_ID}/datasources",
        token,
    )

    datasources = resp.json().get("value", [])

    if not datasources:
        print("  No datasources found — dataset may need a parameter update first")
        print("  Attempting to bind datasource via gateway...")

        # Try to discover and bind
        gateways = discover_gateway_datasources(token)
        if not gateways:
            print("  No gateways available — credentials must be set after first manual refresh")
            print("  Alternatively, use an on-premises data gateway for PostgreSQL")
            return False

    for ds in datasources:
        gw_id = ds.get("gatewayId")
        ds_id = ds.get("datasourceId")
        ds_type = ds.get("datasourceType")

        print(f"  Datasource: {ds_type} (gateway={gw_id}, id={ds_id})")

        if ds_type in ("PostgreSql", "Extension"):
            # Update credentials
            cred_resp = api("PATCH",
                f"gateways/{gw_id}/datasources/{ds_id}",
                token,
                {
                    "credentialDetails": {
                        "credentialType": "Basic",
                        "credentials": json.dumps({
                            "credentialData": [
                                {"name": "username", "value": pg_user},
                                {"name": "password", "value": pg_password},
                            ]
                        }),
                        "encryptedConnection": "Encrypted",
                        "encryptionAlgorithm": "None",
                        "privacyLevel": "Organizational",
                    }
                },
            )

            if cred_resp.status_code == 200:
                print(f"  Credentials configured for {ds_type}")
            else:
                print(f"  Credential update: {cred_resp.status_code} — {cred_resp.text[:200]}")

    return True


def trigger_refresh(token):
    """Trigger dataset refresh."""
    print("Step 4: Triggering dataset refresh...")

    resp = api("POST",
        f"groups/{WORKSPACE_ID}/datasets/{DATASET_ID}/refreshes",
        token,
        {"notifyOption": "MailOnFailure"},
    )

    if resp.status_code == 202:
        print("  Refresh triggered")
        return True
    else:
        print(f"  Refresh response: {resp.status_code} — {resp.text[:200]}")
        return False


def wait_for_refresh(token, timeout_min=10):
    """Poll refresh status until complete."""
    print("Step 5: Waiting for refresh to complete...")

    start = time.time()
    while (time.time() - start) < timeout_min * 60:
        resp = api("GET",
            f"groups/{WORKSPACE_ID}/datasets/{DATASET_ID}/refreshes?$top=1",
            token,
        )
        refreshes = resp.json().get("value", [])
        if not refreshes:
            time.sleep(10)
            continue

        latest = refreshes[0]
        status = latest.get("status")

        if status == "Completed":
            print(f"  Refresh completed at {latest.get('endTime', '?')}")
            return True
        elif status == "Failed":
            error = latest.get("serviceExceptionJson", "Unknown")
            print(f"  Refresh FAILED: {error[:200]}")
            return False
        else:
            elapsed = int(time.time() - start)
            print(f"  Status: {status} ({elapsed}s elapsed)")
            time.sleep(15)

    print(f"  Timeout after {timeout_min} minutes")
    return False


def show_status(token):
    """Show current dataset and report status."""
    print(f"Workspace: Finance PPM ({WORKSPACE_ID})")
    print()

    # Dataset info
    ds_resp = api("GET", f"groups/{WORKSPACE_ID}/datasets/{DATASET_ID}", token)
    ds = ds_resp.json()
    print(f"Dataset: {ds.get('name')} ({DATASET_ID})")
    print(f"  Configured by: {ds.get('configuredBy', 'N/A')}")
    print(f"  Is refreshable: {ds.get('isRefreshable', 'N/A')}")
    print()

    # Datasources
    src_resp = api("GET", f"groups/{WORKSPACE_ID}/datasets/{DATASET_ID}/datasources", token)
    sources = src_resp.json().get("value", [])
    print(f"Datasources: {len(sources)}")
    for s in sources:
        print(f"  {s.get('datasourceType')}: {s.get('connectionDetails', {})}")
    print()

    # Recent refreshes
    ref_resp = api("GET",
        f"groups/{WORKSPACE_ID}/datasets/{DATASET_ID}/refreshes?$top=5",
        token,
    )
    refreshes = ref_resp.json().get("value", [])
    print(f"Refresh history: {len(refreshes)} entries")
    for r in refreshes:
        print(f"  {r.get('startTime', '?')} → {r.get('status')}")
    print()

    # Report
    rpt_resp = api("GET", f"groups/{WORKSPACE_ID}/reports/{REPORT_ID}", token)
    rpt = rpt_resp.json()
    print(f"Report: {rpt.get('name')}")
    print(f"  Web URL: {rpt.get('webUrl')}")
    print(f"  Embed URL: {EMBED_URL}")
    print()


def configure_schedule(token, times=None, days=None):
    """Set up scheduled refresh."""
    if times is None:
        times = ["06:00", "12:00", "18:00"]
    if days is None:
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    print("Step 6: Configuring scheduled refresh...")

    resp = api("PATCH",
        f"groups/{WORKSPACE_ID}/datasets/{DATASET_ID}/refreshSchedule",
        token,
        {
            "value": {
                "enabled": True,
                "notifyOption": "MailOnFailure",
                "days": days,
                "times": times,
                "localTimeZoneId": "Singapore Standard Time",  # UTC+8 (PH)
            }
        },
    )

    if resp.status_code == 200:
        print(f"  Scheduled: {', '.join(times)} on {', '.join(days)}")
    else:
        print(f"  Schedule response: {resp.status_code} — {resp.text[:200]}")


def main():
    parser = argparse.ArgumentParser(
        description="Configure Power BI dataset and trigger refresh"
    )
    parser.add_argument("--pg-server", help="PostgreSQL server hostname")
    parser.add_argument("--pg-database", default="odoo", help="Database name")
    parser.add_argument("--pg-port", default="5432", help="PostgreSQL port")
    parser.add_argument("--pg-user", help="PostgreSQL username")
    parser.add_argument("--pg-password", help="PostgreSQL password (or set PG_READONLY_PASSWORD env)")
    parser.add_argument("--refresh-only", action="store_true", help="Just trigger refresh")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--schedule", action="store_true", help="Configure scheduled refresh")

    args = parser.parse_args()
    token = get_token()

    if args.status:
        show_status(token)
        return

    if args.refresh_only:
        if trigger_refresh(token):
            wait_for_refresh(token)
        return

    if args.schedule:
        configure_schedule(token)
        return

    # Full setup
    pg_password = args.pg_password or os.environ.get("PG_READONLY_PASSWORD")
    if not all([args.pg_server, args.pg_user, pg_password]):
        print("Error: --pg-server, --pg-user, and --pg-password (or PG_READONLY_PASSWORD env) required")
        print()
        print("Example:")
        print("  python configure_and_refresh.py \\")
        print("    --pg-server pg-ipai-odoo.postgres.database.azure.com \\")
        print("    --pg-database odoo \\")
        print("    --pg-user odoo_readonly \\")
        print("    --pg-password $PG_READONLY_PASSWORD")
        sys.exit(1)

    # 1. Update parameters
    update_parameters(token, args.pg_server, args.pg_database, args.pg_port)

    # 2-3. Configure credentials
    configure_credentials(
        token, args.pg_server, args.pg_database,
        args.pg_user, pg_password, args.pg_port,
    )

    # 4-5. Trigger and wait for refresh
    if trigger_refresh(token):
        wait_for_refresh(token)

    # 6. Set up schedule
    configure_schedule(token)

    print()
    print("=" * 60)
    print("Dashboard ready.")
    print(f"  Embed URL: {EMBED_URL}")
    print(f"  Odoo param: ipai_ppm.powerbi_report_url")
    print("=" * 60)


if __name__ == "__main__":
    main()
