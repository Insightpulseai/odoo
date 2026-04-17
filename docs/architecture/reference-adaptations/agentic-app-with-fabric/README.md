# Reference adaptation — `Azure-Samples/agentic-app-with-fabric`

> **Mode:** `clone-reference` (per `ssot/governance/upstream-adoption-register.yaml`)
> **Upstream:** https://github.com/Azure-Samples/agentic-app-with-fabric
> **Do NOT fork. Do NOT inherit Fabric-first operational assumptions.**
> Locked 2026-04-15.

---

## What this repo is

A **demo/sample application** — "Agentic Banking App with Microsoft Fabric" showing OLTP + OLAP + AI side-by-side with a multi-agent system. Key folders on upstream:
- `Data_Ingest/` — sample data loading flows
- `Fabric_artifacts/` — semantic model, Data Agent, Eventhouse, Eventstream configs
- `backend/` — API + agent orchestration code
- `scripts/` — Fabric workspace deploy scripts
- `src/` — frontend/backend app source
- `workshop/` — step-by-step walkthrough

Its setup path is Fabric-heavy: Fabric workspace deployment + SQL DB + Lakehouse + semantic model + Power BI report + Data Agent + Eventhouse + Eventstream + Azure OpenAI config.

## Why IPAI references it

IPAI's architecture is **convergent but not identical**:

| Plane | IPAI's path | Accelerator's path |
|---|---|---|
| Transaction/OLTP | Odoo CE 18 + `pg-ipai-odoo` (PG Flex) | SQL DB in Fabric |
| Analytics/OLAP | Databricks + Unity Catalog (ipai_dev + odoo_erp FOREIGN_CATALOG) | Fabric Lakehouse + semantic model |
| Agent runtime | Foundry (ipai-copilot-resource) + Pulser custom-engine | Azure OpenAI + Fabric Data Agent |
| CI/CD | Azure Pipelines (sole authority per CLAUDE.md) | `azd up` + Bicep |

We reference the accelerator for **patterns to translate**, not **stack to clone**.

## What IPAI keeps from this repo

| Pattern | How we translate to IPAI |
|---|---|
| Multi-agent orchestration | Already canonical in Pulser planner/router + specialists; use accelerator's eval harness shape to inform `spec/pulser-evals/` |
| NL→query translation | When Pulser Finance agent translates operator questions into Unity Catalog metric queries, borrow the prompt-shape patterns from the accelerator's NL→query module |
| Visualization / chart generation | The Code Interpreter (Foundry built-in) + chart patterns the accelerator uses can inform Pulser's artifact output |
| Demo/eval/test harness | Accelerator's workshop structure informs IPAI customer demo flows (TBWA, W9, PrismaLab) |
| Deployment structure | Directory layout + IaC composition worth translating into IPAI's `infra/azure/` + `azure-pipelines/` shape |

## What IPAI explicitly does NOT adopt from this repo

| Accelerator element | Why we skip |
|---|---|
| Fabric as operational truth | IPAI's operational SOR is Odoo, not Fabric SQL DB |
| Banking domain as-is | IPAI verticals are Services / Photo-Video / Research — not banking |
| Direct runtime/env layout | IPAI runtime is ACA + Foundry + Databricks; accelerator's runtime is Fabric-first |
| `azd up` deployment | CLAUDE.md: Azure Pipelines is sole CI/CD authority; `azd` is dev-only tooling at best |
| Azure OpenAI-first assumptions | IPAI uses Foundry (Anthropic endpoint shim available but unused per `feedback_stick_to_gpt41`) |
| Eventhouse/Eventstream runtime | IPAI uses Service Bus (`sb-ipai-dev-sea`) for event routing; Fabric Eventhouse is analytics only |

## File placement convention

Reference notes extracted from upstream land here (`docs/architecture/reference-adaptations/agentic-app-with-fabric/`). Pattern implementations live in:
- `agent-platform/patterns/` — orchestration pattern translations
- `data-intelligence/fabric-reference/` — Fabric-shaped patterns we might need later (Issue 27)

## Update trigger

Revisit this adaptation when:
- Microsoft ships a new major version of the accelerator
- IPAI provisions Fabric capacity (Issue 27) — then the Fabric artifact patterns become directly relevant
- Fabric Data Agent matures into a canonical IPAI consumer (via MCP)

---

*Reference-adapt note locked 2026-04-15. Register entry in `ssot/governance/upstream-adoption-register.yaml` under "Added 2026-04-15 — CDM + agentic-app-with-fabric".*
