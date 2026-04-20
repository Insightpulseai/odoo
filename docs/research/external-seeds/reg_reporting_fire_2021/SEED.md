# SEED · Databricks `reg_reporting` (FIRE) · 2021-09-28

> **Status:** bootstrap seed · **NOT** a baseline. Extract-and-modernize per CLAUDE.md Rule 24.
> **Layer:** L4/L5 hybrid reference (Databricks FSI Solution Accelerators, archived).
> **Author (upstream):** antoine.amend@databricks.com · Apache v2 (FIRE) + Databricks DB-License (notebooks).
> **Vintage:** DBR 9.0 · September 2021 · 4.5 years old as of extraction (2026-04-20).
> **Provenance:** user-supplied `.dbc` archive in `~/Downloads/reg_reporting.dbc` (38 KB). Original preserved as `_original.dbc`.

## What is in the archive

Four Databricks notebooks (NotebookV1 JSON; converted to plain `.py` with `# COMMAND ----------` cell separators):

| Notebook | Cells | What it does |
|---|---|---|
| `00_fire_context.py` | 2 | Narrative + license card. References Suade Labs FIRE regulatory data model (Apache v2). |
| `01_fire_orchestration.py` | 20 | Delta Live Tables pipeline: bronze (auto-loader) → silver (`@dlt.expect_all_or_drop`) → quarantine (failed FIRE expectations). Schema and constraints loaded from `fire.spark.FireModel(entity).schema/constraints`. |
| `02_fire_metrics.py` | 23 | Reads `pipeline_dir/system/events`, extracts `flow_progress.data_quality.expectations` per dataset/expectation, writes operational data store (ODS) via structured streaming + `trigger(once=True)`, then publishes via Delta Sharing `cloneAtVersion`. |
| `config/fire_config.py` | 2 | Trivial config dict (`fire_entity = "collateral"`, FileStore paths). |

Demo entity: **collateral**. Pipeline parameters expected at runtime: `fire_entity`, `landing_zone`, `invalid_format_path`, `file_format`, `max_files`.

## Why this is a seed, not a baseline

| Signal | Concern |
|---|---|
| DBR 9.0 (Sept 2021) | Predates Unity Catalog as default, predates current DLT (now "Lakeflow Declarative Pipelines"), predates `dlt.create_table` API rename. |
| `%pip install git+https://github.com/aamend/fire.git` | Non-pinned git install of an individual's fork of FIRE. Fork is unmaintained vs `SuadeLabs/fire` upstream. |
| `/FileStore/<email>/...` paths | DBFS FileStore is deprecated guidance; Unity Catalog volumes / external locations are the modern path. |
| Single sample entity (`collateral`) | No multi-entity orchestration, no parameter sweep, no CI. |
| No tests, no DAB scaffold, no Unity Catalog grants | Not production-ready as-is. |

Per CLAUDE.md Rule 24 (Adopt Reflex) the right disposition is **extract-and-modernize**, never **adopt-as-is**.

## What is reusable (the actual signal)

The pattern is crisp and maps directly onto IPAI's **BIR-compliance** lane (Pulser specialist `bir-compliance` per CLAUDE.md Rule 27):

| FIRE notebook concept | IPAI BIR-compliance equivalent |
|---|---|
| `fire_entity = "collateral"` | `bir_form = "2550Q" \| "1601C" \| "0619E" \| "2307" \| ...` |
| `fire.spark.FireModel(entity).schema` | `ipai_bir.schema.BirForm(form_code).schema` (to be authored under `data-intelligence/src/bir/`) |
| `fire_model.constraints` (JSON-derived SQL expectations) | BIR field expectations: TIN regex, RDO valid, withholding-tax range, period-end alignment, totals-tie checks |
| Bronze → Silver → Quarantine via `@dlt.expect_all_or_drop` | Same medallion shape; quarantine drives Pulser's "RISKS / OPEN ITEMS" 6-section deliverable section per Rule 27 |
| ODS metrics from `pipeline_dir/system/events` | AGT audit-evidence sink (Rule 30); per-form, per-expectation pass/fail counts feed the AppSource compliance pack |
| Delta Sharing `cloneAtVersion` to regulator | Pre-eFPS BIR submission package; or partner-shared snapshot for CPA review |

