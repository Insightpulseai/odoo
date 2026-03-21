# Odoo Runtime

## Definition

In this repository, **Odoo runtime** means the live Odoo server process operating under a specific environment contract.

That contract consists of:

- the running Odoo process
- the active `odoo.conf`
- the target database
- the loaded addon paths
- the injected environment variables / secrets
- the network / hostname / proxy context for that deployment

In shorthand:

```text
Odoo runtime = process + config + database + addons + secrets + network context
```

---

## Canonical process model

The runtime process is conceptually:

```text
odoo --config=/etc/odoo/odoo.conf
```

The process is not considered valid in isolation. It is only meaningful together with the config and deployment context that define its behavior.

---

## What the config controls

The active `odoo.conf` determines the environment contract for the runtime.

Key controls include:

* `db_name` — which database the runtime uses
* `db_host` / `db_port` — where PostgreSQL lives
* `addons_path` — which addon directories are loaded
* `workers` — concurrency model
* `proxy_mode` — reverse-proxy awareness
* `list_db` — database selector exposure
* logging settings
* selected mail-related runtime behavior where configured

The config file is therefore part of the runtime identity.

---

## Canonical environment mapping

| Environment | Config file                                            | Database       | Runtime surface      |
| ----------- | ------------------------------------------------------ | -------------- | -------------------- |
| local dev   | `config/dev/odoo.conf`                                 | `odoo_dev`     | local Docker runtime |
| staging     | `config/stage/odoo.conf` or `config/staging/odoo.conf` | `odoo_staging` | staging ACA app      |
| prod        | `config/prod/odoo.conf`                                | `odoo_prod`    | prod ACA app         |

### Canonical database naming

The only canonical Odoo database names are:

* `odoo_dev`
* `odoo_staging`
* `odoo_prod`

Any historical references such as `odoo_core`, bare `odoo`, or `odoo_stage` are non-canonical and must not be used for active runtime configuration.

---

## Runtime by environment

### Local dev runtime

Local runtime means:

* Odoo runs via local Docker / compose
* the process uses `config/dev/odoo.conf`
* the runtime connects to `odoo_dev`
* addons are loaded from the local mounted addon paths
* secrets come from local environment injection

### Staging runtime

Staging runtime means:

* Odoo runs in the staging Azure Container App
* the process uses staging config
* the runtime connects to `odoo_staging`
* the runtime uses the staged image/addon set
* secrets come from Azure environment injection / Key Vault-backed configuration

### Production runtime

Production runtime means:

* Odoo runs in the production Azure Container App
* the process uses `config/prod/odoo.conf`
* the runtime connects to `odoo_prod`
* the runtime uses the production image/addon set
* secrets come from Azure environment injection / Key Vault-backed configuration

---

## What is part of runtime identity

An Odoo runtime is defined by all of the following together:

### 1. Process identity

The actual running Odoo server process.

### 2. Config identity

The specific `odoo.conf` mounted into that process.

### 3. Database identity

The database the runtime is pointed at:

* `odoo_dev`
* `odoo_staging`
* `odoo_prod`

### 4. Code identity

The specific addon set available through `addons_path`, including:

* OCA addons
* `ipai_*` addons
* any approved local addons

### 5. Secret/environment identity

Runtime-injected values such as:

* database credentials
* SMTP credentials
* API keys
* provider configuration

These must come from environment injection / secure secret sources, not from committed plaintext config.

### 6. Network identity

The hostname, ingress, reverse proxy, and forwarded-header context for the deployment.

Examples:

* `erp.insightpulseai.com`
* staging ERP hostname
* Azure Front Door / proxy behavior

---

## What is not enough to define runtime

The following alone do **not** define the runtime:

* the container image by itself
* the code checkout by itself
* the database by itself
* the config file by itself

Only the full combination defines the real runtime behavior.

---

## Runtime doctrine

The repository treats runtime as environment-specific and deterministic.

### Rules

1. Local dev runtime must connect only to `odoo_dev`.
2. Staging runtime must connect only to `odoo_staging`.
3. Production runtime must connect only to `odoo_prod`.
4. Runtime config must match the actual deployment mount paths and network context.
5. Secrets must be injected securely and must not be hardcoded into repo-managed config.
6. Addon paths are part of runtime identity and must be treated as deployment-critical.
7. Reverse-proxy / hostname behavior is part of runtime correctness, not an external afterthought.

---

## Practical definition

Use this wording in other docs:

> Odoo runtime is the live Odoo server process running with a specific environment config, connected to a specific database, loading a specific addon set, and receiving its secrets and network context from the current deployment environment.
