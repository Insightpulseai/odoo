# Plan: ipai_odoo_copilot

> **Status**: Draft
> **Constitution**: [constitution.md](constitution.md)
> **PRD**: [prd.md](prd.md)

---

## Architecture Summary

The copilot system is split across five control planes. The `ipai_odoo_copilot`
module owns only the Odoo slice.

| Plane | Owner | Responsibility |
|-------|-------|----------------|
| **Odoo** | `ipai_odoo_copilot` module | UI entry points, context packaging, response rendering, audit, admin config |
| **Foundry** | Azure AI Foundry project | Model hosting, prompt orchestration, tool definitions, grounding indexes |
| **Databricks** | Unity Catalog + DLT | Governed analytics data for grounding (bronze/silver/gold lakehouse) |
| **Entra** | Microsoft Entra ID | User identity, token issuance, group-based authorization |
| **DevOps** | Azure DevOps / GitHub Actions | CI/CD, module testing, deployment pipelines |

### Finance-First Architecture Interpretation

For Release 1, the architecture is narrowed to finance:

```
┌──────────────────────────────────────────────────────────────────┐
│  Odoo CE 19 (ipai_odoo_copilot)                                  │
│                                                                    │
│  Systray ──► Chat Panel ──► Context Packager ──► HTTP Client      │
│                                    │                    │          │
│                                    ▼                    ▼          │
│                            Accounting Models      Foundry API      │
│                            (move, move.line,      (HTTPS POST)     │
│                             partner, bank.stmt)                    │
│                                                         │          │
│  Audit Logger ◄──────────────────────────────────────────┘         │
│  Admin Config (Settings)                                           │
└──────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────┐
│  Azure AI Foundry                                                  │
│                                                                    │
│  Agent ──► Tool Definitions ──► Grounding Index                   │
│    │              │                    │                            │
│    ▼              ▼                    ▼                            │
│  GPT-4o    Odoo JSON-RPC tools   Databricks SQL (governed)        │
│            (read-only by default)                                  │
└──────────────────────────────────────────────────────────────────┘
```

