import type {
  ProviderConfig,
  RuntimeHealth,
  BuildInfo,
  DeployInfo,
  DatabaseInfo,
  ScheduledJob,
  KBCoverage,
  ProviderSummary,
} from './types'

export const AZURE_CONFIG: ProviderConfig = {
  id: 'azure-aca-ipai',
  name: 'Azure Container Apps (IPAI)',
  type: 'azure-aca',
  baseUrl: 'https://ipai-fd-dev-ep-fnh4e8d6gtdhc8ax.z03.azurefd.net',
  projectId: 'rg-ipai-dev',
  enabled: true,
}

export const AZURE_HEALTH: RuntimeHealth = {
  provider: 'azure-aca',
  status: 'healthy',
  checkedAt: new Date().toISOString(),
  components: [
    { name: 'Odoo Web (ACA)', status: 'live', endpoint: 'erp.insightpulseai.com', responseTime: 182, version: '19.0', environment: 'production' },
    { name: 'Keycloak SSO', status: 'live', endpoint: 'auth.insightpulseai.com', responseTime: 95, version: '24.0.4', environment: 'production' },
    { name: 'MCP Coordinator', status: 'live', endpoint: 'mcp.insightpulseai.com', responseTime: 67, environment: 'production' },
    { name: 'OCR Service', status: 'live', endpoint: 'ocr.insightpulseai.com', responseTime: 134, environment: 'production' },
    { name: 'Apache Superset', status: 'live', endpoint: 'superset.insightpulseai.com', responseTime: 210, version: '3.1.0', environment: 'production' },
    { name: 'Plane Project Mgmt', status: 'live', endpoint: 'plane.insightpulseai.com', responseTime: 118, version: '0.22.0', environment: 'production' },
    { name: 'Azure Front Door', status: 'live', endpoint: 'ipai-fd-dev-ep-fnh4e8d6gtdhc8ax.z03.azurefd.net', responseTime: 12, environment: 'edge' },
    { name: 'PostgreSQL Flexible Server', status: 'live', version: '16.6', environment: 'production' },
  ],
}

export const AZURE_BUILDS: BuildInfo[] = [
  { id: 'gh-run-14823', branch: 'main', sha: 'f1a9d3c', status: 'success', startedAt: '2026-03-15T07:45:00Z', finishedAt: '2026-03-15T07:58:12Z', duration: 792, triggeredBy: 'push' },
  { id: 'gh-run-14822', branch: 'feat/azure-aca-deploy', sha: 'e8b2c4f', status: 'success', startedAt: '2026-03-14T19:10:00Z', finishedAt: '2026-03-14T19:22:45Z', duration: 765, triggeredBy: 'push' },
  { id: 'gh-run-14821', branch: 'fix/keycloak-session', sha: 'd7a1e5b', status: 'failure', startedAt: '2026-03-14T15:30:00Z', finishedAt: '2026-03-14T15:39:18Z', duration: 558, triggeredBy: 'push' },
  { id: 'gh-run-14820', branch: 'main', sha: 'c6f3b9a', status: 'success', startedAt: '2026-03-14T11:00:00Z', finishedAt: '2026-03-14T11:13:22Z', duration: 802, triggeredBy: 'merge' },
  { id: 'gh-run-14819', branch: 'feat/superset-dashboards', sha: 'b5e4d8c', status: 'success', startedAt: '2026-03-13T20:15:00Z', finishedAt: '2026-03-13T20:26:40Z', duration: 700, triggeredBy: 'push' },
]

export const AZURE_DEPLOYS: DeployInfo[] = [
  { id: 'aca-deploy-78', environment: 'production', branch: 'main', sha: 'f1a9d3c', status: 'deployed', deployedAt: '2026-03-15T08:02:00Z', version: '19.0.2.1.0', provider: 'azure-aca' },
  { id: 'aca-deploy-77', environment: 'production', branch: 'feat/azure-aca-deploy', sha: 'e8b2c4f', status: 'deployed', deployedAt: '2026-03-14T19:28:00Z', version: '19.0.2.0.1', provider: 'azure-aca' },
  { id: 'aca-deploy-76', environment: 'production', branch: 'fix/keycloak-session', sha: 'd7a1e5b', status: 'failed', deployedAt: '2026-03-14T15:42:00Z', provider: 'azure-aca' },
  { id: 'aca-deploy-75', environment: 'production', branch: 'main', sha: 'c6f3b9a', status: 'deployed', deployedAt: '2026-03-14T11:18:00Z', version: '19.0.2.0.0', provider: 'azure-aca' },
]

