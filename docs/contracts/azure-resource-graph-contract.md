# Azure Resource Graph Contract

> Contract: C-36
> Status: Active
> Defines Azure Resource Graph as the canonical live-Azure estate query layer.

---

## Purpose

Azure Resource Graph is the authoritative query surface for answering "what is actually deployed right now?" across the InsightPulseAI Azure estate. It complements the repo SSOT (intended state) with live inventory (actual state).

---

## Role in architecture

| Plane | Truth type |
|-------|------------|
| Azure Boards | Planned truth (goals, work items) |
| GitHub | Code truth (source, contracts, docs) |
| Azure Pipelines | Release truth (build, deploy, promote) |
| Azure Resource Graph | **Live Azure inventory/drift truth** |
| Foundry | Agent/runtime/eval truth |
| Repo SSOT (`ssot/`) | Intended-state truth |

Resource Graph is the bridge between intended state (repo) and actual state (Azure).

It does **not** replace:
- repo SSOT (intended state)
- Azure Boards (planned work)
- GitHub (code / PR truth)
- Azure Pipelines (release/build evidence)
- Foundry runtime/eval evidence

---

## Core rule

Environment truth in Azure is established by **live resource properties**, not by chat, screenshots, or assumptions.

Resource Graph is the default query plane for answering:
- what exists
- where it exists
- what SKU/region/tags/identity/config class it has
- what changed recently

---

## Read-permission rule

Resource Graph only returns resources the calling identity can read.

If a resource is missing from results, the cause may be:
- resource does not exist
- principal lacks read access
- query scope is too narrow

Therefore: missing results must not be treated as proof of absence until access scope is confirmed.

---

## Scope

### Subscriptions

All queries target the InsightPulseAI tenant subscriptions:
- `Azure subscription 1` (primary)
- Any future subscriptions added to the tenant

### Resource types in scope

| Category | Resource types |
|----------|---------------|
| Compute | Container Apps, Container App Environments |
| Networking | Front Door, CDN profiles, DNS zones, VNets, NSGs |
| Data | PostgreSQL Flexible Server, Storage Accounts |
| AI | Azure OpenAI, AI Foundry, Document Intelligence, Search |
| Identity | Managed Identities, Key Vaults |
| Containers | Container Registries |
| Monitoring | Log Analytics, Application Insights |

---

## Auth requirements

- Queries return only resources where the calling principal has **read** access
- Interactive queries: user principal via `az graph query`
- Automated queries: service principal or managed identity with `Reader` role on target subscriptions
- CI/pipeline queries: same service principal used for deployment, scoped to subscription

---

## Canonical query classes

### Mandatory before release or audit

| Query class | Purpose | Frequency |
|-------------|---------|-----------|
| Resource inventory by type | Full estate snapshot | Pre-release, weekly |
| Tag compliance | Missing or incorrect tags | Pre-release |
| Region compliance | Resources outside allowed regions | Pre-release |
| Managed identity inventory | Orphaned or misconfigured identities | Monthly |
| Recent changes (14-day window) | Unexpected drift detection | Pre-release |

### Recommended for ongoing governance

| Query class | Purpose | Frequency |
|-------------|---------|-----------|
| SKU/tier compliance | Unexpected upgrades or cost drift | Monthly |
| Stale resources | Resources not updated in 30+ days | Monthly |
| Network exposure | Public endpoints outside Front Door | Monthly |
| Key Vault access audit | Who/what can read secrets | Quarterly |

---

## SSOT reconciliation workflow

```
1. Run resource-graph-query-catalog queries (scripts/azure/resource_graph/)
2. Export results as JSON to docs/evidence/<stamp>/resource-graph/
3. Compare against ssot/runtime/ and infra/ssot/azure/resources.yaml
4. Flag drift: resources in Azure but not in SSOT, or SSOT entries with no Azure match
5. Remediate: update SSOT if Azure is correct, or fix Azure if SSOT is correct
6. Commit evidence and any SSOT updates together
```

---

## Constraints

- Resource Graph is **free** but **throttled** per user/tenant (quota headers in response)
- Data is near-real-time, not guaranteed instant — Azure Resource Manager notifies on updates plus regular full scans
- Change history retained for **14 days** only — for longer audit trails, export to evidence
- No write capability — Resource Graph is read-only query surface

---

## Query execution

### CLI

```bash
az graph query -q "<KQL>" --subscriptions "<sub-id>" -o json
```

### Repo-local queries

Canonical KQL files stored in `scripts/azure/resource_graph/queries/*.kql`
Wrapper script: `scripts/azure/resource_graph/run_query.sh`

### Query catalog

`ssot/runtime/resource-graph-query-catalog.yaml` — machine-readable index of canonical queries.

---

## Invariants

1. Resource Graph is the only canonical query surface for live Azure estate inventory
2. Portal "All resources" is not authoritative — it uses Resource Graph internally but is not auditable
3. Every pre-release audit must include at least the mandatory query classes
4. Drift between Resource Graph results and repo SSOT must be resolved before release
5. Query results committed to evidence are snapshots, not SSOT — the live query is always more current

---

## Reconciliation rule

When Resource Graph and repo SSOT disagree:

1. Confirm query scope and permissions
2. Confirm resource identity/name/subscription/resource group
3. Classify mismatch as one of:
   - **SSOT stale** — repo needs update
   - **runtime drift** — Azure needs correction
   - **unauthorized/unexpected resource** — investigate and remediate
   - **permission/query issue** — expand scope and re-query
4. Fix the authoritative source appropriate to the mismatch

---

## Evidence rule

Any major Azure runtime reconciliation should attach:
- the query used
- the query scope
- timestamp
- principal identity or automation context
- result artifact path or summary

---

## Success criteria

This contract is working when:
- live Azure inventory can be reproduced from repo-stored queries
- runtime drift is detectable without manual portal browsing
- release/audit checks can reference repeatable KQL
- SSOT reconciliation is evidence-backed rather than anecdotal

---

## Cross-references

- `ssot/runtime/resource-graph-query-catalog.yaml` — query index
- `scripts/azure/resource_graph/` — KQL files and wrappers
- `infra/ssot/azure/resources.yaml` — intended Azure resource inventory
- `ssot/runtime/live-builder-surfaces.yaml` — builder surface inventory
- `docs/contracts/foundry-vscode-auth-contract.md` — auth paths

---

*Last updated: 2026-03-17*
