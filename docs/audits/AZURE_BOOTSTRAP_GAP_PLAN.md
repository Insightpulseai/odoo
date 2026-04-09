# Azure Bootstrap Gap Plan

> Audit date: 2026-03-14
> Scope: Gap between `deploy-azure.yml` workflow expectations and actual Azure resource state.
> Action: Research and plan only. Nothing provisioned.

---

## 1. Workflow Assumptions Extracted

### 1.1 deploy-azure.yml (canonical Azure-native CI/CD)

| Assumption | Source (line) | Value |
|---|---|---|
| **OIDC auth** | `id-token: write` (L23), `azure/login@v2` (L59) | Requires federated identity credential on an Entra ID app registration |
| **Secret: AZURE_CLIENT_ID** | L61 | GitHub Actions secret -- app registration client ID |
| **Secret: AZURE_TENANT_ID** | L62 | GitHub Actions secret -- `402de71a-87ec-4302-a609-fb76098d1da7` |
| **Secret: AZURE_SUBSCRIPTION_ID** | L63 | GitHub Actions secret -- `536d8cf6-89e1-4815-aef3-d5f2c5f4d070` |
| **Var/default: ACR_REGISTRY** | L30 | `cripaidev.azurecr.io` |
| **Var/default: ACR_REPO** | L31 | `ipai-odoo` |
| **Var/default: ACA_RESOURCE_GROUP** | L32 | `rg-ipai-dev` |
| **Var/default: ACA_APP_NAME** | L33 | `ipai-odoo-dev-web` |
| **Dockerfile** | L72 | `docker/Dockerfile.unified` |
| **ACA update command** | L103 | `az containerapp update --name ipai-odoo-dev-web --resource-group rg-ipai-dev --image <tag>` |
| **Health check URL** | L141 | `https://erp.insightpulseai.com/web/health` |

### 1.2 deploy-production.yml (legacy SSH-based -- for reference)

Uses SSH to a DO droplet (`secrets.SSH_HOST`). Targets `ghcr.io/jgtolentino/odoo`. NOT Azure-native. Included for completeness -- this is the deprecated path.

### 1.3 deploy-odoo-prod.yml (legacy SSH module upgrade)

Uses `appleboy/ssh-action` to SSH into `secrets.ODOO_PROD_HOST`. Targets a self-hosted runner. Also deprecated for Azure migration.

---

## 2. Confirmed Azure Resource State (from resources.yaml + prior investigation)

### 2.1 Resources That EXIST

| Resource | Type | RG | Notes |
|---|---|---|---|
| `rg-ipai-dev` | Resource Group | -- | EXISTS, active |
| `rg-ipai-shared-dev` | Resource Group | -- | EXISTS, contains shared services |
| `rg-ipai-agents-dev` | Resource Group | -- | EXISTS, earlier Deployment A |
| `ipai-odoo-dev-web` | Container App | `rg-ipai-dev` | EXISTS (Deployment B) |
| `ipai-odoo-dev-worker` | Container App | `rg-ipai-dev` | EXISTS |
| `ipai-odoo-dev-cron` | Container App | `rg-ipai-dev` | EXISTS |
| `ipai-odoo-dev-env` | ACA Environment | `rg-ipai-dev` | EXISTS |
| `cripaidev` | ACR | `rg-ipai-shared-dev` | EXISTS, login server: `cripaidev.azurecr.io` |
| `ipaiodoodevacr` | ACR | `rg-ipai-dev` | EXISTS, Odoo-specific |
| `ipai-odoo-dev-pg` | PG Flexible Server | `rg-ipai-dev` | EXISTS |
| `ipai-odoo-dev-kv` | Key Vault | `rg-ipai-dev` | EXISTS |
| `kv-ipai-dev` | Key Vault | `rg-ipai-shared-dev` | EXISTS |
| `ipai-fd-dev` | Front Door | `rg-ipai-shared-dev` | EXISTS |
| `ipaiDevWafPolicy` | WAF Policy | `rg-ipai-shared-dev` | EXISTS |
| `id-ipai-aca-dev` | Managed Identity | `rg-ipai-agents-dev` | EXISTS (Deployment A) |
| `id-ipai-agents-dev` | Managed Identity | `rg-ipai-shared-dev` | EXISTS |
| `law-ipai-dev` | Log Analytics | `rg-ipai-shared-dev` | EXISTS |
| `appi-ipai-dev` | App Insights | `rg-ipai-shared-dev` | EXISTS |

