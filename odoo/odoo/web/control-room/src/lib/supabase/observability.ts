/**
 * Supabase Client for Observability Schema
 * Provides type-safe access to jobs, agents, services, and topology
 */

import type {
  Job,
  JobDetail,
  JobRun,
  JobEvent,
  JobsFilters,
  JobStats,
  Agent,
  AgentWithState,
  AgentsFilters,
  AgentStats,
  Service,
  HealthSummary,
  Topology,
  DeadLetterJob,
  PaginatedResponse,
} from '@/types/observability';

// Environment variables (set in .env.local)
const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || '';

/**
 * Base fetch wrapper for Supabase REST API
 */
async function supabaseFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${SUPABASE_URL}/rest/v1${path}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'apikey': SUPABASE_SERVICE_KEY,
      'Authorization': `Bearer ${SUPABASE_SERVICE_KEY}`,
      'Prefer': 'return=representation',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Supabase error: ${response.status} - ${error}`);
  }

  // Handle empty responses
  const text = await response.text();
  if (!text) return {} as T;

  return JSON.parse(text);
}

/**
 * Call Supabase RPC function
 */
async function supabaseRpc<T>(
  functionName: string,
  params: Record<string, unknown> = {}
): Promise<T> {
  const url = `${SUPABASE_URL}/rest/v1/rpc/${functionName}`;

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'apikey': SUPABASE_SERVICE_KEY,
      'Authorization': `Bearer ${SUPABASE_SERVICE_KEY}`,
    },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Supabase RPC error: ${response.status} - ${error}`);
  }

  const text = await response.text();
  if (!text) return {} as T;

  return JSON.parse(text);
}

// ============ Jobs API ============

export async function listJobs(filters: JobsFilters = {}): Promise<PaginatedResponse<Job>> {
  const { source, job_type, status, limit = 50, offset = 0 } = filters;

  let query = `observability.jobs?select=*&deleted_at=is.null&order=created_at.desc&limit=${limit}&offset=${offset}`;

  if (source) query += `&source=eq.${source}`;
  if (job_type) query += `&job_type=eq.${job_type}`;
  if (status) query += `&status=eq.${status}`;

  const data = await supabaseFetch<Job[]>(`/${query}`, {
    headers: { 'Prefer': 'count=exact' },
  });

  return {
    data,
    total: data.length, // Would need count header parsing for accurate total
    limit,
    offset,
    has_more: data.length === limit,
  };
}

export async function getJob(id: string): Promise<JobDetail | null> {
  const [job] = await supabaseFetch<Job[]>(
    `/observability.jobs?id=eq.${id}&select=*`
  );

  if (!job) return null;

  const [runs, events] = await Promise.all([
    supabaseFetch<JobRun[]>(
      `/observability.job_runs?job_id=eq.${id}&select=*&order=run_number.desc`
    ),
    supabaseFetch<JobEvent[]>(
      `/observability.job_events?job_id=eq.${id}&select=*&order=timestamp.desc`
    ),
  ]);

  return { ...job, runs, events };
}

export async function enqueueJob(
  source: string,
  jobType: string,
  payload: Record<string, unknown> = {},
  options: { priority?: number; scheduledAt?: string; context?: Record<string, unknown> } = {}
): Promise<string> {
  return supabaseRpc<string>('observability.enqueue_job', {
    p_source: source,
    p_job_type: jobType,
    p_payload: payload,
    p_context: options.context,
    p_priority: options.priority ?? 5,
    p_scheduled_at: options.scheduledAt,
  });
}

export async function retryJob(id: string): Promise<boolean> {
  return supabaseRpc<boolean>('observability.retry_dead_letter', {
    p_job_id: id,
  });
}

export async function getJobStats(since?: string): Promise<JobStats[]> {
  return supabaseRpc<JobStats[]>('observability.get_job_stats', {
    p_since: since || new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
  });
}

export async function listDeadLetterJobs(): Promise<DeadLetterJob[]> {
  return supabaseFetch<DeadLetterJob[]>(
    `/observability.dead_letter?select=*&resolved=eq.false&order=moved_at.desc`
  );
}

// ============ Agents API ============

