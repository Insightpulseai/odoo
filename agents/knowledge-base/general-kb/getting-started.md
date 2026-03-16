---
title: "Getting Started with InsightPulse AI"
kb_scope: "general-kb"
group_ids: ["group-guid-placeholder"]
last_updated: "2026-03-15"
---

# Getting Started with InsightPulse AI

## Welcome

This guide walks you through the onboarding process for InsightPulse AI's Odoo on Cloud platform, from initial contact through production go-live. Each phase has clear deliverables and milestones.

---

## Phase 1: Discovery and Demo

### Requesting a Demo

Contact the InsightPulse AI team through any of these channels:

- **Email**: sales@insightpulseai.com
- **Website**: insightpulseai.com/demo (fill out the request form)
- **Slack**: Request access to the InsightPulse AI community workspace

### What to Prepare for the Demo

To make the most of your demo session, prepare the following:

1. **Business Overview**: Brief description of your company, industry, and team size.
2. **Current Systems**: List of software currently in use (accounting, CRM, inventory, etc.).
3. **Pain Points**: Top 3-5 challenges you want to solve.
4. **Compliance Needs**: BIR filing requirements, multi-company structure, industry regulations.
5. **Integration Requirements**: Systems that need to connect with the ERP (banks, marketplaces, email).

### Demo Session

The demo is a 60-minute live session covering:

- Platform walkthrough tailored to your industry
- Module-specific deep dives based on your priorities
- Philippine localization features (BIR compliance, local payment methods)
- Copilot demonstration with live queries
- Q&A on pricing, timeline, and data migration

---

## Phase 2: Trial

### Trial Terms

- **Duration**: 14 days, extendable upon request
- **Access**: Full platform access on a dedicated trial instance
- **Data**: Pre-loaded with sample data for your industry
- **Users**: Up to 5 users during trial
- **Support**: Email support with 24-hour response time during trial

### Trial Instance Setup

Within 24 hours of trial approval, you receive:

1. **Trial URL**: `<your-company>.trial.insightpulseai.com`
2. **Admin Credentials**: Sent via secure link (expires in 24 hours)
3. **Quick Start Guide**: Industry-specific setup checklist
4. **Sample Data**: Pre-loaded chart of accounts, products, customers, and sample transactions

### What to Evaluate During Trial

Use this checklist to evaluate the platform systematically:

**Accounting and Finance**
- [ ] Review the Philippine chart of accounts
- [ ] Create a sample customer invoice
- [ ] Process a sample vendor bill
- [ ] Run a trial balance report
- [ ] Test bank reconciliation with sample data
- [ ] Generate a BIR 2550M computation

**Sales and CRM**
- [ ] Create a lead and convert to opportunity
- [ ] Generate a quotation and convert to sales order
- [ ] Review pipeline stages and kanban view
- [ ] Test email integration for lead capture

**Inventory (if applicable)**
- [ ] Review warehouse configuration
- [ ] Process a sample receipt and delivery
- [ ] Check reorder rules and stock alerts
- [ ] Test barcode scanning (mobile browser)

**Copilot**
- [ ] Try natural language queries on sample data
- [ ] Test Advisory Mode for report generation
- [ ] Explore context-aware suggestions in form views

**General**
- [ ] Evaluate the user interface and navigation
- [ ] Test on mobile devices (responsive design)
- [ ] Review user roles and access control
- [ ] Check email notification templates

---

## Phase 3: Onboarding

Once you decide to proceed, onboarding begins. The process is structured into workstreams that can run in parallel.

### Onboarding Timeline

| Week | Activity | Deliverable |
|------|----------|------------|
| 1 | Kickoff + requirements finalization | Signed requirements document |
| 2-3 | Data migration preparation | Migration scripts + validation report |
| 3-4 | Configuration and customization | Configured production instance |
| 4-5 | User acceptance testing (UAT) | UAT sign-off |
| 5-6 | Training | Trained users |
| 6 | Go-live + hypercare | Production system live |

### Workstream 1: Data Migration

#### Supported Migration Sources

