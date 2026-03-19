/**
 * Precursor Response — structured output from the agent runtime.
 */

import { CorrelationId } from './request.js';

/** Tool call made during response generation */
export interface ToolCallRecord {
  tool_name: string;
  arguments: Record<string, unknown>;
  result: unknown;
  permitted: boolean;
  latency_ms: number;
}

/**
 * Structured response from the agent platform.
 */
export interface PrecursorResponse {
  /** Correlation ID matching the request */
  request_id: CorrelationId;

  /** ISO 8601 timestamp of response completion */
  timestamp: string;

  /** The agent's response content */
  content: string;

  /** Whether the request was blocked by policy */
  blocked: boolean;

  /** Reason for blocking (empty if not blocked) */
  block_reason: string;

  /** Tool calls made during this response */
  tool_calls: ToolCallRecord[];

  /** Foundry thread ID (for conversation continuity) */
  thread_id?: string;

  /** Token usage */
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
  };

  /** Retrieval hits from knowledge base */
  retrieval_hit_count: number;

  /** Response latency in milliseconds */
  latency_ms: number;
}
