# Constitution — PPM Clarity for Odoo 18

## 1. Purpose

Deliver a Clarity PPM-equivalent project portfolio management capability
in Odoo 18 by composing CE + OCA + thin custom delta, not by building
a monolithic replacement module.

## 2. MVP Doctrine

This feature is an explicit MVP baseline for the IPAI platform workstream.

MVP sourcing order (mandatory):

1. CE-native in `project` / `analytic` / `account`
2. OCA-native in `project` / `timesheet` repos
3. OCA-native from adjacent repos (web, server-ux, reporting-engine)
4. Composite CE+OCA pattern
5. Thin custom delta (`ipai_finance_ppm`) only for unresolved gaps
6. External assist (Azure bridges) only when explicitly declared

A capability must not be marked as "custom delta" only because it is absent
from one repo. The full CE/OCA 18 ecosystem must be scanned before declaring
a custom gap.

Non-MVP bridge capabilities (OCR, AI review, governed Azure runtime) are
not required baseline. They are promotion-lane work.

## 3. Architecture Doctrine

### 3.1 CE + OCA first for PPM

The Clarity PPM replacement strategy for Odoo 18 must use:

1. **Odoo CE 18 `project`** as the base project-execution surface
2. **OCA `project`** modules as the default extension path for hierarchy,
   roles, stakeholders, timeline, analytics, review, and governance
3. A **thin `ipai_finance_ppm` delta module** only for portfolio-finance
   features not already covered by CE/OCA

The implementation must not recreate in custom code any capability already
available in:
- Odoo CE `project`
- OCA `project`
- OCA `timesheet`

### 2.2 `ipai_finance_ppm` scope restriction

`ipai_finance_ppm` is not the primary PPM foundation.
It is a **delta-only addon**.

It may own only:
- portfolio budget / forecast / variance
- portfolio health / RAG
- stage-gate / phase review objects if not covered by OCA
- risk / issue register
- scoring / prioritization
- capacity-vs-demand or finance-portfolio controls not available in CE/OCA

It must not own:
- generic project hierarchy (→ `project_parent`)
- generic project roles (→ `project_role`)
- generic stakeholders (→ `project_stakeholder`)
- generic project timeline views (→ `project_timeline`)
- generic project pivot analytics (→ `project_pivot`)
- generic project templates (→ `project_template`)
- generic task hierarchy / WBS features (→ `project_task_ancestor`)
- deprecated external event-bus residue unrelated to current platform doctrine

### 2.3 Clarity equivalence rule

The target is not "clone Clarity in one custom module".
The target is:
- CE/OCA-native where possible
- thin delta where necessary
- explicit gap documentation where parity is not yet achievable

Known planning/dependency gaps (e.g. `project_task_dependency` not ported)
must be documented instead of hidden by parity claims.

## 3. Mandatory Guardrails

### 3.1 No capability duplication
If CE or OCA provides it, the delta module must not reimplement it.

### 3.2 No deprecated infrastructure
The PPM module must not contain Supabase webhook/event-bus code, n8n
workflow bindings, or other deprecated integration patterns. External
service integration follows current platform doctrine (Azure-native).

### 3.3 No unrelated coupling
The PPM module must not own HR expense AI drafting, copilot tool bindings,
or other features outside portfolio management scope.

### 3.4 Multi-company by default
All delta models must use `company_id` fields and respect multi-company
rules, consistent with CE/OCA project behavior.

## 4. OCA Baseline Modules (Odoo 18)

These OCA modules form the structural foundation and must be treated as
the primary implementation layer before any custom code is written:

| Module | Capability |
|--------|-----------|
| `project_parent` | Portfolio hierarchy (parent-child projects) |
| `project_group` | Programme grouping |
| `project_department` | Department-based project classification |
| `project_stakeholder` | Stakeholder registry |
| `project_role` | Role-based resource assignment |
| `project_timeline` | Timeline / Gantt view |
| `project_pivot` | Pivot analytics |
| `project_milestone_status` | Milestone status reporting |
| `project_template` | Repeatable project blueprints |
| `project_key` | Project identifier / shortcode |
| `project_tag_hierarchy` | Hierarchical categorization |
| `project_task_ancestor` | Task hierarchy / WBS |
| `project_task_parent_completion_blocking` | Dependency enforcement |
| `project_reviewer` | Review/approval gates |
| `project_task_stage_mgmt` | Advanced stage management |
| `project_type` | Project type classification |

