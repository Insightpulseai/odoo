# Architecture Documentation

This directory contains the authoritative architecture documentation for InsightPulseAI.

## Documents

| Document | Description |
|----------|-------------|
| [INSIGHTPULSEAI_TECHNICAL_ARCHITECTURE.md](INSIGHTPULSEAI_TECHNICAL_ARCHITECTURE.md) | Master technical architecture specification |

## Related Documentation

| Location | Description |
|----------|-------------|
| [db/DB_TARGET_ARCHITECTURE.md](../../db/DB_TARGET_ARCHITECTURE.md) | Database schema architecture and migration plan |
| [db/rls/RLS_ROLES.md](../../db/rls/RLS_ROLES.md) | Role definitions and RLS policies |
| [db/seeds/SEEDING_STRATEGY.md](../../db/seeds/SEEDING_STRATEGY.md) | Database seeding strategy |
| [odoo/ODOO_INTEGRATION_MAP.md](../../odoo/ODOO_INTEGRATION_MAP.md) | Odoo 18 CE integration mapping |
| [engines/](../../engines/) | Engine YAML specifications |

## Quick Links

- **Engine Specs:** [`engines/_template/engine.yaml`](../../engines/_template/engine.yaml)
- **Migration Scripts:** [`db/migrations/`](../../db/migrations/)
- **RLS Templates:** [`db/rls/RLS_BASE_TEMPLATE.sql`](../../db/rls/RLS_BASE_TEMPLATE.sql)
- **Seed Scripts:** [`tools/seed_*.ts`](../../tools/)
