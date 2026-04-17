# Capabilities Roadmap — Pulser for Odoo

> Structured by capability domain, mapped to release sprints and marketplace publication gates.
> Format: Microsoft product capabilities style (goal → capability → feature set → sprint).

---

## 1. Close & Orchestration

**Goal:** Give finance teams real-time visibility and control over month-end, quarter-end, and annual close.

| # | Capability | Feature Set | Owner | Sprint | Status |
|---|---|---|---|---|---|
| 1.1 | Close Calendar | Phase plan with calendarized deadlines, dependency chains, critical path | Odoo + Databricks | R1-S02 | Building |
| 1.2 | Milestone Tracking | Task/milestone model with sequence, assignment, stage gates | Odoo | R1-S01 | Seeded |
| 1.3 | Approval Queue | Multi-level approval chains with bottleneck detection | Odoo + Pulser | R2-S03 | Planned |
| 1.4 | Bottleneck Analytics | Reviewer/approver workload scoring, compression detection | Databricks | R2-S04 | Planned |
| 1.5 | Close Readiness Summary | Plain-language close status for FD/CFO, auto-generated | Pulser | R2-S05 | Planned |
| 1.6 | Critical Path Analysis | Deadline risk scoring, dependency compression alerts | Databricks | R2-S04 | Planned |

**Benchmark:** SAP AFC + Broadcom Clarity PPM. Delivered at open-source ERP cost.

---

## 2. Evidence & Compliance

**Goal:** Track evidence completeness, surface gaps, and draft evidence requests automatically.

| # | Capability | Feature Set | Owner | Sprint | Status |
|---|---|---|---|---|---|
| 2.1 | Evidence Tracking | Completeness % per filing, per project, per period | Odoo + Databricks | R2-S03 | Planned |
| 2.2 | Evidence Drafting | AI-generated evidence request emails to vendors/staff | Pulser | R2-S05 | Planned |
| 2.3 | Blocker Explanation | Plain-language "why is this blocked?" for any stuck item | Pulser | R2-S04 | Planned |
| 2.4 | Tax Exception Triage | Severity-scored exception queue (blocker/warning/info) | Databricks + Pulser | R3-S07 | Planned |
| 2.5 | Return Validation Checks | Pre-submission validation against BIR rules | Databricks + Pulser | R3-S08 | Planned |

**Benchmark:** SAP Tax Compliance + AvaTax audit trail.

---

## 3. Filing Readiness

**Goal:** Surface filing obligations, deadlines, and readiness state for PH BIR compliance.

| # | Capability | Feature Set | Owner | Sprint | Status |
|---|---|---|---|---|---|
| 3.1 | Filing Readiness Board | Per-form readiness (2550Q, 1601-EQ, 1702, 2307) | Databricks + Pulser | R2-S05 | Planned |
| 3.2 | Tax Obligation Registry | Data-driven obligation calendar (not hardcoded) | Databricks | R2-S03 | Planned |
| 3.3 | Deadline Chain | Prep → review → approval → file dependency tracking | Databricks | R2-S04 | Planned |
| 3.4 | Deadline Risk Scoring | Days-to-deadline vs completion % risk model | Databricks | R2-S04 | Planned |
| 3.5 | Official Format Export | BIR .dat export readiness tracking | Databricks | R3-S09 | Planned |
| 3.6 | PH Statutory Pack | Full BIR statutory package automation | Odoo Bridge + Databricks | R4-S14 | Deferred |

**Benchmark:** Odoo 19 Tax Return + AvaTax compliance automation.

---

## 4. Payment Control

**Goal:** Govern payment approval, track withholding, and link payments to filing dependencies.

| # | Capability | Feature Set | Owner | Sprint | Status |
|---|---|---|---|---|---|
| 4.1 | Payment Approval Queue | Multi-level payment approval with risk indicators | Odoo + Pulser | R2-S03 | Planned |
| 4.2 | Payment Readiness State | Per-payment readiness (docs, approval, funds, withholding) | Databricks + Pulser | R2-S05 | Planned |
| 4.3 | Withholding Review | EWT 2%/10% + VAT 12% auto-classification on payment | Odoo + Pulser | R2-S04 | Planned |
| 4.4 | Payment Evidence Status | Evidence completeness per payment batch | Odoo + Databricks | R2-S05 | Planned |
| 4.5 | Payment-to-Filing Dependency | Payment state → filing readiness linkage | Databricks | R2-S06 | Planned |
| 4.6 | Bank Reconciliation | OCA reconciliation + Genie NL query | Odoo + Databricks | R3-S07 | Planned |

**Benchmark:** D365 Finance Payables Agent + SAP payment workflows.

