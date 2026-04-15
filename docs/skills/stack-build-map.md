# Stack Build Map — How to Assemble IPAI Using Registered Upstreams

> **Locked:** 2026-04-15
> **Authority:** this file (execution map from upstream adoption → building blocks → running system)
> **Upstream register:** [`ssot/governance/upstream-adoption-register.yaml`](../../ssot/governance/upstream-adoption-register.yaml)
> **BOM:** [`docs/architecture/revised-bom-target-state.md`](../architecture/revised-bom-target-state.md)
> **Capability source map:** [`docs/architecture/capability-source-map.md`](../architecture/capability-source-map.md)

---

## Purpose

Show **how to compose the registered upstream repos + installed skills + MCP tools into a running IPAI system**, across four concurrent tracks:

```
Track 1 — Building agents (Pulser, Tax Guru, Recon Agent, etc.)
Track 2 — Authoring IaC (Bicep / CLI / AVM)
Track 3 — Delivery automation (Azure Pipelines + databricks CLI + azd)
Track 4 — Graph + YAML generation (ERD / contracts / schema / dashboards)
```

All four tracks consume the same 100+ upstream-registered repos + the Azure Skills plugin.

---

## Track 1 — Building agents

### The canonical agent stack

```
┌──────────────────────────────────────────────────────────────┐
│  microsoft/agent-framework            ← SDK (Python + .NET)  │
│  • multi-agent orchestration                                 │
│  • pluggable memory (Cosmos/PG/Redis)                        │
│  • Foundry-optimized, cloud-agnostic                         │
├──────────────────────────────────────────────────────────────┤
│  Foundry resource (ipai-copilot-resource)                    │
│  • Foundry SDK endpoint (pending project creation)           │
│  • OpenAI-compat endpoint (live today)                       │
│  • Tools endpoint (Vision, Content Safety, Doc Intelligence) │
├──────────────────────────────────────────────────────────────┤
│  MCP ecosystem                                               │
│  • microsoft/azure-skills plugin (Azure + Foundry MCP)       │
│  • microsoft/mcp (catalog of official MCPs)                  │
│  • modelcontextprotocol/python-sdk (build ipai_* MCPs)       │
│  • modelcontextprotocol/servers (patterns only)              │
├──────────────────────────────────────────────────────────────┤
│  Pulser policy layer (our delta)                             │
│  • ipai_agent, ipai_ai_copilot, ipai_ai_platform             │
│  • Safe Outputs (3-tier defense per microsoftgbb/)           │
│  • Policy-gated action execution                             │
└──────────────────────────────────────────────────────────────┘
```

### Reject list (doctrine — no dual SDKs)

| Rejected | Why |
|---|---|
| `openai/openai-agents-python` | Collides with `microsoft/agent-framework` |
| `microsoft/semantic-kernel` | Agent Framework is canonical forward path |
| `microsoft/autogen` | Research-oriented; Pulser needs prod policy-gated |
| `microsoft/RulesEngine` | Odoo workflow + OCA record-rules already cover |

### Agent build step-by-step

1. **Pick the agent type** per `pulser_agent_classification.md`:
   - Transactional/operational copilot inside Odoo
   - Advisory (Tax Guru) with human-review gate
   - Multi-agent orchestration (Pulser Planner/Router)
2. **Scaffold** using `anthropics/skills` patterns (reference only) + `skill-creator` + `template/`
3. **Implement** with `microsoft/agent-framework` SDK (Python)
4. **Register tools** via MCP — from `microsoft/mcp` catalog or build custom via `python-sdk`
5. **Ground retrieval** via Foundry (if RAG needed) or `ipai_odoo_copilot` (Odoo context)
6. **Apply policy gates** per `feedback_no_custom_default` + Safe Outputs pattern from `microsoftgbb/agentic-platform-engineering`
7. **Deploy** via Azure Pipelines (not GHA) → ACA or Foundry hosted agent
8. **Monitor** via App Insights custom events tagged with `tenant_id`

### Reference samples to mine (patterns only, don't vendor)

- `Azure-Samples/contoso-chat` — eval-driven RAG lifecycle (strip its GHA workflow)
- `Azure-Samples/rag-postgres-openai-python` — RAG over PG Flex (matches our `pg-ipai-odoo`)
- `microsoft/promptflow` — eval/tracing patterns (Foundry eval is canonical runtime)
- `microsoft-foundry/foundry-samples` — Foundry-native agent patterns
- `microsoft-foundry/mcp-foundry` — Foundry MCP implementation

### Guardrails

