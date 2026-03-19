import type {
  ProviderConfig,
  NormalizedService,
  RuntimeHealth,
  BuildInfo,
  DeployInfo,
  ScheduledJob,
  KBCoverage,
  ProviderSummary,
  CapabilityDomain,
} from './types'

// --- Config ---

export const MSCLOUD_CONFIG: ProviderConfig = {
  id: 'microsoft-cloud-ipai',
  name: 'Microsoft Cloud (IPAI)',
  type: 'microsoft-cloud',
  baseUrl: 'https://portal.azure.com',
  projectId: 'ipai-tenant',
  enabled: true,
}

// --- Normalized Services (15 services across 7 domains) ---

export const MSCLOUD_SERVICES: NormalizedService[] = [
  // runtime
  {
    id: 'mscloud-azure',
    provider: 'microsoft-cloud',
    domain: 'runtime',
    displayName: 'Azure',
    category: 'Compute',
    secondaryCategories: ['Containers', 'Web', 'Networking', 'Management and Governance'],
    isExternalProvider: false,
    deploymentSurface: 'Azure Container Apps',
    environment: 'production',
    status: 'operational',
    maturityScore: 0.85,
    lastSync: '2026-03-15T09:00:00Z',
    endpoint: 'https://management.azure.com',
    relatedJobs: ['gh-wf-1', 'gh-wf-2'],
    relatedDeploys: ['aca-deploy-78'],
    kbCoverage: ['Azure Platform Docs'],
  },

  // ai_agents
  {
    id: 'mscloud-ai-foundry',
    provider: 'microsoft-cloud',
    domain: 'ai_agents',
    displayName: 'AI Foundry',
    category: 'AI + Machine Learning',
    isExternalProvider: false,
    deploymentSurface: 'Azure AI Foundry',
    environment: 'production',
    status: 'operational',
    maturityScore: 0.65,
    lastSync: '2026-03-15T08:45:00Z',
    endpoint: 'https://ai.azure.com',
    relatedJobs: ['ai-foundry-eval-1'],
    kbCoverage: ['AI Foundry Docs'],
  },
  {
    id: 'mscloud-copilot-studio',
    provider: 'microsoft-cloud',
    domain: 'ai_agents',
    displayName: 'Copilot Studio',
    category: 'AI + Machine Learning',
    isExternalProvider: false,
    deploymentSurface: 'Microsoft 365',
    environment: 'production',
    status: 'partial',
    maturityScore: 0.45,
    lastSync: '2026-03-15T08:30:00Z',
    endpoint: 'https://copilotstudio.microsoft.com',
    kbCoverage: ['Copilot Studio Docs'],
  },

  // dev_delivery
  {
    id: 'mscloud-github',
    provider: 'microsoft-cloud',
    domain: 'dev_delivery',
    displayName: 'GitHub',
    category: 'Developer Tools',
    secondaryCategories: ['DevOps'],
    isExternalProvider: false,
    deploymentSurface: 'GitHub Cloud',
    environment: 'production',
    status: 'operational',
    maturityScore: 0.90,
    lastSync: '2026-03-15T09:15:00Z',
    endpoint: 'https://github.com/Insightpulseai',
    relatedJobs: ['gh-wf-1', 'gh-wf-2', 'gh-wf-3'],
    relatedDeploys: ['gh-deploy-42', 'gh-deploy-41'],
    kbCoverage: ['GitHub Actions Docs', 'GitHub Enterprise Docs'],
  },
  {
    id: 'mscloud-devops',
    provider: 'microsoft-cloud',
    domain: 'dev_delivery',
    displayName: 'Azure DevOps',
    category: 'DevOps',
    isExternalProvider: false,
    deploymentSurface: 'Azure DevOps Services',
    environment: 'production',
    status: 'operational',
    maturityScore: 0.75,
    lastSync: '2026-03-15T08:50:00Z',
    endpoint: 'https://dev.azure.com/insightpulseai',
    relatedJobs: ['ado-pipeline-1', 'ado-pipeline-2'],
    kbCoverage: ['Azure DevOps Docs'],
  },
  {
    id: 'mscloud-vscode',
    provider: 'microsoft-cloud',
    domain: 'dev_delivery',
    displayName: 'VS Code',
    category: 'Developer Tools',
    isExternalProvider: false,
    deploymentSurface: 'Desktop / Web',
    environment: 'production',
    status: 'operational',
    maturityScore: 0.95,
    lastSync: '2026-03-15T09:00:00Z',
    kbCoverage: ['VS Code Extension Docs'],
  },

  // identity_security
  {
    id: 'mscloud-entra',
    provider: 'microsoft-cloud',
    domain: 'identity_security',
    displayName: 'Entra ID',
    category: 'Identity',
    isExternalProvider: false,
    deploymentSurface: 'Microsoft Entra',
    environment: 'production',
    status: 'operational',
    maturityScore: 0.80,
    lastSync: '2026-03-15T09:10:00Z',
    endpoint: 'https://entra.microsoft.com',
    kbCoverage: ['Entra ID Docs'],
  },
  {
    id: 'mscloud-defender',
    provider: 'microsoft-cloud',
    domain: 'identity_security',
    displayName: 'Defender for Cloud',
    category: 'Security',
    isExternalProvider: false,
    deploymentSurface: 'Azure Security Center',
    environment: 'production',
    status: 'partial',
    maturityScore: 0.55,
    lastSync: '2026-03-15T08:20:00Z',
    endpoint: 'https://security.microsoft.com',
    kbCoverage: ['Defender Docs'],
  },
  {
    id: 'mscloud-intune',
    provider: 'microsoft-cloud',
    domain: 'identity_security',
    displayName: 'Intune',
    category: 'Management and Governance',
    secondaryCategories: ['Security'],
    isExternalProvider: false,
    deploymentSurface: 'Microsoft Intune',
    environment: 'production',
    status: 'unconfigured',
    maturityScore: 0.20,
    lastSync: '2026-03-15T06:00:00Z',
    endpoint: 'https://intune.microsoft.com',
    kbCoverage: ['Intune Docs'],
  },

  // governance_compliance
  {
    id: 'mscloud-purview',
    provider: 'microsoft-cloud',
    domain: 'governance_compliance',
    displayName: 'Purview',
    category: 'Management and Governance',
    secondaryCategories: ['Security'],
    isExternalProvider: false,
    deploymentSurface: 'Microsoft Purview',
    environment: 'production',
    status: 'partial',
    maturityScore: 0.40,
    lastSync: '2026-03-15T07:30:00Z',
    endpoint: 'https://purview.microsoft.com',
    kbCoverage: ['Purview Docs'],
  },
  {
    id: 'mscloud-m365-admin',
    provider: 'microsoft-cloud',
    domain: 'governance_compliance',
    displayName: 'Microsoft 365 Admin',
    category: 'Management and Governance',
    isExternalProvider: false,
    deploymentSurface: 'Microsoft 365',
    environment: 'production',
    status: 'operational',
    maturityScore: 0.70,
    lastSync: '2026-03-15T08:00:00Z',
    endpoint: 'https://admin.microsoft.com',
    kbCoverage: ['M365 Admin Docs'],
  },

  // data_analytics
  {
    id: 'mscloud-data-explorer',
    provider: 'microsoft-cloud',
    domain: 'data_analytics',
    displayName: 'Data Explorer',
    category: 'Analytics',
    isExternalProvider: false,
    deploymentSurface: 'Azure Data Explorer',
    environment: 'production',
    status: 'operational',
    maturityScore: 0.60,
    lastSync: '2026-03-15T08:15:00Z',
    endpoint: 'https://dataexplorer.azure.com',
    kbCoverage: ['Data Explorer Docs'],
  },
  {
    id: 'mscloud-fabric',
    provider: 'microsoft-cloud',
    domain: 'data_analytics',
    displayName: 'Fabric',
    category: 'Analytics',
    isExternalProvider: false,
    deploymentSurface: 'Microsoft Fabric',
    environment: 'production',
    status: 'unconfigured',
    maturityScore: 0.15,
    lastSync: '2026-03-14T12:00:00Z',
    kbCoverage: ['Fabric Docs'],
  },

  // automation
  {
    id: 'mscloud-power-automate',
    provider: 'microsoft-cloud',
    domain: 'automation',
    displayName: 'Power Automate',
    category: 'Integration',
    isExternalProvider: false,
    deploymentSurface: 'Power Platform',
    environment: 'production',
    status: 'partial',
    maturityScore: 0.50,
    lastSync: '2026-03-15T08:40:00Z',
    endpoint: 'https://make.powerautomate.com',
    relatedJobs: ['pa-flow-1', 'pa-flow-2'],
    kbCoverage: ['Power Automate Docs'],
  },
  {
    id: 'mscloud-power-platform',
    provider: 'microsoft-cloud',
    domain: 'automation',
    displayName: 'Power Platform',
    category: 'Integration',
    isExternalProvider: false,
    deploymentSurface: 'Power Platform',
    environment: 'production',
    status: 'partial',
    maturityScore: 0.35,
    lastSync: '2026-03-15T07:00:00Z',
    endpoint: 'https://admin.powerplatform.microsoft.com',
    kbCoverage: ['Power Platform Docs'],
  },
]

