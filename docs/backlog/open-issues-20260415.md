# Open Issues — Pulser / Foundry / Odoo Backlog

> Ready-to-file GitHub Issues for items surfaced during 2026-04-14 / 2026-04-15 session.
> Per CLAUDE.md: GitHub Issues = engineering execution backlog; ADO Boards = portfolio/planning.
> File via `gh issue create -F docs/backlog/open-issues-20260415.md --title "..."` or manually.
> Created 2026-04-15.

---

## P0 — BLOCKERS (must resolve before any external user)

### Issue 1 — Security: BOLA in copilot_gateway.py (missing thread ownership check)
**Labels:** `security`, `blocker`, `p0`
**Area:** `apps/bot-proxy/` or `agent-platform/`

**Problem:** `copilot_gateway.py` accepts `thread_id` parameter without verifying that the authenticated user owns the thread. Classic BOLA (Broken Object-Level Authorization). Any user can read/mutate another user's threads.

**Acceptance criteria:**
- [ ] `thread_id` ownership validated against authenticated Entra user's `oid` claim before any read/write
- [ ] Unit test proves cross-user access returns 403
- [ ] Fuzz test with 100 random UUIDs all return 403 for non-owner
- [ ] Audit log emits `thread_access_denied` event on violation

**Dependencies:** none — pure code fix.

---

### Issue 2 — Security: PgBouncer OFF on pg-ipai-odoo
**Labels:** `security`, `performance`, `blocker`, `p0`
**Area:** infra

**Problem:** `pg-ipai-odoo` (PAYG `rg-ipai-dev-odoo-data`) has PgBouncer disabled. Connection pool exhaustion risk under agent load; also misses transaction-pooling mode benefits.

**Acceptance criteria:**
- [ ] `az postgres flexible-server parameter set -g rg-ipai-dev-odoo-data --server-name pg-ipai-odoo --name pgbouncer.enabled --value on`
- [ ] Restart server (required for parameter to take effect)
- [ ] Test connection via PgBouncer port (6432); verify transaction mode works for Odoo
- [ ] Update `odoo.conf` connection string in ACA if needed

**Dependencies:** none.

---

### Issue 3 — Security: Foundry local-auth (API keys) still enabled
**Labels:** `security`, `blocker`, `p0`
**Area:** infra

**Problem:** `ipai-copilot-resource` allows both API-key auth and Entra ID auth. Per `CLAUDE.md` §Secrets Policy, keyless (Entra/MI) is the canonical path; keys are attack surface.

**Acceptance criteria:**
- [ ] `az cognitiveservices account update -n ipai-copilot-resource -g rg-data-intel-ph --custom-domain ipai-copilot-resource --api-properties disableLocalAuth=true`
- [ ] Verify all existing agents authenticate via MI after cutover (no regression)
- [ ] Rotate any existing keys to invalidate leaked ones
- [ ] Update SSOT `runtime-contract.yaml §4.auth` to mark API-key path as `removed`, not `fallback`

**Dependencies:** Verify all workloads are MI-auth'd first (Issue 4).

---

### Issue 4 — Verify Foundry system-assigned MI state
**Labels:** `security`, `verification`, `p0`
**Area:** infra

**Problem:** A draft document claimed Foundry system MI was OFF; the portal Identity page previously showed principal ID `3293f6ba-d5b6-4928-a62c-684e4d777f11`. Need authoritative state verification and role assignments audit.

**Acceptance criteria:**
- [ ] `az cognitiveservices account show -n ipai-copilot-resource -g rg-data-intel-ph --query identity` returns `SystemAssigned` with principalId
- [ ] All role assignments using that principal ID listed and reviewed for least-privilege
- [ ] If OFF, enable and re-assign required roles to agent workloads
- [ ] Document in `ssot/foundry/runtime-contract.yaml §auth.current_principals`

**Dependencies:** none.

---

### Issue 5 — Defender for AI not enabled on Foundry
**Labels:** `security`, `p0`
**Area:** infra

**Problem:** Microsoft Defender for AI workload (prompt injection, jailbreak, data exfiltration detection) is not enabled on `ipai-copilot-resource`. Prod-blocker for any external user.

**Acceptance criteria:**
- [ ] Defender for AI plan enabled via `az security pricing create --name AI --tier Standard`
- [ ] Prompt injection + jailbreak detection rules active
- [ ] Alerts route to Security Center + `appi-ipai-dev-agent-sea`
- [ ] Cost impact estimated and approved

