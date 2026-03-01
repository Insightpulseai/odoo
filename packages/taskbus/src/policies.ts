// packages/taskbus/src/policies.ts
// SoR / SSOT write-boundary guardrails.
//
// Rule: Agents may only write to the surfaces listed here.
// Any attempt to write outside allowed surfaces MUST throw PolicyViolation.

export type WriteSurface =
  | 'ops.runs'
  | 'ops.run_events'
  | 'ops.artifacts'
  | 'ops.schedules'
  | 'supabase.storage'
  | 'odoo.rpc'       // only via ipai_llm_supabase_bridge; no direct DB writes
  | 'n8n.webhook'

export interface AgentPolicy {
  agent: string
  allowedWrites: WriteSurface[]
  allowedJobTypes: string[]
  maxDurationMs: number
}

/** Central policy registry. Extend when adding new agents. */
export const AGENT_POLICIES: Record<string, AgentPolicy> = {
  'ping-agent': {
    agent: 'ping-agent',
    allowedWrites: ['ops.run_events', 'ops.runs'],
    allowedJobTypes: ['ping'],
    maxDurationMs: 5_000,
  },
  'sync-odoo-agent': {
    agent: 'sync-odoo-agent',
    allowedWrites: ['ops.run_events', 'ops.runs', 'ops.artifacts'],
    allowedJobTypes: ['sync_odoo'],
    maxDurationMs: 60_000,
  },
}

export class PolicyViolation extends Error {
  constructor(agent: string, surface: string) {
    super(`PolicyViolation: agent '${agent}' attempted write to disallowed surface '${surface}'`)
    this.name = 'PolicyViolation'
  }
}

/** Assert that an agent is allowed to write to a surface. Throws if not. */
export function assertAllowed(agent: string, surface: WriteSurface): void {
  const policy = AGENT_POLICIES[agent]
  if (!policy) throw new PolicyViolation(agent, surface)
  if (!policy.allowedWrites.includes(surface)) throw new PolicyViolation(agent, surface)
}

/** Assert that an agent is allowed to handle a job type. Throws if not. */
export function assertJobAllowed(agent: string, jobType: string): void {
  const policy = AGENT_POLICIES[agent]
  if (!policy) throw new PolicyViolation(agent, `job:${jobType}`)
  if (!policy.allowedJobTypes.includes(jobType)) throw new PolicyViolation(agent, `job:${jobType}`)
}
