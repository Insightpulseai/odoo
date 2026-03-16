# PRD: Azure WAF Parity — 78 to 85+

## Problem Statement

The InsightPulse AI stack scored 78/100 (B+) on the Azure Well-Architected Framework assessment (2026-01-25). The two weakest pillars — Security (75) and Cost Optimization (72) — drag the aggregate below the 85 target required for enterprise client readiness.

## Success Criteria

| Metric | Before | After | Method |
|--------|--------|-------|--------|
| WAF Aggregate | 78 | >= 83 | Re-run scorecard |
| Security Pillar | 75 | >= 82 | OAuth module + MFA-ready + verify script |
| Cost Optimization | 72 | >= 78 | Monitoring enables right-sizing visibility |
| Performance Efficiency | 76 | >= 82 | CDN for static assets + Prometheus metrics |
| Operational Excellence | 85 | >= 88 | Prometheus/Grafana + alerting rules + CI gate |
| Reliability | 82 | >= 85 | Backup verification + alerting |

## Deliverables

### D1: Observability Stack
- Prometheus with scrape targets: Odoo health, PostgreSQL exporter, node exporter
- Grafana with provisioned datasource + Odoo overview dashboard
- Alerting rules: Odoo down, PG replication lag, high CPU, disk > 85%
- Docker Compose overlay file (profile-activated, not always-on)

### D2: CDN + Static Asset Caching
- Cloudflare cache rules JSON (cacheable paths, bypass paths)
- Production compose updated with proxy headers (`X-Forwarded-For`, `X-Real-IP`)
- Verification script checking `cf-cache-status` header

### D3: Auth Hardening
- `ipai_auth_oidc` Odoo module declaring OCA `auth_oidc` + `auth_totp` dependencies
- Default OAuth provider data template (Google/Keycloak, credentials from env)
- Verification script checking module installability

### D4: Backup Verification
- Script that checks latest PG backup exists and is < 25 hours old
- Cron-safe, idempotent, exits 0/1

### D5: CI + Evidence
- GitHub Actions workflow running all verify scripts
- Evidence template for WAF re-scoring

## Workspace Alignment

All deliverables are scoped to the `insightpulseai-prod` workspace:
- Monitoring targets: `erp.insightpulseai.com:8069` (Odoo), local PG
- CDN: Cloudflare zone for `insightpulseai.com`
- Auth: Provider for InsightPulse AI org users
- Backup: PostgreSQL on DO droplet `178.128.112.214`

## Out of Scope

- Multi-region deployment (Phase 2)
- Kafka/Redpanda streaming (Phase 3)
- Feature store / Feast (Phase 3)
- OpenMetadata data catalog (Phase 2)
- Debezium CDC (Phase 2)