// --- Aggregate Health ---

function computeAggregateStatus(): 'healthy' | 'degraded' | 'down' | 'unconfigured' {
  const statuses = MSCLOUD_SERVICES.map((s) => s.status)
  if (statuses.every((s) => s === 'operational')) return 'healthy'
  if (statuses.some((s) => s === 'down')) return 'down'
  return 'degraded'
}

export const MSCLOUD_HEALTH: RuntimeHealth = {
  provider: 'microsoft-cloud',
  status: computeAggregateStatus(),
  checkedAt: new Date().toISOString(),
  components: MSCLOUD_SERVICES.map((svc) => ({
    name: svc.displayName,
    status: svc.status,
    endpoint: svc.endpoint,
    environment: svc.environment,
  })),
}

// --- Builds (GitHub Actions + Azure DevOps Pipelines) ---

export const MSCLOUD_BUILDS: BuildInfo[] = [
  { id: 'gh-run-14823', branch: 'main', sha: 'f1a9d3c', status: 'success', startedAt: '2026-03-15T07:45:00Z', finishedAt: '2026-03-15T07:58:12Z', duration: 792, triggeredBy: 'push' },
  { id: 'gh-run-14822', branch: 'feat/ms-cloud-provider', sha: 'a2c4e6f', status: 'success', startedAt: '2026-03-14T22:10:00Z', finishedAt: '2026-03-14T22:21:30Z', duration: 690, triggeredBy: 'push' },
  { id: 'ado-run-5018', branch: 'main', sha: 'f1a9d3c', status: 'success', startedAt: '2026-03-15T08:00:00Z', finishedAt: '2026-03-15T08:14:22Z', duration: 862, triggeredBy: 'pipeline-trigger' },
  { id: 'ado-run-5017', branch: 'release/2.1', sha: 'b3d5c7e', status: 'success', startedAt: '2026-03-14T16:30:00Z', finishedAt: '2026-03-14T16:42:18Z', duration: 738, triggeredBy: 'manual' },
  { id: 'gh-run-14820', branch: 'main', sha: 'c6f3b9a', status: 'success', startedAt: '2026-03-14T11:00:00Z', finishedAt: '2026-03-14T11:13:22Z', duration: 802, triggeredBy: 'merge' },
]

