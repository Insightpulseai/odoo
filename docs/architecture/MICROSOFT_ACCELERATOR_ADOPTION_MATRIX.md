# Microsoft Accelerator Adoption Matrix

> Decision matrix for `microsoft/Deploy-Your-AI-Application-In-Production` against IPAI target repos.
>
> **Doctrine**: Treat as a secure Azure AI platform-pattern reference for `infra` and `agent-platform`, not as the canonical deployment blueprint for `odoo`.

---

## Decision Matrix

| Area in Microsoft repo | Borrow | Adapt | Ignore | Target repo | Why |
|---|---|---|---|---|---|
| `azd`-first deployment flow | Yes | Lightly | No | `infra` | Repeatable Azure provisioning and post-deploy validation |
| Bicep / infra module structure | Yes | Yes | No | `infra` | Strong Azure-native resource composition reference |
| Private networking posture | Yes | Yes | No | `infra` | Matches desired production posture |
| Managed identity + RBAC discipline | Yes | Yes | No | `infra`, `agent-platform` | Service-to-service auth |
| Key Vault-first secret handling | Yes | No | No | `infra`, `platform` | Canonical pattern |
| Post-deployment validation checklist | Yes | Yes | No | `docs`, `infra` | Operational readiness/evidence workflow |
| Foundry provisioning assumptions | Yes | Yes | No | `agent-platform`, `infra` | AI runtime environment setup |
| Azure AI Search integration pattern | Yes | Yes | No | `agent-platform` | Source indexing / retrieval |
| Full AI Landing Zone submodule | No | Maybe | Yes | `infra` | Too heavy as default Odoo runtime baseline |
| Fabric workspace / lakehouse defaults | No | Conditional | Yes | `data-intelligence` | Only relevant for analytics plane |
| Purview integration defaults | No | Conditional | Yes | `platform`, `data-intelligence` | Useful later, not core baseline |
| PostgreSQL-to-Fabric mirroring | No | Maybe later | Yes | `data-intelligence` | Analytics, not ERP runtime |
| "Single-command deploy 30+ resources" | No | Slimmer | Yes | `infra` | Wrong default blast radius |
| Opinionated `main.bicepparam` defaults | No | Selectively | Yes | `infra` | Repo warns these are not neutral |
| Odoo runtime topology | No | No | Yes | `odoo` | Not an Odoo deployment reference |
| Odoo addon / module design | No | No | Yes | `odoo` | Out of scope |
| ERP workflow/state design | No | No | Yes | `odoo` | Must remain Odoo-native |
| Public web / product UI structure | No | No | Yes | `web` | Infra/platform oriented, not product-web |
| Control-plane metadata/contracts | Lightly | Yes | No | `platform` | Borrow security/ops patterns only |

---

## Per-Repo Guidance

### `odoo`

- **Borrow**: almost nothing directly
- **Adapt**: only infra-facing assumptions (external service auth, secret access patterns)
- **Ignore**: the repo as a runtime template
- **Authority**: Odoo 18 CE, OCA-first, thin `ipai_*` bridges, deterministic finance/compliance logic in code

### `infra`

- **Borrow heavily**: azd/Bicep discipline, private networking, managed identity, Key Vault/RBAC, post-deploy verification, "review defaults before deploy" discipline
- **Do not inherit**: Fabric-enabled defaults, Purview-enabled defaults, all AI Landing Zone components, full demo-stack topology

### `platform`

- **Borrow lightly**: governance hooks, secret/identity boundary assumptions, integration contract posture
- **Do not**: let the Microsoft repo define your control-plane model

### `agent-platform`

- **Borrow selectively**: Foundry setup, AI Search / retrieval posture, private-network / MI integration, production AI runtime hygiene
- **Do not inherit**: full Fabric/Purview stack, broad "AI + data platform" sprawl

### `data-intelligence`

- **Borrow later, not now**: Fabric, Purview, PostgreSQL mirroring are potentially relevant for analytics, but only as a deliberate future architecture choice

### `web`

- **Ignore as direct source**: nothing drives browser-facing architecture except general operational discipline

---

## Target Posture

```yaml
borrow_strategy:
  odoo:
    borrow: minimal
    source_of_truth: odoo_native_doctrine
  infra:
    borrow: high
    adapt: slimmed_azure_native_baseline
  platform:
    borrow: low_to_medium
    adapt: control_plane_contracts_only
  agent_platform:
    borrow: medium_to_high
    adapt: foundry_search_runtime_only
  data_intelligence:
    borrow: conditional_later
    adapt: only_if_fabric_purview_are_deliberate_choices
  web:
    borrow: none
```

---

## Key Constraint

The Microsoft repo is a **broad, production-style AI/data platform accelerator** with Foundry, AI Search, optional Fabric, optional Purview, private networking, managed identities, and governance controls. It explicitly warns that its checked-in defaults are an **opinionated end-to-end path**, not a neutral baseline.

---

*Created: 2026-04-09*
