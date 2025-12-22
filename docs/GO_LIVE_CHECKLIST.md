# Odoo CE Production Go-Live Checklist

**Project**: InsightPulse AI - Odoo CE 18.0 (OCA)
**Version**: 0.10.0
**Target Date**: _________________
**Go-Live Lead**: _________________

---

## Table of Contents

1. [Pre-Flight Phase (T-14 to T-7 Days)](#pre-flight-phase)
2. [Final Preparation Phase (T-7 to T-1 Days)](#final-preparation-phase)
3. [Go-Live Day (Day 0)](#go-live-day)
4. [Post-Go-Live Phase (Day 1 to Week 4)](#post-go-live-phase)
5. [Rollback Plan](#rollback-plan)
6. [Contact Matrix](#contact-matrix)
7. [Appendices](#appendices)

---

## Pre-Flight Phase

### T-14 Days: Code Freeze & Final Testing

#### Code Quality
- [ ] All feature branches merged to main
- [ ] Code freeze initiated
- [ ] All CI/CD pipelines passing
- [ ] No critical or high-severity bugs open
- [ ] Security scan completed (0 critical vulnerabilities)
- [ ] OCA compliance verified (pre-commit hooks active)

#### Testing Completion
- [ ] Unit tests passing (target: 80%+ coverage)
- [ ] Integration tests passing
- [ ] End-to-end workflow tests passing
- [ ] Performance testing completed
  - [ ] Response time < 2 seconds (95th percentile)
  - [ ] Concurrent users: 100+ supported
  - [ ] Database query optimization verified
- [ ] User Acceptance Testing (UAT) signed off

#### Module Verification
- [ ] All IPAI modules manifests validated
- [ ] Module dependencies resolved
- [ ] No Enterprise-only features included
- [ ] Web icons and assets validated
- [ ] Translation files complete (if applicable)

### T-10 Days: Infrastructure Readiness

#### Production Environment
- [ ] Production server(s) provisioned
- [ ] Docker environment configured
- [ ] PostgreSQL 15 database provisioned
- [ ] Database performance tuned (see `docs/DB_TUNING.md`)
- [ ] SSL/TLS certificates issued
- [ ] Domain DNS configured
- [ ] Firewall rules configured
- [ ] Load balancer configured (if applicable)

#### Container Configuration
- [ ] Production `docker-compose.prod.yml` validated
- [ ] Environment variables configured (`.env.production`)
- [ ] Secrets management in place
- [ ] Resource limits set appropriately
- [ ] Health check endpoints configured

#### Networking
- [ ] Nginx reverse proxy configured
- [ ] HTTPS redirect configured
- [ ] CORS settings verified
- [ ] WebSocket support configured (if needed)
- [ ] Rate limiting configured

### T-7 Days: Backup & Recovery Verification

#### Backup Systems
- [ ] Automated backup script tested (`scripts/backup_odoo.sh`)
- [ ] Database backup verified (pg_dump)
- [ ] Filestore backup verified
- [ ] Backup retention policy configured
- [ ] Off-site backup destination verified
- [ ] Backup encryption enabled

#### Recovery Testing
- [ ] Full restore tested on staging
- [ ] Recovery Time Objective (RTO) validated
- [ ] Recovery Point Objective (RPO) validated
- [ ] Rollback procedure tested
- [ ] Database restore timing documented

---

## Final Preparation Phase

### T-7 Days: Monitoring & Alerting Setup

#### Monitoring Configuration
- [ ] Prometheus metrics configured
- [ ] Grafana dashboards deployed
  - [ ] System health dashboard
  - [ ] Application metrics dashboard
  - [ ] Business KPIs dashboard
- [ ] Log aggregation configured
- [ ] Audit logging enabled

#### Alerting Rules
- [ ] Critical alerts configured:
  - [ ] Service down
  - [ ] High error rate (>1%)
  - [ ] High response time (>5s)
  - [ ] Database connection issues
  - [ ] Disk space low (<10%)
  - [ ] Memory usage high (>90%)
- [ ] Alert notification channels configured
  - [ ] Email
  - [ ] Mattermost/Slack
  - [ ] PagerDuty (if applicable)

### T-5 Days: Data Migration (if applicable)

#### Data Preparation
- [ ] Source data extracted and validated
- [ ] Data transformation scripts tested
- [ ] Data mapping verified
- [ ] Duplicate detection completed
- [ ] Data quality checks passed

#### Migration Execution
- [ ] Migration dry-run on staging completed
- [ ] Migration timing documented
- [ ] Data validation queries prepared
- [ ] Rollback data preserved

### T-3 Days: Security Final Review

#### Security Checklist
- [ ] All default passwords changed
- [ ] Admin accounts secured with MFA
- [ ] API keys/tokens rotated
- [ ] Security headers configured
- [ ] XSS protection verified
- [ ] CSRF protection verified
- [ ] SQL injection protection verified
- [ ] Session management configured

#### Access Control
- [ ] User roles and permissions verified
- [ ] Access groups configured correctly
- [ ] Record rules tested
- [ ] API access controlled

### T-1 Day: Final Preparation

#### Pre-Go-Live Checklist
- [ ] Final staging deployment successful
- [ ] All stakeholder approvals received
- [ ] Go-Live communication sent
- [ ] Support team briefed
- [ ] On-call schedule published
- [ ] War room (virtual/physical) prepared
- [ ] Rollback decision criteria agreed

#### Documentation Ready
- [ ] User documentation published
- [ ] Admin runbooks available
- [ ] API documentation current
- [ ] Known issues documented
- [ ] FAQ prepared

---

## Go-Live Day

### Phase 1: Pre-Deployment (T-2 hours)

| Time | Task | Owner | Status |
|------|------|-------|--------|
| T-2:00 | Send "deployment starting" notification | _______ | [ ] |
| T-2:00 | Verify backup completed successfully | _______ | [ ] |
| T-1:45 | Lock staging environment | _______ | [ ] |
| T-1:30 | Final code review complete | _______ | [ ] |
| T-1:00 | War room active, all teams joined | _______ | [ ] |
| T-0:30 | Final go/no-go decision | _______ | [ ] |

### Phase 2: Deployment Execution

| Time | Task | Owner | Status |
|------|------|-------|--------|
| T+0:00 | Enable maintenance mode | _______ | [ ] |
| T+0:05 | Stop existing services | _______ | [ ] |
| T+0:10 | Database backup (final) | _______ | [ ] |
| T+0:20 | Deploy new containers | _______ | [ ] |
| T+0:25 | Database migrations (if any) | _______ | [ ] |
| T+0:35 | Update/install modules | _______ | [ ] |
| T+0:45 | Start all services | _______ | [ ] |
| T+0:50 | Disable maintenance mode | _______ | [ ] |

### Phase 3: Validation

| Time | Task | Owner | Status |
|------|------|-------|--------|
| T+1:00 | Health check endpoints responding | _______ | [ ] |
| T+1:05 | Login verification (test accounts) | _______ | [ ] |
| T+1:10 | Core workflow validation | _______ | [ ] |
| T+1:15 | API endpoint validation | _______ | [ ] |
| T+1:20 | Monitoring dashboards showing data | _______ | [ ] |
| T+1:30 | Performance baseline captured | _______ | [ ] |
| T+1:45 | Go-live announcement sent | _______ | [ ] |

### Phase 4: Hypercare (T+2 to T+8 hours)

- [ ] Dedicated support team active
- [ ] Real-time monitoring active
- [ ] User feedback collection active
- [ ] Issue triage in place
- [ ] Quick-fix procedures ready

---

## Post-Go-Live Phase

### Day 1-2: Stabilization

- [ ] Monitor error rates continuously
- [ ] Address P1/P2 issues immediately
- [ ] Document all incidents
- [ ] Daily status reports to stakeholders
- [ ] User feedback triage
- [ ] Performance monitoring review

### Week 1: Early Life Support

- [ ] Daily team check-ins
- [ ] Bug fix releases as needed
- [ ] Performance optimization if required
- [ ] User training support
- [ ] FAQ updates based on queries
- [ ] Backup verification daily

### Week 2-4: Transition to BAU

- [ ] Reduce hypercare coverage
- [ ] Knowledge transfer to support team
- [ ] Post-implementation review
- [ ] Lessons learned documentation
- [ ] Performance baseline established
- [ ] SLA monitoring active
- [ ] Handover to operations complete

---

## Rollback Plan

### Rollback Decision Criteria

Initiate rollback if ANY of the following occur:

| Severity | Condition | Decision |
|----------|-----------|----------|
| Critical | Total system outage >30 minutes | Immediate rollback |
| Critical | Data corruption detected | Immediate rollback |
| Critical | Security breach detected | Immediate rollback |
| High | Error rate >10% for >15 minutes | Consider rollback |
| High | Core workflows blocked | Consider rollback |

### Rollback Procedure

```bash
# Step 1: Announce rollback
# Send notification to all stakeholders

# Step 2: Enable maintenance mode
docker exec odoo-web odoo --stop-after-init

# Step 3: Stop current services
docker compose -f docker-compose.prod.yml down

# Step 4: Restore database
pg_restore -h localhost -U odoo -d odoo_prod < /backups/pre_golive_backup.dump

# Step 5: Restore filestore
rsync -av /backups/filestore_backup/ /var/lib/odoo/filestore/

# Step 6: Deploy previous version
git checkout <previous_tag>
docker compose -f docker-compose.prod.yml up -d

# Step 7: Verify rollback
curl -f http://localhost:8069/web/health

# Step 8: Disable maintenance mode
# Announce rollback complete
```

### Rollback Communication Template

```
SUBJECT: [URGENT] Odoo CE Deployment Rollback Initiated

Dear Stakeholders,

We are initiating a rollback of the Odoo CE deployment due to:
- Issue: [Describe issue]
- Impact: [Describe impact]
- Expected Resolution: [Time estimate]

Actions:
1. System will be unavailable for approximately [X] minutes
2. Data entered since [go-live time] may need to be re-entered
3. Support team will assist with data recovery

Next Update: [Time]

Thank you for your patience.
```

---

## Contact Matrix

### Core Team

| Role | Name | Contact | Escalation |
|------|------|---------|------------|
| Go-Live Lead | _____________ | _____________ | Primary |
| Technical Lead | _____________ | _____________ | Technical issues |
| DevOps Lead | _____________ | _____________ | Infrastructure |
| QA Lead | _____________ | _____________ | Testing issues |
| Security Lead | _____________ | _____________ | Security concerns |
| Business Owner | _____________ | _____________ | Business decisions |

### Support Team

| Level | Contact | Hours | Response SLA |
|-------|---------|-------|--------------|
| L1 Support | _____________ | 8x5 | 15 minutes |
| L2 Support | _____________ | 8x5 | 1 hour |
| L3/Dev Team | _____________ | On-call | 2 hours |
| Emergency | _____________ | 24x7 | 30 minutes |

### External Vendors

| Vendor | Contact | Support Type |
|--------|---------|--------------|
| Hosting Provider | _____________ | Infrastructure |
| PostgreSQL Support | _____________ | Database |
| Security Vendor | _____________ | Security incidents |

---

## Appendices

### Appendix A: Deployment Commands

```bash
# Pull latest changes
git pull origin main

# Build and deploy
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# Check logs
docker compose -f docker-compose.prod.yml logs -f odoo

# Database operations
docker compose exec db psql -U odoo -d odoo_prod

# Update modules
docker compose exec odoo odoo -d odoo_prod -u all --stop-after-init
```

### Appendix B: Health Check Endpoints

| Endpoint | Expected Response | Purpose |
|----------|-------------------|---------|
| `/web/health` | 200 OK | Basic health |
| `/web/database/selector` | 200 OK | DB connectivity |
| `/longpolling/poll` | 200 OK | Bus connectivity |

### Appendix C: Key Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| `docker-compose.prod.yml` | Production Docker config | Project root |
| `.env.production` | Environment variables | Project root |
| `odoo.conf` | Odoo configuration | `/etc/odoo/` |
| `nginx.conf` | Reverse proxy config | `/etc/nginx/` |

### Appendix D: Module Installation Order

```bash
# Core IPAI Modules (install in order)
odoo -d odoo_prod -i ipai --stop-after-init
odoo -d odoo_prod -i ipai_ce_branding --stop-after-init
odoo -d odoo_prod -i ipai_ppm --stop-after-init
odoo -d odoo_prod -i ipai_finance_ppm --stop-after-init
odoo -d odoo_prod -i ipai_month_end --stop-after-init
odoo -d odoo_prod -i ipai_close_orchestration --stop-after-init
odoo -d odoo_prod -i ipai_bir_tax_compliance --stop-after-init
```

---

## Sign-Off Page

### Technical Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Technical Lead | _____________ | _____________ | _______ |
| DevOps Lead | _____________ | _____________ | _______ |
| QA Lead | _____________ | _____________ | _______ |
| Security Lead | _____________ | _____________ | _______ |

### Business Sign-Off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Business Owner | _____________ | _____________ | _______ |
| Product Owner | _____________ | _____________ | _______ |
| Finance Lead | _____________ | _____________ | _______ |

### Final Go-Live Authorization

**Go-Live Authorized By**: _________________________

**Date**: _________________________

**Time**: _________________________

---

*Document Version: 1.0.0*
*Last Updated: 2024-12-22*
*Next Review: Post-implementation*
