# Odoo Platform Details

> **Purpose**: Odoo CE + OCA + IPAI architecture for LLM agents.
> **Version**: Odoo 18.0 Community Edition
> **Constraint**: CE + OCA only (no Enterprise modules)

---

## Platform Composition

```
Odoo 18 CE (Core)
    └── OCA Addons (Community vetted)
        └── IPAI Modules (Custom extensions)
            └── ipai_enterprise_bridge (Base layer)
                ├── ipai_scout_bundle (Retail vertical)
                └── ipai_ces_bundle (Creative services vertical)
```

---

## Module Architecture

### Canonical Modules (Install These)

| Module | Role | Dependencies |
|--------|------|--------------|
| `ipai_enterprise_bridge` | Base: config, approvals, AI glue | `base`, `account`, `project` |
| `ipai_scout_bundle` | Retail: POS, inventory, sales | `ipai_enterprise_bridge` |
| `ipai_ces_bundle` | Creative: projects, timesheets | `ipai_enterprise_bridge` |

### Feature Modules (117 total)

Organized by domain:

| Domain | Prefix | Examples |
|--------|--------|----------|
| Finance | `ipai_finance_*` | `ipai_finance_ppm`, `ipai_finance_month_end` |
| BIR Compliance | `ipai_bir_*` | `ipai_bir_tax_compliance` |
| Expense | `ipai_expense_*` | `ipai_expense`, `ipai_expense_ocr` |
| Equipment | `ipai_equipment` | Cheqroom-style booking |
| AI | `ipai_ai_*` | `ipai_ai_core`, `ipai_ai_agents` |
| Branding | `ipai_ce_*` | `ipai_ce_cleaner`, `ipai_ce_branding` |
| WorkOS | `ipai_workos_*` | Notion-like workspace features |

---

## Database Schema

### Production Database
- **Host**: DigitalOcean Managed Postgres
- **Cluster**: `odoo-db-sgp1`
- **Database**: `odoo_core`
- **Port**: 25060
- **SSL**: Required

### Key Tables (from canonical DBML)

| Table | Purpose |
|-------|---------|
| `res_partner` | Contacts, companies |
| `res_company` | Multi-company config |
| `account_move` | Invoices, journal entries |
| `account_move_line` | Line items |
| `project_project` | Projects |
| `project_task` | Tasks |
| `hr_employee` | Employees |
| `hr_expense` | Expense reports |

### IPAI Extension Tables

| Table | Module | Purpose |
|-------|--------|---------|
| `ipai_ppm_program` | `ipai_finance_ppm` | PPM programs |
| `ipai_ppm_result` | `ipai_finance_ppm` | Logframe results |
| `ipai_ppm_indicator` | `ipai_finance_ppm` | KPI indicators |
| `ipai_equity_tag` | `ipai_enterprise_bridge` | ESG/equity tags |
| `ipai_bir_schedule` | `ipai_bir_*` | BIR form schedules |
| `ipai_ai_trace` | `ipai_ai_core` | AI action audit |

---

## Inheritance Patterns

### Extension Inheritance (`_inherit`)
Most common. Fields merge into base table.

```python
class AccountMove(models.Model):
    _inherit = 'account.move'
    ipai_program_id = fields.Many2one('ipai.ppm_program')
```

### Delegated Inheritance (`_inherits`)
Only 1 case: `attachment.queue` → `ir.attachment`

---

## OCA Dependencies

Key OCA 18.0 modules used:

| Category | Modules |
|----------|---------|
| Queue | `queue_job` |
| Server | `server_environment` |
| Accounting | `account_financial_report_*`, `account_fiscal_period` |
| Reporting | `report_xlsx` |
| Partner | `partner_statement` |

---

## Installation Commands

```bash
# Install canonical stack
docker compose exec -T odoo odoo -d odoo_dev -i ipai_enterprise_bridge --stop-after-init
docker compose exec -T odoo odoo -d odoo_dev -i ipai_scout_bundle --stop-after-init
docker compose exec -T odoo odoo -d odoo_dev -i ipai_ces_bundle --stop-after-init

# Verify installation
docker compose exec -T db psql -U odoo -d odoo_dev -c "
SELECT name, state FROM ir_module_module
WHERE name IN ('ipai_enterprise_bridge','ipai_scout_bundle','ipai_ces_bundle')
ORDER BY name;"
```

---

## Canonical Data Model Artifacts

Located in `docs/data-model/`:

| File | Format | Purpose |
|------|--------|---------|
| `ODOO_CANONICAL_SCHEMA.dbml` | DBML | Schema for dbdiagram.io |
| `ODOO_MODEL_INDEX.json` | JSON | 357 models, 2847 fields |
| `ODOO_ORM_MAP.md` | Markdown | ORM field mapping |
| `ODOO_MODULE_DELTAS.md` | Markdown | Per-module changes |
| `ODOO_ERD.mmd` | Mermaid | ER diagram |

---

## Shadow Schema Strategy

Odoo data is mirrored to Supabase for analytics/RAG:

| Odoo Table | Supabase Shadow |
|------------|-----------------|
| `res_partner` | `odoo_shadow.res_partner` |
| `account_move` | `odoo_shadow.account_move` |
| `project_project` | `odoo_shadow.project_project` |

**Sync Rules**:
- Incremental by `write_date`
- Read-only in Supabase
- Tracking columns: `_odoo_write_date`, `_synced_at`, `_sync_hash`

---

## API Access

### XML-RPC (Native)
```python
import xmlrpc.client
common = xmlrpc.client.ServerProxy('https://erp.insightpulseai.net/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
```

### JSON-RPC (Recommended)
```bash
curl -X POST https://erp.insightpulseai.net/web/session/authenticate \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{"db":"odoo_core","login":"...","password":"..."}}'
```

---

## Environment Configs

### Dev Sandbox
```
Location: sandbox/dev/
Compose: docker-compose.yml
Database: odoo_dev
Port: 8069
```

### Production
```
Droplet: odoo-erp-prod
Database: odoo_core (DO Managed)
URL: https://erp.insightpulseai.net
```

---

## Caveats for LLMs

1. **CE Only** - No Enterprise modules, no odoo.com IAP
2. **OCA First** - Prefer OCA modules over custom IPAI where available
3. **Module Dependencies** - Always install `ipai_enterprise_bridge` first
4. **Database Access** - Use shadow tables in Supabase, not direct Odoo DB
5. **Write Operations** - Go through Odoo ORM/API, never direct SQL
