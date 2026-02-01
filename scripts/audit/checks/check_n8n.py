#!/usr/bin/env python3
"""
n8n Integration Audit Check

Validates:
- Health endpoint
- Workflow listing (if API enabled)
- Executions listing (if API enabled)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import HTTPClient, CheckResult, IntegrationResult, check_env_vars, redact_dict


def main():
    output_file = sys.argv[1] if len(sys.argv) > 1 else "n8n_audit.json"

    # n8n base URL with default
    n8n_url = os.environ.get("N8N_BASE_URL", "https://n8n.insightpulseai.net").rstrip("/")
    api_key = os.environ.get("N8N_API_KEY")

    result = IntegrationResult(
        name="n8n",
        status="SKIP",
        risk_tier="high",
        checks=[],
        recommendations=[]
    )

    client = HTTPClient(timeout=30)
    checks = []
    latencies = []

    # Check 1: Health endpoint
    check = run_health_check(client, n8n_url)
    checks.append(check)
    if check.latency_ms:
        latencies.append(check.latency_ms)

    # Check 2: Workflows (if API key available)
    if api_key:
        check = run_workflows_check(client, n8n_url, api_key)
        checks.append(check)
        if check.latency_ms:
            latencies.append(check.latency_ms)

        # Check 3: Executions
        check = run_executions_check(client, n8n_url, api_key)
        checks.append(check)
        if check.latency_ms:
            latencies.append(check.latency_ms)
    else:
        result.recommendations.append("Set N8N_API_KEY for full audit coverage (workflow/execution listing)")

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
        "n8n_url": n8n_url,
        "api_key_set": bool(api_key)
    }

    save_result(result, output_file)


def run_health_check(client, base_url):
    """Check n8n health endpoint."""
    check = CheckResult(
        name="health_check",
        integration="n8n",
        description="Check n8n health endpoint",
        status="FAIL"
    )

    try:
        # Try /healthz first (common health endpoint)
        resp = client.request("GET", f"{base_url}/healthz")
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            check.status = "PASS"
            check.evidence = {"endpoint": "/healthz", "healthy": True}
        else:
            # Try /health
            resp2 = client.request("GET", f"{base_url}/health")
            if resp2["status_code"] == 200:
                check.status = "PASS"
                check.latency_ms = resp2["latency_ms"]
                check.evidence = {"endpoint": "/health", "healthy": True}
            else:
                # Try root
                resp3 = client.request("GET", base_url)
                if resp3["status_code"] in [200, 302]:
                    check.status = "PASS"
                    check.latency_ms = resp3["latency_ms"]
                    check.evidence = {"endpoint": "/", "reachable": True}
                else:
                    check.error = f"n8n not reachable (tried /healthz, /health, /)"

    except Exception as e:
        check.error = str(e)

    return check


def run_workflows_check(client, base_url, api_key):
    """List n8n workflows."""
    check = CheckResult(
        name="workflows_list",
        integration="n8n",
        description="List n8n workflows",
        status="FAIL"
    )

    try:
        headers = {"X-N8N-API-KEY": api_key}
        resp = client.request("GET", f"{base_url}/api/v1/workflows", headers=headers)
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            check.status = "PASS"
            body = resp.get("body", {})
            workflows = body.get("data", []) if isinstance(body, dict) else body
            if isinstance(workflows, list):
                check.evidence = {
                    "workflow_count": len(workflows),
                    "workflow_names": [w.get("name") for w in workflows[:10] if isinstance(w, dict)]
                }
            else:
                check.evidence = {"note": "Unexpected response format"}
        elif resp["status_code"] == 401:
            check.error = "API key invalid or API not enabled"
        elif resp["status_code"] == 404:
            check.error = "API endpoint not found - API might not be enabled"
        else:
            check.error = f"Workflows list failed: {resp['status_code']}"

    except Exception as e:
        check.error = str(e)

    return check


def run_executions_check(client, base_url, api_key):
    """List recent n8n executions."""
    check = CheckResult(
        name="executions_list",
        integration="n8n",
        description="List recent executions",
        status="FAIL"
    )

    try:
        headers = {"X-N8N-API-KEY": api_key}
        resp = client.request("GET", f"{base_url}/api/v1/executions?limit=10", headers=headers)
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            check.status = "PASS"
            body = resp.get("body", {})
            executions = body.get("data", []) if isinstance(body, dict) else body
            if isinstance(executions, list):
                check.evidence = {
                    "execution_count": len(executions),
                    "recent_executions": [
                        {
                            "id": e.get("id"),
                            "finished": e.get("finished"),
                            "status": e.get("status")
                        }
                        for e in executions[:5] if isinstance(e, dict)
                    ]
                }
            else:
                check.evidence = {"note": "Unexpected response format"}
        elif resp["status_code"] == 401:
            check.error = "API key invalid"
        elif resp["status_code"] == 404:
            check.error = "Executions API not available"
        else:
            check.error = f"Executions list failed: {resp['status_code']}"

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

    print(f"n8n audit: {result.status} ({result.pass_count} passed, {result.error_count} failed)")


if __name__ == "__main__":
    main()
