# OCA Pinned Stack for DigitalOcean

Production-ready Odoo CE + OCA stack with pinned dependencies, CI/CD, TLS, and backups.

## Quick Start

```bash
# 1. Clone OCA repos
make fetch

# 2. Start stack (development)
docker compose up -d

# 3. Start stack (production with TLS)
DOMAIN=odoo.example.com docker compose -f docker-compose.yml -f docker-compose.caddy.yml up -d

# 4. Verify deployment
./scripts/oca-verify.sh
```

## Directory Structure

```
infra/do-oca-stack/
├── addons/
│   ├── custom/          # Your custom modules
│   └── oca/             # OCA repos (managed by Makefile)
├── config/
│   ├── odoo.conf        # Odoo configuration
│   └── Caddyfile        # Caddy reverse proxy config
├── scripts/
│   ├── backup-do-spaces.sh  # Backup to DigitalOcean Spaces
│   ├── oca-verify.sh        # Deployment verification
│   └── oca-rollback.sh      # Rollback procedures
├── docker-compose.yml       # Base stack (Odoo + PostgreSQL)
├── docker-compose.caddy.yml # TLS proxy overlay
├── oca-requirements.txt     # OCA repos and branches
├── oca.lock                 # Pinned commit SHAs
└── Makefile                 # OCA repo management
```

## OCA Module Management

### Fetch repositories

```bash
make fetch
```

### Update to latest (from branch)

```bash
make update
```

### Lock current SHAs

```bash
make lock
```

### Verify repos match lock

```bash
make verify
```

### Add a new OCA repo

1. Edit `oca-requirements.txt`:
   ```
   repo-name https://github.com/OCA/repo-name.git 18.0
   ```
2. Run `make fetch`
3. Run `make lock` to pin the SHA

## Deployment

### Manual deploy

```bash
ssh user@droplet
cd /opt/odoo-oca
git pull origin main --ff-only
make verify || make fetch
docker compose pull
docker compose up -d
./scripts/oca-verify.sh
```

### CI/CD deploy

Push to `main` branch triggers `.github/workflows/deploy-do-oca.yml`:
1. Pre-flight validation
2. Pre-deploy backup
3. Deploy via SSH
4. Post-deploy verification

Required secrets:
- `DO_DROPLET_HOST` - Droplet IP/hostname
- `DO_SSH_PRIVATE_KEY` - SSH key for deployment
- `DO_SPACES_ACCESS_KEY` (optional) - For S3 backups
- `DO_SPACES_SECRET_KEY` (optional)

## Backups

### Manual backup to DO Spaces

```bash
DO_SPACES_BUCKET=my-bucket ./scripts/backup-do-spaces.sh
```

### Scheduled backups (cron)

```bash
# Add to crontab on droplet
0 3 * * * cd /opt/odoo-oca && ./scripts/backup-do-spaces.sh my-bucket >> /var/log/odoo-backup.log 2>&1
```

### Restore from backup

```bash
./scripts/oca-rollback.sh list                    # See available backups
./scripts/oca-rollback.sh backup backups/20260124-030000
```

## Rollback

### Code rollback (git)

```bash
./scripts/oca-rollback.sh list          # See recent commits
./scripts/oca-rollback.sh git abc1234   # Rollback to commit
```

### Database rollback

```bash
./scripts/oca-rollback.sh backup backups/20260124-030000
```

## TLS Configuration

The Caddy overlay provides automatic Let's Encrypt certificates.

### Enable TLS

```bash
DOMAIN=odoo.example.com \
ACME_EMAIL=admin@example.com \
docker compose -f docker-compose.yml -f docker-compose.caddy.yml up -d
```

### Requirements

- DNS A/AAAA record pointing to droplet
- Ports 80 and 443 open in firewall

## Performance Tuning

Edit `config/odoo.conf` based on droplet size:

| Droplet | vCPU | RAM | workers | max_cron_threads |
|---------|------|-----|---------|------------------|
| Basic | 1 | 2GB | 1 | 1 |
| Standard | 2 | 4GB | 2 | 1 |
| Performance | 4 | 8GB | 4 | 2 |
| High Memory | 8 | 16GB | 6 | 2 |

## Troubleshooting

### Check logs

```bash
docker compose logs -f odoo
docker compose logs -f db
docker compose logs -f caddy  # If using TLS
```

### Reset database

```bash
docker compose down -v
docker compose up -d
```

### Verify health

```bash
./scripts/oca-verify.sh --json  # Machine-readable output
```
