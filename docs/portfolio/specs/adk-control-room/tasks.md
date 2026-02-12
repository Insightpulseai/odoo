# ADK Control Room — Task Checklist

## Foundation (Phase 1)

### Database Schema
- [ ] Create Supabase migration file for `cr_runs` table
- [ ] Create Supabase migration file for `cr_jobs` table
- [ ] Create Supabase migration file for `cr_lineage` table
- [ ] Create Supabase migration file for `cr_artifacts` table
- [ ] Add indexes for performance (status, idempotency_key, run_id)
- [ ] Implement RLS policies for all tables
- [ ] Test RLS policies with different roles (admin, finance_lead, auditor, agent)
- [ ] Create database backup strategy
- [ ] Document schema in `docs/DATABASE_SCHEMA.md`

### ADK-TS Runtime
- [ ] Scaffold ADK-TS project structure
- [ ] Define `Tool` interface in TypeScript
- [ ] Implement `runJob` tool
- [ ] Implement `catalogLookup` tool
- [ ] Implement `writeLineage` tool
- [ ] Implement `uploadArtifact` tool
- [ ] Create tool registry with validation
- [ ] Add tool input/output schema validation (Zod or JSON Schema)
- [ ] Write unit tests for each tool (≥80% coverage)
- [ ] Document tool contracts in `docs/TOOL_CONTRACTS.md`

### Agent Runtime
- [ ] Define `Agent` interface in TypeScript
- [ ] Create agent registry
- [ ] Implement agent execution framework
- [ ] Add agent composition support (planner → executor → verifier)
- [ ] Implement multi-agent workflows (sequential, parallel)
- [ ] Add error handling + rollback logic
- [ ] Write integration tests for agent workflows
- [ ] Document agent patterns in `docs/AGENT_PATTERNS.md`

### Job API
- [ ] Create Next.js API route: `POST /api/jobs/run`
- [ ] Implement idempotency key validation
- [ ] Add job state machine (queued → running → success/failed)
- [ ] Implement job queuing (Redis or Supabase)
- [ ] Add job execution worker
- [ ] Implement timeout enforcement
- [ ] Add priority queuing
- [ ] Create API documentation (OpenAPI spec)
- [ ] Write API integration tests
- [ ] Deploy API to staging environment

## Orchestration (Phase 2)

### Job State Machine
- [ ] Implement state transitions (queued → running → success/failed/cancelled)
- [ ] Add state validation (prevent invalid transitions)
- [ ] Implement job status query endpoint: `GET /api/runs/{id}`
- [ ] Add job cancellation endpoint: `POST /api/runs/{id}/cancel`
- [ ] Implement job logs streaming
- [ ] Write state machine tests

### Idempotency
- [ ] Add idempotency key uniqueness constraint
- [ ] Implement duplicate detection logic
- [ ] Test duplicate submission behavior
- [ ] Document idempotency patterns in `docs/IDEMPOTENCY.md`

### Logging & Metrics
- [ ] Implement structured logging (Winston or Pino)
- [ ] Add log persistence to Supabase
- [ ] Implement Prometheus metrics export
- [ ] Create Grafana dashboards
- [ ] Add alerting rules (Alertmanager)
- [ ] Test observability stack end-to-end

## Docs → Code (Phase 3)

### Continue Headless Worker
- [ ] Set up Continue headless service
- [ ] Configure file watchers (`/spec/**/*.md`, `/docs/**/*.md`)
- [ ] Implement spec change handler
- [ ] Add spec validation agent
- [ ] Implement PR generation agent
- [ ] Test Continue integration end-to-end
- [ ] Document Continue setup in `docs/CONTINUE_SETUP.md`

### Spec Validation
- [ ] Implement spec bundle validator
- [ ] Add validation rules:
  - [ ] Constitution exists
  - [ ] PRD exists
  - [ ] Plan exists
  - [ ] Tasks exist
  - [ ] Tool contracts valid
  - [ ] No hardcoded secrets
  - [ ] No direct DB mutation
- [ ] Create validation error messages
- [ ] Test validation with invalid specs
- [ ] Document validation rules in `docs/SPEC_VALIDATION.md`

### PR Automation
- [ ] Create PR template
- [ ] Implement PR generation logic
- [ ] Add GitHub API integration
- [ ] Test PR creation flow
- [ ] Add CI spec validation workflow
- [ ] Document PR workflow in `docs/PR_AUTOMATION.md`

### Artifact Capture
- [ ] Configure Supabase Storage bucket (`artifacts`)
- [ ] Implement artifact upload logic
- [ ] Add artifact metadata storage
- [ ] Test artifact retrieval
- [ ] Implement artifact cleanup (7-year retention)
- [ ] Document artifact storage in `docs/ARTIFACTS.md`

## Business Integration (Phase 4)

### Odoo Approval Hooks
- [ ] Create `ipai.control_room.approval` Odoo model
- [ ] Add approval workflow (pending → approved → rejected)
- [ ] Implement approval check API
- [ ] Add approval gate to job execution
- [ ] Test approval workflow end-to-end
- [ ] Document approval process in `docs/APPROVALS.md`

### Period Locks
- [ ] Create `ipai.finance.period_lock` Odoo model
- [ ] Implement period lock check API
- [ ] Add period lock gate to job execution
- [ ] Test period lock enforcement
- [ ] Document period locks in `docs/PERIOD_LOCKS.md`

