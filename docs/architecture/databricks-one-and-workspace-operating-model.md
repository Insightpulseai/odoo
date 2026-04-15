# Databricks One + Workspace Operating Model (IPAI)

> **Locked:** 2026-04-15
> **Authority:** this file (canonical operating model for Databricks surfaces + URL + search/discovery)
> **Workspace:** `dbw-ipai-dev` — `https://adb-7405608559466577.17.azuredatabricks.net`
> **Companions:**
> - [`docs/skills/databricks-ipai-grounded.md`](../skills/databricks-ipai-grounded.md) — grounded setup guide
> - [`docs/architecture/data-model-erd.md`](./data-model-erd.md) — schema layout
> - [`docs/architecture/revised-bom-target-state.md`](./revised-bom-target-state.md) — data-intelligence plane
>
> **Microsoft refs:**
> - [Databricks One (workspace + account)](https://learn.microsoft.com/azure/databricks/admin/workspace-one/)
> - [Per-workspace URL authority](https://learn.microsoft.com/azure/databricks/workspace/workspace-details)
> - [Workspace browser + special folders](https://learn.microsoft.com/azure/databricks/workspace/workspace-objects)
> - [Workspace search + Unity Catalog](https://learn.microsoft.com/azure/databricks/search/)

---

## 0. Canonical contract (top-of-file lock)

```
Workspace URL authority       = per-workspace URL only
                                https://adb-7405608559466577.17.azuredatabricks.net
Workspace consumption surface = Databricks One
Workspace authoring/admin UI  = Lakehouse workspace UI
Search / discovery authority  = Unity Catalog metadata + tags + Genie spaces
Legacy regional URLs          = forbidden (slower, less reliable, breaks workspace-ID features)
```

Any script, doc, SDK config, pipeline variable, or SSOT entry that references Databricks MUST use the per-workspace URL above. Legacy regional URLs (e.g., `*.azuredatabricks.net` without the `adb-<id>.<shard>` prefix) are non-canonical and must be removed on sight.

---

## 1. Two surfaces, two audiences

| Surface | Audience | Purpose | Scope |
|---|---|---|---|
| **Databricks One** | Business users (CFO, finance ops, research leads) | Dashboards, Genie NL queries, Databricks Apps, Chat | Consumption only |
| **Lakehouse workspace UI** | Data engineers, platform engineers, Pulser build team | Notebooks, Asset Bundles, jobs, UC admin, cluster config, Git folders | Authoring + admin |

**Rule:** Databricks One is NOT the IPAI platform shell. It is a business-consumption surface that sits alongside:

- **Odoo** — transaction system of record
- **Foundry** — agent runtime
- **Databricks** — governed analytics + business consumption
- **Pulser** — multi-agent operating copilot spanning the above

Do not route engineering work, authoring, or admin through Databricks One. Do not treat Databricks One as the "SaaS product shell" for IPAI customers — that is PrismaLab / Pulser surfaces + Odoo.

---

## 2. Access model

| User entitlement | Default landing UI | Can switch? |
|---|---|---|
| **Consumer access only** | Databricks One | No — stays in Databricks One |
| **Broader entitlements** (engineer, analyst, admin) | Lakehouse workspace UI | Yes — can toggle to Databricks One |

This mirrors real-world IPAI roles:

- TBWA\SMP CFO, W9 ops lead → Consumer → Databricks One
- IPAI data engineers, Pulser build team → Broader → Lakehouse UI (with option to preview Databricks One)

---

## 3. Chat posture (Beta — gated)

Databricks One Chat is **Beta** and depends on preview flags + SQL warehouse permission.

**Do NOT enable Chat broadly** until the following exist:

```
1. At least one clean Genie space
2. Governed Gold / semantic tables in Unity Catalog
3. At least one useful dashboard consuming those tables
4. Clear warehouse permission model (who can use serverless, who can't)
5. Optional external connectors (Google Drive, SharePoint) — only if a real document-search use case exists
```

**Chat behavior (when enabled):**
- Routes to matching Genie space; falls back to "Genie in Agent mode" if no space matches
- External connectors (Google Drive, SharePoint) require per-user OAuth
- Limits: one active conversation, auto-selected SQL warehouse, 10 MB file cap, limited supported file types

**IPAI-specific rule:** Chat beta stays disabled on `dbw-ipai-dev` until steps 1–4 above are real. A weak demo is worse than no demo.

---

## 4. Workspace folder model

Databricks already gives a useful organizational model via special folders. Adopt it verbatim:

| Folder | Purpose | IPAI usage |
|---|---|---|
| `Workspace` | Root | Do not clutter root |
| `Shared` | Organization-wide business assets | Dashboards, Genie spaces, canonical notebooks, reference queries for business users |
| `Repos` / Git folders | Git-backed engineering assets | Asset Bundle sources, pipeline definitions, ETL notebooks under version control |
| `Users` | Personal scratch | Exploration only — never the home of business-critical assets |

**Rules:**
- Business-critical assets live under `Shared/` or `Repos/`, never in `Users/`.
- Anything in `Users/` is disposable by policy; not backed up, not referenced by pipelines.
- Git folder authoring context is preferred for any engineering work (tree view preview is on).
- Folder-level sharing/permissions replace ad-hoc per-object ACLs where possible.

---

## 5. Search + discovery (Unity Catalog is the prerequisite)

Workspace search covers notebooks, dashboards, alerts, jobs, repos, files, folders. But the **serious** discovery experience — the one that makes business users succeed — depends on Unity Catalog.

| Capability | Requires UC? |
|---|---|
| Find a notebook / dashboard / job | No — workspace search handles it |
| Find a table by name | No — but poor quality without UC |
| Semantic search on tables | **Yes — UC only** |
| Tag-based search | **Yes — supported object types need UC** |
| Popularity-boosted ranking | **Yes — UC managed tables** |
| Knowledge cards in search results | **Yes — UC managed tables only** |

**Implication for IPAI:**
- If business users are going to rely on Databricks One + Chat, Unity Catalog must be populated with real governed tables (not just `ppm` catalog skeleton).
- Tag every UC table with ownership, sensitivity, tenant scope, freshness SLA.
- Gold-layer tables in `ppm.gold.*` are the canonical target for Genie spaces and dashboards.

---

## 6. Business rollout sequence

Do not skip steps. Enabling Chat before steps 1–4 produces a demo that fails in front of a customer.

```
Step 1. Unity Catalog contracts
        - Catalog: ppm (live)
        - Schemas: bronze / silver / gold (live)
        - Governed table definitions with tags + ownership

Step 2. Gold / semantic tables
        - ppm.gold.<table> populated via Lakeflow SDP
        - Primary/foreign keys declared (UC PK/FK support)
        - Descriptions + tags on every column

Step 3. Dashboards
        - At least one dashboard per domain (finance, ops, research)
        - Lives in Shared/
        - Consumes ppm.gold.* only

Step 4. Genie spaces
        - One Genie space per domain dashboard
        - Curated dataset scope (no "all tables"); starts narrow
        - Owners named per space

Step 5. Databricks One consumption
        - Grant Consumer entitlement to business users
        - They land in Databricks One by default
        - Validate: can they find + use the Step 3 dashboards?

Step 6. Chat beta (gated rollout)
        - Enable for 2–3 pilot users (CFO + 1 ops lead)
        - Chat routes to the Step 4 Genie spaces
        - Collect feedback; iterate space scope before broad rollout
```

---

## 7. What Databricks One is NOT

To prevent misuse of the surface:

- **NOT the IPAI product shell.** PrismaLab / Pulser surfaces + Odoo are.
- **NOT the authoring environment.** Engineers use Lakehouse UI + Git folders.
- **NOT a replacement for Power BI.** Power BI is the primary mandatory business reporting surface (per `CLAUDE.md` cross-repo invariant #12); Databricks One + dashboards complement it, not replace it.
- **NOT for customer-facing tenant shells.** Multitenant customer UX goes through Odoo + Pulser, not directly through Databricks One.
- **NOT where source-of-truth lives.** Truth lives in Unity Catalog managed tables + Odoo PG. Databricks One reads from them.

---

## 8. Enforcement checklist

| Check | Rule | Where enforced |
|---|---|---|
| Workspace URL | Per-workspace URL only | Grep for legacy `.azuredatabricks.net` without `adb-` prefix in `.mcp.json`, `infra/databricks/`, `azure-pipelines/*.yml`, `ssot/` |
| Folder structure | No business-critical assets in `Users/` | Periodic audit via Databricks API (list workspace objects under `/Users/`) |
| Chat beta | Disabled until rollout Steps 1–4 are green | Admin console; documented as explicit gate in `docs/skills/databricks-ipai-grounded.md` §3 |
| UC-first | Every new table is UC-managed | Asset Bundle template forces `USING DELTA` + UC catalog binding |
| Search quality | Every UC table has owner tag + description | Lakeflow SDP validation step + monthly audit |

---

## 9. Delta vs. current state (2026-04-15)

| Item | Current | Target per this model | Gap |
|---|---|---|---|
| Per-workspace URL | Used in `.mcp.json` ✅ | Used everywhere | Grep audit pending across repo |
| Catalog `ppm` | Schemas exist (bronze/silver/gold) | Gold tables populated + tagged | Pending Lakeflow SDP pipelines + tag policy |
| Dashboards | None under `Shared/` | ≥1 per domain | Pending |
| Genie spaces | None | ≥1 per domain dashboard | Pending; `databricks-genie` MCP waits on this |
| Databricks One rollout | No business users entitled yet | TBWA\SMP CFO + W9 ops pilot | Pending Step 3 |
| Chat beta | Disabled | Disabled until Steps 1–4 green | Correct posture |
| Folder hygiene | Unknown | `Shared/` / `Repos/` / `Users/` discipline | Audit needed |

---

## 10. Bottom line

```
Databricks One   = business consumption surface (post-UC-and-Genie)
Lakehouse UI     = engineering + admin surface (today)
Per-workspace URL = canonical; no legacy regional URLs
Unity Catalog    = prerequisite for serious search/discovery
Chat beta        = do not enable until Steps 1–4 are real

Databricks is ready to be the business-consumption + governed-analytics surface
for IPAI — only after the semantic + Genie layer is real. The workspace exists;
the data product doesn't yet.
```

---

## 11. References

Internal:
- [`docs/skills/databricks-ipai-grounded.md`](../skills/databricks-ipai-grounded.md) — operational runbook
- [`docs/architecture/data-model-erd.md`](./data-model-erd.md) — schema
- [`docs/architecture/revised-bom-target-state.md`](./revised-bom-target-state.md) — data-intelligence plane
- [`infra/databricks/databricks.yml`](../../infra/databricks/databricks.yml) — Asset Bundle root
- [`.mcp.json`](../../.mcp.json) — MCP config (per-workspace URL in `databricks-genie`)

External (Microsoft Learn):
- [Databricks One](https://learn.microsoft.com/azure/databricks/admin/workspace-one/)
- [Per-workspace URL authority](https://learn.microsoft.com/azure/databricks/workspace/workspace-details)
- [Workspace browser + special folders](https://learn.microsoft.com/azure/databricks/workspace/workspace-objects)
- [Workspace search + Unity Catalog](https://learn.microsoft.com/azure/databricks/search/)
- [Genie spaces](https://learn.microsoft.com/azure/databricks/genie/)

---

*Last updated: 2026-04-15*
