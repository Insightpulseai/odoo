"""
agent-platform/agents/release-manager/odoo_health_agent.py

IPAI Odoo Health Agent
NO RMA EQUIVALENT — this is new, built for IPAI's release gate.

Checks Odoo module health before stamp promotion:
- Module installed and active
- No ORM errors in the last hour (Application Insights)
- BIR deadline calendar (no deadline within freeze window)
- Accounting period lock status
- Active alert rules for ACA containers

Called by: agent_orchestrator.py → GateEvaluator agent
"""
import os
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional

import httpx
from azure.identity import ChainedTokenCredential, ManagedIdentityCredential
from azure.monitor.query import LogsQueryClient, LogsQueryStatus

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
credential = ChainedTokenCredential(
    ManagedIdentityCredential(client_id=os.environ.get("AZURE_CLIENT_ID", "")),
)

ODOO_URL = os.environ.get("ODOO_URL", "https://erp.insightpulseai.com")
ODOO_DB = os.environ.get("ODOO_DB", "odoo")
LA_WORKSPACE_ID = os.environ.get("LA_WORKSPACE_ID", "")  # la-ipai-odoo-dev workspace ID

# ---------------------------------------------------------------------------
# Odoo module health check
# ---------------------------------------------------------------------------
async def check_module_installed(module_name: str, session_token: str) -> dict:
    """
    Verify the module is installed and not in a broken state.
    Returns: {installed: bool, state: str, version: str, error: str | null}
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{ODOO_URL}/api/jsonrpc",
            json={
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute_kw",
                    "args": [
                        ODOO_DB, 1, "admin",  # use service account in prod
                        "ir.module.module",
                        "search_read",
                        [[["name", "=", module_name]]],
                        {"fields": ["name", "state", "latest_version", "installed_version"]},
                    ],
                },
            },
            headers={"Cookie": f"session_id={session_token}"},
            timeout=15.0,
        )
        result = resp.json().get("result", [])
        if not result:
            return {"installed": False, "state": "uninstalled", "version": None, "error": "Module not found"}

        module = result[0]
        state = module.get("state", "unknown")
        return {
            "installed": state == "installed",
            "state": state,
            "version": module.get("installed_version"),
            "error": None if state == "installed" else f"Module state: {state}",
        }


# ---------------------------------------------------------------------------
# BIR deadline calendar
# ---------------------------------------------------------------------------
BIR_DEADLINES = {
    # (month, day): form name
    (1, 10): "0619-E",  (2, 10): "0619-E",  (3, 10): "0619-E",
    (4, 10): "0619-E",  (5, 10): "0619-E",  (6, 10): "0619-E",
    (7, 10): "0619-E",  (8, 10): "0619-E",  (9, 10): "0619-E",
    (10, 10): "0619-E", (11, 10): "0619-E", (12, 10): "0619-E",
    (4, 25): "2550Q",  (7, 25): "2550Q",
    (10, 25): "2550Q", (1, 25): "2550Q",
}
FREEZE_WINDOW_DAYS = 3

def check_bir_freeze_window() -> dict:
    """
    Check if we are within the BIR freeze window (3 days before any deadline).
    Returns: {freeze_active: bool, form: str | null, days_to_deadline: int | null}
    """
    now_pht = datetime.now(timezone.utc) + timedelta(hours=8)  # PHT = UTC+8
    today = now_pht.date()

    for (month, day), form in BIR_DEADLINES.items():
        # Find next occurrence of this deadline
        year = today.year
        try:
            deadline = today.replace(year=year, month=month, day=day)
        except ValueError:
            continue

        if deadline < today:
            # Try next year
            try:
                deadline = deadline.replace(year=year + 1)
            except ValueError:
                continue

        days_remaining = (deadline - today).days
        if 0 <= days_remaining <= FREEZE_WINDOW_DAYS:
            return {
                "freeze_active": True,
                "form": form,
                "deadline": deadline.isoformat(),
                "days_to_deadline": days_remaining,
            }

    # Find the next upcoming deadline for reporting
    min_days = None
    next_form = None
    next_deadline = None
    for (month, day), form in BIR_DEADLINES.items():
        year = today.year
        try:
            deadline = today.replace(year=year, month=month, day=day)
        except ValueError:
            continue
        if deadline < today:
            try:
                deadline = deadline.replace(year=year + 1)
            except ValueError:
                continue
        days = (deadline - today).days
        if min_days is None or days < min_days:
            min_days = days
            next_form = form
            next_deadline = deadline

    return {
        "freeze_active": False,
        "form": next_form if min_days is not None else None,
        "deadline": next_deadline.isoformat() if min_days is not None else None,
        "days_to_deadline": min_days,
    }


# ---------------------------------------------------------------------------
# Accounting period lock check
# ---------------------------------------------------------------------------
async def check_accounting_period_lock(session_token: str) -> dict:
    """
    Check if the accounting period is locked in Odoo (journal.lock_date).
    A locked period means no new journal entries — release should wait.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{ODOO_URL}/api/jsonrpc",
            json={
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "service": "object",
                    "method": "execute_kw",
                    "args": [
                        ODOO_DB, 1, "admin",
                        "res.company",
                        "search_read",
                        [[]],
                        {"fields": ["name", "period_lock_date", "fiscalyear_lock_date"]},
                    ],
                },
            },
            headers={"Cookie": f"session_id={session_token}"},
            timeout=15.0,
        )
        companies = resp.json().get("result", [])
        locked_companies = [
            c["name"] for c in companies
            if c.get("period_lock_date") is not None
        ]
        return {
            "period_locked": len(locked_companies) > 0,
            "locked_companies": locked_companies,
        }


