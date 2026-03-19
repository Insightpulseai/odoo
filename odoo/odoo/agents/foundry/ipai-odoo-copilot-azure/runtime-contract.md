# IPAI Odoo Copilot — Runtime Contract

> Contract ID: C-30
> Version: 1.3.0
> Last updated: 2026-03-14

## Foundry Project Facts

| Property | Value |
|----------|-------|
| Project | `data-intel-ph` |
| Parent resource | `data-intel-ph-resource` |
| Project endpoint | `https://data-intel-ph-resource.services.ai.azure.com/api/projects/data-intel-ph` |
| Resource group | `rg-data-intel-ph` |
| Location | `eastus2` |
| Subscription | `Azure subscription 1` |
| Service principal | `sp-ipai-azdevops` (Contributor, inherited) |
| AI Search connection | `srchipaidev8tlstu` → `https://srch-ipai-dev.search.windows.net/` |

### Identities with Foundry Access

| Identity | Type | Role |
|----------|------|------|
| `ceo_insightpulseai.com#EXT#` | Human (external) | Owner + Azure AI User |
| `s224670304_deakin.edu.au#EXT#` | Human (external) | Owner |
| `sp-ipai-azdevops` | Service principal | Contributor |

### Endpoint Note

The project endpoint uses the `/api/projects/` path format. The adapter (`foundry_service.py`) currently uses the OpenAI-compat threads/runs surface. Stage 2 should evaluate migrating to the Foundry-native project endpoint for agent operations, tracing, and evaluations.

## Publish Lifecycle

1. **Agent Definition**: Created in Azure AI Foundry portal under project `data-intel-ph`
2. **Knowledge Binding**: Azure AI Search index `ipai-knowledge-index` attached for RAG
3. **Odoo Registration**: Agent name configured in Settings > IPAI Copilot > Agent Name
4. **Health Verification**: `test_connection()` + `ensure_agent()` validate the binding
5. **Nightly Probe**: Cron job runs `nightly_healthcheck()` daily at 02:00 UTC

## Consumption Protocol

### Odoo Discuss Bot (Primary)
- User sends DM to IPAI Copilot partner in Discuss
- `copilot_bot.py` intercepts via `_message_post_after_hook`
- Calls `FoundryService.chat_completion()` with message + conversation history
- Response posted back as copilot partner message

### HTTP API
- `POST /ipai/copilot/chat` (JSON-RPC, auth=user)
- Body: `{"prompt": "...", "record_model": "...", "record_id": 123}`
- Response: `{"content": "...", "blocked": false, "reason": ""}`
- Audit record written for every request

### Documentation Widget
- `documentaion/` repo chat widget calls `POST /api/copilot/chat`
- Server-side Express proxy forwards to Foundry threads/runs API
- No client-side API key exposure

## Auth Chain

**Entra Tenant**: `ceoinsightpulseai.onmicrosoft.com` (Free tier, cloud-only, 2 users, 3 app registrations)

```
Human access:
  Admin → Entra user + MFA (not yet enforced) → Azure portal / Foundry

Machine access (current — Stage 1):
  Odoo User → Odoo Session → FoundryService
                                 ↓
                      IMDS (managed identity) → Azure AI Foundry
                      OR
                      AZURE_FOUNDRY_API_KEY env var → Azure AI Foundry

Machine access (target — Stage 2):
  Odoo Container App → Managed identity → Azure AI Foundry (no API key)
  Docs Express proxy → Entra service principal → Azure AI Foundry
  CI/CD pipeline → Entra service principal → Foundry deployment
```

See `docs/architecture/ENTRA_IDENTITY_BASELINE_FOR_COPILOT.md` for full identity assessment.
See `docs/architecture/FOUNDRY_ODOO_AUTH_AND_ENDPOINT_POLICY.md` for auth preference order.

## Safety Posture

- **read_only_mode** (default: ON): Agent cannot execute write operations
- **memory_enabled** (default: OFF): No conversation persistence for privacy
- All interactions audited in `ipai.copilot.audit` model
- Rate limiting: 2s minimum between Discuss responses, 10 req/min for HTTP API

## Allowed Modes

| Mode | Write Operations | Odoo Mutations | Default |
|------|-----------------|----------------|---------|
| read_only | Blocked | None | Yes |
| draft_only | Surfaced as drafts | Drafts only | No |
| full_access | Executed | Direct writes | No |

## SLA

- Response time: < 30s (poll timeout)
- Availability: Best-effort (depends on Azure AI uptime)
- Fallback: Empty response + audit log entry on failure

---

## Runtime Maturity Stages

### Stage 1 — Prototype / Explore (current)

