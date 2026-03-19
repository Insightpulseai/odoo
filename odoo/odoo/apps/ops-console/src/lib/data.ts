import type {
  CopilotEvalData,
  Service,
  Tool,
  CronJob,
  KnowledgeBase,
} from './types'

// Re-export hooks for convenience
export {
  useServices,
  useEval,
  useAgents,
  useJobs,
  useKnowledgeBases,
  useOrchestrationRegistry,
  useDeployments,
  useTaskBus,
  useOdoosh,
  useAzure,
  useMicrosoftCloud,
  sendCopilotMessage,
} from './hooks'

// --- Fallback static data (used when API routes are unreachable) ---

export const copilotEvalData: CopilotEvalData = {
  overall_score: 0.4174,
  maturity_band: 'scaffolded',
  release_blocked: true,
  domain_scores: {
    tool_execution: 0.75,
    production_readiness: 0.625,
    auth_identity: 0.625,
    knowledge_retrieval: 0.5,
    workflow_orchestration: 0.375,
    context_management: 0.375,
    observability: 0.375,
    error_recovery: 0.25,
    agents: 0.125,
    multi_turn: 0.125,
  },
  blockers: [
    'agent_resolution: current=2 (needs >=3, domain=agents)',
    'multi_turn_success: current=1 (needs >=3, domain=multi_turn)',
    'error_recovery_rate: current=1 (needs >=2, domain=error_recovery)',
  ],
}

export const services: Service[] = [
  { name: 'Odoo CE 19', endpoint: 'erp.insightpulseai.com', status: 'live', type: 'aca' },
  { name: 'n8n', endpoint: 'n8n.insightpulseai.com', status: 'live', type: 'aca' },
  { name: 'Superset', endpoint: 'superset.insightpulseai.com', status: 'live', type: 'aca' },
  { name: 'Keycloak', endpoint: 'auth.insightpulseai.com', status: 'stub', type: 'aca' },
  { name: 'Plane', endpoint: 'plane.insightpulseai.com', status: 'live', type: 'aca' },
  { name: 'MCP Coordinator', endpoint: 'mcp.insightpulseai.com', status: 'live', type: 'aca' },
  { name: 'OCR Service', endpoint: 'ocr.insightpulseai.com', status: 'live', type: 'aca' },
]

export const tools: Tool[] = [
  { name: 'read_record', category: 'read', status: 'operational' },
  { name: 'search_records', category: 'read', status: 'operational' },
  { name: 'search_docs', category: 'read', status: 'operational' },
  { name: 'get_report', category: 'read', status: 'operational' },
  { name: 'read_finance_close', category: 'finance', status: 'operational' },
  { name: 'view_campaign_perf', category: 'finance', status: 'operational' },
  { name: 'view_dashboard', category: 'finance', status: 'operational' },
  { name: 'search_strategy_docs', category: 'knowledge', status: 'operational' },
  { name: 'search_odoo_docs', category: 'knowledge', status: 'operational' },
  { name: 'search_azure_docs', category: 'knowledge', status: 'operational' },
  { name: 'search_databricks_docs', category: 'knowledge', status: 'operational' },
  { name: 'search_org_docs', category: 'knowledge', status: 'operational' },
  { name: 'search_spec_bundles', category: 'knowledge', status: 'operational' },
  { name: 'search_architecture_docs', category: 'knowledge', status: 'operational' },
]

export const cronJobs: CronJob[] = [
  { name: 'Foundry Healthcheck', schedule: 'Daily 02:00 UTC', type: 'odoo-cron', model: 'ipai.foundry.service', method: 'nightly_healthcheck', status: 'active' },
  { name: 'Odoo Docs KB Refresh', schedule: 'Weekly Mon 06:00 UTC', type: 'github-action', workflow: 'odoo-docs-kb-refresh.yml', status: 'active' },
  { name: 'Org Docs Refresh', schedule: 'Weekly Mon 07:00 UTC', type: 'github-action', workflow: 'org-docs-refresh.yml', status: 'active' },
  { name: 'Copilot Eval', schedule: 'On push/PR', type: 'github-action', workflow: 'odoo-copilot-eval.yml', status: 'active' },
  { name: 'Service Matrix Sync', schedule: 'Daily 03:00 UTC', type: 'n8n-workflow', status: 'active' },
  { name: 'DNS Consistency Check', schedule: 'On push (CI)', type: 'github-action', workflow: 'dns-sync-check.yml', status: 'active' },
]

export const knowledgeBases: KnowledgeBase[] = [
  { name: 'odoo19-docs', status: 'operational', chunks: 7224, lastRefresh: '2026-03-15', index: 'odoo19-docs' },
  { name: 'azure-platform-docs', status: 'scaffolded', chunks: 0, lastRefresh: null, index: 'azure-platform-docs' },
  { name: 'databricks-docs', status: 'scaffolded', chunks: 0, lastRefresh: null, index: 'databricks-docs' },
  { name: 'org-docs', status: 'scaffolded', chunks: 0, lastRefresh: null, index: 'org-docs' },
]

// --- Utilities ---

export function formatScore(score: number | undefined | null): string {
  if (score == null || isNaN(score)) return '—'
  return `${Math.round(score * 100)}%`
}

export function domainLabel(key: string): string {
  return key.split('_').map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
}

export function countByStatus<T extends { status: string }>(items: T[], status: string): number {
  return items.filter((item) => item.status === status).length
}
