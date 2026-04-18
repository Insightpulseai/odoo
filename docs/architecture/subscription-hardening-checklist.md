# Subscription Hardening Checklist

> Azure Sponsorship `eba824fb` — InsightPulse AI
> Derived from subscription governance review, 2026-04-18
> SSOT: `ssot/azure/cloud-plane-map.yaml`

---

## Doctrine

```
Subscription = outer governance shell
Resource groups = workload boundaries
Resources = actual platform components
Deployments = executable truth evidence
IAM + Policy = control surface
Quotas + Providers = deployment readiness
```

The subscription page governs the estate. The application architecture lives underneath in resource groups, ACA, PostgreSQL, Foundry, Databricks, Key Vault, and Monitor.

---

## Hardening Order

### 1. Freeze Workload Boundaries

**Check:** Resource groups → Resources

| Resource Group | Purpose | Status |
|---------------|---------|--------|
| `rg-ipai-dev-odoo-sea` | Transaction plane (ACA + Container Apps) | Active |
| `rg-ipai-dev-ai-sea` | Intelligence plane (Foundry, Databricks, AI Search, Doc Intel) | Active |
| `rg-ipai-data-sea` | Data plane (PostgreSQL) | Active |
| `rg-ipai-dev-data-sea` | Lakehouse storage (6 storage accounts) | Active |
| `rg-ipai-dev-security-sea` | Security (Key Vault, MIs, Backup Vault, Purview) | Active |
| `rg-ipai-dev-net-sea` | Networking (VNet, PEs, Private DNS, DNS Zones) | Active |
| `rg-ipai-dev-mon-sea` | Observability (3 App Insights, 4 Log Analytics) | Active |
| `rg-ipai-dev-realtime` | Realtime (Redis, SignalR, Comms Services) | Active |
| `rg-ipai-shared` | Shared (Container Registry) | Active |
| `rg-ipai-dev-dbw-managed` | Databricks managed (do not modify) | System |
| `managed-rg-pv-ipai-dev-sea` | Purview managed (do not modify) | System |
| `NetworkWatcherRG` | Azure default | System |

- [ ] Verify all 12 RGs match expected-estate YAML
- [ ] Confirm no orphan RGs exist
- [ ] Confirm no resources outside canonical RGs

---

### 2. Validate Resource Providers

**Check:** Subscription → Resource providers

Required registrations:

| Provider | Purpose |
|----------|---------|
| `Microsoft.App` | Container Apps |
| `Microsoft.ContainerRegistry` | ACR |
| `Microsoft.CognitiveServices` | AI Foundry, Doc Intelligence |
| `Microsoft.DBforPostgreSQL` | PostgreSQL Flexible Server |
| `Microsoft.Databricks` | Databricks workspace |
| `Microsoft.Network` | VNet, PE, DNS, NSG, Front Door |
| `Microsoft.Insights` | App Insights |
| `Microsoft.OperationalInsights` | Log Analytics |
| `Microsoft.ManagedIdentity` | Managed identities |
| `Microsoft.KeyVault` | Key Vault |
| `Microsoft.Storage` | Storage accounts |
| `Microsoft.Cache` | Redis |
| `Microsoft.SignalRService` | SignalR |
| `Microsoft.Communication` | Communication Services |
| `Microsoft.Search` | AI Search |
| `Microsoft.Purview` | Purview |
| `Microsoft.RecoveryServices` | Backup Vault |
| `Microsoft.EventHub` | Event Hubs (Purview managed) |

- [ ] Run: `az provider list --query "[?registrationState=='Registered'].namespace" -o tsv`
- [ ] Confirm all required providers are registered
- [ ] Flag any unexpected registrations

---

### 3. Confirm Quota Headroom

**Check:** Subscription → Usage + quotas

Focus areas:

| Service | What to check |
|---------|--------------|
| Container Apps | Max environments, max apps per environment |
| Azure OpenAI / Cognitive Services | TPM limits per model deployment |
| PostgreSQL | vCores, storage limits |
| Networking | Public IPs, VNet peerings, Private Endpoints |
| Storage | Account count limit per subscription |

- [ ] Run: `az quota list --scope /subscriptions/eba824fb-332d-4623-9dfb-2c9f7ee83f4e`
- [ ] Confirm no services near limit (>80% consumed)
- [ ] Document any quota increase requests needed

---

### 4. Lock Down Access (IAM)

**Check:** Subscription → Access control (IAM)

| Principle | Rule |
|-----------|------|
| Owners | Minimal (1-2 human principals) |
| Contributors | Named, justified |
| Managed identities | Per-plane (5 exist: platform, agent, data, runtime, pipeline) |
| No broad Contributor sprawl | Each assignment has documented purpose |
| Service principals | Minimal, scoped to resource group |

- [ ] Run: `az role assignment list --scope /subscriptions/eba824fb-... --output table`
- [ ] Verify Owner count <= 2
- [ ] Verify no stale/orphan assignments
- [ ] Verify managed identities scoped to correct RGs
- [ ] Confirm pipeline identity (`id-ipai-dev-pipeline`) has minimal required roles

