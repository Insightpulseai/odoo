/**
 * Observability Types for Platform Kit Integration
 * Defines types for jobs, agents, services, and ecosystem topology
 */

// ============ Job Types ============

export type JobStatus = 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled' | 'dead_letter';
export type JobPriority = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10;

export interface Job {
  id: string;
  source: string;
  job_type: string;
  payload: Record<string, unknown>;
  context?: Record<string, unknown>;
  priority: JobPriority;
  status: JobStatus;
  max_retries: number;
  retry_count: number;
  scheduled_at?: string;
  claimed_by?: string;
  claimed_at?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export type JobRunStatus = 'running' | 'completed' | 'failed' | 'cancelled';

export interface JobRun {
  id: string;
  job_id: string;
  run_number: number;
  status: JobRunStatus;
  started_at: string;
  ended_at?: string;
  duration_ms?: number;
  worker_id?: string;
  result?: Record<string, unknown>;
  error?: Record<string, unknown>;
  metrics?: Record<string, unknown>;
  created_at: string;
}

export type JobEventType =
  | 'created'
  | 'queued'
  | 'claimed'
  | 'started'
  | 'progress'
  | 'completed'
  | 'failed'
  | 'retrying'
  | 'cancelled'
  | 'dead_letter';

export interface JobEvent {
  id: string;
  job_id: string;
  run_id?: string;
  event_type: JobEventType;
  payload?: Record<string, unknown>;
  timestamp: string;
}

export interface DeadLetterJob {
  id: string;
  job_id: string;
  reason: string;
  last_error?: Record<string, unknown>;
  retry_count: number;
  moved_at: string;
  resolved: boolean;
  resolved_at?: string;
  resolved_by?: string;
}

export interface JobDetail extends Job {
  runs: JobRun[];
  events: JobEvent[];
}

// ============ Agent Types ============

export type AgentStatus = 'active' | 'idle' | 'busy' | 'offline' | 'maintenance';
export type AgentTransport = 'stdio' | 'http' | 'grpc' | 'websocket';

export interface Agent {
  id: string;
  name: string;
  version: string;
  description: string;
  capabilities: string[];
  transport: AgentTransport;
  endpoint?: string;
  mcp_server?: string;
  tools: string[];
  input_schema?: Record<string, unknown>;
  output_schema?: Record<string, unknown>;
  timeout_ms: number;
  max_concurrent: number;
  retry_policy?: Record<string, unknown>;
  tags: string[];
  owner?: string;
  status: AgentStatus;
  created_at: string;
  updated_at: string;
  last_heartbeat?: string;
}

export interface AgentState {
  agent_id: string;
  status: AgentStatus;
  current_task_id?: string;
  queue_depth: number;
  last_heartbeat: string;
  resource_usage?: {
    cpu_percent?: number;
    memory_mb?: number;
    disk_percent?: number;
  };
  metrics?: Record<string, unknown>;
  updated_at: string;
}

export interface AgentWithState extends Agent {
  state?: AgentState;
}

// ============ Service Types ============

export type ServiceStatus = 'healthy' | 'degraded' | 'unhealthy' | 'offline' | 'unknown';
export type ServiceType = 'application' | 'database' | 'queue' | 'external';
export type ServiceProtocol = 'http' | 'grpc' | 'tcp' | 'websocket';

export interface Service {
  id: string;
  name: string;
  description?: string;
  service_type: ServiceType;
  endpoint?: string;
  health_endpoint?: string;
  protocol: ServiceProtocol;
  port?: number;
  status: ServiceStatus;
  last_check?: string;
  metadata?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface ServiceHealth {
  id: string;
  service_id: string;
  status: ServiceStatus;
  response_time_ms?: number;
  status_code?: number;
  error_message?: string;
  checked_at: string;
}

export interface HealthSummary {
  total_services: number;
  healthy_count: number;
  degraded_count: number;
  unhealthy_count: number;
  offline_count: number;
  overall_status: ServiceStatus;
}

// ============ Topology Types ============

export type NodeType = 'service' | 'agent' | 'database' | 'external';
export type EdgeType = 'data_flow' | 'health_dependency' | 'agent_delegation' | 'api_call';
export type EdgeDirection = 'outbound' | 'inbound' | 'bidirectional';

export interface TopologyNode {
  id: string;
  type: NodeType;
  name: string;
  status: ServiceStatus | AgentStatus;
  service_type?: ServiceType;
  capabilities?: string[];
}

export interface TopologyEdge {
  id: string;
  source: string;
  target: string;
  type: EdgeType;
  direction: EdgeDirection;
}

export interface Topology {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
}

// ============ Metrics Types ============

export interface JobStats {
  source: string;
  job_type: string;
  total_count: number;
  completed_count: number;
  failed_count: number;
  processing_count: number;
  queued_count: number;
  avg_duration_ms?: number;
  success_rate?: number;
}

export interface AgentStats {
  total_agents: number;
  active_agents: number;
  idle_agents: number;
  busy_agents: number;
  offline_agents: number;
  pending_jobs: number;
  processing_jobs: number;
}

// ============ API Types ============

export interface JobsFilters {
  source?: string;
  job_type?: string;
  status?: JobStatus;
  limit?: number;
  offset?: number;
}

export interface AgentsFilters {
  capabilities?: string[];
  status?: AgentStatus[];
  tags?: string[];
  tools?: string[];
  limit?: number;
}

export interface ObservabilityResponse<T> {
  data: T;
  error?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

// ============ AI SQL Types ============

export interface AISQLRequest {
  prompt: string;
  projectRef?: string;
}

export interface AISQLResponse {
  sql: string;
  explanation?: string;
}
