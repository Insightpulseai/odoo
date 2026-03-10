---
name: odoo19-cli
description: Odoo 19 command-line interface reference for odoo-bin server, database, module, i18n, scaffold, populate, cloc, neutralize, obfuscate, deploy, and upgrade_code commands
metadata:
  author: odoo/documentation
  version: "19.0"
  source: "content/developer/reference/cli.rst"
  extracted: "2026-02-17"
---

# Odoo 19 CLI Reference

Complete reference for the `odoo-bin` command-line interface. Covers the server command, database management, module management, i18n, scaffold, populate, cloc, neutralize, obfuscate, deploy, upgrade_code, and shell commands.

---

## 1. Running odoo-bin

The CLI entry point depends on installation method:

| Installation | Command |
|---|---|
| Source | `./odoo-bin` |
| Package | `odoo` |
| Docker | See Docker image docs |

### Version and Help

```bash
# Show version
odoo-bin --version

# Show help for any command
odoo-bin --help
odoo-bin server --help
odoo-bin db --help
```

Enable shell auto-completion:

```bash
COMMANDS=$(odoo-bin --help | sed -e "s/^    \([^ ]\+\).*$/ \1/gp;d" | xargs)
echo "complete -W '$COMMANDS' odoo-bin" >> ~/.bash_completion
```

---

## 2. Server Command (Default)

The `server` command is the default -- you can omit it. It starts the Odoo HTTP server.

### Core Flags

```bash
# Specify database(s) -- comma-separated restricts access
odoo-bin -d mydb
odoo-bin --database mydb1,mydb2

# Install modules before running (requires -d)
odoo-bin -d mydb -i sale,purchase

# Update modules before running (requires -d)
odoo-bin -d mydb -u sale
odoo-bin -d mydb -u all

# Reinitialize modules (dev/debug only, NOT for production)
odoo-bin -d mydb --reinit sale

# Addons path -- comma-separated directories scanned for modules
odoo-bin --addons-path=addons,enterprise,custom_addons

# Additional upgrade scripts path
odoo-bin --upgrade-path=/path/to/upgrade-util/src

# Pre-upgrade scripts run before loading base
odoo-bin --pre-upgrade-scripts=/path/to/script.py

# Server-wide modules (default: base,web)
odoo-bin --load base,web
```

### Configuration File

```bash
# Use alternate config file
odoo-bin -c /etc/odoo/odoo.conf

# Save current configuration
odoo-bin -s
odoo-bin --save

# Data directory
odoo-bin -D /var/lib/odoo
odoo-bin --data-dir /var/lib/odoo
```

Config file lookup order:
1. `-c` / `--config` argument
2. `ODOO_RC` environment variable
3. `$HOME/.odoorc`

#### Configuration File Format

```ini
[options]
db_user=odoo
dbfilter=odoo
addons_path=addons,enterprise
db_host=localhost
db_port=5432
```

**CLI-to-config name mappings** (non-obvious ones):

| CLI Flag | Config Key |
|---|---|
| `--db-filter` | `dbfilter` |
| `--no-http` | `http_enable` |
| `--smtp` | `smtp_server` |
| `--database` | `db_name` |
| `--log-handler` | `log_handler` |

General rule: remove leading `-` prefix, replace remaining `-` with `_`.

### Demo Data

```bash
# Install demo data in new databases
odoo-bin --with-demo

# No demo data (default)
odoo-bin --without-demo

# Skip auto-installing modules (dev use)
odoo-bin --skip-auto-install
```

### Misc Server Flags

```bash
# PID file
odoo-bin --pidfile=/var/run/odoo.pid

# Stop server after initialization (useful for install/update scripts)
odoo-bin --stop-after-init

# GeoIP databases
odoo-bin --geoip-city-db /path/to/GeoLite2-City.mmdb
odoo-bin --geoip-country-db /path/to/GeoLite2-Country.mmdb
```

---

## 3. Testing Flags

```bash
# Run tests after module installation
odoo-bin -d testdb -i sale --test-enable

# Run a specific Python test file
odoo-bin -d testdb --test-file addons/sale/tests/test_sale.py

# Run tests matching tags (comma-separated specs)
odoo-bin -d testdb --test-tags :TestClass.test_func,/test_module,external

# Screenshot directory for failed HttpCase.browser_js tests
odoo-bin --screenshots /tmp/my_screenshots

# Screencast directory (requires ffmpeg for video encoding)
odoo-bin --screencasts /tmp/my_screencasts
```