**Dependencies:** Subscription-level action; requires Owner on subscription.

---

## P0 — MUST LAND (this week, non-blocking)

### Issue 6 — Foundry connections not yet wired (App Insights / AI Search / Storage)
**Labels:** `foundry`, `p0`, `portal-action`
**Area:** `ssot/foundry/`, Foundry portal

**Problem:** `docs/runbooks/foundry-connections-and-tools.md §2` locks the connection order (App Insights → AI Search → Storage) but none are wired yet. ARM REST PUT returns 404 "workspace not found"; portal is the only working path.

**Acceptance criteria:**
- [ ] Portal action: Foundry project Overview → Connected resources → Add connection
- [ ] 1/3: `appi-ipai-dev-agent-sea` (ApiKey auth — required by Foundry policy for App Insights)
- [ ] 2/3: `srch-ipai-dev-sea` (Entra ID)
- [ ] 3/3: `stipaidevagent` (Entra ID, container scope)
- [ ] Verify via projects API: `GET /api/projects/ipai-copilot/connections?api-version=2025-05-01`
- [ ] Commit connection names back to `ssot/foundry/runtime-contract.yaml` (new §11 connections block)

**Dependencies:** none.

---

### Issue 7 — Fix `d365-displacement-map.md` drift before commit
**Labels:** `docs`, `drift`, `p0`
**Area:** `docs/architecture/`

**Problem:** Draft `docs/architecture/d365-displacement-map.md` has 4+ drift items vs live state:
1. 6 Teams bots claimed 🟢 LIVE — NONE exist
2. `cosmos-ipai-dev` referenced as live backing store — NOT provisioned
3. `stipaiagentdev` (typo) — actual is `stipaidevagent`
4. `fcipaidev` Fabric — not ARM-registered

**Acceptance criteria:**
- [ ] Teams bots → change status to ⚡ NOT YET PROVISIONED
- [ ] `cosmos-ipai-dev` → remove from §0 live list, add as PLANNED with trigger condition
- [ ] `stipaiagentdev` → rename all refs to `stipaidevagent`
- [ ] `fcipaidev` → annotate as "Fabric trial workspace, portal-accessed, not ARM-registered"
- [ ] Add §0.1 cross-sub split paragraph (PAYG for agent runtime; Sponsorship for data-plane services)
- [ ] Remove any lingering Claude-on-Foundry / ipai-copilot-payg references (both retired)

**Dependencies:** none.

---

### Issue 8 — Module naming consolidation (`ipai_expense_*` + `ipai_*_recon`)
**Labels:** `odoo`, `tech-debt`, `p0`
**Area:** `addons/ipai/`, `odoo/addons/ipai/`

**Problem:** Multiple modules named for the same capability:
- `ipai_hr_expense_liquidation` (in `odoo/addons/ipai/`)
- `ipai_expense_ops` (in `addons/ipai/`)
- `ipai_expense_wiring` (in `addons/ipai/`)
- Displacement-map references `ipai_expense_liquidation` (does not exist as named)
- Similarly: `ipai_bank_recon` (exists) vs `ipai_finance_recon` (referenced, does not exist)

**Acceptance criteria:**
- [ ] Pick canonical names per `.claude/rules/oca-governance.md` (single module per capability)
- [ ] Archive duplicates via git rename to canonical; preserve git history
- [ ] Update `ssot/odoo/integration_adoption.yaml` with canonical names
- [ ] Update `docs/research/d365-to-odoo-mapping.md` §4 gap list to use canonical names
- [ ] Verify no `_template` or placeholder files left behind

**Dependencies:** Requires product decision on which name wins per capability.

---

## P1 — SHIP IN CURRENT SPRINT

### Issue 9 — Finalize `ipai_bir_tax_compliance` Phase 1 (DAT + PDF)
**Labels:** `odoo`, `bir`, `ph`, `p1`, `tax-guru-agent`
**Area:** `addons/ipai/ipai_bir_tax_compliance/`

**Problem:** Module exists but needs implementation. Phase 1 scope (not eBIRForms yet): DAT file generation + BIR PDF rendering via Foundry Code Interpreter.

