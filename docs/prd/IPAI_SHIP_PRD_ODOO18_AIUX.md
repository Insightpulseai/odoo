# IPAI AIUX Ship Bundle PRD

## Version

| Field | Value |
|-------|-------|
| PRD Version | v1.1.0 |
| Ship Tag | `ship-aiux-v1.1.0` |
| Repo | `jgtolentino/odoo-ce` |
| Status | Ready to Ship |

---

## 1. Goal

Ship a production-ready Odoo 18 CE + OCA + IPAI bundle that delivers:

- **AIUX UI foundation** (theme tokens + mount points)
- **AI Chat widget stub** (popup/sidepanel/minimize modes)
- **Ask AI backend** (Gemini routing)
- **Document AI module**
- **Expense OCR module** (receipt ingestion + dedupe + confidence workflow)
- **Operational integrations + runbooks** (Mailgun, Sinch, OCR service ops)
- **Deterministic CI ship gate** that proves installability + health

---

## 2. In Scope (What We Ship)

### 2.1 IPAI Modules (must exist + install)

| Module | Type | Status | Required |
|--------|------|--------|----------|
| `ipai_theme_aiux` | Theme | stub v0 | Yes |
| `ipai_aiux_chat` | Widget | stub v0 | Yes |
| `ipai_ask_ai` | Backend | exists | Yes |
| `ipai_document_ai` | Backend | exists | Yes |
| `ipai_expense_ocr` | Backend | exists | Yes |

**Module Details:**

1. **`ipai_theme_aiux`** (stub v0)
   - CSS tokens + sidebar hooks + widget mount points
   - No SCSS compile errors
   - Provides mount points for chat + ask-ai surfaces

2. **`ipai_aiux_chat`** (stub v0)
   - OWL service + templates
   - Mode enum enforced: `minimize` | `popup` | `sidepanel` (NO fullscreen)
   - Loads without JS errors

3. **`ipai_ask_ai`** (existing)
   - Accept query and route to configured model provider
   - Return response within defined timeout
   - Fail gracefully with structured error state

4. **`ipai_document_ai`** (existing)
   - Document intelligence surface

5. **`ipai_expense_ocr`** (existing)
   - Upload receipt to expense -> OCR job queued
   - Duplicate detection blocks same receipt hash
   - Confidence threshold routes to review queue when < 0.70
   - Cron processor runs and updates state deterministically

### 2.2 Ops / Runbooks (must exist)

| Runbook | Path | Purpose |
|---------|------|---------|
| Mailgun Domain Verification | `ops/runbooks/mailgun_domain_verification.md` | Domain verification operational steps |
| Sinch Setup | `ops/runbooks/sinch_setup.md` | Sinch application/provider setup |
| OCR Service | `ops/runbooks/ocr_service.md` | OCR service operations |
| Expenses OCR Runbook | `ops/runbooks/expenses_ocr_runbook.md` | Queue, cron, retry, failure states |

### 2.3 CI/CD Artifacts (must exist)

| Artifact | Path | Purpose |
|----------|------|---------|
| Ship Gate Workflow | `.github/workflows/aiux-ship-gate.yml` | CI gate that proves installability |
| Install Verify Script | `scripts/aiux/verify_install.sh` | Verify module installation |
| Assets Verify Script | `scripts/aiux/verify_assets.sh` | Verify asset compilation |
| Ship Manifest | `aiux_ship_manifest.yml` | Canonical module list for ship |

---

## 3. Out of Scope (NOT shipping in v1.1.0)

- Full production-grade AI chat UX parity (widget is stub v0)
- Full AI doc extraction pipelines beyond what `ipai_document_ai` already supports
- Production hosting resources (infra is bootstrapped from repo specs)

---

## 4. Functional Specs (Acceptance Criteria)

### 4.1 Installability (Hard Gate)

```gherkin
Given a clean Odoo DB
When ship stage installs modules per manifest
Then install completes without registry errors
And server boots successfully
```

### 4.2 UI/Theme (`ipai_theme_aiux`)

- [ ] Tokens load without SCSS compile errors
- [ ] Sidebar hooks render without JS errors
- [ ] Provides mount points for chat + ask-ai surfaces

