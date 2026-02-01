#!/usr/bin/env python3
"""
DigitalOcean Integration Audit Check

Validates:
- API token authentication
- Droplet listing
- Database listing
- Droplet connectivity
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import HTTPClient, CheckResult, IntegrationResult, check_env_vars, redact_dict


def main():
    output_file = sys.argv[1] if len(sys.argv) > 1 else "digitalocean_audit.json"

    env_check = check_env_vars(
        required=["DO_API_TOKEN"],
        optional=["DO_DROPLET_ID", "DO_DATABASE_ID"]
    )

    result = IntegrationResult(
        name="DigitalOcean",
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

    client = HTTPClient(timeout=30)
    token = os.environ["DO_API_TOKEN"]

    checks = []
    latencies = []
    account_info = {}

    # Check 1: Auth test
    check, account_info = run_auth_check(client, token)
    checks.append(check)
    if check.latency_ms:
        latencies.append(check.latency_ms)

    # Check 2: List droplets
    check = run_droplets_check(client, token)
    checks.append(check)
    if check.latency_ms:
        latencies.append(check.latency_ms)

    # Check 3: List databases
    check = run_databases_check(client, token)
    checks.append(check)
    if check.latency_ms:
        latencies.append(check.latency_ms)

    # Check 4: Droplet connectivity
    check = run_droplet_connectivity_check(client)
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
        "account_email": account_info.get("email")
    }

    save_result(result, output_file)


def run_auth_check(client, token):
    """Validate API token."""
    check = CheckResult(
        name="auth_test",
        integration="digitalocean",
        description="Validate API token",
        status="FAIL"
    )
    account_info = {}

    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.request("GET", "https://api.digitalocean.com/v2/account", headers=headers)
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            check.status = "PASS"
            body = resp.get("body", {}).get("account", {})
            account_info = {"email": body.get("email")}
            check.evidence = {
                "account_email": body.get("email"),
                "droplet_limit": body.get("droplet_limit"),
                "status": body.get("status")
            }
        elif resp["status_code"] == 401:
            check.error = "API token invalid"
        else:
            check.error = f"Auth failed: {resp['status_code']}"

    except Exception as e:
        check.error = str(e)

    return check, account_info


def run_droplets_check(client, token):
    """List droplets."""
    check = CheckResult(
        name="list_droplets",
        integration="digitalocean",
        description="List droplets",
        status="FAIL"
    )

    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.request("GET", "https://api.digitalocean.com/v2/droplets", headers=headers)
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            check.status = "PASS"
            body = resp.get("body", {})
            droplets = body.get("droplets", [])
            check.evidence = {
                "droplet_count": len(droplets),
                "droplets": [
                    {
                        "name": d.get("name"),
                        "status": d.get("status"),
                        "region": d.get("region", {}).get("slug"),
                        "ip_address": d.get("networks", {}).get("v4", [{}])[0].get("ip_address") if d.get("networks", {}).get("v4") else None
                    }
                    for d in droplets[:5]
                ]
            }
        else:
            check.error = f"Droplets list failed: {resp['status_code']}"

    except Exception as e:
        check.error = str(e)

    return check


def run_databases_check(client, token):
    """List managed databases."""
    check = CheckResult(
        name="list_databases",
        integration="digitalocean",
        description="List managed databases",
        status="FAIL"
    )

    try:
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.request("GET", "https://api.digitalocean.com/v2/databases", headers=headers)
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            check.status = "PASS"
            body = resp.get("body", {})
            databases = body.get("databases", [])
            check.evidence = {
                "database_count": len(databases),
                "databases": [
                    {
                        "name": db.get("name"),
                        "engine": db.get("engine"),
                        "status": db.get("status"),
                        "region": db.get("region")
                    }
                    for db in databases[:5]
                ]
            }
        else:
            check.error = f"Databases list failed: {resp['status_code']}"

    except Exception as e:
        check.error = str(e)

    return check


def run_droplet_connectivity_check(client):
    """Check droplet connectivity."""
    check = CheckResult(
        name="droplet_connectivity",
        integration="digitalocean",
        description="Check production droplet connectivity",
        status="FAIL"
    )

    try:
        # Known production droplet IP
        droplet_ip = "178.128.112.214"
        resp = client.request("GET", f"https://{droplet_ip}/web/health")
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            check.status = "PASS"
            check.evidence = {"droplet_ip": droplet_ip, "reachable": True}
        elif resp["status_code"] in [301, 302, 400]:
            # Redirect or bad request but reachable
            check.status = "PASS"
            check.evidence = {"droplet_ip": droplet_ip, "reachable": True, "note": "Redirects or needs host header"}
        else:
            check.error = f"Droplet returned: {resp['status_code']}"

    except Exception as e:
        # SSL cert might be for domain, not IP - still consider reachable if connection worked
        if "certificate" in str(e).lower():
            check.status = "PASS"
            check.evidence = {"droplet_ip": "178.128.112.214", "reachable": True, "note": "SSL cert for domain, not IP"}
        else:
            check.error = str(e)

    return check


def save_result(result, output_file):
    """Save result to file."""
    data = result.to_dict()
    data = redact_dict(data)

    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2, default=str)

    print(f"DigitalOcean audit: {result.status} ({result.pass_count} passed, {result.error_count} failed)")


if __name__ == "__main__":
    main()
