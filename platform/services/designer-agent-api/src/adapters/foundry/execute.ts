import type {
  DesignerAgentRequest,
  DesignerAgentResponse,
} from '../../contracts/designer-agent';
import type { FoundryAdapterConfig, FoundryExecutionResult } from '../../contracts/foundry';
import { ensureDesignerAgent } from './agents';
import { normalizeFoundryDesignerResponse } from './normalize';
import { DesignerAgentProviderError, DesignerAgentResponseParseError } from './errors';

type ProjectsClientLike = {
  agents: {
    getAgent?: (agentId: string) => Promise<{ id: string }>;
    createAgent?: (input: Record<string, unknown>) => Promise<{ id: string }>;
    listAgents?: () => AsyncIterable<{ id: string; name?: string }>;
    createConversation?: (input?: Record<string, unknown>) => Promise<{ id: string }>;
    createResponse?: (input: Record<string, unknown>) => Promise<{
      id?: string;
      outputText?: string;
      status?: string;
    }>;
  };
};

function buildFoundryInput(request: DesignerAgentRequest): string {
  return JSON.stringify({
    task: 'designer-agent',
    mode: request.mode,
    brief: request.brief,
    output_contract: {
      mode: 'generate|critique|refine|handoff',
      brief: 'echoed brief',
      proposal: 'optional',
      critique: 'optional',
      handoff: 'optional',
      rationale: ['array'],
      warnings: ['array'],
    },
    rules: [
      'Return JSON only',
      'No markdown fences',
      'Prefer Fluent UI React v9 components',
      'Preserve Microsoft-native tone and hierarchy',
    ],
  });
}

function withTimeout<T>(promise: Promise<T>, ms: number, label: string): Promise<T> {
  return new Promise<T>((resolve, reject) => {
    const timer = setTimeout(() => {
      reject(
        new DesignerAgentProviderError(
          `${label} timed out after ${ms}ms`
        )
      );
    }, ms);

    promise.then(
      (value) => {
        clearTimeout(timer);
        resolve(value);
      },
      (error) => {
        clearTimeout(timer);
        reject(error);
      }
    );
  });
}

export async function executeFoundryDesignerAgent(
  client: ProjectsClientLike,
  config: FoundryAdapterConfig,
  request: DesignerAgentRequest
): Promise<DesignerAgentResponse> {
  const ensured = await withTimeout(
    ensureDesignerAgent(client as never, config),
    config.timeoutMs,
    'Agent ensure'
  );

  const conversation =
    request.conversationId
      ? { id: request.conversationId }
      : await withTimeout(
          client.agents.createConversation?.({}) ?? Promise.reject(new Error('createConversation not available')),
          config.timeoutMs,
          'Conversation creation'
        );

  if (!conversation?.id) {
    throw new DesignerAgentProviderError('Failed to create or reuse conversation');
  }

  const response = await withTimeout(
    client.agents.createResponse?.({
      agentId: ensured.agentId,
      conversationId: conversation.id,
      input: buildFoundryInput(request),
    }) ?? Promise.reject(new Error('createResponse not available')),
    config.timeoutMs,
    'Foundry response'
  );

  if (!response) {
    throw new DesignerAgentProviderError('Foundry returned no response');
  }

  const execution: FoundryExecutionResult = {
    rawText: response.outputText ?? '',
    agentId: ensured.agentId,
    conversationId: conversation.id,
    responseId: response.id,
    finishReason: response.status,
  };

  try {
    return normalizeFoundryDesignerResponse(request, execution);
  } catch (error) {
    if (error instanceof DesignerAgentResponseParseError) {
      throw error;
    }
    throw new DesignerAgentResponseParseError(
      'Failed to normalize Foundry response',
      error
    );
  }
}
