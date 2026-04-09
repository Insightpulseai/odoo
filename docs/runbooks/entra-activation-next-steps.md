# Entra Activation Next Steps — Odoo OIDC Runtime Activation

**Spec**: `spec/entra-identity-migration/`
**Status**: Executable — requires Azure CLI access with `Application.ReadWrite.All` or Global Admin
**Prerequisite**: Entra tenant `402de71a` bootstrapped, app `07bd9669` registered, `ipai_auth_oidc` module deployed
**SSOT**: `ssot/entra/app_registrations.azure_native.yaml`
**Identity contract**: `ssot/contracts/identity.yaml`

---

## Constants

```bash
TENANT_ID="402de71a-b159-4006-87d6-50d39f2dfd3d"
APP_ID="07bd9669-1eca-4d93-8880-fd3abb87f812"
KEY_VAULT="kv-ipai-dev"
ODOO_FQDN="erp.insightpulseai.com"
REDIRECT_URI="https://${ODOO_FQDN}/auth_oauth/signin"
```

---

## Step 1: Verify the App Registration

Confirm the app registration exists and inspect its current configuration.

```bash
# Login to the correct tenant
az login --tenant "${TENANT_ID}"

# Show the app registration
az ad app show --id "${APP_ID}" \
  --query '{displayName:displayName, appId:appId, signInAudience:signInAudience, web:web}' \
  --output json
```

Expected output: `displayName` = `InsightPulseAI Odoo Login`, `appId` = `07bd9669-...`.

Check current redirect URIs:

```bash
az ad app show --id "${APP_ID}" \
  --query 'web.redirectUris' \
  --output tsv
```

If the redirect URI `https://erp.insightpulseai.com/auth_oauth/signin` is already listed, skip Step 2.

---

## Step 2: Add Redirect URI

Add the Odoo OAuth callback URI to the app registration.

```bash
# Get current redirect URIs (if any)
CURRENT_URIS=$(az ad app show --id "${APP_ID}" --query 'web.redirectUris' --output tsv)

# Add the Odoo redirect URI
az ad app update --id "${APP_ID}" \
  --web-redirect-uris "${REDIRECT_URI}"
```

If additional redirect URIs already exist and must be preserved, list them all:

```bash
az ad app update --id "${APP_ID}" \
  --web-redirect-uris \
    "https://erp.insightpulseai.com/auth_oauth/signin" \
    "https://localhost:8069/auth_oauth/signin"
```

The localhost URI is optional for local development. Remove it before production cutover.

Also set the front-channel logout URL:

```bash
az ad app update --id "${APP_ID}" \
  --web-home-page-url "https://erp.insightpulseai.com" \
  --set "web.logoutUrl=https://erp.insightpulseai.com/web/session/logout"
```

Verify:

```bash
az ad app show --id "${APP_ID}" \
  --query '{redirectUris:web.redirectUris, logoutUrl:web.logoutUrl, homePageUrl:web.homePageUrl}' \
  --output json
```

---

## Step 3: Create Client Secret and Store in Key Vault

Odoo's `auth_oauth` module with `id_token_code` flow requires a client secret to exchange the authorization code for tokens.

```bash
# Create a client secret (2-year expiry)
SECRET_JSON=$(az ad app credential reset \
  --id "${APP_ID}" \
  --display-name "odoo-oidc-prod-$(date +%Y%m%d)" \
  --years 2 \
  --query '{password:password, keyId:keyId, endDateTime:endDateTime}' \
  --output json)

# Extract the secret value (only shown once)
CLIENT_SECRET=$(echo "${SECRET_JSON}" | jq -r '.password')
KEY_ID=$(echo "${SECRET_JSON}" | jq -r '.keyId')

echo "Key ID: ${KEY_ID}"
echo "Secret prefix: ${CLIENT_SECRET:0:8}..."
echo "IMPORTANT: This secret is shown only once. Store it in Key Vault immediately."
```

Store in Azure Key Vault:

```bash
# Store client secret
az keyvault secret set \
  --vault-name "${KEY_VAULT}" \
  --name "entra-odoo-login-client-secret" \
  --value "${CLIENT_SECRET}" \
  --description "Entra app 07bd9669 client secret for Odoo OIDC (key: ${KEY_ID})" \
  --tags app=ipai-odoo-login-prod purpose=oidc-client-secret

# Store client ID (for reference / env injection)
az keyvault secret set \
  --vault-name "${KEY_VAULT}" \
  --name "entra-odoo-login-client-id" \
  --value "${APP_ID}" \
  --description "Entra app 07bd9669 client ID for Odoo OIDC" \
  --tags app=ipai-odoo-login-prod purpose=oidc-client-id
```

Verify secrets are stored:

