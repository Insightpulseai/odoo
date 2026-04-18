# Production AI Foundation Adoption

**Upstream**: [microsoft/Deploy-Your-AI-Application-In-Production](https://github.com/microsoft/Deploy-Your-AI-Application-In-Production)
**Status**: canonical — reference-only adoption
**Authority**: [ssot/governance/production-ai-foundation-adoption.yaml](../../ssot/governance/production-ai-foundation-adoption.yaml)
**Related**: [agent-framework-adoption.md](agent-framework-adoption.md), [agent-delivery-stack](../../ssot/agent-platform/agent_delivery_stack.yaml)

---

## What this upstream is

Microsoft's production foundation **solution accelerator** for standing up a
secure, integrated Azure environment for AI workloads. Provisions:

- Microsoft Foundry (AI project/runtime surface)
- Microsoft Fabric (data foundation)
- Azure AI Search (retrieval/search workloads)
- Optional Microsoft Purview (tenant-level governance connection)

Pre-wired with **private networking, managed identities, and governance
controls**. Aligned to Microsoft Well-Architected + Azure production guidance.

It is a **platform baseline / landing-zone accelerator**, not a sample chat
app or frontend template.

---

## Decision

Consume as a **reference pattern source** for infra + platform + (secondarily)
agent-platform production hardening. **Do not** clone the repo topology,
match sample-specific naming, or assume greenfield resource groups. IPAI
canonical naming (`ipai-*`, `rg-ipai-dev-ai-sea`, `insightpulseai.com`) wins
every conflict.

---

## Where it lands in IPAI

| IPAI target | Role | What to absorb from upstream |
|---|---|---|
| [infra/azure/](../../infra/azure/) | **primary** | Private endpoint patterns, managed-identity modules, environment separation, Foundry/Search/Fabric/Purview Bicep modules |
| [platform/](../../platform/) | **primary** | Environment bindings, control-plane metadata for Foundry/Fabric/Search, tenant→env mapping, secret-reference model (Key Vault indirection) |
| [docs/runbooks/](../runbooks/) | **primary** | Production hardening runbooks, deployment checklists, incident response patterns |
| [agent-platform/](../../agent-platform/) | **secondary** | Runtime assumptions that depend on provisioned substrate (Foundry client auth via MI, AI Search retrieval client patterns). Absorbs auth/client patterns, not infra provisioning logic. |

**Not for**: `web/`, `agents/`, `addons/`, `data-intelligence/`.

---

## Copy / adapt

| Upstream pattern | IPAI target module | IPAI delta |
|---|---|---|
| Private endpoints for Foundry/Search/Fabric | `infra/azure/modules/private-endpoints.bicep` | Wire to existing ACA VNet + Azure Front Door topology |
| Managed-identity-first auth | `infra/azure/modules/managed-identities.bicep` | Use `mi-*` naming from [entra_target_state.yaml](../../ssot/identity/entra_target_state.yaml) |
| Environment separation dev/staging/prod | `infra/env/` | Match existing `ipai-dev` / `ipai-staging` / `ipai-prod` conventions |
| Foundry project provisioning | `infra/azure/modules/foundry-project.bicep` | Target canonical `ipai-copilot-resource` / `proj-ipai-copilot` |
| AI Search index/indexer provisioning | `infra/azure/modules/ai-search.bicep` | Schemas live in `agent-platform/src/agent_platform/retrieval/` |
| Fabric workspace + lakehouse binding | `infra/azure/modules/fabric-workspace.bicep` | Reconcile with `data-intelligence/` Databricks-first doctrine (Fabric = mirroring only) |
| Purview tenant-ID optional binding | `infra/azure/modules/purview-binding.bicep` | Flag-gated; deferred until Purview becomes live |
| Governance defaults (diagnostic settings, LAW) | `infra/azure/modules/diagnostics.bicep` | Route to existing App Insights / Log Analytics |

---

## Do not copy blindly

- **Repo topology** — accelerator layout ≠ IPAI monorepo layout
- **Sample-specific naming** — collides with `ipai-*` canonical names
- **Resource group assumptions** — accelerator may assume greenfield RG; IPAI has `rg-ipai-dev-ai-sea` etc.
- **Tenant / domain assumptions** — accelerator uses demo domains; IPAI uses `insightpulseai.com`
- **Single-environment opinions** — IPAI has dev/staging/prod, not one
- **Fabric as primary engineering plane** — conflicts with CLAUDE.md #9/#13 (Databricks is primary)

---

## Conflict reconciliation with IPAI invariants

### Fabric vs Databricks (CLAUDE.md #9, #13)

| Layer | Upstream position | IPAI invariant | Decision |
|---|---|---|---|
| Engineering/transformation plane | Fabric | Databricks + Unity Catalog (mandatory) | Keep Databricks as primary; adopt Fabric provisioning patterns **for mirroring only** |

### Purview

Upstream optional → IPAI status: not yet adopted. **Decision**: reference
only until Purview becomes a live requirement.

### Private networking

Upstream: private endpoints by default. IPAI: partial (ACA behind Front
Door; some PaaS still public). **Decision**: adopt as hardening target for
production environment.

### Managed identity first

Upstream: MI for all workload auth. IPAI: aligned per
[entra_target_state.yaml](../../ssot/identity/entra_target_state.yaml).
**Decision**: reinforce existing doctrine.

---

## Adoption order

| Phase | Scope |
|---|---|
| 1 | Hardening patterns — review private-networking Bicep, land adapted private endpoint patterns, align MI naming |
| 2 | Foundry provisioning — adapt Foundry project Bicep to `ipai-copilot-resource`, wire MI auth to MAF runtime |
| 3 | Search + retrieval — adapt AI Search provisioning, connect to `agent-platform` retrieval module |
| 4 | Fabric mirroring only — adapt workspace provisioning for mirroring; reconcile with Databricks Unity Catalog |
| 5 | Purview — **deferred** until live requirement |

---

## Relation to other upstream references

| Upstream | Role | IPAI reference SSOT |
|---|---|---|
| `microsoft/agent-framework` | Agent runtime/orchestration framework | [agent_framework_adoption.yaml](../../ssot/agent-platform/agent_framework_adoption.yaml) |
| `microsoft-foundry/*` sample repos | App and scenario references | [agent-framework-adoption.md §Appendix A](agent-framework-adoption.md) |
| `microsoft/Deploy-Your-AI-Application-In-Production` | Production Azure AI foundation / environment accelerator | **this doc** |
| Microsoft 365 Agents Toolkit samples | M365 channel delivery patterns | [reference-samples-register.yaml](../../ssot/governance/reference-samples-register.yaml) |

---

## Non-goals

- Not forking the accelerator repo.
- Not matching upstream repo topology.
- Not adopting Fabric as primary engineering plane.
- Not adopting Purview until live requirement.
- Not routing frontend (`web/`), agent definitions (`agents/`), or Odoo
  (`addons/`) decisions through this accelerator.

---

## References

- SSOT: [ssot/governance/production-ai-foundation-adoption.yaml](../../ssot/governance/production-ai-foundation-adoption.yaml)
- Agent framework adoption: [agent-framework-adoption.md](agent-framework-adoption.md)
- Agent delivery stack: [../../ssot/agent-platform/agent_delivery_stack.yaml](../../ssot/agent-platform/agent_delivery_stack.yaml)
- Identity target: [../../ssot/identity/entra_target_state.yaml](../../ssot/identity/entra_target_state.yaml)
- M365 samples register: [../../ssot/governance/reference-samples-register.yaml](../../ssot/governance/reference-samples-register.yaml)
- Upstream repo: https://github.com/microsoft/Deploy-Your-AI-Application-In-Production
- Well-Architected Framework: https://learn.microsoft.com/azure/well-architected/
