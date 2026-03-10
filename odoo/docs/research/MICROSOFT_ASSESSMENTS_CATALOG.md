# Microsoft Assessments Portal — Comprehensive Catalog

**Source**: https://learn.microsoft.com/en-us/assessments/
**Browse All**: https://learn.microsoft.com/en-us/assessments/browse/?page=1&pagesize=30
**Research Date**: 2026-03-07

---

## Table of Contents

1. [Platform Overview](#1-platform-overview)
2. [Assessment Categories](#2-assessment-categories)
3. [Well-Architected Framework Assessments](#3-well-architected-framework-assessments)
4. [Cloud Adoption Framework Assessments](#4-cloud-adoption-framework-assessments)
5. [Security Assessments](#5-security-assessments)
6. [AI/ML Readiness Assessments](#6-aiml-readiness-assessments)
7. [Data & Modernization Assessments](#7-data--modernization-assessments)
8. [Sustainability Assessments](#8-sustainability-assessments)
9. [Developer & Platform Engineering Assessments](#9-developer--platform-engineering-assessments)
10. [Dynamics 365 & Power Platform Assessments](#10-dynamics-365--power-platform-assessments)
11. [How Assessments Work](#11-how-assessments-work)
12. [Integration with Azure Advisor](#12-integration-with-azure-advisor)
13. [Free vs Paid](#13-free-vs-paid)
14. [Self-Hosted Relevance](#14-self-hosted-relevance)
15. [Complete Assessment Index](#15-complete-assessment-index)

---

## 1. Platform Overview

Microsoft Assessments is a **free, self-service online platform** where organizations evaluate business strategies, cloud readiness, security posture, and workload architectures through guided questionnaire experiences. The platform produces **curated, personalized guidance reports** with actionable recommendations.

There are **five distinct assessment types** across the Microsoft ecosystem:

| Type | Platform | Purpose |
|------|----------|---------|
| **Microsoft Assessments** | learn.microsoft.com/assessments | Organization/workload evaluation (this catalog) |
| **Practice Assessments** | learn.microsoft.com/credentials | Certification exam preparation |
| **Applied Skills Assessments** | learn.microsoft.com/credentials/applied-skills | Lab-based credential assessments |
| **On-Demand Assessments** | Services Hub | Deep technical health checks (support plan required) |
| **Certification Renewal** | learn.microsoft.com/credentials | Annual renewal assessments |

This document focuses on the first type: **Microsoft Assessments** for organizational and workload evaluation.

---

## 2. Assessment Categories

Assessments are organized into the following major domains:

| Category | Count (approx.) | Description |
|----------|-----------------|-------------|
| Well-Architected Framework | 13+ | Workload design across 5 pillars |
| Cloud Adoption Framework | 5+ | Strategy, migration, governance readiness |
| Security & Zero Trust | 5+ | Security posture, identity, compliance |
| AI/ML Readiness | 3+ | AI strategy, GenAIOps maturity, AI workloads |
| Data & Modernization | 2+ | App/data modernization, data estate |
| Sustainability | 2+ | Green software, ESG data readiness |
| Developer Experience | 3+ | DevOps, developer velocity, platform engineering |
| Dynamics 365 | 3+ | Implementation readiness, feature usage |
| Power Platform | 3+ | Adoption, solution assessment, ISV readiness |
| FinOps | 1+ | Cloud cost optimization |
| Industry (Healthcare, etc.) | 1+ | Vertical-specific assessments |
| Partner-specific | 3+ | Microsoft Partner program assessments |

The browsable catalog spans **2+ pages of 30 assessments each**, totaling approximately **50-60+ assessments**.

---

## 3. Well-Architected Framework Assessments

The **Azure Well-Architected Framework (WAF)** is the cornerstone assessment category. All WAF assessments evaluate workloads across five pillars:

- **Reliability** -- Resilience, availability, disaster recovery
- **Security** -- Identity, network, data protection
- **Cost Optimization** -- Efficiency, right-sizing, waste elimination
- **Operational Excellence** -- Monitoring, deployment, automation
- **Performance Efficiency** -- Scaling, caching, optimization

### 3.1 Core WAF Assessments

| Assessment | URL | Description |
|------------|-----|-------------|
| **Azure Well-Architected Review** | [Link](https://learn.microsoft.com/en-us/assessments/azure-architecture-review/) | Core ~60 question assessment across all 5 pillars. The flagship assessment. |
| **WAF Maturity Model Assessment** | [Link](https://learn.microsoft.com/en-us/assessments/af7d9889-8cb2-4b8b-b6bb-e5a2e2f2a59c/) | Structured path to improve workload maturity level with incremental recommendations. For startups through enterprises. |
| **Go-Live Well-Architected Review** | [Link](https://learn.microsoft.com/en-us/assessments/b0f9a229-5f82-4f19-ae61-b7be31131f4e/) | Holistic evaluation of Azure workload readiness for production go-live across all 5 pillars. |

### 3.2 Workload-Specific WAF Assessments

| Assessment | URL | Target Workload |
|------------|-----|-----------------|
| **Data Services WAF Review** | [Link](https://learn.microsoft.com/en-us/assessments/azure-architecture-review-data/) | Data platform workloads |
| **AI Workload WAF Review** | [Link](https://learn.microsoft.com/en-us/assessments/ea306cce-c7fa-4a2b-89a6-bfefba6a9cf4/) | AI/ML workloads in production |
| **Azure Local WAF Review** | [Link](https://learn.microsoft.com/en-us/assessments/d8f04a92-c8b9-4ae7-8e51-61b8a1035942/) | Azure Local (formerly Azure Stack HCI) hybrid workloads |
| **Azure Virtual Desktop WAF** | [Link](https://learn.microsoft.com/en-us/assessments/1ef67c4e-b8d1-4193-b850-d192089ae33d/) | Virtual desktop infrastructure |
| **Azure VMware Solution WAF** | [Link](https://learn.microsoft.com/en-us/assessments/2d85e883-bdc4-4854-aaf0-df72c4bcee15/) | VMware workloads on Azure |
| **Sustainability WAF Review** | [Link](https://learn.microsoft.com/en-us/assessments/a24b1079-29a4-4d22-b678-376e84884f76/) | Carbon/energy optimization lens |
| **SaaS Workload Assessment** | [WAF SaaS](https://learn.microsoft.com/en-us/azure/well-architected/saas/assessment) | ISV SaaS applications on Azure |
| **SAP on Azure** | Via WAF Review | SAP workload design (select during WAF Review) |
| **IoT Workloads** | Via WAF Review | IoT solutions (select during WAF Review) |
| **Azure Machine Learning** | Via WAF Review | ML workloads (select during WAF Review) |
| **Mission Critical Workloads** | Via WAF Review | High-availability critical systems |
| **Azure Stack Hub** (Preview) | Via WAF Review | Azure Stack Hub performance |

### 3.3 WAF Assessment Details

**Format**:
- ~60 multiple choice / multiple response questions
- Pillar prioritization step at the beginning
- Collaborative team exercise (recommended)
- Approximately 30-60 minutes to complete

**Scoring**:
- Repeatable baseline score per pillar
- Milestone tracking for progress over time
- Maturity levels (varies by assessment)
- Risk scoring per recommendation

**Output**:
- Personalized recommendation report
- Links to supporting documentation
- Exportable CSV of recommendations
- Integration with Azure DevOps / GitHub backlogs (via DevOps tooling scripts)
- Azure Advisor score update within ~8 hours

---

## 4. Cloud Adoption Framework Assessments

The **Cloud Adoption Framework (CAF)** assessments cover organizational readiness for cloud adoption.

| Assessment | URL | Description |
|------------|-----|-------------|
| **Cloud Adoption Strategy Evaluator** | [Assessments Portal](https://learn.microsoft.com/en-us/assessments/) | Evaluates strategy across motivations, business outcomes, financial considerations, and technical considerations for business case creation. |
| **Strategic Migration Assessment and Readiness Tool (SMART)** | [Assessments Portal](https://learn.microsoft.com/en-us/assessments/) | Evaluates organizational preparedness for cloud migration at scale. Covers business planning, training, security, and governance. |
| **Cloud Journey Tracker** | [Assessments Portal](https://learn.microsoft.com/en-us/assessments/) | Identifies cloud adoption path and recommends relevant CAF content. |
| **Governance Benchmark** | [Link](https://learn.microsoft.com/en-us/assessments/b1891add-7646-4d60-a875-32a4ab26327e/) | Identifies gaps in current governance posture. Produces personalized benchmark report against governance disciplines: cost management, security baseline, resource consistency, identity baseline, deployment automation. |
| **Landing Zone Review** | [Assessments Portal](https://learn.microsoft.com/en-us/assessments/) | Reviews Azure platform readiness and landing zone plans. Designed for customers with 2+ years Azure experience. |

### CAF Methodology Areas Covered

- **Strategy**: Motivations, outcomes, financial justification
- **Plan**: Digital estate, skills readiness, organizational alignment
- **Ready**: Landing zones, Azure setup
- **Migrate**: Assessment, deployment, optimization (rehost/refactor/rearchitect/rebuild/replace)
- **Innovate**: Build new cloud-native solutions
- **Govern**: Cost, security, consistency, identity, automation disciplines
- **Manage**: Operations baseline, platform operations
- **Secure**: Zero Trust, security baseline, incident response

---

## 5. Security Assessments

### 5.1 Microsoft Assessments Portal (learn.microsoft.com/assessments)

| Assessment | URL | Description |
|------------|-----|-------------|
| **Cloud Adoption Security Assessment (CASA)** | [Link](https://learn.microsoft.com/en-us/assessments/31e5d42d-49b2-4892-b7c7-78689f3518f5/) | Evaluates cloud security maturity across: security teams/roles, posture modernization, incident preparedness, confidentiality, integrity, availability, and security sustainment. Aligned with CAF Secure Methodology. |
| **Data Security for Copilot for Microsoft 365** | [Link](https://learn.microsoft.com/en-us/assessments/dde5dcfc-77d3-4f71-aa3f-cc98fa893e99/) | Partner-focused. Evaluates data security governance readiness for Copilot M365 deployments. |

### 5.2 Zero Trust Assessments (Separate Tools)

| Tool | URL | Description |
|------|-----|-------------|
| **Zero Trust Maturity Assessment Quiz** | [Link](https://www.microsoft.com/en-us/security/business/zero-trust/maturity-model-assessment-tool) | Online interactive quiz evaluating maturity across all Zero Trust pillars. Produces maturity score and recommendations. |
| **Zero Trust Assessment (PowerShell)** | [Link](https://learn.microsoft.com/en-us/security/zero-trust/assessment/overview) | **Automated** PowerShell tool that scans Microsoft Entra + Intune configurations against security baselines. Produces detailed HTML report. |
| **Zero Trust Maturity Questionnaire** | [Download](https://www.microsoft.com/en-us/download/details.aspx?id=103935) | Downloadable Excel workbook. ~10 questions per pillar across 6 pillars. Produces radar chart. |
| **Zero Trust Workshop** | [GitHub](https://microsoft.github.io/zerotrustassessment/docs/intro) | Open-source workshop framework for structured Zero Trust evaluation. |

### 5.3 Zero Trust Assessment (PowerShell) -- Deep Dive

**What it is**: An open-source, read-only PowerShell tool that automatically tests **hundreds** of security configuration items in your Microsoft 365/Azure tenant.

**Pillars currently covered**:
- Identity (Entra ID, Conditional Access, authentication methods, audit logs)
- Devices (Windows enrollment, compliance policies, app protection)
- (Applications, Network, Data, Infrastructure -- planned for future releases)

**Standards referenced**: NIST, CISA, CIS benchmarks, Microsoft internal baselines, Secure Future Initiative (SFI)

**How to run**:
```powershell
Install-Module ZeroTrustAssessment -Scope CurrentUser
Connect-ZtAssessment
Invoke-ZtAssessment
```

**Requirements**: PowerShell 7.0+, Global Administrator (first run) or Global Reader (subsequent runs)

**Output**: Detailed HTML report showing pass/fail per configuration item with direct links to remediation in the admin portal.

**Duration**: 20-30 min (small tenant) to 24+ hours (very large tenants)

### 5.4 CISA Zero Trust Maturity Model (Microsoft Guidance)

Microsoft provides detailed guidance mapping to the **CISA Zero Trust Maturity Model** with four maturity levels:

| Level | Description |
|-------|-------------|
| **Traditional** | Starting point; assessment and gap identification |
| **Initial** | Automation in attribute assignment, lifecycle management, initial cross-pillar integration |
| **Advanced** | Centralized identity management, integrated policy enforcement, near real-time risk assessments |
| **Optimal** | Fully automated lifecycle management, dynamic JEA/JIT access controls |

---

## 6. AI/ML Readiness Assessments

| Assessment | URL | Description |
|------------|-----|-------------|
| **AI Readiness Assessment** | [Link](https://learn.microsoft.com/en-us/assessments/94f1c697-9ba7-4d47-ad83-7c6bd94b1505/) | Evaluates AI adoption preparedness across 7 pillars: Business Strategy, AI Governance & Security, Data Foundations, AI Strategy & Experience, Organization & Culture, Infrastructure for AI, Model Management. |
| **GenAIOps Maturity Model Assessment** | [Link](https://learn.microsoft.com/en-us/assessments/e14e1e9f-d339-4d7e-b2bb-24f056cf08b6/) | Evaluates generative AI operations maturity. Produces maturity ranking with process improvement recommendations and Microsoft resource links. |
| **AI Workload WAF Review** | [Link](https://learn.microsoft.com/en-us/assessments/ea306cce-c7fa-4a2b-89a6-bfefba6a9cf4/) | Well-Architected Framework perspective on AI workloads in production. Assesses key technical design areas. |
| **AI Learning Journey** | [Link](https://learn.microsoft.com/en-us/assessments/1c032171-8ca0-4032-8962-a38a5cc424a8/) | Personal learning assessment for AI skills -- from basics to building solutions. |

### AI Readiness Maturity Stages

The AI Readiness Assessment categorizes organizations into five stages:

| Stage | Focus |
|-------|-------|
| **Exploring** | Build AI strategy; learn key AI concepts |
| **Planning** | Formalize business strategy; prioritize AI projects |
| **Implementing** | Leadership support; scale AI expertise |
| **Scaling** | Create culture of innovation; operationalize AI |
| **Realizing** | Most advanced; fully integrated AI-driven operations |

### Related (Non-Assessments Portal)

- **Forrester AI and Low-Code Readiness Assessment** (commissioned by Microsoft) -- Evaluates low-code maturity, AI readiness, data security governance
- **Enterprise AI Maturity in Five Steps** (Microsoft Inside Track) -- Internal Microsoft framework
- **AI Workload WAF Assessment** (learn.microsoft.com/azure/well-architected/ai/assessment) -- Detailed WAF perspective

---

## 7. Data & Modernization Assessments

| Assessment | URL | Description |
|------------|-----|-------------|
| **App and Data Modernization Readiness Tool** | [Link](https://learn.microsoft.com/en-us/assessments/50adbf76-60fb-47ce-a787-f9d5f52f6a48/) | First step in modernizing workloads. Reviews Azure platform readiness, landing zone plans, and adoption strategy. Designed for customers with 2+ years experience but also helps new Azure users identify investment areas. |
| **Data Services WAF Review** | [Link](https://learn.microsoft.com/en-us/assessments/azure-architecture-review-data/) | Well-Architected Framework assessment specifically for data platform workloads. |

---

## 8. Sustainability Assessments

| Assessment | URL | Description |
|------------|-----|-------------|
| **Sustainability Well-Architected Review** | [Link](https://learn.microsoft.com/en-us/assessments/a24b1079-29a4-4d22-b678-376e84884f76/) | Examines workloads through sustainability lens. Curated recommendations for carbon/energy optimization. |
| **Microsoft Cloud for Sustainability Adoption Guide** | [Link](https://learn.microsoft.com/en-us/assessments/9dc58c1c-c4a2-49df-b986-92f340e6bd89/) | Partner-focused. Self-assess sustainability proficiency, training readiness, marketplace offer publishing, and cosell acceleration. |
| **ESG Data Readiness Assessment** | [Assessments Portal](https://learn.microsoft.com/en-us/assessments/) | Gauges data readiness for ESG reporting with personalized recommendations. |

### Related Microsoft Sustainability Tools

- **Emissions Impact Dashboard** -- Calculate cloud footprint for Azure and Microsoft 365
- **Microsoft Sustainability Manager** -- Measure/accelerate sustainability goals across ESG domains
- **Sustainability Data Solutions in Microsoft Fabric** -- Centralize ESG data estate with extensible data model
- **Green Software Foundation principles** -- Referenced in sustainability assessments

---

## 9. Developer & Platform Engineering Assessments

| Assessment | URL | Description |
|------------|-----|-------------|
| **DevOps Capability Assessment** | [Link](https://learn.microsoft.com/en-us/assessments/56ec577c-acb6-4c7b-ad13-e224b0846153/) | Evaluates capabilities across entire software release lifecycle. Identifies improvement opportunities based on Microsoft DevOps practices. |
| **Developer Velocity Assessment** | [Link](https://learn.microsoft.com/en-us/assessments/e50f7040-f235-4360-9d1d-cf753e12fed1/) | Discovers Developer Velocity Index (DVI) score. Provides guidance to boost business performance through developer experience improvements. |
| **Platform Engineering Technical Assessment** | [Link](https://learn.microsoft.com/en-us/assessments/86bf5228-7b58-4854-b932-ac71402e0be4/) | Assesses platform engineering maturity. Recommendations for creating optimized, secure developer experiences using Microsoft and third-party building blocks. |
| **FinOps Review (New)** | [Link](https://learn.microsoft.com/en-us/assessments/60c02533-b280-4dec-ac5f-3f10cdd238b9/) | Based on FinOps Foundation framework. Assesses organizational capability gaps for maximizing cloud business value using FinOps best practices. |

---

## 10. Dynamics 365 & Power Platform Assessments

### Dynamics 365

| Assessment | URL | Description |
|------------|-----|-------------|
| **Implementation Readiness Review** | [Link](https://learn.microsoft.com/en-us/assessments/561d1647-3a8a-43b8-b749-fa5cdd29a8f1/) | Proactive readiness check for D365 implementation. For senior stakeholders, PMs, project leaders. Best taken during early discovery/pre-kickoff. |
| **Finance & Operations Features Usage Excellence** | [Link](https://learn.microsoft.com/en-us/assessments/388159e6-55f1-4287-86fa-09032f5ad812/) | Enablement/awareness for implementation teams on essential F&O features and options. |
| **Finance & Operations Presales Excellence** | [Link](https://learn.microsoft.com/en-us/assessments/bcb90547-d75e-47cd-b133-4c5340e68fc2/) | Partner-focused. Effective sales methods and Microsoft-provided resources for D365 F&O presales. |

### Power Platform

| Assessment | URL | Description |
|------------|-----|-------------|
| **Power Platform Adoption Assessment** | [Link](https://learn.microsoft.com/en-us/assessments/3c62fd23-9d36-491c-8941-26d5553365f8/) | Comprehensive evaluation of Power Platform usage. Identifies optimization opportunities and best practices. |
| **Power Platform Solution Assessment** (Preview) | [Link](https://learn.microsoft.com/en-us/assessments/a5c3b65d-bf7e-4743-850a-0437ae692690/) | Covers solution functionality, user experience, alignment with business goals. Provides actionable insights. |
| **ISV Power Platform Readiness** | [Link](https://learn.microsoft.com/en-us/assessments/66e68487-b748-4576-a1b6-9cd2034407ab/) | Partner/ISV-focused. Evaluates comprehension of partner requirements, technical prerequisites, and topic readiness. |
| **Power Platform Copilot & AI Features** | [Assessments Portal](https://learn.microsoft.com/en-us/assessments/) | Enablement for Copilot and AI-infused features in Power Platform. |

### Other Product Assessments

| Assessment | URL | Description |
|------------|-----|-------------|
| **Microsoft Cloud for Healthcare Learner Self-Assessment** | [Assessments Portal](https://learn.microsoft.com/en-us/assessments/) | Guides healthcare learning journey with recommendations on learning paths and modules. |

---

## 11. How Assessments Work

### Format

All Microsoft Assessments follow a consistent pattern:

1. **Sign in** with Microsoft account (free)
2. **Select assessment** from the browse catalog
3. **Answer questions** -- multiple choice / multiple response, typically 20-60 questions
4. **Prioritize** (for WAF assessments) -- rank pillars by business importance
5. **Receive report** -- personalized recommendations with links to documentation
6. **Export** -- CSV download for backlog integration
7. **Track progress** -- milestone feature for re-assessment over time

### Scoring Model

- **Pillar-based scores** -- Separate scores per assessment dimension (e.g., Reliability: 72%, Security: 85%)
- **Overall maturity level** -- Categorical (e.g., Exploring / Planning / Implementing / Scaling / Realizing for AI Readiness)
- **Moving baseline** -- Scores evolve with your workload; designed for repeated assessment
- **Risk-weighted** -- Recommendations include risk level and user impact

### Output Reports

| Output | Format | Description |
|--------|--------|-------------|
| Online report | Web | Interactive recommendations with links |
| CSV export | .csv | Offline recommendations for backlog import |
| HTML report | .html | Zero Trust Assessment produces standalone HTML |
| Radar chart | Visual | Zero Trust Excel questionnaire |
| Advisor score | Azure | WAF results feed into Azure Advisor within 8 hours |

### Backlog Integration

Microsoft provides DevOps tooling scripts to import WAF CSV recommendations into:
- Azure DevOps work items
- GitHub Issues

---

## 12. Integration with Azure Advisor

### How It Works

```
WAF Assessment completion
    |
    v (max 8 hours)
Azure Advisor receives recommendations
    |
    v
Advisor Score updated (0-100% per pillar)
    |
    v
Recommendations appear in Azure Portal
    |
    v
Act on recommendations -> Re-assess -> Score improves
```

### Azure Advisor Score

- **Overall score** broken into 5 WAF pillar categories (percentages)
- **100%** = all assessed resources follow Advisor best practices
- **0%** = none follow recommendations
- Postponed/dismissed recommendations excluded from score calculation
- Score refreshes periodically based on resource configuration and usage telemetry

### Advisor WAF Assessment Features

- Pull Azure Advisor recommendations directly into the WAF assessment experience
- Scope recommendations to specific Azure subscription or resource group
- Track improvements through Advisor score over time
- Prioritize recommendations by impact score

### Continuous Improvement Cycle

1. Take WAF Assessment
2. Recommendations appear in Azure Advisor (~8 hours)
3. Implement recommendations
4. Advisor score improves
5. Re-run assessment using milestone tracking
6. Compare against previous baseline
7. Repeat

---

## 13. Free vs Paid

### Microsoft Assessments (learn.microsoft.com/assessments)

**ALL assessments on the Microsoft Assessments portal are FREE.**

| Tier | Cost | What You Get |
|------|------|-------------|
| Microsoft Assessments | Free | All questionnaire-based assessments, recommendations, CSV export |
| Azure Advisor | Free (with Azure subscription) | WAF assessment results integration, Advisor score |
| Zero Trust PowerShell Tool | Free (open source) | Automated tenant security scan |
| Zero Trust Maturity Quiz | Free | Online interactive maturity evaluation |
| Zero Trust Excel Questionnaire | Free (download) | Offline self-assessment workbook |

### On-Demand Assessments (Services Hub -- different platform)

| Tier | Cost | What You Get |
|------|------|-------------|
| On-Demand Assessments | Included with Microsoft Support plan | Deep technical health checks, Azure Log Analytics integration |
| Azure usage | Up to $10 USD/year included | Log Analytics workspace costs |
| Additional Azure services | Pay-as-you-go | If you exceed the included $10 |

### Practice/Certification Assessments (different platform)

| Tier | Cost |
|------|------|
| Practice Assessments | Free (unlimited retakes) |
| Certification Exams | $165-$395 USD per exam |
| Applied Skills Assessments | Free |

---

## 14. Self-Hosted Relevance

### Can These Frameworks Apply to Non-Azure Infrastructure?

**Short answer**: The **conceptual pillars are universally applicable**; the **tooling and specific recommendations are Azure-centric**.

### Detailed Breakdown

| Assessment | Self-Hosted Applicability | Notes |
|------------|--------------------------|-------|
| **WAF 5 Pillars (concepts)** | HIGH | Reliability, Security, Cost, Ops Excellence, Performance -- these are universal architectural principles |
| **WAF Assessment Tool** | LOW | Questions reference Azure services; Advisor integration is Azure-only |
| **Cloud Adoption Strategy** | MEDIUM | Strategy/governance concepts apply to any cloud or self-hosted migration |
| **Governance Benchmark** | MEDIUM | Governance disciplines (cost, security, identity, consistency) are universal |
| **Zero Trust Maturity Quiz** | HIGH | Zero Trust principles apply to any infrastructure |
| **Zero Trust PowerShell Tool** | LOW | Scans Microsoft Entra/Intune only |
| **CISA ZT Maturity Model** | HIGH | CISA framework is vendor-agnostic |
| **AI Readiness Assessment** | HIGH | Business Strategy, Governance, Culture pillars are vendor-neutral |
| **GenAIOps Maturity** | MEDIUM-HIGH | MLOps/GenAIOps concepts apply broadly |
| **DevOps Capability** | HIGH | DevOps practices are platform-agnostic |
| **Developer Velocity** | HIGH | DVI concepts apply to any development organization |
| **Platform Engineering** | MEDIUM-HIGH | Platform engineering concepts are universal; some recommendations Azure-specific |
| **FinOps Review** | MEDIUM | FinOps Foundation framework applies to any cloud; specific tooling is Azure-focused |
| **Sustainability WAF** | MEDIUM | Green software principles are universal; implementation guidance is Azure-specific |
| **Data Modernization** | LOW-MEDIUM | Focused on Azure migration; some readiness concepts are general |

### Applying WAF Pillars to Self-Hosted (e.g., DigitalOcean + Odoo)

The **five pillars** translate directly to self-hosted infrastructure:

| WAF Pillar | Self-Hosted Equivalent |
|------------|----------------------|
| **Reliability** | Backup strategy, health checks, failover plans, monitoring (Prometheus/Grafana) |
| **Security** | Firewall rules, TLS, secrets management, Keycloak SSO, vulnerability scanning |
| **Cost Optimization** | Right-sizing droplets, reserved instances, eliminating unused resources |
| **Operational Excellence** | CI/CD pipelines, IaC (Terraform), runbooks, incident response |
| **Performance Efficiency** | Load testing, caching (Redis), CDN, database query optimization |

### Recommended Approach for Self-Hosted Teams

1. **Use the Zero Trust Maturity Quiz** for security baseline (vendor-agnostic)
2. **Use the AI Readiness Assessment** for AI strategy (vendor-agnostic)
3. **Use the DevOps Capability Assessment** for DevOps maturity (platform-agnostic)
4. **Adapt WAF pillar questions** into your own self-assessment checklist
5. **Use the CISA Zero Trust Maturity Model** directly (government-standard, vendor-neutral)
6. **Download the Zero Trust Excel Questionnaire** and adapt for non-Microsoft environments

---

## 15. Complete Assessment Index

### All Known Assessments on learn.microsoft.com/assessments

| # | Assessment Name | Category | Audience | URL |
|---|----------------|----------|----------|-----|
| 1 | Azure Well-Architected Review | WAF | All | [Link](https://learn.microsoft.com/en-us/assessments/azure-architecture-review/) |
| 2 | WAF Maturity Model Assessment | WAF | All | [Link](https://learn.microsoft.com/en-us/assessments/af7d9889-8cb2-4b8b-b6bb-e5a2e2f2a59c/) |
| 3 | Go-Live WAF Review | WAF | All | [Link](https://learn.microsoft.com/en-us/assessments/b0f9a229-5f82-4f19-ae61-b7be31131f4e/) |
| 4 | Data Services WAF Review | WAF | Data teams | [Link](https://learn.microsoft.com/en-us/assessments/azure-architecture-review-data/) |
| 5 | AI Workload WAF Review | WAF / AI | AI teams | [Link](https://learn.microsoft.com/en-us/assessments/ea306cce-c7fa-4a2b-89a6-bfefba6a9cf4/) |
| 6 | Azure Local WAF Review | WAF | Hybrid | [Link](https://learn.microsoft.com/en-us/assessments/d8f04a92-c8b9-4ae7-8e51-61b8a1035942/) |
| 7 | Azure Virtual Desktop WAF | WAF | VDI | [Link](https://learn.microsoft.com/en-us/assessments/1ef67c4e-b8d1-4193-b850-d192089ae33d/) |
| 8 | Azure VMware Solution WAF | WAF | VMware | [Link](https://learn.microsoft.com/en-us/assessments/2d85e883-bdc4-4854-aaf0-df72c4bcee15/) |
| 9 | Sustainability WAF Review | WAF / Sustainability | All | [Link](https://learn.microsoft.com/en-us/assessments/a24b1079-29a4-4d22-b678-376e84884f76/) |
| 10 | Cloud Adoption Strategy Evaluator | CAF | Strategy | [Assessments Portal](https://learn.microsoft.com/en-us/assessments/) |
| 11 | SMART (Migration Readiness) | CAF | Migration | [Assessments Portal](https://learn.microsoft.com/en-us/assessments/) |
| 12 | Cloud Journey Tracker | CAF | All | [Assessments Portal](https://learn.microsoft.com/en-us/assessments/) |
| 13 | Cloud Governance Benchmark | CAF | Governance | [Link](https://learn.microsoft.com/en-us/assessments/b1891add-7646-4d60-a875-32a4ab26327e/) |
| 14 | Landing Zone Review | CAF | Platform | [Assessments Portal](https://learn.microsoft.com/en-us/assessments/) |
| 15 | Cloud Adoption Security Assessment (CASA) | Security | Security | [Link](https://learn.microsoft.com/en-us/assessments/31e5d42d-49b2-4892-b7c7-78689f3518f5/) |
| 16 | Data Security for Copilot M365 | Security | Partners | [Link](https://learn.microsoft.com/en-us/assessments/dde5dcfc-77d3-4f71-aa3f-cc98fa893e99/) |
| 17 | AI Readiness Assessment | AI | All | [Link](https://learn.microsoft.com/en-us/assessments/94f1c697-9ba7-4d47-ad83-7c6bd94b1505/) |
| 18 | GenAIOps Maturity Model | AI | AI/ML Ops | [Link](https://learn.microsoft.com/en-us/assessments/e14e1e9f-d339-4d7e-b2bb-24f056cf08b6/) |
| 19 | AI Learning Journey | AI / Learning | Individual | [Link](https://learn.microsoft.com/en-us/assessments/1c032171-8ca0-4032-8962-a38a5cc424a8/) |
| 20 | App & Data Modernization Readiness | Data | All | [Link](https://learn.microsoft.com/en-us/assessments/50adbf76-60fb-47ce-a787-f9d5f52f6a48/) |
| 21 | Cloud for Sustainability Adoption | Sustainability | Partners | [Link](https://learn.microsoft.com/en-us/assessments/9dc58c1c-c4a2-49df-b986-92f340e6bd89/) |
| 22 | DevOps Capability Assessment | Developer | DevOps teams | [Link](https://learn.microsoft.com/en-us/assessments/56ec577c-acb6-4c7b-ad13-e224b0846153/) |
| 23 | Developer Velocity Assessment | Developer | Dev teams | [Link](https://learn.microsoft.com/en-us/assessments/e50f7040-f235-4360-9d1d-cf753e12fed1/) |
| 24 | Platform Engineering Technical | Developer | Platform eng | [Link](https://learn.microsoft.com/en-us/assessments/86bf5228-7b58-4854-b932-ac71402e0be4/) |
| 25 | FinOps Review (New) | FinOps | Finance/Ops | [Link](https://learn.microsoft.com/en-us/assessments/60c02533-b280-4dec-ac5f-3f10cdd238b9/) |
| 26 | D365 Implementation Readiness | Dynamics 365 | PM/Leaders | [Link](https://learn.microsoft.com/en-us/assessments/561d1647-3a8a-43b8-b749-fa5cdd29a8f1/) |
| 27 | D365 F&O Features Usage Excellence | Dynamics 365 | Impl teams | [Link](https://learn.microsoft.com/en-us/assessments/388159e6-55f1-4287-86fa-09032f5ad812/) |
| 28 | D365 F&O Presales Excellence | Dynamics 365 | Partners | [Link](https://learn.microsoft.com/en-us/assessments/bcb90547-d75e-47cd-b133-4c5340e68fc2/) |
| 29 | Power Platform Adoption | Power Platform | All | [Link](https://learn.microsoft.com/en-us/assessments/3c62fd23-9d36-491c-8941-26d5553365f8/) |
| 30 | Power Platform Solution (Preview) | Power Platform | All | [Link](https://learn.microsoft.com/en-us/assessments/a5c3b65d-bf7e-4743-850a-0437ae692690/) |
| 31 | ISV Power Platform Readiness | Power Platform | ISVs | [Link](https://learn.microsoft.com/en-us/assessments/66e68487-b748-4576-a1b6-9cd2034407ab/) |
| 32 | Healthcare Learner Self-Assessment | Industry | Healthcare | [Assessments Portal](https://learn.microsoft.com/en-us/assessments/) |

### Separate Security Assessment Tools (Outside Assessments Portal)

| # | Tool | Platform | URL |
|---|------|----------|-----|
| S1 | Zero Trust Maturity Assessment Quiz | microsoft.com/security | [Link](https://www.microsoft.com/en-us/security/business/zero-trust/maturity-model-assessment-tool) |
| S2 | Zero Trust Assessment (PowerShell) | PowerShell Gallery | [Link](https://learn.microsoft.com/en-us/security/zero-trust/assessment/overview) |
| S3 | Zero Trust Maturity Questionnaire | Download Center | [Link](https://www.microsoft.com/en-us/download/details.aspx?id=103935) |
| S4 | Zero Trust Workshop | GitHub | [Link](https://microsoft.github.io/zerotrustassessment/docs/intro) |

---

## Sources

- [Microsoft Assessments Portal](https://learn.microsoft.com/en-us/assessments/)
- [Browse All Assessments](https://learn.microsoft.com/en-us/assessments/browse/?page=1&pagesize=30)
- [Microsoft Assessments FAQ](https://learn.microsoft.com/en-us/assessments/support/)
- [Azure Well-Architected Review](https://learn.microsoft.com/en-us/assessments/azure-architecture-review/)
- [Complete a WAF Assessment](https://learn.microsoft.com/en-us/azure/well-architected/design-guides/implementing-recommendations)
- [WAF Assessments in Azure Advisor](https://learn.microsoft.com/en-us/azure/advisor/advisor-assessments)
- [Azure Advisor Score](https://learn.microsoft.com/en-us/azure/advisor/advisor-score)
- [Cloud Adoption Framework](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/)
- [Zero Trust Assessment Overview](https://learn.microsoft.com/en-us/security/zero-trust/assessment/overview)
- [Zero Trust Maturity Quiz](https://www.microsoft.com/en-us/security/business/zero-trust/maturity-model-assessment-tool)
- [CISA Zero Trust Maturity Model - Identity](https://learn.microsoft.com/en-us/security/zero-trust/cisa-zero-trust-maturity-model-identity)
- [AI Readiness Assessment](https://learn.microsoft.com/en-us/assessments/94f1c697-9ba7-4d47-ad83-7c6bd94b1505/)
- [GenAIOps Maturity Model](https://learn.microsoft.com/en-us/assessments/e14e1e9f-d339-4d7e-b2bb-24f056cf08b6/)
- [AI Workload WAF Assessment](https://learn.microsoft.com/en-us/azure/well-architected/ai/assessment)
- [App and Data Modernization Readiness](https://learn.microsoft.com/en-us/assessments/50adbf76-60fb-47ce-a787-f9d5f52f6a48/)
- [Sustainability WAF Review](https://learn.microsoft.com/en-us/assessments/a24b1079-29a4-4d22-b678-376e84884f76/)
- [On-Demand Assessments FAQ](https://learn.microsoft.com/en-us/services-hub/unified/health/assessments-faq)
- [What is the Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/what-is-well-architected-framework)
- [Azure Local WAF Review](https://learn.microsoft.com/en-us/assessments/d8f04a92-c8b9-4ae7-8e51-61b8a1035942/)
- [SaaS Workload Assessment](https://learn.microsoft.com/en-us/azure/well-architected/saas/assessment)
- [Microsoft Blog: AI Readiness](https://www.microsoft.com/en-us/microsoft-cloud/blog/2024/11/06/a-strategic-approach-to-assessing-your-ai-readiness/)
- [Zero Trust Assessment Progress Tracking](https://learn.microsoft.com/en-us/security/zero-trust/zero-trust-assessment-progress-tracking-resources)
