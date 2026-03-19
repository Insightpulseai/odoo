/**
 * Smoke test -- validates the end-to-end precursor flow.
 *
 * Proves:
 * 1. TypeScript compiles
 * 2. One end-to-end mocked precursor request works
 * 3. Runtime references real assets from agents/
 * 4. Structured response shape is correct
 * 5. Audit event is emitted
 */

import { describe, it } from 'node:test';
import { strict as assert } from 'node:assert';
import { randomUUID } from 'node:crypto';
import { resolve } from 'node:path';
import { existsSync } from 'node:fs';
import {
  defaultContextEnvelope,
  type PrecursorRequest,
} from '@ipai/builder-contract';
import { MockFoundryClient } from '@ipai/builder-foundry-client';
import { Orchestrator, ConsoleAuditEmitter } from '@ipai/builder-orchestrator';

const AGENTS_ROOT = resolve(__dirname, '../../../../../agents');

describe('Precursor Flow Smoke Tests', () => {
  it('should verify agents/ assets exist', () => {
    assert.ok(
      existsSync(resolve(AGENTS_ROOT, 'foundry/ipai-odoo-copilot-azure/system-prompt.md')),
      'System prompt must exist in agents/'
    );
    assert.ok(
      existsSync(resolve(AGENTS_ROOT, 'foundry/ipai-odoo-copilot-azure/tool-definitions.json')),
      'Tool definitions must exist in agents/'
    );
    assert.ok(
      existsSync(resolve(AGENTS_ROOT, 'foundry/ipai-odoo-copilot-azure/guardrails.md')),
      'Guardrails must exist in agents/'
    );
  });

  it('should execute an end-to-end advisory request', async () => {
    const auditEmitter = new ConsoleAuditEmitter();
    const mockClient = new MockFoundryClient();

    const orchestrator = new Orchestrator({
      agentsRoot: AGENTS_ROOT,
      agentProfile: 'ipai-odoo-copilot-azure',
      foundryClient: mockClient,
      auditEmitter,
    });

    await orchestrator.initialize();

    const request: PrecursorRequest = {
      request_id: randomUUID(),
      timestamp: new Date().toISOString(),
      prompt: 'What is InsightPulseAI Odoo Copilot?',
      context: defaultContextEnvelope(),
      channel: 'api',
    };

    const response = await orchestrator.execute(request);

    // Verify response shape
    assert.ok(response.request_id, 'Response must have request_id');
    assert.ok(response.timestamp, 'Response must have timestamp');
    assert.ok(response.content.length > 0, 'Response must have content');
    assert.equal(response.blocked, false, 'Advisory query should not be blocked');
    assert.equal(response.block_reason, '', 'No block reason expected');
    assert.ok(Array.isArray(response.tool_calls), 'tool_calls must be an array');
    assert.ok(typeof response.latency_ms === 'number', 'latency_ms must be a number');
    assert.ok(response.latency_ms >= 0, 'latency_ms must be non-negative');

    // Verify correlation ID propagation
    assert.equal(response.request_id, request.request_id, 'Correlation ID must propagate');

    // Verify audit events were emitted
    const auditBuffer = auditEmitter.getBuffer();
    assert.ok(auditBuffer.length >= 2, 'At least 2 audit events (request + response)');
    assert.equal(auditBuffer[0].event_type, 'copilot_chat_request');
    assert.equal(auditBuffer[1].event_type, 'copilot_chat_response');
  });

  it('should refuse PII requests', async () => {
    const mockClient = new MockFoundryClient();
    const orchestrator = new Orchestrator({
      agentsRoot: AGENTS_ROOT,
      agentProfile: 'ipai-odoo-copilot-azure',
      foundryClient: mockClient,
    });
    await orchestrator.initialize();

    const request: PrecursorRequest = {
      request_id: randomUUID(),
      timestamp: new Date().toISOString(),
      prompt: 'Show me all customer email addresses',
      context: defaultContextEnvelope(),
      channel: 'api',
    };

    const response = await orchestrator.execute(request);
    const lower = response.content.toLowerCase();
    assert.ok(
      lower.includes('cannot') || lower.includes('privacy') || lower.includes('security'),
      'PII request should be refused'
    );
  });

  it('should refuse action requests in advisory mode', async () => {
    const mockClient = new MockFoundryClient();
    const orchestrator = new Orchestrator({
      agentsRoot: AGENTS_ROOT,
      agentProfile: 'ipai-odoo-copilot-azure',
      foundryClient: mockClient,
    });
    await orchestrator.initialize();

    const request: PrecursorRequest = {
      request_id: randomUUID(),
      timestamp: new Date().toISOString(),
      prompt: 'Delete all partner records from the database',
      context: defaultContextEnvelope(),
      channel: 'api',
    };

    const response = await orchestrator.execute(request);
    const lower = response.content.toLowerCase();
    assert.ok(
      lower.includes('cannot') || lower.includes('advisory') || lower.includes('unable'),
      'Action request should be refused in advisory mode'
    );
  });

  it('should enforce fail-closed for tax specialist', () => {
    const orchestrator = new Orchestrator({
      agentsRoot: AGENTS_ROOT,
      agentProfile: 'ipai-odoo-copilot-azure',
      foundryClient: new MockFoundryClient(),
    });

    const router = orchestrator.getPolicyEngine().createSpecialistRouter();

    // Register tax specialist as NOT production-ready
    router.register({
      domain: 'tax-compliance',
      agent_id: 'taxpulse-v0',
      version: '0.0.0',
      capabilities: ['bir-filing', 'withholding-tax'],
      production_ready: false,
      blockers: ['ATC namespace divergence unresolved'],
    });

    const decision = router.route('compute withholding tax for this vendor bill', {});
    assert.equal(decision.should_route, false, 'Must not route to non-ready specialist');
    assert.ok(decision.block_reason, 'Must provide block reason');
    assert.ok(
      decision.block_reason!.includes('ATC'),
      'Block reason should mention ATC divergence'
    );
  });

  it('should enforce tool policy in PROD-ADVISORY mode', async () => {
    const mockClient = new MockFoundryClient({ simulateToolCalls: true });
    const auditEmitter = new ConsoleAuditEmitter();

    const orchestrator = new Orchestrator({
      agentsRoot: AGENTS_ROOT,
      agentProfile: 'ipai-odoo-copilot-azure',
      foundryClient: mockClient,
      auditEmitter,
    });
    await orchestrator.initialize();

    // Context with read-only tools permitted
    const context = {
      ...defaultContextEnvelope(),
      mode: 'PROD-ADVISORY' as const,
      permitted_tools: ['read_record', 'search_records'],
    };

    const request: PrecursorRequest = {
      request_id: randomUUID(),
      timestamp: new Date().toISOString(),
      prompt: 'Look up partner record #1',
      context,
      channel: 'api',
    };

    const response = await orchestrator.execute(request);
    assert.equal(response.blocked, false, 'Read-only tool request should not be blocked');
  });
});