// --- Deploys (Azure deployments + GitHub deploys) ---

export const MSCLOUD_DEPLOYS: DeployInfo[] = [
  { id: 'aca-deploy-78', environment: 'production', branch: 'main', sha: 'f1a9d3c', status: 'deployed', deployedAt: '2026-03-15T08:02:00Z', version: '19.0.2.1.0', provider: 'microsoft-cloud' },
  { id: 'gh-deploy-42', environment: 'production', branch: 'main', sha: 'f1a9d3c', status: 'deployed', deployedAt: '2026-03-15T08:05:00Z', version: '2.1.0', provider: 'microsoft-cloud' },
  { id: 'gh-deploy-41', environment: 'staging', branch: 'feat/ms-cloud-provider', sha: 'a2c4e6f', status: 'deployed', deployedAt: '2026-03-14T22:25:00Z', version: '2.1.0-rc.1', provider: 'microsoft-cloud' },
  { id: 'ado-deploy-312', environment: 'production', branch: 'release/2.1', sha: 'b3d5c7e', status: 'deployed', deployedAt: '2026-03-14T16:50:00Z', version: '2.1.0-beta.3', provider: 'microsoft-cloud' },
]

// --- Scheduled Jobs (Power Automate flows, DevOps pipelines, GitHub Actions) ---

