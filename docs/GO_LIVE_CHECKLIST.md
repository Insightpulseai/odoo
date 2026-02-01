# ODOO-CE GO-LIVE CHECKLIST

**InsightPulse Odoo Community Edition ERP Platform**

| Field | Value |
|-------|-------|
| Project | InsightPulseAI Odoo CE Implementation |
| Repository | jgtolentino/odoo-ce |
| Status | MVP Phase 0-1 (CE/OCA Base Stack) |
| Target Go-Live Date | [TO BE FILLED] |
| Prepared | December 22, 2025 |

---

## 📋 PRE-FLIGHT CHECKS (2-4 Weeks Before Go-Live)

### ✅ Code Quality & Compliance

#### Module Manifest Audit

- [ ] All custom modules have complete `__manifest__.py` files
- [ ] All required fields populated: name, version, author, depends, category, installable
- [ ] `external_dependencies` clearly declared for all third-party libraries
- [ ] License field set to AGPL-3.0 or appropriate OCA license
- [ ] No hardcoded references to enterprise modules
- [ ] No `auto_install = True` on custom modules (only base)

**Owner**: [Developer Lead]
**Due**: [Date -14 days]

#### CE/OCA Compliance Check

- [ ] Run CI/CD pipeline: `ci-odoo-ce.yml` passes with 0 failures
- [ ] No enterprise module references detected
- [ ] No odoo.com marketing/upsell links in user-facing code
- [ ] All odoo.com help links rewritten to InsightPulse docs
- [ ] `ipai_ce_cleaner` module active and tested
- [ ] Verify GitHub Actions workflow execution logs

**Owner**: [DevOps/QA Lead]
**Due**: [Date -14 days]

#### Linting & Code Standards

- [ ] Run Flake8 linting on all `addons/ipai_*` modules

```bash
flake8 addons/ipai_* --max-line-length=88 --exclude=migrations
```

- [ ] Fix or document all warnings/errors
- [ ] Python code follows PEP 8 standards
- [ ] XML views formatted consistently (proper indentation, closing tags)
- [ ] SQL queries parameterized (no injection vulnerabilities)

**Owner**: [Developer Lead]
**Due**: [Date -14 days]

#### Security Code Review

- [ ] Manual security review of custom modules completed
- [ ] No hardcoded credentials, API keys, or secrets
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities in templates
- [ ] ORM methods used correctly (no raw SQL except validated)
- [ ] Access control rules (@api.depends, group_ids) properly configured
- [ ] Payment/financial data encrypted at rest

**Owner**: [Security Lead / Senior Developer]
**Due**: [Date -14 days]

---

### 🧪 Testing & QA

#### Unit Tests

- [ ] All custom modules have unit tests in `tests/` directory
- [ ] Test coverage ≥ 80% for critical modules:
  - [ ] `ipai_expense/` - 80%+ coverage
  - [ ] `ipai_equipment/` - 80%+ coverage
- [ ] All tests passing locally

```bash
python -m pytest addons/ipai_* -v --cov
```

- [ ] Tests integrated into CI/CD pipeline

**Owner**: [QA Lead]
**Due**: [Date -14 days]

#### Integration Tests

- [ ] OCA module compatibility verified
- [ ] Custom modules work correctly with OCA dependencies
- [ ] Data import workflows tested end-to-end
- [ ] GL posting integration with account module verified
- [ ] Multi-module scenarios tested (expense → GL → reporting)

**Owner**: [QA Lead]
**Due**: [Date -14 days]

#### User Acceptance Testing (UAT)

- [ ] Business users completed all UAT scenarios
- [ ] UAT sign-off document signed
- [ ] Critical issues resolved or documented
- [ ] Defects tracked and status confirmed
- [ ] Performance testing completed (see below)

**Owner**: [Product Manager / Business Owner]
**Due**: [Date -7 days]

#### Performance Testing

- [ ] Load testing completed: ≥100 concurrent users
- [ ] Response time targets met:
  - [ ] Page load: <2 seconds (90th percentile)
  - [ ] Report generation: <5 seconds
  - [ ] Expense submission: <1 second
