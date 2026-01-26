# Odoo 19 Migration — Task Checklist

---

**Status**: NOT STARTED
**Created**: 2026-01-26
**Last Updated**: 2026-01-26

---

## Task Legend

| Status | Symbol | Meaning |
|--------|--------|---------|
| Not Started | `[ ]` | Task not yet begun |
| In Progress | `[~]` | Task actively being worked |
| Completed | `[x]` | Task finished and verified |
| Blocked | `[!]` | Task blocked by dependency |
| Deferred | `[-]` | Task postponed |

---

## Phase 0: Preparation

### 0.1 Module Audit

- [ ] Create module inventory script (`scripts/audit_ipai_modules.py`)
- [ ] Run audit on all 80+ IPAI modules
- [ ] Generate `docs/IPAI_MODULE_AUDIT.md`
- [ ] Identify deprecated API usage
- [ ] Document API changes for Odoo 19
- [ ] Create `docs/API_CHANGES_ODOO_19.md`
- [ ] Prioritize modules by migration complexity
- [ ] Estimate effort per module

### 0.2 OCA Dependency Check

- [ ] List all OCA dependencies from `oca.lock.json`
- [ ] Check 19.0 branch availability for each OCA repo
  - [ ] OCA/web
  - [ ] OCA/account-financial-tools
  - [ ] OCA/account-financial-reporting
  - [ ] OCA/account-invoicing
  - [ ] OCA/sale-workflow
  - [ ] OCA/purchase-workflow
  - [ ] OCA/stock-logistics-workflow
  - [ ] OCA/hr
  - [ ] OCA/project
  - [ ] OCA/partner-contact
  - [ ] OCA/server-tools
  - [ ] OCA/queue
- [ ] Identify modules without 19.0 branches
- [ ] Research alternatives or plan forks
- [ ] Update `oca.lock.json` with 19.0 targets (dry run)

### 0.3 Test Suite Enhancement

- [ ] Run current test coverage analysis
- [ ] Generate coverage report
- [ ] Identify critical paths with low coverage
- [ ] Write new tests for:
  - [ ] `ipai_dev_studio_base`
  - [ ] `ipai_workspace_core`
  - [ ] `ipai_ce_branding`
  - [ ] `ipai_ai_core`
  - [ ] `ipai_finance_ppm`
  - [ ] `ipai_n8n_connector`
  - [ ] `ipai_mattermost_connector`
- [ ] Achieve 80%+ coverage on P0 modules

### 0.4 Integration Test Suite

- [ ] Document current integration endpoints
- [ ] Create integration test for n8n XML-RPC
- [ ] Create integration test for n8n REST API
- [ ] Create integration test for Mattermost webhooks
- [ ] Create integration test for MCP server connections
- [ ] Create integration test for Supabase sync
- [ ] Create `docs/INTEGRATION_BASELINE.md`

### 0.5 Performance Baseline

- [ ] Define performance metrics to capture
- [ ] Create performance baseline script
- [ ] Run baseline on Odoo 18 production
- [ ] Generate `docs/PERFORMANCE_BASELINE_18.md`
- [ ] Define performance targets for Odoo 19

---

## Phase 1: Sandbox Testing

### 1.1 Odoo 19 Development Environment

- [ ] Wait for Odoo 19 CE official release
- [ ] Create feature branch `feat/odoo-19-migration`
- [ ] Create `docker/Dockerfile.odoo19`
- [ ] Create `docker-compose.odoo19.yml`
- [ ] Create `config/odoo19.conf`
- [ ] Build and test Odoo 19 container
- [ ] Verify base Odoo 19 functionality
- [ ] Document any Odoo 19 breaking changes discovered

### 1.2 Core Module Porting

- [ ] Port `ipai_dev_studio_base`
  - [ ] Update Python API calls
  - [ ] Update XML views
  - [ ] Update JavaScript/OWL components
  - [ ] Run unit tests
  - [ ] Fix failures
- [ ] Port `ipai_workspace_core`
  - [ ] Update Python API calls
  - [ ] Update XML views
  - [ ] Update JavaScript/OWL components
  - [ ] Run unit tests
  - [ ] Fix failures
- [ ] Port `ipai_ce_branding`
  - [ ] Update Python API calls
  - [ ] Update XML views
  - [ ] Update JavaScript/OWL components
  - [ ] Run unit tests
  - [ ] Fix failures
- [ ] Port `ipai_ai_core`
  - [ ] Update Python API calls
  - [ ] Update XML views
  - [ ] Update JavaScript/OWL components
  - [ ] Run unit tests
  - [ ] Fix failures

### 1.3 Migration Script Development

- [ ] Create `scripts/migrate_module.sh`
- [ ] Implement common API migration patterns
- [ ] Implement XML view migration patterns
- [ ] Implement JavaScript/OWL migration patterns
- [ ] Test migration script on sample modules
- [ ] Document migration patterns

### 1.4 OCA Module Validation

- [ ] Clone OCA 19.0 branches
- [ ] Test OCA/web on Odoo 19
- [ ] Test OCA/account-* modules on Odoo 19
- [ ] Test OCA/sale-workflow on Odoo 19
- [ ] Test OCA/purchase-workflow on Odoo 19
- [ ] Test remaining OCA modules
- [ ] Fork and fix any incompatible modules
- [ ] Update `oca.lock.json` with verified 19.0 pins

---

## Phase 2: Staging Migration

### 2.1 Full Module Migration