**Acceptance criteria:**
- [ ] Tool: `generate_bir_dat(form_type, period, company_tin)` — uses Foundry Code Interpreter (not custom ACA)
- [ ] Tool: `render_bir_pdf(form_type, period)` — WeasyPrint/reportlab in Code Interpreter
- [ ] Forms covered Phase 1: 2307, SAWT, QAP, SLSP
- [ ] DAT output passes BIR validator (test fixture in `tests/bir/fixtures/`)
- [ ] PDF output has all required fields per BIR form spec
- [ ] Artifacts stored in `stipaidevagent` via Storage connection
- [ ] State machine in Postgres `ops` schema (NOT Supabase)
- [ ] Tied to Tax Guru agent (`id-ipai-agent-tax-guru-dev`)
- [ ] Eval pass per `spec/pulser-evals/pulser-finance-evals.md §2.1`

**Dependencies:** Issue 6 (connections wired), Issue 8 (naming consolidated).

---

### Issue 10 — Provision AI Search indexes (4 indexes)
**Labels:** `ai-search`, `rag`, `p1`
**Area:** `srch-ipai-dev-sea`

**Problem:** `docs/runbooks/foundry-connections-and-tools.md §2.1` lists 4 required indexes. None provisioned yet.

**Acceptance criteria:**
- [ ] Index: `pulser-odoo-docs` — Odoo 18 CE + OCA module documentation; initial corpus load
- [ ] Index: `pulser-bir-rulings` — BIR Revenue Regulations, RMCs, ATCs; initial corpus load
- [ ] Index: `pulser-prismalab` — PrismaLab SR/MA corpus; initial load
- [ ] Index: `pulser-runbooks` — `automations/runbooks/` from monorepo; initial load
- [ ] Semantic ranker enabled on all 4
- [ ] Refresh schedule documented (cron or manual)
- [ ] `spec/pulser-evals/pulser-research-evals.md` passes against provisioned indexes

**Dependencies:** Issue 6 (AI Search connection wired), corpus assembly.

---

### Issue 11 — Wire Service Bus triggers: Odoo → Bank Recon agent
**Labels:** `integration`, `service-bus`, `p1`, `bank-recon-agent`
**Area:** `apps/odoo-connector/`, `sb-ipai-dev-sea`

**Problem:** Bank Recon agent runs on-demand only. MS benchmark (Balance Sheet Recon Agent) has continuous monitoring via Power Automate. IPAI needs `ipai-odoo-connector` (PAYG) to publish `account.move.posted` events → Service Bus (Sponsorship) → Bank Recon agent.

**Acceptance criteria:**
- [ ] Odoo post-hook publishes event to `sb-ipai-dev-sea` topic `odoo.account.move.posted`
- [ ] Cross-sub MI role assignment: `id-ipai-agent-bank-recon-dev` (PAYG MI) → `Azure Service Bus Data Receiver` on `sb-ipai-dev-sea` (Sponsorship)
- [ ] Bank Recon agent subscribes to the topic with a subscription filter for bank journal moves only
- [ ] End-to-end trace: post → event → agent run → trace in `appi-ipai-dev-agent-sea`
- [ ] Rate-limited to prevent runaway on bulk-post

**Dependencies:** Issue 6 (App Insights connection), Issue 4 (MI state verified).

---

### Issue 12 — Scaffold `ipai_ar_collections` module
**Labels:** `odoo`, `p1`, `pulser-agent`
**Area:** `addons/ipai/`

**Problem:** Pulser agent has AR collections skill wired in `spec/pulser-evals/pulser-finance-evals.md §2.3` but no backing Odoo module exists. OCA `account_credit_control` is the base; `ipai_ar_collections` adds PH tone + Pulser agent integration.

**Acceptance criteria:**
- [ ] Depends on OCA `account_credit_control` + `partner_statement`
- [ ] Fields: `ipai_last_agent_draft_id`, `ipai_agent_draft_status` on `res.partner`
- [ ] Action: `action_draft_collection_email` invokes Pulser agent via `ipai-odoo-mcp` → agent reads AR aging, drafts email, returns as `mail.activity`
- [ ] Tiered templates (30d / 60d / 90d+) in `data/mail_template.xml`
- [ ] Includes `docs/MODULE_INTROSPECTION.md` + `docs/TECHNICAL_GUIDE.md` per CLAUDE.md doctrine
- [ ] Passes `spec/pulser-evals/pulser-finance-evals.md §2.3`

**Dependencies:** Issue 6, Issue 10 (AI Search ready for grounding).

---

