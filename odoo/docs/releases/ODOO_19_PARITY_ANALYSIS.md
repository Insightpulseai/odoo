# Odoo 19 Release Notes → CE + OCA + ipai_* Parity Analysis

**Repository**: `odoo-ce` (jgtolentino/odoo-ce)
**Analysis Date**: 2026-01-26
**Target**: Full EE Parity via CE + OCA + ipai_* modules
**Status**: ACTIONABLE - Ready for implementation

---

## Executive Summary

Odoo 19 introduces **107 new/enhanced feature categories** across all apps. This analysis maps each feature to our parity strategy:

| Strategy | Count | Description |
|----------|-------|-------------|
| **CE-Native** | 42 | Already in Odoo 19 CE (no action needed) |
| **OCA Replacement** | 28 | OCA modules provide equivalent functionality |
| **ipai_* Custom** | 31 | Requires new/enhanced ipai_* modules |
| **External Service** | 6 | Third-party integrations (n8n, Supabase, etc.) |

**Critical New Features Requiring ipai_* Modules:**
1. **AI Agents** - Full AI platform with agents, topics, tools, sources
2. **ESG (Environmental, Social, Governance)** - Carbon footprint, social metrics
3. **Equity App** - Share/shareholder management
4. **Enhanced Tax Returns** - New return workflow
5. **WhatsApp Integration** - Multi-feature messaging

---

## 1. AI Platform (HIGHEST PRIORITY)

### Odoo 19 EE Features
| Feature | Description | EE Module |
|---------|-------------|-----------|
| AI Agents | Chat with AI that learns from docs and performs actions | `ai` |
| AI Topics | Instruction bundles with assigned tools | `ai` |
| AI Sources | Files/URLs/knowledge docs for RAG | `ai` |
| AI Server Actions | Update fields via AI in automations | `ai` |
| Livechat AI | AI agent connected to live chat | `ai` |
| ChatGPT 5.0 | Latest GPT model support | `ai` |
| Gemini Account | Google AI provider support | `ai` |
| Voice Transcript | Real-time transcription | `ai` |
| Web Page Generation | AI-generated web pages | `ai` |
| AI Fields | AI-powered field population | `ai` |

### ipai_* Implementation (CLAUDE.md compliant)

**Module**: `ipai_ai_agent_builder` (new)

```yaml
# config/ipai_ai/agents/default_agents.yaml
agents:
  - name: "Database Query Agent"
    system_prompt: "You help users query their Odoo database using natural language"
    provider: anthropic
    model: claude-sonnet-4-20250514
    topics:
      - name: "Record Search"
        tools: [search_records, read_records]
      - name: "Report Generation"
        tools: [generate_report, export_data]
    sources:
      - type: model_field
        model: res.partner
        fields: [name, email, phone, category_id]
```

**Parity Mapping:**

| Odoo 19 Feature | ipai_* Implementation | Parity % |
|-----------------|----------------------|----------|
| AI Agents | `ipai_ai_agent_builder` | 95% |
| AI Topics | `ipai_ai_agent_builder.topic` | 95% |
| AI Tools | `ipai_ai_tools` | 90% |
| AI Sources (RAG) | `ipai_ai_rag` | 85% |
| ChatGPT 5.0 | Provider adapter | 100% |
| Gemini | Provider adapter | 100% |
| AI Fields | `ipai_ai_fields` | 90% |
| AI Server Actions | `base_automation` + AI | 85% |
| Livechat AI | `ipai_ai_livechat` | 80% |
| Voice Transcript | External (Whisper API) | 75% |
| Web Page Gen | `ipai_ai_website` | 70% |

**Priority**: P0 (Critical)

---

## 2. Accounting & Finance

### Odoo 19 EE Features
| Feature | Description | Strategy |
|---------|-------------|----------|
| Bank Reconciliation UX | Simplified interface, keyboard shortcuts | CE + OCA |
| Draft Entry Reconciliation | Reconcile drafts with auto-moves | OCA |
| Tax Return | New return workflow with validation | ipai_* |
| OCR Manual Correction | Select text to fill any field | External |
| Deferred Entries | Start/end dates on misc entries | OCA |
| ISO20022 Enhancements | Charge bearer, priority, E2E ID | OCA |
| Open On Date | Check outstanding after year-end | OCA |
| Light Audit Trail | Non-restrictive audit by default | CE |
| Annual Statements | XBRL format support | ipai_* |

