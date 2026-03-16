# N8N_AUTOMATION_CONTRACT.md
# Cross-boundary contract: n8n ↔ SSOT taskbus (ops.runs)
#
# Governs: automations/n8n/ ↔ supabase/functions/ ↔ Odoo (SoR) ↔ work.* (SoW)
# Created: 2026-03-01
# Branch:  feat/taskbus-agent-orchestration
# SSOT:    ssot/integrations/n8n.yaml

## 1. Boundary Diagram

```
External Triggers
  │  POST /webhook/{uuid}   (Slack retry, GitHub, BIR scheduler, OCR callback)
  │  Cron (built-in n8n)
  │  Manual trigger (n8n UI / API)
  │
  ▼
automations/n8n/  (self-hosted Docker — n8n.insightpulseai.com)
  │
  │  1. Verify webhook (Header-Auth credential or HMAC)
  │  2. Execute workflow nodes
  │  3. Write ops.run row (idempotency_key = n8n:workflow:{id}:{exec_id})
  │
  ▼
Supabase ops.runs  (SSOT — single append-only queue)
  │
  │  pg_cron / realtime → worker picks up run
  │
  ▼
Worker / Agent  (SoW boundary — all business logic here)
  │
  ├─→  Odoo XML-RPC/JSON-RPC  (SoR — writes only via approved run)
  ├─→  work.*                  (SoW — task state only via approved run)
  └─→  Slack / GitHub response (async result delivery)
```

## 2. Integration Model

n8n is **execution fabric**, not SSOT.

| What n8n IS | What n8n is NOT |
|-------------|-----------------|
| Automation trigger processor | System of record |
| Workflow orchestration engine | Source of durable state |
| HTTP/API glue for integrations | Direct writer to Odoo DB |
| Temporal execution context | Replacement for ops.runs audit trail |

**Golden rule**: Any durable side effect of an n8n workflow MUST be represented as an `ops.runs` row so it is auditable, replayable, and dedup-safe.

## 3. Workflow-as-Code (SSOT)

Workflow JSON files in `automations/n8n/workflows/` are the **authoritative definition** of automation logic.

```
automations/n8n/
├── workflows/
│   ├── 01-health-check.json
│   ├── 02-git-operations-hub.json
│   ├── 03-finance-close-orchestrator.json
│   ├── 04-bir-compliance.json
│   ├── 05-github-oauth-callback.json
│   ├── control-plane/
│   ├── integration/
│   └── claude-ai-mcp/
├── CREDENTIALS.md          ← Required: declares credential names
├── docs/
└── templates/
```

**Workflow import rule**: Any workflow imported via the n8n UI must be exported and committed to `automations/n8n/workflows/` before being treated as canonical. Workflows that exist only in the n8n database are non-SSOT and may be deleted without warning during disaster recovery.

## 4. Idempotency Contract

n8n retries failed workflows and webhooks may be re-delivered. Idempotency prevents duplicate taskbus runs.

| Source | Idempotency key format |
|--------|------------------------|
| Webhook trigger | `n8n:workflow:{workflow_id}:{execution_id}` |
| Scheduled cron | `n8n:cron:{workflow_id}:{scheduled_timestamp_utc}` |
| Manual trigger | `n8n:manual:{workflow_id}:{triggered_at_unix_ms}` |

The `ops.runs.idempotency_key` column has a `UNIQUE` constraint. Duplicate `INSERT` calls silently apply `ON CONFLICT DO NOTHING`.

## 5. SSOT Boundary Rules

| Rule | Rationale |
|------|-----------|
| n8n workflows NEVER write to Odoo directly via Postgres | Preserves SoR write isolation |
| n8n workflows NEVER write to `work.*` or `ops.*` via raw SQL | SoW boundary — only authorized workers write |
| All durable state flows through `ops.runs` | Single audit trail, dedup, replay |
| Credential values NEVER appear in workflow JSON | Secrets in n8n credential store + Supabase Vault |
| Webhooks require authentication (Header-Auth or HMAC) | Prevents unauthorized trigger execution |
| Workflow files must be committed to repo | Workflow-as-code doctrine; no UI-only workflows in production |

## 6. Secrets

