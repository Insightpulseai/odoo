# PostgreSQL 16 Release Features

**Release Date:** September 14, 2023
**Source:** https://www.postgresql.org/docs/16/release-16.html
**Status:** Production Ready

---

## Performance Improvements

### Bulk Data Loading (COPY)

- Up to **300% performance improvement** in some cases
- Improvements for both single and concurrent operations

### Query Planner Optimizations

| Feature | Improvement |
|---------|-------------|
| FULL/RIGHT joins | Can now be parallelized |
| DISTINCT/ORDER BY aggregates | Better optimized plans |
| SELECT DISTINCT | Incremental sorts |
| Window functions | More efficient execution |

### SIMD Acceleration

- Support for both **x86** and **ARM** architectures
- Used for:
  - ASCII string processing
  - JSON string processing
  - Array searches
  - Sub-transaction searches

### Vacuum Improvements

- Page freezing during non-freeze operations where appropriate
- Reduces need for full-table freeze vacuums

---

## Logical Replication Enhancements

### Parallel Apply

```sql
-- Subscribers can now apply large transactions using parallel workers
-- Significant improvement for high-throughput replication
```

### Non-Primary-Key Tables

- Subscribers can use **B-tree indexes** instead of sequential scans
- Improves performance for tables without primary keys

### Standby Replication

- **Logical replication from physical standbys** now supported
- Standbys can publish logical changes to other servers
- Reduces load on primary

### Bidirectional Replication (Initial)

- Beginning support for bi-directional logical replication
- Replicate data between two tables from different publishers

---

## SQL/JSON Features

New constructors and predicates from SQL/JSON standard:

```sql
-- JSON Array Constructor
SELECT JSON_ARRAY(1, 2, 'three');
-- Result: [1, 2, "three"]

-- JSON Array Aggregation
SELECT JSON_ARRAYAGG(column_name) FROM table_name;

-- IS JSON Predicate
SELECT value IS JSON;
SELECT value IS JSON OBJECT;
SELECT value IS JSON ARRAY;
SELECT value IS JSON SCALAR;
```

---

## Monitoring & Statistics

### pg_stat_io (New)

```sql
-- New view for I/O metrics
SELECT * FROM pg_stat_io;

-- Provides granular analysis of I/O access patterns:
-- - Reads/writes by backend type
-- - Buffer operations
-- - I/O timing
```

### Table Scan Tracking

```sql
-- New field in pg_stat_all_tables
SELECT relname, last_seq_scan, last_idx_scan
FROM pg_stat_all_tables;

-- Shows timestamp of last table/index scan
```

### auto_explain Improvements

- Logs values passed into parameterized statements
- More readable query plans

---

## Security & Access Control

### Configuration File Enhancements

**pg_hba.conf / pg_ident.conf:**
- Regular expression matching for user/database names
- Include directives for external configuration files

```
# Example: regex matching in pg_hba.conf
host    all    /^app_user_\d+$/    192.168.0.0/24    scram-sha-256

# Include external files
include /etc/postgresql/hba.d/custom.conf
```

### New Predefined Role

```sql
-- pg_create_subscription role
-- Grants ability to create new logical subscriptions
GRANT pg_create_subscription TO app_user;
```

---

## Relevance to IPAI Stack

### Current Stack Uses PostgreSQL 15

The IPAI stack specifies PostgreSQL 15 in docker-compose:

```yaml
postgres:
  image: postgres:15
```

### Upgrade Considerations for PG 16

| Feature | Benefit for IPAI |
|---------|-----------------|
| COPY performance | Faster data imports |
| Parallel replication | Better Odoo replication |
| pg_stat_io | Enhanced monitoring |
| SIMD JSON | Faster API responses |

### Migration Path

1. Test with PG 16 in development
2. Validate Odoo 18 compatibility
3. Use DigitalOcean zero-downtime upgrade
4. Enable new monitoring features

---

## Sources

- [PostgreSQL 16 Released!](https://www.postgresql.org/about/news/postgresql-16-released-2715/)
- [PostgreSQL 16 Release Notes](https://www.postgresql.org/docs/release/16.0/)
- [AWS PostgreSQL 16 Features Synopsis](https://aws.amazon.com/blogs/database/synopsis-of-several-compelling-features-in-postgresql-16/)
- [PostgreSQL 16 Press Kit](https://www.postgresql.org/about/press/presskit16/)
- [ScaleGrid PostgreSQL 16 Features](https://scalegrid.io/blog/postgresql-16-features/)
