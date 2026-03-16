# DigitalOcean Managed PostgreSQL - Documentation Review

**Date:** 2026-01-19
**Source:** https://docs.digitalocean.com/products/databases/postgresql/
**Status:** Research Complete

---

## Supported Versions

| Version | Status |
|---------|--------|
| PostgreSQL 18 | Available (Latest) |
| PostgreSQL 17 | Available (GA: Feb 2025) |
| PostgreSQL 16 | Available |
| PostgreSQL 15 | Available |
| PostgreSQL 14 | Available |
| PostgreSQL 13 | Available |

**Upgrade Path:** Zero-downtime upgrades available via Control Panel.

---

## Connection Pooling (PgBouncer)

### Configuration

- **Built-in pooler:** PgBouncer
- **Pool port:** 25061 (vs 25060 for direct)
- **Max pools per cluster:** 21
- **Max connections:** Up to 1,000 (plan-dependent)
- **Formula:** 25 connections per 1 GiB RAM (3 reserved for maintenance)

### Pool Modes

| Mode | Use Case | Limitations |
|------|----------|-------------|
| **Transaction** | High idle connections, large client pools | No prepared statements, no `pg_dump` |
| **Session** | Prepared statements, advisory locks, LISTEN/NOTIFY | Holds connection until disconnect |
| **Statement** | Single statements only | Most restrictive |

### Best Practices for Odoo

```
# Odoo recommendation: Transaction mode
# Odoo does not rely on session-level features in standard operation
pool_mode = transaction

# However, if using custom SQL with prepared statements:
pool_mode = session
```

---

## Backups & Recovery

| Feature | Details |
|---------|---------|
| **Frequency** | Daily full backups |
| **WAL backup interval** | Every 5 minutes |
| **PITR retention** | 7 days |
| **Automatic recovery** | Yes (uses latest backup + WAL) |
| **Cost** | Included at no additional fee |

**Warning:** Up to 5 minutes of data may be lost if cluster fails between WAL backups.

---

## High Availability

| Feature | Details |
|---------|---------|
| **Automated failover** | All clusters |
| **Standby nodes** | Required for true HA |
| **Max nodes per cluster** | 3 |
| **Failover detection** | Automatic |

### Node Types

- **Primary:** Read/write operations
- **Standby:** Failover target, no direct access
- **Read-only:** Offload read traffic, cross-region supported

---

## Security

| Feature | Status |
|---------|--------|
| **Encryption in transit** | SSL/TLS required |
| **Encryption at rest** | Yes |
| **VPC isolation** | Yes (private network) |
| **IP allowlisting** | Required for public access |
| **Superuser access** | NOT available |

---

## Monitoring & Alerts

### Built-in Metrics

- CPU utilization
- Memory usage
- Disk I/O
- Connection count
- Cache hit ratio
- Sequential vs indexed scans
- Replication lag (bytes)
- Throughput

### Alert Channels

- Email
- Slack

### Prometheus Integration

```bash
# Get metrics endpoint
curl -X GET \
  -H "Authorization: Bearer $DIGITALOCEAN_TOKEN" \
  "https://api.digitalocean.com/v2/databases/{cluster-id}/metrics/credentials"
```

---

## Storage

| Feature | Details |
|---------|---------|
| **Max storage (PostgreSQL)** | 30 TB |
| **Autoscaling** | GA (General Availability) |
| **Independent scaling** | CPU/RAM separate from storage |
| **Reduction** | Allowed (with constraints) |

---

## Extensions

### pgvector Support

```sql
-- Install pgvector (v0.7.2+)
CREATE EXTENSION vector;

-- Note: Use 'vector' not 'pgvector'
```

### Other Supported Extensions

- PostGIS
- hstore
- bloom
- h3
- uuid-ossp
- pg_trgm
- (See full list in DO documentation)

---

## Limits Summary

| Limit | Value |
|-------|-------|
| Clusters per account | 10 (default, can request increase) |
| Nodes per cluster | 3 |
| Pools per cluster | 21 |
| Connections (max) | 1,000 |
| PITR retention | 7 days |
| Storage (max) | 30 TB |
| Supported versions | 13, 14, 15, 16, 17, 18 |

---

## Pricing

- **Entry tier:** $15.15/month
- **Flat pricing:** Same across all regions
- **Storage:** Billed separately when scaling independently

---

## Relevance to IPAI Stack

### Current Configuration (docker-compose.yml)

The IPAI stack currently uses a local PostgreSQL 15 container:

```yaml
postgres:
  image: postgres:15
  environment:
    POSTGRES_USER: odoo
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

### Migration Considerations

1. **Connection pooling:** Enable transaction mode for Odoo workloads
2. **pgvector:** Available for AI/embedding features
3. **Backups:** Automated vs manual container backups
4. **HA:** Multi-node clusters for production
5. **Monitoring:** Native metrics vs manual Prometheus setup

### Recommended DO PostgreSQL Configuration

```
Version: PostgreSQL 17 or 18
Plan: Basic (start), Professional (production)
Nodes: 2+ for HA
Pool mode: Transaction
Storage: Start with plan default, enable autoscaling
Region: Match droplet region (e.g., sgp1)
```

---

## Sources

- [PostgreSQL Overview](https://docs.digitalocean.com/products/databases/postgresql/)
- [Connection Pooling](https://docs.digitalocean.com/products/databases/postgresql/how-to/manage-connection-pools/)
- [PostgreSQL Limits](https://docs.digitalocean.com/products/databases/postgresql/details/limits/)
- [Supported Extensions](https://docs.digitalocean.com/products/databases/postgresql/details/supported-extensions/)
- [Monitoring Clusters](https://docs.digitalocean.com/products/databases/postgresql/how-to/monitor-clusters/)
- [Alert Setup](https://docs.digitalocean.com/products/databases/postgresql/how-to/set-up-alerts/)
- [PostgreSQL 17 Announcement](https://www.digitalocean.com/blog/postgresql-17)
- [Managed Databases 2025 Updates](https://www.digitalocean.com/blog/managed-databases-updates-h2)
