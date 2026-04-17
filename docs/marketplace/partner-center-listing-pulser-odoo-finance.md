# Partner Center Listing — Pulser for Odoo: Finance Operations & Compliance Control Tower

> Source of truth for the Microsoft commercial marketplace submission.
> All fields map directly to Partner Center offer configuration tabs.
> Maintained by: Jake Tolentino — jake.tolentino@insightpulseai.com

---

## Offer Identification

| Field | Value |
|---|---|
| **Offer name** | Pulser for Odoo — Finance Operations & Compliance Control Tower |
| **Offer alias** | pulser-odoo-finance-control-tower |
| **Publisher** | Dataverse IT Consultancy / InsightPulseAI |
| **Offer type** | Transactable SaaS |
| **Product category** | Finance & Accounting |
| **Industry (primary)** | Financial Services |
| **Industry (secondary)** | Professional Services |
| **Solution area** | Business Applications — Finance & Accounting |
| **Website** | https://www.insightpulseai.com/ |

---

## Contacts

| Role | Name | Email |
|---|---|---|
| **Engineering / submission contact** | Jake Tolentino | jake.tolentino@insightpulseai.com |
| **Support / general** | InsightPulseAI Support | admin@insightpulseai.com |

---

## Search Result Summary

> 255 characters max. Used in marketplace search results and category browse listings.

AI-powered Finance Operations & Compliance Control Tower for Odoo CE — automates month-end close, BIR tax filings, AP/AR collections, and cash flow forecasting on Azure. No Odoo Enterprise license required.

---

## Short Description

> 500 characters max. Shown on the offer tile and summary pane.

Pulser for Odoo brings an AI copilot to your Finance operations. Automate month-end close checklists, generate BIR-compliant tax reports, surface AR aging and AP liabilities in a single dashboard, and receive cash flow forecasts — all inside your self-hosted Odoo CE instance on Azure. Built for Philippine SMEs and regional professional services firms. No Odoo Enterprise license required.

---

## Long Description

> Full HTML/markdown body rendered in the offer detail page. Recommended 3,000–5,000 characters.

**Pulser for Odoo — Finance Operations & Compliance Control Tower** is an AI-augmented finance operations layer for organizations running Odoo Community Edition on Azure. It replaces manual month-end close coordination, fragmented BIR filing workflows, and siloed cash visibility with a structured, agent-assisted control plane.

### What It Does

Pulser extends Odoo CE's native accounting stack with four coordinated capability layers:

- **Month-End Close Automation** — Structured close checklist, automated journal reconciliation, period-lock enforcement, and Pulser-assisted exception triage. Close cycles that previously took 3–5 days are reduced to a single supervised workflow.
- **BIR Compliance Pack (Philippine Tax)** — Automated generation of BIR Form 2307 (Expanded Withholding Tax certificate), VAT summary schedules, and eFPS/eBIRForms-ready export packages. Designed for BIR Revenue Regulations 11-2018 and TRAIN Law compliance.
- **AR Collections Intelligence** — Aging bucket dashboards, overdue escalation workflows, dunning letter automation via Odoo's native mail server, and a Pulser-assisted collections recommendation feed.
- **Cash Flow Forecasting** — Rolling 30/60/90-day cash projection using live AP and AR ledger data, payroll accruals, and configurable forecast scenarios. Delivered as a Power BI-embedded panel inside the Odoo Finance menu.

### Built on Odoo CE + OCA + Azure

No Odoo Enterprise license is required. The stack is:

- **Odoo CE 18.0** — Core ERP transaction layer (GL, AP, AR, Payroll)
- **OCA modules** — Account Accountant, Account Payment Order, Account Financial Report, and related community extensions
- **Thin `ipai_*` delta modules** — Only for BIR-specific fields, Pulser middleware integration, and Azure Key Vault credential binding
- **Azure Container Apps** — Odoo runtime, behind Azure Front Door with WAF
- **Azure AI Foundry** — Pulser agent runtime (gpt-4.1, keyless Managed Identity auth)
- **Power BI** — Finance dashboards and cash flow visualization

