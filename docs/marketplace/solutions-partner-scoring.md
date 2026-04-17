# Solutions Partner Scoring — IPAI Qualification Path

> Source: Partner Center → Membership → Solutions Partner insights (Apr 18, 2026)
> Current status: 0/100 across all designations. Track: SMB.

---

## Relevant Designations for IPAI

| Designation | Relevance | Priority | Why |
|---|---|---|---|
| **Data & AI** | Primary | R3-R4 | Databricks, AI Services, Document Intelligence, AI Search — all count |
| **Digital & App Innovation** | Secondary | Post-R4 | ACA, Container Apps, App Service — our hosting surface |
| **Security** | Potential | Post-R4 | Key Vault, Defender, Sentinel, Entra ID Premium |
| Business Applications | Low | — | Requires D365/Power Platform workloads (not our stack) |
| Modern Work | Low | — | Requires M365/Teams workloads (not our stack) |
| Infrastructure | Low | — | Requires VM/networking-heavy customer ACR |

---

## Data & AI — SMB Track (Primary Target)

**Qualification: 70+ points, >0 in all metrics**

### Performance (30 pts max)

| Metric | Requirement | How IPAI earns it |
|---|---|---|
| Net customer adds | Net new tenants with $500+ ACR in any of last 2 months | Each marketplace customer using Databricks + AI Services generates qualifying ACR |
| Max points | 3 customers = 30 pts | TBWA + 2 more customers |

**Partner association types:** CSP, DPOR, PAL
- **DPOR** (Digital Partner of Record) — claim via Partner Center for each customer tenant
- **PAL** (Partner Admin Link) — link Managed Identity to partner ID in customer subscriptions

### Skilling (40 pts max)

| Metric | Requirement | How IPAI earns it |
|---|---|---|
| Intermediate certifications | Certified individuals in qualifying courses | AI-900, AI-102, DP-100 (free via ISV Success) |
| Max points | 10 certified individuals = 40 pts | Jake + team members |

**Qualifying certifications (Data & AI):**
- AI-900: Azure AI Fundamentals (included in ISV Success)
- AI-102: Azure AI Engineer Associate (included in ISV Success)
- DP-100: Azure Data Scientist Associate (included in ISV Success)
- DP-203: Azure Data Engineer Associate
- DP-600: Microsoft Fabric Analytics Engineer
- AI-3002: Create Document Intelligence Solutions
- AI-3003: Build NLP Solutions with Azure AI
- AI-3004: Build Azure AI Vision Solutions

**Strategy:** Jake passes AI-900 + AI-102 + DP-100 (3 certs, all free) = ~12 pts. Each additional team member with 1 cert = ~4 pts. 3 people × 3 certs each = ~36 pts.

### Customer Success — Deployments (10 pts max)

| Metric | Requirement | How IPAI earns it |
|---|---|---|
| Deployments | Advanced Azure services in customer ACR (excludes VMs and VM licenses) | Databricks, AI Services, AI Search, Document Intelligence, SignalR, ACS |
| Max points | 5 deployments = 10 pts | Each customer with qualifying Azure services |

**Qualifying Azure services (all IPAI services count):**
- Databricks (dbw-*) — primary ACR driver
- Cognitive Services / AI Services (ipai-copilot-resource)
- Document Intelligence (docai-ipai-dev)
- AI Search (srch-ipai-dev-sea)
- Azure Cache for Redis (redis-ipai-dev-sea)
- SignalR Service (sigr-ipai-dev-sea)
- Container Apps (NOT excluded — only VMs excluded)
- Key Vault, Storage, PostgreSQL Flex

**Excluded:** Virtual Machines, Virtual Machine Licenses

### Customer Success — Usage Growth (20 pts max)

| Metric | Requirement | How IPAI earns it |
|---|---|---|
| Usage growth | % growth in ACR across all eligible customer tenants (TTM vs prior 12 months) | Organic growth as customers adopt more Databricks queries, AI calls |
| Max points | 20% ACR growth = 20 pts | Natural expansion as customer usage increases |

---

## IPAI Scoring Projection

### R3 (Aug-Oct 2026) — After marketplace publication + first customers

| Metric | Projected Score | How |
|---|---|---|
| Performance | 10-20 | 1-2 net new customers with $500+ ACR |
| Skilling | 12-24 | Jake: AI-900 + AI-102 + DP-100 (3 certs) |
| Deployments | 2-4 | Databricks + AI Services in 1-2 customer tenants |
| Usage Growth | 0 | No prior year baseline yet |
| **Total** | **24-48** | Not yet qualifying |

### R4 (Nov 2026 - Mar 2027) — Approaching qualification window

| Metric | Projected Score | How |
|---|---|---|
| Performance | 30 | 3 customers with $500+ monthly ACR |
| Skilling | 24-36 | 2-3 people with qualifying certs |
| Deployments | 6-10 | Databricks + AI Services + DocAI + Search across 3 customers |
| Usage Growth | 5-10 | First-year growth (no baseline = low score initially) |
| **Total** | **65-86** | Approaching or qualifying |

### H1 2027 — Qualification target

| Metric | Projected Score | How |
|---|---|---|
| Performance | 30 | 3+ customers maintained |
| Skilling | 36-40 | 3-4 people with 2-3 certs each |
| Deployments | 10 | 5+ deployments across customer base |
| Usage Growth | 10-20 | YoY growth established |
| **Total** | **86-100** | **Qualified** |

---

## Partner Association — How to Claim Customer ACR

For Azure services to count toward scoring, IPAI must be associated with the customer tenant via one of:

### DPOR (Digital Partner of Record)
- Customer assigns IPAI as DPOR in Azure portal
- Covers all Azure services in that subscription
- **Action:** Include DPOR assignment in customer onboarding checklist

### PAL (Partner Admin Link)
- Link Managed Identity or service principal in customer subscription to IPAI partner ID
- **Action:** When deploying to customer Azure subscription, run:
  ```bash
  az managementpartner create --partner-id 7097325
  ```
- MpnId: **7097325** (IPAI / Dataverse IT Consultancy)

### CSP (Cloud Solution Provider)
- If IPAI resells Azure subscriptions to customers
- Not applicable yet (direct model first)

---

## Certified Software Designation (CSD) — Advanced Package Unlock

CSD is the path to the **Advanced ISV Success package** ($176K value, $150K cash incentives).

Requirements:
- Solutions Partner designation achieved (70+ pts in any area)
- Published transactable offer on marketplace
- Meeting additional CSD criteria

**IPAI target:** Achieve Data & AI Solutions Partner → unlock CSD → upgrade to Advanced package with $50K Azure credits + $150K cash incentives.

---

## Immediate Actions (R1-S01)

| # | Action | Feeds |
|---|---|---|
| 1 | Register for AI-900 exam (free via ISV Success) | Skilling: +4 pts |
| 2 | Register for AI-102 exam (free via ISV Success) | Skilling: +4 pts |
| 3 | Register for DP-100 exam (free via ISV Success) | Skilling: +4 pts |
| 4 | Include PAL assignment in customer onboarding template | Performance + Deployments |
| 5 | Include DPOR assignment in customer onboarding checklist | Performance + Deployments |

---

*Generated: 2026-04-18 | MpnId: 7097325 | Track: SMB | Aligned to: ssot/delivery/sprint-isv-alignment.yaml*