### Test Tag Syntax

Format: `[-][tag][/module][:class][.method]`

| Component | Description |
|---|---|
| `-` | Prefix to exclude (instead of include) |
| `tag` | Matches `@tagged` decorators. Default: `standard` (include), `*` (exclude) |
| `/module` | Matches module technical name |
| `:class` | Matches test class name |
| `.method` | Matches test method name |

Tests execute at two stages:
1. After each module install/update (`at_install`)
2. After all modules loaded (`post_install`)

Examples:

```bash
# Run only tests in sale module
odoo-bin -d testdb -i sale --test-tags /sale

# Run a specific test class
odoo-bin -d testdb --test-tags :TestSaleOrder

# Run a specific test method
odoo-bin -d testdb --test-tags :TestSaleOrder.test_confirm

# Exclude external-tagged tests
odoo-bin -d testdb -i sale --test-tags -external

# Run all standard tests except one module
odoo-bin -d testdb --test-tags standard,-/website
```

---

## 4. Database Connection Flags

```bash
# Database user
odoo-bin -r odoo
odoo-bin --db_user odoo

# Database password
odoo-bin -w secret
odoo-bin --db_password secret

# Database host (default: UNIX socket on Linux, localhost on Windows)
odoo-bin --db_host localhost

# Database port (default: 5432)
odoo-bin --db_port 5432

# Replica database (for read scaling)
odoo-bin --db_replica_host replica.host
odoo-bin --db_replica_port 5432

# Database filter (regex, %h = hostname, %d = subdomain)
odoo-bin --db-filter "^mydb$"
odoo-bin --db-filter "^%d$"

# Database template (default: template0)
odoo-bin --db-template template0

# PostgreSQL binaries path
odoo-bin --pg_path /usr/lib/postgresql/16/bin

# Suppress database listing
odoo-bin --no-database-list

# SSL mode for PostgreSQL connection
odoo-bin --db_sslmode prefer

# Enable unaccent extension on new databases
odoo-bin --unaccent
```

### Database Filter Examples

```bash
# Restrict to databases starting with "prod"
odoo-bin --db-filter "^prod.*$"

# Restrict to specific databases
odoo-bin --database db1,db2

# Combined: filter + update
odoo-bin --db-filter "^prod.*$" --database prod1,prod2 -u base
```

---

## 5. HTTP Configuration

```bash
# Disable HTTP server (may still start cron workers)
odoo-bin --no-http

# HTTP interface (default: 0.0.0.0)
odoo-bin --http-interface 127.0.0.1

# HTTP port (default: 8069)
odoo-bin -p 8069
odoo-bin --http-port 8069

# WebSocket port for multiprocessing/gevent (default: 8072)
odoo-bin --gevent-port 8072

# Enable reverse proxy mode (X-Forwarded-* headers)
odoo-bin --proxy-mode

# Enable X-Sendfile/X-Accel for static file serving
odoo-bin --x-sendfile
```

---

## 6. Email Configuration

```bash
odoo-bin --email-from noreply@example.com \
         --from-filter example.com \
         --smtp mail.example.com \
         --smtp-port 587 \
         --smtp-ssl \
         --smtp-user noreply@example.com \
         --smtp-password secret \
         --smtp-ssl-certificate-filename /path/to/cert.pem \
         --smtp-ssl-private-key-filename /path/to/key.pem
```

---

## 7. Logging Configuration

```bash
# Log to file instead of stderr
odoo-bin --logfile /var/log/odoo/odoo.log

# Log to syslog
odoo-bin --syslog

# Log to database table ir_logging
odoo-bin --log-db mydb

# Set specific logger levels (repeatable)
odoo-bin --log-handler :DEBUG \
         --log-handler werkzeug:CRITICAL \
         --log-handler odoo.fields:WARNING

# Shortcut: enable HTTP request/response debug logging
odoo-bin --log-web

# Shortcut: enable SQL query debug logging
odoo-bin --log-sql

# Log level presets
odoo-bin --log-level debug
odoo-bin --log-level debug_sql
odoo-bin --log-level debug_rpc
odoo-bin --log-level debug_rpc_answer
```

---

## 8. Multiprocessing (Workers)