### Who It Is For

Pulser for Odoo Finance targets:

- **SMEs in the Philippines** running Odoo for accounting who need BIR compliance automation and do not want to pay Odoo Enterprise pricing
- **Regional professional services firms** (consulting, IT services, creative agencies) that need project-linked finance close and utilization-to-revenue reconciliation
- **Finance controllers and CFOs** who want AI-assisted exception triage and a single consolidated close dashboard without switching ERP systems
- **IT decision-makers** evaluating D365 Finance or SAP Business One who need a lower-cost, Azure-native alternative with comparable Finance module coverage

### Key Differentiators

- **CE + OCA parity target** — 80%+ D365 Finance functional parity without Enterprise licensing fees
- **Philippine BIR-native** — BIR Form 2307, TRAIN Law VAT schedules, eFPS/eBIRForms export built in
- **Azure-native, no hybrid dependencies** — No Supabase, no n8n, no Cloudflare. Fully Azure DNS + ACA + Front Door + Key Vault
- **Policy-gated Pulser AI** — Mutating finance actions (period lock, journal post, BIR submission package) require explicit approval; read-only recommendations run approval-free
- **Self-hosted control** — Customer owns the Odoo instance and PostgreSQL database; Pulser runs as a sidecar agent, not a cloud-hosted SaaS that controls your ERP data
- **Open source core** — Odoo CE + OCA modules are MIT/LGPL licensed; only the `ipai_*` delta layer is proprietary

---

## Value Proposition Bullets

1. Cut month-end close cycle time by automating checklist tracking, journal reconciliation, and period-lock enforcement inside Odoo CE.
2. Generate BIR-compliant Form 2307, VAT summary schedules, and eFPS-ready packages without manual spreadsheet assembly.
3. Surface AR aging, AP liabilities, and vendor payment status in a single Finance dashboard — no separate BI tool required for day-to-day operations.
4. Receive rolling 30/60/90-day cash flow forecasts derived from live Odoo ledger data, with scenario override capability.
5. Run a policy-gated AI copilot that recommends close exceptions and collections actions — without autonomously mutating your financial records.
6. Deploy entirely on Azure (ACA + PostgreSQL + Front Door) with no Odoo Enterprise license, no proprietary cloud ERP lock-in, and customer-owned data.

---

## Customer Problems Solved

1. **Manual, error-prone month-end close** — Finance teams spend days chasing journal entries, reconciliation exceptions, and sign-off confirmations across email threads. Pulser replaces this with a structured, tracked close workflow inside Odoo.
2. **BIR filing complexity** — Philippine BIR Form 2307 and VAT schedules require data from multiple Odoo modules. Manual extraction into Excel introduces errors and audit risk. Pulser automates the extraction and formats output for eFPS/eBIRForms submission.
3. **Fragmented cash visibility** — AR aging, AP due dates, and payroll accruals live in separate Odoo menus with no consolidated forward-looking view. Pulser aggregates these into a single cash flow forecast panel.
4. **No affordable path from spreadsheets to ERP compliance** — Philippine SMEs cannot justify Odoo Enterprise or D365 Finance pricing. Pulser on Odoo CE provides comparable Finance module coverage at a fraction of the cost.
5. **AI tools that mutate records without approval** — Finance controllers distrust AI copilots that autonomously post journals or lock periods. Pulser's policy-gated model ensures AI only recommends; humans approve.
6. **Vendor and customer payment relationship risk** — Overdue AR and stalled AP create cash flow surprises. Pulser's collections intelligence and payment recommendation feeds surface these proactively, before they become write-offs.

---

## Target Customers

- Philippine SMEs (50–500 employees) using Odoo CE for accounting, payroll, and project billing
- Regional professional services firms in Southeast Asia with multi-entity or project-based revenue
- Mid-market IT services companies evaluating Microsoft Dynamics 365 Finance or SAP Business One alternatives
- Finance controllers and CFOs at growth-stage companies who need compliance automation without ERP re-platforming
- Odoo implementation partners and managed service providers who want to add a Pulser AI layer to existing Odoo CE deployments

