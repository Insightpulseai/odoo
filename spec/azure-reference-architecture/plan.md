# Plan: Azure WAF Parity Implementation

## Execution Order

```
Phase A: Spec bundle (this file) .............. [done]
Phase B: Observability stack .................. [Prometheus, Grafana, exporters]
Phase C: CDN + static asset caching .......... [Cloudflare rules, proxy headers]
Phase D: Auth hardening ...................... [ipai_auth_oidc module]
Phase E: Backup verification ................. [backup_verify.sh]
Phase F: CI + evidence ....................... [workflow, rescore template]
Phase G: Commit + push ....................... [single logical commit]
```

## Phase B: Observability

### Files
- `infra/monitoring/prometheus/prometheus.yml` — scrape config
- `infra/monitoring/grafana/provisioning/datasources/prometheus.yml` — auto-provision
- `infra/monitoring/grafana/provisioning/dashboards/dashboard.yml` — provider
- `infra/monitoring/grafana/provisioning/dashboards/odoo-overview.json` — dashboard
- `infra/monitoring/alerting/rules.yml` — alert rules
- `infra/monitoring/docker-compose.monitoring.yml` — compose overlay
- `scripts/verify_monitoring.sh` — verification

### Targets
- `odoo-core:8069/web/health` (Odoo)
- `postgres-exporter:9187/metrics` (PG stats)
- `node-exporter:9100/metrics` (host metrics)
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
- `scripts/verify_auth.sh`

### Dependencies
- OCA `auth_oidc` (OpenID Connect)
- OCA `auth_totp` (TOTP MFA) — ships with Odoo CE 16+

## Phase E: Backup

### Files
- `scripts/backup_verify.sh`

### Logic
1. Check `pg_dump` or DO managed backup API
2. Verify age < 25 hours
3. Verify size > 1MB (not empty)
4. Exit 0 (pass) or 1 (fail)

## Phase F: CI

### Files
- `.github/workflows/azure-waf-parity.yml`
- `docs/evidence/TEMPLATE_azure_waf_rescore.md`

### Triggers
- Push to `main`
- Weekly schedule (Sunday 02:00 UTC)
- Manual dispatch
