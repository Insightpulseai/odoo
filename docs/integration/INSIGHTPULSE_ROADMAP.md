# InsightPulse Finance SSC — Consolidated Implementation Roadmap

> Generated from architecture review session, January 2026

## Executive Summary

This document consolidates all implementation recommendations for the InsightPulse Finance SSC platform, replacing legacy SaaS tools with self-hosted open-source alternatives.

**Total Annual Savings Target: $48,480**

| SaaS Tool | Replacement | Annual Savings |
|-----------|-------------|----------------|
| Slack | Mattermost | $7,200 |
| Tableau | Apache Superset | $12,600 |
| SAP Analytics Cloud | Apache Superset | $6,480 |
| SAP Concur | ipai_expense (Odoo) | $15,000 |
| Notion | Mattermost Boards + Affine | $4,800 |
| Trello | Mattermost Boards | $2,400 |

---

## Phase 0: Critical Fixes (Immediate)

### 0.1 Fix Odoo Email Configuration

**Problem**: Emails failing to `admin@yourcompany.example.com` (placeholder domain)

```bash
# SSH to primary server
ssh root@159.223.75.148

# Fix via SQL
docker exec -it odoo-db psql -U odoo -d odoo -c "
UPDATE ir_config_parameter SET value = 'insightpulseai.com' WHERE key = 'mail.catchall.domain';
UPDATE ir_config_parameter SET value = 'no-reply@insightpulseai.com' WHERE key = 'mail.default.from';
UPDATE ir_config_parameter SET value = 'https://erp.insightpulseai.com' WHERE key = 'web.base.url';
"

# Restart Odoo
docker restart odoo
```

### 0.2 Add Missing Mailgun DNS Records

Add to DigitalOcean DNS:

| Host | Type | Priority | Data |
|------|------|----------|------|
| `mg` | MX | 10 | mxa.mailgun.org |
| `mg` | MX | 10 | mxb.mailgun.org |
| `_dmarc` | TXT | - | `v=DMARC1; p=none; rua=mailto:dmarc@insightpulseai.com` |

---

## Phase 1: Connector Integration (Week 1)

### 1.1 Enable Claude Connectors

| Connector | Priority | Use Case |
|-----------|----------|----------|
| **n8n** | Critical | Automation backbone, workflow debugging |
| **Gmail** | Critical | Invoice/receipt emails, BIR confirmations |
| **Google Calendar** | High | Month-end deadlines, BIR filing dates |
| **Vercel** | Medium | Deployment visibility |

### 1.2 Claude for Slack Onboarding

See [SLACK_INTEGRATION_SETUP.md](./SLACK_INTEGRATION_SETUP.md) for team onboarding guide.

---

## Phase 2: n8n Workflow Implementation (Week 1-2)

### 2.1 Priority Workflows

