# Benchmark Map

## Purpose

Track which Microsoft reference architectures serve as benchmarks for each IPAI documentation family, and the parity status of each Odoo-on-Azure equivalent.

## Benchmark Sources

| Benchmark | Role | IPAI Equivalent |
|---|---|---|
| SAP on Azure | Workload operating model | Odoo on Azure workload center, monitoring, automation, runtime guidance |
| Microsoft Foundry | End-to-end AI platform | AI platform docs, model ops, evals, grounding, governance |
| AI-led SDLC with Azure and GitHub | Agentic engineering lifecycle | Spec-driven development, coding agents, quality agents, CI/CD, SRE feedback loops |
| Databricks + Fabric data intelligence | End-to-end data platform | Lakehouse, ingestion, governance, BI, real-time and AI-ready data foundation |

## SAP on Azure → Odoo on Azure Doc Parity

| SAP on Azure Doc | Odoo on Azure Equivalent | Status | Applicable | Notes |
|---|---|---|---|---|
| SAP on Azure overview | `overview/index.md` | Scaffold | Yes | Top-level landing |
| What SAP on Azure offerings are available? | `overview/offerings.md` | Scaffold | Yes | Deployment modes, stack options |
| Azure Center for SAP solutions | `workload-center/index.md` | Scaffold | Yes | Internal control-plane analogue (OSI) |
| Azure Monitor for SAP solutions | `monitoring/index.md` | Scaffold | Yes | Workload-specific monitoring pack |
| SAP deployment automation framework | `deployment-automation/index.md` | Scaffold | Yes | Bicep/azd/CI-CD equivalent |
| SAP workloads on Azure VMs | `runtime/container-apps-reference-architecture.md` | Scaffold | Yes, adapted | ACA-first, not VM-first |
| Supported SAP scenarios on Azure VMs | `overview/supported-scenarios.md` | Scaffold | Yes | Validated runtime patterns |
| Supported SAP software on Azure VMs | `overview/support-matrix.md` | Scaffold | Yes | Odoo/OCA/bridge version matrix |
| Planning guidance | `planning/index.md` | Scaffold | Yes | Landing zone, sizing, topology |
| Azure storage types for SAP workloads | `runtime/storage-and-filestore-patterns.md` | Scaffold | Yes | Filestore, artifacts, backups |
| High availability for SAP components | `planning/ha-and-dr.md` | Scaffold | Yes | Web/worker/cron/PG/ingress HA |
| Availability Zones for SAP workloads | `planning/ha-and-dr.md` | Scaffold | Yes | Zone/region strategy |
| Deploy SAP on Azure VMs | `quickstarts/deploy-dev-environment.md` | Scaffold | Yes, adapted | ACA deployment |
| Deploy DBMS on Azure VMs | `how-to/deploy-postgres.md` | Scaffold | Yes, adapted | Managed PG Flexible Server |
| Register existing SAP system | `quickstarts/register-existing-environment.md` | Scaffold | Yes | Import existing env into control plane |
| Start and stop SAP systems | `how-to/start-stop-environment.md` | Scaffold | Yes | ACA revision management |
| Manage a VIS | `workload-center/odoo-system-instance.md` | Scaffold | Yes | OSI management |
| Quality checks and insights | `workload-center/index.md` | Scaffold | Yes | Operational insights |
| View cost analysis for SAP system | `monitoring/cost-analysis.md` | Scaffold | Yes | Per-OSI cost view |
| SAP/Microsoft integrations | `integrations/index.md` | Scaffold | Yes | Entra, Foundry, AI Search, etc. |
| SAP HANA Large Instances | N/A | N/A | No | Not relevant to Odoo |
| SAP certifications on Azure | `overview/support-matrix.md` | Scaffold | Adapted | Tested compatibility, not SAP cert |

## Additional Platform Family Parity

| Microsoft Benchmark | IPAI Doc Family | Status | Notes |
|---|---|---|---|
| Microsoft Foundry (AI platform) | `ai-platform/index.md` | Scaffold | Model access, orchestration, evals, safety, governance |
| AI-led SDLC (Azure + GitHub) | `engineering/index.md` | Scaffold | Spec-first, coding agent, quality agent, CI/CD, SRE loop |
| Databricks + Fabric (data intelligence) | `data-intelligence/index.md` | Scaffold | Lakehouse, governance, BI, real-time, AI-ready data |

---

*Created: 2026-04-05 | Version: 1.0*
