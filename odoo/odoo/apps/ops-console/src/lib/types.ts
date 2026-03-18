export type MaturityBand = 'scaffolded' | 'developing' | 'operational' | 'optimized'

export type ServiceStatus = 'live' | 'stub' | 'scaffolded' | 'planned' | 'degraded' | 'down'

export type ServiceType = 'aca' | 'vm' | 'saas' | 'function'

export type ToolStatus = 'operational' | 'degraded' | 'down' | 'planned'

export type ToolCategory = 'read' | 'write' | 'workflow' | 'navigation' | 'ai' | 'finance' | 'knowledge'

export type CronStatus = 'active' | 'paused' | 'error'

export type CronType = 'odoo-cron' | 'github-action' | 'n8n-workflow'

export type KBStatus = 'operational' | 'scaffolded' | 'error'

export interface DomainScores {
  [domain: string]: number
}

export interface CopilotEvalData {
  overall_score: number
  maturity_band: MaturityBand
  release_blocked: boolean
  domain_scores: DomainScores
  blockers: string[]
}

export interface Service {
  name: string
  endpoint: string
  status: ServiceStatus
  type: ServiceType
}

export interface Tool {
  name: string
  category: ToolCategory
  status: ToolStatus
}

export interface CronJob {
  name: string
  schedule: string
  type: CronType
  model?: string
  method?: string
  workflow?: string
  status: CronStatus
}

export interface KnowledgeBase {
  name: string
  status: KBStatus
  chunks: number
  lastRefresh: string | null
  index: string
}

export interface NavItem {
  key: string
  label: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  iconFilled: React.ComponentType<{ className?: string }>
}