### 2.2 Resources That DO NOT EXIST (per prior investigation)

| Resource | Expected By | Status |
|---|---|---|
| Entra ID app registration for OIDC | `deploy-azure.yml` | MISSING |
| Federated identity credential (GitHub OIDC) | `deploy-azure.yml` | MISSING |
| GitHub secret: `AZURE_CLIENT_ID` | `deploy-azure.yml` | MISSING |
| GitHub secret: `AZURE_TENANT_ID` | `deploy-azure.yml` | MISSING |
| GitHub secret: `AZURE_SUBSCRIPTION_ID` | `deploy-azure.yml` | MISSING |
| RBAC: AcrPush on `cripaidev` for CI identity | `deploy-azure.yml` (L66 `az acr login`) | MISSING |
| RBAC: Contributor on ACA for CI identity | `deploy-azure.yml` (L103 `az containerapp update`) | MISSING |

---

## 3. Complete Gap Matrix

### 3.1 Authentication and Identity

| # | Resource | Type | Expected Name | RG | IaC File | IaC Status | Gap |
|---|---|---|---|---|---|---|---|
| A1 | Entra ID App Registration | `Microsoft.Graph/applications` | `sp-ipai-github-cicd` | N/A (tenant-level) | NONE | No IaC | **CRITICAL** -- no app reg exists for OIDC |
| A2 | Federated Identity Credential | Entra ID federation | Subject: `repo:Insightpulseai/odoo:ref:refs/heads/main` | N/A | NONE | No IaC | **CRITICAL** -- OIDC login will fail |
| A3 | Service Principal RBAC -- AcrPush | Role Assignment | AcrPush on `cripaidev` | `rg-ipai-shared-dev` | NONE | No IaC | **CRITICAL** -- `az acr login` will fail |
| A4 | Service Principal RBAC -- ACA Contributor | Role Assignment | Contributor on ACA apps | `rg-ipai-dev` | NONE | No IaC | **CRITICAL** -- `az containerapp update` will fail |
| A5 | GitHub Secret: `AZURE_CLIENT_ID` | GitHub Actions secret | -- | N/A | N/A | N/A | **CRITICAL** -- workflow step will error |
| A6 | GitHub Secret: `AZURE_TENANT_ID` | GitHub Actions secret | -- | N/A | N/A | N/A | **CRITICAL** -- workflow step will error |
| A7 | GitHub Secret: `AZURE_SUBSCRIPTION_ID` | GitHub Actions secret | -- | N/A | N/A | N/A | **CRITICAL** -- workflow step will error |

### 3.2 Container Registry

| # | Resource | Type | Expected Name | RG | IaC File | IaC Status | Gap |
|---|---|---|---|---|---|---|---|
| R1 | ACR | `Microsoft.ContainerRegistry` | `cripaidev` | `rg-ipai-shared-dev` | `infra/azure/modules/acr.bicep` | Complete module | **NONE** -- resource exists |
| R2 | ACR repository `ipai-odoo` | ACR repository | `ipai-odoo` | -- | N/A (created on first push) | N/A | **MINOR** -- auto-created on first `docker push` |
| R3 | ACR admin disabled | Config | `adminUserEnabled: false` | -- | `acr.bicep` L24 | Correct | **NONE** -- Bicep matches best practice |

### 3.3 Container Apps (Compute)