### Buyer Personas

| Persona | Title | Primary Pain | Decision Trigger |
|---|---|---|---|
| **Finance Controller** | Finance Controller / Head of Finance | Month-end close takes too long; BIR filing is manual | Audit finding or BIR notice |
| **CFO** | CFO / VP Finance | No forward-looking cash view; D365 too expensive | Board pressure for cash visibility |
| **IT Decision-Maker** | CTO / IT Manager | Odoo CE gaps vs. Enterprise; Azure-native requirement | License renewal or cloud migration |
| **Odoo Partner** | Odoo Implementation Partner | Clients asking for AI layer; no off-the-shelf option | Client RFP or competitive displacement |

---

## Geographic Availability

| Region | Priority | Notes |
|---|---|---|
| Philippines | P0 — primary | BIR compliance pack targets PH tax law |
| Indonesia | P1 | VAT compliance demand; Odoo CE footprint |
| Malaysia | P1 | GST/SST compliance potential |
| Singapore | P2 | Professional services concentration |
| Rest of ASEAN | P3 | On-demand partner-led |
| Australia / NZ | P3 | OCA-based accounting parity |

---

## Commercial Model

| Field | Value |
|---|---|
| **Offer type** | Transactable SaaS |
| **Commercial model** | Per-seat subscription (Finance module users) + optional implementation tier |
| **Pricing model (placeholder)** | USD 49/user/month (Finance seat) — subject to Partner Center pricing tool finalization |
| **Free trial** | 30-day trial on shared demo tenant (no credit card required) |
| **Metering** | Azure Marketplace metering API — monthly active Finance users |
| **Private offer** | Available for enterprise and partner-resell agreements |

> Note: Pricing is a placeholder. Final price points will be set in the Partner Center Pricing & Availability tab after GTM review. The $49/user/month placeholder is directionally aligned with the lower bound of D365 Finance Essentials pricing to maintain competitive positioning.

---

## Service Description / Included Components

The following is included in every Pulser for Odoo Finance subscription:

- **Pulser Finance Agent** — AI copilot middleware running on Azure AI Foundry (gpt-4.1, Managed Identity auth), integrated into Odoo via the `ipai_finance_*` module layer
- **Month-End Close Module** (`ipai_finance_close`) — Close checklist, journal reconciliation engine, period-lock gating, exception triage feed
- **BIR Compliance Pack** (`ipai_bir_2307`, `ipai_bir_2307_automation`, `ipai_finance_tax`) — BIR Form 2307 generation, VAT schedule automation, eFPS/eBIRForms export
- **AR Collections Module** (`ipai_ar_collections`, `ipai_finance_ap_ar`) — Aging dashboards, dunning automation, collections recommendation feed
- **Cash Flow Module** (`ipai_finance_cash`) — Rolling 30/60/90-day forecast, scenario override, Power BI-embedded panel
- **FP&A Foundation** (`ipai_finance_fpa`) — Budget-vs-actual, analytic account mapping, department-level P&L
- **Azure deployment baseline** — ACA container definition, Front Door WAF policy, Key Vault secret bindings, Bicep IaC modules
- **Onboarding playbook** — Odoo CE baseline verification, OCA module installation, Pulser agent wiring, demo data load

---

## Optional Add-Ons

| Add-On | Description | Pricing Tier |
|---|---|---|
| **Project Finance Extension** | PPM-linked project billing, utilization-to-revenue reconciliation, milestone invoicing | Add-on seat license |
| **Payroll BIR Pack** | SSS/PhilHealth/Pag-IBIG contribution schedules, BIR Form 2316 / alphalist automation | Add-on per payroll run |
| **Multi-Entity Consolidation** | Cross-company GL consolidation, intercompany eliminations, consolidated cash flow | Enterprise tier |
| **Managed Hosting** | Azure Container Apps provisioning, managed PostgreSQL, Front Door WAF management | Managed services contract |
| **Implementation Jumpstart** | 5-day guided Odoo CE baseline + Pulser onboarding engagement | Fixed-fee SOW |

