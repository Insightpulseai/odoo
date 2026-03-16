# AI Gateway Configuration

> Version: 1.0.0
> Last updated: 2026-03-15
> Status: Phase 2 — Not yet configured
> Canonical repo: `infra`

## Purpose

Azure AI Foundry AI Gateway provides centralized model governance, rate limiting, quota management, and unified monitoring for all AI endpoints.

## Target Configuration

### Gateway Settings

| Setting | Value | Rationale |
|---------|-------|-----------|
| Rate limit (per user) | 20 req/min | Prevent abuse while allowing normal workflow |
| Rate limit (global) | 200 req/min | Platform-wide burst protection |
| Token limit (per request) | 4096 output tokens | Sufficient for advisory responses |
| Model routing | gpt-4.1 primary | Current agent model |
| Fallback model | gpt-4.1-mini | Cost-effective fallback |
| Content safety | Enabled (4 categories) | Hate, Sexual, Violence, SelfHarm |
| Logging | All requests | Full audit trail |
| Caching | Disabled | Each request is user-specific |

### Quota Allocation

| Consumer | Daily token budget | Priority |
|----------|-------------------|----------|
| Odoo Copilot (Discuss) | 500K tokens | High |
| Docs Widget | 200K tokens | Medium |
| API consumers | 300K tokens | Medium |
| Evaluation harness | 100K tokens | Low |

### Monitoring Metrics

| Metric | Alert threshold | Channel |
|--------|----------------|---------|
| Request latency p95 | > 10s | Slack #ops-alerts |
| Error rate | > 5% | Slack #ops-alerts |
| Daily token usage | > 80% budget | Slack #ops-alerts |
| Content safety triggers | Any | Slack #security |
| Rate limit hits | > 50/hour | Slack #ops-alerts |

### Implementation Steps

1. Enable AI Gateway in Foundry project `data-intel-ph`
2. Configure rate limits per the table above
3. Set model routing rules
4. Enable logging to Log Analytics workspace
5. Configure alerts in Azure Monitor
6. Validate with test traffic

### Prerequisites

- Foundry project API access (currently blocked — requires `https://ai.azure.com` audience token)
- Azure Monitor workspace
- Slack webhook for alerts

### Current Blocker

The Foundry project API requires an audience token for `https://ai.azure.com` which cannot be obtained via `az cli`. Gateway configuration must be done via the Foundry portal UI until API access is resolved.

### Evidence Required Before Phase 2 Promotion

- [ ] Gateway enabled screenshot
- [ ] Rate limit configuration evidence
- [ ] Quota allocation evidence
- [ ] Alert configuration evidence
- [ ] Test traffic validation (10 requests, all within limits)
