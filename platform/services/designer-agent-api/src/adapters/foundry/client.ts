import { DefaultAzureCredential } from '@azure/identity';
import { AIProjectClient } from '@azure/ai-projects';
import type { FoundryAdapterConfig } from '../../contracts/foundry';

export function createFoundryClient(config: FoundryAdapterConfig) {
  const credential = new DefaultAzureCredential();

  if (config.projectConnectionString) {
    return AIProjectClient.fromConnectionString(
      config.projectConnectionString,
      credential
    );
  }

  return new AIProjectClient(config.endpoint, credential);
}
