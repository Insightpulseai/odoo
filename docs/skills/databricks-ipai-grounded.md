# Databricks on IPAI — Grounded Setup Guide

> **Locked:** 2026-04-15
> **Authority:** this file (IPAI-grounded Databricks operating doc)
> **Workspace:** `dbw-ipai-dev` (Premium, SEA, Sponsored sub) — already provisioned ✅
> **Companions:**
> - [`docs/skills/azure-postgresql-ipai-grounded.md`](./azure-postgresql-ipai-grounded.md) — same methodology
> - [`docs/architecture/databricks-one-and-workspace-operating-model.md`](../architecture/databricks-one-and-workspace-operating-model.md) — URL / surface / rollout authority
> - [`docs/architecture/data-model-erd.md`](../architecture/data-model-erd.md) — schema layout
> - [`docs/architecture/revised-bom-target-state.md`](../architecture/revised-bom-target-state.md) — data-intelligence plane
>
> **Microsoft refs:**
> - [Databricks tutorials index (Microsoft Learn)](https://learn.microsoft.com/azure/databricks/getting-started/)

---

## 0. Workspace ground truth

| Field | Value |
|---|---|
| Workspace | `dbw-ipai-dev` |
| URL | `https://adb-7405608559466577.17.azuredatabricks.net` |
| Resource group | `rg-ipai-dev-ai-sea` |
| Managed RG | `rg-ipai-dev-dbw-managed` |
| Subscription | Microsoft Azure Sponsorship (`eba824fb-…`) ✅ already on sponsored |
| Region | Southeast Asia |
| Tier | Premium (RBAC + Unity Catalog) |
| Type | Hybrid |
| SQL Warehouse ID | `e7d89eabce4c330c` (per memory) |

Per [`revised-bom-target-state.md`](../architecture/revised-bom-target-state.md) §Data-intelligence plane: 1 Databricks workspace per env. Current = nonprod (= `dbw-ipai-dev`). Prod workspace pending.

---

## 1. What's already in place (per session memory + this verification)

| Component | Status |
|---|---|
| Workspace | ✅ Live |
| Unity Catalog | ✅ Enabled (Premium tier required, confirmed) |
| Access connector | ✅ `unity-catalog-access-connector` in `rg-ipai-dev-dbw-managed` |
| Workers VNet | ✅ `workers-vnet` + `workers-sg` + managed identity in dbw-managed RG |
| SQL Warehouse | ✅ ID `e7d89eabce4c330c` |
| Storage | ✅ `dbstorageqba5raeuajc6u` (UC managed) + `stlkipaidev` (lake) |
| Catalogs | per memory: `ppm` (catalog), schemas: `bronze` / `silver` / `gold` (visible in VS Code Databricks extension) |
| Fabric mirroring | ✅ ACTIVE (`fcipaidev` mirror per memory) |

---

## 2. The 5 Microsoft Learn tutorials — IPAI applicability

From the Microsoft Learn index user shared:

| Tutorial | Apply to IPAI? | How |
|---|---|---|
| **Query and visualize data** | ✅ Yes — onboarding path for new team members | Use `ppm` catalog + `bronze` schema sample data |
| **Import + visualize CSV from notebook** | ⚠️ Useful pattern only | Real ingestion uses Auto Loader / Lakeflow, not manual CSV |
| **Create a table + grant privileges** | ✅ Required for any new dataset | Use UC `GRANT` syntax on `ppm.<schema>.<table>` |
| **Build ETL pipeline (Lakeflow SDP)** | ✅ Canonical for IPAI ingestion | Wire to `infra/databricks/` Asset Bundles |
| **Build ETL pipeline (Apache Spark)** | Reference only | Lakeflow SDP is the modern path |
| **Train + deploy ML model** | ⏸ Defer | Pulser is custom-engine, not ML-first |
| **Query LLMs + prototype agents (no-code)** | ⏸ Reference only | Pulser uses Foundry SDK 2.x, not Databricks AI Playground |
| **Explore Databricks One** | ✅ Future for business users | Genie + dashboards for TBWA\SMP CFO surface |
| **Segment customers with Genie** | ✅ Future — fits Quilt-like wedge | Per `data-intelligence-vertical-target-state.md` |

---

## 3. Auth posture (IPAI doctrine alignment)

```
Default:        DefaultAzureCredential → Entra Managed Identity
                (per CLAUDE.md secrets policy + multitenant doctrine)

Identity:       unity-catalog-access-connector → reads ADLS via MI
                Per-workspace MI → writes audit logs

Workspace user: Per-user Entra (admin@insightpulseai.com today)

Service principal (when needed for automation):
                Use Entra app reg + cert (or federated identity)
                Per docs/architecture/entra-app-registry-governance.md
```

**Forbidden:**
- Personal Access Tokens (PAT) in any tracked file
- DBX PAT in CI without time-limited scope
- Workspace passwords (no such thing — Entra-only)

---

## 4. Asset Bundles (IPAI delivery path)

Per memory `databricks-bundles-deploy.yml` referenced in `azure-pipelines/`:

```bash
# Local dev
databricks auth login --host https://adb-7405608559466577.17.azuredatabricks.net
databricks bundle validate
databricks bundle deploy -t nonprod

# CI deploy (via Azure Pipelines, NOT GitHub Actions per doctrine #24)
azure-pipelines/databricks-bundles-ci.yml
azure-pipelines/databricks-bundles-promote.yml
```

Bundle config lives at `infra/databricks/databricks.yml` (visible in your VS Code Databricks extension panel screenshot).

Per VS Code panel:
- `catalog: ppm`
- `schema_bronze: bronze`
- `schema_silver: silver`
- `schema_gold: gold`
- `warehouse_id: e7d89eab...`

---

## 5. Action checklist (sequence per IPAI doctrine)

### Already done

- [x] Workspace `dbw-ipai-dev` provisioned + on Sponsored sub
- [x] Unity Catalog enabled
- [x] Access connector + MI configured
- [x] SQL Warehouse provisioned
- [x] Bundle structure in `infra/databricks/`
- [x] Fabric mirroring active

### Pending — short term

- [ ] Pin Databricks CLI version in devcontainer (per `databricks/cli` register entry)
- [ ] Set default `databricks` profile (fixes "Multiple login profile" prompt in VS Code extension)
- [ ] Configure Genie Space in workspace UI (prerequisite for `databricks-genie` MCP)
- [ ] Apply IPAI tag set (17 mandatory tags) to workspace + access connector + storage

### Pending — medium term

- [ ] Onboard PrismaLab corpus to UC catalog `prismalab` (separate from `ppm`)
- [ ] Stand up audience-clustering ML pipeline (per `data-intelligence-vertical-target-state.md` Phase 2)
- [ ] Power BI semantic model over UC gold layer (when PBI Pro procured)

### Pending — Pulser integration

- [ ] Wire Pulser data-intel agent skill to query UC via `databricks-genie` MCP
- [ ] Add Databricks Asset Bundle deploy stage to release pipelines
- [ ] Auth Pulser → Databricks via system MI, never PAT

---

## 6. Genie Space prerequisites (for the `databricks-genie` MCP)

Per `databricks-genie` MCP entry in [`.mcp.json`](../../.mcp.json):

1. **Workspace already provisioned** ✅
2. **Pro or Serverless SQL warehouse with CAN USE permission** — verify `e7d89eabce4c330c`
3. **Databricks Assistant enabled** — workspace setting
4. **Unity Catalog access** to relevant schemas — confirm `ppm.gold` is accessible
5. **Create Genie Space:**
   - Workspace UI → AI/BI → Genie Spaces → New
   - Pick datasets (start with `ppm.gold.<table>`)
   - Capture the Space ID
6. **Update `.mcp.json`** with real `DATABRICKS_GENIE_SPACE_ID`
7. **Install MCP server:**
   ```bash
   git clone https://github.com/alexxx-db/databricks-genie-mcp ~/Code/databricks-genie-mcp
   cd ~/Code/databricks-genie-mcp
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
8. **Update `.mcp.json` with absolute path to venv Python:**
   ```json
   "command": "/Users/tbwa/Code/databricks-genie-mcp/.venv/bin/python3"
   ```

---

## 7. Don't / anti-patterns

| Don't | Why |
|---|---|
| Provision via Azure Portal manually | Bicep + `databricks/terraform-provider-databricks` are canonical |
| Use PAT auth in tracked code | Doctrine — MI only for service workloads |
| Create Cosmos DB for "session state" | Per BOM v2: defer Cosmos until justified |
| Train ML models on Databricks "because we can" | No customer ML use case yet — defer |
| Use the `gold` schema as a publishing surface for external consumers | Use UC managed publishing or Fabric mirror; `gold` is the analytics consumption layer |
| Adopt `dbt` without a plane decision | `databricks/dbt-databricks` is `clone_as_reference` only — defer |
| Run ETL via Apache Spark when Lakeflow SDP fits | Lakeflow SDP is the modern Databricks ETL path |

---

## 8. Pulser integration plan (when data-intel skill activates)

```
Pulser → databricks-genie MCP → Genie Space → UC catalog (ppm.gold.*)
       → returns natural-language SQL response
       → renders as artifact in Pulser systray (per ipai_artifact_preview when built)
```

Tied to:
- `data-intelligence-vertical-target-state.md` Phase 2 (PH data intel wedge)
- `pulser-assistant-surface-design.md` Surface 3 (PrismaLab AI grounded retrieval)

---

## 9. References

Internal:
- [`infra/databricks/databricks.yml`](../../infra/databricks/databricks.yml) — bundle root
- [`infra/databricks/`](../../infra/databricks/) — Asset Bundle definitions
- [`azure-pipelines/databricks-*.yml`](../../azure-pipelines/) — CI/CD lanes
- [`docs/architecture/data-model-erd.md`](../architecture/data-model-erd.md) — schema layout
- Memory: `databricks-fabric-repos`, `databricks-cli`, `dbw-ipai-dev`

External:
- [Databricks Documentation index (MS Learn)](https://learn.microsoft.com/azure/databricks/)
- [Get started tutorials](https://learn.microsoft.com/azure/databricks/getting-started/)
- [Unity Catalog overview](https://learn.microsoft.com/azure/databricks/data-governance/unity-catalog/)
- [Asset Bundles](https://learn.microsoft.com/azure/databricks/dev-tools/bundles/)
- [Lakeflow SDP](https://learn.microsoft.com/azure/databricks/lakeflow/declarative-pipelines/)
- [Genie spaces](https://learn.microsoft.com/azure/databricks/genie/)

Upstream registered (`ssot/governance/upstream-adoption-register.yaml`):
- `databricks/cli` (consume_directly)
- `databricks/databricks-sdk-py` (consume_directly)
- `databricks/terraform-provider-databricks` (consume_directly, scoped)
- `databricks/mlops-stacks` (clone_as_reference)
- `databricks/notebook-best-practices` (clone_as_reference)
- `databricks/dbt-databricks` (clone_as_reference, deferred)
- `databricks/bundle-examples` (consume reference)
- `microsoft/unified-data-foundation` (consume_directly, TIME-SENSITIVE — Fabric trial expires ~2026-05-20)

---

## 10. Bottom line

```
Workspace status:    ✅ Live on Sponsored sub, no migration needed
Auth pattern:        ✅ MI + UC access connector (correct)
Bundle delivery:     ✅ Azure Pipelines path defined
Genie Space:         ⏸ pending (prerequisite for databricks-genie MCP)
Pulser integration:  ⏸ deferred until data-intel skill activates
Cost:                Premium tier (RBAC + UC required)
```

Microsoft Learn tutorials are useful onboarding for new team members. **Don't follow them as the IPAI build path** — our delivery is via Asset Bundles + Azure Pipelines + UC governance, not manual notebook ETL.

---

*Last updated: 2026-04-15*
