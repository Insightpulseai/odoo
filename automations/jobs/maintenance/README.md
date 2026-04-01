# Maintenance Jobs

Housekeeping and operational maintenance automations.

Examples: log rotation, stale resource cleanup, certificate renewal checks, DB vacuum.

Each job gets its own directory with:

- `config.yaml` — schedule, scope, safety checks
- `handler.py` (or `.ts`) — maintenance logic
- `test_*.py` — validation tests

## Conventions

- Maintenance jobs must have a dry-run mode.
- Destructive operations require explicit confirmation flags.
- Register in `automations/ssot/schedules/schedule-registry.yaml` with `category: maintenance`.

<!-- TODO: Add first maintenance job -->
