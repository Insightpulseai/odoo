import useSWR from 'swr'
import type { CopilotEvalData, Service, Tool, CronJob, KnowledgeBase } from './types'
import type { ProviderSummary, NormalizedService } from './providers/types'

const fetcher = (url: string) => fetch(url).then((r) => r.json())

// Service health with 30s polling
export function useServices() {
  const { data, error, isLoading, mutate } = useSWR<{
    services: Service[]
    checkedAt: string
    source: string
  }>('/api/services', fetcher, { refreshInterval: 30000 })

  return {
    services: data?.services ?? [],
    checkedAt: data?.checkedAt,
    source: data?.source ?? 'loading',
    isLoading,
    isError: !!error,
    refresh: mutate,
  }
}

// Capability eval scores with 5min refresh
export function useEval() {
  const { data, error, isLoading, mutate } = useSWR<
    CopilotEvalData & { source: string; readAt: string }
  >('/api/eval', fetcher, { refreshInterval: 300000 })

  return {
    eval: data ?? null,
    source: data?.source ?? 'loading',
    isLoading,
    isError: !!error,
    refresh: mutate,
  }
}

// Agent and tool registry with 60s refresh
export function useAgents() {
  const { data, error, isLoading, mutate } = useSWR<{
    agents: Array<{
      name: string
      version: string
      owner: string
      runtime: string
      modelAlias: string
      tools: string[]
      promotionState: string
      description: string
      sourceFile: string
    }>
    tools: Array<{
      name: string
      category: string
      status: string
      agentBinding?: string
      provider?: string
    }>
    source: string
    fetchedAt: string
  }>('/api/agents', fetcher, { refreshInterval: 60000 })

  return {
    agents: data?.agents ?? [],
    tools: data?.tools ?? [],
    source: data?.source ?? 'loading',
    isLoading,
    isError: !!error,
    refresh: mutate,
  }
}

// Jobs and cron with 15s refresh
export function useJobs() {
  const { data, error, isLoading, mutate } = useSWR<{
    jobs: Array<{
      id: string
      name: string
      type: string
      status: string
      schedule?: string
      lastRun?: string
      workflow?: string
    }>
    crons: CronJob[]
    source: string
    fetchedAt: string
  }>('/api/jobs', fetcher, { refreshInterval: 15000 })

  return {
    jobs: data?.jobs ?? [],
    crons: data?.crons ?? [],
    source: data?.source ?? 'loading',
    isLoading,
    isError: !!error,
    refresh: mutate,
  }
}

// Knowledge base status with 2min refresh
export function useKnowledgeBases() {
  const { data, error, isLoading, mutate } = useSWR<{
    knowledgeBases: KnowledgeBase[]
    boundaryContracts: Array<{
      name: string
      kind: string
      odooModel?: string
      description: string
      readOps: number
      writeOps: number
      prohibited: number
      sourceFile: string
    }>
    policies: Array<{
      name: string
      kind: string
      version: string
      sourceFile: string
    }>
    source: string
    fetchedAt: string
  }>('/api/knowledge', fetcher, { refreshInterval: 120000 })

  return {
    knowledgeBases: data?.knowledgeBases ?? [],
    boundaryContracts: data?.boundaryContracts ?? [],
    policies: data?.policies ?? [],
    source: data?.source ?? 'loading',
    isLoading,
    isError: !!error,
    refresh: mutate,
  }
}

// Orchestration registry with 2min refresh
export function useOrchestrationRegistry() {
  const { data, error, isLoading, mutate } = useSWR<{
    pipelines: Array<{
      id: string
      name: string
      description: string
      documentClass: string
      stages: Array<{ name: string; tool?: string; type?: string }>
      sourceFile: string
    }>
    documentClasses: Array<{
      className: string
      displayName: string
      docintModel: string
      odooModel: string | null
      keyFields: string[]
      confidenceThreshold: number
      sourceFile: string
    }>
    source: string
    fetchedAt: string
  }>('/api/orchestration', fetcher, { refreshInterval: 120000 })

  return {
    pipelines: data?.pipelines ?? [],
    documentClasses: data?.documentClasses ?? [],
    source: data?.source ?? 'loading',
    isLoading,
    isError: !!error,
    refresh: mutate,
  }
}

