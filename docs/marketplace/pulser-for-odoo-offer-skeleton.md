# Marketplace Offer Skeleton

**Offer:** Pulser for Odoo — Finance Operations & Compliance Control Tower
**Status:** Draft — internal working skeleton
**Date:** 2026-04-15

---

## 1. Offer Name

Pulser for Odoo — Finance Operations & Compliance Control Tower

---

## 2. One-Line Positioning

An AI-powered finance operations copilot built on Odoo CE that closes the gap between mid-market ERP and enterprise finance automation — without the D365/SAP price tag.

---

## 3. Short Description (300 characters)

Pulser for Odoo is an AI copilot layer for Odoo CE that automates month-end close, BIR tax compliance, AP/AR reconciliation, and project finance reporting. Purpose-built for Philippine SMEs and regional professional services firms running Odoo on Azure.

---

## 4. Long Description (2000 characters)

Pulser for Odoo is a finance operations and compliance control tower that transforms Odoo Community Edition into an enterprise-grade financial management platform. It adds an intelligent copilot layer — built on Azure AI Foundry and Microsoft 365 — directly on top of your existing Odoo 18 CE deployment.

Finance teams in growing Philippine companies face a compounding problem: they are expected to close books faster, file BIR taxes accurately, manage multi-project cash flow, and report to management in near-real time — but with headcount and tooling designed for a smaller operation. Standard Odoo CE covers the record-keeping. Pulser covers the operations layer above it.

Pulser automates the reconciliation loop between bank transactions and Odoo journal entries, generates BIR-compliant 2307 withholding certificates and 1601-C payroll tax summaries, runs structured month-end close checklists with approval gates, and surfaces project finance dashboards that mirror what D365 Project Operations delivers — without the Microsoft ERP licensing cost.

The product is delivered as a pre-configured Azure Container Apps deployment paired with a thin set of Odoo CE modules (`ipai_*`). No Odoo Enterprise license required. No odoo.com cloud dependency. The full stack runs in the customer's own Azure subscription, governed by Entra ID and Azure Key Vault, with Power BI as the reporting surface.

Pulser sits alongside your Odoo instance — it does not fork or patch Odoo core. Upgrades to Odoo 18 → 19 do not break the copilot layer. The architecture is intentionally thin: configuration and OCA modules first, custom code only for the Philippine compliance and AI orchestration gaps that no upstream module covers.

For partners and resellers, Pulser for Odoo ships as a deployable offer on the Microsoft Azure Marketplace with metered billing, transactable through the Partner Center ISV path.

---

## 5. Problem Statement

Philippine SMEs and regional professional services firms running Odoo CE face three compounding gaps:

1. **Compliance burden without automation.** BIR filing (2307, 1601-C, eFPS, eBIRForms) is manual, error-prone, and penalized for lateness. Odoo CE has no Philippine tax automation. Enterprise alternatives cost 5–10x more per seat.

2. **Month-end close that takes weeks.** Without a structured close checklist, reconciliation assistant, and approval workflow, finance teams spend 10–15 days closing books that should close in 3–5. Odoo CE has the ledger; it does not have the close orchestration.

3. **Project finance blind spots.** Professional services firms running projects in Odoo have timesheet data, PO data, and revenue recognition data in separate views. There is no unified project finance P&L, no earned value calculation, no cash flow forecast per engagement — capabilities that D365 Project Operations delivers natively.

Pulser for Odoo closes all three gaps on top of Odoo CE, deployed in the customer's Azure subscription, priced for mid-market.

---

## 6. Target Customer

**Primary:** Philippine SMEs (50–500 employees) in professional services, consulting, media production, and project-based manufacturing — already running or evaluating Odoo CE.

**Secondary:** Regional accounting and ERP implementation partners serving the Philippine mid-market who need a differentiated Odoo practice with compliance automation built in.

**Disqualifier:** Companies already licensed on Odoo Enterprise with full BIR localization from a local partner, or companies on D365 F&O with no appetite to migrate.

