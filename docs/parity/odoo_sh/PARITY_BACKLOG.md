# Odoo.sh Parity Backlog

**Last Updated**: 2026-01-28
**Owner**: DevOps + Odoo teams

---

## P0 (Must Have - Production Blocking)

### 1. Preview Environments per PR
**Goal**: Ephemeral Odoo instances for each PR/feature branch
**Why**: Enable visual testing and stakeholder review before merge
**Implementation**:
- GitHub Actions workflow: `.github/workflows/preview-env-deploy.yml`
- Docker Compose template with dynamic subdomain (`pr-123.dev.insightpulseai.net`)
- Automatic cleanup after PR merge/close (TTL: 3 days after merge)
- nginx/Traefik routing configuration

**Acceptance Criteria**:
- [ ] PR opened → preview URL posted as comment within 5 minutes
- [ ] Preview accessible at `https://pr-{number}.dev.insightpulseai.net`
- [ ] Automatic teardown after PR merge
- [ ] Smoke tests pass before URL is published

---

### 2. Staging Restore from Production Snapshot (Sanitized)
**Goal**: Test changes against real production data without PII exposure
**Why**: Catch data-dependent bugs before production deployment
**Implementation**:
- Script: `scripts/odoo_sh/snapshot_prod.sh` (pg_dump with compression)
- Script: `scripts/odoo_sh/scrub_pii.py` (anonymize res.partner, hr.employee)
- Script: `scripts/odoo_sh/restore_to_staging.sh` (import + smoke test)
- Schedule: Weekly automated restore + validation

**Acceptance Criteria**:
- [ ] Weekly cron job: prod snapshot → scrub → staging restore
- [ ] PII scrubbing validated (no real emails, names, phone numbers)
- [ ] Staging accessible at `https://staging.erp.insightpulseai.net`
- [ ] Smoke tests pass after restore
- [ ] Scheduled actions disabled in staging (`--stop-after-init`)

---

### 3. Automated Smoke Tests on Deploy
**Goal**: Prevent broken deployments from reaching users
**Why**: Fast feedback loop for deployment failures
**Implementation**:
- Script: `scripts/odoo_sh/smoke_test.sh`
- Tests: Health endpoint, database connectivity, module install verification
- CI integration: Block deployment if smoke tests fail

**Acceptance Criteria**:
- [ ] Health check: `/web/health` returns 200
- [ ] Database check: Query `res.users` count > 0
- [ ] Module check: All required modules installed and no errors in log
- [ ] Deployment blocked if any smoke test fails

---

### 4. Backups + Restore Test Automation
**Goal**: Guarantee backup recoverability (backups without restore tests are fiction)
**Why**: Avoid catastrophic data loss scenarios
**Implementation**:
- PostgreSQL WAL archiving: `pgBackRest` or `wal-g` to DigitalOcean Spaces
- Daily full backup + continuous WAL shipping
- Weekly restore test: restore to temporary database → smoke test → destroy
- Alert on restore test failure (Mattermost webhook)

**Acceptance Criteria**:
- [ ] Daily full backups to DigitalOcean Spaces (retention: 30 days)
- [ ] Continuous WAL archiving (RPO: 5 minutes)
- [ ] Weekly automated restore test with validation
- [ ] Restore time < 15 minutes for 100GB database
- [ ] Alert on backup/restore failure

---

### 5. Mail Catcher in Dev/Staging
**Goal**: Prevent accidental email sends from non-prod environments
**Why**: Avoid customer confusion and GDPR violations
**Implementation**:
- MailHog container in dev/staging stacks
- Odoo config override: `smtp_host = mailhog`, `smtp_port = 1025`
- Web UI: `http://localhost:8025` (dev), `https://mail.staging.erp.insightpulseai.net` (staging)

**Acceptance Criteria**:
- [ ] All dev/staging emails captured in MailHog
- [ ] Web UI accessible for email inspection
- [ ] Zero emails sent to real customer addresses from staging
- [ ] Production unchanged (Mailgun SMTP)

---

## P1 (Should Have - Quality of Life)

### 6. Logs/Metrics Dashboards
**Goal**: Observability parity with Odoo.sh monitoring KPIs
**Why**: Faster debugging and performance optimization
**Implementation**:
- Loki + Promtail for log aggregation
- Prometheus + Grafana for metrics
- Custom Odoo dashboards: request latency, error rate, active users

