# Event-Driven Automation Jobs

Jobs triggered by external events (webhooks, queue messages, GitHub events).

Each job gets its own directory with:

- `config.yaml` — trigger source, filter, retry policy
- `handler.py` (or `.ts`) — event handler entry point
- `test_*.py` — unit/contract tests

## Conventions

- Event handlers must be idempotent (duplicate delivery is expected).
- Declare the trigger source explicitly in config.
- Register in `automations/ssot/schedules/schedule-registry.yaml` with `trigger: event`.

<!-- TODO: Add first event-driven job (e.g., PR-label-sync, deployment-notify) -->