---

### 5. Add Policy and Tag Discipline

**Check:** Subscription → Policies + Tags
**SSOT:** `ssot/azure/tag-policy.yaml`

Mandatory tags (per tag policy):

| Tag | Allowed values |
|-----|---------------|
| `org` | `ipai` |
| `platform` | `pulser-odoo` |
| `env` | `dev`, `stg`, `prod`, `shared` |
| `plane` | `transaction`, `data`, `agent`, `delivery`, `observability`, `security`, `shared` |
| `workload` | `odoo`, `finance`, `finance-agents`, `project-ops`, `prismalab`, `dbw`, `monitoring` |
| `service` | free-text slug |
| `owner` | `jake` |
| `managed_by` | `terraform`, `bicep`, `manual`, `azure-system` |
| `criticality` | `low`, `medium`, `high`, `mission-critical` |
| `cost_center` | `ipai-platform` |
| `data_classification` | `public`, `internal`, `confidential`, `restricted` |
| `dr_tier` | `none`, `bronze`, `silver`, `gold` |
| `backup_policy` | `none`, `daily`, `pitr`, `custom` |
| `ops_state` | `active`, `pilot`, `deprecated`, `candidate-delete` |
| `billing_scope` | `core-platform`, `benchmark`, `experimentation`, `shared` |

- [ ] Run: `az tag list --resource-id /subscriptions/eba824fb-...`
- [ ] Audit tag compliance across RGs
- [ ] Deploy policy definitions (Deny if missing mandatory tags)
- [ ] Deploy audit policy (flag drift from allowed values)

---

### 6. Protect Critical Resources

**Check:** Subscription → Resource locks

Lock candidates (CanNotDelete):

| Resource | Type | Priority |
|----------|------|----------|
| `insightpulseai.com` | DNS Zone | Critical |
| `kv-ipai-dev-sea` | Key Vault | Critical |
| `pg-ipai-odoo` | PostgreSQL | Critical |
| `vnet-ipai-dev-sea` | Virtual Network | High |
| `acripaiodoo` | Container Registry | High |
| `log-ipai-dev-sea` | Log Analytics (primary) | Medium |
| `appi-ipai-dev` | App Insights (primary) | Medium |

- [ ] Run: `az lock list --resource-group <rg> --output table` for each critical RG
- [ ] Apply CanNotDelete locks to all Critical/High resources
- [ ] Document locks in `ssot/azure/resource-locks.yaml`

---

### 7. Treat Deployments as Evidence

**Check:** Subscription → Deployments + Activity log

| Goal | How |
|------|-----|
| Prove IaC-created state | Check deployment history for ARM/Bicep deployments |
| Detect portal-only drift | Compare deployments vs activity log for manual changes |
| Audit trail | Activity log for who-changed-what |

- [ ] Run: `az deployment sub list --query "[].{name:name, timestamp:timestamp, state:properties.provisioningState}" -o table`
- [ ] Check for recent manual changes: `az monitor activity-log list --start-time 2026-04-01 --query "[?authorization.action!='']"`
- [ ] Flag any portal-only resource creation (no corresponding IaC)

---

### 8. Defender Decision

**Current:** Not enabled (per subscription baseline YAML)

| Option | Impact | Cost |
|--------|--------|------|
| **Enable Defender CSPM (free tier)** | Secure Score, basic recommendations | Free |
| **Enable Defender for Cloud (paid)** | Advanced threat protection, JIT, adaptive controls | ~$15/server/mo |
| **Document deferral** | Accept risk, revisit at prod readiness | Free |

- [ ] Decision: enable / defer (document either way)
- [ ] If enabling: `az security pricing create --name VirtualMachines --tier Standard`
- [ ] Update `ssot/azure/subscription-baseline.yaml` with decision

---

## Evidence Trail

After completing each step, record evidence:

```
docs/evidence/20260418/subscription-hardening/
  ├── iam-role-assignments.txt
  ├── resource-providers.txt
  ├── quota-usage.txt
  ├── tag-compliance-audit.txt
  ├── resource-locks.txt
  └── deployment-history.txt
```

---

## Canonical Cloud Plane Map

```
Entra      → identity and access
Azure      → runtime and infrastructure
AI Foundry → agents and model runtime
DevOps     → planning and governance
GitHub     → engineering execution
Fabric     → BI and semantic consumption
Purview    → data governance
Defender   → security posture
Databricks → governed intelligence
```

**Do not let the Microsoft Cloud menu tempt you into making every surface first-class.**

Not primary (do not adopt unless explicit decision):
- Copilot Studio (Pulser uses custom-engine orchestration)
- Data Explorer (Log Analytics sufficient at current scale)
- Power Platform (optional for internal tooling only)

---

*SSOT: `ssot/azure/cloud-plane-map.yaml` | Last updated: 2026-04-18*
