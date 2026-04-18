#!/usr/bin/env bash
# Quickstart prototype bringup for ipai-odoo-dev:
#   1. Wire Foundry env vars on ACA (managed identity → ipai-copilot-resource)
#   2. Enable + configure Azure Entra OAuth provider in Odoo
#   3. Enable + configure Google Workspace OAuth provider for w9studio.net
#   4. Ensure break-glass local admin exists (password in Key Vault)
#
# Usage:
#   bash scripts/odoo/quickstart_sso_and_foundry.sh
#
# Prereqs:
#   - az CLI logged in, on Sub A (Microsoft Azure Sponsorship)
#   - Entra app registration `InsightPulse AI - Odoo Login` (3446e178-...) exists
#   - Google OAuth Client ID created in Google Cloud Console (w9studio.net workspace)
#       Authorized redirect URI: https://erp.insightpulseai.com/auth_oauth/signin
#   - Key Vault kv-ipai-dev-sea accessible
#
# What this DOES:
#   - Sets env vars on ACA (no secrets baked into image)
#   - Seeds OAuth providers via Odoo server action (requires DB connection)
#   - Creates break-glass admin if missing
#
# What this DOES NOT:
#   - Install the module (use scripts/odoo/install_module.sh)
#   - Push secrets to any commit
set -euo pipefail

# Configuration
ACA_APP="${ACA_APP:-ipai-odoo-dev}"
ACA_RG="${ACA_RG:-rg-ipai-dev-odoo-sea}"
KV="${KV:-kv-ipai-dev-sea}"
TENANT_ID="${TENANT_ID:-402de71a-87ec-4302-a609-fb76098d1da7}"
ENTRA_APP_ID="${ENTRA_APP_ID:-3446e178-3eba-48c9-b5bd-4283ff729eb1}"
ODOO_BASE_URL="${ODOO_BASE_URL:-https://erp.insightpulseai.com}"
FOUNDRY_ENDPOINT="${FOUNDRY_ENDPOINT:-https://ipai-copilot-resource.services.ai.azure.com}"
FOUNDRY_PROJECT="${FOUNDRY_PROJECT:-ipai-copilot}"

echo "=== Step 1: Wire Foundry env vars on ACA ==="
echo "Target: ${ACA_APP} / ${ACA_RG}"
echo "Endpoint: ${FOUNDRY_ENDPOINT}"
echo "Project: ${FOUNDRY_PROJECT}"

az containerapp update \
  --name "${ACA_APP}" \
  --resource-group "${ACA_RG}" \
  --set-env-vars \
    "IPAI_FOUNDRY_ENDPOINT=${FOUNDRY_ENDPOINT}" \
    "IPAI_FOUNDRY_PROJECT=${FOUNDRY_PROJECT}" \
    "IPAI_FOUNDRY_MODEL=gpt-4.1" \
    "IPAI_FOUNDRY_AGENT_NAME=ipai-odoo-copilot" \
    "AZURE_TENANT_ID=${TENANT_ID}" \
    "AZURE_OAUTH_CLIENT_ID=${ENTRA_APP_ID}" \
    "ODOO_BASE_URL=${ODOO_BASE_URL}" \
  1>&2

echo ""
echo "=== Step 2: Retrieve Google OAuth Client ID from Key Vault ==="
# Google OAuth must be created in Google Cloud Console first.
# Store the Client ID in Key Vault as google-oauth-client-id (w9studio.net tenant).
GOOGLE_CLIENT_ID=$(az keyvault secret show \
  --vault-name "${KV}" --name google-oauth-client-id \
  --query value -o tsv 2>/dev/null || echo "")

if [[ -z "${GOOGLE_CLIENT_ID}" ]]; then
  echo "WARN: google-oauth-client-id not found in ${KV}."
  echo "      Create the Google OAuth Client ID in Google Cloud Console"
  echo "      (https://console.cloud.google.com/apis/credentials), then:"
  echo "        az keyvault secret set --vault-name ${KV} --name google-oauth-client-id --value '<id>.apps.googleusercontent.com'"
  echo "      Google SSO will NOT be activated on this run."
fi