### Issue 13 — Entra Agent ID registration for 3 published agents (deadline 2026-05-01)
**Labels:** `entra`, `agent-365`, `p1`, `deadline`
**Area:** `spec/pulser-agent-365-registration/`

**Problem:** M365 E7 / Agent 365 GA 2026-05-01. Every published Pulser agent needs a distinct Entra service principal with AgentId extension. Missing = not in the Agent 365 catalog.

**Acceptance criteria:**
- [ ] Spec dir created: `spec/pulser-agent-365-registration/`
- [ ] Manifest per agent: `manifest-pulser-finance.json`, `manifest-pulser-ops.json`, `manifest-pulser-research.json`
- [ ] Each SP created in IPAI tenant + TBWA tenant via `az ad sp create`
- [ ] AgentId extension applied via Graph API
- [ ] Appears in Entra admin → Agent catalog on both tenants
- [ ] Resource permissions on `ipai-copilot-resource` + `pg-ipai-odoo` reassigned to new SPs
- [ ] Documented in `docs/runbooks/entra-agent-id-registration.md`

**Dependencies:** Issue 6, Issue 4.

---

## P2 — NEXT SPRINT

### Issue 14 — Fine-tune Phase 1 execution (run evals against gpt-4.1 baseline)
**Labels:** `fine-tune`, `p2`
**Area:** `spec/pulser-evals/`

**Problem:** Eval cases scaffolded today. Need to run them and establish baseline scores before iterating prompts.

**Acceptance criteria:**
- [ ] Baseline run per agent: pulser-finance, pulser-ops, pulser-research
- [ ] Results in `docs/evidence/eval-runs/20260415-<hhmm>/<agent>-baseline.json`
- [ ] Summary table in `docs/evidence/eval-runs/20260415-<hhmm>/README.md`
- [ ] Any blocking-test failure → create follow-up issue
- [ ] Per-test score tracked; deltas logged on every re-run

**Dependencies:** Issue 6 (agents can run against connected data), Issue 10 (AI Search has corpus).

---

### Issue 15 — `ipai_bsp_fx_rate` — BSP currency rate connector
**Labels:** `odoo`, `p2`, `ph`
**Area:** `addons/ipai/ipai_bsp_fx_rate/`

**Problem:** BSP (Bangko Sentral ng Pilipinas) publishes daily reference FX rates. Odoo CE + OCA `currency_rate_update` doesn't have a BSP connector. Manual FX revaluation is error-prone.

**Acceptance criteria:**
- [ ] Module depends on OCA `currency_rate_update`
- [ ] Service class `BSPRateProvider` extends OCA rate-update framework
- [ ] Endpoint: BSP reference rate feed (verify published API spec)
- [ ] Daily cron at BSP publish time (typically 4 PM Manila)
- [ ] Fallback to previous day on feed failure; alert via `appi-ipai-dev-agent-sea`
- [ ] Platform contract: `platform/contracts/fx-rate-sync.yaml`

**Dependencies:** none.

---

### Issue 16 — eBIRForms / eFPS submission via Foundry Browser Automation (Phase 2)
**Labels:** `bir`, `ph`, `p2`, `tax-guru-agent`
**Area:** `addons/ipai/ipai_bir_tax_compliance/`, Foundry Browser Automation tool

**Problem:** Phase 1 generates DAT + PDF. Phase 2 submits to eBIRForms/eFPS portals. Foundry's built-in Browser Automation replaces the originally-planned Playwright sidecar.

**Acceptance criteria:**
- [ ] Browser Automation playbook: login → select form → upload DAT → submit → capture receipt
- [ ] Credentials in `kv-ipai-dev-sea`; never in script
- [ ] Human-approval gate before submit (approval recorded in Postgres `ops` schema)
- [ ] Submission receipt stored in `stipaidevagent` + referenced on `account.move`
- [ ] Retry logic for portal flakiness (exponential backoff, max 3)
- [ ] Eval test with BIR sandbox endpoint (or mock)

**Dependencies:** Issue 9 (DAT gen working), Issue 6.

---

### Issue 17 — `ipai_procurement_comms` — Supplier Comms Pulser skill
**Labels:** `odoo`, `p2`, `ap-invoice-agent`
**Area:** `addons/ipai/ipai_procurement_comms/`

**Problem:** Parity with D365 Supplier Comms Agent. AP Invoice agent (`id-ipai-agent-ap-invoice-dev`) can draft PO status inquiries, invoice chasers, dispute replies. Requires Odoo module for template + audit trail.

