/**
 * A2A Coordinator - Agent-to-Agent communication orchestration
 *
 * Implements the orchestrator pattern from Microsoft's A2A on MCP:
 * - Intelligent task decomposition
 * - Multi-agent coordination
 * - Context propagation
 * - Error handling and retries
 */

import { v4 as uuidv4 } from "uuid";
import { createClient, SupabaseClient } from "@supabase/supabase-js";
import {
  AgentMessage,
  AgentResponse,
  AgentContext,
  AgentJob,
  MessagePayload,
  MessagePriority,
  RequestType,
  HandoffRequest,
  DelegationRequest,
  AgentError,
} from "./types.js";
import { registry } from "./agent-registry.js";

const SUPABASE_URL = process.env.SUPABASE_URL || "";
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || "";

/**
 * A2A Coordinator for managing inter-agent communication
 */
export class A2ACoordinator {
  private supabase: SupabaseClient | null = null;
  private pendingMessages: Map<string, AgentMessage> = new Map();
  private localResults: Map<string, AgentResponse> = new Map();

  constructor() {
    if (SUPABASE_URL && SUPABASE_SERVICE_KEY) {
      this.supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);
    }
  }

  /**
   * Invoke an agent synchronously
   * Waits for response up to timeout
   */
  async invokeAgent(
    targetAgentId: string,
    payload: MessagePayload,
    context?: Partial<AgentContext>,
    options?: {
      priority?: MessagePriority;
      timeout_ms?: number;
    }
  ): Promise<AgentResponse> {
    const agent = await registry.get(targetAgentId);
    if (!agent) {
      return this.createErrorResponse(
        "",
        targetAgentId,
        {
          code: "AGENT_NOT_FOUND",
          message: `Agent ${targetAgentId} not found in registry`,
          recoverable: false,
        },
        0
      );
    }

    const message = this.createMessage(
      context?.caller_agent_id || "coordinator",
      targetAgentId,
      "tool_call",
      payload,
      context,
      options?.priority || "normal",
      options?.timeout_ms || agent.timeout_ms
    );

    // Store message for tracking
    await this.storeMessage(message);

    try {
      // Route based on transport type
      const startTime = Date.now();
      let result: unknown;

      switch (agent.transport) {
        case "http":
          result = await this.invokeHttp(agent.endpoint!, payload, message);
          break;
        case "stdio":
          // For stdio agents, we queue the job for the pulser to handle
          result = await this.queueForStdio(message);
          break;
        default:
          throw new Error(`Unsupported transport: ${agent.transport}`);
      }

      const executionTime = Date.now() - startTime;
      const response = this.createSuccessResponse(
        message.message_id,
        targetAgentId,
        result,
        executionTime
      );

      await this.storeResponse(response);
      return response;
    } catch (error) {
      const executionTime = Date.now() - Date.parse(message.created_at);
      const response = this.createErrorResponse(
        message.message_id,
        targetAgentId,
        {
          code: "INVOCATION_FAILED",
          message: error instanceof Error ? error.message : String(error),
          recoverable: true,
          suggested_retry: true,
        },
        executionTime
      );

      await this.storeResponse(response);
      return response;
    }
  }

  /**
   * Submit an async job to an agent
   * Returns immediately with job ID
   */
  async submitJob(
    sourceAgentId: string,
    targetAgentId: string,
    payload: MessagePayload,
    context?: Partial<AgentContext>,
    options?: {
      priority?: MessagePriority;
      max_retries?: number;
    }
  ): Promise<AgentJob> {
    const job: AgentJob = {
      job_id: uuidv4(),
      source_agent_id: sourceAgentId,
      target_agent_id: targetAgentId,
      request_type: "tool_call",
      payload,
      context: this.buildContext(sourceAgentId, context),
      priority: options?.priority || "normal",
      status: "queued",
      created_at: new Date().toISOString(),
      retry_count: 0,
      max_retries: options?.max_retries || 3,
    };

    if (this.supabase) {
      const { error } = await this.supabase.from("agent_jobs").insert(job);

      if (error) {
        throw new Error(`Job submission failed: ${error.message}`);
      }
    }

    return job;
  }

  /**
   * Get job status
   */
  async getJobStatus(jobId: string): Promise<AgentJob | null> {
    if (this.supabase) {
      const { data, error } = await this.supabase
        .from("agent_jobs")
        .select("*")
        .eq("job_id", jobId)
        .single();

      if (error) {
        if (error.code === "PGRST116") return null;
        throw new Error(`Get job failed: ${error.message}`);
      }

      return data;
    }

    return null;
  }

  /**
   * Cancel a queued job
   */
  async cancelJob(jobId: string): Promise<boolean> {
    if (this.supabase) {
      const { data, error } = await this.supabase
        .from("agent_jobs")
        .update({ status: "cancelled" })
        .eq("job_id", jobId)
        .eq("status", "queued")
        .select();

      if (error) {
        throw new Error(`Cancel failed: ${error.message}`);
      }

      return (data?.length || 0) > 0;
    }

    return false;
  }

  /**
   * Handoff conversation to another agent
   */
  async handoff(request: HandoffRequest): Promise<AgentResponse> {
    const message = this.createMessage(
      request.from_agent_id,
      request.to_agent_id,
      "handoff",
      {
        data: {
          reason: request.reason,
          conversation_context: request.conversation_context,
          memory_refs: request.memory_refs,
          user_intent: request.user_intent,
        },
      },
      undefined,
      "high",
      30000
    );

    await this.storeMessage(message);

    // Notify target agent of handoff
    return this.invokeAgent(
      request.to_agent_id,
      message.payload,
      {
        caller_agent_id: request.from_agent_id,
        memory_refs: request.memory_refs,
      },
      { priority: "high" }
    );
  }

  /**
   * Delegate task to another agent with constraints
   */
  async delegate(request: DelegationRequest): Promise<AgentJob> {
    const context: Partial<AgentContext> = {
      caller_agent_id: request.delegator_id,
      deadline: request.constraints?.timeout_ms
        ? new Date(Date.now() + request.constraints.timeout_ms).toISOString()
        : undefined,
    };

    return this.submitJob(
      request.delegator_id,
      request.delegate_id,
      request.task,
      context,
      { priority: "normal" }
    );
  }

  /**
   * Broadcast message to multiple agents
   */
  async broadcast(
    fromAgentId: string,
    targetAgentIds: string[],
    payload: MessagePayload,
    context?: Partial<AgentContext>
  ): Promise<Map<string, AgentResponse>> {
    const results = new Map<string, AgentResponse>();

    const promises = targetAgentIds.map(async (targetId) => {
      try {
        const response = await this.invokeAgent(targetId, payload, {
          ...context,
          caller_agent_id: fromAgentId,
        });
        results.set(targetId, response);
      } catch (error) {
        results.set(
          targetId,
          this.createErrorResponse(
            "",
            targetId,
            {
              code: "BROADCAST_FAILED",
              message: error instanceof Error ? error.message : String(error),
              recoverable: true,
            },
            0
          )
        );
      }
    });

    await Promise.all(promises);
    return results;
  }

  /**
   * Find and invoke best agent for a capability
   */
  async invokeByCapability(
    capability: string,
    payload: MessagePayload,
    context?: Partial<AgentContext>
  ): Promise<AgentResponse> {
    const agents = await registry.findActiveByCapability(capability);

    if (agents.length === 0) {
      return this.createErrorResponse(
        "",
        "unknown",
        {
          code: "NO_CAPABLE_AGENT",
          message: `No active agent found with capability: ${capability}`,
          recoverable: false,
        },
        0
      );
    }

    // Select agent with lowest queue depth (simple load balancing)
    let selectedAgent = agents[0];
    let lowestQueue = Infinity;

    for (const agent of agents) {
      const state = await registry.getState(agent.id);
      if (state && state.queue_depth < lowestQueue) {
        lowestQueue = state.queue_depth;
        selectedAgent = agent;
      }
    }

    return this.invokeAgent(selectedAgent.id, payload, context);
  }

  /**
   * List pending jobs for an agent
   */
  async listPendingJobs(
    agentId: string,
    limit: number = 20
  ): Promise<AgentJob[]> {
    if (this.supabase) {
      const { data, error } = await this.supabase
        .from("agent_jobs")
        .select("*")
        .eq("target_agent_id", agentId)
        .in("status", ["queued", "processing"])
        .order("created_at", { ascending: true })
        .limit(limit);

      if (error) {
        throw new Error(`List jobs failed: ${error.message}`);
      }

      return data || [];
    }

    return [];
  }

  /**
   * Get message history between agents
   */
  async getMessageHistory(
    agentId1: string,
    agentId2: string,
    limit: number = 50
  ): Promise<AgentMessage[]> {
    if (this.supabase) {
      const { data, error } = await this.supabase
        .from("agent_messages")
        .select("*")
        .or(
          `and(from_agent_id.eq.${agentId1},to_agent_id.eq.${agentId2}),` +
            `and(from_agent_id.eq.${agentId2},to_agent_id.eq.${agentId1})`
        )
        .order("created_at", { ascending: false })
        .limit(limit);

      if (error) {
        throw new Error(`Get history failed: ${error.message}`);
      }

      return data || [];
    }

    return [];
  }

  // Private helpers

  private createMessage(
    fromAgentId: string,
    toAgentId: string,
    requestType: RequestType,
    payload: MessagePayload,
    context?: Partial<AgentContext>,
    priority: MessagePriority = "normal",
    timeout_ms: number = 30000
  ): AgentMessage {
    return {
      message_id: uuidv4(),
      from_agent_id: fromAgentId,
      to_agent_id: toAgentId,
      request_type: requestType,
      payload,
      context: this.buildContext(fromAgentId, context),
      priority,
      timeout_ms,
      requires_ack: true,
      created_at: new Date().toISOString(),
      expires_at: new Date(Date.now() + timeout_ms).toISOString(),
    };
  }

  private buildContext(
    callerId: string,
    partial?: Partial<AgentContext>
  ): AgentContext {
    const existingChain = partial?.call_chain || [];
    return {
      session_id: partial?.session_id || uuidv4(),
      caller_agent_id: callerId,
      call_chain: [...existingChain, callerId],
      workspace: partial?.workspace,
      parent_message_id: partial?.parent_message_id,
      deadline: partial?.deadline,
      trace_id: partial?.trace_id || uuidv4(),
      memory_refs: partial?.memory_refs,
    };
  }

  private createSuccessResponse(
    messageId: string,
    fromAgentId: string,
    result: unknown,
    executionTime: number
  ): AgentResponse {
    return {
      message_id: uuidv4(),
      in_reply_to: messageId,
      from_agent_id: fromAgentId,
      status: "success",
      result,
      execution_time_ms: executionTime,
      created_at: new Date().toISOString(),
    };
  }

  private createErrorResponse(
    messageId: string,
    fromAgentId: string,
    error: AgentError,
    executionTime: number
  ): AgentResponse {
    return {
      message_id: uuidv4(),
      in_reply_to: messageId,
      from_agent_id: fromAgentId,
      status: "error",
      error,
      execution_time_ms: executionTime,
      created_at: new Date().toISOString(),
    };
  }

  private async storeMessage(message: AgentMessage): Promise<void> {
    this.pendingMessages.set(message.message_id, message);

    if (this.supabase) {
      await this.supabase.from("agent_messages").insert(message);
    }
  }

  private async storeResponse(response: AgentResponse): Promise<void> {
    this.localResults.set(response.in_reply_to, response);

    if (this.supabase) {
      await this.supabase.from("agent_responses").insert(response);
    }
  }

  private async invokeHttp(
    endpoint: string,
    payload: MessagePayload,
    message: AgentMessage
  ): Promise<unknown> {
    const response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Message-ID": message.message_id,
        "X-Caller-Agent": message.from_agent_id,
        "X-Trace-ID": message.context?.trace_id || "",
      },
      body: JSON.stringify({
        tool_name: payload.tool_name,
        arguments: payload.arguments,
        context: message.context,
      }),
      signal: AbortSignal.timeout(message.timeout_ms),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${await response.text()}`);
    }

    return response.json();
  }

  private async queueForStdio(message: AgentMessage): Promise<unknown> {
    // For stdio agents, submit to mcp-jobs queue
    if (this.supabase) {
      const { data, error } = await this.supabase.rpc("enqueue_job", {
        p_source: message.from_agent_id,
        p_job_type: "agent_invocation",
        p_payload: {
          target_agent_id: message.to_agent_id,
          message_id: message.message_id,
          payload: message.payload,
          context: message.context,
        },
        p_priority: message.priority === "critical" ? 1 : message.priority === "high" ? 3 : 5,
      });

      if (error) {
        throw new Error(`Queue failed: ${error.message}`);
      }

      return { queued: true, job_id: data };
    }

    throw new Error("Supabase not configured for stdio agent invocation");
  }
}

// Singleton instance
export const coordinator = new A2ACoordinator();
