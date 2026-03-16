# Telemetry Contract

> Version: 1.0.0
> Last updated: 2026-03-15
> Parent: runtime-contract.md (C-30)
> Status: Phase 2C — Not yet active

## Purpose

Define the observability requirements for the copilot runtime. Every request must be traceable end-to-end from UI to Foundry and back. Telemetry enables incident response, performance optimization, and release gating.

## Telemetry Sink

| Property | Value |
|----------|-------|
| Service | Azure Application Insights |
| Connection | `APPINSIGHTS_CONNECTION_STRING` env var |
| Degradation | Graceful — telemetry failure never blocks chat |

## Correlation Model

Every request carries a `request_id` (UUID v4) generated at the entry point:

```
Chat Widget → POST /api/copilot/chat (request_id in header)
    → server.ts logs request_id
    → Foundry thread created (thread_id)
    → Response returned with request_id

Odoo Discuss → copilot_bot intercepts (request_id generated)
    → foundry_service.chat_completion(request_id)
    → audit record includes request_id
    → thread_id logged

Odoo HTTP API → POST /ipai/copilot/chat (request_id generated)
    → controller passes request_id to service
    → audit record includes request_id
```

## Event Taxonomy

### Request Events

| Event | When | Dimensions |
|-------|------|-----------|
| `copilot_chat_request` | Every inbound chat request | request_id, user_id, surface, channel, app_roles, mode |
| `copilot_chat_response` | Every completed response | request_id, latency_ms, prompt_tokens, completion_tokens, retrieval_hit_count |
| `copilot_chat_fallback` | Foundry primary fails, using Odoo/mock | request_id, fallback_path, error_reason |

### Safety Events

| Event | When | Dimensions |
|-------|------|-----------|
| `copilot_blocked` | Request blocked by policy | request_id, reason, user_id, surface |
| `copilot_redirected` | Off-topic redirect triggered | request_id, original_intent, redirect_target |
| `copilot_safety_trigger` | Content safety filter fired | request_id, category, severity |

### Tool Events

| Event | When | Dimensions |
|-------|------|-----------|
| `copilot_tool_request` | Agent requests tool execution | request_id, tool_name, arguments_hash |
| `copilot_tool_permitted` | Tool execution approved | request_id, tool_name, latency_ms |
| `copilot_tool_denied` | Tool not in permitted_tools | request_id, tool_name, reason |
| `copilot_tool_error` | Tool execution failed | request_id, tool_name, error_type |

### System Events

| Event | When | Dimensions |
|-------|------|-----------|
| `copilot_health_probe` | Nightly health check | status, latency_ms, auth_mode |
| `copilot_auth_failure` | Auth unavailable or rejected | auth_mode, error_code |
| `copilot_run_timeout` | Foundry run exceeded 30s | request_id, thread_id, run_id |

## Dimensions Reference

| Dimension | Type | Source |
|-----------|------|--------|
| request_id | string (UUID) | Generated at entry point |
| user_id | string | Context envelope (anonymized for external telemetry) |
| surface | string | Context envelope |
| channel | string | discuss / api / widget |
| app_roles | string[] | Context envelope |
| mode | string | PROD-ADVISORY / PROD-ACTION |
| latency_ms | int | Measured from request start to response |
| prompt_tokens | int | From Foundry run usage |
| completion_tokens | int | From Foundry run usage |
| retrieval_hit_count | int | AI Search results count |
| fallback_path | string | foundry / odoo / mock |
| tool_name | string | Tool being executed |
| blocked | bool | Whether request was blocked |
| reason | string | Block/denial reason |

## SLO Targets

| Metric | Target | Alert threshold |
|--------|--------|----------------|
| Response latency p50 | < 3s | > 5s |
| Response latency p95 | < 10s | > 15s |
| Error rate | < 2% | > 5% |
| Availability | > 99% | < 98% |
| Safety violation rate | 0% | > 0% |
| Tool execution success | > 95% | < 90% |

## Dashboard Panels

### Operations Dashboard

1. Request volume (by channel, surface)
2. Response latency (p50, p95, p99)
3. Error rate (by type)
4. Fallback usage
5. Active users (by surface)

### Safety Dashboard

1. Blocked requests (by reason)
2. Safety trigger events (by category)
3. Redirect events (off-topic rate)
4. PII attempt detections

### Tool Dashboard

1. Tool execution volume (by tool)
2. Tool permission denials
3. Tool execution latency
4. Tool error rate

## Implementation Rules

1. Telemetry is **fire-and-forget** — never blocks the request path
2. Telemetry failures are **logged locally** but never surfaced to users
3. User IDs in external telemetry are **anonymized** (hash, not raw)
4. PII (prompts, responses) is **never sent** to App Insights — only metadata
5. Connection string comes from env var — **never hardcoded**
6. Telemetry can be **disabled entirely** via env var `COPILOT_TELEMETRY_ENABLED=false`

## Release Gate Integration

The release promotion runbook must check:

- [ ] App Insights receiving events (> 0 events in last 24h)
- [ ] Latency p95 < 15s over last 7 days
- [ ] Error rate < 5% over last 7 days
- [ ] 0 safety violations in last 7 days
- [ ] Dashboard accessible and rendering

No release promotion without telemetry confirmation.

## Dependencies

- `context-envelope-contract.md` — provides user_id, surface, app_roles, mode
- `infra/docs/architecture/AI_GATEWAY_CONFIGURATION.md` — gateway-level monitoring
- `infra/docs/runbooks/RELEASE_PROMOTION_RUNBOOK.md` — references telemetry gates