| Source System | Migration Path | Complexity |
|-------------|---------------|-----------|
| Excel / CSV | Direct import via Odoo import tool | Low |
| QuickBooks | Export to CSV, map to Odoo fields | Medium |
| SAP Business One | Custom export scripts + Odoo import | High |
| Xero | API export + transformation | Medium |
| Another Odoo instance | Database-level migration | Low-Medium |
| Custom / Legacy ERP | Assess per case | Variable |

#### Data Migration Checklist

| Data Type | Priority | Notes |
|-----------|----------|-------|
| Chart of Accounts | Critical | Map to Philippine COA template |
| Customer Master | Critical | Include TIN, addresses, payment terms |
| Vendor Master | Critical | Include TIN, bank details, payment terms |
| Product Catalog | Critical | SKUs, categories, pricing, stock levels |
| Opening Balances | Critical | As of cutover date |
| Open Invoices | High | AR and AP balances at cutover |
| Historical Transactions | Medium | Recommended: last 2 fiscal years |
| Employee Records | High | For HR module users |
| Fixed Assets | Medium | Current book values and depreciation schedules |
| Sales History | Medium | For pipeline and analytics |

#### Migration Approach

1. **Extract**: Pull data from source system in CSV or Excel format.
2. **Transform**: Map source fields to Odoo fields using provided templates.
3. **Validate**: Run validation scripts to check data quality (duplicates, missing fields, format issues).
4. **Load**: Import into staging database for review.
5. **Verify**: Compare record counts and totals between source and Odoo.
6. **Cutover**: Final import into production on go-live day.

### Workstream 2: Configuration

#### Company Setup

1. **Company Information**: Name, TIN, address, logo, fiscal year
2. **Chart of Accounts**: Start with Philippine template, customize as needed
3. **Tax Configuration**: VAT rates, withholding tax types, tax groups
4. **Payment Methods**: Bank accounts, GCash, Maya, check, cash
5. **Currencies**: PHP as base, USD/EUR for international transactions
6. **Fiscal Positions**: Domestic, export, tax-exempt mapping rules

#### Module Configuration

Each module is configured according to your requirements document:

- **Accounting**: Journal setup, payment terms, bank feeds, recurring entries
- **Sales**: Pipeline stages, quotation templates, pricing rules, discount policies
- **Purchasing**: Vendor approval workflow, purchase agreement types, procurement rules
- **Inventory**: Warehouse locations, routes, reorder rules, barcode format
- **Manufacturing**: Work centers, routing, BOM structure, quality checks
- **HR**: Department structure, leave types, expense categories, approval chains

#### User Setup

1. **User Accounts**: Create accounts for all users
2. **Role Assignment**: Map organizational roles to Odoo groups
3. **Company Access**: Configure multi-company access if applicable
4. **Email Configuration**: Connect user email for notifications
5. **Two-Factor Authentication**: Enable TOTP for admin and finance users

### Workstream 3: Customization

If standard configuration does not meet a requirement, customization options are:

| Level | Scope | Examples | Timeline |
|-------|-------|---------|----------|
| Configuration | Odoo built-in settings | Fields, views, reports, email templates | Days |
| OCA Module | Install community module | Advanced reconciliation, budget management | Days |
| IPAI Extension | Custom module development | Industry-specific workflows, integrations | Weeks |
| Integration | External system connection | Bank feeds, marketplace sync, payment gateway | Weeks |

---

## Phase 4: Training

### Training Program

Training is delivered in role-based sessions:

| Session | Audience | Duration | Topics |
|---------|----------|----------|--------|
| Admin Training | System administrators | 4 hours | User management, configuration, backup, security |
| Accounting Training | Finance team | 8 hours (2 sessions) | Journal entries, invoicing, reconciliation, BIR reports |
| Sales Training | Sales team | 4 hours | CRM, quotations, orders, pipeline management |
| Inventory Training | Warehouse team | 4 hours | Stock moves, receipts, deliveries, barcode scanning |
| Copilot Training | All users | 2 hours | Advisory queries, Action Mode, best practices |
| HR Training | HR team | 4 hours | Employee records, leave management, expenses |