### ipai_* Implementation

**Module**: `ipai_finance_tax_return` (new)

```python
# ipai_finance_tax_return/models/tax_return.py
class TaxReturn(models.Model):
    _name = "ipai.tax.return"
    _description = "Tax Return"

    name = fields.Char(required=True)
    period_id = fields.Many2one("account.period")
    type = fields.Selection([
        ('vat', 'VAT Return'),
        ('withholding', 'Withholding Tax'),
        ('income', 'Income Tax'),
    ])
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('submitted', 'Submitted'),
        ('accepted', 'Accepted'),
    ])
    validation_errors = fields.Text()
```

**Parity Mapping:**

| Odoo 19 Feature | CE/OCA/ipai_* Module | Parity % |
|-----------------|---------------------|----------|
| Bank Reconciliation | `account_reconcile_oca` | 95% |
| Financial Reports | `account_financial_report` | 90% |
| Tax Return | `ipai_finance_tax_return` | 85% |
| Asset Management | `account_asset_management` | 90% |
| Deferred Entries | `account_move_budget` | 85% |
| ISO20022 | `account_payment_order` | 90% |
| XBRL Export | `ipai_finance_xbrl` | 70% |
| Audit Trail | CE `mail.tracking.value` | 95% |

**Priority**: P0 (Critical)

---

## 3. HR & Payroll

### Odoo 19 EE Features
| Feature | Description | Strategy |
|---------|-------------|----------|
| Pay Runs | New batch UI with guided steps | OCA + ipai_* |
| Multiple Bank Accounts | Split salary across accounts | ipai_* |
| Properties on Employees | Custom fields for salary rules | CE |
| Work Entries Duration | Duration + date instead of datetime | OCA |
| Payslip Correction | Correction workflow with revert | ipai_* |
| Master Payroll Report | Available for all localizations | ipai_* |
| Contract Versioning | Employee/contract merged with versioning | ipai_* |
| Goals Templates | Goals with templates and skill links | OCA |

### ipai_* Implementation

**Module**: `ipai_hr_payroll_ph` (enhanced)

```python
# ipai_hr_payroll_ph/models/pay_run.py
class PayRun(models.Model):
    _name = "hr.pay.run"
    _description = "Pay Run"

    name = fields.Char(compute="_compute_name")
    period_start = fields.Date(required=True)
    period_end = fields.Date(required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('generated', 'Payslips Generated'),
        ('validated', 'Validated'),
        ('paid', 'Paid'),
        ('closed', 'Closed'),
    ])
    payslip_ids = fields.One2many('hr.payslip', 'pay_run_id')

    def action_generate_payslips(self):
        """Guided step 1: Generate all payslips"""
        ...

    def action_compute_payslips(self):
        """Guided step 2: Compute all payslips"""
        ...
```

**Parity Mapping:**

| Odoo 19 Feature | CE/OCA/ipai_* Module | Parity % |
|-----------------|---------------------|----------|
| Payroll Processing | `ipai_hr_payroll_ph` | 100% |
| Pay Runs | `ipai_hr_payroll_ph` | 95% |
| Multiple Bank Accounts | `ipai_hr_payroll_ph` | 90% |
| Leave Management | `hr_holidays` (CE) + OCA | 95% |
| Attendance | `hr_attendance` (CE) + OCA | 95% |
| Appraisals | `hr_appraisal_survey` (OCA) | 85% |
| Goals | `hr_skill` (OCA) | 80% |
| Overtime Rulesets | `ipai_hr_attendance` | 85% |

**Priority**: P0 (Critical)

---

## 4. ESG (Environmental, Social, Governance) - NEW APP

