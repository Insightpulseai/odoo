# Entra Governance Baseline

> Microsoft Entra ID is the canonical identity and access control plane for the InsightPulseAI platform.
> This is a P0 control-plane dependency, not an optional identity add-on.
> Updated: 2026-03-25

---

## Identity / Governance Authority

Microsoft Entra ID is responsible for:

- User lifecycle and enterprise user management
- Group-based access management
- Dynamic group membership rules
- Group-based licensing
- Delegated administration / role delegation
- Domain and tenant configuration governance
- Guest-user and external collaboration restrictions
- Assistive governance surfaces such as Security Copilot

### Design Rule

- **Odoo** remains the transactional system for business operations
- **Entra** remains the identity, access, tenant, and governance authority surface
- **Foundry agents and Copilot experiences** must inherit their enterprise access posture from Entra rather than implementing parallel identity logic

---

## Required Entra Governance Controls

Minimum target controls for production readiness:

### 1. Group-based access model

- Prefer security groups / Microsoft 365 groups over direct per-user assignment where possible
- Use dynamic groups where stable user attributes can drive access or licensing

### 2. Group hygiene

- Enforce naming policy for user-created Microsoft 365 groups
- Enable group expiration where appropriate
- Require at least two owners for managed groups

### 3. License governance

- Use group-based licensing as the default assignment model when the feature/license tier permits it
- Treat Microsoft 365 admin center as the primary UI surface for license assignment workflows

### 4. Privilege minimization

- Avoid broad Global Administrator usage
- Use delegated/admin roles with least privilege
- Treat owner permissions and default member permissions as governance scope, not harmless defaults

### 5. Guest and external collaboration governance

- Explicitly configure guest-user access restrictions
- Explicitly govern invitation rights and external collaboration behavior

### 6. Admin assist lane

- Security Copilot in Entra is an assistive governance surface, not a replacement for RBAC, PIM, or policy
- Security Copilot actions are permission-bound — they operate within the admin's eligible-role boundaries

---

## Operational Note: License Assignment UI

Do not assume license assignment remains centered in the Entra admin UX.

Starting September 1, 2024, the Entra admin center and Azure portal no longer support license assignment through their user interfaces. Operational runbooks must treat the **Microsoft 365 admin center** as the primary UI for license assignment. API and PowerShell automation remain supported.

---

## Platform Integration Model

| Concern | Authority | Notes |
|---------|-----------|-------|
| User identity / SSO | Entra | OAuth2 to Odoo via `auth_oauth` |
| Business permissions | Odoo | Groups, record rules, finance permissions |
| Group-based access | Entra | Security groups / M365 groups |
| Licensing | Entra (M365 admin center) | Group-based licensing preferred |
| Agent identity | Entra managed identity | Foundry agents use MI, not service accounts |
| Guest access | Entra | Restricted by tenant policy |
| Admin delegation | Entra | Least-privilege roles, not Global Admin |
| Admin assistance | Security Copilot | Assistive only, permission-bound |

---

## What This Means for the Stack

### Odoo
- Odoo users authenticate via Entra OAuth (redirect URI: `/auth_oauth/signin`)
- Odoo owns its own groups, record rules, and business permissions
- Odoo does NOT duplicate Entra identity governance

### Foundry / Pulser
- Foundry agents inherit access posture from Entra managed identities
- Agents do NOT implement parallel identity logic
- Tool exposure is scoped per `platform/ssot/tool_contracts.yaml`

### Security Copilot
- Assistive governance surface inside Entra
- Does NOT replace RBAC, PIM, or conditional access policy
- Portal browsing restrictions are NOT a sufficient security boundary

---

*This document extends `AZURE_NATIVE_TARGET_STATE.md` and `PUBLIC_TO_ODOO_INTEGRATION_FLOW.md` for the identity/governance plane.*
