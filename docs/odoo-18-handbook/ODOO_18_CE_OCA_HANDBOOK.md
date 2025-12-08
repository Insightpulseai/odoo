# InsightPulseAI Odoo 18 CE/OCA Implementation Handbook

**Version:** 1.0.0
**Stack:** Odoo 18 CE + OCA + Supabase + n8n + AI Agents
**Organization:** TBWA/InsightPulseAI
**Last Updated:** 2025-12-07

---

## Executive Summary

This handbook provides a **stack-specific documentation set** for the InsightPulseAI Odoo 18 CE/OCA implementation. It adapts the official Odoo 18 documentation to our environment:

- **Core ERP**: Odoo 18 Community Edition + OCA modules (no Enterprise/IAP)
- **Infrastructure**: DigitalOcean droplets, nginx, Docker
- **Data Platform**: Supabase (PostgreSQL) as central analytical store
- **Automation**: n8n workflows, Supabase Edge Functions
- **Analytics**: Apache Superset, Scout/SariCoach dashboards
- **AI Layer**: Claude/OpenAI agents, RAG, Spec-Driven Development

---

## Table of Contents

1. [Odoo 18 Documentation Classification](#1-odoo-18-documentation-classification)
2. [New Documentation IA](#2-new-documentation-ia-for-insightpulseai)
3. [CE/OCA Mapping Tables](#3-ceoce-mapping-tables)
4. [Integration Architecture](#4-integration-architecture)
5. [RAG & Chunking Strategy](#5-rag--chunking-strategy)
6. [Governance & Guidelines](#6-governance--guidelines)

---

## 1. Odoo 18 Documentation Classification

### 1.1 Source Documentation Structure

The official Odoo 18.0 documentation at [https://www.odoo.com/documentation/18.0/](https://www.odoo.com/documentation/18.0/) is organized into:

| Section | URL Path | Description |
|---------|----------|-------------|
| Applications | `/applications.html` | User guides per application |
| Developer | `/developer.html` | Technical/API documentation |
| Contributing | `/contributing.html` | Contribution guidelines |
| Administration | `/administration.html` | Deployment and config |

### 1.2 Application Classification Matrix

| Area | Upstream Section(s) | CE/EE/IAP | Relevance to IPAI | Notes |
|------|---------------------|-----------|-------------------|-------|
| **Finance** | Accounting, Invoicing, Expenses | CE_NATIVE + OCA | HIGH | Core for PPM, TE-Cheq |
| **Accounting** | Finance > Accounting | CE_NATIVE | HIGH | Chart of accounts, journals, reconciliation |
| **Invoicing** | Finance > Invoicing | CE_NATIVE | HIGH | Customer/vendor invoicing |
| **Expenses** | Finance > Expenses | CE_NATIVE | HIGH | TE-Cheq integration |
| **Spreadsheet** | Finance > Spreadsheet | ENTERPRISE | LOW | Use Superset instead |
| **Documents** | Finance > Documents | ENTERPRISE | REPLACE | Use Notion + Supabase |
| **Sign** | Finance > Sign | ENTERPRISE | REPLACE | Use external e-sign |
| **Sales** | Sales, CRM | CE_NATIVE | MEDIUM | Standard sales workflows |
| **CRM** | Sales > CRM | CE_NATIVE | MEDIUM | Lead/opportunity mgmt |
| **POS** | Sales > POS | CE_NATIVE | MEDIUM | Scout retail integration |
| **Subscriptions** | Sales > Subscriptions | ENTERPRISE | OCA_REPLACE | Use OCA/contract |
| **Rental** | Sales > Rental | ENTERPRISE | DROP | Not in scope |
| **Inventory** | Supply Chain > Inventory | CE_NATIVE | MEDIUM | Equipment mgmt base |
| **Manufacturing** | Supply Chain > Manufacturing | CE_NATIVE | LOW | Limited use |
| **PLM** | Supply Chain > PLM | ENTERPRISE | OCA_REPLACE | Use OCA/plm |
| **Purchase** | Supply Chain > Purchase | CE_NATIVE | MEDIUM | Vendor management |
| **Maintenance** | Supply Chain > Maintenance | CE_NATIVE | MEDIUM | Equipment maintenance |
| **Quality** | Supply Chain > Quality | ENTERPRISE | OCA_REPLACE | Use OCA/quality |
| **Project** | Services > Project | CE_NATIVE | HIGH | PPM foundation |
| **Timesheets** | Services > Timesheets | CE_NATIVE | HIGH | PPM time tracking |
| **Field Service** | Services > Field Service | ENTERPRISE | OCA_REPLACE | Use OCA/field-service |
| **Helpdesk** | Services > Helpdesk | ENTERPRISE | OCA_REPLACE | Use OCA/helpdesk |
| **Planning** | Services > Planning | ENTERPRISE | OCA_REPLACE | Use ipai_ppm modules |
| **Appointments** | Services > Appointments | ENTERPRISE | OCA_REPLACE | Use OCA/calendar |
| **Employees** | HR > Employees | CE_NATIVE | HIGH | Core HR data |
| **Recruitment** | HR > Recruitment | CE_NATIVE | MEDIUM | Hiring workflows |
| **Time Off** | HR > Time Off | CE_NATIVE | MEDIUM | Leave management |
| **Appraisals** | HR > Appraisals | ENTERPRISE | OCA_REPLACE | Use OCA/hr |
| **Referrals** | HR > Referrals | ENTERPRISE | DROP | Not in scope |
| **Fleet** | HR > Fleet | CE_NATIVE | LOW | Vehicle management |
| **Email Marketing** | Marketing > Email Marketing | CE_NATIVE | LOW | Use external tools |
| **SMS Marketing** | Marketing > SMS | CE_NATIVE | LOW | Use external tools |
| **Events** | Marketing > Events | CE_NATIVE | LOW | Event management |
| **Marketing Automation** | Marketing > Automation | ENTERPRISE | DROP | Use n8n |
| **Surveys** | Marketing > Surveys | CE_NATIVE | LOW | Basic surveys |
| **Discuss** | Productivity > Discuss | CE_NATIVE | MEDIUM | Internal chat |
| **Approvals** | Productivity > Approvals | ENTERPRISE | REPLACE | Use n8n workflows |
| **IoT** | Productivity > IoT | ENTERPRISE | DROP | Not in scope |
| **VoIP** | Productivity > VoIP | ENTERPRISE | OCA_REPLACE | Use OCA telephony |
| **Knowledge** | Productivity > Knowledge | ENTERPRISE | REPLACE | Use Notion |
| **WhatsApp** | Productivity > WhatsApp | ENTERPRISE | DROP | Not in scope |
| **Studio** | Developer > Studio | ENTERPRISE | DROP | Use proper dev |
| **Website** | Websites > Website | CE_NATIVE | LOW | Basic website |
| **eCommerce** | Websites > eCommerce | CE_NATIVE | LOW | Basic ecommerce |
| **eLearning** | Websites > eLearning | ENTERPRISE | DROP | Not in scope |
| **Live Chat** | Websites > Live Chat | ENTERPRISE | REPLACE | Use Mattermost |

### 1.3 Classification Legend

| Tag | Description |
|-----|-------------|
| `CE_NATIVE` | Available in Odoo 18 Community Edition out-of-box |
| `CE_CONFIG` | Achievable via CE configuration (no code) |
| `OCA_REPLACE` | Replace Enterprise feature with OCA 18.0 module |
| `REPLACE` | Replace with InsightPulseAI stack component |
| `DROP` | Feature not in scope for our implementation |
| `ENTERPRISE` | Enterprise-only feature (documentation reference only) |

---

## 2. New Documentation IA for InsightPulseAI

### 2.1 Proposed Navigation Tree

```
InsightPulseAI Odoo 18 CE/OCA Handbook
├── 0. Welcome & Architecture
│   ├── 0.1 System Overview
│   ├── 0.2 Stack Components (Odoo + Supabase + n8n + AI)
│   ├── 0.3 Environments (local, staging, prod on DigitalOcean)
│   └── 0.4 Multi-Tenant Architecture
│
├── 1. Finance Workspace
│   ├── 1.1 Odoo CE Modules Overview (Accounting, Invoicing, Expenses)
│   ├── 1.2 Chart of Accounts (PH Localization)
│   ├── 1.3 Customer Invoicing Workflow
│   ├── 1.4 Vendor Bills & Payments
│   ├── 1.5 Expense Management (TE-Cheq Integration)
│   ├── 1.6 Bank Reconciliation
│   ├── 1.7 Month-End Close Process
│   ├── 1.8 Supabase Data Mapping (finance.*, expense.*)
│   └── 1.9 n8n Automations (Month-End, Approvals, Sync)
│
├── 2. Projects & PPM
│   ├── 2.1 Odoo CE Project Module
│   ├── 2.2 Portfolio → Program → Project Hierarchy
│   ├── 2.3 WBS & Task Management
│   ├── 2.4 Timesheet Entry & Approval
│   ├── 2.5 Budget & Rate Cards
│   ├── 2.6 Supabase Mapping (projects.*, rates.*)
│   └── 2.7 PPM Analytics (Superset Integration)
│
├── 3. HR & People Ops
│   ├── 3.1 Employee Master Data
│   ├── 3.2 Recruitment Workflows
│   ├── 3.3 Time Off Management
│   ├── 3.4 Attendance Tracking
│   ├── 3.5 Supabase Mapping (core.employees)
│   └── 3.6 AI Agent Integration (HR Coach)
│
├── 4. Retail & Scout Integration
│   ├── 4.1 Point of Sale Configuration
│   ├── 4.2 Scout Data Ingestion
│   ├── 4.3 Medallion Architecture (Bronze → Silver → Gold)
│   ├── 4.4 SariCoach Analytics
│   └── 4.5 AI Agents (Retail Intel Engine)
│
├── 5. Inventory & Equipment
│   ├── 5.1 Inventory Module Basics
│   ├── 5.2 Equipment Management (Cheqroom Parity)
│   ├── 5.3 Booking & Check-out Workflows
│   ├── 5.4 Maintenance Scheduling
│   └── 5.5 Supabase Integration
│
├── 6. Sales & CRM
│   ├── 6.1 CRM Lead Management
│   ├── 6.2 Quotations & Sales Orders
│   ├── 6.3 Pipeline Analytics
│   └── 6.4 Supabase Sync
│
├── 7. AI Workbench & Agents
│   ├── 7.1 Engine Registry Architecture
│   ├── 7.2 MCP Server Configuration
│   ├── 7.3 RAG over Documentation
│   ├── 7.4 Domain Agents (Finance, Retail, HR)
│   └── 7.5 Spec Kit Integration
│
├── 8. Integrations
│   ├── 8.1 Supabase (Data Platform)
│   ├── 8.2 n8n (Workflow Automation)
│   ├── 8.3 Mattermost (ChatOps)
│   ├── 8.4 Superset (Analytics)
│   └── 8.5 External APIs
│
├── 9. DevOps & Deployment
│   ├── 9.1 DigitalOcean Droplet Layout
│   ├── 9.2 Docker Compose Configuration
│   ├── 9.3 CI/CD Pipeline (GitHub Actions)
│   ├── 9.4 Backup & Restore
│   ├── 9.5 SSL & Security
│   └── 9.6 Observability & Monitoring
│
└── 10. Developer Guide
    ├── 10.1 OCA Development Standards
    ├── 10.2 Module Development (ipai_* pattern)
    ├── 10.3 Security & RLS Patterns
    ├── 10.4 Testing Framework
    └── 10.5 Migration Procedures
```

### 2.2 Section Descriptions

| Section | Purpose | How It Differs from Stock Odoo Docs |
|---------|---------|-------------------------------------|
| **0. Welcome & Architecture** | System overview and environment setup | Covers Supabase, n8n, AI stack integration not in Odoo docs |
| **1. Finance Workspace** | Finance operations for TBWA/IPAI | PH-specific localization, TE-Cheq integration, Supabase analytics |
| **2. Projects & PPM** | Portfolio/Project management | Clarity PPM-style hierarchy, ipai_ppm modules, rate cards |
| **3. HR & People Ops** | HR workflows | CE-only features, AI coach integration |
| **4. Retail & Scout Integration** | Retail analytics pipeline | Scout data ingestion, medallion architecture (not in Odoo) |
| **5. Inventory & Equipment** | Equipment booking (Cheqroom-style) | ipai_equipment custom features |
| **6. Sales & CRM** | Standard sales workflows | Supabase sync patterns |
| **7. AI Workbench & Agents** | AI/ML integration | Entirely custom - engine registry, MCP, RAG |
| **8. Integrations** | External system connections | Supabase, n8n, Mattermost (not in Odoo docs) |
| **9. DevOps & Deployment** | Infrastructure management | DigitalOcean-specific, Docker patterns |
| **10. Developer Guide** | Module development | OCA compliance, ipai_* patterns |

---

## 3. CE/OCA Mapping Tables

### 3.1 Finance Domain

| Domain | Process | Odoo Module(s) / Models | OCA Addon(s) | Supabase Schema.Table(s) | n8n / Edge Function Flow(s) | Notes |
|--------|---------|-------------------------|--------------|--------------------------|----------------------------|-------|
| Finance | Customer Invoicing | `account.move`, `account.payment` | - | `finance.invoices`, `finance.payments` | `wf_invoice_sync` | CE-native, no online payments |
| Finance | Vendor Bills | `account.move` (in_invoice) | `account_invoice_supplier_ref_unique` | `finance.vendor_bills` | `wf_vendor_bill_approval` | Approval via n8n |
| Finance | Chart of Accounts | `account.account` | `account_chart_update` | `finance.chart_of_accounts` | - | PH localization via config |
| Finance | Bank Reconciliation | `account.bank.statement` | `account_reconcile_oca` | `finance.bank_statements` | `wf_bank_reconcile_assist` | AI-assisted matching |
| Finance | Journal Entries | `account.move.line` | - | `finance.journal_entries` | - | CE-native |
| Finance | Multi-Currency | `res.currency.rate` | - | `finance.fx_rates` | `wf_fx_rate_update` | Daily rate sync |
| Finance | Month-End Close | `account.period` (deprecated) | `account_fiscal_month` | `finance.close_periods` | `wf_month_end_checklist` | Automated close workflow |
| Expense | Expense Reports | `hr.expense.sheet`, `hr.expense` | `hr_expense_invoice` | `expense.expense_reports`, `expense.expenses` | `wf_expense_approval` | TE-Cheq integration |
| Expense | Cash Advances | - | - | `expense.cash_advances` | `wf_cash_advance_approval` | ipai_cash_advance module |
| Expense | OCR Receipt Processing | - | - | `doc.receipts` | `wf_ocr_receipt_process` | E1 Data Intake Engine |

### 3.2 Projects & PPM Domain

| Domain | Process | Odoo Module(s) / Models | OCA Addon(s) | Supabase Schema.Table(s) | n8n / Edge Function Flow(s) | Notes |
|--------|---------|-------------------------|--------------|--------------------------|----------------------------|-------|
| PPM | Portfolio Management | - | - | `projects.portfolios` | - | ipai_ppm_portfolio module |
| PPM | Program Management | - | - | `projects.programs` | - | ipai_ppm_portfolio module |
| PPM | Project Management | `project.project` | `project_task_default_stage` | `projects.projects` | `wf_project_sync` | Bi-directional sync |
| PPM | WBS / Tasks | `project.task` | `project_task_add_very_high` | `projects.tasks`, `projects.wbs` | - | WBS hierarchy via ipai_ppm |
| PPM | Timesheets | `account.analytic.line` | `hr_timesheet_sheet` | `projects.timesheets` | `wf_timesheet_approval` | Approval workflow |
| PPM | Rate Cards | - | - | `rates.rate_cards`, `rates.rate_entries` | `wf_rate_card_sync` | ipai_rate_card module |
| PPM | Budget Tracking | `crossovered.budget` | `budget_control_sale` | `projects.budgets` | `wf_budget_alert` | Variance alerting |
| PPM | Resource Planning | `resource.resource` | `project_resource_calendar` | `projects.resources` | - | OCA module |
| PPM | Gate Approvals | - | - | `projects.gates` | `wf_gate_approval` | Stage-gate workflow |

### 3.3 HR Domain

| Domain | Process | Odoo Module(s) / Models | OCA Addon(s) | Supabase Schema.Table(s) | n8n / Edge Function Flow(s) | Notes |
|--------|---------|-------------------------|--------------|--------------------------|----------------------------|-------|
| HR | Employee Master | `hr.employee` | - | `core.employees` | `wf_employee_sync` | Odoo → Supabase |
| HR | Departments | `hr.department` | - | `core.departments` | - | CE-native |
| HR | Job Positions | `hr.job` | - | `core.job_positions` | - | CE-native |
| HR | Recruitment | `hr.applicant` | `hr_recruitment_request` | `hr.applicants` | `wf_recruitment_notify` | Notification workflow |
| HR | Time Off | `hr.leave`, `hr.leave.type` | `hr_holidays_public` | `hr.leaves` | `wf_leave_approval` | Public holidays |
| HR | Attendance | `hr.attendance` | - | `hr.attendance` | - | CE-native |
| HR | Appraisals | - | `hr_appraisal`, `hr_evaluation` | `hr.appraisals` | `wf_appraisal_cycle` | OCA module |
| HR | Skills | - | `hr_skills` | `hr.employee_skills` | - | OCA module |

### 3.4 Retail Domain (Scout/SariCoach)

| Domain | Process | Odoo Module(s) / Models | OCA Addon(s) | Supabase Schema.Table(s) | n8n / Edge Function Flow(s) | Notes |
|--------|---------|-------------------------|--------------|--------------------------|----------------------------|-------|
| Retail | POS Sessions | `pos.session` | - | `scout_bronze.pos_sessions` | `wf_pos_session_close` | Transaction capture |
| Retail | POS Orders | `pos.order`, `pos.order.line` | - | `scout_bronze.transactions` | `wf_scout_ingest` | Raw data ingestion |
| Retail | Product Master | `product.product` | - | `scout_dim.products` | `wf_product_sync` | Dimension table |
| Retail | Store Master | `res.partner` (pos config) | - | `scout_dim.stores` | `wf_store_sync` | Dimension table |
| Retail | Sales Analytics | - | - | `scout_silver.*`, `scout_gold.*` | `wf_scout_transform` | Medallion ETL |
| Retail | Brand Performance | - | - | `analytics.brand_performance` | - | Superset dashboards |
| Retail | SariCoach Insights | - | - | `saricoach.*` | `wf_saricoach_generate` | AI-generated insights |

### 3.5 Equipment Domain (Cheqroom Parity)

| Domain | Process | Odoo Module(s) / Models | OCA Addon(s) | Supabase Schema.Table(s) | n8n / Edge Function Flow(s) | Notes |
|--------|---------|-------------------------|--------------|--------------------------|----------------------------|-------|
| Equipment | Asset Registry | `maintenance.equipment` | - | `equipment.assets` | `wf_asset_sync` | ipai_equipment base |
| Equipment | Bookings | - | - | `equipment.bookings` | `wf_booking_notify` | ipai_equipment module |
| Equipment | Check-out/Check-in | - | - | `equipment.checkouts` | `wf_checkout_reminder` | ipai_equipment module |
| Equipment | Maintenance | `maintenance.request` | - | `equipment.maintenance` | `wf_maintenance_schedule` | CE-native |
| Equipment | Utilization | - | - | `equipment.utilization` | `wf_utilization_report` | ipai_equipment_analytics |

### 3.6 Enterprise-Only Delta Notes

#### Delta - Odoo Studio
- **Official docs**: Visual app builder and model editor via Studio (Enterprise)
- **Our stack**: Use OCA `web_*` modules + proper Python/XML module development in `addons/ipai_*`. Use Supabase metadata tables and n8n flows for rapid prototyping. No Studio, no Enterprise.

#### Delta - Documents
- **Official docs**: Enterprise document management with workflows and AI
- **Our stack**: Use Notion for knowledge base + Supabase `doc.*` schema for transactional documents + E1 Data Intake Engine for OCR/parsing. No Enterprise Documents app.

#### Delta - Sign
- **Official docs**: Digital signature collection and workflow
- **Our stack**: Use external e-signature service (DocuSign, local PH providers) with webhook integration to n8n. No Enterprise Sign app.

#### Delta - Helpdesk
- **Official docs**: Enterprise ticketing and support management
- **Our stack**: Use OCA `helpdesk_mgmt` module for ticket management, integrate with Mattermost for real-time notifications.

#### Delta - Planning
- **Official docs**: Resource scheduling and capacity planning
- **Our stack**: Use `ipai_ppm_capacity` module for resource planning, Supabase `projects.resources` for capacity data, Superset for visualization.

#### Delta - Subscriptions
- **Official docs**: Recurring billing and subscription management
- **Our stack**: Use OCA `contract` and `contract_sale` modules for recurring invoicing. MRR/churn analytics in Superset, not Odoo.

#### Delta - Approvals
- **Official docs**: Multi-step approval workflows
- **Our stack**: All approval workflows implemented via n8n with Mattermost notifications. Odoo stores final state only.

#### Delta - Marketing Automation
- **Official docs**: Campaign automation and lead scoring
- **Our stack**: Use n8n for workflow automation, external tools (Mailchimp, etc.) for email campaigns. No Odoo marketing automation.

#### Delta - Knowledge
- **Official docs**: Internal knowledge base and wiki
- **Our stack**: Use Notion as primary knowledge base. Sync to Supabase for AI/RAG access. No Odoo Knowledge app.

---

## 4. Integration Architecture

### 4.1 Data Flow Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACES                                │
│  Odoo Web │ Mattermost │ Superset │ Mobile │ API Clients │ AI Agents   │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────┐
│                         GATEWAY LAYER                                    │
│   Nginx (SSL) │ Supabase Auth │ Edge Functions │ n8n Webhooks           │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────┐
│                       APPLICATION LAYER                                  │
│   Odoo 18 CE/OCA │ n8n Workflows │ Edge Functions │ MCP Server          │
└───────┬────────────────────────┬────────────────────────────┬───────────┘
        │                        │                            │
┌───────▼───────┐     ┌──────────▼──────────┐     ┌──────────▼───────────┐
│  Odoo PostgreSQL  │     │  Supabase PostgreSQL  │     │  Vector Store      │
│  (Local DB)       │     │  (Analytics/AI)       │     │  (pgvector)        │
│  - Transactions   │────▶│  - bronze/silver/gold │     │  - doc chunks      │
│  - Masters        │     │  - RLS enforced       │     │  - embeddings      │
│  - Workflows      │     │  - Multi-tenant       │     │                    │
└───────────────────┘     └─────────────────────────┘     └────────────────────┘
```

### 4.2 Sync Patterns

| Pattern | Direction | Trigger | Implementation |
|---------|-----------|---------|----------------|
| **Master Sync** | Odoo → Supabase | Create/Update in Odoo | n8n webhook → Edge Function |
| **Bulk ETL** | Odoo → Supabase | Scheduled (nightly) | n8n cron → Odoo API → Supabase |
| **Real-time** | Supabase → Odoo | Supabase Realtime | Edge Function → Odoo API |
| **Reconciliation** | Bidirectional | On-demand | n8n workflow with conflict resolution |

### 4.3 InsightPulseAI Integration Call-Outs

Every functional page in this handbook includes:

> **InsightPulseAI Integration:**
> - **Data flows to:** `schema.table(s)`
> - **Used by engines:** `engine_name(s)`
> - **Triggered automations:** `n8n workflow(s)`
> - **AI agents:** `agent_name(s)` (if applicable)

---

## 5. RAG & Chunking Strategy

### 5.1 Document Chunking

| Document Type | Chunk Size | Overlap | Strategy |
|---------------|------------|---------|----------|
| Handbook pages | 1500 tokens | 200 tokens | Section-based splitting |
| API documentation | 1000 tokens | 150 tokens | Function/endpoint based |
| Code examples | 500 tokens | 100 tokens | Preserve code blocks |
| Configuration guides | 1200 tokens | 150 tokens | Step-based splitting |
| Error messages | 300 tokens | 50 tokens | Single-message chunks |

### 5.2 Metadata Schema

Every chunk includes:

```json
{
  "doc_id": "uuid",
  "chunk_id": "uuid",
  "domain": "finance|hr|ppm|retail|equipment|devops",
  "module": "account|project|hr_expense|pos|...",
  "stack_layer": "odoo|supabase|n8n|ai|infra",
  "persona": "finance_user|hr_admin|developer|devops|analyst",
  "doc_type": "guide|reference|tutorial|troubleshooting",
  "version": "18.0",
  "ce_oca_only": true,
  "has_code_example": true,
  "keywords": ["invoice", "payment", "reconciliation"],
  "parent_section": "1.3 Customer Invoicing Workflow",
  "created_at": "2025-12-07T00:00:00Z",
  "updated_at": "2025-12-07T00:00:00Z"
}
```

### 5.3 Agent Query Patterns

| Agent Persona | Primary Query Focus | Metadata Filters |
|---------------|---------------------|------------------|
| **Odoo Developer** | Module development, OCA patterns | `stack_layer=odoo`, `doc_type=reference` |
| **Finance SSC Expert** | Accounting workflows, expense mgmt | `domain=finance`, `persona=finance_user` |
| **DevOps Engineer** | Deployment, CI/CD, Docker | `stack_layer=infra`, `domain=devops` |
| **PPM Analyst** | Project tracking, budgets, reports | `domain=ppm`, `persona=analyst` |
| **Retail Intel Agent** | Scout data, SariCoach | `domain=retail`, `module=pos` |
| **HR Coach** | Employee data, leave, appraisals | `domain=hr`, `persona=hr_admin` |

### 5.4 Embedding Strategy

- **Model**: OpenAI `text-embedding-3-small` (1536 dimensions)
- **Storage**: Supabase pgvector in `rag.doc_chunks`
- **Index**: HNSW index for fast similarity search
- **Refresh**: Incremental on commit, full rebuild on major version

### 5.5 Retrieval Configuration

```sql
-- Example retrieval query
SELECT
  dc.content,
  dc.metadata,
  1 - (dc.embedding <=> query_embedding) as similarity
FROM rag.doc_chunks dc
WHERE
  dc.metadata->>'domain' = 'finance'
  AND dc.metadata->>'ce_oca_only' = 'true'
ORDER BY dc.embedding <=> query_embedding
LIMIT 5;
```

---

## 6. Governance & Guidelines

### 6.1 Smart Delta Rules

All documentation must follow the same gating as code:

```
Documentation Request
    │
    ▼
1. STOCK_ODOO_DOCS – Is it already covered by official Odoo 18 docs?
    │ YES → Link to official docs, add delta notes only
    │ NO
    ▼
2. OCA_DOCS – Is there OCA documentation for this module?
    │ YES → Link to OCA, add integration notes
    │ NO
    ▼
3. IPAI_DOCS – Write new documentation for ipai_* modules
    │
    ▼
4. STACK_DOCS – Document Supabase/n8n/AI integration patterns
```

### 6.2 Documentation Template

Every module documentation page must include:

1. **Overview & Purpose**
2. **Related Domain Engine(s)**
3. **Data Models** (core tables, key fields, tenant_id behaviour)
4. **User Roles & Permissions**
5. **Key Workflows** (step-by-step)
6. **Integrations**
   - Supabase tables/views
   - Edge Functions / n8n workflows
   - AI agents/tools (if any)
7. **"Delta from Official Odoo Docs"** note
8. **Known Limitations / Phase 2+ items**

### 6.3 Version Control

- Documentation lives in `docs/odoo-18-handbook/`
- Changes require PR review
- Version tags match Odoo module versions
- Breaking changes require handbook version bump

### 6.4 Quality Checklist

Before merging any documentation:

- [ ] No Enterprise/IAP features documented without delta notes
- [ ] All Supabase schema references verified
- [ ] n8n workflow names match actual implementations
- [ ] Code examples tested on CE 18.0
- [ ] RAG metadata tags applied
- [ ] Cross-references to official docs included

---

## Related Documents

| Document | Location |
|----------|----------|
| CE/OCA Mapping | [ODOO18_ENTERPRISE_TO_CE_OCA_MAPPING.md](../ODOO18_ENTERPRISE_TO_CE_OCA_MAPPING.md) |
| Constitution | [constitution.md](../../constitution.md) |
| Technical Architecture | [INSIGHTPULSEAI_TECHNICAL_ARCHITECTURE.md](../architecture/INSIGHTPULSEAI_TECHNICAL_ARCHITECTURE.md) |
| Enterprise Feature Gap | [ENTERPRISE_FEATURE_GAP.yaml](../ENTERPRISE_FEATURE_GAP.yaml) |
| Implementation Plan | [plan.md](../../plan.md) |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-07 | Initial handbook release |

---

**Sources:**
- [Odoo 18.0 Documentation](https://www.odoo.com/documentation/18.0/)
- [Odoo Applications](https://www.odoo.com/documentation/18.0/applications.html)
- [Odoo Developer Guide](https://www.odoo.com/documentation/18.0/developer.html)
- [Odoo Enterprise vs Community](https://www.odoo.com/page/editions)
