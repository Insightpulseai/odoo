# Entra IdP Activation Runbook

**Blocker**: B-1
**Status**: DOCUMENTED -- activation runbook exists, execution pending (requires Entra Global Admin + Odoo admin)

---

## Current State

| Component | Status | Evidence |
|-----------|--------|----------|
| Entra tenant | Verified | Tenant `402de71a`, domain `insightpulseai.com` verified and default |
| Entra P2 license | Active | Licensed for Conditional Access, PIM, Identity Protection |
| App registration | Exists | Client ID `07bd9669`, registered for Odoo OIDC |
| OAuth provider XML | In repo | `addons/ipai/ipai_auth_oidc/data/oauth_providers.xml` |
| `auth_oauth` module | Available | Odoo 19 CE ships `auth_oauth` in base addons |
| Break-glass accounts | Not yet created | Prerequisite B-3 must be completed first |
| Conditional Access | Not configured | No baseline policies exist |
| Enterprise app assignment | Not done | No users/groups assigned to the Odoo enterprise app |

---

## Prerequisites

Before executing this runbook:

1. B-3 (break-glass accounts) must be completed -- provides recovery path if Entra activation fails
2. Global Administrator access to tenant `402de71a`
3. Odoo admin access to `erp.insightpulseai.com`
4. Azure Key Vault `kv-ipai-dev` accessible

---

## Activation Steps

### Phase 1: Entra-Side Configuration

#### 1.1 Verify App Registration

```bash
# Confirm app registration exists
az ad app show --id 07bd9669-XXXX-XXXX-XXXX-XXXXXXXXXXXX --query '{appId:appId, displayName:displayName, web:web}'

# Expected: Odoo ERP app with redirect URIs pointing to erp.insightpulseai.com
```

#### 1.2 Configure Redirect URIs

Ensure the app registration has the correct redirect URIs:

```bash
az ad app update --id 07bd9669-XXXX-XXXX-XXXX-XXXXXXXXXXXX \
  --web-redirect-uris \
    "https://erp.insightpulseai.com/auth_oauth/signin" \
    "https://erp.insightpulseai.com/web"
```

#### 1.3 Create Client Secret (or use certificate)

```bash
# Create client secret (2-year expiry)
az ad app credential reset --id 07bd9669-XXXX-XXXX-XXXX-XXXXXXXXXXXX \
  --display-name "Odoo OIDC" \
  --years 2

# Store the secret in Key Vault
az keyvault secret set --vault-name kv-ipai-dev \
  --name "entra-odoo-client-secret" \
  --value "<secret-from-above>"
```

#### 1.4 Assign Users/Groups to Enterprise App

```bash
# Get the service principal (enterprise app) object ID
SP_ID=$(az ad sp show --id 07bd9669-XXXX-XXXX-XXXX-XXXXXXXXXXXX --query id -o tsv)

# Assign all-users group or specific groups
# Option A: Assign all company users
az rest --method POST \
  --url "https://graph.microsoft.com/v1.0/servicePrincipals/$SP_ID/appRoleAssignments" \
  --body "{
    \"principalId\": \"<group-or-user-object-id>\",
    \"resourceId\": \"$SP_ID\",
    \"appRoleId\": \"00000000-0000-0000-0000-000000000000\"
  }"
```

#### 1.5 Configure Token Claims

Ensure the token includes `email`, `name`, and `preferred_username` claims:

```bash
az ad app update --id 07bd9669-XXXX-XXXX-XXXX-XXXXXXXXXXXX \
  --optional-claims '{
    "idToken": [
      {"name": "email", "essential": true},
      {"name": "preferred_username", "essential": true},
      {"name": "given_name"},
      {"name": "family_name"}
    ]
  }'
```

### Phase 2: Odoo-Side Configuration

#### 2.1 Install auth_oauth Module

```bash
# Via Odoo CLI (in ACA container or devcontainer)
odoo-bin -d odoo_dev -i auth_oauth --stop-after-init
```

#### 2.2 Install ipai_auth_oidc Module

```bash
# This module ships the Microsoft Entra OAuth provider configuration
odoo-bin -d odoo_dev -i ipai_auth_oidc --stop-after-init
```

#### 2.3 Configure OAuth Provider in Odoo

After module installation, verify the OAuth provider record in Odoo:

