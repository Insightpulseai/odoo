# Plan: Azure WAF Parity — 78 → 85+

## Workspace Scope

All changes are scoped to the `insightpulseai-prod` workspace.
Workspace definition lives in `Insightpulseai/ipai-ops-platform` (not this repo).
This repo consumes workspace context via `IPAI_WORKSPACE` env var.

## PRD Classification

This is a **shared infrastructure** change (monitoring, auth, backup, CDN).
PRD is **required** per org rules: breaking it breaks >= 2 repos.
PRD: `spec/azure-reference-architecture/prd.md`

## Execution Order

```
Phase A: Spec bundle ........................ [shipped]
Phase B: Observability stack ................ [shipped]
Phase C: CDN + static asset caching ......... [shipped]
Phase D: Auth hardening ..................... [shipped]
Phase E: Backup verification ................ [shipped]
Phase F: CI + evidence ...................... [shipped]
Phase G: Ops baseline (SOPS, S3, Keycloak) .. [shipped]
Phase H: PRD enforcement CI ................. [next]
Phase I: WAF rescore ........................ [after deploy]
```

## Phase B: Observability

### Files
- `infra/monitoring/prometheus/prometheus.yml` — scrape config (workspace-labeled)
- `infra/monitoring/grafana/provisioning/datasources/prometheus.yml` — auto-provision
- `infra/monitoring/grafana/provisioning/dashboards/dashboard.yml` — provider
- `infra/monitoring/grafana/provisioning/dashboards/odoo-overview.json` — dashboard
- `infra/monitoring/alerting/rules.yml` — alert rules (6 alerts)
- `infra/monitoring/docker-compose.monitoring.yml` — compose overlay (512MB budget)
- `ops/observability/docker-compose.yml` — standalone stack with Loki
- `scripts/verify_monitoring.sh` — verification

### Targets
- `odoo-core:8069/web/health` (Odoo)
- `postgres-exporter:9187/metrics` (PG stats)
- `node-exporter:9100/metrics` (host metrics)
- `cadvisor:8080/healthz` (container metrics)
- `prometheus:9090/-/healthy` (self)

## Phase C: CDN

### Files
- `infra/cloudflare/cloudflare-cache-rules.json`
- `scripts/verify_cdn.sh`

### Rules
- Cache: `/web/static/*`, `/web/image/*`, `*.js`, `*.css`, `*.png`, `*.jpg`, `*.woff2`
- Bypass: `/web/login`, `/web/session/*`, `/longpolling/*`, `/xmlrpc/*`, `/web/webclient/*`

## Phase D: Auth

### Files
- `addons/ipai/ipai_auth_oidc/__manifest__.py`
- `addons/ipai/ipai_auth_oidc/__init__.py`
- `addons/ipai/ipai_auth_oidc/data/auth_provider_data.xml`
- `ops/idp/keycloak/docker-compose.yml` — self-hosted Keycloak
- `scripts/verify_auth.sh`

### Dependencies
- Odoo `auth_totp` (TOTP MFA) — ships with Odoo CE 16+
- Keycloak 25 (self-hosted, `ops/idp/keycloak/`)
- Provider credentials from env (never hardcoded)

## Phase E: Backup

### Files
- `ops/backup/pg_backup_to_s3.sh` — dump PG to DO Spaces
- `ops/backup/pg_restore_from_s3.sh` — restore from S3
- `ops/backup/install_cron.sh` — install daily cron
- `scripts/backup_verify.sh` — check freshness + size

### Logic
1. Check `pg_dump` in S3 or local filesystem
2. Verify age < 25 hours
3. Verify size > 1MB (not empty)
4. Exit 0 (pass) or 1 (fail)

## Phase F: CI

### Files
- `.github/workflows/azure-waf-parity.yml` — static + runtime checks
- `.github/workflows/platform-guardrails.yml` — secret hygiene
- `docs/evidence/TEMPLATE_azure_waf_rescore.md` — rescore template

### Triggers
- Push to `main` (path-filtered)
- Weekly schedule (Sunday 02:00 UTC)
- Manual dispatch

## Phase G: Ops Baseline

### Files
- `ops/secrets/.sops.yaml` — SOPS encryption config (age backend)
- `ops/observability/` — standalone Prometheus + Loki + Grafana
- `ops/idp/keycloak/` — self-hosted Keycloak SSO
- `.gitignore` — blocks `ops/secrets/age-key.txt`

## Phase H: PRD Enforcement CI (next)

### Files
- `.github/workflows/prd-enforcement.yml` — block PRs missing PRDs
- `scripts/ci/check_prd_linkage.sh` — enforcement script

### Rules
- PRs that add root-level folders must link a PRD
- PRs that add `spec/<slug>/` must include `prd.md`
- PRs that modify `addons/ipai/ipai_*/__manifest__.py` must reference spec

## Phase I: WAF Rescore (after deploy)

1. Deploy monitoring stack to `erp.insightpulseai.com`
2. Apply Cloudflare cache rules
3. Install `ipai_auth_oidc` module
4. Run all verify scripts
5. Fill in `docs/evidence/TEMPLATE_azure_waf_rescore.md`
6. Update `scorecard.json` with new scores

## Projected Impact

| Pillar | Before | After | Delta |
|--------|--------|-------|-------|
| Reliability | 82 | 85 | +3 |
| Security | 75 | 82 | +7 |
| Cost Optimization | 72 | 78 | +6 |
| Operational Excellence | 85 | 89 | +4 |
| Performance Efficiency | 76 | 83 | +7 |
| **Aggregate** | **78** | **~83-85** | **+5-7** |