**Acceptance Criteria**:
- [ ] Real-time log search UI (Grafana + Loki)
- [ ] Performance dashboard: P50/P95/P99 request latency
- [ ] Error rate alerts (> 1% triggers Mattermost notification)
- [ ] Retention: 30 days logs, 90 days metrics

---

### 7. Deterministic Module Dependency Lock
**Goal**: Reproducible builds across environments
**Why**: Avoid "works on my machine" deployment failures
**Implementation**:
- Already started: `oca.lock.json` with commit SHAs
- CI validation: `.github/workflows/oca-module-drift-gate.yml`
- Lockfile update workflow: automated OCA submodule bumps with PR

**Acceptance Criteria**:
- [ ] All OCA modules pinned to exact commit SHAs
- [ ] CI fails if OCA modules drift from lockfile
- [ ] Automated PR for OCA module updates (weekly)

---

### 8. RBAC-Guarded Exec (No Freeform Shell Without Audit)
**Goal**: Secure shell access with full audit trail
**Why**: Compliance and security (no untracked production access)
**Implementation**:
- Teleport or OpenSSH with session recording
- MCP tool for agent-driven `docker exec` (RBAC-gated)
- Audit log storage in Supabase

**Acceptance Criteria**:
- [ ] All SSH sessions recorded and stored
- [ ] MCP tool requires approval token for production exec
- [ ] Audit log queryable: "show all prod exec sessions in last 30 days"
- [ ] No direct SSH to production (bastion-only)

---

### 9. DNS Automation per Environment
**Goal**: Automatic subdomain creation for preview/staging environments
**Why**: Eliminate manual DNS configuration bottleneck
**Implementation**:
- DigitalOcean DNS API integration
- Script: `scripts/odoo_sh/create_dns_record.sh`
- Automatic TLS via Let's Encrypt + certbot

**Acceptance Criteria**:
- [ ] Preview env creation auto-creates `pr-{number}.dev.insightpulseai.net`
- [ ] TLS certificate provisioned within 2 minutes
- [ ] DNS cleanup after environment teardown

---

## P2 (Nice to Have - Future Enhancements)

### 10. Visual Parity Gates / Regression Checks
**Goal**: Prevent UI regressions in production
**Why**: Maintain design system consistency
**Implementation**:
- Playwright screenshot capture per PR
- SSIM comparison against baseline screenshots
- Block merge if SSIM < 0.97 (mobile) or < 0.98 (desktop)

**Acceptance Criteria**:
- [ ] Baseline screenshots stored in Supabase Storage
- [ ] CI workflow captures screenshots for changed routes
- [ ] Visual diff report attached to PR
- [ ] Manual override available for intentional UI changes

---

### 11. Performance Profiling Dashboard
**Goal**: Odoo-specific performance insights
**Why**: Optimize slow endpoints and database queries
**Implementation**:
- Odoo profiler middleware integration
- Slow query log aggregation (queries > 1s)
- Dashboard: Top 10 slowest endpoints, N+1 query detection

**Acceptance Criteria**:
- [ ] Profiling data collected for all requests
- [ ] Dashboard shows P95 latency per endpoint
- [ ] Alert on queries > 5s
- [ ] Retention: 7 days profiling data

---

### 12. Multi-DC Backup Replication
**Goal**: Geographic redundancy for disaster recovery
**Why**: Protect against single data center failure
**Implementation**:
- Primary: DigitalOcean Spaces (Singapore)
- Replica: AWS S3 (US East)
- Cross-region replication via `rclone` or `wal-g`

**Acceptance Criteria**:
- [ ] Backups replicated to 2+ geographic regions
- [ ] Recovery drill: restore from replica within 30 minutes
- [ ] Automatic failover if primary backup storage unavailable

---

## Implementation Order

1. **Week 1-2**: P0.1 (Preview environments) + P0.5 (Mail catcher)
2. **Week 3-4**: P0.3 (Smoke tests) + P0.4 (Backup automation)
3. **Week 5-6**: P0.2 (Staging restore) - most complex
4. **Week 7+**: P1 and P2 based on team capacity

---

## Success Metrics

- **Deployment Confidence**: 0 → 95% (via smoke tests + staging validation)
- **Incident Recovery Time**: 4 hours → 15 minutes (via automated restore)
- **Developer Velocity**: +30% (via preview environments eliminating local setup)
- **Production Incidents**: 5/month → 1/month (via staging testing)
