# Microsoft Certification Poster (March 2026) — Persona Benchmark Index

> **Source**: Microsoft certification poster, March 2026 edition
> **Purpose**: Top-level certification benchmark map for skills and personas. Not a study list, not a runtime contract.
> **Type**: Benchmark maturity taxonomy for persona capability lanes

---

## Certification Lanes

| Lane | Description |
|------|-------------|
| **Fundamentals** | Entry-level awareness — validates literacy, not execution |
| **Role-based** | Practitioner depth — validates hands-on capability in a job function |
| **Specialty** | Niche depth — validates advanced capability in a narrow domain |
| **Business** | Business-side AI/transformation — validates strategic and change-management fluency |

## Major Domains

| Domain | Scope |
|--------|-------|
| **Cloud & AI Platforms** | Azure infrastructure, networking, identity, AI services, DevOps, developer tools |
| **AI Business Solutions** | Copilot, agents, Dynamics 365, Power Platform, business transformation |
| **Security** | Identity governance, security operations, information protection, cybersecurity architecture |

---

## How to Use

Tag personas and skill families with maturity level (`fundamentals` / `role_based` / `specialty` / `business`).

These are **benchmark references** for what each persona should be capable of — NOT implementation objects, module names, or runtime dependencies.

A persona tagged with `AZ-305` does not mean "must pass AZ-305" — it means the persona's expected capability surface overlaps with what AZ-305 validates.

---

## Persona-to-Certification Benchmark Clusters

### 1. product-manager

| Cert | Name | Lane |
|------|------|------|
| AB-730 | AI Business Professional | Business |
| AB-731 | AI Transformation Leader | Business |
| AB-900 | Microsoft 365 Copilot and Agent Administration Fundamentals | Fundamentals |

**Why**: Clearest business-side AI/product/change-management signals. AB-730 and AB-731 validate the ability to frame AI business cases, measure transformation impact, and govern AI adoption — the core product-manager capability surface.

---

### 2. portfolio-manager

| Cert | Name | Lane |
|------|------|------|
| AB-731 | AI Transformation Leader | Business |
| PL-600 | Power Platform Solution Architect Expert | Role-based |
| MB-700 | Dynamics 365: Finance and Operations Apps Solution Architect Expert | Role-based |

**Why**: Portfolio structure, solution framing, multi-workstream planning. PL-600 and MB-700 validate the ability to decompose a platform into governed workstreams — the portfolio-manager's core discipline.

---

### 3. azure-platform-admin

Maps to: `odoo-platform-admin`, `azure-deployment-ops`, `azure-resiliency-ops`

| Cert | Name | Lane |
|------|------|------|
| AZ-104 | Azure Administrator Associate | Role-based |
| AZ-305 | Azure Solutions Architect Expert | Role-based |
| AZ-400 | DevOps Engineer Expert | Role-based |
| AZ-700 | Azure Network Engineer Associate | Role-based |
| AZ-500 | Azure Security Engineer Associate | Role-based |
| SC-300 | Identity and Access Administrator Associate | Role-based |
| SC-100 | Cybersecurity Architect Expert | Role-based |

**Why**: Core Azure platform, networking, identity, security, delivery. This is the broadest cluster because platform-admin owns the widest surface area — from compute to identity to network to security posture.

---

### 4. foundry-agent-engineer

Maps to: `foundry-model-governor`, `foundry-tool-governor`, `foundry-runtime-builder`, `foundry-eval-judge`, `agent-orchestrator`

| Cert | Name | Lane | Note |
|------|------|------|------|
| AI-102 | Azure AI Engineer Associate | Role-based | |
| AB-100 | Agentic AI Business Solutions Architect | Business | |
| AI-300 | MLOps Engineer Associate | Role-based | Beta |
| AZ-204 | Azure Developer Associate | Role-based | |

**Why**: Agent runtime, model integration, eval/deploy discipline. AI-102 covers the AI service integration surface, AB-100 covers agentic architecture framing, AI-300 covers MLOps lifecycle, AZ-204 covers the developer substrate.

---

