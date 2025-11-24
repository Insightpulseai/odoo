# Odoo CE 18.0 - Finance PPM Deployment Changelog

All notable changes to the Finance PPM system will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.0] - 2025-11-24 — Monitoring & BI Integration

### Added
- **Monitoring Schema** (`deploy/monitoring_schema.sql`)
  - `monitoring.service_health_checks` - Service uptime and latency tracking
  - `monitoring.backup_verifications` - Backup success/failure tracking
  - Optimized indexes for time-series queries

- **Superset-Ready Views** (`deploy/monitoring_views.sql`)
  - `monitoring.v_service_uptime_daily` - Daily uptime percentage calculations
  - `monitoring.v_backup_status_daily` - Daily backup success rates

- **n8n Integration Ready**
  - Extended healthcheck and backup scripts with n8n webhook support
  - JSON payload format optimized for n8n workflow ingestion
  - Prepared for n8n → Postgres → Superset monitoring pipeline

### Technical Details
- **Schema Design**: Time-series optimized with JSONB for raw payload storage
- **View Optimization**: Pre-aggregated daily metrics for Superset dashboards
- **Integration Path**: Scripts → n8n webhooks → Postgres → Superset visualizations
- **SLO Tracking**: Ready for uptime and backup success rate monitoring

### Files Created
```
deploy/monitoring_schema.sql
deploy/monitoring_views.sql
```

### Database Setup
```bash
# Apply monitoring schema
docker compose exec db psql -U odoo -d odoo_ce_prod -f /docker-entrypoint-initdb.d/monitoring_schema.sql

# Apply monitoring views
docker compose exec db psql -U odoo -d odoo_ce_prod -f /docker-entrypoint-initdb.d/monitoring_views.sql
```

### Superset Dashboard Recommendations
1. **Dataset**: `monitoring.v_service_uptime_daily`
   - Chart 1: Line chart – `uptime_pct` over `day`, series by `service_name`
   - Chart 2: Big Number with Trendline – `uptime_pct` (latest day) with history

2. **Dataset**: `monitoring.v_backup_status_daily`
   - Chart 1: Bar chart – `success_pct` by `day` (filter `source_db='odoo_ce_prod'`)
   - Chart 2: Big Number – last `success_pct` (shows if last backup passed)

3. **Dashboard**: `Odoo CE – Prod SLO`
   - Row 1: Uptime big number + trend
   - Row 2: Backup success big number + trend
   - Row 3: Table of last 20 health checks and last 10 backup runs

---

## [1.1.0] - 2025-11-24 — Production Readiness Bundle

### Added
- **Database & Worker Tuning** (`docs/DB_TUNING.md`)
  - PostgreSQL connection limit: 100
  - Odoo worker configuration: 4 HTTP workers, 2 cron workers
  - Connection pool alignment to prevent exhaustion

- **Installation Safety**
  - `scripts/pre_install_snapshot.sh` - Pre-install database backups
  - `scripts/install_ipai_finance_ppm.sh` - Safe module installation wrapper

- **Configuration Updates**
  - `deploy/odoo.conf` - Added worker tuning parameters
  - `docker-compose.prod.yml` - Added PostgreSQL connection limits

- **Documentation & Procedures**
  - `docs/N8N_CREDENTIALS_BOOTSTRAP.md` - n8n credential management
  - `docs/MATTERMOST_ALERTING_SETUP.md` - Alert routing and payload conventions
  - `docs/APP_ICONS_README.md` - Branding and icon standardization

- **Regression Test Scaffolding**
  - Complete test suite for `ipai_equipment`, `ipai_expense`, and `ipai_finance_ppm`
  - Tagged for post-install regression testing

### Technical Details
- **Module Installation Safety**: Pre-install snapshots prevent data loss
- **Connection Pool Management**: Prevents database exhaustion during heavy operations
- **Alerting Infrastructure**: Complete Mattermost integration ready
- **Branding Consistency**: App icon standardization guidelines
- **Test Coverage**: Regression test foundation for core modules

### Files Created
```
docs/DB_TUNING.md
scripts/pre_install_snapshot.sh (executable)
scripts/install_ipai_finance_ppm.sh (executable)
docs/N8N_CREDENTIALS_BOOTSTRAP.md
docs/MATTERMOST_ALERTING_SETUP.md
docs/APP_ICONS_README.md
tests/regression/
├── __init__.py
├── test_ipai_equipment_flow.py
├── test_ipai_expense_flow.py
└── test_finance_ppm_install.py
```

