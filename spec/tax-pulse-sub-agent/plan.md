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