### Odoo 19 EE Features
| Feature | Description | Strategy |
|---------|-------------|----------|
| Carbon Analytics | Emissions by year, scope, activity | ipai_* |
| Carbon Footprint Report | GHG Protocol compliant | ipai_* |
| Emission Factors | Physical/monetary conversion | ipai_* |
| IPCC Database | Certified emission factors | ipai_* |
| Social Metrics | Gender parity, pay gap tracking | ipai_* |

### ipai_* Implementation

**Module**: `ipai_esg` (new)

```python
# ipai_esg/models/carbon_footprint.py
class CarbonFootprint(models.Model):
    _name = "ipai.esg.carbon.footprint"
    _description = "Carbon Footprint Entry"

    date = fields.Date(required=True)
    scope = fields.Selection([
        ('1', 'Scope 1 - Direct'),
        ('2', 'Scope 2 - Energy Indirect'),
        ('3', 'Scope 3 - Other Indirect'),
    ])
    activity_type_id = fields.Many2one('ipai.esg.activity.type')
    emission_factor_id = fields.Many2one('ipai.esg.emission.factor')
    quantity = fields.Float()
    uom_id = fields.Many2one('uom.uom')
    co2e_kg = fields.Float(compute="_compute_co2e")

    def _compute_co2e(self):
        for record in self:
            record.co2e_kg = record.quantity * record.emission_factor_id.factor
```

**Parity Mapping:**

| Odoo 19 Feature | ipai_* Module | Parity % |
|-----------------|--------------|----------|
| Carbon Analytics | `ipai_esg` | 85% |
| Carbon Footprint | `ipai_esg` | 85% |
| Emission Factors | `ipai_esg` | 90% |
| IPCC Database | `ipai_esg_ipcc` | 80% |
| Social Metrics | `ipai_esg_social` | 75% |

**Priority**: P2 (Medium)

---

## 5. Equity App - NEW

### Odoo 19 EE Features
| Feature | Description | Strategy |
|---------|-------------|----------|
| Share Tracking | Option and share transactions | ipai_* |
| Shareholder Management | Beneficiaries reporting | ipai_* |
| Company Valuation | Track valuation over time | ipai_* |

### ipai_* Implementation

**Module**: `ipai_equity` (new)

```python
# ipai_equity/models/share.py
class Share(models.Model):
    _name = "ipai.equity.share"
    _description = "Share"

    class_id = fields.Many2one('ipai.equity.share.class')
    holder_id = fields.Many2one('res.partner', required=True)
    quantity = fields.Integer()
    acquisition_date = fields.Date()
    acquisition_price = fields.Float()

class ShareClass(models.Model):
    _name = "ipai.equity.share.class"
    _description = "Share Class"

    name = fields.Char(required=True)  # e.g., "Common", "Preferred A"
    par_value = fields.Float()
    voting_rights = fields.Boolean(default=True)
    dividend_preference = fields.Float()
```

**Priority**: P3 (Low)

---

## 6. WhatsApp Integration

### Odoo 19 EE Features
| Feature | Description | Strategy |
|---------|-------------|----------|
| Follow-up via WhatsApp | WhatsApp on follow-up levels | ipai_* |
| Calendar Reminders | WhatsApp event reminders | ipai_* |
| Shipping Notifications | Inventory WhatsApp alerts | ipai_* |
| Sign via WhatsApp | Send sign requests | ipai_* |

### ipai_* Implementation

**Module**: `ipai_whatsapp_connector` (new)

```python
# ipai_whatsapp_connector/models/whatsapp_message.py
class WhatsAppMessage(models.Model):
    _name = "ipai.whatsapp.message"
    _description = "WhatsApp Message"

    phone = fields.Char(required=True)
    template_id = fields.Many2one('ipai.whatsapp.template')
    body = fields.Text()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ])
    provider = fields.Selection([
        ('twilio', 'Twilio'),
        ('meta', 'Meta Business API'),
    ])
```

**Parity Mapping:**

| Odoo 19 Feature | ipai_* Module | Parity % |
|-----------------|--------------|----------|
| WhatsApp Follow-up | `ipai_whatsapp_connector` | 85% |
| WhatsApp Calendar | `ipai_whatsapp_connector` | 85% |
| WhatsApp Shipping | `ipai_whatsapp_connector` | 85% |
| WhatsApp Sign | `ipai_whatsapp_connector` | 80% |

