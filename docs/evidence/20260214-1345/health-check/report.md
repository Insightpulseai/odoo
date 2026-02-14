# Service Health Check Report

**Date:** 2026-02-14
**Script:** `scripts/verify-service-health.sh`

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌──────────────┐
│  Claude Web      │     │  GitHub CI   │     │  DO Droplet  │
│  (authors IaC)   │     │  (edge probe)│     │  (origin)    │
│                  │     │              │     │              │
│  - Terraform     │     │  --mode edge │     │  --mode      │
│  - Scripts       │────▶│  + UA header │────▶│    origin    │
│  - Workflows     │     │  + Token hdr │     │  127.0.0.1:* │
└─────────────────┘     └──────────────┘     └──────────────┘
                               │
                        Cloudflare WAF
                        (bypass rule:
                         UA + token +
                         health paths)
```

## Execution Surfaces

| Surface | Purpose | Mode |
|---------|---------|------|
| DO Droplet (178.128.112.214) | Origin health — authoritative | `--mode origin` |
| GitHub Actions CI | Edge health — through Cloudflare | `--mode edge` |
| Claude Code Web | Authors the system, never executes probes | N/A |

## Services (from `infra/dns/subdomain-registry.yaml`)

### Production (6 probed)

| Service | Origin Port | Health Path | Edge FQDN |
|---------|-------------|-------------|-----------|
| erp | 8069 | /web/health | erp.insightpulseai.com |
| n8n | 5678 | /healthz | n8n.insightpulseai.com |
| ocr | 8080 | /health | ocr.insightpulseai.com |
| auth | 3000 | /.well-known/openid-configuration | auth.insightpulseai.com |
| superset | 8088 | /health | superset.insightpulseai.com |
| mcp | CNAME (edge only) | /healthz | mcp.insightpulseai.com |

### Staging (7 probed)

| Service | Origin Port | Health Path | Edge FQDN |
|---------|-------------|-------------|-----------|
| stage-erp | 8069 | /web/health | stage-erp.insightpulseai.com |
| stage-n8n | 5678 | /healthz | stage-n8n.insightpulseai.com |
| stage-ocr | 8080 | /health | stage-ocr.insightpulseai.com |
| stage-auth | 3000 | /.well-known/openid-configuration | stage-auth.insightpulseai.com |
| stage-superset | 8088 | /health | stage-superset.insightpulseai.com |
| stage-mcp | CNAME (edge only) | /healthz | stage-mcp.insightpulseai.com |
| stage-api | 8000 | /api/health | stage-api.insightpulseai.com |

## WAF Bypass Design

Cloudflare WAF bypass rule (Terraform, narrowly scoped):

- **Condition 1:** `User-Agent` contains `healthcheck/`
- **Condition 2:** `X-Healthcheck-Token` equals shared secret
- **Condition 3:** Path is one of: `/healthz`, `/health`, `/web/health`, `/api/health`, `/.well-known/openid-configuration`
- **Action:** Skip current WAF ruleset (no blanket IP bypass)

## Changes Shipped

1. **`scripts/verify-service-health.sh`** — Full rewrite with `--mode origin|edge|all`, declarative SERVICES array, token-authenticated edge probes.
2. **`.github/workflows/service-health-check.yml`** — CI runs edge checks every 15min with `HEALTHCHECK_TOKEN` + `HEALTHCHECK_UA`.
3. **`infra/cloudflare/modules/healthcheck-waf-bypass/`** — Terraform module for narrowly-scoped WAF skip rule.
4. **`infra/cloudflare/envs/prod/main.tf`** — Wired WAF bypass module.
5. **`infra/cloudflare/envs/prod/variables.tf`** — Added `healthcheck_token` variable.

## Setup Required

1. Generate token: `openssl rand -hex 32`
2. Set in Terraform: `healthcheck_token` in `terraform.tfvars`
3. Set in GitHub: `HEALTHCHECK_TOKEN` secret
4. Apply Terraform: `cd infra/cloudflare/envs/prod && terraform apply`

## Verification Checklist

- [ ] From droplet: `--mode origin` returns pass for all services
- [ ] From GitHub Actions: `--mode edge` returns pass (no 403)
- [ ] WAF bypass scoped to health paths + token only
- [ ] No other endpoints become reachable as a side effect
- [ ] Failures produce actionable output (service, URL, status)
