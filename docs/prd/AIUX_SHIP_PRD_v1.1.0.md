# IPAI AIUX Ship PRD v1.1.0 (Complete, Production)

## 0) Release Identity

* **Release:** AIUX Ship
* **Version:** **1.1.0**
* **Repo:** `jgtolentino/odoo-ce`
* **Primary objective:** ship a **fresh-bootstrap deploy** from a known git ref that is **deterministic**, **CI-verifiable**, and **doesn't require manual debugging**.

## 1) What We Ship (Scope In)

### 1.1 Shippable IPAI Modules

* `ipai_theme_aiux` (stub v0)
  * Provides: CSS token plumbing, sidebar hooks, widget mount points

* `ipai_aiux_chat` (stub v0)
  * Provides: OWL service + templates supporting **mode contract**:
    * `minimize | popup | sidepanel` (**not fullscreen**)

* `ipai_ask_ai`
  * Provides: backend "Ask AI" routing/integration

* `ipai_document_ai`
  * Provides: document intelligence features

* `ipai_expense_ocr`
  * Provides: receipt OCR pipeline for expenses:
    * hash-based duplicate detection
    * confidence routing
    * OCR result storage model
    * queue processor cron

### 1.2 Operational Runbooks Included

* **Mailgun domain verification** (DNS + checks)
* **Sinch setup** (SMS provider)
* **OCR service** (your own service contract + ops)
* **Expense OCR operations** (queues, thresholds, reprocess)

### 1.3 Automation/Verification

* CI "ship gate" that fails if:
  * ship manifest references missing modules
  * install/upgrade verification fails

* Deterministic verification scripts:
  * install verification
  * asset verification
  * health checks

## 2) What We Explicitly Do NOT Ship (Out of Scope)

* Full polished AIUX theme (beyond stub)
* Full production chat UX (beyond stub)
* HA cluster / multi-node scaling
* Any "magic" UI steps during deploy (after initial secrets provisioning)

---

# 3) Primary Failure Modes We're Preventing

## 3.1 Observed Errors (taxonomy)

### A) **502 Bad Gateway (nginx)**

Root causes:
* upstream container not reachable (crash loop / wrong target / not ready yet)
* Odoo busy (module upgrade/asset compile) while nginx already serving traffic
* proxy mismatch: longpoll/websocket routing missing, timeouts too low

### B) **500 on /web or assets**

Root causes:
* stale assets after module changes
* missing `-u web` upgrade step after install/upgrade
* inconsistent addon paths / missing dependencies

### C) **Frontend JS errors (OwlError, broken UI)**

Root causes:
* server code updated without upgrading web assets
* OWL templates changed but bundles not rebuilt

### D) **OAuth redirect loops / wrong URL scheme**

Root causes:
* proxy headers not set
* proxy_mode not enforced
* public base URL drift

### E) **Email setup churn**

Root causes:
* Mailgun domain not verified
* DNS not propagated / wrong records
* SMTP config not validated by smoke test

### F) **Queue backlogs / stuck OCR**

Root causes:
* cron not running
* worker timeouts too low
* OCR service unreachable, retries unmanaged

---

# 4) Spec Controls (How the PRD prevents all of the above)

## 4.1 "Fresh Bootstrap" Deployment Contract (non-negotiable)

Deploy is defined as **phases** with **gates**:

1. **Provision** (host + env present)
2. **DB up** (reachable)
3. **Odoo up** (reachable, but not exposed yet)
4. **Install/Upgrade modules** (deterministic)
5. **Assets rebuild** (deterministic)
6. **Expose via proxy** (nginx/traefik)
7. **Smoke tests**
8. **Proof artifacts saved**

### Gate rules

* If any phase fails → stop immediately → output logs/artifacts → do not proceed.

## 4.2 Parameterization (no hardcoded "canonical" names)

All automation must accept:
* compose file path
* service names
* db name
* module list
* ports
* public URL

…via env vars or a single JSON/YAML config.

**This stops "it worked once" assumptions that cause 502/500 later.**

## 4.3 Deterministic Upgrade Step (prevents 500/OwlError)

Required step on every deploy:
* `-i` install for new DB
* `-u web,<ship_modules>` upgrade for existing DB
* **always** run web asset rebuild during upgrade

## 4.4 Proxy Readiness (prevents 502)

* proxy must wait for upstream readiness OR use health checks
* timeouts must tolerate first-run module upgrade and asset build
* explicit longpoll/websocket routing if enabled

## 4.5 Integration Readiness (Mailgun/Sinch/OCR)

Each integration must have:
* runbook
* env var contract
* smoke test command
* "red state" behavior (feature disabled gracefully)

---

# 5) Acceptance Criteria (Ship/No-Ship)

## 5.1 Install/Upgrade

* On clean DB: install completes for all ship modules
* On existing DB: upgrade completes for all ship modules
* No missing module errors
* No registry load failures

## 5.2 App Health

* `/web/login` returns 200 behind proxy
* `/web` returns 200 and loads bundles (no 500 assets)
* Chat stub does not crash UI (mode contract enforced)

## 5.3 OCR

* OCR job can be queued
* Result stored
* Low confidence routes to review queue
* Duplicate receipts blocked

## 5.4 Email/SMS

* Mailgun DNS verification checklist complete + SMTP smoke test passes
* Sinch smoke test passes (or feature disabled gracefully)

## 5.5 Proof Artifacts

Every deploy produces a folder containing:
* compose config snapshot
* env var "shape" (keys only, no values)
* install/upgrade logs
* nginx + odoo + db logs excerpt
* smoke test outputs

---

# 6) Deliverables (Repo Artifacts)