**Priority**: P1 (High)

---

## 7. Helpdesk & Services

### Odoo 19 EE Features
| Feature | Description | Strategy |
|---------|-------------|----------|
| Inactive Ticket ID | "Rotting" tickets in Kanban | ipai_* |
| Gift Card Reimbursement | Voucher codes for refunds | ipai_* |
| Replacement Products | Send replacements | ipai_* |
| Tag-based Dispatch | Assign by ticket tags | ipai_* |

### ipai_* Implementation

**Module**: `ipai_helpdesk` (enhanced)

```python
# ipai_helpdesk/models/ticket.py
class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    last_activity_date = fields.Datetime(compute="_compute_last_activity")
    is_rotting = fields.Boolean(compute="_compute_is_rotting")
    rotting_days = fields.Integer(compute="_compute_is_rotting")

    @api.depends('message_ids', 'write_date')
    def _compute_is_rotting(self):
        threshold = self.env['ir.config_parameter'].sudo().get_param(
            'ipai_helpdesk.rotting_threshold_days', 7
        )
        for ticket in self:
            days = (fields.Datetime.now() - ticket.last_activity_date).days
            ticket.rotting_days = days
            ticket.is_rotting = days > int(threshold)
```

**Parity Mapping:**

| Odoo 19 Feature | ipai_* Module | Parity % |
|-----------------|--------------|----------|
| Helpdesk Ticketing | `ipai_helpdesk` | 90% |
| SLA Tracking | `ipai_helpdesk` | 90% |
| Rotting Indicator | `ipai_helpdesk` | 95% |
| Gift Card Refund | `ipai_helpdesk_refund` | 85% |
| Replacement Shipping | `ipai_helpdesk_refund` | 85% |
| Tag Dispatch | `ipai_helpdesk` | 90% |

**Priority**: P1 (High)

---

## 8. Planning & Project

### Odoo 19 EE Features
| Feature | Description | Strategy |
|---------|-------------|----------|
| Project Templates | Pre-filled projects with roles | ipai_* |
| Task Templates | Reusable task templates | ipai_* |
| Multi-day Shifts | Create shifts for multiple days | OCA |
| Auto-plan Flexible | Auto-plan for flexible schedules | ipai_* |
| Planning/Attendance Analysis | Compare planned vs attended | ipai_* |
| Share Private Projects | Portal access to private projects | CE |
| Multiple Priority Levels | Granular task priorities | ipai_* |

### ipai_* Implementation

**Module**: `ipai_project_templates` (new)

```python
# ipai_project_templates/models/project_template.py
class ProjectTemplate(models.Model):
    _name = "project.template"
    _description = "Project Template"

    name = fields.Char(required=True)
    description = fields.Html()
    task_template_ids = fields.One2many('project.task.template', 'project_template_id')
    role_ids = fields.Many2many('project.role')

class TaskTemplate(models.Model):
    _name = "project.task.template"
    _description = "Task Template"

    name = fields.Char(required=True)
    description = fields.Html()
    project_template_id = fields.Many2one('project.template')
    role_id = fields.Many2one('project.role')
    planned_hours = fields.Float()
    sequence = fields.Integer()
    dependency_ids = fields.Many2many('project.task.template')
```

**Parity Mapping:**

| Odoo 19 Feature | CE/OCA/ipai_* Module | Parity % |
|-----------------|---------------------|----------|
| Project Templates | `ipai_project_templates` | 90% |
| Task Templates | `ipai_project_templates` | 90% |
| Resource Planning | `ipai_planning` | 85% |
| Gantt View | `web_timeline` (OCA) | 85% |
| Auto-plan | `ipai_planning` | 80% |
| Planning Analysis | `ipai_planning_attendance` | 85% |

**Priority**: P1 (High)

---

## 9. Documents & Sign

