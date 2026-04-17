# Judge: runtime-safety-judge

## Scope

Validates runtime environment safety before and after deployment.

## Verdict: PASS when

- `list_db = False` enforced in production
- Health probes returning 200
- DB backup exists within last 24h
- No unresolved container restart loops
- SMTP configured (not open relay)

## Verdict: FAIL when

- `list_db = True` in production (P0 security)
- Health probe failing
- No recent backup
- Container in crash loop
- SMTP misconfigured or absent
