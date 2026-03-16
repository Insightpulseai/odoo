/**
 * InsightPulseAI Platform SDK - Type Definitions
 * Phase 5B: SaaS Platform Kit - SDK Creation
 */

/**
 * AI question parameters
 */
export interface AskQuestionParams {
  /** Question text to ask the AI */
  question: string;

  /** Organization UUID for multi-tenant scoping (optional, uses default from config) */
  org_id?: string;

  /** Filter context by metadata properties (e.g., { category: 'billing' }) */
  filters?: Record<string, any>;

  /** Maximum number of context chunks to retrieve (default: 5) */
  max_chunks?: number;
}

/**
 * Context source metadata
 */
export interface ContextSource {
  /** Unique chunk identifier */
  chunk_id: string;

  /** Source document title or page name */
  document_title: string;

  /** Semantic similarity score (0.0-1.0) */
  similarity: number;

  /** Original content excerpt */
  content?: string;

  /** Document metadata (tags, categories, etc.) */
  metadata?: Record<string, any>;
}

/**
 * AI question response
 */
export interface AskQuestionResponse {
  /** Generated answer text */
  answer: string;

  /** Context sources used to generate answer */
  sources: ContextSource[];

  /** Confidence score (0.0-1.0) */
  confidence: number;

  /** Unique question identifier for tracking */
  question_id: string;

  /** Tokens used in this request (for billing) */
  tokens_used?: number;
}

/**
 * SDK client configuration
 */
export interface AIClientConfig {
  /** Supabase project URL (e.g., https://PROJECT.supabase.co) */
  supabaseUrl: string;

  /** API key (anon key for frontend, service role for backend) */
  apiKey: string;

  /** Default organization UUID (optional) */
  defaultOrgId?: string;

  /** Request timeout in milliseconds (default: 30000) */
  timeout?: number;

  /** Enable debug logging */
  debug?: boolean;
}

/**
 * SDK error types
 */
export enum AIErrorCode {
  /** Configuration error (missing URL/key) */
  CONFIG_ERROR = 'CONFIG_ERROR',

  /** Network error (timeout, connection refused) */
  NETWORK_ERROR = 'NETWORK_ERROR',

  /** Authentication error (invalid API key) */
  AUTH_ERROR = 'AUTH_ERROR',

  /** Rate limit exceeded */
  RATE_LIMIT_ERROR = 'RATE_LIMIT_ERROR',

  /** Service unavailable (Edge Function down) */
  SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE',

  /** Invalid request parameters */
  INVALID_REQUEST = 'INVALID_REQUEST',

  /** Unknown error */
  UNKNOWN_ERROR = 'UNKNOWN_ERROR'
}

/**
 * SDK error class
 */
export class AIError extends Error {
  constructor(
    public code: AIErrorCode,
    message: string,
    public statusCode?: number,
    public details?: any
  ) {
    super(message);
    this.name = 'AIError';
    Object.setPrototypeOf(this, AIError.prototype);
  }

  /**
   * Check if error is retryable
   */
  get isRetryable(): boolean {
    return [
      AIErrorCode.NETWORK_ERROR,
      AIErrorCode.SERVICE_UNAVAILABLE,
      AIErrorCode.RATE_LIMIT_ERROR
    ].includes(this.code);
  }
}

/**
 * Health check response
 */
export interface HealthCheckResponse {
  /** Configuration valid */
  configured: boolean;

  /** Edge Function reachable */
  edge_function: boolean;

  /** OpenAI fallback configured */
  openai_fallback: boolean;

  /** Organization ID */
  org_id?: string;

  /** Test result message */
  test_result?: string;

  /** HTTP status code */
  edge_function_status?: number | string;

  /** Error details (if unhealthy) */
  error?: string;
}