---

## Architecture Summary

Pulser for Odoo Finance operates across four layers:

1. **Transaction Layer (Odoo CE + OCA)** — GL, AP, AR, Payroll, Invoicing. All financial records of truth. Odoo CE 18.0 + OCA community modules. Customer-hosted on Azure Container Apps. PostgreSQL 16 on Azure Database for PostgreSQL.

2. **Agent Layer (Azure AI Foundry + Pulser Middleware)** — Pulser finance agents (close, BIR, collections, cash) run as sidecar services on ACA. gpt-4.1 via Foundry, keyless Managed Identity auth. Policy-gated: read-only tools run approval-free; mutating tools require explicit human approval. Zero credential exposure — all secrets in Azure Key Vault.

3. **Data Layer (Power BI + Azure Database)** — Finance dashboards, cash flow forecasts, and BIR compliance reports served via Power BI embedded. Source data: live Odoo PostgreSQL via direct query or scheduled export to Azure Blob.

4. **Delivery Layer (Azure Front Door + GitHub + Azure Pipelines)** — WAF-gated public endpoint. CI via Azure Pipelines. Odoo container image in Azure Container Registry. IaC in Bicep under `infra/`.

---

## Differentiators

- **Philippine BIR compliance built in** — Not a localization bolt-on; BIR Form 2307 and TRAIN Law VAT schedules are first-class features designed for PH Revenue Regulations 11-2018.
- **CE + OCA + thin delta** — Does not fork Odoo core. Does not require Odoo Enterprise. Maximizes OCA community module reuse; builds only the thinnest `ipai_*` layer for BIR-specific logic and AI wiring.
- **Policy-gated AI, not autonomous AI** — Pulser never posts journals, locks periods, or submits BIR packages autonomously. Every mutating action is gated. This is a deliberate product decision, not a limitation.
- **Azure-native, no external SaaS dependencies** — No Supabase, no n8n, no Cloudflare, no Vercel. Fully Azure DNS + ACA + Front Door + Key Vault. Passes enterprise Azure WAF compliance review.
- **Customer-owned data** — The customer's Odoo instance and PostgreSQL database are in the customer's Azure subscription. InsightPulseAI does not hold or process ERP data in a shared cloud.
- **MpnId 7097325 — ISV Success enrolled** — Eligible for Azure consumption commitments, co-sell, and marketplace GTM programs.

---

## Exclusions / Non-Claims

The following are explicitly out of scope for this offer and must not be represented as included:

- Odoo Enterprise license or any Odoo.com IAP features
- Full D365 Finance functional parity (current coverage: ~40–50%; target: 80% by R4)
- Real-time BIR eFPS e-filing API integration (current output: eFPS-ready export package; actual e-filing remains a manual submission step)
- Payroll processing (covered by optional add-on, not base offer)
- Multi-currency treasury management
- SAP integration or SAP data migration
- Any guarantee of BIR audit defense or tax advisory services
- Odoo data hosting in InsightPulseAI infrastructure (customer hosts in own Azure subscription)

---

## Demo

### Demo Title

Pulser for Odoo — March 2026 Month-End Close & Q1 BIR Filing Walkthrough

### Demo Summary

A 12-minute walkthrough demonstrating:

1. **Finance dashboard entry** — Open the Pulser Finance Control Tower from the Odoo Finance menu. Review AR aging buckets, AP liability summary, and the 30-day cash flow projection for March 2026.
2. **Month-end close initiation** — Launch the March 2026 close checklist. Pulser surfaces two unreconciled journal exceptions. Controller reviews and approves the AI-recommended adjustment entries. Period is locked.
3. **BIR Form 2307 generation** — Navigate to BIR Compliance. Pulser generates Q1 2307 certificates for all active vendor withholding relationships. Export package is eFPS-ready. Controller downloads and reviews the PDF bundle.
4. **AR collections action** — Open the Collections Feed. Pulser surfaces three overdue invoices with recommended dunning actions. Controller approves two dunning emails; one is deferred. Emails are queued via Odoo's native mail server (Zoho SMTP).
5. **Cash flow scenario override** — Adjust the April payroll accrual assumption in the cash flow module. Forecast updates in real time. Controller saves the scenario for CFO review in Power BI.

