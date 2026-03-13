#!/usr/bin/env python3
"""
Vercel Integration Audit Check

Validates:
- Token authentication
- Project listing
- Deployment listing
- Production domain health
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import HTTPClient, CheckResult, IntegrationResult, check_env_vars, redact_dict


def main():
    output_file = sys.argv[1] if len(sys.argv) > 1 else "vercel_audit.json"

    env_check = check_env_vars(
        required=["VERCEL_TOKEN"],
        optional=["VERCEL_TEAM_ID", "VERCEL_PROJECT_NAME"]
    )

    result = IntegrationResult(
        name="Vercel",
        status="SKIP",
        risk_tier="high",
        checks=[],
        recommendations=[]
    )

    if env_check["missing_required"]:
        result.status = "SKIP"
        result.recommendations.append(f"Set required env vars: {', '.join(env_check['missing_required'])}")
        result.evidence = {"missing_required": env_check["missing_required"]}
        save_result(result, output_file)
        return

    client = HTTPClient(timeout=30)
    token = os.environ["VERCEL_TOKEN"]
    team_id = os.environ.get("VERCEL_TEAM_ID")

    checks = []
    latencies = []
    user_info = {}

    # Check 1: Auth test
    check, user_info = run_auth_check(client, token)
    checks.append(check)
    if check.latency_ms:
        latencies.append(check.latency_ms)

    # Check 2: List projects
    check = run_projects_check(client, token, team_id)
    checks.append(check)
    if check.latency_ms:
        latencies.append(check.latency_ms)

    # Check 3: List deployments
    check = run_deployments_check(client, token, team_id)
    checks.append(check)
    if check.latency_ms:
        latencies.append(check.latency_ms)

    # Check 4: Production domain health
    check = run_production_health_check(client)
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
        "user_email": user_info.get("email"),
        "team_id": team_id
    }

    save_result(result, output_file)


def run_auth_check(client, token):
    """Validate token authentication."""
    check = CheckResult(
        name="auth_test",
        integration="vercel",
        description="Validate token authentication",
        status="FAIL"
    )
    user_info = {}

    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.request("GET", "https://api.vercel.com/v2/user", headers=headers)
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            check.status = "PASS"
            body = resp.get("body", {}).get("user", {})
            user_info = {"email": body.get("email"), "id": body.get("id")}
            check.evidence = {
                "user_id": body.get("id"),
                "user_email": body.get("email"),
                "user_name": body.get("name")
            }
        else:
            check.error = f"Auth failed: {resp['status_code']}"

    except Exception as e:
        check.error = str(e)

    return check, user_info


def run_projects_check(client, token, team_id=None):
    """List Vercel projects."""
    check = CheckResult(
        name="list_projects",
        integration="vercel",
        description="List Vercel projects",
        status="FAIL"
    )

    try:
        headers = {"Authorization": f"Bearer {token}"}
        url = "https://api.vercel.com/v9/projects?limit=10"
        if team_id:
            url += f"&teamId={team_id}"

        resp = client.request("GET", url, headers=headers)
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            check.status = "PASS"
            body = resp.get("body", {})
            projects = body.get("projects", [])
            check.evidence = {
                "project_count": len(projects),
                "project_names": [p.get("name") for p in projects[:10]]
            }
        else:
            check.error = f"Projects list failed: {resp['status_code']}"

    except Exception as e:
        check.error = str(e)

    return check


def run_deployments_check(client, token, team_id=None):
    """List recent deployments."""
    check = CheckResult(
        name="list_deployments",
        integration="vercel",
        description="List recent deployments",
        status="FAIL"
    )

    try:
        headers = {"Authorization": f"Bearer {token}"}
        url = "https://api.vercel.com/v6/deployments?limit=5"
        if team_id:
            url += f"&teamId={team_id}"

        resp = client.request("GET", url, headers=headers)
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            check.status = "PASS"
            body = resp.get("body", {})
            deployments = body.get("deployments", [])
            check.evidence = {
                "deployment_count": len(deployments),
                "recent_deployments": [
                    {
                        "name": d.get("name"),
                        "state": d.get("state"),
                        "created": d.get("created")
                    }
                    for d in deployments[:5]
                ]
            }
        else:
            check.error = f"Deployments list failed: {resp['status_code']}"

    except Exception as e:
        check.error = str(e)

    return check


def run_production_health_check(client):
    """Check production domain health."""
    check = CheckResult(
        name="production_health",
        integration="vercel",
        description="Check production domain health (erp.insightpulseai.com)",
        status="FAIL"
    )

    try:
        # This checks the Odoo domain which may be on DO, not Vercel
        # But it's part of the overall deployment verification
        resp = client.request("GET", "https://erp.insightpulseai.com/web/health")
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            check.status = "PASS"
            check.evidence = {"domain": "erp.insightpulseai.com", "healthy": True}
        else:
            check.error = f"Production health check returned: {resp['status_code']}"

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

    print(f"Vercel audit: {result.status} ({result.pass_count} passed, {result.error_count} failed)")


if __name__ == "__main__":
    main()
