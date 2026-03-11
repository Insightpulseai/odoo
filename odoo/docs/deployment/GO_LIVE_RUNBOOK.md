# Go-Live Runbook: Odoo CE 19 + OCA Self-Hosted

**Version**: 1.0.0
**Last Updated**: 2026-01-29
**Status**: Production Ready

---

## Overview

This runbook documents the complete go-live sequence for deploying Odoo CE 19 with OCA modules on self-hosted DigitalOcean infrastructure.

### Architecture Summary

```
┌─────────────────────────────────────────────────────────────────────┐
│                   Production Stack (Self-Hosted)                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   DigitalOcean Droplet (178.128.112.214)                            │
│   ├── Docker Compose                                                 │
│   │   ├── odoo-core (Odoo CE 19 + OCA + IPAI modules)              │
│   │   ├── postgres (PostgreSQL 16)                                  │
│   │   └── nginx (reverse proxy + SSL)                               │
│   │                                                                  │
│   └── Services                                                       │
│       ├── Odoo Web (8069 → nginx → 443)                             │
│       ├── Odoo Longpolling (8072)                                   │
│       └── PostgreSQL (5432 internal)                                │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│   External Integrations                                              │
│   ├── Supabase (spdtwktxdalcfigzeqrz) - Analytics/Task Bus          │
│   ├── n8n (ipa.insightpulseai.com) - Workflow Automation            │
│   ├── Slack - ChatOps/Notifications                                 │
│   └── Apache Superset - BI Dashboards                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Pre-Flight Checklist

### 1. Infrastructure Verification

```bash
# Run pre-flight checks
./scripts/preflight/check_infrastructure.sh

# Expected outputs:
# ✅ DigitalOcean droplet accessible
# ✅ Docker installed and running
# ✅ Docker Compose available
# ✅ SSL certificates valid
# ✅ DNS records configured
```

### 2. Configuration Audit

| Item | Location | Verified |
|------|----------|----------|
| Odoo config | `config/odoo.conf` | ☐ |
| PostgreSQL credentials | `.env.prod` | ☐ |
| SSL certificates | `/etc/letsencrypt/` | ☐ |
| Docker Compose | `docker-compose.yml` | ☐ |
| Nginx config | `deploy/nginx/` | ☐ |

### 3. Backup Verification

```bash
# Test backup/restore cycle
./scripts/backup/backup_test.sh

# Verify backup exists
ls -la /opt/backups/odoo/
```

---

## Go-Live Sequence

### Phase 1: Database Migration (T-60 min)

```bash
# 1. Create final pre-migration backup
./scripts/backup/create_backup.sh --full --tag "pre-golive-$(date +%Y%m%d)"

# 2. Run pending migrations
docker compose exec odoo-core odoo -d production --stop-after-init -u all

# 3. Verify migration success
./scripts/db_verify.sh
```

### Phase 2: Module Deployment (T-45 min)

```bash
# 1. Deploy IPAI modules
./scripts/deploy-odoo-modules.sh --env production

# 2. Install OCA allowlist modules
./scripts/oca/install_allowlist.sh --env production

# 3. Verify module installation
docker compose exec odoo-core odoo shell -d production << 'EOF'
modules = env['ir.module.module'].search([('state', '=', 'installed')])
print(f"Installed modules: {len(modules)}")
ipai_count = len([m for m in modules if m.name.startswith('ipai_')])
print(f"IPAI modules: {ipai_count}")
EOF
```

### Phase 3: Service Startup (T-30 min)

```bash
# 1. Pull latest images
docker compose pull

# 2. Start services
docker compose up -d

# 3. Wait for healthy state
./scripts/wait_healthy.sh --timeout 300

# 4. Verify all containers running
docker compose ps
```

### Phase 4: Smoke Tests (T-15 min)

```bash
# Run comprehensive smoke tests
./scripts/smoke_test_odoo.sh

# Expected outputs:
# ✅ Odoo web accessible (200 OK)
# ✅ Database connection verified
# ✅ Session creation works
# ✅ Core modules responding
# ✅ API endpoints healthy
```

### Phase 5: DNS Cutover (T-0)

```bash
# 1. Update DNS to production IP
# (Manual step in DNS provider or use doctl)

# 2. Verify DNS propagation
dig +short erp.insightpulseai.com

# 3. Test production URL
curl -I https://erp.insightpulseai.com/web/login
```

---

## Post-Go-Live Verification

### Immediate Checks (T+5 min)

```bash
# 1. Verify SSL certificate
openssl s_client -connect erp.insightpulseai.com:443 -servername erp.insightpulseai.com < /dev/null 2>/dev/null | openssl x509 -noout -dates

# 2. Check Odoo logs for errors
docker compose logs --tail=100 odoo-core | grep -i error

# 3. Verify session handling
curl -s -c cookies.txt -b cookies.txt https://erp.insightpulseai.com/web/login

# 4. Run post-deployment validation
./scripts/go_live.sh --validate-only
```

### Integration Checks (T+15 min)

| Integration | Test Command | Expected |
|-------------|--------------|----------|
| n8n Webhooks | `curl -X POST $N8N_WEBHOOK_URL` | 200 OK |
| Supabase Sync | `./scripts/test_supabase_sync.sh` | Records synced |
| Slack Alerts | `./scripts/test_slack_alert.sh` | Message received |

### Performance Baseline (T+30 min)

```bash
# Capture performance baseline
./scripts/perf_baseline.sh

# Metrics to record:
# - Page load time (target: <3s)
# - API response time (target: <500ms)
# - Database query time (target: <100ms)
# - Memory usage (target: <4GB)
```

---

## Rollback Procedure

### Automatic Rollback Triggers

- Odoo health endpoint returns non-200 for >5 minutes
- Error rate exceeds 5% in first 30 minutes
- Critical module fails to load

### Manual Rollback Steps

```bash
# 1. Stop current deployment
docker compose down

# 2. Restore from pre-go-live backup
./scripts/backup/restore_backup.sh --tag "pre-golive-YYYYMMDD"

# 3. Start previous version
docker compose -f docker-compose.rollback.yml up -d

# 4. Verify rollback success
./scripts/smoke_test_odoo.sh
```

---

## Monitoring Setup

### Alert Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| CPU Usage | >70% | >90% | Scale/investigate |
| Memory | >75% | >90% | Restart/scale |
| Disk | >80% | >95% | Cleanup/expand |
| Response Time | >2s | >5s | Investigate |
| Error Rate | >1% | >5% | Rollback consideration |

### Monitoring Commands

```bash
# Real-time logs
docker compose logs -f odoo-core

# Resource usage
docker stats --no-stream

# Database connections
docker compose exec postgres psql -U odoo -c "SELECT count(*) FROM pg_stat_activity;"
```

---

## Support Contacts

| Role | Contact | Escalation |
|------|---------|------------|
| DevOps Lead | (internal) | 15 min |
| Database Admin | (internal) | 30 min |
| Odoo Expert | (internal) | 60 min |

---

## Appendix: Script Reference

| Script | Purpose |
|--------|---------|
| `scripts/go_live.sh` | Main go-live orchestrator |
| `scripts/smoke_test_odoo.sh` | Comprehensive smoke tests |
| `scripts/backup/backup_test.sh` | Backup/restore validation |
| `scripts/preflight/check_infrastructure.sh` | Pre-flight checks |
| `scripts/wait_healthy.sh` | Health check waiter |
| `scripts/perf_baseline.sh` | Performance baseline capture |

---

## Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-01-29 | 1.0.0 | Initial go-live runbook | Claude Code |
