// Agent Orchestrator — entry point
// TODO: Implement orchestration loop (resolve agent manifest -> route -> execute -> checkpoint)

export interface AgentRequest {
  agentId: string;
  input: unknown;
  sessionId?: string;
}

export interface AgentResponse {
  output: unknown;
  status: "success" | "error";
  traceId: string;
}

export class AgentOrchestrator {
  async dispatch(request: AgentRequest): Promise<AgentResponse> {
    // TODO: Resolve agent manifest from agents/ registry
    // TODO: Route to executor based on agent type
    // TODO: Handle checkpointing for long-running sessions
    // TODO: Emit telemetry events
    throw new Error("NotImplemented: orchestrator dispatch");
  }
}
