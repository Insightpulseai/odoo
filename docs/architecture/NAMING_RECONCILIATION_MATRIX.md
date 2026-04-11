# Naming Reconciliation Matrix — Pulser for Odoo

> Canonical rename plan for normalizing from 4 overlapping naming eras to `pulser-odoo` / `Pulser for Odoo`.
> SSOT: `ssot/brand/naming_reconciliation.yaml`
> Last updated: 2026-04-10

---

## Target Canonical Names

| Context | Name |
|---------|------|
| Product (human-facing) | **Pulser for Odoo** |
| Product subtitle | **Pulser Assistant for Odoo** |
| Machine slug | `pulser-odoo` |
| Machine key | `pulser_odoo` |
| Odoo addon | `ipai_odoo_copilot` (unchanged) |
| Odoo version | **Odoo CE 18.0** (NOT 19) |

## Foundry Agent Names

| Old | New |
|-----|-----|
| `ipai-copilot` (top-level agent) | `pulser-odoo` |
| `ask-agent` | `pulser-odoo-ask` |
| `authoring-agent` | `pulser-odoo-authoring` |
| `livechat-agent` | `pulser-odoo-livechat` |
| `transaction-agent` | `pulser-odoo-transaction` |

## Azure Infra — KEEP AS-IS

These are NOT renamed (user directive: keep Azure infra naming):

| Resource | Keep |
|----------|------|
| `ipai-copilot-resource` | Azure AI resource hostname |
| `ipai-copilot` | Foundry project path/ID |
| `ipai-copilot-gateway` | ACA app |
| `ipai_odoo_copilot` | Odoo addon technical name |
| `wg-pulser` | Model deployment alias |
| All `ca-ipai-*`, `pg-ipai-*`, `kv-ipai-*`, `afd-ipai-*`, `acripaiodoo` | Azure infra |

## Rename Matrix

| Old Token | New Token | Scope | Occurrences | Files |
|-----------|-----------|-------|-------------|-------|
| `Odoo CE 19.0` / `Odoo CE 19` / `Odoo 19` | `Odoo CE 18.0` / `Odoo CE 18` / `Odoo 18` | Version fix | 225 | 123 |
| `Odoo Copilot` | `Pulser for Odoo` | Human-facing | 280+ | 160+ |
| `InsightPulseAI Odoo Copilot` | `Pulser for Odoo` | Human-facing | 54 | 37 |
| `IPAI Odoo Copilot` | `Pulser for Odoo` | Human-facing | (incl above) | |
| `Pulser Assistant` (bare) | `Pulser for Odoo` | Human-facing | 28 | 22 |
| `reverse-sap-joule` | `pulser-odoo` | Key/path | 1 | 1 |
| `reverse_sap_joule` | `pulser_odoo` | Key | 1 | 1 |
| `Reverse SAP Joule` | `Pulser for Odoo` | Human-facing | 3 | 2 |
| `ask-agent` | `pulser-odoo-ask` | Agent name | 56 | 15 |
| `authoring-agent` | `pulser-odoo-authoring` | Agent name | 43 | 13 |
| `livechat-agent` | `pulser-odoo-livechat` | Agent name | 44 | 15 |
| `transaction-agent` | `pulser-odoo-transaction` | Agent name | 44 | 13 |
| `pulser-assistant` | `pulser-odoo` | Slug | 3 | 3 |
| `odoo-copilot` (product/agent) | `pulser-odoo` | Slug | varies | varies |

## Execution Phases

### Phase 1 — Version Fix (CRITICAL)
Fix all `Odoo 19` → `Odoo 18`. Factually wrong. 123 files, batch-safe.

### Phase 2 — SSOT Agent Names (HIGH)
Rename 4 child agents in ~15 SSOT/script files. Concentrated, batch-safe.

### Phase 3 — Product Name in SSOT/Spec (HIGH)
Rename `Odoo Copilot` → `Pulser for Odoo` in SSOT YAML and spec bundles. ~40 files, review-required.

### Phase 4 — Product Name in Docs (MEDIUM)
Rename in architecture docs, product docs, guides. ~80 files.

### Phase 5 — Product Name in Code (MEDIUM)
Rename in TypeScript, Python, HTML, tests. ~50 files. Needs test verification.

### Phase 6 — Directory Renames (LOW/DEFERRED)
Rename directories like `agents/foundry/ipai-odoo-copilot-azure/`. Deferred — cascading path updates.

### Phase 7 — Spec Bundle Paths (MEDIUM)
Fix dangling `spec/reverse-sap-joule-*` references. 3 files.

## Safety Rules

1. Never rename `ipai_odoo_copilot` (Odoo addon technical name)
2. Never rename Azure resource hostnames/IDs
3. Never rename inside `odoo/` vendor directory
4. Review each file before batch rename to avoid breaking imports/paths
5. Run tests after code-level renames (Phase 5)
6. Pulser is consumer-facing — internal technical IDs may keep legacy names for stability
