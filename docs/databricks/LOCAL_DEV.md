# Databricks Local Development — IPAI

Three viable patterns for local Databricks development against IPAI's data platform,
ordered from most to least capable. Pick based on whether a live workspace exists.

---

## Environment reality check (2026-04-13)

Run these **first** to confirm which levels apply to your current state:

```bash
# Expected Databricks workspace
az databricks workspace list --query "[?name=='dbw-ipai-dev']" -o json

# Expected lakehouse storage
az storage account list --query "[?starts_with(name, 'st') && contains(name, 'ipai')].{name:name, rg:resourceGroup}" -o table
```

**Current state (verified 2026-04-13):**
- `dbw-ipai-dev` Databricks workspace: **NOT PROVISIONED** in the active subscription
- Lakehouse storage: `stipaidev` in `rg-ipai-dev-odoo-runtime` (memory referenced `stipaidevlake` — stale)

Until `dbw-ipai-dev` is provisioned, only **Level 3** (fully local Spark) works without an Azure-side dependency. Levels 1 and 2 remain the target architecture.

If you need to provision the workspace now, the Bicep spine lives in
[../../infra/azure/modules/](../../infra/azure/modules/) — add a `databricks.bicep`
module binding to `rg-ipai-dev-odoo-runtime` (Premium SKU for Unity Catalog).

---

## Level 1 — Databricks Connect *(recommended once workspace exists)*

Runs Python **locally** but Spark executes on the remote cluster. Best developer
experience: local IDE + debugger + hot reload + real cluster.

```bash
# Install — version MUST match the workspace's DBR version
pip install databricks-connect==15.4.0

# Preferred auth: DefaultAzureCredential (no PATs, no tokens)
databricks configure --host https://adb-<workspace-id>.azuredatabricks.net

# Or — explicit Entra token (rotated per hour via az CLI)
export DATABRICKS_HOST=https://adb-<workspace-id>.azuredatabricks.net
export DATABRICKS_TOKEN=$(az account get-access-token \
  --resource 2ff814a6-3304-4ab8-85cb-cd0e6f879c1d \
  --query accessToken -o tsv)
```

Once configured, write code that runs as if it were on the cluster:

```python
# local_dev.py — Python runs locally, Spark runs on dbw-ipai-dev
from databricks.connect import DatabricksSession

spark = DatabricksSession.builder.getOrCreate()

# Read bronze layer from stipaidev (ADLS Gen2)
df = spark.read.format("delta").load(
    "abfss://bronze@stipaidev.dfs.core.windows.net/odoo/account_move/"
)
df.show(5)
```

**Costs / constraints:**
- Requires a running cluster. Use **job clusters** for batch work or **auto-terminating
  interactive clusters** (10-minute timeout) for dev.
- Min cluster cost: ~$0.40/hr for a 1-worker DS3_v2 dev cluster.
- Unity Catalog metadata is resolved remotely — you see `stipaidev` volumes from VS Code.

---

## Level 2 — VS Code Databricks extension

Same cluster execution as Level 1, but notebook-style workflow in the IDE. File
sync + notebook runs + inline output.

```bash
# Install the extension
code --install-extension databricks.databricks
```

Then: `Cmd+Shift+P` → **Databricks: Configure Workspace** → enter the workspace URL →
authenticate with Entra (DefaultAzureCredential flow — no PAT).

Capabilities:
- Sync local `.py` / `.ipynb` to DBFS automatically on save
- Run notebooks on the remote cluster, see output inline in VS Code
- Unity Catalog browser (schemas, tables, volumes) in the sidebar
- Job run logs stream to the VS Code output panel

This is effectively the Databricks web UI surfaced in your editor — no browser tab
needed for most dev loops. Pairs naturally with Level 1 for interactive Spark.

---

## Level 3 — Fully local Spark *(works TODAY, no Azure dependency)*

For unit-testing DLT pipeline transformation logic without provisioning a workspace.
The only option currently viable given the workspace gap above.

```bash
pip install pyspark==3.5.0 delta-spark
```