The Odoo module sends a structured JSON payload. Foundry decides which tools
to invoke (including calling back into Odoo's JSON-RPC API for data retrieval).
The module renders whatever Foundry returns.

---

## Module Boundaries

### Inside the module (ipai_odoo_copilot)

- Systray OWL component and chat panel.
- Context packager (Python: reads Odoo models, serializes to JSON).
- HTTP client (Python: sends request to Foundry, receives response).
- Response renderer (JS/XML: displays text, tables, action buttons, citations).
- Audit model (`ipai.copilot.audit`).
- Telemetry model (`ipai.copilot.telemetry`).
- Provider abstract model (`ipai.copilot.provider`).
- Foundry provider implementation (`ipai.copilot.provider.foundry`).
- Admin configuration (res.config.settings extension).
- Security groups and ACLs.
- Health check controller.

### Outside the module

- Model selection and prompt engineering (Foundry).
- Tool definitions and orchestration (Foundry agent).
- Grounding data preparation (Databricks lakehouse).
- Identity federation and token issuance (Entra ID).
- WAF, TLS termination, CDN (Azure Front Door).
- Secret management (Azure Key Vault).
- CI/CD pipelines (Azure DevOps / GitHub Actions).
- Reconciliation engine (Odoo native + OCA `account_reconcile_oca`).
- Email delivery (Zoho SMTP via `ir.mail_server`).

---

## Proposed Odoo Module Structure

```
addons/ipai/ipai_odoo_copilot/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── main.py                    # Health check, webhook (if needed)
├── data/
│   ├── ir_config_parameter.xml    # Default system parameters
│   ├── ir_cron.xml                # Scheduled audit cleanup (optional)
│   ├── ir_actions_server.xml      # Server actions for copilot triggers
│   └── copilot_partner_data.xml   # Copilot bot partner record
├── models/
│   ├── __init__.py
│   ├── copilot_audit.py           # ipai.copilot.audit model
│   ├── copilot_bot.py             # Copilot bot partner setup
│   ├── foundry_service.py         # ipai.copilot.provider.foundry
│   ├── res_config_settings.py     # Admin settings extension
│   ├── telemetry.py               # ipai.copilot.telemetry model
│   └── tool_executor.py           # Action mediation logic
├── security/
│   ├── ir.model.access.csv        # ACLs
│   └── copilot_groups.xml         # Security groups
├── static/
│   └── src/
│       ├── js/
│       │   ├── copilot_systray.js # Systray OWL component
│       │   └── copilot_service.js # JS service for API calls
│       ├── xml/
│       │   └── copilot_systray.xml # QWeb templates
│       └── scss/
│           └── copilot.scss       # Styles (o_ipai_copilot_ prefix)
├── tests/
│   ├── __init__.py
│   ├── test_copilot_audit.py      # Audit model tests
│   ├── test_foundry_service.py    # Provider tests (mocked HTTP)
│   ├── test_res_config_settings.py # Settings tests
│   └── test_tool_executor.py      # Action mediation tests
└── views/
    ├── copilot_audit_views.xml    # Audit log list/form views
    └── res_config_settings_views.xml # Settings UI
```

---

## Key Design Decisions

### DD-1: OWL Systray Component (not legacy widget)

The systray icon and chat panel are implemented as Odoo 19 OWL components,
not legacy jQuery widgets. This ensures forward compatibility with Odoo's
web framework direction and avoids deprecation warnings.

**Trade-off**: OWL has a steeper learning curve but is the only supported
path for Odoo 19+ frontend components.

### DD-2: `requests` Library for HTTP (not `urllib3` directly)

The module uses Python `requests` for external HTTP calls. `requests` is
already a transitive dependency of Odoo and provides a clean API for
timeout handling, retries, and TLS verification.

**Trade-off**: Adds no new dependency. `httpx` would offer async support
but is not in Odoo's dependency tree.

### DD-3: Audit as Odoo Model (not external log sink)

Audit records are stored as `ipai.copilot.audit` Odoo records in PostgreSQL.
This keeps audit data queryable via Odoo's standard list views and export tools.

**Trade-off**: High-volume copilot usage could grow the table. Mitigated by
a configurable retention policy (cron job deletes records older than N days)
and a telemetry model for aggregated metrics.

### DD-4: Provider Abstract Model (not hardcoded Foundry calls)

The external runtime call is abstracted behind `ipai.copilot.provider`.
The default implementation targets Azure AI Foundry. This allows swapping
providers (e.g., for testing with a mock, or for an alternative runtime)
without modifying the bridge module.

**Trade-off**: Slightly more code than a direct HTTP call, but essential
for testability and future extensibility.

### DD-5: Context Packaging Respects ACLs

The context packager reads Odoo data using the current user's environment
(`self.env`), not `sudo()`. This means the copilot can only see data the
user is authorized to access. If the user lacks read access to a related
model, that context is omitted (not errored).

**Trade-off**: The copilot may give less complete answers for users with
restricted access. This is by design — security over completeness.

### DD-6: No WebSocket / Long-Polling for Chat

The chat panel uses standard HTTP POST/response. Streaming (SSE or WebSocket)
is deferred to Release 2. For Release 1, the user sees a loading spinner
until the full response arrives.

**Trade-off**: Slightly worse UX for long responses, but dramatically simpler
implementation and no dependency on Odoo's bus module for copilot traffic.

---

## Integration Design

### Identity Flow

```
User logs into Odoo (session cookie)
    │
    ▼
Copilot request initiated (JS → Odoo controller)
    │
    ▼
Odoo controller acquires Entra token:
  - Managed Identity: IMDS endpoint on Azure Container Apps
  - API Key fallback: ir.config_parameter (for non-Azure envs)
    │
    ▼
HTTP POST to Foundry with Bearer token + JSON payload
    │
    ▼
Foundry validates token, extracts user claims, enforces RBAC
```

### Request Contract (Odoo → Foundry)

```json
{
  "session_id": "uuid4",
  "user": {
    "uid": 2,
    "login": "finance@insightpulseai.com",
    "groups": ["account.group_account_user", "ipai_odoo_copilot.group_copilot_user"],
    "company_id": 1,
    "lang": "en_US"
  },
  "context": {
    "active_model": "account.move",
    "active_id": 42,
    "record_data": {
      "name": "INV/2026/0042",
      "state": "posted",
      "amount_total": 45000.00,
      "partner_id": [7, "ABC Corporation"],
      "date": "2026-03-15"
    }
  },
  "question": "Why is this invoice still unreconciled?",
  "capabilities": ["finance_qa", "reconciliation", "collections", "variance"]
}
```

### Response Contract (Foundry → Odoo)

```json
{
  "session_id": "uuid4",
  "response": {
    "text": "Invoice INV/2026/0042 has 2 partial payments...",
    "citations": [
      {"model": "account.move.line", "id": 301, "label": "Payment CUST.IN/2026/0015"},
      {"model": "account.move.line", "id": 302, "label": "Payment CUST.IN/2026/0018"}
    ],
    "suggested_actions": [
      {
        "id": "reconcile_match",
        "label": "Reconcile with these payments",
        "action_type": "reconcile",
        "params": {"move_line_ids": [301, 302]}
      }
    ],
    "escalation": {
      "needed": false
    }
  },
  "metadata": {
    "model": "gpt-4o",
    "latency_ms": 2340,
    "tokens_used": 1250
  }
}
```

### Failure Modes

| Failure | Module Behavior |
|---------|----------------|
| Foundry endpoint unreachable | Retry once after 2s, then show degraded state |
| Foundry returns 4xx | Log audit record with error, show "cannot process request" |
| Foundry returns 5xx | Log audit record, show "service temporarily unavailable" |
| Foundry response timeout | Log audit with `action_result='timeout'`, show timeout message |
| Malformed response JSON | Log raw response (truncated), show generic error |
| User lacks copilot group | Systray icon not rendered, no JS loaded |
| Entra token acquisition fails | Fall back to API key if configured, else show auth error |

---

## Test Strategy

### Unit Tests

| Test | What It Covers |
|------|---------------|
| `test_copilot_audit.py` | Audit record creation, field validation, retention cron |
| `test_foundry_service.py` | HTTP request construction, response parsing, error handling (mocked) |
| `test_res_config_settings.py` | Settings read/write, default values, validation |
| `test_tool_executor.py` | Action allowlist checking, execution with confirmation |

### Integration Tests

| Test | What It Covers |
|------|---------------|
| Module install | `--stop-after-init` on clean DB |
| Context packaging | Real Odoo records → JSON payload correctness |
| ACL enforcement | Restricted user gets filtered context |
| Coexistence | Install alongside `account_reconcile_oca`, `mis_builder`, `ipai_finance_ppm` |

### Mock Provider

A `test` provider implementation returns canned responses for each finance
scenario, enabling end-to-end UI testing without a live Foundry endpoint.

### CI Pipeline

```yaml
- odoo-bin -i ipai_odoo_copilot --stop-after-init --test-enable -d test_ipai_odoo_copilot
- flake8 addons/ipai/ipai_odoo_copilot/
- black --check addons/ipai/ipai_odoo_copilot/
- isort --check addons/ipai/ipai_odoo_copilot/
- coverage report --fail-under=80
```

---

## Deployment Strategy

### Phase 1: Dev Environment

- Install module in devcontainer (`odoo_dev` database).
- Configure Foundry endpoint to dev project.
- Validate all 4 finance scenarios with demo data.

### Phase 2: Staging

- Deploy to `ipai-odoo-dev-web` Container App (staging slot).
- Configure Foundry endpoint to staging project.
- Run automated integration tests.
- Finance team UAT with production-like data.

### Phase 3: Production

- Deploy via standard Odoo module update (`-u ipai_odoo_copilot`).
- Enable copilot for `group_copilot_user` members only.
- Monitor audit logs and telemetry for 7 days.
- Expand to broader user base after validation.

### Rollback

- Disable copilot via Settings toggle (instant, no restart).
- If module itself is broken: `odoo-bin -u ipai_odoo_copilot` with
  the previous module version, or uninstall.
- Audit records are retained even after module uninstall (stored in
  standard Odoo tables).

---

## Risks

| Risk | Impact | Likelihood | Response |
|------|--------|------------|----------|
| Foundry latency exceeds 5s p95 | Poor UX, low adoption | Medium | Implement streaming in Release 2; optimize context payload size |
| Users submit sensitive data in questions | Data leakage to external service | Medium | Document data handling policy; add optional PII redaction filter |
| Audit table grows unbounded | Database bloat | Low | Retention cron (configurable, default 90 days) |
| OCA module conflicts | Install failure | Low | CI coexistence tests; minimal model footprint |
| Entra token acquisition fails on Odoo.sh | Module non-functional outside Azure | Medium | API key fallback mode; document Odoo.sh configuration |
| Users expect write actions in Release 1 | Disappointment, workarounds | Medium | Clear documentation; empty allowlist by default; Release 2 roadmap visible |

---

*Last updated: 2026-03-22*