---

## 7. Core Capabilities

1. **Reconciliation Agent** — Automated bank-to-ledger matching with exception surfacing in Odoo and Slack. Reduces manual reconciliation time by targeting 80%+ auto-match rate on clean bank feeds.

2. **BIR Compliance Pack** — Generates 2307 withholding certificates, 1601-C payroll tax summaries, and eFPS/eBIRForms-ready export files directly from Odoo AP/AR and payroll data.

3. **Month-End Close Orchestration** — Structured close checklist with task assignment, approval gates, and a Pulser copilot that answers "what is still open?" and "what blocked last close?" in natural language.

4. **Project Finance Dashboard** — Per-engagement P&L, earned value, and cash flow forecast surfaced in Power BI, sourced from Odoo timesheets, purchase orders, and invoices.

5. **AP/AR Automation** — AI-assisted vendor invoice processing (via Azure Document Intelligence), payment run preparation, collections follow-up draft generation.

6. **Pulser Copilot Surface** — Natural language query over Odoo financial data, routed through the Pulser agent platform, surfaced in Microsoft Teams and the Odoo web client.

---

## 8. What Is Included

- Odoo CE 18.0 deployment on Azure Container Apps (pre-configured)
- `ipai_finance_ap_ar`, `ipai_finance_cash`, `ipai_finance_fpa`, `ipai_finance_tax`, `ipai_bir_2307`, `ipai_bir_2307_automation` modules
- OCA baseline: `account_reconciliation_widget`, `account_payment_order`, `project_timesheet_time_control`, and supporting modules
- Azure infrastructure: Container Apps environment, Azure Front Door, Key Vault, PostgreSQL 16
- Power BI report pack (GL summary, project finance, BIR compliance tracker)
- Pulser agent runtime (Azure Container Apps) with Reconciliation Agent and BIR Compliance Agent
- 90-day onboarding and hypercare support (Managed Operations tier)
- Monthly BIR filing calendar and close checklist templates

---

## 9. What It Is Not

- Not an Odoo Enterprise license or resale
- Not a replacement for a licensed BIR accredited accounting system (it is a compliance aid, not a CAS substitute)
- Not a payroll system (integrates with payroll output; does not process payroll)
- Not a D365 migration tool (it is an alternative ERP stack, not a migration service)
- Not a multi-tenant SaaS product in the current release (single-tenant Azure deployment per customer)
- Not a general-purpose chatbot — Pulser is scoped to finance, compliance, and project operations workflows

---

## 10. Key Differentiators

1. **Philippine-first compliance.** BIR 2307, 1601-C, eFPS/eBIRForms automation built in — not an afterthought add-on. Designed around Philippine regulatory cadence.

2. **Azure-native, customer-owned.** Runs in the customer's Azure subscription. No vendor data custody. Entra ID governs identity. Key Vault governs secrets. Compliant with data residency requirements.

3. **Odoo CE foundation.** No Enterprise license tax. CE + OCA + thin `ipai_*` delta = 80%+ EE parity at CE cost.

4. **D365 Project Operations parity for services firms.** Project finance P&L, earned value, and cash flow forecasting that matches D365 PO capabilities for professional services delivery.

5. **Copilot embedded, not bolted on.** Pulser is the operational layer, not a chatbot widget. It automates close steps, reconciliation matching, and BIR file generation — it does not just answer questions about them.

6. **Transactable on Microsoft Marketplace.** Metered billing through Partner Center. Eligible for MACC drawdown for Azure-consuming customers.

---

## 11. Architecture Summary

```
Customer Azure Subscription
├── Azure Front Door (WAF + CDN)
├── Azure Container Apps Environment
│   ├── odoo-ce (Odoo 18 CE + OCA + ipai_* modules)
│   ├── pulser-runtime (agent orchestration, tool execution)
│   └── mcp-server (Odoo MCP server, Finance tools)
├── Azure PostgreSQL 16 (Flexible Server)
├── Azure Key Vault (secrets, certs)
├── Azure AI Foundry (gpt-4.1 deployment for Pulser agents)
├── Azure Document Intelligence (AP invoice extraction)
└── Power BI (reporting surface, publisher dataset)

Identity plane: Microsoft Entra ID (OIDC, Managed Identities)
Notification surface: Microsoft Teams (Adaptive Cards), Odoo web client
```

