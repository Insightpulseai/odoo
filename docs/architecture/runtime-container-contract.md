# Runtime Container Contract

> Source roots, addon roots, logs, data directories, addons_path, container
> image layers, and Azure Container Apps specifics for the Odoo runtime.
> Modeled after the Odoo.sh container filesystem contract.

---

## Container Filesystem Layout

### Azure Container Apps (Production)

```
/opt/odoo/                          # Odoo CE 18 installation (read-only layer)
  odoo-bin                          # Odoo server binary
  odoo/                             # Odoo Python package source
  addons/                           # Core addons (base, account, sale, ...)
  setup.py

/workspaces/odoo/                   # Workspace root (repo checkout)
  addons/
    ipai/                           # Custom IPAI modules
      ipai_odoo_copilot/
      ipai_copilot_actions/
      ipai_enterprise_bridge/
      ipai_auth_oidc/
      ipai_slack_connector/
      ...                           # 69 modules total
    oca/                            # OCA community modules (hydrated at build)
      web/
      server-ux/
      account-financial-tools/
      sale-workflow/
      ...
    local/                          # Minimal local overrides (rare, not in default path)

/etc/odoo/
  odoo.conf                         # Server configuration (injected at build)

/var/lib/odoo/                      # Odoo data directory (persistent volume)
  filestore/                        # Attachment filestore (per-database subdirs)
  sessions/                         # Server-side session files

/var/log/odoo/                      # Log directory
  odoo-server.log                   # Main server log (also mirrored to stdout)
```

### Local Development (Native Mac)

```
vendor/odoo/                        # Canonical upstream Odoo 18 root
  odoo-bin
  odoo/
  addons/                           # Core addons

addons/
  ipai/                             # Custom IPAI modules
  oca/                              # OCA community modules

config/dev/odoo.conf                # Dev config (Docker-oriented, not used for native)

/tmp/odoo-data/                     # Local dev data directory (ephemeral)
  filestore/
  sessions/
```

### Devcontainer (Docker)

Same filesystem layout as Azure Container Apps. The devcontainer mounts the
repo at `/workspaces/odoo/`. The Odoo CE installation lives at `/opt/odoo/`
(read-only). The database hostname is `db` (Docker service name).

---

## Source Roots

| Root | Contents | Mutability |
|------|----------|------------|
| `vendor/odoo/` (local) / `/opt/odoo/` (container) | Upstream Odoo CE 18 source | Read-only -- never modify |
| `addons/ipai/` | Custom IPAI bridge and extension modules | Read-write (developer-owned) |
| `addons/oca/` | OCA community modules | Read-only (managed via submodules or build-time hydration) |
| `addons/local/` | Minimal local overrides | Read-write (rarely used) |

### Rules

1. Never modify files under `vendor/odoo/` or `/opt/odoo/` -- these are the upstream mirror
2. Custom modules go in `addons/ipai/` with the naming convention `ipai_<domain>_<feature>`
3. OCA modules are managed via `.gitmodules` (local) or Docker build-time clone (container)
4. `addons/local/` is not in the default `addons_path` -- add explicitly only when needed

---

## Addon Roots and Effective addons_path

The `addons_path` is the ordered list of directories Odoo searches for modules.
Order determines precedence -- first match wins for module name collisions.

### Production addons_path

```ini
addons_path = /opt/odoo/addons,/workspaces/odoo/addons/oca,/workspaces/odoo/addons/ipai
```

| Position | Path | Contains | Precedence |
|----------|------|----------|------------|
| 1 | `/opt/odoo/addons` | Odoo CE core addons (base, account, sale, etc.) | Highest -- upstream takes precedence for base models |
| 2 | `/workspaces/odoo/addons/oca` | OCA community modules (flattened or repo-nested) | Middle -- extends core via `_inherit` |
| 3 | `/workspaces/odoo/addons/ipai` | Custom IPAI bridge/extension modules | Lowest -- thin bridges that extend OCA/core |

### Local dev addons_path

```ini
addons_path = vendor/odoo/addons,addons/oca,addons/ipai
```

### OCA Module Flattening

OCA modules are organized in git repositories by domain (e.g., `web/`,
`account-financial-tools/`, `sale-workflow/`). Inside the container, these are
either:

- **Repo-nested**: `/workspaces/odoo/addons/oca/web/web_responsive/` -- Odoo scans subdirectories
- **Flattened**: `/workspaces/odoo/addons/oca/web_responsive/` -- each module at top level

The production image uses repo-nested layout. The `addons_path` entry
`/workspaces/odoo/addons/oca` combined with Odoo's recursive directory scanning
discovers all nested modules.

### Path Rules

1. Core addons always come first (Odoo upstream takes precedence for base models)
2. OCA addons come second (community extensions use `_inherit`)
3. IPAI addons come last (custom bridges use `_inherit` to extend, never replace)
4. Never add duplicate paths or overlapping module names across positions
5. `addons/local/` is not in the default path -- add explicitly only when needed

---

## Configuration Path

### Container (`/etc/odoo/odoo.conf`)

