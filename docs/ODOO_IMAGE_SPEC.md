# IPAI Odoo 18 Custom Image Specification

**Version:** 2.0.0
**Status:** Approved
**Owner:** jgtolentino
**Last Updated:** 2025-12-19

---

## 1. Purpose

Provide a **reproducible**, **upgrade-safe**, **OCA-compliant** Odoo 18 CE runtime image that:

- Boots Odoo 18 reliably in multi-worker mode
- Loads modules in strict priority: **IPAI → OCA → Core**
- Supports deterministic OCA dependency pinning (no "latest branch drift")
- Supports secrets via files (`*_FILE`) and environment variables
- Ships with build artifacts for audit: **SBOM**, **vuln report**, **image diff**

### Non-Goals

- Not an Enterprise image
- Not embedding Postgres
- Not bundling tenant data or DB migrations into the image artifact

---

## 2. Image Naming, Tags, and Release Channels

### Repository

```
ghcr.io/jgtolentino/odoo-ce
```

### Tags

| Tag Pattern | Description | Example |
|-------------|-------------|---------|
| `18.0-<YYYYMMDD>` | Daily/weekly build cadence | `18.0-20251219` |
| `18.0-<gitsha>` | Immutable CI build | `18.0-abc1234` |
| `18.0` | Floating channel (latest stable) | `18.0` |
| `18.0-standard` | Standard profile build | `18.0-standard` |
| `18.0-parity` | Full enterprise parity | `18.0-parity` |
| `edge-<profile>` | Main branch builds | `edge-parity` |

### OCI Labels

```dockerfile
org.opencontainers.image.source=https://github.com/jgtolentino/odoo-ce
org.opencontainers.image.revision=<git-sha>
org.opencontainers.image.created=<timestamp>
org.opencontainers.image.version=<semver>
org.opencontainers.image.vendor=InsightPulse AI
com.insightpulseai.profile=<standard|parity|dev>
com.insightpulseai.odoo.version=18.0
```

---

## 3. Compatibility Matrix

| Component | Version | Notes |
|-----------|---------|-------|
| Odoo | 18.0 | Official CE base |
| OS | Debian Bookworm | Inherited from `odoo:18.0` |
| Architectures | `linux/amd64`, `linux/arm64` | Multi-arch builds |
| Database | PostgreSQL 15/16 | External |
| Python | 3.11+ | System Python |

### Addons Paths (Priority Order)

1. `/mnt/odoo/addons/ipai` - IPAI custom modules
2. `/mnt/odoo/addons/oca` - OCA modules
3. Base image core addons (unchanged)

---

## 4. Repository Layout

```text
.
├── Dockerfile                      # Legacy single-stage build
├── docker/
│   ├── Dockerfile.unified          # Multi-stage OCA-vendoring build
│   ├── docker-entrypoint.sh        # Container entrypoint
│   └── odoo.conf.template          # (legacy)
├── config/
│   ├── odoo.conf.template          # Configuration template
│   └── entrypoint.d/
│       ├── 10-log-env.sh           # Log environment at startup
│       ├── 20-render-conf.sh       # Render config from template
│       └── 90-preflight.sh         # Pre-flight checks
├── addons/
│   └── ipai_*/                     # IPAI custom modules
├── vendor/
│   ├── oca.lock.json               # Pinned OCA repos + commits
│   └── oca-sync.sh                 # Deterministic sync helper
├── scripts/
│   ├── ci_smoke_test.sh            # CI stop-after-init test
│   └── image_audit.sh              # SBOM/vuln/diff bundle
└── deploy/
    └── odoo.conf                   # Production config
```

---

## 5. Deterministic OCA Vendoring

### 5.1 Lock Format (`vendor/oca.lock.json`)

```json
{
  "version": "2.0",
  "odoo_version": "18.0",
  "generated_at": "2025-12-19T00:00:00Z",
  "repos": [
    {
      "name": "OCA/project",
      "url": "https://github.com/OCA/project.git",
      "ref": "18.0",
      "commit": "<pinned-sha>",
      "modules": ["project_task_default_stage", "project_template"]
    }
  ]
}
```

### 5.2 Rules

- Always pin `commit` for reproducible builds
- Only copy allowed modules into `/mnt/odoo/addons/oca`
- Never ship `.git` directories in runtime image
- Build fails if a pinned module is missing

### 5.3 Sync Commands

