# Sample Adoption Policy

> Microsoft samples are implementation accelerators, not architecture authority.

---

## Principle

The Microsoft sample catalog is a **harvest list**. It contains valid implementation patterns, but it does not override canonical platform decisions that are already settled.

## Settled Architecture (Do Not Re-Open)

| Decision | Authority |
|----------|-----------|
| **Databricks + Unity Catalog** | Required engineering/governance plane |
| **Power BI** | Required primary business consumption plane |
| **Fabric** | Required complementary mirroring / OneLake / semantic integration |
| **n8n** | Orchestration plane (not CDC backbone) |
| **Entra + Key Vault + RBAC** | Required control plane |
| **ACA** | Canonical compute surface |

No sample adoption may pivot the platform to Functions-first, ADF-first, or Logic Apps-first architecture.

## Rules

1. **Every adopted sample must be registered** in `infra/ssot/azure/approved_reference_samples.yaml`
2. **Each entry must map to**: owning repo, target runtime, target control plane, secrets model, and adaptation path
3. **Demo patterns are scaffolding only** — HTTP triggers, timer triggers, order processing, RAG quickstarts, and generic full-stack templates do not carry architecture authority
4. **No ad-hoc link copying** — if a sample is worth adopting, it is worth registering

## Approved Samples — Adopt Now

| Sample | Use For | Owning Repo |
|--------|---------|-------------|
| GitHub OIDC Terraform | Secretless CI auth into Azure | `infra` / `.github` |
| Remote MCP with Azure Functions | Remote MCP hosting | `agent-platform` / `platform` |
| Databricks VNet/private endpoint template | Hardened Databricks infra | `infra` |
| AI Model Starter Kit | Keyless Foundry/runtime adapter — Entra ID auth across Foundry models via Responses API | `agent-platform` / `platform` |
| ChatGPT + Enterprise Data | Enterprise assistant / RAG — AOAI + AI Search with citations and prompt orchestration | `agent-platform` / `web` |

## Approved Samples — Adopt Selectively

| Sample | Use For | Owning Repo | Constraint |
|--------|---------|-------------|------------|
| Purview Custom Connector Accelerator | Optional governance-extension — custom metadata/lineage into Purview | `data-intelligence` | Only if Purview beyond Unity Catalog is needed |
| Azure OpenAI keyless auth | Entra-backed AOAI access | `platform` / `agent-platform` | Prefer AI Model Starter Kit for Foundry-specific access |
| Azure Functions Flex secure-by-default | Control-plane hooks, webhooks | `platform` / `agent-platform` | Small hooks only, not primary workloads |

Full registry: [`infra/ssot/azure/approved_reference_samples.yaml`](../../infra/ssot/azure/approved_reference_samples.yaml)

## Governance Hierarchy (Locked)

- **Unity Catalog** = mandatory Databricks governance plane
- **Purview** = optional/adjacent cross-platform governance extension only
- Purview adoption does NOT make Synapse a canonical data-engineering plane
- Purview adoption does NOT replace Unity Catalog for Databricks-side governance

## Explicitly Not Canonical

- Enterprise VM/database templates (DataStax, Couchbase, Qlik, SQL Enterprise VM)
- GitHub Enterprise Server on VM
- Generic enterprise governance ARM quickstarts
- Synapse as default engineering plane
- Any sample that re-opens settled data/control-plane decisions

## Boundary Reinforcement

Remote MCP hosting is a **runtime/platform concern** (`agent-platform` / `platform`), not an `agents` concern. This aligns with:

- `agents` = personas, skills, judges, evals, metadata, registries, prompt contracts
- `agent-platform` = runtime, orchestration, task ledger, execution contracts, MCP hosting

## Companion Docs

- Global sample doctrine: `agent-platform/ssot/learning/azure_sample_azd_skill_map.yaml`
- Approved registry: `infra/ssot/azure/approved_reference_samples.yaml`
- Repo boundary SSOT: `ssot/repo/org_topology.yaml`

---

*Last updated: 2026-03-21*
