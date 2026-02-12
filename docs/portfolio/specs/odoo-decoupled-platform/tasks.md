# Tasks: Odoo Decoupled Platform

> Implementation checklist with status tracking.

## Legend
- ✅ Complete
- 🔄 In Progress
- ⏳ Pending
- ❌ Blocked

---

## Phase 1: Foundation

### Spec Infrastructure
- [x] Create spec/odoo-decoupled-platform/ directory structure
- [x] Write constitution.md with non-negotiables
- [x] Write prd.md with product requirements
- [x] Write plan.md with implementation plan
- [x] Write tasks.md (this file)

### Auth Specs
- [x] Create spec/auth/roles.yaml
- [ ] Add permission matrix to roles.yaml
- [ ] Document SSO configuration in spec/auth/sso.md

### Schema Specs
- [x] Create spec/schema/entities.yaml
- [ ] Add field-level documentation
- [ ] Generate DBML artifact

### CI Gates
- [x] Add .github/workflows/spec-gate.yml
- [ ] Add migration lint to existing workflow
- [ ] Add RLS verification step

---

## Phase 2: Database Layer

### Core Schemas
- [x] Create app schema (app.orgs, app.org_members)
- [x] Create odoo schema (odoo.instances, odoo.sync_cursors)
- [ ] Add app.projects table (example app entity)
- [ ] Add app.tasks table (example app entity)

### RLS Policies
- [x] Add org membership policies
- [ ] Add role-based policies (owner vs member)
- [ ] Add audit logging triggers

### Odoo Bridge
- [x] Create odoo.instances table
- [x] Create odoo.sync_cursors table
- [ ] Create odoo.webhook_events table
- [ ] Create odoo.entity_mappings table

---

## Phase 3: Sync Infrastructure

### Edge Functions
- [ ] Create supabase/functions/sync-from-odoo/
- [ ] Create supabase/functions/sync-to-odoo/
- [ ] Create supabase/functions/webhook-receiver/

### Sync Logic
- [ ] Implement cursor-based sync
- [ ] Implement exponential backoff
- [ ] Implement conflict resolution

### Event System
- [ ] Define event schema
- [ ] Create event processor
- [ ] Add dead-letter handling

---

## Phase 4: API Layer

### Type Generation
- [ ] Add codegen script for TypeScript types
- [ ] Add codegen script for OpenAPI spec
- [ ] Add to packages/contracts

### SDK
- [ ] Create app client wrapper
- [ ] Add typed query helpers
- [ ] Write usage documentation

---

## Phase 5: Observability

### Ops Schema
- [x] Create ops.runs table
- [x] Create ops.run_events table
- [x] Create ops.artifacts table
- [x] Add helper RPCs (start_run, log_event, etc.)

### Monitoring
- [ ] Create sync health dashboard
- [ ] Add alert rules
- [ ] Document runbooks

---

## Phase 6: Testing

### Infrastructure
- [ ] Add test database setup script
- [ ] Create mock Odoo server
- [ ] Add integration test harness

### Test Cases
- [ ] Test RLS policies
- [ ] Test sync correctness
- [ ] Test API contracts

---

## Quick Reference

| Category | Complete | Total | Progress |
|----------|----------|-------|----------|
| Spec Infrastructure | 5 | 5 | 100% |
| Auth Specs | 1 | 3 | 33% |
| Schema Specs | 1 | 3 | 33% |
| CI Gates | 1 | 3 | 33% |
| Core Schemas | 2 | 4 | 50% |
| RLS Policies | 1 | 3 | 33% |
| Odoo Bridge | 2 | 4 | 50% |
| Edge Functions | 0 | 3 | 0% |
| Sync Logic | 0 | 3 | 0% |
| Event System | 0 | 3 | 0% |
| Type Generation | 0 | 3 | 0% |
| SDK | 0 | 3 | 0% |
| Ops Schema | 4 | 4 | 100% |
| Monitoring | 0 | 3 | 0% |
| Testing | 0 | 6 | 0% |

**Overall Progress: 17/56 (30%)**
