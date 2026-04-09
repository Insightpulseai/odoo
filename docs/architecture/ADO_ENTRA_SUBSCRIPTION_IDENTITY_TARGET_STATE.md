# ADO / Entra / Subscription Identity Link Chain — Target State

> **Status**: Approved
> **Date**: 2026-03-23
> **SSOT**: `ssot/governance/ado_entra_subscription_identity.yaml`

**Cross-references**:
- [Entra Target State](ENTRA_TARGET_STATE_2026.md)
- [ADO/GitHub Authority Map](ADO_GITHUB_AUTHORITY_MAP_2026.md)
- [Azure DevOps Operating Model](AZURE_DEVOPS_OPERATING_MODEL.md)
- `ssot/identity/entra_target_state.yaml`
- `ssot/azure/azure_devops.yaml`

---

## Current Gate

The target state is materially validated. The only remaining blocker is effective **Project Collection Administrators** membership for `admin@`, which is required to complete App B entitlement and full workload identity federation validation.

This is an **authority/privilege gate**, not an architecture or connectivity failure.

| Lane | Status |
|------|--------|
| ADO ↔ Entra linkage | **Complete** |
| Identity discovery | **Complete** (ceo@=Entra guest, not MSA) |
| App A (Odoo Login) | **Complete** (registered, secret in KV) |
| App B (ADO Automation) | **Graph registered**, entitlement blocked |
| KV secret storage | **Complete** |
| PCA authority | **Blocked** — requires ceo@ action |
| WIF pipeline validation | **Blocked** on PCA → SP entitlement |

**Sequence to close**: PCA elevation (ceo@) → SP entitlement → WIF validation → evidence → green.

---

## Current State (2026-03-23)

| Component | Value | Status |
|-----------|-------|--------|
| Entra tenant | `402de71a-87ec-4302-a609-fb76098d1da7` (Default Directory) | Active |
| Custom domain | `insightpulseai.com` (verified) | Active |
| Azure subscription | Bound to Entra tenant | Active |
| ADO organization | `dev.azure.com/insightpulseai` | Active |
| ADO ↔ Entra connection | **Connected** (verified 2026-03-23) | Active |
| ADO project | `ipai-platform` (`b4267980-f678-4fcb-b8b4-3d81d9153445`) | Active |
| Entra license | Free (P1 not yet procured) | Constraint |
| Managed identities | 0 of 3 provisioned | Partial |
| App A (Odoo Login) | `07bd9669` — registered, secret in KV | **Active** |
| App B (ADO Automation) | `ae2df138` — registered, SP pending ADO add | **Partial** |
| admin@ PCA membership | Not in Project Collection Administrators | **Blocker** |

---

## Identity Chain

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Identity Link Chain (Target)                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐   Link 1    ┌──────────────────┐                  │
│  │  Entra ID    │────────────→│ Azure Subscription│                  │
│  │  Tenant      │   (active)  │                  │                  │
│  └──────┬───────┘             └────────┬─────────┘                  │
│         │                              │                            │
│         │ Link 2                       │ Link 4                     │
│         │ (CONNECTED ✓)               │ (partial)                  │
│         ▼                              ▼                            │
│  ┌──────────────┐             ┌──────────────────┐                  │
│  │  ADO Org     │             │ Managed Identities│                  │
│  │  insightpulse│             │ mi-web-runtime    │                  │
│  └──────┬───────┘             │ mi-jobs-automation│                  │
│         │                     │ mi-data-agent     │                  │
│         │ Link 3              └──────────────────┘                  │
│         │ (active)                                                  │
│         ▼                                                           │
│  ┌──────────────┐                                                   │
│  │  ADO Project │                                                   │
│  │  ipai-platform│                                                  │
│  └──────────────┘                                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

| Link | From | To | Binding | Current | Target |
|------|------|----|---------|---------|--------|
| 1 | Entra tenant | Azure subscription | IAM role assignment | **Active** | Active |
| 2 | Entra tenant | ADO organization | Org Entra connection | **Connected** | Connected |
| 3 | ADO organization | ADO project | Project membership | **Active** | Active |
| 4 | Azure subscription | Managed identities | MI provisioning + RBAC | **Partial** | Active |

**Link 2 is now verified connected** (2026-03-23). The remaining gap is admin@ PCA elevation for org-level management operations.

---

## Principal Identity Resolution