```bash
# Enable multiprocessing with N HTTP workers (Unix only, default: 0 = threading)
odoo-bin --workers 4

# Requests per worker before recycling (default: 8196)
odoo-bin --limit-request 8196

# Soft memory limit per worker in bytes (default: 2048 MiB)
odoo-bin --limit-memory-soft 2147483648

# Hard memory limit -- immediate kill (default: 2560 MiB)
odoo-bin --limit-memory-hard 2684354560

# CPU seconds per request (default: 60)
odoo-bin --limit-time-cpu 60

# Wall-clock seconds per request (default: 120)
odoo-bin --limit-time-real 120

# Cron worker threads/processes (default: 2)
odoo-bin --max-cron-threads 2

# Cron worker lifetime limit in seconds (0 = disabled)
odoo-bin --limit-time-worker-cron 0
```

---

## 9. Developer Mode Flags

```bash
# Enable all dev features (xml, reload, qweb, access)
odoo-bin --dev all

# Individual features:
odoo-bin --dev xml       # Read QWeb templates from XML files directly
odoo-bin --dev reload    # Auto-restart on Python file changes
odoo-bin --dev qweb      # Break on t-debug='debugger' in QWeb
odoo-bin --dev werkzeug  # Full traceback on frontend errors
odoo-bin --dev replica   # Simulate replica DB on same server
odoo-bin --dev access    # Log traceback for AccessError (403)

# Combine features
odoo-bin --dev xml,reload
```

---

## 10. Shell Command

Opens an interactive Python console with the ORM available via `env`.

```bash
odoo-bin shell -d mydb

# With a startup script
odoo-bin shell -d mydb --shell-file init_script.py

# Specify REPL (ipython, ptpython, bpython, python)
odoo-bin shell -d mydb --shell-interface ipython
```

### Shell Usage Example

```python
# In the shell:
records = env["res.partner"].search([])
for partner in records:
    partner.name = "%s !" % partner.name

# IMPORTANT: Shell runs in transaction mode. Changes are rolled back on exit.
# To persist changes, commit explicitly:
env.cr.commit()
```

---

## 11. Database Management Commands

### db init -- Initialize a Database

```bash
# Basic initialization (installs base module)
odoo-bin db init mydb

# With demo data
odoo-bin db init mydb --with-demo

# With country and language
odoo-bin db init mydb --country US --language en_US

# Custom admin credentials
odoo-bin db init mydb --username admin --password mysecret

# Force recreate (drops existing DB first)
odoo-bin db init mydb --force
```

### db dump -- Save a Database Dump

```bash
# Dump to file (zip format, default)
odoo-bin db dump mydb /backups/mydb.zip

# Dump to stdout
odoo-bin db dump mydb

# pg_dump format
odoo-bin db dump mydb /backups/mydb.dump --format dump

# Zip without filestore
odoo-bin db dump mydb /backups/mydb.zip --no-filestore
```

### db load -- Load a Database Dump

```bash
# Load from file (DB name derived from filename if omitted)
odoo-bin db load mydb /backups/mydb.zip

# Load and neutralize
odoo-bin db load mydb /backups/mydb.zip --neutralize

# Force overwrite existing DB
odoo-bin db load mydb /backups/mydb.zip --force

# Load from URL
odoo-bin db load mydb https://example.com/backup.zip
```

### db duplicate -- Duplicate a Database

```bash
odoo-bin db duplicate source_db target_db

# Duplicate and neutralize
odoo-bin db duplicate source_db target_db --neutralize

# Force overwrite target
odoo-bin db duplicate source_db target_db --force
```

### db rename -- Rename a Database

```bash
odoo-bin db rename old_name new_name

# Force overwrite target if exists
odoo-bin db rename old_name new_name --force
```

### db drop -- Delete a Database

```bash
odoo-bin db drop mydb
```

---

## 12. Internationalization (i18n) Commands

### i18n import

```bash
# Import translation files (requires language code)
odoo-bin i18n import translations.po --language fr_FR -d mydb

# Import with overwrite of existing terms
odoo-bin i18n import translations.po --overwrite --language fr_FR -d mydb
```

### i18n export

