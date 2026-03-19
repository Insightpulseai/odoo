/**
 * Platform Route Request skill — deterministic routing of user queries.
 *
 * Takes a user query and classifies it to the appropriate skill slug.
 * Acts as the "front-door" dispatcher for the skills framework.
 * Uses keyword matching first (fast path) and falls back to LLM classification.
 */

import type { SkillDefinition, SkillInvocation, SkillResult } from '@ipai/builder-contract';
import type { FoundryClient } from '@ipai/builder-foundry-client';
import type { SkillRegistry } from '../skill-registry.js';

export const platformRouteRequestDefinition: SkillDefinition = {
  name: 'Platform Route Request',
  slug: 'platform.route-request',
  version: '0.1.0',
  description: 'Classify a user query and route it to the appropriate skill',
  type: 'routing',
  capability: 'read_only',
  inputSchema: {
    type: 'object',
    properties: {
      query: { type: 'string' },
    },
    required: ['query'],
  },
  outputSchema: {
    type: 'object',
    properties: {
      targetSkillSlug: { type: 'string' },
      confidence: { type: 'number' },
      reasoning: { type: 'string' },
    },
  },
  allowedTools: [],
  modelHints: { temperature: 0.0, maxTokens: 256 },
  timeoutMs: 5000,
  retryPolicy: { maxRetries: 0, backoffMs: 0 },
  observabilityTags: ['platform', 'routing', 'classification'],
  owner: 'platform',
  deprecated: false,
};

/** Keyword-based routing rules (fast path, no LLM call) */
const KEYWORD_ROUTES: Array<{ patterns: string[]; slug: string }> = [
  { patterns: ['search', 'find', 'look up', 'knowledge', 'what is', 'how to'], slug: 'knowledge.search' },
  { patterns: ['summarize', 'summary', 'recap', 'condense', 'brief'], slug: 'business.summarize' },
  { patterns: ['action items', 'extract actions', 'todo', 'tasks', 'follow up'], slug: 'workflow.extract-actions' },
];

/**
 * Execute the routing skill.
 * Attempts keyword matching first; falls back to LLM classification if no match.
 */
export async function executePlatformRouteRequest(
  invocation: SkillInvocation,
  client: FoundryClient,
  registry?: SkillRegistry,
): Promise<SkillResult> {
  const start = Date.now();
  const query = (invocation.input['query'] as string).toLowerCase();

  // Fast path: keyword matching
  for (const route of KEYWORD_ROUTES) {
    if (route.patterns.some(p => query.includes(p))) {
      return {
        success: true,
        skillSlug: 'platform.route-request',
        output: {
          targetSkillSlug: route.slug,
          confidence: 0.85,
          reasoning: `Keyword match for "${route.slug}"`,
        },
        latencyMs: Date.now() - start,
      };
    }
  }

  // Slow path: LLM classification
  try {
    const availableSkills = registry
      ? registry.list().filter(s => !s.deprecated && s.slug !== 'platform.route-request')
      : [];

    const skillList = availableSkills.length > 0
      ? availableSkills.map(s => `- ${s.slug}: ${s.description}`).join('\n')
      : '- knowledge.search: Search knowledge base\n- business.summarize: Summarize text\n- workflow.extract-actions: Extract action items';

    const response = await client.chatCompletion({
      messages: [
        {
          role: 'system',
          content:
            `You are a request classifier. Given a user query, determine which skill should handle it.\n\nAvailable skills:\n${skillList}\n\n` +
            'Return JSON: { "targetSkillSlug": "...", "confidence": 0.0-1.0, "reasoning": "..." }. ' +
            'If no skill matches, use "knowledge.search" as the default.',
        },
        { role: 'user', content: query },
      ],
      request_id: invocation.context.requestId,
    });

    let output: Record<string, unknown>;
    try {
      output = JSON.parse(response.content) as Record<string, unknown>;
    } catch {
      output = {
        targetSkillSlug: 'knowledge.search',
        confidence: 0.5,
        reasoning: 'LLM response not parseable; defaulting to knowledge search',
      };
    }

    return {
      success: true,
      skillSlug: 'platform.route-request',
      output,
      latencyMs: Date.now() - start,
      tokensUsed: {
        prompt: response.usage.prompt_tokens,
        completion: response.usage.completion_tokens,
      },
    };
  } catch (err) {
    // On failure, default to knowledge search
    return {
      success: true,
      skillSlug: 'platform.route-request',
      output: {
        targetSkillSlug: 'knowledge.search',
        confidence: 0.3,
        reasoning: `Routing failed (${String(err)}); defaulting to knowledge search`,
      },
      latencyMs: Date.now() - start,
      error: {
        code: 'ROUTE_CLASSIFICATION_FAILED',
        message: String(err),
        retryable: false,
      },
    };
  }
}