| Principal | Type | Current Roles | ADO Groups | Resolution |
|-----------|------|---------------|------------|------------|
| `admin@insightpulseai.com` | Entra cloud-native | Subscription Owner, ADO Project Admin | Project Administrators | **Needs PCA elevation** |
| `ceo@insightpulseai.com` | Entra external guest (#EXT#) | ADO Org Owner | Project Collection Administrators | Retain — must add admin@ to PCA |
| `devops@insightpulseai.com` | Entra cloud-native | ADO Contributor | — | Retain |

### ceo@ Identity Resolution (ADR-IDC-003) — RESOLVED

Previously assumed to be MSA. **Verified 2026-03-23**: ceo@ is an Entra external guest (`origin=aad`, `directoryAlias=ceo_insightpulseai.com#EXT#`). No ownership transfer needed.

### admin@ PCA Elevation — PENDING

`admin@` is in **Project Administrators** only (project-level). `ceo@` is in **Project Collection Administrators** (org-level). Org-level operations (adding service principals, managing licenses) require PCA membership.

**Action**: `ceo@` must add `admin@` to PCA via Organization Settings → Permissions.

---

## Linking Sequence (6 Steps)

| Step | Name | Status | Dependencies | Success Criteria |
|------|------|--------|--------------|------------------|
| 1 | Resolve ceo@ identity | **Done** | — | ceo@ is Entra-backed (verified #EXT#) |
| 2 | Connect ADO org to Entra | **Done** | — | All users show origin=aad |
| 3 | Elevate admin@ to PCA + add SP | **Blocked** | ceo@ action | admin@ in PCA, SP `833163d3` in ADO |
| 4 | Configure WIF service connections | In progress | — | sc-ipai-{dev,staging,prod} active |
| 5 | Provision managed identities | Not started | Step 2 (done) | 3 MIs with RBAC assignments |
| 6 | Validate end-to-end chain | Blocked | Steps 3, 4, 5 | Pipeline authenticates via WIF to Azure |

### Dependency Graph

```
Step 1 ──→ Step 2 ──→ Step 3
                 │
                 ├──→ Step 5 ──┐
                 │              │
Step 4 (independent) ──────────├──→ Step 6
                               │
               Step 5 ─────────┘
```

**Step 4 is independent** — service connections can be created before Entra connection, but the full WIF trust chain requires Step 2.

---

## Service Connection Model

### Architecture

```
ADO Pipeline
    │
    ▼ (federated token request)
Entra ID ← InsightPulseAI Azure DevOps Automation (ae2df138)
    │
    ▼ (OIDC token with managed identity)
Azure Resource Manager
    │
    ▼ (RBAC)
Key Vault / ACA / Databricks / etc.
```

### Per-Environment Connections

| Connection | Environment | Scope | App Registration | Status |
|------------|-------------|-------|------------------|--------|
| `sc-ipai-dev` | dev | `rg-ipai-dev-*` | `InsightPulseAI Azure DevOps Automation` | Active |
| `sc-ipai-staging` | staging | `rg-ipai-shared-staging` | `InsightPulseAI Azure DevOps Automation` | Planned |
| `sc-ipai-prod` | prod | `rg-ipai-shared-prod` | `InsightPulseAI Azure DevOps Automation` | Planned |

All connections use **Workload Identity Federation** (WIF) — no long-lived client secrets.

Cross-ref: `ssot/identity/entra_target_state.yaml` → `app_registrations.keep` (sp-ipai-azdevops)

---

## Key Decisions

| ADR | Decision | Rationale |
|-----|----------|-----------|
| ADR-IDC-001 | Single ADO org (`insightpulseai`) | Simplifies Entra connection and billing |
| ADR-IDC-002 | WIF over client secrets | Eliminates rotation burden, reduces attack surface |
| ADR-IDC-003 | ceo@ identity type | **Resolved** — Entra external guest, not MSA |
| ADR-IDC-004 | No Domain Services | No LDAP/Kerberos/NTLM dependency in stack |
| ADR-IDC-005 | Single ADO project (`ipai-platform`) | Simplifies governance and area-path mapping |

---

## Success Criteria

- [x] ADO org connected to Entra tenant `402de71a` (verified 2026-03-23)
- [x] All ADO org members are Entra-backed (admin@=aad, ceo@=aad#EXT#)
- [x] ceo@ identity resolved (Entra external guest, not MSA)
- [x] App A (Odoo Login) registered, secret in Key Vault
- [x] App B (ADO Automation) registered, ADO API permission configured
- [ ] admin@ elevated to Project Collection Administrators (requires ceo@ action)
- [ ] App B service principal added to ADO org (requires PCA)
- [ ] WIF service connections active for dev, staging, prod
- [ ] 3 managed identities provisioned with correct RBAC
- [ ] Pipeline authenticates via WIF and accesses Azure without secrets
- [ ] No long-lived client secrets in any ADO service connection

---

## Cross-References

| Document | Purpose |
|----------|---------|
| `ssot/governance/ado_entra_subscription_identity.yaml` | Machine-readable SSOT (this doc's companion) |
| `ssot/identity/entra_target_state.yaml` | Entra tenant, users, groups, managed identities |
| `ssot/azure/azure_devops.yaml` | ADO project, pipelines, environments, service connections |
| `ssot/governance/ado_github_authority_map.yaml` | ADO project ↔ GitHub repo mapping |
| `ssot/governance/github-entra-target-state.yaml` | GitHub ↔ Entra SAML/SSO configuration |
| `docs/architecture/ENTRA_TARGET_STATE_2026.md` | Entra target state (human-readable) |
| `docs/architecture/ADO_GITHUB_AUTHORITY_MAP_2026.md` | ADO/GitHub authority map (human-readable) |
| `docs/architecture/AZURE_DEVOPS_OPERATING_MODEL.md` | DevOps operating model |
| `docs/architecture/AZDO_TARGET_PIPELINE_ARCHITECTURE.md` | Pipeline architecture target |

---

*Machine-readable version: `ssot/governance/ado_entra_subscription_identity.yaml`*
