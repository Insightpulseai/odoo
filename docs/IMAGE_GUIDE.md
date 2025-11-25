# Target Image Documentation

**Image Tag:** `ghcr.io/jgtolentino/odoo-ce:latest`
**Base System:** Odoo 18.0 (Debian Bookworm)
**Architecture:** AMD64 / ARM64 (Multi-arch)
**Registry:** GitHub Container Registry (ghcr.io)

---

## 1. Image Anatomy

This image is **immutable**. It bundles the core application code, dependencies, and configuration into a single artifact.

| Layer | Path | Description |
|:------|:-----|:------------|
| **Base** | `/usr/lib/python3/dist-packages/odoo` | Official Odoo 18.0 core source code |
| **Config** | `/etc/odoo/odoo.conf` | Production-optimized configuration (Workers, Limits) |
| **Addons** | `/mnt/extra-addons` | **Your Custom Code.** Contains `ipai_*` and `tbwa_*` modules |
| **Deps** | `/usr/local/lib/python3.10/site-packages` | Python libs from `requirements.txt` |

### Baked-In Modules

| Module | Category | Description |
|--------|----------|-------------|
| `ipai_finance_ppm` | Finance PPM | Core finance project portfolio management |
| `ipai_ppm_monthly_close` | Finance PPM | Monthly closing workflow automation |
| `ipai_finance_monthly_closing` | Finance PPM | Monthly closing templates |
| `ipai_finance_ppm_dashboard` | Finance PPM | ECharts-based PPM dashboard |
| `ipai_docs` | Documents | Document management system |
| `ipai_docs_project` | Documents | Project-document integration |
| `ipai_ce_cleaner` | UI/Theme | CE UI cleanup and branding |
| `tbwa_spectra_integration` | Integration | TBWA Spectra expense integration |

---

## 2. Build Process

To create a new version of the target image after changing code:

```bash
# 1. Build the image locally
docker build -t ghcr.io/jgtolentino/odoo-ce:latest .

# 2. Tag with commit SHA for traceability
docker tag ghcr.io/jgtolentino/odoo-ce:latest \
           ghcr.io/jgtolentino/odoo-ce:sha-$(git rev-parse --short HEAD)

# 3. Test strictly (Run only this container, no volumes)
docker run --rm -p 8069:8069 \
  -e HOST=localhost \
  ghcr.io/jgtolentino/odoo-ce:latest

# 4. Login to Registry
echo $GHCR_TOKEN | docker login ghcr.io -u jgtolentino --password-stdin

# 5. Push to Registry (GitHub Container Registry)
docker push ghcr.io/jgtolentino/odoo-ce:latest
docker push ghcr.io/jgtolentino/odoo-ce:sha-$(git rev-parse --short HEAD)
```

---

## 3. Runtime Environment Variables

These variables **must** be passed to the container at runtime (via `.env` or CI/CD secrets).

### Required Variables

| Variable | Default | Purpose |
|:---------|:--------|:--------|
| `DB_HOST` | `db` | Hostname of the PostgreSQL service |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_USER` | `odoo` | Database username |
| `DB_PASSWORD` | **REQUIRED** | Database password (no default!) |
| `ADMIN_PASSWD` | **REQUIRED** | Master password for creating/dropping databases |

### Performance Tuning

| Variable | Default | Purpose |
|:---------|:--------|:--------|
| `WORKERS` | `4` | Number of Gunicorn workers (rec: 2 x CPU_CORES) |
| `MAX_CRON_THREADS` | `2` | Background job threads |
| `DB_MAXCONN` | `64` | Max database connections |
| `LIMIT_MEMORY_HARD` | `2684354560` | Hard memory limit (2.5GB) |
| `LIMIT_MEMORY_SOFT` | `2147483648` | Soft memory limit (2GB) |

### Network/Proxy

| Variable | Default | Purpose |
|:---------|:--------|:--------|
| `PROXY_MODE` | `True` | Must be True when running behind Nginx/Traefik |
| `ODOO_PORT` | `8069` | HTTP port Odoo listens on |

---

## 4. Volume Strategy

### Production (Immutable)
Do **NOT** mount local folders to `/mnt/extra-addons`. The code is already inside the image.

```yaml
# docker-compose.prod.yml
services:
  odoo:
    image: ghcr.io/jgtolentino/odoo-ce:latest
    volumes:
      - odoo-filestore:/var/lib/odoo  # Only filestore is persistent
```

### Development (Hot-Reload)
Mount `./addons:/mnt/extra-addons` to override the baked-in code for hot-reloading:

```yaml
# docker-compose.yml (development)
services:
  odoo:
    image: odoo:18.0
    volumes:
      - ./addons:/mnt/extra-addons:rw  # Override for development
      - ./oca:/mnt/oca-addons:rw
      - odoo-filestore:/var/lib/odoo
```

---

## 5. Health Checks

The image includes a built-in health check endpoint:

```bash
# Check if Odoo is responding
curl -f http://localhost:8069/web/health

# Expected response: {"status": "pass"}
```

Docker Compose health check configuration:

```yaml
healthcheck:
  test: ["CMD-SHELL", "curl -f http://localhost:8069/web/health || exit 1"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s
```

---

## 6. Module Installation

After deploying a new image, modules need to be upgraded:

```bash
# SSH into the server
ssh user@your-server

# Update modules inside running container
docker exec -it odoo-ce odoo -d odoo -u ipai_finance_ppm --stop-after-init

# Or restart with update flag
docker compose -f docker-compose.prod.yml exec odoo \
  odoo -d odoo -u all --stop-after-init
```

---

## 7. Rollback Procedure

If the new image fails, rollback to a previous SHA:

```bash
# 1. Find the previous working tag in GitHub Packages
# https://github.com/jgtolentino/odoo-ce/pkgs/container/odoo-ce

# 2. Edit docker-compose.prod.yml to specific tag
image: ghcr.io/jgtolentino/odoo-ce:sha-057bb3a

# 3. Redeploy
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

---

## 8. Security Considerations

1. **Never expose port 8069 directly** - Always use Nginx/Traefik for SSL termination
2. **Rotate ADMIN_PASSWD regularly** - This is the master database password
3. **Use secrets management** - Store passwords in GitHub Secrets, not in files
4. **Image scanning** - Run `trivy image ghcr.io/jgtolentino/odoo-ce:latest` before deploying

---

**Last Updated:** 2025-11-25
**Maintainer:** InsightPulseAI Team