Demo environment: shared Azure tenant with pre-loaded `odoo_dev` seed data (7 CSV datasets, Q1 2026 transactions).

---

## Support and Implementation Note

- **Support channel**: admin@insightpulseai.com (response within 1 business day, Philippines time zone)
- **Implementation**: Customer is responsible for Odoo CE baseline installation. InsightPulseAI provides an onboarding playbook and optional Implementation Jumpstart engagement (5-day fixed-fee SOW).
- **Self-service**: Full IaC (Bicep), module installation scripts, and configuration playbooks are included in the offer documentation.
- **Partner-led delivery**: Odoo implementation partners may deliver on behalf of customers under a separate partner agreement.

---

## Recommended First Submission Stance

For the initial Partner Center submission, the recommended stance is:

**One offer. One wedge. One demo. One geography. One buyer story.**

- **One offer**: Submit only the Finance Control Tower offer. Do not bundle Project Finance, Payroll, or multi-entity add-ons into the base submission. Add-ons are listed but not transactable at launch.
- **One wedge**: Lead with BIR Form 2307 automation and month-end close as the proof-of-value wedge. These are the highest-pain, most defensible Philippine-specific capabilities.
- **One demo**: Use the March 2026 month-end close and Q1 BIR filing walkthrough as the single demo asset. Keep it under 15 minutes.
- **One geography**: Target Philippines as the sole go-to-market geography for the first 90 days. Expand to Indonesia and Malaysia only after the first 3 paying customers are live.
- **One buyer story**: The Finance Controller at a Philippine SME who received a BIR notice and needs to fix their withholding tax process before the next filing deadline. Everything in the listing should speak to this person first.

This stance reduces review iteration cycles, sharpens the listing narrative, and produces a clean co-sell motion with Microsoft's SME field team in the Philippines.

---

## One-Paragraph Executive Summary

InsightPulseAI is bringing Pulser for Odoo — Finance Operations & Compliance Control Tower to the Microsoft commercial marketplace as a transactable SaaS offer targeting Philippine SMEs and Southeast Asian professional services firms running Odoo Community Edition on Azure. The offer closes the gap between Odoo CE's strong but unassisted accounting foundation and the compliance automation, AI-assisted close, and cash visibility that Finance teams in the region need — without requiring Odoo Enterprise licensing or a D365 Finance migration. Built on Azure Container Apps, AI Foundry, and a thin `ipai_*` module layer over Odoo CE + OCA, Pulser delivers BIR Form 2307 automation, structured month-end close workflows, AR collections intelligence, and rolling cash flow forecasts under a policy-gated AI model where Finance controllers remain in control of every mutating action. The initial submission targets the Philippines with a single wedge (BIR compliance + month-end close), a single demo, and a $49/user/month price point positioned at the lower bound of D365 Finance Essentials — making it a credible Azure Marketplace alternative for the Philippine SME segment.

---

## One-Slide Version

**Title**: Pulser for Odoo — Finance Operations & Compliance Control Tower

**Tagline**: AI-powered month-end close, BIR compliance, and cash flow forecasting for Odoo CE on Azure. No Enterprise license required.

**Problem**: Philippine SMEs running Odoo CE lose days to manual month-end close, face BIR audit risk from spreadsheet-based 2307 filing, and have no consolidated cash visibility.

**Solution**: Pulser adds an AI copilot layer to Odoo CE that automates close checklists, generates BIR-ready Form 2307 packages, surfaces AR/AP dashboards, and delivers 30/60/90-day cash forecasts — policy-gated, no autonomous mutations.

