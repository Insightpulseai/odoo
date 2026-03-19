/**
 * Precursor Request — structured input to the agent runtime.
 */

import { ContextEnvelope } from './context.js';

/** Unique correlation ID for tracing */
export type CorrelationId = string;

/** Channel through which the request arrived */
export type Channel = 'discuss' | 'api' | 'widget';

/**
 * A structured precursor request to the agent platform.
 */
export interface PrecursorRequest {
  /** UUID v4 correlation ID — generated at entry point */
  request_id: CorrelationId;

  /** ISO 8601 timestamp of request creation */
  timestamp: string;

  /** The user's prompt / question */
  prompt: string;

  /** Server-computed context envelope */
  context: ContextEnvelope;

  /** Channel of origin */
  channel: Channel;

  /** Optional conversation history (last N turns) */
  conversation_history?: ConversationTurn[];

  /** Optional Foundry thread ID for continuation */
  thread_id?: string;
}

export interface ConversationTurn {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}
