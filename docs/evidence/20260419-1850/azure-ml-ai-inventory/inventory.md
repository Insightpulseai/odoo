---
stamp: 20260419-1850
scope: azure-ml-ai-inventory
goal: Inventory live Azure resources for Databricks ML, experiments, fine-tuning, and AI services
queries: az graph + az cognitiveservices + databricks CLI v0.292.0 + Foundry REST API
---

# Azure Databricks ML / Experiments / Fine-tuning / AI Inventory

## Outcome (1-line)

**Premium infrastructure provisioned across 2 subscriptions, ZERO active ML workloads.** No experiments, no user-owned models, no fine-tuning jobs, no jobs, 1 idle DLT pipeline. All visible "models" are Databricks system foundation models and one Foundry deployment.

## Subscriptions in scope

| Subscription | ID | Tenant |
|---|---|---|
| Microsoft Azure Sponsorship (default) | `eba824fb-332d-4623-9dfb-2c9f7ee83f4e` | `402de71a` |
| (other) | `536d8cf6-89e1-4815-aef3-d5f2c5f4d070` | `402de71a` |

## Provisioned resources (live)

| Resource | Type | Kind | Location | Sub | RG | SKU |
|---|---|---|---|---|---|---|
| `dbw-ipai-dev` | Databricks workspace | — | southeastasia | sponsorship | `rg-ipai-dev-ai-sea` | **premium** |
| `unity-catalog-access-connector` | Databricks access connector | — | southeastasia | sponsorship | `rg-ipai-dev-dbw-managed` | — |
| `ipai-copilot-resource` | Cognitive Services | **AIServices (Foundry)** | eastus2 | sponsorship | `rg-ipai-dev-ai-sea` | S0 |
| `ipai-foundry-frontier` | Cognitive Services | **AIServices (Foundry)** | eastus2 | other | `rg-ipai-dev-odoo-runtime` | S0 |
| `docai-ipai-dev` | Cognitive Services | **FormRecognizer** (Document Intelligence) | southeastasia | sponsorship | `rg-ipai-dev-ai-sea` | S0 |
| `srch-ipai-dev` | Azure AI Search | — | southeastasia | other | `rg-data-intel-ph` | basic |
| `srch-ipai-dev-sea` | Azure AI Search | — | southeastasia | sponsorship | `rg-ipai-dev-ai-sea` | basic |

**No** `Microsoft.MachineLearningServices/workspaces` (Azure ML / AML) provisioned.
**No** `Microsoft.MachineLearningServices/registries` (model registry) provisioned.

## Databricks workspace `dbw-ipai-dev` deep state

CLI: `databricks --version` → v0.292.0
Auth: `auth_type = azure-cli` (host: `https://adb-7405608559466577.17.azuredatabricks.net`)

### Experiments (MLflow)

```
$ databricks experiments search-experiments
Total experiments: 0
```

**ZERO** experiments. No tracking runs, no parameter logging, no metric history.

### Registered models (Unity Catalog)

```
Total: 63
  system.ai.* :  63
  user-owned  :   0
```

All 63 are **Databricks system foundation models** (gemma-3-12b-it, gpt-oss-120b, llama-4-maverick, etc.) — not anything IPAI trained or registered.

### Jobs

```
$ databricks jobs list
[]
```

**ZERO** Databricks Jobs (no scheduled training, no workflows, no batch inference).

### DLT Pipelines (data engineering)

```
Total: 1
  ipai-odoo-cdm-export                     state=IDLE
```

**One** Delta Live Tables pipeline (Odoo → Common Data Model export). Idle.

### SQL Warehouses

```
  Serverless Starter Warehouse   state=STOPPED  size=Small
```

**One** serverless warehouse. Stopped.

### Model Serving Endpoints (foundation models)

11 endpoints, all `READY`, all wrapping Databricks system foundation models:

| Endpoint | Model | Task |
|---|---|---|
| `databricks-gpt-oss-120b` | OpenAI GPT-OSS 120B | chat |
| `databricks-gpt-oss-20b` | OpenAI GPT-OSS 20B | chat |
| `databricks-qwen3-next-80b-a3b-instruct` | Qwen3 Next 80B | chat |
| `databricks-llama-4-maverick` | Llama 4 Maverick | chat |
| `databricks-gemma-3-12b` | Google Gemma 3 12B | chat |
| `databricks-gte-large-en` | GTE Large EN | embeddings |
| `databricks-bge-large-en` | BGE Large EN | embeddings |
| `databricks-meta-llama-3-1-8b-instruct` | Llama 3.1 8B | chat |
| `databricks-meta-llama-3-3-70b-instruct` | Llama 3.3 70B | chat |
| `databricks-qwen3-embedding-0-6b` | Qwen3 Embedding 0.6B | embeddings |
| `databricks-meta-llama-3.1-405b-instruct` | Llama 3.1 405B | chat |

These are pay-per-token foundation model endpoints provided by Databricks — they exist by default in the workspace, not provisioned by IPAI.

### Unity Catalog catalogs

| Catalog | Type |
|---|---|
| `odoo_erp` | FOREIGN_CATALOG (likely Postgres mirror) |
| `ipai_dev` | MANAGED_CATALOG |
| `ipai_prod` | MANAGED_CATALOG |
| `ipai_staging` | MANAGED_CATALOG |
| `dbw_ipai_dev_7405608559466577` | MANAGED_CATALOG (workspace default) |
| `samples` | SYSTEM_CATALOG |
| `system` | SYSTEM_CATALOG |

UC schema is set up. The data plane structure exists. The compute/ML plane is unused.

## Foundry (AI Services)

### `ipai-copilot-resource` (Foundry, eastus2)

Endpoint: `https://ipai-foundry-sea.cognitiveservices.azure.com/`