**Stack**: Odoo CE 18.0 + OCA + `ipai_*` delta + Azure ACA + AI Foundry (gpt-4.1) + Power BI. Azure DNS + Front Door WAF. PostgreSQL 16. Customer-owned data.

**Differentiators**: BIR-native. CE + OCA parity. Policy-gated AI. Azure-native. No Odoo Enterprise license.

**Market**: Philippines P0, ASEAN P1. Finance Controllers and CFOs at 50–500 person companies.

**Offer**: Transactable SaaS. $49/user/month (placeholder). 30-day free trial. ISV Success enrolled (MpnId 7097325).

**CTA**: https://www.insightpulseai.com/ — jake.tolentino@insightpulseai.com

---

## Marketplace Listing Pack

> Complete listing pack for use across Partner Center tabs, co-sell collateral, and AppSource preview.

---

### Headline

Pulser for Odoo — Finance Operations & Compliance Control Tower

---

### Short Description (150 characters)

AI copilot for Odoo CE Finance: month-end close, BIR 2307 automation, AR collections, and cash flow forecasts on Azure. No Enterprise license.

---

### Medium Description (300 characters)

Automate month-end close, generate BIR Form 2307 packages, surface AR/AP dashboards, and forecast cash flow — all inside Odoo CE on Azure. Pulser adds a policy-gated AI copilot without requiring Odoo Enterprise. Built for Philippine SMEs and ASEAN professional services firms.

---

### Long Description (AppSource body)

**Pulser for Odoo — Finance Operations & Compliance Control Tower** eliminates the manual coordination tax that Finance teams pay every month.

Philippine SMEs running Odoo Community Edition spend 3–5 days per close cycle chasing journal entries and reconciliation exceptions by email. BIR Form 2307 withholding tax certificates and VAT summary schedules are assembled by hand in Excel, creating audit risk before every quarterly filing. AR aging and AP due dates live in separate Odoo menus with no forward-looking cash view. Finance controllers want AI assistance but cannot accept an AI that autonomously posts journals or locks accounting periods.

Pulser solves all four problems with a single Azure-native offer:

**Month-End Close Automation**
Structured close checklist inside Odoo. Automated journal reconciliation. Period-lock enforcement. Pulser-assisted exception triage with human approval required before any correcting entry is posted.

**BIR Compliance Pack**
Automated BIR Form 2307 generation for all active vendor withholding relationships. TRAIN Law VAT summary schedules. eFPS/eBIRForms-ready export packages. Designed for BIR Revenue Regulations 11-2018.

**AR Collections Intelligence**
Aging bucket dashboards. Overdue escalation workflows. Dunning letter automation via Odoo's native mail server. Pulser-assisted collections recommendation feed — controller approves, Pulser executes.

**Cash Flow Forecasting**
Rolling 30/60/90-day cash projection from live Odoo AP and AR ledger data. Payroll accrual inputs. Scenario override capability. Power BI-embedded panel inside the Odoo Finance menu.

Built on Odoo CE 18.0 + OCA community modules + a thin `ipai_*` delta layer. Deployed on Azure Container Apps behind Azure Front Door WAF. No Odoo Enterprise license required. Customer-owned data in customer's Azure subscription.

---

### Category and Positioning

| Field | Value |
|---|---|
| **Primary category** | Finance & Accounting |
| **Secondary category** | Business Applications |
| **Industry** | Financial Services, Professional Services |
| **Solution area** | Business Applications — Finance & Accounting |
| **Competitive positioning** | Lower-cost Azure-native alternative to D365 Finance Essentials for Philippine SME and ASEAN professional services segment |

---

### Key Benefits

1. **Close faster** — Structured close checklist and automated reconciliation reduce month-end cycle from days to hours.
2. **File confidently** — BIR Form 2307 and VAT schedules generated automatically from Odoo ledger data; no Excel assembly required.
3. **See cash clearly** — 30/60/90-day rolling forecast derived from live AR/AP data, updated on each close.
4. **Collect proactively** — AI-assisted collections feed surfaces overdue AR before it becomes bad debt.
5. **Stay in control** — Policy-gated Pulser AI: every mutating finance action requires human approval.
6. **Own your data** — Odoo CE on your Azure subscription; InsightPulseAI does not hold your ERP data.

