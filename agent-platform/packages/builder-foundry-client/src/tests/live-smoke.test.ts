/**
 * Live smoke tests for AzureFoundryClient — validates real Azure AI Foundry connectivity.
 *
 * Covers:
 *   - healthCheck() against real endpoint
 *   - chatCompletion() basic round-trip
 *   - Response contract shape validation
 *   - Latency budget enforcement (< 30s)
 *
 * Requires env vars:
 *   AZURE_AI_FOUNDRY_ENDPOINT
 *   AZURE_FOUNDRY_API_KEY
 *   AZURE_AI_FOUNDRY_PROJECT (optional, defaults to 'ipai-copilot')
 *   AZURE_MODEL_DEPLOYMENT (optional, defaults to 'gpt-4.1')
 *
 * Run: AZURE_AI_FOUNDRY_ENDPOINT=... AZURE_FOUNDRY_API_KEY=... npx tsx --test src/tests/live-smoke.test.ts
 * CI:  Runs in azure_staging_revision gate only (skipped in CI pre-deploy).
 */

import { describe, it } from 'node:test';
import { strict as assert } from 'node:assert';
import { randomUUID } from 'node:crypto';
import { AzureFoundryClient } from '../azure-foundry-client.js';

const SKIP = !process.env['AZURE_AI_FOUNDRY_ENDPOINT'] || !process.env['AZURE_FOUNDRY_API_KEY'];

describe('AzureFoundryClient Live Smoke', { skip: SKIP ? 'AZURE_AI_FOUNDRY_ENDPOINT or AZURE_FOUNDRY_API_KEY not set' : false }, () => {

  it('isConfigured() returns true when env vars are present', () => {
    const client = new AzureFoundryClient();
    assert.ok(client.isConfigured(), 'Client must be configured');
    assert.equal(client.name, 'AzureFoundryClient');
  });

  it('healthCheck() succeeds against live endpoint', async () => {
    const client = new AzureFoundryClient();
    const healthy = await client.healthCheck();
    assert.ok(healthy, 'Health check must pass against real Foundry endpoint');
  });

  it('chatCompletion() returns valid response shape', async () => {
    const client = new AzureFoundryClient();
    const startMs = Date.now();

    const response = await client.chatCompletion({
      request_id: randomUUID(),
      messages: [
        { role: 'system', content: 'Reply with exactly: SMOKE_OK' },
        { role: 'user', content: 'health check' },
      ],
      temperature: 0,
      max_tokens: 20,
    });

    const elapsed = Date.now() - startMs;

    // Shape validation
    assert.ok(typeof response.content === 'string', 'content must be string');
    assert.ok(Array.isArray(response.tool_calls), 'tool_calls must be array');
    assert.ok(typeof response.usage.prompt_tokens === 'number', 'prompt_tokens must be number');
    assert.ok(typeof response.usage.completion_tokens === 'number', 'completion_tokens must be number');
    assert.ok(
      ['stop', 'length', 'tool_calls', 'content_filter'].includes(response.finish_reason),
      `finish_reason must be valid, got: ${response.finish_reason}`,
    );

    // Content must not be empty
    assert.ok(response.content.length > 0, 'Response content must not be empty');

    // Token usage must be reported
    assert.ok(response.usage.prompt_tokens > 0, 'Must report prompt token usage');

    // Latency budget: < 30 seconds for a trivial request
    assert.ok(elapsed < 30_000, `Latency ${elapsed}ms exceeds 30s budget`);
  });

  it('chatCompletion() handles tool definitions without error', async () => {
    const client = new AzureFoundryClient();

    const response = await client.chatCompletion({
      request_id: randomUUID(),
      messages: [
        { role: 'system', content: 'You have a tool available. Reply normally.' },
        { role: 'user', content: 'Hello' },
      ],
      tools: [
        {
          type: 'function',
          function: {
            name: 'get_time',
            description: 'Get the current time',
            parameters: { type: 'object', properties: {} },
          },
        },
      ],
      temperature: 0,
      max_tokens: 50,
    });

    // Should complete without throwing
    assert.ok(
      response.finish_reason === 'stop' || response.finish_reason === 'tool_calls',
      `Expected stop or tool_calls, got: ${response.finish_reason}`,
    );
  });
});

describe('AzureFoundryClient Offline Behavior', () => {
  it('isConfigured() returns false when env vars missing', () => {
    // Save and clear env vars
    const saved = {
      endpoint: process.env['AZURE_AI_FOUNDRY_ENDPOINT'],
      project: process.env['AZURE_AI_FOUNDRY_PROJECT'],
      key: process.env['AZURE_FOUNDRY_API_KEY'],
    };
    delete process.env['AZURE_AI_FOUNDRY_ENDPOINT'];
    delete process.env['AZURE_AI_FOUNDRY_PROJECT'];
    delete process.env['AZURE_FOUNDRY_API_KEY'];

    try {
      const client = new AzureFoundryClient();
      assert.equal(client.isConfigured(), false, 'Client must not be configured without env vars');
    } finally {
      // Restore
      if (saved.endpoint) process.env['AZURE_AI_FOUNDRY_ENDPOINT'] = saved.endpoint;
      if (saved.project) process.env['AZURE_AI_FOUNDRY_PROJECT'] = saved.project;
      if (saved.key) process.env['AZURE_FOUNDRY_API_KEY'] = saved.key;
    }
  });

  it('healthCheck() returns false when not configured', async () => {
    const saved = {
      endpoint: process.env['AZURE_AI_FOUNDRY_ENDPOINT'],
      project: process.env['AZURE_AI_FOUNDRY_PROJECT'],
      key: process.env['AZURE_FOUNDRY_API_KEY'],
    };
    delete process.env['AZURE_AI_FOUNDRY_ENDPOINT'];
    delete process.env['AZURE_AI_FOUNDRY_PROJECT'];
    delete process.env['AZURE_FOUNDRY_API_KEY'];

    try {
      const client = new AzureFoundryClient();
      const healthy = await client.healthCheck();
      assert.equal(healthy, false, 'Unconfigured client health check must return false');
    } finally {
      if (saved.endpoint) process.env['AZURE_AI_FOUNDRY_ENDPOINT'] = saved.endpoint;
      if (saved.project) process.env['AZURE_AI_FOUNDRY_PROJECT'] = saved.project;
      if (saved.key) process.env['AZURE_FOUNDRY_API_KEY'] = saved.key;
    }
  });

  it('chatCompletion() throws when not configured', async () => {
    const saved = {
      endpoint: process.env['AZURE_AI_FOUNDRY_ENDPOINT'],
      project: process.env['AZURE_AI_FOUNDRY_PROJECT'],
      key: process.env['AZURE_FOUNDRY_API_KEY'],
    };
    delete process.env['AZURE_AI_FOUNDRY_ENDPOINT'];
    delete process.env['AZURE_AI_FOUNDRY_PROJECT'];
    delete process.env['AZURE_FOUNDRY_API_KEY'];

    try {
      const client = new AzureFoundryClient();
      await assert.rejects(
        () => client.chatCompletion({
          request_id: randomUUID(),
          messages: [{ role: 'user', content: 'test' }],
        }),
        /not configured/i,
        'Must throw "not configured" error',
      );
    } finally {
      if (saved.endpoint) process.env['AZURE_AI_FOUNDRY_ENDPOINT'] = saved.endpoint;
      if (saved.project) process.env['AZURE_AI_FOUNDRY_PROJECT'] = saved.project;
      if (saved.key) process.env['AZURE_FOUNDRY_API_KEY'] = saved.key;
    }
  });
});
