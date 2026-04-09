# Plan — Tax Pulse Sub-Agent (BIR Compliance Pack)

## Implementation Waves

### Wave 1: Knowledge Ingestion

**Goal**: Ground Advisory agent with BIR compliance knowledge.

**Files**:
- `addons/ipai/ipai_bir_tax_compliance/data/knowledge/` — BIR regulation summaries, form guides
- Knowledge store registration in Foundry project

**Verification**:
- Advisory answers "What is BIR Form 2550M?" with grounded citation
- Advisory refuses ungrounded tax advice

### Wave 2: Rates/Rules Port from TaxPulse Assets

**Goal**: Externalized tax computation substrate. **COMPLETE.**

**Files delivered**:
- `data/rates/ph_rates_2025.json` — TRAIN brackets, EWT, FWT, corporate, VAT
- `data/rules/vat.rules.yaml` — 8 VAT JSONLogic rules
- `data/rules/ewt.rules.yaml` — 11 EWT JSONLogic rules
- `engine/{evaluator,formula,loader}.py` — rules engine
- `tests/` — 67 passing tests + golden dataset fixtures

### Wave 3: Compute/Validate Tools

**Goal**: Copilot tools that trigger Odoo state machine transitions.

**Files**:
- `addons/ipai/ipai_ai_copilot/data/copilot_tools_bir.xml` — 8 BIR tool definitions
- `addons/ipai/ipai_bir_tax_compliance/models/bir_tax_return.py` — add `approved` state + `action_approve()`
- `addons/ipai/ipai_bir_tax_compliance/security/` — add `group_ipai_bir_approver`
- `infra/ssot/agents/tax_pulse_tool_contracts.yaml` — typed tool contracts

**Verification**:
- `compute_bir_vat_return` tool triggers `action_compute()` and returns amounts
- `validate_bir_return` tool triggers `action_validate()` and returns issues
- Approval gate blocks Actions tools without `group_ipai_bir_approver`

### Wave 4: Filing/Export Artifacts

**Goal**: Generate eFPS XML, PDF, alphalist from computed returns.

**Files**:
- `addons/ipai/ipai_bir_tax_compliance/reports/` — QWeb report templates
- `addons/ipai/ipai_bir_tax_compliance/wizards/bir_efps_export.py` — eFPS XML wizard
- `addons/ipai/ipai_bir_tax_compliance/wizards/bir_alphalist_generate.py` — alphalist wizard

**Verification**:
- eFPS XML validates against BIR schema
- PDF renders with correct amounts and TIN
- Alphalist aggregates correctly from WHT returns

### Wave 5: Project/Task/Approval Orchestration

**Goal**: Odoo-native recurring task templates and approval workflows.

**Files**:
- `addons/ipai/ipai_bir_tax_compliance/models/bir_filing_task_template.py` — template model
- `addons/ipai/ipai_bir_tax_compliance/data/bir_task_templates.xml` — seed data per form type
- `addons/ipai/ipai_bir_tax_compliance/views/bir_worklist_views.xml` — Kanban + calendar

**Dependencies**: Month-end closing task workbook (normalize to seed XML)

**Verification**:
- Cron generates filing tasks 15 days before deadline
- Tasks link to `bir.tax.return` records
- Kanban groups by filing stage
- Activities auto-created for approval steps

### Wave 6: Evals + SFT Dataset

**Goal**: Foundry evaluation datasets and fine-tuning assets for BIR domain.

**Files**:
- `eval/datasets/bir_advisory.yaml` — 50 informational test cases
- `eval/datasets/bir_ops.yaml` — 30 navigational test cases
- `eval/datasets/bir_actions.yaml` — 40 transactional test cases
- `eval/training/bir_sft_catalog.yaml` — training sample catalog
- `eval/training/bir_sft_train.jsonl` — training set (80%)
- `eval/training/bir_sft_valid.jsonl` — validation set (20%)

**Verification**:
- Advisory groundedness ≥ 0.8 on `bir_advisory.yaml`
- Actions safety = 1.0 on `bir_actions.yaml`
- SFT validation loss ≤ baseline threshold

### Wave 7: APIM/Foundry/Agent Framework Production Wiring

**Goal**: BIR pack integrated into production ingress and tracing.

**Files**:
- Agent capability matrix updated with BIR pack attachment
- Router rules updated for BIR intent classification
- APIM route configuration for BIR-specific endpoints

**Verification**:
- BIR requests route correctly through APIM → Advisory/Actions
- Traces visible in App Insights with BIR domain tags
- Pack degrades gracefully when BIR knowledge store unavailable

## Exit Gates Per Wave

| Wave | Gate |
|---|---|
| 1 | Advisory answers BIR questions with citations |
| 2 | 67 engine tests pass (COMPLETE) |
| 3 | All 8 tools trigger correct Odoo actions |
| 4 | eFPS XML + PDF + alphalist generate correctly |
| 5 | Task templates auto-generate, worklist renders |
| 6 | Eval datasets pass threshold scores |
| 7 | Production tracing visible, APIM routes work |

## Risk Mitigation