- Server-side only — no client-side credentials
- API key allowed for non-prod bootstrap
- Minimal tool wiring (chat completion only)
- No durable conversation persistence
- Fast iteration prioritized over hardening
- Promotion gate: end-to-end chat works through both Foundry primary and Odoo fallback paths

### Stage 2 — Expand

- Foundry project endpoint preferred over raw OpenAI-compat surface
- Managed identity / Entra-backed auth replaces API key
- Grounding via Azure AI Search index attached
- Tool contracts defined (read-only tools first, then write tools behind `draft_only` mode)
- App Insights / tracing enabled for all Foundry calls
- Eval harness required before promoting tool-use capabilities
- Durable session/conversation persistence added
- Promotion gate: observability dashboard live, eval pass rate > 80%

### Stage 3 — Hardened Production

- Private networking (VNet integration) where required
- Durable state and retrieval substrate fully operational
- Enterprise controls: audit retention policy, PII handling, compliance posture
- No reliance on API key — managed identity only
- Citation-first retrieval for all grounded responses
- Full tool wiring with production safety controls
- Promotion gate: security review complete, SLA contractually defined

---

## Identity and Authentication

The hosted runtime must prefer Microsoft Entra-backed server-side authentication.

**Preference order:**
1. Managed identity (DefaultAzureCredential / IMDS)
2. Service principal / app registration (client credentials)
3. Temporary API key bootstrap for controlled non-production use

**Hard rules:**
- Browser-side credentials are forbidden at all stages
- API keys must not be treated as the permanent production auth contract
- Every copilot invocation path must carry caller identity for audit

See `docs/architecture/FOUNDRY_ODOO_AUTH_AND_ENDPOINT_POLICY.md` for full policy.

## Runtime Monitoring Baseline

The runtime should integrate with the following identity/control-plane monitoring surfaces as maturity increases:

| Surface | Stage Required | Purpose |
|---------|---------------|---------|
| Entra sign-in logs | Stage 1 (read) | Verify admin access patterns |
| Entra audit logs | Stage 1 (read) | Track identity object changes |
| Diagnostic settings | Stage 2 (configure) | Forward identity logs to Log Analytics |
| Log Analytics | Stage 2 (query) | Cross-correlate identity and runtime events |
| Workbooks / usage insights | Stage 2 (dashboard) | Authentication method adoption tracking |
| App Insights | Stage 2 (instrument) | Foundry call latency, error rates, traces |

See `docs/architecture/ENTRA_IDENTITY_BASELINE_FOR_COPILOT.md` for current tenant monitoring state.

## Publish Gate

**Current publish state: ADVISORY_RELEASE_READY** (2026-03-15)

First evaluation pack exists (30/30 pass, eval-20260315-full-final). System prompt v2.1.0 live. Safety thresholds met.

| Level | Status | Required |
|-------|--------|----------|
| Internal Prototype | **Complete** | — |
| Advisory Release | **READY** | 30/30 eval pass, safety thresholds met |
| Grounded Advisory | Blocked | + Entra roles, context envelope, search index, retrieval, telemetry |
| Assisted Actions | Blocked | + read-only tools, tool eval evidence, 150+ eval pass |
| GA | Blocked | + write tools evaluated, security review, SLA, AI Gateway |

### Release Ladder

Promotion requires ALL criteria for that level:

**ADVISORY_RELEASE_READY** (current):
- [x] 30+ eval cases pass all thresholds
- [x] System prompt enforces scope boundaries
- [x] 0 critical safety / PII / unauthorized action failures

**GROUNDED_ADVISORY_READY** (next target):
- [ ] Entra app roles registered and active
- [ ] Context envelope injected in every request path
- [ ] AI Search index populated (≥ 100 chunks)
- [ ] Retrieval injection live with security trimming
- [ ] App Insights telemetry live and dashboard accessible

**ASSISTED_ACTIONS_READY**:
- [ ] Read-only tools wired and evaluated
- [ ] 150+ eval corpus passes all thresholds
- [ ] Tool permission enforcement verified
- [ ] Audit trail captures tool intent + result

**GA**:
- [ ] Write tools evaluated with confirmation flow
- [ ] Security review complete
- [ ] SLA contractually defined
- [ ] AI Gateway governance active
- [ ] Private networking where required

### Contracts

- `context-envelope-contract.md` — envelope schema and injection rules
- `retrieval-grounding-contract.md` — search, trimming, chunking, eval criteria
- `telemetry-contract.md` — event taxonomy, SLOs, dashboard requirements

**Thresholds:** `evals/odoo-copilot/thresholds.yaml`
**Rubric:** `evals/odoo-copilot/rubric.md`
**Spec:** `spec/odoo-copilot-azure-runtime/{plan,tasks}.md`