---

### Core Capabilities

| Capability | Module | Description |
|---|---|---|
| Month-End Close | `ipai_finance_close` | Checklist, journal reconciliation, period lock, exception triage |
| BIR Form 2307 | `ipai_bir_2307` | Withholding tax certificate generation, vendor mapping, PDF export |
| BIR Automation | `ipai_bir_2307_automation` | Scheduled 2307 generation, filing period management |
| Finance Tax | `ipai_finance_tax` | TRAIN Law VAT schedules, eFPS export package |
| AP/AR Management | `ipai_finance_ap_ar` | Unified AP/AR dashboard, aging analysis, payment matching |
| AR Collections | `ipai_ar_collections` | Aging buckets, dunning automation, collections recommendation feed |
| Cash Flow | `ipai_finance_cash` | 30/60/90-day forecast, scenario override, Power BI embed |
| FP&A Foundation | `ipai_finance_fpa` | Budget-vs-actual, analytic P&L, department reporting |

---

### What Is Included

Every subscription includes:

- All `ipai_finance_*` and `ipai_bir_*` Odoo CE modules
- Pulser Finance Agent (Azure AI Foundry, gpt-4.1, Managed Identity auth)
- Azure deployment baseline (Bicep IaC, ACA container definition, Front Door WAF policy, Key Vault bindings)
- Power BI Finance dashboard template
- Onboarding playbook (Odoo CE baseline verification, OCA module installation, Pulser agent wiring, demo data load)
- 30-day free trial on shared demo tenant
- Support via admin@insightpulseai.com (1 business day SLA, Philippines time zone)

---

### Optional Add-Ons

| Add-On | Description |
|---|---|
| Project Finance Extension | PPM-linked billing, utilization reconciliation, milestone invoicing |
| Payroll BIR Pack | SSS/PhilHealth/Pag-IBIG schedules, BIR Form 2316, alphalist |
| Multi-Entity Consolidation | Cross-company GL consolidation, intercompany eliminations |
| Managed Hosting | ACA provisioning, managed PostgreSQL, Front Door WAF management |
| Implementation Jumpstart | 5-day guided Odoo CE + Pulser onboarding (fixed-fee SOW) |

---

### Target Customers

- Philippine SMEs (50–500 employees) on Odoo CE needing BIR compliance automation
- Southeast Asian professional services firms with project-based revenue and multi-entity reporting needs
- Mid-market companies evaluating D365 Finance or SAP Business One and seeking a lower-cost Azure-native path
- Finance controllers and CFOs who need AI-assisted close and cash visibility without ERP re-platforming
- Odoo implementation partners adding an AI layer to existing customer deployments

---

### Buyer Personas

| Persona | Title | Pain | Trigger |
|---|---|---|---|
| Finance Controller | Finance Controller / Head of Finance | Manual close, BIR audit risk | BIR notice or external audit finding |
| CFO | CFO / VP Finance | No cash visibility, D365 too expensive | Board cash flow review |
| IT Decision-Maker | CTO / IT Manager | Odoo CE gaps, Azure-native requirement | License renewal or cloud migration project |
| Odoo Partner | Implementation Partner | Clients requesting AI layer | Customer RFP or competitive displacement situation |

---

### Differentiators

- **Philippine BIR-native** — Form 2307 and TRAIN Law VAT schedules are first-class features, not a localization afterthought
- **CE + OCA parity** — Maximizes Odoo CE and OCA community module reuse; `ipai_*` layer is deliberately thin
- **Policy-gated Pulser AI** — Mutating finance actions require explicit human approval; read-only recommendations are approval-free
- **Azure-native, no external SaaS dependencies** — Passes enterprise Azure WAF compliance review; no Supabase, n8n, Cloudflare, or Vercel
- **Customer-owned data** — Odoo and PostgreSQL run in the customer's Azure subscription
- **ISV Success enrolled** — MpnId 7097325; eligible for co-sell, Azure consumption commitments, and marketplace GTM programs

