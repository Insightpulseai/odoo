# Tasks — Marketing Agency Stack

> **Status:** Draft
> **Date:** 2026-03-25

---

## WS1: OCA Agency Baseline

- [ ] 1.1 Verify `crm` core module on Odoo 19.0 — lead/opportunity CRUD
- [ ] 1.2 Verify `project` core module — task/stage lifecycle
- [ ] 1.3 Verify `hr_timesheet` core module — entry/approval flow
- [ ] 1.4 Verify `mass_mailing` core module — list/campaign/send
- [ ] 1.5 Check OCA `contract` 19.0 branch exists, CI green, test install
- [ ] 1.6 Check OCA `hr_timesheet_sheet` 19.0 branch, test install
- [ ] 1.7 Check OCA `project_template` 19.0 branch, test install
- [ ] 1.8 Evaluate OCA CRM extensions (`crm_lead_scoring`, `crm_deduplicate`) for 19.0
- [ ] 1.9 Document results in `docs/evidence/<stamp>/agency-baseline/`

---

## WS2: Foundry Agent Overlay

- [ ] 2.1 Define `generate_creative_brief` tool contract (input: campaign_id + brand_id; output: brief draft)
- [ ] 2.2 Define `summarize_campaign_performance` tool contract (input: campaign_id; output: metrics summary)
- [ ] 2.3 Define `alert_utilization_threshold` tool contract (input: team/period; output: flagged employees)
- [ ] 2.4 Register tools in `ssot/contracts/tool_contracts.yaml`
- [ ] 2.5 Implement Odoo-side API endpoints for each tool (FastAPI or JSON-RPC)
- [ ] 2.6 Wire Foundry Agent Service tool definitions
- [ ] 2.7 Integration test: Foundry → tool → Odoo draft record creation

---

## WS3: Entra + M365 Channel Readiness

- [ ] 3.1 Confirm Entra Phase 0 complete (dependency — tracked in `spec/entra-identity-migration/`)
- [ ] 3.2 Identify 2-3 Copilot Studio candidate use cases (HR policy, IT helpdesk, onboarding)
- [ ] 3.3 Build Copilot Studio proof-of-concept for top candidate
- [ ] 3.4 Evaluate M365 Agents SDK for wrapping Pulser as custom engine agent
- [ ] 3.5 Create Teams app manifest for Ask Pulser
- [ ] 3.6 Test Teams → Foundry → Odoo round-trip
- [ ] 3.7 Document M365 Copilot licensing requirements

---

## WS4: Reporting / Profitability Gap Closure

- [ ] 4.1 Validate `marketing_pipeline.sql` DLT pipeline end-to-end on Databricks
- [ ] 4.2 Add Gold layer views: project WIP, team utilization, retainer burn-rate
- [ ] 4.3 Create Databricks SQL Warehouse endpoint for Power BI
- [ ] 4.4 Build Power BI profitability dashboard (project margin, utilization, retainer coverage)
- [ ] 4.5 Test refresh cycle and data freshness

---

## WS5: Agency Pack Port (18.0 → 19.0)

- [ ] 5.1 Dry-run: `oca-port origin/18.0 origin/19.0 ipai_marketing_agency_pack --verbose --dry-run`
- [ ] 5.2 Apply port
- [ ] 5.3 Run `odoo-bin upgrade_code` — tree→list, field renames
- [ ] 5.4 Fix Odoo 19 breaking changes (`groups_id` → `group_ids`, `Command` tuples, translation patterns)
- [ ] 5.5 Test install: `odoo-bin -d test_ipai_marketing_agency_pack -i ipai_marketing_agency_pack --stop-after-init --test-enable`
- [ ] 5.6 Classify results per testing policy
- [ ] 5.7 Register in `config/addons.manifest.yaml` with tier and provenance
- [ ] 5.8 Save evidence to `docs/evidence/<stamp>/agency-pack-port/`

---

## AI Integration Contract Definition (cross-cutting)

- [ ] X.1 Add marketing agency tools to `ssot/contracts/tool_contracts.yaml`
- [ ] X.2 Define Odoo → Foundry data contract for campaign/brand/brief entities
- [ ] X.3 Define Foundry → Odoo write contract (draft-only, no auto-confirm)
- [ ] X.4 Update `docs/architecture/marketing-agency-stack.md` with implementation evidence

---

## Identity / Channel Dependency Closure (cross-cutting)

- [ ] Y.1 Verify Entra app registration supports agency tool OAuth scopes
- [ ] Y.2 Test M365 Agents SDK with Foundry-hosted agent
- [ ] Y.3 Confirm Copilot Studio credit model for planned use cases
- [ ] Y.4 Update gap analysis with resolved items

---

**Total: 35 tasks across 5 workstreams + 2 cross-cutting groups.**

*Created 2026-03-25.*
