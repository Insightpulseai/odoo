/**
 * Builder Factory HTTP Server — the gateway that Odoo's copilot controller calls.
 *
 * Routes:
 *   GET  /health          — health check
 *   POST /                — non-streaming chat completion
 *   POST /stream          — SSE streaming chat completion (future)
 *
 * Environment:
 *   PORT                          — listen port (default: 8088)
 *   AGENTS_ROOT                   — path to agents/ assets directory
 *   AZURE_AI_FOUNDRY_ENDPOINT     — Foundry endpoint (optional, falls back to mock)
 *   AZURE_AI_FOUNDRY_KEY          — Foundry API key (optional)
 *   AZURE_AI_FOUNDRY_DEPLOYMENT   — model deployment name (default: gpt-4.1)
 */

import { createServer, type IncomingMessage, type ServerResponse } from 'node:http';
import { randomUUID } from 'node:crypto';
import { resolve } from 'node:path';
import {
  defaultContextEnvelope,
  type PrecursorRequest,
} from '@ipai/builder-contract';
import { MockFoundryClient, AzureFoundryClient } from '@ipai/builder-foundry-client';
import { Orchestrator } from '@ipai/builder-orchestrator';

const PORT = parseInt(process.env['PORT'] || '8088', 10);
const AGENTS_ROOT = resolve(
  process.env['AGENTS_ROOT'] ?? resolve(__dirname, '../../../../agents')
);

let orchestrator: Orchestrator;

async function initOrchestrator(): Promise<void> {
  const endpoint = process.env['AZURE_AI_FOUNDRY_ENDPOINT'];
  const apiKey = process.env['AZURE_AI_FOUNDRY_KEY'];
  const deployment = process.env['AZURE_AI_FOUNDRY_DEPLOYMENT'] || 'gpt-4.1';

  let foundryClient;
  if (endpoint && apiKey) {
    // AzureFoundryClient reads config from env vars internally
    foundryClient = new AzureFoundryClient();
    console.log(`[gateway] Using AzureFoundryClient → ${endpoint}`);
  } else {
    foundryClient = new MockFoundryClient({ simulateToolCalls: true });
    console.log('[gateway] Using MockFoundryClient (set AZURE_AI_FOUNDRY_ENDPOINT to use real Foundry)');
  }

  orchestrator = new Orchestrator({
    agentsRoot: AGENTS_ROOT,
    agentProfile: 'ipai-odoo-copilot-azure',
    foundryClient,
  });

  await orchestrator.initialize();

  // Register tax specialist as blocked
  const router = orchestrator.getPolicyEngine().createSpecialistRouter();
  router.register({
    domain: 'tax-compliance',
    agent_id: 'taxpulse-v0',
    version: '0.0.0',
    capabilities: ['bir-filing', 'withholding-tax'],
    production_ready: false,
    blockers: ['ATC namespace divergence unresolved'],
  });

  console.log(`[gateway] Orchestrator initialized, agents root: ${AGENTS_ROOT}`);
}

function readBody(req: IncomingMessage): Promise<string> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    req.on('data', (chunk) => chunks.push(chunk));
    req.on('end', () => resolve(Buffer.concat(chunks).toString('utf-8')));
    req.on('error', reject);
  });
}

function json(res: ServerResponse, status: number, data: unknown): void {
  const body = JSON.stringify(data);
  res.writeHead(status, {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(body),
  });
  res.end(body);
}

async function handleChat(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const raw = await readBody(req);
  let payload: Record<string, unknown>;
  try {
    payload = JSON.parse(raw);
  } catch {
    json(res, 400, { error: 'Invalid JSON' });
    return;
  }

  const prompt = String(payload['message'] || payload['prompt'] || '');
  if (!prompt) {
    json(res, 400, { error: 'Missing message or prompt field' });
    return;
  }

  const correlationId = String(
    req.headers['x-correlation-id'] || payload['correlation_id'] || randomUUID()
  );
  const mode = String(
    req.headers['x-copilot-mode'] || payload['mode'] || 'PROD-ADVISORY'
  );
  const context = (payload['context'] as Record<string, unknown>) || {};
  const user = (payload['user'] as Record<string, unknown>) || {};

  const request: PrecursorRequest = {
    request_id: correlationId,
    timestamp: new Date().toISOString(),
    prompt,
    context: {
      ...defaultContextEnvelope(),
      user_id: String(user['uid'] || ''),
      user_email: String(user['login'] || ''),
      surface: (['web', 'erp', 'copilot', 'analytics', 'ops'].includes(String(context['surface']))
        ? String(context['surface'])
        : 'erp') as import('@ipai/builder-contract').Surface,
      mode: (mode === 'PROD-ACTION' ? 'PROD-ACTION' : 'PROD-ADVISORY') as import('@ipai/builder-contract').RuntimeMode,
      permitted_tools: ['read_record', 'search_records', 'search_docs'],
    },
    channel: 'api',
  };

  const result = await orchestrator.execute(request);

  json(res, 200, {
    request_id: result.request_id,
    content: result.content,
    blocked: result.blocked,
    tool_calls: result.tool_calls,
    latency_ms: result.latency_ms,
    conversation_id: payload['conversation_id'] || null,
  });
}

async function handleRequest(req: IncomingMessage, res: ServerResponse): Promise<void> {
  const url = req.url || '/';
  const method = req.method || 'GET';

  // CORS for local dev
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, X-Correlation-Id, X-Copilot-Mode');

  if (method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  if (url === '/health' && method === 'GET') {
    json(res, 200, { status: 'pass', service: 'ipai-copilot-gateway', version: '0.1.0' });
    return;
  }

  if ((url === '/' || url === '/chat') && method === 'POST') {
    await handleChat(req, res);
    return;
  }

  json(res, 404, { error: 'Not found' });
}

async function start(): Promise<void> {
  await initOrchestrator();

  const server = createServer(async (req, res) => {
    try {
      await handleRequest(req, res);
    } catch (err) {
      console.error('[gateway] Request error:', err);
      json(res, 500, { error: 'Internal server error' });
    }
  });

  server.listen(PORT, '0.0.0.0', () => {
    console.log(`[gateway] Copilot Gateway listening on http://0.0.0.0:${PORT}`);
  });
}

start().catch((err) => {
  console.error('[gateway] Fatal:', err);
  process.exit(1);
});