### 4.3 Chat Widget Stub (`ipai_aiux_chat`)

- [ ] OWL service loads
- [ ] Supports exactly: `minimize`, `popup`, `sidepanel`
- [ ] No "fullscreen" mode allowed (type-enforced)

### 4.4 Ask AI (`ipai_ask_ai`)

- [ ] Can accept a query and route to configured model provider
- [ ] Returns a response within defined timeout
- [ ] Fails gracefully with structured error state (no OWL crash)

### 4.5 Expense OCR (`ipai_expense_ocr`)

- [ ] Upload receipt to expense -> OCR job queued
- [ ] Duplicate detection blocks same receipt hash
- [ ] Confidence threshold routes to review queue when < 0.70
- [ ] Cron processor runs and updates state deterministically

### 4.6 Sinch Integration (ops + config)

- [ ] App configuration documented (no secrets in repo)
- [ ] SMS/OTP can be enabled via env + provider config

### 4.7 Mailgun Domain Verification (ops + config)

- [ ] Verification procedure documented as operational runbook
- [ ] Pipeline expects verified DNS state before enabling sending

---

## 5. Reliability Specs (Prevents 502 Loop)

### 5.1 Mandatory Health Gates per Deploy

A deployment is **"green"** only if ALL pass:

| Gate | Check | Expected |
|------|-------|----------|
| Login Page | `GET /web/login` | HTTP 200 |
| Health Endpoint | `GET /web/health/*` | HTTP 200 |
| DB Connectivity | Simple query | OK |
| Odoo Registry | Loads with ship modules | OK |
| No Crash Loop | Container uptime stable | true |

### 5.2 Proof Artifacts (Required per Deploy)

Each deploy MUST produce:

1. **Module install logs** - Output from `odoo -u` command
2. **Health check outputs** - Curl results from health gates
3. **Git SHA** - Commit hash of deployed code
4. **Manifest version** - Ship bundle version

---

## 6. Deployment Spec

### 6.1 Fresh Bootstrap Sequence

```
1. Provision infra (DO droplet + managed DB or local)
2. Bring up DB + Odoo + proxy
3. Run install stage from aiux_ship_manifest.yml
4. Run verify scripts
5. Only then mark "production deployed"
```

### 6.2 Environment Variables (Placeholders)

```bash
# Required (set in .env or GitHub Secrets)
MAILGUN_API_KEY=
MAILGUN_DOMAIN=
SINCH_SERVICE_PLAN_ID=
SINCH_API_TOKEN=
OCR_SERVICE_URL=
OCR_SERVICE_TOKEN=
```

---

## 7. Integration Points

### 7.1 Mailgun

- **Scope**: Domain verification and sending
- **Runbook**: `ops/runbooks/mailgun_domain_verification.md`
- **Secrets in repo**: NO

### 7.2 Sinch

- **Scope**: SMS/OTP provider
- **Runbook**: `ops/runbooks/sinch_setup.md`
- **Secrets in repo**: NO

### 7.3 OCR Service

- **Scope**: Receipt/document OCR
- **Runbook**: `ops/runbooks/ocr_service.md`
- **Odoo Module**: `ipai_expense_ocr`

---

## 8. Verification Commands

### Quick Verify (Local)

```bash
./scripts/aiux/verify_install.sh
./scripts/aiux/verify_assets.sh
```

### Full Verify (Production)

```bash
# SSH to droplet
ssh insightpulse-odoo

# Check stack status
docker compose -f docker-compose.prod.yml ps

# Internal health check
docker compose -f docker-compose.prod.yml exec -T odoo bash -lc \
  "curl -sS -o /dev/null -w '%{http_code}\n' http://localhost:8069/web/login"

# Assets check
docker compose -f docker-compose.prod.yml exec -T odoo bash -lc \
  "curl -sS -o /dev/null -w '%{http_code}\n' http://localhost:8069/web/assets/debug/web.assets_backend.js"
```

---

## 9. References

- [Ship Verification Runbook](../ops/SHIP_VERIFICATION.md)
- [End State JSON](./aiux_ship_end_state.v1.1.0.json)
- [Fresh Redeploy PRD](./ODOO18_DO_FRESH_REDEPLOY.md)

---

*Last updated: 2026-01-08*
