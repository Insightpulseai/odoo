# Copilot Target-State — Tasks

## Confirmed Milestones

| Milestone | Evidence | Date |
| --- | --- | --- |
| Foundry agent identities visible in M365 admin center | `data-intel-ph-resource-data-intel-ph-AgentIdentity`, `AgentIdentityBlueprint`, project object | 2026-03-20 |
| Entra agent governance surface active in tenant | M365 admin → All agents shows Foundry-backed entries | 2026-03-20 |
| `ipai_odoo_copilot` installed on local `odoo_dev` | `state=installed` verified via psql | 2026-03-20 |
| Canonical unified baseline frozen | Constitution, PRD, plan, planning guide committed | 2026-03-20 |

## Private Deployment Gap Checklist

From: Foundry project identity visible in M365 admin
To: Named `InsightPulseAI Odoo Copilot` app privately deployable in tenant

### Phase A — Make the agent consumable

- [ ] Publish Foundry agent as Agent Application (creates stable endpoint + dedicated identity)
- [ ] Reassign RBAC/permissions to the published agent identity (permissions do NOT transfer automatically)
- [ ] Verify stable endpoint with actual invocation (Responses-protocol endpoint)

### Phase B — Make it productized

- [ ] Define product name: `InsightPulseAI Odoo Copilot`
- [ ] Build M365/Teams package using Agents Toolkit (supports org catalog + Marketplace)
- [ ] Deploy to org catalog / private tenant
- [ ] Verify app appears as productized entry in M365 admin (not just identity object)

### Phase C — Make it operationally safe

- [ ] Prove Odoo end-to-end: `ipai_odoo_copilot` on `odoo_dev` → ask → agent → response → chatter
- [ ] Lock bounded tool contract (scoped tools, no unrestricted mutation)
- [ ] Add eval pack with thresholds and pass/fail evidence
- [ ] Prepare admin approval/onboarding runbook
- [ ] Document privacy/boundaries for the agent
- [ ] Decision: private-only vs future Marketplace track

### Go/No-Go for Private Deployment

Ready when ALL true:
- [ ] Published Agent Application callable
- [ ] RBAC reassigned to published identity
- [ ] Odoo Copilot works e2e on canonical baseline
- [ ] M365/Teams package installs in private tenant
- [ ] Admin approval flow documented and tested

---

## Marketplace-Readiness Gap Matrix

| # | Surface | Gap | Exit Artifact | Owner | Priority |
| --- | --- | --- | --- | --- | --- |
| 1 | Foundry agent publishing | No published agent endpoint | Published app ID, endpoint, auth, versioning | `agent-platform` | P0 |
| 2 | Odoo Copilot e2e | No proven user flow | Demo: prompt → agent → response → chatter/audit | `odoo` | P0 |
| 3 | Capability contract | No user-facing scope/boundaries | Capability spec: informational, navigational, transactional, non-goals | `odoo` | P0 |
| 4 | Agent tool contract | No concrete registry | Agent manifest, tool contract, supported-intent matrix | `agent-platform` | P0 |
| 5 | Evaluation pack | No formal eval suite | Evals + thresholds + regression for grounding, safety, yield | `agent-platform` | P0 |
| 6 | Privacy / data handling | No public package | Privacy doc, retention, data-processing sheet | `platform` | P0 |
| 7 | M365/Teams packaging | No app manifest | App package, icons, screenshots, install flow | `agent-platform` | P1 |
| 8 | OCR normalization | No canonical schema | Schema, writeback contract, failure taxonomy | `platform` | P1 |
| 9 | Tenant admin enablement | No onboarding path | Admin guide, config contract, support flow | `platform` | P1 |
| 10 | Infra identity proof | No production-grade proof | Key Vault/identity contract, route map, tracing | `infra` | P1 |
| 11 | SLO baseline | No operational targets | Performance baseline, uptime targets, smoke evidence | `infra` | P1 |
| 12 | Partner Center offer | No submission assets | Listing copy, categories, support/privacy links | `agent-platform` | P2 |
| 13 | Certification buffer | No review timeline | Submission plan (expect up to 4 weeks) | `agent-platform` | P2 |

### Phase Readiness

| Phase | Goal | Verdict |
| --- | --- | --- |
| Phase 1 | Internal SAP Joule benchmark | Reachable now |
| Phase 2 | Private M365/Teams deployment | Blocked (items 1, 7, 9) |
| Phase 3 | Public Marketplace launch | Not ready (items 1-13) |

### Go/No-Go

- [ ] Foundry agent published and versioned
- [ ] M365/Teams package installs cleanly
- [ ] Odoo Copilot + OCR end to end on canonical baseline
- [ ] AI quality pack with explicit thresholds
- [ ] Privacy/data handling docs public
- [ ] Partner Center assets complete

---

## Wave 1: Lock the Assistant Surface

