# Odoo 19 Migration - Product Requirements Document
---
**Status**: APPROVED
**Owner**: Jake Tolentino (Technical Lead)
**Created**: 2026-01-26
**Target**: Q3-Q4 2026
**Epic**: IPAI-ODOO19
---

## 1. Executive Summary

Migrate InsightPulse AI ERP stack from Odoo 18 CE to Odoo 19 CE while maintaining:
- 100% feature parity with current ipai_* modules
- Zero data loss during migration
- Minimal downtime (<4 hours)
- Full BIR compliance continuity

### Business Case

| Metric | Current (Odoo 18) | Target (Odoo 19) | Impact |
|--------|-------------------|------------------|--------|
| Performance | Baseline | +30% faster | Reduced wait times |
| Python Version | 3.10 | 3.12 | Security + speed |
| OWL Framework | OWL 1.x | OWL 2.x | Better UX |
| API | REST/RPC | GraphQL-ready | Developer velocity |
| Support | Until 2027 | Until 2029 | Extended LTS |

### Cost Estimate

| Item | Hours | Rate | Cost |
|------|-------|------|------|
| Module Migration (80+ modules) | 160 | $50/hr | $8,000 |
| Testing & QA | 40 | $50/hr | $2,000 |
| Infrastructure | 20 | $50/hr | $1,000 |
| Contingency (20%) | 44 | $50/hr | $2,200 |
| **Total** | **264** | - | **$13,200** |

Infrastructure delta: +$50/month (parallel staging environment)

---

## 2. Problem Statement

### Current State
- Odoo 18 CE deployed at erp.insightpulseai.com
- 80+ ipai_* custom modules
- 15+ OCA dependencies
- PostgreSQL 16 on DigitalOcean Managed DB
- Finance SSC operations for 8 agencies

### Pain Points
1. **Technical Debt**: Some modules use deprecated Odoo 17 patterns
2. **Performance**: Large reports (>10k records) slow
3. **UX**: OWL 1.x limitations in complex forms
4. **Security**: Python 3.10 EOL approaching (Oct 2026)

### Opportunity
Odoo 19 introduces:
- OWL 2.x with better reactivity
- Improved spreadsheet integration
- Enhanced AI/ML hooks
- GraphQL API foundation
- Python 3.12 requirement (faster, more secure)

---

## 3. Goals & Non-Goals

### Goals
1. ✅ Migrate all 80+ ipai_* modules to Odoo 19 compatibility
2. ✅ Upgrade OCA dependencies to Odoo 19 versions
3. ✅ Maintain 100% feature parity (EE parity score ≥80%)
4. ✅ Zero data loss during migration
5. ✅ Downtime <4 hours for production cutover
6. ✅ Pass all BIR compliance audits post-migration

### Non-Goals
1. ❌ Add new features during migration (separate roadmap)
2. ❌ Migrate to Odoo Enterprise (stay CE + OCA + ipai_*)
3. ❌ Change infrastructure provider (stay DigitalOcean)
4. ❌ Redesign UI/UX (cosmetic only)

---

## 4. Success Criteria

### Must Have (P0)
- [ ] All ipai_* modules install without errors on Odoo 19
- [ ] All automated tests pass (pytest + Odoo test framework)
- [ ] EE parity score ≥80% (run test_ee_parity.py)
- [ ] BIR reports (1601-C, 2316, Alphalist) generate correctly
- [ ] Bank reconciliation works with existing statement imports
- [ ] Payroll computes correct SSS/PhilHealth/Pag-IBIG/Tax

### Should Have (P1)
- [ ] Performance improvement ≥20% on key operations
- [ ] OWL 2.x migration for all custom JS components
- [ ] API response time <500ms for standard CRUD
- [ ] Mobile responsiveness improved

### Nice to Have (P2)
- [ ] GraphQL API enabled for external integrations
- [ ] Spreadsheet integration with Superset
- [ ] AI-assisted data entry (experimental)

---

## 5. User Stories

### Finance Team (CKVC, RIM, BOM)
```
As a Finance Manager,
I want the system to work identically after migration,
So that month-end closing and BIR filing are not disrupted.

Acceptance Criteria:
- All existing reports accessible
- All approval workflows functional
- All bank integrations working
- Performance same or better
```

### Accountants (LAS, JAP, JPAL, JLI)
```
As an Accountant,
I want faster report generation,
So that I can complete reconciliations more quickly.

Acceptance Criteria:
- Trial balance generates <10s (currently ~30s)
- Bank reconciliation matching works correctly
- Journal entry posting unchanged
```

### IT Admin (Jake)
```
As the Technical Lead,
I want automated migration validation,
So that I can confidently deploy to production.

Acceptance Criteria:
- CI/CD pipeline validates Odoo 19 compatibility
- Automated rollback tested and documented
- Monitoring dashboards updated
```

---

## 6. Technical Requirements

### 6.1 Module Compatibility Matrix

