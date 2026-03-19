export interface FoundryAdapterConfig {
  endpoint: string;
  projectConnectionString?: string;
  modelDeploymentName?: string;
  agentId?: string;
  agentName: string;
  timeoutMs: number;
}

export interface FoundryExecutionResult {
  rawText: string;
  agentId?: string;
  conversationId?: string;
  responseId?: string;
  finishReason?: string;
}

export interface FoundryAgentEnsureResult {
  agentId: string;
  reused: boolean;
}
