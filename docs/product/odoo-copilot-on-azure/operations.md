# Operations

> Health monitoring, evaluations, tracing, and rollout/rollback for Odoo Copilot.

## Health Checks

### Copilot Health Endpoint

`GET /ipai/copilot/health` returns:

```json
{
  "status": "ok",
  "copilot_module": "installed",
  "actions_module": "installed",
  "foundry_reachable": true,
  "model_deployment": "gpt-4.1",
  "search_index": "connected",
  "latency_ms": 230
}
```

### Dependency Health

| Dependency | Check | Failure mode |
|------------|-------|-------------|
| Azure AI Foundry | Token acquisition + model ping | Copilot returns "service unavailable" |
| Azure AI Search | Index status query | Copilot falls back to record-only grounding |
| Odoo ORM | Standard Odoo health | Entire ERP unavailable |
| Entra ID | Token refresh | Auth failures, copilot inaccessible |

## Evaluations

### Foundry-native Evaluations (target)

When running on Foundry Agent Service, evaluations use Foundry's built-in
evaluation framework:

| Metric | Type | Target |
|--------|------|--------|
| Groundedness | Automatic | >= 0.85 |
| Relevance | Automatic | >= 0.80 |
| Coherence | Automatic | >= 0.90 |
| Tool call accuracy | Custom (dataset) | >= 0.90 |
| Action safety | Custom (red-team dataset) | 0 unsafe actions |

Evaluation datasets live in the Foundry project `data-intel-ph` and are
versioned alongside agent definitions.

### Offline Evaluations

For prompt-only mode, evaluations run as batch scripts against recorded
interaction logs:

```
scripts/copilot/eval_batch.py \
  --dataset ssot/odoo/copilot_eval_dataset.jsonl \
  --model gpt-4.1 \
  --output docs/evidence/$(date +%Y%m%d-%H%M)/copilot-eval/
```

## Tracing

### Foundry Tracing (target)

Foundry Agent Service provides per-request tracing:
- Prompt tokens, completion tokens, total latency
- Tool call sequence with individual latencies
- Knowledge retrieval results and relevance scores
- Model reasoning steps

Traces are queryable in the Foundry project portal and exportable to Azure
Monitor.

### Application-level Tracing (current)

In prompt-only mode, the copilot module logs:
- Request/response pairs to `ipai.copilot.audit.log`
- Tool call inputs/outputs
- Error tracebacks
- Timing per tool call

Logs are available in Odoo server logs and optionally forwarded to Azure
Monitor via the container's stdout/stderr pipeline.

## Monitoring and Alerts

| Signal | Source | Alert condition |
|--------|--------|----------------|
| Copilot error rate | Audit log / Azure Monitor | > 5% error rate over 5 min |
| Foundry latency P95 | Foundry tracing / app logs | > 10s |
| Tool call failure rate | Audit log | > 10% failure rate over 15 min |
| Content filter triggers | Azure AI Content Safety | Any trigger (informational) |
| Token consumption | Foundry usage metrics | > daily budget threshold |

## Rollout / Rollback

### Feature Flag

Copilot availability is controlled by `ir.config_parameter`:

```
ipai_copilot.enabled = True/False
ipai_copilot.allowed_groups = base.group_user
ipai_copilot.beta_groups = ipai_copilot.group_beta_tester
```

### Staged Rollout

| Stage | Audience | Duration | Gate |
|-------|----------|----------|------|
| 1. Internal | Platform team only | 1 week | No P0 bugs, eval scores meet threshold |
| 2. Beta | `group_beta_tester` users | 2 weeks | Error rate < 2%, user feedback positive |
| 3. GA | All `group_user` members | Ongoing | Monitoring stable |

### Rollback Procedure

1. Set `ipai_copilot.enabled = False` via `ir.config_parameter`
2. This immediately hides the copilot UI for all users
3. No module uninstall required -- the flag controls visibility
4. Investigate, fix, re-enable

For model-level rollback (e.g., bad model version):
1. Update `AZURE_OPENAI_DEPLOYMENT` env var to point to previous deployment
2. Restart the container app revision
3. Verify via health endpoint
