/**
 * n8n API Type Definitions
 *
 * Shared types for n8n Public API client and MCP tools.
 */

/**
 * Workflow execution status
 */
export type ExecutionStatus = 'success' | 'error' | 'waiting' | 'canceled' | 'running';

/**
 * Workflow execution mode
 */
export type ExecutionMode = 'manual' | 'trigger' | 'webhook' | 'retry';

/**
 * Workflow tag
 */
export interface WorkflowTag {
  id: string;
  name: string;
}

/**
 * Workflow node
 */
export interface WorkflowNode {
  id: string;
  name: string;
  type: string;
  position: [number, number];
  parameters?: Record<string, unknown>;
}

/**
 * Execution error
 */
export interface ExecutionError {
  message: string;
  stack?: string;
}

/**
 * Execution result data
 */
export interface ExecutionResultData {
  runData?: Record<string, unknown[]>;
  error?: ExecutionError;
}

/**
 * Execution data
 */
export interface ExecutionData {
  resultData?: ExecutionResultData;
}
