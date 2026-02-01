#!/usr/bin/env python3
"""
Apache Superset Integration Audit Check

Validates:
- Health endpoint
- Login page accessibility
- Database connections (if authenticated)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import HTTPClient, CheckResult, IntegrationResult, check_env_vars, redact_dict


def main():
    output_file = sys.argv[1] if len(sys.argv) > 1 else "superset_audit.json"

    # Superset base URL with default
    superset_url = os.environ.get("SUPERSET_BASE_URL", "https://superset.insightpulseai.net").rstrip("/")
    token = os.environ.get("SUPERSET_TOKEN")
    username = os.environ.get("SUPERSET_USERNAME")
    password = os.environ.get("SUPERSET_PASSWORD")

    result = IntegrationResult(
        name="Apache Superset",
        status="SKIP",
        risk_tier="medium",
        checks=[],
        recommendations=[]
    )

    client = HTTPClient(timeout=30)
    checks = []
    latencies = []

    # Check 1: Health endpoint
    check = run_health_check(client, superset_url)
    checks.append(check)
    if check.latency_ms:
        latencies.append(check.latency_ms)

    # Check 2: Login page
    check = run_login_check(client, superset_url)
    checks.append(check)
    if check.latency_ms:
        latencies.append(check.latency_ms)

    # Check 3: API (if token available)
    if token:
        check = run_api_check(client, superset_url, token)
        checks.append(check)
        if check.latency_ms:
            latencies.append(check.latency_ms)
    else:
        result.recommendations.append("Set SUPERSET_TOKEN for API audit coverage")

    # Calculate result
    result.checks = checks
    result.pass_count = sum(1 for c in checks if c.status == "PASS")
    result.error_count = sum(1 for c in checks if c.status == "FAIL")
    result.latency_avg_ms = round(sum(latencies) / len(latencies), 2) if latencies else None

    if result.error_count == 0 and result.pass_count > 0:
        result.status = "PASS"
        result.access_level = "ok"
    elif result.pass_count > 0:
        result.status = "PARTIAL"
        result.access_level = "insufficient"
    else:
        result.status = "FAIL"
        result.access_level = "insufficient"

    result.evidence = {
        "superset_url": superset_url,
        "token_set": bool(token)
    }

    save_result(result, output_file)


def run_health_check(client, base_url):
    """Check Superset health endpoint."""
    check = CheckResult(
        name="health_check",
        integration="superset",
        description="Check Superset health endpoint",
        status="FAIL"
    )

    try:
        resp = client.request("GET", f"{base_url}/health")
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            check.status = "PASS"
            check.evidence = {"healthy": True}
        else:
            # Try /healthcheck
            resp2 = client.request("GET", f"{base_url}/healthcheck")
            if resp2["status_code"] == 200:
                check.status = "PASS"
                check.latency_ms = resp2["latency_ms"]
                check.evidence = {"endpoint": "/healthcheck", "healthy": True}
            else:
                check.error = f"Health check failed: {resp['status_code']}"

    except Exception as e:
        check.error = str(e)

    return check


def run_login_check(client, base_url):
    """Check login page accessibility."""
    check = CheckResult(
        name="login_page",
        integration="superset",
        description="Check login page accessibility",
        status="FAIL"
    )

    try:
        resp = client.request("GET", f"{base_url}/login/")
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] in [200, 302]:
            check.status = "PASS"
            check.evidence = {"login_accessible": True}
        else:
            check.error = f"Login page returned: {resp['status_code']}"

    except Exception as e:
        check.error = str(e)

    return check


def run_api_check(client, base_url, token):
    """Check Superset API with token."""
    check = CheckResult(
        name="api_auth",
        integration="superset",
        description="Check API authentication",
        status="FAIL"
    )

    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.request("GET", f"{base_url}/api/v1/database/", headers=headers)
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            check.status = "PASS"
            body = resp.get("body", {})
            databases = body.get("result", [])
            check.evidence = {
                "database_count": body.get("count", len(databases)),
                "database_names": [db.get("database_name") for db in databases[:5] if isinstance(db, dict)]
            }
        elif resp["status_code"] == 401:
            check.error = "Token invalid or expired"
        else:
            check.error = f"API check failed: {resp['status_code']}"

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

    print(f"Superset audit: {result.status} ({result.pass_count} passed, {result.error_count} failed)")


if __name__ == "__main__":
    main()
