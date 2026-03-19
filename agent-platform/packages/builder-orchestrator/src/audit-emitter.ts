/**
 * ConsoleAuditEmitter — baseline audit implementation.
 *
 * Logs audit events to stdout in structured JSON format.
 * Production replaces with OpenTelemetry/App Insights emitter.
 *
 * Rules (from telemetry-contract.md):
 * - Fire-and-forget: never blocks the request path
 * - Telemetry failures logged locally, never surfaced to users
 * - User IDs anonymized in external telemetry
 * - PII (prompts, responses) never sent to App Insights
 */

import { randomUUID } from 'node:crypto';
import type {
  AuditEvent,
  AuditEventType,
  AuditSeverity,
  AuditEmitter,
  ContextEnvelope,
  ToolCallRecord,
} from '@ipai/builder-contract';

/**
 * Console-based audit emitter for local development.
 * Production should replace with OpenTelemetry-compatible implementation.
 */
export class ConsoleAuditEmitter implements AuditEmitter {
  private buffer: AuditEvent[] = [];
  private enabled: boolean;

  constructor() {
    this.enabled = process.env['COPILOT_TELEMETRY_ENABLED'] !== 'false';
  }

  emit(event: AuditEvent): void {
    if (!this.enabled) return;

    try {
      this.buffer.push(event);
      // Structured JSON log — machine-parseable
      console.log(JSON.stringify({
        _type: 'audit_event',
        ...event,
        // Anonymize user_id for external logging
        context: event.context ? { ...event.context, user_id: this.anonymize(event.context.user_id) } : undefined,
      }));
    } catch {
      // Rule: telemetry failure never blocks request path
    }
  }

  async flush(): Promise<void> {
    // In a real implementation, this would flush to App Insights / OTel
    this.buffer = [];
  }

  /** Create an audit event with defaults populated */
  static createEvent(params: {
    request_id: string;
    event_type: AuditEventType;
    severity?: AuditSeverity;
    context?: Partial<ContextEnvelope>;
    channel?: string;
    dimensions?: Record<string, unknown>;
    tool_calls?: ToolCallRecord[];
    latency_ms?: number;
    blocked?: boolean;
    block_reason?: string;
  }): AuditEvent {
    return {
      event_id: randomUUID(),
      request_id: params.request_id,
      timestamp: new Date().toISOString(),
      event_type: params.event_type,
      severity: params.severity ?? 'info',
      context: params.context ?? {},
      channel: params.channel ?? 'unknown',
      dimensions: params.dimensions ?? {},
      tool_calls: params.tool_calls,
      latency_ms: params.latency_ms,
      blocked: params.blocked,
      block_reason: params.block_reason,
    };
  }

  /** Get buffered events (for testing) */
  getBuffer(): ReadonlyArray<AuditEvent> {
    return this.buffer;
  }

  private anonymize(value: string | undefined): string {
    if (!value) return '';
    // Simple hash-like anonymization for telemetry
    return `user-${value.slice(0, 4)}***`;
  }
}
