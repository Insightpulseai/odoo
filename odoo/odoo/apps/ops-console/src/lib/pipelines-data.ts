/**
 * Integration & ETL pipeline registry.
 *
 * Every integration pipeline in the platform — whether actively flowing,
 * planned, or unconfigured — is registered here with its execution engine,
 * medallion stage, flow status, and last execution metadata.
 */

export type PipelineEngine =
  | 'n8n'
  | 'supabase-edge'
  | 'supabase-pg-cron'
  | 'github-actions'
  | 'azure-data-factory'
  | 'azure-logic-apps'
  | 'power-automate'
  | 'databricks'
  | 'spark'
  | 'dbt'
  | 'airbyte'
  | 'fivetran'
  | 'fabric-pipeline'
  | 'iceberg'
  | 'custom'

export type PipelineStatus =
  | 'flowing'        // actively running on schedule
  | 'idle'           // configured but not currently running
  | 'error'          // last run failed
  | 'paused'         // manually paused
  | 'unconfigured'   // registered but not wired
  | 'planned'        // on roadmap, not yet built
  | 'deprecated'     // being phased out

export type MedallionStage = 'ingest' | 'bronze' | 'silver' | 'gold' | 'platinum' | 'n/a'

export type PipelineCategory =
  | 'etl'            // extract-transform-load
  | 'sync'           // bidirectional sync
  | 'webhook'        // event-driven webhook relay
  | 'ci-cd'          // build/deploy pipeline
  | 'automation'     // business process automation
  | 'ai-ml'          // model training / inference
  | 'observability'  // monitoring / alerting

export interface Pipeline {
  id: string
  name: string
  description: string
  engine: PipelineEngine
  category: PipelineCategory
  status: PipelineStatus
  medallionStage: MedallionStage
  source: string
  destination: string
  schedule: string
  lastRun: string | null
  lastStatus: 'success' | 'failure' | 'running' | null
  lastDuration: number | null // seconds
  nextRun: string | null
  owner: string
  tags: string[]
}

// ============================================================
// FULL PIPELINE REGISTRY
// ============================================================