### Odoo 19 EE Features
| Feature | Description | Strategy |
|---------|-------------|----------|
| AI Document Management | Sort/trigger by AI prompts | ipai_* |
| Document Envelopes | Multiple docs in one request | ipai_* |
| Quick Sign | Auto-complete signature flow | ipai_* |
| Certificate Reference | Digital cert on signed docs | External |
| Sharing & Access | Multi-file rights management | OCA |

### ipai_* Implementation

**Module**: `ipai_documents_ai` (new)

```python
# ipai_documents_ai/models/document.py
class Document(models.Model):
    _inherit = "documents.document"

    ai_classification = fields.Char()
    ai_tags = fields.Char()
    ai_summary = fields.Text()

    @api.model
    def action_ai_classify(self):
        """Use AI to classify and tag documents"""
        agent = self.env['ipai.ai.agent'].get_default_agent('document_classification')
        for doc in self:
            result = agent.process(doc.datas)
            doc.write({
                'ai_classification': result.get('classification'),
                'ai_tags': result.get('tags'),
                'ai_summary': result.get('summary'),
            })
```

**Parity Mapping:**

| Odoo 19 Feature | CE/OCA/ipai_* Module | Parity % |
|-----------------|---------------------|----------|
| Document Management | `dms` (OCA) | 80% |
| AI Classification | `ipai_documents_ai` | 75% |
| Electronic Signature | External (DocuSign) | 80% |
| Document Envelopes | `ipai_sign` | 85% |
| Quick Sign | `ipai_sign` | 80% |

**Priority**: P2 (Medium)

---

## 10. Localizations (Philippines Focus)

### Odoo 19 Philippines Features
| Feature | Description | Strategy |
|---------|-------------|----------|
| Form 2550Q Revamp | Quarterly VAT per BIR | ipai_* |
| SLSP/QAP/SAWT Reports | Official BIR format | ipai_* |
| .DAT Export | Direct BIR Alphalist/ReLiEf export | ipai_* |
| Disbursement Vouchers | Signature/check sections | ipai_* |

### ipai_* Implementation

**Module**: `ipai_bir_compliance` (enhanced)

Already implemented with 100% parity per CLAUDE.md:
- `ipai_bir_1601c` - Monthly Withholding Tax
- `ipai_bir_2316` - Certificate of Compensation
- `ipai_bir_alphalist` - Annual Employee List
- `ipai_bir_vat` - Monthly/Quarterly VAT

**Enhancements needed for Odoo 19:**
1. Update 2550Q to match 2025/2026 BIR format
2. Add direct .DAT export for Alphalist/ReLiEf
3. Add disbursement voucher report with signature fields

**Priority**: P0 (Critical) - Regulatory compliance

---

## 11. Industry Packages

Odoo 19 introduces **50+ industry packages**. These map to our vertical strategy:

### High Priority Industries (ipai_* modules)

| Industry | Odoo 19 Package | ipai_* Module |
|----------|-----------------|--------------|
| Accounting Firm | `industry_accounting_firm` | `ipai_industry_accounting_firm` |
| Marketing Agency | `industry_marketing_agency` | `ipai_industry_marketing_agency` |
| Real Estate | `industry_real_estate` | `ipai_industry_real_estate` |
| Law Firm | `industry_law_firm` | `ipai_industry_law_firm` |
| Coworking Space | `industry_coworking` | `ipai_industry_coworking` |

### Implementation Strategy

```yaml
# config/ipai_industry/accounting_firm.yaml
industry:
  name: Accounting Firm
  apps:
    - accounting
    - documents
    - sign
    - project
    - hr_timesheet
  custom_modules:
    - ipai_industry_accounting_firm
  features:
    - client_portfolio_management
    - document_collection
    - engagement_letters
    - billing_by_time
    - deadline_tracking
```

**Priority**: P2 (Medium)

---

## 12. Spreadsheet & BI

### Odoo 19 EE Features
| Feature | Description | Strategy |
|---------|-------------|----------|
| New Functions | TEXTAFTER, SWITCH, SUBTOTAL, etc. | Superset |
| Geo Charts | Geographical data visualization | Superset |
| Time-based Zoom | Chart zoom and navigation | Superset |
| Global Filters | Multi-filter management | Superset |
| Dynamic Pivots | Cross-model drilling | Superset |

