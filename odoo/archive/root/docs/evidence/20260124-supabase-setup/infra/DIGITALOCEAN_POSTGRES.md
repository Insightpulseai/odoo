# DigitalOcean PostgreSQL Cluster — Infrastructure Evidence

**Date**: 2026-01-24
**Scope**: Production Odoo Database

---

## Cluster Configuration

| Property | Value |
|----------|-------|
| **Cluster Name** | odoo-db-sgp1 |
| **Project** | tbwa-smp |
| **Region** | SGP1 (Singapore) |
| **PostgreSQL Version** | 16 |
| **Configuration Type** | Primary only |

## Resources

| Resource | Specification |
|----------|---------------|
| RAM | 2 GB |
| CPU | 1 vCPU |
| Disk | 30 GiB |
| Standby Nodes | None |
| Read-Only Nodes | None |

## Cost

| Item | Amount |
|------|--------|
| Monthly Rate | $30.45 |
| Billing | Prorated |

## Connection Details

| Property | Value |
|----------|-------|
| Host | `odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com` |
| Port | `25060` |
| Database | `defaultdb` |
| Username | `doadmin` |
| SSL Mode | `require` |
| Network | Public + VPC |

### Connection String Template

```
postgresql://doadmin:<PASSWORD>@odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com:25060/defaultdb?sslmode=require
```

### VPC Network

| Property | Value |
|----------|-------|
| VPC Name | default-sgp1 |
| CIDR | 10.104.0.0/20 |

## Maintenance Window

| Property | Value |
|----------|-------|
| Day | Wednesday |
| Time | 10PM - 2AM (GMT+8) |
| Type | Automatic minor updates and patches |

## Backup & Recovery

| Feature | Status |
|---------|--------|
| Point-in-Time Recovery | Enabled |
| Retention | 7 days |
| Restore Granularity | Any transaction |

## Recommendations

### High Availability (Not Currently Configured)

| Recommendation | Priority | Rationale |
|----------------|----------|-----------|
| Add Standby Node | P1 | Prevent downtime and data loss |
| Add Read-Only Node | P2 | Improve read performance |

**Cost Impact:**
- Standby node: ~$30/month additional
- Read-only node: ~$15-30/month additional

### Connection Pooling

| Recommendation | Priority | Rationale |
|----------------|----------|-----------|
| Enable Connection Pool | P1 | Prevent "too many connections" errors |
| Pool Mode | Transaction | Best for Odoo workloads |

### Security

| Item | Status | Action |
|------|--------|--------|
| SSL Required | ✅ Enabled | None |
| VPC Access | ✅ Available | Use for internal services |
| Firewall | ⚠️ Check | Verify trusted sources only |

## Environment Variable Reference

Add to `.env` (never commit actual values):

```bash
# DigitalOcean Managed PostgreSQL
DO_PG_HOST=odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com
DO_PG_PORT=25060
DO_PG_USER=doadmin
DO_PG_PASSWORD=<from DO dashboard>
DO_PG_DATABASE=defaultdb
DO_PG_SSLMODE=require

# Full connection string
DO_DATABASE_URL=postgresql://${DO_PG_USER}:${DO_PG_PASSWORD}@${DO_PG_HOST}:${DO_PG_PORT}/${DO_PG_DATABASE}?sslmode=require
```

## Migration Commands

### Restore from local dump

```bash
PGPASSWORD=<password> pg_restore \
  -U doadmin \
  -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 \
  -d defaultdb \
  <local-pg-dump-path>
```

### Dump current database

```bash
PGPASSWORD=<password> pg_dump \
  -U doadmin \
  -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 \
  -d defaultdb \
  -F c \
  -f odoo-db-backup-$(date +%Y%m%d).dump
```

## Verification Commands

### Test connection

```bash
PGPASSWORD=<password> psql \
  -U doadmin \
  -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 \
  -d defaultdb \
  -c "SELECT version();"
```

### Check database size

```bash
PGPASSWORD=<password> psql \
  -U doadmin \
  -h odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com \
  -p 25060 \
  -d defaultdb \
  -c "SELECT pg_size_pretty(pg_database_size('defaultdb'));"
```

## Related Resources

- [DigitalOcean Database Docs](https://docs.digitalocean.com/products/databases/)
- [PostgreSQL 16 Release Notes](https://www.postgresql.org/docs/16/release-16.html)
- Download CA certificate from DO dashboard for SSL verification