| # | Resource | Type | Expected Name | RG | IaC File | IaC Status | Gap |
|---|---|---|---|---|---|---|---|
| C1 | ACA Environment | `managedEnvironments` | `ipai-odoo-dev-env` | `rg-ipai-dev` | `modules/container-apps.bicep` | Complete | **NONE** -- exists |
| C2 | ACA App: odoo-web | `containerApps` | `ipai-odoo-dev-web` | `rg-ipai-dev` | `modules/aca-odoo-services.bicep` | Complete | **NONE** -- exists |
| C3 | ACA App: odoo-worker | `containerApps` | `ipai-odoo-dev-worker` | `rg-ipai-dev` | `modules/aca-odoo-services.bicep` | Complete | **NONE** -- exists |
| C4 | ACA App: odoo-cron | `containerApps` | `ipai-odoo-dev-cron` | `rg-ipai-dev` | `modules/aca-odoo-services.bicep` | Complete | **NONE** -- exists |
| C5 | Managed Identity for ACA | `userAssignedIdentities` | `id-ipai-aca-dev` | `rg-ipai-agents-dev` | NONE for Deployment B | **Stub** | **MEDIUM** -- identity exists for Deployment A but may not have correct RBAC for Deployment B resources |
| C6 | ACA registry auth via MI | Config | Identity-based pull from `cripaidev` | -- | `aca-odoo-services.bicep` L166-169 | Complete | **MEDIUM** -- Bicep expects MI-based auth, but workflow uses `az acr login` (token-based). Mismatch. |

### 3.4 Edge (Front Door)

| # | Resource | Type | Expected Name | RG | IaC File | IaC Status | Gap |
|---|---|---|---|---|---|---|---|
| E1 | Front Door profile | `Microsoft.Cdn/profiles` | `ipai-fd-dev` | `rg-ipai-shared-dev` | `modules/front-door.bicep` | Complete (648 lines) | **NONE** -- exists |
| E2 | WAF policy | `FrontDoorWebApplicationFirewallPolicies` | `ipaiDevWafPolicy` | `rg-ipai-shared-dev` | `modules/front-door.bicep` | Complete | **NONE** -- exists |
| E3 | Custom domain: `erp.insightpulseai.com` | Front Door custom domain | -- | -- | Parameterized in front-door.bicep | Complete | **UNKNOWN** -- domain binding and TLS validation status not confirmed |
| E4 | Origin group pointing to ACA | Front Door origin | odoo-web origin | -- | Parameterized | Complete | **UNKNOWN** -- whether origin is configured to Deployment A or B |

### 3.5 Database

| # | Resource | Type | Expected Name | RG | IaC File | IaC Status | Gap |
|---|---|---|---|---|---|---|---|
| D1 | PG Flexible Server | `flexibleServers` | `ipai-odoo-dev-pg` | `rg-ipai-dev` | `modules/postgres-flexible.bicep` | Complete | **NONE** -- exists |
| D2 | PG database: `odoo` | Database | `odoo` | -- | `postgres-flexible.bicep` L68-75 | Complete | **UNKNOWN** -- database existence not verified |
| D3 | PG KV secrets | Key Vault secrets | `pg-odoo-user`, `pg-odoo-password` | `ipai-odoo-dev-kv` | `aca-odoo-services.bicep` L115-123 (references) | References only | **MEDIUM** -- secrets must be populated manually in KV |

### 3.6 Secrets and Wiring