### Next Actions
1. Review and merge branch: `chore/finalize-prod-readiness-v1`
2. Deploy changes and restart containers to apply new configuration
3. Test installation using new wrapper script to safely install `ipai_finance_ppm`

---

## [1.1.0] - 2025-11-24 — Hardening Pack

### Added
- **Load Testing Infrastructure**
  - `tests/load/odoo_login_and_nav.js` - k6-based load tests simulating realistic Odoo usage
  - Simulates login + core menu navigation under 50 concurrent users

- **Automated Backup Verification**
  - `scripts/verify_backup.sh` - Daily backup verification with Mattermost notifications
  - Creates fresh backup, restores to verification DB, runs sanity checks
  - Includes n8n webhook integration for metrics collection

- **Synthetic Monitoring**
  - `scripts/healthcheck_odoo.sh` - 5-minute cron heartbeat with failure alerts
  - Measures HTTP response codes and latency
  - Includes n8n webhook integration for metrics collection

### Technical Details
- **Load Testing**: k6 with Docker for consistent execution environment
- **Backup Verification**: Automated daily verification with rollback capability
- **Health Monitoring**: Continuous uptime monitoring with chat-level heartbeat
- **Integration Ready**: Prepared for n8n + Superset monitoring dashboards

### Files Created
```
tests/load/odoo_login_and_nav.js
scripts/verify_backup.sh (executable)
scripts/healthcheck_odoo.sh (executable)
```

### Usage Examples
```bash
# Load testing
docker run --rm -i loadimpact/k6 run - \
  -e ODOO_BASE_URL="https://erp.insightpulseai.net" \
  -e ODOO_LOGIN="admin" \
  -e ODOO_PASSWORD="your_admin_password" \
  < tests/load/odoo_login_and_nav.js

# Backup verification
./scripts/verify_backup.sh

# Health monitoring
./scripts/healthcheck_odoo.sh
```

### Cron Configuration
```cron
# Health check every 5 minutes
*/5 * * * * ODOO_URL="https://erp.insightpulseai.net/web/login" MM_WEBHOOK_URL="..." SERVICE_NAME="odoo-ce-prod" /opt/odoo-ce/scripts/healthcheck_odoo.sh >> /var/log/odoo_healthcheck.log 2>&1

# Backup verification daily at 3 AM
0 3 * * * cd /opt/odoo-ce && DB_CONTAINER=db DB_USER=odoo SOURCE_DB=odoo_ce_prod BACKUP_DIR=/var/backups/odoo ./scripts/verify_backup.sh >> /var/log/odoo_backup_verify.log 2>&1
```

---

## [1.0.1] - 2025-11-24 — Equipment Cron Compatibility

### Fixed
- **Odoo 18 cron install error** (`addons/ipai_equipment/data/ipai_equipment_cron.xml`)
  - Replaced deprecated `numbercall` with `max_calls` to avoid `Invalid field 'numbercall' on model 'ir.cron'` during installation
  - Added inline note to prevent regressions on future cron definitions

### Changed
- **Module version bump** (`addons/ipai_equipment/__manifest__.py`)
  - Incremented to `18.0.1.0.1` to deliver the cron compatibility fix

---

## [1.0.3] - 2025-11-24 — Equipment Cron max_calls Hardening

### Fixed
- **Cron compatibility alignment** (`addons/ipai_equipment/data/ipai_equipment_cron.xml`)
  - Explicitly set `max_calls` to `0` (unlimited) to replace deprecated `numbercall`
  - Retains explicit cron owner to avoid missing user errors on installs

### Changed
- **Module version bump** (`addons/ipai_equipment/__manifest__.py`)
  - Incremented to `18.0.1.0.3` to ship the cron compatibility hardening

---

## [1.0.2] - 2025-11-24 — Equipment Cron Owner & Compatibility Cleanup

### Fixed
- **Cron compatibility alignment** (`addons/ipai_equipment/data/ipai_equipment_cron.xml`)
  - Removed obsolete `numbercall`/`max_calls` override to rely on Odoo 18 defaults
  - Explicitly set `user_id` to `base.user_root` to avoid missing owner issues on installs

