# Tasks: ipai_odoo_copilot

> **Status**: Draft
> **Plan**: [plan.md](plan.md)
> **PRD**: [prd.md](prd.md)
> **Constitution**: [constitution.md](constitution.md)

---

## Phase 0: Spec and Boundaries

- [ ] P0-1: Finalize constitution.md — confirm governing principles with stakeholders
- [ ] P0-2: Finalize prd.md — confirm finance-first scope, acceptance criteria, and success metrics
- [ ] P0-3: Finalize plan.md — confirm architecture split (Odoo / Foundry / Databricks / Entra / DevOps)
- [ ] P0-4: Document Foundry request/response contract as a versioned JSON schema in `agents/contracts/`
- [ ] P0-5: Confirm Entra identity flow — validate managed identity token acquisition on Azure Container Apps and API key fallback for non-Azure environments

---

## Phase 1: Module Scaffold

- [ ] P1-1: Create `addons/ipai/ipai_odoo_copilot/__manifest__.py` with version `19.0.1.0.0`, license `LGPL-3`, minimal dependencies (`base`, `mail`, `account`)
- [ ] P1-2: Create security groups — `group_copilot_user` (base internal user), `group_copilot_admin` (settings + audit access) — in `security/copilot_groups.xml`
- [ ] P1-3: Create `ir.model.access.csv` with ACLs for `ipai.copilot.audit`, `ipai.copilot.telemetry` models (read for user, full CRUD for admin)
- [ ] P1-4: Create `models/copilot_audit.py` — `ipai.copilot.audit` model with all fields from FR-6 (user_id, session_id, request/response timestamps, question, response, active_model, active_id, action_taken, action_result, provider, latency_ms, company_id)
- [ ] P1-5: Create `models/foundry_service.py` — `ipai.copilot.provider.foundry` implementing the provider abstract model with `send_request()` and `validate_config()` methods, using `requests` library with configurable timeout
- [ ] P1-6: Create `models/res_config_settings.py` — extend `res.config.settings` with copilot fields (enabled, endpoint URL, auth mode, API key, timeout, allowed actions, telemetry enabled, max context records)
- [ ] P1-7: Verify clean install: `odoo-bin -d test_ipai_odoo_copilot -i ipai_odoo_copilot --stop-after-init` passes with 0 errors

---

## Phase 2: Finance-First Bridge Flows

- [ ] P2-1: Implement finance Q&A context packager — read `account.move`, `account.move.line`, `account.bank.statement.line`, `res.partner` based on active record; serialize to JSON payload respecting user ACLs; delegate to Foundry provider
- [ ] P2-2: Implement reconciliation assistance flow — given a bank statement line, package context (statement line + candidate journal items), send to Foundry, render suggested matches with confidence indicators, mediate user-confirmed reconciliation via Odoo's native reconciliation API
- [ ] P2-3: Implement collections assistance flow — given a partner or overdue invoice, package aging and communication history context, send to Foundry, render draft follow-up email in Odoo mail composer for user review and send
- [ ] P2-4: Implement variance-analysis assistance flow — package P&L, budget, analytic account, and cost center context for a given period; send to Foundry; render variance breakdown as structured text/table with journal entry citations
- [ ] P2-5: Implement escalation rendering — parse `escalation` metadata from Foundry response; render callout in chat panel with reason, suggested assignee, and priority; no automatic task creation in Release 1
- [ ] P2-6: Implement audit logging for all flows — every request/response (including errors and timeouts) creates an `ipai.copilot.audit` record; verify 100% audit coverage with integration tests

---

## Phase 3: Policy and Action Mediation

- [ ] P3-1: Implement action allowlist checking — `models/tool_executor.py` reads the `allowed_actions` JSON from `ir.config_parameter`, validates incoming action IDs against the list, rejects unlisted actions with a user-visible message
- [ ] P3-2: Implement user confirmation dialog — when an allowed action is returned by Foundry, display a confirmation dialog in the UI showing exactly what will change (model, record, fields, values) before execution
- [ ] P3-3: Implement action execution via ORM — on user confirmation, execute the action using standard Odoo ORM methods (not raw SQL); log the action and result in the audit trail
- [ ] P3-4: Implement read-only default enforcement — verify that with an empty allowlist, no ORM write operations are triggered by any copilot flow; add a dedicated security test
- [ ] P3-5: Implement admin audit log views — `views/copilot_audit_views.xml` with list and form views accessible to `group_copilot_admin`; regular users see only their own records via record rule

---

## Phase 4: Testing and CI

- [ ] P4-1: Write `tests/test_copilot_audit.py` — test audit record creation, field validation, read-only enforcement (no write after create), retention cron deletes records older than configured days
- [ ] P4-2: Write `tests/test_foundry_service.py` — test HTTP request construction (correct URL, headers, payload), response parsing (valid JSON, malformed JSON, empty), error handling (timeout, 4xx, 5xx), all using `unittest.mock.patch` for `requests.post`
- [ ] P4-3: Write `tests/test_res_config_settings.py` — test settings read/write round-trip, default values, validation (e.g., timeout > 0, endpoint URL starts with https://)
- [ ] P4-4: Write `tests/test_tool_executor.py` — test allowlist checking (allowed, denied, empty list), action execution (success, failure), audit record creation for actions
- [ ] P4-5: Add coexistence install test — CI job installs `ipai_odoo_copilot` alongside `account_reconcile_oca`, `mis_builder`, `ipai_finance_ppm` on a clean DB; verify 0 errors
- [ ] P4-6: Add linting and coverage CI step — `flake8`, `black --check`, `isort --check`, `coverage report --fail-under=80` for the module directory; gate PR merges on pass

---

## Phase 5: Rollout

- [ ] P5-1: Deploy module to dev environment (`odoo_dev` database) — install and configure Foundry endpoint to dev project
- [ ] P5-2: Validate all 4 finance scenarios (month-end Q&A, reconciliation, collections, variance) against demo data — capture evidence in `docs/evidence/`
- [ ] P5-3: Deploy module to staging — configure Foundry endpoint to staging project; run automated integration test suite
- [ ] P5-4: Finance team UAT — 3+ finance operators test the 4 scenarios with production-like data; collect feedback; iterate on UX
- [ ] P5-5: Deploy to production — enable for `group_copilot_user` members only; monitor audit logs and telemetry for 7 days
- [ ] P5-6: Post-launch review — evaluate success criteria (latency < 5s p95, audit coverage 100%, adoption >= 3 weekly users within 30 days); document findings; decide Release 2 timeline

---

## Deferred (Release 2+)

- **D-1**: Streaming response rendering (SSE or WebSocket) for long-running Foundry responses
- **D-2**: Project/PPM copilot context packaging (extends beyond finance to project management domain)
- **D-3**: Helpdesk copilot context packaging (ticket summaries, SLA status, resolution suggestions)
- **D-4**: Automatic task/activity creation from escalation metadata (FR-14 extension)
- **D-5**: Additional provider implementations (non-Foundry runtimes, local model servers for air-gapped environments)

---

*Last updated: 2026-03-22*
