# Tasks: Azure WAF Parity

## Phase A: Spec Bundle
- [x] constitution.md
- [x] prd.md
- [x] plan.md
- [x] tasks.md

## Phase B: Observability Stack
- [x] infra/monitoring/prometheus/prometheus.yml
- [x] infra/monitoring/grafana/provisioning/datasources/prometheus.yml
- [x] infra/monitoring/grafana/provisioning/dashboards/dashboard.yml
- [x] infra/monitoring/grafana/provisioning/dashboards/odoo-overview.json
- [x] infra/monitoring/alerting/rules.yml
- [x] infra/monitoring/docker-compose.monitoring.yml
- [x] scripts/verify_monitoring.sh

## Phase C: CDN
- [x] infra/cloudflare/cloudflare-cache-rules.json
- [x] scripts/verify_cdn.sh

## Phase D: Auth Hardening
- [x] addons/ipai/ipai_auth_oidc/__manifest__.py
- [x] addons/ipai/ipai_auth_oidc/__init__.py
- [x] addons/ipai/ipai_auth_oidc/data/auth_provider_data.xml
- [x] scripts/verify_auth.sh

## Phase E: Backup Verification
- [x] scripts/backup_verify.sh

## Phase F: CI + Evidence
- [x] .github/workflows/azure-waf-parity.yml
- [x] docs/evidence/TEMPLATE_azure_waf_rescore.md

## Phase G: Ship
- [ ] Commit
- [ ] Push to claude/azure-reference-architecture-Gm1Kg
