# BCDR Runbook — Odoo on Azure

> Business Continuity and Disaster Recovery procedures for the InsightPulseAI platform.
> Last verified: 2026-04-09

---

## Scope

| Service | RTO Target | RPO Target | Recovery Method |
|---------|:----------:|:----------:|-----------------|
| Odoo Web/Worker/Cron | 15 min | 0 (stateless) | ACA revision rollback or redeploy |
| PostgreSQL | 30 min | 5 min (PITR) | Point-in-time restore |
| Key Vault | 5 min | 0 (immutable) | Soft-delete recovery |
| Front Door | 10 min | 0 (config) | Route/origin reconfiguration |
| Filestore | 30 min | 24h (snapshot) | Azure Files restore |

---

## 1. ACA Application Failure

### Symptoms
- Alert: `alert-ipai-aca-web-zero-replicas` (Sev 0)
- Alert: `alert-ipai-aca-web-restarts` (Sev 1)
- `curl -sf https://erp.insightpulseai.com/web/login` fails

### Recovery: Restart current revision

```bash
az containerapp revision restart \
  -n ipai-odoo-dev-web \
  -g rg-ipai-dev-odoo-runtime \
  --revision $(az containerapp show -n ipai-odoo-dev-web -g rg-ipai-dev-odoo-runtime --query properties.latestRevisionName -o tsv)
```

### Recovery: Rollback to stable revision

```bash
# List revisions
az containerapp revision list -n ipai-odoo-dev-web -g rg-ipai-dev-odoo-runtime -o table

# Activate previous revision and shift traffic
az containerapp ingress traffic set -n ipai-odoo-dev-web -g rg-ipai-dev-odoo-runtime \
  --revision-weight <previous-revision>=100

# Or use the stable label
az containerapp ingress traffic set -n ipai-odoo-dev-web -g rg-ipai-dev-odoo-runtime \
  --label-weight stable=100
```

### Recovery: Full redeploy

```bash
az containerapp update -n ipai-odoo-dev-web -g rg-ipai-dev-odoo-runtime \
  --image acripaiodoo.azurecr.io/ipai-odoo:18.0-copilot
```

### Verify

```bash
az containerapp replica list -n ipai-odoo-dev-web -g rg-ipai-dev-odoo-runtime -o table
curl -sf https://erp.insightpulseai.com/web/login | head -5
```

---

## 2. PostgreSQL Failure

### Symptoms
- Alert: `alert-ipai-pg-cpu-high` (Sev 2)
- Odoo returns 500 errors / connection refused
- `az postgres flexible-server show --name pg-ipai-odoo -g rg-ipai-dev-odoo-data --query state` != "Ready"

### Recovery: Automatic HA failover

Zone-redundant HA is enabled. Automatic failover occurs when:
- Primary zone is unavailable
- Primary server is unresponsive

No manual action needed. Monitor:

```bash
az postgres flexible-server show --name pg-ipai-odoo -g rg-ipai-dev-odoo-data \
  --query "{state:state,ha:highAvailability.state,zone:availabilityZone}" -o json
```

### Recovery: Forced failover (manual)

```bash
az postgres flexible-server restart --name pg-ipai-odoo -g rg-ipai-dev-odoo-data --failover Forced
```

### Recovery: Point-in-time restore

```bash
# Restore to a new server (35-day retention window)
az postgres flexible-server restore \
  --name pg-ipai-odoo-restored \
  --resource-group rg-ipai-dev-odoo-data \
  --source-server pg-ipai-odoo \
  --restore-time "2026-04-09T10:00:00Z"
```

After restore:
1. Verify data integrity on restored server
2. Update ACA secret `db-password` in Key Vault if connection string changes
3. Update ACA apps to point to new server hostname
4. Verify Odoo connectivity

```bash
az containerapp secret set -n ipai-odoo-dev-web -g rg-ipai-dev-odoo-runtime \
  --secrets "db-password=keyvaultref:https://kv-ipai-dev.vault.azure.net/secrets/odoo-pg-password,identityref:system"
az containerapp revision restart -n ipai-odoo-dev-web -g rg-ipai-dev-odoo-runtime \
  --revision $(az containerapp show -n ipai-odoo-dev-web -g rg-ipai-dev-odoo-runtime --query properties.latestRevisionName -o tsv)
```

---

## 3. Key Vault Failure

### Recovery: Soft-delete recovery

Key Vault has soft-delete enabled (90-day retention).

```bash
# List deleted vaults
az keyvault list-deleted -o table

# Recover
az keyvault recover --name kv-ipai-dev
```

### Recovery: Secret version rollback

```bash
# List versions of a secret
az keyvault secret list-versions --vault-name kv-ipai-dev --name odoo-pg-password -o table

# Set previous version as current
az keyvault secret set --vault-name kv-ipai-dev --name odoo-pg-password --value "<previous-value>"
```

---

## 4. Front Door Failure

### Symptoms
- TLS errors on `erp.insightpulseai.com`
- 502/504 errors from AFD

### Recovery: Bypass AFD (emergency)

Temporarily point DNS directly to ACA FQDN:

```bash
az network dns record-set cname set-record \
  --zone-name insightpulseai.com \
  --resource-group <dns-rg> \
  --record-set-name erp \
  --cname ipai-odoo-dev-web.blackstone-0df78186.southeastasia.azurecontainerapps.io
```

**Warning**: This bypasses WAF protection. Revert as soon as AFD is healthy.

### Recovery: Purge AFD cache

```bash
az afd endpoint purge \
  --profile-name afd-ipai-dev \
  -g rg-ipai-dev-odoo-runtime \
  --endpoint-name afd-ipai-dev-ep \
  --content-paths '/*'
```

---

## 5. Full Region Failure (Southeast Asia)

### Pre-requisites (not yet in place)
- Geo-redundant PG backup (currently disabled — creation-time property)
- Cross-region ACA environment
- AFD origin group with secondary region

### Manual recovery steps
1. Restore PG from geo-backup to secondary region
2. Deploy ACA apps in secondary region
3. Update AFD origin group to point to secondary region
4. Verify and monitor

---

## 6. Verification Checklist

After any recovery action:

```bash
# 1. PG is Ready
az postgres flexible-server show --name pg-ipai-odoo -g rg-ipai-dev-odoo-data --query state -o tsv

# 2. ACA replicas running
az containerapp replica list -n ipai-odoo-dev-web -g rg-ipai-dev-odoo-runtime -o table

# 3. Odoo responds
curl -sf https://erp.insightpulseai.com/web/login -o /dev/null -w "%{http_code}"

# 4. Odoo can read/write DB
curl -sf https://ipai-odoo-dev-web.blackstone-0df78186.southeastasia.azurecontainerapps.io/web/login -o /dev/null -w "%{http_code}"

# 5. Key Vault accessible
az keyvault secret show --vault-name kv-ipai-dev --name odoo-pg-password --query "name" -o tsv

# 6. Alerts are firing (not suppressed)
az monitor metrics alert list -g rg-ipai-dev-odoo-runtime --query "[].{name:name,enabled:enabled}" -o table
```

---

## Contact & Escalation

| Role | Contact | When |
|------|---------|------|
| Platform Admin | admin@insightpulseai.com | All incidents |
| Azure Support | Azure Portal → Support | Sev A/B for PG or AFD |

---

*Last updated: 2026-04-09*
