export type {
  ProviderConfig,
  RuntimeHealth,
  BuildInfo,
  DeployInfo,
  DatabaseInfo,
  ScheduledJob,
  KBCoverage,
  ProviderSummary,
  RuntimeComponent,
  CapabilityDomain,
  NormalizedService,
} from './types'

export {
  getOdooshSummary,
  ODOOSH_CONFIG,
  ODOOSH_HEALTH,
  ODOOSH_BUILDS,
  ODOOSH_DEPLOYS,
  ODOOSH_DATABASES,
  ODOOSH_JOBS,
  ODOOSH_KB_COVERAGE,
} from './odoosh-fixtures'

export {
  getAzureSummary,
  AZURE_CONFIG,
  AZURE_HEALTH,
  AZURE_BUILDS,
  AZURE_DEPLOYS,
  AZURE_DATABASES,
  AZURE_JOBS,
  AZURE_KB_COVERAGE,
} from './azure-fixtures'

export {
  getMicrosoftCloudSummary,
  MSCLOUD_CONFIG,
  MSCLOUD_SERVICES,
  MSCLOUD_HEALTH,
  MSCLOUD_BUILDS,
  MSCLOUD_DEPLOYS,
  MSCLOUD_JOBS,
  MSCLOUD_KB_COVERAGE,
  getDomainLabel,
  getDomainMaturity,
} from './microsoft-cloud-fixtures'