**Acceptance criteria:**
- [ ] Module depends on `purchase` + `mail`
- [ ] Fields on `purchase.order`: `ipai_last_comm_date`, `ipai_pending_inquiries`
- [ ] Action `action_draft_supplier_comm` invokes AP Invoice agent via `ipai-odoo-mcp`
- [ ] Tiered templates per comm type: status / dispute / reminder / escalation
- [ ] MODULE_INTROSPECTION + TECHNICAL_GUIDE docs

**Dependencies:** Issue 6, Issue 11 (Service Bus wiring for triggers).

---

### Issue 18 — `ipai_finance_ppm` KPI definitions in mis_builder
**Labels:** `odoo`, `p2`, `finance-close-agent`, `reporting`
**Area:** `addons/ipai/ipai_finance_ppm/`

**Problem:** 9 KPIs identified in D365 parity analysis (DSO, DPO, Days to close, Filing on-time, etc.) need `mis_builder` definitions to feed Power BI / Fabric.

**Acceptance criteria:**
- [ ] mis.report templates for: DSO, DPO, Cost per analysis request, Outsourcing spend, Risk mgmt, First-pass-yield AP, Days to close, Filing on-time rate
- [ ] Each template tied to a specific agent's accountability (see `agents/skills/_kpi-contracts/SKILL.md`)
- [ ] Data feed to Fabric workspace (once Fabric mirror provisioned)
- [ ] Power BI workspace auto-refresh daily

**Dependencies:** Issue 6, fabric mirror decision.

---

### Issue 19 — Shared KPI accountability contract skill
**Labels:** `agent-design`, `p2`
**Area:** `agents/skills/_kpi-contracts/`

**Problem:** Every specialist agent should inherit the same KPI reporting contract — declare which KPIs it owns + which data sources it reads for them. Prevents KPI ownership ambiguity.

**Acceptance criteria:**
- [ ] `agents/skills/_kpi-contracts/SKILL.md` defines the contract shape
- [ ] Each specialist agent's SKILL.md imports/references this contract
- [ ] Enumerates owner → KPI → data source mapping from `docs/research/d365-to-odoo-mapping.md` §5
- [ ] Used by `ipai_finance_ppm` as the single source for KPI definitions

**Dependencies:** Issue 18.

---

## P3 — TRIGGER-BASED (land when condition met)

### Issue 20 — Claude-on-Foundry revisit gate
**Labels:** `trigger`, `p3`
**Area:** policy

**Problem:** Currently blocked by Enterprise/MCA-E quota gate. Revisit when Microsoft opens Claude quotas beyond Enterprise tier OR user explicitly reopens the question.

**Trigger:** One of:
- MS removes Enterprise-tier quota gate on Claude models
- IPAI converts a subscription to MCA-E
- User explicitly asks

**Acceptance criteria (on trigger):**
- [ ] Re-verify `project_foundry_anthropic_sponsorship_blocker` memory against current MS policy
- [ ] Decision: adopt or stay?
- [ ] If adopt: re-provision PAYG Foundry (deleted 2026-04-15) or use Sponsorship with credit card
- [ ] Update `ssot/foundry/runtime-contract.yaml activation.claude_code_foundry_mode.state`

**Dependencies:** trigger.

---

### Issue 21 — Fine-tune Phase 3 (Supervised FT) trigger
**Labels:** `trigger`, `fine-tune`, `p3`
**Area:** `ssot/foundry/runtime-contract.yaml §fine_tuning_roadmap`

**Problem:** Phase 3 triggers when prompt iteration plateaus below eval targets. Corpus assembly runs in parallel with Phase 2.

**Trigger:** Any of (per `spec/pulser-evals/pulser-finance-evals.md §5`):
- BIR DAT compliance <100% after 10 prompt iterations
- Reconciliation precision stuck <95%
- AR email tone reviewer score stuck <4.0/5
- Expense PH-compliance fields recur in 3+ cases

**Pre-work (do now, ungated):**
- [ ] Assemble corpus: 500+ BIR 2307 historical, 1000+ reconciliation pairs, 200+ anonymized collection emails, 300+ expense liquidation forms
- [ ] Corpus in ADLS `stlkipaidev` with clean train/dev/test splits
- [ ] Corpus review for PII / secret leakage