```python
# tests/test_dlt_logic.py — pure local, no cluster, no cost
from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip

builder = (
    SparkSession.builder
        .appName("ipai-local-test")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
)
spark = configure_spark_with_delta_pip(builder).getOrCreate()

# Test transformation logic with synthetic data
test_df = spark.createDataFrame(
    [
        {"account_id": 1, "amount": 1000.0, "company_id": 1},
        {"account_id": 2, "amount": 2500.0, "company_id": 1},
    ],
    schema="account_id INT, amount DOUBLE, company_id INT",
)

# Same transformation you'd write in a DLT pipeline
result = test_df.filter("amount > 1500").groupBy("company_id").sum("amount")
result.show()
```

**What this CAN'T test:**
- DLT decorators (`@dlt.table`, `@dlt.expect_or_fail`) — the `dlt` module only runs
  on Databricks Runtime.
- Unity Catalog permissions / table ACLs.
- Photon / Delta Live Tables autoscaling behavior.
- Streaming checkpoints against real cloud storage.

**What it IS good for:**
- Business-logic correctness of filters, joins, window functions, aggregates
- Schema validation (StructType match)
- Pure-function transformations from Bronze → Silver rules
- CI integration (runs in GitHub Actions / Azure DevOps without any cloud creds)

---

## Recommended IPAI workflow

```
  ┌────────────────────────┐
  │  Level 3 (now)         │   ← write + unit-test transformation
  │  PySpark + delta-spark │     logic on synthetic data, CI-friendly
  └──────────┬─────────────┘
             │  (when dbw-ipai-dev is provisioned)
             ▼
  ┌────────────────────────┐
  │  Level 1               │   ← validate against real bronze data
  │  Databricks Connect    │     from stipaidev; debug locally, Spark remote
  └──────────┬─────────────┘
             │  (when pipeline is stable)
             ▼
  ┌────────────────────────┐
  │  Level 2 + Asset Bundle│   ← deploy DLT pipeline definitions via CI
  │  databricks CLI deploy │     (data-intelligence/databricks/databricks.yml)
  └────────────────────────┘
```

### Why this order

`dbw-ipai-dev` is **read-only analytics** — it consumes from Odoo mirrored data into
`stipaidev` bronze, never writes back to Odoo. That makes Level 3 unusually safe:
there is no transactional side-effect to guard against when testing locally.

The existing bundle config at [data-intelligence/databricks/databricks.yml](../../data-intelligence/databricks/databricks.yml)
targets the workspace via `databricks bundle deploy`. Wire it to CI once the
workspace exists.

---

## Auth posture (when workspace lands)

Preferred order:
1. **Managed identity** — `id-ipai-dev` (or a new `id-ipai-dbw-dev`) with `Contributor` or `Databricks SQL Administrator` on the workspace
2. **Entra token via `az account get-access-token`** — rotates hourly, no stored credential
3. **Databricks PAT** — last resort, 30-day lifespan, stored in `kv-ipai-dev` as `databricks-workspace-pat`

NEVER:
- Commit PATs or workspace tokens to git
- Use workspace admin PATs for user workflows
- Bind cluster creation authority to end-user MIs (use service principals scoped
  narrowly)

Related: [docs/security/revoke-pat-runbook.md](../security/revoke-pat-runbook.md) for
the broader IPAI PAT policy (all global PATs revoked 2026-04-12).

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `databricks.connect.ClusterUnavailableException` | Cluster not running | Start via UI, or let Level 2 auto-start |
| `ProtocolException: version mismatch` | `databricks-connect` version ≠ DBR | Pin matching: `pip install databricks-connect==<DBR.version>` |
| `abfss://...` 404 on `stipaidev` | Wrong container or no RBAC | Verify container name + grant `Storage Blob Data Reader` to your MI |
| Local Spark OOM on laptop | `spark.driver.memory` default too low | Set `.config("spark.driver.memory", "4g")` in builder |
| `dlt` module not found locally | By design — DLT is Databricks-only | Stay in Level 3 for pure unit tests; run DLT in Level 1 |

---

*Last updated: 2026-04-13*