---

### What It Is Not

- Not an Odoo Enterprise replacement or reseller channel
- Not a full D365 Finance equivalent at launch (40–50% parity today; 80% target by R4 / December 2026)
- Not a real-time BIR eFPS API e-filing service (output is eFPS-ready package; manual submission remains)
- Not a payroll processing platform (payroll BIR pack is an optional add-on)
- Not a hosted ERP (customer owns and operates the Odoo instance)
- Not a general-purpose AI assistant; Pulser is scoped to Finance operations workflows

---

### Demo Summary

**Title**: Pulser for Odoo — March 2026 Month-End Close & Q1 BIR Filing Walkthrough

**Duration**: 12 minutes

**Flow**:
1. Finance dashboard — AR aging, AP liabilities, 30-day cash projection
2. Month-end close — checklist launch, exception triage, period lock
3. BIR 2307 generation — Q1 certificate bundle, eFPS export
4. Collections action — overdue AR feed, dunning email approval
5. Cash flow scenario — payroll accrual override, Power BI refresh

**Environment**: Shared demo tenant, `odoo_dev` database, pre-loaded Q1 2026 seed data (7 CSV datasets, 90-day transaction history).

---

### One-Paragraph Executive Summary

InsightPulseAI is bringing Pulser for Odoo — Finance Operations & Compliance Control Tower to the Microsoft commercial marketplace as a transactable SaaS offer targeting Philippine SMEs and Southeast Asian professional services firms running Odoo Community Edition on Azure. The offer closes the gap between Odoo CE's strong but unassisted accounting foundation and the compliance automation, AI-assisted close, and cash visibility that Finance teams in the region need — without requiring Odoo Enterprise licensing or a D365 Finance migration. Built on Azure Container Apps, AI Foundry, and a thin `ipai_*` module layer over Odoo CE + OCA, Pulser delivers BIR Form 2307 automation, structured month-end close workflows, AR collections intelligence, and rolling cash flow forecasts under a policy-gated AI model where Finance controllers remain in control of every mutating action. The initial submission targets the Philippines with a single wedge (BIR compliance + month-end close), a single demo, and a $49/user/month price point positioned at the lower bound of D365 Finance Essentials — making it a credible Azure Marketplace alternative for the Philippine SME segment.

---

### One-Slide Version

**Title**: Pulser for Odoo — Finance Operations & Compliance Control Tower

**Tagline**: AI-powered month-end close, BIR compliance, and cash flow forecasting for Odoo CE on Azure. No Enterprise license required.

| | |
|---|---|
| **Problem** | Philippine SMEs on Odoo CE lose days to manual close, face BIR audit risk from Excel-assembled 2307 filings, and have no consolidated cash visibility. |
| **Solution** | Policy-gated Pulser AI automates close checklists, generates BIR-ready Form 2307 packages, surfaces AR/AP dashboards, and delivers 30/60/90-day cash forecasts — human approval required for every mutating action. |
| **Stack** | Odoo CE 18.0 + OCA + `ipai_*` delta — Azure ACA + AI Foundry (gpt-4.1, MI auth) + Power BI + PostgreSQL 16 + Front Door WAF. Customer-owned data. |
| **Differentiators** | BIR-native. CE + OCA parity. Policy-gated AI. Azure-native. No Odoo Enterprise. ISV Success MpnId 7097325. |
| **Market** | Philippines P0 — Finance Controllers, CFOs, IT Decision-Makers at 50–500 person companies. ASEAN P1. |
| **Offer** | Transactable SaaS. $49/user/month (placeholder). 30-day free trial. Co-sell eligible. |
| **Contact** | https://www.insightpulseai.com/ — jake.tolentino@insightpulseai.com |

---

*Last updated: 2026-04-15. Maintained by Jake Tolentino. Partner Center submission target: Q2 2026.*
