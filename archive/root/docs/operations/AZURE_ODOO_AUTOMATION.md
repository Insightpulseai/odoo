# Azure Odoo Automation — Operational Guide

## Overview

Azure-native automation for Odoo 18 development following "Odoo.sh-equivalent" patterns:
- **Build**: Azure Container Registry (ACR) builds from Dockerfile
- **Deploy**: Azure Container Apps with blue-green revisions
- **Upgrade**: Container Apps Jobs with evidence generation
- **Auth**: GitHub Actions → Azure OIDC (federated identity)

## Pipeline Stages

### 1. Build → Push

**Workflow:** `.github/workflows/odoo-azure-deploy.yml`
**Trigger:** Push to `main` branch (paths: `docker/**`, `config/**`, `addons/**`) OR manual dispatch
**Steps:**
1. Azure OIDC login (no secrets, federated identity)
2. `az acr build` - build Docker image in ACR
3. Tag with `$GITHUB_SHA` + `latest`
4. Push to ACR

**Artifacts:** `{ACR_NAME}.azurecr.io/odoo:{sha}` and `odoo:latest`

### 2. Deploy → Verify

**Steps:**
1. `az containerapp update` - deploy new revision with image `odoo:{sha}`
2. Revision suffix: `sha-{first-7-chars}`
3. Traffic split: 100% to new revision (blue-green switch)
4. Verification: List active revisions with traffic weight

**Zero-downtime:** Container Apps automatically routes traffic to new revision after health checks pass.

### 3. Upgrade → Evidence

**Workflow:** `.github/workflows/odoo-azure-upgrade-evidence.yml`
**Trigger:** Manual dispatch with inputs (db_name, modules, environment)
**Steps:**
1. Generate evidence stamp: `YYYYMMDD-HHMM+0800`
2. Create Container Apps Job (ephemeral)
3. Execute: `odoo-bin --database={db} --update={modules} --stop-after-init`
4. Capture logs: job start, status, execution output
5. Write evidence: `web/docs/evidence/{stamp}/odoo-upgrade/`
6. Commit evidence to repo
7. Delete job

**Evidence Structure:**
```
web/docs/evidence/20260305-1430+0800/odoo-upgrade/
├── summary.json          # Status, metadata, log paths
└── logs/
    ├── upgrade-job-start.log
    ├── upgrade-status.log
    ├── upgrade-execution.log
    └── upgrade-cleanup.log
```

## Required Azure Resources

| Resource | Naming | Purpose |
|----------|--------|---------|
| Resource Group | `rg-ipai-{env}` | Container for all resources |
| Container Registry | `acripai{env}` | Image artifact storage |
| Container App | `ca-odoo-ipai-{env}` | Odoo runtime |
| Container Apps Environment | `containerapp-env-ipai-{env}` | Shared environment for apps/jobs |
| PostgreSQL Flexible Server | `psql-ipai-{env}` | Odoo database |
| Key Vault | `kv-ipai-{env}` | Runtime secrets |
| Managed Identity | `id-ipai-{env}` | RBAC for Container Apps |

**Environments:** `dev`, `staging`, `production`

## Secrets Inventory

### GitHub Actions Secrets

| Secret | Purpose | Where Used |
|--------|---------|------------|
| `AZURE_SUBSCRIPTION_ID` | Azure subscription | All workflows |
| `AZURE_TENANT_ID` | Azure AD tenant | OIDC login |
| `AZURE_CLIENT_ID` | Managed Identity app ID | OIDC login |
| `ACR_NAME` | Container registry name | Build + deploy |
| `CONTAINERAPP_NAME` | Container app name | Deploy + upgrade |

**Note:** No long-lived credentials. OIDC uses federated identity tokens.

### Azure Key Vault (Runtime)

| Secret | Purpose | Used By |
|--------|---------|---------|
| `ODOO_ADMIN_PASSWORD` | Odoo master password | Container App |
| `POSTGRES_PASSWORD` | Database connection | Container App |
| `ODOO_DB_USER` | Database username | Container App |
| `ODOO_DB_HOST` | PostgreSQL FQDN | Container App |

## Evidence Format

All upgrade operations generate evidence bundles following repo standards:

**Path:** `web/docs/evidence/<YYYYMMDD-HHMM+0800>/<topic>/logs/`
**Timezone:** Asia/Manila (UTC+08:00)
**Summary:** `summary.json` with:
- `timestamp`: Evidence stamp
- `database`: Target database name
- `modules`: Upgraded modules (comma-separated)
- `environment`: Deployment environment
- `status`: `COMPLETE` | `PARTIAL` | `BLOCKED`
- `logs`: Object with paths to log files

**Example:**
```json
{
  "timestamp": "20260305-1430+0800",
  "database": "odoo_prod",
  "modules": "ipai_finance_ppm,ipai_ai_tools",
  "environment": "production",
  "status": "COMPLETE",
  "job_name": "odoo-upgrade-1709627400",
  "commit_sha": "ca46f4b99e",
  "triggered_by": "jgtolentino",
  "workflow_run_id": "123456789",
  "logs": {
    "job_start": "web/docs/evidence/20260305-1430+0800/odoo-upgrade/logs/upgrade-job-start.log",
    "status": "web/docs/evidence/20260305-1430+0800/odoo-upgrade/logs/upgrade-status.log",
    "execution": "web/docs/evidence/20260305-1430+0800/odoo-upgrade/logs/upgrade-execution.log",
    "cleanup": "web/docs/evidence/20260305-1430+0800/odoo-upgrade/logs/upgrade-cleanup.log"
  }
}
```

