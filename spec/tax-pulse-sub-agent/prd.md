# PRD — Tax Pulse Sub-Agent (BIR Compliance Pack)

## Core Objective

Build **Tax Pulse** as a tax-compliance capability pack for Odoo Copilot that can:
- Explain PH BIR compliance (informational)
- Inspect filing readiness (navigational)
- Compute/validate selected returns (transactional)
- Generate filing artifacts (transactional)
- Route work into Odoo-native projects/tasks/activities (workflow)
- Enforce approval-gated tax operations (governance)

## Product Scope

### Tax Calculation Sublayer
- TRAIN law income tax brackets (annual, versioned)
- VAT computation (output, input, payable, adjustments, penalties)
- Expanded Withholding Tax (EWT) — 10 ATC codes (W010–W170)
- Final Withholding Tax (FWT) — 5 ATC codes
- Corporate income tax (25% regular, 2% MCIT)
- JSONLogic rules engine for deterministic evaluation
- Externalized rates JSON for version-independent updates

### Tax Workflow Sublayer
- Filing lifecycle: Draft → Computed → Validated → Approved → Filed → Confirmed
- Approval gates modeled after Odoo PLM-style required/optional approval behavior
- Month-end close checklists via `project.task` templates
- Filing deadline tracking with automatic activity generation
- Overdue/compliance worklist views

### Tax Knowledge Sublayer
- BIR Revenue Regulations grounding (Azure AI Search / Foundry IQ)
- Form-specific filing instructions and requirements
- Penalty and surcharge computation rules
- Deadline calendars per form type and frequency

### Document Intake & Extraction Linkage
- Invoice/receipt ingestion via Azure Document Intelligence
- BIR attachment classification
- Document-to-return record linking
- Evidence normalization for tax workflows

### Filing Artifact Pipeline
- eFPS XML export (BIR electronic filing format)
- PDF generation for manual filing
- Alphalist generation (1604-CF, 1604-E)
- 2316 Certificate of Compensation generation

## Capability Classes (Joule-Style Benchmark)

| Class | Examples | Runtime |
|---|---|---|
| **Informational** | Explain forms, deadlines, rules, statuses, penalty calculation | Advisory |
| **Navigational** | Locate return, task, blocker, workflow stage, approver, overdue items | Ops |
| **Transactional** | Compute, validate, export, prepare filing package, generate alphalist | Actions |

## Runtime Ownership

| Capability | Advisory | Ops | Actions | Router |
|---|---|---|---|---|
| Explain BIR rules/rates | Yes | — | — | — |
| Inspect filing readiness | — | Yes | — | — |
| Check overdue filings | — | Yes | — | — |
| Compute VAT/EWT/WHT | — | — | Yes (approval) | Routes |
| Validate return | — | — | Yes (approval) | Routes |
| Generate eFPS/PDF | — | — | Yes (approval) | Routes |
| Generate alphalist | — | — | Yes (approval) | Routes |
| Search compliance KB | Yes | Yes | — | — |

## Tool Contracts

| Tool | Agent | Input | Output | Approval |
|---|---|---|---|---|
| `bir_compliance_search` | Advisory, Ops | query string | grounded explanation + citations | None |
| `check_overdue_filings` | Ops | optional: form_type, company_id | list of overdue `bir.filing.deadline` records | None |
| `compute_bir_vat_return` | Actions | return_id | computed amounts + validation result | Required |
| `compute_bir_withholding_return` | Actions | return_id | computed amounts + validation result | Required |
| `validate_bir_return` | Actions | return_id | validation pass/fail + issues list | Required |
| `generate_alphalist` | Actions | period, form_type | alphalist record + summary | Required |
| `generate_efps_xml` | Actions | return_id | XML file attachment | Required |
| `generate_bir_pdf` | Actions | return_id | PDF file attachment | Required |

## Approval Gates

Modeled after Odoo 18 PLM approval patterns:
- **Required approval**: Compute, validate, file operations
- **Optional approval**: Search, inspect, explain operations
- **Approval flow**: Router pauses → Activity created → Approver acts → Router resumes
- **Approver roles**: `group_ipai_bir_approver`, `group_ipai_finance_manager`

## Eval Datasets

| Dataset | Purpose | Count | Agent |
|---|---|---|---|
| `bir_advisory.yaml` | Informational accuracy + grounding | 50 cases | Advisory |
| `bir_ops.yaml` | Navigational accuracy + completeness | 30 cases | Ops |
| `bir_actions.yaml` | Transactional correctness + safety | 40 cases | Actions |

