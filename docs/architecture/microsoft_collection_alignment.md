# Microsoft Learn Collection — Repo Alignment Crosswalk

> Maps each Microsoft Learn collection reference to the corresponding
> repo artifact, execution Epic/Feature, evidence, and scope exclusions.
>
> Purpose: Prove that the platform's architecture outputs align with
> what Microsoft's reference architectures expect teams to produce.
>
> SSOT for execution hierarchy: `ssot/governance/azdo-execution-hierarchy.yaml`
> SSOT for strategy: `ssot/governance/platform-strategy-2026.yaml`

---

## 1. Solution Architecture (AZ-305 / Azure Solutions Architect)

Microsoft expects: solution strategy, architecture decisions, implementation approach,
testing approach, identity/governance/monitoring, storage/continuity/infrastructure design.

| Expected Output | Repo Artifact | Epic | Status |
|----------------|---------------|------|--------|
| Solution strategy | `ssot/governance/platform-strategy-2026.yaml` | — | Complete |
| Architecture decisions | `docs/architecture/UNIFIED_TARGET_ARCHITECTURE.md` | OBJ-001 | Complete |
| Implementation approach | `ssot/governance/azdo-execution-hierarchy.yaml` | OBJ-001 | Complete |
| Testing approach | `odoo/.claude/rules/testing.md` | OBJ-005 | Complete |
| Identity architecture | `infra/ssot/azure/PLATFORM_TARGET_STATE.md` §Identity | OBJ-001/FEAT-001-01 | Documented, not implemented |
| Governance model | `ssot/governance/platform-constitution.yaml` | — | Complete |
| Monitoring/observability | `docs/architecture/microsoft_collection_alignment.md` (this file, §2) | OBJ-001/FEAT-001-03 | Gap — see Gap 2 |
| Storage/continuity | `docs/architecture/ADLS_ETL_REVERSE_ETL_ARCHITECTURE.md` | OBJ-004 | Complete |
| Infrastructure design | `infra/ssot/azure/resources.yaml` (65 resources) | OBJ-001 | Complete |

---

## 2. Landing Zone / Operating Model (Foundry Landing Zone)

Microsoft expects: application landing zone, platform landing zone, shared networking,
shared IAM, policy, monitoring, governance and change management.

| Expected Output | Repo Artifact | Epic | Status |
|----------------|---------------|------|--------|
| Platform landing zone | `docs/architecture/foundry_landing_zone_operating_model.md` | OBJ-001 | **New** |
| Application landing zone | `docs/architecture/foundry_landing_zone_operating_model.md` | OBJ-003 | **New** |
| Shared networking | `infra/ssot/azure/PLATFORM_TARGET_STATE.md` §Networking | OBJ-001 | Complete |
| Shared IAM | `infra/ssot/azure/PLATFORM_TARGET_STATE.md` §Identity | OBJ-001/FEAT-001-01 | Documented |
| Policy | `ssot/governance/platform-constitution.yaml` | — | Complete |
| Monitoring | `docs/architecture/foundry_landing_zone_operating_model.md` §Monitoring | OBJ-001/FEAT-001-03 | **New** |
| Governance / change mgmt | `ssot/governance/operating-model.yaml` | — | Complete |
| Workload vs platform team | `docs/architecture/foundry_landing_zone_operating_model.md` | OBJ-003 | **New** |

---

## 3. Finance Solution Architecture (MB-700 / Dynamics 365 F&O)

Microsoft expects: architecture, strategy, implementation, testing outputs
for finance and operations solutions, including Copilot/AI-agent understanding.

| Expected Output | Repo Artifact | Epic | Status |
|----------------|---------------|------|--------|
| Finance solution architecture | `docs/architecture/finance_solution_architecture.md` | OBJ-002 | **New** |
| MB-700 → Odoo CE mapping | `docs/architecture/finance_solution_architecture.md` §2 | OBJ-002 | **New** |
| Implementation lifecycle | `docs/architecture/finance_solution_architecture.md` §4 | OBJ-002 | **New** |
| Testing lifecycle | `odoo/.claude/rules/testing.md` + `docs/architecture/finance_solution_architecture.md` §5 | OBJ-002 | Partial |
| AI/copilot boundaries | `docs/architecture/AI_CONSOLIDATION_FOUNDRY.md` | OBJ-003 | Complete |
| Finance process scope | `docs/architecture/finance_solution_architecture.md` §3 | OBJ-002 | **New** |
| EE parity stance | `odoo/.claude/rules/ee-parity.md` | OBJ-002 | Complete |

