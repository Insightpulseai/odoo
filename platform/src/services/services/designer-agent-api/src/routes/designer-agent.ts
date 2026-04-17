import type { Request, Response } from 'express';
import { DesignerAgentRequestSchema } from '../contracts/designer-agent';
import { readDesignerAgentEnv } from '../config/env';
import { DesignerAgentService } from '../services/designer-agent-service';

export async function postDesignerAgent(req: Request, res: Response) {
  const parsed = DesignerAgentRequestSchema.safeParse(req.body);

  if (!parsed.success) {
    res.status(400).json({
      error: 'Invalid request payload',
      details: parsed.error.flatten(),
    });
    return;
  }

  try {
    const env = readDesignerAgentEnv(process.env);
    const service = new DesignerAgentService({
      endpoint: env.AZURE_FOUNDRY_ENDPOINT,
      projectConnectionString: env.AZURE_FOUNDRY_PROJECT_CONNECTION_STRING,
      modelDeploymentName: env.AZURE_FOUNDRY_MODEL_DEPLOYMENT,
      agentId: env.AZURE_FOUNDRY_DESIGNER_AGENT_ID,
      agentName: env.AZURE_FOUNDRY_DESIGNER_AGENT_NAME,
      timeoutMs: Number(env.DESIGNER_AGENT_TIMEOUT_MS),
    });

    const response = await service.execute(parsed.data);
    res.json(response);
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    res.status(500).json({ error: message });
  }
}
