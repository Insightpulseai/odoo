---
title: "Platform Operations Guide"
kb_scope: "ops-kb"
group_ids: ["group-guid-placeholder"]
last_updated: "2026-03-15"
---

# Platform Operations Guide

## Overview

This document defines the operational procedures for the InsightPulse AI platform running on Azure Container Apps. It covers service health monitoring, incident response, routine maintenance, and troubleshooting procedures.

---

## Platform Architecture

### Service Inventory

| Service | Container App | Port | Health Endpoint | SLA Target |
|---------|--------------|:----:|-----------------|:----------:|
| Odoo ERP | ipai-odoo-dev-web | 8069 | `/web/login` (HTTP 200) | 99.9% |
| Keycloak SSO | ipai-auth-dev | 8080 | `/health/ready` | 99.9% |
| MCP Coordinator | ipai-mcp-dev | 3000 | `/health` | 99.5% |
| OCR Service | ipai-ocr-dev | 8000 | `/health` | 99.0% |
| Apache Superset | ipai-superset-dev | 8088 | `/health` | 99.0% |
| n8n Automation | n8n instance | 5678 | `/healthz` | 99.0% |

### Infrastructure Components

| Component | Service | Purpose |
|-----------|---------|---------|
| Azure Front Door | ipai-fd-dev | Edge routing, TLS, WAF |
| Azure Container App Env | cae-ipai-dev | Container orchestration |
| Azure Database for PostgreSQL | Flex server | Odoo and service databases |
| Azure Key Vault | kv-ipai-dev | Secret management |
| Azure Blob Storage | Blob account | File attachments, backups |
| Azure Monitor | Log Analytics | Centralized logging |

### Network Topology

```
Internet
    |
    v
Cloudflare DNS (insightpulseai.com)
    |
    v
Azure Front Door (TLS termination, WAF, routing)
    |
    +---> erp.insightpulseai.com --> ipai-odoo-dev-web:8069
    +---> auth.insightpulseai.com --> ipai-auth-dev:8080
    +---> mcp.insightpulseai.com --> ipai-mcp-dev:3000
    +---> ocr.insightpulseai.com --> ipai-ocr-dev:8000
    +---> superset.insightpulseai.com --> ipai-superset-dev:8088
    |
    v
Azure Container App Environment (cae-ipai-dev, southeastasia)
    |
    v
Azure PostgreSQL (private endpoint)
    |
    v
Azure Key Vault (managed identity)
```

---

## Health Monitoring

### Automated Health Checks

Health checks run every 60 seconds via Azure Container Apps liveness and readiness probes:

| Service | Liveness Probe | Readiness Probe | Timeout |
|---------|---------------|----------------|:-------:|
| Odoo | `GET /web/login` | `GET /web/login` | 10s |
| Keycloak | `GET /health/live` | `GET /health/ready` | 5s |
| MCP | `GET /health` | `GET /health` | 5s |
| OCR | `GET /health` | `GET /health` | 5s |
| Superset | `GET /health` | `GET /health` | 10s |

### Manual Health Check Procedure

Run these checks to verify platform health:

1. **Odoo Web Interface**
   - Verify `https://erp.insightpulseai.com` loads the login page
   - Expected: HTTP 200 with Odoo login form
   - Verify database connectivity by attempting login

2. **Keycloak SSO**
   - Verify `https://auth.insightpulseai.com/health/ready`
   - Expected: HTTP 200 with `{"status": "UP"}`

3. **Superset BI**
   - Verify `https://superset.insightpulseai.com/health`
   - Expected: HTTP 200 with "OK"

4. **Azure Front Door**
   - Verify all endpoints resolve correctly via Front Door
   - Check for WAF blocks in Azure Monitor logs

5. **Database**
   - Check PostgreSQL connectivity and replication status
   - Verify connection pool usage is below 80%

