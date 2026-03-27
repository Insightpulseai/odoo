# Incident Response and Rollback Runbook

**Blocker**: B-4
**Status**: CLOSED -- runbooks written

---

## 1. Incident Severity Model

| Severity | Name | Definition | Response Time | Resolution Target |
|----------|------|------------|---------------|-------------------|
| **P0** | Critical | Total platform outage. No users can access Odoo ERP. Data loss risk. | 15 min acknowledge | 1 hour mitigate |
| **P1** | High | Major feature unavailable (e.g., invoicing, payroll). Workaround exists but impacts operations. | 30 min acknowledge | 4 hours mitigate |
| **P2** | Medium | Non-critical feature degraded. Cosmetic issues. Performance degradation below SLA. | 2 hours acknowledge | 1 business day |
| **P3** | Low | Minor issues, documentation gaps, non-urgent improvements. | 1 business day | Next sprint |

### Severity Determination

- **P0 triggers**: Odoo web unreachable, database corruption, identity provider total failure, data breach confirmed
- **P1 triggers**: Single critical module broken, email delivery failure, backup failure, partial identity outage
- **P2 triggers**: Slow queries, UI rendering issues, non-critical module error, monitoring gap
- **P3 triggers**: Feature request, documentation update, minor UX improvement

---

## 2. Escalation Chain

| Role | Contact Method | P0 | P1 | P2 | P3 |
|------|---------------|----|----|----|----|
| **Platform On-Call** | Slack #platform-incidents | Immediate | Immediate | Next check-in | Backlog |
| **Platform Owner** | Slack DM + phone | 15 min | 30 min | -- | -- |
| **CTO** | Phone | 30 min | 2 hours | -- | -- |
| **CEO** | Phone (P0 only) | 1 hour | -- | -- | -- |
| **Azure Support** | Azure Portal (Sev A/B/C) | Sev A (15 min) | Sev B (2 hours) | Sev C | -- |

### Incident Commander

- P0/P1: Platform Owner assumes Incident Commander role
- P2/P3: Platform On-Call handles directly

---

## 3. Rollback Procedures

### 3.1 Identity Rollback (Entra to Local Odoo Auth)

**When**: Entra OIDC is down, misconfigured, or causing authentication failures.

**Immediate (< 5 minutes)**:

1. Deactivate the Microsoft Entra OAuth provider in Odoo:
   - If Odoo admin is accessible: Settings > OAuth Providers > deactivate Microsoft Entra
   - If Odoo admin is locked out: use break-glass account (see `docs/runbooks/break-glass-accounts.md`)

2. If admin access is completely lost, connect to database directly:
   ```bash
   # Connect to pg-ipai-odoo via Azure Portal or psql
   psql -h pg-ipai-odoo.postgres.database.azure.com -U <admin> -d odoo

   # Disable OAuth provider
   UPDATE auth_oauth_provider SET enabled = false WHERE name ILIKE '%entra%';

   # Reset admin password if needed
   UPDATE res_users SET password = '' WHERE login = 'admin';
   ```

3. Restart the Odoo container to clear cached sessions:
   ```bash
   az containerapp revision restart --name ipai-odoo-dev-web \
     --resource-group rg-ipai-dev-odoo-runtime \
     --revision $(az containerapp revision list --name ipai-odoo-dev-web \
       --resource-group rg-ipai-dev-odoo-runtime \
       --query "[?properties.active].name" -o tsv)
   ```

4. Verify local login works at `https://erp.insightpulseai.com/web/login`

**Recovery**: Re-enable Entra OAuth only after root cause is identified and fixed.

### 3.2 Data Rollback (Database Backup/Restore)

**When**: Data corruption, bad migration, accidental mass deletion.

**Prerequisites**: Automated backups running via Azure Database for PostgreSQL point-in-time restore.

#### Option A: Point-in-Time Restore (Preferred)

```bash
# Restore to a point in time (up to 35 days back)
az postgres flexible-server restore \
  --resource-group rg-ipai-dev-odoo-data \
  --name pg-ipai-odoo-restored \
  --source-server pg-ipai-odoo \
  --restore-time "2026-03-27T10:00:00Z"

# Verify restored data
psql -h pg-ipai-odoo-restored.postgres.database.azure.com -U <admin> -d odoo \
  -c "SELECT count(*) FROM res_users;"

# If verified, swap connection strings in ACA
az containerapp update --name ipai-odoo-dev-web \
  --resource-group rg-ipai-dev-odoo-runtime \
  --set-env-vars DB_HOST=pg-ipai-odoo-restored.postgres.database.azure.com
```

#### Option B: Backup File Restore

```bash
# List available backups
az postgres flexible-server backup list \
  --resource-group rg-ipai-dev-odoo-data \
  --name pg-ipai-odoo

# Restore from specific backup
az postgres flexible-server restore \
  --resource-group rg-ipai-dev-odoo-data \
  --name pg-ipai-odoo-restored \
  --source-server pg-ipai-odoo \
  --restore-time "<backup-timestamp>"
```