```bash
# Export translations for modules (pot template by default)
odoo-bin i18n export sale purchase -d mydb

# Export specific languages
odoo-bin i18n export sale --languages fr_FR,es_ES -d mydb

# Export to a single output file
odoo-bin i18n export sale --languages fr_FR --output /tmp/sale_fr.po -d mydb

# Export as tgz archive
odoo-bin i18n export sale purchase --languages fr_FR --output /tmp/translations.tgz -d mydb

# Export to stdout
odoo-bin i18n export sale --languages fr_FR --output - -d mydb
```

### i18n loadlang

```bash
# Load and activate languages
odoo-bin i18n loadlang en -d mydb
odoo-bin i18n loadlang es es_AR -d mydb
odoo-bin i18n loadlang sr@latin -d mydb
```

---

## 13. Module Management Commands

All module subcommands support: `--addons-path`, `-c`, `-d`/`--database`.

### module install

```bash
# Install modules (database must be initialized first)
odoo-bin module install sale purchase -d mydb --addons-path=addons
```

### module uninstall

```bash
odoo-bin module uninstall sale -d mydb
```

### module upgrade

```bash
# Upgrade specific modules
odoo-bin module upgrade sale -d mydb

# Upgrade all installed modules
odoo-bin module upgrade all -d mydb
odoo-bin module upgrade base -d mydb

# Upgrade only modules with newer version on disk
odoo-bin module upgrade all --outdated -d mydb
```

### module forcedemo -- Force Demo Data Install

```bash
# WARNING: Cannot be undone. Back up first!
odoo-bin module forcedemo -d mydb
```

---

## 14. Scaffold -- Generate Module Skeleton

```bash
# Create module in specified directory
odoo-bin scaffold my_module /path/to/addons/

# Create module in current directory
odoo-bin scaffold my_module

# Use custom Jinja2 template directory
odoo-bin scaffold my_module /path/to/addons/ -t /path/to/template/
```

This creates the basic module structure with `__init__.py`, `__manifest__.py`, models, views, etc.

---

## 15. Populate -- Duplicate Data for Testing

Duplicates existing data with variation to respect UNIQUE constraints. Follows x2Many relationships.

```bash
# Populate specific models with a factor
odoo-bin populate -d mydb --models res.partner,account.move --factors 1000

# Custom separator for generated record names
odoo-bin populate -d mydb --models res.partner --factors 100 --sep "_"
```

| Flag | Description |
|---|---|
| `-d` | Database name |
| `--models` | Comma-separated model list |
| `--factors` | Comma-separated factors (last reused if fewer than models) |
| `--sep` | Separator for generated names |

---

## 16. Cloc -- Count Lines of Code

Counts relevant lines in Python, JavaScript, CSS, SCSS, and XML. Used for pricing maintenance of extra modules.

```bash
# Count lines in a database's extra modules
odoo-bin cloc --addons-path=addons -d mydb

# Count lines for a specific path
odoo-bin cloc -p addons/account

# Multiple paths
odoo-bin cloc -p addons/account -p addons/sale

# Use config file instead of --addons-path
odoo-bin cloc -c config.conf -d mydb

# Verbose output (per-file details)
odoo-bin cloc -p addons/account -v
```

### Excluded Files

By default, cloc excludes:
- `__manifest__.py` / `__openerp__.py`
- `static/lib/`
- `tests/` and `static/tests/`
- `migrations/` and `upgrades/`
- XML files in manifest `demo` or `demo_xml`

Custom exclusions via manifest:

```python
"cloc_exclude": [
    "lib/common.py",       # single file
    "data/*.xml",          # folder pattern
    "example/**/*",        # recursive folder
    "**/*.scss",           # all scss files
]
```

### Standard vs Extra Module Detection

Modules in the same parent directory as `base`, `web`, or `web_enterprise` are standard. All others are extra.

---

## 17. Neutralize -- Neutralize a Database

Disables external services (email, payments, etc.) in a database for safe testing.

```bash
# Neutralize a database
odoo-bin --addons-path addons neutralize -d mydb

# Output neutralization SQL to stdout instead of applying
odoo-bin --addons-path addons neutralize -d mydb --stdout
```

---

## 18. Obfuscate -- Obfuscate Database Data

Symmetrically obfuscates data for instructional/support purposes. NOT safe for full anonymization.