- **Provider name**: Microsoft Entra ID
- **Client ID**: `07bd9669-XXXX-XXXX-XXXX-XXXXXXXXXXXX`
- **Client Secret**: Retrieved from Key Vault (`entra-odoo-client-secret`)
- **Authorization URL**: `https://login.microsoftonline.com/402de71a-XXXX-XXXX-XXXX-XXXXXXXXXXXX/oauth2/v2.0/authorize`
- **Token URL**: `https://login.microsoftonline.com/402de71a-XXXX-XXXX-XXXX-XXXXXXXXXXXX/oauth2/v2.0/token`
- **JWKS URL**: `https://login.microsoftonline.com/402de71a-XXXX-XXXX-XXXX-XXXXXXXXXXXX/discovery/v2.0/keys`
- **Scope**: `openid email profile`
- **Validation**: `authorization_header = 1` (already set in XML)

#### 2.4 Set Environment Variables

In the ACA container configuration:

```bash
az containerapp update --name ipai-odoo-dev-web \
  --resource-group rg-ipai-dev-odoo-runtime \
  --set-env-vars \
    ENTRA_CLIENT_ID=secretref:entra-odoo-client-id \
    ENTRA_CLIENT_SECRET=secretref:entra-odoo-client-secret \
    ENTRA_TENANT_ID=secretref:entra-tenant-id
```

### Phase 3: Conditional Access Baseline

#### 3.1 Create Baseline Policies

Minimum Conditional Access policies for go-live:

1. **Require MFA for admins**: All users with Global Admin, User Admin, or Privileged Role Admin must use MFA
2. **Block legacy authentication**: Block all authentication using legacy protocols
3. **Require compliant device for sensitive apps**: Optional for Phase 1

Exclude break-glass accounts from all policies (see `docs/runbooks/break-glass-accounts.md`).

### Phase 4: Testing

#### 4.1 Test SSO Round-Trip

1. Navigate to `https://erp.insightpulseai.com/web/login`
2. Click "Log in with Microsoft"
3. Authenticate with Entra credentials
4. Verify redirect back to Odoo with active session
5. Verify user record created/matched in Odoo

#### 4.2 Test Token Validation

```bash
# Verify the OIDC discovery endpoint is reachable from the ACA container
az containerapp exec --name ipai-odoo-dev-web \
  --resource-group rg-ipai-dev-odoo-runtime \
  --command "curl -s https://login.microsoftonline.com/402de71a-XXXX-XXXX-XXXX-XXXXXXXXXXXX/v2.0/.well-known/openid-configuration | python3 -m json.tool"
```

#### 4.3 Test Fallback to Local Auth

1. Disable the OAuth provider in Odoo (Settings > OAuth Providers > deactivate)
2. Verify local username/password login still works
3. Re-enable the OAuth provider

---

## Rollback Procedure

If Entra OIDC causes issues after activation:

### Immediate (< 5 minutes)

1. In Odoo Settings, deactivate the Microsoft Entra OAuth provider record
2. This immediately restores local-only authentication
3. Users can sign in with their Odoo local passwords

### Full Rollback (< 30 minutes)

1. Deactivate OAuth provider (as above)
2. Uninstall `ipai_auth_oidc` module:
   ```bash
   odoo-bin -d odoo_dev -u ipai_auth_oidc --stop-after-init
   ```
3. If `auth_oauth` itself is causing issues:
   ```bash
   # Disable via database (emergency only)
   psql -d odoo_dev -c "UPDATE ir_module_module SET state='uninstalled' WHERE name='auth_oauth';"
   ```
4. Restart the Odoo container:
   ```bash
   az containerapp revision restart --name ipai-odoo-dev-web \
     --resource-group rg-ipai-dev-odoo-runtime \
     --revision <current-revision>
   ```

### Recovery Path

If rollback is needed and admin accounts are locked out:

1. Use break-glass account to access Azure portal
2. Connect to the Odoo database directly via `pg-ipai-odoo`
3. Reset the admin user password:
   ```sql
   UPDATE res_users SET password = '' WHERE login = 'admin';
   ```
4. Sign in with blank password and immediately set a new one

---

## Exit Criteria (B-1 Done When)

- [ ] Production login path is Entra-backed (SSO round-trip succeeds)
- [ ] Target enterprise apps assigned (users can access Odoo via Entra)
- [ ] User/group access model validated
- [ ] Conditional access / MFA baseline applied
- [ ] Rollback procedure tested and documented

---

*Last updated: 2026-03-27*