// Deployments with 30s refresh
export function useDeployments() {
  const { data, error, isLoading, mutate } = useSWR<{
    deployments: Array<{
      id: string
      name: string
      version: string
      environment: string
      status: string
      modelAlias: string
      owner: string
      sourceFile: string
    }>
    modelAliases: Array<{
      alias: string
      currentModel: string
      fallback: string | null
      costTier: string
      useCases: string[]
    }>
    policies: Array<{
      name: string
      kind: string
      version: string
      sourceFile: string
    }>
    source: string
    fetchedAt: string
  }>('/api/deployments', fetcher, { refreshInterval: 30000 })

  return {
    deployments: data?.deployments ?? [],
    modelAliases: data?.modelAliases ?? [],
    policies: data?.policies ?? [],
    source: data?.source ?? 'loading',
    isLoading,
    isError: !!error,
    refresh: mutate,
  }
}

// Task bus with 10s polling
export function useTaskBus() {
  const { data, error, isLoading, mutate } = useSWR<{
    jobs: Array<{
      id: string
      source: string
      jobType: string
      status: string
      priority: number
      createdAt: string
      updatedAt: string
    }>
    stats: {
      queued: number
      processing: number
      completed: number
      failed: number
      dlqCount: number
    }
    source: string
    fetchedAt: string
  }>('/api/taskbus', fetcher, { refreshInterval: 10000 })

  return {
    jobs: data?.jobs ?? [],
    stats: data?.stats ?? { queued: 0, processing: 0, completed: 0, failed: 0, dlqCount: 0 },
    source: data?.source ?? 'loading',
    isLoading,
    isError: !!error,
    refresh: mutate,
  }
}

// Odoo.sh provider with 30s refresh
export function useOdoosh() {
  const { data, error, isLoading, mutate } = useSWR<
    ProviderSummary & { source: string; fetchedAt: string }
  >('/api/odoosh', fetcher, { refreshInterval: 30000 })

  return {
    summary: data ?? null,
    health: data?.health ?? null,
    builds: data?.builds ?? [],
    deploys: data?.deploys ?? [],
    databases: data?.databases ?? [],
    jobs: data?.jobs ?? [],
    kbCoverage: data?.kbCoverage ?? [],
    source: data?.source ?? 'loading',
    isLoading,
    isError: !!error,
    refresh: mutate,
  }
}

// Azure ACA provider with 30s refresh
export function useAzure() {
  const { data, error, isLoading, mutate } = useSWR<
    ProviderSummary & { source: string; fetchedAt: string }
  >('/api/azure', fetcher, { refreshInterval: 30000 })

  return {
    summary: data ?? null,
    health: data?.health ?? null,
    builds: data?.builds ?? [],
    deploys: data?.deploys ?? [],
    databases: data?.databases ?? [],
    jobs: data?.jobs ?? [],
    kbCoverage: data?.kbCoverage ?? [],
    source: data?.source ?? 'loading',
    isLoading,
    isError: !!error,
    refresh: mutate,
  }
}

// Microsoft Cloud provider with 30s refresh
export function useMicrosoftCloud() {
  const { data, error, isLoading, mutate } = useSWR<
    ProviderSummary & { services: NormalizedService[]; source: string; fetchedAt: string }
  >('/api/microsoft-cloud', fetcher, { refreshInterval: 30000 })

  return {
    summary: data ?? null,
    services: data?.services ?? [],
    health: data?.health ?? null,
    builds: data?.builds ?? [],
    deploys: data?.deploys ?? [],
    jobs: data?.jobs ?? [],
    kbCoverage: data?.kbCoverage ?? [],
    source: data?.source ?? 'loading',
    isLoading,
    isError: !!error,
    refresh: mutate,
  }
}

// Copilot chat - not SWR (imperative)
export async function sendCopilotMessage(
  message: string,
  history: Array<{ role: string; content: string }>
): Promise<{ reply: string; source: string }> {
  const res = await fetch('/api/copilot', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history }),
  })
  if (!res.ok) throw new Error(`Chat API error: ${res.status}`)
  return res.json()
}
