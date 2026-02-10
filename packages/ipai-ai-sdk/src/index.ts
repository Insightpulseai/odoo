/**
 * InsightPulseAI Platform SDK
 * Phase 5B: SaaS Platform Kit - SDK Creation
 *
 * @packageDocumentation
 */

export { AIClient } from './client';
export type {
  AIClientConfig,
  AskQuestionParams,
  AskQuestionResponse,
  ContextSource,
  HealthCheckResponse
} from './types';
export { AIError, AIErrorCode } from './types';
export * from './agentLibrary';
