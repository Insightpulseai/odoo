/**
 * Leaderboard data model — maturity scoring, release readiness, benchmarks.
 *
 * Canonical maturity thresholds:
 *   0–24  Missing
 *  25–49  Scaffolded
 *  50–74  Partial
 *  75–89  Operational
 *  90–100 Hardened
 */

// --- Maturity threshold system ---

export type MaturityLevel = 'missing' | 'scaffolded' | 'partial' | 'operational' | 'hardened'

export interface MaturityThreshold {
  level: MaturityLevel
  min: number
  max: number
  label: string
}

export const MATURITY_THRESHOLDS: MaturityThreshold[] = [
  { level: 'missing', min: 0, max: 24, label: 'Missing' },
  { level: 'scaffolded', min: 25, max: 49, label: 'Scaffolded' },
  { level: 'partial', min: 50, max: 74, label: 'Partial' },
  { level: 'operational', min: 75, max: 89, label: 'Operational' },
  { level: 'hardened', min: 90, max: 100, label: 'Hardened' },
]

export function scoreToMaturity(score: number): MaturityLevel {
  const pct = Math.round(score * 100)
  if (pct >= 90) return 'hardened'
  if (pct >= 75) return 'operational'
  if (pct >= 50) return 'partial'
  if (pct >= 25) return 'scaffolded'
  return 'missing'
}

export function maturityLabel(level: MaturityLevel): string {
  return MATURITY_THRESHOLDS.find(t => t.level === level)?.label ?? level
}

// --- Domain maturity with provenance ---

export interface DomainMaturityRow {
  id: string
  domain: string
  score: number
  weight: number
  evidencePassed: number
  evidenceTotal: number
  lastEvaluated: string
  trend: number // delta vs previous run (e.g. +0.04)
  sourceSystems: string[]
}

export const DOMAIN_SCORES: DomainMaturityRow[] = [
  {
    id: 'tool-execution',
    domain: 'Tool Execution',
    score: 0.75,
    weight: 3,
    evidencePassed: 9,
    evidenceTotal: 12,
    lastEvaluated: '2026-03-15T08:30:00Z',
    trend: +0.04,
    sourceSystems: ['GitHub Actions', 'Azure ACA'],
  },
  {
    id: 'ci-cd',
    domain: 'CI/CD Pipeline',
    score: 0.75,
    weight: 3,
    evidencePassed: 9,
    evidenceTotal: 12,
    lastEvaluated: '2026-03-15T09:00:00Z',
    trend: +0.08,
    sourceSystems: ['GitHub Actions', 'Azure DevOps'],
  },
  {
    id: 'production-readiness',
    domain: 'Production Readiness',
    score: 0.63,
    weight: 3,
    evidencePassed: 5,
    evidenceTotal: 8,
    lastEvaluated: '2026-03-15T08:45:00Z',
    trend: +0.05,
    sourceSystems: ['Azure ACA', 'Azure Front Door'],
  },
  {
    id: 'auth-identity',
    domain: 'Auth & Identity',
    score: 0.63,
    weight: 2,
    evidencePassed: 5,
    evidenceTotal: 8,
    lastEvaluated: '2026-03-15T07:00:00Z',
    trend: 0,
    sourceSystems: ['Entra ID', 'Keycloak'],
  },
  {
    id: 'observability',
    domain: 'Observability',
    score: 0.50,
    weight: 2,
    evidencePassed: 6,
    evidenceTotal: 12,
    lastEvaluated: '2026-03-15T08:00:00Z',
    trend: +0.04,
    sourceSystems: ['Azure Monitor', 'GitHub Actions'],
  },
  {
    id: 'knowledge-base',
    domain: 'Knowledge Base',
    score: 0.38,
    weight: 2,
    evidencePassed: 6,
    evidenceTotal: 16,
    lastEvaluated: '2026-03-15T06:00:00Z',
    trend: -0.02,
    sourceSystems: ['AI Foundry', 'Copilot Studio'],
  },
  {
    id: 'error-recovery',
    domain: 'Error Recovery',
    score: 0.25,
    weight: 2,
    evidencePassed: 2,
    evidenceTotal: 8,
    lastEvaluated: '2026-03-15T05:00:00Z',
    trend: +0.12,
    sourceSystems: ['GitHub Actions', 'Power Automate'],
  },
  {
    id: 'multi-agent',
    domain: 'Multi-Agent Coordination',
    score: 0.13,
    weight: 1,
    evidencePassed: 1,
    evidenceTotal: 8,
    lastEvaluated: '2026-03-15T04:00:00Z',
    trend: +0.05,
    sourceSystems: ['AI Foundry', 'n8n'],
  },
]

// --- Weighted overall score ---