---

## 5. Document Intelligence

**Goal:** Extract structured data from invoices, receipts, and forms using Azure Document Intelligence.

| # | Capability | Feature Set | Owner | Sprint | Status |
|---|---|---|---|---|---|
| 5.1 | Invoice Extraction | Prebuilt-invoice model (26 fields, 89-97% confidence) | ipai_doc_intel | R1-S02 | Built |
| 5.2 | Odoo Integration | "Extract with DocAI" button on vendor bill form | ipai_doc_intel | R1-S02 | Built |
| 5.3 | Receipt Extraction | Prebuilt-receipt model for expense reports | DocAI | R3-S08 | Planned |
| 5.4 | Custom TBWA Models | CA form + Expense Report extraction models | DocAI | R3-S11 | Planned |
| 5.5 | Batch Processing | Multi-document extraction queue | ipai_doc_intel | R3-S09 | Planned |

**Benchmark:** D365 Finance Invoice Capture Agent + SAP Joule document processing.

---

## 6. Operational Intelligence

**Goal:** Surface workload patterns, automation candidates, and operational health metrics.

| # | Capability | Feature Set | Owner | Sprint | Status |
|---|---|---|---|---|---|
| 6.1 | Task Burden Analysis | Recurring task volume and distribution heatmap | Databricks | R2-S04 | Planned |
| 6.2 | Automation Candidate Scoring | Score tasks by automation potential (frequency × effort × rule-based) | Databricks | R2-S05 | Planned |
| 6.3 | Manager Summary | Plain-language operational summary for managers/FDs | Pulser | R2-S05 | Planned |
| 6.4 | Budget Variance | Project-level budget vs actual with drill-down | Databricks | R2-S06 | Planned |
| 6.5 | Utilization KPIs | Team workload, capacity, and utilization metrics | Databricks | R3-S07 | Planned |

**Benchmark:** Databricks Control Tower pattern + D365 Project Ops.

---

## 7. Conversational Analytics

**Goal:** Enable natural-language business questions over governed gold data marts.

| # | Capability | Feature Set | Owner | Sprint | Status |
|---|---|---|---|---|---|
| 7.1 | Genie Domain Spaces | Finance Ops + Compliance & Tax NL spaces | Databricks | R1-S01 | Live |
| 7.2 | Gold Mart Queries | NL queries over 6 gold views (103 bronze rows) | Databricks | R1-S01 | Live |
| 7.3 | Databricks One Chat | Unified chat across all marts | Databricks | R1-S02 | Pending |
| 7.4 | Cross-Domain Analytics | Cross-space queries (finance + project + compliance) | Databricks | R2-S06 | Planned |
| 7.5 | DLT Pipeline | Automated Bronze → Silver → Gold refresh | Databricks | R2-S04 | Planned |

**Benchmark:** Notion 3.0 workspace search + D365 Copilot ad-hoc analysis.

---

## 8. AI-Assisted Workflow

**Goal:** Provide guided, role-aware assistance for finance and operations tasks.

| # | Capability | Feature Set | Owner | Sprint | Status |
|---|---|---|---|---|---|
| 8.1 | Pulser Chat | Production Ask Pulser on insightpulseai.com | Pulser + Foundry | R2-S06 | Planned |
| 8.2 | Role-Aware Guidance | Next-best-action per persona (FD, AP clerk, tax analyst) | Pulser | R3-S07 | Planned |
| 8.3 | Change Detection | "What changed since last review" summaries | Pulser | R3-S08 | Planned |
| 8.4 | Action Handoff | Chat guidance → Odoo record mutation with confirmation | Pulser + Odoo | R3-S09 | Planned |
| 8.5 | Workspace Memory | Cross-surface context retention across interactions | Pulser + Databricks | R4-S13 | Deferred |
| 8.6 | Multi-Agent Orchestration | Specialist agent collaboration (finance, tax, project) | Pulser + Foundry | R4-S15 | Deferred |

**Benchmark:** SAP Joule guided experience + Notion 3.0 AI agents.

**D365 F&O Copilot competitive note (Mar 2026):**
D365 now ships Copilot features AND a native MCP server for ERP data access. This validates our MCP-first architecture.

| D365 Copilot Feature | IPAI Equivalent | Status |
|---|---|---|
| Sidecar chat (generative help) | Pulser chat widget | R2-S06 |
| Collections coordinator summary | AR Collections recommendation feed | R2-S05 |
| Customer page summary | Pulser manager/FD summary | R2-S05 |
| Workflow history summary | Close readiness summary | R2-S05 |
| Chat with F&O data | Genie spaces (NL over gold marts) | Live |
| Immersive Home (agent workspace) | Pulser control tower dashboard | R2-S04 |
| **D365 ERP MCP server** | **IPAI MCP topology (12 servers)** | Live |
| Confirmed PO changes workspace | Not in finance wedge | — |
| Supplier Communications Agent | Not in finance wedge | — |
| Time entry Copilot | Pulser: task lookup by person | R3-S08 |

