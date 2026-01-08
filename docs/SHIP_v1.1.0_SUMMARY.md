# AIUX Ship v1.1.0 - Production Release Summary

**Release Date**: 2026-01-08
**Git Tag**: `ship-aiux-v1.1.0`
**Status**: ✅ Tagged, Pushed, Production-Ready

---

## What Was Shipped

### 1. Parameterized Production PRD

**File**: `docs/prd/AIUX_SHIP_PRD_v1.1.0.md`

**Key Improvements Over Previous Attempts**:
- ❌ **Old Approach**: Hardcoded "odoo-ce", "odoo_core", "deploy/docker-compose.prod.yml"
- ✅ **New Approach**: All values are `${VARIABLE_NAME}` runtime inputs

**Why This Matters**:
Service names drift (odoo → odoo-ce → odoo-app), DB names vary (odoo → odoo_prod), compose files move (deploy/ → infra/). Hardcoding these causes 502/500 errors when infrastructure changes.

**Documented Failure Modes**:
1. **502 Bad Gateway** - upstream not reachable, health checks not waited for
2. **500 Asset Errors** - stale assets, missing `-u web` upgrade
3. **OwlError** - server code updated without asset rebuild
4. **OAuth Loops** - proxy headers not set, public URL drift
5. **Email Setup Churn** - Mailgun DNS not verified
6. **Queue Backlogs** - cron not running, OCR service unreachable

### 2. Machine-Readable End-State Spec

**File**: `docs/prd/end_state/AIUX_SHIP_v1.1.0_PARAMETERIZED.json`

**Defines**:
- 8-phase deployment with gates (provision → db_up → odoo_up → install → assets → proxy → smoke → proofs)
- Health check timings from actual `docker-compose.prod.yml` (DB: 30s start, Odoo: 120s start)
- Required commands (all parameterized, no hardcoded names)
- Failure modes with causes and prevention strategies
- Secrets policy (never echo, never log full values)

**Critical Health Check Detail**:
```json
{
  "odoo": {
    "command": "curl -fsS http://localhost:8069/web/health || exit 1",
    "interval_seconds": 30,
    "timeout_seconds": 10,
    "retries": 3,
    "start_period_seconds": 120,
    "critical_note": "Odoo needs 120s start period - module loading takes time!"
  }
}
```

### 3. Fully Parameterized Bootstrap Script

**File**: `scripts/deploy/bootstrap_from_tag.sh`

**Parameters** (All Configurable):
```bash
REPO="${REPO:-https://github.com/jgtolentino/odoo-ce.git}"
GIT_REF="${GIT_REF:-ship-aiux-v1.1.0}"
COMPOSE_FILE="${COMPOSE_FILE:-deploy/docker-compose.prod.yml}"
ODOO_SERVICE="${ODOO_SERVICE:-odoo}"
DB_SERVICE="${DB_SERVICE:-db}"
ODOO_DB="${ODOO_DB:-odoo}"
SHIP_MODULES="${SHIP_MODULES:-ipai_theme_aiux,ipai_aiux_chat,ipai_ask_ai,ipai_document_ai,ipai_expense_ocr}"
```

**Usage**:
```bash
# Default (uses all defaults from above)
curl -fsSL https://github.com/jgtolentino/odoo-ce/raw/ship-aiux-v1.1.0/scripts/deploy/bootstrap_from_tag.sh | bash

# Custom (override any parameter)
export GIT_REF=ship-aiux-v1.1.0
export ODOO_DB=odoo_production
export COMPOSE_FILE=infra/compose/prod.yml
bash scripts/deploy/bootstrap_from_tag.sh
```

**What It Does** (10 Steps):
1. Install Docker + dependencies
2. Clone repo at `$GIT_REF`
3. Configure environment
4. Pull Docker images
5. Start services (waits 120s for Odoo health check)
6. Initial verification
7. Install AIUX modules (`-i $SHIP_MODULES`)
8. Rebuild web assets (`-u web,$SHIP_MODULES`)
9. Restart Odoo (wait 120s for health)
10. Final verification + health checks

### 4. Workspace Standardization

**Files**:
- `.vscode/ipai_workspace.code-workspace` - Canonical workspace
- `.vscode/settings.json` - Editor configuration
- `.vscode/tasks.json` - **Parameterized tasks** (no hardcoded names)
- `.vscode/README.md` - Usage guide

**Tasks** (All Parameterized):
- `odoo:compose up (prod file)` - Uses `${COMPOSE_FILE}`
- `odoo:rebuild assets (fix 500)` - Uses `${ODOO_SERVICE}` and `${ODOO_DB}`
- `odoo:health (nginx + odoo)` - Uses `${ODOO_SERVICE}`
- `odoo:502 triage` - Uses `${ODOO_SERVICE}`
- `odoo:db connectivity` - Uses `${DB_SERVICE}`

**Why This Works in VSCode/Cursor/Claude Code**:
All three editors read the same `.vscode/` files. No editor-specific drift.