## OIDC Setup (One-Time)

### Prerequisites
1. Azure subscription with Owner role
2. GitHub repository with Actions enabled
3. Azure AD application registration

### Steps
```bash
# 1. Create Azure AD app registration
az ad app create --display-name "github-oidc-odoo"

# 2. Create service principal
APP_ID=$(az ad app list --display-name "github-oidc-odoo" --query "[0].appId" -o tsv)
az ad sp create --id $APP_ID

# 3. Create federated credential for GitHub Actions
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "github-main-branch",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:Insightpulseai/odoo:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'

# 4. Assign RBAC roles
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
az role assignment create \
  --assignee $APP_ID \
  --role "Contributor" \
  --scope "/subscriptions/$SUBSCRIPTION_ID"

# 5. Store secrets in GitHub
# AZURE_CLIENT_ID = $APP_ID
# AZURE_TENANT_ID = $(az account show --query tenantId -o tsv)
# AZURE_SUBSCRIPTION_ID = $SUBSCRIPTION_ID
```

### Verification
```bash
# Test OIDC login in GitHub Actions
# Should succeed without client secret
```

## Rollback Strategy

### Scenario 1: Bad Deployment
```bash
# List revisions
az containerapp revision list \
  --name ca-odoo-ipai-production \
  --resource-group rg-ipai-production

# Activate previous revision
az containerapp revision activate \
  --name ca-odoo-ipai-production \
  --resource-group rg-ipai-production \
  --revision {previous-revision-name}

# Deactivate bad revision
az containerapp revision deactivate \
  --name ca-odoo-ipai-production \
  --resource-group rg-ipai-production \
  --revision {bad-revision-name}
```

### Scenario 2: Failed Upgrade
Evidence in `web/docs/evidence/{stamp}/odoo-upgrade/logs/` will show:
- `upgrade-status.log`: Job status (Failed)
- `upgrade-execution.log`: Odoo upgrade errors

**Recovery:**
1. Fix module code locally
2. Commit + push to trigger deploy workflow
3. Re-run upgrade workflow after successful deploy

## Monitoring

### Key Metrics
- **Deployment Success Rate**: Track via GitHub Actions status
- **Revision Traffic Split**: Monitor Container Apps revisions
- **Upgrade Success Rate**: Parse evidence `status` field from `summary.json`
- **Build Time**: ACR build duration in workflow logs

### Health Checks
```bash
# Container App status
az containerapp show \
  --name ca-odoo-ipai-production \
  --resource-group rg-ipai-production \
  --query "properties.{status:runningStatus,replicas:replicaCount}"

# Recent revisions
az containerapp revision list \
  --name ca-odoo-ipai-production \
  --resource-group rg-ipai-production \
  --query "[?properties.trafficWeight > 0].{name:name,traffic:properties.trafficWeight,active:properties.active}"

# Database connectivity
az postgres flexible-server show \
  --name psql-ipai-production \
  --resource-group rg-ipai-production \
  --query "state"
```

## Troubleshooting

### Issue: OIDC Login Fails
**Symptoms:** `az login` fails with authentication error
**Fix:**
1. Verify federated credential exists: `az ad app federated-credential list --id {APP_ID}`
2. Check subject matches: `repo:Insightpulseai/odoo:ref:refs/heads/main`
3. Ensure RBAC role assigned: `az role assignment list --assignee {APP_ID}`

### Issue: ACR Build Timeout
**Symptoms:** `az acr build` exceeds timeout
**Fix:**
1. Optimize Dockerfile (multi-stage build, layer caching)
2. Increase job timeout in workflow
3. Use ACR Tasks for large builds

### Issue: Container App Not Starting
**Symptoms:** Revision shows 0 replicas
**Fix:**
1. Check logs: `az containerapp logs show --name {app} --resource-group {rg}`
2. Verify secrets in Key Vault: `az keyvault secret list --vault-name kv-ipai-{env}`
3. Check PostgreSQL connectivity: `az postgres flexible-server show`

### Issue: Evidence Not Committing
**Symptoms:** Evidence generated but not in repo
**Fix:**
1. Check git config in workflow (user.name, user.email)
2. Verify `contents: write` permission in workflow
3. Ensure evidence path exists before commit

## References

- **SSOT Model:** `infra/dns/subdomain-registry.yaml` (proven pattern)
- **Workflows:** `.github/workflows/odoo-azure-*.yml`
- **Azure Resources:** `ssot/azure/resources.yaml`
- **Evidence Standards:** `docs/agent_instructions/SSOT.md`
- **Azure Container Apps Docs:** https://learn.microsoft.com/azure/container-apps/
- **GitHub OIDC:** https://docs.github.com/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-azure
