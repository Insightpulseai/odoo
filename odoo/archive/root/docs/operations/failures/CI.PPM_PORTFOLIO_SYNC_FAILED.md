# Runbook: CI.PPM_PORTFOLIO_SYNC_FAILED

**Severity**: High
**HTTP Status**: n/a (CI failure)
**Retryable**: Yes

## Symptoms

`.github/workflows/ppm-portfolio-sync.yml` fails with a non-200 response from
`ops-ppm-rollup`, or the Python parse step fails on `ssot/ppm/portfolio.yaml`.

```
::error::ops-ppm-rollup returned HTTP 500 — failure mode: CI.PPM_PORTFOLIO_SYNC_FAILED
```

## Root Causes

1. `ops-ppm-rollup` Edge Function is not deployed or crashed.
2. `SUPABASE_URL` or `SUPABASE_SERVICE_ROLE_KEY` GitHub Secret missing/expired.
3. `ssot/ppm/portfolio.yaml` has a YAML syntax error or missing `initiatives` key.
4. The `ops.ppm_initiatives` migration (20260302000030) has not been applied.

## Remediation

```bash
# 1. Check the workflow run logs
gh run view --log-failed --repo Insightpulseai/odoo

# 2. Validate the YAML locally
python3 -c "import yaml; d=yaml.safe_load(open('ssot/ppm/portfolio.yaml')); print(len(d['initiatives']), 'initiatives')"

# 3. Test the Edge Function manually
curl -X POST "$SUPABASE_URL/functions/v1/ops-ppm-rollup" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"initiatives": [{"id": "INIT-001", "name": "Test"}]}'

# 4. Re-deploy if the function is stale
supabase functions deploy ops-ppm-rollup

# 5. Trigger a dry-run to validate without POSTing
gh workflow run ppm-portfolio-sync.yml \
  --repo Insightpulseai/odoo \
  -f dry_run=true

# 6. Trigger a full sync after fixes
gh workflow run ppm-portfolio-sync.yml --repo Insightpulseai/odoo
```

## Prevention

Dry-run the workflow on every PR that touches `ssot/ppm/portfolio.yaml`.
Add a YAML syntax check as a pre-push hook or linter step.
