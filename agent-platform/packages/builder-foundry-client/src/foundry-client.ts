/**
 * FoundryClient interface — the adapter boundary between orchestration and model execution.
 *
 * Orchestration calls FoundryClient; FoundryClient handles the model backend.
 * Separation: orchestration -> adapter -> tool execution
 */

import type { ContextEnvelope } from '@ipai/builder-contract';

/** A message in a conversation thread */
export interface FoundryMessage {
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string;
  name?: string;
  tool_call_id?: string;
}

/** Tool call from the model */
export interface FoundryToolCall {
  id: string;
  type: 'function';
  function: {
    name: string;
    arguments: string;
  };
}

/** Chat completion request to the Foundry backend */
export interface FoundryChatRequest {
  messages: FoundryMessage[];
  tools?: Array<{
    type: 'function';
    function: {
      name: string;
      description: string;
      parameters: Record<string, unknown>;
    };
  }>;
  temperature?: number;
  max_tokens?: number;
  /** Correlation ID for tracing */
  request_id: string;
}

/** Chat completion response from the Foundry backend */
export interface FoundryChatResponse {
  content: string;
  tool_calls: FoundryToolCall[];
  thread_id?: string;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
  };
  finish_reason: 'stop' | 'tool_calls' | 'length' | 'content_filter';
}

/**
 * Abstract Foundry client interface.
 * All concrete implementations must satisfy this contract.
 */
export interface FoundryClient {
  /** Human-readable name of this client implementation */
  readonly name: string;

  /** Whether this client is configured and ready */
  isConfigured(): boolean;

  /** Execute a chat completion */
  chatCompletion(request: FoundryChatRequest): Promise<FoundryChatResponse>;

  /** Health check — returns true if the backend is reachable */
  healthCheck(): Promise<boolean>;
}
