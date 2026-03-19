/**
 * Workflow Extract Actions skill — extract structured action items from text.
 *
 * Parses meeting notes, emails, or conversation threads to produce
 * a list of actionable items with owner, due date, and priority.
 */

import type { SkillDefinition, SkillInvocation, SkillResult } from '@ipai/builder-contract';
import type { FoundryClient } from '@ipai/builder-foundry-client';

export const workflowExtractActionsDefinition: SkillDefinition = {
  name: 'Workflow Extract Actions',
  slug: 'workflow.extract-actions',
  version: '0.1.0',
  description: 'Extract structured action items (title, owner, dueDate, priority) from text',
  type: 'extraction',
  capability: 'read_only',
  inputSchema: {
    type: 'object',
    properties: {
      text: { type: 'string' },
    },
    required: ['text'],
  },
  outputSchema: {
    type: 'object',
    properties: {
      actions: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            title: { type: 'string' },
            owner: { type: 'string' },
            dueDate: { type: 'string' },
            priority: { type: 'string', enum: ['high', 'medium', 'low'] },
          },
        },
      },
    },
  },
  allowedTools: [],
  modelHints: { temperature: 0.1, maxTokens: 1024 },
  timeoutMs: 12000,
  retryPolicy: { maxRetries: 1, backoffMs: 1000 },
  observabilityTags: ['workflow', 'extraction', 'actions'],
  owner: 'platform',
  deprecated: false,
};

export async function executeWorkflowExtractActions(
  invocation: SkillInvocation,
  client: FoundryClient,
): Promise<SkillResult> {
  const start = Date.now();
  const text = invocation.input['text'] as string;

  try {
    const response = await client.chatCompletion({
      messages: [
        {
          role: 'system',
          content:
            'You are an action-item extractor. From the provided text, extract all action items. ' +
            'Return JSON: { "actions": [{ "title": "...", "owner": "...", "dueDate": "YYYY-MM-DD or empty", "priority": "high|medium|low" }] }. ' +
            'If no actions are found, return { "actions": [] }.',
        },
        { role: 'user', content: text },
      ],
      request_id: invocation.context.requestId,
    });

    let output: Record<string, unknown>;
    try {
      output = JSON.parse(response.content) as Record<string, unknown>;
    } catch {
      output = { actions: [] };
    }

    return {
      success: true,
      skillSlug: 'workflow.extract-actions',
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
      skillSlug: 'workflow.extract-actions',
      output: {},
      latencyMs: Date.now() - start,
      error: {
        code: 'EXTRACT_ACTIONS_FAILED',
        message: String(err),
        retryable: true,
      },
    };
  }
}