No Supabase. No n8n. No Vercel. No Cloudflare. Fully Azure-native.

---

## 12. First Packaged Scenario

**"Close the Month in 5 Days"**

The customer's finance team opens Pulser Close Orchestrator on Day 1 of close. Pulser presents the structured 25-step close checklist, pre-populated with the outstanding items it detected from Odoo: unreconciled bank lines, unapproved vendor bills, unbilled timesheets, missing accruals.

The Reconciliation Agent runs overnight and surfaces the 12 exceptions it could not auto-match. The finance analyst reviews and clears 10 of them in the Odoo reconciliation widget. The remaining 2 go to the approver via Teams Adaptive Card.

On Day 3, the BIR Compliance Agent generates the 2307 certificates for the month's withholding transactions and posts them to the shared Drive folder. The finance manager reviews and approves in one click.

On Day 5, Pulser marks the close complete. The Power BI Close Pack publishes the final P&L, balance sheet, and variance report to the management team's Teams channel.

The same close that previously took 12 days — with 3 people chasing spreadsheets — now takes 5, with Pulser handling the coordination layer.

---

## 13. Delivery Model

**Implementation:** Partner-led deployment. IPAI provides the deployment playbook, Azure infrastructure templates (Bicep), and module install scripts. Partner handles customer configuration, chart of accounts mapping, and user training.

**Timeline:** 8–12 weeks for Core tier. 12–16 weeks for Finance Control Tower. 16–20 weeks for Managed Operations.

**Hosting:** Customer's Azure subscription (BYOS — Bring Your Own Subscription). IPAI does not host customer data.

**Support:** Azure DevOps-tracked tickets. SLA tiers in the MSA. Hypercare period post-go-live.

**Upgrade path:** Odoo version upgrades follow the OCA upgrade path. Pulser module upgrades are delivered as container image updates and module patches through the Azure DevOps release pipeline.

---

## 14. Packaging Tiers

### Tier 1 — Core

**Target:** Small finance teams (3–10 people), straightforward Odoo CE deployment, primary need is BIR compliance and basic close structure.

**Includes:**
- Odoo CE 18 on Azure Container Apps
- BIR Compliance Pack (2307, 1601-C)
- Month-End Close Checklist (manual orchestration, no agent automation)
- Power BI Finance Starter Pack (GL, AP aging, AR aging)
- Standard OCA baseline
- 30-day implementation, 30-day hypercare

**Pricing model:** Fixed implementation fee + monthly platform subscription (metered by active users).

---

### Tier 2 — Finance Control Tower

**Target:** Growing finance teams (10–30 people), multi-entity or multi-project operations, need for reconciliation automation and project finance visibility.

**Includes everything in Core, plus:**
- Reconciliation Agent (automated bank-to-ledger matching)
- AP/AR Automation (Document Intelligence invoice processing)
- Project Finance Dashboard (per-engagement P&L, earned value, cash flow)
- Pulser Copilot Surface (Teams + Odoo web, natural language finance queries)
- Extended OCA pack (project reporting, analytic accounting, payment orders)
- 60-day implementation, 60-day hypercare

**Pricing model:** Fixed implementation fee + higher monthly subscription tier (metered by active users + reconciliation transaction volume).

---

### Tier 3 — Managed Operations

**Target:** Finance teams that want Pulser managed end-to-end — infrastructure, upgrades, BIR filing support, and ongoing close operations support.

