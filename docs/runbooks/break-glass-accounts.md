# Break-Glass Account Runbook

**Blocker**: B-3
**Status**: DOCUMENTED -- procedure exists, execution pending (requires Entra Global Admin)

---

## Purpose

Two cloud-only Global Administrator accounts that provide emergency tenant access when all other authentication paths fail. These accounts bypass Conditional Access and federated identity, ensuring recovery is always possible.

---

## Account Specification

| Property | Account 1 | Account 2 |
|----------|-----------|-----------|
| **UPN** | `breakglass1@insightpulseai.com` | `breakglass2@insightpulseai.com` |
| **Display name** | `Break Glass 1 (Emergency)` | `Break Glass 2 (Emergency)` |
| **Type** | Cloud-only (no federation, no sync) | Cloud-only (no federation, no sync) |
| **Role** | Global Administrator | Global Administrator |
| **License** | Microsoft Entra ID P2 | Microsoft Entra ID P2 |
| **MFA** | Excluded from all Conditional Access policies | Excluded from all Conditional Access policies |

---

## Creation Procedure

### Prerequisites

- Active Global Administrator session on `insightpulseai.com` tenant (`402de71a`)
- Azure Key Vault `kv-ipai-dev` accessible with Key Vault Administrator role

### Step 1: Create the accounts

```bash
# Account 1
az ad user create \
  --display-name "Break Glass 1 (Emergency)" \
  --user-principal-name breakglass1@insightpulseai.com \
  --password "$(openssl rand -base64 32)" \
  --force-change-password-next-sign-in false \
  --account-enabled true

# Account 2
az ad user create \
  --display-name "Break Glass 2 (Emergency)" \
  --user-principal-name breakglass2@insightpulseai.com \
  --password "$(openssl rand -base64 32)" \
  --force-change-password-next-sign-in false \
  --account-enabled true
```

### Step 2: Assign Global Administrator role

```bash
GLOBAL_ADMIN_ROLE_ID=$(az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/directoryRoles" \
  --query "value[?displayName=='Global Administrator'].id" -o tsv)

# Get user object IDs
BG1_ID=$(az ad user show --id breakglass1@insightpulseai.com --query id -o tsv)
BG2_ID=$(az ad user show --id breakglass2@insightpulseai.com --query id -o tsv)

# Assign role
az rest --method POST \
  --url "https://graph.microsoft.com/v1.0/directoryRoles/$GLOBAL_ADMIN_ROLE_ID/members/\$ref" \
  --body "{\"@odata.id\": \"https://graph.microsoft.com/v1.0/directoryObjects/$BG1_ID\"}"

az rest --method POST \
  --url "https://graph.microsoft.com/v1.0/directoryRoles/$GLOBAL_ADMIN_ROLE_ID/members/\$ref" \
  --body "{\"@odata.id\": \"https://graph.microsoft.com/v1.0/directoryObjects/$BG2_ID\"}"
```

### Step 3: Exclude from Conditional Access

When creating any Conditional Access policy, explicitly exclude both break-glass accounts:

- Navigate to Entra ID > Protection > Conditional Access
- In every policy, under "Users" > "Exclude", add both `breakglass1@insightpulseai.com` and `breakglass2@insightpulseai.com`
- Alternatively, create an "Excluded from CA" security group containing both accounts and exclude that group from all policies

### Step 4: Vault the credentials

```bash
# Store passwords in Azure Key Vault
az keyvault secret set --vault-name kv-ipai-dev \
  --name "breakglass1-password" \
  --value "<password-from-step-1>"

az keyvault secret set --vault-name kv-ipai-dev \
  --name "breakglass2-password" \
  --value "<password-from-step-2>"
```

### Step 5: Create offline backup

1. Print the credentials for both accounts
2. Seal in tamper-evident envelopes
3. Store in physically separate locations (e.g., company safe + executive custody)
4. Document storage locations in a sealed register accessible only to the CEO and CTO

---

## MFA Exclusion Rationale

Break-glass accounts are intentionally excluded from MFA requirements because:

1. **Recovery scenario**: If MFA infrastructure fails (Authenticator app outage, FIDO2 hardware lost), break-glass accounts must remain accessible
2. **Conditional Access failure**: If a misconfigured CA policy locks out all admins, break-glass accounts bypass the lockout
3. **Federation failure**: If Entra OIDC or any federated IdP is down, cloud-only accounts with no MFA dependency still work
4. **Microsoft guidance**: Microsoft explicitly recommends excluding break-glass accounts from CA policies (see: "Manage emergency access accounts in Microsoft Entra ID")

### Compensating Controls

Since MFA is not enforced, the following compensating controls apply:

- Passwords are 32+ characters, randomly generated, never memorized
- Passwords are stored only in Azure Key Vault and physical sealed envelopes
- Sign-in logs for both accounts are monitored via Azure Monitor alert rule
- Accounts are tested quarterly (see Recovery Test Procedure below)
- Accounts are never used for day-to-day operations

---

## Monitoring

Create an Azure Monitor alert for any sign-in by break-glass accounts:

```bash
# Create action group for alerting
az monitor action-group create \
  --resource-group rg-ipai-dev-platform \
  --name ag-breakglass-alert \
  --short-name BrkGlass \
  --email-receivers name=PlatformOwner email=platform-owner@insightpulseai.com

# Alert on any sign-in by break-glass UPNs
# Configure in Azure AD Sign-in Logs > Diagnostic Settings > Log Analytics
# KQL: SigninLogs | where UserPrincipalName startswith "breakglass"
```

---

## Recovery Test Procedure

**Frequency**: Quarterly (next: Q2 2026)

1. Retrieve `breakglass1-password` from Azure Key Vault
2. Open an InPrivate/Incognito browser session
3. Navigate to `https://portal.azure.com`
4. Sign in as `breakglass1@insightpulseai.com`
5. Confirm Global Administrator access (verify role assignment in Entra ID > Users)
6. Sign out immediately
7. Verify the Azure Monitor alert fired for the sign-in
8. Document test result in `docs/evidence/<YYYYMMDD-HHMM>/break-glass-test/`
9. If password rotation is due (annual), rotate and re-vault

**Do NOT test both accounts in the same session.** Test account 2 in a separate quarterly cycle to ensure at least one account is always in a known-good state.

---

## When to Use Break-Glass Accounts

Use ONLY when:

- All other Global Administrator accounts are locked out
- Conditional Access misconfiguration prevents admin sign-in
- MFA infrastructure is down and no admin can authenticate
- Federated identity provider is experiencing a total outage
- Tenant configuration needs emergency correction

**Never use for**: routine administration, testing, development, or any non-emergency purpose.

---

*Last updated: 2026-03-27*