- [ ] Port remaining IPAI modules (by priority)
  - [ ] P0 AI/Agents modules (10)
  - [ ] P0 Finance modules (15)
  - [ ] P0 Platform modules (12)
  - [ ] P0 Integration modules (6)
  - [ ] P1 Workspace modules (8)
  - [ ] P1 Studio modules (10)
  - [ ] P1 Industry modules (6)
  - [ ] P2 WorkOS modules (8)
  - [ ] P2 Theme/UI modules (5)
- [ ] Run full test suite
- [ ] Achieve 100% unit test pass rate
- [ ] Generate migration log

### 2.2 Data Migration Testing

- [ ] Create anonymized production snapshot
- [ ] Run database migration script
- [ ] Validate record counts (pre/post)
- [ ] Validate financial balances
- [ ] Validate attachments
- [ ] Validate users/permissions
- [ ] Generate data integrity report
- [ ] Measure migration time

### 2.3 Integration Testing

- [ ] Deploy staging Odoo 19 environment
- [ ] Test n8n workflows against staging
  - [ ] Create record via XML-RPC
  - [ ] Read record via XML-RPC
  - [ ] Update record via XML-RPC
  - [ ] Test REST API authentication
  - [ ] Test REST API CRUD
- [ ] Test Mattermost integration
  - [ ] Slash command handling
  - [ ] Webhook notifications
  - [ ] ChatOps workflows
- [ ] Test MCP server connections
  - [ ] Odoo ERP server
  - [ ] Agent queries
  - [ ] Tool calls
- [ ] Test Supabase sync
  - [ ] Trigger firing
  - [ ] Data flow validation
- [ ] Generate integration test report

### 2.4 Load Testing

- [ ] Set up load testing environment
- [ ] Configure test scenarios (50 users, 30 min)
- [ ] Run load tests
- [ ] Capture performance metrics
- [ ] Compare with Odoo 18 baseline
- [ ] Identify bottlenecks
- [ ] Optimize if needed
- [ ] Generate load test report

### 2.5 User Acceptance Testing

- [ ] Recruit UAT participants
- [ ] Create UAT test cases
- [ ] Conduct UAT sessions
  - [ ] Login/logout flow
  - [ ] Dashboard rendering
  - [ ] Quote creation workflow
  - [ ] Order processing workflow
  - [ ] Invoice generation
  - [ ] Report generation
  - [ ] Custom views/filters
  - [ ] Mobile responsiveness
- [ ] Collect feedback
- [ ] Address critical issues
- [ ] Obtain UAT sign-off

---

## Phase 3: Production Migration

### 3.1 Pre-Migration Preparation

- [ ] Schedule maintenance window
- [ ] Announce to stakeholders (48h advance)
- [ ] Brief on-call team
- [ ] Prepare monitoring dashboards
- [ ] Test rollback procedure
- [ ] Create production backup
- [ ] Verify backup integrity
- [ ] Confirm go/no-go decision

### 3.2 Migration Execution

- [ ] Begin maintenance window
- [ ] Stop production services
- [ ] Create final backup
- [ ] Execute database migration
- [ ] Run data migration scripts
- [ ] Deploy Odoo 19 containers
- [ ] Run post-migration scripts
- [ ] Basic smoke test

### 3.3 Post-Migration Verification

- [ ] Verify all services healthy
- [ ] Verify database accessible
- [ ] Test user login
- [ ] Test core workflows
- [ ] Verify integration connections
- [ ] Run performance spot checks
- [ ] Make go/no-go decision
- [ ] If issues: execute rollback
- [ ] If success: announce completion
- [ ] End maintenance window

---

## Phase 4: Stabilization

### 4.1 Monitoring (Days 1-30)

- [ ] Enable enhanced monitoring
- [ ] Daily health check reviews
- [ ] Track error rates
- [ ] Monitor response times
- [ ] Watch database performance
- [ ] Check integration health
- [ ] Generate daily reports

### 4.2 Bug Resolution

- [ ] Triage incoming issues
- [ ] P0 bugs: fix within 1 hour
- [ ] P1 bugs: fix within 4 hours
- [ ] P2 bugs: fix within 24 hours
- [ ] P3 bugs: schedule for sprint
- [ ] Deploy hotfixes as needed
- [ ] Update test suite with regression tests

### 4.3 Documentation Update

- [ ] Update CLAUDE.md version references
- [ ] Update API documentation
- [ ] Update module documentation
- [ ] Update deployment guides
- [ ] Update architecture diagrams
- [ ] Review and update README files

### 4.4 Cleanup

- [ ] After 30 days: decommission Odoo 18 parallel
- [ ] Archive final Odoo 18 backup
- [ ] Remove temporary migration scripts
- [ ] Clean up staging environments
- [ ] Update CI/CD pipelines
- [ ] Close migration project

---

## Blocked Tasks

*No tasks currently blocked.*

---

## Deferred Tasks

*No tasks currently deferred.*

---

## Completion Summary

| Phase | Total Tasks | Completed | Percentage |
|-------|-------------|-----------|------------|
| Phase 0: Preparation | 35 | 0 | 0% |
| Phase 1: Sandbox | 32 | 0 | 0% |
| Phase 2: Staging | 42 | 0 | 0% |
| Phase 3: Production | 21 | 0 | 0% |
| Phase 4: Stabilization | 20 | 0 | 0% |
| **Total** | **150** | **0** | **0%** |

---

## Notes

- Phase 0 can begin immediately (preparation work)
- Phase 1-4 blocked on Odoo 19 CE official release
- Update this document as tasks complete
- Add new tasks as discovered during migration

---

*Last Updated: 2026-01-26*