export function computeOverallScore(rows: DomainMaturityRow[]): number {
  const totalWeight = rows.reduce((acc, r) => acc + r.weight, 0)
  if (totalWeight === 0) return 0
  return rows.reduce((acc, r) => acc + r.score * r.weight, 0) / totalWeight
}

// --- Release blockers ---

export type BlockerSeverity = 'critical' | 'high' | 'medium'

export interface ReleaseBlocker {
  id: string
  title: string
  severity: BlockerSeverity
  impactedDomains: string[]
  linkedActionId: string
  evidence: string
  owner: string
  status: 'open' | 'in_progress' | 'resolved'
}

export const RELEASE_BLOCKERS: ReleaseBlocker[] = [
  {
    id: 'blocker-1',
    title: 'Auth flow incomplete: Keycloak token exchange not wired to Odoo sessions',
    severity: 'critical',
    impactedDomains: ['auth-identity', 'production-readiness'],
    linkedActionId: 'action-3',
    evidence: 'Entra SSO returns token but Odoo session middleware ignores it',
    owner: 'Platform',
    status: 'in_progress',
  },
  {
    id: 'blocker-2',
    title: 'No structured error recovery: tool failures return raw tracebacks',
    severity: 'high',
    impactedDomains: ['error-recovery', 'tool-execution'],
    linkedActionId: 'action-1',
    evidence: '3 of 8 tool handlers lack try/catch; copilot surfaces Python tracebacks',
    owner: 'Agent Team',
    status: 'open',
  },
  {
    id: 'blocker-3',
    title: 'Knowledge base coverage below 50%: 6 of 12 Foundry buckets unindexed',
    severity: 'medium',
    impactedDomains: ['knowledge-base'],
    linkedActionId: 'action-4',
    evidence: '6/16 KB checks passing; AI Foundry docs, Purview, Fabric unindexed',
    owner: 'Data Team',
    status: 'open',
  },
]

// --- Remediation actions ---

export interface RemediationAction {
  id: string
  title: string
  expectedLift: number // score lift as decimal (e.g. 0.12 = +12%)
  affectedDomains: string[]
  linkedBlockerIds: string[]
  owner: string
  status: 'planned' | 'in_progress' | 'done'
}

export const REMEDIATION_ACTIONS: RemediationAction[] = [
  {
    id: 'action-1',
    title: 'Implement structured error handling in copilot tool handlers',
    expectedLift: 0.12,
    affectedDomains: ['error-recovery', 'tool-execution'],
    linkedBlockerIds: ['blocker-2'],
    owner: 'Agent Team',
    status: 'planned',
  },
  {
    id: 'action-2',
    title: 'Add health check endpoints for all ACA services',
    expectedLift: 0.08,
    affectedDomains: ['observability', 'production-readiness'],
    linkedBlockerIds: [],
    owner: 'Platform',
    status: 'in_progress',
  },
  {
    id: 'action-3',
    title: 'Wire Keycloak SSO tokens into Odoo session middleware',
    expectedLift: 0.15,
    affectedDomains: ['auth-identity', 'production-readiness'],
    linkedBlockerIds: ['blocker-1'],
    owner: 'Platform',
    status: 'in_progress',
  },
  {
    id: 'action-4',
    title: 'Index remaining Foundry doc buckets into knowledge base',
    expectedLift: 0.10,
    affectedDomains: ['knowledge-base'],
    linkedBlockerIds: ['blocker-3'],
    owner: 'Data Team',
    status: 'planned',
  },
  {
    id: 'action-5',
    title: 'Deploy agent coordination bus via MCP Jobs',
    expectedLift: 0.06,
    affectedDomains: ['multi-agent'],
    linkedBlockerIds: [],
    owner: 'Agent Team',
    status: 'planned',
  },
]

// --- Odoo Copilot Benchmark ---

export interface BenchmarkDimension {
  id: string
  label: string
  score: number
  maxScore: number
  trend: number
}

export const BENCHMARK_DIMENSIONS: BenchmarkDimension[] = [
  { id: 'odoo-native', label: 'Odoo-native actions', score: 7, maxScore: 10, trend: +1 },
  { id: 'knowledge', label: 'Knowledge grounding', score: 4, maxScore: 10, trend: 0 },
  { id: 'finance', label: 'Finance workflow depth', score: 6, maxScore: 10, trend: +2 },
  { id: 'agent-platform', label: 'Agent platform maturity', score: 3, maxScore: 10, trend: +1 },
  { id: 'governance', label: 'Governance / safety', score: 5, maxScore: 10, trend: 0 },
]

// --- Time-ago helper ---

export function timeAgo(isoDate: string): string {
  const diffMs = Date.now() - new Date(isoDate).getTime()
  const mins = Math.floor(diffMs / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}
