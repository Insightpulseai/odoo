# IPAI Module Deprecation Plan

> **Purpose**: Clean up temporary/placeholder modules now that EE parity is achieved via CE + OCA + ipai_enterprise_bridge
> **Target**: Reduce 30+ IPAI modules to ~14 canonical modules
> **Timeline**: 4-week phased rollout

## Executive Summary

With EE parity achieved through CE 19 + OCA + `ipai_enterprise_bridge`, we can now deprecate:
- **13** placeholder AI modules (TODO scaffolds)
- **8** duplicate theme/design system modules
- **4** placeholder finance/document modules
- **2** prototype/alpha modules
- **1** already-deprecated module

**Total: 28 modules → Archive or Consolidate**

## Guiding Principles

1. **No data loss**: Migrate data before removing models
2. **No silent drops**: Mark deprecated, then remove in future version
3. **No EE impersonation**: Keep `ipai_*` namespace, don't rename to `odoo_*` or EE module names
4. **One-way migration**: Old → New only, no rollback paths for deprecated modules

## Canonical Stack (POST-DEPRECATION)

```
Odoo CE 19.0
├── OCA Modules (22 repos from oca.lock.ce19.json)
│   ├── account-reconcile (bank reconciliation)
│   ├── account-financial-reporting (financial reports)
│   ├── account-financial-tools (asset management)
│   ├── helpdesk (helpdesk_mgmt)
│   ├── dms (document management)
│   └── ... (17 more)
│
└── IPAI Modules (14 canonical)
    ├── ipai_enterprise_bridge     # EE parity glue layer
    ├── ipai_foundation            # Base dependencies
    ├── ipai_helpdesk              # EE helpdesk replacement
    ├── ipai_hr_payroll_ph         # Philippines payroll
    ├── ipai_finance_ppm           # Finance/PPM workflows
    ├── ipai_finance_workflow      # Month-end close
    ├── ipai_expense_ocr           # Expense OCR
    ├── ipai_design_system_apps_sdk # Design tokens (SSOT)
    ├── ipai_theme_tbwa            # TBWA branding
    ├── ipai_theme_fluent2         # Fluent 2 tokens
    ├── ipai_theme_copilot         # Copilot styling
    ├── ipai_web_icons_fluent      # Icon library
    ├── ipai_vertical_media        # CES vertical
    └── ipai_vertical_retail       # Scout vertical
```

---

## Phase 1: Low-Risk Removals (Week 1)

### Already Deprecated

| Module | Status | Action |
|--------|--------|--------|
| `ipai_theme_tbwa_backend` | `installable: false`, marked deprecated | Archive to `/archive/deprecated/` |

**Manifest already says:**
```python
"summary": "THIS MODULE IS DEPRECATED AND SHOULD NOT BE INSTALLED. Please use ipai_theme_tbwa instead."
```

### Prototype/Alpha Modules

| Module | Status | Action |
|--------|--------|--------|
| `ipai_fluent_web_365_copilot` | `development_status: Alpha` | Move to `/prototypes/` |
| `ipai_aiux_chat` | Scaffold module | Move to `/prototypes/` |

### Commands

```bash
# Archive deprecated theme
mkdir -p archive/deprecated
git mv addons/ipai/ipai_theme_tbwa_backend archive/deprecated/

# Move prototypes
mkdir -p prototypes
git mv addons/ipai/ipai_fluent_web_365_copilot prototypes/
git mv addons/ipai/ipai_aiux_chat prototypes/
git mv addons/ipai/ipai_theme_aiux prototypes/

# Commit
git add -A && git commit -m "chore(ipai): phase 1 - archive deprecated and prototype modules"
```

---

## Phase 2: Placeholder Module Consolidation (Week 2)

### AI Placeholder Modules → ipai_enterprise_bridge

These modules all have the same pattern:
- Single model with `name`, `active`, `company_id`, `notes` fields
- `# TODO: Add specific fields` comment
- No business logic

