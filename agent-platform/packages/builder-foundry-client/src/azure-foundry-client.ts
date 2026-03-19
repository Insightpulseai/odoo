/**
 * AzureFoundryClient — real Azure AI Foundry integration point.
 *
 * This is the production adapter. It requires:
 * - AZURE_AI_FOUNDRY_ENDPOINT env var
 * - AZURE_AI_FOUNDRY_PROJECT env var
 * - Authentication via managed identity (DefaultAzureCredential) or API key
 *
 * Current state: Stub with explicit "not configured" errors.
 * Stage 2 will add real SDK calls via @azure/ai-projects or OpenAI-compat surface.
 */

import type {
  FoundryClient,
  FoundryChatRequest,
  FoundryChatResponse,
} from './foundry-client.js';

export interface AzureFoundryConfig {
  /** Azure AI Foundry endpoint URL */
  endpoint: string;
  /** Azure AI Foundry project name */
  project: string;
  /** Model deployment name (e.g., 'gpt-4.1') */
  modelDeployment: string;
  /** Auth mode: 'managed_identity' | 'api_key' */
  authMode: 'managed_identity' | 'api_key';
  /** API key (only for non-prod bootstrap, never for production) */
  apiKey?: string;
}

/**
 * Azure AI Foundry client — production adapter.
 *
 * Auth preference order (per runtime-contract.md):
 * 1. Managed identity (DefaultAzureCredential / IMDS)
 * 2. Service principal / app registration
 * 3. Temporary API key (non-prod only)
 */
export class AzureFoundryClient implements FoundryClient {
  readonly name = 'AzureFoundryClient';
  private config: AzureFoundryConfig | null;

  constructor() {
    this.config = this.loadConfig();
  }

  isConfigured(): boolean {
    return this.config !== null;
  }

  async chatCompletion(request: FoundryChatRequest): Promise<FoundryChatResponse> {
    if (!this.config) {
      throw new Error(
        'AzureFoundryClient is not configured. ' +
        'Required env vars: AZURE_AI_FOUNDRY_ENDPOINT, AZURE_AI_FOUNDRY_PROJECT. ' +
        'See agents/foundry/ipai-odoo-copilot-azure/runtime-contract.md for setup.'
      );
    }

    // Use OpenAI-compatible endpoint on the Foundry resource
    // Endpoint pattern: https://<resource>.cognitiveservices.azure.com/openai/deployments/<model>/chat/completions?api-version=2025-01-01-preview
    const url = `${this.config.endpoint.replace(/\/$/, '')}/openai/deployments/${this.config.modelDeployment}/chat/completions?api-version=2025-01-01-preview`;

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.config.authMode === 'api_key' && this.config.apiKey) {
      headers['api-key'] = this.config.apiKey;
    } else {
      // For managed identity, we need to acquire a token
      // This requires @azure/identity at runtime
      throw new Error(
        'AzureFoundryClient: managed_identity auth requires @azure/identity. ' +
        'Set AZURE_FOUNDRY_API_KEY for non-prod bootstrap, or install @azure/identity for production.'
      );
    }

    const body = {
      messages: request.messages.map(m => ({
        role: m.role,
        content: m.content,
      })),
      temperature: request.temperature ?? 0.3,
      max_tokens: request.max_tokens ?? 2048,
      ...(request.tools && request.tools.length > 0 ? {
        tools: request.tools,
      } : {}),
    };

    const startMs = Date.now();
    const res = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(30_000),
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => 'unknown');
      throw new Error(`AzureFoundryClient: HTTP ${res.status} from ${this.config.modelDeployment}: ${errText}`);
    }

    const data = await res.json() as {
      choices: Array<{
        message: { role: string; content: string | null; tool_calls?: Array<{ id: string; function: { name: string; arguments: string } }> };
        finish_reason: string;
      }>;
      usage?: { prompt_tokens: number; completion_tokens: number; total_tokens: number };
    };

    const choice = data.choices?.[0];
    if (!choice) {
      throw new Error('AzureFoundryClient: no choices in response');
    }

    const tool_calls = (choice.message.tool_calls ?? []).map(tc => ({
      id: tc.id,
      type: 'function' as const,
      function: {
        name: tc.function.name,
        arguments: tc.function.arguments,
      },
    }));

    return {
      content: choice.message.content ?? '',
      tool_calls,
      finish_reason: choice.finish_reason as 'stop' | 'tool_calls' | 'length' | 'content_filter',
      usage: {
        prompt_tokens: data.usage?.prompt_tokens ?? 0,
        completion_tokens: data.usage?.completion_tokens ?? 0,
      },
    };
  }

  async healthCheck(): Promise<boolean> {
    if (!this.config) {
      return false;
    }

    try {
      const url = `${this.config.endpoint.replace(/\/$/, '')}/openai/models?api-version=2025-01-01-preview`;
      const headers: Record<string, string> = {};
      if (this.config.authMode === 'api_key' && this.config.apiKey) {
        headers['api-key'] = this.config.apiKey;
      }
      const res = await fetch(url, { headers, signal: AbortSignal.timeout(5_000) });
      return res.ok;
    } catch {
      return false;
    }
  }

  private loadConfig(): AzureFoundryConfig | null {
    const endpoint = process.env['AZURE_AI_FOUNDRY_ENDPOINT'];
    const project = process.env['AZURE_AI_FOUNDRY_PROJECT'];

    if (!endpoint || !project) {
      return null;
    }

    const apiKey = process.env['AZURE_FOUNDRY_API_KEY'];

    return {
      endpoint,
      project,
      modelDeployment: process.env['AZURE_MODEL_DEPLOYMENT'] ?? 'gpt-4.1',
      authMode: apiKey ? 'api_key' : 'managed_identity',
      apiKey,
    };
  }
}