| Module Category | Count | Complexity | Est. Hours |
|-----------------|-------|------------|------------|
| ipai_hr_payroll_ph | 1 | High | 16 |
| ipai_approvals | 1 | Medium | 8 |
| ipai_helpdesk | 1 | Medium | 8 |
| ipai_planning | 1 | Medium | 8 |
| ipai_bir_* | 5 | High | 24 |
| ipai_connector_* | 4 | Low | 8 |
| ipai_* (other) | 67 | Low-Medium | 88 |
| **Total** | **80** | - | **160** |

### 6.2 Breaking Changes to Address

| Odoo 19 Change | Impact | Migration Action |
|----------------|--------|------------------|
| `<tree>` → `<list>` | All list views | Find/replace + test |
| OWL 2.x | Custom JS widgets | Rewrite components |
| Python 3.12 | Type hints, async | Update syntax |
| API versioning | External integrations | Update endpoints |
| Asset bundling | Custom CSS/JS | Migrate to new system |

### 6.3 Database Migration

```sql
-- Pre-migration backup
pg_dump -Fc odoo_prod > odoo18_backup_$(date +%Y%m%d).dump

-- Migration steps (handled by Odoo upgrade scripts)
-- 1. Schema updates (automatic)
-- 2. Data transformations (automatic)
-- 3. Custom field migrations (manual review)

-- Post-migration validation
SELECT COUNT(*) FROM account_move;  -- Compare with pre-migration
SELECT COUNT(*) FROM hr_payslip;    -- Compare with pre-migration
```

### 6.4 Infrastructure Requirements

| Component | Current | Migration | Post-Migration |
|-----------|---------|-----------|----------------|
| Odoo Image | odoo:18.0 | odoo:19.0 | odoo:19.0 |
| Python | 3.10 | 3.12 | 3.12 |
| PostgreSQL | 16 | 16 | 16 (no change) |
| RAM | 4GB | 6GB (staging) | 4GB |
| Storage | 50GB | 100GB (dual) | 50GB |

---

## 7. Migration Phases

### Phase 1: Preparation (Week 1-2)
- [ ] Audit all ipai_* modules for deprecated patterns
- [ ] Create Odoo 19 development sandbox
- [ ] Document all breaking changes
- [ ] Update CI/CD for dual-version testing

### Phase 2: Module Migration (Week 3-6)
- [ ] Migrate core modules (accounting, HR, payroll)
- [ ] Migrate service modules (helpdesk, planning)
- [ ] Migrate integration modules (connectors)
- [ ] Update all unit tests

### Phase 3: Testing (Week 7-8)
- [ ] Run EE parity test suite
- [ ] UAT with Finance team
- [ ] Performance benchmarking
- [ ] Security audit

### Phase 4: Deployment (Week 9)
- [ ] Final backup of production
- [ ] Blue-green deployment
- [ ] Smoke tests
- [ ] Monitoring validation

### Phase 5: Stabilization (Week 10-12)
- [ ] Monitor production
- [ ] Fix post-migration issues
- [ ] Documentation updates
- [ ] Decommission Odoo 18 staging

---

## 8. Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| OCA module not ready for Odoo 19 | Medium | High | Fork and maintain internally |
| Data corruption during migration | Low | Critical | Multiple backups, dry-run first |
| Extended downtime | Medium | High | Blue-green deployment |
| Performance regression | Low | Medium | Benchmark before/after |
| BIR compliance failure | Low | Critical | Manual validation of all forms |

---

## 9. Rollback Plan

### Trigger Conditions
- Critical bug affecting >50% of users
- Data integrity issues discovered
- BIR compliance failure
- Performance degradation >50%

### Rollback Steps
```bash
# 1. Stop Odoo 19
docker compose -f docker-compose.prod.yml down

# 2. Restore database
pg_restore -d odoo_prod odoo18_backup_YYYYMMDD.dump

# 3. Start Odoo 18
docker compose -f docker-compose.prod.v18.yml up -d

# 4. Notify stakeholders
# 5. Post-mortem analysis
```

### RTO/RPO
- **RTO** (Recovery Time Objective): 2 hours
- **RPO** (Recovery Point Objective): 4 hours (last backup)

---

## 10. Stakeholder Sign-Off

| Role | Name | Approval | Date |
|------|------|----------|------|
| Technical Lead | Jake Tolentino | ☐ Pending | |
| Finance Director | CKVC | ☐ Pending | |
| Project Sponsor | TBD | ☐ Pending | |

---

## Appendix A: Module Inventory

See `docs/MODULE_INVENTORY.md` for complete list of 80+ modules.

## Appendix B: OCA Dependencies

| OCA Module | Current Version | Odoo 19 Status |
|------------|-----------------|----------------|
| account_financial_report | 18.0.1.0 | TBD |
| account_reconcile_oca | 18.0.1.0 | TBD |
| hr_expense | 18.0.1.0 | TBD |
| helpdesk_mgmt | 18.0.1.0 | TBD |
| ... | ... | ... |

## Appendix C: References

- Odoo 19 Release Notes: https://www.odoo.com/documentation/19.0/
- OCA Migration Guide: https://github.com/OCA/maintainer-tools
- Internal: docs/ODOO_19_MIGRATION_STRATEGY.md