6. **Certificate Status**
   - Verify TLS certificates are valid and not expiring within 30 days
   - Azure Front Door manages certificates automatically, but verify via:
     ```
     az network front-door frontend-endpoint show
     ```

### Monitoring Alerts

| Alert | Condition | Severity | Notification |
|-------|-----------|:--------:|:------------:|
| Service Down | Health check fails 3 consecutive times | Critical | Slack #ops-alerts + PagerDuty |
| High Error Rate | 5xx errors > 5% of requests in 5 minutes | High | Slack #ops-alerts |
| High Latency | P95 response time > 5 seconds for 10 minutes | Medium | Slack #ops-alerts |
| Database CPU | PostgreSQL CPU > 80% for 15 minutes | High | Slack #ops-alerts |
| Database Storage | Storage usage > 85% | Medium | Slack #ops-alerts + email |
| Container Restart | Container restart count > 3 in 1 hour | High | Slack #ops-alerts |
| Certificate Expiry | TLS certificate expires in < 14 days | Medium | Email to ops team |
| WAF Block Rate | WAF blocks > 100/minute | Low | Slack #security-alerts |

---

## Incident Response

### Severity Levels

| Level | Definition | Response Time | Resolution Target |
|:------|:----------|:-------------|:-----------------|
| SEV-1 | Platform completely down, all users affected | 15 minutes | 1 hour |
| SEV-2 | Major feature unavailable (e.g., invoicing, login) | 30 minutes | 4 hours |
| SEV-3 | Minor feature degraded, workaround available | 2 hours | 24 hours |
| SEV-4 | Cosmetic issue, no business impact | Next business day | 5 business days |

### Incident Response Procedure

#### 1. Detection and Triage (0-15 minutes)

1. Alert received via monitoring system or user report
2. Acknowledge the alert in Slack
3. Assess severity using the level definitions above
4. Create an incident channel: `#incident-YYYYMMDD-brief-description`
5. Post initial assessment:
   - Affected service(s)
   - User impact
   - Severity level
   - Current status

#### 2. Investigation (15 minutes - 1 hour)

1. Check service health endpoints
2. Review Azure Monitor logs:
   - Container App logs for errors
   - Front Door access logs for traffic patterns
   - PostgreSQL logs for database issues
3. Check recent deployments (could a deployment have caused this?)
4. Check external dependencies (Cloudflare status, Azure status)
5. Document findings in the incident channel

#### 3. Mitigation (Concurrent with Investigation)

Common mitigation actions:

| Symptom | Immediate Action |
|---------|-----------------|
| Container crash loop | Roll back to previous revision |
| Database connection exhaustion | Restart the container app to reset connections |
| Memory pressure | Scale up the container (increase memory limit) |
| Traffic spike (DDoS) | Enable Azure Front Door rate limiting rules |
| Certificate error | Verify Front Door certificate binding |
| DNS resolution failure | Check Cloudflare DNS records |

#### 4. Resolution

1. Apply the fix (code change, configuration update, infrastructure change)
2. Verify the fix resolves the issue
3. Monitor for 30 minutes to confirm stability
4. Update the incident channel with resolution details
5. Close the alert in the monitoring system

#### 5. Post-Incident Review (Within 48 hours)

1. Create a post-incident report:
   - Timeline of events
   - Root cause analysis
   - Impact assessment (duration, users affected, revenue impact)
   - What went well
   - What could be improved
   - Action items with owners and deadlines
2. Share the report in #ops-team
3. Track action items to completion

---

## Routine Maintenance

### Daily Tasks

| Task | Time | Owner |
|------|------|-------|
| Review overnight alerts | 8:00 AM | On-call engineer |
| Check Odoo cron job status | 8:30 AM | Platform team |
| Review error log summary | 9:00 AM | Platform team |
| Verify backup completion | 9:00 AM | Platform team |

### Weekly Tasks

