# Copilot Runtime Stage Policy

> Version: 1.1.0
> Last updated: 2026-03-14
> Reference: Microsoft SaaS startup architecture (Explore → Expand → Extract)
> Parent: `agents/foundry/ipai-odoo-copilot-azure/runtime-contract.md` (C-30)

## Stage Model

Adapted from Microsoft's startup architecture guidance. Each stage defines what technical shortcuts are allowed and what promotion gates must be passed before advancing.

---

## Stage 1 — Explore (Current)

**Objective:** Validate the copilot works end-to-end with real users.

### Allowed

- API key auth for Foundry (non-prod only)
- Single-turn chat (no session persistence)
- Mock fallback when no backend configured
- Fire-and-forget audit (failures logged but don't block responses)
- Minimal error handling (log and return empty)
- Express proxy without auth middleware (dev only)

### Not Yet Required

- Durable conversation history
- Real tool wiring (Odoo record mutations)
- Grounded retrieval (RAG)
- Production observability
- Eval harness
- Citation in responses
- Private networking

### Identity Posture (Stage 1)

- Entra tenant: `ceoinsightpulseai.onmicrosoft.com` (Free tier, cloud-only)
- API key bootstrap: tolerated temporarily
- MFA: not yet enforced (acceptable for prototype, must fix before Stage 2)
- See `ENTRA_IDENTITY_BASELINE_FOR_COPILOT.md`

### Promotion Gate → Stage 2

- [ ] End-to-end chat works: Foundry primary path returns real responses
- [ ] Odoo audit sidecar writes records successfully
- [ ] Fallback path (Odoo-only) works when Foundry is down
- [ ] Mock path works when neither backend is configured
- [ ] No secrets in client bundle (verified by build inspection)
- [ ] `py_compile` passes for all Odoo module files

---

## Stage 2 — Expand

**Objective:** Add the capabilities that make the copilot genuinely useful.

### Required Additions

| Capability | Implementation |
|-----------|---------------|
| Auth upgrade | Managed identity / Entra SP replaces API key |
| Session persistence | Thread ID stored per user/conversation |
| Grounding | Azure AI Search index attached to agent |
| Tool contracts | Read-only tools first, write tools behind `draft_only` |
| Observability | App Insights traces for all Foundry calls |
| Eval harness | Automated evaluation of response quality |
| Rate limiting | Per-user limits in Odoo controller |

### Allowed Shortcuts

- Single Azure region
- Shared compute (no dedicated Foundry capacity)
- Manual eval review (not fully automated)

### Not Yet Required

- Private endpoints / VNet integration
- Multi-region failover
- PII detection / redaction pipeline
- Formal SLA with uptime targets

### Identity Posture (Stage 2)

- MFA enforced for all admin/privileged users
- Converged Authentication methods policy active (legacy policy retired)
- Managed identity / Entra service principal replaces API key for Foundry
- Conditional Access policy for admin operations
- Dedicated service principal for CI/CD pipeline

### Promotion Gate → Stage 3

- [ ] Managed identity auth working in staging
- [ ] MFA enforced for all admin users
- [ ] Converged auth methods policy active
- [ ] Eval pass rate > 80% on standard test set
- [ ] Observability dashboard live with latency/error metrics
- [ ] At least one grounded tool path working (e.g. record lookup)
- [ ] Session persistence tested across browser refresh
- [ ] Audit retention policy defined

---

## Stage 3 — Hardened Production

**Objective:** Enterprise-grade copilot with full controls.

### Required

| Capability | Implementation |
|-----------|---------------|
| Private networking | VNet integration for Foundry endpoint |
| Managed identity only | No API keys in any environment |
| Citation-first retrieval | Every grounded response includes source references |
| Full tool wiring | Read + write tools with safety controls |
| Compliance posture | PII handling, audit retention, data residency |
| SLA | Contractually defined uptime and response time targets |
| Disaster recovery | Documented failover and recovery procedures |

### No Shortcuts Allowed

- All security controls enforced
- All observability in place
- All eval gates passing
- All audit requirements met

---

## Stage Mapping to Current State

| Component | Current Stage | Notes |
|-----------|--------------|-------|
| `foundry_service.py` (Odoo) | Stage 1 | `chat_completion()` implemented, API key auth |
| `copilot_bot.py` (Discuss) | Stage 1 | Calls `chat_completion()`, no session persistence |
| `controllers/main.py` (HTTP API) | Stage 1 | Both user and service routes working |
| `server.ts` (docs proxy) | Stage 1 | Foundry primary + Odoo fallback + mock |
| `copilot_audit.py` (audit) | Stage 1 | Fire-and-forget audit records |
| Auth posture | Stage 1 | API key + IMDS fallback |
| Grounding | Not started | Azure AI Search index exists but not wired |
| Tool wiring | Not started | `read_only_mode` exists but no tools defined |
| Observability | Not started | Console logging only |
| Eval harness | Not started | — |

---

## Decision Framework

When deciding whether to add a capability now or defer:

1. **Does it block Stage 1 validation?** → Add now
2. **Does it improve Stage 1 quality without adding complexity?** → Add now
3. **Is it a Stage 2 requirement?** → Defer until Stage 1 gates pass
4. **Is it a Stage 3 hardening concern?** → Defer until Stage 2 gates pass

Current priority: **pass all Stage 1 promotion gates**, then plan Stage 2 sprint.
