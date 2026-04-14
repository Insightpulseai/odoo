# MODULE_INTROSPECTION.md — ipai_finance_gl

## Why this module exists

`ipai_finance_gl` captures the D365 Finance "General Ledger and Financial Foundation" parity surface as explicit, queryable records inside Odoo. It exists so that the finance-platform team and stakeholders can see — at a glance — which D365 GL concepts are covered, partially covered, gapped, or out of scope for the current Odoo CE + OCA stack, and link each gap to an ADO task for remediation.

## Business problem

The IPAI platform is displacing D365 Finance for clients migrating to Odoo CE. Stakeholders need a structured parity matrix (not a spreadsheet) to track D365 → Odoo concept mapping across 7 GL wave-01 tasks (chart of accounts, fiscal calendar, financial dimensions, accounting structures, journals, periodic processes, overall GL scope). Without queryable records, the parity state lives in docs only and cannot be filtered, reported, or surfaced in a Pulser agent context.

## CE 18 coverage checked

The following CE 18 models were reviewed as potential native coverage:

| CE Model | Covers |
|---|---|
| `account.account` | Chart of accounts — GL accounts |
| `account.fiscal.year` | Fiscal year/calendar |
| `account.journal` | Financial journals |
| `account.analytic.account` | Analytic dimensions (partial financial dimensions proxy) |
| `account.group` | Account grouping / accounting structures |

CE 18 provides the **runtime** for all GL concepts. It does not provide a parity-tracking data model that maps D365 concepts to Odoo equivalents with status, wave, ADO linkage, and stakeholder-facing views.

## Property-field assessment

Could a property field on `account.account` (or another parent model) solve this requirement?

**No.** Property fields are parent-scoped lightweight metadata for form-level enrichment of existing records (e.g., project-specific task attributes). Parity tracking is metadata *about the mapping between D365 and Odoo* — it is not scoped to a single parent record and has no natural parent model in CE. It requires its own queryable table with status, wave, ADO task linkage, and category taxonomy. A property field cannot carry cross-model D365→Odoo mapping metadata, cannot have SQL uniqueness constraints, cannot be filtered in list/kanban views, and cannot be linked to ADO tasks.

## OCA 18 same-domain coverage checked

| OCA Repo | Modules Reviewed |
|---|---|
| `OCA/account-financial-reporting` | `account_financial_report` — financial statement reports; no parity tracking |
| `OCA/account-financial-tools` | `account_journal_lock_date`, `account_usability` — usability aids; no parity tracking |
| `OCA/mis-builder` | KPI/MIS reports; no parity tracking |
| `OCA/account-analytic` | Analytic account management; no parity tracking |

None of these modules provide a D365→Odoo concept mapping or parity-status data model.

## Adjacent OCA modules reviewed

No adjacent OCA domains (sales, HR, project, purchase) provide a parity-tracking concept applicable here. Parity tracking is a novel concern specific to ERP migration overlay modules.

## Why CE + property fields + OCA composition was insufficient

CE 18 provides GL runtime. OCA finance modules provide reporting and tooling. Neither provides a queryable parity-matrix data model. Property fields cannot represent cross-model mapping metadata. No upstream equivalent exists in CE, OCA, or adjacent OCA domains. The requirement — stakeholder-reviewable, filterable, ADO-linked parity records with status, wave, and category taxonomy — is genuinely novel.

## Why custom code is justified

The Wave-01 parity matrix (7 GL task scopes, N D365 concepts each) needs:
- Queryable status records (`covered` / `partial` / `gap` / `out_of_scope`) for stakeholder review
- ADO Task linkage (`ado_task_id`) for engineering tracking
- Wave segmentation for phased delivery reporting
- Category taxonomy for grouping by GL domain
- A Pulser-accessible surface for agent-driven parity queries (future M2)

None of these are satisfiable by CE configuration, property fields, or OCA composition alone.

## Module type

**overlay** — adds new models and views; does not override or inherit any `account.*` core models.

## Functional boundaries

**In scope:**
- `ipai.finance.gl.parity` — parity record model
- `ipai.finance.gl.parity.category` — category taxonomy model
- GL parity matrix views (tree, form, search, kanban)
- 7 seed categories from `d365_parity_data.xml`
- Security groups (user read-only, manager CRUD)

**Out of scope:**
- Re-implementing GL behavior (Odoo CE + OCA owns it)
- AP/AR parity (separate modules: `ipai_finance_ap`, `ipai_finance_ar`)
- Asset leasing parity (`ipai_asset_leasing` candidate)
- Tax/BIR parity (`ipai_bir_tax`)
- Automated sync from `ssot/benchmarks/parity_matrix.yaml` (M2 scope)

## Extension points used

None. This module adds new models only. It does not use `_inherit` on any existing model, override any view, or hook any CRUD method.

## Blast radius

**Low.** Additive only. Uninstalling this module leaves no orphaned references in `account.*` or any other CE/OCA model. No schema changes to existing tables.

## Upgrade risk

**Low.** Initial release (18.0.1.0.0). No existing schema to migrate. OCA dependency modules (`account_financial_report`, `account_journal_lock_date`, `mis_builder`) must be installed and compatible with Odoo 18.0 before this module can be installed.

## Owner

- Primary: finance-platform team
- Backup: odoo-platform team
- ADO: Epic #523 D365 Finance Parity

## Retirement / replacement criteria

When D365 Finance GL parity reaches ≥80% `covered` status across all Wave-01 parity records, this module can be marked deprecated and the parity matrix moved to docs-only (`ssot/benchmarks/parity_matrix.yaml`). Retirement requires a deliberate deprecation PR reviewed by the finance-platform team lead.