| Task | Day | Owner |
|------|-----|-------|
| Review container resource usage (CPU, memory) | Monday | Platform team |
| Check database vacuum and analyze status | Monday | DBA |
| Review Azure cost report | Tuesday | Finance / Ops |
| Test backup restore (sample table) | Wednesday | Platform team |
| Review security scan results | Thursday | Security |
| Update status page with any maintenance notes | Friday | Platform team |

### Monthly Tasks

| Task | Owner |
|------|-------|
| Review and rotate service account credentials | Security |
| Update OCA module pins after regression testing | Dev team |
| Review and optimize slow database queries | DBA |
| Test disaster recovery procedure | Platform team |
| Review Azure Advisor recommendations | Platform team |
| Update documentation for any infrastructure changes | Platform team |
| Review container image vulnerabilities (Trivy scan) | Security |

### Quarterly Tasks

| Task | Owner |
|------|-------|
| Full disaster recovery drill | Platform team + management |
| Security audit (penetration test or vulnerability assessment) | Security |
| Capacity planning review | Platform team |
| SLA compliance report | Platform team |
| Cost optimization review | Finance / Platform team |

---

## Backup and Recovery

### Backup Schedule

| Component | Method | Frequency | Retention |
|-----------|--------|-----------|-----------|
| PostgreSQL (Odoo) | Azure automated backup | Continuous (PITR) | 35 days |
| PostgreSQL (manual) | pg_dump to Blob Storage | Daily at 2:00 AM | 90 days |
| File attachments | Azure Blob Storage replication | Continuous (GRS) | N/A |
| Container configuration | Git (infrastructure as code) | On change | Indefinite |
| Key Vault secrets | Azure backup | Daily | 90 days |
| n8n workflows | API export to Blob Storage | Daily at 3:00 AM | 90 days |

### Recovery Procedures

#### Database Recovery (Point-in-Time)

1. Identify the target recovery point (timestamp before the issue)
2. Create a new PostgreSQL server from the PITR backup:
   ```
   az postgres flexible-server restore --source-server <source> --restore-time <timestamp>
   ```
3. Verify the recovered database
4. Update the Container App to point to the recovered server
5. Verify application functionality

#### Container Rollback

1. List container app revisions:
   ```
   az containerapp revision list --name <app> --resource-group rg-ipai-dev
   ```
2. Activate the previous working revision:
   ```
   az containerapp revision activate --name <app> --revision <revision-name>
   ```
3. Route traffic to the restored revision
4. Verify functionality

#### Full Platform Recovery (Disaster Recovery)

Recovery Time Objective (RTO): 4 hours
Recovery Point Objective (RPO): 1 hour

1. Deploy infrastructure from IaC templates (Bicep/Terraform)
2. Restore PostgreSQL from latest backup
3. Deploy container images from Azure Container Registry
4. Restore Key Vault secrets
5. Update DNS records if region changed
6. Verify all services
7. Notify users of restoration

---

## Scaling Procedures

### Horizontal Scaling

Azure Container Apps supports automatic horizontal scaling:

| Service | Min Replicas | Max Replicas | Scale Trigger |
|---------|:-----------:|:-----------:|---------------|
| Odoo | 1 | 3 | HTTP concurrent requests > 50 |
| Keycloak | 1 | 2 | HTTP concurrent requests > 30 |
| MCP | 1 | 3 | HTTP concurrent requests > 100 |
| OCR | 0 | 2 | Queue depth > 5 |
| Superset | 1 | 2 | CPU > 70% |

### Vertical Scaling

If horizontal scaling is insufficient, increase container resources:

| Service | Default CPU | Default Memory | Max CPU | Max Memory |
|---------|:----------:|:--------------:|:-------:|:----------:|
| Odoo | 1.0 | 2Gi | 2.0 | 4Gi |
| Keycloak | 0.5 | 1Gi | 1.0 | 2Gi |
| MCP | 0.5 | 1Gi | 1.0 | 2Gi |
| OCR | 0.5 | 1Gi | 2.0 | 4Gi |
| Superset | 1.0 | 2Gi | 2.0 | 4Gi |

