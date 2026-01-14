# State Machine Documentation

Finite State Machine (FSM) specifications for stateful flows across Odoo, Scout, and Superset.

## Purpose

These FSMs capture:
- **States**: All possible system states
- **Events**: User actions, system events, lifecycle hooks
- **Guards**: Conditions for state transitions
- **Side Effects**: API calls, storage, notifications
- **Gaps**: Missing transitions, race conditions, error handling issues

## Directory Structure

```
docs/state_machines/
├── README.md                     # This file
├── odoo/
│   ├── ask_ai_chat.md           # AI chat conversational flow
│   ├── document_upload.md       # Document upload + OCR extraction
│   ├── grid_view_controller.md  # List view with pagination/filtering
│   └── superset_embed.md        # Superset dashboard embedding (client)
├── scout/
│   ├── auth_session.md          # Supabase auth + token refresh
│   ├── realtime_subscription.md # Supabase Realtime channels
│   ├── copilot_session.md       # AI copilot conversation
│   └── offline_queue.md         # Offline action queue + sync
└── superset/
    ├── embed_guest_token.md     # Guest token JWT flow
    ├── dashboard_filtering.md   # Native + cross-filter interactions
    └── chart_query_lifecycle.md # Chart query execution + cache
```

## Coverage Summary

### Odoo (CE 18 + OWL)

| Flow | File | Key Gaps |
|------|------|----------|
| Ask AI Chat | `odoo/ask_ai_chat.md` | No abort on unmount, no retry logic |
| Document Upload | `odoo/document_upload.md` | No progress, no chunked upload, race conditions |
| Grid Controller | `odoo/grid_view_controller.md` | Stale filter race, no bulk rollback |
| Superset Embed | `odoo/superset_embed.md` | No token expiry monitoring, no postMessage |

### Scout (Control Room + Mobile)

| Flow | File | Key Gaps |
|------|------|----------|
| Auth Session | `scout/auth_session.md` | Mock JWT in prod, no MFA, no biometric |
| Realtime Subscription | `scout/realtime_subscription.md` | Event ordering, memory leak on unmount |
| Copilot Session | `scout/copilot_session.md` | No abort, stale closure, no streaming |
| Offline Queue | `scout/offline_queue.md` | No conflict detection, no TTL |

### Superset (Embed)

| Flow | File | Key Gaps |
|------|------|----------|
| Guest Token | `superset/embed_guest_token.md` | No proactive refresh, no revocation |
| Dashboard Filtering | `superset/dashboard_filtering.md` | Debounce issues, cross-filter conflicts |
| Chart Query | `superset/chart_query_lifecycle.md` | Cache stampede, no query batching |

## Using These FSMs

### For Development

1. Before implementing changes, check if the flow has an FSM
2. Verify your changes don't introduce gaps listed
3. Update FSM if adding new states/transitions

### For Code Review

1. Cross-reference PRs against relevant FSMs
2. Flag changes that don't account for edge cases
3. Request FSM updates for significant flow changes

### For Testing

1. Generate test cases from transition tables
2. Focus on gap areas for regression tests
3. Test guard conditions explicitly

## Mermaid Rendering

All FSMs include Mermaid `stateDiagram-v2` diagrams. View in:
- GitHub (native rendering)
- VS Code with Mermaid extension
- [Mermaid Live Editor](https://mermaid.live)

## Contributing

When adding new FSMs:

1. Follow the template structure:
   - Overview
   - States table
   - Events table
   - Guards table
   - Side Effects table
   - Transition table
   - Mermaid diagram
   - Identified Gaps

2. Include source file paths

3. List at least 5 gap areas (races, missing transitions, error handling)

## Generation Commands

FSMs were extracted using prompts in `docs/state_machines/prompts/` (if applicable).

```bash
# Validate Mermaid syntax
npx @mermaid-js/mermaid-cli mmdc -i docs/state_machines/odoo/ask_ai_chat.md -o /dev/null
```

---

*Generated: 2026-01-14*
*Sources: addons/ipai/*, apps/*, infra/superset/*
