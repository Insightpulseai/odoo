# EE Parity Complete Installation Manifest

**Generated**: 2026-01-26
**Target**: Odoo 19.0 Full EE Parity
**Total Features**: 40

---

## Installation Summary

| Strategy | Count | Modules |
|----------|-------|---------|
| **OCA** | 11 | 18 OCA modules across 8 repos |
| **ipai_*** | 21 | 17 unique ipai modules |
| **External** | 6 | 6 external service integrations |
| **CE** | 2 | 2 CE core modules |

---

## 1. OCA Modules to Install

### Repository: OCA/account-financial-tools
```bash
# Branch: 19.0
git clone --branch 19.0 --depth 1 https://github.com/OCA/account-financial-tools.git addons/oca/account-financial-tools
```
- `account_asset_management` - Fixed asset lifecycle management

### Repository: OCA/mis-builder
```bash
git clone --branch 19.0 --depth 1 https://github.com/OCA/mis-builder.git addons/oca/mis-builder
```
- `mis_builder` - Management Information System reports
- `mis_builder_budget` - Budget management

### Repository: OCA/account-consolidation
```bash
git clone --branch 19.0 --depth 1 https://github.com/OCA/account-consolidation.git addons/oca/account-consolidation
```
- `account_consolidation` - Multi-company consolidation

### Repository: OCA/account-analytic
```bash
git clone --branch 19.0 --depth 1 https://github.com/OCA/account-analytic.git addons/oca/account-analytic
```
- `analytic_tag_dimension` - Analytic dimensions

### Repository: OCA/dms
```bash
git clone --branch 19.0 --depth 1 https://github.com/OCA/dms.git addons/oca/dms
```
- `dms` - Document Management System
- `dms_field` - DMS field widget

### Repository: OCA/hr
```bash
git clone --branch 19.0 --depth 1 https://github.com/OCA/hr.git addons/oca/hr
```
- `hr_appraisal_survey` - Survey-based appraisals

### Repository: OCA/payroll
```bash
git clone --branch 19.0 --depth 1 https://github.com/OCA/payroll.git addons/oca/payroll
```
- `payroll` - Base payroll
- `payroll_account` - Payroll accounting integration

### Repository: OCA/web
```bash
git clone --branch 19.0 --depth 1 https://github.com/OCA/web.git addons/oca/web
```
- `web_timeline` - Timeline/Gantt view
- `web_widget_many2many_tags_multi_selection` - Enhanced tags widget

### Repository: OCA/project
```bash
git clone --branch 19.0 --depth 1 https://github.com/OCA/project.git addons/oca/project
```
- `project_timeline` - Project timeline view
- `project_forecast_line` - Resource forecasting

### Repository: OCA/manufacture
```bash
git clone --branch 19.0 --depth 1 https://github.com/OCA/manufacture.git addons/oca/manufacture
```
- `quality_control_oca` - Quality control

### Repository: OCA/social
```bash
git clone --branch 19.0 --depth 1 https://github.com/OCA/social.git addons/oca/social
```
- `sms_no_iap` - SMS without Odoo IAP

---

## 2. ipai_* Modules to Create/Install

### P0 - Critical (Must Have)
| Module | Feature | Status |
|--------|---------|--------|
| `ipai_ai_agent_builder` | AI Agents + ChatGPT/Gemini | TO CREATE |
| `ipai_ai_rag` | RAG Pipeline | TO CREATE |
| `ipai_ai_tools` | AI Tool Registry | TO CREATE |
| `ipai_finance_tax_return` | Tax Return Workflow | TO CREATE |
| `ipai_bir_vat` | BIR 2550Q VAT | EXISTS |
| `ipai_bir_alphalist` | BIR Alphalist .DAT | EXISTS |
| `ipai_hr_payroll_ph` | PH Payroll + Pay Runs | EXISTS |

### P1 - High Priority
| Module | Feature | Status |
|--------|---------|--------|
| `ipai_ai_fields` | AI Field Population | TO CREATE |
| `ipai_ai_automations` | AI Server Actions | TO CREATE |
| `ipai_whatsapp_connector` | WhatsApp Integration | TO CREATE |
| `ipai_helpdesk` | Helpdesk + Rotting | EXISTS |
| `ipai_project_templates` | Project Templates | TO CREATE |
| `ipai_planning_attendance` | Planning Analysis | TO CREATE |

### P2 - Medium Priority
| Module | Feature | Status |
|--------|---------|--------|
| `ipai_ai_livechat` | AI Livechat | TO CREATE |
| `ipai_esg` | Carbon Analytics | TO CREATE |
| `ipai_esg_social` | Social Metrics | TO CREATE |
| `ipai_helpdesk_refund` | Gift Card Refunds | TO CREATE |
| `ipai_documents_ai` | Documents AI | TO CREATE |
| `ipai_sign` | Sign Envelopes | TO CREATE |

### P3 - Low Priority
| Module | Feature | Status |
|--------|---------|--------|
| `ipai_equity` | Share Tracking | TO CREATE |

---

## 3. External Service Integrations

| Service | Feature | Integration Method |
|---------|---------|-------------------|
| DocuSign/SignRequest | Electronic Signatures | REST API + Webhook |
| Twilio/MessageBird | SMS Gateway | REST API |
| OCR.space/Google Vision | Document OCR | REST API |
| Clearbit/Apollo | Partner Autocomplete | REST API |
| n8n/Mautic | Marketing Automation | Webhook + REST |
| Whisper API | Voice Transcription | REST API |

---

## 4. CE Core Modules (Already Included)

- `base_automation` - Automated Actions
- `base_action_rule` - Action Rules (deprecated, use base_automation)

---

## Installation Commands

### Quick Install (All OCA)
```bash
./scripts/install_oca_parity.sh
```

### Quick Install (All ipai_*)
```bash
./scripts/install_ipai_parity.sh
```

### Full Parity Install
```bash
./scripts/install_full_ee_parity.sh
```

### Verify Installation
```bash
python scripts/test_ee_parity.py --odoo-url http://localhost:8069 --db odoo_core
```

---

## Module Dependencies Graph

```
base
├── mail
│   ├── ipai_ai_agent_builder
│   │   ├── ipai_ai_rag
│   │   ├── ipai_ai_tools
│   │   ├── ipai_ai_fields
│   │   └── ipai_ai_livechat
│   └── ipai_whatsapp_connector
├── account
│   ├── account_asset_management (OCA)
│   ├── mis_builder (OCA)
│   ├── ipai_finance_tax_return
│   └── ipai_bir_* (localization)
├── hr
│   ├── payroll (OCA)
│   │   └── ipai_hr_payroll_ph
│   └── hr_appraisal_survey (OCA)
├── project
│   ├── project_timeline (OCA)
│   ├── project_forecast_line (OCA)
│   └── ipai_project_templates
├── helpdesk (if available)
│   ├── ipai_helpdesk
│   └── ipai_helpdesk_refund
├── documents (or dms)
│   ├── dms (OCA)
│   ├── ipai_documents_ai
│   └── ipai_sign
└── stock
    └── quality_control_oca (OCA)
```

---

*Generated by EE Parity Analysis Tool*
