/**
 * Business Summarize skill — condense business context into structured summaries.
 *
 * Takes raw business text (meeting notes, reports, thread transcripts)
 * and produces a structured summary with key points and action items.
 */

import type { SkillDefinition, SkillInvocation, SkillResult } from '@ipai/builder-contract';
import type { FoundryClient } from '@ipai/builder-foundry-client';

export const businessSummarizeDefinition: SkillDefinition = {
  name: 'Business Summarize',
  slug: 'business.summarize',
  version: '0.1.0',
  description: 'Summarize business context into structured key points and takeaways',
  type: 'summarization',
  capability: 'read_only',
  inputSchema: {
    type: 'object',
    properties: {
      text: { type: 'string' },
      maxPoints: { type: 'number' },
    },
    required: ['text'],
  },
  outputSchema: {
    type: 'object',
    properties: {
      summary: { type: 'string' },
      keyPoints: { type: 'array', items: { type: 'string' } },
      sentiment: { type: 'string' },
    },
  },
  allowedTools: [],
  modelHints: { temperature: 0.3, maxTokens: 512 },
  timeoutMs: 10000,
  retryPolicy: { maxRetries: 1, backoffMs: 1000 },
  observabilityTags: ['business', 'summarization'],
  owner: 'platform',
  deprecated: false,
};

export async function executeBusinessSummarize(
  invocation: SkillInvocation,
  client: FoundryClient,
): Promise<SkillResult> {
  const start = Date.now();
  const text = invocation.input['text'] as string;
  const maxPoints = (invocation.input['maxPoints'] as number) ?? 5;

  try {
    const response = await client.chatCompletion({
      messages: [
        {
          role: 'system',
          content: `You are a business analyst. Summarize the following text into a concise summary with up to ${maxPoints} key points. Return JSON: { "summary": "...", "keyPoints": ["..."], "sentiment": "positive|neutral|negative" }`,
        },
        { role: 'user', content: text },
      ],
      request_id: invocation.context.requestId,
    });

    // Parse structured output; fall back to raw content
    let output: Record<string, unknown>;
    try {
      output = JSON.parse(response.content) as Record<string, unknown>;
    } catch {
      output = { summary: response.content, keyPoints: [], sentiment: 'neutral' };
    }

    return {
      success: true,
      skillSlug: 'business.summarize',
      output,
      latencyMs: Date.now() - start,
      tokensUsed: {
        prompt: response.usage.prompt_tokens,
        completion: response.usage.completion_tokens,
      },
    };
  } catch (err) {
    return {
      success: false,
      skillSlug: 'business.summarize',
      output: {},
      latencyMs: Date.now() - start,
      error: {
        code: 'BUSINESS_SUMMARIZE_FAILED',
        message: String(err),
        retryable: true,
      },
    };
  }
}