export const MSCLOUD_JOBS: ScheduledJob[] = [
  { id: 'gh-wf-1', name: 'CI: Odoo CE Tests', model: 'github-actions', method: 'ci-odoo-ce.yml', schedule: 'On push/PR', status: 'active', lastRun: '2026-03-15T07:45:00Z', provider: 'microsoft-cloud' },
  { id: 'gh-wf-2', name: 'Deploy: Production ACA', model: 'github-actions', method: 'deploy-production.yml', schedule: 'On merge to main', status: 'active', lastRun: '2026-03-15T08:00:00Z', provider: 'microsoft-cloud' },
  { id: 'gh-wf-3', name: 'Health Check: Platform', model: 'github-actions', method: 'health-check.yml', schedule: 'Every 15 min', status: 'active', lastRun: '2026-03-15T09:30:00Z', nextRun: '2026-03-15T09:45:00Z', provider: 'microsoft-cloud' },
  { id: 'ado-pipeline-1', name: 'ADO: Infrastructure Validation', model: 'azure-devops', method: 'infra-validate.yml', schedule: 'On PR', status: 'active', lastRun: '2026-03-15T08:00:00Z', provider: 'microsoft-cloud' },
  { id: 'ado-pipeline-2', name: 'ADO: Release Pipeline', model: 'azure-devops', method: 'release-pipeline.yml', schedule: 'On tag', status: 'active', lastRun: '2026-03-14T16:30:00Z', provider: 'microsoft-cloud' },
  { id: 'pa-flow-1', name: 'Power Automate: Approval Routing', model: 'power-automate', method: 'approval-routing-flow', schedule: 'Event-driven', status: 'active', lastRun: '2026-03-15T09:12:00Z', provider: 'microsoft-cloud' },
  { id: 'pa-flow-2', name: 'Power Automate: License Sync', model: 'power-automate', method: 'license-sync-flow', schedule: 'Daily 01:00 UTC', status: 'active', lastRun: '2026-03-15T01:00:00Z', nextRun: '2026-03-16T01:00:00Z', provider: 'microsoft-cloud' },
  { id: 'ai-foundry-eval-1', name: 'AI Foundry: Model Eval', model: 'ai-foundry', method: 'model-evaluation', schedule: 'Weekly Mon 04:00', status: 'active', lastRun: '2026-03-10T04:00:00Z', nextRun: '2026-03-17T04:00:00Z', provider: 'microsoft-cloud' },
]

// --- KB Coverage (docs for each domain) ---

