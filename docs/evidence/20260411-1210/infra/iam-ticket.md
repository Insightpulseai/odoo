# Azure IAM Remediation — Security Remediation Ticket

> **Severity**: P0/P1 governance finding  
> **Observed**: 2026-04-11  
> **SSOT**: [`ssot/governance/azure-rbac-remediation.yaml`](../../ssot/governance/azure-rbac-remediation.yaml)  
> **Gate**: `PULSER-IAM-GATE-01` — blocks Pulser production-ready claim  
> **Owner**: Platform Admin (IAM)

---

## Summary

Azure portal issued an explicit elevated-access warning for the production subscription. This is an IAM / least-privilege violation against the platform's own target operating model.

**This is not a terms violation. It is a governance gap that must be closed before Pulser can claim production readiness.**

---

## Findings

### P0 — Fix immediately

| ID | Principal | Role | Scope | Issue |
|----|-----------|------|-------|-------|
| IAM-P0-01 | Platform Admin | User Access Administrator | **Root (Inherited)** | Root-scope permanent UAA. Azure explicitly warns to remove. Highest-risk finding. |
| IAM-P0-02 | Unknown (×2) | Owner | Subscription | Orphaned/unresolved principals with Owner. Uncontrolled privilege escalation path. |
| IAM-P0-03 | Jake Tolentino | Owner | Subscription | Appears twice as Owner. Duplicate direct + group-inherited assignment. |

### P1 — Fix before production promotion

| ID | Principal | Role | Issue |
|----|-----------|------|-------|
| IAM-P1-01 | 7 principals total | Owner | Too many permanent Owner paths. Target ≤ 2 (break-glass + PIM group). |
| IAM-P1-02 | DevOps Service | Owner | Service principal should be Contributor scoped to deployment RGs, not subscription Owner. |
| IAM-P1-03 | Platform Admin | Owner + Contributor + Azure AI User | Owner encompasses Contributor — redundant stacking. |
| IAM-P1-04 | Jake Tolentino | Owner + Azure AI User | Owner already covers Azure AI User — redundant. |

### P2 — Fix before Gate D

| ID | Finding |
|----|---------|
| IAM-P2-01 | Verify no classic administrator assignments remain (retired 2024-08-31). |
| IAM-P2-02 | Verify DevOps Automation Contributor is scoped to resource-group, not subscription. |

---

## Target Azure RBAC Matrix

### Subscription-level Owner paths (target: exactly 2)

| Principal | Type | Assignment | Notes |
|-----------|------|-----------|-------|
| `ipai-platform-admins` (Entra group) | Human admin group | PIM eligible, time-bound (max 4h), approval-required | Primary admin elevation path |
| `break-glass-admin` | Dedicated emergency account | Active Permanent | Credentials in Key Vault. Monitored by alert. Documented in break-glass runbook. |

### Service principal RBAC (target state)

| Principal | Role | Scope | Rationale |
|-----------|------|-------|-----------|
| DevOps Service | Contributor | RG-level (deployment RGs only) | CI/CD — no role assignment rights needed |
| Azure DevOps Automation | Contributor | RG-level (deployment RGs only) | Pipeline — restrict to deployment scope |
| Odoo Runtime (MI) | Reader + data-plane roles | `rg-ipai-odoo-prod` | Runtime only — no management plane |
| Pulser Agent Runtime (MI) | Cognitive Services User + AI Foundry Reader | `rg-ipai-ai-prod` | Agent invoke only — no management |

### Human user RBAC (target state)

| Principal | Role | Path | Notes |
|-----------|------|------|-------|
| Jake Tolentino | Owner (PIM eligible) | Via `ipai-platform-admins` group only | No direct subscription Owner assignment |
| Developers | Azure AI User | `rg-ipai-ai-prod` only | Scoped to AI RG — not subscription-inherited |

### Eliminated (must not exist)

- ❌ Root-scope User Access Administrator (any principal)
- ❌ Unknown/orphaned principals at any scope
- ❌ Duplicate direct Owner for any principal already in admin group
- ❌ Service principals with permanent subscription-level Owner
- ❌ Redundant role stacking (Owner + Contributor on same principal)
- ❌ Classic administrator assignments

---

## Remediation Steps

### Step 1 — Audit current state

```bash
# Full role assignment inventory
az role assignment list --all --include-inherited \
  --query '[].{principal:principalName,role:roleDefinitionName,scope:scope,type:principalType}' \
  --output table

# Find orphaned principals (Unknown in portal)
az role assignment list --all \
  --query '[?principalName==null || principalName==``].{id:id,role:roleDefinitionName,principalId:principalId,scope:scope}' \
  --output table

# Find root-scope assignments
az role assignment list --all \
  --query '[?scope=="/"].{principal:principalName,role:roleDefinitionName}' \
  --output table
```

### Step 2 — Remove P0 findings

