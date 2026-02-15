# Performance & CLI: Deployment Context

## What it is

Tools and strategies for running Odoo efficiently and managing deployments via command line.

## Key concepts

- **odoo-bin:** The main executable.
- **Profiling:** Tools to analyze slow requests.
- **Workers:** Using multiprocessing for concurrency.

## Implementation patterns

### CLI Commands

- `odoo-bin -d my_db -u my_module` (Update module)
- `odoo-bin scaffold my_module` (Create module structure)
- `odoo-bin shell -d my_db` (Interactive Python shell)

### Deployment

- `workers`: Set > 0 for production (limits = 2 \* CPU + 1).
- `limit_time_cpu`: Request timeout.

## Gotchas

- **Long-polling:** Requires a separate port/proxy configuration when workers > 0.
- **Memory Limits:** Set hard/soft limits to prevent runaway processes.

## References

- [Odoo CLI Documentation](https://www.odoo.com/documentation/19.0/developer/reference/backend/cmdline.html)
