/**
 * Agent-to-Agent (A2A) Communication Types
 *
 * Based on Microsoft's A2A on MCP pattern:
 * https://developer.microsoft.com/blog/can-you-build-agent2agent-communication-on-mcp-yes
 */

/**
 * Transport type for agent communication
 */
export type AgentTransport = "stdio" | "http" | "grpc" | "websocket";

/**
 * Agent capability categories
 */
export type AgentCapability =
  | "odoo_erp"
  | "finance"
  | "hr"
  | "inventory"
  | "sales"
  | "analytics"
  | "infrastructure"
  | "deployment"
  | "documentation"
  | "research"
  | "code_generation"
  | "testing"
  | "monitoring"
  | "custom";

/**
 * Agent status in the registry
 */
export type AgentStatus =
  | "active"
  | "idle"
  | "busy"
  | "offline"
  | "maintenance";

/**
 * Message priority levels
 */
export type MessagePriority = "critical" | "high" | "normal" | "low";

/**
 * Request types for inter-agent communication
 */
export type RequestType =
  | "tool_call"
  | "query"
  | "stream"
  | "event"
  | "handoff"
  | "delegate";

/**
 * Agent metadata for registry
 */
export interface AgentMetadata {
  id: string;
  name: string;
  version: string;
  description: string;
  capabilities: AgentCapability[];
  transport: AgentTransport;
  endpoint?: string;
  mcp_server?: string;
  tools?: string[];
  input_schema?: Record<string, unknown>;
  output_schema?: Record<string, unknown>;
  timeout_ms: number;
  max_concurrent: number;
  retry_policy?: RetryPolicy;
  tags?: string[];
  owner?: string;
  created_at: string;
  updated_at: string;
  last_heartbeat?: string;
}

/**
 * Retry policy configuration
 */
export interface RetryPolicy {
  max_retries: number;
  initial_delay_ms: number;
  max_delay_ms: number;
  backoff_multiplier: number;
}

/**
 * Agent context for propagation across calls
 */
export interface AgentContext {
  session_id: string;
  caller_agent_id: string;
  call_chain: string[];
  workspace?: WorkspaceContext;
  parent_message_id?: string;
  deadline?: string;
  trace_id?: string;
  memory_refs?: string[];
}

/**
 * Workspace context for Odoo/IPAI environment
 */
export interface WorkspaceContext {
  odoo_instance: "odoo_lab" | "odoo_erp" | "odoo_prod";
  database?: string;
  company_id?: number;
  user_id?: number;
  timezone?: string;
}

/**
 * Inter-agent message format
 */
export interface AgentMessage {
  message_id: string;
  from_agent_id: string;
  to_agent_id: string;
  request_type: RequestType;
  payload: MessagePayload;
  context?: AgentContext;
  priority: MessagePriority;
  timeout_ms: number;
  requires_ack: boolean;
  created_at: string;
  expires_at?: string;
}

/**
 * Message payload variants
 */
export interface MessagePayload {
  tool_name?: string;
  arguments?: Record<string, unknown>;
  query?: string;
  data?: unknown;
  stream_config?: StreamConfig;
}

/**
 * Stream configuration for streaming responses
 */
export interface StreamConfig {
  chunk_size?: number;
  format?: "json" | "text" | "binary";
  callback_url?: string;
}

/**
 * Response from agent invocation
 */
export interface AgentResponse {
  message_id: string;
  in_reply_to: string;
  from_agent_id: string;
  status: "success" | "error" | "timeout" | "cancelled" | "partial";
  result?: unknown;
  error?: AgentError;
  execution_time_ms: number;
  tokens_used?: number;
  created_at: string;
}

/**
 * Error details for failed invocations
 */
export interface AgentError {
  code: string;
  message: string;
  details?: unknown;
  recoverable: boolean;
  suggested_retry?: boolean;
}

/**
 * Agent state for coordination
 */
export interface AgentState {
  agent_id: string;
  status: AgentStatus;
  current_task_id?: string;
  queue_depth: number;
  last_heartbeat: string;
  resource_usage?: ResourceUsage;
  metrics?: AgentMetrics;
}

/**
 * Resource usage metrics
 */
export interface ResourceUsage {
  cpu_percent?: number;
  memory_mb?: number;
  token_count?: number;
  active_connections?: number;
}

/**
 * Agent performance metrics
 */
export interface AgentMetrics {
  total_requests: number;
  success_count: number;
  error_count: number;
  avg_latency_ms: number;
  p95_latency_ms: number;
  last_hour_requests: number;
}

/**
 * Discovery query for finding agents
 */
export interface DiscoveryQuery {
  capabilities?: AgentCapability[];
  status?: AgentStatus[];
  tags?: string[];
  tools?: string[];
  max_results?: number;
}

/**
 * Job specification for async agent tasks
 */
export interface AgentJob {
  job_id: string;
  source_agent_id: string;
  target_agent_id: string;
  request_type: RequestType;
  payload: MessagePayload;
  context?: AgentContext;
  priority: MessagePriority;
  status: "queued" | "processing" | "completed" | "failed" | "cancelled";
  result?: unknown;
  error?: AgentError;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  retry_count: number;
  max_retries: number;
}

/**
 * Handoff request for transferring conversation
 */
export interface HandoffRequest {
  from_agent_id: string;
  to_agent_id: string;
  reason: string;
  conversation_context: unknown;
  memory_refs?: string[];
  user_intent?: string;
}

/**
 * Delegation request for task assignment
 */
export interface DelegationRequest {
  delegator_id: string;
  delegate_id: string;
  task: MessagePayload;
  constraints?: DelegationConstraints;
  callback?: CallbackConfig;
}

/**
 * Constraints for delegated tasks
 */
export interface DelegationConstraints {
  timeout_ms?: number;
  max_tokens?: number;
  allowed_tools?: string[];
  forbidden_tools?: string[];
  require_approval?: boolean;
}

/**
 * Callback configuration for async results
 */
export interface CallbackConfig {
  url?: string;
  agent_id?: string;
  tool_name?: string;
}
