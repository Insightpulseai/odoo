# Databricks CLI — Benchmark Reference

> Source: Databricks CLI documentation (v0.205+)
> Status: Public Preview — interface may change
> Last updated: 2026-03-17

## Canonical Rule

Databricks CLI is the canonical CLI surface for all Databricks workspace, data, ML, and serving operations. It maps directly to the Databricks REST API. Public Preview status means: pin CLI version in CI, monitor for breaking changes, but treat as production-ready for interface-stable operations.

## CLI Version

- Minimum: v0.205+
- Install: `curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh`
- Verify: `databricks --version`
- Pin in CI: use specific version in GitHub Actions setup

## Authentication

| Method | When to Use |
|--------|-------------|
| Profile (`~/.databrickscfg`) | Multi-workspace local dev |
| Environment variables (`DATABRICKS_HOST`, `DATABRICKS_TOKEN`) | CI/CD, single workspace |
| Azure CLI auth (`databricks auth login --host <url>`) | Azure-backed workspaces |
| Service principal + OAuth | Automated/non-interactive operations |

## Command Groups

### Workspace & Files

| Command Group | Purpose | Key Operations |
|--------------|---------|----------------|
| `workspace` | Workspace artifacts | ls, import, export, mkdirs, delete |
| `files` | DBFS and UC Volumes | ls, cp, mkdir, rm |
| `repos` | Git repo links | list, create, update, delete |
| `secrets` | Secret management | list-scopes, list, create-scope, put-secret, delete-secret |

### Compute & Jobs

| Command Group | Purpose | Key Operations |
|--------------|---------|----------------|
| `clusters` | Cluster lifecycle | list, get, create, start, delete |
| `cluster-policies` | Cluster policies | list, get, create |
| `instance-pools` | Instance pools | list, get, create |
| `jobs` | Job definitions | list, get, create, run-now, delete |
| `runs` | Job runs | list, get, cancel |
| `pipelines` | DLT/SDP pipelines | list, get, create, start, stop, delete |

### ML & Serving

| Command Group | Purpose | Key Operations |
|--------------|---------|----------------|
| `experiments` | MLflow experiments | list, get, create, delete |
| `feature-engineering` | Feature tables | list-tables |
| `registered-models` | Unity Catalog models | list, get, create, delete |
| `model-versions` | Model versions | list, get |
| `serving-endpoints` | Model serving | list, get, create, update-config, delete, query |

### Identity & SQL

| Command Group | Purpose | Key Operations |
|--------------|---------|----------------|
| `auth` | Authentication | profiles, login, token, env |
| `users` | Workspace users (SCIM) | list, get, create, update, delete |
| `groups` | Workspace groups (SCIM) | list, get, create, delete |
| `service-principals` | Service principals (SCIM) | list, get, create, delete |
| `warehouses` | SQL warehouses | list, get, create, start, stop, delete |
| `queries` | Saved SQL queries | list, get |
| `dashboards` | SQL dashboards | list, get |

## REST API Mapping

Every Databricks CLI command maps to a REST API endpoint:
- `databricks clusters list` -> `GET /api/2.0/clusters/list`
- `databricks jobs run-now --job-id 123` -> `POST /api/2.1/jobs/run-now`
- `databricks serving-endpoints query --name ep` -> `POST /serving-endpoints/ep/invocations`

When CLI has limitations (e.g., complex JSON payloads), use `databricks api` or direct REST calls.

## Output Modes

- `--output json` — structured JSON (default for programmatic use)
- `--output text` — human-readable text
- Always use `--output json` in scripts and CI

## Common Patterns

### List and filter
```bash
databricks jobs list --output json | jq '.jobs[] | select(.settings.name | test("ipai"))'
```

### Create from JSON spec
```bash
databricks jobs create --json @job-spec.json --output json
```

### Poll for completion
```bash
while true; do
  STATE=$(databricks runs get --run-id $RUN_ID --output json | jq -r '.state.life_cycle_state')
  [ "$STATE" = "TERMINATED" ] && break
  sleep 15
done
```
