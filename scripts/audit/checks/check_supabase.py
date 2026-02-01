#!/usr/bin/env python3
"""
Supabase Integration Audit Check

Validates:
- REST API reachability
- Anon key authentication
- Service role key authentication (if available)
- Storage bucket access
- Edge Functions list (via management API)
"""
import json
import os
import sys
from datetime import datetime, timezone

# Add parent directory to path for lib import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import HTTPClient, CheckResult, IntegrationResult, check_env_vars, redact_dict


def main():
    output_file = sys.argv[1] if len(sys.argv) > 1 else "supabase_audit.json"

    # Check environment variables
    env_check = check_env_vars(
        required=["SUPABASE_URL", "SUPABASE_ANON_KEY"],
        optional=["SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_ACCESS_TOKEN", "SUPABASE_PROJECT_REF"]
    )

    result = IntegrationResult(
        name="Supabase",
        status="SKIP",
        risk_tier="critical",
        checks=[],
        recommendations=[]
    )

    if env_check["missing_required"]:
        result.status = "SKIP"
        result.recommendations.append(f"Set required env vars: {', '.join(env_check['missing_required'])}")
        result.evidence = {"missing_required": env_check["missing_required"]}
        save_result(result, output_file)
        return

    # Initialize HTTP client
    client = HTTPClient(timeout=30)
    supabase_url = os.environ["SUPABASE_URL"].rstrip("/")
    anon_key = os.environ["SUPABASE_ANON_KEY"]
    service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    access_token = os.environ.get("SUPABASE_ACCESS_TOKEN")
    project_ref = os.environ.get("SUPABASE_PROJECT_REF")

    checks = []
    latencies = []

    # Check 1: REST API reachability
    check = run_rest_health_check(client, supabase_url)
    checks.append(check)
    if check.latency_ms:
        latencies.append(check.latency_ms)

    # Check 2: Anon key authentication
    check = run_anon_key_check(client, supabase_url, anon_key)
    checks.append(check)
    if check.latency_ms:
        latencies.append(check.latency_ms)

    # Check 3: Service role key authentication (if available)
    if service_role_key:
        check = run_service_role_check(client, supabase_url, service_role_key)
        checks.append(check)
        if check.latency_ms:
            latencies.append(check.latency_ms)

        # Check 4: Storage buckets
        check = run_storage_check(client, supabase_url, service_role_key)
        checks.append(check)
        if check.latency_ms:
            latencies.append(check.latency_ms)
    else:
        result.recommendations.append("Set SUPABASE_SERVICE_ROLE_KEY for full audit coverage")

    # Check 5: Edge Functions (via management API)
    if access_token and project_ref:
        check = run_edge_functions_check(client, access_token, project_ref)
        checks.append(check)
        if check.latency_ms:
            latencies.append(check.latency_ms)
    else:
        result.recommendations.append("Set SUPABASE_ACCESS_TOKEN and SUPABASE_PROJECT_REF for Edge Functions audit")

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
        "supabase_url": supabase_url,
        "project_ref": project_ref,
        "has_service_role": bool(service_role_key),
        "has_access_token": bool(access_token)
    }

    save_result(result, output_file)


def run_rest_health_check(client, base_url):
    """Check REST API reachability."""
    check = CheckResult(
        name="rest_api_health",
        integration="supabase",
        description="Check REST API reachability",
        status="FAIL"
    )

    try:
        resp = client.request("GET", f"{base_url}/rest/v1/")
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]
        check.rate_limit = resp.get("rate_limit")

        # 200 = success, 401 = needs auth but reachable
        if resp["status_code"] in [200, 401]:
            check.status = "PASS"
        else:
            check.error = f"Unexpected status: {resp['status_code']}"

        check.evidence = {"status_code": resp["status_code"]}
    except Exception as e:
        check.error = str(e)

    return check


def run_anon_key_check(client, base_url, anon_key):
    """Validate anon key authentication."""
    check = CheckResult(
        name="anon_key_auth",
        integration="supabase",
        description="Validate anon key authentication",
        status="FAIL"
    )

    try:
        headers = {
            "apikey": anon_key,
            "Authorization": f"Bearer {anon_key}"
        }
        resp = client.request("GET", f"{base_url}/rest/v1/", headers=headers)
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]
        check.rate_limit = resp.get("rate_limit")

        if resp["status_code"] == 200:
            check.status = "PASS"
        elif resp["status_code"] == 401:
            check.error = "Anon key rejected"
        else:
            check.error = f"Unexpected status: {resp['status_code']}"

    except Exception as e:
        check.error = str(e)

    return check


def run_service_role_check(client, base_url, service_role_key):
    """Validate service role key can access protected data."""
    check = CheckResult(
        name="service_role_auth",
        integration="supabase",
        description="Validate service role key authentication",
        status="FAIL"
    )

    try:
        headers = {
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}"
        }
        # Try to access a known table (mcp_jobs.jobs)
        resp = client.request(
            "GET",
            f"{base_url}/rest/v1/mcp_jobs.jobs?limit=1",
            headers=headers
        )
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]
        check.rate_limit = resp.get("rate_limit")

        if resp["status_code"] == 200:
            check.status = "PASS"
            check.evidence = {"rows_returned": len(resp.get("body", [])) if isinstance(resp.get("body"), list) else 0}
        elif resp["status_code"] == 404:
            # Table might not exist, try public schema
            resp2 = client.request("GET", f"{base_url}/rest/v1/", headers=headers)
            if resp2["status_code"] == 200:
                check.status = "PASS"
                check.evidence = {"note": "Auth works but mcp_jobs.jobs table not found"}
            else:
                check.error = f"Service role key not working: {resp2['status_code']}"
        else:
            check.error = f"Service role check failed: {resp['status_code']}"

    except Exception as e:
        check.error = str(e)

    return check


def run_storage_check(client, base_url, service_role_key):
    """Check storage bucket access."""
    check = CheckResult(
        name="storage_buckets",
        integration="supabase",
        description="List storage buckets",
        status="FAIL"
    )

    try:
        headers = {
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}"
        }
        resp = client.request("GET", f"{base_url}/storage/v1/bucket", headers=headers)
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            check.status = "PASS"
            buckets = resp.get("body", [])
            check.evidence = {
                "bucket_count": len(buckets) if isinstance(buckets, list) else 0,
                "bucket_names": [b.get("name") for b in buckets] if isinstance(buckets, list) else []
            }
        else:
            check.error = f"Storage API returned: {resp['status_code']}"

    except Exception as e:
        check.error = str(e)

    return check


def run_edge_functions_check(client, access_token, project_ref):
    """List Edge Functions via management API."""
    check = CheckResult(
        name="edge_functions",
        integration="supabase",
        description="List Edge Functions via management API",
        status="FAIL"
    )

    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = client.request(
            "GET",
            f"https://api.supabase.com/v1/projects/{project_ref}/functions",
            headers=headers
        )
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            check.status = "PASS"
            functions = resp.get("body", [])
            check.evidence = {
                "function_count": len(functions) if isinstance(functions, list) else 0,
                "function_names": [f.get("name") for f in functions] if isinstance(functions, list) else []
            }
        elif resp["status_code"] == 401:
            check.error = "Access token invalid or expired"
        else:
            check.error = f"Management API returned: {resp['status_code']}"

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

    print(f"Supabase audit: {result.status} ({result.pass_count} passed, {result.error_count} failed)")


if __name__ == "__main__":
    main()
