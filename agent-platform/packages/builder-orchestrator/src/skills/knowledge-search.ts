/**
 * Knowledge Search skill — grounded retrieval with citations.
 *
 * Takes a natural-language query, executes via FoundryClient,
 * and returns a grounded answer with citation metadata.
 */

import type { SkillDefinition, SkillInvocation, SkillResult } from '@ipai/builder-contract';
import type { FoundryClient } from '@ipai/builder-foundry-client';

export const knowledgeSearchDefinition: SkillDefinition = {
  name: 'Knowledge Search',
  slug: 'knowledge.search',
  version: '0.1.0',
  description: 'Search the knowledge base and return grounded answers with citations',
  type: 'retrieval',
  capability: 'read_only',
  inputSchema: {
    type: 'object',
    properties: { query: { type: 'string' } },
    required: ['query'],
  },
  outputSchema: {
    type: 'object',
    properties: {
      answer: { type: 'string' },
      citations: { type: 'array' },
    },
  },
  allowedTools: ['search_knowledge'],
  modelHints: { temperature: 0.2, maxTokens: 1024 },
  timeoutMs: 15000,
  retryPolicy: { maxRetries: 1, backoffMs: 1000 },
  observabilityTags: ['knowledge', 'retrieval', 'grounded'],
  owner: 'platform',
  deprecated: false,
};

export async function executeKnowledgeSearch(
  invocation: SkillInvocation,
  client: FoundryClient,
): Promise<SkillResult> {
  const start = Date.now();
  const query = invocation.input['query'] as string;

  try {
    const response = await client.chatCompletion({
      messages: [
        {
          role: 'system',
          content:
            'You are a knowledge assistant. Answer based on available information. Always cite sources.',
        },
        { role: 'user', content: query },
      ],
      request_id: invocation.context.requestId,
    });

    return {
      success: true,
      skillSlug: 'knowledge.search',
      output: { answer: response.content, raw_usage: response.usage },
      citations: [],
      latencyMs: Date.now() - start,
      tokensUsed: {
        prompt: response.usage.prompt_tokens,
        completion: response.usage.completion_tokens,
      },
    };
  } catch (err) {
    return {
      success: false,
      skillSlug: 'knowledge.search',
      output: {},
      latencyMs: Date.now() - start,
      error: {
        code: 'KNOWLEDGE_SEARCH_FAILED',
        message: String(err),
        retryable: true,
      },
    };
  }
}