```ini
[options]
addons_path = /opt/odoo/addons,/workspaces/odoo/addons/oca,/workspaces/odoo/addons/ipai
data_dir = /var/lib/odoo
db_host = <injected from env: ODOO_DB_HOST>
db_port = 5432
db_user = <injected from env: ODOO_DB_USER>
db_password = <injected from env: ODOO_DB_PASSWORD>
db_name = odoo
list_db = False
workers = 4
max_cron_threads = 1
proxy_mode = True
without_demo = all
log_level = info
log_handler = :INFO,ipai:DEBUG,werkzeug:WARNING
logfile = /var/log/odoo/odoo-server.log
server_wide_modules = base,web
```

Database credentials are injected at runtime via environment variables sourced
from Azure Key Vault (managed identity access). The config file itself contains
no secrets.

### Local dev (`config/dev/odoo.conf`)

Used for Docker-based local development. For native Mac development, parameters
are passed as CLI arguments to `odoo-bin`:

```bash
~/.pyenv/versions/odoo-18-dev/bin/python vendor/odoo/odoo-bin \
  --database=odoo_dev \
  --db_host=localhost --db_port=5432 --db_user=tbwa --db_password=False \
  --http-port=8069 \
  --addons-path=vendor/odoo/addons,addons/ipai \
  --dev=xml,reload,qweb \
  --data-dir=/tmp/odoo-data
```

---

## Log Path and Log Format Contract

### Log Targets

| Environment | Primary target | Secondary target | Level |
|-------------|---------------|-----------------|-------|
| Production (ACA) | stdout (captured by ACA log stream) | `/var/log/odoo/odoo-server.log` | `info` |
| Local dev (native) | stdout | None | `debug` |
| Devcontainer | stdout | `/var/log/odoo/odoo-server.log` | `info` |

### Log Format

Odoo uses Python's `logging` module. The default format is:

```
YYYY-MM-DD HH:MM:SS,mmm PID LEVEL DB_NAME MODULE: message
```

Example:

```
2026-03-28 08:15:42,103 1 INFO odoo account.move: Posted journal entry INV/2026/0042
2026-03-28 08:15:42,205 1 INFO odoo ipai.copilot: Tool executed: action_post on account.move[42] by user 7
```

### Copilot Logger Namespace

All copilot-specific logging uses the `ipai.copilot` logger namespace:

```python
import logging
_logger = logging.getLogger('ipai.copilot')
```

Sub-namespaces:

| Namespace | Purpose |
|-----------|---------|
| `ipai.copilot` | General copilot operations |
| `ipai.copilot.tool` | Tool invocation and results |
| `ipai.copilot.auth` | Authentication and authorization decisions |
| `ipai.copilot.gateway` | Gateway routing and adapter operations |
| `ipai.copilot.audit` | Audit trail entries |

### Azure Container Apps Log Integration

ACA captures stdout/stderr from the container and routes it to Azure Monitor
(Log Analytics workspace). Structured queries:

```kusto
ContainerAppConsoleLogs_CL
| where ContainerAppName_s == "ipai-odoo-dev-web"
| where Log_s contains "ipai.copilot"
| order by TimeGenerated desc
```

---

## Data Path

### Filestore

| Environment | Path | Persistence |
|-------------|------|-------------|
| Production | `/var/lib/odoo/filestore/odoo/` | Azure Files (persistent, backed up) |
| Devcontainer | `/var/lib/odoo/filestore/odoo_dev/` | Docker volume |
| Local dev | `/tmp/odoo-data/filestore/odoo_dev/` | Ephemeral |

The filestore contains binary attachments (PDFs, images, etc.) stored by Odoo.
It is NOT in git. Each database has its own subdirectory under `filestore/`.

### Sessions

| Environment | Path | Persistence |
|-------------|------|-------------|
| Production | `/var/lib/odoo/sessions/` | Azure Files |
| Devcontainer | `/var/lib/odoo/sessions/` | Docker volume |
| Local dev | `/tmp/odoo-data/sessions/` | Ephemeral |

Session files are server-side session stores. With `workers > 0`, Odoo uses
file-based sessions by default. Redis session storage is available via
configuration but not currently active.

---

## Required Observables

Every running Odoo container must expose these observables for health
monitoring and operational diagnostics.

### Health Endpoint

| Endpoint | Method | Expected response | Purpose |
|----------|--------|-------------------|---------|
| `/web/health` | GET | `200 OK` with `{"status": "pass"}` | ACA health probe |
| `/web/database/list` | POST | Blocked (`list_db = False`) | Verify DB listing is disabled |

The ACA health probe is configured to hit `/web/health` every 30 seconds.
Three consecutive failures trigger a container restart.

### Addon Discovery Log

On startup, Odoo logs all discovered addons and their paths. This must be
captured and verifiable:

```
INFO odoo.modules.loading: loading 127 modules...
INFO odoo.modules.loading: Modules loaded.
```

The copilot-specific modules must appear in the installed module list:

```
INFO odoo odoo.modules.registry: module ipai_odoo_copilot: creating or updating database tables
INFO odoo odoo.modules.registry: module ipai_copilot_actions: creating or updating database tables
```