* ✅ PRD doc (this)
* ✅ Ship manifest v1.1.0
* ✅ End-state JSON spec (parameterized)
* ✅ Runbooks (4)
* ✅ Verification scripts
* ✅ CI ship gate workflow
* ✅ Bootstrap script that accepts parameters (no hardcodes)

---

# 7) Actual Infrastructure (from docker-compose.prod.yml)

**Service Names (resolved from compose):**
- Database service: `db` (container: `odoo-db`)
- Odoo service: `odoo` (container: `odoo-ce`)

**Environment Variables Required:**
```bash
# Database
DB_NAME=${DB_NAME:-odoo}
DB_USER=${DB_USER:-odoo}
DB_PASSWORD=${DB_PASSWORD:?required}
DB_HOST=${DB_HOST:-db}

# Odoo
APP_IMAGE=${APP_IMAGE:-ghcr.io/jgtolentino/odoo-ce}
APP_IMAGE_VERSION=${APP_IMAGE_VERSION:-latest}
ODOO_PORT=${ODOO_PORT:-8069}

# PostgreSQL tuning
POSTGRES_MAX_CONNECTIONS=${POSTGRES_MAX_CONNECTIONS:-100}
```

**Health Checks:**
- DB: `pg_isready -U ${DB_USER} -d ${DB_NAME}` (interval: 10s, start: 30s)
- Odoo: `curl -fsS http://localhost:8069/web/health` (interval: 30s, start: 120s)

**Critical: Odoo needs 120s start period** - module loading takes time!

---

# 8) Parameter Contract (No Hardcoded Assumptions)

All scripts MUST accept these as inputs (not assume values):

```bash
# Core parameters
COMPOSE_FILE=${COMPOSE_FILE:-deploy/docker-compose.prod.yml}
ODOO_SERVICE=${ODOO_SERVICE:-odoo}
DB_SERVICE=${DB_SERVICE:-db}
ODOO_DB=${ODOO_DB:-odoo}
GIT_REF=${GIT_REF:-ship-aiux-v1.1.0}

# Ship modules
SHIP_MODULES=${SHIP_MODULES:-ipai_theme_aiux,ipai_aiux_chat,ipai_ask_ai,ipai_document_ai,ipai_expense_ocr}

# Deployment
PUBLIC_BASE_URL=${PUBLIC_BASE_URL}  # Must be set explicitly
ODOO_PORT=${ODOO_PORT:-8069}
```

**Why this matters:**
- Service names can change (odoo → odoo-ce → odoo-app)
- DB names can vary per environment (odoo → odoo_prod → odoo_staging)
- Compose files can move (deploy/ → infra/ → docker/)
- Container names can change (odoo-ce → odoo-erp-prod → odoo-18-ce)

**By parameterizing everything, scripts work regardless of these changes.**

---

# 9) Verification Commands (Parameterized)

```bash
# Health check (works with any service names)
docker compose -f "${COMPOSE_FILE}" exec -T "${DB_SERVICE}" \
  psql -U "${DB_USER}" -d "${ODOO_DB}" -c 'SELECT 1'

docker compose -f "${COMPOSE_FILE}" exec -T "${ODOO_SERVICE}" \
  curl -fsS http://localhost:8069/web/health

# Install modules (works with any DB name)
docker compose -f "${COMPOSE_FILE}" exec -T "${ODOO_SERVICE}" \
  odoo -d "${ODOO_DB}" -i "${SHIP_MODULES}" --stop-after-init

# Upgrade with assets (prevents 500 errors)
docker compose -f "${COMPOSE_FILE}" exec -T "${ODOO_SERVICE}" \
  odoo -d "${ODOO_DB}" -u "web,${SHIP_MODULES}" --stop-after-init

# Restart after upgrade
docker compose -f "${COMPOSE_FILE}" restart "${ODOO_SERVICE}"
```

**No hardcoded names = works on any deployment.**

---

# 10) Common Pitfalls (What NOT to do)

❌ **Don't assume container names**
```bash
# BAD: Hardcoded container name
docker exec odoo-ce odoo -d odoo -i ipai_theme_aiux

# GOOD: Resolve from compose
docker compose -f "${COMPOSE_FILE}" exec -T "${ODOO_SERVICE}" \
  odoo -d "${ODOO_DB}" -i "${SHIP_MODULES}"
```

❌ **Don't assume compose file location**
```bash
# BAD: Assumes deploy/docker-compose.prod.yml
docker compose -f deploy/docker-compose.prod.yml up -d

# GOOD: Use variable
docker compose -f "${COMPOSE_FILE}" up -d
```

❌ **Don't assume database name**
```bash
# BAD: Hardcoded database
odoo -d odoo_core -i module

# GOOD: Use variable
odoo -d "${ODOO_DB}" -i "${SHIP_MODULES}"
```

❌ **Don't skip health check wait times**
```bash
# BAD: Start and immediately run commands
docker compose up -d
docker compose exec odoo odoo -d odoo -i module  # FAILS - Odoo not ready!

# GOOD: Wait for health checks
docker compose up -d
docker compose exec odoo odoo -d odoo --wait-until-healthy  # If available
# OR: Manual wait with health check verification
sleep 120  # Match Odoo's start_period
```

---

# 11) End-State Spec Location

See: `docs/prd/end_state/AIUX_SHIP_v1.1.0_PARAMETERIZED.json`

**Key difference from old spec:**
- ❌ Old: Hardcoded `"container": "odoo-ce"`, `"db": "odoo_core"`
- ✅ New: `"container": "${ODOO_SERVICE}"`, `"db": "${ODOO_DB}"`

---

*Last updated: 2026-01-08*
*Spec version: 1.1.0*
*Status: Production-ready, parameterized, drift-resistant*