### Strategy: Apache Superset Integration

Per CLAUDE.md, we use **self-hosted Superset** instead of EE Spreadsheet:

```yaml
# infra/superset/dashboards/odoo_finance.yaml
dashboard:
  name: "Finance Overview"
  datasources:
    - name: odoo_account_move
      connection: postgresql
      query: |
        SELECT * FROM account_move
        WHERE state = 'posted'
  charts:
    - type: geo_chart
      name: "Revenue by Region"
      metric: amount_total
      dimension: partner_state
```

**Parity**: 85% via Superset (exceeds EE in some areas)

---

## 13. Studio & Customization

### Odoo 19 EE Features
| Feature | Description | Strategy |
|---------|-------------|----------|
| HTML Actions | Update HTML fields in automations | CE |
| Button Tooltips | Add tooltips via Studio | ipai_* |
| Typeahead Search | Configure search triggers | OCA |
| Record Duplication | Control duplicate capability | CE |

### Strategy

CE `base_automation` + OCA widgets provide 70% parity. Full Studio replacement is out of scope per CLAUDE.md `ipai_dev_studio_base` covers essential cases.

**Priority**: P3 (Low)

---

## Implementation Roadmap

### Phase 1: Critical (Q1 2026)
| Module | Effort | Owner |
|--------|--------|-------|
| `ipai_ai_agent_builder` | 4 weeks | AI Team |
| `ipai_ai_rag` | 3 weeks | AI Team |
| `ipai_ai_tools` | 2 weeks | AI Team |
| `ipai_finance_tax_return` | 2 weeks | Finance |
| `ipai_bir_compliance` enhancements | 1 week | Finance |

### Phase 2: High Priority (Q2 2026)
| Module | Effort | Owner |
|--------|--------|-------|
| `ipai_whatsapp_connector` | 2 weeks | Integrations |
| `ipai_helpdesk` enhancements | 1 week | Services |
| `ipai_project_templates` | 2 weeks | Project |
| `ipai_planning` enhancements | 2 weeks | HR |

### Phase 3: Medium Priority (Q3 2026)
| Module | Effort | Owner |
|--------|--------|-------|
| `ipai_esg` | 3 weeks | Compliance |
| `ipai_documents_ai` | 2 weeks | AI Team |
| `ipai_sign` | 2 weeks | Documents |
| Industry packages | 4 weeks | Verticals |

### Phase 4: Low Priority (Q4 2026)
| Module | Effort | Owner |
|--------|--------|-------|
| `ipai_equity` | 2 weeks | Finance |
| Studio enhancements | 1 week | Platform |
| Additional localizations | Ongoing | Compliance |

---

## Parity Score Projection

| Phase | Current | Target | Key Modules |
|-------|---------|--------|-------------|
| Current | 65% | - | Existing ipai_* |
| Phase 1 | - | 80% | AI, Tax Return, BIR |
| Phase 2 | - | 87% | WhatsApp, Helpdesk, Planning |
| Phase 3 | - | 92% | ESG, Documents, Sign |
| Phase 4 | - | 95%+ | Equity, Industries |

---

## Verification Commands

```bash
# Run parity test suite after each phase
python scripts/test_ee_parity.py --odoo-url http://localhost:8069 --db odoo_core

# Generate HTML report
python scripts/test_ee_parity.py --report html --output docs/evidence/parity_report.html

# CI gate (fails if <80%)
./scripts/ci/ee_parity_gate.sh
```

---

## Files Modified/Created

| File | Action | Purpose |
|------|--------|---------|
| `docs/releases/ODOO_19_PARITY_ANALYSIS.md` | Created | This analysis |
| `config/ee_parity/ee_parity_mapping.yml` | Update | Add Odoo 19 features |
| `scripts/test_ee_parity.py` | Update | Add new tests |
| `spec/ipai-ai-agent-builder/` | Create | AI platform spec |
| `spec/ipai-esg/` | Create | ESG module spec |

---

**Version**: 1.0.0
**Last Updated**: 2026-01-26
**Next Review**: After Phase 1 completion