### Training Format

- **Live Sessions**: Conducted via video call or on-site (Metro Manila)
- **Hands-On**: Each session includes practical exercises on your configured instance
- **Recording**: All sessions are recorded and available for replay
- **Materials**: User guides and quick reference cards provided

### Self-Service Resources

After training, users have access to:

- In-app Copilot for real-time assistance
- Knowledge base articles (this document set)
- Video tutorials for common workflows
- Slack community channel for peer support

---

## Phase 5: Go-Live

### Go-Live Checklist

**Pre-Go-Live (1 week before):**
- [ ] UAT sign-off from all department heads
- [ ] Final data migration rehearsal completed
- [ ] All users created and tested login
- [ ] Email and notification templates verified
- [ ] Backup and disaster recovery tested
- [ ] Performance testing completed
- [ ] BIR compliance reports validated
- [ ] Integration endpoints verified (bank feeds, email, Slack)

**Go-Live Day:**
- [ ] Final data cutover from legacy system
- [ ] Opening balances verified and reconciled
- [ ] All integrations activated
- [ ] Users notified and access confirmed
- [ ] Support team on standby

**Post-Go-Live (hypercare period, 2 weeks):**
- [ ] Daily check-in calls with key users
- [ ] Priority support channel active (4-hour response)
- [ ] Issue tracking and resolution log maintained
- [ ] Performance monitoring active
- [ ] First BIR filing cycle completed successfully

### Cutover Strategy

The recommended cutover strategy depends on your situation:

**Big Bang**: Switch all modules simultaneously on a single date.
- Best for: Small teams (under 10 users), simple configurations
- Risk: Higher, but shorter transition period

**Phased**: Roll out modules sequentially (Accounting first, then Sales, then Inventory).
- Best for: Larger teams, complex configurations, risk-averse organizations
- Risk: Lower per phase, but longer total timeline

**Parallel Run**: Run old and new systems simultaneously for 1 month.
- Best for: High-risk environments, regulatory requirements
- Risk: Lowest, but highest effort (dual data entry)

---

## Phase 6: Ongoing Support

### Support Channels

| Channel | Response Time | Availability |
|---------|:------------:|:------------:|
| Email (support@insightpulseai.com) | Per SLA tier | Business hours |
| Slack (#support channel) | Best effort | Business hours |
| Copilot (in-app) | Instant | 24/7 |
| Emergency Hotline | 1 hour | 24/7 (Enterprise tier) |

### Maintenance Schedule

- **Security Patches**: Applied within 48 hours of release
- **OCA Updates**: Monthly, after regression testing
- **Platform Updates**: Bi-weekly, with release notes
- **Major Version Upgrades**: Annual, with migration assistance

### Continuous Improvement

After go-live, the platform evolves with your business:

- **Monthly Review**: Usage analytics and optimization recommendations
- **Quarterly Planning**: Feature requests and roadmap alignment
- **Annual Health Check**: Full system audit, performance tuning, security review

---

## Frequently Asked Questions

**Q: How long does the full onboarding take?**
A: Typically 4-6 weeks from kickoff to go-live. Complex implementations with extensive data migration or custom development may take 8-12 weeks.

**Q: Can I migrate data myself?**
A: Yes. We provide templates and validation scripts. Self-service migration is supported for CSV/Excel sources. We handle complex migrations (API-based, database-level).

**Q: What if I need a module that is not included?**
A: We evaluate OCA modules first (200+ available for Odoo 19.0). If no OCA module fits, we develop a custom `ipai_*` module. Custom development is scoped and quoted separately.

**Q: Is training included in the subscription?**
A: Initial training is included. Additional training sessions are available at the Business and Enterprise tiers.

**Q: What happens to my data if I cancel?**
A: You receive a full database export (PostgreSQL dump) and file storage archive. Data is retained for 30 days after cancellation, then permanently deleted.

**Q: Can I run Odoo on my own infrastructure?**
A: Yes. The Odoo CE software is open source. We can assist with on-premise deployment, though managed cloud is recommended for optimal performance and support.