export const PIPELINES: Pipeline[] = [
  // ---- n8n workflows (flowing) ----
  {
    id: 'n8n-github-odoo-sync',
    name: 'GitHub → Odoo Task Sync',
    description: 'Creates Odoo project.task from GitHub issues/PRs via pulser-hub webhooks',
    engine: 'n8n',
    category: 'sync',
    status: 'flowing',
    medallionStage: 'bronze',
    source: 'GitHub (pulser-hub)',
    destination: 'Odoo CE',
    schedule: 'Event-driven (webhook)',
    lastRun: '2026-03-15T09:12:00Z',
    lastStatus: 'success',
    lastDuration: 3,
    nextRun: null,
    owner: 'Platform',
    tags: ['n8n', 'github', 'odoo'],
  },
  {
    id: 'n8n-slack-alerts',
    name: 'CI Failure → Slack Alert',
    description: 'Routes GitHub Actions failure events to Slack #ops-alerts channel',
    engine: 'n8n',
    category: 'webhook',
    status: 'flowing',
    medallionStage: 'n/a',
    source: 'GitHub Actions',
    destination: 'Slack',
    schedule: 'Event-driven (webhook)',
    lastRun: '2026-03-15T07:58:00Z',
    lastStatus: 'success',
    lastDuration: 1,
    nextRun: null,
    owner: 'Platform',
    tags: ['n8n', 'slack', 'alerting'],
  },
  {
    id: 'n8n-service-matrix-sync',
    name: 'Service Matrix Sync',
    description: 'Syncs Azure service health into ops-console service registry',
    engine: 'n8n',
    category: 'sync',
    status: 'flowing',
    medallionStage: 'silver',
    source: 'Azure Resource Manager',
    destination: 'Supabase (ops schema)',
    schedule: 'Daily 03:00 UTC',
    lastRun: '2026-03-15T03:00:00Z',
    lastStatus: 'success',
    lastDuration: 45,
    nextRun: '2026-03-16T03:00:00Z',
    owner: 'Platform',
    tags: ['n8n', 'azure', 'sync'],
  },
  {
    id: 'n8n-actions-audit',
    name: 'GitHub Actions → Supabase Audit',
    description: 'Daily export of Actions run logs to Supabase audit_logs table',
    engine: 'n8n',
    category: 'etl',
    status: 'flowing',
    medallionStage: 'bronze',
    source: 'GitHub Actions API',
    destination: 'Supabase (audit_logs)',
    schedule: 'Daily 02:00 UTC',
    lastRun: '2026-03-15T02:00:00Z',
    lastStatus: 'success',
    lastDuration: 120,
    nextRun: '2026-03-16T02:00:00Z',
    owner: 'Platform',
    tags: ['n8n', 'github', 'audit'],
  },
  {
    id: 'n8n-dep-digest',
    name: 'Dependency Update Digest',
    description: 'Weekly digest of Dependabot PRs emailed to stakeholders',
    engine: 'n8n',
    category: 'automation',
    status: 'flowing',
    medallionStage: 'n/a',
    source: 'GitHub (Dependabot)',
    destination: 'Zoho Mail',
    schedule: 'Weekly Mon 08:00 UTC',
    lastRun: '2026-03-10T08:00:00Z',
    lastStatus: 'success',
    lastDuration: 15,
    nextRun: '2026-03-17T08:00:00Z',
    owner: 'Platform',
    tags: ['n8n', 'email', 'deps'],
  },

  // ---- Supabase ETL ----
  {
    id: 'supa-edge-odoo-mirror',
    name: 'Odoo → Supabase Mirror',
    description: 'Edge Function receives Odoo webhook payloads, upserts into odoo_mirror schema',
    engine: 'supabase-edge',
    category: 'sync',
    status: 'flowing',
    medallionStage: 'bronze',
    source: 'Odoo CE (webhooks)',
    destination: 'Supabase (odoo_mirror)',
    schedule: 'Event-driven',
    lastRun: '2026-03-15T09:30:00Z',
    lastStatus: 'success',
    lastDuration: 2,
    nextRun: null,
    owner: 'Data Team',
    tags: ['supabase', 'odoo', 'mirror'],
  },
  {
    id: 'supa-pgcron-gold-views',
    name: 'Refresh Gold Materialized Views',
    description: 'pg_cron job refreshes gold-tier materialized views for BI dashboards',
    engine: 'supabase-pg-cron',
    category: 'etl',
    status: 'flowing',
    medallionStage: 'gold',
    source: 'Supabase (silver schema)',
    destination: 'Supabase (gold views)',
    schedule: 'Daily 02:00 UTC',
    lastRun: '2026-03-15T02:00:00Z',
    lastStatus: 'success',
    lastDuration: 38,
    nextRun: '2026-03-16T02:00:00Z',
    owner: 'Data Team',
    tags: ['supabase', 'pg_cron', 'medallion'],
  },
  {
    id: 'supa-edge-mcp-enqueue',
    name: 'MCP Job Enqueue',
    description: 'Edge Function for mcp_jobs.enqueue_job RPC — task bus entry point',
    engine: 'supabase-edge',
    category: 'automation',
    status: 'flowing',
    medallionStage: 'n/a',
    source: 'MCP Clients (Odoo, n8n, agents)',
    destination: 'Supabase (mcp_jobs)',
    schedule: 'Event-driven',
    lastRun: '2026-03-15T09:25:00Z',
    lastStatus: 'success',
    lastDuration: 1,
    nextRun: null,
    owner: 'Platform',
    tags: ['supabase', 'mcp', 'taskbus'],
  },
  {
    id: 'supa-pgcron-stale-cleanup',
    name: 'Stale Job Cleanup',
    description: 'pg_cron moves stuck processing jobs to DLQ after 1h timeout',
    engine: 'supabase-pg-cron',
    category: 'automation',
    status: 'flowing',
    medallionStage: 'n/a',
    source: 'Supabase (mcp_jobs.jobs)',
    destination: 'Supabase (mcp_jobs.dead_letter_queue)',
    schedule: 'Every 15 min',
    lastRun: '2026-03-15T09:30:00Z',
    lastStatus: 'success',
    lastDuration: 2,
    nextRun: '2026-03-15T09:45:00Z',
    owner: 'Platform',
    tags: ['supabase', 'pg_cron', 'dlq'],
  },
  {
    id: 'supa-edge-kb-indexer',
    name: 'KB Document Indexer',
    description: 'Edge Function ingests documents, generates embeddings via pgvector',
    engine: 'supabase-edge',
    category: 'ai-ml',
    status: 'idle',
    medallionStage: 'silver',
    source: 'Document uploads / API',
    destination: 'Supabase (pgvector)',
    schedule: 'Event-driven',
    lastRun: '2026-03-14T18:00:00Z',
    lastStatus: 'success',
    lastDuration: 12,
    nextRun: null,
    owner: 'Data Team',
    tags: ['supabase', 'pgvector', 'ai'],
  },

  // ---- GitHub Actions CI/CD ----
  {
    id: 'gha-ci-odoo-ce',
    name: 'CI: Odoo CE Tests',
    description: 'Main CI pipeline — lint, typecheck, Odoo module tests',
    engine: 'github-actions',
    category: 'ci-cd',
    status: 'flowing',
    medallionStage: 'n/a',
    source: 'GitHub (push/PR)',
    destination: 'GitHub Actions',
    schedule: 'On push / PR',
    lastRun: '2026-03-15T07:45:00Z',
    lastStatus: 'success',
    lastDuration: 792,
    nextRun: null,
    owner: 'Platform',
    tags: ['github', 'ci', 'odoo'],
  },
  {
    id: 'gha-deploy-prod',
    name: 'Deploy: Production ACA',
    description: 'Builds Docker image, pushes to ACR, deploys to Azure Container Apps',
    engine: 'github-actions',
    category: 'ci-cd',
    status: 'flowing',
    medallionStage: 'n/a',
    source: 'GitHub (merge to main)',
    destination: 'Azure Container Apps',
    schedule: 'On merge to main',
    lastRun: '2026-03-15T08:00:00Z',
    lastStatus: 'success',
    lastDuration: 862,
    nextRun: null,
    owner: 'Platform',
    tags: ['github', 'deploy', 'azure'],
  },
  {
    id: 'gha-health-check',
    name: 'Health Check: Platform',
    description: 'Periodic health probe of all ACA services and external endpoints',
    engine: 'github-actions',
    category: 'observability',
    status: 'flowing',
    medallionStage: 'n/a',
    source: 'GitHub Actions (cron)',
    destination: 'GitHub / Slack',
    schedule: 'Every 15 min',
    lastRun: '2026-03-15T09:30:00Z',
    lastStatus: 'success',
    lastDuration: 45,
    nextRun: '2026-03-15T09:45:00Z',
    owner: 'Platform',
    tags: ['github', 'health', 'monitoring'],
  },
  {
    id: 'gha-kb-refresh',
    name: 'Odoo Docs KB Refresh',
    description: 'Scrapes Odoo docs, chunks content, pushes to pgvector',
    engine: 'github-actions',
    category: 'etl',
    status: 'flowing',
    medallionStage: 'bronze',
    source: 'Odoo documentation (web)',
    destination: 'Supabase (pgvector)',
    schedule: 'Daily 04:00 UTC',
    lastRun: '2026-03-15T04:00:00Z',
    lastStatus: 'success',
    lastDuration: 340,
    nextRun: '2026-03-16T04:00:00Z',
    owner: 'Data Team',
    tags: ['github', 'kb', 'etl'],
  },
  {
    id: 'gha-dns-sync',
    name: 'DNS SSOT Sync Check',
    description: 'Validates subdomain-registry.yaml against Cloudflare live DNS',
    engine: 'github-actions',
    category: 'observability',
    status: 'flowing',
    medallionStage: 'n/a',
    source: 'GitHub (push)',
    destination: 'Cloudflare DNS',
    schedule: 'On push (infra/dns/**)',
    lastRun: '2026-03-14T16:30:00Z',
    lastStatus: 'success',
    lastDuration: 28,
    nextRun: null,
    owner: 'Platform',
    tags: ['github', 'dns', 'cloudflare'],
  },

  // ---- Power Automate ----
  {
    id: 'pa-approval-routing',
    name: 'Approval Routing Flow',
    description: 'Routes approval requests through M365 Approvals based on document metadata',
    engine: 'power-automate',
    category: 'automation',
    status: 'flowing',
    medallionStage: 'n/a',
    source: 'SharePoint / Teams',
    destination: 'M365 Approvals',
    schedule: 'Event-driven',
    lastRun: '2026-03-15T09:12:00Z',
    lastStatus: 'success',
    lastDuration: 5,
    nextRun: null,
    owner: 'Platform',
    tags: ['power-automate', 'approvals', 'm365'],
  },
  {
    id: 'pa-license-sync',
    name: 'License Sync Flow',
    description: 'Syncs M365 license assignments to Odoo HR records',
    engine: 'power-automate',
    category: 'sync',
    status: 'flowing',
    medallionStage: 'bronze',
    source: 'Microsoft 365 Admin',
    destination: 'Odoo CE (HR)',
    schedule: 'Daily 01:00 UTC',
    lastRun: '2026-03-15T01:00:00Z',
    lastStatus: 'success',
    lastDuration: 30,
    nextRun: '2026-03-16T01:00:00Z',
    owner: 'Platform',
    tags: ['power-automate', 'licensing', 'odoo'],
  },

  // ---- Azure DevOps ----
  {
    id: 'ado-infra-validate',
    name: 'ADO: Infrastructure Validation',
    description: 'Validates Terraform plans and ARM templates on PR',
    engine: 'github-actions',
    category: 'ci-cd',
    status: 'flowing',
    medallionStage: 'n/a',
    source: 'Azure DevOps (PR)',
    destination: 'Azure Resource Manager',
    schedule: 'On PR',
    lastRun: '2026-03-15T08:00:00Z',
    lastStatus: 'success',
    lastDuration: 180,
    nextRun: null,
    owner: 'Platform',
    tags: ['azure-devops', 'terraform', 'infra'],
  },

  // ---- Azure Data Factory (planned) ----
  {
    id: 'adf-odoo-warehouse',
    name: 'Odoo → Data Warehouse ETL',
    description: 'ADF pipeline: extract Odoo PG tables → transform → load into analytics warehouse',
    engine: 'azure-data-factory',
    category: 'etl',
    status: 'planned',
    medallionStage: 'bronze',
    source: 'Azure PostgreSQL (Odoo)',
    destination: 'Azure Data Lake / Synapse',
    schedule: 'Daily 05:00 UTC',
    lastRun: null,
    lastStatus: null,
    lastDuration: null,
    nextRun: null,
    owner: 'Data Team',
    tags: ['adf', 'etl', 'warehouse'],
  },
  {
    id: 'adf-bronze-silver',
    name: 'Bronze → Silver Transform',
    description: 'ADF pipeline: clean, deduplicate, and normalize bronze-tier raw data',
    engine: 'azure-data-factory',
    category: 'etl',
    status: 'planned',
    medallionStage: 'silver',
    source: 'Azure Data Lake (bronze)',
    destination: 'Azure Data Lake (silver)',
    schedule: 'Daily 06:00 UTC',
    lastRun: null,
    lastStatus: null,
    lastDuration: null,
    nextRun: null,
    owner: 'Data Team',
    tags: ['adf', 'medallion', 'transform'],
  },

  // ---- Databricks / Spark (planned) ----
  {
    id: 'dbx-feature-eng',
    name: 'Databricks: Feature Engineering',
    description: 'Spark job for computing ML feature vectors from silver-tier data',
    engine: 'databricks',
    category: 'ai-ml',
    status: 'planned',
    medallionStage: 'gold',
    source: 'Azure Data Lake (silver)',
    destination: 'Databricks Feature Store',
    schedule: 'Daily 07:00 UTC',
    lastRun: null,
    lastStatus: null,
    lastDuration: null,
    nextRun: null,
    owner: 'AI Team',
    tags: ['databricks', 'spark', 'ml'],
  },
  {
    id: 'dbx-copilot-finetune',
    name: 'Databricks: Copilot Fine-tune',
    description: 'Fine-tuning pipeline for domain-specific copilot model on Odoo data',
    engine: 'databricks',
    category: 'ai-ml',
    status: 'planned',
    medallionStage: 'platinum',
    source: 'Databricks Feature Store',
    destination: 'AI Foundry Model Registry',
    schedule: 'Weekly',
    lastRun: null,
    lastStatus: null,
    lastDuration: null,
    nextRun: null,
    owner: 'AI Team',
    tags: ['databricks', 'finetuning', 'copilot'],
  },

  // ---- dbt (planned) ----
  {
    id: 'dbt-silver-gold',
    name: 'dbt: Silver → Gold Models',
    description: 'dbt transforms silver-tier tables into business-ready gold models',
    engine: 'dbt',
    category: 'etl',
    status: 'planned',
    medallionStage: 'gold',
    source: 'Azure PostgreSQL (silver)',
    destination: 'Azure PostgreSQL (gold)',
    schedule: 'Daily 06:30 UTC',
    lastRun: null,
    lastStatus: null,
    lastDuration: null,
    nextRun: null,
    owner: 'Data Team',
    tags: ['dbt', 'medallion', 'transform'],
  },
  {
    id: 'dbt-finance-reporting',
    name: 'dbt: Finance Reporting Models',
    description: 'Finance-specific dbt models for BIR compliance and PPM reporting',
    engine: 'dbt',
    category: 'etl',
    status: 'planned',
    medallionStage: 'gold',
    source: 'Odoo finance tables',
    destination: 'Superset reporting views',
    schedule: 'Daily 07:00 UTC',
    lastRun: null,
    lastStatus: null,
    lastDuration: null,
    nextRun: null,
    owner: 'Finance',
    tags: ['dbt', 'finance', 'bir'],
  },

  // ---- Iceberg (planned) ----
  {
    id: 'iceberg-archive',
    name: 'Iceberg: Historical Archive',
    description: 'Apache Iceberg table format for time-travel analytics on historical Odoo data',
    engine: 'iceberg',
    category: 'etl',
    status: 'planned',
    medallionStage: 'platinum',
    source: 'Azure Data Lake (gold)',
    destination: 'Iceberg tables (Azure Storage)',
    schedule: 'Weekly Sun 00:00 UTC',
    lastRun: null,
    lastStatus: null,
    lastDuration: null,
    nextRun: null,
    owner: 'Data Team',
    tags: ['iceberg', 'archive', 'time-travel'],
  },

  // ---- Fabric (unconfigured) ----
  {
    id: 'fabric-lakehouse',
    name: 'Fabric: Lakehouse Ingestion',
    description: 'Microsoft Fabric lakehouse pipeline for unified analytics on Odoo + M365 data',
    engine: 'fabric-pipeline',
    category: 'etl',
    status: 'unconfigured',
    medallionStage: 'bronze',
    source: 'Azure Data Lake + M365',
    destination: 'Fabric Lakehouse',
    schedule: 'Hourly',
    lastRun: null,
    lastStatus: null,
    lastDuration: null,
    nextRun: null,
    owner: 'Data Team',
    tags: ['fabric', 'lakehouse', 'analytics'],
  },
  {
    id: 'fabric-realtime',
    name: 'Fabric: Real-time Analytics',
    description: 'Fabric Eventstream for real-time operational dashboards',
    engine: 'fabric-pipeline',
    category: 'etl',
    status: 'planned',
    medallionStage: 'gold',
    source: 'Azure Event Hubs',
    destination: 'Fabric KQL Database',
    schedule: 'Streaming',
    lastRun: null,
    lastStatus: null,
    lastDuration: null,
    nextRun: null,
    owner: 'Data Team',
    tags: ['fabric', 'realtime', 'streaming'],
  },

  // ---- Airbyte (planned) ----
  {
    id: 'airbyte-crm-sync',
    name: 'Airbyte: CRM Data Sync',
    description: 'Airbyte connector syncing external CRM data into Odoo contacts',
    engine: 'airbyte',
    category: 'sync',
    status: 'planned',
    medallionStage: 'bronze',
    source: 'External CRM API',
    destination: 'Odoo CE (res.partner)',
    schedule: 'Every 6h',
    lastRun: null,
    lastStatus: null,
    lastDuration: null,
    nextRun: null,
    owner: 'Data Team',
    tags: ['airbyte', 'crm', 'sync'],
  },

  // ---- Fivetran (planned) ----
  {
    id: 'fivetran-saas-ingest',
    name: 'Fivetran: SaaS Connector Ingest',
    description: 'Managed connectors for SaaS data sources (Slack, Zoho, GitHub) into warehouse',
    engine: 'fivetran',
    category: 'etl',
    status: 'planned',
    medallionStage: 'bronze',
    source: 'Slack + Zoho + GitHub APIs',
    destination: 'Azure PostgreSQL (bronze)',
    schedule: 'Every 1h',
    lastRun: null,
    lastStatus: null,
    lastDuration: null,
    nextRun: null,
    owner: 'Data Team',
    tags: ['fivetran', 'saas', 'ingest'],
  },

  // ---- Azure Logic Apps (planned) ----
  {
    id: 'logic-bir-compliance',
    name: 'Logic App: BIR Report Generator',
    description: 'Azure Logic App generating BIR compliance reports from Odoo finance data',
    engine: 'azure-logic-apps',
    category: 'automation',
    status: 'planned',
    medallionStage: 'gold',
    source: 'Odoo CE (finance)',
    destination: 'Azure Blob (BIR reports)',
    schedule: 'Monthly 1st 06:00 UTC',
    lastRun: null,
    lastStatus: null,
    lastDuration: null,
    nextRun: null,
    owner: 'Finance',
    tags: ['logic-apps', 'bir', 'compliance'],
  },

  // ---- AI Foundry (flowing) ----
  {
    id: 'ai-foundry-eval',
    name: 'AI Foundry: Model Evaluation',
    description: 'Weekly evaluation of copilot model performance against benchmark suite',
    engine: 'custom',
    category: 'ai-ml',
    status: 'flowing',
    medallionStage: 'platinum',
    source: 'AI Foundry evaluation dataset',
    destination: 'AI Foundry Model Registry',
    schedule: 'Weekly Mon 04:00 UTC',
    lastRun: '2026-03-10T04:00:00Z',
    lastStatus: 'success',
    lastDuration: 1800,
    nextRun: '2026-03-17T04:00:00Z',
    owner: 'AI Team',
    tags: ['ai-foundry', 'evaluation', 'copilot'],
  },

  // ---- Observability ----
  {
    id: 'n8n-compliance-report',
    name: 'Monthly Compliance Snapshot',
    description: 'Generates compliance report from Supabase data, pushes to Superset',
    engine: 'n8n',
    category: 'observability',
    status: 'flowing',
    medallionStage: 'gold',
    source: 'Supabase (gold views)',
    destination: 'Superset snapshot',
    schedule: 'Monthly 1st 09:00 UTC',
    lastRun: '2026-03-01T09:00:00Z',
    lastStatus: 'success',
    lastDuration: 60,
    nextRun: '2026-04-01T09:00:00Z',
    owner: 'Finance',
    tags: ['n8n', 'compliance', 'superset'],
  },
]

