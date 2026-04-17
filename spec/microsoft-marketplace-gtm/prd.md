# PRD: Microsoft Marketplace GTM

> Product Requirements Document for the Pulser for Odoo commercial offer in the Partner Center.

---

## 1. Overview
As part of the Microsoft ISV Success Program, InsightPulseAI (Dataverse IT Consultancy) is preparing a **Transactable SaaS offer** for the Azure Commercial Marketplace with a target publication of **Q3 (August-September) 2026**. 

## 2. Business Summary
- **Organization**: Dataverse IT Consultancy / InsightPulseAI (Founder-led team of 5, Philippines-based)
- **Primary Market**: Philippines (with regional/international expansion roadmap)
- **Target Audience**: Small to mid-sized businesses with workflow complexity (Founders, Ops Leaders, Finance/Compliance, Marketing/Media Ops).
- **Core Value**: Guided workflows, reporting, and operational control.

## 3. Offering Scope
The offer encapsulates an *AI-assisted operational platform* structured in four layers:
1. **Odoo on Cloud:** Governed system of record for operational workflows.
2. **Pulser AI Wrapper:** AI-assisted workflow, guidance, summarization, and intelligence layer.
3. **Analytics Plane:** Databricks + Unity Catalog for governed BI and conversational analytics.
4. **Managed Support Services:** Setup, integration, technical ops, and Azure deployment.

## 4. Immediate Roadmap & Blockers
- **Priorities**: Finalizing transactable offer packaging, defining publication sequence (platform -> analytics -> AI), and preparing GTM materials.
- **Roadblocks**: Resolving Azure Sponsorship developer conflicts and architecting the minimum publishable version for a strong first entry.

## 5. Deployment Constraints
All customer deployments driven through the Marketplace transactable flow must instantiate canonical Pulser deployment stamps directly onto Azure (using ACR, ACA, PostgreSQL, Databricks, and Entra ID).

## 6. Microsoft Partner Network Solution Area Mapping
To ensure commercial alignment with Microsoft's unified go-to-market motions (and to maximize Marketplace Co-sell potential), Pulser for Odoo explicitly maps to the three updated Microsoft Cloud Solution Areas:

### 6.1 AI Business Solutions
* **Mapped Components:** Odoo on Cloud (ERP), Pulser AI Wrapper
* **Alignment:** Modernizing Line-of-Business (LOB) applications by infusing Agentic AI workflows (Azure Document Intelligence, specialist Copilot assistants) directly into enterprise operational workflows (AP, Month-End Close, Compliance).

### 6.2 Cloud & AI Platforms
* **Mapped Components:** Databricks Lakehouse, Power BI, Azure Container Apps (ACA), PostgreSQL Flexible server.
* **Alignment:** Delivering scalable, governed data gravity and operational analytics through Unity Catalog and Azure's cloud-native app hosting infrastructure.

### 6.3 Security
* **Mapped Components:** Managed Support Services, Entra ID SSO, Platform Invariants.
* **Alignment:** Enforcing zero-trust principles via Entra ID conditional access, Privileged Identity Management (PIM) for Tier-0 support access, and Azure Key Vault for all runtime secrets.

---

*Last updated: 2026-04-18*
