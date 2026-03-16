# Canonical Structure & Namespace Map

**Last Updated**: 2026-01-08
**Purpose**: Single source of truth for all naming conventions, module structure, and namespace rules

---

## 1. Module Naming Rules

### Technical Name Convention

**MUST follow**:
- Pattern: `ipai_<domain>_<feature>` (snake_case only)
- No dots, hyphens, or spaces in technical names
- No uppercase letters
- Maximum length: 64 characters

**Domain Prefixes** (first segment after `ipai_`):
- `finance_*` - Financial operations, BIR compliance, month-end closing
- `platform_*` - Platform services, themes, core infrastructure
- `ai_*` - AI/ML features, agents, prompts, providers
- `workspace_*` - Core workspace functionality
- `dev_studio_*` - Studio and developer tools
- `web_*` - Web/UI components, themes
- `theme_*` - UI themes (alternative to web_theme_*)
- `industry_*` - Industry-specific customizations
- `project_*` - Project management features
- `marketing_*` - Marketing automation
- `ask_*` - AI assistant features

### Manifest Conventions

Every module MUST have:
```python
{
    'name': 'Human Readable Name',
    'version': '18.0.1.0.0',  # Odoo 18 compatible
    'category': 'Tools',  # Standard Odoo category
    'license': 'LGPL-3',
    'depends': ['base'],  # Explicit dependencies
    'data': [],  # XML/CSV data files
    'assets': {},  # Asset bundle definitions
    'installable': True,
    'application': False,  # True only for top-level apps
    'auto_install': False,
}
```

---

## 2. View Conventions (Odoo 18)

### XML View Elements

**Odoo 18 Canonical Syntax**:
```xml
<!-- List view (formerly tree) -->
<list string="Items">
    <field name="name"/>
</list>

<!-- Actions -->
<record id="action_items" model="ir.actions.act_window">
    <field name="view_mode">list,form</field>  <!-- NOT tree,form -->
</record>
```

**BANNED (Odoo 17 syntax)**:
```xml
<tree>  <!-- Use <list> instead -->
<field name="view_mode">tree,form</field>  <!-- Use list,form -->
```

### View Inheritance

```xml
<record id="view_inherited" model="ir.ui.view">
    <field name="name">module.model.view.inherited</field>
    <field name="model">model.name</field>
    <field name="inherit_id" ref="base.view_id"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='field']" position="after">
            <!-- Inheritance content -->
        </xpath>
    </field>
</record>
```

---

## 3. Asset Structure

### File Organization

```
<module>/
├── static/
│   └── src/
│       ├── js/           # JavaScript/OWL components
│       ├── xml/          # QWeb templates
│       └── scss/         # Stylesheets
└── __manifest__.py       # Asset bundle definitions
```

### Asset Bundle Registration

**ONLY in `__manifest__.py`**:
```python
'assets': {
    'web.assets_backend': [
        'ipai_module/static/src/js/**/*',
        'ipai_module/static/src/xml/**/*',
        'ipai_module/static/src/scss/**/*',
    ],
    'web.assets_frontend': [
        # Frontend-specific assets
    ],
}
```

**BANNED**:
- Inline `<link>` or `<script>` tags in XML views
- Assets outside `static/src/`
- Unregistered asset files

### AI Copilot UI Isolation

**Canonical modules**:
- `ipai_ask_ai` - Core AI assistant logic
- `ipai_ask_ai_chatter` - Chatter integration
- `ipai_platform_theme` - Design tokens and theme variables

**Rules**:
- All AI UI components MUST be in `ipai_ask_ai` or `ipai_ask_ai_chatter`
- Design tokens MUST be centralized in `ipai_platform_theme`
- No scattered UI token definitions across modules

---

## 4. Database Namespaces

### Scout Platform (ETL/Analytics)

**Canonical schemas**:
```sql
-- Bronze layer (raw ingestion)
scout.bronze_transactions
scout.bronze_invoices
scout.bronze_expenses

-- Silver layer (cleaned/validated)
scout.silver_transactions
scout.silver_invoices

-- Gold layer (business logic applied)
scout.gold_transactions
scout.gold_invoices

-- Platinum layer (aggregated/enriched)
scout.platinum_kpis
scout.platinum_dashboards

-- Deep research (AI/ML features)
scout.deep_research_insights
scout.deep_research_embeddings
```

