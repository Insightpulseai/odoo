// Runtime API — HTTP surface for agent dispatch and health
// TODO: Replace with full Hono or Express implementation

import type { AgentRequest, AgentResponse } from "../../runtimes/orchestrator/index";

export interface RuntimeApiConfig {
  port: number;
  host: string;
}

export class RuntimeApi {
  private config: RuntimeApiConfig;

  constructor(config: RuntimeApiConfig) {
    this.config = config;
  }

  /** GET /health */
  async health(): Promise<{ status: string; timestamp: string }> {
    return {
      status: "ok",
      timestamp: new Date().toISOString(),
    };
  }

  /** POST /dispatch */
  async dispatch(request: AgentRequest): Promise<AgentResponse> {
    // TODO: Forward to AgentOrchestrator
    throw new Error("NotImplemented: runtime-api dispatch");
  }

  async start(): Promise<void> {
    // TODO: Bind HTTP server on config.port
    throw new Error("NotImplemented: runtime-api start");
  }
}