## SFT Training Assets

| Asset | Purpose |
|---|---|
| `bir_sft_catalog.yaml` | Training sample catalog with metadata |
| `bir_sft_train.jsonl` | Fine-tuning training set (80%) |
| `bir_sft_valid.jsonl` | Fine-tuning validation set (20%) |

## Success Criteria

1. VAT computation matches golden dataset within ₱0.01
2. EWT computation matches all 10 ATC codes in test fixtures
3. TRAIN bracket continuity — no gaps/overlaps in annual brackets
4. Overdue filings correctly identified within 1 business day
5. Approval gate blocks all transactional tools without authorization
6. Advisory groundedness ≥ 0.8 on BIR eval dataset
7. Actions safety = 1.0 (no unauthorized tax operations)
8. Filing artifacts pass BIR eFPS schema validation
9. Task templates generate correct recurring tasks per form cadence
10. No EE module dependencies in any code path

## Do Not

- Create a new top-level Foundry agent for Tax Pulse
- Hold tax computation state in prompts or chat memory
- Bypass Odoo's state machine for filing lifecycle
- Hardcode rates in Python (use externalized JSON)
- Generate tax advice without grounding citations
- Allow Advisory to trigger compute/file operations

---

## AFC Parity — Compliance Check Catalog

Tax Pulse compliance intelligence is driven by a machine-readable check catalog, not hardcoded prompt logic.

**SSOT**: `infra/ssot/tax/compliance_check_catalog.yaml`

The catalog defines 12 checks (CI-001 through CI-012) covering:
- Missing EWT on vendor bills (CI-001)
- Output/Input VAT vs SLSP gaps (CI-002, CI-003)
- Compensation WHT remittance (CI-004)
- Ungenerated BIR 2307 certificates (CI-005)
- ATC code completeness (CI-006)
- Filing deadline countdown (CI-007)
- Overdue compliance tasks (CI-008)
- DST on applicable documents (CI-009)
- QAP/SAWT completeness (CI-010, CI-011)
- Period completion status (CI-012)

Each check specifies: `check_id`, `severity`, `trigger_type`, `query_source` (Odoo model), `capability_class`, and `requires_human_review`.

## BIR Tool Inventory via Odoo Bridge

Agent tools do NOT call Odoo JSON-RPC directly. All tool calls route through a narrow OpenAPI bridge:

```
Foundry Agent -> APIM Gateway -> Bridge API -> Odoo JSON-RPC
```

**Bridge OpenAPI spec**: `agents/contracts/openapi/ipai_odoo_bridge.openapi.yaml`

Phase 1 write surface is intentionally narrow:
- `updateComplianceTask` — state, assignee, completion_note
- `createComplianceFinding` — new finding from compliance check
- `postChatterNote` — audit trail on any Odoo record

Deferred (not Phase 1): `uploadAttachment`, `genericRecordMutation`, `directFilingFlags`

## Externalized Tax Truth

Tax computation rules, rates, and BIR regulations are NOT embedded in agent prompts or instructions. They are externalized to:

| Source | Type | Content |
|---|---|---|
| `data/rates/ph_rates_2025.json` | Versioned JSON | TRAIN brackets, EWT, FWT, corporate, VAT rates |
| `data/rules/vat.rules.yaml` | JSONLogic | 8 VAT computation rules |
| `data/rules/ewt.rules.yaml` | JSONLogic | 11 EWT computation rules |
| `infra/ssot/tax/compliance_check_catalog.yaml` | SSOT YAML | 12 compliance intelligence checks |
| Azure AI Search index `ipai-ph-tax-knowledge` | RAG | BIR regulations, form guides, SOPs |

This ensures the agent can be updated without redeploying prompts, and tax truth is auditable and version-controlled.

## Module Ownership

| Concern | Owning Module |
|---|---|
| Compliance checks, findings, periods | `ipai_bir_tax_compliance` |
| Deadline alerts, proactive notifications | `ipai_bir_notifications` |
| Month-end close orchestration | `ipai_finance_ppm` |
| Copilot runtime, tool dispatch, cards | `ipai_odoo_copilot` |

## Execution surfaces

- Odoo: canonical compliance objects, tasks, findings, approvals, evidence
- Foundry / Agent Framework: reasoning, guidance, routing, bounded action planning
- n8n: asynchronous automation, notification relays, connector workflows, package movement
- Databricks: analytical marts, monitoring signals, forecasting, status intelligence
