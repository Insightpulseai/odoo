"""
Mailgun Integration Check with Zoho Coexistence Validation

This check validates:
1. MAILGUN_DOMAIN must be mg.insightpulseai.com (subdomain, not root)
2. Root MX must be Zoho (mx.zoho.com / mx2.zoho.com / mx3.zoho.com)
3. Root SPF must include both zohomail.com AND mailgun.org
4. Subdomain (mg.) SPF must include Mailgun
5. DMARC record must exist
6. Mailgun API must be reachable (if credentials provided)
"""

import os
import sys
import re
import base64

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.audit.lib import (
    ok, fail, warn, skip, redact,
    http_get, run_cmd, dig_txt, dig_mx,
    has_secret, get_secret
)


# Canonical configuration
ROOT_DOMAIN = os.getenv("ROOT_DOMAIN", "insightpulseai.com").strip()
EXPECTED_MG_DOMAIN = os.getenv("EXPECTED_MG_DOMAIN", f"mg.{ROOT_DOMAIN}").strip()

# Expected DNS values
ZOHO_MX_RECORDS = ["mx.zoho.com", "mx2.zoho.com", "mx3.zoho.com"]
REQUIRED_SPF_INCLUDES = ["include:zohomail.com", "include:mailgun.org"]


def run():
    """Execute Mailgun + Zoho coexistence checks."""
    results = []
    domain = get_secret("MAILGUN_DOMAIN")
    api_key = get_secret("MAILGUN_API_KEY")

    # =========================================================================
    # Check 1: MAILGUN_DOMAIN must match expected subdomain
    # =========================================================================
    if domain:
        if domain != EXPECTED_MG_DOMAIN:
            # HARD FAIL: Domain mismatch is a configuration error
            return fail("mailgun_domain_mismatch", {
                "expected": EXPECTED_MG_DOMAIN,
                "actual": domain,
                "message": f"MAILGUN_DOMAIN must be '{EXPECTED_MG_DOMAIN}', not '{domain}'"
            })
        results.append(("mailgun_domain", "ok", EXPECTED_MG_DOMAIN))
    else:
        results.append(("mailgun_domain", "skip", "MAILGUN_DOMAIN not set"))

    # =========================================================================
    # Check 2: Root MX must be Zoho
    # =========================================================================
    mx_records = dig_mx(ROOT_DOMAIN).lower()

    if not mx_records:
        results.append(("root_mx", "warn", "Could not query MX records"))
    else:
        zoho_found = [z for z in ZOHO_MX_RECORDS if z in mx_records]
        if len(zoho_found) < 3:
            # WARN: MX not fully configured for Zoho
            return warn("root_mx_not_zoho", {
                "root_domain": ROOT_DOMAIN,
                "mx_records": mx_records.split("\n"),
                "expected": ZOHO_MX_RECORDS,
                "found": zoho_found,
                "message": "Root domain MX should point to Zoho for email receiving"
            })
        results.append(("root_mx", "ok", zoho_found))

    # =========================================================================
    # Check 3: Root SPF must include both Zoho and Mailgun
    # =========================================================================
    root_spf = dig_txt(ROOT_DOMAIN)

    if "v=spf1" not in root_spf:
        return warn("spf_missing", {
            "root_domain": ROOT_DOMAIN,
            "spf": root_spf or "<empty>",
            "message": "Root domain has no SPF record"
        })

    missing_includes = []
    for inc in REQUIRED_SPF_INCLUDES:
        if inc not in root_spf:
            missing_includes.append(inc)

    if missing_includes:
        return warn("spf_missing_includes", {
            "root_domain": ROOT_DOMAIN,
            "spf": root_spf,
            "missing": missing_includes,
            "message": f"Root SPF missing: {', '.join(missing_includes)}"
        })

    results.append(("root_spf", "ok", root_spf))

    # =========================================================================
    # Check 4: DMARC record must exist
    # =========================================================================
    dmarc = dig_txt(f"_dmarc.{ROOT_DOMAIN}")

    if "v=DMARC1" not in dmarc:
        return warn("dmarc_missing", {
            "root_domain": ROOT_DOMAIN,
            "dmarc": dmarc or "<empty>",
            "message": "DMARC record missing or invalid"
        })

    results.append(("dmarc", "ok", dmarc))

    # =========================================================================
    # Check 5: Subdomain SPF must include Mailgun
    # =========================================================================
    mg_spf = dig_txt(EXPECTED_MG_DOMAIN)

    if "v=spf1" not in mg_spf:
        return warn("mg_spf_missing", {
            "mg_domain": EXPECTED_MG_DOMAIN,
            "spf": mg_spf or "<empty>",
            "message": f"Mailgun subdomain {EXPECTED_MG_DOMAIN} has no SPF record"
        })

    if "include:mailgun.org" not in mg_spf:
        return warn("mg_spf_invalid", {
            "mg_domain": EXPECTED_MG_DOMAIN,
            "spf": mg_spf,
            "message": "Mailgun subdomain SPF should include mailgun.org"
        })

    results.append(("mg_spf", "ok", mg_spf))

    # =========================================================================
    # Check 6: Mailgun API connectivity (if credentials provided)
    # =========================================================================
    if not api_key or not domain:
        results.append(("mailgun_api", "skip", "Credentials not provided"))
        # Return success with DNS checks only
        return ok("mailgun_dns_checks_passed", {
            "checks": results,
            "root_domain": ROOT_DOMAIN,
            "mg_domain": EXPECTED_MG_DOMAIN
        })

    # Validate API access
    auth_header = base64.b64encode(f"api:{api_key}".encode()).decode()
    response = http_get(
        f"https://api.mailgun.net/v3/{domain}",
        headers={"Authorization": f"Basic {auth_header}"},
        timeout=10
    )

    if not response["success"]:
        if response["status_code"] == 401:
            return fail("mailgun_auth_failed", {
                "domain": domain,
                "api_key": redact(api_key),
                "error": "Authentication failed - check API key"
            })
        elif response["status_code"] == 404:
            return fail("mailgun_domain_not_found", {
                "domain": domain,
                "error": f"Domain '{domain}' not found in Mailgun account"
            })
        else:
            return warn("mailgun_api_error", {
                "domain": domain,
                "status_code": response["status_code"],
                "error": response.get("error", "Unknown error")
            })

    results.append(("mailgun_api", "ok", domain))

    # All checks passed
    return ok("mailgun_full_check_passed", {
        "checks": results,
        "root_domain": ROOT_DOMAIN,
        "mg_domain": domain,
        "api_key": redact(api_key)
    })


if __name__ == "__main__":
    import json
    result = run()
    print(json.dumps(result, indent=2))
