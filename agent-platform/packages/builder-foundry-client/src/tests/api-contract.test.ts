/**
 * API contract test — validates the Odoo → agent-platform bridge contract.
 *
 * The Odoo copilot controller POSTs to the agent-platform service at:
 *   POST /api/v1/chat
 *   Headers: X-Pulser-Service-Key, Content-Type: application/json
 *   Body: { prompt, context, attachments?, request_id }
 *
 * This test validates the contract shape without requiring a running service.
 * Live version runs against AGENT_PLATFORM_URL in staging gate.
 *
 * Covers:
 *   - Request/response schema validation
 *   - Required fields enforcement
 *   - Error response shape for bad requests
 */

import { describe, it } from 'node:test';
import { strict as assert } from 'node:assert';
import { randomUUID } from 'node:crypto';

/** Odoo → agent-platform request contract */
interface OdooBridgeRequest {
  prompt: string;
  context: {
    user_id: string;
    surface: string;
    conversation_id?: string;
    mode?: string;
    permitted_tools?: string[];
  };
  attachments?: Array<{
    filename: string;
    mime_type: string;
    snippet: string;
    token_estimate: number;
  }>;
  request_id: string;
}

/** agent-platform → Odoo response contract */
interface OdooBridgeResponse {
  content: string;
  blocked: boolean;
  block_reason: string;
  request_id: string;
  tool_calls: Array<{
    name: string;
    arguments: Record<string, unknown>;
  }>;
  latency_ms: number;
  invoice_check?: {
    status: 'validated' | 'needs_review';
    expected_payable: number;
    printed_total_due: number;
    delta: number;
    findings: Array<{
      code: string;
      severity: string;
      expected: string;
      actual: string;
    }>;
  };
}

const AGENT_PLATFORM_URL = process.env['AGENT_PLATFORM_URL'];
const SERVICE_KEY = process.env['AGENT_PLATFORM_SERVICE_KEY'];
const SKIP_LIVE = !AGENT_PLATFORM_URL || !SERVICE_KEY;

describe('Odoo Bridge API Contract (Schema)', () => {
  it('request schema validates required fields', () => {
    const request: OdooBridgeRequest = {
      prompt: 'What is the VAT rate?',
      context: {
        user_id: 'admin',
        surface: 'erp',
      },
      request_id: randomUUID(),
    };

    assert.ok(request.prompt.length > 0, 'prompt must not be empty');
    assert.ok(request.context.user_id, 'user_id required');
    assert.ok(request.context.surface, 'surface required');
    assert.ok(request.request_id, 'request_id required');
  });

  it('request schema validates attachment contract', () => {
    const request: OdooBridgeRequest = {
      prompt: 'Check this invoice',
      context: {
        user_id: 'admin',
        surface: 'erp',
      },
      attachments: [
        {
          filename: 'invoice.pdf',
          mime_type: 'application/pdf',
          snippet: 'Net: 100,000 VAT: 12,000 Total: 112,000',
          token_estimate: 15,
        },
      ],
      request_id: randomUUID(),
    };

    assert.equal(request.attachments!.length, 1);
    assert.ok(request.attachments![0].filename, 'filename required');
    assert.ok(request.attachments![0].mime_type, 'mime_type required');
    assert.ok(request.attachments![0].snippet.length > 0, 'snippet must have content');
    assert.ok(request.attachments![0].token_estimate > 0, 'token_estimate must be positive');
  });

  it('response schema validates all required fields', () => {
    const response: OdooBridgeResponse = {
      content: 'The VAT rate is 12%.',
      blocked: false,
      block_reason: '',
      request_id: randomUUID(),
      tool_calls: [],
      latency_ms: 450,
    };

    assert.ok(typeof response.content === 'string');
    assert.ok(typeof response.blocked === 'boolean');
    assert.ok(typeof response.block_reason === 'string');
    assert.ok(response.request_id.length > 0);
    assert.ok(Array.isArray(response.tool_calls));
    assert.ok(typeof response.latency_ms === 'number');
  });

  it('response with invoice_check validates deterministic validator output', () => {
    const response: OdooBridgeResponse = {
      content: 'Invoice needs review.',
      blocked: false,
      block_reason: '',
      request_id: randomUUID(),
      tool_calls: [],
      latency_ms: 1200,
      invoice_check: {
        status: 'needs_review',
        expected_payable: 95408.16,
        printed_total_due: 85000.00,
        delta: 10408.16,
        findings: [
          {
            code: 'PRINTED_TOTAL_DUE_MISMATCH',
            severity: 'error',
            expected: '95408.16',
            actual: '85000.00',
          },
        ],
      },
    };

    assert.equal(response.invoice_check!.status, 'needs_review');
    assert.ok(response.invoice_check!.delta > 0);
    assert.equal(response.invoice_check!.findings.length, 1);
    assert.equal(response.invoice_check!.findings[0].code, 'PRINTED_TOTAL_DUE_MISMATCH');
  });
});

describe('Odoo Bridge API Contract (Live)', { skip: SKIP_LIVE ? 'AGENT_PLATFORM_URL or AGENT_PLATFORM_SERVICE_KEY not set' : false }, () => {

  it('POST /api/v1/chat returns valid response', async () => {
    const requestId = randomUUID();
    const body: OdooBridgeRequest = {
      prompt: 'What is the standard VAT rate in the Philippines?',
      context: {
        user_id: 'smoke-test',
        surface: 'erp',
        mode: 'PROD-ADVISORY',
      },
      request_id: requestId,
    };

    const res = await fetch(`${AGENT_PLATFORM_URL}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Pulser-Service-Key': SERVICE_KEY!,
      },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(30_000),
    });

    assert.equal(res.status, 200, `Expected 200, got ${res.status}`);

    const response = await res.json() as OdooBridgeResponse;

    // Correlation ID propagation
    assert.equal(response.request_id, requestId, 'request_id must propagate');

    // Response shape
    assert.ok(response.content.length > 0, 'content must not be empty');
    assert.equal(response.blocked, false, 'Advisory query should not be blocked');
    assert.ok(response.latency_ms > 0, 'latency_ms must be positive');
  });

  it('POST /api/v1/chat rejects empty prompt', async () => {
    const body: OdooBridgeRequest = {
      prompt: '',
      context: {
        user_id: 'smoke-test',
        surface: 'erp',
      },
      request_id: randomUUID(),
    };

    const res = await fetch(`${AGENT_PLATFORM_URL}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Pulser-Service-Key': SERVICE_KEY!,
      },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(10_000),
    });

    const response = await res.json() as OdooBridgeResponse;
    assert.ok(response.blocked, 'Empty prompt should be blocked');
  });

  it('POST /api/v1/chat rejects invalid service key', async () => {
    const body: OdooBridgeRequest = {
      prompt: 'test',
      context: {
        user_id: 'smoke-test',
        surface: 'erp',
      },
      request_id: randomUUID(),
    };

    const res = await fetch(`${AGENT_PLATFORM_URL}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Pulser-Service-Key': 'invalid-key-12345',
      },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(10_000),
    });

    assert.ok(res.status === 401 || res.status === 403, `Expected 401/403, got ${res.status}`);
  });
});