```bash
# A. Remove root-scope User Access Administrator
az role assignment delete \
  --assignee <platform-admin-object-id> \
  --role "User Access Administrator" \
  --scope "/"

# B. Remove unknown/orphaned Owner principals (use IDs from audit)
az role assignment delete --ids <ASSIGNMENT_ID_1> <ASSIGNMENT_ID_2>

# C. Remove duplicate Owner for Jake Tolentino (keep group-inherited, remove direct)
az role assignment delete \
  --assignee <jake-tolentino-object-id> \
  --role "Owner" \
  --scope /subscriptions/<SUBSCRIPTION_ID>
```

### Step 3 — Fix P1 findings

```bash
# A. Reduce DevOps Service from Owner to Contributor at RG scope
az role assignment delete --assignee <devops-service-sp-id> --role "Owner" \
  --scope /subscriptions/<SUB_ID>
az role assignment create --assignee <devops-service-sp-id> --role "Contributor" \
  --scope /subscriptions/<SUB_ID>/resourceGroups/rg-ipai-deploy-prod

# B. Remove redundant Contributor where Owner already exists (Platform Admin)
az role assignment delete --assignee <platform-admin-id> --role "Contributor" \
  --scope /subscriptions/<SUB_ID>

# C. Remove redundant Azure AI User for Jake Tolentino (Owner covers it)
az role assignment delete --assignee <jake-tolentino-object-id> \
  --role "Azure AI User" --scope /subscriptions/<SUB_ID>
```

### Step 4 — Enable PIM for admin group

1. In Entra ID → Privileged Identity Management → Azure Resources
2. Scope to production subscription
3. Add `ipai-platform-admins` group as **Eligible** for Owner
4. Set max activation duration: 4 hours
5. Require approval for activation
6. Configure alert on activation

### Step 5 — Verify and document

```bash
# Verify clean state
az role assignment list --all --include-inherited \
  --query '[?roleDefinitionName==`Owner`].{principal:principalName,scope:scope,type:principalType}' \
  --output table

# Verify no root-scope
az role assignment list --all \
  --query '[?scope=="/"]' --output table
# Expected: empty
```

---

## Release Gate — `PULSER-IAM-GATE-01`

> **Pulser may not claim production-ready status until all pass criteria are met.**

| Criteria | Status |
|----------|--------|
| No root-scope privileged assignments | ❌ OPEN |
| Zero unknown/orphaned principals at subscription scope | ❌ OPEN |
| Owner count ≤ 2 paths (break-glass + PIM group) | ❌ OPEN |
| No service principal with permanent subscription-level Owner | ❌ OPEN |
| No duplicate role assignments for same principal | ❌ OPEN |
| No classic administrator assignments | ⚠️ UNVERIFIED |
| PIM enabled for admin group Owner elevation | ❌ OPEN |
| Break-glass account documented and monitored | ❌ OPEN |

Evidence location: `docs/evidence/azure-iam-remediation/`

---

## Resource Group — Target RBAC (per RG)

### `rg-ipai-odoo-prod` (or dev equivalent)

| Principal | Target role | Rationale |
|-----------|-------------|-----------|
| Deployment automation SP | Contributor | Deploy ACA, revisions, env-bound resources |
| Odoo Runtime (managed identity) | Specific data-plane roles only | No broad RG Owner — narrow to actual runtime access |
| Human operators | Contributor (eligible/time-bound) | Prefer group-based elevation — not standing |

### `rg-ipai-data-prod` (DB / storage)

| Principal | Target role | Rationale |
|-----------|-------------|-----------|
| DB/platform ops group | Contributor or narrow DB admin path | Manage Postgres and storage infra |
| App/runtime identities | Resource-specific roles only | No broad RG Owner |
| Deployment automation SP | Contributor only if deployment touches this RG | Otherwise no access |

### `rg-ipai-shared-prod` (Key Vault, shared platform)

| Principal | Target role | Rationale |
|-----------|-------------|-----------|
| Platform admin group | Contributor | Key Vault, shared platform resources |
| App identities | Key Vault Secrets User / specific roles | Least privilege — no Contributor required |
| Automation SP | Contributor only if deploying here | Narrow to actual target RG |

### `rg-ipai-ai-prod` (Foundry / AI Search / OpenAI)

| Principal | Target role | Rationale |
|-----------|-------------|-----------|
| AI platform group | Contributor | Manage Foundry/OpenAI/Search resources |
| Pulser Agent Runtime (managed identity) | Cognitive Services User + AI Foundry Reader | Narrow runtime invoke — no management plane |
| Automation SP | Contributor if needed | No Owner |

---

## Service-Level Guidance

| Service / area | Recommended access pattern |
|----------------|---------------------------|
| Azure OpenAI / Foundry | Runtime identities: model/invoke roles only (`Cognitive Services User`) |
| Azure AI Search | `Search Index Data Reader` or `Search Index Data Contributor` — not subscription Owner |
| PostgreSQL | Azure DB roles + narrow infra roles separately; avoid broad Owner on data RG |
| Key Vault | `Key Vault Secrets User` for read; `Key Vault Secrets Officer` for admin; never Owner |
| Container Apps | `Container Apps Contributor` or deploy-scoped Contributor; not subscription Owner |
| Defender managed identities | Leave system-managed roles untouched; document them in the inventory |

---

*Last updated: 2026-04-11*