---

## 4. Enterprise Data Platform (Databricks / ADF / Fabric)

Microsoft expects: ingestion, medallion/lakehouse, data domains/products,
governance, cost controls, BI serving, ML/MLOps, operational model.

| Expected Output | Repo Artifact | Epic | Status |
|----------------|---------------|------|--------|
| Ingestion architecture | `docs/architecture/ADLS_ETL_REVERSE_ETL_ARCHITECTURE.md` §3-4 | OBJ-004 | Complete |
| Medallion/lakehouse design | `docs/architecture/enterprise_data_platform.md` §2 | OBJ-004 | **New** (consolidates existing) |
| Data domains / products | `docs/architecture/enterprise_data_platform.md` §3 | OBJ-004 | **New** |
| Governance | `docs/architecture/enterprise_data_platform.md` §4 | OBJ-004 | **New** |
| Cost controls | `docs/architecture/enterprise_data_platform.md` §5 | OBJ-004 | **New** |
| BI serving path | `docs/architecture/ADLS_ETL_REVERSE_ETL_ARCHITECTURE.md` + `PLATFORM_TARGET_STATE.md` §Analytics | OBJ-004 | Complete |
| ML/MLOps path | `docs/architecture/enterprise_data_platform.md` §6 | OBJ-004 | **New** |
| Operational model / RACI | `docs/architecture/enterprise_data_platform.md` §7 | OBJ-004 | **New** |

---

## 5. Document Intelligence Processing (PDF Forms Architecture)

Microsoft expects: intake trigger, document extraction, orchestration,
processing function, production hardening/reliability path.

| Expected Output | Repo Artifact | Epic | Status |
|----------------|---------------|------|--------|
| Intake source | `docs/architecture/document_intelligence_processing.md` §1 | OBJ-002/FEAT-002-05 | **New** |
| Extraction service | `docs/architecture/document_intelligence_processing.md` §2 | OBJ-002/FEAT-002-05 | **New** |
| Orchestration | `docs/architecture/document_intelligence_processing.md` §3 | OBJ-002/FEAT-002-04 | **New** |
| Processing function | `docs/architecture/document_intelligence_processing.md` §4 | OBJ-002/FEAT-002-04 | **New** |
| Review/exception handling | `docs/architecture/document_intelligence_processing.md` §5 | OBJ-002 | **New** |
| Production hardening | `docs/architecture/document_intelligence_processing.md` §6 | OBJ-002 | **New** |

---

## 6. Guided Learning Measurement (Agent Learning Paths)

Microsoft expects: learning levels, persona lanes, OKRs, KPIs,
assessment evidence, promotion/readiness gates.

| Expected Output | Repo Artifact | Epic | Status |
|----------------|---------------|------|--------|
| Learning levels | `docs/okr/learning_measurement_model.md` §1 | OBJ-003/FEAT-003-03 | **New** |
| Persona lanes | `docs/okr/learning_measurement_model.md` §2 | OBJ-003/FEAT-003-03 | **New** |
| OKRs / KPIs | `docs/okr/learning_measurement_model.md` §3 | OBJ-003/FEAT-003-03 | **New** |
| Assessment evidence | `docs/okr/learning_measurement_model.md` §4 | OBJ-003/FEAT-003-03 | **New** |
| Promotion / readiness gates | `docs/okr/learning_measurement_model.md` §5 | OBJ-003/FEAT-003-03 | **New** |

---

## Intentionally Out of Scope

| Microsoft Reference | Why Excluded |
|---------------------|-------------|
| Dynamics 365 F&O runtime | Platform uses Odoo CE, not D365. MB-700 patterns mapped to Odoo equivalents. |
| Azure Kubernetes Service | Platform uses Azure Container Apps (AKS is deprecated per CONST-004). |
| Power Platform / Dataverse | Not in stack. Supabase + n8n cover equivalent automation surface. |
| Microsoft Fabric (full) | Using Databricks as primary. Fabric referenced only for Tableau connector. |
| Dynamics 365 Copilot | Using Azure AI Foundry agents, not D365 Copilot. Mapped in AI_CONSOLIDATION_FOUNDRY.md. |
| Multi-tenant architecture | Single-tenant platform (per project charter constraints). |

---

## Evidence Policy

Each alignment claim must be backed by one of:
- A file path to a repo artifact that exists on `main`
- A CI validator that gates the artifact
- An execution Epic/Feature in `azdo-execution-hierarchy.yaml`
- An explicit "Gap" or "New" marker for artifacts being created

*Last updated: 2026-03-17*
