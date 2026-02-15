# General Administration

## What it is

Managing users, databases, and system parameters in Odoo.

## Key concepts

- **User Management:** Users, Roles, Access Rights.
- **Database Manager:** Backup, Restore, Duplicate, Delete. (`/web/database/manager`)
- **System Parameters:** `ir.config_parameter` for global settings (e.g., `web.base.url`).

## Patterns

- **Neutralization:** When duplicating a DB for testing, neutralize it (disable emails/cron) to avoid spamming customers.
- **Scheduled Actions:** Cron jobs management.

## References

- [Odoo Administration Guide](https://www.odoo.com/documentation/19.0/administration.html)
