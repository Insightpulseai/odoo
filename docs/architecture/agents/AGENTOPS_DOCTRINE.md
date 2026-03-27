# AgentOps Doctrine

> Evaluation-gated deployment, observability, and release posture for all assistant surfaces.
> SSOT: `ssot/governance/agentops_policy.yaml`, `ssot/governance/copilot_release_stages.yaml`

---

## Release Doctrine

### Evaluation-Gated Deployment Is Mandatory

No assistant surface reaches production without passing its evaluation pack. This is non-negotiable.

### Rollout Model

```
Pre-Merge CI
  -> Staging Validation (eval pack + smoke tests)
  -> Gated Production (canary / feature flag / blue-green)
```

| Stage | Gate | Owner |
|-------|------|-------|
| Pre-merge CI | Lint, type-check, unit tests, YAML validation | Automated |
| Staging validation | Eval pack pass, integration smoke tests, manual review | Agent owner + reviewer |
| Gated production | Canary rollout, feature flag, blue-green swap | Platform operator |

### Safe Rollout Strategies

| Strategy | When to Use |
|----------|------------|
| **Canary** | Default for agent model or prompt changes |
| **Feature flag** | New capabilities that need gradual exposure |
| **Blue-green** | Infrastructure changes (container, gateway, endpoint) |

---

## Observability Contract

### Observe -> Act -> Evolve

Every assistant surface must produce:

| Signal | Implementation | Purpose |
|--------|---------------|---------|
| **Logs** | Structured JSON to App Insights | Debugging, audit trail |
| **Traces** | Correlation IDs across MCP/A2A calls | End-to-end request tracking |
| **Metrics** | Latency, throughput, error rate, eval scores | SLO monitoring |

### Required Metrics Per Surface

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| P95 response latency | < 5s (advisory), < 10s (action) | > 2x target |
| Error rate | < 1% | > 5% |
| Eval score (per-surface) | > 0.70 (staging gate) | < 0.60 (block deploy) |
| Groundedness score | > 0.80 | < 0.65 |

### Audit Trail

- All copilot interactions logged to `ipai.copilot.audit`
- Append-only — no deletes
- Fields: user, company, surface, intent, response summary, confidence, model, latency, correlation_id

---

## Release Stages

| Stage | Description | Gate |
|-------|-------------|------|
| `dev` | Local development, no eval required | None |
| `staging` | Eval pack must pass, integration tests green | Eval score > 0.70 |
| `internal_beta` | Trusted internal users, monitoring active | Manual approval + eval pass |
| `limited_ga` | Selected customers, SLO baseline established | SLO met for 7 days |
| `ga` | General availability | SLO met for 30 days + privacy docs + Partner Center |

### Current Surface Stages

| Surface | Current Stage | Next Gate |
|---------|--------------|-----------|
| Odoo Copilot | `internal_beta` | Eval pack creation |
| Diva Copilot | `internal_beta` | Eval pack creation |
| Studio Copilot | `dev` | PRD finalization |
| Genie | `dev` | Semantic layer wiring |
| Document Intelligence | `dev` | Extraction accuracy baseline |

---

## Registry Policy

Registries (agent registry, tool registry, model registry) are deferred until scale justifies them. Current state uses:
- SSOT YAML files for intended state
- Azure AI Foundry for runtime tool/model management
- No custom registry service

When to introduce a registry service:
- More than 10 active agent surfaces
- More than 50 registered tools
- Multi-team concurrent development requiring versioned discovery

---

## SSOT References

- AgentOps policy: `ssot/governance/agentops_policy.yaml`
- Release stages: `ssot/governance/copilot_release_stages.yaml`
- Per-surface status: `ssot/agents/diva_copilot.yaml#release`
- Go-live checklist: `docs/architecture/GO_LIVE_CHECKLIST.md`

---

*Last updated: 2026-03-24*