```bash
# Clone/update to pinned versions
./vendor/oca-sync.sh sync

# Verify repos match lockfile
./vendor/oca-sync.sh verify

# Update lockfile with current HEAD commits
./vendor/oca-sync.sh update

# Export modules for Docker build (no .git)
./vendor/oca-sync.sh export
```

---

## 6. Addons Path Priority

In `odoo.conf`:

```ini
[options]
addons_path = /mnt/odoo/addons/ipai,/mnt/odoo/addons/oca,/usr/lib/python3/dist-packages/odoo/addons
```

Search order:
1. IPAI modules (custom)
2. OCA modules (community)
3. Core Odoo modules

---

## 7. Runtime Configuration Contract

### 7.1 Environment Variables

**Database:**

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `db` | Database host |
| `PORT` | `5432` | Database port |
| `USER` | `odoo` | Database user |
| `PASSWORD` | - | Database password |
| `PASSWORD_FILE` | - | Path to password file (preferred) |
| `DB_NAME` | `False` | Database name |

**Odoo:**

| Variable | Default | Description |
|----------|---------|-------------|
| `ODOO_RC` | `/etc/odoo/odoo.conf` | Config file path |
| `PROXY_MODE` | `True` | Enable proxy mode |
| `ADMIN_PASSWD` | - | Admin master password |
| `ADMIN_PASSWD_FILE` | - | Path to admin password file |
| `DBFILTER` | `.*` | Database filter |
| `LIST_DB` | `False` | Show database list |

**Workers:**

| Variable | Default | Description |
|----------|---------|-------------|
| `ODOO_WORKERS` | `4` | Number of workers |
| `ODOO_MAX_CRON_THREADS` | `2` | Cron threads |
| `ODOO_LIMIT_MEMORY_SOFT` | `2147483648` | Soft memory limit |
| `ODOO_LIMIT_MEMORY_HARD` | `2684354560` | Hard memory limit |
| `ODOO_LIMIT_TIME_CPU` | `600` | CPU time limit |
| `ODOO_LIMIT_TIME_REAL` | `1200` | Real time limit |

### 7.2 Secrets (Preferred)

Mount secrets at:
- `/run/secrets/postgresql_password` → `PASSWORD_FILE`
- `/run/secrets/odoo_admin_passwd` → `ADMIN_PASSWD_FILE`

No secrets are baked into the image; no defaults in production.

---

## 8. Dockerfile Specification

The unified Dockerfile (`docker/Dockerfile.unified`) uses multi-stage builds:

### Stage 1: OCA Builder

```dockerfile
FROM debian:bookworm-slim AS oca-builder
# Clone OCA repos from lockfile
# Extract only specified modules
# No .git directories in output
```

### Stage 2: Runtime

```dockerfile
FROM odoo:18.0 AS runtime
# Copy OCA modules from builder
# Copy IPAI modules from repo
# Install entrypoint hooks
# Configure environment
```

### Stage 3: Development (optional)

```dockerfile
FROM runtime AS development
# Add dev tools: debugpy, pytest, coverage
```

### Build Commands

```bash
# Standard production build
docker build -f docker/Dockerfile.unified -t ipai-odoo:18.0 .

# With specific profile
docker build -f docker/Dockerfile.unified \
  --build-arg PROFILE=parity \
  -t ipai-odoo:18.0-parity .

# Development build
docker build -f docker/Dockerfile.unified \
  --target development \
  -t ipai-odoo:dev .
```

---

## 9. Entrypoint Hooks

### 9.1 Hook Execution Order

| Script | Purpose |
|--------|---------|
| `10-log-env.sh` | Log environment information |
| `20-render-conf.sh` | Render config from template |
| `90-preflight.sh` | Pre-flight checks |

### 9.2 Preflight Checks

The `90-preflight.sh` script verifies:

1. Required directories exist (IPAI addons, OCA addons)
2. Configuration file is present and readable
3. Filestore directory is writable
4. No `.git` directories in production
5. Optional: Database connectivity (`PREFLIGHT_DB_CHECK=1`)

---

## 10. Production Runtime: Compose Reference

```yaml
services:
  odoo:
    image: ghcr.io/jgtolentino/odoo-ce:18.0
    ports:
      - "8069:8069"
    environment:
      - HOST=postgres
      - PORT=5432
      - USER=odoo
      - PASSWORD_FILE=/run/secrets/postgresql_password
      - PROXY_MODE=true
      - LIST_DB=false
    volumes:
      - odoo-data:/var/lib/odoo
    secrets:
      - postgresql_password
    depends_on:
      - postgres

  postgres:
    image: postgres:16
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD_FILE=/run/secrets/postgresql_password
    volumes:
      - pg-data:/var/lib/postgresql/data
    secrets:
      - postgresql_password

volumes:
  odoo-data:
  pg-data:

secrets:
  postgresql_password:
    file: ./secrets/postgresql_password.txt
```

