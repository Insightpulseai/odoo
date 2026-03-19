# Benchmark: Microsoft Cloud Adoption Framework

> Source: Microsoft Cloud Adoption Framework for Azure
>
> Role: Cloud adoption discipline and Azure landing zone architecture benchmark
>
> This is a benchmark --- not an integration contract. It becomes an integration only when an explicit contract is created in docs/contracts/.

---

## Overview

The Microsoft Cloud Adoption Framework (CAF) is a full-lifecycle methodology for cloud adoption on Azure. It provides guidance across 9 phases plus cross-cutting concerns.

### 9 Lifecycle Phases

| Phase | Purpose | Owner Persona |
|-------|---------|---------------|
| **Strategy** | Define business justification, motivations, outcomes | cloud-strategy-advisor |
| **Plan** | Digital estate inventory, adoption plan, skills readiness | cloud-strategy-advisor |
| **Ready** | Azure landing zone design, subscription topology, platform automation | landing-zone-architect |
| **Migrate** | Workload assessment, migration waves, rehost/replatform | cloud-migration-engineer |
| **Modernize** | Application and database modernization, PaaS migration | cloud-migration-engineer |
| **Cloud-native** | Greenfield design, containers, serverless, microservices | cloud-native-architect |
| **Govern** | Azure Policy, cost management, resource consistency, compliance | cloud-governance-operator |
| **Secure** | Zero trust, identity perimeter, network segmentation, threat detection | cloud-security-architect |
| **Manage** | Management baseline, operational fitness, business alignment | cloud-governance-operator |

### Cross-Cutting Concerns

| Area | Purpose |
|------|---------|
| **Well-Architected Framework** | Five pillars: Reliability, Security, Cost Optimization, Operational Excellence, Performance Efficiency |
| **Architecture Center** | Reference architectures, design patterns, best practices |
| **Azure Accelerate** | FastTrack, landing zone accelerators, implementation guides |

---

## Key Decision Frameworks

### 5 Rs of Rationalization

Used during Strategy and Plan phases to categorize workloads:

| R | Pattern | When to use |
|---|---------|-------------|
| **Rehost** | Lift-and-shift to IaaS | Quick migration, minimal change |
| **Refactor** | Minor code changes for PaaS | Exploit managed services without rearchitecting |
| **Rearchitect** | Significant redesign | Unlock cloud-native capabilities |
| **Rebuild** | Rewrite from scratch | Legacy too costly to modify |
| **Replace** | Adopt SaaS | Commercial SaaS is better fit |

### Governance Maturity Model

| Level | Description |
|-------|-------------|
| **Initial** | Ad-hoc, no formal governance |
| **Defined** | Policies documented, manual enforcement |
| **Managed** | Automated policy enforcement via Azure Policy |
| **Optimized** | Continuous improvement, feedback loops, autonomous remediation |

### Operations Maturity

| Level | Description |
|-------|-------------|
| **Management baseline** | Inventory, visibility, operational compliance |
| **Enhanced management** | Platform specialization, workload specialization |
| **Business alignment** | SLA/SLO commitments, operational fitness reviews |

---

## InsightPulseAI Mapping

How CAF concepts map to our platform:

| CAF Concept | InsightPulseAI Equivalent |
|-------------|--------------------------|
| Management group hierarchy | Single subscription, resource groups (`rg-ipai-*`) |
| Landing zone | `rg-ipai-dev` with ACA environment `cae-ipai-dev` |
| Compute platform | Azure Container Apps (not AKS) |
| Edge/ingress | Azure Front Door (`ipai-fd-dev`) |
| Identity platform | Keycloak (transitional) to Microsoft Entra ID |
| Secrets management | Azure Key Vault (`kv-ipai-dev`, `kv-ipai-staging`, `kv-ipai-prod`) |
| Database | Azure Database for PostgreSQL Flexible Server |
| Container registry | `cripaidev`, `ipaiodoodevacr`, `ipaiwebacr` |
| Monitoring | Azure Monitor, Application Insights |
| Cost management | Azure Cost Management (self-hosted philosophy) |
| IaC | Bicep (canonical), Terraform (supplemental) |

### Current State Assessment

| Phase | Maturity | Notes |
|-------|----------|-------|
| Strategy | Defined | Business outcomes documented, cost-minimized philosophy established |
| Plan | Defined | Workload inventory exists but not formalized in CAF plan format |
| Ready | Managed | Landing zone operational with ACA, AFD, KV, managed PG |
| Migrate | Managed | DigitalOcean to Azure migration completed (2026-03-15) |
| Modernize | In progress | Containerized but modernization of individual services ongoing |
| Cloud-native | In progress | ACA-based architecture, not yet fully event-driven |
| Govern | Defined | Resource naming conventions, manual policy enforcement |
| Secure | Defined | Key Vault, managed identity in use; Entra migration pending |
| Manage | Initial | Monitoring exists, formal management baseline not yet established |

---

## Sources

- [Cloud Adoption Framework](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/)
- [CAF Strategy](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/strategy/)
- [CAF Plan](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/plan/)
- [CAF Ready](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/)
- [CAF Migrate](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/migrate/)
- [CAF Modernize](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/modernize/)
- [CAF Govern](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/govern/)
- [CAF Secure](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/secure/)
- [CAF Manage](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/manage/)

## Cross-references

- `agent-platform/ssot/learning/microsoft_caf_skill_map.yaml`
- `agents/knowledge/benchmarks/azure-saas-well-architected.md`
- `agents/skills/azure-deployment-ops/`
- `agents/skills/azure-migration-ops/`
- `.claude/rules/infrastructure.md`