| Secret name | Purpose | Store |
|-------------|---------|-------|
| `n8n_api_key` | n8n REST API key for external triggering (CI, agents) | Supabase Vault + os_keychain |
| `n8n_webhook_secret` | Shared secret for Header-Auth credential on webhook nodes | Supabase Vault + n8n credential store |

See: `ssot/secrets/registry.yaml` entries `n8n_api_key`, `n8n_webhook_secret`

**n8n credential store**: Runtime credentials (Odoo API, Supabase IPAI, GitHub OAuth2, Anthropic)
are stored in the n8n credential database. Credential **names** are declared in
`automations/n8n/CREDENTIALS.md`. Credential **values** are NOT in git.

## 7. Three Canonical Integration Scenarios

### 7.1 BIR Compliance Filing (04-bir-compliance.json)

```
n8n Cron Trigger (monthly deadline)
  → Fetch BIR deadlines from Supabase (ops.bir_deadlines)
  → Prepare filing data from Odoo (XML-RPC read-only)
  → Write ops.run(job_type='bir.file', idempotency_key='n8n:cron:...')
  → Worker: generate BIR forms, submit via PH eFPS/eBIRForms
  → Write ops.run_event(status='completed')
  → Post Slack notification (response_url from run input)
```

### 7.2 Expense OCR Trigger (expense_receipt_capture.json)

```
n8n Webhook (POST /webhook/{uuid}) ← Odoo sends upload notification
  → Verify Header-Auth credential
  → Extract file metadata from payload
  → Write ops.run(job_type='ocr.receipt', input={file_url, expense_id})
  → Worker: call OCR service, extract fields, update Odoo expense record
```

### 7.3 GitHub → Odoo Bridge (02-git-operations-hub.json)

```
n8n Webhook (POST /webhook/{uuid}) ← GitHub webhook event
  → Verify HMAC-SHA256 (X-Hub-Signature-256) via HTTP header check node
  → Route by event type (push/PR/issue)
  → Write ops.run(job_type='github.event.*', source='github')
  → Worker: map GitHub event to Odoo project task / timesheet entry
```

## 8. Local Development

```bash
# Start n8n locally (Docker Compose)
docker compose -f deploy/odoo-prod.compose.yml up n8n -d

# n8n UI: http://localhost:5678
# Import workflows from automations/n8n/workflows/

# Required env vars for n8n container (set in compose .env)
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=<from os_keychain>
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<from Supabase Vault>
```

## 9. Tests / Validation

```bash
# Contract validation (from repo root)
python3 scripts/ci/check_n8n_workflows_ssot.py

# Covers:
#   §1  Workflow directory structure
#   §2  No hardcoded secrets in workflow JSON
#   §3  No direct Odoo PostgreSQL access
#   §4  n8n integration register exists and has required fields
#   §5  n8n registered in ssot/integrations/_index.yaml
#   §6  CREDENTIALS.md declaration file exists
```

## 10. Deployment

n8n runs as a Docker container on the `odoo-production` DigitalOcean droplet (SGP1).

Compose file: `deploy/odoo-prod.compose.yml`

Env vars must be set in the compose `.env` (not committed to git) and in Supabase Vault.
See `ssot/secrets/registry.yaml` entries `n8n_api_key`, `n8n_webhook_secret`.

## 11. Contract Enforcement

**SSOT files** (these are the authoritative sources — update them, not this doc):
- `ssot/integrations/n8n.yaml` — components, boundary rules, risk flags
- `ssot/integrations/_index.yaml` — integration registration
- `automations/n8n/CREDENTIALS.md` — required credential names

**CI gate**: `.github/workflows/ssot-gates.yml` job `n8n-workflows-ssot` runs
`scripts/ci/check_n8n_workflows_ssot.py` on every change to `automations/n8n/**`
or `ssot/integrations/n8n.yaml`. CI fails if:
- Workflow directory is missing
- Workflow JSON contains hardcoded secrets
- Any workflow Postgres node targets the Odoo DB host directly
- n8n integration register is missing required fields
- CREDENTIALS.md is absent

Cross-boundary rules are enforced by `docs/architecture/SSOT_BOUNDARIES.md`.
