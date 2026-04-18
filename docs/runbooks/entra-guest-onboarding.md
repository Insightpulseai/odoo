# Runbook — Entra B2B Guest Onboarding (TBWA\SMP Finance)

Canonical onboarding procedure for the 11 TBWA\SMP Finance guests defined in
[ssot/identity/guest-invite-registry.yaml](../../ssot/identity/guest-invite-registry.yaml).

This runbook is the ONLY approved procedure. Do not invite guests through
manual, one-off flows.

---

## Inputs

| Artifact | Path |
|---|---|
| Canonical guest list | [ssot/identity/guest-invite-registry.yaml](../../ssot/identity/guest-invite-registry.yaml) |
| Group model | [ssot/identity/guest-groups.yaml](../../ssot/identity/guest-groups.yaml) |
| Bulk-invite CSV | [ops/entra/guests/tbwa-smp-finance-import.csv](../../ops/entra/guests/tbwa-smp-finance-import.csv) |
| Target state | [ssot/identity/entra_target_state.yaml](../../ssot/identity/entra_target_state.yaml) |

---

## Preconditions

1. Operator holds `Jake Tolentino (Admin)` with PIM activation (User Administrator or Guest Inviter).
2. `omc.com` appears in external collaboration allowlist.
3. Guest invite scope is restricted to admins/user-admin role.
4. Groups below exist (create in Step 2 if not):
   - `grp-ext-tbwasmp-finance`
   - `grp-ext-tbwasmp-finance-approvers`
   - `grp-ext-tbwasmp-finance-reviewers`
   - `grp-ext-tbwasmp-finance-readonly`

---

## Step 1 — Create guest groups (one-time)

```bash
for grp in \
  grp-ext-tbwasmp-finance \
  grp-ext-tbwasmp-finance-approvers \
  grp-ext-tbwasmp-finance-reviewers \
  grp-ext-tbwasmp-finance-readonly; do
  az ad group create \
    --display-name "$grp" \
    --mail-nickname "$grp" \
    --description "TBWA\\SMP Finance — $grp" \
    --query id -o tsv
done
```

Evidence: capture group object IDs into
`docs/evidence/<YYYYMMDD-HHMM>/entra-guest-onboarding/groups.json`.

---

## Step 2 — Bulk invite via Entra admin center

1. Navigate: **Entra admin center → Identity → Users → Bulk operations → Bulk invite**.
2. Upload [ops/entra/guests/tbwa-smp-finance-import.csv](../../ops/entra/guests/tbwa-smp-finance-import.csv).
3. Confirm preview shows 11 rows, all `Guest`, all `@omc.com`, all displayName ending `(TBWA\SMP)`.
4. Submit. Entra sends invitations to each `@omc.com` mailbox with redirect
   `https://myapplications.microsoft.com`.

Evidence: export the completed bulk job status to
`docs/evidence/<YYYYMMDD-HHMM>/entra-guest-onboarding/bulk-invite-status.json`.

---

## Step 3 — Assign guests to groups

Use the membership mapping in [guest-groups.yaml](../../ssot/identity/guest-groups.yaml).

```bash
GUEST_UPN="Khalil_Veracruz_omc.com#EXT#@ceoinsightpulseai.onmicrosoft.com"   # pattern
GROUP_ID="$(az ad group show --group grp-ext-tbwasmp-finance --query id -o tsv)"
MEMBER_ID="$(az ad user show --id "$GUEST_UPN" --query id -o tsv)"
az ad group member add --group "$GROUP_ID" --member-id "$MEMBER_ID"
```

Repeat for the role-scoped sub-group per the registry.

---

## Step 4 — Apply attributes

Set the mandatory attributes for each guest (cannot be done in bulk-invite CSV):

```bash
az ad user update --id "$GUEST_UPN" \
  --set companyName="TBWA\\SMP" \
  --set department="Finance" \
  --set employeeType="ExternalClient"
```

---

## Step 5 — Verification

| Check | Command | Pass criteria |
|---|---|---|
| User type | `az ad user show --id "$UPN" --query userType -o tsv` | `Guest` |
| Display name | `az ad user show --id "$UPN" --query displayName -o tsv` | ends with `(TBWA\SMP)` |
| Email preserved | `az ad user show --id "$UPN" --query mail -o tsv` | `*@omc.com` |
| Company | `az ad user show --id "$UPN" --query companyName -o tsv` | `TBWA\SMP` |
| Department | `az ad user show --id "$UPN" --query department -o tsv` | `Finance` |
| Group membership | `az ad user get-member-groups --id "$UPN"` | includes `grp-ext-tbwasmp-finance` |
| No standing role | `az rest --method GET --url "https://graph.microsoft.com/v1.0/users/$OID/memberOf"` | zero directory role memberships |

Capture output to `docs/evidence/<YYYYMMDD-HHMM>/entra-guest-onboarding/verification.txt`.

---

## Step 6 — Conditional Access application

Confirm guest MFA policy covers the new users:

```bash
az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/identity/conditionalAccess/policies" \
  --query "value[?displayName=='guest_mfa_required']"
```

Policy must target `Guest or external users` scope and require MFA.

---

## Prohibited actions

- Direct app assignment to guest users (bypasses group model).
- Adding guests to any directory role.
- Renaming display names without the `(TBWA\SMP)` suffix.
- Inviting `@omc.com` users as Member instead of Guest.
- Creating parallel groups outside the four canonical groups.

---

## Offboarding

When a guest leaves the engagement:

1. Remove from all `grp-ext-tbwasmp-*` groups.
2. Set `accountEnabled: false`.
3. If the engagement is complete, delete the guest user object (30-day soft-delete applies).
4. Update the `disposition` field in the registry YAML.
5. Commit evidence pack.