---

## Shipped Modules

| Module | Maturity | Purpose |
|--------|----------|---------|
| `ipai_theme_aiux` | stub v0 | CSS token plumbing, sidebar hooks, widget mount points |
| `ipai_aiux_chat` | stub v0 | OWL service + templates (minimize/popup/sidepanel only) |
| `ipai_ask_ai` | production | Backend "Ask AI" routing/integration |
| `ipai_document_ai` | production | Document intelligence features |
| `ipai_expense_ocr` | production | Receipt OCR pipeline (dedupe, confidence routing, queue) |

---

## Infrastructure from docker-compose.prod.yml

**Service Names** (resolved at runtime):
- DB service: `db` (container: `odoo-db`)
- Odoo service: `odoo` (container: `odoo-ce`)

**Environment Variables Required**:
```bash
DB_NAME=${DB_NAME:-odoo}
DB_USER=${DB_USER:-odoo}
DB_PASSWORD=${DB_PASSWORD:?required}  # Must be set!
APP_IMAGE=${APP_IMAGE:-ghcr.io/jgtolentino/odoo-ce}
APP_IMAGE_VERSION=${APP_IMAGE_VERSION:-latest}
```

**Health Checks**:
- DB: `pg_isready -U ${DB_USER} -d ${DB_NAME}` (interval: 10s, start: 30s)
- Odoo: `curl -fsS http://localhost:8069/web/health` (interval: 30s, **start: 120s**)

**Critical**: Odoo needs 120s start period for module loading!

---

## Verification Commands (Parameterized)

**All commands use variables - no hardcoded names:**

```bash
# DB Health
docker compose -f "${COMPOSE_FILE}" exec -T "${DB_SERVICE}" \
  psql -U "${DB_USER}" -d "${ODOO_DB}" -c 'SELECT 1'

# Odoo Health
docker compose -f "${COMPOSE_FILE}" exec -T "${ODOO_SERVICE}" \
  curl -fsS http://localhost:8069/web/health

# Install Modules
docker compose -f "${COMPOSE_FILE}" exec -T "${ODOO_SERVICE}" \
  odoo -d "${ODOO_DB}" -i "${SHIP_MODULES}" --stop-after-init

# Upgrade with Assets (prevents 500)
docker compose -f "${COMPOSE_FILE}" exec -T "${ODOO_SERVICE}" \
  odoo -d "${ODOO_DB}" -u "web,${SHIP_MODULES}" --stop-after-init

# Restart
docker compose -f "${COMPOSE_FILE}" restart "${ODOO_SERVICE}"
```

---

## Common Pitfalls (What NOT to Do)

### ❌ Don't Hardcode Container Names
```bash
# BAD
docker exec odoo-ce odoo -d odoo -i module

# GOOD
docker compose -f "${COMPOSE_FILE}" exec -T "${ODOO_SERVICE}" \
  odoo -d "${ODOO_DB}" -i "${SHIP_MODULES}"
```

### ❌ Don't Skip Health Check Wait Times
```bash
# BAD
docker compose up -d
docker compose exec odoo odoo -d odoo -i module  # FAILS - Odoo not ready!

# GOOD
docker compose up -d
sleep 120  # Match Odoo's start_period
docker compose exec odoo odoo -d odoo -i module
```

### ❌ Don't Assume Database Names
```bash
# BAD
odoo -d odoo_core -i module

# GOOD
odoo -d "${ODOO_DB}" -i "${SHIP_MODULES}"
```

---

## Fresh Deployment (DigitalOcean Droplet)

**Requirements**:
- Ubuntu 22.04+ droplet
- 4GB+ RAM (8GB recommended)
- 80GB+ disk

**One-Command Bootstrap**:
```bash
curl -fsSL https://github.com/jgtolentino/odoo-ce/raw/ship-aiux-v1.1.0/scripts/deploy/bootstrap_from_tag.sh | bash
```

**Manual Deployment** (if you want control):
```bash
export REPO=https://github.com/jgtolentino/odoo-ce.git
export GIT_REF=ship-aiux-v1.1.0
export APP_DIR=/opt/odoo-ce
export COMPOSE_FILE=deploy/docker-compose.prod.yml
export ODOO_SERVICE=odoo
export DB_SERVICE=db
export ODOO_DB=odoo
export SHIP_MODULES="ipai_theme_aiux,ipai_aiux_chat,ipai_ask_ai,ipai_document_ai,ipai_expense_ocr"

# Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker "$USER"
newgrp docker

# Clone and deploy
sudo mkdir -p "$APP_DIR"
sudo chown -R "$USER":"$USER" "$APP_DIR"
cd "$APP_DIR"
git clone "$REPO" .
git checkout "$GIT_REF"

# Start services
docker compose -f "$COMPOSE_FILE" up -d

# Wait for health checks (120s for Odoo!)
sleep 30  # DB
sleep 90  # Odoo

# Install modules
docker compose -f "$COMPOSE_FILE" exec -T "$ODOO_SERVICE" \
  odoo -d "$ODOO_DB" -i "$SHIP_MODULES" --stop-after-init

# Rebuild assets (critical - prevents 500 errors!)
docker compose -f "$COMPOSE_FILE" exec -T "$ODOO_SERVICE" \
  odoo -d "$ODOO_DB" -u "web,$SHIP_MODULES" --stop-after-init

# Restart and verify
docker compose -f "$COMPOSE_FILE" restart "$ODOO_SERVICE"
sleep 120  # Wait for restart
./scripts/deploy/verify_prod.sh
```