- [ ] Database query optimization completed
- [ ] Slow queries identified and indexed
- [ ] Caching strategy validated (Redis if configured)

**Owner**: [DevOps/Performance Lead]
**Due**: [Date -7 days]

#### Data Migration Testing

- [ ] Data migration scripts created and tested
- [ ] Data validation rules defined
- [ ] Sample data successfully migrated to staging
- [ ] Data integrity checks automated
- [ ] Rollback procedures tested
- [ ] Migration time estimate documented

**Owner**: [DBA / Data Lead]
**Due**: [Date -7 days]

---

### 📚 Documentation & Knowledge Transfer

#### Technical Documentation

- [ ] Architecture diagram updated (`docs/architecture.md`)
- [ ] Module dependency diagram created
- [ ] API documentation completed for custom endpoints
- [ ] Database schema documented
- [ ] Configuration parameter guide completed
- [ ] Troubleshooting guide created

**Owner**: [Technical Writer / Lead Developer]
**Due**: [Date -10 days]

#### User Documentation

- [ ] User guides for each module (expense, equipment)
- [ ] Quick-start guides for common workflows
- [ ] Video tutorials recorded (optional but recommended)
- [ ] FAQ document created
- [ ] Help desk knowledge base populated

**Owner**: [Technical Writer / Product Manager]
**Due**: [Date -10 days]

#### Operations Documentation

- [ ] Deployment runbook completed (`deploy/RUNBOOK.md`)
- [ ] Backup & restore procedures documented
- [ ] Disaster recovery plan (DRP) created
- [ ] Monitoring & alerting setup documented
- [ ] Log rotation and retention policy defined
- [ ] Maintenance window procedures documented

**Owner**: [DevOps / Ops Lead]
**Due**: [Date -10 days]

#### Knowledge Transfer (KT) Sessions

- [ ] Ops team trained on deployment procedures (4 hours)
- [ ] Support team trained on module functionality (8 hours)
- [ ] Developer team trained on codebase (4 hours)
- [ ] Business users trained on workflows (varies)
- [ ] KT session recordings available
- [ ] Attendees signed KT checklist

**Owner**: [Project Manager]
**Due**: [Date -7 days]

---

### 🏗️ Infrastructure & Deployment

#### Production Environment Setup

- [ ] Production server provisioned (DigitalOcean droplet)
- [ ] DNS records created and verified:
  - [ ] A record: `erp.insightpulseai.com` → IP
  - [ ] MX records (if mail needed)
  - [ ] TXT records (SPF, DKIM if applicable)
