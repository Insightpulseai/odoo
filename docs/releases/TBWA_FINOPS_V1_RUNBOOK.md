# TBWA Finance Ops Pilot – Go-Live Runbook v1

**Version:** 1.0.0
**Date:** 2026-01-12
**Stack:** Odoo CE 18.0 + ipai_finance_ppm + ipai_theme_tbwa + ipai_superset_connector

---

## 1. Access Information

| Item | Value |
|------|-------|
| **Odoo URL** | https://erp.insightpulseai.net/ |
| **Finance PPM App** | Finance Ops menu |
| **Superset Dashboard** | Embedded in Finance Ops workspace |
| **Support Email** | business@insightpulseai.com |
| **Issue Tracker** | GitHub: jgtolentino/odoo-ce/issues |

---

## 2. Pilot Scope

### What's Included

- `ipai_finance_ppm` module (month-end close, checklists, BIR deadlines)
- TBWA theme (branded navigation, trimmed menus)
- Embedded Superset dashboard (Finance close health view)
- Sample data: December/January close periods, pre-seeded tasks

### What's NOT Included

- Real accounting postings (sample data only)
- Settings / Apps / Technical menus
- Module installation capabilities
- Database administration

---

## 3. User Roles

| Group | Access Level | Capabilities |
|-------|--------------|--------------|
| **TBWA Finance Ops** | User | View month-end checklists, dashboards. Read-only. |
| **TBWA Finance Ops Lead** | Approver | Above + update task statuses, approve items |

---

## 4. Data Source

| Data Type | Source | Refresh |
|-----------|--------|---------|
| Month-end tasks | Sample seed data | Static (demo) |
| BIR deadlines | `finance_bir_2026_seed.xml` | Static |
| Dashboard metrics | Sample PostgreSQL | On-demand |

---

## 5. Operational Checklist

### Pre-Go-Live

- [ ] Verify HTTPS certificate valid
- [ ] Test login from incognito browser
- [ ] Confirm TBWA Finance Ops group sees correct menus
- [ ] Verify Superset embed loads without auth errors
- [ ] Confirm sample data is populated

### Go-Live

- [ ] Send invitation emails to pilot users
- [ ] Monitor error logs for 24h: `docker logs odoo-prod --tail 100`
- [ ] Verify no 500 errors in access logs

### Rollback Procedure

1. Stop Odoo: `docker stop odoo-prod`
2. Restore DB snapshot: `pg_restore -d odoo_core /backups/odoo_core_pre_pilot.dump`
3. Restart: `docker start odoo-prod`
4. Notify users of rollback

---

## 6. Issue Reporting

**For pilot users:**
- Email: business@insightpulseai.com
- GitHub: Create issue with label `pilot:tbwa-finops`

**Include:**
- Screenshot
- URL where error occurred
- Approximate time
- Steps to reproduce

---

## 7. Version Tag

```bash
git tag -a odoo-ce-finops-v1 -m "TBWA Finance Ops pilot v1"
git push origin odoo-ce-finops-v1
```

---

## 8. Health Checks

### Odoo
```bash
curl -s -o /dev/null -w "%{http_code}" https://erp.insightpulseai.net/web/login
# Expected: 200
```

### Database
```bash
docker exec postgres psql -U odoo -d odoo_core -c "SELECT 1;"
# Expected: returns 1
```

### Superset Embed
```bash
# Verify guest token endpoint responds
curl -s https://erp.insightpulseai.net/superset/guest_token
# Expected: 200 or 401 (auth required)
```

---

## 9. Contacts

| Role | Name | Contact |
|------|------|---------|
| Technical Lead | Jake Tolentino | business@insightpulseai.com |
| Product | InsightPulseAI | GitHub issues |

---

*Last updated: 2026-01-12*
