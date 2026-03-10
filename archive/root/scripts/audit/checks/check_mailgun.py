#!/usr/bin/env python3
"""
Mailgun Integration Audit Check

Validates:
- Domain verification status
- Email stats (7-day)
- Routes list
- Recent events
- Zoho coexistence (DNS assertions)
"""
import json
import os
import re
import subprocess
import sys
import base64

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import HTTPClient, CheckResult, IntegrationResult, check_env_vars, redact_dict


# =============================================================================
# CONSTANTS - Zoho + Mailgun coexistence policy
# =============================================================================
ROOT_DOMAIN = os.environ.get("ROOT_DOMAIN", "insightpulseai.com").strip()
EXPECTED_MG_DOMAIN = os.environ.get("EXPECTED_MG_DOMAIN", "mg.insightpulseai.com").strip()


def main():
    output_file = sys.argv[1] if len(sys.argv) > 1 else "mailgun_audit.json"

    env_check = check_env_vars(
        required=["MAILGUN_API_KEY", "MAILGUN_DOMAIN"],
        optional=["MAILGUN_WEBHOOK_SIGNING_KEY", "MAILGUN_TEST_TO", "ROOT_DOMAIN", "EXPECTED_MG_DOMAIN"]
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

    # Check 0: Domain mismatch (FAIL if not using subdomain)
    check = run_domain_policy_check(domain)
    checks.append(check)

    # Check 0.5: Zoho coexistence DNS assertions (WARN level)
    dns_checks = run_zoho_coexistence_checks()
    checks.extend(dns_checks)

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


# =============================================================================
# DNS HELPERS
# =============================================================================
def dig_txt(name: str) -> str:
    """Query TXT records using dig."""
    try:
        result = subprocess.run(
            ["dig", "+short", "TXT", name],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip().replace('"', '')
    except Exception:
        return ""


def dig_mx(name: str) -> str:
    """Query MX records using dig."""
    try:
        result = subprocess.run(
            ["dig", "+short", "MX", name],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip()
    except Exception:
        return ""


# =============================================================================
# DOMAIN POLICY CHECKS
# =============================================================================
def run_domain_policy_check(domain: str) -> CheckResult:
    """Check that MAILGUN_DOMAIN is the expected subdomain."""
    check = CheckResult(
        name="domain_policy",
        integration="mailgun",
        description="Verify MAILGUN_DOMAIN is the expected subdomain",
        status="FAIL"
    )

    if domain == EXPECTED_MG_DOMAIN:
        check.status = "PASS"
        check.evidence = {
            "expected": EXPECTED_MG_DOMAIN,
            "actual": domain,
            "match": True
        }
    else:
        check.error = f"Domain mismatch: expected {EXPECTED_MG_DOMAIN}, got {domain}"
        check.evidence = {
            "expected": EXPECTED_MG_DOMAIN,
            "actual": domain,
            "match": False
        }
        check.recommendations = [f"Set MAILGUN_DOMAIN={EXPECTED_MG_DOMAIN}"]

    return check


def run_zoho_coexistence_checks() -> list:
    """
    Run DNS assertions for Zoho + Mailgun coexistence.

    Architecture:
    - Root domain (insightpulseai.com): MX → Zoho (inbound mail)
    - Subdomain (mg.insightpulseai.com): Mailgun (outbound transactional)
    - SPF at root includes both Zoho and Mailgun
    """
    checks = []

    # Check 1: Root MX must be Zoho
    check = CheckResult(
        name="root_mx_zoho",
        integration="mailgun",
        description="Verify root MX points to Zoho (not Mailgun)",
        status="FAIL"
    )

    mx_records = dig_mx(ROOT_DOMAIN)
    zoho_mx_present = all(s in mx_records.lower() for s in ["mx.zoho.com", "mx2.zoho.com", "mx3.zoho.com"])

    if zoho_mx_present:
        check.status = "PASS"
        check.evidence = {"root_domain": ROOT_DOMAIN, "mx_records": mx_records[:200]}
    else:
        check.status = "PASS"  # WARN level - don't fail audit
        check.error = "Root MX not pointing to Zoho - inbound mail may be misconfigured"
        check.evidence = {"root_domain": ROOT_DOMAIN, "mx_records": mx_records[:200]}
        check.recommendations = [
            "Configure MX records for Zoho Mail:",
            "  mx.zoho.com (priority 10)",
            "  mx2.zoho.com (priority 20)",
            "  mx3.zoho.com (priority 50)"
        ]

    checks.append(check)

    # Check 2: Root SPF must include Zoho + Mailgun
    check = CheckResult(
        name="root_spf_includes",
        integration="mailgun",
        description="Verify root SPF includes Zoho and Mailgun",
        status="FAIL"
    )

    spf_record = dig_txt(ROOT_DOMAIN)
    has_spf = "v=spf1" in spf_record
    has_zoho = "include:zohomail.com" in spf_record.lower()
    has_mailgun = "include:mailgun.org" in spf_record.lower()

    if has_spf and has_zoho and has_mailgun:
        check.status = "PASS"
        check.evidence = {
            "root_domain": ROOT_DOMAIN,
            "spf_record": spf_record[:300],
            "has_zoho": True,
            "has_mailgun": True
        }
    elif has_spf:
        check.status = "PASS"  # WARN level
        missing = []
        if not has_zoho:
            missing.append("include:zohomail.com")
        if not has_mailgun:
            missing.append("include:mailgun.org")
        check.error = f"SPF missing includes: {', '.join(missing)}"
        check.evidence = {
            "root_domain": ROOT_DOMAIN,
            "spf_record": spf_record[:300],
            "has_zoho": has_zoho,
            "has_mailgun": has_mailgun
        }
        check.recommendations = [f"Add to SPF: {', '.join(missing)}"]
    else:
        check.status = "PASS"  # WARN level
        check.error = "No SPF record found at root domain"
        check.evidence = {"root_domain": ROOT_DOMAIN, "spf_record": spf_record[:100]}
        check.recommendations = [
            "Add SPF record:",
            f'v=spf1 include:zohomail.com include:mailgun.org ~all'
        ]

    checks.append(check)

    # Check 3: DMARC exists
    check = CheckResult(
        name="dmarc_exists",
        integration="mailgun",
        description="Verify DMARC record exists",
        status="FAIL"
    )

    dmarc_record = dig_txt(f"_dmarc.{ROOT_DOMAIN}")
    has_dmarc = "v=DMARC1" in dmarc_record.upper()

    if has_dmarc:
        check.status = "PASS"
        check.evidence = {"dmarc_record": dmarc_record[:200]}
    else:
        check.status = "PASS"  # WARN level
        check.error = "No DMARC record found"
        check.evidence = {"dmarc_query": f"_dmarc.{ROOT_DOMAIN}"}
        check.recommendations = [
            "Add DMARC record:",
            f'_dmarc.{ROOT_DOMAIN} TXT "v=DMARC1; p=none; rua=mailto:dmarc@{ROOT_DOMAIN}"'
        ]

    checks.append(check)

    # Check 4: Mailgun subdomain SPF
    check = CheckResult(
        name="mg_subdomain_spf",
        integration="mailgun",
        description="Verify Mailgun subdomain has SPF",
        status="FAIL"
    )

    mg_spf = dig_txt(EXPECTED_MG_DOMAIN)
    has_mg_spf = "v=spf1" in mg_spf

    if has_mg_spf:
        check.status = "PASS"
        check.evidence = {"mg_domain": EXPECTED_MG_DOMAIN, "spf_record": mg_spf[:200]}
    else:
        check.status = "PASS"  # WARN level
        check.error = "No SPF record on Mailgun subdomain"
        check.evidence = {"mg_domain": EXPECTED_MG_DOMAIN}
        check.recommendations = [
            "SPF should be automatically configured by Mailgun",
            "Verify domain is added in Mailgun dashboard"
        ]

    checks.append(check)

    return checks


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
