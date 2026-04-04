# Production Verification

## Purpose

Deterministic proof that core Odoo surfaces are reachable, rendering, and secure after deployment.
Runs Playwright headless browser smoke tests and captures evidence artifacts.

## Invocation

```bash
BASE_URL=https://erp.insightpulseai.com ./automations/scripts/prod_verify_playwright.sh
```

## What it checks

| Check | Spec | Pass criteria |
|-------|------|---------------|
| Login page reachable | `prod-verify.spec.ts` | HTTP < 500, form visible, password field present |
| Static assets load | `prod-verify.spec.ts` | CSS applied, JS bundles present |
| Database selector blocked | `prod-verify.spec.ts` | `list_db=False` enforced (403/404/redirect) |
| Security headers | `prod-verify.spec.ts` | X-Frame-Options or CSP frame-ancestors, X-Content-Type-Options: nosniff |

## Evidence artifacts

All artifacts land in `docs/evidence/<YYYYMMDD-HHMM>/prod-verify/`:

```
prod-verify/
  verification.json      # Machine-readable manifest (verdict, counts, paths)
  playwright.log         # Full Playwright stdout/stderr
  screenshots/
    01-login-page.png    # Login page render proof
    02-assets-loaded.png # Static assets proof
    03-db-selector-blocked.png  # list_db enforcement proof
  test-results/          # Playwright raw test output
```

## Verification manifest schema

```json
{
  "timestamp": "20260404-1530",
  "target": "https://erp.insightpulseai.com",
  "verdict": "PASS",
  "exit_code": 0,
  "counts": { "passed": 4, "failed": 0, "screenshots": 3 },
  "artifacts": {
    "log": "docs/evidence/.../playwright.log",
    "screenshots": "docs/evidence/.../screenshots/",
    "test_results": "docs/evidence/.../test-results/"
  }
}
```

## Failure semantics

- `exit 0` = all checks passed, `verdict: "PASS"`
- `exit 1` = one or more checks failed, `verdict: "FAIL"`
- Evidence artifacts are always produced regardless of verdict
- The script never exits silently — log + manifest are always written

## Pipeline integration

Called from `.azuredevops/pipelines/odoo-test.yml` as a post-test verification step.
Runs on the same self-hosted agent pool (`ipai-private-linux`) that has browser dependencies.
Evidence is published as a pipeline artifact alongside test logs.

## Environment variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `BASE_URL` | Yes | — | Target URL to verify |
| `EVIDENCE_ROOT` | No | `docs/evidence` | Override evidence output root |
| `SKIP_INSTALL` | No | `0` | Set to `1` to skip browser install (CI with pre-cached browsers) |