| # | Resource | Type | Expected Name | Location | IaC File | IaC Status | Gap |
|---|---|---|---|---|---|---|---|
| W1 | KV secret: pg-odoo-user | Key Vault secret | `pg-odoo-user` | `ipai-odoo-dev-kv` | Referenced in Bicep, not created | N/A | **HIGH** -- must be manually seeded |
| W2 | KV secret: pg-odoo-password | Key Vault secret | `pg-odoo-password` | `ipai-odoo-dev-kv` | Referenced in Bicep, not created | N/A | **HIGH** -- must be manually seeded |
| W3 | KV secret: zoho-smtp-user | Key Vault secret | `zoho-smtp-user` | `kv-ipai-dev` | Referenced in SSOT rules | N/A | **MEDIUM** -- mail won't work without it |
| W4 | KV secret: zoho-smtp-password | Key Vault secret | `zoho-smtp-password` | `kv-ipai-dev` | Referenced in SSOT rules | N/A | **MEDIUM** -- mail won't work without it |
| W5 | DNS: `erp.insightpulseai.com` CNAME | Cloudflare DNS | CNAME to Front Door | Cloudflare | `infra/dns/subdomain-registry.yaml` | Declared | **UNKNOWN** -- current target may point to DO droplet |
| W6 | Front Door custom domain TLS | TLS cert | Managed certificate | Front Door | front-door.bicep L280 | Parameterized | **UNKNOWN** -- validation may not be complete |

---

## 4. Workflow-to-Resource Dependency Chain

```
deploy-azure.yml execution path:

  [1] azure/login@v2 (OIDC)
       |
       +-- Requires: Entra App Reg (A1)
       +-- Requires: Federated Credential (A2)
       +-- Requires: GitHub secrets (A5, A6, A7)
       |
  [2] az acr login --name cripaidev
       |
       +-- Requires: ACR exists (R1) ............ OK
       +-- Requires: AcrPush RBAC (A3) .......... MISSING
       |
  [3] docker build + docker push
       |
       +-- Requires: Dockerfile.unified ......... OK (exists)
       +-- Requires: ACR repository ............. OK (auto-created)
       |
  [4] az containerapp update
       |
       +-- Requires: ACA app exists (C2) ........ OK
       +-- Requires: Contributor RBAC (A4) ...... MISSING
       +-- Requires: ACA can pull from ACR ...... UNCERTAIN (C5, C6)
       |
  [5] Health check: curl erp.insightpulseai.com
       |
       +-- Requires: DNS CNAME (W5) ............. UNCERTAIN
       +-- Requires: Front Door origin (E4) ..... UNCERTAIN
       +-- Requires: TLS validation (W6) ........ UNCERTAIN
       +-- Requires: DB connectivity (D2, D3) ... UNCERTAIN
```

**Blocking chain**: Steps 1-4 will all fail without the A1-A7 items. The workflow cannot run at all today.

---

## 5. IaC Coverage Assessment

| Bicep File | Purpose | Completeness | Notes |
|---|---|---|---|
| `infra/azure/main.bicep` | Orchestrator (KV, storage, Databricks, App Service, FD, APIM, Odoo) | **80%** | All modules wired. Odoo services gated by `enableOdooServices` param. Does NOT include ACR or PG directly (those are in `odoo-runtime.bicep`). |
| `infra/azure/odoo-runtime.bicep` | Self-contained Odoo stack (ACR + PG + ACA + KV) | **90%** | Complete. Uses `modules/container-apps.bicep` (different from `aca-odoo-services.bicep`). |
| `modules/acr.bicep` | ACR module | **100%** | Simple, complete. |
| `modules/container-apps.bicep` | Full 9-service ACA environment | **95%** | Complete for all services. Uses username/password registry auth (not MI). |
| `modules/aca-odoo-services.bicep` | 3-role Odoo ACA (web/worker/cron) | **95%** | Complete. Uses MI-based registry auth + KV secret references. |
| `modules/front-door.bicep` | Front Door Premium + WAF + rules engine | **100%** | Comprehensive: WAF, caching, security headers, WebSocket, rate limiting. |
| `modules/postgres-flexible.bicep` | PG Flexible Server | **95%** | Includes Odoo-tuned params. Missing: VNet integration parameters for ACA. |
| `modules/keyvault.bicep` | Key Vault | **90%** | RBAC-enabled, soft delete, purge protection. Missing: secret seeding. |
| `platform/main.bicep` | Phase 0 landing zone (RG scaffold) | **100%** | Subscription-scoped. Creates 3 RGs. |

