import type {
  DesignerAgentRequest,
  DesignerAgentResponse,
} from '../../contracts/designer-agent';
import { DesignerAgentResponseSchema } from '../../contracts/designer-agent';
import type { FoundryExecutionResult } from '../../contracts/foundry';
import { DesignerAgentResponseParseError } from './errors';

export function normalizeFoundryDesignerResponse(
  request: DesignerAgentRequest,
  execution: FoundryExecutionResult
): DesignerAgentResponse {
  let raw: unknown;
  try {
    raw = JSON.parse(execution.rawText);
  } catch (error) {
    throw new DesignerAgentResponseParseError(
      'Foundry response is not valid JSON',
      error
    );
  }

  const result = DesignerAgentResponseSchema.safeParse(raw);

  if (!result.success) {
    throw new DesignerAgentResponseParseError(
      'Foundry response does not match DesignerAgentResponse schema',
      result.error.flatten()
    );
  }

  return {
    ...result.data,
    metadata: {
      provider: 'foundry',
      agentId: execution.agentId,
      conversationId: execution.conversationId,
      responseId: execution.responseId,
      correlationId: request.correlationId ?? crypto.randomUUID(),
    },
  };
}
