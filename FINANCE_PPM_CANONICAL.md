# Finance PPM Canonical State

**Status:** 🟢 LOCKED AND TAMED  
**Last Updated:** 2025-12-26  
**Git Tag:** finance-ppm-v1.1.1

## Executive Summary

The Finance PPM system is now fully deployed, documented, and locked down with the following guarantees:

✅ **Version Control**: Git tags provide rollback capability  
✅ **Data Integrity**: Health check validates canonical state  
✅ **Documentation**: Comprehensive README with workflows  
✅ **Legacy Isolation**: Old projects quarantined  
✅ **UI Access**: Menu structure deployed  
✅ **Seed Protection**: Warnings prevent manual drift

## Quick Commands

```bash
# Health check (production)
ssh root@159.223.75.148 "cd /root/odoo-prod && ./scripts/finance_ppm_health_check.sh odoo"

# Expected output: 8 / 12 / 144 / 36 / 36

# Rollback to v1.0.0 if needed
git checkout finance-ppm-v1.0.0
ssh root@159.223.75.148 "cd /root/odoo-prod && docker exec -e PGHOST=odoo-db-1 odoo-production odoo -d odoo -u ipai_finance_ppm,ipai_finance_ppm_umbrella --stop-after-init"
```

## Canonical State Matrix

| Component | Expected | Actual | Status |
|-----------|----------|--------|--------|
| Employees with codes | 8 | 8 | ✅ |
| Logframe entries | 12 | 12 | ✅ |
| BIR schedule records | 144 | 144 | ✅ |
| Closing tasks (project 30) | 36 | 36 | ✅ |
| Logframe-linked tasks | 36 | 36 | ✅ |
| Active projects | 1 (ID 30) | 1 | ✅ |
| Legacy projects | 0 active | 0 | ✅ |
| UI menus | 3 submenus | 3 | ✅ |

## Version History

### v1.1.1 (2025-12-26) - Solidification Release
- **Commit:** 24aa3191
- **Changes:**
  - Comprehensive README with regeneration workflows
  - Health check shell script wrapper
  - Health check SQL validation query
  - Canonical state documentation
- **Purpose:** Lock down system against future drift

### v1.1.0 (2025-12-26) - UI & Warnings Release
- **Commit:** 6627b22e
- **Changes:**
  - Finance PPM root menu (ID 753)
  - 3 submenus: Logframe, BIR Schedule, Closing Tasks
  - Canonical warning headers in XML seed files
  - Legacy projects quarantined (19, 28, 29)
- **Purpose:** Surface system in UI and document seed source

### v1.0.0 (2025-12-26) - Initial Canonical Release
- **Commit:** d50c71a2
- **Changes:**
  - Base module: ipai_finance_ppm (models, views, security)
  - Umbrella module: ipai_finance_ppm_umbrella (seed data)
  - 8 employees (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
  - 12 logframe entries
  - 144 BIR schedules (Q4 2025 + 2026)
  - 36 closing tasks linked to logframe
  - Project ID 30 as canonical
- **Purpose:** Establish baseline production deployment

## File Structure

```
odoo-ce/
├── FINANCE_PPM_CANONICAL.md          # This file
├── addons/
│   ├── ipai_finance_ppm/             # Base module (framework)
│   │   ├── models/                   # Core models
│   │   ├── views/                    # UI views
│   │   ├── security/                 # Access control
│   │   └── data/                     # Project seed
│   └── ipai_finance_ppm_umbrella/    # Umbrella module (seed)
│       ├── README.md                 # Complete documentation
│       ├── data/                     # Seed XML files
│       │   ├── 01_employees.xml      # 8 employees + codes
│       │   ├── 02_logframe_complete.xml  # 12 logframe entries
│       │   ├── 03_bir_schedule.xml   # 144 BIR records
│       │   └── 04_closing_tasks.xml  # 36 tasks + links
│       └── views/
│           └── finance_ppm_menu.xml  # UI navigation
├── scripts/
│   ├── finance_ppm_health_check.sh   # Health check runner
│   ├── finance_ppm_health_check.sql  # Validation query
│   └── generate_seed_from_excel.py   # Seed generator
└── config/finance/
    └── BIR_SCHEDULE_2026.xlsx        # Source of truth
```

## Workflows

### Health Check Workflow

```bash
# 1. From local machine
./scripts/finance_ppm_health_check.sh odoo

# 2. From remote server
ssh root@159.223.75.148
cd /root/odoo-prod
./scripts/finance_ppm_health_check.sh odoo

# 3. Expected output
8 / 12 / 144 / 36 / 36
```

### Regeneration Workflow

```bash
# 1. Update source Excel
open config/finance/BIR_SCHEDULE_2026.xlsx

# 2. Generate XML
python3 scripts/generate_seed_from_excel.py

# 3. Test on test DB
ssh root@159.223.75.148 "docker exec odoo-production odoo -d odoo_ppm_test -u ipai_finance_ppm,ipai_finance_ppm_umbrella --stop-after-init"
./scripts/finance_ppm_health_check.sh odoo_ppm_test

# 4. Deploy to production
ssh root@159.223.75.148 "docker exec odoo-production odoo -d odoo -u ipai_finance_ppm,ipai_finance_ppm_umbrella --stop-after-init"
./scripts/finance_ppm_health_check.sh odoo

# 5. Tag release
git add addons/ipai_finance_ppm_umbrella/data/*.xml
git commit -m "feat(finance-ppm): Update seed data"
git tag -a finance-ppm-v1.2.0 -m "Updated seed [date]"
git push origin main finance-ppm-v1.2.0
```

### Rollback Workflow

```bash
# 1. Checkout canonical tag
git checkout finance-ppm-v1.0.0

# 2. Rollback Odoo
ssh root@159.223.75.148 "docker exec odoo-production odoo -d odoo -u ipai_finance_ppm,ipai_finance_ppm_umbrella --stop-after-init"

# 3. Verify
./scripts/finance_ppm_health_check.sh odoo

# 4. Return to main
git checkout main
```

## References

- **Production Server:** 159.223.75.148
- **Production Database:** odoo (PostgreSQL on odoo-db-1)
- **Test Database:** odoo_ppm_test
- **Odoo Container:** odoo-production
- **DB Container:** odoo-db-1
- **Git Repository:** github.com/jgtolentino/odoo-ce

## Support Contacts

- **Module Developer:** InsightPulse AI
- **Co-Author:** Claude Sonnet 4.5
- **Finance SSC Manager:** Jake Tolentino

---

**The beast is tamed.** 🐉