**Gap**: There are TWO competing Odoo deployment templates:
1. `odoo-runtime.bicep` -- standalone, uses `modules/container-apps.bicep` (different module)
2. `main.bicep` + `modules/aca-odoo-services.bicep` -- part of the larger platform orchestrator

The workflow (`deploy-azure.yml`) does NOT deploy infrastructure -- it only updates an existing ACA app with a new image. All infrastructure must be pre-provisioned.

**Missing from IaC entirely**:
- Entra ID app registration + federated credential (cannot be expressed in Bicep, requires Microsoft Graph API or az CLI)
- RBAC role assignments for CI/CD service principal
- Key Vault secret values (by design -- secrets are runtime concerns)
- DNS records (managed by Cloudflare, not Azure)

---

## 6. Phased Bootstrap Plan

### Phase 0: Prerequisites (non-Azure)

| Step | Action | Tool | Notes |
|---|---|---|---|
| P0.1 | Verify `az` CLI access to subscription `536d8cf6-89e1-4815-aef3-d5f2c5f4d070` | `az account show` | Must confirm working login before anything else |
| P0.2 | Register required resource providers | `infra/azure/scripts/register-providers.sh` | Script exists but is incomplete -- missing `Microsoft.App`, `Microsoft.ContainerRegistry`, `Microsoft.KeyVault`, `Microsoft.Cdn`, `Microsoft.DBforPostgreSQL` |

### Phase 1: Auth (OIDC + Managed Identity + RBAC)

| Step | Action | Command / Tool | Blocking? |
|---|---|---|---|
| 1.1 | Create Entra ID app registration | `az ad app create --display-name sp-ipai-github-cicd` | YES -- blocks all CI/CD |
| 1.2 | Create service principal | `az ad sp create --id <app-id>` | YES |
| 1.3 | Add federated identity credential for GitHub OIDC | `az ad app federated-credential create --id <app-id> --parameters '{"name":"github-main","issuer":"https://token.actions.githubusercontent.com","subject":"repo:Insightpulseai/odoo:ref:refs/heads/main","audiences":["api://AzureADTokenExchange"]}'` | YES |
| 1.4 | Add federated credential for environment-scoped deploys | Same as 1.3 with subject `repo:Insightpulseai/odoo:environment:staging` (and `dev`, `prod`) | YES for environment-gated deploys |
| 1.5 | Grant AcrPush role on `cripaidev` | `az role assignment create --assignee <sp-object-id> --role AcrPush --scope /subscriptions/.../resourceGroups/rg-ipai-shared-dev/providers/Microsoft.ContainerRegistry/registries/cripaidev` | YES |
| 1.6 | Grant Contributor on `rg-ipai-dev` (for `az containerapp update`) | `az role assignment create --assignee <sp-object-id> --role Contributor --scope /subscriptions/.../resourceGroups/rg-ipai-dev` | YES |
| 1.7 | Set GitHub secrets | `gh secret set AZURE_CLIENT_ID --body <value>`, same for `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID` | YES |
| 1.8 | Verify OIDC login | Trigger `deploy-azure.yml` manually with `workflow_dispatch`, observe build job step "Azure Login (OIDC)" | Validation step |

**Manual steps required**: Steps 1.1-1.4 cannot be automated via Bicep. They require either `az ad` CLI commands or the Microsoft Graph API. A bootstrap script should be created at `infra/azure/scripts/bootstrap-oidc.sh`.

### Phase 2: Registry (ACR)

| Step | Action | Command / Tool | Blocking? |
|---|---|---|---|
| 2.1 | Verify `cripaidev.azurecr.io` is accessible | `az acr show --name cripaidev --query loginServer` | Validation only |
| 2.2 | Verify AcrPush works for CI SP | `az acr login --name cripaidev` using SP credentials | Validation only |
| 2.3 | Verify ACA managed identity has AcrPull on `cripaidev` | `az role assignment list --assignee <aca-mi-object-id> --scope <acr-id>` | If missing, ACA cannot pull images |
| 2.4 | Grant AcrPull to ACA managed identity if missing | `az role assignment create --assignee <aca-mi-principal-id> --role AcrPull --scope <acr-id>` | YES if ACA uses MI-based pull |