| Module | Model | Consolidate To |
|--------|-------|----------------|
| `ipai_ai_agent_builder` | `ipai.ai.agent.builder` | `ipai_enterprise_bridge.config_ai` |
| `ipai_ai_automations` | `ipai.ai.automations` | `ipai_enterprise_bridge.config_ai` |
| `ipai_ai_fields` | `ipai.ai.fields` | `ipai_enterprise_bridge.config_ai` |
| `ipai_ai_livechat` | `ipai.ai.livechat` | `ipai_enterprise_bridge.config_ai` |
| `ipai_ai_rag` | `ipai.ai.rag` | `ipai_enterprise_bridge.config_ai` |
| `ipai_ai_tools` | `ipai.ai.tools` | `ipai_enterprise_bridge.config_ai` |

### Business Placeholder Modules → ipai_enterprise_bridge

| Module | Model | Consolidate To |
|--------|-------|----------------|
| `ipai_equity` | `ipai.equity` | `ipai_enterprise_bridge.config_finance` |
| `ipai_esg` | `ipai.esg` | `ipai_enterprise_bridge.config_sustainability` |
| `ipai_esg_social` | `ipai.esg.social` | `ipai_enterprise_bridge.config_sustainability` |
| `ipai_planning_attendance` | `ipai.planning.attendance` | `ipai_enterprise_bridge.config_hr` |
| `ipai_project_templates` | `ipai.project.templates` | `ipai_enterprise_bridge.config_project` |
| `ipai_whatsapp_connector` | `ipai.whatsapp.connector` | `ipai_enterprise_bridge.config_integrations` |
| `ipai_finance_tax_return` | `ipai.finance.tax.return` | `ipai_enterprise_bridge.config_finance` |

### Migration Strategy

1. **Create config models in ipai_enterprise_bridge**:
   ```python
   # addons/ipai/ipai_enterprise_bridge/models/config_ai.py
   class IpaiConfigAI(models.Model):
       _name = 'ipai.config.ai'
       _description = 'AI Configuration (consolidated from placeholder modules)'

       name = fields.Char(required=True)
       category = fields.Selection([
           ('agent_builder', 'Agent Builder'),
           ('automations', 'Automations'),
           ('fields', 'AI Fields'),
           ('livechat', 'Live Chat'),
           ('rag', 'RAG'),
           ('tools', 'AI Tools'),
       ])
       active = fields.Boolean(default=True)
       company_id = fields.Many2one('res.company')
       notes = fields.Text()
       config_json = fields.Text(string="Configuration JSON")
   ```

2. **Add data migration** (post_init_hook):
   ```python
   def migrate_placeholder_modules(cr, registry):
       """Migrate data from placeholder modules to ipai_enterprise_bridge."""
       cr.execute("""
           INSERT INTO ipai_config_ai (name, category, active, company_id, notes)
           SELECT name, 'agent_builder', active, company_id, notes
           FROM ipai_ai_agent_builder
           WHERE NOT EXISTS (
               SELECT 1 FROM ipai_config_ai WHERE name = ipai_ai_agent_builder.name
           )
       """)
       # Repeat for other placeholder tables
   ```