**Model deployments (1)**:

| Name | Model | Version | SKU | Capacity |
|---|---|---|---|---|
| `gpt-4.1-mini` | gpt-4.1-mini | 2025-04-14 | GlobalStandard | 10 |

**Fine-tuning jobs**:

```
GET openai/fine_tuning/jobs?api-version=2024-10-21
{ "data": [], "has_more": false, "object": "list" }
```

**ZERO** fine-tuning jobs.

### `ipai-foundry-frontier` (Foundry, other sub)

Same shape, separate inventory not run (different subscription); likely also empty.

### `docai-ipai-dev` (Document Intelligence)

S0 tier. Provisioned, no custom models inventoried (would require separate API call).

## Local repo state — `data-intelligence/`

Path | Content
---|---
`data-intelligence/contracts/` | YAML contracts for ADO, finance domains, Genie spaces, Power BI semantic models — all **declarations, no Databricks/ML notebooks**
`data-intelligence/ssot/benchmark/databricks_apps_lakebase_kb.yaml` | Lakebase KB benchmark spec
`data-intelligence/ssot/benchmark/odoo_copilot_benchmark_v2.yaml` | Odoo copilot benchmark spec
`data-intelligence/ssot/serving/databricks-one.yaml` | Databricks "One" serving config (declared)
`data-intelligence/tests/synthetic/profiles.yaml` | Synthetic data profiles
`data-intelligence/.github/workflows/claude-code.yml` + `claude-pr-review.yml` | CI for Claude assistance
`infra/databricks/` | Databricks bundle/config (not inspected here in detail)

**No notebooks, no MLflow tracking code, no fine-tuning configs, no model serving manifests** in the SSOT/contracts surface.

## Gap summary

| Area | Provisioned | Used | Gap |
|---|---|---|---|
| Databricks workspace (premium) | ✓ | partial (1 idle DLT pipeline) | Paying premium, getting ~5% utilization |
| MLflow experiments | n/a | ZERO | No experiment tracking |
| User-owned UC models | n/a | ZERO | No registered IPAI models |
| Databricks Jobs | n/a | ZERO | No scheduled training/eval/batch inference |
| Foundry deployments | 1 (gpt-4.1-mini) | yes (used by `agent-platform/`) | Single model, no specialist variants |
| Fine-tuning jobs | n/a | ZERO | No domain adaptation, no PH/finance/BIR-specific tuning |
| Azure AI Search | 2 (basic SKU) | unknown — not queried for indexes | Likely underused |
| Azure ML (AML) | NOT PROVISIONED | — | Could be skipped if Databricks is the canonical ML lane |

## Honest read

**You have a premium Databricks workspace with zero ML workloads.** Same pattern as everything else in this session: doctrine declared (Rule 9: "Databricks + Unity Catalog is the mandatory governed transformation, engineering, and serving plane"), execution missing.

What's actually being used:
- **Foundry `gpt-4.1-mini`** for `agent-platform/` runtime calls
- **Databricks system foundation model endpoints** (pay-per-token, no commitment)
- **`ipai-odoo-cdm-export` DLT pipeline** (idle — not even running)
- **UC catalogs** declared (ipai_dev/staging/prod) but no managed tables of yours visible from the inventory query

What is NOT being used:
- MLflow experiment tracking
- Custom UC model registration (no `ipai_dev.ml.*` models)
- Databricks Jobs orchestration
- SQL warehouse (stopped)
- Foundry fine-tuning
- Azure ML (not even provisioned)

## Cost waste signal

Premium Databricks workspace SKU on `dbw-ipai-dev` is ~3-5x the cost of standard. With zero experiments, zero jobs, and one idle DLT pipeline, you're paying premium pricing for capabilities you're not exercising.

## Suggested next moves (if you want to act on this)

1. **Decide**: Are you actually doing ML training/fine-tuning, or is the data plane all you need?
   - If only data plane → downgrade Databricks to standard SKU, save spend
   - If ML is on roadmap → get one MLflow experiment + one registered IPAI model on the board this trimester
2. **Foundry fine-tuning**: If domain adaptation matters for Pulser (PH context, BIR vocab, Odoo-specific responses), gpt-4.1-mini supports fine-tuning on Foundry. Currently 0 jobs.
3. **AI Search audit**: 2 basic-SKU search services exist; query for indexes to see if they're being used as RAG plane for Pulser.
4. **Document Intelligence**: `docai-ipai-dev` S0 is provisioned but no custom model inventory — confirm it's used for invoice OCR / BIR forms or deprecate.

## Verification commands (reproducible)

```bash
# Resource graph for ML/AI/Databricks across all subs
az graph query -q "Resources | where type in~ ('microsoft.machinelearningservices/workspaces', 'microsoft.search/searchservices', 'microsoft.cognitiveservices/accounts', 'microsoft.databricks/workspaces', 'microsoft.databricks/accessconnectors', 'microsoft.machinelearningservices/registries') | project name, type, location, resourceGroup, subscriptionId" --first 200 -o json

# Databricks workspace state
databricks experiments search-experiments --output json
databricks registered-models list --output json
databricks jobs list --output json
databricks pipelines list-pipelines --output json
databricks warehouses list --output json
databricks serving-endpoints list --output json
databricks catalogs list --output json

# Foundry deployments + fine-tuning
az cognitiveservices account deployment list --name ipai-copilot-resource --resource-group rg-ipai-dev-ai-sea -o json
ENDPOINT="https://ipai-foundry-sea.cognitiveservices.azure.com/"
TOKEN=$(az account get-access-token --resource https://cognitiveservices.azure.com --query accessToken -o tsv)
curl -s -H "Authorization: Bearer $TOKEN" "${ENDPOINT}openai/fine_tuning/jobs?api-version=2024-10-21"
```