| Risk | Mitigation |
|---|---|
| BIR updates TRAIN rates mid-year | Versioned rates JSON; new file per tax year |
| eFPS XML schema undocumented | Reverse-engineer from BIR sample files; validate incrementally |
| Knowledge store lag on new regulations | Manual knowledge update process; flag stale citations |
| Approval workflow complexity | Use Odoo's native `mail.activity` first; escalate to Agent Framework only if needed |

---

## AFC Parity — Additional Phases

The following phases extend the original 7-wave plan with AFC parity requirements from the copilot agent framework analysis.

### Wave 1A: Knowledge Grounding (Azure AI Search)

**Goal**: Externalize all BIR tax knowledge into Azure AI Search for RAG grounding.

**Files**:
- Azure AI Search index `ipai-ph-tax-knowledge` with content:
  - Odoo 18 accounting docs
  - BIR forms catalog (all form types, requirements, deadlines)
  - BIR Revenue Regulations (full text)
  - Internal SOPs and compliance procedures

**Dependencies**: Wave 1 (knowledge ingestion creates raw content)

**Verification**:
- Advisory agent answers BIR questions with grounded citations from AI Search
- Knowledge freshness: index rebuild on RR/RMO updates

### Wave 3A: Read-Only Bridge API

**Goal**: Implement the narrow OpenAPI bridge between Foundry agents and Odoo.

**Files**:
- `agents/contracts/openapi/ipai_odoo_bridge.openapi.yaml` — OpenAPI spec (COMPLETE)
- Azure Function / FastAPI implementation for bridge endpoints
- APIM policy for `apim-ipai-dev.azure-api.net/odoo/*` routes

**Endpoints (read)**:
- `GET /compliance_findings` — retrieve findings by period/state
- `GET /compliance_tasks` — retrieve tasks
- `GET /compliance_periods` — retrieve periods
- Read endpoints for invoices, tax summaries, withholding lines, reports

**Dependencies**: Wave 3 (Odoo models must exist)

**Verification**:
- Bridge returns correct data for each endpoint
- APIM auth enforced (X-IPAI-Key required)
- No direct JSON-RPC calls from agent

### Wave 3B: Compliance Check Execution

**Goal**: Agent runs compliance checks from the check catalog against live Odoo data.

**Files**:
- `infra/ssot/tax/compliance_check_catalog.yaml` — check registry (COMPLETE)
- Bridge endpoint for check execution
- Odoo method on `tax.compliance.period` to run checks

**Verification**:
- Each of 12 checks (CI-001 through CI-012) executes and returns findings
- Findings are persisted as `tax.compliance.finding` records in Odoo
- High/critical severity findings trigger notification

### Wave 3C: Narrow Write Operations

**Goal**: Enable Phase 1 write surface through the bridge with confirmation.

**Endpoints (write)**:
- `PATCH /compliance_tasks/{id}` — update state, assignee, completion note
- `POST /compliance_findings` — create new finding
- `POST /chatter/{model}/{id}` — post audit note

**Confirmation requirement**: All writes present `ConfirmActionCard` to user before execution.

**Files**:
- `agents/contracts/ui/confirm_action_card.json` — Adaptive Card JSON (COMPLETE)
- Bridge write endpoint implementations
- Chatter note posting for audit trail

**Dependencies**: Wave 3A (bridge exists), Wave 3 (Odoo models exist)

**Verification**:
- Write blocked without confirmation
- Chatter note posted on every write
- Audit trail visible in Odoo mail thread

### Wave 5A: Teams Card Surfaces

**Goal**: Surface compliance data in Microsoft Teams via Adaptive Cards.

**Files**:
- `agents/contracts/ui/adaptive_cards_index.yaml` — card index (COMPLETE)
- Teams channel integration for `#tax-compliance`
- Proactive DM for deadline alerts

**Cards**:
- `ComplianceBriefingCard` — period summary posted to channel
- `FindingCard` — individual finding with Create/View buttons
- `TaskCard` — task with Mark Complete/Reassign buttons
- `DeadlineAlertCard` — proactive countdown DM

**Dependencies**: Wave 5 (task orchestration), Wave 3C (write bridge)

**Verification**:
- Cards render correctly in Teams
- Button actions route through bridge with confirmation
- Proactive alerts fire on schedule

### Wave 5B: Odoo Widget Integration

**Goal**: Surface Tax Pulse capabilities in the Odoo web client via `ipai_ai_copilot` widget.

**Files**:
- Widget integration in `ipai_ai_copilot` for BIR-specific panels
- Card rendering in Odoo OWL components

**Dependencies**: Wave 5A (card definitions exist)

**Verification**:
- Compliance briefing renders in Odoo widget
- Confirmation cards work in Odoo context
- Same card JSON used across Teams and Odoo

### Wave 7A: Production Hardening

**Goal**: Full production readiness for Tax Pulse capability pack.

**Checklist**:
- APIM rate limiting configured for bridge endpoints
- App Insights custom dimensions for BIR domain (check_id, form_code, severity)
- Graceful degradation when AI Search index unavailable
- Prompt versioning for Tax Pulse instructions
- Compliance check catalog schema validation in CI

**Verification**:
- Load test: 100 concurrent compliance check requests
- Failover: AI Search down -> agent responds with cached knowledge
- Tracing: end-to-end trace from Teams message to Odoo write
