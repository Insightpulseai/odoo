---
title: "InsightPulse AI Product Offerings"
kb_scope: "general-kb"
group_ids: ["group-guid-placeholder"]
last_updated: "2026-03-15"
---

# InsightPulse AI Product Offerings

## Company Overview

InsightPulse AI provides AI-augmented business management solutions built on open-source foundations. The platform combines Odoo Community Edition with AI capabilities, workflow automation, and Philippine-localized compliance features to deliver enterprise-grade solutions without enterprise-grade licensing costs.

**Target Market**: Small-to-medium enterprises (SMEs) in the Philippines and Southeast Asia.

**Core Philosophy**: Open source first. AI augmented. Compliance built-in.

---

## Product Portfolio

### 1. Odoo on Cloud

**The core ERP platform.**

Odoo on Cloud is a fully managed deployment of Odoo CE 18.0 enhanced with 56+ OCA modules and custom InsightPulse AI extensions. It runs on Azure Container Apps with enterprise-grade infrastructure.

**What's Included:**

| Capability | Details |
|-----------|---------|
| Accounting & Finance | Double-entry accounting, bank reconciliation, financial reporting, asset management, budget tracking |
| Sales & CRM | Lead management, pipeline tracking, quotations, sales orders, pricing rules |
| Purchasing | Purchase orders, vendor management, procurement automation, RFQ workflow |
| Inventory | Multi-warehouse management, stock moves, barcode support, reorder rules |
| Manufacturing | Bill of materials, work orders, production planning, quality control |
| HR & Payroll | Employee management, leave tracking, expense management, org charts |
| Project Management | Tasks, timesheets, Gantt charts, project billing |
| Website & eCommerce | CMS, product catalog, online payments, SEO tools |
| Reporting | MIS Builder, financial reports, Excel export, pivot analysis |

**Philippine Localization:**
- BIR-compliant chart of accounts
- Automated tax computation (VAT, EWT, FWT)
- BIR form generation (2550M, 2550Q, 1601-C, 2316, 1604-CF, 1604-E)
- Philippine payment methods (GCash, Maya, bank transfer, check)
- BSP exchange rate integration

**Pricing Tiers:**

| Tier | Users | Modules | Support | Price |
|------|-------|---------|---------|-------|
| Starter | Up to 5 | Core (Accounting, Sales, CRM, Inventory) | Email, 48hr SLA | Contact sales |
| Business | Up to 25 | Full suite | Email + Slack, 24hr SLA | Contact sales |
| Enterprise | Unlimited | Full suite + custom modules | Dedicated support, 4hr SLA | Contact sales |

---

### 2. Copilot

**AI assistant for Odoo.**

The Copilot brings natural language interaction to the Odoo interface, allowing users to query data, generate reports, and execute actions through conversation.

**Key Features:**

- **Natural Language Queries**: Ask questions in English or Filipino about any business data in Odoo.
- **Advisory Mode**: Read-only data access for safe exploration and reporting.
- **Action Mode**: Execute Odoo operations through natural language commands with confirmation safeguards.
- **Context Awareness**: Understands your current screen, role, and company context.
- **Inline Assistance**: Field-level help and suggestions in form views.
- **Report Generation**: Create ad-hoc reports from natural language descriptions.

**Use Cases by Role:**

| Role | Example Queries |
|------|----------------|
| CFO | "Show me cash flow summary for Q1 2026 across all companies" |
| Accountant | "List all unreconciled bank transactions for BDO account" |
| Sales Manager | "What is our win rate by sales channel this quarter?" |
| Warehouse Staff | "Which products in Manila warehouse are below reorder point?" |
| HR Manager | "Show leave balances for all employees expiring this year" |
| CEO | "Compare revenue this month vs same month last year" |

**Integration Points:**
- Accessible from any Odoo view
- Keyboard shortcut activation
- Slack integration for query-via-chat
- API access for programmatic queries

---

### 3. Analytics (Superset BI)

**Business intelligence and dashboarding.**

The Analytics product is powered by Apache Superset, connected to the Odoo PostgreSQL database for real-time business intelligence.

**Capabilities:**

- **Pre-built Dashboards**: Ready-to-use dashboards for finance, sales, inventory, and HR.
- **Custom Visualizations**: Build charts, tables, pivot tables, and geographic maps.
- **SQL Lab**: Direct SQL access for advanced analysts (read-only, sandboxed).
- **Scheduled Reports**: Automated report generation and email delivery.
- **Embedded Analytics**: Embed dashboards into Odoo views or external portals.
- **Row-Level Security**: Data access filtered by user role and company.

**Pre-built Dashboard Templates:**

| Dashboard | Metrics Included |
|-----------|-----------------|
| Financial Overview | Revenue, expenses, profit margin, cash position, AR/AP aging |
| Sales Performance | Pipeline value, conversion rates, revenue by product/channel, quota attainment |
| Inventory Health | Stock levels, turnover rate, dead stock, reorder alerts |
| Customer Analytics | Customer lifetime value, acquisition cost, retention rate, segment analysis |
| HR Summary | Headcount, turnover, leave utilization, department distribution |
| BIR Compliance | Tax liabilities by type, filing status, upcoming deadlines |

**Access**: `superset.insightpulseai.com` (SSO via Keycloak)

---

### 4. Ops Console