```bash
# Obfuscate with password
odoo-bin obfuscate -d mydb --pwd=mysecret

# Unobfuscate
odoo-bin obfuscate -d mydb --pwd=mysecret --unobfuscate

# Specify fields to obfuscate
odoo-bin obfuscate -d mydb --pwd=mysecret --fields res_partner.name,res_partner.email

# From a file
odoo-bin obfuscate -d mydb --pwd=mysecret --file fields_list.txt

# Exclude specific fields
odoo-bin obfuscate -d mydb --pwd=mysecret --exclude res_partner.phone

# Unobfuscate all fields (slower)
odoo-bin obfuscate -d mydb --pwd=mysecret --unobfuscate --allfields

# Vacuum after unobfuscation
odoo-bin obfuscate -d mydb --pwd=mysecret --unobfuscate --vacuum

# Commit per table (avoids timeout on large DBs)
odoo-bin obfuscate -d mydb --pwd=mysecret --pertablecommit

# Skip confirmation prompt
odoo-bin obfuscate -d mydb --pwd=mysecret -y
```

---

## 19. Deploy -- Remote Module Deployment

Uploads and installs a module on a remote Odoo server. Requires `base_import_module` installed on the server and admin credentials.

```bash
# Deploy to remote server
odoo-bin deploy /path/to/module https://remote.example.com \
    --db mydb \
    --login admin \
    --password admin

# Deploy to localhost (default URL)
odoo-bin deploy /path/to/module

# With SSL verification
odoo-bin deploy /path/to/module https://remote.example.com --verify-ssl

# Force re-initialization (updates noupdate=1 records)
odoo-bin deploy /path/to/module https://remote.example.com --force
```

---

## 20. upgrade_code -- Rewrite Source Code

Runs code migration scripts from `odoo/upgrade_code` for major version upgrades.

```bash
# Rewrite code from 18.0 to 19.0 (dry run)
odoo-bin upgrade_code --from 18.0 --to 19.0 --dry-run

# Apply changes
odoo-bin upgrade_code --from 18.0 --to 19.0

# Run a single script
odoo-bin upgrade_code --script /path/to/script.py

# Filter files
odoo-bin upgrade_code --from 18.0 --to 19.0 --glob "**/*.py"

# With custom addons path
odoo-bin upgrade_code --from 18.0 --to 19.0 --addons-path custom_addons
```

### Writing Code Upgrade Scripts

Script filename: `{version}-{name}.py`

Must expose an `upgrade` function:

```python
def upgrade(file_manager):
    files = (file for file in file_manager if file.path.suffix == '.py')
    for fileno, file in enumerate(files, start=1):
        file.content = file.content.replace("old_api_call", "new_api_call")
        file_manager.print_progress(fileno, len(files))
```

The `file_manager` provides files with:
- `path`: `pathlib.Path` on the file system
- `addon`: the addon the file belongs to
- `content`: re-writable file content (lazy loaded)
- `print_progress(current, total)`: progress output

---

## 21. Common Operational Patterns

### Install Module and Stop

```bash
odoo-bin -d mydb -i sale --stop-after-init --addons-path=addons
```

### Update All Modules

```bash
odoo-bin -d mydb -u all --stop-after-init
```

### Run Tests for a Module

```bash
odoo-bin -d testdb -i sale --test-enable --stop-after-init --addons-path=addons
```

### Run Specific Test

```bash
odoo-bin -d testdb --test-tags /sale:TestSaleOrder.test_confirm --stop-after-init
```

### Production Server with Workers

```bash
odoo-bin -c /etc/odoo/odoo.conf \
    --workers 4 \
    --limit-memory-hard 2684354560 \
    --limit-memory-soft 2147483648 \
    --limit-time-real 120 \
    --limit-time-cpu 60 \
    --proxy-mode
```

### Database Backup and Restore Workflow

```bash
# Backup
odoo-bin db dump prod_db /backups/prod_$(date +%Y%m%d).zip

# Restore to staging
odoo-bin db load staging_db /backups/prod_20260217.zip --force --neutralize
```

### Full Module Lifecycle

```bash
# Scaffold new module
odoo-bin scaffold my_module addons/

# Initialize DB and install
odoo-bin db init devdb --with-demo
odoo-bin module install my_module -d devdb --addons-path=addons

# Test
odoo-bin -d devdb --test-tags /my_module --stop-after-init --addons-path=addons

# Upgrade after changes
odoo-bin module upgrade my_module -d devdb --addons-path=addons
```
