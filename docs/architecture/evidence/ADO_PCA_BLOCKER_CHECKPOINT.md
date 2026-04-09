# ADO PCA Blocker Checkpoint

> **Date**: 2026-03-23
> **Status**: Authority gate — awaiting ceo@ action
> **SSOT**: `ssot/governance/ado_entra_subscription_identity.yaml` (blocker `ado-pca-001`)

---

## Confirmed Facts

| Fact | Evidence |
|------|----------|
| ADO org connected to Entra tenant `402de71a` | `/userentitlements` API: all users show `origin=aad` |
| ceo@ is Entra external guest, not MSA | `directoryAlias=ceo_insightpulseai.com#EXT#`, `origin=aad` |
| admin@ is in Project Administrators only | Graph memberships API: 1 group (PA descriptor) |
| ceo@ is in Project Collection Administrators | Graph memberships API: 3 groups including PCA descriptor |
| App A (Odoo Login) registered and secret in KV | `kv-ipai-dev/odoo-entra-oauth-client-secret` |
| App B (ADO Automation) graph-registered in ADO | Graph servicePrincipals API: `subjectKind=servicePrincipal`, `origin=aad` |
| App B entitlement NOT granted | serviceprincipalentitlements API: count=0 |

## Disproven Assumptions

| Previous claim | Actual |
|---|---|
| ADO org not connected to Entra | Connected (all users origin=aad) |
| ceo@ is MSA (ceo0670) | Entra external guest (#EXT#) |
| admin@ has org-level authority | Project Admin only, not PCA |
| Self-elevation to PCA via API works | API call accepted but membership did not persist |

## Remaining Blocker

**`ado-pca-001`**: `admin@` is not in Project Collection Administrators.

- **Owner**: `ceo@insightpulseai.com`
- **Type**: Authority/privilege gate
- **Impact**: Cannot add service principals to ADO org, cannot manage user entitlements

### Required Action

`ceo@` must navigate to:

```
Azure DevOps → Organization Settings → Permissions
  → Project Collection Administrators → Members → Add
  → Search: admin@insightpulseai.com → Add
```

## Success Conditions

1. `admin@` appears as effective PCA member (verify via Graph memberships API — should show PCA descriptor)
2. App B SP entitlement granted (Basic license, Contributors in ipai-platform)
3. WIF pipeline runs end-to-end: ADO → Entra token → Azure RM → Key Vault
4. SSOT flipped from `blocked_on_pca` to `validated`

## Post-Unblock Sequence

```
ceo@ adds admin@ to PCA
  → admin@ re-authenticates (fresh token with PCA claims)
  → POST /serviceprincipalentitlements (App B SP, Basic, Contributors)
  → Create/verify WIF service connections (dev, staging, prod)
  → Run validation pipeline
  → Capture evidence
  → Update SSOT: workstream_status.* → complete/validated
```
