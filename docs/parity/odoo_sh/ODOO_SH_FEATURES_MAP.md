# Odoo.sh Features → Open-Stack Parity Map (SSOT)

**Source**: https://www.odoo.sh/features
**Last Updated**: 2026-01-28
**Status**: Active development

## Executive Summary

Odoo.sh is a managed platform providing CI/CD, staging/prod environments, backups, monitoring, and DNS. This document maps each capability to open-stack alternatives for self-hosted parity.

---

## Capability Areas

### 1. CI/CD & GitHub Integration
**Odoo.sh provides**: Auto test + deploy per commit/PR/merge/fork, clear logs, runbot dashboard
**Open-stack parity**:
- GitHub Actions (already implemented)
- Self-hosted runners on DigitalOcean droplets
- Artifact storage in GitHub Actions or Supabase Storage
- Real-time log streaming via GitHub Actions UI

### 2. Preview/Feature Environments
**Odoo.sh provides**: Per-branch/PR instant deploy, public/private URLs, TTL-based cleanup
**Open-stack parity**:
- Docker Compose ephemeral stacks (per PR)
- Dynamic subdomain routing via nginx/Traefik
- GitHub Actions workflow: `preview-env-deploy.yml`
- Automatic cleanup after PR merge/close

### 3. Staging with Production Data
**Odoo.sh provides**: Sanitized prod snapshots, scheduled actions disabled, mail interception, TTL enforcement
**Open-stack parity**:
- PostgreSQL `pg_dump` → PII scrubbing script → staging restore
- `ir.cron` disabled in staging via Odoo config
- Mail catcher (MailHog/Mailpit) for staging
- 90-day TTL via cron cleanup script

### 4. Logs & Monitoring
**Odoo.sh provides**: Filtered real-time logs, performance KPIs, monitoring dashboards
**Open-stack parity**:
- Docker logs → Loki/Promtail (self-hosted)
- Prometheus + Grafana for metrics
- Custom Odoo performance dashboards
- Alert routing via Mattermost webhooks

### 5. Shell/SSH Access
**Odoo.sh provides**: Web shell to build/prod containers
**Open-stack parity**:
- SSH bastion with audit logging (Teleport or OpenSSH)
- Docker exec via MCP tool (RBAC-gated, audit-logged)
- No human web shell (security policy)

### 6. Module Dependency Management
**Odoo.sh provides**: Git submodules for OCA/community addons, automated installation
**Open-stack parity**:
- `oca.lock.json` for deterministic OCA module pins
- `addons/external/oca/` git submodules
- CI validation: `oca-module-drift-gate.yml`

### 7. Mail Catcher (Non-Prod)
**Odoo.sh provides**: Dev/staging emails intercepted and captured (not sent)
**Open-stack parity**:
- MailHog for dev/staging (port 8025 UI)
- Odoo `mail_catchall_domain` config override
- Production: Mailgun SMTP (already configured)

### 8. Backups & Recovery
**Odoo.sh provides**: Incremental backups across multiple DCs, instant recovery to staging/prod
**Open-stack parity**:
- PostgreSQL WAL archiving via `pgBackRest` or `wal-g`
- Daily full backups + continuous WAL shipping to DigitalOcean Spaces
- Automated restore tests (weekly CI job)
- One-command staging restore script

### 9. DNS & Custom Domains
**Odoo.sh provides**: Automatic DNS per environment, custom domain support, TLS
**Open-stack parity**:
- DigitalOcean DNS API automation
- Let's Encrypt + certbot for TLS
- Traefik/nginx dynamic routing per environment

### 10. Security Baseline
**Odoo.sh provides**: Least privilege, secret scanning, supply chain security (references Odoo security page)
**Open-stack parity**:
- GitHub secret scanning + Dependabot
- GitLeaks pre-commit hook
- Docker image scanning via Trivy
- Supabase RLS for data access control

---

## Implementation Status

| Capability | Status | Implementation Location |
|------------|--------|------------------------|
| CI/CD GitHub integration | ✅ Active | `.github/workflows/` |
| Preview environments | 🟡 Planned | `docs/parity/odoo_sh/PREVIEW_ENVS.md` |
| Staging from prod data | 🟡 Planned | `scripts/odoo_sh/snapshot_restore.sh` |
| Logs & monitoring | 🟡 Partial | DigitalOcean metrics |
| SSH/shell access | ✅ Active | SSH to droplets |
| Module dependencies | ✅ Active | `oca.lock.json` + CI gates |
| Mail catcher | 🔴 Not started | - |
| Backups & restore tests | 🟡 Partial | Manual `pg_dump` only |
| DNS automation | ✅ Active | DigitalOcean DNS |
| Security baseline | ✅ Active | GitHub security features |

---

## Priority Roadmap

### P0 (Must Have)
1. **Preview environments** per PR with dynamic subdomains
2. **Staging restore** from prod snapshot (PII-scrubbed)
3. **Automated smoke tests** on deploy (health checks + critical paths)
4. **Backups + restore test automation** (weekly validation)
5. **Mail catcher** in dev/staging (MailHog)

### P1 (Should Have)
6. Logs/metrics dashboards (Loki + Prometheus + Grafana)
7. Deterministic module dependency lock (already started with `oca.lock.json`)
8. RBAC-guarded exec (no freeform shell without audit)
9. DNS automation per environment

### P2 (Nice to Have)
10. Visual parity gates / regression checks (SSIM validation)
11. Performance profiling dashboard (Odoo-specific metrics)
12. Multi-DC backup replication (DigitalOcean Spaces + AWS S3)

---

## References

- [Odoo.sh Features](https://www.odoo.sh/features) - Official capability inventory
- [Odoo.sh Staging/Dev Behavior](https://www.odoo.com/documentation/19.0/administration/odoo_sh/getting_started/branches.html) - Neutralization semantics
- [odoo-ce/CLAUDE.md](../../CLAUDE.md) - Project execution model
- [odoo-ce/.github/workflows/](../../.github/workflows/) - CI/CD implementation