### Config Dump

On startup with `--log-level=debug`, Odoo logs the effective configuration.
The following parameters must be verified in CI:

| Parameter | Expected value |
|-----------|---------------|
| `addons_path` | Contains all three roots in correct order |
| `db_name` | `odoo` (production) or `odoo_dev` (development) |
| `list_db` | `False` |
| `proxy_mode` | `True` |
| `workers` | `>= 2` |

---

## Container Image Layers

The production Docker image is built in layers for cache efficiency and
separation of concerns.

### Layer Stack

```
+--------------------------------------------------+
| Layer 5: Config overlay                           |
|   /etc/odoo/odoo.conf (build-time template)       |
|   Entrypoint script                                |
+--------------------------------------------------+
| Layer 4: IPAI modules                             |
|   /workspaces/odoo/addons/ipai/*                  |
|   69 custom modules                               |
+--------------------------------------------------+
| Layer 3: OCA dependencies                         |
|   /workspaces/odoo/addons/oca/*                   |
|   Cloned from OCA GitHub repos at build time       |
|   Pinned to specific commits                       |
+--------------------------------------------------+
| Layer 2: Python dependencies                      |
|   pip install -r requirements.txt                 |
|   OCA requirements, IPAI requirements              |
+--------------------------------------------------+
| Layer 1: Base Odoo 18                             |
|   /opt/odoo/ (Odoo CE 18 source)                  |
|   System packages (PostgreSQL client, wkhtmltopdf) |
|   Python 3.12                                      |
+--------------------------------------------------+
| Layer 0: Base OS                                  |
|   Debian Bookworm (slim)                          |
+--------------------------------------------------+
```

### Build Arguments

| Build arg | Purpose | Example |
|-----------|---------|---------|
| `ODOO_VERSION` | Odoo CE branch | `19.0` |
| `OCA_REPOS` | Comma-separated OCA repo list | `web,server-ux,account-financial-tools` |
| `OCA_BRANCH` | OCA branch | `19.0` |

### Image Registry

| Registry | Image | Tag convention |
|----------|-------|---------------|
| `acripaiodoo.azurecr.io` | `odoo-ce` | `19.0-<git-short-sha>` |
| `acripaiodoo.azurecr.io` | `odoo-ce` | `latest` (rolling, points to last successful build) |

---

## Azure Container Apps Specifics

### Revision Mode

The ACA apps use **single revision mode**. Each deployment replaces the
previous revision entirely. There is no traffic splitting between revisions.

### Scaling Configuration

| App | Min replicas | Max replicas | Scale rule |
|-----|-------------|-------------|-----------|
| `ipai-odoo-dev-web` | 1 | 3 | HTTP concurrent requests > 50 |
| `ipai-odoo-dev-worker` | 1 | 2 | Queue length (custom metric) |
| `ipai-odoo-dev-cron` | 1 | 1 | Fixed (singleton) |
| `ipai-copilot-gateway` | 1 | 3 | HTTP concurrent requests > 30 |

### Environment Variable Injection from Key Vault

Secrets are injected from Azure Key Vault into ACA environment variables using
managed identity. The flow:

```
ACA managed identity
  --> Azure Key Vault (kv-ipai-dev)
  --> Secret reference in ACA config
  --> Environment variable in container
```

| Environment variable | Key Vault secret name | Consumer |
|---------------------|----------------------|----------|
| `ODOO_DB_HOST` | `odoo-db-host` | Odoo web/worker/cron |
| `ODOO_DB_USER` | `odoo-db-user` | Odoo web/worker/cron |
| `ODOO_DB_PASSWORD` | `odoo-db-password` | Odoo web/worker/cron |
| `AZURE_OPENAI_API_KEY` | `azure-openai-api-key` | Copilot gateway (fallback) |
| `ZOHO_SMTP_USER` | `zoho-smtp-user` | Odoo web |
| `ZOHO_SMTP_PASSWORD` | `zoho-smtp-password` | Odoo web |
| `ENTRA_CLIENT_SECRET` | `entra-client-secret` | Odoo web (OIDC) |

### Ingress Configuration

| App | External ingress | Target port | Transport |
|-----|-----------------|-------------|-----------|
| `ipai-odoo-dev-web` | Yes (via Front Door) | 8069 | HTTP/1.1 |
| `ipai-copilot-gateway` | Internal only | 8088 | HTTP/1.1 |
| `ipai-odoo-dev-worker` | None | N/A | N/A (queue consumer) |
| `ipai-odoo-dev-cron` | None | N/A | N/A (cron runner) |

### Resource Limits

| App | CPU | Memory |
|-----|-----|--------|
| `ipai-odoo-dev-web` | 1.0 | 2Gi |
| `ipai-odoo-dev-worker` | 0.75 | 1.5Gi |
| `ipai-odoo-dev-cron` | 0.5 | 1Gi |
| `ipai-copilot-gateway` | 0.5 | 1Gi |

---

## Machine-Readable Contract

See `ssot/odoo/runtime_contract.yaml` for the YAML-encoded version of this
contract, suitable for CI validation and agent consumption.
