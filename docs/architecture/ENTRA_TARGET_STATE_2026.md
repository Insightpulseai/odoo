# Microsoft Entra ID — Target State 2026

> **Status**: Approved
> **Date**: 2026-03-23
> **SSOT**: `ssot/identity/entra_target_state.yaml`

---

## One-Line Target

Cloud-only Entra tenant, root custom domain only, P1 minimum, Security Defaults now → Conditional Access next, managed-identity-first workload auth, Domain Services = zero, Verified ID = zero.

---

## Current State

| Item | Value |
|------|-------|
| Tenant | Default Directory |
| Primary domain | `insightpulseai.com` (verified) |
| Microsoft domain | `ceoinsightpulseai.onmicrosoft.com` |
| License | Entra ID Free |
| Users | 4 |
| Groups | 12 |
| Enterprise apps | 4 |
| App registrations | 6 |
| Devices | 0 |
| Domain Services | 0 |
| Auth baseline | Security Defaults |
| Legacy MFA/SSPR | Needs migration to modern policy |

---

## Target State

### Tenant & Domain

- **1** Entra tenant (keep)
- **1** verified custom domain: `insightpulseai.com` (keep)
- **1** default Microsoft domain: `ceoinsightpulseai.onmicrosoft.com` (keep)
- **0** additional Entra subdomains (do not add)

### Licensing

- **Minimum**: Entra ID P1 (unlocks Conditional Access)
- **Preferred**: Entra ID P2 (adds risk-based identity protection)

### Authentication

**Now (Free tier)**:
- Security Defaults enabled
- Modern auth methods policy: FIDO2, Authenticator, TAP, Software OATH, Email OTP
- Migrate off legacy MFA/SSPR policy (immediate cleanup)

**After P1**:
- Replace Security Defaults with 4 Conditional Access policies:
  1. Admins require MFA
  2. All users require strong auth
  3. Block legacy auth
  4. Secure MFA registration

### Users & Groups

- 4-8 human users (separate admin from daily-use)
- **2 emergency access accounts** (excluded from CA lockout)
- 8-15 role/entitlement groups (all app assignment group-based)

### Enterprise Applications (target: 4-6)

| App | Status |
|-----|--------|
| Databricks | Keep |
| GitHub system app | Keep |
| ipai-n8n-entra | Keep |
| Graph CLI | Keep |
| Odoo ERP SSO | Add if using Entra sign-in |
| Tableau Cloud | Keep/Add |

### App Registrations (target: 8)

| Registration | Purpose | Status |
|-------------|---------|--------|
| InsightPulse AI - Odoo ERP | Odoo SSO/API | Keep |
| InsightPulse AI - Tableau Cloud | Tableau | Keep |
| ipai-github-oidc | GitHub OIDC federation | Keep |
| ipai-n8n-entra | n8n auth | Keep |
| sp-ipai-azdevops | Azure DevOps | Keep |
| ipai-tableau-sso | Tableau SSO | Keep |
| **Diva Goals Web** | Browser sign-in (SPA) | **Add** |
| **Diva Goals API** | Protected API resource | **Add** |

### Managed Identities (target: 3)

| Identity | Scope | Purpose |
|----------|-------|---------|
| mi-web-runtime | ACA | Web apps → Key Vault, Search |
| mi-jobs-automation | Databricks, ACA Jobs | Scheduled jobs, pipelines |
| mi-data-agent | Foundry, Databricks | Agent/data services |

### Domain Services

**Target: 0.** No LDAP/Kerberos/NTLM dependency. Modern-auth only.

### Verified ID

**Target: 0 now.** Enable only for concrete credential use cases later.

---

## Immediate Actions

1. Migrate off legacy MFA/SSPR policy → modern auth methods policy
2. Create 2 emergency access accounts
3. Audit and clean group model (target 8-15 purpose-driven groups)
4. Plan Entra ID P1 procurement
5. Register Diva Goals Web + API app registrations

## After P1

6. Disable Security Defaults
7. Enable 4 Conditional Access policies
8. Assign enterprise apps via groups only
9. Provision 3 managed identities for workloads

---

## What NOT to Do

- Do not add Entra subdomains without a real UPN namespace need
- Do not provision Domain Services for modern-auth workloads
- Do not use long-lived client secrets when MI/OIDC/federation is available
- Do not assign apps directly to users (use groups)
- Do not skip emergency access accounts
