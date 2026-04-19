# Runbook — Power Platform Inventory, Notifications, Announcements

Canonical source: [`ssot/governance/power-platform-admin-surface.yaml`](../../ssot/governance/power-platform-admin-surface.yaml)

## Metadata

- **Owner**: platform-architecture + identity-ops
- **Last updated**: 2026-04-19
- **Preconditions**: IPAI tenant on commercial cloud (not GCC / DoD / 21Vianet); at least one named Power Platform Administrator
- **Postconditions**: three admin capabilities verified enabled; role assignments + programmatic access baseline recorded
- **Rollback**: revoke Power Platform Administrator role from newly assigned principals; disable programmatic connections if any were created

## Scope

Enable and verify the three Power Platform admin capabilities:

1. Power Platform inventory (GA)
2. Admin center notifications (preview)
3. Admin center announcements (preview)

## Role prerequisites

Assign one of the following to at least one operator (primary holder: Jake Tolentino):

- Power Platform Administrator
- Dynamics 365 Administrator
- Global Administrator (for notifications + announcements only; avoid using GA for daily ops)

Assignment follows [`ssot/identity/entra_target_state.yaml`](../../ssot/identity/entra_target_state.yaml). GA should not be the daily operator identity.

## Steps

- [ ] Confirm tenant is commercial cloud (not sovereign).
- [ ] Confirm at least one named Power Platform Administrator exists.
- [ ] Confirm MFA / Conditional Access allows admin access to `https://admin.powerplatform.microsoft.com`.
- [ ] Confirm no blocking CA policy on Azure Resource Manager for admin identities.
- [ ] Sign in to the Power Platform admin center: `https://admin.powerplatform.microsoft.com`.
- [ ] Navigate to **Resources** → **Inventory** and verify agents / apps / flows / environments / environment groups load.
- [ ] Verify dedicated views load: Copilot Studio, Power Apps, Power Automate.
- [ ] Open the 🔔 notifications pane; confirm access as Power Platform Administrator.
- [ ] Open the 📣 announcements pane; confirm access.
- [ ] Export inventory to Excel to verify the export capability.
- [ ] Record last-verified timestamp in [`power-platform-admin-surface.yaml`](../../ssot/governance/power-platform-admin-surface.yaml) under `enablement_state.last_verified`.

## Programmatic access (optional)

If tooling / automation is planned:

- [ ] Create a service principal or Managed Identity for Power Platform API calls.
- [ ] Grant minimum Power Platform admin scope; store the identity reference in `ssot/identity/` (no secrets committed).
- [ ] Register the principal with the Power Platform API endpoints required.
- [ ] If using **Power Platform for Admins V2** connector (Power Automate / Logic Apps), create a connection using Managed Identity.
- [ ] If using **Azure Resource Graph**, confirm the identity has `Reader` on relevant subscriptions.

> [!IMPORTANT]
> No hardcoded admin credentials. No long-lived secrets outside Key Vault. No interactive admin login in automation. See `ssot/governance/power-platform-admin-surface.yaml#programmatic_access`.

## Verification

- [ ] Inventory view loads within expected ~15-minute freshness window.
- [ ] Filter + sort work on key attributes (owner, region, environment).
- [ ] Resource count updates when a filter is applied.
- [ ] Export to Excel produces a file with expected columns.
- [ ] Notifications pane opens; at least one test notification scenario understood (info / warning / critical severities acknowledged by admin).
- [ ] Announcements pane opens with current product updates.

## Known limitations to acknowledge

- Classic chatbots are not in the new inventory page.
- UI search is limited to the first 1,000 loaded items — use programmatic access for larger sets.
- Some columns may be incomplete or misleading for certain resource types.
- Dismissed notifications are effectively removed (no undo).
- Notifications preview has no customization and no Teams delivery yet.

## Relationship to Microsoft 365 Message center

- M365 Message center remains the authoritative source for major planned changes, deprecations, and feature rollouts.
- Power Platform notifications are for **tenant-specific** operational / compliance / capacity issues.
- Both are consumed — they complement, they do not replace each other.

## Rollback

- [ ] Revoke Power Platform Administrator role from any principal granted only for this enablement.
- [ ] Delete any programmatic connections created under this runbook.
- [ ] Update `enablement_state` back to `to_be_verified` in the canonical SSOT.

## Related

- [Power Platform admin surface SSOT](../../ssot/governance/power-platform-admin-surface.yaml)
- [Power Platform capability map](../architecture/POWER_PLATFORM_CAPABILITY_MAP.md)
- [Entra target state](../../ssot/identity/entra_target_state.yaml)
- [Copilot release stages](../../ssot/governance/copilot_release_stages.yaml)
