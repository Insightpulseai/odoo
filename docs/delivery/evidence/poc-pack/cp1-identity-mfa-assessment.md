# CP-1: Identity & MFA Assessment Evidence

## Date
2026-03-19

## Scope
Assessment of Microsoft Entra identity readiness for Odoo go-live, focused on MFA availability, MFA enforcement, and evidence required to close CP-1.

## Current status
**Status: PARTIAL**

MFA-related authentication methods are enabled at the tenant level, but CP-1 is not yet complete because:
- MFA enforcement for privileged users is not yet evidenced through Conditional Access policy assignment.
- Per-user MFA enrollment for required admin accounts is not yet evidenced.
- The current artifact set does not yet prove that the required admin accounts are both enrolled and enforced.

## What is already in place
- Microsoft Authenticator is enabled.
- Software OATH tokens are enabled.
- Temporary Access Pass is available for bootstrap/recovery scenarios.
- Emergency/break-glass admin presence is established in the tenant.
- Tenant-level method availability means MFA can be used, but availability alone is not the same as enforcement or enrollment proof.

## What is still missing to close CP-1
1. **Conditional Access enforcement**
   - A Conditional Access policy must require MFA for the relevant privileged admin scope.
   - Report-only rollout is acceptable as a validation step, but CP-1 should only be marked DONE once enforcement and evidence are in place.

2. **Enrollment verification**
   - Required admin accounts must be shown as actually registered for MFA, not merely eligible.
   - Evidence must identify the target admin accounts and show their registration/enforcement status.

3. **Evidence artifact**
   - The go-live pack must include a final evidence artifact showing the admin MFA control is configured and the required admin identities are enrolled.

## Important control boundary note
User MFA and Conditional Access policies apply to **human user identities**.
Your ACA managed identities are **not governed the same way** as user MFA policy targets, and current Conditional Access for workload identities applies to eligible service principals rather than managed identities. Managed identities should instead be governed with least-privilege RBAC, scoped resource access, Key Vault controls, and monitoring.

## Recommended actions to close CP-1
1. Create or confirm a Conditional Access policy requiring MFA for the admin scope used for go-live administration.
2. Verify MFA registration for the required admin accounts.
3. Capture the final evidence artifact and link it into:
   - `ssot/delivery/go_live_plan.yaml`
   - `docs/delivery/GO_LIVE_ACCELERATION_PLAN.md`
   - `docs/delivery/evidence/poc-pack/`
4. Reassess CP-1 after enforcement and enrollment proof are attached.

## Go-live interpretation
CP-1 is no longer fully blocked because MFA capability exists, but it is **not yet done**.
Go-live should treat CP-1 as a remaining governance/control closure item until enforcement and enrollment evidence are attached.