### Changed
- **Module version bump** (`addons/ipai_equipment/__manifest__.py`)
  - Incremented to `18.0.1.0.2` to ship the cron XML cleanup

---

## [1.0.0] - 2025-11-23 — Equipment MVP + CI/CD Automation

### Fixed
- **Odoo 18 Compatibility Issue** - ipai_equipment module installation
  - Removed deprecated `numbercall` field from ir.cron model
  - File: `addons/ipai_equipment/data/ipai_equipment_cron.xml:13`
  - Error: `ValueError: Invalid field 'numbercall' on model 'ir.cron'`
  - Resolution: Odoo 18 crons run indefinitely by default (field removed)

### Added
- **CI/CD Automation Infrastructure**
  - `odoo-bin` shim: Portable wrapper for GitHub Actions (fixes path issues)
  - `scripts/run_odoo_migrations.sh`: Auto-detect ipai_*/tbwa_* modules
  - `scripts/report_ci_telemetry.sh`: n8n webhook integration for CI health

- **Equipment MVP Module** (Ready for Installation)
  - Module: `ipai_equipment` (Cheqroom parity)
  - Features: Equipment Catalog, Bookings, Incidents tracking
  - Cron: Daily overdue booking checks
  - Status: ⏳ Requires manual UI installation (dependency: maintenance module)

### Documentation
- Added `DEPLOYMENT_MVP.md`: Complete installation guide with troubleshooting
- Installation method: Odoo Apps menu (manual step required)
- Acceptance gates: Module state, UI access, cron registration, zero errors

### Technical Details
- **Odoo 18 Breaking Change**: ir.cron.numbercall field removed
- **Migration Path**: Remove field from all cron XML definitions
- **Reference**: https://www.odoo.com/documentation/18.0/developer/reference/upgrades.html

### Files Modified
```
M  addons/ipai_equipment/data/ipai_equipment_cron.xml
A  odoo-bin (executable)
A  scripts/run_odoo_migrations.sh (executable)
A  scripts/report_ci_telemetry.sh (executable)
A  DEPLOYMENT_MVP.md
```

### Next Actions
1. Install via Odoo UI: Apps > Update Apps List > Search "ipai_equipment" > Install
2. Verify: Equipment menu visible with 3 submenus (Catalog, Bookings, Incidents)
3. Test: Create test equipment record and verify cron job registered

---

## [1.1.0] - 2025-11-23 — Finance PPM Automation Go-Live

### Added
- **Finance PPM Automation Framework** - Full n8n workflow orchestration
  - BIR Deadline Alert workflow (daily 8 AM monitoring)
  - Task Escalation workflow (twice daily supervisor alerts)
  - Monthly Compliance Report workflow (1st of month summary)

- **Supabase Database Infrastructure**
  - Schema: `finance_ppm`
  - Table: `monthly_reports` (20 columns, 6 indexes, 2 RLS policies)
  - Migration: `003_finance_ppm_reports.sql` applied successfully

- **SuperClaude Agent Integration**
  - Agent: `odoo_frontend_ux_n8n` registered
  - Auto-activation: Odoo UI, n8n workflows, view debugging
  - Documentation: CLAUDE.md Section 13.1

### Changed
- Updated Finance PPM module to support n8n integration
  - Added `finance_logframe_seed.xml` (Logical Framework seed data)
  - Added `finance_bir_schedule_seed.xml` (BIR schedule entries)
  - Enhanced views for workflow compatibility

### Technical Details
- **Odoo Instance**: https://erp.insightpulseai.net/ (verified accessible)
- **n8n Instance**: https://n8n.insightpulseai.net/ (verified accessible)
- **Supabase Project**: ublqmilcjtpnflofprkr (verified connected)
- **Database**: PostgreSQL 15 via connection pooler (port 6543)

### Files Created
```
workflows/finance_ppm/
├── bir_deadline_alert.json (11.3 KB, 9 nodes)
├── task_escalation.json (13.4 KB, 10 nodes)
├── monthly_report.json (15.5 KB, 11 nodes)
├── DEPLOYMENT.md (comprehensive deployment guide)
├── DEPLOYMENT_SUMMARY.md (executive summary)
└── verify_deployment.sh (automated verification)

migrations/
└── 003_finance_ppm_reports.sql (✅ applied)

.claude/superclaude/agents/domain/
└── odoo_frontend_ux_n8n.agent.yaml (257 lines)
```

