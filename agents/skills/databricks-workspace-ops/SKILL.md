# Databricks Workspace Ops Skill

## Purpose

Manage Databricks workspace artifacts via the Databricks CLI (v0.205+).
Covers workspace ls/import/export, repos, secrets, files, and notebooks.

## Owner

databricks-cli-operator

## Preconditions

- Databricks CLI v0.205+ installed (`databricks --version`)
- Authentication configured via profile or environment variables
- `DATABRICKS_HOST` and `DATABRICKS_TOKEN` (or profile) set
- Target workspace accessible

## Covered Operations

### Workspace

- `databricks workspace ls <path>` — list workspace objects
- `databricks workspace import <local-path> <remote-path>` — import notebook/file
- `databricks workspace export <remote-path> <local-path>` — export notebook/file
- `databricks workspace mkdirs <path>` — create workspace directory
- `databricks workspace delete <path>` — delete workspace object (destructive)

### Files (DBFS and Unity Catalog Volumes)

- `databricks fs ls <path>` — list files
- `databricks fs cp <src> <dst>` — copy files (local to remote, remote to local)
- `databricks fs mkdir <path>` — create directory
- `databricks fs rm <path>` — remove file (destructive)

### Repos

- `databricks repos list` — list Git repos
- `databricks repos create --url <url> --provider <provider>` — create repo link
- `databricks repos update --repo-id <id> --branch <branch>` — update repo branch
- `databricks repos delete --repo-id <id>` — delete repo link (destructive)

### Secrets

- `databricks secrets list-scopes` — list secret scopes
- `databricks secrets list --scope <scope>` — list secrets in scope (metadata only)
- `databricks secrets create-scope --scope <scope>` — create secret scope
- `databricks secrets put-secret --scope <scope> --key <key>` — store secret (stdin)
- `databricks secrets delete-secret --scope <scope> --key <key>` — delete secret (destructive)

## Disallowed Operations

- Interactive notebook execution (requires Databricks UI or Jobs API)
- Direct SQL execution (use databricks-identity-sql-ops for SQL warehouses)
- Cluster management (use databricks-compute-jobs-ops)

## Output Contract

- All commands use `--output json` for programmatic consumption
- Workspace listing returns array of objects with `object_type`, `path`, `language`
- File operations return success/failure status
- Secret operations never expose secret values in output

## Verification

- After import: `databricks workspace ls <path>` confirms object exists
- After file copy: `databricks fs ls <path>` confirms file exists
- After repo create: `databricks repos list` confirms repo appears
