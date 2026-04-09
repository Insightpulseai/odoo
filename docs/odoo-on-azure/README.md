# Odoo on Azure Documentation

> The canonical documentation system for running Odoo 18 CE + OCA on Azure as the ERP system of record.

This documentation set mirrors the operating-model taxonomy of Microsoft's SAP on Azure documentation — not by copying SAP product behavior, but by achieving the same **documentation maturity** for Odoo workloads on Azure.

---

## Documentation Authority Model

This documentation system uses a **federated model**: each subsystem directory owns docs closest to its executable truth, while `docs/odoo-on-azure/` serves as the cross-repo architecture index and navigation surface.

| Authority | Owns |
|---|---|
| `docs/` | Cross-repo narrative, benchmark mapping, overview, planning, reference index |
| `platform/` | Control-plane truth: workload center, monitoring, AI platform bridge |
| `infra/` | Deployment/IaC truth: automation, networking, environment bootstrap |
| repo root | ERP runtime/app truth: Odoo topology, how-tos, thin integration surfaces |
| `agents/` | Agent/runtime/skill truth: agent patterns, AI-led SDLC, orchestration |
| `data-intelligence/` | Analytics/lakehouse truth: medallion, governance, BI, AI-ready data |

See [reference/doc-authority.md](reference/doc-authority.md) for the full ownership matrix.

---

## Benchmarks

This documentation system uses four Microsoft reference architectures as benchmarks:

| Benchmark | IPAI Equivalent | Doc Family |
|---|---|---|
| SAP on Azure | Odoo workload operating model | `overview/`, `workload-center/`, `monitoring/`, `deployment-automation/`, `runtime/`, `planning/` |
| Microsoft Foundry | AI platform operating model | `ai-platform/` → canonical in `platform/docs/ai-platform/` |
| AI-led SDLC with Azure + GitHub | Agentic engineering operating model | `engineering/` → canonical in `agents/docs/engineering/` |
| Databricks + Fabric data intelligence | Data intelligence operating model | `data-intelligence/` → canonical in `data-intelligence/docs/` |

See [reference/benchmark-map.md](reference/benchmark-map.md) for the full parity matrix.

---

## Documentation Families

### Workload Operating Model (source: `docs/` + `platform/` + `infra/`)

| Family | Purpose | Canonical Location |
|---|---|---|
| [Overview](overview/) | What Odoo on Azure is, supported scenarios, support matrix | `docs/odoo-on-azure/overview/` |
| [Workload Center](workload-center/) | Inventory, topology, lifecycle, drift — the Odoo equivalent of Azure Center for SAP | `platform/docs/workload-center/` |
| [Monitoring](monitoring/) | Workload-specific monitoring pack — the Odoo equivalent of Azure Monitor for SAP | `platform/docs/monitoring/` |
| [Deployment Automation](deployment-automation/) | Bicep/azd-based repeatable provisioning and promotion | `infra/docs/deployment-automation/` |
| [Runtime](runtime/) | ACA, PostgreSQL, Front Door, networking reference patterns | `docs/odoo-on-azure/runtime/` |
| [Planning](planning/) | Landing zone, identity, sizing, HA/DR, environment topology | `docs/odoo-on-azure/planning/` |

### Operational Guides (split by subsystem, indexed here)

| Family | Purpose | Canonical Location |
|---|---|---|
| [Quickstarts](quickstarts/) | Short, opinionated, reproducible deployment flows | Split: `infra/`, `odoo/`, `platform/` |
| [How-To](how-to/) | Operational tasks: deploy, rotate, upgrade, rollback, restore | Split by subsystem |
| [Integrations](integrations/) | Entra, Key Vault, Foundry, AI Search, Document Intelligence, Service Bus, M365 | Split: `platform/`, `odoo/`, `agents/` |

### Additional Platform Families (index pages here, canonical content in subsystems)

| Family | Purpose | Canonical Location |
|---|---|---|
| [AI Platform](ai-platform/) | Model access, orchestration, evaluation, safety, governance. Benchmarked against Microsoft Foundry. | `platform/docs/ai-platform/` + `agents/docs/ai-platform/` |
| [Engineering](engineering/) | Spec-first delivery, coding agents, quality agents, CI/CD, SRE feedback. Benchmarked against Azure + GitHub SDLC. | `agents/docs/engineering/` + `.github/docs/engineering/` |
| [Data Intelligence](data-intelligence/) | Ingestion, governance, real-time/batch, BI, AI-ready foundations. Benchmarked against Databricks + Fabric. | `data-intelligence/docs/` |

### Reference

| Family | Purpose |
|---|---|
| [Reference](reference/) | Benchmark parity matrix, doc authority model, terminology |

---

## Key Abstraction: Odoo System Instance (OSI)

This documentation system defines **OSI (Odoo System Instance)** as the logical workload object that groups:

- Odoo web process
- Worker process
- Cron process
- PostgreSQL database
- Filestore/storage
- Ingress (Front Door + WAF)
- Identity/secrets dependencies
- Monitor pack (alerts, workbooks, dashboards)
- AI/OCR/connector sidecars (if attached)

OSI is an **IPAI control-plane concept** inspired by SAP on Azure's Virtual Instance for SAP solutions (VIS). It is not a Microsoft Azure product.

---

## Architectural Principles

1. **Odoo CE + OCA is the application baseline.** Functional parity defaults to CE and OCA.
2. **Azure is the system/platform layer.** Runtime, identity, observability, AI, and networking are Azure-native.
3. **Custom addons remain thin.** `ipai_*` addons are bridge/connector/adapter only.
4. **Heavy AI and orchestration stay outside Odoo.** Agent runtime, RAG, OCR → external services.
5. **Live runtime and IaC must converge.** Drift is a governed risk, not an accepted norm.
6. **Each platform family has its own benchmark.** SAP for workload, Foundry for AI, SDLC for engineering, Databricks+Fabric for data.

---

## Page Authoring Standard

Every page in this documentation system should use:

```
# Title
## Purpose
## Scope
## When to Use This
## Architecture / Concepts
## Prerequisites
## Procedure / Guidance
## Outputs / Expected State
## Related Documents
## Evidence / Source of Truth
```

---

## Related Documents

- `docs/architecture/ODOO_ON_AZURE_REFERENCE_ARCHITECTURE.md` — single-page reference architecture
- `docs/architecture/IPAI_PLATFORM_ANALYSIS.md` — platform assessment and risk register
- `ssot/azure/odoo_bridge_matrix.yaml` — Azure bridge catalog
- `ssot/odoo/ee_gap_matrix.yaml` — EE parity coverage
- `ssot/odoo/custom_module_policy.yaml` — addon boundary rules

---

*Created: 2026-04-05 | Version: 1.0*
