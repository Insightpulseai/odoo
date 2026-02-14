# Service Health Check Report

**Date:** 2026-02-14 13:45 UTC
**Environment:** Claude Code Web (sandboxed — no outbound network)
**Script:** `scripts/verify-service-health.sh`

## Result

Health checks could not be executed from this environment. Claude Code Web blocks all outbound HTTP/HTTPS connections. This is a platform constraint, not a service issue.

## Services Registered (from `infra/dns/subdomain-registry.yaml`)

### Production (7 active)

| # | Service | FQDN | Port | Health Endpoint | Status |
|---|---------|------|------|-----------------|--------|
| 1 | Odoo CE 19.0 | erp.insightpulseai.com | 8069 | /web/login | Unknown |
| 2 | n8n Automation | n8n.insightpulseai.com | 5678 | /healthz | Unknown |
| 3 | PaddleOCR | ocr.insightpulseai.com | 8080 | /health | Unknown |
| 4 | Auth Service | auth.insightpulseai.com | 3000 | /.well-known/openid-configuration | Unknown |
| 5 | MCP Gateway | mcp.insightpulseai.com | CNAME | /healthz | Unknown |
| 6 | Apache Superset | superset.insightpulseai.com | 8088 | /health | Unknown |
| 7 | WWW Redirect | www.insightpulseai.com | 80 | / | Unknown |

### Staging (7 active)

| # | Service | FQDN | Health Endpoint |
|---|---------|------|-----------------|
| 1 | stage-erp | stage-erp.insightpulseai.com | /web/login |
| 2 | stage-n8n | stage-n8n.insightpulseai.com | /healthz |
| 3 | stage-ocr | stage-ocr.insightpulseai.com | /health |
| 4 | stage-auth | stage-auth.insightpulseai.com | /.well-known/openid-configuration |
| 5 | stage-mcp | stage-mcp.insightpulseai.com | /healthz |
| 6 | stage-superset | stage-superset.insightpulseai.com | /health |
| 7 | stage-api | stage-api.insightpulseai.com | /api/health |

### Planned (not yet deployed)

| Service | FQDN | Port |
|---------|------|------|
| API Gateway | api.insightpulseai.com | 8000 |

### Deprecated

| Service | Removed |
|---------|---------|
| Affine | 2026-02-09 |

## Changes Shipped

1. **`scripts/verify-service-health.sh`** — Rewritten to cover all 14 active subdomains (was only 6). Added `--staging`, `--all`, `--json`, `--quiet` flags. Added DNS resolution checks and deprecated domain verification.
2. **`.github/workflows/service-health-check.yml`** — New CI workflow running every 4 hours with manual dispatch, JSON artifact output, n8n webhook alerting on failures.

## How to Run

```bash
# From the DO droplet or any host with network access:
./scripts/verify-service-health.sh              # production only (default)
./scripts/verify-service-health.sh --all        # production + staging
./scripts/verify-service-health.sh --staging    # staging only
./scripts/verify-service-health.sh --json       # JSON output for automation
./scripts/verify-service-health.sh --all --json # everything, machine-readable
```

Or trigger via GitHub Actions: **Actions → Service Health Check (All Services) → Run workflow**
