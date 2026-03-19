/**
 * Orchestrator — the core engine that ties everything together.
 *
 * Flow:
 * 1. Accept PrecursorRequest
 * 2. Load agent assets (system prompt, tools, policies)
 * 3. Enforce policy (tool permissions, mode restrictions)
 * 4. Build Foundry request with context envelope
 * 5. Execute via FoundryClient
 * 6. Handle tool calls (if permitted)
 * 7. Emit audit events
 * 8. Return structured PrecursorResponse
 */

import { randomUUID } from 'node:crypto';
import type {
  PrecursorRequest,
  PrecursorResponse,
  ToolCallRecord,
  AuditEmitter,
  ContextEnvelope,
  ToolManifest,
  SkillInvocation,
  SkillResult,
  SkillDefinition,
} from '@ipai/builder-contract';
import type { FoundryClient, FoundryMessage, FoundryToolCall } from '@ipai/builder-foundry-client';
import { AssetLoader, type AgentAssets } from './asset-loader.js';
import { PolicyEngine } from './policy-engine.js';
import { ConsoleAuditEmitter } from './audit-emitter.js';
import { SkillRegistry } from './skill-registry.js';
import { SkillRouter } from './skill-router.js';
import { executeKnowledgeSearch } from './skills/knowledge-search.js';
import { executeBusinessSummarize } from './skills/business-summarize.js';
import { executeWorkflowExtractActions } from './skills/workflow-extract-actions.js';
import { executePlatformRouteRequest } from './skills/platform-route-request.js';

/** Orchestrator configuration */
export interface OrchestratorConfig {
  /** Path to the agents/ repository root */
  agentsRoot: string;
  /** Agent profile to load */
  agentProfile: string;
  /** Foundry client implementation */
  foundryClient: FoundryClient;
  /** Audit emitter implementation (defaults to ConsoleAuditEmitter) */
  auditEmitter?: AuditEmitter;
  /** Model temperature (default 0.4 per system-prompt.md) */
  temperature?: number;
}

/**
 * The Orchestrator — heart of the agent platform runtime.
 */
export class Orchestrator {
  private config: OrchestratorConfig;
  private assets: AgentAssets | null = null;
  private policyEngine: PolicyEngine;
  private auditEmitter: AuditEmitter;
  private skillRegistry: SkillRegistry;
  private skillRouter: SkillRouter;

  constructor(config: OrchestratorConfig) {
    this.config = config;
    this.policyEngine = new PolicyEngine();
    this.auditEmitter = config.auditEmitter ?? new ConsoleAuditEmitter();
    this.skillRegistry = new SkillRegistry();
    this.skillRouter = new SkillRouter(this.skillRegistry);
  }

  /**
   * Initialize the orchestrator: load assets, validate configuration.
   */
  async initialize(): Promise<void> {
    const loader = new AssetLoader({
      agentsRoot: this.config.agentsRoot,
      agentProfile: this.config.agentProfile,
    });

    this.assets = loader.load();

    // Validate Foundry client
    if (!this.config.foundryClient.isConfigured()) {
      console.warn(
        `FoundryClient "${this.config.foundryClient.name}" is not configured. ` +
        `Requests will fail until configuration is provided.`
      );
    }
  }