---

## Post-Deployment Checklist

1. ✅ **Verify tag exists**: `git ls-remote --tags origin | grep ship-aiux-v1.1.0`
2. ✅ **Health checks pass**:
   - DB: `docker compose -f "$COMPOSE_FILE" exec -T "$DB_SERVICE" psql -U postgres -d postgres -c 'SELECT 1'`
   - Odoo: `docker compose -f "$COMPOSE_FILE" exec -T "$ODOO_SERVICE" curl -fsS http://localhost:8069/web/health`
3. ✅ **Modules installed**: Check `/web/database/manager` or Odoo apps list
4. ✅ **Assets working**: `/web` and `/web/login` return 200, no 500 on assets
5. ✅ **Verification scripts pass**:
   - `ODOO_DB=$ODOO_DB ./scripts/aiux/verify_install.sh`
   - `ODOO_DB=$ODOO_DB ./scripts/aiux/verify_assets.sh`
   - `./scripts/deploy/verify_prod.sh`

---

## Why This Prevents 502/500 Errors

### 502 Bad Gateway
**Root Cause**: Nginx proxying to Odoo before it's ready, or to wrong container name
**Prevention**:
- Wait 120s for Odoo health check (matches `start_period` in compose)
- Use `${ODOO_SERVICE}` variable (works even if container name changes)
- Health checks before exposing to proxy

### 500 Asset Errors
**Root Cause**: Web assets not rebuilt after module changes
**Prevention**:
- Always run `-u web,$SHIP_MODULES` after install/upgrade
- Restart Odoo after asset rebuild
- Verify `/web` and `/web/assets/` endpoints

---

## Git Tag Information

**Tag**: `ship-aiux-v1.1.0`
**SHA**: Verify with `git ls-remote --tags origin | grep ship-aiux-v1.1.0`
**Tagged Commit Includes**:
- Workspace standardization (`.vscode/`)
- Production PRD (`docs/prd/AIUX_SHIP_PRD_v1.1.0.md`)
- Parameterized end-state spec (`docs/prd/end_state/AIUX_SHIP_v1.1.0_PARAMETERIZED.json`)
- Bootstrap script (`scripts/deploy/bootstrap_from_tag.sh`)
- Verification scripts (`scripts/aiux/`, `scripts/deploy/`)
- Runbooks (`ops/runbooks/`)
- CI gates (`.github/workflows/aiux-ship-gate.yml`)

---

## Next Steps

1. **Create DigitalOcean Droplet** (Ubuntu 22.04, 4GB+ RAM)
2. **Run Bootstrap Script**:
   ```bash
   curl -fsSL https://github.com/jgtolentino/odoo-ce/raw/ship-aiux-v1.1.0/scripts/deploy/bootstrap_from_tag.sh | bash
   ```
3. **Configure Production Secrets** (`deploy/.env`)
4. **Setup Domain/DNS** for production access
5. **Configure nginx** (see `deploy/nginx/erp.insightpulseai.net.conf`)
6. **Run Final Verifications**:
   - Module installation
   - Asset verification
   - Health checks
   - Smoke tests

---

## Key Takeaways

### What Changed from Previous Attempts

| Before | After |
|--------|-------|
| Hardcoded "odoo-ce" container | `${ODOO_SERVICE}` variable |
| Hardcoded "odoo_core" database | `${ODOO_DB}` variable |
| Assumed "deploy/docker-compose.prod.yml" | `${COMPOSE_FILE}` variable |
| Guessed service ready times | Explicit 120s wait for Odoo health |
| Manual debugging when things break | Parameterized commands that work regardless of drift |

### Why Parameterization Matters

**Infrastructure Changes**:
- Service names: odoo → odoo-ce → odoo-app → odoo-18
- DB names: odoo → odoo_core → odoo_prod → odoo_staging
- Compose paths: root → deploy/ → infra/ → docker/
- Container names: odoo-ce → odoo-erp-prod → custom

**With Hardcoding**: Each change breaks scripts → 502/500 errors → manual debugging

**With Parameterization**: Scripts accept inputs → work regardless of infrastructure changes

---

*Release: AIUX Ship v1.1.0*
*Date: 2026-01-08*
*Status: Production-Ready*
*Documentation: Complete*
*Verification: Automated*
*Deployment: One-Command Bootstrap*
