# Implementation Plan — PPM Clarity for Odoo 18

## 1. Strategy Reset

Refactor the delivery strategy from:
- "enhance the existing custom PPM addon"

To:
- "compose CE + OCA baseline, then shrink `ipai_finance_ppm` to delta-only scope"

## 2. Workstreams

### Workstream 1 — Baseline inventory and ownership reset

1. Confirm CE `project` baseline surface
2. Confirm OCA `project` and `timesheet` modules to adopt as canonical base
3. Classify every existing `ipai_finance_ppm` feature as:
   - Replace with CE
   - Replace with OCA
   - Keep as thin delta
   - Delete as deprecated residue

### Workstream 2 — Module decomposition

Refactor `ipai_finance_ppm` into:
- CE/OCA configuration + install-set composition
- Minimal custom models for finance-portfolio delta
- Removal of unrelated/deprecated event-bus or non-PPM glue

Specific removals:
- `project_task_integration.py` — Supabase webhook event emission (deprecated)
- `hr_expense.py` — Pulser AI draft binding (unrelated to PPM)
- `data/ir_cron_ppm_sync.xml` — cron referencing deprecated webhook
- `data/ir_config_parameter_powerbi.xml` — evaluate if still needed
- `static/src/js/okr_dashboard_action.js` — rewrite or remove empty shell

Specific additions (delta models):
- `ppm.budget.line` — budget/forecast/actual per project per period
- `ppm.portfolio.health` — RAG status + health scoring per project
- `ppm.risk` — risk register linked to projects
- `ppm.issue` — issue register linked to projects
- `ppm.scoring` — investment scoring / prioritization
- `ppm.gate.review` — phase-gate review records

### Workstream 3 — Parity and gap management

Document:
- What is now covered by CE/OCA
- What remains delta
- What remains a known gap

Known project-planning dependency gaps must be tracked explicitly and
not hidden under parity claims.

## 3. Target Implementation Shape

### CE / OCA base (install set)

| Module | Purpose |
|--------|---------|
| CE `project` | Core execution surface |
| `project_parent` | Portfolio hierarchy |
| `project_group` | Programme grouping |
| `project_department` | Department classification |
| `project_stakeholder` | Stakeholder registry |
| `project_reviewer` | Review gates |
| `project_role` | Role-based assignment |
| `project_timeline` + `web_timeline` | Timeline view |
| `project_pivot` | Pivot analytics |
| `project_milestone_status` | Milestone reporting |
| `project_template` | Project templates |
| `project_key` | Project shortcodes |
| `project_tag_hierarchy` | Tag classification |
| `project_task_ancestor` | Task hierarchy |
| `project_task_parent_completion_blocking` | Dependency enforcement |
| `project_task_stage_mgmt` | Stage management |
| `project_type` | Type classification |

### Thin custom delta (`ipai_finance_ppm` v18.0.2.0.0)

Only these families remain custom:
- Portfolio finance measures (budget/forecast/variance)
- Portfolio governance objects (gate reviews)
- Risk/issue/scoring
- Executive portfolio rollups (RAG dashboard)

### Manifest dependencies

```python
"depends": [
    "project",
    "account",
    "analytic",
    "project_parent",
    "project_milestone_status",
]
```

## 4. MVP Deployment Mode

The PPM MVP runs on Odoo CE 18 + OCA modules. No Azure bridge or governed
runtime is required for the MVP. Azure services are promotion-lane only.

- **MVP**: Odoo CE 18 + OCA project/timesheet + thin `ipai_finance_ppm` delta
- **Promotion**: Azure-hosted dashboards, AI-assisted portfolio review, Foundry runtime

## 5. SaaS / Multitenancy Guidance

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

## 6. Testing Strategy

Use Odoo-native backend testing as the default strategy.

Preferred layers:

- `TransactionCase` for portfolio/project/task business rules
- `Form` for reviewer/stakeholder/task-entry flows
- `HttpCase` only if there is a truly browser-critical operator path
- `@tagged(...)` and `--test-tags` for explicit execution control

## 7. MCP Tooling Boundary

Allowed MCP tooling roles:

- Microsoft Learn MCP for design/reference support
- Azure MCP Server for platform validation
- Playwright MCP only for thin browser-critical operator flows

Prohibited role: using MCP as the primary owner of workflow or business state.

## 8. Review and Go-Live Inputs

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

## 8. API Replacement Strategy

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

## 9. Azure API Edge Baseline

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

## 10. AI Template Baseline

Where AI companion surfaces are required, prefer lightweight Azure
AI/chat/agent templates and managed identity patterns. Do not make heavy
OCR/multimodal templates part of MVP unless extraction is explicitly
required.

## Foundry Project Baseline

Confirmed Foundry project baseline:

- project: `ipai-copilot`
- parent resource: `ipai-copilot-resource`
- resource group: `rg-data-intel-ph`
- region: `eastus2`
- project endpoint: `https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot`

## Connected Resources Strategy

The Foundry project uses attachable connections. Do not assume Azure AI Search,
Azure OpenAI, Cosmos DB, Storage, Application Insights, Bing grounding, or Fabric
are already attached unless explicitly verified.

For this bundle (PPM / Clarity parity), MVP connections:

- no Foundry project connections are required for the PPM MVP — the MVP runs on
  Odoo CE 18 + OCA modules with no AI surface
- Azure AI-assisted portfolio review and Foundry runtime are promotion-lane only
- if AI surfaces are added post-MVP, attach Azure OpenAI at that time and document
  the connection before implementation depends on it
- keep Azure AI Search, Cosmos DB, Bing grounding, Fabric, and Serverless Model
  connections off the critical path unless explicitly justified

## 11. Proof Gates

The refactor is complete only when:
- No CE/OCA-covered capability remains custom without a documented reason
- `ipai_finance_ppm` no longer owns generic project shell features
- Deprecated integration residue is removed
- Known parity gaps are documented in SSOT and docs
- Module installs cleanly with `--test-enable`