  /**
   * Execute a precursor request end-to-end.
   */
  async execute(request: PrecursorRequest): Promise<PrecursorResponse> {
    const startTime = Date.now();

    if (!this.assets) {
      throw new Error('Orchestrator not initialized. Call initialize() first.');
    }

    // Emit request audit event
    this.auditEmitter.emit(
      ConsoleAuditEmitter.createEvent({
        request_id: request.request_id,
        event_type: 'copilot_chat_request',
        context: request.context,
        channel: request.channel,
        dimensions: {
          surface: request.context.surface,
          mode: request.context.mode,
          prompt_length: request.prompt.length,
        },
      })
    );

    try {
      // Build messages with context envelope + system prompt
      const messages = this.buildMessages(request);

      // Filter tools by policy
      const permittedTools = this.policyEngine.filterPermittedTools(
        this.assets.toolManifest.tools,
        request.context
      );

      // Execute via Foundry client
      const foundryRequest = {
        messages,
        tools: permittedTools.length > 0
          ? permittedTools.map((t) => ({
              type: 'function' as const,
              function: {
                name: t.function.name,
                description: t.function.description,
                parameters: t.function.parameters as unknown as Record<string, unknown>,
              },
            }))
          : undefined,
        temperature: this.config.temperature ?? 0.4,
        request_id: request.request_id,
      };

      const foundryResponse = await this.config.foundryClient.chatCompletion(foundryRequest);

      // Handle tool calls
      const toolCallRecords: ToolCallRecord[] = [];
      let finalContent = foundryResponse.content;

      if (foundryResponse.tool_calls.length > 0) {
        const toolResults = await this.executeToolCalls(
          foundryResponse.tool_calls,
          request.context,
          request.request_id
        );
        toolCallRecords.push(...toolResults);

        // If tools were called, make a follow-up call with tool results
        // (simplified: in production, this loops until no more tool calls)
        if (toolResults.length > 0) {
          finalContent = toolResults
            .map((r) => (r.permitted ? `Tool ${r.tool_name}: ${JSON.stringify(r.result)}` : `Tool ${r.tool_name}: denied`))
            .join('\n');
        }
      }

      const latencyMs = Date.now() - startTime;

      const response: PrecursorResponse = {
        request_id: request.request_id,
        timestamp: new Date().toISOString(),
        content: finalContent,
        blocked: false,
        block_reason: '',
        tool_calls: toolCallRecords,
        thread_id: foundryResponse.thread_id,
        usage: foundryResponse.usage,
        retrieval_hit_count: 0,
        latency_ms: latencyMs,
      };

      // Emit response audit event
      this.auditEmitter.emit(
        ConsoleAuditEmitter.createEvent({
          request_id: request.request_id,
          event_type: 'copilot_chat_response',
          context: request.context,
          channel: request.channel,
          latency_ms: latencyMs,
          dimensions: {
            prompt_tokens: foundryResponse.usage.prompt_tokens,
            completion_tokens: foundryResponse.usage.completion_tokens,
            tool_call_count: toolCallRecords.length,
          },
        })
      );

      return response;
    } catch (error) {
      const latencyMs = Date.now() - startTime;
      const errorMessage = error instanceof Error ? error.message : String(error);

      // Emit fallback audit event
      this.auditEmitter.emit(
        ConsoleAuditEmitter.createEvent({
          request_id: request.request_id,
          event_type: 'copilot_chat_fallback',
          severity: 'error',
          context: request.context,
          channel: request.channel,
          latency_ms: latencyMs,
          blocked: true,
          block_reason: errorMessage,
          dimensions: { error_reason: errorMessage },
        })
      );

      // Fail-closed: return empty response, never hallucinate
      return {
        request_id: request.request_id,
        timestamp: new Date().toISOString(),
        content: '',
        blocked: true,
        block_reason: errorMessage,
        tool_calls: [],
        retrieval_hit_count: 0,
        latency_ms: latencyMs,
      };
    }
  }

  /** Get the policy engine for specialist routing */
  getPolicyEngine(): PolicyEngine {
    return this.policyEngine;
  }

  /** Get the skill registry for external registration */
  getSkillRegistry(): SkillRegistry {
    return this.skillRegistry;
  }

  /** Get the skill router for external resolution */
  getSkillRouter(): SkillRouter {
    return this.skillRouter;
  }

  /**
   * Execute a skill invocation.
   * Resolves the skill via the router, validates permissions,
   * dispatches to the skill executor, and emits audit events.
   */
  async executeSkill(invocation: SkillInvocation): Promise<SkillResult> {
    const startTime = Date.now();

    // Resolve skill
    const skill = this.skillRouter.resolve(invocation);
    if (!skill) {
      return {
        success: false,
        skillSlug: invocation.skillSlug,
        output: {},
        latencyMs: Date.now() - startTime,
        error: {
          code: 'SKILL_NOT_FOUND',
          message: `Skill "${invocation.skillSlug}" not found or deprecated`,
          retryable: false,
        },
      };
    }

    // Validate permissions
    if (!this.skillRouter.validatePermissions(skill, invocation.context)) {
      this.auditEmitter.emit(
        ConsoleAuditEmitter.createEvent({
          request_id: invocation.context.requestId,
          event_type: 'copilot_tool_denied',
          dimensions: {
            skill_slug: skill.slug,
            reason: 'Insufficient tool permissions for skill capability',
          },
        })
      );

      return {
        success: false,
        skillSlug: invocation.skillSlug,
        output: {},
        latencyMs: Date.now() - startTime,
        error: {
          code: 'SKILL_PERMISSION_DENIED',
          message: `Caller lacks required tool permissions for skill "${skill.slug}"`,
          retryable: false,
        },
      };
    }

    // Emit skill invocation audit event
    this.auditEmitter.emit(
      ConsoleAuditEmitter.createEvent({
        request_id: invocation.context.requestId,
        event_type: 'copilot_chat_request',
        dimensions: {
          skill_slug: skill.slug,
          skill_type: skill.type,
          skill_version: skill.version,
        },
      })
    );

    // Dispatch to skill executor
    const result = await this.dispatchSkill(skill, invocation);

    // Emit skill result audit event
    this.auditEmitter.emit(
      ConsoleAuditEmitter.createEvent({
        request_id: invocation.context.requestId,
        event_type: result.success ? 'copilot_chat_response' : 'copilot_chat_fallback',
        severity: result.success ? 'info' : 'error',
        latency_ms: result.latencyMs,
        dimensions: {
          skill_slug: skill.slug,
          success: result.success,
          ...(result.tokensUsed ? {
            prompt_tokens: result.tokensUsed.prompt,
            completion_tokens: result.tokensUsed.completion,
          } : {}),
          ...(result.error ? { error_code: result.error.code } : {}),
        },
      })
    );

    return result;
  }

