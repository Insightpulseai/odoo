using './main.bicep'

param acaEnvironmentName = 'ipai-odoo-dev-env-v2'
param postgresFqdn = 'pg-ipai-odoo.postgres.database.azure.com'
param dbName = 'odoo'
param dbUser = 'odoo_admin'
param keyVaultUri = 'https://kv-ipai-dev.vault.azure.net/'
param logAnalyticsWorkspaceName = 'la-ipai-odoo-dev'
param managedIdentityName = 'id-ipai-dev'

param webAppName = 'ipai-odoo-dev-web'
param workerAppName = 'ipai-odoo-dev-worker'
param cronAppName = 'ipai-odoo-dev-cron'

param odooImage = 'acripaiodoo.azurecr.io/ipai-odoo:18.0-copilot'

param webCpu = '2.0'
param webMemory = '4Gi'
param workerCpu = '1.0'
param workerMemory = '2Gi'
param cronCpu = '0.5'
param cronMemory = '1Gi'

param tags = {
  app: 'odoo'
  workload: 'odoo'
  platform: 'azure'
  'managed-by': 'bicep'
  owner: 'insightpulseai'
  repo: 'odoo'
  service: 'erp'
  environment: 'dev'
  'cost-center': 'ipai'
  'data-classification': 'internal'
  lifecycle: 'active'
}
