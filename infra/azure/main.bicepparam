// main.bicepparam — IPAI Pulser Production Parameters
// Populate secrets via: az keyvault secret set OR azd env set
// NEVER commit populated secret values to git

using './main.bicep'

param env              = readEnvironmentVariable('AZURE_ENV_TOKEN', 'dev')
param locationSea      = 'southeastasia'
param locationEus2     = 'eastus2'
param zoneRedundant    = true

// Secrets: set via CI/CD pipeline from Key Vault or azd env set
// azd env set AZURE_PG_ADMIN_LOGIN <value>
// azd env set AZURE_PG_ADMIN_PASSWORD <value>  (rotated after first deploy)
// azd env set AZURE_ADE_API_KEY <value>
// azd env set AZURE_DEPLOY_PRINCIPAL_ID <objectId of deploying SP>
param pgAdminLogin     = readEnvironmentVariable('AZURE_PG_ADMIN_LOGIN', 'ipaiadmin')
param pgAdminPassword  = readEnvironmentVariable('AZURE_PG_ADMIN_PASSWORD', '')
param adeApiKey        = readEnvironmentVariable('AZURE_ADE_API_KEY', '')
param deployPrincipalId= readEnvironmentVariable('AZURE_DEPLOY_PRINCIPAL_ID', '')
param odooImageTag     = readEnvironmentVariable('AZURE_ODOO_IMAGE_TAG', 'latest')
