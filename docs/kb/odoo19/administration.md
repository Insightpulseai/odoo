# Odoo 19 Administration & Hosting

## Hosting Types

- **Odoo Online (SaaS):** Fully managed, standard modules only. Easiest start.
- **Odoo.sh (PaaS):** Managed cloud hosting for custom development. Includes CI/CD, staging, and production environments.
- **On-Premise:** Self-hosted. Full control, requires infrastructure maintenance.

## Odoo.sh Platform

### Key Features

- **CI/CD:** Automatic builds for every commit.
- **Branches:**
  - `production`: The live database.
  - `staging`: Syncs with production data (sanitized) for testing.
  - `development`: Fresh databases for coding features.
- **Tools:**
  - **Web Shell:** Full command-line access (`odoo-bin`, `pip`, `psql`).
  - **Editor:** Online code editor.
  - **Logs:** Real-time server and transaction logs.
  - **Backups:** Automated daily backups (Staging/Production).

### Getting Started

1. **Login:** Sign in with GitHub.
2. **Authorize:** Grant Odoo.sh access to your repositories.
3. **Deploy:** Select repository and Odoo version (e.g., 19.0).

## Database Management

### Odoo Online

- **Manager:** Accessible at `https://www.odoo.com/my/databases`.
- **Operations:** Duplicate, Delete, Rename, Download Backup.
- **Domains:** Configure custom domains via the manager.
- **API:** Use `odoo.database` external API to list/manage remotely.

### On-Premise

- **Registration:** Link database to Enterprise subscription via the dashboard.
- **Neutralization:** When duplicating a production DB to test, ALWAYS neutralize to stop crons/emails:
  ```bash
  odoo-bin neutralize -d <db_name>
  ```
- **Common Issues:**
  - "Too many users": Subscription limit reached. Deactivate users or upgrade.
  - "Registration error": Check UUID conflict or firewall access to `services.odoo.com`.

## Source Links

- [Odoo.sh Documentation](https://www.odoo.com/documentation/19.0/administration/odoo_sh.html)
- [Odoo Online](https://www.odoo.com/documentation/19.0/administration/odoo_online.html)
- [On-Premise Admin](https://www.odoo.com/documentation/19.0/administration/on_premise.html)
