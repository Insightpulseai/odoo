# Odoo CE 18 – Database & Worker Tuning

Last updated: 2025-11-24
Scope: `erp.insightpulseai.net` – single-instance Odoo 18 CE + `ipai_*` modules

---

## 1. Objectives

- Prevent connection pool exhaustion during module installs (esp. `ipai_finance_ppm`)
- Align Odoo workers, cron workers, and PostgreSQL `max_connections`
- Provide a repeatable tuning baseline for dev/stage/prod

---

## 2. Target Topology

- Odoo:
  - HTTP workers: **4**
  - Cron workers: **2**
- PostgreSQL:
  - `max_connections`: **100**
  - Reserved for superuser/maintenance: **10**
  - Odoo pool target: **60–80** connections (normal operation << max)

---

## 3. Odoo Tuning (odoo.conf)

In `deploy/odoo.conf`:

```ini
[options]
workers = 4
max_cron_threads = 2
limit_memory_hard = 2684354560   ; 2.5 GB
limit_memory_soft = 2147483648   ; 2 GB
limit_request = 8192
limit_time_cpu = 120
limit_time_real = 240
db_maxconn = 64                  ; Odoo DB pool cap
```

Notes:

* `db_maxconn` < PostgreSQL `max_connections` to leave headroom.
* `limit_time_*` increased for heavy module installs (PPM, accounting).

---

## 4. PostgreSQL Tuning

If using `postgresql.conf` inside container (mapped via volume):

```conf
max_connections = 100
shared_buffers = 1GB
work_mem = 32MB
maintenance_work_mem = 256MB
effective_cache_size = 3GB
wal_buffers = 16MB
checkpoint_timeout = 15min
max_wal_size = 2GB
min_wal_size = 512MB
```

If using env vars (docker-compose):

```yaml
environment:
  - POSTGRES_MAX_CONNECTIONS=100
```

---

## 5. Module Installation Strategy

To avoid pool exhaustion:

1. **Single-module installs only** for heavy modules:

   * `ipai_finance_ppm`
   * future `ipai_*` finance / reporting modules.

2. Use the installer wrapper:

```bash
scripts/install_ipai_finance_ppm.sh -d odoo
```

3. Always run with **no concurrent UI installs** and **no parallel CI jobs** pointing to the same DB.

---

## 6. Rollback & Safety

* Always call `scripts/pre_install_snapshot.sh` before a major module install.
* Snapshot naming: `odoo_preinstall_<module>_<YYYYMMDDHHMM>.sql`
* Store snapshots on a separate disk or S3-compatible storage.

---

## 7. Monitoring

* Use `docker stats` to watch Odoo memory + CPU.
* Use `SELECT * FROM pg_stat_activity;` to diagnose stuck installs.
* Wire failures into n8n → Mattermost using CI telemetry + auto-heal hooks.
