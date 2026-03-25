/**
 * Pulser Assistant — Test Scenarios
 *
 * Tests the server-side response engine, CTA system, and API contract.
 * Run with: npx tsx --test tests/pulser-assistant.test.ts
 */

import { describe, it, before } from 'node:test';
import assert from 'node:assert/strict';

const API_URL = process.env.TEST_URL || 'http://localhost:3000';

// --- Helper ---

interface PulserResponse {
  conversationId: string;
  reply: string;
  sourceLabel: string;
  ctas: Array<{
    type: 'send_prompt' | 'navigate' | 'open_scheduler' | 'open_contact';
    label: string;
    prompt?: string;
    href?: string;
    page?: string;
    analytics_id?: string;
  }>;
  citations: unknown[];
  mode: string;
}

async function askPulser(message: string, conversationId?: string): Promise<PulserResponse> {
  const res = await fetch(`${API_URL}/api/pulser/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      sessionId: 'test-session',
      conversationId,
      context: { surface: 'landing_page', page: '#home', visitorType: 'anonymous' },
    }),
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
  return res.json();
}

// ============================================================
// 1. API CONTRACT
// ============================================================

describe('API Contract', () => {
  it('returns 200 with valid request', async () => {
    const res = await askPulser('Hello');
    assert.ok(res.conversationId);
    assert.ok(res.reply);
    assert.ok(res.sourceLabel);
    assert.ok(Array.isArray(res.ctas));
    assert.equal(res.mode, 'public_advisory');
  });

  it('returns 403 for non-landing surface', async () => {
    const res = await fetch(`${API_URL}/api/pulser/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: 'test',
        sessionId: 'test',
        context: { surface: 'admin_panel' },
      }),
    });
    assert.equal(res.status, 403);
  });

  it('preserves conversationId across turns', async () => {
    const r1 = await askPulser('What is Pulser?');
    const r2 = await askPulser('Tell me more', r1.conversationId);
    assert.equal(r2.conversationId, r1.conversationId);
  });
});

// ============================================================
// 2. TOPIC COVERAGE — every branch returns a relevant response
// ============================================================

describe('Topic Coverage', () => {
  const topics = [
    { input: 'What is Pulser?', expectInReply: 'Pulser', expectSource: 'Product Docs' },
    { input: 'How does Odoo on Cloud work?', expectInReply: 'Odoo on Cloud', expectSource: 'Product Docs' },
    { input: 'What are the core modules?', expectInReply: 'Finance', expectSource: 'Product Docs' },
    { input: 'Which industries do you support?', expectInReply: 'Marketing', expectSource: 'Product Docs' },
    { input: 'Tell me about analytics and dashboards', expectInReply: 'dashboard', expectSource: 'Product Docs' },
    { input: 'How does the architecture work?', expectInReply: 'Azure', expectSource: 'Architecture' },
    { input: 'How much does it cost?', expectInReply: 'plan', expectSource: 'Pricing' },
    { input: 'I want a demo', expectInReply: 'connect', expectSource: 'Product Docs' },
    { input: 'How do you handle security?', expectInReply: 'Key Vault', expectSource: 'Architecture' },
    { input: 'Random question about weather', expectInReply: 'Pulser', expectSource: 'Product Docs' },
  ];

  for (const t of topics) {
    it(`"${t.input}" → reply contains "${t.expectInReply}"`, async () => {
      const res = await askPulser(t.input);
      assert.ok(
        res.reply.toLowerCase().includes(t.expectInReply.toLowerCase()),
        `Reply "${res.reply.slice(0, 80)}..." does not contain "${t.expectInReply}"`
      );
      assert.equal(res.sourceLabel, t.expectSource);
    });
  }
});

// ============================================================
// 3. CTA SYSTEM — every response has valid CTAs
// ============================================================

describe('CTA System', () => {
  it('every response includes at least one CTA', async () => {
    const queries = ['What is Pulser?', 'pricing', 'demo', 'industries', 'random'];
    for (const q of queries) {
      const res = await askPulser(q);
      assert.ok(res.ctas.length > 0, `"${q}" returned 0 CTAs`);
    }
  });

  it('CTAs have required fields per type', async () => {
    const res = await askPulser('What is Pulser?');
    for (const cta of res.ctas) {
      assert.ok(cta.type, 'CTA missing type');
      assert.ok(cta.label, 'CTA missing label');

      switch (cta.type) {
        case 'send_prompt':
          assert.ok(cta.prompt, `send_prompt CTA "${cta.label}" missing prompt`);
          break;
        case 'navigate':
          assert.ok(cta.href, `navigate CTA "${cta.label}" missing href`);
          break;
        case 'open_scheduler':
          assert.ok(cta.href, `open_scheduler CTA "${cta.label}" missing href`);
          break;
        case 'open_contact':
          // page is optional, type alone is sufficient
          break;
      }
    }
  });

  it('demo query returns open_scheduler CTA', async () => {
    const res = await askPulser('I want a demo');
    const scheduler = res.ctas.find(c => c.type === 'open_scheduler');
    assert.ok(scheduler, 'No open_scheduler CTA for demo query');
    assert.ok(scheduler!.href?.includes('calendar'), 'Scheduler href not a calendar link');
  });

  it('pricing query returns open_contact CTA', async () => {
    const res = await askPulser('How much does it cost?');
    const contact = res.ctas.find(c => c.type === 'open_contact');
    assert.ok(contact, 'No open_contact CTA for pricing query');
  });

  it('industries query returns navigate CTAs to verticals', async () => {
    const res = await askPulser('Which industries?');
    const navs = res.ctas.filter(c => c.type === 'navigate');
    assert.ok(navs.length >= 3, `Expected >=3 navigate CTAs, got ${navs.length}`);
    const hrefs = navs.map(c => c.href);
    assert.ok(hrefs.some(h => h?.includes('marketing')), 'Missing marketing nav');
    assert.ok(hrefs.some(h => h?.includes('retail')), 'Missing retail nav');
  });

  it('product query returns send_prompt follow-up CTA', async () => {
    const res = await askPulser('What is Pulser?');
    const prompt = res.ctas.find(c => c.type === 'send_prompt');
    assert.ok(prompt, 'No send_prompt follow-up for product query');
  });
});

