---
title: "Deployment Guide"
kb_scope: "ops-kb"
group_ids: ["group-guid-placeholder"]
last_updated: "2026-03-15"
---

# Deployment Guide

## Overview

This document covers the deployment procedures for the InsightPulse AI platform on Azure Container Apps. It includes the CI/CD pipeline configuration, deployment strategies, rollback procedures, and environment management.

---

## Environments

### Environment Matrix

| Environment | Purpose | Branch | URL | Database |
|-------------|---------|--------|-----|----------|
| Development | Feature development and testing | `develop` | `dev-erp.insightpulseai.com` | `odoo_dev` |
| Staging | Pre-production validation | `staging` | `staging-erp.insightpulseai.com` | `odoo_staging` |
| Production | Live system | `main` | `erp.insightpulseai.com` | `odoo` |

### Environment Parity

All environments use identical:
- Container images (tagged by environment)
- Azure Container App configuration (differing only in resource limits)
- PostgreSQL version and extensions
- OCA and IPAI module versions (promoted through environments)

Differences between environments:
- Resource allocation (production has higher limits)
- Replica count (production has more replicas)
- Database size and data (production has real data; dev/staging have anonymized copies)
- Secret values (each environment has its own Key Vault entries)

---

## CI/CD Pipeline

### Pipeline Architecture

```
Developer Push / PR Merge
    |
    v
GitHub Actions Workflow
    |
    +-- Lint & Static Analysis (ruff, pylint, mypy)
    +-- Unit Tests (pytest, disposable DB)
    +-- Security Scan (Trivy container scan)
    +-- Build Container Image
    +-- Push to Azure Container Registry
    |
    v
Deploy to Target Environment
    |
    +-- Create new Container App revision
    +-- Run health checks
    +-- Route traffic (blue-green or canary)
    |
    v
Post-Deployment Validation
    |
    +-- Smoke tests
    +-- Integration tests
    +-- Monitoring baseline comparison
```

### GitHub Actions Workflows

#### Build and Test (`ci.yml`)

Triggered on: Pull request to `develop`, `staging`, `main`

Steps:
1. Checkout code
2. Set up Python 3.12
3. Install dependencies from `requirements.txt`
4. Run linting: `ruff check .`
5. Run type checking: `mypy addons/ipai_*/`
6. Run unit tests: `pytest tests/ --tb=short`
7. Build Docker image
8. Run Trivy vulnerability scan on the image
9. Push image to ACR if all checks pass

#### Deploy to Development (`deploy-dev.yml`)

Triggered on: Push to `develop` branch (after CI passes)

Steps:
1. Pull the latest image from ACR
2. Create a new Container App revision for `ipai-odoo-dev-web`
3. Run Odoo module update: `-u all --stop-after-init`
4. Verify health endpoint returns 200
5. Route 100% traffic to new revision
6. Post deployment notification to Slack #deployments

#### Deploy to Staging (`deploy-staging.yml`)

Triggered on: Push to `staging` branch

Steps:
1. Same as dev deployment
2. Additionally run integration tests against staging
3. Refresh staging database from anonymized production backup (weekly)
4. Run full module install test: `-i all --stop-after-init`

#### Deploy to Production (`deploy-prod.yml`)

Triggered on: Push to `main` branch (requires manual approval)

Steps:
1. Create a new revision with 0% traffic
2. Run health checks on the new revision
3. Canary deployment: route 10% traffic to new revision
4. Monitor error rate for 15 minutes
5. If error rate < 1%: route 50% traffic
6. Monitor for 15 minutes
7. If still healthy: route 100% traffic
8. Deactivate old revision after 1 hour
9. Post deployment notification to Slack #deployments

---

## Container Image Management

### Docker Image Structure

```dockerfile
# Base image: Odoo CE 18.0 on Python 3.12
FROM odoo:18.0

# Install OCA module dependencies
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy OCA modules
COPY addons/oca/ /mnt/extra-addons/oca/

# Copy IPAI custom modules
COPY addons/ipai_*/ /mnt/extra-addons/ipai/

# Copy configuration
COPY config/odoo.conf /etc/odoo/

# Set addons path
ENV ADDONS_PATH="/mnt/extra-addons/oca,/mnt/extra-addons/ipai,/opt/odoo/addons"
```