// ---- Helpers ----

export function pipelinesByStatus(pipelines: Pipeline[]): Record<PipelineStatus, Pipeline[]> {
  const result = {} as Record<PipelineStatus, Pipeline[]>
  for (const p of pipelines) {
    if (!result[p.status]) result[p.status] = []
    result[p.status].push(p)
  }
  return result
}

export function pipelinesByEngine(pipelines: Pipeline[]): Record<string, Pipeline[]> {
  const result = {} as Record<string, Pipeline[]>
  for (const p of pipelines) {
    if (!result[p.engine]) result[p.engine] = []
    result[p.engine].push(p)
  }
  return result
}

export function pipelinesByMedallion(pipelines: Pipeline[]): Record<MedallionStage, Pipeline[]> {
  const result = {} as Record<MedallionStage, Pipeline[]>
  for (const p of pipelines) {
    if (!result[p.medallionStage]) result[p.medallionStage] = []
    result[p.medallionStage].push(p)
  }
  return result
}

export function pipelineStats(pipelines: Pipeline[]) {
  return {
    total: pipelines.length,
    flowing: pipelines.filter(p => p.status === 'flowing').length,
    idle: pipelines.filter(p => p.status === 'idle').length,
    error: pipelines.filter(p => p.status === 'error').length,
    paused: pipelines.filter(p => p.status === 'paused').length,
    planned: pipelines.filter(p => p.status === 'planned').length,
    unconfigured: pipelines.filter(p => p.status === 'unconfigured').length,
    deprecated: pipelines.filter(p => p.status === 'deprecated').length,
  }
}

const ENGINE_LABELS: Record<PipelineEngine, string> = {
  'n8n': 'n8n',
  'supabase-edge': 'Supabase Edge',
  'supabase-pg-cron': 'Supabase pg_cron',
  'github-actions': 'GitHub Actions',
  'azure-data-factory': 'Azure Data Factory',
  'azure-logic-apps': 'Azure Logic Apps',
  'power-automate': 'Power Automate',
  'databricks': 'Databricks',
  'spark': 'Apache Spark',
  'dbt': 'dbt',
  'airbyte': 'Airbyte',
  'fivetran': 'Fivetran',
  'fabric-pipeline': 'Microsoft Fabric',
  'iceberg': 'Apache Iceberg',
  'custom': 'Custom',
}

export function engineLabel(engine: PipelineEngine): string {
  return ENGINE_LABELS[engine] ?? engine
}

const MEDALLION_LABELS: Record<MedallionStage, string> = {
  'ingest': 'Ingest',
  'bronze': 'Bronze',
  'silver': 'Silver',
  'gold': 'Gold',
  'platinum': 'Platinum',
  'n/a': 'N/A',
}

export function medallionLabel(stage: MedallionStage): string {
  return MEDALLION_LABELS[stage] ?? stage
}