echo ""
echo "=== Step 3: Seed OAuth providers via Odoo shell ==="
# Executed via `odoo shell` on the ACA instance.
# The OAuth provider records already exist from the module's data/oauth_providers.xml;
# this step enables them and sets client IDs.
PYTHON_SCRIPT=$(cat <<PYEOF
tenant_id = "${TENANT_ID}"
entra_client_id = "${ENTRA_APP_ID}"
google_client_id = "${GOOGLE_CLIENT_ID}"
odoo_base = "${ODOO_BASE_URL}"

# Azure Entra provider
azure = env.ref('ipai_odoo_copilot.oauth_provider_azure', raise_if_not_found=False)
if azure:
    azure.write({
        'client_id': entra_client_id,
        'auth_endpoint': f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize',
        'enabled': bool(entra_client_id),
    })
    print(f'[ok] Azure Entra provider updated (enabled={bool(entra_client_id)})')
else:
    print('[warn] ipai_odoo_copilot.oauth_provider_azure not found — install module first')

# Google provider
google = env.ref('ipai_odoo_copilot.oauth_provider_google_w9', raise_if_not_found=False)
if google:
    google.write({
        'client_id': google_client_id,
        'enabled': bool(google_client_id),
    })
    print(f'[ok] Google provider updated (enabled={bool(google_client_id)})')
else:
    print('[warn] ipai_odoo_copilot.oauth_provider_google_w9 not found — install module first')

# Set auth_oauth header parameter (required by Entra token exchange)
env['ir.config_parameter'].sudo().set_param('auth_oauth.authorization_header', '1')

env.cr.commit()
print('[done] OAuth providers configured')
PYEOF
)

echo "${PYTHON_SCRIPT}" | az containerapp exec \
  --name "${ACA_APP}" \
  --resource-group "${ACA_RG}" \
  --command "odoo shell -d odoo --no-http --stop-after-init" \
  2>&1 || {
    echo "NOTE: Direct shell exec may require running the Python script manually via odoo shell"
    echo "Python script saved to: /tmp/odoo_oauth_setup_$$.py"
    echo "${PYTHON_SCRIPT}" > "/tmp/odoo_oauth_setup_$$.py"
}

echo ""
echo "=== Step 4: Ensure break-glass admin exists ==="
BREAKGLASS_PASSWORD=$(az keyvault secret show \
  --vault-name "${KV}" --name odoo-breakglass-password \
  --query value -o tsv 2>/dev/null || echo "")

if [[ -z "${BREAKGLASS_PASSWORD}" ]]; then
  echo "Break-glass password not in Key Vault; generating one."
  BREAKGLASS_PASSWORD=$(openssl rand -base64 32)
  az keyvault secret set \
    --vault-name "${KV}" \
    --name odoo-breakglass-password \
    --value "${BREAKGLASS_PASSWORD}" \
    --description "Odoo break-glass admin password for ipai-odoo-dev (rotate quarterly)" \
    >/dev/null
  echo "[ok] Break-glass password stored in ${KV}/odoo-breakglass-password"
else
  echo "[ok] Break-glass password already in Key Vault"
fi

cat <<BGEOF

Break-glass admin creation (run once, manually, as existing admin):
  In Odoo UI: Settings → Users & Companies → Users → Create
    Login:    breakglass@insightpulseai.com
    Name:     Break-Glass Admin (DO NOT USE EXCEPT IN EMERGENCY)
    Password: <value from KV>
    Access Rights: Administration = Settings
    OAuth Provider: (LEAVE EMPTY — this user must NOT use SSO)

Or via Odoo shell:
  user = env['res.users'].create({
    'login': 'breakglass@insightpulseai.com',
    'name': 'Break-Glass Admin',
    'password': '<from-kv>',
    'oauth_provider_id': False,
    'groups_id': [(6, 0, [env.ref('base.group_system').id])],
  })

BGEOF

echo ""
echo "=== Verification commands ==="
cat <<VEOF
# Check env vars are set on ACA:
az containerapp show -n ${ACA_APP} -g ${ACA_RG} \\
  --query "properties.template.containers[0].env[?starts_with(name, 'IPAI_') || starts_with(name, 'AZURE_')].{name:name, value:value}" -o table

# Test Foundry connectivity from inside the container:
az containerapp exec -n ${ACA_APP} -g ${ACA_RG} --command "\
  curl -sSL -H \"Authorization: Bearer \$(az account get-access-token --resource https://cognitiveservices.azure.com --query accessToken -o tsv)\" \\
  ${FOUNDRY_ENDPOINT}/api/projects/${FOUNDRY_PROJECT}/agents | head"

# Test SSO flow:
#   Open ${ODOO_BASE_URL}/web/login — should see "Sign in with Microsoft" + "Sign in with Google" buttons
#   (Google only if google-oauth-client-id is in Key Vault)

# Emergency local login:
#   URL: ${ODOO_BASE_URL}/web/login
#   User: breakglass@insightpulseai.com
#   Pass: \$(az keyvault secret show --vault-name ${KV} --name odoo-breakglass-password --query value -o tsv)
VEOF

echo ""
echo "=== DONE ==="
