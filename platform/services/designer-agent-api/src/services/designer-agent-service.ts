import type {
  DesignerAgentRequest,
  DesignerAgentResponse,
} from '../contracts/designer-agent';
import type { FoundryAdapterConfig } from '../contracts/foundry';
import { createFoundryClient } from '../adapters/foundry/client';
import { executeFoundryDesignerAgent } from '../adapters/foundry/execute';

export class DesignerAgentService {
  constructor(private readonly config: FoundryAdapterConfig) {}

  async execute(request: DesignerAgentRequest): Promise<DesignerAgentResponse> {
    const client = createFoundryClient(this.config);
    return executeFoundryDesignerAgent(client as never, this.config, {
      ...request,
      correlationId: request.correlationId ?? crypto.randomUUID(),
    });
  }
}