  /** Dispatch a resolved skill to its executor function */
  private async dispatchSkill(
    skill: SkillDefinition,
    invocation: SkillInvocation,
  ): Promise<SkillResult> {
    const client = this.config.foundryClient;

    switch (skill.slug) {
      case 'knowledge.search':
        return executeKnowledgeSearch(invocation, client);
      case 'business.summarize':
        return executeBusinessSummarize(invocation, client);
      case 'workflow.extract-actions':
        return executeWorkflowExtractActions(invocation, client);
      case 'platform.route-request':
        return executePlatformRouteRequest(invocation, client, this.skillRegistry);
      default:
        return {
          success: false,
          skillSlug: invocation.skillSlug,
          output: {},
          latencyMs: 0,
          error: {
            code: 'SKILL_NO_EXECUTOR',
            message: `No executor registered for skill "${skill.slug}"`,
            retryable: false,
          },
        };
    }
  }

  private buildMessages(request: PrecursorRequest): FoundryMessage[] {
    const messages: FoundryMessage[] = [];

    // System prompt from agents/ assets
    messages.push({
      role: 'system',
      content: this.assets!.systemPrompt,
    });

    // Conversation history
    if (request.conversation_history) {
      for (const turn of request.conversation_history) {
        messages.push({
          role: turn.role,
          content: turn.content,
        });
      }
    }

    // User message with context envelope prefix
    const contextPrefix = this.policyEngine.buildContextPrefix(request.context);
    messages.push({
      role: 'user',
      content: `${contextPrefix}\n\n${request.prompt}`,
    });

    return messages;
  }

  private async executeToolCalls(
    toolCalls: FoundryToolCall[],
    context: ContextEnvelope,
    requestId: string
  ): Promise<ToolCallRecord[]> {
    const results: ToolCallRecord[] = [];

    for (const call of toolCalls) {
      const startTime = Date.now();
      const toolName = call.function.name;

      // Policy check
      const policyCheck = this.policyEngine.checkToolPermission(toolName, context);

      if (!policyCheck.permitted) {
        // Emit tool denied event
        this.auditEmitter.emit(
          ConsoleAuditEmitter.createEvent({
            request_id: requestId,
            event_type: 'copilot_tool_denied',
            context,
            dimensions: { tool_name: toolName, reason: policyCheck.reason },
          })
        );

        results.push({
          tool_name: toolName,
          arguments: JSON.parse(call.function.arguments),
          result: null,
          permitted: false,
          latency_ms: Date.now() - startTime,
        });
        continue;
      }

      // Emit tool request event
      this.auditEmitter.emit(
        ConsoleAuditEmitter.createEvent({
          request_id: requestId,
          event_type: 'copilot_tool_request',
          context,
          dimensions: { tool_name: toolName },
        })
      );

      // Execute tool (mock implementation - real tool execution in Stage 2)
      const args = JSON.parse(call.function.arguments);
      const mockResult = this.mockToolExecution(toolName, args);

      results.push({
        tool_name: toolName,
        arguments: args,
        result: mockResult,
        permitted: true,
        latency_ms: Date.now() - startTime,
      });

      // Emit tool permitted event
      this.auditEmitter.emit(
        ConsoleAuditEmitter.createEvent({
          request_id: requestId,
          event_type: 'copilot_tool_permitted',
          context,
          dimensions: { tool_name: toolName, latency_ms: Date.now() - startTime },
        })
      );
    }

    return results;
  }

  /**
   * Mock tool execution — returns synthetic data.
   * Stage 2 replaces with real Odoo JSON-RPC / search calls.
   */
  private mockToolExecution(toolName: string, args: Record<string, unknown>): unknown {
    switch (toolName) {
      case 'read_record':
        return {
          id: args['record_id'],
          model: args['model'],
          data: { name: 'Mock Record', state: 'draft' },
        };
      case 'search_records':
        return {
          model: args['model'],
          count: 3,
          records: [
            { id: 1, name: 'Record A' },
            { id: 2, name: 'Record B' },
            { id: 3, name: 'Record C' },
          ],
        };
      case 'search_docs':
        return {
          query: args['query'],
          results: [{ title: 'Mock KB Article', relevance: 0.95 }],
        };
      default:
        return { tool: toolName, status: 'mock_executed', args };
    }
  }
}
