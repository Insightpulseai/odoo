# Canonical Platform Architecture — IPAI (8 components, 3 planes)

> **Locked:** 2026-04-15
> **Authority:** this file is the top-of-stack architecture reference for IPAI.
> All subordinate docs (BOM v2, Fabric mirroring target state, Databricks operating model, Pulser surface design) must align with this one.
>
> **Companions:**
> - [`docs/architecture/revised-bom-target-state.md`](./revised-bom-target-state.md) — bill of materials (what's provisioned)
> - [`docs/architecture/fabric-mirroring-target-state.md`](./fabric-mirroring-target-state.md) — mirror paths
> - [`docs/architecture/databricks-one-and-workspace-operating-model.md`](./databricks-one-and-workspace-operating-model.md) — Databricks surfaces
> - [`CLAUDE.md`](../../CLAUDE.md) — cross-repo invariants

---

## 0. One-line contract

```
Odoo is truth.   Postgres stores it.   Foundry thinks.   MAF agents act.
Databricks processes.   UC governs.   Fabric publishes.   ADLS persists.
AI Landing Zone is the envelope around all of the above.
```

Three planes:

| Plane | Purpose | Components |
|---|---|---|
| **Transaction** | System of record + physical DB | Odoo 18 CE + OCA, PostgreSQL Flex |
| **Intelligence** | Inference + agents | Foundry, MAF Agent Platform |
| **Analytics & consumption** | Processing + governance + publication | Databricks, Unity Catalog, Fabric, ADLS Gen2 |

Governance envelope: **AI Landing Zone** (subscription boundary, policy, tags, networking, MI).

---

## 1. The 8 components

### 1.1 Odoo 18 CE + OCA — system of record (SoR)

- Every financial transaction, PO, SO, expense, and BIR filing lives here.
- Nothing outside Odoo writes into Odoo-owned domains.
- `ipai_*` delta modules extend CE only where OCA can't cover (BIR compliance, expense liquidation, AR collections).
- Runtime: Azure Container Apps (`ca-ipai-odoo-web-dev` + worker + cron).
- CE only. No Enterprise. No `odoo.com` IAP.
- Module philosophy: **Config → CE property fields → OCA → adjacent OCA → compose → thin `ipai_*` as last resort** (see [`CLAUDE.md`](../../CLAUDE.md) §"Odoo extension and customization doctrine").

### 1.2 PostgreSQL Flexible Server (`pg-ipai-odoo`, SEA) — physical DB

- Backs Odoo (`odoo`, `odoo_staging`, `odoo_dev`).
- Also hosts the `platform` schema with `ops.runs`, `ops.run_events` — agent audit trail persisted alongside transaction data.
- Extensions enabled (Azure allowlist): `vector`, `azure_ai`, `age`, `timescaledb`, `pg_diskann`, `azure_storage`, `pg_cron`, `pgcrypto`, `uuid-ossp`, `pg_trgm`, `btree_gin`, `btree_gist`, `hstore`, `postgres_fdw`, `tds_fdw`, `oracle_fdw`, `pgaudit`, `hypopg`, `pg_hint_plan`, `pg_partman`, `pg_stat_statements`.
- `azure_ai` extension lets PG call Foundry models directly from SQL.
- **PgBouncer on port 6432** — config toggle (`pgbouncer.enabled = True`), not a deployment. Apps connect through 6432; admin/DDL on 5432.
- Zone Redundant HA + 2 Approved Private Endpoints on `vnet-ipai-dev/snet-pe`.
- Local dev parity: stock PG 16 + `pgvector/pgvector:pg16` Docker image covers 90%+ of features; Azure-only extensions (`azure_ai`, `pg_diskann`, `azure_local_ai`, `azure_storage`) branch on server version or are exercised only against Azure.

### 1.3 Azure AI Foundry (`ipai-copilot-resource`, East US 2) — inference plane

- All model calls route through Foundry.
- Model catalog: `o3-pro`, `gpt-5.4` (1M-token context), `Sora 2`, `gpt-image-1.5`, `deep-research` (via Agent Service only — not available as direct deployment).
- `model-router` at the front auto-selects models based on task class.
- Keyless via Managed Identity + `DefaultAzureCredential`.
- Location rationale: East US 2 is the capacity region; SEA workloads accept the cross-region latency for model access.
- Not the agent runtime — see 1.4.

### 1.4 MAF Agent Platform — 6 provisioned agents on ACA

Six agents, all Microsoft Agent Framework (MAF)-based, all running on Azure Container Apps:

| Agent | Purpose |
|---|---|
| `tax-guru` | PH BIR filings, tax computation, compliance checks |
| `bank-recon` | Bank statement reconciliation against Odoo ledger |
| `ap-invoice` | AP invoice intake, three-way match, posting |
| `doc-intel` | Document intelligence (invoices, receipts, contracts) |
| `finance-close` | Month-end close orchestration |
| `pulser` | Router / generalist — delegates to specialists |

**Tool access rules:**
- Agents call **Foundry** for inference.
- Agents call **`ipai-odoo-mcp`** to read/write Odoo (the Odoo MCP server — canonical tool path to Odoo; bypassing MCP is forbidden).
- Agents read PostgreSQL **only via MCP** — never direct connection strings to PG from agent code.
- Agent state lives in **`cosmos-ipai-dev`** (Cosmos DB, SESSION-scoped state, not a cross-cutting data store).
- Audit trail: every agent run writes to `platform.ops.run_events` in PG (see 1.2).

### 1.5 Databricks (`dbw-ipai-dev`) — processing engine

- Reads from PG via **Lakehouse Federation** (zero-copy — no data duplication in Databricks for operational tables) and from Odoo exports.
- Runs **DLT pipelines Bronze → Silver → Gold**, writing to ADLS.
- Writes to ADLS (CDM folder format) only.
- **Never writes back to Postgres or Odoo.** Read-only from operational systems.
- Premium tier (UC required).
- Region: Southeast Asia (co-located with PG).

### 1.6 Unity Catalog — governance inside Databricks

- **Not a separate service** — it is the metastore inside the Databricks workspace.
- Controls: who sees which tables (catalog/schema/table RBAC), row-level security, column-level security, data lineage across Bronze/Silver/Gold.
- Canonical catalog for IPAI Finance/PPM/Research: `ppm`. Schemas: `bronze`, `silver`, `gold` (today); `metrics`, `features` (planned).
- Prerequisite for: Databricks One Chat, Genie spaces, Fabric metadata mirroring, Power BI semantic models.

### 1.7 Microsoft Fabric (`fcipaidev`) — consumption layer

- Power BI dashboards, Finance PPM workspace, OKR reporting.
- Reads **Gold from ADLS** (via OneLake shortcut or mount).
- **Mirrors** directly from `pg-ipai-odoo` via Fabric Mirroring (**Preview** for PG Flex as of 2026-04-15 — confirm status before production commit).
- Exposes a **Fabric Data Agent** (future MCP endpoint) so M365 Copilot can query Odoo data without touching PG directly.
- Trial capacity — expires ~2026-05-20. F-SKU procurement decision pending.

### 1.8 ADLS Gen2 (`stipaidevlake`) — the lake

- **CDM folder format per entity** — so Fabric, Synapse, and any CDM-aware tool can read without schema mapping.
- Layers:
  - **Bronze** — raw Odoo exports (minimal transform)
  - **Silver** — cleaned, joined, type-conformed
  - **Gold** — domain-specific aggregates (finance metrics, PPM, research)
- Purview catalogs the whole thing (data discovery + sensitivity classification).

---

## 2. AI Landing Zone — the envelope (not a service)

The governance scaffolding that makes all 8 components operate securely together:

| Concern | Artifact |
|---|---|
| Subscription boundary | `Microsoft Azure Sponsorship` (eba824fb-…) |
| Policy assignments | Built-in + custom Azure Policies (tag enforcement, region restrictions, TLS minimum, diagnostic settings) |
| Tag contracts | 17 mandatory tags incl. `tenant_scope`, `billing_scope`, `regulated_scope`, `source_repo` (per BOM v3 tag contract) |
| Budget alerts | Per-RG + per-component |
| Private DNS zones | `privatelink.postgres.database.azure.com`, `privatelink.azurecr.io`, etc. |
| VNet / subnet topology | `vnet-ipai-dev` with `snet-pe`, `snet-aca`, `snet-dbw`, `snet-jumpbox` |
| Managed identity assignments | Per-ACA-app MI + UC access connector + per-Foundry-project MI |
| WAF alignment | Azure Well-Architected Framework checklist applied at this level |

**Rule:** No component deploys without Landing Zone compliance. Non-compliant resources are removed by policy (warn → deny).

---

## 3. Data flow patterns

### 3.1 Write path (user action → durable truth)

```
User / Agent  →  Odoo (via UI or ipai-odoo-mcp)
              →  res.* / account.* / project.* models
              →  PostgreSQL (pg-ipai-odoo)  ← SoR persisted
              →  platform.ops.runs  ← audit row written
```

### 3.2 Analytics path (truth → consumable insight)

```
pg-ipai-odoo  →  Databricks Lakehouse Federation (zero-copy read)
              →  DLT Bronze  (ADLS stipaidevlake/bronze/*)
              →  DLT Silver  (ADLS stipaidevlake/silver/*)
              →  DLT Gold    (ADLS stipaidevlake/gold/*)
              →  Unity Catalog (registration + RLS/CLS)
              →  Fabric (OneLake shortcut to Gold, or Fabric Mirror to PG)
              →  Power BI / Fabric Data Agent / M365 Copilot
```

### 3.3 Agent path (user question → action)

```
User  →  Copilot/Teams/Web surface
      →  Pulser router agent (ACA)
      →  delegates to specialist (tax-guru / bank-recon / ap-invoice / doc-intel / finance-close)
      →  Foundry (inference) + ipai-odoo-mcp (read/write Odoo)
      →  Odoo CRUD happens via MCP → PG
      →  Response back to surface
      →  platform.ops.run_events appended
```

### 3.4 Never-do list (anti-patterns)

| Pattern | Why forbidden |
|---|---|
| Agent writes directly to PG | Bypasses Odoo validation + audit |
| Databricks writes to PG or Odoo | Breaks read-only analytics contract |
| Fabric writes upstream | Fabric is consumption, not authoritative |
| Odoo calls Foundry without going through MAF agent | Agents own inference routing + guardrails |
| Two components claiming same data (Databricks Gold + Fabric Mirror of same PG table) | Diverges truth — pick one (Fabric Mirror for operational tables; Databricks Gold for cross-source joins) |

---

## 4. Deltas vs. current repo state (2026-04-15)

Captured here so future work knows what's aspirational vs. live.

| Component | Current state | Target per this doc | Gap |
|---|---|---|---|
| Odoo 18 CE + OCA | Live on ACA; baseline achieved | Same | None architectural |
| PostgreSQL Flex | Live (OLD sub); PgBouncer enabled 2026-04-15 | Same; cross-sub move per ADR-002 | Cross-sub move pending |
| Foundry | `ipai-copilot-resource` live East US 2; o3-pro etc. deployments not yet confirmed | Per §1.3 catalog | Verify `gpt-5.4`, `Sora 2`, `gpt-image-1.5`, `deep-research`, `model-router` deployments exist |
| MAF Agent Platform | 6 Teams app regs exist for these agents per `entra-app-registry-governance.md` | All 6 running on ACA | Verify ACA apps per agent; today only `pulser` and `tax-guru` are referenced as built |
| `ipai-odoo-mcp` | **P0 gap** per memory `project_odoo_mcp_server_p0_gap` | Canonical tool for agent→Odoo | **To build** — no upstream OSS exists |
| `cosmos-ipai-dev` | Memory says "defer Cosmos until justified" | Used for agent session state | Decision point — Cosmos now justified by MAF state requirements; or substitute (Redis, PG table) |
| Databricks | Live, UC enabled, `ppm` catalog + 3 schemas | Same | DLT pipelines Bronze→Silver→Gold not yet wired for Odoo tables |
| Unity Catalog | Enabled | Populated with governed tables | Gold-layer tables pending |
| Fabric | `fcipaidev` trial active; expires ~2026-05-20 | F-SKU procurement; both mirror paths wired | Procurement + mirror setup pending |
| ADLS Gen2 | `stipaidevlake` exists | CDM folder layout per entity | CDM structure not yet enforced |
| AI Landing Zone | Partial (5+1 RG model + tags + policies live) | Full compliance + private DNS zones + MI per component | Ongoing |

---

## 5. Decisions this doc locks

1. **Agents read PG via MCP only.** No direct PG connection strings in agent code.
2. **Databricks is read-only from operational systems.** No write-back.
3. **Fabric is consumption-only.** No upstream mutations.
4. **Odoo is authoritative.** Everything else derives.
5. **Six named MAF agents — no more, no less — for Wave-01 scope.** New agents require an architecture amendment.
6. **`ipai-odoo-mcp` is the canonical Odoo tool path.** Building it is a P0.
7. **Agent state = Cosmos (`cosmos-ipai-dev`); agent audit = PG `platform.ops.*`.** Two stores, two purposes.
8. **ADLS is CDM-folder-formatted.** Any tool that needs lake data reads via CDM, not custom schemas.
9. **AI Landing Zone compliance is a deploy gate.** Non-compliant resources are denied by policy.

---

## 6. References

Internal:
- [`docs/architecture/revised-bom-target-state.md`](./revised-bom-target-state.md) — BOM v2
- [`docs/architecture/fabric-mirroring-target-state.md`](./fabric-mirroring-target-state.md)
- [`docs/architecture/databricks-one-and-workspace-operating-model.md`](./databricks-one-and-workspace-operating-model.md)
- [`docs/architecture/multitenant-saas-target-state.md`](./multitenant-saas-target-state.md)
- [`docs/architecture/pulser-assistant-surface-design.md`](./pulser-assistant-surface-design.md)
- [`docs/architecture/entra-app-registry-governance.md`](./entra-app-registry-governance.md)
- [`CLAUDE.md`](../../CLAUDE.md) — operating contract + invariants
- Memory: `target_architecture_v2`, `operating_model_decisions`, `project_odoo_mcp_server_p0_gap`, `pulser_agent_classification`

External (Microsoft Learn):
- [Azure Well-Architected Framework for AI workloads](https://learn.microsoft.com/azure/well-architected/ai/)
- [Fabric Mirroring from Azure Postgres Flex](https://learn.microsoft.com/fabric/mirroring/azure-database-postgresql)
- [Unity Catalog](https://learn.microsoft.com/azure/databricks/data-governance/unity-catalog/)
- [Microsoft Agent Framework](https://learn.microsoft.com/semantic-kernel/agents/)
- [Azure Postgres `azure_ai` extension](https://learn.microsoft.com/azure/postgresql/flexible-server/generative-ai-azure-ai-extension)
- [CDM folder format](https://learn.microsoft.com/common-data-model/data-lake)

---

*Last updated: 2026-04-15*
