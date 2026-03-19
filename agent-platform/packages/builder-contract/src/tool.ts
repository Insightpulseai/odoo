/**
 * Tool contract — defines the shape of tools available to agents.
 * Mirrors: agents/foundry/ipai-odoo-copilot-azure/tool-definitions.json
 */

/** A tool parameter definition */
export interface ToolParameter {
  type: string;
  description: string;
  items?: ToolParameter;
  properties?: Record<string, ToolParameter>;
  required?: string[];
  default?: unknown;
}

/** A tool function definition (OpenAI function-calling schema) */
export interface ToolFunction {
  name: string;
  description: string;
  parameters: ToolParameter;
}

/** A tool definition as used in the tool manifest */
export interface ToolDefinition {
  type: 'function';
  function: ToolFunction;
}

/** Tool manifest — the full set of tools available to an agent */
export interface ToolManifest {
  version: string;
  stage: number;
  description: string;
  tools: ToolDefinition[];
}

/**
 * Tool execution request — what the orchestrator sends to a tool executor.
 */
export interface ToolExecutionRequest {
  tool_name: string;
  arguments: Record<string, unknown>;
  request_id: string;
  user_id: string;
  mode: string;
}

/**
 * Tool execution result — what a tool executor returns.
 */
export interface ToolExecutionResult {
  tool_name: string;
  success: boolean;
  data: unknown;
  error?: string;
  latency_ms: number;
}
