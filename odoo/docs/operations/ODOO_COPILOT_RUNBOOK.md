# Odoo Copilot — Runbook

> Version: 1.0.0
> Last updated: 2026-03-14
> Stage: Internal Prototype (Stage 1)

## Service Overview

| Property | Value |
|----------|-------|
| Service | IPAI Odoo Copilot |
| Runtime | Azure AI Foundry (project: `data-intel-ph`) |
| Odoo module | `ipai_odoo_copilot` |
| Consumption | Discuss bot, HTTP API, docs widget |
| Auth | API key (Stage 1) → Managed identity (Stage 2) |

## Health Check

### Foundry connectivity

```bash
# From Odoo container
docker compose exec web python3 -c "
from odoo import api, SUPERUSER_ID
import odoo
db = odoo.sql_db.db_connect('odoo_dev')
with db.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    svc = env['ipai.foundry.service']
    print(svc.test_connection())
"
```

### Odoo copilot endpoint

```bash
# Health endpoint
curl -s http://localhost:8069/api/health | python3 -m json.tool

# Chat endpoint (requires auth session)
curl -s -X POST http://localhost:8069/ipai/copilot/chat \
  -H 'Content-Type: application/json' \
  -b 'session_id=<session>' \
  -d '{"jsonrpc":"2.0","method":"call","params":{"prompt":"hello"}}' | python3 -m json.tool
```

### Docs widget proxy

```bash
# Health
curl -s http://localhost:3001/api/health | python3 -m json.tool

# Chat
curl -s -X POST http://localhost:3001/api/copilot/chat \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"hello"}' | python3 -m json.tool
```

## Common Issues

### Foundry returns empty response

**Symptoms:** `content: ""`, `blocked: true`, `reason: "No response from Foundry"`

**Check:**
1. Verify `AZURE_AI_FOUNDRY_API_KEY` is set in environment
2. Verify `AZURE_AI_FOUNDRY_ENDPOINT` is correct
3. Verify agent ID exists in Foundry project
4. Check Foundry service health in Azure portal

### Odoo audit sidecar fails

**Symptoms:** Console warning `Odoo audit sidecar failed: <error>`

**Impact:** Non-blocking — Foundry responses still delivered. Audit records not written.

**Check:**
1. Verify `ODOO_URL` is reachable from docs proxy
2. Verify `IPAI_COPILOT_SERVICE_KEY` matches on both sides
3. Check Odoo logs for controller errors

### Rate limiting triggered

**Symptoms:** `429 Too Many Requests` or `{ error: 'Too many requests...' }`

**Limits:**
- Docs widget: 10 req/min per IP
- Discuss bot: 2s minimum between responses

### Mock mode active

**Symptoms:** Responses prefixed with `[Mock]`

**Cause:** Neither `AZURE_AI_FOUNDRY_*` nor `ODOO_URL` + `IPAI_COPILOT_SERVICE_KEY` configured.

**Fix:** Set environment variables per `.env.example`

## Escalation

| Severity | Condition | Action |
|----------|-----------|--------|
| P1 | Foundry endpoint unreachable | Check Azure status page, verify managed identity/API key |
| P2 | Audit writes failing | Check Odoo container health, verify service key |
| P3 | High latency (>8s p95) | Check Foundry agent complexity, thread creation rate |
| P4 | Mock mode in staging | Configure environment variables |

## Monitoring (Stage 2+)

Not yet instrumented. When Stage 2 begins:
- Add App Insights tracing to `foundry_service.py`
- Add correlation IDs to audit records
- Forward Entra sign-in/audit logs to Log Analytics
- Create latency/error dashboard