**Acceptance criteria (on trigger):**
- [ ] Submit Azure OpenAI FT job on `gpt-4.1` with assembled corpus
- [ ] New pinned deployment `gpt-4.1-pulser-ft-<yyyymmdd>`
- [ ] Re-run evals; confirm improvement > baseline
- [ ] Roll specialist agents to new deployment via SKILL.md updates

**Dependencies:** Issue 14 (baseline evals), corpus assembly.

---

### Issue 22 — Cosmos DB provisioning trigger
**Labels:** `trigger`, `p3`
**Area:** `ssot/foundry/`

**Problem:** Cosmos is DEFERRED. Provision only when Postgres `ops` schema on `pg-ipai-odoo` is insufficient for a specific agent.

**Trigger:** Any of:
- A specific agent requires multi-region durable state
- Postgres `ops` schema query latency exceeds 200ms p95 under agent load
- Agent-session history exceeds comfortable Postgres row count (>10M rows)

**Acceptance criteria (on trigger):**
- [ ] Provision `cosmos-ipai-dev-agent-eus2` (co-located with Foundry)
- [ ] Migrate specific workload with data migration script
- [ ] Update `ssot/foundry/runtime-contract.yaml` backing_stores

**Dependencies:** trigger.

---

### Issue 23 — Teams bot provisioning (if GTM requires Teams surface)
**Labels:** `teams`, `agent-surface`, `p3`
**Area:** `infra/azure/bot-service/`

**Problem:** Displacement-map draft claimed 6 Teams bots LIVE but none exist. If GTM says Pulser agents need Teams surface (to match D365 Copilot Time & Expense UX), provision them.

**Trigger:** Explicit GTM need for Teams surface (e.g., TBWA\SMP pilot requires Teams bot).

**Acceptance criteria (on trigger):**
- [ ] Bot Framework registration: `ipai-<agent>-teams-bot-dev` per agent
- [ ] Bicep module `infra/azure/bot-service/pulser-bot.bicep`
- [ ] Entra app registration with Teams channel enabled
- [ ] Azure Bot proxies to ACA app that routes to agent
- [ ] App manifest in `apps/bot-proxy/manifests/`

**Dependencies:** Pilot kickoff decision.

---

### Issue 24 — ipai_bir_1601c + 1702 (Phase 3 BIR forms)
**Labels:** `bir`, `ph`, `p3`, `tax-guru-agent`
**Area:** `addons/ipai/ipai_bir_tax_compliance/`

**Problem:** Phase 1 covers 2307/SAWT/QAP/SLSP. 1601-C (monthly EWT remit) and 1702 (annual ITR) are Phase 3 — larger scope, annual cadence for 1702.

**Acceptance criteria (on scope):**
- [ ] 1601-C DAT gen + PDF render + eBIRForms submission
- [ ] 1702-RT + 1702-EX variant handling
- [ ] Annual close workflow integration
- [ ] Multi-year reconciliation for 1702 (reads prior-year posted returns)

**Dependencies:** Issue 9 (Phase 1 solid), Issue 16 (Phase 2 eBIRForms).

---

### Issue 26 — CDM folder export pipeline (Databricks DLT → stipaidevlake/gold/)
**Labels:** `data-intelligence`, `cdm`, `p1`, `fabric`
**Area:** `data-intelligence/pipelines/`

**Problem:** Power BI / Fabric Data Agent / M365 Copilot Analyst can't natively consume Odoo data without CDM-formatted input. Implementing the projection unlocks the entire M365 analytics ecosystem.

**Acceptance criteria:**
- [ ] Pipeline: `data-intelligence/pipelines/odoo_cdm_export.py` (Databricks DLT)
- [ ] Reads Bronze Odoo-shaped tables; writes Gold CDM-formatted entities per `platform/contracts/cdm-entity-map.yaml`
- [ ] Generates `{Entity}.cdm.json` manifest per entity folder
- [ ] Generates top-level `manifest.cdm.json` listing all entities
- [ ] Parquet (Snappy) data format, date-partitioned
- [ ] Refresh: hourly for transactional entities, daily for master data
- [ ] Verify CDM manifest validates against Microsoft CDM spec
- [ ] `stipaidevlake/gold/` populated end-to-end for 3 core entities as proof: Invoice, Payment, BankStatementLine
- [ ] Documented in `docs/architecture/cdm-odoo-mapping.md`

**Dependencies:** Issue 6 (data available via AI Search / PG MCP), `dbw-ipai-dev` access.

---