export const AZURE_DATABASES: DatabaseInfo[] = [
  { name: 'ipai-odoo-dev-pg (odoo)', environment: 'production', status: 'running', size: '3.1 GB', version: '16.6', lastBackup: '2026-03-15T03:00:00Z', backupFresh: true },
  { name: 'ipai-odoo-dev-pg (odoo_staging)', environment: 'staging', status: 'running', size: '2.2 GB', version: '16.6', lastBackup: '2026-03-15T03:00:00Z', backupFresh: true },
  { name: 'ipai-odoo-dev-pg (odoo_dev)', environment: 'development', status: 'running', size: '1.4 GB', version: '16.6', lastBackup: '2026-03-14T03:00:00Z', backupFresh: true },
  { name: 'ipai-odoo-dev-pg (keycloak)', environment: 'production', status: 'running', size: '480 MB', version: '16.6', lastBackup: '2026-03-15T03:00:00Z', backupFresh: true },
]

export const AZURE_JOBS: ScheduledJob[] = [
  { id: 'gh-wf-1', name: 'CI: Odoo CE Tests', model: 'github-actions', method: 'ci-odoo-ce.yml', schedule: 'On push/PR', status: 'active', lastRun: '2026-03-15T07:45:00Z', provider: 'azure-aca' },
  { id: 'gh-wf-2', name: 'Deploy: Production ACA', model: 'github-actions', method: 'deploy-production.yml', schedule: 'On merge to main', status: 'active', lastRun: '2026-03-15T08:00:00Z', provider: 'azure-aca' },
  { id: 'gh-wf-3', name: 'Health Check: Platform', model: 'github-actions', method: 'health-check.yml', schedule: 'Every 15 min', status: 'active', lastRun: '2026-03-15T09:30:00Z', nextRun: '2026-03-15T09:45:00Z', provider: 'azure-aca' },
  { id: 'n8n-sched-1', name: 'n8n: GitHub Events Export', model: 'n8n-workflow', method: 'github-audit-export', schedule: 'Daily 00:00 UTC', status: 'active', lastRun: '2026-03-15T00:00:00Z', nextRun: '2026-03-16T00:00:00Z', provider: 'azure-aca' },
  { id: 'n8n-sched-2', name: 'n8n: Dependency Digest', model: 'n8n-workflow', method: 'dep-update-digest', schedule: 'Weekly Mon 08:00', status: 'active', lastRun: '2026-03-10T08:00:00Z', nextRun: '2026-03-17T08:00:00Z', provider: 'azure-aca' },
  { id: 'n8n-sched-3', name: 'n8n: BIR Compliance Report', model: 'n8n-workflow', method: 'bir-compliance-snapshot', schedule: 'Monthly 1st 06:00', status: 'active', lastRun: '2026-03-01T06:00:00Z', nextRun: '2026-04-01T06:00:00Z', provider: 'azure-aca' },
  { id: 'pg-cron-1', name: 'PostgreSQL: Automated Backup', model: 'azure-pg-flex', method: 'automated_backup', schedule: 'Daily 03:00 UTC', status: 'active', lastRun: '2026-03-15T03:00:00Z', nextRun: '2026-03-16T03:00:00Z', provider: 'azure-aca' },
]

export const AZURE_KB_COVERAGE: KBCoverage[] = [
  { name: 'Odoo 19 Technical Docs', provider: 'azure-aca', indexed: 7450, total: 8500, freshness: 'fresh', lastUpdated: '2026-03-15T04:00:00Z' },
  { name: 'Azure Platform Docs', provider: 'azure-aca', indexed: 1280, total: 1500, freshness: 'fresh', lastUpdated: '2026-03-14T12:00:00Z' },
  { name: 'IPAI Module Docs', provider: 'azure-aca', indexed: 185, total: 350, freshness: 'stale', lastUpdated: '2026-03-05T06:00:00Z' },
  { name: 'Infrastructure Runbooks', provider: 'azure-aca', indexed: 32, total: 60, freshness: 'stale', lastUpdated: '2026-03-01T06:00:00Z' },
  { name: 'BIR Compliance KB', provider: 'azure-aca', indexed: 95, total: 120, freshness: 'fresh', lastUpdated: '2026-03-13T10:00:00Z' },
]

export function getAzureSummary(): ProviderSummary {
  return {
    config: AZURE_CONFIG,
    health: AZURE_HEALTH,
    builds: AZURE_BUILDS,
    deploys: AZURE_DEPLOYS,
    databases: AZURE_DATABASES,
    jobs: AZURE_JOBS,
    kbCoverage: AZURE_KB_COVERAGE,
  }
}