### SLA + Escalation
- [ ] Define SLA configuration (YAML)
- [ ] Implement SLA monitoring cron job
- [ ] Add escalation notification logic
- [ ] Test escalation flow
- [ ] Document SLA policies in `docs/SLA_POLICIES.md`

### Result Write-Back
- [ ] Create `ipai.control_room.result` Odoo model
- [ ] Implement result write-back API
- [ ] Add artifact attachment to Odoo
- [ ] Test result persistence
- [ ] Document write-back process in `docs/RESULT_WRITEBACK.md`

## CI/CD (Phase 5)

### Spec Validation CI
- [ ] Create GitHub Actions workflow: `spec-validation.yml`
- [ ] Add spec bundle validation step
- [ ] Add tool contract validation step
- [ ] Add security scan (no secrets in code)
- [ ] Test CI workflow with invalid specs
- [ ] Document CI workflow in `docs/CI_CD.md`

### Agent Tests
- [ ] Write unit tests for all agents
- [ ] Write integration tests for multi-agent workflows
- [ ] Add test coverage reporting
- [ ] Enforce ≥80% coverage gate
- [ ] Document testing patterns in `docs/TESTING.md`

### Tool Contract Tests
- [ ] Write contract tests for all tools
- [ ] Add input validation tests
- [ ] Add output validation tests
- [ ] Test error handling
- [ ] Document contract testing in `docs/TOOL_TESTING.md`

## Production Hardening (Phase 6)

### Visual Lineage UI
- [ ] Set up D3.js force-directed graph
- [ ] Implement lineage query API: `GET /api/lineage/graph`
- [ ] Add lineage visualization component
- [ ] Test lineage graph rendering
- [ ] Add lineage search/filter
- [ ] Document lineage UI in `docs/LINEAGE_UI.md`

### Retry Policies
- [ ] Define retry configuration (YAML)
- [ ] Implement retry with exponential backoff
- [ ] Add circuit breaker pattern
- [ ] Test retry behavior
- [ ] Document retry policies in `docs/RETRY_POLICIES.md`

### RBAC / RLS
- [ ] Define roles (admin, platform_engineer, finance_lead, auditor, agent)
- [ ] Implement RLS policies for each role
- [ ] Add role-based API authorization
- [ ] Test RBAC enforcement
- [ ] Document RBAC in `docs/RBAC.md`

### Observability
- [ ] Set up Prometheus metrics export
- [ ] Create Grafana dashboards:
  - [ ] Job submissions
  - [ ] Job success rate
  - [ ] Job duration (P95)
  - [ ] Lineage coverage
- [ ] Configure Alertmanager rules
- [ ] Test observability stack
- [ ] Document observability in `docs/OBSERVABILITY.md`

## Deployment

### Staging Deployment
- [ ] Deploy to staging environment (159.223.75.148)
- [ ] Run smoke tests
- [ ] Validate all acceptance criteria
- [ ] Document staging deployment in `docs/STAGING_DEPLOYMENT.md`

### Production Deployment
- [ ] Deploy to production (DigitalOcean App Platform)
- [ ] Run production smoke tests
- [ ] Monitor metrics for 24 hours
- [ ] Document production deployment in `docs/PRODUCTION_DEPLOYMENT.md`

### Rollback Plan
- [ ] Create rollback procedure
- [ ] Test rollback flow
- [ ] Document rollback in `docs/ROLLBACK.md`

## Documentation

### User Guides
- [ ] Control Room Overview (`docs/CONTROL_ROOM_OVERVIEW.md`)
- [ ] Job Submission Guide (`docs/JOB_SUBMISSION.md`)
- [ ] Lineage Query Guide (`docs/LINEAGE_QUERIES.md`)
- [ ] Approval Workflow Guide (`docs/APPROVAL_WORKFLOW.md`)

### Developer Guides
- [ ] Agent Development Guide (`docs/AGENT_DEVELOPMENT.md`)
- [ ] Tool Development Guide (`docs/TOOL_DEVELOPMENT.md`)
- [ ] Testing Guide (`docs/TESTING_GUIDE.md`)
- [ ] Deployment Guide (`docs/DEPLOYMENT_GUIDE.md`)

### Operations Guides
- [ ] Monitoring Guide (`docs/MONITORING.md`)
- [ ] Troubleshooting Guide (`docs/TROUBLESHOOTING.md`)
- [ ] Incident Response Guide (`docs/INCIDENT_RESPONSE.md`)
- [ ] Backup & Recovery Guide (`docs/BACKUP_RECOVERY.md`)

## Task Summary

- **Foundation**: 29 tasks
- **Orchestration**: 12 tasks
- **Docs → Code**: 13 tasks
- **Business Integration**: 14 tasks
- **CI/CD**: 11 tasks
- **Production Hardening**: 17 tasks
- **Deployment**: 7 tasks
- **Documentation**: 12 tasks

**Total**: 115 tasks

## Progress Tracking

- [ ] Phase 1 Complete (Foundation)
- [ ] Phase 2 Complete (Orchestration)
- [ ] Phase 3 Complete (Docs → Code)
- [ ] Phase 4 Complete (Business Integration)
- [ ] Phase 5 Complete (CI/CD)
- [ ] Phase 6 Complete (Production Hardening)
- [ ] Staging Deployment Complete
- [ ] Production Deployment Complete

## Version History

- **v1.0.0** (2025-11-24): Initial task checklist
  - 115 tasks defined across 6 phases
  - Documentation tasks added
  - Deployment tasks specified
