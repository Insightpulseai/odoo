# Databricks CLI & Asset Bundles

> Platform skill: CLI installation, authentication, and DAB deploy workflow for Azure Databricks.
> Source: https://docs.databricks.com/aws/en/dev-tools/cli/tutorial

---

## Installation

```bash
# macOS (Homebrew)
brew tap databricks/tap && brew install databricks

# Windows (winget)
winget install Databricks.DatabricksCLI

# Verify (requires >= 0.205.0)
databricks -v
```

---

## Authentication (Azure Databricks)

```bash
# OAuth U2M login — creates a named profile
databricks auth login --host https://adb-7405610347978231.11.azuredatabricks.net

# Verify token
databricks auth token -p DEFAULT

# Environment variable auth (CI/CD)
export DATABRICKS_HOST=https://adb-7405610347978231.11.azuredatabricks.net
export DATABRICKS_TOKEN=dapi...
```

Profile is stored in `~/.databrickscfg`. For service principal auth (CI), use env vars or Azure AD token.

---

## Bundle Commands

### Init (scaffold new bundle)

```bash
databricks bundle init                        # Interactive template picker
databricks bundle init default-python         # Python template
databricks bundle init --output-dir ./my-proj # Custom output dir
```

### Validate (syntax + schema check)

```bash
databricks bundle validate                    # Default target
databricks bundle validate --target prod      # Specific target
```

Returns bundle identity summary and any schema warnings.

### Deploy (push to workspace)

```bash
databricks bundle deploy                      # Default target (dev)
databricks bundle deploy --target staging     # Named target
databricks bundle deploy --auto-approve       # Skip interactive prompts
databricks bundle deploy --fail-on-active-runs  # Fail if jobs running
databricks bundle deploy --force              # Override Git branch validation
```

Bundle identity = `bundle_name + target + workspace`. Deploy is idempotent.

### Run (execute job/pipeline)

```bash
# Run a job
databricks bundle run odoo_jdbc_extract --target dev
databricks bundle run odoo_jdbc_extract --no-wait  # Fire and forget

# Run a DLT pipeline
databricks bundle run finance_bir_pipeline --target dev
databricks bundle run finance_bir_pipeline --validate-only
databricks bundle run finance_bir_pipeline --full-refresh-all

# Pass job parameters
databricks bundle run my_job --params key1=value1,key2=value2
```

### Summary (inspect deployed resources)

```bash
databricks bundle summary                     # Show resources + deep links
databricks bundle summary --force-pull        # Refresh from workspace
```

### Destroy (tear down)

```bash
databricks bundle destroy                     # Interactive confirmation
databricks bundle destroy --auto-approve      # Skip confirmation
```

**Warning**: Permanently deletes jobs, pipelines, and artifacts. Cannot be undone.

---

## IPAI Lakehouse Deploy Workflow

### Workspace

- URL: `https://adb-7405610347978231.11.azuredatabricks.net`
- Tier: Premium, Southeast Asia, VNet-injected
- Bundle: `ipai-lakehouse` (`odoo/infra/databricks/databricks.yml`)

### Targets

| Target | Catalog | ADLS Path | Mode |
|--------|---------|-----------|------|
| `dev` | `dev_ipai` | `abfss://bronze@stipaidev.dfs.core.windows.net` | development |
| `staging` | `staging_ipai` | `abfss://bronze@stipaistaging.dfs.core.windows.net` | development |
| `prod` | `ipai_gold` | `abfss://bronze@stipaiprod.dfs.core.windows.net` | production |

### Deploy sequence

```bash
cd odoo/infra/databricks

# 1. Authenticate
databricks auth login --host https://adb-7405610347978231.11.azuredatabricks.net

# 2. Validate
databricks bundle validate --target dev

# 3. Deploy
databricks bundle deploy --target dev

# 4. Run connectivity test
databricks bundle run -- python3 notebooks/test/test_connectivity.py

# 5. Run JDBC extract (first load)
databricks bundle run odoo_jdbc_extract --target dev

# 6. Trigger DLT pipeline
databricks bundle run finance_bir_pipeline --target dev
```

### CI/CD (GitHub Actions)

```yaml
- name: Deploy lakehouse
  env:
    DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
    DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
  run: |
    cd odoo/infra/databricks
    databricks bundle validate --target ${{ inputs.target }}
    databricks bundle deploy --target ${{ inputs.target }} --auto-approve
```

---

## Key Flags Reference

| Flag | Command | Purpose |
|------|---------|---------|
| `--target` / `-t` | all | Select dev/staging/prod |
| `--auto-approve` | deploy, destroy | Skip interactive prompts |
| `--fail-on-active-runs` | deploy | Fail if jobs/pipelines running |
| `--force` | deploy | Override Git branch check |
| `--no-wait` | run | Don't wait for completion |
| `--full-refresh-all` | run (pipeline) | Reset all streaming tables |
| `--validate-only` | run (pipeline) | Validate without executing |
| `--restart` | run | Restart if already running |
| `--profile` / `-p` | all | Named auth profile |
| `--debug` | all | Enable debug logging |
| `--output json` / `-o json` | all | JSON output for scripting |

---

## Prerequisites

- Databricks CLI >= 0.205.0
- Azure Databricks workspace access
- Secret scope `odoo-pg` with keys: `jdbc_url`, `jdbc_user`, `jdbc_password`
- ADLS storage account with Bronze container
- Network connectivity from Databricks VNet to Odoo PG