#### Option C: Manual pg_dump Restore (Last Resort)

```bash
# Restore from a pg_dump file
psql -h pg-ipai-odoo.postgres.database.azure.com -U <admin> -d odoo < backup.sql
```

**Post-restore checklist**:
- [ ] Verify user count matches expected
- [ ] Verify recent transactions exist
- [ ] Verify module list is correct (`ir_module_module`)
- [ ] Run Odoo health check: `curl -s https://erp.insightpulseai.com/web/health`

### 3.3 Deployment Rollback (ACA Revision)

**When**: Bad code deployment, container crash loop, configuration error.

#### Immediate: Activate Previous Revision

```bash
# List all revisions
az containerapp revision list \
  --name ipai-odoo-dev-web \
  --resource-group rg-ipai-dev-odoo-runtime \
  --output table

# Activate previous known-good revision (route 100% traffic to it)
az containerapp ingress traffic set \
  --name ipai-odoo-dev-web \
  --resource-group rg-ipai-dev-odoo-runtime \
  --revision-weight <previous-revision-name>=100

# Deactivate the bad revision
az containerapp revision deactivate \
  --name ipai-odoo-dev-web \
  --resource-group rg-ipai-dev-odoo-runtime \
  --revision <bad-revision-name>
```

#### Container Image Rollback

```bash
# Deploy previous known-good image
az containerapp update --name ipai-odoo-dev-web \
  --resource-group rg-ipai-dev-odoo-runtime \
  --image acripaiodoo.azurecr.io/ipai-odoo:previous-tag
```

#### Full Stack Rollback

If multiple containers are affected (web + worker + cron):

```bash
for app in ipai-odoo-dev-web ipai-odoo-dev-worker ipai-odoo-dev-cron; do
  az containerapp update --name $app \
    --resource-group rg-ipai-dev-odoo-runtime \
    --image acripaiodoo.azurecr.io/ipai-odoo:previous-tag
done
```

**Post-rollback verification**:
```bash
# Health check
curl -s -o /dev/null -w "%{http_code}" https://erp.insightpulseai.com/web/health
# Expected: 200

# Check logs for errors
az containerapp logs show --name ipai-odoo-dev-web \
  --resource-group rg-ipai-dev-odoo-runtime \
  --tail 50
```

---

## 4. Communication Templates

### P0 -- Initial Notification

```
INCIDENT: [Brief description]
SEVERITY: P0 -- Critical
TIME: [ISO 8601 timestamp]
IMPACT: [What users/services are affected]
STATUS: Investigating
INCIDENT COMMANDER: [Name]
NEXT UPDATE: [Time, within 30 min]
```

### P0 -- Status Update

```
INCIDENT UPDATE: [Brief description]
SEVERITY: P0
TIME: [ISO 8601 timestamp]
STATUS: [Investigating / Identified / Mitigating / Resolved]
ROOT CAUSE: [If known, else "Under investigation"]
MITIGATION: [What has been done]
NEXT UPDATE: [Time]
```

### P0 -- Resolution

```
INCIDENT RESOLVED: [Brief description]
SEVERITY: P0
DURATION: [Start to resolution time]
ROOT CAUSE: [Summary]
RESOLUTION: [What fixed it]
FOLLOW-UP: Post-incident review scheduled for [date]
```

---

## 5. Post-Incident Review Process

**Required for**: All P0 and P1 incidents. Optional for P2.

**Timeline**: Review meeting within 3 business days of resolution.

### Review Template

```markdown
# Post-Incident Review: [Incident Title]

**Date**: [YYYY-MM-DD]
**Severity**: [P0/P1/P2]
**Duration**: [Total time from detection to resolution]
**Incident Commander**: [Name]

## Timeline
- HH:MM -- [Event]
- HH:MM -- [Event]

## Root Cause
[Technical root cause analysis]

## Impact
- Users affected: [count/scope]
- Data loss: [yes/no, details]
- Revenue impact: [if applicable]

## What Went Well
- [Item]

## What Needs Improvement
- [Item]

## Action Items
| # | Action | Owner | Due Date | Status |
|---|--------|-------|----------|--------|
| 1 | [Action] | [Name] | [Date] | Open |
```

### Storage

Post-incident reviews are stored at:
```
docs/evidence/<YYYYMMDD-HHMM>/incident-review/
```

---

## 6. Stop Conditions

Halt any deployment or migration if:

1. Health check returns non-200 after deployment
2. Error rate exceeds 5% in the first 10 minutes post-deploy
3. Any P0 incident is active and unresolved
4. Database backup verification fails
5. Identity provider is unreachable during an identity-related change

---

*Last updated: 2026-03-27*
