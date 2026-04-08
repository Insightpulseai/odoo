# Plan — Pulser Assistant: Odoo Adapter

## Status
Draft

## Architecture Approach

### Embedded UI (OWL/QWeb)

```text
addons/ipai/ipai_pulser_assistant/
  static/src/
    components/
      PulserSystray/         # Systray icon component (OWL)
      PulserRecordPanel/     # Contextual record panel (OWL)
      PulserRecommendation/  # Recommendation card component (OWL)
    services/
      pulser_service.js      # Client-side service for agent API calls
  views/
    pulser_templates.xml     # QWeb templates for embedded UI
  models/
    pulser_context.py        # Record context assembly
    pulser_action.py         # Action request/result handling
    pulser_telemetry.py      # Evidence/telemetry emission
  controllers/
    pulser_api.py            # FastAPI tool endpoints for agents
  security/
    ir.model.access.csv      # ACLs
  data/
    pulser_config.xml        # Default configuration data
```

### Record Context Assembly

The context adapter inspects the current Odoo model/record and assembles:
- Model name and record ID
- Key display fields (name, state, amount, partner, date)
- Related records (invoice lines, payment history, linked POs)
- User permissions on the record
- Company context

Context is passed to the agent runtime via the `PulserContextProvider` contract defined in `agents`.

### Safe Action Modes

| Mode | When Used | User Experience |
|------|-----------|----------------|
| Read-only | Default for browse/query | Agent returns data, no mutations |
| Suggest-only | Recommendations, analysis | Agent shows cards, user clicks to execute |
| Approval-required | Finance-sensitive (JE, payment, tax) | Agent proposes, confirmation dialog, then execute |
| Direct-execution | Narrow safe actions (log note, set tag) | Agent executes immediately, logs in chatter |

Action mode is determined by:
1. Action type classification (in tool binding metadata)
2. User trust level (from platform identity binding)
3. Module configuration (per-company override)

### Telemetry/Evidence Emission

All assistant interactions emit structured events:
- Action requests (what agent asked to do)
- Action results (what happened)
- Safety mode applied (which mode was used)
- User identity (who approved/executed)
- Timestamp and correlation ID

Events are sent to `platform` evidence store via webhook/API.

### Tool Endpoints

FastAPI endpoints exposed for agent consumption:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/pulser/context/{model}/{id}` | GET | Record context assembly |
| `/api/v1/pulser/action` | POST | Execute approved Odoo action |
| `/api/v1/pulser/search/{model}` | POST | Search records with domain filter |
| `/api/v1/pulser/recommend/{model}/{id}` | GET | Get contextual recommendations |

All endpoints require API key or OAuth2 bearer token (via `auth_api_key` OCA module).

## Design Principles

1. **Never make Odoo the sole assistant authority**: Odoo is one integrated system in a Pulser formation
2. **Record-aware, company-aware, permission-aware**: Context assembly always includes record, company, and user permission context
3. **Destructive actions require approval**: Finance-sensitive and compliance actions always use approval-required or suggest-only modes
4. **All actions are attributable and auditable**: Every assistant action logs in Odoo chatter and emits telemetry to platform
5. **Tool endpoints are the contract surface**: Agents interact with Odoo exclusively through FastAPI endpoints, never direct ORM
6. **Preview/prod separation**: Different assistant configurations for preview and production channels
7. **Capability-type adapters**: Odoo adapter separates logic by capability type — transactional (action adapters), navigational (resolvers), informational (context exporters)
8. **Tax adapter scope**: Odoo owns tax context assembly and safe action execution; tax reasoning lives in agents, tax governance lives in platform

## Cross-Repo Dependencies

| Repo | `odoo` provides | `odoo` consumes |
|------|----------------|----------------|
| `agents` | FastAPI tool endpoints, record context | Agent-initiated action requests |
| `platform` | Telemetry/evidence events, adapter module status | Formation metadata, identity bindings, action policies |
| `web` | — (agents mediate) | — |
| `data-intelligence` | — (agents query directly) | — |

## OCA Dependencies

Per OCA governance rules, the adapter module depends on:
- `fastapi` — API endpoint hosting
- `auth_api_key` — Machine authentication for agent calls
- `auditlog` — Action audit trail
- `base_user_role` — Operator role separation
- `web_environment_ribbon` — Environment visual indicator (preview vs. production)

### Phase O5 — Tax Guru Odoo Adapter

- Implement ipai.pulser.tax_context model (record-aware tax context assembly for invoices, bills, POs, expenses, journals)
- Implement ipai.pulser.tax_action_request model (structured tax action proposals with safe execution modes)
- Implement ipai.pulser.tax_exception_event model (outbound exception emission to platform)
- Add tax context builders for account.move, purchase.order, hr.expense record types
- Add FastAPI endpoints for tax context retrieval and action execution
