// packages/agents/src/registry.ts
// Agent definitions: name, capabilities, allowed tools, input/output schemas.
// SSOT for what agents exist and what they can do.

export interface AgentCapability {
  /** Human-readable name */
  name: string
  /** Unique agent identifier used in ops.runs.agent */
  id: string
  /** Job types this agent can handle */
  jobTypes: string[]
  /** Max duration for a single run in milliseconds */
  maxDurationMs: number
  /** Human-readable description */
  description: string
  /** Input schema (JSON Schema style, for documentation) */
  inputSchema: Record<string, unknown>
}

export const AGENT_REGISTRY: Record<string, AgentCapability> = {
  'ping-agent': {
    name: 'Ping Agent',
    id: 'ping-agent',
    jobTypes: ['ping'],
    maxDurationMs: 5_000,
    description: 'Health check agent. Writes a run_event and marks the run complete. Used to validate the task bus end-to-end.',
    inputSchema: {
      type: 'object',
      properties: {
        message: { type: 'string', description: 'Optional message to echo in the event' },
      },
    },
  },
  'sync-odoo-agent': {
    name: 'Odoo Sync Agent',
    id: 'sync-odoo-agent',
    jobTypes: ['sync_odoo'],
    maxDurationMs: 60_000,
    description: 'Placeholder agent for Odoo → Supabase sync. Emits NOT_CONFIGURED when credentials are absent.',
    inputSchema: {
      type: 'object',
      properties: {
        dry_run: { type: 'boolean', description: 'If true, no writes to Odoo SoR' },
        model: { type: 'string', description: 'Odoo model to sync (e.g. account.move)' },
      },
    },
  },
}

/** Look up an agent by ID. Returns null if not found. */
export function getAgent(agentId: string): AgentCapability | null {
  return AGENT_REGISTRY[agentId] ?? null
}

/** Returns the list of registered agent IDs. */
export function listAgents(): string[] {
  return Object.keys(AGENT_REGISTRY)
}