### Database Scaling

PostgreSQL scaling options:

1. **Vertical**: Increase compute tier (Burstable > General Purpose > Memory Optimized)
2. **Read Replicas**: Add read replicas for reporting workloads (Superset)
3. **Connection Pooling**: Enable PgBouncer for connection management
4. **Storage**: Increase storage allocation (auto-grow enabled, max 16 TB)

---

## Troubleshooting Guide

### Common Issues

#### Odoo 502 Bad Gateway

**Symptoms**: Users see "502 Bad Gateway" error
**Causes**:
- Odoo container crashed or is restarting
- Database connection timeout
- Front Door backend health probe failing

**Resolution**:
1. Check container status: `az containerapp revision list`
2. Check container logs for errors
3. If container is in crash loop, check for database connectivity
4. If database is reachable, check Odoo logs for Python tracebacks
5. Last resort: restart the container app

#### Slow Performance

**Symptoms**: Pages take >5 seconds to load
**Causes**:
- Database query performance degradation
- Container resource exhaustion (CPU/memory)
- Network latency between container and database

**Resolution**:
1. Check container CPU and memory usage in Azure Monitor
2. Check PostgreSQL slow query log
3. Run `ANALYZE` on frequently queried tables
4. Check if Odoo cron jobs are running during business hours (reschedule to off-peak)
5. Verify no long-running transactions are holding locks

#### Login Failures

**Symptoms**: Users cannot log in to Odoo
**Causes**:
- Keycloak service down (if SSO is enabled)
- Database authentication issue
- Session cookie problems

**Resolution**:
1. Verify Keycloak health endpoint
2. Try direct Odoo login (bypassing SSO) to isolate the issue
3. Check Odoo logs for authentication errors
4. Clear browser cookies and retry
5. Check if the user account is locked (too many failed attempts)

#### Email Delivery Failures

**Symptoms**: Outbound emails (invoices, notifications) not being delivered
**Causes**:
- SMTP credentials expired or rotated
- Zoho SMTP rate limiting
- Email marked as spam by recipient's server

**Resolution**:
1. Check Odoo outgoing mail queue: Accounting > Configuration > Emails
2. Verify SMTP settings in Odoo configuration
3. Test SMTP connection from the container
4. Check Zoho admin panel for sending limits and blocks
5. Verify SPF, DKIM, and DMARC records are correct in Cloudflare DNS

---

## Security Operations

### Access Control

| Access Level | Who | What |
|-------------|-----|------|
| Azure Portal (Reader) | All platform team | View resources, logs, metrics |
| Azure Portal (Contributor) | Senior engineers | Modify container apps, database |
| Azure Portal (Owner) | Platform lead, CTO | Full control including IAM |
| Container SSH | Senior engineers | Debug running containers |
| Database Direct | DBA only | Direct PostgreSQL access |
| Key Vault | Managed identity only | Runtime secret access |

### Secret Rotation Schedule

| Secret | Rotation Frequency | Method |
|--------|:------------------:|--------|
| Odoo admin password | 90 days | Update in Key Vault, restart container |
| Database password | 90 days | Azure CLI, update container env vars |
| SMTP credentials | 180 days | Update in Zoho, update Key Vault |
| API keys (MCP, OCR) | 90 days | Regenerate, update Key Vault |
| SSO client secrets | 365 days | Rotate in Keycloak, update Key Vault |

### Security Checklist (Monthly)

- [ ] Review Azure Activity Log for suspicious operations
- [ ] Verify WAF rules are up to date
- [ ] Check for new CVEs affecting container base images
- [ ] Review user access list and remove inactive accounts
- [ ] Verify audit logging is active (OCA auditlog module)
- [ ] Check Odoo user login history for anomalies
- [ ] Test password policy enforcement
- [ ] Verify 2FA is enabled for admin and finance users