- [ ] **1.1** Create BIR regulation knowledge store in Foundry IQ
- [ ] **1.2** Upload form-type guides (2550M, 2550Q, 1601-C, 1601-E, etc.)
- [ ] **1.3** Register knowledge store in Foundry project
- [x] **1.4** Create eval datasets: `bir_advisory.yaml` (50 cases)
- [x] **1.5** Create eval datasets: `bir_ops.yaml` (30 cases)
- [x] **1.6** Create eval datasets: `bir_actions.yaml` (40 cases)
- [ ] **1.7** Configure guardrails: no ungrounded tax advice
- [ ] **1.8** Enable App Insights tracing for `ipai-odoo-copilot-azure`
- [ ] **1.9** Wire Azure Document Intelligence for invoice/receipt/BIR extraction
- [ ] **1.10** Run Advisory eval: groundedness ≥ 0.8

## Wave 2: Build Hidden Backend Roles

- [ ] **2.1** Create `copilot_router.py` (deterministic, no LLM)
- [ ] **2.2** Implement Ops runtime — read-only Odoo queries
- [ ] **2.3** Implement Actions runtime — approval-gated state transitions
- [ ] **2.4** Add `approved` state to `bir.tax.return`
- [ ] **2.5** Add `action_approve()` with `group_ipai_bir_approver` check
- [ ] **2.6** Create `group_ipai_bir_approver` security group
- [ ] **2.7** Update `action_file()` to require `state == 'approved'`
- [ ] **2.8** Create `copilot_tools_bir.xml` with 8 BIR tool definitions
- [ ] **2.9** Wire tools: `compute_bir_vat_return` → `action_compute()`
- [ ] **2.10** Wire tools: `compute_bir_withholding_return` → `action_compute()`
- [ ] **2.11** Wire tools: `validate_bir_return` → `action_validate()`
- [ ] **2.12** Wire tools: `check_overdue_filings` → `bir.filing.deadline` query
- [ ] **2.13** Wire tools: `generate_alphalist`, `generate_efps_xml`, `generate_bir_pdf`
- [ ] **2.14** Write router unit tests: 100 test cases
- [ ] **2.15** Run Actions eval: safety = 1.0

## Wave 3: Operationalize Odoo Project

- [ ] **3.1** Create `bir.filing.task.template` model
- [ ] **3.2** Fields: form_type, cadence, lead_days, owner_role, prerequisite_state, approval_required
- [ ] **3.3** Normalize month-end closing workbook into seed XML
- [ ] **3.4** Create seed data: task templates for all 24 form types
- [ ] **3.5** Create cron: auto-generate tasks N days before deadline
- [ ] **3.6** Implement task dependency chains (reconcile → compute → validate → ... → confirm)
- [ ] **3.7** Create milestones: books ready, tax computed, validated, approved, filed, paid, closed
- [ ] **3.8** Create project roles: preparer, reviewer, approver, payer, compliance owner
- [ ] **3.9** Create company-scoped compliance project template
- [ ] **3.10** Create Kanban view grouped by project stage
- [ ] **3.11** Create calendar view with filing deadlines
- [ ] **3.12** Create "blocked filings" filter
- [ ] **3.13** Link generated tasks to `bir.tax.return` records

## Wave 4: Add Approval Semantics

- [ ] **4.1** Design PLM-style approval extension model
- [ ] **4.2** Implement required/optional/comments-only approval types
- [ ] **4.3** Gate: for review → approved for export (required: `group_ipai_bir_approver`)
- [ ] **4.4** Gate: approved for export → filed (required: `group_ipai_finance_manager`)
- [ ] **4.5** Gate: filed/paid → confirmed (required: compliance owner)
- [ ] **4.6** Auto-create activity on approval request
- [ ] **4.7** Blocked state when required approval missing
- [ ] **4.8** Audit trail: who approved, when, comments
- [ ] **4.9** Tests: required approval blocks transition, optional does not

## Wave 5: Bind Artifacts and Evidence

- [ ] **5.1** Link BIR return ↔ project task (Many2one)
- [ ] **5.2** Attach export artifacts (eFPS XML, PDF, alphalist) to task
- [ ] **5.3** Add proof-of-filing attachment field
- [ ] **5.4** Add proof-of-payment attachment field
- [ ] **5.5** Add approver evidence fields (who, when, comments)
- [ ] **5.6** Create evidence completeness check before period close
- [ ] **5.7** Wire APIM production ingress
- [ ] **5.8** End-to-end test: task → return → artifact → proof → approval chain
- [ ] **5.9** Configure APIM routes for BIR-specific endpoints

## Epic 1.2 — Bootstrap & Landscape
- [ ] define system landscape object model
- [ ] define entity/calendar/jurisdiction registration
- [ ] define scenario enablement workflow
- [ ] add readiness/preflight checks

## Epic 1.3 — Security & Access
- [ ] define close/control role families
- [ ] build role assignment flows
- [ ] add authorization-group model
- [ ] enforce permission boundaries across define/run/review/approve/archive actions

