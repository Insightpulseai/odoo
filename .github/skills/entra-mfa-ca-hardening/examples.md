# entra-mfa-ca-hardening -- Worked Examples

## Example 1: Baseline Conditional Access Policy (JSON)

```json
{
  "displayName": "Require MFA for all users",
  "state": "enabledForReportingButNotEnforced",
  "conditions": {
    "users": {
      "includeUsers": ["All"]
    },
    "applications": {
      "includeApplications": ["All"]
    },
    "clientAppTypes": ["browser", "mobileAppsAndDesktopClients"]
  },
  "grantControls": {
    "operator": "OR",
    "builtInControls": ["mfa"]
  }
}
```

Notes:
- Start with `enabledForReportingButNotEnforced` (report-only) to audit impact
  before enforcement.
- Switch to `enabled` after a 7-day report-only observation period.
- Requires Entra ID P1 license.

## Example 2: Admin-Only MFA Policy (Security Defaults alternative)

If P1 is not yet licensed, Security Defaults enforces MFA for admin roles only.
Document this as an interim state:

```json
{
  "displayName": "Security Defaults -- MFA for admin roles",
  "state": "enabled",
  "note": "Security Defaults auto-enforces MFA for Global Admin, Security Admin, etc. No custom CA policies available without P1.",
  "conditions": {
    "users": { "includeRoles": ["62e90394-69f5-4237-9190-012177145e10"] }
  },
  "grantControls": {
    "builtInControls": ["mfa"]
  }
}
```

## Example 3: MCP Query Sequence

```
Step 1: microsoft_docs_search("Entra ID Security Defaults MFA enforcement")
Result: Security Defaults requires MFA registration for all users, enforces
        MFA for admin roles, blocks legacy auth. Free tier. Cannot customize.

Step 2: microsoft_docs_search("Entra ID Conditional Access policy MFA require all users")
Result: CA policies allow granular control -- per-app, per-user-group,
        per-location, per-device-state. Requires Entra ID P1 ($6/user/month).

Step 3: microsoft_docs_search("Entra ID P1 license Conditional Access comparison")
Result: P1 adds: CA policies, risk-based CA (with P2), named locations,
        terms of use, session controls. Security Defaults is all-or-nothing.
```

## Example 4: Go-Live Checklist MFA Section

```markdown
## Identity -- MFA Enforcement

- [ ] Confirm Security Defaults is ON in Entra portal (or CA policies active)
- [ ] Verify all admin accounts have completed MFA registration
- [ ] Test MFA challenge for Odoo ERP access via Azure Front Door
- [ ] Test MFA challenge for Azure Portal access
- [ ] Confirm legacy authentication protocols are blocked
- [ ] Document exception list (service accounts excluded from MFA) with justification
- [ ] If using CA policies: confirm report-only period completed with < 5% block rate
```

## Example 5: Entra Token Validation in Middleware

```python
import jwt
from jwt import PyJWKClient

ENTRA_TENANT_ID = os.getenv("ENTRA_TENANT_ID")
ENTRA_CLIENT_ID = os.getenv("ENTRA_CLIENT_ID")
JWKS_URL = f"https://login.microsoftonline.com/{ENTRA_TENANT_ID}/discovery/v2.0/keys"

jwks_client = PyJWKClient(JWKS_URL)

def validate_entra_token(token: str) -> dict:
    """Validate an Entra ID JWT token."""
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    payload = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=ENTRA_CLIENT_ID,
        issuer=f"https://login.microsoftonline.com/{ENTRA_TENANT_ID}/v2.0",
    )
    return payload
```
