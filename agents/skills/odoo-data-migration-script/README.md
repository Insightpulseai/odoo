# odoo-data-migration-script

Writes data migration scripts for seeding, transforming, backfilling, or migrating data during module upgrades.

## When to use
- A module version bump requires data transformation
- A new required field is added to an existing model
- Existing records need data backfill
- Schema changes require pre-migration SQL
- Module renaming or model refactoring

## Key rule
Never use `cr.commit()` in migration scripts -- the framework handles transactions. Pre-migrations
use raw SQL (ORM not loaded), post-migrations use ORM when possible. All migrations must be
idempotent and tested on a disposable database with existing data.

## Cross-references
- `agents/knowledge/benchmarks/odoo-developer-howtos.md`
- `agents/knowledge/benchmarks/odoo-coding-guidelines.md`
- `~/.claude/rules/odoo19-coding.md`
