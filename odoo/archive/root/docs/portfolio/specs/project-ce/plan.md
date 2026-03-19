# Plan — Implementation

## Phase 0 — Scaffold

- [x] Create `ipai_project_suite` module
- [x] Add config toggles (res.config.settings -> ir.config_parameter)
- [x] Add base security groups + ACL skeleton

## Phase 1 — Feature Models

- [x] Implement milestone model + links to project/task
- [x] Implement dependency model + links to task
- [x] Implement budget + budget lines
- [x] Implement RACI model + assignment links
- [x] Implement stage gate model + approval mechanics
- [x] Implement template model + apply-to-project action

## Phase 2 — Views + UX

- [x] Inherit project/task forms with toggle-gated tabs
- [x] Add list/tree views for new models
- [x] Add menus/actions for feature management
- [x] Add smart buttons for milestones and budgets

## Phase 3 — Import System

- [x] Create CSV generator from Excel workbook
- [x] Create JSON-RPC importer script
- [x] Create import templates
- [x] Create CI workflow for artifact generation

## Phase 4 — Reporting (Future)

- [ ] Add SQL views for task aging
- [ ] Add SQL views for overdue by assignee
- [ ] Add SQL views for project progress rollups
- [ ] Add SQL views for milestone status
- [ ] Add SQL views for budget vs actual
- [ ] Add indexes for join paths

## Phase 5 — Verification + CI

- [ ] Add deterministic install/upgrade check
- [ ] Add smoke test script
- [ ] Add GitHub Action for install/upgrade gate

## Architecture Decisions

### REST vs GraphQL

For this implementation, we chose **REST (JSON-RPC)** over GraphQL for the following reasons:

1. **Odoo Native**: Odoo's web API is JSON-RPC based, providing natural integration
2. **Simple Operations**: Import/export are CRUD operations that map well to REST
3. **Caching**: REST endpoints benefit from HTTP caching for read operations
4. **Tooling**: Existing Odoo tools and SDKs work with JSON-RPC
5. **Auth**: Session-based auth works seamlessly with Odoo's security model

### When to Consider GraphQL

If future requirements include:
- Complex nested queries across multiple models
- UI composition requiring flexible data fetching
- Aggregation across Odoo + external services (Supabase, etc.)

Then a GraphQL BFF layer could be added on top of the JSON-RPC backend.
