# Azure Service Mapping — InsightPulse AI

> Human-readable view of `ssot/capabilities/azure_service_mapping.yaml`.
> This file is **derived** — edit the YAML source, not this document.

---

## Service Classification

### Keep (Canonical)

| Service | Plane | Role |
|---------|-------|------|
| GitHub | Governance / Control | Code truth |
| Azure DevOps | Governance / Control | Planned truth + release governance |
| VS Code | Experience / Domain Apps | Engineering cockpit |
| Application Insights | Governance / Control | App observability + runtime feedback |
| Azure Monitor | Governance / Control | Infrastructure observability |
| Microsoft Entra ID | Identity / Network / Security | Identity, RBAC, SSO |
| Managed Identities | Identity / Network / Security | Workload authentication |
| Azure Key Vault | Identity / Network / Security | Secrets + key management |
| Azure Front Door | Identity / Network / Security | Edge routing + WAF |
| Azure API Management | Identity / Network / Security | Governed API boundary |
| Odoo CE 19 | Business Systems | Transactional SoR |
| PostgreSQL Flexible Server | Business Systems | Odoo database |
| Azure Databricks | Data Intelligence | Governed data intelligence |
| Unity Catalog | Data Intelligence | Data governance + lineage |
| ADLS Gen2 | Data Intelligence | Lake substrate |
| Microsoft Foundry | Agent / AI Runtime | Hosted agents, eval, tracing |
| Azure Static Web Apps | Experience / Domain Apps | Frontend preview + web apps |
| Azure Container Apps | Experience / Domain Apps | Custom services + backends |
| Azure Functions | Experience / Domain Apps | Event-driven compute |

### Adapt (Selective Use)

| Service | Role | When to Use |
|---------|------|-------------|
| Logic Apps | Integration orchestration | Select workflows only |
| Service Bus | Durable messaging | When async boundary needed |
| Event Grid | Event fanout | When reactive distribution needed |
| Copilot Studio | Business copilot surface | Experience layer only |
| Microsoft Fabric | Semantic/consumption surface | Secondary to Databricks |
| Power Platform | Low-code accelerator | Bounded lightweight workflows |
| App Service | Traditional web host | When SWA/ACA don't fit |

### Defer (Not Runtime Foundations)

| Service | Why Deferred |
|---------|-------------|
| M365 Admin | Admin surface, not product runtime |
| Intune | Endpoint management only |
| Defender | Security ops, not app foundation |
| Portal Guided Deployment | Provisioning reference only |

---

## Capability Lanes

| Lane | Objective | Key Services |
|------|-----------|-------------|
| **App Development** | Fast repo-to-preview-deploy loop | GitHub, DevOps, VS Code, Static Web Apps, Container Apps, Functions, App Insights |
| **Agent SDLC** | Spec → code → review → deploy → observe | GitHub, DevOps, VS Code, Foundry, Container Apps, Functions, App Insights |
| **Data Engineering** | Governed datasets + context products | Databricks, Unity Catalog, ADLS, App Insights |
| **Finance / PPM** | Transactional finance, close, compliance | Odoo, PostgreSQL, Entra, Key Vault, APIM |
| **Marketing** | Campaign planning + measurement | Databricks, Foundry, APIM, Static Web Apps |
| **Retail / Merchandising** | Merch intelligence + operations | Odoo, Databricks, Foundry, APIM, Container Apps |
| **Creative** | Brief → asset → review → publish | Static Web Apps, Container Apps, Foundry, App Insights |
| **People Development** | Learning, builder enablement | VS Code, GitHub, DevOps, Foundry |

---

## Prohibited Misuse

| Service | Do NOT Use As |
|---------|--------------|
| Databricks | Direct transaction authority for finance/Odoo records |
| Foundry | Unrestricted business system write authority |
| APIM | System of record or agent runtime |
| Fabric | Primary data engineering core (Databricks is canonical) |
| Copilot Studio | Core platform runtime or SDLC engine |
| Power Platform | Primary execution core for finance |
| Portal templates | Canonical repo or runtime foundation |

---

## Implementation Priority

1. **P0 Foundation**: GitHub, DevOps, VS Code, Entra, Managed Identities, Key Vault, App Insights, Monitor, Front Door, WAF
2. **P1 Runtime**: Static Web Apps, Container Apps, Functions, APIM, Odoo, PostgreSQL
3. **P2 Intelligence**: Databricks, Unity Catalog, ADLS, Foundry
4. **P3 Selective Adapt**: Logic Apps, Service Bus, Event Grid, Copilot Studio, Fabric, Power Platform

---

*Source: `ssot/capabilities/azure_service_mapping.yaml` (last updated 2026-03-18)*