| Rule | Enforcement |
|---|---|
| One agent SDK | `microsoft/agent-framework` only |
| No GHA runtime | Azure Pipelines deploys only (CLAUDE.md #24) |
| No OpenAI API key auth | Entra MI via `DefaultAzureCredential` |
| MCP server allowlist per agent | `.mcp.json` PR required for each new tool |
| Safe Outputs | 3-tier defense per `microsoftgbb/agentic-platform-engineering` |

---

## Track 2 — Authoring IaC (Bicep / CLI / AVM)

### The Bicep stack

```
┌──────────────────────────────────────────────────────────────┐
│  Azure/bicep            ← Compiler + language server         │
│  • az bicep CLI (pin version in devcontainer)                │
│  • VS Code Bicep extension                                   │
├──────────────────────────────────────────────────────────────┤
│  Azure/bicep-registry-modules  ← AVM modules (consume)       │
│  Azure/Azure-Verified-Modules  ← AVM program docs (reference)│
│  Azure/azure-resource-manager-schemas ← IntelliSense power   │
├──────────────────────────────────────────────────────────────┤
│  Azure/azure-quickstart-templates  ← Snippet discovery only  │
│  Azure/Enterprise-Scale       ← Naming/policy taxonomy ref   │
├──────────────────────────────────────────────────────────────┤
│  IPAI infra/                                                 │
│  • infra/azure/tags/main.bicep  (canonical tag module)       │
│  • infra/azure/modules/*/main.bicep (per-plane modules)      │
│  • infra/azure/environments/{nonprod,prod}/                  │
│  • infra/main.bicep + infra/main.bicepparam                  │
└──────────────────────────────────────────────────────────────┘
```

### Reject list

| Rejected | Why |
|---|---|
| `Azure/terraform-azurerm-caf-enterprise-scale` | Bicep is canonical Azure core IaC |
| `Azure/ResourceModules` | Superseded by AVM |

### Terraform is allowed ONLY for

- Databricks workspace config (via `databricks/terraform-provider-databricks`)
- Fabric mirroring (via `microsoft/unified-data-foundation` — time-sensitive: Fabric trial expires ~2026-05-20)

### Bicep build step-by-step

1. **Discover** what AVM module covers the need: search `Azure/bicep-registry-modules` or `mcp__azure__bicepschema`
2. **Compose** via `module <name> 'br/public:avm/res/<path>:<version>' = { ... }`
3. **Author** in VS Code with the Bicep extension (uses `azure-resource-manager-schemas`)
4. **Apply tags** via `infra/azure/tags/main.bicep` (17 mandatory tags per `tagging-standard.yaml` v3)
5. **Validate locally**: `az bicep build` + `az deployment group what-if`
6. **Deploy** via Azure Pipelines (not GHA, not azd-GHA-scaffolded)
7. **Reconcile** drift: `az deployment group what-if` on cadence

### Graphing IaC (what the user asked for)

**Bicep dependency graph (already exists):**
```bash
# Existing repo tooling
platform/tools/graphs/generate_schema_erd.sh  # DB ERD
scripts/generate_erd_graphviz.py              # referenced by the above
```

**New graph types to add (suggested for Track 4):**

| Graph | Source | Tool | Output |
|---|---|---|---|
| Bicep module dependency tree | `infra/azure/**/*.bicep` | `az bicep` + custom parser + Graphviz | `docs/graphs/bicep-module-deps.svg` |
| Resource topology | `az resource list` | `mcp__azure__group_resource_list` + Mermaid | `docs/graphs/resource-topology.svg` |
| Tag coverage heatmap | Resource Graph query | Azure Monitor workbook + Power BI | Tier 2 Power BI |
| Pipeline dependency graph | `azure-pipelines/**/*.yml` | YAML parser + Graphviz | `docs/graphs/pipeline-deps.svg` |
| MCP tool dependency | `.mcp.json` + Foundry connections | Python parser + Mermaid | `docs/graphs/mcp-deps.svg` |
| Agent + skill graph | `.claude/skills/` + `.mcp.json` | Plugin manifests parser | `docs/graphs/agent-stack.svg` |

---

## Track 3 — Delivery automation

### The pipeline stack

```
┌──────────────────────────────────────────────────────────────┐
│  Azure Pipelines (SOLE CI/CD authority per CLAUDE.md #24)    │
│  • azure-pipelines/*.yml                                     │
│  • azure-pipelines/templates/jobs/*.yml                      │
│  • Environments + service connections + approvals            │
├──────────────────────────────────────────────────────────────┤
│  Databricks delivery                                         │
│  • databricks/cli (pin in devcontainer)                      │
│  • databricks/databricks-sdk-py                              │
│  • databricks/terraform-provider-databricks (workspace only) │
│  • databricks/bundle-examples (pattern ref)                  │
├──────────────────────────────────────────────────────────────┤
│  Azure Dev CLI (azd)                                         │
│  • Azure/azure-dev (consume; STRIP its GHA default)          │
│  • Templates: web + Foundry + databricks patterns            │
├──────────────────────────────────────────────────────────────┤
│  REJECTED at this layer:                                     │
│  • GitHub Actions as delivery runtime                        │
│  • Vercel (deprecated 2026-04-07)                            │
│  • azure-pipelines-terraform (Bicep is canonical)            │
└──────────────────────────────────────────────────────────────┘
```

### Pipeline authoring flow

1. **Pick a job template** from `azure-pipelines/templates/jobs/` (e.g., `validate-bicep`, `deploy-containerapp`, `databricks-bundle-promote`)
2. **Compose** a stage-level pipeline referencing templates
3. **Pin** Bicep + Azure CLI + databricks CLI versions (devcontainer drives parity)
4. **Gate** on what-if + test results + approvals
5. **Deploy** to environment per service connection
6. **Strip GHA workflows** from any sample we adopt (per 4 reassessments in the register delta)

### YAML assembly (what the user asked for — "YAL etc.")

| YAML type | Source | Validation |
|---|---|---|
| `azure-pipelines/*.yml` | Handwritten / templates | `az pipelines runs show --validate` |
| `.mcp.json` | MCP catalog | JSON schema validation |
| `config/addons.manifest.yaml` | Module registry | Python loader validation |
| `ssot/azure/*.yaml` | BOM / tagging / naming | Python + JSON schema |
| `platform/contracts/odata/v1/*.yaml` | OData contracts | `tests/contracts/odata/*.py` |
| `ssot/tenants/*/seed/*.yaml` | Tenant seeds | Per-tenant loader |
| `databricks.yml` | Asset bundles | `databricks bundle validate` |
| `.devcontainer/devcontainer.json` | Dev env | VS Code dev-container CLI |

**PR gate:** every new YAML needs a validator or it won't merge.

---

## Track 4 — Graph + YAML generation

### What exists today

| Graph / contract | Path | Status |
|---|---|---|
| Odoo schema ERD (Mermaid) | `docs/architecture/data-model-erd.md` | ✅ written (32 models enumerated) |
| Odoo schema ERD (DOT/SVG, stale) | `archive/root-cleanup-20260224/scratch/out/graphs/schema/` | ⚠️ from older run |
| Bicep dependency graph | — | ❌ not yet |
| Resource topology graph | — | ❌ not yet |
| Agent/skill graph | — | ❌ not yet |
| OData contracts | `platform/contracts/odata/v1/` | ✅ 3 entity sets |
| SSOT YAMLs | `ssot/**/*.yaml` | ✅ partial |

### What to build (concrete, grounded by registered upstreams)

#### A. Bicep dependency graph

```python
# scripts/generate_bicep_deps.py
# Parses infra/azure/**/*.bicep + main.bicepparam
# Emits Graphviz DOT → SVG
# Uses az bicep build --outfile to resolve modules
# Azure/bicep (consume) drives parse
```

#### B. Resource topology graph

```python
# scripts/generate_resource_topology.py
# Uses Azure Resource Graph query via mcp__azure__group_resource_list
# Outputs Mermaid per plane (transaction/agent/data-intel/web/obs/shared)
# Consumes tags per tagging-standard.yaml v3 for coloring
```

#### C. Agent / MCP / skill graph

```python
# scripts/generate_agent_stack_graph.py
# Parses:
#   .mcp.json (MCP servers)
#   .claude/skills/*/SKILL.md (skill metadata)
#   ~/.claude/plugins/azure-skills/skills/ (upstream skills)
#   addons/ipai/ipai_ai_*/  (IPAI agent modules)
#   config/agent-manifest.yaml (if it exists; create if not)
# Emits Mermaid: Agent → Skills → MCP Servers → Tools
```

#### D. Odoo ORM full extraction (deferred — was the `extract` from earlier)

```python
# scripts/generate_odoo_dbml.py
# Requires live Odoo instance or Odoo shell
# Emits:
#   docs/data-model/ODOO_CANONICAL_SCHEMA.dbml
#   docs/data-model/ODOO_ERD.mmd
#   docs/data-model/ODOO_MODEL_INDEX.json
# Scoped to ipai_* + installed OCA + referenced CE (not all 600+ CE models)
```

---

## The integration — how agents consume IaC graphs

This is where the tracks connect:

```
Pulser agent (Track 1)
  → invokes mcp__azure__bicepschema (Azure MCP)
  → reads from infra/azure/**/*.bicep (Track 2)
  → checks pipeline status via mcp__azure-devops__pipelines_get_build_status (Track 3)
  → renders Bicep dep graph on demand via scripts/generate_bicep_deps.py (Track 4)
  → reports to user with links to docs/graphs/*.svg
```

All four tracks already have the upstream repos registered. **What's missing is the glue**:

1. `scripts/generate_bicep_deps.py` — 1-day build
2. `scripts/generate_resource_topology.py` — 1-day build (use Resource Graph queries)
3. `scripts/generate_agent_stack_graph.py` — 1-day build
4. `scripts/generate_odoo_dbml.py` — 2-day build (needs live Odoo shell)
5. Azure Pipelines job to run these on cadence — 0.5-day
6. Commit outputs to `docs/graphs/` + link from `docs/architecture/*` — 0.5-day

**Total: ~5 days** to fill the graph/automation coverage gap.

---

## Skills to build next (authoring guide)

Apply `anthropics/skills` authoring spec + `skill-creator` template. Create these under `.claude/skills/` (IPAI-owned):

| Skill | Purpose | Consumes upstream |
|---|---|---|
| `bicep-module-composer` | Author AVM-first Bicep modules | `Azure/bicep-registry-modules`, `Azure/bicep` |
| `azure-pipelines-author` | Compose pipelines from templates | `azure-pipelines/templates/jobs/` |
| `mcp-server-builder` | Build `ipai_*` MCP servers | `modelcontextprotocol/python-sdk`, `microsoft/mcp` |
| `agent-framework-scaffolder` | Scaffold Pulser agents | `microsoft/agent-framework` |
| `odoo-mcp-server` | Build the P0 odoo-mcp-server | Above + existing `ipai-odoo-mcp` patterns |
| `databricks-bundle-author` | Author Databricks Asset Bundles | `databricks/cli`, `databricks/bundle-examples` |
| `foundry-project-scaffolder` | Create + wire Foundry projects | `microsoft-foundry/foundry-samples` patterns |
| `ipai-graph-generator` | Run the 4 graph scripts on demand | Scripts in Track 4 |

None need to be built today. All 8 are **composition** work over registered upstreams.

---

## The full upstream → output pipeline

```
Register entry (ssot/governance/upstream-adoption-register.yaml)
        ↓ adopts
Upstream repo (microsoft/azure-skills, Azure/bicep, microsoft/agent-framework, etc.)
        ↓ provides
Tools / modules / SDKs / patterns
        ↓ composed by
IPAI skill (.claude/skills/) + IPAI module (addons/ipai/) + IPAI pipeline (azure-pipelines/)
        ↓ executes
Running system (agents, IaC, deploys, graphs, contracts)
        ↓ evidence to
docs/evidence/, docs/graphs/, pipeline runs, App Insights
```

Every layer is registered, every step is gated, every output has evidence.

---

## Anti-patterns to block at PR gate

| Anti-pattern | Block |
|---|---|
| New GHA workflow | `.github/workflows/` PR gate rejects |
| Terraform for Azure core | PR review + Bicep mandate |
| OpenAI API key in code | Secret scanner + `Azure/openai` reject |
| Agent Framework alternative SDK (SK, AutoGen, openai-agents) | Import scanner + dep review |
| MCP server without `.mcp.json` PR | `.mcp.json` required for new tools |
| Untagged resource | Azure Policy `require-canonical-tags` |
| Resource outside canonical 7 RGs | BOM validator |
| Hard-coded % complete on Epic/Feature | Boards rollup enforcement |

---

## Bottom line

```
Register 100+ upstreams        → already done (78 + 26 new delta 2026-04-15)
Build agents                    → compose Agent Framework + Foundry + MCP
Author IaC                      → compose Bicep + AVM + CLI + templates
Automate delivery               → Azure Pipelines + databricks CLI + azd (strip GHA)
Generate graphs + contracts     → 5-day glue work (scripts + Pipelines job)

Zero forks. Build the delta only. Doctrine holds.
```

---

## References

- [`ssot/governance/upstream-adoption-register.yaml`](../../ssot/governance/upstream-adoption-register.yaml) — canonical register (1064 lines post-delta)
- [`docs/architecture/capability-source-map.md`](../architecture/capability-source-map.md) — what we consume today
- [`docs/architecture/revised-bom-target-state.md`](../architecture/revised-bom-target-state.md) — BOM v2
- [`docs/architecture/data-model-erd.md`](../architecture/data-model-erd.md) — Odoo schema narrative
- [`docs/backlog/az400-devops-platform-learning-board-pack.md`](../backlog/az400-devops-platform-learning-board-pack.md) — 110 backlog items drive this
- Memory `feedback_upstream_adoption_doctrine`, `feedback_engineering_execution_doctrine`, `feedback_no_custom_default`

---

*Last updated: 2026-04-15*