## Disposition

```yaml
# Registry stub — to be added under ssot/microsoft-artifact-registry/seeds/external/
id: external/databricks-fsi-reg-reporting-fire-2021
upstream:
  source: databrickslabs/fsi-solution-accelerators
  path: reg_reporting
  vintage: 2021-09-28
  dbr: "9.0"
  authors: ["antoine.amend@databricks.com"]
  license: Apache-2.0 (FIRE) + Databricks DB-License (notebooks)
classification:
  layer: L4_L5_hybrid_reference
  status: archived
  decision: bootstrap_seed
  baseline_candidate: false
  pattern_candidate: true
  retarget_purpose: high   # for regulatory-reporting / BIR-compliance vertical
  modernization_required: high
target_lane: data-intelligence/regulatory-reporting    # NOT agent-platform/Pulser core
human_equivalent:               # per Rule 29 triad
  builder_roles: ["DP-700 Fabric Data Engineer Associate", "data-intelligence engineer"]
  operator_roles: ["AB-730 AI Business Professional", "BIR-compliance specialist (Pulser)"]
  judge_roles:    ["AZ-305 Solutions Architect", "CPA reviewer", "AGT policy gate"]
modernization_required:
  - replace_dbfs_filestore_with_unity_catalog_volumes
  - pin_or_replace_aamend_fire_fork_with_suadelabs_fire_or_inhouse_birmodel
  - rename_dlt_create_table_to_current_lakeflow_api
  - add_databricks_asset_bundle_scaffold (`databricks/bundles/bir-compliance/`)
  - add_unity_catalog_grants_per_tenant
  - add_AGT_policy_hooks_at_quarantine_and_ods_publish
  - add_pytest_for_constraint_authoring
  - retarget_demo_entity_from_collateral_to_BIR_2550Q
```

## Where this should land (final, after submodule lands its in-flight branch)

```
data-intelligence/seeds/external/reg_reporting_fire_2021/   # this directory, copied across submodule boundary
data-intelligence/databricks/bundles/bir-compliance/        # NEW — modernized DAB derived from these notebooks
data-intelligence/src/bir/schema.py                         # NEW — IPAI BirModel (replaces FireModel as load surface)
data-intelligence/src/bir/expectations/                     # NEW — per-form expectation SQL (2550Q, 1601C, …)
ssot/microsoft-artifact-registry/seeds/external/databricks-fsi-reg-reporting-fire-2021.yaml
ssot/governance/agt-policies/data-intelligence/quarantine-publish.yaml   # AGT gate on quarantine-rate spikes
```

## Why this is staged here instead of in the `data-intelligence` submodule

The `data-intelligence` submodule is currently on branch `feat/dab-template` with active in-progress work (multiple `D ` and `M ` files). Staging here in the parent repo's `docs/research/external-seeds/` keeps the seed visible and discoverable without colliding with that branch. Promote into the submodule once `feat/dab-template` lands.

## Boundaries — what this seed does NOT do

- Does **not** belong in `agent-platform/` or `agents/` — it is a **data pipeline pattern**, not an agent.
- Does **not** replace any Microsoft canonical (per Rule 25 the Microsoft regulatory-reporting answer would be Fabric + Purview Unified Catalog + DLT-on-Databricks; this seed slots into the DLT-on-Databricks half).
- Does **not** justify a long-term dependency on `aamend/fire`. Pin a vendored copy or rebuild the constraint-loader against `SuadeLabs/fire` upstream.

## License notes

- FIRE (the data model and `fire` library): Apache 2.0 (Suade Labs). Reusable.
- The notebooks themselves: Databricks DB-License (https://databricks.com/db-license-source). Reusable for derivative work; preserve attribution to Antoine Amend in modernized derivatives.