**Exposure rules**:
- Bronze/Silver: Internal only (ETL processes)
- Gold/Platinum: Exposed via Odoo models and APIs
- Deep Research: Exposed via AI assistant APIs

### Odoo Database

**Standard Odoo schema**: `public` (no custom schema prefixes unless required for isolation)

**Naming conventions**:
- Models: `model.name` (snake_case with dots)
- Tables: Odoo auto-generates (e.g., `model_name` → `model_name` table)
- Foreign keys: `<related_model>_id`
- Many2many: `<model1>_<model2>_rel`

---

## 5. Runtime Identifiers

### Docker Containers

**Canonical names** (from docker-compose.yml):
```yaml
odoo-prod:        # Main Odoo service
  image: odoo:18
  volumes:
    - odoo-web-data:/var/lib/odoo

postgres-prod:    # PostgreSQL database
  image: postgres:16
  volumes:
    - postgres-data:/var/lib/postgresql/data

nginx-prod:       # Reverse proxy
  image: nginx:alpine

n8n-prod:         # Workflow automation
superset-prod:    # BI dashboards
```

**Volume naming**:
- `odoo-web-data` - Odoo filestore (MUST be mounted at `/var/lib/odoo`)
- `postgres-data` - PostgreSQL data directory
- `nginx-conf` - Nginx configuration
- `nginx-certs` - SSL certificates (Let's Encrypt)

### Environment Variables

**Canonical env vars**:
```bash
# Odoo
DB_HOST=postgres
DB_PORT=5432
DB_USER=odoo
DB_PASSWORD=<secret>
ODOO_DB=odoo

# PostgreSQL
POSTGRES_USER=odoo
POSTGRES_PASSWORD=<secret>
POSTGRES_DB=odoo

# Supabase (external integrations only)
SUPABASE_PROJECT_REF=spdtwktxdalcfigzeqrz
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_ANON_KEY=<secret>
SUPABASE_SERVICE_ROLE_KEY=<secret>
```

---

## 6. Canonical Module List & Install Order

### Install Profiles

**Complete Documentation**: See `docs/ipai/PROFILES.md`

#### Profile: `finance_prod` (Production - 10 modules)
Minimal production finance operations with BIR compliance.

**Platform** (2): `ipai_platform_theme`, `ipai_approvals`

**Finance** (4): `ipai_finance_ppm`, `ipai_ppm_monthly_close`, `ipai_finance_ppm_closing`, `ipai_finance_bir_compliance`

**Integrations** (2): `ipai_superset_connector`, `ipai_ocr_expense`

**AI** (1): `ipai_ask_ai`

**Theme** (1): `ipai_theme_tbwa_backend`

#### Profile: `workos_experimental` (Development)
**Status**: ⚠️ **NOT AVAILABLE** - WorkOS modules don't exist in repository yet.

All 9 planned WorkOS modules (`ipai_workos_*`) are missing from `addons/ipai/`. This profile cannot be created until WorkOS modules are implemented.

### Core Dependencies (Install Order)

**Tier 0 - Odoo Core**:
- `base`, `web`, `mail`, `bus`, `web_tour`, `account`, `sale_management`, `project`, `hr`

**Tier 1 - OCA Foundation**:
- `remove_odoo_enterprise` - CE branding cleanup (required)
- `disable_odoo_online` - Remove odoo.com integration (required)
- `server_environment` - Multi-environment config
- `base_user_role` - Advanced permissions

**Tier 2 - IPAI Platform Core**:
- `ipai_platform_theme` - Design tokens (centralized)
- `ipai_approvals` - Approval workflows for finance operations

**Tier 3 - IPAI Finance** (install after Tier 2):
- `ipai_finance_ppm` - Finance PPM dashboard
- `ipai_ppm_monthly_close` - Monthly close scheduler
- `ipai_finance_ppm_closing` - Closing task generator (canonical)
- `ipai_finance_bir_compliance` - BIR tax filing (canonical)

**Tier 4 - IPAI Integrations**:
- `ipai_superset_connector` - Apache Superset BI
- `ipai_ocr_expense` - OCR expense processing

**Tier 5 - IPAI AI Layer**:
- `ipai_ask_ai` - AI chat interface
- `ipai_ask_ai_chatter` - Chatter integration (optional)

**Tier 6 - IPAI Theme** (install LAST):
- `ipai_theme_tbwa_backend` - TBWA corporate theme

### Module Dependency Rules

1. **No circular dependencies** - Use dependency graph validation
2. **Explicit depends** - Never rely on auto-install
3. **Minimal dependencies** - Only declare direct dependencies
4. **OCA before IPAI** - Install OCA modules before custom modules
5. **Base before workspace** - `ipai_dev_studio_base` → `ipai_workspace_core` → others

---

## 7. Asset Bundle Ownership

### Core Bundles

**`web.assets_backend`**:
- Owner: Odoo core `web` module
- Extensions: `ipai_platform_theme` (tokens only)
- Per-feature: Each module contributes its own backend assets

**`web.assets_frontend`**:
- Owner: Odoo core `website` module
- Extensions: `ipai_platform_theme` (tokens only)
- Per-feature: Each module contributes its own frontend assets

**`web.assets_qweb`**:
- Owner: Odoo core `web` module
- Extensions: Per-module QWeb templates

### Custom Bundles

**`ipai_platform_theme.assets_tokens`**:
- Owner: `ipai_platform_theme`
- Purpose: Centralized design tokens (colors, spacing, typography)
- Loaded: Before all other IPAI modules

**`ipai_ask_ai.assets_backend`**:
- Owner: `ipai_ask_ai`
- Purpose: AI assistant UI components
- Dependencies: `ipai_platform_theme.assets_tokens`

---

## 8. Forbidden Patterns

### Module Level

❌ **Dotted technical names**: `ipai_module.backup`
✅ **Use**: `ipai_module_backup`

❌ **Non-prefixed custom modules**: `custom_expense`
✅ **Use**: `ipai_expense`

❌ **Umbrella modules**: `ipai_all_features`
✅ **Use**: Separate modules with clear responsibilities

### View Level

❌ **`<tree>` tag**: `<tree string="Items">`
✅ **Use**: `<list string="Items">`

❌ **`view_mode="tree,form"`**
✅ **Use**: `view_mode="list,form"`

### Asset Level

❌ **Assets outside `static/src/`**: `static/js/script.js`
✅ **Use**: `static/src/js/script.js`

❌ **Inline `<script>` in views**
✅ **Use**: Register in `__manifest__.py` assets

❌ **Scattered design tokens**: Each module defines colors
✅ **Use**: `ipai_platform_theme` centralizes tokens

---

## 9. Verification Commands

### Module Name Validation
```bash
# Find invalid module names (dots, uppercase, non-ipai)
python scripts/canonical_audit.py --check modules
```

### View Syntax Validation
```bash
# Find <tree> usage and view_mode="tree"
python scripts/canonical_audit.py --check views
```

### Asset Structure Validation
```bash
# Find unregistered assets and assets outside static/src/
python scripts/canonical_audit.py --check assets
```

### Full Canonical Audit
```bash
# Run all checks
python scripts/canonical_audit.py --all
```

---

## 10. Migration Path (Legacy → Canonical)

### Step 1: Rename Invalid Modules
```bash
# Example: ipai_module.backup → ipai_module_backup
mv addons/ipai/ipai_module.backup addons/ipai/ipai_module_backup
# Update all references (see CANONICAL_LINT.md)
```

### Step 2: Update Views (tree → list)
```bash
# Automatic replacement
python scripts/canonical_audit.py --fix views
```

### Step 3: Consolidate Design Tokens
```bash
# Move scattered tokens to ipai_platform_theme
python scripts/canonical_audit.py --fix tokens
```

### Step 4: Validate
```bash
# Ensure all checks pass
python scripts/canonical_audit.py --all --strict
```

---

**Status**: ✅ Canonical structure enforced via CI gate
**CI Workflow**: `.github/workflows/canonical-gate.yml`
**Next Review**: 2026-02-01