**Platform operations and monitoring.**

The Ops Console provides visibility into the health and performance of the entire InsightPulse AI platform.

**Features:**

- **Service Health Dashboard**: Real-time status of all platform services (Odoo, Keycloak, Superset, n8n, OCR).
- **Log Aggregation**: Centralized log viewing with search and filter.
- **Performance Metrics**: Response times, error rates, database query performance.
- **Alerting**: Slack and email notifications for service degradation or outages.
- **Deployment History**: Track deployments, rollbacks, and configuration changes.
- **User Activity**: Login patterns, active sessions, feature usage analytics.

**Incident Response Integration:**
- Automated incident detection based on error rate thresholds
- Slack channel creation for incident triage
- Runbook linking for common failure scenarios
- Post-incident report generation

---

### 5. Document Processing (OCR)

**Automated document extraction.**

The OCR service processes business documents (invoices, receipts, BIR forms) and extracts structured data for import into Odoo.

**Supported Document Types:**

| Document Type | Extracted Fields |
|--------------|-----------------|
| Supplier Invoices | Vendor name, invoice number, date, line items, tax amounts, total |
| Official Receipts | OR number, date, amount, TIN, address |
| BIR Forms | Form type, period, tax amounts, TIN |
| Purchase Orders | PO number, vendor, line items, quantities, prices |
| Delivery Receipts | DR number, items, quantities, condition notes |
| Bank Statements | Transaction date, description, debit/credit amounts, running balance |

**Processing Pipeline:**
1. Upload document (PDF, image, or scan) via Odoo interface or API
2. OCR engine extracts text and structure
3. AI model maps extracted data to Odoo fields
4. User reviews and confirms the extracted data
5. Record is created in Odoo (invoice, bill, or journal entry)

**Accuracy**: 95%+ for printed documents, 85%+ for handwritten amounts. Always requires human review before posting.

---

### 6. Workflow Automation (n8n)

**Cross-system integration engine.**

The n8n workflow engine connects Odoo with external systems for automated business processes.

**Pre-built Workflows:**

| Workflow | Trigger | Action |
|----------|---------|--------|
| Invoice Notification | Invoice posted in Odoo | Send PDF via email + Slack notification |
| Lead Capture | Form submission on website | Create lead in Odoo CRM + assign to team |
| Payment Reminder | Invoice overdue by 7/14/30 days | Send graduated reminder emails |
| Stock Alert | Product below reorder point | Create purchase order + notify purchasing team |
| BIR Filing Reminder | 5 days before filing deadline | Slack alert to accounting team |
| Expense Approval | Expense report submitted | Route to manager via Slack for approval |
| Customer Onboarding | New customer created | Send welcome email + create project + schedule kickoff |

**Custom Workflow Development:**
- Visual workflow builder at `n8n.insightpulseai.com`
- 400+ pre-built integrations (Slack, Gmail, Google Sheets, Stripe, etc.)
- Webhook endpoints for external triggers
- Scheduled execution for recurring tasks

---

## Supported Industries

### Professional Services
- Time and material billing
- Project profitability tracking
- Resource allocation and capacity planning
- Client portal for project visibility
- Retainer and subscription billing

### Retail and Distribution
- Multi-location inventory management
- Point-of-sale integration
- Landed cost calculation
- Batch and serial number tracking
- Drop-shipping and cross-docking

### Manufacturing
- Multi-level bill of materials
- Work center capacity planning
- Quality control checkpoints
- Subcontracting management
- Production cost analysis

### Real Estate and Property Management
- Lease management and billing
- Tenant communication portal
- Maintenance request tracking
- Property financial reporting
- Common area expense allocation

### Healthcare Clinics
- Patient record management
- Appointment scheduling
- Billing and insurance claims
- Inventory tracking for medical supplies
- Compliance documentation

### Education
- Student information system
- Fee collection and tracking
- Course and class scheduling
- Parent communication portal
- Financial aid management

---

## Integration Ecosystem

The platform integrates with common Philippine business systems:

| System | Integration Type | Purpose |
|--------|-----------------|---------|
| BDO / BPI / Metrobank | Bank feed import | Automated bank reconciliation |
| GCash / Maya | Payment gateway | Online payment collection |
| Lazada / Shopee | Marketplace sync | Order and inventory sync |
| Slack | Real-time messaging | Notifications and approvals |
| Google Workspace | Email and calendar | Communication and scheduling |
| Zoho Mail | Transactional email | Invoice delivery and notifications |

---

## Service Level Agreements

| Metric | Starter | Business | Enterprise |
|--------|---------|----------|-----------|
| Uptime | 99.5% | 99.9% | 99.95% |
| Support Response | 48 hours | 24 hours | 4 hours |
| Data Backup | Daily | Daily | Continuous |
| Disaster Recovery | 24 hours RPO | 4 hours RPO | 1 hour RPO |
| Training | Self-service docs | 2 sessions/month | Unlimited |

---

## Getting Started

1. **Request a Demo**: Contact sales@insightpulseai.com or fill out the form at insightpulseai.com/demo
2. **Trial**: 14-day full-access trial on a dedicated instance
3. **Onboarding**: Guided setup with data migration assistance
4. **Go Live**: Production deployment with monitoring and support

See the Getting Started guide for detailed onboarding steps.