### Verification Status
- ✅ Passed: 13 checks
- ⚠️ Warnings: 3 (Mattermost optional, n8n API manual import, Odoo module credentials)
- ❌ Failed: 0

### Pending Actions
- [ ] Import workflows to n8n via UI (`https://n8n.insightpulseai.net/workflows`)
- [ ] Configure n8n credentials (Odoo, Mattermost, Supabase)
- [ ] Test each workflow manually
- [ ] Activate workflow schedules
- [ ] Verify first BIR deadline alert (next day 8 AM)

### System Status
| Component | Status |
|-----------|--------|
| Odoo Module | ✅ Deployed v1.0.0 |
| Supabase Table | ✅ Live |
| n8n Workflows | 🔧 Ready for import |
| Agent Integration | ✅ Registered |
| CI Compliance | ✅ Passed |

---

## [1.0.0] - 2025-11-22 — Initial Finance PPM Module Deployment

### Added
- **Odoo Module**: `ipai_finance_ppm` v1.0.0
  - Logical Framework model (`ipai.finance.logframe`)
  - BIR Schedule model (`ipai.finance.bir_schedule`)
  - Project Task extension (Finance PPM integration)
  - List/Form views with Odoo 18 compatibility
  - Security access rules (ir.model.access.csv)
  - Cron job: Daily 8 AM BIR task sync

### Fixed
- Odoo 18 compatibility issues
  - Replaced `<tree>` tags with `<list>` in all views
  - Updated `view_mode` from `tree,form` to `list,form`
  - Removed deprecated `allow_timesheets` field

### Technical Details
- **Installation Time**: 0.69s (272 queries)
- **Database**: production
- **Registry**: 193 modules loaded
- **Container**: odoo-odoo-1 (restarted successfully)

### Files Created
```
addons/ipai_finance_ppm/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── finance_logframe.py
│   ├── finance_bir_schedule.py
│   └── project_task.py
├── views/
│   ├── finance_ppm_views.xml
│   └── ppm_dashboard_template.xml
├── data/
│   ├── finance_logframe_seed.xml
│   ├── finance_bir_schedule_seed.xml
│   └── finance_cron.xml
├── security/
│   └── ir.model.access.csv
└── static/
    └── description/
        └── icon.png
```

### Verification
- ✅ Module loaded successfully
- ✅ All views validated (no XML errors)
- ✅ Seed data imported (8 BIR forms, 1 logframe entry)
- ✅ Cron job configured (daily 8 AM)
- ✅ Access rules applied

### Access
- **URL**: https://erp.insightpulseai.net/
- **Menu**: Finance PPM (main navigation)
- **Submenus**:
  - Logical Framework (list/form views)
  - BIR Schedule (deadline tracking)
  - PPM Dashboard (ECharts visualizations)
- **HTTP Route**: `/ipai/finance/ppm`

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.1.0 | 2025-11-23 | Finance PPM Automation (n8n workflows) |
| 1.0.0 | 2025-11-22 | Initial Finance PPM Module Deployment |

---

## Support & Documentation

### Deployment Guides
- **Finance PPM Module**: `/Users/tbwa/odoo-ce/verify_finance_ppm.py`
- **n8n Workflows**: `/Users/tbwa/odoo-ce/workflows/finance_ppm/DEPLOYMENT.md`
- **Verification**: `/Users/tbwa/odoo-ce/workflows/finance_ppm/verify_deployment.sh`

### Issues & Troubleshooting
- Odoo Logs: `ssh root@erp.insightpulseai.net "docker logs odoo-odoo-1 --tail 100"`
- n8n Logs: Check execution history at `https://n8n.insightpulseai.net/executions`
- Supabase: `psql "$POSTGRES_URL" -c "SELECT * FROM finance_ppm.monthly_reports ORDER BY generated_at DESC LIMIT 5;"`

### Contacts
- **Finance SSC Manager**: Jake Tolentino
- **Technical Lead**: Jake Tolentino
- **Agencies**: RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB
