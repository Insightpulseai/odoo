# Runbooks

Common operational procedures for the odoo-ce platform.

## Deployment

### Deploy to Production

```bash
# 1. Ensure all CI gates pass on main
gh run list --workflow "ci-odoo-ce.yml" --repo jgtolentino/odoo-ce

# 2. SSH to production server
ssh root@<PRODUCTION_IP>

# 3. Pull latest changes
cd /opt/odoo-ce/repo
git pull origin main

# 4. Rebuild and restart containers
docker compose build --no-cache
docker compose down && docker compose up -d

# 5. Verify health
curl -s http://localhost:8069/web/health
```

### Deploy IPAI Modules

```bash
# Run deployment script
./scripts/deploy-odoo-modules.sh

# Or manually update specific module
docker compose exec odoo-core odoo -d odoo_core -u ipai_finance_ppm --stop-after-init

# Verify module status
docker compose exec odoo-core odoo shell -d odoo_core <<< "print(env['ir.module.module'].search([('name','=','ipai_finance_ppm')]).state)"
```

## Backup & Restore

### Database Backup

```bash
# Create backup
docker compose exec postgres pg_dump -U odoo odoo_core > backup_$(date +%Y%m%d_%H%M%S).sql

# Compressed backup
docker compose exec postgres pg_dump -U odoo odoo_core | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

### Database Restore

```bash
# Stop Odoo first
docker compose stop odoo-core

# Drop existing database
docker compose exec postgres dropdb -U odoo odoo_core

# Create fresh database
docker compose exec postgres createdb -U odoo odoo_core

# Restore backup
cat backup.sql | docker compose exec -T postgres psql -U odoo odoo_core

# Start Odoo
docker compose start odoo-core
```

### Filestore Backup

```bash
# Backup filestore
tar -czf filestore_$(date +%Y%m%d_%H%M%S).tar.gz /var/lib/odoo/.local/share/Odoo/filestore/

# Restore filestore
tar -xzf filestore_backup.tar.gz -C /var/lib/odoo/.local/share/Odoo/filestore/
```

## Troubleshooting

### Odoo Won't Start

```bash
# Check logs
docker compose logs -f odoo-core

# Check database connection
docker compose exec postgres psql -U odoo -c "SELECT 1"

# Check disk space
df -h

# Check memory
free -h
```

### Module Installation Failed

```bash
# Check Odoo logs for errors
docker compose logs odoo-core | grep -i error

# Try with verbose logging
docker compose exec odoo-core odoo -d odoo_core -i module_name --log-level=debug --stop-after-init
```

### Database Connection Issues

```bash
# Check PostgreSQL status
docker compose ps postgres
docker compose logs postgres

# Test connection
docker compose exec postgres pg_isready -U odoo

# Restart PostgreSQL
docker compose restart postgres
```

### Permission Errors (SCSS)

```bash
# Fix addon permissions
./scripts/verify-addon-permissions.sh

# Or manually
ssh root@<SERVER_IP>
cd /opt/odoo-ce/repo/addons
chown -R 100:101 ipai ipai_theme_tbwa*
chmod -R 755 ipai ipai_theme_tbwa*
docker restart odoo-prod
```

## Maintenance

### Clear Browser Cache

Instruct users to:
1. Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
2. Clear browser cache for the Odoo domain

### Clear Odoo Assets Cache

```bash
# Clear assets
docker compose exec odoo-core odoo shell -d odoo_core << 'EOF'
env['ir.attachment'].search([('res_model', '=', 'ir.ui.view'), ('type', '=', 'binary')]).unlink()
env.cr.commit()
EOF

# Restart Odoo
docker compose restart odoo-core
```

### Update OCA Modules

```bash
# Update OCA submodules
git submodule update --remote --merge

# Commit changes
git add addons/oca
git commit -m "chore(oca): update OCA modules"
git push
```

## Monitoring

### Health Checks

```bash
# Basic health
curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/health

# Database status
docker compose exec postgres psql -U odoo -c "SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) FROM pg_database"

# Container status
docker compose ps
```

### Log Analysis

```bash
# Recent errors
docker compose logs --since 1h odoo-core | grep -i error

# Access patterns
docker compose logs --since 1h odoo-core | grep "HTTP/1" | awk '{print $1}' | sort | uniq -c | sort -rn

# Slow queries
docker compose exec postgres psql -U odoo -c "SELECT query, calls, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10"
```

## Emergency Procedures

### Rollback Deployment

```bash
# Identify previous working commit
git log --oneline -10

# Checkout previous version
git checkout <PREVIOUS_SHA>

# Rebuild and restart
docker compose build --no-cache
docker compose down && docker compose up -d
```

### Database Point-in-Time Recovery

```bash
# If using continuous archiving, restore to specific time
# (Requires WAL archiving to be configured)

# Stop Odoo
docker compose stop odoo-core

# Restore from base backup + WAL
# ... (depends on backup configuration)

# Start Odoo
docker compose start odoo-core
```

### Contact Information

- **On-Call**: Check PagerDuty rotation
- **Slack**: #odoo-ops
- **Escalation**: @tech-leads
