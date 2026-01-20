# Modules

Overview of IPAI custom modules and OCA community addons.

## Module Hierarchy

```
ipai_dev_studio_base           # Base dependencies (install first)
    └── ipai_workspace_core    # Core workspace functionality
        └── ipai_ce_branding   # CE branding layer
            ├── ipai_ai_core   # AI core framework
            │   ├── ipai_ai_agents     # Agent system
            │   └── ipai_ai_prompts    # Prompt management
            ├── ipai_finance_ppm       # Finance PPM
            │   └── ipai_finance_month_end
            └── [other modules]
```

## IPAI Modules by Domain

### AI / Agents

| Module | Description |
|--------|-------------|
| `ipai_ai_core` | AI core framework |
| `ipai_ai_agents` | Agent system |
| `ipai_ai_prompts` | Prompt management |
| `ipai_agent_core` | Core agent framework |

### Finance

| Module | Description |
|--------|-------------|
| `ipai_finance_ppm` | Project Portfolio Management |
| `ipai_finance_bir_compliance` | BIR tax compliance |
| `ipai_finance_month_end` | Month-end close workflows |

### Platform

| Module | Description |
|--------|-------------|
| `ipai_platform_workflow` | Workflow automation |
| `ipai_platform_audit` | Audit trail |
| `ipai_platform_approvals` | Approval workflows |

### Workspace

| Module | Description |
|--------|-------------|
| `ipai_workspace_core` | Core workspace functionality |
| `ipai_dev_studio_base` | Development studio base |

### WorkOS

| Module | Description |
|--------|-------------|
| `ipai_workos_core` | WorkOS core |
| `ipai_workos_blocks` | Block-based UI |
| `ipai_workos_canvas` | Canvas interface |

### Integrations

| Module | Description |
|--------|-------------|
| `ipai_n8n_connector` | n8n workflow integration |
| `ipai_mattermost_connector` | Mattermost integration |
| `ipai_superset_connector` | Superset BI integration |

### Theme / UI

| Module | Description |
|--------|-------------|
| `ipai_theme_tbwa_backend` | TBWA backend theme |
| `ipai_ui_brand_tokens` | Brand design tokens |
| `ipai_ce_branding` | CE branding layer |

## OCA Modules

The repository includes OCA (Odoo Community Association) modules for standard functionality:

```
addons/OCA/
├── account-financial-reporting/
├── account-reconcile/
├── bank-payment/
├── reporting-engine/
├── server-tools/
├── web/
└── ...
```

### Key OCA Repositories

| Repository | Purpose |
|------------|---------|
| `server-tools` | Server utilities |
| `web` | Web UI enhancements |
| `account-financial-reporting` | Financial reports |
| `reporting-engine` | Report generation |

## Installing Modules

### Via Docker

```bash
# Install specific module
docker compose exec odoo-core odoo -d odoo_core -i ipai_finance_ppm --stop-after-init

# Update module
docker compose exec odoo-core odoo -d odoo_core -u ipai_finance_ppm --stop-after-init
```

### Via Script

```bash
# Deploy all IPAI modules
./scripts/deploy-odoo-modules.sh
```

## Module Development

### Create New Module

```bash
# Use mrbob scaffolding
mrbob bobtemplates.odoo:addon
# Move to addons/ipai/
```

### Module Manifest

```python
# __manifest__.py
{
    'name': 'IPAI My Module',
    'version': '18.0.1.0.0',
    'category': 'IPAI',
    'summary': 'My module description',
    'author': 'InsightPulse AI',
    'website': 'https://github.com/jgtolentino/odoo-ce',
    'license': 'LGPL-3',
    'depends': ['ipai_dev_studio_base'],
    'data': [
        'security/ir.model.access.csv',
        'views/my_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

## Testing Modules

```bash
# Run module tests
docker compose exec odoo-core odoo -d odoo_core --test-enable -i ipai_my_module --stop-after-init

# Run specific test
docker compose exec odoo-core odoo -d odoo_core --test-tags ipai_my_module --stop-after-init
```