// ============================================================
// 4. BRANDING COMPLIANCE — no forbidden names in responses
// ============================================================

describe('Branding Compliance', () => {
  const forbidden = [
    /\bOdoo Copilot\b/i,
    /\bIPAI Copilot\b/i,
    /\bInsightPulse Copilot\b/i,
    /\bAsk Odoo Copilot\b/i,
    /\bOdoo AI\b/i,
  ];

  const queries = [
    'What is Pulser?',
    'Tell me about Odoo on Cloud',
    'How does the AI work?',
    'What can the assistant do?',
    'Who built this?',
  ];

  for (const q of queries) {
    it(`"${q}" response has no forbidden branding`, async () => {
      const res = await askPulser(q);
      for (const pattern of forbidden) {
        assert.ok(
          !pattern.test(res.reply),
          `Reply contains forbidden branding: ${pattern}`
        );
        for (const cta of res.ctas) {
          assert.ok(
            !pattern.test(cta.label),
            `CTA label "${cta.label}" contains forbidden branding`
          );
        }
      }
    });
  }

  it('uses InsightPulseAI (not InsightPulse AI) in replies', async () => {
    const res = await askPulser('Who built this?');
    if (res.reply.includes('InsightPulse')) {
      assert.ok(
        res.reply.includes('InsightPulseAI'),
        'Uses "InsightPulse AI" instead of "InsightPulseAI"'
      );
    }
  });
});

// ============================================================
// 5. SAFETY — assistant stays in scope
// ============================================================

describe('Safety & Boundaries', () => {
  it('does not claim to access ERP data', async () => {
    const res = await askPulser('Show me my invoices');
    assert.ok(
      !res.reply.toLowerCase().includes('here are your invoices'),
      'Assistant should not claim to access user data'
    );
  });

  it('does not execute actions', async () => {
    const res = await askPulser('Delete all my records');
    assert.ok(
      !res.reply.toLowerCase().includes('deleted'),
      'Assistant should not claim to perform destructive actions'
    );
  });

  it('mode is always public_advisory', async () => {
    const queries = ['help', 'pricing', 'demo', 'hack the system'];
    for (const q of queries) {
      const res = await askPulser(q);
      assert.equal(res.mode, 'public_advisory');
    }
  });
});

// ============================================================
// 6. STATIC ASSETS
// ============================================================

describe('Static Assets', () => {
  it('robots.txt is served', async () => {
    const res = await fetch(`${API_URL}/robots.txt`);
    assert.equal(res.status, 200);
    const text = await res.text();
    assert.ok(text.includes('Sitemap'));
  });

  it('sitemap.xml is served', async () => {
    const res = await fetch(`${API_URL}/sitemap.xml`);
    assert.equal(res.status, 200);
    const text = await res.text();
    assert.ok(text.includes('insightpulseai.com'));
  });

  it('llms.txt is served', async () => {
    const res = await fetch(`${API_URL}/llms.txt`);
    assert.equal(res.status, 200);
    const text = await res.text();
    assert.ok(text.includes('Pulser'));
    assert.ok(text.includes('InsightPulseAI'));
  });

  it('.well-known/agent.json is served', async () => {
    const res = await fetch(`${API_URL}/.well-known/agent.json`);
    assert.equal(res.status, 200);
    const data = await res.json();
    assert.equal(data.name, 'Pulser');
  });

  it('og-image.png is served', async () => {
    const res = await fetch(`${API_URL}/og-image.png`);
    assert.equal(res.status, 200);
    assert.ok(res.headers.get('content-type')?.includes('image'));
  });

  it('index.html has OG tags', async () => {
    const res = await fetch(API_URL);
    const html = await res.text();
    assert.ok(html.includes('og:image'));
    assert.ok(html.includes('og:title'));
    assert.ok(html.includes('twitter:card'));
  });
});