**Decision needed**: The workflow pushes to `cripaidev.azurecr.io/ipai-odoo:<sha>`, but `aca-odoo-services.bicep` references `containerRegistryServer` as a parameter with MI-based auth. The ACA app itself needs an identity with AcrPull. Confirm which managed identity (`id-ipai-aca-dev` in `rg-ipai-agents-dev` or a different one in `rg-ipai-dev`) is assigned to the Deployment B container apps.

### Phase 3: Compute (ACA Environment + App Wiring)

| Step | Action | Command / Tool | Blocking? |
|---|---|---|---|
| 3.1 | Verify ACA environment health | `az containerapp env show --name ipai-odoo-dev-env --resource-group rg-ipai-dev` | Validation |
| 3.2 | Verify `ipai-odoo-dev-web` current image | `az containerapp show --name ipai-odoo-dev-web --resource-group rg-ipai-dev --query properties.template.containers[0].image` | Validation |
| 3.3 | Verify ACA registry configuration | `az containerapp show --name ipai-odoo-dev-web --resource-group rg-ipai-dev --query properties.configuration.registries` | **IMPORTANT** -- confirms whether username/password or MI auth is configured |
| 3.4 | Test `az containerapp update` with current image | Dry run: `az containerapp update --name ipai-odoo-dev-web --resource-group rg-ipai-dev --image <current-image>` | Validation of RBAC |
| 3.5 | Seed KV secrets: `pg-odoo-user`, `pg-odoo-password` | `az keyvault secret set --vault-name ipai-odoo-dev-kv --name pg-odoo-user --value <value>` | YES -- ACA env vars reference these |
| 3.6 | Verify PG connectivity from ACA | Check ACA logs for DB connection errors | Validation |

### Phase 4: Edge (Front Door)

| Step | Action | Command / Tool | Blocking? |
|---|---|---|---|
| 4.1 | Verify Front Door endpoint | `az afd endpoint show --profile-name ipai-fd-dev --resource-group rg-ipai-shared-dev --endpoint-name <name>` | Validation |
| 4.2 | Verify origin group points to `ipai-odoo-dev-web` (Deployment B) | `az afd origin-group list --profile-name ipai-fd-dev --resource-group rg-ipai-shared-dev` | **IMPORTANT** -- may still point to Deployment A |
| 4.3 | Verify custom domain `erp.insightpulseai.com` binding | `az afd custom-domain list --profile-name ipai-fd-dev --resource-group rg-ipai-shared-dev` | Validation |
| 4.4 | Verify TLS certificate status | Check `validationState` and `provisioningState` of custom domain | Must be `Approved` + `Succeeded` |
| 4.5 | Update origin if needed | Point to Deployment B ACA environment FQDN | May require Bicep redeployment |

### Phase 5: Wire (Secrets, DNS, Health Checks)

| Step | Action | Command / Tool | Blocking? |
|---|---|---|---|
| 5.1 | Verify Cloudflare DNS for `erp.insightpulseai.com` | `dig erp.insightpulseai.com CNAME` | Must point to Front Door |
| 5.2 | Seed remaining KV secrets (Zoho SMTP) | `az keyvault secret set` for `zoho-smtp-user`, `zoho-smtp-password` | Non-blocking for deploy, blocking for mail |
| 5.3 | End-to-end health check | `curl -sL -o /dev/null -w "%{http_code}" https://erp.insightpulseai.com/web/health` | Validation |
| 5.4 | Trigger full deploy-azure.yml workflow | `gh workflow run deploy-azure.yml -f environment=dev` | Final validation |
| 5.5 | Verify deployment summary job output | Check GitHub Actions run for all 4 stages passing | Acceptance gate |

---

## 7. Risk Summary

