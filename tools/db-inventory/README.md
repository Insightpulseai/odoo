# Database Instance Inventory Scanner

A comprehensive tool for auditing all database and datastore references across a repository.

## Features

- **Multi-datastore support**: PostgreSQL, MySQL, MSSQL, SQLite, Redis, MongoDB, ClickHouse, Elasticsearch, OpenSearch, Supabase
- **Secret redaction**: Automatically redacts passwords, tokens, API keys, and other sensitive data
- **Multiple output formats**: JSON, CSV, and Markdown reports
- **Extensive detection**: Environment files, Docker Compose, Kubernetes manifests, Terraform, Prisma schemas, Python/JS configs, documentation
- **Odoo-aware**: Special handling for Odoo database configuration patterns
- **Fast and offline**: No network calls, works entirely on local files

## Installation

No installation required. Uses Python 3 standard library.

Optional: Install PyYAML for better Docker Compose parsing:
```bash
pip install pyyaml
```

## Usage

### Basic Usage

```bash
# From repository root
python3 tools/db-inventory/inventory.py

# Explicit root path
python3 tools/db-inventory/inventory.py --root /path/to/repo
```

### Output

By default, generates 4 files in `tools/db-inventory/output/`:

| File | Description |
|------|-------------|
| `db_inventory.json` | Machine-readable full inventory |
| `db_inventory.csv` | Spreadsheet-compatible format |
| `db_inventory.md` | Detailed human-readable report |
| `db_inventory_summary.md` | High-level summary statistics |

### CLI Options

```bash
python3 tools/db-inventory/inventory.py [OPTIONS]

Options:
  --root, -r PATH         Repository root (default: current directory)
  --out, -o PATH          Output directory (default: tools/db-inventory/output)
  --format, -f FORMATS    Output formats: json,csv,md (default: all)
  --include-datastores    Only include specific types (e.g., postgres,mysql)
  --exclude-dirs          Additional directories to exclude
  --max-file-mb SIZE      Maximum file size in MB (default: 5)
  --verbose, -v           Verbose output
  --version               Show version
```

### Examples

```bash
# Verbose scan with specific formats
python3 tools/db-inventory/inventory.py --verbose --format json,md

# Only PostgreSQL and MySQL
python3 tools/db-inventory/inventory.py --include-datastores postgres,mysql

# Custom output location
python3 tools/db-inventory/inventory.py --out ./audit-results

# Exclude additional directories
python3 tools/db-inventory/inventory.py --exclude-dirs archive,legacy,old
```

## Detection Coverage

### File Types Scanned

| Type | Extensions/Patterns |
|------|---------------------|
| Environment files | `.env`, `.env.*`, `*.env` |
| Docker | `docker-compose*.yml`, `compose*.yml` |
| Kubernetes | `k8s/*.yaml`, manifests |
| Terraform | `*.tf` |
| Ansible | `*.yml` in ansible directories |
| Helm | Chart templates |
| App configs | `*.yaml`, `*.yml`, `*.json`, `*.toml`, `*.ini`, `*.cfg` |
| Prisma | `schema.prisma` |
| Python | `*.py` (connection strings, config) |
| JavaScript/TypeScript | `*.js`, `*.ts`, `*.mjs`, `*.tsx` |
| Documentation | `*.md` (with connection examples) |
| Odoo | `odoo.conf`, `odoo*.conf` |

### Environment Variables Detected

- `DATABASE_URL`, `POSTGRES_URL`, `MYSQL_URL`, `REDIS_URL`
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`
- `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_DB_URL`
- And many more patterns...

### URL Formats Detected

- `postgres://`, `postgresql://`, `jdbc:postgresql://`
- `mysql://`, `mysql+pymysql://`, `jdbc:mysql://`
- `mssql://`, `jdbc:sqlserver://`
- `redis://`, `rediss://`
- `mongodb://`, `mongodb+srv://`
- `clickhouse://`
- `elasticsearch://`, `opensearch://`

## Output Schema

### JSON Structure

```json
{
  "generated_at": "2025-01-15T10:30:00+00:00",
  "repo_root": "/path/to/repo",
  "total_findings": 42,
  "findings": [
    {
      "id": "abc123def456...",
      "datastore_type": "postgres",
      "instance_name": "odoo",
      "host": "db.example.com",
      "port": "5432",
      "database": "odoo_prod",
      "user": "odoo_user",
      "ssl_mode": "require",
      "url_redacted": "postgres://odoo_user:***REDACTED***@db.example.com:5432/odoo_prod",
      "secrets_present": true,
      "secret_fields": ["password"],
      "source": {
        "file_path": "docker-compose.yml",
        "line_start": 15,
        "line_end": 15,
        "snippet_redacted": "DATABASE_URL=***REDACTED***",
        "detector": "docker_compose"
      },
      "tags": ["prod", "odoo", "docker"]
    }
  ]
}
```

### Tags

Findings are automatically tagged based on context:

| Tag | Meaning |
|-----|---------|
| `prod`, `staging`, `dev`, `test`, `local` | Environment |
| `odoo`, `superset`, `supabase`, `n8n`, `mattermost` | Application |
| `docker`, `k8s`, `terraform`, `ansible`, `helm`, `ci` | Infrastructure |

## Security

### What Gets Redacted

- Passwords in URLs and environment variables
- JWT tokens (`eyJ...`)
- API keys and service role keys
- Private keys and secrets
- Long base64-encoded strings (likely tokens)

### What Remains Visible

- Hostnames and IP addresses
- Port numbers
- Database names
- Usernames
- SSL modes

## CI Integration

Add to your CI pipeline for drift detection:

```yaml
# GitHub Actions example
name: DB Inventory Audit
on:
  schedule:
    - cron: '0 0 * * *'  # Nightly
  push:
    branches: [main]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run inventory scan
        run: python3 tools/db-inventory/inventory.py --format json
      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: db-inventory
          path: tools/db-inventory/output/
```

## Troubleshooting

### YAML parsing issues

If Docker Compose files aren't being fully parsed, install PyYAML:
```bash
pip install pyyaml
```

### Large files skipped

Increase the file size limit:
```bash
python3 tools/db-inventory/inventory.py --max-file-mb 10
```

### Missing findings

Run with verbose mode to see what's being scanned:
```bash
python3 tools/db-inventory/inventory.py --verbose
```

## License

Part of the odoo-ce project.
