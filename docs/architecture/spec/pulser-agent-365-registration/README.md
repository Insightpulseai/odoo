# Pulser Agent 365 Registration

> Entra Agent ID registration manifests for 3 published Pulser agents.
> Deadline: **2026-05-01** (M365 E7 / Agent 365 GA).
> Closes Issue 13 (`docs/backlog/open-issues-20260415.md`).

---

## Identity architecture — 2 identities per agent

Each published Pulser agent has **two distinct Entra identities**:

| Identity type | Purpose | Naming | Example |
|---|---|---|---|
| **Runtime MI (UserAssignedManagedIdentity)** | Executes the agent — calls Odoo MCP, Foundry, AI Search, etc. | `id-ipai-agent-<domain>-dev` | `id-ipai-agent-finance-close-dev` |
| **Agent 365 SP (Entra app registration + Service Principal)** | Catalog identity for M365 Agent 365 surface | `ipai-agent-<published-name>-dev` | `ipai-agent-pulser-finance-dev` |

The Runtime MI is the identity that RUNS; the Agent 365 SP is the identity that's REGISTERED in the catalog. Separation allows fine-grained RBAC — the catalog SP gets read-only visibility while the runtime MI has write paths to Odoo via `ipai-odoo-connector`.

## 3 published agents

| Published agent | Agent 365 SP appId | Runtime MI | Manifest |
|---|---|---|---|
| `pulser-finance` | `49aceaad-554d-4cd9-89d6-7d5cb388a508` | `id-ipai-agent-finance-close-dev` (+ peers: ap-invoice, bank-recon, doc-intel, tax-guru) | `manifest-pulser-finance.json` |
| `pulser-ops` | `486bd9d1-dfe6-4ca0-8b39-5daa8d7b75c5` | `id-ipai-agent-pulser-dev` | `manifest-pulser-ops.json` |
| `pulser-research` | `faab82f3-0da4-4e7b-a563-b27f7418579f` | (new or reuse `id-ipai-agent-pulser-dev`) | `manifest-pulser-research.json` |

## Repo inventory wiring

Each manifest explicitly references which IPAI repos / skills / Odoo modules / Foundry endpoints the agent uses. This is the "wire the repo inventory" answer — manifest is the contract.

| Wiring dimension | Source of truth |
|---|---|
| Agent skills | `agents/skills/<domain>/SKILL.md` files |
| Runtime code | `agent-platform/` container apps |
| Odoo models read | via `ipai-odoo-mcp` tool catalog (`apps/odoo-connector/` + MCP spec) |
| Odoo modules installed | `addons/ipai/ipai_*/` (Odoo-side bridges) |
| Foundry project endpoint | `ssot/foundry/runtime-contract.yaml` §endpoints |
| Model deployment | `gpt-4.1` or `gpt-4.1-mini-20260415` per `feedback_stick_to_gpt41` |
| Azure resources | `docs/architecture/data-model-erd.md` §0.2 + `docs/runbooks/foundry-connections-and-tools.md` §0 |
| AI Search index (if RAG) | `srch-ipai-dev-sea` catalog — `pulser-odoo-docs`, `pulser-bir-rulings`, `pulser-prismalab` |
| Evals | `spec/pulser-evals/<agent>-evals.md` |

## Current status (2026-04-15)

- ✅ 3 Entra app registrations + SPs created on IPAI tenant
- ✅ 3 manifests committed below
- ⏳ **Agent 365 catalog registration is frontier-gated** — `/identity/agents` Graph endpoint returns 404 "Resource not found for the segment 'agents'." Once Microsoft opens the endpoint (expected pre or at 2026-05-01 GA), apply Agent ID extension per manifest
- ⏳ TBWA tenant dual registration — deferred until IPAI tenant registration succeeds
- ⏳ Per-agent permission reassignment post-publish — applied after catalog ingestion

## Manifest schema (applied to all 3)

```json
{
  "agent_identity": {
    "catalog_sp_appId": "<uuid>",
    "catalog_sp_objectId": "<uuid>",
    "runtime_mi_name": "id-ipai-agent-*-dev",
    "runtime_mi_principalId": "<uuid>",
    "runtime_mi_clientId": "<uuid>"
  },
  "catalog_metadata": {
    "display_name": "<public name>",
    "description": "<one-sentence purpose>",
    "publisher": "InsightPulse AI (MpnId 7097325)",
    "category": "<Finance | DevOps | Research>",
    "version": "1.0.0"
  },
  "runtime": {
    "foundry_project_endpoint": "https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot",
    "model_deployment": "gpt-4.1 | gpt-4.1-mini-20260415",
    "region": "eastus2"
  },
  "tool_surface": ["<list of Foundry tools + MCP endpoints>"],
  "repo_inventory": {
    "skills": ["agents/skills/<domain>/SKILL.md"],
    "odoo_modules": ["addons/ipai/ipai_*/..."],
    "runtime_code": ["apps/<ACA-app>/", "agent-platform/<path>"],
    "evals": ["spec/pulser-evals/<agent>-evals.md"]
  },
  "rbac_at_publish": {
    "ipai_tenant": ["Azure AI User on ipai-copilot-resource", "SELECT on ipai_dev.gold, ipai_dev.metrics"],
    "tbwa_tenant": "deferred"
  },
  "agent_365_extension_applied": false,
  "frontier_gate_release_tracked": true
}
```

## How to apply the Agent ID extension (when frontier opens)

Pseudocode for the eventual Graph call:

```bash
# When /identity/agents endpoint returns 200 instead of 404:
for manifest in spec/pulser-agent-365-registration/manifest-*.json; do
  appId=$(jq -r .agent_identity.catalog_sp_appId $manifest)
  az rest --method post \
    --uri "https://graph.microsoft.com/beta/identity/agents" \
    --body "$(jq '.' $manifest)"
done
```

Until then, the SPs are pre-created and manifest-ready — zero additional IPAI-side work once Microsoft opens the endpoint.
