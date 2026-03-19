/**
 * Skill contracts — typed definitions for the Copilot Skills framework.
 *
 * Skills are discrete, well-typed capabilities that can be registered,
 * routed, and executed through the orchestrator. Each skill has:
 * - A definition (schema, policy, observability)
 * - An execution context (identity, permissions, correlation)
 * - A structured result (output, citations, telemetry)
 */

/** Classification of what a skill does */
export type SkillType = 'retrieval' | 'summarization' | 'extraction' | 'routing' | 'action';

/** What level of access a skill requires */
export type SkillCapability = 'read_only' | 'read_write' | 'advisory';

/**
 * Static definition of a skill — registered at startup, immutable at runtime.
 */
export interface SkillDefinition {
  /** Human-readable name */
  name: string;
  /** Unique slug (dot-separated namespace) */
  slug: string;
  /** Semver version */
  version: string;
  /** What this skill does */
  description: string;
  /** Skill classification */
  type: SkillType;
  /** Required capability level */
  capability: SkillCapability;
  /** JSON Schema for input validation */
  inputSchema: Record<string, unknown>;
  /** JSON Schema for output shape */
  outputSchema: Record<string, unknown>;
  /** Tools this skill is allowed to invoke */
  allowedTools: string[];
  /** Hints for model selection */
  modelHints: { preferredDeployment?: string; temperature?: number; maxTokens?: number };
  /** Maximum execution time before timeout */
  timeoutMs: number;
  /** Retry configuration */
  retryPolicy: { maxRetries: number; backoffMs: number };
  /** Tags for telemetry/observability */
  observabilityTags: string[];
  /** Owning team/domain */
  owner: string;
  /** Whether this skill is deprecated (will not be routed) */
  deprecated: boolean;
}

/**
 * Runtime context for a skill invocation — injected server-side.
 */
export interface SkillExecutionContext {
  /** Unique request identifier */
  requestId: string;
  /** Authenticated user */
  userId: string;
  /** Tenant for multi-tenancy */
  tenantId: string;
  /** Odoo company scope */
  companyId: number;
  /** Runtime mode (e.g. PROD-ADVISORY) */
  mode: string;
  /** Tools the caller is permitted to use */
  permittedTools: string[];
  /** Correlation ID for distributed tracing */
  correlationId: string;
}

/**
 * A request to invoke a skill.
 */
export interface SkillInvocation {
  /** Which skill to execute */
  skillSlug: string;
  /** Input payload (validated against skill's inputSchema) */
  input: Record<string, unknown>;
  /** Server-injected execution context */
  context: SkillExecutionContext;
}

/**
 * Result of a skill execution.
 */
export interface SkillResult {
  /** Whether the skill executed successfully */
  success: boolean;
  /** Which skill was executed */
  skillSlug: string;
  /** Structured output */
  output: Record<string, unknown>;
  /** Source citations for grounded responses */
  citations?: Array<{ title: string; source: string; snippet: string }>;
  /** Execution time in milliseconds */
  latencyMs: number;
  /** Token usage if a model was invoked */
  tokensUsed?: { prompt: number; completion: number };
  /** Error details if success is false */
  error?: SkillError;
}

/**
 * Structured error from a skill execution.
 */
export interface SkillError {
  /** Machine-readable error code */
  code: string;
  /** Human-readable error message */
  message: string;
  /** Whether the caller should retry */
  retryable: boolean;
}