## 5. Known Gaps

| Gap | Impact | Status |
|-----|--------|--------|
| `project_task_dependency` | Task dependency chains / CPM | Not ported to OCA 18.0 |
| Interactive drag-and-drop Gantt | Resource leveling | EE-only, no OCA equivalent |
| Portfolio-level resource capacity | Demand vs supply planning | Requires custom delta |

## 6. MVP Is a Viable Horizontal Slice

For ERP/SaaS-adjacent features, MVP must be defined as the smallest viable
cross-cutting slice that delivers end-to-end value. Avoid isolated
component-only MVPs when the user workflow depends on multiple tightly
connected business objects.

## 7. SaaS and Multitenancy Are Separate Decisions

SaaS is the delivery/business model. Multitenancy is an architecture choice.
Tenant model, data isolation, and shared-component boundaries must be chosen
explicitly per feature.

## 8. External Checklists Inform Review, Not Source-of-Truth Design

Community and external review checklists may be used to validate readiness
and catch omissions, but they do not replace the feature bundle as the
source of truth.

- Azure review checklists are review aids and promotion-lane controls.
- Odoo go-live checklists are operational readiness aids.
- Neither may override Odoo-first workflow/accounting truth or the MVP
  scope defined in this bundle.

## 9. Odoo-Native Testing Is Required

Addon and bridge code must follow Odoo-native testing patterns.

At minimum:

- model/business logic tests use Odoo test case classes
- form-driven behaviors use server-side `Form` tests
- HTTP / tour behavior uses `HttpCase` only where UI flow coverage is actually required
- test selection must be explicit through tags
- browser-critical end-to-end flows may use Playwright where backend/form
  coverage is insufficient
- MVP is not complete without executable tests for core workflows

## 10. Browser Automation Is Targeted, Not Default

Playwright is reserved for browser-critical flows and smoke coverage.
Chrome DevTools is a debugging surface, not the primary test framework.
Manual QA and ad hoc scripts do not replace executable automated tests.

## 11. MCP Tooling Is Optional and Bounded

MCP servers are optional developer and operator tooling surfaces. They
assist with automation, debugging, reference lookup, and platform
validation. They must never own workflow state, business logic, or
approval truth.

Allowed roles:

- Playwright MCP for browser automation
- Chrome DevTools MCP for debugging
- Azure MCP Server for platform/runtime validation
- Microsoft Learn MCP for documentation lookup

Prohibited role: MCP as the primary owner of workflow or business state.

## 12. Experimental MCP Integrations Are Non-Critical

Experimental or preview MCP integrations (e.g., Azure AI Foundry MCP)
must not be on the MVP critical path. They may be evaluated and adopted
when stable, but must not block delivery or become implicit dependencies.

## 13. Foundry Project Connections Are Optional and Minimum-Necessary

The Foundry project (`ipai-copilot`) supports attachable connections (Azure OpenAI,
AI Search, Cosmos DB, Storage, Fabric, etc.). These are optional enrichments, not
mandatory baseline dependencies.

- Do not assume any connection is already configured unless explicitly proven.
- For the PPM / Clarity parity surface: no Foundry project connections are required
  for the MVP — the MVP runs on Odoo CE 18 + OCA modules with no AI surface.
  Azure AI-assisted portfolio review and Foundry runtime are promotion-lane only.
  If AI surfaces are added post-MVP, attach Azure OpenAI at that time and document
  the connection before implementation depends on it.
- Add only the minimum connections required for MVP.
- Microsoft Fabric is preview and must not be on the MVP critical path.
- Document every new project connection before implementation depends on it.

## 14. API Edge Replacement Is Facade-Only

FastAPI or external API layers may replace the public/mobile API edge,
but they must not replace Odoo/OCA as the owner of workflow, approvals,
accounting, tax, or ERP state. The FastAPI edge may package, orchestrate,
proxy, or expose workflows, but Odoo remains the authoritative write path
for all ERP business objects.
