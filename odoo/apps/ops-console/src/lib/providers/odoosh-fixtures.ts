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

export const ODOOSH_CONFIG: ProviderConfig = {
  id: 'odoosh-ipai',
  name: 'Odoo.sh (IPAI)',
  type: 'odoosh',
  baseUrl: 'https://ipai.odoo.com',
  projectId: 'ipai-production',
  enabled: true,
}

export const ODOOSH_HEALTH: RuntimeHealth = {
  provider: 'odoosh',
  status: 'healthy',
  checkedAt: new Date().toISOString(),
  components: [
    { name: 'Odoo Web', status: 'live', endpoint: 'ipai.odoo.com', responseTime: 245, version: '19.0', environment: 'production' },
    { name: 'Odoo Longpolling', status: 'live', endpoint: 'ipai.odoo.com/longpolling', responseTime: 52 },
    { name: 'PostgreSQL', status: 'live', version: '16.2', environment: 'production' },
    { name: 'Worker Pool', status: 'live', environment: 'production' },
    { name: 'Cron Worker', status: 'live', environment: 'production' },
    { name: 'Staging', status: 'degraded', endpoint: 'ipai-staging.odoo.com', responseTime: 890, environment: 'staging' },
  ],
}

export const ODOOSH_BUILDS: BuildInfo[] = [
  { id: 'build-101', branch: 'main', sha: 'a3f9c2e', status: 'success', startedAt: '2026-03-15T08:00:00Z', finishedAt: '2026-03-15T08:12:34Z', duration: 754, triggeredBy: 'push' },
  { id: 'build-100', branch: 'feat/copilot-tools', sha: 'b7d4e1a', status: 'success', startedAt: '2026-03-14T16:30:00Z', finishedAt: '2026-03-14T16:41:22Z', duration: 682, triggeredBy: 'push' },
  { id: 'build-99', branch: 'fix/auth-flow', sha: 'c2e8f3b', status: 'failure', startedAt: '2026-03-14T14:15:00Z', finishedAt: '2026-03-14T14:23:45Z', duration: 525, triggeredBy: 'push' },
  { id: 'build-98', branch: 'main', sha: 'd1a5b6c', status: 'success', startedAt: '2026-03-14T10:00:00Z', finishedAt: '2026-03-14T10:11:18Z', duration: 678, triggeredBy: 'merge' },
  { id: 'build-97', branch: 'feat/kb-search', sha: 'e4f7a9d', status: 'success', startedAt: '2026-03-13T22:00:00Z', finishedAt: '2026-03-13T22:10:55Z', duration: 655, triggeredBy: 'push' },
]

export const ODOOSH_DEPLOYS: DeployInfo[] = [
  { id: 'deploy-51', environment: 'production', branch: 'main', sha: 'a3f9c2e', status: 'deployed', deployedAt: '2026-03-15T08:15:00Z', version: '19.0.2.0.0', provider: 'odoosh' },
  { id: 'deploy-50', environment: 'staging', branch: 'feat/copilot-tools', sha: 'b7d4e1a', status: 'deployed', deployedAt: '2026-03-14T16:45:00Z', version: '19.0.2.0.0-rc1', provider: 'odoosh' },
  { id: 'deploy-49', environment: 'staging', branch: 'fix/auth-flow', sha: 'c2e8f3b', status: 'failed', deployedAt: '2026-03-14T14:30:00Z', provider: 'odoosh' },
  { id: 'deploy-48', environment: 'production', branch: 'main', sha: 'd1a5b6c', status: 'deployed', deployedAt: '2026-03-14T10:15:00Z', version: '19.0.1.9.0', provider: 'odoosh' },
]

export const ODOOSH_DATABASES: DatabaseInfo[] = [
  { name: 'ipai-production', environment: 'production', status: 'running', size: '2.4 GB', version: '16.2', lastBackup: '2026-03-15T02:00:00Z', backupFresh: true },
  { name: 'ipai-staging', environment: 'staging', status: 'running', size: '1.8 GB', version: '16.2', lastBackup: '2026-03-15T02:00:00Z', backupFresh: true },
  { name: 'ipai-dev', environment: 'development', status: 'running', size: '890 MB', version: '16.2', lastBackup: '2026-03-14T02:00:00Z', backupFresh: true },
]

export const ODOOSH_JOBS: ScheduledJob[] = [
  { id: 'osh-cron-1', name: 'Mail: Fetchmail Service', model: 'fetchmail.server', method: 'fetch_mail', schedule: 'Every 5 min', status: 'active', lastRun: '2026-03-15T09:35:00Z', nextRun: '2026-03-15T09:40:00Z', provider: 'odoosh' },
  { id: 'osh-cron-2', name: 'Sales: Generate Recurring Invoices', model: 'sale.subscription', method: '_cron_recurring_create_invoice', schedule: 'Daily 01:00 UTC', status: 'active', lastRun: '2026-03-15T01:00:00Z', nextRun: '2026-03-16T01:00:00Z', provider: 'odoosh' },
  { id: 'osh-cron-3', name: 'Digest: Send Digests', model: 'digest.digest', method: '_cron_send_digest_email', schedule: 'Weekly Mon 06:00', status: 'active', lastRun: '2026-03-10T06:00:00Z', nextRun: '2026-03-17T06:00:00Z', provider: 'odoosh' },
  { id: 'osh-cron-4', name: 'Copilot: Nightly Healthcheck', model: 'ipai.foundry.service', method: 'nightly_healthcheck', schedule: 'Daily 02:00 UTC', status: 'active', lastRun: '2026-03-15T02:00:00Z', nextRun: '2026-03-16T02:00:00Z', provider: 'odoosh' },
  { id: 'osh-cron-5', name: 'Base: Update Notification', model: 'publisher_warranty.contract', method: 'update_notification', schedule: 'Weekly', status: 'paused', provider: 'odoosh' },
  { id: 'osh-cron-6', name: 'HR: Payroll Computation', model: 'hr.payslip', method: '_cron_compute_payslip', schedule: 'Monthly 1st', status: 'active', lastRun: '2026-03-01T00:00:00Z', nextRun: '2026-04-01T00:00:00Z', provider: 'odoosh' },
]

export const ODOOSH_KB_COVERAGE: KBCoverage[] = [
  { name: 'Odoo 19 Technical Docs', provider: 'odoosh', indexed: 7224, total: 8500, freshness: 'fresh', lastUpdated: '2026-03-15T06:00:00Z' },
  { name: 'Odoo.sh Operations', provider: 'odoosh', indexed: 450, total: 600, freshness: 'fresh', lastUpdated: '2026-03-14T06:00:00Z' },
  { name: 'IPAI Module Docs', provider: 'odoosh', indexed: 120, total: 350, freshness: 'stale', lastUpdated: '2026-03-01T06:00:00Z' },
  { name: 'Deployment Runbooks', provider: 'odoosh', indexed: 0, total: 45, freshness: 'missing' },
]

export function getOdooshSummary(): ProviderSummary {
  return {
    config: ODOOSH_CONFIG,
    health: ODOOSH_HEALTH,
    builds: ODOOSH_BUILDS,
    deploys: ODOOSH_DEPLOYS,
    databases: ODOOSH_DATABASES,
    jobs: ODOOSH_JOBS,
    kbCoverage: ODOOSH_KB_COVERAGE,
  }
}