3. **Mark placeholder modules deprecated** (don't remove yet):
   ```python
   # In each placeholder module's __manifest__.py:
   {
       "name": "DEPRECATED: IPAI AI Agent Builder",
       "summary": "DEPRECATED - Migrated to ipai_enterprise_bridge. Do not install.",
       "installable": False,
       "auto_install": False,
   }
   ```

### Commands

```bash
# Update manifests to mark deprecated
for module in ipai_ai_agent_builder ipai_ai_automations ipai_ai_fields \
              ipai_ai_livechat ipai_ai_rag ipai_ai_tools ipai_equity \
              ipai_esg ipai_esg_social ipai_planning_attendance \
              ipai_project_templates ipai_whatsapp_connector ipai_finance_tax_return; do
    echo "Marking $module as deprecated..."
    # Update manifest (script will be created)
done

git add -A && git commit -m "chore(ipai): phase 2 - deprecate placeholder modules, add migration"
```

---

## Phase 3: Theme Architecture Cleanup (Week 3)

### Design System Consolidation

**Problem**: Multiple competing "single source of truth" modules for design tokens.

**Solution**: `ipai_design_system_apps_sdk` becomes the canonical SSOT.

| Module | Action | Reason |
|--------|--------|--------|
| `ipai_design_system_apps_sdk` | **KEEP** | Manifest claims SSOT status |
| `ipai_design_system` | DEPRECATE | Duplicate of apps_sdk |
| `ipai_platform_theme` | DEPRECATE | Superseded by apps_sdk |
| `ipai_ui_brand_tokens` | MERGE into apps_sdk | Duplicate token system |

### Theme Module Consolidation

| Module | Action | Reason |
|--------|--------|--------|
| `ipai_theme_tbwa` | **KEEP** | Primary TBWA branding |
| `ipai_web_theme_tbwa` | DEPRECATE | Duplicate of theme_tbwa |
| `ipai_theme_fluent2` | **KEEP** | Fluent 2 tokens |
| `ipai_web_fluent2` | DEPRECATE | Duplicate of theme_fluent2 |
| `ipai_theme_copilot` | **KEEP** | Copilot styling |
| `ipai_copilot_ui` | MERGE into theme_copilot | Overlapping functionality |
| `ipai_chatgpt_sdk_theme` | ARCHIVE | Move to /prototypes/ |
| `ipai_web_icons_fluent` | **KEEP** | Icon library |

### Dependency Updates

```python
# Before (in various modules):
"depends": ["ipai_platform_theme", "ipai_ui_brand_tokens"]

# After:
"depends": ["ipai_design_system_apps_sdk"]
```

### Migration Script

```python
# scripts/migrate_theme_deps.py
import re
import glob

DEPRECATED_THEMES = [
    'ipai_platform_theme',
    'ipai_design_system',
    'ipai_ui_brand_tokens',
    'ipai_web_theme_tbwa',
    'ipai_web_fluent2',
]
CANONICAL_THEME = 'ipai_design_system_apps_sdk'

for manifest_path in glob.glob('addons/ipai/*/__manifest__.py'):
    with open(manifest_path, 'r') as f:
        content = f.read()

    for dep in DEPRECATED_THEMES:
        if dep in content:
            content = content.replace(f'"{dep}"', f'"{CANONICAL_THEME}"')
            print(f"Updated {manifest_path}: {dep} -> {CANONICAL_THEME}")

    with open(manifest_path, 'w') as f:
        f.write(content)
```

---

## Phase 4: Finance/Document Migration (Week 4)

### Modules to Migrate to OCA

| Module | OCA Replacement | Migration |
|--------|-----------------|-----------|
| `ipai_documents_ai` | `dms` (OCA) + AI bridge | Create `ipai_dms_ai_extension` |
| `ipai_sign` | `sign` (OCA) | Direct replacement |

### Modules to Merge into ipai_helpdesk

| Module | Target | Migration |
|--------|--------|-----------|
| `ipai_helpdesk_refund` | `ipai_helpdesk` | Add `refund_amount` field to ticket model |

### Data Migration

```python
# For ipai_helpdesk_refund → ipai_helpdesk
def migrate_helpdesk_refund(cr, registry):
    """Migrate refund data to helpdesk tickets."""
    cr.execute("""
        ALTER TABLE ipai_helpdesk_ticket
        ADD COLUMN IF NOT EXISTS refund_amount NUMERIC(16,2);

        UPDATE ipai_helpdesk_ticket t
        SET refund_amount = r.amount
        FROM ipai_helpdesk_refund r
        WHERE r.ticket_id = t.id;
    """)
```

---

## Post-Deprecation Verification

### Check No Broken Dependencies

```bash
# Verify all modules can still load
docker exec -it odoo_ce19_ee_parity \
  odoo -d test_db --stop-after-init \
  -i ipai_enterprise_bridge,ipai_helpdesk,ipai_hr_payroll_ph

# Check for missing dependencies
grep -r "depends.*ipai_" addons/ipai/*/\__manifest__.py | \
  grep -E "(ipai_platform_theme|ipai_design_system[^_]|ipai_ui_brand_tokens)"
```

### Verify EE Parity Still Holds

```bash
# Run parity tests
python scripts/test_ee_parity.py --odoo-url http://localhost:8069 --db odoo_ce19

# Verify parity score >= 80%
./scripts/ci/ee_parity_gate.sh
```

### Module Count Verification

```bash
# Before: ~30 ipai modules
find addons/ipai -maxdepth 1 -type d | wc -l

# After: ~14 canonical modules
find addons/ipai -maxdepth 1 -type d -name "ipai_*" | wc -l
```

---

## Rollback Strategy

If any phase causes issues:

1. **Revert git commits** for that phase
2. **Restore archived modules** if data loss occurred:
   ```bash
   git checkout HEAD~1 -- archive/deprecated/ipai_theme_tbwa_backend
   git mv archive/deprecated/ipai_theme_tbwa_backend addons/ipai/
   ```
3. **Re-enable deprecated modules** by setting `installable: True`

---

## Timeline Summary

| Week | Phase | Modules Affected | Risk |
|------|-------|------------------|------|
| 1 | Low-Risk Removals | 4 modules | Low |
| 2 | Placeholder Consolidation | 13 modules | Medium |
| 3 | Theme Cleanup | 8 modules | Medium |
| 4 | Finance/Document Migration | 4 modules | Low |

**Total Duration**: 4 weeks
**Total Modules Deprecated**: 28
**Remaining Canonical Modules**: 14

---

## Appendix: Module Status Matrix

| Module | Category | Status | Action | Phase |
|--------|----------|--------|--------|-------|
| ipai_enterprise_bridge | Core | KEEP | Canonical | - |
| ipai_foundation | Core | KEEP | Canonical | - |
| ipai_helpdesk | Core | KEEP | Canonical | - |
| ipai_hr_payroll_ph | Core | KEEP | Canonical | - |
| ipai_finance_ppm | Core | KEEP | Canonical | - |
| ipai_finance_workflow | Core | KEEP | Canonical | - |
| ipai_expense_ocr | Core | KEEP | Canonical | - |
| ipai_design_system_apps_sdk | Theme | KEEP | SSOT | - |
| ipai_theme_tbwa | Theme | KEEP | Brand | - |
| ipai_theme_fluent2 | Theme | KEEP | Tokens | - |
| ipai_theme_copilot | Theme | KEEP | Styling | - |
| ipai_web_icons_fluent | Theme | KEEP | Icons | - |
| ipai_vertical_media | Vertical | KEEP | Production | - |
| ipai_vertical_retail | Vertical | KEEP | Production | - |
| ipai_theme_tbwa_backend | Theme | DEPRECATED | Archive | 1 |
| ipai_fluent_web_365_copilot | Prototype | ALPHA | Prototype | 1 |
| ipai_aiux_chat | Prototype | SCAFFOLD | Prototype | 1 |
| ipai_theme_aiux | Theme | SCAFFOLD | Prototype | 1 |
| ipai_ai_agent_builder | AI | PLACEHOLDER | Consolidate | 2 |
| ipai_ai_automations | AI | PLACEHOLDER | Consolidate | 2 |
| ipai_ai_fields | AI | PLACEHOLDER | Consolidate | 2 |
| ipai_ai_livechat | AI | PLACEHOLDER | Consolidate | 2 |
| ipai_ai_rag | AI | PLACEHOLDER | Consolidate | 2 |
| ipai_ai_tools | AI | PLACEHOLDER | Consolidate | 2 |
| ipai_equity | Finance | PLACEHOLDER | Consolidate | 2 |
| ipai_esg | ESG | PLACEHOLDER | Consolidate | 2 |
| ipai_esg_social | ESG | PLACEHOLDER | Consolidate | 2 |
| ipai_planning_attendance | HR | PLACEHOLDER | Consolidate | 2 |
| ipai_project_templates | Project | PLACEHOLDER | Consolidate | 2 |
| ipai_whatsapp_connector | Integrations | PLACEHOLDER | Consolidate | 2 |
| ipai_finance_tax_return | Finance | PLACEHOLDER | Consolidate | 2 |
| ipai_design_system | Theme | DUPLICATE | Deprecate | 3 |
| ipai_platform_theme | Theme | DUPLICATE | Deprecate | 3 |
| ipai_ui_brand_tokens | Theme | DUPLICATE | Merge | 3 |
| ipai_web_theme_tbwa | Theme | DUPLICATE | Deprecate | 3 |
| ipai_web_fluent2 | Theme | DUPLICATE | Deprecate | 3 |
| ipai_copilot_ui | Theme | DUPLICATE | Merge | 3 |
| ipai_chatgpt_sdk_theme | Theme | NICHE | Archive | 3 |
| ipai_documents_ai | Documents | PLACEHOLDER | OCA | 4 |
| ipai_sign | Documents | PLACEHOLDER | OCA | 4 |
| ipai_helpdesk_refund | Helpdesk | PLACEHOLDER | Merge | 4 |

---

*Document Version: 1.0.0*
*Created: 2026-01-28*
*Author: Claude Code Agent*