**Tier 1 — Immediate Value:**
| Workflow | Source Template | Adaptation |
|----------|----------------|------------|
| Invoice OCR → Odoo | [n8n.io/workflows/4331](https://n8n.io/workflows/4331) | Replace with PaddleOCR, add BIR fields |
| Receipt Capture | [n8n.io/workflows/5442](https://n8n.io/workflows/5442) | Route to Odoo hr.expense |
| Invoice Verification | [n8n.io/workflows/4860](https://n8n.io/workflows/4860) | Add PO matching |

**Tier 2 — Month-End Automation:**
- JE Template Generator
- Intercompany Settlement Matcher
- Depreciation Calculator

**Tier 3 — BIR Compliance:**
- Withholding Tax Extractor (EWT, VAT)
- Form 1601-C Data Prep
- Form 2550Q Quarterly Summary

### 2.2 Integration Architecture

```
Input Sources                n8n Processing              Output Destinations
─────────────────           ────────────────            ─────────────────────
Gmail                       ┌─────────────────┐
Google Drive         ──────►│  PaddleOCR      │         Odoo 18 CE
Telegram                    │  (RTX 4090)     │──────►  • account.move
                            │                 │         • hr.expense
                            │  AI Agent       │
                            │  (Claude/GPT)   │──────►  Supabase
                            │                 │         • staging_invoices
                            │  HTTP Request   │         • audit_log
                            │  (Odoo XML-RPC) │
                            └─────────────────┘──────►  Google Sheets
```

---

## Phase 3: Apache Superset Configuration (Week 2)

**Status**: Deployed at `https://superset.insightpulseai.com`

### 3.1 Data Source Connections

| Source | Connection String | Purpose |
|--------|-------------------|---------|
| Odoo PostgreSQL | `postgresql://odoo:***@159.223.75.148:5432/odoo` | ERP data |
| Supabase | `postgresql://postgres:***@db.spdtwktxdalcfigzeqrz.supabase.co:5432/postgres` | Staging/logs |

### 3.2 Virtual Datasets Required

```sql
-- BIR Withholding Summary
CREATE VIEW vw_bir_withholding_summary AS
SELECT
    partner.name AS vendor_name,
    partner.vat AS tin,
    move.date AS invoice_date,
    line.debit AS gross_amount,
    tax.amount AS tax_rate,
    (line.debit * tax.amount / 100) AS withholding_amount,
    company.name AS agency
FROM account_move_line line
JOIN account_move move ON line.move_id = move.id
JOIN res_partner partner ON move.partner_id = partner.id
JOIN account_tax tax ON line.tax_line_id = tax.id
JOIN res_company company ON move.company_id = company.id
WHERE tax.type_tax_use = 'purchase'
  AND tax.name ILIKE '%withholding%';
```

### 3.3 Dashboards to Create

1. **BIR Compliance** — Withholding tax summary, filing deadlines
2. **Month-End Operations** — Cash position, AP/AR aging
3. **Executive Summary** — KPI scorecards, YoY comparison
4. **Expense Analytics** — Policy violations, spend by category

---

## Phase 4: Mattermost Configuration (Week 2-3)

**Status**: Deployed at `https://chat.insightpulseai.com`

### 4.1 Channel Structure

```
📢 FINANCE OPS
├── #finance-general
├── #month-end-closing
├── #journal-entries
├── #bank-reconciliation
└── #intercompany

📋 BIR COMPLIANCE
├── #bir-filings
├── #bir-deadlines
└── #bir-alerts

🤖 AUTOMATION
├── #n8n-notifications
├── #odoo-alerts
└── #system-health

🔒 PRIVATE
├── finance-leadership
└── audit-committee
```

### 4.2 n8n → Mattermost Webhooks

| Webhook | Channel | Trigger |
|---------|---------|---------|
| Invoice Approved | #journal-entries | Odoo account.move state=posted |
| Month-End Task | #month-end-closing | Playbook checklist item |
| BIR Filing Due | #bir-alerts | 3 days before deadline |
| Policy Violation | #finance-general | Policy rule breach |

### 4.3 Playbooks

**Month-End Closing:**
| Phase | Day | Tasks |
|-------|-----|-------|
| Pre-Close | 1-3 | Verify invoices, bank reconciliation, intercompany |
| Close | 4-5 | Depreciation, payroll entries, trial balance |
| Reporting | 6-7 | Financial statements, variance analysis, submit |

**BIR Filing:**
| Form | Deadline | Checklist |
|------|----------|-----------|
| 1601-C | 10th of month | Withholding tax computation, eFPS submission |
| 2550Q | 25th after quarter | VAT summary, input/output reconciliation |
| 1702 | April 15 | ITR preparation, audited FS attachment |

---

## Phase 5: Documentation (Week 3)

### 5.1 GitBook Handbook Structure

```
📚 TBWA FINANCE SSC HANDBOOK
├── 🏢 ORGANIZATION
│   ├── About Finance SSC
│   └── Team Directory (employee codes)
├── 💰 FINANCE OPERATIONS
│   ├── 📋 Policies
│   │   ├── How to Spend Company Money
│   │   ├── Travel & Expense Policy
│   │   └── Corporate Card Policy
│   ├── 🧾 Expense Management
│   │   ├── How to Submit
│   │   └── Approval Workflow
│   └── 📊 Month-End Close
│       ├── Checklist
│       └── Journal Standards
├── 🏛️ BIR COMPLIANCE
│   ├── Tax Calendar
│   └── Form Guides
└── 🛠️ SYSTEMS
    ├── Odoo Guide
    ├── Superset Guide
    └── Mattermost Guide
```

### 5.2 Key Policies

**Expense Approval Thresholds (PHP):**
| Amount | Approval Required |
|--------|-------------------|
| < ₱5,000 | Self-approval with receipt |
| ₱5,000 - ₱25,000 | Manager approval |
| ₱25,000 - ₱100,000 | Department Head + Finance |
| > ₱100,000 | CFO/Finance Director |

---

## Phase 6: Claude Skills (Week 3-4)

### 6.1 Skills to Create

| Skill | Purpose | Location |
|-------|---------|----------|
| finance-month-end | Month-end closing automation | `/mnt/skills/user/` |
| bir-tax-filing | BIR compliance workflows | `/mnt/skills/user/` |
| expense-processing | Receipt OCR → Odoo posting | `/mnt/skills/user/` |
| journal-entry-validator | JE validation rules | `/mnt/skills/user/` |

### 6.2 Skill Template (Anthropic Format)

```yaml
---
name: finance-ssc-month-end
description: Automates month-end closing for TBWA Finance SSC
---

# Finance SSC Month-End Closing

## Prerequisites
- Access to Odoo 18 CE via MCP
- Supabase staging tables populated
- n8n workflows active

## Workflow Steps
[Step-by-step instructions...]

## Automation Triggers
- `/month-end start` - Initiates closing
- `/month-end status` - Shows progress
- `/month-end report` - Generates report
```

---

## Phase 7: MCP Server Development (Week 4)

### 7.1 MCP Servers Required

| Server | Purpose | Tools Exposed |
|--------|---------|---------------|
| odoo-mcp | Odoo XML-RPC/REST | search, read, create, execute |
| supabase-mcp | Supabase queries | query, insert, realtime |
| n8n-mcp | Workflow triggers | trigger_workflow, get_execution |
| paddleocr-mcp | OCR processing | extract_receipt, extract_invoice |

---

## Phase 8: OCA Module Installation (Week 5)

### 8.1 Priority Modules

| Repository | Module | Purpose |
|------------|--------|---------|
| account-financial-tools | account_lock_date | Period lock |
| account-financial-reporting | account_financial_report | Trial balance |
| account-reconcile | account_reconcile_oca | Bank reconciliation |
| reporting-engine | report_xlsx | Excel exports |
| rest-framework | base_rest | REST API |

### 8.2 Installation

```bash
cd /opt/odoo-ce
git submodule add https://github.com/OCA/account-financial-tools.git oca/account-financial-tools
git submodule add https://github.com/OCA/account-financial-reporting.git oca/account-financial-reporting
git submodule add https://github.com/OCA/reporting-engine.git oca/reporting-engine
```

---

## Infrastructure Map

| Service | URL | Server IP |
|---------|-----|-----------|
| Odoo ERP | https://erp.insightpulseai.com | 159.223.75.148 |
| n8n | https://n8n.insightpulseai.com | 159.223.75.148 |
| Mattermost | https://chat.insightpulseai.com | 159.223.75.148 |
| Auth | https://auth.insightpulseai.com | 159.223.75.148 |
| PaddleOCR | https://ocr.insightpulseai.com | 188.166.237.231 |
| Affine | https://affine.insightpulseai.com | 188.166.237.231 |
| Superset | https://superset.insightpulseai.com | DO App Platform |
| MCP | https://mcp.insightpulseai.com | DO App Platform |
| Agent | https://agent.insightpulseai.com | DO AI Platform |

---

## Quick Reference Links

| Resource | URL |
|----------|-----|
| Supabase Docs | https://supabase.com/docs |
| Odoo 18 Docs | https://www.odoo.com/documentation/18.0/ |
| OCA Repositories | https://github.com/orgs/OCA/repositories |
| Anthropic Skills | https://github.com/anthropics/skills |
| MS Agent Framework | https://github.com/microsoft/agent-framework |
| n8n Invoice Workflows | https://n8n.io/workflows/categories/invoice-processing/ |

---

## Execution Checklist

### Week 1
- [ ] Fix Odoo email configuration (Phase 0.1)
- [ ] Add missing Mailgun DNS records (Phase 0.2)
- [ ] Enable Claude connectors: n8n, Gmail, Calendar (Phase 1.1)
- [ ] Share Claude for Slack onboarding (Phase 1.2)
- [ ] Fork Invoice OCR n8n workflow (Phase 2.1)

### Week 2
- [ ] Adapt n8n workflows for PaddleOCR + Odoo (Phase 2.2)
- [ ] Connect Superset to Odoo PostgreSQL (Phase 3.1)
- [ ] Create BIR Withholding virtual dataset (Phase 3.2)
- [ ] Build first Superset dashboard (Phase 3.3)

### Week 3
- [ ] Configure Mattermost channels (Phase 4.1)
- [ ] Set up n8n → Mattermost webhooks (Phase 4.2)
- [ ] Create Month-End Playbook (Phase 4.3)
- [ ] Initialize GitBook handbook (Phase 5.1)
- [ ] Write Expense Policy document (Phase 5.2)

### Week 4
- [ ] Create finance-month-end Claude skill (Phase 6.1)
- [ ] Create bir-tax-filing Claude skill (Phase 6.1)
- [ ] Build odoo-mcp server (Phase 7.1)
- [ ] Build n8n-mcp server (Phase 7.1)

### Week 5
- [ ] Install OCA account-financial-tools (Phase 8.1)
- [ ] Install OCA reporting-engine (Phase 8.1)
- [ ] End-to-end testing of automated month-end

---

*Last updated: 2026-01-06*
