// packages/taskbus/src/types.ts
// Deterministic types for the ops task bus. Mirrors ops.* Supabase schema.

export type RunStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
export type EventSource = 'odoo' | 'supabase' | 'n8n' | 'manual'

/** Mirrors ops.runs row */
export interface Run {
  id: string
  run_type: string
  agent: string | null
  status: RunStatus
  source: EventSource
  input_json: Record<string, unknown>
  error_json: Record<string, unknown> | null
  idempotency_key: string | null
  odoo_db: string | null
  odoo_model: string | null
  odoo_id: number | null
  metadata: Record<string, unknown>
  started_at: string
  completed_at: string | null
  created_at: string
  updated_at: string
}

/** Mirrors ops.run_events row */
export interface RunEvent {
  id: string
  run_id: string | null
  event_type: string
  idempotency_key: string | null
  source: EventSource
  payload: Record<string, unknown>
  timestamp: string
  ingested_at: string
}

/** Mirrors ops.artifacts row */
export interface Artifact {
  id: string
  run_id: string | null
  artifact_type: string
  name: string | null
  content: Record<string, unknown> | null
  storage_path: string | null
  created_at: string
}

/** Mirrors ops.schedules row */
export interface Schedule {
  id: string
  name: string
  cron: string
  job_type: string
  agent: string
  input_json: Record<string, unknown>
  enabled: boolean
  last_run_at: string | null
  last_run_id: string | null
  created_at: string
  updated_at: string
}

/** Payload sent to a queue consumer or handler */
export interface JobMessage {
  run_id: string
  job_type: string
  agent: string
  input: Record<string, unknown>
  idempotency_key: string
  schedule_id?: string
}

/** What an agent handler returns */
export interface HandlerResult {
  status: 'completed' | 'failed'
  output?: Record<string, unknown>
  error?: string
  events?: Array<{
    event_type: string
    payload: Record<string, unknown>
  }>
  artifacts?: Array<{
    artifact_type: string
    name: string
    content?: Record<string, unknown>
    storage_path?: string
  }>
}