---

## 11. CI/CD Gates

### 11.1 Required CI Checks

1. **Build**: Multi-arch image build (`amd64`, `arm64`)
2. **Smoke Test**: `--stop-after-init` passes
3. **Module Validation**: Addons paths verified
4. **Audit Bundle**: SBOM + vulns + image diff

### 11.2 Smoke Test

```bash
./scripts/ci_smoke_test.sh ghcr.io/jgtolentino/odoo-ce:18.0-<sha>
```

The smoke test:
- Starts PostgreSQL container
- Runs Odoo with `--stop-after-init`
- Verifies database creation
- Checks for critical errors in logs

### 11.3 Audit Bundle

```bash
./scripts/image_audit.sh ghcr.io/jgtolentino/odoo-ce:18.0 odoo:18.0
```

Generates:
- `sbom.json` - Software Bill of Materials
- `vulns.json` - Vulnerability scan
- `image_diff.json` - File/package differences
- `audit_summary.md` - Human-readable report

---

## 12. IPAI Module Policy

### Target Architecture (5 Canonical Modules)

1. `ipai_workspace_core` - Shared groups, menus, base config
2. `ipai_ppm` - Project Portfolio Management
3. `ipai_advisor` - AI-powered recommendations
4. `ipai_workbooks` - Reporting workbooks
5. `ipai_connectors` - External integrations (n8n, APIs)

### Current State

The image currently includes 30+ IPAI modules. Module consolidation to the 5-module target is a future phase.

### Rules

- No business logic in `ipai_connectors` beyond integration glue
- Shared groups/menus live in `ipai_workspace_core`
- Views must use unique xmlids (`ipai_*` prefix)
- Tests required for modules with computed fields / scheduled jobs

---

## 13. Operational Defaults

In `odoo.conf`:

```ini
[options]
proxy_mode = True
list_db = False
log_level = info
workers = 4
max_cron_threads = 2
limit_memory_soft = 2147483648
limit_memory_hard = 2684354560
limit_time_cpu = 600
limit_time_real = 1200
```

---

## 14. Acceptance Criteria

A build is **releaseable** when:

- [ ] Image builds for `amd64` + `arm64`
- [ ] `--stop-after-init` passes against fresh Postgres
- [ ] Addons paths load without errors
- [ ] OCA lock is enforced (missing module/commit fails build)
- [ ] `image_audit.tgz` produced
- [ ] No `.git` directories in `/mnt/odoo/addons/oca`
- [ ] Unique xmlid collision check passes

---

## 15. Troubleshooting Playbook

### Module Not Found

1. Check addons path ordering in config
2. Verify module exists under `/mnt/odoo/addons/ipai` or `/mnt/odoo/addons/oca`
3. Run preflight check: `PREFLIGHT_STRICT=1 /entrypoint.d/90-preflight.sh`

### View xmlid Collision

1. Enforce `ipai_<module>_*` xmlid naming
2. Never reuse generic ids like `assets_backend`
3. Check for duplicates: `grep -r "id=" addons/ipai_*/views/`

### Stuck Restart Loop

1. Run with stop-after-init: `docker run --rm <image> --stop-after-init`
2. Check logs for errors
3. Disable autoupgrade in entrypoint hooks if present

### Database Connection Failed

1. Verify `HOST`, `PORT`, `USER` environment variables
2. Check PostgreSQL is running: `pg_isready -h <host> -p <port>`
3. Verify network connectivity between containers

---

## 16. Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 2.0.0 | 2025-12-19 | Deterministic OCA vendoring, JSON lockfile, CI gates | jgtolentino |
| 1.0.0 | 2025-11-24 | Initial specification | jgtolentino |

---

## 17. Related Documentation

- [003-odoo-ce-custom-image-spec.md](./003-odoo-ce-custom-image-spec.md) - Original image spec
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Deployment guide
- [OCA_MIGRATION.md](./OCA_MIGRATION.md) - OCA module migration notes
- [SECRETS_NAMING_AND_STORAGE.md](./SECRETS_NAMING_AND_STORAGE.md) - Secret management

---

*This specification ensures that the custom Odoo CE image serves as a reliable, secure, and consistent deployment artifact across all IPAI environments.*