```bash
az keyvault secret show \
  --vault-name "${KEY_VAULT}" \
  --name "entra-odoo-login-client-secret" \
  --query '{name:name, created:attributes.created, enabled:attributes.enabled}' \
  --output json

az keyvault secret show \
  --vault-name "${KEY_VAULT}" \
  --name "entra-odoo-login-client-id" \
  --query '{name:name, created:attributes.created, enabled:attributes.enabled}' \
  --output json
```

Clear the secret from the shell environment:

```bash
unset CLIENT_SECRET SECRET_JSON
```

---

## Step 4: Configure Odoo Auth Provider

The `ipai_auth_oidc` module ships with placeholder values. Two options to activate:

### Option A: Environment Variables (Preferred for ACA)

Set on the `ipai-odoo-dev-web` container app. The module's `get_values()` method auto-detects `ENTRA_ODOO_CLIENT_ID`.

```bash
# Set env vars on the Odoo container app
az containerapp update \
  --name ipai-odoo-dev-web \
  --resource-group rg-ipai-dev-odoo-runtime \
  --set-env-vars \
    "ENTRA_ODOO_CLIENT_ID=07bd9669-1eca-4d93-8880-fd3abb87f812" \
    "ENTRA_ODOO_TENANT_ID=402de71a-b159-4006-87d6-50d39f2dfd3d"
```

Note: The client secret is NOT set as an env var. Odoo's `auth_oauth` reads it from the `auth.oauth.provider` record's `client_secret` field (if Odoo 18 supports it) or uses the Authorization Code flow where the server-side token exchange reads the secret from a secure config.

### Option B: Direct Odoo Configuration (via XML-RPC or Settings UI)

If direct Odoo database access is available:

```bash
# Using odoo-bin shell (inside container or devcontainer)
odoo-bin shell -d odoo_dev --no-http <<'PYEOF'
ICP = env['ir.config_parameter'].sudo()
ICP.set_param('ipai.auth.oidc.entra.tenant_id', '402de71a-b159-4006-87d6-50d39f2dfd3d')
ICP.set_param('ipai.auth.oidc.entra.client_id', '07bd9669-1eca-4d93-8880-fd3abb87f812')
ICP.set_param('ipai.auth.oidc.entra.enabled', 'True')

# Update the auth.oauth.provider record with tenant-specific endpoints
provider = env['auth.oauth.provider'].sudo().search([('name', '=', 'Microsoft Entra ID')], limit=1)
if provider:
    tenant = '402de71a-b159-4006-87d6-50d39f2dfd3d'
    provider.write({
        'client_id': '07bd9669-1eca-4d93-8880-fd3abb87f812',
        'auth_endpoint': f'https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize',
        'validation_endpoint': f'https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token',
        'enabled': True,
    })
    print(f'Provider updated: {provider.name} (id={provider.id})')
else:
    print('ERROR: Entra ID provider not found — ensure ipai_auth_oidc is installed')

env.cr.commit()
PYEOF
```

Alternatively, use the Settings UI:
1. Navigate to Settings > General Settings > Microsoft Entra ID SSO
2. Set Tenant ID = `402de71a-b159-4006-87d6-50d39f2dfd3d`
3. Set Client ID = `07bd9669-1eca-4d93-8880-fd3abb87f812`
4. Click "Apply Entra Provider"

---

## Step 5: Configure Optional Token Claims

Add `email`, `preferred_username`, and `groups` to the ID token claims so Odoo receives them during login.

```bash
# Add optional claims for ID token
az ad app update --id "${APP_ID}" \
  --set "optionalClaims={
    \"idToken\": [
      {\"name\": \"email\", \"essential\": true},
      {\"name\": \"preferred_username\", \"essential\": false},
      {\"name\": \"groups\", \"essential\": false}
    ],
    \"accessToken\": [
      {\"name\": \"email\", \"essential\": true}
    ]
  }"
```

For group claims, configure the app to emit security group object IDs:

```bash
# Set groupMembershipClaims to SecurityGroup
az ad app update --id "${APP_ID}" \
  --set "groupMembershipClaims=SecurityGroup"
```

Verify claims configuration:

```bash
az ad app show --id "${APP_ID}" \
  --query '{optionalClaims:optionalClaims, groupMembershipClaims:groupMembershipClaims}' \
  --output json
```

---

## Step 6: Test the Login Flow

### 6a: Smoke test — verify Entra authorization endpoint responds