**Key insight:** Microsoft now provides a **Dynamics 365 ERP MCP server** that lets agents perform data operations without custom code. This is architecturally identical to our `ipai-odoo-mcp` server for Odoo. Our approach is validated — we're building the same pattern on Odoo CE that Microsoft ships natively on D365 F&O.

---

## 9. Platform & Infrastructure

**Goal:** Enterprise-grade hosting, security, and marketplace readiness.

| # | Capability | Feature Set | Owner | Sprint | Status |
|---|---|---|---|---|---|
| 9.1 | ACA Runtime | 6 Container Apps (Odoo web/worker/cron + 3 web surfaces) | Infra | R1-S01 | Live |
| 9.2 | Custom Domains + TLS | 4 managed certs (erp, www, prismalab, w9studio) | Infra | R1-S01 | Live |
| 9.3 | Realtime Services | SignalR + ACS + Redis for agent communication | Infra | R1-S01 | Live |
| 9.4 | Private Networking | VNet + private endpoints for PG, KV, Search | Infra | R2-S03 | Planned |
| 9.5 | APIM GenAI Gateway | Rate limiting + observability for agent API calls | Infra | R2-S05 | Planned |
| 9.6 | Marketplace Offer | Transactable offer on Azure Marketplace | GTM | R3-S09 | Target |
| 9.7 | Production Hardening | AFD Premium + NSGs + NAT Gateway + Chaos Studio | Infra | R3-S08 | Planned |
| 9.8 | Multi-Tenant Isolation | Per-customer data isolation + tenant routing | Infra | R4-S13 | Deferred |

---

## Release Summary

| Release | Sprints | Theme | Capabilities Shipping |
|---|---|---|---|
| **v1** (R1+R2) | S01–S06 | Finance Control Tower | 23 must-have capabilities |
| **v1.1** (R3) | S07–S12 | Guided Assistance + Marketplace | 7 should-have + marketplace publication |
| **v2** (R4) | S13–S16 | Automation & Scale | 6 deferred capabilities + GA |

## Pricing Position

| Competitor | Price | IPAI Position |
|---|---|---|
| D365 Finance | $210–300/user/month | Open-source ERP + pay-per-query analytics |
| D365 Project Ops | $150/user/month | Odoo CE + OCA (free) + Databricks consumption |
| D365 Customer Insights | $1,700/tenant/month | Databricks gold marts + Genie (NL analytics) + Pulser (guided ops) |
| SAP AFC + Joule | Enterprise license | Control tower on commodity stack |
| Notion 3.0 | $12–28/user/month | Governed ERP data (not wiki data) |
| AvaTax | $50–200/filing | PH-first, BIR-native |

### D365 Customer Insights competitive note

D365 CI offers unified customer data, AI-powered journeys, Copilot content generation, and real-time segmentation at $1,700/tenant/month (100K unified people, 10K interacted). IPAI does NOT compete directly on CDP/marketing automation — our wedge is **finance ops + compliance + project control**. However, the data unification and AI-guided action patterns are architecturally equivalent:

| D365 CI Capability | IPAI Architectural Equivalent |
|---|---|
| Unified customer profiles | Databricks Unity Catalog (unified data governance) |
| AI predictions / lead scoring | Gold mart KPIs + deadline risk scoring |
| Copilot content generation | Pulser summaries + evidence drafting |
| Real-time journeys | Odoo approval chains + Pulser guided workflows |
| Segmentation via NL | Genie spaces (NL over gold marts) |
| $1,700/tenant/month | Databricks consumption + Odoo CE (free) |

---

## Competitive Landscape: Marketing & Advertising Intelligence

> Adjacent competitors relevant to TBWA\SMP pilot and marketing agency vertical expansion.

### Smartly.io — Creative + Media Automation

| Capability | Smartly | IPAI Equivalent |
|---|---|---|
| AI creative production at scale | Smartly Creative | Not in scope (creative is client domain) |
| Cross-channel media optimization | Smartly Media (Meta, TikTok, Pinterest, Snap, CTV) | Not in scope |
| Unified performance dashboard | Smartly Intelligence | Databricks gold marts + Genie (operational, not media) |
| Conversational commerce | ChatGPT integration | Pulser (ops-focused, not commerce) |

