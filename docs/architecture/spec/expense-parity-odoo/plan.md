# Implementation Plan — Expense Management Parity for Odoo 18

## 1. Strategy

This is a **composition formalization**, not a rewrite.

The expense stack is already correctly layered. The work is:
- Boundary hardening (document what each layer owns)
- Adjacent-module wiring (connect installed OCA modules to expense flow)
- Proof of current install/runtime state
- Gap documentation

## 2. Workstreams

### Workstream 1 — Baseline verification and ownership formalization

1. Verify CE `hr_expense` baseline capabilities on current runtime
2. Verify OCA `hr-expense` modules installed and functional
3. Verify `ipai_hr_expense_liquidation` v3 models and workflow
4. Verify `ipai_expense_ops` v1 approval chain and BIR hooks
5. Document proven vs declared vs candidate coverage

### Workstream 2 — Adjacent OCA module wiring

Wire already-installed OCA modules into the expense flow:

| Module | Wiring | Priority |
|--------|--------|----------|
| `dms` + `dms_field` | Receipt attachment archival on expense reports | P1 |
| `queue_job` | Async OCR pipeline via `ipai_document_intelligence` | P1 |
| `auditlog` | Audit rules for `hr.expense.sheet` and `cash.advance` | P1 |
| `document_page_approval` | Expense policy document versioning | P2 |
| `mis_builder` | Expense budget tracking integration | P2 |
| `helpdesk_mgmt` | Expense dispute ticket creation | P2 |

### Workstream 3 — Bridge evaluation

1. Verify `ipai_document_intelligence` bridge boundary is clean
2. Evaluate `account_bank_statement_import` + OCA statement modules for
   corporate card feed composition
3. Document bridge boundary: extraction in bridge, workflow in Odoo,
   `queue_job` for async orchestration

### Workstream 4 — Gap documentation

Document in SSOT parity matrix:
- OCR: bridge-required via Azure Document Intelligence
- Corporate card feeds: candidate composition / candidate bridge
- Mileage/per-diem: unresolved, PH-specific rates needed
- Mobile receipt capture: unresolved, EE-only

## 3. Target Implementation Shape

### CE baseline (installed)

| Module | Purpose |
|--------|---------|
| CE `hr_expense` | Core expense execution surface |
| CE `sale_expense` | Customer reinvoicing |
| CE `analytic` | Cost allocation |
| CE `account` | Posting and payment |

### OCA direct (installed)

| Module | Purpose |
|--------|---------|
| `hr_expense_advance_clearing` | Cash advance clearing |
| `hr_expense_payment` | Payment management |
| `hr_expense_tier_validation` | Multi-tier approval |
| `hr_expense_sequence` | Report sequencing |
| `hr_expense_advance_clearing_sequence` | Clearing sequencing |
| `base_tier_validation` | Approval framework |

### OCA adjacent (wire into expense flow)

| Module | Purpose |
|--------|---------|
| `dms` + `dms_field` | Receipt archival |
| `auditlog` | Change audit trail |
| `queue_job` | Async orchestration |
| `document_page_approval` | Policy versioning |
| `mis_builder` | Budget tracking |
| `helpdesk_mgmt` | Dispute tickets |

### Custom delta (keep as-is)

| Module | Purpose |
|--------|---------|
| `ipai_hr_expense_liquidation` v18.0.3.0.0 | PH liquidation lifecycle |
| `ipai_expense_ops` v18.0.1.0.0 | PH compliance/BIR |

### External bridges

| Module | Purpose |
|--------|---------|
| `ipai_document_intelligence` | OCR receipt extraction |

## 4. Module Boundary — TBWA Forms

Implement the TBWA cash advance and liquidation forms as thin addon surfaces only.

Recommended module split:

- `ipai_hr_cash_advance`
  - Cash advance request header
  - Request lines
  - Payment method
  - Approval / release workflow
  - Printable cash advance form (QWeb report)

- `ipai_hr_expense_liquidation_forms`
  - Liquidation header
  - Liquidation lines
  - Advance-to-liquidation linkage
  - Balance settlement logic
  - Printable itemized expense / liquidation form (QWeb report)

If an existing liquidation module already contains the core models
(`ipai_hr_expense_liquidation` v3 has `cash.advance`, `cash.advance.line`,
`hr.expense.liquidation`, `hr.expense.liquidation.line`), this feature
should patch that module instead of creating duplicate models. In that case,
only add:

- Missing fields required by the current paper forms
- Workflow refinements
- Totals / settlement behavior
- Printable report templates

## 5. Architecture Boundary — TBWA Forms

### Addon-owned

- Cash advance request state
- Liquidation state
- Form fields
- Settlement totals
- Signatures / signoff metadata
- Printable report layouts

### Odoo-owned

- User / employee identity
- Approvals
- Accounting posting
- Reimbursement / refund outcomes
- Access control
- Document attachments

### Optional bridge-owned (later)

- OCR extraction
- AI review assistance
- External card feeds
- External tax or compliance enrichment

## 6. Workflow Outline — TBWA Forms

1. User creates cash advance request
2. Request is approved
3. Advance is released / marked disbursed
4. User prepares liquidation / itemized expense report
5. Liquidation references the related advance where applicable
6. System computes:
   - Total expense
   - Total advance
   - Due to employee
   - Refundable by employee
7. Finance reviews / posts / approves
8. Case is closed or flagged overdue

## 7. Azure Boundary

Azure is an external intelligence and deployment substrate, not the source
of workflow truth.

Odoo CE 18 + OCA + thin IPAI delta remain the spend workflow core.
Azure-hosted capabilities may provide:

- OCR / document extraction (Azure Document Intelligence)
- Agentic review assistance (Azure-hosted agent surface)
- Search / retrieval over policies and evidence (Azure AI Search, if needed)
- Orchestration surfaces for review queues (Azure Container Apps)

They must not replace:

- Odoo expense lifecycle truth
- Accounting posting truth
- Approval state truth
- Policy enforcement record truth

Azure delivery path selection (Lane A pilot vs Lane B governed production)
is defined in `spec/reverse-sap-concur/plan.md` and applies to the
intelligence/bridge layer, not to the Odoo workflow core.

## 8. Current Azure MVP Baseline

The MVP targets the existing Azure dev footprint and should prefer reuse over new infrastructure.

Current baseline includes:

- runtime RG: `rg-ipai-dev-odoo-runtime`
- data RG: `rg-ipai-dev-odoo-data`
- platform RG: `rg-ipai-dev-platform`
- network: `vnet-ipai-dev`
- WAF: `wafipaidev`
- PostgreSQL Flexible Server: `pg-ipai-odoo`
- Key Vault: `kv-ipai-dev`
- private endpoints / private DNS for Key Vault and PostgreSQL
- Log Analytics workspaces already provisioned
- Container Apps already provisioned in the runtime RG

MVP work must assume this footprint is the default target unless a missing capability is explicitly proven.

## 9. Runtime Baseline

Expense, cash advance monitoring, liquidation, and mobile companion MVP must target the already-provisioned Azure environment.

Reuse first:

- `pg-ipai-odoo` for transactional persistence through Odoo
- `kv-ipai-dev` for secrets/config
- existing runtime Container Apps for companion/API surfaces where needed
- existing VNet / private endpoint topology
- existing Front Door WAF for exposed surfaces

No new standalone persistence or parallel workflow backend is allowed for MVP.

## 10. SaaS / Multitenancy Guidance

Treat SaaS as the business model and multitenancy as an architecture decision.
Document:

- tenant definition
- shared vs isolated components
- control-plane responsibilities
- operational rollout strategy

### Promotion-lane SaaS controls

The following are promotion-lane capabilities unless explicitly required in MVP:

- deployment stamps
- advanced tenant isolation automation
- safe deployment rings
- feature flag operations
- live-site automation at scale

## 11. Testing Strategy

Use Odoo-native backend testing as the default strategy.

Preferred layers:

- `TransactionCase` for business logic and model behavior
- `Form` for onchange/default/form-flow fidelity
- `HttpCase` for end-to-end web/tour flows only when the workflow truly requires browser coverage
- `@tagged(...)` and `--test-tags` for explicit execution control

Use Playwright only for critical mobile companion browser flows or thin
end-user smoke coverage.

Use Chrome DevTools for debugging mobile/browser issues.

## 12. MCP Tooling Boundary

Allowed MCP tooling roles:

- Playwright MCP for browser automation
- Chrome DevTools MCP for debugging
- Azure MCP Server for platform/runtime validation
- Microsoft Learn MCP for trusted Microsoft documentation lookup

Prohibited role: using MCP as the primary owner of workflow or business state.

## 13. Review and Go-Live Inputs

### Azure review-checklists

Use Azure review-checklists as a structured architecture review input for:

- multitenancy
- WAF / perimeter controls
- AI landing zone
- cost
- application delivery/networking

Treat these as review aids, not architecture sign-off.

### Odoo 18 go-live checklist

Use the Odoo 18 community go-live checklist as a cutover/readiness input for:

- opening entries import
- inventory readiness
- receivable/payable balancing
- payment and reconciliation checks
- finance go-live validation

Treat this as an operational checklist seed that must be adapted to the
target localization and workflow.

## 12. API Replacement Strategy

Do not replace Odoo/OCA 18 as the owner of business workflow or accounting truth.

Allowed replacement:

- replace only the external API edge with a thin FastAPI facade or sidecar

Odoo-owned:

- business objects
- approvals
- accounting/tax/expense state
- final write-path integrity

FastAPI-owned:

- external/mobile/public API surface
- orchestration endpoints
- async job handling
- webhook ingestion
- API auth/rate-limit/productization

Prohibited:

- direct writes from FastAPI to Odoo PostgreSQL tables
- duplicate business rules in FastAPI
- parallel transactional truth outside Odoo

## 13. Azure API Edge Baseline

The default external API edge for mobile, public, partner, and async
workloads is a thin FastAPI layer on Azure Container Apps.

Preferred accelerator baseline:

- FastAPI Membership API Template for Azure Container Apps

Allowed responsibilities:

- external/mobile API surface
- webhook ingestion
- async orchestration
- notifications/reminders
- bounded AI-assisted facade behavior
- optional edge-local cache/session/job state

Prohibited responsibilities:

- owning ERP transactional truth
- direct writes to Odoo PostgreSQL business tables
- duplicate approval/accounting/tax logic outside Odoo

## 14. AI Template Baseline

Where AI companion surfaces are required, prefer lightweight Azure
AI/chat/agent templates and managed identity patterns. Do not make heavy
OCR/multimodal templates part of MVP unless extraction is explicitly
required.

## 15. Proof Gates

The formalization is complete only when:

- CE/OCA expense baseline is verified on current runtime
- Custom delta boundary is documented with may-own/must-not-reimplement
- Adjacent OCA wiring is proven or documented as candidate
- OCR bridge boundary is explicit (bridge = extraction, Odoo = workflow)
- Known gaps are documented in SSOT parity matrix
- No architecture claim implies unverified runtime truth
