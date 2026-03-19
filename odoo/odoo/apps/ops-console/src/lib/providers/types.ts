// Provider identity
export interface ProviderConfig {
  id: string
  name: string
  type: 'azure-aca' | 'odoosh' | 'microsoft-cloud' | 'mock'
  baseUrl?: string
  projectId?: string
  enabled: boolean
}

// Capability domains for Microsoft Cloud provider
export type CapabilityDomain =
  | 'runtime'
  | 'ai_agents'
  | 'dev_delivery'
  | 'identity_security'
  | 'governance_compliance'
  | 'data_analytics'
  | 'automation'

// Azure canonical product taxonomy
export type AzureCategory =
  | 'AI + Machine Learning'
  | 'Analytics'
  | 'Compute'
  | 'Containers'
  | 'Databases'
  | 'Developer Tools'
  | 'DevOps'
  | 'Hybrid + multicloud'
  | 'Identity'
  | 'Integration'
  | 'Internet of Things'
  | 'Management and Governance'
  | 'Media'
  | 'Migration'
  | 'Mixed reality'
  | 'Mobile'
  | 'Networking'
  | 'Security'
  | 'Storage'
  | 'Virtual desktop infrastructure'
  | 'Web'
  | 'Unclassified'

// Normalized service representation across providers
export interface NormalizedService {
  id: string
  provider: string  // 'microsoft-cloud' | 'azure-aca' | 'odoosh'
  domain: CapabilityDomain
  displayName: string
  environment: string
  status: 'operational' | 'degraded' | 'down' | 'unconfigured' | 'partial'
  maturityScore?: number  // 0-1
  lastSync?: string
  endpoint?: string
  relatedJobs?: string[]
  relatedDeploys?: string[]
  kbCoverage?: string[]
  // Azure canonical taxonomy
  category?: AzureCategory
  secondaryCategories?: AzureCategory[]
  isExternalProvider?: boolean
  deploymentSurface?: string
  tags?: string[]
}

// Normalized domain contracts
export interface RuntimeHealth {
  provider: string
  status: 'healthy' | 'degraded' | 'down' | 'unconfigured'
  checkedAt: string
  components: RuntimeComponent[]
}

export interface RuntimeComponent {
  name: string
  status: string
  endpoint?: string
  responseTime?: number
  version?: string
  environment?: string
}

export interface BuildInfo {
  id: string
  branch: string
  sha: string
  status: 'success' | 'failure' | 'building' | 'queued' | 'cancelled'
  startedAt: string
  finishedAt?: string
  duration?: number
  triggeredBy?: string
}

export interface DeployInfo {
  id: string
  environment: string
  branch: string
  sha: string
  status: 'deployed' | 'deploying' | 'failed' | 'queued' | 'rolled-back'
  deployedAt: string
  version?: string
  provider: string
}

export interface DatabaseInfo {
  name: string
  environment: string
  status: 'running' | 'stopped' | 'maintenance' | 'error'
  size?: string
  version?: string
  lastBackup?: string
  backupFresh: boolean
}

export interface ScheduledJob {
  id: string
  name: string
  model?: string
  method?: string
  schedule: string
  status: 'active' | 'paused' | 'error'
  lastRun?: string
  nextRun?: string
  provider: string
}

export interface KBCoverage {
  name: string
  provider: string
  indexed: number
  total: number
  freshness: 'fresh' | 'stale' | 'missing'
  lastUpdated?: string
}

export interface ProviderSummary {
  config: ProviderConfig
  health: RuntimeHealth
  builds: BuildInfo[]
  deploys: DeployInfo[]
  databases: DatabaseInfo[]
  jobs: ScheduledJob[]
  kbCoverage: KBCoverage[]
}
