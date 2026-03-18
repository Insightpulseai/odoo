# n8n Automation Runbook

**Last Updated:** 2026-02-20
**Scope:** Operational procedures for n8n workflow management
**Automation-First:** CLI/API operations, UI only for OAuth flows

---

## Quick Reference

| **Task** | **Command** |
|---------|-------------|
| Export workflow | `curl -H "X-N8N-API-KEY:$N8N_API_KEY" https://n8n.insightpulseai.com/api/v1/workflows/{id} > workflows/{name}.json` |
| Import workflow | `curl -X POST -H "X-N8N-API-KEY:$N8N_API_KEY" -d @workflows/{name}.json https://n8n.insightpulseai.com/api/v1/workflows` |
| List active workflows | `curl -H "X-N8N-API-KEY:$N8N_API_KEY" https://n8n.insightpulseai.com/api/v1/workflows?filter=active` |
| Trigger manually | `curl -X POST -H "X-N8N-API-KEY:$N8N_API_KEY" https://n8n.insightpulseai.com/api/v1/workflows/{id}/execute` |
| View execution log | `curl -H "X-N8N-API-KEY:$N8N_API_KEY" https://n8n.insightpulseai.com/api/v1/executions/{id}` |

---

## Workflow Export/Import (Version Control)

### Export All Workflows

```bash
#!/bin/bash
# scripts/n8n/export_workflows.sh

set -euo pipefail

N8N_API_KEY="${N8N_API_KEY:?N8N_API_KEY required}"
N8N_URL="https://n8n.insightpulseai.com"
OUTPUT_DIR="automations/n8n/workflows"

workflows=$(curl -s -H "X-N8N-API-KEY:${N8N_API_KEY}" "${N8N_URL}/api/v1/workflows" | jq -r '.data[] | @base64')

for workflow in ${workflows}; do
  name=$(echo "${workflow}" | base64 -d | jq -r '.name' | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
  id=$(echo "${workflow}" | base64 -d | jq -r '.id')

  curl -s -H "X-N8N-API-KEY:${N8N_API_KEY}" "${N8N_URL}/api/v1/workflows/${id}" \
    | jq '.' > "${OUTPUT_DIR}/${name}.json"

  echo "✅ Exported: ${name}.json (id: ${id})"
done
```

### Import Workflow from JSON

```bash
#!/bin/bash
# scripts/n8n/import_workflow.sh <workflow-file.json>

set -euo pipefail

WORKFLOW_FILE="${1:?Workflow JSON file required}"
N8N_API_KEY="${N8N_API_KEY:?N8N_API_KEY required}"
N8N_URL="https://n8n.insightpulseai.com"

curl -X POST -H "X-N8N-API-KEY:${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @"${WORKFLOW_FILE}" \
  "${N8N_URL}/api/v1/workflows"

echo "✅ Imported workflow: ${WORKFLOW_FILE}"
```

---

## Workflow Management

### Activate/Deactivate

```bash
# Activate workflow
curl -X PATCH -H "X-N8N-API-KEY:${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"active": true}' \
  https://n8n.insightpulseai.com/api/v1/workflows/{id}

# Deactivate workflow
curl -X PATCH -H "X-N8N-API-KEY:${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"active": false}' \
  https://n8n.insightpulseai.com/api/v1/workflows/{id}
```

### Delete Workflow

```bash
curl -X DELETE -H "X-N8N-API-KEY:${N8N_API_KEY}" \
  https://n8n.insightpulseai.com/api/v1/workflows/{id}
```

---

## Execution & Monitoring

### Manual Trigger

```bash
# Trigger workflow with test data
curl -X POST -H "X-N8N-API-KEY:${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"data": {"test": true}}' \
  https://n8n.insightpulseai.com/api/v1/workflows/{id}/execute
```

### View Recent Executions

```bash
# List last 10 executions
curl -H "X-N8N-API-KEY:${N8N_API_KEY}" \
  'https://n8n.insightpulseai.com/api/v1/executions?limit=10&status=error'
```

---

## Idempotency & Retry

### Handling Failures

- **Transient errors (429, 500):** n8n auto-retries with exponential backoff
- **Data errors (invalid input):** No retry; fix data and re-trigger
- **Authentication errors (401, 403):** Refresh credentials, re-trigger

### Preventing Duplicate Runs

- Use **external_id** in payload for deduplication
- Query Supabase `ops.integration_state` before processing
- Update cursor/checkpoint after successful run

---

## Operational Playbooks

### Scenario 1: Workflow Fails Due to Rate Limit

**Symptoms:** Execution log shows HTTP 429 from Google API

**Resolution:**
1. Check rate limit quota in Google Cloud Console
2. Increase quota OR reduce workflow frequency
3. Re-trigger workflow manually after cooldown period
4. Monitor `ops.run_events` for quota usage patterns

### Scenario 2: OAuth Token Expired

**Symptoms:** Execution log shows HTTP 401 from Google API

**Resolution:**
1. Open n8n UI → Credentials → Find OAuth credential
2. Click "Reconnect" → Browser OAuth flow
3. Verify token refresh successful
4. Re-trigger workflow

### Scenario 3: Workflow Stuck in "Running" State

**Symptoms:** Workflow execution shows "running" for >30 minutes

**Resolution:**
1. Check n8n logs: `docker logs odoo-n8n-1 --tail 100`
2. If timeout: Kill execution via API
3. If stuck node: Debug node configuration
4. Re-trigger workflow after fix

---

## Audit Trail Compliance

**Required for Every Workflow:**
- [ ] Emits `ops.runs` entry at start
- [ ] Emits `ops.run_events` for each external API call
- [ ] Updates `ops.integration_state` with sync cursor
- [ ] No hardcoded credentials (uses credential references)
- [ ] Workflow JSON committed to git (no secrets)

**Verification:**
```sql
-- Check audit completeness for workflow executions
SELECT
  r.correlation_id,
  r.task_name,
  COUNT(e.id) AS event_count
FROM ops.runs r
LEFT JOIN ops.run_events e ON r.id = e.run_id
WHERE r.agent_id LIKE 'n8n-%'
  AND r.created_at >= NOW() - INTERVAL '7 days'
GROUP BY r.correlation_id, r.task_name
HAVING COUNT(e.id) = 0  -- Executions with no events (audit gap)
ORDER BY r.created_at DESC;
```

---

## Cross-References

- **Odoo Connector:** `automations/n8n/docs/ODOO_CONNECTOR.md`
- **Credentials Model:** `automations/n8n/docs/CREDENTIALS_MODEL.md`
- **Audit Trail:** `docs/architecture/AUTOMATION_AUDIT_TRAIL.md`
- **n8n Spec:** `spec/odoo-sh/prd.md` (FR6: n8n Workflow Automation Layer)