### 5. data-intelligence-engineer

Maps to skills: `databricks-pipeline-production-readiness`, `databricks-app-production-readiness`, `databricks-agent-production-readiness`, `databricks-model-serving-production-readiness`

| Cert | Name | Lane | Note |
|------|------|------|------|
| DP-700 | Fabric Data Engineer Associate | Role-based | |
| DP-600 | Fabric Analytics Engineer Associate | Role-based | |
| DP-100 | Azure Data Scientist Associate | Role-based | |
| DP-300 | Azure Database Administrator Associate | Role-based | |
| DP-750 | Azure Databricks Data Engineer Associate | Role-based | Beta |

**Why**: Analytics, Databricks, data engineering, database benchmark lane. DP-750 is the most direct Databricks certification; DP-700 and DP-600 cover the Fabric analytics surface that benchmarks lakehouse discipline.

---

### 6. odoo-solution-architect

Maps to: `odoo-developer`, `odoo-release-manager`, `odoo-delivery-judge`

| Cert | Name | Lane | Note |
|------|------|------|------|
| MB-700 | Dynamics 365: Finance and Operations Apps Solution Architect Expert | Role-based | Benchmark analog only — not building on Dynamics |
| MB-500 | Dynamics 365: Finance and Operations Apps Developer Associate | Role-based | Benchmark analog for ERP dev discipline |
| MB-330 | Dynamics 365 Supply Chain Management Functional Consultant | Role-based | |
| MB-335 | Dynamics 365 Supply Chain Management Expert | Role-based | |
| MB-310 | Dynamics 365 Finance Functional Consultant | Role-based | |

**Why**: NOT because we are building on Dynamics. These are the closest Microsoft business-app benchmark surfaces to ERP solution architecture, finance, and operations. An odoo-solution-architect who could pass MB-700 has the right depth of ERP architectural thinking; MB-310/MB-330 validate functional consulting discipline in finance and supply chain.

---

### 7. security-ops

| Cert | Name | Lane |
|------|------|------|
| SC-200 | Security Operations Analyst Associate | Role-based |
| SC-300 | Identity and Access Administrator Associate | Role-based |
| SC-401 | Information Security Administrator Associate | Role-based |
| AZ-500 | Azure Security Engineer Associate | Role-based |
| SC-100 | Cybersecurity Architect Expert | Role-based |

**Why**: Security operations and governance lane. SC-200 covers SOC analyst discipline, SC-300 covers identity governance, SC-401 covers information protection, AZ-500 covers cloud security engineering, SC-100 covers the architectural overlay.

---

### 8. developer-copilot

| Cert | Name | Lane |
|------|------|------|
| GH-900 | GitHub Foundations | Fundamentals |
| GH-100 | GitHub Administration | Role-based |
| GH-200 | GitHub Actions | Role-based |
| GH-300 | GitHub Copilot | Role-based |
| GH-500 | GitHub Advanced Security | Role-based |

**Why**: Coding-agent, repo automation, CI, Copilot, AppSec posture. GH-900 is the literacy gate; GH-200 validates CI/CD pipeline discipline; GH-300 validates Copilot-assisted development; GH-500 validates security posture in code.

---

## Cross-References

| Asset | Location |
|-------|----------|
| Skill map (YAML) | `agent-platform/ssot/learning/microsoft_certification_persona_map.yaml` |
| Foundry model/tool/runtime map | `agent-platform/ssot/learning/foundry_model_tool_runtime_map.yaml` |
| Azure Copilot agent skill map | `agent-platform/ssot/learning/azure_copilot_agent_skill_map.yaml` |
| OdooSH skill persona map | `agent-platform/ssot/learning/odoo_sh_skill_persona_map.yaml` |
| Databricks production-ready skill map | `agent-platform/ssot/learning/databricks_production_ready_skill_map.yaml` |
| Agent SDK stack map | `agent-platform/ssot/learning/agent_sdk_stack_map.yaml` |
| Persona files | `agents/personas/` |

---

*Benchmark taxonomy — not a study list, not a runtime contract.*