### Issue 27 — Fabric capacity provisioning + `fcipaidev` workspace + Data Agent
**Labels:** `fabric`, `infrastructure`, `p1`, `deadline`
**Area:** `infra/fabric/`

**Problem:** Fabric workspace `fcipaidev` referenced as Fabric mirror target but not ARM-registered. Fabric trial expires ~2026-05-20 per memory. Fabric Data Agent is the integration unlock for M365 Copilot.

**Acceptance criteria:**
- [ ] Decide: extend trial OR commit to paid Fabric capacity (F2 minimum)
- [ ] Provision capacity via `az resource create` on `Microsoft.Fabric/capacities`
- [ ] Create workspace `fcipaidev` attached to capacity
- [ ] Shortcut to `stipaidevlake/gold/` (requires Issue 26 complete)
- [ ] Create Fabric Data Agent wrapping CDM entities from `platform/contracts/cdm-entity-map.yaml §fabric_data_agent.expose_entities`
- [ ] Surface MCP endpoint
- [ ] Register MCP endpoint in Pulser tool catalog

**Dependencies:** Issue 26.

---

### Issue 28 — Unity Catalog namespace + metrics schema bootstrap
**Labels:** `databricks`, `unity-catalog`, `p1`, `semantic-layer`
**Area:** `dbw-ipai-dev`, `data-intelligence/unity-catalog/`

**Problem:** Per `docs/architecture/semantic-layer.md`, Unity Catalog is the canonical semantic layer. Namespace + access control + first metric views must land for downstream consumers (Power BI, Fabric Data Agent, Pulser agents) to reference a single source of truth.

**Acceptance criteria:**
- [ ] Metastore assigned for SEA region (verify on `dbw-ipai-dev` or provision)
- [ ] Catalogs: `ipai_dev`, `ipai_staging`, `ipai_prod`
- [ ] Schemas per catalog: `bronze`, `silver`, `gold`, `metrics`, `features`
- [ ] Role assignments per §5.1:
  - `data_owner_ipai`, `data_engineer_ipai`, `metrics_owner_ipai`
  - `agent_reader_ipai` granted to each of 6 Pulser agent MIs
  - `bi_reader_ipai` granted to Power BI service principal (when provisioned)
  - `auditor_ipai` read-only
- [ ] First 3 metric views landed + validated against Odoo-direct SQL:
  - `ipai_dev.metrics.dso_daily`
  - `ipai_dev.metrics.dpo_daily`
  - `ipai_dev.metrics.filing_on_time_rate`
- [ ] Lineage visible in `system.access.table_lineage`
- [ ] `mis_builder` reads metrics via Databricks SQL Warehouse endpoint proven end-to-end
- [ ] DDL committed to `data-intelligence/unity-catalog/metrics/*.sql`

**Dependencies:** Issue 26 (CDM Gold exists).

---

### Issue 25 — BIR CAS certification (direct eFPS integration)
**Labels:** `bir`, `ph`, `certification`, `p3`, `strategic`
**Area:** regulatory

**Problem:** CAS (Computerized Accounting System) permit allows direct eFPS API integration, bypassing portal automation. Major moat once certified.

**Trigger:** After Phase 1-2 stable in production for 3+ months.

**Acceptance criteria (on trigger):**
- [ ] Submit CAS permit application (BIR RR 9-2009, updated requirements)
- [ ] System documentation per BIR CAS checklist
- [ ] PH-registered legal entity sponsors the application
- [ ] Pilot with 1-2 customers post-approval

**Dependencies:** Production track record, legal entity readiness.

---

## Summary

| Priority | Count | Estimated scope |
|---|---|---|
| P0 Blockers | 5 | Security + drift — days |
| P0 Must Land | 3 | Portal actions + docs — 1 week |
| P1 Current Sprint | 5 | Features — 2-3 weeks |
| P2 Next Sprint | 6 | Features + rollout — 4-6 weeks |
| P3 Trigger-based | 6 | Conditional |
| **Total** | **25** | — |

---

## How to file

```bash
# Batch-file all P0 and P1 via gh CLI
gh issue create --title "P0: Security BOLA in copilot_gateway.py" \
  --label "security,blocker,p0" \
  --body "$(sed -n '/^### Issue 1/,/^---/p' docs/backlog/open-issues-20260415.md)"
# ... repeat per issue, or script it
```

Or load into Azure DevOps Boards (portfolio) and map to existing Wave-01 epics from `project_azdo_boards_populated_20260414` memory.
