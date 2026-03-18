# Databricks ML & Serving Ops Skill

## Purpose

Manage Databricks ML experiments, feature engineering, model registry, and serving endpoints via the Databricks CLI (v0.205+).

## Owner

databricks-cli-operator

## Preconditions

- Databricks CLI v0.205+ installed
- Authentication configured with MLflow and serving permissions
- Unity Catalog enabled for model registry (recommended)

## Covered Operations

### Experiments (MLflow)

- `databricks experiments list` — list experiments
- `databricks experiments get --experiment-id <id>` — get experiment details
- `databricks experiments create --name <name>` — create experiment
- `databricks experiments delete --experiment-id <id>` — delete experiment (soft delete)

### Feature Engineering

- `databricks feature-engineering list-tables` — list feature tables (Unity Catalog)
- Feature table operations are primarily API/SDK-driven; CLI provides listing and metadata

### Model Registry (Unity Catalog)

- `databricks registered-models list` — list registered models
- `databricks registered-models get --full-name <catalog.schema.model>` — get model details
- `databricks registered-models create --name <name> --catalog-name <cat> --schema-name <schema>` — register model
- `databricks registered-models delete --full-name <catalog.schema.model>` — delete model (destructive)
- `databricks model-versions list --full-name <catalog.schema.model>` — list model versions
- `databricks model-versions get --full-name <catalog.schema.model> --version <v>` — get version details

### Serving Endpoints

- `databricks serving-endpoints list` — list serving endpoints
- `databricks serving-endpoints get --name <name>` — get endpoint details
- `databricks serving-endpoints create --json <spec>` — create serving endpoint
- `databricks serving-endpoints update-config --name <name> --json <spec>` — update endpoint config
- `databricks serving-endpoints delete --name <name>` — delete endpoint (destructive)
- `databricks serving-endpoints query --name <name> --json <input>` — query endpoint for inference

## Disallowed Operations

- Direct model training (use Jobs/notebooks, not CLI)
- Experiment run creation (use MLflow SDK in notebooks/jobs)
- Workspace artifact management (use databricks-workspace-ops)

## Output Contract

- All commands use `--output json`
- Experiments return `experiment_id`, `name`, `lifecycle_stage`
- Models return `full_name`, `creation_timestamp`, `comment`
- Serving endpoints return `name`, `state.ready`, `config.served_models`

## Verification

- After model register: `registered-models get` returns model metadata
- After endpoint create: poll `serving-endpoints get` until `state.ready` is `READY`
- After endpoint query: response contains `predictions` array
