#!/usr/bin/env python3
"""
Mailgun Integration Audit Check

Validates:
- Domain verification status
- Email stats (7-day)
- Routes list
- Recent events
"""
import json
import os
import sys
import base64

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import HTTPClient, CheckResult, IntegrationResult, check_env_vars, redact_dict


def main():
    output_file = sys.argv[1] if len(sys.argv) > 1 else "mailgun_audit.json"

    env_check = check_env_vars(
        required=["MAILGUN_API_KEY", "MAILGUN_DOMAIN"],
        optional=["MAILGUN_WEBHOOK_SIGNING_KEY", "MAILGUN_TEST_TO"]
    )

    result = IntegrationResult(
        name="Mailgun",
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
    api_key = os.environ["MAILGUN_API_KEY"]
    domain = os.environ["MAILGUN_DOMAIN"]

    checks = []
    latencies = []

    # Check 1: Domain info
    check = run_domain_check(client, api_key, domain)
    checks.append(check)
    if check.latency_ms:
        latencies.append(check.latency_ms)

    # Check 2: Domain stats
    check = run_stats_check(client, api_key, domain)
    checks.append(check)
    if check.latency_ms:
        latencies.append(check.latency_ms)

    # Check 3: Routes list
    check = run_routes_check(client, api_key)
    checks.append(check)
    if check.latency_ms:
        latencies.append(check.latency_ms)

    # Check 4: Recent events
    check = run_events_check(client, api_key, domain)
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

    result.evidence = {"domain": domain}

    save_result(result, output_file)


def get_auth_header(api_key):
    """Get basic auth header for Mailgun."""
    credentials = base64.b64encode(f"api:{api_key}".encode()).decode()
    return {"Authorization": f"Basic {credentials}"}


def run_domain_check(client, api_key, domain):
    """Get domain verification status."""
    check = CheckResult(
        name="domain_info",
        integration="mailgun",
        description="Get domain verification status",
        status="FAIL"
    )

    try:
        headers = get_auth_header(api_key)
        resp = client.request(
            "GET",
            f"https://api.mailgun.net/v3/domains/{domain}",
            headers=headers
        )
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            check.status = "PASS"
            body = resp.get("body", {}).get("domain", {})
            check.evidence = {
                "domain": body.get("name"),
                "state": body.get("state"),
                "type": body.get("type"),
                "smtp_password_set": bool(body.get("smtp_password")),
                "spam_action": body.get("spam_action")
            }

            # Check DNS records
            sending_dns = body.get("sending_dns_records", [])
            receiving_dns = body.get("receiving_dns_records", [])
            check.evidence["sending_dns_valid"] = all(r.get("valid") for r in sending_dns)
            check.evidence["receiving_dns_valid"] = all(r.get("valid") for r in receiving_dns)

            if not check.evidence["sending_dns_valid"]:
                check.recommendations = ["Some sending DNS records are not valid"]
        elif resp["status_code"] == 401:
            check.error = "API key invalid"
        elif resp["status_code"] == 404:
            check.error = f"Domain {domain} not found"
        else:
            check.error = f"Domain check failed: {resp['status_code']}"

    except Exception as e:
        check.error = str(e)

    return check


def run_stats_check(client, api_key, domain):
    """Get 7-day email stats."""
    check = CheckResult(
        name="domain_stats",
        integration="mailgun",
        description="Get 7-day email stats",
        status="FAIL"
    )

    try:
        headers = get_auth_header(api_key)
        resp = client.request(
            "GET",
            f"https://api.mailgun.net/v3/{domain}/stats/total?event=accepted&event=failed&event=delivered&duration=7d",
            headers=headers
        )
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            check.status = "PASS"
            body = resp.get("body", {})
            stats = body.get("stats", [])
            # Aggregate stats
            totals = {"accepted": 0, "delivered": 0, "failed": 0}
            for day in stats:
                totals["accepted"] += day.get("accepted", {}).get("total", 0)
                totals["delivered"] += day.get("delivered", {}).get("total", 0)
                totals["failed"] += day.get("failed", {}).get("total", 0)

            check.evidence = {
                "period": "7d",
                "accepted_total": totals["accepted"],
                "delivered_total": totals["delivered"],
                "failed_total": totals["failed"],
                "delivery_rate": round(totals["delivered"] / totals["accepted"] * 100, 2) if totals["accepted"] > 0 else 0
            }

            if totals["failed"] > totals["delivered"] * 0.1:  # >10% failure rate
                check.recommendations = [f"High failure rate: {totals['failed']} failed out of {totals['accepted']} accepted"]
        else:
            check.error = f"Stats check failed: {resp['status_code']}"

    except Exception as e:
        check.error = str(e)

    return check


def run_routes_check(client, api_key):
    """List email routes."""
    check = CheckResult(
        name="routes_list",
        integration="mailgun",
        description="List email routes",
        status="FAIL"
    )

    try:
        headers = get_auth_header(api_key)
        resp = client.request(
            "GET",
            "https://api.mailgun.net/v3/routes",
            headers=headers
        )
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            check.status = "PASS"
            body = resp.get("body", {})
            routes = body.get("items", [])
            check.evidence = {
                "route_count": body.get("total_count", len(routes)),
                "routes": [
                    {
                        "expression": r.get("expression"),
                        "priority": r.get("priority"),
                        "description": r.get("description")
                    }
                    for r in routes[:5]
                ]
            }
        else:
            check.error = f"Routes check failed: {resp['status_code']}"

    except Exception as e:
        check.error = str(e)

    return check


def run_events_check(client, api_key, domain):
    """Query recent events."""
    check = CheckResult(
        name="events_query",
        integration="mailgun",
        description="Query recent events",
        status="FAIL"
    )

    try:
        headers = get_auth_header(api_key)
        resp = client.request(
            "GET",
            f"https://api.mailgun.net/v3/{domain}/events?limit=10",
            headers=headers
        )
        check.http_status = resp["status_code"]
        check.latency_ms = resp["latency_ms"]

        if resp["status_code"] == 200:
            check.status = "PASS"
            body = resp.get("body", {})
            events = body.get("items", [])
            check.evidence = {
                "event_count": len(events),
                "recent_events": [
                    {
                        "event": e.get("event"),
                        "timestamp": e.get("timestamp"),
                        "recipient": e.get("recipient", "")[:20] + "..." if e.get("recipient") else None
                    }
                    for e in events[:5]
                ]
            }
        else:
            check.error = f"Events check failed: {resp['status_code']}"

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

    print(f"Mailgun audit: {result.status} ({result.pass_count} passed, {result.error_count} failed)")


if __name__ == "__main__":
    main()