### Image Tagging Convention

| Tag Format | Example | Purpose |
|-----------|---------|---------|
| `<branch>-<sha>` | `develop-a1b2c3d` | Specific commit on a branch |
| `<branch>-latest` | `staging-latest` | Latest successful build on a branch |
| `v<semver>` | `v1.2.3` | Production release tag |
| `<branch>-<date>` | `main-20260315` | Daily production build |

### Azure Container Registry

- **Registry**: `acripaidev.azurecr.io`
- **Repository**: `ipai-odoo`
- **Retention**: Keep last 30 images per branch, keep all tagged releases

---

## Deployment Strategies

### Blue-Green Deployment (Default for Production)

Blue-green deployment runs two identical environments and switches traffic between them:

1. **Blue** (current production) is running and serving all traffic
2. **Green** (new version) is deployed alongside Blue with 0% traffic
3. Health checks verify Green is healthy
4. Traffic is switched from Blue to Green
5. Blue is kept running for 1 hour as a rollback target
6. Blue is deactivated after the rollback window

**Azure Container Apps Implementation:**
- Each deployment creates a new "revision"
- Traffic weight is controlled via revision management
- Rollback = reactivate the previous revision and route traffic

### Canary Deployment (For Risky Changes)

For changes with higher risk (database migrations, breaking API changes):

1. Deploy new revision with 0% traffic
2. Route 5% of traffic to new revision
3. Monitor for 30 minutes (error rate, latency, user feedback)
4. If healthy: increase to 25%, monitor 30 minutes
5. If still healthy: increase to 50%, monitor 30 minutes
6. If still healthy: increase to 100%
7. At any step, if unhealthy: roll back to 0% on new revision

### Rolling Update (For Low-Risk Changes)

For configuration changes, minor bug fixes, or content updates:

1. Deploy new revision
2. Route 100% traffic immediately
3. Monitor for issues
4. Rollback if needed

---

## Database Migrations

### Odoo Module Updates

When deploying module changes that require database updates:

1. **Pre-deployment**: Take a database snapshot
   ```
   az postgres flexible-server backup create
   ```

2. **Run the update**:
   ```
   odoo-bin -d odoo -u <module_list> --stop-after-init
   ```

3. **Verify**: Check Odoo logs for migration errors

4. **Post-deployment**: Verify the module version in Odoo Settings > Apps

### Migration Best Practices

1. **Always test migrations on staging first** using a copy of production data
2. **Never run `-u all` in production** unless absolutely necessary (it is slow and risky)
3. **Update only the changed modules**: `-u ipai_finance_ppm,ipai_ai_copilot`
4. **Back up before any migration**: Database snapshots are fast and cheap
5. **Monitor migration logs**: Check for `WARNING` and `ERROR` messages
6. **Lock the system during migration**: Set maintenance mode or restrict access

### Schema Change Guidelines

| Change Type | Risk | Procedure |
|-------------|:----:|-----------|
| Add a new field (no default) | Low | Standard module update |
| Add a new field (with default) | Medium | Test on staging; may lock large tables |
| Add an index | Medium | May lock the table during creation; use `CREATE INDEX CONCURRENTLY` for large tables |
| Drop a field | High | Ensure no code references the field; test thoroughly |
| Rename a field | High | Use Odoo migration scripts; requires `pre_init_hook` or `post_init_hook` |
| Add a new model | Low | Standard module update |
| Drop a model | High | Ensure all foreign keys and references are removed first |

---

## Rollback Procedures

### Container Rollback (Immediate, < 5 minutes)

If a deployment causes issues:

1. **Identify the previous working revision**:
   ```
   az containerapp revision list --name ipai-odoo-dev-web --resource-group rg-ipai-dev -o table
   ```

