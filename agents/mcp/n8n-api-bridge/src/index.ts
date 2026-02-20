/**
 * n8n API Bridge
 *
 * Public exports for n8n Public API client
 */

export {
  N8nClient,
  N8nApiError,
  getN8nClient,
  resetN8nClient,
  type Workflow,
  type WorkflowDetail,
  type Execution,
  type ExecutionDetail,
  type AuditEvent,
  type ListWorkflowsOptions,
  type ListExecutionsOptions,
} from './n8nClient.js';

export {
  type ExecutionStatus,
  type ExecutionMode,
  type WorkflowTag,
  type WorkflowNode,
  type ExecutionError,
  type ExecutionResultData,
  type ExecutionData,
} from './types.js';
