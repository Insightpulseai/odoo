/**
 * Audit event contract — every agent interaction produces an audit record.
 * Mirrors: agents/foundry/ipai-odoo-copilot-azure/telemetry-contract.md
 */

import { ContextEnvelope } from './context.js';
import { ToolCallRecord } from './response.js';

/** Audit event severity */
export type AuditSeverity = 'info' | 'warning' | 'error' | 'critical';

/** Audit event type taxonomy */
export type AuditEventType =
  | 'copilot_chat_request'
  | 'copilot_chat_response'
  | 'copilot_chat_fallback'
  | 'copilot_blocked'
  | 'copilot_redirected'
  | 'copilot_safety_trigger'
  | 'copilot_tool_request'
  | 'copilot_tool_permitted'
  | 'copilot_tool_denied'
  | 'copilot_tool_error'
  | 'copilot_health_probe'
  | 'copilot_auth_failure'
  | 'copilot_run_timeout';

/**
 * A structured audit event emitted by the runtime.
 */
export interface AuditEvent {
  /** UUID v4 event ID */
  event_id: string;

  /** Correlation ID linking to the originating request */
  request_id: string;

  /** ISO 8601 timestamp */
  timestamp: string;

  /** Event type from the taxonomy */
  event_type: AuditEventType;

  /** Severity level */
  severity: AuditSeverity;

  /** Context envelope snapshot (user_id anonymized for external telemetry) */
  context: Partial<ContextEnvelope>;

  /** Channel of origin */
  channel: string;

  /** Event-specific dimensions */
  dimensions: Record<string, unknown>;

  /** Tool calls associated with this event */
  tool_calls?: ToolCallRecord[];

  /** Latency in milliseconds */
  latency_ms?: number;

  /** Whether the request was blocked */
  blocked?: boolean;

  /** Reason for blocking */
  block_reason?: string;
}

/**
 * Audit emitter interface — implemented by the runtime.
 */
export interface AuditEmitter {
  /** Emit an audit event (fire-and-forget, never blocks request path) */
  emit(event: AuditEvent): void;

  /** Flush pending events (for graceful shutdown) */
  flush(): Promise<void>;
}
