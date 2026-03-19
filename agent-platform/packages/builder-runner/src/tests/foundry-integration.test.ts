/**
 * Integration test — validates real Azure AI Foundry model call through agent-platform.
 *
 * Requires env vars:
 *   AZURE_AI_FOUNDRY_ENDPOINT
 *   AZURE_FOUNDRY_API_KEY
 *   AZURE_MODEL_DEPLOYMENT (defaults to 'gpt-4.1')
 *
 * Run: AZURE_AI_FOUNDRY_ENDPOINT=... AZURE_FOUNDRY_API_KEY=... npm run test
 */

import { describe, it } from 'node:test';
import { strict as assert } from 'node:assert';
import { randomUUID } from 'node:crypto';
import { resolve } from 'node:path';
import { defaultContextEnvelope } from '@ipai/builder-contract';
import type { PrecursorRequest } from '@ipai/builder-contract';
import { AzureFoundryClient } from '@ipai/builder-foundry-client';
import { Orchestrator, ConsoleAuditEmitter } from '@ipai/builder-orchestrator';

const AGENTS_ROOT = resolve(__dirname, '../../../../../agents');

const SKIP = !process.env['AZURE_AI_FOUNDRY_ENDPOINT'] || !process.env['AZURE_FOUNDRY_API_KEY'];

describe('Azure AI Foundry Integration Tests', { skip: SKIP ? 'AZURE_AI_FOUNDRY_ENDPOINT or AZURE_FOUNDRY_API_KEY not set' : false }, () => {

  it('should confirm AzureFoundryClient is configured', () => {
    const client = new AzureFoundryClient();
    assert.ok(client.isConfigured(), 'AzureFoundryClient should be configured when env vars are set');
    assert.equal(client.name, 'AzureFoundryClient');
  });

  it('should pass health check against real endpoint', async () => {
    const client = new AzureFoundryClient();
    const healthy = await client.healthCheck();
    console.log(`Health check result: ${healthy}`);
    assert.ok(healthy, 'Health check should pass against real endpoint');
  });

  it('should complete a raw chat request via AzureFoundryClient', async () => {
    const client = new AzureFoundryClient();

    const response = await client.chatCompletion({
      request_id: randomUUID(),
      messages: [
        { role: 'system', content: 'You are a helpful Odoo ERP assistant.' },
        { role: 'user', content: 'What is the standard month-end close process?' },
      ],
      temperature: 0.3,
      max_tokens: 200,
    });

    console.log(`\n--- Raw Foundry Response ---`);
    console.log(`Content (first 300 chars): ${response.content.slice(0, 300)}`);
    console.log(`Finish reason: ${response.finish_reason}`);
    console.log(`Prompt tokens: ${response.usage.prompt_tokens}`);
    console.log(`Completion tokens: ${response.usage.completion_tokens}`);

    assert.ok(response.content.length > 0, 'Response content must not be empty');
    assert.ok(response.usage.prompt_tokens > 0, 'Must report prompt token usage');
    assert.ok(response.usage.completion_tokens > 0, 'Must report completion token usage');
    assert.ok(
      response.finish_reason === 'stop' || response.finish_reason === 'length',
      `Finish reason should be stop or length, got: ${response.finish_reason}`
    );
  });

  it('should execute a full orchestrator flow with real Foundry client', async () => {
    const foundryClient = new AzureFoundryClient();
    const auditEmitter = new ConsoleAuditEmitter();

    const orchestrator = new Orchestrator({
      agentsRoot: AGENTS_ROOT,
      agentProfile: 'ipai-odoo-copilot-azure',
      foundryClient,
      auditEmitter,
    });

    await orchestrator.initialize();

    const request: PrecursorRequest = {
      request_id: randomUUID(),
      timestamp: new Date().toISOString(),
      prompt: 'What is the standard month-end close process in Odoo?',
      context: {
        ...defaultContextEnvelope(),
        user_id: 'integration-test',
        surface: 'erp',
      },
      channel: 'api',
    };

    const response = await orchestrator.execute(request);

    console.log(`\n--- Orchestrator Response ---`);
    console.log(`Content (first 500 chars): ${response.content.slice(0, 500)}`);
    console.log(`Request ID: ${response.request_id}`);
    console.log(`Blocked: ${response.blocked}`);
    console.log(`Block reason: ${response.block_reason || 'none'}`);
    console.log(`Latency: ${response.latency_ms}ms`);
    console.log(`Tool calls: ${response.tool_calls.length}`);

    assert.ok(response.content.length > 0, 'Orchestrated response must have content');
    assert.equal(response.blocked, false, 'Advisory query should not be blocked');
    assert.equal(response.request_id, request.request_id, 'Correlation ID must propagate');
    assert.ok(response.latency_ms > 0, 'Latency must be positive (real network call)');

    // Verify audit events
    const auditBuffer = auditEmitter.getBuffer();
    assert.ok(auditBuffer.length >= 2, 'At least 2 audit events (request + response)');
  });
});