2. **Route traffic to the previous revision**:
   ```
   az containerapp ingress traffic set --name ipai-odoo-dev-web \
     --resource-group rg-ipai-dev \
     --revision-weight <old-revision>=100
   ```

3. **Verify**: Check the health endpoint and user-facing functionality

4. **Investigate**: Review logs from the failed revision to determine root cause

### Database Rollback (30-60 minutes)

If a database migration causes issues:

1. **Restore from point-in-time recovery**:
   ```
   az postgres flexible-server restore \
     --source-server <source> \
     --restore-time <pre-migration-timestamp> \
     --name <new-server-name>
   ```

2. **Update the container app** to point to the restored database

3. **Roll back the container** to the pre-migration revision

4. **Verify**: Full functionality check

### Full Rollback (2-4 hours)

For catastrophic failures requiring complete environment restoration:

1. Deploy infrastructure from IaC templates
2. Restore database from latest good backup
3. Deploy last known good container image
4. Restore Key Vault secrets
5. Verify DNS resolution
6. Run full health check suite
7. Notify users of restoration

---

## Environment Configuration

### Environment Variables

All services use environment variables for configuration. Variables are sourced from Azure Key Vault via managed identity.

| Variable | Description | Source |
|----------|-------------|--------|
| `DB_HOST` | PostgreSQL hostname | Key Vault |
| `DB_PORT` | PostgreSQL port | Container App env |
| `DB_NAME` | Database name | Container App env |
| `DB_USER` | Database username | Key Vault |
| `DB_PASSWORD` | Database password | Key Vault |
| `ODOO_ADMIN_PASSWORD` | Odoo master password | Key Vault |
| `SMTP_HOST` | Zoho SMTP host | Container App env |
| `SMTP_PORT` | Zoho SMTP port | Container App env |
| `SMTP_USER` | Zoho SMTP username | Key Vault |
| `SMTP_PASSWORD` | Zoho SMTP password | Key Vault |
| `MCP_ENDPOINT` | MCP service URL | Container App env |
| `MCP_API_KEY` | MCP authentication key | Key Vault |
| `AZURE_SEARCH_ENDPOINT` | AI Search endpoint | Container App env |
| `AZURE_SEARCH_API_KEY` | AI Search key | Key Vault |

### Configuration Management

1. **Infrastructure as Code**: All Azure resources defined in Bicep/Terraform templates
2. **Container Configuration**: Defined in Container App YAML manifests
3. **Odoo Configuration**: `odoo.conf` baked into the container image
4. **Secrets**: Managed exclusively via Azure Key Vault (never in code or config files)
5. **Version Control**: All configuration files (except secrets) are in the Git repository

---

## Deployment Checklist

### Pre-Deployment

- [ ] All CI checks pass (lint, test, security scan)
- [ ] Code reviewed and approved (PR merged)
- [ ] Migration tested on staging with production-like data
- [ ] Rollback plan documented
- [ ] Stakeholders notified of deployment window
- [ ] Database backup taken (for production deployments)

### During Deployment

- [ ] Monitor container app revision creation
- [ ] Verify health check passes on new revision
- [ ] Monitor error rates during traffic shift
- [ ] Watch Slack #deployments for automated notifications

### Post-Deployment

- [ ] Verify all health endpoints return 200
- [ ] Spot-check key user workflows (login, create invoice, run report)
- [ ] Monitor error rate for 30 minutes post-deployment
- [ ] Confirm no increase in support tickets
- [ ] Deactivate old revision after rollback window (1 hour for production)
- [ ] Update deployment log with revision, timestamp, and changes

---

## Deployment Log Template

| Field | Value |
|-------|-------|
| Date | YYYY-MM-DD HH:MM |
| Environment | dev / staging / production |
| Deployer | Name |
| Revision | Container App revision name |
| Image Tag | ACR image tag |
| Changes | Brief description of what changed |
| Migration | Yes/No (if database migration was required) |
| Rollback | N/A / Performed (with reason) |
| Duration | Total deployment time |
| Status | Success / Partial / Failed |
| Notes | Any observations or issues |
