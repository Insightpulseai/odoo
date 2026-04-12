# Docker

The local development stack runs Odoo CE 18 and PostgreSQL 16 via Docker Compose. An optional tools profile adds pgAdmin and Mailpit for database inspection and email testing.

## Development stack

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| `web` | Odoo CE 18 | `8069` | Odoo web server |
| `db` | PostgreSQL 16 | `5433` | Database (mapped to 5433 to avoid host conflicts) |

### Optional tools profile

| Service | Port | Purpose |
|---------|------|---------|
| pgAdmin | `5050` | Database administration UI |
| Mailpit | `8025` | Email capture and inspection |

Activate the tools profile:

```bash
docker compose --profile tools up -d
```

## Canonical setup

The Odoo instance runs from the `odoo18/` directory with `list_db=False`. Each environment uses a single, named database:

| Environment | Database |
|-------------|----------|
| Development | `odoo_dev` |
| Staging | `odoo_staging` |
| Production | `odoo` |

!!! warning "Database policy"
    Never create additional databases. Use only the canonical database for the target environment.

## Key commands

### Start the stack

```bash
docker compose up -d
```

### Install or update a module

```bash
docker compose exec web odoo -d odoo_dev -i <module_name> --stop-after-init
```

### Update an existing module

```bash
docker compose exec web odoo -d odoo_dev -u <module_name> --stop-after-init
```

### Verify module installation

Use `--stop-after-init` to confirm the module installs without runtime errors:

```bash
docker compose exec web odoo -d odoo_dev -i ipai_finance_ppm --stop-after-init
echo $?  # 0 = success
```

### Access the database

```bash
docker compose exec db psql -U odoo -d odoo_dev
```

### View logs

```bash
docker compose logs -f web
```

### Rebuild after Dockerfile changes

```bash
docker compose build --no-cache web
docker compose up -d
```

## Volume mounts

| Host path | Container path | Purpose |
|-----------|----------------|---------|
| `./addons` | `/mnt/extra-addons` | Custom `ipai_*` modules |
| `./oca_addons` | `/mnt/oca-addons` | OCA community modules |
| `./config` | `/etc/odoo` | Odoo configuration |
| `pgdata` (named volume) | `/var/lib/postgresql/data` | PostgreSQL data persistence |

## Health check

Verify the stack is running:

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/login
# Expected: 200
```
