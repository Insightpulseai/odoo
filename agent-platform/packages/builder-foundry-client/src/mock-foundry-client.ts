/**
 * MockFoundryClient — local dev/test implementation that returns deterministic responses.
 * No external dependencies. Used for:
 * - Local development without Azure credentials
 * - Unit testing the orchestration layer
 * - CI validation
 */

import type {
  FoundryClient,
  FoundryChatRequest,
  FoundryChatResponse,
  FoundryToolCall,
} from './foundry-client.js';

/** Configuration for mock responses */
export interface MockConfig {
  /** Default response content when no pattern matches */
  defaultResponse: string;
  /** Simulated latency in ms (0 for instant) */
  latencyMs: number;
  /** Whether to simulate tool calls for known prompts */
  simulateToolCalls: boolean;
}

const DEFAULT_MOCK_CONFIG: MockConfig = {
  defaultResponse:
    'I am the IPAI Odoo Copilot operating in advisory mode. I cannot access live systems, but I can guide you through Odoo workflows, Philippine tax compliance, and business operations.',
  latencyMs: 50,
  simulateToolCalls: false,
};

/**
 * Mock Foundry client for local development and testing.
 */
export class MockFoundryClient implements FoundryClient {
  readonly name = 'MockFoundryClient';
  private config: MockConfig;
  private callLog: Array<{ request: FoundryChatRequest; response: FoundryChatResponse }> = [];

  constructor(config: Partial<MockConfig> = {}) {
    this.config = { ...DEFAULT_MOCK_CONFIG, ...config };
  }

  isConfigured(): boolean {
    return true; // Mock is always configured
  }

  async chatCompletion(request: FoundryChatRequest): Promise<FoundryChatResponse> {
    if (this.config.latencyMs > 0) {
      await new Promise((resolve) => setTimeout(resolve, this.config.latencyMs));
    }

    const lastUserMessage = request.messages
      .filter((m) => m.role === 'user')
      .pop();

    const content = this.generateResponse(lastUserMessage?.content ?? '');
    const toolCalls = this.maybeGenerateToolCalls(lastUserMessage?.content ?? '', request.tools);

    const response: FoundryChatResponse = {
      content: toolCalls.length > 0 ? '' : content,
      tool_calls: toolCalls,
      thread_id: `mock-thread-${Date.now()}`,
      usage: {
        prompt_tokens: Math.ceil((lastUserMessage?.content ?? '').length / 4),
        completion_tokens: Math.ceil(content.length / 4),
      },
      finish_reason: toolCalls.length > 0 ? 'tool_calls' : 'stop',
    };

    this.callLog.push({ request, response });
    return response;
  }

  async healthCheck(): Promise<boolean> {
    return true;
  }

  /** Get the call log for test assertions */
  getCallLog(): ReadonlyArray<{ request: FoundryChatRequest; response: FoundryChatResponse }> {
    return this.callLog;
  }

  /** Clear the call log */
  clearCallLog(): void {
    this.callLog = [];
  }

  private generateResponse(prompt: string): string {
    const lower = prompt.toLowerCase();

    // Scope boundary: refuse off-topic
    if (this.isOffTopic(lower)) {
      return 'I specialize in Odoo ERP, Philippine tax compliance, finance operations, and business process guidance. I cannot help with that topic, but I am happy to assist with business operations questions.';
    }

    // Safety: refuse action requests in advisory mode
    if (this.isActionRequest(lower)) {
      return 'I am operating in advisory mode and cannot execute actions in Odoo. However, I can guide you through the steps to accomplish this in Odoo (CE 19.0).';
    }

    // Safety: refuse PII/credential requests
    if (this.isPIIRequest(lower)) {
      return 'I cannot provide personally identifiable information, credentials, or internal system details due to privacy and security policies.';
    }

    // Knowledge responses for known domains
    if (lower.includes('bir') || lower.includes('tax') || lower.includes('vat')) {
      return 'For Philippine tax compliance (BIR), the key forms and deadlines depend on your business type and registration status. This is general guidance. Consult a qualified professional for your specific situation.';
    }

    if (lower.includes('odoo') || lower.includes('module') || lower.includes('erp')) {
      return 'Odoo CE 19.0 provides comprehensive ERP functionality. I can help you understand module configuration, workflows, and best practices.';
    }

    return this.config.defaultResponse;
  }

  private maybeGenerateToolCalls(
    prompt: string,
    tools?: FoundryChatRequest['tools']
  ): FoundryToolCall[] {
    if (!this.config.simulateToolCalls || !tools || tools.length === 0) {
      return [];
    }

    const lower = prompt.toLowerCase();

    // Simulate read_record tool call for record lookup patterns
    if (lower.includes('look up') || lower.includes('show me record') || lower.includes('find')) {
      const readRecordTool = tools.find((t) => t.function.name === 'read_record');
      if (readRecordTool) {
        return [
          {
            id: `call-mock-${Date.now()}`,
            type: 'function',
            function: {
              name: 'read_record',
              arguments: JSON.stringify({ model: 'res.partner', record_id: 1, fields: ['name', 'email'] }),
            },
          },
        ];
      }
    }

    // Simulate search_records for search patterns
    if (lower.includes('search') || lower.includes('list')) {
      const searchTool = tools.find((t) => t.function.name === 'search_records');
      if (searchTool) {
        return [
          {
            id: `call-mock-${Date.now()}`,
            type: 'function',
            function: {
              name: 'search_records',
              arguments: JSON.stringify({
                model: 'res.partner',
                domain: [['is_company', '=', true]],
                fields: ['name'],
                limit: 10,
              }),
            },
          },
        ];
      }
    }

    return [];
  }

  private isOffTopic(prompt: string): boolean {
    const offTopicPatterns = ['poem', 'recipe', 'joke', 'story', 'song', 'game', 'weather'];
    return offTopicPatterns.some((p) => prompt.includes(p));
  }

  private isActionRequest(prompt: string): boolean {
    const actionPatterns = [
      'delete', 'create', 'update', 'approve', 'confirm', 'post invoice',
      'send email', 'execute', 'run',
    ];
    return actionPatterns.some((p) => prompt.includes(p));
  }

  private isPIIRequest(prompt: string): boolean {
    const piiPatterns = [
      'api key', 'password', 'connection string', 'email address',
      'phone number', 'secret', 'credential', 'token',
    ];
    return piiPatterns.some((p) => prompt.includes(p));
  }
}
