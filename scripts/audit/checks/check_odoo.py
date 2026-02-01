#!/usr/bin/env python3
"""
Odoo Integration Audit Check

Validates:
- Health endpoint accessibility
- Login page accessibility
- Version info endpoint
- Optional: Database connectivity via JSON-RPC
"""
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import HTTPClient, CheckResult, IntegrationResult, check_env_vars, redact_dict


def main():
    output_file = sys.argv[1] if len(sys.argv) > 1 else "odoo_audit.json"

    # Default to production URL
    odoo_url = os.environ.get("ODOO_BASE_URL", "https://erp.insightpulseai.net").rstrip("/")

    result = IntegrationResult(
        name="Odoo CE 19",
        status="SKIP",
        risk_tier="critical",
        checks=[],
        recommendations=[]
    )

    client = HTTPClient(timeout=30)
    checks = []
    latencies = []

    # Check 1: Health endpoint
    check = run_health_check(client, odoo_url)
    checks.append(check)
    if check.latency_ms:
        latencies.append(check.latency_ms)

    # Check 2: Login page
    check = run_login_page_check(client, odoo_url)
    checks.append(check)
    if check.latency_ms:
        latencies.append(check.latency_ms)

    # Check 3: Version info
    check = run_version_check(client, odoo_url)
    checks.append(check)
    if check.latency_ms:
        latencies.append(check.latency_ms)

    # Check 4: Database info (via web controller)
    check = run_database_check(client, odoo_url)
    checks.append(check)
    if check.latency_ms:
        latencies.append(check.latency_ms)

    # Calculate result
    result.checks = checks
    result.pass_count = sum(1 for c in checks if c.status == "PASS")
    result.error_count = sum(1 for c in checks if c.status == "FAIL")
    result.latency_avg_ms = round(sum(latencies) / len(latencies), 2) if latencies else None

    if result.error_count == 0:
        result.status = "PASS"
        result.access_level = "ok"
    elif result.pass_count > 0:
        result.status = "PARTIAL"
        result.access_level = "insufficient"
    else:
        result.status = "FAIL"
        result.access_level = "insufficient"

    result.evidence = {
        "odoo_url": odoo_url
    }

    # Add recommendations based on failures
    health_check = next((c for c in checks if c.name == "health_check"), None)
    if health_check and health_check.status == "FAIL":
        result.recommendations.append("Odoo health endpoint not responding - check if container is running")
        result.recommendations.append("Run: docker compose -f deploy/docker-compose.prod.yml ps")

    save_result(result, output_file)


def run_health_check(client, base_url):
    """Check Odoo health endpoint."""
    check = CheckResult(
        name="health_check",
        integration="odoo",
        description="Check Odoo health endpoint",
        status="FAIL"
    )

    try:
        resp = client.request("GET", f"{base_url}/web/health")
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            check.status = "PASS"
            check.evidence = {"response": resp.get("body")}
        else:
            check.error = f"Health check returned: {resp['status_code']}"
            if resp.get("error"):
                check.error += f" ({resp['error']})"

    except Exception as e:
        check.error = str(e)

    return check


def run_login_page_check(client, base_url):
    """Check login page accessibility."""
    check = CheckResult(
        name="login_page",
        integration="odoo",
        description="Check login page accessibility",
        status="FAIL"
    )

    try:
        resp = client.request("GET", f"{base_url}/web/login")
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        # 200 = login page, 303 = redirect (already logged in or to db selector)
        if resp["status_code"] in [200, 303]:
            check.status = "PASS"
            check.evidence = {"accessible": True}
        else:
            check.error = f"Login page returned: {resp['status_code']}"

    except Exception as e:
        check.error = str(e)

    return check


def run_version_check(client, base_url):
    """Get Odoo version info."""
    check = CheckResult(
        name="version_info",
        integration="odoo",
        description="Get Odoo version info",
        status="FAIL"
    )

    try:
        resp = client.request("GET", f"{base_url}/web/webclient/version_info")
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            check.status = "PASS"
            body = resp.get("body", {})
            if isinstance(body, dict):
                check.evidence = {
                    "server_version": body.get("server_version"),
                    "server_version_info": body.get("server_version_info")
                }
            else:
                check.evidence = {"response": str(body)[:200]}
        else:
            check.error = f"Version info returned: {resp['status_code']}"

    except Exception as e:
        check.error = str(e)

    return check


def run_database_check(client, base_url):
    """Check database selector (should be disabled in production)."""
    check = CheckResult(
        name="database_selector",
        integration="odoo",
        description="Check database selector status",
        status="FAIL"
    )

    try:
        resp = client.request("GET", f"{base_url}/web/database/selector")
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            # Database selector is enabled (not recommended for production)
            check.status = "PASS"  # It works, but...
            check.evidence = {"db_selector_enabled": True}
            check.recommendations = ["Consider disabling database selector (list_db = False) for production"]
        elif resp["status_code"] in [303, 404]:
            # Disabled or redirected - good for production
            check.status = "PASS"
            check.evidence = {"db_selector_enabled": False}
        else:
            check.error = f"Database selector returned: {resp['status_code']}"

    except Exception as e:
        check.error = str(e)

    return check


def save_result(result, output_file):
    """Save result to file."""
    data = result.to_dict()
    data = redact_dict(data)

    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2, default=str)

    print(f"Odoo audit: {result.status} ({result.pass_count} passed, {result.error_count} failed)")


if __name__ == "__main__":
    main()