- [ ] SSL/TLS certificates obtained and installed (Let's Encrypt)
- [ ] Certificate auto-renewal configured
- [ ] Firewall (UFW) configured with proper rules
- [ ] SSH access restricted (only authorized keys)

**Owner**: [DevOps Lead]
**Due**: [Date -14 days]

#### Database Setup

- [ ] PostgreSQL 13+ installed and configured
- [ ] Database created: `odoo` or `insightpulse`
- [ ] Database user created with restricted privileges
- [ ] Regular backup schedule configured (daily, 2 AM UTC)
- [ ] Backup retention policy enforced (30+ days)
- [ ] Backup restoration tested successfully
- [ ] WAL (Write-Ahead Logging) enabled for crash safety
- [ ] Replication configured (optional, recommended)

**Owner**: [DBA / DevOps Lead]
**Due**: [Date -14 days]

#### Docker & Container Setup

- [ ] `docker-compose.yml` validated and tested
- [ ] Odoo image built and tested locally
- [ ] PostgreSQL image configured with persistence
- [ ] Container resource limits set (CPU, memory)
- [ ] Health checks configured and working
- [ ] Log drivers configured (structured logging)
- [ ] Container restart policies set correctly

**Owner**: [DevOps Lead]
**Due**: [Date -14 days]

#### Nginx Reverse Proxy

- [ ] Nginx configuration for `erp.insightpulseai.com` validated
- [ ] SSL/TLS ciphers optimized (A+ rating recommended)
- [ ] HTTP/2 enabled
- [ ] HSTS headers configured
- [ ] Rate limiting configured to prevent abuse
- [ ] Load balancing configured (if multiple backends)
- [ ] Error pages customized

**Owner**: [DevOps Lead]
**Due**: [Date -14 days]

#### Monitoring & Alerting

- [ ] Monitoring tool deployed (Prometheus/Grafana or equivalent)
- [ ] Key metrics configured:
  - [ ] Odoo process uptime
  - [ ] PostgreSQL connection pool usage
  - [ ] Disk space (alert at 80%)
  - [ ] Memory usage (alert at 85%)
  - [ ] Request latency (p95, p99)
  - [ ] Error rates (500 errors, timeouts)
- [ ] Alert channels configured (email, Slack, PagerDuty)
- [ ] Alert thresholds validated
- [ ] Dashboard created for on-call team

**Owner**: [DevOps Lead]
**Due**: [Date -10 days]

#### Logging & Centralization

- [ ] Container logs configured for centralized collection
- [ ] Log aggregation tool deployed (ELK, Loki, etc.)
- [ ] Odoo logs sent to centralized system
- [ ] PostgreSQL logs captured
- [ ] Nginx access/error logs captured
- [ ] Log retention policy enforced (90 days)
- [ ] Log search and alerting configured

**Owner**: [DevOps Lead]
**Due**: [Date -10 days]

---

### 🔐 Security & Access Control

#### Authentication & Authorization

- [ ] Admin user created with strong password (16+ chars, mixed case, special)
- [ ] Password policy configured in Odoo
- [ ] LDAP/SSO integration configured (if applicable)
- [ ] MFA enabled for admin accounts (if supported by Odoo version)
- [ ] Group-based access control configured for each module
- [ ] Data access rules (record rules) configured correctly
- [ ] Default permissions reviewed and tightened

**Owner**: [Security Lead / Sys Admin]
**Due**: [Date -7 days]

#### Data Protection & Encryption

- [ ] Database encryption at rest configured (or at volume level)
- [ ] Sensitive fields encrypted (passwords, API keys)
- [ ] Encrypted connections to external systems (HTTPS, TLS)
- [ ] Encryption keys stored in secure vault (environment variables, not code)
- [ ] Data masking configured for non-production environments

**Owner**: [Security Lead / DBA]
**Due**: [Date -7 days]

#### Secrets Management

- [ ] Database password stored in `.env` (not git)
- [ ] Admin password stored securely (password manager, not git)
- [ ] API keys for external services (if any) stored in environment
- [ ] `.env` file excluded from git (`.gitignore`)
- [ ] Secrets rotation procedure documented
- [ ] Emergency access procedures documented

**Owner**: [DevOps Lead]
**Due**: [Date -14 days]

#### Vulnerability Assessment

- [ ] Dependency scanning completed (`pip audit`, `safety`)
- [ ] No critical or high-severity vulnerabilities in dependencies
- [ ] Known vulnerabilities documented and mitigated
- [ ] Security patching strategy defined
- [ ] Container image scanning completed

**Owner**: [Security Lead]
**Due**: [Date -7 days]

---

### 📋 Legal & Compliance

#### License & IP Compliance

- [ ] AGPL-3.0 license file present in root
- [ ] All OCA module licenses verified and documented
- [ ] No proprietary or unlicensed code in repository
- [ ] Third-party library licenses audited (no GPL conflicts)
- [ ] CONTRIBUTORS.md or credits file created

**Owner**: [Legal / Compliance Lead]
**Due**: [Date -14 days]

#### Data Privacy & GDPR

- [ ] Data privacy policy reviewed with Legal
- [ ] Data retention policies configured
- [ ] GDPR compliance verified (if applicable)
- [ ] User consent mechanisms configured (if needed)
- [ ] Right to be forgotten procedures documented
- [ ] Data processing addendum (DPA) signed with vendors

**Owner**: [Legal / Compliance Lead]
**Due**: [Date -10 days]

---

## 🚀 GO-LIVE PHASE (1 Week Before - Day Of)

### ⚠️ Final Validation (3 Days Before Go-Live)

#### Staging Environment Final Run

- [ ] Production environment cloned to staging
- [ ] Full data migration dry-run completed successfully
- [ ] Rollback procedures tested end-to-end
- [ ] All modules tested in staging
- [ ] Performance benchmarked matches production targets
- [ ] Backup/restore tested on staging

**Owner**: [DevOps Lead / QA Lead]
**Sign-Off**: _____________ (DevOps Lead)

#### Critical System Tests

- [ ] Database connectivity verified
- [ ] SSL/TLS certificates valid and working
- [ ] All DNS records resolving correctly
- [ ] External API integrations tested (if any)
- [ ] Email delivery tested (if mail configured)
- [ ] File storage working (documents, attachments)
- [ ] PDF report generation working

**Owner**: [DevOps Lead / QA Lead]
**Sign-Off**: _____________ (DevOps Lead)

#### Business Process Validation

- [ ] Sample expense report submitted end-to-end
- [ ] Equipment booking workflow completed
- [ ] GL posting verified in test data
- [ ] Reports generated and verified
- [ ] Data exports (CSV, Excel) working
- [ ] Print/PDF output validated

**Owner**: [Product Manager / Business Analyst]
**Sign-Off**: _____________ (Business Owner)

#### Support Team Readiness

- [ ] Support hotline tested and ready
- [ ] Issue tracking system (Jira/Linear) set up
- [ ] Escalation procedures defined and communicated
- [ ] Support documentation finalized
- [ ] On-call rotation schedule published
- [ ] Emergency contact list created

**Owner**: [Operations / Support Lead]
**Sign-Off**: _____________ (Support Manager)

---

### 🎯 Go-Live Day Checklist (Day Of)

**Scheduled Maintenance Window**: [Date/Time] UTC
**Expected Duration**: [X hours]
**Maintenance Page**: Active? Yes / No

#### Morning (6-8 Hours Before Cutover)

##### Final Production Checks

- [ ] Production server health verified
- [ ] Disk space confirmed (>50% free)
- [ ] Memory available (>2GB free)
- [ ] Database backup running and completing
- [ ] Monitoring alerts all green

**Time**: _________ | **Owner**: _________ | **Status**: ✓

##### Team Assembly

- [ ] DevOps team in command center (Slack/Teams war room)
- [ ] Support team on standby
- [ ] Business owner/PM available for decisions
- [ ] DBA on call for database issues
- [ ] Developer on call for code issues

**Time**: _________ | **Owner**: _________ | **Status**: ✓

##### Communications Ready

- [ ] Maintenance announcement sent to all users
- [ ] Status page deployed showing "Maintenance in Progress"
- [ ] Slack notifications configured
- [ ] Email support notification sent
- [ ] Expected completion time communicated

**Time**: _________ | **Owner**: _________ | **Status**: ✓

---

#### Cutover Phase (Actual Go-Live)

##### Pre-Cutover Validation (1 Hour Before)

- [ ] Final backup completed

```bash
docker-compose exec db pg_dump odoo > /backups/pre_golive_$(date +%s).sql
```

- [ ] Backup verified (test restore on separate instance)
- [ ] Git repository at correct commit/tag
- [ ] All environment variables set correctly
- [ ] Database connection string verified

**Time**: _________ | **Executed By**: _________ | **Status**: ✓

##### System Shutdown (Production Traffic Stop)

- [ ] DNS updated (if domain change needed)
- [ ] Application server stopped gracefully

```bash
docker-compose stop odoo
```

- [ ] New containers pulled/built

```bash
docker-compose pull && docker-compose build
```

- [ ] Health checks disabled temporarily

**Time**: _________ | **Executed By**: _________ | **Status**: ✓

##### Data Migration Execution

- [ ] Migration script executed:

```bash
docker-compose exec odoo python migrate_data.py
```

- [ ] Data validation checks passed
- [ ] Record counts verified against source
- [ ] Data integrity checks all green
- [ ] No orphaned records detected

**Time**: _________ | **Executed By**: _________ | **Status**: ✓
**Records Migrated**: _________ (Expense records, Equipment records, etc.)

##### Application Startup

- [ ] Odoo container started

```bash
docker-compose up -d odoo
```

- [ ] Health check endpoint responding (✓ status)
- [ ] Application logs show no errors
- [ ] Database connection established
- [ ] All modules loaded successfully

**Time**: _________ | **Executed By**: _________ | **Status**: ✓

##### Production Smoke Testing (15-30 Minutes)

- [ ] Login page accessible
- [ ] Admin login successful
- [ ] Dashboard loads without errors
- [ ] Sample expense record retrieves data correctly
- [ ] Equipment module responsive
- [ ] Sample report generates successfully
- [ ] File attachments working
- [ ] Pagination working on large lists

**Time**: _________ | **Executed By**: _________ | **Status**: ✓

##### External Integration Verification

- [ ] GL posting integration working (if applicable)
- [ ] Email notifications sending (test email)
- [ ] External APIs responding (if any)
- [ ] Third-party integrations functional

**Time**: _________ | **Executed By**: _________ | **Status**: ✓

---

#### Post-Launch (Next 4 Hours)

##### Production Traffic Enabled

- [ ] Maintenance page removed
- [ ] Status page set to "Operational"
- [ ] DNS changes propagated (if applicable)
- [ ] Users notified that system is live
- [ ] Support team accepting tickets

**Time**: _________ | **Executed By**: _________ | **Status**: ✓

##### Real-World Usage Validation (First Hour)

- [ ] Monitor error logs for exceptions
- [ ] Monitor slow query logs
- [ ] Check user activity indicators
- [ ] CPU, memory, disk I/O within normal ranges
- [ ] Database connections stable
- [ ] No cascading failures detected

**Time**: _________ | **Owner**: _________ | **Status**: ✓

##### User Issue Resolution (Real-Time Support)

- [ ] First user tickets responded to within 15 min
- [ ] Critical issues escalated immediately
- [ ] Known issues documented in real-time
- [ ] Workarounds communicated
- [ ] Status updates sent every 30 min (if issues)

**Time**: _________ | **Owner**: _________ | **Status**: ✓

##### Stabilization Period (Next 3 Hours)

- [ ] Monitor for memory leaks (check process memory)
- [ ] Monitor for connection pool exhaustion
- [ ] Check for database lock contention
- [ ] Verify backup cron jobs scheduled
- [ ] Test email notifications work with real users
- [ ] Verify concurrent user limits respected

**Time**: _________ | **Owner**: _________ | **Status**: ✓

---

### ✅ Post-Go-Live Sign-Off

#### Technical Go-Live Sign-Off

- [ ] All smoke tests passed
- [ ] No critical production issues
- [ ] Monitoring showing normal operation
- [ ] Database integrity verified
- [ ] Backup/restore procedures validated

**Signed By**: _________________________ (DevOps Lead)
**Date/Time**: _________________________ (Go-Live Official Time)

#### Business Go-Live Sign-Off

- [ ] Core business processes working
- [ ] Users able to perform critical tasks
- [ ] Data integrity confirmed
- [ ] Performance acceptable
- [ ] No blockers to daily operations

**Signed By**: _________________________ (Business Owner)
**Date/Time**: _________________________

---

## 📊 POST-GO-LIVE PHASE (1-4 Weeks)

### Week 1: Stabilization & Monitoring

#### Daily Health Checks (First 7 Days)

- [ ] 8 AM: Daily standup review of issues
- [ ] Noon: Mid-day spot check
- [ ] 5 PM: End-of-day status report
- [ ] All critical issues resolved
- [ ] Documentation updated with findings

**Owner**: [DevOps/Support Lead]

#### Performance Monitoring

- [ ] Response times tracked and documented
- [ ] Error rates monitored
- [ ] Database performance baseline established
- [ ] Slow queries identified and optimized
- [ ] Cache hit rates verified

**Owner**: [DevOps Lead]

#### User Feedback Collection

- [ ] User feedback survey sent (Day 3)
- [ ] Critical feature requests logged
- [ ] Usability issues documented
- [ ] Training gap analysis completed

**Owner**: [Product Manager]

#### Support Metrics

- [ ] Track response times (target: <15 min)
- [ ] Track resolution times (target: <2 hours for high-priority)
- [ ] Identify recurring issues
- [ ] Update FAQ with common questions

**Owner**: [Support Lead]

---

### Week 2-4: Optimization & Refinement

#### Performance Optimization

- [ ] Implement database query optimizations
- [ ] Configure caching where beneficial
- [ ] Enable compression for static assets
- [ ] Optimize report generation performance

**Owner**: [DevOps/Developer Lead]

#### Bug Fix Sprint

- [ ] All P0/P1 bugs resolved
- [ ] P2 bugs triaged and prioritized
- [ ] Patches deployed in controlled manner
- [ ] Change log updated

**Owner**: [Development Team]

#### Documentation Refinement

- [ ] Update docs based on user feedback
- [ ] Record additional video tutorials
- [ ] Expand FAQ section
- [ ] Create runbooks for common issues

**Owner**: [Technical Writer]

#### Team Handoff to Operations

- [ ] Runbooks finalized
- [ ] Ops team confidence level assessed
- [ ] On-call procedures validated
- [ ] Escalation paths confirmed

**Owner**: [Project Manager]

---

## 🔄 Rollback Plan (If Needed)

**Rollback Criteria**: If critical production issues prevent normal business operations

### Decision Criteria Met (Any of the following)

- [ ] More than 50% of users unable to access system
- [ ] Data corruption detected
- [ ] Security breach confirmed
- [ ] Core business processes (expense, equipment) down >30 min

**Time to Decide**: Within 30 minutes of issue identification

### Rollback Execution

- [ ] Notify all stakeholders immediately
- [ ] Stop current Odoo container
- [ ] Restore database from pre-go-live backup

```bash
docker-compose exec db psql -U odoo < /backups/pre_golive_TIMESTAMP.sql
```

- [ ] Restart with previous version
- [ ] Verify previous system fully operational
- [ ] Provide root cause analysis within 24 hours

### Communication During Rollback

- [ ] Status update every 15 minutes
- [ ] Estimated time to recovery provided
- [ ] Post-mortem scheduled for next day

**Owner**: [Project Manager / DevOps Lead]

---

## 📞 Contact & Escalation Matrix

| Role | Name | Email | Phone | Availability |
|------|------|-------|-------|--------------|
| Go-Live Lead | [Name] | [Email] | [Phone] | 24/7 (Go-Live Day) |
| DevOps Lead | [Name] | [Email] | [Phone] | 24/7 (Go-Live Week) |
| Database Admin | [Name] | [Email] | [Phone] | On-call |
| Developer Lead | [Name] | [Email] | [Phone] | On-call |
| Business Owner | [Name] | [Email] | [Phone] | Available for decisions |
| Support Manager | [Name] | [Email] | [Phone] | Primary support contact |

---

## 📅 Timeline Summary

| Phase | Duration | Key Activities | Owner |
|-------|----------|----------------|-------|
| Pre-Flight (Weeks -4 to -2) | 2 weeks | Code review, testing, docs | All teams |
| Final Validation (Days -3 to -1) | 3 days | Staging dry-run, team readiness | DevOps/QA |
| Go-Live Day (Day 0) | 4-8 hours | Cutover, smoke tests, launch | All teams |
| Stabilization (Week +1) | 7 days | Monitoring, issue resolution | DevOps/Support |
| Optimization (Weeks +2-4) | 3 weeks | Performance tuning, bug fixes | Dev/DevOps |

---

**Document Version**: 1.0
**Last Updated**: December 22, 2025
**Next Review Date**: [Date - 2 weeks before go-live]

---

*This comprehensive checklist ensures a smooth, professional go-live with clear ownership, accountability, and rollback procedures. Customize the dates, names, and specific requirements to match your actual timeline and organization.*