| Risk | Severity | Mitigation |
|---|---|---|
| No OIDC federation exists -- workflow cannot authenticate | **P0 / CRITICAL** | Phase 1 must complete before any CI/CD works |
| Two competing Odoo deployments (A and B) cause confusion | **P1 / HIGH** | Resolve which deployment is canonical. Resources.yaml documents both. |
| Front Door origin may point to wrong ACA environment | **P1 / HIGH** | Verify in Phase 4.2. Update origin group if needed. |
| KV secrets not seeded -- ACA apps cannot connect to PG | **P1 / HIGH** | Phase 3.5 -- manual secret seeding required |
| Two ACR registries (`cripaidev` shared + `ipaiodoodevacr` Odoo-specific) | **P2 / MEDIUM** | Decide which ACR to use. Workflow defaults to `cripaidev`. |
| `register-providers.sh` missing critical providers | **P2 / MEDIUM** | Add `Microsoft.App`, `Microsoft.ContainerRegistry`, `Microsoft.KeyVault`, `Microsoft.Cdn`, `Microsoft.DBforPostgreSQL` |
| No IaC for OIDC/RBAC setup | **P2 / MEDIUM** | Create `infra/azure/scripts/bootstrap-oidc.sh` |
| `container-apps.bicep` uses username/password auth but `aca-odoo-services.bicep` uses MI auth | **P2 / MEDIUM** | Standardize on MI auth. Verify which module was used to deploy the actual resources. |

---

## 8. Recommended File Changes

| File | Action | Purpose |
|---|---|---|
| `infra/azure/scripts/bootstrap-oidc.sh` | **CREATE** | Script to create Entra ID app reg, SP, federated credential, RBAC assignments |
| `infra/azure/scripts/register-providers.sh` | **UPDATE** | Add missing providers: `Microsoft.App`, `Microsoft.ContainerRegistry`, `Microsoft.KeyVault`, `Microsoft.Cdn`, `Microsoft.DBforPostgreSQL` |
| `infra/azure/scripts/seed-keyvault.sh` | **CREATE** | Script to seed required KV secrets (prompts for values, never logs them) |
| `infra/azure/scripts/verify-deploy-prereqs.sh` | **CREATE** | Pre-flight check: validates all Phase 1-5 prerequisites before running deploy-azure.yml |
| `.github/workflows/deploy-azure.yml` | **UPDATE** | Add pre-flight job that checks `az account show` and ACR access before build |
| `docs/audits/AZURE_BOOTSTRAP_GAP_PLAN.md` | **CREATE** | This document |

---

## 9. Estimated Cost Impact

All resources that need to be created in Phase 1 (Entra ID app registration, service principal, federated credentials, RBAC role assignments) are **zero-cost**. No new billable Azure resources are required to unblock the CI/CD pipeline.

The existing infrastructure (ACR Basic, ACA Consumption, PG Flexible Burstable B1ms, Front Door Premium) is already provisioned and billing. The bootstrap work only wires the CI/CD pipeline to these existing resources.

---

## 10. Decision Log (Requires Human Input)

| # | Decision | Options | Impact |
|---|---|---|---|
| D1 | Which Odoo deployment is canonical? | A (`rg-ipai-agents-dev`) or B (`rg-ipai-dev`) | Determines Front Door origin, KV secrets, and workflow targets |
| D2 | Which ACR should CI push to? | `cripaidev` (shared) or `ipaiodoodevacr` (Odoo-specific) | Affects workflow ACR_REGISTRY var and ACA pull config |
| D3 | Should the workflow build custom images or use stock Odoo? | Custom (Dockerfile.unified) or `docker.io/library/odoo:18.0` | `odoo-runtime.bicep` uses stock image; `deploy-azure.yml` builds custom |
| D4 | Who creates the Entra ID app registration? | Platform admin via CLI or request via Azure portal | Requires Global Admin or Application Admin role |

---

*Generated: 2026-03-14 by gap audit. No resources provisioned.*
