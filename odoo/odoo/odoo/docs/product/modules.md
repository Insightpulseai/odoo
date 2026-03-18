# Modules

Overview of IPAI custom modules and OCA community addons for Odoo 19 CE.

## Module Philosophy

```
Config -> OCA -> Delta (ipai_*)
```

1. **Config**: Built-in Odoo CE configuration first
2. **OCA**: Vetted community modules second
3. **Delta**: Custom `ipai_*` only for truly custom needs

## IPAI Modules by Domain

### Finance / PPM

| Module | Version | Description |
|--------|---------|-------------|
| `ipai_finance_ppm` | 19.0 | Project Portfolio Management (Clarity parity) |
| `ipai_finance_ppm_umbrella` | 19.0.1.1.0 | Full seed data: 9 employees, 22 BIR forms, 36 tasks, RACI |
| `ipai_finance_ppm_golive` | 19.0 | Go-live checklist (60+ items, CFO sign-off) |
| `ipai_finance_closing` | 19.0 | SAP AFC-style month-end closing templates |
| `ipai_month_end` | 19.0 | Month-end automation with PH holiday awareness |
| `ipai_bir_tax_compliance` | 19.0 | BIR tax compliance (36 eBIRForms) |

### AI / Agents

| Module | Version | Description |
|--------|---------|-------------|
| `ipai_ai_agent_builder` | 19.0.1.0.0 | AI agents with topics, tools, RAG (Joule parity) |
| `ipai_ai_rag` | 19.0 | RAG pipeline for knowledge retrieval |
| `ipai_ai_tools` | 19.0 | AI tools integration |
| `ipai_ask_ai` | 19.0 | ChatGPT/Gemini provider toggles |
| `ipai_ask_ai_chatter` | 19.0 | Headless AI chatter integration |

### OCR / Documents

| Module | Version | Description |
|--------|---------|-------------|
| `ipai_ocr_gateway` | 19.0.1.0.0 | Multi-provider OCR (Tesseract, GCV, Azure) |

### Platform / Workflow

| Module | Version | Description |
|--------|---------|-------------|
| `ipai_platform_approvals` | 19.0 | Approval workflow system |
| `ipai_platform_audit` | 19.0 | Audit trail logging |
| `ipai_platform_permissions` | 19.0 | Permission management |
| `ipai_platform_workflow` | 19.0 | Workflow engine |

### Integrations

| Module | Version | Description |
|--------|---------|-------------|
| `ipai_ops_mirror` | 19.0 | Supabase SSOT sync (read-only mirror) |
| `ipai_superset_connector` | 19.0 | Apache Superset BI integration |
| `ipai_sms_gateway` | 19.0 | SMS gateway |

### Theme / UI

| Module | Version | Description |
|--------|---------|-------------|
| `ipai_theme_tbwa` | 19.0 | TBWA backend theme |
| `ipai_theme_tbwa_backend` | 19.0 | Consolidated backend theme |

## OCA Modules (19.0 Available)

| Module | Repository | Version |
|--------|-----------|---------|
| `account_financial_report` | OCA/account-financial-reporting | 19.0.0.0.2 |
| `account_tax_balance` | OCA/account-financial-reporting | 19.0.1.0.2 |
| `partner_statement` | OCA/account-financial-reporting | 19.0.1.0.0 |

## OCA Submodules (18.0 branch, tracked)

| Repository | Path | Purpose |
|-----------|------|---------|
| `reporting-engine` | external-src/ | Report generation |
| `account-closing` | external-src/ | Period closing |
| `project` | external-src/ | Project extensions |
| `hr-expense` | external-src/ | Expense extensions |
| `purchase-workflow` | external-src/ | Purchase workflows |
| `maintenance` | external-src/ | Maintenance management |
| `dms` | external-src/ | Document management |
| `calendar` | external-src/ | Calendar extensions |
| `web` | external-src/ | Web UI enhancements |
| `account-invoicing` | external-src/ | Invoice extensions |
| `account-financial-reporting` | external-src/ | Financial reports |
| `account-financial-tools` | external-src/ | Financial tools |
| `contract` | external-src/ | Contract management |
| `server-tools` | external-src/ | Server utilities |

## Installing Modules

### Via Docker

```bash
# Install specific module
docker compose exec odoo-core odoo -d odoo -i ipai_finance_ppm --stop-after-init

# Update module
docker compose exec odoo-core odoo -d odoo -u ipai_finance_ppm --stop-after-init

# Install Finance PPM full stack
docker compose exec odoo-core odoo -d odoo \
  -i ipai_finance_ppm,ipai_finance_ppm_umbrella,ipai_finance_ppm_golive,ipai_month_end,ipai_bir_tax_compliance \
  --stop-after-init
```

### Via Script

```bash
# Deploy all IPAI modules
./scripts/deploy-odoo-modules.sh
```

## Module Development

### Naming Convention

```
ipai_<domain>_<feature>
```

Examples: `ipai_finance_ppm`, `ipai_ai_tools`, `ipai_auth_oidc`

### Module Manifest (19.0)

```python
{
    'name': 'IPAI My Module',
    'version': '19.0.1.0.0',
    'category': 'IPAI',
    'summary': 'Module description',
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.com',
    'license': 'LGPL-3',
    'depends': ['base'],
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
docker compose exec odoo-core odoo -d odoo --test-enable -i ipai_my_module --stop-after-init

# Run specific test
docker compose exec odoo-core odoo -d odoo --test-tags ipai_my_module --stop-after-init
```