**Includes everything in Finance Control Tower, plus:**
- Managed Azure infrastructure (IPAI manages the ACA environment, PG, Key Vault, AFD)
- Monthly BIR filing support (IPAI agent-assisted, partner-reviewed)
- Quarterly Odoo + Pulser upgrade runs
- Dedicated Pulser success manager
- SLA: 99.5% uptime, 4-hour critical response
- 90-day implementation, ongoing hypercare (quarterly reviews)

**Pricing model:** Monthly managed service fee (per-entity, includes platform + operations). No separate implementation fee for standard deployment.

---

## 15. Marketplace Value Proposition Bullets

- Deploy a D365-class finance operations platform at Odoo CE cost
- BIR 2307 and 1601-C automation built in — no third-party compliance add-on required
- Close your books in 5 days, not 12 — AI-orchestrated close checklist + reconciliation agent
- Runs in your Azure subscription — you own the data, Entra governs the access
- Transactable on Microsoft Azure Marketplace — eligible for MACC drawdown
- No Odoo Enterprise license required — CE + OCA + thin AI layer
- Microsoft Teams surface — finance alerts, approvals, and close status in your existing collaboration tool
- Power BI reporting pack included — no separate BI license required for standard dashboards
- Partner-deployable — IPAI-certified partners can implement and resell

---

## 16. Demo Storyline

**Title:** "Maria closes the month — with Pulser"

**Persona:** Maria Santos, Finance Manager, mid-size Manila professional services firm (80 staff, 12 active projects, monthly BIR obligations).

**Act 1 — Open the close (Day 1)**
Maria opens Pulser Close Orchestrator in Odoo. The checklist shows 25 steps. 8 are already complete (automated by Pulser overnight). 3 are blocked. Pulser explains why each is blocked in plain language and links directly to the Odoo record.

**Act 2 — Reconciliation (Day 2)**
Maria opens the Reconciliation Agent view. 94 bank lines processed. 81 auto-matched. 13 exceptions flagged with confidence scores and suggested matches. Maria accepts 11 suggestions with one click. 2 require manual review — she reassigns them to her analyst via Teams.

**Act 3 — BIR compliance (Day 3)**
Maria opens the BIR Compliance Pack. Pulser has generated all 2307 certificates for the month. She previews one, approves the batch, and Pulser generates the eFPS-ready export file. Total time: 4 minutes.

**Act 4 — Project finance (Day 4)**
Maria opens the Project Finance dashboard in Power BI. She sees 12 active engagements with P&L, earned value %, and cash flow forecast. Two engagements are flagged red — over budget and behind on billing milestones. She clicks through to Odoo and raises corrective invoices directly.

**Act 5 — Close complete (Day 5)**
Pulser marks the close complete. The Power BI Close Pack publishes automatically to the management Teams channel. Maria's CFO sees the P&L by 9am on Day 5. Previously it arrived on Day 14.

---

## Best Category Framing

**Primary Microsoft Marketplace category:** Business Applications > Finance & Accounting
**Secondary category:** Business Applications > ERP
**Azure Marketplace tag:** AI + Machine Learning, Integration, Business Process Automation

**Comparable offers for positioning:**
- Not competing with D365 Finance (different price point and deployment model)
- Positioned alongside mid-market Odoo SI offers and Philippine localization packs
- Differentiator vs. generic Odoo Marketplace listings: AI copilot layer + BIR compliance + Azure-native hosting

---

## Internal Offer Statement

Pulser for Odoo is IPAI's flagship transactable offer. It packages the finance operations and compliance automation capabilities of the Pulser platform — built on Odoo CE 18, Azure AI Foundry, and Microsoft 365 — into a partner-deployable, marketplace-transactable product for the Philippine and Southeast Asian mid-market.

The offer demonstrates the full IPAI platform stack in a single customer-facing SKU: Odoo as the system of record, Pulser as the agent layer, Azure as the infrastructure substrate, Power BI as the reporting surface, and Microsoft Teams as the notification and approval surface.

It is the primary vehicle for Partner Center ISV revenue, MACC-consuming enterprise conversations, and partner channel activation in the Philippine market.