```bash
# Construct the authorization URL
AUTH_URL="https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/authorize?client_id=${APP_ID}&response_type=code&redirect_uri=https%3A%2F%2Ferp.insightpulseai.com%2Fauth_oauth%2Fsignin&scope=openid+email+profile+User.Read&response_mode=query"

echo "Open in browser:"
echo "${AUTH_URL}"

# Verify the endpoint returns HTML (not an error)
curl -s -o /dev/null -w "%{http_code}" \
  "https://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/authorize?client_id=${APP_ID}&response_type=code&redirect_uri=https%3A%2F%2Ferp.insightpulseai.com%2Fauth_oauth%2Fsignin&scope=openid+email+profile&response_mode=query"
# Expected: 200 (login page) or 302 (redirect to login)
```

### 6b: Verify Odoo shows the "Sign in with Microsoft" button

```bash
curl -s "https://erp.insightpulseai.com/web/login" | grep -o "Sign in with Microsoft"
# Expected: "Sign in with Microsoft"
```

### 6c: Full interactive test (browser)

1. Open `https://erp.insightpulseai.com/web/login` in an incognito window
2. Click "Sign in with Microsoft"
3. Authenticate with an Entra ID user from the `insightpulseai.com` tenant
4. Verify redirect back to Odoo with an active session
5. Check the user was JIT-provisioned: Settings > Users > search by email

### 6d: Verify JIT user in database

```bash
# Inside Odoo shell or via XML-RPC
odoo-bin shell -d odoo_dev --no-http <<'PYEOF'
user = env['res.users'].sudo().search([('login', '=', 'test@insightpulseai.com')], limit=1)
if user:
    print(f'User: {user.name} (login={user.login}, id={user.id})')
    print(f'OAuth provider: {user.oauth_provider_id.name}')
    print(f'OAuth UID: {user.oauth_uid}')
    print(f'Groups: {[g.full_name for g in user.group_ids]}')
else:
    print('User not found — JIT provisioning may not have triggered')
PYEOF
```

---

## Step 7: Evidence Collection

After successful login test, capture evidence:

```bash
STAMP=$(date +%Y%m%d-%H%M)
EVIDENCE_DIR="docs/evidence/${STAMP}/entra-activation"
mkdir -p "${EVIDENCE_DIR}"

# Export app registration config
az ad app show --id "${APP_ID}" --output json > "${EVIDENCE_DIR}/app_registration.json"

# Export OAuth provider state from Odoo (via shell)
# Save the login page HTML showing the button
curl -s "https://erp.insightpulseai.com/web/login" > "${EVIDENCE_DIR}/login_page.html"

# Verify Key Vault secrets exist (metadata only, not values)
az keyvault secret list --vault-name "${KEY_VAULT}" \
  --query "[?starts_with(name, 'entra-odoo')]" \
  --output json > "${EVIDENCE_DIR}/keyvault_secrets_metadata.json"

echo "Evidence saved to: ${EVIDENCE_DIR}/"
```

---

## Rollback

If the login flow fails or causes issues:

1. **Disable the provider in Odoo**:
   ```bash
   odoo-bin shell -d odoo_dev --no-http <<'PYEOF'
   provider = env['auth.oauth.provider'].sudo().search([('name', '=', 'Microsoft Entra ID')], limit=1)
   if provider:
       provider.write({'enabled': False})
       print('Entra ID provider disabled')
   env.cr.commit()
   PYEOF
   ```

2. **Or via Settings UI**: Settings > General Settings > Entra ID SSO > uncheck "Entra ID SSO Enabled" > Apply Entra Provider

3. Users revert to basic Odoo password login. No data loss. JIT-provisioned users remain but cannot SSO until re-enabled.

---

## Post-Activation Checklist

After successful end-to-end test:

- [ ] Tenant ID set to `402de71a` (not `common`)
- [ ] Client ID set to `07bd9669` (not placeholder)
- [ ] Redirect URI `https://erp.insightpulseai.com/auth_oauth/signin` registered
- [ ] Client secret stored in Key Vault `kv-ipai-dev` as `entra-odoo-login-client-secret`
- [ ] "Sign in with Microsoft" button visible on login page
- [ ] At least one user successfully authenticated via Entra
- [ ] JIT-provisioned user exists in Odoo with correct email and OAuth UID
- [ ] Evidence captured in `docs/evidence/<stamp>/entra-activation/`
- [ ] `spec/entra-identity-migration/tasks.md` updated with completed items

---

## References

- App registration SSOT: `ssot/entra/app_registrations.azure_native.yaml`
- Identity contract: `ssot/contracts/identity.yaml`
- Module source: `addons/ipai/ipai_auth_oidc/`
- Spec bundle: `spec/entra-identity-migration/`
- Existing IdP runbook: `docs/runbooks/entra-idp-activation.md`
- Odoo Azure SSO docs: https://www.odoo.com/documentation/19.0/applications/general/users/azure.html
- Entra app registration best practices: https://learn.microsoft.com/entra/identity-platform/security-best-practices-for-app-registration
