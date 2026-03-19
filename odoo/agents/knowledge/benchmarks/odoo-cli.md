# Odoo CLI (odoo-bin) — Benchmark Reference

> Source: Odoo 19 CE documentation and odoo-bin --help
> Status: GA — stable production interface
> Last updated: 2026-03-17

## Canonical Rule

Odoo CLI (odoo-bin) is the canonical CLI surface for all Odoo runtime, admin, and developer operations. It is the single entry point for server management, database operations, module scaffolding, testing, data manipulation, and code metrics.

## Binary Location

| Environment | Path |
|-------------|------|
| Local dev (Mac) | `vendor/odoo/odoo-bin` (via pyenv `odoo-19-dev`) |
| Devcontainer | `/opt/odoo/odoo-bin` |
| Production (Docker) | Container entrypoint |

## Python Runtime

- Canonical interpreter: pyenv virtualenv `odoo-19-dev` (Python 3.11.x)
- Local launch: `~/.pyenv/versions/odoo-19-dev/bin/python vendor/odoo/odoo-bin`
- Never use system Python or Homebrew Python for Odoo

## Subcommands

### Server (default)

Start the Odoo HTTP server.

| Flag | Purpose | Default |
|------|---------|---------|
| `-d, --database` | Target database | (required) |
| `--db_host` | PostgreSQL host | localhost |
| `--db_port` | PostgreSQL port | 5432 |
| `--db_user` | PostgreSQL user | (current user) |
| `--db_password` | PostgreSQL password | False |
| `--http-port` | HTTP port | 8069 |
| `--workers` | Worker processes (0=no workers) | 0 |
| `--proxy-mode` | Trust X-Forwarded-* headers | False |
| `--dev` | Dev mode: xml, reload, qweb, all | (disabled) |
| `--addons-path` | Comma-separated addons dirs | (required) |
| `--data-dir` | Filestore directory | ~/.local/share/Odoo |
| `--config, -c` | Config file path | (none) |
| `--save` | Save current options to config | (no) |
| `--log-level` | debug, info, warn, error, critical | info |
| `--list-db` | Allow database listing | True |
| `-i, --init` | Install modules (comma-separated) | (none) |
| `-u, --update` | Update modules (comma-separated) | (none) |
| `--stop-after-init` | Stop server after init/update | False |
| `--test-enable` | Run module tests during init/update | False |
| `--test-tags` | Filter tests by tag | (all) |
| `--without-demo` | Skip demo data (use `all` for all modules) | (none) |

### shell

Interactive Python shell with Odoo environment.

```bash
odoo-bin shell -d odoo_dev --addons-path=vendor/odoo/addons,addons/ipai --no-http
```

Provides: `self` (current user), `self.env` (Odoo environment), access to all models.

### scaffold

Generate new module skeleton.

```bash
odoo-bin scaffold <module_name> <destination_directory>
```

Creates: `__init__.py`, `__manifest__.py`, controllers/, models/, views/, security/, demo/, static/

### neutralize

Strip sensitive data from database for safe sharing.

```bash
odoo-bin neutralize --database <db>
```

Removes: SMTP credentials, user passwords, API keys, webhook URLs, cron schedules.

### populate

Generate test/demo data for modules that implement `_populate_factories`.

```bash
odoo-bin populate --database <db> [--models model1,model2] [--size small|medium|large]
```

### cloc

Count lines of code in Odoo modules.

```bash
odoo-bin cloc --database <db> --addons-path <paths>
odoo-bin cloc --path <addons-directory>
```

Reports: Python, XML, JavaScript, CSS lines per module.

## Database Naming Convention

| Database | Purpose | Environment |
|----------|---------|-------------|
| `odoo_dev` | Clean development | Local / devcontainer |
| `odoo_dev_demo` | Demo/showroom with demo data | Local / devcontainer |
| `odoo_staging` | Staging rehearsal | Staging ACA |
| `odoo` | Production | Production ACA |
| `test_<module>` | Disposable test databases | Any |

Deprecated names (never use): `odoo_core`, `odoo_prod`, `odoo_db`, `odoo_stage`

## Test Tags Syntax

```bash
# All tests in a module
--test-tags /<module_name>

# Specific test class
--test-tags /<module_name>:TestClassName

# Specific test method
--test-tags /<module_name>:TestClassName.test_method

# Skip a module's tests
--test-tags -/<module_name>

# Combine
--test-tags /<mod1>,/<mod2>,-/<mod3>
```

## Common Patterns

### Install module in test database
```bash
odoo-bin -d test_mymod -i my_module --test-enable --stop-after-init --without-demo all
```

### Update module
```bash
odoo-bin -d odoo_dev -u my_module --stop-after-init
```

### Dev mode with auto-reload
```bash
odoo-bin -d odoo_dev --dev=xml,reload,qweb --http-port=8069
```

### Scripted shell query
```bash
echo "print(self.env['ir.module.module'].search_count([('state','=','installed')]))" | odoo-bin shell -d odoo_dev --no-http
```
