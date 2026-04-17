// Tool Routing Gateway — routes agent tool calls to backend services
// TODO: Implement service routing with auth, rate limiting, and circuit breaking

export interface ToolCall {
  toolName: string;
  parameters: Record<string, unknown>;
  agentId: string;
  sessionId: string;
}

export interface ToolResult {
  output: unknown;
  durationMs: number;
  status: "success" | "error" | "rate_limited";
}

export class ToolGateway {
  async invoke(call: ToolCall): Promise<ToolResult> {
    // TODO: Resolve tool backend from routing config
    // TODO: Authenticate using managed identity
    // TODO: Apply rate limiting and circuit breaker
    throw new Error("NotImplemented: tool gateway invoke");
  }
}
