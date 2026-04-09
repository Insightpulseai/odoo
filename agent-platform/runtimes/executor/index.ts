// Agent Executor — runs agent logic within safety boundaries
// TODO: Implement execution sandbox with tool allowlist and timeout enforcement

export interface ExecutionContext {
  agentId: string;
  sessionId: string;
  tools: string[];
  maxTokens: number;
  timeoutMs: number;
}

export interface ExecutionResult {
  output: unknown;
  toolCalls: number;
  durationMs: number;
  status: "completed" | "timeout" | "error";
}

export class AgentExecutor {
  async execute(context: ExecutionContext, input: unknown): Promise<ExecutionResult> {
    // TODO: Load agent manifest and validate tool allowlist
    // TODO: Execute within timeout boundary
    // TODO: Enforce safety policy from ssot/policies/safety-policy.yaml
    throw new Error("NotImplemented: agent executor");
  }
}