export async function listAgents(filters: AgentsFilters = {}): Promise<AgentWithState[]> {
  const { status, limit = 50 } = filters;

  let query = `agent_coordination.agent_registry?select=*&order=last_heartbeat.desc.nullsfirst&limit=${limit}`;

  if (status && status.length > 0) {
    query += `&status=in.(${status.join(',')})`;
  }

  const agents = await supabaseFetch<Agent[]>(`/${query}`);

  // Fetch states for active agents
  const agentIds = agents.map(a => a.id);
  const states = agentIds.length > 0
    ? await supabaseFetch<{ agent_id: string; status: string; queue_depth: number; last_heartbeat: string }[]>(
        `/agent_coordination.agent_state?agent_id=in.(${agentIds.join(',')})&select=*`
      )
    : [];

  const stateMap = new Map(states.map(s => [s.agent_id, s]));

  return agents.map(agent => ({
    ...agent,
    state: stateMap.get(agent.id),
  }));
}

export async function getAgentStats(): Promise<AgentStats> {
  const stats = await supabaseRpc<AgentStats[]>('agent_coordination.get_stats');
  return stats[0] || {
    total_agents: 0,
    active_agents: 0,
    idle_agents: 0,
    busy_agents: 0,
    offline_agents: 0,
    pending_jobs: 0,
    processing_jobs: 0,
  };
}

export async function sendAgentHeartbeat(agentId: string): Promise<boolean> {
  return supabaseRpc<boolean>('agent_coordination.agent_heartbeat', {
    p_agent_id: agentId,
  });
}

// ============ Services API ============

export async function listServices(): Promise<Service[]> {
  return supabaseFetch<Service[]>(
    `/observability.services?select=*&order=name.asc`
  );
}

export async function getHealthSummary(): Promise<HealthSummary> {
  const summary = await supabaseRpc<HealthSummary[]>('observability.get_health_summary');
  return summary[0] || {
    total_services: 0,
    healthy_count: 0,
    degraded_count: 0,
    unhealthy_count: 0,
    offline_count: 0,
    overall_status: 'unknown',
  };
}

export async function recordServiceHealth(
  serviceId: string,
  status: string,
  options: { responseTimeMs?: number; statusCode?: number; errorMessage?: string } = {}
): Promise<void> {
  await supabaseRpc('observability.record_health', {
    p_service_id: serviceId,
    p_status: status,
    p_response_time_ms: options.responseTimeMs,
    p_status_code: options.statusCode,
    p_error_message: options.errorMessage,
  });
}

// ============ Topology API ============

export async function getTopology(): Promise<Topology> {
  const result = await supabaseRpc<{ nodes: Topology['nodes']; edges: Topology['edges'] }[]>(
    'observability.get_topology'
  );

  if (!result || result.length === 0) {
    return { nodes: [], edges: [] };
  }

  return {
    nodes: result[0].nodes || [],
    edges: result[0].edges || [],
  };
}

// ============ Utility Functions ============

/**
 * Check if Supabase is configured
 */
export function isSupabaseConfigured(): boolean {
  return Boolean(SUPABASE_URL && SUPABASE_SERVICE_KEY);
}

/**
 * Get schema information for AI SQL generation
 */
export async function getObservabilitySchema(): Promise<string> {
  // Return simplified schema description for AI context
  return `
Schema: observability
Tables:
- jobs (id, source, job_type, payload, context, priority, status, max_retries, retry_count, scheduled_at, claimed_by, claimed_at, created_at, updated_at, completed_at, deleted_at)
- job_runs (id, job_id, run_number, status, started_at, ended_at, duration_ms, worker_id, result, error, metrics, created_at)
- job_events (id, job_id, run_id, event_type, payload, timestamp)
- dead_letter (id, job_id, reason, last_error, retry_count, moved_at, resolved, resolved_at, resolved_by)
- services (id, name, description, service_type, endpoint, health_endpoint, protocol, port, status, last_check, metadata, created_at, updated_at)
- service_health (id, service_id, status, response_time_ms, status_code, error_message, checked_at)
- edges (id, source_id, source_type, target_id, target_type, edge_type, direction, metadata, created_at)
- metrics (id, metric_type, dimensions, values, period_start, period_end, created_at)

Schema: agent_coordination
Tables:
- agent_registry (id, name, version, description, capabilities, transport, endpoint, mcp_server, tools, input_schema, output_schema, timeout_ms, max_concurrent, retry_policy, tags, owner, status, created_at, updated_at, last_heartbeat)
- agent_state (agent_id, status, current_task_id, queue_depth, last_heartbeat, resource_usage, metrics, updated_at)
- agent_messages (message_id, from_agent_id, to_agent_id, request_type, payload, context, priority, timeout_ms, requires_ack, created_at, expires_at)
- agent_jobs (job_id, source_agent_id, target_agent_id, request_type, payload, context, priority, status, result, error, created_at, started_at, completed_at, retry_count, max_retries)
`.trim();
}