export const MSCLOUD_KB_COVERAGE: KBCoverage[] = [
  { name: 'Azure Platform Docs', provider: 'microsoft-cloud', indexed: 1280, total: 1500, freshness: 'fresh', lastUpdated: '2026-03-14T12:00:00Z' },
  { name: 'GitHub Enterprise Docs', provider: 'microsoft-cloud', indexed: 3200, total: 3500, freshness: 'fresh', lastUpdated: '2026-03-15T06:00:00Z' },
  { name: 'GitHub Actions Docs', provider: 'microsoft-cloud', indexed: 890, total: 1000, freshness: 'fresh', lastUpdated: '2026-03-15T06:00:00Z' },
  { name: 'Azure DevOps Docs', provider: 'microsoft-cloud', indexed: 620, total: 800, freshness: 'stale', lastUpdated: '2026-03-05T08:00:00Z' },
  { name: 'Entra ID Docs', provider: 'microsoft-cloud', indexed: 450, total: 600, freshness: 'fresh', lastUpdated: '2026-03-13T10:00:00Z' },
  { name: 'Defender Docs', provider: 'microsoft-cloud', indexed: 180, total: 400, freshness: 'stale', lastUpdated: '2026-03-01T06:00:00Z' },
  { name: 'AI Foundry Docs', provider: 'microsoft-cloud', indexed: 310, total: 500, freshness: 'fresh', lastUpdated: '2026-03-14T15:00:00Z' },
  { name: 'Power Platform Docs', provider: 'microsoft-cloud', indexed: 220, total: 450, freshness: 'stale', lastUpdated: '2026-03-03T12:00:00Z' },
  { name: 'Purview Docs', provider: 'microsoft-cloud', indexed: 95, total: 300, freshness: 'stale', lastUpdated: '2026-02-28T06:00:00Z' },
  { name: 'Data Explorer Docs', provider: 'microsoft-cloud', indexed: 340, total: 400, freshness: 'fresh', lastUpdated: '2026-03-12T09:00:00Z' },
  { name: 'Fabric Docs', provider: 'microsoft-cloud', indexed: 50, total: 350, freshness: 'missing', lastUpdated: '2026-02-15T06:00:00Z' },
  { name: 'VS Code Extension Docs', provider: 'microsoft-cloud', indexed: 720, total: 750, freshness: 'fresh', lastUpdated: '2026-03-14T18:00:00Z' },
  { name: 'Copilot Studio Docs', provider: 'microsoft-cloud', indexed: 140, total: 250, freshness: 'stale', lastUpdated: '2026-03-04T10:00:00Z' },
  { name: 'Intune Docs', provider: 'microsoft-cloud', indexed: 30, total: 200, freshness: 'missing', lastUpdated: '2026-02-10T06:00:00Z' },
  { name: 'M365 Admin Docs', provider: 'microsoft-cloud', indexed: 380, total: 500, freshness: 'fresh', lastUpdated: '2026-03-13T14:00:00Z' },
  { name: 'Power Automate Docs', provider: 'microsoft-cloud', indexed: 260, total: 350, freshness: 'stale', lastUpdated: '2026-03-02T08:00:00Z' },
]

// --- Helpers ---

const DOMAIN_LABELS: Record<CapabilityDomain, string> = {
  runtime: 'Runtime',
  ai_agents: 'AI Agents',
  dev_delivery: 'Dev & Delivery',
  identity_security: 'Identity & Security',
  governance_compliance: 'Governance & Compliance',
  data_analytics: 'Data & Analytics',
  automation: 'Automation',
}

export function getDomainLabel(domain: CapabilityDomain): string {
  return DOMAIN_LABELS[domain] ?? domain
}

export function getDomainMaturity(services: NormalizedService[]): Record<CapabilityDomain, number> {
  const result = {} as Record<CapabilityDomain, number>
  const counts = {} as Record<CapabilityDomain, number>

  for (const svc of services) {
    const score = svc.maturityScore ?? 0
    if (result[svc.domain] === undefined) {
      result[svc.domain] = 0
      counts[svc.domain] = 0
    }
    result[svc.domain] += score
    counts[svc.domain] += 1
  }

  for (const domain of Object.keys(result) as CapabilityDomain[]) {
    result[domain] = counts[domain] > 0 ? result[domain] / counts[domain] : 0
  }

  return result
}

// --- Summary ---

export function getMicrosoftCloudSummary(): ProviderSummary & { services: NormalizedService[] } {
  return {
    config: MSCLOUD_CONFIG,
    health: MSCLOUD_HEALTH,
    builds: MSCLOUD_BUILDS,
    deploys: MSCLOUD_DEPLOYS,
    databases: [],
    jobs: MSCLOUD_JOBS,
    kbCoverage: MSCLOUD_KB_COVERAGE,
    services: MSCLOUD_SERVICES,
  }
}
