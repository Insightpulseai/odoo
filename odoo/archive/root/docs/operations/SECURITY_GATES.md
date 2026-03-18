# Security Gates Runbook

**SSOT policy**: `ssot/security/vuln_policy.yaml`
**Snapshot**: `reports/security/github_alerts_snapshot.json`
**CI workflow**: `.github/workflows/security-alerts-snapshot.yml`

---

## What the gate does

1. **Daily + on PRs**: Pulls open Dependabot + Code Scanning alert counts from GitHub.
2. **Writes snapshot**: `reports/security/github_alerts_snapshot.json` (auditable, tracks drift).
3. **Compares against policy**: `ssot/security/vuln_policy.yaml` defines thresholds per severity.
4. **Fails CI** if `critical` or `high` (Dependabot) / `error` (Code Scanning) exceed thresholds without a valid, non-expired exception.
5. **Posts PR comment** with a severity breakdown table.

---

## How to add an exception

When a vulnerability cannot be fixed immediately, add a time-bounded exception to `ssot/security/vuln_policy.yaml`:

```yaml
exceptions:
  - id: EX-NNNN                      # unique, sequential
    scope: dependabot                 # dependabot | code_scanning
    severity: high                   # maps to severity in thresholds block
    count_at_creation: 3             # number of alerts at time of exception
    expires_on: "2026-04-30"         # REQUIRED — max 90 days
    tracking_issue: "GH#1234"        # REQUIRED — GitHub Issue or PR
    rationale: >
      Upstream fix pending; mitigated by WAF rule X.
      Will re-evaluate when upstream releases patch.
```

**Rules**:
- `expires_on` is required and enforced at CI evaluation time.
- An expired exception is treated as **no exception** — CI will fail.
- `tracking_issue` must link to a real issue or PR.
- Never delete an exception entry; mark it resolved with a `resolved_on` field instead.

---

## How to investigate and fix

### Dependabot (SCA)

```bash
# List open critical/high
gh api "repos/Insightpulseai/odoo/dependabot/alerts?state=open&severity=critical,high" \
  | jq '.[] | {id: .number, pkg: .dependency.package.name, sev: .security_advisory.severity}'

# Auto-fix npm/pnpm transitive deps
pnpm audit --fix

# Auto-fix Python
pip-audit --fix
```

### Code Scanning (SAST)

```bash
# List open error-severity
gh api "repos/Insightpulseai/odoo/code-scanning/alerts?state=open&severity=error" \
  | jq '.[] | {id: .number, rule: .rule.id, file: .most_recent_instance.location.path}'

# Dismiss as false positive (requires justification)
gh api -X PATCH "repos/Insightpulseai/odoo/code-scanning/alerts/<ID>" \
  -f state=dismissed -f dismissed_reason=false_positive \
  -f dismissed_comment="<reason>"
```

### Regenerate snapshot manually

```bash
GITHUB_TOKEN="$(gh auth token)" \
  python3 scripts/security/export_github_alerts_snapshot.py
```

---

## Severity mapping

| GitHub scale | Threshold key | Blocks CI? |
|---|---|---|
| Dependabot: critical | `dependabot.critical` | ✅ Yes |
| Dependabot: high | `dependabot.high` | ✅ Yes |
| Dependabot: medium | `dependabot.medium` | ❌ No (logged) |
| Dependabot: low | `dependabot.low` | ❌ No (logged) |
| Code scanning: error | `code_scanning.error` | ✅ Yes |
| Code scanning: warning | `code_scanning.warning` | ❌ No (logged) |
| Code scanning: note | `code_scanning.note` | ❌ No (logged) |

---

## Current exceptions (summary)

| ID | Scope | Severity | Count | Expires | Tracking |
|----|-------|----------|-------|---------|----------|
| EX-0001 | dependabot | critical | 4 | 2026-03-31 | Dependabot dashboard |
| EX-0002 | dependabot | high | 62 | 2026-04-30 | Dependabot dashboard |
| EX-0003 | code_scanning | error | 43 | 2026-04-30 | Code Scanning dashboard |

All three are **baseline exceptions** covering alerts present before this policy was introduced (2026-02-27).
Each must be resolved (count → 0) or individually re-excepted before their expiry date.