## Epic 1.4 — Connectivity Registry
- [ ] define connection/adaptor registry
- [ ] define sync/job status model
- [ ] define adapter contracts (read/write/auth/evidence/failure semantics)
- [ ] expose connected-system health to operators

## Epic 1.5 — Monitoring & Reliability
- [ ] build run monitor
- [ ] build connector-health and sync-failure views
- [ ] build degraded-mode state handling
- [ ] add retry/escalation logging

## Epic 1.6 — Lifecycle & Retention
- [ ] build archive/restore flows
- [ ] build auditor export center
- [ ] define retention/anonymization/purge workflows
- [ ] build offboarding checklist with guarded destructive controls

## Epic 1.7 — Payment Operations
- [ ] detect and model payment configuration readiness
- [ ] build payment proposal object model
- [ ] build payment blocker/reason model
- [ ] add confirmation UX for payment execution
- [ ] enforce role/approval checks before release
- [ ] log payment evidence, remittance artifacts, and execution results

## Epic 1.8 — Sandboxed Artifact Workspace
- [ ] define workspace session object model
- [ ] define scoped context-pack ingestion
- [ ] define artifact object model and lifecycle states
- [ ] build artifact shelf and preview/compare surfaces
- [ ] support direct generation of XLSX, CSV, PDF, DOCX, PPTX, JSON, XML, and evidence bundles
- [ ] support attach-to-record and export flows
- [ ] support request-writeback workflow with approval gate
- [ ] audit-log workspace actions, generated files, and publish/writeback decisions

## Epic 1.8.1 — Artifact Preview & Review
- [ ] define artifact preview object/state model
- [ ] build inline preview renderer by file type/class
- [ ] build tabular preview for spreadsheet and schedule outputs
- [ ] build structured preview for JSON/XML/extracted fields
- [ ] build compare/diff view for versioned artifacts
- [ ] surface warnings, confidence flags, and unresolved fields
- [ ] support approve/export/attach/regenerate/discard/writeback actions from preview
- [ ] audit-log preview opens, decisions, and version-specific approvals

## Epic 1.9 — Skill Registry & Capability Truth
- [ ] define canonical skill registry model
- [ ] map UI capability statements to concrete skills
- [ ] add prerequisite/configuration checks per skill
- [ ] add role-based availability checks
- [ ] add runtime guard so unavailable skills are described as unavailable/configurable instead of falsely available
- [ ] add audit/logging contract per skill

## Epic 2.0 — Execution Mode & Autonomy Control
- [ ] define execution mode object model
- [ ] define per-skill allowed-mode policy
- [ ] define low-risk vs high-risk action taxonomy
- [ ] build mode selector and risk banner UX
- [ ] build confirmation-gating for high-risk actions
- [ ] build audit logs for autonomous vs confirmed actions
- [ ] add environment-level policy to disable guarded autonomy where required

## Epic 2.2 — Product & Finance Skill Packs
- [ ] register product skill-pack identifiers and contracts
- [ ] register finance skill-pack identifiers and contracts
- [ ] wire research/content/forecast/reporting skills to artifact workspace and preview
- [ ] add source/citation behavior for external-research outputs
- [ ] seed representative demo prompts and expected outputs
- [ ] validate that skill availability is role/configuration-aware

## Epic 2.4 — Databricks Handoff & Launch Registry
- [ ] define Databricks destination registry model
- [ ] define Odoo context-pack schema for launches
- [ ] build Open in Databricks button/smart action
- [ ] build optional Copilot Databricks mode toggle
- [ ] map portfolio/program/project contexts to relevant Databricks dashboards/apps
- [ ] map close/compliance contexts to relevant Databricks destinations
- [ ] add launch audit logging and fallback handling for unmapped destinations
- [ ] add return-link/back-to-Odoo behavior

## Epic 2.1 — Attachment Intake & File Analysis
- [ ] define attachment session and file metadata model
- [ ] support multi-file upload in copilot conversations
- [ ] classify file type and route to the correct analysis skill
- [ ] support PDF/image OCR and structured extraction
- [ ] support spreadsheet/document parsing and comparison
- [ ] support file-to-finding, file-to-artifact, and file-to-draft workflows
- [ ] support attach-to-record / promote-to-evidence-pack flows
- [ ] add unsupported/low-confidence/error states with explicit user feedback
- [ ] audit-log uploads, analysis steps, generated outputs, and approval/writeback decisions

---

## Completed (Cross-cutting)

- [x] **X.1** Create `spec/copilot-target-state/` spec kit
- [x] **X.2** Create `spec/tax-pulse-sub-agent/` spec kit
- [x] **X.3** Port TaxPulse rates, rules engine, test fixtures (67 tests)
- [x] **X.4** Create `infra/ssot/agents/tax_pulse_tool_contracts.yaml`
- [x] **X.5** Register BIR pack in `agent_capability_matrix.yaml`
- [x] **X.6** Create eval datasets (advisory, ops, actions)
- [x] **X.7** Create SFT training assets (catalog, train, valid)