**Positioning:** Smartly owns creative-media optimization. IPAI owns the **operational backbone** (finance, compliance, project control) that agencies like TBWA run on. Complementary, not competitive.

### Quilt.AI (Sphere) — Cultural Intelligence

| Capability | Quilt.AI | IPAI Equivalent |
|---|---|---|
| Cultural conversation analysis | Social Meaning | Not in scope |
| Trend tracking (100-300/month) | Trends Explorer | Databricks gold marts (operational trends, not cultural) |
| Psychographic segmentation | Agentic Segmentation | Not in scope |
| Creative testing (1M+ ads trained) | LUME | Not in scope |
| Brand health tracking | Brand Health Tracker | Not in scope |
| LLM equity analytics | LLM Equity Analytics | Not in scope |

**Positioning:** Quilt.AI is a research/insights platform for brand strategy. IPAI is an operations platform. The **data engineering pattern** (billions of signals → governed marts → NL query) is architecturally similar — validate our Databricks + Genie approach against Quilt's Sphere pattern.

### Cannes Lions Marketing Assistant — Award Research AI

| Capability | Lions MA | IPAI Equivalent |
|---|---|---|
| Cross-category campaign search | WARC + Contagious IQ + The Work | Not in scope |
| Pattern discovery in award data | AI analysis | Pulser pattern (evidence-based guidance, not generative) |
| Privacy-first (no prompt sharing) | Core design | Same doctrine (zero-secret agents, no data leakage) |
| Non-generative (research curation) | Intentional constraint | Pulser is also non-generative for mutations (approval-gated) |

**Positioning:** Lions MA is a research tool for creative strategists. Relevant pattern: **non-generative AI that curates and surfaces evidence** — validates Pulser's "guided, not autonomous" approach.

### Data Intelligence (Romania) — Marketing Data Hub

| Capability | DI Romania | IPAI Equivalent |
|---|---|---|
| Real-time data acquisition | Processing marketing data daily | Databricks DLT (operational data, not marketing) |
| Proprietary indexes (Digital Health, Content Impact) | Custom scoring models | Gold mart KPIs (deadline risk, automation candidate, bottleneck) |
| Marketing Mix Modeling | ROI optimization | Not in scope (finance ROI, not media ROI) |
| Consumer journey mapping | Behavior analysis | Not in scope |
| 38+ industry categories | Broad coverage | PH finance + compliance first, then vertical expansion |

**Positioning:** DI Romania is a marketing analytics consultancy. IPAI competes on **operational analytics** (ERP-sourced, not media-sourced). The consultancy-plus-platform model (29 specialists + custom algorithms) mirrors IPAI's lean team + AI-augmented approach.

### Marketing Vertical Opportunity Map

| Layer | Current Tools | IPAI Opportunity | Sprint |
|---|---|---|---|
| **Campaign execution** | Smartly, Meta, Google | Not competing — client domain | — |
| **Cultural intelligence** | Quilt.AI, Brandwatch | Not competing — research domain | — |
| **Creative research** | Lions MA, WARC | Not competing — strategy domain | — |
| **Media analytics** | DI Romania, Smartly Intelligence | Not competing — media domain | — |
| **Agency operations** | Spreadsheets, Notion, Monday.com | **IPAI wedge** — project control, finance, compliance | R2 |
| **Agency finance** | QuickBooks, Xero, manual | **IPAI wedge** — Odoo + close cockpit + BIR | R2 |
| **Agency reporting** | PowerPoint, manual dashboards | **IPAI wedge** — Genie + gold marts + Pulser summaries | R2 |

**Doctrine:** IPAI does not compete with creative/media/research tools. IPAI owns the **operational backbone** that marketing agencies run on: project finance, close, compliance, resource control, and guided ops intelligence. TBWA\SMP is the proving ground.

### Data Architecture Advantage vs D365

| Concern | D365 (7 steps) | IPAI (2 steps) |
|---|---|---|
| ERP → Lake | ChangeFeed → ADLS Gen2 (deprecated) | PG → Fabric Mirroring (direct) |
| Data format | CDM folders in ADLS | Delta tables in OneLake |
| Auth setup | Entra app + KV + 3 secrets + LCS add-in | Managed Identity (existing) |
| Downstream | Synapse SQL → Power BI | Databricks gold → Genie + Power BI |
| Zero-copy analytics | Not available (data must be copied) | Lakehouse Federation (zero-copy PG read) |

D365 journey: `Export to Data Lake → Synapse Link → Fabric Mirroring` (3 generations)
IPAI journey: `PG Flex → Fabric Mirroring` (direct to current gen)

---

*Generated: 2026-04-18 | Aligned to: ssot/delivery/sprint-isv-alignment.yaml*
