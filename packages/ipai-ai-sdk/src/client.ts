/**
 * InsightPulseAI Platform SDK - AI Client
 * Phase 5B: SaaS Platform Kit - SDK Creation
 *
 * TypeScript/JavaScript client for InsightPulseAI AI services.
 *
 * @example
 * ```typescript
 * import { AIClient } from '@ipai/ai-sdk';
 *
 * const client = new AIClient({
 *   supabaseUrl: 'https://PROJECT.supabase.co',
 *   apiKey: 'your-api-key'
 * });
 *
 * const result = await client.askQuestion({
 *   question: 'What is RAG?'
 * });
 *
 * console.log(result.answer);
 * ```
 */

import type {
  AIClientConfig,
  AskQuestionParams,
  AskQuestionResponse,
  HealthCheckResponse
} from './types';
import { AIError, AIErrorCode } from './types';
import { parseHTTPError, parseNetworkError, validateConfig } from './errors';

/**
 * InsightPulseAI AI Client
 */
export class AIClient {
  private supabaseUrl: string;
  private apiKey: string;
  private defaultOrgId?: string;
  private timeout: number;
  private debug: boolean;

  /**
   * Create AI client instance
   *
   * @param config - Client configuration
   * @throws {AIError} If configuration is invalid
   */
  constructor(config: AIClientConfig) {
    // Validate configuration
    const configError = validateConfig(config.supabaseUrl, config.apiKey);
    if (configError) {
      throw configError;
    }

    this.supabaseUrl = config.supabaseUrl.replace(/\/$/, ''); // Remove trailing slash
    this.apiKey = config.apiKey;
    this.defaultOrgId = config.defaultOrgId;
    this.timeout = config.timeout || 30000;
    this.debug = config.debug || false;

    this.log('Client initialized', { supabaseUrl: this.supabaseUrl });
  }

  /**
   * Ask a question to the AI service
   *
   * @param params - Question parameters
   * @returns AI response with answer and sources
   * @throws {AIError} If request fails
   */
  async askQuestion(params: AskQuestionParams): Promise<AskQuestionResponse> {
    this.log('askQuestion called', params);

    // Validate question
    if (!params.question || !params.question.trim()) {
      throw new AIError(
        AIErrorCode.INVALID_REQUEST,
        'Question text is required'
      );
    }

    // Build request body
    const body = {
      question: params.question.trim(),
      org_id: params.org_id || this.defaultOrgId,
      filters: params.filters || {},
      max_chunks: params.max_chunks || 5
    };

    // Call Edge Function
    try {
      const response = await this.fetchWithTimeout(
        `${this.supabaseUrl}/functions/v1/docs-ai-ask`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(body)
        },
        this.timeout
      );

      // Handle non-OK responses
      if (!response.ok) {
        const errorBody = await response.text();
        throw parseHTTPError(response, errorBody);
      }

      // Parse response
      const result: AskQuestionResponse = await response.json();

      this.log('askQuestion success', {
        answer_length: result.answer.length,
        sources_count: result.sources.length,
        confidence: result.confidence
      });

      return result;

    } catch (error) {
      // Network/fetch errors
      if (error instanceof TypeError || error.name === 'AbortError') {
        throw parseNetworkError(error as Error);
      }

      // Already an AIError
      if (error instanceof AIError) {
        throw error;
      }

      // Unknown error
      throw new AIError(
        AIErrorCode.UNKNOWN_ERROR,
        error instanceof Error ? error.message : 'Unknown error occurred'
      );
    }
  }

  /**
   * Check AI service health and configuration
   *
   * @returns Health check response
   */
  async healthCheck(): Promise<HealthCheckResponse> {
    this.log('healthCheck called');

    try {
      const response = await this.fetchWithTimeout(
        `${this.supabaseUrl}/functions/v1/docs-ai-ask`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ question: 'health check' })
        },
        10000 // Shorter timeout for health check
      );

      return {
        configured: true,
        edge_function: response.ok,
        openai_fallback: false, // Unknown from client side
        edge_function_status: response.status,
        test_result: response.ok
          ? 'Edge Function reachable'
          : `HTTP ${response.status}: ${response.statusText}`
      };

    } catch (error) {
      // Service unreachable
      if (error instanceof TypeError || error.name === 'AbortError') {
        return {
          configured: true,
          edge_function: false,
          openai_fallback: false,
          edge_function_status: 'UNREACHABLE',
          test_result: 'Edge Function unreachable - check network or deployment'
        };
      }

      // Auth error
      if (error instanceof AIError && error.code === AIErrorCode.AUTH_ERROR) {
        return {
          configured: false,
          edge_function: false,
          openai_fallback: false,
          error: 'Authentication failed - check API key'
        };
      }

      // Other error
      return {
        configured: false,
        edge_function: false,
        openai_fallback: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Fetch with timeout support
   */
  private async fetchWithTimeout(
    url: string,
    options: RequestInit,
    timeout: number
  ): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal
      });
      return response;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  /**
   * Debug logging
   */
  private log(message: string, data?: any): void {
    if (this.debug) {
      console.log(`[IPAI AI SDK] ${message}`, data || '');
    }
  }
}
