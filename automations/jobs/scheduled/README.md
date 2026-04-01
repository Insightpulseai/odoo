# Scheduled Automation Jobs

Each job gets its own directory with:

- `config.yaml` — schedule, timeout, retry policy
- `handler.py` (or `.ts`) — job entry point
- `test_*.py` — unit/contract tests

## Conventions

- Jobs must be idempotent (safe to re-run on failure).
- Schedule definitions are registered in `automations/ssot/schedules/schedule-registry.yaml`.
- Secrets resolved via Azure Key Vault environment bindings, never hardcoded.

<!-- TODO: Add first scheduled job (e.g., repo-hygiene, stale-branch-cleanup) -->