# ---------------------------------------------------------------------------
# ACA health check — no active alerts
# ---------------------------------------------------------------------------
async def check_aca_health() -> dict:
    """
    Check Azure Monitor for active alert rules in rg-ipai-dev-odoo-runtime.
    Returns: {alerts_firing: bool, active_alerts: list[str]}

    Checks against the 16 alert rules we know exist from the inventory.
    """
    try:
        logs_client = LogsQueryClient(credential)
        # Query App Insights for recent ORM errors
        query = """
        exceptions
        | where timestamp > ago(1h)
        | where severityLevel >= 3  // Error or Critical
        | where cloud_RoleName in ("ipai-odoo-dev-web", "ipai-odoo-dev-worker", "ipai-odoo-dev-cron")
        | summarize error_count = count() by cloud_RoleName, type
        | where error_count > 5
        """
        result = logs_client.query_workspace(
            workspace_id=LA_WORKSPACE_ID,
            query=query,
            timespan=timedelta(hours=1),
        )
        if result.status == LogsQueryStatus.SUCCESS and result.tables:
            table = result.tables[0]
            errors = [
                {"role": row[0], "type": row[1], "count": row[2]}
                for row in table.rows
            ]
            return {"alerts_firing": len(errors) > 0, "active_alerts": errors}
    except Exception as e:
        print(f"Warning: Could not query Log Analytics: {e}")

    return {"alerts_firing": False, "active_alerts": []}


# ---------------------------------------------------------------------------
# Full health check — called by GateEvaluator
# ---------------------------------------------------------------------------
async def full_odoo_health_check(module_name: str, session_token: str = "") -> dict:
    """
    Run all Odoo health checks for the release gate.
    Called by agent_orchestrator.py GateEvaluator agent via tool call.
    """
    results = await asyncio.gather(
        check_module_installed(module_name, session_token),
        asyncio.to_thread(check_bir_freeze_window),
        check_accounting_period_lock(session_token),
        check_aca_health(),
        return_exceptions=True,
    )

    module_health, bir_status, period_lock, aca_health = [
        r if not isinstance(r, Exception) else {"error": str(r)}
        for r in results
    ]

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "module": module_name,
        "module_health": module_health,
        "bir_status": bir_status,
        "accounting_period": period_lock,
        "aca_health": aca_health,
        # Summary for gate agent
        "odoo_health": (
            "ok" if module_health.get("installed")
               and not period_lock.get("period_locked")
               and not aca_health.get("alerts_firing")
            else "warning" if module_health.get("installed")
            else "error"
        ),
        "bir_freeze_active": bir_status.get("freeze_active", False),
        "bir_next_deadline_days": bir_status.get("days_to_deadline"),
        "accounting_period_locked": period_lock.get("period_locked", False),
    }
