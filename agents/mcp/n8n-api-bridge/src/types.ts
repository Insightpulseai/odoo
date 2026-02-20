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

// ============================================================================
// Configuration Types
// ============================================================================

export interface N8nConfig {
  baseUrl: string;
  apiKey: string;
  requestTimeout: number;
  allowMutations: boolean;
}

export interface McpServerConfig {
  port: number;
  logLevel: 'debug' | 'info' | 'warn' | 'error';
}

// ============================================================================
// API Response Types
// ============================================================================

export interface N8nWorkflow {
  id: string;
  name: string;
  active: boolean;
  createdAt: string;
  updatedAt: string;
  tags?: WorkflowTag[];
  nodes?: WorkflowNode[];
  connections?: Record<string, unknown>;
  settings?: Record<string, unknown>;
}

export interface N8nExecution {
  id: string;
  workflowId: string;
  workflowName?: string;
  mode: ExecutionMode;
  status: ExecutionStatus;
  startedAt: string;
  stoppedAt?: string;
  finished: boolean;
  data?: ExecutionData;
}

export interface N8nCredential {
  id: string;
  name: string;
  type: string;
  createdAt: string;
  updatedAt: string;
}

export interface N8nTag {
  id: string;
  name: string;
  createdAt: string;
  updatedAt: string;
}

export interface N8nPaginatedResponse<T> {
  data: T[];
  nextCursor?: string;
}

// ============================================================================
// Error Types
// ============================================================================

export class N8nApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public responseBody?: unknown,
  ) {
    super(message);
    this.name = 'N8nApiError';
  }
}

export class MutationNotAllowedError extends Error {
  constructor(operation: string) {
    super(`Mutation not allowed: ${operation}. Set ALLOW_MUTATIONS=true to enable.`);
    this.name = 'MutationNotAllowedError';
  }
}

export class ConfigurationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ConfigurationError';
  }
}

// ============================================================================
// Zod Schemas for Parameter Validation
// ============================================================================

import { z } from 'zod';

// Workflow parameter schemas
export const ListWorkflowsParamsSchema = z.object({
  active: z.boolean().optional(),
  tags: z.array(z.string()).optional(),
  limit: z.number().int().positive().max(100).optional(),
  cursor: z.string().optional(),
});

export const GetWorkflowParamsSchema = z.object({
  workflowId: z.string().min(1),
});

export const ActivateWorkflowParamsSchema = z.object({
  workflowId: z.string().min(1),
});

export const DeactivateWorkflowParamsSchema = z.object({
  workflowId: z.string().min(1),
});

export const TriggerWorkflowParamsSchema = z.object({
  workflowId: z.string().min(1),
  data: z.record(z.unknown()).optional(),
});

// Execution parameter schemas
export const ListExecutionsParamsSchema = z.object({
  workflowId: z.string().optional(),
  status: z.enum(['success', 'error', 'waiting', 'canceled', 'running']).optional(),
  limit: z.number().int().positive().max(100).optional(),
  cursor: z.string().optional(),
});

export const GetExecutionParamsSchema = z.object({
  executionId: z.string().min(1),
  includeData: z.boolean().optional().default(true),
});

export const DeleteExecutionParamsSchema = z.object({
  executionId: z.string().min(1),
});

export const RetryExecutionParamsSchema = z.object({
  executionId: z.string().min(1),
});

// Audit parameter schema
export const AuditEventParamsSchema = z.object({
  eventName: z.string().min(1),
  userId: z.string().optional(),
  metadata: z.record(z.unknown()).optional(),
});

// Credential parameter schemas
export const ListCredentialsParamsSchema = z.object({
  limit: z.number().int().positive().max(100).optional(),
  cursor: z.string().optional(),
});

// Tag parameter schemas
export const ListTagsParamsSchema = z.object({
  limit: z.number().int().positive().max(100).optional(),
  cursor: z.string().optional(),
});

// AI Tool parameter schemas
export const ListWorkflowToolsParamsSchema = z.object({
  workflowId: z.string().optional(),
  toolType: z.string().optional(),
});

export const ExecuteWorkflowWithContextParamsSchema = z.object({
  workflowId: z.string().min(1),
  inputData: z.record(z.unknown()).optional(),
  aiContext: z.object({
    message: z.string().optional(),
    variables: z.record(z.unknown()).optional(),
  }).optional(),
});

export const GetToolDefinitionParamsSchema = z.object({
  workflowId: z.string().min(1),
  nodeId: z.string().min(1),
});

// ============================================================================
// MCP Tool Definition
// ============================================================================

/**
 * MCP tool response content
 */
export interface McpToolContent {
  type: 'text' | 'image' | 'resource';
  text?: string;
  data?: string;
  mimeType?: string;
}

/**
 * MCP tool response
 */
export interface McpToolResponse {
  content: McpToolContent[];
  isError?: boolean;
}

/**
 * MCP tool definition
 */
export interface McpToolDefinition {
  name: string;
  description: string;
  inputSchema: z.ZodObject<any>;
  handler: (args: any) => Promise<McpToolResponse>;
}
