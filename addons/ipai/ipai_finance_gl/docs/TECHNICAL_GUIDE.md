# TECHNICAL_GUIDE.md — ipai_finance_gl

## Architecture

Three layers:

1. **Model layer** — two new models (`ipai.finance.gl.parity`, `ipai.finance.gl.parity.category`) with no inheritance from existing CE models.
2. **Parity matrix data** — seed XML (`data/d365_parity_data.xml`) populates 7 `ipai.finance.gl.parity.category` records representing the Wave-01 GL taxonomy.
3. **View layer** — tree / form / search / kanban views for the parity model, plus a top-level menu under Finance → Configuration.

No inherited models. No CRUD overrides. No webhooks or background jobs in v1.

## Models extended

None. This module adds new models only and does not `_inherit` any existing CE or OCA model.

## Fields added

### `ipai.finance.gl.parity`

| Field | Type | Purpose |
|---|---|---|
| `name` | `Char` (computed, store=True) | Display name, format: `[GL] <d365_concept>` |
| `d365_concept` | `Char` (required) | D365 Finance concept name (e.g., "Main Account") |
| `d365_module` | `Char` | D365 module owning this concept (e.g., "General Ledger") |
| `d365_doc_url` | `Char` | URL to Microsoft Learn doc for this concept |
| `category_id` | `Many2one('ipai.finance.gl.parity.category')` | GL taxonomy category |
| `odoo_module` | `Char` | Odoo CE/OCA module providing coverage (e.g., `account`) |
| `odoo_model` | `Char` | Odoo model providing coverage (e.g., `account.account`) |
| `odoo_view_ref` | `Char` | XML ID of the Odoo form view for this model (used in `action_open_odoo_model`) |
| `status` | `Selection` | Parity status: `covered` / `partial` / `gap` / `out_of_scope` |
| `status_color` | `Integer` (computed) | Odoo color index for kanban/list decoration: covered=10, partial=2, gap=1, out_of_scope=4 |
| `notes` | `Html` | Free-form notes (rich text) |
| `ipai_module_id` | `Many2one('ir.module.module')` | `ipai_*` module bridging this gap (if any) |
| `wave` | `Char` (default `'Wave-01'`) | Delivery wave for phased parity tracking |
| `ado_task_id` | `Char` | Azure DevOps task ID for the remediation work item |
| `active` | `Boolean` (default `True`) | Supports archiving via standard Odoo active pattern |

### `ipai.finance.gl.parity.category`

| Field | Type | Purpose |
|---|---|---|
| `name` | `Char` (required) | Human-readable category name |
| `code` | `Char` (required) | Unique machine key (e.g., `chart_of_accounts`) |
| `description` | `Text` | Optional longer description |
| `sequence` | `Integer` (default `10`) | Display ordering |
| `active` | `Boolean` (default `True`) | Supports archiving |

## Methods overridden

None.

## View inheritance points

None. All views in this module are original (not inheriting from CE or OCA views).

Views defined in `views/d365_parity_views.xml`:
- `ipai_finance_gl_parity_view_tree`
- `ipai_finance_gl_parity_view_form`
- `ipai_finance_gl_parity_view_search`
- `ipai_finance_gl_parity_view_kanban`
- `ipai_finance_gl_parity_category_view_tree`
- `ipai_finance_gl_parity_category_view_form`

## Security model

Two security groups defined in `security/ipai_finance_gl_security.xml`:

| Group XML ID | Name | Permissions |
|---|---|---|
| `group_ipai_finance_gl_user` | GL Parity User | Read parity records and categories |
| `group_ipai_finance_gl_manager` | GL Parity Manager | Full CRUD on parity records and categories |

ACL entries in `security/ir.model.access.csv`:

| Model | User group | R | W | C | D |
|---|---|---|---|---|---|
| `ipai.finance.gl.parity` | GL Parity User | ✓ | | | |
| `ipai.finance.gl.parity` | GL Parity Manager | ✓ | ✓ | ✓ | ✓ |
| `ipai.finance.gl.parity.category` | GL Parity User | ✓ | | | |
| `ipai.finance.gl.parity.category` | GL Parity Manager | ✓ | ✓ | ✓ | ✓ |

## Data files loaded

Load order (from `__manifest__.py`):

1. `security/ipai_finance_gl_security.xml` — group definitions
2. `security/ir.model.access.csv` — ACL entries
3. `data/d365_parity_data.xml` — 7 seed `ipai.finance.gl.parity.category` records:
   - `chart_of_accounts` — Chart of Accounts & Main Accounts
   - `fiscal_calendar` — Fiscal Calendar & Periods
   - `financial_dimensions` — Financial Dimensions & Dimension Sets
   - `accounting_structure` — Accounting Structures & Rules
   - `financial_journal` — Financial Journals
   - `periodic_process` — Periodic Financial Processes
   - `gl_overall` — GL Overall Scope
4. `views/d365_parity_views.xml` — all views
5. `views/menu.xml` — Finance → Configuration → D365 Parity menu items

## Jobs / cron / queues / webhooks

None in v1. M2 may add a cron job to sync parity status from `ssot/benchmarks/parity_matrix.yaml`.

## External integrations

None in v1. The `ado_task_id` field stores an ADO task ID as a plain `Char` — no live API call to Azure DevOps is made. Future versions may add a clickable URL or a sync action via Azure DevOps MCP.

## Test strategy

Three test files in `tests/`:

| File | Coverage |
|---|---|
| `test_parity_category.py` | Category model: defaults, unique code constraint, archiving, ordering |
| `test_parity_record.py` | Parity model: gap/covered validation constraint, name compute, status_color compute, unique (d365_concept, wave) SQL constraint, `action_open_odoo_model()` |
| `test_seed_data.py` | Seed data: 7 categories exist post-install with required fields populated |

All test classes are tagged `@tagged('post_install', '-at_install')` and use `TransactionCase` for proper rollback isolation. Run with:

```bash
odoo-bin -d test_ipai_finance_gl -i ipai_finance_gl --test-enable --stop-after-init
```

## Upgrade / rollback notes

- **Upgrade**: No existing schema to migrate. Safe to install fresh.
- **Rollback / uninstall**: Uninstalling drops `ipai_finance_gl_parity` and `ipai_finance_gl_parity_category` tables. No foreign keys exist on any CE/OCA table pointing to these models. Uninstall is safe with no orphaned references.
- OCA dependency modules must remain installed; uninstalling them while `ipai_finance_gl` is installed will fail the manifest dependency check.

## Known limitations and failure modes

- **GL scope only**: v1 covers only General Ledger. AP, AR, asset, and tax parity need separate `ipai_finance_*` modules.
- **Manual data entry**: Parity records are entered manually. No automated sync from `ssot/benchmarks/parity_matrix.yaml` until M2.
- **No drill-through from gap records**: `action_open_odoo_model()` only works when `odoo_view_ref` is explicitly set; gap records (no CE coverage) will always return falsy.
- **`d365_concept` + `wave` uniqueness is enforced at DB level**: Duplicate records attempted via import will produce an `IntegrityError` rather than a user-friendly `ValidationError`. A `@api.constrains` wrapper can be added in M2 if needed.
- **`ipai_module_id` is advisory**: The field links to `ir.module.module` for discoverability but no install/uninstall side-effects are triggered.
